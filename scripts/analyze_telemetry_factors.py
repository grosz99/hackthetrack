"""
Analyze Telemetry Features for Factor Structure

Determines if telemetry features form a 5th factor or load onto existing 4 factors.
Merges tier-1 features with telemetry features and runs exploratory factor analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
import warnings
warnings.filterwarnings('ignore')


def load_and_merge_data(base_path: Path) -> pd.DataFrame:
    """Load tier-1 and telemetry features and merge them."""
    # Load tier-1 features
    tier1_path = base_path / "data" / "analysis_outputs" / "all_races_tier1_features.csv"
    tier1_df = pd.read_csv(tier1_path)

    # Load telemetry features
    telemetry_path = base_path / "data" / "analysis_outputs" / "all_races_telemetry_features.csv"
    telemetry_df = pd.read_csv(telemetry_path)

    print(f"Tier-1 features: {len(tier1_df)} observations")
    print(f"Telemetry features: {len(telemetry_df)} observations")

    # Merge on race and driver_number
    merged = pd.merge(
        tier1_df,
        telemetry_df,
        on=['race', 'driver_number'],
        how='inner'
    )

    print(f"Merged dataset: {len(merged)} observations")
    print(f"Unique drivers: {merged['driver_number'].nunique()}")
    print(f"Unique races: {merged['race'].nunique()}")

    return merged


def prepare_features_for_efa(df: pd.DataFrame) -> tuple:
    """Prepare feature matrix for EFA."""
    # Tier-1 feature columns (same as original analysis)
    tier1_features = [
        'qualifying_pace', 'best_race_lap', 'avg_top10_pace',
        'stint_consistency', 'sector_consistency', 'braking_consistency',
        'pace_degradation', 'late_stint_perf', 'early_vs_late_pace',
        'position_changes', 'positions_gained', 'performance_normalized'
    ]

    # Telemetry feature columns
    telemetry_features = [
        'throttle_smoothness', 'steering_smoothness', 'accel_efficiency',
        'lateral_g_utilization', 'straight_speed_consistency',
        'braking_point_consistency', 'corner_efficiency'
    ]

    all_features = tier1_features + telemetry_features

    # Extract feature matrix
    X = df[all_features].copy()

    # Handle missing values (some races don't have 'aps' so throttle/accel are NaN)
    print("\nMissing values before imputation:")
    missing = X.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])

        # Drop columns with >50% missing
        high_missing = missing[missing > len(X) * 0.5].index.tolist()
        if high_missing:
            print(f"\nDropping columns with >50% missing: {high_missing}")
            X = X.drop(columns=high_missing)
            for col in high_missing:
                if col in telemetry_features:
                    telemetry_features.remove(col)
                if col in all_features:
                    all_features.remove(col)

        # Impute remaining missing with column mean
        X = X.fillna(X.mean())

    # Standardize (z-score normalization)
    X_standardized = (X - X.mean()) / X.std()

    return X_standardized, tier1_features, telemetry_features, all_features


def run_factor_analysis(X: pd.DataFrame, n_factors_range: range) -> dict:
    """Run EFA with different numbers of factors."""
    results = {}

    # Check factorability
    chi_square_value, p_value = calculate_bartlett_sphericity(X)
    kmo_all, kmo_model = calculate_kmo(X)

    print("\n" + "="*80)
    print("FACTORABILITY TESTS")
    print("="*80)
    print(f"Bartlett's Test of Sphericity:")
    print(f"  Chi-square = {chi_square_value:.2f}, p-value = {p_value:.2e}")
    print(f"  Result: {'✓ Data is factorable' if p_value < 0.05 else '✗ Data may not be factorable'}")
    print(f"\nKaiser-Meyer-Olkin (KMO) Test:")
    print(f"  Overall KMO = {kmo_model:.3f}")
    if kmo_model >= 0.90:
        print(f"  Result: ✓ Marvelous factorability")
    elif kmo_model >= 0.80:
        print(f"  Result: ✓ Meritorious factorability")
    elif kmo_model >= 0.70:
        print(f"  Result: ✓ Middling factorability")
    elif kmo_model >= 0.60:
        print(f"  Result: ⚠ Mediocre factorability")
    else:
        print(f"  Result: ✗ Unacceptable factorability")

    # Run EFA for different factor counts
    for n_factors in n_factors_range:
        fa = FactorAnalyzer(n_factors=n_factors, rotation='varimax', method='principal')
        fa.fit(X)

        # Get loadings
        loadings = pd.DataFrame(
            fa.loadings_,
            index=X.columns,
            columns=[f'Factor{i+1}' for i in range(n_factors)]
        )

        # Get variance explained
        variance = fa.get_factor_variance()

        results[n_factors] = {
            'model': fa,
            'loadings': loadings,
            'variance_explained': variance[1],  # Proportional variance
            'cumulative_variance': variance[2]   # Cumulative variance
        }

    return results


def analyze_telemetry_factor_contribution(
    loadings_4f: pd.DataFrame,
    loadings_5f: pd.DataFrame,
    tier1_features: list,
    telemetry_features: list
) -> None:
    """Analyze whether telemetry creates a 5th factor or loads onto existing factors."""

    print("\n" + "="*80)
    print("TELEMETRY FACTOR ANALYSIS")
    print("="*80)

    # Check if Factor 5 exists and is dominated by telemetry features
    if 'Factor5' in loadings_5f.columns:
        print("\n5-Factor Solution:")
        print("\nFactor 5 Loadings (sorted by absolute value):")
        factor5_loadings = loadings_5f['Factor5'].abs().sort_values(ascending=False)

        for feature in factor5_loadings.head(10).index:
            loading = loadings_5f.loc[feature, 'Factor5']
            feature_type = "TELEMETRY" if feature in telemetry_features else "Tier-1"
            print(f"  {feature:30s} {loading:7.3f}  [{feature_type}]")

        # Count telemetry vs tier-1 in top loadings
        top_5 = factor5_loadings.head(5).index
        telemetry_count = sum(1 for f in top_5 if f in telemetry_features)

        print(f"\nTop 5 loadings: {telemetry_count}/5 are telemetry features")

        if telemetry_count >= 3:
            print("✓ Factor 5 appears to be a DISTINCT TELEMETRY FACTOR")
        else:
            print("✗ Factor 5 is NOT dominated by telemetry - likely noise")

    # Analyze where telemetry features load in both solutions
    print("\n" + "="*80)
    print("WHERE DO TELEMETRY FEATURES LOAD?")
    print("="*80)

    for feature in telemetry_features:
        if feature not in loadings_4f.index:
            continue

        print(f"\n{feature}:")
        print("  4-Factor Solution:")
        loadings_4 = loadings_4f.loc[feature].abs()
        dominant_factor_4 = loadings_4.idxmax()
        print(f"    Dominant: {dominant_factor_4} (loading = {loadings_4f.loc[feature, dominant_factor_4]:.3f})")

        if 'Factor5' in loadings_5f.columns:
            print("  5-Factor Solution:")
            loadings_5 = loadings_5f.loc[feature].abs()
            dominant_factor_5 = loadings_5.idxmax()
            print(f"    Dominant: {dominant_factor_5} (loading = {loadings_5f.loc[feature, dominant_factor_5]:.3f})")


def main():
    """Main analysis pipeline."""
    base_path = Path(__file__).parent.parent

    # Load and merge data
    print("="*80)
    print("LOADING DATA")
    print("="*80)
    merged_df = load_and_merge_data(base_path)

    # Prepare features
    print("\n" + "="*80)
    print("PREPARING FEATURES")
    print("="*80)
    X, tier1_features, telemetry_features, all_features = prepare_features_for_efa(merged_df)
    print(f"Final feature count: {len(all_features)}")
    print(f"  Tier-1: {len(tier1_features)}")
    print(f"  Telemetry: {len(telemetry_features)}")
    print(f"Sample size: {len(X)}")

    # Run factor analysis with 4 and 5 factors
    print("\n" + "="*80)
    print("RUNNING EXPLORATORY FACTOR ANALYSIS")
    print("="*80)
    results = run_factor_analysis(X, range(4, 6))

    # Compare variance explained
    print("\n" + "="*80)
    print("VARIANCE EXPLAINED")
    print("="*80)

    for n_factors in [4, 5]:
        var_explained = results[n_factors]['variance_explained']
        cum_var = results[n_factors]['cumulative_variance']

        print(f"\n{n_factors}-Factor Solution:")
        for i in range(n_factors):
            print(f"  Factor {i+1}: {var_explained[i]*100:.1f}% (cumulative: {cum_var[i]*100:.1f}%)")
        print(f"  Total variance explained: {cum_var[-1]*100:.1f}%")

    # Analyze telemetry contribution
    analyze_telemetry_factor_contribution(
        results[4]['loadings'],
        results[5]['loadings'],
        tier1_features,
        telemetry_features
    )

    # Save detailed loadings
    output_path = base_path / "data" / "analysis_outputs"
    results[4]['loadings'].to_csv(output_path / "combined_4factor_loadings.csv")
    results[5]['loadings'].to_csv(output_path / "combined_5factor_loadings.csv")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"Loadings saved to {output_path}")


if __name__ == "__main__":
    main()
