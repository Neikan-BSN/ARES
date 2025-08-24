# ARES - Advanced BuildKit Multi-Stage Dockerfile
# Agent Reliability Enforcement System - Production-ready multi-agent coordination
# Optimized for <3min builds with advanced caching strategy
# syntax=docker/dockerfile:1.7

# ===== STAGE 1: Base Python with UV =====
FROM python:3.12-slim-bookworm AS base

# Build arguments for optimization
ARG PYTHON_VERSION=3.12
ARG UV_VERSION=0.8.3
ARG PROJECT_NAME="ares"
ARG BUILDKIT_INLINE_CACHE=1

# Environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_CACHE_DIR=/root/.cache/uv \
    UV_COMPILE_BYTECODE=1

# Security: Create non-root user early for layer caching
RUN groupadd -r appuser && useradd -r -g appuser appuser

# System dependencies with advanced caching
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    curl \
    git \
    # Agent-system specific dependencies
    libpq-dev \
    redis-tools \
    # Security updates
    && apt-get upgrade -y

# Install UV with cache mount for faster rebuilds
RUN --mount=type=cache,target=/root/.cache/uv \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uv && \
    uv --version

# Set working directory
WORKDIR /app

# Copy essential files only (for optimal caching)
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./

# ===== STAGE 2: Core Dependency Installation =====
FROM base AS dependencies

# Install Python dependencies with advanced UV caching
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    uv sync --frozen --no-dev

# ===== STAGE 3: Development Dependencies =====
FROM dependencies AS development-deps

# Install development dependencies with cache mounts
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    uv sync --frozen --all-extras

# Install additional development tools with cache
RUN --mount=type=cache,target=/root/.cache/uv \
    uv tool install ruff && \
    uv tool install mypy && \
    uv tool install pytest

# ===== STAGE 4: Application Code =====
FROM dependencies AS app-base

# Copy application source code (optimized order for caching)
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Ensure project is installed properly
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --no-dev

# Security: Change ownership to non-root user
RUN chown -R appuser:appuser /app

# ===== STAGE 5: Production Image =====
FROM app-base AS production

# Install production runtime dependencies with cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    # Runtime dependencies only
    libpq5 \
    curl \
    # Security updates
    && apt-get upgrade -y

# Security hardening
RUN find /app -type f -name "*.py" -exec chmod 644 {} \; && \
    find /app -type d -exec chmod 755 {} \; && \
    chmod +x /app/scripts/*.sh 2>/dev/null || true

# Health check script
COPY docker-healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh && \
    chown appuser:appuser /usr/local/bin/healthcheck.sh

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Production command
CMD ["uv", "run", "uvicorn", "src.ares.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ===== STAGE 6: Development Image =====
FROM development-deps AS development

# Install additional development tools with cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    # Development tools
    vim \
    curl \
    netcat-traditional \
    postgresql-client \
    redis-tools \
    # Debugging tools
    strace

# Copy application source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Create .env file for development
RUN touch ./.env

# Install project with development dependencies
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --all-extras

# Security: Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Development command with hot reload
CMD ["uv", "run", "uvicorn", "src.ares.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ===== STAGE 7: Testing Image =====
FROM development-deps AS testing

# Copy all source code and tests
COPY . .

# Install project with test dependencies
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --all-extras

# Security: Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Test command
CMD ["uv", "run", "pytest", "-v", "--cov=src"]

# ===== STAGE 8: Celery Worker =====
FROM app-base AS celery-worker

# Install runtime dependencies for Celery
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    libpq5 \
    && apt-get upgrade -y

# Security hardening
RUN find /app -type f -name "*.py" -exec chmod 644 {} \; && \
    find /app -type d -exec chmod 755 {} \; && \
    chmod +x /app/scripts/*.sh 2>/dev/null || true

# Security: Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Celery worker command
CMD ["uv", "run", "celery", "-A", "src.ares.celery_app", "worker", "--loglevel=info"]

# ===== STAGE 9: Celery Beat =====
FROM app-base AS celery-beat

# Install runtime dependencies for Celery Beat
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    libpq5 \
    && apt-get upgrade -y

# Security hardening
RUN find /app -type f -name "*.py" -exec chmod 644 {} \; && \
    find /app -type d -exec chmod 755 {} \; && \
    chmod +x /app/scripts/*.sh 2>/dev/null || true

# Security: Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Celery beat command
CMD ["uv", "run", "celery", "-A", "src.ares.celery_app", "beat", "--loglevel=info"]

# ===== BUILD METADATA =====
LABEL maintainer="Agent System Development Team" \
      version="0.1.0" \
      description="Agent Reliability Enforcement System - Production-ready multi-agent coordination" \
      security.scan="enabled" \
      build.multi-arch="linux/amd64,linux/arm64" \
      framework="fastapi" \
      package-manager="uv" \
      python.version="3.12" \
      optimization="buildkit-cache-mounts"

# Build information
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL build.date="${BUILD_DATE}" \
      vcs.ref="${VCS_REF}" \
      version="${VERSION}"
