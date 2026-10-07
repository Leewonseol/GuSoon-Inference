# AUDIT 5 — Interactive Visualization (Temporal DAG)

핵심 질문: **탐색용 화면 데이터(docs/data)가 canonical 산출물을 바꾸거나, context·LATENT를 사건처럼 보이게 하거나, 시간 순서·world 결말을 깨뜨렸는가?**

- 판정: **PASS** (ERROR 0 · WARN 0 · UNRESOLVED 0 · INFO 4)
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
| **합계** | **0** | **0** | **0** | **4** |

ERROR 검사: ui_node_not_canonical·ui_node_missing·ui_node_altered(1), ui_edge_not_canonical·ui_edge_missing·ui_edge_altered(2), status_changed(3), w6_not_rejected(4), outcome_dropped(5), unspecified_as_off(6), context_as_event(7), environment_to_individual(8), responsibility_to_biological(9), temporal_order(10), candidate_grade_changed(11), intervention_changed(12), 그리고 count_mismatch·frozen_graph_changed·stale_ui_data·bundle_mismatch·interaction_changed.

### ERROR
_없음_

### WARN
_없음_

### UNRESOLVED
_없음_

### INFO
- `ui_summary` **docs/data** — node 122 · edge 205 · 후보 38 · world 선택 7 · view 4 · 개입 행 13 · 공존 쌍 21 (canonical과 같음)
- `temporal_order` **layout** — 날짜 있는 관측 node 36개가 기준일 순서대로 왼쪽 → 오른쪽에 놓임. 날짜 미기록 node EP08는 시간 축 밖 '날짜 미기록' 구간에 두었다(위치가 날짜를 뜻하지 않음).
- `responsibility_to_biological` **view:death** — A branch 13개 · B branch 12개 node 사이 직접 edge 0개
- `frozen_graph_changed` **observed_dag** — 동결 해시 일치 ccb7ec63763a

## 화면 규칙(검사 대상)

- 배치: 물리 시뮬레이션 없는 preset 좌표. 날짜 있는 관측 node는 정렬 기준일(t_max, 없으면 t_min) 순서로 왼쪽 → 오른쪽, 같은 날짜 안에서는 frozen edge 깊이 순서. 시간 구간: 2월 → 3월 → 5월 → 6월 → 최종 판단·처분(6/13 이후 정조 판단·명령).
- 날짜 없는 node(메커니즘·구조 변수·후보·context·UNRESOLVED)는 별도 lane. x는 연결된 node 근처일 뿐 날짜가 아니다.
- world 선택(ALL·W1–W5·W6)은 worlds.json의 always_visible·dim·hideable·highlight 목록대로만 동작한다. 관측 node는 모든 선택에서 always_visible이고 app.js의 backbone 보호 규칙(`AUDIT5:BACKBONE_GUARD`)이 어떤 필터·view·개입에서도 숨기지 않는다.
- W6은 REJECTED 배너와 함께 표시되고 공존·개입 패널의 world 목록에 들어가지 않는다(canonical과 같음).
- 상태 필터와 메커니즘 필터는 화면 보이기/숨기기일 뿐 분석상 ON/OFF가 아니다. 개입 do(M=OFF)는 저장된 결과만 보여 준다.

## Regression (Audit 5)

깨끗한 화면 데이터에서 ERROR 0을 확인한 뒤, 사본 하나만 바꿔 검사기에 넣었다. 기대한 check가 ERROR로 나와야 통과다.

| rule | 넣은 결함 | 결과 | 나온 ERROR |
|---|---|---|---|
| `ui_node_not_canonical` | 화면 데이터에 canonical에 없는 관측 사건 node(EP_NEW)를 추가 | 탐지 | count_mismatch, temporal_order, ui_node_not_canonical |
| `ui_edge_not_canonical` | 화면 데이터에 canonical에 없는 edge(CTX_F007 → EP09)를 추가 | 탐지 | count_mismatch, ui_edge_not_canonical |
| `status_changed` | LATENT 후보 G04a를 화면에서 OBSERVED로 표시 | 탐지 | status_changed, ui_node_altered |
| `w6_not_rejected` | W6을 화면에서 경쟁 설명(COMPETING_EXPLANATION)으로 표시하고 REJECTED 배너를 뺌 | 탐지 | unspecified_as_off, w6_not_rejected |
| `outcome_dropped` | W3 선택 시 공통 결말 EP33(구순 신지도 정배)을 숨김 대상으로 둠 | 탐지 | outcome_dropped |
| `unspecified_as_off` | W5의 M3(UNSPECIFIED)를 화면에서 OFF로 표시 | 탐지 | unspecified_as_off |
| `context_as_event` | 환경 context ENV03을 4/10 날짜 구간에 사건처럼 배치 | 탐지 | context_as_event |
| `environment_to_individual` | 환경 ENV03 → 김명신 구금 경과 후보 G06a edge를 화면에 추가 | 탐지 | count_mismatch, environment_to_individual, ui_edge_not_canonical |
| `responsibility_to_biological` | 책임 V_RESPONSIBILITY → 사인 판단 EP27 직접 edge를 화면에 추가 | 탐지 | count_mismatch, responsibility_to_biological, ui_edge_not_canonical |
| `temporal_order` | 3/4 체포 지시(EP09)와 6/13 최종 도난 판단(EP25)의 x 위치를 맞바꿈 | 탐지 | temporal_order |
| `candidate_grade_changed` | 화면에서 후보 G01a의 final grade를 MEDIUM → HIGH로 표시 | 탐지 | candidate_grade_changed |
| `intervention_changed` | 화면에서 do(M1=OFF)·V_COMPLAINT_TO_BARRACKS 결과를 PATH_BREAKS → PATH_REMAINS로 표시 | 탐지 | intervention_changed |

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
