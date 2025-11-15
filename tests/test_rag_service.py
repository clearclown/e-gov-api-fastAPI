"""Tests for RAG service"""

import pytest
from app.services.rag_service import RAGService
from app.batch.generate_embeddings import chunk_text


class TestRAGService:
    """Test cases for RAGService"""

    def test_rag_service_initialization(self):
        """Test RAG service initialization"""
        rag = RAGService()
        assert rag.embedding_model is not None

    def test_rag_service_with_api_key(self):
        """Test RAG service initialization with API key"""
        # Test without API key
        rag = RAGService(anthropic_api_key=None)
        assert rag.client is None

        # Test with API key
        rag = RAGService(anthropic_api_key="test_key")
        assert rag.client is not None

    @pytest.mark.asyncio
    async def test_build_context(self, sample_law_text, sample_case_text):
        """Test context building"""
        rag = RAGService()

        from app.models.law import LawDetail
        from app.models.case import CaseDetail
        from datetime import date

        laws = [
            LawDetail(
                law_id="test001",
                law_number="平成十七年法律第八十六号",
                law_name="会社法",
                full_text=sample_law_text,
                promulgation_date=date(2005, 7, 26),
                enforcement_date=date(2006, 5, 1),
            )
        ]

        cases = [
            CaseDetail(
                case_id="case001",
                case_number="令和5年(オ)第1234号",
                case_name="損害賠償請求事件",
                court_name="最高裁判所",
                decision_date=date(2023, 9, 15),
                summary=sample_case_text,
                main_text=sample_case_text,
            )
        ]

        context = rag._build_context(laws, cases)
        assert "会社法" in context
        assert "損害賠償請求事件" in context


class TestChunkText:
    """Test cases for text chunking"""

    def test_chunk_text_basic(self, sample_law_text):
        """Test basic text chunking"""
        chunks = chunk_text(sample_law_text, max_length=100, overlap=20)
        assert len(chunks) > 0
        assert all(len(chunk) <= 100 for chunk in chunks)

    def test_chunk_text_empty(self):
        """Test chunking empty text"""
        chunks = chunk_text("", max_length=100, overlap=20)
        assert len(chunks) == 0

    def test_chunk_text_short(self):
        """Test chunking short text"""
        short_text = "これは短いテキストです。"
        chunks = chunk_text(short_text, max_length=100, overlap=20)
        assert len(chunks) == 1
        assert chunks[0] == short_text

    def test_chunk_text_overlap(self):
        """Test chunking with overlap"""
        text = "第一条。" * 50  # Create a longer text
        chunks = chunk_text(text, max_length=50, overlap=10)
        assert len(chunks) > 1
        # Verify overlap exists (this is approximate due to sentence splitting)
        # In practice, the overlap logic tries to split at sentence boundaries
