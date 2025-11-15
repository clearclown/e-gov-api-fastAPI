"""API エンドポイントのテスト"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_check():
    """ヘルスチェックのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_related_cases():
    """関連判例取得APIのテスト"""
    response = client.get("/api/v1/analytics/laws/405AC0000000087/related-cases")
    assert response.status_code == 200
    data = response.json()
    assert "law_id" in data
    assert "total" in data
    assert "related_cases" in data


def test_get_most_cited_laws():
    """最多引用法令APIのテスト"""
    response = client.get("/api/v1/analytics/laws/most-cited")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "laws" in data


def test_visualize_relationships():
    """関連図可視化APIのテスト"""
    response = client.get("/api/v1/analytics/visualize/law/405AC0000000087")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data


def test_visualize_relationships_invalid_type():
    """無効なタイプでの関連図可視化APIのテスト"""
    response = client.get("/api/v1/analytics/visualize/invalid/test-id")
    assert response.status_code == 400


def test_graph_stats():
    """グラフ統計情報APIのテスト"""
    response = client.get("/api/v1/analytics/graph/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_nodes" in data
    assert "total_edges" in data


def test_start_conversation():
    """会話開始APIのテスト"""
    response = client.post(
        "/api/v1/conversation/start", json={"user_id": "test_user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data


def test_ask_question():
    """質問送信APIのテスト"""
    # まず会話を開始
    start_response = client.post(
        "/api/v1/conversation/start", json={"user_id": "test_user"}
    )
    conversation_id = start_response.json()["conversation_id"]

    # 質問を送信
    response = client.post(
        "/api/v1/conversation/ask",
        json={
            "conversation_id": conversation_id,
            "question": "契約解除について教えてください",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "references" in data


def test_ask_question_invalid_conversation():
    """無効な会話IDでの質問APIのテスト"""
    response = client.post(
        "/api/v1/conversation/ask",
        json={"conversation_id": "invalid_id", "question": "test"},
    )
    assert response.status_code == 404


def test_get_conversation_history():
    """会話履歴取得APIのテスト"""
    # 会話を開始
    start_response = client.post(
        "/api/v1/conversation/start", json={"user_id": "test_user"}
    )
    conversation_id = start_response.json()["conversation_id"]

    # 質問を送信
    client.post(
        "/api/v1/conversation/ask",
        json={"conversation_id": conversation_id, "question": "テスト質問"},
    )

    # 履歴を取得
    response = client.get(f"/api/v1/conversation/history/{conversation_id}")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert len(data["history"]) > 0


def test_summarize_case():
    """判例要約APIのテスト"""
    response = client.get("/api/v1/summarize/case/CASE-2024-001?style=brief")
    assert response.status_code == 200
    data = response.json()
    assert "case_id" in data
    assert "summary" in data


def test_summarize_case_not_found():
    """存在しない判例の要約APIのテスト"""
    response = client.get("/api/v1/summarize/case/NONEXISTENT")
    assert response.status_code == 404


def test_explain_article():
    """条文解説APIのテスト"""
    response = client.get("/api/v1/summarize/law/405AC0000000087/article/541")
    assert response.status_code == 200
    data = response.json()
    assert "law_id" in data
    assert "explanation" in data


def test_compare_laws():
    """法令比較APIのテスト"""
    response = client.get(
        "/api/v1/summarize/compare/laws?law_id_1=LAW-001&law_id_2=LAW-002"
    )
    assert response.status_code == 200
    data = response.json()
    assert "comparison" in data
