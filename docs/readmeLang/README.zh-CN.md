<div align="center">

# 📚 e-gov API FastAPI

**提供日本法令和判例数据的高速API服务器**

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

## 📸 截图

<div align="center">

### API 文档 (Swagger UI)

![API Documentation](../pics/api-docs.png)

*FastAPI自动生成的API文档*

---

### 法令搜索响应示例

![Law Search Response](../pics/law-search.png)

*关键词"言论自由"的搜索结果*

---

### 判例搜索响应示例

![Case Search Response](../pics/case-search.png)

*关键词"言论不自由展关西"的判例搜索结果*

</div>

---

## 📖 简介

**e-gov API FastAPI** 是一个提供日本法令和判例数据高速访问的RESTful API服务器。

它与[e-gov法令API](https://elaws.e-gov.go.jp/)和[法院网站](https://www.courts.go.jp/)集成，实时提供最新的法律信息。

**主要功能:**
- 🔍 法令搜索、详细检索和修订历史
- ⚖️ 判例搜索和详细检索
- 📊 法令与判例关系分析
- 🚀 通过Redis缓存实现高速化
- 🌐 支持VPN/Tailscale

---

## 🎯 为什么需要 + 它做什么

### 问题

访问日本法律信息时存在以下问题：

- **法令数据分散**: 政府API难以使用，文档不足
- **判例数据获取困难**: 不存在系统化的API
- **数据集成复杂**: 没有分析法令与判例关系的机制

### 解决方案

该API服务器整合多个数据源，使开发者能够轻松访问日本法律信息。

**它做什么:**
- 统一访问法令数据库
- 搜索和获取判例数据
- 分析法令与判例的关系
- 快速响应（缓存功能）

**用例:**
- 法律咨询应用的后端
- LegalTech产品的基础API
- 法律数据分析和研究
- 法令修订自动跟踪系统

---

## 🚀 安装

### 必要环境

- Python 3.12+
- Docker 或 Podman
- uv (包管理器)

### 方法1: 使用Docker/Podman启动（推荐）

```bash
# 克隆仓库
git clone https://github.com/clearclown/e-gov-api-fastAPI.git
cd e-gov-api-fastapi

# 配置环境变量
cp .env.example .env

# 启动
podman compose up -d
# 或
docker compose up -d

# 确认运行
curl http://localhost:8000/health
```

### 方法2: 使用uv设置开发环境

```bash
# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装依赖
uv pip install -e .

# 启动开发服务器
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 访问

- **API 文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

---

## 🗑️ 卸载

### Docker/Podman 环境

```bash
# 停止并删除服务
podman compose down

# 包括卷的完全删除
podman compose down -v

# 删除镜像
podman rmi e-gov-api-fastapi-app
```

### uv 环境

```bash
# 删除虚拟环境
rm -rf .venv

# 清除缓存
uv cache clean
```

---

## 📚 文档

### 核心技术

| 类别 | 技术 |
|---------|---------|
| **框架** | FastAPI |
| **语言** | Python 3.12+ |
| **数据库** | PostgreSQL 16 + pgvector |
| **缓存** | Redis 7 |
| **包管理器** | uv |
| **容器** | Docker / Podman |
| **外部API** | e-gov法令API, 法院 |

### 架构

```
┌─────────────┐
│   客户端    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│   FastAPI 应用程序          │
│  ┌──────────────────────┐  │
│  │  法令端点            │  │
│  │  判例端点            │  │
│  │  分析端点            │  │
│  └──────────────────────┘  │
└──┬───────────┬──────────┬───┘
   │           │          │
   ▼           ▼          ▼
┌──────┐  ┌────────┐  ┌─────────┐
│Redis │  │Postgres│  │e-gov API│
│缓存  │  │数据库  │  │法院DB   │
└──────┘  └────────┘  └─────────┘
```

**数据流:**
1. 客户端发送API请求
2. FastAPI处理请求
3. 检查Redis缓存（命中时立即响应）
4. 缓存未命中时从外部API获取数据(e-gov/法院)
5. 将获取的数据保存到PostgreSQL
6. 返回响应并缓存到Redis

### 基础设施

**文件结构:**
```
e-gov-api-fastapi/
├── app/                    # 应用程序代码
│   ├── api/               # API端点
│   ├── core/              # 核心配置和DB连接
│   ├── services/          # 业务逻辑
│   └── main.py            # 入口点
├── infra/
│   └── podmanOrDocker/    # Docker/Podman配置
│       ├── Dockerfile     # 完整版（含AI功能）
│       └── Dockerfile.lite # 轻量版（仅API功能）
├── docs/                   # 文档
│   ├── pics/              # 截图
│   └── readmeLang/        # 多语言README
├── scripts/               # 实用脚本
├── docker-compose.yml     # 主Compose配置
├── pyproject.toml         # 项目配置
└── .env                   # 环境变量
```

**资源使用:**

轻量版（默认）:
- API服务器: ~600MB
- PostgreSQL: ~500MB
- Redis: ~50MB
- **合计:** ~1.2GB

完整版（含AI功能）:
- API服务器: ~3-4GB (PyTorch + CUDA)
- PostgreSQL: ~500MB
- Redis: ~50MB
- **合计:** ~4-5GB

### 网络

**访问方法:**

所有服务在 `0.0.0.0` 上监听，可通过以下方式访问：

1. **本地主机**: `http://localhost:8000`
2. **本地网络**: `http://[主机IP]:8000`
3. **Tailscale/VPN**: `http://[TailscaleIP]:8000`

**端口配置（可在.env中更改）:**
- API服务器: `8000`
- PostgreSQL: `5432`
- Redis: `6379`

**VPN/Tailscale支持:**

0.0.0.0绑定支持远程访问。

### 路线图

**阶段1和2: 基本功能** ✅ **已完成**
- [x] e-gov API客户端实现
- [x] 法令搜索和详细检索端点
- [x] 判例抓取和搜索功能
- [x] Redis缓存实现
- [x] PostgreSQL数据库集成
- [x] 完整Docker/Podman支持

**阶段3: AI集成** 🔄 **计划中**
- [ ] AgenticRAG用于语义搜索
- [ ] 向量搜索（使用pgvector）
- [ ] Claude API集成
- [ ] 自然语言问答
- [ ] MCP服务器实现

**阶段4: 高级分析** 🔄 **计划中**
- [ ] 法令-判例关系图可视化
- [ ] 判例引用网络分析
- [ ] 自动摘要生成
- [ ] 聊天式法律咨询界面

---

## 🤝 贡献

欢迎为项目做贡献！

**错误报告和功能请求:**

请在[GitHub Issues](https://github.com/clearclown/e-gov-api-fastAPI/issues)报告。

**拉取请求:**

1. Fork此仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建拉取请求

**开发指南:**
- 代码风格: 遵循PEP 8
- 提交消息: Conventional Commits格式
- 测试: 新功能必须添加测试

---

## 📚 资源

### 官方文档
- [FastAPI](https://fastapi.tiangolo.com/)
- [e-gov法令API规范](https://elaws.e-gov.go.jp/apitop/)
- [uv - Python包管理器](https://github.com/astral-sh/uv)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)

### 相关项目
- [pgvector](https://github.com/pgvector/pgvector) - PostgreSQL向量搜索扩展
- [Claude API](https://docs.anthropic.com/) - Anthropic Claude AI

### 数据源
- [e-gov法令数据库](https://elaws.e-gov.go.jp/)
- [法院网站](https://www.courts.go.jp/)

---

## ⚖️ 法律

本项目采用双重许可证提供：

### MIT许可证
适合个人和商业用途

参见 [LICENSE-MIT](../../LICENSE-MIT)

### Apache许可证2.0
适合企业使用和专利保护

参见 [LICENSE-APACHE](../../LICENSE-APACHE)

**您可以选择适合您需求的任一许可证。**

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给个星！**

用 ❤️ 制作 by [clearclown](https://github.com/clearclown)

📧 联系: clearclown@gmail.com

</div>
