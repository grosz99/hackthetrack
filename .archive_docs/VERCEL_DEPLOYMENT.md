# Vercel Deployment Guide - Full-Stack React + FastAPI

## Overview

This guide provides complete instructions for deploying your React (Vite) + FastAPI monorepo application to Vercel with proper routing for both frontend SPA and backend API.

## Project Structure

```
hackthetrack-master/
├── frontend/          # React + Vite application
│   ├── src/
│   ├── dist/         # Build output
│   ├── config/
│   │   └── vite.config.js
│   └── package.json
├── backend/          # FastAPI Python backend
│   ├── api/
│   │   └── index.py  # Vercel serverless function entry point
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   └── services/
│   ├── main.py       # FastAPI application
│   ├── requirements.txt
│   └── circuit-fit.db (SQLite database)
├── data/             # Excluded via .vercelignore
├── vercel.json       # Vercel configuration
├── .vercelignore     # Files to exclude from deployment
└── package.json      # Root package.json
```

## Issues Fixed

### Previous Issues
1. 404 errors on all routes after deployment
2. Frontend not being served correctly
3. React Router client-side routing not working
4. API routes not properly configured
5. Static assets (CSS, JS) not loading

### Root Causes
1. **Incorrect route configuration**: Using deprecated patterns
2. **Missing SPA fallback**: All non-API routes must fall back to index.html for React Router
3. **Asset path issues**: Static assets were not properly routed
4. **Build configuration**: Missing proper build commands for Vercel

## Key Configuration Changes

### 1. Updated vercel.json

The routing order and configuration is critical:
- API routes must be checked FIRST
- Static assets (JS, CSS, images) must be routed correctly
- ALL other routes must fall back to index.html for React Router

### 2. Updated Vite Configuration

Added explicit base path and build settings for Vercel compatibility.

### 3. Updated Backend Handler

Ensured proper Mangum wrapper and handler export for Vercel serverless functions.

## Deployment Steps

### Quick Deploy (Recommended)

1. **Commit Changes**
   ```bash
   git add .
   git commit -m "fix: configure Vercel deployment with corrected routing"
   git push origin master
   ```

2. **Deploy to Vercel**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Vercel will auto-detect configuration from vercel.json
   - Add environment variable: `ANTHROPIC_API_KEY`
   - Click Deploy

3. **Verify Deployment**
   ```bash
   # Test frontend routes
   curl https://your-app.vercel.app/
   curl https://your-app.vercel.app/scout
   curl https://your-app.vercel.app/scout/driver/1/overview
   
   # Test API routes
   curl https://your-app.vercel.app/api/health
   curl https://your-app.vercel.app/api/drivers
   ```

## Environment Variables Required

Add these in Vercel Dashboard (Settings > Environment Variables):

1. **ANTHROPIC_API_KEY** (Required)
   - Scope: Production + Preview + Development
   - Value: Your Anthropic API key from https://console.anthropic.com/

2. **PORT** (Optional, defaults to 8000)
   - Scope: All environments
   - Value: 8000

## Verification Checklist

After deployment, verify:

- [ ] Root route (/) loads Scout Landing page
- [ ] Direct navigation to /scout/driver/1/overview works (no 404)
- [ ] React Router navigation works without page refresh
- [ ] Assets load correctly (check DevTools Network tab)
- [ ] API endpoints respond correctly
- [ ] No CORS errors in browser console

## Common Issues & Solutions

### Issue: 404 on React Router Routes

**Solution:** The catch-all route in vercel.json must be LAST and point to `/frontend/dist/index.html`

### Issue: Assets Not Loading

**Solution:** Ensure `base: '/'` is set in vite.config.js and rebuild frontend

### Issue: API Returns 404

**Solution:** Verify `/backend/api/index.py` exists and API route is first in vercel.json

### Issue: CORS Errors

**Solution:** Add your Vercel domain to CORS origins in `/backend/main.py`

## Files Modified

1. `/vercel.json` - Updated routing configuration
2. `/frontend/package.json` - Added vercel-build script
3. `/frontend/config/vite.config.js` - Added base path and build settings
4. `/backend/api/index.py` - Updated handler wrapper

## Testing Locally Before Deploy

```bash
# Build frontend
cd frontend
npm run build

# Verify build output
ls -la dist/

# Test backend locally
cd ../backend
python main.py

# In another terminal, test frontend build
cd frontend
npm run preview
```

## Rollback Strategy

If deployment fails:

1. **Dashboard Rollback:** Deployments > Previous deployment > Promote to Production
2. **Git Rollback:** `git revert [commit-hash] && git push`
3. **CLI Rollback:** `vercel rollback [deployment-url]`

## Next Steps

1. Monitor deployment in Vercel dashboard
2. Check function logs for any errors
3. Set up custom domain if needed
4. Enable Vercel Analytics for monitoring

---

**Last Updated:** November 3, 2025
