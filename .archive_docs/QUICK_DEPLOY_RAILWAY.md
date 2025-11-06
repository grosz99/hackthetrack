# Quick Deploy Reference Card - Railway + Vercel

## TL;DR - Deploy in 5 Commands

```bash
# 1. Deploy backend to Railway
cd backend
railway login && railway init && railway up
railway domain  # Copy this URL

# 2. Deploy frontend to Vercel
cd ..
npm i -g vercel
vercel login
vercel  # Preview first

# 3. Set environment variable in Vercel dashboard
# VITE_API_URL = https://your-railway-backend.railway.app

# 4. Deploy to production
vercel --prod

# 5. Test
curl https://your-app.vercel.app
```

## Critical Environment Variable

**In Vercel Dashboard** → Project Settings → Environment Variables:

```
VITE_API_URL = https://your-railway-backend.railway.app
```

**NO TRAILING SLASH!**

## Files Changed Summary

| File | What Changed |
|------|--------------|
| `vercel.json` | Frontend-only config, removed API routes |
| `frontend/src/services/api.js` | Use VITE_API_URL for all environments |
| `frontend/.env.production` | Point to Railway backend |

## Test Command

```bash
# Local test with Railway backend
cd frontend
VITE_API_URL=https://your-backend.railway.app npm run preview
```

## Verification Checklist

```bash
# Backend health
curl https://your-backend.railway.app/api/health

# Frontend loads
curl https://your-app.vercel.app

# Check Vercel deployment
vercel ls

# Check Railway logs
railway logs
```

## Common Issues & Fixes

### CORS Error
```python
# In backend: Update CORS origins
origins = ["https://your-app.vercel.app", "https://*.vercel.app"]
```

### API 404
1. Check VITE_API_URL is set in Vercel
2. Verify Railway backend is running
3. Redeploy Vercel after setting env var

### SPA 404 on Refresh
Already fixed in `vercel.json` with:
```json
{"source": "/(.*)", "destination": "/index.html"}
```

## Rollback

```bash
vercel rollback [previous-deployment-url]
```

## Full Documentation

- **Complete Guide**: `VERCEL_DEPLOYMENT_GUIDE.md`
- **Backend Setup**: `RAILWAY_BACKEND_SETUP.md`
- **Detailed Checklist**: `DEPLOYMENT_CHECKLIST.md`
- **Summary**: `VERCEL_DEPLOYMENT_SUMMARY.md`

## Architecture

```
Browser → Vercel (Static Frontend) → Railway (API Backend)
```

## Cost

- Vercel: Free tier (sufficient)
- Railway: ~$10-20/month

## Status: READY TO DEPLOY ✅

All configuration complete. Follow commands above.
