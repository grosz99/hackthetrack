# Five-Step Implementation Plan: Circuit Fit Racing Model

**Date**: 2025-10-26
**Alignment**: Circuit Fit Research Methodology + Five Factor Racing Model + RepTrak Structure
**Goal**: Build validated 5-factor driver skill model with track-specific demand profiles

---

## Context Alignment

### What We Have:
1. ✅ **circuit_fit_research_methodology.md** - Cycling research-inspired EFA approach
2. ✅ **five_factor_racing_model.md** - Hypothesized 5 factors: FOCUS, SPRINTING, DEFENSE, ENDURANCE, AGGRESSIVENESS
3. ✅ **REPTRAK_MODEL_FOR_RACING.md** - RepTrak structure (7 dimensions → 23 attributes)
4. ✅ **METRICS_VALIDATION_REPORT.md** - 24/25 variables validated on 12 races
5. ✅ **VARIABLE_DEF.md** - 25 observable variables calculated from data

### What We Need to Build:
- **5-factor model** validated through Exploratory Factor Analysis
- **Track demand profiles** (which factors matter at each circuit)
- **Driver skill profiles** (individual factor scores)
- **Circuit Fit scoring** (driver × track matching)
- **Actionable diagnostics** (specific practice recommendations)

---

## 🎯 STEP 1: Calculate Observable Variables for EFA

**Goal**: Build feature matrix with 24 observable variables across all 12 races

### Actions:

#### 1.1: Fix Data Loading Issues
**File**: `build_feature_matrices.py`

**Fixes Needed**:
```python
# Issue: Column names have leading spaces
endurance.columns = endurance.columns.str.strip()

# Issue: Driver number mismatches (provisional vs best_10_laps)
# Use provisional drivers as base, handle NaN gracefully

# Issue: Qualifying POS data type
qual_position = int(qual_data['POS'].iloc[0])  # Cast to int
```

#### 1.2: Expand Variable Set
**Current**: 11 variables calculated
**Target**: 24 variables aligned with Five Factor Model

**Add these variables** (from five_factor_racing_model.md):

**FOCUS Variables** (4):
- ✅ stint_consistency (already have)
- Add: Sector time variance (S1, S2, S3 variance)
- Add: Braking point consistency
- Add: Throttle application consistency

**SPRINTING Variables** (5):
- ✅ qualifying_pace (already have)
- ✅ best_race_lap (already have)
- ✅ avg_top10_pace (already have)
- Add: Restart performance (first lap after FCY)
- Add: Peak corner speed achievement

**DEFENSE Variables** (4):
- ✅ position_changes (partially - need to split into offensive/defensive)
- Add: Defense success rate (position held when pressured)
- Add: Gap management under pressure
- Add: Overtake resistance time

**ENDURANCE Variables** (4):
- ✅ pace_degradation (already have)
- ✅ late_stint_perf (already have)
- Add: Consistency degradation (early vs late variance)
- Add: Late-race competitiveness percentile

**AGGRESSIVENESS Variables** (5):
- Add: Late braking index (from S1 performance)
- Add: Peak brake pressure (if telemetry available)
- Add: Entry speed differential
- Add: Peak lateral G (if telemetry available)
- Add: Trail braking skill

**Priority**: Focus on non-telemetry variables first (we have lap timing, qualifying, race results)

#### 1.3: Build Complete Feature Matrix
**Command**:
```bash
python build_feature_matrices.py
```

**Expected Output**:
- `data/analysis_outputs/all_races_features.csv`
- ~250-300 observations (12 races × 25 drivers avg)
- 24 feature columns + race + driver_number + finishing_position

**Success Criteria**:
- ✅ All 12 races processed successfully
- ✅ >80% data completeness per variable
- ✅ 220+ driver-track combinations (10 per variable minimum for EFA)

---

## 🔬 STEP 2: Run Exploratory Factor Analysis

**Goal**: Discover if the 5 hypothesized factors actually exist in the data

### Actions:

#### 2.1: Data Preparation
**File**: `run_factor_analysis.py`

```python
import pandas as pd
import numpy as np
from factor_analyzer import FactorAnalyzer, calculate_kmo, calculate_bartlett_sphericity
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

# Load feature matrix
features = pd.read_csv('data/analysis_outputs/all_races_features.csv')

# Separate features from metadata
feature_cols = [c for c in features.columns
                if c not in ['race', 'driver_number', 'finishing_position']]
X = features[feature_cols].copy()

# Handle missing data
# Strategy 1: Impute with column mean (simple)
X = X.fillna(X.mean())

# Strategy 2 (alternative): Drop variables with >20% missing
# completeness = X.notna().mean()
# X = X[completeness[completeness > 0.8].index]

# Standardize (mean=0, std=1)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
```

#### 2.2: Test Data Suitability for Factor Analysis
```python
# Bartlett's Test: Are variables correlated?
chi_square, p_value = calculate_bartlett_sphericity(X_scaled)
print(f"Bartlett's Test: χ²={chi_square:.2f}, p={p_value:.4f}")
# Need: p < 0.05 ✓

# KMO Test: Sampling adequacy
kmo_all, kmo_model = calculate_kmo(X_scaled)
print(f"KMO: {kmo_model:.3f}")
# Need: KMO > 0.6 (acceptable), > 0.8 (great)
```

**Success Criteria**:
- ✅ Bartlett's p < 0.05 (variables are correlated enough)
- ✅ KMO > 0.6 (sampling adequacy acceptable)

#### 2.3: Determine Number of Factors
```python
# Scree plot - visualize eigenvalues
fa_test = FactorAnalyzer(rotation=None, n_factors=X_scaled.shape[1])
fa_test.fit(X_scaled)

eigenvalues, _ = fa_test.get_eigenvalues()

plt.figure(figsize=(10, 6))
plt.plot(range(1, len(eigenvalues)+1), eigenvalues, 'bo-')
plt.axhline(y=1.0, color='r', linestyle='--', label='Eigenvalue = 1.0')
plt.xlabel('Factor Number')
plt.ylabel('Eigenvalue')
plt.title('Scree Plot - Determining Number of Factors')
plt.legend()
plt.grid(True)
plt.savefig('data/analysis_outputs/scree_plot.png')

# Kaiser criterion: Keep factors with eigenvalue > 1.0
n_factors = sum(eigenvalues > 1.0)
print(f"\nFactors with eigenvalue > 1.0: {n_factors}")
```

**Expected Result**: 5-7 factors (test your hypothesis!)

#### 2.4: Extract Factors with Rotation
```python
# Use oblique rotation (allows factors to correlate)
fa = FactorAnalyzer(n_factors=5, rotation='oblimin', method='minres')
fa.fit(X_scaled)

# Get factor loadings
loadings = pd.DataFrame(
    fa.loadings_,
    index=X.columns,
    columns=[f'Factor_{i+1}' for i in range(5)]
)

print("\nFactor Loadings:")
print(loadings.round(3))

# Save loadings
loadings.to_csv('data/analysis_outputs/factor_loadings.csv')
```

#### 2.5: Interpret Factors
```python
# Identify which variables load strongly on each factor
print("\n" + "="*80)
print("FACTOR INTERPRETATION")
print("="*80)

for factor in loadings.columns:
    print(f"\n{factor}:")
    # Show variables with loading > 0.5
    high_loadings = loadings[factor][abs(loadings[factor]) > 0.5].sort_values(ascending=False)

    if len(high_loadings) > 0:
        print("  High loadings (>0.5):")
        for var, loading in high_loadings.items():
            print(f"    {var:30s}: {loading:6.3f}")
    else:
        print("  No high loadings found")
```

**Manual Interpretation Step**:
- Look at which variables cluster together
- Name each factor based on the pattern
- Compare to hypothesized factors (FOCUS, SPRINTING, DEFENSE, ENDURANCE, AGGRESSIVENESS)

**Example**:
```
Factor_1 (Hypothesized: SPRINTING):
  qualifying_pace           : 0.856
  best_race_lap             : 0.782
  avg_top10_pace            : 0.741
→ Name: "RAW SPEED"

Factor_2 (Hypothesized: FOCUS):
  stint_consistency         : 0.824
  sector_variance           : 0.791
  braking_consistency       : 0.673
→ Name: "CONSISTENCY"
```

---

## ✅ STEP 3: Validate Factors Against Race Results

**Goal**: Prove that discovered factors actually predict winning

### Actions:

#### 3.1: Calculate Factor Scores
```python
# Transform data to factor scores
factor_scores = fa.transform(X_scaled)

# Add back to dataframe
factors_df = features[['race', 'driver_number', 'finishing_position']].copy()
for i in range(5):
    factors_df[f'Factor_{i+1}'] = factor_scores[:, i]

factors_df.to_csv('data/analysis_outputs/driver_factor_scores.csv', index=False)
```

#### 3.2: Test Factor-Result Correlations
```python
from scipy.stats import pearsonr

print("\n" + "="*80)
print("FACTOR VALIDATION - Correlation with Finishing Position")
print("="*80)

results = []

for i in range(5):
    factor_col = f'Factor_{i+1}'

    # Correlation with finishing position
    # Note: Lower position = better (1st place = 1)
    # So negative correlation = factor helps winning
    r, p_value = pearsonr(factors_df[factor_col], factors_df['finishing_position'])

    results.append({
        'Factor': factor_col,
        'Correlation': r,
        'P_Value': p_value,
        'Significant': 'YES' if p_value < 0.05 else 'NO'
    })

    print(f"\n{factor_col}:")
    print(f"  Correlation with finish: r = {r:.3f}")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Significant: {'✓' if p_value < 0.05 else '✗'}")

results_df = pd.DataFrame(results)
results_df.to_csv('data/analysis_outputs/factor_validation.csv', index=False)
```

**Success Criteria**:
- ✅ At least 3/5 factors with p < 0.05 (statistically significant)
- ✅ Negative correlations (better factor score → lower/better finishing position)

#### 3.3: Combined Predictive Power
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Multiple regression: Finishing Position ~ Factor1 + Factor2 + ... + Factor5
X_factors = factors_df[[f'Factor_{i+1}' for i in range(5)]]
y = factors_df['finishing_position']

model = LinearRegression()
model.fit(X_factors, y)

# R² - how much variance do factors explain?
r_squared = model.score(X_factors, y)

print(f"\n{'='*80}")
print(f"COMBINED MODEL VALIDATION")
print(f"{'='*80}")
print(f"R² = {r_squared:.3f}")
print(f"Factors explain {r_squared*100:.1f}% of variance in finishing position")
print(f"\nTarget: R² > 0.60 (60%)")
print(f"Result: {'✓ SUCCESS' if r_squared > 0.6 else '✗ Below target'}")

# Individual factor coefficients
print(f"\nFactor Coefficients (importance):")
for i, coef in enumerate(model.coef_):
    print(f"  Factor_{i+1}: {coef:7.3f}")
```

**Success Criteria**:
- ✅ R² > 0.60 (factors explain >60% of results)

---

## 📊 STEP 4: Create Track Demand Profiles

**Goal**: Identify which factors matter most at each track

### Actions:

#### 4.1: Track-Specific Regressions
```python
tracks = factors_df['race'].str.split('_').str[0].unique()

track_profiles = {}

print(f"\n{'='*80}")
print(f"TRACK DEMAND PROFILES")
print(f"{'='*80}")

for track in tracks:
    # Filter to this track's races
    track_data = factors_df[factors_df['race'].str.contains(track)]

    X_track = track_data[[f'Factor_{i+1}' for i in range(5)]]
    y_track = track_data['finishing_position']

    # Fit model
    model_track = LinearRegression()
    model_track.fit(X_track, y_track)

    # Store coefficients (absolute value = importance)
    track_profiles[track] = {}
    for i, coef in enumerate(model_track.coef_):
        track_profiles[track][f'Factor_{i+1}'] = abs(coef)

    # Normalize to percentages
    total = sum(track_profiles[track].values())
    for factor in track_profiles[track]:
        track_profiles[track][factor] = (track_profiles[track][factor] / total) * 100

    # Display
    print(f"\n{track.upper()}:")
    print(f"  R² = {model_track.score(X_track, y_track):.3f}")
    print(f"  Factor importance:")
    for factor, importance in sorted(track_profiles[track].items(),
                                     key=lambda x: x[1], reverse=True):
        print(f"    {factor}: {importance:5.1f}%")

# Save profiles
profiles_df = pd.DataFrame(track_profiles).T
profiles_df.to_csv('data/analysis_outputs/track_demand_profiles.csv')
```

**Expected Output**:
```
BARBER (technical):
  Factor_1 (Speed):        20%
  Factor_2 (Consistency):  25%
  Factor_3 (Racecraft):    15%
  Factor_4 (Endurance):    10%
  Factor_5 (Aggression):   30% ← Highest

COTA (high-speed):
  Factor_1 (Speed):        35% ← Highest
  Factor_2 (Consistency):  20%
  Factor_3 (Racecraft):    10%
  Factor_4 (Endurance):    20%
  Factor_5 (Aggression):   15%
```

---

## 🎯 STEP 5: Build Circuit Fit Scoring System

**Goal**: Match drivers to tracks and generate actionable recommendations

### Actions:

#### 5.1: Calculate Driver Skill Profiles
```python
# For each driver, average their factor scores across all races
driver_profiles = factors_df.groupby('driver_number').agg({
    'Factor_1': 'mean',
    'Factor_2': 'mean',
    'Factor_3': 'mean',
    'Factor_4': 'mean',
    'Factor_5': 'mean',
    'finishing_position': 'mean'
}).round(3)

driver_profiles.to_csv('data/analysis_outputs/driver_skill_profiles.csv')

print(f"\n{'='*80}")
print(f"TOP 5 DRIVERS BY AVERAGE FINISH")
print(f"{'='*80}")

top_drivers = driver_profiles.sort_values('finishing_position').head(5)
print(top_drivers)
```

#### 5.2: Calculate Circuit Fit Scores
```python
def calculate_circuit_fit(driver_number, track_name, driver_profiles, track_profiles):
    """
    Calculate how well a driver's skills match a track's demands.

    Fit Score = Σ (track_demand_i × driver_ability_i)
    """
    driver_skills = driver_profiles.loc[driver_number]
    track_demands = track_profiles.loc[track_name]

    fit_score = 0
    breakdown = {}

    for i in range(1, 6):
        factor = f'Factor_{i}'

        # Track demand (as decimal, e.g., 0.35 for 35%)
        demand = track_demands[factor] / 100

        # Driver ability (z-score normalized)
        ability = driver_skills[factor]

        # Contribution to fit
        contribution = demand * ability
        fit_score += contribution

        breakdown[factor] = {
            'demand': track_demands[factor],
            'ability': ability,
            'contribution': contribution
        }

    return fit_score, breakdown

# Example: Calculate fit for all drivers at Barber
track = 'barber'
fit_scores = []

for driver in driver_profiles.index:
    fit, breakdown = calculate_circuit_fit(driver, track, driver_profiles, profiles_df)
    fit_scores.append({
        'driver': driver,
        'track': track,
        'fit_score': fit,
        **{f'{k}_ability': v['ability'] for k, v in breakdown.items()},
        **{f'{k}_contribution': v['contribution'] for k, v in breakdown.items()}
    })

fit_df = pd.DataFrame(fit_scores).sort_values('fit_score', ascending=False)
fit_df.to_csv(f'data/analysis_outputs/{track}_circuit_fit_scores.csv', index=False)

print(f"\nTop 5 Best Fit Drivers for {track.upper()}:")
print(fit_df[['driver', 'fit_score']].head(10))
```

#### 5.3: Generate Actionable Diagnostics
```python
def generate_driver_report(driver_number, track_name,
                          driver_profiles, track_profiles, factors_df):
    """
    Generate Circuit Fit report with actionable recommendations.
    """
    driver = driver_profiles.loc[driver_number]
    track = track_profiles.loc[track_name]

    fit_score, breakdown = calculate_circuit_fit(
        driver_number, track_name, driver_profiles, track_profiles
    )

    # Percentile rank for each factor
    percentiles = {}
    for i in range(1, 6):
        factor = f'Factor_{i}'
        percentiles[factor] = (driver[factor] > driver_profiles[factor]).mean() * 100

    print(f"\n{'='*80}")
    print(f"CIRCUIT FIT REPORT")
    print(f"{'='*80}")
    print(f"Driver: #{driver_number}")
    print(f"Track: {track_name.upper()}")
    print(f"Circuit Fit Score: {fit_score:.3f}")
    print(f"")

    print(f"TRACK DEMANDS:")
    for i in range(1, 6):
        factor = f'Factor_{i}'
        print(f"  {factor}: {track[factor]:5.1f}%")

    print(f"\nYOUR STRENGTHS:")
    # Show factors where driver is >70th percentile
    for i in range(1, 6):
        factor = f'Factor_{i}'
        if percentiles[factor] > 70:
            print(f"  ✓ {factor}: {percentiles[factor]:.0f}th percentile")

    print(f"\nFOCUS AREAS FOR {track_name.upper()}:")
    # Show factors where track demand is high (>25%) but driver is weak (<50th percentile)
    for i in range(1, 6):
        factor = f'Factor_{i}'
        demand = track[factor]
        ability_percentile = percentiles[factor]

        if demand > 25 and ability_percentile < 50:
            print(f"  ⚠ {factor}:")
            print(f"     Track demand: {demand:.0f}% (HIGH)")
            print(f"     Your level: {ability_percentile:.0f}th percentile")
            print(f"     → Priority practice area")

    # Historical performance at this track
    driver_at_track = factors_df[
        (factors_df['driver_number'] == driver_number) &
        (factors_df['race'].str.contains(track_name))
    ]

    if len(driver_at_track) > 0:
        print(f"\nHISTORICAL PERFORMANCE AT {track_name.upper()}:")
        print(f"  Races: {len(driver_at_track)}")
        print(f"  Average finish: P{driver_at_track['finishing_position'].mean():.1f}")
        print(f"  Best finish: P{driver_at_track['finishing_position'].min():.0f}")

# Example: Generate report for top driver at Barber
top_driver_num = fit_df.iloc[0]['driver']
generate_driver_report(top_driver_num, 'barber', driver_profiles, profiles_df, factors_df)
```

**Expected Output**:
```
================================================================================
CIRCUIT FIT REPORT
================================================================================
Driver: #13
Track: BARBER
Circuit Fit Score: 0.847

TRACK DEMANDS:
  Factor_1: 20.0%
  Factor_2: 25.0%
  Factor_3: 15.0%
  Factor_4: 10.0%
  Factor_5: 30.0%

YOUR STRENGTHS:
  ✓ Factor_1: 95th percentile
  ✓ Factor_2: 88th percentile
  ✓ Factor_5: 82nd percentile

FOCUS AREAS FOR BARBER:
  ⚠ Factor_3:
     Track demand: 15% (MODERATE)
     Your level: 45th percentile
     → Opportunity area

HISTORICAL PERFORMANCE AT BARBER:
  Races: 2
  Average finish: P1.0
  Best finish: P1
```

---

## 📦 Deliverables

### Code Files:
1. ✅ `build_feature_matrices.py` (fixed and expanded)
2. ✅ `run_factor_analysis.py` (Steps 2-3)
3. ✅ `track_demand_profiles.py` (Step 4)
4. ✅ `circuit_fit_scoring.py` (Step 5)
5. ✅ `generate_driver_reports.py` (Final product)

### Data Outputs:
1. `data/analysis_outputs/all_races_features.csv` - Feature matrix
2. `data/analysis_outputs/scree_plot.png` - Factor count visualization
3. `data/analysis_outputs/factor_loadings.csv` - Variable → Factor mapping
4. `data/analysis_outputs/driver_factor_scores.csv` - Individual scores
5. `data/analysis_outputs/factor_validation.csv` - Statistical validation
6. `data/analysis_outputs/track_demand_profiles.csv` - Track requirements
7. `data/analysis_outputs/driver_skill_profiles.csv` - Driver strengths
8. `data/analysis_outputs/{track}_circuit_fit_scores.csv` - Match scores

### Documentation:
1. `FACTOR_ANALYSIS_RESULTS.md` - Discovered factors and interpretation
2. `TRACK_PROFILES_GUIDE.md` - Track-by-track demands
3. `USER_GUIDE.md` - How to use Circuit Fit system

---

## 🎯 Success Metrics

### Statistical Validation:
- ✅ Bartlett's Test: p < 0.05
- ✅ KMO: > 0.6 (acceptable) or > 0.8 (great)
- ✅ 5 factors with eigenvalue > 1.0
- ✅ Cumulative variance > 70%
- ✅ 3+ factors with p < 0.05 correlation to results
- ✅ Combined R² > 0.60

### Product Validation:
- ✅ Factors are interpretable (can explain to drivers)
- ✅ Track profiles make racing sense
- ✅ Circuit Fit scores predict actual results
- ✅ Recommendations are specific and actionable

---

## ⏱️ Estimated Timeline

**Step 1**: 2-3 hours (fix and expand feature calculations)
**Step 2**: 1-2 hours (run EFA and interpret factors)
**Step 3**: 1 hour (validate against results)
**Step 4**: 1 hour (build track profiles)
**Step 5**: 2-3 hours (build scoring system and reports)

**Total**: 7-10 hours of development

---

## 🚀 Next Actions

1. **Fix `build_feature_matrices.py`** with data loading corrections
2. **Run Step 1** to generate complete feature matrix
3. **Create `run_factor_analysis.py`** and execute Steps 2-3
4. **Interpret discovered factors** - name them based on loadings
5. **Build track demand profiles** (Step 4)
6. **Create Circuit Fit scoring tool** (Step 5)
7. **Generate sample driver reports** to validate actionability

**Ready to start?** Let's begin with fixing the feature matrix builder!
