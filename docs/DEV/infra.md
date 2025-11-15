# インフラストラクチャ構成ドキュメント

**最終更新日:** 2025-11-15
**対象:** e-gov API FastAPI プロジェクト

---

## 📊 システムアーキテクチャ概要

### 全体構成

```
┌──────────────────────────────────────────────────────────┐
│                      インターネット/VPN                        │
│              (Tailscale, ローカルネットワーク)           │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │                                     │
        │           ファイアウォール                           │
        │          (UFW / firewalld / iptables)                      │
        └────────┬───────────────────┬────────┘
       │                     │
       ├─── ローカルホスト (127.0.0.1:8000)
       ├─── ローカルネットワーク (192.168.x.x:8000)
       └─── VPN/Tailscale (100.x.x.x:8000)
                         │
                         │
        ┌────────────────────────────────────┐
        │   Docker/Podman Network    │
        │    (egov-network)          │
        │      Bridge Mode           │
        └────┬───────────┬───────────┘
                      │
        ┌─────────────┴─────────────┐
        │             │             │
   ┌─────────┐   ┌──────────┐   ┌────────┐
   │  app   │   │postgres │   │ redis  │
   │ :8000  │   │ :5432   │   │ :6379  │
   └─────────┘   └──────────┘   └────────┘
```

---

## 🏗️ インフラコンポーネント

### コンポーネント概要

| コンポーネント | バージョン | ポート番号 | プロトコル | 用途 |
|---------|--------------|-------------|-----------|------|
| FastAPI | 0.109+ | ${API_PORT:-8000} | HTTP | API エンドポイント |
| PostgreSQL | 16 | ${POSTGRES_PORT:-5432} | TCP | データベース |
| Redis | 7-alpine | ${REDIS_PORT:-6379} | TCP | キャッシュ |

### 1. FastAPI アプリケーション

**役割:** メインAPI サーバー

**技術スタック:**
- **フレームワーク:** FastAPI 0.109+
- **ASGI サーバー:** Uvicorn
- **言語:** Python 3.12+
- **パッケージマネージャー:** uv

**リソース要件:**

| バージョン | CPU | メモリ | ディスク |
|-----------|-----|--------|---------|
| **Lite版** | 1-2 cores | 512MB-1GB | 600MB |
| **Full版** | 2-4 cores | 4-8GB | 4-5GB |

**設定:**
```yaml
# docker-compose.yml
app:
  build:
    context: .
    dockerfile: infra/podmanOrDocker/Dockerfile.lite
  ports:
    - "0.0.0.0:${API_PORT:-8000}:8000"
  environment:
    - UVICORN_WORKERS=${UVICORN_WORKERS:-4}
  restart: unless-stopped
```

**ワーカー設定:**
- 設定可能: `UVICORN_WORKERS` 環境変数で調整
- 推奨値: `CPU コア数 × 2 + 1`
- 例: 4コアの場合は 9ワーカー

---

### 2. PostgreSQL + pgvector

**役割:** メインデータベース + ベクトル検索

**使用バージョン:** PostgreSQL 16 + pgvector extension

**リソース要件:**

| 項目 | 値 |
|-----|---|
| CPU | 1-2 cores |
| メモリ | 512MB-2GB |
| ディスク | 1GB-10GB (データ量に依存) |

**基本設定:**
```yaml
postgres:
  image: docker.io/pgvector/pgvector:pg16
  environment:
    POSTGRES_DB: egov_db
    POSTGRES_USER: egov
    POSTGRES_PASSWORD: egov_password
  ports:
    - "0.0.0.0:${POSTGRES_PORT:-5432}:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U egov -d egov_db"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**重要機能:**
- **pgvector:** ベクトル埋め込み検索 (Phase 3で使用)
- インデックス作成: `CREATE INDEX ON table USING ivfflat (embedding vector_cosine_ops)`

**バックアップ運用:**
```bash
# バックアップ作成
podman exec egov-postgres pg_dump -U egov egov_db > backup.sql

# リストア
podman exec -i egov-postgres psql -U egov -d egov_db < backup.sql
```

---

### 3. Redis

**役割:** キャッシュサーバー

**使用バージョン:** Redis 7 Alpine

**リソース要件:**

| 項目 | 値 |
|-----|---|
| CPU | 0.5-1 core |
| メモリ | 256MB-1GB |
| ディスク | 50MB-500MB |

**設定:**
```yaml
redis:
  image: docker.io/library/redis:7-alpine
  command: redis-server --bind 0.0.0.0 --protected-mode no
  ports:
    - "0.0.0.0:${REDIS_PORT:-6379}:6379"
```

**キャッシュ運用:**
- TTL設定: データ型別 (24時間、検索結果 1時間)
- LRU (Least Recently Used) エビクション
- 最大メモリ: 512MB

**監視:**
```bash
# Redis 接続確認
podman exec egov-redis redis-cli INFO

# メモリ使用量
podman exec egov-redis redis-cli INFO memory

# キャッシュ統計
podman exec egov-redis redis-cli INFO stats
```

---

## 🌐 ネットワーク構成

### コンテナネットワーク

```
┌────────────────────────────────────────┐
│         egov-network (bridge)           │
│                                          │
│  ┌──────────┐  ┌──────────┐            │
│  │   app    │  │ postgres │            │
│  │  :8000   │  │  :5432   │            │
│  └─────┬────┘  └─────┬────┘            │
│        │            │                   │
│        │       ┌────┴─────┐            │
│        └───────┤  redis   │            │
│                │  :6379   │            │
│                └──────────┘            │
└────────────────────────────────────────┘
         │
         │ Port Mapping
         ▼
   ┌─────────────────┐
   │  ホストOS        │
   │  0.0.0.0:8000  │
   │  0.0.0.0:5432  │
   │  0.0.0.0:6379  │
   └─────────────────┘
```

**ネットワーク設定:**
```yaml
networks:
  egov-network:
    driver: bridge
```

**コンテナ間接続:**
- FastAPI → PostgreSQL: `postgresql://egov:password@postgres:5432/egov_db`
- FastAPI → Redis: `redis://redis:6379/0`
- DNS解決: Docker/PodmanのコンテナDNS機能

---

## 💾 データ永続化

### ボリューム管理

```yaml
volumes:
  postgres_data:
    driver: local
```

**データ保存場所:**
- PostgreSQL: `/var/lib/postgresql/data`
- 推奨サイズ: 初期1GB、最大10GB~

**ボリューム管理:**
```bash
# ボリューム一覧
podman volume ls

# ボリューム詳細
podman volume inspect postgres_data

# ボリューム削除（注意！データ消失）
podman volume rm postgres_data

# バックアップ
podman run --rm -v postgres_data:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/postgres_backup.tar.gz /data
```

---

## 🔐 セキュリティ

### ネットワークセキュリティ

**0.0.0.0 バインディング:**
- **メリット:** VPN/Tailscaleから接続可能
- **リスク:** すべてのインターフェースから接続可能な状態
- **対策:**
  - ファイアウォール設定 (必須)
  - VPNのみに限定する運用
  - または127.0.0.1に変更し外部公開を防止

**ファイアウォール設定 (Ubuntu/Debian):**
```bash
# UFW使用
sudo ufw allow from 100.0.0.0/8 to any port 8000  # Tailscale
sudo ufw allow from 192.168.0.0/16 to any port 8000  # ローカルネットワーク
sudo ufw deny 8000  # その他は拒否
```

### 環境変数セキュリティ

**パーミッション設定:**
```bash
# .env ファイルを読み取り専用に設定
chmod 600 .env

# Gitで追跡されないように
echo ".env" >> .gitignore
```

**セキュアな運用:**
- 機密情報は環境変数に
- 最小権限の原則
- SSL/TLS暗号化 (本番環境)

---

## 📊 監視とログ

### ログ管理

**ログ確認:**
```bash
# すべてのコンテナのログ
podman compose logs

# 特定コンテナ
podman compose logs app
podman compose logs postgres
podman compose logs redis

# リアルタイム監視
podman compose logs -f app
```

**ログローテーション:**
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### ヘルスチェック

**エンドポイント:**
- Health: `GET /health`
- Metrics (オプション): `GET /metrics`

**ヘルスチェックスクリプト:**
```bash
#!/bin/bash
# health_check.sh

HEALTH_URL="http://localhost:8000/health"

response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $response -eq 200 ]; then
  echo "✓ API is healthy"
  exit 0
else
  echo "✗ API is down (HTTP $response)"
  exit 1
fi
```

---

## 🚀 デプロイメント運用

### 開発環境

```bash
# uv使用 (ローカル開発)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### ステージング環境

```bash
# Docker Composeでステージング環境を構築
podman compose -f docker-compose.staging.yml up -d
```

### 本番環境

**推奨構成:**
1. リバースプロキシ (Nginx/Caddy)
2. SSL/TLS証明書 (Let's Encrypt)
3. 冗長化構成 (Kubernetes/Docker Swarm)
4. バックアップ自動化
5. 監視 (Prometheus + Grafana)

**Blue-Green デプロイメント:**
```bash
# Greenバージョンを構築
podman run -d --name egov-api-green \
  -p 8001:8000 egov-api-fastapi:latest

# ヘルスチェック後、成功したら切り替え
# (リバースプロキシで切り替える)

# Blueバージョンを停止
podman stop egov-api-blue
```

---

## 📈 パフォーマンス最適化

### アプリケーション最適化

**Uvicornワーカー調整:**
```bash
# CPU依存型
UVICORN_WORKERS=$(($(nproc) * 2 + 1))

# I/O依存型
UVICORN_WORKERS=$(($(nproc) * 4))
```

**非同期処理:**
- FastAPIの非同期エンドポイント活用
- データベースクエリの並列化
- 外部APIコールの非同期化

### データベース最適化

**インデックス作成:**
```sql
-- 法令インデックス
CREATE INDEX idx_law_name ON laws(law_name);
CREATE INDEX idx_law_type ON laws(law_type);

-- 判例インデックス
CREATE INDEX idx_case_name ON cases(case_name);
CREATE INDEX idx_case_court ON cases(court_name);

-- ベクトルインデックス (Phase 3)
CREATE INDEX ON embeddings USING ivfflat (vector vector_cosine_ops);
```

**接続プール:**
```python
# app/core/database.py
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### キャッシュ運用

**階層的キャッシュ:**
1. **L1:** アプリケーションメモリキャッシュ
2. **L2:** Redis分散キャッシュ
3. **L3:** PostgreSQLクエリキャッシュ

---

## 🛠️ トラブルシューティング

### よくある問題と解決

**1. ポート衝突 (Address already in use)**
```bash
# 使用中のポートを確認
sudo lsof -i :8000

# .envで変更
API_PORT=8001
```

**2. データベース接続失敗**
```bash
# PostgreSQL ログ確認
podman logs egov-postgres

# 接続テスト
podman exec egov-postgres psql -U egov -d egov_db -c "SELECT 1"
```

**3. Redis メモリ不足**
```bash
# メモリ使用量確認
podman exec egov-redis redis-cli INFO memory

# キャッシュクリア
podman exec egov-redis redis-cli FLUSHALL
```

---

## 📝 関連ドキュメント

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - デプロイメント詳細ガイド
- [networks.md](networks.md) - ネットワーク詳細設定
- [README.md](../../README.md) - プロジェクト概要

---

## ✅ チェックリスト

### システム構築確認

- [ ] Docker/Podmanネットワーク作成
- [ ] 環境変数ファイル設定
- [ ] localhost でアクセス確認
- [ ] ローカルネットワークからアクセス確認 (必要な場合)
- [ ] VPN/Tailscale からアクセス確認 (必要な場合)

### 本番環境準備

- [ ] ファイアウォール設定
- [ ] SSL/TLS証明書設定
- [ ] リバースプロキシ設定
- [ ] DNS設定
- [ ] バックアップ設定
- [ ] セキュリティ監査
- [ ] 負荷テスト実施
- [ ] DDoS対策検討
- [ ] 侵入検知システム構築

---

**更新履歴:**
- 2025-11-15: 初版作成
