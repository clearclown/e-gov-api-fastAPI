"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "e-gov API FastAPI"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/egov_db"

    # Courts website
    courts_base_url: str = "https://www.courts.go.jp"
    scraper_timeout: int = 30
    scraper_rate_limit: int = 10  # requests per minute

    # API settings
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]


settings = Settings()
