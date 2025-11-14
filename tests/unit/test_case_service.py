"""
判例サービスの単体テスト
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from app.services.case_service import CaseService
from app.models.case import CaseSearchResult, CaseDetail
from app.core.exceptions import InvalidParameterError


class TestCaseService:
    """判例サービスのテストクラス"""

    @pytest.fixture
    async def service(self):
        """テスト用サービスの作成"""
        service = CaseService(
            base_url="https://test.courts.go.jp",
            timeout=10
        )
        await service.connect()
        yield service
        await service.disconnect()

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """サービスの初期化テスト"""
        service = CaseService()
        assert service.base_url is not None
        assert service.timeout > 0

    @pytest.mark.asyncio
    async def test_search_cases_empty_keywords(self, service):
        """空のキーワードでの検索テスト"""
        with pytest.raises(InvalidParameterError) as exc_info:
            await service.search_cases(keywords="")

        assert "keywords" in str(exc_info.value.parameter)

    @pytest.mark.asyncio
    async def test_search_cases_invalid_limit(self, service):
        """無効なlimitパラメータのテスト"""
        with pytest.raises(InvalidParameterError) as exc_info:
            await service.search_cases(keywords="特許権侵害", limit=0)

        assert "limit" in str(exc_info.value.parameter)

        with pytest.raises(InvalidParameterError) as exc_info:
            await service.search_cases(keywords="特許権侵害", limit=101)

        assert "limit" in str(exc_info.value.parameter)

    @pytest.mark.asyncio
    async def test_search_cases_invalid_offset(self, service):
        """無効なoffsetパラメータのテスト"""
        with pytest.raises(InvalidParameterError) as exc_info:
            await service.search_cases(keywords="特許権侵害", offset=-1)

        assert "offset" in str(exc_info.value.parameter)

    @pytest.mark.asyncio
    async def test_search_cases_success(self, service):
        """判例検索成功のテスト（モック実装）"""
        results = await service.search_cases(keywords="特許権侵害")

        assert isinstance(results, list)
        assert len(results) >= 0

        if results:
            assert isinstance(results[0], CaseSearchResult)
            assert results[0].case_id is not None
            assert results[0].case_name is not None

    @pytest.mark.asyncio
    async def test_search_cases_with_filters(self, service):
        """フィルター付き検索のテスト"""
        results = await service.search_cases(
            keywords="特許権侵害",
            court_name="知的財産高等裁判所",
            case_type="行政"
        )

        assert isinstance(results, list)
        if results:
            assert isinstance(results[0], CaseSearchResult)

    @pytest.mark.asyncio
    async def test_get_case_detail_empty_id(self, service):
        """空のIDで詳細取得テスト"""
        with pytest.raises(InvalidParameterError) as exc_info:
            await service.get_case_detail(case_id="")

        assert "case_id" in str(exc_info.value.parameter)

    @pytest.mark.asyncio
    async def test_get_case_detail_success(self, service):
        """判例詳細取得成功のテスト（モック実装）"""
        case_detail = await service.get_case_detail(case_id="2020WLJPCA01010001")

        assert isinstance(case_detail, CaseDetail)
        assert case_detail.case_id == "2020WLJPCA01010001"
        assert case_detail.case_name is not None
        assert case_detail.full_text is not None

    @pytest.mark.asyncio
    async def test_get_courts(self, service):
        """裁判所一覧取得のテスト"""
        courts = await service.get_courts()

        assert isinstance(courts, list)
        assert len(courts) > 0
        assert courts[0].court_id is not None
        assert courts[0].court_name is not None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """コンテキストマネージャーのテスト"""
        async with CaseService() as service:
            assert service.client is not None
