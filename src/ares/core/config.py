"""ARES Configuration Management."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"

    # Database - PostgreSQL primary, SQLite fallback for development
    DATABASE_URL: str = "postgresql+asyncpg://postgres:devpass@localhost:5432/ares_dev"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "ares_dev"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "devpass"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ARES-specific settings
    ARES_AGENT_MONITORING_INTERVAL: int = 30
    ARES_ENFORCEMENT_ENABLED: bool = True
    ARES_MCP_DISCOVERY_ENABLED: bool = True
    EVIDENCE_STORAGE_PATH: str | None = None

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    # Server
    RELOAD: bool = True
    WORKERS: int = 1

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
