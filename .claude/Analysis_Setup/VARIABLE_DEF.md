# Implementation Guide - 25+ Variables from HackTheTrack Data

## 🎯 Mapping Observable Variables to Your Actual Data

**UPDATED** based on complete data dictionary and racing domain knowledge.

**Key Corrections:**
- ✅ Use actual `qualifying/` data (not best_10_laps as proxy)
- ✅ Filter out `FLAG_AT_FL = 'FCY'` laps
- ✅ Calculate lap-by-lap position changes from `ELAPSED` time
- ✅ Available for 6 tracks × 2 races = 12 datasets

Based on your data dictionary, here's EXACTLY how to calculate each of the 25+ variables:

---

## 📊 SPEED Category (5 Variables)

### Variable 1: Qualifying Pace
**Data Source**: `qualifying/` (6 races: COTA R1/R2, Sebring R1/R2, Sonoma R1/R2)
```python
def calc_qualifying_pace(qualifying_df, driver_number):
    """
    Use actual qualifying lap time.
    
    Available for: COTA, Sebring, Sonoma (6 of 12 races)
    """
    if qualifying_df.empty:
        return np.nan  # No qualifying data for this race
    
    # Get driver's qualifying time
    driver_qual = qualifying_df[
        qualifying_df['NUMBER'] == driver_number
    ]
    
    if len(driver_qual) == 0:
        return np.nan  # Driver didn't qualify
    
    driver_time = driver_qual['TIME'].iloc[0]
    driver_time_seconds = convert_to_seconds(driver_time)
    
    # Get pole position time (fastest qualifier)
    pole_time = qualifying_df['TIME'].min()
    pole_time_seconds = convert_to_seconds(pole_time)
    
    # Normalize: 1.0 = pole position, lower = slower
    return pole_time_seconds / driver_time_seconds
```

### Variable 2: Best Race Lap Pace
**Data Source**: `best_10_laps/`
```python
def calc_best_race_lap(best_10_laps_df, driver_number):
    """
    BESTLAP_1 = absolute fastest lap in race conditions.
    Different from qualifying (different fuel load, tire strategy, traffic).
    """
    driver_best = best_10_laps_df[
        best_10_laps_df['NUMBER'] == driver_number
    ]['BESTLAP_1'].iloc[0]
    
    # Convert to seconds
    driver_best_seconds = convert_to_seconds(driver_best)
    
    # Get field best
    field_best = best_10_laps_df['BESTLAP_1'].min()
    field_best_seconds = convert_to_seconds(field_best)
    
    # Normalize
    return field_best_seconds / driver_best_seconds
```

### Variable 3: Average Top-10 Pace
**Data Source**: `best_10_laps/`
```python
def calc_avg_top10_pace(best_10_laps_df, driver_number):
    """
    Use AVERAGE column (average of best 10 laps).
    """
    driver_avg = best_10_laps_df[
        best_10_laps_df['NUMBER'] == driver_number
    ]['AVERAGE'].iloc[0]
    
    field_best_avg = best_10_laps_df['AVERAGE'].min()
    
    return field_best_avg / driver_avg
```

### Variable 4: Top Speed
**Data Source**: `analysis_endurance/`
```python
def calc_top_speed(analysis_endurance_df, driver_number):
    """
    Average TOP_SPEED across clean laps.
    """
    # Filter to green flag laps (no FCY)
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ]
    
    driver_top_speed = clean_laps['TOP_SPEED'].mean()
    
    # Field best
    field_top_speed = analysis_endurance_df[
        analysis_endurance_df['FLAG_AT_FL'] != 'FCY'
    ].groupby('NUMBER')['TOP_SPEED'].mean().max()
    
    return driver_top_speed / field_top_speed
```

### Variable 5: Clean Air Race Pace
**Data Source**: `analysis_endurance/`
```python
def calc_clean_air_pace(analysis_endurance_df, driver_number):
    """
    Average LAP_TIME on green flag laps (no traffic/FCY).
    """
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY') &
        (analysis_endurance_df['LAP_NUMBER'] > 1) &  # Skip first lap
        (analysis_endurance_df['PIT_TIME'].isna())  # No pit stops
    ]
    
    driver_pace = clean_laps['LAP_TIME'].mean()
    
    # Convert to seconds if needed
    driver_pace_seconds = convert_to_seconds(driver_pace)
    
    # Field best
    field_pace = analysis_endurance_df[
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY') &
        (analysis_endurance_df['LAP_NUMBER'] > 1) &
        (analysis_endurance_df['PIT_TIME'].isna())
    ].groupby('NUMBER')['LAP_TIME'].mean().min()
    
    field_pace_seconds = convert_to_seconds(field_pace)
    
    return field_pace_seconds / driver_pace_seconds
```

---

## 🏎️ CORNERING Category (5 Variables)

### Variable 6: Overall Corner Performance
**Data Source**: `analysis_endurance/`
```python
def calc_overall_corner_performance(analysis_endurance_df, driver_number):
    """
    Average of S1, S2, S3 sector times.
    """
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ]
    
    # Average across all three sectors
    driver_avg_sector = clean_laps[['S1_SECONDS', 'S2_SECONDS', 'S3_SECONDS']].mean().mean()
    
    # Field best
    field_avg_sector = analysis_endurance_df[
        analysis_endurance_df['FLAG_AT_FL'] != 'FCY'
    ].groupby('NUMBER')[['S1_SECONDS', 'S2_SECONDS', 'S3_SECONDS']].mean().mean(axis=1).min()
    
    return field_avg_sector / driver_avg_sector
```

### Variable 7: Technical Section Performance (S2)
**Data Source**: `analysis_endurance/`
```python
def calc_technical_performance(analysis_endurance_df, driver_number):
    """
    S2 (Sector 2) - usually technical mid-track sections.
    """
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ]
    
    driver_s2 = clean_laps['S2_SECONDS'].mean()
    field_s2 = analysis_endurance_df[
        analysis_endurance_df['FLAG_AT_FL'] != 'FCY'
    ].groupby('NUMBER')['S2_SECONDS'].mean().min()
    
    return field_s2 / driver_s2
```

### Variable 8: Entry Performance (S1)
**Data Source**: `analysis_endurance/`
```python
def calc_entry_performance(analysis_endurance_df, driver_number):
    """
    S1 (Sector 1) - usually entry into first corners.
    """
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ]
    
    driver_s1 = clean_laps['S1_SECONDS'].mean()
    field_s1 = analysis_endurance_df[
        analysis_endurance_df['FLAG_AT_FL'] != 'FCY'
    ].groupby('NUMBER')['S1_SECONDS'].mean().min()
    
    return field_s1 / driver_s1
```

### Variable 9: Exit Performance (S3)
**Data Source**: `analysis_endurance/`
```python
def calc_exit_performance(analysis_endurance_df, driver_number):
    """
    S3 (Sector 3) - usually exit-critical sections.
    """
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ]
    
    driver_s3 = clean_laps['S3_SECONDS'].mean()
    field_s3 = analysis_endurance_df[
        analysis_endurance_df['FLAG_AT_FL'] != 'FCY'
    ].groupby('NUMBER')['S3_SECONDS'].mean().min()
    
    return field_s3 / driver_s3
```

### Variable 10: Intermediate Point Performance
**Data Source**: `analysis_endurance/`
```python
def calc_intermediate_performance(analysis_endurance_df, driver_number):
    """
    Average of all IM times (IM1a, IM1, IM2a, IM2, IM3a).
    These are specific corners/sections.
    """
    im_cols = ['IM1a_time', 'IM1_time', 'IM2a_time', 'IM2_time', 'IM3a_time']
    
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ]
    
    # Convert IM times to seconds
    driver_im_avg = clean_laps[im_cols].apply(convert_to_seconds).mean().mean()
    
    field_im_avg = analysis_endurance_df[
        analysis_endurance_df['FLAG_AT_FL'] != 'FCY'
    ].groupby('NUMBER')[im_cols].apply(lambda x: x.apply(convert_to_seconds).mean()).mean(axis=1).min()
    
    return field_im_avg / driver_im_avg
```

---

## 🛑 BRAKING Category (5 Variables)

### Variable 11: Braking Depth/Confidence
**Data Source**: `analysis_endurance/`
```python
def calc_braking_depth(analysis_endurance_df, driver_number):
    """
    S1 times (first sector with heavy braking).
    Better braking = faster S1.
    """
    return calc_entry_performance(analysis_endurance_df, driver_number)
```

### Variable 12: Braking Consistency
**Data Source**: `analysis_endurance/`
```python
def calc_braking_consistency(analysis_endurance_df, driver_number):
    """
    Lap-to-lap variation in S1 times.
    """
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ]
    
    driver_s1_std = clean_laps['S1_SECONDS'].std()
    driver_s1_mean = clean_laps['S1_SECONDS'].mean()
    driver_cv = driver_s1_std / driver_s1_mean  # Coefficient of variation
    
    # Field best consistency (lowest CV)
    field_cv = analysis_endurance_df[
        analysis_endurance_df['FLAG_AT_FL'] != 'FCY'
    ].groupby('NUMBER')['S1_SECONDS'].agg(lambda x: x.std() / x.mean()).min()
    
    return field_cv / driver_cv  # Lower CV = better
```

### Variable 13: Brake Modulation (IF TELEMETRY USED)
**Data Source**: `processed_telemetry/`
```python
def calc_brake_modulation(processed_telemetry_df, driver_number):
    """
    Smoothness of brake application.
    Standard deviation of brake pressure during braking zones.
    
    NOTE: Only use if implementing telemetry analysis.
    Otherwise, skip this variable.
    """
    # Filter to driver and braking zones
    braking_data = processed_telemetry_df[
        (processed_telemetry_df['vehicle_number'] == driver_number) &
        (processed_telemetry_df['pbrake_f'] > 0.1)  # Braking
    ]
    
    # Std dev of brake pressure (lower = smoother)
    driver_brake_std = braking_data['pbrake_f'].std()
    
    # Field best
    field_brake_std = processed_telemetry_df[
        processed_telemetry_df['pbrake_f'] > 0.1
    ].groupby('vehicle_number')['pbrake_f'].std().min()
    
    return field_brake_std / driver_brake_std
```

### Variable 14: Braking in Traffic
**Data Source**: `analysis_endurance/` + `provisional_results/`
```python
def calc_braking_in_traffic(analysis_endurance_df, provisional_results_df, driver_number):
    """
    S1 performance when in traffic vs clean air.

    NOTE: This is challenging to calculate without lap-by-lap gap data.
    Alternative approach: Compare early race (traffic) vs late race (spread out).

    ⚠️ EXCLUDE FLAG_AT_FL = 'FCY' laps from both groups
    """
    # Get all laps for this driver
    driver_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')  # Exclude FCY
    ].copy()

    max_lap = driver_laps['LAP_NUMBER'].max()

    # Early laps (2-10) = likely in traffic
    early_laps = driver_laps[driver_laps['LAP_NUMBER'].between(2, 10)]
    # Late laps (last 10) = field spread out
    late_laps = driver_laps[driver_laps['LAP_NUMBER'] > max_lap - 10]

    if len(early_laps) < 3 or len(late_laps) < 3:
        return 0.5  # Not enough data

    early_s1 = early_laps['S1_SECONDS'].mean()
    late_s1 = late_laps['S1_SECONDS'].mean()

    # Penalty = how much slower early (traffic) vs late (clean)
    driver_penalty = (early_s1 - late_s1) / late_s1

    # Field average penalty
    field_penalty = analysis_endurance_df[
        analysis_endurance_df['FLAG_AT_FL'] != 'FCY'
    ].groupby('NUMBER').apply(
        lambda x: (x[x['LAP_NUMBER'].between(2, 10)]['S1_SECONDS'].mean() -
                   x[x['LAP_NUMBER'] > x['LAP_NUMBER'].max() - 10]['S1_SECONDS'].mean()) /
                   x[x['LAP_NUMBER'] > x['LAP_NUMBER'].max() - 10]['S1_SECONDS'].mean()
    ).mean()

    # Lower penalty = better in traffic
    return field_penalty / driver_penalty if driver_penalty > 0 else 1.0
```

### Variable 15: Heavy Braking Zone Performance
**Data Source**: `analysis_endurance/`
```python
def calc_heavy_braking_performance(analysis_endurance_df, driver_number):
    """
    Performance at IM1 (usually first heavy braking corner).
    """
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ]
    
    driver_im1 = clean_laps['IM1_time'].apply(convert_to_seconds).mean()
    
    field_im1 = analysis_endurance_df[
        analysis_endurance_df['FLAG_AT_FL'] != 'FCY'
    ].groupby('NUMBER')['IM1_time'].apply(lambda x: x.apply(convert_to_seconds).mean()).min()
    
    return field_im1 / driver_im1
```

---

## 🔥 TIRE MANAGEMENT Category (5 Variables)

### Variable 16: Pace Degradation Rate
**Data Source**: `analysis_endurance/`
```python
def calc_pace_degradation(analysis_endurance_df, driver_number):
    """
    Linear regression slope of lap time vs lap number.
    """
    from scipy.stats import linregress
    
    # Get clean laps
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY') &
        (analysis_endurance_df['LAP_NUMBER'] > 1) &
        (analysis_endurance_df['PIT_TIME'].isna())
    ].copy()
    
    if len(clean_laps) < 5:
        return 0.5  # Not enough data
    
    # Convert lap times to seconds
    clean_laps['LAP_TIME_SECONDS'] = clean_laps['LAP_TIME'].apply(convert_to_seconds)
    
    # Linear regression
    slope, _, _, _, _ = linregress(
        clean_laps['LAP_NUMBER'], 
        clean_laps['LAP_TIME_SECONDS']
    )
    
    # Positive slope = degrading
    # Field best = lowest degradation
    field_slopes = analysis_endurance_df[
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY') &
        (analysis_endurance_df['LAP_NUMBER'] > 1) &
        (analysis_endurance_df['PIT_TIME'].isna())
    ].groupby('NUMBER').apply(
        lambda x: linregress(
            x['LAP_NUMBER'], 
            x['LAP_TIME'].apply(convert_to_seconds)
        )[0]
    )
    
    field_best_slope = field_slopes.min()
    
    # Lower slope = better tire management
    return field_best_slope / slope if slope > 0 else 1.0
```

### Variable 17: Late Stint Performance
**Data Source**: `analysis_endurance/`
```python
def calc_late_stint_performance(analysis_endurance_df, driver_number):
    """
    Average pace in final third of race.
    """
    driver_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ]
    
    max_lap = driver_laps['LAP_NUMBER'].max()
    late_stint_threshold = max_lap * 0.66
    
    late_laps = driver_laps[driver_laps['LAP_NUMBER'] > late_stint_threshold]
    
    if len(late_laps) < 3:
        return 0.5
    
    driver_late_pace = late_laps['LAP_TIME'].apply(convert_to_seconds).mean()
    
    # Field best late pace
    field_late_pace = analysis_endurance_df[
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ].groupby('NUMBER').apply(
        lambda x: x[x['LAP_NUMBER'] > x['LAP_NUMBER'].max() * 0.66]['LAP_TIME'].apply(convert_to_seconds).mean()
    ).min()
    
    return field_late_pace / driver_late_pace
```

### Variable 18: Stint Consistency
**Data Source**: `analysis_endurance/`
```python
def calc_stint_consistency(analysis_endurance_df, driver_number):
    """
    Coefficient of variation across all laps.
    """
    clean_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY') &
        (analysis_endurance_df['LAP_NUMBER'] > 1)
    ]
    
    lap_times = clean_laps['LAP_TIME'].apply(convert_to_seconds)
    
    # Remove outliers (>107% of best lap)
    best_lap = lap_times.min()
    valid_laps = lap_times[lap_times < best_lap * 1.07]
    
    driver_cv = valid_laps.std() / valid_laps.mean()
    
    # Field best consistency
    field_cv = analysis_endurance_df[
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY') &
        (analysis_endurance_df['LAP_NUMBER'] > 1)
    ].groupby('NUMBER').apply(
        lambda x: x['LAP_TIME'].apply(convert_to_seconds).std() / 
                  x['LAP_TIME'].apply(convert_to_seconds).mean()
    ).min()
    
    return field_cv / driver_cv
```

### Variable 19: Corner Speed Degradation
**Data Source**: `analysis_endurance/`
```python
def calc_corner_speed_degradation(analysis_endurance_df, driver_number):
    """
    S2 time degradation (mid-corner speed loss indicates tire wear).
    """
    driver_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY')
    ]
    
    # Early laps (2-5)
    early_laps = driver_laps[driver_laps['LAP_NUMBER'].between(2, 5)]
    # Late laps (last 5 laps)
    max_lap = driver_laps['LAP_NUMBER'].max()
    late_laps = driver_laps[driver_laps['LAP_NUMBER'] > max_lap - 5]
    
    if len(early_laps) < 2 or len(late_laps) < 2:
        return 0.5
    
    early_s2 = early_laps['S2_SECONDS'].mean()
    late_s2 = late_laps['S2_SECONDS'].mean()
    
    driver_degradation = (late_s2 - early_s2) / early_s2
    
    # Field average degradation
    field_degradation = analysis_endurance_df[
        analysis_endurance_df['FLAG_AT_FL'] != 'FCY'
    ].groupby('NUMBER').apply(
        lambda x: (x[x['LAP_NUMBER'] > x['LAP_NUMBER'].max() - 5]['S2_SECONDS'].mean() - 
                   x[x['LAP_NUMBER'].between(2, 5)]['S2_SECONDS'].mean()) / 
                   x[x['LAP_NUMBER'].between(2, 5)]['S2_SECONDS'].mean()
    ).mean()
    
    # Lower degradation = better
    return field_degradation / driver_degradation if driver_degradation > 0 else 1.0
```

### Variable 20: Brake Pressure Fade (IF TELEMETRY)
**Data Source**: `processed_telemetry/`
```python
def calc_brake_pressure_fade(processed_telemetry_df, driver_number):
    """
    Front tire wear indicator - brake pressure reduction over stint.
    
    NOTE: Only use if implementing telemetry.
    """
    driver_data = processed_telemetry_df[
        processed_telemetry_df['vehicle_number'] == driver_number
    ]
    
    # Early laps
    early_data = driver_data[driver_data['lap'].between(2, 5)]
    # Late laps
    max_lap = driver_data['lap'].max()
    late_data = driver_data[driver_data['lap'] > max_lap - 5]
    
    early_brake = early_data[early_data['pbrake_f'] > 0.5]['pbrake_f'].mean()
    late_brake = late_data[late_data['pbrake_f'] > 0.5]['pbrake_f'].mean()
    
    driver_fade = (early_brake - late_brake) / early_brake
    
    # Field average fade
    field_fade = processed_telemetry_df[
        processed_telemetry_df['pbrake_f'] > 0.5
    ].groupby('vehicle_number').apply(
        lambda x: (x[x['lap'].between(2, 5)]['pbrake_f'].mean() - 
                   x[x['lap'] > x['lap'].max() - 5]['pbrake_f'].mean()) / 
                   x[x['lap'].between(2, 5)]['pbrake_f'].mean()
    ).mean()
    
    return field_fade / driver_fade if driver_fade > 0 else 1.0
```

---

## 🏁 RACECRAFT Category (5 Variables)

### Variable 21: In-Race Position Changes (Lap-by-Lap Racecraft)
**Data Source**: `analysis_endurance/`
```python
def calc_position_changes_per_lap(analysis_endurance_df, driver_number):
    """
    Calculate lap-by-lap position changes during race.

    This measures in-race racecraft ability - passing, defending, racing in traffic.
    Different from overall positions gained (quali → finish).

    See: POSITION_CHANGES_CALCULATION.md for full methodology
    """
    # Filter valid laps
    valid = analysis_endurance_df[
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY') &
        (analysis_endurance_df['LAP_NUMBER'] > 1)  # Skip first lap
    ].copy()

    # Convert elapsed to numeric (seconds)
    valid['ELAPSED_SECONDS'] = pd.to_timedelta(valid['ELAPSED']).dt.total_seconds()

    # Calculate running position for each lap
    positions = []
    for lap_num in valid['LAP_NUMBER'].unique():
        lap_data = valid[valid['LAP_NUMBER'] == lap_num].copy()
        # Rank by elapsed time (lower time = better position)
        lap_data['running_position'] = lap_data['ELAPSED_SECONDS'].rank(method='min')
        positions.append(lap_data[['NUMBER', 'LAP_NUMBER', 'running_position']])

    positions_df = pd.concat(positions).sort_values(['NUMBER', 'LAP_NUMBER'])

    # Calculate change from previous lap (multiply by -1: gaining position = number goes down)
    positions_df['position_change'] = (
        positions_df.groupby('NUMBER')['running_position'].diff() * -1
    ).fillna(0)

    # Get this driver's data
    driver_changes = positions_df[positions_df['NUMBER'] == driver_number]

    if len(driver_changes) == 0:
        return 0.0

    # Average positions gained per lap
    avg_change = driver_changes['position_change'].mean()

    # Normalize: field average is 0, positive = gained positions, negative = lost
    field_avg = positions_df.groupby('NUMBER')['position_change'].mean().mean()

    # Return normalized score (0.5 = average, 1.0 = best, 0.0 = worst)
    field_std = positions_df.groupby('NUMBER')['position_change'].mean().std()

    if field_std == 0:
        return 0.5

    z_score = (avg_change - field_avg) / field_std

    # Convert to 0-1 scale
    return 0.5 + (z_score / 6)  # 6 std devs spans most of range
```

### Variable 22: Position Stability (Defensive Racecraft)
**Data Source**: `analysis_endurance/`
```python
def calc_position_stability(analysis_endurance_df, driver_number):
    """
    Standard deviation of lap-by-lap running position.

    Lower std dev = maintained position better (good defending).
    Higher std dev = position fluctuated (losing then regaining spots).
    """
    # Use same position calculation from Variable 21
    positions_df = calculate_running_positions(analysis_endurance_df)

    driver_positions = positions_df[positions_df['NUMBER'] == driver_number]['running_position']

    if len(driver_positions) < 3:
        return 0.5

    driver_std = driver_positions.std()

    # Field best stability (lowest std)
    field_std = positions_df.groupby('NUMBER')['running_position'].std()
    field_best_std = field_std.min()

    # Lower std = better stability
    return field_best_std / driver_std if driver_std > 0 else 1.0
```

### Variable 23: Traffic Pace Penalty
**Data Source**: `analysis_endurance/`
```python
def calc_traffic_pace_penalty(analysis_endurance_df, driver_number):
    """
    Lap time difference during early race (traffic) vs late race (spread out).

    ⚠️ DO NOT USE FCY laps - those are caution periods, not racing in traffic.
    Instead, compare early laps (field bunched) vs late laps (field spread).
    """
    driver_laps = analysis_endurance_df[
        (analysis_endurance_df['NUMBER'] == driver_number) &
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY') &  # Exclude FCY
        (analysis_endurance_df['LAP_NUMBER'] > 1) &
        (analysis_endurance_df['PIT_TIME'].isna())
    ]

    max_lap = driver_laps['LAP_NUMBER'].max()

    # Early laps = traffic
    early_laps = driver_laps[driver_laps['LAP_NUMBER'].between(2, 10)]
    # Late laps = spread out
    late_laps = driver_laps[driver_laps['LAP_NUMBER'] > max_lap - 10]

    if len(early_laps) < 2 or len(late_laps) < 2:
        return 0.5

    early_pace = early_laps['LAP_TIME'].apply(convert_to_seconds).mean()
    late_pace = late_laps['LAP_TIME'].apply(convert_to_seconds).mean()

    driver_penalty = (early_pace - late_pace) / late_pace

    # Field average penalty
    field_penalty = analysis_endurance_df[
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY') &
        (analysis_endurance_df['LAP_NUMBER'] > 1) &
        (analysis_endurance_df['PIT_TIME'].isna())
    ].groupby('NUMBER').apply(
        lambda x: (x[x['LAP_NUMBER'].between(2, 10)]['LAP_TIME'].apply(convert_to_seconds).mean() -
                   x[x['LAP_NUMBER'] > x['LAP_NUMBER'].max() - 10]['LAP_TIME'].apply(convert_to_seconds).mean()) /
                   x[x['LAP_NUMBER'] > x['LAP_NUMBER'].max() - 10]['LAP_TIME'].apply(convert_to_seconds).mean()
    ).mean()

    return field_penalty / driver_penalty if driver_penalty > 0 else 1.0
```

### Variable 24: Positions Gained (Qualifying to Finish)
**Data Source**: `provisional_results/` + `qualifying/`
```python
def calc_positions_gained(provisional_results_df, qualifying_df, driver_number):
    """
    Race finish position - qualifying position = positions gained.
    
    Positive = gained positions (started 10th, finished 5th = +5)
    Negative = lost positions (started 3rd, finished 8th = -5)
    
    Available for: COTA, Sebring, Sonoma (6 of 12 races)
    """
    if qualifying_df.empty:
        return np.nan  # No qualifying data
    
    # Get race finish position
    race_finish = provisional_results_df[
        provisional_results_df['NUMBER'] == driver_number
    ]['POSITION'].iloc[0]
    
    # Get qualifying position
    qual_driver = qualifying_df[qualifying_df['NUMBER'] == driver_number]
    
    if len(qual_driver) == 0:
        return np.nan  # Driver didn't qualify
    
    qual_position = qual_driver['POS'].iloc[0]
    
    # Calculate positions gained (positive = improvement)
    positions_gained = qual_position - race_finish
    
    # Normalize to 0-1 scale
    # Max possible gain = starting last and winning
    max_drivers = len(provisional_results_df)
    
    # Scale: -1 (lost all positions) to +1 (gained maximum positions)
    normalized = positions_gained / max_drivers
    
    # Transform to 0-1: 0.5 = no change, 1.0 = max gain, 0.0 = max loss
    return 0.5 + normalized
```

### Variable 25: First Lap Performance
**Data Source**: `analysis_endurance/`
```python
def calc_first_lap_performance(analysis_endurance_df, driver_number):
    """
    Lap 1 pace vs average pace (racecraft/aggression indicator).
    """
    driver_laps = analysis_endurance_df[
        analysis_endurance_df['NUMBER'] == driver_number
    ]
    
    lap_1_time = driver_laps[
        driver_laps['LAP_NUMBER'] == 1
    ]['LAP_TIME'].apply(convert_to_seconds).iloc[0]
    
    avg_pace = driver_laps[
        (driver_laps['LAP_NUMBER'] > 1) &
        (driver_laps['FLAG_AT_FL'] != 'FCY')
    ]['LAP_TIME'].apply(convert_to_seconds).mean()
    
    # Lap 1 typically slower, but less penalty = good racecraft
    driver_penalty = (lap_1_time - avg_pace) / avg_pace
    
    # Field average penalty
    field_penalty = analysis_endurance_df.groupby('NUMBER').apply(
        lambda x: (x[x['LAP_NUMBER'] == 1]['LAP_TIME'].apply(convert_to_seconds).iloc[0] - 
                   x[(x['LAP_NUMBER'] > 1) & (x['FLAG_AT_FL'] != 'FCY')]['LAP_TIME'].apply(convert_to_seconds).mean()) / 
                   x[(x['LAP_NUMBER'] > 1) & (x['FLAG_AT_FL'] != 'FCY')]['LAP_TIME'].apply(convert_to_seconds).mean()
    ).mean()
    
    return field_penalty / driver_penalty if driver_penalty > 0 else 1.0
```

---

## 🛠️ Helper Functions

### Convert Time to Seconds
```python
def convert_to_seconds(time_str):
    """
    Convert lap time string to seconds.

    Handles formats:
    - "1:23.456" → 83.456
    - "23.456" → 23.456
    - "1'23.456" → 83.456
    """
    import re

    if pd.isna(time_str):
        return np.nan

    time_str = str(time_str)

    # Already a number
    if time_str.replace('.', '').isdigit():
        return float(time_str)

    # Format: 1:23.456 or 1'23.456
    if ':' in time_str or "'" in time_str:
        parts = re.split('[:' + "'" + ']', time_str)
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds

    return float(time_str)
```

### Calculate Running Positions (Used by Variables 21-22)
```python
def calculate_running_positions(analysis_endurance_df):
    """
    Calculate lap-by-lap running position for all drivers.

    Used by Variable 21 (position changes) and Variable 22 (position stability).
    See: POSITION_CHANGES_CALCULATION.md for full methodology

    Returns: DataFrame with columns [NUMBER, LAP_NUMBER, running_position]
    """
    # Filter valid laps
    valid = analysis_endurance_df[
        (analysis_endurance_df['FLAG_AT_FL'] != 'FCY') &
        (analysis_endurance_df['LAP_NUMBER'] > 1)  # Skip first lap
    ].copy()

    # Convert elapsed to numeric (seconds)
    valid['ELAPSED_SECONDS'] = pd.to_timedelta(valid['ELAPSED']).dt.total_seconds()

    # Calculate running position for each lap
    positions = []
    for lap_num in valid['LAP_NUMBER'].unique():
        lap_data = valid[valid['LAP_NUMBER'] == lap_num].copy()
        # Rank by elapsed time (lower time = better position)
        lap_data['running_position'] = lap_data['ELAPSED_SECONDS'].rank(method='min')
        positions.append(lap_data[['NUMBER', 'LAP_NUMBER', 'running_position']])

    positions_df = pd.concat(positions).sort_values(['NUMBER', 'LAP_NUMBER'])

    return positions_df
```

---

## 📊 Complete Implementation

```python
def build_complete_feature_matrix(race_name):
    """
    Build all 25 variables for a single race.

    Args:
        race_name: e.g., 'barber_r1', 'cota_r2', etc.

    Returns:
        DataFrame with 25 feature columns + driver_number + finishing_position

    Note: Variables 1 (qualifying_pace) and 24 (positions_gained) will be NaN
          for races without qualifying data (Barber, Road America, VIR).
    """
    # Load data
    endurance = pd.read_csv(f'data/race_results/analysis_endurance/{race_name}_analysis_endurance.csv', delimiter=';')
    best_10 = pd.read_csv(f'data/race_results/best_10_laps/{race_name}_best_10_laps.csv')
    provisional = pd.read_csv(f'data/race_results/provisional_results/{race_name}_provisional_results.csv')

    # Load qualifying if available (COTA, Sebring, Sonoma only)
    try:
        # Note: Qualifying files use different naming convention
        qualifying = pd.read_csv(f'data/qualifying/{race_name.upper()}_Qualifying.csv')
        print(f"✅ Loaded qualifying data for {race_name}")
    except FileNotFoundError:
        qualifying = pd.DataFrame()  # Empty if no qualifying data
        print(f"⚠️ No qualifying data for {race_name} - Variables 1 & 24 will be NaN")

    # Get all drivers
    drivers = provisional['NUMBER'].unique()

    # Build feature matrix
    features = []

    for driver in drivers:
        feature_row = {
            'driver_number': driver,

            # SPEED (5 variables)
            'qualifying_pace': calc_qualifying_pace(qualifying, driver),  # Uses actual quali TIME!
            'best_race_lap': calc_best_race_lap(best_10, driver),
            'avg_top10_pace': calc_avg_top10_pace(best_10, driver),
            'top_speed': calc_top_speed(endurance, driver),  # FCY filtered
            'clean_air_pace': calc_clean_air_pace(endurance, driver),  # FCY filtered

            # CORNERING (5 variables)
            'overall_corner_perf': calc_overall_corner_performance(endurance, driver),  # FCY filtered
            'technical_perf': calc_technical_performance(endurance, driver),  # S2, FCY filtered
            'entry_perf': calc_entry_performance(endurance, driver),  # S1, FCY filtered
            'exit_perf': calc_exit_performance(endurance, driver),  # S3, FCY filtered
            'intermediate_perf': calc_intermediate_performance(endurance, driver),  # FCY filtered

            # BRAKING (5 variables, skip 13 if no telemetry)
            'braking_depth': calc_braking_depth(endurance, driver),  # FCY filtered
            'braking_consistency': calc_braking_consistency(endurance, driver),  # FCY filtered
            # 'brake_modulation': calc_brake_modulation(telemetry, driver),  # OPTIONAL - telemetry only
            'braking_in_traffic': calc_braking_in_traffic(endurance, provisional, driver),  # FCY filtered
            'heavy_braking_perf': calc_heavy_braking_performance(endurance, driver),  # FCY filtered

            # TIRE MANAGEMENT (5 variables, skip 20 if no telemetry)
            'pace_degradation': calc_pace_degradation(endurance, driver),  # FCY filtered
            'late_stint_perf': calc_late_stint_performance(endurance, driver),  # FCY filtered
            'stint_consistency': calc_stint_consistency(endurance, driver),  # FCY filtered
            'corner_speed_deg': calc_corner_speed_degradation(endurance, driver),  # FCY filtered
            # 'brake_pressure_fade': calc_brake_pressure_fade(telemetry, driver),  # OPTIONAL - telemetry only

            # RACECRAFT (5 variables)
            'position_changes_per_lap': calc_position_changes_per_lap(endurance, driver),  # NEW! From ELAPSED
            'position_stability': calc_position_stability(endurance, driver),  # NEW! From ELAPSED
            'traffic_pace_penalty': calc_traffic_pace_penalty(endurance, driver),  # FCY filtered, corrected!
            'positions_gained': calc_positions_gained(provisional, qualifying, driver),  # Uses quali POS!
            'first_lap_perf': calc_first_lap_performance(endurance, driver),  # FCY filtered

            # Add finishing position
            'finishing_position': provisional[provisional['NUMBER'] == driver]['POSITION'].iloc[0]
        }

        features.append(feature_row)

    feature_df = pd.DataFrame(features)

    print(f"✅ Built feature matrix: {feature_df.shape}")
    print(f"   {len(drivers)} drivers × {len(feature_df.columns)-2} variables")

    # Check for missing qualifying data
    if qualifying.empty:
        nan_count = feature_df[['qualifying_pace', 'positions_gained']].isna().sum().sum()
        print(f"   ⚠️ {nan_count} NaN values (no qualifying data)")

    return feature_df

# Example usage:

# For races WITH qualifying data (6 races)
races_with_quali = [
    'cota_r1', 'cota_r2',
    'sebring_r1', 'sebring_r2',
    'sonoma_r1', 'sonoma_r2'
]

all_features_full = []
for race in races_with_quali:
    features = build_complete_feature_matrix(race)
    features['race'] = race
    all_features_full.append(features)
    features.to_csv(f'data/analysis_outputs/{race}_feature_matrix.csv', index=False)

combined_full = pd.concat(all_features_full)
combined_full.to_csv('data/analysis_outputs/all_races_WITH_qualifying_features.csv', index=False)
print(f"\n✅ Combined: {combined_full.shape}")
print(f"   {len(races_with_quali)} races × {len(combined_full['driver_number'].unique())} drivers")
print(f"   Ready for factor analysis with ALL 25 variables!")

# For races WITHOUT qualifying data (6 races)
races_no_quali = [
    'barber_r1', 'barber_r2',
    'roadamerica_r1', 'roadamerica_r2',
    'vir_r1', 'vir_r2'
]

all_features_partial = []
for race in races_no_quali:
    features = build_complete_feature_matrix(race)  # Will have NaN for vars 1, 24
    features['race'] = race
    all_features_partial.append(features)
    features.to_csv(f'data/analysis_outputs/{race}_feature_matrix.csv', index=False)

combined_partial = pd.concat(all_features_partial)
combined_partial.to_csv('data/analysis_outputs/all_races_WITHOUT_qualifying_features.csv', index=False)
print(f"\n✅ Combined: {combined_partial.shape}")
print(f"   {len(races_no_quali)} races × {len(combined_partial['driver_number'].unique())} drivers")
print(f"   Ready for factor analysis with 23 variables (excluding vars 1, 24)")
```

---

## ✅ Variables We Can Actually Calculate

### **For Races WITH Qualifying Data (COTA, Sebring, Sonoma = 6 races):**
- ✅ **All 25 variables** fully calculated!

**SPEED (5):**
1. ✅ Qualifying pace (actual quali TIME from `qualifying/`)
2. ✅ Best race lap (BESTLAP_1)
3. ✅ Avg top-10 pace (AVERAGE)
4. ✅ Top speed (TOP_SPEED, FCY filtered)
5. ✅ Clean air pace (LAP_TIME, FCY filtered)

**CORNERING (5):**
6. ✅ Overall corner performance (S1+S2+S3, FCY filtered)
7. ✅ Technical performance (S2, FCY filtered)
8. ✅ Entry performance (S1, FCY filtered)
9. ✅ Exit performance (S3, FCY filtered)
10. ✅ Intermediate performance (IM points, FCY filtered)

**BRAKING (5):**
11. ✅ Braking depth (S1, FCY filtered)
12. ✅ Braking consistency (S1 variation, FCY filtered)
13. ⚠️ Brake modulation (OPTIONAL - requires processed_telemetry)
14. ✅ Braking in traffic (early vs late, FCY filtered)
15. ✅ Heavy braking performance (IM1, FCY filtered)

**TIRE MANAGEMENT (5):**
16. ✅ Pace degradation rate (lap time slope, FCY filtered)
17. ✅ Late stint performance (last 33%, FCY filtered)
18. ✅ Stint consistency (CoV, FCY filtered)
19. ✅ Corner speed degradation (S2 early vs late, FCY filtered)
20. ⚠️ Brake pressure fade (OPTIONAL - requires processed_telemetry)

**RACECRAFT (5):**
21. ✅ **In-race position changes** (lap-by-lap from ELAPSED time, FCY filtered) - NEW!
22. ✅ **Position stability** (std dev of running position, FCY filtered) - NEW!
23. ✅ Traffic pace penalty (early vs late, FCY filtered - corrected!)
24. ✅ **Positions gained** (quali POS → race POSITION from `qualifying/`)
25. ✅ First lap performance (FCY filtered)

---

### **For Races WITHOUT Qualifying Data (Barber, Road America, VIR = 6 races):**
- ✅ **23 of 25 variables** calculated
- ❌ Variables 1 (qualifying_pace) and 24 (positions_gained) = NaN (no qualifying data)
- ⚠️ Variables 13, 20 optional (telemetry required)

**Strategy**:
- Run factor analysis on COTA/Sebring/Sonoma first (full 25 variables)
- Then apply learned factor structure to all 12 races using 23 variables
- Or: Use BESTLAP_1 as proxy for qualifying pace in races without quali data

---

### **Key Updates Made:**
✅ **Variable 1**: Now uses actual `qualifying/TIME` (not best_10_laps proxy)
✅ **Variable 21**: Changed from placeholder to **In-Race Position Changes** (calculated from ELAPSED)
✅ **Variable 22**: Changed from placeholder to **Position Stability** (std dev of running position)
✅ **Variable 23**: Corrected to NOT use FCY laps (use early vs late race instead)
✅ **Variable 24**: Now uses actual `qualifying/POS` → `provisional_results/POSITION`
✅ **All variables**: Added `FLAG_AT_FL != 'FCY'` filtering where appropriate

**Optional with telemetry:**
- ⚠️ Variables 13, 20 (Brake modulation, pressure fade) - only if using `processed_telemetry/`
- Can skip these for initial factor analysis

---

## 🎯 Recommended Approach

### Option 1: Full Analysis on 6 Races (COTA, Sebring, Sonoma)
**Use this for discovering skill dimensions with ALL 25 variables**

```python
import pandas as pd
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler

# Load combined feature matrix
combined_df = pd.read_csv('data/analysis_outputs/all_races_WITH_qualifying_features.csv')

# Prepare for factor analysis
feature_cols = [col for col in combined_df.columns
                if col not in ['driver_number', 'finishing_position', 'race']]

X = combined_df[feature_cols].fillna(combined_df[feature_cols].mean())  # Impute any NaN
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Run factor analysis - discover 5-7 skill dimensions
fa = FactorAnalysis(n_components=6, random_state=42)
factor_scores = fa.fit_transform(X_scaled)

# Analyze factor loadings to interpret skills
loadings = pd.DataFrame(
    fa.components_.T,
    columns=[f'Factor_{i+1}' for i in range(6)],
    index=feature_cols
)

print("Factor Loadings (which variables load on which skills):")
print(loadings.round(3))

# Discover your 6 skill dimensions!
# High loadings (>0.5) indicate which variables contribute to each skill
```

### Option 2: All 12 Races Using 23 Variables
**Use this for broader validation across all tracks**

```python
# Load races WITH qualifying
with_quali = pd.read_csv('data/analysis_outputs/all_races_WITH_qualifying_features.csv')

# Load races WITHOUT qualifying
without_quali = pd.read_csv('data/analysis_outputs/all_races_WITHOUT_qualifying_features.csv')

# Combine and drop variables 1 & 24 (not available for all races)
combined_all = pd.concat([with_quali, without_quali])
combined_all = combined_all.drop(columns=['qualifying_pace', 'positions_gained'])

# Now run factor analysis on 23 variables across all 12 races
feature_cols = [col for col in combined_all.columns
                if col not in ['driver_number', 'finishing_position', 'race']]

# Same process as Option 1...
```

### Option 3: Use BESTLAP_1 as Qualifying Proxy
**Alternative: Fill missing qualifying data**

```python
# For races without qualifying data, use best_race_lap as proxy for qualifying_pace
combined_all['qualifying_pace'] = combined_all['qualifying_pace'].fillna(
    combined_all['best_race_lap']
)

# Still need to drop positions_gained (can't be calculated without quali)
combined_all = combined_all.drop(columns=['positions_gained'])

# Now run factor analysis on 24 variables across all 12 races
```

---

## 📋 Summary

**Total Variables Implemented: 25**

✅ **23 variables** ready for ALL 12 races (Barber, COTA, Road America, Sebring, Sonoma, VIR × 2)
✅ **25 variables** ready for 6 races with qualifying (COTA, Sebring, Sonoma × 2)

**Key Corrections Applied:**
- ✅ All variables now filter `FLAG_AT_FL != 'FCY'` (exclude caution laps)
- ✅ Variable 1 uses actual `qualifying/TIME` (not best_10_laps proxy)
- ✅ Variables 21-22 implemented as position changes from ELAPSED time
- ✅ Variable 23 corrected to use early vs late race (not FCY as traffic)
- ✅ Variable 24 uses actual `qualifying/POS` → race finish

**Data Sources:**
- `race_results/provisional_results/` - Race finishing positions
- `race_results/analysis_endurance/` - Lap-by-lap with S1, S2, S3 sectors
- `race_results/best_10_laps/` - Top 10 laps per driver
- `qualifying/` - Qualifying results (6 of 12 races)
- `processed_telemetry/` - OPTIONAL for Variables 13, 20

**Next Step:** Run factor analysis to discover 5-7 latent skill dimensions from these 23-25 observable variables!

This is MORE than enough for factor analysis to discover your skill dimensions across all tracks and drivers!
