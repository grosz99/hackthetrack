# Data Structures - Circuit Fit Analysis

## 📋 Overview
This document defines all data formats available from GR Cup racing data and how they should be structured for analysis.

## 🗄️ Core Data Sources

### Actual Repository Structure
```
data/
├── analysis_outputs/      # Processed analytics and reports
├── lap_timing/           # Lap time data by race
├── qualifying/           # Qualifying session data
└── race_results/         # Race result files
    ├── analysis_endurance/     # Endurance race analysis
    ├── best_10_laps/          # Top 10 lap compilations
    └── provisional_results/    # Official race results
```

### 1. Race Results Data
**Location**: `data/race_results/provisional_results/`  
**File Format**: CSV  
**Example**: `03_Provisional_Results_Race_1_Anonymized.CSV`

```python
{
    'Position': int,          # Final finishing position
    'Car Number': str,        # Vehicle number (e.g., "86", "42")
    'Driver Name': str,       # Driver identifier
    'Laps': int,             # Total laps completed
    'Total Time': str,        # Race duration (HH:MM:SS.mmm)
    'Best Lap': str,         # Fastest lap time (MM:SS.mmm)
    'Gap': str,              # Time behind leader
    'Class': str             # Racing class/category
}
```

**Usage**: 
- Map performance groups (top-3, mid-pack, back-of-field)
- Identify target drivers for comparison
- Validate correlation between features and finishing position

---

### 2. Lap Time Data
**Location**: `data/lap_timing/`  
**File Format**: CSV  
**Example**: `R1_barber_lap_time.csv`

```python
{
    'vehicle_id': int,        # Unique vehicle identifier in telemetry system
    'vehicle_number': str,    # Car number matching race results
    'lap_number': int,        # Lap count (1, 2, 3, ...)
    'lap_time': float,        # Lap time in seconds
    'session': str,           # 'Race', 'Qualifying', 'Practice'
    'driver_name': str,       # Driver identifier
    'timestamp': datetime     # When lap was completed
}
```

**Key Relationships**:
```python
# Map vehicle_number → vehicle_id for telemetry joins
vehicle_mapping = lap_time_df[['vehicle_number', 'vehicle_id']].drop_duplicates()

# Calculate lap-to-lap consistency
consistency = lap_time_df.groupby('vehicle_id')['lap_time'].std()
```

**Usage**:
- Join race results to telemetry data
- Calculate pace consistency
- Identify tire degradation patterns
- Detect outlier laps (incidents, traffic)

---

### 3. Telemetry Data
**File Format**: CSV (Large: 100MB-2GB per race)  
**Example**: `R1_barber_telemetry_data.csv`

```python
{
    'vehicle_id': int,        # Links to lap_time.vehicle_id
    'lap_number': int,        # Current lap
    'timestamp': float,       # Time within lap (seconds from lap start)
    'distance': float,        # Distance traveled on track (meters)
    'speed': float,          # Current speed (mph or km/h)
    'throttle': float,       # Throttle position (0.0-1.0)
    'brake': float,          # Brake pressure (0.0-1.0)
    'gear': int,             # Current gear (1-6)
    'rpm': int,              # Engine RPM
    'steering_angle': float  # Steering input (degrees, if available)
}
```

**Sampling Rate**: Typically 10-100 Hz (10-100 readings per second)

**Critical Notes**:
- Data is **massive** - filter before loading full dataset
- Pre-filter to specific cars and laps when possible
- Consider downsampling to 10 Hz for analysis

**Example Filtering**:
```python
# Only load top-3 finishers, laps 5-15 (representative racing laps)
top_3_vehicle_ids = [12, 45, 67]  # From race results
chunk_filter = (telemetry_df['vehicle_id'].isin(top_3_vehicle_ids)) & \
               (telemetry_df['lap_number'].between(5, 15))
```

**Usage**:
- Extract corner-specific metrics
- Identify braking points and throttle application
- Calculate apex speeds
- Detect driving style differences

---

### 4. Section Time Data
**File Format**: CSV  
**Example**: `R1_barber_section_times.csv`

```python
{
    'vehicle_id': int,
    'lap_number': int,
    'section_number': int,    # Corner/sector identifier (1, 2, 3, ...)
    'section_time': float,    # Time to complete section (seconds)
    'section_name': str,      # Optional: "Turn 1", "Sector 2", etc.
    'distance_start': float,  # Where section begins (meters)
    'distance_end': float     # Where section ends (meters)
}
```

**Track Section Definitions**:
Different tracks have different section counts:
- **Barber**: 17 corners, 5 sectors
- **Sonoma**: 12 corners, 3 sectors  
- **Road America**: 14 corners, 4 sectors

**Usage**:
- Compare corner-by-corner performance
- Identify specific weak/strong corners
- Generate targeted practice recommendations
- Much faster than analyzing full telemetry

---

### 5. Weather Data
**File Format**: CSV  
**Example**: `R1_barber_weather.csv`

```python
{
    'timestamp': datetime,
    'temperature': float,     # Track temp (°F or °C)
    'air_temp': float,       # Ambient temp
    'humidity': float,       # Percentage
    'wind_speed': float,     # mph or km/h
    'wind_direction': str,   # Cardinal direction
    'track_condition': str   # 'Dry', 'Wet', 'Damp'
}
```

**Usage**:
- Contextualize performance variations
- Identify weather-dependent driving styles
- Filter to comparable conditions

---

## 🔗 Data Relationships

```
Race Results (Position, Car Number)
    ↓
Lap Time Data (vehicle_number → vehicle_id)
    ↓
Telemetry Data (vehicle_id, lap_number, timestamp)
    ↓
Section Times (vehicle_id, lap_number, section_number)
```

**Critical Join Keys**:
1. `vehicle_number` (Race Results) → `vehicle_number` (Lap Time)
2. `vehicle_id` (Lap Time) → `vehicle_id` (Telemetry)
3. `vehicle_id`, `lap_number` (Telemetry) → (Section Times)

---

## 📊 Recommended Data Schema for Analysis

### Processed Lap Summary Table
```python
{
    'lap_id': str,              # Unique: f"{vehicle_id}_{lap_number}"
    'vehicle_id': int,
    'vehicle_number': str,
    'driver_name': str,
    'lap_number': int,
    'lap_time': float,
    'finishing_position': int,   # From race results
    'performance_group': str,    # 'top_3', 'mid_pack', 'back_field'
    
    # Aggregate metrics (from telemetry)
    'avg_speed': float,
    'max_speed': float,
    'total_braking_time': float,
    'avg_throttle': float,
    
    # Consistency metrics
    'brake_consistency': float,  # Std dev of brake points
    'throttle_consistency': float,
    'corner_entry_speed_var': float,
    
    # Tire degradation indicators
    'lap_delta_from_best': float,
    'brake_pressure_avg': float
}
```

### Corner Performance Table
```python
{
    'corner_id': str,           # f"{vehicle_id}_{lap_number}_{section_number}"
    'vehicle_id': int,
    'lap_number': int,
    'corner_number': int,
    'corner_name': str,         # "Turn 1", "Turn 5-6 Complex"
    
    # Section time
    'section_time': float,
    
    # Telemetry-derived metrics
    'entry_speed': float,       # Speed at corner entry
    'apex_speed': float,        # Speed at apex
    'exit_speed': float,        # Speed at corner exit
    'min_speed': float,         # Minimum speed in corner
    
    'braking_point': float,     # Distance where braking starts
    'brake_pressure_max': float,
    'brake_duration': float,
    
    'throttle_application_point': float,  # Distance where throttle applied
    'time_to_full_throttle': float,
    
    # Comparison metrics
    'time_vs_winner': float,    # Delta to fastest driver this corner
    'time_vs_avg': float        # Delta to field average
}
```

---

## 🎯 Data Quality Considerations

### Lap Filtering Rules
**Exclude these laps from analysis**:
```python
def is_valid_racing_lap(lap):
    # Lap 1: Formation lap/race start chaos
    if lap['lap_number'] == 1:
        return False
    
    # Last lap: Often incomplete/cooldown
    if lap['lap_number'] == lap['total_laps']:
        return False
    
    # Outlier lap times (>107% of best lap = incident/traffic)
    if lap['lap_time'] > lap['best_lap_time'] * 1.07:
        return False
    
    # Incomplete telemetry data
    if lap['telemetry_points'] < expected_points * 0.90:
        return False
    
    return True
```

### Telemetry Cleaning
```python
# Remove impossible values
telemetry['throttle'] = telemetry['throttle'].clip(0, 1)
telemetry['brake'] = telemetry['brake'].clip(0, 1)
telemetry['speed'] = telemetry['speed'].clip(0, 200)  # mph

# Interpolate missing values (gaps < 0.5 seconds)
telemetry = telemetry.interpolate(method='linear', limit=5)

# Remove telemetry from pit lane
telemetry = telemetry[telemetry['distance'] <= track_length]
```

---

## 💾 Storage Recommendations

### SQLite Schema
```sql
CREATE TABLE race_results (
    result_id INTEGER PRIMARY KEY,
    race_id TEXT,
    vehicle_number TEXT,
    driver_name TEXT,
    finishing_position INTEGER,
    best_lap_time REAL,
    total_laps INTEGER
);

CREATE TABLE lap_times (
    lap_id TEXT PRIMARY KEY,
    vehicle_id INTEGER,
    vehicle_number TEXT,
    lap_number INTEGER,
    lap_time REAL,
    session TEXT,
    timestamp DATETIME,
    FOREIGN KEY (vehicle_number) REFERENCES race_results(vehicle_number)
);

CREATE TABLE corner_performance (
    corner_id TEXT PRIMARY KEY,
    vehicle_id INTEGER,
    lap_number INTEGER,
    corner_number INTEGER,
    section_time REAL,
    entry_speed REAL,
    apex_speed REAL,
    exit_speed REAL,
    braking_point REAL,
    throttle_point REAL,
    time_vs_winner REAL,
    FOREIGN KEY (vehicle_id) REFERENCES lap_times(vehicle_id)
);

CREATE INDEX idx_vehicle_lap ON corner_performance(vehicle_id, lap_number);
CREATE INDEX idx_corner ON corner_performance(corner_number);
```

---

## 🔄 Data Pipeline Flow

1. **Load Race Results** → Identify performance groups
2. **Load Lap Times** → Map vehicle IDs, calculate consistency
3. **Filter Telemetry** → Load only relevant vehicles/laps
4. **Process Telemetry** → Extract corner metrics
5. **Join Section Times** → Add granular corner data
6. **Create Analytics Tables** → Store processed metrics
7. **Generate Features** → Run feature engineering pipeline

---

## 📝 Quick Reference

**Data Sizes** (typical race):
- Race Results: ~50 rows, <10 KB
- Lap Times: ~1,500 rows, ~100 KB
- Telemetry: ~5M rows, 500 MB - 2 GB
- Section Times: ~25,000 rows, ~2 MB

**Critical Fields for Joins**:
- `vehicle_number` (race results ↔ lap times)
- `vehicle_id` (lap times ↔ telemetry)
- `lap_number` (all tables)

**Performance Groups**:
- Top 3: Positions 1-3
- Mid Pack: Positions 4-12
- Back Field: Positions 13+

---

Ready to move to Feature Engineering? See `02_FEATURE_ENGINEERING.md`
