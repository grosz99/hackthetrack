"""
Re-normalize ALL factor scores to ensure consistent spread across all dimensions.

Problem: Consistency and Racecraft are compressed, making driver differentiation difficult.
Solution: Apply percentile-based stretching to all factors for consistent 5-95 range.
"""

import json
import numpy as np
from pathlib import Path


def stretch_to_full_range(percentiles: list, min_output: float = 5, max_output: float = 95) -> list:
    """
    Stretch compressed percentiles to use full range while preserving rankings.

    Args:
        percentiles: List of original percentile values
        min_output: Minimum output value (default 5)
        max_output: Maximum output value (default 95)

    Returns:
        List of stretched percentiles using full range
    """
    if not percentiles or len(percentiles) == 0:
        return []

    arr = np.array(percentiles)
    current_min = np.min(arr)
    current_max = np.max(arr)

    if current_max == current_min:
        return [50.0] * len(percentiles)

    # Linear stretch to full range
    stretched = min_output + (arr - current_min) / (current_max - current_min) * (max_output - min_output)

    return stretched.tolist()


def analyze_and_renormalize_all_factors():
    """Analyze all factors and renormalize those with insufficient spread."""

    # Load current driver factors
    factors_path = Path(__file__).parent.parent / "data" / "driver_factors.json"
    with open(factors_path, 'r') as f:
        data = json.load(f)

    print("=" * 70)
    print("FACTOR NORMALIZATION ANALYSIS")
    print("=" * 70)
    print()

    factors = ['speed', 'consistency', 'racecraft', 'tire_management']

    # Target: all factors should have std dev >= 25 and range >= 80
    TARGET_STD_DEV = 25.0
    TARGET_RANGE = 80.0

    renormalized_count = 0

    for factor in factors:
        print(f"\n{factor.upper().replace('_', ' ')}:")
        print("-" * 70)

        # Extract current percentiles
        percentiles = []
        for driver in data['drivers']:
            percentiles.append(driver['factors'][factor]['percentile'])

        current_min = min(percentiles)
        current_max = max(percentiles)
        current_range = current_max - current_min
        current_std = np.std(percentiles)

        print(f"Current Distribution:")
        print(f"  Min:     {current_min:.1f}")
        print(f"  25th:    {np.percentile(percentiles, 25):.1f}")
        print(f"  Median:  {np.median(percentiles):.1f}")
        print(f"  75th:    {np.percentile(percentiles, 75):.1f}")
        print(f"  Max:     {current_max:.1f}")
        print(f"  Std Dev: {current_std:.1f}")
        print(f"  Range:   {current_range:.1f}")

        # Decide if renormalization is needed
        needs_renorm = current_std < TARGET_STD_DEV or current_range < TARGET_RANGE

        if needs_renorm:
            print(f"\n⚠️  RENORMALIZING: Std dev {current_std:.1f} < {TARGET_STD_DEV} or Range {current_range:.1f} < {TARGET_RANGE}")

            # Apply stretching
            stretched_percentiles = stretch_to_full_range(percentiles, min_output=5, max_output=95)

            new_min = min(stretched_percentiles)
            new_max = max(stretched_percentiles)
            new_range = new_max - new_min
            new_std = np.std(stretched_percentiles)

            print(f"\nNew Distribution:")
            print(f"  Min:     {new_min:.1f}")
            print(f"  25th:    {np.percentile(stretched_percentiles, 25):.1f}")
            print(f"  Median:  {np.median(stretched_percentiles):.1f}")
            print(f"  75th:    {np.percentile(stretched_percentiles, 75):.1f}")
            print(f"  Max:     {new_max:.1f}")
            print(f"  Std Dev: {new_std:.1f}")
            print(f"  Range:   {new_range:.1f}")
            print(f"  Improvement: Std Dev +{new_std - current_std:.1f}, Range +{new_range - current_range:.1f}")

            # Update driver data
            for i, driver in enumerate(data['drivers']):
                old_percentile = driver['factors'][factor]['percentile']
                new_percentile = round(stretched_percentiles[i], 2)
                driver['factors'][factor]['percentile'] = new_percentile
                driver['factors'][factor]['score'] = new_percentile

            renormalized_count += 1
            print(f"\n✅ Updated {len(data['drivers'])} drivers for {factor}")

        else:
            print(f"\n✅ Good spread - no renormalization needed")

    if renormalized_count > 0:
        # Write updated data back
        with open(factors_path, 'w') as f:
            json.dump(data, f, indent=2)

        print("\n" + "=" * 70)
        print(f"✅ RENORMALIZED {renormalized_count} factors")
        print(f"   Written to: {factors_path}")
        print("=" * 70)

        # Update dashboardData.json as well
        update_dashboard_data(data)
    else:
        print("\n" + "=" * 70)
        print("✅ All factors already have good spread")
        print("=" * 70)


def update_dashboard_data(factors_data):
    """Update dashboardData.json with new factor scores."""

    print("\nUpdating dashboardData.json...")

    # Create lookup for all factor scores
    factor_scores = {}
    for driver in factors_data['drivers']:
        driver_num = driver['driver_number']
        factor_scores[driver_num] = {
            'speed': {
                'score': driver['factors']['speed']['score'],
                'percentile': driver['factors']['speed']['percentile']
            },
            'consistency': {
                'score': driver['factors']['consistency']['score'],
                'percentile': driver['factors']['consistency']['percentile']
            },
            'racecraft': {
                'score': driver['factors']['racecraft']['score'],
                'percentile': driver['factors']['racecraft']['percentile']
            },
            'tire_management': {
                'score': driver['factors']['tire_management']['score'],
                'percentile': driver['factors']['tire_management']['percentile']
            }
        }

    # Load dashboardData.json
    dashboard_path = Path(__file__).parent.parent / "data" / "dashboardData.json"
    with open(dashboard_path, 'r') as f:
        dashboard_data = json.load(f)

    # Update all factors in dashboardData
    # Note: dashboardData uses different key names (raw_speed, tire_mgmt)
    factor_mapping = {
        'speed': 'raw_speed',
        'consistency': 'consistency',
        'racecraft': 'racecraft',
        'tire_management': 'tire_mgmt'
    }

    updated_count = 0
    for driver in dashboard_data['drivers']:
        driver_num = driver['number']
        if driver_num in factor_scores:
            for src_key, dst_key in factor_mapping.items():
                driver['factors'][dst_key]['score'] = factor_scores[driver_num][src_key]['score']
                driver['factors'][dst_key]['percentile'] = factor_scores[driver_num][src_key]['percentile']
            updated_count += 1

    # Write back
    with open(dashboard_path, 'w') as f:
        json.dump(dashboard_data, f, indent=2)

    print(f"✅ Updated {updated_count} drivers in dashboardData.json")


if __name__ == "__main__":
    analyze_and_renormalize_all_factors()

    print("\nNext steps:")
    print("- Review the changes in driver_factors.json and dashboardData.json")
    print("- Commit and push to GitHub")
    print("- Deploy to Heroku")
