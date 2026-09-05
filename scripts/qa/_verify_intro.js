// Verify narrative visuals: photo, chips, stats; no errors/overflow
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
    const fig = document.querySelector('.narrative-figure');
    out.figure = !!fig;
    if (fig) { const img = fig.querySelector('img'); out.imgSrc = img ? (img.src.split('/').pop() || img.src) : null; out.imgLoaded = img ? (img.complete && img.naturalWidth > 0) : false; out.caption = fig.querySelector('figcaption')?.textContent.trim().slice(0, 60); }
    out.chipsLabel = document.querySelector('.narrative-chips-label')?.textContent.trim();
    out.chips = [...document.querySelectorAll('.narrative-chips span')].map(s => s.textContent.trim());
    out.stats = [...document.querySelectorAll('.narrative-stat .ns-num')].map(n => n.textContent.trim());
    out.statsNote = document.querySelector('.narrative-stats-note')?.textContent.trim().slice(0, 120);
    out.narrativeLeadCount = document.querySelectorAll('.narrative-lead').length;
    // narrative text still on flat bg
    const paper = document.querySelector('.intro-narrative-paper');
    out.paperBg = paper ? getComputedStyle(paper).backgroundColor : null;
    out.overflowX = document.documentElement.scrollWidth > document.documentElement.clientWidth;
    // mobile
    return out;
  });

  // mobile check
  const mob = await browser.newPage({ viewport: { width: 375, height: 812 } });
  await mob.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await mob.waitForTimeout(800);
  const mobRes = await mob.evaluate(() => ({
    overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    statsCols: getComputedStyle(document.querySelector('.narrative-stats')).gridTemplateColumns
  }));

  console.log(JSON.stringify({ res, mobRes, errors: errors.slice(0, 6), notFound: notFound.slice(0, 6) }, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
