"""설정 로드: config.yaml (검색 프로필) + .env (비밀 키).

여러 명을 한 번에 처리할 수 있도록 profiles(리스트)를 지원한다.
과거 형식(단일 target)도 그대로 읽는다.
"""
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

    @property
    def display_name(self) -> str:
        return self.name_ko or self.name_en


@dataclass
class Config:
    profiles: List[TargetProfile]
    scholar_max_results: int = 50
    kipris_max_results: int = 100
    kipris_search_field: str = "inventor"  # inventor | applicant
    kipris_service_key: str = ""


def _parse_profile(t: dict) -> TargetProfile:
    name_ko = (t.get("name_ko") or "").strip()
    name_en = (t.get("name_en") or "").strip()
    if not name_ko and not name_en:
        raise ValueError("profile: name_ko 또는 name_en 중 하나는 반드시 필요합니다.")
    return TargetProfile(
        name_ko=name_ko,
        name_en=name_en,
        affiliations=[str(a).strip() for a in (t.get("affiliations") or []) if str(a).strip()],
        keywords=[str(k).strip() for k in (t.get("keywords") or []) if str(k).strip()],
        match_threshold=int(t.get("match_threshold", 2)),
    )


def load_config(path: str) -> Config:
    """YAML 프로필과 .env를 읽어 Config로 합칩니다."""
    load_dotenv()  # .env -> 환경변수

    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    # 신 형식(profiles 리스트) 우선, 없으면 구 형식(target 단일)
    profiles: List[TargetProfile] = []
    if isinstance(raw.get("profiles"), list) and raw["profiles"]:
        profiles = [_parse_profile(p or {}) for p in raw["profiles"]]
    elif raw.get("target"):
        profiles = [_parse_profile(raw["target"])]
    else:
        raise ValueError("config: profiles(리스트) 또는 target(단일) 중 하나가 필요합니다.")

    scholar = raw.get("scholar", {}) or {}
    kipris = raw.get("kipris", {}) or {}

    return Config(
        profiles=profiles,
        scholar_max_results=int(scholar.get("max_results", 50)),
        kipris_max_results=int(kipris.get("max_results", 100)),
        kipris_search_field=str(kipris.get("search_field", "inventor")).strip() or "inventor",
        kipris_service_key=os.environ.get("KIPRIS_SERVICE_KEY", "").strip(),
    )
