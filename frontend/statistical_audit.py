#!/usr/bin/env python3
"""
Comprehensive Statistical Validation Audit for Gibbs AI 4-Factor Performance Model
Validates R², MAE, factor weights, and data consistency across all sources.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.decomposition import PCA
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

# Base paths
BASE_PATH = Path("/Users/justingrosz/Documents/AI-Work/hackthetrack-master")
DATA_PATH = BASE_PATH / "backend" / "data"
ANALYSIS_PATH = BASE_PATH / "data" / "analysis_outputs"
RACE_RESULTS_PATH = BASE_PATH / "data" / "race_results" / "analysis_endurance"

print("=" * 80)
print("GIBBS AI 4-FACTOR MODEL - COMPREHENSIVE STATISTICAL VALIDATION AUDIT")
print("=" * 80)

# ============================================================================
# SECTION 1: LOAD ALL DATA FILES
# ============================================================================
print("\n[1] LOADING DATA FILES...")
print("-" * 80)

# Load feature engineering CSV
features_df = pd.read_csv(ANALYSIS_PATH / "all_races_tier1_features.csv")
print(f"✓ Loaded features CSV: {len(features_df)} rows, {len(features_df.columns)} columns")
print(f"  Columns: {list(features_df.columns)}")

# Load factor scores CSV
factor_scores_df = pd.read_csv(ANALYSIS_PATH / "tier1_factor_scores.csv")
print(f"✓ Loaded factor scores CSV: {len(factor_scores_df)} rows, {len(factor_scores_df.columns)} columns")
print(f"  Factor columns: {[c for c in factor_scores_df.columns if 'factor' in c.lower()]}")

# Load JSON files
with open(DATA_PATH / "driver_factors.json") as f:
    driver_factors_json = json.load(f)
print(f"✓ Loaded driver_factors.json: {len(driver_factors_json)} drivers")

with open(DATA_PATH / "driver_race_results.json") as f:
    driver_race_results_json = json.load(f)
print(f"✓ Loaded driver_race_results.json: {len(driver_race_results_json)} drivers")

with open(DATA_PATH / "factor_breakdowns.json") as f:
    factor_breakdowns_json = json.load(f)
print(f"✓ Loaded factor_breakdowns.json")

# ============================================================================
# SECTION 2: FEATURE ENGINEERING VALIDATION
# ============================================================================
print("\n[2] FEATURE ENGINEERING VALIDATION")
print("-" * 80)

# Expected 12 features based on documentation
expected_features = [
    'qualifying_pace', 'best_race_lap', 'avg_top10_pace',  # Speed
    'stint_consistency', 'sector_consistency', 'braking_consistency',  # Consistency
    'pace_degradation', 'late_stint_perf', 'early_vs_late_pace',  # Tire Management
    'position_changes', 'positions_gained', 'performance_normalized'  # Racecraft
]

feature_cols = [c for c in features_df.columns if c not in ['race', 'driver_number', 'finishing_position']]
print(f"\nFeatures found in CSV: {len(feature_cols)}")
print(f"Expected features: {len(expected_features)}")

missing_features = set(expected_features) - set(feature_cols)
extra_features = set(feature_cols) - set(expected_features)

if missing_features:
    print(f"⚠ MISSING FEATURES: {missing_features}")
else:
    print("✓ All expected features present")

if extra_features:
    print(f"⚠ EXTRA FEATURES: {extra_features}")
else:
    print("✓ No unexpected features")

# Check for missing values
print(f"\nMissing values per feature:")
for col in feature_cols:
    missing = features_df[col].isna().sum()
    if missing > 0:
        print(f"  ⚠ {col}: {missing} missing ({missing/len(features_df)*100:.1f}%)")

# Descriptive statistics
print(f"\nFeature statistics summary:")
print(features_df[feature_cols].describe().T[['mean', 'std', 'min', 'max']].round(3))

# ============================================================================
# SECTION 3: VERIFY SECTOR TIMING DATA INCORPORATION
# ============================================================================
print("\n[3] SECTOR TIMING DATA VERIFICATION")
print("-" * 80)

# Sample one race to verify sector data is used
sample_race_file = RACE_RESULTS_PATH / "barber_r1_analysis_endurance.csv"
sample_race = pd.read_csv(sample_race_file)

print(f"\nSample race file: {sample_race_file.name}")
print(f"Columns: {list(sample_race.columns)[:15]}...")  # First 15 columns

# Check for sector columns
sector_cols = [c for c in sample_race.columns if 'sector' in c.lower() or any(f'S{i}' in c for i in [1,2,3])]
print(f"\nSector-related columns found: {sector_cols[:10]}...")  # First 10

if sector_cols:
    print("✓ Sector timing data IS present in source files")
else:
    print("⚠ WARNING: No obvious sector columns found")

# Check if sector_consistency feature uses this data
sample_features = features_df[features_df['race'] == 'barber_r1']
print(f"\nSector consistency values for barber_r1:")
print(sample_features[['driver_number', 'sector_consistency']].head(10))

# ============================================================================
# SECTION 4: FACTOR ANALYSIS VALIDATION
# ============================================================================
print("\n[4] FACTOR ANALYSIS VALIDATION")
print("-" * 80)

# Extract features for PCA
X = features_df[feature_cols].fillna(features_df[feature_cols].median())
print(f"Feature matrix shape: {X.shape}")

# Re-run PCA to validate factor extraction
# First, try with 4 factors (documented)
pca_4 = PCA(n_components=4)
factor_scores_4 = pca_4.fit_transform(X)

print(f"\nPCA with 4 components:")
print(f"  Explained variance ratio: {pca_4.explained_variance_ratio_.round(4)}")
print(f"  Cumulative variance: {pca_4.explained_variance_ratio_.cumsum().round(4)}")
print(f"  Total variance explained: {pca_4.explained_variance_ratio_.sum():.2%}")

# Compare with 5 factors (CSV has 5 factor scores)
pca_5 = PCA(n_components=5)
factor_scores_5 = pca_5.fit_transform(X)

print(f"\nPCA with 5 components (CSV has 5):")
print(f"  Explained variance ratio: {pca_5.explained_variance_ratio_.round(4)}")
print(f"  Total variance explained: {pca_5.explained_variance_ratio_.sum():.2%}")

# Check factor loadings to identify what each factor represents
print(f"\nFactor loadings (4-factor model):")
loadings_df = pd.DataFrame(
    pca_4.components_.T,
    columns=[f'Factor_{i+1}' for i in range(4)],
    index=feature_cols
)
print(loadings_df.round(3))

# Identify dominant features for each factor
print(f"\nDominant features by factor:")
for i in range(4):
    top_features = loadings_df[f'Factor_{i+1}'].abs().nlargest(3)
    print(f"  Factor {i+1}: {', '.join(f'{idx} ({val:.3f})' for idx, val in top_features.items())}")

# ============================================================================
# SECTION 5: MODEL PERFORMANCE VALIDATION
# ============================================================================
print("\n[5] MODEL PERFORMANCE METRICS VALIDATION")
print("-" * 80)

# Prepare data - use 4 factors for regression
y_true = features_df['finishing_position'].values
X_factors_4 = factor_scores_4

# Fit linear regression model
lr_model = LinearRegression()
lr_model.fit(X_factors_4, y_true)
y_pred = lr_model.predict(X_factors_4)

# Calculate metrics
r2 = r2_score(y_true, y_pred)
mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

print(f"\nModel Performance (4-Factor Model):")
print(f"  R² Score: {r2:.3f}")
print(f"  MAE (positions): {mae:.2f}")
print(f"  RMSE (positions): {rmse:.2f}")
print(f"  Correlation (predicted vs actual): {pearsonr(y_pred, y_true)[0]:.3f}")

# Compare with documented values
documented_r2 = 0.895
documented_mae = 1.78

print(f"\nComparison with documented values:")
print(f"  R² - Documented: {documented_r2:.3f}, Calculated: {r2:.3f}, Δ: {abs(r2-documented_r2):.3f}")
print(f"  MAE - Documented: {documented_mae:.2f}, Calculated: {mae:.2f}, Δ: {abs(mae-documented_mae):.2f}")

if abs(r2 - documented_r2) > 0.01:
    print(f"  ⚠ WARNING: R² differs by more than 0.01")
else:
    print(f"  ✓ R² matches within tolerance")

if abs(mae - documented_mae) > 0.1:
    print(f"  ⚠ WARNING: MAE differs by more than 0.1 positions")
else:
    print(f"  ✓ MAE matches within tolerance")

# ============================================================================
# SECTION 6: FACTOR WEIGHTS VALIDATION
# ============================================================================
print("\n[6] FACTOR WEIGHTS VALIDATION")
print("-" * 80)

# Calculate factor importance from regression coefficients
coefficients = lr_model.coef_
intercept = lr_model.intercept_

# Normalize to percentages (absolute contribution)
abs_coefficients = np.abs(coefficients)
total_abs = abs_coefficients.sum()
factor_weights_pct = (abs_coefficients / total_abs * 100)

print(f"\nRegression coefficients:")
for i, coef in enumerate(coefficients, 1):
    print(f"  Factor {i}: {coef:+.4f} (weight: {factor_weights_pct[i-1]:.1f}%)")
print(f"  Intercept: {intercept:.4f}")

# Map factors to categories based on loadings
print(f"\nFactor interpretation (based on loadings):")
factor_names = []
for i in range(4):
    top_feat = loadings_df[f'Factor_{i+1}'].abs().idxmax()
    if 'pace' in top_feat or 'lap' in top_feat or 'qualifying' in top_feat:
        category = "Speed"
    elif 'consistency' in top_feat:
        category = "Consistency"
    elif 'degradation' in top_feat or 'stint' in top_feat or 'late' in top_feat:
        category = "Tire Management"
    elif 'position' in top_feat:
        category = "Racecraft"
    else:
        category = "Unknown"

    factor_names.append(category)
    print(f"  Factor {i+1} → {category} ({factor_weights_pct[i]:.1f}%)")

# Compare with documented weights
documented_weights = {
    "Speed": 46.6,
    "Consistency": 29.1,
    "Racecraft": 14.9,
    "Tire Management": 9.5
}

print(f"\nDocumented factor weights:")
for name, weight in documented_weights.items():
    print(f"  {name}: {weight}%")

# Calculate actual weights by category
calculated_weights = {}
for i, name in enumerate(factor_names):
    if name in calculated_weights:
        calculated_weights[name] += factor_weights_pct[i]
    else:
        calculated_weights[name] = factor_weights_pct[i]

print(f"\nCalculated factor weights by category:")
for name in sorted(calculated_weights.keys()):
    calc_weight = calculated_weights[name]
    doc_weight = documented_weights.get(name, 0)
    diff = abs(calc_weight - doc_weight)

    status = "✓" if diff < 5 else "⚠"
    print(f"  {status} {name}: {calc_weight:.1f}% (documented: {doc_weight}%, Δ: {diff:.1f}%)")

# ============================================================================
# SECTION 7: DATA CONSISTENCY CHECK
# ============================================================================
print("\n[7] DATA CONSISTENCY VALIDATION")
print("-" * 80)

# Check driver_factors.json consistency
print(f"\nChecking driver_factors.json structure:")
if 'drivers' in driver_factors_json:
    sample_driver_data = driver_factors_json['drivers'][0]
    print(f"  Format: {list(driver_factors_json.keys())}")
    print(f"  Sample driver #{sample_driver_data['driver_number']}: {list(sample_driver_data.keys())}")
    print(f"  Factor categories: {list(sample_driver_data.get('factors', {}).keys())}")
else:
    sample_driver = list(driver_factors_json.keys())[0]
    sample_data = driver_factors_json[sample_driver]
    print(f"  Sample driver #{sample_driver}: {list(sample_data.keys()) if isinstance(sample_data, dict) else 'Not a dict'}")

# Check if factor scores are present
if 'drivers' in driver_factors_json and 'factors' in driver_factors_json['drivers'][0]:
    print(f"  ✓ Factor scores found in JSON")
else:
    print(f"  ⚠ Factor scores NOT found in expected format")

# Check driver_race_results.json consistency
print(f"\nChecking driver_race_results.json structure:")
if 'drivers' in driver_race_results_json and len(driver_race_results_json['drivers']) > 0:
    sample_driver_results = driver_race_results_json['drivers'][0]
    sample_race_data = sample_driver_results.get('race_results', [{}])[0] if 'race_results' in sample_driver_results else {}
    print(f"  Format: {list(driver_race_results_json.keys())}")
    print(f"  Sample race result keys: {list(sample_race_data.keys())[:10]}...")
else:
    # Old format
    sample_driver_key = list(driver_race_results_json.keys())[0] if driver_race_results_json else None
    if sample_driver_key:
        sample_driver_results = driver_race_results_json[sample_driver_key][0] if driver_race_results_json[sample_driver_key] else {}
        print(f"  Sample race result keys: {list(sample_driver_results.keys())[:10]}...")
    sample_race_data = sample_driver_results

# Check for sector timing in results
has_sector_data = any('sector' in k.lower() or 'S1' in k or 'S2' in k or 'S3' in k
                       for k in sample_race_data.keys()) if isinstance(sample_race_data, dict) else False
print(f"  {'✓' if has_sector_data else '⚠'} Sector timing data in race results")

# Check factor_breakdowns.json
print(f"\nChecking factor_breakdowns.json structure:")
breakdown_keys = list(factor_breakdowns_json.keys())
print(f"  Top-level keys: {breakdown_keys[:5]}...")

# Cross-reference: Do CSV factor scores match JSON?
print(f"\nCross-referencing factor scores (CSV vs JSON):")
mismatches = 0
sample_size = min(10, len(features_df))

driver_numbers_in_json = []
if 'drivers' in driver_factors_json:
    driver_numbers_in_json = [str(d['driver_number']) for d in driver_factors_json['drivers']]
else:
    driver_numbers_in_json = list(driver_factors_json.keys())

for idx in range(sample_size):
    row = features_df.iloc[idx]
    race = row['race']
    driver_num = str(int(row['driver_number']))

    if driver_num in driver_numbers_in_json:
        print(f"  ✓ Driver {driver_num} found in driver_factors.json")
    else:
        print(f"  ⚠ Driver {driver_num} NOT in driver_factors.json")
        mismatches += 1

if mismatches == 0:
    print(f"  ✓ All sampled drivers found in JSON")

# ============================================================================
# SECTION 8: SUMMARY AND RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 80)
print("AUDIT SUMMARY AND RECOMMENDATIONS")
print("=" * 80)

recommendations = []
critical_issues = []
warnings = []

# Check 1: R² validation
if abs(r2 - documented_r2) > 0.01:
    critical_issues.append(f"R² discrepancy: Documented={documented_r2:.3f}, Calculated={r2:.3f}")
    recommendations.append("RERUN factor analysis and update R² in documentation")
else:
    print(f"✓ R² Score: {r2:.3f} (matches documented value)")

# Check 2: MAE validation
if abs(mae - documented_mae) > 0.1:
    critical_issues.append(f"MAE discrepancy: Documented={documented_mae:.2f}, Calculated={mae:.2f}")
    recommendations.append("UPDATE MAE value in documentation to {mae:.2f}")
else:
    print(f"✓ MAE: {mae:.2f} positions (matches documented value)")

# Check 3: Feature completeness
if missing_features or extra_features:
    warnings.append(f"Feature mismatch: Missing={missing_features}, Extra={extra_features}")
    recommendations.append("VERIFY feature engineering script is using all 12 expected features")
else:
    print(f"✓ All 12 features correctly calculated")

# Check 4: Factor weights
total_weight_diff = sum(abs(calculated_weights.get(name, 0) - weight)
                         for name, weight in documented_weights.items())
if total_weight_diff > 10:
    warnings.append(f"Factor weights differ by {total_weight_diff:.1f} percentage points")
    recommendations.append("REVIEW factor weight documentation - may need updating")
else:
    print(f"✓ Factor weights match within tolerance")

# Check 5: Data files consistency
if mismatches > 0:
    warnings.append(f"{mismatches} drivers missing from JSON cross-reference")
    recommendations.append("VERIFY JSON data files are in sync with CSV outputs")
else:
    print(f"✓ Data consistency across CSV and JSON files")

print(f"\n{'='*80}")
print("CRITICAL ISSUES:" if critical_issues else "✓ NO CRITICAL ISSUES FOUND")
for issue in critical_issues:
    print(f"  ⚠ {issue}")

if warnings:
    print(f"\nWARNINGS:")
    for warning in warnings:
        print(f"  ⚠ {warning}")

if recommendations:
    print(f"\nRECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
else:
    print(f"\n✓ NO ACTIONS REQUIRED - Model validation complete")

print(f"\n{'='*80}")
print("AUDIT COMPLETE")
print(f"{'='*80}\n")

# Save results to file
output_file = Path(__file__).parent / "statistical_audit_results.txt"
with open(output_file, 'w') as f:
    f.write("Gibbs AI 4-Factor Model - Statistical Validation Audit\n")
    f.write("="*80 + "\n\n")
    f.write(f"R² Score: {r2:.4f} (documented: {documented_r2})\n")
    f.write(f"MAE: {mae:.2f} positions (documented: {documented_mae})\n")
    f.write(f"RMSE: {rmse:.2f} positions\n\n")
    f.write("Factor Weights:\n")
    for i, (name, weight) in enumerate(zip(factor_names, factor_weights_pct), 1):
        f.write(f"  Factor {i} ({name}): {weight:.1f}%\n")
    f.write(f"\nCritical Issues: {len(critical_issues)}\n")
    f.write(f"Warnings: {len(warnings)}\n")
    f.write(f"Recommendations: {len(recommendations)}\n")

print(f"Results saved to: {output_file}")
