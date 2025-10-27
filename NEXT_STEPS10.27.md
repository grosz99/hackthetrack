# Next Steps - Circuit Fit Analysis Project

**Last Updated**: 2025-10-26 (End of Session)
**Current Status**: ✅ TIER 1 COMPLETE - MAJOR SUCCESS!

---

## What We Accomplished Today

### 1. Fixed DNS (Did Not Start) Driver Handling
- **Issue**: Driver #15 (Road America R2) and Driver #78 (VIR R1/R2) had STATUS="Not started" with POSITION=NaN
- **Fix**: Added proper null checking before int() conversion in [build_features_tiered.py](build_features_tiered.py):530-538
- **Result**: 309 observations successfully processed (3 DNS drivers properly excluded)

### 2. Built Tier 1 Feature Matrix
- **Script**: [build_features_tiered.py](build_features_tiered.py)
- **Variables**: 12 highest confidence features
  - RAW SPEED: qualifying_pace, best_race_lap, avg_top10_pace
  - CONSISTENCY: stint_consistency, sector_consistency, braking_consistency
  - TIRE MANAGEMENT: pace_degradation, late_stint_perf, early_vs_late_pace
  - RACECRAFT: position_changes, positions_gained, performance_normalized
- **Output**: [data/analysis_outputs/all_races_tier1_features.csv](data/analysis_outputs/all_races_tier1_features.csv)
- **Data Quality**: 94.2% retention (291/309 observations), 95-100% completeness per variable

### 3. Ran Tier 1 Exploratory Factor Analysis
- **Script**: [run_tier1_efa.py](run_tier1_efa.py)
- **Result**: **R² = 0.900** (90% predictive accuracy!) - FAR EXCEEDS 60% target!
- **Factors Discovered**: 5 coherent skill dimensions
  1. CONSISTENCY/PRECISION (28.4% variance) - r=0.487
  2. RACECRAFT (18.6% variance) - r=0.245
  3. **RAW SPEED (13.6% variance) - r=0.759 DOMINANT!**
  4. TIRE MANAGEMENT (9.5% variance) - r=0.146
  5. RESIDUAL (8.3% variance) - r=-0.074 (weak)
- **Report**: [.claude/Analysis_Setup/TIER1_EFA_RESULTS.md](.claude/Analysis_Setup/TIER1_EFA_RESULTS.md)

### 4. Key Finding: RAW SPEED is King
- Factor 3 (RAW SPEED) has regression coefficient = 6.08
- Correlation with finish = 0.759 (very strong!)
- Gaining 1 std dev in speed improves finish by ~6 positions
- This validates the importance of qualifying pace + best lap metrics

---

## Tomorrow's Priority: Build Tier 2 Variables

### Step 1: Create `build_features_tier2.py`

Add 8 additional variables to the existing 12 (total = 20 variables):

#### RAW SPEED (+1 variable)
```python
def tier2_top_speed(endurance_df, driver_number):
    """Variable 4 from VARIABLE_DEF.md - Top Speed
    NOTE: Missing at Sebring & VIR (4 of 12 races)
    """
    if 'TOP_SPEED' not in endurance_df.columns or endurance_df['TOP_SPEED'].isna().all():
        return np.nan

    driver_data = endurance_df[endurance_df['NUMBER'] == driver_number]
    driver_top = driver_data['TOP_SPEED'].max()
    field_top = endurance_df['TOP_SPEED'].max()
    return driver_top / field_top
```

#### CONSISTENCY (+2 variables)
```python
def tier2_lap_to_lap_variation(endurance_df, driver_number):
    """Calculate coefficient of variation for consecutive lap time deltas"""
    driver_laps = endurance_df[endurance_df['NUMBER'] == driver_number].copy()
    driver_laps = driver_laps[driver_laps['IN_LAP'] == 0]  # Exclude pit laps

    lap_times = driver_laps['LAP_TIME'].apply(convert_to_seconds)
    lap_deltas = lap_times.diff().abs()

    # Remove outliers (>3 std dev)
    mean_delta = lap_deltas.mean()
    std_delta = lap_deltas.std()
    clean_deltas = lap_deltas[lap_deltas < mean_delta + 3*std_delta]

    driver_cv = clean_deltas.std() / clean_deltas.mean()

    # Compare to field best
    # ... (calculate field_cv similarly for all drivers)
    return field_cv / driver_cv  # Higher = better (less variation)

def tier2_sector_balance(endurance_df, driver_number):
    """Measure consistency across S1, S2, S3 relative to field"""
    driver_laps = endurance_df[endurance_df['NUMBER'] == driver_number]

    # Get driver's relative performance in each sector
    s1_rel = driver_laps['S1'].mean() / endurance_df['S1'].mean()
    s2_rel = driver_laps['S2'].mean() / endurance_df['S2'].mean()
    s3_rel = driver_laps['S3'].mean() / endurance_df['S3'].mean()

    # Lower std dev = more balanced across sectors
    balance = np.std([s1_rel, s2_rel, s3_rel])
    field_balance = # ... calculate for all drivers

    return field_balance / balance  # Higher = better (more balanced)
```

#### TIRE MANAGEMENT (+2 variables)
```python
def tier2_corner_speed_degradation(endurance_df, driver_number):
    """S2+S3 degradation slope (corners, not straights)"""
    driver_laps = endurance_df[endurance_df['NUMBER'] == driver_number].copy()
    driver_laps['corner_time'] = driver_laps['S2'] + driver_laps['S3']

    lap_numbers = driver_laps['LAP_NUMBER'].values
    corner_times = driver_laps['corner_time'].apply(convert_to_seconds).values

    slope, _, _, _, _ = linregress(lap_numbers, corner_times)

    # Lower slope = better corner speed maintenance
    field_best_slope = # ... calculate for all drivers
    return field_best_slope / slope

def tier2_stint_to_stint_consistency(endurance_df, driver_number):
    """If multiple stints, measure pace consistency across stints"""
    # Use IN_LAP and OUT_LAP to identify stint boundaries
    # Calculate avg pace per stint
    # Return CoV of stint average paces
    # (Implementation depends on pit stop data structure)
```

#### RACECRAFT (+3 variables)
```python
def tier2_first_lap_performance(endurance_df, driver_number):
    """Lap 1 vs Lap 2 pace (avoid first lap chaos penalty)"""
    driver_laps = endurance_df[endurance_df['NUMBER'] == driver_number]

    lap1_time = driver_laps[driver_laps['LAP_NUMBER'] == 1]['LAP_TIME'].iloc[0]
    lap2_time = driver_laps[driver_laps['LAP_NUMBER'] == 2]['LAP_TIME'].iloc[0]

    lap1_sec = convert_to_seconds(lap1_time)
    lap2_sec = convert_to_seconds(lap2_time)

    # Ratio - closer to 1.0 = good first lap
    ratio = lap2_sec / lap1_sec

    # Compare to field average ratio
    # ...
    return driver_ratio / field_ratio

def tier2_traffic_pace_penalty(endurance_df, driver_number):
    """Pace when gap < 2.0s vs gap > 3.0s (clean air)"""
    driver_laps = endurance_df[endurance_df['NUMBER'] == driver_number].copy()

    # Calculate gap to car ahead from ELAPSED times
    driver_laps['gap_ahead'] = # ... calculate from running positions

    traffic_laps = driver_laps[driver_laps['gap_ahead'] < 2.0]
    clean_laps = driver_laps[driver_laps['gap_ahead'] > 3.0]

    traffic_pace = traffic_laps['LAP_TIME'].mean()
    clean_pace = clean_laps['LAP_TIME'].mean()

    penalty = (traffic_pace - clean_pace) / clean_pace

    # Lower penalty = better in traffic
    field_penalty = # ... calculate for all drivers
    return field_penalty / penalty

def tier2_position_stability(endurance_df, driver_number):
    """DEFENSE metric - how often do you LOSE positions?
    (Opposite of position_changes which measures gaining)
    """
    # Calculate running positions from ELAPSED
    driver_laps = endurance_df[endurance_df['NUMBER'] == driver_number]
    driver_laps['running_position'] = # ... from ELAPSED rank

    position_changes = driver_laps['running_position'].diff()

    # Count laps where position got WORSE (positive change)
    laps_lost = (position_changes > 0).sum()
    total_laps = len(driver_laps)

    loss_rate = laps_lost / total_laps

    # Lower = better (stable positions)
    return 1.0 - loss_rate
```

### Step 2: Run Tier 2 EFA

```bash
# After building Tier 2 features
python build_features_tier2.py

# Update run_tier1_efa.py to run_tier2_efa.py
# - Change to 20 variables
# - Expect 5-6 factors
# - Target: KMO > 0.6, R² > 0.65
python run_tier2_efa.py
```

**Expected Outcomes**:
- KMO improves from 0.598 to 0.65+ (more variables = better sampling adequacy)
- R² maintains > 0.85 (may drop slightly but still excellent)
- Factor 2 (RACECRAFT) splits into OFFENSIVE and DEFENSIVE
- Factor 5 (RESIDUAL) either strengthens or gets absorbed

---

## Step 3: Build Tier 3 (Optional Enhancement Variables)

Add 6 more variables to reach 26 total:

#### PRECISION (New Factor?) (+2 variables)
- **Qualifying sector consistency** - S1/S2/S3 variance in qualifying
- **Error-free laps percentage** - % laps within 102% of best

#### ADAPTABILITY (New Factor?) (+2 variables)
- **Cross-track consistency** - StdDev of pace across different tracks
- **Learning rate** - Race 1 vs Race 2 improvement at same track

#### AGGRESSIVENESS (+2 variables)
- **Over-driving index** - Frequency of laps >105% of best (mistakes)
- **Edge management** - Laps between 98-100% of best (on the limit)

---

## Step 4: Build Track Demand Profiles

Once we have the final factor structure (5 or 6 factors from Tier 2/3):

```python
# track_demand_profiles.py

# For each track, run regression:
# Finish Position ~ Factor1 + Factor2 + ... + FactorN

# Example output:
SONOMA_PROFILE = {
    'RAW_SPEED': 5.2,      # High importance
    'CONSISTENCY': 3.8,
    'TIRE_MGMT': 4.5,      # Very important at Sonoma (tire wear track)
    'RACECRAFT': 1.2,      # Low importance (hard to pass)
    'DEFENSE': 2.3
}

ROAD_AMERICA_PROFILE = {
    'RAW_SPEED': 6.8,      # VERY high (high speed track)
    'CONSISTENCY': 2.1,
    'TIRE_MGMT': 1.5,      # Low (short race)
    'RACECRAFT': 3.2,
    'DEFENSE': 1.8
}
```

---

## Step 5: Build Circuit Fit Scoring System

```python
# circuit_fit_scoring.py

# Driver skill profile (from factor scores)
driver_profile = {
    'RAW_SPEED': 0.82,      # Z-score
    'CONSISTENCY': 1.15,
    'TIRE_MGMT': -0.23,
    'RACECRAFT': 0.45,
    'DEFENSE': 0.67
}

# Track demand profile (from Step 4)
track_profile = SONOMA_PROFILE

# Circuit fit score = weighted dot product
fit_score = sum(driver_profile[factor] * track_profile[factor] for factor in factors)

# Normalize to 0-100 scale
fit_score_100 = (fit_score - min_possible) / (max_possible - min_possible) * 100

# Output:
# Driver #13 at Sonoma: 87/100 Circuit Fit
#   - Strong CONSISTENCY (1.15) × High demand (3.8) = +4.37
#   - Strong RAW SPEED (0.82) × High demand (5.2) = +4.26
#   - Weak TIRE_MGMT (-0.23) × High demand (4.5) = -1.04
#   - NET: +7.59 → 87/100
```

---

## Files to Reference

### Core Data Files
- `data/analysis_outputs/all_races_tier1_features.csv` - Current feature matrix (12 vars)
- `data/analysis_outputs/tier1_factor_scores.csv` - Factor scores for 291 observations
- `data/analysis_outputs/tier1_factor_loadings.csv` - Factor structure

### Methodology Documents
- `.claude/Analysis_Setup/FIVE_STEP_IMPLEMENTATION_PLAN.md` - Overall roadmap
- `.claude/Analysis_Setup/FACTOR_THEMES_AND_FEATURES.md` - Variable ideas
- `.claude/Analysis_Setup/TIER1_EFA_RESULTS.md` - Today's results (READ THIS!)
- `.claude/Analysis_Setup/VARIABLE_DEF.md` - All 25 variable definitions
- `.claude/Analysis_Setup/circuit_fit_research_methodology.md` - EFA approach
- `.claude/Analysis_Setup/five_factor_racing_model.md` - Original hypothesis

### Code Files
- `build_features_tiered.py` - Tier 1 feature builder (working!)
- `run_tier1_efa.py` - EFA analysis script (working!)
- `test_metrics.py` - Validation testing (from earlier session)

---

## Quick Start for Tomorrow

### Option 1: Dive Straight into Tier 2
```bash
# 1. Copy build_features_tiered.py to build_features_tier2.py
# 2. Add 8 new functions (see above)
# 3. Run it
python build_features_tier2.py

# 4. Copy run_tier1_efa.py to run_tier2_efa.py
# 5. Update to 20 variables
# 6. Run it
python run_tier2_efa.py

# 7. Compare results to Tier 1
```

### Option 2: Review & Interpret Tier 1 First
```bash
# Look at the visualizations
start data/analysis_outputs/tier1_scree_plot.png
start data/analysis_outputs/tier1_loadings_heatmap.png

# Read the detailed results
# Open .claude/Analysis_Setup/TIER1_EFA_RESULTS.md

# Examine factor scores for specific drivers
python -c "
import pandas as pd
df = pd.read_csv('data/analysis_outputs/tier1_factor_scores.csv')
print(df[df['driver_number'] == 13])  # Your driver of interest
"
```

### Option 3: Build Track Demand Profiles with Tier 1
```bash
# Even with just 5 factors, we can start building track profiles
# This would validate the approach before expanding to Tier 2

# Create track_demand_profiles_tier1.py
# For each track, regress: Finish ~ Factor1 + ... + Factor5
# See which factors matter most at each track
```

---

## Open Questions to Consider

1. **Should we keep Factor 5 (RESIDUAL)?**
   - Eigenvalue = 1.002 (barely retained)
   - No strong loadings
   - r = -0.074 with finish (nearly zero)
   - **Option A**: Drop it, use 4-factor model
   - **Option B**: Keep it, see if Tier 2 strengthens it
   - **Recommendation**: Keep for Tier 2, then decide

2. **Should we split RACECRAFT into OFFENSIVE + DEFENSIVE?**
   - Current Factor 2 only has offensive metrics (positions gained, changes)
   - Need defensive metrics (position stability, gap management)
   - Tier 2 adds `position_stability` - this should help
   - **Recommendation**: Add defensive variables in Tier 2, let EFA decide if it splits

3. **How to handle missing TOP_SPEED data?**
   - Missing at Sebring & VIR (4 of 12 races)
   - **Option A**: Impute from straight line speed (S3 at some tracks)
   - **Option B**: Accept 67% completeness, include anyway
   - **Option C**: Skip it, RAW SPEED already well-measured
   - **Recommendation**: Option B - include but accept missingness

4. **When to build driver reports?**
   - Could build basic reports now with Tier 1 (5 factors)
   - Or wait for final model with Tier 2/3 (6 factors)
   - **Recommendation**: Wait for Tier 2, then build prototype report

---

## Background Processes (Check Tomorrow)

You have 2 background bash processes running:
1. `7def2a` - Running `01_discover_skills_eda.py`
2. `4879a0` - Running `test_metrics.py`

Check their output tomorrow:
```bash
# In the Claude Code interface, or:
# Check if still running and get output
```

These might have completed overnight - review output for any insights.

---

## Success Metrics

### Tier 2 Targets
- [ ] KMO > 0.60 (currently 0.598)
- [ ] R² > 0.85 (currently 0.900 - allow small drop)
- [ ] 5-6 interpretable factors
- [ ] DEFENSIVE RACECRAFT factor emerges
- [ ] All factor loadings interpretable (no "junk" factors)

### Tier 3 Targets (Optional)
- [ ] KMO > 0.65
- [ ] R² > 0.80
- [ ] 6 factors: SPEED, CONSISTENCY, TIRE MGMT, OFFENSE, DEFENSE, PRECISION
- [ ] Track demand profiles show meaningful differences
- [ ] Circuit fit scores correlate with actual results

---

## Celebrate Today's Win! 🏁

**R² = 0.900 with just 12 variables is EXCEPTIONAL!**

This validates:
- ✅ RepTrak methodology works for racing
- ✅ EFA discovers meaningful skill dimensions
- ✅ Factors predict race results (90% variance!)
- ✅ RAW SPEED is indeed the dominant factor in spec racing
- ✅ Our tiered approach (start simple, expand) was the right call

Tomorrow we make it even better with Tier 2!

---

**END OF SESSION - GOOD NIGHT!**
