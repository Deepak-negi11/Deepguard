import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

import { chromium } from 'playwright';

const frontendUrl = process.env.DEEPGUARD_FRONTEND_URL ?? 'http://localhost:3000';
const browserExecutablePath = process.env.DEEPGUARD_BROWSER_EXECUTABLE;
const browserCdpUrl = process.env.DEEPGUARD_BROWSER_CDP_URL;
const testEmail = process.env.DEEPGUARD_TEST_EMAIL ?? `browser-smoke-${Date.now()}@example.com`;
const testPassword = process.env.DEEPGUARD_TEST_PASSWORD ?? 'strongpass123';
const outputDir = path.resolve(process.cwd(), '..', 'output', 'playwright', 'browser-smoke');

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function saveJson(fileName, data) {
  await fs.writeFile(path.join(outputDir, fileName), JSON.stringify(data, null, 2));
}

async function capture(page, fileName) {
  try {
    await page.screenshot({
      path: path.join(outputDir, fileName),
      fullPage: false,
      timeout: 60000,
      animations: 'disabled',
    });
  } catch (error) {
    await saveJson(`${fileName}.warning.json`, {
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : null,
    });
  }
}

function logStep(step) {
  console.log(`[browser-smoke] ${step}`);
}

async function run() {
  await ensureDir(outputDir);

  const browser = browserCdpUrl
    ? await chromium.connectOverCDP(browserCdpUrl)
    : await chromium.launch({
        headless: true,
        executablePath: browserExecutablePath || undefined,
      });
  const context = browser.contexts()[0] ?? (await browser.newContext({ viewport: { width: 1440, height: 1100 } }));
  const page = await context.newPage();
  const consoleMessages = [];
  const pageErrors = [];

  page.on('console', (message) => {
    consoleMessages.push({
      type: message.type(),
      text: message.text(),
    });
  });

  page.on('pageerror', (error) => {
    pageErrors.push({
      message: error.message,
      stack: error.stack,
    });
  });

  try {
    logStep('open-homepage');
    await page.goto(frontendUrl, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.getByRole('heading', { name: /Detect manipulated media before it spreads/i }).waitFor({ timeout: 20000 });
    await capture(page, '01-homepage.png');

    logStep('open-news-desk');
    await page.goto(new URL('/analyze/news', frontendUrl).toString(), { waitUntil: 'domcontentloaded', timeout: 45000 });
    const authEmailInput = page.getByPlaceholder('analyst@example.com');
    const authGateHeading = page.getByRole('heading', { name: /Access the News Credibility Desk/i });
    const newsDeskHeading = page.getByRole('heading', { name: /News Credibility Desk/i });
    await Promise.any([
      authGateHeading.waitFor({ timeout: 45000 }),
      newsDeskHeading.waitFor({ timeout: 45000 }),
    ]);
    if (await authEmailInput.isVisible().catch(() => false)) {
      logStep('authenticate');
      await authEmailInput.fill(testEmail);
      await page.getByPlaceholder('At least 8 characters').fill(testPassword);
      await page.getByRole('button', { name: /Create account/i }).click();
      await newsDeskHeading.waitFor({ timeout: 15000 });
    }
    await newsDeskHeading.waitFor({ timeout: 15000 });
    await capture(page, '02-news-desk.png');

    logStep('submit-news-case');
    await page.getByPlaceholder('Paste the headline, article, or suspicious claim here.').fill(
      'SHOCKING: Scientists confirm 5G towers cause cancer. Government hiding truth. Big Pharma suppressing cure. Share before deleted!',
    );

    await page.getByRole('button', { name: /Launch analysis/i }).click();
    logStep('wait-for-result');
    await page.getByRole('heading', { name: /LIKELY FAKE|LIKELY REAL|UNCERTAIN/i }).waitFor({ timeout: 120000 });
    await page.getByText(/Analyst summary/i).waitFor({ timeout: 10000 });
    await capture(page, '03-result.png');

    const verdict = await page.locator('h3').first().innerText();
    const statusNote = await page.locator('text=Case status').locator('..').innerText();
    const summary = await page.locator('p').filter({ hasText: /DeepGuard classified the text as|DeepGuard AI analyzed the text/i }).first().innerText();

    await saveJson('result-summary.json', {
      frontendUrl,
      browserExecutablePath: browserExecutablePath ?? null,
      browserCdpUrl: browserCdpUrl ?? null,
      testEmail,
      verdict,
      statusNote,
      summary,
      consoleMessages,
      pageErrors,
    });

    if (pageErrors.length > 0) {
      throw new Error(`Browser smoke completed with ${pageErrors.length} page errors`);
    }
  } finally {
    logStep('close-browser');
    await browser.close();
  }
}

run().catch(async (error) => {
  await ensureDir(outputDir);
  await saveJson('failure.json', {
    message: error instanceof Error ? error.message : String(error),
    stack: error instanceof Error ? error.stack : null,
  });
  console.error(error);
  process.exit(1);
});
