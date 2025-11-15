"""Unit tests for case repository."""

from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import CaseDetail, CaseType, CourtType
from app.repositories.case_repository import CaseRepository


@pytest.mark.asyncio
async def test_save_and_get_case(test_db_session: AsyncSession) -> None:
    """Test saving and retrieving a case."""
    repo = CaseRepository(test_db_session)

    # Create test case
    test_case = CaseDetail(
        case_id="test_case_001",
        case_number="令和2年(オ)第123号",
        case_name="テスト事件",
        court_type=CourtType.SUPREME,
        court_name="最高裁判所第一小法廷",
        case_type=CaseType.CIVIL,
        decision_date=date(2020, 6, 15),
        summary="テスト要旨",
        main_text="テスト判決全文",
        holdings="テスト判示事項",
        case_summary="テスト裁判要旨",
        references=["law_001"],
        related_cases=["case_002"],
        metadata={"source": "test"},
    )

    # Save case
    case_id = await repo.save_case(test_case)
    await test_db_session.commit()

    assert case_id == "test_case_001"

    # Retrieve case
    retrieved = await repo.get_case_by_id("test_case_001")
    assert retrieved is not None
    assert retrieved.case_id == "test_case_001"
    assert retrieved.case_name == "テスト事件"
    assert retrieved.court_type == CourtType.SUPREME
    assert retrieved.case_type == CaseType.CIVIL


@pytest.mark.asyncio
async def test_search_cases(test_db_session: AsyncSession) -> None:
    """Test searching cases."""
    repo = CaseRepository(test_db_session)

    # Create multiple test cases
    for i in range(3):
        test_case = CaseDetail(
            case_id=f"test_case_{i:03d}",
            case_number=f"令和{i}年(オ)第{i}号",
            case_name=f"テスト事件{i}",
            court_type=CourtType.SUPREME,
            court_name="最高裁判所",
            case_type=CaseType.CIVIL,
            decision_date=date(2020 + i, 1, 1),
            summary=f"要旨{i}",
            main_text=f"判決全文{i}",
        )
        await repo.save_case(test_case)

    await test_db_session.commit()

    # Search all cases
    results, total = await repo.search_cases(limit=10)
    assert total == 3
    assert len(results) == 3

    # Search with query
    results, total = await repo.search_cases(query="テスト事件0", limit=10)
    assert total >= 1


@pytest.mark.asyncio
async def test_get_cases_by_law(test_db_session: AsyncSession) -> None:
    """Test getting cases by law ID."""
    repo = CaseRepository(test_db_session)

    # Create test case with law reference
    test_case = CaseDetail(
        case_id="test_case_law",
        case_number="令和3年(オ)第456号",
        case_name="法令引用事件",
        court_type=CourtType.HIGH,
        court_name="東京高等裁判所",
        case_type=CaseType.CIVIL,
        decision_date=date(2021, 3, 1),
        summary="法令引用テスト",
        main_text="判決全文",
        references=["law_123"],
    )
    await repo.save_case(test_case)
    await test_db_session.commit()

    # Get cases by law
    results, total = await repo.get_cases_by_law("law_123")
    assert total >= 1
    assert any(r.case_id == "test_case_law" for r in results)


@pytest.mark.asyncio
async def test_fulltext_search(test_db_session: AsyncSession) -> None:
    """Test PostgreSQL full-text search functionality."""
    repo = CaseRepository(test_db_session)

    # Create test cases with specific keywords
    test_cases = [
        CaseDetail(
            case_id="fulltext_001",
            case_number="令和5年(オ)第100号",
            case_name="損害賠償請求事件",
            court_type=CourtType.SUPREME,
            court_name="最高裁判所",
            case_type=CaseType.CIVIL,
            decision_date=date(2023, 1, 1),
            summary="交通事故による損害賠償",
            main_text="本件は交通事故により生じた損害の賠償を求める事案である。",
        ),
        CaseDetail(
            case_id="fulltext_002",
            case_number="令和5年(オ)第101号",
            case_name="契約解除請求事件",
            court_type=CourtType.HIGH,
            court_name="東京高等裁判所",
            case_type=CaseType.CIVIL,
            decision_date=date(2023, 2, 1),
            summary="売買契約の解除請求",
            main_text="本件は売買契約の解除及び代金返還を求める事案である。",
        ),
        CaseDetail(
            case_id="fulltext_003",
            case_number="令和5年(オ)第102号",
            case_name="所有権確認請求事件",
            court_type=CourtType.DISTRICT,
            court_name="大阪地方裁判所",
            case_type=CaseType.CIVIL,
            decision_date=date(2023, 3, 1),
            summary="不動産の所有権確認",
            main_text="本件は土地の所有権確認を求める事案である。",
        ),
    ]

    for case in test_cases:
        await repo.save_case(case)
    await test_db_session.commit()

    # Test full-text search with use_fulltext=True (PostgreSQL FTS)
    results, total = await repo.search_cases(query="損害賠償", use_fulltext=True)
    assert total >= 1
    assert any(r.case_id == "fulltext_001" for r in results)

    # Test search for "契約"
    results, total = await repo.search_cases(query="契約", use_fulltext=True)
    assert total >= 1
    assert any(r.case_id == "fulltext_002" for r in results)

    # Test search for "所有権"
    results, total = await repo.search_cases(query="所有権", use_fulltext=True)
    assert total >= 1
    assert any(r.case_id == "fulltext_003" for r in results)

    # Test fallback to ILIKE search
    results, total = await repo.search_cases(query="損害賠償", use_fulltext=False)
    assert total >= 1
    assert any(r.case_id == "fulltext_001" for r in results)
