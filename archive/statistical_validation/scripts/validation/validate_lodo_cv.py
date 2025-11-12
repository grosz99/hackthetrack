"""
Leave-One-Driver-Out Cross-Validation (LODO-CV)

Statistical validation of the factor-based finish position prediction model.
Tests whether factors generalize to unseen drivers or if the model is overfitting.

Methodology:
- For each driver, train model on remaining 37 drivers
- Predict finish position for held-out driver using their factor scores
- Calculate out-of-sample R², MAE, and compare to in-sample performance
- Provides rigorous assessment of model generalizability

Statistical Interpretation:
- High in-sample R², low out-of-sample R² = overfitting
- Similar in-sample and out-of-sample R² = good generalization
- LODO-CV is conservative: estimates performance on completely new drivers
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict


def load_data(data_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load factor scores and features."""
    factor_scores = pd.read_csv(data_path / "analysis_outputs" / "tier1_factor_scores.csv")
    features = pd.read_csv(data_path / "analysis_outputs" / "all_races_tier1_features.csv")
    return factor_scores, features


def reflect_factors(factor_scores: pd.DataFrame) -> pd.DataFrame:
    """
    Apply factor reflection to match corrected factor_analyzer.py.

    Factors 1, 2, 3 have negative loadings and must be reflected.
    Factor 4 has positive loadings and is correct as-is.
    """
    df = factor_scores.copy()

    # Reflect factors with negative dominant loadings
    df['factor_1_score'] = -1 * df['factor_1_score']  # Consistency
    df['factor_2_score'] = -1 * df['factor_2_score']  # Racecraft
    df['factor_3_score'] = -1 * df['factor_3_score']  # Speed
    # factor_4_score stays as-is (tire management has positive loadings)

    return df


def calculate_in_sample_performance(
    X: np.ndarray,
    y: np.ndarray
) -> Tuple[float, float]:
    """
    Calculate in-sample performance (training on all data).

    This is what was previously reported - model trained and tested on same data.
    """
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)

    return r2, mae


def leave_one_driver_out_cv(
    factor_scores: pd.DataFrame,
    features: pd.DataFrame
) -> Dict:
    """
    Perform Leave-One-Driver-Out Cross-Validation.

    For each driver:
    1. Remove all races for that driver from training set
    2. Train model on remaining drivers
    3. Predict finish positions for held-out driver
    4. Calculate prediction error

    Returns:
        Dictionary with results including:
        - out_of_sample_r2: R² on held-out predictions
        - out_of_sample_mae: Mean absolute error on held-out predictions
        - driver_predictions: DataFrame with per-driver results
    """
    # Aggregate factor scores by driver (average across races)
    driver_factors = factor_scores.groupby('driver_number')[
        ['factor_1_score', 'factor_2_score', 'factor_3_score', 'factor_4_score']
    ].mean().reset_index()

    # Get average finishing position per driver
    driver_finish = features.groupby('driver_number')['finishing_position'].mean().reset_index()

    # Merge
    data = driver_factors.merge(driver_finish, on='driver_number')

    # Prepare data
    X = data[['factor_1_score', 'factor_2_score', 'factor_3_score', 'factor_4_score']].values
    y = data['finishing_position'].values
    driver_numbers = data['driver_number'].values

    # Calculate in-sample performance (train on all, test on all)
    in_sample_r2, in_sample_mae = calculate_in_sample_performance(X, y)

    # LODO-CV: Leave one driver out
    predictions = []
    actuals = []
    drivers_out = []

    for i, held_out_driver in enumerate(driver_numbers):
        # Training set: all drivers except current one
        train_mask = np.arange(len(X)) != i
        X_train = X[train_mask]
        y_train = y[train_mask]

        # Test set: just the held-out driver
        X_test = X[i:i+1]
        y_test = y[i]

        # Train model on remaining drivers
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predict for held-out driver
        y_pred = model.predict(X_test)[0]

        predictions.append(y_pred)
        actuals.append(y_test)
        drivers_out.append(held_out_driver)

    # Calculate out-of-sample metrics
    predictions = np.array(predictions)
    actuals = np.array(actuals)

    out_of_sample_r2 = r2_score(actuals, predictions)
    out_of_sample_mae = mean_absolute_error(actuals, predictions)

    # Create detailed results DataFrame
    results_df = pd.DataFrame({
        'driver_number': drivers_out,
        'actual_position': actuals,
        'predicted_position': predictions,
        'error': predictions - actuals,
        'abs_error': np.abs(predictions - actuals)
    })
    results_df = results_df.sort_values('abs_error', ascending=False)

    return {
        'in_sample_r2': in_sample_r2,
        'in_sample_mae': in_sample_mae,
        'out_of_sample_r2': out_of_sample_r2,
        'out_of_sample_mae': out_of_sample_mae,
        'driver_predictions': results_df,
        'n_drivers': len(driver_numbers)
    }


def plot_lodo_results(results: Dict, output_path: Path):
    """Create visualization of LODO-CV results."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    df = results['driver_predictions']

    # 1. Predicted vs Actual
    ax = axes[0, 0]
    ax.scatter(df['actual_position'], df['predicted_position'], alpha=0.6, s=100)

    # Perfect prediction line
    min_pos = min(df['actual_position'].min(), df['predicted_position'].min())
    max_pos = max(df['actual_position'].max(), df['predicted_position'].max())
    ax.plot([min_pos, max_pos], [min_pos, max_pos], 'r--', alpha=0.5, label='Perfect Prediction')

    ax.set_xlabel('Actual Average Finish Position', fontsize=12)
    ax.set_ylabel('Predicted Average Finish Position', fontsize=12)
    ax.set_title(f'LODO-CV: Predicted vs Actual\nOut-of-Sample R² = {results["out_of_sample_r2"]:.3f}',
                 fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. Error distribution
    ax = axes[0, 1]
    ax.hist(df['error'], bins=15, edgecolor='black', alpha=0.7)
    ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero Error')
    ax.set_xlabel('Prediction Error (Predicted - Actual)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f'Error Distribution\nMAE = {results["out_of_sample_mae"]:.2f} positions',
                 fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # 3. In-sample vs Out-of-sample comparison
    ax = axes[1, 0]
    metrics = ['R²', 'MAE']
    in_sample_vals = [results['in_sample_r2'], results['in_sample_mae']]
    out_sample_vals = [results['out_of_sample_r2'], results['out_of_sample_mae']]

    x = np.arange(len(metrics))
    width = 0.35

    # Normalize MAE to same scale as R² for visualization
    in_sample_display = [in_sample_vals[0], in_sample_vals[1] / 20]  # Scale MAE to 0-1
    out_sample_display = [out_sample_vals[0], out_sample_vals[1] / 20]

    ax.bar(x - width/2, in_sample_display, width, label='In-Sample', alpha=0.8)
    ax.bar(x + width/2, out_sample_display, width, label='Out-of-Sample', alpha=0.8)

    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('In-Sample vs Out-of-Sample Performance', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Add actual values as text
    for i, (in_val, out_val) in enumerate(zip([in_sample_vals[0], in_sample_vals[1]],
                                               [out_sample_vals[0], out_sample_vals[1]])):
        ax.text(i - width/2, in_sample_display[i] + 0.02, f'{in_val:.3f}',
                ha='center', va='bottom', fontsize=9)
        ax.text(i + width/2, out_sample_display[i] + 0.02, f'{out_val:.3f}',
                ha='center', va='bottom', fontsize=9)

    # 4. Worst predictions
    ax = axes[1, 1]
    worst_10 = df.nlargest(10, 'abs_error')
    ax.barh(range(len(worst_10)), worst_10['abs_error'], alpha=0.7)
    ax.set_yticks(range(len(worst_10)))
    ax.set_yticklabels([f"Driver #{int(d)}" for d in worst_10['driver_number']])
    ax.set_xlabel('Absolute Error (positions)', fontsize=12)
    ax.set_title('10 Worst Predictions', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(output_path / 'lodo_cv_validation.png', dpi=300, bbox_inches='tight')
    print(f"Saved visualization to {output_path / 'lodo_cv_validation.png'}")
    plt.close()


def generate_statistical_report(results: Dict) -> str:
    """Generate detailed statistical interpretation report."""

    in_r2 = results['in_sample_r2']
    out_r2 = results['out_of_sample_r2']
    shrinkage = in_r2 - out_r2

    # Statistical interpretation
    if shrinkage < 0.05:
        generalization = "excellent"
        interpretation = "The model generalizes well to unseen drivers."
    elif shrinkage < 0.15:
        generalization = "good"
        interpretation = "The model shows acceptable generalization with minor overfitting."
    elif shrinkage < 0.30:
        generalization = "moderate"
        interpretation = "The model shows moderate overfitting. Predictions for new drivers should be interpreted cautiously."
    else:
        generalization = "poor"
        interpretation = "The model shows substantial overfitting. Predictions for new drivers are unreliable."

    report = f"""
================================================================================
        LEAVE-ONE-DRIVER-OUT CROSS-VALIDATION REPORT
================================================================================

SAMPLE CHARACTERISTICS:
-----------------------
Number of drivers: {results['n_drivers']}
Validation strategy: Leave-One-Driver-Out (LODO-CV)
Model type: Linear Regression on 4 reflected factor scores

PERFORMANCE METRICS:
--------------------
In-Sample Performance (train = test):
  - R² = {in_r2:.4f}
  - MAE = {results['in_sample_mae']:.3f} positions

Out-of-Sample Performance (LODO-CV):
  - R² = {out_r2:.4f}
  - MAE = {results['out_of_sample_mae']:.3f} positions

Model Shrinkage:
  - R² shrinkage = {shrinkage:.4f} ({shrinkage/in_r2*100:.1f}% reduction)
  - Generalization: {generalization.upper()}

STATISTICAL INTERPRETATION:
---------------------------
{interpretation}

R² shrinkage of {shrinkage:.3f} indicates that the model explains
{shrinkage*100:.1f}% less variance when predicting unseen drivers compared
to drivers in the training set.

The out-of-sample R² of {out_r2:.3f} means the model explains
{out_r2*100:.1f}% of variance in finish position for completely new drivers.

PREDICTION ACCURACY:
--------------------
- Mean absolute error: {results['out_of_sample_mae']:.2f} positions
- This means predictions are typically off by ±{results['out_of_sample_mae']:.1f} positions
- With {results['n_drivers']} drivers, this represents ±{results['out_of_sample_mae']/results['n_drivers']*100:.1f}% of the field

WORST PREDICTIONS (Top 5):
---------------------------
"""

    worst_5 = results['driver_predictions'].nlargest(5, 'abs_error')
    for idx, row in worst_5.iterrows():
        report += f"  Driver #{int(row['driver_number'])}: "
        report += f"Predicted {row['predicted_position']:.1f}, "
        report += f"Actual {row['actual_position']:.1f}, "
        report += f"Error = {row['error']:+.1f} positions\n"

    report += f"""
RECOMMENDATIONS:
----------------
1. Use out-of-sample R² ({out_r2:.3f}) when reporting model performance
2. Report prediction uncertainty: ±{results['out_of_sample_mae']:.1f} positions (68% CI)
3. For new drivers, expect predictions within ±{results['out_of_sample_mae']*2:.1f} positions (95% CI)
4. Consider factors as descriptive summaries rather than strict predictive models

STATISTICAL NOTES:
------------------
- LODO-CV provides conservative estimate of generalization
- Small sample size (n={results['n_drivers']}) increases uncertainty
- Model is most reliable for drivers similar to training set
- Extrapolation beyond observed range is not recommended

================================================================================
"""

    return report


def main():
    """Run LODO-CV validation and generate report."""
    # Setup paths
    base_path = Path(__file__).parent.parent
    data_path = base_path / "data"
    output_path = base_path / "data" / "analysis_outputs"

    print("Loading data...")
    factor_scores, features = load_data(data_path)

    print("Applying factor reflection...")
    factor_scores = reflect_factors(factor_scores)

    print("Running Leave-One-Driver-Out Cross-Validation...")
    results = leave_one_driver_out_cv(factor_scores, features)

    print("\nGenerating visualization...")
    plot_lodo_results(results, output_path)

    print("\nGenerating statistical report...")
    report = generate_statistical_report(results)

    # Save report
    report_path = output_path / "lodo_cv_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)

    print(report)
    print(f"\nReport saved to {report_path}")

    # Save detailed results
    results_csv_path = output_path / "lodo_cv_predictions.csv"
    results['driver_predictions'].to_csv(results_csv_path, index=False)
    print(f"Detailed predictions saved to {results_csv_path}")

    print("\n" + "="*80)
    print("LODO-CV VALIDATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
