// Accessibility + meta audit
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const imgs = [...html.matchAll(/<img[^>]*>/g)].map(m => m[0]);
const noAlt = imgs.filter(i => !/alt\s*=/.test(i));
const emptyAlt = imgs.filter(i => /alt\s*=\s*""/.test(i));
const descriptiveAlt = imgs.filter(i => {
  const m = i.match(/alt="([^"]+)"/);
  return m && m[1].trim().length >= 4;
});
console.log('img tags:', imgs.length);
console.log('无 alt 属性:', noAlt.length);
console.log('空 alt:', emptyAlt.length);
console.log('描述性 alt(>=4字):', descriptiveAlt.length);
console.log('button 总数:', (html.match(/<button/g) || []).length);
console.log('aria-label 出现次数:', (html.match(/aria-label=/g) || []).length);
console.log('aria-hidden:', (html.match(/aria-hidden=/g) || []).length);
console.log('--- head meta ---');
const meta = [...html.matchAll(/<meta[^>]*>/g)].map(m => m[0]);
meta.forEach(m => console.log(m.slice(0, 150)));
console.log('--- 语义化 ---');
console.log('main:', (html.match(/<main/g) || []).length, '| article:', (html.match(/<article/g) || []).length, '| figure:', (html.match(/<figure/g) || []).length, '| nav:', (html.match(/<nav/g) || []).length);
console.log('h1 数:', (html.match(/<h1[ >]/g) || []).length, '| h2 数:', (html.match(/<h2[ >]/g) || []).length, '| h3 数:', (html.match(/<h3[ >]/g) || []).length);
