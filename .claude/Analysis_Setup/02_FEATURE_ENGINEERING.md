# Feature Engineering - Circuit Fit Analysis

## 🎯 Philosophy: Actionable Over Aggregate

Every feature must answer: **"What specific technique should the driver change?"**

❌ Bad: "Overall corner performance: 0.72"  
✅ Good: "Turn 3 entry speed 8mph below winners - brake 15m later"

---

## 📊 Feature Categories

### 1. Corner-Specific Metrics
**Goal**: Identify exact locations where time is lost

#### A. Corner Entry
Extract precise entry metrics for each corner including entry speed, braking initiation point, peak brake pressure, and time spent braking.

**Key Metrics:**
- `entry_speed` - Speed when driver first brakes (mph)
- `braking_point` - Distance before apex where braking starts (meters)
- `max_brake_pressure` - Peak brake application (0-1)
- `brake_duration` - Total time on brakes (seconds)
- `brake_consistency` - Standard deviation of brake pressure

**Actionable Output Example**:
> "Turn 7: You brake 12m earlier than winners (88m vs 76m from apex). Try carrying more speed and braking at the 80m board."

---

#### B. Apex Performance
Measure apex execution quality - critical for optimal racing line, speed carried through corner, and setup compromise.

**Key Metrics:**
- `apex_speed` - Average speed in 5m window around apex (mph)
- `min_speed` - Minimum speed in corner (mph)
- `apex_throttle` - Throttle position at apex (0-1)
- `min_speed_location` - Distance where minimum speed occurs relative to geometric apex (meters)

**Actionable Output Example**:
> "Turn 12 apex: 62mph vs winners' 65mph. Your minimum speed occurs 3m early - rotate car more at entry to apex later."

---

#### C. Corner Exit
Measure exit execution and acceleration quality - most important for lap time on tracks with long straights.

**Key Metrics:**
- `throttle_application_point` - Distance after apex where throttle first applied (meters)
- `throttle_application_speed` - Speed when throttle first applied (mph)
- `time_to_full_throttle` - Time from initial to full throttle (seconds)
- `distance_to_full_throttle` - Distance traveled to reach full throttle (meters)
- `exit_speed` - Speed at end of exit zone, 100m after apex (mph)
- `throttle_modulation` - Standard deviation of throttle in exit zone (indicates traction issues)

**Actionable Output Example**:
> "Turn 8 exit: You apply throttle 0.3s earlier than winners (1.2s vs 1.5s after apex) but exit 4mph slower (87mph vs 91mph). You're getting wheelspin - delay initial throttle by 0.2s and reduce aggression."

---

### 2. Consistency Metrics
**Goal**: Identify inconsistent technique costing lap time

Measure how repeatable the driver's technique is. Inconsistency indicates uncertain technique, poor reference points, or confidence issues.

**Key Metrics:**
- `lap_time_std` - Standard deviation of lap times
- `lap_time_coefficient_of_variation` - Lap time std / mean
- `corner_N_consistency` - Std dev of section time for each corner
- `corner_N_braking_consistency` - Std dev of braking point for each corner

**Actionable Output Example**:
> "Your most inconsistent corner is Turn 5 (braking point varies by 14m across laps). Establish a consistent reference point: brake at the 100m board every lap. Your best lap braked at 95m, worst at 109m."

---

### 3. Tire Degradation Indicators
**Goal**: Detect tire wear patterns and recommend management strategy

Track how performance degrades over stint by dividing into thirds (early/mid/late laps) and comparing.

**Key Metrics:**
- `lap_time_early/mid/late` - Average lap time in each stint third
- `degradation_rate` - Lap time increase per lap (seconds/lap)
- `brake_pressure_drop` - Reduction in brake pressure over stint (indicates front tire wear)
- `corner_N_speed_drop` - Apex speed reduction per corner over stint

**Actionable Output Example**:
> "Laps 8-12: Brake pressure drops 15% vs Lap 3, indicating earlier tire wear than top 3 finishers. Turns 1, 5, and 11 lose 3-4mph apex speed. Try reducing initial brake force by 8% to preserve front tires."

---

### 4. Racecraft Metrics
**Goal**: Measure wheel-to-wheel racing ability

Evaluate racing in traffic vs clean air, including overtake success and defensive effectiveness.

**Key Metrics:**
- `lap_time_in_traffic` - Average lap time when gap to car ahead < 1.5s
- `lap_time_clean_air` - Average lap time when gap > 3.0s  
- `traffic_penalty` - Difference between traffic and clean air lap times
- `overtakes_completed` - Number of positions gained
- `positions_lost` - Number of positions lost
- `racecraft_ratio` - Overtakes / (overtakes + losses)
- `overtake_opportunity_zones` - Which corners overtakes typically happen

**Actionable Output Example**:
> "You lose 0.6s per lap in traffic vs clean air (field average: 0.3s). You completed 2 overtakes, both in Turn 1 braking zone. Practice later braking under pressure - your braking point moves 8m earlier when following."

---

### 5. Track-Specific Style Metrics
**Goal**: Identify if driver's style suits track characteristics

Match driver style to track requirements. Tracks categorized as:
- High-speed flow (Road America, Barber)
- Technical slow-speed (Sonoma)  
- Mixed (Sebring)

**Key Metrics:**
- `high_speed_comfort` - Average time delta in corners > 80mph
- `technical_precision` - Average time delta in corners < 50mph
- `exit_prioritization` - Exit speed delta in corners before long straights (>300m)
- `braking_confidence` - Braking point delta in heavy braking zones (>2.0s brake duration)

**Actionable Output Example**:
> "Barber rewards high-speed flow. Your high-speed corners (T4, T9, T13) average -0.15s vs winners. Low-speed technical corners (T5, T15) you're only -0.04s behind. Focus practice on carrying more speed through fast corners - you're lifting where winners stay flat."

---

## 🎯 Feature Priority Framework

Rank features by:
1. **Time Impact** - How much lap time does this cost?
2. **Actionability** - Can the driver change this?
3. **Consistency** - Is this a repeatable issue or one-off?

Algorithm prioritizes opportunities by `time_loss * actionability_score`, sorting from highest impact to lowest.

---

## 📋 Complete Feature List

### Must-Have Features (High Discrimination Power)
These should differentiate top-3 from mid-pack:

**Corner Entry:**
- `braking_point_vs_winner` (meters)
- `entry_speed_vs_winner` (mph)
- `max_brake_pressure_vs_winner`

**Apex:**
- `apex_speed_vs_winner` (mph)
- `min_speed_location` (distance from geometric apex)

**Corner Exit:**
- `throttle_application_point` (meters after apex)
- `exit_speed_vs_winner` (mph)
- `time_to_full_throttle` (seconds)

**Consistency:**
- `braking_point_std_dev` (meters)
- `lap_time_coefficient_of_variation`
- `corner_time_consistency` (per corner)

**Tire Degradation:**
- `brake_pressure_degradation_rate` (%/lap)
- `apex_speed_degradation_rate` (mph/lap)
- `lap_time_degradation_rate` (s/lap)

### Optional Features (Context-Dependent)
Test these for statistical significance:

**Racecraft:**
- `traffic_penalty` (seconds)
- `overtake_success_rate`
- `defensive_effectiveness`

**Style Fit:**
- `high_speed_corner_delta` (vs winners)
- `technical_corner_delta` (vs winners)
- `brake_heavy_corner_confidence`

---

## 🔬 Feature Validation Process

Before including any feature in the final system, validate that it actually discriminates performance groups using ANOVA and effect size (Cohen's d).

**Decision Criteria:**
- p-value < 0.05 AND |effect_size| > 0.5 → **KEEP**
- p-value < 0.10 → **INVESTIGATE** 
- Otherwise → **DROP**

Only keep features with strong statistical discrimination power.

---

## 💾 Feature Storage Schema

**Reference**: `data/analysis_outputs/` in your GitHub repo

Recommended SQLite table structure:

```sql
CREATE TABLE driver_corner_features (
    feature_id TEXT PRIMARY KEY,
    vehicle_id INTEGER,
    driver_name TEXT,
    lap_number INTEGER,
    corner_number INTEGER,
    
    -- Entry features
    entry_speed REAL,
    braking_point REAL,
    max_brake_pressure REAL,
    brake_duration REAL,
    
    -- Apex features
    apex_speed REAL,
    min_speed REAL,
    min_speed_location REAL,
    
    -- Exit features
    throttle_application_point REAL,
    time_to_full_throttle REAL,
    exit_speed REAL,
    
    -- Comparison to winners
    entry_speed_vs_winner REAL,
    apex_speed_vs_winner REAL,
    exit_speed_vs_winner REAL,
    braking_point_vs_winner REAL,
    section_time_vs_winner REAL,
    
    -- Metadata
    finishing_position INTEGER,
    performance_group TEXT,
    timestamp DATETIME
);
```

---

## 🚀 Implementation Steps

1. **Load telemetry data** for all drivers in race
2. **Define corner zones** from track map (see `06_CIRCUIT_KNOWLEDGE.md`)
3. **Extract raw metrics** (speeds, braking points, throttle application)
4. **Calculate comparison metrics** vs race winner
5. **Compute consistency metrics** across laps
6. **Detect tire degradation** over stint
7. **Validate features** for discrimination power (ANOVA, effect size)
8. **Store processed features** in database (`data/analysis_outputs/`)
9. **Generate diagnostics** from features

---

## ✅ Success Criteria

A good feature must:
1. ✅ **Discriminate** performance (p < 0.05, effect > 0.5)
2. ✅ **Be actionable** (driver can change it)
3. ✅ **Be specific** (corner-level, not track-level)
4. ✅ **Include comparison** (vs winner, vs average)
5. ✅ **Suggest action** (what to do differently)

---

Ready for statistical validation? See `03_STATISTICAL_VALIDATION.md`
