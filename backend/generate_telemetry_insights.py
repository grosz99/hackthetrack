"""
Pre-calculate and aggregate telemetry coaching insights for all drivers.
Stores results as JSON for fast API access.
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List
from telemetry_comparison import compare_drivers_at_corners, TRACK_CONFIGS


def find_fastest_driver(track_id: str, race_num: int, data_path: Path) -> int:
    """Find the fastest driver at a track based on most consistent laps."""
    telemetry_file = data_path / "telemetry" / "processed" / f"{track_id}_r{race_num}_wide.csv"

    df = pd.read_csv(telemetry_file, nrows=50000)  # Sample to find drivers

    # Count laps per driver (more laps = more consistent/faster)
    lap_counts = df.groupby('vehicle_number')['lap'].nunique()
    fastest_driver = lap_counts.idxmax()

    return int(fastest_driver)


def aggregate_driver_insights(
    track_id: str,
    race_num: int,
    driver_number: int,
    target_driver: int,
    data_path: Path
) -> Dict:
    """
    Generate aggregated coaching insights for a driver at a specific track.

    Returns:
        {
            "track_id": "barber",
            "race_num": 1,
            "driver_number": 7,
            "target_driver": 0,
            "summary": {
                "total_corners": 7,
                "corners_on_pace": 3,
                "corners_need_work": 4,
                "primary_weakness": "Braking Consistency"
            },
            "key_insights": [
                "Turn 5: Brake 74m earlier (Consistency)",
                "Turn 1: Focus on harder braking (Racecraft)"
            ],
            "factor_breakdown": {
                "Speed": 0,
                "Consistency": 2,
                "Racecraft": 2,
                "Tire Management": 0
            }
        }
    """
    print(f"\nAnalyzing driver #{driver_number} at {track_id} R{race_num}...")

    try:
        comparisons = compare_drivers_at_corners(
            track_id=track_id,
            race_num=race_num,
            current_driver=driver_number,
            target_driver=target_driver,
            data_path=data_path
        )

        if not comparisons:
            return None

        # Count corners by status
        corners_on_pace = sum(1 for c in comparisons if "similar to fastest" in c.primary_insight)
        corners_need_work = len(comparisons) - corners_on_pace

        # Count issues by factor
        factor_counts = {}
        for comp in comparisons:
            factor = comp.factor_impact
            factor_counts[factor] = factor_counts.get(factor, 0) + 1

        # Find primary weakness (most affected factor)
        if factor_counts:
            primary_weakness = max(factor_counts, key=factor_counts.get)
        else:
            primary_weakness = "None"

        # Extract top 3 most important insights (skip "similar to fastest")
        key_insights = []
        for comp in comparisons:
            if "similar to fastest" not in comp.primary_insight:
                key_insights.append(comp.primary_insight)

        key_insights = key_insights[:5]  # Top 5 insights max

        return {
            "track_id": track_id,
            "race_num": race_num,
            "driver_number": driver_number,
            "target_driver": target_driver,
            "summary": {
                "total_corners": len(comparisons),
                "corners_on_pace": corners_on_pace,
                "corners_need_work": corners_need_work,
                "primary_weakness": primary_weakness
            },
            "key_insights": key_insights,
            "factor_breakdown": factor_counts,
            "detailed_comparisons": [
                {
                    "corner_num": c.corner_num,
                    "distance_m": round(c.distance_m, 1),
                    "insight": c.primary_insight,
                    "factor": c.factor_impact,
                    "speed_delta_mph": round(c.speed_delta_mph, 1),
                    "brake_delta_m": round(c.brake_point_delta_m, 1)
                }
                for c in comparisons
            ]
        }

    except Exception as e:
        print(f"Error analyzing driver #{driver_number}: {e}")
        return None


def generate_all_insights(data_path: Path, output_path: Path):
    """
    Generate telemetry insights for all drivers at all tracks.
    Stores results as JSON.
    """
    # Tracks with telemetry data (start with just Barber for testing)
    tracks = ["barber"]  # ["barber", "cota", "roadamerica", "sonoma", "vir"]

    all_insights = {}

    for track_id in tracks:
        print(f"\n{'='*60}")
        print(f"Processing {track_id.upper()}")
        print(f"{'='*60}")

        # Process both races
        for race_num in [1, 2]:
            telemetry_file = data_path / "telemetry" / "processed" / f"{track_id}_r{race_num}_wide.csv"

            if not telemetry_file.exists():
                print(f"Skipping {track_id} R{race_num} - no telemetry file")
                continue

            # Find fastest driver
            target_driver = find_fastest_driver(track_id, race_num, data_path)
            print(f"Target (fastest) driver: #{target_driver}")

            # Get all unique drivers from telemetry features
            features_file = data_path / "analysis_outputs" / f"{track_id}_r{race_num}_telemetry_features.csv"
            if features_file.exists():
                features_df = pd.read_csv(features_file)
                drivers = features_df['driver_number'].unique().tolist()
            else:
                # Fallback: sample from telemetry
                df = pd.read_csv(telemetry_file, nrows=10000)
                drivers = df['vehicle_number'].unique().tolist()

            print(f"Analyzing {len(drivers)} drivers...")

            track_race_key = f"{track_id}_r{race_num}"
            all_insights[track_race_key] = {}

            for driver in drivers:
                driver = int(driver)

                if driver == target_driver:
                    # Skip comparing fastest driver to themselves
                    continue

                insights = aggregate_driver_insights(
                    track_id=track_id,
                    race_num=race_num,
                    driver_number=driver,
                    target_driver=target_driver,
                    data_path=data_path
                )

                if insights:
                    all_insights[track_race_key][str(driver)] = insights
                    print(f"  ✓ Driver #{driver}: {insights['summary']['corners_need_work']}/{insights['summary']['total_corners']} corners need work")

    # Save to JSON
    output_file = output_path / "telemetry_coaching_insights.json"
    with open(output_file, 'w') as f:
        json.dump(all_insights, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✓ Saved insights to {output_file}")
    print(f"Total tracks processed: {len(tracks)}")
    print(f"Total driver insights: {sum(len(races) for races in all_insights.values())}")
    print(f"{'='*60}")


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent
    data_path = base_path / "data"
    output_path = base_path / "backend" / "data"
    output_path.mkdir(exist_ok=True)

    generate_all_insights(data_path, output_path)
