// Verify whole page = single flat background, no masks
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
  await page.waitForTimeout(1000);
  await page.evaluate(async () => {
    const s = document.createElement('style');
    s.textContent = 'html, body { scroll-behavior: auto !important; }';
    document.head.appendChild(s);
    const h = document.body.scrollHeight;
    for (let y = 0; y <= h; y += 250) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 25)); }
    window.scrollTo(0, 0);
  });
  await page.waitForTimeout(800);

  const res = await page.evaluate(() => {
    const FLAT = 'rgb(13, 27, 21)'; // #0D1B15
    const out = { flat: true, mismatches: [], gateArtHidden: [], coverBg: null };
    // section backgrounds
    ['chapter-map','chapter-pathways','chapter-spread','chapter-impact','chapter-defense','chapter-action','chapter-species','chapter-intro'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        const bg = getComputedStyle(el).backgroundColor;
        if (id === 'chapter-intro') { out.coverBg = bg; }  // cover keeps image, bg color is base
        else if (bg === FLAT) { /* good */ }
        else { out.flat = false; out.mismatches.push(id + '=' + bg); }
      }
    });
    // intro narrative sections
    ['intro-narrative-dark','intro-narrative-paper'].forEach(c => {
      const el = document.querySelector('.' + c);
      if (el) { const bg = getComputedStyle(el).backgroundColor; if (bg !== FLAT) { out.flat = false; out.mismatches.push(c + '=' + bg); } }
    });
    // gate-art hidden
    document.querySelectorAll('.gate-art').forEach(g => { if (getComputedStyle(g).display !== 'none') out.gateArtHidden.push(g.className); });
    // fade background
    const fade = document.querySelector('.intro-outro-fade');
    out.fadeBg = fade ? getComputedStyle(fade).backgroundColor : null;
    // gate open? count gates
    out.gates = document.querySelectorAll('.chapter-gate').length;
    out.overflowX = document.documentElement.scrollWidth > document.documentElement.clientWidth;
    out.coverHasImage = out.coverBg === FLAT ? 'base-color (image via background-image)' : 'different';
    return out;
  });

  console.log(JSON.stringify({ res, errors: errors.slice(0, 6), notFound: notFound.slice(0, 4) }, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
