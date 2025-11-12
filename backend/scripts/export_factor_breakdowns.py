"""
Export factor breakdowns with REAL underlying variables from EFA analysis.

Uses actual Tier 1 EFA results with 12 variables that compose the 4 factors:
- Factor 1 (CONSISTENCY): braking_consistency, sector_consistency, stint_consistency, performance_normalized
- Factor 2 (RACECRAFT): positions_gained, position_changes
- Factor 3 (RAW SPEED): best_race_lap, avg_top10_pace, qualifying_pace, performance_normalized
- Factor 4 (TIRE MANAGEMENT): early_vs_late_pace, late_stint_perf
"""

import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Factor variable definitions with REAL loadings from Tier 1 EFA
FACTOR_VARIABLES = {
    "speed": {
        "explanation": "Raw Speed measures your ability to extract maximum pace from the car in qualifying and race conditions. It combines straight-line speed, cornering velocity, and optimal racing line execution.",
        "variables": [
            {
                "name": "qualifying_pace",
                "display_name": "Qualifying Pace",
                "loading": -0.693,
                "description": "One-lap qualifying speed relative to pole position"
            },
            {
                "name": "best_race_lap",
                "display_name": "Best Race Lap",
                "loading": -0.764,
                "description": "Fastest single lap during race conditions"
            },
            {
                "name": "avg_top10_pace",
                "display_name": "Top 10 Lap Average",
                "loading": -0.710,
                "description": "Average pace across best 10 race laps"
            },
        ]
    },
    "consistency": {
        "explanation": "Consistency measures lap-to-lap predictability and ability to maintain pace throughout a stint. Consistent drivers minimize variation, maximize tire life, and build confidence in race strategy.",
        "variables": [
            {
                "name": "braking_consistency",
                "display_name": "Braking Consistency",
                "loading": -0.934,
                "description": "Lap-to-lap consistency in braking zones"
            },
            {
                "name": "sector_consistency",
                "display_name": "Sector Consistency",
                "loading": -0.796,
                "description": "Consistency across all track sectors"
            },
            {
                "name": "stint_consistency",
                "display_name": "Stint Consistency",
                "loading": -0.469,
                "description": "Lap time variation during race stints"
            },
        ]
    },
    "racecraft": {
        "explanation": "Racecraft measures overtaking ability, defensive driving, and performance in traffic. Strong racecraft enables position gains, successful battles, and maintaining position under pressure.",
        "variables": [
            {
                "name": "positions_gained",
                "display_name": "Positions Gained",
                "loading": -0.857,
                "description": "Net positions gained from quali to finish"
            },
            {
                "name": "position_changes",
                "display_name": "Position Changes",
                "loading": -0.737,
                "description": "Lap-by-lap position changes during race"
            },
        ]
    },
    "tire_management": {
        "explanation": "Tire Management measures ability to preserve tire life while maintaining competitive pace. Good tire management enables longer stints, flexible strategy, and strong late-race pace.",
        "variables": [
            {
                "name": "early_vs_late_pace",
                "display_name": "Early vs Late Pace",
                "loading": 0.622,
                "description": "Ratio of early stint to late stint pace"
            },
            {
                "name": "late_stint_perf",
                "display_name": "Late Stint Performance",
                "loading": 0.470,
                "description": "Pace maintained in final third of race"
            },
        ]
    }
}


def normalize_value(raw_value: float, all_values: list, invert: bool = False) -> float:
    """
    Normalize value to 0-100 scale based on percentile rank.

    Args:
        raw_value: The value to normalize
        all_values: All values in the dataset for comparison
        invert: If True, lower raw values get higher normalized scores (for times/consistency metrics)

    Returns:
        Normalized value on 0-100 scale
    """
    if pd.isna(raw_value):
        return 50.0  # Default to median for missing values

    # Calculate percentile rank
    percentile = (np.sum(np.array(all_values) < raw_value) / len(all_values)) * 100

    # Invert if needed (for time-based metrics where lower is better)
    if invert:
        percentile = 100 - percentile

    return round(percentile, 2)


def calculate_percentile(value: float, all_values: list) -> float:
    """Calculate percentile rank of a value among all values."""
    if pd.isna(value) or not all_values:
        return 50.0

    sorted_values = sorted([v for v in all_values if not pd.isna(v)])
    rank = sum(1 for v in sorted_values if v < value)
    percentile = (rank / len(sorted_values)) * 100
    return round(percentile, 2)


def export_factor_breakdowns():
    """
    Export factor breakdowns using REAL EFA data.

    Reads from data/analysis_outputs/driver_average_scores_tier1.csv
    and data/analysis_outputs/all_races_tier1_features.csv
    """
    # Load the all races tier1 features data
    features_path = Path(__file__).parent.parent.parent / "data" / "analysis_outputs" / "all_races_tier1_features.csv"

    if not features_path.exists():
        print(f"❌ Error: Tier1 features file not found at {features_path}")
        return

    print(f"Loading EFA data from {features_path}")
    df = pd.read_csv(features_path)

    # Calculate driver averages for each variable
    driver_averages = df.groupby('driver_number').agg({
        'qualifying_pace': 'mean',
        'best_race_lap': 'mean',
        'avg_top10_pace': 'mean',
        'braking_consistency': 'mean',
        'sector_consistency': 'mean',
        'stint_consistency': 'mean',
        'positions_gained': 'mean',
        'position_changes': 'mean',
        'early_vs_late_pace': 'mean',
        'late_stint_perf': 'mean',
    }).reset_index()

    print(f"Processing {len(driver_averages)} drivers...")

    # Load existing driver factors for overall scores
    driver_factors_path = Path(__file__).parent.parent / "data" / "driver_factors.json"
    with open(driver_factors_path, "r") as f:
        factors_data = json.load(f)

    # Create lookup for overall factor scores
    factor_scores_lookup = {
        driver["driver_number"]: driver["factors"]
        for driver in factors_data["drivers"]
    }

    # Collect all variable values for percentile calculation
    all_variable_values = {}
    for factor_name, factor_config in FACTOR_VARIABLES.items():
        all_variable_values[factor_name] = {}
        for var in factor_config["variables"]:
            var_name = var["name"]
            all_variable_values[factor_name][var_name] = driver_averages[var_name].dropna().tolist()

    # Build driver breakdowns
    driver_breakdowns = {}

    for _, row in driver_averages.iterrows():
        driver_num = int(row['driver_number'])
        driver_breakdowns[driver_num] = {}

        for factor_name, factor_config in FACTOR_VARIABLES.items():
            driver_breakdowns[driver_num][factor_name] = {}

            for var in factor_config["variables"]:
                var_name = var["name"]
                raw_value = row[var_name]

                # Get all values for this variable
                all_vals = all_variable_values[factor_name][var_name]

                # Calculate percentile (for display)
                percentile = calculate_percentile(raw_value, all_vals)

                # Normalize to 0-100 scale
                # For consistency metrics (lower variance is better) and pace metrics (higher ratio is better)
                # we want to invert so better performance = higher score
                if var_name in ['braking_consistency', 'sector_consistency', 'stint_consistency']:
                    # Lower variance = better, so invert
                    normalized_value = 100 - normalize_value(raw_value, all_vals, invert=False)
                elif var_name in ['qualifying_pace', 'best_race_lap', 'avg_top10_pace', 'late_stint_perf', 'early_vs_late_pace']:
                    # Higher is better (normalized ratios)
                    normalized_value = normalize_value(raw_value, all_vals, invert=False)
                elif var_name in ['positions_gained', 'position_changes']:
                    # Higher is better (more positions gained/changed)
                    normalized_value = normalize_value(raw_value, all_vals, invert=False)
                else:
                    normalized_value = normalize_value(raw_value, all_vals, invert=False)

                driver_breakdowns[driver_num][factor_name][var_name] = {
                    "normalized_value": round(normalized_value, 2),
                    "raw_value": round(float(raw_value), 4) if not pd.isna(raw_value) else None,
                    "percentile": percentile,
                    "display_name": var["display_name"],
                    "loading": var["loading"],
                    "description": var["description"]
                }

    # Create output structure
    output = {
        "version": "2.0",
        "description": "Factor breakdowns with REAL underlying variables from Tier 1 EFA analysis",
        "driver_count": len(driver_averages),
        "data_source": "Tier 1 EFA - 12 variables, 291 observations, R²=0.895",
        "factor_definitions": FACTOR_VARIABLES,
        "driver_breakdowns": driver_breakdowns
    }

    # Export to JSON
    output_path = Path(__file__).parent.parent / "data" / "factor_breakdowns.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    output_size = output_path.stat().st_size / 1024
    print(f"\n✅ Exported REAL factor breakdowns: {output_path}")
    print(f"   Drivers: {len(driver_averages)}")
    print(f"   Factors: {len(FACTOR_VARIABLES)}")
    print(f"   Variables: {sum(len(f['variables']) for f in FACTOR_VARIABLES.values())}")
    print(f"   Size: {output_size:.1f} KB")
    print(f"\n✅ Factor breakdown export complete with REAL EFA data!")


if __name__ == "__main__":
    export_factor_breakdowns()
