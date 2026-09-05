const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1366, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await p.waitForTimeout(1000);
  await p.evaluate(async () => {
    const s = document.createElement('style'); s.textContent = 'html,body{scroll-behavior:auto!important}'; document.head.appendChild(s);
    const h = document.body.scrollHeight; for (let y = 0; y <= h; y += 220) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 15)); }
  });
  await p.waitForTimeout(700);
  const r = await p.evaluate(() => {
    const fig = document.querySelector('.narrative-figure');
    const antImgs = [...document.querySelectorAll('img')].filter(i => (i.alt || '').includes('红火蚁 Solenopsis')).length;
    const paper = document.querySelector('.intro-narrative-paper');
    const dark = document.querySelector('.intro-narrative-dark');
    return {
      figureGone: !fig,
      antImgCount: antImgs,
      paperPadTop: paper ? getComputedStyle(paper).paddingTop : null,
      darkPadTop: dark ? getComputedStyle(dark).paddingTop : null,
      overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth
    };
  });
  console.log(JSON.stringify({ r, errs: errs.slice(0, 5) }, null, 1));
  await b.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
