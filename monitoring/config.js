/**
 * Monitoring Configuration
 * Define all pages to monitor and validation rules
 */

export const config = {
  // Base URL - replace with your actual Netlify URL
  baseUrl: process.env.NETLIFY_URL || 'https://gibbs-ai.netlify.app',

  // API URL
  apiUrl: process.env.VITE_API_URL || 'https://hackthetrack-api-ae28ad6f804d.herokuapp.com',

  // Screenshot settings
  screenshot: {
    width: 1920,
    height: 1080,
    fullPage: true,
    type: 'png',
  },

  // Timeout settings (in milliseconds)
  timeouts: {
    navigation: 30000,  // 30 seconds
    apiResponse: 15000, // 15 seconds
  },

  // Pages to monitor
  pages: [
    {
      name: 'Rankings',
      url: '/rankings',
      waitForSelector: 'table tbody tr',
      dataValidation: [
        { selector: 'table tbody tr', minCount: 10, description: 'Driver rows should be present' },
        { selector: 'table th', minCount: 5, description: 'Table headers should be visible' },
      ],
    },
    {
      name: 'Overview - Driver 7',
      url: '/driver/7/overview',
      waitForSelector: '[data-testid="overview-content"], .overview-container',
      dataValidation: [
        { selector: '[data-testid="stat-card"], .stat-card', minCount: 3, description: 'Stat cards should be visible' },
        { selector: 'canvas, svg', minCount: 1, description: 'Charts should be rendered' },
      ],
    },
    {
      name: 'Race Log - Driver 7',
      url: '/driver/7/race-log',
      waitForSelector: '[data-testid="race-log"], .race-log-container',
      dataValidation: [
        { selector: '[data-testid="race-entry"], .race-entry', minCount: 1, description: 'Race entries should be present' },
      ],
    },
    {
      name: 'Skills - Driver 7',
      url: '/driver/7/skills',
      waitForSelector: '[data-testid="skills-content"], .skills-container',
      dataValidation: [
        { selector: 'canvas, svg, [data-testid="radar-chart"]', minCount: 1, description: 'Skill visualization should be present' },
      ],
    },
    {
      name: 'Driver Development - Driver 7',
      url: '/driver/7/driver-development',
      waitForSelector: '[data-testid="improve-content"], .improve-container',
      dataValidation: [
        { selector: '[data-testid="skill-slider"], input[type="range"]', minCount: 1, description: 'Skill sliders should be present' },
      ],
    },
    {
      name: 'Telemetry Comparison - Driver 7',
      url: '/driver/7/telemetry-comparison',
      waitForSelector: '[data-testid="telemetry-content"], .telemetry-container',
      dataValidation: [
        { selector: 'canvas, svg, [data-testid="speed-trace"]', minCount: 1, description: 'Telemetry charts should be rendered' },
      ],
    },
    {
      name: 'Strategy Chat - Driver 7',
      url: '/driver/7/strategy-chat',
      waitForSelector: '[data-testid="chat-container"], .chat-interface',
      dataValidation: [
        { selector: '[data-testid="chat-input"], input, textarea', minCount: 1, description: 'Chat input should be present' },
      ],
    },
    {
      name: 'Track Intelligence',
      url: '/track-intelligence',
      waitForSelector: '[data-testid="track-intelligence"], .track-intelligence-container',
      dataValidation: [
        { selector: 'canvas, svg, [data-testid="track-map"]', minCount: 1, description: 'Track visualization should be present' },
      ],
    },
  ],

  // Alert settings
  alerts: {
    email: {
      enabled: process.env.ALERT_EMAIL_ENABLED === 'true',
      to: process.env.ALERT_EMAIL_TO || 'your-email@example.com',
      from: process.env.ALERT_EMAIL_FROM || 'monitoring@hackthetrack.com',
    },
    slack: {
      enabled: process.env.ALERT_SLACK_ENABLED === 'true',
      webhookUrl: process.env.SLACK_WEBHOOK_URL,
    },
  },

  // Storage settings
  storage: {
    keepScreenshots: 168, // Keep screenshots for 7 days (in hours)
    screenshotPath: './screenshots',
    reportPath: './reports',
    logPath: './logs',
  },
};

export default config;
