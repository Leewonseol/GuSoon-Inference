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

## Regression validation rules

build.py는 Audit 1 전에 아래 케이스를 검사기에 넣어 모두 ERROR로 잡히는지 확인한다(26/26 탐지).

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
