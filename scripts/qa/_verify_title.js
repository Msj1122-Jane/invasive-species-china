// Verify retitle + narrative reframe + no overflow
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  const notFound = [];
  page.on('pageerror', e => errors.push(String(e).slice(0, 120)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 100)); });
  page.on('response', r => { if (r.status() === 404) notFound.push(r.url()); });
  await page.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1500);
  await page.evaluate(async () => {
    const s = document.createElement('style');
    s.textContent = 'html, body { scroll-behavior: auto !important; }';
    document.head.appendChild(s);
    const h = document.body.scrollHeight;
    for (let y = 0; y <= h; y += 300) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 25)); }
    window.scrollTo(0, 0);
  });
  await page.waitForTimeout(700);

  const res = await page.evaluate(() => {
    const out = {};
    out.docTitle = document.title;
    out.ogTitle = document.querySelector('meta[property="og:title"]')?.content;
    out.hero = document.querySelector('.intro-main-title')?.textContent.trim();
    out.lead = document.querySelector('.intro-lead')?.textContent.trim();
    out.subtitle = document.querySelector('.intro-subtitle')?.textContent.trim();
    out.navLogo = document.querySelector('#mainNav .nav-logo')?.textContent.trim();
    // narrative closing no longer says 来者何物 (except subtitle tagline)
    out.introHas_laiZhe = document.querySelector('.intro-narrative-paper .intro-narrative-inner')?.textContent.includes('来者何物');
    out.introHas_shouwei = document.querySelector('.intro-narrative-paper .intro-narrative-inner')?.textContent.includes('守卫国门');
    // img load
    const fig = document.querySelector('.narrative-figure img');
    out.imgLoaded = fig ? (fig.complete && fig.naturalWidth > 0) : null;
    out.overflowX = document.documentElement.scrollWidth > document.documentElement.clientWidth;
    return out;
  });

  const mob = await browser.newPage({ viewport: { width: 375, height: 812 } });
  await mob.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await mob.waitForTimeout(700);
  const mobRes = await mob.evaluate(() => ({
    overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    hero: document.querySelector('.intro-main-title')?.textContent.trim()
  }));

  console.log(JSON.stringify({ res, mobRes, errors: errors.slice(0, 6), notFound: notFound.slice(0, 4) }, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
