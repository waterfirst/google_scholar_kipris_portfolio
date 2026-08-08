# -*- coding: utf-8 -*-
"""Individual Plotly charts - no subplot overlap issues."""
import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')

with open('portfolio_data.json','r',encoding='utf-8') as f: D=json.load(f)
P=D['profile'];S=P['stats'];C=D['charts'];KR=D['kr_patents'];US=D['us_patents'];PP=D['papers']

def esc(s): return str(s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def kr_rows():
    r=[]
    for i,p in enumerate(KR):
        st='reg' if p['status']=='등록' else 'pub'
        r.append(f'<tr><td>{i+1}</td><td>{esc(p["app_date"])}</td><td><span class="tag {st}">{esc(p["status"])}</span></td><td><span class="tag">{esc(p["tech"])}</span></td><td title="{esc(p["title"])}">{esc(p["title"])[:70]}</td><td style="font-family:monospace;font-size:0.75em">{esc(p["app_number"])}</td></tr>')
    return '\n'.join(r)

def us_rows():
    r=[]
    for i,p in enumerate(US):
        rc='lead' if p.get('lead') else 'co'; rt='Lead' if p.get('lead') else 'Co'
        r.append(f'<tr><td>{i+1}</td><td>{p["year"]}</td><td><span class="tag {rc}">{rt}</span></td><td>{p.get("cites",0)}</td><td><span class="tag">{esc(p["tech"])}</span></td><td title="{esc(p["title"])}">{esc(p["title"])[:70]}</td></tr>')
    return '\n'.join(r)

def pp_rows():
    r=[]
    for i,p in enumerate(PP):
        r.append(f'<tr><td>{i+1}</td><td>{p["year"]}</td><td>{p.get("cites",0)}</td><td><span class="tag">{esc(p["tech"])}</span></td><td title="{esc(p["title"])}">{esc(p["title"])[:70]}</td><td style="color:var(--t2);font-size:0.8em">{esc(p.get("venue",""))}</td></tr>')
    return '\n'.join(r)

CJS=json.dumps(C,ensure_ascii=False); KJS=json.dumps(KR,ensure_ascii=False); UJS=json.dumps(US,ensure_ascii=False); PJS=json.dumps(PP,ensure_ascii=False)

html=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Research Portfolio - Nak Cho Choi</title>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
:root{{--bg:#0a0a1a;--card:rgba(255,255,255,0.035);--bd:rgba(255,255,255,0.06);--tx:#c8c8d4;--t2:#8888a0;--bl:#5b9cf5;--rd:#f56565;--gn:#68d391;--or:#f6ad55;--pr:#b794f4}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter','Noto Sans KR','Segoe UI',sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;color:var(--tx)}}
.wrap{{max-width:1500px;margin:0 auto;padding:20px}}
.hdr{{background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);padding:28px 40px;border-radius:16px;margin-bottom:22px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.15)}}
.hdr h1{{margin:0;font-size:2em;font-weight:800;color:#fff}}
.hdr .sub{{opacity:0.8;font-size:0.95em;margin-top:6px;font-weight:300;color:#ccc}}
.cards{{display:flex;gap:14px;margin-bottom:22px;flex-wrap:wrap}}
.card{{flex:1;min-width:130px;background:#fff;border-radius:12px;padding:20px 16px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.08);border-top:4px solid var(--bl)}}
.card .val{{font-size:1.7em;font-weight:700;color:#2C3E50}}
.card .lbl{{color:var(--t2);font-size:0.72em;text-transform:uppercase;letter-spacing:1px;margin-top:4px}}
.card.hl{{border-top-color:var(--rd)}}.card.kr{{border-top-color:var(--bl)}}.card.us{{border-top-color:var(--rd)}}.card.pp{{border-top-color:var(--gn)}}.card.tl{{border-top-color:var(--or)}}
.insight{{background:#fff;border-radius:12px;padding:20px 24px;margin-bottom:22px;box-shadow:0 2px 12px rgba(0,0,0,0.06);border-left:4px solid var(--or)}}
.insight h3{{color:#E67E22;font-size:0.95em;margin:0 0 8px}}
.insight ul{{margin:0;padding-left:20px;color:#7D6608;font-size:0.85em;line-height:1.7}}
.sec{{background:#fff;border-radius:12px;padding:20px 24px;margin-bottom:22px;box-shadow:0 2px 12px rgba(0,0,0,0.06)}}
.sec h2{{color:#2C3E50;font-size:1.1em;margin:0 0 14px;border-bottom:2px solid var(--bl);padding-bottom:8px}}
.chart-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.chart-box{{background:#fff;border-radius:8px;padding:12px;min-height:380px;border:1px solid #eee}}
.chart-wide{{grid-column:1/-1;min-height:400px}}
details{{margin-bottom:8px}}
summary{{cursor:pointer;padding:10px 14px;background:#F8F9FA;border-radius:8px;font-size:0.88em;font-weight:500;color:#2C3E50;display:flex;justify-content:space-between}}
summary:hover{{background:#E8F0FE}}
summary span{{color:var(--t2);font-size:0.85em}}
.tbl-wrap{{max-height:480px;overflow-y:auto;border-radius:6px;border:1px solid #eee;margin-top:8px}}
.tbl-wrap table{{width:100%;border-collapse:collapse;font-size:0.78em}}
.tbl-wrap thead{{position:sticky;top:0;z-index:1}}
.tbl-wrap th{{background:#2C3E50;color:#fff;padding:8px 6px;text-align:left;font-weight:600;font-size:0.76em;text-transform:uppercase}}
.tbl-wrap td{{padding:6px;border-bottom:1px solid #eee;color:#444;max-width:360px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.tbl-wrap tr:nth-child(even) td{{background:#F8F9FA}}
.tbl-wrap tr:hover td{{background:#E8F0FE}}
.tag{{display:inline-block;padding:2px 8px;border-radius:5px;font-size:0.72em;font-weight:600}}
.tag.lead{{background:rgba(245,101,101,0.15);color:#d32f2f}}
.tag.co{{background:#eee;color:#999}}
.tag.reg{{background:rgba(104,211,145,0.15);color:#2E7D32}}
.tag.pub{{background:rgba(91,156,245,0.15);color:#1565C0}}
.inp{{width:100%;padding:8px 14px;background:#f5f5f5;border:1px solid #ddd;border-radius:8px;color:#333;font-size:0.84em;outline:none;margin-bottom:10px}}
.inp:focus{{border-color:var(--bl);background:#fff}}
.tbl-info{{color:#999;font-size:0.8em;margin-bottom:6px}}
.timeline{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:16px}}
.phase{{background:#f8f9fa;border-radius:12px;padding:16px;border-left:4px solid var(--bl)}}
.phase.p1{{border-color:#E74C3C}}.phase.p2{{border-color:#3498DB}}.phase.p3{{border-color:#2ECC71}}.phase.p4{{border-color:#F39C12}}
.phase h4{{color:#2C3E50;font-size:0.88em;margin:0 0 6px}}
.phase p{{color:#666;font-size:0.8em;line-height:1.5;margin:0}}
.lang-bar{{text-align:right;margin-bottom:8px}}
.lbtn{{padding:5px 14px;background:rgba(255,255,255,0.04);border:1px solid var(--bd);border-radius:8px;color:var(--t2);cursor:pointer;font-size:0.78em;margin-left:4px}}
.lbtn.on{{background:rgba(91,156,245,0.15);border-color:var(--bl);color:var(--bl)}}
.fields{{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}}
.fields span{{padding:5px 14px;background:#EBF5FB;border-radius:20px;font-size:0.82em;color:#2980B9}}
.disc{{background:#FFF3CD;border:1px solid #FFEAA7;border-radius:10px;padding:14px 22px;margin-top:22px;font-size:0.82em;color:#856404}}
@media(max-width:768px){{.chart-grid{{grid-template-columns:1fr}}.cards{{flex-direction:column}}}}
</style>
</head>
<body>
<div class="wrap">
<div class="lang-bar"><button class="lbtn on" id="lben">English</button><button class="lbtn" id="lbko">한국어</button></div>
<div class="hdr"><h1>📊 Research Portfolio Report</h1><p class="sub">Nak Cho Choi (최낙초) — Samsung Display Principal Engineer | 25+ Years in Display Technology</p></div>
<div class="cards">
<div class="card tl"><div class="val">{S['total']}</div><div class="lbl" data-en="Total IP" data-ko="총 IP">Total IP</div></div>
<div class="card kr"><div class="val">{S['kr_patents']}</div><div class="lbl" data-en="KR Patents" data-ko="한국 특허">KR Patents</div></div>
<div class="card us"><div class="val">{S['us_patents']}</div><div class="lbl" data-en="US Patents" data-ko="미국 특허">US Patents</div></div>
<div class="card pp"><div class="val">{S['papers']}</div><div class="lbl" data-en="Papers" data-ko="논문">Papers</div></div>
<div class="card hl"><div class="val">{S['h_index']}</div><div class="lbl">h-index</div></div>
<div class="card"><div class="val">{S['total_cites']:,}</div><div class="lbl" data-en="Citations" data-ko="인용">Citations</div></div>
</div>
<div class="insight"><h3 data-en="Key Insights" data-ko="핵심 인사이트">Key Insights</h3><ul>
<li data-en="Total {S['total']} IP assets: {S['kr_patents']} KR + {S['us_patents']} US + {S['papers']} papers" data-ko="총 {S['total']}건: 한국 {S['kr_patents']} + 미국 {S['us_patents']} + 논문 {S['papers']}">Total {S['total']} IP assets: {S['kr_patents']} KR + {S['us_patents']} US + {S['papers']} papers</li>
<li data-en="KR tech: LCD 96 | OLED 33 | Micro LED 10 | TFT 6 (by IPC classification)" data-ko="한국 특허 기술분류: LCD 96건 | OLED 33건 | Micro LED 10건 | TFT 6건 (IPC 기준)">KR tech: LCD 96 | OLED 33 | Micro LED 10 | TFT 6 (by IPC classification)</li>
<li data-en="Career: LCD(2001-2017) → OLED(2017-2022) → Micro LED + Automotive(2021-2026) → TFT Reliability(2026.5+)" data-ko="경력: LCD(2001-2017) → OLED(2017-2022) → Micro LED + Automotive(2021-2026) → TFT 신뢰성(2026.5+)">Career: LCD(2001-2017) → OLED(2017-2022) → Micro LED + Automotive(2021-2026) → TFT Reliability(2026.5+)</li>
<li data-en="h-index {S['h_index']}, total {S['total_cites']:,} citations — solid impact in display technology R&D" data-ko="h-index {S['h_index']}, 총 인용 {S['total_cites']:,}회 — 디스플레이 R&D 분야 견고한 영향력">h-index {S['h_index']}, total {S['total_cites']:,} citations — solid impact in display technology R&D</li>
</ul></div>

<div class="sec"><h2 data-en="📈 Charts & Analytics" data-ko="📈 차트 & 분석">📈 Charts & Analytics</h2>
<div class="chart-grid">
<div class="chart-box" id="c1"></div>
<div class="chart-box" id="c2"></div>
<div class="chart-box chart-wide" id="c3"></div>
<div class="chart-box" id="c4"></div>
<div class="chart-box" id="c5"></div>
<div class="chart-box chart-wide" id="c6"></div>
</div></div>

<div class="sec"><h2 data-en="📋 Patent & Paper Lists" data-ko="📋 특허 및 논문 목록">📋 Patent & Paper Lists</h2>
<details open><summary><span data-en="KR Patents (KIPRIS)" data-ko="한국 특허 (KIPRIS)">KR Patents (KIPRIS)</span><span>{len(KR)} items</span></summary>
<input class="inp" id="krFilter" oninput="ft('kr')" placeholder="Search...">
<div class="tbl-info" id="krInfo">{len(KR)} items</div>
<div class="tbl-wrap"><table><thead><tr><th>#</th><th>Date</th><th>St</th><th>Tech</th><th>Title</th><th>App Number</th></tr></thead><tbody id="krTbody">{kr_rows()}</tbody></table></div></details>
<details><summary><span data-en="US Patents (Google Scholar)" data-ko="미국 특허 (Google Scholar)">US Patents (Google Scholar)</span><span>{len(US)} items</span></summary>
<input class="inp" id="usFilter" oninput="ft('us')" placeholder="Search...">
<div class="tbl-info" id="usInfo">{len(US)} items</div>
<div class="tbl-wrap"><table><thead><tr><th>#</th><th>Year</th><th>Role</th><th>Cite</th><th>Tech</th><th>Title</th></tr></thead><tbody id="usTbody">{us_rows()}</tbody></table></div></details>
<details><summary><span data-en="Papers (Google Scholar)" data-ko="논문 (Google Scholar)">Papers (Google Scholar)</span><span>{len(PP)} items</span></summary>
<input class="inp" id="ppFilter" oninput="ft('pp')" placeholder="Search...">
<div class="tbl-info" id="ppInfo">{len(PP)} items</div>
<div class="tbl-wrap"><table><thead><tr><th>#</th><th>Year</th><th>Cite</th><th>Tech</th><th>Title</th><th>Venue</th></tr></thead><tbody id="ppTbody">{pp_rows()}</tbody></table></div></details></div>

<div class="disc">⚠️ <b data-en="Disclaimer" data-ko="면책조항">Disclaimer</b>: <span data-en="Combined Google Scholar + KIPRIS analysis. Tech classification via IPC codes & keyword matching. Data as of 2026-08-09." data-ko="Google Scholar + KIPRIS 통합 분석. 기술 분류는 IPC 코드 및 키워드 매칭 기반. 데이터 기준: 2026-08-09.">Combined Google Scholar + KIPRIS analysis. Tech classification via IPC codes & keyword matching. Data as of 2026-08-09.</span></div>
</div>

<script>
var C={CJS},KR={KJS},US={UJS},PP={PJS},L='en';

document.getElementById('lben').onclick=function(){{setLang('en')}};
document.getElementById('lbko').onclick=function(){{setLang('ko')}};
function setLang(l){{L=l;document.getElementById('lben').className='lbtn'+(l==='en'?' on':'');document.getElementById('lbko').className='lbtn'+(l==='ko'?' on':'');document.querySelectorAll('[data-en][data-ko]').forEach(function(e){{e.textContent=l==='ko'?e.getAttribute('data-ko'):e.getAttribute('data-en')}});}}

function ft(t){{
var f=document.getElementById((t==='pp'?'pp':t)+'Filter').value.toLowerCase();
var d=t==='kr'?KR:t==='us'?US:PP;
var fd=f?d.filter(function(p){{
if(t==='kr')return(p.title+p.ipc+p.app_number).toLowerCase().indexOf(f)!==-1;
if(t==='us')return(p.title||'').toLowerCase().indexOf(f)!==-1||(p.authors||'').toLowerCase().indexOf(f)!==-1;
return(p.title||'').toLowerCase().indexOf(f)!==-1||(p.venue||'').toLowerCase().indexOf(f)!==-1;
}}):d;
document.getElementById((t==='pp'?'pp':t)+'Info').textContent=fd.length+' / '+d.length+' items';
var h='',esc2=function(s){{return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}};
fd.forEach(function(p,i){{
var ti=esc2((p.title||'').substring(0,70));
if(t==='kr'){{var sc=p.status==='등록'?'reg':'pub';h+='<tr><td>'+(i+1)+'</td><td>'+esc2(p.app_date||'')+'</td><td><span class="tag '+sc+'">'+esc2(p.status||'')+'</span></td><td><span class="tag">'+esc2(p.tech||'')+'</span></td><td title="'+esc2(p.title||'')+'">'+ti+'</td><td style="font-family:monospace;font-size:0.75em">'+esc2(p.app_number||'')+'</td></tr>';}}
else if(t==='us'){{var rc=p.lead?'lead':'co',rt=p.lead?'Lead':'Co';h+='<tr><td>'+(i+1)+'</td><td>'+p.year+'</td><td><span class="tag '+rc+'">'+rt+'</span></td><td>'+(p.cites||0)+'</td><td><span class="tag">'+esc2(p.tech||'')+'</span></td><td title="'+esc2(p.title||'')+'">'+ti+'</td></tr>';}}
else{{h+='<tr><td>'+(i+1)+'</td><td>'+p.year+'</td><td>'+(p.cites||0)+'</td><td><span class="tag">'+esc2(p.tech||'')+'</span></td><td title="'+esc2(p.title||'')+'">'+ti+'</td><td style="color:#999;font-size:0.8em">'+esc2(p.venue||'')+'</td></tr>';}}
}});
document.getElementById(t+'Tbody').innerHTML=h;
}}

// INDIVIDUAL CHARTS - no overlap
setTimeout(function(){{
var isKo=L==='ko';
var bg='#fff', fg='#555';
var m={{t:50,b:40,l:50,r:20}};
var lo={{paper_bgcolor:bg,plot_bgcolor:bg,font:{{color:fg,size:11}},margin:m}};

// C1: KR Tech Pie
var techs=Object.entries(C.kr_tech||{{}}).filter(function(e){{return e[1]>0}}).sort(function(a,b){{return b[1]-a[1]}});
Plotly.newPlot('c1',[{{type:'pie',labels:techs.map(function(t){{return t[0]}}),values:techs.map(function(t){{return t[1]}}),marker:{{colors:techs.map(function(t){{return t[0]==='LCD'?'#E74C3C':t[0]==='OLED'?'#3498DB':t[0]==='Micro LED'?'#2ECC71':'#95A5A6'}})}},textinfo:'label+percent',hole:0.35}}],Object.assign({{}},lo,{{title:isKo?'한국 특허 기술 분류 (IPC)':'KR Patent Tech (IPC)'}}));

// C2: Yearly Stacked Bar
var years=Object.keys(Object.assign({{}},C.kr_yearly||{{}},C.us_yearly||{{}},C.paper_yearly||{{}})).map(Number).filter(function(y){{return y>=2000&&y<=2026}}).sort(function(a,b){{return a-b}});
var ykr=years.map(function(y){{return(C.kr_yearly||{{}})[y]||0}}),yus=years.map(function(y){{return(C.us_yearly||{{}})[y]||0}}),ypp=years.map(function(y){{return(C.paper_yearly||{{}})[y]||0}});
Plotly.newPlot('c2',[{{x:years,y:ykr,type:'bar',name:'KR',marker:{{color:'#3498DB'}}}},{{x:years,y:yus,type:'bar',name:'US',marker:{{color:'#E74C3C'}}}},{{x:years,y:ypp,type:'bar',name:'Paper',marker:{{color:'#2ECC71'}}}}],Object.assign({{}},lo,{{barmode:'stack',title:isKo?'연도별 발행 추이':'Yearly Output',legend:{{x:0.01,y:0.98}},xaxis:{{title:isKo?'연도':'Year'}},yaxis:{{title:isKo?'건수':'Count'}}}}));

// C3: Tech Evolution Heatmap (wide)
var htechs=['LCD','OLED','Micro LED','TFT','Driving','Panel'];
var hdata=htechs.map(function(tech){{return years.map(function(y){{return KR.filter(function(p){{return p.year===y&&p.tech===tech}}).length}})}});
Plotly.newPlot('c3',[{{z:hdata,x:years,y:htechs,type:'heatmap',colorscale:'YlOrRd',showscale:true,text:hdata.map(function(r){{return r.map(function(v){{return v>0?String(v):''}})}}),texttemplate:'%{{text}}',textfont:{{size:10}},colorbar:{{title:isKo?'건수':'Count'}}}}],Object.assign({{}},lo,{{title:isKo?'한국 특허 기술 진화 (2005-2026)':'KR Patent Tech Evolution',margin:{{t:50,b:40,l:100,r:60}},xaxis:{{title:isKo?'연도':'Year'}}}}));

// C4: US Tech Bar
var ust=Object.entries(C.us_tech||{{}}).filter(function(e){{return e[1]>0}}).sort(function(a,b){{return a[1]-b[1]}});
Plotly.newPlot('c4',[{{type:'bar',x:ust.map(function(t){{return t[1]}}),y:ust.map(function(t){{return t[0]}}),orientation:'h',marker:{{color:ust.map(function(t){{return t[0]==='LCD'?'#E74C3C':t[0]==='OLED'?'#3498DB':t[0]==='Micro LED'?'#2ECC71':'#95A5A6'}})}},text:ust.map(function(t){{return t[1]}}),textposition:'outside'}}],Object.assign({{}},lo,{{title:isKo?'미국 특허 기술 분류':'US Patent Tech',margin:{{t:50,b:30,l:120,r:40}}}}));

// C5: Top 10 US cited
var top10=US.slice().sort(function(a,b){{return(b.cites||0)-(a.cites||0)}}).slice(0,10);
Plotly.newPlot('c5',[{{type:'bar',x:top10.map(function(t){{return t.cites||0}}).reverse(),y:top10.map(function(t){{return(t.title||'').substring(0,45)}}).reverse(),orientation:'h',marker:{{color:'#E74C3C'}},text:top10.map(function(t){{return t.cites||0}}).reverse(),textposition:'outside'}}],Object.assign({{}},lo,{{title:isKo?'주발명자 Top 10 인용 (US)':'Lead Inventor Top 10 (US)',margin:{{t:50,b:30,l:80,r:50}},xaxis:{{title:isKo?'인용 수':'Citations'}}}}));

// C6: Total Trend Line (wide)
Plotly.newPlot('c6',[{{x:years,y:years.map(function(y,i){{return ykr[i]+yus[i]+ypp[i]}}),type:'scatter',mode:'lines+markers',line:{{color:'#8E44AD',width:3}},marker:{{size:7,color:'#8E44AD'}},fill:'tozeroy',name:isKo?'전체':'Total'}}],Object.assign({{}},lo,{{title:isKo?'전체 발행 추이 (KR+US+Papers)':'Total Output (KR+US+Papers)',xaxis:{{title:isKo?'연도':'Year'}},yaxis:{{title:isKo?'건수':'Count'}}}}));
}},300);
</script>
</body>
</html>'''

out='frontend/index.html'
with open(out,'w',encoding='utf-8') as f: f.write(html)
import base64
with open(out,'rb') as f: b64=base64.b64encode(f.read()).decode()
print(f'OK: {out} ({len(html):,} bytes)')
print('6 individual charts: Pie, Stacked Bar, Heatmap, Bar(H), Top10, Line')
print('No subplots - no overlap issues')
