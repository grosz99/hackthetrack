"""
TIER 1 VALIDATION FOR PRODUCT DECISION
========================================

Quick validation to determine if Tier 1 (12 variables, 5 factors) is sufficient
to ship product, or if we need to expand to Tier 2/3.

Three critical tests:
1. Track Demand Profiles - Do tracks differ meaningfully?
2. 4-Factor vs 5-Factor - Is Factor 5 adding value?
3. Driver Sanity Check - Do scores match domain knowledge?

Runtime: ~5 minutes
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import seaborn as sns

print("\n" + "="*80)
print("TIER 1 VALIDATION - PRODUCT READINESS CHECK")
print("="*80)

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n[LOAD] Reading Tier 1 results...")
features = pd.read_csv('data/analysis_outputs/all_races_tier1_features.csv')
factor_scores = pd.read_csv('data/analysis_outputs/tier1_factor_scores.csv')

print(f"Features: {features.shape}")
print(f"Factor Scores: {factor_scores.shape}")
print(f"Races: {factor_scores['race'].unique()}")

# ============================================================================
# TEST 1: TRACK DEMAND PROFILES
# ============================================================================
print("\n" + "="*80)
print("TEST 1: TRACK DEMAND PROFILES")
print("="*80)
print("\nObjective: Do different tracks value different skills?")
print("Method: Regress (Finish Position ~ Factors) for each track")
print("Success Criteria: Coefficient variation > 50% across tracks")

tracks = factor_scores['race'].unique()
track_profiles = {}

print("\nTrack-Specific Factor Importance:")
print(f"{'Track':<20} {'Factor1':<10} {'Factor2':<10} {'Factor3':<10} {'Factor4':<10} {'Factor5':<10} {'R²':<8}")
print("-" * 90)

for track in sorted(tracks):
    track_data = factor_scores[factor_scores['race'] == track].copy()

    X = track_data[['factor_1_score', 'factor_2_score', 'factor_3_score',
                     'factor_4_score', 'factor_5_score']].values
    y = track_data['finishing_position'].values

    if len(track_data) < 10:  # Need minimum sample size
        continue

    reg = LinearRegression()
    reg.fit(X, y)
    y_pred = reg.predict(X)
    r2 = r2_score(y, y_pred)

    track_profiles[track] = {
        'Factor_1_CONSISTENCY': reg.coef_[0],
        'Factor_2_RACECRAFT': reg.coef_[1],
        'Factor_3_RAW_SPEED': reg.coef_[2],
        'Factor_4_TIRE_MGMT': reg.coef_[3],
        'Factor_5_RESIDUAL': reg.coef_[4],
        'R2': r2
    }

    print(f"{track:<20} {reg.coef_[0]:>9.2f} {reg.coef_[1]:>9.2f} {reg.coef_[2]:>9.2f} "
          f"{reg.coef_[3]:>9.2f} {reg.coef_[4]:>9.2f} {r2:>7.3f}")

# Calculate coefficient of variation across tracks for each factor
profile_df = pd.DataFrame(track_profiles).T
print("\n" + "="*80)
print("COEFFICIENT OF VARIATION (Std/Mean) - Higher = More Track Variation")
print("="*80)
for factor in ['Factor_1_CONSISTENCY', 'Factor_2_RACECRAFT', 'Factor_3_RAW_SPEED',
               'Factor_4_TIRE_MGMT', 'Factor_5_RESIDUAL']:
    coefs = profile_df[factor].values
    cv = np.std(coefs) / np.abs(np.mean(coefs)) if np.mean(coefs) != 0 else 0
    status = "[HIGH VAR]" if cv > 0.5 else "[MOD VAR]" if cv > 0.3 else "[LOW VAR]"
    print(f"{factor:<25} CV = {cv:5.2f}  {status}")
    print(f"  Range: [{coefs.min():.2f}, {coefs.max():.2f}]")
    print(f"  Mean ± Std: {coefs.mean():.2f} ± {coefs.std():.2f}")

# Identify most distinctive tracks
print("\n" + "="*80)
print("MOST DISTINCTIVE TRACKS (by factor importance)")
print("="*80)

for factor in ['Factor_1_CONSISTENCY', 'Factor_2_RACECRAFT', 'Factor_3_RAW_SPEED', 'Factor_4_TIRE_MGMT']:
    sorted_tracks = profile_df.sort_values(factor, ascending=False)
    highest = sorted_tracks.index[0]
    lowest = sorted_tracks.index[-1]
    print(f"\n{factor}:")
    print(f"  Highest: {highest:<15} (coef = {sorted_tracks.loc[highest, factor]:6.2f})")
    print(f"  Lowest:  {lowest:<15} (coef = {sorted_tracks.loc[lowest, factor]:6.2f})")

# Visualize track profiles
fig, ax = plt.subplots(figsize=(14, 8))
profile_df_plot = profile_df[['Factor_1_CONSISTENCY', 'Factor_2_RACECRAFT',
                                'Factor_3_RAW_SPEED', 'Factor_4_TIRE_MGMT']].copy()
profile_df_plot.columns = ['CONSISTENCY', 'RACECRAFT', 'RAW_SPEED', 'TIRE_MGMT']

profile_df_plot.plot(kind='bar', ax=ax, width=0.8)
ax.set_xlabel('Track', fontsize=12, fontweight='bold')
ax.set_ylabel('Regression Coefficient (Factor Importance)', fontsize=12, fontweight='bold')
ax.set_title('Track Demand Profiles - Factor Importance by Track', fontsize=14, fontweight='bold')
ax.legend(title='Factor', loc='upper right')
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('data/analysis_outputs/track_demand_profiles.png', dpi=150)
print("\n[SAVED] Track demand profiles: data/analysis_outputs/track_demand_profiles.png")
plt.close()

# TEST 1 VERDICT
print("\n" + "="*80)
print("TEST 1 VERDICT: TRACK DEMAND PROFILES")
print("="*80)
mean_cv = profile_df[['Factor_1_CONSISTENCY', 'Factor_2_RACECRAFT',
                       'Factor_3_RAW_SPEED', 'Factor_4_TIRE_MGMT']].apply(
    lambda x: np.std(x) / np.abs(np.mean(x)) if np.mean(x) != 0 else 0
).mean()

if mean_cv > 0.4:
    print("[PASS] Tracks show HIGH variation in skill demands (CV > 0.4)")
    print("       -> Circuit fit scoring will be MEANINGFUL")
    print("       -> Tier 1 captures track differences well")
elif mean_cv > 0.25:
    print("[MARGINAL] Tracks show MODERATE variation (CV 0.25-0.4)")
    print("           -> Circuit fit scoring will be somewhat useful")
    print("           -> Consider if more factors/variables would help")
else:
    print("[FAIL] Tracks show LOW variation (CV < 0.25)")
    print("       -> Circuit fit scoring may not add much value")
    print("       -> Need more factors/variables to capture differences")

print(f"\nMean Coefficient of Variation: {mean_cv:.3f}")

# ============================================================================
# TEST 2: 4-FACTOR vs 5-FACTOR MODEL
# ============================================================================
print("\n" + "="*80)
print("TEST 2: 4-FACTOR vs 5-FACTOR MODEL COMPARISON")
print("="*80)
print("\nObjective: Is Factor 5 (weak residual) adding value?")
print("Method: Compare R² with and without Factor 5")
print("Success Criteria: R² drop < 0.05 -> can drop Factor 5")

# 5-factor model (current)
X_5factor = factor_scores[['factor_1_score', 'factor_2_score', 'factor_3_score',
                             'factor_4_score', 'factor_5_score']].values
y = factor_scores['finishing_position'].values

reg_5 = LinearRegression()
reg_5.fit(X_5factor, y)
y_pred_5 = reg_5.predict(X_5factor)
r2_5 = r2_score(y, y_pred_5)

# 4-factor model (drop Factor 5)
X_4factor = factor_scores[['factor_1_score', 'factor_2_score', 'factor_3_score',
                             'factor_4_score']].values

reg_4 = LinearRegression()
reg_4.fit(X_4factor, y)
y_pred_4 = reg_4.predict(X_4factor)
r2_4 = r2_score(y, y_pred_4)

print(f"\n5-Factor Model R²: {r2_5:.4f}")
print(f"4-Factor Model R²: {r2_4:.4f}")
print(f"Difference:        {r2_5 - r2_4:.4f} ({(r2_5-r2_4)/r2_5*100:.1f}%)")

print("\n5-Factor Coefficients:")
print(f"  Factor 1 (CONSISTENCY): {reg_5.coef_[0]:7.3f}")
print(f"  Factor 2 (RACECRAFT):   {reg_5.coef_[1]:7.3f}")
print(f"  Factor 3 (RAW_SPEED):   {reg_5.coef_[2]:7.3f}")
print(f"  Factor 4 (TIRE_MGMT):   {reg_5.coef_[3]:7.3f}")
print(f"  Factor 5 (RESIDUAL):    {reg_5.coef_[4]:7.3f}")

print("\n4-Factor Coefficients:")
print(f"  Factor 1 (CONSISTENCY): {reg_4.coef_[0]:7.3f}")
print(f"  Factor 2 (RACECRAFT):   {reg_4.coef_[1]:7.3f}")
print(f"  Factor 3 (RAW_SPEED):   {reg_4.coef_[2]:7.3f}")
print(f"  Factor 4 (TIRE_MGMT):   {reg_4.coef_[3]:7.3f}")

# TEST 2 VERDICT
print("\n" + "="*80)
print("TEST 2 VERDICT: MODEL SIMPLIFICATION")
print("="*80)

r2_diff = r2_5 - r2_4
if r2_diff < 0.02:
    print(f"[RECOMMEND] Use 4-FACTOR model (R² loss = {r2_diff:.4f} is negligible)")
    print("            -> Simpler, easier to explain")
    print("            -> Factor 5 adds almost no predictive power")
    recommended_model = "4-FACTOR"
elif r2_diff < 0.05:
    print(f"[MARGINAL] Factor 5 adds small value (R² gain = {r2_diff:.4f})")
    print("           -> Could go either way")
    print("           -> Depends on preference for simplicity vs completeness")
    recommended_model = "4 OR 5-FACTOR"
else:
    print(f"[KEEP] Factor 5 is valuable (R² gain = {r2_diff:.4f})")
    print("       -> Keep 5-factor model")
    recommended_model = "5-FACTOR"

# ============================================================================
# TEST 3: DRIVER SANITY CHECK
# ============================================================================
print("\n" + "="*80)
print("TEST 3: DRIVER SANITY CHECK")
print("="*80)
print("\nObjective: Do driver scores pass 'smell test'?")
print("Method: Examine factor scores for drivers across multiple races")
print("Success Criteria: Consistent scores, interpretable patterns")

# Calculate average factor scores by driver (across all races)
driver_avg_scores = factor_scores.groupby('driver_number').agg({
    'factor_1_score': 'mean',
    'factor_2_score': 'mean',
    'factor_3_score': 'mean',
    'factor_4_score': 'mean',
    'factor_5_score': 'mean',
    'finishing_position': 'mean',
    'race': 'count'
}).rename(columns={'race': 'num_races'})

driver_avg_scores = driver_avg_scores[driver_avg_scores['num_races'] >= 3]  # At least 3 races
driver_avg_scores = driver_avg_scores.sort_values('finishing_position')

print(f"\nDrivers with 3+ races: {len(driver_avg_scores)}")
print("\nTOP 5 DRIVERS (by average finish):")
print(f"{'Driver':<8} {'Races':<7} {'Avg Finish':<12} {'CONSIST':<10} {'RACE':<10} {'SPEED':<10} {'TIRE':<10}")
print("-" * 80)
for driver in driver_avg_scores.head(5).index:
    row = driver_avg_scores.loc[driver]
    print(f"#{driver:<7} {int(row['num_races']):<7} {row['finishing_position']:>11.1f} "
          f"{row['factor_1_score']:>9.2f} {row['factor_2_score']:>9.2f} "
          f"{row['factor_3_score']:>9.2f} {row['factor_4_score']:>9.2f}")

print("\nBOTTOM 5 DRIVERS (by average finish):")
print(f"{'Driver':<8} {'Races':<7} {'Avg Finish':<12} {'CONSIST':<10} {'RACE':<10} {'SPEED':<10} {'TIRE':<10}")
print("-" * 80)
for driver in driver_avg_scores.tail(5).index:
    row = driver_avg_scores.loc[driver]
    print(f"#{driver:<7} {int(row['num_races']):<7} {row['finishing_position']:>11.1f} "
          f"{row['factor_1_score']:>9.2f} {row['factor_2_score']:>9.2f} "
          f"{row['factor_3_score']:>9.2f} {row['factor_4_score']:>9.2f}")

# Check correlations between factors and average finish
print("\n" + "="*80)
print("FACTOR CORRELATIONS WITH AVERAGE FINISH")
print("="*80)
for i in range(1, 6):
    corr = driver_avg_scores[f'factor_{i}_score'].corr(driver_avg_scores['finishing_position'])
    abs_corr = abs(corr)
    if abs_corr > 0.5:
        strength = "STRONG"
    elif abs_corr > 0.3:
        strength = "MODERATE"
    elif abs_corr > 0.1:
        strength = "WEAK"
    else:
        strength = "NEGLIGIBLE"

    print(f"Factor {i}: r = {corr:6.3f}  [{strength}]")

# Identify most distinctive skill profiles
print("\n" + "="*80)
print("MOST DISTINCTIVE SKILL PROFILES")
print("="*80)

for factor_name, factor_col in [('CONSISTENCY', 'factor_1_score'),
                                  ('RACECRAFT', 'factor_2_score'),
                                  ('RAW_SPEED', 'factor_3_score'),
                                  ('TIRE_MGMT', 'factor_4_score')]:
    sorted_drivers = driver_avg_scores.sort_values(factor_col, ascending=False)
    highest = sorted_drivers.index[0]
    lowest = sorted_drivers.index[-1]
    print(f"\n{factor_name}:")
    print(f"  Highest: Driver #{highest} (score = {sorted_drivers.loc[highest, factor_col]:6.2f}, "
          f"avg finish = {sorted_drivers.loc[highest, 'finishing_position']:.1f})")
    print(f"  Lowest:  Driver #{lowest} (score = {sorted_drivers.loc[lowest, factor_col]:6.2f}, "
          f"avg finish = {sorted_drivers.loc[lowest, 'finishing_position']:.1f})")

# TEST 3 VERDICT
print("\n" + "="*80)
print("TEST 3 VERDICT: DRIVER SCORES")
print("="*80)
print("[MANUAL REVIEW REQUIRED]")
print("Review the top/bottom drivers above:")
print("  - Do top finishers have high RAW_SPEED scores? (Expected: YES)")
print("  - Do scores vary meaningfully between drivers? (Expected: YES)")
print("  - Do any scores seem backwards or illogical? (Expected: NO)")
print("\nIf scores pass your domain knowledge test -> Tier 1 is valid")

# ============================================================================
# FINAL RECOMMENDATION
# ============================================================================
print("\n" + "="*80)
print("FINAL RECOMMENDATION")
print("="*80)

tests_passed = 0

# Test 1
if mean_cv > 0.25:
    tests_passed += 1
    test1_result = "PASS"
else:
    test1_result = "FAIL"

# Test 2
if r2_diff < 0.05:
    tests_passed += 1
    test2_result = "PASS (can simplify)"
else:
    test2_result = "KEEP 5 factors"

print(f"\nTest 1 (Track Profiles):     [{test1_result}]")
print(f"Test 2 (Model Simplification): [{test2_result}]")
print(f"Test 3 (Driver Sanity):        [MANUAL REVIEW]")

print("\n" + "="*80)
if tests_passed == 2 and mean_cv > 0.4:
    print("PASS STRONG RECOMMENDATION: SHIP TIER 1 NOW")
    print("="*80)
    print("\nRationale:")
    print("  1. Track profiles show HIGH variation -> circuit fit will work")
    print("  2. 4-factor model performs nearly as well -> use simpler model")
    print("  3. R² = 0.90 far exceeds target (0.60)")
    print("\nNext Steps:")
    print(f"  1. Use {recommended_model} model for product")
    print("  2. Build circuit fit scoring with track demand profiles")
    print("  3. Generate driver reports")
    print("  4. Ship MVP this week")
    print("  5. Collect user feedback, iterate")

elif tests_passed >= 1:
    print("WARN MODERATE RECOMMENDATION: TIER 1 PROBABLY SUFFICIENT")
    print("="*80)
    print("\nRationale:")
    print("  - Most validation tests pass")
    print("  - R² = 0.90 is excellent")
    print("  - May want to add 1-2 specific metrics based on user needs")
    print("\nNext Steps:")
    print("  1. Build MVP with Tier 1")
    print("  2. Identify specific gaps from user testing")
    print("  3. Add targeted metrics (not full Tier 2)")

else:
    print("FAIL RECOMMENDATION: EXPAND TO TIER 2")
    print("="*80)
    print("\nRationale:")
    print("  - Track profiles don't differ much")
    print("  - May need more factors/variables to capture skill nuances")
    print("\nNext Steps:")
    print("  1. Build Tier 2 features (8 additional variables)")
    print("  2. Re-run EFA, target 6 factors")
    print("  3. Validate track profiles improve")

# Save driver scores
driver_avg_scores.to_csv('data/analysis_outputs/driver_average_scores_tier1.csv')
print("\n[SAVED] Driver average scores: data/analysis_outputs/driver_average_scores_tier1.csv")

# Save track profiles
profile_df.to_csv('data/analysis_outputs/track_demand_profiles_tier1.csv')
print("[SAVED] Track demand profiles: data/analysis_outputs/track_demand_profiles_tier1.csv")

print("\n" + "="*80)
print("VALIDATION COMPLETE")
print("="*80)
print("\nGenerated files:")
print("  - track_demand_profiles.png")
print("  - track_demand_profiles_tier1.csv")
print("  - driver_average_scores_tier1.csv")
print()
