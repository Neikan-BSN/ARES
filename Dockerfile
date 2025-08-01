# ARES Multi-Stage Dockerfile
# Agent Reliability Enforcement System - Production-grade container build

# ===== STAGE 1: Base Python with UV =====
FROM python:3.11-slim-bookworm AS base

# Build arguments
ARG PYTHON_VERSION=3.11
ARG UV_VERSION=0.4.18
ARG PROJECT_NAME="ares"

# Environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Security: Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# System dependencies and security updates
RUN apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    curl \
    git \
    # PostgreSQL dependencies
    libpq-dev \
    # Security updates
    && apt-get upgrade -y \
    # Cleanup to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy UV configuration files first (for better caching)
COPY pyproject.toml uv.lock* ./

# ===== STAGE 2: Dependency Installation =====
FROM base AS dependencies

# Ensure UV is in PATH and available
ENV PATH="/root/.cargo/bin:$PATH"

# Install Python dependencies with UV
RUN uv sync --frozen --no-dev

# ===== STAGE 3: Development Dependencies =====
FROM dependencies AS development-deps

# Install development dependencies
RUN uv sync --frozen --all-extras

# Install additional development tools
RUN uv tool install black && \
    uv tool install ruff && \
    uv tool install mypy && \
    uv tool install pytest

# ===== STAGE 4: Application Code =====
FROM dependencies AS app-base

# Copy application source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Security: Change ownership to non-root user
RUN chown -R appuser:appuser /app

# ===== STAGE 5: Production Image =====
FROM app-base AS production

# Install production system dependencies
RUN apt-get update && apt-get install -y \
    # Runtime dependencies only
    libpq5 \
    # Security updates
    && apt-get upgrade -y \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Security hardening
RUN find /app -type f -name "*.py" -exec chmod 644 {} \; && \
    find /app -type d -exec chmod 755 {} \; && \
    chmod +x /app/scripts/*.sh

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

# Install additional development tools
RUN apt-get update && apt-get install -y \
    # Development tools
    vim \
    curl \
    netcat-traditional \
    postgresql-client \
    redis-tools \
    # Debugging tools
    strace \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/
COPY config/ ./config/
COPY migrations/ ./migrations/
COPY alembic.ini ./
COPY .env.example ./.env

# Security: Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Development command with hot reload
CMD ["uv", "run", "uvicorn", "src.ares.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ===== STAGE 7: Celery Worker =====
FROM app-base AS celery-worker

# Switch to non-root user
USER appuser

# Celery worker command
CMD ["uv", "run", "celery", "-A", "src.ares.celery_app", "worker", "--loglevel=INFO"]

# ===== STAGE 8: Celery Beat Scheduler =====
FROM app-base AS celery-beat

# Switch to non-root user
USER appuser

# Celery beat command
CMD ["uv", "run", "celery", "-A", "src.ares.celery_app", "beat", "--loglevel=INFO"]

# ===== STAGE 9: Testing Image =====
FROM development-deps AS testing

# Copy all source code and tests
COPY . .

# Install test-specific dependencies
RUN uv add pytest-cov pytest-asyncio pytest-mock

# Security: Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Test command
CMD ["uv", "run", "pytest", "-v", "--cov=src"]

# ===== BUILD METADATA =====
LABEL maintainer="ARES Development Team" \
      version="0.1.0" \
      description="Agent Reliability Enforcement System" \
      security.scan="enabled" \
      build.multi-arch="linux/amd64,linux/arm64" \
      framework="fastapi" \
      package-manager="uv" \
      python.version="3.11"

# Build information
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL build.date="${BUILD_DATE}" \
      vcs.ref="${VCS_REF}" \
      version="${VERSION}"
