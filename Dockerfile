# Multi-Platform Dockerfile for Automated Trading Model
# Compatible with macOS (Apple Silicon & Intel), Ubuntu/Linux, and Windows (Docker Desktop / WSL2)

FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Install system dependencies (build tools & curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies manifest first for Docker layer caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code into container
COPY config/ ./config/
COPY data/ ./data/
COPY strategy/ ./strategy/
COPY risk/ ./risk/
COPY execution/ ./execution/
COPY main.py .

# Entrypoint command to run the trading model
CMD ["python", "main.py"]
