"""
Simple corner detection using braking zones in telemetry data.
Identifies corners by finding where drivers brake (speed drops + brake applied).
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Track configurations (correct corner counts from research)
TRACK_CONFIGS = {
    "barber": {"name": "Barber Motorsports Park", "corners": 17, "length_miles": 2.3},
    "cota": {"name": "Circuit of the Americas", "corners": 20, "length_miles": 3.426},
    "roadamerica": {"name": "Road America", "corners": 14, "length_miles": 4.048},
    "sonoma": {"name": "Sonoma Raceway", "corners": 12, "length_miles": 2.22},
    "vir": {"name": "Virginia International Raceway", "corners": 17, "length_miles": 3.27}
}


def detect_corners_from_telemetry(track_id: str, race_num: int, data_path: Path) -> dict:
    """
    Detect corner locations by analyzing braking zones in telemetry.

    Strategy:
    1. Load one complete lap from fastest driver
    2. Find braking zones (speed decrease + brake pressure > threshold)
    3. Cluster nearby braking points into corners
    4. Return corner distance markers
    """
    telemetry_file = data_path / "telemetry" / "processed" / f"{track_id}_r{race_num}_wide.csv"

    if not telemetry_file.exists():
        raise FileNotFoundError(f"Telemetry file not found: {telemetry_file}")

    print(f"\n=== Analyzing {track_id.upper()} Race {race_num} ===")

    # Load full file to analyze (we need complete laps)
    print("Loading telemetry data...")
    df = pd.read_csv(telemetry_file)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    # Forward-fill distance data (interpolate between distance markers)
    df['Laptrigger_lapdist_dls'] = df.groupby(['vehicle_number', 'lap'])['Laptrigger_lapdist_dls'].ffill()

    # Get fastest driver (assuming vehicle_number with most clean laps)
    lap_counts = df.groupby('vehicle_number')['lap'].nunique()
    fastest_driver = lap_counts.idxmax()
    print(f"Analyzing driver #{fastest_driver} (most complete laps: {lap_counts[fastest_driver]})")

    # Get one clean lap from fastest driver
    driver_df = df[df['vehicle_number'] == fastest_driver].copy()

    # Sort by lap and distance
    driver_df = driver_df.sort_values(['lap', 'Laptrigger_lapdist_dls'])

    # Get a middle lap (avoid out/in laps)
    available_laps = driver_df['lap'].unique()
    if len(available_laps) < 3:
        selected_lap = available_laps[0]
    else:
        selected_lap = available_laps[len(available_laps) // 2]

    lap_df = driver_df[driver_df['lap'] == selected_lap].copy()
    print(f"Analyzing lap {selected_lap}: {len(lap_df)} data points")

    # Detect braking zones
    # Brake applied = pbrake_f > 5 bar (captures both heavy and light braking)
    lap_df['is_braking'] = (lap_df['pbrake_f'] > 5)

    # Find continuous braking zones
    lap_df['braking_zone'] = (lap_df['is_braking'] != lap_df['is_braking'].shift()).cumsum()

    # Filter to only actual braking zones
    braking_zones = lap_df[lap_df['is_braking']].groupby('braking_zone').agg({
        'Laptrigger_lapdist_dls': ['min', 'max', 'mean'],
        'pbrake_f': 'max',
        'speed': 'min'
    }).reset_index()

    braking_zones.columns = ['zone_id', 'dist_start', 'dist_end', 'dist_mid', 'max_brake', 'min_speed']

    # Filter out minor braking zones (max brake < 10 bar or zone < 15m)
    braking_zones['zone_length'] = braking_zones['dist_end'] - braking_zones['dist_start']
    significant_zones = braking_zones[
        (braking_zones['max_brake'] > 10) &
        (braking_zones['zone_length'] > 15)
    ].copy()

    print(f"\nDetected {len(significant_zones)} significant braking zones")
    print(f"Expected {TRACK_CONFIGS[track_id]['corners']} corners")

    # Create corner list
    corners = []
    for idx, zone in significant_zones.iterrows():
        corners.append({
            "corner_num": len(corners) + 1,
            "distance_m": round(zone['dist_mid'], 1),
            "braking_distance": round(zone['zone_length'], 1),
            "max_brake_bar": round(zone['max_brake'], 2),
            "min_speed_mph": round(zone['min_speed'], 1)
        })

    return {
        "track_id": track_id,
        "race_num": race_num,
        "expected_corners": TRACK_CONFIGS[track_id]["corners"],
        "detected_corners": len(corners),
        "corners": corners
    }


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent
    data_path = base_path / "data"

    # Test with Barber
    result = detect_corners_from_telemetry("barber", 1, data_path)
    print(f"\n=== RESULTS ===")
    print(f"Expected corners: {result['expected_corners']}")
    print(f"Detected corners: {result['detected_corners']}")
    print(f"\nCorner Details:")
    for corner in result['corners']:
        print(f"  Turn {corner['corner_num']}: {corner['distance_m']}m "
              f"(brake: {corner['max_brake_bar']} bar, "
              f"min speed: {corner['min_speed_mph']} mph)")
