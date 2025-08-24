"""Test configuration for ARES"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))


# Global test fixtures
@pytest.fixture
def mock_async_session():
    """Create a mock async session for database testing."""
    session = AsyncMock()
    session.execute.return_value = Mock(rowcount=1)
    session.commit.return_value = None
    session.rollback.return_value = None
    return session


@pytest.fixture
def mock_database_get_session(mock_async_session):
    """Mock the get_async_session dependency."""
    return lambda: mock_async_session
