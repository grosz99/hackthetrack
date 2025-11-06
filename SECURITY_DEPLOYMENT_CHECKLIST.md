# 🔐 Security & Deployment Checklist

**CRITICAL**: Follow this checklist BEFORE deploying to ensure all secrets are secure.

---

## ⚠️ SECURITY ISSUES FOUND & FIXED

### ✅ Fixed in Latest Commit
1. **Removed `.env` file from git** - Contained Snowflake credentials
2. **Removed `rsa_key_old.pub` from git** - Old public key
3. **Updated `.gitignore`** - Prevents future commits of sensitive files

### ⚠️ ACTION REQUIRED

**You should rotate the following credentials as a precaution** since they were in the git history:

```
SNOWFLAKE_ACCOUNT=EOEPNYL-PR46214
SNOWFLAKE_USER=hackthetrack_svc
```

Even though the private key was NOT committed, it's best practice to rotate credentials that were exposed.

---

## 🔐 Environment Variables Setup

### Railway (Backend) - All Required Variables

Go to: **Railway Dashboard → Your Project → Variables**

#### **Snowflake Configuration** (if using Snowflake)
```bash
SNOWFLAKE_ACCOUNT=your-account-id
SNOWFLAKE_USER=your-service-account-user
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKTHETRACK
SNOWFLAKE_SCHEMA=TELEMETRY
SNOWFLAKE_ROLE=ACCOUNTADMIN
USE_SNOWFLAKE=true

# For RSA key authentication (RECOMMENDED):
# Upload your rsa_key.p8 file to Railway's file storage
# Then set:
SNOWFLAKE_PRIVATE_KEY_PATH=/path/to/rsa_key.p8

# OR use password auth (NOT recommended for production):
# SNOWFLAKE_PASSWORD=your-secure-password
```

#### **Anthropic AI**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

#### **Application Settings**
```bash
ENVIRONMENT=production
DEBUG=false
```

### Vercel (Frontend) - Required Variables

Go to: **Vercel Dashboard → circuit-fit Project → Settings → Environment Variables**

```bash
# Must point to your Railway backend URL
VITE_API_URL=https://your-app-name.railway.app
```

**IMPORTANT**: Set this for ALL environments:
- ✅ Production
- ✅ Preview
- ✅ Development

---

## ✅ Security Verification Checklist

### Before Deploying

- [ ] **.env files NOT in git**
  ```bash
  git ls-files | grep '\.env$' | grep -v '\.example$'
  # Should return NOTHING
  ```

- [ ] **No RSA keys in git**
  ```bash
  git ls-files | grep -E '\.p8$|\.pem$|rsa_key'
  # Should return NOTHING
  ```

- [ ] **No API keys in code**
  ```bash
  rg 'sk-ant-api' --type py
  rg 'ANTHROPIC_API_KEY.*=' --type py | grep -v 'os.getenv'
  # Should only find os.getenv() calls, NOT hardcoded keys
  ```

- [ ] **No Snowflake passwords in code**
  ```bash
  rg 'SNOWFLAKE_PASSWORD.*=' --type py | grep -v 'os.getenv'
  # Should return NOTHING or only os.getenv() calls
  ```

- [ ] **.gitignore is comprehensive**
  ```bash
  cat .gitignore | grep -E '\.env|\.p8|\.pem|rsa_key'
  # Should show these patterns are ignored
  ```

### During Deployment

- [ ] **Railway environment variables set**
  - Go to Railway dashboard and verify all vars are configured
  - Test the backend health endpoint after deployment

- [ ] **Vercel environment variables set**
  - Verify VITE_API_URL points to Railway backend
  - Check all environments (Production, Preview, Development)

- [ ] **Secrets uploaded securely**
  - If using RSA keys, upload via Railway's secure file storage
  - NEVER paste private keys in environment variable fields

### After Deployment

- [ ] **Backend health check passing**
  ```bash
  curl https://your-railway-url.railway.app/api/health
  # Should return: {"status": "healthy", ...}
  ```

- [ ] **Frontend can reach backend**
  - Open browser console on frontend
  - Check Network tab for successful API calls
  - No CORS errors

- [ ] **No secrets in browser**
  - View page source - should NOT contain any API keys
  - Check Network responses - should NOT expose credentials

---

## 🚨 What NOT to Commit

### NEVER commit these to git:

```bash
# Environment files
.env
.env.local
.env.production
backend/.env
frontend/.env

# RSA private keys
rsa_key.p8
*.p8
*.pem
snowflake_key.*

# Database files
*.db
*.sqlite
*.sqlite3

# Credentials
*credential*
*secret*
*password*

# API keys (if in files)
anthropic_key.txt
api_keys.json
```

### ALWAYS use:
- ✅ Environment variables (via Railway/Vercel dashboard)
- ✅ `.env.example` files (with placeholder values)
- ✅ `os.getenv()` in Python code
- ✅ `import.meta.env.VITE_*` in Vite/React code

---

## 🔄 Credential Rotation Guide

If credentials were exposed (as they were in `.env` file):

### 1. Snowflake Credentials

```bash
# In Snowflake console:
# 1. Create new service account user
CREATE USER hackthetrack_svc_new LOGIN_NAME='hackthetrack_svc_new' ...;

# 2. Grant same permissions
GRANT ROLE ACCOUNTADMIN TO USER hackthetrack_svc_new;

# 3. Generate new RSA key pair locally
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key_new.p8 -nocrypt
openssl rsa -in rsa_key_new.p8 -pubout -out rsa_key_new.pub

# 4. Update Snowflake with new public key
ALTER USER hackthetrack_svc_new SET RSA_PUBLIC_KEY='<paste content of rsa_key_new.pub>';

# 5. Update Railway with new credentials
# 6. Test connection
# 7. Drop old user
DROP USER hackthetrack_svc;
```

### 2. Anthropic API Key

```bash
# 1. Go to https://console.anthropic.com/settings/keys
# 2. Create new API key
# 3. Update Railway environment variables
# 4. Revoke old API key
```

---

## 📋 Deployment Workflow

### Step 1: Verify Security
```bash
# Run security checks
git ls-files | grep -E '\.env$|\.p8$|\.pem$' | grep -v '\.example$'
# Should be empty

# Check for hardcoded secrets
rg 'sk-ant-api|SNOWFLAKE_PASSWORD' --type py | grep -v 'os.getenv'
# Should be empty or only show os.getenv() usage
```

### Step 2: Push to GitHub
```bash
git push origin master
```

### Step 3: Configure Railway
1. Go to https://railway.app/dashboard
2. Verify backend deployment triggered
3. Add all environment variables (see above)
4. Wait for deployment to complete
5. Test health endpoint

### Step 4: Configure Vercel
1. Go to https://vercel.com/dashboard
2. Find circuit-fit project
3. Settings → Environment Variables
4. Add `VITE_API_URL` with Railway URL
5. Deployment triggers automatically

### Step 5: Verify Production
```bash
# Test backend
curl https://your-railway-url.railway.app/api/health

# Test frontend
# Visit https://your-vercel-url.vercel.app
# Open DevTools → Network tab
# Verify API calls succeed
```

---

## 🎯 Current Status

### ✅ Completed
- [x] Removed `.env` from git tracking
- [x] Removed old RSA public key from git
- [x] Updated `.gitignore` to prevent future leaks
- [x] Removed large CSV files (>100MB)
- [x] Verified no private keys in git

### ⏳ Pending
- [ ] Rotate Snowflake credentials (recommended)
- [ ] Configure Railway environment variables
- [ ] Configure Vercel environment variables
- [ ] Upload RSA private key to Railway (if using Snowflake)
- [ ] Test backend deployment
- [ ] Test frontend deployment
- [ ] Verify end-to-end functionality

---

## 🆘 If You Accidentally Commit Secrets

### Immediate Actions:

1. **Remove from git tracking** (like we just did)
   ```bash
   git rm --cached path/to/secret/file
   git commit -m "security: remove secret file"
   git push origin master --force  # ⚠️ Only if nobody else has pulled!
   ```

2. **Rotate the exposed credentials** IMMEDIATELY
   - Generate new keys/passwords
   - Update deployment platforms
   - Revoke old credentials

3. **Clean git history** (if the secret was in previous commits)
   ```bash
   # This is complex - consider using BFG Repo-Cleaner
   # https://rtyley.github.io/bfg-repo-cleaner/
   ```

4. **Monitor for unauthorized access**
   - Check Snowflake query history
   - Check Anthropic API usage
   - Look for anomalous activity

---

## 📞 Security Contacts

- **Snowflake Support**: https://support.snowflake.com
- **Anthropic Support**: support@anthropic.com
- **Railway Support**: https://railway.app/help
- **Vercel Support**: https://vercel.com/support

---

**Remember**: Security is not optional. Always verify before deploying!

**Last Updated**: November 6, 2025
**Status**: Security issues fixed, credentials rotation recommended
