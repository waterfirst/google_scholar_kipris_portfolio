# -*- coding: utf-8 -*-
"""Generate fully pre-rendered HTML portfolio page. JS only for tabs & charts."""
import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')

with open('portfolio_data.json','r',encoding='utf-8') as f: D=json.load(f)
P=D['profile'];S=P['stats'];C=D['charts'];KR=D['kr_patents'];US=D['us_patents'];PP=D['papers']

def esc(s): return str(s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

# Pre-render tables
def kr_rows():
    rows=[]
    for i,p in enumerate(KR[:50]):  # first 50 for performance
        st_cls='reg' if p['status']=='등록' else 'pub'
        rows.append(f'<tr><td>{i+1}</td><td style="white-space:nowrap">{esc(p["app_date"])}</td><td><span class="tag {st_cls}">{esc(p["status"])}</span></td><td><span class="tag">{esc(p["tech"])}</span></td><td title="{esc(p["title"])}">{esc(p["title"])[:80]}</td><td style="font-family:monospace;font-size:0.78em">{esc(p["app_number"])}</td></tr>')
    return '\n'.join(rows)

def us_rows():
    rows=[]
    for i,p in enumerate(US):
        r_cls='lead' if p.get('lead') else 'co'; r_txt='주발명' if p.get('lead') else '공동'
        rows.append(f'<tr><td>{i+1}</td><td>{p["year"]}</td><td><span class="tag {r_cls}">{r_txt}</span></td><td>{p.get("cites",0)}</td><td><span class="tag">{esc(p["tech"])}</span></td><td title="{esc(p["title"])}">{esc(p["title"])[:80]}</td></tr>')
    return '\n'.join(rows)

def pp_rows():
    rows=[]
    for i,p in enumerate(PP):
        rows.append(f'<tr><td>{i+1}</td><td>{p["year"]}</td><td>{p.get("cites",0)}</td><td><span class="tag">{esc(p["tech"])}</span></td><td title="{esc(p["title"])}">{esc(p["title"])[:80]}</td><td style="color:var(--text2);font-size:0.78em">{esc(p.get("venue",""))}</td></tr>')
    return '\n'.join(rows)

# Build charts JSON
CHARTS_JSON=json.dumps(C,ensure_ascii=False)

html=f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Research Portfolio - Nak Cho Choi</title>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
<style>
:root{{--bg:#0a0a1a;--bg2:#12122a;--card:rgba(255,255,255,0.03);--border:rgba(255,255,255,0.06);--text:#c8c8d4;--text2:#8888a0;--blue:#5b9cf5;--red:#f56565;--green:#68d391;--orange:#f6ad55;--purple:#b794f4}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI','Inter','Noto Sans KR',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}}
.wrap{{max-width:1440px;margin:0 auto;padding:20px}}
.hdr{{text-align:center;padding:28px 20px 10px}}
.hdr h1{{font-size:2em;font-weight:900;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-1px}}
.hdr .sub{{color:var(--text2);font-size:0.9em;margin-top:6px}}
.cards{{display:flex;gap:12px;margin:20px 0;flex-wrap:wrap}}
.card{{flex:1;min-width:120px;background:var(--card);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:14px;padding:18px 14px;text-align:center}}
.card .val{{font-size:1.7em;font-weight:800}}
.card .lbl{{color:var(--text2);font-size:0.7em;text-transform:uppercase;letter-spacing:1px;margin-top:4px}}
.card.c0{{border-top:3px solid var(--orange)}}.card.c1{{border-top:3px solid var(--blue)}}.card.c2{{border-top:3px solid var(--red)}}.card.c3{{border-top:3px solid var(--green)}}.card.c4{{border-top:3px solid var(--purple)}}
.tabs{{display:flex;gap:2px;margin-bottom:0;flex-wrap:wrap}}
.tb{{padding:10px 20px;background:rgba(255,255,255,0.03);border:1px solid transparent;border-radius:12px 12px 0 0;cursor:pointer;font-size:0.84em;font-weight:500;color:var(--text2);transition:all .2s}}
.tb:hover{{color:var(--text)}}.tb.on{{background:var(--card);border-color:var(--border);border-bottom-color:transparent;color:#fff}}
.tb .badge{{background:rgba(255,255,255,0.08);padding:1px 8px;border-radius:10px;font-size:0.75em;margin-left:6px}}
.main{{background:var(--card);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:0 14px 14px 14px;padding:24px;min-height:300px}}
.panel{{display:none}}.panel.on{{display:block}}
.chart-grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:16px}}
.chart-panel{{min-height:360px;border-radius:10px}}.chart-full{{grid-column:1/-1;min-height:380px}}
.inp{{width:100%;padding:8px 14px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:0.84em;outline:none;margin-bottom:12px}}
.inp:focus{{border-color:var(--blue)}}
.tbl-info{{color:var(--text2);font-size:0.78em;margin-bottom:8px}}
.tbl-wrap{{max-height:500px;overflow-y:auto;border-radius:8px;border:1px solid var(--border)}}
.tbl-wrap table{{width:100%;border-collapse:collapse;font-size:0.8em}}
.tbl-wrap thead{{position:sticky;top:0;z-index:1}}
.tbl-wrap th{{background:#16163a;padding:9px 7px;text-align:left;font-weight:600;color:var(--text2);font-size:0.76em;text-transform:uppercase;border-bottom:1px solid var(--border)}}
.tbl-wrap td{{padding:7px;border-bottom:1px solid rgba(255,255,255,0.03);max-width:380px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.tbl-wrap tr:hover td{{background:rgba(255,255,255,0.02)}}
.tag{{display:inline-block;padding:2px 8px;border-radius:5px;font-size:0.73em;font-weight:600}}
.tag.lead{{background:rgba(245,101,101,0.15);color:var(--red)}}
.tag.co{{background:rgba(255,255,255,0.05);color:var(--text2)}}
.tag.reg{{background:rgba(104,211,145,0.15);color:var(--green)}}
.tag.pub{{background:rgba(91,156,245,0.15);color:var(--blue)}}
.timeline{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:16px}}
.phase{{background:rgba(255,255,255,0.02);border-radius:12px;padding:16px;border-left:4px solid var(--blue)}}
.phase.p1{{border-color:var(--red)}}.phase.p2{{border-color:var(--blue)}}.phase.p3{{border-color:var(--green)}}.phase.p4{{border-color:var(--orange)}}
.phase h4{{color:#ddd;font-size:0.88em;margin-bottom:6px;margin-top:0}}
.phase p{{color:var(--text2);font-size:0.8em;line-height:1.5;margin:0}}
.lang-bar{{text-align:right;margin-bottom:8px}}
.lbtn{{padding:5px 14px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:8px;color:var(--text2);cursor:pointer;font-size:0.78em;margin-left:4px}}
.lbtn.on{{background:rgba(91,156,245,0.15);border-color:var(--blue);color:var(--blue)}}
.fields{{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}}
.fields span{{padding:5px 14px;background:rgba(91,156,245,0.1);border-radius:20px;font-size:0.8em;color:var(--blue)}}
@media(max-width:768px){{.chart-grid{{grid-template-columns:1fr}}.cards{{flex-direction:column}}}}
</style>
</head>
<body>
<div class="wrap">
<div class="lang-bar"><button class="lbtn on" id="lben">English</button><button class="lbtn" id="lbko">한국어</button></div>
<div class="hdr"><h1 id="titleText">Research Portfolio Analysis</h1><p class="sub">Integrated Patent & Paper Analysis — Google Scholar + KIPRIS</p></div>

<div class="cards">
<div class="card c0"><div class="val">{S['total']}</div><div class="lbl" data-en="Total IP" data-ko="총 IP 자산">Total IP</div></div>
<div class="card c1"><div class="val">{S['kr_patents']}</div><div class="lbl" data-en="KR Patents" data-ko="한국 특허">KR Patents</div></div>
<div class="card c2"><div class="val">{S['us_patents']}</div><div class="lbl" data-en="US Patents" data-ko="미국 특허">US Patents</div></div>
<div class="card c3"><div class="val">{S['papers']}</div><div class="lbl" data-en="Papers" data-ko="논문">Papers</div></div>
<div class="card c4"><div class="val">{S['h_index']}</div><div class="lbl">h-index</div></div>
<div class="card"><div class="val">{S['total_cites']:,}</div><div class="lbl" data-en="Citations" data-ko="인용">Citations</div></div>
</div>

<div class="tabs">
<div class="tb on" onclick="switchTab('overview')"><span data-en="Overview" data-ko="개요">Overview</span></div>
<div class="tb" onclick="switchTab('kr')"><span data-en="KR Patents" data-ko="한국 특허">KR Patents</span> <span class="badge">{len(KR)}</span></div>
<div class="tb" onclick="switchTab('us')"><span data-en="US Patents" data-ko="미국 특허">US Patents</span> <span class="badge">{len(US)}</span></div>
<div class="tb" onclick="switchTab('papers')"><span data-en="Papers" data-ko="논문">Papers</span> <span class="badge">{len(PP)}</span></div>
<div class="tb" onclick="switchTab('charts')"><span data-en="Charts" data-ko="차트">Charts</span></div>
</div>

<div class="main">
<div class="panel on" id="panel_overview">
<div class="timeline">
<div class="phase p1"><h4 data-en="Phase 1: LCD Era (2001-2017)" data-ko="Phase 1: LCD 시대 (2001-2017)">Phase 1: LCD Era (2001-2017)</h4><p data-en="TFT-LCD substrates, PVA/VA alignment, color filters. Samsung LCD Division." data-ko="TFT-LCD 기판, PVA/VA 배향, 컬러필터. 삼성전자 LCD 사업부.">TFT-LCD substrates, PVA/VA alignment, color filters. Samsung LCD Division.</p></div>
<div class="phase p2"><h4 data-en="Phase 2: OLED Transition (2017-2022)" data-ko="Phase 2: OLED 전환 (2017-2022)">Phase 2: OLED Transition (2017-2022)</h4><p data-en="Black PDL, UPC, Polarizer-free, Foldable. Led OLED Innovation." data-ko="Black PDL, UPC, Polarizer-free, Foldable. OLED Innovation 리드.">Black PDL, UPC, Polarizer-free, Foldable. Led OLED Innovation.</p></div>
<div class="phase p3"><h4 data-en="Phase 3: Micro LED + Automotive (2021-2026)" data-ko="Phase 3: Micro LED + Automotive (2021-2026)">Phase 3: Micro LED + Automotive (2021-2026)</h4><p data-en="Micro LED transfer/tiling, Automotive OLED Switchable Privacy." data-ko="Micro LED 전사·타일링, Automotive OLED Switchable Privacy.">Micro LED transfer/tiling, Automotive OLED Switchable Privacy.</p></div>
<div class="phase p4"><h4 data-en="Phase 4: TFT Reliability (2026.5-Present)" data-ko="Phase 4: TFT 신뢰성 (2026.5-현재)">Phase 4: TFT Reliability (2026.5-Present)</h4><p data-en="Development Quality Group, TFT reliability. Full-cycle display engineer." data-ko="개발품질그룹 TFT 소자 신뢰성. 풀사이클 엔지니어.">Development Quality Group, TFT reliability. Full-cycle display engineer.</p></div>
</div>
<div style="margin-top:18px"><h3 style="color:var(--text2);font-size:0.8em;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px" data-en="Research Fields" data-ko="연구 분야">Research Fields</h3>
<div class="fields">{' '.join(f'<span>{f}</span>' for f in P['fields'])}</div></div>
</div>

<div class="panel" id="panel_kr">
<input class="inp" id="krFilter" oninput="filterTable('kr')" placeholder="Search title, IPC, app#...">
<div class="tbl-info" id="krInfo">{len(KR)} items</div>
<div class="tbl-wrap"><table><thead><tr><th>#</th><th>Date</th><th>St</th><th>Tech</th><th>Title</th><th>App#</th></tr></thead><tbody>
{kr_rows()}
</tbody></table></div>
</div>

<div class="panel" id="panel_us">
<input class="inp" id="usFilter" oninput="filterTable('us')" placeholder="Search title, author...">
<div class="tbl-info" id="usInfo">{len(US)} items</div>
<div class="tbl-wrap"><table><thead><tr><th>#</th><th>Yr</th><th>Role</th><th>Cite</th><th>Tech</th><th>Title</th></tr></thead><tbody>
{us_rows()}
</tbody></table></div>
</div>

<div class="panel" id="panel_papers">
<input class="inp" id="ppFilter" oninput="filterTable('pp')" placeholder="Search title, author, venue...">
<div class="tbl-info" id="ppInfo">{len(PP)} items</div>
<div class="tbl-wrap"><table><thead><tr><th>#</th><th>Yr</th><th>Cite</th><th>Tech</th><th>Title</th><th>Venue</th></tr></thead><tbody>
{pp_rows()}
</tbody></table></div>
</div>

<div class="panel" id="panel_charts">
<div class="chart-grid"><div class="chart-panel" id="chart1"></div><div class="chart-panel" id="chart2"></div></div>
<div class="chart-grid"><div class="chart-panel" id="chart3"></div><div class="chart-panel" id="chart4"></div></div>
<div class="chart-grid"><div class="chart-panel chart-full" id="chart5"></div></div>
</div>
</div>
</div>

<script>
var CHART_DATA = {CHARTS_JSON};
var KR_DATA = {json.dumps(KR,ensure_ascii=False)};
var US_DATA = {json.dumps(US,ensure_ascii=False)};
var PP_DATA = {json.dumps(PP,ensure_ascii=False)};
var LANG='en';

// Language switching
document.getElementById('lben').onclick=function(){{setLang('en')}};
document.getElementById('lbko').onclick=function(){{setLang('ko')}};

function setLang(l){{
  LANG=l;
  document.getElementById('lben').className='lbtn'+(l==='en'?' on':'');
  document.getElementById('lbko').className='lbtn'+(l==='ko'?' on':'');
  document.querySelectorAll('[data-en][data-ko]').forEach(function(el){{
    el.textContent=l==='ko'?el.getAttribute('data-ko'):el.getAttribute('data-en');
  }});
  document.getElementById('titleText').textContent=l==='ko'?'연구 포트폴리오 분석':'Research Portfolio Analysis';
}}

// Tab switching
function switchTab(tab){{
  document.querySelectorAll('.tb').forEach(function(b){{b.className='tb'}});
  document.querySelectorAll('.panel').forEach(function(p){{p.className='panel'}});
  document.getElementById('panel_'+tab).className='panel on';
  // Highlight the correct tab
  var tabs=document.querySelectorAll('.tb');
  for(var i=0;i<tabs.length;i++){{
    if(tabs[i].textContent.toLowerCase().indexOf(tab)!==-1||(tab==='charts'&&tabs[i].textContent.toLowerCase().indexOf('chart')!==-1)||(tab==='kr'&&tabs[i].textContent.indexOf('154')!==-1)||(tab==='us'&&tabs[i].textContent.indexOf('93')!==-1)||(tab==='papers'&&tabs[i].textContent.indexOf('7')!==-1)){{
      tabs[i].className='tb on';break;
    }}
  }}
  if(tab==='charts') renderCharts();
}}

// Table filter
function filterTable(type){{
  var f=document.getElementById((type==='pp'?'pp':type)+'Filter').value.toLowerCase();
  var data=type==='kr'?KR_DATA:type==='us'?US_DATA:PP_DATA;
  var filtered=f?data.filter(function(p){{
    if(type==='kr')return(p.title+p.ipc+p.app_number).toLowerCase().indexOf(f)!==-1;
    if(type==='us')return(p.title||'').toLowerCase().indexOf(f)!==-1||(p.authors||'').toLowerCase().indexOf(f)!==-1;
    return(p.title||'').toLowerCase().indexOf(f)!==-1||(p.venue||'').toLowerCase().indexOf(f)!==-1;
  }}):data;
  document.getElementById((type==='pp'?'pp':type)+'Info').textContent=filtered.length+' / '+data.length+' items';
  var h='';
  filtered.forEach(function(p,i){{
    var title=(p.title||'').substring(0,80);
    if(type==='kr'){{
      var sc=p.status==='등록'?'reg':'pub';
      h+='<tr><td>'+(i+1)+'</td><td style="white-space:nowrap">'+(p.app_date||'')+'</td><td><span class="tag '+sc+'">'+(p.status||'')+'</span></td><td><span class="tag">'+(p.tech||'')+'</span></td><td title="'+title+'">'+title+'</td><td style="font-family:monospace;font-size:0.78em">'+(p.app_number||'')+'</td></tr>';
    }}else if(type==='us'){{
      var rc=p.lead?'lead':'co', rt=p.lead?'주발명':'공동';
      h+='<tr><td>'+(i+1)+'</td><td>'+p.year+'</td><td><span class="tag '+rc+'">'+rt+'</span></td><td>'+(p.cites||0)+'</td><td><span class="tag">'+(p.tech||'')+'</span></td><td title="'+title+'">'+title+'</td></tr>';
    }}else{{
      h+='<tr><td>'+(i+1)+'</td><td>'+p.year+'</td><td>'+(p.cites||0)+'</td><td><span class="tag">'+(p.tech||'')+'</span></td><td title="'+title+'">'+title+'</td><td style="color:var(--text2);font-size:0.78em">'+(p.venue||'')+'</td></tr>';
    }}
  }});
  document.querySelector('#panel_'+type+' .tbl-wrap tbody').innerHTML=h;
}}

// Charts
function renderCharts(){{
  setTimeout(function(){{
    var ch=CHART_DATA;
    var isKo=LANG==='ko';
    var cfg={{paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{{color:'#8888a0'}},margin:{{t:50,b:40,l:60,r:30}}}};
    var techs=Object.entries(ch.kr_tech||{{}}).filter(function(e){{return e[1]>0}}).sort(function(a,b){{return b[1]-a[1]}});
    Plotly.newPlot('chart1',[{{type:'pie',labels:techs.map(function(t){{return t[0]}}),values:techs.map(function(t){{return t[1]}}),marker:{{colors:techs.map(function(t){{return t[0]==='LCD'?'#f56565':t[0]==='OLED'?'#5b9cf5':t[0]==='Micro LED'?'#68d391':'#8888a0'}})}},textinfo:'label+value+percent',hole:0.4}}],Object.assign({{}},cfg,{{title:isKo?'한국 특허 기술 분류':'KR Patent Technology'}}));
    var years=Object.keys(Object.assign({{}},ch.kr_yearly||{{}},ch.us_yearly||{{}},ch.paper_yearly||{{}})).map(Number).filter(function(y){{return y>=2000&&y<=2026}}).sort(function(a,b){{return a-b}});
    var ykr=years.map(function(y){{return(ch.kr_yearly||{{}})[y]||0}}),yus=years.map(function(y){{return(ch.us_yearly||{{}})[y]||0}}),ypp=years.map(function(y){{return(ch.paper_yearly||{{}})[y]||0}});
    Plotly.newPlot('chart2',[{{x:years,y:ykr,type:'bar',name:isKo?'한국 특허':'KR Patents',marker:{{color:'#5b9cf5'}}}},{{x:years,y:yus,type:'bar',name:isKo?'미국 특허':'US Patents',marker:{{color:'#f56565'}}}},{{x:years,y:ypp,type:'bar',name:isKo?'논문':'Papers',marker:{{color:'#68d391'}}}}],Object.assign({{}},cfg,{{barmode:'stack',title:isKo?'연도별 포트폴리오':'Yearly Portfolio',legend:{{font:{{color:'#8888a0'}}}}}}));
    var htechs=['LCD','OLED','Micro LED','TFT','Driving','Panel'];
    var hdata=htechs.map(function(tech){{return years.map(function(y){{return KR_DATA.filter(function(p){{return p.year===y&&p.tech===tech}}).length}})}});
    Plotly.newPlot('chart3',[{{z:hdata,x:years,y:htechs,type:'heatmap',colorscale:'YlOrRd',text:hdata.map(function(r){{return r.map(function(v){{return v>0?String(v):''}})}}),texttemplate:'%{{text}}',textfont:{{color:'#333',size:11}}}}],Object.assign({{}},cfg,{{title:isKo?'한국 특허 기술 진화':'KR Patent Tech Evolution',margin:{{t:50,b:40,l:100,r:20}}}}));
    var ust=Object.entries(ch.us_tech||{{}}).filter(function(e){{return e[1]>0}}).sort(function(a,b){{return b[1]-a[1]}});
    if(ust.length)Plotly.newPlot('chart4',[{{type:'bar',x:ust.map(function(t){{return t[1]}}),y:ust.map(function(t){{return t[0]}}),orientation:'h',marker:{{color:ust.map(function(t){{return t[0]==='LCD'?'#f56565':t[0]==='OLED'?'#5b9cf5':t[0]==='Micro LED'?'#68d391':'#8888a0'}})}},text:ust.map(function(t){{return t[1]}}),textposition:'outside'}}],Object.assign({{}},cfg,{{title:isKo?'미국 특허 기술 분류':'US Patent Technology',margin:{{t:50,b:30,l:120,r:40}}}}));
    Plotly.newPlot('chart5',[{{x:years,y:years.map(function(y,i){{return ykr[i]+yus[i]+ypp[i]}}),type:'scatter',mode:'lines+markers',line:{{color:'#b794f4',width:3}},marker:{{size:8,color:'#b794f4'}},fill:'tozeroy',name:isKo?'전체':'Total'}}],Object.assign({{}},cfg,{{title:isKo?'전체 발행 추이':'Total Output Trend'}}));
  }},100);
}}
</script>
</body>
</html>'''

out='frontend/index.html'
with open(out,'w',encoding='utf-8') as f: f.write(html)
import base64
with open(out,'rb') as f: b64=base64.b64encode(f.read()).decode()
print(f'OK: {out} ({len(html):,} bytes)')
print(f'Cards: {"cards" in html}, Tabs: {"panel_overview" in html}, Tables: {"tbl-wrap" in html}')
