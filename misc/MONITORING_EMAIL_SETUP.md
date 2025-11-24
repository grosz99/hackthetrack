# Email Alert Setup for Monitoring System

## ✅ What's Already Configured

The monitoring system is set to send alerts to **justin.m.grosz@gmail.com** whenever a page fails.

## 🔧 Required: Set Up GitHub Secrets for Email

To enable email alerts, you need to add your Gmail app password as a GitHub secret.

### Step 1: Generate Gmail App Password

1. **Go to your Google Account**: https://myaccount.google.com/
2. **Enable 2-Factor Authentication** (if not already enabled):
   - Security → 2-Step Verification → Turn on
3. **Create an App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other (Custom name)" → Enter "HackTheTrack Monitoring"
   - Click "Generate"
   - **Copy the 16-character password** (you won't see it again!)

### Step 2: Add Secrets to GitHub

1. **Go to your GitHub repository**: https://github.com/grosz99/hackthetrack
2. **Navigate to**: Settings → Secrets and variables → Actions
3. **Click**: "New repository secret"
4. **Add these two secrets**:

   **Secret 1:**
   - Name: `SMTP_USER`
   - Value: `justin.m.grosz@gmail.com`

   **Secret 2:**
   - Name: `SMTP_PASS`
   - Value: `[paste the 16-character app password from Step 1]`

### Step 3: Verify It Works

1. Go to your repo's **Actions** tab
2. Click **"Automated Site Monitoring"** workflow
3. Click **"Run workflow"** → **"Run workflow"** (manual trigger)
4. Wait for it to complete
5. Check your email at **justin.m.grosz@gmail.com**

## 📧 What Emails You'll Receive

### When Pages Are Down

You'll get an email with:
- **Subject**: `🚨 HackTheTrack Monitoring Alert: X Page(s) Failed`
- **Content**:
  - Which pages failed
  - What errors occurred
  - Validation failures
  - Links to screenshots

### Email Format

```
HackTheTrack Monitoring Report
Generated: 2025-11-23T18:00:00.000Z
Duration: 42.5s

Status: ❌ FAILURES DETECTED

Summary
- Total Pages: 5
- Passed: 3
- Failed: 2

Failed Pages
- Driver Development - Driver 72 (/driver/72/driver-development)
  Errors: HTTP 404: Not Found

All Results
✅ Home - Rankings
✅ Overview - Driver 72
❌ Race Log - Driver 72
✅ Skills - Driver 72
❌ Driver Development - Driver 72
```

## 🎯 Pages Being Monitored

Every 6 hours, these 5 pages will be checked:

1. **https://gibbs-ai.netlify.app/** (Home - Rankings)
2. **https://gibbs-ai.netlify.app/driver/72/overview**
3. **https://gibbs-ai.netlify.app/driver/72/race-log**
4. **https://gibbs-ai.netlify.app/driver/72/skills**
5. **https://gibbs-ai.netlify.app/driver/72/driver-development**

## ⏰ Monitoring Schedule

Automated checks run at:
- **12:00 AM** (00:00 UTC)
- **6:00 AM** (06:00 UTC)
- **12:00 PM** (12:00 UTC)
- **6:00 PM** (18:00 UTC)

## 🔍 Troubleshooting

### Not Receiving Emails?

1. **Check spam folder** - Gmail might filter automated emails
2. **Verify secrets are set**:
   - GitHub repo → Settings → Secrets and variables → Actions
   - Should see `SMTP_USER` and `SMTP_PASS` listed
3. **Check workflow logs**:
   - Actions tab → Click on a completed run
   - Look for email sending errors
4. **Regenerate app password** if it's not working

### Test Email Locally

You can test email sending locally:

```bash
cd monitoring

# Create .env file
cat > .env << 'EOF'
NETLIFY_URL=https://gibbs-ai.netlify.app
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_TO=justin.m.grosz@gmail.com
ALERT_EMAIL_FROM=monitoring@hackthetrack.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=justin.m.grosz@gmail.com
SMTP_PASS=your-16-char-app-password-here
EOF

# Run monitoring
node monitor.js
```

## ✅ Current Status

- ✅ YAML syntax fixed
- ✅ Email alerts enabled
- ✅ Recipient set to justin.m.grosz@gmail.com
- ✅ 5 pages configured for monitoring
- ✅ 6-hour schedule active
- ⏳ **Waiting for**: GitHub secrets (SMTP_USER and SMTP_PASS)

## 🚀 Once Secrets Are Added

After you add the GitHub secrets:
1. Email alerts will work automatically
2. No code changes needed
3. You'll get notified every time monitoring runs and finds issues
4. Screenshots and reports will still be saved in GitHub Actions artifacts

---

**Next Step**: Add the two GitHub secrets (SMTP_USER and SMTP_PASS) and you're done! 🎉
