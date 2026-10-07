# Python vs Oracle 독립 재검증 — 비교 항목

Oracle SQL 레이어의 목적은 Python 결과를 **다른 구현으로 다시 계산해** 같은 답이 나오는지 보는 것이다.
기대값은 Python 산출물에서 읽었다(`extract_expected_from_python.py` → `expected_counts.sql` 1부). 손으로 적은 값이 없다.
Oracle 쪽 값은 canonical 표에서 SQL로 다시 센다(`expected_counts.sql` 2부 `v_oracle_actual_count`, Python 결과를 참조하지 않음).

> Oracle runtime unavailable — 아래 'DuckDB 에뮬레이션' 열은 같은 SQL을 DuckDB로 옮겨 돌린 값이다(Oracle 실행이 아님). Oracle에서 `@sql/08_validation/expected_counts.sql`을 실행하면 'oracle_value' 열이 채워진다.

## 1. 구조 지표

| 지표 (metric_id) | Python 기대값 | 출처 | Oracle SQL 계산 | DuckDB 에뮬레이션 |
|---|---|---|---|---|
| canonical node count (`canonical_node_count`) | 41 | output/clean/episode_nodes.csv | `COUNT(*) FROM dag_node` | 41 MATCH |
| canonical edge count (`canonical_edge_count`) | 68 | output/clean/observed_edges.csv | `COUNT(*) FROM dag_edge` | 68 MATCH |
| 동결 기록 node·edge (`freeze_n_nodes`·`freeze_n_edges`) | 41 · 68 | observed_dag_freeze.json | `dag_freeze` | MATCH |
| episode count (`episode_count`) | 37 | episode_nodes.csv (layer ≠ ENVIRONMENT) | `layer <> 'ENVIRONMENT'` | 37 MATCH |
| 환경 context node (`env_context_node_count`) | 4 | episode_nodes.csv | `layer = 'ENVIRONMENT'` | 4 MATCH |
| node status별 (`node_status_OBSERVED`) | OBSERVED 41 | episode_nodes.csv | `GROUP BY node_status` | MATCH |
| edge status별 (`edge_status_*`) | OBSERVED 4 · DERIVED 64 | observed_edges.csv | `GROUP BY status` | MATCH |
| Super-DAG node status별 (`sd_node_status_*`) | OBSERVED 37 · LATENT_MECHANISM 55 · CONTEXT 24 · UNRESOLVED 6 | mechanism_super_dag_nodes.csv | `GROUP BY sd_status` | MATCH |
| Super-DAG edge status별 (`sd_edge_status_*`) | DERIVED 64 · OBSERVED 4 · LATENT_MECHANISM 90 · CONTEXT 38 · UNRESOLVED 9 | mechanism_super_dag_edges.csv | `GROUP BY sd_status` | MATCH |
| source count (`source_count`) | 8 | 04_source_records.csv | `source_record` | 8 MATCH |
| 확정 사실 (`confirmed_fact_count`) | 50 | 01_confirmed_facts.csv | `confirmed_fact` | 50 MATCH |
| audit 명제 (`audit_proposition_count`) | 156 | 05_…AUDIT_ONLY.csv | `audit_proposition` | 156 MATCH |
| world count (`world_count`) | 6 (경쟁 5 · 배제 1) | narrative_worlds.csv | `narrative_world` | MATCH |
| world bridge 합계 (`world_bridge_total`) | 44 | narrative_worlds.latent_bridges | `world_candidate` 행 수 | 44 MATCH |
| candidate count (`candidate_count`, `candidate_status_LATENT`) | 38 · 38 | latent_candidates.csv | `latent_candidate` | MATCH |
| final HIGH 후보 (`candidate_overall_HIGH`) | 0 | latent_candidates.csv | `overall = 'HIGH'` | 0 MATCH |
| gap count (`gap_count`) | 13 | gaps.csv | `gap` | 13 MATCH |
| mechanism count (`mechanism_count`) | 7 | mechanism_definitions.csv | `mechanism` | 7 MATCH |

## 2. unresolved 지표

| 지표 | Python 기대값 | 출처 | Oracle SQL 계산 | DuckDB 에뮬레이션 |
|---|---|---|---|---|
| 미확정 동일성 (`identity_unresolved_count`) | 4 (ID04·06·07·08) | identity_register.csv | `status = 'UNRESOLVED'` | 4 MATCH |
| 사용자 확정 동일성 (`identity_resolved_count`) | 5 (ID01·02·03·05·11) | identity_register.csv | `status = 'RESOLVED'` | 5 MATCH |
| 열어 둔 gap (`gap_open_unresolved_count`) | 1 (G10) | gaps.csv | `gap_status = 'OPEN_UNRESOLVED'` | 1 MATCH |
| 불확실성 표시 edge (`edge_uncertainty_count`) | 5 | observed_edges.csv | `COUNT(uncertainty_status)` | 5 MATCH |
| Super-DAG UNRESOLVED node | 6 | mechanism_super_dag_nodes.csv | `sd_node_status_UNRESOLVED` | 6 MATCH |
| Python audit UNRESOLVED (`py_audit1~4_unresolved`) | 4 · 5 · 1 · 20 | DuckDB audit_findings | `v_sql_audit_all` severity = UNRESOLVED | 4 · 5 · 1 · 20 MATCH (대상 id까지 일치) |

## 3. 무결성 지표 (정상 = 0)

| 지표 | Python 기대값 | Python 쪽 근거 | Oracle SQL 계산 | DuckDB 에뮬레이션 |
|---|---|---|---|---|
| duplicate edge count (`duplicate_edge_count`) | 0 | observed_edges.csv의 (src, dst, edge_type) 중복 묶음 | `GROUP BY … HAVING COUNT(*) > 1` | 0 MATCH |
| self-loop count (`self_loop_count`) | 0 | observed_edges.csv `src = dst` | `src = dst` (+CHECK) | 0 MATCH |
| cycle count (`cycle_count`) | 0 | Audit 2 acyclicity ERROR 수 | `CONNECT_BY_ISCYCLE = 1` 행 수 | 0 MATCH (DuckDB는 재귀 CTE로 대체) |
| unsupported DERIVED edge count (`unsupported_derived_edge_count`) | 0 | `status = DERIVED`이고 supporting 빈 edge | `NOT EXISTS edge_source_basis` | 0 MATCH |
| CAUSES edge (`causes_edge_count`) | 0 | observed_edges.csv | `edge_type = 'CAUSES'` (+CHECK) | 0 MATCH |
| direct causal death edge count (`direct_causal_death_edge_count`) | 0 | audits.py FORBIDDEN_DIRECT {EP01·EP08·EP10·EP29} → {EP13·EP26·EP27} | `rule_set_member` 두 집합 조인 | 0 MATCH |

## 4. Audit 결과 대조 (audit × severity)

| Audit | Python ERROR / WARN / UNRESOLVED / INFO | SQL (에뮬레이션) | 비고 |
|---|---|---|---|
| AUDIT 1 episode fidelity | 0 / 0 / 4 / 13 | 0 / 0 / 4 / 13 | check 단위로도 일치 |
| AUDIT 2 graph fidelity | 0 / 0 / 5 / 1 | 0 / 0 / 5 / 1 | 〃 |
| AUDIT 3 observed/latent 분리 | 0 / 0 / 1 / 11 | 0 / 0 / 1 / 11 | 〃 (freeze INFO는 해시 대신 집계 대조) |
| AUDIT 4 mechanism Super-DAG | 0 / 0 / 20 / 2 | 0 / 0 / 20 / 2 | 〃 |
| AUDIT 5 interactive visualization | 0 / 0 / 0 / 5 | — | NOT PORTED (화면 데이터 검사) |

`expected_counts.sql` 비교 결과(에뮬레이션): **MATCH 56 · NOT PORTED 3(py_audit5_*) · DIFF 0**.

## 5. Python만 할 수 있는 것과 SQL만 하는 것

- Python만: 동결 sha256 재계산(값 자체는 `dag_freeze`에 보존: `ccb7ec63…`), 어휘 보존율, 전후방 탐색 정규식, world configuration 재계산, Audit 5. (`sql/README.md` §6 NOT PORTED)
- SQL 추가: 중복 edge 검사(INV05), 2-cycle·같은 node 쌍 다중 type 보고(`06_graph/cycle_checks.sql`), 적재 정규화 누락 검사, DuckDB episode_members ↔ episode_nodes.member_fact_ids 교차 검증(`02_load/03_load_validation.sql` §3).
