# 🔐 Security Credential Rotation Guide

**CRITICAL: Follow these steps immediately before deploying to Vercel**

## ⚠️ Exposed Credentials Found

The following credentials were found in your repository and MUST be rotated:

1. **Anthropic API Key** (in `.env`)
2. **Snowflake Password** (in `.env`)
3. **RSA Private Keys** (in parent directory)

---

## Step 1: Rotate Anthropic API Key

### Generate New Key:
1. Go to: https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Name it: `hackthetrack-production-2025`
4. Copy the new key (starts with `sk-ant-api03-...`)
5. **SAVE IT SECURELY** - you'll need it for Vercel

### Revoke Old Key:
1. Find the old key in the console: `sk-ant-api03-vVReMtoVURETsieNCAbfxb6o...`
2. Click "Revoke" next to it
3. Confirm revocation

### Update Vercel:
1. Go to: https://vercel.com/your-team/hackthetrack/settings/environment-variables
2. Find `ANTHROPIC_API_KEY`
3. Click "Edit" → Paste new key → Save

---

## Step 2: Rotate Snowflake Password

### Option A: Generate New Password (Recommended)

1. **Log into Snowflake**:
   - URL: https://app.snowflake.com/EOEPNYL/PR46214
   - User: Your admin account

2. **Reset Service Account Password**:
   ```sql
   USE ROLE ACCOUNTADMIN;
   ALTER USER hackthetrack_svc SET PASSWORD = '<NEW_SECURE_PASSWORD>';

   -- Example of strong password:
   -- HackTrack2025!Prod#Secure$v2
   ```

3. **Test New Password**:
   ```sql
   -- Log out and log back in with hackthetrack_svc user
   ```

### Option B: Switch to Key-Pair Auth (Most Secure)

**This is RECOMMENDED for production** - eliminates password entirely.

1. **Generate New RSA Key Pair**:
   ```bash
   cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

   # Generate private key (encrypted)
   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key_new.p8 -nocrypt

   # Generate public key
   openssl rsa -in rsa_key_new.p8 -pubout -out rsa_key_new.pub
   ```

2. **Get Public Key for Snowflake**:
   ```bash
   # Remove header/footer and make single line
   grep -v "BEGIN PUBLIC" rsa_key_new.pub | grep -v "END PUBLIC" | tr -d '\n'
   ```

3. **Set Public Key in Snowflake**:
   ```sql
   USE ROLE ACCOUNTADMIN;
   ALTER USER hackthetrack_svc SET RSA_PUBLIC_KEY='<PASTE_PUBLIC_KEY_HERE>';

   -- Verify it was set
   DESC USER hackthetrack_svc;
   ```

4. **Prepare Private Key for Vercel**:
   ```bash
   # Convert private key to single line with \n
   cat rsa_key_new.p8 | sed 's/$/\\n/' | tr -d '\n'
   ```

5. **Update Vercel Environment Variable**:
   - Go to Vercel → Settings → Environment Variables
   - Find or create `SNOWFLAKE_PRIVATE_KEY`
   - Paste the converted key (with `\n` escapes)
   - Remove `SNOWFLAKE_PASSWORD` variable (no longer needed)

6. **Delete Old Keys**:
   ```bash
   # After confirming new keys work
   rm rsa_key.p8 rsa_key.pub
   mv rsa_key_new.p8 rsa_key.p8
   mv rsa_key_new.pub rsa_key.pub
   ```

---

## Step 3: Update Vercel Environment Variables

### Required Environment Variables:

**Go to**: Vercel → Your Project → Settings → Environment Variables

#### Snowflake Configuration:
```
SNOWFLAKE_ACCOUNT=EOEPNYL-PR46214
SNOWFLAKE_USER=hackthetrack_svc
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKTHETRACK
SNOWFLAKE_SCHEMA=TELEMETRY
SNOWFLAKE_ROLE=ACCOUNTADMIN
USE_SNOWFLAKE=true
```

#### Choose ONE authentication method:

**Option A: Password Auth**
```
SNOWFLAKE_PASSWORD=<YOUR_NEW_ROTATED_PASSWORD>
```

**Option B: Key-Pair Auth (Recommended)**
```
SNOWFLAKE_PRIVATE_KEY=<PASTE_PRIVATE_KEY_WITH_\n_ESCAPED>
```

#### Anthropic API:
```
ANTHROPIC_API_KEY=<YOUR_NEW_ROTATED_KEY>
```

#### Frontend URL:
```
FRONTEND_URL=https://your-production-domain.vercel.app
```

#### Optional Performance Settings:
```
SNOWFLAKE_LOGIN_TIMEOUT=5
SNOWFLAKE_NETWORK_TIMEOUT=15
SNOWFLAKE_MAX_RETRIES=2
```

---

## Step 4: Clean Up Local Files

### Remove Secrets from Local .env:

1. **Backup important non-secret config**:
   ```bash
   # Review backend/.env for any non-secret settings
   cat backend/.env | grep -v "PASSWORD\|API_KEY\|PRIVATE_KEY"
   ```

2. **Delete exposed .env file**:
   ```bash
   cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend
   rm .env
   ```

3. **Create new .env from template**:
   ```bash
   cp .env.example .env
   # Edit .env and add your NEW credentials (local dev only)
   ```

### Secure RSA Keys:

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Ensure proper permissions (owner read-only)
chmod 600 rsa_key.p8
chmod 644 rsa_key.pub

# Verify they're in .gitignore
cat .gitignore | grep rsa_key
```

---

## Step 5: Verify Security

### Check Git Status:
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Should NOT show .env or rsa_key files
git status

# Verify .gitignore is working
git check-ignore -v .env
git check-ignore -v rsa_key.p8
git check-ignore -v rsa_key.pub
```

### Test Snowflake Connection Locally:
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend

# Test with new credentials
python -c "
from app.services.snowflake_service_v2 import snowflake_service
status = snowflake_service.check_connection()
print(status)
"
```

---

## Step 6: Commit Security Improvements

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Stage security improvements
git add .gitignore backend/.gitignore

# Commit with clear message
git commit -m "fix(security): enhance .gitignore to prevent credential exposure

- Add .env to root .gitignore
- Expand backend/.gitignore with comprehensive patterns
- Prevent RSA keys, Python cache, and database files from being committed

SECURITY NOTE: No credentials were committed. All secrets managed via Vercel environment variables."

# Push to repository
git push origin master
```

---

## 🔒 Security Best Practices Going Forward

### DO:
- ✅ Use Vercel environment variables for ALL secrets
- ✅ Use key-pair authentication instead of passwords
- ✅ Rotate credentials every 90 days
- ✅ Use different credentials for dev/staging/production
- ✅ Enable MFA on all admin accounts
- ✅ Review `.env.example` files before committing

### DON'T:
- ❌ NEVER commit `.env` files
- ❌ NEVER commit private keys (`.p8`, `.pem`)
- ❌ NEVER hardcode credentials in source code
- ❌ NEVER share credentials via Slack/email
- ❌ NEVER use production credentials in development
- ❌ NEVER commit to git before checking `git status`

---

## 📞 Emergency: Credentials Exposed?

If you accidentally commit credentials:

1. **IMMEDIATE**: Rotate ALL exposed credentials
2. **Remove from git history** (if public repo):
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   git push origin --force --all
   ```
3. **Contact security team** if customer data was exposed
4. **Update incident log** with what was exposed and remediation steps

---

## ✅ Checklist: Pre-Deployment Security

- [ ] Anthropic API key rotated and old key revoked
- [ ] Snowflake password rotated OR key-pair auth configured
- [ ] New credentials set in Vercel environment variables
- [ ] Old credentials removed from local `.env` files
- [ ] `.gitignore` updated to prevent future exposure
- [ ] Git status shows NO `.env` or key files
- [ ] Snowflake connection tested with new credentials
- [ ] Security improvements committed to git
- [ ] Team notified of credential rotation

---

**After completing all steps, you're ready for secure deployment! 🚀**
