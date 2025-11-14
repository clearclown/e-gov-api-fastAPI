"""MCP Tools for legal information search

This module provides MCP tools for searching Japanese laws and court precedents
using the Claude Agent SDK.

Note: This is a placeholder implementation. The actual claude-agent-sdk integration
will be done once the SDK is available and properly configured.
"""

from typing import Any, Dict
from app.services.rag_service import RAGService

# Initialize RAG service
rag_service = RAGService()


# Tool definitions (placeholder - will be integrated with Claude Agent SDK)

async def search_law(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    法令検索ツール

    Args:
        query: 検索クエリ（例: "会社法", "株主総会に関する法律"）
        use_rag: RAG検索を使用するか（デフォルト: True）

    Returns:
        検索結果を含む辞書
    """
    query = args["query"]
    use_rag = args.get("use_rag", True)

    if use_rag:
        # RAG検索
        results = await rag_service.search_with_context(
            query=query, search_type="law", top_k=3
        )

        response_text = f"検索クエリ: {query}\n\n"
        for law in results["laws"]:
            excerpt = law.full_text[:300] + "..." if len(law.full_text) > 300 else law.full_text
            response_text += f"""
法令名: {law.law_name}
法令番号: {law.law_number}
概要: {excerpt}
---
"""
    else:
        # 従来の検索（Phase 1で実装予定のegov_clientを使用）
        response_text = f"検索クエリ: {query}\n\n"
        response_text += "※ 従来の検索機能はPhase 1で実装予定です。\n"

    return {"content": [{"type": "text", "text": response_text}]}


async def search_case(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    判例検索ツール

    Args:
        query: 検索クエリ
        court_type: 裁判所種別（オプション）
        use_rag: RAG検索を使用するか

    Returns:
        検索結果を含む辞書
    """
    query = args["query"]
    court_type = args.get("court_type")
    use_rag = args.get("use_rag", True)

    if use_rag:
        results = await rag_service.search_with_context(
            query=query, search_type="case", top_k=5
        )

        response_text = f"判例検索: {query}\n\n"
        for case in results["cases"]:
            response_text += f"""
事件名: {case.case_name}
裁判所: {case.court_name}
判決日: {case.decision_date}
要旨: {case.summary}
---
"""
    else:
        # 従来の検索（Phase 2で実装予定のcase_repositoryを使用）
        response_text = f"判例検索: {query}\n\n"
        response_text += "※ 従来の検索機能はPhase 2で実装予定です。\n"

    return {"content": [{"type": "text", "text": response_text}]}


async def get_law_detail(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    法令詳細取得ツール

    Args:
        law_id: 法令ID

    Returns:
        法令詳細を含む辞書
    """
    law_id = args["law_id"]

    # Phase 1で実装予定のegov_clientを使用
    response_text = f"""
法令ID: {law_id}

※ 法令詳細取得機能はPhase 1で実装予定です。
"""

    return {"content": [{"type": "text", "text": response_text}]}


async def get_case_detail(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    判例詳細取得ツール

    Args:
        case_id: 判例ID

    Returns:
        判例詳細を含む辞書
    """
    case_id = args["case_id"]

    # Phase 2で実装予定のcase_repositoryを使用
    response_text = f"""
判例ID: {case_id}

※ 判例詳細取得機能はPhase 2で実装予定です。
"""

    return {"content": [{"type": "text", "text": response_text}]}


async def ask_legal_question(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    自然言語法律相談ツール

    Args:
        question: 法律に関する質問

    Returns:
        回答を含む辞書
    """
    question = args["question"]

    try:
        # RAG検索でコンテキスト取得
        search_results = await rag_service.search_with_context(
            query=question, search_type="both", top_k=3
        )

        # Claude APIで回答生成
        answer = await rag_service.generate_answer(
            query=question, context=search_results["context"]
        )

        law_names = [law.law_name for law in search_results["laws"]]
        case_names = [case.case_name for case in search_results["cases"]]

        response_text = f"""
質問: {question}

回答:
{answer}

参照した法令:
{', '.join(law_names) if law_names else 'なし'}

参照した判例:
{', '.join(case_names) if case_names else 'なし'}
"""

    except ValueError as e:
        # Anthropic API keyが設定されていない場合
        response_text = f"""
質問: {question}

エラー: {str(e)}

※ この機能を使用するには、ANTHROPIC_API_KEY環境変数を設定してください。
"""

    return {"content": [{"type": "text", "text": response_text}]}


# Tool metadata for MCP registration
LEGAL_TOOLS = {
    "search_law": {
        "name": "search_law",
        "description": "日本の法令を検索します。キーワードまたは自然言語での質問に対応。",
        "parameters": {"query": str, "use_rag": bool},
        "function": search_law,
    },
    "search_case": {
        "name": "search_case",
        "description": "判例を検索します。事件名、キーワード、または法的問題で検索可能。",
        "parameters": {"query": str, "court_type": str, "use_rag": bool},
        "function": search_case,
    },
    "get_law_detail": {
        "name": "get_law_detail",
        "description": "指定された法令IDの詳細情報を取得します。",
        "parameters": {"law_id": str},
        "function": get_law_detail,
    },
    "get_case_detail": {
        "name": "get_case_detail",
        "description": "指定された判例IDの詳細情報を取得します。",
        "parameters": {"case_id": str},
        "function": get_case_detail,
    },
    "ask_legal_question": {
        "name": "ask_legal_question",
        "description": "法律に関する質問に、関連する法令・判例を参照して回答します。",
        "parameters": {"question": str},
        "function": ask_legal_question,
    },
}


# Note: Actual MCP server creation with Claude Agent SDK will be implemented
# once the SDK is properly installed and configured. Example:
#
# from claude_agent_sdk import tool, create_sdk_mcp_server
#
# legal_tools_server = create_sdk_mcp_server(
#     name="legal_tools",
#     version="1.0.0",
#     tools=[search_law, search_case, get_law_detail, get_case_detail, ask_legal_question]
# )
