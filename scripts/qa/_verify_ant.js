// Verify ant decorations + flat bg maintained
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  const notFound = [];
  page.on('pageerror', e => errors.push(String(e).slice(0, 150)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 120)); });
  page.on('response', r => { if (r.status() === 404) notFound.push(r.url()); });
  await page.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1500);

  const res = await page.evaluate(() => {
    const out = {};
    const ants = [...document.querySelectorAll('.narrative-ant')];
    out.antCount = ants.length;
    out.antSvg = ants.map(a => ({ pos: a.className.includes('--left') ? 'left' : 'right', opacity: getComputedStyle(a).opacity, hasSvg: !!a.querySelector('svg') }));
    // bg unchanged
    const dark = document.querySelector('.intro-narrative-dark');
    const paper = document.querySelector('.intro-narrative-paper');
    out.darkBg = dark ? getComputedStyle(dark).backgroundColor : null;
    out.paperBg = paper ? getComputedStyle(paper).backgroundColor : null;
    out.overflowX = document.documentElement.scrollWidth > document.documentElement.clientWidth;
    // mobile hidden but no overflow
    return out;
  });

  const mob = await browser.newPage({ viewport: { width: 375, height: 812 } });
  await mob.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await mob.waitForTimeout(700);
  const mobRes = await mob.evaluate(() => ({
    overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    antsVisible: [...document.querySelectorAll('.narrative-ant')].filter(a => getComputedStyle(a).display !== 'none').length
  }));

  console.log(JSON.stringify({ res, mobRes, errors: errors.slice(0, 6), notFound: notFound.slice(0, 4) }, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
