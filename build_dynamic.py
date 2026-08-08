# -*- coding: utf-8 -*-
"""Dynamic search page: input name → API → render charts"""
import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')

# Load default data for initial display
with open('portfolio_data.json','r',encoding='utf-8') as f: D=json.load(f)

html='''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Research Portfolio Search</title>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
:root{--bg:#0a0a1a;--card:rgba(255,255,255,0.035);--bd:rgba(255,255,255,0.06);--tx:#c8c8d4;--t2:#8888a0;--bl:#5b9cf5;--rd:#f56565;--gn:#68d391;--or:#f6ad55;--pr:#b794f4}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter','Noto Sans KR','Segoe UI',sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;color:var(--tx)}
.wrap{max-width:1500px;margin:0 auto;padding:20px}
.hdr{background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);padding:24px 40px 18px;border-radius:16px;margin-bottom:22px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.15)}
.hdr h1{margin:0 0 14px;font-size:1.8em;font-weight:800;color:#fff}
.search-wrap{display:flex;gap:10px;max-width:600px;margin:0 auto}
.search-wrap input{flex:1;padding:12px 18px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:12px;color:#fff;font-size:1em;outline:none;font-family:inherit}
.search-wrap input::placeholder{color:rgba(255,255,255,0.4)}
.search-wrap input:focus{border-color:var(--bl);box-shadow:0 0 0 3px rgba(91,156,245,0.15)}
.search-wrap button{padding:12px 28px;background:var(--gr,linear-gradient(135deg,#667eea,#764ba2));color:#fff;border:none;border-radius:12px;font-size:0.95em;font-weight:600;cursor:pointer;white-space:nowrap}
.search-wrap button:hover{opacity:0.9}
.search-wrap button:disabled{opacity:0.5;cursor:not-allowed}
.hints{display:flex;gap:8px;margin-top:10px;justify-content:center;flex-wrap:wrap}
.hints span{padding:4px 14px;background:rgba(255,255,255,0.06);border-radius:20px;cursor:pointer;font-size:0.8em;color:var(--t2);transition:all .2s}
.hints span:hover{background:rgba(91,156,245,0.15);color:var(--bl)}
.status{text-align:center;padding:60px 20px}
.spinner{width:40px;height:40px;border:3px solid var(--bd);border-top-color:var(--bl);border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 16px}
@keyframes spin{to{transform:rotate(360deg)}}
.err{background:rgba(245,101,101,0.08);border:1px solid rgba(245,101,101,0.2);border-radius:14px;padding:20px;text-align:center;max-width:500px;margin:40px auto;color:var(--rd)}
.cards{display:flex;gap:14px;margin-bottom:22px;flex-wrap:wrap}
.card{flex:1;min-width:130px;background:#fff;border-radius:12px;padding:20px 16px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.08);border-top:4px solid var(--bl)}
.card .val{font-size:1.7em;font-weight:700;color:#2C3E50}
.card .lbl{color:var(--t2);font-size:0.72em;text-transform:uppercase;letter-spacing:1px;margin-top:4px}
.card.tl{border-top-color:var(--or)}.card.kr{border-top-color:var(--bl)}.card.us{border-top-color:var(--rd)}.card.pp{border-top-color:var(--gn)}.card.hl{border-top-color:var(--rd)}
.insight{background:#fff;border-radius:12px;padding:20px 24px;margin-bottom:22px;box-shadow:0 2px 12px rgba(0,0,0,0.06);border-left:4px solid var(--or)}
.insight h3{color:#E67E22;font-size:0.95em;margin:0 0 8px}
.insight ul{margin:0;padding-left:20px;color:#7D6608;font-size:0.85em;line-height:1.7}
.sec{background:#fff;border-radius:12px;padding:20px 24px;margin-bottom:22px;box-shadow:0 2px 12px rgba(0,0,0,0.06)}
.sec h2{color:#2C3E50;font-size:1.1em;margin:0 0 14px;border-bottom:2px solid var(--bl);padding-bottom:8px}
.chart-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.chart-box{background:#fff;border-radius:8px;padding:12px;min-height:380px;border:1px solid #eee}
.chart-wide{grid-column:1/-1;min-height:400px}
details{margin-bottom:8px}
summary{cursor:pointer;padding:10px 14px;background:#F8F9FA;border-radius:8px;font-size:0.88em;font-weight:500;color:#2C3E50;display:flex;justify-content:space-between}
summary:hover{background:#E8F0FE}
summary span.cnt{color:var(--t2);font-size:0.85em}
.tbl-wrap{max-height:480px;overflow-y:auto;border-radius:6px;border:1px solid #eee;margin-top:8px}
.tbl-wrap table{width:100%;border-collapse:collapse;font-size:0.78em}
.tbl-wrap thead{position:sticky;top:0;z-index:1}
.tbl-wrap th{background:#2C3E50;color:#fff;padding:8px 6px;text-align:left;font-weight:600;font-size:0.76em;text-transform:uppercase}
.tbl-wrap td{padding:6px;border-bottom:1px solid #eee;color:#444;max-width:360px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tbl-wrap tr:nth-child(even) td{background:#F8F9FA}
.tbl-wrap tr:hover td{background:#E8F0FE}
.tag{display:inline-block;padding:2px 8px;border-radius:5px;font-size:0.72em;font-weight:600}
.tag.lead{background:rgba(245,101,101,0.15);color:#d32f2f}
.tag.co{background:#eee;color:#999}
.tag.reg{background:rgba(104,211,145,0.15);color:#2E7D32}
.tag.pub{background:rgba(91,156,245,0.15);color:#1565C0}
.inp{width:100%;padding:8px 14px;background:#f5f5f5;border:1px solid #ddd;border-radius:8px;color:#333;font-size:0.84em;outline:none;margin-bottom:10px}
.inp:focus{border-color:var(--bl);background:#fff}
.tbl-info{color:#999;font-size:0.8em;margin-bottom:6px}
@media(max-width:768px){.chart-grid{grid-template-columns:1fr}.cards{flex-direction:column}}
</style>
</head>
<body>
<div class="wrap">
<div class="hdr">
<h1>📊 Research Portfolio Search</h1>
<div class="search-wrap">
<input id="searchInput" placeholder="Enter name (e.g., Nak Cho Choi, 최낙초)..." onkeydown="if(event.key==='Enter')doSearch()">
<button id="searchBtn" onclick="doSearch()">Search</button>
</div>
<div class="hints">
<span onclick="quickSearch('Nak Cho Choi')">Nak Cho Choi</span>
<span onclick="quickSearch('최낙초')">최낙초</span>
</div>
</div>

<div id="statusArea"><div class="status"><p style="color:var(--t2)">Enter a researcher name above to generate portfolio report.</p></div></div>
<div id="resultArea" style="display:none"></div>
</div>

<script>
function esc(s){return(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}

function quickSearch(name){
  document.getElementById('searchInput').value=name;
  doSearch();
}

async function doSearch(){
  var name=document.getElementById('searchInput').value.trim();
  if(!name) return;
  
  var sa=document.getElementById('statusArea');
  var ra=document.getElementById('resultArea');
  var btn=document.getElementById('searchBtn');
  
  btn.disabled=true; btn.textContent='Searching...';
  sa.style.display='block'; ra.style.display='none';
  sa.innerHTML='<div class="status"><div class="spinner"></div><p style="color:var(--t2)">Fetching data for <b>'+esc(name)+'</b> from Google Scholar + KIPRIS...</p></div>';
  
  try{
    var resp=await fetch('/api/portfolio/'+encodeURIComponent(name));
    if(!resp.ok) throw new Error(await resp.text());
    var data=await resp.json();
    if(!data.success) throw new Error(data.error||'No data found');
    render(data);
  }catch(e){
    sa.innerHTML='<div class="err"><p><b>Error:</b> '+esc(e.message)+'</p><p style="margin-top:8px;font-size:0.85em">Try "Nak Cho Choi" or "최낙초"</p></div>';
  }finally{
    btn.disabled=false; btn.textContent='Search';
  }
}

function render(data){
  document.getElementById('statusArea').style.display='none';
  var ra=document.getElementById('resultArea');
  ra.style.display='block';
  
  var S=data.profile.stats, P=data.profile, KR=data.kr_patents||[], US=data.us_patents||[], PP=data.papers||[], C=data.charts||{};
  
  // Cards
  var cardsHTML='<div class="cards">'+
    '<div class="card tl"><div class="val">'+S.total+'</div><div class="lbl">Total IP</div></div>'+
    '<div class="card kr"><div class="val">'+S.kr_patents+'</div><div class="lbl">KR Patents</div></div>'+
    '<div class="card us"><div class="val">'+S.us_patents+'</div><div class="lbl">US Patents</div></div>'+
    '<div class="card pp"><div class="val">'+S.papers+'</div><div class="lbl">Papers</div></div>'+
    '<div class="card hl"><div class="val">'+S.h_index+'</div><div class="lbl">h-index</div></div>'+
    '<div class="card"><div class="val">'+(S.total_cites||0).toLocaleString()+'</div><div class="lbl">Citations</div></div>'+
    '</div>';
  
  // Insight
  var krTechs=Object.entries(C.kr_tech||{}).sort(function(a,b){return b[1]-a[1]}).slice(0,3).map(function(t){return t[0]+' '+t[1]}).join(' | ');
  var insightHTML='<div class="insight"><h3>Key Insights</h3><ul>'+
    '<li>Total <b>'+S.total+'</b> IP assets: '+S.kr_patents+' KR + '+S.us_patents+' US + '+S.papers+' papers</li>'+
    '<li>KR technology: '+krTechs+'</li>'+
    '<li>h-index <b>'+S.h_index+'</b>, i10-index '+S.i10_index+', total <b>'+(S.total_cites||0).toLocaleString()+'</b> citations</li>'+
    '<li>Fields: '+(P.fields||[]).map(function(f){return '<span style="background:#EBF5FB;padding:2px 10px;border-radius:12px;font-size:0.9em">'+f+'</span>'}).join(' ')+'</li>'+
    '</ul></div>';
  
  // Charts section
  var chartsHTML='<div class="sec"><h2>Charts & Analytics</h2>'+
    '<div class="chart-grid">'+
    '<div class="chart-box" id="c1"></div><div class="chart-box" id="c2"></div>'+
    '<div class="chart-box chart-wide" id="c3"></div>'+
    '<div class="chart-box" id="c4"></div><div class="chart-box" id="c5"></div>'+
    '<div class="chart-box chart-wide" id="c6"></div>'+
    '</div></div>';
  
  // Tables
  var tablesHTML='<div class="sec"><h2>Patent & Paper Lists</h2>';
  tablesHTML+=buildTable('kr','KR Patents (KIPRIS)',KR,['App Date','St','Tech','Title','App Number'],function(p,i){var sc=p.status==='등록'?'reg':'pub';return'<td>'+esc(p.app_date||'')+'</td><td><span class="tag '+sc+'">'+esc(p.status||'')+'</span></td><td><span class="tag">'+esc(p.tech||'')+'</span></td><td title="'+esc(p.title||'')+'">'+esc(p.title||'').substring(0,70)+'</td><td style="font-family:monospace;font-size:0.75em">'+esc(p.app_number||'')+'</td>';});
  tablesHTML+=buildTable('us','US Patents (Google Scholar)',US,['Year','Role','Cite','Tech','Title'],function(p,i){var rc=p.lead?'lead':'co',rt=p.lead?'Lead':'Co';return'<td>'+p.year+'</td><td><span class="tag '+rc+'">'+rt+'</span></td><td>'+(p.cites||0)+'</td><td><span class="tag">'+esc(p.tech||'')+'</span></td><td title="'+esc(p.title||'')+'">'+esc(p.title||'').substring(0,70)+'</td>';});
  tablesHTML+=buildTable('pp','Papers (Google Scholar)',PP,['Year','Cite','Tech','Title','Venue'],function(p,i){return'<td>'+p.year+'</td><td>'+(p.cites||0)+'</td><td><span class="tag">'+esc(p.tech||'')+'</span></td><td title="'+esc(p.title||'')+'">'+esc(p.title||'').substring(0,70)+'</td><td style="color:#999;font-size:0.8em">'+esc(p.venue||'')+'</td>';});
  tablesHTML+='</div>';
  
  ra.innerHTML=cardsHTML+insightHTML+chartsHTML+tablesHTML;
  
  // Initialize table filters
  ['kr','us','pp'].forEach(function(t){
    document.getElementById(t+'Filter').oninput=function(){filterTable(t,{kr:KR,us:US,pp:PP}[t]);};
    filterTable(t,{kr:KR,us:US,pp:PP}[t]);
  });
  
  // Render charts
  setTimeout(function(){renderCharts(C,KR,US,PP);},300);
}

function buildTable(type,title,data,headers,rowFn){
  var h='<details><summary><span>'+title+'</span><span class="cnt">'+data.length+' items</span></summary>';
  h+='<input class="inp" id="'+type+'Filter" placeholder="Search...">';
  h+='<div class="tbl-info" id="'+type+'Info">'+data.length+' items</div>';
  h+='<div class="tbl-wrap"><table><thead><tr><th>#</th>'+headers.map(function(h){return'<th>'+h+'</th>'}).join('')+'</tr></thead><tbody id="'+type+'Tbody"></tbody></table></div></details>';
  return h;
}

function filterTable(type,data){
  var f=document.getElementById(type+'Filter').value.toLowerCase();
  var fd=f?data.filter(function(p){
    if(type==='kr')return(p.title+p.ipc+p.app_number).toLowerCase().indexOf(f)!==-1;
    if(type==='us')return(p.title||'').toLowerCase().indexOf(f)!==-1||(p.authors||'').toLowerCase().indexOf(f)!==-1;
    return(p.title||'').toLowerCase().indexOf(f)!==-1||(p.venue||'').toLowerCase().indexOf(f)!==-1;
  }):data;
  document.getElementById(type+'Info').textContent=fd.length+' / '+data.length+' items';
  var rows='';
  fd.forEach(function(p,i){
    rows+='<tr><td>'+(i+1)+'</td>';
    if(type==='kr'){var sc=p.status==='등록'?'reg':'pub';
      rows+='<td>'+esc(p.app_date||'')+'</td><td><span class="tag '+sc+'">'+esc(p.status||'')+'</span></td><td><span class="tag">'+esc(p.tech||'')+'</span></td><td title="'+esc(p.title||'')+'">'+esc(p.title||'').substring(0,70)+'</td><td style="font-family:monospace;font-size:0.75em">'+esc(p.app_number||'')+'</td>';
    }else if(type==='us'){var rc=p.lead?'lead':'co',rt=p.lead?'Lead':'Co';
      rows+='<td>'+p.year+'</td><td><span class="tag '+rc+'">'+rt+'</span></td><td>'+(p.cites||0)+'</td><td><span class="tag">'+esc(p.tech||'')+'</span></td><td title="'+esc(p.title||'')+'">'+esc(p.title||'').substring(0,70)+'</td>';
    }else{
      rows+='<td>'+p.year+'</td><td>'+(p.cites||0)+'</td><td><span class="tag">'+esc(p.tech||'')+'</span></td><td title="'+esc(p.title||'')+'">'+esc(p.title||'').substring(0,70)+'</td><td style="color:#999;font-size:0.8em">'+esc(p.venue||'')+'</td>';
    }
    rows+='</tr>';
  });
  document.getElementById(type+'Tbody').innerHTML=rows;
}

function renderCharts(C,KR,US,PP){
  var lo={paper_bgcolor:'#fff',plot_bgcolor:'#fff',font:{color:'#555',size:11},margin:{t:50,b:40,l:50,r:20}};
  var bg='#fff';

  // C1: KR Tech Pie
  var techs=Object.entries(C.kr_tech||{}).filter(function(e){return e[1]>0}).sort(function(a,b){return b[1]-a[1]});
  Plotly.newPlot('c1',[{type:'pie',labels:techs.map(function(t){return t[0]}),values:techs.map(function(t){return t[1]}),marker:{colors:techs.map(function(t){return t[0]==='LCD'?'#E74C3C':t[0]==='OLED'?'#3498DB':t[0]==='Micro LED'?'#2ECC71':'#95A5A6'})},textinfo:'label+percent',hole:0.35}],Object.assign({},lo,{title:'KR Patent Tech (IPC)'}));

  // C2: Yearly Stacked Bar
  var years=Object.keys(Object.assign({},C.kr_yearly||{},C.us_yearly||{},C.paper_yearly||{})).map(Number).filter(function(y){return y>=2000&&y<=2026}).sort(function(a,b){return a-b});
  var ykr=years.map(function(y){return(C.kr_yearly||{})[y]||0}),yus=years.map(function(y){return(C.us_yearly||{})[y]||0}),ypp=years.map(function(y){return(C.paper_yearly||{})[y]||0});
  Plotly.newPlot('c2',[{x:years,y:ykr,type:'bar',name:'KR',marker:{color:'#3498DB'}},{x:years,y:yus,type:'bar',name:'US',marker:{color:'#E74C3C'}},{x:years,y:ypp,type:'bar',name:'Paper',marker:{color:'#2ECC71'}}],Object.assign({},lo,{barmode:'stack',title:'Yearly Output',legend:{x:0.01,y:0.98},xaxis:{title:'Year'},yaxis:{title:'Count'}}));

  // C3: Heatmap
  var htechs=['LCD','OLED','Micro LED','TFT','Driving','Panel'];
  var hdata=htechs.map(function(tech){return years.map(function(y){return KR.filter(function(p){return p.year===y&&p.tech===tech}).length})});
  Plotly.newPlot('c3',[{z:hdata,x:years,y:htechs,type:'heatmap',colorscale:'YlOrRd',showscale:true,text:hdata.map(function(r){return r.map(function(v){return v>0?String(v):''})}),texttemplate:'%{text}',textfont:{size:10},colorbar:{title:'Count'}}],Object.assign({},lo,{title:'KR Patent Tech Evolution',margin:{t:50,b:40,l:100,r:60},xaxis:{title:'Year'}}));

  // C4: US Tech
  var ust=Object.entries(C.us_tech||{}).filter(function(e){return e[1]>0}).sort(function(a,b){return a[1]-b[1]});
  Plotly.newPlot('c4',[{type:'bar',x:ust.map(function(t){return t[1]}),y:ust.map(function(t){return t[0]}),orientation:'h',marker:{color:ust.map(function(t){return t[0]==='LCD'?'#E74C3C':t[0]==='OLED'?'#3498DB':t[0]==='Micro LED'?'#2ECC71':'#95A5A6'})},text:ust.map(function(t){return t[1]}),textposition:'outside'}],Object.assign({},lo,{title:'US Patent Tech',margin:{t:50,b:30,l:120,r:40}}));

  // C5: Top 10
  var top10=US.slice().sort(function(a,b){return(b.cites||0)-(a.cites||0)}).slice(0,10);
  Plotly.newPlot('c5',[{type:'bar',x:top10.map(function(t){return t.cites||0}).reverse(),y:top10.map(function(t){return(t.title||'').substring(0,45)}).reverse(),orientation:'h',marker:{color:'#E74C3C'},text:top10.map(function(t){return t.cites||0}).reverse(),textposition:'outside'}],Object.assign({},lo,{title:'Top 10 Cited (US)',margin:{t:50,b:30,l:80,r:50},xaxis:{title:'Citations'}}));

  // C6: Total Line
  Plotly.newPlot('c6',[{x:years,y:years.map(function(y,i){return ykr[i]+yus[i]+ypp[i]}),type:'scatter',mode:'lines+markers',line:{color:'#8E44AD',width:3},marker:{size:7,color:'#8E44AD'},fill:'tozeroy',name:'Total'}],Object.assign({},lo,{title:'Total Output (KR+US+Papers)',xaxis:{title:'Year'},yaxis:{title:'Count'}}));
}

// Auto-load default on page open
window.addEventListener('DOMContentLoaded',function(){
  document.getElementById('searchInput').value='Nak Cho Choi';
  setTimeout(doSearch,200);
});
</script>
</body>
</html>'''

out='frontend/index.html'
with open(out,'w',encoding='utf-8') as f: f.write(html)
import base64
with open(out,'rb') as f: b64=base64.b64encode(f.read()).decode()
print(f'OK: {out} ({len(html):,} bytes)')
print('Dynamic search page: input name → API → render')
