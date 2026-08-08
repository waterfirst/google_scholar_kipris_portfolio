# -*- coding: utf-8 -*-
"""Build Vue.js Portfolio Web App — single HTML file with embedded JSON"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json

# Load portfolio data
with open('portfolio_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

json_str = json.dumps(data, ensure_ascii=False)

html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nak Cho Choi — Research Portfolio</title>
<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter','Noto Sans KR',sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;color:#e0e0e0}}
#app{{max-width:1500px;margin:0 auto;padding:16px}}
.header{{text-align:center;padding:32px 20px 24px}}
.header h1{{font-size:2em;font-weight:800;background:linear-gradient(90deg,#64b5f6,#ce93d8,#81c784);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.header p{{color:#aaa;margin-top:8px;font-size:0.95em}}
.cards{{display:flex;gap:14px;margin-bottom:24px;flex-wrap:wrap}}
.card{{flex:1;min-width:130px;background:rgba(255,255,255,0.06);backdrop-filter:blur(10px);border-radius:14px;padding:18px 14px;text-align:center;border:1px solid rgba(255,255,255,0.1);transition:transform .2s}}
.card:hover{{transform:translateY(-3px)}}
.card .v{{font-size:1.7em;font-weight:800}}
.card .l{{color:#999;font-size:0.75em;text-transform:uppercase;letter-spacing:1px;margin-top:4px}}
.card.kr{{border-top:3px solid #42a5f5}} .card.us{{border-top:3px solid #ef5350}} .card.pp{{border-top:3px solid #66bb6a}} .card.tl{{border-top:3px solid #ffa726}}
.tabs{{display:flex;gap:4px;margin-bottom:20px;flex-wrap:wrap}}
.tab{{padding:10px 22px;background:rgba(255,255,255,0.05);border-radius:10px 10px 0 0;cursor:pointer;font-size:0.88em;font-weight:500;color:#999;border:1px solid transparent;transition:all .2s}}
.tab:hover{{color:#fff;background:rgba(255,255,255,0.1)}}
.tab.active{{color:#fff;background:rgba(255,255,255,0.12);border-color:rgba(255,255,255,0.15);border-bottom-color:transparent}}
.tab .badge{{background:rgba(255,255,255,0.15);padding:2px 8px;border-radius:10px;font-size:0.75em;margin-left:6px}}
.content{{background:rgba(255,255,255,0.04);backdrop-filter:blur(12px);border-radius:0 14px 14px 14px;padding:24px;border:1px solid rgba(255,255,255,0.08);min-height:400px}}
.chart-row{{display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap}}
.chart-box{{flex:1;min-width:400px;min-height:350px}}
.search-box{{margin-bottom:16px}}
.search-box input{{width:100%;padding:10px 16px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);border-radius:10px;color:#e0e0e0;font-size:0.9em;outline:none}}
.search-box input:focus{{border-color:#64b5f6}}
table{{width:100%;border-collapse:collapse;font-size:0.84em}}
th{{position:sticky;top:0;background:rgba(30,30,60,0.95);padding:10px 8px;text-align:left;font-weight:600;color:#bbb;border-bottom:2px solid rgba(255,255,255,0.1)}}
td{{padding:8px;border-bottom:1px solid rgba(255,255,255,0.05);color:#ccc}}
tr:hover td{{background:rgba(255,255,255,0.04)}}
.tag{{display:inline-block;padding:2px 8px;border-radius:6px;font-size:0.78em;font-weight:500}}
.tag.lead{{background:rgba(239,83,80,0.25);color:#ef5350}}
.tag.co{{background:rgba(255,255,255,0.1);color:#999}}
.tag.reg{{background:rgba(102,187,106,0.25);color:#81c784}}
.tag.pub{{background:rgba(66,165,245,0.25);color:#64b5f6}}
.tag.lcd{{background:rgba(239,83,80,0.25);color:#ef9a9a}}
.tag.oled{{background:rgba(66,165,245,0.25);color:#90caf9}}
.tag.mled{{background:rgba(102,187,106,0.25);color:#a5d6a7}}
.lang-toggle{{position:absolute;top:20px;right:30px;display:flex;gap:4px}}
.lang-btn{{padding:6px 14px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-radius:8px;color:#999;cursor:pointer;font-size:0.8em;transition:all .2s}}
.lang-btn.active{{background:rgba(100,181,246,0.2);border-color:#64b5f6;color:#64b5f6}}
.phase-row{{display:flex;gap:14px;margin-top:16px;flex-wrap:wrap}}
.phase{{flex:1;min-width:200px;background:rgba(255,255,255,0.04);border-radius:12px;padding:16px;border-left:3px solid}}
.phase.p1{{border-left-color:#ef5350}} .phase.p2{{border-left-color:#42a5f5}} .phase.p3{{border-left-color:#66bb6a}} .phase.p4{{border-left-color:#ffa726}}
.phase h4{{color:#ddd;font-size:0.9em;margin-bottom:6px}}
.phase p{{color:#999;font-size:0.8em;line-height:1.5}}
.table-wrap{{max-height:600px;overflow-y:auto;border-radius:8px}}
@media(max-width:768px){{.cards{{flex-direction:column}}.chart-box{{min-width:100%}}.tabs{{flex-wrap:wrap}}}}
</style>
</head>
<body>
<div id="app">
<div style="position:relative">
<div class="lang-toggle">
  <button class="lang-btn" :class="{{active:lang==='ko'}}" @click="lang='ko'">한국어</button>
  <button class="lang-btn" :class="{{active:lang==='en'}}" @click="lang='en'">English</button>
</div>
<div class="header">
  <h1>{{lang==='ko'?'연구 포트폴리오':'Research Portfolio'}}</h1>
  <p>{{lang==='ko'?pro.affiliation_ko:pro.affiliation}} · {{lang==='ko'?'25년+ 디스플레이 기술 연구':'25+ Years in Display Technology'}}</p>
</div>
<div class="cards">
  <div class="card tl"><div class="v">{{pro.stats.total}}</div><div class="l">{{lang==='ko'?'총 IP 자산':'Total IP'}}</div></div>
  <div class="card kr"><div class="v">{{pro.stats.kr_patents}}</div><div class="l">{{lang==='ko'?'한국 특허':'KR Patents'}}</div></div>
  <div class="card us"><div class="v">{{pro.stats.us_patents}}</div><div class="l">{{lang==='ko'?'미국 특허':'US Patents'}}</div></div>
  <div class="card pp"><div class="v">{{pro.stats.papers}}</div><div class="l">{{lang==='ko'?'논문':'Papers'}}</div></div>
  <div class="card"><div class="v">{{pro.stats.h_index}}</div><div class="l">h-index</div></div>
  <div class="card"><div class="v">{{pro.stats.total_cites.toLocaleString()}}</div><div class="l">{{lang==='ko'?'인용':'Citations'}}</div></div>
</div>
<div class="tabs">
  <div class="tab" :class="{{active:tab==='overview'}}" @click="tab='overview'">{{lang==='ko'?'개요':'Overview'}}</div>
  <div class="tab" :class="{{active:tab==='kr'}}" @click="tab='kr'">{{lang==='ko'?'한국 특허':'KR Patents'}}<span class="badge">{{pro.stats.kr_patents}}</span></div>
  <div class="tab" :class="{{active:tab==='us'}}" @click="tab='us'">{{lang==='ko'?'미국 특허':'US Patents'}}<span class="badge">{{pro.stats.us_patents}}</span></div>
  <div class="tab" :class="{{active:tab==='papers'}}" @click="tab='papers'">{{lang==='ko'?'논문':'Papers'}}<span class="badge">{{pro.stats.papers}}</span></div>
  <div class="tab" :class="{{active:tab==='charts'}}" @click="tab='charts';initCharts()">{{lang==='ko'?'차트':'Charts'}}</div>
</div>
<div class="content">
  <!-- Overview -->
  <div v-if="tab==='overview'">
    <div class="phase-row">
      <div class="phase p1"><h4>{{lang==='ko'?'📺 Phase 1: LCD 시대 (2001–2017)':'📺 Phase 1: LCD Era (2001–2017)'}}</h4><p>{{lang==='ko'?'TFT-LCD 기판, 액정 배향(PVA/VA), 컬러필터, curved LCD. 삼성전자 LCD 사업부에서 핵심 특허 다수 출원.':'TFT-LCD substrates, alignment, color filters, curved LCD. Core patents at Samsung LCD Division.'}}</p></div>
      <div class="phase p2"><h4>{{lang==='ko'?'💡 Phase 2: OLED 전환 (2017–2022)':'💡 Phase 2: OLED Transition (2017–2022)'}}</h4><p>{{lang==='ko'?'Black PDL(LTPO), UPC, Polarizer-free OLED, 폴더블 디스플레이. 삼성디스플레이 OLED Materials & Process Innovation 리드.':'Black PDL (LTPO), UPC, Polarizer-free OLED, Foldable displays. Led OLED Materials & Process Innovation.'}}</p></div>
      <div class="phase p3"><h4>{{lang==='ko'?'🔬 Phase 3: Micro LED + Automotive (2021–2026)':'🔬 Phase 3: Micro LED + Automotive (2021–2026)'}}</h4><p>{{lang==='ko'?'Micro LED 전사·타일링, Automotive OLED Switchable Privacy. 2025년 13건 특허로 피크.':'Micro LED transfer/tiling, Automotive OLED Switchable Privacy. Peak at 13 patents in 2025.'}}</p></div>
      <div class="phase p4"><h4>{{lang==='ko'?'🛡️ Phase 4: TFT 신뢰성 (2026.5–현재)':'🛡️ Phase 4: TFT Reliability (2026.5–Present)'}}</h4><p>{{lang==='ko'?'개발품질그룹, TFT 소자 신뢰성 담당. 25년+ 소자·공정 전문성 기반 품질 검증.':'Development Quality Group, TFT device reliability. Full-cycle display engineer.'}}</p></div>
    </div>
    <div style="margin-top:24px">
      <h3 style="color:#ccc;margin-bottom:12px">{{lang==='ko'?'🔬 연구 분야':'🔬 Research Fields'}}</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap">{{pro.fields.map(f=>`<span class="tag" style="background:rgba(100,181,246,0.15);color:#90caf9;padding:6px 14px;font-size:0.85em">${{f}}</span>`).join('')}}</div>
    </div>
  </div>
  <!-- KR Patents -->
  <div v-if="tab==='kr'">
    <div class="search-box"><input v-model="krSearch" :placeholder="lang==='ko'?'한국 특허 검색 (제목, IPC, 출원번호)...':'Search Korean patents (title, IPC, app#)...'"></div>
    <div class="table-wrap"><table><thead><tr><th>#</th><th>{{lang==='ko'?'출원일':'App Date'}}</th><th>{{lang==='ko'?'상태':'Status'}}</th><th>{{lang==='ko'?'기술':'Tech'}}</th><th>{{lang==='ko'?'발명의 명칭':'Title'}}</th><th>{{lang==='ko'?'출원번호':'App Number'}}</th></tr></thead>
    <tbody><tr v-for="(p,i) in filteredKR" :key="i"><td>{{i+1}}</td><td>{{p.app_date}}</td><td><span class="tag" :class="p.status==='등록'?'reg':'pub'">{{p.status}}</span></td><td><span class="tag" :class="p.tech==='LCD'?'lcd':p.tech==='OLED'?'oled':'mled'">{{p.tech}}</span></td><td style="max-width:400px">{{p.title}}</td><td style="font-family:monospace;font-size:0.8em">{{p.app_number}}</td></tr></tbody></table></div>
    <div style="margin-top:12px;color:#999;font-size:0.85em">{{lang==='ko'?'총 ':'Total '}}{{filteredKR.length}}{{lang==='ko'?'건':' items'}}</div>
  </div>
  <!-- US Patents -->
  <div v-if="tab==='us'">
    <div class="search-box"><input v-model="usSearch" :placeholder="lang==='ko'?'미국 특허 검색 (제목, 저자)...':'Search US patents (title, author)...'"></div>
    <div class="table-wrap"><table><thead><tr><th>#</th><th>{{lang==='ko'?'연도':'Year'}}</th><th>{{lang==='ko'?'역할':'Role'}}</th><th>{{lang==='ko'?'인용':'Cites'}}</th><th>{{lang==='ko'?'기술':'Tech'}}</th><th>{{lang==='ko'?'제목':'Title'}}</th></tr></thead>
    <tbody><tr v-for="(p,i) in filteredUS" :key="i"><td>{{i+1}}</td><td>{{p.year}}</td><td><span class="tag" :class="p.lead?'lead':'co'">{{p.lead?(lang==='ko'?'주발명자':'Lead'):(lang==='ko'?'공동':'Co')}}</span></td><td>{{p.cites||0}}</td><td><span class="tag" :class="p.tech==='LCD'?'lcd':p.tech==='OLED'?'oled':'mled'">{{p.tech}}</span></td><td style="max-width:400px">{{p.title}}</td></tr></tbody></table></div>
    <div style="margin-top:12px;color:#999;font-size:0.85em">{{lang==='ko'?'총 ':'Total '}}{{filteredUS.length}}{{lang==='ko'?'건':' items'}}</div>
  </div>
  <!-- Papers -->
  <div v-if="tab==='papers'">
    <div class="search-box"><input v-model="paperSearch" :placeholder="lang==='ko'?'논문 검색 (제목, 저자)...':'Search papers (title, author)...'"></div>
    <div class="table-wrap"><table><thead><tr><th>#</th><th>{{lang==='ko'?'연도':'Year'}}</th><th>{{lang==='ko'?'인용':'Cites'}}</th><th>{{lang==='ko'?'기술':'Tech'}}</th><th>{{lang==='ko'?'제목':'Title'}}</th><th>{{lang==='ko'?'저널':'Venue'}}</th></tr></thead>
    <tbody><tr v-for="(p,i) in filteredPapers" :key="i"><td>{{i+1}}</td><td>{{p.year}}</td><td>{{p.cites||0}}</td><td><span class="tag" :class="p.tech==='LCD'?'lcd':p.tech==='OLED'?'oled':'mled'">{{p.tech}}</span></td><td style="max-width:350px">{{p.title}}</td><td style="font-size:0.8em;color:#999">{{p.venue}}</td></tr></tbody></table></div>
    <div style="margin-top:12px;color:#999;font-size:0.85em">{{lang==='ko'?'총 ':'Total '}}{{filteredPapers.length}}{{lang==='ko'?'건':' items'}}</div>
  </div>
  <!-- Charts -->
  <div v-if="tab==='charts'">
    <div class="chart-row"><div class="chart-box" id="chart1"></div><div class="chart-box" id="chart2"></div></div>
    <div class="chart-row"><div class="chart-box" id="chart3"></div><div class="chart-box" id="chart4"></div></div>
    <div class="chart-row"><div class="chart-box" id="chart5" style="min-height:400px"></div></div>
  </div>
</div>
</div>
</div>
<script>
const PORTFOLIO_DATA = {json_str};
const {{createApp,ref,computed,nextTick,onMounted}} = Vue;
createApp({{setup(){{
  const lang=ref('ko');
  const tab=ref('overview');
  const krSearch=ref('');const usSearch=ref('');const paperSearch=ref('');
  const pro=PORTFOLIO_DATA.profile;
  const kr=PORTFOLIO_DATA.kr_patents;const us=PORTFOLIO_DATA.us_patents;const pp=PORTFOLIO_DATA.papers;
  const ch=PORTFOLIO_DATA.charts;
  
  const filteredKR=computed(()=>kr.filter(p=>!krSearch.value||(p.title+p.ipc+p.app_number).toLowerCase().includes(krSearch.value.toLowerCase())));
  const filteredUS=computed(()=>us.filter(p=>!usSearch.value||(p.title+p.authors).toLowerCase().includes(usSearch.value.toLowerCase())));
  const filteredPapers=computed(()=>pp.filter(p=>!paperSearch.value||(p.title+p.authors+p.venue).toLowerCase().includes(paperSearch.value.toLowerCase())));
  
  function initCharts(){{
    nextTick(()=>{{
      const t=lang.value==='ko'?'한국어':'en';
      // Chart 1: Tech pie
      const techs=Object.entries(ch.kr_tech).filter(([,v])=>v>0).sort((a,b)=>b[1]-a[1]);
      Plotly.newPlot('chart1',[{{type:'pie',labels:techs.map(t=>t[0]),values:techs.map(t=>t[1]),
        marker:{{colors:techs.map(t=>t[0]==='LCD'?'#ef5350':t[0]==='OLED'?'#42a5f5':t[0]==='Micro LED'?'#66bb6a':'#999')}},
        textinfo:'label+value+percent',hole:.4}}],
        {{title:(t==='ko'?'한국 특허 기술 분류':'KR Patent Technology'),paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{{color:'#ccc'}},margin:{{t:50,b:30,l:30,r:30}}}});
      // Chart 2: Yearly stacked bar
      const years=[...new Set([...Object.keys(ch.kr_yearly),...Object.keys(ch.us_yearly),...Object.keys(ch.paper_yearly)])].map(Number).filter(y=>y>=2000&&y<=2026).sort();
      Plotly.newPlot('chart2',[
        {{x:years,y:years.map(y=>ch.kr_yearly[y]||0),type:'bar',name:t==='ko'?'한국 특허':'KR Patents',marker:{{color:'#42a5f5'}}}},
        {{x:years,y:years.map(y=>ch.us_yearly[y]||0),type:'bar',name:t==='ko'?'미국 특허':'US Patents',marker:{{color:'#ef5350'}}}},
        {{x:years,y:years.map(y=>ch.paper_yearly[y]||0),type:'bar',name:t==='ko'?'논문':'Papers',marker:{{color:'#66bb6a'}}}},
      ],{{barmode:'stack',title:(t==='ko'?'연도별 포트폴리오':'Yearly Portfolio'),paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{{color:'#ccc'}},margin:{{t:50,b:40,l:50,r:20}},legend:{{font:{{color:'#ccc'}}}}}});
      // Chart 3: Tech evolution heatmap
      const htechs=['LCD','OLED','Micro LED','TFT','Driving'];
      const hdata=htechs.map(tech=>years.map(y=>kr.filter(p=>p.year===y&&p.tech===tech).length));
      Plotly.newPlot('chart3',[{{z:hdata,x:years,y:htechs,type:'heatmap',colorscale:'YlOrRd',
        text:hdata.map(r=>r.map(v=>v>0?String(v):'')),texttemplate:'%{{text}}',textfont:{{color:'#333',size:11}},
        hoverongaps:false}}],
        {{title:(t==='ko'?'한국 특허 기술 진화':'KR Patent Tech Evolution'),paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{{color:'#ccc'}},margin:{{t:50,b:40,l:80,r:20}},xaxis:{{title:null}}}});
      // Chart 4: US tech
      const ust=Object.entries(ch.us_tech).filter(([,v])=>v>0).sort((a,b)=>b[1]-a[1]);
      Plotly.newPlot('chart4',[{{type:'bar',x:ust.map(t=>t[1]),y:ust.map(t=>t[0]),orientation:'h',
        marker:{{color:ust.map(t=>t[0]==='LCD'?'#ef5350':t[0]==='OLED'?'#42a5f5':t[0]==='Micro LED'?'#66bb6a':'#999')}},
        text:ust.map(t=>t[1]),textposition:'outside'}}],
        {{title:(t==='ko'?'미국 특허 기술 분류':'US Patent Technology'),paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{{color:'#ccc'}},margin:{{t:50,b:30,l:100,r:50}}}});
      // Chart 5: Timeline
      Plotly.newPlot('chart5',[
        {{x:years,y:years.map(y=>(ch.kr_yearly[y]||0)+(ch.us_yearly[y]||0)+(ch.paper_yearly[y]||0)),type:'scatter',mode:'lines+markers',line:{{color:'#64b5f6',width:3}},marker:{{size:8}},fill:'tozeroy',name:(t==='ko'?'전체':'Total')}},
      ],{{title:(t==='ko'?'전체 발행 추이 (한국+미국+논문)':'Total Output Trend (KR+US+Papers)'),paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{{color:'#ccc'}},margin:{{t:50,b:40,l:50,r:20}}}});
    }});
  }}
  return{{lang,tab,krSearch,usSearch,paperSearch,pro,kr,us,pp,filteredKR,filteredUS,filteredPapers,initCharts}};
}}}}).mount('#app');
</script>
</body>
</html>'''

with open('portfolio_app.html', 'w', encoding='utf-8') as f:
    f.write(html)

import base64
with open('portfolio_app.html', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')
with open('portfolio_app.b64', 'w') as f:
    f.write(b64)

print(f"✅ portfolio_app.html ({len(html):,} bytes)")
print(f"✅ portfolio_app.b64 ({len(b64):,} chars)")
