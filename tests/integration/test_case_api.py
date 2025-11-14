"""
判例API エンドポイントの統合テスト
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app
from app.models.case import CaseSearchResult, CaseDetail
from datetime import date


class TestCaseAPI:
    """判例APIエンドポイントの統合テスト"""

    @pytest.fixture
    async def async_client(self):
        """非同期テストクライアント"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_search_cases_success(self, async_client):
        """判例検索API成功のテスト"""
        response = await async_client.get("/api/v1/cases/search?keywords=特許権侵害")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    @pytest.mark.asyncio
    async def test_search_cases_missing_keywords(self, async_client):
        """検索キーワードなしでの検索テスト"""
        response = await async_client.get("/api/v1/cases/search")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_search_cases_invalid_limit(self, async_client):
        """無効なlimitパラメータのテスト"""
        response = await async_client.get("/api/v1/cases/search?keywords=特許権侵害&limit=101")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_search_cases_with_filters(self, async_client):
        """フィルター付き検索のテスト"""
        response = await async_client.get(
            "/api/v1/cases/search?keywords=特許権侵害&court_name=知的財産高等裁判所&case_type=行政&limit=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10

    @pytest.mark.asyncio
    async def test_get_case_detail_success(self, async_client):
        """判例詳細取得成功のテスト"""
        response = await async_client.get("/api/v1/cases/2020WLJPCA01010001")

        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == "2020WLJPCA01010001"
        assert "case_name" in data
        assert "full_text" in data

    @pytest.mark.asyncio
    async def test_get_courts_list(self, async_client):
        """裁判所一覧取得のテスト"""
        response = await async_client.get("/api/v1/cases/courts/list")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "court_id" in data[0]
        assert "court_name" in data[0]

    @pytest.mark.asyncio
    async def test_cases_root_endpoint(self, async_client):
        """判例APIルートエンドポイントのテスト"""
        response = await async_client.get("/api/v1/cases/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data

    @pytest.mark.asyncio
    async def test_root_endpoint_includes_cases(self, async_client):
        """ルートエンドポイントに判例エンドポイントが含まれるかテスト"""
        response = await async_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "cases_search" in data["endpoints"]
        assert "case_detail" in data["endpoints"]
        assert "courts_list" in data["endpoints"]
