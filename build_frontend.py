# -*- coding: utf-8 -*-
import sys,io;sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
import json

with open('portfolio_data.json','r',encoding='utf-8') as f: DATA=json.load(f)
DATA_JS=json.dumps(DATA,ensure_ascii=False)

html=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Research Portfolio</title>
<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0a0a1a;--bg2:#12122a;--card:rgba(255,255,255,0.03);--border:rgba(255,255,255,0.06);--text:#c8c8d4;--text2:#8888a0;--blue:#5b9cf5;--red:#f56565;--green:#68d391;--orange:#f6ad55;--purple:#b794f4;--gradient:linear-gradient(135deg,#667eea 0%,#764ba2 100%)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter','Noto Sans KR',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}}
#app{{max-width:1440px;margin:0 auto;padding:20px}}
.header{{text-align:center;padding:32px 20px 12px}}
.header h1{{font-size:2.2em;font-weight:900;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-1px}}
.header .sub{{color:var(--text2);margin-top:6px;font-size:0.95em;font-weight:300}}
.cards{{display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap}}
.card{{flex:1;min-width:120px;background:var(--card);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:14px;padding:18px 14px;text-align:center;transition:transform .2s}}
.card:hover{{transform:translateY(-3px);box-shadow:0 8px 32px rgba(0,0,0,0.3)}}
.card .val{{font-size:1.8em;font-weight:800;letter-spacing:-1px}}
.card .lbl{{color:var(--text2);font-size:0.7em;text-transform:uppercase;letter-spacing:1px;margin-top:4px}}
.card.c0{{border-top:3px solid var(--orange)}}.card.c1{{border-top:3px solid var(--blue)}}.card.c2{{border-top:3px solid var(--red)}}.card.c3{{border-top:3px solid var(--green)}}.card.c4{{border-top:3px solid var(--purple)}}
.tabs{{display:flex;gap:2px;margin-bottom:0;flex-wrap:wrap}}
.tab{{padding:10px 20px;background:rgba(255,255,255,0.03);border:1px solid transparent;border-radius:12px 12px 0 0;cursor:pointer;font-size:0.84em;font-weight:500;color:var(--text2);transition:all .2s}}
.tab:hover{{color:var(--text)}}
.tab.active{{background:var(--card);border-color:var(--border);border-bottom-color:transparent;color:#fff}}
.tab .badge{{background:rgba(255,255,255,0.08);padding:1px 8px;border-radius:10px;font-size:0.75em;margin-left:6px}}
.content{{background:var(--card);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:0 14px 14px 14px;padding:24px;min-height:300px}}
.chart-grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:16px}}
.chart-panel{{min-height:360px;border-radius:10px}}
.chart-full{{grid-column:1/-1;min-height:380px}}
.tbl-ctrl{{display:flex;gap:10px;margin-bottom:12px;align-items:center;flex-wrap:wrap}}
.tbl-ctrl input{{flex:1;min-width:180px;padding:8px 14px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:0.84em;outline:none}}
.tbl-ctrl input:focus{{border-color:var(--blue)}}
.tbl-info{{color:var(--text2);font-size:0.78em}}
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
.timeline{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:18px}}
.phase{{background:rgba(255,255,255,0.02);border-radius:12px;padding:16px;border-left:4px solid var(--blue)}}
.phase.p1{{border-color:var(--red)}}.phase.p2{{border-color:var(--blue)}}.phase.p3{{border-color:var(--green)}}.phase.p4{{border-color:var(--orange)}}
.phase h4{{font-size:0.88em;margin-bottom:6px;color:#ddd}}
.phase p{{color:var(--text2);font-size:0.8em;line-height:1.5}}
.lang-bar{{text-align:right;margin-bottom:8px}}
.lang-btn{{padding:5px 14px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:8px;color:var(--text2);cursor:pointer;font-size:0.78em;margin-left:4px}}
.lang-btn.active{{background:rgba(91,156,245,0.15);border-color:var(--blue);color:var(--blue)}}
@media(max-width:768px){{.chart-grid{{grid-template-columns:1fr}}.cards{{flex-direction:column}}.header h1{{font-size:1.5em}}}}
</style>
</head>
<body>
<div id="app">
<div class="lang-bar">
  <button class="lang-btn" :class="{{active:lang==='en'}}" @click="lang='en'">English</button>
  <button class="lang-btn" :class="{{active:lang==='ko'}}" @click="lang='ko'">한국어</button>
</div>
<div class="header">
  <h1>{{ lang==='ko'?'연구 포트폴리오 분석':'Research Portfolio Analysis' }}</h1>
  <p class="sub">{{ lang==='ko'?'Google Scholar + KIPRIS 통합 특허·논문 분석':'Integrated Patent & Paper Analysis - Google Scholar + KIPRIS' }}</p>
</div>
<div class="cards">
  <div class="card c0"><div class="val">{{data.summary.total_ip}}</div><div class="lbl">{{lang==='ko'?'총 IP 자산':'Total IP'}}</div></div>
  <div class="card c1"><div class="val">{{data.summary.kr_patents}}</div><div class="lbl">{{lang==='ko'?'한국 특허':'KR Patents'}}</div></div>
  <div class="card c2"><div class="val">{{data.summary.us_patents}}</div><div class="lbl">{{lang==='ko'?'미국 특허':'US Patents'}}</div></div>
  <div class="card c3"><div class="val">{{data.summary.papers}}</div><div class="lbl">{{lang==='ko'?'논문':'Papers'}}</div></div>
  <div class="card c4"><div class="val">{{data.profile.stats.h_index}}</div><div class="lbl">h-index</div></div>
  <div class="card"><div class="val">{{(data.profile.stats.total_cites||0).toLocaleString()}}</div><div class="lbl">{{lang==='ko'?'인용':'Citations'}}</div></div>
</div>
<div class="tabs">
  <div class="tab" :class="{{active:tab==='overview'}}" @click="tab='overview'">{{lang==='ko'?'개요':'Overview'}}</div>
  <div class="tab" :class="{{active:tab==='kr'}}" @click="tab='kr'">{{lang==='ko'?'한국 특허':'KR Patents'}}<span class="badge">{{data.kr_patents.length}}</span></div>
  <div class="tab" :class="{{active:tab==='us'}}" @click="tab='us'">{{lang==='ko'?'미국 특허':'US Patents'}}<span class="badge">{{data.us_patents.length}}</span></div>
  <div class="tab" :class="{{active:tab==='papers'}}" @click="tab='papers'">{{lang==='ko'?'논문':'Papers'}}<span class="badge">{{data.papers.length}}</span></div>
  <div class="tab" :class="{{active:tab==='charts'}}" @click="tab='charts';renderCharts()">{{lang==='ko'?'차트':'Charts'}}</div>
</div>
<div class="content">
  <div v-if="tab==='overview'">
    <div class="timeline">
      <div class="phase p1"><h4>{{lang==='ko'?'Phase 1: LCD 시대 (2001-2017)':'Phase 1: LCD Era (2001-2017)'}}</h4><p>{{lang==='ko'?'TFT-LCD 기판, 액정 배향(PVA/VA), 컬러필터. 삼성전자 LCD 사업부.':'TFT-LCD substrates, PVA/VA alignment, color filters. Samsung LCD Division.'}}</p></div>
      <div class="phase p2"><h4>{{lang==='ko'?'Phase 2: OLED 전환 (2017-2022)':'Phase 2: OLED Transition (2017-2022)'}}</h4><p>{{lang==='ko'?'Black PDL(LTPO), UPC, Polarizer-free, Foldable. 삼성디스플레이 OLED Innovation.':'Black PDL (LTPO), UPC, Polarizer-free, Foldable. Samsung Display OLED Innovation.'}}</p></div>
      <div class="phase p3"><h4>{{lang==='ko'?'Phase 3: Micro LED + Automotive (2021-2026)':'Phase 3: Micro LED + Automotive (2021-2026)'}}</h4><p>{{lang==='ko'?'Micro LED 전사·타일링, Automotive OLED Switchable Privacy.':'Micro LED transfer/tiling, Automotive OLED Switchable Privacy.'}}</p></div>
      <div class="phase p4"><h4>{{lang==='ko'?'Phase 4: TFT 신뢰성 (2026.5-현재)':'Phase 4: TFT Reliability (2026.5-Present)'}}</h4><p>{{lang==='ko'?'개발품질그룹 TFT 소자 신뢰성. 풀사이클 엔지니어.':'Development Quality Group, TFT reliability. Full-cycle engineer.'}}</p></div>
    </div>
    <div style="margin-top:20px">
      <h3 style="color:var(--text2);margin-bottom:8px;font-size:0.82em;text-transform:uppercase;letter-spacing:1px">{{lang==='ko'?'연구 분야':'Research Fields'}}</h3>
      <div style="display:flex;gap:6px;flex-wrap:wrap"><span v-for="f in data.profile.fields" style="padding:5px 14px;background:rgba(91,156,245,0.1);border-radius:20px;font-size:0.8em;color:var(--blue)">{{f}}</span></div>
    </div>
  </div>
  <div v-if="tab==='kr'">
    <div class="tbl-ctrl"><input v-model="krFilter" :placeholder="lang==='ko'?'검색 (제목, IPC, 출원번호)...':'Search (title, IPC, app#)...'"><span class="tbl-info">{{filteredKR.length}} / {{data.kr_patents.length}}</span></div>
    <div class="tbl-wrap"><table><thead><tr><th>#</th><th>{{lang==='ko'?'출원일':'Date'}}</th><th>{{lang==='ko'?'상태':'St'}}</th><th>{{lang==='ko'?'기술':'Tech'}}</th><th>{{lang==='ko'?'발명의 명칭':'Title'}}</th><th>{{lang==='ko'?'출원번호':'App#'}}</th></tr></thead>
    <tbody><tr v-for="(p,i) in filteredKR" :key="i"><td>{{i+1}}</td><td style="white-space:nowrap">{{p.app_date}}</td><td><span class="tag" :class="p.status==='등록'?'reg':'pub'">{{p.status}}</span></td><td><span class="tag">{{p.tech}}</span></td><td :title="p.title">{{p.title}}</td><td style="font-family:'JetBrains Mono',monospace;font-size:0.78em">{{p.app_number}}</td></tr></tbody></table></div>
  </div>
  <div v-if="tab==='us'">
    <div class="tbl-ctrl"><input v-model="usFilter" :placeholder="lang==='ko'?'검색 (제목, 저자)...':'Search (title, author)...'"><span class="tbl-info">{{filteredUS.length}} / {{data.us_patents.length}}</span></div>
    <div class="tbl-wrap"><table><thead><tr><th>#</th><th>{{lang==='ko'?'연도':'Yr'}}</th><th>{{lang==='ko'?'역할':'Role'}}</th><th>{{lang==='ko'?'인용':'Cite'}}</th><th>{{lang==='ko'?'기술':'Tech'}}</th><th>{{lang==='ko'?'제목':'Title'}}</th></tr></thead>
    <tbody><tr v-for="(p,i) in filteredUS" :key="i"><td>{{i+1}}</td><td>{{p.year}}</td><td><span class="tag" :class="p.lead?'lead':'co'">{{p.lead?(lang==='ko'?'주발명':'Lead'):(lang==='ko'?'공동':'Co')}}</span></td><td>{{p.cites||0}}</td><td><span class="tag">{{p.tech}}</span></td><td :title="p.title">{{p.title}}</td></tr></tbody></table></div>
  </div>
  <div v-if="tab==='papers'">
    <div class="tbl-ctrl"><input v-model="paperFilter" :placeholder="lang==='ko'?'검색 (제목, 저자)...':'Search (title, author)...'"><span class="tbl-info">{{filteredPapers.length}} / {{data.papers.length}}</span></div>
    <div class="tbl-wrap"><table><thead><tr><th>#</th><th>{{lang==='ko'?'연도':'Yr'}}</th><th>{{lang==='ko'?'인용':'Cite'}}</th><th>{{lang==='ko'?'기술':'Tech'}}</th><th>{{lang==='ko'?'제목':'Title'}}</th><th>{{lang==='ko'?'저널':'Venue'}}</th></tr></thead>
    <tbody><tr v-for="(p,i) in filteredPapers" :key="i"><td>{{i+1}}</td><td>{{p.year}}</td><td>{{p.cites||0}}</td><td><span class="tag">{{p.tech}}</span></td><td :title="p.title">{{p.title}}</td><td style="color:var(--text2);font-size:0.78em">{{p.venue}}</td></tr></tbody></table></div>
  </div>
  <div v-if="tab==='charts'">
    <div class="chart-grid"><div class="chart-panel" id="chart1"></div><div class="chart-panel" id="chart2"></div></div>
    <div class="chart-grid"><div class="chart-panel" id="chart3"></div><div class="chart-panel" id="chart4"></div></div>
    <div class="chart-grid"><div class="chart-panel chart-full" id="chart5"></div></div>
  </div>
</div>
</div>
<script>
var PORTFOLIO_DATA = {DATA_JS};

var app = Vue.createApp({{
  data() {{
    return {{
      lang: 'en',
      tab: 'overview',
      krFilter: '', usFilter: '', paperFilter: '',
      data: PORTFOLIO_DATA
    }}
  }},
  computed: {{
    filteredKR() {{
      var f = this.krFilter.toLowerCase();
      var items = this.data.kr_patents || [];
      if (!f) return items;
      return items.filter(function(p) {{ return (p.title+p.ipc+p.app_number).toLowerCase().indexOf(f) !== -1; }});
    }},
    filteredUS() {{
      var f = this.usFilter.toLowerCase();
      var items = this.data.us_patents || [];
      if (!f) return items;
      return items.filter(function(p) {{ return (p.title||'').toLowerCase().indexOf(f) !== -1 || (p.authors||'').toLowerCase().indexOf(f) !== -1; }});
    }},
    filteredPapers() {{
      var f = this.paperFilter.toLowerCase();
      var items = this.data.papers || [];
      if (!f) return items;
      return items.filter(function(p) {{ return (p.title||'').toLowerCase().indexOf(f) !== -1 || (p.authors||'').toLowerCase().indexOf(f) !== -1 || (p.venue||'').toLowerCase().indexOf(f) !== -1; }});
    }}
  }},
  methods: {{
    renderCharts: function() {{
      var self = this;
      Vue.nextTick(function() {{
        var d = self.data;
        var ch = d.charts || {{}};
        var isKo = self.lang === 'ko';
        var cfg = {{paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{{color:'#8888a0'}},margin:{{t:50,b:40,l:60,r:30}}}};

        // Chart 1: KR Tech Pie
        var techs = [];
        var tkeys = Object.keys(ch.kr_tech || {{}});
        for (var i=0;i<tkeys.length;i++) {{ var k=tkeys[i]; if(ch.kr_tech[k]>0) techs.push([k,ch.kr_tech[k]]); }}
        techs.sort(function(a,b){{return b[1]-a[1]}});
        var colors = techs.map(function(t){{return t[0]==='LCD'?'#f56565':t[0]==='OLED'?'#5b9cf5':t[0]==='Micro LED'?'#68d391':'#8888a0'}});
        Plotly.newPlot('chart1', [{{type:'pie',labels:techs.map(function(t){{return t[0]}}),values:techs.map(function(t){{return t[1]}}),marker:{{colors:colors}},textinfo:'label+value+percent',hole:0.4}}], Object.assign({{}},cfg,{{title:isKo?'한국 특허 기술 분류':'KR Patent Technology',margin:{{t:50,b:30,l:10,r:10}}}}));

        // Chart 2: Yearly Stacked Bar
        var years=[];
        var ykeys=Object.keys(Object.assign({{}},ch.kr_yearly||{{}},ch.us_yearly||{{}},ch.paper_yearly||{{}}));
        for(var i=0;i<ykeys.length;i++){{var y=parseInt(ykeys[i]);if(y>=2000&&y<=2026)years.push(y);}}
        years.sort(function(a,b){{return a-b}});
        var ykr=years.map(function(y){{return (ch.kr_yearly||{{}})[y]||0}});
        var yus=years.map(function(y){{return (ch.us_yearly||{{}})[y]||0}});
        var ypp=years.map(function(y){{return (ch.paper_yearly||{{}})[y]||0}});
        Plotly.newPlot('chart2',[
          {{x:years,y:ykr,type:'bar',name:isKo?'한국 특허':'KR Patents',marker:{{color:'#5b9cf5'}}}},
          {{x:years,y:yus,type:'bar',name:isKo?'미국 특허':'US Patents',marker:{{color:'#f56565'}}}},
          {{x:years,y:ypp,type:'bar',name:isKo?'논문':'Papers',marker:{{color:'#68d391'}}}}
        ],Object.assign({{}},cfg,{{barmode:'stack',title:isKo?'연도별 포트폴리오':'Yearly Portfolio',legend:{{font:{{color:'#8888a0'}}}}}}));

        // Chart 3: Heatmap
        var htechs=['LCD','OLED','Micro LED','TFT','Driving','Panel'];
        var hdata=htechs.map(function(tech){{return years.map(function(y){{return (d.kr_patents||[]).filter(function(p){{return p.year===y&&p.tech===tech}}).length}})}});
        Plotly.newPlot('chart3',[{{z:hdata,x:years,y:htechs,type:'heatmap',colorscale:'YlOrRd',text:hdata.map(function(r){{return r.map(function(v){{return v>0?String(v):''}})}}),texttemplate:'%{{text}}',textfont:{{color:'#333',size:11}}}}],Object.assign({{}},cfg,{{title:isKo?'한국 특허 기술 진화':'KR Patent Tech Evolution',margin:{{t:50,b:40,l:100,r:20}}}}));

        // Chart 4: US Tech
        var ust=[];
        var ukeys=Object.keys(ch.us_tech||{{}});
        for(var i=0;i<ukeys.length;i++){{var k=ukeys[i];if(ch.us_tech[k]>0)ust.push([k,ch.us_tech[k]]);}}
        ust.sort(function(a,b){{return b[1]-a[1]}});
        if(ust.length) Plotly.newPlot('chart4',[{{type:'bar',x:ust.map(function(t){{return t[1]}}),y:ust.map(function(t){{return t[0]}}),orientation:'h',marker:{{color:ust.map(function(t){{return t[0]==='LCD'?'#f56565':t[0]==='OLED'?'#5b9cf5':t[0]==='Micro LED'?'#68d391':'#8888a0'}})}},text:ust.map(function(t){{return t[1]}}),textposition:'outside'}}],Object.assign({{}},cfg,{{title:isKo?'미국 특허 기술 분류':'US Patent Technology',margin:{{t:50,b:30,l:120,r:40}}}}));

        // Chart 5: Total Output
        Plotly.newPlot('chart5',[{{x:years,y:years.map(function(y){{return ykr[years.indexOf(y)]+yus[years.indexOf(y)]+ypp[years.indexOf(y)]}}),type:'scatter',mode:'lines+markers',line:{{color:'#b794f4',width:3}},marker:{{size:8,color:'#b794f4'}},fill:'tozeroy',name:isKo?'전체':'Total'}}],Object.assign({{}},cfg,{{title:isKo?'전체 발행 추이 (KR+US+Papers)':'Total Output Trend',margin:{{t:50,b:40,l:50,r:20}}}}));
      }});
    }}
  }}
}});

app.mount('#app');
</script>
</body>
</html>'''

out='frontend/index.html'
with open(out,'w',encoding='utf-8') as f: f.write(html)
import base64
with open(out,'rb') as f: b64=base64.b64encode(f.read()).decode()
with open('frontend/index.b64','w') as f: f.write(b64)
print(f'OK: {out} ({len(html):,} bytes) + index.b64 ({len(b64):,} chars)')
