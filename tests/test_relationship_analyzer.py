"""RelationshipAnalyzer のテスト"""

import pytest
from app.services.relationship_analyzer import RelationshipAnalyzer


@pytest.mark.asyncio
async def test_build_citation_graph():
    """引用グラフ構築テスト"""
    analyzer = RelationshipAnalyzer()
    graph = await analyzer.build_citation_graph()

    # グラフが構築されていることを確認
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0

    # 法令ノードと判例ノードが存在することを確認
    law_nodes = [n for n in graph.nodes() if n.startswith("law_")]
    case_nodes = [n for n in graph.nodes() if n.startswith("case_")]

    assert len(law_nodes) > 0, "法令ノードが存在すること"
    assert len(case_nodes) > 0, "判例ノードが存在すること"


@pytest.mark.asyncio
async def test_find_related_cases():
    """関連判例検索テスト"""
    analyzer = RelationshipAnalyzer()

    # 民法のIDで検索
    results = await analyzer.find_related_cases("405AC0000000087")

    # 結果が返ってくることを確認
    assert isinstance(results, list)

    # 結果が存在する場合、必要なフィールドが含まれていることを確認
    if len(results) > 0:
        result = results[0]
        assert "case_id" in result
        assert "case_name" in result
        assert "relevance_score" in result
        assert "is_direct_citation" in result

        # スコアが0-1の範囲内であることを確認
        assert 0 <= result["relevance_score"] <= 1


@pytest.mark.asyncio
async def test_find_related_cases_nonexistent_law():
    """存在しない法令IDでの検索テスト"""
    analyzer = RelationshipAnalyzer()

    # 存在しない法令IDで検索
    results = await analyzer.find_related_cases("NONEXISTENT")

    # 空のリストが返ることを確認
    assert results == []


@pytest.mark.asyncio
async def test_get_most_cited_laws():
    """最多引用法令取得テスト"""
    analyzer = RelationshipAnalyzer()

    # 上位3件を取得
    results = await analyzer.get_most_cited_laws(limit=3)

    # 結果が返ってくることを確認
    assert isinstance(results, list)
    assert len(results) <= 3

    # 結果が存在する場合、必要なフィールドが含まれていることを確認
    if len(results) > 0:
        result = results[0]
        assert "law_id" in result
        assert "law_name" in result
        assert "citation_count" in result

        # 引用数が降順であることを確認
        if len(results) > 1:
            assert results[0]["citation_count"] >= results[1]["citation_count"]


@pytest.mark.asyncio
async def test_visualize_relationships_law():
    """法令中心の関連図データ生成テスト"""
    analyzer = RelationshipAnalyzer()

    # 民法を中心とした関連図を生成
    graph_data = await analyzer.visualize_relationships(
        center_id="405AC0000000087", center_type="law", depth=1
    )

    # 必要なフィールドが含まれていることを確認
    assert "nodes" in graph_data
    assert "edges" in graph_data
    assert "center" in graph_data

    # ノードとエッジがリストであることを確認
    assert isinstance(graph_data["nodes"], list)
    assert isinstance(graph_data["edges"], list)

    # 中心ノードが存在することを確認
    center_nodes = [n for n in graph_data["nodes"] if n.get("is_center")]
    assert len(center_nodes) == 1


@pytest.mark.asyncio
async def test_visualize_relationships_case():
    """判例中心の関連図データ生成テスト"""
    analyzer = RelationshipAnalyzer()

    # 判例を中心とした関連図を生成
    graph_data = await analyzer.visualize_relationships(
        center_id="CASE-2024-001", center_type="case", depth=2
    )

    # 必要なフィールドが含まれていることを確認
    assert "nodes" in graph_data
    assert "edges" in graph_data

    # ノードが存在することを確認
    assert len(graph_data["nodes"]) > 0


@pytest.mark.asyncio
async def test_visualize_relationships_nonexistent():
    """存在しないノードでの関連図生成テスト"""
    analyzer = RelationshipAnalyzer()

    # 存在しないIDで関連図を生成
    graph_data = await analyzer.visualize_relationships(
        center_id="NONEXISTENT", center_type="law", depth=1
    )

    # エラーが含まれていることを確認
    assert "error" in graph_data
