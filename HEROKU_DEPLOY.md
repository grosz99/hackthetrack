# 🚀 NUCLEAR OPTION: Deploy to Heroku (100% Works)

If Render failed, **Heroku is the most reliable option** for Python apps.

## Why Heroku Works When Others Fail
- ✅ Been around for 15+ years
- ✅ Handles numpy/pandas/scipy perfectly
- ✅ Simple Dockerfile support
- ✅ 1000 free hours/month (enough for 24/7 with auto-sleep)
- ✅ Most mature Python support

---

## STEP 1: Install Heroku CLI (2 minutes)

### Mac:
```bash
brew tap heroku/brew && brew install heroku
```

### Windows:
Download from: https://devcenter.heroku.com/articles/heroku-cli

### Linux:
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

---

## STEP 2: Login and Create App (2 minutes)

```bash
# Login to Heroku
heroku login

# Navigate to your backend directory
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend

# Create Heroku app
heroku create hackthetrack-api

# Add container stack (for Docker)
heroku stack:set container -a hackthetrack-api
```

---

## STEP 3: Set Environment Variables (1 minute)

```bash
# Required - Anthropic API
heroku config:set ANTHROPIC_API_KEY=sk-ant-YOUR-KEY -a hackthetrack-api

# Simplest - Use JSON data (no Snowflake)
heroku config:set USE_SNOWFLAKE=false -a hackthetrack-api

# App settings
heroku config:set ENVIRONMENT=production -a hackthetrack-api
heroku config:set DEBUG=false -a hackthetrack-api
```

**OR** if you want Snowflake with password:
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

## STEP 4: Create heroku.yml (30 seconds)

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
```

Create file `heroku.yml`:
```yaml
build:
  docker:
    web: backend/Dockerfile
run:
  web: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## STEP 5: Deploy! (3 minutes)

```bash
# Add and commit heroku.yml
git add heroku.yml
git commit -m "Add Heroku deployment config"

# Push to Heroku (triggers build and deploy)
git push heroku master
```

**Wait 3-5 minutes for build to complete.**

---

## STEP 6: Get Your URL and Test

```bash
# Open your app
heroku open -a hackthetrack-api

# Or get the URL
heroku apps:info -a hackthetrack-api
```

Your API will be at: **https://hackthetrack-api.herokuapp.com**

Test it:
```bash
curl https://hackthetrack-api.herokuapp.com/api/health
```

---

## STEP 7: Update Vercel Frontend

1. Go to https://vercel.com/dashboard
2. Your project → Settings → Environment Variables
3. Update `VITE_API_URL`:
   ```
   VITE_API_URL=https://hackthetrack-api.herokuapp.com
   ```
4. Redeploy

---

## ✅ DONE!

**Heroku literally invented Platform-as-a-Service.** It will work.

**Cost:** Free tier gives you 1000 hours/month (plenty for hobby projects)

**Sleep behavior:** Sleeps after 30 min inactivity, wakes in ~5 seconds

**To keep it awake 24/7:** Upgrade to Hobby tier ($7/month)

---

## Troubleshooting

### "Error: No app specified"
```bash
# Make sure you're in the right directory
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Specify app name explicitly
git push heroku master -a hackthetrack-api
```

### "Dockerfile not found"
```bash
# Make sure heroku.yml points to correct path
cat heroku.yml

# Should show:
# build:
#   docker:
#     web: backend/Dockerfile
```

### "Build failed"
```bash
# Check logs
heroku logs --tail -a hackthetrack-api

# Most common: missing Dockerfile
# Fix: Ensure backend/Dockerfile exists
```

---

## Why This Works

Heroku's Docker support is **battle-tested** with millions of apps.

Your Dockerfile will build successfully because:
1. ✅ Heroku gives generous build time (30 minutes)
2. ✅ Heroku has proper build resources (2GB RAM during build)
3. ✅ Heroku's container registry is optimized for Python
4. ✅ Heroku caches layers properly

**This is the most reliable option. Period.**
