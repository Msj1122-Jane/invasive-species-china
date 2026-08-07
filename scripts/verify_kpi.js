const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = [];
  page.on('pageerror', e => errs.push('pageerror: ' + e.message));
  await page.goto('http://127.0.0.1:8936/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);
  await page.evaluate(() => document.querySelector('.overview-kpis').scrollIntoView({ block: 'start' }));
  await page.waitForTimeout(2500); // 等数字滚动动画
  await page.screenshot({ path: 'outputs/kpi_new.png' });
  // 移动端
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(800);
  await page.evaluate(() => document.querySelector('.overview-kpis').scrollIntoView({ block: 'start' }));
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'outputs/kpi_new_mobile.png' });
  console.log('ERRORS:', JSON.stringify(errs.slice(0, 5)));
  await browser.close();
})();
