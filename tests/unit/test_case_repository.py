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
