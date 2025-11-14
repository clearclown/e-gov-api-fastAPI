"""Law-related API endpoints (placeholder for future Phase 1 implementation)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.case_repository import CaseRepository

router = APIRouter(prefix="/laws", tags=["laws"])


@router.get("/{law_id}/cases", response_model=dict)
async def get_cases_by_law(
    law_id: str,
    limit: int = Query(50, ge=1, le=100, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """法令別判例取得API

    指定された法令IDを引用している判例を取得します。

    - **law_id**: 法令ID
    - **limit**: 取得件数（最大100件）
    - **offset**: オフセット（ページネーション用）
    """
    repo = CaseRepository(session)
    results, total = await repo.get_cases_by_law(law_id, limit=limit, offset=offset)

    # TODO: Fetch law name from law repository when Phase 1 is implemented
    law_name = "（法令情報未実装）"

    return {
        "law_id": law_id,
        "law_name": law_name,
        "total": total,
        "limit": limit,
        "offset": offset,
        "cases": [result.model_dump(mode="json") for result in results],
    }
