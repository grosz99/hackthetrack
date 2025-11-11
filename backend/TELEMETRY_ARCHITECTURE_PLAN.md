# Telemetry Data Architecture Plan

## Current State (November 6, 2025)

### What's Working
- ✅ Snowflake connection established with RSA keypair authentication
- ✅ `/api/telemetry/drivers` endpoint returns 35 drivers from Snowflake
- ✅ Application stable with 31 drivers loaded from CSV data
- ✅ Driver factor scores, season stats, and race results working from JSON

### Critical Issues Discovered
- ❌ **Memory Crash**: Loading full telemetry dataset (15.7M rows) exceeds Heroku memory quota
- ❌ **Improve Tab Not Working**: `/api/telemetry/compare` returns 404 (no CSV data for barber, cota, etc.)
- ❌ **Mixed Data Sources**: Confusion about when to use Snowflake vs CSV

### Data Sources Overview
1. **Snowflake TELEMETRY_DATA_ALL**: 15.7M rows of lap-by-lap telemetry data
   - Tracks: barber, cota, roadamerica, sonoma, vir (races 1 and 2)
   - 35 drivers with telemetry data
   - Columns: VEHICLE_NUMBER, TRACK_ID, RACE_NUM, LAP, LAPTRIGGER_LAPDIST_DLS, FLAG_AT_FL, etc.

2. **Local CSV Files**: Race results and lap analysis
   - Located in: `backend/data/race_results/`
   - Loaded into memory via `DataLoader.lap_analysis` dict
   - Currently NOT available for Snowflake tracks (barber, cota, etc.)

3. **JSON Files**: Pre-calculated aggregations
   - `driver_factors.json`: RepTrak-normalized factor scores
   - `driver_season_stats.json`: Season-level aggregations
   - `driver_race_results.json`: Race-by-race results

## User Requirement (from previous session)

> "so to be clear only the improve page should use the telemetry data"

> "write that as a plan for next time as snowflake should only be for that endpoint or you need to make the decision should the csv be in snowflake"

## Architecture Decision Required

### Option A: Migrate CSV to Snowflake ⭐ RECOMMENDED
**Use Snowflake as single source of truth for all telemetry data**

#### Implementation Steps
1. **Upload existing CSV files to Snowflake**
   ```python
   # Script to upload CSV data to TELEMETRY_DATA_ALL table
   # Ensure column names match: VEHICLE_NUMBER, TRACK_ID, RACE_NUM, LAP, etc.
   ```

2. **Create memory-efficient telemetry endpoint**
   ```python
   @router.get("/telemetry/compare")
   async def compare_drivers(
       track_id: str,
       race_num: int,
       driver_1: int,
       driver_2: int
   ):
       """
       Query Snowflake with WHERE clause to filter BEFORE loading into memory.

       SQL:
           SELECT *
           FROM HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL
           WHERE TRACK_ID = %s
             AND RACE_NUM = %s
             AND VEHICLE_NUMBER IN (%s, %s)
             AND FLAG_AT_FL = 'GF'
           ORDER BY VEHICLE_NUMBER, LAP, LAPTRIGGER_LAPDIST_DLS

       This loads only ~2000 rows instead of 15.7M rows.
       """
   ```

3. **Remove CSV lap analysis loading**
   - Delete `self.lap_analysis` from `DataLoader`
   - Remove CSV parsing in `_load_race_data()`
   - Simplify codebase to single data source

#### Pros
- ✅ Single source of truth
- ✅ Scalable to millions of rows
- ✅ No need to manage CSV files on Heroku
- ✅ Memory efficient with smart filtering
- ✅ Can add new tracks without deploying CSV files

#### Cons
- ⚠️ Requires CSV migration (one-time effort)
- ⚠️ Depends on Snowflake availability (but we have JSON fallback for aggregations)
- ⚠️ Need to ensure all queries use WHERE clause filtering

#### Estimated Effort
- **Migration Script**: 2 hours
- **Endpoint Implementation**: 1 hour
- **Testing**: 1 hour
- **Total**: 4 hours

---

### Option B: Keep CSV Separate
**Continue using CSV files for lap analysis, Snowflake only for driver lists**

#### Implementation Steps
1. **Upload CSV files to Heroku**
   - Store in `backend/data/race_results/`
   - Ensure files are included in Docker image
   - OR use external storage (AWS S3)

2. **Keep current `get_lap_data()` implementation**
   ```python
   def get_lap_data(self, track_id: str, race_num: int = 1) -> Optional[pd.DataFrame]:
       """Get lap analysis data from local CSV files."""
       key = f"{track_id}_r{race_num}_analysis_endurance"
       return self.lap_analysis.get(key)
   ```

3. **Snowflake only for `/api/telemetry/drivers`**
   - No changes needed (already working)

#### Pros
- ✅ No migration needed
- ✅ Known working solution
- ✅ Independent of Snowflake for core functionality

#### Cons
- ❌ Multiple data sources to maintain
- ❌ CSV files increase Docker image size
- ❌ Limited scalability (memory constraints for large CSVs)
- ❌ Need to deploy new CSV files when adding tracks

#### Estimated Effort
- **CSV Storage Setup**: 1 hour
- **Docker Image Update**: 30 minutes
- **Testing**: 30 minutes
- **Total**: 2 hours

---

### Option C: Hybrid Approach
**Use Snowflake for raw telemetry, CSV for pre-aggregated metrics**

#### Implementation Steps
1. **Snowflake for raw lap-by-lap data**
   - Implement memory-efficient queries with WHERE clause filtering
   - Use for `/api/telemetry/compare` (Improve tab)

2. **CSV/JSON for aggregated metrics**
   - Keep season stats, race results in JSON
   - Keep summary lap analysis in CSV (if needed)

3. **Create dedicated service layer**
   ```python
   class TelemetryService:
       def get_raw_telemetry(self, track_id, race_num, drivers):
           """Query Snowflake with filtering."""
           return snowflake_service.get_telemetry_data_filtered(...)

       def get_aggregated_stats(self, driver_number):
           """Load from JSON."""
           return data_loader.get_season_stats(driver_number)
   ```

#### Pros
- ✅ Best performance (pre-aggregated data)
- ✅ Scalable for raw data queries
- ✅ Fallback options for both data types

#### Cons
- ⚠️ Most complex to implement
- ⚠️ Need to maintain both CSV and Snowflake
- ⚠️ Risk of data inconsistency

#### Estimated Effort
- **Service Layer**: 3 hours
- **Migration**: 2 hours
- **Testing**: 2 hours
- **Total**: 7 hours

---

## Recommended Approach: Option A (Snowflake Migration)

### Rationale
1. **User Requirement**: "only the improve page should use the telemetry data" - This suggests Snowflake should handle telemetry queries
2. **Scalability**: Snowflake handles 15.7M rows efficiently with proper WHERE clause filtering
3. **Simplicity**: Single source of truth reduces complexity
4. **Memory Safety**: Server-side filtering prevents memory crashes

### Implementation Plan

#### Phase 1: Create Snowflake Service Method (30 minutes)
```python
# backend/app/services/snowflake_service.py

def get_telemetry_data_filtered(
    self,
    track_id: str,
    race_num: int,
    driver_numbers: List[int]
) -> Optional[pd.DataFrame]:
    """
    Get filtered telemetry data for specific drivers.

    CRITICAL: This method filters in Snowflake to avoid loading 15.7M rows.

    Args:
        track_id: Track identifier (e.g., 'barber')
        race_num: Race number (1 or 2)
        driver_numbers: List of driver numbers to filter

    Returns:
        DataFrame with ~1000-2000 rows (instead of 15.7M)
    """
    if not self.enabled:
        logger.warning("Snowflake disabled, cannot get telemetry")
        return None

    try:
        # Create parameterized query with IN clause
        placeholders = ', '.join(['%s'] * len(driver_numbers))

        sql = f"""
            SELECT *
            FROM HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL
            WHERE TRACK_ID = %s
              AND RACE_NUM = %s
              AND VEHICLE_NUMBER IN ({placeholders})
              AND FLAG_AT_FL = 'GF'
            ORDER BY VEHICLE_NUMBER, LAP, LAPTRIGGER_LAPDIST_DLS
        """

        # Combine parameters
        params = [track_id, race_num] + driver_numbers

        df = self.query(sql, params=params)

        if df is not None and not df.empty:
            logger.info(f"✅ Loaded {len(df)} filtered telemetry rows from Snowflake")
            return df
        else:
            logger.warning(f"No telemetry data for {track_id} race {race_num}, drivers {driver_numbers}")
            return None

    except Exception as e:
        logger.error(f"❌ Failed to get filtered telemetry: {e}")
        return None
```

#### Phase 2: Update Telemetry Compare Endpoint (30 minutes)
```python
# backend/app/api/routes.py

@router.get("/telemetry/compare")
async def compare_drivers(
    track_id: str,
    race_num: int = 1,
    driver_1: int = Query(...),
    driver_2: int = Query(...),
):
    """
    Compare two drivers' telemetry data for Improve tab.

    Uses Snowflake with WHERE clause filtering to avoid memory crashes.
    """
    from ..services.snowflake_service import snowflake_service

    # Get filtered data from Snowflake (only 2 drivers)
    lap_data = snowflake_service.get_telemetry_data_filtered(
        track_id=track_id,
        race_num=race_num,
        driver_numbers=[driver_1, driver_2]
    )

    if lap_data is None or lap_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No telemetry data found for {track_id} race {race_num}"
        )

    # Filter for each driver (data already filtered in Snowflake)
    driver_1_data = lap_data[lap_data["VEHICLE_NUMBER"] == driver_1]
    driver_2_data = lap_data[lap_data["VEHICLE_NUMBER"] == driver_2]

    if driver_1_data.empty or driver_2_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Missing data for one or both drivers"
        )

    # Rest of comparison logic...
    # (Calculate lap times, speed differences, etc.)

    return {
        "track_id": track_id,
        "race_num": race_num,
        "driver_1": {
            "number": driver_1,
            "lap_count": len(driver_1_data["LAP"].unique()),
            "avg_speed": driver_1_data["SPEED"].mean(),
            # ... more metrics
        },
        "driver_2": {
            "number": driver_2,
            "lap_count": len(driver_2_data["LAP"].unique()),
            "avg_speed": driver_2_data["SPEED"].mean(),
            # ... more metrics
        }
    }
```

#### Phase 3: Remove CSV Lap Analysis Loading (15 minutes)
```python
# backend/app/services/data_loader.py

def __init__(self):
    # ... existing initialization ...

    # REMOVE THIS:
    # self.lap_analysis: Dict[str, pd.DataFrame] = {}

def _load_data(self):
    # ... existing loads ...

    # REMOVE THIS CALL:
    # self._load_race_data()

# REMOVE THIS METHOD:
# def _load_race_data(self):
#     """Load race results and lap analysis data."""
#     ...

# REMOVE THIS METHOD:
# def get_lap_data(self, track_id: str, race_num: int = 1) -> Optional[pd.DataFrame]:
#     """Get lap analysis data for a specific track and race."""
#     ...
```

#### Phase 4: Testing (1 hour)
1. **Test memory usage**
   ```bash
   # Monitor Heroku memory
   heroku logs --tail -a hackthetrack-api | grep "Memory"
   ```

2. **Test telemetry compare endpoint**
   ```bash
   # Should return comparison data without memory crash
   curl "https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/telemetry/compare?track_id=barber&race_num=1&driver_1=7&driver_2=13"
   ```

3. **Verify row counts**
   - Query should return ~1000-2000 rows (2 drivers × ~500-1000 laps each)
   - NOT 15.7M rows

#### Phase 5: Documentation (15 minutes)
Update this document with:
- ✅ Decision made: Option A (Snowflake Migration)
- ✅ Implementation completed
- ✅ Test results
- ✅ Memory usage verified

---

## CSV Migration (Optional - Only if needed)

If there are CSV files with data NOT in Snowflake, run this migration:

```python
# backend/scripts/migrate_csv_to_snowflake.py

import pandas as pd
from pathlib import Path
from app.services.snowflake_service import SnowflakeService

def migrate_csv_to_snowflake():
    """
    Migrate local CSV files to Snowflake TELEMETRY_DATA_ALL table.

    Only run if CSV files contain data not in Snowflake.
    """
    snowflake = SnowflakeService()
    csv_dir = Path(__file__).parent.parent / "data" / "race_results" / "analysis_endurance"

    if not csv_dir.exists():
        print("No CSV directory found, skipping migration")
        return

    for csv_file in csv_dir.glob("*.csv"):
        print(f"Processing {csv_file.name}...")

        # Load CSV
        df = pd.read_csv(csv_file, delimiter=';')
        df.columns = df.columns.str.strip().str.upper()

        # Insert into Snowflake
        conn = snowflake.get_connection()
        if conn:
            cursor = conn.cursor()

            # Bulk insert (adjust column names as needed)
            cursor.execute("""
                INSERT INTO HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL
                SELECT * FROM VALUES (...)
            """)

            conn.commit()
            cursor.close()
            print(f"✅ Migrated {len(df)} rows from {csv_file.name}")

if __name__ == "__main__":
    migrate_csv_to_snowflake()
```

---

## Success Criteria

- ✅ `/api/telemetry/compare` returns data without memory crashes
- ✅ Heroku memory usage stays below R14 threshold
- ✅ Improve tab works with Snowflake telemetry data
- ✅ Query performance < 2 seconds for 2-driver comparison
- ✅ No CSV files needed for telemetry queries

---

## Rollback Plan

If Snowflake approach fails:

1. **Revert to CSV-only**
   ```bash
   git revert <commit-hash>
   heroku restart -a hackthetrack-api
   ```

2. **Upload CSV files to Heroku**
   - Include in Docker image build
   - Verify files present in container

3. **Re-enable `get_lap_data()` method**

---

## Next Session Checklist

- [ ] Review this plan with user
- [ ] Decide on Option A, B, or C
- [ ] Implement chosen approach
- [ ] Test memory usage on Heroku
- [ ] Verify Improve tab functionality
- [ ] Update documentation with results
- [ ] Consider pagination for large result sets (if needed)

---

**Created**: November 6, 2025
**Next Review**: When continuing Snowflake integration work
**Owner**: Development team working on HackTheTrack Snowflake integration
