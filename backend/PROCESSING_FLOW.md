# Telemetry Corner Analysis - Processing Flow

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RAW TELEMETRY DATA (CSV)                         │
│  1.6 GB | 10 races | ~11M rows | 20-40Hz sampling                  │
│  Columns: lap, distance, speed, steering, brakes, G-forces, GPS    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TELEMETRY PROCESSOR                              │
│  Load CSV → Filter drivers → Identify best laps                    │
│  Processing: ~2.5s per race (122MB)                                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CORNER DETECTOR                                  │
│  1. High Steering Angle (>30°)                                     │
│  2. High Lateral G-Force (>0.8g)                                   │
│  3. Group consecutive zones                                         │
│  4. Filter by min duration (0.5s)                                  │
│  5. Merge nearby corners (<50m gap)                                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CORNER ZONE ANALYSIS                             │
│  For each detected corner:                                          │
│  • Find apex (min speed)                                           │
│  • Identify entry/exit points                                      │
│  • Extract 9 key metrics                                           │
│  • Calculate braking point                                         │
│  • Find throttle application point                                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    METRIC AGGREGATION                               │
│  Per driver, per lap, per corner:                                  │
│  • Braking point (m)                                               │
│  • Entry/apex/exit speeds (km/h)                                   │
│  • Corner time (s)                                                 │
│  • Lateral G max (g)                                               │
│  • Steering smoothness (std)                                       │
│  • Brake pressure max (bar)                                        │
│  • Throttle application point (m)                                  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    JSON OUTPUT                                      │
│  {                                                                  │
│    "track": "barber",                                              │
│    "race": 1,                                                      │
│    "drivers": {                                                    │
│      "7": { "best_lap": 23, "corners": [...] },                   │
│      "13": { "best_lap": 9, "corners": [...] }                    │
│    }                                                               │
│  }                                                                 │
│  Size: ~1.5 MB for all races (300 KB compressed)                  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DRIVER COMPARISON                                │
│  Compare two drivers on specific corner:                           │
│  • Calculate metric differences                                    │
│  • Generate coaching insights                                      │
│  • Identify improvement opportunities                              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    COACHING INSIGHTS                                │
│  "Driver 13 is 0.3s faster through Turn 1"                         │
│  "Brake 15 meters later (125m vs 110m)"                            │
│  "Carry 3.2 km/h more entry speed"                                 │
│  "Apply throttle 8 meters earlier"                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Processing Steps

### Step 1: Data Loading

```
Input:  barber_r1_wide.csv (122 MB, 1,043,290 rows)
Action: Load CSV with pandas, filter by vehicle_numbers
Output: DataFrame with telemetry for selected drivers
Time:   ~1.5 seconds
```

**Key Columns**:
- `Laptrigger_lapdist_dls` - Distance along lap (meters)
- `Steering_Angle` - Steering input (-180 to +180 degrees)
- `accy_can` - Lateral G-force (-3.0 to +3.0 g)
- `speed` - Vehicle speed (km/h)
- `pbrake_f` - Front brake pressure (0-150 bar)
- `aps` - Throttle position (0-100%)

---

### Step 2: Lap Identification

```
Input:  Driver telemetry DataFrame
Action: Group by 'lap' column, calculate lap times
Output: Best lap identification per driver
Logic:  Parse timestamps, calculate duration, sort by time
```

**Lap Time Calculation**:
```python
lap_data = driver_data[driver_data['lap'] == lap_num]
start_time = pd.to_datetime(lap_data.iloc[0]['timestamp'])
end_time = pd.to_datetime(lap_data.iloc[-1]['timestamp'])
lap_time = (end_time - start_time).total_seconds()
```

---

### Step 3: Corner Detection

```
Input:  Single lap telemetry
Action: Identify cornering zones using multi-signal approach
Output: List of corner zones with entry/apex/exit indices
```

**Detection Algorithm**:

```
1. Calculate absolute values:
   abs_steering = |Steering_Angle|
   abs_lateral_g = |accy_can|

2. Apply thresholds:
   is_cornering = (abs_steering > 30°) AND (abs_lateral_g > 0.8g)

3. Find continuous zones:
   Group consecutive True values in is_cornering

4. Filter by duration:
   Keep zones lasting ≥ 0.5 seconds

5. Merge nearby corners:
   Combine zones with gap < 50 meters
```

**Visual Example**:

```
Distance (m):  0     500    1000   1500   2000   2500   3000   3500
Steering:      ▁▁▁▁▁▁▁▁██████▁▁▁▁██████▁▁▁▁▁▁▁▁███████▁▁▁▁
Lateral G:     ▁▁▁▁▁▁▁▁██████▁▁▁▁██████▁▁▁▁▁▁▁▁███████▁▁▁▁
Cornering:     ▁▁▁▁▁▁▁▁██████▁▁▁▁██████▁▁▁▁▁▁▁▁███████▁▁▁▁
                       Corner1    Corner2         Corner3

Detected: 3 corners
Corner 1: 188m - 612m
Corner 2: 1068m - 1193m
Corner 3: 1785m - 1916m
```

---

### Step 4: Corner Metric Extraction

```
Input:  Corner zone telemetry (entry to exit)
Action: Calculate 9 key metrics
Output: Corner metrics dictionary
```

**Metric Calculation Logic**:

| Metric | Calculation | Example |
|--------|-------------|---------|
| **Entry Point** | First sample in corner zone | Distance: 188m |
| **Apex Point** | Minimum speed in zone | Distance: 507m |
| **Exit Point** | Last sample in corner zone | Distance: 612m |
| **Entry Speed** | Speed at entry point | 185.4 km/h |
| **Apex Speed** | Speed at apex | 114.0 km/h |
| **Exit Speed** | Speed at exit point | 142.8 km/h |
| **Corner Time** | Exit timestamp - entry timestamp | 12.96s |
| **Lateral G Max** | max(abs(accy_can)) | 1.741g |
| **Steering Max** | max(abs(Steering_Angle)) | 71.3° |

**Braking Point Detection**:
```python
# Look back 100 samples before corner entry
lookback = lap_data[corner_start_idx - 100 : corner_start_idx]

# Find where brake pressure exceeds threshold
brake_mask = lookback['pbrake_f'] > 20  # bar

# First brake application
braking_point = lookback[brake_mask].iloc[0]['Laptrigger_lapdist_dls']
```

**Throttle Application Detection**:
```python
# Look from apex onwards
post_apex = corner_data[apex_idx:]

# Find where throttle exceeds 50%
throttle_mask = post_apex['aps'] > 50

# First throttle application
throttle_point = post_apex[throttle_mask].iloc[0]['Laptrigger_lapdist_dls']
```

---

### Step 5: Driver Comparison

```
Input:  Corner metrics for two drivers
Action: Calculate differences and generate insights
Output: Comparison dictionary with coaching recommendations
```

**Comparison Logic**:

```python
# Calculate differences
diff_braking = driver_b['braking_point'] - driver_a['braking_point']
diff_entry_speed = driver_b['entry_speed'] - driver_a['entry_speed']
diff_apex_speed = driver_b['apex_speed'] - driver_a['apex_speed']
diff_exit_speed = driver_b['exit_speed'] - driver_a['exit_speed']
diff_corner_time = driver_b['corner_time'] - driver_a['corner_time']

# Generate insights
if abs(diff_braking) > 5:
    direction = 'later' if diff_braking > 0 else 'earlier'
    insight = f"Driver B brakes {abs(diff_braking):.1f}m {direction}"

if abs(diff_entry_speed) > 2:
    direction = 'more' if diff_entry_speed > 0 else 'less'
    insight = f"Driver B carries {abs(diff_entry_speed):.1f} km/h {direction} entry speed"
```

---

## Processing Performance

### Single Race Breakdown

```
┌──────────────────────────┬───────────┬─────────┐
│ Step                     │ Time (s)  │ Memory  │
├──────────────────────────┼───────────┼─────────┤
│ Load CSV                 │ 1.5       │ 500 MB  │
│ Filter drivers           │ 0.1       │ -       │
│ Identify best laps       │ 0.2       │ -       │
│ Corner detection         │ 0.5       │ 200 MB  │
│ Metric extraction        │ 0.2       │ -       │
│ JSON serialization       │ 0.1       │ -       │
├──────────────────────────┼───────────┼─────────┤
│ TOTAL                    │ 2.5       │ 700 MB  │
└──────────────────────────┴───────────┴─────────┘
```

### Full Dataset Projection

```
10 races × 2.5s = 25 seconds (sequential)
10 races × ~20 drivers = 200 driver analyses
Processing time with parallelization: ~4-5 minutes
Output size: ~1.5 MB JSON (300 KB compressed)
```

---

## Data Flow Diagram

### High-Level Architecture

```
┌─────────────────────┐
│   CSV Files (S3)    │
│  1.6 GB telemetry   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Batch Processor    │
│  (Python + pandas)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   JSON Output       │
│  (S3 or Snowflake)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   FastAPI Backend   │
│  (Real-time query)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  React Dashboard    │
│  (Coaching UI)      │
└─────────────────────┘
```

### API Integration Flow

```
User Request: "Compare Driver 7 vs 13 on Barber Turn 1"
     ↓
Frontend → GET /api/corner-comparison/barber/1/7/13/1
     ↓
Backend → Load cached JSON results
     ↓
Backend → Run compare_drivers(7, 13, corner=1)
     ↓
Backend → Generate coaching insights
     ↓
Backend → Return JSON response
     ↓
Frontend → Display comparison card with recommendations
```

---

## Output Schema Reference

### Race Analysis JSON

```json
{
  "track_name": "barber",
  "race_num": 1,
  "drivers": {
    "<driver_id>": {
      "best_lap_num": 23,
      "best_lap_time_s": 98.03,
      "laps_analyzed": [
        {
          "lap_num": 23,
          "corners": [
            {
              "number": 1,
              "distance_start_m": 188.0,
              "distance_apex_m": 507.0,
              "distance_exit_m": 612.0,
              "entry_speed_kmh": 185.4,
              "apex_speed_kmh": 114.0,
              "exit_speed_kmh": 142.8,
              "corner_time_s": 12.96,
              "lateral_g_max": 1.741,
              "steering_angle_max_deg": 71.3,
              "steering_smoothness": 42.31,
              "braking_point_m": 111.0,
              "brake_pressure_max_bar": 142.3,
              "throttle_application_point_m": 507.0
            }
          ]
        }
      ]
    }
  }
}
```

### Driver Comparison JSON

```json
{
  "track": "barber",
  "race": 1,
  "corner_number": 1,
  "driver_a": 7,
  "driver_b": 13,
  "differences": {
    "braking_point_m": -3.0,
    "entry_speed_kmh": 2.8,
    "apex_speed_kmh": 2.2,
    "exit_speed_kmh": 3.3,
    "corner_time_s": -0.06
  },
  "coaching_insights": [
    "Driver 13 brakes 3.0m earlier (111.0m vs 108.0m)",
    "Driver 13 carries 2.8 km/h less entry speed",
    "Apex speed is 2.2 km/h lower for driver 13"
  ]
}
```

---

## Error Handling

### Common Issues and Mitigations

```
Issue: Corner detection merges chicanes
├─ Symptom: Expected 17 corners, detected 10
├─ Cause: Merge gap too large (50m)
└─ Solution: Reduce merge_gap_m parameter or use manual definitions

Issue: NaN values in metrics
├─ Symptom: Missing brake_pressure_max_bar
├─ Cause: Data gaps in telemetry stream
└─ Solution: Interpolate or use fallback values

Issue: Lap boundary issues
├─ Symptom: Corner crossing start/finish line
├─ Cause: Distance wraps from 3850m to 0m
└─ Solution: Handle wrap-around in distance calculations

Issue: Memory exhausted
├─ Symptom: Process killed during load
├─ Cause: Loading 180MB COTA file
└─ Solution: Use chunked reading or increase available RAM
```

---

## Future Enhancements

### Phase 2: Manual Corner Integration

```
1. Load track_layouts.json
2. Match auto-detected corners to manual definitions
3. Split merged corners using distance ranges
4. Assign official corner numbers
5. Add corner metadata (name, type, gear)
```

### Phase 3: Real-Time Processing

```
1. Stream telemetry data from live timing
2. Pre-compute corner boundaries per track
3. Calculate metrics on-the-fly
4. Push updates to dashboard via WebSocket
5. Generate live coaching insights
```

### Phase 4: Machine Learning

```
1. Train model to predict optimal racing line
2. Classify driver style (aggressive vs smooth)
3. Predict lap time improvement potential
4. Auto-tune detection thresholds per track
5. Generate personalized coaching priorities
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-10
**Status**: Reference for integration team
