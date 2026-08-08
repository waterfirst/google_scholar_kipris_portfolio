# -*- coding: utf-8 -*-
"""Google Scholar: Nak Cho Choi - English Report"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json, base64, re
from collections import defaultdict, Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# ============================================================
# 1. LOAD
# ============================================================
with open('scholar_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
profile = data['profile']
pubs = data['publications']

# ============================================================
# 2. CLASSIFICATION (same as Korean version)
# ============================================================
NAME_RE = re.compile(
    r'\bNC\s*CHOI\b|\bNC\s*Choi\b|\bN\s*CHOI\b|\bN\s*Choi\b|'
    r'\bC\s*Nakcho\b|\bNakcho\s*Choi\b|\bChoi\s*Nak\s*Cho\b|'
    r'\bKL\s*Nakcho\s*Choi\b|\bNak\s*Cho\s*Choi\b', re.IGNORECASE)

def is_lead(authors):
    if not authors: return False
    return bool(NAME_RE.search(authors.split(',')[0].strip()))

OLED_KW = [
    'oled', 'organic light emitting', 'organic electroluminescent',
    'organic light-emitting',
    'pixel define layer', 'pixel-defining', 'pixel defining',
    'black pixel define', 'black-pixel define', 'black pdl',
    'pixel definition', 'pixel-definition',
    'bank layer', 'bank structure',
    'overcoat layer', 'overcoat',
    'planarization layer', 'planarization',
    'thin film encapsul', 'encapsulation layer',
    'encapsulation substrate', 'tfe', 'barrier film',
    'foldable display', 'folding display', 'foldable device',
    'bendable display', 'rollable display',
    'under panel camera', 'under display camera',
    'under-display camera', 'camera under display', 'upc', 'udc',
    'polarizer free', 'polarizer-free',
    'color filter on', 'color filter layer',
    'black matrix',
    'switchable privacy', 'privacy mode',
    'ltpo', 'kickback voltage', 'cst',
    'siloxane', 'hpdl',
    'automotive', 'vehicle display',
    'inorganic insulating layer', 'metal blocking layer',
    'light blocking layer',
]

LCD_KW = [
    'liquid crystal', 'lcd', 'liquid-crystal',
    'liquid crystal display', 'alignment layer', 'polyimide',
    'sealant', 'retardation', 'ocb', 'pva', 'va mode',
    'viewing angle', 'curved lcd', 'transparent lcd',
    'tft array panel', 'panel therefor',
    'liquid crystal display and',
]

MICRO_LED_KW = [
    'micro led', 'micro-led', 'led chip', 'led display',
    'micro light emitting', 'micro-light-emitting',
    'tiled display', 'tile display', 'tiling',
    'side metal', 'side-metal',
    'wrap-around electrode', 'wrap around electrode',
    'black organic layer',
]

def classify_tech(pub):
    combined = (pub['title'] + ' ' + pub.get('venue', '')).lower()
    year = int(pub.get('year', '0') or '0')

    for kw in OLED_KW:
        if kw in combined: return 'OLED'
    for kw in LCD_KW:
        if kw in combined: return 'LCD'
    for kw in MICRO_LED_KW:
        if kw in combined: return 'Micro LED'

    if any(kw in combined for kw in ['va architecture', 'va mode', 'vertical alignment',
                                        'ocb mode', 'pva mode', 'va lcd']):
        return 'LCD'

    title = pub['title'].lower()
    if 'display device' in title or 'display panel' in title or 'display apparatus' in title:
        weak_oled = ['light blocking', 'light-blocking', 'metal blocking',
                     'color filter', 'transmission area', 'camera',
                     'light control', 'optical', 'stylus',
                     'electronic device', 'electronic apparatus']
        for kw in weak_oled:
            if kw in combined: return 'OLED'
        weak_ml = ['bump', 'bonding', 'tile', 'seamless', 'large area', 'large-area']
        for kw in weak_ml:
            if kw in combined: return 'Micro LED'
        if year >= 2023:
            if 'led' in combined or 'bump' in combined or 'tile' in combined:
                return 'Micro LED'
            return 'OLED'
        if year <= 2016:
            return 'LCD'
    return 'Other'

SUB_KW = {
    'Mfg Process': ['manufacturing', 'fabricating', 'fabrication', 'method of making',
                    'method of forming', 'process'],
    'TFT/Backplane': ['thin film transistor', 'tft', 'array panel', 'array substrate',
                      'backplane', 'polycrystalline silicon', 'excimer laser'],
    'Pkg/Bonding': ['bonding', 'bump', 'package', 'interconnect', 'electrode connect',
                    'anisotropic', 'acf', 'flexible circuit'],
    'Panel/Substrate': ['display panel', 'display substrate', 'tile', 'substrate'],
    'Driving/Circuit': ['driving circuit', 'driver', 'pixel circuit', 'scan driver',
                        'data driver', 'emission driver', 'gate driver'],
    'Inspection/Test': ['inspection', 'testing', 'inspect', 'repair', 'defect'],
    'Optics/Color': ['color filter', 'color conversion', 'wavelength', 'quantum dot',
                     'light control', 'optical', 'polarizer'],
    'Touch/Sensor': ['touch', 'sensor', 'sensing', 'fingerprint', 'stylus'],
    'Flexible/Foldable': ['flexible', 'stretchable', 'foldable', 'bendable', 'rollable', 'folding'],
    'Encapsulation': ['encapsulation', 'barrier', 'dam', 'filler', 'moisture', 'oxygen', 'tfe'],
}

def get_sub_cats(pub):
    combined = (pub['title'] + ' ' + pub.get('venue', '')).lower()
    return [cat for cat, kws in SUB_KW.items() if any(kw in combined for kw in kws)]

def get_pub_type(pub):
    venue = pub.get('venue', '').lower()
    if any(kw in venue for kw in ['patent', 'app.', 'application']):
        return 'Patent'
    elif venue:
        return 'Paper'
    return 'Other'

for p in pubs:
    p['year_int'] = int(p.get('year', '0') or '0')
    p['cites_int'] = int(p.get('citations', '0') or '0')
    p['lead'] = is_lead(p.get('authors', ''))
    p['role'] = 'Lead Inventor' if p['lead'] else 'Co-Inventor'
    p['primary_tech'] = classify_tech(p)
    p['sub_cats'] = get_sub_cats(p)
    p['pub_type_ko'] = get_pub_type(p)

df = pd.DataFrame(pubs)
lead_pubs = [p for p in pubs if p['lead']]
co_pubs = [p for p in pubs if not p['lead']]

# Yearly data
yearly_lead = defaultdict(lambda: defaultdict(int))
yearly_co = defaultdict(lambda: defaultdict(int))
for p in lead_pubs:
    y = p['year_int']
    if y > 0: yearly_lead[y][p['primary_tech']] += 1
for p in co_pubs:
    y = p['year_int']
    if y > 0: yearly_co[y][p['primary_tech']] += 1
years_all = sorted(set(list(yearly_lead.keys()) + list(yearly_co.keys())))

# Stats
lead_total = len(lead_pubs)
co_total = len(co_pubs)
lead_patents = sum(1 for p in lead_pubs if p['pub_type_ko'] == 'Patent')
lead_papers = sum(1 for p in lead_pubs if p['pub_type_ko'] == 'Paper')
try: h_idx = int(profile['stats'].get('h-index', 14))
except: h_idx = 14
try: i10_idx = int(profile['stats'].get('i10-index', 22))
except: i10_idx = 22
total_cites = int(profile['stats'].get('서지정보', 813))

primary_dist = Counter(p['primary_tech'] for p in pubs)
lead_primary_dist = Counter(p['primary_tech'] for p in lead_pubs)
lead_top = sorted(lead_pubs, key=lambda p: p['cites_int'], reverse=True)[:10]

oled_total = primary_dist.get('OLED', 0)
oled_lead = lead_primary_dist.get('OLED', 0)
micro_led_total = primary_dist.get('Micro LED', 0)
lcd_total = primary_dist.get('LCD', 0)
other_total = primary_dist.get('Other', 0)

# ============================================================
# 3. VISUALIZATION (ENGLISH)
# ============================================================
colors_en = {
    'Micro LED': '#2ECC71', 'OLED': '#3498DB', 'LCD': '#E74C3C',
    'Mfg Process': '#34495E', 'TFT/Backplane': '#9B59B6',
    'Pkg/Bonding': '#F39C12', 'Panel/Substrate': '#1ABC9C',
    'Driving/Circuit': '#E67E22', 'Inspection/Test': '#95A5A6',
    'Optics/Color': '#16A085', 'Touch/Sensor': '#D35400',
    'Flexible/Foldable': '#8E44AD', 'Encapsulation': '#8E44AD',
    'Other': '#7F8C8D',
}

fig = make_subplots(
    rows=4, cols=3,
    specs=[
        [{"type": "indicator"}, {"type": "pie"}, {"type": "bar"}],
        [{"type": "scatter", "colspan": 2}, None, {"type": "bar"}],
        [{"type": "heatmap", "colspan": 2}, None, {"type": "bar"}],
        [{"type": "table", "colspan": 3}, None, None],
    ],
    subplot_titles=(
        "Research Impact Metrics",
        "Lead Inventor vs Co-Inventor",
        "Primary Technology Distribution (All)",
        "Yearly Publication Trend (Lead vs Co-Inventor)",
        "Lead Inventor Top 10 Cited",
        "Core Technology Evolution Heatmap (Lead Inventor)",
        "Recent Activity (2024-2026, Lead Inventor)",
    ),
    vertical_spacing=0.11, horizontal_spacing=0.08,
)

# (1) Indicator
fig.add_trace(go.Indicator(
    mode="number+gauge+delta", value=h_idx,
    title={"text": f"<b>h-index: {h_idx}</b><br>i10-index: {i10_idx}<br>Total Citations: {total_cites:,}"},
    gauge={'axis': {'range': [None, 30]}, 'bar': {'color': "#2C3E50"},
           'steps': [{'range': [0, 10], 'color': "#E8F8F5"},
                     {'range': [10, 20], 'color': "#A3E4D7"},
                     {'range': [20, 30], 'color': "#1ABC9C"}]},
    number={'font': {'size': 38}},
), row=1, col=1)

# (2) Pie
fig.add_trace(go.Pie(
    labels=['Lead Inventor', 'Co-Inventor'], values=[lead_total, co_total],
    marker_colors=['#E74C3C', '#BDC3C7'],
    textinfo='label+value+percent', hole=0.4,
    showlegend=False, textfont=dict(size=13),
), row=1, col=2)

# (3) Bar
tech_sorted_all = sorted(primary_dist.items(), key=lambda x: x[1], reverse=True)
fig.add_trace(go.Bar(
    x=[v for _, v in tech_sorted_all],
    y=[t for t, _ in tech_sorted_all], orientation='h',
    marker_color=[colors_en.get(t, '#7F8C8D') for t, _ in tech_sorted_all],
    text=[v for _, v in tech_sorted_all],
    textposition='outside', showlegend=False
), row=1, col=3)

# (4) Stacked area
lead_yt = [sum(yearly_lead[y].values()) for y in years_all]
co_yt = [sum(yearly_co[y].values()) for y in years_all]
fig.add_trace(go.Scatter(
    x=years_all, y=lead_yt, mode='lines+markers',
    name='Lead Inventor', fill='tozeroy',
    line=dict(color='#E74C3C', width=2.5), marker=dict(size=6),
    stackgroup='lc',
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=years_all, y=co_yt, mode='lines+markers',
    name='Co-Inventor', fill='tonexty',
    line=dict(color='#BDC3C7', width=2), marker=dict(size=4),
    stackgroup='lc',
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=years_all, y=[a+b for a,b in zip(lead_yt, co_yt)],
    mode='lines+markers', name='Total',
    line=dict(color='#2C3E50', width=3, dash='dot'),
    marker=dict(size=7, symbol='diamond', color='#2C3E50'),
), row=2, col=1)
fig.update_xaxes(title_text="Year", row=2, col=1)
fig.update_yaxes(title_text="Publications", row=2, col=1)

# (5) Top cited
top_names = [f"[{p['year']}] {p['title'][:55]}" for p in lead_top]
top_vals = [p['cites_int'] for p in lead_top]
fig.add_trace(go.Bar(
    x=top_vals[::-1], y=top_names[::-1], orientation='h',
    marker_color='#E74C3C', text=top_vals[::-1],
    textposition='outside', showlegend=False
), row=2, col=3)
fig.update_xaxes(title_text="Citations", row=2, col=3)

# (6) Heatmap
main_techs = ['Micro LED', 'OLED', 'LCD']
heat_data = [[yearly_lead[y].get(t, 0) for y in years_all] for t in main_techs]
fig.add_trace(go.Heatmap(
    z=heat_data, x=years_all, y=main_techs, colorscale='YlOrRd',
    showscale=True,
    text=[[str(v) if v > 0 else '' for v in row] for row in heat_data],
    texttemplate='%{text}', textfont={"size": 12},
    colorbar=dict(title="Count"),
), row=3, col=1)
fig.update_xaxes(title_text="Year", row=3, col=1)

# (7) Recent
recent_techs_en = ['Micro LED', 'OLED', 'LCD', 'Panel/Substrate', 'Mfg Process', 'Other']
bar_colors_yr = ['#E74C3C', '#F39C12', '#2ECC71']
for y_idx, y in enumerate([2024, 2025, 2026]):
    vals = [yearly_lead.get(y, {}).get(t, 0) for t in recent_techs_en]
    if sum(vals) > 0:
        fig.add_trace(go.Bar(
            name=str(y), x=recent_techs_en, y=vals, text=vals,
            textposition='outside', marker_color=bar_colors_yr[y_idx],
        ), row=3, col=3)
fig.update_xaxes(title_text="Technology", row=3, col=3, tickangle=-25)
fig.update_yaxes(title_text="Count", row=3, col=3)

# (8) Table
max_lead_year = years_all[lead_yt.index(max(lead_yt))] if lead_yt else 'N/A'
table_data = [
    ['Total Publications', str(len(pubs)), 'via Google Scholar'],
    ['Lead / Co-Inventor', f'{lead_total} / {co_total}', f'{lead_total/len(pubs)*100:.1f}% lead'],
    ['Core Technologies', f'LCD {lcd_total} / OLED {oled_total} / Micro LED {micro_led_total}', '3 major display techs'],
    ['Lead: Patents / Papers', f'{lead_patents} / {lead_papers}', 'Patent-driven industrial R&D'],
    ['h-index / i10-index', f'{h_idx} / {i10_idx}', f'{total_cites:,} total citations'],
    ['Active Period', '2005 - 2026', '22 years'],
    ['Peak Year (Lead)', f'{max(lead_yt)} pubs', f'{max_lead_year}'],
    ['Most Cited', f'{lead_top[0]["cites_int"]} cites', lead_top[0]['title'][:45]],
    ['Recent Focus', 'Micro LED / Automotive OLED', f'{sum(lead_yt[-3:]) if len(lead_yt)>=3 else "N/A"} pubs (2024-26)'],
    ['Latest Role', 'TFT Reliability (Dev. Quality)', 'Since May 2026'],
]

fig.add_trace(go.Table(
    header=dict(values=['Metric', 'Value', 'Note'],
                fill_color='#2C3E50', font=dict(color='white', size=13), align='left'),
    cells=dict(values=list(zip(*table_data)),
               fill_color=[['#F8F9FA', 'white'] * 5],
               font=dict(size=12), align='left'),
    columnwidth=[35, 30, 35]
), row=4, col=1)

fig.update_layout(
    title=dict(
        text=f"<b>Google Scholar Research Profile Analysis</b><br>"
             f"<span style='font-size:13px;color:#7F8C8D;'>"
             f"{profile['name']}  |  Fields: {', '.join(profile['fields'])}  |  "
             f"Date: 2026-08-08  |  Source: Google Scholar</span>",
        x=0.5, font=dict(size=22)
    ),
    height=1950, width=1600,
    template='plotly_white',
    showlegend=True,
    legend=dict(x=1.02, y=0.5, bgcolor='rgba(255,255,255,0.85)'),
    margin=dict(t=130, b=40, l=60, r=80),
    barmode='group',
)

# ============================================================
# 4. HTML (ENGLISH)
# ============================================================
css_en = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+KR:wght@400;700&display=swap');
    * { font-family: 'Inter', 'Segoe UI', 'Noto Sans KR', sans-serif; }
    body { background: #f0f2f5; margin: 20px; }
    .report-wrapper { max-width: 1700px; margin: 0 auto; }
    .report-header { 
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white; padding: 28px 40px; border-radius: 16px; margin-bottom: 22px;
        text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .report-header h1 { margin: 0 0 8px; font-size: 2em; letter-spacing: -0.5px; }
    .report-header .subtitle { opacity: 0.85; font-size: 1em; margin: 0; font-weight: 300; }
    .summary-cards { display: flex; gap: 14px; margin-bottom: 22px; flex-wrap: wrap; }
    .card { 
        flex: 1; min-width: 140px; background: white; border-radius: 12px;
        padding: 18px 14px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        text-align: center; border-top: 4px solid #3498DB;
    }
    .card .value { font-size: 1.6em; font-weight: 700; color: #2C3E50; }
    .card .label { color: #7F8C8D; margin-top: 6px; font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.5px; }
    .card.highlight { border-top-color: #E74C3C; }
    .card.oled { border-top-color: #3498DB; }
    .card.lcd { border-top-color: #E74C3C; }
    .card.mled { border-top-color: #2ECC71; }
    .card.green { border-top-color: #2ECC71; }
    .sub-section { 
        background: white; border-radius: 12px; padding: 20px 24px; 
        margin-bottom: 22px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .sub-section h2 { margin: 0 0 16px; font-size: 1.15em; color: #2C3E50; 
                      border-bottom: 2px solid #3498DB; padding-bottom: 10px; }
    .insight-box {
        background: #FEF9E7; border-left: 4px solid #F39C12; border-radius: 8px;
        padding: 16px 20px; margin-top: 16px;
    }
    .insight-box h3 { margin: 0 0 8px; color: #E67E22; font-size: 0.95em; }
    .insight-box ul { margin: 0; padding-left: 20px; color: #7D6608; font-size: 0.88em; line-height: 1.7; }
    .plot-container { background: white; border-radius: 12px; padding: 8px; 
                      box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 22px; }
    .disclaimer { 
        background: #FFF3CD; border: 1px solid #FFEAA7; border-radius: 10px;
        padding: 14px 22px; margin-top: 22px; font-size: 0.82em; color: #856404;
    }
    .phase-timeline { display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
    .phase {
        flex: 1; min-width: 200px; background: white; border-radius: 10px;
        padding: 16px; box-shadow: 0 1px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #3498DB;
    }
    .phase.n1 { border-left-color: #E74C3C; }
    .phase.n2 { border-left-color: #3498DB; }
    .phase.n3 { border-left-color: #2ECC71; }
    .phase.n4 { border-left-color: #F39C12; }
    .phase h4 { margin: 0 0 8px; color: #2C3E50; }
    .phase p { margin: 0; font-size: 0.84em; color: #555; line-height: 1.5; }
</style>
"""

html_content = fig.to_html(include_plotlyjs=True, full_html=True)

header_html = f"""
<div class="report-wrapper">
<div class="report-header">
<h1>📊 Google Scholar Research Profile Report</h1>
<p class="subtitle">{profile['name']} — Principal Engineer, Samsung Display | 25+ Years in Display Technology (2005–2026)</p>
</div>
<div class="summary-cards">
<div class="card"><div class="value">{len(pubs)}</div><div class="label">Total Pubs</div></div>
<div class="card highlight"><div class="value">{lead_total}</div><div class="label">Lead Inventor</div></div>
<div class="card"><div class="value">{co_total}</div><div class="label">Co-Inventor</div></div>
<div class="card lcd"><div class="value">{lcd_total}</div><div class="label">LCD</div></div>
<div class="card oled"><div class="value">{oled_total}</div><div class="label">OLED</div></div>
<div class="card mled"><div class="value">{micro_led_total}</div><div class="label">Micro LED</div></div>
</div>
"""

insight_html = f"""
<div class="sub-section">
<h2>🔍 Key Insights (Resume-Informed Analysis)</h2>
<div class="insight-box">
<h3>📌 Career Summary — Nak Cho Choi, Samsung Display Principal Engineer</h3>
<ul>
<li><b>{len(pubs)} total publications</b>: <b>{lead_total} as Lead Inventor ({lead_total/len(pubs)*100:.1f}%)</b>, {co_total} as Co-Inventor — Patent-driven industrial researcher</li>
<li><b>LCD {lcd_total}</b> (2005–2017: TFT-LCD substrates, alignment, color filters), <b>OLED {oled_total}</b> (2017+: PDL, UPC, Foldable, Black PDL, Encapsulation), <b>Micro LED {micro_led_total}</b> (2021+: Transfer, Bonding, Tiling)</li>
<li>OLED patents cover <b>Black PDL (LTPO), UPC (Under Panel Camera), Polarizer-free, Foldable, Switchable Privacy</b> — differentiated technologies</li>
<li>Google Scholar h-index <b>{h_idx}</b>, total citations <b>{total_cites:,}</b> | Resume: 130+ US Patents, UDC Pioneering Technology Award</li>
<li>Key projects: <b>Galaxy Fold 3 (Project Lead)</b>, Automotive OLED Switchable Privacy, Micro LED tiled display, Polarizer-free OLED (15% efficiency gain)</li>
</ul>
</div>
<div class="phase-timeline">
<div class="phase n1">
<h4>📺 Phase 1: LCD Era (2001–2017)</h4>
<p>Joined Samsung Electronics LCD Division. Core patents in TFT-LCD substrates, liquid crystal alignment (PVA/VA), color filters, curved LCD. Started as co-inventor, gradually increasing lead inventor role. Developed LTPS OLED backplane and plastic LCD substrates.</p>
</div>
<div class="phase n2">
<h4>💡 Phase 2: OLED Transition (2017–2022)</h4>
<p>Led OLED Materials & Process Innovation. <b>Black PDL</b> development (LTPO/A3 line), <b>UPC</b> for Galaxy Fold 3, Polarizer-free OLED (+15% efficiency), siloxane HPDL, CMP optimization. Mass-production enabling patents for foldable displays.</p>
</div>
<div class="phase n3">
<h4>🔬 Phase 3: Micro LED + Automotive OLED (2021–Apr 2026)</h4>
<p>Micro LED side metal patterning, 3D photolithography, tiled display technology. Expanded into Automotive OLED — <b>Switchable Privacy Mode</b>, black matrix/lens. Peak IP creation: 13 patents in 2025. UDC Pioneering Technology Award recipient.</p>
</div>
<div class="phase n4">
<h4>🛡️ Phase 4: Development Quality — TFT Reliability (May 2026–Present)</h4>
<p>Transitioned to <b>Development Quality Group</b>, leading <b>TFT device reliability</b>. Leveraging 25+ years of device and process expertise for reliability validation, failure analysis, and quality gate management. Full-cycle display engineer: R&D → Development → Mass Production → Quality.</p>
</div>
</div>
</div>
"""

html_content = html_content.replace('<body>', f'<body>\n{header_html}\n{insight_html}\n<div class="plot-container">')
html_content = html_content.replace('</body>',
    '</div>\n'
    '<div class="disclaimer">\n'
    '⚠️ <b>Disclaimer:</b> This report was auto-generated from Google Scholar public profile data (scholar.google.com) and resume (resume_20250914.docx). '
    'Lead/Co-Inventor classification is based on first-author position. Technology categories use keyword matching on titles/venues + resume career timeline inference. '
    'OLED classification includes Samsung Display patent vocabulary: Black PDL, UPC, Foldable, Overcoat, Planarization, TFE, Switchable Privacy. '
    'Data as of 2026-08-08.\n'
    '</div>\n</div>\n</body>')
html_content = html_content.replace('</head>', css_en + '\n</head>')

# Save
report_path = 'deepseek_english_report.html'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(html_content)
with open(report_path, 'rb') as f:
    b64_content = base64.b64encode(f.read()).decode('utf-8')
with open('deepseek_english_report.b64', 'w') as f:
    f.write(b64_content)

print(f"English report saved: {report_path} ({len(html_content):,} bytes)")
print(f"Base64: deepseek_english_report.b64 ({len(b64_content):,} chars)")
print(f"\nClassification: LCD {lcd_total} | OLED {oled_total} | Micro LED {micro_led_total} | Other {other_total}")
print(f"Lead Inventor: {lead_total} | Co-Inventor: {co_total}")
