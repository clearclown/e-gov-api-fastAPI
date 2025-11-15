# Case Law API Implementation Guide

## Overview

This document describes the implementation of the Case Law API (Phase 2) for the e-gov API FastAPI project.

## Implementation Status

✅ **Completed Features:**

1. **Data Models** (`app/models/case.py`)
   - CourtType enum (5 court types)
   - CaseType enum (4 case types)
   - CaseSearchResult model
   - CaseDetail model
   - CaseReference model

2. **Database Layer** (`app/db/`)
   - SQLAlchemy models for cases and references
   - Async session management
   - Database initialization utilities
   - Alembic migrations (including GIN index for full-text search)

3. **Repository Layer** (`app/repositories/case_repository.py`)
   - Case CRUD operations
   - **PostgreSQL Full-Text Search** with GIN index
   - Dual search modes: FTS (default) and ILIKE fallback
   - Law-to-case relationship queries
   - Pagination support

4. **Service Layer** (`app/services/case_scraper.py`)
   - Base scraper service structure
   - HTTP client configuration
   - Rate limiting setup
   - Placeholder implementation (ready for actual scraping logic)

5. **API Endpoints** (`app/api/endpoints/`)
   - `GET /api/v1/cases/search` - Search cases
   - `GET /api/v1/cases/{case_id}` - Get case details
   - `GET /api/v1/laws/{law_id}/cases` - Get cases by law

6. **Batch Processing** (`app/batch/fetch_cases.py`)
   - Scheduled case fetching script
   - Command-line interface
   - Error handling and logging

7. **Testing**
   - Unit tests for scraper service
   - Unit tests for repository (including full-text search tests)
   - Integration tests for API endpoints
   - Test fixtures and configuration

8. **Full-Text Search** (`docs/FULLTEXT_SEARCH.md`)
   - PostgreSQL GIN index implementation
   - `to_tsvector` and `plainto_tsquery` usage
   - Dual search mode support
   - Japanese text search considerations

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac

# Install dependencies
uv pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/egov_db
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb egov_db

# Run migrations (including GIN index for full-text search)
alembic upgrade head
```

**Note:** Migration `002_add_fulltext_search_index.py` creates a GIN index for high-performance full-text search. See `docs/FULLTEXT_SEARCH.md` for details.

### 4. Run the Application

```bash
# Start FastAPI server
uvicorn app.main:app --reload

# Access API documentation
# http://localhost:8000/docs
```

## API Usage Examples

### Search Cases

```bash
# Search all cases
curl "http://localhost:8000/api/v1/cases/search"

# Search with keyword
curl "http://localhost:8000/api/v1/cases/search?q=損害賠償"

# Filter by court type
curl "http://localhost:8000/api/v1/cases/search?court=最高裁判所"

# Filter by case type
curl "http://localhost:8000/api/v1/cases/search?type=civil"

# Filter by date range
curl "http://localhost:8000/api/v1/cases/search?date_from=2020-01-01&date_to=2020-12-31"

# Pagination
curl "http://localhost:8000/api/v1/cases/search?limit=20&offset=40"
```

### Get Case Detail

```bash
curl "http://localhost:8000/api/v1/cases/{case_id}"
```

### Get Cases by Law

```bash
curl "http://localhost:8000/api/v1/laws/{law_id}/cases"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_case_repository.py

# Run integration tests only
pytest tests/integration/
```

## Batch Processing

```bash
# Fetch recent cases (last 7 days)
python -m app.batch.fetch_cases

# Fetch cases from last 30 days
python -m app.batch.fetch_cases --days 30
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current
```

## Project Structure

```
e-gov-api-fastAPI/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── cases.py          # Case API endpoints
│   │   │   └── laws.py           # Law-related endpoints
│   │   └── router.py             # Main API router
│   ├── batch/
│   │   └── fetch_cases.py        # Batch processing script
│   ├── core/
│   │   └── config.py             # Application configuration
│   ├── db/
│   │   ├── base.py               # SQLAlchemy base
│   │   ├── models.py             # Database models
│   │   └── session.py            # Session management
│   ├── models/
│   │   └── case.py               # Pydantic models
│   ├── repositories/
│   │   └── case_repository.py    # Data access layer
│   ├── services/
│   │   └── case_scraper.py       # Scraper service
│   └── main.py                   # FastAPI application
├── alembic/
│   ├── versions/                 # Migration scripts
│   └── env.py                    # Alembic configuration
├── tests/
│   ├── integration/              # Integration tests
│   ├── unit/                     # Unit tests
│   └── conftest.py               # Test configuration
├── alembic.ini                   # Alembic settings
├── pyproject.toml                # Project dependencies
└── .env.example                  # Environment template
```

## Next Steps

### TODO: Complete Scraper Implementation

The current scraper service (`app/services/case_scraper.py`) is a placeholder. To complete it:

1. **Research Courts Website Structure**
   - Check `https://www.courts.go.jp/` structure
   - Review `robots.txt` for scraping permissions
   - Identify case search and detail pages

2. **Implement Scraping Logic**
   - Update `search_cases()` method
   - Update `fetch_case_detail()` method
   - Update `parse_case_html()` method

3. **Add Rate Limiting**
   - Implement request throttling
   - Add retry logic with exponential backoff
   - Respect `SCRAPER_RATE_LIMIT` setting

4. **Handle Errors**
   - Network errors
   - Parsing errors
   - Invalid data

### Optional Enhancements

1. **Full-Text Search**
   - Add PostgreSQL full-text search indexes
   - Implement Japanese text search with `pg_bigm` or similar

2. **Caching**
   - Add Redis for caching frequently accessed cases
   - Cache search results

3. **Background Jobs**
   - Use Celery for scheduled scraping
   - Implement job queue for async processing

4. **Monitoring**
   - Add logging
   - Add metrics (Prometheus)
   - Add health checks

## Notes

- Always check and respect `robots.txt` when implementing scraping
- Consider legal aspects of scraping court case data
- Rate limiting is crucial to avoid overloading the Courts website
- The scraper is designed to be easily swappable if an official API becomes available

## Support

For questions or issues, please refer to:
- API Documentation: `http://localhost:8000/docs`
- Project README: `readme.md`
- Feature Specification: `docs/rd/feature-02-case-api.md`
