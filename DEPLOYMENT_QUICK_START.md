# Snowflake + Vercel Deployment Quick Start Guide

## TL;DR - Get to Production in 30 Minutes

This guide will help you deploy your Snowflake-integrated backend to Vercel serverless.

---

## Prerequisites

- [ ] Snowflake account with data loaded (HACKTHETRACK.TELEMETRY.telemetry_data)
- [ ] RSA key-pair authentication configured (rsa_key.p8)
- [ ] Vercel account and CLI installed (`npm i -g vercel`)
- [ ] Backend code with tests passing locally

---

## Step 1: Update Backend Code (15 minutes)

### 1.1 Replace Snowflake Service

```bash
# Backup current service
cd backend
cp app/services/snowflake_service.py app/services/snowflake_service_backup.py

# Replace with Vercel-compatible version
mv app/services/snowflake_service_v2.py app/services/snowflake_service.py
```

### 1.2 Test Locally

```bash
# Set environment variable for testing
export SNOWFLAKE_PRIVATE_KEY=$(cat ../rsa_key.p8 | tr '\n' '\\n')

# Run tests
pytest tests/test_snowflake_integration.py -v

# Start local server
python main.py

# Test endpoint
curl http://localhost:8000/api/telemetry/drivers
```

---

## Step 2: Prepare Private Key for Vercel (5 minutes)

### 2.1 Convert Key to Environment Variable Format

```bash
# Run helper script
./scripts/prepare_private_key_for_vercel.sh ../rsa_key.p8

# This creates: snowflake_key_for_vercel.txt
# Contains your key in one-line format for Vercel
```

### 2.2 Copy Key Content

```bash
# Open the file
cat snowflake_key_for_vercel.txt

# Copy the entire key value (including -----BEGIN PRIVATE KEY----- and -----END PRIVATE KEY-----)
```

**SECURITY**: Delete this file after use: `rm snowflake_key_for_vercel.txt`

---

## Step 3: Configure Vercel Environment Variables (5 minutes)

### 3.1 Via Vercel Dashboard (Recommended)

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add each variable below:

| Variable Name | Value | Environments |
|--------------|-------|--------------|
| `SNOWFLAKE_ACCOUNT` | `EOEPNYL-PR46214` | Production, Preview, Development |
| `SNOWFLAKE_USER` | `hackthetrack_svc` | Production, Preview, Development |
| `SNOWFLAKE_PRIVATE_KEY` | (paste from snowflake_key_for_vercel.txt) | Production, Preview, Development |
| `SNOWFLAKE_ROLE` | `ACCOUNTADMIN` | Production, Preview, Development |
| `SNOWFLAKE_WAREHOUSE` | `COMPUTE_WH` | Production, Preview, Development |
| `SNOWFLAKE_DATABASE` | `HACKTHETRACK` | Production, Preview, Development |
| `SNOWFLAKE_SCHEMA` | `TELEMETRY` | Production, Preview, Development |
| `USE_SNOWFLAKE` | `true` | Production, Preview, Development |
| `ANTHROPIC_API_KEY` | (your key) | Production, Preview, Development |

### 3.2 Via Vercel CLI (Alternative)

```bash
# Set each variable
vercel env add SNOWFLAKE_ACCOUNT
# Enter value when prompted
# Select: Production, Preview, Development

# Repeat for all variables above
```

### 3.3 Verify Variables

```bash
# List all environment variables
vercel env ls

# Pull variables to local file for testing
vercel env pull .env.vercel

# Verify
cat .env.vercel | grep SNOWFLAKE
```

---

## Step 4: Deploy to Vercel (5 minutes)

### 4.1 Deploy to Preview First

```bash
# Deploy to preview environment
vercel

# Output will show preview URL like:
# https://hackthetrack-abc123.vercel.app
```

### 4.2 Test Preview Deployment

```bash
# Test with validation script
python scripts/validate_deployment.py --url https://hackthetrack-abc123.vercel.app

# Should output:
# ✅ ALL TESTS PASSED - DEPLOYMENT IS HEALTHY

# Or test manually
curl https://hackthetrack-abc123.vercel.app/api/health
curl https://hackthetrack-abc123.vercel.app/api/telemetry/drivers
```

**Expected Response** (driver list):
```json
{
  "drivers_with_telemetry": [0, 2, 3, 5, 7, 13, 27, ...],
  "count": 25,
  "source": "snowflake"
}
```

⚠️ If `"source": "local"`, check Snowflake environment variables!

### 4.3 Deploy to Production

```bash
# If preview tests pass, deploy to production
vercel --prod

# Output will show production URL
```

### 4.4 Test Production Deployment

```bash
# Test production
python scripts/validate_deployment.py --url https://your-prod-domain.vercel.app

# Monitor logs
vercel logs --follow
```

---

## Troubleshooting

### Issue: "Connection failed" in Vercel

**Symptoms**: Health check fails, Snowflake errors in logs

**Fixes**:

1. **Check private key format**:
   ```bash
   # In Vercel dashboard, check SNOWFLAKE_PRIVATE_KEY value
   # Should start with: -----BEGIN PRIVATE KEY-----\n
   # Should end with: \n-----END PRIVATE KEY-----
   ```

2. **Verify account format**:
   ```bash
   # Correct format: ORGNAME-ACCOUNTNAME or ACCOUNTID.REGION
   # Example: EOEPNYL-PR46214
   # NOT: https://app.snowflake.com/...
   ```

3. **Check warehouse status**:
   - Log into Snowflake console
   - Verify warehouse is running (not suspended)
   - Check user has permissions

### Issue: "0 drivers" returned

**Symptoms**: Driver list is empty, `"count": 0`

**Fixes**:

1. **Check Snowflake data**:
   ```sql
   -- In Snowflake console
   USE DATABASE HACKTHETRACK;
   USE SCHEMA TELEMETRY;
   SELECT COUNT(DISTINCT vehicle_number) FROM telemetry_data;
   -- Should return > 0
   ```

2. **Verify environment variable**:
   ```bash
   # Check USE_SNOWFLAKE is set to "true"
   vercel env ls | grep USE_SNOWFLAKE
   ```

3. **Check fallback source**:
   - If response shows `"source": "local"`, Snowflake connection failed
   - Check Vercel logs for error details: `vercel logs`

### Issue: "Timeout" or slow responses

**Symptoms**: Requests take >10 seconds or timeout

**Fixes**:

1. **Check warehouse size**:
   - Small warehouses may be slow for large queries
   - Consider upgrading to MEDIUM or LARGE

2. **Optimize queries**:
   - Check Snowflake query history for slow queries
   - Add indexes if needed

3. **Implement caching**:
   - Use Vercel Edge Config for driver list caching
   - Reduces Snowflake queries by 80%

### Issue: "Authentication failed"

**Symptoms**: "Invalid username or password" errors

**Fixes**:

1. **Test credentials locally**:
   ```bash
   # Set environment variables from Vercel
   export SNOWFLAKE_ACCOUNT="EOEPNYL-PR46214"
   export SNOWFLAKE_USER="hackthetrack_svc"
   export SNOWFLAKE_PRIVATE_KEY=$(cat ../rsa_key.p8 | tr '\n' '\\n')

   # Run Python test
   python -c "from app.services.snowflake_service import snowflake_service; print(snowflake_service.check_connection())"
   ```

2. **Verify RSA public key uploaded**:
   - Log into Snowflake as ACCOUNTADMIN
   - Check user has public key: `DESC USER hackthetrack_svc;`
   - Should show RSA_PUBLIC_KEY_FP

3. **Check user permissions**:
   ```sql
   -- Grant required permissions
   GRANT USAGE ON WAREHOUSE COMPUTE_WH TO USER hackthetrack_svc;
   GRANT USAGE ON DATABASE HACKTHETRACK TO USER hackthetrack_svc;
   GRANT USAGE ON SCHEMA HACKTHETRACK.TELEMETRY TO USER hackthetrack_svc;
   GRANT SELECT ON ALL TABLES IN SCHEMA HACKTHETRACK.TELEMETRY TO USER hackthetrack_svc;
   ```

---

## Monitoring After Deployment

### 1. Check Vercel Logs

```bash
# Real-time logs
vercel logs --follow

# Filter for errors
vercel logs | grep ERROR

# Filter for Snowflake
vercel logs | grep Snowflake
```

### 2. Test Critical Endpoints

```bash
# Health check (should respond in <1s)
time curl https://your-domain.vercel.app/api/health

# Driver list (should respond in <5s)
time curl https://your-domain.vercel.app/api/telemetry/drivers

# Coaching endpoint (test with real driver numbers)
curl -X POST https://your-domain.vercel.app/api/telemetry/coaching \
  -H "Content-Type: application/json" \
  -d '{
    "track_id": "barber",
    "race_num": 1,
    "driver_number": 13,
    "reference_driver_number": 27
  }'
```

### 3. Monitor Snowflake Usage

- Log into Snowflake console
- Go to **Activity** → **Query History**
- Filter by user: `hackthetrack_svc`
- Check:
  - Query count (should be reasonable)
  - Query duration (should be <5s)
  - Data scanned (optimize if excessive)
  - Warehouse usage (check credits consumed)

### 4. Set Up Alerts (Optional but Recommended)

```bash
# Install Sentry for error tracking
pip install sentry-sdk[fastapi]

# Add to requirements.txt
echo "sentry-sdk[fastapi]==1.40.0" >> requirements.txt

# Configure in main.py
# See SNOWFLAKE_DEPLOYMENT_VALIDATION.md Section 7.2
```

---

## Success Criteria

Your deployment is successful when:

- ✅ Health check returns `"status": "healthy"`
- ✅ Driver list returns `"source": "snowflake"` (not "local")
- ✅ Driver list has `"count" > 0` (not 0 drivers!)
- ✅ Response times <5 seconds for driver list
- ✅ Coaching endpoint returns telemetry insights
- ✅ No authentication errors in logs
- ✅ Frontend can fetch and display driver data

---

## Rollback Plan

If deployment fails:

```bash
# Option 1: Revert to previous deployment
vercel rollback <previous-deployment-url>

# Option 2: Disable Snowflake temporarily
# In Vercel dashboard, change:
USE_SNOWFLAKE=false
# This falls back to local CSV files

# Option 3: Restore old service
cd backend
cp app/services/snowflake_service_backup.py app/services/snowflake_service.py
vercel --prod
```

---

## Next Steps

After successful deployment:

1. **Implement Caching** (improves performance by 80%)
   - See: SNOWFLAKE_DEPLOYMENT_VALIDATION.md Section 6.2
   - Use Vercel Edge Config or KV store

2. **Add Error Tracking** (catch production issues)
   - Install Sentry: `pip install sentry-sdk[fastapi]`
   - Configure DSN in environment variables

3. **Optimize Queries** (reduce Snowflake costs)
   - Add indexes on commonly queried columns
   - Enable result caching in Snowflake

4. **Set Up Monitoring** (proactive issue detection)
   - Configure alerts for error rates >1%
   - Monitor query performance trends
   - Track Snowflake credit usage

5. **Rotate Secrets** (security best practice)
   - Add calendar reminder for 90-day key rotation
   - Document rotation process
   - Test rotation in staging first

---

## Quick Reference - Important Files

| File | Purpose |
|------|---------|
| `app/services/snowflake_service.py` | Snowflake connection service (Vercel-compatible) |
| `app/services/snowflake_service_v2.py` | New version (rename to replace old) |
| `scripts/prepare_private_key_for_vercel.sh` | Convert key to env var format |
| `scripts/validate_deployment.py` | Test deployed endpoints |
| `SNOWFLAKE_DEPLOYMENT_VALIDATION.md` | Full technical documentation |
| `DEPLOYMENT_CHECKLIST.md` | Detailed pre-deployment checklist |

---

## Getting Help

**If validation fails**:
1. Read error messages in `python scripts/validate_deployment.py` output
2. Check Vercel logs: `vercel logs`
3. Review: SNOWFLAKE_DEPLOYMENT_VALIDATION.md Troubleshooting section
4. Test locally first: `vercel dev`

**Common Documentation**:
- Vercel environment variables: https://vercel.com/docs/concepts/projects/environment-variables
- Snowflake key-pair auth: https://docs.snowflake.com/en/user-guide/key-pair-auth.html
- Vercel serverless functions: https://vercel.com/docs/concepts/functions/serverless-functions

---

## Summary

```bash
# Complete deployment in 4 commands:

# 1. Update service
mv app/services/snowflake_service_v2.py app/services/snowflake_service.py

# 2. Prepare key
./scripts/prepare_private_key_for_vercel.sh ../rsa_key.p8

# 3. Configure Vercel (via dashboard or CLI)
vercel env add SNOWFLAKE_PRIVATE_KEY

# 4. Deploy
vercel --prod

# 5. Validate
python scripts/validate_deployment.py --url https://your-domain.vercel.app
```

**Time to production**: ~30 minutes ⚡

---

✅ **Deployment Complete**: Your Snowflake-integrated backend is now live on Vercel serverless!
