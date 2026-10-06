# AUDIT 2 — Graph Fidelity Audit

핵심 질문: **원본 사실들을 연결하는 과정에서 원본보다 더 많은 관계를 주장했는가?**

- 판정: **PASS** (ERROR 0)
- node 41개 (episode 37, 환경 context 4) · edge 68개 · feature link 57개
- edge status: {'DERIVED': 64, 'OBSERVED': 4}
- edge type: {'TEMPORAL_BEFORE': 7, 'ORDER_TO_ACTION': 3, 'PROCEDURAL_NEXT': 14, 'CONTRADICTS_AT_CLAIM_LEVEL': 5, 'INFORMATION_FLOW': 12, 'REVIEW_OF': 9, 'REVISES': 2, 'CONTEXT_SUPPORTS': 9, 'RESPONSIBILITY_LINK': 7}
- CAUSES edge: 0개
- claim-level edge: 12개 · 조건부(identity) edge: 6개

## 1. 자동 검사 요약

| check | ERROR | WARN | INFO |
|---|---|---|---|
| identity_forcing | 0 | 0 | 6 |
| unsupported_edge | 0 | 0 | 1 |

검사 항목: unsupported_edge(근거 fact가 endpoint 구성 fact인지), causal_inflation(CAUSES 금지, 책임은 판단 node로만, 구순→사망 직접 연결 금지), institutional_overreach, environmental_leakage, missing_relation(필수 관계 17개), judgment_flattening, temporal_inversion, order_execution_conflation, testimony_to_fact(claim_level), identity_forcing(조건부 edge), acyclicity, latent_leak.

### ERROR
_없음_

### WARN
_없음_

### INFO
- `identity_forcing` **OE007** — 조건부 edge — ID02 미확정 상태 유지
- `identity_forcing` **OE010** — 조건부 edge — ID08 미확정 상태 유지
- `unsupported_edge` **OE060** — 절차 근거로 endpoint 밖 fact 인용: ['CF035']
- `identity_forcing` **OE071** — 조건부 edge — ID05 미확정 상태 유지
- `identity_forcing` **OE071** — 조건부 edge — ID06 미확정 상태 유지
- `identity_forcing` **OE080** — 조건부 edge — ID07 미확정 상태 유지
- `identity_forcing` **OE081** — 조건부 edge — ID01 미확정 상태 유지

## 2. 수동 관계 검토 (원본 CSV 대조)

| 대상 | 검사 | 판정 | 근거 |
|---|---|---|---|
| OE001–OE107 (68개) | unsupported_edge | PASS | 모든 edge의 supporting fact가 양 끝 node의 구성 CF 또는 환경 행이다. 예외는 OE060 하나로, 안핵 명령 CF035를 절차 근거로 인용했고 INFO로 표시했다. |
| edge type 전체 | causal_inflation | PASS | CAUSES 0개. 정조의 책임 귀속은 RESPONSIBILITY_LINK 7개로 표현했고 모두 royal judgment node(EP29·EP30)로만 들어간다. 구순 관련 node(EP01·EP08·EP10·EP29)에서 사망·사인 node(EP13·EP26·EP27)로 가는 edge는 없다. |
| Branch A (생물학적) | missing_relation (지정 구조) | PASS | EP13 → EP26(REVIEW_OF) → EP27(REVIEW_OF), ENV01·ENV03 → EP26·EP27(CONTEXT_SUPPORTS). 홍대협 질병 평가와 정조 부처 전염병 판단이 별개 node다. |
| Branch B (절차·책임) | missing_relation (지정 구조) | PASS | 구순 쪽: EP01(관계 악화)·EP08(발언 기록)·EP11(체포)·EP13(구금·사망 보고) → EP29. 이광섭 쪽: EP04(출동·철편, ID07)·EP09(병사 지시, ID01) → EP30, EP14(5/12 평가) → EP30(REVIEW_OF). 두 사슬은 EP29 → EP30(책임 비교)에서만 만난다. 구순 → 김명신 사망 단일 edge는 없다. |
| EP15 → EP25 (REVISES) · EP15·EP17 ↔ EP24 | judgment_flattening (5월 → 6월) | PASS | 5/12 도난 부재 방향(EP15)과 5/27 이조원 보고(EP17)를 지우지 않았다. 6/13 판단(EP24·EP25)과 CONTRADICTS_AT_CLAIM_LEVEL·REVIEW_OF·REVISES로 잇는다. 판단 node 9개가 모두 남아 있다. |
| OE100–OE107 (환경 8개) | environmental_leakage | PASS | 모두 ENV → 판단·보고 node(EP21 윤노동 별단, EP26 홍대협 평가, EP27 정조 판단)의 CONTEXT_SUPPORTS이고 basis는 ENVIRONMENTAL_CONTEXT 하나다. 김명신 개인 감염 node는 없다. |
| OE104 (ENV04 = E004 → EP27) | environmental_leakage / temporal | PASS | E004(5/12 옥수 전염병 치료 명)는 김명신 사망 보고와 같은 날이고 사망보다 뒤다. 처우나 사망에 영향을 준 것으로 잇지 않고 6/13 판단 node의 custody-health context로만 두었다(caution 명시). |
| feature link 57개 | institutional_overreach | PASS | creates_event=NO로 고정했다. basis가 INSTITUTIONAL_COMPATIBILITY 하나뿐인 edge는 0개다. 예: 3/4 병사 → 장교 체포 지시(OE008)는 F007 COMPATIBLE, 구순 → 병사 서찰(EP10)은 공식 경로로서 F020·F007 LOW. |
| OE008 (EP09 → EP11) | order_execution_conflation | PASS | CF023 '병사의 분부에 따라'가 지시와 실행을 원문에서 잇는다. ORDER_TO_ACTION 가운데 유일한 OBSERVED edge이고 EP09·EP11은 별개 node다. |
| OE004 (EP04 → EP05) | order_execution_conflation | PASS (주의) | DERIVED ORDER_TO_ACTION. 실행이 확인되는 것은 덕평 출동뿐이고 변지돌·정원돌 체포 지시는 실행되지 않았다(변지돌 기체포, 정원돌 미기록). 이 한계를 caution에 적었다. |
| EP16·EP19 (의금부 명) | order_execution_conflation | PASS | 명령만 관측된다. 실행 node를 만들지 않고 G13 gap으로 넘겼다. |
| claim_level 표시 edge 12개 | testimony_to_fact | PASS | 진술 내용 속 순서를 잇는 edge 9개(OE001–OE006, OE008–OE010)와 진술이 끼는 충돌·검토 edge 3개(OE007·OE013·OE090)에 claim_level을 표시했다. 객관적 사건 순서로 확정한 것이 아니다. |
| OE020–OE031 (진술 → EP23) | testimony_to_fact | PASS | '진술이 안핵 기록에 들어갔다'는 정보 흐름이며 진술 내용의 진위를 주장하지 않는다(caution 명시). |
| 조건부 edge 6개 (OE007·OE010·OE040·OE071·OE080·OE081) | identity_forcing | PASS | 미확정 동일성에 기대는 edge는 condition 컬럼에 ID02·ID08·ID09·ID05·ID06·ID07·ID01을 적었다. ID09만 같은 기사 provenance로 ACCEPTED_BY_PROVENANCE이고 나머지는 UNRESOLVED다. |
| OE080 (EP04 → EP30, 철편/철퇴) | identity_forcing (ID07) | PASS | RESPONSIBILITY_LINK는 condition=ID07일 때만 성립한다. 제작·지급(한재욱)과 제작 지시(이광섭)는 행위 층위가 달라 모순으로도 동일 행위로도 확정하지 않는다. |
| OE071 (EP08 → EP29) | identity_forcing / claim-level 차이 | PASS | 정조의 '구순이 성명을 적어 주었다'와 유제희의 '구순이 말했고 자신이 기록했다'를 하나로 합치지 않았다. condition=ID05·ID06. |
| OE082 (EP14 → EP30) | judgment_flattening (주체 혼동) | PASS | '비장에게 맡김'은 5/12에는 이문협, 6/13에는 이광섭에 대한 비판이다. 주체를 합치지 않고 REVIEW_OF로만 이었다. |
| OE063 (EP27 → EP28) | causal_inflation | PASS (주의) | 같은 날 정조 판단 안의 두 판단을 CONTEXT_SUPPORTS(basis SOURCE_DIRECT)로 잇는다. 앞 판단이 뒤 판단의 사유라는 문장은 없으므로 원인이 아니라 양립 관계로만 둔다. |
| OE013 (EP02 ↔ EP24) | testimony_to_fact | PASS | 중첩 진술의 '30여 명·횃불'과 홍대협의 '보통 좀도둑' 사이의 충돌은 규모에 관한 것이다. 도난 존재 자체는 양쪽이 인정한다(caution). |
| OE097 (EP36 → EP37) | judgment_flattening | PASS | 6/13 파직과 6/16 유임을 모두 node로 남기고 REVISES로 이었다. 사유는 G10 gap이다. |
| 전체 edge | temporal_inversion / acyclicity | PASS | CONTRADICTS 외의 edge는 모두 src.t_min ≤ dst.t_max이고 cycle이 없다. 날짜가 없는 EP08은 시간 edge 없이 INFORMATION_FLOW(OE027)·RESPONSIBILITY_LINK(OE071)에만 참여한다. |
| 고립 node | missing_relation | PASS | 고립 node 0개. 처분 node(EP33–EP37)는 책임 판단·복명과 PROCEDURAL_NEXT로 이어진다. |

## 3. 수정 이력

| 회차 | 발견 | 조치 |
|---|---|---|
| 이 세션 이전 전체 실행 (인계 기록) | ERROR 0으로 통과 | 수정 없음 |
| 이 세션 재실행 (ID11 반영 뒤, 이후 모든 실행 동일) | ERROR 0, WARN 0, INFO 7 (조건부 edge INFO 6개, endpoint 밖 절차 근거 OE060 INFO 1개). ID11은 어느 edge condition에도 쓰이지 않음 | INFO를 하나씩 수동 검토(§2) — 수정 없음. 동결 해시 86a529da3baf… 유지 |

## 4. Edge 전체 목록

| edge | src → dst | type | basis | status | claim | cond | 근거 |
|---|---|---|---|---|---|---|---|
| OE001 | EP01 → EP02 | TEMPORAL_BEFORE | TEMPORAL | DERIVED | Y |  | CF002, CF004 |
| OE002 | EP02 → EP03 | TEMPORAL_BEFORE | TEMPORAL | DERIVED | Y |  | CF004, CF006 |
| OE003 | EP02 → EP04 | TEMPORAL_BEFORE | TEMPORAL | DERIVED | Y |  | CF004, CF007 |
| OE004 | EP04 → EP05 | ORDER_TO_ACTION | SOURCE_DIRECT + TEMPORAL | DERIVED | Y |  | CF008, CF011, CF012 |
| OE005 | EP05 → EP06 | PROCEDURAL_NEXT | TEMPORAL | DERIVED | Y |  | CF012, CF013 |
| OE006 | EP06 → EP07 | PROCEDURAL_NEXT | TEMPORAL | DERIVED | Y |  | CF015, CF016, CF017 |
| OE007 | EP07 → EP12 | CONTRADICTS_AT_CLAIM_LEVEL | SOURCE_DIRECT | DERIVED | Y | ID02 | CF017, CF018 |
| OE008 | EP09 → EP11 | ORDER_TO_ACTION | SOURCE_DIRECT | OBSERVED | Y |  | CF021, CF023 |
| OE009 | EP09 → EP10 | PROCEDURAL_NEXT | SOURCE_DIRECT + TEMPORAL | DERIVED | Y |  | CF021, CF024 |
| OE010 | EP10 → EP11 | TEMPORAL_BEFORE | SOURCE_DIRECT | DERIVED | Y | ID08 | CF024, CF023 |
| OE011 | EP11 → EP13 | PROCEDURAL_NEXT | PROCEDURAL | DERIVED |  |  | CF023, CF027 |
| OE020 | EP01 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF001, CF037 |
| OE021 | EP02 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF004, CF037 |
| OE022 | EP03 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF006, CF037 |
| OE023 | EP04 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF007, CF037 |
| OE024 | EP05 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF011, CF037 |
| OE025 | EP06 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF013, CF037 |
| OE026 | EP07 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF016, CF037 |
| OE027 | EP08 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF020, CF037 |
| OE028 | EP09 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF021, CF037 |
| OE029 | EP10 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF024, CF037 |
| OE030 | EP11 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF023, CF037 |
| OE031 | EP12 → EP23 | INFORMATION_FLOW | SOURCE_DIRECT | DERIVED |  |  | CF018, CF037 |
| OE013 | EP02 → EP24 | CONTRADICTS_AT_CLAIM_LEVEL | SOURCE_DIRECT | DERIVED | Y |  | CF005, CF038 |
| OE040 | EP13 → EP15 | REVIEW_OF | SOURCE_DIRECT | DERIVED |  | ID09 | CF027, CF030 |
| OE041 | EP15 → EP16 | PROCEDURAL_NEXT | SOURCE_DIRECT + TEMPORAL | DERIVED |  |  | CF030, CF031 |
| OE042 | EP16 → EP19 | TEMPORAL_BEFORE | TEMPORAL | DERIVED |  |  | CF031, CF034 |
| OE043 | EP17 → EP18 | REVIEW_OF | SOURCE_DIRECT | OBSERVED |  |  | CF032, CF033 |
| OE044 | EP17 → EP19 | PROCEDURAL_NEXT | SOURCE_DIRECT | DERIVED |  |  | CF032, CF034 |
| OE045 | EP18 → EP20 | TEMPORAL_BEFORE | TEMPORAL | DERIVED |  |  | CF033, CF035 |
| OE046 | EP20 → EP23 | ORDER_TO_ACTION | SOURCE_DIRECT + PROCEDURAL | DERIVED |  |  | CF035, CF037 |
| OE047 | EP21 → EP22 | REVIEW_OF | SOURCE_DIRECT | OBSERVED |  |  | CF029, CF036 |
| OE048 | EP22 → EP23 | PROCEDURAL_NEXT | SOURCE_DIRECT | OBSERVED |  |  | CF036, CF037 |
| OE050 | EP23 → EP24 | PROCEDURAL_NEXT | SOURCE_DIRECT | DERIVED |  |  | CF037, CF038 |
| OE051 | EP23 → EP26 | PROCEDURAL_NEXT | SOURCE_DIRECT | DERIVED |  |  | CF037, CF040 |
| OE052 | EP23 → EP31 | PROCEDURAL_NEXT | SOURCE_DIRECT | DERIVED |  |  | CF037, CF045 |
| OE053 | EP15 → EP24 | CONTRADICTS_AT_CLAIM_LEVEL | SOURCE_DIRECT | DERIVED |  |  | CF030, CF038 |
| OE054 | EP17 → EP24 | CONTRADICTS_AT_CLAIM_LEVEL | SOURCE_DIRECT | DERIVED |  |  | CF032, CF038 |
| OE055 | EP24 → EP25 | REVIEW_OF | SOURCE_DIRECT | DERIVED |  |  | CF038, CF039 |
| OE056 | EP15 → EP25 | REVISES | SOURCE_DIRECT + TEMPORAL | DERIVED |  |  | CF030, CF039 |
| OE060 | EP13 → EP26 | REVIEW_OF | PROCEDURAL | DERIVED |  |  | CF027, CF035, CF040 |
| OE061 | EP26 → EP27 | REVIEW_OF | SOURCE_DIRECT | DERIVED |  |  | CF040 |
| OE062 | EP13 → EP27 | CONTRADICTS_AT_CLAIM_LEVEL | SOURCE_DIRECT | DERIVED |  |  | CF027, CF041 |
| OE063 | EP27 → EP28 | CONTEXT_SUPPORTS | SOURCE_DIRECT | DERIVED |  |  | CF040, CF041, CF042 |
| OE070 | EP01 → EP29 | RESPONSIBILITY_LINK | SOURCE_DIRECT | DERIVED |  |  | CF043, CF002, CF003 |
| OE071 | EP08 → EP29 | RESPONSIBILITY_LINK | SOURCE_DIRECT | DERIVED |  | ID05, ID06 | CF043, CF020 |
| OE072 | EP11 → EP29 | RESPONSIBILITY_LINK | SOURCE_DIRECT | DERIVED |  |  | CF043, CF023 |
| OE073 | EP13 → EP29 | RESPONSIBILITY_LINK | SOURCE_DIRECT | DERIVED |  |  | CF043, CF027 |
| OE074 | EP29 → EP33 | PROCEDURAL_NEXT | SOURCE_DIRECT | DERIVED |  |  | CF043, CF046 |
| OE080 | EP04 → EP30 | RESPONSIBILITY_LINK | SOURCE_DIRECT | DERIVED |  | ID07 | CF010, CF044 |
| OE081 | EP09 → EP30 | RESPONSIBILITY_LINK | SOURCE_DIRECT | DERIVED |  | ID01 | CF021, CF044 |
| OE082 | EP14 → EP30 | REVIEW_OF | PROCEDURAL | DERIVED |  |  | CF025, CF026, CF044 |
| OE083 | EP29 → EP30 | RESPONSIBILITY_LINK | SOURCE_DIRECT | DERIVED |  |  | CF043, CF044 |
| OE084 | EP30 → EP34 | PROCEDURAL_NEXT | SOURCE_DIRECT | DERIVED |  |  | CF044, CF047 |
| OE090 | EP02 → EP31 | REVIEW_OF | SOURCE_DIRECT | DERIVED | Y |  | CF005, CF045 |
| OE091 | EP31 → EP32 | REVIEW_OF | SOURCE_DIRECT | DERIVED |  |  | CF045 |
| OE095 | EP23 → EP35 | PROCEDURAL_NEXT | SOURCE_DIRECT | DERIVED |  |  | CF037, CF048 |
| OE096 | EP23 → EP36 | PROCEDURAL_NEXT | SOURCE_DIRECT | DERIVED |  |  | CF037, CF049 |
| OE097 | EP36 → EP37 | REVISES | TEMPORAL + SOURCE_DIRECT | DERIVED |  |  | CF049, CF050 |
| OE098 | EP25 → EP36 | TEMPORAL_BEFORE | TEMPORAL | DERIVED |  |  | CF039, CF049 |
| OE100 | ENV01 → EP26 | CONTEXT_SUPPORTS | ENVIRONMENTAL_CONTEXT | DERIVED |  |  | E001, CF040 |
| OE101 | ENV03 → EP26 | CONTEXT_SUPPORTS | ENVIRONMENTAL_CONTEXT | DERIVED |  |  | E003, CF040 |
| OE102 | ENV01 → EP27 | CONTEXT_SUPPORTS | ENVIRONMENTAL_CONTEXT | DERIVED |  |  | E001, CF040 |
| OE103 | ENV03 → EP27 | CONTEXT_SUPPORTS | ENVIRONMENTAL_CONTEXT | DERIVED |  |  | E003, CF040 |
| OE104 | ENV04 → EP27 | CONTEXT_SUPPORTS | ENVIRONMENTAL_CONTEXT | DERIVED |  |  | E004, CF040 |
| OE105 | ENV02 → EP27 | CONTEXT_SUPPORTS | ENVIRONMENTAL_CONTEXT | DERIVED |  |  | E002, CF040 |
| OE106 | ENV01 → EP21 | CONTEXT_SUPPORTS | ENVIRONMENTAL_CONTEXT | DERIVED |  |  | E001, CF029 |
| OE107 | ENV03 → EP21 | CONTEXT_SUPPORTS | ENVIRONMENTAL_CONTEXT | DERIVED |  |  | E003, CF029 |
