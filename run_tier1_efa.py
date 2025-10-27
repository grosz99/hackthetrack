"""
RUN TIER 1 EXPLORATORY FACTOR ANALYSIS
=======================================

Test EFA on 12 highest confidence variables to validate approach.
This is Step 2 of the Five-Step Implementation Plan.

Based on:
- FIVE_STEP_IMPLEMENTATION_PLAN.md
- REPTRAK_MODEL_FOR_RACING.md
- circuit_fit_research_methodology.md
"""

import pandas as pd
import numpy as np
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler
from scipy.stats import bartlett
from factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
import matplotlib.pyplot as plt
import seaborn as sns

print("\n" + "="*80)
print("TIER 1 EXPLORATORY FACTOR ANALYSIS")
print("="*80)
print("\nObjective: Test if 12 variables reveal coherent skill factors")
print("Expected: 3-5 factors from Tier 1 (RAW SPEED, CONSISTENCY, TIRE MGMT, RACECRAFT)")
print("="*80)

# Load Tier 1 feature matrix
print("\n[LOAD] Reading all_races_tier1_features.csv...")
df = pd.read_csv('data/analysis_outputs/all_races_tier1_features.csv')
print(f"Shape: {df.shape}")
print(f"Races: {df['race'].nunique()}")
print(f"Drivers: {df['driver_number'].nunique()}")
print(f"Observations: {len(df)}")

# Define feature columns (exclude metadata and outcome)
feature_cols = [
    'qualifying_pace', 'best_race_lap', 'avg_top10_pace',  # RAW SPEED
    'stint_consistency', 'sector_consistency', 'braking_consistency',  # CONSISTENCY
    'pace_degradation', 'late_stint_perf', 'early_vs_late_pace',  # TIRE MANAGEMENT
    'position_changes', 'positions_gained', 'performance_normalized'  # RACECRAFT
]

print(f"\n[FEATURES] Using {len(feature_cols)} variables:")
for i, col in enumerate(feature_cols, 1):
    missing_pct = (df[col].isna().sum() / len(df)) * 100
    print(f"  {i:2d}. {col:30s} - {missing_pct:4.1f}% missing")

# Handle missing values (drop rows with any missing features)
print(f"\n[CLEAN] Handling missing values...")
df_clean = df[feature_cols + ['finishing_position', 'race', 'driver_number']].dropna()
print(f"Observations after dropping NaN: {len(df)} -> {len(df_clean)}")
print(f"Data retained: {len(df_clean)/len(df)*100:.1f}%")

# Extract feature matrix
X = df_clean[feature_cols].values
print(f"\n[MATRIX] Feature matrix shape: {X.shape}")

# Standardize features (mean=0, std=1)
print(f"\n[STANDARDIZE] Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"Mean check (should be ~0): {X_scaled.mean(axis=0).mean():.6f}")
print(f"Std check (should be ~1): {X_scaled.std(axis=0).mean():.6f}")

# ============================================================================
# STEP 1: TEST EFA SUITABILITY
# ============================================================================
print("\n" + "="*80)
print("STEP 1: TEST EFA SUITABILITY")
print("="*80)

# Test 1: Bartlett's Test of Sphericity
print("\n[TEST 1] Bartlett's Test of Sphericity")
print("  H0: Variables are uncorrelated (identity matrix)")
print("  Need: p < 0.05 to reject H0 (variables ARE correlated)")
chi_square, p_value = calculate_bartlett_sphericity(X_scaled)
print(f"  Chi-square: {chi_square:.2f}")
print(f"  p-value: {p_value:.6f}")
if p_value < 0.05:
    print("  [PASS] Variables are significantly correlated - EFA is appropriate")
else:
    print("  [FAIL] Variables are not correlated enough - EFA questionable")

# Test 2: Kaiser-Meyer-Olkin (KMO) Test
print("\n[TEST 2] Kaiser-Meyer-Olkin (KMO) Test")
print("  Measures sampling adequacy")
print("  Need: KMO > 0.6 (>0.7 is good, >0.8 is great)")
kmo_all, kmo_model = calculate_kmo(X_scaled)
print(f"  Overall KMO: {kmo_model:.3f}")
if kmo_model > 0.8:
    print("  [EXCELLENT] Sampling adequacy is great")
elif kmo_model > 0.7:
    print("  [GOOD] Sampling adequacy is good")
elif kmo_model > 0.6:
    print("  [PASS] Sampling adequacy is acceptable")
else:
    print("  [FAIL] Sampling inadequate for EFA")

print("\n  KMO by variable:")
for i, col in enumerate(feature_cols):
    status = "[OK]" if kmo_all[i] > 0.6 else "[WARN]"
    print(f"    {status} {col:30s}: {kmo_all[i]:.3f}")

# ============================================================================
# STEP 2: DETERMINE NUMBER OF FACTORS
# ============================================================================
print("\n" + "="*80)
print("STEP 2: DETERMINE NUMBER OF FACTORS")
print("="*80)

# Correlation matrix eigenvalues
print("\n[SCREE] Calculating eigenvalues from correlation matrix...")
corr_matrix = np.corrcoef(X_scaled.T)
eigenvalues, eigenvectors = np.linalg.eig(corr_matrix)
eigenvalues = sorted(eigenvalues, reverse=True)

print("\nEigenvalues (Kaiser criterion: > 1.0):")
for i, ev in enumerate(eigenvalues, 1):
    status = "[RETAIN]" if ev > 1.0 else "[DROP]"
    print(f"  Factor {i:2d}: {ev:6.3f} {status}")

# Count factors > 1.0
n_factors_kaiser = sum(1 for ev in eigenvalues if ev > 1.0)
print(f"\nKaiser criterion suggests: {n_factors_kaiser} factors")

# Scree plot
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(eigenvalues)+1), eigenvalues, 'bo-', linewidth=2, markersize=8)
plt.axhline(y=1.0, color='r', linestyle='--', label='Kaiser criterion (eigenvalue = 1)')
plt.xlabel('Factor Number', fontsize=12)
plt.ylabel('Eigenvalue', fontsize=12)
plt.title('Scree Plot - Tier 1 Variables (12 features)', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
scree_path = 'data/analysis_outputs/tier1_scree_plot.png'
plt.savefig(scree_path, dpi=150)
print(f"\n[SAVED] Scree plot: {scree_path}")
plt.close()

# ============================================================================
# STEP 3: RUN EXPLORATORY FACTOR ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("STEP 3: RUN EXPLORATORY FACTOR ANALYSIS")
print("="*80)

# Test multiple factor solutions
print("\n[EFA] Testing factor solutions from 2 to 6...")
for n_factors in range(2, 7):
    print(f"\n--- {n_factors} Factor Solution ---")

    fa = FactorAnalysis(n_components=n_factors, random_state=42, max_iter=1000)
    factor_scores = fa.fit_transform(X_scaled)

    # Get loadings
    loadings = fa.components_.T

    # Calculate variance explained (approximate)
    # For each factor, sum of squared loadings / number of variables
    variance_per_factor = (loadings**2).sum(axis=0) / len(feature_cols)
    total_variance = variance_per_factor.sum()

    print(f"Variance explained per factor:")
    for i, var in enumerate(variance_per_factor, 1):
        print(f"  Factor {i}: {var:.3f} ({var/total_variance*100:.1f}%)")
    print(f"Total variance explained: {total_variance:.3f} ({total_variance/len(feature_cols)*100:.1f}%)")

# ============================================================================
# STEP 4: INTERPRET BEST SOLUTION
# ============================================================================
print("\n" + "="*80)
print("STEP 4: INTERPRET FACTOR LOADINGS")
print("="*80)

# Use Kaiser criterion result
n_factors_best = n_factors_kaiser
print(f"\nInterpreting {n_factors_best}-factor solution...")

fa_best = FactorAnalysis(n_components=n_factors_best, random_state=42, max_iter=1000)
factor_scores = fa_best.fit_transform(X_scaled)
loadings = fa_best.components_.T

# Create loadings dataframe
loadings_df = pd.DataFrame(
    loadings,
    columns=[f'Factor_{i+1}' for i in range(n_factors_best)],
    index=feature_cols
)

print("\nFactor Loadings (absolute > 0.4 highlighted):")
print(loadings_df.to_string(float_format=lambda x: f"{x:6.3f}"))

# Highlight strongest loadings per factor
print("\n" + "="*80)
print("STRONGEST LOADINGS PER FACTOR (>0.4)")
print("="*80)
for factor_col in loadings_df.columns:
    print(f"\n{factor_col}:")
    high_loadings = loadings_df[loadings_df[factor_col].abs() > 0.4][factor_col].sort_values(key=abs, ascending=False)
    if len(high_loadings) > 0:
        for var, loading in high_loadings.items():
            print(f"  {loading:6.3f}  {var}")
    else:
        print("  (No loadings > 0.4)")

# Save loadings
loadings_path = 'data/analysis_outputs/tier1_factor_loadings.csv'
loadings_df.to_csv(loadings_path)
print(f"\n[SAVED] Factor loadings: {loadings_path}")

# Heatmap of loadings
plt.figure(figsize=(10, 8))
sns.heatmap(loadings_df, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            vmin=-1, vmax=1, cbar_kws={'label': 'Loading'})
plt.title(f'Factor Loadings Heatmap - {n_factors_best} Factor Solution', fontsize=14, fontweight='bold')
plt.xlabel('Factors', fontsize=12)
plt.ylabel('Variables', fontsize=12)
plt.tight_layout()
heatmap_path = 'data/analysis_outputs/tier1_loadings_heatmap.png'
plt.savefig(heatmap_path, dpi=150)
print(f"[SAVED] Loadings heatmap: {heatmap_path}")
plt.close()

# ============================================================================
# STEP 5: VALIDATE AGAINST RACE RESULTS
# ============================================================================
print("\n" + "="*80)
print("STEP 5: VALIDATE AGAINST RACE RESULTS")
print("="*80)

# Add factor scores to dataframe
df_clean_copy = df_clean.copy()
for i in range(n_factors_best):
    df_clean_copy[f'factor_{i+1}_score'] = factor_scores[:, i]

# Correlate each factor with finishing position
print("\n[CORRELATE] Factor scores vs Finishing Position")
print("(Negative correlation expected: lower position = better finish)")
for i in range(n_factors_best):
    corr = df_clean_copy[f'factor_{i+1}_score'].corr(df_clean_copy['finishing_position'])
    print(f"  Factor {i+1} vs Finish: r = {corr:6.3f}")

# Multiple regression: predict finishing position from all factors
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

X_factors = factor_scores
y_finish = df_clean_copy['finishing_position'].values

reg = LinearRegression()
reg.fit(X_factors, y_finish)
y_pred = reg.predict(X_factors)
r2 = r2_score(y_finish, y_pred)

print(f"\n[REGRESSION] Predicting Finishing Position from {n_factors_best} Factors")
print(f"R-squared: {r2:.3f}")
print(f"Target: R² > 0.60 (circuit fit research)")
if r2 > 0.60:
    print("[PASS] Factors explain race results well")
elif r2 > 0.40:
    print("[WARN] Moderate predictive power - may need more variables")
else:
    print("[FAIL] Weak predictive power - need more variables or different factors")

print("\nFactor coefficients:")
for i, coef in enumerate(reg.coef_, 1):
    print(f"  Factor {i}: {coef:7.3f}")
print(f"  Intercept: {reg.intercept_:7.3f}")

# Save factor scores
factor_scores_df = df_clean_copy[['race', 'driver_number', 'finishing_position'] +
                                   [f'factor_{i+1}_score' for i in range(n_factors_best)]]
scores_path = 'data/analysis_outputs/tier1_factor_scores.csv'
factor_scores_df.to_csv(scores_path, index=False)
print(f"\n[SAVED] Factor scores: {scores_path}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("TIER 1 EFA SUMMARY")
print("="*80)

print(f"\n[SUITABILITY]")
print(f"  Bartlett p-value: {p_value:.6f} (need < 0.05) - {'PASS' if p_value < 0.05 else 'FAIL'}")
print(f"  KMO: {kmo_model:.3f} (need > 0.6) - {'PASS' if kmo_model > 0.6 else 'FAIL'}")

print(f"\n[FACTOR STRUCTURE]")
print(f"  Number of factors (Kaiser): {n_factors_best}")
print(f"  Variance explained: {total_variance:.3f} ({total_variance/len(feature_cols)*100:.1f}%)")

print(f"\n[VALIDATION]")
print(f"  R-squared (factors to finish): {r2:.3f} (target > 0.60) - {'PASS' if r2 > 0.60 else 'WARN' if r2 > 0.40 else 'FAIL'}")

print(f"\n[NEXT STEPS]")
if r2 > 0.60 and kmo_model > 0.6 and p_value < 0.05:
    print("  1. [OK] Tier 1 validates the approach!")
    print("  2. Add Tier 2 variables (8 more) and re-run EFA")
    print("  3. Add Tier 3 variables (6 more) for final 26-variable model")
    print("  4. Build track demand profiles")
    print("  5. Create circuit fit scoring")
else:
    print("  1. [WARN] Tier 1 results need review")
    print("  2. Check if we need to adjust variables or add Tier 2 immediately")
    print("  3. Review factor interpretations")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print("\nOutputs saved:")
print(f"  - {scree_path}")
print(f"  - {loadings_path}")
print(f"  - {heatmap_path}")
print(f"  - {scores_path}")
print()
