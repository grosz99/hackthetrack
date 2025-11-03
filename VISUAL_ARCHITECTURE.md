# Visual Architecture: FastAPI + React on Vercel

## 🎯 Problem We Solved

```
BEFORE (Not Working):
Frontend → https://your-app.vercel.app/api/drivers → 404 Error
Why? Backend handler was at /backend/api/index.py (wrong location)
```

```
AFTER (Working):
Frontend → https://your-app.vercel.app/api/drivers → 200 OK with data
Why? Backend handler moved to /api/index.py (correct location)
```

## 📁 Project Structure Transformation

### Before (Broken)
```
hackthetrack-master/
├── backend/
│   ├── api/
│   │   └── index.py          ❌ Wrong location for Vercel
│   ├── main.py
│   └── circuit-fit.db         ❌ Wrong location
├── frontend/
│   └── dist/
└── vercel.json                ❌ Simple config, missing Python
```

### After (Working)
```
hackthetrack-master/
├── api/                       ✅ Correct location
│   └── index.py              ✅ Serverless handler
├── backend/
│   ├── main.py               ✅ CORS updated
│   ├── database/
│   │   └── connection.py     ✅ DB path fixed
│   └── app/api/routes.py
├── circuit-fit.db            ✅ At root
├── frontend/
│   ├── src/services/
│   │   └── api.js            ✅ Auto-detect URL
│   └── dist/
└── vercel.json               ✅ Full Python config
```

## 🔄 Request Flow (Production)

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Browser                           │
│                                                             │
│  https://your-app.vercel.app                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Vercel Edge Network                        │
│                  (Global CDN + Router)                      │
└─────────────┬───────────────────────┬───────────────────────┘
              │                       │
              │ /api/*               │ /*
              ▼                       ▼
┌─────────────────────┐    ┌──────────────────────┐
│  Python Serverless  │    │   Static Frontend    │
│    Function         │    │   (React SPA)        │
│                     │    │                      │
│  /api/index.py      │    │  frontend/dist/      │
│         │           │    │                      │
│         ▼           │    │  • index.html        │
│  ┌──────────┐      │    │  • *.js bundles      │
│  │ FastAPI  │      │    │  • *.css             │
│  │   App    │      │    │  • assets/           │
│  └────┬─────┘      │    │                      │
│       │            │    └──────────────────────┘
│       ▼            │
│  ┌──────────┐     │
│  │ SQLite   │     │
│  │ Database │     │
│  └──────────┘     │
│  circuit-fit.db   │
└───────────────────┘
```

## 🔌 API Integration Flow

### Development (Local)
```
React Dev Server          FastAPI Dev Server
http://localhost:5173 → http://localhost:8000/api/drivers
                 ↓
        CORS allows localhost
                 ↓
        Returns JSON data
```

### Production (Vercel)
```
React Static Build         Python Serverless
https://app.vercel.app → /api/drivers (relative path)
                 ↓
        Same origin (no CORS needed)
                 ↓
        Returns JSON data
```

## 🛠️ Files Changed Summary

| File | Status | Purpose |
|------|--------|---------|
| `/api/index.py` | ✅ Created | Vercel serverless entry point |
| `/vercel.json` | ✅ Updated | Python + React build config |
| `/backend/database/connection.py` | ✅ Updated | Environment-aware DB path |
| `/backend/main.py` | ✅ Updated | CORS for all Vercel domains |
| `/frontend/src/services/api.js` | ✅ Updated | Auto-detect API URL |
| `/frontend/.env.production` | ✅ Created | Production env vars |
| `/.env.production` | ✅ Created | Root env vars |

## 🎨 Component Interaction Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                    Frontend (React)                           │
│                                                               │
│  ┌─────────────┐         ┌─────────────┐                    │
│  │ Dashboard   │────────▶│   API       │                    │
│  │ Component   │         │  Service    │                    │
│  └─────────────┘         └──────┬──────┘                    │
│                                  │                            │
│                   const url = import.meta.env.PROD           │
│                                ? '/api'                       │
│                                : 'http://localhost:8000'     │
└───────────────────────────────┬─────────────────────────────┘
                                │
                                │ HTTP Request
                                │ GET /api/drivers
                                ▼
┌────────────────────────────────────────────────────────────┐
│              Backend (FastAPI)                             │
│                                                            │
│  ┌────────────┐      ┌──────────────┐    ┌─────────────┐ │
│  │   CORS     │─────▶│   Routes     │───▶│ Data Loader │ │
│  │ Middleware │      │   Handler    │    │   Service   │ │
│  └────────────┘      └──────────────┘    └──────┬──────┘ │
│                                                   │        │
│                                                   ▼        │
│                                          ┌─────────────┐  │
│                                          │  Database   │  │
│                                          │ Connection  │  │
│                                          └──────┬──────┘  │
│                                                 │         │
└─────────────────────────────────────────────────┼─────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │  circuit-fit.db │
                                         │   (SQLite)      │
                                         └─────────────────┘
```

## 🚀 Deployment Process

```
┌─────────────┐
│   git push  │
│   to master │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│     Vercel Build Process                │
│                                         │
│  1. Clone repository                    │
│  2. Install dependencies:               │
│     - pip install -r requirements.txt   │
│     - cd frontend && npm install        │
│  3. Build frontend:                     │
│     - npm run build → dist/             │
│  4. Create Python serverless function:  │
│     - Bundle api/index.py               │
│     - Include backend/ modules          │
│     - Include circuit-fit.db            │
│  5. Deploy to edge network              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Deployment Complete             │
│                                         │
│  Frontend: https://app.vercel.app       │
│  API: https://app.vercel.app/api/*      │
│                                         │
│  Status: ✅ Live                        │
└─────────────────────────────────────────┘
```

## 🔍 Database Path Resolution Logic

```python
# In /api/index.py (runs first)
BASE_DIR = Path(__file__).parent.parent  # Project root
db_path = BASE_DIR / "circuit-fit.db"     # /var/task/circuit-fit.db
os.environ["DATABASE_PATH"] = str(db_path)

# In /backend/database/connection.py
env_db_path = os.environ.get("DATABASE_PATH")
if env_db_path:
    db_path = Path(env_db_path)  # Use environment variable
else:
    db_path = Path(__file__).parent.parent.parent / "circuit-fit.db"
```

### Why This Works
```
Vercel Deployment Structure:
/var/task/
├── api/
│   └── index.py           (sets DATABASE_PATH=/var/task/circuit-fit.db)
├── backend/
│   ├── main.py
│   └── database/
│       └── connection.py  (reads DATABASE_PATH from environment)
└── circuit-fit.db         (accessible via environment path)
```

## 📊 CORS Configuration

### Local Development
```python
allow_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8000",  # FastAPI dev server
]
```

### Production
```python
allow_origin_regex = r"https://.*\.vercel\.app"

# Matches:
# https://your-app.vercel.app
# https://your-app-abc123.vercel.app (preview)
# https://your-app-xyz789.vercel.app (preview)
```

## 🎯 API Endpoints Map

```
Base URL: https://your-app.vercel.app/api

Health & Info:
├─ GET  /health                    → {"status": "healthy", ...}

Drivers:
├─ GET  /drivers                   → [driver1, driver2, ...]
├─ GET  /drivers/{number}          → {driver details}
├─ GET  /drivers/{number}/stats    → {season stats}
├─ GET  /drivers/{number}/results  → [race results]
└─ GET  /drivers/{number}/factors/{factor}
    ├─ /factors/speed
    ├─ /factors/consistency
    ├─ /factors/racecraft
    └─ /factors/tire_management

Tracks:
├─ GET  /tracks                    → [track1, track2, ...]
└─ GET  /tracks/{id}               → {track details}

Predictions:
├─ POST /predict                   → {circuit fit prediction}
└─ POST /drivers/{number}/improve/predict

Telemetry:
├─ GET  /telemetry/compare         → {comparison data}
└─ GET  /telemetry/detailed        → {detailed telemetry}

AI Chat:
└─ POST /chat                      → {AI response}
```

## ✅ Success Verification Checklist

```
Deployment Success Indicators:

📦 Build Phase:
[ ] Vercel build completes without errors
[ ] Python function created successfully
[ ] Frontend dist/ folder generated
[ ] Database included in deployment

🌐 Runtime Phase:
[ ] https://app.vercel.app loads
[ ] GET /api/health returns 200
[ ] GET /api/drivers returns data
[ ] Frontend shows driver count > 0
[ ] No CORS errors in console
[ ] API calls complete successfully

🧪 Testing Phase:
[ ] Dashboard loads with data
[ ] Driver selection works
[ ] Track selection works
[ ] Navigation between pages works
[ ] All API endpoints respond
```

## 🐛 Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| 404 on `/api/*` | API calls fail | Verify `api/index.py` at root |
| Module not found | Import errors | Check `sys.path` in `api/index.py` |
| Database errors | "No such file" | Verify `circuit-fit.db` at root |
| CORS errors | Blocked requests | Check `allow_origin_regex` |
| 0 drivers found | No data loads | Test `/api/drivers` directly |

## 🎓 Key Learnings

1. **Vercel Structure**: API handlers must be at `/api/*.py` at project root
2. **Serverless Paths**: Use environment variables for dynamic path resolution
3. **CORS Strategy**: Use regex patterns for preview deployments
4. **Relative URLs**: Frontend should use `/api` not absolute URLs
5. **Database Location**: Must be at project root, included in deployment

## 📚 Documentation Files

- `DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- `DEPLOY_NOW.md` - Quick deployment checklist
- `BACKEND_FIX_SUMMARY.md` - Detailed fix documentation
- `VISUAL_ARCHITECTURE.md` - This file (visual overview)

---

**Status**: ✅ Ready for Production
**Date**: 2025-11-03
**Deployment URL**: https://circuit-fbtth1gml-justin-groszs-projects.vercel.app
