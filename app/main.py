"""
e-gov API FastAPI メインアプリケーション

日本の法令情報を提供するFastAPIアプリケーション。
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.cache import law_cache
from app.core.exceptions import EGovAPIError
from app.api.endpoints import laws

# ロギング設定
log_level_str = settings.log_level.strip('"').strip("'").upper()
logging.basicConfig(
    level=getattr(logging, log_level_str, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理

    起動時と終了時の処理を定義します。

    Args:
        app: FastAPIアプリケーションインスタンス
    """
    # 起動時処理
    logger.info("=" * 50)
    logger.info(f"{settings.app_name} v{settings.app_version} 起動中...")
    logger.info("=" * 50)

    # Redisキャッシュ接続
    if settings.redis_enabled:
        try:
            await law_cache.connect()
            logger.info("✓ Redisキャッシュ接続成功")
        except Exception as e:
            logger.warning(f"⚠ Redisキャッシュ接続失敗（キャッシュなしで続行）: {e}")

    logger.info("✓ アプリケーション起動完了")
    logger.info(f"✓ デバッグモード: {settings.debug}")
    logger.info(f"✓ e-gov API: {settings.egov_api_base_url}")

    yield

    # 終了時処理
    logger.info("アプリケーション終了処理開始...")

    # Redisキャッシュ切断
    if settings.redis_enabled:
        await law_cache.disconnect()
        logger.info("✓ Redisキャッシュ切断完了")

    logger.info("✓ アプリケーション終了完了")


# FastAPIアプリケーション作成
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## 日本法令API

    e-gov法令APIと連携し、日本国内の法令データを検索・取得するAPIです。

    ### 主な機能
    - **法令検索**: キーワードによる法令検索
    - **法令詳細取得**: 特定の法令の全文および詳細情報
    - **改正履歴取得**: 法令の改正履歴

    ### データソース
    - [e-gov 法令API](https://elaws.e-gov.go.jp/)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug
)

# CORSミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# リクエスト処理時間ログミドルウェア
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """リクエスト処理時間をログに記録

    Args:
        request: HTTPリクエスト
        call_next: 次の処理

    Returns:
        HTTPレスポンス
    """
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Time: {process_time:.3f}s"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# グローバル例外ハンドラー
@app.exception_handler(EGovAPIError)
async def egov_api_error_handler(request: Request, exc: EGovAPIError):
    """e-gov APIエラーハンドラー

    Args:
        request: HTTPリクエスト
        exc: e-gov API例外

    Returns:
        JSONレスポンス
    """
    logger.error(f"e-gov APIエラー: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """一般例外ハンドラー

    Args:
        request: HTTPリクエスト
        exc: 例外

    Returns:
        JSONレスポンス
    """
    logger.error(f"予期しないエラー: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "内部サーバーエラーが発生しました",
            "path": str(request.url.path)
        }
    )


# ルーター登録
app.include_router(laws.router)


# ルートエンドポイント
@app.get(
    "/",
    tags=["root"],
    summary="APIルート",
    description="APIの基本情報を返します"
)
async def root():
    """ルートエンドポイント

    Returns:
        基本情報
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "日本法令API - e-gov法令APIと連携した法令情報検索サービス",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "laws_search": "/api/v1/laws/search",
            "law_detail": "/api/v1/laws/{law_id}",
            "law_history": "/api/v1/laws/{law_id}/history"
        }
    }


# ヘルスチェックエンドポイント
@app.get(
    "/health",
    tags=["health"],
    summary="ヘルスチェック",
    description="APIサーバーの稼働状態を確認します"
)
async def health_check():
    """ヘルスチェックエンドポイント

    Returns:
        稼働状態
    """
    # Redis接続確認
    redis_status = "healthy"
    if settings.redis_enabled:
        try:
            if law_cache.redis:
                await law_cache.redis.ping()
            else:
                redis_status = "disconnected"
        except Exception as e:
            redis_status = f"unhealthy: {str(e)}"
    else:
        redis_status = "disabled"

    return {
        "status": "healthy",
        "version": settings.app_version,
        "cache": {
            "redis": redis_status,
            "enabled": settings.redis_enabled
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
