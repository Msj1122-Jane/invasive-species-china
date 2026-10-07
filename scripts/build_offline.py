#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成离线版《来者何物》。

用法：python3 scripts/build_offline.py [输出目录]   默认输出到 offline/

离线版把所有 JSON 数据内联进 index.html，并用一个 fetch 垫片拦截对
data/*.json 的请求直接返回内联数据。这样双击 index.html（file:// 协议）
也能完整运行——浏览器在 file:// 下会拦截 fetch 读本地文件，内联可绕过。

图片、图表库仍是独立文件：<img> 和 <script src> 在 file:// 下正常工作。
"""
import json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, 'offline')

# 需要内联的数据：应用启动时加载的全部 JSON + 三份地图
DATA_FILES = [
    'data/overview.json', 'data/provinces.json', 'data/species.json',
    'data/species_341.json', 'data/species_images.json',
    'data/customs_cases_full.json', 'data/red_fire_ant.json',
    'data/economic_loss.json', 'data/customs_cases.json', 'data/pathway.json',
    'data/control.json', 'data/timeline.json', 'data/total_species_trend.json',
    'data/defense_rings.json', 'data/report_guide.json',
    'data/invasion_timeline.json', 'data/county_invasion.json',
    'data/customs_visual.json',
    'data/geo/china.json', 'data/geo/china-full.json', 'data/geo/world.json',
]
COPY_DIRS = ['assets', 'vendor']
COPY_FILES = ['methodology.html', 'favicon.svg']

SHIM = """<script>
/* 离线版：数据已内联，拦截对本地 JSON 的 fetch 直接返回，
   这样用 file:// 双击打开也能完整运行。由 scripts/build_offline.py 生成。 */
window.__OFFLINE_DATA__ = __PAYLOAD__;
(function () {
  var real = window.fetch ? window.fetch.bind(window) : null;
  window.fetch = function (input, init) {
    var url = (typeof input === 'string') ? input : (input && input.url) || '';
    var key = String(url).replace(/^\\.\\//, '').split('?')[0].split('#')[0];
    if (Object.prototype.hasOwnProperty.call(window.__OFFLINE_DATA__, key)) {
      var d = window.__OFFLINE_DATA__[key];
      return Promise.resolve({
        ok: true, status: 200,
        json: function () { return Promise.resolve(d); },
        text: function () { return Promise.resolve(JSON.stringify(d)); }
      });
    }
    if (!real) return Promise.reject(new Error('offline: ' + key));
    return real(input, init);
  };
})();
</script>
"""

def main():
    missing = [f for f in DATA_FILES if not os.path.exists(os.path.join(ROOT, f))]
    if missing:
        sys.exit('缺少数据文件：\n  ' + '\n  '.join(missing))

    payload = {}
    for rel in DATA_FILES:
        with open(os.path.join(ROOT, rel), encoding='utf-8') as fh:
            payload[rel] = json.load(fh)

    with open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='') as fh:
        html = fh.read()

    blob = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    # </script> 出现在数据里会提前闭合脚本块
    blob = blob.replace('</', '<\\/')
    shim = SHIM.replace('__PAYLOAD__', blob)

    anchor = '</head>'
    assert html.count(anchor) >= 1, '未找到 </head>'
    html = html.replace(anchor, shim + anchor, 1)

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8', newline='') as fh:
        fh.write(html)
    for d in COPY_DIRS:
        src = os.path.join(ROOT, d)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(OUT, d))
    for f in COPY_FILES:
        src = os.path.join(ROOT, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT, f))

    total = sum(os.path.getsize(os.path.join(dp, n))
                for dp, _, ns in os.walk(OUT) for n in ns)
    print(f'离线版已生成：{OUT}')
    print(f'  内联数据 {len(payload)} 份，共 {len(blob)/1024/1024:.1f} MB')
    print(f'  index.html {os.path.getsize(os.path.join(OUT, "index.html"))/1024/1024:.1f} MB')
    print(f'  整个文件夹 {total/1024/1024:.0f} MB')
    print('  用法：把整个文件夹拷走，双击 index.html 即可，无需联网')

if __name__ == '__main__':
    main()
