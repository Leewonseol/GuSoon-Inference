# Validation Summary

통과 조건: 각 Audit의 ERROR = 0, WARN = 0. INFO와 UNRESOLVED는 허용하되, UNRESOLVED는 사료 자체의 불확실성 때문에 남은 것이어야 한다.

```
Audit 1:
ERROR = 0
WARN = 0
INFO = 8
UNRESOLVED = 9

Audit 2:
ERROR = 0
WARN = 0
INFO = 1
UNRESOLVED = 8

Audit 3:
ERROR = 0
WARN = 0
INFO = 8
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

## UNRESOLVED 목록

### Audit 1

- `unresolved_identity` **ID01** — 공초의 '병사' (CF021·CF023·CF024) ↔ 이광섭 · 관련 episode EP09, EP10, EP11, EP14, EP30, EP34 · unresolved_reason: 공초 문장의 주어는 '병사'라는 직함뿐이다. 이광섭을 병사로 다루는 것은 5/12 기사(CF025)이고, 3/4 공초가 같은 사람을 가리킨다고 쓴 문장은 없다.
- `unresolved_identity` **ID02** — '한 비장' (CF016·CF017) ↔ 한재욱 · 관련 episode EP07, EP12 · unresolved_reason: 자미덕은 성(한)과 직함(비장)만 말했다. 한재욱 공초(CF018)는 자미덕을 방으로 부른 사실을 인정하지만 자신이 '한 비장'이라고 하지는 않는다.
- `unresolved_identity` **ID03** — 처분문의 '한가' (CF048) ↔ 한재욱 · 관련 episode EP04, EP12, EP35 · unresolved_reason: 처분문(CF048)은 '한가'라는 성 표기만 쓴다. 이름과 직함을 함께 적은 처분 문장이 없다.
- `unresolved_identity` **ID04** — '병영의 하급 보조자' (audit-only V3P0026·V3P0027·V3P0124) ↔ 한재욱 · 관련 episode 없음(DAG 미사용) · unresolved_reason: '하급 보조자'는 이조원 보고(05, audit-only)에만 나오며 confirmed set에는 없다.
- `unresolved_identity` **ID05** — '풍각 김상제' (CF020) ↔ 김명신 · 관련 episode EP08, EP09 · unresolved_reason: '풍각 김상제'(상주 호칭)와 '풍각 김생원'(=김명신, CF022)은 다른 호칭이다. 둘을 같은 사람으로 적은 confirmed 문장이 없다.
- `unresolved_identity` **ID06** — '병영의 염탐 담당자' (CF043) ↔ 유제희 · 관련 episode EP08, EP29 · unresolved_reason: 정조 판단(CF043)은 직책 표현('병영의 염탐 담당자')만 쓰고 이름을 적지 않았다.
- `unresolved_identity` **ID07** — '철편 네 개' (CF010, 이진욱: 한재욱이 만들어 줌) ↔ '철퇴 네 개' (CF044, 정조: 이광섭이 만들게 함) · 관련 episode EP04, EP30 · unresolved_reason: 개수(네 개)와 사건은 같지만 물건 이름(철편/철퇴)과 행위 층위(제작·지급/제작 지시)가 다르다.
- `unresolved_identity` **ID08** — 3/4 '장교 일행' (CF023) ↔ 조계완 포함 여부 (CF024) · 관련 episode EP04, EP10, EP11 · unresolved_reason: 3/4 '장교 일행'의 구성원은 기록되지 않았다.
- `unresolved_identity` **ID11** — '원돌' (CF020 '원돌 등의 이름') ↔ 정원돌 (CF009·CF016) · 관련 episode EP04, EP07, EP08 · unresolved_reason: '원돌'과 '정원돌'은 이름 일부만 겹친다. 같은 사람이라는 문장이 없다.

### Audit 2

- `conditional_edge` **OE007** — ID02 미확정 — edge는 condition으로만 성립 · unresolved_reason: 자미덕은 성(한)과 직함(비장)만 말했다. 한재욱 공초(CF018)는 자미덕을 방으로 부른 사실을 인정하지만 자신이 '한 비장'이라고 하지는 않는다.
- `partial_tension` **OE007** — 부분 충돌 — 원문 표현의 범위가 같은지 사료로 확정할 수 없어 충돌 강도를 PARTIAL로 보존 · unresolved_reason: 충돌은 '한 비장=한재욱'(미확정)일 때만 성립한다. 한재욱의 부인 범위는 '은밀한 사주'에 한정되므로 PARTIAL 충돌이다.
- `conditional_edge` **OE010** — ID08 미확정 — edge는 condition으로만 성립 · unresolved_reason: 3/4 '장교 일행'의 구성원은 기록되지 않았다.
- `partial_tension` **OE062** — 부분 충돌 — 원문 표현의 범위가 같은지 사료로 확정할 수 없어 충돌 강도를 PARTIAL로 보존 · unresolved_reason: PARTIAL_TENSION: '조사'가 곧 '신문'이라고 확정할 수 없다. CF028의 '무고한 평민들 모진 형벌'은 김명신 포함 여부가 열린 집합이므로 충돌 근거로 쓰지 않는다.
- `conditional_edge` **OE071** — ID05 미확정 — edge는 condition으로만 성립 · unresolved_reason: '풍각 김상제'(상주 호칭)와 '풍각 김생원'(=김명신, CF022)은 다른 호칭이다. 둘을 같은 사람으로 적은 confirmed 문장이 없다.
- `conditional_edge` **OE071** — ID06 미확정 — edge는 condition으로만 성립 · unresolved_reason: 정조 판단(CF043)은 직책 표현('병영의 염탐 담당자')만 쓰고 이름을 적지 않았다.
- `conditional_edge` **OE080** — ID07 미확정 — edge는 condition으로만 성립 · unresolved_reason: 개수(네 개)와 사건은 같지만 물건 이름(철편/철퇴)과 행위 층위(제작·지급/제작 지시)가 다르다.
- `conditional_edge` **OE081** — ID01 미확정 — edge는 condition으로만 성립 · unresolved_reason: 공초 문장의 주어는 '병사'라는 직함뿐이다. 이광섭을 병사로 다루는 것은 5/12 기사(CF025)이고, 3/4 공초가 같은 사람을 가리킨다고 쓴 문장은 없다.

### Audit 3

- `unresolved_gap` **G10** — 어느 retained world도 이 gap을 메우지 않음 (후보 G10a=MEDIUM, G10b=LOW, G10c=LOW) · unresolved_reason: 파직과 3일 뒤 유임의 사유가 모두 기록되지 않았다. 관측 근거(CF049, CF050)에 사유를 적은 문장이 없어 어느 후보도 world backbone에 넣지 않음

## Regression validation rules

build.py는 Audit 1 전에 아래 케이스를 검사기에 넣어 모두 ERROR로 잡히는지 확인한다(15/15 탐지).

| rule | 케이스 | 탐지 |
|---|---|---|
| epistemic_marker_deletion | A1-W1 원안 EP01: 진술 3건을 '명업의 진술에 따르면' 하나로 합침 | OK |
| testimony_to_fact | A1-E1 원안 EP07: '자미덕의 진술에 따르면 … 거짓으로 꾸며 말했다' | OK |
| actor_substitution | A1-W2 원안 EP04: '자신'을 '이진욱'으로 치환 | OK |
| actor_substitution | 진술자 바꿔치기: EP12의 한재욱 공초를 자미덕 진술로 | OK |
| semantic_weakening | '은밀히' 삭제: 어떤 사주도 없었다 | OK |
| identity_forcing | 공초 '병사'를 이광섭으로 치환(EP09) | OK |
| identity_forcing | '한 비장'을 한재욱으로 치환(EP07) | OK |
| closed_set | '등' 삭제(EP07) | OK |
| semantic_strengthening | '극히 수상하다' → 범인 지목(EP08) | OK |
| responsibility_to_causation | 책임 판단을 직접 사인으로(EP29) | OK |
| environment_to_individual_fact | 환경을 개인 사인으로(EP27) | OK |
| occurrence_record_confusion | 기록일(6/13)을 진술 내용의 발생 시점으로 사용(EP06) | OK |
| latent_as_observed | A3-W1 원안 G08a: 관측 node 사이 직접 latent edge | OK |
| open_set_closure | world 서술에서 열린 명단의 '등' 삭제 | OK |
| environment_to_individual_fact | 후보·world 서술: 환경 → 개인 감염 단정 | OK |

## 동결 그래프

- 현재 sha256: `c50402af878ffb4d202f7c8c28c5d829ecabcc5ad0e1f5d2d78665aaef7df7c8`
- 이전 sha256(앞자리): `86a529da3baff8f3…`
- 구조 sha256(문구 제외): `7b4d97185d70baa95a2efdb55492b854a0d39dcf26411b70a1bf830f0b79a1b3` — 이전과 동일
- 변경 내용: WARN 처리(A1-W1–W4, A1-E1)로 EP01·EP04·EP05·EP06·EP07 summary 문구만 바뀜. node·edge 구조는 그대로

## Narrative worlds

| world | 상태 | bridge | 최저 등급 | 미해결 gap |
|---|---|---|---|---|
| W1 | RETAINED | G01a G02a G03a G04a G05a G06a G07a G08a G09a G11a G12a G13a | MEDIUM | G10 |
| W2 | RETAINED | G01a G02b G03a G04b G06b G07c G08a G09a G12a | MEDIUM | G05, G10, G11, G13 |
| W3 | RETAINED | G01b G02a G04c G05a G06a G07a G08a G12a | LOW | G03, G09, G10, G11, G13 |
| W4 | RETAINED | G01a G02b G03c G06a G07b G08b G11a G13a | LOW | G04, G05, G09, G10, G12 |
| W5 | RETAINED | G01a G06a G07a G08a | HIGH | G02, G03, G04, G05, G09, G10, G11, G12, G13 |
| W6 | REJECTED | G06c G07d G12b | LOW | G01, G02, G03, G04, G05, G08, G09, G10, G11, G13 |
