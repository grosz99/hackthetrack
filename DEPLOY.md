# 🚀 Deploy HackTheTrack to Production

**Platform:** Heroku (backend) + Vercel (frontend)
**Time:** 15 minutes
**Cost:** $0 (free tier)

---

## Quick Start

```bash
# 1. Install Heroku CLI
brew install heroku

# 2. Login and deploy backend
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
heroku login
heroku create hackthetrack-api
heroku stack:set container
git push heroku master

# 3. Set your API key
heroku config:set ANTHROPIC_API_KEY=your-key-here

# 4. Get your backend URL
heroku apps:info -a hackthetrack-api

# 5. Update Vercel frontend
# Go to vercel.com → Settings → Environment Variables
# Set: VITE_API_URL=https://hackthetrack-api.herokuapp.com
# Redeploy
```

---

## Step-by-Step Guide

### 1. Install Heroku CLI (one-time setup)

**Mac:**
```bash
brew install heroku
```

**Windows:**
Download from: https://devcenter.heroku.com/articles/heroku-cli

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

---

### 2. Deploy Backend to Heroku

```bash
# Navigate to project root
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Login to Heroku (opens browser)
heroku login

# Create app
heroku create hackthetrack-api

# Use Docker/container deployment
heroku stack:set container -a hackthetrack-api

# Deploy (triggers build from Dockerfile)
git push heroku master
```

**Wait 3-5 minutes** for build. You'll see:
```
remote: Verifying deploy... done.
To https://git.heroku.com/hackthetrack-api.git
 * [new branch]      master -> master
```

---

### 3. Configure Environment Variables

**Minimum required (use JSON data, no Snowflake):**
```bash
heroku config:set ANTHROPIC_API_KEY=sk-ant-YOUR-KEY -a hackthetrack-api
heroku config:set USE_SNOWFLAKE=false -a hackthetrack-api
```

**Optional - Enable Snowflake (with password auth):**
```bash
heroku config:set USE_SNOWFLAKE=true -a hackthetrack-api
heroku config:set SNOWFLAKE_ACCOUNT=EOEPNYL-PR46214 -a hackthetrack-api
heroku config:set SNOWFLAKE_USER=hackthetrack_svc -a hackthetrack-api
heroku config:set SNOWFLAKE_PASSWORD=your-password -a hackthetrack-api
heroku config:set SNOWFLAKE_WAREHOUSE=COMPUTE_WH -a hackthetrack-api
heroku config:set SNOWFLAKE_DATABASE=HACKTHETRACK -a hackthetrack-api
heroku config:set SNOWFLAKE_SCHEMA=TELEMETRY -a hackthetrack-api
heroku config:set SNOWFLAKE_ROLE=ACCOUNTADMIN -a hackthetrack-api
```

---

### 4. Verify Backend is Live

```bash
# Get your app URL
heroku apps:info -a hackthetrack-api

# Test health endpoint
curl https://hackthetrack-api.herokuapp.com/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "tracks_loaded": 6,
  "drivers_loaded": 31,
  "snowflake": {
    "enabled": false,
    "status": "disabled"
  }
}
```

✅ **Backend is live!**

---

### 5. Update Frontend on Vercel

1. Go to https://vercel.com/dashboard
2. Find your project (circuit-fit or similar)
3. Click **Settings** → **Environment Variables**
4. Add or update:
   ```
   Name: VITE_API_URL
   Value: https://hackthetrack-api.herokuapp.com
   ```
5. Check **all 3 environments**: Production, Preview, Development
6. Click **Save**
7. Go to **Deployments** → Click **"..."** → **Redeploy**

**Wait 2 minutes** for Vercel to rebuild.

✅ **Frontend is live!**

---

### 6. Test Complete System

**Backend endpoints:**
```bash
curl https://hackthetrack-api.herokuapp.com/api/health
curl https://hackthetrack-api.herokuapp.com/api/tracks
curl https://hackthetrack-api.herokuapp.com/api/drivers
```

**Frontend:**
1. Visit your Vercel URL (e.g., https://circuit-fit.vercel.app)
2. Open DevTools (F12) → Console tab
3. Check for **zero errors**
4. Test functionality:
   - Select a driver
   - Choose a track
   - View all 3 tabs (Track Intelligence, Strategy Chat, Telemetry)
5. Check Network tab → API calls should hit Heroku backend

✅ **Everything works!**

---

## Architecture

```
┌─────────────────────────────────────────┐
│         User's Browser                  │
│   https://circuit-fit.vercel.app        │
└────────────────┬────────────────────────┘
                 │
                 │ HTTPS requests
                 ▼
┌─────────────────────────────────────────┐
│      Backend API (Heroku)               │
│  https://hackthetrack-api.herokuapp.com │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  FastAPI + Uvicorn              │   │
│  │  - Anthropic Claude API         │   │
│  │  - Driver/Track analysis        │   │
│  │  - Strategy recommendations     │   │
│  └─────────────────────────────────┘   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Data Sources                    │
│                                         │
│  ┌──────────────┐   ┌────────────────┐ │
│  │  JSON Files  │   │   Snowflake    │ │
│  │  (fallback)  │   │   (optional)   │ │
│  └──────────────┘   └────────────────┘ │
└─────────────────────────────────────────┘
```

---

## Useful Commands

**View logs:**
```bash
heroku logs --tail -a hackthetrack-api
```

**Restart backend:**
```bash
heroku restart -a hackthetrack-api
```

**Open app in browser:**
```bash
heroku open -a hackthetrack-api
```

**View all config vars:**
```bash
heroku config -a hackthetrack-api
```

**Scale dynos (for more power):**
```bash
heroku ps:scale web=1 -a hackthetrack-api
```

---

## Troubleshooting

### Build failed
```bash
# Check build logs
heroku logs --tail -a hackthetrack-api

# Common: Dockerfile not found
# Fix: Ensure backend/Dockerfile exists
# Check: heroku.yml points to backend/Dockerfile
```

### 500 Internal Server Error
```bash
# Check app logs
heroku logs --tail -a hackthetrack-api

# Common: Missing ANTHROPIC_API_KEY
# Fix: heroku config:set ANTHROPIC_API_KEY=your-key
```

### Frontend can't connect to backend
```bash
# 1. Verify backend is running
curl https://hackthetrack-api.herokuapp.com/api/health

# 2. Check VITE_API_URL in Vercel
# Should be: https://hackthetrack-api.herokuapp.com (no trailing slash)

# 3. Redeploy frontend after fixing
```

### App sleeps (slow first request)
```bash
# Free tier sleeps after 30 min inactivity
# First request wakes it up (~5-10 seconds)

# To prevent sleep:
# Upgrade to Eco dynos ($5/month)
heroku ps:type eco -a hackthetrack-api
```

---

## Free Tier Limits

**Heroku:**
- ✅ 1000 dyno hours/month (plenty for hobby projects)
- ✅ Sleeps after 30 min inactivity
- ✅ Wakes on first request (~5-10 sec)
- ✅ 512MB RAM
- ✅ Unlimited bandwidth

**Vercel:**
- ✅ 100GB bandwidth/month
- ✅ Unlimited builds
- ✅ No sleep
- ✅ Global CDN

**Total monthly cost: $0**

---

## Production Tips

**1. Keep backend awake (optional):**
```bash
# Use a service like Uptime Robot to ping every 25 minutes
# Ping: https://hackthetrack-api.herokuapp.com/api/health
```

**2. Monitor performance:**
```bash
# Install New Relic (free tier)
heroku addons:create newrelic:wayne -a hackthetrack-api
```

**3. Add custom domain:**
```bash
# Backend
heroku domains:add api.yourdomain.com -a hackthetrack-api

# Frontend (in Vercel dashboard)
# Settings → Domains → Add
```

---

## ✅ You're Done!

Your app is now live:
- **Backend**: https://hackthetrack-api.herokuapp.com
- **Frontend**: https://circuit-fit.vercel.app

**Features working:**
- ✅ 31 drivers with performance metrics
- ✅ 6 tracks with circuit fit analysis
- ✅ AI-powered strategy chat
- ✅ Telemetry comparison
- ✅ Snowflake database support (optional)
- ✅ Auto HTTPS/SSL
- ✅ Auto deploys from GitHub

**Next steps:**
- Share your app URL
- Add more drivers/tracks
- Enable Snowflake for live data
- Monitor usage in Heroku dashboard
