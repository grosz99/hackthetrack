"""
Pytest configuration and fixtures for Racing Analytics tests.
"""

import pytest
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--run-ai-tests",
        action="store_true",
        default=False,
        help="Run AI tests (require API keys)",
    )
    parser.addoption(
        "--api-url",
        action="store",
        default="http://localhost:8000",
        help="API base URL for deployment tests",
    )
    parser.addoption(
        "--frontend-url",
        action="store",
        default="http://localhost:5173",
        help="Frontend URL for integration tests",
    )


@pytest.fixture(scope="session")
def api_url(request):
    """Get API URL from command line option."""
    return request.config.getoption("--api-url")


@pytest.fixture(scope="session")
def frontend_url(request):
    """Get frontend URL from command line option."""
    return request.config.getoption("--frontend-url")


@pytest.fixture(scope="session")
def run_ai_tests(request):
    """Check if AI tests should be run."""
    return request.config.getoption("--run-ai-tests")
