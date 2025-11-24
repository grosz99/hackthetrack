/**
 * Monitoring Configuration
 * Define all pages to monitor and validation rules
 */

export const config = {
  // Base URL
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

  // Pages to monitor - ONLY the 5 pages requested
  pages: [
    {
      name: 'Home - Rankings',
      url: '/',
      waitForSelector: 'table tbody tr',
      dataValidation: [
        { selector: 'table tbody tr', minCount: 10, description: 'Driver rows should be present' },
        { selector: 'table th', minCount: 5, description: 'Table headers should be visible' },
      ],
    },
    {
      name: 'Overview - Driver 72',
      url: '/driver/72/overview',
      waitForSelector: 'body',
      dataValidation: [
        { selector: 'h1, h2, h3', minCount: 1, description: 'Page headers should be present' },
      ],
    },
    {
      name: 'Race Log - Driver 72',
      url: '/driver/72/race-log',
      waitForSelector: 'body',
      dataValidation: [
        { selector: 'h1, h2, h3', minCount: 1, description: 'Page headers should be present' },
      ],
    },
    {
      name: 'Skills - Driver 72',
      url: '/driver/72/skills',
      waitForSelector: 'body',
      dataValidation: [
        { selector: 'h1, h2, h3', minCount: 1, description: 'Page headers should be present' },
        { selector: 'canvas, svg', minCount: 1, description: 'Charts should be rendered' },
      ],
    },
    {
      name: 'Driver Development - Driver 72',
      url: '/driver/72/driver-development',
      waitForSelector: 'body',
      dataValidation: [
        { selector: 'h1, h2, h3', minCount: 1, description: 'Page headers should be present' },
      ],
    },
  ],

  // Alert settings
  alerts: {
    email: {
      enabled: process.env.ALERT_EMAIL_ENABLED === 'true',
      to: process.env.ALERT_EMAIL_TO || 'justin.m.grosz@gmail.com',
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
