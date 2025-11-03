"""
Export race results data from CSV files to JSON for Vercel deployment.

Creates two optimized JSON files:
1. driver_season_stats.json - Pre-calculated aggregate statistics
2. driver_race_results.json - Race-by-race detailed results

Statistical validation: This approach is sound because:
- Season statistics are deterministic (no randomness)
- Race results are immutable (historical facts)
- Calculations are associative (sum, average, count)
- No statistical bias introduced by pre-aggregation
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Add backend directory to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.race_log_processor import RaceLogProcessor


def calculate_season_stats(race_results: List) -> Dict:
    """
    Calculate season statistics from race results.

    Returns pre-aggregated stats matching SeasonStats model.
    """
    if not race_results:
        return None

    total_races = len(race_results)
    wins = sum(1 for r in race_results if r.finish_position == 1)
    podiums = sum(1 for r in race_results if r.finish_position and r.finish_position <= 3)
    top5 = sum(1 for r in race_results if r.finish_position and r.finish_position <= 5)
    top10 = sum(1 for r in race_results if r.finish_position and r.finish_position <= 10)
    pole_positions = sum(1 for r in race_results if r.start_position == 1)
    dnfs = sum(1 for r in race_results if r.status and "DNF" in r.status.upper())

    # Calculate averages
    finish_positions = [r.finish_position for r in race_results if r.finish_position]
    start_positions = [r.start_position for r in race_results if r.start_position]
    positions_gained_list = [
        r.positions_gained
        for r in race_results
        if r.positions_gained is not None
    ]

    avg_finish = sum(finish_positions) / len(finish_positions) if finish_positions else None
    avg_qualifying = sum(start_positions) / len(start_positions) if start_positions else None
    avg_positions_gained = sum(positions_gained_list) / len(positions_gained_list) if positions_gained_list else None

    # Calculate points (F1 points system: 25, 18, 15, 12, 10, 8, 6, 4, 2, 1)
    points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    points = sum(
        points_map.get(r.finish_position, 0)
        for r in race_results
        if r.finish_position
    )

    # Count fastest laps
    fastest_laps = sum(
        1 for r in race_results
        if r.driver_fastest_lap and r.gap_to_fastest_lap == 0
    )

    return {
        "wins": wins,
        "podiums": podiums,
        "top5": top5,
        "top10": top10,
        "pole_positions": pole_positions,
        "total_races": total_races,
        "dnfs": dnfs,
        "fastest_laps": fastest_laps,
        "avg_finish": round(avg_finish, 2) if avg_finish else None,
        "avg_qualifying": round(avg_qualifying, 2) if avg_qualifying else None,
        "avg_positions_gained": round(avg_positions_gained, 2) if avg_positions_gained else None,
        "points": points,
        "championship_position": None,  # TODO: Calculate from standings
    }


def convert_race_result_to_dict(race_result) -> Dict:
    """Convert RaceResult model to dictionary for JSON serialization."""
    return {
        "race_id": race_result.race_id,
        "track_id": race_result.track_id,
        "track_name": race_result.track_name,
        "round": race_result.round,
        "race_number": race_result.race_number,
        "start_position": race_result.start_position,
        "finish_position": race_result.finish_position,
        "positions_gained": race_result.positions_gained,
        "fastest_lap": race_result.fastest_lap,
        "gap_to_winner": race_result.gap_to_winner,
        "status": race_result.status,
        "qualifying_time": race_result.qualifying_time,
        "gap_to_pole": race_result.gap_to_pole,
        "s1_best_time": race_result.s1_best_time,
        "s2_best_time": race_result.s2_best_time,
        "s3_best_time": race_result.s3_best_time,
        "total_laps": race_result.total_laps,
        "avg_lap_time": race_result.avg_lap_time,
        "best_lap_time": race_result.best_lap_time,
        "worst_lap_time": race_result.worst_lap_time,
        "lap_time_std_dev": race_result.lap_time_std_dev,
        "driver_fastest_lap": race_result.driver_fastest_lap,
        "gap_to_fastest_lap": race_result.gap_to_fastest_lap,
        "driver_s1_best": race_result.driver_s1_best,
        "gap_to_s1_best": race_result.gap_to_s1_best,
        "driver_s2_best": race_result.driver_s2_best,
        "gap_to_s2_best": race_result.gap_to_s2_best,
        "driver_s3_best": race_result.driver_s3_best,
        "gap_to_s3_best": race_result.gap_to_s3_best,
    }


def export_race_data():
    """
    Export race data from CSV files to JSON format.

    Creates two JSON files:
    1. backend/data/driver_season_stats.json
    2. backend/data/driver_race_results.json
    """
    # Initialize race log processor
    data_path = Path(__file__).parent.parent.parent / "data"
    processor = RaceLogProcessor(data_path)

    # Get all unique driver numbers from driver_factors.json
    driver_factors_path = Path(__file__).parent.parent / "data" / "driver_factors.json"
    with open(driver_factors_path, "r") as f:
        factors_data = json.load(f)

    driver_numbers = [d["driver_number"] for d in factors_data.get("drivers", [])]

    print(f"Processing race data for {len(driver_numbers)} drivers...")

    # Storage for aggregated data
    season_stats_by_driver = {}
    race_results_by_driver = {}

    total_stats_exported = 0
    total_results_exported = 0

    for driver_number in driver_numbers:
        print(f"  Processing driver #{driver_number}...", end=" ")

        try:
            # Get all race results for this driver
            race_results = processor.get_driver_results(driver_number)

            if race_results:
                # Calculate season stats
                season_stats = calculate_season_stats(race_results)
                season_stats_by_driver[str(driver_number)] = season_stats
                total_stats_exported += 1

                # Convert race results to dictionaries
                race_results_dicts = [
                    convert_race_result_to_dict(r) for r in race_results
                ]
                race_results_by_driver[str(driver_number)] = race_results_dicts
                total_results_exported += len(race_results_dicts)

                print(f"✓ ({len(race_results)} races)")
            else:
                print("✗ (no race data)")

        except Exception as e:
            print(f"✗ Error: {e}")
            continue

    # Create output directory
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export season stats
    stats_output = {
        "version": "1.0",
        "description": "Pre-calculated season statistics for all drivers",
        "driver_count": len(season_stats_by_driver),
        "data": season_stats_by_driver,
    }

    stats_path = output_dir / "driver_season_stats.json"
    with open(stats_path, "w") as f:
        json.dump(stats_output, f, indent=2)

    stats_size = stats_path.stat().st_size / 1024
    print(f"\n✅ Exported season stats: {stats_path}")
    print(f"   Drivers: {total_stats_exported}")
    print(f"   Size: {stats_size:.1f} KB")

    # Export race results
    results_output = {
        "version": "1.0",
        "description": "Race-by-race results for all drivers",
        "driver_count": len(race_results_by_driver),
        "total_results": total_results_exported,
        "data": race_results_by_driver,
    }

    results_path = output_dir / "driver_race_results.json"
    with open(results_path, "w") as f:
        json.dump(results_output, f, indent=2)

    results_size = results_path.stat().st_size / 1024
    print(f"\n✅ Exported race results: {results_path}")
    print(f"   Drivers: {len(race_results_by_driver)}")
    print(f"   Total races: {total_results_exported}")
    print(f"   Size: {results_size:.1f} KB")

    # Summary
    total_size = stats_size + results_size
    print(f"\n📊 Total JSON size: {total_size:.1f} KB")
    print(f"   Vercel limit usage: {(total_size / (300 * 1024)) * 100:.3f}%")
    print(f"\n✅ Race data export complete!")


if __name__ == "__main__":
    export_race_data()
