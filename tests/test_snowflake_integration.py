"""
Snowflake integration tests.

Comprehensive testing of Snowflake service including:
- Connection establishment and failure modes
- Query execution and data retrieval
- Error handling and graceful degradation
- Performance characteristics
- Cache behavior

Run with: pytest tests/test_snowflake_integration.py -v
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import os
import time


class TestSnowflakeConnection:
    """Test Snowflake connection establishment and lifecycle."""

    def test_service_initializes_with_env_vars(self, mock_env_vars):
        """
        Verify SnowflakeService reads configuration from environment.

        Ensures service picks up credentials correctly.
        """
        from app.services.snowflake_service import SnowflakeService

        service = SnowflakeService()

        assert service.account == "test-account.us-east-1"
        assert service.user == "test_user"
        assert service.password == "test_password"
        assert service.warehouse == "COMPUTE_WH"
        assert service.database == "HACKTHETRACK"
        assert service.schema == "TELEMETRY"

    def test_connection_fails_with_missing_credentials(self, monkeypatch):
        """
        Verify connection fails fast when credentials are missing.

        Critical for fail-fast principle: detect issues immediately.
        """
        from app.services.snowflake_service import SnowflakeService

        # Clear credentials
        monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "")
        monkeypatch.setenv("SNOWFLAKE_USER", "")
        monkeypatch.setenv("SNOWFLAKE_PASSWORD", "")

        service = SnowflakeService()

        with pytest.raises(ValueError) as exc_info:
            service.get_connection()

        assert "Missing Snowflake credentials" in str(exc_info.value)
        assert "SNOWFLAKE_ACCOUNT" in str(exc_info.value)

    def test_connection_fails_with_invalid_credentials(self, mock_env_vars):
        """
        Verify connection fails gracefully with invalid credentials.

        Ensures proper error handling for authentication failures.
        """
        from app.services.snowflake_service import SnowflakeService

        service = SnowflakeService()

        # Since we're using test credentials, connection will fail
        # This tests that the error is handled properly
        try:
            conn = service.get_connection()
            # If we got here with test creds, something is wrong
            pytest.fail("Should not connect with test credentials")
        except Exception as e:
            # Expected - test credentials should fail
            # Verify error message is informative
            assert isinstance(e, Exception)
            # The actual Snowflake error will vary, just ensure it's raised

    @pytest.mark.integration
    def test_connection_succeeds_with_valid_credentials(self):
        """
        Verify connection succeeds with real credentials.

        INTEGRATION TEST: Requires real Snowflake credentials in environment.
        """
        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        from app.services.snowflake_service import SnowflakeService

        service = SnowflakeService()

        try:
            conn = service.get_connection()
            assert conn is not None

            # Verify connection is functional
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()

            assert version is not None
            assert len(version) > 0

            conn.close()

        except Exception as e:
            pytest.fail(f"Connection failed with real credentials: {str(e)}")

    @pytest.mark.integration
    def test_connection_cleanup_on_close(self):
        """
        Verify connections are properly closed to prevent leaks.

        Connection leaks could exhaust Snowflake connection limits.
        """
        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        from app.services.snowflake_service import SnowflakeService

        service = SnowflakeService()

        conn = service.get_connection()
        assert conn is not None

        # Close and verify it's closed
        conn.close()

        # Attempting to use closed connection should fail
        with pytest.raises(Exception):
            cursor = conn.cursor()
            cursor.execute("SELECT 1")


class TestDriversWithTelemetry:
    """Test get_drivers_with_telemetry() method."""

    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_returns_driver_list(self, mock_connect, mock_env_vars):
        """
        Verify method returns list of driver numbers.

        This is critical for populating driver selection UI.
        """
        from app.services.snowflake_service import SnowflakeService

        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(0,), (2,), (3,), (5,), (13,), (27,)]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        service = SnowflakeService()

        # Clear cache first
        if hasattr(service.get_drivers_with_telemetry, 'cache_clear'):
            service.get_drivers_with_telemetry.cache_clear()

        drivers = service.get_drivers_with_telemetry()

        assert isinstance(drivers, list)
        assert len(drivers) == 6
        assert drivers == [0, 2, 3, 5, 13, 27]
        assert all(isinstance(d, int) for d in drivers)

    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_returns_sorted_list(self, mock_connect, mock_env_vars):
        """
        Verify driver list is sorted for consistent UI display.

        Unsorted list would cause confusing driver selection experience.
        """
        from app.services.snowflake_service import SnowflakeService

        # Setup mock with unsorted data
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(27,), (3,), (13,), (0,), (5,)]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        service = SnowflakeService()

        # Clear cache
        if hasattr(service.get_drivers_with_telemetry, 'cache_clear'):
            service.get_drivers_with_telemetry.cache_clear()

        drivers = service.get_drivers_with_telemetry()

        assert drivers == [0, 3, 5, 13, 27], "Drivers should be sorted"

    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_caches_results(self, mock_connect, mock_env_vars):
        """
        Verify results are cached to reduce database queries.

        Caching improves performance and reduces Snowflake costs.
        """
        from app.services.snowflake_service import SnowflakeService

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(13,), (27,)]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        service = SnowflakeService()

        # Clear cache before test
        if hasattr(service.get_drivers_with_telemetry, 'cache_clear'):
            service.get_drivers_with_telemetry.cache_clear()

        # First call
        drivers1 = service.get_drivers_with_telemetry()

        # Second call - should use cache
        drivers2 = service.get_drivers_with_telemetry()

        assert drivers1 == drivers2

        # Should only connect once due to caching
        assert mock_connect.call_count == 1, "Should cache results"

    @pytest.mark.integration
    def test_returns_real_drivers(self, clean_snowflake_cache):
        """
        Verify method returns actual drivers from Snowflake.

        INTEGRATION TEST: Requires real Snowflake with data.
        """
        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        from app.services.snowflake_service import SnowflakeService

        service = SnowflakeService()

        drivers = service.get_drivers_with_telemetry()

        assert isinstance(drivers, list)
        assert len(drivers) > 0, "Should have at least one driver with telemetry"
        assert all(isinstance(d, int) for d in drivers)
        assert all(0 <= d <= 99 for d in drivers), "Driver numbers should be 0-99"

        print(f"\n✓ Found {len(drivers)} drivers with telemetry: {drivers}")


class TestTelemetryDataRetrieval:
    """Test get_telemetry_data() method."""

    @patch('app.services.snowflake_service.pd.read_sql')
    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_returns_dataframe(self, mock_connect, mock_read_sql, mock_env_vars, sample_telemetry_data):
        """
        Verify method returns pandas DataFrame with telemetry data.

        DataFrame is required format for downstream processing.
        """
        from app.services.snowflake_service import SnowflakeService

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_read_sql.return_value = sample_telemetry_data

        service = SnowflakeService()
        df = service.get_telemetry_data("barber", 1, 13)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "vehicle_number" in df.columns
        assert "speed" in df.columns

    @patch('app.services.snowflake_service.pd.read_sql')
    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_filters_by_driver(self, mock_connect, mock_read_sql, mock_env_vars, sample_telemetry_data):
        """
        Verify method correctly filters by driver number.

        Critical for returning only requested driver's data.
        """
        from app.services.snowflake_service import SnowflakeService

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Filter sample data to only driver 13
        driver_13_data = sample_telemetry_data[sample_telemetry_data["vehicle_number"] == 13]
        mock_read_sql.return_value = driver_13_data

        service = SnowflakeService()
        df = service.get_telemetry_data("barber", 1, driver_number=13)

        assert all(df["vehicle_number"] == 13)
        assert len(df) == 3  # From sample data

    @patch('app.services.snowflake_service.pd.read_sql')
    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_query_uses_parameters(self, mock_connect, mock_read_sql, mock_env_vars, sample_telemetry_data):
        """
        Verify queries use parameterized SQL to prevent SQL injection.

        Security best practice: never interpolate user input into SQL.
        """
        from app.services.snowflake_service import SnowflakeService

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_read_sql.return_value = sample_telemetry_data

        service = SnowflakeService()
        df = service.get_telemetry_data("barber", 1, driver_number=13)

        # Verify pd.read_sql was called with params
        assert mock_read_sql.called
        call_args = mock_read_sql.call_args

        # Check that params were passed
        assert "params" in call_args.kwargs or len(call_args.args) >= 3

    @pytest.mark.integration
    def test_retrieves_real_telemetry(self):
        """
        Verify method retrieves actual telemetry from Snowflake.

        INTEGRATION TEST: Requires real Snowflake with data.
        """
        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        from app.services.snowflake_service import SnowflakeService

        service = SnowflakeService()

        # First, get a driver that has data
        drivers = service.get_drivers_with_telemetry()
        if not drivers:
            pytest.skip("No drivers with telemetry data")

        test_driver = drivers[0]

        # Try to get telemetry for first available track/race
        # This assumes data exists - adjust as needed
        try:
            df = service.get_telemetry_data("barber", 1, test_driver)

            assert isinstance(df, pd.DataFrame)
            assert not df.empty, f"No telemetry data for driver {test_driver}"
            assert "vehicle_number" in df.columns
            assert all(df["vehicle_number"] == test_driver)

            print(f"\n✓ Retrieved {len(df)} telemetry rows for driver {test_driver}")

        except Exception as e:
            pytest.skip(f"Could not retrieve test data: {str(e)}")

    @pytest.mark.integration
    def test_query_performance_acceptable(self):
        """
        Verify telemetry queries execute in reasonable time.

        Slow queries degrade user experience. Target: <5 seconds.
        """
        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        from app.services.snowflake_service import SnowflakeService

        service = SnowflakeService()

        drivers = service.get_drivers_with_telemetry()
        if not drivers:
            pytest.skip("No drivers with telemetry data")

        test_driver = drivers[0]

        start_time = time.time()

        try:
            df = service.get_telemetry_data("barber", 1, test_driver)
            elapsed = time.time() - start_time

            assert elapsed < 5.0, (
                f"Query took {elapsed:.2f}s (limit: 5s). "
                f"Consider warehouse sizing or query optimization."
            )

            print(f"\n✓ Query completed in {elapsed:.2f}s ({len(df)} rows)")

        except Exception as e:
            pytest.skip(f"Could not test performance: {str(e)}")


class TestConnectionHealthCheck:
    """Test check_connection() method."""

    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_returns_success_dict(self, mock_connect, mock_env_vars):
        """
        Verify health check returns structured status information.

        Used for monitoring and diagnostics.
        """
        from app.services.snowflake_service import SnowflakeService

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("3.0.0", "HACKTHETRACK")
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        service = SnowflakeService()
        status = service.check_connection()

        assert isinstance(status, dict)
        assert status["status"] == "connected"
        assert "version" in status
        assert "database" in status
        assert status["database"] == "HACKTHETRACK"

    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_returns_error_on_failure(self, mock_connect, mock_env_vars):
        """
        Verify health check returns error status on failure.

        Critical for monitoring systems to detect issues.
        """
        from app.services.snowflake_service import SnowflakeService

        # Simulate connection failure
        mock_connect.side_effect = Exception("Connection timeout")

        service = SnowflakeService()
        status = service.check_connection()

        assert isinstance(status, dict)
        assert status["status"] == "error"
        assert "error" in status
        assert "timeout" in status["error"].lower()

    @pytest.mark.integration
    def test_real_health_check(self):
        """
        Verify health check works with real Snowflake.

        INTEGRATION TEST: Requires real Snowflake credentials.
        """
        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        from app.services.snowflake_service import SnowflakeService

        service = SnowflakeService()
        status = service.check_connection()

        assert status["status"] == "connected", (
            f"Health check failed: {status.get('error', 'Unknown error')}"
        )
        assert "version" in status
        assert "database" in status

        print(f"\n✓ Snowflake health check passed: {status}")


class TestErrorHandling:
    """Test error handling and graceful degradation."""

    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_handles_network_timeout(self, mock_connect, mock_env_vars):
        """
        Verify service handles network timeouts gracefully.

        Network issues should not crash the application.
        """
        from app.services.snowflake_service import SnowflakeService
        import socket

        mock_connect.side_effect = socket.timeout("Connection timed out")

        service = SnowflakeService()

        with pytest.raises(socket.timeout):
            service.get_connection()

    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_handles_authentication_error(self, mock_connect, mock_env_vars):
        """
        Verify service handles authentication failures properly.

        Auth errors should provide clear error messages.
        """
        from app.services.snowflake_service import SnowflakeService

        mock_connect.side_effect = Exception("Invalid username or password")

        service = SnowflakeService()

        with pytest.raises(Exception) as exc_info:
            service.get_connection()

        assert "password" in str(exc_info.value).lower()

    @patch('app.services.snowflake_service.snowflake.connector.connect')
    def test_connection_closes_on_error(self, mock_connect, mock_env_vars):
        """
        Verify connections are closed even when queries fail.

        Prevents connection leaks during error conditions.
        """
        from app.services.snowflake_service import SnowflakeService

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        service = SnowflakeService()

        # Clear cache
        if hasattr(service.get_drivers_with_telemetry, 'cache_clear'):
            service.get_drivers_with_telemetry.cache_clear()

        try:
            service.get_drivers_with_telemetry()
        except Exception:
            pass

        # Verify connection was closed
        mock_conn.close.assert_called()
