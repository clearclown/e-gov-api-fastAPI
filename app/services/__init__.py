"""Services for the legal API"""

# RAGService は AI機能がインストールされている場合のみ利用可能
try:
    from app.services.rag_service import RAGService
    __all__ = ["RAGService"]
except ImportError:
    # sentence_transformers等のAI依存関係がない場合
    RAGService = None  # type: ignore
    __all__ = []
