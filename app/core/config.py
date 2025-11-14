"""Application configuration"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    api_title: str = "e-gov Legal API"
    api_version: str = "0.1.0"
    api_description: str = "FastAPI-based API server for accessing Japanese legal information"

    # Database Settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/legal_db"

    # Anthropic API Settings
    anthropic_api_key: Optional[str] = None

    # Embedding Model Settings
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    embedding_dimension: int = 768

    # RAG Settings
    rag_top_k: int = 5
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 50

    # Vector Search Settings
    vector_index_lists: int = 100

    # e-gov API Settings
    egov_api_base_url: str = "https://elaws.e-gov.go.jp/api/1"

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
