"""Repository for managing embeddings in the database"""

from typing import List, Optional, Tuple
import numpy as np
from app.core.database import db
from app.models.law import LawDetail
from app.models.case import CaseDetail


class EmbeddingRepository:
    """埋め込みベクトルのリポジトリ"""

    async def get_all_laws(self) -> List[LawDetail]:
        """
        全ての法令を取得

        Returns:
            法令詳細のリスト
        """
        query = """
            SELECT law_id, law_number, law_name, promulgation_date,
                   enforcement_date, category, full_text, toc, appendix, last_updated
            FROM laws
            ORDER BY law_id
        """

        laws = []
        async with db.get_cursor() as cur:
            await cur.execute(query)
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

    async def get_all_cases(self) -> List[CaseDetail]:
        """
        全ての判例を取得

        Returns:
            判例詳細のリスト
        """
        query = """
            SELECT case_id, case_number, case_name, court_name, decision_date,
                   case_type, summary, holdings, case_summary, main_text,
                   cited_laws, related_cases
            FROM cases
            ORDER BY case_id
        """

        cases = []
        async with db.get_cursor() as cur:
            await cur.execute(query)
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

    async def save_law_embedding(
        self,
        law_id: str,
        chunk_index: int,
        chunk_text: str,
        embedding: np.ndarray,
    ) -> None:
        """
        法令の埋め込みベクトルを保存

        Args:
            law_id: 法令ID
            chunk_index: チャンク番号
            chunk_text: チャンクテキスト
            embedding: 埋め込みベクトル
        """
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        query = """
            INSERT INTO law_embeddings (law_id, chunk_index, chunk_text, embedding)
            VALUES (%s, %s, %s, %s::vector)
            ON CONFLICT (law_id, chunk_index)
            DO UPDATE SET chunk_text = EXCLUDED.chunk_text,
                         embedding = EXCLUDED.embedding
        """

        async with db.get_cursor() as cur:
            await cur.execute(query, (law_id, chunk_index, chunk_text, embedding_str))
            await cur.connection.commit()

    async def save_case_embedding(
        self,
        case_id: str,
        chunk_index: int,
        chunk_text: str,
        embedding: np.ndarray,
    ) -> None:
        """
        判例の埋め込みベクトルを保存

        Args:
            case_id: 判例ID
            chunk_index: チャンク番号
            chunk_text: チャンクテキスト
            embedding: 埋め込みベクトル
        """
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        query = """
            INSERT INTO case_embeddings (case_id, chunk_index, chunk_text, embedding)
            VALUES (%s, %s, %s, %s::vector)
            ON CONFLICT (case_id, chunk_index)
            DO UPDATE SET chunk_text = EXCLUDED.chunk_text,
                         embedding = EXCLUDED.embedding
        """

        async with db.get_cursor() as cur:
            await cur.execute(query, (case_id, chunk_index, chunk_text, embedding_str))
            await cur.connection.commit()

    async def get_law_embeddings_count(self) -> int:
        """
        法令埋め込みの総数を取得

        Returns:
            埋め込みの総数
        """
        query = "SELECT COUNT(*) FROM law_embeddings"

        async with db.get_cursor() as cur:
            await cur.execute(query)
            result = await cur.fetchone()
            return result[0] if result else 0

    async def get_case_embeddings_count(self) -> int:
        """
        判例埋め込みの総数を取得

        Returns:
            埋め込みの総数
        """
        query = "SELECT COUNT(*) FROM case_embeddings"

        async with db.get_cursor() as cur:
            await cur.execute(query)
            result = await cur.fetchone()
            return result[0] if result else 0

    async def delete_law_embeddings(self, law_id: str) -> None:
        """
        指定された法令の埋め込みを削除

        Args:
            law_id: 法令ID
        """
        query = "DELETE FROM law_embeddings WHERE law_id = %s"

        async with db.get_cursor() as cur:
            await cur.execute(query, (law_id,))
            await cur.connection.commit()

    async def delete_case_embeddings(self, case_id: str) -> None:
        """
        指定された判例の埋め込みを削除

        Args:
            case_id: 判例ID
        """
        query = "DELETE FROM case_embeddings WHERE case_id = %s"

        async with db.get_cursor() as cur:
            await cur.execute(query, (case_id,))
            await cur.connection.commit()
