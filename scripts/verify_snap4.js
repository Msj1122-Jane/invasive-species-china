const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://127.0.0.1:8934/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);
  const info = await page.evaluate(() => {
    const scene = document.querySelector('.story-scene');
    const chain = [];
    let el = scene;
    while (el && el !== document.documentElement) {
      const cs = getComputedStyle(el);
      chain.push({
        tag: el.tagName, cls: (el.className || '').toString().slice(0, 40),
        overflow: cs.overflow + '/' + cs.overflowY,
        transform: cs.transform !== 'none',
        contain: cs.contain
      });
      el = el.parentElement;
    }
    return {
      scrollingElement: document.scrollingElement.tagName,
      htmlSnap: getComputedStyle(document.documentElement).scrollSnapType,
      bodySnap: getComputedStyle(document.body).scrollSnapType,
      sceneSnapAlign: getComputedStyle(scene).scrollSnapAlign,
      htmlOverflow: getComputedStyle(document.documentElement).overflowY,
      bodyOverflow: getComputedStyle(document.body).overflowY,
      bodyH: getComputedStyle(document.body).height,
      chain
    };
  });
  console.log(JSON.stringify(info, null, 1));
  await browser.close();
})();
