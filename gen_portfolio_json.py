# -*- coding: utf-8 -*-
"""Generate unified portfolio JSON for Vue.js web app"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json, re

# Load GS data
with open('scholar_analysis.json', 'r', encoding='utf-8') as f:
    gs = json.load(f)

# Load KIPRIS data
with open('patent_data.json', 'r', encoding='utf-8') as f:
    kp_raw = json.load(f)

# Parse KIPRIS
kp_headers = kp_raw['headers']
kp_data = kp_raw['data']
kp_patents = []
for row in kp_data:
    p = {}
    for i, h in enumerate(kp_headers):
        p[h] = row[i] if i < len(row) else ''
    kp_patents.append(p)

# Name patterns for lead inventor
name_re = re.compile(
    r'\bNC\s*CHOI\b|\bNC\s*Choi\b|\bN\s*CHOI\b|\bN\s*Choi\b|'
    r'\bC\s*Nakcho\b|\bNakcho\s*Choi\b|\bChoi\s*Nak\s*Cho\b|'
    r'\bKL\s*Nakcho\s*Choi\b|\bNak\s*Cho\s*Choi\b', re.IGNORECASE)

def is_lead(au):
    if not au: return False
    return bool(name_re.search(au.split(',')[0].strip()))

# Process GS publications
us_patents = []
papers = []
for p in gs['publications']:
    venue = p.get('venue', '').lower()
    is_pat = any(k in venue for k in ['patent', 'app.', 'application'])
    cls = p.get('classification', {})
    item = {
        'title': p.get('title', ''),
        'year': p.get('year_int', 0) or int(p.get('year', '0') or '0'),
        'cites': p.get('citations_int', 0) or int(p.get('citations', '0') or '0'),
        'authors': p.get('authors', ''),
        'venue': p.get('venue', ''),
        'tech': cls.get('primary_tech', 'Other') if isinstance(cls, dict) else str(cls),
        'lead': is_lead(p.get('authors', '')),
    }
    if is_pat:
        us_patents.append(item)
    else:
        papers.append(item)

# Process KIPRIS patents
def parse_kr_year(d):
    if not d: return 0
    parts = str(d).replace('-','.').split('.')
    return int(parts[0]) if parts and parts[0].isdigit() else 0

def ipc_tech(ipc_str):
    if not ipc_str: return 'Other'
    for part in str(ipc_str).split('|'):
        part = part.strip()
        parts = part.split()
        if parts and len(parts[0]) >= 3:
            code = parts[0][:4]
            mapping = {'G02F':'LCD','H10K':'OLED','H10H':'Micro LED',
                       'H10D':'TFT','H01L':'TFT','G09G':'Driving',
                       'G09F':'Panel','G06F':'Touch','H05B':'Display'}
            return mapping.get(code, code)
    return 'Other'

kr_patents = []
for p in kp_patents:
    inventors = p.get('발명자', '')
    lead = False
    if inventors:
        first = inventors.split('|')[0].strip() if '|' in inventors else inventors[:10]
        lead = '최낙초' in first or name_re.search(first)
    kr_patents.append({
        'title': p.get('발명의명칭', ''),
        'title_en': p.get('발명의명칭(영문)', ''),
        'year': parse_kr_year(p.get('출원일자', '')),
        'app_number': p.get('출원번호', ''),
        'app_date': p.get('출원일자', ''),
        'reg_number': p.get('등록번호', ''),
        'reg_date': p.get('등록일자', ''),
        'status': '등록' if '등록' in str(p.get('법적상태','')) else ('공개' if '공개' in str(p.get('법적상태','')) else '기타'),
        'ipc': p.get('IPC분류', ''),
        'applicant': p.get('출원인', ''),
        'tech': ipc_tech(p.get('IPC분류', '')),
        'lead': lead,
    })

# Profile
profile = gs['profile']
try: h_idx = int(profile['stats'].get('h-index', 14))
except: h_idx = 14
try: i10_idx = int(profile['stats'].get('i10-index', 22))
except: i10_idx = 22
try: total_cites = int(profile['stats'].get('서지정보', 813))
except: total_cites = 813

# Stats
kr_tech_counts = {}
for p in kr_patents:
    kr_tech_counts[p['tech']] = kr_tech_counts.get(p['tech'], 0) + 1

us_tech_counts = {}
for p in us_patents:
    us_tech_counts[p['tech']] = us_tech_counts.get(p['tech'], 0) + 1

kr_yearly = {}
for p in kr_patents:
    if p['year'] > 0:
        kr_yearly[p['year']] = kr_yearly.get(p['year'], 0) + 1

us_yearly = {}
for p in us_patents:
    if p['year'] > 0:
        us_yearly[p['year']] = us_yearly.get(p['year'], 0) + 1

paper_yearly = {}
for p in papers:
    if p['year'] > 0:
        paper_yearly[p['year']] = paper_yearly.get(p['year'], 0) + 1

# Build unified data
unified = {
    'profile': {
        'name': 'Nak Cho Choi (최낙초)',
        'name_en': 'Nak Cho Choi',
        'affiliation': 'Samsung Display, Principal Engineer',
        'affiliation_ko': '삼성디스플레이, 수석연구원',
        'fields': profile.get('fields', []),
        'stats': {
            'h_index': h_idx,
            'i10_index': i10_idx,
            'total_cites': total_cites,
            'kr_patents': len(kr_patents),
            'us_patents': len(us_patents),
            'papers': len(papers),
            'total': len(kr_patents) + len(us_patents) + len(papers),
        }
    },
    'kr_patents': sorted(kr_patents, key=lambda x: x['year'], reverse=True),
    'us_patents': sorted(us_patents, key=lambda x: x['year'], reverse=True),
    'papers': sorted(papers, key=lambda x: x['year'], reverse=True),
    'charts': {
        'kr_tech': kr_tech_counts,
        'us_tech': us_tech_counts,
        'kr_yearly': kr_yearly,
        'us_yearly': us_yearly,
        'paper_yearly': paper_yearly,
    }
}

with open('portfolio_data.json', 'w', encoding='utf-8') as f:
    json.dump(unified, f, ensure_ascii=False, indent=2)

print(f"✅ portfolio_data.json generated")
print(f"   KR Patents: {len(kr_patents)}")
print(f"   US Patents: {len(us_patents)}")
print(f"   Papers: {len(papers)}")
print(f"   Total: {len(kr_patents) + len(us_patents) + len(papers)}")
print(f"   KR Tech: {kr_tech_counts}")
