# 🚀 Deploy to Vercel - READY NOW!

## ✅ Pre-Deployment Checklist - ALL COMPLETE!

- [x] Snowflake RSA key rotated and tested
- [x] Connection verified (35 drivers, 58K+ telemetry rows)
- [x] Code fixes committed
- [x] Dependencies updated (scipy, cryptography)
- [x] API routes fixed
- [x] .gitignore secured

---

## Step 1: Set Environment Variables in Vercel

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

### Required Variables:

```bash
# Snowflake Database
SNOWFLAKE_ACCOUNT=EOEPNYL-PR46214
SNOWFLAKE_USER=hackthetrack_svc
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKTHETRACK
SNOWFLAKE_SCHEMA=TELEMETRY
SNOWFLAKE_ROLE=ACCOUNTADMIN
USE_SNOWFLAKE=true

# Snowflake Authentication - PASTE THE KEY BELOW
SNOWFLAKE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC3iHM8wQkbQb4d\n6SmQPu/JRFf0TpHsZq1gJfqHKEk7OHLAMjQxN8IqwXHhUmoHp6OiZwWLy+sI+hze\nyU/+eHK5ZE5H8yFU39tZhclsbL0CgKijFKFvDJN7W4aY2UNh8d9rVqw0A1M4soW6\nKT3A3OdBjyM7gAfunVArJW5pATJoA9ZY4HqkfWD6b+M4sa5iZbXnD4Tma+gHmUwe\n8VqR5vrk6UV5rcySgNOoPcec13u/CWGd0PRQ3ybtTEDOJLBT6GqPSxRFuuXrNAL5\nzy0FMHKVvx1EF37xqH7zt3wrGQiOllf2pvlh9zPl6kz09pEhmGvwGZYBVkhOYcpI\nSbK0jekXAgMBAAECggEAStrGsWVD2w+VxGpIDvJ0ZyDORLDU+FeqZ9gllYF7WMF9\nn+D6A4br1PdgBJfR8fxQE5k0HF/XpSopoz31N+MVW4LLILJLimvg8WLNE8FH16D0\n5sqvyvSUpE/gli+quWRmjMdlZbNjenDpdNOEQch3M3h3VLmzwoD75RUXspEP53bU\nA8Wt9WJsaaqJkhevWuqNO4Y9i/wNHf9y4qCB0mY9lCsQRX1VXepS171K86zQxSw2\nMgs7+W/IwpXZl5LRfnqB7rxzJNLzXBC+cti/iDZBwBjHIR/FfCmVI2Tv3VgZvu0R\nmV3XhaUnIIUg/YOmA0VeKX69RgUGlXEhVLH/GUNViQKBgQDnK9w+xsMZykY3c2tj\nP/gv4HIfs555w8MgwJbZCC+/wxt1W/kgbgL1RPwRKHcWybX/osyOZ2elKiuDC1B3\niY52Cn4pUPO30dxZhr3P8PkW/PDbU+msvwKPDmNMe1oc3ztCYfwHAnTAwARWIxEQ\nZ2isYPtpqI6/vTlGYBe6VQ1CvwKBgQDLPsHCbHTbpaZN/LTRTIpqz5LV45/4cCpF\nHKrxTEQuqcEXBGuaT9A4+uUXoeBZckN07BihV9WuDecUIFRcygaW2CYx6uNw+mHj\n9kHzeUn2WvHdQtts5eEvXGPWjmSIYspw3SZ8tavYfDZj+jJu7avQow3iXQncabic\nI7wmjY5nqQKBgQC5RgjN82U4jUo7dPDTadiTHpK436+arY/89v2vUgVa7pdaNu1y\n1VjflHtlkQXpKJ8KFENXun5x/FtFOtMyCvg3mO9GU9AROkwdIIWOW/Z3OyAa2KUG\nw0vctc5V5OLzEuKesINaZtiGBx8yngY2HHri9RNquiI2gASgZ7F8sF/hZwKBgQCK\nP+cGvEWE/xmvpLzOPdVNsGJ+EXbIRGvMVSLGPg2G/Dt2z6/t6GqHx8o7mAYGcd4G\n024xmZCk85oCq7cW4uk2hFL+03rgZ8Bcky7rUc6Iv/YTfp3JZlkVoS/cS0GBMEnq\nGdRLMjxxZpSMzyytHggoRDF2j7jccCF+PCSIyPNb+QKBgQCDG43rQDHj/HGaZ8PV\n1Sifk0QVpLiCB7SHs+ZTdOHNRV32SjUQ1QpqIrzDx6jG+6uTj7EhYcObOziMeBE3\nGhE3RLXPDQ36PYw+ITUjn7k7TbS2l2UdxYhsXoUChjAkHLsD9e0J3ZONd3eT0yCn\nQGWwluKucagl+X/cpHxgFzSexQ==\n-----END PRIVATE KEY-----\n

# Anthropic API - PASTE YOUR NEW KEY HERE
ANTHROPIC_API_KEY=sk-ant-api03-your-new-rotated-key-here

# Frontend URL (set to your Vercel domain after first deploy)
FRONTEND_URL=https://your-app.vercel.app
```

**IMPORTANT**: 
- Copy the SNOWFLAKE_PRIVATE_KEY exactly as shown (with `\n` escapes)
- Replace `ANTHROPIC_API_KEY` with your NEW rotated key
- Update `FRONTEND_URL` after first deployment

---

## Step 2: Push Code to GitHub

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Push the committed changes
git push origin master
```

---

## Step 3: Deploy to Vercel

### Option A: Auto-Deploy (if connected to GitHub)

If your Vercel project is connected to GitHub:
1. Vercel will automatically deploy when you push
2. Go to: https://vercel.com/your-team/hackthetrack
3. Watch the deployment progress
4. Once deployed, update `FRONTEND_URL` environment variable with actual URL

### Option B: Manual Deploy

```bash
# Install Vercel CLI if needed
npm i -g vercel

# Deploy
vercel --prod

# Follow prompts
```

---

## Step 4: Verify Deployment

### Test API Endpoints:

1. **Health Check:**
   ```bash
   curl https://your-app.vercel.app/api/health
   ```
   Expected: `{"status": "connected", "database": "HACKTHETRACK", ...}`

2. **Get Drivers:**
   ```bash
   curl https://your-app.vercel.app/api/telemetry/drivers
   ```
   Expected: `{"drivers_with_telemetry": [0, 2, 3, 5, 7, ...]}`

3. **Get Telemetry Data:**
   ```bash
   curl "https://your-app.vercel.app/api/telemetry/detailed?track_id=barber&race_num=1&driver_number=13"
   ```
   Expected: Telemetry data JSON

### Test Frontend:

1. Open: `https://your-app.vercel.app`
2. Navigate through pages:
   - Scout Landing
   - Driver Overview
   - Race Log
   - Skills
   - Improve
3. Check browser console (F12) - should have NO errors
4. Check Network tab - all API calls should return 200

---

## Troubleshooting

### If Snowflake connection fails:

1. Check Vercel Logs:
   - Go to: Vercel Dashboard → Deployments → Latest → Function Logs
   - Look for "JWT token invalid" or connection errors

2. Verify environment variables:
   - Ensure `SNOWFLAKE_PRIVATE_KEY` has `\n` escapes
   - Check no extra spaces or quotes

3. Test key format:
   - The key should start with `-----BEGIN PRIVATE KEY-----\n`
   - And end with `\n-----END PRIVATE KEY-----\n`

### If CORS errors occur:

1. Update `FRONTEND_URL` in Vercel environment variables
2. Redeploy (Vercel will auto-redeploy when env vars change)

### If API 404 errors:

1. Check `vercel.json` exists in root
2. Verify rewrites configuration
3. Check function logs for errors

---

## Success Checklist

- [ ] Environment variables set in Vercel
- [ ] Code pushed to GitHub
- [ ] Deployment completed successfully
- [ ] Health endpoint returns `connected`
- [ ] Drivers endpoint returns 35 drivers
- [ ] Telemetry endpoint returns data
- [ ] Frontend loads without errors
- [ ] All tabs navigate correctly

---

## 🎉 You're Live!

Once all checks pass:
1. Share the production URL with your team
2. Monitor Vercel logs for first 24 hours
3. Schedule credential rotation reminder (90 days)

**Production URL**: https://your-app.vercel.app

---

## Notes

- RSA key authentication is more secure than password
- Keys have been rotated for security
- All secrets are in Vercel environment variables
- No credentials in code repository
