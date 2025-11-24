# HackTheTrack Automated Monitoring - Setup Complete ✅

**Date**: 2025-11-23
**Status**: ✅ Ready to Deploy

---

## 🎯 What Was Built

An automated monitoring system that:
- **Screenshots every page** of your Netlify app every 6 hours
- **Validates data is present** on each page
- **Sends alerts** when pages fail (Email/Slack)
- **Creates GitHub issues** automatically when monitoring fails
- **Stores artifacts** (screenshots for 7 days, reports for 30 days)

## 📊 Monitored Pages (8 total)

1. **Rankings** - Main landing page with driver table
2. **Overview** - Driver performance dashboard
3. **Race Log** - Historical race data
4. **Skills** - Skill breakdown and radar charts
5. **Driver Development** - Improvement recommendations
6. **Telemetry Comparison** - Telemetry charts
7. **Strategy Chat** - AI chat interface
8. **Track Intelligence** - Track analysis

## ⏰ Monitoring Schedule

Runs automatically every 6 hours:
- **12:00 AM** (00:00 UTC)
- **6:00 AM** (06:00 UTC)
- **12:00 PM** (12:00 UTC)
- **6:00 PM** (18:00 UTC)

## 🚀 Quick Start

### Option 1: GitHub Actions (Automatic - Recommended)

1. **Push this code to GitHub:**
   ```bash
   git add .
   git commit -m "feat(monitoring): add automated 6-hour monitoring system"
   git push origin master
   ```

2. **Enable GitHub Actions** (if not already enabled):
   - Go to your repo → Settings → Actions → Allow all actions

3. **That's it!** Monitoring will run automatically every 6 hours

4. **View Results:**
   - Go to `Actions` tab in your GitHub repo
   - Click on latest "Automated Site Monitoring" workflow
   - Download artifacts to see screenshots

### Option 2: Manual Testing (Local)

```bash
cd monitoring
npm install
npx playwright install chromium
node test-monitor.js    # Quick test
node monitor.js         # Full monitoring run
```

## 📧 Optional: Setup Alerts

### Email Alerts

Add these as GitHub Secrets (Settings → Secrets and variables → Actions):

```
ALERT_EMAIL_ENABLED = true
ALERT_EMAIL_TO = your-email@example.com
ALERT_EMAIL_FROM = monitoring@hackthetrack.com
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 587
SMTP_USER = your-email@gmail.com
SMTP_PASS = your-app-password
```

**Gmail Setup:**
1. Enable 2FA on Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use app password as `SMTP_PASS`

### Slack Alerts

Add these as GitHub Secrets:

```
ALERT_SLACK_ENABLED = true
SLACK_WEBHOOK_URL = https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## 🔍 How It Works

Every 6 hours, GitHub Actions:
1. ✅ Spins up Ubuntu VM
2. ✅ Installs Node.js and Playwright
3. ✅ Launches headless Chrome browser
4. ✅ Visits each of your 8 pages
5. ✅ Takes screenshot of each page
6. ✅ Validates that data is present
7. ✅ Generates JSON + HTML reports
8. ✅ Uploads screenshots as artifacts
9. ✅ Sends alerts if any failures detected
10. ✅ Creates GitHub issue if monitoring fails

## 📁 What's Included

```
monitoring/
├── package.json              # Dependencies
├── config.js                 # Page config and validation rules
├── monitor.js                # Main monitoring script
├── alerts.js                 # Email/Slack alert system
├── report-generator.js       # HTML/JSON report generation
├── test-monitor.js           # Quick test script
├── .env.example              # Example environment variables
├── .gitignore                # Ignore generated files
└── README.md                 # Detailed documentation

.github/workflows/
└── monitoring.yml            # GitHub Actions workflow (6-hour schedule)
```

## 🎯 Benefits

### For the Competition

- **Prevents downtime** - You'll know immediately if the app goes down
- **Data validation** - Ensures critical data is loading on every page
- **Evidence of uptime** - Screenshots prove your app was working
- **No manual checking** - Automated every 6 hours

### Peace of Mind

- **Sleep soundly** - Monitoring runs while you sleep
- **Automatic alerts** - Get notified only when there's a problem
- **Historical record** - 30 days of monitoring reports
- **Easy debugging** - Screenshots show exactly what failed

## 📊 What You'll See

### GitHub Actions Artifacts

After each run, you can download:
- **screenshots-[run-number].zip** - PNG files of every page
- **reports-[run-number].zip** - JSON monitoring reports

### Example Report

```json
{
  "timestamp": "2025-11-23T18:00:00.000Z",
  "summary": {
    "total": 8,
    "passed": 8,
    "failed": 0,
    "duration": "42.15s"
  },
  "results": [
    {
      "name": "Rankings",
      "url": "/rankings",
      "success": true,
      "screenshot": "Rankings-1700755200000.png",
      "validations": [
        {
          "description": "Driver rows should be present",
          "expected": ">= 10",
          "actual": 31,
          "passed": true
        }
      ]
    }
  ]
}
```

## 🐛 Troubleshooting

### No Actions Running?

- Check: Settings → Actions → Allow all actions
- Check: `.github/workflows/monitoring.yml` exists
- Trigger manually: Actions tab → Automated Site Monitoring → Run workflow

### Monitoring Failing?

1. Check the screenshots in artifacts
2. Review the JSON report for specific errors
3. Verify your Netlify site is accessible
4. Check API is responding: https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/health

### No Alerts Received?

- Verify GitHub Secrets are set correctly
- Check alert enable flags are set to `'true'` (as strings)
- Test SMTP credentials locally first

## ✅ Testing Checklist

- [x] ✅ Monitoring system built
- [x] ✅ 8 pages configured
- [x] ✅ Data validation rules set
- [x] ✅ GitHub Actions workflow created
- [x] ✅ Alert system implemented
- [x] ✅ Tested locally - all working
- [x] ✅ Documentation complete

## 🔄 Next Steps

1. **Commit and push** this code to GitHub
2. **Wait for first run** (or trigger manually)
3. **Check Actions tab** to see results
4. **Optional:** Set up email/Slack alerts

## 📞 Support

- **Full Documentation**: `monitoring/README.md`
- **Test Script**: `cd monitoring && node test-monitor.js`
- **Manual Run**: `cd monitoring && node monitor.js`

---

**Status**: ✅ **READY FOR DEPLOYMENT**

Your monitoring system is configured and tested. Just push to GitHub and it will start monitoring every 6 hours automatically!

**No more manual checking required.** 🎉
