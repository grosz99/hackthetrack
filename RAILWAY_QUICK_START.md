# Railway Deployment - Quick Start Guide

## TL;DR - Deploy in 10 Minutes

### Step 1: Push to GitHub (if not already done)
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
git add backend/Procfile backend/railway.json backend/nixpacks.toml
git commit -m "feat(deploy): add Railway configuration files"
git push origin master
```

### Step 2: Deploy to Railway
1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select **hackthetrack-master**
4. Set **Root Directory** to `backend`
5. Click **"Deploy"**

### Step 3: Set Environment Variables
In Railway dashboard, add these variables:

```bash
ANTHROPIC_API_KEY=<your-anthropic-key>
SNOWFLAKE_ACCOUNT=<your-snowflake-account>
SNOWFLAKE_USER=<your-snowflake-user>
SNOWFLAKE_PASSWORD=<your-snowflake-password>
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKTHETRACK
SNOWFLAKE_SCHEMA=TELEMETRY
SNOWFLAKE_ROLE=ACCOUNTADMIN
USE_SNOWFLAKE=true
FRONTEND_URL=https://your-frontend.vercel.app
ENVIRONMENT=production
DEBUG=false
```

### Step 4: Get Railway URL
1. Copy the Railway URL from dashboard (e.g., `https://hackthetrack-production.up.railway.app`)

### Step 5: Update Frontend
1. Go to Vercel dashboard → Your frontend project
2. Settings → Environment Variables
3. Add/Update:
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```
4. Redeploy frontend

### Step 6: Validate Deployment
```bash
# Test health
curl https://your-backend.railway.app/api/health

# Run full validation
cd backend
python scripts/validate_railway_deployment.py \
  https://your-backend.railway.app \
  https://your-frontend.vercel.app
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  User Browser                                                 │
│       │                                                       │
│       │ HTTPS                                                 │
│       ▼                                                       │
│  ┌─────────────────────┐                                     │
│  │  Vercel Frontend    │                                     │
│  │  (Static Hosting)   │                                     │
│  │                     │                                     │
│  │  - React/Vite       │                                     │
│  │  - Edge CDN         │                                     │
│  └─────────────────────┘                                     │
│           │                                                   │
│           │ API Calls                                         │
│           │ (CORS enabled)                                    │
│           ▼                                                   │
│  ┌─────────────────────┐                                     │
│  │  Railway Backend    │                                     │
│  │  (Always-On Server) │                                     │
│  │                     │                                     │
│  │  - FastAPI          │                                     │
│  │  - Python 3.12      │                                     │
│  │  - Uvicorn          │                                     │
│  └─────────────────────┘                                     │
│           │                                                   │
│           ├──────────────┐                                    │
│           │              │                                    │
│           ▼              ▼                                    │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  Snowflake   │  │  Anthropic   │                         │
│  │  Data        │  │  Claude API  │                         │
│  └──────────────┘  └──────────────┘                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Why Railway?

| Feature | Vercel Serverless | Railway |
|---------|-------------------|---------|
| Deployment Size | 250MB limit | No limit |
| Server Type | Serverless (cold starts) | Always-on |
| Heavy Dependencies | ❌ Limited | ✅ Full support |
| Database Connections | ❌ Tricky (connection pooling) | ✅ Native support |
| Build Time | Fast | Moderate |
| Cost | Free tier generous | $5/month |
| Use Case | Frontend, lightweight APIs | Backend, data processing |

**Our backend** has:
- Snowflake connector (~100MB)
- SciPy/NumPy (~150MB)
- Anthropic SDK (~50MB)
- Total: **~400MB** → Too large for Vercel

---

## Configuration Files Created

### 1. Procfile
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```
- Tells Railway how to start the server
- `$PORT` is injected by Railway automatically

### 2. railway.json
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
- Railway deployment configuration
- Defines build steps and health checks

### 3. nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["python312", "gcc"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```
- Nixpacks build configuration (alternative to Dockerfile)
- Specifies Python version and build commands

---

## Environment Variables Reference

### Required Variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` | Claude AI API access |
| `SNOWFLAKE_ACCOUNT` | `xy12345.us-east-1` | Snowflake connection |
| `SNOWFLAKE_USER` | `SERVICE_ACCOUNT` | Snowflake user |
| `SNOWFLAKE_PASSWORD` | `***` | Snowflake auth |
| `SNOWFLAKE_WAREHOUSE` | `COMPUTE_WH` | Snowflake warehouse |
| `SNOWFLAKE_DATABASE` | `HACKTHETRACK` | Snowflake database |
| `SNOWFLAKE_SCHEMA` | `TELEMETRY` | Snowflake schema |
| `SNOWFLAKE_ROLE` | `ACCOUNTADMIN` | Snowflake role |
| `USE_SNOWFLAKE` | `true` | Enable Snowflake |
| `FRONTEND_URL` | `https://your-app.vercel.app` | CORS configuration |
| `ENVIRONMENT` | `production` | Environment mode |
| `DEBUG` | `false` | Debug mode |

### Optional Variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `SNOWFLAKE_LOGIN_TIMEOUT` | `10` | Snowflake connection timeout |
| `SNOWFLAKE_NETWORK_TIMEOUT` | `30` | Network timeout |
| `SNOWFLAKE_MAX_RETRIES` | `3` | Connection retry limit |

---

## Deployment Checklist

### Pre-Deployment
- [ ] All code committed to GitHub
- [ ] `requirements.txt` up to date
- [ ] Railway config files created (Procfile, railway.json, nixpacks.toml)
- [ ] Environment variables ready (Anthropic, Snowflake)

### Railway Deployment
- [ ] Railway project created
- [ ] GitHub repo connected
- [ ] Root directory set to `backend`
- [ ] Environment variables added
- [ ] First deployment successful
- [ ] Railway URL copied

### Frontend Update
- [ ] Vercel environment variable `VITE_API_URL` updated
- [ ] Frontend redeployed
- [ ] Frontend can connect to Railway backend

### Validation
- [ ] Health endpoint returns 200 OK
- [ ] Tracks endpoint loads data
- [ ] Drivers endpoint loads data
- [ ] Telemetry drivers endpoint works (Snowflake)
- [ ] AI chat endpoint works (Anthropic)
- [ ] CORS allows frontend requests
- [ ] Full integration test passed

---

## Testing Commands

### 1. Test Backend Health
```bash
curl https://your-backend.railway.app/api/health
```

**Expected Response:**
```json
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

### 2. Test CORS
```bash
curl -H "Origin: https://your-frontend.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-backend.railway.app/api/health
```

**Expected Headers:**
```
access-control-allow-origin: https://your-frontend.vercel.app
access-control-allow-methods: *
access-control-allow-headers: *
```

### 3. Run Full Validation
```bash
cd backend
python scripts/validate_railway_deployment.py \
  https://your-backend.railway.app \
  https://your-frontend.vercel.app
```

---

## Troubleshooting

### Issue: "Build Failed"

**Check Railway Logs:**
1. Dashboard → Service → Deployments
2. Click failed deployment
3. View build logs

**Common Fixes:**
- Missing dependencies in `requirements.txt`
- Python version mismatch (use 3.12)
- Build timeout (increase timeout in railway.json)

### Issue: "Application Failed to Respond"

**Check Runtime Logs:**
1. Dashboard → Service → Observables → Logs
2. Look for errors in application startup

**Common Fixes:**
- Port not binding to `$PORT` (check main.py)
- Missing environment variables
- Import errors (check Python paths)

### Issue: "CORS Error"

**Verify:**
- `FRONTEND_URL` in Railway matches Vercel domain exactly
- No trailing slash in `FRONTEND_URL`
- CORS middleware configured in main.py

**Fix:**
```python
# In backend/main.py
allowed_origins = [
    "http://localhost:5173",
    os.getenv("FRONTEND_URL", ""),
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: "Snowflake Connection Failed"

**Check:**
1. Environment variables correct?
2. Snowflake account/user/password valid?
3. Network access allowed from Railway IP?

**Test Locally:**
```python
from app.services.snowflake_service import snowflake_service
snowflake_service.test_connection()
```

**Fallback:**
- Set `USE_SNOWFLAKE=false` to use JSON files
- Data reliability service will automatically fall back

---

## Monitoring

### Railway Dashboard Metrics
- **CPU Usage**: Should be <50% under normal load
- **Memory Usage**: Should be <1GB
- **Network**: Monitor egress (affects cost)
- **Response Time**: Health endpoint <500ms

### Set Up Alerts
1. Railway → Service → Observables → Metrics
2. Create alert for:
   - High CPU (>80%)
   - High memory (>1.5GB)
   - Deployment failures
   - Health check failures

### External Monitoring
Consider using:
- **UptimeRobot**: Free uptime monitoring
- **Better Uptime**: Advanced monitoring with status page
- **Sentry**: Error tracking and performance monitoring

---

## Cost Management

### Railway Pricing
- **Free Tier**: $5 credit/month
- **Developer Plan**: $5/month + usage
- **Estimated Cost**: $5-10/month for moderate usage

### Cost Optimization
- Use environment-based scaling (reduce resources for dev)
- Set up autoscaling based on traffic
- Monitor logs for inefficient queries
- Cache expensive operations

---

## Rollback Plan

### If Railway Fails

**Option 1: Revert to Vercel** (temporary)
```bash
# 1. Disable Snowflake
USE_SNOWFLAKE=false

# 2. Remove heavy dependencies
# Edit requirements.txt, remove:
# - snowflake-connector-python
# - scipy

# 3. Redeploy to Vercel
cd backend
vercel --prod

# 4. Update frontend
VITE_API_URL=/api
```

**Option 2: Deploy to Render/Heroku**
- Similar to Railway
- Use same config files
- Different pricing model

### If Frontend Fails

**Rollback to Previous Deployment:**
1. Vercel → Deployments
2. Find last working deployment
3. Click "..." → "Promote to Production"

---

## Next Steps After Deployment

1. **Monitor for 24 hours**: Watch Railway logs for errors
2. **Test all features**: Go through entire app workflow
3. **Set up monitoring**: UptimeRobot or similar
4. **Document URLs**: Save Railway URL for team
5. **Clean up Vercel backend**: Remove `/api` folder (optional)
6. **Update README**: Document new architecture

---

## Support

- **Railway Discord**: https://discord.gg/railway
- **Railway Docs**: https://docs.railway.app
- **Railway Status**: https://status.railway.app

---

**Last Updated**: 2025-11-06
**Deployment Type**: Backend → Railway, Frontend → Vercel
**Status**: ✅ Ready for Production
