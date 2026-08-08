"""포트폴리오 보고서 생성 (HTML + Markdown)."""
from __future__ import annotations

import datetime as _dt
from typing import Dict, List, Any

from jinja2 import Template

HTML_TEMPLATE = Template(
    """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ name }} — 연구·특허 포트폴리오</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: -apple-system, "Segoe UI", "Malgun Gothic", sans-serif;
         max-width: 960px; margin: 0 auto; padding: 24px; line-height: 1.6; }
  h1 { margin-bottom: 4px; }
  .sub { color: #888; margin-top: 0; }
  .cards { display: flex; gap: 12px; flex-wrap: wrap; margin: 20px 0; }
  .card { flex: 1 1 160px; border: 1px solid #8883; border-radius: 10px;
          padding: 14px 16px; }
  .card .n { font-size: 28px; font-weight: 700; }
  .card .l { color: #888; font-size: 13px; }
  h2 { border-bottom: 2px solid #8884; padding-bottom: 6px; margin-top: 36px; }
  .item { border-bottom: 1px solid #8882; padding: 10px 0; }
  .item .t { font-weight: 600; }
  .item .m { color: #888; font-size: 13px; }
  .badge { display: inline-block; font-size: 11px; padding: 1px 7px; border-radius: 10px;
           background: #4caf5022; color: #2e7d32; margin-left: 6px; }
  .badge.warn { background: #ff980022; color: #e65100; }
  a { color: #1565c0; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .note { background: #ff980011; border-left: 3px solid #ff9800; padding: 8px 12px;
          border-radius: 4px; font-size: 14px; }
  footer { margin-top: 40px; color: #999; font-size: 12px; }
</style>
</head>
<body>
  <h1>{{ name }}</h1>
  <p class="sub">연구·특허 포트폴리오 · 생성일 {{ generated }}</p>

  <div class="cards">
    <div class="card"><div class="n">{{ papers|length }}</div><div class="l">논문 (Google Scholar)</div></div>
    <div class="card"><div class="n">{{ total_citations }}</div><div class="l">총 피인용수</div></div>
    <div class="card"><div class="n">{{ patents|length }}</div><div class="l">특허·실용신안 (KIPRIS)</div></div>
    <div class="card"><div class="n">{{ uncertain_count }}</div><div class="l">확인 필요</div></div>
  </div>

  <p class="note">
    이름 검색 결과를 소속기관/연구분야 키워드로 필터링했습니다(임계값 {{ threshold }}점).
    소속·키워드 힌트: <b>{{ hints }}</b>
  </p>

  <h2>논문 — {{ papers|length }}건</h2>
  {% for p in papers %}
  <div class="item">
    <div class="t">
      {% if p.url %}<a href="{{ p.url }}" target="_blank">{{ p.title }}</a>{% else %}{{ p.title }}{% endif %}
      <span class="badge">match {{ p._score }}</span>
    </div>
    <div class="m">{{ p.authors }} · {{ p.venue }} {{ p.year }} · 피인용 {{ p.num_citations }}
      {% if p._matched_affiliations %}· 소속: {{ p._matched_affiliations|join(', ') }}{% endif %}
    </div>
  </div>
  {% else %}<p>수집된 논문이 없습니다.</p>{% endfor %}

  <h2>특허·실용신안 — {{ patents|length }}건</h2>
  {% for p in patents %}
  <div class="item">
    <div class="t">
      {% if p.url %}<a href="{{ p.url }}" target="_blank">{{ p.title }}</a>{% else %}{{ p.title }}{% endif %}
      <span class="badge">match {{ p._score }}</span>
    </div>
    <div class="m">출원인: {{ p.applicant }} · 출원번호 {{ p.application_number }}
      · {{ p.application_date }} · 상태: {{ p.register_status }}
      {% if p.ipc %}· IPC {{ p.ipc }}{% endif %}
    </div>
  </div>
  {% else %}<p>수집된 특허가 없습니다.</p>{% endfor %}

  {% if uncertain %}
  <h2>확인 필요 (동명이인 의심) — {{ uncertain|length }}건</h2>
  <p class="note">소속/키워드 매칭 점수가 임계값 미만입니다. 본인 성과가 맞는지 직접 확인하세요.</p>
  {% for p in uncertain %}
  <div class="item">
    <div class="t">
      {% if p.url %}<a href="{{ p.url }}" target="_blank">{{ p.title }}</a>{% else %}{{ p.title }}{% endif %}
      <span class="badge warn">{{ p.source }} · match {{ p._score }}</span>
    </div>
    <div class="m">
      {% if p.source == 'kipris' %}출원인: {{ p.applicant }} · {{ p.application_number }}
      {% else %}{{ p.authors }} · {{ p.venue }} {{ p.year }}{% endif %}
    </div>
  </div>
  {% endfor %}
  {% endif %}

  <footer>google_scholar_kipris_portfolio · 자동 생성 보고서. 필터링 결과는 사람이 최종 검토가 필요합니다.</footer>
</body>
</html>"""
)


def _build_context(name: str, papers, patents, uncertain, threshold: int, hints: str) -> Dict[str, Any]:
    total_citations = sum(int(p.get("num_citations", 0) or 0) for p in papers)
    return {
        "name": name,
        "generated": _dt.date.today().isoformat(),
        "papers": papers,
        "patents": patents,
        "uncertain": uncertain,
        "uncertain_count": len(uncertain),
        "total_citations": total_citations,
        "threshold": threshold,
        "hints": hints,
    }


def render_html(name, papers, patents, uncertain, threshold, hints) -> str:
    return HTML_TEMPLATE.render(**_build_context(name, papers, patents, uncertain, threshold, hints))


def render_markdown(name, papers, patents, uncertain, threshold, hints) -> str:
    total_citations = sum(int(p.get("num_citations", 0) or 0) for p in papers)
    lines: List[str] = []
    lines.append(f"# {name} — 연구·특허 포트폴리오")
    lines.append("")
    lines.append(f"- 생성일: {_dt.date.today().isoformat()}")
    lines.append(f"- 논문: **{len(papers)}건**, 총 피인용: **{total_citations}**")
    lines.append(f"- 특허·실용신안: **{len(patents)}건**")
    lines.append(f"- 확인 필요(동명이인 의심): **{len(uncertain)}건**")
    lines.append(f"- 필터 기준(임계값 {threshold}): {hints}")
    lines.append("")

    lines.append(f"## 논문 ({len(papers)}건)")
    if papers:
        for p in papers:
            title = f"[{p['title']}]({p['url']})" if p.get("url") else p["title"]
            lines.append(
                f"- {title} — {p.get('authors','')} · {p.get('venue','')} "
                f"{p.get('year','')} · 피인용 {p.get('num_citations',0)} (match {p.get('_score',0)})"
            )
    else:
        lines.append("- (없음)")
    lines.append("")

    lines.append(f"## 특허·실용신안 ({len(patents)}건)")
    if patents:
        for p in patents:
            title = f"[{p['title']}]({p['url']})" if p.get("url") else p["title"]
            lines.append(
                f"- {title} — 출원인: {p.get('applicant','')} · "
                f"{p.get('application_number','')} · {p.get('application_date','')} · "
                f"상태: {p.get('register_status','')} (match {p.get('_score',0)})"
            )
    else:
        lines.append("- (없음)")
    lines.append("")

    if uncertain:
        lines.append(f"## 확인 필요 — 동명이인 의심 ({len(uncertain)}건)")
        for p in uncertain:
            title = f"[{p['title']}]({p['url']})" if p.get("url") else p["title"]
            lines.append(f"- [{p.get('source','')}] {title} (match {p.get('_score',0)})")
        lines.append("")

    return "\n".join(lines)
