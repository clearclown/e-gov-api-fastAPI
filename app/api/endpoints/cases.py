"""
判例API エンドポイント

判例の検索、詳細取得のためのREST APIエンドポイント。
"""

from fastapi import APIRouter, Query, HTTPException, Path, Depends
from typing import Optional, Literal, List
from datetime import date
import logging

from app.models.case import (
    CaseSearchResponse,
    CaseSearchResult,
    CaseDetail,
    CourtInfo,
)
from app.services.case_service import CaseService
from app.core.cache import law_cache
from app.core.exceptions import (
    InvalidParameterError,
    EGovAPITimeoutError,
    EGovAPIConnectionError,
)

logger = logging.getLogger(__name__)

# APIルーター
router = APIRouter(prefix="/api/v1/cases", tags=["cases"])


async def get_case_service() -> CaseService:
    """判例サービスの依存性注入

    Yields:
        CaseService: 接続済みのサービス
    """
    service = CaseService()
    try:
        await service.connect()
        yield service
    finally:
        await service.disconnect()


@router.get(
    "/search",
    response_model=CaseSearchResponse,
    summary="判例検索",
    description="キーワードによる判例検索を実行します。",
    responses={
        200: {"description": "検索成功"},
        400: {"description": "無効なパラメータ"},
        429: {"description": "レート制限超過"},
        500: {"description": "サーバーエラー"},
    }
)
async def search_cases(
    keywords: str = Query(
        ...,
        description="検索キーワード",
        min_length=1,
        max_length=100,
        examples=["特許権侵害"]
    ),
    court_name: Optional[str] = Query(
        None,
        description="裁判所名でフィルター",
        examples=["知的財産高等裁判所"]
    ),
    case_type: Optional[Literal["民事", "刑事", "行政"]] = Query(
        None,
        description="事件種別でフィルター",
        examples=["行政"]
    ),
    date_from: Optional[date] = Query(
        None,
        description="判決日の開始日（YYYY-MM-DD形式）"
    ),
    date_to: Optional[date] = Query(
        None,
        description="判決日の終了日（YYYY-MM-DD形式）"
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
    service: CaseService = Depends(get_case_service)
) -> CaseSearchResponse:
    """判例検索API

    指定されたキーワードで判例を検索します。

    Args:
        keywords: 検索キーワード
        court_name: 裁判所名でフィルター
        case_type: 事件種別でフィルター
        date_from: 判決日の開始日
        date_to: 判決日の終了日
        limit: 取得件数
        offset: オフセット
        service: 判例サービス

    Returns:
        CaseSearchResponse: 検索結果

    Raises:
        HTTPException: エラー発生時
    """
    try:
        # キャッシュキーの生成
        cache_params = {
            "keywords": keywords,
            "court_name": court_name,
            "case_type": case_type,
            "date_from": str(date_from) if date_from else None,
            "date_to": str(date_to) if date_to else None,
            "limit": limit,
            "offset": offset
        }

        # キャッシュチェック
        cached_results = await law_cache.get_search_results(cache_params)
        if cached_results is not None:
            logger.info(f"判例検索キャッシュヒット: keywords={keywords}")
            return CaseSearchResponse(
                total=len(cached_results),
                limit=limit,
                offset=offset,
                results=[CaseSearchResult(**r) for r in cached_results]
            )

        # 判例サービスで検索
        results = await service.search_cases(
            keywords=keywords,
            court_name=court_name,
            case_type=case_type,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )

        # キャッシュに保存
        results_dict = [r.model_dump() for r in results]
        await law_cache.set_search_results(cache_params, results_dict)

        logger.info(f"判例検索完了: keywords={keywords}, 件数={len(results)}")

        return CaseSearchResponse(
            total=len(results),
            limit=limit,
            offset=offset,
            results=results
        )

    except InvalidParameterError as e:
        logger.warning(f"無効なパラメータ: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except EGovAPITimeoutError as e:
        logger.error(f"タイムアウト: {e.message}")
        raise HTTPException(status_code=504, detail=e.message)
    except EGovAPIConnectionError as e:
        logger.error(f"接続エラー: {e.message}")
        raise HTTPException(status_code=503, detail="判例データベースへの接続に失敗しました")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました")


@router.get(
    "/{case_id}",
    response_model=CaseDetail,
    summary="判例詳細取得",
    description="指定された判例IDの詳細情報を取得します。",
    responses={
        200: {"description": "取得成功"},
        404: {"description": "判例が見つかりません"},
        429: {"description": "レート制限超過"},
        500: {"description": "サーバーエラー"},
    }
)
async def get_case_detail(
    case_id: str = Path(
        ...,
        description="判例ID",
        min_length=1,
        max_length=50,
        examples=["2020WLJPCA01010001"]
    ),
    service: CaseService = Depends(get_case_service)
) -> CaseDetail:
    """判例詳細取得API

    指定された判例IDの詳細情報を取得します。

    Args:
        case_id: 判例ID
        service: 判例サービス

    Returns:
        CaseDetail: 判例詳細

    Raises:
        HTTPException: エラー発生時
    """
    try:
        # キャッシュチェック
        cached_case = await law_cache.get_law(f"case:{case_id}")
        if cached_case is not None:
            logger.info(f"判例詳細キャッシュヒット: case_id={case_id}")
            return CaseDetail(**cached_case)

        # 判例サービスで取得
        case_detail = await service.get_case_detail(case_id)

        # キャッシュに保存
        await law_cache.set_law(f"case:{case_id}", case_detail.model_dump())

        logger.info(f"判例詳細取得完了: {case_detail.case_name}")
        return case_detail

    except InvalidParameterError as e:
        logger.warning(f"無効なパラメータ: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except EGovAPITimeoutError as e:
        logger.error(f"タイムアウト: {e.message}")
        raise HTTPException(status_code=504, detail=e.message)
    except EGovAPIConnectionError as e:
        logger.error(f"接続エラー: {e.message}")
        raise HTTPException(status_code=503, detail="判例データベースへの接続に失敗しました")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました")


@router.get(
    "/courts/list",
    response_model=List[CourtInfo],
    summary="裁判所一覧取得",
    description="利用可能な裁判所の一覧を取得します。",
    responses={
        200: {"description": "取得成功"},
        500: {"description": "サーバーエラー"},
    }
)
async def get_courts(
    service: CaseService = Depends(get_case_service)
) -> List[CourtInfo]:
    """裁判所一覧取得API

    Returns:
        List[CourtInfo]: 裁判所情報のリスト

    Raises:
        HTTPException: エラー発生時
    """
    try:
        courts = await service.get_courts()
        logger.info(f"裁判所一覧取得完了: {len(courts)}件")
        return courts

    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました")


@router.get(
    "/",
    summary="判例APIルート",
    description="判例APIの基本情報を返します。",
    include_in_schema=False
)
async def cases_root():
    """判例APIルートエンドポイント"""
    return {
        "message": "判例API",
        "version": "v1",
        "endpoints": {
            "search": "/api/v1/cases/search",
            "detail": "/api/v1/cases/{case_id}",
            "courts": "/api/v1/cases/courts/list"
        }
    }
