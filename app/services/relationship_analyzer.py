"""法令・判例の関連性分析サービス"""

from typing import List, Dict, Optional, Any
import networkx as nx
from app.models.law import LawDetail
from app.models.case import CaseDetail, CaseReference
from app.repositories.case_repository import CaseRepository
from app.services.egov_client import EGovAPIClient


class RelationshipAnalyzer:
    """法令・判例の関連性分析サービス"""

    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()
        self.case_repo = CaseRepository()
        self.egov_client = EGovAPIClient()
        self._graph_built = False

    async def build_citation_graph(self) -> nx.DiGraph:
        """
        引用グラフを構築

        Returns:
            引用関係のグラフ（法令・判例ノード）
        """
        # 全法令・判例データを取得
        laws = await self._get_all_laws()
        cases = await self._get_all_cases()
        references = await self._get_all_references()

        # ノードを追加
        for law in laws:
            self.graph.add_node(
                f"law_{law.law_id}",
                type="law",
                name=law.law_name,
                data=law,
            )

        for case in cases:
            self.graph.add_node(
                f"case_{case.case_id}",
                type="case",
                name=case.case_name,
                data=case,
            )

        # エッジ（引用関係）を追加
        for ref in references:
            if ref.referenced_law_id:
                self.graph.add_edge(
                    f"case_{ref.case_id}",
                    f"law_{ref.referenced_law_id}",
                    type="cites_law",
                    context=ref.context,
                )
            if ref.referenced_case_id:
                self.graph.add_edge(
                    f"case_{ref.case_id}",
                    f"case_{ref.referenced_case_id}",
                    type="cites_case",
                    context=ref.context,
                )

        self._graph_built = True
        return self.graph

    async def find_related_cases(
        self, law_id: str, max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        特定の法令に関連する判例を検索

        Args:
            law_id: 法令ID
            max_depth: 探索深度

        Returns:
            関連判例のリスト（関連度スコア付き）
        """
        if not self._graph_built:
            await self.build_citation_graph()

        law_node = f"law_{law_id}"
        if law_node not in self.graph:
            return []

        # 直接引用している判例
        direct_cases = list(self.graph.predecessors(law_node))

        # 間接的に関連する判例（共通の法令を引用）
        indirect_cases = set()
        for case_node in direct_cases:
            # その判例が引用している他の法令
            other_laws = [
                n for n in self.graph.successors(case_node) if n.startswith("law_")
            ]
            # その法令を引用している他の判例
            for other_law in other_laws:
                related = self.graph.predecessors(other_law)
                indirect_cases.update(related)

        # 関連度スコアを計算
        results = []
        all_cases = set(direct_cases) | indirect_cases

        for case_node in all_cases:
            score = self._calculate_relevance_score(
                law_node, case_node, is_direct=(case_node in direct_cases)
            )

            case_data = self.graph.nodes[case_node]["data"]
            results.append(
                {
                    "case_id": case_data.case_id,
                    "case_name": case_data.case_name,
                    "court_name": case_data.court_name,
                    "decision_date": case_data.decision_date.isoformat(),
                    "relevance_score": score,
                    "is_direct_citation": case_node in direct_cases,
                }
            )

        # スコア順にソート
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results

    def _calculate_relevance_score(
        self, law_node: str, case_node: str, is_direct: bool
    ) -> float:
        """
        関連度スコアを計算

        直接引用: 1.0
        間接引用: PageRankベースのスコア
        """
        if is_direct:
            return 1.0

        try:
            pagerank = nx.pagerank(self.graph)
            return pagerank.get(case_node, 0.0)
        except Exception:
            return 0.5

    async def get_most_cited_laws(self, limit: int = 10) -> List[Dict[str, Any]]:
        """最も引用されている法令を取得"""
        if not self._graph_built:
            await self.build_citation_graph()

        law_citations: Dict[str, Dict[str, Any]] = {}
        for node in self.graph.nodes():
            if node.startswith("law_"):
                # この法令を引用している判例数
                citation_count = len(list(self.graph.predecessors(node)))
                law_data = self.graph.nodes[node]["data"]
                law_citations[node] = {
                    "law_id": law_data.law_id,
                    "law_name": law_data.law_name,
                    "citation_count": citation_count,
                }

        sorted_laws = sorted(
            law_citations.values(), key=lambda x: x["citation_count"], reverse=True
        )
        return sorted_laws[:limit]

    async def visualize_relationships(
        self, center_id: str, center_type: str = "law", depth: int = 2
    ) -> Dict[str, Any]:
        """
        特定の法令/判例を中心とした関連図データを生成

        Args:
            center_id: 中心となるID
            center_type: "law" または "case"
            depth: 探索深度

        Returns:
            グラフビジュアライゼーション用のデータ
        """
        if not self._graph_built:
            await self.build_citation_graph()

        center_node = f"{center_type}_{center_id}"
        if center_node not in self.graph:
            return {"nodes": [], "edges": [], "center": center_node, "error": "Node not found"}

        subgraph = nx.ego_graph(self.graph, center_node, radius=depth)

        # D3.jsなどで使用できる形式に変換
        nodes = []
        edges = []

        for node in subgraph.nodes():
            node_data = subgraph.nodes[node]
            nodes.append(
                {
                    "id": node,
                    "type": node_data["type"],
                    "name": node_data["name"],
                    "is_center": node == center_node,
                }
            )

        for source, target in subgraph.edges():
            edge_data = subgraph.edges[source, target]
            edges.append(
                {
                    "source": source,
                    "target": target,
                    "type": edge_data["type"],
                    "context": edge_data.get("context"),
                }
            )

        return {"nodes": nodes, "edges": edges, "center": center_node}

    async def _get_all_laws(self) -> List[LawDetail]:
        """全法令を取得"""
        return await self.egov_client.get_all_laws()

    async def _get_all_cases(self) -> List[CaseDetail]:
        """全判例を取得"""
        return await self.case_repo.get_all_cases()

    async def _get_all_references(self) -> List[CaseReference]:
        """全引用関係を取得"""
        return await self.case_repo.get_all_references()
