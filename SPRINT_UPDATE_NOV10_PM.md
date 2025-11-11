# Sprint Update - November 10, 2025 (Evening)

**Time**: 5:30 PM
**Goal**: Deploy working Barber telemetry coaching to Vercel
**Status**: Code review and cleanup phase

---

## 🎯 Current State Assessment

### ✅ What's Working (Production Ready)

#### **Backend API Endpoints** (localhost:8000)
- ✅ `GET /api/drivers` - Returns 31 drivers from JSON
- ✅ `GET /api/drivers/{id}/match` - Cosine similarity matching
- ✅ `GET /api/drivers/{id}/telemetry-coaching` - **NEW!** Turn-by-turn coaching
- ✅ `GET /api/health` - Health check
- ✅ Weighted scoring (Speed 46.6%, Consistency 29.1%, Racecraft 14.9%, Tire 9.5%)

**Data Source**: 100% JSON files (~500KB total)
- `driver_factors.json` (204KB) - 34 drivers, 4 factors each
- `telemetry_coaching_insights.json` (98KB) - 34 drivers at Barber R1+R2
- `driver_season_stats.json` (11KB)
- `driver_race_results.json` (288KB)

#### **Frontend Pages** (React + Vite)
- ✅ Rankings page - Working, displays driver table
- ✅ DriverContext - Manages state, fetches from API
- ⚠️ Improve/Performance Analysis page - **NOT YET BUILT**

---

## ⚠️ Issues to Fix

### **Issue #1: Snowflake Dependencies (Not Needed)**

**Problem**: Code still references Snowflake even though we use JSON

**Files with Snowflake imports**:
```python
# backend/app/api/routes.py (lines 419, 576, 1063, 1095)
from ..services.snowflake_service import snowflake_service

# Line 419: /api/telemetry/compare endpoint
lap_data = snowflake_service.get_telemetry_data_filtered(...)
# Has CSV fallback but Snowflake is tried first

# Line 576: Health check
snowflake_health = snowflake_service.health_check()
# Fails with MFA error (non-blocking)

# Lines 1063, 1095: Legacy telemetry endpoints
# Not used by frontend
```

**Impact**:
- ❌ Deployment to Vercel will fail (Snowflake requires private keys)
- ❌ Health endpoint shows Snowflake errors in logs
- ❌ Slower startup (tries Snowflake connection first)

**Solution**: Remove Snowflake entirely, use only JSON/CSV files

---

### **Issue #2: Missing Performance Analysis UI**

**Problem**: Design exists, data exists, but no component built

**What We Have**:
- ✅ API endpoint: `/api/drivers/7/telemetry-coaching?track_id=barber&race_num=1`
- ✅ Data: 34 drivers at Barber with turn-by-turn coaching
- ✅ Design mockup: `design/New_Design/Screenshot 2025-11-10 at 10.16.48 AM.png`

**What's Missing**:
- ❌ React component to display insights
- ❌ Route to navigate to /improve page
- ❌ Integration with DriverContext

**Required Component Structure**:
```
frontend/src/pages/Improve/
  ├── Improve.jsx              # Main page
  └── Improve.css              # Styling

frontend/src/components/
  ├── PerformanceAnalysis/
  │   ├── PerformanceAnalysis.jsx
  │   └── PerformanceAnalysis.css
  └── TelemetryInsightCard/
      ├── TelemetryInsightCard.jsx
      └── TelemetryInsightCard.css
```

---

### **Issue #3: Vercel Deployment Config**

**Problem**: No Vercel configuration for serverless functions

**What's Needed**:
```json
// vercel.json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "dist" }
    },
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "backend/main.py" },
    { "src": "/(.*)", "dest": "frontend/$1" }
  ]
}
```

**Also Need**:
- `backend/requirements.txt` - Clean dependencies (remove Snowflake)
- `backend/vercel_app.py` - Wrapper for FastAPI on Vercel
- Environment variables in Vercel dashboard

---

## 📊 Code Metrics

### Backend
```
Total Lines: ~4,500
Services: 8 files
  - data_loader.py: 450 lines (✅ Uses JSON)
  - snowflake_service.py: 320 lines (❌ DELETE)
  - ai_strategy.py: 200 lines (✅ Keep)
  - factor_analyzer.py: 495 lines (✅ Keep)

Routes: 1,365 lines
  - 68 endpoints total
  - 4 use Snowflake (lines 419, 576, 1063, 1095)
  - 64 use JSON only

Data Files: 540KB
  - driver_factors.json: 204KB
  - telemetry_coaching_insights.json: 98KB
  - driver_race_results.json: 288KB
  - Other: ~50KB
```

### Frontend
```
Pages: 10
  - Rankings ✅ (working)
  - Improve ⚠️ (empty stub)
  - Overview ✅
  - Skills ✅
  - Others...

Components: 12
  - RankingsTable ✅ (updated with weighted scores)
  - PerformanceRadar ✅
  - DriverCard ✅
  - PerformanceAnalysis ❌ (NOT BUILT)
  - TelemetryInsightCard ❌ (NOT BUILT)
```

---

## 🎯 Sprint Tasks (Next 2 Hours)

### **Task 1: Remove Snowflake Dependencies** (30 min)
**Owner**: Backend cleanup
**Priority**: HIGH - Blocks Vercel deployment

**Actions**:
1. Comment out Snowflake imports in routes.py (lines 419, 576, 1063, 1095)
2. Remove snowflake_service.py (or rename to .bak)
3. Update requirements.txt - remove snowflake-connector-python
4. Test that `/api/drivers` still works
5. Update .env.example - remove Snowflake vars

**Success Criteria**:
- [ ] Backend starts without Snowflake connection attempt
- [ ] `/api/drivers` returns 200 OK
- [ ] `/api/health` returns 200 OK (without Snowflake check)
- [ ] No Snowflake errors in logs

---

### **Task 2: Build Performance Analysis Component** (60 min)
**Owner**: Frontend development
**Priority**: HIGH - User-facing feature

**Design Reference**: `design/New_Design/Screenshot 2025-11-10 at 10.16.48 AM.png`

**Component Spec**:
```jsx
// frontend/src/components/PerformanceAnalysis/PerformanceAnalysis.jsx

<PerformanceAnalysis driverNumber={7} trackId="barber" raceNum={1}>

  {/* Team Principal's Note (Yellow Box) */}
  <TeamNote>
    Focus on Speed - you're 4/7 corners off pace at Barber
  </TeamNote>

  {/* Priority Areas (Red Bars) */}
  <PriorityAreas>
    <InsightCard
      corner={5}
      insight="Brake 74m earlier"
      factor="Consistency"
      severity="high"
    />
    <InsightCard
      corner={7}
      insight="Brake 24m earlier"
      factor="Consistency"
      severity="medium"
    />
  </PriorityAreas>

  {/* Top Strengths (Green Checkmarks) */}
  <TopStrengths>
    <StrengthBadge corner={2} text="Similar to fastest driver ✓" />
    <StrengthBadge corner={3} text="Similar to fastest driver ✓" />
    <StrengthBadge corner={6} text="Similar to fastest driver ✓" />
  </TopStrengths>

</PerformanceAnalysis>
```

**API Integration**:
```javascript
// Fetch insights
const response = await api.get(
  `/api/drivers/${driverNumber}/telemetry-coaching`,
  { params: { track_id: 'barber', race_num: 1 } }
);

// Response structure:
{
  "driver_number": 7,
  "summary": {
    "total_corners": 7,
    "corners_on_pace": 3,
    "corners_need_work": 4,
    "primary_weakness": "Speed"
  },
  "key_insights": [
    "Turn 5: Brake 74m EARLIER (Consistency)",
    "Turn 7: Brake 24m EARLIER (Consistency)"
  ],
  "factor_breakdown": {
    "Racecraft": 2,
    "Speed": 3,
    "Consistency": 2
  }
}
```

**Success Criteria**:
- [ ] Component renders with design mockup styling
- [ ] Fetches data from API
- [ ] Displays priority areas (red bars)
- [ ] Displays strengths (green checkmarks)
- [ ] Shows "Team Note" summary at top
- [ ] Responsive on mobile

---

### **Task 3: Configure Vercel Deployment** (30 min)
**Owner**: DevOps
**Priority**: HIGH - Deployment target

**Actions**:
1. Create `vercel.json` in project root
2. Create `backend/vercel_app.py` (FastAPI wrapper)
3. Clean up `backend/requirements.txt`:
   ```
   # Remove:
   snowflake-connector-python
   cryptography

   # Keep:
   fastapi
   uvicorn
   pandas
   numpy
   pydantic
   python-multipart
   ```
4. Test local build: `vercel dev`
5. Deploy: `vercel --prod`

**Environment Variables (Vercel Dashboard)**:
```
PYTHON_VERSION=3.11
```

**Success Criteria**:
- [ ] `vercel dev` runs locally
- [ ] Frontend loads at localhost:3000
- [ ] API responds at localhost:3000/api/drivers
- [ ] Production deploy succeeds
- [ ] Live URL accessible

---

## 📈 Expected Outcomes

### **After This Sprint**:
1. ✅ Clean backend (no Snowflake dependencies)
2. ✅ Working Performance Analysis UI for Barber
3. ✅ Deployed to Vercel (live URL)
4. ✅ Demo-ready for user feedback

### **Metrics to Track**:
- API response time < 100ms (JSON-only)
- Frontend load time < 2s
- Zero deployment errors
- All 31 drivers have coaching data

---

## 🚀 Post-Sprint (Tomorrow)

1. Expand to all 5 tracks (COTA, Road America, Sonoma, VIR)
2. Add track selector dropdown
3. Build comparison view (driver vs driver)
4. Add achievements/gamification

---

## 📝 Decision Log

**Decision 1**: Remove Snowflake entirely
- **Reason**: MFA hassles, deployment complexity, not needed (data is 428KB)
- **Impact**: Simpler deployment, faster API, no external dependencies
- **Trade-off**: Can't query 15.7M rows live (but we don't need to)

**Decision 2**: Deploy to Vercel (not Heroku)
- **Reason**: Simpler, faster, free tier sufficient, supports serverless Python
- **Impact**: No server management, auto-scaling, global CDN
- **Trade-off**: Serverless cold starts (~200ms)

**Decision 3**: Start with Barber only for UI
- **Reason**: Validate UX first, then expand
- **Impact**: Faster iteration, focused testing
- **Trade-off**: Users can't see other tracks yet (will add tomorrow)

---

**Sprint Start**: 5:30 PM
**Sprint End**: 7:30 PM (target)
**Review**: 7:30 PM - Show working UI on Vercel

---

**Created**: November 10, 2025, 5:30 PM
**Updated**: November 10, 2025, 5:30 PM
**Status**: Ready to execute
