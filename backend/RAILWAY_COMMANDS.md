# Railway Deployment - Command Reference

Quick reference for common Railway deployment commands and checks.

---

## Pre-Deployment

### Verify Backend Locally
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend

# Start server
python main.py

# Test health endpoint
curl http://localhost:8000/api/health

# Test tracks endpoint
curl http://localhost:8000/api/tracks
```

### Check Configuration Files
```bash
# Verify Procfile exists
cat backend/Procfile

# Verify railway.json exists
cat backend/railway.json

# Verify nixpacks.toml exists
cat backend/nixpacks.toml

# Check requirements.txt
cat backend/requirements.txt
```

### Git Commit Changes
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

git add backend/Procfile backend/railway.json backend/nixpacks.toml
git commit -m "feat(deploy): add Railway configuration files"
git push origin master
```

---

## Railway Deployment

### Via Dashboard (Recommended)
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `hackthetrack-master`
4. Set Root Directory: `backend`
5. Click "Deploy"

### Via CLI (Alternative)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
cd backend
railway init

# Deploy
railway up

# Set environment variables
railway variables set ANTHROPIC_API_KEY=sk-ant-api03-...
railway variables set SNOWFLAKE_ACCOUNT=...
railway variables set SNOWFLAKE_USER=...
# ... (add all variables from .env.example)

# Get deployment URL
railway domain
```

---

## Post-Deployment Testing

### Test Railway Backend
```bash
# Set Railway URL (replace with your actual URL)
export RAILWAY_URL=https://your-backend.railway.app

# Test root endpoint
curl $RAILWAY_URL/

# Test health endpoint
curl $RAILWAY_URL/api/health

# Test tracks endpoint
curl $RAILWAY_URL/api/tracks

# Test drivers endpoint
curl $RAILWAY_URL/api/drivers

# Test Snowflake connection
curl $RAILWAY_URL/api/telemetry/drivers

# Test AI chat endpoint
curl -X POST $RAILWAY_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quick test",
    "driver_number": 13,
    "track_id": "road_atlanta",
    "history": []
  }'
```

### Test CORS
```bash
export RAILWAY_URL=https://your-backend.railway.app
export FRONTEND_URL=https://your-frontend.vercel.app

curl -H "Origin: $FRONTEND_URL" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     $RAILWAY_URL/api/health
```

### Run Validation Script
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend

python scripts/validate_railway_deployment.py \
  https://your-backend.railway.app \
  https://your-frontend.vercel.app
```

---

## Frontend Update

### Update Vercel Environment Variable
```bash
# Via Vercel Dashboard:
# 1. Go to project settings
# 2. Environment Variables
# 3. Add/Update: VITE_API_URL=https://your-backend.railway.app
# 4. Redeploy

# Via Vercel CLI:
vercel env add VITE_API_URL production
# Enter: https://your-backend.railway.app

# Redeploy
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend
vercel --prod
```

### Test Frontend Connection
```bash
# Open browser
open https://your-frontend.vercel.app

# Check network requests in DevTools
# Should see requests to https://your-backend.railway.app/api/*
```

---

## Monitoring

### Railway Logs (Live)
```bash
# Via CLI
railway logs

# Via Dashboard
# Go to: Dashboard → Service → Observables → Logs
```

### Watch Health Endpoint
```bash
# Every 5 seconds
watch -n 5 curl https://your-backend.railway.app/api/health

# With formatted output
watch -n 5 'curl -s https://your-backend.railway.app/api/health | python -m json.tool'
```

### Monitor Railway Metrics
```bash
# Via Dashboard
# Go to: Dashboard → Service → Observables → Metrics
# Monitor:
# - CPU usage
# - Memory usage
# - Network egress
# - Response time
```

---

## Troubleshooting

### Check Railway Build Logs
```bash
# Via CLI
railway logs --deployment <deployment-id>

# Via Dashboard
# Dashboard → Deployments → Click deployment → View logs
```

### Check Environment Variables
```bash
# Via CLI
railway variables

# Via Dashboard
# Dashboard → Service → Variables
```

### Restart Service
```bash
# Via CLI
railway restart

# Via Dashboard
# Dashboard → Service → Settings → Restart
```

### View Railway Status
```bash
# Check Railway platform status
open https://status.railway.app

# Check if your region is healthy
```

---

## Common Issues & Fixes

### Issue: "ModuleNotFoundError"
```bash
# Check requirements.txt
cat backend/requirements.txt

# Verify module is listed
rg "missing-module" backend/requirements.txt

# If missing, add it
echo "missing-module==1.0.0" >> backend/requirements.txt
git add backend/requirements.txt
git commit -m "fix: add missing dependency"
git push
# Railway will auto-redeploy
```

### Issue: "Address already in use"
```bash
# Check if PORT is correctly handled in main.py
rg "PORT" backend/main.py

# Should see:
# port = int(os.getenv("PORT", 8000))

# If hardcoded to 8000, fix it:
# port = int(os.getenv("PORT", 8000))
```

### Issue: "CORS error"
```bash
# Check FRONTEND_URL in Railway
railway variables | grep FRONTEND_URL

# Should match Vercel domain exactly (no trailing slash)
# Fix if needed:
railway variables set FRONTEND_URL=https://your-app.vercel.app

# Restart
railway restart
```

### Issue: "Snowflake connection failed"
```bash
# Check Snowflake credentials
railway variables | grep SNOWFLAKE

# Test connection manually
railway run python
>>> from app.services.snowflake_service import snowflake_service
>>> snowflake_service.test_connection()

# If fails, check:
# 1. SNOWFLAKE_ACCOUNT correct?
# 2. SNOWFLAKE_USER correct?
# 3. SNOWFLAKE_PASSWORD correct?
# 4. Network access allowed from Railway?

# Fallback to JSON files
railway variables set USE_SNOWFLAKE=false
railway restart
```

---

## Rollback Procedures

### Rollback to Previous Railway Deployment
```bash
# Via Dashboard
# 1. Dashboard → Deployments
# 2. Find last working deployment
# 3. Click "..." → "Redeploy"

# Via CLI
railway rollback
```

### Revert Frontend to Vercel Backend
```bash
# 1. Update Vercel environment variable
vercel env rm VITE_API_URL production

# 2. Redeploy frontend
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend
vercel --prod

# 3. Verify frontend uses relative /api path
# (Falls back to Vercel backend)
```

### Emergency: Disable Snowflake
```bash
# If Snowflake is causing issues, disable it
railway variables set USE_SNOWFLAKE=false
railway restart

# Data reliability service will fall back to JSON files
```

---

## Maintenance

### Update Dependencies
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend

# Update requirements.txt
# Edit manually or use pip-tools

# Commit changes
git add backend/requirements.txt
git commit -m "chore: update dependencies"
git push

# Railway auto-deploys
```

### Scale Up/Down
```bash
# Via Dashboard
# 1. Dashboard → Service → Settings
# 2. Adjust resources (CPU, memory)
# 3. Click "Save"

# Railway automatically restarts with new resources
```

### View Deployment History
```bash
# Via CLI
railway deployments

# Via Dashboard
# Dashboard → Deployments → View all
```

---

## Cost Monitoring

### Check Current Usage
```bash
# Via Dashboard
# 1. Dashboard → Billing
# 2. View current month usage
# 3. Check:
#    - CPU minutes
#    - Memory usage
#    - Network egress
#    - Estimated cost
```

### Set Budget Alerts
```bash
# Via Dashboard
# 1. Dashboard → Billing → Alerts
# 2. Set monthly budget limit
# 3. Configure email notifications
```

### Optimize Costs
```bash
# 1. Review resource usage
# Dashboard → Service → Observables → Metrics

# 2. Adjust resources if over-provisioned
# Dashboard → Service → Settings → Adjust resources

# 3. Enable sleep mode for non-production environments
# Dashboard → Service → Settings → Sleep mode
```

---

## Useful Commands

### Quick Health Check
```bash
curl -s https://your-backend.railway.app/api/health | python -m json.tool
```

### Full System Check
```bash
python backend/scripts/validate_railway_deployment.py \
  https://your-backend.railway.app \
  https://your-frontend.vercel.app
```

### Watch Railway Logs
```bash
railway logs --follow
```

### Get Railway URL
```bash
railway domain
```

### View All Environment Variables
```bash
railway variables
```

### Export Environment Variables
```bash
railway variables > railway_vars.txt
```

### Import Environment Variables
```bash
# Create .env file with Railway variables
railway variables | grep "=" > .env

# Or bulk import from file
railway variables set --from-file .env
```

---

## Emergency Contacts

### Railway Support
- Discord: https://discord.gg/railway
- Email: team@railway.app
- Status: https://status.railway.app

### Vercel Support
- Support: https://vercel.com/support
- Status: https://vercel-status.com

### Snowflake Support
- Support: https://community.snowflake.com
- Status: https://status.snowflake.com

---

## Quick Reference URLs

### Railway
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app
- CLI Docs: https://docs.railway.app/develop/cli

### Vercel
- Dashboard: https://vercel.com/dashboard
- Docs: https://vercel.com/docs

### This Project
- Health: https://your-backend.railway.app/api/health
- API Docs: https://your-backend.railway.app/docs
- Frontend: https://your-frontend.vercel.app

---

**Last Updated**: 2025-11-06
**Quick Start Guide**: See `RAILWAY_QUICK_START.md`
**Full Deployment Guide**: See `RAILWAY_DEPLOYMENT.md`
