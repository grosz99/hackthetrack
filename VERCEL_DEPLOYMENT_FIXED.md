# VERCEL DEPLOYMENT - COMPLETE SOLUTION

## WHAT WAS FIXED

### Critical Bugs Identified & Resolved:

1. **DOUBLE `/api` PREFIX BUG** ✅ FIXED
   - **Problem**: Backend routes had `prefix="/api"` AND frontend was adding `/api` again
   - **Result**: Requests went to `/api/api/drivers` (404 error)
   - **Solution**: Moved prefix to `main.py` router inclusion, updated frontend to use empty string in production

2. **VERCEL ROUTING MISCONFIGURATION** ✅ FIXED
   - **Problem**: Using `builds` + `routes` (legacy v1 approach)
   - **Solution**: Switched to `rewrites` with proper SPA fallback

3. **FRONTEND BUILD PATH** ✅ FIXED
   - **Problem**: Vercel didn't know where to find built frontend files
   - **Solution**: Added `buildCommand` and `outputDirectory` to `vercel.json`

4. **SQLITE DATABASE PATH** ✅ CONFIGURED
   - **Problem**: Database path resolution in serverless environment
   - **Solution**: Set `DATABASE_PATH` environment variable in `api/index.py`

---

## PROJECT STRUCTURE (CORRECT)

```
/Users/justingrosz/Documents/AI-Work/hackthetrack-master/
├── frontend/
│   ├── src/
│   │   └── services/
│   │       └── api.js          # API_BASE_URL = '' in production
│   ├── config/
│   │   └── vite.config.js      # outDir: 'dist', base: '/'
│   ├── dist/                   # Build output (generated)
│   └── package.json            # vercel-build script
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py       # router = APIRouter() - NO prefix
│   │   └── services/
│   ├── database/
│   │   └── connection.py       # Uses DATABASE_PATH env var
│   ├── main.py                 # app.include_router(router, prefix="/api")
│   └── requirements.txt
│
├── api/
│   └── index.py                # Vercel serverless entry point
│
├── circuit-fit.db              # SQLite database (292KB) - MUST BE AT ROOT
├── requirements.txt            # Python dependencies for Vercel
├── vercel.json                 # Deployment configuration
└── .vercelignore               # Exclude large files
```

---

## ROUTING FLOW (HOW IT WORKS)

### Production (Vercel):

```
User visits: https://your-app.vercel.app/

1. Frontend Routes (SPA):
   ├── / → frontend/dist/index.html
   ├── /drivers → frontend/dist/index.html (React Router handles)
   ├── /tracks → frontend/dist/index.html (React Router handles)
   └── /assets/* → frontend/dist/assets/* (static files)

2. API Routes (Serverless Function):
   ├── /api/drivers → api/index.py → FastAPI app → /api/drivers endpoint
   ├── /api/tracks → api/index.py → FastAPI app → /api/tracks endpoint
   └── /api/health → api/index.py → FastAPI app → /api/health endpoint
```

### How Requests Flow:

```
Browser: GET https://your-app.vercel.app/api/drivers

1. Vercel rewrites rule matches: /api/:path*
2. Vercel routes to: /api/index.py (Python serverless function)
3. Mangum handler wraps FastAPI app
4. FastAPI receives: /api/drivers
5. Router (with prefix="/api") matches: /drivers endpoint
6. Returns: JSON response with driver data
```

### Development (Local):

```
Frontend: http://localhost:5173
Backend:  http://localhost:8000

Frontend calls: http://localhost:8000/api/drivers
                ^^^^^^^^^^^^^^^^^^^^ API_BASE_URL
                                   ^^^^^^^^^^ Route with /api
```

---

## CONFIGURATION FILES EXPLAINED

### `vercel.json` - Deployment Configuration

```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "functions": {
    "api/index.py": {
      "runtime": "python3.9",
      "maxDuration": 30
    }
  },
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/index.py"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**Key Points:**
- `buildCommand`: Builds React frontend using Vite
- `outputDirectory`: Where Vercel finds the built HTML/JS/CSS
- `functions`: Configures Python serverless function
- `rewrites`:
  - `/api/*` → Python serverless function
  - Everything else → `index.html` (SPA fallback for React Router)

### `api/index.py` - Serverless Entry Point

```python
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Add backend to Python path
backend_dir = BASE_DIR / "backend"
sys.path.insert(0, str(backend_dir))

# Set database path
db_path = BASE_DIR / "circuit-fit.db"
os.environ["DATABASE_PATH"] = str(db_path)

# Import and wrap FastAPI app
from main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")
```

**Key Points:**
- Adds `backend/` to Python path so `from main import app` works
- Sets `DATABASE_PATH` environment variable for SQLite
- Wraps FastAPI app with Mangum for AWS Lambda/Vercel compatibility

### `frontend/src/services/api.js` - API Client

```javascript
const getApiBaseUrl = () => {
  if (import.meta.env.PROD) {
    return '';  // Production: routes already have /api prefix
  }
  return 'http://localhost:8000';  // Development: full URL
};

const API_BASE_URL = getApiBaseUrl();

// Example: GET /api/drivers
export async function getDrivers() {
  const response = await fetch(`${API_BASE_URL}/api/drivers`);
  //                             ^^^^^^^^^^^^^ Empty in prod
  //                                         ^^^^^^^^^^ Route
  return response.json();
}
```

**Key Points:**
- Production: `API_BASE_URL = ''`, so `''/api/drivers` = `/api/drivers`
- Development: `API_BASE_URL = 'http://localhost:8000'`, so `'http://localhost:8000/api/drivers'`

---

## DEPLOYMENT STEPS

### Step 1: Test Locally First

```bash
# Terminal 1: Start backend
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend
python main.py

# Terminal 2: Start frontend
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend
npm run dev

# Test in browser:
# http://localhost:5173
# http://localhost:5173/drivers
# http://localhost:8000/api/health
```

**Verify:**
- ✅ Frontend loads
- ✅ API calls work
- ✅ Data displays correctly

### Step 2: Build Frontend Locally

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend
npm run build

# Verify build output
ls -la dist/
# Should see: index.html, assets/, etc.
```

### Step 3: Commit Changes

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
git add .
git commit -m "fix: resolve Vercel deployment 404 errors

- Remove double /api prefix bug
- Fix vercel.json routing configuration
- Update frontend API service for production
- Configure SQLite database path for serverless"

git push origin master
```

### Step 4: Deploy to Vercel

#### Option A: Via Vercel CLI (Recommended)

```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
vercel --prod

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (your account)
# - Link to existing project? (Yes if exists, No for new)
# - Project name? (e.g., circuit-fit)
```

#### Option B: Via Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New Project"
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: (leave empty - uses vercel.json)
   - **Output Directory**: (leave empty - uses vercel.json)
5. Click "Deploy"

### Step 5: Verify Deployment

Once deployed, test these URLs:

```bash
# Replace YOUR-APP with your Vercel URL
BASE_URL="https://your-app.vercel.app"

# Frontend routes (should load React app)
curl $BASE_URL/
curl $BASE_URL/drivers
curl $BASE_URL/tracks

# API routes (should return JSON)
curl $BASE_URL/api/health
curl $BASE_URL/api/drivers
curl $BASE_URL/api/tracks
```

**Expected Results:**
- ✅ Frontend: HTML with React app
- ✅ API: JSON responses with data
- ✅ No 404 errors
- ✅ No authentication walls

---

## TROUBLESHOOTING

### Issue: 404 on `/api/*` routes

**Check:**
1. Verify `api/index.py` exists at project root
2. Check Vercel function logs:
   ```bash
   vercel logs --prod
   ```
3. Verify `requirements.txt` at root has all dependencies
4. Check Python runtime version in `vercel.json`

**Fix:**
```bash
# Ensure api/index.py exists
ls -la api/index.py

# Redeploy
vercel --prod --force
```

### Issue: 404 on frontend routes (e.g., `/drivers`)

**Check:**
1. Verify `vercel.json` has SPA fallback rewrite
2. Check that `frontend/dist/index.html` exists after build
3. Verify `outputDirectory` in `vercel.json`

**Fix:**
```bash
# Build locally and check output
cd frontend
npm run build
ls -la dist/

# Should see index.html and assets/
```

### Issue: Database not found error

**Check:**
1. Verify `circuit-fit.db` is at project root
2. Check it's NOT in `.vercelignore`
3. Verify size is under 50MB (yours is 292KB - fine)

**Fix:**
```bash
# Verify database location
ls -lh circuit-fit.db

# Check .vercelignore doesn't exclude .db files
grep -i "\.db" .vercelignore
```

### Issue: Module import errors in serverless function

**Check:**
1. Verify `sys.path.insert(0, str(backend_dir))` in `api/index.py`
2. Check backend folder structure
3. Verify all `__init__.py` files exist

**Fix:**
```bash
# Find missing __init__.py files
find backend -type d -exec test ! -e {}/__init__.py \; -print
```

### Issue: CORS errors in browser

**Check:**
1. Verify `backend/main.py` has CORS middleware
2. Check `allow_origin_regex` includes `*.vercel.app`
3. Verify `allow_credentials=True`

**Fix:**
Already configured correctly in `backend/main.py` lines 40-47.

---

## DATABASE CONSIDERATIONS

### Current Setup: SQLite (Read-Only)

**Pros:**
- ✅ Simple deployment (just include the file)
- ✅ No external dependencies
- ✅ Fast reads
- ✅ Works for 292KB database

**Cons:**
- ❌ Read-only in serverless (can't write)
- ❌ Cold starts might be slower
- ❌ Doesn't scale to multiple functions

**Recommendation:**
Keep SQLite for now since your app is **read-only** (analytics/visualization). If you need writes later, migrate to Vercel Postgres or Turso.

### Future: If You Need Database Writes

Consider these options:

1. **Vercel Postgres** (Recommended)
   - Managed PostgreSQL
   - Integrated with Vercel
   - Connection pooling built-in
   - Free tier available

2. **Turso** (SQLite in the cloud)
   - Keeps SQLite syntax
   - Distributed edge database
   - LibSQL (SQLite fork)
   - Generous free tier

3. **Supabase**
   - PostgreSQL with real-time features
   - REST API included
   - Free tier available

---

## SUCCESS CRITERIA CHECKLIST

After deployment, verify:

- [ ] ✅ Frontend loads at production URL (no 404)
- [ ] ✅ React Router routes work (`/drivers`, `/tracks`, etc.)
- [ ] ✅ API endpoints return data (no 404, no auth wall)
- [ ] ✅ Database queries work (data shows in frontend)
- [ ] ✅ No CORS errors in browser console
- [ ] ✅ Function logs show no errors
- [ ] ✅ Build completes successfully
- [ ] ✅ Deployment is repeatable

---

## ALTERNATIVE OPTIONS (IF VERCEL STILL FAILS)

If you continue having issues with Vercel after following this guide, here are alternatives:

### Option 1: Separate Frontend + Backend Deployments

**Frontend:** Vercel (static hosting only)
**Backend:** Railway, Render, or Fly.io

**Pros:**
- Simpler frontend deployment
- Backend runs as traditional server (not serverless)
- Can use SQLite with writes

**Cons:**
- Need to manage two deployments
- CORS configuration required
- Separate domains or subdomains

### Option 2: All-in-One Platform

**Platform:** Railway or Render

**Pros:**
- Single deployment
- Traditional server (not serverless)
- Can use SQLite with writes
- Simpler configuration

**Cons:**
- Not as fast as Vercel's edge network
- Slightly more expensive for traffic

### Option 3: Containerize Everything

**Platform:** Fly.io or Railway with Docker

**Pros:**
- Complete control
- Can use SQLite with writes
- Runs exactly like local development

**Cons:**
- Need to create Dockerfile
- More complex setup
- Longer deploy times

---

## FINAL NOTES

**This configuration SHOULD work on Vercel.** The issues you were experiencing were configuration bugs, not fundamental incompatibilities.

**If deployment still fails:**
1. Check Vercel function logs: `vercel logs --prod`
2. Verify build logs in Vercel dashboard
3. Test the serverless function locally:
   ```bash
   vercel dev
   ```

**If you need help:**
- Share the Vercel deployment URL
- Share the error logs
- Share the browser console errors

The stack (React + FastAPI + SQLite) is proven to work on Vercel when configured correctly.
