# Nak Cho Choi (최낙초) — Research Portfolio Analysis

Google Scholar + KIPRIS 특허/논문 AI 분석 및 시각화 보고서 자동 생성 프로젝트

## 📊 프로젝트 개요

삼성디스플레이 수석연구원 **Nak Cho Choi(최낙초)** 의 연구 포트폴리오를
Google Scholar 및 KIPRIS 데이터를 기반으로 AI 분석하여
인터랙티브 시각화 보고서를 생성했습니다.

### 분석 대상

| 구분 | 데이터 소스 | 건수 |
|---|---|---|
| 🇰🇷 한국 특허 | KIPRIS (특허정보원) | **154건** |
| 🇺🇸 미국 특허 | Google Scholar | **93건** |
| 📄 논문 | Google Scholar | **7건** |
| **총 IP 자산** | — | **254건** |

### 연구자 정보

- **이름**: Nak Cho Choi (최낙초)
- **소속**: 삼성디스플레이, 수석연구원
- **연구 분야**: Micro LED, OLED, LCD
- **경력**: 25년+ (2001–현재)
- **h-index**: 14 / i10-index: 22
- **총 인용**: 813회 (Google Scholar)

### 경력 타임라인

| Phase | 기간 | 내용 |
|---|---|---|
| 📺 Phase 1 | 2001–2017 | LCD 시대 — TFT-LCD 기판, 배향, 컬러필터 |
| 💡 Phase 2 | 2017–2022 | OLED 전환 — Black PDL, UPC, Polarizer-free, Foldable |
| 🔬 Phase 3 | 2021–2026.4 | Micro LED + Automotive OLED — tiled display, Switchable Privacy |
| 🛡️ Phase 4 | 2026.5–현재 | 개발품질 — TFT 소자 신뢰성 |

## 🚀 실행 방법

### 1. Google Scholar 데이터 수집
```bash
python scrape_full.py       # 프로필 + 논문/특허 스크래핑
python analyze.py            # 분류 분석 → scholar_analysis.json
```

### 2. KIPRIS 데이터 처리
```bash
python parse_excel.py        # KIPRIS Excel → patent_data.json
```

### 3. 보고서 생성
```bash
# Google Scholar 보고서 (이력서 기반)
python report_final2.py      # 한국어 deepseek_report.html
python report_en.py          # 영어 deepseek_english_report.html

# KIPRIS 특허 보고서
python gen_patent_reports.py # korean_patent_report.html + english_patent_report.html

# 통합 보고서
python gen_integrated_report.py  # integrated_report.html
```

### 요구사항
```
pip install requests beautifulsoup4 pandas plotly lxml python-docx xmltodict stringcase python-dotenv
```

## 📁 프로젝트 구조

```
├── scrape_scholar.py          # Google Scholar 크롤링
├── scrape_full.py             # 전체 페이징 크롤링
├── analyze.py                 # 초기 분류 분석
├── report_final2.py           # 한글 GS 보고서 (이력서 반영)
├── report_en.py               # 영문 GS 보고서
├── parse_excel.py             # KIPRIS Excel 파싱
├── gen_patent_reports.py      # KIPRIS 특허 보고서
├── gen_integrated_report.py   # 🏆 통합 보고서
├── kipris_search.py           # KIPRIS API 실험
├── fix_kipris.py              # API 디버깅
├── explore_kipris.py          # API 엔드포인트 탐색
├── scholar_data.json          # GS 크롤링 원본
├── scholar_analysis.json      # GS 분류 결과
├── patent_data.json           # KIPRIS 파싱 결과
├── resume_20250914.docx       # 이력서 (참고용)
├── SKILL.md                   # 방법론 문서
├── REPORTS.md                 # 보고서 파일 목록
└── README.md                  # 이 파일
```

## 📝 라이선스 / 면책

본 프로젝트는 개인 연구 포트폴리오 분석 목적으로 생성되었으며,
데이터의 정확성은 각 출처(Google Scholar, KIPRIS)에 따라 달라질 수 있습니다.
기술 분류는 AI 기반 키워드 매칭 및 IPC 코드 분석에 의한 추정치입니다.
