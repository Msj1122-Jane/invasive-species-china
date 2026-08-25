# -*- coding: utf-8 -*-
"""
原产地字段清洗：把 iflora 自由文本 origin 归入 8 个洲级区域 + 跨洲/泛化 + 未知。
规则原则：
1) 跨大洲组合（如"欧洲、西亚和北非"）不硬塞单洲，归"跨洲/泛化"；
2) 仅写"美洲"未细分南北者，归"跨洲/泛化"，不与南北美洲并列（P0 修正）；
3) "热带美洲"（新热带区）为数据库原始标注、学界通行原产地类别，单列一行；
4) 中美洲、加勒比在地理上属北美洲，归入"北美洲"；
5) "不详/不明"归"未知"；
6) 原产中国/国内区域的记录归"亚洲"，但在清洗报告中单独标注存疑。
"""
import json, re, collections, shutil, sys

CROSS = {
    # 跨大洲 / 泛化标注（逐一审核）
    '美洲', '美洲温带地区', '欧亚大陆', '广泛分布于欧亚各国',
    '欧洲、西亚和北非', '欧洲、亚洲西南部', '欧洲、中亚、俄罗斯等地',
    '欧亚地区里海、阿拉海、哈萨克斯坦等地', '里海、黑海、波罗的海、阿拉伯海、爱琴海等地',
    '非洲、中东等地', '印度至非洲北部', '热带非洲、热带亚洲', '可能是热带非洲或亚洲热带地区',
    '热带和亚热带', '北美洲、南美洲和亚洲', '欧洲伊比利亚半岛和非洲西北部',
    '亚洲、非洲、欧洲、大洋洲、美洲', '中美洲和南美洲', '南美洲、墨西哥和西印度群岛',
    '南美洲、墨西哥', '非洲、阿拉伯半岛、墨西哥和南美洲',
    '从欧洲的西班牙半岛(包括西班牙、葡萄牙)、法国到亚洲东部(北到外贝加尔和蒙古，中国东部、中部和北部，朝鲜和日本)，为各地留鸟',
    '北太平洋沿岸高纬度地区', '中国东北、日本、朝鲜、俄罗斯远东及北美太平洋沿岸地带',
    '东亚、北美洲', '澳大利亚、新西兰、阿根廷、智利', '大洋洲至太平洋岛屿',
    '北半球温带地区', '北非、中亚、西亚和欧洲', '西亚至南欧', '西亚、中亚及地中海',
    '南欧、西亚', '中亚、西亚至南欧', '中亚和西亚', '西亚和地中海地区', '西亚、欧洲',
    '西亚和欧洲', '欧洲至西亚', '欧洲、西亚', '欧洲和西亚', '欧洲、亚洲西部',
    '中亚、西亚、北非和欧洲', '中亚、西亚、北非、欧洲', '欧洲、亚洲', '亚洲、欧洲',
    '印度、非洲', '热带亚洲和非洲', '热带非洲、热带亚洲',
    '南美洲、墨西哥和西印度群岛', '美洲、南美洲和西印度半岛',
    '亚洲泛热带地区', '非洲、亚洲', '大洋洲至太平洋岛屿', '不丹、印度及中亚',
    '南亚、中亚至南欧', '印度、巴基斯坦', '东南亚和印度', '南亚、东南亚',
    '欧洲、西亚、北非', '欧洲和地中海地区',
}
EUROPE_EXACT = {
    '欧洲', '欧洲(法国)', '欧洲(希腊等地)', '意大利', '大不列颠岛', '最早报道在英国',
    '俄罗斯', '南欧地中海地区', '欧洲地中海地区', '欧洲和地中海沿岸', '地中海地区',
    '地中海沿岸地区', '地中海', '地中海沿岸',
}
RULES = [
    ('未知', re.compile(r'不详|不明')),
    ('热带美洲', re.compile(r'热带美洲|美洲热带')),
    ('北美洲', re.compile(r'中美|北美|美国|墨西哥|加勒比|西印度群岛|古巴')),
    ('南美洲', re.compile(r'南美|巴西|阿根廷|秘鲁|圭亚那|智利')),
    ('大洋洲', re.compile(r'澳大利亚|新西兰|大洋洲')),
    ('非洲', re.compile(r'非洲|马达加斯加|安哥拉|南非|赞比西|东非')),
    ('亚洲', re.compile(r'亚洲|中国|日本|印度|东南亚|南亚|西亚|中亚|东洋|马来西亚|印度尼西亚|越南|韩国|朝鲜|蒙古|巴基斯坦|孟加拉|尼泊尔|斯里兰卡|缅甸|老挝|柬埔寨|泰国|东亚|广东|东北|华北|华东|华中|兴凯湖|西北太平洋')),
]
# "欧洲"关键词放最后检查，避免"欧洲、西亚和北非"这类被截胡（已在 CROSS 中）

def classify(o):
    if not o:
        return '未知'
    o = o.strip()
    if RULES[0][1].search(o):
        return '未知'
    if o in CROSS:
        return '跨洲/泛化'
    if o in EUROPE_EXACT:
        return '欧洲'
    for name, pat in RULES[1:]:
        if pat.search(o):
            return name
    if '欧洲' in o or '地中海' in o:
        return '欧洲'
    if o == '美洲':
        return '跨洲/泛化'
    return None

def main():
    files = ['data/species.json', 'data/species_341.json']
    all_origins = collections.Counter()
    datasets = {}
    for f in files:
        with open(f, encoding='utf-8') as fh:
            datasets[f] = json.load(fh)
        for x in datasets[f]:
            all_origins[(x.get('origin') or '').strip()] += 1

    unmapped = [o for o in all_origins if classify(o) is None]
    if unmapped:
        print('UNMAPPED:', unmapped)
        sys.exit(1)

    # 导出映射表
    mapping = {o: classify(o) for o in sorted(all_origins)}
    with open('data/origin_region_map.json', 'w', encoding='utf-8') as fh:
        json.dump(mapping, fh, ensure_ascii=False, indent=1)

    # 备份并写回
    for f in files:
        shutil.copy(f, f + '.bak')
        for x in datasets[f]:
            x['origin_region'] = classify(x.get('origin') or '')
        with open(f, 'w', encoding='utf-8') as fh:
            json.dump(datasets[f], fh, ensure_ascii=False)

    # 输出核对表
    for f in files:
        rows = collections.Counter(x['origin_region'] for x in datasets[f])
        print(f, dict(rows.most_common()))
    print('origins mapped:', len(mapping))

if __name__ == '__main__':
    main()
