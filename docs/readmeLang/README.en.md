<div align="center">

# 📚 e-gov API FastAPI

**High-Speed API Server Providing Japanese Law and Case Precedent Data**

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

## 📸 Screenshots

<div align="center">

### API Documentation (Swagger UI)

![API Documentation](../pics/api-docs.png)

*Auto-generated API documentation by FastAPI*

---

### Law Search Response Example

![Law Search Response](../pics/law-search.png)

*Search results for keyword "freedom of expression"*

---

### Case Precedent Search Response Example

![Case Search Response](../pics/case-search.png)

*Case search results for keyword "Unfreedom of Expression Exhibition Kansai"*

</div>

---

## 📖 Overview

**e-gov API FastAPI** is a RESTful API server that provides high-speed access to Japanese law and case precedent data.

It integrates with the [e-gov Law API](https://elaws.e-gov.go.jp/) and [Courts Website](https://www.courts.go.jp/) to provide real-time access to the latest legal information.

**Key Features:**
- 🔍 Law search, detailed retrieval, and amendment history
- ⚖️ Case precedent search and detailed retrieval
- 📊 Relationship analysis between laws and cases
- 🚀 High-speed performance with Redis caching
- 🌐 VPN/Tailscale support

---

## 🎯 Why This is Needed + What It Does

### The Problem

When accessing Japanese legal information, there are several challenges:

- **Scattered Legal Data**: Government APIs are difficult to use with insufficient documentation
- **Difficult Case Data Retrieval**: No systematic API exists
- **Complex Data Integration**: No mechanism to analyze relationships between laws and cases

### The Solution

This API server integrates multiple data sources, making it easy for developers to access Japanese legal information.

**What It Does:**
- Unified access to legal databases
- Search and retrieval of case precedent data
- Analysis of relationships between laws and cases
- Fast response times (caching functionality)

**Use Cases:**
- Backend for legal consultation applications
- Foundation API for LegalTech products
- Legal data analysis and research
- Automatic law amendment tracking systems

---

## 🚀 Installation

### Prerequisites

- Python 3.12+
- Docker or Podman
- uv (package manager)

### Method 1: Start with Docker/Podman (Recommended)

```bash
# Clone the repository
git clone https://github.com/clearclown/e-gov-api-fastAPI.git
cd e-gov-api-fastapi

# Configure environment variables
cp .env.example .env

# Start the services
podman compose up -d
# or
docker compose up -d

# Verify operation
curl http://localhost:8000/health
```

### Method 2: Setup Development Environment with uv

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e .

# Start development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access Points

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🗑️ Uninstall

### Docker/Podman Environment

```bash
# Stop and remove services
podman compose down

# Complete removal including volumes
podman compose down -v

# Remove images
podman rmi e-gov-api-fastapi-app
```

### uv Environment

```bash
# Remove virtual environment
rm -rf .venv

# Clear cache
uv cache clean
```

---

## 📚 Documentation

### Core Technologies

| Category | Technology |
|---------|---------|
| **Framework** | FastAPI |
| **Language** | Python 3.12+ |
| **Database** | PostgreSQL 16 + pgvector |
| **Cache** | Redis 7 |
| **Package Manager** | uv |
| **Container** | Docker / Podman |
| **External APIs** | e-gov Law API, Courts |

### Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│   FastAPI Application       │
│  ┌──────────────────────┐  │
│  │  Law Endpoints       │  │
│  │  Case Endpoints      │  │
│  │  Analysis Endpoints  │  │
│  └──────────────────────┘  │
└──┬───────────┬──────────┬───┘
   │           │          │
   ▼           ▼          ▼
┌──────┐  ┌────────┐  ┌─────────┐
│Redis │  │Postgres│  │e-gov API│
│Cache │  │Database│  │Courts DB│
└──────┘  └────────┘  └─────────┘
```

**Data Flow:**
1. Client sends API request
2. FastAPI processes the request
3. Check Redis cache (immediate response on hit)
4. On cache miss, fetch data from external APIs (e-gov/Courts)
5. Save retrieved data to PostgreSQL
6. Return response and cache in Redis

### Infrastructure

**File Structure:**
```
e-gov-api-fastapi/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   ├── core/              # Core settings & DB connection
│   ├── services/          # Business logic
│   └── main.py            # Entry point
├── infra/
│   └── podmanOrDocker/    # Docker/Podman configuration
│       ├── Dockerfile     # Full version (with AI features)
│       └── Dockerfile.lite # Lite version (API features only)
├── docs/                   # Documentation
│   ├── pics/              # Screenshots
│   └── readmeLang/        # Multi-language README
├── scripts/               # Utility scripts
├── docker-compose.yml     # Main Compose configuration
├── pyproject.toml         # Project configuration
└── .env                   # Environment variables
```

**Resource Usage:**

Lite Version (Default):
- API Server: ~600MB
- PostgreSQL: ~500MB
- Redis: ~50MB
- **Total:** ~1.2GB

Full Version (with AI features):
- API Server: ~3-4GB (PyTorch + CUDA)
- PostgreSQL: ~500MB
- Redis: ~50MB
- **Total:** ~4-5GB

### Network

**Access Methods:**

All services listen on `0.0.0.0` and can be accessed via:

1. **Localhost**: `http://localhost:8000`
2. **Local Network**: `http://[HostIP]:8000`
3. **Tailscale/VPN**: `http://[TailscaleIP]:8000`

**Port Configuration (configurable in .env):**
- API Server: `8000`
- PostgreSQL: `5432`
- Redis: `6379`

**VPN/Tailscale Support:**

0.0.0.0 binding enables remote access.

### Roadmap

**Phase 1 & 2: Basic Features** ✅ **Completed**
- [x] e-gov API client implementation
- [x] Law search and detail retrieval endpoints
- [x] Case scraping and search functionality
- [x] Redis cache implementation
- [x] PostgreSQL database integration
- [x] Full Docker/Podman support

**Phase 3: AI Integration** 🔄 **Planned**
- [ ] AgenticRAG for semantic search
- [ ] Vector search (using pgvector)
- [ ] Claude API integration
- [ ] Natural language Q&A
- [ ] MCP server implementation

**Phase 4: Advanced Analytics** 🔄 **Planned**
- [ ] Law-case relationship graph visualization
- [ ] Case citation network analysis
- [ ] Automatic summary generation
- [ ] Chat-based legal consultation interface

---

## 🤝 Contributing

Contributions to the project are welcome!

**Bug Reports & Feature Requests:**

Please report at [GitHub Issues](https://github.com/clearclown/e-gov-api-fastAPI/issues).

**Pull Requests:**

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

**Development Guidelines:**
- Code Style: Follow PEP 8
- Commit Messages: Conventional Commits format
- Testing: Always add tests for new features

---

## 📚 Resources

### Official Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [e-gov Law API Specification](https://elaws.e-gov.go.jp/apitop/)
- [uv - Python Package Manager](https://github.com/astral-sh/uv)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)

### Related Projects
- [pgvector](https://github.com/pgvector/pgvector) - PostgreSQL vector search extension
- [Claude API](https://docs.anthropic.com/) - Anthropic Claude AI

### Data Sources
- [e-gov Legal Database](https://elaws.e-gov.go.jp/)
- [Courts Website](https://www.courts.go.jp/)

---

## ⚖️ Legal

This project is provided under a dual license:

### MIT License
Ideal for personal and commercial use

See [LICENSE-MIT](../../LICENSE-MIT)

### Apache License 2.0
For enterprise use and patent protection

See [LICENSE-APACHE](../../LICENSE-APACHE)

**You may choose whichever license suits your needs.**

---

<div align="center">

**⭐ If this project is helpful, please give it a star!**

Made with ❤️ by [clearclown](https://github.com/clearclown)

📧 Contact: clearclown@gmail.com

</div>
