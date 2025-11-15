<div align="center">

# 📚 e-gov API FastAPI

**日本の法令・判例データを提供する高速APIサーバー**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compatible-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Podman](https://img.shields.io/badge/Podman-Compatible-892CA0?style=for-the-badge&logo=podman&logoColor=white)](https://podman.io/)
[![uv](https://img.shields.io/badge/uv-Package_Manager-FF6B35?style=for-the-badge)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[🇯🇵 日本語](README.md) | [🇬🇧 English](docs/readmeLang/README.en.md) | [🇨🇳 简体中文](docs/readmeLang/README.zh-CN.md) | [🇹🇼 繁體中文](docs/readmeLang/README.zh-TW.md) | [🇷🇺 Русский](docs/readmeLang/README.ru.md) | [🇮🇷 فارسی](docs/readmeLang/README.fa.md) | [🇸🇦 العربية](docs/readmeLang/README.ar.md)

</div>

---

## 📸 スクリーンショット

<div align="center">

### API ドキュメント (Swagger UI)

![API Documentation](docs/pics/api-docs.png)

*FastAPIによる自動生成APIドキュメント*

---

### 法令検索のレスポンス例

![Law Search Response](docs/pics/law-search.png)

*キーワード「表現の自由」での検索結果*

---

### 判例検索のレスポンス例

![Case Search Response](docs/pics/case-search.png)

*キーワード「表現の不自由展かんさい」での判例検索結果*

</div>

---

## 📖 簡単な説明

**e-gov API FastAPI** は、日本の法令および判例データに高速アクセスできるRESTful APIサーバーです。

[e-gov 法令API](https://elaws.e-gov.go.jp/) および [裁判所ウェブサイト](https://www.courts.go.jp/) と連携し、リアルタイムで最新の法律情報を提供します。

**主な機能:**
- 🔍 法令検索・詳細取得・改正履歴
- ⚖️ 判例検索・詳細取得
- 📊 法令と判例の関係性分析
- 🚀 Redisキャッシュによる高速化
- 🌐 VPN/Tailscale対応

---

## 🎯 なぜこれが必要なのか + 何をするものなのか

### 課題

日本の法律情報にアクセスする際、以下の問題があります：

- **法令データの散在**: 政府APIは使いづらく、ドキュメント不足
- **判例データの取得困難**: 体系的なAPIが存在しない
- **データ統合の複雑さ**: 法令と判例の関連性を分析する仕組みがない

### 解決策

このAPIサーバーは、複数のデータソースを統合し、開発者が簡単に日本の法律情報にアクセスできるようにします。

**何をするものなのか:**
- 法令データベースへの統一的なアクセス
- 判例データの検索・取得
- 法令と判例の関係性分析
- 高速レスポンス（キャッシュ機能）

**ユースケース:**
- 法律相談アプリケーションのバックエンド
- リーガルテック製品の基盤API
- 法律データ分析・研究
- 法令改正の自動追跡システム

---

## 🚀 Installation

### 必要な環境

- Python 3.12+
- Docker または Podman
- uv (パッケージマネージャー)

### 方法1: Docker/Podman で起動（推奨）

```bash
# リポジトリのクローン
git clone https://github.com/clearclown/e-gov-api-fastAPI.git
cd e-gov-api-fastapi

# 環境変数の設定
cp .env.example .env

# 起動
podman compose up -d
# または
docker compose up -d

# 動作確認
curl http://localhost:8000/health
```

### 方法2: uv で開発環境セットアップ

```bash
# uv のインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 仮想環境の作成
uv venv

# 仮想環境の有効化
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 依存関係のインストール
uv pip install -e .

# 開発サーバーの起動
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### アクセス

- **API ドキュメント**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **ヘルスチェック**: http://localhost:8000/health

---

## 🗑️ Uninstall

### Docker/Podman 環境

```bash
# サービスの停止と削除
podman compose down

# ボリュームも含めて完全削除
podman compose down -v

# イメージの削除
podman rmi e-gov-api-fastapi-app
```

### uv 環境

```bash
# 仮想環境の削除
rm -rf .venv

# キャッシュのクリア
uv cache clean
```

---

## 📚 Documentation

### 基本技術

| カテゴリ | 技術 |
|---------|------|
| **フレームワーク** | FastAPI |
| **言語** | Python 3.12+ |
| **データベース** | PostgreSQL 16 + pgvector |
| **キャッシュ** | Redis 7 |
| **パッケージマネージャー** | uv |
| **コンテナ** | Docker / Podman |
| **外部API** | e-gov 法令API, 裁判所 |

### 仕組み

```
┌─────────────┐
│  クライアント  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│   FastAPI アプリケーション   │
│  ┌──────────────────────┐  │
│  │  法令エンドポイント    │  │
│  │  判例エンドポイント    │  │
│  │  分析エンドポイント    │  │
│  └──────────────────────┘  │
└──┬───────────┬──────────┬───┘
   │           │          │
   ▼           ▼          ▼
┌──────┐  ┌────────┐  ┌─────────┐
│Redis │  │Postgres│  │e-gov API│
│Cache │  │Database│  │裁判所DB  │
└──────┘  └────────┘  └─────────┘
```

**データフロー:**
1. クライアントがAPIリクエストを送信
2. FastAPIがリクエストを処理
3. Redisキャッシュを確認（ヒット時は即座にレスポンス）
4. キャッシュミス時は外部API（e-gov/裁判所）からデータ取得
5. 取得データをPostgreSQLに保存
6. レスポンスを返却し、Redisにキャッシュ

### インフラ

**ファイル構成:**
```
e-gov-api-fastapi/
├── app/                    # アプリケーションコード
│   ├── api/               # APIエンドポイント
│   ├── core/              # コア設定・DB接続
│   ├── services/          # ビジネスロジック
│   └── main.py            # エントリーポイント
├── infra/
│   └── podmanOrDocker/    # Docker/Podman設定
│       ├── Dockerfile     # フル版（AI機能含む）
│       └── Dockerfile.lite # 軽量版（API機能のみ）
├── docs/                   # ドキュメント
│   ├── pics/              # スクリーンショット
│   └── readmeLang/        # 多言語README
├── scripts/               # 便利スクリプト
├── docker-compose.yml     # メインCompose設定
├── pyproject.toml         # プロジェクト設定
└── .env                   # 環境変数
```

**リソース使用量:**

軽量版（デフォルト）:
- API サーバー: ~600MB
- PostgreSQL: ~500MB
- Redis: ~50MB
- **合計:** ~1.2GB

フル版（AI機能含む）:
- API サーバー: ~3-4GB (PyTorch + CUDA)
- PostgreSQL: ~500MB
- Redis: ~50MB
- **合計:** ~4-5GB

### ネットワーク

**アクセス方法:**

すべてのサービスは `0.0.0.0` でリッスンしており、以下の方法でアクセス可能：

1. **ローカルホスト**: `http://localhost:8000`
2. **ローカルネットワーク**: `http://[ホストIP]:8000`
3. **Tailscale/VPN**: `http://[TailscaleのIP]:8000`

**ポート設定（.env で変更可能）:**
- API サーバー: `8000`
- PostgreSQL: `5432`
- Redis: `6379`

**VPN/Tailscale対応:**

0.0.0.0 バインディングにより、リモートアクセスが可能です。

### これからの課題

**Phase 1 & 2: 基本機能** ✅ **完了**
- [x] e-gov API クライアント実装
- [x] 法令検索・詳細取得エンドポイント
- [x] 判例スクレイピング・検索機能
- [x] Redis キャッシュ実装
- [x] PostgreSQL データベース統合
- [x] Docker/Podman 完全対応

**Phase 3: AI統合機能** 🔄 **計画中**
- [ ] AgenticRAG による意味的検索
- [ ] ベクトル検索（pgvector使用）
- [ ] Claude API 統合
- [ ] 自然言語での質問応答
- [ ] MCP サーバー実装

**Phase 4: 高度な分析機能** 🔄 **計画中**
- [ ] 法令・判例の関係性グラフ可視化
- [ ] 判例引用ネットワーク分析
- [ ] 自動要約生成
- [ ] チャット形式の法律相談インターフェース

---

## 🤝 Contributing

プロジェクトへの貢献を歓迎します！

**バグ報告・機能リクエスト:**

[GitHub Issues](https://github.com/clearclown/e-gov-api-fastAPI/issues) で報告してください。

**プルリクエスト:**

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'feat: Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

**開発ガイドライン:**
- コードスタイル: PEP 8 に準拠
- コミットメッセージ: Conventional Commits 形式
- テスト: 新機能には必ずテストを追加

---

## 📚 Resources

### 公式ドキュメント
- [FastAPI](https://fastapi.tiangolo.com/)
- [e-gov 法令API 仕様](https://elaws.e-gov.go.jp/apitop/)
- [uv - Python パッケージマネージャー](https://github.com/astral-sh/uv)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)

### 関連プロジェクト
- [pgvector](https://github.com/pgvector/pgvector) - PostgreSQL ベクトル検索拡張
- [Claude API](https://docs.anthropic.com/) - Anthropic Claude AI

### データソース
- [e-gov 法令データベース](https://elaws.e-gov.go.jp/)
- [裁判所ウェブサイト](https://www.courts.go.jp/)

---

## ⚖️ Legal

このプロジェクトは以下のデュアルライセンスで提供されています：

### MIT License
個人・商用利用に最適

[LICENSE-MIT](LICENSE-MIT) を参照

### Apache License 2.0
企業利用・特許保護が必要な場合

[LICENSE-APACHE](LICENSE-APACHE) を参照

**お好きなライセンスを選択してご利用ください。**

---

<div align="center">

**⭐ このプロジェクトが役に立った場合は、スターをお願いします！**

Made with ❤️ by [clearclown](https://github.com/clearclown)

📧 Contact: clearclown@gmail.com

</div>
