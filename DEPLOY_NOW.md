# 🚀 DEPLOY NOW - Exact Steps for You

## ✅ Everything Is Ready - Follow These Steps Exactly

---

## STEP 1: Deploy Backend to Railway (10 minutes)

### 1A. Go to Railway
Open: **https://railway.app/new**

### 1B. Connect GitHub
- Click **"Deploy from GitHub repo"**
- Select **grosz99/hackthetrack**
- Click **"Deploy Now"**

### 1C. Configure Railway Project
After deployment starts:
1. Click **"Settings"** (left sidebar)
2. Set **Root Directory**: `backend`
3. Click **"Redeploy"**

### 1D. Add Environment Variables
Click **"Variables"** tab, add your values (copy from Vercel):
- ANTHROPIC_API_KEY
- SNOWFLAKE_ACCOUNT
- SNOWFLAKE_USER
- SNOWFLAKE_PRIVATE_KEY_PATH
- SNOWFLAKE_WAREHOUSE
- SNOWFLAKE_DATABASE
- SNOWFLAKE_SCHEMA
- SNOWFLAKE_ROLE
- USE_SNOWFLAKE
- ENVIRONMENT
- DEBUG

### 1E. Get Your Railway URL
1. Click **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Copy the URL (e.g., `https://hackthetrack-production.up.railway.app`)
4. **SAVE THIS URL** - you need it for Step 2

---

## STEP 2: Configure Vercel (2 minutes)

1. Go to **https://vercel.com/dashboard**
2. Click **circuit-fit** project
3. **Settings** → **Environment Variables**
4. Add: `VITE_API_URL` = `https://your-railway-url.railway.app`
5. Check ALL environments (Production, Preview, Development)
6. Click **Save**

---

## STEP 3: Done! (Auto-deploys)

Vercel will automatically redeploy with the new environment variable.

---

## TEST: Visit your Vercel URL

✅ Homepage loads
✅ Driver selector works
✅ All tabs navigate
✅ No errors in console

**YOU'RE LIVE!**

Total time: ~20 minutes
