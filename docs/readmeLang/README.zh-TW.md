<div align="center">

# 📚 e-gov API FastAPI

**提供日本法令和判例資料的高速API伺服器**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compatible-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Podman](https://img.shields.io/badge/Podman-Compatible-892CA0?style=for-the-badge&logo=podman&logoColor=white)](https://podman.io/)
[![uv](https://img.shields.io/badge/uv-Package_Manager-FF6B35?style=for-the-badge)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[🇯🇵 日本語](../../README.md) | [🇬🇧 English](README.en.md) | [🇨🇳 简体中文](README.zh-CN.md) | [🇹🇼 繁體中文](README.zh-TW.md) | [🇷🇺 Русский](README.ru.md) | [🇮🇷 فارسی](README.fa.md) | [🇸🇦 العربية](README.ar.md)

</div>

---

## 📸 螢幕截圖

<div align="center">

### API 文件 (Swagger UI)

![API Documentation](../pics/api-docs.png)

*FastAPI自動產生的API文件*

---

### 法令搜尋回應範例

![Law Search Response](../pics/law-search.png)

*關鍵字「言論自由」的搜尋結果*

---

### 判例搜尋回應範例

![Case Search Response](../pics/case-search.png)

*關鍵字「言論不自由展關西」的判例搜尋結果*

</div>

---

## 📖 簡介

**e-gov API FastAPI** 是一個提供日本法令和判例資料高速存取的RESTful API伺服器。

它與[e-gov法令API](https://elaws.e-gov.go.jp/)和[法院網站](https://www.courts.go.jp/)整合，即時提供最新的法律資訊。

**主要功能:**
- 🔍 法令搜尋、詳細檢索和修訂歷史
- ⚖️ 判例搜尋和詳細檢索
- 📊 法令與判例關係分析
- 🚀 透過Redis快取實現高速化
- 🌐 支援VPN/Tailscale

---

## 🎯 為什麼需要 + 它做什麼

### 問題

存取日本法律資訊時存在以下問題：

- **法令資料分散**: 政府API難以使用，文件不足
- **判例資料獲取困難**: 不存在系統化的API
- **資料整合複雜**: 沒有分析法令與判例關係的機制

### 解決方案

該API伺服器整合多個資料來源，使開發者能夠輕鬆存取日本法律資訊。

**它做什麼:**
- 統一存取法令資料庫
- 搜尋和獲取判例資料
- 分析法令與判例的關係
- 快速回應（快取功能）

**用例:**
- 法律諮詢應用程式的後端
- LegalTech產品的基礎API
- 法律資料分析和研究
- 法令修訂自動追蹤系統

---

## 🚀 安裝

### 必要環境

- Python 3.12+
- Docker 或 Podman
- uv (套件管理器)

### 方法1: 使用Docker/Podman啟動（推薦）

```bash
# 克隆儲存庫
git clone https://github.com/clearclown/e-gov-api-fastAPI.git
cd e-gov-api-fastapi

# 設定環境變數
cp .env.example .env

# 啟動
podman compose up -d
# 或
docker compose up -d

# 確認運行
curl http://localhost:8000/health
```

### 方法2: 使用uv設定開發環境

```bash
# 安裝uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 建立虛擬環境
uv venv

# 啟動虛擬環境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安裝相依性
uv pip install -e .

# 啟動開發伺服器
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 存取

- **API 文件**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康檢查**: http://localhost:8000/health

---

## 🗑️ 解除安裝

### Docker/Podman 環境

```bash
# 停止並刪除服務
podman compose down

# 包括卷的完全刪除
podman compose down -v

# 刪除映像
podman rmi e-gov-api-fastapi-app
```

### uv 環境

```bash
# 刪除虛擬環境
rm -rf .venv

# 清除快取
uv cache clean
```

---

## 📚 文件

### 核心技術

| 類別 | 技術 |
|---------|---------|
| **框架** | FastAPI |
| **語言** | Python 3.12+ |
| **資料庫** | PostgreSQL 16 + pgvector |
| **快取** | Redis 7 |
| **套件管理器** | uv |
| **容器** | Docker / Podman |
| **外部API** | e-gov法令API, 法院 |

### 架構

```
┌─────────────┐
│   客戶端    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│   FastAPI 應用程式          │
│  ┌──────────────────────┐  │
│  │  法令端點            │  │
│  │  判例端點            │  │
│  │  分析端點            │  │
│  └──────────────────────┘  │
└──┬───────────┬──────────┬───┘
   │           │          │
   ▼           ▼          ▼
┌──────┐  ┌────────┐  ┌─────────┐
│Redis │  │Postgres│  │e-gov API│
│快取  │  │資料庫  │  │法院DB   │
└──────┘  └────────┘  └─────────┘
```

**資料流:**
1. 客戶端傳送API請求
2. FastAPI處理請求
3. 檢查Redis快取（命中時立即回應）
4. 快取未命中時從外部API獲取資料(e-gov/法院)
5. 將獲取的資料儲存到PostgreSQL
6. 傳回回應並快取到Redis

### 基礎架構

**檔案結構:**
```
e-gov-api-fastapi/
├── app/                    # 應用程式程式碼
│   ├── api/               # API端點
│   ├── core/              # 核心設定和DB連線
│   ├── services/          # 業務邏輯
│   └── main.py            # 進入點
├── infra/
│   └── podmanOrDocker/    # Docker/Podman設定
│       ├── Dockerfile     # 完整版（含AI功能）
│       └── Dockerfile.lite # 輕量版（僅API功能）
├── docs/                   # 文件
│   ├── pics/              # 螢幕截圖
│   └── readmeLang/        # 多語言README
├── scripts/               # 實用腳本
├── docker-compose.yml     # 主Compose設定
├── pyproject.toml         # 專案設定
└── .env                   # 環境變數
```

**資源使用:**

輕量版（預設）:
- API伺服器: ~600MB
- PostgreSQL: ~500MB
- Redis: ~50MB
- **合計:** ~1.2GB

完整版（含AI功能）:
- API伺服器: ~3-4GB (PyTorch + CUDA)
- PostgreSQL: ~500MB
- Redis: ~50MB
- **合計:** ~4-5GB

### 網路

**存取方法:**

所有服務在 `0.0.0.0` 上監聽，可透過以下方式存取：

1. **本機主機**: `http://localhost:8000`
2. **本機網路**: `http://[主機IP]:8000`
3. **Tailscale/VPN**: `http://[TailscaleIP]:8000`

**連接埠設定（可在.env中變更）:**
- API伺服器: `8000`
- PostgreSQL: `5432`
- Redis: `6379`

**VPN/Tailscale支援:**

0.0.0.0繫結支援遠端存取。

### 路線圖

**階段1和2: 基本功能** ✅ **已完成**
- [x] e-gov API客戶端實作
- [x] 法令搜尋和詳細檢索端點
- [x] 判例擷取和搜尋功能
- [x] Redis快取實作
- [x] PostgreSQL資料庫整合
- [x] 完整Docker/Podman支援

**階段3: AI整合** 🔄 **計劃中**
- [ ] AgenticRAG用於語意搜尋
- [ ] 向量搜尋（使用pgvector）
- [ ] Claude API整合
- [ ] 自然語言問答
- [ ] MCP伺服器實作

**階段4: 進階分析** 🔄 **計劃中**
- [ ] 法令-判例關係圖視覺化
- [ ] 判例引用網路分析
- [ ] 自動摘要產生
- [ ] 聊天式法律諮詢介面

---

## 🤝 貢獻

歡迎為專案做貢獻！

**錯誤報告和功能請求:**

請在[GitHub Issues](https://github.com/clearclown/e-gov-api-fastAPI/issues)報告。

**拉取請求:**

1. Fork此儲存庫
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立拉取請求

**開發指南:**
- 程式碼風格: 遵循PEP 8
- 提交訊息: Conventional Commits格式
- 測試: 新功能必須新增測試

---

## 📚 資源

### 官方文件
- [FastAPI](https://fastapi.tiangolo.com/)
- [e-gov法令API規範](https://elaws.e-gov.go.jp/apitop/)
- [uv - Python套件管理器](https://github.com/astral-sh/uv)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)

### 相關專案
- [pgvector](https://github.com/pgvector/pgvector) - PostgreSQL向量搜尋擴充
- [Claude API](https://docs.anthropic.com/) - Anthropic Claude AI

### 資料來源
- [e-gov法令資料庫](https://elaws.e-gov.go.jp/)
- [法院網站](https://www.courts.go.jp/)

---

## ⚖️ 法律

本專案採用雙重授權條款提供：

### MIT授權條款
適合個人和商業用途

參見 [LICENSE-MIT](../../LICENSE-MIT)

### Apache授權條款2.0
適合企業使用和專利保護

參見 [LICENSE-APACHE](../../LICENSE-APACHE)

**您可以選擇適合您需求的任一授權條款。**

---

<div align="center">

**⭐ 如果這個專案對您有幫助，請給個星！**

用 ❤️ 製作 by [clearclown](https://github.com/clearclown)

📧 聯絡: clearclown@gmail.com

</div>
