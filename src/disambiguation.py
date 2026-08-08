"""동명이인 필터링.

이름 검색 결과는 동명이인이 섞이므로, 각 항목을 소속기관/연구분야 키워드와
대조해 점수를 매긴다. 점수가 임계값 이상이면 '내 성과'로 채택하고,
미만이면 '확인 필요'로 분리한다.

점수 규칙(기본):
  - 소속(affiliation) 1건 매칭 = +2점
  - 키워드(keyword) 1건 매칭   = +1점
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

AFFILIATION_WEIGHT = 2
KEYWORD_WEIGHT = 1


@dataclass
class MatchResult:
    score: int
    matched_affiliations: List[str]
    matched_keywords: List[str]

    @property
    def is_match(self) -> bool:
        # threshold 비교는 호출부에서. 여기서는 근거만 담는다.
        return self.score > 0


def _contains_any(haystack: str, needles: List[str]) -> List[str]:
    """haystack(소문자 비교) 안에 들어있는 needle 목록을 돌려준다."""
    if not haystack:
        return []
    low = haystack.lower()
    return [n for n in needles if n and n.lower() in low]


def score_item(text_fields: List[str], affiliations: List[str], keywords: List[str]) -> MatchResult:
    """여러 텍스트 필드(소속/제목/초록 등)를 합쳐 점수화한다."""
    blob = " \n ".join(f for f in text_fields if f)

    matched_aff = _contains_any(blob, affiliations)
    matched_kw = _contains_any(blob, keywords)

    score = len(matched_aff) * AFFILIATION_WEIGHT + len(matched_kw) * KEYWORD_WEIGHT
    return MatchResult(
        score=score,
        matched_affiliations=matched_aff,
        matched_keywords=matched_kw,
    )


def split_by_threshold(items, threshold: int):
    """(text_fields, payload) 튜플 목록을 confirmed / uncertain으로 나눈다.

    items: list of (text_fields: List[str], payload: dict, match: MatchResult)
    반환: (confirmed, uncertain)  — 각 원소는 payload에 _match 정보가 붙는다.
    """
    confirmed, uncertain = [], []
    for payload, match in items:
        payload["_score"] = match.score
        payload["_matched_affiliations"] = match.matched_affiliations
        payload["_matched_keywords"] = match.matched_keywords
        if match.score >= threshold:
            confirmed.append(payload)
        else:
            uncertain.append(payload)
    # 점수 높은 순 정렬
    confirmed.sort(key=lambda p: p["_score"], reverse=True)
    uncertain.sort(key=lambda p: p["_score"], reverse=True)
    return confirmed, uncertain
