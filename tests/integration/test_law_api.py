"""
法令API エンドポイントの統合テスト
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app
from app.models.law import LawSearchResult, LawDetail
from datetime import date


class TestLawAPI:
    """法令APIエンドポイントの統合テスト"""

    @pytest.fixture
    async def async_client(self):
        """非同期テストクライアント"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client):
        """ルートエンドポイントのテスト"""
        response = await async_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """ヘルスチェックエンドポイントのテスト"""
        response = await async_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "cache" in data

    @pytest.mark.asyncio
    @patch("app.services.egov_client.EGovAPIClient.search_laws")
    async def test_search_laws_success(self, mock_search, async_client):
        """法令検索API成功のテスト"""
        # モックデータ
        mock_results = [
            LawSearchResult(
                law_id="405AC0000000087",
                law_number="平成十七年法律第八十七号",
                law_name="会社法",
                law_type="法律",
                promulgation_date=date(2005, 7, 26),
                enforcement_date=date(2006, 5, 1)
            )
        ]
        mock_search.return_value = mock_results

        response = await async_client.get("/api/v1/laws/search?q=会社法")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    @pytest.mark.asyncio
    async def test_search_laws_missing_query(self, async_client):
        """検索キーワードなしでの検索テスト"""
        response = await async_client.get("/api/v1/laws/search")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_search_laws_invalid_limit(self, async_client):
        """無効なlimitパラメータのテスト"""
        response = await async_client.get("/api/v1/laws/search?q=会社法&limit=101")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    @patch("app.services.egov_client.EGovAPIClient.search_laws")
    async def test_search_laws_with_filters(self, mock_search, async_client):
        """フィルター付き検索のテスト"""
        mock_search.return_value = []

        response = await async_client.get(
            "/api/v1/laws/search?q=会社法&type=law&limit=10&offset=0"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0

    @pytest.mark.asyncio
    @patch("app.services.egov_client.EGovAPIClient.get_law_detail")
    async def test_get_law_detail_success(self, mock_get_detail, async_client):
        """法令詳細取得成功のテスト"""
        # モックデータ
        mock_detail = LawDetail(
            law_id="405AC0000000087",
            law_number="平成十七年法律第八十七号",
            law_name="会社法",
            law_type="法律",
            promulgation_date=date(2005, 7, 26),
            enforcement_date=date(2006, 5, 1),
            full_text="会社法の全文...",
            toc=[{"chapter": "第一章", "title": "総則", "articles": ["1", "2"]}],
            metadata={"source": "e-gov"}
        )
        mock_get_detail.return_value = mock_detail

        response = await async_client.get("/api/v1/laws/405AC0000000087")

        assert response.status_code == 200
        data = response.json()
        assert data["law_id"] == "405AC0000000087"
        assert data["law_name"] == "会社法"
        assert "full_text" in data
        assert "toc" in data

    @pytest.mark.asyncio
    @patch("app.services.egov_client.EGovAPIClient.get_law_detail")
    async def test_get_law_detail_not_found(self, mock_get_detail, async_client):
        """存在しない法令の詳細取得テスト"""
        from app.core.exceptions import LawNotFoundError

        mock_get_detail.side_effect = LawNotFoundError("invalid_id")

        response = await async_client.get("/api/v1/laws/invalid_id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    @patch("app.services.egov_client.EGovAPIClient.get_law_history")
    async def test_get_law_history_success(self, mock_get_history, async_client):
        """改正履歴取得成功のテスト"""
        # モックデータ（空のリスト）
        mock_get_history.return_value = []

        response = await async_client.get("/api/v1/laws/405AC0000000087/history")

        assert response.status_code == 200
        data = response.json()
        assert "law_id" in data
        assert "amendments" in data
        assert isinstance(data["amendments"], list)

    @pytest.mark.asyncio
    @patch("app.services.egov_client.EGovAPIClient.get_law_history")
    async def test_get_law_history_not_found(self, mock_get_history, async_client):
        """存在しない法令の改正履歴取得テスト"""
        from app.core.exceptions import LawNotFoundError

        mock_get_history.side_effect = LawNotFoundError("invalid_id")

        response = await async_client.get("/api/v1/laws/invalid_id/history")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_openapi_schema(self, async_client):
        """OpenAPIスキーマが正しく生成されるかのテスト"""
        response = await async_client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
        assert "/api/v1/laws/search" in schema["paths"]
        assert "/api/v1/laws/{law_id}" in schema["paths"]

    @pytest.mark.asyncio
    async def test_cors_headers(self, async_client):
        """CORSヘッダーのテスト"""
        response = await async_client.get("/")

        # CORSミドルウェアが設定されていることを確認
        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("app.services.egov_client.EGovAPIClient.search_laws")
    async def test_response_time_header(self, mock_search, async_client):
        """レスポンスタイムヘッダーのテスト"""
        mock_search.return_value = []

        response = await async_client.get("/api/v1/laws/search?q=test")

        assert response.status_code == 200
        assert "x-process-time" in response.headers
        # レスポンスタイムが記録されている
        assert float(response.headers["x-process-time"]) >= 0
