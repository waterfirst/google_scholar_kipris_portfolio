# -*- coding: utf-8 -*-
import sys,io;sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
import json
with open('portfolio_data.json','r',encoding='utf-8') as f: DATA=json.load(f)
DATA_JS=json.dumps(DATA,ensure_ascii=False)

html='''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Research Portfolio — Nak Cho Choi</title>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
<style>
:root{--bg:#0a0a1a;--bg2:#12122a;--card:rgba(255,255,255,0.03);--border:rgba(255,255,255,0.06);--text:#c8c8d4;--text2:#8888a0;--blue:#5b9cf5;--red:#f56565;--green:#68d391;--orange:#f6ad55;--purple:#b794f4}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI','Inter','Noto Sans KR',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.wrap{max-width:1440px;margin:0 auto;padding:20px}
.hdr{text-align:center;padding:32px 20px 12px}
.hdr h1{font-size:2.2em;font-weight:900;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hdr p{color:var(--text2);font-size:0.95em;margin-top:6px}
.cards{display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap}
.card{flex:1;min-width:120px;background:var(--card);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:14px;padding:18px 14px;text-align:center}
.card .val{font-size:1.8em;font-weight:800}.card .lbl{color:var(--text2);font-size:0.7em;text-transform:uppercase;letter-spacing:1px;margin-top:4px}
.card.c0{border-top:3px solid var(--orange)}.card.c1{border-top:3px solid var(--blue)}.card.c2{border-top:3px solid var(--red)}.card.c3{border-top:3px solid var(--green)}.card.c4{border-top:3px solid var(--purple)}
.tabs{display:flex;gap:2px;margin-bottom:0;flex-wrap:wrap}
.tb{padding:10px 20px;background:rgba(255,255,255,0.03);border:1px solid transparent;border-radius:12px 12px 0 0;cursor:pointer;font-size:0.84em;font-weight:500;color:var(--text2);transition:all .2s}
.tb:hover{color:var(--text)}.tb.on{background:var(--card);border-color:var(--border);border-bottom-color:transparent;color:#fff}
.tb .badge{background:rgba(255,255,255,0.08);padding:1px 8px;border-radius:10px;font-size:0.75em;margin-left:6px}
.main{background:var(--card);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:0 14px 14px 14px;padding:24px;min-height:300px}
.panel{display:none}.panel.on{display:block}
.chart-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:16px}
.chart-panel{min-height:360px;border-radius:10px}.chart-full{grid-column:1/-1;min-height:380px}
.inp{width:100%;padding:8px 14px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:0.84em;outline:none;margin-bottom:12px}
.inp:focus{border-color:var(--blue)}
.tbl-info{color:var(--text2);font-size:0.78em;margin-bottom:8px}
.tbl-wrap{max-height:500px;overflow-y:auto;border-radius:8px;border:1px solid var(--border)}
.tbl-wrap table{width:100%;border-collapse:collapse;font-size:0.8em}
.tbl-wrap thead{position:sticky;top:0;z-index:1}
.tbl-wrap th{background:#16163a;padding:9px 7px;text-align:left;font-weight:600;color:var(--text2);font-size:0.76em;text-transform:uppercase;border-bottom:1px solid var(--border)}
.tbl-wrap td{padding:7px;border-bottom:1px solid rgba(255,255,255,0.03);max-width:380px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tbl-wrap tr:hover td{background:rgba(255,255,255,0.02)}
.tag{display:inline-block;padding:2px 8px;border-radius:5px;font-size:0.73em;font-weight:600}
.tag.lead{background:rgba(245,101,101,0.15);color:var(--red)}
.tag.co{background:rgba(255,255,255,0.05);color:var(--text2)}
.tag.reg{background:rgba(104,211,145,0.15);color:var(--green)}
.tag.pub{background:rgba(91,156,245,0.15);color:var(--blue)}
.timeline{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:18px}
.phase{background:rgba(255,255,255,0.02);border-radius:12px;padding:16px;border-left:4px solid var(--blue)}
.phase.p1{border-color:var(--red)}.phase.p2{border-color:var(--blue)}.phase.p3{border-color:var(--green)}.phase.p4{border-color:var(--orange)}
.phase h4{color:#ddd;font-size:0.88em;margin-bottom:6px}
.phase p{color:var(--text2);font-size:0.8em;line-height:1.5}
.lang-bar{text-align:right;margin-bottom:8px}
.lbtn{padding:5px 14px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:8px;color:var(--text2);cursor:pointer;font-size:0.78em;margin-left:4px}
.lbtn.on{background:rgba(91,156,245,0.15);border-color:var(--blue);color:var(--blue)}
.err{color:var(--red);text-align:center;padding:40px}
@media(max-width:768px){.chart-grid{grid-template-columns:1fr}.cards{flex-direction:column}}
</style>
</head>
<body>
<div class="wrap">
<div class="lang-bar"><button class="lbtn on" onclick="setLang('en')">English</button><button class="lbtn" onclick="setLang('ko')">한국어</button></div>
<div class="hdr"><h1 id="mainTitle">Research Portfolio Analysis</h1><p>Integrated Patent & Paper Analysis — Google Scholar + KIPRIS</p></div>
<div class="cards" id="cards"></div>
<div class="tabs" id="tabs"></div>
<div class="main" id="mainContent"></div>
</div>
<script>
// PORTFOLIO DATA
var D = __DATA__;
var LANG = 'en';

function T(key) {
  var map = {
    'title': {en:'Research Portfolio Analysis', ko:'연구 포트폴리오 분석'},
    'total': {en:'Total IP', ko:'총 IP 자산'},
    'kr': {en:'KR Patents', ko:'한국 특허'},
    'us': {en:'US Patents', ko:'미국 특허'},
    'papers': {en:'Papers', ko:'논문'},
    'cites': {en:'Citations', ko:'인용'},
    'overview': {en:'Overview', ko:'개요'},
    'charts': {en:'Charts', ko:'차트'},
    'krTab': {en:'KR Patents', ko:'한국 특허'},
    'usTab': {en:'US Patents', ko:'미국 특허'},
    'papersTab': {en:'Papers', ko:'논문'},
    'searchKR': {en:'Search (title, IPC, app#)...', ko:'검색 (제목, IPC, 출원번호)...'},
    'searchUS': {en:'Search (title, author)...', ko:'검색 (제목, 저자)...'},
    'searchPP': {en:'Search (title, author, venue)...', ko:'검색 (제목, 저자, 저널)...'},
    'date': {en:'Date', ko:'출원일'},
    'status': {en:'St', ko:'상태'},
    'tech': {en:'Tech', ko:'기술'},
    'titleCol': {en:'Title', ko:'발명의 명칭'},
    'appNum': {en:'App#', ko:'출원번호'},
    'yr': {en:'Yr', ko:'연도'},
    'role': {en:'Role', ko:'역할'},
    'cite': {en:'Cite', ko:'인용'},
    'venue': {en:'Venue', ko:'저널'},
    'lead': {en:'Lead', ko:'주발명'},
    'co': {en:'Co', ko:'공동'},
    'searchPlaceholder': {en:'Enter name...', ko:'이름 입력...'},
  };
  return (map[key]||{})[LANG] || key;
}

function setLang(l) {
  LANG = l;
  document.querySelectorAll('.lbtn').forEach(function(b,i){ b.className = 'lbtn' + ((i===0&&l==='en')||(i===1&&l==='ko')?' on':''); });
  document.getElementById('mainTitle').textContent = T('title');
  renderCards();
  renderOverview();
}

function renderCards() {
  var s = D.profile.stats;
  document.getElementById('cards').innerHTML =
    '<div class="card c0"><div class="val">'+s.total+'</div><div class="lbl">'+T('total')+'</div></div>'+
    '<div class="card c1"><div class="val">'+s.kr_patents+'</div><div class="lbl">'+T('kr')+'</div></div>'+
    '<div class="card c2"><div class="val">'+s.us_patents+'</div><div class="lbl">'+T('us')+'</div></div>'+
    '<div class="card c3"><div class="val">'+s.papers+'</div><div class="lbl">'+T('papers')+'</div></div>'+
    '<div class="card c4"><div class="val">'+s.h_index+'</div><div class="lbl">h-index</div></div>'+
    '<div class="card"><div class="val">'+s.total_cites.toLocaleString()+'</div><div class="lbl">'+T('cites')+'</div></div>';
}

var currentTab = 'overview';

function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tb').forEach(function(b){ b.className='tb'; });
  document.getElementById('tab_'+tab).className='tb on';
  document.querySelectorAll('.panel').forEach(function(p){ p.className='panel'; });
  document.getElementById('panel_'+tab).className='panel on';
  if (tab==='charts') renderCharts();
}

function renderOverview() {
  document.getElementById('mainContent').innerHTML =
    '<div id="panel_overview" class="panel on">'+
    '<div class="timeline">'+
    '<div class="phase p1"><h4>'+ (LANG==='ko'?'Phase 1: LCD 시대 (2001-2017)':'Phase 1: LCD Era (2001-2017)') +'</h4><p>'+ (LANG==='ko'?'TFT-LCD 기판, PVA/VA 배향, 컬러필터. 삼성전자 LCD 사업부.':'TFT-LCD substrates, PVA/VA alignment, color filters. Samsung LCD Division.') +'</p></div>'+
    '<div class="phase p2"><h4>'+ (LANG==='ko'?'Phase 2: OLED 전환 (2017-2022)':'Phase 2: OLED Transition (2017-2022)') +'</h4><p>'+ (LANG==='ko'?'Black PDL, UPC, Polarizer-free, Foldable. OLED Innovation 리드.':'Black PDL, UPC, Polarizer-free, Foldable. Led OLED Innovation.') +'</p></div>'+
    '<div class="phase p3"><h4>'+ (LANG==='ko'?'Phase 3: Micro LED + Automotive (2021-2026)':'Phase 3: Micro LED + Automotive (2021-2026)') +'</h4><p>'+ (LANG==='ko'?'Micro LED 전사·타일링, Automotive OLED Switchable Privacy.':'Micro LED transfer/tiling, Automotive OLED Switchable Privacy.') +'</p></div>'+
    '<div class="phase p4"><h4>'+ (LANG==='ko'?'Phase 4: TFT 신뢰성 (2026.5-현재)':'Phase 4: TFT Reliability (2026.5-Present)') +'</h4><p>'+ (LANG==='ko'?'개발품질그룹 TFT 소자 신뢰성. 풀사이클 엔지니어.':'Development Quality Group, TFT reliability. Full-cycle display engineer.') +'</p></div>'+
    '</div>'+
    '<div style="margin-top:20px"><h3 style="color:var(--text2);font-size:0.82em;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">'+ (LANG==='ko'?'연구 분야':'Research Fields') +'</h3>'+
    '<div style="display:flex;gap:6px;flex-wrap:wrap">'+ D.profile.fields.map(function(f){return '<span style="padding:5px 14px;background:rgba(91,156,245,0.1);border-radius:20px;font-size:0.8em;color:var(--blue)">'+f+'</span>'}).join('') +'</div></div></div>'+
    '<div id="panel_kr" class="panel"><input class="inp" id="krFilter" oninput="filterTable(\'kr\')" placeholder="'+T('searchKR')+'"><div class="tbl-info" id="krInfo"></div><div class="tbl-wrap" id="krTable"></div></div>'+
    '<div id="panel_us" class="panel"><input class="inp" id="usFilter" oninput="filterTable(\'us\')" placeholder="'+T('searchUS')+'"><div class="tbl-info" id="usInfo"></div><div class="tbl-wrap" id="usTable"></div></div>'+
    '<div id="panel_papers" class="panel"><input class="inp" id="ppFilter" oninput="filterTable(\'pp\')" placeholder="'+T('searchPP')+'"><div class="tbl-info" id="ppInfo"></div><div class="tbl-wrap" id="ppTable"></div></div>'+
    '<div id="panel_charts" class="panel"><div class="chart-grid"><div class="chart-panel" id="chart1"></div><div class="chart-panel" id="chart2"></div></div><div class="chart-grid"><div class="chart-panel" id="chart3"></div><div class="chart-panel" id="chart4"></div></div><div class="chart-grid"><div class="chart-panel chart-full" id="chart5"></div></div></div>';
}

function renderTabs() {
  document.getElementById('tabs').innerHTML =
    '<div class="tb on" id="tab_overview" onclick="switchTab(\'overview\')">'+T('overview')+'</div>'+
    '<div class="tb" id="tab_kr" onclick="switchTab(\'kr\')">'+T('krTab')+'<span class="badge">'+D.kr_patents.length+'</span></div>'+
    '<div class="tb" id="tab_us" onclick="switchTab(\'us\')">'+T('usTab')+'<span class="badge">'+D.us_patents.length+'</span></div>'+
    '<div class="tb" id="tab_papers" onclick="switchTab(\'papers\')">'+T('papersTab')+'<span class="badge">'+D.papers.length+'</span></div>'+
    '<div class="tb" id="tab_charts" onclick="switchTab(\'charts\')">'+T('charts')+'</div>';
}

function filterTable(type) {
  var f = document.getElementById((type==='pp'?'pp':type)+'Filter').value.toLowerCase();
  var data = type==='kr'?D.kr_patents:type==='us'?D.us_patents:D.papers;
  var filtered = data;
  if(f) {
    filtered = data.filter(function(p){
      if(type==='kr') return (p.title+p.ipc+p.app_number).toLowerCase().indexOf(f)!==-1;
      if(type==='us') return (p.title||'').toLowerCase().indexOf(f)!==-1 || (p.authors||'').toLowerCase().indexOf(f)!==-1;
      return (p.title||'').toLowerCase().indexOf(f)!==-1 || (p.venue||'').toLowerCase().indexOf(f)!==-1;
    });
  }
  document.getElementById((type==='pp'?'pp':type)+'Info').textContent = filtered.length + ' / ' + data.length;
  if(type==='kr') renderKRTable(filtered);
  else if(type==='us') renderUSTable(filtered);
  else renderPPTable(filtered);
}

function esc(s) { return (s||'').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function renderKRTable(data) {
  var h='<table><thead><tr><th>#</th><th>'+T('date')+'</th><th>'+T('status')+'</th><th>'+T('tech')+'</th><th>'+T('titleCol')+'</th><th>'+T('appNum')+'</th></tr></thead><tbody>';
  data.forEach(function(p,i){
    var st=p.status==='등록'?'reg':'pub';
    h+='<tr><td>'+(i+1)+'</td><td style="white-space:nowrap">'+esc(p.app_date)+'</td><td><span class="tag '+st+'">'+esc(p.status)+'</span></td><td><span class="tag">'+esc(p.tech)+'</span></td><td title="'+esc(p.title)+'">'+esc(p.title)+'</td><td style="font-family:monospace;font-size:0.78em">'+esc(p.app_number)+'</td></tr>';
  });
  h+='</tbody></table>';
  document.getElementById('krTable').innerHTML=h;
}

function renderUSTable(data) {
  var h='<table><thead><tr><th>#</th><th>'+T('yr')+'</th><th>'+T('role')+'</th><th>'+T('cite')+'</th><th>'+T('tech')+'</th><th>'+T('titleCol')+'</th></tr></thead><tbody>';
  data.forEach(function(p,i){
    var r=p.lead?'lead':'co', rl=p.lead?T('lead'):T('co');
    h+='<tr><td>'+(i+1)+'</td><td>'+p.year+'</td><td><span class="tag '+r+'">'+rl+'</span></td><td>'+(p.cites||0)+'</td><td><span class="tag">'+esc(p.tech)+'</span></td><td title="'+esc(p.title)+'">'+esc(p.title)+'</td></tr>';
  });
  h+='</tbody></table>';
  document.getElementById('usTable').innerHTML=h;
}

function renderPPTable(data) {
  var h='<table><thead><tr><th>#</th><th>'+T('yr')+'</th><th>'+T('cite')+'</th><th>'+T('tech')+'</th><th>'+T('titleCol')+'</th><th>'+T('venue')+'</th></tr></thead><tbody>';
  data.forEach(function(p,i){
    h+='<tr><td>'+(i+1)+'</td><td>'+p.year+'</td><td>'+(p.cites||0)+'</td><td><span class="tag">'+esc(p.tech)+'</span></td><td title="'+esc(p.title)+'">'+esc(p.title)+'</td><td style="color:var(--text2);font-size:0.78em">'+esc(p.venue)+'</td></tr>';
  });
  h+='</tbody></table>';
  document.getElementById('ppTable').innerHTML=h;
}

function renderCharts() {
  setTimeout(function(){
    var ch = D.charts || {};
    var isKo = LANG==='ko';
    var cfg = {paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{color:'#8888a0'},margin:{t:50,b:40,l:60,r:30}};

    // Chart 1: Pie
    var techs=Object.entries(ch.kr_tech||{}).filter(function(e){return e[1]>0}).sort(function(a,b){return b[1]-a[1]});
    Plotly.newPlot('chart1',[{type:'pie',labels:techs.map(function(t){return t[0]}),values:techs.map(function(t){return t[1]}),marker:{colors:techs.map(function(t){return t[0]==='LCD'?'#f56565':t[0]==='OLED'?'#5b9cf5':t[0]==='Micro LED'?'#68d391':'#8888a0'})},textinfo:'label+value+percent',hole:0.4}],Object.assign({},cfg,{title:isKo?'한국 특허 기술 분류':'KR Patent Technology'}));

    // Chart 2: Stacked Bar
    var years=Object.keys(Object.assign({},ch.kr_yearly||{},ch.us_yearly||{},ch.paper_yearly||{})).map(Number).filter(function(y){return y>=2000&&y<=2026}).sort(function(a,b){return a-b});
    var ykr=years.map(function(y){return (ch.kr_yearly||{})[y]||0}), yus=years.map(function(y){return (ch.us_yearly||{})[y]||0}), ypp=years.map(function(y){return (ch.paper_yearly||{})[y]||0});
    Plotly.newPlot('chart2',[{x:years,y:ykr,type:'bar',name:isKo?'한국 특허':'KR Patents',marker:{color:'#5b9cf5'}},{x:years,y:yus,type:'bar',name:isKo?'미국 특허':'US Patents',marker:{color:'#f56565'}},{x:years,y:ypp,type:'bar',name:isKo?'논문':'Papers',marker:{color:'#68d391'}}],Object.assign({},cfg,{barmode:'stack',title:isKo?'연도별 포트폴리오':'Yearly Portfolio',legend:{font:{color:'#8888a0'}}}));

    // Chart 3: Heatmap
    var htechs=['LCD','OLED','Micro LED','TFT','Driving','Panel'];
    var hdata=htechs.map(function(tech){return years.map(function(y){return (D.kr_patents||[]).filter(function(p){return p.year===y&&p.tech===tech}).length})});
    Plotly.newPlot('chart3',[{z:hdata,x:years,y:htechs,type:'heatmap',colorscale:'YlOrRd',text:hdata.map(function(r){return r.map(function(v){return v>0?String(v):''})}),texttemplate:'%{text}',textfont:{color:'#333',size:11}}],Object.assign({},cfg,{title:isKo?'한국 특허 기술 진화':'KR Patent Tech Evolution',margin:{t:50,b:40,l:100,r:20}}));

    // Chart 4: US Tech
    var ust=Object.entries(ch.us_tech||{}).filter(function(e){return e[1]>0}).sort(function(a,b){return b[1]-a[1]});
    if(ust.length) Plotly.newPlot('chart4',[{type:'bar',x:ust.map(function(t){return t[1]}),y:ust.map(function(t){return t[0]}),orientation:'h',marker:{color:ust.map(function(t){return t[0]==='LCD'?'#f56565':t[0]==='OLED'?'#5b9cf5':t[0]==='Micro LED'?'#68d391':'#8888a0'})},text:ust.map(function(t){return t[1]}),textposition:'outside'}],Object.assign({},cfg,{title:isKo?'미국 특허 기술 분류':'US Patent Technology',margin:{t:50,b:30,l:120,r:40}}));

    // Chart 5: Total Output
    Plotly.newPlot('chart5',[{x:years,y:years.map(function(y,i){return ykr[i]+yus[i]+ypp[i]}),type:'scatter',mode:'lines+markers',line:{color:'#b794f4',width:3},marker:{size:8,color:'#b794f4'},fill:'tozeroy',name:isKo?'전체':'Total'}],Object.assign({},cfg,{title:isKo?'전체 발행 추이':'Total Output Trend'}));
  },200);
}

// INIT
try {
  renderCards();
  renderTabs();
  renderOverview();
  filterTable('kr');
  filterTable('us');
  filterTable('pp');
} catch(e) {
  document.getElementById('mainContent').innerHTML = '<div class="err"><h2>Error</h2><p>'+e.message+'</p></div>';
}
</script>
</body>
</html>'''

html=html.replace('__DATA__',DATA_JS)
out='frontend/index.html'
with open(out,'w',encoding='utf-8') as f: f.write(html)
import base64
with open(out,'rb') as f: b64=base64.b64encode(f.read()).decode()
print(f'OK: {out} ({len(html):,} bytes)')
