# AUDIT 5 — Interactive Visualization (Temporal DAG)

핵심 질문: **탐색용 화면 데이터(docs/data)가 canonical 산출물을 바꾸거나, context·LATENT를 사건처럼 보이게 하거나, 시간 순서·world 결말을 깨뜨렸는가?**

- 판정: **PASS** (ERROR 0 · WARN 0 · UNRESOLVED 0 · INFO 5)
- 화면 데이터: node 122 · edge 205 (canonical `mechanism_super_dag_nodes.csv`·`mechanism_super_dag_edges.csv`와 같음)
- 동결 해시: `ccb7ec63763a715ae90c74dfff37d3ed7980fa705fd152f59de8bed2e31d4e0c`
- 생성: `scripts/gusun_clean/build_visualization.py` → `docs/data/*.json` + `docs/data/bundle.js`(같은 내용, file:// 용)

## 자동 검사 요약

| check | ERROR | WARN | UNRESOLVED | INFO |
|---|---|---|---|---|
| frozen_graph_changed | 0 | 0 | 0 | 1 |
| responsibility_to_biological | 0 | 0 | 0 | 1 |
| temporal_order | 0 | 0 | 0 | 1 |
| ui_summary | 0 | 0 | 0 | 1 |
| view_summary | 0 | 0 | 0 | 1 |
| **합계** | **0** | **0** | **0** | **5** |

ERROR 검사: ui_node_not_canonical·ui_node_missing·ui_node_altered(1), ui_edge_not_canonical·ui_edge_missing·ui_edge_altered(2), status_changed(3), w6_not_rejected(4), outcome_dropped(5), unspecified_as_off(6), context_as_event(7), environment_to_individual(8), responsibility_to_biological(9), temporal_order(10), candidate_grade_changed(11), intervention_changed(12), 그리고 count_mismatch·frozen_graph_changed·stale_ui_data·bundle_mismatch·interaction_changed.

관점별 View·가독성 검사(13): view_not_subset(View node·edge가 canonical 부분집합이고 edge = View node 사이 canonical edge 전부, 새 node·edge 없음), view_status_changed(View metadata에 상태·판정·해석 필드 없음, 좌표 항목은 x·y·lane만), view_hidden_notice_missing(subset View의 숨긴 OBSERVED 목록 = 관측 node − View node, '시각적 필터·삭제 아님·분석상 ON/OFF 아님' 안내와 그 안내를 그리는 코드), label_clipped(node label이 canonical 글자를 모두 담고 말줄임 없음, 가장 긴 줄 ≤ 글자 영역, 높이 ≥ 줄 수 × 줄 높이), font_too_small(node·edge label과 CSS의 모든 font-size ≥ 11pt), line_height_too_small(CSS·node label line-height ≥ 1.6), initial_label_unreadable(모든 View의 첫 화면 최소 배율 × node 글자 ≥ 11pt, lane·시간 구간 글자 포함), responsibility_to_biological(View edge에도 branch A↔B 직접 edge 없음), layout_nondeterministic(같은 입력으로 두 번 계산한 좌표가 같고 화면 데이터와도 같음), view_node_overlap(Overview·View 좌표에서 node 상자 겹침 0), temporal_order·context_as_event(View 좌표에서도 날짜 순서·context lane 유지). W6 REJECTED는 4번 검사가 그대로 본다.

실행 시 빈 그래프 방지 검사(14): stale_asset_version(index.html이 싣는 css·js 주소의 `?v=`가 지금 파일 내용 해시와 같음 — 배포 직후 새 index.html이 브라우저 캐시의 옛 app.js와 섞이지 않게), dom_id_missing(app.js가 찾는 DOM id가 index.html 또는 app.js가 만드는 HTML에 모두 있음), runtime_failsafe_missing(초기화 예외 시 그래프 영역에 '시각화 초기화 오류'를 보여 주는 `AUDIT5:RUNTIME_GUARD`, 보이는 node 0이면 안내 후 Overview로 1회 복구하는 `AUDIT5:EMPTY_VIEW_GUARD`). 실제 브라우저 렌더(첫 화면·A–J 각 View에서 보이는 node가 화면 창과 겹치고 그래프 영역 픽셀이 비어 있지 않음, console·pageerror 0)는 `scripts/gusun_clean/test_visualization.py`가 검사한다.

### ERROR
_없음_

### WARN
_없음_

### UNRESOLVED
_없음_

### INFO
- `view_summary` **views** — View 10개(subset 8) 모두 canonical node·edge 부분집합, 좌표 결정적·겹침 0. node 글자 16px·line-height 1.6·첫 화면 배율 ≥ 0.95
- `ui_summary` **docs/data** — node 122 · edge 205 · 후보 38 · world 선택 7 · view 10 · 개입 행 13 · 공존 쌍 21 (canonical과 같음)
- `temporal_order` **layout** — 날짜 있는 관측 node 36개가 기준일 순서대로 왼쪽 → 오른쪽에 놓임. 날짜 미기록 node EP08는 시간 축 밖 '날짜 미기록' 구간에 두었다(위치가 날짜를 뜻하지 않음).
- `responsibility_to_biological` **view:death** — A branch 13개 · B branch 5개 node 사이 직접 edge 0개
- `frozen_graph_changed` **observed_dag** — 동결 해시 일치 ccb7ec63763a

## 화면 규칙(검사 대상)

- 배치: 물리 시뮬레이션 없는 preset 좌표. 날짜 있는 관측 node는 정렬 기준일(t_max, 없으면 t_min) 순서로 왼쪽 → 오른쪽, 같은 날짜 안에서는 frozen edge 깊이 순서. 시간 구간: 2월 → 3월 → 5월 → 6월 → 최종 판단·처분(6/13 이후 정조 판단·명령).
- 날짜 없는 node(메커니즘·구조 변수·후보·context·UNRESOLVED)는 별도 lane. x는 연결된 node 근처일 뿐 날짜가 아니다.
- world 선택(ALL·W1–W5·W6)은 worlds.json의 always_visible·dim·hideable·highlight 목록대로만 동작한다. 관측 node는 모든 선택에서 always_visible이고 app.js의 backbone 보호 규칙(`AUDIT5:BACKBONE_GUARD`)이 어떤 필터·world 선택·개입에서도 숨기지 않는다(관점별 View B–I의 범위 숨김은 아래 규칙).
- W6은 REJECTED 배너와 함께 표시되고 공존·개입 패널의 world 목록에 들어가지 않는다(canonical과 같음).
- 상태 필터와 메커니즘 필터는 화면 보이기/숨기기일 뿐 분석상 ON/OFF가 아니다. 개입 do(M=OFF)는 저장된 결과만 보여 준다.
- 관점별 View(views.json): A 전체 Overview(전체), B–I 관점별 View(subset: View 밖 node 숨김, 숨긴 OBSERVED 개수·ID 안내, '전체 주변 맥락 표시'로 Overview 좌표에 흐리게 다시 표시), J LATENT·World 비교(dim: 밖의 OBSERVED는 흐리게만). View는 node·edge 부분집합과 표시 좌표만 담는다. 필터·world·개입은 여전히 OBSERVED를 숨기지 못한다(BACKBONE_GUARD). subset View의 범위 숨김만 OBSERVED를 숨길 수 있고(`AUDIT5:VIEW_SCOPE`), 그때는 안내(`AUDIT5:VIEW_HIDDEN_NOTICE`)가 항상 보인다.
- 가독성: node label 16px(12pt)·line-height 1.6, UI 글자 15px(11.25pt) 이상·line-height 1.6. 모든 View의 첫 화면 배율 ≥ 0.95(node 글자 ≥ 15.2px). 그보다 작게 축소하면(전체 지도) node는 ID만 크게 표시한다. node 폭은 종류별 고정, 높이는 줄 수로 정하고, label은 자르지 않고 줄바꿈한다.

## Regression (Audit 5)

깨끗한 화면 데이터에서 ERROR 0을 확인한 뒤, 사본 하나만 바꿔 검사기에 넣었다. 기대한 check가 ERROR로 나와야 통과다.

| rule | 넣은 결함 | 결과 | 나온 ERROR |
|---|---|---|---|
| `ui_node_not_canonical` | 화면 데이터에 canonical에 없는 관측 사건 node(EP_NEW)를 추가 | 탐지 | count_mismatch, label_clipped, layout_nondeterministic, temporal_order, ui_node_not_canonical, view_node_overlap |
| `ui_edge_not_canonical` | 화면 데이터에 canonical에 없는 edge(CTX_F007 → EP09)를 추가 | 탐지 | count_mismatch, ui_edge_not_canonical |
| `status_changed` | LATENT 후보 G04a를 화면에서 OBSERVED로 표시 | 탐지 | status_changed, ui_node_altered |
| `w6_not_rejected` | W6을 화면에서 경쟁 설명(COMPETING_EXPLANATION)으로 표시하고 REJECTED 배너를 뺌 | 탐지 | unspecified_as_off, w6_not_rejected |
| `outcome_dropped` | W3 선택 시 공통 결말 EP33(구순 신지도 정배)을 숨김 대상으로 둠 | 탐지 | outcome_dropped |
| `unspecified_as_off` | W5의 M3(UNSPECIFIED)를 화면에서 OFF로 표시 | 탐지 | unspecified_as_off |
| `context_as_event` | 환경 context ENV03을 4/10 날짜 구간에 사건처럼 배치 | 탐지 | context_as_event, layout_nondeterministic |
| `environment_to_individual` | 환경 ENV03 → 김명신 구금 경과 후보 G06a edge를 화면에 추가 | 탐지 | count_mismatch, environment_to_individual, ui_edge_not_canonical |
| `responsibility_to_biological` | 책임 V_RESPONSIBILITY → 사인 판단 EP27 직접 edge를 화면에 추가 | 탐지 | count_mismatch, responsibility_to_biological, ui_edge_not_canonical |
| `temporal_order` | 3/4 체포 지시(EP09)와 6/13 최종 도난 판단(EP25)의 x 위치를 맞바꿈 | 탐지 | layout_nondeterministic, temporal_order |
| `candidate_grade_changed` | 화면에서 후보 G01a의 final grade를 MEDIUM → HIGH로 표시 | 탐지 | candidate_grade_changed |
| `intervention_changed` | 화면에서 do(M1=OFF)·V_COMPLAINT_TO_BARRACKS 결과를 PATH_BREAKS → PATH_REMAINS로 표시 | 탐지 | intervention_changed |
| `view_not_subset` | D 병영 지휘·체포 View에 canonical에 없는 edge(EP09 → EP33 직접 연결)를 추가 | 탐지 | view_not_subset |
| `view_not_subset` | C 구순→김명신 View에 canonical에 없는 node(EP_NEW)와 그 좌표를 추가 | 탐지 | layout_nondeterministic, ui_node_not_canonical, view_not_subset |
| `view_status_changed` | E 자미덕 View 좌표 항목에 G04b의 status를 OBSERVED로 적어 넣음 | 탐지 | layout_nondeterministic, view_status_changed |
| `view_hidden_notice_missing` | F 구금·사망 View의 '시각적 필터·삭제 아님' 안내를 빈 문자열로 바꿈 | 탐지 | view_hidden_notice_missing |
| `label_clipped` | EP13 node label을 '5월 12일 이형원 장계…'로 잘라 말줄임 표시 | 탐지 | label_clipped |
| `font_too_small` | 화면 CSS의 본문 글자 크기를 12px(9pt)로 줄임 | 탐지 | font_too_small |
| `line_height_too_small` | 화면 CSS의 기본 line-height를 1.3으로 줄임 | 탐지 | line_height_too_small |
| `initial_label_unreadable` | I 정조 최종 판단 View의 첫 화면 최소 배율을 0.5로 낮춤(글자 8px) | 탐지 | initial_label_unreadable |
| `view_node_overlap` | B 시간순 View에서 EP11 좌표를 EP09 위로 옮김 | 탐지 | layout_nondeterministic, view_node_overlap |
| `temporal_order` | H 홍대협 재조사 View에서 EP02(2/22)와 EP24(6/13)의 x를 맞바꿈 | 탐지 | layout_nondeterministic, temporal_order |
| `responsibility_to_biological` | F 구금·사망 View에서 책임 판단 EP29를 branch A(생물학적 사인) 묶음에도 넣음 | 탐지 | responsibility_to_biological |
| `dom_id_missing` | app.js가 index.html에 없는 #foot-note에 글자를 넣음(25f81b6 배포 직후 옛 app.js가 멈춘 그 줄) | 탐지 | dom_id_missing |
| `stale_asset_version` | index.html의 js/app.js 주소를 옛 내용 해시(?v=000000000000)로 둠 | 탐지 | stale_asset_version |
| `stale_asset_version` | index.html이 data/bundle.js를 버전 없이 실음(캐시된 옛 데이터와 섞일 수 있음) | 탐지 | stale_asset_version |
| `runtime_failsafe_missing` | index.html에서 '시각화 초기화 오류' 표시 guard를 뺌 | 탐지 | runtime_failsafe_missing |
| `runtime_failsafe_missing` | app.js에서 보이는 node 0 → Overview 복구 guard 호출을 뺌 | 탐지 | runtime_failsafe_missing |

## 생성 근거 파일 (sha256)

| 파일 | sha256 |
|---|---|
| `gusun_clean_restart_csv_pack/01_confirmed_facts.csv` | `868bb0b5ec3ca371…` |
| `gusun_clean_restart_csv_pack/02_institutional_normative_features.csv` | `d205145d5654c2d7…` |
| `gusun_clean_restart_csv_pack/03_environment_1793.csv` | `b989ada695297a31…` |
| `gusun_clean_restart_csv_pack/04_source_records.csv` | `f75a000299e1c7ea…` |
| `output/clean/episode_nodes.csv` | `ac81effa3ab94f0f…` |
| `output/clean/gaps.csv` | `746ece84c2ac80b0…` |
| `output/clean/latent_candidates.csv` | `169ca9dc7c63dbb7…` |
| `output/clean/mechanism_definitions.csv` | `5f67be713b4aaca7…` |
| `output/clean/mechanism_interaction_matrix.csv` | `3d172c98c7693dd8…` |
| `output/clean/mechanism_interventions.csv` | `be3fdc1ae907a81d…` |
| `output/clean/mechanism_super_dag_edges.csv` | `ccd5e144cc42f06d…` |
| `output/clean/mechanism_super_dag_nodes.csv` | `c219f115b1aa0c44…` |
| `output/clean/narrative_worlds.csv` | `7b1e50fe6e284aef…` |
| `output/clean/observed_dag_freeze.json` | `06aaed4147675a65…` |
| `output/clean/observed_edges.csv` | `6007babfa2e1638e…` |
| `output/clean/qualitative_structural_rules.csv` | `ca7d7ec15e0283a2…` |
| `output/clean/world_mechanism_configurations.csv` | `2f66ef0e2cff1065…` |

## 수정 이력

| 회차 | 발견 | 조치 |
|---|---|---|
| Stage 7 설계 | force-directed 배치는 실행마다 위치가 달라지고 시간 순서를 보장하지 못함. 화면 쪽에서 world별 숨김 규칙을 코드로만 두면 공통 결말이 사라져도 검사할 수 없음 | x·y를 Python(build_visualization.py)에서 결정적으로 계산하는 preset 배치로 고정하고(node 이동 불가), world 선택별 always_visible·dim·hideable 목록을 worlds.json에 데이터로 내보냄. Audit 5가 그 목록과 날짜 순서를 직접 검사 |
| 배치 규칙 검토(실행 전) | EP08(유제희 현지 탐문)은 t_min·t_max가 비어 있음. 2월·3월 사이 등 날짜 구간 안에 두면 날짜를 지어내는 셈 | '날짜 미기록' 구간(시간 축 밖, 빗금)에 따로 둠. Audit 5는 날짜 없는 관측 node가 날짜 구간에 들어가면 temporal_order ERROR |
| 배치 규칙 검토(실행 전) | 환경 context ENV01–ENV04는 기록일(1/22·4/10·5/12)이 있어 날짜 축에 놓기 쉬움 — 사건처럼 보일 위험 | 환경 context는 날짜 구간이 아닌 '환경 context' lane에 두고 date_key·band를 비움. 상세 패널에만 'context 기록일'로 표시. Audit 5 context_as_event 검사로 고정 |
| canonical 보강 | 개입 결과·구조 규칙이 md(mechanism_interventions.md·qualitative_structural_rules.md)에만 있어 화면이 md를 파싱해야 했음 | report_mech가 같은 sd·STRUCT_VARS 값으로 mechanism_interventions.csv·qualitative_structural_rules.csv를 추가로 씀(판단 변경 없음, 기존 파일은 바이트 동일) |
| regression 추가 | 요청된 Audit 5 regression 12건(새 node, 새 edge, 상태 변경, W6 재활성, 공통 결말 숨김, UNSPECIFIED→OFF, context의 사건화, 환경→개인 감염, 책임→생물학 사인, 시간 순서 역전, 후보 등급 변경, 개입 결과 변경) | 깨끗한 화면 데이터에서 ERROR 0을 먼저 확인한 뒤 사본만 바꿔 넣음. 12건 모두 기대한 check가 ERROR로 잡힘 |
| 1차 실행·화면 확인 | ERROR 0, WARN 0. 헤드리스 브라우저 스크린샷에서 축소 화면의 구조 변수 ID 라벨이 서로 겹침 | 축소 시 라벨 줄바꿈(text-overflow-wrap)과 글자 크기를 node 종류별로 조정, column 간격 조정. 데이터·판단 변경 없음 |
| UI 테스트 1차 | 20항목 중 3항목 FAIL. world 패널의 OFF 검사가 설명 문구('UNSPECIFIED ≠ OFF')까지 셌고, cytoscape visible()이 렌더 전 값을 캐시해 필터 직후의 숨김을 읽지 못함(화면 자체는 정상) | 테스트가 표시 값(chip)과 계산된 display style을 읽도록 고침. 화면 코드·데이터 변경 없음. 재실행 20/20 PASS |
| 화면 확인 2차 | 개입 패널의 6열 표가 오른쪽 패널 폭을 넘어 잘리고, 공존 패널의 두 번째 선택 상자가 잘림 | 개입 결과를 구조 변수별 카드(관측 대상·사라지는 후보·남는 후보·영향 world·설명)로 바꾸고 선택 상자 폭을 유연하게 함. 값은 canonical 그대로 |
| 최종 실행 | Audit 5 ERROR 0, WARN 0, UNRESOLVED 0, INFO 4. regression 48/48 탐지, UI 테스트 20/20 PASS | PASS. 동결 해시 ccb7ec63763a 그대로, 기존 canonical CSV·md는 바이트 동일(새 파일 3개와 validation_summary.md만 추가·변경) |
| 가독성·분할 개선(설계) | Overview가 첫 화면에서 약 0.2배로 축소되어 node ID만 보였고 node label 11px·UI 글자 11–13px·line-height 1.4–1.5였다. View 4개는 범위 밖 OBSERVED를 흐리게만 남겨 화면이 복잡했다 | View를 A 전체 Overview·B 시간순 사건·C 구순→김명신 수사선상·D 병영 지휘·체포·E 자미덕·진술·대질·F 김명신 구금·사망·G 5월 재검토·H 홍대협 재조사·I 정조 최종 판단·처분·J LATENT·World 비교 10개로 다시 나눔. View는 canonical node·edge 부분집합과 표시 좌표만 담고(새 inference 없음) subset View는 범위 밖 node를 숨기되 숨긴 OBSERVED 개수·ID와 '시각적 필터' 안내를 늘 보여 줌. node label 16px·UI 15px·line-height 1.6, label 전체를 줄바꿈해 node 크기를 정하고, 첫 화면 배율 하한 0.95. 같은 규칙으로 View마다 결정적 좌표를 다시 계산 |
| 가독성·분할 개선(검사 추가) | 새 화면 규칙을 검사할 수단이 없었음 | Audit 5에 view_not_subset·view_status_changed·view_hidden_notice_missing·label_clipped·font_too_small·line_height_too_small·initial_label_unreadable·layout_nondeterministic·view_node_overlap과 View 좌표의 temporal_order·context_as_event·A/B 검사를 추가. regression 11건 추가(59건), UI 테스트 27항목(computed font·line-height, 렌더된 label 잘림·node 겹침, 첫 화면 배율, 검색 이동, 스크롤·끌기·미니맵, 420px) |
| 화면 확인(가독성 개선 1차) | 헤드리스 스크린샷: 1600px에서 그래프 영역이 머리글·배너에 밀려 520px 정도, 오른쪽 아래 확대 버튼과 미니맵이 node를 가림. 긴 같은 lane edge(OE007, 2/29 → 6/13)가 다른 edge(OE008)와 겹쳐 클릭이 엉뚱한 edge로 감 | 확대 버튼을 그래프 위 도구 막대로 옮기고 안내 문구를 한 줄로 줄임, 미니맵 끄기 버튼 추가. 직선이 다른 node 상자를 지나는 edge는 정해진 순서의 곡률 후보 중 상자를 피하는 가장 작은 값으로 곡선 처리(좌표에서 결정적으로 계산) |
| 화면 확인(가독성 개선 2차) | H 홍대협 재조사 View는 맥락 node EP02(2/22) 때문에 첫 화면이 빈 2월 구간에서 시작. lane 이름 칸이 화면 밖으로 나가면 lane을 알 수 없음 | 첫 화면 기준점을 View 핵심 관측 node 앞으로 옮기고, 시간상 앞쪽 창에 핵심 node가 2개 미만일 때만 핵심 node가 가장 많이 들어오는 창을 고름. lane 이름·시간 구간 이름이 화면 밖으로 나가면 그래프 가장자리에 고정 표시(HTML, 11pt 이상) |
| 최종 실행(가독성 개선) | Audit 1–5 ERROR 0·WARN 0, regression 59/59, UI 테스트 27/27 | PASS. 동결 해시 ccb7ec63763a 그대로, canonical CSV·json·md(output/clean)는 audit_5·validation_summary 문서 말고 바이트 동일 |
| 배포 화면 빈 그래프(25f81b6) | 배포된 화면에서 머리글 node 122·edge 205만 보이고 그래프·Status·Mechanism 필터·상세 패널이 모두 빔. 재현: 새 index.html + 브라우저 캐시의 옛 app.js(7ea077b)에서 pageerror 'Cannot set properties of null (setting textContent)' — 옛 app.js가 머리글을 그린 직후 새 index.html에서 없어진 #foot-note에 글자를 넣다가 멈춰 cytoscape 생성·필터·상세가 실행되지 않음. css·js 주소에 버전이 없어 GitHub Pages 캐시(max-age 600) 동안 새 HTML과 옛 JS가 섞임. 기존 UI 테스트는 같은 버전 파일만 열고 머리글 글자만 확인해 이 실패를 볼 수 없었음 | index.html의 css·js 주소에 내용 해시 ?v=를 붙이고 build_visualization.stamp_assets가 build마다 맞춤. 초기화 예외 시 그래프 영역에 '시각화 초기화 오류'(AUDIT5:RUNTIME_GUARD), 보이는 node 0이면 안내 후 Overview 1회 복구(AUDIT5:EMPTY_VIEW_GUARD). Audit 5에 stale_asset_version·dom_id_missing·runtime_failsafe_missing 검사, regression 5건(64건), UI 테스트에 실제 렌더 검사 4항목(31항목: 첫 로드 cy·보이는 node·화면 창 교차·canvas 픽셀·스크린샷 흰색 비율·필터 UI·View 탭·오류 0, A–J View별 렌더, 옛 app.js 재현 시 오류 안내, 빈 View 복구). 데이터·판단·배치 변경 없음 |
