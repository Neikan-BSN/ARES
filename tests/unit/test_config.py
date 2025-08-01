"""Test ARES configuration."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ares.core.config import Settings


def test_settings_defaults():
    """Test default settings."""
    settings = Settings()

    assert settings.DEBUG is True
    assert settings.ENVIRONMENT == "development"
    assert settings.LOG_LEVEL == "DEBUG"
    assert settings.DATABASE_URL == "sqlite:///./ares.db"
    assert settings.REDIS_URL == "redis://localhost:6379/0"
    assert settings.ARES_AGENT_MONITORING_INTERVAL == 30
    assert settings.ARES_ENFORCEMENT_ENABLED is True
    assert settings.ARES_MCP_DISCOVERY_ENABLED is True


def test_settings_environment_override():
    """Test settings can be overridden by environment."""
    import os

    # Temporarily set environment variable
    os.environ["ARES_AGENT_MONITORING_INTERVAL"] = "60"

    settings = Settings()
    assert settings.ARES_AGENT_MONITORING_INTERVAL == 60

    # Clean up
    del os.environ["ARES_AGENT_MONITORING_INTERVAL"]
