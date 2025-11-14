# e-gov API FastAPI

日本国内の法律および判例に関する正確で最新の情報を取得するためのAPIプロジェクト

## プロジェクト概要

このプロジェクトは、日本の法律・判例情報へのアクセスを提供するFastAPIベースのAPIサーバーです。uvパッケージマネージャーを使用し、将来的にはAgentic RAGやClaude Agent SDKとの統合を見据えた設計となっています。

## 主な機能目標

### 1. 法律情報の取得
- **e-gov法令API**との統合
  - 日本国内の現行法令の検索・取得
  - 法令の改正履歴の追跡
  - 法令データの構造化された提供

### 2. 判例情報の取得
- 信頼性の高い判例データソースの統合
  - 裁判所ウェブサイトからのデータ取得
  - 判例データベースAPIの活用
  - Webスクレイピングによる補完的なデータ収集

### 3. 将来的な拡張

#### Agentic RAG統合
- 法律・判例データの効率的な検索と取得
- コンテキストを考慮した情報提供
- 複数のデータソースを横断した統合検索

#### Claude Agent SDK統合
参考: [Claude Agent SDK Migration Guide](https://code.claude.com/docs/ja/sdk/migration-guide)

- カスタムツールとしての法律・判例検索機能の提供
- 自然言語による法律相談インターフェース
- 法的文書の分析・要約機能

## 技術スタック

- **フレームワーク**: FastAPI
- **パッケージ管理**: uv
- **Python**: 3.10+
- **予定統合**:
  - Claude Agent SDK (`@anthropic-ai/claude-agent-sdk`)
  - MCP (Model Context Protocol) サーバー実装

## プロジェクト構造（予定）

```
e-gov-api-fastAPI/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── laws.py          # 法令API
│   │   │   └── cases.py         # 判例API
│   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── services/
│   │   ├── egov_client.py       # e-gov API クライアント
│   │   ├── case_scraper.py      # 判例スクレイピング
│   │   └── rag_service.py       # RAG統合サービス
│   └── main.py
├── .claude/
│   ├── agents/                   # Claude サブエージェント定義
│   ├── skills/                   # カスタムスキル
│   └── settings.json
├── tests/
├── pyproject.toml
└── README.md
```

## セットアップ

### 必要要件
- Python 3.10以上
- uv パッケージマネージャー

### インストール

```bash
# uvのインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトのセットアップ
uv venv
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate  # Windows

# 依存関係のインストール
uv pip install -e .
```

## API設計（予定）

### 法令エンドポイント

```
GET /api/v1/laws/search        # 法令検索
GET /api/v1/laws/{law_id}      # 特定法令の取得
GET /api/v1/laws/{law_id}/history  # 改正履歴
```

### 判例エンドポイント

```
GET /api/v1/cases/search       # 判例検索
GET /api/v1/cases/{case_id}    # 特定判例の取得
```

## データソース

### 1. e-gov 法令API
- URL: https://elaws.e-gov.go.jp/
- 提供データ: 日本国内の全法令データ
- 更新頻度: リアルタイム

### 2. 裁判所ウェブサイト
- URL: https://www.courts.go.jp/
- 提供データ: 判例情報
- 取得方法: APIまたはWebスクレイピング

### 3. その他検討中のデータソース
- 判例データベースAPI（商用含む）
- 法律関連オープンデータ

## Claude Agent SDK統合例

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("search_law", "日本の法令を検索", {"query": str})
async def search_law(args):
    # e-gov APIを使用した法令検索
    results = await egov_client.search(args["query"])
    return {"content": [{"type": "text", "text": results}]}

@tool("search_case", "判例を検索", {"keywords": str})
async def search_case(args):
    # 判例データベースでの検索
    results = await case_service.search(args["keywords"])
    return {"content": [{"type": "text", "text": results}]}

# MCPサーバーの作成
legal_tools = create_sdk_mcp_server(
    name="legal_tools",
    version="1.0.0",
    tools=[search_law, search_case]
)
```

## 開発ロードマップ

### Phase 1: 基盤構築（現在）
- [ ] FastAPIプロジェクトの初期化
- [ ] e-gov API クライアントの実装
- [ ] 基本的な法令検索エンドポイントの実装

### Phase 2: 判例データの統合
- [ ] 判例データソースの調査・選定
- [ ] スクレイピング/APIクライアントの実装
- [ ] 判例検索エンドポイントの実装

### Phase 3: AI統合
- [ ] Agentic RAGの実装
- [ ] Claude Agent SDK統合
- [ ] MCPサーバーとしての機能提供

### Phase 4: 高度な機能
- [ ] 法令・判例の関連性分析
- [ ] 自然言語による法律相談
- [ ] 法的文書の自動要約

## ライセンス

TBD

## 貢献

TBD

## 参考資料

- [e-gov 法令API](https://elaws.e-gov.go.jp/)
- [Claude Agent SDK Documentation](https://code.claude.com/docs/ja/sdk/migration-guide)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [uv Documentation](https://github.com/astral-sh/uv)
