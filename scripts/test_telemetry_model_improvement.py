"""
Test if Telemetry Features Improve Prediction Model

Compares baseline 4-factor model vs enhanced model with telemetry features.
Uses Leave-One-Driver-Out cross-validation for rigorous comparison.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


def load_data(base_path: Path) -> pd.DataFrame:
    """Load tier-1 features, factor scores, and telemetry features."""
    # Load tier-1 features with finishing position
    tier1_path = base_path / "data" / "analysis_outputs" / "all_races_tier1_features.csv"
    tier1_df = pd.read_csv(tier1_path)

    # Load factor scores (with reflection already applied)
    factor_scores_path = base_path / "data" / "analysis_outputs" / "tier1_factor_scores.csv"
    factor_scores_df = pd.read_csv(factor_scores_path)

    # Apply reflection (in case not already done)
    FACTORS_TO_REFLECT = {
        "factor_1_score": True,
        "factor_2_score": True,
        "factor_3_score": True,
        "factor_4_score": False,
    }
    for factor_col, should_reflect in FACTORS_TO_REFLECT.items():
        if should_reflect and factor_col in factor_scores_df.columns:
            # Check if already reflected (positive correlation with good performance)
            if factor_scores_df[factor_col].mean() < 0:
                factor_scores_df[factor_col] = -1 * factor_scores_df[factor_col]

    # Load telemetry features
    telemetry_path = base_path / "data" / "analysis_outputs" / "all_races_telemetry_features.csv"
    telemetry_df = pd.read_csv(telemetry_path)

    # Merge tier-1 with factor scores (drop finishing_position from factor scores to avoid duplicate)
    factor_scores_clean = factor_scores_df.drop(columns=['finishing_position'], errors='ignore')
    merged = pd.merge(
        tier1_df[['race', 'driver_number', 'finishing_position']],
        factor_scores_clean,
        on=['race', 'driver_number'],
        how='inner'
    )

    # Merge with telemetry
    merged = pd.merge(
        merged,
        telemetry_df[['race', 'driver_number', 'steering_smoothness', 'lateral_g_utilization']],
        on=['race', 'driver_number'],
        how='inner'
    )

    # Drop rows with missing values
    merged = merged.dropna()

    print(f"Final dataset: {len(merged)} observations")
    print(f"Unique drivers: {merged['driver_number'].nunique()}")
    print(f"Unique races: {merged['race'].nunique()}")

    return merged


def average_by_driver(df: pd.DataFrame) -> pd.DataFrame:
    """Average all features and outcomes by driver (across all races)."""
    # Group by driver and average
    driver_avg = df.groupby('driver_number').agg({
        'finishing_position': 'mean',
        'factor_1_score': 'mean',
        'factor_2_score': 'mean',
        'factor_3_score': 'mean',
        'factor_4_score': 'mean',
        'steering_smoothness': 'mean',
        'lateral_g_utilization': 'mean'
    }).reset_index()

    return driver_avg


def lodo_cv_comparison(df: pd.DataFrame) -> dict:
    """
    Compare baseline vs telemetry-enhanced model using LODO-CV.

    Returns dictionary with performance metrics for both models.
    """
    drivers = df['driver_number'].unique()

    # Storage for predictions
    baseline_predictions = []
    enhanced_predictions = []
    actual_positions = []

    print("\nRunning Leave-One-Driver-Out Cross-Validation...")
    print("="*80)

    for held_out_driver in drivers:
        # Split data
        train_df = df[df['driver_number'] != held_out_driver]
        test_df = df[df['driver_number'] == held_out_driver]

        # Baseline model: 4 factors only
        X_train_baseline = train_df[['factor_1_score', 'factor_2_score',
                                       'factor_3_score', 'factor_4_score']]
        y_train = train_df['finishing_position']

        X_test_baseline = test_df[['factor_1_score', 'factor_2_score',
                                     'factor_3_score', 'factor_4_score']]
        y_test = test_df['finishing_position']

        # Enhanced model: 4 factors + 2 telemetry features
        X_train_enhanced = train_df[['factor_1_score', 'factor_2_score',
                                       'factor_3_score', 'factor_4_score',
                                       'steering_smoothness', 'lateral_g_utilization']]
        X_test_enhanced = test_df[['factor_1_score', 'factor_2_score',
                                     'factor_3_score', 'factor_4_score',
                                     'steering_smoothness', 'lateral_g_utilization']]

        # Train and predict - Baseline
        model_baseline = LinearRegression()
        model_baseline.fit(X_train_baseline, y_train)
        pred_baseline = model_baseline.predict(X_test_baseline)[0]

        # Train and predict - Enhanced
        model_enhanced = LinearRegression()
        model_enhanced.fit(X_train_enhanced, y_train)
        pred_enhanced = model_enhanced.predict(X_test_enhanced)[0]

        # Store results
        baseline_predictions.append(pred_baseline)
        enhanced_predictions.append(pred_enhanced)
        actual_positions.append(y_test.values[0])

        # Print progress every 10 drivers
        if len(baseline_predictions) % 10 == 0:
            print(f"  Processed {len(baseline_predictions)}/{len(drivers)} drivers...")

    # Calculate metrics
    baseline_r2 = r2_score(actual_positions, baseline_predictions)
    enhanced_r2 = r2_score(actual_positions, enhanced_predictions)

    baseline_mae = mean_absolute_error(actual_positions, baseline_predictions)
    enhanced_mae = mean_absolute_error(actual_positions, enhanced_predictions)

    # Calculate errors
    baseline_errors = np.array(actual_positions) - np.array(baseline_predictions)
    enhanced_errors = np.array(actual_positions) - np.array(enhanced_predictions)

    # Statistical significance test (paired t-test on absolute errors)
    baseline_abs_errors = np.abs(baseline_errors)
    enhanced_abs_errors = np.abs(enhanced_errors)

    t_stat, p_value = stats.ttest_rel(baseline_abs_errors, enhanced_abs_errors)

    return {
        'baseline': {
            'r2': baseline_r2,
            'mae': baseline_mae,
            'predictions': baseline_predictions,
            'errors': baseline_errors,
            'abs_errors': baseline_abs_errors
        },
        'enhanced': {
            'r2': enhanced_r2,
            'mae': enhanced_mae,
            'predictions': enhanced_predictions,
            'errors': enhanced_errors,
            'abs_errors': enhanced_abs_errors
        },
        'actual': actual_positions,
        'drivers': drivers,
        't_stat': t_stat,
        'p_value': p_value
    }


def print_results(results: dict):
    """Print comprehensive comparison results."""
    print("\n" + "="*80)
    print("MODEL COMPARISON RESULTS (Leave-One-Driver-Out Cross-Validation)")
    print("="*80)

    print("\nBASELINE MODEL (4 Factors Only):")
    print(f"  Out-of-sample R² = {results['baseline']['r2']:.4f}")
    print(f"  Mean Absolute Error = ±{results['baseline']['mae']:.2f} positions")
    print(f"  Variance Explained = {results['baseline']['r2']*100:.1f}%")

    print("\nENHANCED MODEL (4 Factors + 2 Telemetry Features):")
    print(f"  Out-of-sample R² = {results['enhanced']['r2']:.4f}")
    print(f"  Mean Absolute Error = ±{results['enhanced']['mae']:.2f} positions")
    print(f"  Variance Explained = {results['enhanced']['r2']*100:.1f}%")

    print("\n" + "="*80)
    print("IMPROVEMENT ANALYSIS")
    print("="*80)

    r2_improvement = results['enhanced']['r2'] - results['baseline']['r2']
    r2_pct_improvement = (r2_improvement / results['baseline']['r2']) * 100
    mae_improvement = results['baseline']['mae'] - results['enhanced']['mae']
    mae_pct_improvement = (mae_improvement / results['baseline']['mae']) * 100

    print(f"\nR² Improvement:")
    print(f"  Absolute: {r2_improvement:+.4f}")
    print(f"  Percentage: {r2_pct_improvement:+.1f}%")
    print(f"  Additional variance explained: {r2_improvement*100:.1f}%")

    print(f"\nMAE Improvement:")
    print(f"  Absolute: {mae_improvement:+.3f} positions")
    print(f"  Percentage: {mae_pct_improvement:+.1f}%")

    print(f"\nStatistical Significance (Paired t-test on absolute errors):")
    print(f"  t-statistic = {results['t_stat']:.3f}")
    print(f"  p-value = {results['p_value']:.4f}")

    if results['p_value'] < 0.01:
        print(f"  Result: *** HIGHLY SIGNIFICANT improvement (p < 0.01)")
    elif results['p_value'] < 0.05:
        print(f"  Result: ** SIGNIFICANT improvement (p < 0.05)")
    elif results['p_value'] < 0.10:
        print(f"  Result: * MARGINALLY SIGNIFICANT improvement (p < 0.10)")
    else:
        print(f"  Result: NOT statistically significant (p >= 0.10)")

    # Practical significance
    print("\n" + "="*80)
    print("PRACTICAL SIGNIFICANCE")
    print("="*80)

    if r2_improvement > 0.05:
        print(f"✓ R² improvement of {r2_improvement*100:.1f}% is SUBSTANTIAL")
    elif r2_improvement > 0.02:
        print(f"⚠ R² improvement of {r2_improvement*100:.1f}% is MODERATE")
    elif r2_improvement > 0:
        print(f"⚠ R² improvement of {r2_improvement*100:.1f}% is SMALL")
    else:
        print(f"✗ R² decreased by {abs(r2_improvement)*100:.1f}%")

    if mae_improvement > 0.2:
        print(f"✓ MAE improvement of {mae_improvement:.2f} positions is SUBSTANTIAL")
    elif mae_improvement > 0.1:
        print(f"⚠ MAE improvement of {mae_improvement:.2f} positions is MODERATE")
    elif mae_improvement > 0:
        print(f"⚠ MAE improvement of {mae_improvement:.2f} positions is SMALL")
    else:
        print(f"✗ MAE worsened by {abs(mae_improvement):.2f} positions")

    # Overall recommendation
    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)

    if results['p_value'] < 0.05 and r2_improvement > 0.02:
        print("✓ RECOMMEND: Include telemetry features in production model")
        print("  - Statistically significant improvement")
        print("  - Practically meaningful increase in predictive power")
    elif results['p_value'] < 0.05:
        print("⚠ CONSIDER: Telemetry features show statistical improvement")
        print("  - Statistically significant but small practical effect")
    elif r2_improvement > 0.05:
        print("⚠ CONSIDER: Telemetry features show large improvement")
        print("  - Large effect but not yet statistically significant (may need more data)")
    else:
        print("✗ DO NOT RECOMMEND: Telemetry features do not improve model")
        print("  - Insufficient statistical or practical significance")


def save_comparison_report(results: dict, output_path: Path):
    """Save detailed comparison to CSV."""
    comparison_df = pd.DataFrame({
        'driver_number': results['drivers'],
        'actual_position': results['actual'],
        'baseline_prediction': results['baseline']['predictions'],
        'enhanced_prediction': results['enhanced']['predictions'],
        'baseline_error': results['baseline']['errors'],
        'enhanced_error': results['enhanced']['errors'],
        'baseline_abs_error': results['baseline']['abs_errors'],
        'enhanced_abs_error': results['enhanced']['abs_errors']
    })

    comparison_df = comparison_df.sort_values('baseline_abs_error', ascending=False)

    output_file = output_path / "telemetry_model_comparison.csv"
    comparison_df.to_csv(output_file, index=False)
    print(f"\nDetailed comparison saved to: {output_file}")

    # Show top 5 most improved predictions
    comparison_df['improvement'] = comparison_df['baseline_abs_error'] - comparison_df['enhanced_abs_error']

    print("\n" + "="*80)
    print("TOP 5 MOST IMPROVED PREDICTIONS:")
    print("="*80)
    top_improved = comparison_df.nlargest(5, 'improvement')
    for _, row in top_improved.iterrows():
        print(f"  Driver #{int(row['driver_number'])}: {row['improvement']:+.2f} positions better")
        print(f"    Baseline error: {row['baseline_abs_error']:.2f} → Enhanced error: {row['enhanced_abs_error']:.2f}")

    print("\n" + "="*80)
    print("TOP 5 MOST WORSENED PREDICTIONS:")
    print("="*80)
    top_worsened = comparison_df.nsmallest(5, 'improvement')
    for _, row in top_worsened.iterrows():
        print(f"  Driver #{int(row['driver_number'])}: {row['improvement']:+.2f} positions worse")
        print(f"    Baseline error: {row['baseline_abs_error']:.2f} → Enhanced error: {row['enhanced_abs_error']:.2f}")


def main():
    """Main analysis pipeline."""
    base_path = Path(__file__).parent.parent

    print("="*80)
    print("TELEMETRY MODEL IMPROVEMENT TEST")
    print("="*80)

    # Load data
    print("\nLoading data...")
    df = load_data(base_path)

    # Average by driver
    print("\nAveraging by driver...")
    driver_avg = average_by_driver(df)
    print(f"Driver-level dataset: {len(driver_avg)} drivers")

    # Run comparison
    results = lodo_cv_comparison(driver_avg)

    # Print results
    print_results(results)

    # Save detailed comparison
    output_path = base_path / "data" / "analysis_outputs"
    save_comparison_report(results, output_path)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
