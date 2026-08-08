# -*- coding: utf-8 -*-
"""Professional-grade static portfolio page - matching integrated_report.html quality."""
import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')

with open('portfolio_data.json','r',encoding='utf-8') as f: D=json.load(f)
P=D['profile'];S=P['stats'];C=D['charts'];KR=D['kr_patents'];US=D['us_patents'];PP=D['papers']

def esc(s): return str(s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def kr_rows():
    rows=[]
    for i,p in enumerate(KR):
        st='reg' if p['status']=='등록' else 'pub'
        rows.append(f'<tr><td>{i+1}</td><td>{esc(p["app_date"])}</td><td><span class="tag {st}">{esc(p["status"])}</span></td><td><span class="tag">{esc(p["tech"])}</span></td><td title="{esc(p["title"])}">{esc(p["title"])[:70]}</td><td style="font-family:monospace;font-size:0.75em">{esc(p["app_number"])}</td></tr>')
    return '\n'.join(rows)

def us_rows():
    rows=[]
    for i,p in enumerate(US):
        rc='lead' if p.get('lead') else 'co'; rt='Lead' if p.get('lead') else 'Co'
        rows.append(f'<tr><td>{i+1}</td><td>{p["year"]}</td><td><span class="tag {rc}">{rt}</span></td><td>{p.get("cites",0)}</td><td><span class="tag">{esc(p["tech"])}</span></td><td title="{esc(p["title"])}">{esc(p["title"])[:70]}</td></tr>')
    return '\n'.join(rows)

def pp_rows():
    rows=[]
    for i,p in enumerate(PP):
        rows.append(f'<tr><td>{i+1}</td><td>{p["year"]}</td><td>{p.get("cites",0)}</td><td><span class="tag">{esc(p["tech"])}</span></td><td title="{esc(p["title"])}">{esc(p["title"])[:70]}</td><td style="color:var(--t2);font-size:0.8em">{esc(p.get("venue",""))}</td></tr>')
    return '\n'.join(rows)

CHARTS_JSON=json.dumps(C,ensure_ascii=False)
KR_JSON=json.dumps(KR,ensure_ascii=False)
US_JSON=json.dumps(US,ensure_ascii=False)
PP_JSON=json.dumps(PP,ensure_ascii=False)

html=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Research Portfolio — Nak Cho Choi</title>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
:root{{--bg:#0a0a1a;--bg2:#12122a;--card:rgba(255,255,255,0.035);--bd:rgba(255,255,255,0.06);--tx:#c8c8d4;--t2:#8888a0;--bl:#5b9cf5;--rd:#f56565;--gn:#68d391;--or:#f6ad55;--pr:#b794f4;--gr:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter','Noto Sans KR','Segoe UI',sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;color:var(--tx)}}
.wrap{{max-width:1500px;margin:0 auto;padding:20px}}
.hdr{{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);padding:30px 40px;border-radius:16px;margin-bottom:22px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.15)}}
.hdr h1{{margin:0;font-size:2em;font-weight:800;letter-spacing:-0.5px;color:#fff}}
.hdr .sub{{opacity:0.8;font-size:0.95em;margin-top:6px;font-weight:300;color:#ccc}}
.cards{{display:flex;gap:14px;margin-bottom:22px;flex-wrap:wrap}}
.card{{flex:1;min-width:130px;background:#fff;border-radius:12px;padding:20px 16px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.08);border-top:4px solid var(--bl)}}
.card:hover{{transform:translateY(-2px);box-shadow:0 4px 16px rgba(0,0,0,0.12);transition:all .2s}}
.card .val{{font-size:1.8em;font-weight:700;color:#2C3E50}}
.card .lbl{{color:var(--t2);font-size:0.72em;text-transform:uppercase;letter-spacing:1px;margin-top:4px}}
.card.hl{{border-top-color:var(--rd)}}.card.kr{{border-top-color:var(--bl)}}.card.us{{border-top-color:var(--rd)}}.card.pp{{border-top-color:var(--gn)}}.card.tl{{border-top-color:var(--or)}}
.insight{{background:#fff;border-radius:12px;padding:20px 24px;margin-bottom:22px;box-shadow:0 2px 12px rgba(0,0,0,0.06);border-left:4px solid var(--or)}}
.insight h3{{color:#E67E22;font-size:0.95em;margin:0 0 8px}}
.insight ul{{margin:0;padding-left:20px;color:#7D6608;font-size:0.85em;line-height:1.7}}
.plot-box{{background:#fff;border-radius:12px;padding:8px;box-shadow:0 2px 12px rgba(0,0,0,0.06);margin-bottom:22px}}
.tables-section{{background:#fff;border-radius:12px;padding:20px 24px;margin-bottom:22px;box-shadow:0 2px 12px rgba(0,0,0,0.06)}}
.tables-section h2{{margin:0 0 14px;font-size:1.1em;color:#2C3E50;border-bottom:2px solid var(--bl);padding-bottom:8px}}
.tables-section details{{margin-bottom:8px}}
.tables-section summary{{cursor:pointer;padding:10px 14px;background:#F8F9FA;border-radius:8px;font-size:0.88em;font-weight:500;color:#2C3E50}}
.tables-section summary:hover{{background:#E8F0FE}}
.tables-section summary span{{color:var(--t2);font-size:0.85em}}
.tbl-wrap{{max-height:480px;overflow-y:auto;border-radius:6px;border:1px solid #eee;margin-top:8px}}
.tbl-wrap table{{width:100%;border-collapse:collapse;font-size:0.78em}}
.tbl-wrap thead{{position:sticky;top:0;z-index:1}}
.tbl-wrap th{{background:#2C3E50;color:#fff;padding:8px 6px;text-align:left;font-weight:600;font-size:0.76em;text-transform:uppercase}}
.tbl-wrap td{{padding:6px;border-bottom:1px solid #eee;color:#444;max-width:360px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.tbl-wrap tr:nth-child(even) td{{background:#F8F9FA}}
.tbl-wrap tr:hover td{{background:#E8F0FE}}
.tag{{display:inline-block;padding:2px 8px;border-radius:5px;font-size:0.72em;font-weight:600}}
.tag.lead{{background:rgba(245,101,101,0.15);color:var(--rd)}}
.tag.co{{background:#eee;color:#999}}
.tag.reg{{background:rgba(104,211,145,0.15);color:#2E7D32}}
.tag.pub{{background:rgba(91,156,245,0.15);color:#1565C0}}
.tabs{{display:flex;gap:4px;margin-bottom:0;flex-wrap:wrap}}
.tb{{padding:10px 20px;background:rgba(255,255,255,0.06);border-radius:12px 12px 0 0;cursor:pointer;font-size:0.85em;font-weight:500;color:var(--t2);border:1px solid transparent;transition:all .2s}}
.tb:hover{{color:#fff;background:rgba(255,255,255,0.1)}}
.tb.on{{color:#fff;background:var(--card);border-color:var(--bd);border-bottom-color:transparent}}
.tb .badge{{background:rgba(255,255,255,0.1);padding:1px 8px;border-radius:10px;font-size:0.75em;margin-left:6px}}
.content{{background:var(--card);backdrop-filter:blur(12px);border:1px solid var(--bd);border-radius:0 14px 14px 14px;padding:24px;min-height:200px}}
.panel{{display:none}}.panel.on{{display:block}}
.inp{{width:100%;padding:8px 14px;background:rgba(255,255,255,0.04);border:1px solid var(--bd);border-radius:10px;color:var(--tx);font-size:0.84em;outline:none;margin-bottom:10px}}
.inp:focus{{border-color:var(--bl)}}
.tbl-info{{color:var(--t2);font-size:0.8em;margin-bottom:6px}}
.timeline{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:16px}}
.phase{{background:rgba(255,255,255,0.03);border-radius:12px;padding:16px;border-left:4px solid var(--bl)}}
.phase.p1{{border-color:var(--rd)}}.phase.p2{{border-color:var(--bl)}}.phase.p3{{border-color:var(--gn)}}.phase.p4{{border-color:var(--or)}}
.phase h4{{color:#ddd;font-size:0.88em;margin:0 0 6px}}
.phase p{{color:var(--t2);font-size:0.8em;line-height:1.5;margin:0}}
.lang-bar{{text-align:right;margin-bottom:8px}}
.lbtn{{padding:5px 14px;background:rgba(255,255,255,0.04);border:1px solid var(--bd);border-radius:8px;color:var(--t2);cursor:pointer;font-size:0.78em;margin-left:4px;transition:all .2s}}
.lbtn.on{{background:rgba(91,156,245,0.15);border-color:var(--bl);color:var(--bl)}}
.fields{{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}}
.fields span{{padding:5px 14px;background:rgba(91,156,245,0.12);border-radius:20px;font-size:0.82em;color:var(--bl)}}
.disc{{background:#FFF3CD;border:1px solid #FFEAA7;border-radius:10px;padding:14px 22px;margin-top:22px;font-size:0.82em;color:#856404}}
@media(max-width:768px){{.cards{{flex-direction:column}}.hdr{{padding:20px}}}}
</style>
</head>
<body>
<div class="wrap">
<div class="lang-bar"><button class="lbtn on" id="lben">English</button><button class="lbtn" id="lbko">한국어</button></div>

<div class="hdr">
<h1>📊 Research Portfolio Report</h1>
<p class="sub">Nak Cho Choi (최낙초) — Samsung Display Principal Engineer | 25+ Years in Display Technology | Google Scholar + KIPRIS</p>
</div>

<div class="cards">
<div class="card tl"><div class="val">{S['total']}</div><div class="lbl" data-en="Total IP Assets" data-ko="총 IP 자산">Total IP Assets</div></div>
<div class="card kr"><div class="val">{S['kr_patents']}</div><div class="lbl" data-en="KR Patents" data-ko="한국 특허">KR Patents</div></div>
<div class="card us"><div class="val">{S['us_patents']}</div><div class="lbl" data-en="US Patents" data-ko="미국 특허">US Patents</div></div>
<div class="card pp"><div class="val">{S['papers']}</div><div class="lbl" data-en="Papers" data-ko="논문">Papers</div></div>
<div class="card hl"><div class="val">{S['h_index']}</div><div class="lbl">h-index</div></div>
<div class="card"><div class="val">{S['total_cites']:,}</div><div class="lbl" data-en="Citations" data-ko="인용">Citations</div></div>
</div>

<div class="insight">
<h3 data-en="🔍 Key Insights" data-ko="🔍 핵심 인사이트">🔍 Key Insights</h3>
<ul>
<li data-en="Total {S['total']} IP assets: {S['kr_patents']} Korean patents + {S['us_patents']} US patents + {S['papers']} papers — dual-track IP strategy" data-ko="총 {S['total']}건 IP 자산: 한국 특허 {S['kr_patents']}건 + 미국 특허 {S['us_patents']}건 + 논문 {S['papers']}건">Total {S['total']} IP assets: {S['kr_patents']} Korean patents + {S['us_patents']} US patents + {S['papers']} papers — dual-track IP strategy</li>
<li data-en="KR tech: LCD 96 | OLED 33 | Micro LED 10 (by IPC)" data-ko="한국 특허 기술: LCD 96건 | OLED 33건 | Micro LED 10건 (IPC 기준)">KR tech: LCD 96 | OLED 33 | Micro LED 10 (by IPC)</li>
<li data-en="Career: LCD (2001-2017) → OLED (2017-2022) → Micro LED + Automotive (2021-2026) → TFT Reliability (2026.5+)" data-ko="경력: LCD (2001-2017) → OLED (2017-2022) → Micro LED + Automotive (2021-2026) → TFT 신뢰성 (2026.5+)">Career: LCD (2001-2017) → OLED (2017-2022) → Micro LED + Automotive (2021-2026) → TFT Reliability (2026.5+)</li>
<li data-en="h-index 14, i10-index 22, total {S['total_cites']:,} citations — solid impact in display technology" data-ko="h-index 14, i10-index 22, 총 {S['total_cites']:,}회 인용 — 디스플레이 분야 견고한 영향력">h-index 14, i10-index 22, total {S['total_cites']:,} citations — solid impact in display technology</li>
</ul>
</div>

<div class="tables-section">
<h2 data-en="📋 Patent & Paper Lists (click to expand)" data-ko="📋 특허 및 논문 목록 (클릭하여 펼치기)">📋 Patent & Paper Lists (click to expand)</h2>
<details><summary data-en="🇰🇷 Korean Patents" data-ko="🇰🇷 한국 특허">🇰🇷 Korean Patents</summary> <span>{len(KR)} items</span>
<input class="inp" id="krFilter" oninput="filterTable('kr')" placeholder="Search title, IPC, app number..." style="margin-top:8px">
<div class="tbl-info" id="krInfo">{len(KR)} items</div>
<div class="tbl-wrap"><table><thead><tr><th>#</th><th>App Date</th><th>St</th><th>Tech</th><th>Title</th><th>App Number</th></tr></thead><tbody>{kr_rows()}</tbody></table></div>
</details>
<details><summary data-en="🇺🇸 US Patents (Google Scholar)" data-ko="🇺🇸 미국 특허 (Google Scholar)">🇺🇸 US Patents (Google Scholar)</summary> <span>{len(US)} items</span>
<input class="inp" id="usFilter" oninput="filterTable('us')" placeholder="Search title, author..." style="margin-top:8px">
<div class="tbl-info" id="usInfo">{len(US)} items</div>
<div class="tbl-wrap"><table><thead><tr><th>#</th><th>Year</th><th>Role</th><th>Cite</th><th>Tech</th><th>Title</th></tr></thead><tbody>{us_rows()}</tbody></table></div>
</details>
<details><summary data-en="📄 Papers (Google Scholar)" data-ko="📄 논문 (Google Scholar)">📄 Papers (Google Scholar)</summary> <span>{len(PP)} items</span>
<input class="inp" id="ppFilter" oninput="filterTable('pp')" placeholder="Search title, author, venue..." style="margin-top:8px">
<div class="tbl-info" id="ppInfo">{len(PP)} items</div>
<div class="tbl-wrap"><table><thead><tr><th>#</th><th>Year</th><th>Cite</th><th>Tech</th><th>Title</th><th>Venue</th></tr></thead><tbody>{pp_rows()}</tbody></table></div>
</details>
</div>

<div class="plot-box"><div id="dashboard" style="width:100%;height:1800px"></div></div>

<div class="disc">
⚠️ <b data-en="Disclaimer" data-ko="면책조항">Disclaimer</b>: <span data-en="This report combines Google Scholar and KIPRIS data. Technology classification uses IPC codes and keyword matching. Data as of 2026-08-09." data-ko="본 보고서는 Google Scholar와 KIPRIS 데이터를 통합 분석했습니다. 기술 분류는 IPC 코드와 키워드 매칭 기반입니다. 데이터 기준일: 2026-08-09.">This report combines Google Scholar and KIPRIS data. Technology classification uses IPC codes and keyword matching. Data as of 2026-08-09.</span>
</div>
</div>

<script>
var C={CHARTS_JSON};var KR={KR_JSON};var US={US_JSON};var PP={PP_JSON};var L='en';

document.getElementById('lben').onclick=function(){{setLang('en')}};
document.getElementById('lbko').onclick=function(){{setLang('ko')}};
function setLang(l){{L=l;document.getElementById('lben').className='lbtn'+(l==='en'?' on':'');document.getElementById('lbko').className='lbtn'+(l==='ko'?' on':'');document.querySelectorAll('[data-en][data-ko]').forEach(function(e){{if(e.tagName==='INPUT')e.placeholder=l==='ko'?e.getAttribute('data-ko'):e.getAttribute('data-en');else e.textContent=l==='ko'?e.getAttribute('data-ko'):e.getAttribute('data-en')}});}}

function esc(s){{return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}}

function filterTable(t){{
var f=document.getElementById((t==='pp'?'pp':t)+'Filter').value.toLowerCase();
var d=t==='kr'?KR:t==='us'?US:PP;
var fd=f?d.filter(function(p){{
if(t==='kr')return(p.title+p.ipc+p.app_number).toLowerCase().indexOf(f)!==-1;
if(t==='us')return(p.title||'').toLowerCase().indexOf(f)!==-1||(p.authors||'').toLowerCase().indexOf(f)!==-1;
return(p.title||'').toLowerCase().indexOf(f)!==-1||(p.venue||'').toLowerCase().indexOf(f)!==-1;
}}):d;
document.getElementById((t==='pp'?'pp':t)+'Info').textContent=fd.length+' / '+d.length+' items';
var h='';fd.forEach(function(p,i){{
var ti=(p.title||'').substring(0,70);
if(t==='kr'){{var sc=p.status==='등록'?'reg':'pub';h+='<tr><td>'+(i+1)+'</td><td>'+esc(p.app_date||'')+'</td><td><span class="tag '+sc+'">'+esc(p.status||'')+'</span></td><td><span class="tag">'+esc(p.tech||'')+'</span></td><td title="'+esc(p.title||'')+'">'+ti+'</td><td style="font-family:monospace;font-size:0.75em">'+esc(p.app_number||'')+'</td></tr>';}}
else if(t==='us'){{var rc=p.lead?'lead':'co',rt=p.lead?'Lead':'Co';h+='<tr><td>'+(i+1)+'</td><td>'+p.year+'</td><td><span class="tag '+rc+'">'+rt+'</span></td><td>'+(p.cites||0)+'</td><td><span class="tag">'+esc(p.tech||'')+'</span></td><td title="'+esc(p.title||'')+'">'+ti+'</td></tr>';}}
else{{h+='<tr><td>'+(i+1)+'</td><td>'+p.year+'</td><td>'+(p.cites||0)+'</td><td><span class="tag">'+esc(p.tech||'')+'</span></td><td title="'+esc(p.title||'')+'">'+ti+'</td><td style="color:#999;font-size:0.8em">'+esc(p.venue||'')+'</td></tr>';}}
}});
document.querySelector('details:nth-of-type('+(t==='kr'?1:t==='us'?2:3)+') .tbl-wrap tbody').innerHTML=h;
}}

// PROFESSIONAL DASHBOARD (matching integrated_report.html)
(function(){{
var isKo=L==='ko';
var cfg={{paper_bgcolor:'#fff',plot_bgcolor:'#fff',font:{{color:'#555',size:12}}}};
var m={{t:50,b:40,l:60,r:30}};
var layout={{paper_bgcolor:'#fff',plot_bgcolor:'#fff',showlegend:true,legend:{{x:1.02,y:0.5,bgcolor:'rgba(255,255,255,0.9)'}},margin:{{t:120,b:40,l:60,r:80}}}};

// Build subplots (4 rows x 3 cols)
var rows=4,cols=3;
var sp=[];
for(var r=0;r<rows;r++){{var row=[];for(var c=0;c<cols;c++)row.push({{}});sp.push(row)}}
sp[0][0]={{type:'indicator'}};sp[0][1]={{type:'pie'}};sp[0][2]={{type:'bar'}};
sp[1][0]={{type:'scatter',colspan:2}};sp[1][1]=null;sp[1][2]={{type:'bar'}};
sp[2][0]={{type:'heatmap',colspan:2}};sp[2][1]=null;sp[2][2]={{type:'bar'}};
sp[3][0]={{type:'table',colspan:3}};sp[3][1]=null;sp[3][2]=null;

var subtitles=[
isKo?'인용 영향력 지표':'Citation Impact',isKo?'포트폴리오 구성':'Portfolio Composition',isKo?'한국 특허 기술 분류':'KR Patent Tech',
isKo?'연도별 발행 추이':'Yearly Trend',isKo?'미국 특허 Top 10':'US Patent Top 10',
isKo?'기술 진화 히트맵':'Technology Evolution',isKo?'최근 3년 (2024-2026)':'Recent 3 Years',
isKo?'핵심 통계':'Key Statistics','','',
];

var is=Plotly.newPlot('dashboard',[],layout,{{rows:rows,cols:cols,specs:sp}});
var traces=[];

// (1,1) Indicator: h-index
traces.push({{type:'indicator',mode:'number+gauge',value:{S['h_index']},title:{{text:'h-index: {S["h_index"]}<br>i10: {S["i10_index"]} | Cites: {S["total_cites"]:,}'}},gauge:{{axis:{{range:[0,30]}},bar:{{color:'#2C3E50'}},steps:[{{range:[0,10],color:'#E8F8F5'}},{{range:[10,20],color:'#A3E4D7'}},{{range:[20,30],color:'#1ABC9C'}}]}},number:{{font:{{size:36}}}},domain:{{row:0,column:0}}}});

// (1,2) Pie: Portfolio
traces.push({{type:'pie',labels:['KR Patents','US Patents','Papers'],values:[{S['kr_patents']},{S['us_patents']},{S['papers']}],marker:{{colors:['#3498DB','#E74C3C','#2ECC71']}},textinfo:'label+value+percent',hole:0.35,showlegend:false,domain:{{row:0,column:1}}}});

// (1,3) Bar: KR tech
var techs=Object.entries(C.kr_tech||{{}}).filter(function(e){{return e[1]>0}}).sort(function(a,b){{return a[1]-b[1]}});
traces.push({{type:'bar',x:techs.map(function(t){{return t[1]}}),y:techs.map(function(t){{return t[0]}}),orientation:'h',marker:{{color:techs.map(function(t){{return t[0]==='LCD'?'#E74C3C':t[0]==='OLED'?'#3498DB':t[0]==='Micro LED'?'#2ECC71':'#999'}})}},text:techs.map(function(t){{return t[1]}}),textposition:'outside',showlegend:false,xaxis:'x3',yaxis:'y3'}});

// (2,1) Stacked area: yearly trend
var years=Object.keys(Object.assign({{}},C.kr_yearly||{{}},C.us_yearly||{{}},C.paper_yearly||{{}})).map(Number).filter(function(y){{return y>=2000&&y<=2026}}).sort(function(a,b){{return a-b}});
var krY=years.map(function(y){{return(C.kr_yearly||{{}})[y]||0}}),usY=years.map(function(y){{return(C.us_yearly||{{}})[y]||0}}),ppY=years.map(function(y){{return(C.paper_yearly||{{}})[y]||0}});
traces.push({{type:'scatter',x:years,y:krY,mode:'lines',name:'KR Patents',fill:'tozeroy',line:{{color:'#3498DB',width:2}},stackgroup:'all',xaxis:'x4',yaxis:'y4'}});
traces.push({{type:'scatter',x:years,y:usY,mode:'lines',name:'US Patents',fill:'tonexty',line:{{color:'#E74C3C',width:2}},stackgroup:'all',xaxis:'x4',yaxis:'y4'}});
traces.push({{type:'scatter',x:years,y:ppY,mode:'lines',name:'Papers',fill:'tonexty',line:{{color:'#2ECC71',width:2}},stackgroup:'all',xaxis:'x4',yaxis:'y4'}});

// (2,3) Top 10 US
var top10=US.slice().sort(function(a,b){{return(b.cites||0)-(a.cites||0)}}).slice(0,10);
traces.push({{type:'bar',x:top10.map(function(t){{return t.cites||0}}).reverse(),y:top10.map(function(t){{return(t.title||'').substring(0,50)}}).reverse(),orientation:'h',marker:{{color:'#E74C3C'}},text:top10.map(function(t){{return t.cites||0}}).reverse(),textposition:'outside',showlegend:false,xaxis:'x6',yaxis:'y6'}});

// (3,1) Heatmap: tech evolution
var htechs=['LCD','OLED','Micro LED','TFT','Driving','Panel'];
var hdata=htechs.map(function(tech){{return years.map(function(y){{return KR.filter(function(p){{return p.year===y&&p.tech===tech}}).length}})}});
traces.push({{type:'heatmap',z:hdata,x:years,y:htechs,colorscale:'YlOrRd',showscale:true,text:hdata.map(function(r){{return r.map(function(v){{return v>0?String(v):''}})}}),texttemplate:'%{{text}}',textfont:{{size:10}},colorbar:{{title:'Count'}},xaxis:'x7',yaxis:'y7'}});

// (3,3) Recent 3 years
var rY=[2024,2025,2026];
traces.push({{type:'bar',x:rY.map(String),y:rY.map(function(y){{return krY[years.indexOf(y)]||0}}),name:'KR Patents',marker:{{color:'#3498DB'}},xaxis:'x9',yaxis:'y9'}});
traces.push({{type:'bar',x:rY.map(String),y:rY.map(function(y){{return usY[years.indexOf(y)]||0}}),name:'US Patents',marker:{{color:'#E74C3C'}},xaxis:'x9',yaxis:'y9'}});
traces.push({{type:'bar',x:rY.map(String),y:rY.map(function(y){{return ppY[years.indexOf(y)]||0}}),name:'Papers',marker:{{color:'#2ECC71'}},xaxis:'x9',yaxis:'y9'}});

// (4,1) Summary table
traces.push({{type:'table',header:{{values:['Metric','Value','Note'],fill:{{color:'#2C3E50'}},font:{{color:'white',size:12}},align:'left'}},
cells:{{values:[['Total IP','KR Patents','US Patents','Papers','h-index','i10-index','Citations','Lead Inventor (KR)','Lead Inventor (US)','Period'],
['{S["total"]}','{S["kr_patents"]}','{S["us_patents"]}','{S["papers"]}','{S["h_index"]}','{S["i10_index"]}','{S["total_cites"]:,}','70','45','2005-2026'],
['Google Scholar + KIPRIS','Registered 55','via Google Scholar','via Google Scholar','','','','of 154 KR patents','of 93 US patents','22 years']],
fill:{{color:[['#F8F9FA','white','#F8F9FA','white','#F8F9FA']]}},
font:{{size:11}},align:'left'}},
domain:{{row:3,column:0}}}});

Plotly.react('dashboard',traces,Object.assign({{}},layout,{{title:{{text:'<b>Research Portfolio: Nak Cho Choi</b><br><span style="font-size:13px;color:#888">Samsung Display Principal Engineer | {S["total"]} IP Assets | 2026-08-09</span>',x:0.5,font:{{size:20}}}}}},{{
'xaxis3':{{}}, 'yaxis3':{{}},
'xaxis4':{{title:'Year'}}, 'yaxis4':{{title:'Publications'}},
'xaxis6':{{title:'Citations'}}, 'yaxis6':{{}},
'xaxis7':{{title:'Year'}}, 'yaxis7':{{}},
'xaxis9':{{title:'Year'}}, 'yaxis9':{{title:'Count'}},
}}));
}})();
</script>
</body>
</html>'''

out='frontend/index.html'
with open(out,'w',encoding='utf-8') as f: f.write(html)
import base64
with open(out,'rb') as f: b64=base64.b64encode(f.read()).decode()
print(f'OK: {out} ({len(html):,} bytes)')
print(f'Subplots: yes, 4x3 dashboard with gauge, pie, stacked area, heatmap, bars, table')
