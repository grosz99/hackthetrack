# Final 4-Factor Driver Skill Model

**Model Performance**:
- R² = 0.895 (explains 89.5% of finishing position variance)
- Mean Absolute Error = 1.78 positions
- Cross-Validation R² = 0.877 (minimal overfitting)
- Leave-One-Race-Out R² = 0.867 (generalizes to new tracks)

**Based on**: 12 observable variables from 291 driver-race observations

---

## The 4 Factors

### Factor 1: **CONSISTENCY / PRECISION** (β = 3.792)
**Impact**: 2nd most important factor - contributes ~31% to overall score

**Variables** (loading > 0.4):
1. **braking_consistency** (-0.934) - DOMINANT LOADING!
   - Lap-to-lap consistency in braking zones (S1)
   - Measured by coefficient of variation
   - Higher consistency = better driver control

2. **sector_consistency** (-0.796)
   - Consistency across S1, S2, S3
   - Measures overall smoothness

3. **stint_consistency** (-0.469)
   - Lap time coefficient of variation
   - Excludes outliers (>107% of best)

4. **performance_normalized** (-0.504)
   - Normalized finishing position (0-1 scale)
   - Shows consistency leads to results

**Interpretation**: This factor captures drivers who have a "steady hand" - they brake at the same point lap after lap, maintain consistent sector times, and drive smoothly throughout the stint. Think of it as the difference between a metronome (high CONSISTENCY) vs a driver who's fast one lap, slow the next.

**Product Label**: "Precision" or "Consistency"

**Example High Scorer**: Driver with minimal lap-to-lap variation, smooth inputs

**Example Low Scorer**: Driver who's erratic, inconsistent braking points, variable pace

---

### Factor 2: **RACECRAFT / OVERTAKING** (β = 1.943)
**Impact**: 3rd most important - contributes ~16% to overall score

**Variables** (loading > 0.4):
1. **positions_gained** (-0.857) - DOMINANT LOADING!
   - Qualifying position - finishing position
   - Positive = gained positions
   - Measures ability to move forward through field

2. **position_changes** (-0.737)
   - Lap-by-lap position changes during race
   - Calculated from ELAPSED time rankings
   - Captures offensive racecraft

**Interpretation**: This factor captures drivers who can PASS. They start mid-pack and finish higher, make position changes throughout the race. This is "wheel-to-wheel" racing ability - the skill of overtaking under braking, positioning the car, and executing passes.

**Product Label**: "Racecraft" or "Overtaking"

**Example High Scorer**: Driver who qualifies 15th, finishes 8th, makes 20+ position changes

**Example Low Scorer**: Driver who qualifies 5th, finishes 5th, makes 2 position changes

**Note**: This factor is OFFENSIVE racecraft only. Defensive racecraft (holding position) is not currently captured.

---

### Factor 3: **RAW SPEED** (β = 6.079) - **DOMINANT FACTOR**
**Impact**: Most important factor - contributes ~50% to overall score!

**Variables** (loading > 0.4):
1. **best_race_lap** (-0.764)
   - Best lap time relative to field best
   - Single-lap pace on demand

2. **avg_top10_pace** (-0.710)
   - Average of best 10 laps
   - Sustained fast pace capability

3. **qualifying_pace** (-0.693)
   - Qualifying time relative to pole
   - Pure one-lap speed

4. **performance_normalized** (-0.692)
   - Finishing position (also loads here)
   - Shows speed = results

**Interpretation**: This factor captures OUTRIGHT CAR PACE. How fast can you lap? This is qualifying speed, best lap potential, and sustained top-10 lap pace. In spec racing (same cars), this is THE dominant predictor of results. If you're fast, you win. If you're slow, you're at the back.

**Product Label**: "Speed" or "Raw Pace"

**Example High Scorer**: Driver qualifies on pole, sets fastest lap, averages 0.5s faster than field

**Example Low Scorer**: Driver qualifies at back, best lap is 2s off pace, averages 1.5s slower

**Key Insight**: RAW SPEED has regression coefficient of 6.08 - meaning gaining 1 standard deviation in speed improves finish by ~6 positions! This is why it's 50% of the overall score.

---

### Factor 4: **TIRE MANAGEMENT / ENDURANCE** (β = 1.237)
**Impact**: Smallest factor - contributes ~10% to overall score

**Variables** (loading > 0.4):
1. **early_vs_late_pace** (0.622) - DOMINANT LOADING!
   - Ratio of early stint (laps 2-5) vs late stint (final 33%)
   - Lower ratio = pace drops off
   - Higher ratio = maintains pace

2. **late_stint_perf** (0.470)
   - Average lap time in final 33% of race
   - Relative to field best late pace
   - Measures tire preservation

**Interpretation**: This factor captures drivers who can PRESERVE TIRES and maintain pace over long runs. In races with high tire degradation (Sonoma, Sebring), this becomes more important. Some drivers "burn up" tires early and fade at the end. Others manage tires and maintain pace throughout.

**Product Label**: "Endurance" or "Tire Management"

**Example High Scorer**: Early laps 1:30.5, late laps 1:30.8 (only 0.3s dropoff)

**Example Low Scorer**: Early laps 1:30.5, late laps 1:32.5 (2.0s dropoff)

**Note**: POSITIVE loadings (unlike other factors). Higher score = better tire management = better late-race pace.

---

## Summary Table

| Factor | Name | Beta Coefficient | % Weight | Top Variables |
|--------|------|------------------|----------|---------------|
| **Factor 3** | RAW SPEED | 6.079 | 50% | qualifying_pace, best_race_lap, avg_top10_pace |
| **Factor 1** | CONSISTENCY | 3.792 | 31% | braking_consistency, sector_consistency |
| **Factor 2** | RACECRAFT | 1.943 | 16% | positions_gained, position_changes |
| **Factor 4** | TIRE MGMT | 1.237 | 10% | early_vs_late_pace, late_stint_perf |

**Total Beta Sum**: 12.051 (excludes intercept of 13.01)

---

## How Factors Predict Finishing Position

**The Equation**:
```
Predicted Finish = 13.01
                 + (3.792 × CONSISTENCY_score)
                 + (1.943 × RACECRAFT_score)
                 + (6.079 × RAW_SPEED_score)
                 + (1.237 × TIRE_MGMT_score)
```

**Factor Scores**: Z-scores (mean=0, std=1)
- Negative score = better than average
- Positive score = worse than average
- 0 = average

**Example - Driver #13 at Barber R1 (Winner)**:
```
Predicted Finish = 13.01
                 + (3.792 × -0.77) = -2.92  [Very consistent]
                 + (1.943 ×  0.05) = +0.10  [Average racecraft]
                 + (6.079 × -1.17) = -7.09  [VERY FAST!]
                 + (1.237 ×  0.08) = +0.10  [Average tire mgmt]
                 = 3.0 predicted finish

Actual: 1st place (error of +2.0 positions)
```

**Key Insight**: Driver #13's dominant RAW SPEED (-1.17 z-score) contributes -7.09 positions, nearly guaranteeing a front-running result!

---

## Variables NOT Used (Dropped Factor 5)

Factor 5 had eigenvalue of 1.002 (barely > 1.0) and no strong loadings (all < 0.4). Dropping it:
- Reduces R² by only 0.0055 (0.900 → 0.895)
- Simplifies model significantly
- Makes results easier to explain

Variables that loaded primarily on Factor 5:
- pace_degradation (loading = -0.12) - too weak
- None had loading > 0.4

---

## What's Missing from This Model?

1. **Defensive Racecraft** - Currently only measures offensive passing, not holding position
2. **Adaptability** - Cross-track consistency, learning rate
3. **Traffic Management** - Pace penalty when following cars
4. **Precision vs Over-driving** - Error rate, mistakes
5. **First Lap Performance** - Race start capability

**Recommendation**: Add these in v2.0 based on user feedback. Current 4-factor model is sufficient for MVP.

---

## Track-Specific Factor Importance (From Validation)

Some tracks value different skills:

**RAW SPEED is King Everywhere** (coef 3.93-7.08):
- Highest: Sebring R2 (7.08) - Pure speed track
- Lowest: VIR R2 (3.93) - But still most important!

**CONSISTENCY Varies Most** (coef 2.19-9.94):
- Highest: Road America R1 (9.94) - CRITICAL!
- Lowest: Road America R2 (2.19) - Interesting R1 vs R2 difference

**TIRE MANAGEMENT Track-Dependent** (coef -0.19 to 5.59):
- Highest: Road America R1 (5.59) - Long race, high degradation
- Lowest: VIR R1 (-0.19) - Negative! Tire mgmt doesn't help

**RACECRAFT Less Important** (coef -1.08 to 2.64):
- Highest: Sonoma R1 (2.64) - Passing opportunities
- Lowest: Road America R1 (-1.08) - Hard to pass, consistency > racecraft

---

## Data Source: 12 Variables

All calculated from existing race data:

**From Qualifying** (data/qualifying/):
- qualifying_pace

**From Best 10 Laps** (data/race_results/best_10_laps/):
- best_race_lap
- avg_top10_pace

**From Endurance Analysis** (data/race_results/analysis_endurance/):
- stint_consistency
- sector_consistency
- braking_consistency
- pace_degradation
- late_stint_perf
- early_vs_late_pace
- position_changes (calculated from ELAPSED times)

**From Provisional Results** (data/race_results/provisional_results/):
- positions_gained (qualifying vs finish)
- performance_normalized (normalized finish position)

---

## Product Implementation

### Overall Driver Score (0-100 scale)

**Method 1: Weighted Factor Average**
```python
overall_score = (
    0.50 * normalize(RAW_SPEED) +
    0.31 * normalize(CONSISTENCY) +
    0.16 * normalize(RACECRAFT) +
    0.10 * normalize(TIRE_MGMT)
) * 100
```

**Method 2: Predicted Finish → Score**
```python
# Lower predicted finish = higher score
predicted_finish = regression(factors)
max_possible_finish = 30  # Field size
overall_score = (max_possible_finish - predicted_finish) / max_possible_finish * 100
```

### Track-Specific Circuit Fit Score

```python
# Driver skill profile
driver = {
    'RAW_SPEED': 0.82,
    'CONSISTENCY': 1.15,
    'RACECRAFT': 0.45,
    'TIRE_MGMT': -0.23
}

# Track demand profile (from validation)
track = {
    'RAW_SPEED': 5.62,     # Road America R1
    'CONSISTENCY': 9.94,
    'RACECRAFT': -1.08,
    'TIRE_MGMT': 5.59
}

# Dot product
fit_score = sum(driver[f] * track[f] for f in factors)

# Normalize to 0-100
circuit_fit = normalize(fit_score, min=-20, max=20) * 100
```

### Driver Report Template

```
DRIVER #13 - OVERALL RATING: 95/100

SKILL BREAKDOWN:
  RAW SPEED:     98/100 ★★★★★ [ELITE]
  CONSISTENCY:   92/100 ★★★★☆ [STRONG]
  RACECRAFT:     75/100 ★★★☆☆ [AVERAGE]
  TIRE MGMT:     68/100 ★★★☆☆ [AVERAGE]

BEST TRACKS (Circuit Fit):
  1. Sebring     94/100 - Rewards pure speed
  2. COTA        91/100 - Speed + consistency
  3. Sonoma      88/100 - Speed + racecraft

WORST TRACKS:
  1. Road America R1  72/100 - Demands high tire mgmt (your weakness)
  2. VIR R1           78/100 - Requires balance you lack

RECOMMENDATIONS:
  • Focus on tire management practice (weak area)
  • Maintain elite speed (your strength)
  • Work on racecraft in traffic (average skill)
```

---

## Files Generated

1. **tier1_factor_loadings.csv** - Factor loading matrix
2. **tier1_factor_scores.csv** - Driver factor scores (291 observations)
3. **track_demand_profiles_tier1.csv** - Track-specific coefficients
4. **driver_average_scores_tier1.csv** - Driver averages across races
5. **tier1_scree_plot.png** - Eigenvalue plot
6. **tier1_loadings_heatmap.png** - Visual factor structure
7. **prediction_diagnostics.png** - Actual vs predicted plot

---

## Next Steps for Product

1. **Build scoring system** - Convert factor scores to 0-100 scale
2. **Build circuit fit algorithm** - Driver × track matching
3. **Generate driver reports** - Automated report generation
4. **API endpoints** - Integrate with product
5. **Deploy** - Ship MVP

**Timeline**: 3-5 days to product launch

---

**Model Status**: ✅ VALIDATED & READY FOR PRODUCTION
