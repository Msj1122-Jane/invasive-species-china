# -*- coding: utf-8 -*-
"""
从中国外来入侵物种数据库（iflora）抓取的入侵动物数据（invasion_animals.xlsx）
导入站点数据：

1. data/species.json  —— 补充缺失的动物/昆虫记录，并按 xlsx 修正已有记录
2. data/provinces.json —— 重算各省 animal（此前为编造值，如云南132种动物，
   远超全国入侵动物总数119种）；plant = total - animal 保持恒等式

用法：py -X utf8 scripts/import_invasion_animals.py [xlsx路径] [--apply]
默认仅打印审查报告，加 --apply 才写回文件。
"""
import json
import re
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("需要 openpyxl：py -m pip install openpyxl")

ROOT = Path(__file__).resolve().parent.parent
XLSX_DEFAULT = r"C:\Users\lenovo\WorkBuddy\2026-08-07-10-13-33\invasion_animals.xlsx"

# provinces.json 使用的省份名（台湾/香港/澳门无前缀）
PROVINCES = [
    "北京", "天津", "上海", "重庆", "河北", "河南", "山东", "山西", "陕西",
    "甘肃", "青海", "宁夏", "新疆", "西藏", "内蒙古", "黑龙江", "吉林", "辽宁",
    "江苏", "浙江", "安徽", "福建", "江西", "湖北", "湖南", "广东", "广西",
    "海南", "四川", "贵州", "云南", "台湾", "香港", "澳门",
]
# 长的先匹配，避免“黑龙江”被“龙江”之类截断（本表无此情况，保险起见）
PROVINCES_SORTED = sorted(PROVINCES, key=len, reverse=True)

INSECT_CLASSES = {"昆虫纲"}

# 等级归一：罗马数字 → 阿拉伯
LEVEL_FIX = {"Ⅰ": "1", "Ⅱ": "2", "Ⅲ": "3", "Ⅳ": "4", "Ⅴ": "5",
             "IV": "4", "I": "1", "II": "2", "III": "3", "V": "5"}


def norm_level(raw):
    if not raw:
        return None
    s = str(raw).strip()
    m = re.match(r"^([1-5一二三四五]|IV|III|II|I|V|Ⅰ|Ⅱ|Ⅲ|Ⅳ|Ⅴ)\s*级$", s)
    if m:
        token = m.group(1)
        token = LEVEL_FIX.get(token, token)
        cn = {"一": "1", "二": "2", "三": "3", "四": "4", "五": "5"}
        token = cn.get(token, token)
        return f"{token}级"
    return s  # 保留原样，报告里人工看


ALL_PROVINCES = set(PROVINCES)


def parse_distribution(text):
    """从「国内分布」自由文本解析省份集合与记录数。
    返回 (province_set, count_or_None, note)
    count 取值规则：显式数字 > 排除法（除…以外）> 干净列表计数 > None（下限不明）"""
    if not text or not str(text).strip():
        return set(), None, "空"
    t = str(text)
    note = ""
    # 显式总数：“等34个省级行政区”“遍布全国30多个省份”
    explicit = None
    m = re.search(r"(\d{1,2})\s*多?\s*个?(?:省级行政区|省份|省(?!份))", t)
    if m:
        explicit = int(m.group(1))
    # 排除法：“除甘肃、海南…以外的各省区”“几乎遍布于除新疆、西藏以外的所有省份”
    m_ex = re.search(r"除([^。；]{1,60}?)以?外", t)
    if m_ex:
        excluded = {p for p in PROVINCES_SORTED if p in m_ex.group(1)}
        found = ALL_PROVINCES - excluded
        return found, explicit or len(found), f"排除法：除{sorted(excluded)}外"
    # 特例：'中国北京以南地区均有养殖' 里的“北京”不是分布点
    t2 = re.sub(r"北京以南[^，。]*[，。]?", "", t)
    found = {p for p in PROVINCES_SORTED if p in t2}
    if explicit:
        if len(found) < explicit:
            note = f"显式{explicit}省，文本仅列出{len(found)}个"
        return found, explicit, note
    if not found:
        return found, None, "未解析出省份"
    # 列表后带“等”且无数字：真实范围大于列出项，计数不可考
    if re.search(r"等(?:省|省份|省区|地区|区域|多个|个|地)", t):
        return found, None, f"开放式列表（等），已列{len(found)}省"
    return found, len(found), note


def latin_key(latin):
    """取属+种加词做匹配键（忽略亚种、命名人）"""
    if not latin:
        return None
    parts = re.findall(r"[A-Za-z]+", str(latin))
    if len(parts) >= 2:
        return " ".join(parts[:2]).lower()
    return None


def load_xlsx(path):
    wb = openpyxl.load_workbook(path)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    headers = [str(h).strip() if h else "" for h in rows[0]]
    out = []
    for r in rows[1:]:
        if not any(r):
            continue
        d = dict(zip(headers, r))
        out.append(d)
    return out


def main():
    xlsx_path = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else XLSX_DEFAULT
    apply = "--apply" in sys.argv

    raw = load_xlsx(xlsx_path)
    print(f"xlsx 记录数: {len(raw)}")

    records = []
    problems = []
    for d in raw:
        name = (d.get("中文名") or "").strip()
        if not name:
            continue
        provs, prov_count, note = parse_distribution(d.get("国内分布"))
        level = norm_level(d.get("入侵等级"))
        if level and not re.match(r"^[1-5]级$", level):
            problems.append(f"等级异常: {name} -> {d.get('入侵等级')!r}")
        rec = {
            "name_cn": name,
            "alias": (d.get("别名") or "").strip() or None,
            "name_latin": (d.get("规范学名") or "").strip() or None,
            "family": (d.get("中文科名") or "").strip() or None,
            "origin": (d.get("原产地") or "").strip().rstrip("。") or None,
            "level": level,
            "category": "insect" if (d.get("中文纲名") or "").strip() in INSECT_CLASSES else "animal",
            "province_count": prov_count,
            "provinces": sorted(provs),
            "harm": (d.get("入侵危害") or "").strip() or None,
            "_note": note,
        }
        records.append(rec)
        if note in ("空", "未解析出省份"):
            problems.append(f"分布{note}: {name} | {(d.get('国内分布') or '')[:60]}")

    # ---------- 审查报告 ----------
    print("\n===== 分布解析需人工复核 =====")
    for r in records:
        if r["_note"] and r["_note"] != "空":
            print(f"  {r['name_cn']}: {r['_note']} -> {r['provinces']}")
        elif r["_note"] == "空":
            print(f"  {r['name_cn']}: 国内分布为空")
    print("\n===== 其他问题 =====")
    for p in problems:
        print(" ", p)

    # ---------- 合并进 species.json ----------
    species_path = ROOT / "data" / "species.json"
    species = json.loads(species_path.read_text(encoding="utf-8"))
    by_latin = {}
    by_name = {}
    for s in species:
        k = latin_key(s.get("name_latin"))
        if k:
            by_latin.setdefault(k, s)
        by_name.setdefault(s.get("name_cn"), s)

    # 现有15种动物/昆虫/病害均已列入《重点管理外来入侵物种名录》（2023年59种）
    KEY_LIST = {"红火蚁", "美国白蛾", "草地贪夜蛾", "苹果蠹蛾", "红脂大小蠹", "稻水象甲",
                "松材线虫", "梨火疫病菌", "红耳彩龟", "克氏原螯虾", "福寿螺",
                "非洲大蜗牛", "鳄雀鳝", "美洲牛蛙", "豹纹翼甲鲶"}

    updated, added = [], []
    matched_key = set()
    for r in records:
        k = latin_key(r["name_latin"])
        target = by_latin.get(k) or by_name.get(r["name_cn"])
        # 别名也试试（如 xlsx「牛蛙」 vs 站点「美洲牛蛙」）
        if not target and r["alias"]:
            for alt in re.split(r"[、,，/]", r["alias"]):
                if alt.strip() in by_name:
                    target = by_name[alt.strip()]
                    break
        if not target:
            # 站点俗名 → xlsx 学名 的已知对应
            KNOWN = {"美洲牛蛙": "lithobates catesbeianus", "红耳彩龟": "trachemys scripta"}
            if r["name_cn"] in KNOWN and KNOWN[r["name_cn"]] in by_latin:
                target = by_latin[KNOWN[r["name_cn"]]]
        if target:
            changed = []
            matched_key.add(target["name_cn"])
            if r["province_count"] and target.get("province_count") != r["province_count"]:
                changed.append(f"province_count {target.get('province_count')}→{r['province_count']}")
                target["province_count"] = r["province_count"]
            # 等级语义统一为 iflora 入侵等级；名录身份用 key_list 标记
            if r["level"] and target.get("level") != r["level"]:
                changed.append(f"level {target.get('level')}→{r['level']}")
                target["level"] = r["level"]
            if r["family"] and not target.get("family"):
                target["family"] = r["family"]
                changed.append("补family")
            if target["name_cn"] in KEY_LIST:
                target["key_list"] = True
            if changed:
                updated.append(f"{target['name_cn']}（xlsx: {r['name_cn']}）: " + ", ".join(changed))
        else:
            new = {k2: v for k2, v in r.items() if not k2.startswith("_") and k2 != "provinces"}
            new["_provinces"] = r["provinces"]  # 暂存，供省份计数
            species.append(new)
            added.append(r["name_cn"])

    # 给名录物种打上 key_list；未被 xlsx 覆盖到的名录物种等级置空
    # （原“1级”是名录含义，与 iflora 入侵等级语义不同，不能混用）
    for s in species:
        if s.get("name_cn") in KEY_LIST:
            s["key_list"] = True
            if s["name_cn"] not in matched_key:
                s["level"] = None

    print(f"\n===== species.json =====")
    print(f"更新已有记录 {len(updated)} 条:")
    for u in updated:
        print(" ", u)
    print(f"新增记录 {len(added)} 条")
    from collections import Counter
    print("合并后分类:", Counter(s.get("category") for s in species), "总计", len(species))

    # ---------- 重算 provinces.json 的 animal ----------
    prov_path = ROOT / "data" / "provinces.json"
    provs = json.loads(prov_path.read_text(encoding="utf-8"))
    prov_names = [p["name"] for p in provs]
    print("\nprovinces.json 省份:", prov_names)

    animal_counter = Counter()
    # 用合并后的 species 列表统计（含新增），但只统计 xlsx 来源记录：
    # 直接遍历 records（含与已有记录匹配上的）
    for r in records:
        for p in r["provinces"]:
            animal_counter[p] += 1

    print("\n===== 各省动物种数（xlsx 明确点名的省份，下限值） =====")
    report = []
    for p in provs:
        name = p["name"]
        new_a = animal_counter.get(name, 0)
        old_a = p.get("animal", 0)
        report.append((name, old_a, new_a, p.get("total", 0)))
    for name, old_a, new_a, total in sorted(report, key=lambda x: -x[2]):
        flag = "  <-- 原值明显错误" if old_a > len(records) else ""
        print(f"  {name}: animal {old_a} -> {new_a} (total {total}){flag}")

    if not apply:
        print("\n（未加 --apply，未写回任何文件）")
        return

    # 写回 species.json（去掉暂存字段）
    for s in species:
        s.pop("_provinces", None)
    species_path.write_text(json.dumps(species, ensure_ascii=False, indent=2), encoding="utf-8")

    # 写回 provinces.json：animal 用解析值，plant = total - animal 保持恒等
    for p in provs:
        new_a = animal_counter.get(p["name"], 0)
        p["animal"] = new_a
        p["plant"] = p.get("total", 0) - new_a
    prov_path.write_text(json.dumps(provs, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n已写回 data/species.json 与 data/provinces.json")


if __name__ == "__main__":
    main()
