"""
DEMONSTRATE FACTOR PREDICTION MODEL
====================================

Show exactly how factors predict finishing position.
Address overfitting concerns with cross-validation.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import KFold, LeaveOneGroupOut
import matplotlib.pyplot as plt

print("\n" + "="*80)
print("FACTOR PREDICTION MODEL - DETAILED DEMONSTRATION")
print("="*80)

# Load data
factor_scores = pd.read_csv('data/analysis_outputs/tier1_factor_scores.csv')
print(f"\nData: {len(factor_scores)} observations from {factor_scores['race'].nunique()} races")

# ============================================================================
# PART 1: THE BASIC REGRESSION MODEL
# ============================================================================
print("\n" + "="*80)
print("PART 1: THE REGRESSION EQUATION")
print("="*80)

X = factor_scores[['factor_1_score', 'factor_2_score', 'factor_3_score',
                    'factor_4_score', 'factor_5_score']].values
y = factor_scores['finishing_position'].values

reg = LinearRegression()
reg.fit(X, y)
y_pred = reg.predict(X)
r2 = r2_score(y, y_pred)
mae = mean_absolute_error(y, y_pred)

print("\nThe Regression Equation:")
print("="*80)
print("Predicted Finish = Intercept + (beta1 * Factor1) + (beta2 * Factor2) + ... + (beta5 * Factor5)")
print()
print(f"Predicted Finish = {reg.intercept_:.3f}")
print(f"                 + ({reg.coef_[0]:6.3f} * CONSISTENCY)")
print(f"                 + ({reg.coef_[1]:6.3f} * RACECRAFT)")
print(f"                 + ({reg.coef_[2]:6.3f} * RAW_SPEED)")
print(f"                 + ({reg.coef_[3]:6.3f} * TIRE_MGMT)")
print(f"                 + ({reg.coef_[4]:6.3f} * RESIDUAL)")

print(f"\nModel Performance:")
print(f"  R² = {r2:.4f} (explains {r2*100:.1f}% of variance)")
print(f"  MAE = {mae:.2f} positions (average error)")

# ============================================================================
# PART 2: EXAMPLE PREDICTIONS FOR ACTUAL DRIVERS
# ============================================================================
print("\n" + "="*80)
print("PART 2: EXAMPLE PREDICTIONS FOR REAL DRIVERS")
print("="*80)

# Show 10 examples (5 from top, 5 from bottom)
examples = pd.concat([
    factor_scores.nsmallest(5, 'finishing_position'),
    factor_scores.nlargest(5, 'finishing_position')
])

print("\nTop 5 Finishers:")
print("="*80)
print(f"{'Race':<15} {'Driver':<8} {'F1':<7} {'F2':<7} {'F3':<7} {'F4':<7} {'F5':<7} | {'Actual':<7} {'Pred':<7} {'Error':<7}")
print("-"*100)

for idx, row in examples.nsmallest(5, 'finishing_position').iterrows():
    prediction = (reg.intercept_ +
                  reg.coef_[0] * row['factor_1_score'] +
                  reg.coef_[1] * row['factor_2_score'] +
                  reg.coef_[2] * row['factor_3_score'] +
                  reg.coef_[3] * row['factor_4_score'] +
                  reg.coef_[4] * row['factor_5_score'])

    error = prediction - row['finishing_position']

    print(f"{row['race']:<15} #{row['driver_number']:<7} "
          f"{row['factor_1_score']:6.2f} {row['factor_2_score']:6.2f} "
          f"{row['factor_3_score']:6.2f} {row['factor_4_score']:6.2f} "
          f"{row['factor_5_score']:6.2f} | "
          f"{row['finishing_position']:6.0f} {prediction:6.1f} {error:+6.2f}")

print("\nBottom 5 Finishers:")
print("="*80)
print(f"{'Race':<15} {'Driver':<8} {'F1':<7} {'F2':<7} {'F3':<7} {'F4':<7} {'F5':<7} | {'Actual':<7} {'Pred':<7} {'Error':<7}")
print("-"*100)

for idx, row in examples.nlargest(5, 'finishing_position').iterrows():
    prediction = (reg.intercept_ +
                  reg.coef_[0] * row['factor_1_score'] +
                  reg.coef_[1] * row['factor_2_score'] +
                  reg.coef_[2] * row['factor_3_score'] +
                  reg.coef_[3] * row['factor_4_score'] +
                  reg.coef_[4] * row['factor_5_score'])

    error = prediction - row['finishing_position']

    print(f"{row['race']:<15} #{row['driver_number']:<7} "
          f"{row['factor_1_score']:6.2f} {row['factor_2_score']:6.2f} "
          f"{row['factor_3_score']:6.2f} {row['factor_4_score']:6.2f} "
          f"{row['factor_5_score']:6.2f} | "
          f"{row['finishing_position']:6.0f} {prediction:6.1f} {error:+6.2f}")

# ============================================================================
# PART 3: STEP-BY-STEP CALCULATION FOR ONE DRIVER
# ============================================================================
print("\n" + "="*80)
print("PART 3: DETAILED CALCULATION FOR ONE DRIVER")
print("="*80)

# Pick Driver #13 from barber_r1 (winner)
example = factor_scores[(factor_scores['driver_number'] == 13) &
                        (factor_scores['race'] == 'barber_r1')].iloc[0]

print(f"\nDriver #{example['driver_number']} at {example['race']}")
print(f"Actual Finish: {example['finishing_position']}")
print("\nStep-by-step prediction:")
print(f"  1. Start with intercept:        {reg.intercept_:8.3f}")
print(f"  2. Add CONSISTENCY contribution: ({reg.coef_[0]:6.3f} * {example['factor_1_score']:6.3f}) = {reg.coef_[0] * example['factor_1_score']:8.3f}")
print(f"  3. Add RACECRAFT contribution:   ({reg.coef_[1]:6.3f} * {example['factor_2_score']:6.3f}) = {reg.coef_[1] * example['factor_2_score']:8.3f}")
print(f"  4. Add RAW_SPEED contribution:   ({reg.coef_[2]:6.3f} * {example['factor_3_score']:6.3f}) = {reg.coef_[2] * example['factor_3_score']:8.3f}")
print(f"  5. Add TIRE_MGMT contribution:   ({reg.coef_[3]:6.3f} * {example['factor_4_score']:6.3f}) = {reg.coef_[3] * example['factor_4_score']:8.3f}")
print(f"  6. Add RESIDUAL contribution:    ({reg.coef_[4]:6.3f} * {example['factor_5_score']:6.3f}) = {reg.coef_[4] * example['factor_5_score']:8.3f}")

prediction = (reg.intercept_ +
              reg.coef_[0] * example['factor_1_score'] +
              reg.coef_[1] * example['factor_2_score'] +
              reg.coef_[2] * example['factor_3_score'] +
              reg.coef_[3] * example['factor_4_score'] +
              reg.coef_[4] * example['factor_5_score'])

print(f"\n  PREDICTED FINISH: {prediction:.2f}")
print(f"  ACTUAL FINISH:    {example['finishing_position']:.0f}")
print(f"  ERROR:            {prediction - example['finishing_position']:+.2f} positions")

# ============================================================================
# PART 4: OVERFITTING CHECKS
# ============================================================================
print("\n" + "="*80)
print("PART 4: OVERFITTING ANALYSIS")
print("="*80)

print("\nOVERFITTING CONCERN: Model trained and tested on same data!")
print("Solution: Cross-validation to estimate out-of-sample performance")

# Check 1: K-Fold Cross-Validation (general)
print("\n" + "="*80)
print("CHECK 1: 5-FOLD CROSS-VALIDATION")
print("="*80)
print("Method: Split data into 5 folds, train on 4, test on 1, repeat")

kfold = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = []
cv_maes = []

print(f"\n{'Fold':<6} {'Train R²':<12} {'Test R²':<12} {'Test MAE':<12} {'Overfit?':<10}")
print("-"*60)

for fold_num, (train_idx, test_idx) in enumerate(kfold.split(X), 1):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    reg_fold = LinearRegression()
    reg_fold.fit(X_train, y_train)

    train_score = reg_fold.score(X_train, y_train)
    test_score = reg_fold.score(X_test, y_test)
    test_mae = mean_absolute_error(y_test, reg_fold.predict(X_test))

    overfit = "YES" if train_score - test_score > 0.1 else "NO"

    cv_scores.append(test_score)
    cv_maes.append(test_mae)

    print(f"Fold {fold_num:<3} {train_score:>10.4f} {test_score:>10.4f} {test_mae:>10.2f} {overfit:>8}")

print("-"*60)
print(f"Mean:  {np.mean([r2]*5):>10.4f} {np.mean(cv_scores):>10.4f} {np.mean(cv_maes):>10.2f}")
print(f"Std:   {'':>10} {np.std(cv_scores):>10.4f} {np.std(cv_maes):>10.2f}")

print("\nInterpretation:")
if np.mean(cv_scores) > 0.80:
    print("  [EXCELLENT] Cross-validated R² > 0.80 - model generalizes well")
elif np.mean(cv_scores) > 0.60:
    print("  [GOOD] Cross-validated R² > 0.60 - acceptable generalization")
else:
    print("  [WARNING] Cross-validated R² < 0.60 - may be overfitting")

if np.std(cv_scores) < 0.05:
    print("  [STABLE] Low std dev - consistent across folds")
else:
    print("  [UNSTABLE] High std dev - performance varies by split")

# Check 2: Leave-One-Race-Out Cross-Validation
print("\n" + "="*80)
print("CHECK 2: LEAVE-ONE-RACE-OUT CROSS-VALIDATION")
print("="*80)
print("Method: Train on 11 races, test on 1 held-out race, repeat for all races")
print("This tests: Can model trained on some tracks predict unseen tracks?")

races = factor_scores['race'].values
logo = LeaveOneGroupOut()
logo_scores = []
logo_maes = []

print(f"\n{'Test Race':<18} {'Train R²':<12} {'Test R²':<12} {'Test MAE':<12} {'Overfit?':<10}")
print("-"*70)

for train_idx, test_idx in logo.split(X, y, groups=races):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    test_race = factor_scores.iloc[test_idx[0]]['race']

    reg_logo = LinearRegression()
    reg_logo.fit(X_train, y_train)

    train_score = reg_logo.score(X_train, y_train)
    test_score = reg_logo.score(X_test, y_test)
    test_mae = mean_absolute_error(y_test, reg_logo.predict(X_test))

    overfit = "YES" if train_score - test_score > 0.2 else "NO"

    logo_scores.append(test_score)
    logo_maes.append(test_mae)

    print(f"{test_race:<18} {train_score:>10.4f} {test_score:>10.4f} {test_mae:>10.2f} {overfit:>8}")

print("-"*70)
print(f"Mean:              {np.mean([r2]*12):>10.4f} {np.mean(logo_scores):>10.4f} {np.mean(logo_maes):>10.2f}")
print(f"Std:               {'':>10} {np.std(logo_scores):>10.4f} {np.std(logo_maes):>10.2f}")

print("\nInterpretation:")
if np.mean(logo_scores) > 0.75:
    print("  [EXCELLENT] LORO R² > 0.75 - model generalizes to new tracks")
elif np.mean(logo_scores) > 0.60:
    print("  [GOOD] LORO R² > 0.60 - acceptable generalization to new tracks")
else:
    print("  [WARNING] LORO R² < 0.60 - may be track-specific overfitting")

if np.std(logo_scores) < 0.10:
    print("  [STABLE] Low std dev - consistent across tracks")
else:
    print("  [VARIABLE] High std dev - some tracks harder to predict")

# Check 3: Residual Analysis
print("\n" + "="*80)
print("CHECK 3: RESIDUAL ANALYSIS")
print("="*80)
print("Check: Are errors randomly distributed or systematic?")

residuals = y - y_pred
print(f"\nResidual Statistics:")
print(f"  Mean:    {np.mean(residuals):6.3f} (should be ~0)")
print(f"  Std Dev: {np.std(residuals):6.3f}")
print(f"  Min:     {np.min(residuals):6.3f}")
print(f"  Max:     {np.max(residuals):6.3f}")

# Plot residuals
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Actual vs Predicted
axes[0].scatter(y, y_pred, alpha=0.5, s=30)
axes[0].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Perfect prediction')
axes[0].set_xlabel('Actual Finishing Position', fontsize=12)
axes[0].set_ylabel('Predicted Finishing Position', fontsize=12)
axes[0].set_title(f'Actual vs Predicted (R² = {r2:.3f})', fontsize=13, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Residual Distribution
axes[1].hist(residuals, bins=30, edgecolor='black', alpha=0.7)
axes[1].axvline(x=0, color='r', linestyle='--', linewidth=2, label='Zero error')
axes[1].set_xlabel('Prediction Error (positions)', fontsize=12)
axes[1].set_ylabel('Frequency', fontsize=12)
axes[1].set_title(f'Residual Distribution (MAE = {mae:.2f})', fontsize=13, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/analysis_outputs/prediction_diagnostics.png', dpi=150)
print("\n[SAVED] Prediction diagnostics: data/analysis_outputs/prediction_diagnostics.png")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("OVERFITTING VERDICT")
print("="*80)

print("\nMetric Summary:")
print(f"  Full Model R²:              {r2:.4f}")
print(f"  K-Fold Cross-Val R²:        {np.mean(cv_scores):.4f} (± {np.std(cv_scores):.4f})")
print(f"  Leave-One-Race-Out R²:      {np.mean(logo_scores):.4f} (± {np.std(logo_scores):.4f})")
print(f"  Average Error (MAE):        {mae:.2f} positions")
print(f"  Cross-Val MAE:              {np.mean(cv_maes):.2f} positions")

print("\nKey Findings:")

# Finding 1: Overall fit
if r2 > 0.85:
    print("  1. [EXCELLENT] Model explains 85%+ of variance")
else:
    print("  1. [GOOD] Model explains 60-85% of variance")

# Finding 2: Cross-validation
cv_drop = r2 - np.mean(cv_scores)
if cv_drop < 0.05:
    print(f"  2. [NO OVERFITTING] CV R² drops only {cv_drop:.3f} - model generalizes well")
elif cv_drop < 0.10:
    print(f"  2. [MILD OVERFITTING] CV R² drops {cv_drop:.3f} - some overfitting but acceptable")
else:
    print(f"  2. [OVERFITTING!] CV R² drops {cv_drop:.3f} - significant overfitting concern")

# Finding 3: Track generalization
loro_drop = r2 - np.mean(logo_scores)
if loro_drop < 0.10:
    print(f"  3. [GENERALIZES] LORO R² drops only {loro_drop:.3f} - works on unseen tracks")
elif loro_drop < 0.20:
    print(f"  3. [MODERATE] LORO R² drops {loro_drop:.3f} - some track-specific learning")
else:
    print(f"  3. [TRACK-SPECIFIC] LORO R² drops {loro_drop:.3f} - may not generalize to new tracks")

# Finding 4: Practical accuracy
if mae < 2.0:
    print(f"  4. [VERY ACCURATE] Average error = {mae:.2f} positions (< 2 positions off)")
elif mae < 3.5:
    print(f"  4. [ACCURATE] Average error = {mae:.2f} positions (< 3.5 positions off)")
else:
    print(f"  4. [MODERATE] Average error = {mae:.2f} positions (predictions are rough)")

print("\n" + "="*80)
print("FINAL VERDICT")
print("="*80)

if cv_drop < 0.05 and loro_drop < 0.10 and mae < 3.0:
    print("\nPASS NO SIGNIFICANT OVERFITTING")
    print("   Model generalizes well to new data and new tracks")
    print("   Safe to use for predictions")
elif cv_drop < 0.10 and loro_drop < 0.20:
    print("\nWARN MILD OVERFITTING")
    print("   Model shows some memorization but still useful")
    print("   Predictions should be interpreted with caution")
else:
    print("\nFAIL OVERFITTING DETECTED")
    print("   Model may be memorizing training data")
    print("   Consider: fewer features, regularization, or more data")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print()
