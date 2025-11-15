#!/bin/bash
# Start services with Podman/Docker Compose

set -e

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Set defaults if not defined
API_PORT=${API_PORT:-8000}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
REDIS_PORT=${REDIS_PORT:-6379}

echo "🐳 Starting e-gov API services..."

# Start using docker-compose
if command -v podman &> /dev/null; then
    podman compose up -d
else
    docker compose up -d
fi

echo "✅ Services started!"
echo ""
echo "API: http://localhost:${API_PORT}"
echo "Health check: http://localhost:${API_PORT}/health"
echo "API Docs: http://localhost:${API_PORT}/docs"
echo ""
echo "Services:"
echo "  - PostgreSQL: localhost:${POSTGRES_PORT}"
echo "  - Redis: localhost:${REDIS_PORT}"
echo "  - API: localhost:${API_PORT}"
echo ""
echo "To view logs:"
echo "  podman compose logs -f"
echo "  # or: docker compose logs -f"
echo ""
echo "To stop services:"
echo "  podman compose down"
echo "  # or: docker compose down"
