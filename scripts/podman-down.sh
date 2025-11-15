#!/bin/bash
# Stop services with Podman/Docker Compose

set -e

echo "🛑 Stopping e-gov API services..."

# Stop using docker-compose
if command -v podman &> /dev/null; then
    podman compose down
else
    docker compose down
fi

echo "✅ Services stopped!"
