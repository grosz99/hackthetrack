# 🚀 Vercel Deployment Checklist

## ✅ Security & Credentials (COMPLETE FIRST)

- [ ] **Read SECURITY_ROTATION_GUIDE.md completely**
- [ ] Rotate Anthropic API key (revoke old, generate new)
- [ ] Rotate Snowflake password OR configure key-pair auth
- [ ] Set ALL environment variables in Vercel
- [ ] Verify `.env` and `rsa_key.*` files are in `.gitignore`
- [ ] Run `git status` - should show NO secret files
- [ ] Delete local `.env` file with old credentials
- [ ] Test Snowflake connection with new credentials locally

## ✅ Code Fixes (COMPLETED ✓)

- [x] Fix API route prefix in `getTracks()` function
- [x] Add `scipy` and `cryptography` to requirements.txt
- [x] Fix `/predict` endpoint to accept JSON body
- [x] Update Snowflake service to query `TELEMETRY_DATA_ALL`
- [x] Verify all processed CSV files have `track_id` and `race_num`

## ✅ Pre-Deployment Tests

- [ ] **Test Backend Locally**:
  ```bash
  cd backend
  python -c "from app.services.snowflake_service_v2 import snowflake_service; print(snowflake_service.check_connection())"
  python -c "from app.services.snowflake_service_v2 import snowflake_service; print(len(snowflake_service.get_drivers_with_telemetry()))"
  ```

- [ ] **Test Frontend Build**:
  ```bash
  cd frontend
  npm run build
  # Should complete without errors
  ```

- [ ] **Check Bundle Size**:
  ```bash
  cd frontend/dist
  ls -lh
  # assets/ folder should be < 10MB total
  ```

## ✅ Vercel Configuration

### Environment Variables to Set:

**Snowflake** (Required):
```
SNOWFLAKE_ACCOUNT=EOEPNYL-PR46214
SNOWFLAKE_USER=hackthetrack_svc
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKTHETRACK
SNOWFLAKE_SCHEMA=TELEMETRY
SNOWFLAKE_ROLE=ACCOUNTADMIN
USE_SNOWFLAKE=true
```

**Choose auth method**:
```
SNOWFLAKE_PASSWORD=<new-password>
OR
SNOWFLAKE_PRIVATE_KEY=<paste-key-with-\n>
```

**Anthropic** (Required):
```
ANTHROPIC_API_KEY=<new-rotated-key>
```

**Frontend** (Required):
```
FRONTEND_URL=https://your-domain.vercel.app
```

**Performance** (Optional):
```
SNOWFLAKE_LOGIN_TIMEOUT=5
SNOWFLAKE_NETWORK_TIMEOUT=15
SNOWFLAKE_MAX_RETRIES=2
ENVIRONMENT=production
```

### Verify vercel.json Exists:
- [ ] Check `vercel.json` has correct build and rewrite configuration

## ✅ Git Commit & Push

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Check what will be committed
git status

# Stage security improvements
git add .gitignore backend/.gitignore backend/.env.example

# Stage code fixes
git add frontend/src/services/api.js
git add backend/requirements.txt
git add backend/app/api/routes.py
git add backend/app/services/snowflake_service_v2.py

# Commit
git commit -m "fix(deployment): prepare for Vercel deployment

- Fix API route prefix in getTracks()
- Add scipy and cryptography dependencies
- Fix /predict endpoint to accept JSON body
- Update Snowflake service to query TELEMETRY_DATA_ALL
- Enhance .gitignore to prevent credential exposure
- Add comprehensive .env.example template

SECURITY: All secrets managed via Vercel environment variables"

# Push to main/master branch
git push origin master
```

## ✅ Deploy to Vercel

### Option A: Deploy via Vercel Dashboard

1. Go to: https://vercel.com/new
2. Import your Git repository
3. Configure project:
   - Framework Preset: `Vite`
   - Root Directory: `./`
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
   - Install Command: `npm install`

4. Add Environment Variables (from checklist above)

5. Click "Deploy"

### Option B: Deploy via CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
vercel --prod

# Follow prompts and set environment variables
```

## ✅ Post-Deployment Verification

### Test Critical Endpoints:

1. **Health Check**:
   ```bash
   curl https://your-app.vercel.app/api/health
   # Should return 200 with Snowflake connection status
   ```

2. **Get Drivers**:
   ```bash
   curl https://your-app.vercel.app/api/telemetry/drivers
   # Should return list of 35 drivers
   ```

3. **Get Track**:
   ```bash
   curl https://your-app.vercel.app/api/tracks/barber
   # Should return Barber Motorsports Park data
   ```

4. **Get Telemetry** (requires track_id, race_num, driver_number):
   ```bash
   curl "https://your-app.vercel.app/api/telemetry/detailed?track_id=barber&race_num=1&driver_number=13"
   # Should return telemetry data
   ```

### Test Frontend:

1. Open: `https://your-app.vercel.app`
2. Navigate to Scout Landing page
3. Select a driver (e.g., Driver 13)
4. Check each tab:
   - [ ] Overview page loads
   - [ ] RaceLog page loads
   - [ ] Skills page loads
   - [ ] Improve page loads
5. Verify no console errors (F12 → Console)
6. Check Network tab for API calls (should all be 200)

## ✅ Monitor Deployment

### Check Vercel Logs:

1. Go to: Vercel Dashboard → Your Project → Deployments → Latest
2. Click "View Function Logs"
3. Monitor for errors:
   - Snowflake connection errors
   - API timeout errors
   - CORS errors

### Monitor Performance:

- Function Execution Time (should be < 10s)
- Cold Start Time (should be < 3s)
- Error Rate (should be < 1%)

## ✅ Rollback Plan (If Issues Occur)

If deployment has critical issues:

1. **Immediate Rollback**:
   - Go to Vercel Dashboard → Deployments
   - Find previous working deployment
   - Click "..." → "Promote to Production"

2. **Investigate Logs**:
   ```bash
   vercel logs <deployment-url>
   ```

3. **Common Issues**:
   - **Snowflake timeout**: Reduce `SNOWFLAKE_NETWORK_TIMEOUT` to 10
   - **CORS errors**: Check `FRONTEND_URL` environment variable
   - **404 errors**: Verify `vercel.json` rewrites configuration
   - **Build failure**: Check `package.json` scripts

## ✅ Success Criteria

Deployment is successful when:

- [ ] Frontend loads at production URL
- [ ] All API endpoints return 200 status codes
- [ ] Driver data loads correctly
- [ ] Telemetry data displays on Improve page
- [ ] No errors in browser console
- [ ] No errors in Vercel function logs
- [ ] Page navigation works (Overview → RaceLog → Skills → Improve)
- [ ] Snowflake connection is stable

## 🎉 Post-Deployment

- [ ] Update team on deployment status
- [ ] Share production URL with stakeholders
- [ ] Monitor for 24 hours for any issues
- [ ] Schedule credential rotation reminder (90 days)
- [ ] Document any deployment issues encountered
- [ ] Update README.md with production URL

---

**Estimated Time**: 2-3 hours (including security rotation and testing)

**Critical Path**: Security → Code Fixes → Test → Deploy → Verify
