// Post-edit regression verification
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  const notFound = [];
  page.on('pageerror', e => errors.push('PAGEERROR: ' + String(e).slice(0, 300)));
  page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE: ' + m.text().slice(0, 200)); });
  page.on('response', r => { if (r.status() === 404) notFound.push(r.url()); });

  await page.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1200);
  // instant scroll to activate everything
  await page.evaluate(async () => {
    const style = document.createElement('style');
    style.textContent = 'html, body { scroll-behavior: auto !important; }';
    document.head.appendChild(style);
    const h = document.body.scrollHeight;
    for (let y = 0; y <= h; y += 250) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 30)); }
    window.scrollTo(0, h); // go to bottom for credits
  });
  await page.waitForTimeout(1500);

  const res = await page.evaluate(() => {
    const out = {};
    // meta
    out.ogTitle = document.querySelector('meta[property="og:title"]')?.content || null;
    out.ogImage = document.querySelector('meta[property="og:image"]')?.content || null;
    out.description = document.querySelector('meta[name="description"]')?.content?.slice(0, 60) || null;
    // cover byline
    const byline = document.querySelector('.intro-byline');
    out.coverByline = byline ? byline.textContent.trim() : null;
    // credits block
    const credits = document.querySelector('.data-credits');
    out.credits = credits ? credits.textContent.replace(/\s+/g, ' ').trim().slice(0, 150) : null;
    out.creditsLast = credits ? (credits === document.querySelector('#actionContent').lastElementChild) : null;
    // src links count
    out.srcLinks = [...document.querySelectorAll('a.src-link')].map(a => a.textContent.trim() + ' -> ' + a.href);
    // defense note
    out.defenseNote = !!document.body.textContent.includes('分别为宁波、北京、上海海关公开通报口径');
    // new copy
    out.newPetCopy = document.body.textContent.includes('1707 万人饲养"异宠"');
    out.oldPetCopyGone = !document.body.textContent.includes('养殖异宠规模已超1700万');
    // activated chapters
    out.activated = [...document.querySelectorAll('section.activated')].map(s => s.id);
    // overflow
    out.overflowX = document.documentElement.scrollWidth > document.documentElement.clientWidth;
    // body height
    out.bodyH = document.body.scrollHeight;
    // scroll to cover to check byline visible position (skip)
    return out;
  });

  // mobile check
  const mob = await browser.newPage({ viewport: { width: 375, height: 812 } });
  await mob.goto('http://127.0.0.1:8741/index.html', { waitUntil: 'networkidle', timeout: 60000 });
  await mob.waitForTimeout(800);
  const mobRes = await mob.evaluate(() => ({
    overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    bylineVisible: !!document.querySelector('.intro-byline')
  }));

  console.log(JSON.stringify({ res, mobRes, errors: errors.slice(0, 10), notFound: notFound.slice(0, 5) }, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
