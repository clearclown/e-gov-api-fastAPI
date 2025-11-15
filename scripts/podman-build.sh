#!/bin/bash
# Build Docker image with Podman/Docker

set -e

echo "🔨 Building e-gov API image..."

# Build using docker-compose
if command -v podman &> /dev/null; then
    podman compose build
else
    docker compose build
fi

echo "✅ Build complete!"
echo ""
echo "To start services:"
echo "  podman compose up -d"
echo "  # or: docker compose up -d"
