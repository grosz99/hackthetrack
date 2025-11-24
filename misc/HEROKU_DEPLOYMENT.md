# HackTheTrack - Heroku Deployment Guide

## Overview

This document provides step-by-step instructions for deploying the HackTheTrack backend to Heroku and configuring CORS for the Netlify frontend.

**Current Deployment Stack:**
- **Frontend**: Netlify (https://gibbs-ai.netlify.app)
- **Backend**: Heroku (https://hackthetrack-api-ae28ad6f804d.herokuapp.com)
- **AI Service**: Anthropic Claude API

---

## ⚠️ CRITICAL: CORS Configuration

### Current Status

The backend currently has `CORS_ALLOW_ALL=true` set in Heroku, which allows requests from ANY origin. This is insecure for production.

### Required Changes (IN THIS EXACT ORDER)

**DO NOT remove `CORS_ALLOW_ALL` until after testing the new configuration!**

#### Step 1: Update Heroku Environment Variables

```bash
# Set the Netlify frontend URL
heroku config:set FRONTEND_URL=https://gibbs-ai.netlify.app --app hackthetrack-api

# Verify it was set correctly
heroku config --app hackthetrack-api | grep FRONTEND_URL
```

Expected output:
```
FRONTEND_URL: https://gibbs-ai.netlify.app
```

#### Step 2: Deploy Backend Code Changes

The CORS configuration in `backend/main.py` has been updated to:
- Use Netlify URLs instead of Vercel
- Support Netlify preview deployments (`*.netlify.app`)
- Log a warning when `CORS_ALLOW_ALL` is enabled

```bash
# From repository root
git add backend/main.py
git commit -m "fix(cors): update CORS config for Netlify deployment"
git push heroku master
```

#### Step 3: Test with CORS_ALLOW_ALL Still Enabled

Before removing the safety net, verify everything works:

1. **Open Netlify site**: https://gibbs-ai.netlify.app
2. **Test each feature**:
   - Driver rankings load correctly
   - Driver profile page displays
   - Strategy chat sends/receives messages
   - Telemetry comparison works
   - Development page loads recommendations

3. **Check browser console** (F12 → Console tab):
   - Should see NO CORS errors
   - All API calls should succeed

4. **Check Heroku logs**:
```bash
heroku logs --tail --app hackthetrack-api
```
   - Should see warning: "CORS_ALLOW_ALL is enabled - all origins allowed (development only)"
   - Should see successful API requests

#### Step 4: Remove CORS_ALLOW_ALL (Only After Tests Pass!)

```bash
# Remove the dangerous wildcard configuration
heroku config:unset CORS_ALLOW_ALL --app hackthetrack-api

# Verify it's removed
heroku config --app hackthetrack-api
# CORS_ALLOW_ALL should NOT appear in the list
```

#### Step 5: Re-Test Everything

Repeat all tests from Step 3. If any CORS errors occur:

**Emergency Rollback:**
```bash
# Immediately restore CORS_ALLOW_ALL
heroku config:set CORS_ALLOW_ALL=true --app hackthetrack-api
```

Then debug the issue before trying again.

---

## Environment Variables

### Required Environment Variables

The backend requires these environment variables to be set in Heroku:

```bash
# AI Service (CRITICAL - app won't start without this)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Frontend URL (for CORS)
FRONTEND_URL=https://gibbs-ai.netlify.app

# Database credentials (if using Snowflake - optional)
SNOWFLAKE_ACCOUNT=...
SNOWFLAKE_USER=...
SNOWFLAKE_WAREHOUSE=...
SNOWFLAKE_DATABASE=...
SNOWFLAKE_SCHEMA=...
SNOWFLAKE_PRIVATE_KEY_BASE64=...
```

### Check Current Configuration

```bash
# View all environment variables
heroku config --app hackthetrack-api

# Check specific variable
heroku config:get ANTHROPIC_API_KEY --app hackthetrack-api
```

### Set Environment Variables

```bash
# Set a single variable
heroku config:set VARIABLE_NAME=value --app hackthetrack-api

# Set multiple variables at once
heroku config:set \
  FRONTEND_URL=https://gibbs-ai.netlify.app \
  ANTHROPIC_API_KEY=sk-ant-... \
  --app hackthetrack-api
```

---

## Deployment Process

### Initial Setup (One-Time)

1. **Install Heroku CLI**:
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login to Heroku**:
```bash
heroku login
```

3. **Add Heroku remote** (if not already added):
```bash
heroku git:remote -a hackthetrack-api
```

4. **Verify remote**:
```bash
git remote -v
```
Should show:
```
heroku  https://git.heroku.com/hackthetrack-api.git (fetch)
heroku  https://git.heroku.com/hackthetrack-api.git (push)
```

### Deploy Updates

```bash
# Make sure you're on the master branch
git checkout master

# Push to Heroku (triggers automatic deployment)
git push heroku master
```

### Monitor Deployment

```bash
# Watch logs in real-time
heroku logs --tail --app hackthetrack-api

# View recent logs
heroku logs --num=100 --app hackthetrack-api

# Check app status
heroku ps --app hackthetrack-api
```

---

## Health Checks

### Backend Health Check

```bash
# Check if backend is running
curl https://hackthetrack-api-ae28ad6f804d.herokuapp.com/

# Expected response:
{
  "name": "Racing Analytics API",
  "version": "1.0.0",
  "theme": "Making the Predictable Unpredictable",
  "docs": "/docs",
  "endpoints": {...}
}
```

### API Endpoint Tests

```bash
# Test drivers endpoint
curl https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/drivers

# Test tracks endpoint
curl https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/tracks

# Test health endpoint
curl https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/health
```

---

## Troubleshooting

### App Crashes on Startup

**Symptom**: `heroku logs` shows `State changed from starting to crashed`

**Common Causes**:
1. **Missing ANTHROPIC_API_KEY**: Backend validates this on startup
   ```bash
   heroku config:set ANTHROPIC_API_KEY=sk-ant-... --app hackthetrack-api
   ```

2. **Python version mismatch**: Check `runtime.txt`
   ```bash
   cat runtime.txt
   # Should show: python-3.11.x
   ```

3. **Missing dependencies**: Check `requirements.txt`
   ```bash
   git add requirements.txt
   git commit -m "update dependencies"
   git push heroku master
   ```

### CORS Errors After Removing CORS_ALLOW_ALL

**Symptom**: Browser console shows errors like:
```
Access to fetch at 'https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/drivers'
from origin 'https://gibbs-ai.netlify.app' has been blocked by CORS policy
```

**Solutions**:

1. **Verify FRONTEND_URL is set correctly**:
   ```bash
   heroku config:get FRONTEND_URL --app hackthetrack-api
   # Should return: https://gibbs-ai.netlify.app
   ```

2. **Check Netlify deployment URL matches**:
   - Go to Netlify dashboard
   - Verify the production URL is exactly `https://gibbs-ai.netlify.app`
   - If different, update FRONTEND_URL

3. **Temporary fix** (while debugging):
   ```bash
   heroku config:set CORS_ALLOW_ALL=true --app hackthetrack-api
   ```

### AI Services Return 503 Errors

**Symptom**: Strategy chat, coaching features fail with "Service temporarily unavailable"

**Common Causes**:
1. **Anthropic API rate limiting**: Wait 60 seconds and try again
2. **Invalid API key**: Check key is valid
   ```bash
   heroku config:get ANTHROPIC_API_KEY --app hackthetrack-api
   ```
3. **Anthropic service outage**: Check https://status.anthropic.com

### Slow Response Times

**Check dyno status**:
```bash
heroku ps --app hackthetrack-api
```

**Restart dynos**:
```bash
heroku restart --app hackthetrack-api
```

**Scale up** (if needed):
```bash
# Check current dyno type
heroku dyno:type --app hackthetrack-api

# Upgrade to better performance tier (costs money)
heroku dyno:resize web=standard-1x --app hackthetrack-api
```

---

## Testing Changes Before Deployment

### Run Backend Locally

```bash
# Navigate to backend directory
cd backend

# Install dependencies (if needed)
pip install -r requirements.txt

# Create local .env file with API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Run backend
python main.py
```

Backend will be available at: http://localhost:8000

### Test with Local Backend + Netlify Frontend

1. **Update frontend API URL**:
```bash
cd frontend
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

2. **Test in browser**: http://localhost:5173

3. **When done, remove `.env.local`** to use Heroku backend again

---

## Rollback Strategy

If a deployment causes issues:

### Option 1: Rollback to Previous Release

```bash
# List recent releases
heroku releases --app hackthetrack-api

# Rollback to previous release (e.g., v47)
heroku rollback v47 --app hackthetrack-api
```

### Option 2: Emergency Fix

```bash
# Create a fix
git revert <bad-commit-hash>
git commit -m "fix: revert breaking changes"

# Deploy immediately
git push heroku master
```

---

## Security Best Practices

### ✅ DO:
- Keep `ANTHROPIC_API_KEY` in environment variables (never commit to Git)
- Use specific CORS origins (Netlify URL only)
- Monitor Heroku logs for suspicious activity
- Update dependencies regularly: `pip list --outdated`

### ❌ DON'T:
- Commit `.env` files to Git
- Leave `CORS_ALLOW_ALL=true` in production
- Share API keys in Slack, email, or documentation
- Use `--force` push to Heroku unless absolutely necessary

---

## Monitoring

### View Logs

```bash
# Real-time logs
heroku logs --tail --app hackthetrack-api

# Filter by severity
heroku logs --tail --app hackthetrack-api | grep ERROR

# Search for specific pattern
heroku logs --tail --app hackthetrack-api | grep "CORS"
```

### Metrics Dashboard

```bash
# Open Heroku dashboard in browser
heroku open --app hackthetrack-api
```

Then navigate to **Metrics** tab to see:
- Response times
- Memory usage
- Request volume
- Error rates

---

## Cost Optimization

### Current Plan
- **Dyno Type**: eco (sleeps after 30 minutes of inactivity)
- **Cost**: $5/month (shared across all eco dynos)

### Keep App Awake (Optional)

If you want the app to respond instantly:

1. **Upgrade to Basic dyno** ($7/month):
```bash
heroku dyno:resize web=basic --app hackthetrack-api
```

2. **Or use a monitoring service** (free):
- UptimeRobot: https://uptimerobot.com
- Ping every 25 minutes to keep eco dyno awake

---

## Support

### Useful Commands

```bash
# Check app info
heroku info --app hackthetrack-api

# Open app in browser
heroku open --app hackthetrack-api

# Access Heroku bash
heroku run bash --app hackthetrack-api

# Run Python shell
heroku run python --app hackthetrack-api

# Check dyno status
heroku ps --app hackthetrack-api
```

### Documentation
- Heroku Python Docs: https://devcenter.heroku.com/articles/getting-started-with-python
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
- Anthropic API Docs: https://docs.anthropic.com/

---

## Summary Checklist

Before going live with CORS changes:

- [ ] Heroku `FRONTEND_URL` set to `https://gibbs-ai.netlify.app`
- [ ] Backend code deployed with Netlify CORS config
- [ ] All features tested with `CORS_ALLOW_ALL` still enabled
- [ ] No CORS errors in browser console
- [ ] Heroku logs show successful API requests
- [ ] `CORS_ALLOW_ALL` removed from Heroku
- [ ] All features re-tested without `CORS_ALLOW_ALL`
- [ ] Monitoring enabled for production traffic

---

**Last Updated**: 2025-01-20
**Backend**: https://hackthetrack-api-ae28ad6f804d.herokuapp.com
**Frontend**: https://gibbs-ai.netlify.app
