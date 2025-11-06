"""
Deployment validation tests.

Tests that can be run against a deployed instance to ensure everything works.
These tests validate the full stack: frontend → backend → data sources.
"""

import pytest
import os
import requests
from typing import Optional


def get_api_base_url() -> str:
    """Get API base URL from environment or use localhost."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")


def get_frontend_url() -> str:
    """Get frontend URL from environment or use localhost."""
    return os.getenv("FRONTEND_URL", "http://localhost:5173")


class TestDeploymentHealth:
    """Test basic deployment health checks."""

    def test_backend_is_reachable(self):
        """Backend should be reachable and return root info."""
        url = get_api_base_url()
        response = requests.get(f"{url}/", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data

    def test_health_endpoint_responds(self):
        """Health endpoint should return service status."""
        url = get_api_base_url()
        response = requests.get(f"{url}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        # Check data sources are accessible
        assert "data_sources" in data or "tracks_loaded" in data

    def test_cors_headers_present(self):
        """CORS headers should be configured for frontend."""
        url = get_api_base_url()
        frontend_url = get_frontend_url()

        response = requests.options(
            f"{url}/api/health",
            headers={"Origin": frontend_url, "Access-Control-Request-Method": "GET"},
            timeout=10,
        )
        # Check CORS headers
        assert (
            "access-control-allow-origin" in response.headers
            or response.status_code == 200
        )


class TestCriticalEndpoints:
    """Test critical endpoints that frontend depends on."""

    def test_drivers_endpoint_works(self):
        """Drivers endpoint should return data."""
        url = get_api_base_url()
        response = requests.get(f"{url}/api/drivers", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should have at least one driver"

    def test_tracks_endpoint_works(self):
        """Tracks endpoint should return data."""
        url = get_api_base_url()
        response = requests.get(f"{url}/api/tracks", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should have at least one track"

    def test_prediction_endpoint_works(self):
        """Prediction endpoint should work with valid data."""
        url = get_api_base_url()

        # Get valid driver and track
        drivers = requests.get(f"{url}/api/drivers", timeout=10).json()
        tracks = requests.get(f"{url}/api/tracks", timeout=10).json()

        if len(drivers) > 0 and len(tracks) > 0:
            response = requests.post(
                f"{url}/api/predict",
                json={
                    "driver_number": drivers[0]["driver_number"],
                    "track_id": tracks[0]["track_id"],
                },
                timeout=10,
            )
            assert response.status_code == 200
            data = response.json()
            assert "circuit_fit_score" in data
            assert "predicted_finish" in data


class TestDataSources:
    """Test data source connectivity."""

    def test_snowflake_connection(self):
        """Snowflake should be accessible (via health check)."""
        url = get_api_base_url()
        response = requests.get(f"{url}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()

        # Check if data sources are reported
        if "data_sources" in data:
            # If Snowflake is configured, check its status
            snowflake_status = data["data_sources"].get("snowflake", {})
            # Snowflake can be unavailable (degraded mode), but health should report it
            assert snowflake_status.get("status") in [
                "healthy",
                "degraded",
                "unavailable",
            ]

    def test_local_data_fallback_works(self):
        """Local JSON data should be available as fallback."""
        url = get_api_base_url()
        response = requests.get(f"{url}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()

        # Should have data loaded from somewhere
        assert data.get("tracks_loaded", 0) > 0
        assert data.get("drivers_loaded", 0) > 0


class TestPerformance:
    """Test performance requirements."""

    def test_health_check_responds_quickly(self):
        """Health check should respond in under 2 seconds."""
        url = get_api_base_url()
        import time

        start = time.time()
        response = requests.get(f"{url}/api/health", timeout=5)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0, f"Health check took {elapsed:.2f}s (should be < 2s)"

    def test_drivers_endpoint_responds_quickly(self):
        """Drivers endpoint should respond in under 5 seconds."""
        url = get_api_base_url()
        import time

        start = time.time()
        response = requests.get(f"{url}/api/drivers", timeout=10)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 5.0, f"Drivers endpoint took {elapsed:.2f}s (should be < 5s)"


class TestErrorHandling:
    """Test error handling."""

    def test_404_for_nonexistent_endpoint(self):
        """Should return 404 for nonexistent endpoints."""
        url = get_api_base_url()
        response = requests.get(f"{url}/api/nonexistent", timeout=10)
        assert response.status_code == 404

    def test_404_for_invalid_driver(self):
        """Should return 404 for invalid driver."""
        url = get_api_base_url()
        response = requests.get(f"{url}/api/drivers/99999", timeout=10)
        assert response.status_code == 404

    def test_validation_error_for_invalid_input(self):
        """Should return validation error for invalid prediction input."""
        url = get_api_base_url()
        response = requests.post(
            f"{url}/api/predict",
            json={"driver_number": "invalid", "track_id": "invalid"},
            timeout=10,
        )
        # Should return 422 (validation error) or 404 (not found)
        assert response.status_code in [400, 404, 422]


class TestFrontendIntegration:
    """Test frontend integration points."""

    @pytest.mark.skipif(
        not os.getenv("FRONTEND_URL"), reason="Frontend URL not configured"
    )
    def test_frontend_is_reachable(self):
        """Frontend should be reachable."""
        url = get_frontend_url()
        response = requests.get(url, timeout=10)
        assert response.status_code == 200

    def test_api_docs_accessible(self):
        """API documentation should be accessible."""
        url = get_api_base_url()
        response = requests.get(f"{url}/docs", timeout=10)
        assert response.status_code == 200


# Pytest markers
pytestmark = pytest.mark.integration


if __name__ == "__main__":
    # Can be run standalone for quick deployment validation
    print("Running deployment validation tests...")
    print(f"API URL: {get_api_base_url()}")
    print(f"Frontend URL: {get_frontend_url()}")
    pytest.main([__file__, "-v"])
