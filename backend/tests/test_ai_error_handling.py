"""
AI Service Error Handling Tests

Tests that AI services handle errors gracefully and return appropriate HTTP responses.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
import anthropic


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    with patch('anthropic.Anthropic') as mock_client:
        yield mock_client


def test_ai_strategy_handles_api_error(mock_anthropic_client):
    """Test that AIStrategyService handles Anthropic API errors gracefully."""
    from app.services.ai_strategy import AIStrategyService
    from models import Driver, Track, ChatMessage

    # Mock the client to raise an API error
    mock_instance = mock_anthropic_client.return_value
    mock_instance.messages.create.side_effect = anthropic.APIError("Rate limit exceeded")

    service = AIStrategyService()

    # Create mock objects
    driver = Mock(spec=Driver)
    driver.driver_number = 13
    driver.overall_score = 85.0
    driver.speed = Mock(score=80.0, percentile=75, z_score=0.5)
    driver.consistency = Mock(score=85.0, percentile=80, z_score=0.8)
    driver.racecraft = Mock(score=90.0, percentile=85, z_score=1.0)
    driver.tire_management = Mock(score=75.0, percentile=70, z_score=0.3)
    driver.stats = Mock(races_completed=10, average_finish=5.2, best_finish=1, worst_finish=12)
    driver.circuit_fits = {"barber": 82.5}

    track = Mock(spec=Track)
    track.name = "Barber Motorsports Park"
    track.location = "Alabama"
    track.length_miles = 2.38
    track.id = "barber"
    track.demand_profile = Mock(speed=85.0, consistency=90.0, racecraft=75.0, tire_management=70.0)

    # Should raise HTTPException with 503 status
    with pytest.raises(HTTPException) as exc_info:
        service.get_strategy_insights(
            message="How should I approach this race?",
            driver=driver,
            track=track,
            history=[]
        )

    assert exc_info.value.status_code == 503
    assert "temporarily unavailable" in exc_info.value.detail.lower()


def test_ai_strategy_handles_unexpected_error(mock_anthropic_client):
    """Test that AIStrategyService handles unexpected errors."""
    from app.services.ai_strategy import AIStrategyService
    from models import Driver, Track

    # Mock the client to raise unexpected error
    mock_instance = mock_anthropic_client.return_value
    mock_instance.messages.create.side_effect = ValueError("Unexpected error")

    service = AIStrategyService()

    driver = Mock(spec=Driver)
    driver.driver_number = 13
    driver.overall_score = 85.0
    driver.speed = Mock(score=80.0, percentile=75, z_score=0.5)
    driver.consistency = Mock(score=85.0, percentile=80, z_score=0.8)
    driver.racecraft = Mock(score=90.0, percentile=85, z_score=1.0)
    driver.tire_management = Mock(score=75.0, percentile=70, z_score=0.3)
    driver.stats = Mock(races_completed=10, average_finish=5.2, best_finish=1, worst_finish=12)
    driver.circuit_fits = {"barber": 82.5}

    track = Mock(spec=Track)
    track.name = "Barber Motorsports Park"
    track.location = "Alabama"
    track.length_miles = 2.38
    track.id = "barber"
    track.demand_profile = Mock(speed=85.0, consistency=90.0, racecraft=75.0, tire_management=70.0)

    # Should raise HTTPException with 500 status
    with pytest.raises(HTTPException) as exc_info:
        service.get_strategy_insights(
            message="How should I approach this race?",
            driver=driver,
            track=track,
            history=[]
        )

    assert exc_info.value.status_code == 500
    assert "unable" in exc_info.value.detail.lower()


def test_ai_telemetry_coach_handles_api_error(mock_anthropic_client):
    """Test that AITelemetryCoach handles API errors gracefully."""
    from app.services.ai_telemetry_coach import AITelemetryCoach

    # Mock the client to raise an API error
    mock_instance = mock_anthropic_client.return_value
    mock_instance.messages.create.side_effect = anthropic.APIError("Service unavailable")

    coach = AITelemetryCoach()

    telemetry_insights = {
        'total_delta': '0.523',
        'potential_gain': '0.523',
        'braking_pattern': 'Braking 15m earlier than reference',
        'throttle_pattern': 'Late throttle application',
        'speed_pattern': 'Lower apex speeds',
        'steering_pattern': 'More steering input variation'
    }

    corner_analysis = [
        {
            'corner_number': 1,
            'corner_name': 'Turn 1',
            'time_loss': 0.125,
            'driver_apex_speed': 92.0,
            'reference_apex_speed': 98.0,
            'apex_speed_delta': -6.0,
            'focus_area': 'Braking point'
        }
    ]

    # Should raise HTTPException with 503 status
    with pytest.raises(HTTPException) as exc_info:
        coach.generate_coaching(
            driver_number=13,
            reference_driver_number=7,
            track_name="Barber Motorsports Park",
            telemetry_insights=telemetry_insights,
            corner_analysis=corner_analysis
        )

    assert exc_info.value.status_code == 503
    assert "telemetry coaching" in exc_info.value.detail.lower()


def test_ai_skill_coach_handles_api_error(mock_anthropic_client):
    """Test that AISkillCoach handles API errors gracefully."""
    from app.services.ai_skill_coach import AISkillCoach

    # Mock the client to raise an API error
    mock_instance = mock_anthropic_client.return_value
    mock_instance.messages.create.side_effect = anthropic.APIError("Timeout")

    coach = AISkillCoach()

    variables = [
        {"name": "Qualifying Pace", "value": 85.2, "percentile": 78},
        {"name": "Best Lap", "value": 92.1, "percentile": 85}
    ]

    # Should raise HTTPException with 503 status
    with pytest.raises(HTTPException) as exc_info:
        coach.generate_factor_coaching(
            driver_number=13,
            factor_name="speed",
            variables=variables,
            overall_percentile=80.0,
            rank_among_drivers=7,
            total_drivers=34,
            race_results=[],
            driver_name="Driver #13"
        )

    assert exc_info.value.status_code == 503
    assert "skill coaching" in exc_info.value.detail.lower()


def test_ai_services_log_errors_without_exposing_details():
    """Test that AI services log errors internally without exposing them to users."""
    from app.services.ai_strategy import AIStrategyService

    with patch('app.services.ai_strategy.logger') as mock_logger:
        with patch('anthropic.Anthropic') as mock_client:
            # Mock API error
            mock_instance = mock_client.return_value
            mock_instance.messages.create.side_effect = anthropic.APIError("Internal API error with sensitive data")

            service = AIStrategyService()

            driver = Mock()
            driver.driver_number = 13
            driver.overall_score = 85.0
            driver.speed = Mock(score=80.0, percentile=75, z_score=0.5)
            driver.consistency = Mock(score=85.0, percentile=80, z_score=0.8)
            driver.racecraft = Mock(score=90.0, percentile=85, z_score=1.0)
            driver.tire_management = Mock(score=75.0, percentile=70, z_score=0.3)
            driver.stats = Mock(races_completed=10, average_finish=5.2, best_finish=1, worst_finish=12)
            driver.circuit_fits = {"barber": 82.5}

            track = Mock()
            track.name = "Barber"
            track.location = "Alabama"
            track.length_miles = 2.38
            track.id = "barber"
            track.demand_profile = Mock(speed=85.0, consistency=90.0, racecraft=75.0, tire_management=70.0)

            try:
                service.get_strategy_insights("test", driver, track, [])
            except HTTPException as e:
                # Error logged internally
                assert mock_logger.exception.called

                # But user sees sanitized message
                assert "sensitive data" not in e.detail.lower()
                assert "temporarily unavailable" in e.detail.lower()


def test_successful_ai_response_does_not_raise_error(mock_anthropic_client):
    """Test that successful AI responses work correctly."""
    from app.services.ai_strategy import AIStrategyService
    from models import Driver, Track

    # Mock successful response
    mock_instance = mock_anthropic_client.return_value
    mock_response = Mock()
    mock_response.content = [Mock(text="Here is your strategy advice...")]
    mock_instance.messages.create.return_value = mock_response

    service = AIStrategyService()

    driver = Mock(spec=Driver)
    driver.driver_number = 13
    driver.overall_score = 85.0
    driver.speed = Mock(score=80.0, percentile=75, z_score=0.5)
    driver.consistency = Mock(score=85.0, percentile=80, z_score=0.8)
    driver.racecraft = Mock(score=90.0, percentile=85, z_score=1.0)
    driver.tire_management = Mock(score=75.0, percentile=70, z_score=0.3)
    driver.stats = Mock(races_completed=10, average_finish=5.2, best_finish=1, worst_finish=12)
    driver.circuit_fits = {"barber": 82.5}

    track = Mock(spec=Track)
    track.name = "Barber Motorsports Park"
    track.location = "Alabama"
    track.length_miles = 2.38
    track.id = "barber"
    track.demand_profile = Mock(speed=85.0, consistency=90.0, racecraft=75.0, tire_management=70.0)

    # Should not raise any exception
    result, suggestions = service.get_strategy_insights(
        message="How should I approach this race?",
        driver=driver,
        track=track,
        history=[]
    )

    assert result == "Here is your strategy advice..."
    assert isinstance(suggestions, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
