# VERCEL DEPLOYMENT CHECKLIST

## PRE-DEPLOYMENT VERIFICATION

### 1. Files Modified ✅

- [x] `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend/app/api/routes.py`
  - Removed `prefix="/api"` from APIRouter

- [x] `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend/main.py`
  - Added `prefix="/api"` to router inclusion

- [x] `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend/src/services/api.js`
  - Changed production `API_BASE_URL` from `'/api'` to `''` (empty string)

- [x] `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/api/index.py`
  - Simplified and cleaned up serverless handler

- [x] `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/vercel.json`
  - Complete rewrite with correct configuration

### 2. Local Testing

```bash
# Test backend starts correctly
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend
python main.py

# Expected: Server running on http://0.0.0.0:8000
# Test: http://localhost:8000/api/health
```

```bash
# Test frontend builds correctly
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend
npm run build

# Expected: Build successful, dist/ folder created
# Verified: ✅ Build completed (738.79 kB main bundle)
```

### 3. Required Files Present

- [x] `circuit-fit.db` (292KB) at project root
- [x] `requirements.txt` at project root
- [x] `api/index.py` (serverless entry point)
- [x] `vercel.json` (deployment config)
- [x] `.vercelignore` (exclude large files)
- [x] `frontend/dist/index.html` (after build)

### 4. Configuration Verification

**vercel.json:**
```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "rewrites": [
    { "source": "/api/:path*", "destination": "/api/index.py" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**frontend/src/services/api.js:**
```javascript
// Production: API_BASE_URL = '' (empty)
// Calls: /api/drivers, /api/tracks, etc.
```

**backend/main.py:**
```python
# Router included with /api prefix
app.include_router(router, prefix="/api")
```

---

## DEPLOYMENT COMMANDS

### Option 1: Vercel CLI (Recommended)

```bash
# From project root
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Deploy to production
vercel --prod

# Monitor deployment
vercel logs --prod --follow
```

### Option 2: Git Push (Auto-deploy)

```bash
# Commit all changes
git add .
git commit -m "fix: resolve Vercel 404 errors with routing configuration"
git push origin master

# Vercel will auto-deploy if connected to GitHub
```

---

## POST-DEPLOYMENT VERIFICATION

### 1. Frontend Routes (Should Return HTML)

```bash
# Replace with your actual Vercel URL
VERCEL_URL="https://your-app.vercel.app"

# Homepage
curl -I $VERCEL_URL/
# Expected: 200 OK, text/html

# React Router routes
curl -I $VERCEL_URL/drivers
curl -I $VERCEL_URL/tracks
# Expected: 200 OK, text/html (SPA fallback)

# Static assets
curl -I $VERCEL_URL/vite.svg
# Expected: 200 OK, image/svg+xml
```

### 2. API Routes (Should Return JSON)

```bash
# Health check
curl $VERCEL_URL/api/health
# Expected: {"status":"healthy","tracks_loaded":X,"drivers_loaded":Y}

# Drivers endpoint
curl $VERCEL_URL/api/drivers
# Expected: JSON array of driver objects

# Tracks endpoint
curl $VERCEL_URL/api/tracks
# Expected: JSON array of track objects

# Specific driver
curl $VERCEL_URL/api/drivers/11
# Expected: JSON object with driver data
```

### 3. Browser Testing

Open browser to `https://your-app.vercel.app` and verify:

- [ ] Homepage loads without errors
- [ ] Navigation menu works
- [ ] `/drivers` page loads and shows data
- [ ] `/tracks` page loads and shows data
- [ ] No CORS errors in console (F12)
- [ ] No 404 errors in network tab
- [ ] Data displays correctly (from database)

### 4. Vercel Dashboard Checks

Go to https://vercel.com/dashboard and verify:

- [ ] Build completed successfully (green checkmark)
- [ ] No build errors in logs
- [ ] Function deployed successfully
- [ ] Domain is active

---

## TROUBLESHOOTING QUICK REFERENCE

### Issue: Frontend 404

**Symptom:** `/drivers` returns 404
**Cause:** SPA fallback not working
**Fix:**
```bash
# Check vercel.json has catch-all rewrite
grep -A 3 "rewrites" vercel.json
# Should include: { "source": "/(.*)", "destination": "/index.html" }
```

### Issue: API 404

**Symptom:** `/api/drivers` returns 404
**Cause:** Serverless function not deployed or wrong routing
**Fix:**
```bash
# Check function exists
ls -la api/index.py

# Check logs
vercel logs --prod | grep -i error

# Redeploy
vercel --prod --force
```

### Issue: Database Errors

**Symptom:** "Database not found" or "No such table"
**Cause:** Database file not deployed or wrong path
**Fix:**
```bash
# Verify database at root
ls -lh circuit-fit.db

# Check not in .vercelignore
grep -i "circuit-fit.db" .vercelignore
# Should NOT be listed

# Verify size (should be ~292KB)
du -sh circuit-fit.db
```

### Issue: Module Import Errors

**Symptom:** "ModuleNotFoundError: No module named 'app'"
**Cause:** Python path not set correctly
**Fix:**
```bash
# Check api/index.py has:
grep "sys.path.insert" api/index.py
# Should include: sys.path.insert(0, str(backend_dir))

# Verify backend/__init__.py exists
ls -la backend/__init__.py
```

### Issue: CORS Errors

**Symptom:** "CORS policy: No 'Access-Control-Allow-Origin'"
**Cause:** Backend CORS not configured for Vercel domain
**Fix:**
```python
# Check backend/main.py has:
allow_origin_regex=r"https://.*\.vercel\.app"
```

---

## ROLLBACK PLAN

If deployment fails, rollback with:

```bash
# Option 1: Rollback via Vercel CLI
vercel rollback

# Option 2: Rollback via Vercel Dashboard
# Go to Deployments → Select working deployment → Promote to Production
```

---

## SUCCESS METRICS

After successful deployment, you should see:

1. **Build Time:** ~2-3 minutes
2. **Function Cold Start:** <2 seconds
3. **API Response Time:** <500ms
4. **Frontend Load Time:** <2 seconds
5. **No 404 Errors:** 0
6. **No CORS Errors:** 0
7. **Database Queries Work:** Yes

---

## NEXT STEPS AFTER DEPLOYMENT

### 1. Set Up Custom Domain (Optional)

```bash
vercel domains add yourdomain.com
```

### 2. Configure Environment Variables

If you need to add secrets (e.g., Anthropic API key):

```bash
vercel env add ANTHROPIC_API_KEY
# Paste your API key when prompted
```

### 3. Enable Monitoring

- Set up Vercel Analytics
- Configure error tracking (Sentry, etc.)
- Set up uptime monitoring

### 4. Optimize Performance

- Enable Vercel's Edge Caching
- Consider splitting frontend bundle
- Optimize images

### 5. Database Migration (Future)

If you need write operations:
- Migrate to Vercel Postgres or Turso
- Update connection.py to use new database

---

## SUPPORT RESOURCES

- **Vercel Docs:** https://vercel.com/docs
- **FastAPI on Vercel:** https://vercel.com/guides/python-serverless
- **Vite Deployment:** https://vitejs.dev/guide/static-deploy.html
- **Mangum (Lambda/Vercel):** https://github.com/jordaneremieff/mangum

---

## DEPLOYMENT STATUS

- [x] Code changes completed
- [x] Local testing passed
- [x] Frontend builds successfully
- [ ] **READY TO DEPLOY** → Run `vercel --prod`
