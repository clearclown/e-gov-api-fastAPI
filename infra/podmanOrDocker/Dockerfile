# Podman/Docker-compatible Dockerfile using uv
FROM docker.io/library/python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY app ./app
COPY scripts ./scripts

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Expose port (internal container port - host mapping in compose)
EXPOSE 8000

# Environment variables for runtime configuration
ENV UVICORN_WORKERS=1

# Run the application using uv with configurable workers
# Shell form allows environment variable expansion
CMD uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS}
