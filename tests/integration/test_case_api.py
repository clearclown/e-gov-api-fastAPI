"""Integration tests for case API endpoints."""

from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import CaseDetail, CaseType, CourtType
from app.repositories.case_repository import CaseRepository


@pytest.mark.asyncio
async def test_health_check(test_client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_root_endpoint(test_client: AsyncClient) -> None:
    """Test root endpoint."""
    response = await test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_search_cases_empty(test_client: AsyncClient) -> None:
    """Test case search API with no data."""
    response = await test_client.get("/api/v1/cases/search")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


@pytest.mark.asyncio
async def test_search_cases_with_data(
    test_client: AsyncClient, test_db_session: AsyncSession
) -> None:
    """Test case search API with data."""
    # Insert test case
    repo = CaseRepository(test_db_session)
    test_case = CaseDetail(
        case_id="api_test_001",
        case_number="令和2年(オ)第789号",
        case_name="API テスト事件",
        court_type=CourtType.SUPREME,
        court_name="最高裁判所",
        case_type=CaseType.CIVIL,
        decision_date=date(2020, 12, 1),
        summary="APIテスト要旨",
        main_text="API判決全文",
    )
    await repo.save_case(test_case)
    await test_db_session.commit()

    # Test search
    response = await test_client.get("/api/v1/cases/search")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["case_id"] == "api_test_001"


@pytest.mark.asyncio
async def test_get_case_detail(test_client: AsyncClient, test_db_session: AsyncSession) -> None:
    """Test get case detail API."""
    # Insert test case
    repo = CaseRepository(test_db_session)
    test_case = CaseDetail(
        case_id="api_test_002",
        case_number="令和3年(オ)第100号",
        case_name="詳細テスト事件",
        court_type=CourtType.HIGH,
        court_name="大阪高等裁判所",
        case_type=CaseType.CRIMINAL,
        decision_date=date(2021, 5, 20),
        summary="詳細テスト要旨",
        main_text="詳細判決全文",
        holdings="判示事項",
        case_summary="裁判要旨",
    )
    await repo.save_case(test_case)
    await test_db_session.commit()

    # Test get detail
    response = await test_client.get("/api/v1/cases/api_test_002")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "api_test_002"
    assert data["case_name"] == "詳細テスト事件"
    assert data["main_text"] == "詳細判決全文"


@pytest.mark.asyncio
async def test_get_case_not_found(test_client: AsyncClient) -> None:
    """Test get case detail API with non-existent case."""
    response = await test_client.get("/api/v1/cases/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_cases_by_law(test_client: AsyncClient, test_db_session: AsyncSession) -> None:
    """Test get cases by law API."""
    # Insert test case with law reference
    repo = CaseRepository(test_db_session)
    test_case = CaseDetail(
        case_id="api_test_003",
        case_number="令和4年(オ)第200号",
        case_name="法令参照事件",
        court_type=CourtType.DISTRICT,
        court_name="東京地方裁判所",
        case_type=CaseType.ADMINISTRATIVE,
        decision_date=date(2022, 8, 15),
        summary="法令参照テスト",
        main_text="判決全文",
        references=["test_law_001"],
    )
    await repo.save_case(test_case)
    await test_db_session.commit()

    # Test get cases by law
    response = await test_client.get("/api/v1/laws/test_law_001/cases")
    assert response.status_code == 200
    data = response.json()
    assert data["law_id"] == "test_law_001"
    assert data["total"] >= 1
    assert any(case["case_id"] == "api_test_003" for case in data["cases"])
