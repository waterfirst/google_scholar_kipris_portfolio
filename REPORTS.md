# 📊 보고서 파일 목록

생성일: 2026-08-08

## 주요 보고서 HTML

| 파일명 | 언어 | 내용 | 크기 |
|---|---|---|---|
| **🏆 `integrated_report.html`** | 🇬🇧 English | **통합 보고서** (GS + KIPRIS) | 4.79 MB |
| `deepseek_report.html` | 🇰🇷 한국어 | Google Scholar 분석 (이력서 기반) | 4.75 MB |
| `deepseek_english_report.html` | 🇬🇧 English | Google Scholar analysis (resume-based) | 4.75 MB |
| `korean_patent_report.html` | 🇰🇷 한국어 | KIPRIS 국내 특허 분석 | 4.75 MB |
| `english_patent_report.html` | 🇬🇧 English | KIPRIS Korean patent analysis | 4.75 MB |

## Base64 인코딩 (임베딩/전송용)

| 파일명 | 크기 |
|---|---|
| `integrated_report.b64` | 6.39 MB |
| `deepseek_report.b64` | 6.34 MB |
| `deepseek_english_report.b64` | 6.34 MB |
| `korean_patent_report.b64` | 6.33 MB |
| `english_patent_report.b64` | 6.33 MB |

## 보고서별 구성

### 1. `integrated_report.html` (통합) 🏆

| 차트 | 유형 | 설명 |
|---|---|---|
| Research Impact | Gauge | h-index 14, i10 22, citations 813 |
| Portfolio Composition | Pie | KR 154 + US 93 + Papers 7 |
| Yearly Output (Stacked) | Stacked Area | 연도별 KR+US+Papers 누적 |
| KR Patent Tech Distribution | Bar | LCD 96, OLED 33, Micro LED 10 |
| KR/US/Papers Yearly | Bar ×3 | 각 소스별 연도별 추이 |
| Technology Evolution | Heatmap | LCD→OLED→Micro LED 시계열 |
| Recent 3 Years | Bar | 2024-2026 포트폴리오 |
| Summary | Table | 10개 핵심 지표 |

접이식 테이블:
- 🇰🇷 한국 특허 154건 (출원일자, 상태, 명칭, 번호, IPC)
- 🇺🇸 미국 특허 93건 (연도, 주/공동, 인용, 제목)
- 📄 논문 7건 (연도, 주/공동, 인용, 제목)

### 2. `deepseek_report.html` (Google Scholar, 한글)

| 차트 | 설명 |
|---|---|
| 인용 영향력 지표 | h-index 게이지 |
| 주발명자 vs 공동발명자 | Pie |
| 기술 카테고리 분포 | Bar (LCD/OLED/Micro LED) |
| 연도별 발행 추이 | Stacked Area |
| 주발명자 Top 10 인용 | Bar |
| 기술 진화 히트맵 | Heatmap |
| 최근 활동 (2024-2026) | Bar |
| 핵심 인사이트 | 4단계 경력 타임라인 |

### 3. `deepseek_english_report.html` (Google Scholar, English)

동일 구성, 영문 레이블

### 4. `korean_patent_report.html` (KIPRIS, 한글)

| 차트 | 설명 |
|---|---|
| 법적 상태 분포 | Pie (등록/공개/기타) |
| 연도별 출원 추이 | Line |
| IPC 기술 분류 | Bar |
| 기술 분야별 출원 | Heatmap |
| 상위 IPC 클래스 | Bar |
| 최근 출원 (2022-2026) | Bar |

### 5. `english_patent_report.html` (KIPRIS, English)

동일 구성, 영문 레이블

## 분석 요약

### 통합 수치

| 지표 | 값 |
|---|---|
| 총 IP 자산 | **254건** |
| 한국 특허 | 154건 (등록 55건, 주발명자 70건) |
| 미국 특허 | 93건 (주발명자 45건) |
| 논문 | 7건 (주발명자 4건) |
| h-index | 14 |
| 총 인용 | 813회 |

### 기술 분류 (한국 특허, IPC 기준)

| 기술 | 건수 | IPC |
|---|---|---|
| LCD | 96건 | G02F |
| OLED | 33건 | H10K |
| Micro LED | 10건 | H10H |
| TFT/반도체 | 6건 | H10D, H01L |
| 구동/회로 | 3건 | G09G |
| 기타 | 6건 | — |

## 참고: KIPRIS API 상태

- `langchain_kipris_tools` 패키지 (`D:\nakcho\deppseek\langchain_kipris_tools`)
- `freeSearchInfo` 엔드포인트 호출 시도 → `INVALID_REQUEST_PARAMETER_ERROR`
- API 키: `api.txt.txt` 참조
- Excel 내보내기 데이터(154건)로 대체하여 보고서 생성 완료
- KIPRIS 개발자 포털에서 API 파라미터 형식 확인 필요
