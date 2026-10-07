# AUDIT 4 — Mechanism Super-DAG

핵심 질문: **메커니즘 Super-DAG가 관측 사실을 바꾸거나, context로 사건을 만들거나, world·branch를 섞었는가?**

- 판정: **PASS** (ERROR 0 · WARN 0 · UNRESOLVED 20 · INFO 2)

## 자동 검사 요약

| check | ERROR | WARN | UNRESOLVED | INFO |
|---|---|---|---|---|
| coexistence_undetermined | 0 | 0 | 2 | 0 |
| frozen_graph_changed | 0 | 0 | 0 | 1 |
| interaction_direction | 0 | 0 | 8 | 0 |
| multiple_explanations | 0 | 0 | 4 | 0 |
| super_dag_summary | 0 | 0 | 0 | 1 |
| unresolved_item | 0 | 0 | 6 | 0 |
| **합계** | **0** | **0** | **20** | **2** |

ERROR 검사: frozen_graph_changed, context_to_fact(새 관측 node 포함), observed_to_latent, latent_to_observed, world_latent_promoted, institution_to_event, environment_to_personal_fact, context_to_fact, causal_inflation, responsibility_to_biological, incompatible_coexistence, w6_reactivation, off_mechanism_alive, unspecified_as_off, config_value, world_merge, outcome_world_dependency, dangling_edge.

UNRESOLVED(사료가 결정하지 않음, 허용): coexistence_undetermined, interaction_direction, multiple_explanations, unresolved_item.

### ERROR
_없음_

### WARN
_없음_

### UNRESOLVED
- `interaction_direction` **M1×M2** — 함께 쓰이는 world(W2)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음
- `interaction_direction` **M1×M3** — 함께 쓰이는 world(W1, W3)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음
- `interaction_direction` **M1×M4** — 함께 쓰이는 world(W1, W2, W4)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음
- `interaction_direction` **M1×M6** — 함께 쓰이는 world(W1, W3, W5)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음
- `coexistence_undetermined` **M2×M3** — COMPATIBLE — 충돌 근거는 없지만 어느 경쟁 world도 둘을 함께 쓰지 않아, 함께 작동했는지는 사료로 결정되지 않음
- `interaction_direction` **M2×M4** — 함께 쓰이는 world(W2, W4)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음
- `interaction_direction` **M2×M6** — 함께 쓰이는 world(W2)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음
- `coexistence_undetermined` **M3×M4** — COMPATIBLE — 충돌 근거는 없지만 어느 경쟁 world도 둘을 함께 쓰지 않아, 함께 작동했는지는 사료로 결정되지 않음
- `interaction_direction` **M3×M6** — 함께 쓰이는 world(W1, W3)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음
- `interaction_direction` **M4×M6** — 함께 쓰이는 world(W1, W2, W4)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음
- `multiple_explanations` **V_COMMAND_SOURCE** — XOR: M1, M4가 같은 관측 전이(EP04)를 설명할 수 있음. 어느 쪽이 실제로 작동했는지는 사료로 결정되지 않음
- `multiple_explanations` **V_INFO_TO_COMMANDER** — OR: M1, M2, M3, M4가 같은 관측 전이(EP09)를 설명할 수 있음. 어느 쪽이 실제로 작동했는지는 사료로 결정되지 않음
- `multiple_explanations` **V_INVESTIGATION_SCOPE** — OR: M2, M4가 같은 관측 전이(EP11)를 설명할 수 있음. 어느 쪽이 실제로 작동했는지는 사료로 결정되지 않음
- `multiple_explanations` **V_INITIAL_JUDGMENT_BASIS** — OR: M2, M6가 같은 관측 전이(EP15)를 설명할 수 있음. 어느 쪽이 실제로 작동했는지는 사료로 결정되지 않음
- `unresolved_item` **U_ID06** — ID06 병영의 염탐 담당자 = 유제희?
- `unresolved_item` **U_ID07** — ID07 철편 네 개 = 철퇴 네 개?
- `unresolved_item` **U_ID08** — ID08 3/4 장교 일행에 조계완 포함?
- `unresolved_item` **U_OE007** — OE007 자미덕 '지휘' 주장 ↔ 한재욱 '은밀한 사주' 부인 (PARTIAL_CONFLICT)
- `unresolved_item` **U_OE062** — OE062 5월 '조사' = 정조 '평범한 신문'? (UNRESOLVED_SCOPE)
- `unresolved_item` **U_G10** — G10 이형원 파직 → 유임 이유 (OPEN_UNRESOLVED)

### INFO
- `super_dag_summary` **super_dag** — node CONTEXT 24, LATENT_MECHANISM 55, OBSERVED 37, UNRESOLVED 6 · edge CONTEXT 38, DERIVED 64, LATENT_MECHANISM 90, OBSERVED 4, UNRESOLVED 9
- `frozen_graph_changed` **observed_dag** — 동결 해시 일치 ccb7ec63763a

UNRESOLVED는 오류가 아니다. 사료가 결정하지 않는 것(어느 메커니즘이 실제로 작동했는지, 함께 작동했는지, 방향)과 사용자가 열어 두기로 한 항목(ID06·ID07·ID08·OE007·OE062·G10)이다. WARN으로 두지 않았다.

## Regression (Audit 4)

깨끗한 Super-DAG에서 ERROR 0을 확인한 뒤, 사본 하나만 바꿔 검사기에 넣었다. 기대한 check가 ERROR로 나와야 통과다.

| rule | 넣은 결함 | 결과 | 나온 ERROR |
|---|---|---|---|
| `context_to_fact` | context(F013 암행어사 제도)에서 새 관측 사건 node를 만듦 | 탐지 | context_to_fact, institution_to_event |
| `environment_to_personal_fact` | 환경(ENV03 전염병)을 김명신 구금 경과 후보(G06a)에 직접 연결 | 탐지 | environment_to_personal_fact |
| `institution_to_event` | 제도 가능성(F007 병사 지휘권)이 3/4 체포 지시(EP09)를 직접 만듦 | 탐지 | institution_to_event |
| `world_merge` | 상충 후보 G03b를 W2(G04b 사용)에 섞음 | 탐지 | world_merge |
| `w6_reactivation` | REJECTED W6을 경쟁 설명으로 되살리고 공존 분석에 넣음 | 탐지 | w6_reactivation |
| `responsibility_to_biological` | 책임 구조 변수(V_RESPONSIBILITY) → 사인 판단(EP27) 직접 edge | 탐지 | responsibility_to_biological |
| `off_mechanism_alive` | W1에서 M1=OFF로 바꿨는데 M1 후보(G01a·G02a·G03a·G04a)가 그대로 살아 있음 | 탐지 | off_mechanism_alive, unspecified_as_off |
| `unspecified_as_off` | W5의 M3(관련 후보 없음, UNSPECIFIED)를 OFF로 표기 | 탐지 | unspecified_as_off |
| `world_latent_promoted` | W1 전용 후보 G04a를 모든 world 공통 사실로 표시 | 탐지 | world_latent_promoted |
| `outcome_world_dependency` | 확정 처분(EP33 구순 정배)을 W1에만 속한 결과로 표시 | 탐지 | outcome_world_dependency |

## 수정 이력

| 회차 | 발견 | 조치 |
|---|---|---|
| Stage 6 설계 | 메커니즘 M1–M5만으로는 G07 계열(5월 판단 근거)과 G06·G12 계열(구금·질병 경과)을 담을 곳이 없음 | 기존 후보를 묶기만 해서 M6_INITIAL_JUDGMENT_BASIS와 MB_CUSTODY_BIOLOGICAL_COURSE를 추가. 새 후보·사건·등급 변경 없음 |
| configuration 규칙 검토(실행 전) | 부정 후보(G02b·G05b·G13b)만 있는 world를 OFF로, 후보가 없는 world도 OFF로 읽을 위험 | OFF는 '부정 후보만 있음', UNSPECIFIED는 '관련 후보 없음'으로 분리. 내용상 '작동하지 않았다'는 주장만 하는 G05b·G11c·G13b는 null variant로 두어 공존·개입 분석의 근거에서 뺌 |
| 공존 규칙 검토(실행 전) | 두 메커니즘이 한 world에서 모두 PARTIAL이기만 해도 '함께 쓰인다'로 셈 | 함께 쓰임은 적어도 한쪽이 ON일 때만 인정. 함께 쓰는 world가 없으면 COMPATIBLE이라도 UNRESOLVED(coexistence_undetermined)로 기록 |
| 1차 실행 | ERROR 0, WARN 0. 수동 검토에서 mechanism → investigation·review Mermaid의 관측 edge 일부를 손으로 쓴 것이 frozen edge와 다름을 발견(EP15→EP18, EP23→EP25 등은 frozen graph에 없음. 실제는 EP17 REVIEW_OF EP18, EP24 REVIEW_OF EP25) | Mermaid 패널을 mechanism_super_dag_edges.csv에서 생성하도록 바꿈(관측 edge는 frozen type 그대로). 손으로 쓴 edge 0 |
| 검사기 보강 | frozen graph에 없는 관측 사건 node가 Super-DAG에 새로 생겨도 잡는 검사가 없었고, W6의 role_type을 바꾸면 되살아나도 모름 | context_to_fact에 '새 관측 node 생성'을 추가, WORLD_ROLES에서 REJECTED로 정한 world가 다른 role로 바뀌면 w6_reactivation ERROR |
| regression 추가 | 요청된 Audit 4 regression 10건(context→사실, 환경→개인 감염, 제도→사건, world 병합, W6 재활성, 책임→생물학 사인, OFF인데 후보 생존, UNSPECIFIED를 OFF로, world 전용 LATENT 공통화, 결말의 world 종속) | 깨끗한 Super-DAG에서 ERROR 0을 먼저 확인한 뒤 사본만 바꿔 넣음. 10건 모두 ERROR로 잡힘(전체 36/36) |
| 2차 실행 | ERROR 0, WARN 0, UNRESOLVED 20(방향 미결 8, 공존 미결 2, 복수 설명 4, 기존 미해결 6), INFO 2 | PASS. 동결 해시 ccb7ec63763a 그대로 |
