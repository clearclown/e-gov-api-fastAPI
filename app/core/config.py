"""
アプリケーション設定

環境変数からの設定読み込みおよびアプリケーション全体の設定を管理します。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """アプリケーション設定

    環境変数または.envファイルから設定を読み込みます。

    Attributes:
        app_name: アプリケーション名
        app_version: アプリケーションバージョン
        debug: デバッグモード
        egov_api_base_url: e-gov APIのベースURL
        egov_api_timeout: e-gov APIタイムアウト秒数
        redis_url: RedisサーバーURL
        redis_enabled: Redisキャッシュの有効/無効
        cache_ttl_law_detail: 法令詳細のキャッシュTTL（秒）
        cache_ttl_search: 検索結果のキャッシュTTL（秒）
        rate_limit_per_minute: 1分あたりのリクエスト制限
        cors_origins: CORS許可オリジン
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # アプリケーション基本設定
    app_name: str = "e-gov API FastAPI"
    app_version: str = "0.1.0"
    debug: bool = False

    # e-gov API設定
    egov_api_base_url: str = "https://elaws.e-gov.go.jp"
    egov_api_timeout: int = 30

    # Redis設定
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = True

    # キャッシュTTL設定（秒）
    cache_ttl_law_detail: int = 86400  # 24時間
    cache_ttl_search: int = 3600  # 1時間

    # レート制限
    rate_limit_per_minute: int = 60

    # CORS設定
    cors_origins: list[str] = ["*"]

    # ログ設定
    log_level: str = "INFO"


# グローバル設定インスタンス
settings = Settings()
