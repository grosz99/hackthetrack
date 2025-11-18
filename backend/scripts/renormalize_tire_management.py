"""
Re-normalize tire management scores to have better spread.

Problem: Tire management scores are too compressed (everyone 50-70) due to low variance in raw data.
Solution: Apply percentile-based stretching to spread scores across 0-100 range while preserving ranking.
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats


def stretch_to_full_range(percentiles: list, min_output: float = 0, max_output: float = 100) -> list:
    """
    Stretch compressed percentiles to use full 0-100 range.

    Uses sigmoid-based stretching to maintain relative distances while expanding range.

    Args:
        percentiles: List of original percentile values
        min_output: Minimum output value (default 0)
        max_output: Maximum output value (default 100)

    Returns:
        List of stretched percentiles using full range
    """
    if not percentiles or len(percentiles) == 0:
        return []

    # Convert to numpy array
    arr = np.array(percentiles)

    # Get current min/max
    current_min = np.min(arr)
    current_max = np.max(arr)

    if current_max == current_min:
        # All values the same, return middle value
        return [50.0] * len(percentiles)

    # Method 1: Linear stretch to full range
    # This preserves exact percentile rankings while using full 0-100 scale
    stretched = min_output + (arr - current_min) / (current_max - current_min) * (max_output - min_output)

    return stretched.tolist()


def renormalize_tire_management():
    """Re-normalize tire management factor to have better score distribution."""

    # Load current driver factors
    factors_path = Path(__file__).parent.parent / "data" / "driver_factors.json"

    with open(factors_path, 'r') as f:
        data = json.load(f)

    print("Loading current driver factors...")
    print(f"Total drivers: {len(data['drivers'])}\n")

    # Extract current tire management percentiles
    tire_percentiles = []
    for driver in data['drivers']:
        tire_score = driver['factors']['tire_management']['percentile']
        tire_percentiles.append(tire_score)

    print("Current Tire Management Distribution:")
    print(f"  Min: {min(tire_percentiles):.1f}")
    print(f"  25th: {np.percentile(tire_percentiles, 25):.1f}")
    print(f"  Median: {np.median(tire_percentiles):.1f}")
    print(f"  75th: {np.percentile(tire_percentiles, 75):.1f}")
    print(f"  Max: {max(tire_percentiles):.1f}")
    print(f"  Std Dev: {np.std(tire_percentiles):.1f}\n")

    # Stretch to full 0-100 range
    stretched_percentiles = stretch_to_full_range(tire_percentiles, min_output=5, max_output=95)

    print("New Tire Management Distribution (after stretching):")
    print(f"  Min: {min(stretched_percentiles):.1f}")
    print(f"  25th: {np.percentile(stretched_percentiles, 25):.1f}")
    print(f"  Median: {np.median(stretched_percentiles):.1f}")
    print(f"  75th: {np.percentile(stretched_percentiles, 75):.1f}")
    print(f"  Max: {max(stretched_percentiles):.1f}")
    print(f"  Std Dev: {np.std(stretched_percentiles):.1f}\n")

    # Update driver factors with new tire management percentiles
    for i, driver in enumerate(data['drivers']):
        old_percentile = driver['factors']['tire_management']['percentile']
        new_percentile = round(stretched_percentiles[i], 2)
        driver['factors']['tire_management']['percentile'] = new_percentile

        # Also update the score to match (keep it simple - use percentile as score)
        driver['factors']['tire_management']['score'] = new_percentile

    # Write updated data back
    with open(factors_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Updated {len(data['drivers'])} drivers")
    print(f"   Written to: {factors_path}")

    # Show some examples
    print("\nExample transformations (first 10 drivers):")
    print(f"{'Driver':<8} {'Old %ile':<10} {'New %ile':<10} {'Change':<8}")
    print("-" * 40)
    for i, driver in enumerate(data['drivers'][:10]):
        old_val = tire_percentiles[i]
        new_val = stretched_percentiles[i]
        change = new_val - old_val
        print(f"#{driver['driver_number']:<7} {old_val:<10.1f} {new_val:<10.1f} {change:+.1f}")


if __name__ == "__main__":
    print("=" * 70)
    print("TIRE MANAGEMENT RE-NORMALIZATION")
    print("=" * 70)
    print()

    renormalize_tire_management()

    print("\nNext steps:")
    print("- Review the changes in driver_factors.json")
    print("- Re-export database: python3 export_db_to_json.py")
    print("- Deploy to Heroku")
