"""RAG (Retrieval-Augmented Generation) Service for legal information"""

from typing import List, Optional
import anthropic
from sentence_transformers import SentenceTransformer
import numpy as np
from app.models.law import LawDetail
from app.models.case import CaseDetail
from app.core.config import settings
from app.core.database import db


class RAGService:
    """RAG（Retrieval-Augmented Generation）サービス"""

    def __init__(
        self,
        embedding_model: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
    ):
        """
        Initialize RAG service

        Args:
            embedding_model: Embedding model name (defaults to settings)
            anthropic_api_key: Anthropic API key (defaults to settings)
        """
        model_name = embedding_model or settings.embedding_model
        self.embedding_model = SentenceTransformer(model_name)

        api_key = anthropic_api_key or settings.anthropic_api_key
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None

    async def search_with_context(
        self,
        query: str,
        search_type: str = "both",
        top_k: Optional[int] = None,
    ) -> dict:
        """
        コンテキストを考慮した検索

        Args:
            query: 自然言語クエリ
            search_type: 検索対象（"law", "case", "both"）
            top_k: 取得件数（デフォルトは設定値）

        Returns:
            検索結果と関連コンテキスト
        """
        top_k = top_k or settings.rag_top_k

        # クエリの埋め込みベクトル生成
        query_embedding = self.embedding_model.encode(query)

        results = {"query": query, "laws": [], "cases": [], "context": ""}

        # ベクトル検索で関連文書を取得
        if search_type in ["law", "both"]:
            results["laws"] = await self._search_laws(query_embedding, top_k)

        if search_type in ["case", "both"]:
            results["cases"] = await self._search_cases(query_embedding, top_k)

        # コンテキスト生成
        results["context"] = self._build_context(results["laws"], results["cases"])

        return results

    async def _search_laws(
        self, embedding: np.ndarray, top_k: int
    ) -> List[LawDetail]:
        """
        法令のベクトル検索

        Args:
            embedding: クエリの埋め込みベクトル
            top_k: 取得件数

        Returns:
            法令詳細のリスト
        """
        # pgvector を使用したベクトル検索
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        query = """
            SELECT DISTINCT ON (l.law_id)
                l.law_id,
                l.law_number,
                l.law_name,
                l.promulgation_date,
                l.enforcement_date,
                l.category,
                l.full_text,
                l.toc,
                l.appendix,
                l.last_updated,
                le.embedding <=> %s::vector AS distance
            FROM laws l
            JOIN law_embeddings le ON l.law_id = le.law_id
            WHERE le.embedding IS NOT NULL
            ORDER BY l.law_id, distance
            LIMIT %s
        """

        laws = []
        async with db.get_cursor() as cur:
            await cur.execute(query, (embedding_str, top_k))
            rows = await cur.fetchall()

            for row in rows:
                law = LawDetail(
                    law_id=row[0],
                    law_number=row[1],
                    law_name=row[2],
                    promulgation_date=row[3],
                    enforcement_date=row[4],
                    category=row[5],
                    full_text=row[6],
                    toc=row[7],
                    appendix=row[8],
                    last_updated=row[9],
                )
                laws.append(law)

        return laws

    async def _search_cases(
        self, embedding: np.ndarray, top_k: int
    ) -> List[CaseDetail]:
        """
        判例のベクトル検索

        Args:
            embedding: クエリの埋め込みベクトル
            top_k: 取得件数

        Returns:
            判例詳細のリスト
        """
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        query = """
            SELECT DISTINCT ON (c.case_id)
                c.case_id,
                c.case_number,
                c.case_name,
                c.court_name,
                c.decision_date,
                c.case_type,
                c.summary,
                c.holdings,
                c.case_summary,
                c.main_text,
                c.cited_laws,
                c.related_cases,
                ce.embedding <=> %s::vector AS distance
            FROM cases c
            JOIN case_embeddings ce ON c.case_id = ce.case_id
            WHERE ce.embedding IS NOT NULL
            ORDER BY c.case_id, distance
            LIMIT %s
        """

        cases = []
        async with db.get_cursor() as cur:
            await cur.execute(query, (embedding_str, top_k))
            rows = await cur.fetchall()

            for row in rows:
                case = CaseDetail(
                    case_id=row[0],
                    case_number=row[1],
                    case_name=row[2],
                    court_name=row[3],
                    decision_date=row[4],
                    case_type=row[5],
                    summary=row[6],
                    holdings=row[7],
                    case_summary=row[8],
                    main_text=row[9],
                    cited_laws=row[10] or [],
                    related_cases=row[11] or [],
                )
                cases.append(case)

        return cases

    def _build_context(
        self, laws: List[LawDetail], cases: List[CaseDetail]
    ) -> str:
        """
        検索結果からコンテキストを構築

        Args:
            laws: 法令リスト
            cases: 判例リスト

        Returns:
            構築されたコンテキスト文字列
        """
        context_parts = []

        if laws:
            context_parts.append("【関連法令】")
            for law in laws:
                excerpt = law.full_text[:200] + "..." if len(law.full_text) > 200 else law.full_text
                context_parts.append(f"- {law.law_name}: {excerpt}")

        if cases:
            context_parts.append("\n【関連判例】")
            for case in cases:
                context_parts.append(
                    f"- {case.case_name} ({case.decision_date}): {case.summary}"
                )

        return "\n".join(context_parts)

    async def generate_answer(self, query: str, context: str) -> str:
        """
        Claude APIを使用して回答生成

        Args:
            query: ユーザーの質問
            context: 検索結果から構築されたコンテキスト

        Returns:
            生成された回答

        Raises:
            ValueError: Anthropic API keyが設定されていない場合
        """
        if not self.client:
            raise ValueError(
                "Anthropic API key is not configured. "
                "Please set ANTHROPIC_API_KEY in your environment."
            )

        system_prompt = """あなたは日本の法律に詳しい専門家です。
提供されたコンテキスト（法令・判例）を基に、質問に正確に回答してください。
不確かな情報は提供せず、根拠となる法令や判例を明示してください。"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"""コンテキスト:
{context}

質問: {query}

上記のコンテキストを参考に、質問に回答してください。""",
                }
            ],
        )

        return message.content[0].text
