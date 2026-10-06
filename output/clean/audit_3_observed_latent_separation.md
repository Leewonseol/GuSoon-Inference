# AUDIT 3 — Observed / Derived / Latent Separation

핵심 질문: **추론한 것을 사료에서 확인된 사실처럼 표시했는가?**

- 판정: **PASS** (ERROR 0)
- LATENT → OBSERVED 둔갑: **0건**
- 동결 해시: `86a529da3baff8f326831620bc9a55c2e351452b03dd5f67e852768a33dc4bfe` (Stage 4·5 뒤에도 observed DAG 변경 없음)

## 1. 분류 집계

| 층 | node | edge | 위치 |
|---|---|---|---|
| OBSERVED | 41 (episode·환경 행) | 4 | episode_nodes.csv / observed_edges.csv |
| DERIVED | 0 (node는 만들지 않음) | 64 | observed_edges.csv (status=DERIVED) |
| LATENT | 46 | 71 | latent_candidates.csv / latent_elements.csv / gap_candidates.md |

DERIVED는 원본에 한 문장으로 쓰여 있지는 않지만 원본 정보에서 안전하게 도출되는 구조적 관계만 가리킨다(명시 날짜의 시간 순서, 같은 기사 안의 절차 순서, 판단 문구와 episode의 대응). 모든 episode node는 OBSERVED이며 원본 CF에서만 만들었다.

## 2. 자동 검사 요약

| check | ERROR | WARN | INFO |
|---|---|---|---|
| audit_only_support | 0 | 0 | 3 |
| freeze_violation | 0 | 0 | 1 |
| latent_as_observed | 0 | 1 | 0 |
| support_basis_cap | 0 | 0 | 3 |
| world_integrity | 0 | 0 | 1 |

### ERROR
_없음_

### WARN
- `latent_as_observed` **G08a** — 관측 node 사이 직접 latent edge EP18->EP20 — LATENT 표지 확인

### INFO
- `freeze_violation` **observed_dag** — 동결 해시 일치 86a529da3baf
- `support_basis_cap` **G01c** — INSTITUTIONAL_COMPATIBILITY만 근거 → LOW 상한 적용
- `audit_only_support` **G04d** — confirmed 지지 없이 05 흔적만 있음 — LATENT 유지
- `audit_only_support` **G07d** — confirmed 지지 없이 05 흔적만 있음 — LATENT 유지
- `support_basis_cap` **G10b** — ENVIRONMENTAL_CONTEXT만 근거 → LOW 상한 적용
- `support_basis_cap` **G10c** — INSTITUTIONAL_COMPATIBILITY만 근거 → LOW 상한 적용
- `audit_only_support` **G12b** — confirmed 지지 없이 05 흔적만 있음 — LATENT 유지
- `world_integrity` **worlds** — world 6개 (retained 5, rejected 1) — 쌍별 gap 차이 ≥2 확인

## 3. 수동 검토

| 대상 | 검사 | 판정 | 근거 |
|---|---|---|---|
| 후보 38개 · latent node 46 · latent edge 71 | latent_as_observed | PASS | 모든 후보는 status=LATENT다. latent node id는 LN_ 접두어를 쓰고 서술은 [LATENT]로 시작한다(C() helper). observed 표(episode_nodes.csv·observed_edges.csv)에는 LATENT가 하나도 없다. |
| audit_attestation이 있는 후보 19개 | audit-only 승격 금지 | PASS | 05 prop을 인용한 후보도 모두 LATENT다. G04d(석단 공초)·G07d·G12b는 confirmed 지지 없이 05 흔적만 있어 INFO로 표시했고 LOW에 머문다. 05 prop은 node로도 edge로도 쓰지 않았다. |
| G08a (EP18 → EP20) | observed node 사이 latent edge (WARN) | PASS (수동) | latent node 없이 EP18·EP20 사이에 LATENT PROCEDURAL_NEXT 하나를 둔 후보다. 이 edge는 latent_elements.csv에만 있고, observed_edges.csv의 OE045(TEMPORAL_BEFORE, DERIVED)는 그대로다. gap_candidates.md·latent_elements.csv 모두 LATENT로 표시한다. |
| G09b (원안 EP04 → EP35 RESPONSIBILITY_LINK) | causal_inflation | PASS (수정 후) | 원안은 observed 처분 node(royal order)로 RESPONSIBILITY_LINK를 바로 걸었다. 책임 귀속은 판단 수준이어야 하므로 latent 근거 node LN_G09b_2를 사이에 두고 처분에는 PROCEDURAL_NEXT로 잇게 고쳤다. |
| G10b (환경만) · G01c·G10c (제도만) | support_basis 상한 | PASS | 근거가 환경 context 하나 또는 제도 compatibility 하나뿐인 후보는 grade 규칙 (5)로 LOW 상한이다. G10b의 latent node는 판단 사유 가설(individual_level=False)이고, 환경에서 개인 사건을 만들지 않았다. |
| G06a·G06b·G12a (개인 발병·사망) | environmental_leakage | PASS | 개인 수준 latent node의 근거는 CF029(윤노동: '병들어 죽었다')와 CF040(정조: '부처가 전염병')이다. E001·E003은 environmental_fit 평가에만 썼고 ENV node에서 나가는 latent edge는 없다. |
| 동일성에 기대는 후보 10개 | identity_forcing | PASS | 가정에 IDxx가 있으면 identity_conditions로 모으고 MEDIUM 상한을 적용했다(grade 규칙 6). 그래서 G02a(ID07)가 HIGH에서 MEDIUM으로 내려갔다. 금지 동일성 ID01–ID04는 identity_register.csv에서 모두 UNRESOLVED다(자동 검사). |
| G02a·G03a·G09c 원안 서술 | identity_forcing | PASS (수정 후) | 원안 G02a는 '병사(이광섭)'로 ID01을 사실처럼 썼다. G03a는 '김상제' 언급 뒤 '김명신 체포'를 이어 ID05에 기댔고, G09c는 '한가 ≠ 한재욱'을 ID03 표시 없이 썼다. 서술을 조건형으로 고치고 가정에 IDxx를 넣었다. 보강한 검사를 원안에 다시 돌려 이 세 건이 ERROR로 잡히는 것을 확인했다. |
| G04b·G07b·G07c 서술 | testimony_to_fact | PASS | '회유된 자미덕'처럼 진술 내용을 사실로 쓰던 원안 문구를 '자미덕은 …라고 진술했다'로 바꿨다. G07b의 '꾸몄다'와 G07c의 '위협'은 05 진술 내용으로만 귀속한다. |
| G06c·G07d·G12b (대조 후보) | contradiction 표시 | PASS | 원안은 최종 판단과 부딪히는 latent 주장을 CONTEXT_SUPPORTS로 이었다. 충돌 대상(EP27·EP25)으로 CONTRADICTS_AT_CLAIM_LEVEL latent edge를 두도록 고쳤다. 세 후보 모두 contradiction_risk HIGH → LOW, KEPT_AS_CONTRAST이며 기각 world W6에만 쓴다. |
| G04e | pruning | PASS | 구순 → 장교 공식 체포 명령. F007·F008(지휘권)과 CF023('병사의 분부에 따라')에 모두 어긋나 INCOMPATIBLE, PRUNED. 어느 world에도 쓰지 않는다. |
| G04b·G05a institutional_fit | grading 판단 | PASS (판단 기록) | 원안은 관측 행위의 합법성 평가(EP07 회유 F002 LOW, EP10 서찰 F020 LOW)를 bridge 등급에 그대로 옮겼다. bridge가 가정하는 것은 '진술·서찰이 전달되었다'는 정보 흐름뿐이므로 MEDIUM으로 두고 근거를 notes에 적었다. 관측 행위의 LOW 평가는 node_feature_links.csv에 그대로 있다. |
| gap별 후보 수 | candidate_budget | PASS | gap 13개, 후보 2–5개(G04만 5개). 모든 gap에 후보가 있다. |
| W1–W6 | world_integrity | PASS | 한 gap에 후보 1개, retained world에 INCOMPATIBLE·대조용 후보 0, 상충 쌍(G03b+G04b, G03c+G04a, G01a+G02c) 동시 사용 0, world 쌍마다 2개 이상 gap에서 다르다. 모든 서술에 [L] 표지가 bridge 수 이상 있다. |
| W1–W6 서술 | identity_forcing / testimony_to_fact | PASS | 두 표면형(병사·이광섭, 한 비장·한재욱, 한가·한재욱, 김상제·김명신, 철편·철퇴, 원돌·정원돌)이 함께 나오면 같은 서술 안에 IDxx 조건을 적었다(자동 검사). 관측 부분은 '…라고 진술했다/보고했다/판단했다'로 남겼다. |
| latent edge 71개 | causal_inflation | PASS | CAUSES 0개. latent edge type은 모두 Stage 2의 허용 목록 안에 있다. |
| 동결 해시 | freeze_violation | PASS | Stage 3 해시 86a529da3baf…가 Stage 4 뒤와 Stage 5 뒤에 다시 계산한 값과 같다. observed DAG(41 node · 68 edge)는 바뀌지 않았다. |

## 4. 수정 이력

| 회차 | 발견 | 조치 |
|---|---|---|
| 1차 실행 (Stage 4 첫 실행) | ERROR 2건: G01b·G03c의 audit_attestation에 'V3P0084(반대 방향)'처럼 주석이 붙어 prop id 검증 실패 | 주석을 attestation에서 빼고 반대 방향 근거는 conflicts 문구로 옮김 |
| 1차 뒤 수동 의미 검토 | 자동 검사가 못 잡은 문제: G02a '병사(이광섭)'(ID01 단정), G02b '한재욱(비장)'(직함 단정), G03a의 ID05 암묵 의존, G09c의 ID03 표시 누락, G09b의 latent RESPONSIBILITY_LINK가 royal order node(EP35)로 직접 감, G04b '회유된 자미덕'(진술의 사실화), G06c·G07d·G12b가 충돌 대상에 CONTEXT_SUPPORTS 사용, G02a가 ID07에 기대면서 HIGH | 서술을 조건형·진술 귀속형으로 고침. G09b에 근거 node 추가. 대조 후보에 CONTRADICTS_AT_CLAIM_LEVEL 사용. grade 규칙 (6) 추가(미확정 동일성 → MEDIUM 상한, G02a HIGH → MEDIUM). G01a·G08a의 latent edge type을 PROCEDURAL_NEXT로 정정. G04b·G05a institutional_fit을 정보 흐름 기준 MEDIUM으로 조정 |
| 검사기 보강 | 위 문제를 자동으로 잡도록 audit3에 검사 추가: 서술 속 동일성 표면형 쌍 ↔ IDxx 조건, latent RESPONSIBILITY_LINK 대상, 모든 CAUSES 금지, 환경만 근거 후보의 MEDIUM 이상 금지, 동일성 의존 후보의 HIGH 금지, 금지 동일성 status, world 상충 쌍·[L] 표지·쌍별 차이 | 보강한 검사를 원안 후보에 다시 돌려 ERROR 6건(provenance 2, identity_forcing 3, causal_inflation 1)이 잡히는 것을 확인 |
| 2차 실행 | ERROR 0, WARN 1 (G08a 관측 node 사이 latent edge) | 수동 검토 PASS (§3) |
| Stage 5 작성 중 | W4 서술에 '병사'와 '이광섭'이 ID01 표시 없이 함께 나옴(실행 전 자체 검토) | W4 서술에 ID01 조건 문장 추가 |
| 3차 실행 (world 포함 재검사) | ERROR 0, WARN 1 (같은 G08a) | PASS. 이후 서술 문구 두 곳(자미덕 진술 인용, 홍대협의 '평가' 동사)을 원문에 맞게 다듬고 재실행 — 결과 동일 |

## 5. 전체 요소 분류표

| id | 종류 | 분류 | 출처 |
|---|---|---|---|
| EP01 | node | OBSERVED | CF001, CF002, CF003 |
| EP02 | node | OBSERVED | CF004, CF005 |
| EP03 | node | OBSERVED | CF006 |
| EP04 | node | OBSERVED | CF007, CF008, CF009, CF010 |
| EP05 | node | OBSERVED | CF011, CF012 |
| EP06 | node | OBSERVED | CF013, CF014, CF015 |
| EP07 | node | OBSERVED | CF016, CF017 |
| EP08 | node | OBSERVED | CF020 |
| EP09 | node | OBSERVED | CF021, CF022 |
| EP10 | node | OBSERVED | CF024 |
| EP11 | node | OBSERVED | CF023 |
| EP12 | node | OBSERVED | CF018, CF019 |
| EP13 | node | OBSERVED | CF027, CF028 |
| EP14 | node | OBSERVED | CF025, CF026 |
| EP15 | node | OBSERVED | CF030 |
| EP16 | node | OBSERVED | CF031 |
| EP17 | node | OBSERVED | CF032 |
| EP18 | node | OBSERVED | CF033 |
| EP19 | node | OBSERVED | CF034 |
| EP20 | node | OBSERVED | CF035 |
| EP21 | node | OBSERVED | CF029 |
| EP22 | node | OBSERVED | CF036 |
| EP23 | node | OBSERVED | CF037 |
| EP24 | node | OBSERVED | CF038 |
| EP25 | node | OBSERVED | CF039 |
| EP26 | node | OBSERVED | CF040 |
| EP27 | node | OBSERVED | CF040, CF041 |
| EP28 | node | OBSERVED | CF042 |
| EP29 | node | OBSERVED | CF043 |
| EP30 | node | OBSERVED | CF044 |
| EP31 | node | OBSERVED | CF045 |
| EP32 | node | OBSERVED | CF045 |
| EP33 | node | OBSERVED | CF046 |
| EP34 | node | OBSERVED | CF047 |
| EP35 | node | OBSERVED | CF048 |
| EP36 | node | OBSERVED | CF049 |
| EP37 | node | OBSERVED | CF050 |
| ENV01 | node | OBSERVED | E001 |
| ENV02 | node | OBSERVED | E002 |
| ENV03 | node | OBSERVED | E003 |
| ENV04 | node | OBSERVED | E004 |
| OE001 | edge | DERIVED | CF002, CF004 |
| OE002 | edge | DERIVED | CF004, CF006 |
| OE003 | edge | DERIVED | CF004, CF007 |
| OE004 | edge | DERIVED | CF008, CF011, CF012 |
| OE005 | edge | DERIVED | CF012, CF013 |
| OE006 | edge | DERIVED | CF015, CF016, CF017 |
| OE007 | edge | DERIVED | CF017, CF018 |
| OE008 | edge | OBSERVED | CF021, CF023 |
| OE009 | edge | DERIVED | CF021, CF024 |
| OE010 | edge | DERIVED | CF024, CF023 |
| OE011 | edge | DERIVED | CF023, CF027 |
| OE020 | edge | DERIVED | CF001, CF037 |
| OE021 | edge | DERIVED | CF004, CF037 |
| OE022 | edge | DERIVED | CF006, CF037 |
| OE023 | edge | DERIVED | CF007, CF037 |
| OE024 | edge | DERIVED | CF011, CF037 |
| OE025 | edge | DERIVED | CF013, CF037 |
| OE026 | edge | DERIVED | CF016, CF037 |
| OE027 | edge | DERIVED | CF020, CF037 |
| OE028 | edge | DERIVED | CF021, CF037 |
| OE029 | edge | DERIVED | CF024, CF037 |
| OE030 | edge | DERIVED | CF023, CF037 |
| OE031 | edge | DERIVED | CF018, CF037 |
| OE013 | edge | DERIVED | CF005, CF038 |
| OE040 | edge | DERIVED | CF027, CF030 |
| OE041 | edge | DERIVED | CF030, CF031 |
| OE042 | edge | DERIVED | CF031, CF034 |
| OE043 | edge | OBSERVED | CF032, CF033 |
| OE044 | edge | DERIVED | CF032, CF034 |
| OE045 | edge | DERIVED | CF033, CF035 |
| OE046 | edge | DERIVED | CF035, CF037 |
| OE047 | edge | OBSERVED | CF029, CF036 |
| OE048 | edge | OBSERVED | CF036, CF037 |
| OE050 | edge | DERIVED | CF037, CF038 |
| OE051 | edge | DERIVED | CF037, CF040 |
| OE052 | edge | DERIVED | CF037, CF045 |
| OE053 | edge | DERIVED | CF030, CF038 |
| OE054 | edge | DERIVED | CF032, CF038 |
| OE055 | edge | DERIVED | CF038, CF039 |
| OE056 | edge | DERIVED | CF030, CF039 |
| OE060 | edge | DERIVED | CF027, CF035, CF040 |
| OE061 | edge | DERIVED | CF040 |
| OE062 | edge | DERIVED | CF027, CF041 |
| OE063 | edge | DERIVED | CF040, CF041, CF042 |
| OE070 | edge | DERIVED | CF043, CF002, CF003 |
| OE071 | edge | DERIVED | CF043, CF020 |
| OE072 | edge | DERIVED | CF043, CF023 |
| OE073 | edge | DERIVED | CF043, CF027 |
| OE074 | edge | DERIVED | CF043, CF046 |
| OE080 | edge | DERIVED | CF010, CF044 |
| OE081 | edge | DERIVED | CF021, CF044 |
| OE082 | edge | DERIVED | CF025, CF026, CF044 |
| OE083 | edge | DERIVED | CF043, CF044 |
| OE084 | edge | DERIVED | CF044, CF047 |
| OE090 | edge | DERIVED | CF005, CF045 |
| OE091 | edge | DERIVED | CF045 |
| OE095 | edge | DERIVED | CF037, CF048 |
| OE096 | edge | DERIVED | CF037, CF049 |
| OE097 | edge | DERIVED | CF049, CF050 |
| OE098 | edge | DERIVED | CF039, CF049 |
| OE100 | edge | DERIVED | E001, CF040 |
| OE101 | edge | DERIVED | E003, CF040 |
| OE102 | edge | DERIVED | E001, CF040 |
| OE103 | edge | DERIVED | E003, CF040 |
| OE104 | edge | DERIVED | E004, CF040 |
| OE105 | edge | DERIVED | E002, CF040 |
| OE106 | edge | DERIVED | E001, CF029 |
| OE107 | edge | DERIVED | E003, CF029 |
| LN_G01a_1 | node | LATENT | G01a |
| LN_G01a_2 | node | LATENT | G01a |
| G01a.e1 | edge | LATENT | EP03→LN_G01a_1 |
| G01a.e2 | edge | LATENT | LN_G01a_1→LN_G01a_2 |
| G01a.e3 | edge | LATENT | LN_G01a_2→EP04 |
| LN_G01b_1 | node | LATENT | G01b |
| G01b.e1 | edge | LATENT | EP03→LN_G01b_1 |
| G01b.e2 | edge | LATENT | LN_G01b_1→EP04 |
| LN_G01c_1 | node | LATENT | G01c |
| LN_G01c_2 | node | LATENT | G01c |
| G01c.e1 | edge | LATENT | EP03→LN_G01c_1 |
| G01c.e2 | edge | LATENT | LN_G01c_1→LN_G01c_2 |
| G01c.e3 | edge | LATENT | LN_G01c_2→EP04 |
| LN_G02a_1 | node | LATENT | G02a |
| G02a.e1 | edge | LATENT | LN_G02a_1→EP04 |
| LN_G02b_1 | node | LATENT | G02b |
| LN_G02b_2 | node | LATENT | G02b |
| G02b.e1 | edge | LATENT | LN_G02b_1→EP04 |
| G02b.e2 | edge | LATENT | EP04→LN_G02b_2 |
| LN_G02c_1 | node | LATENT | G02c |
| G02c.e1 | edge | LATENT | LN_G02c_1→EP04 |
| LN_G03a_1 | node | LATENT | G03a |
| LN_G03a_2 | node | LATENT | G03a |
| G03a.e1 | edge | LATENT | LN_G03a_1→EP08 |
| G03a.e2 | edge | LATENT | EP08→LN_G03a_2 |
| G03a.e3 | edge | LATENT | LN_G03a_2→EP04 |
| LN_G03b_1 | node | LATENT | G03b |
| G03b.e1 | edge | LATENT | EP08→LN_G03b_1 |
| G03b.e2 | edge | LATENT | LN_G03b_1→EP09 |
| LN_G03c_1 | node | LATENT | G03c |
| G03c.e1 | edge | LATENT | EP08→LN_G03c_1 |
| G03c.e2 | edge | LATENT | LN_G03c_1→EP09 |
| LN_G04a_1 | node | LATENT | G04a |
| G04a.e1 | edge | LATENT | EP08→LN_G04a_1 |
| G04a.e2 | edge | LATENT | LN_G04a_1→EP09 |
| LN_G04b_1 | node | LATENT | G04b |
| G04b.e1 | edge | LATENT | EP07→LN_G04b_1 |
| G04b.e2 | edge | LATENT | LN_G04b_1→EP09 |
| LN_G04c_1 | node | LATENT | G04c |
| G04c.e1 | edge | LATENT | EP01→LN_G04c_1 |
| G04c.e2 | edge | LATENT | LN_G04c_1→EP09 |
| LN_G04d_1 | node | LATENT | G04d |
| G04d.e1 | edge | LATENT | LN_G04d_1→EP09 |
| LN_G04e_1 | node | LATENT | G04e |
| G04e.e1 | edge | LATENT | LN_G04e_1→EP11 |
| LN_G05a_1 | node | LATENT | G05a |
| LN_G05a_2 | node | LATENT | G05a |
| G05a.e1 | edge | LATENT | EP10→LN_G05a_1 |
| G05a.e2 | edge | LATENT | LN_G05a_1→LN_G05a_2 |
| G05a.e3 | edge | LATENT | LN_G05a_2→EP30 |
| LN_G05b_1 | node | LATENT | G05b |
| G05b.e1 | edge | LATENT | EP10→LN_G05b_1 |
| LN_G06a_1 | node | LATENT | G06a |
| LN_G06a_2 | node | LATENT | G06a |
| G06a.e1 | edge | LATENT | EP11→LN_G06a_1 |
| G06a.e2 | edge | LATENT | LN_G06a_1→LN_G06a_2 |
| G06a.e3 | edge | LATENT | LN_G06a_2→EP13 |
| LN_G06b_1 | node | LATENT | G06b |
| LN_G06b_2 | node | LATENT | G06b |
| G06b.e1 | edge | LATENT | EP11→LN_G06b_1 |
| G06b.e2 | edge | LATENT | LN_G06b_1→LN_G06b_2 |
| G06b.e3 | edge | LATENT | LN_G06b_2→EP13 |
| LN_G06c_1 | node | LATENT | G06c |
| LN_G06c_2 | node | LATENT | G06c |
| G06c.e1 | edge | LATENT | EP11→LN_G06c_1 |
| G06c.e2 | edge | LATENT | LN_G06c_1→LN_G06c_2 |
| G06c.e3 | edge | LATENT | LN_G06c_2→EP13 |
| G06c.e4 | edge | LATENT | LN_G06c_1→EP27 |
| LN_G07a_1 | node | LATENT | G07a |
| G07a.e1 | edge | LATENT | EP13→LN_G07a_1 |
| G07a.e2 | edge | LATENT | LN_G07a_1→EP15 |
| LN_G07b_1 | node | LATENT | G07b |
| G07b.e1 | edge | LATENT | LN_G07b_1→EP13 |
| G07b.e2 | edge | LATENT | LN_G07b_1→EP15 |
| LN_G07c_1 | node | LATENT | G07c |
| G07c.e1 | edge | LATENT | LN_G07c_1→EP13 |
| LN_G07d_1 | node | LATENT | G07d |
| G07d.e1 | edge | LATENT | LN_G07d_1→EP15 |
| G07d.e2 | edge | LATENT | LN_G07d_1→EP25 |
| G08a.e1 | edge | LATENT | EP18→EP20 |
| LN_G08b_1 | node | LATENT | G08b |
| G08b.e1 | edge | LATENT | LN_G08b_1→EP20 |
| LN_G09a_1 | node | LATENT | G09a |
| G09a.e1 | edge | LATENT | EP07→LN_G09a_1 |
| G09a.e2 | edge | LATENT | EP04→LN_G09a_1 |
| G09a.e3 | edge | LATENT | LN_G09a_1→EP35 |
| LN_G09b_1 | node | LATENT | G09b |
| LN_G09b_2 | node | LATENT | G09b |
| G09b.e1 | edge | LATENT | EP07→LN_G09b_1 |
| G09b.e2 | edge | LATENT | EP04→LN_G09b_2 |
| G09b.e3 | edge | LATENT | LN_G09b_2→EP35 |
| LN_G09c_1 | node | LATENT | G09c |
| G09c.e1 | edge | LATENT | LN_G09c_1→EP35 |
| LN_G10a_1 | node | LATENT | G10a |
| G10a.e1 | edge | LATENT | EP25→LN_G10a_1 |
| G10a.e2 | edge | LATENT | LN_G10a_1→EP36 |
| LN_G10b_1 | node | LATENT | G10b |
| G10b.e1 | edge | LATENT | LN_G10b_1→EP37 |
| LN_G10c_1 | node | LATENT | G10c |
| G10c.e1 | edge | LATENT | EP36→LN_G10c_1 |
| G10c.e2 | edge | LATENT | LN_G10c_1→EP37 |
| LN_G11a_1 | node | LATENT | G11a |
| G11a.e1 | edge | LATENT | LN_G11a_1→EP05 |
| LN_G11b_1 | node | LATENT | G11b |
| G11b.e1 | edge | LATENT | LN_G11b_1→EP05 |
| LN_G11c_1 | node | LATENT | G11c |
| G11c.e1 | edge | LATENT | LN_G11c_1→EP05 |
| LN_G12a_1 | node | LATENT | G12a |
| G12a.e1 | edge | LATENT | LN_G12a_1→EP27 |
| LN_G12b_1 | node | LATENT | G12b |
| G12b.e1 | edge | LATENT | LN_G12b_1→EP27 |
| LN_G13a_1 | node | LATENT | G13a |
| G13a.e1 | edge | LATENT | EP16→LN_G13a_1 |
| G13a.e2 | edge | LATENT | EP19→LN_G13a_1 |
| G13a.e3 | edge | LATENT | LN_G13a_1→EP32 |
| LN_G13b_1 | node | LATENT | G13b |
| G13b.e1 | edge | LATENT | EP16→LN_G13b_1 |
