"""SummarizationService のテスト"""

import pytest
from datetime import date
from app.services.summarization_service import SummarizationService
from app.models.case import CaseDetail
from app.models.law import LawDetail


@pytest.mark.asyncio
async def test_summarize_case_brief():
    """判例の簡潔な要約テスト"""
    service = SummarizationService()

    # テスト用の判例データ
    case = CaseDetail(
        case_id="TEST-001",
        case_name="テスト事件",
        court_name="最高裁判所",
        decision_date=date(2024, 1, 15),
        holdings="テスト判示事項",
        case_summary="テスト要旨",
        main_text="テスト全文",
    )

    # 簡潔な要約を生成
    result = await service.summarize_case(case, style="brief")

    # 必要なフィールドが含まれていることを確認
    assert "case_id" in result
    assert "case_name" in result
    assert "summary" in result
    assert "style" in result
    assert result["style"] == "brief"


@pytest.mark.asyncio
async def test_summarize_case_detailed():
    """判例の詳細な要約テスト"""
    service = SummarizationService()

    case = CaseDetail(
        case_id="TEST-001",
        case_name="テスト事件",
        court_name="最高裁判所",
        decision_date=date(2024, 1, 15),
        main_text="テスト全文",
    )

    # 詳細な要約を生成
    result = await service.summarize_case(case, style="detailed")

    assert result["style"] == "detailed"
    assert len(result["summary"]) > 0


@pytest.mark.asyncio
async def test_summarize_case_plain():
    """判例の平易な要約テスト"""
    service = SummarizationService()

    case = CaseDetail(
        case_id="TEST-001",
        case_name="テスト事件",
        court_name="最高裁判所",
        decision_date=date(2024, 1, 15),
        main_text="テスト全文",
    )

    # 平易な要約を生成
    result = await service.summarize_case(case, style="plain")

    assert result["style"] == "plain"
    assert len(result["summary"]) > 0


@pytest.mark.asyncio
async def test_explain_law_article():
    """法令条文解説テスト"""
    service = SummarizationService()

    # テスト用の法令データ
    law = LawDetail(
        law_id="TEST-LAW",
        law_name="テスト法",
        full_text="""第一条 テスト条文1
これはテストです。
第二条 テスト条文2
これもテストです。
""",
    )

    # 第一条の解説を生成
    result = await service.explain_law_article(law, "第一条")

    # エラーが含まれていないことを確認
    assert "error" not in result

    # 必要なフィールドが含まれていることを確認
    assert "law_id" in result
    assert "law_name" in result
    assert "article_number" in result
    assert "original_text" in result
    assert "explanation" in result


@pytest.mark.asyncio
async def test_explain_law_article_without_prefix():
    """条文番号（数字のみ）での解説テスト"""
    service = SummarizationService()

    law = LawDetail(
        law_id="TEST-LAW",
        law_name="テスト法",
        full_text="第1条 テスト\nテスト内容",
    )

    # 数字のみで指定
    result = await service.explain_law_article(law, "1")

    # 正規化されて処理されることを確認
    assert result["article_number"] == "第1条"


@pytest.mark.asyncio
async def test_explain_law_article_not_found():
    """存在しない条文の解説テスト"""
    service = SummarizationService()

    law = LawDetail(
        law_id="TEST-LAW",
        law_name="テスト法",
        full_text="第一条 テスト",
    )

    # 存在しない条文を指定
    result = await service.explain_law_article(law, "第999条")

    # エラーが含まれていることを確認
    assert "error" in result


@pytest.mark.asyncio
async def test_generate_comparative_summary():
    """法令比較要約テスト"""
    service = SummarizationService()

    # 比較要約を生成
    result = await service.generate_comparative_summary("LAW-001", "LAW-002")

    # 必要なフィールドが含まれていることを確認
    assert "law_id_1" in result
    assert "law_id_2" in result
    assert "comparison" in result
