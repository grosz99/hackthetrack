"""
Pydantic models for Racing Analytics API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class FactorScore(BaseModel):
    """Individual factor score for a driver."""

    name: str
    score: float = Field(..., ge=0, le=100)
    percentile: float = Field(..., ge=0, le=100)
    z_score: float


class TrackDemand(BaseModel):
    """Track demand profile showing skill requirements."""

    speed: float
    consistency: float
    racecraft: float
    tire_management: float


class Track(BaseModel):
    """Track information and characteristics."""

    id: str
    name: str
    length_miles: float
    location: str
    demand_profile: TrackDemand
    description: Optional[str] = None


class DriverStats(BaseModel):
    """Driver statistics and performance metrics."""

    driver_number: int
    overall_score: float = Field(..., ge=0, le=100)
    races_completed: int
    average_finish: float
    best_finish: int
    worst_finish: int


class Driver(BaseModel):
    """Complete driver profile with skill breakdown."""

    driver_number: int
    driver_name: Optional[str] = None
    overall_score: float = Field(..., ge=0, le=100)
    speed: FactorScore
    consistency: FactorScore
    racecraft: FactorScore
    tire_management: FactorScore
    stats: DriverStats
    circuit_fits: Dict[str, float] = {}


class CircuitFitPrediction(BaseModel):
    """Prediction for driver performance at specific track."""

    driver_number: int
    track_id: str
    circuit_fit_score: float = Field(..., ge=0, le=100)
    predicted_finish: float
    explanation: str


class ChatMessage(BaseModel):
    """Chat message for AI strategy chatbot."""

    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    """Request for AI strategy chatbot."""

    message: str
    driver_number: int
    track_id: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    """Response from AI strategy chatbot."""

    message: str
    suggested_questions: List[str] = []


class LapData(BaseModel):
    """Lap-by-lap timing data."""

    lap_number: int
    lap_time: float
    sector_1: float
    sector_2: float
    sector_3: float
    flag_status: str


class TelemetryComparison(BaseModel):
    """Comparison data between two drivers."""

    track_id: str
    driver_1: int
    driver_2: int
    driver_1_laps: List[LapData]
    driver_2_laps: List[LapData]
    sector_deltas: Dict[str, float]
    insights: List[str]
