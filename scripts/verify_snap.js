const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = [];
  page.on('pageerror', e => errs.push('pageerror: ' + e.message));
  await page.goto('http://127.0.0.1:8934/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3500);

  // 注入目标样式（模拟改完后的效果）
  await page.addStyleTag({ content: `
    html { scroll-snap-type: y mandatory !important; }
    .story-scene { scroll-snap-stop: always !important; }
    .chapter-gate { scroll-snap-align: start !important; scroll-snap-stop: always !important; }
  `});
  await page.waitForTimeout(500);

  // 1) 快照目标高度普查
  const survey = await page.evaluate(() => {
    const vh = innerHeight;
    const targets = [...document.querySelectorAll('.story-scene, .chapter-gate')];
    const tall = targets.filter(el => el.offsetHeight > vh * 1.05).map(el => ({
      cls: el.className.slice(0, 30), label: el.dataset?.sceneLabel || '',
      h: Math.round(el.offsetHeight / vh * 10) / 10
    }));
    return { vh, count: targets.length, tall, docH: Math.round(document.body.scrollHeight / vh * 10) / 10 };
  });
  console.log('SURVEY:', JSON.stringify(survey, null, 1));

  // 2) 滚轮向下：每次一滚，记录停留位置
  const rests = new Set();
  let stuck = 0, last = -1;
  for (let i = 0; i < 160; i++) {
    await page.mouse.move(720, 450);
    await page.mouse.wheel(0, 480);
    await page.waitForTimeout(450);
    const y = await page.evaluate(() => Math.round(scrollY));
    if (y === last) stuck++; else stuck = 0;
    last = y; rests.add(y);
    if (stuck >= 6) break;
  }
  const maxY = await page.evaluate(() => Math.round(document.body.scrollHeight - innerHeight));
  console.log('DOWN: rest stops =', rests.size, 'finalY =', last, 'maxY =', maxY, 'reachedBottom =', last >= maxY - 5);

  // 3) 滚轮向上
  let lastUp = last, stuckUp = 0;
  const restsUp = new Set();
  for (let i = 0; i < 160; i++) {
    await page.mouse.wheel(0, -480);
    await page.waitForTimeout(450);
    const y = await page.evaluate(() => Math.round(scrollY));
    if (y === lastUp) stuckUp++; else stuckUp = 0;
    lastUp = y; restsUp.add(y);
    if (stuckUp >= 6) break;
  }
  console.log('UP: rest stops =', restsUp.size, 'finalY =', lastUp, 'reachedTop =', lastUp <= 5);
  console.log('ERRORS:', JSON.stringify(errs.slice(0, 8)));
  await browser.close();
})();
