# Architecture Rebuild Plan

## Executive Summary

This document outlines the systematic approach to fix the critical data architecture and deployment issues identified in the HackTheTrack application.

**Current State:** Mixed data sources (JSON/SQLite/Snowflake), broken serverless deployment, no unified data layer, inefficient API patterns.

**Goal:** Single source of truth, proper deployment architecture, efficient APIs, production-ready error handling.

---

## 🔴 Phase 1: IMMEDIATE FIXES (Tonight/Tomorrow - 2 hours)

### 1.1 Fix Production Deployment (30 minutes)

**Problem:** Frontend doesn't know where API is. Vercel serverless functions are broken.

**Solution:**
1. Set `VITE_API_URL=https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api` in Vercel
2. Remove all Vercel serverless function code (already done)
3. Document: Frontend (Vercel) → Backend API (Heroku)

**Files to update:**
- `frontend/.env.production` ✓ Already correct
- Vercel dashboard environment variables
- `README.md` - document deployment architecture

### 1.2 Fix Skills Page API Efficiency (30 minutes)

**Problem:** Loading all 34 drivers (~40KB) just to calculate top 3 average.

**Current:**
```javascript
// Skills.jsx loads ALL drivers
const driversResponse = await api.get('/api/drivers')
const drivers = driversResponse.data
const topDrivers = drivers.sort((a, b) => b[factor] - a[factor]).slice(0, 3)
const avgTopDrivers = topDrivers.reduce((sum, d) => sum + d[factor], 0) / 3
```

**Solution:** Add new endpoint that returns only what we need.

**New endpoint:**
```python
@router.get("/api/factors/{factor_name}/top-average")
async def get_factor_top_average(factor_name: str, limit: int = 3):
    """Get average of top N drivers for a specific factor."""
    # Returns: { "factor": "speed", "top_average": 85.2, "count": 3 }
```

**Files to create:**
- `backend/app/api/routes.py` - add new endpoint
- `frontend/src/services/api.js` - add helper function
- `frontend/src/pages/Skills.jsx` - use new endpoint

---

## 🟡 Phase 2: UNIFIED DATA ARCHITECTURE (Week 1 - 8 hours)

### 2.1 Consolidate to Single Source of Truth

**Problem:** Three data sources that can get out of sync.

**Decision Matrix:**

| Data Source | Size | Speed | Scalability | Production Ready |
|-------------|------|-------|-------------|------------------|
| JSON files | 428KB | ⚡ Fast | ❌ Limited | ✅ Yes (for read-only) |
| SQLite | 139KB | ⚡ Fast | ❌ Single file | ❌ No (not for production) |
| Snowflake | ☁️ Cloud | 🐌 Network latency | ✅ Unlimited | ✅ Yes |

**RECOMMENDATION: Hybrid Approach**

```
┌─────────────────────────────────────────────┐
│         APPLICATION LAYER                   │
├─────────────────────────────────────────────┤
│  Unified Data Service (Single Interface)   │
├─────────────────────────────────────────────┤
│  READ CACHE          │  WRITE MASTER        │
│  (JSON in memory)    │  (Snowflake)         │
│  - Driver stats      │  - New race data     │
│  - Track info        │  - Telemetry         │
│  - Factor scores     │  - User data         │
└─────────────────────────────────────────────┘
```

**Implementation:**

```python
# backend/app/services/unified_data_service.py

class UnifiedDataService:
    """Single point of access for all application data."""

    def __init__(self):
        self.cache = self._load_static_cache()
        self.snowflake = SnowflakeConnection() if ENABLE_SNOWFLAKE else None

    def get_driver(self, driver_number: int) -> Driver:
        """Get driver from cache (fast)."""
        return self.cache.drivers.get(driver_number)

    def get_driver_telemetry(self, driver_number: int, race_id: str) -> Telemetry:
        """Get telemetry from Snowflake (detailed analysis)."""
        if not self.snowflake:
            raise ServiceUnavailableError("Telemetry service unavailable")
        return self.snowflake.query_telemetry(driver_number, race_id)

    def refresh_cache(self):
        """Rebuild cache from Snowflake (scheduled job)."""
        # Run nightly to sync JSON cache with Snowflake
        pass
```

### 2.2 Eliminate SQLite Database

**Problem:** SQLite is not production-ready, adds complexity.

**Migration Plan:**

1. **Extract all data from circuit-fit.db:**
   ```bash
   python scripts/export_sqlite_to_json.py
   ```

2. **Merge into existing JSON files:**
   - Factor breakdowns → `driver_factors.json` (already has most data)
   - Variables → add to same file

3. **Update API routes:**
   ```python
   # OLD (SQLite)
   conn = sqlite3.connect(db_path)
   cursor = conn.execute("SELECT * FROM factors WHERE driver_number = ?", (driver_num,))

   # NEW (Unified Service)
   driver = data_service.get_driver(driver_num)
   return driver.factors[factor_name]
   ```

4. **Delete:**
   - `circuit-fit.db`
   - All SQLite connection code
   - `database/` directory

**Files to update:**
- `backend/app/services/data_loader.py` - remove SQLite logic
- `backend/app/api/routes.py` - use unified service
- `backend/app/services/factor_analyzer.py` - use unified service

---

## 🟠 Phase 3: PERFORMANCE & RELIABILITY (Week 2 - 6 hours)

### 3.1 Implement Connection Pooling

**Problem:** Creating new connections for every request.

**Solution:**

```python
# backend/app/services/snowflake_service.py

from snowflake.connector.connection import SnowflakeConnection
from functools import lru_cache
import threading

class SnowflakeConnectionPool:
    """Thread-safe connection pool for Snowflake."""

    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.connections = []
        self.lock = threading.Lock()
        self._initialize_pool()

    def get_connection(self) -> SnowflakeConnection:
        with self.lock:
            if self.connections:
                return self.connections.pop()
            return self._create_connection()

    def return_connection(self, conn: SnowflakeConnection):
        with self.lock:
            if len(self.connections) < self.pool_size:
                self.connections.append(conn)
            else:
                conn.close()

@lru_cache()
def get_connection_pool() -> SnowflakeConnectionPool:
    return SnowflakeConnectionPool(pool_size=5)
```

### 3.2 Add Comprehensive Error Handling

**Problem:** Inconsistent error handling, generic messages to users.

**Solution:**

```python
# backend/app/middleware/error_handler.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class DataNotFoundError(APIError):
    """Data not found."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=404, details=details)

class ServiceUnavailableError(APIError):
    """External service unavailable."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=503, details=details)

async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors."""
    logger.error(
        f"API Error: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "details": exc.details
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )

# Register in main.py
app.add_exception_handler(APIError, api_error_handler)
```

### 3.3 Add Retry Logic

**Problem:** No retry for transient failures.

**Solution:**

```python
# backend/app/utils/retry.py

from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise

                    logger.warning(
                        f"Attempt {attempt} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1

        return wrapper
    return decorator

# Usage:
@retry(max_attempts=3, delay=1.0)
def fetch_from_snowflake(query: str):
    return snowflake_service.execute(query)
```

---

## 🔵 Phase 4: CODE QUALITY (Week 3 - 4 hours)

### 4.1 Remove Hardcoded Values

**Problem:** Magic numbers everywhere.

**Solution:** Configuration management.

```python
# backend/app/config/constants.py

from pydantic import BaseModel
from typing import Dict

class ModelCoefficients(BaseModel):
    """Validated model coefficients."""
    speed: float = 0.466
    consistency: float = 0.291
    racecraft: float = 0.149
    tire_management: float = 0.095

    def __post_init__(self):
        total = sum([self.speed, self.consistency, self.racecraft, self.tire_management])
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Coefficients must sum to 1.0, got {total}")

class AppConstants:
    """Application-wide constants."""

    # Model configuration
    MODEL_COEFFICIENTS = ModelCoefficients()

    # API defaults
    DEFAULT_PAGINATION_LIMIT = 50
    MAX_PAGINATION_LIMIT = 100

    # Skills page defaults
    TOP_DRIVERS_COUNT = 3
    SKILLS_BUDGET = 320

    # Track IDs (should eventually come from database)
    TRACK_IDS: Dict[str, str] = {
        "barber": "barber_motorsports_park",
        "cota": "circuit_of_the_americas",
        # ... etc
    }
```

### 4.2 Add Input Validation

**Problem:** No validation on API endpoints.

**Solution:**

```python
# backend/app/api/routes.py

from pydantic import BaseModel, Field, validator
from typing import Optional

class PredictionRequest(BaseModel):
    """Validated prediction request."""
    driver_number: int = Field(..., ge=1, le=99, description="Driver number (1-99)")
    track_id: str = Field(..., min_length=1, max_length=50)
    skill_adjustments: Optional[Dict[str, float]] = Field(default=None)

    @validator('skill_adjustments')
    def validate_adjustments(cls, v):
        if v is None:
            return v

        valid_skills = {'speed', 'consistency', 'racecraft', 'tire_management'}
        if not set(v.keys()).issubset(valid_skills):
            raise ValueError(f"Invalid skills. Must be one of: {valid_skills}")

        for value in v.values():
            if not -50 <= value <= 50:
                raise ValueError("Skill adjustments must be between -50 and 50")

        return v

@router.post("/predict")
async def predict_circuit_fit(request: PredictionRequest):
    """Predict circuit fit with validated input."""
    # Input is already validated by Pydantic
    pass
```

---

## 📊 SUCCESS METRICS

### Phase 1 Complete When:
- ✅ Skills page loads in production
- ✅ API calls take < 500ms
- ✅ No CORS errors
- ✅ Clear deployment documentation

### Phase 2 Complete When:
- ✅ Single `UnifiedDataService` for all data access
- ✅ SQLite database removed
- ✅ All data comes from either cache (JSON) or Snowflake
- ✅ Cache refresh process documented and scheduled

### Phase 3 Complete When:
- ✅ Connection pooling implemented
- ✅ All endpoints have proper error handling
- ✅ Retry logic on external service calls
- ✅ Error logs include context and are actionable

### Phase 4 Complete When:
- ✅ No hardcoded values in route handlers
- ✅ All API inputs validated with Pydantic
- ✅ Configuration centralized in `constants.py`
- ✅ Code passes linting with no warnings

---

## 🚀 IMPLEMENTATION SCHEDULE

### Tonight (30 minutes)
1. Set VITE_API_URL in Vercel dashboard
2. Verify Skills page works

### Tomorrow (2 hours)
1. Add `/api/factors/{factor}/top-average` endpoint
2. Update Skills.jsx to use new endpoint
3. Document deployment architecture in README

### Week 1 (8 hours)
1. Day 1-2: Build `UnifiedDataService`
2. Day 3: Migrate from SQLite to JSON
3. Day 4: Update all routes to use unified service
4. Day 5: Testing and documentation

### Week 2 (6 hours)
1. Day 1: Implement connection pooling
2. Day 2-3: Add comprehensive error handling
3. Day 4: Add retry logic and monitoring

### Week 3 (4 hours)
1. Day 1-2: Extract constants and configuration
2. Day 3: Add input validation
3. Day 4: Final testing and documentation

---

## NOTES

- **Do NOT try to do everything at once**
- Each phase builds on the previous
- Test thoroughly after each change
- Document as you go
- Keep the app working throughout the refactor

---

**Created:** 2025-11-11
**Author:** Claude Code
**Status:** Planning Phase
