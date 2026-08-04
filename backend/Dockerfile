# Use official Python image as base
FROM python:3.13-slim

# Prevent Python from buffering stdout/stderr and writing .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000

WORKDIR /app

# Install basic system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install project dependencies into global python environment
RUN uv pip install --system --no-cache .

# Install Playwright Chromium browser and its system dependencies
RUN playwright install chromium --with-deps

# Copy project source code
COPY . .

# Expose default port
EXPOSE 8000

# Run FastAPI app with Uvicorn reading PORT dynamically (Render/Koyeb compatible)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
