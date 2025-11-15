"""会話型法律相談サービス"""

from typing import List, Dict, Any
from datetime import datetime
from app.services.rag_service import RAGService


class ConversationService:
    """会話型法律相談サービス"""

    def __init__(self) -> None:
        self.rag = RAGService()
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}

    async def start_conversation(self, user_id: str) -> str:
        """
        新しい会話セッションを開始

        Returns:
            conversation_id
        """
        conversation_id = f"{user_id}_{int(datetime.now().timestamp())}"
        self.conversations[conversation_id] = []
        return conversation_id

    async def ask_question(
        self, conversation_id: str, question: str
    ) -> Dict[str, Any]:
        """
        質問に回答（会話履歴を考慮）

        Args:
            conversation_id: 会話ID
            question: 質問文

        Returns:
            回答と参照情報
        """
        if conversation_id not in self.conversations:
            raise ValueError("Invalid conversation_id")

        # 会話履歴を取得
        history = self.conversations[conversation_id]

        # 会話コンテキストを構築
        context_query = self._build_context_query(question, history)

        # RAG検索
        search_results = await self.rag.search_with_context(
            query=context_query, search_type="both", top_k=5
        )

        # 会話履歴を含めたプロンプト作成
        conversation_context = self._format_conversation_history(history)

        full_prompt = f"""これまでの会話:
{conversation_context}

利用可能な情報:
{search_results['context']}

新しい質問: {question}

上記の会話履歴と情報を踏まえて、質問に回答してください。
"""

        # Claude APIで回答生成
        answer = await self.rag.generate_answer(query=question, context=full_prompt)

        # 会話履歴に追加
        history.append(
            {
                "role": "user",
                "content": question,
                "timestamp": datetime.now().isoformat(),
            }
        )
        history.append(
            {
                "role": "assistant",
                "content": answer,
                "references": {
                    "laws": [law.law_id for law in search_results["laws"]],
                    "cases": [case.case_id for case in search_results["cases"]],
                },
                "timestamp": datetime.now().isoformat(),
            }
        )

        return {
            "conversation_id": conversation_id,
            "question": question,
            "answer": answer,
            "references": {
                "laws": [
                    {
                        "law_id": law.law_id,
                        "law_name": law.law_name,
                    }
                    for law in search_results["laws"]
                ],
                "cases": [
                    {
                        "case_id": case.case_id,
                        "case_name": case.case_name,
                        "court_name": case.court_name,
                        "decision_date": case.decision_date.isoformat(),
                    }
                    for case in search_results["cases"]
                ],
            },
        }

    def _build_context_query(self, question: str, history: List[Dict[str, Any]]) -> str:
        """会話履歴を考慮したクエリを構築"""
        if not history:
            return question

        # 直近3ターンの質問を含める
        recent_questions = [
            turn["content"] for turn in history[-6:] if turn["role"] == "user"
        ]

        return " ".join(recent_questions + [question])

    def _format_conversation_history(
        self, history: List[Dict[str, Any]], max_turns: int = 3
    ) -> str:
        """会話履歴をフォーマット"""
        if not history:
            return "（会話履歴なし）"

        formatted = []
        for turn in history[-max_turns * 2 :]:
            role = "ユーザー" if turn["role"] == "user" else "アシスタント"
            formatted.append(f"{role}: {turn['content']}")
        return "\n\n".join(formatted)

    def get_conversation_history(
        self, conversation_id: str
    ) -> List[Dict[str, Any]]:
        """会話履歴を取得"""
        if conversation_id not in self.conversations:
            raise ValueError("Invalid conversation_id")
        return self.conversations[conversation_id]
