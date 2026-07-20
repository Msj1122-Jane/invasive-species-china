# -*- coding: utf-8 -*-
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_start = content.find('// ============================================\n// CHAPTER 3: SUNBURST CHART')
old_end = content.find('// CHAPTER 4: IMPACT')

if old_start == -1 or old_end == -1:
    print(f'ERROR: old_start={old_start}, old_end={old_end}')
    sys.exit(1)

new_js = r'''// ============================================
// CHAPTER 3: SPECIES GALLERY (Horizontal Scroll)
// ============================================

let _galleryData = [];
let _galleryFilter = 'level1';
let _galleryIdx = 0;

function renderSpeciesGallery() {
  if (!Data.species) return;
  _galleryData = Data.species;
  var familyColors = {
    '菊科': ['#8B4513', '#A0522D', '#6B3A2E', '#CD853F', '#D2691E'],
    '苋科': ['#DC143C', '#B22222', '#8B0000', '#CD5C5C', '#F08080'],
    '禾本科': ['#228B22', '#2E8B57', '#3CB371', '#6B8E23', '#556B2F'],
    '旋花科': ['#DA70D6', '#BA55D3', '#9370DB', '#8B008B', '#9932CC'],
    '豆科': ['#FFD700', '#DAA520', '#B8860B', '#FFA500', '#F4A460'],
    '马鞭草科': ['#FF6347', '#FF4500', '#E74C3C', '#FF7F50', '#FA8072'],
    '雨久花科': ['#4682B4', '#5F9EA0', '#6495ED', '#4169E1', '#7B68EE'],
    '莎草科': ['#20B2AA', '#48D1CC', '#40E0D0', '#00CED1', '#008B8B'],
    '天南星科': ['#2F4F4F', '#556B2F', '#8FBC8F', '#6B8E23', '#3CB371'],
    '藜科': ['#A0522D', '#D2691E', '#F4A460', '#DEB887', '#CD853F'],
    '落葵科': ['#9ACD32', '#6B8E23', '#ADFF2F', '#7CFC00', '#32CD32'],
    '商陆科': ['#800080', '#9400D3', '#9932CC', '#8B008B', '#BA55D3'],
    '_default': ['#1B3A2F', '#2D5A47', '#3D7A5F', '#4D9A77', '#0F2A1E']
  };

  var cardsContainer = document.getElementById('galleryCards');
  var track = document.getElementById('galleryTrack');
  var dotsContainer = document.getElementById('galleryDots');
  if (!cardsContainer) return;

  var filtered = _galleryData;
  if (_galleryFilter === 'level1') filtered = _galleryData.filter(function(s) { return s.level === '1级' || s.level === '1'; });
  else if (_galleryFilter === 'animal') filtered = _galleryData.filter(function(s) { return s.category === 'animal'; });
  else if (_galleryFilter === 'plant') filtered = _galleryData.filter(function(s) { return s.category === 'plant'; });

  var total = filtered.length;
  document.getElementById('gcTotal').textContent = String(total).padStart(2, '0');
  _galleryIdx = 0;
  document.getElementById('gcCurrent').textContent = '01';

  cardsContainer.innerHTML = '';
  dotsContainer.innerHTML = '';

  filtered.forEach(function(sp, i) {
    var lv = String(sp.level || '1').replace(/级$/, '');
    var fam = sp.family || '';
    var colors = familyColors[fam] || familyColors['_default'];
    var bg1 = colors[i % colors.length];
    var bg2 = colors[(i + 1) % colors.length];
    var distroPct = Math.min((sp.province_count || 1) / 35 * 100, 100);

    var card = document.createElement('div');
    card.className = 'gc-card';
    card.id = 'gCard' + i;
    card.innerHTML =
      '<div class="gc-image" style="background: linear-gradient(135deg, ' + bg1 + ' 0%, ' + bg2 + ' 100%);">' +
        '<div class="gc-image-placeholder">' +
          '<div class="gc-image-pattern" style="background: radial-gradient(circle, rgba(255,255,255,0.35) 0%, transparent 70%);"></div>' +
        '</div>' +
        '<div class="gc-prompt-hint" title="AI图像提示词">点击查看提示词</div>' +
      '</div>' +
      '<div class="gc-info">' +
        '<span class="gc-level-badge l' + lv + '">' + sp.level + '入侵物种</span>' +
        '<div class="gc-name-cn">' + sp.name_cn + '</div>' +
        '<div class="gc-name-la">' + (sp.name_latin || '') + '</div>' +
        '<div class="gc-meta">' +
          '<div class="gc-meta-item"><span class="gc-meta-label">科属</span><span class="gc-meta-value">' + fam + '</span></div>' +
          '<div class="gc-meta-item"><span class="gc-meta-label">原产地</span><span class="gc-meta-value">' + (sp.origin || '未知') + '</span></div>' +
          '<div class="gc-meta-item"><span class="gc-meta-label">类别</span><span class="gc-meta-value">' + (sp.category === 'animal' ? '动物' : '植物') + '</span></div>' +
        '</div>' +
        '<div class="gc-harm">' + (sp.harm ? (sp.harm.length > 160 ? sp.harm.substring(0, 157) + '...' : sp.harm) : '暂无危害描述') + '</div>' +
        '<div class="gc-distro">' +
          '<span class="gc-distro-label">分布省份</span>' +
          '<div class="gc-distro-bar"><div class="gc-distro-fill" style="width:' + distroPct + '%"></div></div>' +
          '<span class="gc-distro-num">' + (sp.province_count || 0) + '/35</span>' +
        '</div>' +
      '</div>';
    cardsContainer.appendChild(card);

    var dot = document.createElement('span');
    dot.className = 'gallery-dot' + (i === 0 ? ' active' : '');
    (function(idx) {
      dot.onclick = function() { scrollToCard(idx); };
    })(i);
    dotsContainer.appendChild(dot);
  });

  track.onscroll = updateActiveDot;
  updateActiveDot();
}

function scrollToCard(idx) {
  var card = document.getElementById('gCard' + idx);
  if (!card) return;
  card.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
  _galleryIdx = idx;
  document.getElementById('gcCurrent').textContent = String(idx + 1).padStart(2, '0');
  updateDots();
}

function updateActiveDot() {
  var track = document.getElementById('galleryTrack');
  var cards = document.querySelectorAll('.gc-card');
  if (!track || cards.length === 0) return;
  var center = track.scrollLeft + track.clientWidth / 2;
  var closest = 0, minDist = Infinity;
  cards.forEach(function(card, i) {
    var dist = Math.abs(card.offsetLeft + card.offsetWidth / 2 - center);
    if (dist < minDist) { minDist = dist; closest = i; }
  });
  _galleryIdx = closest;
  document.getElementById('gcCurrent').textContent = String(closest + 1).padStart(2, '0');
  updateDots();
}

function updateDots() {
  document.querySelectorAll('.gallery-dot').forEach(function(dot, i) {
    dot.classList.toggle('active', i === _galleryIdx);
  });
}

(function initGalleryNav() {
  setTimeout(function() {
    var left = document.getElementById('galleryLeft');
    var right = document.getElementById('galleryRight');
    if (!left || !right) return;
    left.onclick = function() {
      if (_galleryIdx > 0) scrollToCard(_galleryIdx - 1);
    };
    right.onclick = function() {
      var total = document.querySelectorAll('.gc-card').length;
      if (_galleryIdx < total - 1) scrollToCard(_galleryIdx + 1);
    };
  }, 800);
})();

document.addEventListener('keydown', function(e) {
  if (!document.getElementById('chapter-species').classList.contains('active')) return;
  if (e.key === 'ArrowLeft') {
    e.preventDefault();
    if (_galleryIdx > 0) scrollToCard(_galleryIdx - 1);
  } else if (e.key === 'ArrowRight') {
    e.preventDefault();
    var total = document.querySelectorAll('.gc-card').length;
    if (_galleryIdx < total - 1) scrollToCard(_galleryIdx + 1);
  }
});

setTimeout(function() {
  document.querySelectorAll('.gf-btn').forEach(function(btn) {
    btn.onclick = function() {
      document.querySelectorAll('.gf-btn').forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      _galleryFilter = btn.dataset.gf;
      renderSpeciesGallery();
    };
  });
}, 800);

setTimeout(function() {
  var track = document.getElementById('galleryTrack');
  if (!track) return;
  track.addEventListener('wheel', function(e) {
    if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
      e.preventDefault();
      track.scrollLeft += e.deltaY;
    }
  }, { passive: false });
}, 800);
'''

# Find and keep the original comment line
old_comment_end = content.find('\n', old_start) + 1
content = content[:old_start] + content[old_start:old_comment_end] + new_js + '\n' + content[old_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('DONE: Old species functions replaced')
print(f'Range replaced: {old_start} -> {old_end}')
print(f'New JS size: {len(new_js)} chars')
