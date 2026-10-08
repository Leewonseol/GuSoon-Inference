-- =============================================================================
-- expected_counts.sql — Python 산출물에서 읽은 기대값 + Oracle에서 독립 계산한 실제값 비교
-- -----------------------------------------------------------------------------
-- 1부(INSERT)는 sql/08_validation/extract_expected_from_python.py가 Python 산출물을 읽어 생성했다.
--   값을 손으로 적지 않았다. 동결 해시(참고): ccb7ec63763a715ae90c74dfff37d3ed7980fa705fd152f59de8bed2e31d4e0c
-- 2부(비교 질의)는 Oracle canonical 표에서 같은 지표를 다시 센다(Python 결과를 참조하지 않음).
-- 선행: 01_schema, 02_load, 03_views, 05_audits (py_* 지표 비교에는 v_sql_audit_all이 필요)
-- 정상: 마지막 질의의 comparison 컬럼이 모두 MATCH (py_audit5_*는 NOT PORTED)
-- =============================================================================

DELETE FROM expected_count;

INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('audit_proposition_count', 156, 'gusun_clean_restart_csv_pack/05_…AUDIT_ONLY.csv', 'audit 전용 명제 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('candidate_count', 38, 'output/clean/latent_candidates.csv', 'LATENT 후보 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('candidate_overall_HIGH', 0, 'output/clean/latent_candidates.csv', 'final HIGH 후보 수(재감사 후 0)');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('candidate_status_LATENT', 38, 'output/clean/latent_candidates.csv', 'status=LATENT 후보 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('canonical_edge_count', 68, 'output/clean/observed_edges.csv', '동결 observed edge 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('canonical_node_count', 41, 'output/clean/episode_nodes.csv', '동결 observed node 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('causes_edge_count', 0, 'output/clean/observed_edges.csv', 'CAUSES edge 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('confirmed_fact_count', 50, 'gusun_clean_restart_csv_pack/01_confirmed_facts.csv', '확정 사실 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('cycle_count', 0, 'database/gusun_clean.duckdb audit_findings', 'Python Audit 2 acyclicity ERROR 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('direct_causal_death_edge_count', 0, 'output/clean/observed_edges.csv + audits.py FORBIDDEN_DIRECT', '구순 관련 node → 사망·사인 node 직접 edge 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('duplicate_edge_count', 0, 'output/clean/observed_edges.csv', '(src,dst,type) 중복 묶음 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('edge_status_DERIVED', 64, 'output/clean/observed_edges.csv', '동결 edge status=DERIVED');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('edge_status_OBSERVED', 4, 'output/clean/observed_edges.csv', '동결 edge status=OBSERVED');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('edge_uncertainty_count', 5, 'output/clean/observed_edges.csv', 'uncertainty_status가 있는 edge 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('env_context_node_count', 4, 'output/clean/episode_nodes.csv', '환경 context node 수(ENV)');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('episode_count', 37, 'output/clean/episode_nodes.csv', 'episode node 수(EP)');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('freeze_n_edges', 68, 'output/clean/observed_dag_freeze.json', '동결 기록의 edge 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('freeze_n_nodes', 41, 'output/clean/observed_dag_freeze.json', '동결 기록의 node 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('gap_count', 13, 'output/clean/gaps.csv', 'gap 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('gap_open_unresolved_count', 1, 'output/clean/gaps.csv', 'OPEN_UNRESOLVED gap 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('identity_resolved_count', 5, 'output/clean/identity_register.csv', '사용자 확정 동일성 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('identity_unresolved_count', 4, 'output/clean/identity_register.csv', 'UNRESOLVED 동일성 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('mechanism_count', 7, 'output/clean/mechanism_definitions.csv', '메커니즘 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('node_status_OBSERVED', 41, 'output/clean/episode_nodes.csv', '동결 node status=OBSERVED');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit1_error', 0, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT1 ERROR finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit1_info', 13, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT1 INFO finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit1_unresolved', 4, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT1 UNRESOLVED finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit1_warn', 0, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT1 WARN finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit2_error', 0, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT2 ERROR finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit2_info', 1, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT2 INFO finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit2_unresolved', 5, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT2 UNRESOLVED finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit2_warn', 0, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT2 WARN finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit3_error', 0, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT3 ERROR finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit3_info', 11, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT3 INFO finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit3_unresolved', 1, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT3 UNRESOLVED finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit3_warn', 0, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT3 WARN finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit4_error', 0, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT4 ERROR finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit4_info', 2, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT4 INFO finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit4_unresolved', 20, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT4 UNRESOLVED finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit4_warn', 0, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT4 WARN finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit5_error', 0, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT5 ERROR finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit5_info', 5, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT5 INFO finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('py_audit5_warn', 0, 'database/gusun_clean.duckdb audit_findings', 'Python AUDIT5 WARN finding 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('sd_edge_status_CONTEXT', 38, 'output/clean/mechanism_super_dag_edges.csv', 'Super-DAG edge status=CONTEXT');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('sd_edge_status_DERIVED', 64, 'output/clean/mechanism_super_dag_edges.csv', 'Super-DAG edge status=DERIVED');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('sd_edge_status_LATENT_MECHANISM', 90, 'output/clean/mechanism_super_dag_edges.csv', 'Super-DAG edge status=LATENT_MECHANISM');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('sd_edge_status_OBSERVED', 4, 'output/clean/mechanism_super_dag_edges.csv', 'Super-DAG edge status=OBSERVED');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('sd_edge_status_UNRESOLVED', 9, 'output/clean/mechanism_super_dag_edges.csv', 'Super-DAG edge status=UNRESOLVED');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('sd_node_status_CONTEXT', 24, 'output/clean/mechanism_super_dag_nodes.csv', 'Super-DAG node status=CONTEXT');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('sd_node_status_LATENT_MECHANISM', 55, 'output/clean/mechanism_super_dag_nodes.csv', 'Super-DAG node status=LATENT_MECHANISM');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('sd_node_status_OBSERVED', 37, 'output/clean/mechanism_super_dag_nodes.csv', 'Super-DAG node status=OBSERVED');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('sd_node_status_UNRESOLVED', 6, 'output/clean/mechanism_super_dag_nodes.csv', 'Super-DAG node status=UNRESOLVED');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('self_loop_count', 0, 'output/clean/observed_edges.csv', 'self-loop edge 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('source_count', 8, 'gusun_clean_restart_csv_pack/04_source_records.csv', '사료 기사 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('unsupported_derived_edge_count', 0, 'output/clean/observed_edges.csv', '근거(supporting) 없는 DERIVED edge 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('world_bridge_total', 44, 'output/clean/narrative_worlds.csv', 'world bridge 합계');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('world_competing_count', 5, 'output/clean/narrative_worlds.csv', '경쟁 설명 world 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('world_count', 6, 'output/clean/narrative_worlds.csv', 'world 수');
INSERT INTO expected_count (metric_id, expected_value, python_source, description)
VALUES ('world_rejected_count', 1, 'output/clean/narrative_worlds.csv', '배제된 world 수');
COMMIT;

-- =============================================================================
-- 2부. Oracle 실제값 (canonical 표에서 독립 계산)
-- =============================================================================
CREATE OR REPLACE VIEW v_oracle_actual_count AS
SELECT 'canonical_node_count' AS metric_id, COUNT(*) AS actual_value FROM dag_node
UNION ALL SELECT 'canonical_edge_count',   COUNT(*) FROM dag_edge
UNION ALL SELECT 'freeze_n_nodes',         MAX(n_nodes) FROM dag_freeze
UNION ALL SELECT 'freeze_n_edges',         MAX(n_edges) FROM dag_freeze
UNION ALL SELECT 'episode_count',          COUNT(*) FROM dag_node WHERE layer <> 'ENVIRONMENT'
UNION ALL SELECT 'env_context_node_count', COUNT(*) FROM dag_node WHERE layer = 'ENVIRONMENT'
UNION ALL SELECT 'node_status_' || node_status, COUNT(*) FROM dag_node GROUP BY node_status
UNION ALL SELECT 'edge_status_' || status, COUNT(*) FROM dag_edge GROUP BY status
UNION ALL SELECT 'sd_node_status_' || sd_status, COUNT(*) FROM sd_node GROUP BY sd_status
UNION ALL SELECT 'sd_edge_status_' || sd_status, COUNT(*) FROM sd_edge GROUP BY sd_status
UNION ALL SELECT 'source_count',            COUNT(*) FROM source_record
UNION ALL SELECT 'confirmed_fact_count',    COUNT(*) FROM confirmed_fact
UNION ALL SELECT 'audit_proposition_count', COUNT(*) FROM audit_proposition
UNION ALL SELECT 'world_count',             COUNT(*) FROM narrative_world
UNION ALL SELECT 'world_competing_count',   COUNT(*) FROM narrative_world WHERE status = 'COMPETING_EXPLANATION'
UNION ALL SELECT 'world_rejected_count',    COUNT(*) FROM narrative_world WHERE status = 'REJECTED'
UNION ALL SELECT 'world_bridge_total',      COUNT(*) FROM world_candidate
UNION ALL SELECT 'candidate_count',         COUNT(*) FROM latent_candidate
UNION ALL SELECT 'candidate_status_LATENT', COUNT(*) FROM latent_candidate WHERE status = 'LATENT'
UNION ALL SELECT 'candidate_overall_HIGH',  COUNT(*) FROM latent_candidate WHERE overall = 'HIGH'
UNION ALL SELECT 'gap_count',               COUNT(*) FROM gap
UNION ALL SELECT 'mechanism_count',         COUNT(*) FROM mechanism
UNION ALL SELECT 'identity_unresolved_count', COUNT(*) FROM identity_register WHERE status = 'UNRESOLVED'
UNION ALL SELECT 'identity_resolved_count',   COUNT(*) FROM identity_register WHERE status = 'RESOLVED'
UNION ALL SELECT 'gap_open_unresolved_count', COUNT(*) FROM gap WHERE gap_status = 'OPEN_UNRESOLVED'
UNION ALL SELECT 'edge_uncertainty_count',    COUNT(uncertainty_status) FROM dag_edge
UNION ALL SELECT 'duplicate_edge_count',      COUNT(*)
            FROM (SELECT src, dst, edge_type FROM dag_edge GROUP BY src, dst, edge_type HAVING COUNT(*) > 1)
UNION ALL SELECT 'self_loop_count',           COUNT(*) FROM dag_edge WHERE src = dst
UNION ALL SELECT 'cycle_count',               COUNT(*)
            FROM (SELECT 1 FROM dag_edge WHERE CONNECT_BY_ISCYCLE = 1 CONNECT BY NOCYCLE PRIOR dst = src)
UNION ALL SELECT 'unsupported_derived_edge_count', COUNT(*)
            FROM dag_edge e
           WHERE e.status = 'DERIVED'
             AND NOT EXISTS (SELECT 1 FROM edge_source_basis b WHERE b.edge_id = e.edge_id)
UNION ALL SELECT 'causes_edge_count',         COUNT(*) FROM dag_edge WHERE edge_type = 'CAUSES'
UNION ALL SELECT 'direct_causal_death_edge_count', COUNT(*)
            FROM dag_edge e
            JOIN rule_set_member s ON s.rule_set = 'FORBIDDEN_DIRECT_SRC' AND s.member_id = e.src
            JOIN rule_set_member d ON d.rule_set = 'FORBIDDEN_DIRECT_DST' AND d.member_id = e.dst
UNION ALL SELECT 'py_' || LOWER(audit_name) || '_' || LOWER(severity), COUNT(*)
            FROM v_sql_audit_all GROUP BY audit_name, severity;

-- 비교 — FULL OUTER JOIN: 기대값만 있는 지표(SQL이 0건이라 행이 없는 py_*_error 등)도 남긴다
SELECT COALESCE(x.metric_id, a.metric_id)              AS metric_id,
       x.expected_value,
       NVL(a.actual_value, 0)                           AS oracle_value,
       CASE WHEN COALESCE(x.metric_id, a.metric_id) LIKE 'py\_audit5\_%' ESCAPE '\' THEN 'NOT PORTED'
            WHEN x.metric_id IS NULL                                            THEN 'ORACLE_ONLY'
            WHEN x.expected_value = NVL(a.actual_value, 0)                      THEN 'MATCH'
            ELSE 'DIFF' END                             AS comparison,
       x.python_source
  FROM expected_count x
  FULL OUTER JOIN v_oracle_actual_count a ON a.metric_id = x.metric_id
 ORDER BY CASE WHEN COALESCE(x.metric_id, a.metric_id) LIKE 'py\_%' ESCAPE '\' THEN 2 ELSE 1 END,
          1;

-- 요약 — 기대: DIFF 0
SELECT comparison, COUNT(*) AS n_metrics
  FROM (SELECT CASE WHEN COALESCE(x.metric_id, a.metric_id) LIKE 'py\_audit5\_%' ESCAPE '\' THEN 'NOT PORTED'
                    WHEN x.metric_id IS NULL                                            THEN 'ORACLE_ONLY'
                    WHEN x.expected_value = NVL(a.actual_value, 0)                      THEN 'MATCH'
                    ELSE 'DIFF' END AS comparison
          FROM expected_count x
          FULL OUTER JOIN v_oracle_actual_count a ON a.metric_id = x.metric_id)
 GROUP BY comparison
 ORDER BY comparison;
