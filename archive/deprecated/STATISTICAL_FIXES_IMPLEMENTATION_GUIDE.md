# Statistical Fixes: Implementation Guide

**Priority**: HIGH - Implement before MVP launch
**Estimated Effort**: 4-6 hours
**Impact**: Ensures statistical validity and proper validation

---

## Overview of Required Changes

Based on the statistical validation report, three critical fixes are needed:

1. **Replace RepTrak calculation with reflected factor scores** (while keeping percentile display)
2. **Implement Leave-One-Driver-Out cross-validation** (proper generalization test)
3. **Add confidence intervals to factor scores** (uncertainty quantification)

---

## Fix 1: Reflected Factor Scores (CRITICAL)

### Current Problem

Your `factor_analyzer.py` recalculates scores from scratch using weighted percentiles, ignoring the actual factor scores from the factor analysis. This breaks the statistical properties of factor analysis.

### Solution: Use Reflected Factor Scores

**File**: `/backend/app/services/factor_analyzer.py`

Replace the `_calculate_factor_breakdown()` method with this approach:

```python
def _calculate_factor_breakdown(self, driver_number: int, factor_name: str) -> FactorBreakdown:
    """Calculate detailed breakdown using REFLECTED factor scores."""
    factor_config = FACTOR_VARIABLES[factor_name]
    factor_column = factor_config["factor_column"]  # e.g., "factor_3_score"

    # Get driver's actual factor z-score (averaged across races)
    driver_factor_scores = self.factor_scores_df[
        self.factor_scores_df['driver_number'] == driver_number
    ]

    # Get the z-score from factor analysis
    factor_zscore = driver_factor_scores[factor_column].mean()

    # REFLECT factors with negative loadings to flip interpretation
    # Factor 1 (consistency): REFLECT (negative loadings)
    # Factor 2 (racecraft): REFLECT (negative loadings)
    # Factor 3 (speed): REFLECT (negative loadings)
    # Factor 4 (tire mgmt): KEEP (positive loadings)
    if factor_name in ["consistency", "racecraft", "speed"]:
        factor_zscore_reflected = -factor_zscore
    else:
        factor_zscore_reflected = factor_zscore

    # Convert reflected z-score to percentile FOR DISPLAY ONLY
    all_factor_scores = self.factor_scores_df.groupby('driver_number')[factor_column].mean()

    if factor_name in ["consistency", "racecraft", "speed"]:
        all_factor_scores_reflected = -all_factor_scores
    else:
        all_factor_scores_reflected = all_factor_scores

    percentile = (all_factor_scores_reflected < factor_zscore_reflected).sum() / len(all_factor_scores_reflected) * 100

    # Now calculate variable breakdowns for explanation
    driver_features = self.features_df[
        self.features_df['driver_number'] == driver_number
    ].drop(columns=['race', 'driver_number']).mean()

    variables = []
    for var_name, display_name, weight in factor_config["variables"]:
        raw_value = driver_features.get(var_name, 0)

        # Calculate percentile for this variable
        all_values = self.features_df.groupby('driver_number')[var_name].mean()
        var_percentile = (all_values < raw_value).sum() / len(all_values) * 100

        # Contribution is now based on factor loading, not arbitrary weight
        # Get the actual loading from the factor analysis
        loading = self._get_factor_loading(var_name, factor_column)
        contribution = abs(loading) * var_percentile  # Use magnitude of loading

        variables.append(VariableBreakdown(
            name=var_name,
            display_name=display_name,
            raw_value=raw_value,
            normalized_value=var_percentile,
            weight=abs(loading),  # Use actual loading magnitude
            contribution=contribution,
            percentile=var_percentile
        ))

    # Sort by contribution
    variables.sort(key=lambda x: x.contribution, reverse=True)

    # Overall score for display is the factor percentile
    overall_score = percentile
    overall_percentile = percentile

    # Find strongest and weakest
    strongest = max(variables, key=lambda x: x.percentile)
    weakest = min(variables, key=lambda x: x.percentile)

    explanation = self._generate_racing_explanation(
        factor_name, strongest, weakest, overall_percentile
    )

    return FactorBreakdown(
        factor_name=factor_name,
        overall_score=overall_score,
        percentile=overall_percentile,
        variables=variables,
        explanation=explanation,
        strongest_area=strongest.display_name,
        weakest_area=weakest.display_name
    )

def _get_factor_loading(self, variable_name: str, factor_column: str) -> float:
    """Get the actual factor loading for a variable from the loadings matrix."""
    # Load the factor loadings CSV
    loadings_path = self.data_path / "analysis_outputs" / "tier1_factor_loadings.csv"
    loadings_df = pd.read_csv(loadings_path, index_col=0)

    # Map factor_column to loading column name
    # factor_1_score -> Factor_1, etc.
    loading_col = factor_column.replace("_score", "").replace("factor_", "Factor_")

    if variable_name in loadings_df.index and loading_col in loadings_df.columns:
        return loadings_df.loc[variable_name, loading_col]
    else:
        # Fallback to equal weighting if not found
        return 1.0 / len(self.features_df.columns)
```

**Key Changes**:
1. Use actual factor z-scores from factor analysis (not recalculated)
2. Reflect negative factors to flip interpretation
3. Use factor loadings as weights (not arbitrary assignments)
4. Convert to percentiles only for display, not for calculations

---

## Fix 2: Leave-One-Driver-Out Cross-Validation (CRITICAL)

### Current Problem

Your reported R² = 0.895 is in-sample performance. You report LORO-CV (Leave-One-Race-Out) but this doesn't test generalization to new drivers.

### Solution: Implement LODO-CV

**Create new file**: `/scripts/validate_lodo_cv.py`

```python
"""
Leave-One-Driver-Out Cross-Validation
Tests if factor model generalizes to unseen drivers.
"""

import pandas as pd
import numpy as np
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns

print("\n" + "="*80)
print("LEAVE-ONE-DRIVER-OUT CROSS-VALIDATION")
print("="*80)

# Load data
df = pd.read_csv('data/analysis_outputs/all_races_tier1_features.csv')

feature_cols = [
    'qualifying_pace', 'best_race_lap', 'avg_top10_pace',
    'stint_consistency', 'sector_consistency', 'braking_consistency',
    'pace_degradation', 'late_stint_perf', 'early_vs_late_pace',
    'position_changes', 'positions_gained', 'performance_normalized'
]

df_clean = df[feature_cols + ['finishing_position', 'driver_number']].dropna()
unique_drivers = df_clean['driver_number'].unique()

print(f"\nTotal drivers: {len(unique_drivers)}")
print(f"Total observations: {len(df_clean)}")

# LODO-CV
predicted_finishes = []
actual_finishes = []
driver_errors = []

for i, test_driver in enumerate(unique_drivers):
    print(f"\nFold {i+1}/{len(unique_drivers)}: Holding out Driver #{test_driver}")

    # Split data
    train_data = df_clean[df_clean['driver_number'] != test_driver]
    test_data = df_clean[df_clean['driver_number'] == test_driver]

    print(f"  Train: {len(train_data)} obs, {train_data['driver_number'].nunique()} drivers")
    print(f"  Test:  {len(test_data)} obs")

    # Standardize training data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(train_data[feature_cols])
    X_test = scaler.transform(test_data[feature_cols])

    # Factor analysis on training data
    fa = FactorAnalysis(n_components=4, random_state=42, max_iter=1000)
    train_factor_scores = fa.fit_transform(X_train)
    test_factor_scores = fa.transform(X_test)

    # Reflect factors (negative loadings)
    train_factor_scores[:, 0] *= -1  # Factor 1 (Consistency)
    train_factor_scores[:, 1] *= -1  # Factor 2 (Racecraft)
    train_factor_scores[:, 2] *= -1  # Factor 3 (Speed)

    test_factor_scores[:, 0] *= -1
    test_factor_scores[:, 1] *= -1
    test_factor_scores[:, 2] *= -1

    # Fit regression on training data
    reg = LinearRegression()
    reg.fit(train_factor_scores, train_data['finishing_position'])

    # Predict test driver
    test_preds = reg.predict(test_factor_scores)
    test_actual = test_data['finishing_position'].values

    # Store results
    predicted_finishes.extend(test_preds)
    actual_finishes.extend(test_actual)

    # Calculate error for this driver
    mae_driver = mean_absolute_error(test_actual, test_preds)
    driver_errors.append({
        'driver': test_driver,
        'mae': mae_driver,
        'n_races': len(test_data)
    })
    print(f"  MAE: {mae_driver:.2f} positions")

# Overall LODO-CV performance
lodo_r2 = r2_score(actual_finishes, predicted_finishes)
lodo_mae = mean_absolute_error(actual_finishes, predicted_finishes)

print("\n" + "="*80)
print("LODO-CV RESULTS")
print("="*80)
print(f"\nR² (LODO-CV): {lodo_r2:.3f}")
print(f"MAE (LODO-CV): {lodo_mae:.2f} positions")
print(f"\nCompare to in-sample R²: 0.895")
print(f"Generalization gap: {0.895 - lodo_r2:.3f}")

if lodo_r2 > 0.60:
    print("\n[PASS] Good generalization to new drivers")
elif lodo_r2 > 0.40:
    print("\n[WARN] Moderate generalization - model may be overfitting")
else:
    print("\n[FAIL] Poor generalization - significant overfitting detected")

# Driver-level error analysis
errors_df = pd.DataFrame(driver_errors)
print(f"\nWorst predicted drivers (highest MAE):")
print(errors_df.nlargest(5, 'mae')[['driver', 'mae', 'n_races']])

# Visualization
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Actual vs Predicted
axes[0].scatter(actual_finishes, predicted_finishes, alpha=0.6)
axes[0].plot([0, 30], [0, 30], 'r--', label='Perfect prediction')
axes[0].set_xlabel('Actual Finishing Position')
axes[0].set_ylabel('Predicted Finishing Position')
axes[0].set_title(f'LODO-CV: R² = {lodo_r2:.3f}, MAE = {lodo_mae:.2f}')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Plot 2: Residuals
residuals = np.array(actual_finishes) - np.array(predicted_finishes)
axes[1].scatter(predicted_finishes, residuals, alpha=0.6)
axes[1].axhline(y=0, color='r', linestyle='--')
axes[1].set_xlabel('Predicted Finishing Position')
axes[1].set_ylabel('Residual (Actual - Predicted)')
axes[1].set_title('Residual Plot')
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('data/analysis_outputs/lodo_cv_diagnostics.png', dpi=150)
print(f"\n[SAVED] LODO-CV diagnostics: data/analysis_outputs/lodo_cv_diagnostics.png")

# Save results
results_df = pd.DataFrame({
    'actual': actual_finishes,
    'predicted': predicted_finishes,
    'residual': residuals
})
results_df.to_csv('data/analysis_outputs/lodo_cv_predictions.csv', index=False)
print(f"[SAVED] Predictions: data/analysis_outputs/lodo_cv_predictions.csv")

print("\n" + "="*80)
print("VALIDATION COMPLETE")
print("="*80)
```

**Run this script**:
```bash
python scripts/validate_lodo_cv.py
```

**Expected outcome**:
- LODO-CV R² will be lower than 0.895 (probably 0.50-0.70)
- This is your TRUE generalization performance
- Report this in your product documentation

---

## Fix 3: Bootstrap Confidence Intervals (MEDIUM PRIORITY)

### Purpose

Show scouts the uncertainty in factor scores: "Is Driver #13 truly elite, or just lucky in these races?"

**Create new file**: `/scripts/bootstrap_confidence_intervals.py`

```python
"""
Bootstrap Confidence Intervals for Factor Scores
Quantifies uncertainty in driver skill estimates.
"""

import pandas as pd
import numpy as np
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample

print("\n" + "="*80)
print("BOOTSTRAP CONFIDENCE INTERVALS FOR FACTOR SCORES")
print("="*80)

# Load data
df = pd.read_csv('data/analysis_outputs/all_races_tier1_features.csv')

feature_cols = [
    'qualifying_pace', 'best_race_lap', 'avg_top10_pace',
    'stint_consistency', 'sector_consistency', 'braking_consistency',
    'pace_degradation', 'late_stint_perf', 'early_vs_late_pace',
    'position_changes', 'positions_gained', 'performance_normalized'
]

df_clean = df[feature_cols + ['driver_number']].dropna()
unique_drivers = df_clean['driver_number'].unique()

# Number of bootstrap iterations
n_bootstrap = 1000
print(f"\nRunning {n_bootstrap} bootstrap iterations...")

# Store bootstrap samples
bootstrap_scores = {driver: {f'factor_{i}': [] for i in range(1, 5)} for driver in unique_drivers}

for b in range(n_bootstrap):
    if b % 100 == 0:
        print(f"  Iteration {b}/{n_bootstrap}")

    # Resample drivers WITH REPLACEMENT
    boot_drivers = resample(unique_drivers, n_samples=len(unique_drivers), random_state=b)
    boot_data = df_clean[df_clean['driver_number'].isin(boot_drivers)]

    # Standardize
    scaler = StandardScaler()
    X_boot = scaler.fit_transform(boot_data[feature_cols])

    # Factor analysis
    fa = FactorAnalysis(n_components=4, random_state=42, max_iter=1000)
    factor_scores = fa.fit_transform(X_boot)

    # Reflect factors
    factor_scores[:, 0] *= -1  # Consistency
    factor_scores[:, 1] *= -1  # Racecraft
    factor_scores[:, 2] *= -1  # Speed

    # Average by driver
    boot_data_copy = boot_data.copy()
    for i in range(4):
        boot_data_copy[f'factor_{i+1}'] = factor_scores[:, i]

    driver_avg = boot_data_copy.groupby('driver_number')[[f'factor_{i}' for i in range(1, 5)]].mean()

    # Store scores for each driver in original sample
    for driver in unique_drivers:
        if driver in driver_avg.index:
            for i in range(1, 5):
                bootstrap_scores[driver][f'factor_{i}'].append(driver_avg.loc[driver, f'factor_{i}'])

print("\nBootstrap sampling complete. Calculating confidence intervals...")

# Calculate confidence intervals
ci_results = []
for driver in unique_drivers:
    for i in range(1, 5):
        scores = bootstrap_scores[driver][f'factor_{i}']
        if len(scores) > 0:
            mean_score = np.mean(scores)
            ci_lower = np.percentile(scores, 2.5)
            ci_upper = np.percentile(scores, 97.5)
            ci_width = ci_upper - ci_lower

            ci_results.append({
                'driver_number': driver,
                'factor': i,
                'mean_zscore': mean_score,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'ci_width': ci_width
            })

ci_df = pd.DataFrame(ci_results)
ci_df.to_csv('data/analysis_outputs/factor_score_confidence_intervals.csv', index=False)
print(f"[SAVED] Confidence intervals: data/analysis_outputs/factor_score_confidence_intervals.csv")

# Find drivers with widest CIs (most uncertain)
print("\nDrivers with WIDEST confidence intervals (most uncertain):")
wide_ci = ci_df.nlargest(10, 'ci_width')[['driver_number', 'factor', 'ci_width']]
print(wide_ci)

# Find drivers with narrowest CIs (most certain)
print("\nDrivers with NARROWEST confidence intervals (most certain):")
narrow_ci = ci_df.nsmallest(10, 'ci_width')[['driver_number', 'factor', 'ci_width']]
print(narrow_ci)

print("\n" + "="*80)
print("BOOTSTRAP ANALYSIS COMPLETE")
print("="*80)
```

**Run this script**:
```bash
python scripts/bootstrap_confidence_intervals.py
```

---

## Fix 4: Update Database Schema (MINOR)

Add a column to store reflected z-scores alongside percentiles.

**File**: `backend/database/schema.sql` (or migration script)

```sql
ALTER TABLE factor_breakdowns
ADD COLUMN zscore_reflected REAL;

-- Update calculation to store both
-- Percentile: for display
-- Z-score: for predictions and analysis
```

Update `factor_analyzer.py` to store both values:

```python
cursor.execute("""
    INSERT OR REPLACE INTO factor_breakdowns
    (driver_number, factor_name, variable_name, variable_display_name,
     raw_value, normalized_value, zscore_reflected, weight, contribution, percentile)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    int(driver_number), factor_name, var.name, var.display_name,
    float(var.raw_value), float(var.normalized_value),
    float(factor_zscore_reflected),  # NEW: store z-score
    float(var.weight), float(var.contribution), float(var.percentile)
))
```

---

## Implementation Checklist

**Before MVP Launch**:
- [ ] Implement reflected factor scores in `factor_analyzer.py` (2 hours)
- [ ] Run LODO-CV validation script (30 min)
- [ ] Document actual generalization R² in product docs (30 min)
- [ ] Update prediction model to use reflected z-scores (1 hour)
- [ ] Add limitations section to UI/documentation (30 min)

**Post-Launch (v1.1)**:
- [ ] Run bootstrap confidence intervals (30 min)
- [ ] Add confidence intervals to driver profiles in UI (2 hours)
- [ ] Update database schema to store z-scores (1 hour)

**Future (v2.0)**:
- [ ] Implement hierarchical/multilevel factor analysis (2-3 days)
- [ ] Collect more data (target n≥100 drivers) (ongoing)
- [ ] Add Bayesian uncertainty quantification (3-5 days)

---

## Testing Your Implementation

After implementing fixes, verify correctness:

**Test 1: Factor Score Reflection**
```python
# Load original factor scores
original = pd.read_csv('data/analysis_outputs/tier1_factor_scores.csv')

# Check that reflection flips sign correctly
driver_13_speed_original = original[original.driver_number == 13]['factor_3_score'].mean()
# Should be negative (e.g., -1.17)

driver_13_speed_reflected = -driver_13_speed_original
# Should be positive (e.g., +1.17)

# Higher reflected score should correlate with BETTER finish
assert driver_13_speed_reflected > 0  # Driver 13 is fast
```

**Test 2: LODO-CV**
```python
# LODO-CV R² should be lower than in-sample R²
assert lodo_r2 < 0.895
assert lodo_r2 > 0.40  # Still reasonable performance
```

**Test 3: Percentile Conversion**
```python
# Percentile should be monotonic with z-score
from scipy.stats import spearmanr
corr, _ = spearmanr(z_scores, percentiles)
assert corr > 0.99  # Should be nearly perfect rank correlation
```

---

## Expected Outcomes

After implementing these fixes:

1. **Factor scores will be statistically valid**
   - Use actual factor analysis output
   - Proper use of factor loadings as weights
   - Maintain factor analysis properties

2. **Realistic performance expectations**
   - LODO-CV R² likely 0.50-0.70 (vs inflated 0.895)
   - Clear understanding of generalization ability
   - Better trust from technical stakeholders

3. **Uncertainty quantification**
   - Bootstrap CIs show which drivers are "truly elite" vs "lucky"
   - Helps scouts understand reliability of ratings
   - Builds confidence in product

---

## Questions or Issues?

If you encounter problems during implementation:

1. **Factor loadings don't match variable mapping**:
   - Check that factor column names match between factor analysis output and your mapping
   - Verify Factor_1 in loadings CSV corresponds to factor_1_score in scores CSV

2. **LODO-CV R² is very low (< 0.30)**:
   - This indicates severe overfitting
   - May need to simplify model or collect more data
   - Consider regularization (Ridge/Lasso regression)

3. **Bootstrap takes too long**:
   - Reduce n_bootstrap from 1000 to 500
   - Use parallel processing: `joblib.Parallel(n_jobs=-1)`

4. **Percentiles look wrong after reflection**:
   - Ensure you reflect BEFORE calculating percentiles
   - Check that reflected z-scores are monotonic with performance

---

**END OF IMPLEMENTATION GUIDE**

Estimated total time: **4-6 hours** for critical MVP fixes, **4-6 additional hours** for post-launch improvements.
