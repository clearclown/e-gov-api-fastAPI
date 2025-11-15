"""ConversationService のテスト"""

import pytest
from app.services.conversation_service import ConversationService


@pytest.mark.asyncio
async def test_start_conversation():
    """会話セッション開始テスト"""
    service = ConversationService()

    conversation_id = await service.start_conversation("test_user")

    # 会話IDが生成されていることを確認
    assert conversation_id is not None
    assert isinstance(conversation_id, str)
    assert "test_user" in conversation_id


@pytest.mark.asyncio
async def test_ask_question():
    """質問送信テスト"""
    service = ConversationService()

    # 会話セッションを開始
    conversation_id = await service.start_conversation("test_user")

    # 質問を送信
    result = await service.ask_question(
        conversation_id, "契約を解除するにはどうすればよいですか？"
    )

    # 必要なフィールドが含まれていることを確認
    assert "conversation_id" in result
    assert "question" in result
    assert "answer" in result
    assert "references" in result

    # 回答が含まれていることを確認
    assert len(result["answer"]) > 0


@pytest.mark.asyncio
async def test_ask_question_invalid_conversation():
    """無効な会話IDでの質問テスト"""
    service = ConversationService()

    # 存在しない会話IDで質問
    with pytest.raises(ValueError, match="Invalid conversation_id"):
        await service.ask_question("invalid_id", "テスト質問")


@pytest.mark.asyncio
async def test_conversation_history():
    """会話履歴のテスト"""
    service = ConversationService()

    # 会話セッションを開始
    conversation_id = await service.start_conversation("test_user")

    # 複数回質問
    await service.ask_question(conversation_id, "質問1")
    await service.ask_question(conversation_id, "質問2")

    # 会話履歴を取得
    history = service.get_conversation_history(conversation_id)

    # 履歴が正しく保存されていることを確認
    assert len(history) == 4  # 2質問 × 2ターン（user + assistant）

    # 最初の質問が含まれていることを確認
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "質問1"


@pytest.mark.asyncio
async def test_get_conversation_history_invalid():
    """無効な会話IDでの履歴取得テスト"""
    service = ConversationService()

    # 存在しない会話IDで履歴を取得
    with pytest.raises(ValueError, match="Invalid conversation_id"):
        service.get_conversation_history("invalid_id")
