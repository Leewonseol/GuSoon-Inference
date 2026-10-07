# 구순–김명신 사건(1793) clean 재구성 — 산출물 안내

`gusun_clean_restart_csv_pack/`의 confirmed fact 50개에서 시작해 episode → 검증된 observed partial DAG → gap별 latent 후보 → 소수의 narrative world → mechanism Super-DAG → 탐색용 interactive temporal DAG(`docs/`)까지 만든 결과물이다.
각 단계 뒤에는 원본 pack과 다시 대조하는 audit가 있고, ERROR가 하나라도 나오면 다음 단계로 넘어가지 않는다.
SMC·MCMC·particle filtering·posterior sampling·전수 조합은 쓰지 않는다.

## 실행 방법

```bash
pip install duckdb                      # 한 번만
python3 scripts/gusun_clean/build.py    # 저장소 루트에서 실행
```

실행 순서는 STAGE 1 episode → AUDIT 1 → STAGE 2 graph → AUDIT 2 → STAGE 3 동결(sha256) → STAGE 4 gap·latent 후보 → AUDIT 3 → STAGE 5 world → AUDIT 3 재검사(world 포함) → STAGE 6 mechanism Super-DAG(질적 SCM) → AUDIT 4 → STAGE 7 interactive temporal DAG 데이터(`docs/data`) → AUDIT 5 → md/CSV 작성 → DuckDB 작성이다.
Audit 1 전에 regression 케이스 59개(`regression.py`, Audit 4용 10개·Audit 5용 23개 포함)를 검사기에 넣어 모두 잡히는지 먼저 확인한다. Audit 5 케이스는 `output/clean`의 canonical 산출물로 화면 데이터를 메모리에서 만든 뒤 사본만 바꿔 넣는다. audit에 ERROR 또는 disposition 없는 WARN이 있으면 그 자리에서 exit 1로 멈춘다. 같은 입력이면 출력이 바이트 단위로 같다.

| 스크립트 | 역할 |
|---|---|
| `scripts/gusun_clean/build.py` | 전체 실행·gate·동결 해시·DuckDB 작성 |
| `stage1_episodes.py` | episode 37개(EP01–EP37)와 동일성 대장(ID01–ID11) |
| `stage2_graph.py` | 환경 context node 4개, edge 68개, 제도·환경 feature link |
| `stage4_latent.py` | gap 13개, latent 후보 38개, 기계적 등급 `grade()`·`prune()` |
| `stage4_reaudit.py` | LATENT 후보 38개의 bridge 근거 재감사 값 |
| `stage5_worlds.py` | world 6개(경쟁 설명 5, rejected 1), 상충 후보 쌍, 무결성 assert |
| `stage6_mechanisms.py` | 메커니즘 7개, 후보 → 메커니즘 매핑, 질적 구조 변수, world configuration·공존·개입 규칙 |
| `build_visualization.py` | canonical CSV → `docs/data/*.json`·`bundle.js`(interactive temporal DAG 데이터, 결정적 preset 좌표). 단독 실행 가능 |
| `test_visualization.py` | `docs/`를 로컬 http 서버로 띄워 헤드리스 Chromium(Playwright)으로 화면을 검사하는 UI 테스트 27항목(글자 크기·line-height·label 잘림·첫 화면 배율 포함) |
| `audits.py` | Audit 1·2·3·4·5 자동 검사 |
| `regression.py` | 과거 결함·금지 규칙 59개를 검사기가 다시 잡는지 확인하는 regression 케이스 |
| `manual_review.py` | 원본 CSV 대조 수동 검토표와 실제 수정 이력 |
| `report.py` · `report_mech.py` | md·CSV·mermaid 작성(Stage 1–5 · Stage 6) |

## 파일 지도

| 파일 | 내용 |
|---|---|
| `00_preflight_report.md` | 구현 전 입력 pack 실측과 합의된 계획 |
| `episode_nodes.csv` | observed node 41개(episode 37 + 환경 4). 모두 OBSERVED |
| `observed_edges.csv` | observed edge 68개(OBSERVED 4, DERIVED 64). basis·claim_level·identity condition 포함 |
| `node_feature_links.csv` | 제도(F001–F020)·환경(E001–E004) 평가 링크 57개. `creates_event=NO` |
| `identity_register.csv` | 확정하지 않는 동일성 대장(ID01–ID11) |
| `observed_dag.md` | 동결 DAG의 mermaid 그림 |
| `observed_dag_freeze.json` | 동결 해시와 집계 |
| `gap_candidates.md` · `gaps.csv` · `latent_candidates.csv` · `latent_elements.csv` | gap 13개와 LATENT 후보·요소 |
| `narrative_worlds.md` · `narrative_worlds.csv` | world 6개, 비교표, 상충 쌍, gap별 선택표 |
| `audit_1_episode_fidelity.md` | episode 충실도 audit |
| `audit_2_graph_fidelity.md` | graph 충실도 audit |
| `audit_3_observed_latent_separation.md` | OBSERVED / DERIVED / LATENT 분리 audit |
| `validation_summary.md` | 최종 audit count, UNRESOLVED 목록, regression 규칙, 해시 비교 |
| `manual_review_table.md` | 사람이 판단할 항목만 모은 검토표 |
| `narrative_world_story_matrix.md` | 공통 OBSERVED 사실·결말과 world별 LATENT 가설을 한 장에서 구분한 표 |
| `latent_candidate_reaudit.md` | LATENT 후보 38개의 bridge 근거 재감사(before/after) |
| `mechanism_super_dag.md` · `mechanism_super_dag.mmd` | 메커니즘 Super-DAG 개요(정의·제도 제약·configuration·공존·branch 분리)와 세 패널 Mermaid |
| `mechanism_super_dag_nodes.csv` · `mechanism_super_dag_edges.csv` | Super-DAG node·edge(OBSERVED / DERIVED / LATENT_MECHANISM / CONTEXT / UNRESOLVED). frozen node·edge는 그대로 복사 |
| `mechanism_definitions.csv` | 메커니즘 정의표 |
| `world_mechanism_configurations.csv` | world별 메커니즘 값(ON / OFF / PARTIAL / UNSPECIFIED)과 판정 근거 |
| `mechanism_interaction_matrix.csv` | 메커니즘 쌍 공존 분석(COMPATIBLE / PARTIALLY_COMPATIBLE / INCOMPATIBLE / UNKNOWN) |
| `qualitative_structural_rules.md` | OR / AND / XOR / ANCHORED 질적 구조 규칙 |
| `mechanism_interventions.md` · `mechanism_interventions.csv` | do(M=OFF) 질적 개입 결과(PATH_REMAINS / WEAKENS / BREAKS / UNKNOWN). CSV는 같은 값을 기계가 읽는 형태로 낸 것 |
| `qualitative_structural_rules.csv` | `qualitative_structural_rules.md`의 구조 변수·연산(OR/AND/XOR/ANCHORED)·입력 후보를 CSV로 낸 것 |
| `audit_4_mechanism_super_dag.md` | Super-DAG audit, Audit 4 regression 10건 |
| `audit_5_interactive_visualization.md` | 화면 데이터(docs/data)·관점별 View·가독성 audit, Audit 5 regression 23건 |
| `../../docs/` | Interactive Temporal DAG(정적 웹 페이지). `index.html`·`css/app.css`·`js/app.js`·`data/*.json`·`data/bundle.js`·`vendor/cytoscape/`(Cytoscape.js 3.30.4, MIT, LICENSE 포함) |
| `warn_dispositions.csv` | WARN별 disposition (FIXED / RECLASSIFIED_INFO / UNRESOLVED / ESCALATED_ERROR) |
| `../../database/gusun_clean.duckdb` | 원본 6표(`raw_*`)와 위 산출물 표, `episode_members`, `dag_freeze`, `audit_findings` |

## Audit 결과 요약

| audit | 판정 | ERROR | WARN | UNRESOLVED | INFO |
|---|---|---|---|---|---|
| AUDIT 1 episode fidelity | PASS | 0 | 0 | 4 (미확정 동일성, ID04 참고용 포함) | 13 |
| AUDIT 2 graph fidelity | PASS | 0 | 0 | 5 (조건부 edge 3, 부분 충돌 2) | 1 |
| AUDIT 3 observed/latent 분리 | PASS | 0 | 0 | 1 (G10) | 11 |
| AUDIT 4 mechanism Super-DAG | PASS | 0 | 0 | 20 (방향 미결 8, 공존 미결 2, 복수 설명 4, 기존 미해결 6) | 2 |
| AUDIT 5 interactive visualization | PASS | 0 | 0 | 0 | 5 |

- 통과 조건은 ERROR 0, WARN 0이다. 이전 실행의 WARN 5건(A1-W1–W4, A3-W1)은 모두 FIXED로 처리했다. 새 regression 규칙이 찾아낸 EP07 1건(A1-E1)은 ESCALATED_ERROR로 올린 뒤 고쳤다. 처리 내역은 `warn_dispositions.csv`와 각 audit 문서의 WARN disposition 절에 있다.
- 사용자 수동 검토로 ID01(병사=이광섭)·ID02(한 비장=한재욱)·ID03(한가=한재욱)·ID05(풍각 김상제=김명신)·ID11(원돌=정원돌)을 확정했다(`identity_register.csv`의 status=RESOLVED, resolved_by=USER). episode summary는 원문 표면형을 그대로 두고, 확정된 ID는 edge condition과 후보 가정에서 뺐다. 확정과 충돌하는 후보 G09b·G09c는 PRUNED 처리했다(어느 world에도 쓰이지 않던 후보). 사람이 판단할 항목은 `manual_review_table.md`에 있다. 사용자 검토에서 ID06·ID07·ID08·OE007·OE062·G10은 추가 사료 없이 확정하지 않기로 했다. 이 항목들은 오류가 아니라 보존된 불확실성이며 `identity_register.csv`(review_decision), `observed_edges.csv`(uncertainty_status), `gaps.csv`(gap_status)에 기록되어 있다.
- UNRESOLVED는 사료 자체가 결정해 주지 않는 동일성·부분 충돌·gap이다. 데이터에는 condition·caution·unresolved_reason으로 보존한다. 전체 목록은 `validation_summary.md`에 있다.
- AUDIT 1: 1차 실행의 ERROR 2건(EP15 '받아들였다', EP32 '인정하지 않았다')은 검사기 어휘 누락에 따른 오탐이었다. 내용이 아니라 검사기를 고쳤다. 이후 미등록 동일성 '원돌'↔'정원돌'을 찾아 ID11로 등록하고 다시 돌렸다.
- AUDIT 3: 1차 실행의 ERROR 2건(audit_attestation 주석)을 고쳤다. 이어서 수동 검토로 찾은 서술상 동일성 단정, 판단 아닌 node로 가는 책임 edge, 진술의 사실화 등을 고치고, 같은 문제를 자동으로 잡는 검사를 추가했다.
- Narrative world: W1–W5는 하나를 고르는 후보가 아니라 함께 보존하는 경쟁 설명(COMPETING_EXPLANATION)이다. W6은 배제된 설명(REJECTED)이다. 재검토·최종 판단·처분은 모든 world에 공통인 OBSERVED 결말이고, world들은 그 앞의 미확인 경로만 다르게 설명한다. 서로 다른 world의 LATENT 가설은 합치지 않는다.
- LATENT 재감사: 후보가 새로 추가한 bridge 내용 자체의 사료 근거만 source support로 다시 평가했다(양끝 관측 사실의 확실성·시간 인접·제도 가능성은 제외). HIGH 후보는 4개에서 0개가 되었다. final 등급은 근거 등급(evidence)과 개연성(plausibility) 중 낮은 쪽이다. 상세: `latent_candidate_reaudit.md`.
- 동결 해시: `86a529da3baf…` → `c50402af878f…`(WARN 처리로 EP01·EP04–EP07 문구 수정) → `005d4b7df030…`(동일성 확정으로 OE007·OE081 condition 제거) → `ccb7ec63763a…`(ID05 확정으로 OE071 condition에서 ID05 제거). node·edge id·끝점·type을 본 topology 해시는 그대로이고, Stage 4·5 뒤에도 observed DAG는 변하지 않는다. LATENT가 OBSERVED로 둔갑한 경우는 0건이다.

- Mechanism Super-DAG(Stage 6): 기존 후보를 묶어 메커니즘 7개(M1–M6, MB)를 만들고, 각 world를 메커니즘 configuration으로 다시 읽었다. configuration은 world의 실제 bridge에서 규칙으로 계산했다. 관측 node·edge·후보 내용·등급은 바꾸지 않았고 확률·SEM 계수는 쓰지 않았다. 동결 해시 그대로.

자세한 수동 검토표와 수정 이력은 각 audit 문서 §3·§4에 있다.

## Interactive Temporal DAG (docs/)

`mechanism_super_dag.mmd`(Mermaid)는 정적 문서 요약이고, `docs/index.html`은 탐색용 화면이다. 둘 다 같은 canonical CSV에서 나온다.
화면은 이미 있는 데이터만 보여 준다. 새 node·edge·사실·판단을 만들지 않고, 상태·configuration·공존 판정·개입 결과·후보 등급은 CSV 값을 그대로 쓴다.

- 배치: Cytoscape.js `preset` 좌표(물리 시뮬레이션 없음, node 이동 불가). 좌표는 `build_visualization.py`가 결정적으로 계산한다. 날짜 있는 관측 node는 정렬 기준일(t_max, 없으면 t_min) 순서로 왼쪽 → 오른쪽(2월 → 3월 → 5월 → 6월 → 최종 판단·처분), 같은 날짜 안에서는 frozen edge 깊이 순서다. 날짜가 없는 EP08은 시간 축 밖 '날짜 미기록' 구간에 둔다. 메커니즘·구조 변수·후보·context·UNRESOLVED는 별도 lane이고 x는 연결된 node 근처일 뿐 날짜가 아니다.
- 관점별 View 10개(`docs/data/views.json`): A 전체 Overview · B 시간순 사건 · C 구순→김명신 수사선상 · D 병영 지휘·체포 · E 자미덕·진술·대질 · F 김명신 구금·사망(A 생물학적 경과 / B 절차·책임, 직접 edge 0) · G 5월 재검토 · H 홍대협 재조사 · I 정조 최종 판단·처분 · J LATENT·World 비교.
  View는 canonical node·edge의 부분집합과 표시 좌표만 담는다(새 node·edge·상태·해석 없음). 각 View의 선택 규칙(핵심 관측 node, 맥락 관측 node, gap별 후보, 그 후보의 메커니즘·UNRESOLVED)은 화면의 '선택 규칙 보기'와 `scope_rule`에 그대로 적혀 있다.
  B–I는 범위 밖 node를 숨기고(시각적 필터, 분석상 ON/OFF 아님) 숨긴 OBSERVED 개수·ID를 늘 보여 준다. '전체 주변 맥락 표시'를 켜면 전체 node가 Overview 좌표로 다시 나타나고 범위 밖 node는 흐리게 표시된다. J는 범위 밖 OBSERVED를 흐리게만 한다.
- 가독성: node label 16px(12pt)·line-height 1.6, UI 글자 15px(11.25pt) 이상·line-height 1.6. node는 'ID + canonical label 전체'를 줄바꿈해 담고(말줄임 없음) 높이가 줄 수에 맞춰 늘어난다. 모든 View의 첫 화면 배율은 0.95 이상(node 글자 15.2px)이고, 화면에 다 들어오지 않으면 시간상 앞쪽(핵심 node가 부족하면 핵심 node가 가장 많은 곳)부터 보여 준다. 휠 = 스크롤, Ctrl/⌘+휠 = 확대, '전체 지도' = 한 화면 축소(ID만 표시). lane·시간 구간 이름은 화면 밖으로 나가면 가장자리에 고정된다. 다른 node 밑을 지나는 edge는 결정적으로 고른 곡선으로 그린다.
- 왼쪽: world 선택(ALL·W1–W5·W6 REJECTED), 표시 필터(Status·Mechanism — 분석상 ON/OFF가 아님), 검색, 초기화, 범례. 오른쪽: 상세 · World 구성 · 공존 · 개입 패널.
- OBSERVED backbone(관측 node 37개, 공통 결말 23개 포함)은 어떤 world·필터·개입에서도 숨기지 않는다. Overview·J·'전체 주변 맥락 표시'에서는 늘 전부 보이고, B–I에서는 View 범위의 관측 node가 늘 보이며 범위 밖은 안내와 함께 숨긴다(Audit 5 `outcome_dropped`·`view_hidden_notice_missing`, UI 테스트 13·14·15).

로컬에서 보기:

```bash
python3 -m http.server -d docs 8000      # 저장소 루트에서. 브라우저로 http://localhost:8000/
```

`docs/data/bundle.js`에 같은 데이터가 들어 있어 `docs/index.html`을 파일로 바로 열어도(file://) 동작한다. 외부 CDN을 쓰지 않는다.

UI 테스트(헤드리스 Chromium):

```bash
pip install playwright                   # 한 번만. 브라우저가 없으면 python3 -m playwright install chromium
python3 scripts/gusun_clean/test_visualization.py [--shots 스크린샷폴더]
```

GitHub Pages: 저장소 Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: 이 브랜치(또는 병합한 기본 브랜치) · 폴더 `/docs` → Save. `docs/.nojekyll`이 있어 그대로 정적 파일로 배포된다.

## 결과 한눈에

- gap 13개, 후보 38개(재감사 후 final: MEDIUM 7 · LOW 28 · INCOMPATIBLE 3, HIGH 0)
- gap별 최고 등급은 MEDIUM 7개(G01–G04·G06·G07·G10), LOW 6개(G05·G08·G09·G11–G13)다.

| world | 역할 | bridge | 메커니즘 configuration (M1 M2 M3 M4 M5 M6 MB) |
|---|---|---|---|
| W1 | 공식 정보 경로 | 12 | ON · UNSPECIFIED · PARTIAL · PARTIAL · ON · ON · ON |
| W2 | 대질 진술 증폭 경로 | 9 | PARTIAL · ON · UNSPECIFIED · ON · ON · PARTIAL · ON |
| W3 | 사적 후원 경로 | 8 | PARTIAL · UNSPECIFIED · ON · UNSPECIFIED · ON · ON · ON |
| W4 | 분산 지휘 | 8 | PARTIAL · PARTIAL · UNSPECIFIED · ON · ON · PARTIAL · ON |
| W5 | 최소 가정 | 4 | PARTIAL · UNSPECIFIED · UNSPECIFIED · UNSPECIFIED · ON · ON · ON |
| W6 | 모함·장형 사망 — REJECTED(대조군) | 3 | 공존·개입 분석에서 제외 |

## 핵심 설계 규칙

1. **episode는 confirmed sentence에서만** 만든다. 문장을 원자 명제로 다시 쪼개지 않는다. 예외는 판단 주체(홍대협↔정조) 경계에서 나눈 CF040·CF045 두 건이며, 각 절은 원문 substring이다.
2. **진술은 진술로** 둔다. 진술 episode의 summary에는 진술 귀속이 있고, 진술 내용 속 순서를 잇는 edge는 `claim_level`로 표시한다. 중첩 진술(CF005)은 NESTED_TESTIMONY로 둔다.
3. **동일성을 강제하지 않는다.** 사용자가 확정한 ID01·ID02·ID03·ID05·ID11 밖의 미확정 동일성(ID06·ID07·ID08 등)은 대장에만 두고, edge는 `condition`으로, 후보는 가정과 `identity_conditions`로만 참조한다. 동일성에 기대는 후보는 HIGH가 될 수 없다.
4. **CAUSES edge는 0개다.** 정조의 책임 귀속은 `RESPONSIBILITY_LINK`로 표현하고 royal judgment node로만 들어간다. 김명신 사망은 생물학적 branch A(홍대협 질병 평가 → 정조 전염병 판단, 환경 context)와 절차·책임 branch B(구순 쪽 사슬, 이광섭 쪽 사슬)로 나뉘며, 구순 → 사망 직접 edge는 없다.
5. **판단 변화를 지우지 않는다.** 5월 '도난 없음 방향'과 6월 '도난 실재'를 모두 node로 두고 `REVIEW_OF`·`REVISES`·`CONTRADICTS_AT_CLAIM_LEVEL`로 잇는다.
6. **제도 피쳐는 사건을 만들지 않는다.** 제도는 compatibility 평가이며 확률이 아니다. 제도 compatibility만 근거인 edge는 없고, 그런 후보는 LOW 상한이다.
7. **환경은 context다.** 환경 node는 판단·보고 node로 가는 `CONTEXT_SUPPORTS`의 출발점으로만 쓴다. 개인 감염 같은 개인 수준 사건을 환경에서 만들지 않는다. E004(5/12)는 사망 이후라 context로만 쓴다.
8. **05(AUDIT_ONLY)는 DAG 입력이 아니다.** latent 후보의 `audit_attestation`으로만 인용하고, 인용해도 후보는 LATENT로 남는다.
9. **observed DAG는 Stage 3에서 동결한다.** Stage 4·5는 동결본을 바꾸지 않고, LATENT 요소는 별도 표(`latent_*`)에만 있다.
10. **world는 손으로 고른다.** 전수 조합 없이 설명 축이 다른 world 몇 개만 둔다. gap마다 후보는 최대 1개이고, 상충 쌍은 함께 쓰지 않으며, world 쌍마다 2개 이상 gap에서 다르다. 서술의 `[L]`이 LATENT 부분이다.
11. **메커니즘은 분석 변수다.** World = configuration, Mechanism = 분석 변수, Observed fact = 고정, Context feature = 제약조건, Latent bridge = 가설, Outcome = confirmed backbone. 제도·환경 context는 메커니즘을 제약할 뿐 사건을 만들지 않고, M5(재검토·교정)는 관측 backbone에 고정되어 world마다 달라지지 않는다. 사망 branch A(MB)와 책임 branch B(M1–M4)를 잇는 edge는 없다.
12. **화면은 canonical을 보여 주기만 한다.** `docs/data`는 canonical CSV에서 결정적으로 생성되고 Audit 5가 node·edge·상태·configuration·후보 등급·개입 결과·시간 순서·W6 REJECTED·공통 결말 표시를 다시 대조한다. 화면 편의를 위해 node·edge를 만들지 않는다.
