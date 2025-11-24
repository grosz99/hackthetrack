/**
 * HackTheTrack Monitoring System
 * Takes screenshots and validates data on all pages every 6 hours
 */

import { chromium } from 'playwright';
import fs from 'fs/promises';
import path from 'path';
import { config } from './config.js';
import { sendAlert } from './alerts.js';
import { generateReport } from './report-generator.js';

class MonitoringSystem {
  constructor() {
    this.results = [];
    this.startTime = new Date();
  }

  async init() {
    // Ensure directories exist
    await fs.mkdir(config.storage.screenshotPath, { recursive: true });
    await fs.mkdir(config.storage.reportPath, { recursive: true });
    await fs.mkdir(config.storage.logPath, { recursive: true });
  }

  async captureScreenshot(page, pageName, timestamp) {
    const filename = `${pageName.replace(/\s+/g, '-')}-${timestamp}.png`;
    const filepath = path.join(config.storage.screenshotPath, filename);

    await page.screenshot({
      path: filepath,
      fullPage: config.screenshot.fullPage,
      type: config.screenshot.type,
    });

    return { filename, filepath };
  }

  async validatePage(page, pageConfig) {
    const validationResults = [];

    for (const validation of pageConfig.dataValidation) {
      try {
        const elements = await page.$$(validation.selector);
        const count = elements.length;
        const passed = count >= validation.minCount;

        validationResults.push({
          description: validation.description,
          selector: validation.selector,
          expected: `>= ${validation.minCount}`,
          actual: count,
          passed,
        });

        if (!passed) {
          console.warn(`⚠️  Validation failed: ${validation.description}`);
          console.warn(`   Expected >= ${validation.minCount}, got ${count}`);
        }
      } catch (error) {
        validationResults.push({
          description: validation.description,
          selector: validation.selector,
          error: error.message,
          passed: false,
        });
      }
    }

    return validationResults;
  }

  async monitorPage(browser, pageConfig, timestamp) {
    const context = await browser.newContext({
      viewport: {
        width: config.screenshot.width,
        height: config.screenshot.height,
      },
    });

    const page = await context.newPage();

    const result = {
      name: pageConfig.name,
      url: pageConfig.url,
      timestamp: new Date().toISOString(),
      success: false,
      screenshot: null,
      validations: [],
      errors: [],
    };

    try {
      console.log(`📄 Monitoring: ${pageConfig.name} (${pageConfig.url})`);

      // Navigate to page
      const response = await page.goto(`${config.baseUrl}${pageConfig.url}`, {
        waitUntil: 'networkidle',
        timeout: config.timeouts.navigation,
      });

      if (!response.ok()) {
        throw new Error(`HTTP ${response.status()}: ${response.statusText()}`);
      }

      // Wait for main content
      try {
        await page.waitForSelector(pageConfig.waitForSelector, {
          timeout: config.timeouts.navigation,
        });
      } catch (error) {
        result.errors.push(`Wait for selector failed: ${pageConfig.waitForSelector}`);
      }

      // Additional wait for data to load
      await page.waitForTimeout(3000);

      // Capture screenshot
      const screenshot = await this.captureScreenshot(page, pageConfig.name, timestamp);
      result.screenshot = screenshot;

      // Validate page data
      result.validations = await this.validatePage(page, pageConfig);

      // Check if all validations passed
      const allPassed = result.validations.every(v => v.passed);
      result.success = allPassed && result.errors.length === 0;

      if (result.success) {
        console.log(`✅ ${pageConfig.name}: All checks passed`);
      } else {
        console.log(`❌ ${pageConfig.name}: Some checks failed`);
      }

    } catch (error) {
      result.errors.push(error.message);
      console.error(`❌ Error monitoring ${pageConfig.name}:`, error.message);

      // Try to capture screenshot even on error
      try {
        const screenshot = await this.captureScreenshot(page, `${pageConfig.name}-ERROR`, timestamp);
        result.screenshot = screenshot;
      } catch (screenshotError) {
        console.error(`Failed to capture error screenshot: ${screenshotError.message}`);
      }
    } finally {
      await context.close();
    }

    return result;
  }

  async run() {
    console.log('\n🚀 Starting HackTheTrack Monitoring System');
    console.log(`📅 Timestamp: ${this.startTime.toISOString()}`);
    console.log(`🌐 Base URL: ${config.baseUrl}`);
    console.log(`📊 Pages to monitor: ${config.pages.length}\n`);

    await this.init();

    const timestamp = this.startTime.getTime();
    const browser = await chromium.launch({ headless: true });

    try {
      // Monitor all pages
      for (const pageConfig of config.pages) {
        const result = await this.monitorPage(browser, pageConfig, timestamp);
        this.results.push(result);
      }

      // Generate report
      const report = await generateReport(this.results, this.startTime);

      // Save report
      const reportFilename = `monitoring-report-${timestamp}.json`;
      const reportPath = path.join(config.storage.reportPath, reportFilename);
      await fs.writeFile(reportPath, JSON.stringify(report, null, 2));

      // Check for failures
      const failures = this.results.filter(r => !r.success);

      if (failures.length > 0) {
        console.log(`\n⚠️  ${failures.length} page(s) failed monitoring checks`);
        await sendAlert('failure', report);
      } else {
        console.log('\n✅ All pages passed monitoring checks');
      }

      // Log summary
      console.log('\n📊 Summary:');
      console.log(`   Total pages: ${this.results.length}`);
      console.log(`   Passed: ${this.results.filter(r => r.success).length}`);
      console.log(`   Failed: ${failures.length}`);
      console.log(`   Report saved: ${reportPath}`);

      // Cleanup old screenshots
      await this.cleanupOldScreenshots();

    } finally {
      await browser.close();
    }

    return this.results;
  }

  async cleanupOldScreenshots() {
    const cutoffTime = Date.now() - (config.storage.keepScreenshots * 60 * 60 * 1000);

    try {
      const files = await fs.readdir(config.storage.screenshotPath);
      let deletedCount = 0;

      for (const file of files) {
        const filepath = path.join(config.storage.screenshotPath, file);
        const stats = await fs.stat(filepath);

        if (stats.mtimeMs < cutoffTime) {
          await fs.unlink(filepath);
          deletedCount++;
        }
      }

      if (deletedCount > 0) {
        console.log(`🗑️  Cleaned up ${deletedCount} old screenshot(s)`);
      }
    } catch (error) {
      console.error('Error cleaning up screenshots:', error.message);
    }
  }
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const monitor = new MonitoringSystem();
  monitor.run()
    .then(() => {
      console.log('\n✅ Monitoring completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Monitoring failed:', error);
      process.exit(1);
    });
}

export default MonitoringSystem;
