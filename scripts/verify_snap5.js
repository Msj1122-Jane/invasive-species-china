const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = [];
  page.on('pageerror', e => errs.push('pageerror: ' + e.message));
  await page.goto('http://127.0.0.1:8934/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3500);

  const snap = await page.evaluate(() => ({
    htmlSnap: getComputedStyle(document.documentElement).scrollSnapType,
    sectionOverflow: getComputedStyle(document.querySelector('.section')).overflow,
    targets: [...document.querySelectorAll('.story-scene, .chapter-gate')].length
  }));
  console.log('SNAP CONFIG:', JSON.stringify(snap));

  // 向下逐滚
  let last = -1, stuck = 0; const stops = [];
  for (let i = 0; i < 260; i++) {
    await page.mouse.move(20, 450);
    await page.mouse.wheel(0, 480);
    await page.waitForTimeout(420);
    const y = await page.evaluate(() => Math.round(scrollY));
    if (y === last) { stuck++; } else { stuck = 0; stops.push(y); }
    last = y;
    if (stuck >= 6) { console.log('STUCK at', y); break; }
  }
  const maxY = await page.evaluate(() => Math.round(document.body.scrollHeight - innerHeight));
  console.log('DOWN stops:', stops.length, 'finalY:', last, '/', maxY, 'bottom:', last >= maxY - 5);
  console.log('stops seq:', stops.slice(0, 30).join(','));

  // 向上逐滚
  let lastUp = last, stuckUp = 0;
  for (let i = 0; i < 260; i++) {
    await page.mouse.move(20, 450);
    await page.mouse.wheel(0, -480);
    await page.waitForTimeout(420);
    const y = await page.evaluate(() => Math.round(scrollY));
    if (y === lastUp) { stuckUp++; } else { stuckUp = 0; }
    lastUp = y;
    if (stuckUp >= 6) { console.log('STUCK-UP at', y); break; }
  }
  console.log('UP finalY:', lastUp, 'top:', lastUp <= 5);
  console.log('ERRORS:', JSON.stringify(errs.slice(0, 6)));
  await browser.close();
})();
