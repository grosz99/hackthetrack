# Railway Deployment Guide - HackTheTrack Backend

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend (Vercel)                 Backend (Railway)         │
│  ┌──────────────────┐              ┌──────────────────┐     │
│  │  Static Hosting  │──────────────▶│  FastAPI Server  │     │
│  │  React/Vite      │    HTTPS     │  Python 3.12     │     │
│  │                  │    CORS      │  Uvicorn         │     │
│  └──────────────────┘              └──────────────────┘     │
│         │                                   │                │
│         │                                   │                │
│         ▼                                   ▼                │
│  circuit-xyz.vercel.app      your-backend.railway.app       │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Data Sources:
├── Snowflake (Primary)
├── JSON Files (Fallback)
└── Cache (Performance)
```

---

## Why Railway vs Vercel?

### Problem
Vercel has a **250MB serverless function limit**, which we exceeded due to:
- Snowflake connector dependencies
- SciPy and NumPy packages
- Anthropic SDK
- Total deployment size: **~400MB**

### Solution
**Railway** provides:
- ✅ **No size limits** for standard deployments
- ✅ **Always-on server** (not serverless)
- ✅ **Better for heavy dependencies** (scientific computing, data processing)
- ✅ **Built-in PostgreSQL** (if needed later)
- ✅ **Simple deployment** from GitHub

**Vercel** stays for:
- ✅ **Static hosting** for React frontend
- ✅ **Edge CDN** for fast global delivery
- ✅ **Preview deployments** for PRs

---

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Repository**: Code pushed to GitHub
3. **Environment Variables**: Ready from `.env.example`

---

## Step 1: Prepare Backend for Railway

### 1.1 Verify Configuration Files

The following files have been created for Railway deployment:

#### **Procfile**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### **railway.json**
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100
  }
}
```

#### **nixpacks.toml**
```toml
[phases.setup]
nixPkgs = ["python312", "gcc"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

### 1.2 Verify PORT Handling

The `main.py` already handles the `PORT` environment variable correctly:

```python
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
```

✅ **No changes needed** - Railway will inject `$PORT` automatically.

### 1.3 Verify CORS Configuration

The `main.py` CORS setup needs to be updated to allow Railway backend URL:

**Current CORS** (in `backend/main.py`):
```python
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
    "http://localhost:8000",
]

production_url = os.getenv("FRONTEND_URL", "https://circuit-fbtth1gml-justin-groszs-projects.vercel.app")
if production_url:
    allowed_origins.append(production_url)

allowed_origins.append("https://*.vercel.app")
```

**Updated CORS** (after Railway deployment):
```python
# Add the FRONTEND_URL environment variable to Railway
# Railway will automatically handle all Vercel subdomains via regex
```

✅ **Current config is good** - uses `allow_origin_regex` for `*.vercel.app`

---

## Step 2: Deploy to Railway

### 2.1 Create New Railway Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select the **hackthetrack-master** repository
6. Select the **backend** directory as root

### 2.2 Configure Railway Service

Railway will automatically detect:
- ✅ Python project (via `requirements.txt`)
- ✅ Start command (via `Procfile` or `railway.json`)
- ✅ Health check endpoint (`/api/health`)

### 2.3 Set Environment Variables

In Railway dashboard, add these environment variables:

#### **Required Variables**

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your-account-id
SNOWFLAKE_USER=your-service-account-user
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKTHETRACK
SNOWFLAKE_SCHEMA=TELEMETRY
SNOWFLAKE_ROLE=ACCOUNTADMIN
USE_SNOWFLAKE=true

# Choose ONE Snowflake auth method:
# Option A: Password (not recommended)
SNOWFLAKE_PASSWORD=your-password

# Option B: Key-Pair (recommended)
SNOWFLAKE_PRIVATE_KEY_PATH=/app/rsa_key.p8
# Note: You'll need to upload the private key as a Railway volume or secret

# Frontend URL for CORS
FRONTEND_URL=https://your-vercel-url.vercel.app

# Application Settings
ENVIRONMENT=production
DEBUG=false
```

#### **How to Add Variables in Railway**

1. Click on your service
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add each variable (key-value pair)
5. Click **"Deploy"** to apply changes

### 2.4 Handle Snowflake Private Key (if using key-pair auth)

If using Snowflake key-pair authentication:

**Option 1: Environment Variable (Recommended)**
```bash
# Base64 encode the private key file
cat rsa_key.p8 | base64 > rsa_key.base64.txt

# Add as Railway environment variable
SNOWFLAKE_PRIVATE_KEY_BASE64=<paste-base64-content>

# Update backend/app/services/snowflake_service.py to decode it
import base64
import os
from cryptography.hazmat.primitives import serialization

private_key_b64 = os.getenv("SNOWFLAKE_PRIVATE_KEY_BASE64")
if private_key_b64:
    private_key_bytes = base64.b64decode(private_key_b64)
    # Use private_key_bytes for connection
```

**Option 2: Railway Volume**
```bash
# Upload the key file to Railway volume
# Not recommended for security reasons
```

---

## Step 3: Deploy and Get Railway URL

### 3.1 Initial Deployment

Railway will automatically:
1. ✅ Clone your repository
2. ✅ Install dependencies from `requirements.txt`
3. ✅ Run the start command from `Procfile`
4. ✅ Assign a public URL

### 3.2 Get Your Railway URL

After deployment:
1. Go to **"Settings"** tab
2. Under **"Domains"**, you'll see something like:
   ```
   https://hackthetrack-backend-production.up.railway.app
   ```
3. **Copy this URL** - you'll need it for frontend configuration

### 3.3 Test the Deployment

```bash
# Test health endpoint
curl https://your-backend.railway.app/api/health

# Expected response:
{
  "status": "healthy",
  "tracks_loaded": 14,
  "drivers_loaded": 42,
  "data_sources": {
    "snowflake": "healthy",
    "local_json": "healthy",
    "cache": "healthy"
  },
  "overall_data_health": "healthy"
}
```

---

## Step 4: Update Frontend to Use Railway Backend

### 4.1 Update Frontend Environment Variables

In **Vercel** dashboard for your frontend:

1. Go to **"Settings"** → **"Environment Variables"**
2. Update/add:
   ```bash
   VITE_API_URL=https://your-backend.railway.app
   ```
3. **Redeploy** the frontend:
   - Go to **"Deployments"**
   - Click **"..."** on latest deployment
   - Click **"Redeploy"**

### 4.2 Verify Frontend API Configuration

The frontend (`frontend/src/services/api.js`) will automatically use the Railway URL:

```javascript
const getApiBaseUrl = () => {
  if (import.meta.env.PROD) {
    // In production, use the environment variable
    return import.meta.env.VITE_API_URL || '';
  }
  // Development: use localhost
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};
```

### 4.3 Test Frontend → Backend Connection

1. Open your Vercel frontend: `https://your-frontend.vercel.app`
2. Open browser DevTools → Network tab
3. Navigate through the app
4. Verify requests are going to Railway backend:
   ```
   GET https://your-backend.railway.app/api/drivers
   GET https://your-backend.railway.app/api/tracks
   ```

---

## Step 5: Deployment Validation Checklist

### 5.1 Backend Health Checks

```bash
# 1. Root endpoint
curl https://your-backend.railway.app/
# Expected: API info with endpoints

# 2. Health check
curl https://your-backend.railway.app/api/health
# Expected: "status": "healthy"

# 3. Tracks endpoint
curl https://your-backend.railway.app/api/tracks
# Expected: Array of track objects

# 4. Drivers endpoint
curl https://your-backend.railway.app/api/drivers
# Expected: Array of driver objects

# 5. Telemetry drivers (Snowflake test)
curl https://your-backend.railway.app/api/telemetry/drivers
# Expected: List of drivers with telemetry data
```

### 5.2 CORS Verification

```bash
# Test CORS from frontend domain
curl -H "Origin: https://your-frontend.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-backend.railway.app/api/health

# Expected headers:
# access-control-allow-origin: https://your-frontend.vercel.app
# access-control-allow-methods: *
# access-control-allow-headers: *
```

### 5.3 Snowflake Connection Test

```bash
# Test Snowflake data retrieval
curl https://your-backend.railway.app/api/telemetry/drivers

# Expected response:
{
  "drivers_with_telemetry": [13, 42, 78, ...],
  "count": 42,
  "source": "snowflake",
  "health": "healthy"
}
```

### 5.4 Anthropic API Test

```bash
# Test AI chat endpoint
curl -X POST https://your-backend.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What should I focus on?",
    "driver_number": 13,
    "track_id": "road_atlanta",
    "history": []
  }'

# Expected: AI-generated coaching response
```

### 5.5 Full Integration Test

1. ✅ Open frontend in browser
2. ✅ Select a driver from dropdown
3. ✅ Navigate to "Overview" tab
4. ✅ Check that driver stats load
5. ✅ Navigate to "Skills" tab
6. ✅ Verify factor breakdowns load
7. ✅ Navigate to "Improve" tab
8. ✅ Test skill adjustment predictions
9. ✅ Navigate to "Telemetry" tab
10. ✅ Test telemetry comparison
11. ✅ Navigate to "AI Coach" tab
12. ✅ Send a chat message
13. ✅ Verify AI response

---

## Step 6: Update Backend CORS for Production

### 6.1 Add Railway Backend to CORS

Update `backend/main.py` to ensure Railway backend URL is in allowed origins:

```python
# After Railway deployment, add this to .env:
FRONTEND_URL=https://your-frontend.vercel.app
RAILWAY_URL=https://your-backend.railway.app

# Update main.py:
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
    os.getenv("RAILWAY_URL", "http://localhost:8000"),
]

production_url = os.getenv("FRONTEND_URL")
if production_url:
    allowed_origins.append(production_url)
```

---

## Environment Variables Summary

### Railway (Backend)

| Variable | Example | Required | Notes |
|----------|---------|----------|-------|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` | ✅ Yes | For AI chat/coaching |
| `SNOWFLAKE_ACCOUNT` | `xy12345.us-east-1` | ✅ Yes | Snowflake account ID |
| `SNOWFLAKE_USER` | `SERVICE_ACCOUNT` | ✅ Yes | Snowflake user |
| `SNOWFLAKE_WAREHOUSE` | `COMPUTE_WH` | ✅ Yes | Snowflake warehouse |
| `SNOWFLAKE_DATABASE` | `HACKTHETRACK` | ✅ Yes | Snowflake database |
| `SNOWFLAKE_SCHEMA` | `TELEMETRY` | ✅ Yes | Snowflake schema |
| `SNOWFLAKE_ROLE` | `ACCOUNTADMIN` | ✅ Yes | Snowflake role |
| `SNOWFLAKE_PASSWORD` | `***` | ⚠️ One of | Password auth |
| `SNOWFLAKE_PRIVATE_KEY_BASE64` | `***` | ⚠️ One of | Key-pair auth (recommended) |
| `USE_SNOWFLAKE` | `true` | ✅ Yes | Enable Snowflake |
| `FRONTEND_URL` | `https://your-app.vercel.app` | ✅ Yes | For CORS |
| `ENVIRONMENT` | `production` | ✅ Yes | Production mode |
| `DEBUG` | `false` | ✅ Yes | Disable debug |

### Vercel (Frontend)

| Variable | Example | Required | Notes |
|----------|---------|----------|-------|
| `VITE_API_URL` | `https://your-backend.railway.app` | ✅ Yes | Railway backend URL |

---

## Rollback Plan

### If Railway Deployment Fails

#### **Scenario 1: Deployment Error**

1. Check Railway logs:
   ```
   Dashboard → Service → "Deployments" → Click failed deployment → View logs
   ```

2. Common issues:
   - **Missing dependencies**: Add to `requirements.txt`
   - **Import errors**: Check Python paths in code
   - **Port binding**: Ensure `$PORT` is used correctly

3. Fix locally, push to GitHub, Railway auto-redeploys

#### **Scenario 2: Frontend Can't Connect to Backend**

1. **Verify CORS**:
   ```bash
   # Check if CORS headers are present
   curl -I https://your-backend.railway.app/api/health
   ```

2. **Check environment variables**:
   - Railway: Verify `FRONTEND_URL` is set
   - Vercel: Verify `VITE_API_URL` is set

3. **Redeploy**:
   - Railway: Click "Redeploy" in dashboard
   - Vercel: Go to Deployments → Redeploy

#### **Scenario 3: Need to Revert to Vercel Serverless**

If you need to go back to Vercel (e.g., Railway is down):

1. **Remove heavy dependencies** from `requirements.txt`:
   ```bash
   # Temporarily remove:
   # - snowflake-connector-python
   # - scipy
   # Set USE_SNOWFLAKE=false
   ```

2. **Redeploy to Vercel**:
   ```bash
   cd backend
   vercel --prod
   ```

3. **Update frontend**:
   ```bash
   # In Vercel, set:
   VITE_API_URL=/api
   # Redeploy frontend
   ```

#### **Scenario 4: Database Connection Issues**

1. **Test Snowflake directly**:
   ```bash
   # SSH into Railway container (if needed)
   railway run python
   >>> from app.services.snowflake_service import snowflake_service
   >>> snowflake_service.test_connection()
   ```

2. **Check failover**:
   - Data reliability service should automatically fall back to JSON files
   - Check health endpoint for data source status

3. **Verify credentials**:
   - Snowflake account/user/password
   - Private key encoding (if using key-pair auth)

---

## Monitoring and Observability

### Railway Logs

```bash
# View real-time logs in Railway dashboard
Dashboard → Service → "Observables" → Logs

# Look for:
✅ "Application startup complete"
✅ "Uvicorn running on http://0.0.0.0:$PORT"
✅ "GET /api/health 200 OK"

# Watch for errors:
❌ "ModuleNotFoundError"
❌ "Connection refused"
❌ "500 Internal Server Error"
```

### Health Monitoring

Set up monitoring with:
- **Railway built-in monitoring**: CPU, memory, network
- **UptimeRobot**: External uptime monitoring
- **Sentry**: Error tracking (optional)

### Performance Metrics

Track these KPIs:
- **Response time**: `/api/health` should be <500ms
- **Memory usage**: Should stay <1GB for normal operation
- **CPU usage**: Should stay <50% under normal load
- **Uptime**: Target 99.9%

---

## Cost Estimate

### Railway Pricing

**Starter Plan** (Free):
- $5 free credit/month
- 512MB RAM
- 1GB storage
- **Good for**: Development/testing

**Developer Plan** ($5/month):
- $5 credit + $5/month
- 8GB RAM
- 100GB storage
- **Good for**: Production with moderate traffic

**Estimated cost** for HackTheTrack:
- **~$5-10/month** (assuming moderate usage)
- Railway charges based on:
  - CPU usage: ~$0.000463/vCPU-min
  - Memory: ~$0.000231/GB-min
  - Network egress: $0.10/GB

### Vercel Pricing

**Hobby Plan** (Free):
- Unlimited deployments
- 100GB bandwidth/month
- **Good for**: Frontend hosting

**Total estimated cost**: **$5-10/month** (Railway only)

---

## Security Best Practices

### 1. Environment Variables

✅ **Never commit** `.env` files to GitHub
✅ **Use Railway secrets** for sensitive data
✅ **Rotate API keys** regularly

### 2. CORS Configuration

✅ **Restrict origins** to only Vercel domains
✅ **Use regex** for preview deployments: `*.vercel.app`
✅ **Disable CORS** in development if needed

### 3. API Keys

✅ **Anthropic API**: Store in Railway environment
✅ **Snowflake credentials**: Use key-pair auth (not password)
✅ **Private keys**: Base64 encode or use Railway volumes

### 4. Rate Limiting

Consider adding rate limiting to prevent abuse:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.get("/api/chat")
@limiter.limit("10/minute")
async def chat_endpoint():
    ...
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution**: Ensure Railway root directory is `backend`:
```bash
# In Railway settings:
Root Directory: backend
```

### Issue: "Address already in use"

**Solution**: Railway handles `$PORT` automatically - don't hardcode port 8000
```python
# ✅ Correct:
port = int(os.getenv("PORT", 8000))

# ❌ Wrong:
port = 8000
```

### Issue: "CORS error: No 'Access-Control-Allow-Origin' header"

**Solution**: Verify `FRONTEND_URL` in Railway matches Vercel domain exactly
```bash
# Railway environment variable:
FRONTEND_URL=https://your-app.vercel.app
# (no trailing slash!)
```

### Issue: "Snowflake connection failed"

**Solution**: Check these in order:
1. Snowflake account/user/password correct?
2. Network access from Railway allowed in Snowflake?
3. Private key encoded correctly (if using key-pair auth)?
4. Fallback to JSON files working?

---

## Next Steps After Deployment

1. ✅ **Monitor logs** for the first 24 hours
2. ✅ **Test all endpoints** via frontend
3. ✅ **Set up uptime monitoring** (UptimeRobot)
4. ✅ **Document Railway URL** for team
5. ✅ **Update README** with new architecture
6. ✅ **Remove Vercel backend** deployment (optional)

---

## Support and Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/

---

**Last Updated**: 2025-11-06
**Author**: Claude Code - Full Stack Integration Architect
