#!/bin/bash
# Setup script for uv environment

set -e

echo "📦 Setting up e-gov API with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv version: $(uv --version)"

# Sync dependencies
echo "📥 Syncing dependencies..."
uv sync

echo "✅ Setup complete!"
echo ""
echo "To run the development server:"
echo "  ./scripts/run-dev.sh"
echo ""
echo "Or use uv run directly:"
echo "  uv run uvicorn app.main:app --reload"
