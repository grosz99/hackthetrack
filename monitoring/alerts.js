/**
 * Alert System
 * Sends notifications when monitoring checks fail
 */

import nodemailer from 'nodemailer';
import { config } from './config.js';

/**
 * Send email alert
 */
async function sendEmailAlert(type, report) {
  if (!config.alerts.email.enabled) {
    return;
  }

  const transporter = nodemailer.createTransporter({
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: process.env.SMTP_PORT || 587,
    secure: false,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  });

  const failures = report.results.filter(r => !r.success);
  const failureList = failures.map(f =>
    `- ${f.name} (${f.url}): ${f.errors.join(', ')}`
  ).join('\n');

  const subject = type === 'failure'
    ? `🚨 HackTheTrack Monitoring Alert: ${failures.length} Page(s) Failed`
    : `✅ HackTheTrack Monitoring: All Systems Operational`;

  const html = `
    <h2>HackTheTrack Monitoring Report</h2>
    <p><strong>Timestamp:</strong> ${report.timestamp}</p>
    <p><strong>Status:</strong> ${type === 'failure' ? '❌ FAILURES DETECTED' : '✅ All Passed'}</p>

    <h3>Summary</h3>
    <ul>
      <li>Total Pages: ${report.summary.total}</li>
      <li>Passed: ${report.summary.passed}</li>
      <li>Failed: ${report.summary.failed}</li>
    </ul>

    ${failures.length > 0 ? `
      <h3>Failed Pages</h3>
      <pre>${failureList}</pre>
    ` : ''}

    <h3>All Results</h3>
    ${report.results.map(r => `
      <div style="margin: 10px 0; padding: 10px; background: ${r.success ? '#e8f5e9' : '#ffebee'};">
        <strong>${r.success ? '✅' : '❌'} ${r.name}</strong>
        <br>URL: ${r.url}
        ${r.errors.length > 0 ? `<br>Errors: ${r.errors.join(', ')}` : ''}
        ${r.screenshot ? `<br>Screenshot: ${r.screenshot.filename}` : ''}
      </div>
    `).join('')}

    <p style="margin-top: 20px; font-size: 12px; color: #666;">
      This is an automated monitoring report from HackTheTrack.
    </p>
  `;

  await transporter.sendMail({
    from: config.alerts.email.from,
    to: config.alerts.email.to,
    subject,
    html,
  });

  console.log(`📧 Email alert sent to ${config.alerts.email.to}`);
}

/**
 * Send Slack alert
 */
async function sendSlackAlert(type, report) {
  if (!config.alerts.slack.enabled || !config.alerts.slack.webhookUrl) {
    return;
  }

  const failures = report.results.filter(r => !r.success);

  const color = type === 'failure' ? 'danger' : 'good';
  const emoji = type === 'failure' ? ':rotating_light:' : ':white_check_mark:';

  const fields = [
    {
      title: 'Total Pages',
      value: report.summary.total.toString(),
      short: true,
    },
    {
      title: 'Passed',
      value: report.summary.passed.toString(),
      short: true,
    },
    {
      title: 'Failed',
      value: report.summary.failed.toString(),
      short: true,
    },
  ];

  if (failures.length > 0) {
    fields.push({
      title: 'Failed Pages',
      value: failures.map(f => `• ${f.name}`).join('\n'),
      short: false,
    });
  }

  const payload = {
    username: 'HackTheTrack Monitor',
    icon_emoji: emoji,
    attachments: [
      {
        color,
        title: type === 'failure'
          ? `${failures.length} Page(s) Failed Monitoring Checks`
          : 'All Pages Passed Monitoring Checks',
        text: `Monitoring run completed at ${report.timestamp}`,
        fields,
        footer: 'HackTheTrack Monitoring System',
        ts: Math.floor(new Date(report.timestamp).getTime() / 1000),
      },
    ],
  };

  const response = await fetch(config.alerts.slack.webhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Slack webhook failed: ${response.status}`);
  }

  console.log('💬 Slack alert sent');
}

/**
 * Main alert function
 */
export async function sendAlert(type, report) {
  const alerts = [];

  try {
    if (config.alerts.email.enabled) {
      alerts.push(sendEmailAlert(type, report));
    }

    if (config.alerts.slack.enabled) {
      alerts.push(sendSlackAlert(type, report));
    }

    await Promise.all(alerts);
  } catch (error) {
    console.error('Error sending alerts:', error.message);
  }
}

export default sendAlert;
