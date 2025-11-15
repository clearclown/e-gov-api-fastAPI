"""Batch script to generate embeddings for laws and cases"""

import asyncio
import logging
from typing import List
from app.services.rag_service import RAGService
from app.repositories.embedding_repository import EmbeddingRepository
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def chunk_text(text: str, max_length: int = 500, overlap: int = 50) -> List[str]:
    """
    テキストを重複を持たせて分割

    Args:
        text: 分割するテキスト
        max_length: 各チャンクの最大文字数
        overlap: チャンク間の重複文字数

    Returns:
        分割されたテキストのリスト
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + max_length
        chunk = text[start:end]

        # 文の途中で切れないように調整（句点で分割）
        if end < text_length:
            last_period = chunk.rfind("。")
            if last_period > max_length // 2:  # チャンクが短すぎないように
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append(chunk)

        # 次のチャンクの開始位置（重複を考慮）
        start = end - overlap if end < text_length else text_length

    return chunks


async def generate_law_embeddings():
    """法令データの埋め込みベクトルを生成"""
    logger.info("Starting law embeddings generation...")

    rag = RAGService()
    repo = EmbeddingRepository()

    try:
        laws = await repo.get_all_laws()
        logger.info(f"Found {len(laws)} laws to process")

        processed_count = 0
        total_chunks = 0

        for law in laws:
            try:
                # 長文を分割（チャンキング）
                chunks = chunk_text(
                    law.full_text,
                    max_length=settings.rag_chunk_size,
                    overlap=settings.rag_chunk_overlap,
                )

                for idx, chunk in enumerate(chunks):
                    # 埋め込みベクトル生成
                    embedding = rag.embedding_model.encode(chunk)

                    # データベースに保存
                    await repo.save_law_embedding(
                        law_id=law.law_id,
                        chunk_index=idx,
                        chunk_text=chunk,
                        embedding=embedding,
                    )

                    total_chunks += 1

                processed_count += 1

                if processed_count % 10 == 0:
                    logger.info(f"Processed {processed_count}/{len(laws)} laws")

            except Exception as e:
                logger.error(f"Error processing law {law.law_id}: {e}")
                continue

        logger.info(
            f"Law embeddings generation completed. "
            f"Processed {processed_count} laws, {total_chunks} chunks"
        )

    except Exception as e:
        logger.error(f"Fatal error during law embeddings generation: {e}")
        raise


async def generate_case_embeddings():
    """判例データの埋め込みベクトルを生成"""
    logger.info("Starting case embeddings generation...")

    rag = RAGService()
    repo = EmbeddingRepository()

    try:
        cases = await repo.get_all_cases()
        logger.info(f"Found {len(cases)} cases to process")

        processed_count = 0
        total_chunks = 0

        for case in cases:
            try:
                # 判例の主要なテキストを結合
                full_text = f"{case.summary}\n\n{case.case_summary or ''}\n\n{case.main_text}"

                # 長文を分割（チャンキング）
                chunks = chunk_text(
                    full_text,
                    max_length=settings.rag_chunk_size,
                    overlap=settings.rag_chunk_overlap,
                )

                for idx, chunk in enumerate(chunks):
                    # 埋め込みベクトル生成
                    embedding = rag.embedding_model.encode(chunk)

                    # データベースに保存
                    await repo.save_case_embedding(
                        case_id=case.case_id,
                        chunk_index=idx,
                        chunk_text=chunk,
                        embedding=embedding,
                    )

                    total_chunks += 1

                processed_count += 1

                if processed_count % 10 == 0:
                    logger.info(f"Processed {processed_count}/{len(cases)} cases")

            except Exception as e:
                logger.error(f"Error processing case {case.case_id}: {e}")
                continue

        logger.info(
            f"Case embeddings generation completed. "
            f"Processed {processed_count} cases, {total_chunks} chunks"
        )

    except Exception as e:
        logger.error(f"Fatal error during case embeddings generation: {e}")
        raise


async def main():
    """メインエントリポイント"""
    logger.info("Starting embeddings generation batch process")

    try:
        # 法令の埋め込み生成
        await generate_law_embeddings()

        # 判例の埋め込み生成
        await generate_case_embeddings()

        logger.info("All embeddings generation completed successfully")

    except Exception as e:
        logger.error(f"Embeddings generation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
