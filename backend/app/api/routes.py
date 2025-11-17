"""
API routes for Racing Analytics platform.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import pandas as pd
import logging

logger = logging.getLogger(__name__)
from app.utils.errors import NotFoundError, ValidationError
from models import (
    Track,
    Driver,
    CircuitFitPrediction,
    ChatRequest,
    ChatResponse,
    TelemetryComparison,
    LapData,
    SeasonStats,
    RaceResult,
    FactorVariable,
    FactorBreakdownResponse,
    DriverFactorComparison,
    FactorComparisonResponse,
    AdjustedSkills,
    PredictionWithUncertainty,
    FindSimilarDriverRequest,
    SimilarDriverMatch,
    ImprovementRecommendation,
    ImprovePredictionResponse,
    TelemetryCoachingRequest,
    TelemetryCoachingResponse,
    CornerAnalysis,
    PracticePlanRequest,
    PracticePlanResponse,
    WeeklyMilestone,
    SkillPriority,
    FinalPrediction,
    SkillGapItem,
    SkillGapAnalysisResponse,
    CoachRecommendation,
    CoachRecommendationsResponse,
    ProjectedDriverRanking,
    ProjectedRankingsResponse,
    TrackImprovementFocus,
    TrackImprovementPlanResponse,
    FactorCoachingResponse,
)
from ..services.data_loader import data_loader
from ..services.ai_strategy import ai_service
from ..services.ai_telemetry_coach import ai_telemetry_coach
from ..services.ai_skill_coach import ai_skill_coach

# No prefix here - it's added by main.py when including the router
router = APIRouter(tags=["racing"])


# ============================================================================
# TRACK ENDPOINTS
# ============================================================================


@router.get("/tracks", response_model=List[Track])
async def get_all_tracks():
    """Get all available tracks with demand profiles."""
    tracks = data_loader.get_all_tracks()
    if not tracks:
        raise HTTPException(status_code=404, detail="No tracks found")
    return tracks


@router.get("/tracks/{track_id}", response_model=Track)
async def get_track(track_id: str):
    """Get specific track by ID."""
    track = data_loader.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail=f"Track {track_id} not found")
    return track


# ============================================================================
# DRIVER ENDPOINTS
# ============================================================================


@router.get("/drivers", response_model=List[Driver])
async def get_all_drivers(
    track_id: Optional[str] = Query(
        None, description="Filter drivers by track to include circuit fit"
    )
):
    """
    Get all drivers with skill profiles and season stats.

    If track_id is provided, includes circuit fit scores for that track.
    """
    drivers = data_loader.get_all_drivers()
    if not drivers:
        raise HTTPException(status_code=404, detail="No drivers found")

    if track_id:
        # Add circuit fit calculations for the specified track
        for driver in drivers:
            fit_score = data_loader.calculate_circuit_fit(
                driver.driver_number, track_id
            )
            if fit_score is not None:
                driver.circuit_fits[track_id] = fit_score

    return drivers


@router.get("/drivers/{driver_number}", response_model=Driver)
async def get_driver(driver_number: int):
    """Get specific driver by number."""
    driver = data_loader.get_driver(driver_number)
    if not driver:
        raise HTTPException(
            status_code=404, detail=f"Driver {driver_number} not found"
        )
    return driver


@router.get("/drivers/{driver_number}/stats", response_model=SeasonStats)
async def get_driver_season_stats(driver_number: int):
    """
    Get season statistics for a driver.

    Calculates wins, podiums, top 5/10, poles, DNFs, and averages from race results.
    """
    stats = data_loader.get_season_stats(driver_number)
    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"No season stats found for driver {driver_number}",
        )
    return stats


@router.get("/drivers/{driver_number}/results", response_model=List[RaceResult])
async def get_driver_race_results(driver_number: int):
    """
    Get all race results for a driver for trending/historical data.

    Returns race-by-race results ordered by round and race number.
    """
    results = data_loader.get_race_results(driver_number)
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No race results found for driver {driver_number}",
        )
    return results


@router.get("/drivers/{driver_number}/match")
async def get_similar_drivers(
    driver_number: int,
    adjusted_skills: Optional[dict] = None,
    top_n: int = Query(5, ge=1, le=10, description="Number of similar drivers to return")
):
    """
    Find similar drivers based on 4-factor profile using cosine similarity.

    This endpoint supports two modes:
    1. **Current Profile Mode** (no adjusted_skills): Finds drivers similar to current profile
    2. **Adjusted Profile Mode** (with adjusted_skills): Finds drivers matching hypothetical adjusted profile

    Args:
        driver_number: Target driver number
        adjusted_skills: Optional dict with adjusted factor values (0-100 scale)
                        Format: {"speed": 85, "consistency": 75, "racecraft": 80, "tire_management": 70}
        top_n: Number of similar drivers to return (default: 5)

    Returns:
        List of similar drivers with match percentage and shared attributes

    Algorithm:
        Uses cosine similarity on 4-factor vectors for robust matching.
        Formula: similarity = (A · B) / (||A|| × ||B||)
        Where A and B are 4-dimensional vectors [speed, consistency, racecraft, tire_mgmt]
    """
    import numpy as np

    # Get target driver
    driver = data_loader.get_driver(driver_number)
    if not driver:
        raise HTTPException(
            status_code=404,
            detail=f"Driver {driver_number} not found"
        )

    # Build target vector (either current or adjusted profile)
    if adjusted_skills:
        # Use adjusted skills from slider
        target_vector = np.array([
            adjusted_skills.get('speed', driver.speed.percentile),
            adjusted_skills.get('consistency', driver.consistency.percentile),
            adjusted_skills.get('racecraft', driver.racecraft.percentile),
            adjusted_skills.get('tire_management', driver.tire_management.percentile)
        ])
    else:
        # Use current driver profile
        target_vector = np.array([
            driver.speed.percentile,
            driver.consistency.percentile,
            driver.racecraft.percentile,
            driver.tire_management.percentile
        ])

    # Get all other drivers
    all_drivers = data_loader.get_all_drivers()
    similarities = []

    for other_driver in all_drivers:
        if other_driver.driver_number == driver_number:
            continue

        # Build comparison vector
        other_vector = np.array([
            other_driver.speed.percentile,
            other_driver.consistency.percentile,
            other_driver.racecraft.percentile,
            other_driver.tire_management.percentile
        ])

        # Calculate cosine similarity
        dot_product = np.dot(target_vector, other_vector)
        magnitude_target = np.linalg.norm(target_vector)
        magnitude_other = np.linalg.norm(other_vector)

        if magnitude_target == 0 or magnitude_other == 0:
            cosine_sim = 0
        else:
            cosine_sim = dot_product / (magnitude_target * magnitude_other)

        # Convert to 0-100 percentage
        match_percentage = round(cosine_sim * 100, 1)

        # Identify shared strengths (factors within 10 points)
        shared_attributes = []
        factor_pairs = [
            ('speed', driver.speed.percentile if not adjusted_skills else adjusted_skills.get('speed'), other_driver.speed.percentile),
            ('consistency', driver.consistency.percentile if not adjusted_skills else adjusted_skills.get('consistency'), other_driver.consistency.percentile),
            ('racecraft', driver.racecraft.percentile if not adjusted_skills else adjusted_skills.get('racecraft'), other_driver.racecraft.percentile),
            ('tire_management', driver.tire_management.percentile if not adjusted_skills else adjusted_skills.get('tire_management'), other_driver.tire_management.percentile)
        ]

        for factor_name, target_val, other_val in factor_pairs:
            if abs(target_val - other_val) <= 10:
                # Both strong in this factor (both > 70)
                if target_val >= 70 and other_val >= 70:
                    shared_attributes.append(f"High {factor_name.replace('_', ' ')}")
                # Both moderate/weak (similar but < 70)
                elif abs(target_val - other_val) <= 5:
                    shared_attributes.append(f"Similar {factor_name.replace('_', ' ')}")

        similarities.append({
            'driver_number': other_driver.driver_number,
            'driver_name': other_driver.driver_name,
            'match_percentage': match_percentage,
            'shared_attributes': shared_attributes[:3],  # Top 3 shared attributes
            'overall_score': other_driver.overall_score,
            'factors': {
                'speed': other_driver.speed.percentile,
                'consistency': other_driver.consistency.percentile,
                'racecraft': other_driver.racecraft.percentile,
                'tire_management': other_driver.tire_management.percentile
            }
        })

    # Sort by match percentage descending
    similarities.sort(key=lambda x: x['match_percentage'], reverse=True)

    # Return top N matches
    return {
        'target_driver': driver_number,
        'adjusted_profile': adjusted_skills is not None,
        'similar_drivers': similarities[:top_n]
    }


# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================


class PredictRequest(BaseModel):
    """Request model for performance prediction."""
    driver_number: int
    track_id: str

@router.post("/predict", response_model=CircuitFitPrediction)
async def predict_performance(request: PredictRequest):
    """
    Predict driver performance at specific track.

    Returns circuit fit score and predicted finish position using the 4-factor model.
    """
    driver = data_loader.get_driver(request.driver_number)
    track = data_loader.get_track(request.track_id)

    if not driver:
        raise HTTPException(
            status_code=404, detail=f"Driver {request.driver_number} not found"
        )
    if not track:
        raise HTTPException(status_code=404, detail=f"Track {request.track_id} not found")

    # Calculate circuit fit
    fit_score = data_loader.calculate_circuit_fit(request.driver_number, request.track_id)
    if fit_score is None:
        raise HTTPException(
            status_code=500, detail="Failed to calculate circuit fit"
        )

    # Predict finish position
    predicted_finish = data_loader.predict_finish_position(request.driver_number, request.track_id)
    if predicted_finish is None:
        raise HTTPException(
            status_code=500, detail="Failed to predict finish position"
        )

    # Generate explanation
    explanation = _generate_prediction_explanation(driver, track, fit_score)

    return CircuitFitPrediction(
        driver_number=request.driver_number,
        track_id=request.track_id,
        circuit_fit_score=fit_score,
        predicted_finish=predicted_finish,
        explanation=explanation,
    )


def _generate_prediction_explanation(
    driver: Driver, track: Track, fit_score: float
) -> str:
    """Generate human-readable explanation of prediction."""

    # Identify strongest and weakest factors
    factors = {
        "Speed": driver.speed.score,
        "Consistency": driver.consistency.score,
        "Racecraft": driver.racecraft.score,
        "Tire Management": driver.tire_management.score,
    }
    strongest = max(factors, key=factors.get)
    weakest = min(factors, key=factors.get)

    # Track demands
    demands = {
        "Speed": track.demand_profile.speed,
        "Consistency": track.demand_profile.consistency,
        "Racecraft": track.demand_profile.racecraft,
        "Tire Management": track.demand_profile.tire_management,
    }
    highest_demand = max(demands, key=demands.get)

    explanation = f"Circuit fit: {fit_score:.0f}/100. "
    explanation += f"Your strongest skill is {strongest} ({factors[strongest]:.0f}/100), "
    explanation += f"while {track.name} demands {highest_demand} most ({demands[highest_demand]:.0f}/100). "

    if fit_score >= 75:
        explanation += "This is an excellent track match for your skill profile!"
    elif fit_score >= 50:
        explanation += (
            f"Consider focusing on {highest_demand} to maximize performance here."
        )
    else:
        explanation += f"This track challenges your {weakest} ({factors[weakest]:.0f}/100) - an area to work on."

    return explanation


# ============================================================================
# AI CHATBOT ENDPOINTS
# ============================================================================


@router.post("/chat", response_model=ChatResponse)
async def chat_strategy(request: ChatRequest):
    """
    Get AI-powered racing strategy insights.

    Provides contextual advice based on driver skills and track demands.
    """
    driver = data_loader.get_driver(request.driver_number)
    track = data_loader.get_track(request.track_id)

    if not driver:
        raise HTTPException(
            status_code=404, detail=f"Driver {request.driver_number} not found"
        )
    if not track:
        raise HTTPException(
            status_code=404, detail=f"Track {request.track_id} not found"
        )

    try:
        response_message, suggested_questions = ai_service.get_strategy_insights(
            message=request.message,
            driver=driver,
            track=track,
            history=request.history,
        )

        return ChatResponse(
            message=response_message, suggested_questions=suggested_questions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


# ============================================================================
# TELEMETRY ENDPOINTS
# ============================================================================


@router.get("/telemetry/compare", response_model=TelemetryComparison)
async def compare_telemetry(
    track_id: str,
    driver_1: int,
    driver_2: int,
    race_num: int = Query(1, ge=1, le=2, description="Race number (1 or 2)"),
):
    """
    Compare lap-by-lap telemetry between two drivers.

    Returns sector times, lap times, and delta analysis.
    Uses CSV data files (Snowflake removed to simplify deployment).
    """
    # Load from CSV data files
    lap_data = data_loader.get_lap_data(track_id, race_num)

    if lap_data is None or lap_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No lap data found for {track_id} race {race_num}",
        )

    # Filter for each driver (green flag laps only)
    # FLAG_AT_FL values: "GF" = Green Flag (normal lap), "FCY" = caution lap
    if "FLAG_AT_FL" in lap_data.columns:
        # Apply green flag filter
        driver_1_data = lap_data[
            (lap_data["VEHICLE_NUMBER"] == driver_1) & (lap_data["FLAG_AT_FL"] == "GF")
        ]
        driver_2_data = lap_data[
            (lap_data["VEHICLE_NUMBER"] == driver_2) & (lap_data["FLAG_AT_FL"] == "GF")
        ]
    else:
        # No flag data available, use all laps
        driver_1_data = lap_data[lap_data["VEHICLE_NUMBER"] == driver_1]
        driver_2_data = lap_data[lap_data["VEHICLE_NUMBER"] == driver_2]

    if driver_1_data.empty or driver_2_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Insufficient data for drivers {driver_1} and/or {driver_2}",
        )

    # Convert to LapData objects
    driver_1_laps = _convert_to_lap_data(driver_1_data)
    driver_2_laps = _convert_to_lap_data(driver_2_data)

    # Calculate sector deltas (using best laps)
    sector_deltas = _calculate_sector_deltas(driver_1_data, driver_2_data)

    # Generate insights
    insights = _generate_telemetry_insights(
        driver_1, driver_2, sector_deltas, driver_1_data, driver_2_data
    )

    return TelemetryComparison(
        track_id=track_id,
        driver_1=driver_1,
        driver_2=driver_2,
        driver_1_laps=driver_1_laps[:50],  # Limit to 50 laps for performance
        driver_2_laps=driver_2_laps[:50],
        sector_deltas=sector_deltas,
        insights=insights,
    )


def _convert_to_lap_data(df) -> List[LapData]:
    """Convert DataFrame to list of LapData objects."""
    laps = []
    for _, row in df.iterrows():
        laps.append(
            LapData(
                lap_number=int(row["LAP_NUMBER"]),
                lap_time=float(row.get("LAP_TIME", 0)),
                sector_1=float(row.get("S1_SECONDS", 0)),
                sector_2=float(row.get("S2_SECONDS", 0)),
                sector_3=float(row.get("S3_SECONDS", 0)),
                flag_status=str(row.get("FLAG_AT_FL", "")),
            )
        )
    return laps


def _calculate_sector_deltas(df1, df2) -> dict:
    """Calculate average sector time deltas between two drivers."""

    # Get best laps for each driver
    best_lap_1 = df1.loc[df1["LAP_TIME"].idxmin()]
    best_lap_2 = df2.loc[df2["LAP_TIME"].idxmin()]

    return {
        "sector_1": float(best_lap_1["S1_SECONDS"] - best_lap_2["S1_SECONDS"]),
        "sector_2": float(best_lap_1["S2_SECONDS"] - best_lap_2["S2_SECONDS"]),
        "sector_3": float(best_lap_1["S3_SECONDS"] - best_lap_2["S3_SECONDS"]),
        "total": float(best_lap_1["LAP_TIME"] - best_lap_2["LAP_TIME"]),
    }


def _generate_telemetry_insights(
    driver_1: int, driver_2: int, sector_deltas: dict, df1, df2
) -> List[str]:
    """Generate insights from telemetry comparison."""
    insights = []

    total_delta = sector_deltas["total"]

    if abs(total_delta) < 0.1:
        insights.append(
            f"Drivers #{driver_1} and #{driver_2} are extremely closely matched (within 0.1s)!"
        )
    elif total_delta > 0:
        insights.append(
            f"Driver #{driver_2} is faster overall by {abs(total_delta):.3f}s per lap"
        )
    else:
        insights.append(
            f"Driver #{driver_1} is faster overall by {abs(total_delta):.3f}s per lap"
        )

    # Sector-specific insights
    for sector in ["sector_1", "sector_2", "sector_3"]:
        delta = sector_deltas[sector]
        sector_num = sector.split("_")[1]

        if abs(delta) > 0.1:  # Significant delta
            if delta > 0:
                insights.append(
                    f"You lose {abs(delta):.3f}s in Sector {sector_num} - focus on this area"
                )
            else:
                insights.append(
                    f"You gain {abs(delta):.3f}s in Sector {sector_num} - this is a strength!"
                )

    # Consistency insights
    cv1 = df1["LAP_TIME"].std() / df1["LAP_TIME"].mean()
    cv2 = df2["LAP_TIME"].std() / df2["LAP_TIME"].mean()

    if cv1 < cv2:
        insights.append(
            f"Driver #{driver_1} is more consistent (CV: {cv1:.3f} vs {cv2:.3f})"
        )
    else:
        insights.append(
            f"Driver #{driver_2} is more consistent (CV: {cv2:.3f} vs {cv1:.3f})"
        )

    return insights


# ============================================================================
# HEALTH CHECK
# ============================================================================


@router.get("/health")
async def health_check():
    """
    Health check endpoint - simple and fast.

    Returns service health and basic data availability.
    """
    # Snowflake removed - using JSON files only

    return {
        "status": "healthy",
        "tracks_loaded": len(data_loader.tracks),
        "drivers_loaded": len(data_loader.drivers),
        "data_source": "JSON files"
    }


# ============================================================================
# TELEMETRY DETAILED ENDPOINTS
# ============================================================================


@router.get("/telemetry/detailed")
async def get_detailed_telemetry(
    track_id: str,
    race_num: int,
    driver_number: int,
    lap_number: Optional[int] = None,
    data_type: str = Query("speed_trace", description="Type of telemetry data to return")
):
    """
    Get detailed high-frequency telemetry with three-tier comparison.

    Three-tier comparison system:
    - user: Your performance
    - next_tier: Driver 1-2 positions ahead (achievable target)
    - leader: Race winner/top performer (ultimate goal)

    data_type options:
    - speed_trace: Speed over distance with comparisons
    - brake_comparison: Brake pressure analysis
    - full: All telemetry channels
    """
    from ..services.telemetry_processor import get_telemetry_processor
    from pathlib import Path

    # Get telemetry processor
    data_path = Path(__file__).parent.parent.parent.parent / "data"
    processor = get_telemetry_processor(data_path)

    # Identify comparison drivers
    comparison_drivers = processor.identify_comparison_drivers(
        track_id, race_num, driver_number
    )

    if data_type == "speed_trace":
        # Get speed traces for all three tiers
        traces = processor.create_speed_trace(
            track_id, race_num, driver_number, comparison_drivers, lap_number
        )

        return {
            "track_id": track_id,
            "race_num": race_num,
            "data_type": "speed_trace",
            "comparison_drivers": comparison_drivers,
            "traces": traces,
            "metadata": {
                "user_position": comparison_drivers.get("user_position"),
                "description": "Three-tier comparison: You → Next Tier → Leader"
            }
        }

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported data_type: {data_type}. Supported: speed_trace"
    )


# ============================================================================
# FACTOR STATISTICS ENDPOINTS (Efficient JSON-based)
# ============================================================================


@router.get("/factors/{factor_name}/stats")
async def get_factor_stats(factor_name: str):
    """
    Get statistics for a factor across all drivers (efficient endpoint).

    Returns aggregated statistics without loading full driver details.
    Used by Skills page to display factor comparisons efficiently.

    Args:
        factor_name: One of speed, consistency, racecraft, tire_management

    Returns:
        Factor statistics including top 3 average, league average, min, max
    """
    # Validate factor name
    valid_factors = ["speed", "consistency", "racecraft", "tire_management"]
    if factor_name not in valid_factors:
        raise ValidationError(
            f"Invalid factor. Must be one of: {', '.join(valid_factors)}"
        )

    # Get all drivers from data_loader
    drivers = list(data_loader.drivers.values())

    if not drivers:
        raise NotFoundError("No driver data available")

    # Extract factor scores for this factor
    scores = []
    for driver in drivers:
        factor_obj = getattr(driver, factor_name, None)
        if factor_obj and hasattr(factor_obj, 'score'):
            scores.append(factor_obj.score)

    if not scores:
        raise NotFoundError(f"No scores available for factor {factor_name}")

    # Sort scores descending
    scores.sort(reverse=True)

    # Calculate statistics
    top_3_average = sum(scores[:3]) / 3 if len(scores) >= 3 else sum(scores) / len(scores)
    league_average = sum(scores) / len(scores)
    min_score = min(scores)
    max_score = max(scores)

    return {
        "factor": factor_name,
        "top_3_average": round(top_3_average, 2),
        "league_average": round(league_average, 2),
        "min": round(min_score, 2),
        "max": round(max_score, 2),
        "count": len(scores)
    }


@router.get("/factors/{factor_name}/breakdown/{driver_number}")
async def get_factor_breakdown(factor_name: str, driver_number: int):
    """
    Get detailed factor breakdown for a specific driver.

    Returns underlying variables, weights, and values that compose the factor score.

    Args:
        factor_name: One of speed, consistency, racecraft, tire_management
        driver_number: Driver number

    Returns:
        Factor breakdown with variables, explanation, and driver's values
    """
    import json
    from pathlib import Path

    # Validate factor name
    valid_factors = ["speed", "consistency", "racecraft", "tire_management"]
    if factor_name not in valid_factors:
        raise ValidationError(
            f"Invalid factor. Must be one of: {', '.join(valid_factors)}"
        )

    # Load factor breakdowns
    breakdowns_path = Path(__file__).parent.parent.parent / "data" / "factor_breakdowns.json"

    if not breakdowns_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Factor breakdowns not available. Run export_factor_breakdowns.py first."
        )

    with open(breakdowns_path, 'r') as f:
        breakdowns_data = json.load(f)

    # Get factor definition
    factor_def = breakdowns_data["factor_definitions"].get(factor_name)
    if not factor_def:
        raise NotFoundError(f"Factor definition not found for {factor_name}")

    # Get driver breakdown
    driver_breakdown = breakdowns_data["driver_breakdowns"].get(str(driver_number))
    if not driver_breakdown:
        raise NotFoundError(f"Driver {driver_number} not found in breakdowns")

    factor_variables = driver_breakdown.get(factor_name)
    if not factor_variables:
        raise NotFoundError(f"No {factor_name} data for driver {driver_number}")

    # Format response to match frontend expectations
    variables = []
    for var_config in factor_def["variables"]:
        var_name = var_config["name"]
        var_data = factor_variables[var_name]

        variables.append({
            "name": var_name,
            "display_name": var_data["display_name"],
            "normalized_value": var_data["normalized_value"],
            "percentile": var_data["percentile"],
            "loading": var_data.get("loading", var_data.get("weight", 0)),  # Support both old and new format
            "description": var_data.get("description", "")
        })

    return {
        "factor_name": factor_name,
        "explanation": factor_def["explanation"],
        "variables": variables
    }


@router.get("/factors/{factor_name}/comparison/{driver_number}")
async def get_factor_comparison(factor_name: str, driver_number: int):
    """
    Compare driver's factor performance with top 3 drivers.

    Shows how the driver stacks up against top performers in this factor,
    with variable-level breakdown.

    Args:
        factor_name: One of speed, consistency, racecraft, tire_management
        driver_number: Driver number

    Returns:
        Comparison data with user driver and top 3 drivers
    """
    import json
    from pathlib import Path

    # Validate factor name
    valid_factors = ["speed", "consistency", "racecraft", "tire_management"]
    if factor_name not in valid_factors:
        raise ValidationError(
            f"Invalid factor. Must be one of: {', '.join(valid_factors)}"
        )

    # Load factor breakdowns
    breakdowns_path = Path(__file__).parent.parent.parent / "data" / "factor_breakdowns.json"

    if not breakdowns_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Factor breakdowns not available"
        )

    with open(breakdowns_path, 'r') as f:
        breakdowns_data = json.load(f)

    # Get all drivers' factor scores for ranking
    all_drivers = data_loader.get_all_drivers()
    driver_scores = []

    for driver in all_drivers:
        factor_obj = getattr(driver, factor_name, None)
        if factor_obj and hasattr(factor_obj, 'percentile'):
            driver_scores.append({
                'driver_number': driver.driver_number,
                'driver_name': driver.driver_name,
                'percentile': factor_obj.percentile,
                'score': factor_obj.score
            })

    # Sort by percentile descending
    driver_scores.sort(key=lambda x: x['percentile'], reverse=True)

    # Get top 3 drivers
    top_3_drivers = driver_scores[:3]

    # Get user driver
    user_driver = next((d for d in driver_scores if d['driver_number'] == driver_number), None)
    if not user_driver:
        raise NotFoundError(f"Driver {driver_number} not found")

    # Build comparison response
    def build_driver_comparison(driver_info):
        """Helper to build driver comparison data."""
        driver_breakdown = breakdowns_data["driver_breakdowns"].get(str(driver_info['driver_number']))
        if not driver_breakdown:
            return None

        factor_variables = driver_breakdown.get(factor_name, {})

        variables_dict = {}
        for var_name, var_data in factor_variables.items():
            variables_dict[var_name] = var_data["percentile"]

        return {
            "driver_number": driver_info['driver_number'],
            "driver_name": driver_info['driver_name'],
            "percentile": driver_info['percentile'],
            "variables": variables_dict
        }

    user_comparison = build_driver_comparison(user_driver)
    top_comparisons = [build_driver_comparison(d) for d in top_3_drivers]
    top_comparisons = [c for c in top_comparisons if c is not None]

    # Generate insights
    insights = []
    if user_driver['percentile'] >= 75:
        insights.append(f"You're in the top 25% of drivers for {factor_name.replace('_', ' ')}!")
    elif user_driver['percentile'] >= 50:
        insights.append(f"You're above average in {factor_name.replace('_', ' ')}.")
    else:
        insights.append(f"{factor_name.replace('_', ' ').title()} is an area for improvement.")

    # Find user's rank
    user_rank = next((i + 1 for i, d in enumerate(driver_scores) if d['driver_number'] == driver_number), None)
    if user_rank:
        insights.append(f"You rank #{user_rank} out of {len(driver_scores)} drivers in {factor_name.replace('_', ' ')}.")

    # Gap to leader
    if top_3_drivers and user_driver['percentile'] < top_3_drivers[0]['percentile']:
        gap = top_3_drivers[0]['percentile'] - user_driver['percentile']
        insights.append(f"You're {gap:.1f} percentile points behind the leader in this factor.")

    return {
        "factor_name": factor_name,
        "user_driver": user_comparison,
        "top_drivers": top_comparisons,
        "insights": insights
    }


@router.get(
    "/factors/{factor_name}/coaching/{driver_number}",
    response_model=FactorCoachingResponse,
    summary="Get AI-powered coaching for a specific factor",
    description="Get pre-calculated personalized coaching recommendations"
)
async def get_factor_coaching(factor_name: str, driver_number: int):
    """
    Get AI-powered coaching recommendations for a driver's specific skill factor.

    Returns pre-calculated coaching analysis that includes:
    - Assessment of current performance
    - Priority focus areas based on weakest variables
    - Specific drills and exercises
    - Expected progress timeline

    Args:
        factor_name: One of speed, consistency, racecraft, tire_management
        driver_number: Driver number

    Returns:
        AI-generated coaching analysis with actionable recommendations
    """
    import json
    from pathlib import Path

    valid_factors = ["speed", "consistency", "racecraft", "tire_management"]
    if factor_name not in valid_factors:
        raise ValidationError(
            f"Invalid factor. Must be one of: {', '.join(valid_factors)}"
        )

    coaching_path = Path(__file__).parent.parent.parent / "data" / "coaching_recommendations.json"

    if not coaching_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Coaching recommendations not available. Run generate_coaching_recommendations.py first."
        )

    with open(coaching_path, 'r') as f:
        coaching_data = json.load(f)

    driver_recs = coaching_data.get("recommendations", {}).get(str(driver_number))
    if not driver_recs:
        raise NotFoundError(f"No coaching recommendations for driver {driver_number}")

    factor_rec = driver_recs.get(factor_name)
    if not factor_rec:
        raise NotFoundError(f"No {factor_name} coaching for driver {driver_number}")

    if factor_rec.get("coaching_analysis") is None:
        raise HTTPException(
            status_code=500,
            detail=f"Coaching generation failed for driver {driver_number} {factor_name}"
        )

    return FactorCoachingResponse(
        driver_number=driver_number,
        factor_name=factor_name,
        factor_percentile=factor_rec["factor_percentile"],
        factor_rank=factor_rec["factor_rank"],
        total_drivers=factor_rec["total_drivers"],
        coaching_analysis=factor_rec["coaching_analysis"],
        generated_at=factor_rec["generated_at"]
    )


# ============================================================================
# IMPROVE (POTENTIAL) PAGE ENDPOINTS
# ============================================================================

@router.post(
    "/drivers/{driver_number}/improve/predict",
    response_model=ImprovePredictionResponse,
    summary="Predict potential with adjusted skills",
    description="Calculate predictions, similar drivers, and recommendations for adjusted skills"
)
async def predict_with_adjusted_skills(driver_number: int, adjusted_skills: AdjustedSkills):
    """
    Predict driver performance with adjusted skill levels.

    Simplified version using existing driver data (no SQLite dependency).
    """
    POINTS_BUDGET = 1.0

    # Model coefficients from validated 4-factor model
    MODEL_COEFFICIENTS = {
        'speed': 6.079,
        'consistency': 3.792,
        'racecraft': 1.943,
        'tire_management': 1.237,
        'intercept': 13.01
    }

    # Get current driver skills
    driver = data_loader.get_driver(driver_number)
    if not driver:
        raise HTTPException(
            status_code=404,
            detail=f"Driver {driver_number} not found"
        )

    # Extract current skills (convert percentile to 0-1 scale to match adjusted_skills input)
    current_skills = {
        'speed': driver.speed.percentile / 100,
        'consistency': driver.consistency.percentile / 100,
        'racecraft': driver.racecraft.percentile / 100,
        'tire_management': driver.tire_management.percentile / 100
    }

    # Convert adjusted_skills to dict
    adjusted_skills_dict = {
        'speed': adjusted_skills.speed,
        'consistency': adjusted_skills.consistency,
        'racecraft': adjusted_skills.racecraft,
        'tire_management': adjusted_skills.tire_management
    }

    # Calculate points used (sum of absolute changes)
    points_used = sum(
        abs(adjusted_skills_dict[factor] - current_skills[factor])
        for factor in current_skills.keys()
    )

    # Validate points budget
    if points_used > POINTS_BUDGET:
        raise HTTPException(
            status_code=400,
            detail=f"Points used ({points_used:.1f}) exceeds budget ({POINTS_BUDGET}). "
                   f"Adjust your skills to stay within the {POINTS_BUDGET} point limit."
        )

    # Simple z-score conversion (percentile to z-score)
    # Using numpy-only implementation to reduce serverless function size
    from app.utils.numpy_stats import percentile_to_z

    # Calculate prediction using adjusted skills (convert back to 0-100 scale for z-score calculation)
    adjusted_z_scores = {
        factor: percentile_to_z(adjusted_skills_dict[factor] * 100)
        for factor in adjusted_skills_dict.keys()
    }

    predicted_finish = (
        MODEL_COEFFICIENTS['intercept'] +
        MODEL_COEFFICIENTS['speed'] * adjusted_z_scores['speed'] +
        MODEL_COEFFICIENTS['consistency'] * adjusted_z_scores['consistency'] +
        MODEL_COEFFICIENTS['racecraft'] * adjusted_z_scores['racecraft'] +
        MODEL_COEFFICIENTS['tire_management'] * adjusted_z_scores['tire_management']
    )

    # Simple confidence interval (±10% of prediction)
    confidence_range = predicted_finish * 0.1

    prediction = PredictionWithUncertainty(
        predicted_finish=round(predicted_finish, 2),
        confidence_interval_lower=round(max(1, predicted_finish - confidence_range), 2),
        confidence_interval_upper=round(predicted_finish + confidence_range, 2),
        confidence_level="medium",
        is_extrapolating=False,
        warning_message=None
    )

    # Find similar drivers based on skill similarity
    all_drivers = data_loader.get_all_drivers()
    similar_drivers = []

    for other_driver in all_drivers:
        if other_driver.driver_number == driver_number:
            continue

        # Calculate similarity score based on skill differences
        skill_diff = sum([
            abs(adjusted_skills_dict['speed'] - other_driver.speed.percentile),
            abs(adjusted_skills_dict['consistency'] - other_driver.consistency.percentile),
            abs(adjusted_skills_dict['racecraft'] - other_driver.racecraft.percentile),
            abs(adjusted_skills_dict['tire_management'] - other_driver.tire_management.percentile)
        ])

        # Convert difference to similarity (0-100 scale)
        similarity = max(0, 100 - skill_diff / 4)

        similar_drivers.append({
            'driver': other_driver,
            'similarity': similarity,
            'predicted_finish': other_driver.stats.average_finish
        })

    # Sort by similarity and take top 4
    similar_drivers.sort(key=lambda x: x['similarity'], reverse=True)
    top_similar = similar_drivers[:4]

    similar_driver_matches = [
        SimilarDriverMatch(
            driver_number=sd['driver'].driver_number,
            driver_name=sd['driver'].driver_name,
            similarity_score=round(sd['similarity'], 1),
            match_percentage=round(sd['similarity'], 1),
            skill_differences={
                'speed': round(adjusted_skills_dict['speed'] - sd['driver'].speed.percentile, 1),
                'consistency': round(adjusted_skills_dict['consistency'] - sd['driver'].consistency.percentile, 1),
                'racecraft': round(adjusted_skills_dict['racecraft'] - sd['driver'].racecraft.percentile, 1),
                'tire_management': round(adjusted_skills_dict['tire_management'] - sd['driver'].tire_management.percentile, 1)
            },
            predicted_finish=round(sd['predicted_finish'], 2),
            key_strengths=["Speed", "Consistency"]  # Simplified
        )
        for sd in top_similar
    ]

    # Generate simple recommendations
    factor_priorities = [
        ('speed', 'Raw Speed', MODEL_COEFFICIENTS['speed']),
        ('consistency', 'Consistency', MODEL_COEFFICIENTS['consistency']),
        ('racecraft', 'Racecraft', MODEL_COEFFICIENTS['racecraft']),
        ('tire_management', 'Tire Management', MODEL_COEFFICIENTS['tire_management'])
    ]

    # Sort by coefficient (impact) and current score gap
    recommendations = []
    for i, (factor, display_name, coefficient) in enumerate(sorted(factor_priorities, key=lambda x: x[2], reverse=True)):
        current_score = current_skills[factor]
        impact = round(coefficient * 0.5, 1)  # Simplified impact estimate

        recommendations.append(
            ImprovementRecommendation(
                factor_name=factor,
                display_name=display_name,
                current_score=round(current_score, 1),
                current_percentile=round(current_score, 1),
                priority=i + 1,
                rationale=f"High impact factor (coefficient: {coefficient})",
                impact_estimate=f"±{impact} positions",
                drills=["Practice session", "Data review"]  # Simplified
            )
        )

    # Build response
    response = ImprovePredictionResponse(
        driver_number=driver_number,
        current_skills=AdjustedSkills(**current_skills),
        adjusted_skills=adjusted_skills,
        points_used=points_used,
        points_available=POINTS_BUDGET - points_used,
        prediction=prediction,
        similar_drivers=similar_driver_matches,
        recommendations=recommendations
    )

    return response


# ============================================================================
# TELEMETRY COACHING ENDPOINT
# ============================================================================


@router.get(
    "/telemetry/drivers",
    summary="Get drivers with telemetry data"
)
async def get_telemetry_drivers():
    """
    Get a list of driver numbers that have telemetry data available.

    Returns a deduplicated list of driver numbers across all tracks and races.
    Uses pre-calculated JSON data.
    """
    # Get all drivers from the main drivers list
    drivers = [d.number for d in data_loader.drivers]

    return {
        "drivers_with_telemetry": drivers,
        "count": len(drivers)
    }


# DEPRECATED: Old telemetry coaching POST endpoint removed
# New endpoint: GET /api/drivers/{id}/telemetry-coaching (uses pre-calculated JSON)


# ============================================================================
# TELEMETRY COACHING ENDPOINT (JSON-based)
# ============================================================================


@router.get("/drivers/{driver_number}/telemetry-coaching")
async def get_telemetry_coaching(
    driver_number: int,
    track_id: str = Query(..., description="Track identifier (e.g., 'barber')"),
    race_num: int = Query(1, description="Race number (1 or 2)")
):
    """
    Get turn-by-turn telemetry coaching insights for a driver at a specific track.

    Returns pre-calculated insights comparing driver to fastest driver at that track.
    Includes:
    - Summary of corner performance
    - Key coaching insights (top 5)
    - Factor breakdown (which factors need work)
    - Detailed corner-by-corner analysis

    Example:
        GET /api/drivers/7/telemetry-coaching?track_id=barber&race_num=1
    """
    import json
    from pathlib import Path

    # Load pre-calculated insights
    insights_file = Path(__file__).parent.parent.parent / "data" / "telemetry_coaching_insights.json"

    if not insights_file.exists():
        raise HTTPException(
            status_code=503,
            detail="Telemetry insights not available. Run generate_telemetry_insights.py first."
        )

    with open(insights_file, 'r') as f:
        all_insights = json.load(f)

    # Get insights for this track/race/driver
    track_race_key = f"{track_id}_r{race_num}"

    if track_race_key not in all_insights:
        raise HTTPException(
            status_code=404,
            detail=f"No telemetry data available for {track_id} race {race_num}"
        )

    driver_key = str(driver_number)

    if driver_key not in all_insights[track_race_key]:
        raise HTTPException(
            status_code=404,
            detail=f"No telemetry insights for driver #{driver_number} at {track_id} R{race_num}"
        )

    insights = all_insights[track_race_key][driver_key]

    return {
        "driver_number": driver_number,
        "track_id": track_id,
        "race_num": race_num,
        "target_driver": insights["target_driver"],
        "summary": insights["summary"],
        "key_insights": insights["key_insights"],
        "factor_breakdown": insights["factor_breakdown"],
        "detailed_comparisons": insights["detailed_comparisons"]
    }


# ============================================================================
# IMPROVE PAGE - FIND SIMILAR DRIVER
# ============================================================================


@router.post("/drivers/find-similar")
async def find_similar_driver(request: FindSimilarDriverRequest):
    """
    Find top 3 drivers with skill patterns most similar to target skills.

    CRITICAL REQUIREMENT: Only returns drivers with BETTER performance (lower avg_finish).
    Uses Euclidean distance in 4D skill space (speed, consistency, racecraft, tire_management).
    Returns up to 3 matching drivers sorted by similarity, all guaranteed to perform better.
    """
    try:
        # Get all drivers with their skills
        all_drivers = data_loader.get_all_drivers()

        if not all_drivers:
            raise HTTPException(status_code=500, detail="No driver data available")

        current_driver_num = request.current_driver_number
        target = request.target_skills

        # Get current driver's performance baseline for comparison
        current_driver = next((d for d in all_drivers if d.driver_number == current_driver_num), None)
        if not current_driver:
            raise HTTPException(status_code=404, detail=f"Current driver {current_driver_num} not found")

        # Get current driver's avg_finish for performance filtering
        current_season_stats = data_loader.get_season_stats(current_driver_num)
        current_avg_finish = (
            current_season_stats.avg_finish
            if current_season_stats and current_season_stats.avg_finish
            else current_driver.stats.average_finish
        )

        if not current_avg_finish or current_avg_finish <= 0:
            raise HTTPException(
                status_code=400,
                detail="Current driver has no valid performance data for comparison"
            )

        # Extract target skills
        target_speed = target.get('speed', 0)
        target_consistency = target.get('consistency', 0)
        target_racecraft = target.get('racecraft', 0)
        target_tire = target.get('tire_management', 0)

        # List to store all driver matches with distances
        matches = []

        # Calculate distance for all drivers
        for driver in all_drivers:
            # Skip current driver
            if driver.driver_number == current_driver_num:
                continue

            # Get driver skills (access Pydantic model attributes)
            speed = driver.speed.score
            consistency = driver.consistency.score
            racecraft = driver.racecraft.score
            tire = driver.tire_management.score

            # Get season stats for average finish
            season_stats = data_loader.get_season_stats(driver.driver_number)
            avg_finish = season_stats.avg_finish if season_stats and season_stats.avg_finish else driver.stats.average_finish

            # CRITICAL FILTER: Skip drivers without valid avg_finish or who perform worse
            # In racing, LOWER avg_finish = BETTER performance
            if not avg_finish or avg_finish <= 0 or avg_finish >= current_avg_finish:
                continue

            # Calculate Euclidean distance in 4D space
            distance = (
                (speed - target_speed) ** 2 +
                (consistency - target_consistency) ** 2 +
                (racecraft - target_racecraft) ** 2 +
                (tire - target_tire) ** 2
            ) ** 0.5

            matches.append({
                'driver': driver,
                'distance': distance,
                'skills': {
                    'speed': round(speed, 1),
                    'consistency': round(consistency, 1),
                    'racecraft': round(racecraft, 1),
                    'tire_management': round(tire, 1)
                },
                'avg_finish': round(avg_finish, 2),
                'performance_improvement': round(current_avg_finish - avg_finish, 2)  # How much better
            })

        # Edge case: No better drivers found
        if not matches:
            return {
                "similar_drivers": [],
                "message": f"No drivers found with better performance than current avg finish of {round(current_avg_finish, 2)}",
                "current_avg_finish": round(current_avg_finish, 2)
            }

        # Sort by distance (closest skill match first) and take top 3
        matches.sort(key=lambda x: x['distance'])
        top_matches = matches[:3]  # Take up to 3 (may be fewer if <3 better drivers exist)

        # Calculate dynamic max_distance from actual data for better scoring
        all_distances = [m['distance'] for m in matches]
        max_distance = max(all_distances) if all_distances else 200.0
        min_distance = min(all_distances) if all_distances else 0.0

        similar_drivers = []
        for match in top_matches:
            driver = match['driver']
            distance = match['distance']

            # Improved match score: normalize to 0-100 based on actual distance range
            # Uses min-max normalization for better interpretability
            if max_distance > min_distance:
                normalized_distance = (distance - min_distance) / (max_distance - min_distance)
                match_score = max(0, 100 * (1 - normalized_distance))
            else:
                match_score = 100.0  # Perfect match if all distances are identical

            similar_drivers.append({
                "driver_number": driver.driver_number,
                "driver_name": driver.driver_name or f"Driver #{driver.driver_number}",
                "skills": match['skills'],
                "match_score": round(match_score, 1),
                "distance": round(distance, 2),
                "avg_finish": match['avg_finish'],
                "performance_improvement": match['performance_improvement'],
                "current_avg_finish": round(current_avg_finish, 2)
            })

        return {
            "similar_drivers": similar_drivers,
            "current_avg_finish": round(current_avg_finish, 2),
            "total_better_drivers": len(matches)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar drivers: {e}")
        raise HTTPException(status_code=500, detail=f"Error finding similar drivers: {str(e)}")


# ============================================================================
# PRACTICE PLAN ENDPOINT - THE KILLER FEATURE
# ============================================================================


@router.post(
    "/practice/generate-plan",
    response_model=PracticePlanResponse,
    summary="Generate personalized practice plan",
    description="Create a week-by-week practice plan to reach target position"
)
async def generate_practice_plan(request: PracticePlanRequest):
    """
    Generate a personalized practice plan showing exactly what to improve and by how much.

    This is the killer feature that predicts position improvement based on skill gains.
    """
    # Model coefficients from validated 4-factor model
    MODEL_COEFFICIENTS = {
        'speed': 6.079,
        'consistency': 3.792,
        'racecraft': 1.943,
        'tire_management': 1.237,
        'intercept': 13.01
    }

    FACTOR_WEIGHTS = {
        'speed': 0.466,
        'consistency': 0.291,
        'racecraft': 0.149,
        'tire_management': 0.095
    }

    try:
        # Get driver data
        driver = data_loader.get_driver(request.driver_number)
        if not driver:
            raise HTTPException(
                status_code=404,
                detail=f"Driver {request.driver_number} not found"
            )

        # Get track data
        track = data_loader.get_track(request.current_track)
        if not track:
            raise HTTPException(
                status_code=404,
                detail=f"Track {request.current_track} not found"
            )

        # Calculate current predicted position
        from app.utils.numpy_stats import percentile_to_z

        current_z_scores = {
            'speed': percentile_to_z(driver.speed.percentile),
            'consistency': percentile_to_z(driver.consistency.percentile),
            'racecraft': percentile_to_z(driver.racecraft.percentile),
            'tire_management': percentile_to_z(driver.tire_management.percentile)
        }

        current_position = (
            MODEL_COEFFICIENTS['intercept'] +
            MODEL_COEFFICIENTS['speed'] * current_z_scores['speed'] +
            MODEL_COEFFICIENTS['consistency'] * current_z_scores['consistency'] +
            MODEL_COEFFICIENTS['racecraft'] * current_z_scores['racecraft'] +
            MODEL_COEFFICIENTS['tire_management'] * current_z_scores['tire_management']
        )

        # Calculate gap to target
        positions_to_gain = current_position - request.target_position

        if positions_to_gain <= 0:
            # Already at or better than target
            return PracticePlanResponse(
                current_position=round(current_position, 2),
                target_position=request.target_position,
                positions_to_gain=0,
                success_probability=1.0,
                weekly_plan=[],
                skill_priorities={},
                final_prediction=FinalPrediction(
                    predicted_position=round(current_position, 2),
                    confidence_interval=[round(current_position - 0.5, 2), round(current_position + 0.5, 2)],
                    success_probability=1.0
                ),
                track_name=track.name,
                ai_coaching_summary="You're already at or above your target position! Focus on maintaining your current performance."
            )

        # Determine which skills to prioritize based on:
        # 1. Model coefficient (impact on position)
        # 2. Current score (room for improvement)
        # 3. Track demand profile

        skill_gaps = {}
        for skill in ['speed', 'consistency', 'racecraft', 'tire_management']:
            current_percentile = getattr(driver, skill).percentile
            track_demand = getattr(track.demand_profile, skill)

            # Calculate skill priority score
            model_weight = MODEL_COEFFICIENTS[skill]
            room_for_improvement = 100 - current_percentile
            track_importance = track_demand / 100

            priority_score = model_weight * room_for_improvement * track_importance

            skill_gaps[skill] = {
                'current': current_percentile,
                'weight': model_weight,
                'room': room_for_improvement,
                'track_fit': track_importance,
                'priority': priority_score
            }

        # Sort skills by priority
        sorted_skills = sorted(skill_gaps.items(), key=lambda x: x[1]['priority'], reverse=True)

        # Calculate how much to improve each skill per week
        total_weeks = request.weeks_available
        weekly_plan = []

        # Distribute improvement across top 2-3 skills
        primary_skills = sorted_skills[:2]  # Focus on top 2 skills

        # Calculate points needed to reach target
        # Each percentile point improvement translates to position change via coefficient
        points_per_position = 1.5  # Rough estimate: need ~1.5 percentile points per position
        total_points_needed = positions_to_gain * points_per_position

        # Distribute improvement across primary skills weighted by their coefficients
        total_coefficient = sum(skill_gaps[skill]['weight'] for skill, _ in primary_skills)

        skill_targets = {}
        for skill, data in primary_skills:
            proportion = skill_gaps[skill]['weight'] / total_coefficient
            points_to_add = total_points_needed * proportion
            target_score = min(95, data['current'] + points_to_add)  # Cap at 95th percentile
            skill_targets[skill] = target_score

        # Generate weekly milestones
        cumulative_improvement = {skill: 0 for skill, _ in primary_skills}

        for week in range(1, total_weeks + 1):
            # Distribute improvement linearly across weeks
            week_fraction = week / total_weeks

            # Pick primary skill for this week (alternate between top skills)
            focus_skill_name = primary_skills[week % len(primary_skills)][0]
            focus_skill_data = skill_gaps[focus_skill_name]

            # Calculate targets for this week
            week_target = focus_skill_data['current'] + (skill_targets[focus_skill_name] - focus_skill_data['current']) * week_fraction
            improvement_this_week = week_target - (focus_skill_data['current'] + cumulative_improvement[focus_skill_name])
            cumulative_improvement[focus_skill_name] += improvement_this_week

            # Calculate predicted position after this week
            projected_skills = {
                skill: focus_skill_data['current'] + cumulative_improvement.get(skill, 0)
                for skill, focus_skill_data in skill_gaps.items()
            }

            # Convert to z-scores and predict
            projected_z = {
                skill: percentile_to_z(min(99, max(1, projected_skills[skill])))
                for skill in projected_skills
            }

            week_predicted_position = (
                MODEL_COEFFICIENTS['intercept'] +
                MODEL_COEFFICIENTS['speed'] * projected_z['speed'] +
                MODEL_COEFFICIENTS['consistency'] * projected_z['consistency'] +
                MODEL_COEFFICIENTS['racecraft'] * projected_z['racecraft'] +
                MODEL_COEFFICIENTS['tire_management'] * projected_z['tire_management']
            )

            # Generate practice drills for focused skill
            drill_map = {
                'speed': [
                    "Qualifying simulation laps (5-10 lap sessions)",
                    "Sector time optimization exercises",
                    "Low-fuel sprint race practice"
                ],
                'consistency': [
                    "20-lap consistency runs (track lap time variation)",
                    "Race simulation with tire management",
                    "Steady-state pace practice"
                ],
                'racecraft': [
                    "Overtaking scenario practice",
                    "Defensive driving exercises",
                    "Race start simulations"
                ],
                'tire_management': [
                    "Long-run tire degradation practice",
                    "Smooth driving input exercises",
                    "Fuel-and-tire saving techniques"
                ]
            }

            milestone = WeeklyMilestone(
                week=week,
                focus_skill=focus_skill_name.replace('_', ' ').title(),
                current_score=round(focus_skill_data['current'] + cumulative_improvement[focus_skill_name] - improvement_this_week, 1),
                target_score=round(week_target, 1),
                improvement_needed=f"+{round(improvement_this_week, 1)} pts",
                practice_hours=3 if week_fraction < 0.5 else 4,  # More hours in later weeks
                drills=drill_map.get(focus_skill_name, ["General practice"]),
                expected_position_after_week=round(week_predicted_position, 2),
                milestone=f"Week {week}: Improve {focus_skill_name.replace('_', ' ').title()} to {round(week_target, 1)}th percentile"
            )

            weekly_plan.append(milestone)

        # Build skill priorities summary
        skill_priorities = {}
        for skill, data in sorted_skills[:3]:  # Top 3 skills
            target = skill_targets.get(skill, data['current'])
            improvement = target - data['current']

            # Estimate position impact
            z_current = percentile_to_z(data['current'])
            z_target = percentile_to_z(target)
            position_impact = (z_target - z_current) * MODEL_COEFFICIENTS[skill]

            skill_priorities[skill] = SkillPriority(
                skill_name=skill.replace('_', ' ').title(),
                current=round(data['current'], 1),
                target=round(target, 1),
                position_impact=f"+{abs(round(position_impact, 1))} positions" if position_impact < 0 else f"{round(position_impact, 1)} positions",
                effort_score="High (4 hrs/week)" if improvement > 10 else "Medium (3 hrs/week)"
            )

        # Final prediction
        final_predicted_position = weekly_plan[-1].expected_position_after_week if weekly_plan else current_position
        success_probability = min(0.95, max(0.5, 1 - (abs(final_predicted_position - request.target_position) / positions_to_gain)))

        final_prediction = FinalPrediction(
            predicted_position=round(final_predicted_position, 2),
            confidence_interval=[
                round(max(1, final_predicted_position - 1.0), 2),
                round(final_predicted_position + 1.0, 2)
            ],
            success_probability=round(success_probability, 2)
        )

        # AI coaching summary (optional - can use Claude API here if needed)
        ai_coaching_summary = (
            f"Based on your current performance at {track.name}, focus on improving "
            f"{' and '.join([skill.replace('_', ' ').title() for skill, _ in primary_skills])}. "
            f"With {total_weeks} weeks of dedicated practice, you have a "
            f"{round(success_probability * 100)}% probability of reaching P{request.target_position}."
        )

        return PracticePlanResponse(
            current_position=round(current_position, 2),
            target_position=request.target_position,
            positions_to_gain=round(positions_to_gain, 2),
            success_probability=round(success_probability, 2),
            weekly_plan=weekly_plan,
            skill_priorities=skill_priorities,
            final_prediction=final_prediction,
            track_name=track.name,
            ai_coaching_summary=ai_coaching_summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating practice plan: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating practice plan: {str(e)}")


# ============================================================================
# SKILLS PAGE - DIAGNOSTIC ENDPOINTS (Coach View)
# ============================================================================


@router.get(
    "/drivers/{driver_number}/skill-gaps",
    response_model=SkillGapAnalysisResponse,
    summary="Analyze skill gaps with position impact",
    description="Calculate prioritized skill gaps showing how much each gap costs in positions"
)
async def get_skill_gap_analysis(driver_number: int):
    """
    Analyze driver's skill gaps vs top 3 drivers with position impact.

    Returns prioritized list of skill gaps showing:
    - Gap in percentile points vs top 3 average
    - Estimated positions gained if gap is closed (using 4-factor model coefficients)
    - Telemetry evidence from Barber (where available)
    - Priority ranking based on impact

    This is the core of the Coach View - showing WHERE to focus improvement efforts.
    """
    import json
    from pathlib import Path
    from app.utils.numpy_stats import percentile_to_z

    # Model coefficients from validated 4-factor model
    MODEL_COEFFICIENTS = {
        "speed": 6.079,
        "consistency": 3.792,
        "racecraft": 1.943,
        "tire_management": 1.237,
        "intercept": 13.01,
    }

    # Get driver
    driver = data_loader.get_driver(driver_number)
    if not driver:
        raise HTTPException(
            status_code=404, detail=f"Driver {driver_number} not found"
        )

    # Get all drivers to calculate rankings and top 3
    all_drivers = data_loader.get_all_drivers()
    if not all_drivers:
        raise HTTPException(status_code=500, detail="No driver data available")

    # Sort drivers by overall score to get ranking
    drivers_ranked = sorted(all_drivers, key=lambda d: d.overall_score, reverse=True)
    current_rank = next(
        (i + 1 for i, d in enumerate(drivers_ranked) if d.driver_number == driver_number),
        len(drivers_ranked),
    )

    # Calculate top 3 average for each factor
    top3_averages = {
        "speed": sum(d.speed.percentile for d in drivers_ranked[:3]) / 3,
        "consistency": sum(d.consistency.percentile for d in drivers_ranked[:3]) / 3,
        "racecraft": sum(d.racecraft.percentile for d in drivers_ranked[:3]) / 3,
        "tire_management": sum(d.tire_management.percentile for d in drivers_ranked[:3]) / 3,
    }

    # Load telemetry insights for evidence (Barber only for now)
    telemetry_evidence = {}
    try:
        insights_file = Path(__file__).parent.parent.parent / "data" / "telemetry_coaching_insights.json"
        if insights_file.exists():
            with open(insights_file, "r") as f:
                all_insights = json.load(f)
            # Check for Barber R1 data for this driver
            if "barber_r1" in all_insights and str(driver_number) in all_insights["barber_r1"]:
                barber_data = all_insights["barber_r1"][str(driver_number)]
                # Map factor breakdown to evidence
                for factor, count in barber_data.get("factor_breakdown", {}).items():
                    if count > 0:
                        factor_key = factor.lower().replace(" ", "_")
                        if factor_key == "speed":
                            telemetry_evidence["speed"] = [
                                insight for insight in barber_data.get("key_insights", [])
                                if "mph SLOWER" in insight or "speed" in insight.lower()
                            ]
                        elif factor_key == "consistency":
                            telemetry_evidence["consistency"] = [
                                insight for insight in barber_data.get("key_insights", [])
                                if "EARLIER" in insight or "LATER" in insight
                            ]
                        elif factor_key == "racecraft":
                            telemetry_evidence["racecraft"] = [
                                insight for insight in barber_data.get("key_insights", [])
                                if "braking" in insight.lower() or "exit" in insight.lower()
                            ]
    except Exception as e:
        logger.warning(f"Could not load telemetry evidence: {e}")

    # Calculate skill gaps with position impact
    skill_gaps = []
    total_potential_positions = 0

    factors = [
        ("speed", "Speed", driver.speed.percentile),
        ("consistency", "Consistency", driver.consistency.percentile),
        ("racecraft", "Racecraft", driver.racecraft.percentile),
        ("tire_management", "Tire Management", driver.tire_management.percentile),
    ]

    for factor_key, display_name, current_pct in factors:
        top3_avg = top3_averages[factor_key]
        gap = top3_avg - current_pct

        # Only include if there's a gap (top 3 is better)
        if gap > 0:
            # Calculate position impact using model coefficient
            # z-score change from closing the gap
            current_z = percentile_to_z(current_pct)
            target_z = percentile_to_z(top3_avg)
            z_improvement = target_z - current_z

            # Position impact = coefficient * z-score change
            # Negative because lower position number is better
            position_impact = abs(MODEL_COEFFICIENTS[factor_key] * z_improvement)

            total_potential_positions += position_impact

            skill_gaps.append(
                SkillGapItem(
                    factor_name=factor_key,
                    display_name=display_name,
                    current_percentile=round(current_pct, 1),
                    top3_average=round(top3_avg, 1),
                    gap_percentile=round(gap, 1),
                    position_impact=round(position_impact, 2),
                    priority_rank=0,  # Will be set after sorting
                    telemetry_evidence=telemetry_evidence.get(factor_key, [])[:3],  # Top 3 evidence items
                )
            )

    # Sort by position impact (highest first) and assign priority ranks
    skill_gaps.sort(key=lambda x: x.position_impact, reverse=True)
    for i, gap in enumerate(skill_gaps):
        gap.priority_rank = i + 1

    # Determine primary weakness
    primary_weakness = skill_gaps[0].display_name if skill_gaps else "None identified"

    # Estimate potential rank if all gaps closed
    estimated_potential_rank = max(1, int(current_rank - total_potential_positions))

    # Generate coach summary
    if skill_gaps:
        top_gap = skill_gaps[0]
        coach_summary = (
            f"Focus on {top_gap.display_name} - closing the {top_gap.gap_percentile:.1f} percentile gap "
            f"to top 3 average could gain you {top_gap.position_impact:.1f} positions. "
            f"Total potential improvement: {total_potential_positions:.1f} positions "
            f"(from P{current_rank} to ~P{estimated_potential_rank})."
        )
    else:
        coach_summary = "Excellent! You're performing at or above top 3 level in all skill areas."

    return SkillGapAnalysisResponse(
        driver_number=driver_number,
        driver_name=driver.driver_name or f"Driver #{driver_number}",
        current_overall_rank=current_rank,
        total_drivers=len(all_drivers),
        skill_gaps=skill_gaps,
        primary_weakness=primary_weakness,
        estimated_potential_rank=estimated_potential_rank,
        coach_summary=coach_summary,
    )


@router.get(
    "/drivers/{driver_number}/coach-recommendations",
    response_model=CoachRecommendationsResponse,
    summary="Get telemetry-backed coaching recommendations",
    description="Generate prioritized coaching recommendations based on telemetry evidence"
)
async def get_coach_recommendations(driver_number: int):
    """
    Generate actionable coaching recommendations based on skill gaps and telemetry evidence.

    Uses:
    - Skill gap analysis to prioritize areas
    - Barber telemetry data for specific corner evidence
    - Model coefficients for impact estimation

    Returns prioritized list of recommendations with specific evidence.
    """
    import json
    from pathlib import Path

    # Get skill gaps first
    skill_gaps_response = await get_skill_gap_analysis(driver_number)

    # Load telemetry insights
    track_insights = {}
    try:
        insights_file = Path(__file__).parent.parent.parent / "data" / "telemetry_coaching_insights.json"
        if insights_file.exists():
            with open(insights_file, "r") as f:
                all_insights = json.load(f)

            # Get Barber insights if available
            if "barber_r1" in all_insights and str(driver_number) in all_insights["barber_r1"]:
                barber_data = all_insights["barber_r1"][str(driver_number)]
                track_insights["barber"] = barber_data.get("key_insights", [])
    except Exception as e:
        logger.warning(f"Could not load telemetry insights: {e}")

    # Generate recommendations based on skill gaps
    recommendations = []

    for i, gap in enumerate(skill_gaps_response.skill_gaps[:3]):  # Top 3 priorities
        evidence = gap.telemetry_evidence if gap.telemetry_evidence else []

        # Generate specific recommendation based on factor
        if gap.factor_name == "speed":
            recommendation_text = (
                f"Increase corner entry and apex speeds. You're {gap.gap_percentile:.1f} percentile points "
                f"behind top 3 average in raw speed."
            )
            expected = f"+{gap.position_impact:.1f} positions"
        elif gap.factor_name == "consistency":
            recommendation_text = (
                f"Improve lap-to-lap consistency. Focus on consistent braking points and "
                f"throttle application. Gap: {gap.gap_percentile:.1f} percentile points."
            )
            expected = f"+{gap.position_impact:.1f} positions"
        elif gap.factor_name == "racecraft":
            recommendation_text = (
                f"Develop better race craft through overtaking and defensive skills. "
                f"Gap: {gap.gap_percentile:.1f} percentile points to top 3."
            )
            expected = f"+{gap.position_impact:.1f} positions"
        else:  # tire_management
            recommendation_text = (
                f"Improve tire management through smoother inputs and strategic pace management. "
                f"Gap: {gap.gap_percentile:.1f} percentile points."
            )
            expected = f"+{gap.position_impact:.1f} positions"

        recommendations.append(
            CoachRecommendation(
                priority=i + 1,
                skill_area=gap.display_name,
                recommendation=recommendation_text,
                evidence=evidence,
                expected_improvement=expected,
            )
        )

    # Summary
    if recommendations:
        summary = (
            f"Focus on {recommendations[0].skill_area} as your primary improvement area. "
            f"Combined improvements could gain you ~{sum(g.position_impact for g in skill_gaps_response.skill_gaps):.1f} positions."
        )
    else:
        summary = "You're performing at top 3 level. Focus on maintaining consistency."

    return CoachRecommendationsResponse(
        driver_number=driver_number,
        recommendations=recommendations,
        track_specific_insights=track_insights,
        summary=summary,
    )


# ============================================================================
# DEVELOPMENT PAGE - PROJECTION ENDPOINTS
# ============================================================================


@router.get(
    "/rankings/projected",
    response_model=ProjectedRankingsResponse,
    summary="Get projected rankings with adjusted skills",
    description="Calculate where driver would rank with hypothetical skill improvements"
)
async def get_projected_rankings(
    driver_number: int = Query(..., description="Driver number to project"),
    speed: float = Query(..., ge=0, le=100, description="Projected speed percentile"),
    consistency: float = Query(..., ge=0, le=100, description="Projected consistency percentile"),
    racecraft: float = Query(..., ge=0, le=100, description="Projected racecraft percentile"),
    tire_management: float = Query(..., ge=0, le=100, description="Projected tire management percentile"),
):
    """
    Project where driver would rank with adjusted skill levels.

    Returns:
    - Complete rankings table with all drivers
    - User's current rank and projected rank
    - Projected average finish position
    - Visual indicator of user's projected position among real drivers

    This is THE KILLER FEATURE for the Development page.
    """
    from app.utils.numpy_stats import percentile_to_z

    # Model coefficients
    MODEL_COEFFICIENTS = {
        "speed": 6.079,
        "consistency": 3.792,
        "racecraft": 1.943,
        "tire_management": 1.237,
        "intercept": 13.01,
    }

    # Get user driver
    user_driver = data_loader.get_driver(driver_number)
    if not user_driver:
        raise HTTPException(
            status_code=404, detail=f"Driver {driver_number} not found"
        )

    # Get all drivers
    all_drivers = data_loader.get_all_drivers()
    if not all_drivers:
        raise HTTPException(status_code=500, detail="No driver data available")

    # Calculate projected average finish for user
    projected_z_scores = {
        "speed": percentile_to_z(speed),
        "consistency": percentile_to_z(consistency),
        "racecraft": percentile_to_z(racecraft),
        "tire_management": percentile_to_z(tire_management),
    }

    projected_avg_finish = (
        MODEL_COEFFICIENTS["intercept"]
        + MODEL_COEFFICIENTS["speed"] * projected_z_scores["speed"]
        + MODEL_COEFFICIENTS["consistency"] * projected_z_scores["consistency"]
        + MODEL_COEFFICIENTS["racecraft"] * projected_z_scores["racecraft"]
        + MODEL_COEFFICIENTS["tire_management"] * projected_z_scores["tire_management"]
    )

    # Calculate current average finish
    current_z_scores = {
        "speed": percentile_to_z(user_driver.speed.percentile),
        "consistency": percentile_to_z(user_driver.consistency.percentile),
        "racecraft": percentile_to_z(user_driver.racecraft.percentile),
        "tire_management": percentile_to_z(user_driver.tire_management.percentile),
    }

    current_avg_finish = (
        MODEL_COEFFICIENTS["intercept"]
        + MODEL_COEFFICIENTS["speed"] * current_z_scores["speed"]
        + MODEL_COEFFICIENTS["consistency"] * current_z_scores["consistency"]
        + MODEL_COEFFICIENTS["racecraft"] * current_z_scores["racecraft"]
        + MODEL_COEFFICIENTS["tire_management"] * current_z_scores["tire_management"]
    )

    # Build rankings table with all drivers
    rankings_data = []

    for driver in all_drivers:
        # Calculate avg finish using the same model
        driver_z = {
            "speed": percentile_to_z(driver.speed.percentile),
            "consistency": percentile_to_z(driver.consistency.percentile),
            "racecraft": percentile_to_z(driver.racecraft.percentile),
            "tire_management": percentile_to_z(driver.tire_management.percentile),
        }

        driver_avg_finish = (
            MODEL_COEFFICIENTS["intercept"]
            + MODEL_COEFFICIENTS["speed"] * driver_z["speed"]
            + MODEL_COEFFICIENTS["consistency"] * driver_z["consistency"]
            + MODEL_COEFFICIENTS["racecraft"] * driver_z["racecraft"]
            + MODEL_COEFFICIENTS["tire_management"] * driver_z["tire_management"]
        )

        rankings_data.append(
            {
                "driver_number": driver.driver_number,
                "driver_name": driver.driver_name or f"Driver #{driver.driver_number}",
                "speed": driver.speed.percentile,
                "consistency": driver.consistency.percentile,
                "racecraft": driver.racecraft.percentile,
                "tire_management": driver.tire_management.percentile,
                "overall_score": driver.overall_score,
                "avg_finish": driver_avg_finish,
                "is_user": driver.driver_number == driver_number,
                "is_projected": False,
            }
        )

    # Add projected user as separate entry
    projected_overall = (
        speed * 0.466
        + consistency * 0.291
        + racecraft * 0.149
        + tire_management * 0.095
    )

    rankings_data.append(
        {
            "driver_number": driver_number,
            "driver_name": f"{user_driver.driver_name or f'Driver #{driver_number}'} (PROJECTED)",
            "speed": speed,
            "consistency": consistency,
            "racecraft": racecraft,
            "tire_management": tire_management,
            "overall_score": projected_overall,
            "avg_finish": projected_avg_finish,
            "is_user": True,
            "is_projected": True,
        }
    )

    # Sort by avg_finish (lower is better) to determine rankings
    rankings_data.sort(key=lambda x: x["avg_finish"])

    # Assign ranks and build response
    rankings_table = []
    current_rank = 0
    projected_rank = 0

    for i, data in enumerate(rankings_data):
        rank = i + 1

        # Track user's current and projected ranks
        if data["driver_number"] == driver_number:
            if data["is_projected"]:
                projected_rank = rank
            else:
                current_rank = rank

        rankings_table.append(
            ProjectedDriverRanking(
                rank=rank,
                driver_number=data["driver_number"],
                driver_name=data["driver_name"],
                speed=round(data["speed"], 1),
                consistency=round(data["consistency"], 1),
                racecraft=round(data["racecraft"], 1),
                tire_management=round(data["tire_management"], 1),
                overall_score=round(data["overall_score"], 1),
                avg_finish=round(data["avg_finish"], 2),
                is_user=data["is_user"],
                is_projected=data["is_projected"],
            )
        )

    # Determine confidence level based on skill changes
    skill_changes = abs(speed - user_driver.speed.percentile) + abs(consistency - user_driver.consistency.percentile) + abs(racecraft - user_driver.racecraft.percentile) + abs(tire_management - user_driver.tire_management.percentile)

    if skill_changes < 10:
        confidence_level = "high"
    elif skill_changes < 25:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    positions_gained = current_rank - projected_rank

    return ProjectedRankingsResponse(
        user_driver_number=driver_number,
        current_rank=current_rank,
        projected_rank=projected_rank,
        positions_gained=positions_gained,
        projected_avg_finish=round(projected_avg_finish, 2),
        current_avg_finish=round(current_avg_finish, 2),
        rankings_table=rankings_table,
        confidence_level=confidence_level,
    )
