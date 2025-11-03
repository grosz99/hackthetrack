# Deployment Guide: FastAPI Backend + React Frontend on Vercel

This guide covers the complete deployment setup for the Racing Analytics platform on Vercel.

## Architecture Overview

```
Project Structure:
hackthetrack-master/
├── api/                      # Serverless API handler (NEW)
│   └── index.py             # Vercel Python function entry point
├── backend/                  # FastAPI application code
│   ├── main.py              # FastAPI app definition
│   ├── app/
│   │   ├── api/routes.py    # API endpoints
│   │   └── services/        # Business logic
│   ├── database/            # Database utilities
│   └── requirements.txt     # Python dependencies
├── frontend/                 # React + Vite app
│   ├── src/
│   ├── dist/                # Build output (created during build)
│   └── package.json
├── circuit-fit.db           # SQLite database (136KB)
└── vercel.json              # Vercel configuration
```

## Key Changes Made

### 1. Created `/api/index.py` at Project Root
**File**: `/api/index.py`

This is the serverless function entry point that Vercel expects. It:
- Sets up Python path to import backend modules
- Configures database path via environment variable
- Wraps FastAPI app with Mangum for AWS Lambda/Vercel compatibility

### 2. Updated `vercel.json`
**File**: `/vercel.json`

Configured for Python + Node.js monorepo:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build"
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

### 3. Fixed Database Path Resolution
**File**: `/backend/database/connection.py`

Added environment variable support:
- Checks `DATABASE_PATH` environment variable first
- Falls back to relative path resolution
- Works in both development and Vercel serverless environment

### 4. Updated CORS Configuration
**File**: `/backend/main.py`

Added regex-based CORS for all Vercel deployments:
```python
allow_origin_regex=r"https://.*\.vercel\.app"
```

### 5. Updated Frontend API Client
**File**: `/frontend/src/services/api.js`

Automatically detects environment:
- **Production**: Uses relative path `/api`
- **Development**: Uses `http://localhost:8000`

## Deployment Instructions

### Step 1: Verify Project Structure

Ensure the following files exist:
```bash
ls -la api/index.py
ls -la circuit-fit.db
ls -la backend/requirements.txt
ls -la frontend/package.json
ls -la vercel.json
```

### Step 2: Set Environment Variables in Vercel

Go to Vercel Dashboard > Project Settings > Environment Variables:

**Production Environment Variables:**
```
ANTHROPIC_API_KEY=your_api_key_here
ENVIRONMENT=production
```

**Optional (if using custom domain):**
```
FRONTEND_URL=https://your-custom-domain.com
```

### Step 3: Deploy to Vercel

**Option A: Automatic Deployment (Recommended)**
```bash
# Push to GitHub (if connected to Vercel)
git add .
git commit -m "fix: configure backend for Vercel serverless deployment"
git push origin master
```

Vercel will automatically build and deploy.

**Option B: Manual Deployment**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from project root
vercel --prod
```

### Step 4: Verify Deployment

1. **Check build logs** in Vercel Dashboard
2. **Test API endpoint**: Visit `https://your-app.vercel.app/api/health`
3. **Test frontend**: Visit `https://your-app.vercel.app`
4. **Check browser console** for any CORS or API errors

## Expected API Endpoints

All API endpoints are prefixed with `/api`:

```
GET  /api/health                              # Health check
GET  /api/drivers                             # List all drivers
GET  /api/drivers/{driver_number}             # Get driver details
GET  /api/drivers/{driver_number}/stats       # Get driver season stats
GET  /api/drivers/{driver_number}/results     # Get driver race results
GET  /api/tracks                              # List all tracks
GET  /api/tracks/{track_id}                   # Get track details
POST /api/predict                             # Predict performance
POST /api/chat                                # AI strategy chatbot
GET  /api/telemetry/compare                   # Compare telemetry
GET  /api/telemetry/detailed                  # Detailed telemetry
```

## Testing the Deployment

### 1. Test Health Endpoint
```bash
curl https://your-app.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "tracks_loaded": 14,
  "drivers_loaded": 30
}
```

### 2. Test Drivers Endpoint
```bash
curl https://your-app.vercel.app/api/drivers
```

Should return array of driver objects.

### 3. Test Frontend
Open browser to `https://your-app.vercel.app`
- Should see "Scout Portal" interface
- Should load driver data (not "0 drivers found")
- Check browser console for errors

## Troubleshooting

### Issue: 404 on `/api/*` routes
**Solution**:
- Verify `api/index.py` exists at project root
- Check Vercel build logs for Python function creation
- Ensure `vercel.json` has correct routing configuration

### Issue: "Module not found" errors
**Solution**:
- Verify `backend/requirements.txt` includes all dependencies
- Check that `api/index.py` correctly adds backend to Python path
- Review Vercel build logs for import errors

### Issue: Database errors
**Solution**:
- Ensure `circuit-fit.db` exists at project root
- Verify database file size (should be ~136KB)
- Check that `DATABASE_PATH` environment variable is set correctly
- Review Vercel logs for database connection errors

### Issue: CORS errors in browser
**Solution**:
- Verify production URL in `backend/main.py` CORS configuration
- Check that `allow_origin_regex` matches your Vercel domain
- Ensure frontend is using relative path `/api` in production

### Issue: Frontend shows "0 drivers found"
**Solution**:
- Open browser DevTools > Network tab
- Check if API calls are returning 200 status
- Verify response data format
- Check browser console for JavaScript errors

## Database Limitations

**Important**: SQLite on Vercel serverless functions is READ-ONLY because:
- Each serverless invocation gets a fresh copy of files
- File system is ephemeral and resets after function execution
- Any writes won't persist across requests

For write operations, you would need to:
1. Migrate to a hosted database (PostgreSQL, PlanetScale, etc.)
2. Use Vercel KV/Postgres
3. Keep using SQLite for read-only analytics

Current setup works perfectly for the Racing Analytics use case since it's primarily read-only data.

## Local Development

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend runs on `http://localhost:8000`

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

## File Checklist

Before deploying, ensure these files are correct:

- [x] `/api/index.py` - Serverless handler
- [x] `/vercel.json` - Build and routing configuration
- [x] `/circuit-fit.db` - Database at project root
- [x] `/backend/requirements.txt` - Python dependencies
- [x] `/backend/main.py` - FastAPI app with CORS
- [x] `/backend/database/connection.py` - Database path resolution
- [x] `/frontend/src/services/api.js` - API client with auto-detection
- [x] `/frontend/.env.production` - Production environment variables
- [x] `.vercelignore` - Files to exclude from deployment

## Success Indicators

Deployment is successful when:

1. ✅ Vercel build completes without errors
2. ✅ `/api/health` returns 200 status with correct data
3. ✅ `/api/drivers` returns driver list
4. ✅ Frontend loads and displays driver data
5. ✅ No CORS errors in browser console
6. ✅ All API endpoints respond correctly
7. ✅ Database queries execute successfully

## Next Steps

After successful deployment:

1. **Set up custom domain** (optional) in Vercel settings
2. **Configure monitoring** with Vercel Analytics
3. **Set up error tracking** (Sentry, LogRocket, etc.)
4. **Enable caching** for static assets
5. **Monitor function logs** for errors or performance issues

## Support Resources

- **Vercel Python Runtime**: https://vercel.com/docs/functions/runtimes/python
- **Vercel Routing**: https://vercel.com/docs/edge-network/routing
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Mangum (Lambda adapter)**: https://mangum.io/

---

**Last Updated**: 2025-11-03
**Status**: Ready for deployment
