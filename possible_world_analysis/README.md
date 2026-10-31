# 《시곡 — 한 사발의 밥》 역사적 가능세계 계산 및 사료 검증 시스템

정조 연간 황해도 백천(배천) **조재항 옥사**를 바탕으로 한 역사영화 《시곡》의 가능세계를 계산·비교한다. 목표는 그럴듯한 줄거리 생성이 아니라, **1차 사료·학술연구·제도·이론·극중 창작을 분리한 채** 윤씨 살해와 조재항 무고가 동시에 성립하는 사건 구조를 논리적으로 도출하고, 각 구조에 필요한 가정·근거·변경 비용을 보이는 것이다.

> **이 폴더의 결과는 '역사적으로 그랬을 확률'이 아니다.** SAT는 모순이 없다는 뜻일 뿐이다. 확률·가중 점수는 쓰지 않았다.
> 위키백과·나무위키 등 위키 계열 자료는 사용하지 않았다. 원본 PDF·시놉시스는 수정하지 않았다.

## 0. 이번 실행(2026-10-31)의 자료 접근 상태

| 자료 | 접근 | 결과 |
|---|---|---|
| 《시곡》 PDF (기획의도·인물소개·시놉시스 v4·사료 부록) | 사용자 업로드본 + Google Drive 동일본 | **읽음**. 로컬 사본 [`source_local/`](source_local/), 페이지별 텍스트 [`source_extracts/sigok_pdf_pages/`](source_extracts/sigok_pdf_pages/) |
| 사용자 연구 데이터셋(CORE_EVENTS·CORE_CASE_CLAIMS·SOURCES), C안 고증보고서, 3대 연구과제 계획서, 3사례 비교 보고서 | Google Drive | **읽음**. 스냅숏 [`source_extracts/`](source_extracts/) |
| 국사편찬위원회 조선왕조실록·한국사DB·승정원일기, RISS·DBpia, doi.org | 웹 | **차단** — 이 세션의 네트워크 정책이 접속을 거부(프록시 CONNECT 403). 38개 링크 모두 `NETWORK_BLOCKED`. **자료가 없다는 뜻이 아니다.** |

따라서 한문 원문 구절은 **사용자 데이터셋의 전사본**으로만 확인했고(`간접 확인`), 원문 대조는 [`10_evidence_gaps.md`](10_evidence_gaps.md)의 과제로 남겼다. 이세영(2009)은 본문·초록 모두 열람하지 못했다. 접속이 허용되면 `python tools/check_links.py --write`로 링크 상태를 갱신하고 검증 과제를 진행한다.

## 1. 핵심 결과

| 질문 | 결과 | 문서 |
|---|---|---|
| 《심리록》(1780 성옥)만 채택한 역사 고정 모드 | **SAT** (윤씨 사망 ≤ 1780 L5 24경) | [04](04_historical_conflicts.md) |
| 《정조실록》 회고(1781)만 채택한 역사 고정 모드 | **SAT** (성옥 1781 L1–L3) | [04](04_historical_conflicts.md) |
| 두 사료를 동시에 절대 사실로 고정 | **UNSAT** — 이렇게 고정해서는 안 됨 | [04](04_historical_conflicts.md) |
| 극중 필수 순서(부임<포폄<사망<성옥) + 《심리록》 연대 | **UNSAT** — MUS: 극중 순서·1780 6월 성옥·약 40일·조상진 여름 부임·6/12월 포폄. 하나만 바꾸면 성립 | [04 §3](04_historical_conflicts.md) |
| 시놉시스 v4 날짜(사망 1780 L4 하순, 조상진 L6 부임) + 극중 필수 순서 | **UNSAT** — 시놉시스와 새 필수 조건이 서로 충돌 | [04 §4](04_historical_conflicts.md) |
| MODE F 최소 사료 연대 변경 | **1개**: 1780 6월 성옥 대신 실록 회고 1781 채택(격쟁·판부 날짜 유지 가능) | [04 §6](04_historical_conflicts.md) |
| 시놉시스 결말 압축까지 유지 | 앵커 **6개** 변경, 성옥이 1780 L7–L12로 밀려 두 사료 모두와 불일치 | [04 §6.1](04_historical_conflicts.md) |
| 구별되는 성립 인과구조 | 4,320개 중 대표 10개, 파레토 비지배 W03·W05·W07·W09·W10 | [06](06_world_comparison.md) |
| 반사실 10문항 | 예: 이가원이 살해범을 몰라도 무고는 성립(Q9); 복검이 바로잡으면 장기 구금 불가(Q10) | [07](07_counterfactual_analysis.md) |

**최종 연구보고서(§19 A–E 답변): [`12_final_research_report.md`](12_final_research_report.md)**

## 2. 파일 안내

| 파일 | 내용 |
|---|---|
| [`README.md`](README.md) | 목적·방법·APA 참고문헌·근거 추적표·변수 정의 |
| [`sources.yaml`](sources.yaml) | 참고문헌의 구조화된 서지·URL·검증 상태(단일 원천) |
| [`01_claim_registry.csv`](01_claim_registry.csv) | 개별 주장 77건: 원문·번역 분리, 주장 유형, 검증 상태, 사건일/편찬일 분리 |
| [`02_variables.yaml`](02_variables.yaml) | 변수 103개(T·E·A·S·F·M·J): 정의·값·층위·근거 |
| [`03_constraints.py`](03_constraints.py) | CSP·시간제약·구조적 인과모형·MUS/MCS·가능세계·반사실 계산기 |
| [`04_historical_conflicts.md`](04_historical_conflicts.md) | 역사적 사건과 극중 제약의 충돌 |
| [`05_possible_worlds.csv`](05_possible_worlds.csv) | 대표 가능세계(자동 생성) |
| [`06_world_comparison.md`](06_world_comparison.md) | 대표 가능세계 비교·파레토(자동 생성) |
| [`07_counterfactual_analysis.md`](07_counterfactual_analysis.md) | 반사실 분석 10문항(자동 생성) |
| [`08_causal_graph.mmd`](08_causal_graph.mmd) | 전체 인과관계(자동 생성, 간선 유형 구분) |
| [`09_family_systems.mmd`](09_family_systems.mmd) | 가족관계·삼각관계 |
| [`10_evidence_gaps.md`](10_evidence_gaps.md) | 추가 원문 검증 과제(§18 최우선 과제 포함) |
| [`11_scenario_implications.md`](11_scenario_implications.md) | 영화적 활용과 작가가 결정할 설정 |
| [`12_final_research_report.md`](12_final_research_report.md) | 최종 연구보고서 |
| [`results/`](results/) | `csp_results.json`·[`csp_report.md`](results/csp_report.md)·`worlds.json`·`counterfactuals.json`·`economic_scenarios.json`·`link_check.json` |
| [`scenario/scenario_parameters.yaml`](scenario/scenario_parameters.yaml) | **가상** 곡식 수량(가상 단위). 역사 데이터와 분리 |
| [`source_local/`](source_local/) · [`source_extracts/`](source_extracts/) | 원본 PDF 사본(읽기 전용, SHA-256)·입력자료 스냅숏 |
| [`tools/`](tools/) | 링크 검사·주장/변수/README 생성기·보고서 생성기 |
| [`tests/`](tests/) | 제약충족·출처 연결·시간 계산·README 일치 테스트 |

## 3. 실행 방법

```bash
pip install z3-solver networkx pyyaml pytest
```

```bash
cd possible_world_analysis && python tools/build_claim_registry.py && python tools/build_variables.py
```

```bash
cd possible_world_analysis && python 03_constraints.py
```

```bash
cd possible_world_analysis && python tools/check_links.py --write && python tools/build_readme.py
```

```bash
cd possible_world_analysis && python -m pytest -q tests
```

`03_constraints.py`는 약 1분 걸린다. 링크 검사는 네트워크가 막혀 있으면 모든 항목을 `NETWORK_BLOCKED`로 기록한다(자료 부재로 기록하지 않음).

## 4. 방법 개요

- **층위 분리**: 모든 제약은 `STR`(모형 구조)·`INST`(제도)·`HIST_TEN`(인사 연표)·`HIST_T`(사료 연대)·`HIST_C`(사료 인과 사실)·`FILM_REQ`(극중 필수)·`FILM_SYN`(시놉시스 선택)·`SCM`(구조방정식)으로 표시되고 근거 주장 ID를 가진다.
- **시간**: 음력 서수 인덱스 \(L = ((y-1780)\cdot 12 + (m-1))\cdot 30 + (d-1)\). 양력 변환이 아니며 윤달을 반영하지 않는다(Dechter et al., 1991의 시간제약네트워크를 단순 선후·구간 제약으로 사용; Allen 관계는 불필요해 쓰지 않음).
- **판정**: z3(de Moura & Bjørner, 2008). UNSAT이면 MUS(최소 충돌집합)와 MCS(최소 수정집합)를 MARCO 방식(Liffiton et al., 2016)으로 열거한다.
- **인과**: 22개 구조방정식. 간선 유형: 사료에 나타난 관계 / 이론이 제안한 인과 / 극중 추가 가정 / 시간 선후(인과 아님). 개입은 do 연산(식 절단), 관찰은 조건 추가로 구분한다(Pearl, 2009).
- **세계 비교**: 가중치 없이 '미확인 가정 수↓·연대 변경 수↓·각 설명 기준 충족↑'의 파레토 비지배만 판정한다.

<a id="references"></a>
## A. References — APA 7판 참고문헌

고문헌은 APA 응용 형식: 문헌명을 저자 자리에 두고, 괄호 안 날짜는 **기사가 다루는 사건의 음력 날짜**이며 편찬 시기와 다르다. 편찬 시기를 확인하지 못한 경우 "확인 필요"로 남겼다. 각 항목 아래 작은 글씨는 이번 실행의 URL 상태와 원문 검증 수준이다 — **URL 확인과 원문 검증은 별개**다. 데이터 원천: [`sources.yaml`](sources.yaml).

<!-- BEGIN:REFERENCES -->
### A-1. 1차 사료

<a id="src-SIM"></a>**[SIM]** 《심리록》. (편찬 시기 확인 필요). [제2권 황해도, 백천 조재항옥(白川 趙載恒獄)](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [사건 범위: 1780(경자)~1783년]. 국사편찬위원회 한국사데이터베이스 조선시대 법령자료.  
<sub>사건 날짜: 1780(경자) L6 성옥 ~ 1782 L7 격쟁·판부 (기사 내 복수 시점) · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 원문 구절은 사용자 데이터셋 전사본으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/drive_CORE_EVENTS.csv`, `source_extracts/drive_CORE_CASE_CLAIMS.csv`</sub>

<a id="src-SIL1783"></a>**[SIL1783]** 《정조실록》. (1783년 음력 6월 3일 기사; 편찬 시기 확인 필요). [배천군 살해 죄인 조재항을 방면하고 계략을 꾸민 이가원을 귀양보내다](https://sillok.history.go.kr/id/kva_10706003_004). 국사편찬위원회 조선왕조실록.  
<sub>사건 날짜: 1783 L6 3 (판부); 기사 내 회고: 辛丑(1781), 辛丑春 審理 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 원문 구절은 사용자 데이터셋 전사본으로만 확인 — **원문 검증 미완료** · 대체 링크: <https://sillok.history.go.kr/id/wva_10706003_004> · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/drive_CORE_CASE_CLAIMS.csv`, `source_extracts/drive_other_documents.md#D3`</sub>

<a id="src-CHUG"></a>**[CHUG]** 《추관지》. (편찬 시기 확인 필요). [권2 상복부·윤상·살처, 중보 — 조재항 옥안](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080). 국사편찬위원회 한국사데이터베이스 조선시대 법령자료.  
<sub>사건 날짜: 1780~1783 (개별 시점 미상) · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 대체 링크: <https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080>, <https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200_0020_0020_0050_0080_0080> · 링크 불일치: 사용자 자료 3종이 서로 다른 levelId를 사용(PDF: ..._0080_0080 / SOURCES.csv: ..._0080 / C안 보고서: jlawb_200_ 'r' 없음). 어느 것이 개별 기사인지 미검증. · 확인 못 한 서지 요소: 편찬연도, 확정 levelId · 로컬 위치: `source_extracts/sigok_pdf_pages/p11.txt`, `source_extracts/drive_other_documents.md#D1`</sub>

<a id="src-BIB1781"></a>**[BIB1781]** 《비변사등록》. (1781년 음력 9월 29일 기사). [황해감사 조상진의 도내 농황 분등 장계 관련 논의](https://db.history.go.kr/item/compareViewer.do?levelId=bb_163r_001_03_0590). 국사편찬위원회 한국사데이터베이스.  
<sub>사건 날짜: 1781 L9 29 · 편찬·작성 시기: 확인 필요 (등록류는 당대 작성으로 알려져 있으나 이번 실행 미검증) · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬 시기 · 로컬 위치: `source_extracts/sigok_pdf_pages/p10.txt`</sub>

<a id="src-SIL178204"></a>**[SIL178204]** 《정조실록》. (1782년 음력 4월 23일 기사; 편찬 시기 확인 필요). [황해감사 이경양의 농황 보고 부실을 질책하고 월봉 1등을 명하다](https://sillok.history.go.kr/id/kva_10604023_001). 국사편찬위원회 조선왕조실록.  
<sub>사건 날짜: 1782 L4 23 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 원문 구절은 사용자 데이터셋 전사본으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도, 기사 공식 제목 · 로컬 위치: `source_extracts/drive_CORE_EVENTS.csv`</sub>

<a id="src-SIL1783M"></a>**[SIL1783M]** 《정조실록》. (1783년 음력 5월 9일 기사; 편찬 시기 확인 필요). [조상진을 성균관 대사성으로 삼다](https://sillok.history.go.kr/id/kva_10705009_002). 국사편찬위원회 조선왕조실록.  
<sub>사건 날짜: 1783 L5 9 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/sigok_pdf_pages/p11.txt`</sub>

<a id="src-SJW1780"></a>**[SJW1780]** 《승정원일기》. (1780년 음력 3월 14일 기사). [정조 4년 3월 14일 기사(이득준 평산부사 임명 관련으로 지목됨 — 내용 미검증)](https://sjw.history.go.kr/id/SJW-G04030140-02600). 국사편찬위원회 승정원일기.  
<sub>사건 날짜: 1780 L3 14 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 미검증 — **검증 미완료** · 확인 못 한 서지 요소: 편찬 시기, 기사 제목, 이득준 관련 여부 · 로컬 위치: `source_extracts/sigok_pdf_pages/p03.txt`, `source_extracts/drive_other_documents.md#D2`</sub>

<a id="src-GYDJ_POPHYEOM"></a>**[GYDJ_POPHYEOM]** 《경국대전》. (편찬 시기 확인 필요). *이전(吏典) 포폄(褒貶)조* [원문 링크 미확보].  
<sub>사건 날짜: 해당 없음(법전 조문) · 편찬·작성 시기: 확인 필요 · 원문 링크 없음 (2026-10-31T15:47:40Z) · 미검증 — **검증 미완료** · 링크 비어 있는 이유: 개별 조문 링크를 이번 실행에서 찾거나 열 수 없었음(네트워크 차단). '정기 포폄은 음력 6월·12월'은 사용자 지시문의 진술이며 원문 미대조. · 확인 못 한 서지 요소: 편찬연도, URL, 조문 원문</sub>

<a id="src-SIL1780J"></a>**[SIL1780J]** 《정조실록》. (1780년 음력 1월 1일 기사; 편찬 시기 확인 필요). [팔도와 양도에 내린 권농 윤음](https://sillok.history.go.kr/id/kva_10401001_002). 국사편찬위원회 조선왕조실록.  
<sub>사건 날짜: 1780 L1 1 (1779년 수확 회복 언급) · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/drive_other_documents.md#D1`</sub>

<a id="src-BIB178206"></a>**[BIB178206]** 《비변사등록》. (1782년 음력 6월 14일 기사). [배천 향곡의 3분의 1 가분 요청과 불허 논의](https://db.history.go.kr/item/compareViewer.do?levelId=bb_164_001_06_0220). 국사편찬위원회 한국사데이터베이스.  
<sub>사건 날짜: 1782 L6 14 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 원문 구절은 사용자 데이터셋 전사본으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬 시기 · 로컬 위치: `source_extracts/drive_CORE_EVENTS.csv`</sub>

<a id="src-BIB178207"></a>**[BIB178207]** 《비변사등록》. (1782년 음력 7월 4일 기사). [정창순이 배천의 향곡 가분을 다시 청하다](https://db.history.go.kr/common/compareViewer.do?levelId=bb_165_001_01_0070&type=joseon). 국사편찬위원회 한국사데이터베이스.  
<sub>사건 날짜: 1782 L7 4 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 원문 구절은 사용자 데이터셋 전사본으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬 시기 · 로컬 위치: `source_extracts/drive_CORE_EVENTS.csv`</sub>

<a id="src-SJW1782"></a>**[SJW1782]** 《승정원일기》. (1782년 음력 10월 6일 기사). [황해감사 황승원의 연안·배천 진전·포락전 보고](https://sjw.history.go.kr/search/inspectionDayList.do?wday=17821006L0). 국사편찬위원회 승정원일기.  
<sub>사건 날짜: 1782 L10 6 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬 시기, 개별 기사 링크 · 로컬 위치: `source_extracts/sigok_pdf_pages/p10.txt`</sub>

<a id="src-SIL1783A"></a>**[SIL1783A]** 《정조실록》. (1783년 음력 1월 18일 기사; 편찬 시기 확인 필요). [부민의 진휼을 권장하되 수령의 권분 강요를 경계하다](https://sillok.history.go.kr/id/kva_10701018_004). 국사편찬위원회 조선왕조실록.  
<sub>사건 날짜: 1783 L1 18 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/sigok_pdf_pages/p11.txt`</sub>

<a id="src-SIL1783O"></a>**[SIL1783O]** 《정조실록》. (1783년 음력 10월 29일 기사; 편찬 시기 확인 필요). [각도 어사 사목과 권분 강제징수 감찰](https://sillok.history.go.kr/id/kva_10710029_003). 국사편찬위원회 조선왕조실록.  
<sub>사건 날짜: 1783 L10 29 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/drive_other_documents.md#D1`</sub>

<a id="src-BIB1727"></a>**[BIB1727]** 《비변사등록》. (1727년 음력 12월 14일 기사). [첩문을 이용하여 곡물을 모으는 문제에 대한 논의](https://db.history.go.kr/item/compareViewer.do?levelId=bb_082_001_06_0310). 국사편찬위원회 한국사데이터베이스.  
<sub>사건 날짜: 1727 L12 14 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬 시기 · 로컬 위치: `source_extracts/drive_other_documents.md#D1`</sub>

<a id="src-BIB1731"></a>**[BIB1731]** 《비변사등록》. (1731년 음력 12월 9일 기사). [정언 송징계가 권분의 폐단을 논한 상소](https://db.history.go.kr/common/compareViewer.do?levelId=bb_090r_001_06_0190&type=joseon). 국사편찬위원회 한국사데이터베이스.  
<sub>사건 날짜: 1731 L12 9 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬 시기 · 로컬 위치: `source_extracts/sigok_pdf_pages/p10.txt`</sub>

<a id="src-BIB1741"></a>**[BIB1741]** 《비변사등록》. (1741년 음력 11월 21일 기사). [북도 부민 권분 논상 절목과 별단](https://db.history.go.kr/common/compareViewer.do?levelId=bb_109_001_05_0430&type=joseon). 국사편찬위원회 한국사데이터베이스.  
<sub>사건 날짜: 1741 L11 21 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬 시기 · 로컬 위치: `source_extracts/sigok_pdf_pages/p10.txt`</sub>

<a id="src-SIL1793"></a>**[SIL1793]** 《정조실록》. (1793년 음력 9월 16일 기사; 편찬 시기 확인 필요). [연안 등 고을에 대한 윤음](https://sillok.history.go.kr/id/kva_11709016_003). 국사편찬위원회 조선왕조실록.  
<sub>사건 날짜: 1793 L9 16 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/drive_other_documents.md#D1`</sub>

<a id="src-HOGU"></a>**[HOGU]** 《호구총수》. (1789). [황해도 백천군 호구](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_590_0050_0160). 국사편찬위원회 한국사데이터베이스 조선시대 법령자료.  
<sub>사건 날짜: 1789 (조사일 미상) · 편찬·작성 시기: 1789 (사용자 데이터셋 표기; 이번 실행 미검증) · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 원문 구절은 사용자 데이터셋 전사본으로만 확인 — **원문 검증 미완료** · 로컬 위치: `source_extracts/drive_SOURCES.csv`</sub>

<a id="src-YEO"></a>**[YEO]** 《여지도서》. (18세기 중엽 편찬 사업; 백천 항목 기재 시점 확인 필요). [하권, 황해도·백천 (단묘·강역)](https://db.history.go.kr/id/sa_037_0010_0210_0120). 국사편찬위원회 한국사료총서.  
<sub>사건 날짜: 1780 이전(정확 시점 미상) · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 대체 링크: <https://db.history.go.kr/diachronic/level.do?levelId=sa_037_0010_0210_0010> · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/sigok_pdf_pages/p12.txt`</sub>

<a id="src-YJSIL1742"></a>**[YJSIL1742]** 《영조실록》. (1742년 음력 1월 6일 기사; 편찬 시기 확인 필요). [이천보를 옥천 안핵어사로 삼다](https://sillok.history.go.kr/id/wua_11801006_001). 국사편찬위원회 조선왕조실록.  
<sub>사건 날짜: 1742 L1 6 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/sigok_pdf_pages/p11.txt`</sub>

<a id="src-TGJS"></a>**[TGJS]** 《특교정식》. (1783년 음력 7월 8일 전거; 편찬 시기 확인 필요). [사계정식](https://db.history.go.kr/joseon/item/level.do?allViewYn=Y&levelId=jlawb_120_0020_0290). 국사편찬위원회 조선시대 법령자료.  
<sub>사건 날짜: 1783 L7 8 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/sigok_pdf_pages/p12.txt`</sub>

<a id="src-DMYJ_MOSAL"></a>**[DMYJ_MOSAL]** 《대명률직해》. (n.d.). [권19 형률·인명, 제305조 모살인](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_170_0190_0010_0010). 국사편찬위원회 조선시대 법령자료.  
<sub>사건 날짜: 해당 없음(법전 조문) · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/sigok_pdf_pages/p09.txt`</sub>

<a id="src-DMYJ_MUGO"></a>**[DMYJ_MUGO]** 《대명률직해》. (n.d.). [권22 형률·소송, 제359조 무고](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_170_0220_0010_0050). 국사편찬위원회 조선시대 법령자료.  
<sub>사건 날짜: 해당 없음(법전 조문) · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 편찬연도 · 로컬 위치: `source_extracts/sigok_pdf_pages/p10.txt`</sub>

### A-2. 학술연구

<a id="src-LEE2009"></a>**[LEE2009]** 이세영. (2009). [조선후기의 勸分과 富民의 실태](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE10953875). *역사문화연구, 34*, 157–264.  
<sub>사건 날짜: 해당 없음(연구 문헌; 대상 시기 조선 후기) · 편찬·작성 시기: 2009 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 미검증 — **검증 미완료** · 대체 링크: <https://m.riss.kr/search/detail/DetailView.do?control_no=084cfac90c32987bffe0bdc3ef48d419&p_mat_type=1a0202e37d52c72d> · 확인 못 한 서지 요소: 호(번호), DOI</sub>

<a id="src-LEEJW2015"></a>**[LEEJW2015]** 이종원. (2015). [희생양 메커니즘과 폭력의 윤리적 문제: 르네 지라르의 모방이론과 희생양 메커니즘을 중심으로](https://doi.org/10.33156/philos.2015.40..010). *철학탐구, 40*, 273–301. https://doi.org/10.33156/philos.2015.40..010  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 2015 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료**</sub>

<a id="src-NIKH_NH36"></a>**[NIKH_NH36]** 국사편찬위원회. (n.d.). [1) 민중세계의 각성](https://contents.history.go.kr/mobile/nh/view.do?levelId=nh_036_0030_0010_0010). In *신편 한국사: 36. 조선 후기 민중사회의 성장*. 우리역사넷.  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 확인 필요 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료** · 확인 못 한 서지 요소: 발행연도</sub>

<a id="src-ROTHSCHILD2012"></a>**[ROTHSCHILD2012]** Rothschild, Z. K., Landau, M. J., Sullivan, D., & Keefer, L. A. (2012). [A dual-motive model of scapegoating: Displacing blame to reduce guilt or increase control](https://doi.org/10.1037/a0027413). *Journal of Personality and Social Psychology, 102*(6), 1148–1163.  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 2012 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 서지만 확인(본문 미열람) — **검증 미완료**</sub>

<a id="src-JEDWAB2019"></a>**[JEDWAB2019]** Jedwab, R., Johnson, N. D., & Koyama, M. (2019). [Negative shocks and mass persecutions: Evidence from the Black Death](https://doi.org/10.1007/s10887-019-09167-1). *Journal of Economic Growth, 24*(4), 345–395.  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 2019 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 서지만 확인(본문 미열람) — **검증 미완료**</sub>

### A-3. 이론·제도·방법 해설

<a id="src-GIRARD1986"></a>**[GIRARD1986]** Girard, R. (1986). *The scapegoat* (Y. Freccero, Trans.). Johns Hopkins University Press. (Original work published 1982)  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 1982(원저) / 1986(영역) · 원문 링크 없음 (2026-10-31T15:47:40Z) · 서지만 확인(본문 미열람) — **검증 미완료** · 링크 비어 있는 이유: 단행본. 공개 원문 링크 없음. 서지는 작성자 지식에 근거하며 이번 실행에서 미검증. · 확인 못 한 서지 요소: URL</sub>

<a id="src-BOWEN1978"></a>**[BOWEN1978]** Bowen, M. (1978). *Family therapy in clinical practice*. Jason Aronson.  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 1978 · 원문 링크 없음 (2026-10-31T15:47:40Z) · 서지만 확인(본문 미열람) — **검증 미완료** · 링크 비어 있는 이유: 단행본. 공개 원문 링크 없음. 서지는 작성자 지식에 근거하며 이번 실행에서 미검증. · 확인 못 한 서지 요소: URL</sub>

<a id="src-KERR1988"></a>**[KERR1988]** Kerr, M. E., & Bowen, M. (1988). *Family evaluation: An approach based on Bowen theory*. W. W. Norton.  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 1988 · 원문 링크 없음 (2026-10-31T15:47:40Z) · 서지만 확인(본문 미열람) — **검증 미완료** · 링크 비어 있는 이유: 단행본. 공개 원문 링크 없음. 서지는 작성자 지식에 근거하며 이번 실행에서 미검증. · 확인 못 한 서지 요소: URL</sub>

<a id="src-FAO2008"></a>**[FAO2008]** Food and Agriculture Organization of the United Nations. (2008). [An introduction to the basic concepts of food security](https://www.fao.org/agrifood-economics/publications/detail/en/c/122386/) [Guide].  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 2008 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 사용자 문서의 요약으로만 확인 — **원문 검증 미완료**</sub>

<a id="src-ALLEN1983"></a>**[ALLEN1983]** Allen, J. F. (1983). [Maintaining knowledge about temporal intervals](https://doi.org/10.1145/182.358434). *Communications of the ACM, 26*(11), 832–843.  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 1983 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 서지만 확인(본문 미열람) — **검증 미완료**</sub>

<a id="src-DECHTER1991"></a>**[DECHTER1991]** Dechter, R., Meiri, I., & Pearl, J. (1991). [Temporal constraint networks](https://doi.org/10.1016/0004-3702(91)90006-6). *Artificial Intelligence, 49*(1–3), 61–95.  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 1991 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 서지만 확인(본문 미열람) — **검증 미완료**</sub>

<a id="src-DEMOURA2008"></a>**[DEMOURA2008]** de Moura, L., & Bjørner, N. (2008). [Z3: An efficient SMT solver](https://doi.org/10.1007/978-3-540-78800-3_24). In C. R. Ramakrishnan & J. Rehof (Eds.), *Tools and algorithms for the construction and analysis of systems* (Lecture Notes in Computer Science, Vol. 4963, pp. 337–340). Springer.  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 2008 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 서지만 확인(본문 미열람) — **검증 미완료**</sub>

<a id="src-LIFFITON2016"></a>**[LIFFITON2016]** Liffiton, M. H., Previti, A., Malik, A., & Marques-Silva, J. (2016). [Fast, flexible MUS enumeration](https://doi.org/10.1007/s10601-015-9183-0). *Constraints, 21*(2), 223–250.  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 2016 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 서지만 확인(본문 미열람) — **검증 미완료**</sub>

<a id="src-PEARL2009"></a>**[PEARL2009]** Pearl, J. (2009). [Causality: Models, reasoning, and inference](https://doi.org/10.1017/CBO9780511803161) (2nd ed.). Cambridge University Press.  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 2009 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 서지만 확인(본문 미열람) — **검증 미완료**</sub>

### A-4. 프로젝트 내부 자료 (증거 아님 — 추적용)

<a id="src-SIGOK_PDF"></a>**[SIGOK_PDF]** 《시곡 — 한 사발의 밥》 제작팀. (2026). [시곡_인물소개_이득준_출생정보_검증_최종.pdf](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) [미간행 기획 문서, 12쪽].  
<sub>사건 날짜: 해당 없음(창작 문서) · 편찬·작성 시기: 2026-10-30 (Drive 수정 시각) · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 원문(본문) 직접 확인 · 로컬 위치: `source_local/시곡_인물소개_이득준_출생정보_검증_최종.pdf`</sub>

<a id="src-SIGOK_CREPORT"></a>**[SIGOK_CREPORT]** 《시곡 — 한 사발의 밥》 제작팀. (2026). [배천군의 곡물 분급 제약과 권분 압박의 경제적 구조 (C안 고증·서사 설계 보고서)](https://drive.google.com/file/d/1ErIYuXcU-98y2GWldDtUKc3D8Ti9HOp8/view) [미간행 연구 보고서].  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 2026-10-31 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 원문(본문) 직접 확인 · 로컬 위치: `source_extracts/drive_other_documents.md#D1`</sub>

<a id="src-SIGOK_DATASET"></a>**[SIGOK_DATASET]** 《시곡 — 한 사발의 밥》 제작팀. (2026). [CORE_EVENTS.csv · CORE_CASE_CLAIMS.csv · SOURCES.csv](https://drive.google.com/file/d/1JgnSa9omaxrgCm1f9ksC1FVLMKeKhopE/view) [미간행 데이터셋].  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 2026-10-30 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 원문(본문) 직접 확인 · 로컬 위치: `source_extracts/drive_CORE_EVENTS.csv`</sub>

<a id="src-SIGOK_3CASE"></a>**[SIGOK_3CASE]** 《시곡》 제작팀. (2026). [정조대 형사절차의 독립적 재검증 사례 비교](https://drive.google.com/file/d/1fm79ThcInNPsOcnumEG_1vTTxA-UztgV/view) [미간행 연구 보고서].  
<sub>사건 날짜: 해당 없음 · 편찬·작성 시기: 2026-10-02 · URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) (2026-10-31T15:47:40Z) · 원문(본문) 직접 확인 · 로컬 위치: `source_extracts/drive_other_documents.md#D3`</sub>
<!-- END:REFERENCES -->

<a id="evidence-map"></a>
## B. Evidence Map — 변수별 근거 추적표

변수 ID를 누르면 아래 변수 정의로, 근거 문헌 ID를 누르면 위 참고문헌으로 이동한다. '원문 링크'의 ↗는 해당 변수의 주장(01_claim_registry.csv)과 출처에 연결된 개별 기사 링크다. **근거 유형이 '극중 설정/가설'이거나 검증 상태가 '미입증'인 변수는 역사적 사실이 아니다.** 비교·후대 맥락으로만 쓰인 자료는 "(비교·후대 맥락 포함)"으로 표시했고, 1780년 배천의 관측 근거로 쓰지 않았다.

<!-- BEGIN:EVIDENCE_MAP -->
| 변수 ID | 변수 또는 주장 | 근거 문헌 | 원문 링크 | 근거 유형 | 검증 상태 |
|---|---|---|---|---|---|
| [T1](#var-T1) | 권중립의 백천군수 재임 구간 | [SIM](#src-SIM) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) | 1차 사료 | 미확인 |
| [T2](#var-T2) | 조상진의 황해감사 재임 구간 | [SIGOK_PDF](#src-SIGOK_PDF), [BIB1781](#src-BIB1781), [SIL1783M](#src-SIL1783M), [SIL1783](#src-SIL1783) | [↗1](https://db.history.go.kr/item/compareViewer.do?levelId=bb_163r_001_03_0590) [↗2](https://sillok.history.go.kr/id/kva_10705009_002) [↗3](https://sillok.history.go.kr/id/kva_10706003_004) [↗4](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 1차 사료 | 간접 확인 |
| [T3](#var-T3) | 이경양의 황해감사 부임 및 재임 | [SIL178204](#src-SIL178204) | [↗1](https://sillok.history.go.kr/id/kva_10604023_001) | 1차 사료 | 간접 확인 |
| [T4](#var-T4) | 권중립·조상진 재임 중첩 여부 | [SIM](#src-SIM), [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [↗2](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 모형 추론 | 미확인 |
| [T5](#var-T5) | 권중립의 포폄 시점 | [GYDJ_POPHYEOM](#src-GYDJ_POPHYEOM) | 없음 | 제도 해설 | 미확인 |
| [T6](#var-T6) | 포폄의 평가자 | [GYDJ_POPHYEOM](#src-GYDJ_POPHYEOM) | 없음 | 극중 설정 | 미확인 |
| [T7](#var-T7) | 권중립의 포폄 등급 | 없음 | 없음 | 극중 가설 | 미확인 |
| [T8](#var-T8) | 윤씨 사망 시점 | [SIM](#src-SIM), [SIL1783](#src-SIL1783), [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [↗2](https://sillok.history.go.kr/id/kva_10706003_004) [↗3](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 1차 사료 | 사료 간 충돌 |
| [T9](#var-T9) | 윤씨 매장 시점 | [CHUG](#src-CHUG), [SIM](#src-SIM) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) [↗2](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) | 1차 사료 | 간접 확인 |
| [T10](#var-T10) | 이가원의 금전 요구 시점 | [CHUG](#src-CHUG) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) | 1차 사료 | 간접 확인 |
| [T11](#var-T11) | 농요 제작·유포 시점 | [SIL1783](#src-SIL1783), [CHUG](#src-CHUG) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) [↗2](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) | 1차 사료 | 간접 확인 |
| [T12](#var-T12) | 조환 사주 시점 | [CHUG](#src-CHUG) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) | 1차 사료 | 간접 확인 |
| [T13](#var-T13) | 공식 고발 시점 | [SIM](#src-SIM), [CHUG](#src-CHUG), [SIL1783](#src-SIL1783) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [↗2](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) [↗3](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [T14](#var-T14) | 권중립 초검 시점 | [SIM](#src-SIM) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) | 1차 사료 | 간접 확인 |
| [T15](#var-T15) | 이우배 복검 시점 | [SIM](#src-SIM) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) | 1차 사료 | 간접 확인 |
| [T16](#var-T16) | 옥사 성립 시점 | [SIM](#src-SIM), [SIL1783](#src-SIL1783) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [↗2](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 사료 간 충돌 |
| [T17](#var-T17) | 조재항 구금 시작·종료 | [SIL1783](#src-SIL1783) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [T18](#var-T18) | 정조의 재조사 명령 | [SIL1783](#src-SIL1783), [SIM](#src-SIM), [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) [↗2](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [↗3](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 1차 사료 | 사료 간 충돌 |
| [T19](#var-T19) | 조재정 격쟁 | [SIM](#src-SIM) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [↗2](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 1차 사료 | 간접 확인 |
| [T20](#var-T20) | 최종 판부 | [SIL1783](#src-SIL1783) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [E1](#var-E1) | 1780~1781년 배천의 농업 상황 | [SIL1780J](#src-SIL1780J), [BIB178207](#src-BIB178207), [SIL1793](#src-SIL1793) | [↗1](https://sillok.history.go.kr/id/kva_10401001_002) [↗2](https://db.history.go.kr/common/compareViewer.do?levelId=bb_165_001_01_0070&type=joseon) [↗3](https://sillok.history.go.kr/id/kva_11709016_003) | 1차 사료(비교·후대) (비교·후대 맥락 포함) | 미확인 |
| [E2](#var-E2) | 가구별 식량 접근성 격차 | [FAO2008](#src-FAO2008), [NIKH_NH36](#src-NIKH_NH36) | [↗1](https://www.fao.org/agrifood-economics/publications/detail/en/c/122386/) [↗2](https://contents.history.go.kr/mobile/nh/view.do?levelId=nh_036_0030_0010_0010) | 이론 | 미확인 |
| [E3](#var-E3) | 상층 양반지주·토호지주의 경제력 | [LEE2009](#src-LEE2009), [NIKH_NH36](#src-NIKH_NH36) | [↗1](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE10953875) [↗2](https://contents.history.go.kr/mobile/nh/view.do?levelId=nh_036_0030_0010_0010) | 학술연구 | 미확인 |
| [E4](#var-E4) | 조재항의 경제적 지위 | [CHUG](#src-CHUG) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) | 1차 사료 | 간접 확인 |
| [E5](#var-E5) | 조재항의 영향력·강제 권분 회피 능력 | [LEE2009](#src-LEE2009) | [↗1](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE10953875) | 극중 설정 | 미입증 |
| [E6](#var-E6) | 서민지주·부농·요호부민의 출연 부담 | [LEE2009](#src-LEE2009), [BIB1741](#src-BIB1741) | [↗1](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE10953875) [↗2](https://db.history.go.kr/common/compareViewer.do?levelId=bb_109_001_05_0430&type=joseon) | 극중 가설 (비교·후대 맥락 포함) | 미입증 |
| [E7](#var-E7) | 상층 지주들의 권분 회피 여부 | [LEE2009](#src-LEE2009) | [↗1](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE10953875) | 극중 가설 | 미입증 |
| [E8](#var-E8) | 조재항의 최초 출연량 | 없음 | 없음 | 극중 설정 | 극중 설정 |
| [E9](#var-E9) | 추가 출연 요구량 | 없음 | 없음 | 극중 설정 | 극중 설정 |
| [E10](#var-E10) | 식솔의 양식과 종자 비축량 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 극중 설정 |
| [E11](#var-E11) | 소작농과 관련된 부담 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [E12](#var-E12) | 다음 수확 전까지의 생계 위험 | 없음 | 없음 | 극중 가설 | 미입증 |
| [E13](#var-E13) | 빈농·몰락 소농의 식량 부족 | [FAO2008](#src-FAO2008), [BIB178206](#src-BIB178206), [BIB178207](#src-BIB178207) | [↗1](https://www.fao.org/agrifood-economics/publications/detail/en/c/122386/) [↗2](https://db.history.go.kr/item/compareViewer.do?levelId=bb_164_001_06_0220) [↗3](https://db.history.go.kr/common/compareViewer.do?levelId=bb_165_001_01_0070&type=joseon) | 극중 가설 (비교·후대 맥락 포함) | 미입증 |
| [E14](#var-E14) | 공곡·환곡과 민간 권분의 관계 | [BIB178206](#src-BIB178206), [BIB178207](#src-BIB178207) | [↗1](https://db.history.go.kr/item/compareViewer.do?levelId=bb_164_001_06_0220) [↗2](https://db.history.go.kr/common/compareViewer.do?levelId=bb_165_001_01_0070&type=joseon) | 1차 사료(비교·후대) (비교·후대 맥락 포함) | 미확인 |
| [E15](#var-E15) | 지역 내 구휼 대상 가호의 규모 | [HOGU](#src-HOGU) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_590_0050_0160) | 1차 사료(비교·후대) (비교·후대 맥락 포함) | 미확인 |
| [A1](#var-A1) | 권분의 자발성 | [LEE2009](#src-LEE2009), [SIL1783A](#src-SIL1783A), [BIB1741](#src-BIB1741) | [↗1](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE10953875) [↗2](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) [↗3](https://db.history.go.kr/common/compareViewer.do?levelId=bb_109_001_05_0430&type=joseon) [↗4](https://sillok.history.go.kr/id/kva_10701018_004) | 극중 가설 (비교·후대 맥락 포함) | 미입증 |
| [A2](#var-A2) | 늑분 발생 여부 | [LEE2009](#src-LEE2009), [BIB1727](#src-BIB1727), [BIB1731](#src-BIB1731), [SIL1783O](#src-SIL1783O) | [↗1](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE10953875) [↗2](https://db.history.go.kr/item/compareViewer.do?levelId=bb_082_001_06_0310) [↗3](https://db.history.go.kr/common/compareViewer.do?levelId=bb_090r_001_06_0190&type=joseon) [↗4](https://sillok.history.go.kr/id/kva_10710029_003) | 극중 가설 (비교·후대 맥락 포함) | 미입증 |
| [A3](#var-A3) | 관봉(官封) 발생 여부 | [BIB1727](#src-BIB1727) | [↗1](https://db.history.go.kr/item/compareViewer.do?levelId=bb_082_001_06_0310) | 극중 가설 (비교·후대 맥락 포함) | 미확인 |
| [A4](#var-A4) | 강제 대부 및 상환 여부 | 없음 | 없음 | 극중 가설 (비교·후대 맥락 포함) | 미확인 |
| [A5](#var-A5) | 권중립의 실제 구휼 실적 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [A6](#var-A6) | 권중립의 인사상 이익 | [BIB1741](#src-BIB1741) | [↗1](https://db.history.go.kr/common/compareViewer.do?levelId=bb_109_001_05_0430&type=joseon) | 극중 가설 (비교·후대 맥락 포함) | 미확인 |
| [A7](#var-A7) | 조상진의 포폄 등급 및 근거 | [GYDJ_POPHYEOM](#src-GYDJ_POPHYEOM) | 없음 | 극중 가설 | 미확인 |
| [A8](#var-A8) | 포폄계본의 사실 정확성 | [SIGOK_PDF](#src-SIGOK_PDF), [SIL178204](#src-SIL178204) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) [↗2](https://sillok.history.go.kr/id/kva_10604023_001) | 극중 가설 (비교·후대 맥락 포함) | 미확인 |
| [A9](#var-A9) | 강제 권분 관련 주민 항의 | [SIGOK_PDF](#src-SIGOK_PDF), [SIL1783O](#src-SIL1783O) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) [↗2](https://sillok.history.go.kr/id/kva_10710029_003) | 극중 설정 (비교·후대 맥락 포함) | 미입증 |
| [A10](#var-A10) | 권중립의 강압 인지 | 없음 | 없음 | 극중 가설 | 미입증 |
| [A11](#var-A11) | 조상진의 강압 인지 시점 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 가설 | 미입증 |
| [A12](#var-A12) | 권중립의 책임 전가 | 없음 | 없음 | 극중 가설 | 미입증 |
| [A13](#var-A13) | 조상진의 평가 방어 | [SIL1783](#src-SIL1783), [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) [↗2](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 가설 | 미입증 |
| [A14](#var-A14) | 장부 누락·변조·허위 보고 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [A15](#var-A15) | 정조의 재조사 명령에 대한 대응 | [SIL1783](#src-SIL1783) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [S1](#var-S1) | 주민들의 최초 불만 대상 | [GIRARD1986](#src-GIRARD1986) | 없음 | 극중 가설 | 미입증 |
| [S2](#var-S2) | 권중립의 책임 전가 | [ROTHSCHILD2012](#src-ROTHSCHILD2012) | [↗1](https://doi.org/10.1037/a0027413) | 극중 가설 | 미입증 |
| [S3](#var-S3) | 이가원의 선택적 정보 공개 | [SIGOK_PDF](#src-SIGOK_PDF), [BIB1731](#src-BIB1731) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) [↗2](https://db.history.go.kr/common/compareViewer.do?levelId=bb_090r_001_06_0190&type=joseon) | 극중 설정 (비교·후대 맥락 포함) | 미입증 |
| [S4](#var-S4) | 윤씨의 기존 출연에 대한 주민 인지 | 없음 | 없음 | 극중 가설 | 미입증 |
| [S5](#var-S5) | 윤씨의 거절 이유에 대한 주민 정보 | 없음 | 없음 | 극중 가설 | 미입증 |
| [S6](#var-S6) | 윤씨에게 식량난 책임을 돌리는 정도 | [GIRARD1986](#src-GIRARD1986), [ROTHSCHILD2012](#src-ROTHSCHILD2012) | [↗1](https://doi.org/10.1037/a0027413) | 이론 | 미입증 |
| [S7](#var-S7) | 주민들의 집단적 분노 | [GIRARD1986](#src-GIRARD1986), [LEEJW2015](#src-LEEJW2015), [JEDWAB2019](#src-JEDWAB2019) | [↗1](https://doi.org/10.33156/philos.2015.40..010) [↗2](https://doi.org/10.1007/s10887-019-09167-1) | 이론 | 미입증 |
| [S8](#var-S8) | 폭력에 동조한 사람들의 범위 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [S9](#var-S9) | 실제 살해를 계획한 사람 | [SIGOK_PDF](#src-SIGOK_PDF), [LEEJW2015](#src-LEEJW2015), [DMYJ_MOSAL](#src-DMYJ_MOSAL) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) [↗2](https://doi.org/10.33156/philos.2015.40..010) [↗3](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_170_0190_0010_0010) | 극중 설정 | 미입증 |
| [S10](#var-S10) | 실행자·방관자·반대자의 구분 | [SIGOK_PDF](#src-SIGOK_PDF), [DMYJ_MOSAL](#src-DMYJ_MOSAL) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) [↗2](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_170_0190_0010_0010) [↗3](https://sillok.history.go.kr/id/kva_10706003_004) | 극중 설정 | 미입증 |
| [S11](#var-S11) | 살인을 촉발한 구체적 사건 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [S12](#var-S12) | 시신 이동과 범행 후 침묵 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [F1](#var-F1) | 조재항과 윤씨의 부부관계 | [SIM](#src-SIM) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) | 극중 설정 | 미입증 |
| [F2](#var-F2) | 권분 문제로 발생한 부부 갈등 | [SIM](#src-SIM), [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [↗2](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [F3](#var-F3) | 윤씨와 외숙부 조환의 정서적 관계 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [F4](#var-F4) | 조환이 윤씨의 경제적 판단을 알았는가 | 없음 | 없음 | 극중 가설 | 미입증 |
| [F5](#var-F5) | 조환과 조재항 사이의 신뢰 | [BOWEN1978](#src-BOWEN1978) | 없음 | 극중 가설 | 미입증 |
| [F6](#var-F6) | 조환의 병환과 정보 접근성 | [CHUG](#src-CHUG) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) | 1차 사료 | 간접 확인 |
| [F7](#var-F7) | 윤씨 여동생의 최초 인식 | 없음 | 없음 | 극중 설정 | 미입증 |
| [F8](#var-F8) | 윤씨 사망 이후 가족의 정서적 반응 | 없음 | 없음 | 극중 설정 | 미입증 |
| [F9](#var-F9) | 이가원이 조환에게 제공한 정보 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 가설 | 미입증 |
| [F10](#var-F10) | 조환의 고발 동기 | [BOWEN1978](#src-BOWEN1978), [KERR1988](#src-KERR1988) | 없음 | 극중 가설 | 미입증 |
| [F11](#var-F11) | 가족 내부의 삼각관계 | [BOWEN1978](#src-BOWEN1978), [KERR1988](#src-KERR1988) | 없음 | 이론 | 미입증 |
| [F12](#var-F12) | 조환이 이가원의 주장을 믿게 되는 조건 | [BOWEN1978](#src-BOWEN1978) | 없음 | 이론 | 미입증 |
| [M1](#var-M1) | 이가원의 실제 경제적 위치 | 없음 | 없음 | 1차 사료 | 미확인 |
| [M2](#var-M2) | 조재항(또는 윤씨)과의 친족관계 | [SIL1783](#src-SIL1783), [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) [↗2](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 1차 사료 | 사료 간 충돌 |
| [M3](#var-M3) | 극중 호방 직책 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 극중 설정 |
| [M4](#var-M4) | 권분 정보 접근 가능성 | [SIGOK_PDF](#src-SIGOK_PDF), [BIB1731](#src-BIB1731) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) [↗2](https://db.history.go.kr/common/compareViewer.do?levelId=bb_090r_001_06_0190&type=joseon) | 극중 설정 (비교·후대 맥락 포함) | 미입증 |
| [M5](#var-M5) | 윤씨 생전 갈등에 대한 인지 | [SIM](#src-SIM) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) | 극중 가설 | 미입증 |
| [M6](#var-M6) | 실제 살해범 인지 여부 | 없음 | 없음 | 극중 가설 | 미입증 |
| [M7](#var-M7) | 금전 요구의 내용 | [CHUG](#src-CHUG) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) | 1차 사료 | 간접 확인 |
| [M8](#var-M8) | 금전 요구 거절 이후의 행동 | [CHUG](#src-CHUG) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) | 1차 사료 | 간접 확인 |
| [M9](#var-M9) | 조환 사주 | [CHUG](#src-CHUG), [SIL1783](#src-SIL1783) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) [↗2](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [M10](#var-M10) | 이봉의 고발 참여 | 없음 | 없음 | 1차 사료 | 미확인 |
| [M11](#var-M11) | 농요 제작과 최초 유포 | [SIL1783](#src-SIL1783), [CHUG](#src-CHUG) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) [↗2](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080) | 1차 사료 | 간접 확인 |
| [M12](#var-M12) | 목격담과 전언의 구분 | [SIL1783](#src-SIL1783) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [M13](#var-M13) | 허위증언의 전파 | [SIL1783](#src-SIL1783) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [M14](#var-M14) | 조재항에게 살인 혐의를 집중시키는 과정 | [SIM](#src-SIM), [SIL1783](#src-SIL1783), [DMYJ_MUGO](#src-DMYJ_MUGO) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [↗2](https://sillok.history.go.kr/id/kva_10706003_004) [↗3](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_170_0220_0010_0050) | 1차 사료 | 간접 확인 |
| [J1](#var-J1) | 권중립 초검의 정확성 | [SIM](#src-SIM), [SIL1783](#src-SIL1783) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [↗2](https://sillok.history.go.kr/id/kva_10706003_004) | 모형 추론 | 간접 확인 |
| [J2](#var-J2) | 이우배 복검의 독립성 | [SIM](#src-SIM) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) | 극중 가설 | 미입증 |
| [J3](#var-J3) | 상흔 해석 | [SIM](#src-SIM), [SIL1783](#src-SIL1783) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) [↗2](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [J4](#var-J4) | 직접 목격과 전언의 구분 | [SIL1783](#src-SIL1783) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [J5](#var-J5) | 최초 수사에서 권분 갈등 조사 여부 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [J6](#var-J6) | 실제 범행 장소와 시신 발견 장소 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [J7](#var-J7) | 조재항 구금 | [SIL1783](#src-SIL1783) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [J8](#var-J8) | 정조의 재조사 명령 | [SIL1783](#src-SIL1783), [SIM](#src-SIM) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) [↗2](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) | 1차 사료 | 간접 확인 |
| [J9](#var-J9) | 조상진의 재조사 수행 | [SIL1783](#src-SIL1783), [BIB1781](#src-BIB1781), [TGJS](#src-TGJS) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) [↗2](https://db.history.go.kr/item/compareViewer.do?levelId=bb_163r_001_03_0590) [↗3](https://db.history.go.kr/joseon/item/level.do?allViewYn=Y&levelId=jlawb_120_0020_0290) | 1차 사료 (비교·후대 맥락 포함) | 간접 확인 |
| [J10](#var-J10) | 원본 기록과 감영 보고의 차이 | [SIGOK_PDF](#src-SIGOK_PDF) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) | 극중 설정 | 미입증 |
| [J11](#var-J11) | 이득준의 극중 재조사 역할 | [SJW1780](#src-SJW1780), [TGJS](#src-TGJS) | [↗1](https://sjw.history.go.kr/id/SJW-G04030140-02600) [↗2](https://db.history.go.kr/joseon/item/level.do?allViewYn=Y&levelId=jlawb_120_0020_0290) | 극중 설정 (비교·후대 맥락 포함) | 미확인 |
| [J12](#var-J12) | 심낙수의 극중 독립 조사 | [SIGOK_PDF](#src-SIGOK_PDF), [YJSIL1742](#src-YJSIL1742) | [↗1](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) [↗2](https://sillok.history.go.kr/id/wua_11801006_001) | 극중 설정 (비교·후대 맥락 포함) | 극중 설정 |
| [J13](#var-J13) | 조재정 격쟁 | [SIM](#src-SIM) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040) | 1차 사료 | 간접 확인 |
| [J14](#var-J14) | 조재항의 방면 | [SIL1783](#src-SIL1783) | [↗1](https://sillok.history.go.kr/id/kva_10706003_004) | 1차 사료 | 간접 확인 |
| [J15](#var-J15) | 실제 살해범 확인 및 처벌 | [DMYJ_MOSAL](#src-DMYJ_MOSAL) | [↗1](https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_170_0190_0010_0010) [↗2](https://sillok.history.go.kr/id/kva_10706003_004) | 극중 설정 | 극중 설정 |
<!-- END:EVIDENCE_MAP -->

<a id="variables"></a>
## C. 변수 정의

데이터 원천: [`02_variables.yaml`](02_variables.yaml) (생성기 [`tools/build_variables.py`](tools/build_variables.py)).

<!-- BEGIN:VARIABLES -->
#### T군 — 시간·관직·사건 순서

- <a id="var-T1"></a>**T1 권중립의 백천군수 재임 구간** — 권중립이 백천군수로 재임한 음력 시작·종료 시점 〔값: [KJR_START, KJR_END] (음력 서수) · 층위: historical · 미확인〕 출처: [SIM](#src-SIM) · 주장: CL-SIM-07 · 모형 기호: `KJR_START`, `KJR_END` · 주: 초검관이었다는 간접 기록만 있음 → 초검 시점에 재임했다는 제약만 사용. 부임·이임 기사 미확보
- <a id="var-T2"></a>**T2 조상진의 황해감사 재임 구간** — 조상진이 황해감사로 재임한 구간 〔값: [JSJ_ARRIVE, JSJ_END] · 층위: historical · 간접 확인〕 출처: [SIGOK_PDF](#src-SIGOK_PDF), [BIB1781](#src-BIB1781), [SIL1783M](#src-SIL1783M), [SIL1783](#src-SIL1783) · 주장: CL-OFF-04, CL-OFF-01, CL-OFF-03, CL-SIL-09 · 모형 기호: `JSJ_ARRIVE`, `JSJ_END` · 주: 부임(1780 여름)은 미확인, 1781 L9 재임·1783 L5 대사성은 간접 확인
- <a id="var-T3"></a>**T3 이경양의 황해감사 부임 및 재임** — 후임 감사 이경양의 부임 시점 〔값: LKY_START ≤ 1782 L4 23 · 층위: historical · 간접 확인〕 출처: [SIL178204](#src-SIL178204) · 주장: CL-OFF-02 · 모형 기호: `LKY_START` · 주: 정확한 부임일 미확인
- <a id="var-T4"></a>**T4 권중립·조상진 재임 중첩 여부** — 두 관리의 재임 구간이 겹치는가 〔값: bool (T1 ∩ T2 ≠ ∅) · 층위: historical · 미확인〕 출처: [SIM](#src-SIM), [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-OFF-04, CL-SIM-07 · 주: T1이 미확인이므로 판정 불가. 극중 필수 조건은 중첩을 요구
- <a id="var-T5"></a>**T5 권중립의 포폄 시점** — 조상진(또는 다른 감사)이 권중립을 평가한 시점 〔값: 음력 6·12월(정기) 또는 수시 · 층위: institutional · 미확인〕 출처: [GYDJ_POPHYEOM](#src-GYDJ_POPHYEOM) · 주장: CL-INST-01, CL-FILM-REQ-01 · 모형 기호: `POPHYEOM` · 주: 실제 포폄계본 미확보
- <a id="var-T6"></a>**T6 포폄의 평가자** — 포폄을 내린 관찰사 〔값: {조상진, 윤방 등 전임, 미상} · 층위: scenario · 미확인〕 출처: [GYDJ_POPHYEOM](#src-GYDJ_POPHYEOM) · 주장: CL-FILM-REQ-01, CL-INST-01 · 모형 기호: `pophyeom_by_jsj` · 주: 윤방 등 전임 감사의 성명·재임은 이번 실행에서 확인하지 못함
- <a id="var-T7"></a>**T7 권중립의 포폄 등급** — 상·중·하 등 평가 등급 〔값: {상, 중, 하, 미상} · 층위: scenario · 미확인〕 출처: 없음 · 주장: CL-FILM-REQ-02 · 모형 기호: `jsj_good_pophyeom` · 주: 포폄계본 미확보
- <a id="var-T8"></a>**T8 윤씨 사망 시점** — 윤씨가 사망한 음력 시점 〔값: 음력 서수 · 층위: historical · 사료 간 충돌〕 출처: [SIM](#src-SIM), [SIL1783](#src-SIL1783), [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-SIM-01, CL-SIL-01, CL-SIM-06, CL-FILM-03 · 모형 기호: `DEATH` · 주: 사료가 사망일을 직접 주지 않음. 성옥 연대(1780/1781) 채택에 따라 가능 구간이 달라짐
- <a id="var-T9"></a>**T9 윤씨 매장 시점** — 사망 후 매장까지 〔값: 사망 + 4~5일 · 층위: historical · 간접 확인〕 출처: [CHUG](#src-CHUG), [SIM](#src-SIM) · 주장: CL-CHUG-01, CL-SIM-06 · 모형 기호: `BURIAL` · 주: 원문 일수 표현 미확보
- <a id="var-T10"></a>**T10 이가원의 금전 요구 시점** — 이가원이 조재항에게 금품을 요구한 시점 〔값: > 사망 · 층위: historical · 간접 확인〕 출처: [CHUG](#src-CHUG) · 주장: CL-CHUG-02 · 모형 기호: `MONEY_DEMAND`
- <a id="var-T11"></a>**T11 농요 제작·유포 시점** — 이가원이 농요를 만들어 퍼뜨리기 시작한 시점 〔값: > 사망 · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783), [CHUG](#src-CHUG) · 주장: CL-SIL-03, CL-CHUG-04 · 모형 기호: `SONG`
- <a id="var-T12"></a>**T12 조환 사주 시점** — 이가원이 조환을 사주한 시점 〔값: 사망 < T12 < 고발 · 층위: historical · 간접 확인〕 출처: [CHUG](#src-CHUG) · 주장: CL-CHUG-03 · 모형 기호: `INSTIGATE`
- <a id="var-T13"></a>**T13 공식 고발 시점** — 관아에 고발이 접수된 시점 〔값: 사망 + 약 40일(35~45 허용) · 층위: historical · 간접 확인〕 출처: [SIM](#src-SIM), [CHUG](#src-CHUG), [SIL1783](#src-SIL1783) · 주장: CL-SIM-06, CL-CHUG-04, CL-SIL-13 · 모형 기호: `ACCUSE`
- <a id="var-T14"></a>**T14 권중립 초검 시점** — 초검 실시 시점 〔값: ≥ 고발 · 층위: historical · 간접 확인〕 출처: [SIM](#src-SIM) · 주장: CL-SIM-07, CL-SIM-06 · 모형 기호: `CHOGEOM`
- <a id="var-T15"></a>**T15 이우배 복검 시점** — 복검 실시 시점 〔값: > 초검 · 층위: historical · 간접 확인〕 출처: [SIM](#src-SIM) · 주장: CL-SIM-07 · 모형 기호: `BOKGEOM`
- <a id="var-T16"></a>**T16 옥사 성립 시점** — 살인 옥사가 성립한 시점 〔값: 1780 L6(심리록) vs 1781(실록 회고) · 층위: historical · 사료 간 충돌〕 출처: [SIM](#src-SIM), [SIL1783](#src-SIL1783) · 주장: CL-SIM-01, CL-SIL-01 · 모형 기호: `OKSA` · 주: 04_historical_conflicts.md 참조
- <a id="var-T17"></a>**T17 조재항 구금 시작·종료** — 구금 구간 〔값: [초검 이후, 방면 판부 이후] · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783) · 주장: CL-SIL-07, CL-SIL-11 · 모형 기호: `DETAIN_START`, `DETAIN_END` · 주: 석방 집행일 미상
- <a id="var-T18"></a>**T18 정조의 재조사 명령** — 조상진에게 재조사를 명한 시점 〔값: 1781 봄(실록 회고) / 극중 1780 L12 · 층위: historical · 사료 간 충돌〕 출처: [SIL1783](#src-SIL1783), [SIM](#src-SIM), [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-SIL-02, CL-SIM-03, CL-FILM-07 · 모형 기호: `REVIEW_ORDER`, `HYEONGJO_1781_8` · 주: 시곡 PDF 부록은 1780 L12 명령을 '역사에 근거'로 분류하나 근거 구절을 제시하지 않음
- <a id="var-T19"></a>**T19 조재정 격쟁** — 격쟁 시점 〔값: 1782 L7 · 층위: historical · 간접 확인〕 출처: [SIM](#src-SIM) · 주장: CL-SIM-04, CL-FILM-10 · 모형 기호: `JOKJAENG`
- <a id="var-T20"></a>**T20 최종 판부** — 방면·정배·파직 판부 〔값: 1783 L6 3 · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783) · 주장: CL-SIL-07, CL-SIL-08, CL-SIL-09 · 모형 기호: `FINAL`

#### E군 — 경제·농업·계층

- <a id="var-E1"></a>**E1 1780~1781년 배천의 농업 상황** — 배천의 작황·구휼 수요 〔값: {양호, 부분 부족, 흉작, 미상} · 층위: context · 미확인〕 출처: [SIL1780J](#src-SIL1780J), [BIB178207](#src-BIB178207), [SIL1793](#src-SIL1793) · 주장: CL-ECON-01 · 맥락 주장: CL-ECON-03, CL-ECON-06 · 주: 1780년 배천 직접 기록 없음. 1779 전국 회복 평가는 전면 흉년 가정을 제약
- <a id="var-E2"></a>**E2 가구별 식량 접근성 격차** — 가용성과 접근성의 가구 간 차이 〔값: 정성 · 층위: theory · 미확인〕 출처: [FAO2008](#src-FAO2008), [NIKH_NH36](#src-NIKH_NH36) · 주장: CL-THY-06, CL-ECON-07
- <a id="var-E3"></a>**E3 상층 양반지주·토호지주의 경제력** — 고을 내 최상층 지주의 경제력 〔값: 정성 · 층위: context · 미확인〕 출처: [LEE2009](#src-LEE2009), [NIKH_NH36](#src-NIKH_NH36) · 주장: CL-LEE-01, CL-ECON-07 · 주: 배천 개별 자료 없음
- <a id="var-E4"></a>**E4 조재항의 경제적 지위** — 조재항 가호의 재력 〔값: {넉넉함(사료), 정확한 규모 미상} · 층위: historical · 간접 확인〕 출처: [CHUG](#src-CHUG) · 주장: CL-CHUG-05 · 주: '넉넉하게 살았다'까지만. 토지·곡식 규모 없음
- <a id="var-E5"></a>**E5 조재항의 영향력·강제 권분 회피 능력** — 서민지주·요호부민으로서 권분 요구를 회피하기 어려웠는가 〔값: bool · 층위: scenario · 미입증〕 출처: [LEE2009](#src-LEE2009) · 주장: CL-FILM-REQ-03, CL-LEE-01 · 모형 기호: `e5_cannot_evade` · 주: 계층 규정은 창작
- <a id="var-E6"></a>**E6 서민지주·부농·요호부민의 출연 부담** — 부담이 조재항에게 집중되는가 〔값: bool · 층위: scenario · 미입증〕 출처: [LEE2009](#src-LEE2009), [BIB1741](#src-BIB1741) · 주장: CL-LEE-01 · 맥락 주장: CL-CMP-03 · 모형 기호: `burden_concentrated`
- <a id="var-E7"></a>**E7 상층 지주들의 권분 회피 여부** — 상층 지주가 출연을 회피했는가 〔값: bool · 층위: scenario · 미입증〕 출처: [LEE2009](#src-LEE2009) · 주장: CL-LEE-01 · 모형 기호: `u_elite_evade`
- <a id="var-E8"></a>**E8 조재항의 최초 출연량** — 최초 출연 곡식량 〔값: 가상 단위(scenario/scenario_parameters.yaml) · 층위: scenario · 극중 설정〕 출처: 없음 · 주장: 없음 · 주: 가상 실험값 전용. 역사 데이터셋에 넣지 않음
- <a id="var-E9"></a>**E9 추가 출연 요구량** — 추가 요구량과 가용량의 비교 〔값: 가상 단위; u_extra_exceeds · 층위: scenario · 극중 설정〕 출처: 없음 · 주장: 없음 · 모형 기호: `u_extra_exceeds` · 주: ECON_A(초과)/ECON_B(이내) 시나리오
- <a id="var-E10"></a>**E10 식솔의 양식과 종자 비축량** — G_양식·G_종자 〔값: 가상 단위 · 층위: scenario · 극중 설정〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-01 · 주: 가상 실험값 전용
- <a id="var-E11"></a>**E11 소작농과 관련된 부담** — 소작 관계에서 생기는 양식·종자 부담 〔값: 정성 · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-01
- <a id="var-E12"></a>**E12 다음 수확 전까지의 생계 위험** — G_가용 < 추가 요구일 때의 위험 〔값: bool · 층위: scenario · 미입증〕 출처: 없음 · 주장: 없음 · 모형 기호: `econ_refusal`
- <a id="var-E13"></a>**E13 빈농·몰락 소농의 식량 부족** — 일부 가구의 당장의 부족 〔값: bool · 층위: scenario · 미입증〕 출처: [FAO2008](#src-FAO2008), [BIB178206](#src-BIB178206), [BIB178207](#src-BIB178207) · 주장: CL-THY-06 · 맥락 주장: CL-ECON-02, CL-ECON-03 · 모형 기호: `u_shortage` · 주: 1782년 배천 기록을 1780년으로 소급 금지
- <a id="var-E14"></a>**E14 공곡·환곡과 민간 권분의 관계** — 가분(관곡)과 권분(부민 출연)의 병존·대체 〔값: 정성 · 층위: context · 미확인〕 출처: [BIB178206](#src-BIB178206), [BIB178207](#src-BIB178207) · 주장: 없음 · 맥락 주장: CL-ECON-02, CL-ECON-03 · 주: 加分 ≠ 勸分
- <a id="var-E15"></a>**E15 지역 내 구휼 대상 가호의 규모** — 구휼 대상 호수 〔값: 미상 · 층위: context · 미확인〕 출처: [HOGU](#src-HOGU) · 주장: 없음 · 맥락 주장: CL-ECON-05 · 주: 1789 호구를 1780년 값으로 쓰지 않음

#### A군 — 권분·포폄·행정 책임

- <a id="var-A1"></a>**A1 권분의 자발성** — 출연이 권유에 그쳤는가 〔값: bool · 층위: scenario · 미입증〕 출처: [LEE2009](#src-LEE2009), [SIL1783A](#src-SIL1783A), [BIB1741](#src-BIB1741) · 주장: CL-LEE-02, CL-FILM-01 · 맥락 주장: CL-CMP-03, CL-CMP-04 · 모형 기호: `entitlement_framing`
- <a id="var-A2"></a>**A2 늑분 발생 여부** — 강제 권분(늑분)이 있었는가 〔값: bool · 층위: scenario · 미입증〕 출처: [LEE2009](#src-LEE2009), [BIB1727](#src-BIB1727), [BIB1731](#src-BIB1731), [SIL1783O](#src-SIL1783O) · 주장: CL-LEE-02 · 맥락 주장: CL-CMP-01, CL-CMP-02, CL-CMP-05 · 모형 기호: `kjr_coercive` · 주: 제도적 선례는 있으나 1780 배천 직접 기록 없음
- <a id="var-A3"></a>**A3 관봉(官封) 발생 여부** — 관아가 부민 곡식을 봉함했는가 〔값: bool · 층위: scenario · 미확인〕 출처: [BIB1727](#src-BIB1727) · 주장: 없음 · 맥락 주장: CL-REQ-01, CL-CMP-01 · 주: 1782 서명선 비판 기사 미확보
- <a id="var-A4"></a>**A4 강제 대부 및 상환 여부** — 강제 대부·상환 〔값: bool · 층위: scenario · 미확인〕 출처: 없음 · 주장: 없음 · 맥락 주장: CL-REQ-01 · 주: 1782 서명선 비판 기사 미확보(비교 사례 후보)
- <a id="var-A5"></a>**A5 권중립의 실제 구휼 실적** — 실적의 실재·과장 여부 〔값: {실재, 과장, 미상} · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-01, CL-FILM-14 · 모형 기호: `a5_inflated`, `RELIEF_ADMIN`
- <a id="var-A6"></a>**A6 권중립의 인사상 이익** — 포폄·포상을 통한 이익 기대 〔값: bool · 층위: scenario · 미확인〕 출처: [BIB1741](#src-BIB1741) · 주장: 없음 · 맥락 주장: CL-REQ-02, CL-CMP-03 · 모형 기호: `u_kjr_reward_expect`, `kjr_career_stake`
- <a id="var-A7"></a>**A7 조상진의 포폄 등급 및 근거** — 긍정 포폄 여부와 근거 〔값: bool · 층위: scenario · 미확인〕 출처: [GYDJ_POPHYEOM](#src-GYDJ_POPHYEOM) · 주장: CL-FILM-REQ-02, CL-INST-01 · 모형 기호: `jsj_good_pophyeom` · 주: 포폄계본 미확보
- <a id="var-A8"></a>**A8 포폄계본의 사실 정확성** — 평가 근거 보고가 강압·부담을 포함했는가 〔값: bool · 층위: scenario · 미확인〕 출처: [SIGOK_PDF](#src-SIGOK_PDF), [SIL178204](#src-SIL178204) · 주장: CL-FILM-14 · 맥락 주장: CL-ECON-04 · 모형 기호: `a5_inflated` · 주: 1782 이경양 농황 보고 질책은 '보고 부실'의 후대 비교 사례일 뿐
- <a id="var-A9"></a>**A9 강제 권분 관련 주민 항의** — 항의가 관아에 접수되었는가 〔값: bool + 시점 · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF), [SIL1783O](#src-SIL1783O) · 주장: CL-FILM-14 · 맥락 주장: CL-CMP-05 · 모형 기호: `COMPLAINT`
- <a id="var-A10"></a>**A10 권중립의 강압 인지** — 권중립이 강압을 알았는가 〔값: bool · 층위: scenario · 미입증〕 출처: 없음 · 주장: 없음 · 모형 기호: `kjr_knew_coercion`
- <a id="var-A11"></a>**A11 조상진의 강압 인지 시점** — 포폄 전 / 포폄 후 / 모름 〔값: {사전, 사후, 미인지} · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-06 · 모형 기호: `jsj_knew_at_pophyeom`, `jsj_learned_later_no_correct`, `JSJ_LEARN`
- <a id="var-A12"></a>**A12 권중립의 책임 전가** — 구휼 실패 책임을 윤씨에게 돌리는가(행정 동기 측면) 〔값: bool · 층위: scenario · 미입증〕 출처: 없음 · 주장: 없음 · 모형 기호: `kjr_cover_motive`
- <a id="var-A13"></a>**A13 조상진의 평가 방어** — 포폄·감독 책임을 방어할 동기 〔값: bool · 층위: scenario · 미입증〕 출처: [SIL1783](#src-SIL1783), [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-SIL-06, CL-FILM-08 · 모형 기호: `jsj_cover_motive`, `u_jsj_supervisory_fear` · 주: 실록은 '직접 조사하지 않음'만 기록. 동기는 기록 없음
- <a id="var-A14"></a>**A14 장부 누락·변조·허위 보고** — 의도적 문서 조작 여부 〔값: bool · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-08, CL-FILM-14 · 주: 1787 관리 비위 사례(CL-REQ-03)는 출처 미특정
- <a id="var-A15"></a>**A15 정조의 재조사 명령에 대한 대응** — 조상진의 재조사 수행 방식 〔값: {직접 조사, 수령 위임} · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783) · 주장: CL-SIL-06, CL-SIL-09 · 모형 기호: `reinvest_motivated` · 주: 수령 위임은 간접 확인, '고의'는 극중 설정

#### S군 — 희생양화·책임 귀인·집단폭력

- <a id="var-S1"></a>**S1 주민들의 최초 불만 대상** — 불만이 처음 향한 대상(수령·부민·윤씨) 〔값: 범주 · 층위: scenario · 미입증〕 출처: [GIRARD1986](#src-GIRARD1986) · 주장: CL-THY-01 · 모형 기호: `u_resident_rumor`
- <a id="var-S2"></a>**S2 권중립의 책임 전가** — 권중립이 윤씨에게 책임을 전가하는 정보 행위 〔값: bool · 층위: scenario · 미입증〕 출처: [ROTHSCHILD2012](#src-ROTHSCHILD2012) · 주장: CL-THY-03 · 모형 기호: `kjr_shifts_blame`
- <a id="var-S3"></a>**S3 이가원의 선택적 정보 공개** — 출연량·종자 몫을 숨기고 '곳간에 곡식이 있다'만 알림 〔값: bool · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF), [BIB1731](#src-BIB1731) · 주장: CL-FILM-01 · 맥락 주장: CL-CMP-02 · 모형 기호: `lgw_selective`
- <a id="var-S4"></a>**S4 윤씨의 기존 출연에 대한 주민 인지** — 주민이 기존 협조를 알았는가 〔값: bool · 층위: scenario · 미입증〕 출처: 없음 · 주장: 없음 · 모형 기호: `s4_prior_known`
- <a id="var-S5"></a>**S5 윤씨의 거절 이유에 대한 주민 정보** — 주민에게 전달된 거절 사유 정보 〔값: 범주 · 층위: scenario · 미입증〕 출처: 없음 · 주장: 없음 · 모형 기호: `blame_path`
- <a id="var-S6"></a>**S6 윤씨에게 식량난 책임을 돌리는 정도** — 책임 귀인의 집중 〔값: bool · 층위: theory · 미입증〕 출처: [GIRARD1986](#src-GIRARD1986), [ROTHSCHILD2012](#src-ROTHSCHILD2012) · 주장: CL-THY-01, CL-THY-03 · 모형 기호: `hostility_to_yun` · 주: 분노 ≠ 살인
- <a id="var-S7"></a>**S7 주민들의 집단적 분노** — 적대감의 형성 〔값: bool + 시점 · 층위: theory · 미입증〕 출처: [GIRARD1986](#src-GIRARD1986), [LEEJW2015](#src-LEEJW2015), [JEDWAB2019](#src-JEDWAB2019) · 주장: CL-THY-01, CL-THY-02, CL-THY-04 · 모형 기호: `HOSTILITY`
- <a id="var-S8"></a>**S8 폭력에 동조한 사람들의 범위** — 실행자·동조자의 규모 〔값: 범주 · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-03
- <a id="var-S9"></a>**S9 실제 살해를 계획한 사람** — 사전 결의 vs 현장 의도 〔값: {사전, 현장} · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF), [LEEJW2015](#src-LEEJW2015), [DMYJ_MOSAL](#src-DMYJ_MOSAL) · 주장: CL-FILM-03, CL-THY-02, CL-CMP-08 · 모형 기호: `premeditated`, `u_spont_intent`, `murder_by_residents`
- <a id="var-S10"></a>**S10 실행자·방관자·반대자의 구분** — 가담 거부 주민의 존재 〔값: bool · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF), [DMYJ_MOSAL](#src-DMYJ_MOSAL) · 주장: CL-FILM-03, CL-CMP-08, CL-SIL-10 · 모형 기호: `witness_dissenter` · 주: 실록의 '從輕重決罪'는 무고 관련인 처벌이지 살해범 처벌이 아님
- <a id="var-S11"></a>**S11 살인을 촉발한 구체적 사건** — 밤길의 요구·거절 등 〔값: bool · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-03 · 모형 기호: `u_trigger`
- <a id="var-S12"></a>**S12 시신 이동과 범행 후 침묵** — 시신 이동·침묵 강제 〔값: bool · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-04

#### F군 — 가족체계와 조환 사주

- <a id="var-F1"></a>**F1 조재항과 윤씨의 부부관계** — 관계의 질 〔값: 정성 · 층위: scenario · 미입증〕 출처: [SIM](#src-SIM) · 주장: CL-SIM-02 · 주: 사료의 '밥 한 사발' 폭행은 혐의일 뿐
- <a id="var-F2"></a>**F2 권분 문제로 발생한 부부 갈등** — 출연을 둘러싼 이견 〔값: bool · 층위: scenario · 미입증〕 출처: [SIM](#src-SIM), [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-SIM-02, CL-FILM-01 · 모형 기호: `yun_refuses`, `u_yun_other_reason`
- <a id="var-F3"></a>**F3 윤씨와 외숙부 조환의 정서적 관계** — 친밀도 〔값: 정성 · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-13 · 주: '외숙부'는 사용자 지시문. PDF는 '윤씨의 친족'
- <a id="var-F4"></a>**F4 조환이 윤씨의 경제적 판단을 알았는가** — 거절 이유 인지 〔값: bool · 층위: scenario · 미입증〕 출처: 없음 · 주장: 없음 · 모형 기호: `hwan_knows_reason`
- <a id="var-F5"></a>**F5 조환과 조재항 사이의 신뢰** — 기존 신뢰 〔값: bool · 층위: scenario · 미입증〕 출처: [BOWEN1978](#src-BOWEN1978) · 주장: CL-THY-05 · 모형 기호: `hwan_trusts_jjh`
- <a id="var-F6"></a>**F6 조환의 병환과 정보 접근성** — 병환 및 정보 의존 〔값: bool · 층위: historical · 간접 확인〕 출처: [CHUG](#src-CHUG) · 주장: CL-CHUG-03 · 모형 기호: `hwan_ill`, `u_hwan_isolated` · 주: 병환은 간접 확인, 정보 의존은 추론
- <a id="var-F7"></a>**F7 윤씨 여동생의 최초 인식** — 여동생이 아는 마지막 행적 〔값: 정성 · 층위: scenario · 미입증〕 출처: 없음 · 주장: 없음
- <a id="var-F8"></a>**F8 윤씨 사망 이후 가족의 정서적 반응** — 애도·의심 〔값: 정성 · 층위: scenario · 미입증〕 출처: 없음 · 주장: 없음
- <a id="var-F9"></a>**F9 이가원이 조환에게 제공한 정보** — 부부 언쟁·거절 이유의 재구성 〔값: bool · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-13 · 모형 기호: `lgw_reports_quarrel`, `lgw_reframes_reason`
- <a id="var-F10"></a>**F10 조환의 고발 동기** — 죄책감·가족 의무·금전 〔값: 범주 · 층위: scenario · 미입증〕 출처: [BOWEN1978](#src-BOWEN1978), [KERR1988](#src-KERR1988) · 주장: CL-THY-05 · 모형 기호: `hwan_guilt`, `u_family_duty`, `hwan_money_interest`, `hwan_accepts`
- <a id="var-F11"></a>**F11 가족 내부의 삼각관계** — 윤씨–조재항–조환 등 삼각관계 〔값: 정성 · 층위: theory · 미입증〕 출처: [BOWEN1978](#src-BOWEN1978), [KERR1988](#src-KERR1988) · 주장: CL-THY-05 · 주: 09_family_systems.mmd
- <a id="var-F12"></a>**F12 조환이 이가원의 주장을 믿게 되는 조건** — 믿음 성립 조건 〔값: bool · 층위: theory · 미입증〕 출처: [BOWEN1978](#src-BOWEN1978) · 주장: CL-THY-05 · 모형 기호: `hwan_believes`, `u_lgw_extra_evidence`

#### M군 — 이가원의 금전 요구와 무고

- <a id="var-M1"></a>**M1 이가원의 실제 경제적 위치** — 이가원의 재산·생계 〔값: 미상 · 층위: historical · 미확인〕 출처: 없음 · 주장: 없음 · 주: 사료 미확보: 원문 확인 전까지 값 없음(10_evidence_gaps.md)
- <a id="var-M2"></a>**M2 조재항(또는 윤씨)과의 친족관계** — 이가원의 친족 위치 〔값: 범주 · 층위: historical · 사료 간 충돌〕 출처: [SIL1783](#src-SIL1783), [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-SIL-12 · 주: 3사례 보고서: 조재항의 먼 인척 / PDF: 윤씨 친족관계
- <a id="var-M3"></a>**M3 극중 호방 직책** — 관아 호방 여부 〔값: bool · 층위: scenario · 극중 설정〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-02 · 주: 사료 미확인
- <a id="var-M4"></a>**M4 권분 정보 접근 가능성** — 출연 장부 접근 〔값: bool · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF), [BIB1731](#src-BIB1731) · 주장: CL-FILM-02 · 맥락 주장: CL-CMP-02
- <a id="var-M5"></a>**M5 윤씨 생전 갈등에 대한 인지** — 부부 갈등을 알았는가 〔값: bool · 층위: scenario · 미입증〕 출처: [SIM](#src-SIM) · 주장: CL-SIM-02 · 모형 기호: `lgw_reports_quarrel`
- <a id="var-M6"></a>**M6 실제 살해범 인지 여부** — 이가원이 살해범을 아는가·사전 관여 〔값: {모름, 사후 인지, 사전 관여} · 층위: scenario · 미입증〕 출처: 없음 · 주장: 없음 · 모형 기호: `lgw_knows_killers`, `lgw_prior_involvement`, `LGW_PRE_CONTACT` · 주: 사전 관여는 사료의 '사후 무고' 서술을 넘어섬
- <a id="var-M7"></a>**M7 금전 요구의 내용** — 요구한 금품 〔값: 미상 · 층위: historical · 간접 확인〕 출처: [CHUG](#src-CHUG) · 주장: CL-CHUG-02
- <a id="var-M8"></a>**M8 금전 요구 거절 이후의 행동** — 거절 → 사주로의 전환 〔값: bool · 층위: historical · 간접 확인〕 출처: [CHUG](#src-CHUG) · 주장: CL-CHUG-02, CL-CHUG-03 · 모형 기호: `lgw_money_refused`, `u_lgw_other_motive`, `lgw_motive` · 주: '거절'은 무고로 이어진 정황에서의 추론
- <a id="var-M9"></a>**M9 조환 사주** — 이가원의 조환 사주 〔값: bool · 층위: historical · 간접 확인〕 출처: [CHUG](#src-CHUG), [SIL1783](#src-SIL1783) · 주장: CL-CHUG-03, CL-SIL-13 · 모형 기호: `lgw_instigates`
- <a id="var-M10"></a>**M10 이봉의 고발 참여** — 조환 외 고발자 〔값: bool · 층위: historical · 미확인〕 출처: 없음 · 주장: 없음 · 모형 기호: `u_other_accuser` · 주: 사료 미확보: 시놉시스 v4(p.6)만 언급. 원문 확인 필요(10_evidence_gaps.md P8)
- <a id="var-M11"></a>**M11 농요 제작과 최초 유포** — 농요 조작 〔값: bool · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783), [CHUG](#src-CHUG) · 주장: CL-SIL-03, CL-SIL-04, CL-CHUG-04 · 모형 기호: `song_fabricated`, `lgw_song_choice`
- <a id="var-M12"></a>**M12 목격담과 전언의 구분** — 직접 목격 vs 전언 〔값: 범주 · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783) · 주장: CL-SIL-05
- <a id="var-M13"></a>**M13 허위증언의 전파** — 농요·전언의 확산 〔값: 정성 · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783) · 주장: CL-SIL-04
- <a id="var-M14"></a>**M14 조재항에게 살인 혐의를 집중시키는 과정** — 고발·혐의 집중 〔값: bool · 층위: historical · 간접 확인〕 출처: [SIM](#src-SIM), [SIL1783](#src-SIL1783), [DMYJ_MUGO](#src-DMYJ_MUGO) · 주장: CL-SIM-02, CL-SIL-08, CL-SIM-05, CL-CMP-09 · 모형 기호: `accusation`

#### J군 — 검험·무고·재조사·책임 은폐

- <a id="var-J1"></a>**J1 권중립 초검의 정확성** — 초검 결론의 오류 〔값: bool · 층위: historical · 간접 확인〕 출처: [SIM](#src-SIM), [SIL1783](#src-SIL1783) · 주장: CL-SIM-07, CL-SIL-05, CL-SIL-13 · 모형 기호: `chogeom_error`, `oksa_formed` · 주: 최종 판부에서 혐의가 무너졌다는 데서의 추론. 고의성은 극중 설정
- <a id="var-J2"></a>**J2 이우배 복검의 독립성** — 복검이 독립 증거를 썼는가 〔값: {진술원 공유, 검증 소홀, 교정} · 층위: scenario · 미입증〕 출처: [SIM](#src-SIM) · 주장: CL-SIM-07 · 모형 기호: `bokgeom_shared_sources`, `bokgeom_negligent`, `bokgeom_corrects`
- <a id="var-J3"></a>**J3 상흔 해석** — 발길질 상흔 해석 〔값: 정성 · 층위: historical · 간접 확인〕 출처: [SIM](#src-SIM), [SIL1783](#src-SIL1783) · 주장: CL-SIM-02, CL-SIL-05
- <a id="var-J4"></a>**J4 직접 목격과 전언의 구분** — 수사 단계의 증언 구분 〔값: 정성 · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783) · 주장: CL-SIL-05
- <a id="var-J5"></a>**J5 최초 수사에서 권분 갈등 조사 여부** — 초검이 권분 갈등을 조사했는가 〔값: bool · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-05
- <a id="var-J6"></a>**J6 실제 범행 장소와 시신 발견 장소** — 두 장소의 동일 여부 〔값: bool · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-03, CL-FILM-04
- <a id="var-J7"></a>**J7 조재항 구금** — 장기 구금 〔값: bool · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783) · 주장: CL-SIL-11, CL-SIL-07 · 모형 기호: `long_detention`
- <a id="var-J8"></a>**J8 정조의 재조사 명령** — 재조사 명령·형조 심리 〔값: bool + 시점 · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783), [SIM](#src-SIM) · 주장: CL-SIL-02, CL-SIM-03, CL-SIL-11 · 모형 기호: `HYEONGJO_1781_8`
- <a id="var-J9"></a>**J9 조상진의 재조사 수행** — 직접 조사 여부 〔값: bool · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783), [BIB1781](#src-BIB1781), [TGJS](#src-TGJS) · 주장: CL-SIL-06, CL-OFF-01 · 맥락 주장: CL-CMP-07 · 모형 기호: `jsj_direct_investigation`, `reinvest_nonindependent`, `JSJ_REINVEST`
- <a id="var-J10"></a>**J10 원본 기록과 감영 보고의 차이** — 이득준 원본 vs 감영 보고 〔값: bool · 층위: scenario · 미입증〕 출처: [SIGOK_PDF](#src-SIGOK_PDF) · 주장: CL-FILM-08 · 모형 기호: `records_preserved`
- <a id="var-J11"></a>**J11 이득준의 극중 재조사 역할** — 사관 지정 〔값: bool · 층위: scenario · 미확인〕 출처: [SJW1780](#src-SJW1780), [TGJS](#src-TGJS) · 주장: CL-OFF-05 · 맥락 주장: CL-CMP-07 · 주: 1780 L3 평산부사 임명은 미확인, 재조사 참여는 창작
- <a id="var-J12"></a>**J12 심낙수의 극중 독립 조사** — 암행어사 파견 〔값: bool · 층위: scenario · 극중 설정〕 출처: [SIGOK_PDF](#src-SIGOK_PDF), [YJSIL1742](#src-YJSIL1742) · 주장: CL-FILM-09, CL-OFF-06 · 맥락 주장: CL-CMP-06 · 모형 기호: `independent_investigator`, `truth_recoverable`
- <a id="var-J13"></a>**J13 조재정 격쟁** — 격쟁 〔값: bool + 시점 · 층위: historical · 간접 확인〕 출처: [SIM](#src-SIM) · 주장: CL-SIM-04 · 모형 기호: `JOKJAENG`
- <a id="var-J14"></a>**J14 조재항의 방면** — 방면 명령 〔값: bool · 층위: historical · 간접 확인〕 출처: [SIL1783](#src-SIL1783) · 주장: CL-SIL-07
- <a id="var-J15"></a>**J15 실제 살해범 확인 및 처벌** — 살해범 식별 〔값: bool · 층위: scenario · 극중 설정〕 출처: [DMYJ_MOSAL](#src-DMYJ_MOSAL) · 주장: CL-CMP-08, CL-SIL-10 · 모형 기호: `killers_identifiable` · 주: 사료는 실제 살해범을 확정하지 않음
<!-- END:VARIABLES -->

## D. 링크 검사 결과

<!-- BEGIN:LINKCHECK -->
검사 시각: 2026-10-31T15:47:40Z · 결과 파일: [`results/link_check.json`](results/link_check.json)

| 상태 | 개수 | 의미 |
|---|---|---|
| `NETWORK_BLOCKED` | 38 | URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님) |
| `NO_URL` | 4 | 원문 링크 없음 |
<!-- END:LINKCHECK -->

## E. 로컬 사료 파일 위치

| 자료 | 로컬 위치 | 외부 위치 |
|---|---|---|
| 《시곡》 PDF(원본 사본, 읽기 전용) | [`source_local/시곡_인물소개_이득준_출생정보_검증_최종.pdf`](source_local/) · SHA-256 [`source_local/SHA256SUMS`](source_local/SHA256SUMS) | [Google Drive](https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view) |
| PDF 페이지별 텍스트(p.1 기획의도, p.2–3 인물, p.4–8 시놉시스 5막, p.9–12 사료 부록) | [`source_extracts/sigok_pdf_pages/`](source_extracts/sigok_pdf_pages/) | — |
| 사용자 데이터셋(한문 전사 구절 포함) | [`source_extracts/drive_CORE_EVENTS.csv`](source_extracts/drive_CORE_EVENTS.csv) · [`drive_CORE_CASE_CLAIMS.csv`](source_extracts/drive_CORE_CASE_CLAIMS.csv) · [`drive_SOURCES.csv`](source_extracts/drive_SOURCES.csv) | Google Drive |
| C안 보고서·연구계획서·3사례 비교 보고서 인용 위치 | [`source_extracts/drive_other_documents.md`](source_extracts/drive_other_documents.md) | Google Drive |
| 1차 사료 원문 | 로컬 사본 없음(접속 차단) | 위 참고문헌의 개별 기사 링크 |
