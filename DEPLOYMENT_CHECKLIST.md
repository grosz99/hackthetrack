# Pre-Deployment Checklist

Use this checklist before every production deployment to ensure backend readiness.

## ⚡ Quick Validation (2 minutes)

```bash
# 1. Install test dependencies (first time only)
pip install -r requirements-dev.txt

# 2. Run pre-deployment check
python scripts/pre_deployment_check.py

# 3. Check exit code
echo $?  # Should be 0 (success)
```

**Result**:
- ✅ Exit code 0 = **SAFE TO DEPLOY**
- ❌ Exit code 1 = **FIX ISSUES FIRST**

---

## 📋 Manual Checklist

Use this if automated validation fails or for additional verification:

### 1. Environment Variables ✓

- [ ] `.env` file exists and is configured
- [ ] `ANTHROPIC_API_KEY` set (starts with `sk-ant-`)
- [ ] `USE_SNOWFLAKE=true` for production
- [ ] `SNOWFLAKE_ACCOUNT` set (format: `account.region`)
- [ ] `SNOWFLAKE_USER` set (not placeholder)
- [ ] `SNOWFLAKE_PASSWORD` set (not placeholder)
- [ ] `SNOWFLAKE_WAREHOUSE` set (default: `COMPUTE_WH`)
- [ ] `SNOWFLAKE_DATABASE` set (default: `HACKTHETRACK`)
- [ ] `SNOWFLAKE_SCHEMA` set (default: `TELEMETRY`)
- [ ] No placeholder values remain (check for "your-account", "your_password", etc.)

**Verify**:
```bash
grep -E "(SNOWFLAKE_|ANTHROPIC_)" .env | grep -v "your-"
```

### 2. Snowflake Connectivity ✓

- [ ] Snowflake connection establishes successfully
- [ ] Database `HACKTHETRACK` exists
- [ ] Schema `TELEMETRY` exists
- [ ] Table `TELEMETRY_DATA` exists
- [ ] Table has data (>0 rows)
- [ ] At least one driver has telemetry data
- [ ] Queries execute in <5 seconds

**Verify**:
```bash
pytest tests/test_deployment_readiness.py::TestSnowflakeConnectivity -v
```

### 3. Dependencies ✓

- [ ] `requirements.txt` exists
- [ ] All imports have corresponding packages in requirements.txt
- [ ] `snowflake-connector-python` version is pinned
- [ ] `fastapi`, `uvicorn`, `anthropic`, `pandas` present

**Verify**:
```bash
pytest tests/test_deployment_readiness.py::TestDependencyCompleteness -v
```

### 4. Security ✓

- [ ] No hardcoded credentials in code
- [ ] `.env` file in `.gitignore`
- [ ] `.env` not committed to git
- [ ] All secrets use environment variables
- [ ] SQL queries use parameterization (no string interpolation)

**Verify**:
```bash
pytest tests/test_deployment_readiness.py::TestSecurityCompliance -v
git ls-files | grep "\.env$"  # Should be empty
```

### 5. API Endpoints ✓

- [ ] `/api/health` endpoint responds
- [ ] `/api/telemetry/drivers` endpoint exists
- [ ] `/api/telemetry/coaching` endpoint exists
- [ ] Endpoints return valid JSON
- [ ] Error responses are properly formatted
- [ ] Snowflake fallback to local CSV works

**Verify**:
```bash
pytest tests/test_telemetry_endpoints.py -v
```

### 6. Data Validation ✓

- [ ] Telemetry data uploaded to Snowflake
- [ ] Driver list returns >0 drivers
- [ ] Driver numbers are in range 0-99
- [ ] Telemetry data has required columns (vehicle_number, lap, speed, etc.)
- [ ] No null/missing critical data

**Verify**:
```bash
pytest tests/test_snowflake_integration.py::TestDriversWithTelemetry::test_returns_real_drivers -v
```

### 7. Performance ✓

- [ ] Snowflake connection <2 seconds
- [ ] Driver list query <5 seconds
- [ ] Telemetry data query <5 seconds
- [ ] API endpoints respond <1 second
- [ ] No connection leaks (connections properly closed)

**Verify**:
```bash
pytest tests/test_snowflake_integration.py -k "performance" -v
```

### 8. Vercel Configuration ✓ (if deploying to Vercel)

- [ ] Environment variables set in Vercel dashboard
- [ ] `vercel.json` exists and is valid JSON (if present)
- [ ] Production URL configured
- [ ] CORS origins include production URL

**Verify in Vercel Dashboard**:
1. Go to Project Settings → Environment Variables
2. Verify all required variables are set for "Production"
3. Check values match local `.env` (except credentials may differ)

**Required in Vercel**:
- `ANTHROPIC_API_KEY`
- `USE_SNOWFLAKE=true`
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`

---

## 🚀 Deployment Steps

### 1. Pre-Deployment Validation

```bash
# Full validation with integration tests
python scripts/pre_deployment_check.py

# Should output:
# ✓ ALL CHECKS PASSED
# System is ready for deployment!
# Exit code: 0
```

### 2. Deploy to Vercel

```bash
# Using Vercel CLI
vercel --prod

# Or push to main branch (if auto-deploy configured)
git push origin main
```

### 3. Post-Deployment Verification

```bash
# Test health endpoint
curl https://your-domain.vercel.app/api/health

# Expected response:
# {"status":"healthy","tracks_loaded":15,"drivers_loaded":25}

# Test telemetry drivers endpoint
curl https://your-domain.vercel.app/api/telemetry/drivers

# Expected response:
# {"drivers_with_telemetry":[0,2,3,5,7,...],"count":25,"source":"snowflake"}
```

### 4. Monitor Deployment

- [ ] Check Vercel deployment logs for errors
- [ ] Verify frontend can connect to backend
- [ ] Test driver selection in UI (should show drivers)
- [ ] Test telemetry coaching feature
- [ ] Check error rates in monitoring dashboard

---

## ❌ Common Issues and Fixes

### Issue: "Missing Snowflake credentials"

**Fix**:
```bash
# Copy example and fill in real values
cp .env.example .env
nano .env  # Edit with real credentials
```

### Issue: "Table TELEMETRY_DATA not found"

**Fix**:
```bash
# Upload telemetry data to Snowflake
python upload_to_snowflake.py

# Verify in Snowflake console
```

### Issue: "No drivers with telemetry data"

**Fix**:
1. Verify CSV files exist in `data/telemetry/`
2. Upload CSVs to Snowflake: `python upload_to_snowflake.py`
3. Check data in Snowflake console: `SELECT COUNT(DISTINCT vehicle_number) FROM telemetry_data;`

### Issue: "Connection timeout"

**Fix**:
1. Check network connectivity: `ping account.snowflakecomputing.com`
2. Verify Snowflake account is not suspended
3. Check IP whitelisting (if applicable)
4. Test with SnowSQL CLI: `snowsql -a account -u user`

### Issue: "Tests fail with real credentials"

**Fix**:
1. Verify credentials in Snowflake console
2. Check user has required permissions: `USAGE`, `SELECT`
3. Ensure warehouse is running
4. Test manually: `pytest tests/test_snowflake_integration.py::TestSnowflakeConnection::test_connection_succeeds_with_valid_credentials -v -s`

### Issue: "Exit code 1 from pre_deployment_check.py"

**Fix**:
1. Review output for specific failures
2. Fix each failing check
3. Re-run validation
4. Repeat until exit code is 0

---

## 🎯 Go/No-Go Decision

### ✅ SAFE TO DEPLOY if:

- Pre-deployment check exits with code 0
- All manual checklist items checked
- Snowflake connection works
- Telemetry data present (>0 drivers)
- No security issues
- API endpoints respond correctly

### ❌ DO NOT DEPLOY if:

- Pre-deployment check exits with code 1
- Any manual checklist item fails
- Snowflake connection fails
- No telemetry data (would cause "0 drivers" issue)
- Security issues detected
- API endpoints not functional

---

## 📊 Success Metrics

After deployment, monitor these metrics:

- **Driver Count**: Should match Snowflake data (>0)
- **API Response Time**: <1 second for most endpoints
- **Error Rate**: <1% of requests
- **Snowflake Query Time**: <5 seconds average
- **Connection Failures**: 0 (with fallback to local)

---

## 🔄 Regular Maintenance

### Weekly

- [ ] Run full validation: `python scripts/pre_deployment_check.py`
- [ ] Check Snowflake data freshness
- [ ] Review error logs for patterns

### Before Each Deployment

- [ ] Run pre-deployment check (required)
- [ ] Update telemetry data if needed
- [ ] Verify environment variables unchanged
- [ ] Test on staging environment (if available)

### After Each Deployment

- [ ] Run post-deployment verification
- [ ] Monitor for 15 minutes
- [ ] Check user reports for issues
- [ ] Update deployment log

---

## 📞 Support

If validation fails:

1. **Check test output**: Shows specific failures and error messages
2. **Review documentation**: `DEPLOYMENT_VALIDATION.md`
3. **Run specific tests**: `pytest tests/test_<category>.py -v`
4. **Check logs**: Backend logs, Vercel logs, Snowflake query history
5. **Verify manually**: Test endpoints with curl, check Snowflake console

---

## 🎓 Quick Reference

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run all validations
python scripts/pre_deployment_check.py

# Run specific test category
pytest tests/test_deployment_readiness.py -v
pytest tests/test_snowflake_integration.py -v
pytest tests/test_telemetry_endpoints.py -v

# Skip integration tests (faster)
python scripts/pre_deployment_check.py --skip-integration
pytest tests/ -m "not integration" -v

# Debug specific test
pytest tests/test_<file>.py::<TestClass>::<test_method> -v -s

# Check exit code
python scripts/pre_deployment_check.py && echo "SAFE TO DEPLOY" || echo "FIX ISSUES FIRST"
```

---

**Remember: Zero tolerance for backend fragility. If validation fails, fix before deploying.**

**Exit code 0 = ✅ Deploy**
**Exit code 1 = ❌ Fix issues**
