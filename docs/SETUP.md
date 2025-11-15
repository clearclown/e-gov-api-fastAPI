# セットアップガイド

## 前提条件

- Python 3.10以上
- PostgreSQL 14以上（pgvector拡張機能対応）
- uv パッケージマネージャー

## 1. 環境構築

### 1.1 uvのインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 1.2 仮想環境の作成

```bash
# プロジェクトディレクトリに移動
cd e-gov-api-fastAPI

# 仮想環境を作成
uv venv

# 仮想環境を有効化
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate  # Windows
```

### 1.3 依存関係のインストール

```bash
# 本番用依存関係
uv pip install -e .

# 開発用依存関係も含める
uv pip install -e ".[dev]"
```

## 2. データベースセットアップ

### 2.1 PostgreSQLのインストール

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql@14

# PostgreSQLを起動
sudo service postgresql start  # Linux
brew services start postgresql@14  # macOS
```

### 2.2 pgvector拡張機能のインストール

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-14-pgvector

# macOS (Homebrew)
brew install pgvector

# または、ソースからビルド
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### 2.3 データベースの作成

```bash
# PostgreSQLに接続
sudo -u postgres psql

# データベースとユーザーを作成
CREATE DATABASE legal_db;
CREATE USER legal_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE legal_db TO legal_user;

# 接続を終了
\q
```

### 2.4 データベーススキーマの初期化

```bash
# 初期化スクリプトを実行
psql -U postgres -d legal_db -f scripts/init_db.sql

# または、環境変数を使用
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/legal_db"
psql $DATABASE_URL -f scripts/init_db.sql
```

## 3. 環境変数の設定

### 3.1 .envファイルの作成

```bash
# .env.exampleをコピー
cp .env.example .env

# .envファイルを編集
vim .env  # または任意のエディタ
```

### 3.2 必要な環境変数

```bash
# データベース接続文字列
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/legal_db

# Anthropic API Key（Phase 3のRAG機能に必要）
ANTHROPIC_API_KEY=your_api_key_here

# 埋め込みモデル設定
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
EMBEDDING_DIMENSION=768

# RAG設定
RAG_TOP_K=5
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50

# ベクトル検索設定
VECTOR_INDEX_LISTS=100

# アプリケーション設定
DEBUG=false
LOG_LEVEL=INFO
```

## 4. データの準備（Phase 3向け）

### 4.1 法令データの取得

```bash
# Phase 1で実装予定のe-gov APIクライアントを使用
# python -m app.scripts.fetch_laws
```

### 4.2 判例データの取得

```bash
# Phase 2で実装予定の判例スクレイパーを使用
# python -m app.scripts.fetch_cases
```

### 4.3 埋め込みベクトルの生成

```bash
# 法令と判例の埋め込みベクトルを生成
python -m app.batch.generate_embeddings

# ベクトルインデックスを作成
psql $DATABASE_URL -f scripts/create_vector_indexes.sql
```

## 5. アプリケーションの起動

### 5.1 開発サーバーの起動

```bash
# FastAPIサーバーを起動
python -m app.main

# または、uvicornを直接使用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5.2 動作確認

```bash
# ヘルスチェック
curl http://localhost:8000/health

# APIドキュメント
# ブラウザで http://localhost:8000/docs にアクセス
```

## 6. テストの実行

### 6.1 全テストの実行

```bash
pytest
```

### 6.2 カバレッジ付きテスト

```bash
pytest --cov=app --cov-report=html
```

### 6.3 特定のテストファイルのみ実行

```bash
pytest tests/test_rag_service.py
```

## 7. トラブルシューティング

### pgvector拡張機能が見つからない

```bash
# PostgreSQLの拡張機能ディレクトリを確認
pg_config --sharedir

# pgvectorが正しくインストールされているか確認
ls $(pg_config --sharedir)/extension/vector*
```

### 埋め込みモデルのダウンロードエラー

```bash
# sentence-transformersのキャッシュディレクトリを確認
echo $SENTENCE_TRANSFORMERS_HOME

# 手動でモデルをダウンロード
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')"
```

### データベース接続エラー

```bash
# PostgreSQLが起動しているか確認
sudo service postgresql status

# 接続文字列を確認
echo $DATABASE_URL

# 直接psqlで接続確認
psql $DATABASE_URL
```

## 8. 本番環境へのデプロイ

### 8.1 環境変数の設定

本番環境では、以下の環境変数を適切に設定してください：

- `DATABASE_URL`: 本番データベースの接続文字列
- `ANTHROPIC_API_KEY`: Anthropic APIキー
- `DEBUG=false`: デバッグモードを無効化
- `LOG_LEVEL=INFO`: ログレベルを適切に設定

### 8.2 Gunicornでの起動

```bash
# Gunicornをインストール
uv pip install gunicorn

# 起動
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 参考資料

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [sentence-transformers Documentation](https://www.sbert.net/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
