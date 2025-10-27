# Metrics Validation Report

**Date**: 2025-10-26
**Test Coverage**: All 12 races (Barber, COTA, Road America, Sebring, Sonoma, VIR × 2 each)
**Metrics Tested**: 5 representative variables from VARIABLE_DEF.md

---

## Executive Summary

✅ **ALL 12 races have qualifying data** (not just 6 as initially thought!)

📊 **Test Results Summary**:
- ✅ **Variable 1 (Qualifying Pace)**: 100% success (36/36 drivers tested)
- ⚠️ **Variable 4 (Top Speed)**: 67% success (24/36) - missing TOP_SPEED data at Sebring & VIR
- ✅ **Variable 8 (S1 Entry Performance)**: 100% success (36/36)
- ✅ **Variable 21 (Position Changes)**: 100% success (36/36) - NEW metric works perfectly!
- ⚠️ **Variable 24 (Positions Gained)**: 75% success (27/36) - data type issue at 3 races

---

## Data Quality Findings

### ✅ What Works Perfectly

#### 1. Qualifying Data
- **Status**: ✅ Available for ALL 12 races
- **Files**: Barberrd1Qualifying.csv, Cotard1Qualifying.csv, etc.
- **Columns**: POS, NUMBER, LAP, TIME, GAP_FIRST, GAP_PREVIOUS, KPH
- **Delimiter**: Semicolon (`;`)
- **Quality**: Excellent - all drivers have valid times

**Examples**:
```
barber_r1: Driver 13 qualified P1 with 1:36.926
cota_r1: Driver 46 qualified P1 with 2:26.900
sonoma_r1: Driver 46 qualified P1 with 1:51.266
```

#### 2. FCY Filtering
- **Status**: ✅ Working perfectly
- **Column**: `FLAG_AT_FL` in analysis_endurance
- **Values**: 'FCY' (Full Course Yellow) vs empty/other
- **FCY Lap Counts**:
  - Barber R1: 44 FCY laps (out of 579 total)
  - Barber R2: 0 FCY laps (clean race!)
  - COTA R1: 89 FCY laps
  - COTA R2: 124 FCY laps (heavy caution)
  - Road America R1: 56 FCY laps
  - Sonoma R2: 109 FCY laps

**Impact**: FCY filtering is critical - some races had 25%+ caution laps

#### 3. Sector Performance (S1, S2, S3)
- **Status**: ✅ Working perfectly
- **Columns**: `S1_SECONDS`, `S2_SECONDS`, `S3_SECONDS`
- **Quality**: All races have clean sector data
- **Precision**: Sub-second timing accuracy

**Examples** (Barber R1, S1 times):
```
Driver 13: 27.08s (winner)
Driver 22: 27.03s (field best!)
Driver 72: 27.13s
```

#### 4. Position Changes (ELAPSED tracking)
- **Status**: ✅ Working perfectly (after column name fix)
- **Column**: ` ELAPSED` (note: has leading space!)
- **Format**: Cumulative elapsed time as "M:SS.mmm"
- **Calculation**: Works as designed in POSITION_CHANGES_CALCULATION.md

**Examples** (position changes per lap):
```
COTA R2:
  Driver 13: +0.364 positions/lap (great racecraft!)
  Driver 16: +0.417 positions/lap
Road America R1:
  Driver 55: +0.462 positions/lap (P7 → P1, gained 6 positions)
  Driver 13: +0.538 positions/lap (P10 → P3, gained 7 positions)
```

---

### ⚠️ Data Quality Issues Found

#### Issue 1: TOP_SPEED Missing at Sebring & VIR

**Affected Races**: sebring_r1, sebring_r2, vir_r1, vir_r2 (4 of 12 races)

**Symptoms**:
```
Driver 13 (Sebring R1): TOP_SPEED = NaN
Result: nan / nan = nan
```

**Root Cause**: TOP_SPEED column exists but contains NaN values for all drivers

**Impact**:
- Variable 4 (Top Speed) cannot be calculated
- Related variables affected: None (TOP_SPEED is only used in Var 4)

**Workaround**:
- Skip Variable 4 for Sebring & VIR races
- Use remaining 23 variables for factor analysis on those races

**Recommendation**:
- Check if TOP_SPEED can be derived from telemetry data for these tracks
- Or exclude Variable 4 from cross-track analysis (not critical for skill discovery)

---

#### Issue 2: Qualifying POS Data Type Mismatch

**Affected Races**: roadamerica_r2, vir_r1, vir_r2 (3 of 12 races)

**Symptoms**:
```python
ERROR: Unknown format code 'd' for object of type 'float'
```

**Root Cause**:
- In most races, qualifying `POS` is integer (1, 2, 3...)
- In 3 races, `POS` appears to be float (1.0, 2.0, 3.0...)
- Python format string uses `{positions_gained:+d}` expecting int

**Impact**: Variable 24 (Positions Gained) calculation crashes

**Fix Applied** (in test script):
```python
# Before (fails):
return positions_gained, f"OK: Started P{qual_position}, finished P{race_finish} = {positions_gained:+d}"

# After (works):
return positions_gained, f"OK: Started P{int(qual_position)}, finished P{int(race_finish)} = {int(positions_gained):+d}"
```

**Recommendation**: Cast to int in VARIABLE_DEF.md Variable 24 function

---

#### Issue 3: Column Names with Leading Spaces

**Affected Files**: analysis_endurance/*.csv

**Columns with spaces**:
```
' DRIVER_NUMBER'
' LAP_NUMBER'
' LAP_TIME'
' ELAPSED'  <-- Critical for Variable 21!
' S1', ' S2', ' S3'
' KPH'
' HOUR'
```

**Impact**:
- Accessing `endurance['ELAPSED']` fails (KeyError)
- Must use `endurance[' ELAPSED']` or strip columns first

**Fix Applied**:
```python
endurance = pd.read_csv(path, delimiter=';')
endurance.columns = endurance.columns.str.strip()  # Remove leading/trailing spaces
```

**Recommendation**: Add column stripping to all data loading in VARIABLE_DEF.md

---

## Updated Data Coverage Summary

| Data Type | Available Races | Quality | Notes |
|-----------|----------------|---------|-------|
| **qualifying/** | ✅ 12/12 | Excellent | All tracks, all drivers |
| **provisional_results/** | ✅ 12/12 | Excellent | Complete finishing data |
| **analysis_endurance/** | ✅ 12/12 | Good | Needs column stripping |
| **best_10_laps/** | ✅ 12/12 | Excellent | - |
| **S1, S2, S3 sectors** | ✅ 12/12 | Excellent | - |
| **ELAPSED times** | ✅ 12/12 | Excellent | For position tracking |
| **FLAG_AT_FL** | ✅ 12/12 | Excellent | FCY filtering works |
| **TOP_SPEED** | ⚠️ 8/12 | Good | Missing at Sebring & VIR |

---

## Recommended Updates to VARIABLE_DEF.md

### 1. Add Column Stripping to Data Loading

```python
def build_complete_feature_matrix(race_name):
    # Load analysis_endurance
    endurance = pd.read_csv(
        f'data/race_results/analysis_endurance/{race_name}_analysis_endurance.csv',
        delimiter=';'
    )
    endurance.columns = endurance.columns.str.strip()  # FIX: Remove leading spaces

    # Same for other data sources
    provisional = pd.read_csv(
        f'data/race_results/provisional_results/{race_name}_provisional_results.csv',
        delimiter=';'
    )
    provisional.columns = provisional.columns.str.strip()
```

### 2. Fix Variable 24 Data Type Handling

```python
def calc_positions_gained(provisional_results_df, qualifying_df, driver_number):
    # ... existing code ...

    # Get positions (cast to int to handle float values)
    qual_position = int(qual_driver['POS'].iloc[0])
    race_finish = int(provisional_results_df[
        provisional_results_df['NUMBER'] == driver_number
    ]['POSITION'].iloc[0])

    positions_gained = qual_position - race_finish

    # Return with int formatting
    return positions_gained, f"OK: Started P{qual_position}, finished P{race_finish} = {positions_gained:+d}"
```

### 3. Handle Missing TOP_SPEED Gracefully

```python
def calc_top_speed(analysis_endurance_df, driver_number):
    # ... existing filtering ...

    # Check if TOP_SPEED has valid data
    if clean_laps['TOP_SPEED'].isna().all():
        return np.nan, "No TOP_SPEED data for this race"

    driver_top_speed = clean_laps['TOP_SPEED'].mean()
    # ... rest of calculation ...
```

### 4. Update Data Availability Notes

Change documentation from:
```markdown
**For races WITH qualifying data (COTA, Sebring, Sonoma = 6 races):**
- ✅ **All 25 variables** fully calculated
```

To:
```markdown
**For ALL 12 races:**
- ✅ **Qualifying data available** for all tracks!
- ✅ **24-25 variables** calculated (23-24 core + 1-2 optional)

**Variable availability by race:**
- **Barber, COTA, Road America, Sonoma**: All 25 variables (or 23 if skipping telemetry)
- **Sebring, VIR**: 24 variables (TOP_SPEED missing - skip Variable 4)
```

---

## Final Metrics Validation Summary

### ✅ Working Perfectly (100% success rate)

1. **Variable 1 - Qualifying Pace**: 36/36 drivers
   - Uses `qualifying/TIME`
   - Normalized to pole position
   - Works across all 12 races

2. **Variable 8 - S1 Entry Performance**: 36/36 drivers
   - Uses `S1_SECONDS` with FCY filtering
   - Sector timing precise and reliable
   - Works across all 12 races

3. **Variable 21 - In-Race Position Changes**: 36/36 drivers
   - Calculates from `ELAPSED` cumulative times
   - Lap-by-lap running position tracking
   - NEW metric validated successfully!
   - Works across all 12 races

### ⚠️ Working with Minor Issues

4. **Variable 4 - Top Speed**: 24/36 drivers (67%)
   - Missing data at Sebring & VIR (8/12 races work)
   - **Fix**: Skip this variable for affected races OR derive from telemetry

5. **Variable 24 - Positions Gained**: 27/36 drivers (75%)
   - Data type mismatch at 3 races
   - **Fix**: Cast `POS` and `POSITION` to int (already fixed in test script)

---

## Conclusion

### Key Findings:

1. ✅ **Qualifying data exists for ALL 12 races** (major discovery!)
2. ✅ **Position tracking works perfectly** using ELAPSED times
3. ✅ **FCY filtering is critical** and working correctly
4. ⚠️ **TOP_SPEED missing** at 2 tracks (Sebring, VIR)
5. ⚠️ **Column names need stripping** (leading spaces)
6. ⚠️ **Minor data type issues** easily fixed

### Recommendations:

1. **Update VARIABLE_DEF.md** with the 4 fixes above
2. **Skip Variable 4 (TOP_SPEED)** for Sebring & VIR races, or mark as optional
3. **Use all 12 races** for factor analysis (not just 6!)
4. **24 variables** available for ALL races (skip TOP_SPEED if needed)
5. **25 variables** available for 8 races (Barber, COTA, Road America, Sonoma)

### Next Steps:

1. Apply the 4 code fixes to VARIABLE_DEF.md
2. Build feature matrices for all 12 races
3. Run factor analysis with 24 core variables
4. Discover 5-7 latent skill dimensions across ALL tracks and drivers!

---

**Test completed**: 2025-10-26
**Full test log**: `metrics_test_output.log`
**Summary CSV**: `data/analysis_outputs/metrics_validation_summary.csv`
