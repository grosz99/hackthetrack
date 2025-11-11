"""
Turn-by-turn telemetry comparison for driver coaching.
Compares driver performance at key corners and generates specific insights.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

from track_corner_detector import detect_corners_from_telemetry, TRACK_CONFIGS


@dataclass
class CornerComparison:
    """Comparison data for a single corner."""
    corner_num: int
    distance_m: float

    # Target (fastest) driver metrics
    target_brake_point_m: float
    target_max_brake_bar: float
    target_min_speed_mph: float
    target_apex_distance_m: float

    # Current driver metrics
    current_brake_point_m: float
    current_max_brake_bar: float
    current_min_speed_mph: float
    current_apex_distance_m: float

    # Deltas
    brake_point_delta_m: float  # Negative = brake earlier, Positive = brake later
    speed_delta_mph: float  # Negative = slower, Positive = faster
    brake_pressure_delta_bar: float

    # Insight
    primary_insight: str
    factor_impact: str  # Which of the 4 factors this affects


def get_corner_metrics(
    telemetry_df: pd.DataFrame,
    driver_number: int,
    lap_number: int,
    corner_distance_m: float,
    window_m: float = 100
) -> Dict:
    """
    Extract metrics for a specific corner from telemetry.

    Args:
        telemetry_df: Full telemetry dataframe
        driver_number: Driver to analyze
        lap_number: Lap to analyze
        corner_distance_m: Distance marker for corner
        window_m: Window around corner to analyze (default 100m before/after)

    Returns:
        Dict with brake_point, max_brake, min_speed, apex_distance
    """
    # Get driver's lap data
    lap_df = telemetry_df[
        (telemetry_df['vehicle_number'] == driver_number) &
        (telemetry_df['lap'] == lap_number)
    ].copy()

    if lap_df.empty:
        return None

    # Get data in window around corner
    corner_df = lap_df[
        (lap_df['Laptrigger_lapdist_dls'] >= corner_distance_m - window_m) &
        (lap_df['Laptrigger_lapdist_dls'] <= corner_distance_m + window_m)
    ].copy()

    if corner_df.empty:
        return None

    # Find braking point (first point where brake > 20 bar)
    braking_rows = corner_df[corner_df['pbrake_f'] > 20]
    if not braking_rows.empty:
        brake_point = braking_rows.iloc[0]['Laptrigger_lapdist_dls']
    else:
        brake_point = corner_distance_m  # No braking detected

    # Find max brake pressure in window
    max_brake = corner_df['pbrake_f'].max()

    # Find minimum speed (apex speed)
    min_speed_row = corner_df.loc[corner_df['speed'].idxmin()]
    min_speed = min_speed_row['speed']
    apex_distance = min_speed_row['Laptrigger_lapdist_dls']

    return {
        'brake_point': brake_point,
        'max_brake': max_brake,
        'min_speed': min_speed,
        'apex_distance': apex_distance
    }


def compare_drivers_at_corners(
    track_id: str,
    race_num: int,
    current_driver: int,
    target_driver: int,
    data_path: Path
) -> List[CornerComparison]:
    """
    Compare two drivers at all key corners of a track.

    Args:
        track_id: Track identifier (e.g., 'barber')
        race_num: Race number
        current_driver: Driver number to analyze
        target_driver: Driver number to compare against (fastest)
        data_path: Path to data directory

    Returns:
        List of CornerComparison objects
    """
    # Detect corners for this track
    corner_data = detect_corners_from_telemetry(track_id, race_num, data_path)
    corners = corner_data['corners']

    # Load telemetry
    telemetry_file = data_path / "telemetry" / "processed" / f"{track_id}_r{race_num}_wide.csv"
    print(f"Loading telemetry from {telemetry_file}...")
    df = pd.read_csv(telemetry_file)

    # Forward-fill distance data
    df['Laptrigger_lapdist_dls'] = df.groupby(['vehicle_number', 'lap'])['Laptrigger_lapdist_dls'].ffill()

    # Select middle laps for comparison (avoid in/out laps)
    current_laps = df[df['vehicle_number'] == current_driver]['lap'].unique()
    target_laps = df[df['vehicle_number'] == target_driver]['lap'].unique()

    if len(current_laps) < 3 or len(target_laps) < 3:
        print("Not enough laps for comparison")
        return []

    current_lap = current_laps[len(current_laps) // 2]
    target_lap = target_laps[len(target_laps) // 2]

    print(f"Comparing driver #{current_driver} (lap {current_lap}) vs driver #{target_driver} (lap {target_lap})")

    comparisons = []

    for corner in corners:
        corner_num = corner['corner_num']
        corner_dist = corner['distance_m']

        # Get metrics for both drivers
        target_metrics = get_corner_metrics(df, target_driver, target_lap, corner_dist)
        current_metrics = get_corner_metrics(df, current_driver, current_lap, corner_dist)

        if not target_metrics or not current_metrics:
            continue

        # Calculate deltas
        brake_delta = current_metrics['brake_point'] - target_metrics['brake_point']
        speed_delta = current_metrics['min_speed'] - target_metrics['min_speed']
        brake_pressure_delta = current_metrics['max_brake'] - target_metrics['max_brake']

        # Generate insight
        insight, factor = generate_corner_insight(
            corner_num, brake_delta, speed_delta, brake_pressure_delta
        )

        comparisons.append(CornerComparison(
            corner_num=corner_num,
            distance_m=corner_dist,
            target_brake_point_m=target_metrics['brake_point'],
            target_max_brake_bar=target_metrics['max_brake'],
            target_min_speed_mph=target_metrics['min_speed'],
            target_apex_distance_m=target_metrics['apex_distance'],
            current_brake_point_m=current_metrics['brake_point'],
            current_max_brake_bar=current_metrics['max_brake'],
            current_min_speed_mph=current_metrics['min_speed'],
            current_apex_distance_m=current_metrics['apex_distance'],
            brake_point_delta_m=brake_delta,
            speed_delta_mph=speed_delta,
            brake_pressure_delta_bar=brake_pressure_delta,
            primary_insight=insight,
            factor_impact=factor
        ))

    return comparisons


def generate_corner_insight(
    corner_num: int,
    brake_delta_m: float,
    speed_delta_mph: float,
    brake_pressure_delta_bar: float
) -> Tuple[str, str]:
    """
    Generate specific coaching insight for a corner.

    Returns:
        (insight_text, factor_affected)
    """
    insights = []
    factor = "Speed"  # Default

    # Determine primary issue
    # If faster through apex but not braking hard enough, might be overslowing or poor exit
    if speed_delta_mph > 3 and brake_pressure_delta_bar < -20:
        # Faster apex but less brake pressure = might be carrying speed wrong way
        insights.append(f"You're {speed_delta_mph:.1f} mph faster at apex but using {abs(brake_pressure_delta_bar):.0f} bar less brake. Focus on harder braking and better corner exit")
        factor = "Racecraft"  # Corner execution technique

    # If slower through apex, need more speed
    elif speed_delta_mph < -3:
        insights.append(f"You're {abs(speed_delta_mph):.1f} mph SLOWER at apex. Carry more speed through the corner")
        factor = "Speed"

    # Braking point consistency
    if brake_delta_m < -15:
        insights.append(f"Brake {abs(brake_delta_m):.0f}m LATER (currently braking too early)")
        factor = "Consistency"  # Braking consistency
    elif brake_delta_m > 15:
        insights.append(f"Brake {brake_delta_m:.0f}m EARLIER (currently braking too late)")
        factor = "Consistency"

    # If good execution
    if abs(speed_delta_mph) < 3 and abs(brake_delta_m) < 15:
        insights.append("Corner execution is similar to fastest driver ✓")

    if not insights:
        insights.append("Minor differences only")

    insight_text = f"Turn {corner_num}: " + ". ".join(insights)

    return insight_text, factor


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent
    data_path = base_path / "data"

    # Test: Compare driver 7 vs driver 0 (fastest) at Barber
    print("\n=== DRIVER COMPARISON: #7 vs #0 (fastest) ===\n")

    comparisons = compare_drivers_at_corners(
        track_id="barber",
        race_num=1,
        current_driver=7,
        target_driver=0,
        data_path=data_path
    )

    print(f"\n=== COACHING INSIGHTS ({len(comparisons)} corners analyzed) ===\n")

    for comp in comparisons:
        print(comp.primary_insight)
        print(f"  → Impacts: {comp.factor_impact} factor")
        print(f"  → Target speed: {comp.target_min_speed_mph:.1f} mph | Your speed: {comp.current_min_speed_mph:.1f} mph")
        print(f"  → Target brake point: {comp.target_brake_point_m:.0f}m | Your brake point: {comp.current_brake_point_m:.0f}m")
        print()
