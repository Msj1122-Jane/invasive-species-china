// Quick asset reference check
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const checks = ['red-fire-ant-april-nobile', 'Scientific_illustration', 'Scientific_botanical', 'species/', 'cases/', 'timeline/', 'spread/', 'generated-images'];
checks.forEach(c => {
  const re = new RegExp(c.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
  const n = (html.match(re) || []).length;
  console.log(c + ':', n, '处引用');
});
// What image files does the atlas actually use? sample
const m = JSON.parse(fs.readFileSync('data/species_images.json', 'utf8'));
const vals = Object.values(m).flat().filter(Boolean);
console.log('atlas 引用图片示例:', vals.slice(0, 3));
console.log('atlas 图片目录分布: species/', vals.filter(v => v.includes('species/')).length);
