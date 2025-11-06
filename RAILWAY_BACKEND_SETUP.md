# Railway Backend Setup Guide

## Overview

Deploy the FastAPI backend to Railway to work with the Vercel frontend.

## Prerequisites

- Railway account: https://railway.app
- GitHub account (for Railway connection)
- Backend code ready in `/backend` directory

## Deployment Steps

### 1. Install Railway CLI (Optional but Recommended)

```bash
# macOS
brew install railway

# Or using npm
npm i -g @railway/cli
```

### 2. Login to Railway

```bash
railway login
```

### 3. Create New Project

**Option A: Via Railway CLI**
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend
railway init
railway up
```

**Option B: Via Railway Dashboard** (Recommended)
1. Go to https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select repository: `hackthetrack-master`
5. Configure root directory: `/backend`

### 4. Configure Build Settings

Railway should auto-detect Python, but verify:

**Build Configuration**:
```
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Root Directory: /backend (if monorepo)
```

### 5. Add Environment Variables

In Railway Dashboard → Variables, add:

```bash
# Python
PYTHONUNBUFFERED=1

# Database (if using Snowflake)
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

# Or use keypair authentication (recommended)
SNOWFLAKE_PRIVATE_KEY=your_base64_encoded_key
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE=your_passphrase

# Anthropic AI
ANTHROPIC_API_KEY=your_api_key

# CORS (will be updated after Vercel deployment)
CORS_ORIGINS=http://localhost:5173,https://*.vercel.app

# Optional: Logging
LOG_LEVEL=INFO
```

### 6. Update Backend CORS Configuration

Edit `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Racing Analytics API")

# Get CORS origins from environment
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173"
).split(",")

# Add wildcard support for Vercel preview deployments
origins = cors_origins + [
    "https://*.vercel.app",  # Preview deployments
    "https://your-app.vercel.app"  # Production (update after Vercel deploy)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7. Deploy

**If using CLI**:
```bash
railway up
```

**If using Dashboard**:
- Push to GitHub
- Railway auto-deploys

### 8. Get Railway URL

After deployment:
```bash
# Via CLI
railway domain

# Or check Railway Dashboard → Settings → Domains
```

You'll get a URL like:
```
https://hackthetrack-backend-production.up.railway.app
```

### 9. Test Backend

```bash
# Health check
curl https://your-backend.railway.app/api/health

# Test API endpoint
curl https://your-backend.railway.app/api/drivers

# Check logs
railway logs
```

## Configuration Files

### Create `railway.json` (Optional)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100
  }
}
```

### Create `Procfile` (Optional)

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Create `nixpacks.toml` (Optional)

```toml
[phases.setup]
nixPkgs = ["python310", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

## Verify Backend Requirements

Ensure `/backend/requirements.txt` has all dependencies:

```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
anthropic>=0.7.0
snowflake-connector-python>=3.0.0
pandas>=2.0.0
numpy>=1.24.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

## Database Connection

### If Using Snowflake:

Railway supports environment variables for Snowflake credentials. Make sure your backend code reads from environment:

```python
import os
from snowflake.connector import connect

def get_snowflake_connection():
    return connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
```

### If Using PostgreSQL:

Railway can provision PostgreSQL automatically:
1. Add PostgreSQL plugin in Railway dashboard
2. Use `DATABASE_URL` environment variable

## Monitoring

### Check Logs
```bash
railway logs
# Or via Dashboard → Deployments → View Logs
```

### Monitor Metrics
- Railway Dashboard shows:
  - CPU usage
  - Memory usage
  - Network traffic
  - Request volume

### Set Up Alerts
- Railway → Settings → Notifications
- Enable deployment notifications
- Enable error alerts

## Performance Optimization

### 1. Enable Keep-Alive

In `main.py`:
```python
from fastapi import FastAPI

app = FastAPI(
    title="Racing Analytics API",
    # Enable keep-alive for better performance
    # Railway handles this automatically
)
```

### 2. Add Caching

Consider adding Redis via Railway plugins:
```bash
railway add redis
```

### 3. Connection Pooling

For Snowflake/database connections:
```python
from functools import lru_cache

@lru_cache()
def get_db_connection():
    return connect(...)
```

## Troubleshooting

### Issue: Build Fails

**Check**:
1. `requirements.txt` is complete
2. Python version compatibility
3. Check Railway build logs

**Fix**:
```bash
railway logs --build
```

### Issue: App Crashes on Start

**Check**:
1. Start command is correct
2. Environment variables are set
3. Port is bound to `$PORT` (Railway requirement)

**Fix**:
```python
# Make sure you're using Railway's PORT
import os
port = int(os.getenv("PORT", 8000))
```

### Issue: Slow Response Times

**Optimize**:
1. Add database connection pooling
2. Enable caching for frequent queries
3. Use async endpoints where possible
4. Consider Railway's scale plan

### Issue: Database Connection Fails

**Check**:
1. Environment variables are correct
2. Snowflake credentials are valid
3. Network access is allowed from Railway IPs

### Issue: CORS Errors

**Check**:
1. CORS origins include Vercel domain
2. Wildcard `https://*.vercel.app` is included
3. Credentials are enabled if using cookies

## Cost Considerations

**Railway Pricing**:
- Starter Plan: $5/month credit
- Usage-based: ~$0.000231/GB-hour
- Estimated backend cost: $10-20/month

**Optimization Tips**:
- Use Railway's sleep feature for non-critical apps
- Optimize database queries to reduce compute
- Enable caching to reduce API calls

## Scaling

As traffic grows:

1. **Horizontal Scaling**: Add more instances in Railway
2. **Vertical Scaling**: Increase RAM/CPU
3. **Caching**: Add Redis for frequently accessed data
4. **CDN**: Use Vercel edge for static responses

## Security

### Best Practices:
1. Never commit secrets to Git
2. Use Railway's secret management
3. Enable HTTPS (Railway provides automatically)
4. Rotate API keys regularly
5. Use keypair auth for Snowflake (more secure)

### Environment Variable Security:
- Railway encrypts environment variables at rest
- Use Railway CLI for sensitive operations
- Rotate credentials if exposed

## Next Steps

After Railway deployment:

1. ✅ Copy Railway URL
2. ✅ Test health endpoint
3. ✅ Update Vercel environment variables with Railway URL
4. ✅ Deploy Vercel frontend
5. ✅ Test end-to-end integration

## Support Resources

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Templates: https://railway.app/templates
- FastAPI Railway Guide: https://docs.railway.app/guides/fastapi

## Quick Commands Reference

```bash
# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# View logs
railway logs

# Get domain
railway domain

# Open dashboard
railway open

# Run command in Railway environment
railway run python script.py

# Link to existing project
railway link

# View environment variables
railway variables

# Add service
railway add
```
