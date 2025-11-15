#!/bin/bash
# Production server startup script using uv

set -e

echo "🚀 Starting e-gov API production server with uv..."

# Run with uv (without reload)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
