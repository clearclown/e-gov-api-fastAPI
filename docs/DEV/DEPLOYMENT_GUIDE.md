# インフラデプロイメントガイド

**最終更新:** 2025-11-15

---

## 📁 ディレクトリ構成

```
infra/podmanOrDocker/
├── docker-compose.yml      # Docker/Podman統合構成ファイル
├── Dockerfile             # プロダクション用Dockerfile (uv使用)
├── Dockerfile.lite        # 軽量版 (基本機能のみ)
├── Dockerfile.podman      # 旧Podman専用 (非推奨)
├── INTEGRATION_SUMMARY.md # 過去の統合サマリー
└── DEPLOYMENT_GUIDE.md    # このファイル
```

---

## 🎯 設計方針

### Docker/Podman互換性

**重要:** PodmanとDockerは完全互換性があるため、以下のように統一しています:

- ✅ ファイル名: `docker-compose.yml` (podman-compose.ymlではない)
- ✅ Dockerfile: `Dockerfile` (Dockerfile.podmanは非推奨)
- ✅ コマンド: `podman compose` または `docker compose` 両方で動作

### VPN/Tailscale対応

すべてのサービスが `0.0.0.0` にバインドされており、以下の環境からアクセス可能:
- ローカルホスト (127.0.0.1)
- ローカルネットワーク (192.168.x.x)
- **Tailscale VPN** (100.x.x.x)
- その他のVPNネットワーク

### 環境変数ベース設定

`.env` ファイルで以下を設定可能:
- `API_PORT` - APIサーバーポート (デフォルト: 8000)
- `POSTGRES_PORT` - PostgreSQLポート (デフォルト: 5432)
- `REDIS_PORT` - Redisポート (デフォルト: 6379)
- `UVICORN_WORKERS` - Uvicornワーカー数 (デフォルト: 4)

---

## 🚀 使用方法

### 環境準備

```bash
# プロジェクトルートに移動
cd /path/to/e-gov-api-fastAPI

# 環境変数ファイルを作成
cp .env.example .env
# 必要に応じて .env を編集
```

### ビルド

```bash
# スクリプトを使用 (推奨)
./scripts/podman-build.sh

# または手動で
cd infra/podmanOrDocker
podman build -f Dockerfile -t e-gov-api-fastapi:latest ../..
# または: docker build -f Dockerfile -t e-gov-api-fastapi:latest ../..
```

### 起動

```bash
# スクリプトを使用 (推奨)
./scripts/podman-up.sh

# または手動で
podman compose -f infra/podmanOrDocker/docker-compose.yml up -d
# または: docker compose -f infra/podmanOrDocker/docker-compose.yml up -d
```

### 停止

```bash
# スクリプトを使用
./scripts/podman-down.sh

# または手動で
podman compose -f infra/podmanOrDocker/docker-compose.yml down
# または: docker compose -f infra/podmanOrDocker/docker-compose.yml down
```

### ログ確認

```bash
# APIサーバー
podman logs -f egov-api

# PostgreSQL
podman logs -f egov-postgres

# Redis
podman logs -f egov-redis
```

---

## 🔧 設定検証

### docker-compose.yml の検証

```bash
podman compose -f infra/podmanOrDocker/docker-compose.yml config
# または: docker compose -f infra/podmanOrDocker/docker-compose.yml config
```

### サービス確認

```bash
# 起動中のサービス一覧
podman ps
# または: docker ps

# ネットワーク確認
podman network ls
# または: docker network ls
```

---

## 📊 サービス構成

### 1. PostgreSQL (pgvector)

- **イメージ:** `docker.io/pgvector/pgvector:pg16`
- **ポート:** `${POSTGRES_PORT:-5432}` (0.0.0.0バインド)
- **データベース:** `egov_db`
- **ユーザー:** `egov`
- **機能:** ベクトル検索対応 (pgvector拡張)

### 2. Redis

- **イメージ:** `docker.io/library/redis:7-alpine`
- **ポート:** `${REDIS_PORT:-6379}` (0.0.0.0バインド)
- **設定:** `--bind 0.0.0.0 --protected-mode no`
- **用途:** キャッシュ (オプション)

### 3. FastAPI Application

- **ビルド:** カスタムDockerfile (uv使用)
- **ポート:** `${API_PORT:-8000}` (0.0.0.0バインド)
- **ワーカー:** `${UVICORN_WORKERS:-4}`
- **依存:** PostgreSQL, Redis (ヘルスチェック完了後に起動)

---

## 🌐 アクセスURL

### ローカル

```
Health:  http://localhost:8000/health
API Docs: http://localhost:8000/docs
OpenAPI: http://localhost:8000/openapi.json
```

### VPN経由 (Tailscale例)

```
Health:  http://100.82.83.122:8000/health
API Docs: http://100.82.83.122:8000/docs
```

### ローカルネットワーク

```
Health:  http://192.168.0.13:8000/health
API Docs: http://192.168.0.13:8000/docs
```

---

## 🔐 セキュリティ考慮事項

### 0.0.0.0 バインディング

**利点:**
- VPN/Tailscale経由でのアクセスが可能
- マルチホーム環境での柔軟性

**注意点:**
- ファイアウォール設定が重要
- プロダクション環境では適切なアクセス制御を実施
- VPN内のみでの使用を推奨

### Redis設定

```yaml
command: redis-server --bind 0.0.0.0 --protected-mode no
```

- `--protected-mode no`: ローカルネットワーク/VPN内での使用を想定
- プロダクション環境では認証設定を推奨 (`requirepass`)

---

## 📝 環境変数リファレンス

### アプリケーション設定

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| `APP_NAME` | `e-gov API FastAPI` | アプリケーション名 |
| `APP_VERSION` | `0.1.0` | バージョン |
| `DEBUG` | `true` | デバッグモード |
| `LOG_LEVEL` | `INFO` | ログレベル |

### ネットワーク設定

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| `API_HOST` | `0.0.0.0` | APIホストバインド |
| `API_PORT` | `8000` | APIポート |

### データベース設定

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| `POSTGRES_DB` | `egov_db` | データベース名 |
| `POSTGRES_USER` | `egov` | データベースユーザー |
| `POSTGRES_PASSWORD` | `egov_password` | データベースパスワード |
| `POSTGRES_PORT` | `5432` | PostgreSQLポート |

### Redis設定

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| `REDIS_ENABLED` | `false` | Redis有効化 |
| `REDIS_PORT` | `6379` | Redisポート |
| `REDIS_URL` | `redis://redis:6379/0` | Redis接続URL |

### e-gov API設定

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| `EGOV_API_BASE_URL` | `https://laws.e-gov.go.jp` | e-gov APIベースURL |
| `EGOV_API_TIMEOUT` | `30` | APIタイムアウト(秒) |

### Uvicorn設定

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| `UVICORN_WORKERS` | `4` | ワーカープロセス数 |
| `UVICORN_TIMEOUT` | `60` | タイムアウト(秒) |

---

## ⚠️ 既知の制限事項

### ディスク容量要件

**フルビルド (PyTorch含む):**
- 必要容量: 約10-15GB
- PyTorch + CUDA依存関係: 約3-4GB
- その他依存関係: 約2-3GB

**現在の問題:**
- ディスク容量不足により、フルビルドが失敗する場合があります
- 解決策:
  1. 追加ディスク容量の確保 (10GB以上推奨)
  2. `Dockerfile.lite` の使用 (基本機能のみ、PyTorchなし)
  3. 十分な容量がある環境でビルド後、イメージを転送

### 軽量版の使用

```bash
# Dockerfile.lite を使用
cd infra/podmanOrDocker
podman build -f Dockerfile.lite -t e-gov-api-fastapi:lite ../..
```

**制限事項:**
- 埋め込み生成機能なし (PyTorchなし)
- 基本的なAPI機能のみ提供
- ベクトル検索は利用不可

---

## 🔄 更新履歴

### 2025-11-15
- ✅ インフラファイルを `infra/podmanOrDocker/` に統合
- ✅ Docker/Podman互換性のため `docker-compose.yml` に統一
- ✅ VPN対応 (0.0.0.0バインディング)
- ✅ 環境変数ベースの設定
- ✅ スクリプトパス更新
- ✅ `.gitignore` 更新
- ✅ ルートディレクトリ整理

---

## 📚 関連ドキュメント

- `INTEGRATION_SUMMARY.md` - 過去の統合作業サマリー
- `/docs/SETUP_UV_PODMAN.md` - uv/Podmanセットアップガイド
- `/UV_PODMAN_SETUP_SUMMARY.md` - uv/Podman移行サマリー
- `/VPN_PORT_CONFIG_SUMMARY.md` - VPN対応・ポート設定サマリー
- `/README.md` - プロジェクト全体ガイド

---

## 🎉 まとめ

すべてのインフラファイルが `infra/podmanOrDocker/` に統合され、Docker/Podman両方で動作する統一された環境が完成しました。

**主な特徴:**
- ✅ Docker/Podman完全互換
- ✅ VPN/Tailscale対応
- ✅ 環境変数ベース設定
- ✅ ポート競合回避
- ✅ 本番環境対応

**次のステップ:**
1. 十分なディスク容量の確保
2. `./scripts/podman-build.sh` でビルド
3. `./scripts/podman-up.sh` で起動
4. VPN経由でのアクセステスト
