# GitHub リポジトリ設定ガイド

## 📝 リポジトリ設定

### 1. About セクション（リポジトリページ右上）

**Description（説明）:**
```
High-speed RESTful API server providing Japanese law and court case data with Redis caching, PostgreSQL storage, and optional AI features
```

日本語版：
```
日本の法令・判例データを提供する高速APIサーバー（Redis キャッシュ、PostgreSQL、AI 機能オプション）
```

**Website:**
```
https://clearclown.github.io/e-gov-api-fastAPI
```
（GitHub Pagesを有効化する場合）

### 2. Topics（タグ）

以下のトピックを追加（Settings → General → Topics）:

**主要技術:**
- `fastapi`
- `python`
- `postgresql`
- `redis`
- `docker`
- `podman`
- `uvicorn`

**用途・分野:**
- `legal-tech`
- `japanese-law`
- `court-cases`
- `api-server`
- `restful-api`
- `legal-data`
- `e-gov`
- `jurisprudence`

**機能:**
- `caching`
- `database`
- `web-scraping`
- `api-integration`
- `multi-language`

**AI関連（オプション機能）:**
- `vector-search`
- `pgvector`
- `rag`
- `ai-integration`
- `semantic-search`

## 🏷️ リリース・タグ設定

### 現在の推奨タグ

```bash
# 現在のバージョンにタグを付ける
git tag -a v0.2.0 -m "v0.2.0: Documentation Enhancement & Lite Version Support

- Comprehensive documentation in 7 languages
- Lite version with ~600MB memory usage
- AI features as optional dependencies
- Network and infrastructure guides
- Multi-language README support"

git push origin v0.2.0
```

### リリースノート作成

GitHub上で Releases → Create a new release で以下を設定：

**Tag:** `v0.2.0`

**Title:** `📚 v0.2.0 - Documentation Enhancement & Lite Version Support`

**Description:**
```markdown
## 🎉 Major Updates

### 📖 Documentation Enhancements
- **Multi-language Support**: 7 languages (Japanese, English, Chinese Simplified/Traditional, Russian, Persian, Arabic)
- **Comprehensive Guides**:
  - Infrastructure setup (516 lines)
  - Network configuration (522 lines)
  - Screenshots and visual examples
- **Architecture Diagrams**: Complete system and data flow diagrams

### 🪶 Lite Version Support
- **Memory Optimization**: ~600MB (Lite) vs ~3-4GB (Full with AI)
- **Optional AI Features**: `pip install -e ".[ai]"` for AI capabilities
- **Improved Performance**: Faster startup and reduced resource usage

### 🛠️ Infrastructure Improvements
- Default Docker configuration optimized for Lite version
- Enhanced PostgreSQL healthcheck
- Reorganized dependency management

## 📸 Screenshots

- API Documentation (Swagger UI)
- Law Search Example ("表現の自由")
- Court Case Search Example

## 🚀 Installation

**Standard (Lite) Version:**
```bash
git clone https://github.com/clearclown/e-gov-api-fastAPI.git
cd e-gov-api-fastapi
podman compose up -d
```

**With AI Features:**
```bash
uv pip install -e ".[ai]"
```

## 📚 Documentation

- [English README](docs/readmeLang/README.en.md)
- [Infrastructure Guide](docs/DEV/infra.md)
- [Network Configuration](docs/DEV/networks.md)

## 🙏 Contributors

- [@clearclown](https://github.com/clearclown)
- Generated with [Claude Code](https://claude.com/claude-code)

---

**Full Changelog**: https://github.com/clearclown/e-gov-api-fastAPI/compare/v0.1.0...v0.2.0
```

## 📌 GitHub Pages 設定（オプション）

### 有効化手順

1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` / `docs` (または `gh-pages` ブランチ作成)
4. Folder: `/ (root)` または `/docs`

### index.html 作成（docs/ に配置）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>e-gov API FastAPI - 日本の法令・判例データAPI</title>
    <meta http-equiv="refresh" content="0; url=https://github.com/clearclown/e-gov-api-fastAPI#readme">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
        }
        h1 { font-size: 2.5em; margin-bottom: 0.5em; }
        p { font-size: 1.2em; }
        a { color: #fff; text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 e-gov API FastAPI</h1>
        <p>Redirecting to README...</p>
        <p>If not redirected, <a href="https://github.com/clearclown/e-gov-api-fastAPI">click here</a>.</p>
    </div>
</body>
</html>
```

## 🎨 追加バッジ（README.md）

すでに追加済みですが、今後追加できるバッジ：

```markdown
<!-- CI/CD -->
[![CI](https://github.com/clearclown/e-gov-api-fastAPI/workflows/CI/badge.svg)](https://github.com/clearclown/e-gov-api-fastAPI/actions)

<!-- Code Quality -->
[![codecov](https://codecov.io/gh/clearclown/e-gov-api-fastAPI/branch/main/graph/badge.svg)](https://codecov.io/gh/clearclown/e-gov-api-fastAPI)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<!-- Documentation -->
[![Documentation Status](https://readthedocs.org/projects/e-gov-api-fastapi/badge/?version=latest)](https://e-gov-api-fastapi.readthedocs.io/en/latest/?badge=latest)

<!-- Community -->
[![GitHub stars](https://img.shields.io/github/stars/clearclown/e-gov-api-fastAPI?style=social)](https://github.com/clearclown/e-gov-api-fastAPI/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/clearclown/e-gov-api-fastAPI?style=social)](https://github.com/clearclown/e-gov-api-fastAPI/network/members)
```

## 🔍 検索最適化

### .github/FUNDING.yml（スポンサー設定）

```yaml
# Sponsor information
github: [clearclown]
custom: ["https://paypal.me/clearclown"]
```

### .github/CODEOWNERS

```
# Code owners
* @clearclown
/docs/ @clearclown
/app/ @clearclown
```

## 📊 GitHub Insights 設定

### Community Standards チェックリスト

- [x] Description
- [x] README
- [x] License (MIT + Apache 2.0)
- [ ] Code of Conduct (必要に応じて)
- [ ] Contributing guidelines (必要に応じて)
- [ ] Issue templates
- [ ] Pull request template

### Issue Templates 作成例

`.github/ISSUE_TEMPLATE/bug_report.md`:
```yaml
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: clearclown
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1.
2.
3.

**Expected behavior**
What you expected to happen.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Python version: [e.g. 3.12]
 - Installation method: [Docker/uv]

**Additional context**
Add any other context about the problem here.
```

## 🌟 推奨アクション

1. **リポジトリ設定を確認**
   - Settings → General → Features で Issues, Discussions を有効化
   - Wikis も有効化してドキュメント拡充

2. **セキュリティ設定**
   - Settings → Security → Dependabot を有効化
   - Code scanning alerts を有効化

3. **Actions設定**
   - CI/CD ワークフローを追加（テスト自動化）

4. **プロジェクトボード作成**
   - Projects タブで開発ロードマップを可視化

---

これらの設定により、プロジェクトの可視性と使いやすさが大幅に向上します！
