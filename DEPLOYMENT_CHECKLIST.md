# Vercel Deployment Checklist

## Pre-Deployment Checklist

- [ ] All code changes committed to Git
- [ ] Frontend builds successfully locally (`cd frontend && npm run build`)
- [ ] Backend runs without errors locally (`cd backend && python main.py`)
- [ ] Environment variables documented in backend/.env.example
- [ ] Large files excluded in .vercelignore
- [ ] Database file (circuit-fit.db) exists and is included

## Configuration Files Checklist

- [ ] `/vercel.json` exists with correct routing
- [ ] `/frontend/package.json` has `vercel-build` script
- [ ] `/frontend/config/vite.config.js` has `base: '/'`
- [ ] `/backend/api/index.py` exports handler correctly
- [ ] `/backend/requirements.txt` has all dependencies with pinned versions
- [ ] `/.vercelignore` excludes data/ and *.csv files

## Deployment Steps

1. [ ] Push code to GitHub
   ```bash
   git add .
   git commit -m "fix: configure Vercel deployment"
   git push origin master
   ```

2. [ ] Import repository to Vercel
   - Go to https://vercel.com/new
   - Select repository
   - Framework: Other (custom config)

3. [ ] Add environment variables
   - ANTHROPIC_API_KEY (required)
   - Scope: Production + Preview + Development

4. [ ] Click Deploy
   - Wait 2-4 minutes for build

## Post-Deployment Verification

### Frontend Checks
- [ ] Root loads: `https://your-app.vercel.app/`
- [ ] Scout page loads: `https://your-app.vercel.app/scout`
- [ ] Driver route loads: `https://your-app.vercel.app/scout/driver/1/overview`
- [ ] No 404 errors on direct navigation to routes
- [ ] React Router navigation works without refresh

### Asset Checks
- [ ] CSS loads (check DevTools > Network)
- [ ] JavaScript loads (no errors in Console)
- [ ] Images/SVGs load correctly
- [ ] No 404s for any static assets

### API Checks
- [ ] Health endpoint works: `curl https://your-app.vercel.app/api/health`
- [ ] Root API works: `curl https://your-app.vercel.app/api/`
- [ ] Drivers endpoint works: `curl https://your-app.vercel.app/api/drivers`
- [ ] No CORS errors in browser console

### Backend Checks
- [ ] Check function logs in Vercel dashboard
- [ ] No serverless function errors
- [ ] Database queries work correctly
- [ ] API responses are correct format

## Troubleshooting

### If You See 404 Errors

1. Check catch-all route in vercel.json is LAST
2. Verify route points to `/frontend/dist/index.html`
3. Redeploy after fixing

### If Assets Don't Load

1. Check `base: '/'` in vite.config.js
2. Rebuild: `cd frontend && npm run build`
3. Commit and push changes

### If API Doesn't Work

1. Check `/backend/api/index.py` exists
2. Verify handler is exported
3. Check function logs in dashboard
4. Verify environment variables are set

### If CORS Errors Appear

1. Add Vercel domain to CORS in backend/main.py
2. Redeploy

## Rollback Plan

If something goes wrong:

### Option 1: Dashboard
1. Go to Deployments
2. Find previous working deployment
3. Click "Promote to Production"

### Option 2: Git
```bash
git revert HEAD
git push origin master
```

## Success Criteria

Deployment is successful when:
- [ ] All frontend routes load without 404
- [ ] All static assets load without errors
- [ ] All API endpoints return correct data
- [ ] No CORS errors in browser
- [ ] React Router navigation works correctly
- [ ] No errors in Vercel function logs

## Support Resources

- Vercel Docs: https://vercel.com/docs
- Vercel Status: https://vercel-status.com
- Project Logs: Dashboard > Deployments > [Your Deploy] > Logs
- Function Logs: Dashboard > Project > Functions

---

**Quick Command Reference:**

```bash
# Local build test
cd frontend && npm run build && npm run preview

# Deploy via CLI
vercel --prod

# Check logs
vercel logs [deployment-url]

# Rollback
vercel rollback [deployment-url]
```
