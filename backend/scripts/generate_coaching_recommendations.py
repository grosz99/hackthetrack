#!/usr/bin/env python3
"""
Generate AI Coaching Recommendations for all drivers and factors.

Pre-calculates and stores personalized coaching recommendations using Claude API.
Run this script periodically or after data updates to refresh recommendations.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.ai_skill_coach import ai_skill_coach


def load_factor_breakdowns():
    """Load the factor breakdowns JSON file."""
    breakdowns_path = backend_path / "data" / "factor_breakdowns.json"

    if not breakdowns_path.exists():
        raise FileNotFoundError(
            f"Factor breakdowns not found at {breakdowns_path}. "
            "Run export_factor_breakdowns.py first."
        )

    with open(breakdowns_path, 'r') as f:
        return json.load(f)


def load_driver_data():
    """Load driver data to get percentiles and rankings."""
    drivers_path = backend_path / "data" / "driver_factors.json"

    if not drivers_path.exists():
        raise FileNotFoundError(f"Driver data not found at {drivers_path}")

    with open(drivers_path, 'r') as f:
        data = json.load(f)
        # Handle nested structure
        if isinstance(data, dict) and "drivers" in data:
            return data["drivers"]
        return data


def load_race_results():
    """Load race results for track-specific context."""
    results_path = backend_path / "data" / "driver_race_results.json"

    if not results_path.exists():
        print(f"Warning: Race results not found at {results_path}")
        return {}

    with open(results_path, 'r') as f:
        data = json.load(f)
        return data.get("data", {})


def load_driver_names():
    """Load driver names from dashboard data."""
    dashboard_path = backend_path / "data" / "dashboardData.json"

    if not dashboard_path.exists():
        print(f"Warning: Dashboard data not found at {dashboard_path}")
        return {}

    with open(dashboard_path, 'r') as f:
        data = json.load(f)
        drivers = data.get("drivers", [])

        # Create lookup: driver_number -> driver_name
        driver_names = {}
        for driver in drivers:
            driver_num = driver.get("number", driver.get("driverNumber"))
            driver_name = driver.get("name", f"Driver #{driver_num}")
            if driver_num:
                driver_names[str(driver_num)] = driver_name

        print(f"Loaded names for {len(driver_names)} drivers")
        return driver_names


def calculate_factor_rankings(drivers_data):
    """Calculate rankings for each factor across all drivers."""
    factors = ["speed", "consistency", "racecraft", "tire_management"]
    rankings = {}

    for factor in factors:
        driver_percentiles = []
        for driver in drivers_data:
            # Handle nested structure: driver.factors.speed.percentile
            if "factors" in driver and factor in driver["factors"]:
                factor_data = driver["factors"][factor]
                if "percentile" in factor_data:
                    driver_percentiles.append({
                        "driver_number": driver["driver_number"],
                        "percentile": factor_data["percentile"]
                    })
            # Also handle flat structure: driver.speed.percentile
            elif factor in driver and "percentile" in driver[factor]:
                driver_percentiles.append({
                    "driver_number": driver["driver_number"],
                    "percentile": driver[factor]["percentile"]
                })

        driver_percentiles.sort(key=lambda x: x["percentile"], reverse=True)

        rankings[factor] = {
            d["driver_number"]: {
                "rank": i + 1,
                "percentile": d["percentile"],
                "total": len(driver_percentiles)
            }
            for i, d in enumerate(driver_percentiles)
        }

    return rankings


def generate_all_recommendations(dry_run=False):
    """Generate coaching recommendations for all drivers and factors."""
    print("Loading data...")
    breakdowns_data = load_factor_breakdowns()
    drivers_data = load_driver_data()
    race_results = load_race_results()
    driver_names = load_driver_names()

    print("Calculating factor rankings...")
    factor_rankings = calculate_factor_rankings(drivers_data)

    factors = ["speed", "consistency", "racecraft", "tire_management"]
    driver_numbers = list(breakdowns_data["driver_breakdowns"].keys())

    print(f"Found {len(driver_numbers)} drivers and {len(factors)} factors")
    print(f"Total recommendations to generate: {len(driver_numbers) * len(factors)}")

    if dry_run:
        print("\n[DRY RUN] Would generate recommendations for:")
        for driver_num in driver_numbers[:3]:
            print(f"  Driver #{driver_num}: {', '.join(factors)}")
        print(f"  ... and {len(driver_numbers) - 3} more drivers")
        return

    recommendations = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_drivers": len(driver_numbers),
        "factors": factors,
        "recommendations": {}
    }

    total = len(driver_numbers) * len(factors)
    current = 0

    for driver_num in driver_numbers:
        driver_int = int(driver_num)
        recommendations["recommendations"][driver_num] = {}

        for factor_name in factors:
            current += 1
            print(f"[{current}/{total}] Generating {factor_name} coaching for driver #{driver_num}...")

            factor_def = breakdowns_data["factor_definitions"].get(factor_name)
            driver_breakdown = breakdowns_data["driver_breakdowns"].get(driver_num)

            if not factor_def or not driver_breakdown:
                print(f"  [SKIP] Missing data for driver #{driver_num} {factor_name}")
                continue

            factor_variables = driver_breakdown.get(factor_name)
            if not factor_variables:
                print(f"  [SKIP] No {factor_name} data for driver #{driver_num}")
                continue

            variables = []
            for var_config in factor_def["variables"]:
                var_name = var_config["name"]
                var_data = factor_variables.get(var_name, {})

                variables.append({
                    "name": var_name,
                    "display_name": var_data.get("display_name", var_name),
                    "percentile": var_data.get("percentile", 50.0),
                    "description": var_data.get("description", "")
                })

            ranking_info = factor_rankings.get(factor_name, {}).get(driver_int, {})
            user_rank = ranking_info.get("rank", 1)
            user_percentile = ranking_info.get("percentile", 50.0)
            total_drivers = ranking_info.get("total", len(driver_numbers))

            driver_races = race_results.get(driver_num, [])
            driver_display_name = driver_names.get(driver_num, f"Driver #{driver_num}")

            try:
                coaching_text = ai_skill_coach.generate_factor_coaching(
                    driver_number=driver_int,
                    factor_name=factor_name,
                    variables=variables,
                    overall_percentile=user_percentile,
                    rank_among_drivers=user_rank,
                    total_drivers=total_drivers,
                    race_results=driver_races,
                    driver_name=driver_display_name
                )

                recommendations["recommendations"][driver_num][factor_name] = {
                    "factor_percentile": user_percentile,
                    "factor_rank": user_rank,
                    "total_drivers": total_drivers,
                    "coaching_analysis": coaching_text,
                    "generated_at": datetime.utcnow().isoformat()
                }

                print(f"  [OK] Generated {len(coaching_text)} chars")

            except Exception as e:
                print(f"  [ERROR] Failed to generate: {e}")
                recommendations["recommendations"][driver_num][factor_name] = {
                    "factor_percentile": user_percentile,
                    "factor_rank": user_rank,
                    "total_drivers": total_drivers,
                    "coaching_analysis": None,
                    "error": str(e),
                    "generated_at": datetime.utcnow().isoformat()
                }

    output_path = backend_path / "data" / "coaching_recommendations.json"
    print(f"\nSaving recommendations to {output_path}...")

    with open(output_path, 'w') as f:
        json.dump(recommendations, f, indent=2)

    successful = sum(
        1 for driver_recs in recommendations["recommendations"].values()
        for rec in driver_recs.values()
        if rec.get("coaching_analysis") is not None
    )

    print(f"\nGeneration complete!")
    print(f"  Total recommendations: {total}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {total - successful}")
    print(f"  Output: {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate AI coaching recommendations")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without calling API"
    )

    args = parser.parse_args()

    generate_all_recommendations(dry_run=args.dry_run)
