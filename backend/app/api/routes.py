"""
API routes for Racing Analytics platform.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
import pandas as pd
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
    Get all drivers with skill profiles.

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


# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================


@router.post("/predict", response_model=CircuitFitPrediction)
async def predict_performance(driver_number: int, track_id: str):
    """
    Predict driver performance at specific track.

    Returns circuit fit score and predicted finish position using the 4-factor model.
    """
    driver = data_loader.get_driver(driver_number)
    track = data_loader.get_track(track_id)

    if not driver:
        raise HTTPException(
            status_code=404, detail=f"Driver {driver_number} not found"
        )
    if not track:
        raise HTTPException(status_code=404, detail=f"Track {track_id} not found")

    # Calculate circuit fit
    fit_score = data_loader.calculate_circuit_fit(driver_number, track_id)
    if fit_score is None:
        raise HTTPException(
            status_code=500, detail="Failed to calculate circuit fit"
        )

    # Predict finish position
    predicted_finish = data_loader.predict_finish_position(driver_number, track_id)
    if predicted_finish is None:
        raise HTTPException(
            status_code=500, detail="Failed to predict finish position"
        )

    # Generate explanation
    explanation = _generate_prediction_explanation(driver, track, fit_score)

    return CircuitFitPrediction(
        driver_number=driver_number,
        track_id=track_id,
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
    """
    # Get lap data
    lap_data = data_loader.get_lap_data(track_id, race_num)

    if lap_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"No lap data found for {track_id} race {race_num}",
        )

    # Filter for each driver and exclude caution laps
    driver_1_data = lap_data[
        (lap_data["VEHICLE_NO"] == driver_1) & (lap_data["FLAG_AT_FL"] == 0)
    ]
    driver_2_data = lap_data[
        (lap_data["VEHICLE_NO"] == driver_2) & (lap_data["FLAG_AT_FL"] == 0)
    ]

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
    """Health check endpoint."""
    return {
        "status": "healthy",
        "tracks_loaded": len(data_loader.tracks),
        "drivers_loaded": len(data_loader.drivers),
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

    # Extract current skills
    current_skills = {
        'speed': driver.speed.percentile,
        'consistency': driver.consistency.percentile,
        'racecraft': driver.racecraft.percentile,
        'tire_management': driver.tire_management.percentile
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
    def percentile_to_z(percentile):
        from scipy import stats
        return stats.norm.ppf(max(0.01, min(0.99, percentile / 100.0)))

    # Calculate prediction using adjusted skills
    adjusted_z_scores = {
        factor: percentile_to_z(adjusted_skills_dict[factor])
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
    """
    import pandas as pd
    from pathlib import Path

    data_path = Path(__file__).parent.parent.parent.parent / "data"
    telemetry_path = data_path / "telemetry"

    # Get all telemetry CSV files
    driver_numbers = set()

    for csv_file in telemetry_path.glob("*_wide.csv"):
        try:
            df = pd.read_csv(csv_file)
            if 'vehicle_number' in df.columns:
                driver_numbers.update(df['vehicle_number'].unique().tolist())
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
            continue

    return {
        "drivers_with_telemetry": sorted([int(d) for d in driver_numbers if pd.notna(d)]),
        "count": len(driver_numbers)
    }


@router.post(
    "/telemetry/coaching",
    response_model=TelemetryCoachingResponse,
    summary="Get AI telemetry coaching",
    description="Analyze telemetry and provide race engineer-style coaching advice"
)
async def get_telemetry_coaching(request: TelemetryCoachingRequest):
    """
    Analyze telemetry data and provide AI-powered coaching.

    Compares driver's telemetry against a reference driver and generates
    specific, actionable coaching recommendations.
    """
    import pandas as pd
    import numpy as np
    from pathlib import Path

    # Load telemetry data
    data_path = Path(__file__).parent.parent.parent.parent / "data"
    telemetry_path = data_path / "telemetry" / f"{request.track_id}_r{request.race_num}_wide.csv"

    if not telemetry_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Telemetry data not found for {request.track_id} race {request.race_num}"
        )

    # Load telemetry
    df = pd.read_csv(telemetry_path)

    # Filter for both drivers
    driver_df = df[df['vehicle_number'] == request.driver_number].copy()
    reference_df = df[df['vehicle_number'] == request.reference_driver_number].copy()

    if driver_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No telemetry data found for driver {request.driver_number}"
        )

    if reference_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No telemetry data found for reference driver {request.reference_driver_number}"
        )

    # Get track info
    track = data_loader.get_track(request.track_id)
    track_name = track.name if track else request.track_id.title()

    # Calculate overall time delta (simplified - using best laps)
    driver_laps = driver_df[driver_df['lap'] >= 3]
    reference_laps = reference_df[reference_df['lap'] >= 3]

    driver_best_lap = None
    reference_best_lap = None

    if len(driver_laps) > 0:
        lap_counts = driver_laps.groupby('lap')['speed'].count()
        if len(lap_counts) > 0:
            driver_best_lap = lap_counts.idxmax()

    if len(reference_laps) > 0:
        lap_counts = reference_laps.groupby('lap')['speed'].count()
        if len(lap_counts) > 0:
            reference_best_lap = lap_counts.idxmax()

    # Calculate telemetry insights
    telemetry_insights = _analyze_telemetry_patterns(driver_df, reference_df)

    # Analyze corner performance (simplified - using speed differentials)
    corner_analysis = _analyze_corners(driver_df, reference_df, track_name)

    # Calculate total potential gain
    total_time_delta = telemetry_insights.get('total_delta', 0)
    potential_gain = sum(c.time_loss for c in corner_analysis)

    # Generate AI coaching
    coaching_text = ai_telemetry_coach.generate_coaching(
        driver_number=request.driver_number,
        reference_driver_number=request.reference_driver_number,
        track_name=track_name,
        telemetry_insights=telemetry_insights,
        corner_analysis=[c.dict() for c in corner_analysis]
    )

    return TelemetryCoachingResponse(
        driver_number=request.driver_number,
        reference_driver_number=request.reference_driver_number,
        track_name=track_name,
        total_time_delta=total_time_delta,
        potential_time_gain=potential_gain,
        corner_analysis=corner_analysis,
        ai_coaching=coaching_text,
        telemetry_insights=telemetry_insights
    )


def _analyze_telemetry_patterns(driver_df: pd.DataFrame, reference_df: pd.DataFrame) -> Dict:
    """Analyze overall telemetry patterns between drivers."""

    insights = {}

    # Braking pattern
    if 'pbrake_f' in driver_df.columns and 'pbrake_f' in reference_df.columns:
        driver_brake_avg = driver_df['pbrake_f'].mean()
        reference_brake_avg = reference_df['pbrake_f'].mean()

        if driver_brake_avg > reference_brake_avg:
            insights['braking_pattern'] = f"You're using more brake pressure on average ({driver_brake_avg:.1f}% vs {reference_brake_avg:.1f}%). Consider trail braking technique."
        else:
            insights['braking_pattern'] = f"Your average brake pressure is lower ({driver_brake_avg:.1f}% vs {reference_brake_avg:.1f}%)."
    else:
        insights['braking_pattern'] = "Brake data not available"

    # Throttle pattern
    if 'aps' in driver_df.columns and 'aps' in reference_df.columns:
        driver_throttle_avg = driver_df['aps'].mean()
        reference_throttle_avg = reference_df['aps'].mean()

        insights['throttle_pattern'] = f"Average throttle application: {driver_throttle_avg:.1f}% (reference: {reference_throttle_avg:.1f}%)"
    else:
        insights['throttle_pattern'] = "Throttle data not available"

    # Speed profile
    if 'speed' in driver_df.columns and 'speed' in reference_df.columns:
        driver_speed_avg = float(driver_df['speed'].mean())
        reference_speed_avg = float(reference_df['speed'].mean())
        speed_delta = reference_speed_avg - driver_speed_avg

        insights['speed_pattern'] = f"Average speed: {driver_speed_avg:.1f} km/h (reference: {reference_speed_avg:.1f} km/h, delta: {speed_delta:+.1f} km/h)"
        insights['total_delta'] = f"{float(speed_delta / 10):.3f}"  # Convert to string
    else:
        insights['speed_pattern'] = "Speed data not available"
        insights['total_delta'] = "0.000"

    # Steering smoothness
    if 'Steering_Angle' in driver_df.columns and 'Steering_Angle' in reference_df.columns:
        driver_steering_std = float(driver_df['Steering_Angle'].std())
        reference_steering_std = float(reference_df['Steering_Angle'].std())

        if driver_steering_std > reference_steering_std * 1.1:
            insights['steering_pattern'] = f"Your steering inputs are less smooth (std: {driver_steering_std:.2f} vs {reference_steering_std:.2f}). Focus on being smoother on entries."
        else:
            insights['steering_pattern'] = f"Steering smoothness is good (std: {driver_steering_std:.2f} vs {reference_steering_std:.2f})"
    else:
        insights['steering_pattern'] = "Steering data not available"

    # Convert potential_gain to string as well
    insights['potential_gain'] = f"{float(abs(float(insights.get('total_delta', '0')))):.3f}"

    return insights


def _analyze_corners(driver_df: pd.DataFrame, reference_df: pd.DataFrame, track_name: str) -> List[CornerAnalysis]:
    """Analyze corner performance (simplified version)."""

    corner_analysis = []

    # Simplified: Use lap-based speed differentials as proxy for corners
    # In production, you'd want actual corner location data

    if 'speed' not in driver_df.columns or 'speed' not in reference_df.columns:
        return corner_analysis

    # Group by lap and find minimum speeds (corners)
    driver_laps = driver_df.groupby('lap')
    reference_laps = reference_df.groupby('lap')

    # Find common laps
    common_laps = set(driver_df['lap'].unique()) & set(reference_df['lap'].unique())

    if not common_laps:
        return corner_analysis

    # For each common lap, estimate 3-5 "corners" based on speed minimums
    for lap in sorted(common_laps)[:1]:  # Just analyze one representative lap
        driver_lap_data = driver_df[driver_df['lap'] == lap].copy()
        reference_lap_data = reference_df[reference_df['lap'] == lap].copy()

        if len(driver_lap_data) < 10 or len(reference_lap_data) < 10:
            continue

        # Find local minima in speed (corners)
        from scipy.signal import find_peaks

        driver_speeds = driver_lap_data['speed'].values
        reference_speeds = reference_lap_data['speed'].values

        # Find valleys (inverted peaks)
        peaks, _ = find_peaks(-driver_speeds, distance=50, prominence=5)

        for i, peak_idx in enumerate(peaks[:5]):  # Limit to 5 corners
            if peak_idx >= len(driver_speeds) or peak_idx >= len(reference_speeds):
                continue

            driver_apex_speed = driver_speeds[peak_idx]
            reference_apex_speed = reference_speeds[min(peak_idx, len(reference_speeds) - 1)]

            apex_delta = reference_apex_speed - driver_apex_speed
            time_loss = abs(apex_delta) * 0.01  # Rough estimate: 1 km/h = 0.01s

            focus_area = "Apex Speed" if apex_delta > 3 else "Brake Point" if apex_delta > 1 else "Throttle Application"

            corner_analysis.append(CornerAnalysis(
                corner_number=i + 1,
                corner_name=f"Turn {i + 1}",
                driver_apex_speed=float(driver_apex_speed),
                reference_apex_speed=float(reference_apex_speed),
                apex_speed_delta=float(apex_delta),
                time_loss=float(time_loss),
                focus_area=focus_area
            ))

    return sorted(corner_analysis, key=lambda x: x.time_loss, reverse=True)
