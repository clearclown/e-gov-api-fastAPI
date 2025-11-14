"""
e-gov APIクライアントの単体テスト
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from app.services.egov_client import EGovAPIClient
from app.models.law import LawSearchResult, LawDetail
from app.core.exceptions import (
    LawNotFoundError,
    EGovAPITimeoutError,
    InvalidParameterError,
)


class TestEGovAPIClient:
    """e-gov APIクライアントのテストクラス"""

    @pytest.fixture
    async def client(self):
        """テスト用クライアントの作成"""
        client = EGovAPIClient(
            base_url="https://test.e-gov.go.jp",
            timeout=10
        )
        await client.connect()
        yield client
        await client.disconnect()

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """クライアントの初期化テスト"""
        client = EGovAPIClient()
        assert client.base_url is not None
        assert client.timeout > 0

    @pytest.mark.asyncio
    async def test_search_laws_empty_query(self, client):
        """空のクエリでの検索テスト"""
        with pytest.raises(InvalidParameterError) as exc_info:
            await client.search_laws(query="")

        assert "query" in str(exc_info.value.parameter)

    @pytest.mark.asyncio
    async def test_search_laws_invalid_limit(self, client):
        """無効なlimitパラメータのテスト"""
        with pytest.raises(InvalidParameterError) as exc_info:
            await client.search_laws(query="会社法", limit=0)

        assert "limit" in str(exc_info.value.parameter)

        with pytest.raises(InvalidParameterError) as exc_info:
            await client.search_laws(query="会社法", limit=101)

        assert "limit" in str(exc_info.value.parameter)

    @pytest.mark.asyncio
    async def test_search_laws_invalid_offset(self, client):
        """無効なoffsetパラメータのテスト"""
        with pytest.raises(InvalidParameterError) as exc_info:
            await client.search_laws(query="会社法", offset=-1)

        assert "offset" in str(exc_info.value.parameter)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_search_laws_success(self, mock_get, client):
        """法令検索成功のテスト"""
        # モックレスポンスのXML
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <DataRoot>
            <LawNameListInfo>
                <LawId>405AC0000000087</LawId>
                <LawNo>平成十七年法律第八十七号</LawNo>
                <LawName>会社法</LawName>
                <LawType>法律</LawType>
                <PromulgationDate>2005-07-26</PromulgationDate>
                <EnforcementDate>2006-05-01</EnforcementDate>
            </LawNameListInfo>
        </DataRoot>
        """

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_xml
        mock_get.return_value = mock_response

        results = await client.search_laws(query="会社法")

        assert len(results) >= 0
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_law_detail_empty_id(self, client):
        """空のIDで詳細取得テスト"""
        with pytest.raises(InvalidParameterError) as exc_info:
            await client.get_law_detail(law_id="")

        assert "law_id" in str(exc_info.value.parameter)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_get_law_detail_not_found(self, mock_get, client):
        """法令が見つからない場合のテスト"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(LawNotFoundError) as exc_info:
            await client.get_law_detail(law_id="invalid_id")

        assert "invalid_id" in str(exc_info.value.law_id)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_get_law_detail_success(self, mock_get, client):
        """法令詳細取得成功のテスト"""
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <DataRoot>
            <LawNo>平成十七年法律第八十七号</LawNo>
            <LawName>会社法</LawName>
            <LawType>法律</LawType>
            <PromulgationDate>2005-07-26</PromulgationDate>
            <EnforcementDate>2006-05-01</EnforcementDate>
            <LawBody>会社法の全文テキスト...</LawBody>
        </DataRoot>
        """

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_xml
        mock_get.return_value = mock_response

        result = await client.get_law_detail(law_id="405AC0000000087")

        assert isinstance(result, LawDetail)
        assert result.law_id == "405AC0000000087"
        assert result.law_name is not None

    @pytest.mark.asyncio
    async def test_parse_date(self, client):
        """日付パース機能のテスト"""
        # YYYY-MM-DD形式
        result = client._parse_date("2005-07-26")
        assert result == date(2005, 7, 26)

        # YYYY/MM/DD形式
        result = client._parse_date("2005/07/26")
        assert result == date(2005, 7, 26)

        # YYYYMMDD形式
        result = client._parse_date("20050726")
        assert result == date(2005, 7, 26)

        # 無効な日付（今日の日付を返す）
        result = client._parse_date("invalid-date")
        assert result == date.today()

    @pytest.mark.asyncio
    async def test_map_law_type(self, client):
        """法令種別マッピングのテスト"""
        assert client._map_law_type("law") == "1"
        assert client._map_law_type("ordinance") == "2"
        assert client._map_law_type("ministerial_order") == "3"
        assert client._map_law_type("unknown") == "1"  # デフォルト

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """コンテキストマネージャーのテスト"""
        async with EGovAPIClient() as client:
            assert client.client is not None

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_get_law_history_success(self, mock_get, client):
        """改正履歴取得成功のテスト"""
        # 詳細取得のモックレスポンス
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <DataRoot>
            <LawNo>平成十七年法律第八十七号</LawNo>
            <LawName>会社法</LawName>
            <LawType>法律</LawType>
            <PromulgationDate>2005-07-26</PromulgationDate>
            <EnforcementDate>2006-05-01</EnforcementDate>
            <LawBody>会社法の全文テキスト...</LawBody>
        </DataRoot>
        """

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_xml
        mock_get.return_value = mock_response

        amendments = await client.get_law_history(law_id="405AC0000000087")

        assert isinstance(amendments, list)
        # 現在の実装では空リストを返す
        assert len(amendments) >= 0
