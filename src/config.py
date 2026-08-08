"""설정 로드: config.yaml (검색 프로필) + .env (비밀 키)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

import yaml
from dotenv import load_dotenv


@dataclass
class TargetProfile:
    name_ko: str
    name_en: str
    affiliations: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    match_threshold: int = 2


@dataclass
class Config:
    target: TargetProfile
    scholar_max_results: int = 50
    kipris_max_results: int = 100
    kipris_search_field: str = "inventor"  # inventor | applicant
    kipris_service_key: str = ""


def load_config(path: str) -> Config:
    """YAML 프로필과 .env를 읽어 Config로 합칩니다."""
    load_dotenv()  # .env -> 환경변수

    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    t = raw.get("target", {}) or {}
    name_ko = (t.get("name_ko") or "").strip()
    name_en = (t.get("name_en") or "").strip()
    if not name_ko and not name_en:
        raise ValueError("config: target.name_ko 또는 target.name_en 중 하나는 반드시 필요합니다.")

    target = TargetProfile(
        name_ko=name_ko,
        name_en=name_en,
        affiliations=[str(a).strip() for a in (t.get("affiliations") or []) if str(a).strip()],
        keywords=[str(k).strip() for k in (t.get("keywords") or []) if str(k).strip()],
        match_threshold=int(t.get("match_threshold", 2)),
    )

    scholar = raw.get("scholar", {}) or {}
    kipris = raw.get("kipris", {}) or {}

    return Config(
        target=target,
        scholar_max_results=int(scholar.get("max_results", 50)),
        kipris_max_results=int(kipris.get("max_results", 100)),
        kipris_search_field=str(kipris.get("search_field", "inventor")).strip() or "inventor",
        kipris_service_key=os.environ.get("KIPRIS_SERVICE_KEY", "").strip(),
    )
