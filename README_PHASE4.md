# Phase 4: 高度な分析機能 実装完了

## 概要

Phase 4（高度な分析機能）の実装が完了しました。このフェーズでは以下の機能を提供します：

1. **法令・判例関連性分析**（RelationshipAnalyzer）
2. **会話型法律相談**（ConversationService）
3. **法的文書自動要約**（SummarizationService）

## 実装された機能

### 1. 法令・判例関連性分析

#### 引用グラフ構築
- NetworkXを使用した引用関係のグラフ化
- 法令ノードと判例ノードの管理
- 直接引用・間接引用の追跡

#### 主要API
- `GET /api/v1/analytics/laws/{law_id}/related-cases` - 関連判例検索
- `GET /api/v1/analytics/laws/most-cited` - 最多引用法令
- `GET /api/v1/analytics/visualize/{type}/{id}` - 関連図可視化
- `GET /api/v1/analytics/graph/stats` - グラフ統計情報

### 2. 会話型法律相談

#### 会話履歴管理
- 会話セッションの作成・管理
- コンテキストを考慮した質問応答
- 会話履歴の保持・参照

#### 主要API
- `POST /api/v1/conversation/start` - 会話セッション開始
- `POST /api/v1/conversation/ask` - 質問送信
- `GET /api/v1/conversation/history/{conversation_id}` - 会話履歴取得

### 3. 法的文書自動要約

#### 要約スタイル
- **brief**: 簡潔（200文字程度）
- **detailed**: 詳細（500文字程度）
- **plain**: 平易な言葉（一般向け）

#### 主要API
- `GET /api/v1/summarize/case/{case_id}` - 判例要約
- `GET /api/v1/summarize/law/{law_id}/article/{article_number}` - 条文解説
- `GET /api/v1/summarize/compare/laws` - 法令比較

## セットアップ

### 1. 依存関係のインストール

```bash
# uvを使用する場合
uv venv
source .venv/bin/activate  # Linux/Mac
uv pip install -e ".[dev]"

# pipを使用する場合
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"
```

### 2. 環境変数の設定

```bash
cp .env.example .env
# .envファイルを編集（必要に応じて）
```

### 3. サーバーの起動

```bash
# 開発サーバー起動
uvicorn app.main:app --reload

# または
python -m app.main
```

サーバーは http://localhost:8000 で起動します。

### 4. APIドキュメントの確認

ブラウザで以下のURLにアクセス：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## テストの実行

```bash
# 全テスト実行
pytest

# カバレッジ付きで実行
pytest --cov=app --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/test_relationship_analyzer.py

# 詳細出力
pytest -v
```

## 使用例

### 関連判例の検索

```bash
curl http://localhost:8000/api/v1/analytics/laws/405AC0000000087/related-cases?limit=5
```

### 会話型相談

```bash
# 会話開始
curl -X POST http://localhost:8000/api/v1/conversation/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001"}'

# 質問送信
curl -X POST http://localhost:8000/api/v1/conversation/ask \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user_001_1699999999",
    "question": "契約を解除するにはどうすればよいですか？"
  }'
```

### 判例要約

```bash
# 簡潔な要約
curl http://localhost:8000/api/v1/summarize/case/CASE-2024-001?style=brief

# 詳細な要約
curl http://localhost:8000/api/v1/summarize/case/CASE-2024-001?style=detailed

# 平易な要約
curl http://localhost:8000/api/v1/summarize/case/CASE-2024-001?style=plain
```

## プロジェクト構造

```
e-gov-api-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPIアプリケーション
│   ├── api/
│   │   └── endpoints/
│   │       ├── analytics.py       # 分析API
│   │       ├── conversation.py    # 会話API
│   │       └── summarization.py   # 要約API
│   ├── models/
│   │   ├── law.py                 # 法令モデル
│   │   └── case.py                # 判例モデル
│   ├── services/
│   │   ├── relationship_analyzer.py  # 関連性分析
│   │   ├── conversation_service.py   # 会話サービス
│   │   ├── summarization_service.py  # 要約サービス
│   │   ├── rag_service.py            # RAGサービス（モック）
│   │   └── egov_client.py            # e-gov APIクライアント（モック）
│   └── repositories/
│       └── case_repository.py     # 判例リポジトリ（モック）
├── tests/
│   ├── test_relationship_analyzer.py
│   ├── test_conversation_service.py
│   ├── test_summarization_service.py
│   └── test_api.py
├── docs/
│   └── rd/
│       └── feature-04-advanced-features.md
├── pyproject.toml
├── .env.example
└── README_PHASE4.md
```

## 重要な注意事項

### モック実装について

Phase 4では、以下のコンポーネントはモック実装となっています：

1. **データソース**
   - 法令データ（e-gov API）→ Phase 1で実装予定
   - 判例データ → Phase 2で実装予定

2. **AI統合**
   - Claude API呼び出し → Phase 3で実装予定
   - RAGサービス → Phase 3で実装予定

現在のモック実装でも、API構造とデータフローの検証は可能です。

### 今後の実装予定

- **Phase 1**: e-gov API統合（法令データの実データ化）
- **Phase 2**: 判例データ統合（Courts.go.jp等）
- **Phase 3**: Claude API統合（実際のAI要約・RAG実装）

## テスト結果

実装されたテストの範囲：
- 単体テスト: RelationshipAnalyzer, ConversationService, SummarizationService
- APIテスト: 全エンドポイント
- 目標カバレッジ: 75%以上

## ライセンス

MIT

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## サポート

質問や問題がある場合は、GitHubのissueを作成してください。
