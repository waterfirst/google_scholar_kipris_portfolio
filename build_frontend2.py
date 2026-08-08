# -*- coding: utf-8 -*-
import sys,io;sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
import json

with open('portfolio_data.json','r',encoding='utf-8') as f: DATA=json.load(f)
DATA_JS=json.dumps(DATA,ensure_ascii=False)

# Use __DATA__ placeholder instead of f-string to avoid brace issues
with open('frontend_template.html','r',encoding='utf-8') as f:
    template=f.read()

html=template.replace('__PORTFOLIO_DATA__',DATA_JS)

out='frontend/index.html'
with open(out,'w',encoding='utf-8') as f: f.write(html)
print(f'OK: {out} ({len(html):,} bytes)')
print(f'Has {{{{: {html.count("{{")}')
print(f'Has lang===: {"lang===" in html}')
