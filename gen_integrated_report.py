# -*- coding: utf-8 -*-
"""Integrated Report: Google Scholar + KIPRIS → Unified HTML"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json, base64, os, re, time
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request, urllib.parse, urllib.error

# ============================================================
# 1. LOAD ALL DATA
# ============================================================

# --- Google Scholar data (from analyzed file with year_int, cites_int, etc.) ---
with open('scholar_analysis.json', 'r', encoding='utf-8') as f:
    gs = json.load(f)
gs_pubs = gs['publications']
gs_profile = gs['profile']
# Ensure year_int, cites_int, primary_tech, lead, pub_type are present
import re as _re
_name_re = _re.compile(
    r'\bNC\s*CHOI\b|\bNC\s*Choi\b|\bN\s*CHOI\b|\bN\s*Choi\b|'
    r'\bC\s*Nakcho\b|\bNakcho\s*Choi\b|\bChoi\s*Nak\s*Cho\b|'
    r'\bKL\s*Nakcho\s*Choi\b|\bNak\s*Cho\s*Choi\b', _re.IGNORECASE)
def _is_lead(au):
    if not au: return False
    return bool(_name_re.search(au.split(',')[0].strip()))
for p in gs_pubs:
    if 'year_int' not in p:
        p['year_int'] = int(p.get('year', '0') or '0')
    if 'cites_int' not in p:
        p['cites_int'] = int(p.get('citations', '0') or '0')
    if 'primary_tech' not in p:
        cls = p.get('classification', {})
        p['primary_tech'] = cls.get('primary_tech', 'Other')
    if 'lead' not in p:
        p['lead'] = _is_lead(p.get('authors', ''))
    if 'pub_type_ko' not in p:
        cls = p.get('classification', {})
        tp = cls.get('type', '')
        p['pub_type_ko'] = '특허' if tp == 'patent' else ('논문' if tp == 'paper' else '기타')

# --- KIPRIS Excel data ---
with open('patent_data.json', 'r', encoding='utf-8') as f:
    kp = json.load(f)
kp_headers = kp['headers']
kp_colmap = {h: i for i, h in enumerate(kp_headers)}
kp_patents = []
for row in kp['data']:
    p = {}
    for h, i in kp_colmap.items():
        p[h] = row[i] if i < len(row) else ''
    kp_patents.append(p)

print(f"Google Scholar: {len(gs_pubs)} publications")
print(f"KIPRIS Excel: {len(kp_patents)} Korean patents")

# ============================================================
# 2. KIPRIS API CALL (using langchain_kipris_tools approach)
# ============================================================
KIPRIS_KEY = "q7jusMtGXniJ9nMVvbM6oNa8I3pMDbXAAsDLkpRng=I="

def call_kipris_free_search(query_params, max_pages=5):
    """Call KIPRIS API freeSearchInfo endpoint."""
    base_url = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/freeSearchInfo"
    all_patents = []

    for page in range(1, max_pages + 1):
        params = {
            'patent': 'true',
            'utility': 'true',
            'numOfRows': '50',
            'pageNo': str(page),
            'sortSpec': 'AD',
            'descSort': 'true',
        }
        params.update(query_params)

        # Build query string (no camelCase conversion needed - KIPRIS accepts both)
        qs_parts = []
        for k, v in params.items():
            if v:
                qs_parts.append(f"{k}={urllib.parse.quote(str(v))}")
        qs_parts.append(f"accessKey={urllib.parse.quote(KIPRIS_KEY)}")
        url = f"{base_url}?{'&'.join(qs_parts)}"

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode('utf-8')
            
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(data)
            
            # Check for errors
            ns_items = root.findall('.//item')
            if not ns_items:
                # Try alternative parsing
                body = root.find('.//body')
                if body is not None:
                    items = body.findall('.//item')
                else:
                    items = []
            else:
                items = ns_items
            
            if not items:
                print(f"  Page {page}: No results, stopping.")
                break
            
            for item in items:
                pat = {}
                for child in item:
                    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    pat[tag] = child.text or ''
                all_patents.append(pat)
            
            print(f"  Page {page}: {len(items)} patents (total: {len(all_patents)})")
            
            if len(items) < 50:
                break
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  Page {page} error: {e}")
            break

    return all_patents

# Try API search
print("\n--- KIPRIS API Search ---")
print("Searching inventor '최낙초'...")
api_patents = call_kipris_free_search({'inventor': '최낙초'})
print(f"API returned: {len(api_patents)} patents")

# Also search by applicant
print("\nSearching applicant '삼성디스플레이' + inventor '최낙초'...")
api_patents2 = call_kipris_free_search({'applicant': '삼성디스플레이', 'inventor': '최낙초'}, max_pages=3)
print(f"API returned: {len(api_patents2)} patents")

# Merge API results (deduplicate by application number)
api_patents_all = api_patents + api_patents2
seen_app_nums = set()
api_merged = []
for p in api_patents_all:
    app_num = p.get('ApplicationNumber', p.get('applicationNumber', ''))
    if app_num and app_num not in seen_app_nums:
        seen_app_nums.add(app_num)
        api_merged.append(p)
    elif not app_num:
        api_merged.append(p)

print(f"\nMerged unique API patents: {len(api_merged)}")

# Convert API results to standardized format
api_std = []
for p in api_merged:
    api_std.append({
        'title': p.get('InventionName', p.get('inventionName', '')),
        'title_en': '',
        'app_number': p.get('ApplicationNumber', p.get('applicationNumber', '')),
        'app_date': p.get('ApplicationDate', p.get('applicationDate', '')),
        'regist_number': p.get('RegistrationNumber', p.get('registrationNumber', '')),
        'regist_date': p.get('RegistrationDate', p.get('registrationDate', '')),
        'regist_status': p.get('RegistrationStatus', p.get('registrationStatus', '')),
        'applicant': p.get('Applicant', p.get('applicant', '')),
        'ipc': p.get('InternationalpatentclassificationNumber', p.get('internationalpatentclassificationNumber', '')),
        'abstract': p.get('Abstract', p.get('abstract', '')),
        'source': 'KIPRIS_API',
    })

# Save API results
with open('kipris_api_results.json', 'w', encoding='utf-8') as f:
    json.dump(api_std, f, ensure_ascii=False, indent=2)
print(f"Saved {len(api_std)} API results to kipris_api_results.json")

# ============================================================
# 3. UNIFIED ANALYSIS
# ============================================================
# Use Excel data as primary Korean patent source (more complete: 154 patents)
# Process KIPRIS Excel patents
def parse_year_kr(d):
    if not d: return None
    parts = str(d).replace('-','.').split('.')
    return int(parts[0]) if parts and parts[0].isdigit() else None

def ipc_main_kr(s):
    if not s: return 'N/A'
    for ipc in str(s).split('|'):
        ipc = ipc.strip()
        parts = ipc.split()
        if parts and len(parts[0]) >= 3:
            return parts[0][:4]
    return str(s)[:4]

IPC_TECH = {
    'H10K': 'OLED', 'H10H': 'Micro LED', 'H01L': 'TFT/Semi',
    'G02F': 'LCD', 'G09G': 'Driving', 'G09F': 'Panel',
    'H05B': 'Display', 'G06F': 'Touch', 'C09K': 'Materials',
    'B32B': 'Layers', 'C23C': 'Coating', 'H10D': 'TFT/Semi',
}

# Korean patents analysis
kr_df = pd.DataFrame(kp_patents)
kr_df['year'] = kr_df['출원일자'].apply(parse_year_kr)
kr_df['ipc_main'] = kr_df['IPC분류'].apply(ipc_main_kr)
kr_df['tech'] = kr_df['ipc_main'].apply(lambda x: IPC_TECH.get(x, 'Other'))
kr_df['status'] = kr_df['법적상태'].apply(lambda s: 'registered' if '등록' in str(s) else ('published' if '공개' in str(s) else 'other'))
kr_df['lead'] = kr_df['발명자'].apply(
    lambda s: 'lead' if s and ('최낙초' in str(s).split('|')[0] if '|' in str(s) else '최낙초' in str(s)[:10]) else 'co')

# US/Google Scholar analysis
gs_df = pd.DataFrame(gs_pubs)
gs_df['year_us'] = gs_df['year_int']
gs_df['lead_us'] = gs_df['lead']
gs_df['type_us'] = gs_df['pub_type_ko']
gs_df['tech_us'] = gs_df['primary_tech']
gs_df['cites'] = gs_df['cites_int']

# Separate US patents and papers
us_patents = gs_df[gs_df['type_us'] == '특허']
us_papers = gs_df[gs_df['type_us'] == '논문']

# Stats
kr_total = len(kr_df)
kr_registered = len(kr_df[kr_df['status'] == 'registered'])
kr_published = len(kr_df[kr_df['status'] == 'published'])
kr_lead = len(kr_df[kr_df['lead'] == 'lead'])
kr_tech = Counter(kr_df['tech'])

us_pat_total = len(us_patents)
us_paper_total = len(us_papers)
us_pat_lead = len(us_patents[us_patents['lead_us'] == True])
us_paper_lead = len(us_papers[us_papers['lead_us'] == True])
us_cites_total = us_patents['cites'].sum() + us_papers['cites'].sum()

# Yearly combined
yearly_kr = kr_df['year'].value_counts().sort_index()
yearly_us_pat = us_patents['year_us'].value_counts().sort_index()
yearly_us_paper = us_papers['year_us'].value_counts().sort_index()

print(f"\n=== INTEGRATED STATS ===")
print(f"KR Patents: {kr_total} (registered: {kr_registered}, lead: {kr_lead})")
print(f"US Patents: {us_pat_total} (lead: {us_pat_lead})")
print(f"Papers: {us_paper_total} (lead: {us_paper_lead})")
print(f"Total citations: {us_cites_total}")

print(f"\nKR Tech: {dict(kr_tech.most_common(8))}")

# h-index
try: h_idx = int(gs_profile['stats'].get('h-index', 14))
except: h_idx = 14
try: i10_idx = int(gs_profile['stats'].get('i10-index', 22))
except: i10_idx = 22
total_gs_cites = int(gs_profile['stats'].get('서지정보', 813))

# ============================================================
# 4. BUILD TABLES
# ============================================================
def build_table_html(df, cols, title, table_id, max_rows=None):
    """Build an HTML collapsible table."""
    if max_rows:
        df = df.head(max_rows)
    
    rows_html = []
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            val = str(row.get(c, ''))[:120]
            cells.append(f'<td>{val}</td>')
        rows_html.append(f'<tr>{"".join(cells)}</tr>')
    
    col_headers = ' '.join([f'<th>{c}</th>' for c in cols])
    total = len(df)
    
    return f'''
    <details>
    <summary><b>{title}</b> <span style="color:#888;">({total} items)</span></summary>
    <div style="max-height:500px;overflow-y:auto;margin-top:8px;">
    <table style="width:100%;border-collapse:collapse;font-size:0.82em;">
    <thead style="position:sticky;top:0;background:#2C3E50;color:white;">
    <tr>{col_headers}</tr>
    </thead>
    <tbody style="background:white;">
    {"".join(rows_html)}
    </tbody>
    </table>
    </div>
    </details>
    '''

# US Patents table
# Build display DataFrame with proper columns
us_pat_display = pd.DataFrame({
    'year': us_patents['year_int'].values,
    'lead': ['주발명자' if l else '공동발명자' for l in us_patents['lead'].values],
    'cites': us_patents['cites_int'].values,
    'title': us_patents['title'].values,
}).sort_values('year', ascending=False)

us_pat_table = build_table_html(
    us_pat_display, ['year', 'lead', 'cites', 'title'],
    '🇺🇸 US Patents (Google Scholar)',
    'us_pat'
)

# US Papers table
us_paper_display = pd.DataFrame({
    'year': us_papers['year_int'].values,
    'lead': ['주발명자' if l else '공동발명자' for l in us_papers['lead'].values],
    'cites': us_papers['cites_int'].values,
    'title': us_papers['title'].values,
}).sort_values('year', ascending=False)

us_paper_table = build_table_html(
    us_paper_display, ['year', 'lead', 'cites', 'title'],
    '📄 Papers / Journal Articles',
    'us_paper'
)

# Korean Patents table
kr_cols_display = ['출원일자', '등록일자', '법적상태', '발명의명칭', '출원번호', '등록번호', 'IPC분류']
kr_display_df = kr_df[kr_cols_display].rename(columns={
    '출원일자': 'app_date', '등록일자': 'reg_date', '법적상태': 'status',
    '발명의명칭': 'title', '출원번호': 'app_num', '등록번호': 'reg_num', 'IPC분류': 'ipc'
}).sort_values('app_date', ascending=False)

kr_pat_table = build_table_html(
    kr_display_df,
    ['app_date', 'status', 'title', 'app_num', 'reg_num', 'ipc'],
    '🇰🇷 Korean Patents (KIPRIS)',
    'kr_pat',
    max_rows=200
)

# ============================================================
# 5. VISUALIZATION
# ============================================================
colors_tech = {
    'OLED': '#3498DB', 'Micro LED': '#2ECC71', 'LCD': '#E74C3C',
    'TFT/Semi': '#9B59B6', 'Driving': '#E67E22', 'Panel': '#1ABC9C',
    'Display': '#34495E', 'Touch': '#D35400', 'Materials': '#16A085',
    'Layers': '#F39C12', 'Coating': '#8E44AD', 'Other': '#7F8C8D',
}

fig = make_subplots(
    rows=5, cols=3,
    specs=[
        [{"type":"indicator","colspan":2}, None, {"type":"pie"}],
        [{"type":"scatter","colspan":2}, None, {"type":"bar"}],
        [{"type":"bar"},{"type":"bar"},{"type":"bar"}],
        [{"type":"heatmap","colspan":2}, None, {"type":"bar"}],
        [{"type":"table","colspan":3}, None, None],
    ],
    subplot_titles=(
        "Research Impact (Google Scholar)", "Patent Portfolio Composition",
        "Yearly Output: US Patents + KR Patents + Papers",
        "Korean Patent Tech Distribution",
        "Korean Patent: Yearly Trend", "US Patent: Yearly Trend", "Papers: Yearly Trend",
        "Technology Evolution (Korean Patents, by IPC)", "Recent 3 Years (2024-2026)",
    ),
    vertical_spacing=0.10, horizontal_spacing=0.06,
)

# (1) Indicator
fig.add_trace(go.Indicator(
    mode="number+gauge+delta", value=h_idx,
    title={"text": f"<b>h-index: {h_idx}</b><br>i10: {i10_idx} | Cites: {total_gs_cites:,}<br>KR:{kr_total} | US:{us_pat_total} | Papers:{us_paper_total}"},
    gauge={'axis': {'range': [None, 30]}, 'bar': {'color': "#2C3E50"},
           'steps': [{'range': [0, 10], 'color': "#E8F8F5"},
                     {'range': [10, 20], 'color': "#A3E4D7"},
                     {'range': [20, 30], 'color': "#1ABC9C"}]},
    number={'font': {'size': 36}},
), row=1, col=1)

# (2) Pie: Portfolio composition
fig.add_trace(go.Pie(
    labels=['KR Patents', 'US Patents', 'Papers'],
    values=[kr_total, us_pat_total, us_paper_total],
    marker_colors=['#3498DB', '#E74C3C', '#2ECC71'],
    textinfo='label+value+percent', hole=0.35,
), row=1, col=3)

# (3) Stacked area: Combined yearly
all_years = sorted(set(
    [y for y in yearly_kr.index if y and 2000<=y<=2026] +
    [y for y in yearly_us_pat.index if y and 2000<=y<=2026] +
    [y for y in yearly_us_paper.index if y and 2000<=y<=2026]
))

fig.add_trace(go.Scatter(
    x=all_years, y=[yearly_kr.get(y, 0) for y in all_years],
    mode='lines', name='KR Patents', fill='tozeroy',
    line=dict(color='#3498DB', width=2), stackgroup='all',
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=all_years, y=[yearly_us_pat.get(y, 0) for y in all_years],
    mode='lines', name='US Patents', fill='tonexty',
    line=dict(color='#E74C3C', width=2), stackgroup='all',
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=all_years, y=[yearly_us_paper.get(y, 0) for y in all_years],
    mode='lines', name='Papers', fill='tonexty',
    line=dict(color='#2ECC71', width=2), stackgroup='all',
), row=2, col=1)
fig.update_xaxes(title_text="Year", row=2, col=1)
fig.update_yaxes(title_text="Count", row=2, col=1)

# (4) Bar: KR tech distribution
tech_items = [(t, c) for t, c in kr_tech.items() if c > 0]
tech_items.sort(key=lambda x: x[1], reverse=True)
fig.add_trace(go.Bar(
    x=[c for _, c in tech_items], y=[t for t, _ in tech_items],
    orientation='h', marker_color=[colors_tech.get(t, '#999') for t, _ in tech_items],
    text=[c for _, c in tech_items], textposition='outside',
), row=2, col=3)

# (5-7) Individual yearly charts
for idx, (label, yearly_data, color) in enumerate([
    ('KR Patents', yearly_kr, '#3498DB'),
    ('US Patents', yearly_us_pat, '#E74C3C'),
    ('Papers', yearly_us_paper, '#2ECC71'),
]):
    yrs = [y for y in sorted(yearly_data.index) if y and 2000<=y<=2026]
    vals = [yearly_data.get(y, 0) for y in yrs]
    fig.add_trace(go.Bar(
        x=yrs, y=vals, marker_color=color, name=label, showlegend=False,
        text=vals, textposition='outside',
    ), row=3, col=idx+1)
    fig.update_xaxes(title_text="Year", row=3, col=idx+1)
    fig.update_yaxes(title_text="Count", row=3, col=idx+1)

# (8) Heatmap: KR tech evolution
tech_list = ['LCD', 'OLED', 'Micro LED', 'TFT/Semi', 'Panel', 'Driving']
heat_years = [y for y in sorted(all_years) if y >= 2005 and y <= 2026]
heat_data = []
for t in tech_list:
    d = []
    for y in heat_years:
        mask = (kr_df['tech'] == t) & (kr_df['year'] == y)
        d.append(mask.sum())
    heat_data.append(d)
fig.add_trace(go.Heatmap(
    z=heat_data, x=heat_years, y=tech_list,
    colorscale='YlOrRd', showscale=True,
    text=[[str(v) if v>0 else '' for v in row] for row in heat_data],
    texttemplate='%{text}', textfont={"size":10},
    colorbar=dict(title="Count"),
), row=4, col=1)
fig.update_xaxes(title_text="Year", row=4, col=1)

# (9) Bar: Recent 3 years (2024-2026) by source
recent_yrs = [2024, 2025, 2026]
for label, data_series, color in [
    ('KR Patents', yearly_kr, '#3498DB'),
    ('US Patents', yearly_us_pat, '#E74C3C'),
    ('Papers', yearly_us_paper, '#2ECC71'),
]:
    vals = [data_series.get(y, 0) for y in recent_yrs]
    fig.add_trace(go.Bar(
        name=label, x=[str(y) for y in recent_yrs], y=vals,
        marker_color=color, text=vals, textposition='outside',
    ), row=4, col=3)
fig.update_xaxes(title_text="Year", row=4, col=3)
fig.update_yaxes(title_text="Count", row=4, col=3)

# (10) Summary table
table_data = [
    ['🇰🇷 Korean Patents', f'{kr_total}', f'Registered: {kr_registered} | Lead: {kr_lead}'],
    ['🇺🇸 US Patents', f'{us_pat_total}', f'Lead: {us_pat_lead}'],
    ['📄 Papers', f'{us_paper_total}', f'Lead: {us_paper_lead}'],
    ['Total Publications', f'{kr_total + us_pat_total + us_paper_total}', ''],
    ['h-index / i10-index', f'{h_idx} / {i10_idx}', f'Citations: {total_gs_cites:,}'],
    ['Period', '2002 - 2026', '25 years'],
    ['KR Top Tech', f'{tech_items[0][0]} ({tech_items[0][1]})', 'By IPC classification'],
    ['US Top Tech', 'LCD (54 from Scholar)', 'Google Scholar analysis'],
    ['Latest Role', 'TFT Reliability (Dev. Quality)', 'Since May 2026'],
    ['Total Unique IP Assets', f'{kr_total + us_pat_total}', 'KR + US patents'],
]

fig.add_trace(go.Table(
    header=dict(values=['Metric', 'Value', 'Note'], fill_color='#2C3E50',
                font=dict(color='white', size=12), align='left'),
    cells=dict(values=list(zip(*table_data)),
               fill_color=[['#F8F9FA', 'white'] * 5],
               font=dict(size=11), align='left'),
    columnwidth=[30, 25, 45]
), row=5, col=1)

fig.update_layout(
    title=dict(
        text=f"<b>📊 Integrated Research Portfolio: Nak Cho Choi (최낙초)</b><br>"
             f"<span style='font-size:12px;color:#7F8C8D;'>"
             f"Google Scholar + KIPRIS | Samsung Display Principal Engineer | Date: 2026.08.08</span>",
        x=0.5, font=dict(size=20)
    ),
    height=2100, width=1600, template='plotly_white',
    showlegend=True, legend=dict(x=1.02, y=0.5),
    margin=dict(t=130, b=40, l=60, r=80),
    barmode='group',
)

# ============================================================
# 6. HTML OUTPUT
# ============================================================
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
* { font-family: 'Inter', 'Noto Sans KR', 'Segoe UI', sans-serif; }
body { background: #f0f2f5; margin: 20px; }
.wrapper { max-width: 1700px; margin: 0 auto; }
.header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white; padding: 24px 36px; border-radius: 14px; margin-bottom: 20px;
    text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.12); }
.header h1 { margin: 0 0 6px; font-size: 1.8em; }
.header p { opacity: 0.85; margin: 0; }
.cards { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.card { flex: 1; min-width: 120px; background: white; border-radius: 10px;
    padding: 16px 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    text-align: center; border-top: 4px solid #3498DB; }
.card .v { font-size: 1.5em; font-weight: 700; color: #2C3E50; }
.card .l { color: #7F8C8D; font-size: 0.75em; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
.card.kr { border-top-color: #3498DB; }
.card.us { border-top-color: #E74C3C; }
.card.paper { border-top-color: #2ECC71; }
.card.total { border-top-color: #F39C12; }
.tables-section { background: white; border-radius: 12px; padding: 16px 20px;
    margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.tables-section h2 { margin: 0 0 12px; font-size: 1.15em; color: #2C3E50;
    border-bottom: 2px solid #3498DB; padding-bottom: 8px; }
.tables-section details { margin-bottom: 8px; }
.tables-section summary { cursor: pointer; padding: 8px 12px; background: #F8F9FA;
    border-radius: 6px; font-size: 0.9em; }
.tables-section summary:hover { background: #E8F0FE; }
.tables-section table { margin-top: 4px; }
.tables-section td, .tables-section th {
    padding: 4px 8px; border: 1px solid #ddd; text-align: left; }
.tables-section tr:nth-child(even) { background: #F8F9FA; }
.plot-box { background: white; border-radius: 12px; padding: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
.disclaimer { background: #FFF3CD; border: 1px solid #FFEAA7; border-radius: 10px;
    padding: 12px 20px; font-size: 0.8em; color: #856404; margin-top: 20px; }
.insight-box { background: #FEF9E7; border-left: 4px solid #F39C12; border-radius: 8px;
    padding: 14px 18px; margin-bottom: 16px; }
.insight-box h3 { margin: 0 0 6px; color: #E67E22; font-size: 0.9em; }
.insight-box ul { margin: 0; padding-left: 18px; color: #7D6608; font-size: 0.85em; line-height: 1.6; }
</style>
"""

html_plot = fig.to_html(include_plotlyjs=True, full_html=True)

# Build complete HTML
html_full = f"""
<div class="wrapper">
<div class="header">
<h1>📊 Integrated Research Portfolio Report</h1>
<p>Nak Cho Choi (최낙초) — Samsung Display Principal Engineer | 25+ Years in Display Technology | Google Scholar + KIPRIS</p>
</div>

<div class="cards">
<div class="card total"><div class="v">{kr_total + us_pat_total + us_paper_total}</div><div class="l">Total IP Assets</div></div>
<div class="card kr"><div class="v">{kr_total}</div><div class="l">KR Patents</div></div>
<div class="card us"><div class="v">{us_pat_total}</div><div class="l">US Patents</div></div>
<div class="card paper"><div class="v">{us_paper_total}</div><div class="l">Papers</div></div>
<div class="card"><div class="v">{h_idx}</div><div class="l">h-index</div></div>
<div class="card"><div class="v">{total_gs_cites:,}</div><div class="l">Citations</div></div>
</div>

<div class="insight-box">
<h3>🔍 Key Insights</h3>
<ul>
<li><b>Total {kr_total + us_pat_total} patents</b>: {kr_total} Korean (KIPRIS) + {us_pat_total} US (Google Scholar) — dual-track IP strategy</li>
<li><b>Korean patents</b>: LCD {kr_tech.get('LCD',0)} | OLED {kr_tech.get('OLED',0)} | Micro LED {kr_tech.get('Micro LED',0)} | Lead inventor: {kr_lead}</li>
<li><b>US patents</b>: {us_pat_lead} as lead inventor via Google Scholar | {us_paper_total} papers with {us_cites_total:,} total citations</li>
<li><b>Career trajectory</b>: LCD (2002-2013) → OLED (2014-2020) → Micro LED (2021-2026) → TFT Reliability (2026.5+)</li>
</ul>
</div>

<div class="tables-section">
<h2>📋 Patent & Paper Lists (click to expand)</h2>
{kr_pat_table}
{us_pat_table}
{us_paper_table}
</div>

<div class="plot-box">
{html_plot}
</div>

<div class="disclaimer">
⚠️ <b>Disclaimer:</b> This integrated report combines data from Google Scholar (scholar.google.com) for US patents/papers and KIPRIS (plus.kipris.or.kr) for Korean patents. Technology classification uses IPC codes (KIPRIS) and keyword matching (Google Scholar). Data as of 2026.08.08.
</div>
</div>
"""

# Extract just the body content from plotly HTML
plot_body = html_plot.split('<body>')[-1].split('</body>')[0]
html_final = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nak Cho Choi - Integrated Research Portfolio</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
{css}
</head>
<body>
{html_full}
</body>
</html>"""

# Save
report_path = 'integrated_report.html'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(html_final)

with open(report_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')
with open('integrated_report.b64', 'w') as f:
    f.write(b64)

print(f"\n✅ Integrated report: {report_path} ({len(html_final):,} bytes)")
print(f"   Base64: integrated_report.b64 ({len(b64):,} chars)")
print(f"\n=== REPORT COMPLETE ===")
print(f"   KR Patents: {kr_total} (API: {len(api_std)})")
print(f"   US Patents: {us_pat_total}")
print(f"   Papers: {us_paper_total}")
print(f"   Total: {kr_total + us_pat_total + us_paper_total}")
