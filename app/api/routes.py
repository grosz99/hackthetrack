"""
API routes for Racing Analytics platform.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models import (
    Track,
    Driver,
    CircuitFitPrediction,
    ChatRequest,
    ChatResponse,
    TelemetryComparison,
    LapData,
)
from ..services.data_loader import data_loader
from ..services.ai_strategy import ai_service

router = APIRouter(prefix="/api", tags=["racing"])


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
