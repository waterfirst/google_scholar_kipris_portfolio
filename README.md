# google_scholar_kipris_portfolio

연구자 **한 사람의 이름**을 입력하면 **논문(Google Scholar)** 과 **특허(KIPRIS)** 정보를
함께 수집하여 **연구·특허 포트폴리오 보고서**(HTML / Markdown)로 만들어 주는 도구입니다.

## 왜 만들었나

이름만으로 검색하면 **동명이인(同名異人)** 의 논문·특허가 섞여 잘못된 포트폴리오가 만들어집니다.
이 프로젝트는 이름 검색 결과를 **소속기관(affiliation)** 과 **연구분야 키워드** 로 다시 걸러
내가 원하는 인물의 성과만 남기는 것을 핵심 목표로 합니다.

## 무엇을 하나

1. **Google Scholar 검색** — 저자 이름(+소속)으로 논문 목록·인용수를 수집합니다.
2. **KIPRIS 검색** — 출원인/발명자 이름으로 특허·실용신안을 수집합니다.
   (KIPRIS Plus Open API 사용, 서비스 키 필요)
3. **동명이인 필터링(disambiguation)** — 각 결과를 소속/키워드와 대조해 점수를 매기고,
   임계값 미만은 "확인 필요"로 분리합니다.
4. **포트폴리오 보고서 생성** — 요약 지표, 논문 목록, 특허 목록을 HTML/Markdown으로 출력합니다.

## 데이터 소스와 MCP에 대하여

기획 단계에서는 "구글 스칼라 MCP + 키프리스 MCP" 두 개의 MCP로 검색하는 것을 상정했습니다.
다만 두 MCP는 claude.ai 커넥터에 별도로 등록·인증해야 하며 현재 세션 기본 환경에는 없습니다.
그래서 이 프로젝트는 **MCP에 의존하지 않고 각 서비스의 공개 데이터 소스를 직접 사용**하도록
구현했습니다. 이렇게 하면 어느 환경에서든 그대로 실행할 수 있습니다.

| 소스 | 구현 방식 | 필요한 것 |
|---|---|---|
| Google Scholar | `scholarly` 라이브러리 | (없음, 과도한 호출 시 차단될 수 있음) |
| KIPRIS | KIPRIS Plus Open API (REST) | 서비스 키 (`KIPRIS_SERVICE_KEY`) |

> MCP를 꼭 쓰고 싶다면 `src/scholar_search.py` / `src/kipris_search.py` 의 `search()`
> 함수만 MCP 호출로 교체하면 나머지(필터링·보고서)는 그대로 재사용됩니다.

## 설치

```bash
pip install -r requirements.txt
cp .env.example .env          # KIPRIS_SERVICE_KEY 입력
cp config.example.yaml config.yaml   # 이름/소속/키워드 입력
```

## 검색 대상 설정 (`config.yaml`)

동명이인을 거르는 기준을 여기서 정합니다.

```yaml
target:
  name_ko: "홍길동"                # KIPRIS(한글) 검색용
  name_en: "Gildong Hong"          # Google Scholar 검색용
  affiliations:                    # 소속기관 (하나라도 맞으면 가점)
    - "Samsung Display"
    - "삼성디스플레이"
    - "Seoul National University"
  keywords:                        # 연구/기술 분야 (제목·초록 대조)
    - "OLED"
    - "display"
    - "thin film"
  match_threshold: 1               # 이 점수 미만이면 "확인 필요"로 분리
```

## 실행

```bash
python -m src.main --config config.yaml --out report
```

- `report.html` : 브라우저에서 볼 수 있는 포트폴리오 보고서
- `report.md`   : Markdown 보고서

## 프로젝트 구조

```
src/
  config.py           # config.yaml + .env 로드
  scholar_search.py   # Google Scholar 검색
  kipris_search.py    # KIPRIS Open API 검색
  disambiguation.py   # 동명이인 필터링(소속/키워드 점수화)
  report.py           # HTML/Markdown 보고서 생성
  main.py             # 전체 오케스트레이션
```

## 주의

- Google Scholar는 공식 API가 없어 짧은 시간에 많이 호출하면 일시적으로 차단될 수 있습니다.
  차단 시 잠시 후 재시도하거나 프록시를 사용하세요.
- KIPRIS Open API는 [KIPRIS Plus](https://plus.kipris.or.kr)에서 무료 서비스 키를 발급받아야 합니다.
- 수집된 결과는 자동 필터링이므로, 보고서의 "확인 필요" 항목은 사람이 최종 검토하세요.
