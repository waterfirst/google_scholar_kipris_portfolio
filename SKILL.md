# SKILL.md — Google Scholar + KIPRIS 특허/논문 분석 방법론

## 개요

연구자의 Google Scholar 프로필과 KIPRIS(한국특허정보원) 특허 데이터를 통합 분석하여
시각화 보고서(HTML+base64)를 자동 생성하는 작업 파이프라인.

## 데이터 소스

| 소스 | 내용 | 수집 방법 |
|---|---|---|
| Google Scholar | US 특허 93건 + 논문 7건 (총 100건) | Python `requests` + `BeautifulSoup` 크롤링 (페이징 처리) |
| KIPRIS Excel | 한국 특허 154건 | raw XML 파싱 (`zipfile` + `ElementTree`) |
| 이력서 (DOCX) | 경력 타임라인, 프로젝트 상세 | `python-docx` 텍스트 추출 |
| KIPRIS API | 직접 검색 시도 | `langchain_kipris_tools` 패키지 (`freeSearchInfo` 엔드포인트) |

## 분류 방법

### 1. 주발명자 vs 공동발명자
- 저자 문자열의 **첫 번째 저자(first author)** 가 최낙초 이름 변형과 일치하면 `주발명자`
- 이름 패턴: `NC CHOI`, `NC Choi`, `N CHOI`, `C Nakcho`, `Nakcho Choi`, `KL Nakcho Choi` 등

### 2. 기술 카테고리 (Google Scholar)
- **Micro LED**: `micro led`, `led chip`, `led display`, `tiling`, `side metal`
- **OLED**: `oled`, `organic light emitting`, `pixel define layer`, `PDL`, `UPC`, `foldable`, `overcoat`, `planarization`, `encapsulation`, `TFE`, `switchable privacy`
- **LCD**: `liquid crystal`, `LCD`, `alignment layer`, `PVA`, `VA mode`
- **세부 카테고리**: 제조공정, TFT/백플레인, 패키징/본딩, 구동/회로, 검사/테스트, 광학/컬러, 플렉서블, 봉지/배리어

### 3. 기술 카테고리 (KIPRIS)
- IPC 코드 기반 자동 분류
  - `G02F` → LCD
  - `H10K` → OLED
  - `H10H` → Micro LED
  - `H10D`, `H01L` → TFT/반도체
  - `G09G` → 구동/회로

### 4. 법적 상태 (KIPRIS)
- `등록`(registered), `공개`(published), `거절`/`취하`/기타

## 시각화 도구

- **Plotly** (`plotly.graph_objects`, `plotly.subplots`)
- `make_subplots`로 3~5행 × 3열 대시보드 구성
- 한글 폰트: `Noto Sans KR` (Google Fonts CDN)
- 영문 폰트: `Inter` (Google Fonts CDN)
- 차트 유형: Indicator gauge, Pie, Stacked Area, Bar (h/v), Heatmap, Table

## 생성된 스크립트

| 스크립트 | 역할 |
|---|---|
| `scrape_scholar.py` | Google Scholar 프로필 크롤링 |
| `scrape_full.py` | 페이징 포함 전체 크롤링 |
| `analyze.py` | 초기 분류 분석 |
| `report_final2.py` | 한글 Google Scholar 보고서 (이력서 반영) |
| `report_en.py` | 영문 Google Scholar 보고서 |
| `parse_excel.py` | KIPRIS Excel raw XML 파싱 |
| `gen_patent_reports.py` | KIPRIS 한글+영문 특허 보고서 |
| `gen_integrated_report.py` | **통합 보고서** (Scholar + KIPRIS) |
| `kipris_search.py` | KIPRIS API 탐색 |
| `fix_kipris.py` | KIPRIS API 파라미터 디버깅 |

## 주요 해결한 문제

1. **OLED 분류 누락**: `Light Emitting Display Device`가 Micro LED로 오분류 → OLED 키워드에 `organic`, `PDL`, `UPC`, `foldable`, `overcoat` 등 삼성디스플레이 특허 전문용어 추가
2. **Excel 인코딩**: openpyxl 스타일시트 버그 → raw XML 파싱 (`zipfile` + `ElementTree`)
3. **KIPRIS API**: `INVALID_REQUEST_PARAMETER_ERROR` → API 파라미터 형식 불일치 (KIPRIS 개발자 포털 확인 필요)
4. **pandas 컬럼명 불일치**: 분석 데이터 구조 변경에 따른 KeyError → 실제 키 확인 후 적응적 처리

## 보고서 HTML 구조

각 보고서는 다음 CSS 클래스로 구성됨:
- `.wrapper` / `.header` — 상단 제목
- `.summary-cards` / `.card` — 요약 통계 카드
- `.insight-box` — 핵심 인사이트
- `.tables-section` / `details` / `summary` — 접이식 테이블
- `.plot-box` — Plotly 차트
- `.disclaimer` — 면책조항
