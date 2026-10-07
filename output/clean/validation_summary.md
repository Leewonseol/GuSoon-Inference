# Validation Summary

통과 조건: 각 Audit의 ERROR = 0, WARN = 0. INFO와 UNRESOLVED는 허용하되, UNRESOLVED는 사료 자체의 불확실성 때문에 남은 것이어야 한다.

```
Audit 1:
ERROR = 0
WARN = 0
INFO = 13
UNRESOLVED = 4

Audit 2:
ERROR = 0
WARN = 0
INFO = 1
UNRESOLVED = 5

Audit 3:
ERROR = 0
WARN = 0
INFO = 11
UNRESOLVED = 1

Audit 4:
ERROR = 0
WARN = 0
INFO = 2
UNRESOLVED = 20

Audit 5:
ERROR = 0
WARN = 0
INFO = 5
UNRESOLVED = 0

```

판정: **PASS**

## WARN disposition 집계

| disposition | 건수 | 항목 |
|---|---|---|
| FIXED | 5 | A1-W1, A1-W2, A1-W3, A1-W4, A3-W1 |
| RECLASSIFIED_INFO | 0 | - |
| UNRESOLVED | 0 | - |
| ESCALATED_ERROR | 1 | A1-E1 |

## 동일성 상태

RESOLVED(사용자 확정) 5개 · UNRESOLVED 4개 (그중 사용자 판단 필요 0개) · 기타 2개

| ID | 동일성 | status | 모델 사용처 | 사용자 판단 필요 | 검토 결정 |
|---|---|---|---|---|---|
| ID01 | 공초의 '병사' (CF021·CF023·CF024) ↔ 이광섭 | RESOLVED | 조건부 사용 없음(RESOLVED) | NO | RESOLVED_BY_USER |
| ID02 | '한 비장' (CF016·CF017) ↔ 한재욱 | RESOLVED | 조건부 사용 없음(RESOLVED); 확정과 충돌해 PRUNED된 후보: G09b | NO | RESOLVED_BY_USER |
| ID03 | 처분문의 '한가' (CF048) ↔ 한재욱 | RESOLVED | 조건부 사용 없음(RESOLVED); 확정과 충돌해 PRUNED된 후보: G09c | NO | RESOLVED_BY_USER |
| ID04 | '병영의 하급 보조자' (audit-only V3P0026·V3P0027·V3P0124) ↔ 한재욱 | UNRESOLVED | NONE | NO | REFERENCE_ONLY (모델 미사용) |
| ID05 | '풍각 김상제' (CF020) ↔ 김명신 | RESOLVED | 조건부 사용 없음(RESOLVED) | NO | RESOLVED_BY_USER |
| ID06 | '병영의 염탐 담당자' (CF043) ↔ 유제희 | UNRESOLVED | OE071, G04a, W1 | NO | KEEP_UNRESOLVED (사용자 수동 검토: 추가 사료 없이 확정하지 않고 현재 불확실성 유지) |
| ID07 | '철편 네 개' (CF010, 이진욱: 한재욱이 만들어 줌) ↔ '철퇴 네 개' (CF044, 정조: 이광섭이 만들게 함) | UNRESOLVED | OE080, G02a, W1, W3 | NO | KEEP_UNRESOLVED (사용자 수동 검토: 추가 사료 없이 확정하지 않고 현재 불확실성 유지) |
| ID08 | 3/4 '장교 일행' (CF023) ↔ 조계완 포함 여부 (CF024) | UNRESOLVED | OE010 | NO | KEEP_UNRESOLVED (사용자 수동 검토: 추가 사료 없이 확정하지 않고 현재 불확실성 유지) |
| ID09 | CF030 '당시 장계' ↔ 이형원 5/12 장계(CF027) | ACCEPTED_BY_PROVENANCE | OE040 | NO |  |
| ID10 | 풍각 김생원 / 흥덕 김생원 ↔ 김명신 / 김갑득 | DOCUMENTED | NONE | NO |  |
| ID11 | '원돌' (CF020 '원돌 등의 이름') ↔ 정원돌 (CF009·CF016) | RESOLVED | 조건부 사용 없음(RESOLVED) | NO | RESOLVED_BY_USER |

## LATENT 후보 재감사 (bridge 자체의 사료 근거)

- source support: HIGH 0 · MEDIUM 7 · LOW 18 · NONE 13
- final grade: HIGH 0 · MEDIUM 7 · LOW 28 · INCOMPATIBLE 3
- source support가 바뀐 후보 30개, final이 바뀐 후보 16개. 상세: `latent_candidate_reaudit.md`
- 검사: bridge_support_inflation · temporal_inflation · institutional_inflation · endpoint_leakage · latent_classification (모두 ERROR 0)

## UNRESOLVED 목록

### Audit 1

- `unresolved_identity` **ID04** — '병영의 하급 보조자' (audit-only V3P0026·V3P0027·V3P0124) ↔ 한재욱 · 관련 episode 없음(DAG 미사용) · 참고용(model_relevance=NONE, manual_decision_required=NO) · unresolved_reason: audit-only 자료(05, 이조원 주장)에만 있고 인명이 직접 나오지 않는다. 현재 DAG·후보·world 어디에도 쓰이지 않아 결정해도 모델 결과가 바뀌지 않는다(참고용 미해결).
- `unresolved_identity` **ID06** — '병영의 염탐 담당자' (CF043) ↔ 유제희 · 관련 episode EP08, EP29 · unresolved_reason: 정조 판단(CF043)은 직책 표현('병영의 염탐 담당자')만 쓰고 이름을 적지 않았다.
- `unresolved_identity` **ID07** — '철편 네 개' (CF010, 이진욱: 한재욱이 만들어 줌) ↔ '철퇴 네 개' (CF044, 정조: 이광섭이 만들게 함) · 관련 episode EP04, EP30 · unresolved_reason: 개수(네 개)와 사건은 같지만 물건 이름(철편/철퇴)과 행위 층위(제작·지급/제작 지시)가 다르다.
- `unresolved_identity` **ID08** — 3/4 '장교 일행' (CF023) ↔ 조계완 포함 여부 (CF024) · 관련 episode EP04, EP10, EP11 · unresolved_reason: 3/4 '장교 일행'의 구성원은 기록되지 않았다.

### Audit 2

- `partial_tension` **OE007** — PARTIAL_CONFLICT — 원문 표현의 범위가 같은지 사료로 확정할 수 없어 보존 · review_decision: 사용자 검토: 정면 충돌로 승격하지 않음. 자미덕의 '지휘' 주장과 한재욱의 '은밀한 사주' 부인은 범위가 완전히 같지 않다. · unresolved_reason: '한 비장'=한재욱은 ID02 사용자 확정(RESOLVED)이라 같은 인물에 대한 두 진술이다. 사주 주장(자미덕)과 은밀한 사주 부인(한재욱)은 서로 다른 진술로 유지하며 어느 쪽도 객관적 사실로 확정하지 않는다. 한재욱의 부인 범위는 '은밀한 사주'에 한정되므로 PARTIAL 충돌이다.
- `conditional_edge` **OE010** — ID08 미확정 — edge는 condition으로만 성립 · unresolved_reason: 3/4 '장교 일행'의 구성원은 기록되지 않았다.
- `partial_tension` **OE062** — UNRESOLVED_SCOPE — 원문 표현의 범위가 같은지 사료로 확정할 수 없어 보존 · review_decision: 사용자 검토: 5월 장계의 '조사'와 정조의 '평범한 신문'이 같은 범위인지 확정하지 않음. 부분 긴장 유지. · unresolved_reason: PARTIAL_TENSION: '조사'가 곧 '신문'이라고 확정할 수 없다. CF028의 '무고한 평민들 모진 형벌'은 김명신 포함 여부가 열린 집합이므로 충돌 근거로 쓰지 않는다.
- `conditional_edge` **OE071** — ID06 미확정 — edge는 condition으로만 성립 · unresolved_reason: 정조 판단(CF043)은 직책 표현('병영의 염탐 담당자')만 쓰고 이름을 적지 않았다.
- `conditional_edge` **OE080** — ID07 미확정 — edge는 condition으로만 성립 · unresolved_reason: 개수(네 개)와 사건은 같지만 물건 이름(철편/철퇴)과 행위 층위(제작·지급/제작 지시)가 다르다.

### Audit 3

- `unresolved_gap` **G10** — OPEN_UNRESOLVED — 어느 경쟁 설명 world도 이 gap을 메우지 않음 (후보 G10a=MEDIUM, G10b=LOW, G10c=LOW) · review_decision: 사용자 검토: latent bridge를 채택하지 않음. 이유를 억지로 채우지 않고 gap을 열어 둔다(world에서도 비움). · unresolved_reason: 파직과 3일 뒤 유임의 사유가 모두 기록되지 않았다. 관측 근거(CF049, CF050)에 사유를 적은 문장이 없음

### Audit 4

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

### Audit 5

_없음_

## Regression validation rules

build.py는 Audit 1 전에 아래 케이스를 검사기에 넣어 모두 ERROR로 잡히는지 확인한다(64/64 탐지).

| rule | 케이스 | 탐지 |
|---|---|---|
| epistemic_marker_deletion | A1-W1 원안 EP01: 진술 3건을 '명업의 진술에 따르면' 하나로 합침 | OK |
| testimony_to_fact | A1-E1 원안 EP07: '자미덕의 진술에 따르면 … 거짓으로 꾸며 말했다' | OK |
| actor_substitution | A1-W2 원안 EP04: '자신'을 '이진욱'으로 치환 | OK |
| actor_substitution | 진술자 바꿔치기: EP12의 한재욱 공초를 자미덕 진술로 | OK |
| semantic_weakening | '은밀히' 삭제: 어떤 사주도 없었다 | OK |
| surface_form_substitution | 확정 동일성(ID01)이라도 episode summary에서 '병사'를 이광섭으로 바꾸면 안 됨(EP09) | OK |
| surface_form_substitution | 확정 동일성(ID02)이라도 episode summary에서 '한 비장'을 한재욱으로 바꾸면 안 됨(EP07) | OK |
| surface_form_substitution | 확정 동일성(ID05)이라도 episode summary에서 '풍각 김상제'를 김명신으로 바꾸면 안 됨(EP08) | OK |
| identity_forcing | 미확정 동일성(ID06) 강제: '병영의 염탐 담당자'를 유제희로 치환(EP29) | OK |
| stale_identity_condition | 사용자 확정 동일성(ID01)이 edge condition에 남아 있음(OE081) | OK |
| resolved_identity_conflict | 확정 동일성(ID02)을 불성립으로 전제한 후보(G09b)가 INCOMPATIBLE이 아님 | OK |
| open_gap_filled | 사용자가 열어 두기로 한 G10을 world가 채움 | OK |
| bridge_support_inflation | 재감사 이전 G08a: 동기 bridge 근거 없음(NO)인데 source_support=HIGH | OK |
| temporal_inflation | 시간 인접·endpoint 내용만으로 동기 bridge를 MEDIUM 이상으로 평가(G08a) | OK |
| institutional_inflation | 제도 가능성만으로 source_support=MEDIUM(G01c) | OK |
| endpoint_leakage | endpoint 구성 fact(CF033·CF035)를 bridge 근거로 인용(G08a) | OK |
| bridge_support_inflation | 재감사 이전 값 전체(source_consistency_v1)를 다시 넣으면 검사가 잡는지 | OK |
| outcome_world_dependency | 확정 처분(구순 정배)을 특정 world의 결과로 서술 | OK |
| closed_set | '등' 삭제(EP07) | OK |
| semantic_strengthening | '극히 수상하다' → 범인 지목(EP08) | OK |
| responsibility_to_causation | 책임 판단을 직접 사인으로(EP29) | OK |
| environment_to_individual_fact | 환경을 개인 사인으로(EP27) | OK |
| occurrence_record_confusion | 기록일(6/13)을 진술 내용의 발생 시점으로 사용(EP06) | OK |
| latent_as_observed | A3-W1 원안 G08a: 관측 node 사이 직접 latent edge | OK |
| open_set_closure | world 서술에서 열린 명단의 '등' 삭제 | OK |
| environment_to_individual_fact | 후보·world 서술: 환경 → 개인 감염 단정 | OK |
| context_to_fact | context(F013 암행어사 제도)에서 새 관측 사건 node를 만듦 | OK |
| environment_to_personal_fact | 환경(ENV03 전염병)을 김명신 구금 경과 후보(G06a)에 직접 연결 | OK |
| institution_to_event | 제도 가능성(F007 병사 지휘권)이 3/4 체포 지시(EP09)를 직접 만듦 | OK |
| world_merge | 상충 후보 G03b를 W2(G04b 사용)에 섞음 | OK |
| w6_reactivation | REJECTED W6을 경쟁 설명으로 되살리고 공존 분석에 넣음 | OK |
| responsibility_to_biological | 책임 구조 변수(V_RESPONSIBILITY) → 사인 판단(EP27) 직접 edge | OK |
| off_mechanism_alive | W1에서 M1=OFF로 바꿨는데 M1 후보(G01a·G02a·G03a·G04a)가 그대로 살아 있음 | OK |
| unspecified_as_off | W5의 M3(관련 후보 없음, UNSPECIFIED)를 OFF로 표기 | OK |
| world_latent_promoted | W1 전용 후보 G04a를 모든 world 공통 사실로 표시 | OK |
| outcome_world_dependency | 확정 처분(EP33 구순 정배)을 W1에만 속한 결과로 표시 | OK |
| ui_node_not_canonical | 화면 데이터에 canonical에 없는 관측 사건 node(EP_NEW)를 추가 | OK |
| ui_edge_not_canonical | 화면 데이터에 canonical에 없는 edge(CTX_F007 → EP09)를 추가 | OK |
| status_changed | LATENT 후보 G04a를 화면에서 OBSERVED로 표시 | OK |
| w6_not_rejected | W6을 화면에서 경쟁 설명(COMPETING_EXPLANATION)으로 표시하고 REJECTED 배너를 뺌 | OK |
| outcome_dropped | W3 선택 시 공통 결말 EP33(구순 신지도 정배)을 숨김 대상으로 둠 | OK |
| unspecified_as_off | W5의 M3(UNSPECIFIED)를 화면에서 OFF로 표시 | OK |
| context_as_event | 환경 context ENV03을 4/10 날짜 구간에 사건처럼 배치 | OK |
| environment_to_individual | 환경 ENV03 → 김명신 구금 경과 후보 G06a edge를 화면에 추가 | OK |
| responsibility_to_biological | 책임 V_RESPONSIBILITY → 사인 판단 EP27 직접 edge를 화면에 추가 | OK |
| temporal_order | 3/4 체포 지시(EP09)와 6/13 최종 도난 판단(EP25)의 x 위치를 맞바꿈 | OK |
| candidate_grade_changed | 화면에서 후보 G01a의 final grade를 MEDIUM → HIGH로 표시 | OK |
| intervention_changed | 화면에서 do(M1=OFF)·V_COMPLAINT_TO_BARRACKS 결과를 PATH_BREAKS → PATH_REMAINS로 표시 | OK |
| view_not_subset | D 병영 지휘·체포 View에 canonical에 없는 edge(EP09 → EP33 직접 연결)를 추가 | OK |
| view_not_subset | C 구순→김명신 View에 canonical에 없는 node(EP_NEW)와 그 좌표를 추가 | OK |
| view_status_changed | E 자미덕 View 좌표 항목에 G04b의 status를 OBSERVED로 적어 넣음 | OK |
| view_hidden_notice_missing | F 구금·사망 View의 '시각적 필터·삭제 아님' 안내를 빈 문자열로 바꿈 | OK |
| label_clipped | EP13 node label을 '5월 12일 이형원 장계…'로 잘라 말줄임 표시 | OK |
| font_too_small | 화면 CSS의 본문 글자 크기를 12px(9pt)로 줄임 | OK |
| line_height_too_small | 화면 CSS의 기본 line-height를 1.3으로 줄임 | OK |
| initial_label_unreadable | I 정조 최종 판단 View의 첫 화면 최소 배율을 0.5로 낮춤(글자 8px) | OK |
| view_node_overlap | B 시간순 View에서 EP11 좌표를 EP09 위로 옮김 | OK |
| temporal_order | H 홍대협 재조사 View에서 EP02(2/22)와 EP24(6/13)의 x를 맞바꿈 | OK |
| responsibility_to_biological | F 구금·사망 View에서 책임 판단 EP29를 branch A(생물학적 사인) 묶음에도 넣음 | OK |
| dom_id_missing | app.js가 index.html에 없는 #foot-note에 글자를 넣음(25f81b6 배포 직후 옛 app.js가 멈춘 그 줄) | OK |
| stale_asset_version | index.html의 js/app.js 주소를 옛 내용 해시(?v=000000000000)로 둠 | OK |
| stale_asset_version | index.html이 data/bundle.js를 버전 없이 실음(캐시된 옛 데이터와 섞일 수 있음) | OK |
| runtime_failsafe_missing | index.html에서 '시각화 초기화 오류' 표시 guard를 뺌 | OK |
| runtime_failsafe_missing | app.js에서 보이는 node 0 → Overview 복구 guard 호출을 뺌 | OK |

## 동결 그래프

- 현재 sha256: `ccb7ec63763a715ae90c74dfff37d3ed7980fa705fd152f59de8bed2e31d4e0c`
- 직전 sha256(앞자리): `ccb7ec63763a715a…`
- 구조 sha256(문구 제외): `0b69134457880767285c3516e1e9c962bb9b778a5c6f4e85b248c6b16b01c80d` — 이전과 동일
- topology sha256(id·끝점·type): `04c84b0e24af31f5605800ae30bc2750563a1aeb3e72390aa6d6643676b68e84` — 이전과 동일
- 변경 내용: narrative world 사용 방식 재정리(경쟁하는 설명으로 병렬 보존). observed graph는 손대지 않음 — node·edge·condition·끝점·type 모두 그대로

## Narrative worlds

| world | 상태 | bridge | 최저 등급 | bridge 근거 등급 분포 | 가정 수 | 미확정 동일성 의존 | 미해결 gap |
|---|---|---|---|---|---|---|---|
| W1 | COMPETING_EXPLANATION | G01a G02a G03a G04a G05a G06a G07a G08a G09a G11a G12a G13a | LOW | MEDIUM 5 / LOW 7 | 20 | ID06, ID07 | G10 |
| W2 | COMPETING_EXPLANATION | G01a G02b G03a G04b G06b G07c G08a G09a G12a | LOW | MEDIUM 2 / LOW 7 | 18 | 0 | G05, G10, G11, G13 |
| W3 | COMPETING_EXPLANATION | G01b G02a G04c G05a G06a G07a G08a G12a | LOW | MEDIUM 2 / LOW 5 / NONE 1 | 11 | ID07 | G03, G09, G10, G11, G13 |
| W4 | COMPETING_EXPLANATION | G01a G02b G03c G06a G07b G08b G11a G13a | LOW | MEDIUM 3 / LOW 4 / NONE 1 | 14 | 0 | G04, G05, G09, G10, G12 |
| W5 | COMPETING_EXPLANATION | G01a G06a G07a G08a | LOW | MEDIUM 2 / LOW 2 | 5 | 0 | G02, G03, G04, G05, G09, G10, G11, G12, G13 |
| W6 | REJECTED | G06c G07d G12b | LOW | LOW 3 | 4 | 0 | G01, G02, G03, G04, G05, G08, G09, G10, G11, G13 |
