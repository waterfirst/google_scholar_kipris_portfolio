# -*- coding: utf-8 -*-
"""Google Scholar: Nak Cho Choi - Comprehensive Korean Report (Resume-informed)
Key fixes:
1. "organic" + "light emitting diode" = OLED (not Micro LED)  
2. OLED sub-keywords: PDL, UPC, foldable, overcoat, planarization, black matrix, etc.
3. Year-contextual fallback for ambiguous "Display device" patents per resume timeline
"""
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
# 2. CLASSIFICATION (FIXED)
# ============================================================

# Lead inventor regex
NAME_RE = re.compile(
    r'\bNC\s*CHOI\b|\bNC\s*Choi\b|\bN\s*CHOI\b|\bN\s*Choi\b|'
    r'\bC\s*Nakcho\b|\bNakcho\s*Choi\b|\bChoi\s*Nak\s*Cho\b|'
    r'\bKL\s*Nakcho\s*Choi\b|\bNak\s*Cho\s*Choi\b',
    re.IGNORECASE)

def is_lead(authors):
    if not authors: return False
    return bool(NAME_RE.search(authors.split(',')[0].strip()))

# --- TECHNOLOGY CLASSIFICATION ---
# Priority: check explicit OLED/LCD keywords FIRST,
# then check Micro LED (which is narrower),
# then fall back to context.

# OLED keywords (comprehensive, per resume + Samsung Display vocabulary)
OLED_KW = [
    # === Explicit OLED ===
    'oled', 'organic light emitting', 'organic electroluminescent',
    'organic light-emitting', '유기 발광', '유기전계',
    # === OLED-specific structures ===
    # PDL (Pixel Define Layer)
    'pixel define layer', 'pixel-defining', 'pixel defining',
    'black pixel define', 'black-pixel define', 'black pdl',
    'pixel definition', 'pixel-definition',
    # Bank / Overcoat / Planarization
    'bank layer', 'bank structure',
    'overcoat layer', 'overcoat',
    'planarization layer', 'planarization',
    # Encapsulation (TFE)
    'thin film encapsul', 'encapsulation layer',
    'encapsulation substrate', 'tfe', 'barrier film',
    # Foldable / Bendable → typically OLED
    'foldable display', 'folding display', 'foldable device',
    'bendable display', 'rollable display',
    # UPC / Under Panel Camera / UDC
    'under panel camera', 'under display camera',
    'under-display camera', 'camera under display',
    'upc', 'udc',
    # Polarizer-free / Color Filter on OLED
    'polarizer free', 'polarizer-free',
    'color filter on', 'color filter layer',
    # Black Matrix (OLED)
    'black matrix',
    # Switchable privacy (automotive OLED)
    'switchable privacy', 'privacy mode',
    # LTPO / Cst
    'ltpo', 'kickback voltage', 'cst',
    # Siloxane / HPDL
    'siloxane', 'hpdl',
    # Automotive + display → OLED
    'automotive', 'vehicle display',
    # Inorganic insulating → OLED TFT structure
    'inorganic insulating layer', 'metal blocking layer',
    'light blocking layer',
]

# LCD keywords (explicit)
LCD_KW = [
    'liquid crystal', 'lcd', 'liquid-crystal', '액정',
    'liquid crystal display', 'alignment layer', 'polyimide',
    'sealant', 'retardation', 'ocb', 'pva', 'va mode',
    'viewing angle', 'curved lcd', 'transparent lcd',
    'tft array panel', 'panel therefor',
    'liquid crystal display and',
]

# Micro LED keywords (narrower, more specific)
MICRO_LED_KW = [
    'micro led', 'micro-led', 'μled', 'μ-led',
    'led chip', 'led display',
    'micro light emitting', 'micro-light-emitting',
    'tiled display', 'tile display', 'tiling',
    'side metal', 'side-metal',
    'wrap-around electrode', 'wrap around electrode',
    'black organic layer',
]

def classify_tech(pub):
    """Returns primary tech: OLED, LCD, Micro LED, or 기타."""
    title = pub['title'].lower()
    venue = pub.get('venue', '').lower()
    combined = title + ' ' + venue
    year = int(pub.get('year', '0') or '0')

    # --- STEP 1: Check explicit OLED keywords ---
    for kw in OLED_KW:
        if kw in combined:
            return 'OLED'

    # --- STEP 2: Check LCD keywords ---
    for kw in LCD_KW:
        if kw in combined:
            return 'LCD'

    # --- STEP 3: Check Micro LED keywords ---
    # Exclude if title contains "organic" (preserve OLED)
    for kw in MICRO_LED_KW:
        if kw in combined:
            return 'Micro LED'

    # --- STEP 4: Contextual fallback for generic "Display device" patents ---
    # Per resume: 2001-2016 LCD, 2017-2020 OLED transition, 2021+ OLED/Micro LED
    # Use light heuristics only for completely ambiguous titles
    # Additional explicit LCD patterns not caught earlier
    if any(kw in combined for kw in ['va architecture', 'va mode', 'vertical alignment',
                                        'ocb mode', 'pva mode', 'va lcd']):
        return 'LCD'

    if 'display device' in title or 'display panel' in title or 'display apparatus' in title:
        # Check for weak OLED signals
        weak_oled = ['light blocking', 'light-blocking', 'metal blocking',
                     'color filter', 'transmission area', 'camera',
                     'light control', 'optical', 'stylus',
                     'electronic device', 'electronic apparatus']
        for kw in weak_oled:
            if kw in combined:
                return 'OLED'

        # Check for weak Micro LED signals
        weak_ml = ['bump', 'bonding', 'tile', 'seamless', 'large area', 'large-area']
        for kw in weak_ml:
            if kw in combined:
                return 'Micro LED'

        # Year-based hint: 2023+ with no LCD markers → likely Micro LED or OLED
        if year >= 2023:
            # Recent patent, check if LCD markers exist
            if not any(kw in combined for kw in ['liquid crystal', 'lcd']):
                # Check for any LED indicator
                if 'led' in combined or 'bump' in combined or 'tile' in combined:
                    return 'Micro LED'
                # Otherwise could be OLED (automotive, mobile)
                if year >= 2023:
                    return 'OLED'

        # 2001-2016 with no OLED/LCD indicators but "display" → likely LCD
        if year <= 2016:
            return 'LCD'

    return '기타'

# Sub-categories (non-exclusive)
SUB_KW = {
    '제조 공정': ['manufacturing', 'fabricating', 'fabrication', 'method of making',
                'method of forming', '제조 방법', '제조', 'process'],
    'TFT/백플레인': ['thin film transistor', 'tft', 'array panel', 'array substrate',
                   'backplane', '트랜지스터', 'polycrystalline silicon', 'excimer laser'],
    '패키징/본딩': ['bonding', 'bump', 'package', 'interconnect', 'electrode connect',
                  'anisotropic', 'acf', 'flexible circuit', '본딩', '전사'],
    '디스플레이 패널/기판': ['display panel', 'display substrate', '기판', 'tile',
                         'substrate', 'panel'],
    '구동/회로': ['driving circuit', 'driver', 'pixel circuit', 'scan driver',
                'data driver', 'emission driver', 'gate driver', '구동'],
    '검사/테스트': ['inspection', 'testing', 'inspect', 'repair', 'defect', '검사', '리페어'],
    '광학/컬러': ['color filter', 'color conversion', 'wavelength', 'quantum dot',
                'light control', 'optical', '컬러', '색', '파장', 'polarizer'],
    '터치/센서': ['touch', 'sensor', 'sensing', 'fingerprint', 'stylus', '터치', '센서'],
    '플렉서블/폴더블': ['flexible', 'stretchable', 'foldable', 'bendable', 'rollable',
                      'folding', '플렉서블', '폴더블'],
    '봉지/배리어': ['encapsulation', 'barrier', 'dam', 'filler', 'moisture', 'oxygen',
                  '봉지', '밀봉', 'tfe'],
}

def get_sub_cats(pub):
    combined = (pub['title'] + ' ' + pub.get('venue', '')).lower()
    cats = []
    for cat, keywords in SUB_KW.items():
        for kw in keywords:
            if kw in combined:
                cats.append(cat)
                break
    return cats

def get_pub_type(pub):
    venue = pub.get('venue', '').lower()
    if any(kw in venue for kw in ['patent', 'app.', 'application']):
        return '특허'
    elif venue:
        return '논문'
    return '기타'

# ---- Apply ----
for p in pubs:
    p['year_int'] = int(p.get('year', '0') or '0')
    p['cites_int'] = int(p.get('citations', '0') or '0')
    p['lead'] = is_lead(p.get('authors', ''))
    p['role'] = '주발명자' if p['lead'] else '공동발명자'
    p['primary_tech'] = classify_tech(p)
    p['sub_cats'] = get_sub_cats(p)
    p['pub_type_ko'] = get_pub_type(p)

df = pd.DataFrame(pubs)
lead_pubs = [p for p in pubs if p['lead']]
co_pubs = [p for p in pubs if not p['lead']]

# ============================================================
# 3. PRINT & VERIFY
# ============================================================
print("=" * 100)
print(f"전체 {len(pubs)}건 발행물 분류 결과 (이력서 기반 보강)")
print("=" * 100)

for i, p in enumerate(pubs):
    role_mark = '★LEAD' if p['lead'] else ' co'
    tech = p['primary_tech']
    print(f'{i:3d} [{p["year"]:<4s}] {role_mark} | {tech:<14s} | {p["title"][:90]}')
    if p['sub_cats']:
        print(f'       sub: {", ".join(p["sub_cats"])}')

# Summary
primary_dist = Counter(p['primary_tech'] for p in pubs)
lead_primary_dist = Counter(p['primary_tech'] for p in lead_pubs)
sub_dist = Counter()
for p in pubs:
    for s in p['sub_cats']:
        sub_dist[s] += 1

print(f"\n{'='*60}")
print(f"분류 요약")
print(f"{'='*60}")
print(f"주발명자: {len(lead_pubs)}건 / 공동발명자: {len(co_pubs)}건")
print(f"\n주요 기술 분류 (전체):")
for t, c in primary_dist.most_common():
    print(f"  {t}: {c}건")
print(f"\n주요 기술 분류 (주발명자):")
for t, c in lead_primary_dist.most_common():
    print(f"  {t}: {c}건")
print(f"\n세부 카테고리:")
for t, c in sub_dist.most_common():
    print(f"  {t}: {c}건")

# ============================================================
# 4. YEARLY DATA
# ============================================================
yearly_lead = defaultdict(lambda: defaultdict(int))
yearly_co = defaultdict(lambda: defaultdict(int))
yearly_lead_cites = defaultdict(int)
yearly_co_cites = defaultdict(int)

for p in lead_pubs:
    y = p['year_int']
    if y > 0:
        yearly_lead[y][p['primary_tech']] += 1
        yearly_lead_cites[y] += p['cites_int']

for p in co_pubs:
    y = p['year_int']
    if y > 0:
        yearly_co[y][p['primary_tech']] += 1
        yearly_co_cites[y] += p['cites_int']

years_all = sorted(set(list(yearly_lead.keys()) + list(yearly_co.keys())))

# ============================================================
# 5. STATS
# ============================================================
lead_total = len(lead_pubs)
co_total = len(co_pubs)
lead_patents = sum(1 for p in lead_pubs if p['pub_type_ko'] == '특허')
lead_papers = sum(1 for p in lead_pubs if p['pub_type_ko'] == '논문')
lead_cites_total = sum(p['cites_int'] for p in lead_pubs)

try: h_idx = int(profile['stats'].get('h-index', 14))
except: h_idx = 14
try: i10_idx = int(profile['stats'].get('i10-index', 22))
except: i10_idx = 22
total_cites = int(profile['stats'].get('서지정보', 813))

lead_tech_dist = Counter(p['primary_tech'] for p in lead_pubs)
lead_top = sorted(lead_pubs, key=lambda p: p['cites_int'], reverse=True)[:10]

oled_total = primary_dist.get('OLED', 0)
oled_lead = lead_primary_dist.get('OLED', 0)
micro_led_total = primary_dist.get('Micro LED', 0)
lcd_total = primary_dist.get('LCD', 0)

recent_3y_total = sum(sum(yearly_lead.get(y, {}).values()) for y in [2024, 2025, 2026])

# ============================================================
# 6. VISUALIZATION (KOREAN)
# ============================================================
colors_ko = {
    'Micro LED': '#2ECC71', 'OLED': '#3498DB', 'LCD': '#E74C3C',
    'TFT/백플레인': '#9B59B6', '패키징/본딩': '#F39C12',
    '디스플레이 패널/기판': '#1ABC9C', '구동/회로': '#E67E22',
    '검사/테스트': '#95A5A6', '제조 공정': '#34495E',
    '광학/컬러': '#16A085', '터치/센서': '#D35400',
    '플렉서블/폴더블': '#8E44AD', '봉지/배리어': '#8E44AD',
    '기타 디스플레이': '#7F8C8D',
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
        "연구 영향력 지표",
        "주발명자 vs 공동발명자",
        "주요 기술 분류 (전체)",
        "연도별 발행 추이 (주발명자 vs 공동발명자)",
        "주발명자 Top 10 인용",
        "주요 기술 분야 진화 히트맵 (주발명자)",
        "최근 활동 (2024-2026, 주발명자)",
    ),
    vertical_spacing=0.11, horizontal_spacing=0.08,
)

# (1) Indicator
fig.add_trace(go.Indicator(
    mode="number+gauge+delta", value=h_idx,
    title={"text": f"<b>h-index: {h_idx}</b><br>i10-index: {i10_idx}<br>총 인용: {total_cites:,}회"},
    gauge={'axis': {'range': [None, 30]}, 'bar': {'color': "#2C3E50"},
           'steps': [{'range': [0, 10], 'color': "#E8F8F5"},
                     {'range': [10, 20], 'color': "#A3E4D7"},
                     {'range': [20, 30], 'color': "#1ABC9C"}]},
    number={'font': {'size': 38}},
), row=1, col=1)

# (2) Pie: lead vs co
fig.add_trace(go.Pie(
    labels=['주발명자', '공동발명자'], values=[lead_total, co_total],
    marker_colors=['#E74C3C', '#BDC3C7'],
    textinfo='label+value+percent', hole=0.4,
    showlegend=False, textfont=dict(size=13),
), row=1, col=2)

# (3) Bar: primary tech (ALL)
tech_sorted_all = sorted(primary_dist.items(), key=lambda x: x[1], reverse=True)
fig.add_trace(go.Bar(
    x=[v for _, v in tech_sorted_all],
    y=[t for t, _ in tech_sorted_all], orientation='h',
    marker_color=[colors_ko.get(t, '#7F8C8D') for t, _ in tech_sorted_all],
    text=[v for _, v in tech_sorted_all],
    textposition='outside', showlegend=False
), row=1, col=3)

# (4) Stacked area: lead vs co
lead_yearly_total = [sum(yearly_lead[y].values()) for y in years_all]
co_yearly_total = [sum(yearly_co[y].values()) for y in years_all]

fig.add_trace(go.Scatter(
    x=years_all, y=lead_yearly_total, mode='lines+markers',
    name='주발명자', fill='tozeroy',
    line=dict(color='#E74C3C', width=2.5), marker=dict(size=6),
    stackgroup='lc',
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=years_all, y=co_yearly_total, mode='lines+markers',
    name='공동발명자', fill='tonexty',
    line=dict(color='#BDC3C7', width=2), marker=dict(size=4),
    stackgroup='lc',
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=years_all, y=[a+b for a,b in zip(lead_yearly_total, co_yearly_total)],
    mode='lines+markers', name='전체',
    line=dict(color='#2C3E50', width=3, dash='dot'),
    marker=dict(size=7, symbol='diamond', color='#2C3E50'),
), row=2, col=1)
fig.update_xaxes(title_text="연도", row=2, col=1)
fig.update_yaxes(title_text="발행 건수", row=2, col=1)

# (5) Top 10 cited
top_names = [f"[{p['year']}] {p['title'][:55]}" for p in lead_top]
top_vals = [p['cites_int'] for p in lead_top]
fig.add_trace(go.Bar(
    x=top_vals[::-1], y=top_names[::-1], orientation='h',
    marker_color='#E74C3C', text=top_vals[::-1],
    textposition='outside', showlegend=False
), row=2, col=3)
fig.update_xaxes(title_text="인용 수", row=2, col=3)

# (6) Heatmap: main techs (lead)
main_techs = ['Micro LED', 'OLED', 'LCD']
heat_data = [[yearly_lead[y].get(t, 0) for y in years_all] for t in main_techs]
fig.add_trace(go.Heatmap(
    z=heat_data, x=years_all, y=main_techs, colorscale='YlOrRd',
    showscale=True,
    text=[[str(v) if v > 0 else '' for v in row] for row in heat_data],
    texttemplate='%{text}', textfont={"size": 12},
    colorbar=dict(title="건수"),
), row=3, col=1)
fig.update_xaxes(title_text="연도", row=3, col=1)

# (7) Recent activity
recent_techs = ['Micro LED', 'OLED', 'LCD', '디스플레이 패널/기판', '제조 공정', '기타 디스플레이']
bar_colors_yr = ['#E74C3C', '#F39C12', '#2ECC71']
for y_idx, y in enumerate([2024, 2025, 2026]):
    vals = [yearly_lead.get(y, {}).get(t, 0) for t in recent_techs]
    if sum(vals) > 0:
        fig.add_trace(go.Bar(
            name=str(y), x=recent_techs, y=vals, text=vals,
            textposition='outside', marker_color=bar_colors_yr[y_idx],
        ), row=3, col=3)
fig.update_xaxes(title_text="기술 분야", row=3, col=3, tickangle=-25)
fig.update_yaxes(title_text="건수", row=3, col=3)

# (8) Table
max_lead_year = years_all[lead_yearly_total.index(max(lead_yearly_total))] if lead_yearly_total else 'N/A'
table_data = [
    ['전체 발행물', f'{len(pubs)}건', 'Google Scholar 기준'],
    ['주발명자 / 공동발명자', f'{lead_total}건 / {co_total}건', f'주발명자 비중 {lead_total/len(pubs)*100:.1f}%'],
    ['주요 기술', f'LCD {lcd_total} / OLED {oled_total} / Micro LED {micro_led_total}', '3대 디스플레이 모두 포괄'],
    ['주발명자 특허 / 논문', f'{lead_patents}건 / {lead_papers}건', '특허 중심 산업 연구자'],
    ['h-index / i10-index', f'{h_idx} / {i10_idx}', f'총 인용 {total_cites:,}회'],
    ['활동 기간', '2005 - 2026', '22년'],
    ['주발명자 최다 연도', f'{max(lead_yearly_total)}건', f'{max_lead_year}년'],
    ['최다 인용', f'{lead_top[0]["cites_int"]}회', lead_top[0]['title'][:45]],
    ['최근 집중 분야', 'Micro LED / Automotive OLED', f'최근 3년 주발명자 {recent_3y_total}건'],
    ['이력서 기준 경력', '삼성디스플레이 25년+', 'LCD→OLED→Micro LED'],
]

fig.add_trace(go.Table(
    header=dict(values=['지표', '값', '비고'],
                fill_color='#2C3E50', font=dict(color='white', size=13), align='left'),
    cells=dict(values=list(zip(*table_data)),
               fill_color=[['#F8F9FA', 'white'] * 5],
               font=dict(size=12), align='left'),
    columnwidth=[35, 30, 35]
), row=4, col=1)

fig.update_layout(
    title=dict(
        text=f"<b>📊 Google Scholar 연구 프로필 분석 보고서</b><br>"
             f"<span style='font-size:13px;color:#7F8C8D;'>"
             f"{profile['name']}  |  연구분야: {', '.join(profile['fields'])}  |  "
             f"분석일: 2026-08-08  |  출처: Google Scholar</span>",
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
# 7. HTML
# ============================================================
css_ko = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    * { font-family: 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; }
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
    .card .label { color: #7F8C8D; margin-top: 6px; font-size: 0.8em; }
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
    .phase h4 { margin: 0 0 8px; color: #2C3E50; }
    .phase p { margin: 0; font-size: 0.84em; color: #555; line-height: 1.5; }
    .career-timeline {
        display: flex; gap: 0; margin-top: 16px; overflow-x: auto;
    }
    .career-bar {
        display: flex; height: 40px; border-radius: 8px; overflow: hidden;
        flex: 1; min-width: 300px;
    }
    .career-bar .seg { display: flex; align-items: center; justify-content: center; 
                        color: white; font-size: 0.75em; font-weight: 500; }
</style>
"""

html_content = fig.to_html(include_plotlyjs=True, full_html=True)

# Build header + insight
header_html = f"""
<div class="report-wrapper">
<div class="report-header">
<h1>📊 Google Scholar 연구 프로필 분석 보고서</h1>
<p class="subtitle">{profile['name']} — 삼성디스플레이 수석연구원 | 디스플레이 기술 25년+ 연구 여정 (2005–2026)</p>
</div>
<div class="summary-cards">
<div class="card"><div class="value">{len(pubs)}</div><div class="label">전체 발행물</div></div>
<div class="card highlight"><div class="value">{lead_total}</div><div class="label">주발명자</div></div>
<div class="card"><div class="value">{co_total}</div><div class="label">공동발명자</div></div>
<div class="card lcd"><div class="value">{lcd_total}</div><div class="label">LCD</div></div>
<div class="card oled"><div class="value">{oled_total}</div><div class="label">OLED</div></div>
<div class="card mled"><div class="value">{micro_led_total}</div><div class="label">Micro LED</div></div>
</div>
"""

insight_html = f"""
<div class="sub-section">
<h2>🔍 핵심 인사이트 (이력서 기반 분석)</h2>
<div class="insight-box">
<h3>📌 연구 경력 요약 — Nak Cho Choi (최낙초), 삼성디스플레이 수석연구원</h3>
<ul>
<li><b>전체 100건</b> 중 <b>주발명자 {lead_total}건 ({lead_total/len(pubs)*100:.1f}%)</b>, 공동발명자 {co_total}건 — 특허 중심 산업 연구자</li>
<li><b>LCD {lcd_total}건</b> (2005-2017, TFT-LCD 기판·배향·컬러필터), <b>OLED {oled_total}건</b> (2017+, PDL·UPC·폴더블·Black PDL·봉지), <b>Micro LED {micro_led_total}건</b> (2021+, 전사·타일링·본딩)</li>
<li>OLED 특허는 <b>Black PDL(LTPO), UPC(Under Panel Camera), Polarizer-free, Foldable, Switchable Privacy</b> 등 차별화 기술</li>
<li>Google Scholar h-index <b>{h_idx}</b>, 총 인용 <b>{total_cites:,}회</b>, 이력서 기준 130+ US Patents, UDC Pioneering Technology Award 수상</li>
<li>주요 경력: <b>Galaxy Fold 3 개발(Project Lead)</b>, Automotive OLED Switchable Privacy, Micro LED tiled display, Polarizer-free OLED</li>
</ul>
</div>
<div class="phase-timeline">
<div class="phase n1">
<h4>📺 Phase 1: LCD 시대 (2001–2017)</h4>
<p>삼성전자 LCD 사업부 입사. TFT-LCD 기판, 액정 배향(PVA/VA), 컬러필터, curved LCD 등 핵심 특허 다수 출원. 초기 공동발명자로 시작해 점차 주발명자 비중 증가. LTPS OLED backplane 개발, plastic LCD substrate 연구.</p>
</div>
<div class="phase n2">
<h4>💡 Phase 2: OLED 전환기 (2017–2022)</h4>
<p>OLED Materials & Process Innovation 리드. <b>Black PDL</b> 소재 개발(LTPO/A3 라인), <b>UPC</b>(Under Panel Camera) for Galaxy Fold 3, Polarizer-free OLED(효율 15%↑), siloxane HPDL, CMP 공정 최적화. 폴더블 디스플레이 양산 핵심 특허 주도.</p>
</div>
<div class="phase n3">
<h4>🔬 Phase 3: Micro LED + Automotive OLED (2021–2026.4)</h4>
<p>Micro LED side metal patterning, 3D 포토리소그래피, tiled display 기술 개발. Automotive OLED로 확장 — <b>Switchable Privacy Mode</b>, black matrix/lens 구조. 2025년 13건으로 폭발적 IP 창출. UDC Pioneering Technology Award 수상.</p>
<h4>🛡️ Phase 4: 개발품질 — TFT 소자 신뢰성 (2026.5–현재)</h4>
<p><b>개발품질그룹</b>으로 이동, <b>TFT 소자 신뢰성</b> 업무 담당. 20년+ 디스플레이 소자·공정 전문성을 바탕으로 제품 개발 단계에서의 신뢰성 검증, 불량 분석, 품질 게이트 관리. 연구→개발→양산→품질로 이어지는 Full-cycle 디스플레이 엔지니어링 전문가로 진화.</p>
</div>
</div>
</div>
"""

html_content = html_content.replace('<body>', f'<body>\n{header_html}\n{insight_html}\n<div class="plot-container">')
html_content = html_content.replace('</body>',
    '</div>\n'
    '<div class="disclaimer">\n'
    '⚠️ <b>면책조항:</b> 본 보고서는 Google Scholar 공개 프로필(scholar.google.com) 데이터와 이력서(resume_20250914.docx)를 기반으로 AI가 자동 생성했습니다. '
    '주발명자/공동발명자 분류는 저자 순서(1저자 여부) 기준이며, 기술 카테고리는 제목·출처 텍스트의 키워드 매칭 + 이력서 경력 타임라인 기반 추정입니다. '
    'OLED 분류에는 Black PDL, UPC, Foldable, Overcoat, Planarization, TFE, Switchable Privacy 등 Samsung Display 특허 전문용어를 포함했습니다. '
    '데이터 기준일: 2026-08-08.\n'
    '</div>\n</div>\n</body>')
html_content = html_content.replace('</head>', css_ko + '\n</head>')

# Save
report_path = 'deepseek_report.html'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(html_content)
with open(report_path, 'rb') as f:
    b64_content = base64.b64encode(f.read()).decode('utf-8')
with open('deepseek_report.b64', 'w') as f:
    f.write(b64_content)

print(f"\n{'='*60}")
print(f"✅ 보고서 저장 완료")
print(f"{'='*60}")
print(f"   HTML: {report_path} ({len(html_content):,} bytes)")
print(f"   Base64: deepseek_report.b64 ({len(b64_content):,} chars)")
print(f"\n=== 최종 분류 ===")
print(f"   LCD: {lcd_total}건 | OLED: {oled_total}건 | Micro LED: {micro_led_total}건 | 기타: {len(pubs)-lcd_total-oled_total-micro_led_total}건")
print(f"   주발명자: {lead_total}건 (OLED {oled_lead}건, LCD {lead_primary_dist.get('LCD',0)}건, Micro LED {lead_primary_dist.get('Micro LED',0)}건)")
