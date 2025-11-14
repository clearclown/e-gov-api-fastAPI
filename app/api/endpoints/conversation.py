"""Conversation API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/api/v1/conversation", tags=["conversation"])
conversation_service = ConversationService()


class StartConversationRequest(BaseModel):
    """会話開始リクエスト"""

    user_id: str

    class Config:
        json_schema_extra = {"example": {"user_id": "user_12345"}}


class AskQuestionRequest(BaseModel):
    """質問リクエスト"""

    conversation_id: str
    question: str

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "user_12345_1699999999",
                "question": "契約を解除するにはどうすればよいですか？",
            }
        }


@router.post("/start")
async def start_conversation(request: StartConversationRequest) -> dict:
    """
    会話セッション開始

    新しい法律相談セッションを開始します。
    返却されたconversation_idを使用して質問を送信してください。

    Args:
        request: ユーザーID

    Returns:
        会話ID
    """
    conversation_id = await conversation_service.start_conversation(request.user_id)

    return {
        "conversation_id": conversation_id,
        "message": "会話セッションを開始しました",
    }


@router.post("/ask")
async def ask_question(request: AskQuestionRequest) -> dict:
    """
    質問を送信（会話履歴を考慮）

    会話履歴を考慮して質問に回答します。
    関連する法令・判例を自動的に検索し、回答に含めます。

    Args:
        request: 会話IDと質問

    Returns:
        回答と参照情報

    Raises:
        HTTPException: 会話IDが無効な場合
    """
    try:
        result = await conversation_service.ask_question(
            request.conversation_id, request.question
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/history/{conversation_id}")
async def get_conversation_history(conversation_id: str) -> dict:
    """
    会話履歴を取得

    Args:
        conversation_id: 会話ID

    Returns:
        会話履歴

    Raises:
        HTTPException: 会話IDが無効な場合
    """
    try:
        history = conversation_service.get_conversation_history(conversation_id)
        return {
            "conversation_id": conversation_id,
            "total_turns": len(history),
            "history": history,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
