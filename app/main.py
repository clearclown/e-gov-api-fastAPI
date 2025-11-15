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
from app.core.database import db
from app.core.exceptions import EGovAPIError
from app.api.endpoints import laws, cases, analytics, conversation, summarization

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

    # データベース接続
    try:
        await db.connect()
        logger.info("✓ データベース接続成功")
    except Exception as e:
        logger.warning(f"⚠ データベース接続失敗（一部機能が制限されます）: {e}")

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

    # データベース切断
    await db.disconnect()
    logger.info("✓ データベース切断完了")

    logger.info("✓ アプリケーション終了完了")


# FastAPIアプリケーション作成
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## 日本法令・判例API

    e-gov法令APIおよび裁判所判例データと連携し、日本国内の法令・判例データを検索・取得し、
    AI技術を活用した高度な分析・要約・対話機能を提供するAPIです。

    ### Phase 1 & 2: 基本機能
    - **法令検索**: キーワードによる法令検索
    - **法令詳細取得**: 特定の法令の全文および詳細情報
    - **改正履歴取得**: 法令の改正履歴
    - **判例検索**: キーワード・裁判所・事件タイプによる判例検索
    - **判例詳細取得**: 特定の判例の全文および詳細情報

    ### Phase 3: AI統合機能
    - **RAG検索**: ベクトル検索による意味的な法令・判例検索
    - **コンテキスト生成**: 関連する法令・判例の自動抽出
    - **Claude API連携**: 自然言語での質問応答

    ### Phase 4: 高度な分析機能
    - **関係分析**: 法令と判例の関連性をグラフ構造で分析
    - **ネットワーク可視化**: 判例の引用関係をネットワークで表現
    - **要約生成**: 法令・判例の自動要約
    - **対話型インターフェース**: チャット形式での法律相談

    ### データソース
    - [e-gov 法令API](https://elaws.e-gov.go.jp/)
    - [裁判所ウェブサイト](https://www.courts.go.jp/)
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
app.include_router(cases.router)
app.include_router(analytics.router)
app.include_router(conversation.router)
app.include_router(summarization.router)


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
        "description": "日本法令・判例API - e-gov法令APIおよび裁判所判例データと連携した法律情報検索サービス",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "laws": {
                "search": "/api/v1/laws/search",
                "detail": "/api/v1/laws/{law_id}",
                "history": "/api/v1/laws/{law_id}/history"
            },
            "cases": {
                "search": "/api/v1/cases/search",
                "detail": "/api/v1/cases/{case_id}",
                "courts": "/api/v1/cases/courts/list"
            },
            "analytics": {
                "law_case_relationship": "/api/v1/analytics/law-case-relationship",
                "case_network": "/api/v1/analytics/case-network"
            },
            "conversation": {
                "ask": "/api/v1/conversation/ask"
            },
            "summarization": {
                "law": "/api/v1/summarization/law/{law_id}",
                "case": "/api/v1/summarization/case/{case_id}"
            }
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
