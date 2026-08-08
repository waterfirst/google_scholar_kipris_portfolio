"""전체 오케스트레이션.

    python -m src.main --config config.yaml --out report

흐름: 설정 로드 → (프로필마다) Scholar/KIPRIS 검색 → 동명이인 필터링 →
      보고서(HTML/MD) 저장. 프로필이 여러 개면 사람별로 파일을 나눠 생성한다.
"""
from __future__ import annotations

import argparse
import re
import sys
from typing import List, Dict, Any

from .config import load_config, Config, TargetProfile
from . import scholar_search, kipris_search, disambiguation, report


def _slugify(name: str) -> str:
    """파일명에 안전한 슬러그. 한글은 유지하고 공백/특수문자만 정리."""
    s = name.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^0-9a-z가-힣_\-]", "", s)
    return s or "profile"


def _score_papers(papers: List[Dict[str, Any]], profile: TargetProfile):
    scored = []
    for p in papers:
        match = disambiguation.score_item(
            text_fields=[p.get("authors", ""), p.get("venue", ""),
                         p.get("title", ""), p.get("abstract", "")],
            affiliations=profile.affiliations,
            keywords=profile.keywords,
        )
        scored.append((p, match))
    return scored


def _score_patents(patents: List[Dict[str, Any]], profile: TargetProfile):
    scored = []
    for p in patents:
        match = disambiguation.score_item(
            text_fields=[p.get("applicant", ""), p.get("title", ""),
                         p.get("abstract", ""), p.get("ipc", "")],
            affiliations=profile.affiliations,
            keywords=profile.keywords,
        )
        scored.append((p, match))
    return scored


def _process_profile(profile: TargetProfile, cfg: Config, out_prefix: str, multi: bool) -> None:
    display_name = profile.display_name
    print(f"\n=== 프로필: {display_name} ===")
    print(f"[*] 소속 힌트: {', '.join(profile.affiliations) or '(없음)'}")
    print(f"[*] 키워드 힌트: {', '.join(profile.keywords) or '(없음)'}")

    # 1) Google Scholar
    papers: List[Dict[str, Any]] = []
    try:
        print("[*] Google Scholar 검색 중...")
        papers = scholar_search.search(
            profile.name_en, profile.affiliations, cfg.scholar_max_results
        )
        print(f"    -> {len(papers)}건 수집")
    except RuntimeError as exc:
        print(f"    [!] 논문 수집 건너뜀: {exc}", file=sys.stderr)

    # 2) KIPRIS
    patents: List[Dict[str, Any]] = []
    try:
        print("[*] KIPRIS 검색 중...")
        patents = kipris_search.search(
            profile.name_ko, cfg.kipris_service_key,
            cfg.kipris_search_field, profile.affiliations, cfg.kipris_max_results
        )
        print(f"    -> {len(patents)}건 수집")
    except RuntimeError as exc:
        print(f"    [!] 특허 수집 건너뜀: {exc}", file=sys.stderr)

    # 3) 동명이인 필터링
    paper_ok, paper_uncertain = disambiguation.split_by_threshold(
        _score_papers(papers, profile), profile.match_threshold
    )
    patent_ok, patent_uncertain = disambiguation.split_by_threshold(
        _score_patents(patents, profile), profile.match_threshold
    )
    uncertain = paper_uncertain + patent_uncertain
    print(f"[*] 채택: 논문 {len(paper_ok)} / 특허 {len(patent_ok)} · 확인필요 {len(uncertain)}")

    # 4) 보고서
    hints = ", ".join(profile.affiliations + profile.keywords) or "(없음)"
    html = report.render_html(display_name, paper_ok, patent_ok, uncertain,
                              profile.match_threshold, hints)
    md = report.render_markdown(display_name, paper_ok, patent_ok, uncertain,
                                profile.match_threshold, hints)

    # 여러 명이면 파일명에 이름 슬러그를 붙인다.
    suffix = f"_{_slugify(display_name)}" if multi else ""
    html_path = f"{out_prefix}{suffix}.html"
    md_path = f"{out_prefix}{suffix}.md"
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"[+] 보고서 생성 완료: {html_path}, {md_path}")


def run(config_path: str, out_prefix: str) -> int:
    cfg = load_config(config_path)
    multi = len(cfg.profiles) > 1
    print(f"[*] 프로필 {len(cfg.profiles)}개 처리")
    for profile in cfg.profiles:
        _process_profile(profile, cfg, out_prefix, multi)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="논문(Google Scholar)+특허(KIPRIS) 포트폴리오 보고서 생성"
    )
    parser.add_argument("--config", default="config.yaml", help="설정 파일 경로")
    parser.add_argument("--out", default="report", help="출력 파일 접두사 (기본: report)")
    args = parser.parse_args(argv)

    try:
        return run(args.config, args.out)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[오류] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
