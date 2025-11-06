# 🚀 Deploy to Render.com - SIMPLE 3-STEP GUIDE

**Total Time: 20 minutes**
**Cost: $0 (Free tier)**

---

## STEP 1: Deploy Backend to Render (15 minutes)

### 1A. Create Render Account
1. Go to https://render.com/
2. Click "Get Started" → Sign in with GitHub
3. Authorize Render to access your GitHub account

### 1B. Create New Web Service
1. Click **"New +"** (top right)
2. Select **"Web Service"**
3. Find and select **"grosz99/hackthetrack"** repository
4. Click **"Connect"**

### 1C. Configure Service
Fill in these settings:

**Basic Settings:**
```
Name: hackthetrack-api
Region: Oregon (US West) [or closest to you]
Branch: master
Root Directory: backend
```

**Build Settings:**
```
Environment: Docker
Docker Command: [Leave blank - auto-detected]
Docker Context: backend
```

**Instance Settings:**
```
Instance Type: Free
```

### 1D. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these ONE BY ONE:

**Required - AI:**
```
ANTHROPIC_API_KEY = sk-ant-api03-YOUR-KEY-HERE
```

**Snowflake - Option 1 (SIMPLEST - Use JSON data only):**
```
USE_SNOWFLAKE = false
```

**Snowflake - Option 2 (Use Snowflake with password):**
```
USE_SNOWFLAKE = true
SNOWFLAKE_ACCOUNT = EOEPNYL-PR46214
SNOWFLAKE_USER = hackthetrack_svc
SNOWFLAKE_PASSWORD = your-snowflake-password
SNOWFLAKE_WAREHOUSE = COMPUTE_WH
SNOWFLAKE_DATABASE = HACKTHETRACK
SNOWFLAKE_SCHEMA = TELEMETRY
SNOWFLAKE_ROLE = ACCOUNTADMIN
```

**App Settings:**
```
ENVIRONMENT = production
DEBUG = false
```

### 1E. Deploy!
1. Click **"Create Web Service"** (bottom of page)
2. Wait 3-5 minutes (watch the build logs)
3. Look for: **"Application startup complete"**
4. Your service will show **"Live"** status
5. **COPY YOUR URL**: https://hackthetrack-api.onrender.com

### 1F. Verify Backend Works
Open in browser or curl:
```
https://hackthetrack-api.onrender.com/api/health
```

You should see:
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

✅ **Backend is LIVE!**

---

## STEP 2: Update Vercel Frontend (5 minutes)

### 2A. Go to Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Find and click your **"circuit-fit"** project (or whatever it's named)

### 2B. Add Environment Variable
1. Click **"Settings"** tab
2. Click **"Environment Variables"** (left sidebar)
3. Click **"Add New"**

Fill in:
```
Name: VITE_API_URL
Value: https://hackthetrack-api.onrender.com
```

4. **IMPORTANT**: Check ALL THREE boxes:
   - ✅ Production
   - ✅ Preview
   - ✅ Development

5. Click **"Save"**

### 2C. Redeploy Frontend
1. Go to **"Deployments"** tab
2. Find the most recent deployment
3. Click **"..."** menu → **"Redeploy"**
4. Wait 2 minutes for build
5. Click the deployment URL when ready

✅ **Frontend is LIVE!**

---

## STEP 3: Test Everything (5 minutes)

### Test Backend
Open these URLs in your browser:

1. Health: https://hackthetrack-api.onrender.com/api/health
2. Tracks: https://hackthetrack-api.onrender.com/api/tracks
3. Drivers: https://hackthetrack-api.onrender.com/api/drivers

All should return JSON data ✅

### Test Frontend
1. Open your Vercel URL (e.g., https://circuit-fit.vercel.app)
2. Press **F12** to open DevTools
3. Check **Console** tab → Should be NO red errors
4. Test app:
   - Select a driver from dropdown
   - Choose a track
   - Click **"Track Intelligence"** tab
   - Click **"Strategy Chat"** tab
   - Click **"Telemetry"** tab
5. Check **Network** tab:
   - Look for API calls to `hackthetrack-api.onrender.com`
   - All should show **200 OK** status

✅ **Everything Works!**

---

## 🎉 YOU'RE DEPLOYED!

**Your app is now live:**
- Backend API: https://hackthetrack-api.onrender.com
- Frontend App: https://circuit-fit.vercel.app

**Free tier includes:**
- ✅ 750 hours/month (Render)
- ✅ Auto HTTPS/SSL
- ✅ Auto deploys from GitHub
- ✅ Snowflake connection support
- ✅ All 31 drivers + 6 tracks

---

## 🔧 Troubleshooting

### "Build failed on Render"
**Check:** Render build logs for error
**Fix:** Ensure Dockerfile exists in backend/ directory

### "Frontend can't connect to backend"
**Check:** VITE_API_URL is set correctly in Vercel
**Fix:** No trailing slash in URL
**Verify:** Visit backend health endpoint directly

### "500 Internal Server Error"
**Check:** Render logs for Python traceback
**Common:** Missing ANTHROPIC_API_KEY
**Fix:** Add missing environment variable

---

## 💰 Keeping It Free

**Render Free Tier:**
- Your service sleeps after 15 minutes of inactivity
- First request wakes it up (~30 seconds)
- Stays awake while in use

**To prevent sleep:**
- Upgrade to Render Starter ($7/month)
- Or ping your health endpoint every 10 minutes

**Vercel Free Tier:**
- No sleep, always fast
- 100GB bandwidth/month (plenty for hobby projects)

---

## 🚀 Next Steps

**Want to add more features?**
1. Monitor logs in Render dashboard
2. Add custom domain (both Render and Vercel support this)
3. Enable Snowflake for live data (just change USE_SNOWFLAKE=true)
4. Add more telemetry data
5. Implement caching for faster responses

**Need help?**
- Render docs: https://render.com/docs
- Vercel docs: https://vercel.com/docs
- Your code is all set up correctly!

---

**This should be straightforward. Railway was the problem, not your code!** 🎯
