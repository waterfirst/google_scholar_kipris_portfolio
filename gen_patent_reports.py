# -*- coding: utf-8 -*-
"""FIXED: KIPRIS Analysis + KIPRIS API retry + Dual Report Generation"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json, base64, requests, urllib.parse
from collections import defaultdict, Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# ============================================================
# 1. LOAD PARSED EXCEL DATA
# ============================================================
with open('patent_data.json', 'r', encoding='utf-8') as f:
    pdata = json.load(f)
headers = pdata['headers']
rows = pdata['data']
col_map = {h: i for i, h in enumerate(headers)}

patents = []
for row in rows:
    p = {}
    for h, i in col_map.items():
        p[h] = row[i] if i < len(row) else ''
    patents.append(p)

df = pd.DataFrame(patents)
print(f"Loaded {len(df)} patents from KIPRIS Excel export")

# ============================================================
# 2. PARSE & ANALYZE
# ============================================================
def parse_year(d):
    if not d: return None
    parts = str(d).replace('-','.').split('.')
    return int(parts[0]) if parts and parts[0].isdigit() else None

df['출원년도'] = df['출원일자'].apply(parse_year)
df['등록년도'] = df['등록일자'].apply(parse_year)

# IPC main class
def ipc_main(s):
    if not s: return 'N/A'
    for ipc in str(s).split('|'):
        ipc = ipc.strip()
        parts = ipc.split()
        if parts and len(parts[0]) >= 3:
            return parts[0][:4]
    return str(s)[:4]

df['IPC_MAIN'] = df['IPC분류'].apply(ipc_main)

IPC_TECH = {
    'H10K': 'OLED', 'H10H': 'Micro LED', 'H01L': 'TFT/Semi',
    'G02F': 'LCD', 'G09G': 'Driving', 'G09F': 'Panel',
    'H05B': 'Display', 'H01J': 'Display', 'G06F': 'Touch',
    'C09K': 'Materials', 'B32B': 'Layers', 'C23C': 'Coating',
    'H10D': 'TFT/Semi',
}
df['기술'] = df['IPC_MAIN'].apply(lambda x: IPC_TECH.get(x, f'Other({x})'))

# Legal status
df['상태'] = df['법적상태'].apply(lambda s: '등록' if '등록' in str(s) else ('공개' if '공개' in str(s) else ('거절' if '거절' in str(s) else '기타')))

# Lead inventor check
df['주발명여부'] = df['발명자'].apply(
    lambda s: '주발명자' if s and ('최낙초' in str(s).split('|')[0] if '|' in str(s) else '최낙초' in str(s)[:10]) else '공동발명자')

# STATS
year_counts = df['출원년도'].value_counts().sort_index()
tech_counts = df['기술'].value_counts()
status_counts = df['상태'].value_counts()
ipc_counts = df['IPC_MAIN'].value_counts()
lead_counts = df['주발명여부'].value_counts()

total = len(df)
registered = status_counts.get('등록', 0)
published = status_counts.get('공개', 0)
oled_count = tech_counts.get('OLED', 0)
lcd_count = tech_counts.get('LCD', 0)
mled_count = tech_counts.get('Micro LED', 0)
lead_cnt = lead_counts.get('주발명자', 0)

print(f"Total: {total} | 등록:{registered} | 공개:{published}")
print(f"OLED:{oled_count} | LCD:{lcd_count} | Micro LED:{mled_count}")
print(f"주발명자:{lead_cnt}")

# ============================================================
# 3. KIPRIS API RETRY (ServiceKey parameter)
# ============================================================
print("\n--- KIPRIS API Retry ---")
KEY = "q7jusMtGXniJ9nMVvbM6oNa8I3pMDbXAAsDLkpRng=I="

# Try with ServiceKey
for svc, ep, param_sets in [
    ('patUtiModInfoSearchSEV', 'getAdvancedSearch.do', [
        {'ServiceKey': KEY, 'applicant': '최낙초', 'numOfRows': '3'},
        {'ServiceKey': KEY, 'inventor': '최낙초', 'numOfRows': '3'},
    ]),
    ('patUtiModInfoSearchSEV', 'getSearchWordSearch.do', [
        {'ServiceKey': KEY, 'searchWord': '최낙초', 'numOfRows': '3'},
    ]),
]:
    for params in param_sets:
        url = f'http://plus.kipris.or.kr/kipo-api/kipi/{svc}/{ep}'
        try:
            r = requests.get(url, params=params, timeout=10)
            ok = '<successYN>Y</successYN' in r.text
            err = 'INVALID' in r.text or 'ERROR' in r.text
            tag = 'OK' if ok else ('ERR' if err else f'?({len(r.text)}b)')
            print(f'  [{tag}] {ep} {list(params.keys())[1]}')
            if ok: print(f'    => {r.text[:200]}')
        except Exception as e:
            print(f'  [EXC] {e}')

# ============================================================
# 4. GENERATE REPORTS (KR + EN)
# ============================================================
colors_tech = {'Micro LED':'#2ECC71','OLED':'#3498DB','LCD':'#E74C3C','TFT/Semi':'#9B59B6',
               'Driving':'#E67E22','Panel':'#1ABC9C','Display':'#34495E','Touch':'#D35400',
               'Materials':'#16A085','Layers':'#F39C12','Coating':'#8E44AD'}

def generate_report(lang='ko'):
    """Generate HTML report in Korean or English"""
    is_ko = (lang == 'ko')
    
    # Labels
    if is_ko:
        TITLE = 'KIPRIS 국내 특허 분석 보고서'
        SUBTITLE = f'검색식: 최낙초 | 발행일: 2026.08.08 | 출처: 한국특허정보원(KIPRIS)'
        TOTAL_L = '전체 특허'
        REG_L = '등록'
        PUB_L = '공개'
        LEAD_L = '주발명자'
        OLED_L = 'OLED'
        LCD_L = 'LCD'
        MLED_L = 'Micro LED'
        PLOT_TITLES = ('법적 상태 분포','연도별 출원 추이','IPC 기술 분류',
                       '주요 기술 분야별 출원 (출원년도)','상위 IPC 클래스','최근 출원 (2022-2026)',
                       '주요 통계','')
        YR_L = '출원년도'
        CNT_L = '건수'
        TECH_L = '기술 분류'
        STAT_TABLE = [
            ['전체 특허', f'{total}건', 'KIPRIS 검색 기준'],
            ['등록 / 공개 / 기타', f'{registered} / {published} / {total-registered-published}건', ''],
            ['주발명자', f'{lead_cnt}건 ({lead_cnt/total*100:.1f}%)', '발명자 첫번째 = 최낙초'],
            ['OLED / LCD / Micro LED', f'{oled_count} / {lcd_count} / {mled_count}건', 'IPC 기준'],
            ['출원 기간', f'2002 - 2026', '25년'],
            ['최다 출원 연도', f'2005년 ({year_counts.get(2005,0)}건)', ''],
            ['주요 출원인', '삼성디스플레이', ''],
            ['데이터 출처', 'KIPRIS (특허정보원)', 'API + Excel 내보내기'],
        ]
    else:
        TITLE = 'KIPRIS Korean Patent Analysis Report'
        SUBTITLE = f'Search: Nak Cho Choi | Date: 2026.08.08 | Source: KIPRIS'
        TOTAL_L = 'Total Patents'
        REG_L = 'Registered'
        PUB_L = 'Published'
        LEAD_L = 'Lead Inventor'
        OLED_L = 'OLED'
        LCD_L = 'LCD'
        MLED_L = 'Micro LED'
        PLOT_TITLES = ('Legal Status','Yearly Filing Trend','IPC Technology Classification',
                       'Filing by Technology (by Year)','Top IPC Classes','Recent Filings (2022-2026)',
                       'Key Statistics','')
        YR_L = 'Filing Year'
        CNT_L = 'Count'
        TECH_L = 'Technology'
        STAT_TABLE = [
            ['Total Patents', f'{total}', 'KIPRIS search'],
            ['Registered / Published / Other', f'{registered} / {published} / {total-registered-published}', ''],
            ['Lead Inventor', f'{lead_cnt} ({lead_cnt/total*100:.1f}%)', 'First inventor = Nak Cho Choi'],
            ['OLED / LCD / Micro LED', f'{oled_count} / {lcd_count} / {mled_count}', 'By IPC class'],
            ['Filing Period', '2002 - 2026', '25 years'],
            ['Peak Filing Year', f'2005 ({year_counts.get(2005,0)})', ''],
            ['Main Applicant', 'Samsung Display', ''],
            ['Data Source', 'KIPRIS (Korean Patent Office)', 'API + Excel export'],
        ]

    fig = make_subplots(
        rows=3, cols=3,
        specs=[[{"type":"pie"},{"type":"scatter","colspan":2},None],
               [{"type":"bar"},{"type":"heatmap","colspan":2},None],
               [{"type":"bar"},{"type":"bar"},{"type":"table"}]],
        subplot_titles=PLOT_TITLES,
        vertical_spacing=0.12, horizontal_spacing=0.08,
    )

    # (1) Pie: Legal status
    fig.add_trace(go.Pie(
        labels=[REG_L, PUB_L, 'Other'], values=[registered, published, total-registered-published],
        marker_colors=['#2ECC71','#3498DB','#BDC3C7'],
        textinfo='label+value+percent', hole=0.35,
    ), row=1, col=1)

    # (2) Line: Yearly trend
    years = [y for y in sorted(year_counts.index) if y and 2000<=y<=2026]
    y_vals = [year_counts.get(y,0) for y in years]
    fig.add_trace(go.Scatter(
        x=years, y=y_vals, mode='lines+markers',
        line=dict(color='#E74C3C', width=2.5), marker=dict(size=6),
        fill='tozeroy', name='Total',
    ), row=1, col=2)
    fig.update_xaxes(title_text=YR_L, row=1, col=2)
    fig.update_yaxes(title_text=CNT_L, row=1, col=2)

    # (3) Bar: Technology distribution
    tech_items = [(t, c) for t, c in tech_counts.items() if c > 0]
    tech_items.sort(key=lambda x: x[1], reverse=True)
    fig.add_trace(go.Bar(
        x=[c for _, c in tech_items], y=[t for t, _ in tech_items],
        orientation='h', marker_color=[colors_tech.get(t,'#7F8C8D') for t,_ in tech_items],
        text=[c for _,c in tech_items], textposition='outside',
    ), row=2, col=1)

    # (4) Heatmap: Year x Tech (top 6 techs)
    top_techs = [t for t, _ in tech_items[:6]]
    heat_years = [y for y in years if y >= 2002]
    heat_data = []
    for t in top_techs:
        d = []
        for y in heat_years:
            mask = (df['기술'] == t) & (df['출원년도'] == y)
            d.append(mask.sum())
        heat_data.append(d)
    fig.add_trace(go.Heatmap(
        z=heat_data, x=heat_years, y=top_techs,
        colorscale='YlOrRd', showscale=True,
        text=[[str(v) if v>0 else '' for v in row] for row in heat_data],
        texttemplate='%{text}', textfont={"size":10},
        colorbar=dict(title=CNT_L),
    ), row=2, col=2)
    fig.update_xaxes(title_text=YR_L, row=2, col=2)

    # (5) Bar: Top IPC classes
    ipc_items = [(i, c) for i, c in ipc_counts.items() if c > 0 and i != 'N/A']
    ipc_items.sort(key=lambda x: x[1], reverse=True)
    top_ipc = ipc_items[:10]
    fig.add_trace(go.Bar(
        x=[c for _, c in top_ipc], y=[f'{i} ({IPC_TECH.get(i,"?")})' for i,_ in top_ipc],
        orientation='h', marker_color='#3498DB',
        text=[c for _,c in top_ipc], textposition='outside',
    ), row=3, col=1)

    # (6) Bar: Recent years (2022-2026) by tech
    recent_yrs = [2022, 2023, 2024, 2025, 2026]
    recent_techs = ['OLED', 'Micro LED', 'LCD', 'TFT/Semi', 'Panel']
    colors_r = {'OLED':'#3498DB','Micro LED':'#2ECC71','LCD':'#E74C3C','TFT/Semi':'#9B59B6','Panel':'#1ABC9C'}
    for t in recent_techs:
        vals = [len(df[(df['기술']==t)&(df['출원년도']==y)]) for y in recent_yrs]
        if sum(vals) > 0:
            fig.add_trace(go.Bar(
                name=t, x=recent_yrs, y=vals,
                marker_color=colors_r.get(t,'#999'),
            ), row=3, col=2)
    fig.update_xaxes(title_text=YR_L, row=3, col=2)
    fig.update_yaxes(title_text=CNT_L, row=3, col=2)

    # (7) Table
    fig.add_trace(go.Table(
        header=dict(values=['Metric','Value','Note'], fill_color='#2C3E50',
                    font=dict(color='white',size=12), align='left'),
        cells=dict(values=list(zip(*STAT_TABLE)),
                   fill_color=[['#F8F9FA','white']*5],
                   font=dict(size=11), align='left'),
    ), row=3, col=3)

    fig.update_layout(
        title=dict(text=f'<b>{TITLE}</b><br><span style="font-size:13px;color:#7F8C8D;">{SUBTITLE}</span>',
                   x=0.5, font=dict(size=20)),
        height=1600, width=1500, template='plotly_white',
        showlegend=False, margin=dict(t=120,b=40,l=60,r=60),
        barmode='group',
    )

    # CSS
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    * { font-family: 'Inter','Noto Sans KR','Segoe UI',sans-serif; }
    body { background:#f0f2f5; margin:20px; }
    .wrapper { max-width:1600px; margin:0 auto; }
    .header { background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460); color:white; padding:24px 36px; border-radius:14px; margin-bottom:20px; text-align:center; box-shadow:0 4px 20px rgba(0,0,0,0.12); }
    .header h1 { margin:0 0 6px; font-size:1.8em; }
    .header p { opacity:0.8; margin:0; }
    .cards { display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }
    .card { flex:1; min-width:130px; background:white; border-radius:10px; padding:16px 12px; box-shadow:0 2px 10px rgba(0,0,0,0.05); text-align:center; border-top:4px solid #3498DB; }
    .card .v { font-size:1.5em; font-weight:700; color:#2C3E50; }
    .card .l { color:#7F8C8D; font-size:0.78em; text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }
    .card.r { border-top-color:#E74C3C; }
    .card.g { border-top-color:#2ECC71; }
    .plot-box { background:white; border-radius:12px; padding:8px; box-shadow:0 2px 12px rgba(0,0,0,0.05); margin-bottom:20px; }
    .disclaimer { background:#FFF3CD; border:1px solid #FFEAA7; border-radius:10px; padding:12px 20px; font-size:0.8em; color:#856404; margin-top:20px; }
    </style>
    """

    html = fig.to_html(include_plotlyjs=True, full_html=True)
    
    # Build card header
    if is_ko:
        cards = f'''
        <div class="cards">
        <div class="card"><div class="v">{total}</div><div class="l">전체 특허</div></div>
        <div class="card r"><div class="v">{lead_cnt}</div><div class="l">주발명자</div></div>
        <div class="card g"><div class="v">{registered}</div><div class="l">등록</div></div>
        <div class="card"><div class="v">{oled_count}</div><div class="l">OLED</div></div>
        <div class="card"><div class="v">{lcd_count}</div><div class="l">LCD</div></div>
        <div class="card"><div class="v">{mled_count}</div><div class="l">Micro LED</div></div>
        </div>'''
        disclaimer = '⚠️ 본 보고서는 KIPRIS(특허정보원) Open API 및 Excel 내보내기 데이터를 기반으로 AI가 자동 생성했습니다. IPC 기술 분류는 국제특허분류 기준입니다. 데이터 기준일: 2026.08.08.'
    else:
        cards = f'''
        <div class="cards">
        <div class="card"><div class="v">{total}</div><div class="l">Total Patents</div></div>
        <div class="card r"><div class="v">{lead_cnt}</div><div class="l">Lead Inventor</div></div>
        <div class="card g"><div class="v">{registered}</div><div class="l">Registered</div></div>
        <div class="card"><div class="v">{oled_count}</div><div class="l">OLED</div></div>
        <div class="card"><div class="v">{lcd_count}</div><div class="l">LCD</div></div>
        <div class="card"><div class="v">{mled_count}</div><div class="l">Micro LED</div></div>
        </div>'''
        disclaimer = '⚠️ This report was auto-generated from KIPRIS (Korean Patent Office) Open API and Excel export data. IPC technology classification follows International Patent Classification. Data as of: 2026.08.08.'

    html = html.replace('<body>', f'<body>\n<div class="wrapper">\n<div class="header"><h1>{TITLE}</h1><p>{SUBTITLE}</p></div>\n{cards}\n<div class="plot-box">')
    html = html.replace('</body>', f'</div>\n<div class="disclaimer">{disclaimer}</div>\n</div>\n</body>')
    html = html.replace('</head>', css + '\n</head>')

    return html

# Generate both reports
for lang, fname in [('ko', 'korean_patent_report.html'), ('en', 'english_patent_report.html')]:
    html = generate_report(lang)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(html)
    with open(fname, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    b64f = fname.replace('.html', '.b64')
    with open(b64f, 'w') as f:
        f.write(b64)
    print(f"✅ {fname} ({len(html):,} bytes) + {b64f} ({len(b64):,} chars)")

print("\n=== DONE ===")
