# Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- `uv` package manager

## Installation

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup Project

```bash
# Navigate to project directory
cd e-gov-api-fastAPI

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -e ".[dev]"
```

### 3. Configure Database

```bash
# Create PostgreSQL database
createdb egov_db

# Create test database (for running tests)
createdb egov_test_db

# Copy environment template
cp .env.example .env

# Edit .env and update DATABASE_URL if needed
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/egov_db
```

### 4. Run Database Migrations

```bash
# Apply migrations to create tables
alembic upgrade head
```

### 5. Start the Application

```bash
# Run development server
uvicorn app.main:app --reload

# The API will be available at:
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

## Verify Installation

### Check Health Endpoint

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Test API

```bash
# Search cases (will be empty initially)
curl http://localhost:8000/api/v1/cases/search
# Expected: {"total": 0, "limit": 50, "offset": 0, "results": []}
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Development Workflow

### 1. Making Code Changes

The application will auto-reload when you make changes (when using `--reload` flag).

### 2. Adding Database Changes

```bash
# After modifying models, create a migration
alembic revision --autogenerate -m "description of changes"

# Apply the migration
alembic upgrade head
```

### 3. Running Batch Jobs

```bash
# Fetch recent cases (placeholder - needs scraper implementation)
python -m app.batch.fetch_cases --days 7
```

## Troubleshooting

### Database Connection Error

If you get database connection errors:
1. Ensure PostgreSQL is running
2. Check DATABASE_URL in `.env`
3. Verify database exists: `psql -l`

### Import Errors

If you get import errors:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `uv pip install -e ".[dev]"`

### Migration Errors

If migrations fail:
1. Check current version: `alembic current`
2. Downgrade if needed: `alembic downgrade -1`
3. Re-run upgrade: `alembic upgrade head`

## Next Steps

1. **Implement Scraper Logic**
   - Update `app/services/case_scraper.py` with actual scraping code
   - Research Courts website structure

2. **Add More Tests**
   - Increase test coverage
   - Add edge case tests

3. **Implement Phase 1 (Law API)**
   - Add e-gov API client
   - Implement law endpoints

4. **Setup Production**
   - Configure production database
   - Setup environment variables
   - Deploy application

## Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic: https://alembic.sqlalchemy.org/
- uv: https://github.com/astral-sh/uv
