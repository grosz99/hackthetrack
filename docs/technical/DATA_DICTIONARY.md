# Data Dictionary - HackTheTrack Racing Data

## Folder Structure

```
data/
├── raw_telemetry/              # Raw sensor data (long format, 11M+ rows per race)
├── processed_telemetry/        # Processed sensor data (wide format, 1M rows per race)
├── lap_timing/                 # Lap time records (36 files)
├── qualifying/                 # Qualifying session results (6 files)
├── race_results/               # Race results organized by type
│   ├── provisional_results/    # Official race results (12 files)
│   ├── analysis_endurance/     # Lap-by-lap with sector times (12 files)
│   └── best_10_laps/          # Top 10 laps per driver (12 files)
└── analysis_outputs/          # Generated analysis results (EDA outputs)
```

## File Types Overview

### 1. Provisional Results (`provisional_results/`)
**Purpose**: Official race results with finishing positions and times

**Key Columns**:
- `POSITION` - Finishing position (1st, 2nd, 3rd, etc.)
- `NUMBER` - Car/Driver number
- `STATUS` - Classification status (Classified, DNF, etc.)
- `LAPS` - Total laps completed
- `TOTAL_TIME` - Total race time
- `GAP_FIRST` - Time gap to 1st place
- `GAP_PREVIOUS` - Time gap to car ahead
- `FL_LAPNUM` - Lap number of fastest lap
- `FL_TIME` - Fastest lap time
- `FL_KPH` - Fastest lap speed
- `CLASS` - Race class (Am)
- `VEHICLE` - Car model (Toyota GR86)

**Use for**:
- Defining performance groups (Top 3, Middle 5, Bottom 3)
- Overall race performance
- Gap analysis

---

### 2. Analysis Endurance (`analysis_endurance/`)
**Purpose**: Lap-by-lap data with SECTION TIMES for each corner/segment

**Key Columns**:
- `NUMBER` - Car number
- `DRIVER_NUMBER` - Driver identifier
- `LAP_NUMBER` - Lap number
- `LAP_TIME` - Total lap time
- `LAP_IMPROVEMENT` - Improvement vs previous lap

**Section Times** (CRITICAL FOR CORNER ANALYSIS):
- `S1`, `S2`, `S3` - Main sector times (3 sectors per track)
- `S1_SECONDS`, `S2_SECONDS`, `S3_SECONDS` - Sector times in seconds
- `S1_IMPROVEMENT`, `S2_IMPROVEMENT`, `S3_IMPROVEMENT` - Sector improvements

**Intermediate Times** (MORE GRANULAR):
- `IM1a_time`, `IM1a_elapsed` - Intermediate point 1a
- `IM1_time`, `IM1_elapsed` - Intermediate point 1
- `IM2a_time`, `IM2a_elapsed` - Intermediate point 2a
- `IM2_time`, `IM2_elapsed` - Intermediate point 2
- `IM3a_time`, `IM3a_elapsed` - Intermediate point 3a
- `FL_time`, `FL_elapsed` - Finish line time/elapsed

**Other Performance Data**:
- `KPH` - Average lap speed
- `TOP_SPEED` - Top speed on that lap
- `FLAG_AT_FL` - Track conditions (FCY = Full Course Yellow, GREEN = racing, etc.)
  - **⚠️ IMPORTANT**: Exclude laps where `FLAG_AT_FL = 'FCY'` from analysis (caution laps are slower)
- `PIT_TIME` - Pit stop time if applicable
- `CROSSING_FINISH_LINE_IN_PIT` - Whether in pit lane

**Calculated Metrics** (can be derived from this data):
- `running_position` - Position at end of each lap (rank drivers by ELAPSED time)
- `position_change` - Positions gained/lost from previous lap
- `avg_position_change_per_lap` - In-race racecraft metric

**Use for**:
- **Corner-by-corner performance** (S1, S2, S3 represent different corner groups)
- **Intermediate segment analysis** (IM points = specific corners/sections)
- **Consistency analysis** (lap-to-lap variation)
- **Tire degradation** (lap time evolution over stint)
- **Track condition impact** (FCY laps vs green flag)
- **In-race racecraft** (lap-by-lap position changes - see POSITION_CHANGES_CALCULATION.md)

---

### 3. Best 10 Laps (`best_10_laps/`)
**Purpose**: Each driver's 10 fastest laps of the race

**Key Columns**:
- `NUMBER` - Car number
- `VEHICLE` - Car model
- `CLASS` - Race class
- `TOTAL_DRIVER_LAPS` - Total laps completed
- `BESTLAP_1` through `BESTLAP_10` - 10 fastest lap times
- `BESTLAP_1_LAPNUM` through `BESTLAP_10_LAPNUM` - Lap numbers when achieved
- `AVERAGE` - Average of best 10 laps

**Use for**:
- **Peak performance capability** (BESTLAP_1 = absolute best lap in race)
- **Peak performance consistency** (std dev of best 10 laps)
- **Race pace vs ultimate pace** (average lap vs best lap)
- **NOT for qualifying pace** - use actual `qualifying/` data instead

---

### 4. Lap Timing (`lap_timing/`)
**Purpose**: Simple lap time records (appears to be telemetry metadata)

**Columns**:
- `lap` - Lap number
- `vehicle_number` - Car identifier
- `timestamp` - When lap completed
- `meta_event`, `meta_session`, `meta_source` - Metadata

**Note**: This appears to be metadata rather than actual lap times. The `analysis_endurance` file has the actual lap times.

**Use for**:
- Possibly linking to other telemetry data
- Less useful for skill discovery

---

### 5. Raw Telemetry (`raw_telemetry/`)
**Purpose**: Raw sensor data in LONG format (pre-processing)

**File Size**: ~11.5 million rows per race

**Status**: ⚠️ **NOT NEEDED FOR ANALYSIS** - This is the raw input to create `processed_telemetry`

**Note**: Use `processed_telemetry/` instead (already pivoted to wide format)

---

### 6. Processed Telemetry (`processed_telemetry/`)
**Purpose**: Telemetry data pivoted to WIDE format (one row per timestamp)

**File Size**: ~1 million rows per race (10x smaller than raw)

**Format**: Wide format - all sensors in columns

**Key Columns**:
- `vehicle_number` - Car identifier
- `lap` - Lap number
- `timestamp` - Timestamp
- `Laptrigger_lapdist_dls` - Distance along track (meters)
- `Steering_Angle` - Steering input (degrees)
- `VBOX_Lat_Min`, `VBOX_Long_Minutes` - GPS position
- `accx_can` - Longitudinal G-force
- `accy_can` - Lateral G-force
- `aps` - Throttle position (%)
- `gear` - Current gear
- `nmot` - Engine RPM
- `pbrake_f` - Front brake pressure
- `pbrake_r` - Rear brake pressure
- `speed` - Vehicle speed

**Example Data**:
```
vehicle_number,lap,timestamp,speed,accx_can,accy_can,aps,pbrake_f,Steering_Angle
0,2,2025-09-05T00:27:38.589Z,45.2,-0.04,0.002,14.17,0.0,3.9
```

**Use for**:
- Easier to work with than raw format
- Time-series analysis
- Corner-by-corner telemetry analysis
- G-force analysis in specific corners
- Braking performance analysis
- **For advanced skill discovery after initial EDA**

---

### 7. Qualifying (`qualifying/`)
**Purpose**: Qualifying session results

**Available Files**: 6 files (COTA R1/R2, Sebring R1/R2, Sonoma R1/R2)

**Key Columns**:
- `POS` - Qualifying position
- `NUMBER` - Car number
- `LAP` - Lap number of fastest time
- `TIME` - Qualifying lap time
- `GAP_FIRST` - Gap to pole position
- `GAP_PREVIOUS` - Gap to car ahead
- `KPH` - Average speed
- `LAPS` - Total laps completed in qualifying
- `TEAM` - Team name
- `CLASS` - Race class
- `VEHICLE` - Car model
- `DRIVER_FIRSTNAME`, `DRIVER_SECONDNAME` - Driver name

**Example Data**:
```
POS,NUMBER,LAP,TIME,GAP_FIRST,KPH
1,46,3,2:26.900,-,134.1
2,7,4,2:26.939,+0.039,134.1
```

**Use for**:
- **"Qualifying pace" skill** - Ultimate one-lap speed
- **"Racecraft" skill** - Positions gained (quali position vs race finish)
- Comparing qualifying vs race performance

**Note**: Only available for COTA, Sebring, and Sonoma (6 of 12 races)

---

### 8. Analysis Outputs (`analysis_outputs/`)
**Purpose**: Generated analysis, metrics, and EDA results

**Status**: ⚠️ **LEGACY/JUNK FROM PREVIOUS ANALYSIS** - Can be deleted/regenerated

**Current Contents**:
- Old EDA attempts with incorrect methodology
- Metrics calculated before data dictionary was complete
- Legacy coaching reports

**Action**: Clean up and regenerate with corrected EDA approach

---

## Racing Domain Knowledge

### Track Sections Explained

Most tracks are divided into **3 main sectors** (S1, S2, S3):

**S1 (Sector 1)** - Typically includes:
- Start/finish straight
- First heavy braking zone
- Initial corner sequence
- **Skills tested**: Braking precision, turn-in, first-lap aggression

**S2 (Sector 2)** - Typically includes:
- Middle technical sections
- Combination corners
- Elevation changes
- **Skills tested**: Mid-corner speed, car balance, technical precision

**S3 (Sector 3)** - Typically includes:
- Final corners before finish
- Exit onto main straight
- Often determines next lap's S1
- **Skills tested**: Exit traction, throttle application, carrying momentum

### Intermediate Points (IM)

The intermediate points (IM1a, IM1, IM2a, IM2, IM3a) are **specific timing beacons** placed at critical corners or sections. These allow analysis of:
- Specific corner performance
- Entry vs exit speed
- Line choice through complex sections

---

## Performance Groups (CORRECTED)

For skill discrimination analysis, we should use:

1. **Top 3** - Positions 1, 2, 3 (winners)
2. **Middle 5** - Positions 4-8 (mid-pack competitive)
3. **Bottom 3** - Last 3 finishers in class (struggling drivers)

This gives us clear separation between skill levels.

---

## Key Metrics to Discover

### 1. Corner Entry/Braking
- S1 times (usually heavy braking into turn 1)
- First IM point times
- Improvement in S1 over race (learning/confidence)

### 2. Mid-Corner Speed/Technical Precision
- S2 times (technical sections)
- Middle IM points
- Consistency in technical sections

### 3. Corner Exit/Traction
- S3 times (exit-critical sections)
- Final IM points
- Top speed achieved (indicates good exit)

### 4. Qualifying Pace
- BESTLAP_1 vs field average
- Gap between best and average lap
- Peak performance capability

### 5. Consistency
- Standard deviation of lap times (excluding outliers)
- Coefficient of variation
- Lap-to-lap variation

### 6. Tire Management
- Lap time degradation over stint
- Early pace vs late pace
- Ability to maintain speed on old tires

### 7. Race Craft (if qualifying data available)
- Positions gained from start to finish
- Performance in traffic vs clean air
- First lap performance

---

## Data Quality Considerations

### Track Variability
- **Barber** - 75% sections discriminate (good data quality)
- **Sebring** - 50% sections discriminate
- **VIR** - 50% sections discriminate
- **COTA** - 8.3% sections discriminate (possible data quality issue?)
- **Road America** - 0% sections discriminate (DATA ISSUE - investigate)
- **Sonoma** - 25% sections discriminate

### Next Steps for EDA

1. **Verify S1, S2, S3 data** across all tracks
2. **Map IM points to actual corners** (need track maps)
3. **Analyze by performance groups**: Top 3, Middle 5, Bottom 3
4. **Test discrimination at SECTOR level** (S1, S2, S3) not just intermediate points
5. **Identify skills that work across at least 4 of 6 tracks**
6. **Account for track-specific characteristics** (some tracks favor certain skills)

---

## Questions to Answer

1. Which **sectors** (S1, S2, S3) discriminate most consistently?
2. Which **intermediate points** represent key corners?
3. Does **braking** (S1) matter more than **exit** (S3)?
4. Is **consistency** (lap time std dev) a real discriminator?
5. Does **tire management** (degradation rate) separate winners from losers?
6. Can we identify **qualifying pace** as distinct from race pace?

---

## Expected Skill Categories

Based on racing domain knowledge, we expect to find:

1. **Heavy Braking Mastery** - Performance in S1/first corners
2. **Technical Precision** - Performance in S2/mid-track sections
3. **Exit Traction** - Performance in S3/final corners
4. **Qualifying Pace** - Ultimate one-lap speed (BESTLAP_1)
5. **Consistency** - Lap time variation (std dev)
6. **Tire Management** - Pace degradation over stint

Let the data validate or refute these hypotheses!
