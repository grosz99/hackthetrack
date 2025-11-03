# CIRCUIT FIT - VERCEL DEPLOYMENT ARCHITECTURE

## COMPLETE SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VERCEL DEPLOYMENT PLATFORM                          │
│                    https://your-app.vercel.app                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ User Request
                                    ▼
                        ┌───────────────────────┐
                        │   Vercel Edge CDN     │
                        │  (Global Network)     │
                        └───────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
         ┌──────────▼──────────┐       ┌───────────▼────────────┐
         │   Frontend Routes   │       │     API Routes         │
         │  (Static Assets)    │       │ (Serverless Function)  │
         └─────────────────────┘       └────────────────────────┘
                    │                               │
                    │                               │
         ┌──────────▼──────────┐       ┌───────────▼────────────┐
         │  React SPA + Vite   │       │   Python Runtime       │
         │  ================   │       │   ==============       │
         │                     │       │                        │
         │  • index.html       │       │  api/index.py          │
         │  • assets/*.js      │       │  └─> Mangum Handler    │
         │  • assets/*.css     │       │      └─> FastAPI App   │
         │  • React Router     │       │                        │
         └─────────────────────┘       └────────────────────────┘
                    │                               │
                    │ API Calls                     │
                    │ /api/*                        │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  FastAPI Application  │
                        │  ===================  │
                        │                       │
                        │  backend/main.py      │
                        │  └─> router           │
                        │      prefix="/api"    │
                        └───────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
         ┌──────────▼─────┐  ┌─────▼──────┐  ┌────▼──────┐
         │  /api/drivers  │  │ /api/tracks│  │ /api/chat │
         │                │  │            │  │           │
         │  routes.py     │  │ routes.py  │  │ routes.py │
         └────────────────┘  └────────────┘  └───────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │   Data Layer          │
                        │   ==========          │
                        │                       │
                        │  data_loader.py       │
                        │  ai_strategy.py       │
                        └───────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │   SQLite Database     │
                        │   ===============     │
                        │                       │
                        │  circuit-fit.db       │
                        │  (292KB, read-only)   │
                        │                       │
                        │  Tables:              │
                        │  • drivers            │
                        │  • tracks             │
                        │  • race_results       │
                        │  • factor_breakdowns  │
                        └───────────────────────┘
```

---

## REQUEST FLOW DIAGRAMS

### SCENARIO 1: User Visits Homepage

```
User Browser
    │
    │ GET https://your-app.vercel.app/
    ▼
Vercel Edge CDN
    │
    │ Match: source="/(.*)" → destination="/index.html"
    ▼
Static File (frontend/dist/index.html)
    │
    │ Return HTML + JS bundles
    ▼
User Browser
    │
    │ Parse HTML, Load React App
    ▼
React Router
    │
    │ Client-side routing initialized
    ▼
Homepage Component Rendered
```

### SCENARIO 2: User Navigates to /drivers

```
User Browser (React App Already Loaded)
    │
    │ Click: Navigate to /drivers
    ▼
React Router (Client-Side)
    │
    │ Match route: /drivers → DriversPage component
    │ No server request (SPA behavior)
    ▼
DriversPage Component
    │
    │ useEffect: Fetch drivers data
    │ API Call: GET /api/drivers
    ▼
Vercel Edge CDN
    │
    │ Match: source="/api/:path*" → destination="/api/index.py"
    ▼
Serverless Function (api/index.py)
    │
    │ Initialize Python runtime (cold start ~1-2s)
    │ Import FastAPI app
    │ Wrap with Mangum handler
    ▼
FastAPI Application (backend/main.py)
    │
    │ Route: /api/drivers
    │ Router matches (prefix="/api")
    ▼
Routes Handler (backend/app/api/routes.py)
    │
    │ @router.get("/drivers")
    │ Call: data_loader.get_all_drivers()
    ▼
Data Loader (backend/app/services/data_loader.py)
    │
    │ Query SQLite database
    │ SELECT * FROM drivers
    ▼
SQLite Database (circuit-fit.db)
    │
    │ Return driver records
    ▼
Data Loader
    │
    │ Convert to Driver Pydantic models
    ▼
Routes Handler
    │
    │ Return JSON response
    ▼
FastAPI Application
    │
    │ Serialize to JSON
    │ Add CORS headers
    ▼
Serverless Function
    │
    │ Mangum wraps response
    ▼
Vercel Edge CDN
    │
    │ Cache response (optional)
    ▼
User Browser
    │
    │ Parse JSON, Update UI
    ▼
DriversPage Component
    │
    │ Render driver list with data
    ▼
User sees drivers displayed
```

### SCENARIO 3: User Refreshes /drivers Page

```
User Browser
    │
    │ Refresh: GET https://your-app.vercel.app/drivers
    ▼
Vercel Edge CDN
    │
    │ Match: source="/(.*)" → destination="/index.html"
    │ (SPA fallback - sends index.html for any non-API route)
    ▼
Static File (frontend/dist/index.html)
    │
    │ Return same HTML as homepage
    ▼
User Browser
    │
    │ Parse HTML, Load React App
    ▼
React Router
    │
    │ Check window.location.pathname → "/drivers"
    │ Match route: /drivers → DriversPage component
    ▼
DriversPage Component
    │
    │ useEffect: Fetch drivers data
    │ API Call: GET /api/drivers
    ▼
(Same flow as Scenario 2 for API call)
```

---

## FILE ROUTING EXPLAINED

### Frontend Routes (Static Assets)

```
Request: https://your-app.vercel.app/
Vercel checks rewrites:
  ✗ /api/:path* → No match
  ✓ /(.*) → Match
Result: Serve /index.html

Request: https://your-app.vercel.app/drivers
Vercel checks rewrites:
  ✗ /api/:path* → No match
  ✓ /(.*) → Match
Result: Serve /index.html (React Router handles /drivers)

Request: https://your-app.vercel.app/assets/index-BBCkBI1Z.js
Vercel checks rewrites:
  ✗ /api/:path* → No match
  ✓ /(.*) → Match
Result: Serve /assets/index-BBCkBI1Z.js (actual file)

Request: https://your-app.vercel.app/vite.svg
Vercel checks rewrites:
  ✗ /api/:path* → No match
  ✓ /(.*) → Match
Result: Serve /vite.svg (actual file)
```

### API Routes (Serverless Function)

```
Request: https://your-app.vercel.app/api/drivers
Vercel checks rewrites:
  ✓ /api/:path* → Match
Result: Execute /api/index.py → FastAPI → /api/drivers endpoint

Request: https://your-app.vercel.app/api/tracks
Vercel checks rewrites:
  ✓ /api/:path* → Match
Result: Execute /api/index.py → FastAPI → /api/tracks endpoint

Request: https://your-app.vercel.app/api/health
Vercel checks rewrites:
  ✓ /api/:path* → Match
Result: Execute /api/index.py → FastAPI → /api/health endpoint
```

---

## API PREFIX FLOW (THE FIX)

### BEFORE (BROKEN - Double /api prefix):

```
Frontend Code:
  API_BASE_URL = '/api'  ❌
  fetch(`${API_BASE_URL}/api/drivers`)
  → GET /api/api/drivers

Backend Code:
  router = APIRouter(prefix="/api")  ❌
  @router.get("/drivers")
  → Route: /api/drivers

Result: Request to /api/api/drivers doesn't match /api/drivers → 404
```

### AFTER (FIXED - Single /api prefix):

```
Frontend Code:
  API_BASE_URL = ''  ✅ (empty in production)
  fetch(`${API_BASE_URL}/api/drivers`)
  → GET /api/drivers

Backend Code:
  router = APIRouter()  ✅ (no prefix)
  app.include_router(router, prefix="/api")  ✅
  @router.get("/drivers")
  → Route: /api/drivers

Result: Request to /api/drivers matches /api/drivers → Success!
```

---

## ENVIRONMENT-SPECIFIC BEHAVIOR

### Development (Local)

```javascript
// frontend/src/services/api.js
API_BASE_URL = 'http://localhost:8000'  // Full URL

// API Call
fetch(`${API_BASE_URL}/api/drivers`)
→ GET http://localhost:8000/api/drivers
```

```python
# backend/main.py
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

# Route: /api/drivers
# Backend runs on: http://localhost:8000
# Full URL: http://localhost:8000/api/drivers
```

### Production (Vercel)

```javascript
// frontend/src/services/api.js
API_BASE_URL = ''  // Empty string

// API Call
fetch(`${API_BASE_URL}/api/drivers`)
→ GET /api/drivers (relative URL)
```

```python
# api/index.py
handler = Mangum(app, lifespan="off")

# Serverless function handles: /api/*
# Route in FastAPI: /api/drivers
# Full URL: https://your-app.vercel.app/api/drivers
```

---

## COLD START VS WARM START

### Cold Start (First Request or After ~5 Minutes Idle)

```
1. Vercel receives request: /api/drivers
2. Initialize Python 3.9 runtime          [~500ms]
3. Import dependencies (FastAPI, pandas)  [~800ms]
4. Import application code                [~300ms]
5. Execute request handler                [~200ms]
6. Query SQLite database                  [~50ms]
7. Return response                        [~50ms]
───────────────────────────────────────────────────
Total: ~1.9 seconds
```

### Warm Start (Function Already Initialized)

```
1. Vercel receives request: /api/drivers
2. Function already loaded                [~0ms]
3. Execute request handler                [~200ms]
4. Query SQLite database                  [~50ms]
5. Return response                        [~50ms]
───────────────────────────────────────────────────
Total: ~300ms
```

**Optimization Tips:**
- Vercel keeps functions warm for ~5 minutes
- High traffic = more warm starts
- Consider upgrading to Pro for longer warm periods

---

## DATABASE ACCESS PATTERN

```
SQLite Database (Read-Only)
  │
  │ Deployed to: /var/task/circuit-fit.db
  │ Size: 292KB
  │ Mode: Read-only (Vercel filesystem is immutable)
  │
  ├─> Connection Pool (per function instance)
  │   └─> SQLite Connection
  │       ├─> check_same_thread=False
  │       ├─> row_factory=sqlite3.Row (dict results)
  │       └─> PRAGMA foreign_keys=ON
  │
  └─> Queries
      ├─> SELECT * FROM drivers
      ├─> SELECT * FROM tracks
      ├─> SELECT * FROM race_results WHERE driver_number=?
      └─> SELECT * FROM factor_breakdowns WHERE driver_number=?

Note: Each serverless function instance maintains its own connection.
Multiple concurrent requests = multiple function instances = multiple connections.
```

---

## CACHING STRATEGY

### Static Assets (Frontend)

```
File: /assets/index-BBCkBI1Z.js
Cache-Control: public, max-age=31536000, immutable
  → Cached for 1 year (safe due to hash in filename)

File: /index.html
Cache-Control: public, max-age=0, must-revalidate
  → Never cached (always checks for updates)
```

### API Responses

```
Route: /api/drivers
Cache-Control: no-store, must-revalidate
  → Never cached (dynamic data)

Consider adding:
  - Redis for expensive queries
  - Vercel Edge Config for static data
  - stale-while-revalidate for acceptable staleness
```

---

## SCALABILITY CONSIDERATIONS

### Current Architecture Limits

```
Serverless Functions:
  • Max duration: 30 seconds (configured in vercel.json)
  • Max memory: 1024MB (default)
  • Concurrent: 100+ instances (scales automatically)

SQLite Database:
  • Read-only: ✓ No write conflicts
  • Size: 292KB (excellent for serverless)
  • Concurrent reads: ✓ Each instance has own connection

Frontend:
  • Static files: Unlimited (CDN)
  • Global distribution: ✓ Edge CDN
  • Bandwidth: Unlimited (Vercel free tier: 100GB/month)
```

### When to Consider Migration

**Migrate Database if:**
- Need write operations
- Database grows >10MB
- Need relational joins across multiple tables frequently
- Need real-time updates

**Consider Alternatives:**
- Vercel Postgres (writes, relations, 256MB free)
- Turso (distributed SQLite, 8GB free)
- Supabase (PostgreSQL + realtime, 500MB free)

---

## MONITORING & DEBUGGING

### Vercel Logs

```bash
# Real-time logs
vercel logs --prod --follow

# Filter by function
vercel logs --prod | grep "api/index.py"

# Search for errors
vercel logs --prod | grep -i error
```

### Browser DevTools

```
Network Tab:
  • Check request URLs (should be /api/*)
  • Check response status (200 for success)
  • Check response time (<2s cold, <500ms warm)

Console Tab:
  • No CORS errors
  • No 404 errors
  • No JavaScript errors
```

### Performance Monitoring

```
Key Metrics:
  • Frontend First Contentful Paint: <1.5s
  • API Response Time (cold): <2s
  • API Response Time (warm): <500ms
  • Database Query Time: <100ms
  • Total Page Load: <3s
```

---

## COMPARISON: CURRENT VS PREVIOUS FAILED ATTEMPTS

### Failed Attempt (builds + routes):

```json
{
  "builds": [
    { "src": "api/index.py", "use": "@vercel/python" },
    { "src": "frontend/package.json", "use": "@vercel/static-build" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/index.py" },
    { "src": "/(.*)", "dest": "/frontend/dist/index.html" }
  ]
}
```

**Problems:**
- `builds` is legacy (deprecated in v2)
- `routes` don't handle SPA fallback correctly
- File paths were incorrect (`/frontend/dist/` instead of `/`)

### Current Working Config (rewrites):

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "rewrites": [
    { "source": "/api/:path*", "destination": "/api/index.py" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**Improvements:**
- `rewrites` properly handles SPA routing
- Correct file paths (Vercel serves from outputDirectory root)
- Explicit build command (no ambiguity)

---

This architecture provides a complete mental model of how your application
is deployed and operates on Vercel's platform.
