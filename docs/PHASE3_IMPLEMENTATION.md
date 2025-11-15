# Phase 3実装ドキュメント: AI統合

## 概要

Phase 3では、Agentic RAGとClaude Agent SDKを統合し、自然言語による法律情報検索とMCPツールとしての機能提供を実現しました。

## 実装内容

### 1. RAGサービス (`app/services/rag_service.py`)

#### 主要機能

- **ベクトル検索**: pgvectorを使用した法令・判例の意味的検索
- **コンテキスト構築**: 検索結果から関連情報を抽出してコンテキストを生成
- **回答生成**: Claude APIを使用して自然言語での回答を生成

#### 使用例

```python
from app.services.rag_service import RAGService

rag = RAGService()

# 法令を検索
results = await rag.search_with_context(
    query="株主総会の決議要件",
    search_type="law",
    top_k=5
)

# Claude APIで回答生成
answer = await rag.generate_answer(
    query="株主総会の決議要件は？",
    context=results["context"]
)
```

### 2. 埋め込みベクトル管理

#### リポジトリ (`app/repositories/embedding_repository.py`)

- 法令・判例データの取得
- 埋め込みベクトルの保存・削除
- 統計情報の取得

#### バッチ処理 (`app/batch/generate_embeddings.py`)

```bash
# 埋め込みベクトルの生成
python -m app.batch.generate_embeddings
```

**処理内容:**
1. 法令・判例データを取得
2. テキストを適切なサイズにチャンク分割
3. sentence-transformersで埋め込みベクトルを生成
4. データベースに保存

**チャンキング戦略:**
- デフォルトチャンクサイズ: 500文字
- オーバーラップ: 50文字
- 句点で分割して文の途中で切れないように調整

### 3. MCPツール (`app/mcp/legal_tools.py`)

#### 提供ツール

1. **search_law**: 法令検索
   - キーワード検索またはRAG検索
   - 自然言語クエリに対応

2. **search_case**: 判例検索
   - 事件名、キーワード、法的問題で検索
   - 裁判所種別でフィルタリング可能

3. **get_law_detail**: 法令詳細取得
   - 法令IDを指定して詳細情報を取得

4. **get_case_detail**: 判例詳細取得
   - 判例IDを指定して詳細情報を取得

5. **ask_legal_question**: 法律相談
   - 自然言語での質問に対して、関連する法令・判例を参照して回答

#### 使用例

```python
from app.mcp.legal_tools import search_law, ask_legal_question

# 法令検索
result = await search_law({
    "query": "会社法",
    "use_rag": True
})

# 法律相談
result = await ask_legal_question({
    "question": "株主総会の決議要件について教えてください"
})
```

### 4. データベーススキーマ

#### 埋め込みテーブル

```sql
-- 法令埋め込み
CREATE TABLE law_embeddings (
    id SERIAL PRIMARY KEY,
    law_id VARCHAR(50) NOT NULL REFERENCES laws(law_id),
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(law_id, chunk_index)
);

-- 判例埋め込み
CREATE TABLE case_embeddings (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) NOT NULL REFERENCES cases(case_id),
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(case_id, chunk_index)
);
```

#### ベクトルインデックス

```sql
-- IVFFlatインデックス（コサイン類似度）
CREATE INDEX ON law_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX ON case_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 5. 設定

#### 環境変数

- `DATABASE_URL`: PostgreSQL接続文字列
- `ANTHROPIC_API_KEY`: Anthropic APIキー
- `EMBEDDING_MODEL`: 埋め込みモデル名
- `EMBEDDING_DIMENSION`: 埋め込みベクトルの次元数
- `RAG_TOP_K`: RAG検索で取得する件数
- `RAG_CHUNK_SIZE`: チャンクサイズ
- `RAG_CHUNK_OVERLAP`: チャンクのオーバーラップサイズ

#### MCP設定 (`.mcp.json`)

```json
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

## テスト

### テストファイル

1. `tests/test_rag_service.py`: RAGサービスのテスト
2. `tests/test_legal_tools.py`: MCPツールのテスト
3. `tests/test_main.py`: FastAPIアプリのテスト

### テスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付き
pytest --cov=app --cov-report=html

# 特定のテストのみ
pytest tests/test_rag_service.py -v
```

## パフォーマンス

### ベンチマーク目標

- **ベクトル検索**: 平均200ms以内
- **RAG検索（全体）**: 平均1秒以内
- **回答生成**: 平均3秒以内（Claude API依存）

### 最適化のポイント

1. **ベクトルインデックスのチューニング**
   - `lists`パラメータの調整（データ量に応じて100-1000）
   - HNSWインデックスの検討（高速だがメモリ消費大）

2. **チャンキング戦略**
   - 文書の特性に応じてチャンクサイズを調整
   - オーバーラップを増やして情報の欠落を防ぐ

3. **キャッシング**
   - 頻繁に検索される法令・判例の埋め込みをメモリキャッシュ
   - Claude APIのプロンプトキャッシング活用

## 依存関係

### Phase 1・Phase 2への依存

Phase 3は以下の機能に依存しています（現在は未実装）：

- **Phase 1**: e-gov APIクライアント（`app/services/egov_client.py`）
- **Phase 2**: 判例リポジトリ（`app/repositories/case_repository.py`）

これらが実装されるまで、MCPツールの一部機能は制限されています。

### 外部ライブラリ

- `sentence-transformers`: 埋め込みベクトル生成
- `pgvector`: PostgreSQLベクトル検索拡張
- `anthropic`: Claude API
- `psycopg`: PostgreSQL接続

## セキュリティ

### API Key管理

- 環境変数でAPIキーを管理
- `.env`ファイルは`.gitignore`に追加済み
- 本番環境では秘密管理サービス（AWS Secrets Managerなど）を推奨

### データベースセキュリティ

- 接続文字列に平文パスワードを含めない
- SSL/TLS接続の使用を推奨
- 最小権限の原則に従ったユーザー権限設定

## 今後の拡張

### 短期的な改善

1. Claude Agent SDKの正式統合
2. より高度なチャンキング戦略（意味的分割）
3. ハイブリッド検索（キーワード + ベクトル）
4. リランキング機能の追加

### 長期的な展望

1. マルチモーダル対応（判例の図表解析）
2. 時系列分析（法令の改正履歴追跡）
3. 法令間の関連性グラフ構築
4. カスタムファインチューニングされた埋め込みモデル

## トラブルシューティング

### よくある問題

1. **埋め込み生成が遅い**
   - GPUを使用してsentence-transformersを高速化
   - バッチサイズを調整

2. **ベクトル検索の精度が低い**
   - チャンクサイズを調整
   - 異なる埋め込みモデルを試す
   - インデックスパラメータを調整

3. **Claude APIタイムアウト**
   - タイムアウト設定を増やす
   - コンテキストサイズを削減
   - プロンプトキャッシングを活用

## 参考資料

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [sentence-transformers Documentation](https://www.sbert.net/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Agent SDK Migration Guide](https://code.claude.com/docs/ja/sdk/migration-guide)
