# Quick Deploy Checklist

## Pre-Deployment Verification

Run these commands to verify everything is in place:

```bash
# 1. Verify project root files exist
ls -la api/index.py circuit-fit.db vercel.json

# 2. Verify backend structure
ls -la backend/main.py backend/requirements.txt backend/database/connection.py

# 3. Verify frontend build configuration
ls -la frontend/package.json frontend/.env.production
```

## Deploy Commands

### Option 1: Push to GitHub (Auto-deploy)

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Stage all changes
git add .

# Commit with descriptive message
git commit -m "fix: configure backend for Vercel serverless deployment

- Add /api/index.py serverless handler at project root
- Update vercel.json for Python + React monorepo
- Fix database path resolution with environment variable
- Update CORS to allow all Vercel deployments
- Configure frontend API client for production"

# Push to trigger deployment
git push origin master
```

### Option 2: Direct Vercel Deploy

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Install Vercel CLI (if not already installed)
npm install -g vercel

# Deploy to production
vercel --prod
```

## Environment Variables to Set in Vercel

Go to: https://vercel.com/dashboard → Your Project → Settings → Environment Variables

Add these:

```
Name: ANTHROPIC_API_KEY
Value: [your-api-key]
Environment: Production

Name: ENVIRONMENT
Value: production
Environment: Production
```

## Post-Deployment Tests

### 1. Test API Health
```bash
# Replace with your actual Vercel URL
curl https://circuit-fbtth1gml-justin-groszs-projects.vercel.app/api/health
```

Expected: `{"status":"healthy","tracks_loaded":14,"drivers_loaded":30}`

### 2. Test Drivers Endpoint
```bash
curl https://circuit-fbtth1gml-justin-groszs-projects.vercel.app/api/drivers
```

Expected: Array of driver objects

### 3. Test Frontend
Open in browser:
```
https://circuit-fbtth1gml-justin-groszs-projects.vercel.app
```

Expected:
- Scout Portal loads
- Driver count shows actual number (not 0)
- No CORS errors in console
- Data loads successfully

## If Build Fails

### Check Vercel Build Logs

1. Go to Vercel Dashboard
2. Click on your deployment
3. Click "Building" tab
4. Look for error messages

### Common Issues and Fixes

**Error: "Module not found: backend/main.py"**
- Solution: Verify `api/index.py` exists at project root
- Run: `ls -la api/index.py`

**Error: "No module named 'mangum'"**
- Solution: Add `mangum==0.17.0` to `backend/requirements.txt`
- Already added in requirements.txt

**Error: "Database not found"**
- Solution: Verify `circuit-fit.db` is at project root
- Run: `ls -la circuit-fit.db`
- Check file size: Should be ~136KB

**Error: "CORS policy blocking requests"**
- Solution: Check `backend/main.py` CORS configuration
- Verify `allow_origin_regex` includes your Vercel domain

## Success Criteria

Deployment is successful when ALL are true:

- [ ] Vercel build completes (green checkmark)
- [ ] `/api/health` returns 200 status
- [ ] `/api/drivers` returns driver data
- [ ] Frontend displays driver count > 0
- [ ] Browser console has no CORS errors
- [ ] All pages navigate correctly

## Key Files Changed

These files were created or modified:

1. **Created**: `/api/index.py` - Serverless handler
2. **Updated**: `/vercel.json` - Build configuration
3. **Updated**: `/backend/database/connection.py` - Database path
4. **Updated**: `/backend/main.py` - CORS configuration
5. **Updated**: `/frontend/src/services/api.js` - API client
6. **Created**: `/frontend/.env.production` - Frontend env vars
7. **Created**: `/.env.production` - Root env vars

## Project Structure (Final)

```
hackthetrack-master/
├── api/
│   └── index.py ✅ NEW - Serverless entry point
├── backend/
│   ├── main.py ✅ UPDATED - CORS config
│   ├── database/
│   │   └── connection.py ✅ UPDATED - DB path
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── services/
│   │       └── api.js ✅ UPDATED - API URL
│   └── .env.production ✅ NEW
├── circuit-fit.db ✅ (at root)
├── vercel.json ✅ UPDATED
└── .env.production ✅ NEW
```

## Need Help?

If deployment fails, check:

1. **Vercel Build Logs**: Dashboard → Deployment → Building tab
2. **Function Logs**: Dashboard → Deployment → Functions tab
3. **Browser Console**: F12 → Console tab for frontend errors
4. **Network Tab**: F12 → Network tab to see API requests

## Quick Fixes

### If API returns 404:
```bash
# Verify api/index.py exists
ls -la api/index.py

# Check vercel.json routes configuration
cat vercel.json | grep -A 5 "routes"
```

### If frontend shows "0 drivers":
```bash
# Check if API is accessible
curl https://your-app.vercel.app/api/drivers

# Check browser console for errors
# Open DevTools → Console → Look for API errors
```

### If CORS errors:
```bash
# Verify CORS configuration in backend/main.py
grep -A 10 "CORSMiddleware" backend/main.py
```

---

**Ready to Deploy!** 🚀

Choose Option 1 (Git push) or Option 2 (Vercel CLI) above.
