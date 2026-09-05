const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1366, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160))); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('species-icons')) errs.push(m.text().slice(0, 110)); });
  await p.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await p.waitForTimeout(1000);
  await p.evaluate(async () => {
    const s = document.createElement('style'); s.textContent = 'html,body{scroll-behavior:auto!important}'; document.head.appendChild(s);
    const h = document.body.scrollHeight; for (let y = 0; y <= h; y += 220) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 15)); }
  });
  await p.waitForTimeout(900);
  const r = await p.evaluate(() => ({
    insightGone: !document.querySelector('.insight-box'),
    bubbleGone: !document.querySelector('.bubble-section'),
    petTradeChartGone: !document.getElementById('pet-trade-chart'),
    narrativeStatsInIntro: !!document.querySelector('.narrative-stats'),
    kpiStillThere: !!document.querySelector('.overview-kpis'),
    countyQuery: !!document.getElementById('hqProvince'),
    overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth
  }));
  console.log(JSON.stringify({ r, errs: errs.slice(0, 6) }, null, 1));
  await b.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
