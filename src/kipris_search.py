"""KIPRIS 특허/실용신안 검색.

KIPRIS Plus Open API 의 '특허·실용신안 서지정보 검색'(getAdvancedSearch)을 사용한다.
응답은 XML이며, 필요한 서지 필드만 표준 dict로 변환한다.

서비스 키: https://plus.kipris.or.kr 에서 발급 후 .env 의 KIPRIS_SERVICE_KEY 에 설정.

MCP로 바꾸고 싶다면 search() 만 교체하면 된다.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import List, Dict, Any

import requests

BASE_URL = (
    "http://plus.kipris.or.kr/openapi/rest/"
    "patUtiliInfoSearchSevice/getAdvancedSearch"
)


def _text(node: ET.Element, tag: str) -> str:
    el = node.find(tag)
    return (el.text or "").strip() if el is not None and el.text else ""


def _normalize_item(item: ET.Element) -> Dict[str, Any]:
    """KIPRIS item element -> 표준 dict."""
    return {
        "source": "kipris",
        "title": _text(item, "inventionTitle"),
        "applicant": _text(item, "applicantName"),
        "application_number": _text(item, "applicationNumber"),
        "application_date": _text(item, "applicationDate"),
        "register_status": _text(item, "registerStatus"),
        "register_number": _text(item, "registerNumber"),
        "publication_number": _text(item, "publicationNumber"),
        "ipc": _text(item, "ipcNumber"),
        "abstract": _text(item, "astrtCont"),
        "url": _kipris_url(_text(item, "applicationNumber")),
    }


def _kipris_url(application_number: str) -> str:
    an = application_number.replace("-", "")
    if not an:
        return ""
    # KIPRIS 상세보기(출원번호 기반) 공개 링크
    return f"https://www.kipris.or.kr/khome/search/searchResult.do?applicationNumber={an}"


def search(
    name_ko: str,
    service_key: str,
    search_field: str = "inventor",
    affiliations: List[str] | None = None,
    max_results: int = 100,
) -> List[Dict[str, Any]]:
    """발명자/출원인 이름으로 특허를 수집한다.

    search_field: 'inventor'(발명자) 또는 'applicant'(출원인)
    """
    if not name_ko:
        return []
    if not service_key:
        raise RuntimeError(
            "KIPRIS_SERVICE_KEY 가 없습니다. .env 에 서비스 키를 설정하세요."
        )

    params: Dict[str, Any] = {
        "ServiceKey": service_key,
        "patent": "true",
        "utility": "true",
        "numOfRows": min(max_results, 500),
        "pageNo": 1,
    }
    if search_field == "applicant":
        params["applicant"] = name_ko
    else:
        params["inventors"] = name_ko

    try:
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"KIPRIS 요청 실패: {exc}") from exc

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as exc:
        raise RuntimeError(f"KIPRIS 응답 파싱 실패: {exc}") from exc

    # 오류 응답 확인
    result_code = root.findtext(".//resultCode")
    result_msg = root.findtext(".//resultMsg")
    if result_code and result_code not in ("00", "0"):
        raise RuntimeError(f"KIPRIS API 오류 [{result_code}]: {result_msg}")

    items = root.findall(".//item")
    return [_normalize_item(it) for it in items][:max_results]
