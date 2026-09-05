# -*- coding: utf-8 -*-
"""Extract embedded images from 图鉴缺图采集表.xlsx, mapped to species rows."""
import zipfile, re, os, sys
import xml.etree.ElementTree as ET
import openpyxl

XLSX = r'C:\Users\lenovo\Downloads\图鉴缺图采集表.xlsx'
OUT = r'D:\OneDrive\Desktop\专题新闻\invasive-species-china\data_raw\collected_images'
os.makedirs(OUT, exist_ok=True)

NS = {
    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}

z = zipfile.ZipFile(XLSX)

# 1. drawing rels: rId -> media file
rels = ET.fromstring(z.read('xl/drawings/_rels/drawing1.xml.rels'))
rid2file = {}
for rel in rels:
    rid2file[rel.get('Id')] = 'xl/drawings/' + rel.get('Target')

# 2. anchors: (row, col) -> media file
drawing = ET.fromstring(z.read('xl/drawings/drawing1.xml'))
anchors = []  # (from_row, from_col, media)
for anchor in drawing:
    frm = anchor.find('xdr:from', NS)
    if frm is None:
        continue
    row = int(frm.find('xdr:row', NS).text)
    col = int(frm.find('xdr:col', NS).text)
    blip = anchor.find('.//a:blip', NS)
    if blip is None:
        continue
    rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    if rid and rid in rid2file:
        anchors.append((row, col, rid2file[rid]))

# 3. read sheet rows: row index (0-based) -> species info
wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb['缺图清单']
# find header row
rows = list(ws.iter_rows(values_only=True))
# headers: row index 1 (#, 中文名, 拉丁学名...) is 0-based row 1
species_by_row = {}
for i, row in enumerate(rows):
    if row[2] and row[3] and str(row[2]).strip() not in ('', '中文名'):
        cn = str(row[2]).strip()
        latin = str(row[3]).strip()
        species_by_row[i] = (cn, latin)

print('anchors:', len(anchors), 'species rows:', len(species_by_row))

# 4. extract: image anchored in row r belongs to species at row r (or nearest above with same anchor col)
manifest = []
for (row, col, media) in sorted(anchors):
    # find species for this row: use the species whose row index == row-? 
    # images anchored slightly below the species row; find nearest species row <= row
    cand = None
    for r in species_by_row:
        if r <= row and (cand is None or r > cand):
            cand = r
    if cand is None:
        continue
    cn, latin = species_by_row[cand]
    ext = os.path.splitext(media)[1]
    idx = sum(1 for m in manifest if m['cn'] == cn) + 1
    fname = f"{latin.replace(' ', '_')}_{idx}{ext}"
    with open(os.path.join(OUT, fname), 'wb') as f:
        f.write(z.read(media))
    manifest.append({'cn': cn, 'latin': latin, 'file': fname, 'anchor_row': row, 'col': col})

# summary
from collections import Counter
c = Counter(m['cn'] for m in manifest)
print('species with images:', len(c))
for cn, n in c.most_common(10):
    print(' ', cn, n)

# which of the 83 have images?
all_species = set(v[0] for v in species_by_row.values())
missing = all_species - set(c.keys())
print('still missing images:', len(missing))
for m in sorted(missing):
    print('  MISS', m)

import json
with open(os.path.join(OUT, '_manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)
print('manifest written, total images:', len(manifest))
