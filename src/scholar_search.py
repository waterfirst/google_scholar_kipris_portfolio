"""Google Scholar 논문 검색.

`scholarly` 라이브러리를 사용한다. 공식 API가 없어 과도한 호출 시 일시 차단될
수 있으므로, 저자 프로필이 잡히면 프로필 기반으로 논문을 모으고, 없으면
키워드 검색으로 대체한다.

MCP로 바꾸고 싶다면 search() 만 교체하면 된다. 반환 형식(dict 리스트)만 지키면
disambiguation / report 는 그대로 동작한다.
"""
from __future__ import annotations

from typing import List, Dict, Any


def _normalize_pub(pub: Dict[str, Any]) -> Dict[str, Any]:
    """scholarly publication -> 표준 dict."""
    bib = pub.get("bib", {}) if isinstance(pub, dict) else {}
    return {
        "source": "google_scholar",
        "title": bib.get("title", "") or "",
        "authors": bib.get("author", "") or "",
        "venue": bib.get("venue", "") or bib.get("journal", "") or "",
        "year": str(bib.get("pub_year", "") or ""),
        "abstract": bib.get("abstract", "") or "",
        "num_citations": pub.get("num_citations", 0) or 0,
        "url": pub.get("pub_url", "") or pub.get("eprint_url", "") or "",
    }


def search(name_en: str, affiliations: List[str], max_results: int = 50) -> List[Dict[str, Any]]:
    """저자 이름(+소속 힌트)으로 논문을 수집한다.

    실패(네트워크/차단/미설치)하면 빈 리스트를 반환하고 예외를 삼키지 않고
    호출부가 알 수 있도록 RuntimeError를 던진다.
    """
    if not name_en:
        return []

    try:
        from scholarly import scholarly
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "scholarly 미설치: pip install scholarly"
        ) from exc

    results: List[Dict[str, Any]] = []

    # 1) 저자 프로필 검색 (소속 힌트로 정확도 향상)
    query = name_en
    if affiliations:
        query = f"{name_en} {affiliations[0]}"

    try:
        author_gen = scholarly.search_author(query)
        author = next(author_gen, None)
    except Exception as exc:  # 차단/네트워크
        raise RuntimeError(f"Google Scholar 저자 검색 실패: {exc}") from exc

    if author is not None:
        try:
            filled = scholarly.fill(author, sections=["publications"])
            pubs = filled.get("publications", [])[:max_results]
            for p in pubs:
                try:
                    full = scholarly.fill(p)
                except Exception:
                    full = p
                results.append(_normalize_pub(full))
            return results
        except Exception as exc:
            raise RuntimeError(f"Google Scholar 논문 수집 실패: {exc}") from exc

    # 2) 저자 프로필이 없으면 키워드(제목) 검색으로 대체
    try:
        pub_gen = scholarly.search_pubs(name_en)
        for _ in range(max_results):
            pub = next(pub_gen, None)
            if pub is None:
                break
            results.append(_normalize_pub(pub))
    except Exception as exc:
        raise RuntimeError(f"Google Scholar 논문 검색 실패: {exc}") from exc

    return results
