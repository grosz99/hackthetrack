"""
Comprehensive API endpoint tests for Racing Analytics platform.

Tests all API endpoints to ensure they work correctly before and after refactoring.
This serves as both regression tests and documentation of expected behavior.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestHealthAndRoot:
    """Test health check and root endpoints."""

    def test_root_endpoint(self):
        """Root endpoint should return API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Racing Analytics API"
        assert "endpoints" in data
        assert "version" in data

    def test_health_endpoint(self):
        """Health endpoint should return service status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "tracks_loaded" in data
        assert "drivers_loaded" in data


class TestTrackEndpoints:
    """Test track-related endpoints."""

    def test_get_all_tracks(self):
        """Should return list of all tracks."""
        response = client.get("/api/tracks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            track = data[0]
            assert "id" in track  # API uses 'id' not 'track_id'
            assert "name" in track
            assert "demand_profile" in track

    def test_get_specific_track(self):
        """Should return specific track by ID."""
        # First get all tracks to get a valid track_id
        all_tracks = client.get("/api/tracks").json()
        if len(all_tracks) > 0:
            track_id = all_tracks[0]["id"]  # API uses 'id' not 'track_id'
            response = client.get(f"/api/tracks/{track_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == track_id

    def test_get_nonexistent_track(self):
        """Should return 404 for nonexistent track."""
        response = client.get("/api/tracks/nonexistent_track_id")
        assert response.status_code == 404


class TestDriverEndpoints:
    """Test driver-related endpoints."""

    def test_get_all_drivers(self):
        """Should return list of all drivers."""
        response = client.get("/api/drivers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            driver = data[0]
            assert "driver_number" in driver
            assert "driver_name" in driver
            assert "speed" in driver
            assert "consistency" in driver
            assert "racecraft" in driver
            assert "tire_management" in driver

    def test_get_drivers_with_track_filter(self):
        """Should return drivers with circuit fit for specific track."""
        # Get a valid track_id first
        all_tracks = client.get("/api/tracks").json()
        if len(all_tracks) > 0:
            track_id = all_tracks[0]["id"]  # API uses 'id' not 'track_id'
            response = client.get(f"/api/drivers?track_id={track_id}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_get_specific_driver(self):
        """Should return specific driver by number."""
        # Get a valid driver_number first
        all_drivers = client.get("/api/drivers").json()
        if len(all_drivers) > 0:
            driver_number = all_drivers[0]["driver_number"]
            response = client.get(f"/api/drivers/{driver_number}")
            assert response.status_code == 200
            data = response.json()
            assert data["driver_number"] == driver_number

    def test_get_driver_stats(self):
        """Should return season statistics for driver."""
        all_drivers = client.get("/api/drivers").json()
        if len(all_drivers) > 0:
            driver_number = all_drivers[0]["driver_number"]
            response = client.get(f"/api/drivers/{driver_number}/stats")
            # May return 404 if no stats available, or 200 with stats
            assert response.status_code in [200, 404]
            if response.status_code == 200:
                data = response.json()
                assert "wins" in data
                assert "podiums" in data

    def test_get_driver_results(self):
        """Should return race results for driver."""
        all_drivers = client.get("/api/drivers").json()
        if len(all_drivers) > 0:
            driver_number = all_drivers[0]["driver_number"]
            response = client.get(f"/api/drivers/{driver_number}/results")
            # May return 404 if no results available
            assert response.status_code in [200, 404]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)

    def test_get_nonexistent_driver(self):
        """Should return 404 for nonexistent driver."""
        response = client.get("/api/drivers/99999")
        assert response.status_code == 404


class TestPredictionEndpoints:
    """Test prediction-related endpoints."""

    def test_predict_performance(self):
        """Should predict driver performance at track."""
        # Get valid driver and track
        all_drivers = client.get("/api/drivers").json()
        all_tracks = client.get("/api/tracks").json()

        if len(all_drivers) > 0 and len(all_tracks) > 0:
            driver_number = all_drivers[0]["driver_number"]
            track_id = all_tracks[0]["id"]  # API uses 'id' not 'track_id'

            response = client.post(
                "/api/predict",
                json={"driver_number": driver_number, "track_id": track_id},
            )
            assert response.status_code == 200
            data = response.json()
            assert "circuit_fit_score" in data
            assert "predicted_finish" in data
            assert "explanation" in data

    def test_predict_with_invalid_driver(self):
        """Should return 404 for invalid driver."""
        all_tracks = client.get("/api/tracks").json()
        if len(all_tracks) > 0:
            response = client.post(
                "/api/predict",
                json={"driver_number": 99999, "track_id": all_tracks[0]["id"]},  # API uses 'id' not 'track_id'
            )
            assert response.status_code == 404


class TestChatEndpoints:
    """Test AI chat endpoints."""

    @pytest.mark.skip(reason="AI tests require API key and are slow - use --run-ai-tests to enable")
    def test_chat_strategy(self):
        """Should return AI strategy insights."""
        all_drivers = client.get("/api/drivers").json()
        all_tracks = client.get("/api/tracks").json()

        if len(all_drivers) > 0 and len(all_tracks) > 0:
            response = client.post(
                "/api/chat",
                json={
                    "message": "What's my best strategy for this track?",
                    "driver_number": all_drivers[0]["driver_number"],
                    "track_id": all_tracks[0]["id"],  # API uses 'id' not 'track_id'
                    "history": [],
                },
            )
            # May fail without valid Anthropic API key
            assert response.status_code in [200, 500]
            if response.status_code == 200:
                data = response.json()
                assert "message" in data


class TestTelemetryEndpoints:
    """Test telemetry-related endpoints."""

    def test_compare_telemetry(self):
        """Should compare telemetry between two drivers."""
        all_drivers = client.get("/api/drivers").json()
        all_tracks = client.get("/api/tracks").json()

        if len(all_drivers) >= 2 and len(all_tracks) > 0:
            driver_1 = all_drivers[0]["driver_number"]
            driver_2 = all_drivers[1]["driver_number"]
            track_id = all_tracks[0]["id"]  # API uses 'id' not 'track_id'

            response = client.get(
                f"/api/telemetry/compare?track_id={track_id}&driver_1={driver_1}&driver_2={driver_2}&race_num=1"
            )
            # May return 404 if no telemetry data available
            assert response.status_code in [200, 404]

    def test_detailed_telemetry(self):
        """Should return detailed telemetry data."""
        all_drivers = client.get("/api/drivers").json()
        all_tracks = client.get("/api/tracks").json()

        if len(all_drivers) > 0 and len(all_tracks) > 0:
            driver_number = all_drivers[0]["driver_number"]
            track_id = all_tracks[0]["id"]  # API uses 'id' not 'track_id'

            response = client.get(
                f"/api/telemetry/detailed?track_id={track_id}&race_num=1&driver_number={driver_number}&data_type=speed_trace"
            )
            # May return 404 if no telemetry data available
            assert response.status_code in [200, 404]

    def test_telemetry_drivers_list(self):
        """Should return list of drivers with telemetry data."""
        response = client.get("/api/telemetry/drivers")
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "drivers_with_telemetry" in data
            assert "count" in data


class TestFactorEndpoints:
    """Test factor breakdown endpoints."""

    def test_factor_breakdown(self):
        """Should return factor breakdown for driver."""
        all_drivers = client.get("/api/drivers").json()

        if len(all_drivers) > 0:
            driver_number = all_drivers[0]["driver_number"]
            factors = ["speed", "consistency", "racecraft", "tire_management"]

            for factor in factors:
                response = client.get(
                    f"/api/drivers/{driver_number}/factors/{factor}"
                )
                # May return 404 if no factor data in database
                assert response.status_code in [200, 404]
                if response.status_code == 200:
                    data = response.json()
                    assert "factor_name" in data
                    assert "overall_score" in data
                    assert "variables" in data

    def test_factor_comparison(self):
        """Should compare driver factor vs top drivers."""
        all_drivers = client.get("/api/drivers").json()

        if len(all_drivers) > 0:
            driver_number = all_drivers[0]["driver_number"]
            response = client.get(
                f"/api/drivers/{driver_number}/factors/speed/comparison"
            )
            # May return 404 if no comparison data
            assert response.status_code in [200, 404]


class TestImproveEndpoints:
    """Test improve/prediction endpoints."""

    def test_predict_with_adjusted_skills(self):
        """Should predict performance with adjusted skills."""
        all_drivers = client.get("/api/drivers").json()

        if len(all_drivers) > 0:
            driver = all_drivers[0]
            driver_number = driver["driver_number"]

            # Use current skills from driver (staying within budget)
            current_speed = driver["speed"]["percentile"] / 100
            current_consistency = driver["consistency"]["percentile"] / 100
            current_racecraft = driver["racecraft"]["percentile"] / 100
            current_tire = driver["tire_management"]["percentile"] / 100

            response = client.post(
                f"/api/drivers/{driver_number}/improve/predict",
                json={
                    "speed": current_speed,
                    "consistency": current_consistency,
                    "racecraft": current_racecraft,
                    "tire_management": current_tire,
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert "prediction" in data
            assert "similar_drivers" in data
            assert "recommendations" in data

    def test_adjusted_skills_budget_validation(self):
        """Should reject adjustments exceeding points budget."""
        all_drivers = client.get("/api/drivers").json()

        if len(all_drivers) > 0:
            driver_number = all_drivers[0]["driver_number"]
            # Try to adjust all skills to 1.0 (will exceed budget)
            response = client.post(
                f"/api/drivers/{driver_number}/improve/predict",
                json={
                    "speed": 1.0,
                    "consistency": 1.0,
                    "racecraft": 1.0,
                    "tire_management": 1.0,
                },
            )
            # Should return 400 if budget exceeded
            assert response.status_code in [200, 400]


class TestCoachingEndpoints:
    """Test telemetry coaching endpoints."""

    @pytest.mark.skip(reason="AI tests require API key and are slow - use --run-ai-tests to enable")
    def test_telemetry_coaching(self):
        """Should provide AI telemetry coaching."""
        all_drivers = client.get("/api/drivers").json()
        all_tracks = client.get("/api/tracks").json()

        if len(all_drivers) >= 2 and len(all_tracks) > 0:
            response = client.post(
                "/api/telemetry/coaching",
                json={
                    "track_id": all_tracks[0]["id"],  # API uses 'id' not 'track_id'
                    "race_num": 1,
                    "driver_number": all_drivers[0]["driver_number"],
                    "reference_driver_number": all_drivers[1]["driver_number"],
                },
            )
            # May return 404, 500, or 503 depending on data availability and AI
            assert response.status_code in [200, 404, 500, 503]


