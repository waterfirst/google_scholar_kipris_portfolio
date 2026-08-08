# -*- coding: utf-8 -*-
"""Parse Excel patent data fully, save as JSON"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json, zipfile
from xml.etree import ElementTree as ET

z = zipfile.ZipFile('patent_nakcho_choi_20260808.xlsx', 'r')
ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

# Shared strings
with z.open('xl/sharedStrings.xml') as f:
    sstree = ET.fromstring(f.read().decode('utf-8'))
strings = []
for si in sstree.findall('.//s:si', ns):
    t = si.find('s:t', ns)
    strings.append(t.text if t is not None and t.text else '')

# Parse all rows
with z.open('xl/worksheets/sheet1.xml') as f:
    sheet = ET.fromstring(f.read().decode('utf-8'))

sd = sheet.find('s:sheetData', ns)
all_rows = []

for row in sd.findall('s:row', ns):
    r_num = int(row.get('r', '0'))
    cells_data = {}
    for cell in row.findall('s:c', ns):
        ref = cell.get('r', '')
        col_letter = ''.join(c for c in ref if c.isalpha())
        col_idx = 0
        for c in col_letter:
            col_idx = col_idx * 26 + (ord(c) - ord('A') + 1)
        col_idx -= 1
        
        v_el = cell.find('s:v', ns)
        cell_type = cell.get('t', '')
        if v_el is not None and v_el.text:
            val = v_el.text
            if cell_type == 's':
                try:
                    val = strings[int(val)]
                except:
                    pass
            cells_data[col_idx] = val

    # Build row list
    if cells_data:
        max_c = max(cells_data.keys())
        row_list = [str(cells_data.get(i, '')) for i in range(max_c + 1)]
        all_rows.append({'row_num': r_num, 'data': row_list})

z.close()

# Find the header row (row 6 or 7 typically)
print(f"Total rows: {len(all_rows)}")
for r in all_rows[:12]:
    print(f"  Row {r['row_num']}: {r['data'][:8]}... ({len(r['data'])} cols)")

# Extract headers and data
# Usually row 6 or 7 is the header row in KIPRIS export
header_row = None
for r in all_rows:
    row_text = ' '.join(r['data'])
    if '발명의명칭' in row_text or '출원번호' in row_text or 'IPC' in row_text:
        header_row = r
        break

if header_row:
    headers = header_row['data']
    print(f"\nHeaders (row {header_row['row_num']}):")
    for i, h in enumerate(headers):
        if h.strip():
            print(f"  [{i}] {h}")
    
    # Extract data rows (rows after header)
    data_rows = []
    start_found = False
    for r in all_rows:
        if r['row_num'] == header_row['row_num']:
            start_found = True
            continue
        if start_found:
            row_data = r['data']
            # Pad to match headers
            while len(row_data) < len(headers):
                row_data.append('')
            data_rows.append(row_data)
    
    print(f"\nData rows: {len(data_rows)}")
    for row in data_rows[:3]:
        # Print key fields
        print(f"  번호={row[3][:30] if len(row)>3 else '?'} | 명칭={row[5][:60] if len(row)>5 else '?'} | 출원번호={row[9][:20] if len(row)>9 else '?'} | 등록번호={row[13][:20] if len(row)>13 else '?'} | 출원인={row[11][:30] if len(row)>11 else '?'}")

    # Save
    output = {
        'headers': headers,
        'data': data_rows,
        'total': len(data_rows)
    }
    with open('patent_data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved patent_data.json ({len(data_rows)} patents)")
else:
    print("Header row not found. Dumping all rows...")
    for r in all_rows[:20]:
        print(f"  Row {r['row_num']}: {r['data'][:6]}")
