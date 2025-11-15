# ネットワーク構成ドキュメント

**最終更新日:** 2025-11-15
**対象:** e-gov API FastAPI プロジェクト

---

## 🌐 ネットワークアーキテクチャ概要のため

### 全体図

```
┌──────────────────────────────────────────────────────────┐
│                      インターネット                        │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                   ファイアウォール                          │
│          (UFW / firewalld / iptables)                      │
└────────┬───────────────────┬────────────────────────────┘
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
             │             │
        ┌────┴───┐   ┌────┴────┐   ┌────────┐
   ┌─────────┐   ┌──────────┐   ┌────────┐
   │  app   │   │postgres │   │ redis  │
   │ :8000  │   │ :5432   │   │ :6379  │
   └─────────┘   └──────────┘   └────────┘
```

---

## 🔌 ポート設定

### コンポーネントポート

| サービス | コンテナポート | ホストポート | プロトコル | 用途 |
|---------|--------------|-------------|-----------|------|
| FastAPI | 8000 | ${API_PORT:-8000} | HTTP | API エンドポイント |
| PostgreSQL | 5432 | ${POSTGRES_PORT:-5432} | TCP | データベース |
| Redis | 6379 | ${REDIS_PORT:-6379} | TCP | キャッシュ |

### 0.0.0.0 バインディング設定

**docker-compose.yml:**
```yaml
services:
  app:
    ports:
      - "0.0.0.0:${API_PORT:-8000}:8000"

  postgres:
    ports:
      - "0.0.0.0:${POSTGRES_PORT:-5432}:5432"

  redis:
    ports:
      - "0.0.0.0:${REDIS_PORT:-6379}:6379"
```

**メリット:**
- すべてのネットワークインターフェースから接続可能
- ローカルホスト、ローカルネットワーク、VPNから柔軟にアクセス

**デメリット/注意点:**
- ファイアウォール必須設定が必要
- 本番環境では `127.0.0.1` に変更を検討

---

## 🔐 VPN/Tailscale 設定

### Tailscale とは

**Tailscaleの特徴:**
- メッシュ型VPNネットワーク
- WireGuardベース
- NAT越えが容易

**設定手順:**

1. **Tailscaleのインストール (ホストOS)**
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://tailscale.com/install.sh | sh

   # 起動
   sudo tailscale up
   ```

2. **Tailscale IPアドレス確認**
   ```bash
   tailscale ip -4
   # 例: 100.82.83.122
   ```

3. **接続テスト**
   ```bash
   # 別端末から接続
   curl http://100.82.83.122:8000/health
   ```

**Tailscale ACL設定 (共有時の制御):**
```json
{
  "acls": [
    {
      "action": "accept",
      "users": ["*"],
      "ports": [
        "tag:api-server:8000"
      ]
    }
  ],
  "tagOwners": {
    "tag:api-server": ["your-email@example.com"]
  }
}
```

---

## 🌉 Docker/Podman ネットワーク

### ネットワーク設定

**docker-compose.yml:**
```yaml
networks:
  egov-network:
    driver: bridge
```

**特性:**
- **分離された環境**: コンテナ間は独立したネットワーク
- **自動DNS**: コンテナ名でお互いを解決
- **セキュリティ**: 外部ネットワークから隔離

### コンテナ間接続

**接続文字列:**

1. **FastAPI → PostgreSQL**
   ```
   postgresql://egov:egov_password@postgres:5432/egov_db
   ```
   - ホスト名: `postgres` (コンテナ名)
   - コンテナ間はコンテナDNS解決

2. **FastAPI → Redis**
   ```
   redis://redis:6379/0
   ```
   - ホスト名: `redis` (コンテナ名)

**コンテナ間IP確認:**
```bash
# ネットワーク詳細確認
podman network inspect egov-network

# コンテナのIP確認
podman inspect egov-api | grep IPAddress
```

---

## 🔒 ファイアウォール設定

### UFW (Ubuntu/Debian)

**基本設定:**
```bash
# UFW有効化
sudo ufw enable

# デフォルトルール
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH接続許可 (重要！締め出されないように)
sudo ufw allow ssh

# Tailscale許可 (サブネット全体)
sudo ufw allow from 100.64.0.0/10

# ローカルネットワーク許可 (必要に応じて)
sudo ufw allow from 192.168.0.0/16 to any port 8000
sudo ufw allow from 192.168.0.0/16 to any port 5432
sudo ufw allow from 192.168.0.0/16 to any port 6379

# 確認
sudo ufw status verbose
```

**特定IPのみ許可:**
```bash
# 特定のTailscale IPのみ
sudo ufw allow from 100.82.83.122 to any port 8000

# 複数IP
sudo ufw allow from 100.82.83.122 to any port 8000
sudo ufw allow from 100.82.83.123 to any port 8000
```

### firewalld (RHEL/CentOS/Fedora)

**基本設定:**
```bash
# firewalld起動
sudo systemctl start firewalld
sudo systemctl enable firewalld

# Tailscale用ゾーン作成
sudo firewall-cmd --permanent --new-zone=tailscale
sudo firewall-cmd --permanent --zone=tailscale \
  --add-source=100.64.0.0/10

# ポート許可
sudo firewall-cmd --permanent --zone=tailscale \
  --add-port=8000/tcp
sudo firewall-cmd --permanent --zone=tailscale \
  --add-port=5432/tcp
sudo firewall-cmd --permanent --zone=tailscale \
  --add-port=6379/tcp

# 反映
sudo firewall-cmd --reload

# 確認
sudo firewall-cmd --list-all --zone=tailscale
```

---

## 🔍 DNS設定

### コンテナDNS (自動解決)

**Docker/Podman のコンテナDNS:**
- コンテナ名が自動的にDNS名として使用可能
- 例: `postgres`, `redis`, `app`

**接続例:**
```bash
# コンテナ内でDNS解決をテスト
podman exec egov-api nslookup postgres
podman exec egov-api nslookup redis
```

### 外部DNS (カスタムドメイン)

**/etc/hosts 設定 (ホスト側):**
```bash
# ローカル開発用 /etc/hosts
127.0.0.1       api.egov.local
192.168.0.13    api.egov.local  # ローカルネットワーク
100.82.83.122   api.egov.local  # Tailscale
```

**接続例:**
```bash
curl http://api.egov.local:8000/health
```

---

## 🔄 リバースプロキシ設定

### Nginx設定

**nginx.conf:**
```nginx
upstream egov_api {
    server 127.0.0.1:8000;
    # または Tailscale IP
    # server 100.82.83.122:8000;
}

server {
    listen 80;
    server_name api.egov.local;

    # HTTPS リダイレクト (本番環境)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://egov_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTPS設定 (本番環境)
server {
    listen 443 ssl http2;
    server_name api.egov.local;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://egov_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Caddy設定

**Caddyfile:**
```
api.egov.local {
    reverse_proxy localhost:8000

    # または Tailscale IP
    # reverse_proxy 100.82.83.122:8000
}

# 自動HTTPS (Let's Encrypt)
api.example.com {
    reverse_proxy localhost:8000
}
```

---

## 📊 ネットワーク監視

### 接続確認

**基本コマンド確認:**
```bash
# すべてのリッスンポート確認
sudo netstat -tulpn

# 特定ポート
sudo lsof -i :8000
sudo lsof -i :5432
sudo lsof -i :6379
```

### トラフィック監視

**iftop使用:**
```bash
# インストール
sudo apt install iftop  # Debian/Ubuntu
sudo dnf install iftop  # RHEL/Fedora

# 実行
sudo iftop -i eth0
```

**tcpdump使用:**
```bash
# APIトラフィックのキャプチャ
sudo tcpdump -i any port 8000 -n

# PostgreSQLトラフィック
sudo tcpdump -i any port 5432 -n
```

---

## 🛠️ トラブルシューティング

### 接続できない場合の確認手順

1. **サービスが起動しているか確認**
   ```bash
   sudo netstat -tulpn | grep 8000
   ```

2. **ファイアウォール設定確認**
   ```bash
   sudo ufw status
   # または
   sudo firewall-cmd --list-all
   ```

3. **Docker ネットワーク確認**
   ```bash
   podman network ls
   podman network inspect egov-network
   ```

4. **ログ確認**
   ```bash
   podman logs egov-api
   ```

5. **ローカル接続テスト**
   ```bash
   curl http://localhost:8000/health
   curl http://127.0.0.1:8000/health
   curl http://$(hostname -I | awk '{print $1}'):8000/health
   ```

6. **コンテナ内からの接続テスト**
   ```bash
   podman exec egov-api curl http://localhost:8000/health
   podman exec egov-api curl http://postgres:5432
   podman exec egov-api curl http://redis:6379
   ```

### よくあるエラー

**1. ポート競合 (Address already in use)**
```
Error: bind: address already in use
```
**解決方法:**
```bash
# 使用中のポート確認
sudo lsof -i :8000

# ポート変更 (.env)
API_PORT=8001
```

**2. ファイアウォールブロック**
```
curl: (7) Failed to connect to X.X.X.X port 8000: No route to host
```
**解決方法:**
```bash
# UFW
sudo ufw allow 8000

# firewalld
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload
```

**3. DNS解決失敗 (コンテナ内)**
```
could not translate host name "postgres" to address
```
**解決方法:**
```bash
# ネットワーク再作成
podman compose down
podman compose up -d
```

---

## 🔐 セキュリティベストプラクティス

### ネットワークセキュリティ

1. **最小権限の原則**
   - 必要なポートのみ開放
   - 信頼できるIPのみ許可

2. **SSL/TLS使用**
   - 本番環境では必須
   - Let's Encrypt使用で無料化

3. **ファイアウォール設定**
   - デフォルトDENY
   - 必要な接続のみALLOW

4. **VPN使用**
   - Tailscaleなどで安全なリモート接続
   - 暗号化された通信を確保

5. **ネットワーク分離**
   - Dockerネットワークで環境を分離
   - 必要最小限のポートマッピング

---

## 📝 関連ドキュメント

- [infra.md](infra.md) - インフラ構成概要
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - デプロイメント手順
- [README.md](../../README.md) - プロジェクト概要

---

## ✅ ネットワーク設定チェックリスト

### 開発環境

- [ ] Dockerネットワーク作成確認
- [ ] 環境変数設定確認
- [ ] localhost アクセス確認
- [ ] ローカルネットワークからアクセス確認 (必要な場合)
- [ ] VPN/Tailscale からアクセス確認 (必要な場合)

### 本番環境

- [ ] ファイアウォール設定
- [ ] SSL/TLS証明書設定
- [ ] リバースプロキシ設定
- [ ] DNS設定
- [ ] バックアップ設定
- [ ] セキュリティ監査
- [ ] 負荷テスト実施
- [ ] DDoS対策実施
- [ ] 侵入検知システム構築

---

**更新履歴:**
- 2025-11-15: 初版作成
