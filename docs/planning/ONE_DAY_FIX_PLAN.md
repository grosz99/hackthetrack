# ONE DAY FIX PLAN
## Reality Check: What We Can Actually Accomplish in 8 Hours

---

## 🎯 **GOAL: Working, Stable, Single Source of Truth**

**NOT:** Perfect architecture
**YES:** Skills page works, data is consistent, deployment is clear

---

## ⏰ **HOUR-BY-HOUR BREAKDOWN**

### **TONIGHT (30 minutes - DO THIS NOW)**

**Task:** Get Skills page working in production

**Steps:**
1. Vercel Dashboard → Environment Variables → Set `VITE_API_URL`
2. Redeploy
3. Test Skills page - verify it loads factor breakdowns

**Success:** You can click a Skills tile and see data

---

### **HOUR 1-2: Eliminate SQLite (Morning - 2 hours)**

**Task:** Merge circuit-fit.db data into existing JSON files

**Why:** SQLite is the root of your sync problems. Kill it.

**Script to create:**
```python
# scripts/migrate_sqlite_to_json.py

import sqlite3
import json
from pathlib import Path

# Read from SQLite
conn = sqlite3.connect('circuit-fit.db')
cursor = conn.cursor()

# Load existing driver_factors.json
with open('backend/data/driver_factors.json', 'r') as f:
    data = json.load(f)

# Merge SQLite factor breakdown data
cursor.execute("""
    SELECT driver_number, factor_name, variable_name, value, percentile
    FROM factor_variables
""")

for row in cursor.fetchall():
    driver_num, factor, variable, value, percentile = row

    # Find driver in JSON
    for driver in data['drivers']:
        if driver['driver_number'] == driver_num:
            # Add variable breakdown
            if 'variables' not in driver['factors'][factor]:
                driver['factors'][factor]['variables'] = []

            driver['factors'][factor]['variables'].append({
                'name': variable,
                'value': value,
                'percentile': percentile
            })

# Save enhanced JSON
with open('backend/data/driver_factors_complete.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ SQLite data migrated to JSON")
```

**Run it:**
```bash
cd backend
python scripts/migrate_sqlite_to_json.py
mv data/driver_factors_complete.json data/driver_factors.json
git rm circuit-fit.db
```

**Update code:**
```python
# backend/app/services/factor_analyzer.py - DELETE ALL SQLITE CODE

# OLD (DELETE THIS):
def get_factor_breakdown(driver_number, factor_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(...)
    return cursor.fetchall()

# NEW (USE THIS):
def get_factor_breakdown(driver_number, factor_name):
    from app.services.data_loader import data_loader
    driver = data_loader.drivers.get(driver_number)
    if not driver:
        raise ValueError(f"Driver {driver_number} not found")

    factor = driver.factors.get(factor_name)
    if not factor:
        raise ValueError(f"Factor {factor_name} not found")

    return factor  # Already has variables from JSON
```

**Files to update:**
- `backend/app/services/factor_analyzer.py` - remove SQLite
- `backend/app/api/routes.py` - use data_loader instead of SQLite
- Delete `backend/database/` directory

**Success:** No more SQLite. All data comes from JSON.

---

### **HOUR 3-4: Fix Inefficient APIs (Afternoon - 2 hours)**

**Task:** Add efficient endpoints that return ONLY what frontend needs

**Current problem:**
```javascript
// Skills.jsx loads 40KB to calculate 1 number
const drivers = await api.get('/api/drivers')  // ALL 34 drivers
const top3 = drivers.sort(...).slice(0, 3)
const avg = top3.reduce((sum, d) => sum + d.speed, 0) / 3
```

**New endpoint:**
```python
# backend/app/api/routes.py

@router.get("/api/factors/{factor_name}/stats")
async def get_factor_stats(factor_name: str):
    """Get statistics for a factor WITHOUT loading all drivers."""

    drivers = list(data_loader.drivers.values())

    # Extract just the factor scores
    scores = [getattr(d, factor_name).score for d in drivers]
    scores.sort(reverse=True)

    return {
        "factor": factor_name,
        "top_3_average": sum(scores[:3]) / 3,
        "league_average": sum(scores) / len(scores),
        "min": min(scores),
        "max": max(scores),
        "count": len(scores)
    }
```

**Frontend update:**
```javascript
// frontend/src/pages/Skills.jsx

// OLD (delete):
const driversResponse = await api.get('/api/drivers')
const drivers = driversResponse.data
// ... sorting logic ...

// NEW (use this):
const statsResponse = await api.get(`/api/factors/${factor}/stats`)
const { top_3_average, league_average } = statsResponse.data
```

**Bandwidth saved:** 40KB → 200 bytes (200x improvement!)

**Success:** Skills page loads instantly, uses 200x less bandwidth

---

### **HOUR 5-6: Basic Error Handling (Afternoon - 2 hours)**

**Task:** Add consistent error handling so we know what breaks

**Create simple error handler:**
```python
# backend/app/utils/errors.py

class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(AppError):
    """Resource not found."""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class ValidationError(AppError):
    """Invalid input."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

# backend/main.py

from fastapi import Request
from fastapi.responses import JSONResponse
from app.utils.errors import AppError
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.error(f"{exc.status_code}: {exc.message} [{request.url.path}]")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "path": str(request.url.path)}
    )

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "path": str(request.url.path)}
    )
```

**Update routes to use it:**
```python
# backend/app/api/routes.py

from app.utils.errors import NotFoundError, ValidationError

@router.get("/api/drivers/{driver_number}")
async def get_driver(driver_number: int):
    driver = data_loader.drivers.get(driver_number)
    if not driver:
        raise NotFoundError(f"Driver {driver_number} not found")
    return driver

@router.get("/api/drivers/{driver_number}/factors/{factor_name}")
async def get_factor_breakdown(driver_number: int, factor_name: str):
    valid_factors = ['speed', 'consistency', 'racecraft', 'tire_management']
    if factor_name not in valid_factors:
        raise ValidationError(f"Invalid factor. Must be one of: {valid_factors}")

    driver = data_loader.drivers.get(driver_number)
    if not driver:
        raise NotFoundError(f"Driver {driver_number} not found")

    return driver.factors[factor_name]
```

**Success:** Errors are logged properly and return clear messages

---

### **HOUR 7: Deploy & Test (Evening - 1 hour)**

**Task:** Get everything deployed and verify it works

**Deployment checklist:**
```bash
# 1. Commit all changes
git add -A
git commit -m "fix: consolidate to JSON, efficient APIs, error handling"
git push origin master

# 2. Deploy backend to Heroku
git push heroku master

# 3. Verify Heroku deployment
heroku logs --tail -a hackthetrack-api

# 4. Vercel will auto-deploy frontend
# Check: https://vercel.com/dashboard

# 5. Test production
curl https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/drivers/13
curl https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/factors/speed/stats
```

**Manual testing:**
1. Open production site
2. Go to Rankings → Verify 31 drivers load
3. Click driver → Overview loads
4. Skills page → Click each tile → Factor breakdowns load
5. Check browser console → No errors

**Success:** Everything works in production

---

### **HOUR 8: Document (Evening - 1 hour)**

**Task:** Write clear docs so this doesn't break again

**Create/update:**

```markdown
# README.md

## Architecture

**Frontend:** React + Vite (Deployed on Vercel)
**Backend:** FastAPI (Deployed on Heroku)
**Data:** JSON files loaded into memory on startup

### Data Flow
```
User → Vercel (Static Site) → Heroku API → JSON Cache → Response
```

### Deployment

**Frontend (Vercel):**
1. Push to GitHub master branch
2. Vercel auto-deploys
3. Environment variable: `VITE_API_URL=https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api`

**Backend (Heroku):**
```bash
git push heroku master
```

### Data Updates

All data comes from JSON files in `backend/data/`:
- `dashboardData.json` - Driver/track overview
- `driver_factors.json` - Factor scores and breakdowns
- `driver_season_stats.json` - Season statistics
- `driver_race_results.json` - Race-by-race results

To update data:
1. Edit JSON files
2. Commit and push to GitHub
3. Deploy to Heroku
4. Heroku restart picks up new data

### API Endpoints

**Efficient endpoints (use these):**
- `GET /api/factors/{factor}/stats` - Factor statistics (200 bytes)
- `GET /api/drivers/{number}` - Single driver (2KB)

**Legacy endpoints (avoid in new code):**
- `GET /api/drivers` - All drivers (40KB)
```

**Success:** Someone else can understand and maintain this

---

## 📊 **END OF DAY SUCCESS CRITERIA**

### ✅ **You're Done When:**

1. **Skills page works** - Click any tile, see breakdown
2. **No SQLite** - `circuit-fit.db` deleted, all data from JSON
3. **Fast APIs** - Factor stats endpoint returns <1KB instead of 40KB
4. **Errors are clear** - Logs show what failed and where
5. **Deployment is documented** - README explains architecture
6. **Tests pass** - Can load Rankings, Overview, Skills pages

### ❌ **What We're NOT Doing:**

- ❌ Connection pooling (not needed for JSON)
- ❌ Snowflake integration (keeping it simple)
- ❌ Input validation on every endpoint (just key ones)
- ❌ Perfect code (just working code)
- ❌ Retry logic (can add later if needed)

---

## 🚨 **IF YOU GET STUCK**

### Skills page still broken?
→ Check Vercel env var is set correctly
→ Check Heroku logs: `heroku logs --tail -a hackthetrack-api`

### SQLite migration fails?
→ Skip it, just update routes to use data_loader directly
→ Delete SQLite references, return data from JSON

### Deployment fails?
→ Check Heroku logs
→ Make sure requirements.txt is up to date
→ scipy is removed from requirements.txt

---

## 📋 **TOMORROW'S CHECKLIST**

```bash
# Morning (Hour 1-2)
[ ] Run migrate_sqlite_to_json.py
[ ] Delete circuit-fit.db
[ ] Update factor_analyzer.py to use JSON
[ ] Update routes.py to use data_loader
[ ] Test locally: python backend/main.py

# Afternoon (Hour 3-6)
[ ] Add /api/factors/{factor}/stats endpoint
[ ] Update Skills.jsx to use new endpoint
[ ] Add error handling to main.py
[ ] Add NotFoundError, ValidationError classes
[ ] Update key routes to use error classes
[ ] Test locally

# Evening (Hour 7-8)
[ ] git commit and push
[ ] Deploy to Heroku
[ ] Test production site
[ ] Update README.md
[ ] Celebrate 🎉
```

---

**Created:** 2025-11-11 23:00
**Timeline:** 8 hours
**Approach:** Working > Perfect
**Focus:** Fix what's broken, document what works
