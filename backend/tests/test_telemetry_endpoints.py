"""
API endpoint tests for telemetry functionality.

Tests the critical telemetry endpoints that integrate with Snowflake:
- /api/telemetry/drivers - Driver list retrieval
- /api/telemetry/coaching - AI coaching with telemetry analysis

Validates both Snowflake and local CSV fallback paths.

Run with: pytest tests/test_telemetry_endpoints.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
import os


@pytest.fixture
def client():
    """
    Fixture providing FastAPI test client.

    Use this to make API requests in tests.
    """
    from main import app
    return TestClient(app)


class TestTelemetryDriversEndpoint:
    """Test /api/telemetry/drivers endpoint."""

    def test_endpoint_exists(self, client):
        """
        Verify telemetry drivers endpoint is accessible.

        Critical endpoint for preventing "0 drivers" issue.
        """
        response = client.get("/api/telemetry/drivers")

        assert response.status_code in [200, 500], (
            "Endpoint should exist (200) or fail gracefully (500)"
        )

    @patch('app.api.routes.os.getenv')
    @patch('app.api.routes.pd.read_csv')
    def test_returns_driver_list_from_local_csv(self, mock_read_csv, mock_getenv, client):
        """
        Verify endpoint returns drivers from local CSV when Snowflake disabled.

        Tests fallback mechanism for local development.
        """
        # Configure to use local files
        def getenv_side_effect(key, default=None):
            if key == "USE_SNOWFLAKE":
                return "false"
            return os.getenv(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Mock CSV data
        sample_df = pd.DataFrame({
            "vehicle_number": [13, 27, 5, 3]
        })
        mock_read_csv.return_value = sample_df

        response = client.get("/api/telemetry/drivers")

        assert response.status_code == 200
        data = response.json()

        assert "drivers_with_telemetry" in data
        assert "count" in data
        assert "source" in data
        assert data["source"] == "local"
        assert isinstance(data["drivers_with_telemetry"], list)
        assert len(data["drivers_with_telemetry"]) > 0

    @patch('app.api.routes.os.getenv')
    def test_uses_snowflake_when_enabled(self, mock_getenv, client):
        """
        Verify endpoint attempts Snowflake when USE_SNOWFLAKE=true.

        Tests Snowflake integration path.
        """
        def getenv_side_effect(key, default=None):
            if key == "USE_SNOWFLAKE":
                return "true"
            # Return test values for Snowflake config
            if key.startswith("SNOWFLAKE_"):
                return "test-value"
            return os.getenv(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Mock Snowflake service
        with patch('app.api.routes.snowflake_service') as mock_service:
            mock_service.get_drivers_with_telemetry.return_value = [13, 27, 5]

            response = client.get("/api/telemetry/drivers")

            assert response.status_code == 200
            data = response.json()

            assert data["source"] == "snowflake"
            assert data["drivers_with_telemetry"] == [13, 27, 5]
            assert data["count"] == 3

    @patch('app.api.routes.os.getenv')
    def test_falls_back_to_local_on_snowflake_error(self, mock_getenv, client):
        """
        Verify endpoint falls back to local CSV if Snowflake fails.

        Critical for resilience: app should work even if Snowflake is down.
        """
        def getenv_side_effect(key, default=None):
            if key == "USE_SNOWFLAKE":
                return "true"
            if key.startswith("SNOWFLAKE_"):
                return "test-value"
            return os.getenv(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Mock Snowflake to fail
        with patch('app.api.routes.snowflake_service') as mock_service:
            mock_service.get_drivers_with_telemetry.side_effect = Exception("Connection failed")

            # Mock local CSV fallback
            with patch('app.api.routes.pd.read_csv') as mock_read_csv:
                sample_df = pd.DataFrame({"vehicle_number": [13, 27]})
                mock_read_csv.return_value = sample_df

                response = client.get("/api/telemetry/drivers")

                assert response.status_code == 200
                data = response.json()

                # Should fall back to local
                assert data["source"] == "local"
                assert len(data["drivers_with_telemetry"]) > 0

    def test_response_includes_source_field(self, client):
        """
        Verify response includes "source" field indicating data origin.

        Important for debugging and monitoring where data comes from.
        """
        response = client.get("/api/telemetry/drivers")

        if response.status_code == 200:
            data = response.json()
            assert "source" in data
            assert data["source"] in ["snowflake", "local"]

    def test_response_includes_count_field(self, client):
        """
        Verify response includes count of drivers found.

        Useful for monitoring and validation.
        """
        response = client.get("/api/telemetry/drivers")

        if response.status_code == 200:
            data = response.json()
            assert "count" in data
            assert isinstance(data["count"], int)
            assert data["count"] >= 0

    def test_driver_list_is_sorted(self, client):
        """
        Verify driver numbers are returned in sorted order.

        Consistent ordering improves UX.
        """
        response = client.get("/api/telemetry/drivers")

        if response.status_code == 200:
            data = response.json()
            drivers = data["drivers_with_telemetry"]

            # Check if sorted
            assert drivers == sorted(drivers), "Drivers should be sorted"

    @pytest.mark.integration
    def test_real_endpoint_returns_drivers(self, client):
        """
        Verify endpoint returns actual drivers in integration environment.

        INTEGRATION TEST: Tests with real backend setup.
        """
        response = client.get("/api/telemetry/drivers")

        assert response.status_code == 200, (
            f"Endpoint failed: {response.text}"
        )

        data = response.json()

        assert "drivers_with_telemetry" in data
        assert "source" in data
        assert len(data["drivers_with_telemetry"]) > 0, (
            "No drivers returned - check Snowflake data or local CSV files"
        )

        print(f"\n✓ Endpoint returned {data['count']} drivers from {data['source']}")


class TestTelemetryCoachingEndpoint:
    """Test /api/telemetry/coaching endpoint."""

    def test_endpoint_exists(self, client):
        """
        Verify telemetry coaching endpoint is accessible.

        Critical endpoint for AI coaching feature.
        """
        # POST request with minimal data
        request_data = {
            "driver_number": 13,
            "reference_driver_number": 27,
            "track_id": "barber",
            "race_num": 1
        }

        response = client.post("/api/telemetry/coaching", json=request_data)

        # Should exist (might be 404 if no data, but shouldn't be 404 for route)
        assert response.status_code != 404, "Endpoint should exist"

    @patch('app.api.routes.os.getenv')
    @patch('app.api.routes.pd.read_csv')
    @patch('app.api.routes.ai_telemetry_coach.generate_coaching')
    def test_uses_local_csv_when_snowflake_disabled(
        self, mock_coaching, mock_read_csv, mock_getenv, client
    ):
        """
        Verify coaching endpoint uses local CSV when Snowflake disabled.

        Tests local development path.
        """
        def getenv_side_effect(key, default=None):
            if key == "USE_SNOWFLAKE":
                return "false"
            return os.getenv(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Mock CSV data
        sample_df = pd.DataFrame({
            "vehicle_number": [13, 13, 27, 27],
            "lap": [1, 1, 1, 1],
            "speed": [100, 105, 98, 103],
            "pbrake_f": [0, 0, 0, 0],
            "aps": [75, 80, 73, 78]
        })
        mock_read_csv.return_value = sample_df

        # Mock AI coaching response
        mock_coaching.return_value = "Focus on brake point in Turn 1"

        request_data = {
            "driver_number": 13,
            "reference_driver_number": 27,
            "track_id": "barber",
            "race_num": 1
        }

        response = client.post("/api/telemetry/coaching", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "ai_coaching" in data
        assert "corner_analysis" in data
        assert data["driver_number"] == 13
        assert data["reference_driver_number"] == 27

    @patch('app.api.routes.os.getenv')
    @patch('app.api.routes.ai_telemetry_coach.generate_coaching')
    def test_uses_snowflake_when_enabled(self, mock_coaching, mock_getenv, client):
        """
        Verify coaching endpoint uses Snowflake when enabled.

        Tests Snowflake integration path for coaching.
        """
        def getenv_side_effect(key, default=None):
            if key == "USE_SNOWFLAKE":
                return "true"
            if key.startswith("SNOWFLAKE_"):
                return "test-value"
            return os.getenv(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Mock Snowflake service
        with patch('app.api.routes.snowflake_service') as mock_service:
            sample_df = pd.DataFrame({
                "vehicle_number": [13, 13, 27, 27],
                "lap": [1, 1, 1, 1],
                "speed": [100, 105, 98, 103],
                "pbrake_f": [0, 0, 0, 0],
                "aps": [75, 80, 73, 78]
            })
            mock_service.get_telemetry_data.return_value = sample_df

            # Mock AI coaching
            mock_coaching.return_value = "Snowflake coaching response"

            request_data = {
                "driver_number": 13,
                "reference_driver_number": 27,
                "track_id": "barber",
                "race_num": 1
            }

            response = client.post("/api/telemetry/coaching", json=request_data)

            assert response.status_code == 200
            assert mock_service.get_telemetry_data.called

    @patch('app.api.routes.os.getenv')
    @patch('app.api.routes.pd.read_csv')
    @patch('app.api.routes.ai_telemetry_coach.generate_coaching')
    def test_falls_back_to_local_on_snowflake_error(
        self, mock_coaching, mock_read_csv, mock_getenv, client
    ):
        """
        Verify coaching falls back to local CSV if Snowflake fails.

        Critical for resilience during Snowflake outages.
        """
        def getenv_side_effect(key, default=None):
            if key == "USE_SNOWFLAKE":
                return "true"
            if key.startswith("SNOWFLAKE_"):
                return "test-value"
            return os.getenv(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Mock Snowflake to fail
        with patch('app.api.routes.snowflake_service') as mock_service:
            mock_service.get_telemetry_data.side_effect = Exception("Snowflake down")

            # Mock local CSV fallback
            sample_df = pd.DataFrame({
                "vehicle_number": [13, 13, 27, 27],
                "lap": [1, 1, 1, 1],
                "speed": [100, 105, 98, 103],
                "pbrake_f": [0, 0, 0, 0],
                "aps": [75, 80, 73, 78]
            })
            mock_read_csv.return_value = sample_df

            # Mock AI coaching
            mock_coaching.return_value = "Fallback coaching"

            request_data = {
                "driver_number": 13,
                "reference_driver_number": 27,
                "track_id": "barber",
                "race_num": 1
            }

            response = client.post("/api/telemetry/coaching", json=request_data)

            # Should succeed with fallback
            assert response.status_code == 200

    def test_returns_404_for_missing_driver(self, client):
        """
        Verify proper error handling for non-existent drivers.

        Should return 404 with clear error message.
        """
        request_data = {
            "driver_number": 999,  # Non-existent
            "reference_driver_number": 27,
            "track_id": "barber",
            "race_num": 1
        }

        response = client.post("/api/telemetry/coaching", json=request_data)

        assert response.status_code == 404
        assert "driver" in response.text.lower() or "not found" in response.text.lower()

    def test_validates_request_schema(self, client):
        """
        Verify request validation catches invalid inputs.

        Pydantic should validate required fields.
        """
        # Missing required fields
        invalid_request = {
            "driver_number": 13
            # Missing reference_driver_number, track_id, race_num
        }

        response = client.post("/api/telemetry/coaching", json=invalid_request)

        assert response.status_code == 422, "Should validate request schema"

    @patch('app.api.routes.os.getenv')
    @patch('app.api.routes.pd.read_csv')
    @patch('app.api.routes.ai_telemetry_coach.generate_coaching')
    def test_response_includes_all_required_fields(
        self, mock_coaching, mock_read_csv, mock_getenv, client
    ):
        """
        Verify response includes all expected fields.

        Frontend depends on complete response structure.
        """
        def getenv_side_effect(key, default=None):
            if key == "USE_SNOWFLAKE":
                return "false"
            return os.getenv(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Mock data
        sample_df = pd.DataFrame({
            "vehicle_number": [13, 13, 27, 27],
            "lap": [1, 1, 1, 1],
            "speed": [100, 105, 98, 103],
            "pbrake_f": [0, 0, 0, 0],
            "aps": [75, 80, 73, 78]
        })
        mock_read_csv.return_value = sample_df
        mock_coaching.return_value = "Test coaching"

        request_data = {
            "driver_number": 13,
            "reference_driver_number": 27,
            "track_id": "barber",
            "race_num": 1
        }

        response = client.post("/api/telemetry/coaching", json=request_data)

        if response.status_code == 200:
            data = response.json()

            # Check required fields
            required_fields = [
                "driver_number",
                "reference_driver_number",
                "track_name",
                "total_time_delta",
                "potential_time_gain",
                "corner_analysis",
                "ai_coaching",
                "telemetry_insights"
            ]

            for field in required_fields:
                assert field in data, f"Response missing required field: {field}"


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_endpoint_exists(self, client):
        """
        Verify health check endpoint is accessible.

        Used by monitoring systems.
        """
        response = client.get("/api/health")

        assert response.status_code == 200

    def test_health_returns_status(self, client):
        """
        Verify health check returns structured status.

        Should include operational metrics.
        """
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_includes_data_counts(self, client):
        """
        Verify health check includes loaded data counts.

        Helps diagnose data loading issues.
        """
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        assert "tracks_loaded" in data
        assert "drivers_loaded" in data
        assert isinstance(data["tracks_loaded"], int)
        assert isinstance(data["drivers_loaded"], int)


class TestErrorResponses:
    """Test error handling in telemetry endpoints."""

    def test_handles_malformed_json(self, client):
        """
        Verify API handles malformed JSON gracefully.

        Should return 422 validation error.
        """
        response = client.post(
            "/api/telemetry/coaching",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [422, 400]

    def test_returns_json_error_responses(self, client):
        """
        Verify all error responses are JSON formatted.

        Consistent error format helps frontend error handling.
        """
        # Test with invalid request
        response = client.post("/api/telemetry/coaching", json={})

        assert response.status_code in [422, 400, 404]
        assert response.headers["content-type"].startswith("application/json")

    @patch('app.api.routes.os.getenv')
    def test_handles_database_connection_error(self, mock_getenv, client):
        """
        Verify graceful handling of database errors.

        Should not crash, should return meaningful error.
        """
        def getenv_side_effect(key, default=None):
            if key == "USE_SNOWFLAKE":
                return "true"
            if key.startswith("SNOWFLAKE_"):
                return "test-value"
            return os.getenv(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Mock Snowflake and local fallback to both fail
        with patch('app.api.routes.snowflake_service') as mock_service:
            mock_service.get_drivers_with_telemetry.side_effect = Exception("Database error")

            with patch('app.api.routes.pd.read_csv') as mock_read_csv:
                mock_read_csv.side_effect = FileNotFoundError("No CSV files")

                response = client.get("/api/telemetry/drivers")

                # Should handle error (might be 200 with empty list or 500)
                assert response.status_code in [200, 500]

                if response.status_code == 200:
                    data = response.json()
                    # Should return valid JSON even on error
                    assert isinstance(data, dict)
