"""Tests for MCP legal tools"""

import pytest
from app.mcp.legal_tools import (
    search_law,
    search_case,
    get_law_detail,
    get_case_detail,
    ask_legal_question,
)


class TestLegalTools:
    """Test cases for legal tools"""

    @pytest.mark.asyncio
    async def test_search_law_tool(self):
        """Test law search tool"""
        result = await search_law({"query": "会社法", "use_rag": False})
        assert "content" in result
        assert len(result["content"]) > 0
        assert result["content"][0]["type"] == "text"

    @pytest.mark.asyncio
    async def test_search_case_tool(self):
        """Test case search tool"""
        result = await search_case(
            {"query": "損害賠償", "use_rag": False}
        )
        assert "content" in result
        assert len(result["content"]) > 0

    @pytest.mark.asyncio
    async def test_get_law_detail_tool(self):
        """Test law detail retrieval tool"""
        result = await get_law_detail({"law_id": "321AC0000000086"})
        assert "content" in result
        assert len(result["content"]) > 0

    @pytest.mark.asyncio
    async def test_get_case_detail_tool(self):
        """Test case detail retrieval tool"""
        result = await get_case_detail({"case_id": "test_case_001"})
        assert "content" in result
        assert len(result["content"]) > 0

    @pytest.mark.asyncio
    async def test_ask_legal_question_tool_without_api_key(self):
        """Test legal question tool without API key"""
        # This should handle the case when API key is not configured
        result = await ask_legal_question(
            {"question": "株主総会の決議要件は？"}
        )
        assert "content" in result
        # Without API key, it should return an error message
        text = result["content"][0]["text"]
        assert "質問" in text
