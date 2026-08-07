const { chromium } = require('playwright');

async function trial(page, name, css) {
  await page.evaluate(() => scrollTo(0, 0));
  if (css) await page.addStyleTag({ content: css });
  await page.waitForTimeout(400);
  let last = -1, stuck = 0, stops = new Set();
  for (let iter = 0; iter < 220; iter++) {
    await page.mouse.move(20, 450);   // 页面左缘，避开图表
    await page.mouse.wheel(0, 480);
    await page.waitForTimeout(380);
    const y = await page.evaluate(() => Math.round(scrollY));
    if (y === last) { stuck++; } else { stuck = 0; stops.add(y); }
    last = y;
    if (stuck >= 5) break;
  }
  const maxY = await page.evaluate(() => Math.round(document.body.scrollHeight - innerHeight));
  let lastUp = last, stuckUp = 0;
  for (let i = 0; i < 220; i++) {
    await page.mouse.move(20, 450);
    await page.mouse.wheel(0, -480);
    await page.waitForTimeout(380);
    const y = await page.evaluate(() => Math.round(scrollY));
    if (y === lastUp) { stuckUp++; } else { stuckUp = 0; }
    lastUp = y;
    if (stuckUp >= 5) break;
  }
  console.log(`${name}: down stops=${stops.size} finalY=${last}/${maxY} bottom=${last >= maxY - 5} | up finalY=${lastUp} top=${lastUp <= 5}`);
  return { stops: [...stops] };
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://127.0.0.1:8934/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3500);

  await trial(page, '现状 proximity+normal（对照）', null);
  await page.reload({ waitUntil: 'networkidle' }); await page.waitForTimeout(3000);
  await trial(page, 'A: mandatory + snap-stop:normal', `
    html { scroll-snap-type: y mandatory !important; }
    .story-scene { scroll-snap-stop: normal !important; }
    .chapter-gate { scroll-snap-align: start !important; }
  `);
  await page.reload({ waitUntil: 'networkidle' }); await page.waitForTimeout(3000);
  await trial(page, 'B: proximity + snap-stop:always', `
    html { scroll-snap-type: y proximity !important; }
    .story-scene { scroll-snap-stop: always !important; }
    .chapter-gate { scroll-snap-align: start !important; scroll-snap-stop: always !important; }
  `);
  await browser.close();
})();
