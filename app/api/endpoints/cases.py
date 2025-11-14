"""Case law API endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.case import CaseDetail, CaseSearchResult
from app.repositories.case_repository import CaseRepository

router = APIRouter(prefix="/cases", tags=["cases"])


# Response models
class CaseSearchResponse(dict):  # type: ignore
    """判例検索APIレスポンス"""

    pass


class CasesByLawResponse(dict):  # type: ignore
    """法令別判例取得APIレスポンス"""

    pass


@router.get("/search", response_model=dict)
async def search_cases(
    q: str | None = Query(None, description="検索キーワード"),
    court: str | None = Query(None, description="裁判所種別"),
    type: str | None = Query(None, description="事件種別（civil, criminal, administrative, family）"),
    date_from: date | None = Query(None, description="判決日開始（YYYY-MM-DD）"),
    date_to: date | None = Query(None, description="判決日終了（YYYY-MM-DD）"),
    limit: int = Query(50, ge=1, le=100, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """判例検索API

    日本の裁判所の判例を検索します。

    - **q**: 検索キーワード（事件名、要旨、判決文から検索）
    - **court**: 裁判所種別（最高裁判所、高等裁判所、地方裁判所、家庭裁判所、簡易裁判所）
    - **type**: 事件種別（民事、刑事、行政、家事）
    - **date_from**: 判決日の開始日
    - **date_to**: 判決日の終了日
    - **limit**: 取得件数（最大100件）
    - **offset**: オフセット（ページネーション用）
    """
    repo = CaseRepository(session)

    # Map English type to Japanese
    case_type_map = {
        "civil": "民事",
        "criminal": "刑事",
        "administrative": "行政",
        "family": "家事",
    }
    case_type_jp = case_type_map.get(type) if type else None

    results, total = await repo.search_cases(
        query=q,
        court_type=court,
        case_type=case_type_jp,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [result.model_dump(mode="json") for result in results],
    }


@router.get("/{case_id}", response_model=CaseDetail)
async def get_case_detail(
    case_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> CaseDetail:
    """判例詳細取得API

    指定された判例IDの詳細情報を取得します。

    - **case_id**: 判例ID
    """
    repo = CaseRepository(session)
    case = await repo.get_case_by_id(case_id)

    if not case:
        raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

    return case
