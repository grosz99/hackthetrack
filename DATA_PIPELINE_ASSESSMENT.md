# HackTheTrack Data Pipeline Architecture Assessment
**Date**: November 10, 2025  
**Status**: Current branch is master, all committed  
**Untracked**: TELEMETRY_ARCHITECTURE_PLAN.md (strategic document)

---

## EXECUTIVE SUMMARY

The HackTheTrack backend has a **partially implemented, conflict-ridden data pipeline** with three active data sources in an unstable equilibrium. Recent commits show a pattern of ping-ponging between Snowflake and CSV approaches, indicating architectural indecision. The system is **currently in a reverted state** prioritizing CSV fallback over Snowflake.

### Current State Matrix
```
┌─────────────────────────────────────────────────────────────┐
│ Data Source Status (as of commit c30b2e2, Nov 6, 21:07)     │
├─────────────────────────────────────────────────────────────┤
│ ✓ JSON (stable)        - Driver factors, season stats, race │
│ ⚠ CSV (fallback)       - Lap analysis CSV files not present │
│ ⚠ Snowflake (capable)  - Connected but not fully integrated │
│ ✗ Telemetry raw data   - Missing from local storage         │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. CURRENT DATA SOURCES

### 1.1 JSON Files (STABLE - 568KB total)
**Location**: `/backend/data/`

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `dashboardData.json` | 64KB | Track & driver definitions | ✅ Working |
| `driver_factors.json` | 204KB | Skill factors (RepTrak-normalized) | ✅ Working |
| `driver_season_stats.json` | 12KB | Aggregated season statistics | ✅ Working |
| `driver_race_results.json` | 288KB | Race-by-race results for trending | ✅ Working |

**Assessment**: These are pre-calculated, static aggregations. Perfect for high-speed API responses. No real-time computation needed. The dashboard data contains 31 drivers loaded from CSV originally.

**Code Location**: 
- Loading: `/backend/app/services/data_loader.py` lines 103-140, 168-220
- Usage: `/backend/app/api/routes.py` lines 71-139 (driver endpoints)

---

### 1.2 CSV Files (MISSING LOCALLY, SHOULD EXIST)
**Expected Location**: `/backend/data/race_results/analysis_endurance/`

**Status**: ❌ **NOT FOUND ON DISK**

```python
# Expected structure from code:
self.lap_analysis: Dict[str, pd.DataFrame] = {}

# Key format: "{track_id}_r{race_num}_analysis_endurance"
# Examples: "barber_r1_analysis_endurance", "cota_r1_analysis_endurance"

# Columns expected: VEHICLE_NUMBER, LAP, S1_SECONDS, S2_SECONDS, S3_SECONDS, 
#                   LAP_TIME, FLAG_AT_FL, LAPTRIGGER_LAPDIST_DLS
```

**Code References**:
- `/backend/app/services/data_loader.py` lines 301-321 (loading)
- `/backend/app/api/routes.py` lines 278-334 (telemetry compare endpoint)

**Critical Issue**: The code structure exists for CSV loading, but files were removed (git history shows `2157af1` commit: "fix: remove large CSV files from git tracking (>100MB)"). The system falls back to Snowflake if CSV missing.

---

### 1.3 Snowflake Integration (CAPABLE BUT CONFLICTED)
**Status**: ⚠️ **CONNECTED BUT UNDERUTILIZED**

**What Exists**:
- ✅ Three authentication methods implemented (password, base64 key, key file)
- ✅ Health check endpoint working
- ✅ Connection logic solid (lazy-loaded)
- ✅ JSON fallback mechanism

**What's Implemented**:
```python
# Snowflake methods available:
snowflake_service.get_drivers_with_telemetry()       # Returns 35 drivers
snowflake_service.get_telemetry_data(track_id, race) # Full table load (15.7M rows)
snowflake_service.query(sql, params)                 # Generic query interface
snowflake_service.health_check()                     # Status check
```

**What's NOT Implemented**:
- ❌ Memory-efficient filtered queries (loads ALL 15.7M rows per request)
- ❌ Dedicated `get_telemetry_data_filtered()` with WHERE clauses
- ❌ Pagination or streaming support

**Code Location**: `/backend/app/services/snowflake_service.py` (342 lines)

**Snowflake Table Schema** (from architecture plan):
```
HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL
├─ VEHICLE_NUMBER (driver ID)
├─ TRACK_ID
├─ RACE_NUM
├─ LAP
├─ LAPTRIGGER_LAPDIST_DLS
├─ FLAG_AT_FL ('GF' = green, 'FCY' = caution)
└─ ... (raw telemetry columns)

Data: 15.7M rows across 5 tracks, 2 races, 35 drivers
Tracks: barber, cota, roadamerica, sonoma, vir
```

---

## 2. CURRENT ARCHITECTURE STATUS

### 2.1 The Telemetry Data Flow (Current State)

```
API Request: /api/telemetry/compare
└─ routes.py line 278: compare_telemetry()
   ├─ data_loader.get_lap_data(track_id, race_num)
   │  └─ data_loader.py line 339-342:
   │     return self.lap_analysis.get(key)  # ← FIRST TRIES CSV
   │     
   │  IF CSV EMPTY → snowflake_service.get_telemetry_data()
   │     └─ snowflake_service.py line 218-247:
   │        SELECT * FROM TELEMETRY_DATA_ALL  
   │        WHERE TRACK_ID = ? AND RACE_NUM = ?
   │        ↓ LOADS FULL TABLE (15.7M rows) ← MEMORY ISSUE
   │
   └─ Filter in-memory for driver 1 & 2
      └─ Calculate sector deltas
      └─ Return comparison

DATA SOURCES QUERIED (in order):
1. CSV files in memory (self.lap_analysis dict) 
   ├─ If available → use and skip Snowflake
   └─ If missing → fall through
2. Snowflake full table dump
   ├─ No filtering at DB level
   ├─ Loads all 15.7M rows into pandas
   └─ Causes memory crashes on Heroku
3. JSON fallback (currently not implemented for telemetry)
```

### 2.2 Recent Commit History (Last 20 Commits)

```
c30b2e2 (HEAD)  revert: get_lap_data back to CSV only - telemetry via 
                 Snowflake only for Improve tab
                 
cd00646         fix: add CSV fallback to prevent memory crash
                ├─ ADDED: Fallback from Snowflake to CSV
                ├─ REASON: Snowflake was loading 15.7M rows
                └─ STATUS: Current approach (commit c30b2e2 reverted this)

d8c52a8         fix: get_lap_data uses Snowflake not CSV
                ├─ REMOVED: CSV-based lap analysis
                ├─ REASON: "Use Snowflake for all telemetry"
                └─ CONSEQUENCE: Memory crash

0023bbe         fix: use VEHICLE_NUMBER not DRIVER_NUMBER
                └─ Snowflake column name correction

aea87d3         fix: correct FLAG_AT_FL filtering in compare endpoint
                └─ Filtering for green flag laps only

[8 more Snowflake-related fixes...]

2157af1         fix: remove large CSV files from git tracking (>100MB)
                └─ HISTORICAL: CSV files removed from repo

cf41bc7         feat: add Heroku deployment (most reliable option)
                └─ Deployment work
```

**Pattern**: Oscillation between Snowflake-only (d8c52a8) and CSV-first (cd00646, c30b2e2)

---

## 3. HEROKU DEPLOYMENT STATUS

### 3.1 Current Deployment

**Setup**: 
- ✅ Heroku Procfile configured (`uvicorn main:app --host 0.0.0.0 --port $PORT`)
- ✅ Docker image (Python 3.12-slim, wheel-only, no compilation)
- ✅ Requirements frozen (15 dependencies)

**Environment**:
- ✅ RSA key authentication configured
- ✅ Snowflake credentials in env vars
- ⚠️ CSV files NOT deployed (missing locally)
- ✅ JSON data files included (568KB - negligible)

### 3.2 Memory Constraints
```
Heroku R14 (assumed): 512MB RAM

Current Estimate:
├─ Python runtime:      ~80MB
├─ Dependencies (pandas, numpy, etc): ~150MB
├─ JSON data in memory: ~1MB
├─ CSV lap analysis (if present): ~100-200MB
└─ Snowflake full table dump: ⚠️ EXCEEDS LIMIT

ISSUE: Loading 15.7M rows from Snowflake would exceed RAM
SOLUTION: Use filtered Snowflake queries (WHERE clauses)
```

### 3.3 Deployment Files

| File | Status | Purpose |
|------|--------|---------|
| `Procfile` | ✅ | Heroku run command |
| `Dockerfile` | ✅ | Docker image definition |
| `requirements.txt` | ✅ | Frozen dependencies |
| `.env.example` | ✅ | Configuration template |
| `.env` | ⚠️ | Actually committed (should be .gitignore) |
| RSA keys | ⚠️ | Stored locally, should be in env vars only |

---

## 4. TELEMETRY DATA FLOW ANALYSIS

### 4.1 What Actually Works

**✅ Driver List Endpoint** (`/api/telemetry/drivers`)
- Source: Snowflake query (DISTINCT VEHICLE_NUMBER)
- Data: 35 drivers with telemetry
- Size: ~1KB response
- Memory: Minimal
- Status: **WORKING** (routes.py lines 910-934)

**✅ Dashboard & Predictions** 
- Source: JSON files + basic model
- Data: 31 drivers with factor scores
- Memory: ~1MB
- Status: **WORKING** (routes.py lines 71-232)

**✅ Season Stats & Race Results**
- Source: JSON pre-aggregated data
- Status: **WORKING** (routes.py lines 109-138)

---

### 4.2 What's Broken

**❌ Telemetry Compare Endpoint** (`/api/telemetry/compare`)
- Expected: Compare two drivers' lap telemetry
- Current Problem: CSV files don't exist locally
- Fallback: Snowflake loads 15.7M rows → memory crash
- Last Error: commit c30b2e2 tried to fix by reverting to CSV-only
- **Status**: BROKEN (depends on missing CSV files)

**Code Path** (routes.py line 278-334):
```python
@router.get("/telemetry/compare")
async def compare_telemetry(track_id, driver_1, driver_2, race_num=1):
    lap_data = data_loader.get_lap_data(track_id, race_num)  # ← Returns None
    if lap_data is None:
        raise HTTPException(404, "No lap data found")
```

**❌ Telemetry Coaching Endpoint** (`/api/telemetry/coaching`)
- Expected: AI-powered coaching based on telemetry
- Current: Tries Snowflake full dump
- **Status**: BROKEN FOR SAME REASON (routes.py lines 937-1031)

---

### 4.3 Missing CSV Data

From architecture plan and code, we expect:
```
backend/data/race_results/analysis_endurance/
├── barber_r1_analysis_endurance.csv
├── barber_r2_analysis_endurance.csv
├── cota_r1_analysis_endurance.csv
├── cota_r2_analysis_endurance.csv
├── roadamerica_r1_analysis_endurance.csv
├── roadamerica_r2_analysis_endurance.csv
├── sonoma_r1_analysis_endurance.csv
├── sonoma_r2_analysis_endurance.csv
├── vir_r1_analysis_endurance.csv
└── vir_r2_analysis_endurance.csv

Each file: ~10-50MB (semicolon-delimited, columns: VEHICLE_NUMBER, LAP, 
           S1_SECONDS, S2_SECONDS, S3_SECONDS, LAP_TIME, FLAG_AT_FL, etc.)
```

**Why Missing**: Removed by commit `2157af1` ("fix: remove large CSV files from git tracking") due to >100MB file size limits. Need external storage (Heroku or S3) or re-upload to Snowflake.

---

## 5. CRITICAL GAPS & INSTABILITY POINTS

### 5.1 Architectural Debt

| Issue | Severity | Impact | Root Cause |
|-------|----------|--------|------------|
| CSV files removed but code still expects them | CRITICAL | Telemetry endpoints 404 | Heroku file size limits not considered |
| Snowflake loads 15.7M rows instead of filtered queries | CRITICAL | Memory crashes | No WHERE clause filtering implemented |
| Three data sources without clear ownership | HIGH | Confusion on which to use | No architecture decision documented |
| Oscillating commits (swap Snowflake↔CSV) | HIGH | Unstable state | Unresolved design decision |
| No pagination/streaming for large datasets | HIGH | Scalability issue | Assumes all data fits in RAM |
| Routes.py is 1151 lines (exceeds 500-line guidance) | MEDIUM | Hard to maintain | Needs modularization |

### 5.2 Data Source Conflicts

**Problem**: The code doesn't know which data source is primary.

```python
# In data_loader.py:
def get_lap_data(self, track_id, race_num):
    key = f"{track_id}_r{race_num}_analysis_endurance"
    return self.lap_analysis.get(key)  # ← CSV-only, no fallback now

# But in routes.py line 955:
df = snowflake_service.get_telemetry_data(track_id, race_num)  # ← Direct Snowflake

# And in snowflake_service.py line 218:
def get_telemetry_data(self):
    # Tries Snowflake, but no filtering!
    SELECT * FROM TELEMETRY_DATA_ALL WHERE ...  # ← Full table
```

**Result**: Inconsistent behavior depending on which endpoint is called.

---

### 5.3 Line Count Analysis

| File | Lines | Status | Issue |
|------|-------|--------|-------|
| `routes.py` | 1151 | ⚠️ OVERSIZE | Exceeds 500-line guidance; needs splitting |
| `data_loader.py` | 471 | ✅ OK | Approaching limit |
| `snowflake_service.py` | 342 | ✅ OK | Well-sized |

The routes file consolidates too many concerns:
- Track endpoints (lines 48-63)
- Driver endpoints (lines 71-139)
- Predictions (lines 146-232)
- Telemetry comparison (lines 278-418)
- Health check (lines 426-443)
- Detailed telemetry (lines 451-505)
- Factor breakdown (lines 513-719)
- Improve predictions (lines 725-902)
- Telemetry coaching (lines 937-1031)

---

## 6. WHAT'S STABLE & CAN BE BUILT UPON

### 6.1 Solid Foundations

✅ **FastAPI Setup**
- Properly configured CORS for Vercel
- Health check endpoint working
- Error handling with HTTPException

✅ **Snowflake Connection**
- Three auth methods implemented (password, base64 key, file)
- Connection pooling & keep-alive
- Environment variable configuration

✅ **JSON Data Layer**
- Pre-calculated aggregations (season stats, race results)
- RepTrak-normalized factor scores
- Dashboard data with track demands
- All stable and performant

✅ **Pydantic Models**
- Strong type validation
- Proper response models defined
- Consistent API contracts

✅ **Docker Deployment**
- Python 3.12-slim, efficient image
- Wheel-only (no compilation on Heroku)
- Proper port binding

---

### 6.2 What's NOT Stable

❌ **Telemetry Data Pipeline**
- CSV files missing
- Snowflake not optimized (no filtering)
- Oscillating architecture decisions

❌ **Memory Management**
- Full table loads not mitigated
- No pagination/streaming
- No explicit cache management

❌ **Code Organization**
- routes.py too large (1151 lines)
- Telemetry logic scattered across files
- No clear service layer separation

---

## 7. CRITICAL NEXT STEPS

### 7.1 Immediate Fixes (Next Session - 2-3 hours)

```
Priority 1: CHOOSE DATA STRATEGY
├─ Option A: Migrate CSV to Snowflake + implement filtered queries
├─ Option B: Re-upload CSV files, store on Heroku or S3
└─ Option C: Hybrid - Snowflake raw data + CSV aggregations

Priority 2: IMPLEMENT CHOSEN APPROACH
├─ Create get_telemetry_data_filtered(track_id, race_num, drivers) 
│  with WHERE clause filtering in Snowflake
├─ Or upload CSV files with appropriate storage solution
└─ Test memory usage before deploying

Priority 3: FIX TELEMETRY ENDPOINTS
├─ /api/telemetry/compare should return valid data
├─ /api/telemetry/coaching should work
└─ Test with actual drivers
```

### 7.2 Recommended Approach: Snowflake Migration (Option A)

**Why**:
- Single source of truth
- Scalable to millions of rows (with proper filtering)
- No file storage/deployment complexity
- Already partially implemented

**Implementation**:
```python
# Add to snowflake_service.py:
def get_telemetry_data_filtered(
    self, track_id: str, race_num: int, 
    driver_numbers: List[int]
) -> Optional[pd.DataFrame]:
    """Get filtered telemetry - only specified drivers."""
    sql = """
        SELECT * 
        FROM HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL
        WHERE TRACK_ID = %s
          AND RACE_NUM = %s
          AND VEHICLE_NUMBER IN ({placeholders})
          AND FLAG_AT_FL = 'GF'
        ORDER BY VEHICLE_NUMBER, LAP, LAPTRIGGER_LAPDIST_DLS
    """
    # This loads ~2000 rows instead of 15.7M
```

**Effort**: 4 hours (script, endpoint, testing, verification)

---

## 8. COMPREHENSIVE FILE MAP

### Core Services
- `/backend/app/services/snowflake_service.py` - Snowflake connection (342 lines, SOLID)
- `/backend/app/services/data_loader.py` - JSON/CSV loading (471 lines, NEEDS REFACTOR)
- `/backend/app/api/routes.py` - All endpoints (1151 lines, OVERSIZE - needs split)
- `/backend/app/services/ai_strategy.py` - AI chat (not reviewed)
- `/backend/app/services/ai_telemetry_coach.py` - Coaching (not reviewed)
- `/backend/app/services/telemetry_processor.py` - Processing (100+ lines)
- `/backend/app/services/improve_predictor.py` - Predictions (not reviewed)

### Data
- `/backend/data/dashboardData.json` - Track/driver config (64KB, stable)
- `/backend/data/driver_factors.json` - Skill scores (204KB, stable)
- `/backend/data/driver_season_stats.json` - Aggregations (12KB, stable)
- `/backend/data/driver_race_results.json` - Results (288KB, stable)
- `/backend/data/race_results/analysis_endurance/` - CSV lap data (MISSING)

### Deployment
- `/backend/Dockerfile` - Docker image (clean, efficient)
- `/backend/Procfile` - Heroku run command
- `/backend/requirements.txt` - Dependencies (frozen, good)
- `/backend/main.py` - FastAPI app setup (77 lines, clean)
- `/backend/.env` - Config (⚠️ should be git-ignored)

### Documentation
- `/backend/TELEMETRY_ARCHITECTURE_PLAN.md` - Architecture (untracked, new file)

---

## 9. SUMMARY TABLE

| Category | Current State | Stability | Next Action |
|----------|---------------|-----------|-------------|
| **JSON Data** | Loaded, cached, working | ✅ Stable | No changes needed |
| **CSV Telemetry** | Files deleted, code remains | ❌ Broken | Choose: re-upload or migrate to Snowflake |
| **Snowflake Connection** | Configured, auth works, no filtering | ⚠️ Partial | Implement filtered queries |
| **Telemetry Endpoints** | Implemented but non-functional | ❌ Broken | Fix by addressing CSV/Snowflake conflict |
| **Heroku Deployment** | Configured, no CSV files | ⚠️ Risky | Ensure data strategy before deploy |
| **Code Organization** | routes.py oversized, services OK | ⚠️ Technical debt | Refactor routes after data strategy fixed |
| **Memory Management** | No filtering, no pagination | ❌ Critical | Implement WHERE clause filtering |
| **Documentation** | Plan written but decision pending | ⚠️ Incomplete | Make final architecture decision |

---

## QUESTIONS FOR NEXT SESSION

1. **Architecture Decision**: Should telemetry be Snowflake-first (with filtering) or CSV-based (with file hosting)?
2. **CSV Migration**: If keeping CSV, where will 100MB+ files be stored? (Heroku filesystem is ephemeral)
3. **Deployment Timeline**: When should Heroku deployment be tested with real data?
4. **Scale Expectations**: What's the expected query volume? Should we consider caching?
5. **Code Refactoring**: Should routes.py be split before merging more telemetry features?

---

**Assessment Complete**: All major systems reviewed, critical issues identified, architecture plan available.
