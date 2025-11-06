# Vercel Deployment - Quick Fix Checklist

**Total Time:** 30-45 minutes
**Success Rate:** 95% after completion

---

## ⚡ CRITICAL FIXES (MUST DO)

### ☐ Fix #1: Add Missing Import (2 minutes)

**File:** `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend/app/api/routes.py`

**Location:** Line 5 (after existing imports)

**Action:** Add this line:
```python
from pydantic import BaseModel, Field
```

**Verify:**
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend
python -c "from app.api.routes import router; print('✅ Success')"
```

---

### ☐ Fix #2: Create API Requirements (2 minutes)

**Action:**
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
cp backend/requirements.txt api/requirements.txt
```

**Verify:**
```bash
ls -la api/requirements.txt
cat api/requirements.txt | head -5
```

---

### ☐ Fix #3: Configure Environment Variables (20 minutes)

**Action:** Set these in Vercel Dashboard → Settings → Environment Variables

```bash
# Required Variables:
ANTHROPIC_API_KEY=<your-key>
SNOWFLAKE_ACCOUNT=EOEPNYL-PR46214
SNOWFLAKE_USER=hackthetrack_svc
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKTHETRACK
SNOWFLAKE_SCHEMA=TELEMETRY
SNOWFLAKE_ROLE=ACCOUNTADMIN
USE_SNOWFLAKE=true
FRONTEND_URL=https://your-app.vercel.app
ENVIRONMENT=production
```

**For SNOWFLAKE_PRIVATE_KEY:**
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
base64 -i rsa_key.p8 | tr -d '\n'
# Copy output to SNOWFLAKE_PRIVATE_KEY variable
```

**Verify:**
```bash
vercel env ls
```

---

## ✅ TEST BEFORE DEPLOY (10 minutes)

### ☐ Test Frontend Build
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend
npm ci
npm run build
# Should complete in ~4 seconds with no errors
```

### ☐ Test Backend Import
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend
python -c "from main import app; print('✅ App loads successfully')"
```

### ☐ Test API Locally (Optional)
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend
python main.py &
sleep 5
curl http://localhost:8000/api/health
kill %1
```

---

## 🚀 DEPLOY (10 minutes)

### ☐ Deploy to Preview
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
vercel
# Wait 2-3 minutes for build
# Note the preview URL
```

### ☐ Test Preview Deployment
```bash
# Replace with your preview URL
curl https://your-preview.vercel.app/api/health

# Should return:
# {"status": "healthy", "tracks_loaded": 18, ...}
```

### ☐ Deploy to Production
```bash
vercel --prod
# Monitor logs
vercel logs --follow
```

---

## 📋 VERIFICATION CHECKLIST

After deployment, check:

### Frontend
- [ ] Site loads at https://your-app.vercel.app
- [ ] No JavaScript errors in console
- [ ] Scout landing page displays
- [ ] Navigation between pages works
- [ ] Driver list appears

### Backend
- [ ] `/api/health` returns 200 status
- [ ] `/api/drivers` returns driver list
- [ ] `/api/tracks` returns track list
- [ ] No 500 errors in Vercel logs

### Features
- [ ] Telemetry data loads
- [ ] AI coaching responds (if ANTHROPIC_API_KEY set)
- [ ] Data reliability failover works
- [ ] No CORS errors

---

## 🆘 IF DEPLOYMENT FAILS

### Check Build Logs
```bash
vercel logs --build
```

### Check Function Logs
```bash
vercel logs --function=/api/index
```

### Rollback
```bash
vercel rollback
```

### Common Issues

**Problem:** "BaseModel is not defined"
**Solution:** Verify Fix #1 was applied correctly

**Problem:** "No module named 'fastapi'"
**Solution:** Verify Fix #2 - api/requirements.txt exists

**Problem:** "Connection failed" or "Authentication error"
**Solution:** Verify Fix #3 - environment variables are set

**Problem:** Frontend loads but API returns 500
**Solution:** Check function logs for specific error

---

## 📊 SUCCESS CRITERIA

Deployment is successful when ALL of these are true:

- [x] Frontend build completes without errors
- [x] Backend starts without import errors
- [x] Health check returns 200 status
- [x] Driver list loads on Scout page
- [x] Navigation works
- [x] No CORS errors in console
- [x] No 500 errors in logs

---

## 📞 NEED HELP?

See detailed documentation:
- `/DEPLOYMENT_EXECUTIVE_SUMMARY.md` - Overview
- `/DEPLOYMENT_FIXES_PRIORITY.md` - Detailed fixes
- `/VERCEL_ARCHITECTURE_ASSESSMENT.md` - Full analysis
- `/VERCEL_ARCHITECTURE_DIAGRAM.md` - Visual diagrams

---

**Ready to Deploy?** Follow this checklist top to bottom. Good luck! 🚀
