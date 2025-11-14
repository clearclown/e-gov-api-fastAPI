# 機能仕様書: AI統合（Phase 3）

**機能ID**: FEAT-003
**担当者**: ［担当者名］
**作成日**: 2025-11-14
**ステータス**: 未着手
**依存**: FEAT-001（法令API）、FEAT-002（判例API）

## 1. 機能概要

Agentic RAGとClaude Agent SDKを統合し、自然言語による法律情報検索とMCPツールとしての機能提供を実現する。

## 2. 対象要件

- FR-012: Agentic RAG実装
- FR-013: Claude Agent SDK統合
- FR-014: MCP Tool定義

## 3. 詳細仕様

### 3.1 Agentic RAG アーキテクチャ

#### 3.1.1 システム構成

```
┌─────────────────┐
│  Claude Agent   │
│      SDK        │
└────────┬────────┘
         │ MCP Protocol
         │
┌────────▼────────┐
│  MCP Server     │
│  (Legal Tools)  │
└────────┬────────┘
         │
    ┌────▼─────┐
    │   RAG    │
    │  Engine  │
    └────┬─────┘
         │
    ┌────▼─────────────┐
    │  Vector Store    │
    │  (Embeddings)    │
    └──────────────────┘
         │
    ┌────▼─────────────┐
    │   PostgreSQL     │
    │ (Law/Case Data)  │
    └──────────────────┘
```

#### 3.1.2 RAGエンジン設計

```python
# app/services/rag_service.py

from typing import List, Optional
import anthropic
from sentence_transformers import SentenceTransformer
import numpy as np
from app.models.law import LawDetail
from app.models.case import CaseDetail

class RAGService:
    """RAG（Retrieval-Augmented Generation）サービス"""

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        anthropic_api_key: str = None
    ):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)

    async def search_with_context(
        self,
        query: str,
        search_type: str = "both",  # "law", "case", "both"
        top_k: int = 5
    ) -> dict:
        """
        コンテキストを考慮した検索

        Args:
            query: 自然言語クエリ
            search_type: 検索対象（法令/判例/両方）
            top_k: 取得件数

        Returns:
            検索結果と関連コンテキスト
        """
        # クエリの埋め込みベクトル生成
        query_embedding = self.embedding_model.encode(query)

        results = {
            "query": query,
            "laws": [],
            "cases": [],
            "context": ""
        }

        # ベクトル検索で関連文書を取得
        if search_type in ["law", "both"]:
            results["laws"] = await self._search_laws(query_embedding, top_k)

        if search_type in ["case", "both"]:
            results["cases"] = await self._search_cases(query_embedding, top_k)

        # コンテキスト生成
        results["context"] = self._build_context(
            results["laws"],
            results["cases"]
        )

        return results

    async def _search_laws(
        self,
        embedding: np.ndarray,
        top_k: int
    ) -> List[LawDetail]:
        """法令のベクトル検索"""
        # pgvector を使用したベクトル検索
        # 実装詳細

    async def _search_cases(
        self,
        embedding: np.ndarray,
        top_k: int
    ) -> List[CaseDetail]:
        """判例のベクトル検索"""
        # pgvector を使用したベクトル検索
        # 実装詳細

    def _build_context(
        self,
        laws: List[LawDetail],
        cases: List[CaseDetail]
    ) -> str:
        """検索結果からコンテキストを構築"""
        context_parts = []

        if laws:
            context_parts.append("【関連法令】")
            for law in laws:
                context_parts.append(f"- {law.law_name}: {law.full_text[:200]}...")

        if cases:
            context_parts.append("\n【関連判例】")
            for case in cases:
                context_parts.append(
                    f"- {case.case_name} ({case.decision_date}): {case.summary}"
                )

        return "\n".join(context_parts)

    async def generate_answer(
        self,
        query: str,
        context: str
    ) -> str:
        """Claude APIを使用して回答生成"""
        system_prompt = """あなたは日本の法律に詳しい専門家です。
提供されたコンテキスト（法令・判例）を基に、質問に正確に回答してください。
不確かな情報は提供せず、根拠となる法令や判例を明示してください。"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"""コンテキスト:
{context}

質問: {query}

上記のコンテキストを参考に、質問に回答してください。"""
                }
            ]
        )

        return message.content[0].text
```

### 3.2 ベクトルストア設計

#### 3.2.1 PostgreSQL + pgvector

```sql
-- pgvector 拡張機能を有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- 法令埋め込みテーブル
CREATE TABLE law_embeddings (
    id SERIAL PRIMARY KEY,
    law_id VARCHAR(50) NOT NULL REFERENCES cases.laws(law_id),
    chunk_index INT NOT NULL,  -- 分割された文書の番号
    chunk_text TEXT NOT NULL,
    embedding vector(768),  -- 埋め込みベクトル（768次元）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(law_id, chunk_index)
);

-- 判例埋め込みテーブル
CREATE TABLE case_embeddings (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) NOT NULL REFERENCES cases(case_id),
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(case_id, chunk_index)
);

-- ベクトル検索用インデックス（IVFFlat）
CREATE INDEX ON law_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX ON case_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

#### 3.2.2 埋め込み生成バッチ

```python
# app/batch/generate_embeddings.py

import asyncio
from app.services.rag_service import RAGService
from app.repositories.embedding_repository import EmbeddingRepository

async def generate_law_embeddings():
    """法令データの埋め込みベクトルを生成"""
    rag = RAGService()
    repo = EmbeddingRepository()

    laws = await repo.get_all_laws()

    for law in laws:
        # 長文を分割（チャンキング）
        chunks = chunk_text(law.full_text, max_length=500)

        for idx, chunk in enumerate(chunks):
            embedding = rag.embedding_model.encode(chunk)
            await repo.save_law_embedding(
                law_id=law.law_id,
                chunk_index=idx,
                chunk_text=chunk,
                embedding=embedding
            )

    print(f"処理した法令数: {len(laws)}")

def chunk_text(text: str, max_length: int = 500) -> List[str]:
    """テキストを分割"""
    # 実装詳細
```

### 3.3 Claude Agent SDK統合

#### 3.3.1 MCPツール定義

```python
# app/mcp/legal_tools.py

from claude_agent_sdk import tool, create_sdk_mcp_server
from app.services.rag_service import RAGService
from app.services.egov_client import EGovAPIClient
from app.repositories.case_repository import CaseRepository

# RAGサービスのインスタンス
rag_service = RAGService()
egov_client = EGovAPIClient()

@tool(
    "search_law",
    "日本の法令を検索します。キーワードまたは自然言語での質問に対応。",
    {"query": str, "use_rag": bool}
)
async def search_law(args):
    """
    法令検索ツール

    Args:
        query: 検索クエリ（例: "会社法", "株主総会に関する法律"）
        use_rag: RAG検索を使用するか（デフォルト: True）
    """
    query = args["query"]
    use_rag = args.get("use_rag", True)

    if use_rag:
        # RAG検索
        results = await rag_service.search_with_context(
            query=query,
            search_type="law",
            top_k=3
        )

        response_text = f"検索クエリ: {query}\n\n"
        for law in results["laws"]:
            response_text += f"""
法令名: {law.law_name}
法令番号: {law.law_number}
概要: {law.full_text[:300]}...
---
"""
    else:
        # 従来の検索
        results = await egov_client.search_laws(query)
        response_text = f"検索結果: {len(results)}件\n"
        for law in results[:5]:
            response_text += f"- {law.law_name} ({law.law_number})\n"

    return {
        "content": [{"type": "text", "text": response_text}]
    }


@tool(
    "search_case",
    "判例を検索します。事件名、キーワード、または法的問題で検索可能。",
    {"query": str, "court_type": str, "use_rag": bool}
)
async def search_case(args):
    """
    判例検索ツール

    Args:
        query: 検索クエリ
        court_type: 裁判所種別（オプション）
        use_rag: RAG検索を使用するか
    """
    query = args["query"]
    court_type = args.get("court_type")
    use_rag = args.get("use_rag", True)

    if use_rag:
        results = await rag_service.search_with_context(
            query=query,
            search_type="case",
            top_k=5
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
        repo = CaseRepository()
        results, total = await repo.search_cases(
            query=query,
            court_type=court_type,
            limit=5
        )
        response_text = f"判例検索結果: {total}件\n"
        for case in results:
            response_text += f"- {case.case_name} ({case.decision_date})\n"

    return {
        "content": [{"type": "text", "text": response_text}]
    }


@tool(
    "get_law_detail",
    "指定された法令IDの詳細情報を取得します。",
    {"law_id": str}
)
async def get_law_detail(args):
    """法令詳細取得ツール"""
    law_id = args["law_id"]
    law = await egov_client.get_law_detail(law_id)

    response_text = f"""
法令名: {law.law_name}
法令番号: {law.law_number}
公布日: {law.promulgation_date}
施行日: {law.enforcement_date}

全文:
{law.full_text}
"""

    return {
        "content": [{"type": "text", "text": response_text}]
    }


@tool(
    "get_case_detail",
    "指定された判例IDの詳細情報を取得します。",
    {"case_id": str}
)
async def get_case_detail(args):
    """判例詳細取得ツール"""
    case_id = args["case_id"]
    repo = CaseRepository()
    case = await repo.get_case_by_id(case_id)

    if not case:
        return {
            "content": [{"type": "text", "text": f"判例ID {case_id} が見つかりません"}],
            "is_error": True
        }

    response_text = f"""
事件名: {case.case_name}
事件番号: {case.case_number}
裁判所: {case.court_name}
判決日: {case.decision_date}

判示事項:
{case.holdings}

裁判要旨:
{case.case_summary}

判決全文:
{case.main_text}
"""

    return {
        "content": [{"type": "text", "text": response_text}]
    }


@tool(
    "ask_legal_question",
    "法律に関する質問に、関連する法令・判例を参照して回答します。",
    {"question": str}
)
async def ask_legal_question(args):
    """自然言語法律相談ツール"""
    question = args["question"]

    # RAG検索でコンテキスト取得
    search_results = await rag_service.search_with_context(
        query=question,
        search_type="both",
        top_k=3
    )

    # Claude APIで回答生成
    answer = await rag_service.generate_answer(
        query=question,
        context=search_results["context"]
    )

    response_text = f"""
質問: {question}

回答:
{answer}

参照した法令:
{', '.join([law.law_name for law in search_results['laws']])}

参照した判例:
{', '.join([case.case_name for case in search_results['cases']])}
"""

    return {
        "content": [{"type": "text", "text": response_text}]
    }


# MCPサーバーを作成
legal_tools_server = create_sdk_mcp_server(
    name="legal_tools",
    version="1.0.0",
    tools=[
        search_law,
        search_case,
        get_law_detail,
        get_case_detail,
        ask_legal_question
    ]
)
```

#### 3.3.2 MCPサーバー起動

```python
# app/main.py

from fastapi import FastAPI
from app.mcp.legal_tools import legal_tools_server
from app.api.endpoints import laws, cases

app = FastAPI(
    title="e-gov Legal API",
    description="日本の法令・判例情報API",
    version="1.0.0"
)

# REST APIルーター
app.include_router(laws.router)
app.include_router(cases.router)

# MCP統合の例（実際の統合方法はプロジェクトによる）
@app.on_event("startup")
async def startup_event():
    """起動時の初期化"""
    # RAGサービスの初期化など
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 3.3.3 Claude Agent SDKからの使用例

```python
# examples/use_legal_tools.py

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from app.mcp.legal_tools import legal_tools_server

async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"legal": legal_tools_server},
        allowed_tools=[
            "mcp__legal__search_law",
            "mcp__legal__search_case",
            "mcp__legal__ask_legal_question"
        ],
        system_prompt="あなたは日本の法律に詳しいアシスタントです。"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "会社の株主総会に関する法律について教えてください。"
        )

        async for message in client.receive_response():
            print(message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 3.4 MCP設定ファイル

```json
# .mcp.json

{
  "mcpServers": {
    "legal_tools": {
      "type": "sdk",
      "command": "python",
      "args": ["-m", "app.mcp.legal_tools"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}",
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

## 4. テスト仕様

### 4.1 単体テスト

```python
# tests/test_rag_service.py

import pytest
from app.services.rag_service import RAGService

@pytest.mark.asyncio
async def test_search_with_context():
    """RAG検索テスト"""
    rag = RAGService()
    results = await rag.search_with_context(
        query="株主総会の決議要件",
        search_type="law",
        top_k=3
    )
    assert len(results["laws"]) > 0
    assert results["context"] != ""

@pytest.mark.asyncio
async def test_generate_answer():
    """回答生成テスト"""
    rag = RAGService()
    answer = await rag.generate_answer(
        query="株主総会の決議要件は？",
        context="会社法第309条..."
    )
    assert len(answer) > 0
```

### 4.2 MCPツールテスト

```python
# tests/test_legal_tools.py

import pytest
from app.mcp.legal_tools import search_law, ask_legal_question

@pytest.mark.asyncio
async def test_search_law_tool():
    """法令検索ツールテスト"""
    result = await search_law({"query": "会社法", "use_rag": False})
    assert "content" in result
    assert len(result["content"]) > 0

@pytest.mark.asyncio
async def test_ask_legal_question_tool():
    """法律相談ツールテスト"""
    result = await ask_legal_question({
        "question": "株主総会の決議要件は？"
    })
    assert "content" in result
```

## 5. パフォーマンス要件

- ベクトル検索: 平均200ms以内
- RAG検索（全体）: 平均1秒以内
- 回答生成: 平均3秒以内（Claude API依存）

## 6. セキュリティ考慮事項

- Anthropic API Keyの安全な管理（環境変数）
- RAGコンテキストのサイズ制限（トークン数管理）
- MCPツールの認証・認可

## 7. 実装手順

1. **ステップ1**: pgvector セットアップ
2. **ステップ2**: 埋め込みモデル選定・テスト
3. **ステップ3**: RAGサービス実装
4. **ステップ4**: 埋め込み生成バッチ実装
5. **ステップ5**: MCPツール実装
6. **ステップ6**: Claude Agent SDK統合
7. **ステップ7**: テスト作成
8. **ステップ8**: ドキュメント作成

## 8. 依存関係

- sentence-transformers (埋め込み生成)
- pgvector (ベクトル検索)
- anthropic (Claude API)
- claude-agent-sdk (MCP統合)

## 9. 完了条件

- [ ] ベクトルストアが構築され動作する
- [ ] RAG検索が正常に動作する
- [ ] 全MCPツールが実装され動作する
- [ ] Claude Agent SDKから利用可能
- [ ] 単体テストカバレッジ80%以上
- [ ] 統合テストが全てパス
- [ ] パフォーマンス要件を満たす
- [ ] 使用例ドキュメントが完備

## 10. 備考

- 埋め込みモデルは日本語対応のものを選定すること
- Claude APIのコストに注意（キャッシング活用）
- ベクトル検索のチューニング（lists パラメータ調整）
- RAGの精度評価を定期的に実施すること
