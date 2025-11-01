# Vercel Deployment Guide for Circuit Fit

## Why Vercel? ✨

Vercel makes deployment **much easier** than Netlify for this project because:
- ✅ **Native Python support** - Run FastAPI backend as serverless functions
- ✅ **Monorepo friendly** - Deploy frontend + backend from single repo
- ✅ **Zero configuration** - Works with our existing structure
- ✅ **Automatic HTTPS** - Free SSL certificates
- ✅ **Edge network** - Fast global CDN
- ✅ **Preview deployments** - Every PR gets a unique URL

## Project Structure

```
hackthetrack-master/
├── frontend/              # React + Vite
│   ├── src/
│   ├── dist/             # Build output
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── models.py
│   │   └── services/
│   ├── api/
│   │   └── index.py      # ⭐ Vercel entry point
│   ├── main.py           # FastAPI app
│   └── requirements.txt
├── data/                  # Race data CSVs
├── vercel.json           # ⭐ Vercel configuration
└── netlify.toml          # (can be deleted)
```

## Setup Steps

### 1. Install Vercel CLI (Optional, for local testing)

```bash
npm install -g vercel
```

### 2. File Configuration

All necessary files are already created:
- ✅ `vercel.json` - Deployment configuration
- ✅ `backend/api/index.py` - Serverless function wrapper
- ✅ `backend/requirements.txt` - Updated with `mangum` dependency

### 3. Deploy to Vercel

#### Option A: Via Vercel Website (Recommended for first deployment)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "Add New Project"
3. Import your GitHub repository: `grosz99/hackthetrack`
4. Vercel will auto-detect the configuration from `vercel.json`
5. Click "Deploy"

That's it! Vercel will:
- Build the frontend (React/Vite)
- Package the backend as serverless functions
- Deploy both to the same domain
- Set up automatic deployments for future git pushes

#### Option B: Via CLI

```bash
# From project root
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name? circuit-fit
# - Directory? ./ (root)
# - Override settings? No

# For production deployment:
vercel --prod
```

### 4. Environment Variables (if needed)

If your backend uses environment variables (API keys, etc.):

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add variables:
   - `ANTHROPIC_API_KEY` (for AI features)
   - Any other secrets from `backend/.env`

## How It Works

### Frontend Routing
```
https://your-app.vercel.app/          → React app (frontend/dist/index.html)
https://your-app.vercel.app/overview  → React app (SPA routing)
https://your-app.vercel.app/race-log  → React app (SPA routing)
```

### API Routing
```
https://your-app.vercel.app/api/drivers/13/stats   → backend/api/index.py (FastAPI)
https://your-app.vercel.app/api/drivers/13/results → backend/api/index.py (FastAPI)
```

### Serverless Functions

Vercel converts your FastAPI app into serverless functions:
- Each API request spawns a new function instance
- Functions include the entire `backend/` directory and `data/` folder
- Max execution time: 30 seconds (configured in vercel.json)
- Memory: 1024 MB (configured in vercel.json)

## Data Files

The `data/` directory (>50MB of CSV files) will be included in the deployment:
- ✅ Configured in `vercel.json` via `includeFiles`
- ✅ Available to backend functions at runtime
- ⚠️ Large data files may increase cold start time slightly

## Configuration Details

### vercel.json Explained

```json
{
  "builds": [
    {
      "src": "frontend/package.json",      // Build frontend
      "use": "@vercel/static-build"
    },
    {
      "src": "backend/api/index.py",       // Build backend function
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",                  // API routes → backend
      "dest": "backend/api/index.py"
    },
    {
      "src": "/(.*)",                      // All other routes → frontend
      "dest": "frontend/$1"
    }
  ],
  "functions": {
    "backend/api/index.py": {
      "includeFiles": "{data/**,backend/**}",  // Include data + backend code
      "memory": 1024,                           // 1GB RAM
      "maxDuration": 30                         // 30 second timeout
    }
  }
}
```

### backend/api/index.py Explained

```python
from mangum import Mangum
from main import app

# Mangum adapter converts FastAPI → AWS Lambda/Vercel format
handler = Mangum(app, lifespan="off")
```

## Testing Locally

### Test Frontend
```bash
cd frontend
npm install
npm run dev
# Opens on http://localhost:5173
```

### Test Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API on http://localhost:8000
```

### Test Full Stack with Vercel Dev
```bash
vercel dev
# Simulates Vercel environment locally
# Frontend: http://localhost:3000
# API: http://localhost:3000/api/*
```

## Post-Deployment

### 1. Update API Base URL (if needed)

Check `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

For Vercel, this should automatically work since API is on same domain:
```javascript
const API_BASE_URL = '';  // Relative URLs work on Vercel
```

### 2. Verify Endpoints

After deployment, test these URLs:
- `https://your-app.vercel.app/` - Frontend loads
- `https://your-app.vercel.app/api/health` - API health check
- `https://your-app.vercel.app/api/drivers/13/stats` - Driver stats
- `https://your-app.vercel.app/api/drivers/13/results` - Race log data

### 3. Check Deployment Logs

- Go to Vercel Dashboard → Your Project → Deployments
- Click on latest deployment
- View "Build Logs" and "Function Logs"

## Automatic Deployments

Once connected to GitHub:
- ✅ Every `git push` to `master` → Production deployment
- ✅ Every PR → Preview deployment with unique URL
- ✅ Automatic rollbacks if deployment fails

## Limitations & Considerations

### Serverless Function Limits
- **Execution time**: 30 seconds max (enough for API calls)
- **Memory**: 1024 MB (configurable up to 3GB on Pro plan)
- **Cold starts**: First request may be slower (~1-2 seconds)
- **File size**: 50MB function limit (our data fits)

### Data Files
- CSV files are included in each function deployment
- Consider migrating to database if data grows beyond 100MB
- Current size (~50MB) is acceptable

### Database
- Currently using SQLite (`circuit-fit.db`)
- ⚠️ SQLite writes won't persist between function calls
- ✅ Read-only operations work fine
- For write operations, consider:
  - PostgreSQL (Vercel Postgres)
  - PlanetScale (MySQL)
  - Supabase (PostgreSQL)

## Cost

**Free Tier includes:**
- Unlimited API calls (with rate limits)
- 100GB bandwidth/month
- Automatic SSL
- Preview deployments
- Perfect for development and low-traffic production

## Troubleshooting

### Build Failures

**Frontend build fails:**
```bash
# Check frontend/package.json scripts
cd frontend
npm install
npm run build  # Should work locally
```

**Backend function fails:**
```bash
# Check requirements.txt
cd backend
pip install -r requirements.txt
python -c "from main import app; print('Import successful')"
```

### API Not Working

1. Check function logs in Vercel Dashboard
2. Verify `vercel.json` routes configuration
3. Test locally with `vercel dev`
4. Check CORS settings in `backend/main.py`

### Data Files Missing

If race results are empty:
- Verify `includeFiles` in `vercel.json`
- Check function logs for file not found errors
- Ensure data files are in git (not .gitignored)

## Migration from Netlify

Since you already have `netlify.toml`:

1. Keep Netlify config (doesn't hurt)
2. Deploy to Vercel (both can coexist)
3. Compare performance
4. Switch DNS to Vercel if satisfied
5. Delete Netlify site when confident

## Next Steps

1. ✅ Push all changes to GitHub
2. ✅ Connect repository to Vercel
3. ✅ Deploy and test
4. ✅ Share Vercel URL with team

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI + Vercel Guide](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Mangum Documentation](https://mangum.io/)
