/**
 * Test Monitoring System
 * Quick test to verify monitoring setup before deploying
 */

import { chromium } from 'playwright';
import { config } from './config.js';

async function testMonitoring() {
  console.log('🧪 Testing HackTheTrack Monitoring System\n');

  // Test 1: Configuration
  console.log('📋 Test 1: Configuration');
  console.log(`   Base URL: ${config.baseUrl}`);
  console.log(`   Pages to monitor: ${config.pages.length}`);
  console.log(`   Screenshot path: ${config.storage.screenshotPath}`);
  console.log('   ✅ Configuration loaded\n');

  // Test 2: Browser Launch
  console.log('🌐 Test 2: Browser Launch');
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    console.log('   ✅ Browser launched successfully\n');
  } catch (error) {
    console.log('   ❌ Browser launch failed:', error.message);
    return;
  }

  // Test 3: Page Navigation
  console.log('📄 Test 3: Page Navigation (testing first page only)');
  const testPage = config.pages[0];
  console.log(`   Testing: ${testPage.name} (${testPage.url})`);

  try {
    const context = await browser.newContext({
      viewport: {
        width: config.screenshot.width,
        height: config.screenshot.height,
      },
    });

    const page = await context.newPage();

    const response = await page.goto(`${config.baseUrl}${testPage.url}`, {
      waitUntil: 'networkidle',
      timeout: config.timeouts.navigation,
    });

    if (response.ok()) {
      console.log(`   ✅ Page loaded (HTTP ${response.status()})`);
    } else {
      console.log(`   ⚠️  Page loaded with status: HTTP ${response.status()}`);
    }

    // Test 4: Selector Wait
    console.log('\n🎯 Test 4: Content Loading');
    try {
      await page.waitForSelector(testPage.waitForSelector, {
        timeout: config.timeouts.navigation,
      });
      console.log(`   ✅ Content selector found: ${testPage.waitForSelector}`);
    } catch (error) {
      console.log(`   ⚠️  Content selector not found: ${testPage.waitForSelector}`);
      console.log(`      This may indicate the page structure changed`);
    }

    // Test 5: Screenshot
    console.log('\n📸 Test 5: Screenshot Capture');
    try {
      await page.screenshot({
        path: './test-screenshot.png',
        fullPage: false,
      });
      console.log('   ✅ Screenshot captured: ./test-screenshot.png');
    } catch (error) {
      console.log('   ❌ Screenshot failed:', error.message);
    }

    // Test 6: Data Validation
    console.log('\n✅ Test 6: Data Validation');
    for (const validation of testPage.dataValidation) {
      try {
        const elements = await page.$$(validation.selector);
        const count = elements.length;
        const passed = count >= validation.minCount;

        if (passed) {
          console.log(`   ✅ ${validation.description}: ${count} found (need ${validation.minCount})`);
        } else {
          console.log(`   ⚠️  ${validation.description}: ${count} found (need ${validation.minCount})`);
        }
      } catch (error) {
        console.log(`   ❌ ${validation.description}: Error - ${error.message}`);
      }
    }

    await context.close();

  } catch (error) {
    console.log('   ❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }

  console.log('\n' + '='.repeat(60));
  console.log('🎉 Test complete!\n');
  console.log('Next steps:');
  console.log('1. Review the test results above');
  console.log('2. Check the test screenshot: ./test-screenshot.png');
  console.log('3. If everything looks good, run: node monitor.js');
  console.log('4. Set up GitHub secrets for automated monitoring');
  console.log('='.repeat(60));
}

testMonitoring()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error('Test failed:', error);
    process.exit(1);
  });
