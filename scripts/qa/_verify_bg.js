// Verify unified base background + gate-art layers + no regressions
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  const notFound = [];
  page.on('pageerror', e => errors.push('PAGEERROR: ' + String(e).slice(0, 200)));
  page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE: ' + m.text().slice(0, 150)); });
  page.on('response', r => { if (r.status() === 404) notFound.push(r.url()); });

  await page.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1200);
  await page.evaluate(async () => {
    const s = document.createElement('style');
    s.textContent = 'html, body { scroll-behavior: auto !important; }';
    document.head.appendChild(s);
    const h = document.body.scrollHeight;
    for (let y = 0; y <= h; y += 250) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 30)); }
    window.scrollTo(0, 0);
  });
  await page.waitForTimeout(1200);

  const res = await page.evaluate(() => {
    const out = {};
    // computed section backgrounds
    out.sectionBg = {};
    ['chapter-map','chapter-pathways','chapter-spread','chapter-impact','chapter-defense','chapter-action'].forEach(id => {
      const el = document.getElementById(id);
      if (el) out.sectionBg[id] = getComputedStyle(el).backgroundColor;
    });
    out.bodyBg = getComputedStyle(document.body).backgroundColor;
    // gates and art
    out.gates = document.querySelectorAll('.chapter-gate').length;
    out.gateArt = [...document.querySelectorAll('.gate-art')].map(g => g.style.backgroundImage.split('/').pop());
    // gate-content visible (above art)
    const gc = document.querySelector('.chapter-gate .gate-content');
    out.gateContentZ = gc ? getComputedStyle(gc).zIndex : null;
    // text not hidden by art
    out.gateTitleVisible = !!document.querySelector('.chapter-gate .gate-title');
    // credits still last
    const credits = document.querySelector('.data-credits');
    out.creditsLast = credits ? (credits === document.querySelector('#actionContent').lastElementChild) : null;
    out.overflowX = document.documentElement.scrollWidth > document.documentElement.clientWidth;
    out.activated = [...document.querySelectorAll('section.activated')].map(s => s.id);
    return out;
  });

  console.log(JSON.stringify({ res, errors: errors.slice(0, 8), notFound: notFound.slice(0, 5) }, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
