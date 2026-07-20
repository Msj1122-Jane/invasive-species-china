#!/usr/bin/env python3
"""Restore radar chart with species selector - using line-based replacement."""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ============================================================
# 1. CSS: Replace lines 890-1227 (gallery CSS) with radar CSS
# ============================================================

# Verify what's on those lines
print(f'Line 890: {lines[889][:60]}...')
print(f'Line 1218: {lines[1217][:60]}...')
print(f'Line 1228: {lines[1227][:60]}...')
print(f'Line 1229: {lines[1228][:60]}...')

# Find the exact end of gallery CSS (first non-gallery declaration after .gallery-kb-hint)
css_end = None
for i in range(1218, len(lines)):
    if lines[i].strip() == '':
        continue
    if '.gallery' not in lines[i]:
        css_end = i
        break

print(f'Gallery CSS end at line: {css_end + 1}')

new_radar_css = '''/* ---- Species Radar Comparison ---- */
.radar-compare-section {
  width: 100%;
  padding: 60px 40px 80px;
  max-width: 1400px;
  margin: 0 auto;
}
.radar-compare-section .section-number {
  color: var(--b-gold); font-size: 0.75rem; letter-spacing: 0.15em;
  margin-bottom: 8px; font-family: var(--font-system);
}
.radar-header { text-align: center; margin-bottom: 36px; }
.radar-title {
  font-family: var(--font-serif);
  font-size: clamp(1.4rem, 3vw, 2.2rem);
  font-weight: 900; color: var(--b-text);
  letter-spacing: 0.02em; margin-bottom: 4px;
}
.radar-subtitle {
  font-size: 0.82rem; color: var(--b-text-dim); opacity: 0.75;
  max-width: 560px; margin: 0 auto;
}
.radar-prompt {
  font-size: 0.72rem; color: var(--b-gold); opacity: 0.65;
  margin-bottom: 16px;
  animation: pulse-text 3s ease-in-out infinite;
}
@keyframes pulse-text {
  0%,100%{opacity:0.45} 50%{opacity:0.9}
}
.radar-main {
  display: flex; gap: 32px;
  align-items: flex-start; flex-wrap: wrap;
}
.radar-chart-wrap {
  flex: 1 1 500px; min-width: 400px;
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--b-border);
  border-radius: 16px; padding: 20px; position: relative;
}
.radar-chart-wrap .chart-source {
  position: absolute; bottom: 12px; right: 16px;
  font-size: 0.62rem; color: var(--b-text-dim); opacity: 0.35;
}
.radar-sel-wrap {
  flex: 0 0 380px; min-width: 320px;
  display: flex; flex-direction: column; gap: 16px;
}

/* Selected tags */
.radar-sel-tags {
  display: flex; flex-wrap: wrap; gap: 8px; min-height: 36px;
  padding: 8px 12px;
  background: rgba(255,255,255,0.03);
  border: 1px dashed var(--b-border);
  border-radius: 10px;
}
.radar-sel-tags:empty::after {
  content: '点击下方物种名添加到雷达图中';
  color: var(--b-text-dim); opacity: 0.4; font-size: 0.72rem;
  padding: 4px 0;
}
.rst-tag {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 5px 10px; border-radius: 14px;
  font-size: 0.75rem; font-weight: 600; color: #fff;
  cursor: pointer; transition: transform 0.2s;
  animation: tagPop 0.3s ease;
}
@keyframes tagPop {
  0%{transform:scale(0.7);opacity:0} 70%{transform:scale(1.08)} 100%{transform:scale(1);opacity:1}
}
.rst-tag:hover { transform: scale(1.05); }
.rst-tag .rst-x { font-size: 0.65rem; opacity: 0.6; margin-left: 2px; }

/* Search & filters */
.radar-sel-controls {
  display: flex; gap: 8px; flex-wrap: wrap;
}
.radar-search {
  flex: 1; min-width: 180px;
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--b-border);
  color: var(--b-text);
  padding: 8px 14px; border-radius: 20px;
  font-size: 0.82rem; outline: none; font-family: var(--font-system);
  transition: border-color 0.3s;
}
.radar-search:focus { border-color: var(--b-accent); }
.radar-lv-btns {
  display: flex; gap: 6px;
}
.rs-lv-btn {
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--b-border);
  color: var(--b-text-dim);
  padding: 5px 10px; border-radius: 14px;
  font-size: 0.7rem; cursor: pointer;
  transition: all 0.2s; white-space: nowrap;
  font-family: var(--font-system);
}
.rs-lv-btn:hover { border-color: var(--b-gold); color: var(--b-text); }
.rs-lv-btn.active { background: var(--b-accent); border-color: var(--b-accent); color: #fff; font-weight: 600; }

/* Species list */
.radar-sel-list {
  max-height: 520px; overflow-y: auto;
  border: 1px solid var(--b-border);
  border-radius: 12px;
  background: rgba(255,255,255,0.02);
}
.radar-sel-list::-webkit-scrollbar { width: 4px; }
.radar-sel-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 2px; }
.rsl-group-title {
  padding: 8px 14px; font-size: 0.68rem; color: var(--b-gold);
  font-weight: 700; letter-spacing: 0.05em;
  background: rgba(255,255,255,0.03);
  position: sticky; top: 0; z-index: 2;
}
.rsl-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 9px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  cursor: pointer; transition: background 0.2s;
  font-size: 0.82rem;
}
.rsl-item:hover { background: rgba(255,255,255,0.06); }
.rsl-item.selected { background: rgba(220,38,38,0.12); }
.rsl-item.selected .rsl-name { color: var(--b-accent); }
.rsl-name { color: var(--b-text); font-weight: 500; flex: 1; }
.rsl-latin { color: var(--b-text-dim); font-style: italic; font-size: 0.7rem; opacity: 0.55; margin: 0 8px; }
.rsl-lv {
  font-size: 0.65rem; padding: 2px 6px; border-radius: 6px;
  font-weight: 600; white-space: nowrap;
}
.rsl-lv.lv1 { background: rgba(220,38,38,0.2); color: #EF4444; }
.rsl-lv.lv2 { background: rgba(245,158,11,0.2); color: #F59E0B; }
.rsl-lv.lv3 { background: rgba(59,130,246,0.2); color: #3B82F6; }
.rsl-lv.lv4 { background: rgba(16,185,129,0.2); color: #10B981; }
.rsl-lv.lv5 { background: rgba(148,163,184,0.2); color: #94A3B8; }

/* Responsive */
@media (max-width: 900px) {
  .radar-compare-section { padding: 40px 16px 60px; }
  .radar-main { flex-direction: column; }
  .radar-chart-wrap { min-width: 100%; }
  .radar-sel-wrap { flex: 1 1 auto; min-width: 100%; }
  .radar-sel-list { max-height: 300px; }
}

'''

# Replace CSS section
old_css_lines = ''.join(lines[889:css_end])
new_css_lines = new_radar_css
lines[889:css_end] = [new_css_lines]
print('[OK] CSS replaced (lines 890-' + str(css_end) + ')')

# ============================================================
# 2. HTML: Replace gallery HTML with radar HTML
# ============================================================
html_start = None
html_end = None
for i, line in enumerate(lines):
    if '<div class="gallery-stage" id="galleryStage">' in line:
        html_start = i
    if html_start and 'gallery-kb-hint' in line and '</div>' in line and i > html_start + 50:
        html_end = i
        break

if html_start is None or html_end is None:
    print(f'ERROR: Gallery HTML not found! Start: {html_start}, End: {html_end}')
    exit(1)

print(f'Gallery HTML: lines {html_start+1} to {html_end+1}')

new_radar_html = '''  <!-- ==================== 物种雷达对比图 ==================== -->
  <div class="radar-compare-section" id="radarCompareSection">
    <div class="section-number">Chapter 03</div>
    <div class="radar-header">
      <h2 class="radar-title">物种档案 · 五维雷达</h2>
      <p class="radar-subtitle">从扩散广度、危害等级、生态威胁、防治难度、监管紧迫度 5 个维度对比入侵物种</p>
      <p class="radar-prompt">▼ 点击下方物种名添加到雷达图中 ▼</p>
    </div>
    <div class="radar-main">
      <div class="radar-chart-wrap">
        <div id="radarChart" style="width:100%;height:460px;"></div>
        <div class="chart-source">数据来源：iPlant植物智外来入侵物种数据库(iflora) · 省级分布数据</div>
      </div>
      <div class="radar-sel-wrap">
        <div class="radar-sel-tags" id="radarSelTags"></div>
        <div class="radar-sel-controls">
          <input type="text" class="radar-search" id="radarSearch" placeholder="搜索物种名 / 拉丁名 / 科名...">
          <div class="radar-lv-btns" id="radarLvBtns">
            <button class="rs-lv-btn active" data-rlv="all">全部</button>
            <button class="rs-lv-btn" data-rlv="1">L1 恶性</button>
            <button class="rs-lv-btn" data-rlv="2">L2 严重</button>
            <button class="rs-lv-btn" data-rlv="3">L3 局部</button>
            <button class="rs-lv-btn" data-rlv="4">L4 一般</button>
            <button class="rs-lv-btn" data-rlv="5">L5 观察</button>
          </div>
        </div>
        <div class="radar-sel-list" id="radarSelList"></div>
      </div>
    </div>
  </div>
'''

old_html_lines = ''.join(lines[html_start:html_end+1])
lines[html_start:html_end+1] = [new_radar_html]
print('[OK] HTML replaced')

# ============================================================
# 3. renderChapter: replace renderSpeciesGallery() call
# ============================================================
for i, line in enumerate(lines):
    if 'renderSpeciesGallery();' in line and 'renderInvasionPyramid' in ''.join(lines[i-5:i+5]):
        lines[i] = line.replace('renderSpeciesGallery();', '          renderRadarCompare();')
        print(f'[OK] renderChapter case 3 updated (line {i+1})')
        break

# ============================================================
# 4. JS: Replace gallery JS with radar JS
# ============================================================
js_start = None
js_end = None
for i, line in enumerate(lines):
    if 'SPECIES GALLERY (Canvas Abstract Patterns)' in line:
        js_start = i
    if js_start and 'function renderInvasionPyramid' in line and i > js_start + 100:
        js_end = i - 2  # back to before the function
        break

if js_start is None or js_end is None:
    print(f'ERROR: Gallery JS not found! Start: {js_start}, End: {js_end}')
    exit(1)

print(f'Gallery JS: lines {js_start+1} to {js_end+1}')

new_radar_js = '''// ============================================
// CHAPTER 3: RADAR COMPARISON CHART
// ============================================
let _radarSpeciesData = [];
let _radarSelected = [];
let _radarFilterLevel = 'all';
let _radarMaxSelect = 5;

const _radarColors = ['#DC2626','#3B82F6','#F59E0B','#10B981','#8B5CF6','#EC4899','#14B8A6','#F97316'];

function renderRadarCompare() {
  if (!Data.species_341) return;
  _radarSpeciesData = Data.species_341;
  updateRadarChart();
  renderRadarSpeciesList();
  bindRadarControls();
}

function calcRadarValues(sp) {
  var lv = sp.level || 5;
  var pc = sp.province_count || 1;
  var hasHarm = (sp.harm_description || '') !== '';
  var hasCtrl = (sp.control_method || '') !== '';
  return [
    Math.min(5, ((pc - 1) / 33) * 4 + 1),
    (6 - lv),
    (6 - lv) * (hasHarm ? 1 : 0.6),
    (6 - lv) * (hasCtrl ? 0.9 : 0.5),
    (6 - lv) * 1.1
  ].map(function(v) { return Math.max(0.5, Math.min(5, v)); });
}

function updateRadarChart() {
  var el = document.getElementById('radarChart');
  if (!el) return;
  if (!window._radarChart) window._radarChart = echarts.init(el);
  
  var indicator = [
    { name: '扩散广度', max: 5 },
    { name: '危害等级', max: 5 },
    { name: '生态威胁', max: 5 },
    { name: '防治难度', max: 5 },
    { name: '监管紧迫度', max: 5 }
  ];
  
  var series;
  if (_radarSelected.length === 0) {
    series = [{
      type: 'radar',
      data: [{ value: [0,0,0,0,0], name: '请选择物种', symbol: 'none' }],
      lineStyle: { color: 'transparent' },
      itemStyle: { color: 'transparent' },
      areaStyle: { color: 'transparent' }
    }];
  } else {
    series = _radarSelected.map(function(sp, i) {
      return {
        type: 'radar',
        data: [{ value: calcRadarValues(sp), name: sp.name_cn }],
        symbol: 'circle', symbolSize: 6,
        lineStyle: { width: 2.5, color: _radarColors[i % _radarColors.length] },
        itemStyle: { color: _radarColors[i % _radarColors.length] },
        areaStyle: { color: _radarColors[i % _radarColors.length], opacity: 0.08 }
      };
    });
  }
  
  window._radarChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: function(p) {
        if (!p.value || p.value[0] === 0) return '';
        return '<strong>' + p.name + '</strong><br/>' +
          '扩散广度: ' + p.value[0].toFixed(1) + '<br/>' +
          '危害等级: ' + p.value[1].toFixed(1) + '<br/>' +
          '生态威胁: ' + p.value[2].toFixed(1) + '<br/>' +
          '防治难度: ' + p.value[3].toFixed(1) + '<br/>' +
          '监管紧迫度: ' + p.value[4].toFixed(1);
      }
    },
    legend: {
      data: _radarSelected.map(function(s) { return s.name_cn; }),
      bottom: 0, textStyle: { color: '#94A3B8', fontSize: 12 },
      itemWidth: 12, itemHeight: 12, icon: 'circle'
    },
    radar: {
      indicator: indicator,
      center: ['50%', '50%'], radius: '65%',
      axisName: { color: '#94A3B8', fontSize: 11, borderRadius: 3, padding: [3, 5] },
      splitArea: { areaStyle: { color: ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.01)'] } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
    },
    series: series
  });
  
  renderRadarTags();
}

function renderRadarTags() {
  var tagsEl = document.getElementById('radarSelTags');
  if (!tagsEl) return;
  tagsEl.innerHTML = _radarSelected.map(function(sp, i) {
    var color = _radarColors[i % _radarColors.length];
    return '<span class="rst-tag" style="background:' + color + '" onclick="removeRadarSpecies(' + i + ')" title="点击移除">' +
      sp.name_cn + '<span class="rst-x">✕</span></span>';
  }).join('');
}

function removeRadarSpecies(i) {
  _radarSelected.splice(i, 1);
  updateRadarChart();
  renderRadarSpeciesList();
}

function addRadarSpecies(spid) {
  var sp = _radarSpeciesData.find(function(s) { return s.species_id === spid; });
  if (!sp) return;
  var already = _radarSelected.findIndex(function(s) { return s.species_id === spid; });
  if (already >= 0) {
    _radarSelected.splice(already, 1);
  } else {
    if (_radarSelected.length >= _radarMaxSelect) _radarSelected.shift();
    _radarSelected.push(sp);
  }
  updateRadarChart();
  renderRadarSpeciesList();
}

function renderRadarSpeciesList() {
  var listEl = document.getElementById('radarSelList');
  var searchInput = document.getElementById('radarSearch');
  if (!listEl) return;
  
  var searchTerm = (searchInput ? searchInput.value : '').toLowerCase().trim();
  
  var filtered = _radarSpeciesData;
  if (_radarFilterLevel !== 'all') {
    filtered = filtered.filter(function(s) { return s.level === parseInt(_radarFilterLevel); });
  }
  if (searchTerm) {
    filtered = filtered.filter(function(s) {
      return (s.name_cn || '').toLowerCase().indexOf(searchTerm) >= 0 ||
             (s.name_latin || '').toLowerCase().indexOf(searchTerm) >= 0 ||
             (s.family || '').toLowerCase().indexOf(searchTerm) >= 0;
    });
  }
  
  var groups = {};
  filtered.forEach(function(s) {
    var fam = s.family || '未知';
    if (!groups[fam]) groups[fam] = [];
    groups[fam].push(s);
  });
  
  var selectedIds = {};
  _radarSelected.forEach(function(s) { selectedIds[s.species_id] = true; });
  
  var html = '';
  var famNames = Object.keys(groups).sort(function(a, b) { return groups[b].length - groups[a].length; });
  famNames.forEach(function(fam) {
    html += '<div class="rsl-group-title">' + fam + ' (' + groups[fam].length + ')</div>';
    groups[fam].forEach(function(sp) {
      var isSel = selectedIds[sp.species_id];
      var lv = sp.level;
      html += '<div class="rsl-item' + (isSel ? ' selected' : '') + '" onclick="addRadarSpecies(' + sp.species_id + ')">';
      html += '<span class="rsl-name">' + sp.name_cn + '</span>';
      html += '<span class="rsl-latin">' + (sp.name_latin || '') + '</span>';
      html += '<span class="rsl-lv lv' + lv + '">L' + lv + '</span>';
      html += '</div>';
    });
  });
  
  if (html === '') {
    html = '<div style="padding:20px;text-align:center;color:var(--b-text-dim);opacity:0.5;font-size:0.82rem;">无匹配物种</div>';
  }
  listEl.innerHTML = html;
}

function bindRadarControls() {
  var lvBtns = document.querySelectorAll('#radarLvBtns .rs-lv-btn');
  lvBtns.forEach(function(btn) {
    btn.onclick = function() {
      _radarFilterLevel = this.dataset.rlv;
      lvBtns.forEach(function(b) { b.classList.remove('active'); });
      this.classList.add('active');
      renderRadarSpeciesList();
    };
  });
  
  var searchInput = document.getElementById('radarSearch');
  if (searchInput) searchInput.oninput = function() { renderRadarSpeciesList(); };
}

function resizeRadarChart() {
  if (window._radarChart) window._radarChart.resize();
}

'''

old_js_lines = ''.join(lines[js_start:js_end+1])
lines[js_start:js_end+1] = [new_radar_js]
print('[OK] JS replaced')

# ============================================================
# 5. Add radarChart to resize handler
# ============================================================
# Find the activateSection function
for i, line in enumerate(lines):
    if 'window._radarChart && window._radarChart.resize();' in line:
        print(f'[INFO] _radarChart resize already present (line {i+1})')
        break
    if 'window._pyramidChart' in line or 'window._famRankChart' in line:
        # Check nearby for _radarChart
        block = ''.join(lines[i:i+20])
        if '_radarChart' not in block:
            # Need to add
            lines.insert(i, '      window._radarChart && window._radarChart.resize();\n')
            print(f'[OK] Added _radarChart resize (before line {i+1})')
            break

# ============================================================
# Write back
# ============================================================
with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('\n=== ALL DONE ===')
# Verify
content_check = open('index.html', 'r', encoding='utf-8').read()
print(f'radarCompareSection: {"radarCompareSection" in content_check}')
print(f'renderRadarCompare: {"renderRadarCompare()" in content_check}')
print(f'addRadarSpecies: {"addRadarSpecies" in content_check}')
print(f'gallery-stage: {"gallery-stage" in content_check}')
print(f'renderSpeciesGallery: {"renderSpeciesGallery" in content_check}')
