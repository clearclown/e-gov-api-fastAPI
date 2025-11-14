# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based API server for accessing Japanese legal information (laws and court precedents). The project uses `uv` for package management and is designed with future integration of Agentic RAG and Claude Agent SDK in mind.

**Current Status**: Phase 1 - Foundation building (project initialization stage)

## Development Setup

This project uses `uv` as the package manager. Setup commands:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e .
```

## Architecture Overview

### Planned Structure

The project is designed around three main data layers:

1. **Legal Data Layer** (`app/services/egov_client.py`)
   - Integrates with e-gov API (https://elaws.e-gov.go.jp/) for Japanese law data
   - Handles law searches, retrieval, and amendment history

2. **Case Law Layer** (`app/services/case_scraper.py`)
   - Integrates with Courts website (https://www.courts.go.jp/)
   - May use API or web scraping depending on available data sources

3. **AI Integration Layer** (`app/services/rag_service.py`)
   - Agentic RAG for efficient search across legal data
   - Claude Agent SDK integration for custom tools
   - MCP server implementation for tool provision

### API Design

The API will follow RESTful patterns with versioning:

**Laws endpoints**:
- `GET /api/v1/laws/search` - Search laws
- `GET /api/v1/laws/{law_id}` - Get specific law
- `GET /api/v1/laws/{law_id}/history` - Get amendment history

**Cases endpoints**:
- `GET /api/v1/cases/search` - Search court precedents
- `GET /api/v1/cases/{case_id}` - Get specific case

### Claude Agent SDK Integration

The project will expose legal search functionality as MCP tools:

```python
@tool("search_law", "日本の法令を検索", {"query": str})
async def search_law(args):
    # e-gov API を使用した法令検索
    results = await egov_client.search(args["query"])
    return {"content": [{"type": "text", "text": results}]}

@tool("search_case", "判例を検索", {"keywords": str})
async def search_case(args):
    # 判例データベースでの検索
    results = await case_service.search(args["keywords"])
    return {"content": [{"type": "text", "text": results}]}
```

## Key Technical Decisions

- **Package Manager**: uv (for fast, reliable dependency management)
- **API Framework**: FastAPI (for async support and automatic OpenAPI documentation)
- **Python Version**: 3.10+ (required for modern async features)
- **Claude Integration**: Agent SDK with MCP server pattern (not direct API calls)

## Data Sources

1. **e-gov Law API**: Official source for all Japanese laws, real-time updates
2. **Courts Website**: Source for court precedent data
3. **Future considerations**: Commercial case databases, open legal data

## Development Phases

**Phase 1** (Current): Foundation
- FastAPI project initialization
- e-gov API client implementation
- Basic law search endpoints

**Phase 2**: Case law integration
- Data source selection for court precedents
- Scraper/API client implementation
- Case search endpoints

**Phase 3**: AI integration
- Agentic RAG implementation
- Claude Agent SDK integration
- MCP server functionality

**Phase 4**: Advanced features
- Law-case relationship analysis
- Natural language legal consultation
- Automatic legal document summarization

## Important Notes

- All API responses should be in Japanese (法律・判例データは日本語)
- Legal data accuracy is critical - always verify data sources
- Consider data update frequency and caching strategies
- MCP tools should handle both structured queries and natural language
