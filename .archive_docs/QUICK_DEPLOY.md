# Quick Deploy to Vercel - 5 Minute Guide

## Prerequisites

- GitHub repository with latest code
- Vercel account (free tier works)
- Anthropic API key

## Step 1: Verify Local Build (2 minutes)

```bash
# Navigate to frontend
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend

# Install dependencies and build
npm install
npm run build

# Verify build output
ls -la dist/
# Should see: index.html, assets/, track_maps/

# Quick test
npm run preview
# Open http://localhost:4173 and verify it loads
```

## Step 2: Commit and Push (1 minute)

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

git add .
git commit -m "fix: configure Vercel deployment with corrected routing"
git push origin master
```

## Step 3: Deploy to Vercel (2 minutes)

### Option A: Via Dashboard (Recommended)

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your repository
4. Configure:
   - Framework Preset: **Other**
   - Root Directory: `./`
   - Leave other settings as auto-detected
5. Add Environment Variable:
   - Key: `ANTHROPIC_API_KEY`
   - Value: `your-api-key-here`
   - Scope: Production + Preview + Development
6. Click "Deploy"
7. Wait 2-3 minutes

### Option B: Via CLI

```bash
# Install Vercel CLI if needed
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod

# When prompted, add environment variables:
vercel env add ANTHROPIC_API_KEY
```

## Step 4: Verify Deployment (1 minute)

Visit your deployment URL (e.g., https://your-app.vercel.app):

### Quick Checks
- [ ] Root loads: `/`
- [ ] Scout page: `/scout`
- [ ] Driver page: `/scout/driver/1/overview`
- [ ] API health: `/api/health`

### Browser DevTools Checks
- [ ] Network tab shows no 404s
- [ ] Console shows no errors
- [ ] Assets load (check CSS, JS files)

## Troubleshooting

### If you see 404 errors:

1. Check Vercel build logs in dashboard
2. Verify `vercel.json` is committed
3. Rebuild frontend: `cd frontend && npm run build && git add . && git commit -m "rebuild" && git push`

### If assets don't load:

1. Clear Vercel cache: Dashboard > Settings > Clear Cache
2. Redeploy: Dashboard > Deployments > [Latest] > Redeploy

### If API fails:

1. Check environment variables: Dashboard > Settings > Environment Variables
2. Verify `ANTHROPIC_API_KEY` is set for all environments
3. Check function logs: Dashboard > Functions > api/index

## Success!

If all checks pass:
- Your app is live at https://your-app.vercel.app
- Automatic deployments on push to master
- Preview deployments for PRs

## What Was Fixed?

This deployment works because we:
1. Fixed route configuration in vercel.json (proper order, SPA fallback)
2. Added base path to vite.config.js (assets load correctly)
3. Added vercel-build script (respects custom config)
4. Excluded large files via .vercelignore (faster builds)

## Configuration Files

All configuration is already set up:
- `/vercel.json` - Routing and build config
- `/frontend/config/vite.config.js` - Base path and build settings
- `/frontend/package.json` - Build scripts
- `/backend/api/index.py` - Serverless function handler
- `/.vercelignore` - Excluded files

## Need More Help?

- Detailed guide: `VERCEL_DEPLOYMENT.md`
- Checklist: `DEPLOYMENT_CHECKLIST.md`
- What was fixed: `DEPLOYMENT_FIXES_SUMMARY.md`

## Rollback

If something goes wrong:
1. Dashboard > Deployments
2. Find previous working deployment
3. Click "..." > "Promote to Production"

---

**Total Time:** ~5 minutes
**Cost:** Free (Vercel free tier)
**Next Deploy:** Automatic on git push
