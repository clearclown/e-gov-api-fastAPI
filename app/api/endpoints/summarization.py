"""Summarization API endpoints"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.summarization_service import SummarizationService
from app.repositories.case_repository import CaseRepository
from app.services.egov_client import EGovAPIClient

router = APIRouter(prefix="/api/v1/summarize", tags=["summarization"])


@router.get("/case/{case_id}")
async def summarize_case(
    case_id: str,
    style: str = Query(
        "brief",
        regex="^(brief|detailed|plain)$",
        description="要約スタイル: brief(簡潔), detailed(詳細), plain(平易)",
    ),
) -> dict:
    """
    判例を要約

    指定されたスタイルで判例を自動要約します。

    Args:
        case_id: 判例ID（例: "CASE-2024-001"）
        style: 要約スタイル
            - brief: 簡潔（200文字程度）
            - detailed: 詳細（500文字程度）
            - plain: 平易な言葉（一般向け）

    Returns:
        要約テキスト

    Raises:
        HTTPException: 判例が見つからない場合
    """
    repo = CaseRepository()
    case = await repo.get_case_by_id(case_id)

    if not case:
        raise HTTPException(status_code=404, detail="判例が見つかりません")

    summarizer = SummarizationService()
    summary = await summarizer.summarize_case(case, style=style)

    return summary


@router.get("/law/{law_id}/article/{article_number}")
async def explain_article(law_id: str, article_number: str) -> dict:
    """
    法令の特定条文を平易に説明

    法律用語を分かりやすく解説し、具体例を交えて説明します。

    Args:
        law_id: 法令ID（例: "405AC0000000087"）
        article_number: 条文番号（例: "309" または "第309条"）

    Returns:
        条文の解説

    Raises:
        HTTPException: 法令または条文が見つからない場合
    """
    egov = EGovAPIClient()
    law = await egov.get_law_detail(law_id)

    if not law:
        raise HTTPException(status_code=404, detail="法令が見つかりません")

    summarizer = SummarizationService()
    explanation = await summarizer.explain_law_article(law, article_number)

    if "error" in explanation:
        raise HTTPException(status_code=404, detail=explanation["error"])

    return explanation


@router.get("/compare/laws")
async def compare_laws(
    law_id_1: str = Query(..., description="比較対象法令1のID"),
    law_id_2: str = Query(..., description="比較対象法令2のID"),
) -> dict:
    """
    2つの法令を比較要約

    2つの法令の主な違いや関連性をAIが自動的に分析します。

    Args:
        law_id_1: 比較対象法令1のID
        law_id_2: 比較対象法令2のID

    Returns:
        比較要約

    Note:
        この機能は Phase 3 で完全実装予定です（現在はモック）
    """
    summarizer = SummarizationService()
    comparison = await summarizer.generate_comparative_summary(law_id_1, law_id_2)

    return comparison
