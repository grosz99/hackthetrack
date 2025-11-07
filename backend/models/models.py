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


class SeasonStats(BaseModel):
    """Season statistics for a driver."""

    driver_number: int
    wins: int = 0
    podiums: int = 0
    top5: int = 0
    top10: int = 0
    pole_positions: int = 0
    total_races: int = 0
    dnfs: int = 0
    fastest_laps: int = 0
    avg_finish: Optional[float] = None
    avg_qualifying: Optional[float] = None
    avg_positions_gained: Optional[float] = None
    points: int = 0
    championship_position: Optional[int] = None


class RaceResult(BaseModel):
    """Individual race result for trending data."""

    race_id: int
    track_id: str
    track_name: str
    round: int
    race_number: int
    date: Optional[str] = None
    start_position: Optional[int] = None
    finish_position: Optional[int] = None
    positions_gained: Optional[int] = None
    fastest_lap: Optional[str] = None  # Changed from fastest_lap_time
    gap_to_winner: Optional[str] = None
    status: Optional[str] = None
    # Qualifying data
    qualifying_time: Optional[str] = None
    gap_to_pole: Optional[str] = None
    # Sector times (best from race)
    s1_best_time: Optional[str] = None
    s2_best_time: Optional[str] = None
    s3_best_time: Optional[str] = None
    # Race lap analysis
    total_laps: Optional[int] = None
    avg_lap_time: Optional[str] = None
    best_lap_time: Optional[str] = None
    worst_lap_time: Optional[str] = None
    lap_time_std_dev: Optional[float] = None  # Consistency metric
    # Comparisons to race best
    driver_fastest_lap: Optional[str] = None  # Driver's fastest lap in race
    gap_to_fastest_lap: Optional[str] = None  # Gap to fastest lap of race
    driver_s1_best: Optional[str] = None
    gap_to_s1_best: Optional[str] = None
    driver_s2_best: Optional[str] = None
    gap_to_s2_best: Optional[str] = None
    driver_s3_best: Optional[str] = None
    gap_to_s3_best: Optional[str] = None


class FactorVariable(BaseModel):
    """Variable contributing to a skill factor."""

    name: str
    display_name: str
    raw_value: float
    normalized_value: float = Field(..., ge=0, le=100)
    weight: float
    contribution: float
    percentile: float


class FactorBreakdownResponse(BaseModel):
    """Breakdown of a skill factor showing component variables."""

    factor_name: str
    overall_score: float
    percentile: float
    variables: List[FactorVariable]
    explanation: str
    strongest_area: str
    weakest_area: str


class TelemetryPoint(BaseModel):
    """Single telemetry data point."""

    distance: float  # Meters from start/finish
    time: float  # Seconds
    speed: float  # km/h
    throttle: float  # 0-100%
    brake: float  # 0-100%
    steering: float  # degrees or -1 to 1
    gear: Optional[int] = None


class CornerAnalysis(BaseModel):
    """Analysis of performance in a specific corner."""

    corner_number: int
    corner_name: str
    driver_apex_speed: float
    reference_apex_speed: float
    apex_speed_delta: float
    time_loss: float  # Seconds lost in this corner
    focus_area: str  # "Brake Point", "Apex Speed", "Throttle Application"
    driver_brake_point: Optional[float] = None  # Distance in meters
    reference_brake_point: Optional[float] = None


class TelemetryCoachingRequest(BaseModel):
    """Request for AI telemetry coaching."""

    driver_number: int
    reference_driver_number: int
    track_id: str
    race_num: int


class TelemetryCoachingResponse(BaseModel):
    """AI coaching response with telemetry analysis."""

    driver_number: int
    reference_driver_number: int
    track_name: str
    total_time_delta: float
    potential_time_gain: float
    corner_analysis: List[CornerAnalysis]
    ai_coaching: str  # Markdown-formatted coaching advice
    telemetry_insights: Dict[str, str]  # Overall patterns (braking, throttle, etc.)


class DriverFactorComparison(BaseModel):
    """Comparison data for one driver."""

    driver_number: int
    driver_name: str
    factor_score: float
    percentile: float
    variables: Dict[str, float]


class FactorComparisonResponse(BaseModel):
    """Factor comparison between user and top drivers."""

    factor_name: str
    user_driver: DriverFactorComparison
    top_drivers: List[DriverFactorComparison]
    insights: List[str]


# Improve Page Models

class AdjustedSkills(BaseModel):
    """User's adjusted skill levels for potential prediction."""

    speed: float = Field(..., ge=0, le=100, description="Speed percentile (0-100)")
    consistency: float = Field(..., ge=0, le=100, description="Consistency percentile (0-100)")
    racecraft: float = Field(..., ge=0, le=100, description="Racecraft percentile (0-100)")
    tire_management: float = Field(..., ge=0, le=100, description="Tire Management percentile (0-100)")


class PredictionWithUncertainty(BaseModel):
    """Prediction result with confidence intervals."""

    predicted_finish: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    confidence_level: str  # 'high', 'medium', 'low'
    is_extrapolating: bool
    warning_message: Optional[str] = None


class SimilarDriverMatch(BaseModel):
    """Similar driver match result."""

    driver_number: int
    driver_name: str
    similarity_score: float
    match_percentage: float
    skill_differences: Dict[str, float]
    predicted_finish: float
    key_strengths: List[str]


class ImprovementRecommendation(BaseModel):
    """Skill improvement recommendation."""

    factor_name: str
    display_name: str
    current_score: float
    current_percentile: float
    priority: int
    rationale: str
    impact_estimate: str
    drills: List[str]


class ImprovePredictionResponse(BaseModel):
    """Complete response for Improve page prediction."""

    driver_number: int
    current_skills: AdjustedSkills
    adjusted_skills: AdjustedSkills
    points_used: float
    points_available: float
    prediction: PredictionWithUncertainty
    similar_drivers: List[SimilarDriverMatch]
    recommendations: List[ImprovementRecommendation]


# 2K-Style Driver Development Models

class DriverTier(BaseModel):
    """Driver tier classification (2K-style)."""

    tier: str = Field(..., pattern="^(S|A|B|C|D)$", description="Tier: S (Elite), A (Great), B (Good), C (Average), D (Developing)")
    overall_rating: int = Field(..., ge=0, le=100, description="Overall rating 0-100")
    rank_in_tier: int = Field(..., description="Rank within this tier")
    total_in_tier: int = Field(..., description="Total drivers in this tier")
    next_tier_threshold: Optional[float] = Field(None, description="Score needed for next tier")


class RadarChartData(BaseModel):
    """Radar chart data for skill visualization."""

    speed: float = Field(..., ge=0, le=100)
    consistency: float = Field(..., ge=0, le=100)
    racecraft: float = Field(..., ge=0, le=100)
    tire_management: float = Field(..., ge=0, le=100)


class DriverProfile2K(BaseModel):
    """2K-style driver profile with tier and radar chart."""

    driver_number: int
    driver_name: str
    tier: DriverTier
    current_skills: RadarChartData
    season_stats: SeasonStats
    archetype: str = Field(..., description="Driver archetype: 'Speed Demon', 'Consistent Finisher', etc.")


class SkillAdjustment(BaseModel):
    """1% skill adjustment for what-if scenarios."""

    factor: str = Field(..., pattern="^(speed|consistency|racecraft|tire_management)$")
    adjustment_percent: float = Field(..., ge=-10, le=10, description="Adjustment in percentage points (-10 to +10)")


class TrainingDrill(BaseModel):
    """Specific training drill recommendation."""

    drill_name: str
    description: str
    focus_area: str
    duration: str
    difficulty: str = Field(..., pattern="^(Beginner|Intermediate|Advanced|Expert)$")
    expected_improvement: str


class TrainingPlan(BaseModel):
    """AI-generated training plan for skill improvement."""

    target_skill: str
    current_level: float
    target_level: float
    estimated_time: str
    drills: List[TrainingDrill]
    ai_coaching_summary: str


class WhatIfScenario(BaseModel):
    """What-if scenario result showing predicted outcomes."""

    scenario_name: str
    adjusted_skills: RadarChartData
    predicted_finish: float
    predicted_position_change: int
    similar_driver_match: SimilarDriverMatch
    training_plan: TrainingPlan
