"""Unit tests for case scraper service."""

import pytest

from app.services.case_scraper import CaseScraperService


@pytest.mark.asyncio
async def test_case_scraper_initialization() -> None:
    """Test case scraper initialization."""
    scraper = CaseScraperService()
    assert scraper.base_url is not None
    await scraper.close()


@pytest.mark.asyncio
async def test_search_cases_empty_query() -> None:
    """Test case search with empty query."""
    scraper = CaseScraperService()
    try:
        results = await scraper.search_cases()
        # Since this is a placeholder implementation, it should return empty list
        assert isinstance(results, list)
    finally:
        await scraper.close()


@pytest.mark.asyncio
async def test_fetch_case_detail() -> None:
    """Test fetching case detail."""
    scraper = CaseScraperService()
    try:
        # This is a placeholder implementation, so it should return sample data
        case = await scraper.fetch_case_detail("test_case_id")
        assert case.case_id == "test_case_id"
        assert case.case_name is not None
        assert case.main_text is not None
    finally:
        await scraper.close()


@pytest.mark.asyncio
async def test_case_scraper_context_manager() -> None:
    """Test case scraper as context manager."""
    async with CaseScraperService() as scraper:
        assert scraper.base_url is not None
