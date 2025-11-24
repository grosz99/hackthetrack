# HackTheTrack Monitoring System

Automated monitoring system that takes screenshots and validates data on all pages every 6 hours to ensure the application is running properly and prevent downtime during the competition.

## Features

- **📸 Automated Screenshots**: Captures full-page screenshots of all key pages
- **✅ Data Validation**: Verifies that critical data and UI elements are present
- **🔔 Smart Alerts**: Sends notifications via Email or Slack when issues are detected
- **📊 Detailed Reports**: Generates HTML and JSON reports for each monitoring run
- **⏰ Scheduled Runs**: Automatically runs every 6 hours via GitHub Actions
- **🗂️ Artifact Storage**: Keeps screenshots for 7 days and reports for 30 days
- **🐛 Auto Issue Creation**: Creates GitHub issues when monitoring fails

## Monitored Pages

The system monitors all critical pages of the application:

1. **Rankings** - Main landing page with driver rankings table
2. **Overview** - Driver performance dashboard
3. **Race Log** - Historical race data
4. **Skills** - Skill breakdown with radar charts
5. **Driver Development** - Improvement recommendations
6. **Telemetry Comparison** - Telemetry charts and analysis
7. **Strategy Chat** - AI chat interface
8. **Track Intelligence** - Track analysis and insights

## How It Works

### Automated Monitoring (GitHub Actions)

The monitoring runs automatically every 6 hours:
- 12:00 AM
- 6:00 AM
- 12:00 PM
- 6:00 PM

Each run:
1. Launches a headless browser
2. Visits each page
3. Waits for content to load
4. Takes a screenshot
5. Validates that data is present
6. Generates a report
7. Sends alerts if failures detected
8. Uploads artifacts to GitHub

### Manual Monitoring (Local)

You can also run monitoring manually:

\`\`\`bash
cd monitoring
npm install
npx playwright install chromium
node monitor.js
\`\`\`

## Setup Instructions

### 1. Set Your Netlify URL

Update `.github/workflows/monitoring.yml` with your actual Netlify URL, or set it as a GitHub secret:

\`\`\`bash
# In your GitHub repo: Settings → Secrets and variables → Actions
NETLIFY_URL = https://your-app.netlify.app
\`\`\`

### 2. Configure Alerts (Optional)

#### Email Alerts

Set these GitHub secrets to enable email alerts:

\`\`\`
ALERT_EMAIL_ENABLED = true
ALERT_EMAIL_TO = your-email@example.com
ALERT_EMAIL_FROM = monitoring@hackthetrack.com
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 587
SMTP_USER = your-email@gmail.com
SMTP_PASS = your-app-password
\`\`\`

**For Gmail:**
1. Enable 2FA on your Google account
2. Generate an App Password at https://myaccount.google.com/apppasswords
3. Use the app password as `SMTP_PASS`

#### Slack Alerts

Set these GitHub secrets to enable Slack alerts:

\`\`\`
ALERT_SLACK_ENABLED = true
SLACK_WEBHOOK_URL = https://hooks.slack.com/services/YOUR/WEBHOOK/URL
\`\`\`

**To create a Slack webhook:**
1. Go to https://api.slack.com/apps
2. Create a new app → From scratch
3. Enable "Incoming Webhooks"
4. Add webhook to your workspace
5. Copy the webhook URL

### 3. Enable GitHub Actions

The workflow is already configured. Just push to your repository and it will:
- Run automatically every 6 hours
- Can be triggered manually from Actions tab

## Viewing Results

### GitHub Actions Artifacts

After each run, view results at:
`https://github.com/YOUR-USERNAME/YOUR-REPO/actions`

Artifacts include:
- **Screenshots** - PNG files of each page (kept 7 days)
- **Reports** - JSON and monitoring logs (kept 30 days)

### Local Results

When running locally, files are saved to:
- `monitoring/screenshots/` - Screenshot images
- `monitoring/reports/` - JSON reports
- `monitoring/logs/` - Execution logs

## Monitoring Report

Each report includes:

- **Summary**: Total pages, passed/failed counts, duration
- **Per-Page Results**:
  - Screenshot filename and path
  - Validation results (expected vs actual)
  - Any errors encountered
  - Timestamp

Example report structure:

\`\`\`json
{
  "timestamp": "2025-11-23T12:00:00.000Z",
  "summary": {
    "total": 8,
    "passed": 8,
    "failed": 0,
    "duration": "45.23s"
  },
  "results": [
    {
      "name": "Rankings",
      "url": "/rankings",
      "success": true,
      "screenshot": {
        "filename": "Rankings-1700740800000.png",
        "filepath": "./screenshots/Rankings-1700740800000.png"
      },
      "validations": [
        {
          "description": "Driver rows should be present",
          "selector": "table tbody tr",
          "expected": ">= 1",
          "actual": 42,
          "passed": true
        }
      ],
      "errors": []
    }
  ]
}
\`\`\`

## Customization

### Adding New Pages

Edit `monitoring/config.js` to add pages:

\`\`\`javascript
{
  name: 'New Page Name',
  url: '/new-page-url',
  waitForSelector: '[data-testid="content"]',
  dataValidation: [
    {
      selector: '.data-element',
      minCount: 1,
      description: 'Data should be visible'
    }
  ]
}
\`\`\`

### Adjusting Schedule

Edit `.github/workflows/monitoring.yml`:

\`\`\`yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  # - cron: '0 */4 * * *'  # Every 4 hours
  # - cron: '0 */2 * * *'  # Every 2 hours
  # - cron: '0 * * * *'    # Every hour
\`\`\`

### Screenshot Settings

Edit `monitoring/config.js`:

\`\`\`javascript
screenshot: {
  width: 1920,
  height: 1080,
  fullPage: true,  // Capture entire page
  type: 'png',     // or 'jpeg'
}
\`\`\`

## Troubleshooting

### Monitoring Fails Locally

1. Ensure Playwright is installed: `npx playwright install chromium`
2. Check your NETLIFY_URL is set correctly
3. Verify the site is accessible

### No Alerts Received

1. Check GitHub secrets are set correctly
2. Verify SMTP credentials (for email)
3. Test Slack webhook URL
4. Check alert enable flags are `'true'` (as strings)

### Screenshots Are Missing Content

1. Increase wait times in config
2. Add more specific selectors
3. Check console for JavaScript errors

## Maintenance

The system automatically:
- Cleans up screenshots older than 7 days
- Keeps reports for 30 days
- Manages storage in GitHub Actions artifacts

## Security

- Never commit credentials to git
- Always use GitHub Secrets for sensitive data
- SMTP passwords should be app-specific passwords
- Webhook URLs are secret tokens

## Support

For issues or questions:
1. Check GitHub Issues on this repository
2. Review monitoring reports for error details
3. Check GitHub Actions logs for detailed execution info

---

**Status**: ✅ Active and monitoring every 6 hours
