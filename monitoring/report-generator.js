/**
 * Report Generator
 * Creates detailed monitoring reports
 */

export async function generateReport(results, startTime) {
  const endTime = new Date();
  const duration = endTime - startTime;

  const summary = {
    total: results.length,
    passed: results.filter(r => r.success).length,
    failed: results.filter(r => !r.success).length,
    duration: `${(duration / 1000).toFixed(2)}s`,
  };

  const report = {
    timestamp: startTime.toISOString(),
    endTime: endTime.toISOString(),
    duration: summary.duration,
    summary,
    results: results.map(r => ({
      ...r,
      validationSummary: {
        total: r.validations.length,
        passed: r.validations.filter(v => v.passed).length,
        failed: r.validations.filter(v => !v.passed).length,
      },
    })),
  };

  return report;
}

export function generateHTMLReport(report) {
  const failedPages = report.results.filter(r => !r.success);

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HackTheTrack Monitoring Report</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: #f5f5f5;
      padding: 20px;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      overflow: hidden;
    }

    .header {
      background: linear-gradient(135deg, #EB0A1E 0%, #C4161C 100%);
      color: white;
      padding: 30px;
    }

    .header h1 {
      font-size: 28px;
      margin-bottom: 10px;
    }

    .header p {
      opacity: 0.9;
      font-size: 14px;
    }

    .summary {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      padding: 30px;
      background: #f9f9f9;
      border-bottom: 1px solid #eee;
    }

    .summary-card {
      background: white;
      padding: 20px;
      border-radius: 6px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .summary-card h3 {
      font-size: 14px;
      color: #666;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .summary-card .value {
      font-size: 32px;
      font-weight: bold;
      color: #333;
    }

    .summary-card.passed .value { color: #4CAF50; }
    .summary-card.failed .value { color: #EB0A1E; }

    .results {
      padding: 30px;
    }

    .results h2 {
      font-size: 20px;
      margin-bottom: 20px;
      color: #333;
    }

    .result-card {
      background: white;
      border: 2px solid #eee;
      border-radius: 6px;
      padding: 20px;
      margin-bottom: 20px;
    }

    .result-card.success {
      border-color: #4CAF50;
    }

    .result-card.failure {
      border-color: #EB0A1E;
      background: #fff5f5;
    }

    .result-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 15px;
    }

    .status-icon {
      font-size: 24px;
    }

    .result-title {
      flex: 1;
    }

    .result-title h3 {
      font-size: 18px;
      color: #333;
      margin-bottom: 4px;
    }

    .result-title p {
      font-size: 14px;
      color: #666;
    }

    .validations {
      margin-top: 15px;
      padding-top: 15px;
      border-top: 1px solid #eee;
    }

    .validation-item {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 8px 0;
      font-size: 14px;
    }

    .validation-item .icon {
      flex-shrink: 0;
      font-size: 16px;
    }

    .errors {
      margin-top: 15px;
      padding: 12px;
      background: #ffebee;
      border-left: 4px solid #EB0A1E;
      border-radius: 4px;
    }

    .errors h4 {
      color: #EB0A1E;
      font-size: 14px;
      margin-bottom: 8px;
    }

    .errors ul {
      list-style: none;
      font-size: 14px;
      color: #666;
    }

    .errors li {
      padding: 4px 0;
    }

    .screenshot {
      margin-top: 15px;
      padding: 12px;
      background: #f9f9f9;
      border-radius: 4px;
      font-size: 14px;
      color: #666;
    }

    .screenshot strong {
      color: #333;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🏁 HackTheTrack Monitoring Report</h1>
      <p>Generated: ${report.timestamp}</p>
      <p>Duration: ${report.duration}</p>
    </div>

    <div class="summary">
      <div class="summary-card">
        <h3>Total Pages</h3>
        <div class="value">${report.summary.total}</div>
      </div>
      <div class="summary-card passed">
        <h3>Passed</h3>
        <div class="value">${report.summary.passed}</div>
      </div>
      <div class="summary-card failed">
        <h3>Failed</h3>
        <div class="value">${report.summary.failed}</div>
      </div>
    </div>

    <div class="results">
      ${failedPages.length > 0 ? `
        <h2>❌ Failed Pages (${failedPages.length})</h2>
        ${failedPages.map(result => generateResultCard(result, false)).join('')}
      ` : ''}

      <h2>✅ All Results</h2>
      ${report.results.map(result => generateResultCard(result, true)).join('')}
    </div>
  </div>
</body>
</html>
  `;
}

function generateResultCard(result, showSuccess) {
  const statusClass = result.success ? 'success' : 'failure';
  const statusIcon = result.success ? '✅' : '❌';

  return `
    <div class="result-card ${statusClass}">
      <div class="result-header">
        <div class="status-icon">${statusIcon}</div>
        <div class="result-title">
          <h3>${result.name}</h3>
          <p>${result.url}</p>
        </div>
      </div>

      ${result.errors.length > 0 ? `
        <div class="errors">
          <h4>Errors</h4>
          <ul>
            ${result.errors.map(e => `<li>• ${e}</li>`).join('')}
          </ul>
        </div>
      ` : ''}

      ${result.validations.length > 0 ? `
        <div class="validations">
          <strong>Validations (${result.validationSummary.passed}/${result.validationSummary.total} passed)</strong>
          ${result.validations.map(v => `
            <div class="validation-item">
              <span class="icon">${v.passed ? '✓' : '✗'}</span>
              <div>
                <div>${v.description}</div>
                <div style="font-size: 12px; color: #999;">
                  Expected: ${v.expected}, Got: ${v.actual || 'error'}
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      ` : ''}

      ${result.screenshot ? `
        <div class="screenshot">
          <strong>Screenshot:</strong> ${result.screenshot.filename}
        </div>
      ` : ''}
    </div>
  `;
}

export default generateReport;
