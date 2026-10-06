# 구순–김명신 사건(1793) clean 재구성 — 산출물 안내

`gusun_clean_restart_csv_pack/`의 confirmed fact 50개에서 시작해 episode → 검증된 observed partial DAG → gap별 latent 후보 → 소수의 narrative world까지 만든 결과물이다.
각 단계 뒤에는 원본 pack과 다시 대조하는 audit가 있고, ERROR가 하나라도 나오면 다음 단계로 넘어가지 않는다.
SMC·MCMC·particle filtering·posterior sampling·전수 조합은 쓰지 않는다.

## 실행 방법

```bash
pip install duckdb                      # 한 번만
python3 scripts/gusun_clean/build.py    # 저장소 루트에서 실행
```

실행 순서는 STAGE 1 episode → AUDIT 1 → STAGE 2 graph → AUDIT 2 → STAGE 3 동결(sha256) → STAGE 4 gap·latent 후보 → AUDIT 3 → STAGE 5 world → AUDIT 3 재검사(world 포함) → md/CSV 작성 → DuckDB 작성이다.
audit에 ERROR가 있으면 그 자리에서 exit 1로 멈춘다. 같은 입력이면 출력이 바이트 단위로 같다.

| 스크립트 | 역할 |
|---|---|
| `scripts/gusun_clean/build.py` | 전체 실행·gate·동결 해시·DuckDB 작성 |
| `stage1_episodes.py` | episode 37개(EP01–EP37)와 동일성 대장(ID01–ID11) |
| `stage2_graph.py` | 환경 context node 4개, edge 68개, 제도·환경 feature link |
| `stage4_latent.py` | gap 13개, latent 후보 38개, 기계적 등급 `grade()`·`prune()` |
| `stage5_worlds.py` | world 6개(retained 5, rejected 1), 상충 후보 쌍, 무결성 assert |
| `audits.py` | Audit 1·2·3 자동 검사 |
| `manual_review.py` | 원본 CSV 대조 수동 검토표와 실제 수정 이력 |
| `report.py` | md·CSV·mermaid 작성 |

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
| `../../database/gusun_clean.duckdb` | 원본 6표(`raw_*`)와 위 산출물 표, `episode_members`, `dag_freeze`, `audit_findings` |

## Audit 결과 요약

| audit | 판정 | ERROR | WARN | 수동 판정 |
|---|---|---|---|---|
| AUDIT 1 episode fidelity | PASS | 0 | 4 | EP01·EP04·EP05·EP06 어휘 보존율 0.71–0.79. 빠진 것은 진술 어미와 '자신'→진술자 이름뿐이라 왜곡 없음 |
| AUDIT 2 graph fidelity | PASS | 0 | 0 | 조건부 edge 6개와 절차 근거 1개(INFO)를 하나씩 검토 |
| AUDIT 3 observed/latent 분리 | PASS | 0 | 1 | G08a: observed node 사이의 LATENT edge 하나. observed 표에는 들어가지 않음 |

- AUDIT 1: 1차 실행의 ERROR 2건(EP15 '받아들였다', EP32 '인정하지 않았다')은 검사기 어휘 누락에 따른 오탐이었다. 내용이 아니라 검사기를 고쳤다. 이후 미등록 동일성 '원돌'↔'정원돌'을 찾아 ID11로 등록하고 다시 돌렸다.
- AUDIT 3: 1차 실행의 ERROR 2건(audit_attestation 주석)을 고쳤다. 이어서 수동 검토로 찾은 서술상 동일성 단정, 판단 아닌 node로 가는 책임 edge, 진술의 사실화 등을 고치고, 같은 문제를 자동으로 잡는 검사를 추가했다.
- 동결 해시 `86a529da3baf…`는 Stage 4·5 뒤에도 같다. LATENT가 OBSERVED로 둔갑한 경우는 0건이다.

자세한 수동 검토표와 수정 이력은 각 audit 문서 §3·§4에 있다.

## 결과 한눈에

- gap 13개, 후보 38개(HIGH 4 · MEDIUM 17 · LOW 16 · INCOMPATIBLE 1, gap당 2–5개)
- gap별 최고 등급은 HIGH 4개(G01·G06·G07·G08), MEDIUM 9개(G02–G05·G09–G13)다.

| world | 이름 | bridge | 최저 등급 | 상태 |
|---|---|---|---|---|
| W1 | 공식 정보 경로 (정조 최종 판단과 정합) | 12 | MEDIUM | RETAINED |
| W2 | 대질 진술 증폭 경로 | 9 | MEDIUM | RETAINED |
| W3 | 사적 후원 경로 (약함) | 8 | LOW | RETAINED |
| W4 | 분산 지휘 | 8 | LOW | RETAINED |
| W5 | 최소 가정 (HIGH 후보만) | 4 | HIGH | RETAINED |
| W6 | 모함·장형 사망 (이조원·윤노동 쪽 주장) | 3 | LOW | REJECTED (대조용) |

## 핵심 설계 규칙

1. **episode는 confirmed sentence에서만** 만든다. 문장을 원자 명제로 다시 쪼개지 않는다. 예외는 판단 주체(홍대협↔정조) 경계에서 나눈 CF040·CF045 두 건이며, 각 절은 원문 substring이다.
2. **진술은 진술로** 둔다. 진술 episode의 summary에는 진술 귀속이 있고, 진술 내용 속 순서를 잇는 edge는 `claim_level`로 표시한다. 중첩 진술(CF005)은 NESTED_TESTIMONY로 둔다.
3. **동일성을 확정하지 않는다.** 병사=이광섭(ID01), 한 비장=한재욱(ID02), 한가=한재욱(ID03), 하급 보조자=한재욱(ID04)을 포함한 미확정 동일성은 대장에만 두고, edge는 `condition`으로, 후보는 가정과 `identity_conditions`로만 참조한다. 동일성에 기대는 후보는 HIGH가 될 수 없다.
4. **CAUSES edge는 0개다.** 정조의 책임 귀속은 `RESPONSIBILITY_LINK`로 표현하고 royal judgment node로만 들어간다. 김명신 사망은 생물학적 branch A(홍대협 질병 평가 → 정조 전염병 판단, 환경 context)와 절차·책임 branch B(구순 쪽 사슬, 이광섭 쪽 사슬)로 나뉘며, 구순 → 사망 직접 edge는 없다.
5. **판단 변화를 지우지 않는다.** 5월 '도난 없음 방향'과 6월 '도난 실재'를 모두 node로 두고 `REVIEW_OF`·`REVISES`·`CONTRADICTS_AT_CLAIM_LEVEL`로 잇는다.
6. **제도 피쳐는 사건을 만들지 않는다.** 제도는 compatibility 평가이며 확률이 아니다. 제도 compatibility만 근거인 edge는 없고, 그런 후보는 LOW 상한이다.
7. **환경은 context다.** 환경 node는 판단·보고 node로 가는 `CONTEXT_SUPPORTS`의 출발점으로만 쓴다. 개인 감염 같은 개인 수준 사건을 환경에서 만들지 않는다. E004(5/12)는 사망 이후라 context로만 쓴다.
8. **05(AUDIT_ONLY)는 DAG 입력이 아니다.** latent 후보의 `audit_attestation`으로만 인용하고, 인용해도 후보는 LATENT로 남는다.
9. **observed DAG는 Stage 3에서 동결한다.** Stage 4·5는 동결본을 바꾸지 않고, LATENT 요소는 별도 표(`latent_*`)에만 있다.
10. **world는 손으로 고른다.** 전수 조합 없이 설명 축이 다른 world 몇 개만 둔다. gap마다 후보는 최대 1개이고, 상충 쌍은 함께 쓰지 않으며, world 쌍마다 2개 이상 gap에서 다르다. 서술의 `[L]`이 LATENT 부분이다.
