# Five Factor Racing Model - Data Dictionary Mapping

## THE 5 FACTORS (Your Hypothesis)

1. **FOCUS** - Consistency at high pace
2. **SPRINTING** - Fast laps when needed (race-winning moments)
3. **DEFENSE** - Holding off competitors in battles
4. **ENDURANCE** - Maintaining pace as race progresses
5. **AGGRESSIVENESS** - Driving harder into corners than others

---

## FACTOR 1: FOCUS (Consistency at High Pace)

### Definition
The ability to maintain consistent lap times while running at competitive pace. Not just being consistent slowly - being consistent FAST.

### Observable Variables (4-5 metrics)

#### **F1.1: Competitive Pace Consistency**
**Formula:** `StdDev(lap times) for laps within 0.5s of race winner's pace`
**Data Required:**
- `lap` (from lap timing data)
- `laptrigger_laptime_dur` (lap time duration)
- Race winner's average pace (calculate from race results)
**Calculation:**
```python
# Filter to competitive laps only
competitive_laps = laps[laps['laptrigger_laptime_dur'] <= winner_avg + 0.5]
focus_score_1 = competitive_laps['laptrigger_laptime_dur'].std()
# Lower = better focus
```

#### **F1.2: Sector Time Variance (Clean Laps)**
**Formula:** `Average StdDev across all 3 sectors on clean laps`
**Data Required:**
- Sector times from analysis endurance data
- Traffic detection (laps >3s clear of other cars)
**Calculation:**
```python
clean_laps = identify_clean_laps(gap_to_car_ahead > 3.0)
sector_variances = []
for sector in [1, 2, 3]:
    sector_variances.append(clean_laps[f'sector_{sector}_time'].std())
focus_score_2 = np.mean(sector_variances)
# Lower = better focus
```

#### **F1.3: Throttle Application Consistency**
**Formula:** `StdDev of throttle_can values at same GPS coordinate across laps`
**Data Required:**
- `throttle_can` (telemetry)
- `ecu_gpslatitude` + `ecu_gpslongitude` (telemetry)
**Calculation:**
```python
# For each GPS point on track (binned)
for gps_point in track_reference_line:
    throttle_at_point = []
    for lap in laps:
        throttle_val = get_telemetry_at_gps(lap, gps_point, 'throttle_can')
        throttle_at_point.append(throttle_val)
    consistency_at_point = np.std(throttle_at_point)

focus_score_3 = np.mean(consistency_at_all_points)
# Lower = more focused/consistent
```

#### **F1.4: Braking Point Consistency**
**Formula:** `StdDev of brake application points (distance to corner) across laps`
**Data Required:**
- `brake_can` (telemetry)
- `Laptrigger_lapdist_dls` (distance along track)
- Corner locations (derived from speed drops)
**Calculation:**
```python
# For each major corner
for corner in major_corners:
    brake_points = []
    for lap in laps:
        # Find where brake_can > 10% before corner
        brake_distance = find_brake_application_point(lap, corner)
        brake_points.append(brake_distance)
    
    corner_consistency = np.std(brake_points)

focus_score_4 = np.mean(consistency_across_corners)
# Lower = better focus
```

### Hypothesis: FOCUS → Race Results
**H1:** Higher FOCUS (lower variance scores) should correlate POSITIVELY with better finishing positions.
- **Expected Pearson r:** 0.4 to 0.6 (moderate to strong)
- **Why:** Consistent drivers make fewer mistakes, especially important in spec racing where speed is equal

---

## FACTOR 2: SPRINTING (Fast Laps on Demand)

### Definition
The ability to deliver fast laps at critical race moments - qualifying, restarts, overtaking attempts, defensive laps.

### Observable Variables (4-5 metrics)

#### **S2.1: Qualifying Pace Percentile**
**Formula:** `Driver's Q time rank / Total drivers × 100`
**Data Required:**
- Qualifying results
- Total field size
**Calculation:**
```python
qual_time = get_qualifying_time(driver, race)
field = get_all_qualifying_times(race)
sprinting_score_1 = percentile_rank(qual_time, field)
# Higher = better sprinter
```

#### **S2.2: Best 3 Laps Average (Relative)**
**Formula:** `Average of best 3 race laps vs. race winner's best 3 average`
**Data Required:**
- All lap times for driver
- Race winner's best laps
**Calculation:**
```python
driver_best_3 = sorted(driver_laps)[:3].mean()
winner_best_3 = sorted(winner_laps)[:3].mean()
sprinting_score_2 = (winner_best_3 - driver_best_3) / winner_best_3
# Higher = better sprinter (smaller gap to winner)
```

#### **S2.3: Restart Performance**
**Formula:** `Average lap time on first lap after safety car vs. field average`
**Data Required:**
- Lap times
- Safety car periods (from race notes or gap analysis)
**Calculation:**
```python
restart_laps = identify_restart_laps(race)
driver_restart_avg = driver_laps[restart_laps].mean()
field_restart_avg = all_drivers_laps[restart_laps].mean()
sprinting_score_3 = (field_restart_avg - driver_restart_avg) / field_restart_avg
# Higher = better sprinter (faster than field on restarts)
```

#### **S2.4: Overtake Attempt Speed**
**Formula:** `Average speed differential when closing to <0.5s behind another car`
**Data Required:**
- Gap to car ahead (calculate from lap times + positions)
- Speed when gap is closing
**Calculation:**
```python
overtake_attempts = identify_closing_gaps(gap_ahead)
for attempt in overtake_attempts:
    # Speed differential during approach
    speed_diff = driver_speed - ahead_car_speed
    
sprinting_score_4 = np.mean(speed_diff_during_attempts)
# Higher = more aggressive sprint speed in battles
```

#### **S2.5: Peak Corner Speed Achievement**
**Formula:** `% of corners where driver achieves top-3 minimum corner speed vs. field`
**Data Required:**
- Minimum corner speed for each corner, each lap
- All drivers' corner speeds for comparison
**Calculation:**
```python
for corner in corners:
    field_corner_speeds = get_all_drivers_min_speed(corner)
    top_3_threshold = np.percentile(field_corner_speeds, 85)
    
    driver_corner_speed = driver_min_speed(corner)
    if driver_corner_speed >= top_3_threshold:
        peak_corners += 1

sprinting_score_5 = peak_corners / total_corners
# Higher = better ability to hit peak speeds when needed
```

### Hypothesis: SPRINTING → Race Results
**H2:** Higher SPRINTING should correlate POSITIVELY with better finishing positions.
- **Expected Pearson r:** 0.5 to 0.7 (strong)
- **Why:** Qualifying position and ability to overtake are critical in short races

---

## FACTOR 3: DEFENSE (Holding Off Competitors)

### Definition
The ability to maintain position when being pressured by a faster car behind, including defensive driving lines and preventing overtakes.

### Observable Variables (4-5 metrics)

#### **D3.1: Defense Success Rate**
**Formula:** `Laps with car within 1.0s behind where position held / Total laps under pressure`
**Data Required:**
- Lap-by-lap positions
- Gap to car behind (calculate from lap times)
**Calculation:**
```python
defensive_situations = laps_where(gap_to_behind < 1.0)
positions_held = count(position[lap] == position[lap+1])
defense_score_1 = positions_held / len(defensive_situations)
# Higher = better defender
```

#### **D3.2: Defensive Line Usage**
**Formula:** `% of corners where driver takes inside/defensive line when car is within 1.5s behind`
**Data Required:**
- GPS racing line vs. defensive line (calculated)
- Gap to car behind
**Calculation:**
```python
# When under pressure
pressure_corners = corners_where(gap_behind < 1.5)

for corner in pressure_corners:
    racing_line = optimal_racing_line[corner]
    driver_line = driver_gps_line[corner]
    
    # Is driver on inside (defensive) line?
    if is_defensive_line(driver_line, racing_line):
        defensive_count += 1

defense_score_2 = defensive_count / len(pressure_corners)
# Higher = more defensive awareness
```

#### **D3.3: Gap Management Under Pressure**
**Formula:** `Average gap maintained to car behind during defensive situations`
**Data Required:**
- Gap to car behind across laps
**Calculation:**
```python
defensive_laps = laps_where(gap_behind < 2.0)
gaps_maintained = []

for lap in defensive_laps:
    gap_behind = calculate_gap(lap)
    gaps_maintained.append(gap_behind)

defense_score_3 = np.mean(gaps_maintained)
# Higher gap = better defense (kept them further back)
```

#### **D3.4: Overtake Resistance Time**
**Formula:** `Average laps car stays behind before overtaking vs. field average`
**Data Required:**
- Position changes
- Laps under pressure
**Calculation:**
```python
overtake_events = identify_position_losses(driver)

for event in overtake_events:
    laps_under_pressure = count_laps_with_gap_behind_less_than(1.0, before_overtake)
    resistance_times.append(laps_under_pressure)

defense_score_4 = np.mean(resistance_times)
# Higher = holds position longer under pressure
```

### Hypothesis: DEFENSE → Race Results
**H3:** Higher DEFENSE should correlate POSITIVELY with better finishing positions.
- **Expected Pearson r:** 0.3 to 0.5 (moderate)
- **Why:** Important for protecting positions but less predictive than speed/sprinting
- **Context-dependent:** More important at tracks where overtaking is common

---

## FACTOR 4: ENDURANCE (Maintaining Pace Over Race Distance)

### Definition
The ability to maintain competitive pace in the later stages of the race, avoiding tire degradation and maintaining concentration.

### Observable Variables (4-5 metrics)

#### **E4.1: Pace Degradation Rate**
**Formula:** `Slope of lap time vs. lap number (clean laps only)`
**Data Required:**
- Lap times across race
- Clean lap identification
**Calculation:**
```python
clean_laps = identify_clean_laps(gap_ahead > 3.0, gap_behind > 3.0)
lap_numbers = clean_laps['lap']
lap_times = clean_laps['laptrigger_laptime_dur']

# Linear regression
slope, intercept = linear_regression(lap_numbers, lap_times)
endurance_score_1 = -slope  # Negative slope = getting slower
# Higher negative value = worse endurance
# Convert to positive: endurance_score_1 = -slope (so positive = better)
```

#### **E4.2: Early vs. Late Race Pace**
**Formula:** `(Avg lap time laps 1-5) / (Avg lap time laps 15-20)`
**Data Required:**
- Lap times for early and late race
**Calculation:**
```python
early_laps = laps[1:6]
late_laps = laps[15:21]

early_avg = early_laps['laptrigger_laptime_dur'].mean()
late_avg = late_laps['laptrigger_laptime_dur'].mean()

endurance_score_2 = early_avg / late_avg
# Value > 1.0 = slowing down (bad endurance)
# Value close to 1.0 = maintaining pace (good endurance)
# Convert: endurance_score_2 = 1 / ratio (so higher = better)
```

#### **E4.3: Late-Race Competitiveness**
**Formula:** `Percentile rank of pace in final 5 laps vs. field`
**Data Required:**
- All drivers' lap times in laps 15-20
**Calculation:**
```python
final_laps = laps[15:21]
driver_final_avg = driver_laps[final_laps].mean()

# Compare to field
field_final_avgs = []
for other_driver in field:
    field_final_avgs.append(other_driver_laps[final_laps].mean())

endurance_score_3 = percentile_rank(driver_final_avg, field_final_avgs)
# Higher = better late-race pace relative to field
```

#### **E4.4: Consistency Degradation**
**Formula:** `StdDev(laps 15-20) / StdDev(laps 1-5)`
**Data Required:**
- Lap time variance early vs. late
**Calculation:**
```python
early_laps_std = laps[1:6]['laptrigger_laptime_dur'].std()
late_laps_std = laps[15:21]['laptrigger_laptime_dur'].std()

endurance_score_4 = early_laps_std / late_laps_std
# Value < 1.0 = getting less consistent (bad endurance)
# Value > 1.0 = maintaining or improving consistency
```

### Hypothesis: ENDURANCE → Race Results
**H4:** Higher ENDURANCE should correlate POSITIVELY with better finishing positions.
- **Expected Pearson r:** 0.3 to 0.5 (moderate)
- **Why:** Important in longer races, less critical in short sprints
- **Context-dependent:** More important in hot weather races or longer race formats

---

## FACTOR 5: AGGRESSIVENESS (Driving Harder Into Corners)

### Definition
The willingness to take more risk by braking later, carrying more speed into corners, and driving at the edge of grip.

### Observable Variables (4-5 metrics)

#### **A5.1: Late Braking Index**
**Formula:** `Average brake application point vs. field average (closer to corner = later)`
**Data Required:**
- `brake_can` telemetry
- `Laptrigger_lapdist_dls` (distance)
- Corner entry points
**Calculation:**
```python
for corner in major_corners:
    driver_brake_point = calculate_brake_distance_from_corner(driver, corner)
    field_avg_brake_point = calculate_field_avg(corner)
    
    # Distance difference (negative = braking later)
    brake_delta = driver_brake_point - field_avg_brake_point

aggressiveness_score_1 = -np.mean(brake_deltas)
# Positive value = braking later than field average (more aggressive)
```

#### **A5.2: Peak Brake Pressure**
**Formula:** `Average maximum brake_can value in braking zones vs. field`
**Data Required:**
- `brake_can` telemetry for all braking zones
**Calculation:**
```python
for braking_zone in braking_zones:
    driver_max_brake = max(driver_brake_telemetry[braking_zone])
    field_avg_max_brake = mean(field_max_brakes[braking_zone])
    
    pressure_ratio = driver_max_brake / field_avg_max_brake

aggressiveness_score_2 = np.mean(pressure_ratios)
# Higher = more aggressive braking
```

#### **A5.3: Entry Speed Differential**
**Formula:** `Corner entry speed vs. field average (higher = more aggressive)`
**Data Required:**
- `speed` at corner entry point (defined location before apex)
**Calculation:**
```python
for corner in corners:
    entry_point = define_entry_location(corner)  # e.g., 50m before apex
    
    driver_entry_speed = get_speed_at_point(driver, entry_point)
    field_avg_entry_speed = get_field_avg_speed(entry_point)
    
    speed_delta = driver_entry_speed - field_avg_entry_speed

aggressiveness_score_3 = np.mean(speed_deltas)
# Positive = entering faster (more aggressive)
```

#### **A5.4: Peak Lateral G-Force**
**Formula:** `Average maximum lateral G vs. field in corners`
**Data Required:**
- `accy_can` (lateral acceleration in corners)
**Calculation:**
```python
for corner in corners:
    driver_max_lat_g = max(abs(driver_accy_can[corner]))
    field_avg_max_lat_g = mean(field_max_lat_g[corner])
    
    g_ratio = driver_max_lat_g / field_avg_max_lat_g

aggressiveness_score_4 = np.mean(g_ratios)
# Higher = pushing harder through corners
```

#### **A5.5: Risk-Taking Index (Trail Braking)**
**Formula:** `% of corners where brake release happens after turn-in`
**Data Required:**
- Steering angle (`steer_can`)
- Brake pressure (`brake_can`)
- Corner identification
**Calculation:**
```python
trail_brake_corners = 0

for corner in corners:
    turn_in_point = find_first_steering_input(corner)
    brake_release_point = find_brake_release(corner)  # brake_can < 5%
    
    if brake_release_point > turn_in_point:
        trail_brake_corners += 1

aggressiveness_score_5 = trail_brake_corners / total_corners
# Higher = more trail braking (advanced/aggressive technique)
```

### Hypothesis: AGGRESSIVENESS → Race Results
**H5:** Relationship with results is **NON-LINEAR** and **context-dependent**
- **Expected pattern:** 
  - Too low aggressiveness (conservative) = worse results
  - Optimal aggressiveness (right amount of risk) = best results
  - Too high aggressiveness (over-driving) = worse results (crashes, tire wear)
- **Quadratic relationship** expected: Results = β₀ + β₁(AGG) + β₂(AGG²)
- **Context-dependent:** 
  - More important at technical tracks (Barber, Sonoma)
  - Less important at high-speed tracks (COTA)

---

## EXPLORATORY FACTOR ANALYSIS - VALIDATION PLAN

### Step 1: Calculate All 22 Observable Variables
From your data dictionary, calculate all metrics above for each driver-track-race combination.

### Step 2: Test if 5 Factors Emerge
Run EFA with different factor solutions (3, 4, 5, 6, 7 factors) and compare:

**Scree Plot:** Eigenvalues should show 5 factors above 1.0 if your hypothesis is correct

**Factor Loadings:** Check if variables cluster as expected:
| Variable | Expected Factor | Loading Threshold |
|----------|----------------|-------------------|
| F1.1-F1.4 | FOCUS | > 0.5 |
| S2.1-S2.5 | SPRINTING | > 0.5 |
| D3.1-D3.4 | DEFENSE | > 0.5 |
| E4.1-E4.4 | ENDURANCE | > 0.5 |
| A5.1-A5.5 | AGGRESSIVENESS | > 0.5 |

### Step 3: Validate Against Results

**Correlation Analysis:**
```python
factor_scores = fa.transform(data)

for i, factor_name in enumerate(['FOCUS', 'SPRINTING', 'DEFENSE', 'ENDURANCE', 'AGGRESSIVENESS']):
    r, p_value = pearsonr(factor_scores[:, i], finishing_positions)
    print(f"{factor_name}: r={r:.3f}, p={p_value:.4f}")
```

**Expected Correlations with Finishing Position:**
- FOCUS: r = 0.4-0.6, p < 0.05 ✓
- SPRINTING: r = 0.5-0.7, p < 0.001 ✓✓
- DEFENSE: r = 0.3-0.5, p < 0.05 ✓
- ENDURANCE: r = 0.3-0.5, p < 0.05 ✓
- AGGRESSIVENESS: Quadratic relationship (need polynomial regression)

**Multiple Regression:**
```python
# Test combined predictive power
from sklearn.linear_model import LinearRegression

X = factor_scores
y = finishing_positions

model = LinearRegression()
model.fit(X, y)
r_squared = model.score(X, y)

print(f"R² = {r_squared:.3f}")
# Target: R² > 0.60 (factors explain >60% of variance in results)
```

### Step 4: Discover Unexpected Patterns

**Cross-Loadings:** If variables load on multiple factors:
- Example: "Late Braking Index" loads on both SPRINTING (0.6) and AGGRESSIVENESS (0.5)
- Interpretation: Late braking contributes to both race-winning moments AND risk-taking

**Factor Correlations:** Using oblique rotation, check if factors correlate:
- Example: FOCUS and ENDURANCE correlate at r=0.7
- Interpretation: Might be same underlying dimension (merge into "CONSISTENCY")

**Unexpected Factors:** If EFA suggests 6 factors instead of 5:
- Examine which variables split into new factor
- Name and interpret the new dimension
- Example: "Entry Speed" and "Peak Lat G" split from AGGRESSIVENESS → New factor "COURAGE"

---

## TRACK-SPECIFIC FACTOR IMPORTANCE

### Hypothesis: Different Tracks Demand Different Skills

Run separate regressions for each track:

```python
for track in ['Barber', 'COTA', 'Sebring', 'Sonoma', 'VIR', 'Road America']:
    track_data = data[data['track'] == track]
    X_track = factor_scores[data['track'] == track]
    y_track = finishing_positions[data['track'] == track]
    
    model = LinearRegression()
    model.fit(X_track, y_track)
    
    track_profiles[track] = {
        'FOCUS': abs(model.coef_[0]),
        'SPRINTING': abs(model.coef_[1]),
        'DEFENSE': abs(model.coef_[2]),
        'ENDURANCE': abs(model.coef_[3]),
        'AGGRESSIVENESS': abs(model.coef_[4])
    }
    
    # Normalize to percentages
    total = sum(track_profiles[track].values())
    for factor in track_profiles[track]:
        track_profiles[track][factor] = track_profiles[track][factor] / total * 100
```

**Expected Track Profiles:**

**Barber (Technical):**
- FOCUS: 25%
- SPRINTING: 20%
- DEFENSE: 15%
- ENDURANCE: 10%
- AGGRESSIVENESS: 30% ← Highest

**COTA (High-Speed):**
- FOCUS: 20%
- SPRINTING: 35% ← Highest
- DEFENSE: 10%
- ENDURANCE: 15%
- AGGRESSIVENESS: 20%

**Road America (Long):**
- FOCUS: 30%
- SPRINTING: 15%
- DEFENSE: 15%
- ENDURANCE: 25% ← Highest
- AGGRESSIVENESS: 15%

---

## SUCCESS CRITERIA - HOW WE KNOW IT WORKED

### Statistical Validation (Required for Research Credibility)
✅ **Bartlett's Test:** p < 0.05 (variables are correlated enough for FA)
✅ **KMO Measure:** > 0.7 (sampling adequacy is good)
✅ **5 Eigenvalues > 1.0:** (5 factors exist in the data)
✅ **Cumulative Variance:** > 70% (factors explain most of the variance)
✅ **Factor-Result Correlation:** At least 4/5 factors with p < 0.05
✅ **R² > 0.60:** Combined factors predict >60% of finishing position variance

### Practical Validation (Required for Hackathon/Product)
✅ **Interpretability:** Can you explain each factor to a driver in 1 sentence?
✅ **Track Profiles Make Sense:** Do technical tracks show high AGGRESSIVENESS demand?
✅ **Driver Fit Matches Reality:** Do winners at each track score high on that track's profile?
✅ **Actionability:** Can you give specific practice recommendations from factor scores?

### Example Output - If Everything Works:

```
VALIDATED: 5-Factor Model of GR Cup Driver Performance

Factor 1: FOCUS (Consistency at pace)
- Explains 22% of variance
- Correlation with results: r=0.54, p<0.001 ✓

Factor 2: SPRINTING (Race-winning laps)  
- Explains 18% of variance
- Correlation with results: r=0.65, p<0.001 ✓

Factor 3: DEFENSE (Position holding)
- Explains 12% of variance
- Correlation with results: r=0.38, p=0.003 ✓

Factor 4: ENDURANCE (Late-race pace)
- Explains 15% of variance
- Correlation with results: r=0.47, p<0.001 ✓

Factor 5: AGGRESSIVENESS (Risk-taking)
- Explains 11% of variance  
- Quadratic relationship with results ✓

Combined Model: R²=0.67 (explains 67% of variance in finishing position)

Track Profiles:
- Barber: 30% Aggressiveness, 25% Focus
- COTA: 35% Sprinting, 25% Endurance
```

---

## DATA DICTIONARY REQUIREMENTS - WHAT YOU NEED

### From Telemetry Data (per lap):
✓ `brake_can` - brake pressure
✓ `throttle_can` - throttle position
✓ `speed` - vehicle speed
✓ `accy_can` - lateral acceleration
✓ `steer_can` - steering angle
✓ `ecu_gpslatitude` + `ecu_gpslongitude` - position
✓ `Laptrigger_lapdist_dls` - distance along lap

### From Lap Timing Data:
✓ `lap` - lap number
✓ `laptrigger_laptime_dur` - lap time
✓ Sector times (from analysis endurance data)

### From Race Results:
✓ Finishing position
✓ Qualifying position/time

### Calculated/Derived:
- Gap to car ahead (from lap times + positions)
- Gap to car behind (from lap times + positions)
- Corner locations (from speed profile)
- Clean lap identification (from gap data)
- Safety car periods (from lap time anomalies)

---

## NEXT STEP: BUILD THE CALCULATOR

Want me to create the Python script that:
1. Reads your telemetry + lap time data
2. Calculates all 22 observable variables
3. Organizes into EFA-ready dataframe
4. Runs the factor analysis
5. Outputs factor loadings + correlations with results?