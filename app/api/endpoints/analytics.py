"""Analytics API endpoints"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.relationship_analyzer import RelationshipAnalyzer

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/laws/{law_id}/related-cases")
async def get_related_cases(
    law_id: str, limit: int = Query(10, ge=1, le=100, description="取得件数")
) -> dict:
    """
    特定の法令に関連する判例を取得

    関連度スコア付きで返却します。
    直接引用している判例と、間接的に関連する判例を含みます。

    Args:
        law_id: 法令ID（例: "405AC0000000087"）
        limit: 取得件数（1-100）

    Returns:
        関連判例のリスト
    """
    analyzer = RelationshipAnalyzer()
    results = await analyzer.find_related_cases(law_id)

    return {
        "law_id": law_id,
        "total": len(results),
        "related_cases": results[:limit],
    }


@router.get("/laws/most-cited")
async def get_most_cited_laws(
    limit: int = Query(10, ge=1, le=100, description="取得件数")
) -> dict:
    """
    最も判例で引用されている法令ランキング

    Args:
        limit: 取得件数（1-100）

    Returns:
        引用回数が多い法令のリスト
    """
    analyzer = RelationshipAnalyzer()
    results = await analyzer.get_most_cited_laws(limit)

    return {
        "total": len(results),
        "laws": results,
    }


@router.get("/visualize/{type}/{id}")
async def visualize_relationships(
    type: str,
    id: str,
    depth: int = Query(2, ge=1, le=3, description="探索深度（1-3）"),
) -> dict:
    """
    法令・判例の関連図データを取得

    D3.jsなどのグラフビジュアライゼーションライブラリで使用可能な
    ノード・エッジ形式のデータを返します。

    Args:
        type: "law" または "case"
        id: 法令ID または 判例ID
        depth: 探索深度（1-3）

    Returns:
        グラフデータ（ノードとエッジのリスト）

    Raises:
        HTTPException: typeが無効な場合
    """
    if type not in ["law", "case"]:
        raise HTTPException(
            status_code=400,
            detail="type must be 'law' or 'case'",
        )

    analyzer = RelationshipAnalyzer()
    graph_data = await analyzer.visualize_relationships(
        center_id=id, center_type=type, depth=depth
    )

    if "error" in graph_data:
        raise HTTPException(
            status_code=404,
            detail=graph_data["error"],
        )

    return graph_data


@router.get("/graph/stats")
async def get_graph_stats() -> dict:
    """
    引用グラフの統計情報を取得

    Returns:
        グラフの統計情報（ノード数、エッジ数等）
    """
    analyzer = RelationshipAnalyzer()
    graph = await analyzer.build_citation_graph()

    # グラフの統計を計算
    law_nodes = [n for n in graph.nodes() if n.startswith("law_")]
    case_nodes = [n for n in graph.nodes() if n.startswith("case_")]

    return {
        "total_nodes": graph.number_of_nodes(),
        "total_edges": graph.number_of_edges(),
        "law_count": len(law_nodes),
        "case_count": len(case_nodes),
        "average_degree": sum(dict(graph.degree()).values()) / graph.number_of_nodes()
        if graph.number_of_nodes() > 0
        else 0,
    }
