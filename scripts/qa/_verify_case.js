// Verify spread side panel now shows case record (no-photo species) and photos (photo species)
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1366, height: 850 } });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e).slice(0, 140)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 100)); });
  await page.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1000);
  // scroll through to activate spread chapter
  await page.evaluate(async () => {
    const s = document.createElement('style'); s.textContent = 'html,body{scroll-behavior:auto!important}'; document.head.appendChild(s);
    const h = document.body.scrollHeight; for (let y = 0; y <= h; y += 200) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 20)); }
  });
  await page.waitForTimeout(800);

  async function readPanel() {
    return await page.evaluate(() => {
      const layer = document.querySelector('.spread-photo-layer');
      const caseCard = layer ? layer.querySelector('.spread-case-card') : null;
      return {
        header: (document.querySelector('.spread-side-title') || {}).textContent?.trim(),
        hasCase: !!caseCard,
        caseText: caseCard ? caseCard.textContent.replace(/\s+/g, ' ').trim().slice(0, 120) : null,
        photoImgs: layer ? layer.querySelectorAll('.spread-photo-card img').length : 0,
        noPhotoMsg: layer ? layer.textContent.includes('暂无实地观察照片') : false
      };
    });
  }

  // find the species tab buttons
  const tabs = await page.evaluate(() => [...document.querySelectorAll('.spread-tab')].map(t => t.textContent.trim()));
  const results = { header: null, byTab: {} };
  // click each tab that exists
  for (const name of ['三裂叶豚草', '互花米草', '松材线虫病']) {
    const clicked = await page.evaluate((n) => {
      const t = [...document.querySelectorAll('.spread-tab')].find(x => x.textContent.trim() === n);
      if (t) { t.click(); return true; } return false;
    }, name);
    if (clicked) {
      await page.waitForTimeout(900);
      results.byTab[name] = await readPanel();
    }
  }

  console.log(JSON.stringify({ tabs, results, errors: errors.slice(0, 6) }, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
