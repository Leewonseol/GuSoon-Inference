# AUDIT 1 — Episode Fidelity Audit

핵심 질문: **문장들을 episode로 묶으면서 원래 내용이 바뀌었는가?**

- 판정: **PASS** (ERROR 0 · WARN 0 · UNRESOLVED 5 · INFO 12)
- confirmed fact 50개 중 episode로 추적 가능: 50개
- episode 37개 — 모두 confirmed fact로 역추적됨 (unsupported episode = 0)

## 1. 자동 검사 요약

| check | ERROR | WARN | UNRESOLVED | INFO |
|---|---|---|---|---|
| clause_prop_alignment | 0 | 0 | 0 | 4 |
| clause_split | 0 | 0 | 0 | 2 |
| outside_confirmed_set | 0 | 0 | 0 | 1 |
| over_merge | 0 | 0 | 0 | 1 |
| resolved_identity | 0 | 0 | 0 | 4 |
| unresolved_identity | 0 | 0 | 5 | 0 |
| **합계** | **0** | **0** | **5** | **12** |

검사 항목: omission, unsupported_episode, clause_fidelity, over_merge, order_execution_conflation, semantic_strengthening, semantic_weakening(한정 표현 보존 + 원문 어휘 보존율), epistemic_collapse, testimony_to_fact, temporal_conflation, identity_forcing, closed_set, clause_prop_alignment(05 대조), provenance(04·05 대조).

### ERROR
_없음_

### WARN (수동 판정은 §3)
_없음_

### INFO
- `clause_split` **CF040** — 2개 절로 분할 — 합치면 원문 전체를 덮음
- `clause_split` **CF045** — 2개 절로 분할 — 합치면 원문 전체를 덮음
- `over_merge` **EP09** — 허용된 혼합 ['IDENT', 'TESTIMONY'] — 근거: 지시 행위와 지시 대상의 사료 식별은 같은 문장 단위로 묶는다. 실행(EP11)은 분리.
- `clause_prop_alignment` **EP26** — CF040 절 → V3P0101
- `clause_prop_alignment` **EP27** — CF040 절 → V3P0105
- `clause_prop_alignment` **EP31** — CF045 절 → V3P0136
- `clause_prop_alignment` **EP32** — CF045 절 → V3P0146
- `resolved_identity` **ID01** — 공초의 '병사' (CF021·CF023·CF024) = 이광섭 · 사용자 확정 · episode summary는 원문 표면형 유지
- `resolved_identity` **ID02** — '한 비장' (CF016·CF017) = 한재욱 · 사용자 확정 · episode summary는 원문 표면형 유지
- `resolved_identity` **ID03** — 처분문의 '한가' (CF048) = 한재욱 · 사용자 확정 · episode summary는 원문 표면형 유지
- `resolved_identity` **ID11** — '원돌' (CF020 '원돌 등의 이름') = 정원돌 (CF009·CF016) · 사용자 확정 · episode summary는 원문 표면형 유지
- `outside_confirmed_set` **05** — CF가 참조하지 않는 prop 83개 — DAG node로 쓰지 않음

## 2. Fact → Episode 추적표

| episode | 제목 | 구성 fact | 인식 floor | 진술/기록 주체 |
|---|---|---|---|---|
| EP01 | 구순–김명신 관계 변화 | CF001, CF002, CF003 | RECORDED_TESTIMONY | 명업 |
| EP02 | 2월 22일 밤 도적 침입 전언 | CF004, CF005 | RECORDED_NESTED_TESTIMONY | 명업(나복 발언 전달) |
| EP03 | 구순의 소장과 체포령 | CF006 | RECORDED_TESTIMONY | 명업 |
| EP04 | 2월 28일 밤 병영 출동 준비 | CF007, CF008, CF009, CF010 | RECORDED_TESTIMONY | 이진욱 |
| EP05 | 2월 29일 덕평 체포 활동 | CF011, CF012 | RECORDED_TESTIMONY | 이진욱 |
| EP06 | 자미덕의 병영 압송·신문·구류 | CF013, CF014, CF015 | RECORDED_TESTIMONY | 자미덕 |
| EP07 | 한 비장의 석방 조건 제시와 대질 시 거짓 진술 | CF016, CF017 | RECORDED_TESTIMONY | 자미덕 |
| EP08 | 유제희의 현지 탐문과 구순 발언 기록 | CF020 | RECORDED_TESTIMONY | 유제희 |
| EP09 | 3월 4일 병사의 김생원 체포 지시 | CF021, CF022 | RECORDED_TESTIMONY | 이진욱 / 기사 식별 |
| EP10 | 3월 4일 조계완의 구순 집 방문과 서찰 | CF024 | RECORDED_TESTIMONY | 조계완 |
| EP11 | 3월 4일 김명신·김갑득 체포 | CF023 | RECORDED_TESTIMONY | 이진욱 |
| EP12 | 한재욱의 안핵 공초 | CF018, CF019 | RECORDED_TESTIMONY | 한재욱 |
| EP13 | 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고 | CF027, CF028 | DOCUMENTED_OFFICIAL_REPORT | 이형원(충청도 관찰사) |
| EP14 | 5월 12일 이형원의 지휘 계통 평가 | CF025, CF026 | DOCUMENTED_OFFICIAL_EVALUATION | 이형원 |
| EP15 | 5월 12일 정조 1차 판단: 도난 부재 방향 | CF030 | DOCUMENTED_ROYAL_JUDGMENT | 정조 |
| EP16 | 5월 12일 정조 명: 구순 의금부 구금·엄사 | CF031 | DOCUMENTED_ROYAL_ORDER | 정조 |
| EP17 | 5월 27일 암행어사 이조원 보고: 도난 부재 방향 | CF032 | DOCUMENTED_INSPECTOR_REPORT | 이조원(암행어사) |
| EP18 | 5월 27일 정조의 이조원 비판·파직 | CF033 | DOCUMENTED_ROYAL_JUDGMENT_AND_ORDER | 정조 |
| EP19 | 5월 27일 정조 명: 구순 의금부 엄수·반복 신문 | CF034 | DOCUMENTED_ROYAL_ORDER | 정조 |
| EP20 | 5월 28일 홍대협 공주 안핵어사 차하 | CF035 | DOCUMENTED_ROYAL_ORDER | 정조 |
| EP21 | 6월 11일 윤노동 별단 | CF029 | DOCUMENTED_INSPECTOR_REPORT | 윤노동(암행어사) |
| EP22 | 6월 11일 비변사 처리 보류 청·윤허 | CF036 | DOCUMENTED_COURT_ACTION | 비변사·정조 |
| EP23 | 6월 13일 홍대협 공주목 신문·복명 | CF037 | DOCUMENTED_OFFICIAL_ACTION | 홍대협(안핵어사) |
| EP24 | 홍대협 도난 판단: 약간의 실제 도난, 좀도둑 수준 | CF038 | DOCUMENTED_OFFICIAL_FINDING | 홍대협 |
| EP25 | 정조 최종 도난 판단: 실재 | CF039 | DOCUMENTED_ROYAL_JUDGMENT | 정조 |
| EP26 | 홍대협 사인 평가: 질병 | CF040 (절: CF040:홍대협은 김명신의 죽음을 질병 때문이라고 평가했고) | DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT | 홍대협 |
| EP27 | 정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음 | CF040, CF041 (절: CF040:정조는 김명신 부처가 전염병에 걸려 죽은 것으로 판단했다.) | DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT | 정조 |
| EP28 | 정조: 구순→김명신 직접 사망 인과 불확실 | CF042 | DOCUMENTED_ROYAL_JUDGMENT | 정조 |
| EP29 | 정조: 구순 책임 연결 판단 | CF043 | DOCUMENTED_ROYAL_JUDGMENT | 정조 |
| EP30 | 정조: 이광섭 책임 판단 | CF044 | DOCUMENTED_ROYAL_JUDGMENT | 정조 |
| EP31 | 홍대협: 지세 호칭 기원 미확정 | CF045 (절: CF045:홍대협은 여러 차례 신문과 별도 탐문에도 지세 호칭의 기원을 확정하지 못했고) | DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT | 홍대협 |
| EP32 | 정조: 구순 지세 호칭 날조 죄 불인정 | CF045 (절: CF045:정조는 구순이 지세 호칭을 스스로 만들어냈다는 죄는 인정하지 않았다.) | DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT | 정조 |
| EP33 | 구순 신지도 정배 | CF046 | DOCUMENTED_ROYAL_ORDER | 정조 |
| EP34 | 이광섭 영동현 유배 | CF047 | DOCUMENTED_ROYAL_ORDER | 정조 |
| EP35 | 병영 비장 한가 처분 | CF048 | DOCUMENTED_ROYAL_ORDER | 정조 |
| EP36 | 이형원 파직 | CF049 | DOCUMENTED_ROYAL_ORDER | 정조 |
| EP37 | 6월 16일 이형원 유임 | CF050 | DOCUMENTED_ROYAL_ORDER | 정조 |

## 3. 수동 의미 검토 (원본 CSV 대조)

자동 검사로 잡기 어려운 의미 변화는 episode마다 원문 `confirmed_statement`, `notes`, 대응 05 prop과 대조해 판정했다.

| 대상 | 검사 | 판정 | 근거 |
|---|---|---|---|
| CF001–CF050 → EP01–EP37 | omission / unsupported_episode | PASS | CF 50개가 모두 1개 이상 episode에 속하고, episode 37개가 모두 CF로 역추적된다. unsupported episode 0. CF가 참조하지 않는 05 prop 83개는 §5에 목록만 두고 node로 쓰지 않았다. |
| EP08 (CF020) | semantic_strengthening | PASS | summary가 '풍각 김상제도 극히 수상하다고 말했고'를 그대로 둔다. '범인 지목'·'고발'로 바꾸지 않았고 caution에 '범인 지목이 아님'을 적었다. |
| EP07 (CF017) | semantic_strengthening | PASS | '한 비장의 지휘에 따라 거짓으로 꾸며 말했다'를 유지했다. 무엇을 거짓으로 말했는지(누구를 지목했는지)는 원문에 없으므로 '거짓 지목'으로 쓰지 않았다. |
| EP12 (CF018) | semantic_weakening (부인 범위 확대) | PASS | '은밀히 사주한 일은 없다'를 유지했다. '어떤 사주도 없었다'로 넓히지 않았고, '남은 밥을 준 사실은 인정'도 함께 남겨 인정과 부인의 경계를 지켰다. |
| EP04 '조계완 등' · EP07 '김흥득 등' · EP08 '원돌 등' | closed_set | PASS | 세 '등'이 summary에 그대로 남는다. 05 set_status(V3P0080 OPEN_SET_EXPLICIT_MEMBERS, V3P0096 OPEN_SET)와 일치한다. EP07 caution은 김명신이 명시 명단에 없지만 열린 목록이라 배제도 확정하지 않는다고 적었다. |
| EP13 '무고한 평민들' · EP21 '여러 죄수' | closed_set | PASS | 05 V3P0007·V3P0040은 OPEN_SET이다. summary는 복수 표현을 유지하고 caution에 김명신 포함 여부를 확정하지 않는다고 적었다. '김명신이 형벌을 받았다'는 문장은 어디에도 만들지 않았다. |
| EP09·EP11 (공초의 '병사') | surface form (ID01, 사용자 확정) | PASS | ID01(병사=이광섭)은 사용자 확정(RESOLVED)이다. 그래도 summary는 원문 표면형 '병사'를 유지한다(surface_form_substitution 검사). 동일성 확정은 3/4 지시 행위를 관측 사실로 올리지 않는다(이진욱 진술 그대로). |
| EP07 '한 비장' | surface form (ID02, 사용자 확정) | PASS | ID02(한 비장=한재욱)는 사용자 확정이다. summary는 '한 비장'을 유지한다. OE007은 condition 없이 같은 인물에 대한 두 진술(사주 주장 ↔ 은밀한 사주 부인)의 PARTIAL 충돌로 남고, 사주를 사실로 확정하지 않는다. |
| EP35 '한가' | surface form (ID03, 사용자 확정) | PASS | ID03(한가=한재욱)은 사용자 확정이다. 처분문 표면형 '병영 비장으로 표기된 한가'를 유지했고(CF048 notes), 연결은 동일성 대장과 identity_links 컬럼에 둔다. 처분 근거 행위는 confirmed set에 없어 G09 gap으로 남는다. |
| '병영의 하급 보조자' | identity_forcing (ID04, 참고용 미해결) | PASS | 이 표현은 05(이조원 V3P0026·V3P0027·V3P0124)에만 있다. confirmed set에 없으므로 episode·edge 어디에도 쓰지 않았다. UNRESOLVED로 두되 model_relevance=NONE, manual_decision_required=NO다. |
| EP08 '풍각 김상제' · EP29 '병영의 염탐 담당자' | identity_forcing (ID05·ID06) | PASS | EP08은 '풍각 김상제'를 김명신으로, EP29는 '염탐 담당자'를 유제희로 바꾸지 않았다. 05 V3P0095의 object 필드(김명신)는 audit용 주석이라 summary에 반영하지 않았다. 두 node를 잇는 OE071은 condition=ID05·ID06이다. |
| EP04 '철편 네 개' · EP30 '철퇴 네 개' | identity_forcing (ID07) | PASS | 물건 이름과 행위자(이진욱: 한재욱이 만들어 줌 / 정조: 이광섭이 만들게 함)를 각 원문대로 두었다. 대응 edge OE080은 condition=ID07이다. |
| EP08 '원돌 등' ↔ EP04·EP07 '정원돌' | identity_forcing (ID11) | PASS (수정 후) | Stage 4 준비 중 찾은 미등록 동일성이다. summary는 원문 그대로였지만 동일성 대장에 없었다. ID11(UNRESOLVED)을 추가하고 EP08 caution과 identity 검사 규칙에 넣은 뒤 Audit 1을 다시 돌렸다. |
| EP02 (CF004·CF005) | epistemic_collapse (중첩 진술) | PASS | layer=NESTED_TESTIMONY, epistemic_floor=RECORDED_NESTED_TESTIMONY. '명업은 나복이 … 말했다고 진술했다'로 이중 귀속을 유지했다. 30여 명·횃불·지세대감은 CF005 notes대로 caution에서 객관적 사실이 아니라고 적었다. |
| EP09 (CF021 + CF022) | over_merge / epistemic_collapse | PASS | 진술(이진욱)과 사료 식별(CF022)을 한 episode로 묶었지만 floor는 더 약한 RECORDED_TESTIMONY다. 지시(EP09)와 실행(EP11)은 분리했다. 허용 혼합 {TESTIMONY, IDENT}로 INFO 처리했다. |
| CF040 → EP26·EP27, CF045 → EP31·EP32 | over_merge (절 분할) | PASS | 판단 주체가 다른 홍대협(official)과 정조(royal)의 경계에서만 나눴다. 두 절은 원문 substring이고 합치면 원문 전체를 덮는다. 05 대조: CF040 절 → V3P0101(홍대협)·V3P0105(정조), CF045 절 → V3P0136(홍대협)·V3P0146(정조). |
| EP27 (CF040 정조 절 + CF041) | over_merge | PASS | 같은 주체(정조)·같은 날·같은 기사(SRC3_006)·같은 사인/처우 쟁점이다. 판단 대상이 '부처'(아내 포함)로 넓어진 점을 summary와 caution에 남겼다. |
| EP27 (CF041) ↔ EP13 (CF027) | semantic 긴장 보존 | PASS | 5/12 장계의 '구금·조사'와 6/13 정조의 '평범한 신문도 받지 않았다'를 어느 쪽으로도 맞추지 않았다. CF041 notes대로 royal judgment 자체로 보존하고, 긴장은 OE062(CONTRADICTS_AT_CLAIM_LEVEL, PARTIAL_TENSION)로 남겼다. CF028의 열린 집합은 충돌 근거로 쓰지 않았다. |
| EP29 (CF043) · EP28 (CF042) | semantic_strengthening | PASS | '책임을 연결해 판단했다'를 유지했고 '구순 때문에 죽었다'(직접 인과)로 바꾸지 않았다. 정조의 직접 인과 유보('십분 확실하다고 할 수 없다')는 EP28로 따로 두었다. |
| EP32 (CF045 정조 절) | semantic_strengthening | PASS | '스스로 만들어냈다는 죄는 인정하지 않았다'를 '구순은 지세와 무관'으로 강화하지 않았다. |
| EP15 (CF030) · EP24 (CF038) · EP13 (CF027) | semantic_weakening | PASS | '도난 자체가 없었다는 방향을 받아들였다'의 '방향', '약간의 실제 도난'·'보통 좀도둑 수준', '달포 이상'·'확실한 장물'을 모두 유지했다. |
| EP01·EP04·EP05·EP06 (A1-W1–W4) | semantic_weakening / epistemic marker | FIXED | 이전 판정은 'PASS(수동)'였으나 재검토에서 표현 차이로 넘기지 않았다. 여러 진술을 '…의 진술에 따르면' 하나로 귀속하면 뒤쪽 절이 사실 서술처럼 읽힐 수 있다. 그래서 원문 문장마다 '진술했다'를 복원하고 EP04의 '자신'을 원문대로 되돌렸다. 진술자·대상·시간·동일성은 수정 전후 모두 원문과 같다. 재실행 결과 WARN 0. |
| EP07 (A1-E1) | testimony_to_fact (새 regression 규칙) | FIXED | 보존율로는 WARN이 아니었으나 새 규칙 epistemic_marker_deletion·testimony_to_fact가 같은 유형을 ERROR로 잡았다. 두 진술 각각에 '진술했다'를 복원했다. |
| EP01–EP12 (진술 episode 전체) | actor_substitution / testimony_to_fact (새 규칙) | PASS | summary 첫 주어가 원문 첫 문장의 진술자와 같고, '진술했' 개수가 진술 member 수 이상이며, 원문의 '자신'이 그대로 남는 것을 자동 검사로 확인했다. |
| EP01 (CF001–CF003) · EP04 (CF007–CF010) | temporal_conflation | PASS | EP01은 친숙·왕래(2월 초순 이전) → 힐책(2월 초순) → 단절(그 이후)의 순서를 summary 어순으로 보존한다. EP04는 28일 밤의 호출·지시와 28일 밤~29일 새벽의 철편 제작을 한 출동 준비 단계로 묶고 시간 범위(228–229)를 남겼다. |
| EP12 · EP23 | temporal_conflation (진술 시점 vs 내용 시점) | PASS | 공초 진술 행위는 안핵 기간(5/28–6/13)으로, 진술 내용 속 사건 시점은 각 episode의 occurrence_text로 따로 기록했다(preflight §4). |
| AUDIT 1 1차 실행 ERROR 2건 (EP15·EP32) | epistemic_collapse 오탐 | 오탐 확인 | EP15 '받아들였다', EP32 '인정하지 않았다'는 원문 그대로의 royal judgment 동사다. 검사기의 기록 행위 어휘에 없어 ERROR가 났다. 내용은 고치지 않고 검사기 정규식에 '받아들'·'인정'을 추가했다. |

## 3-1. WARN disposition

모든 WARN은 FIXED / RECLASSIFIED_INFO / UNRESOLVED / ESCALATED_ERROR 중 하나로 처리했다. disposition이 없는 WARN이 남으면 build.py가 멈춘다. 전체 표는 `warn_dispositions.csv`에 있다.

| warning_id | audit_stage | affected_item | warning_type | original_text | generated_text | risk | disposition | justification | final_status |
|---|---|---|---|---|---|---|---|---|---|
| A1-W1 | AUDIT1 | EP01 | semantic_weakening | CF001 명업은 김명신이 본래 구순과 친숙하여 날마다 왕래했다고 진술했다. / CF002 명업은 김명신이 박거사 일로 구순에게 편지를 보내 힐책했다고 진술했다. / CF003 명업은 그 뒤 구순과 김명신의 왕래가 끊겼다고 진술했다. | 명업의 진술에 따르면, 김명신은 본래 구순과 친숙하여 날마다 왕래했으나, 박거사 일로 구순에게 편지를 보내 힐책했고, 그 뒤 구순과 김명신의 왕래가 끊겼다. | 원문 어휘 보존율 0.78. 세 진술의 '진술했다' 표지가 하나의 '따르면'으로 합쳐져 뒤쪽 절(힐책·단절)이 사실 서술처럼 읽힐 수 있음 | FIXED | 원문 대조 결과 진술자(명업)·대상(김명신·구순)·내부 순서는 그대로였다. 그러나 뒤쪽 절의 귀속이 약해지므로 표현 차이로 넘기지 않고 세 진술 각각에 '진술했다'를 복원했다. 재실행 결과 WARN 사라짐(보존율 1.00). | RESOLVED |
| A1-W2 | AUDIT1 | EP04 | semantic_weakening | CF007 이진욱은 2월 28일 밤 병영에서 자신을 비장청으로 불렀다고 진술했다. / CF008 이진욱은 한재욱이 자신과 조계완 등에게 덕평으로 가도록 지시했다고 진술했다. / CF009 이진욱은 한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했다. / CF010 이진욱은 한재욱이 철편 네 개를 만들어 주었다고 진술했다. | 이진욱의 진술에 따르면, 2월 28일 밤 병영에서 이진욱을 비장청으로 불렀고, 한재욱이 이진욱과 조계완 등에게 덕평으로 가도록 지시하고 변지돌과 정원돌을 잡아오라고 지시했으며, 한재욱이 철편 네 개를 만들어 주었다. | 보존율 0.71. (1) 네 진술의 '진술했다' 표지 삭제. (2) '자신'이 '이진욱'으로 치환됨. 치환이 주체를 바꾸었는지 확인 필요 | FIXED | '자신'의 지시 대상은 원문에서도 진술자 이진욱이라 주체는 바뀌지 않았다. 그래도 대명사 치환은 actor 정규화이므로 자동 INFO로 넘기지 않고, '자신'을 원문대로 되돌리고 네 진술 각각에 '진술했다'를 복원했다. 재실행 결과 WARN 사라짐. | RESOLVED |
| A1-W3 | AUDIT1 | EP05 | semantic_weakening | CF011 이진욱은 변지돌이 이미 공주진에서 잡혀간 상태였다고 진술했다. / CF012 이진욱은 장교 일행이 재돌의 처 자미덕을 붙잡았다고 진술했다. | 이진욱의 진술에 따르면, 2월 29일 변지돌은 이미 공주진에서 잡혀간 상태였고, 장교 일행이 재돌의 처 자미덕을 붙잡았다. | 보존율 0.79. 두 진술의 '진술했다' 표지가 합쳐져 체포 사실이 객관 사실처럼 읽힐 수 있음 | FIXED | 진술자·대상·날짜(2/29, chronology 열)는 유지되었다. 표지 복원으로 처리했다. 재실행 결과 WARN 사라짐. | RESOLVED |
| A1-W4 | AUDIT1 | EP06 | semantic_weakening | CF013 자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔다고 진술했다. / CF014 자미덕은 병영에서 도적 혐의로 한 차례 신문을 받았다고 진술했다. / CF015 자미덕은 신문 뒤 비장청 다모방에 구류되었다고 진술했다. | 자미덕의 진술에 따르면, 자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔고, 병영에서 도적 혐의로 한 차례 신문을 받았으며, 신문 뒤 비장청 다모방에 구류되었다. | 보존율 0.76. 세 진술 표지 삭제로 신문·구류가 관측 사실처럼 읽힐 수 있음 | FIXED | 진술자·대상·'한 차례'는 유지되었다. 표지 복원으로 처리했다. 재실행 결과 WARN 사라짐. | RESOLVED |
| A1-E1 | AUDIT1 | EP07 | testimony_to_fact | CF016 자미덕은 한 비장이 … 등을 큰 도적이라고 말하면 자신과 남편을 다음 날 석방하겠다고 말했다고 진술했다. / CF017 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술했다. | 자미덕의 진술에 따르면, 한 비장이 … 석방하겠다고 말했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다. | 이전 실행에서는 보존율 0.80 이상이라 WARN이 아니었다. 이번에 추가한 regression 규칙(epistemic_marker_deletion·testimony_to_fact)이 같은 결함 유형을 찾아냄. 대질·거짓 진술이 객관 사실처럼 읽힐 위험 | ESCALATED_ERROR | A1-W1–W4와 같은 결함 유형이므로 ERROR로 올리고 다음 stage 진행 전에 고쳤다. 두 진술 각각에 '진술했다'를 복원했다. '한 비장'·'등'·'거짓으로 꾸며'는 그대로 두었다. 재실행 ERROR 0. | RESOLVED |

수정 후 문구 / 최종 분류:

- **A1-W1** → 명업은 김명신이 본래 구순과 친숙하여 날마다 왕래했다고 진술했고, 김명신이 박거사 일로 구순에게 편지를 보내 힐책했다고 진술했으며, 그 뒤 구순과 김명신의 왕래가 끊겼다고 진술했다. · 최종 분류: OBSERVED (RECORDED_TESTIMONY 유지)
- **A1-W2** → 이진욱은 2월 28일 밤 병영에서 자신을 비장청으로 불렀다고 진술했고, 한재욱이 자신과 조계완 등에게 덕평으로 가도록 지시했다고 진술했으며, 한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했고, 한재욱이 철편 네 개를 만들어 주었다고 진술했다. · 최종 분류: OBSERVED (RECORDED_TESTIMONY 유지)
- **A1-W3** → 이진욱은 2월 29일 변지돌이 이미 공주진에서 잡혀간 상태였다고 진술했고, 장교 일행이 재돌의 처 자미덕을 붙잡았다고 진술했다. · 최종 분류: OBSERVED (RECORDED_TESTIMONY 유지)
- **A1-W4** → 자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔다고 진술했고, 병영에서 도적 혐의로 한 차례 신문을 받았다고 진술했으며, 신문 뒤 비장청 다모방에 구류되었다고 진술했다. · 최종 분류: OBSERVED (RECORDED_TESTIMONY 유지)
- **A1-E1** → 자미덕은 한 비장이 … 석방하겠다고 말했다고 진술했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술했다. · 최종 분류: OBSERVED (RECORDED_TESTIMONY 유지)

## 3-2. UNRESOLVED (사료 자체의 모호성 — 허용, 데이터에 보존)

- `unresolved_identity` **ID04** — '병영의 하급 보조자' (audit-only V3P0026·V3P0027·V3P0124) ↔ 한재욱 · 관련 episode 없음(DAG 미사용) · 참고용(model_relevance=NONE, manual_decision_required=NO) · unresolved_reason: audit-only 자료(05, 이조원 주장)에만 있고 인명이 직접 나오지 않는다. 현재 DAG·후보·world 어디에도 쓰이지 않아 결정해도 모델 결과가 바뀌지 않는다(참고용 미해결).
- `unresolved_identity` **ID05** — '풍각 김상제' (CF020) ↔ 김명신 · 관련 episode EP08, EP09 · unresolved_reason: '풍각 김상제'(상주 호칭)와 '풍각 김생원'(=김명신, CF022)은 다른 호칭이다. 둘을 같은 사람으로 적은 confirmed 문장이 없다.
- `unresolved_identity` **ID06** — '병영의 염탐 담당자' (CF043) ↔ 유제희 · 관련 episode EP08, EP29 · unresolved_reason: 정조 판단(CF043)은 직책 표현('병영의 염탐 담당자')만 쓰고 이름을 적지 않았다.
- `unresolved_identity` **ID07** — '철편 네 개' (CF010, 이진욱: 한재욱이 만들어 줌) ↔ '철퇴 네 개' (CF044, 정조: 이광섭이 만들게 함) · 관련 episode EP04, EP30 · unresolved_reason: 개수(네 개)와 사건은 같지만 물건 이름(철편/철퇴)과 행위 층위(제작·지급/제작 지시)가 다르다.
- `unresolved_identity` **ID08** — 3/4 '장교 일행' (CF023) ↔ 조계완 포함 여부 (CF024) · 관련 episode EP04, EP10, EP11 · unresolved_reason: 3/4 '장교 일행'의 구성원은 기록되지 않았다.


## 4. 수정 이력 (Audit → 수정 → 재검사)

| 회차 | 발견 | 조치 |
|---|---|---|
| 1차 실행 | ERROR 2건: EP15 '받아들였다', EP32 '인정하지 않았다'가 epistemic_collapse로 잡힘. 검사기의 기록 행위 어휘에 빠져 있던 오탐 | episode 내용은 그대로 두고 검사기 정규식에 '받아들'·'인정'을 추가 |
| 2차 실행 | ERROR 0, WARN 4 (EP01·EP04·EP05·EP06 원문 어휘 보존율 0.71–0.79) | 원문 대조 수동 검토: 빠진 토큰은 진술 어미와 '자신'→진술자 이름뿐이라 왜곡 없음 → PASS (§3) |
| Stage 4 준비 중 | 미등록 동일성 발견: CF020 '원돌 등' ↔ CF009·CF016 '정원돌' | IDENTITY_REGISTER에 ID11(UNRESOLVED) 추가, EP08 caution 보강, identity 검사 규칙에 (원돌, 정원돌, ID11) 추가 |
| 3차 실행 (ID11 반영) | ERROR 0, WARN 4 (같은 4건). 이후 모든 전체 실행에서 같은 결과 | 수동 판정 유지 → PASS |
| WARN 0 작업 — 4차 | WARN 4건을 다시 검토: 진술자·대상·시간은 유지되었으나 '진술했다' 표지가 합쳐져 testimony가 사실처럼 읽힐 위험 | 자동 INFO 강등 대신 FIXED: EP01·EP04·EP05·EP06 문장마다 '진술했다' 복원, EP04 '자신' 원문 복원 → ERROR 0, WARN 0 |
| WARN 0 작업 — 5차 | 새 regression 규칙(epistemic_marker_deletion·testimony_to_fact·actor_substitution·occurrence_record_confusion·responsibility_to_causation·environment_to_individual_fact) 추가 후 ERROR 2건: EP07 '진술' 표지 2→0 | ESCALATED_ERROR로 처리하고 EP07 문장마다 '진술했다' 복원 → ERROR 0, WARN 0 |
| WARN 0 작업 — 6차 | regression 케이스 15개 중 '진술자 바꿔치기' 1개를 검사기가 놓침(이름이 summary 어딘가에 있으면 통과하던 약점) | actor_substitution에 'summary 첫 주어 = 원문 첫 주어' 검사를 추가 → 15/15 탐지. 최종 ERROR 0, WARN 0, UNRESOLVED 9(동일성), INFO 8 |
| 사용자 동일성 확정 반영 | 사용자가 ID01·ID02·ID03·ID11을 확정 | 동일성 대장 status=RESOLVED(resolved_by=USER, 근거 기록). summary는 원문 표면형 유지. 확정 ID 치환은 surface_form_substitution, 미확정 ID 치환은 identity_forcing으로 구분. 재실행 ERROR 0, WARN 0, UNRESOLVED 9→5(ID04 참고용 포함), INFO 8→12(resolved_identity 4) |

## 5. confirmed set 밖의 사료 내용 (05에만 있음 — DAG node로 쓰지 않음)

CF가 참조하지 않는 05 prop 83개. Stage 4에서는 latent 후보의 `audit_attestation`으로만 인용하고, 인용하더라도 후보는 LATENT로 유지한다.

| prop | 기록 | 진술/보고자 | 내용 |
|---|---|---|---|
| V3P0001 | SRC3_001 | 이형원 | 구순 — 거주 (청주 덕평) |
| V3P0002 | SRC3_001 | 이형원 | 구순 — 도난 피해를 입었다고 보고됨 |
| V3P0003 | SRC3_001 | 이형원 | 구순 — 김명신을 도적 괴수라고 말했다고 보고됨 (김명신) |
| V3P0008 | SRC3_001 | 이형원 | 회동 조사 응답자들 — 구순과 김명신 사이에 원한이 있었다고 진술했다고 보고됨 |
| V3P0009 | SRC3_001 | 이형원 | 회동 조사 응답자들 — 구순이 도난 상황을 꾸몄다고 진술했다고 보고됨 |
| V3P0010 | SRC3_001 | 이형원 | 회동 조사 응답자들 — 구순이 행랑 하인과 교졸을 통해 김명신에게 도적 괴수 누명을 씌웠다고 진술했다고 보고됨 |
| V3P0011 | SRC3_001 | 이형원 | 전후 체포자들 — 구순 집에서 미워하던 사람들이었다고 진술됐다고 보고됨 |
| V3P0014 | SRC3_001 | 비변사 | 비변사 — 이광섭 파직·나문·엄한 감죄를 청함 (이광섭) |
| V3P0015 | SRC3_001 | 정조 | 정조 — 이광섭 처분 요청을 윤허함 (이광섭) |
| V3P0018 | SRC3_002 | 이조원 | 이조원 — 구순 집에 화적이 들었다는 설명이 이치에 맞지 않는다고 판단 |
| V3P0019 | SRC3_002 | 이조원 | 구순 — 김명신의 비판 때문에 앙심을 품고 모함하려 했다고 주장 (김명신) |
| V3P0020 | SRC3_002 | 이조원 | 구순 — 도난 상황을 꾸몄다고 주장 |
| V3P0021 | SRC3_002 | 이조원 | 구순 — 지세랑이라는 말을 만들어 퍼뜨렸다고 주장 |
| V3P0022 | SRC3_002 | 이조원 | 구순 — 작은 궤짝의 돈을 도둑맞았다고 꾸몄다고 주장 |
| V3P0023 | SRC3_002 | 이조원 | 구순 — 하인의 부스럼 흔적을 창상으로 꾸몄다고 주장 |
| V3P0024 | SRC3_002 | 이조원 | 김명신 — 구순이 구성한 죄안으로 병영 옥에서 원통하게 죽었다고 주장 |
| V3P0025 | SRC3_002 | 이조원 | 김명신의 아내 — 김명신이 죽은 뒤 따라 죽었다고 보고 |
| V3P0026 | SRC3_002 | 이조원 | 병사 — 사건을 자세히 조사하지 않고 하급 보조자에게 맡겼다고 주장 |
| V3P0027 | SRC3_002 | 이조원 | 병영의 하급 보조자 — 구순의 가객이었다고 주장 |
| V3P0028 | SRC3_002 | 정조/비변사 당상 | 이조원 — 도난 진위와 중대 사실을 현장에서 직접 안핵하지 않은 점을 비판받음 |
| V3P0033 | SRC3_004 | 정조 | 정조 — 구순 사건과 지세랑 호칭을 홍대협에게 물음 |
| V3P0034 | SRC3_004 | 홍대협 | 홍대협 — 귀로에 사건 개요를 조금 들었다고 말함 |
| V3P0035 | SRC3_004 | 홍대협 | 홍대협 — 지세랑 호칭은 예전 호중 화적도 사용한 적이 있어 이번에 처음 생긴 말이 아닌 듯하다고 말함 |
| V3P0038 | SRC3_005 | 윤노동 | 구순 — 도적을 만났다고 말하고 영교를 불러 김명신 등의 이름을 써 주었다고 주장 |
| V3P0042 | SRC3_005 | 윤노동 | 한재욱 — 변가의 처를 꾀어 김명신이 도적 괴수라는 취지의 공초를 내게 했다고 주장 |
| V3P0046 | SRC3_006 | 명업 | 명업 — 구순 집 계집종의 남편이며 바깥사랑에 거주했다고 진술 |
| V3P0053 | SRC3_006 | 명업 | 구순 — 찾아온 장교 한 명을 안행랑으로 불러 조용히 대화했다고 진술 (장교 1명) |
| V3P0054 | SRC3_006 | 명업 | 명업 — 병영 뜰 공초에서 처음에는 사실대로 말했으나 위협이 두려워 도적이 없었다는 취지로 바꾸었다고 진술 |
| V3P0059 | SRC3_006 | 이진욱 | 한재욱 — 변지돌과 정원돌이 처남매부 사이이며 변지돌이 힘이 세니 조심하라고 말했다고 진술 |
| V3P0062 | SRC3_006 | 이진욱 | 장교 일행 — 자미덕을 데리고 구순 집으로 가 도난 상황을 물었다고 진술 (구순) |
| V3P0063 | SRC3_006 | 이진욱 | 구순 — 잃은 물건들을 열거했다고 진술됨 |
| V3P0064 | SRC3_006 | 이진욱 | 구순 — 도적이 스스로 지세대사라고 자칭했다고 말했다고 진술됨 |
| V3P0070 | SRC3_006 | 조계완 | 구순 — 왜 다시 왔는지 물었다고 진술됨 (조계완) |
| V3P0071 | SRC3_006 | 조계완 | 조계완 — 풍각의 상주를 잡으러 왔다고 답했다고 진술 |
| V3P0074 | SRC3_006 | 자미덕 | 재돌 — 아산에 나가 있었다고 진술 |
| V3P0078 | SRC3_006 | 자미덕 | 한 비장 — 그 후 매일 자미덕을 방안으로 불러들였다고 진술 (자미덕) |
| V3P0079 | SRC3_006 | 자미덕 | 한 비장 — 자미덕의 남편 재돌이 이미 체포되었다고 말했다고 진술 |
| V3P0081 | SRC3_006 | 자미덕 | 한 비장 — 자미덕에게 떡과 밥을 주었다고 진술 (자미덕) |
| V3P0084 | SRC3_006 | 한재욱 | 구순 — 구순 집 도난이 진영에 정소된 뒤였다고 진술 |
| V3P0085 | SRC3_006 | 한재욱 | 한재욱 — 도적 진상을 탐지하려고 병영 아전 유제희를 내보냈다고 진술 (유제희) |
| V3P0086 | SRC3_006 | 한재욱 | 유제희 — 변지돌·변재돌·정원돌·김명신·김성손·김흥득·김흥길 등의 성명을 적어왔다고 진술됨 |
| V3P0087 | SRC3_006 | 한재욱 | 유제희 — 그 이름들을 자신이 직접 염탐해 알아냈다고 말했다고 진술됨 |
| V3P0089 | SRC3_006 | 한재욱 | 유제희 — 석단 공초에서 김명신이 도적 괴수라고 했으니 자미덕에게 다시 물어보라고 말했다고 진술됨 |
| V3P0090 | SRC3_006 | 한재욱 | 한재욱 — 유제희 말에 따라 자미덕에게 다시 물었다고 진술 (자미덕) |
| V3P0091 | SRC3_006 | 한재욱 | 자미덕 — 재질문에 모른다고 답했다고 진술됨 |
| V3P0099 | SRC3_006 | 홍대협 | 지세 호칭 조사 — 여러 차례 조사와 별도 탐문에도 기원을 확정하지 못함 |
| V3P0100 | SRC3_006 | 홍대협 | 이광섭 — 구순의 과장과 아전의 거짓 보고를 믿고 장물 없이 큰 도적으로 판단했다고 평가 |
| V3P0102 | SRC3_006 | 홍대협 | 이문협 — 장물부터 확보하지 않고 장교·나졸을 풀어 평민을 잡고 병영 비장 지휘대로 죄를 얽었다고 평가 |
| V3P0103 | SRC3_006 | 정조 | 정조 — 공주목 안핵의 핵심을 도난 여부·김명신 사망 원인·지세 호칭 날조 여부의 세 의안으로 분리 |
| V3P0107 | SRC3_006 | 정조 | 정조 — 지세대감·지세대사·지세랑 호칭은 예전 무식한 좀도둑들도 쓰던 말이라고 판단 |
| V3P0108 | SRC3_006 | 정조 | 정조 — 구순이 지세 호칭을 스스로 만들어냈다는 죄는 면하게 됐다고 판단 |
| V3P0109 | SRC3_006 | 정조 | 정조 — 구순을 사형에서 감해 외딴 섬으로 정배하도록 명함 (구순) |
| V3P0112 | SRC3_006 | 정조 | 정조 — 병영 비장 한가를 도백이 엄히 세 차례 형장 친 뒤 먼 섬의 종으로 보내도록 명함 (한가) |
| V3P0115 | SRC3_001 | 이형원 | 회동 조사 응답자들 — 구순이 김명신에게 원한이 있어 해치려는 마음을 품었다고 진술했다고 보고됨 |
| V3P0116 | SRC3_001 | 이형원 | 회동 조사 응답자들 — 구순이 행랑 하인들에게 당부해 밖으로 소문을 퍼뜨렸다고 진술했다고 보고됨 |
| V3P0117 | SRC3_001 | 이형원 | 회동 조사 응답자들 — 구순이 교졸들과 결탁해 성명을 써 주고 김명신에게 도적 괴수 누명을 씌웠다고 진술했다고 보고됨 (김명신) |
| V3P0118 | SRC3_001 | 정조 | 정조 — 김명신이 병으로 죽었는지와 별개로 원통함을 품고 죽었다는 점과 구순에게서 비롯되었다는 점을 당시 사실로 받아들임 |
| V3P0119 | SRC3_002 | 이조원 | 구순의 집 — 앞이 큰길에 접하고 마을이 조밀하여 화적이 들어오기 어려운 곳이라고 이조원이 판단 |
| V3P0120 | SRC3_002 | 이조원 | 이조원 — 화적이 들었다면 사방 이웃과 노복이 알아야 하는데 한 마을에서 목격자가 없다는 점을 불합리하다고 판단 |
| V3P0121 | SRC3_002 | 이조원 | 김명신 — 구순이 거상 중 조석의 상식에 참여하지 않은 일을 비판했다고 보고 (구순) |
| V3P0122 | SRC3_002 | 이조원 | 김명신 — 피우와 관련해 구순의 형이 용접하는 것을 허락하지 않은 일 등을 비판했다고 보고 (구순) |
| V3P0123 | SRC3_002 | 이조원 | 이조원 — 김명신 사후 그 아내도 따라 죽었고 사건 뒤 도 전체의 공분이 컸다고 보고 |
| V3P0124 | SRC3_002 | 이조원 | 병영의 하급 보조자 — 구순의 가객이어서 구순의 부탁을 따라 옥안을 단련했다고 이조원이 주장 |
| V3P0125 | SRC3_003 | 이조원 | 김명신 — 구순과 이웃해 살며 구순의 불효한 행실을 늘 비판했다고 실록에 보고됨 (구순) |
| V3P0126 | SRC3_003 | 이조원 | 이조원 — 구순 집의 입지·마을 상황과 목격 부재를 들어 화적 설명이 이치에 맞지 않는다고 판단 |
| V3P0127 | SRC3_005 | 윤노동 | 윤노동 — 구순이 도난을 칭탁하고 양민을 얽어 무고해 목숨을 상하게 한 일이 있다고 평가 |
| V3P0128 | SRC3_005 | 윤노동 | 한재욱 — 변가의 처를 여러 방식으로 꾀어 김명신이 확실한 도적 괴수라는 내용의 공초를 내게 했다고 주장 (변가의 처) |
| V3P0129 | SRC3_005 | 윤노동 | 윤노동 — 구순 사건 관계자를 법에 따라 처단해 도 전체의 분함을 풀어야 한다고 건의 |
| V3P0131 | SRC3_006 | 홍대협 | 홍대협 — 내려가는 길에 널리 탐문했을 때에는 사람들이 애당초 도난이 없었다고 말했다고 보고 |
| V3P0132 | SRC3_006 | 홍대협 | 홍대협 — 정식 조사에서는 명업 등 세 사람의 공초가 분명해 약간의 실제 도난이 있었다고 판단 |
| V3P0133 | SRC3_006 | 홍대협 | 홍대협 — 실제 도난은 보통 좀도둑의 소행에 불과하다고 평가 |
| V3P0134 | SRC3_006 | 홍대협 | 구순 — 사실대로 고발할 수 있었는데도 과장하고 의혹을 키우다가 미운 사람에게 악감을 행사해 날조된 옥사를 사주해 이루기에 이르렀다고 평가 |
| V3P0135 | SRC3_006 | 홍대협 | 사람들 — 구순 사건의 전개에 놀라고 분개했다고 홍대협이 보고 |
| V3P0137 | SRC3_006 | 홍대협 | 홍대협 — 지세 호칭의 실정을 밝히려면 구순을 의금부에서 엄히 국문할 필요가 있다고 건의 (구순) |
| V3P0138 | SRC3_006 | 홍대협 | 이광섭 — 평민을 일부러 해치려는 의도에서 나온 것은 아니라고 보면서도 결과적으로 옥안을 강제로 만든 책임은 피하기 어렵다고 평가 |
| V3P0139 | SRC3_006 | 홍대협 | 김명신 — 질병으로 죽었더라도 사람들이 원통하게 죽었다고 말하는 것은 정황상 그럴 만하다고 평가 |
| V3P0140 | SRC3_006 | 홍대협 | 이광섭 — 한쪽 말만 듣고 잘못 판결한 죄는 중하게 다스려야 한다고 평가 |
| V3P0145 | SRC3_006 | 정조 | 구순 — 사건이 이렇게 된 원인을 구순의 무상함과 불량함에 돌려 책임을 물음 |
| V3P0147 | SRC3_006 | 정조 | 정조 — 구순을 감형해 외딴 섬에 정배하여 김명신 부처의 원한에 사죄하도록 명함 (구순) |
| V3P0152 | SRC3_006 | 정조 | 정조 — 도신 장계와 안핵어사 보고가 구순의 도난 여부에서 현격히 달랐다고 지적 |
| V3P0154 | SRC3_007 | 정조 | 이조원 — 담당 이외 고을을 두루 살핀 것은 어사 사목에 어긋난다고 앞서 판단했음 |
| V3P0155 | SRC3_007 | 정조 | 윤노동 — 담당 외 지역을 자의로 조사하고 다른 어사 출도 지역까지 거듭 들어간 점 등을 사명 위반으로 판단 |
| V3P0156 | SRC3_007 | 정조 | 정조 — 윤노동을 파직하고 불서의 법을 시행하도록 명함 (윤노동) |
