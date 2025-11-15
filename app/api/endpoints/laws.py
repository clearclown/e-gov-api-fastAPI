"""
法令API エンドポイント

法令の検索、詳細取得、改正履歴取得のためのREST APIエンドポイント。
"""

from fastapi import APIRouter, Query, HTTPException, Path, Depends
from typing import Optional, Literal
import logging

from app.models.law import (
    LawSearchResponse,
    LawSearchResult,
    LawDetail,
    LawHistoryResponse,
)
from app.services.egov_client import EGovAPIClient
from app.core.cache import law_cache
from app.core.exceptions import (
    LawNotFoundError,
    EGovAPITimeoutError,
    EGovAPIRateLimitError,
    EGovAPIConnectionError,
    InvalidParameterError,
)

logger = logging.getLogger(__name__)

# APIルーター
router = APIRouter(prefix="/api/v1/laws", tags=["laws"])


async def get_egov_client() -> EGovAPIClient:
    """e-gov APIクライアントの依存性注入

    Yields:
        EGovAPIClient: 接続済みのAPIクライアント
    """
    client = EGovAPIClient()
    try:
        await client.connect()
        yield client
    finally:
        await client.disconnect()


@router.get(
    "/search",
    response_model=LawSearchResponse,
    summary="法令検索",
    description="キーワードによる法令検索を実行します。",
    responses={
        200: {"description": "検索成功"},
        400: {"description": "無効なパラメータ"},
        429: {"description": "レート制限超過"},
        500: {"description": "サーバーエラー"},
    }
)
async def search_laws(
    q: str = Query(
        ...,
        description="検索キーワード",
        min_length=1,
        max_length=100,
        example="会社法"
    ),
    type: Optional[Literal["law", "ordinance", "ministerial_order"]] = Query(
        None,
        description="法令種別（law: 法律、ordinance: 政令、ministerial_order: 省令）",
        example="law"
    ),
    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="取得件数（最大100）"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="オフセット"
    ),
    client: EGovAPIClient = Depends(get_egov_client)
) -> LawSearchResponse:
    """法令検索API

    指定されたキーワードで法令を検索します。

    Args:
        q: 検索キーワード
        type: 法令種別
        limit: 取得件数
        offset: オフセット
        client: e-gov APIクライアント

    Returns:
        LawSearchResponse: 検索結果

    Raises:
        HTTPException: エラー発生時
    """
    try:
        # キャッシュキーの生成
        cache_params = {
            "q": q,
            "type": type,
            "limit": limit,
            "offset": offset
        }

        # キャッシュチェック
        cached_results = await law_cache.get_search_results(cache_params)
        if cached_results is not None:
            logger.info(f"検索キャッシュヒット: q={q}")
            return LawSearchResponse(
                total=len(cached_results),
                limit=limit,
                offset=offset,
                results=[LawSearchResult(**r) for r in cached_results]
            )

        # e-gov APIで検索
        results = await client.search_laws(
            query=q,
            law_type=type,
            limit=limit,
            offset=offset
        )

        # キャッシュに保存
        results_dict = [r.model_dump() for r in results]
        await law_cache.set_search_results(cache_params, results_dict)

        logger.info(f"法令検索完了: q={q}, 件数={len(results)}")

        return LawSearchResponse(
            total=len(results),
            limit=limit,
            offset=offset,
            results=results
        )

    except InvalidParameterError as e:
        logger.warning(f"無効なパラメータ: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except EGovAPIRateLimitError as e:
        logger.warning(f"レート制限: {e.message}")
        raise HTTPException(status_code=429, detail=e.message)
    except EGovAPITimeoutError as e:
        logger.error(f"タイムアウト: {e.message}")
        raise HTTPException(status_code=504, detail=e.message)
    except EGovAPIConnectionError as e:
        logger.error(f"接続エラー: {e.message}")
        raise HTTPException(status_code=503, detail="e-gov APIへの接続に失敗しました")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました")


@router.get(
    "/{law_id}",
    response_model=LawDetail,
    summary="法令詳細取得",
    description="指定された法令IDの詳細情報を取得します。",
    responses={
        200: {"description": "取得成功"},
        404: {"description": "法令が見つかりません"},
        429: {"description": "レート制限超過"},
        500: {"description": "サーバーエラー"},
    }
)
async def get_law_detail(
    law_id: str = Path(
        ...,
        description="法令ID",
        min_length=1,
        max_length=50,
        example="405AC0000000087"
    ),
    format: Literal["json", "xml"] = Query(
        "json",
        description="レスポンス形式"
    ),
    client: EGovAPIClient = Depends(get_egov_client)
) -> LawDetail:
    """法令詳細取得API

    指定された法令IDの詳細情報を取得します。

    Args:
        law_id: 法令ID
        format: レスポンス形式（現在はjsonのみサポート）
        client: e-gov APIクライアント

    Returns:
        LawDetail: 法令詳細

    Raises:
        HTTPException: エラー発生時
    """
    try:
        # キャッシュチェック
        cached_law = await law_cache.get_law(law_id)
        if cached_law is not None:
            logger.info(f"法令詳細キャッシュヒット: law_id={law_id}")
            return LawDetail(**cached_law)

        # e-gov APIで取得
        law_detail = await client.get_law_detail(law_id)

        # キャッシュに保存
        await law_cache.set_law(law_id, law_detail.model_dump())

        logger.info(f"法令詳細取得完了: {law_detail.law_name}")

        # Note: XML形式のサポートは将来的な拡張として実装可能
        return law_detail

    except LawNotFoundError as e:
        logger.warning(f"法令が見つかりません: {law_id}")
        raise HTTPException(status_code=404, detail=e.message)
    except InvalidParameterError as e:
        logger.warning(f"無効なパラメータ: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except EGovAPIRateLimitError as e:
        logger.warning(f"レート制限: {e.message}")
        raise HTTPException(status_code=429, detail=e.message)
    except EGovAPITimeoutError as e:
        logger.error(f"タイムアウト: {e.message}")
        raise HTTPException(status_code=504, detail=e.message)
    except EGovAPIConnectionError as e:
        logger.error(f"接続エラー: {e.message}")
        raise HTTPException(status_code=503, detail="e-gov APIへの接続に失敗しました")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました")


@router.get(
    "/{law_id}/history",
    response_model=LawHistoryResponse,
    summary="法令改正履歴取得",
    description="指定された法令の改正履歴を取得します。",
    responses={
        200: {"description": "取得成功"},
        404: {"description": "法令が見つかりません"},
        429: {"description": "レート制限超過"},
        500: {"description": "サーバーエラー"},
    }
)
async def get_law_history(
    law_id: str = Path(
        ...,
        description="法令ID",
        min_length=1,
        max_length=50,
        example="405AC0000000087"
    ),
    client: EGovAPIClient = Depends(get_egov_client)
) -> LawHistoryResponse:
    """法令改正履歴取得API

    指定された法令の改正履歴を取得します。

    Args:
        law_id: 法令ID
        client: e-gov APIクライアント

    Returns:
        LawHistoryResponse: 改正履歴

    Raises:
        HTTPException: エラー発生時
    """
    try:
        # e-gov APIで改正履歴を取得
        amendments = await client.get_law_history(law_id)

        # 法令名を取得（キャッシュから試行）
        law_name = "不明"
        cached_law = await law_cache.get_law(law_id)
        if cached_law:
            law_name = cached_law.get("law_name", "不明")
        elif amendments:
            # 改正履歴がある場合、法令詳細も取得
            try:
                detail = await client.get_law_detail(law_id)
                law_name = detail.law_name
            except Exception:
                pass

        logger.info(f"改正履歴取得完了: {law_name}, 件数={len(amendments)}")

        return LawHistoryResponse(
            law_id=law_id,
            law_name=law_name,
            amendments=amendments
        )

    except LawNotFoundError as e:
        logger.warning(f"法令が見つかりません: {law_id}")
        raise HTTPException(status_code=404, detail=e.message)
    except InvalidParameterError as e:
        logger.warning(f"無効なパラメータ: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except EGovAPIRateLimitError as e:
        logger.warning(f"レート制限: {e.message}")
        raise HTTPException(status_code=429, detail=e.message)
    except EGovAPITimeoutError as e:
        logger.error(f"タイムアウト: {e.message}")
        raise HTTPException(status_code=504, detail=e.message)
    except EGovAPIConnectionError as e:
        logger.error(f"接続エラー: {e.message}")
        raise HTTPException(status_code=503, detail="e-gov APIへの接続に失敗しました")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました")


@router.get(
    "/",
    summary="法令APIルート",
    description="法令APIの基本情報を返します。",
    include_in_schema=False
)
async def laws_root():
    """法令APIルートエンドポイント"""
    return {
        "message": "法令API",
        "version": "v1",
        "endpoints": {
            "search": "/api/v1/laws/search",
            "detail": "/api/v1/laws/{law_id}",
            "history": "/api/v1/laws/{law_id}/history"
        }
    }
