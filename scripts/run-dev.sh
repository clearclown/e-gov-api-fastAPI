#!/bin/bash
# Development server startup script using uv

set -e

echo "🚀 Starting e-gov API development server with uv..."

# Run with uv
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
