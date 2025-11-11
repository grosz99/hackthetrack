"""
API routes for Racing Analytics platform.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import pandas as pd
import logging

logger = logging.getLogger(__name__)
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
    SimilarDriverMatch,
    ImprovementRecommendation,
    ImprovePredictionResponse,
    TelemetryCoachingRequest,
    TelemetryCoachingResponse,
    CornerAnalysis,
)
from ..services.data_loader import data_loader
from ..services.ai_strategy import ai_service
from ..services.ai_telemetry_coach import ai_telemetry_coach

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

    # Add season stats to each driver
    for driver in drivers:
        season_stats = data_loader.get_season_stats(driver.driver_number)
        if season_stats:
            driver.stats = season_stats

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
# FACTOR BREAKDOWN ENDPOINTS
# ============================================================================


@router.get(
    "/drivers/{driver_number}/factors/{factor_name}",
    response_model=FactorBreakdownResponse
)
async def get_factor_breakdown(driver_number: int, factor_name: str):
    """
    Get detailed breakdown of a skill factor for a driver.

    Shows underlying variables that contribute to the factor, with percentile
    rankings and racing-focused explanations.

    factor_name: speed, consistency, racecraft, or tire_management
    """
    import sqlite3
    from pathlib import Path

    # Validate factor name
    valid_factors = ["speed", "consistency", "racecraft", "tire_management"]
    if factor_name not in valid_factors:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid factor_name. Must be one of: {', '.join(valid_factors)}"
        )

    # Connect to database
    db_path = Path(__file__).parent.parent.parent.parent / "circuit-fit.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query factor breakdown
    cursor.execute("""
        SELECT variable_name, variable_display_name, raw_value, normalized_value,
               weight, contribution, percentile
        FROM factor_breakdowns
        WHERE driver_number = ? AND factor_name = ?
        ORDER BY percentile DESC
    """, (driver_number, factor_name))

    rows = cursor.fetchall()

    if not rows:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"No factor breakdown found for driver {driver_number}, factor {factor_name}"
        )

    # Convert to FactorVariable models
    variables = []
    for row in rows:
        variables.append(FactorVariable(
            name=row[0],
            display_name=row[1],
            raw_value=row[2],
            normalized_value=row[3],
            weight=row[4],
            contribution=row[5],
            percentile=row[6]
        ))

    # Calculate overall score from variables
    overall_score = sum(var.contribution for var in variables)
    overall_percentile = sum(var.percentile * var.weight for var in variables) / sum(var.weight for var in variables)

    # Find strongest and weakest
    sorted_vars = sorted(variables, key=lambda x: x.percentile, reverse=True)
    strongest = sorted_vars[0]
    weakest = sorted_vars[-1]

    # Generate explanation
    explanation = _generate_factor_explanation(factor_name, strongest, weakest, overall_percentile)

    conn.close()

    return FactorBreakdownResponse(
        factor_name=factor_name,
        overall_score=overall_score,
        percentile=overall_percentile,
        variables=variables,
        explanation=explanation,
        strongest_area=strongest.display_name,
        weakest_area=weakest.display_name
    )


@router.get(
    "/drivers/{driver_number}/factors/{factor_name}/comparison",
    response_model=FactorComparisonResponse
)
async def get_factor_comparison(driver_number: int, factor_name: str):
    """
    Compare driver's factor performance vs top 3 drivers.

    Shows how driver stacks up against the best in each variable, with
    specific insights on where to improve.
    """
    import sqlite3
    from pathlib import Path

    # Validate factor name
    valid_factors = ["speed", "consistency", "racecraft", "tire_management"]
    if factor_name not in valid_factors:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid factor_name. Must be one of: {', '.join(valid_factors)}"
        )

    # Connect to database
    db_path = Path(__file__).parent.parent.parent.parent / "circuit-fit.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get user driver breakdown
    user_breakdown = await get_factor_breakdown(driver_number, factor_name)

    # Get top 3 drivers for comparison
    cursor.execute("""
        SELECT top_driver_1, top_driver_2, top_driver_3, insights
        FROM factor_comparisons
        WHERE driver_number = ? AND factor_name = ?
    """, (driver_number, factor_name))

    comparison_row = cursor.fetchone()

    if not comparison_row:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"No comparison found for driver {driver_number}, factor {factor_name}"
        )

    top_driver_ids = [comparison_row[0], comparison_row[1], comparison_row[2]]
    insights = comparison_row[3].split("\n") if comparison_row[3] else []

    # Get breakdowns for top drivers (skip drivers without telemetry data)
    top_drivers = []
    for top_driver_id in top_driver_ids:
        if top_driver_id is None:
            continue

        try:
            top_breakdown = await get_factor_breakdown(top_driver_id, factor_name)

            # Build variables dict
            variables_dict = {var.name: var.normalized_value for var in top_breakdown.variables}

            top_drivers.append(DriverFactorComparison(
                driver_number=top_driver_id,
                driver_name=f"Driver #{top_driver_id}",
                factor_score=top_breakdown.overall_score,
                percentile=top_breakdown.percentile,
                variables=variables_dict
            ))
        except HTTPException as e:
            # Skip drivers without telemetry data (404 errors)
            if e.status_code == 404:
                print(f"Skipping driver {top_driver_id} - no telemetry data")
                continue
            raise

    # Build user driver comparison
    user_variables = {var.name: var.normalized_value for var in user_breakdown.variables}

    user_driver = DriverFactorComparison(
        driver_number=driver_number,
        driver_name=f"Driver #{driver_number}",
        factor_score=user_breakdown.overall_score,
        percentile=user_breakdown.percentile,
        variables=user_variables
    )

    conn.close()

    return FactorComparisonResponse(
        factor_name=factor_name,
        user_driver=user_driver,
        top_drivers=top_drivers,
        insights=insights
    )


def _generate_factor_explanation(
    factor_name: str, strongest: FactorVariable,
    weakest: FactorVariable, overall_percentile: float
) -> str:
    """Generate plain-English, racing-focused explanation."""

    # Overall performance qualifier
    if overall_percentile >= 90:
        qualifier = "elite"
    elif overall_percentile >= 75:
        qualifier = "strong"
    elif overall_percentile >= 50:
        qualifier = "solid"
    elif overall_percentile >= 25:
        qualifier = "developing"
    else:
        qualifier = "needs work"

    explanation = (
        f"Your {factor_name} is {qualifier} (top {100-overall_percentile:.0f}% of the field). "
        f"Your best area is {strongest.display_name} where you rank in the top {100-strongest.percentile:.0f}%. "
        f"Focus on improving {weakest.display_name} - that's where you're giving up the most."
    )

    return explanation


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
