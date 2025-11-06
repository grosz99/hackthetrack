"""
Pytest configuration and shared fixtures for backend tests.

Provides reusable fixtures for Snowflake testing, database mocking,
and environment setup.
"""

import os
import pytest
from typing import Generator, Dict
from unittest.mock import Mock, MagicMock
import pandas as pd


@pytest.fixture(scope="session")
def test_env_vars() -> Dict[str, str]:
    """
    Fixture providing test environment variables.

    Returns test-safe values for all required environment variables.
    Use this for tests that don't need real Snowflake connections.
    """
    return {
        "ANTHROPIC_API_KEY": "sk-ant-test-key-123",
        "USE_SNOWFLAKE": "false",
        "SNOWFLAKE_ACCOUNT": "test-account.us-east-1",
        "SNOWFLAKE_USER": "test_user",
        "SNOWFLAKE_PASSWORD": "test_password",
        "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH",
        "SNOWFLAKE_DATABASE": "HACKTHETRACK",
        "SNOWFLAKE_SCHEMA": "TELEMETRY",
        "SNOWFLAKE_ROLE": "ACCOUNTADMIN",
    }


@pytest.fixture(scope="function")
def mock_snowflake_connection():
    """
    Fixture providing a mocked Snowflake connection.

    Use this for unit tests that need to simulate Snowflake connectivity
    without making actual network calls.

    Example:
        def test_query(mock_snowflake_connection):
            mock_conn = mock_snowflake_connection
            # Connection is already configured with basic mock behavior
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Configure cursor behavior
    mock_cursor.fetchall.return_value = [(1,), (2,), (3,)]
    mock_cursor.fetchone.return_value = ("3.0.0", "HACKTHETRACK")
    mock_conn.cursor.return_value = mock_cursor

    return mock_conn


@pytest.fixture(scope="function")
def sample_telemetry_data() -> pd.DataFrame:
    """
    Fixture providing sample telemetry data for testing.

    Returns a DataFrame with realistic telemetry data structure
    matching Snowflake schema.
    """
    return pd.DataFrame({
        "vehicle_number": [13, 13, 13, 27, 27, 27],
        "lap": [1, 1, 1, 1, 1, 1],
        "sample_time": [0.0, 0.1, 0.2, 0.0, 0.1, 0.2],
        "speed": [100.5, 105.2, 110.3, 98.5, 103.2, 108.1],
        "throttle": [75.5, 80.2, 85.3, 72.5, 78.2, 83.1],
        "brake": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "track_id": ["barber"] * 6,
        "race_num": [1] * 6,
    })


@pytest.fixture(scope="function")
def real_env_check() -> bool:
    """
    Fixture that checks if real Snowflake credentials are available.

    Use this to conditionally skip tests that require actual Snowflake access.

    Example:
        @pytest.mark.skipif(not real_env_check, reason="No real credentials")
        def test_real_snowflake(real_env_check):
            # Test that needs actual Snowflake connection
            pass
    """
    required_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD"
    ]

    return all(
        os.getenv(var) and os.getenv(var) not in ["", "your-account.your-region", "your_username", "your_password"]
        for var in required_vars
    )


@pytest.fixture(scope="function")
def mock_env_vars(test_env_vars, monkeypatch):
    """
    Fixture that sets test environment variables for the duration of a test.

    Automatically cleans up after test completion.

    Example:
        def test_with_env(mock_env_vars):
            # Environment variables are set
            assert os.getenv("SNOWFLAKE_ACCOUNT") == "test-account.us-east-1"
    """
    for key, value in test_env_vars.items():
        monkeypatch.setenv(key, value)

    return test_env_vars


@pytest.fixture(scope="function")
def clean_snowflake_cache():
    """
    Fixture that clears LRU cache on SnowflakeService between tests.

    Ensures tests don't share cached connection state.
    """
    from app.services.snowflake_service import SnowflakeService

    # Clear the LRU cache before test
    if hasattr(SnowflakeService.get_drivers_with_telemetry, 'cache_clear'):
        SnowflakeService.get_drivers_with_telemetry.cache_clear()

    yield

    # Clear again after test
    if hasattr(SnowflakeService.get_drivers_with_telemetry, 'cache_clear'):
        SnowflakeService.get_drivers_with_telemetry.cache_clear()
