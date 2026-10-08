-- =============================================================================
-- 03_load_validation.sql — 적재 검증 (04_transform_to_canonical.sql 실행 뒤)
-- -----------------------------------------------------------------------------
-- 각 질의는 '문제 행'만 돌려준다. 정상이면 0행(또는 diff = 0)이다.
-- =============================================================================

-- 1. STG ↔ canonical 행 수 비교 (1:1로 옮기는 표) ------------------------------
--    정상: diff 컬럼이 모두 0
SELECT 'confirmed_fact' AS table_name,
       (SELECT COUNT(*) FROM stg_confirmed_facts) AS stg_rows,
       (SELECT COUNT(*) FROM confirmed_fact)      AS canonical_rows FROM dual
UNION ALL SELECT 'source_record',          (SELECT COUNT(*) FROM stg_source_records),         (SELECT COUNT(*) FROM source_record)          FROM dual
UNION ALL SELECT 'audit_proposition',      (SELECT COUNT(*) FROM stg_audit_propositions),     (SELECT COUNT(*) FROM audit_proposition)      FROM dual
UNION ALL SELECT 'institutional_feature',  (SELECT COUNT(*) FROM stg_institutional_features), (SELECT COUNT(*) FROM institutional_feature)  FROM dual
UNION ALL SELECT 'environment_context',    (SELECT COUNT(*) FROM stg_environment_1793),       (SELECT COUNT(*) FROM environment_context)    FROM dual
UNION ALL SELECT 'dag_node',               (SELECT COUNT(*) FROM stg_episode_nodes),          (SELECT COUNT(*) FROM dag_node)               FROM dual
UNION ALL SELECT 'dag_edge',               (SELECT COUNT(*) FROM stg_observed_edges),         (SELECT COUNT(*) FROM dag_edge)               FROM dual
UNION ALL SELECT 'episode_member',         (SELECT COUNT(*) FROM stg_episode_members),        (SELECT COUNT(*) FROM episode_member)         FROM dual
UNION ALL SELECT 'node_feature_link',      (SELECT COUNT(*) FROM stg_node_feature_links),     (SELECT COUNT(*) FROM node_feature_link)      FROM dual
UNION ALL SELECT 'identity_register',      (SELECT COUNT(*) FROM stg_identity_register),      (SELECT COUNT(*) FROM identity_register)      FROM dual
UNION ALL SELECT 'gap',                    (SELECT COUNT(*) FROM stg_gaps),                   (SELECT COUNT(*) FROM gap)                    FROM dual
UNION ALL SELECT 'latent_candidate',       (SELECT COUNT(*) FROM stg_latent_candidates),      (SELECT COUNT(*) FROM latent_candidate)       FROM dual
UNION ALL SELECT 'latent_element',         (SELECT COUNT(*) FROM stg_latent_elements),        (SELECT COUNT(*) FROM latent_element)         FROM dual
UNION ALL SELECT 'narrative_world',        (SELECT COUNT(*) FROM stg_narrative_worlds),       (SELECT COUNT(*) FROM narrative_world)        FROM dual
UNION ALL SELECT 'mechanism',              (SELECT COUNT(*) FROM stg_mechanism_definitions),  (SELECT COUNT(*) FROM mechanism)              FROM dual
UNION ALL SELECT 'mechanism_interaction',  (SELECT COUNT(*) FROM stg_mech_interactions),      (SELECT COUNT(*) FROM mechanism_interaction)  FROM dual
UNION ALL SELECT 'mechanism_intervention', (SELECT COUNT(*) FROM stg_mech_interventions),     (SELECT COUNT(*) FROM mechanism_intervention) FROM dual
UNION ALL SELECT 'structural_rule',        (SELECT COUNT(*) FROM stg_structural_rules),       (SELECT COUNT(*) FROM structural_rule)        FROM dual
UNION ALL SELECT 'sd_node',                (SELECT COUNT(*) FROM stg_sd_nodes),               (SELECT COUNT(*) FROM sd_node)                FROM dual
UNION ALL SELECT 'sd_edge',                (SELECT COUNT(*) FROM stg_sd_edges),               (SELECT COUNT(*) FROM sd_edge)                FROM dual
UNION ALL SELECT 'warn_disposition',       (SELECT COUNT(*) FROM stg_warn_dispositions),      (SELECT COUNT(*) FROM warn_disposition)       FROM dual
UNION ALL SELECT 'py_audit_finding',       (SELECT COUNT(*) FROM stg_py_audit_findings),      (SELECT COUNT(*) FROM py_audit_finding)       FROM dual
UNION ALL SELECT 'dag_freeze',             (SELECT COUNT(*) FROM stg_dag_freeze),             (SELECT COUNT(*) FROM dag_freeze)             FROM dual
UNION ALL SELECT 'world_mechanism_config(×7)', (SELECT COUNT(*) * 7 FROM stg_world_mech_configs), (SELECT COUNT(*) FROM world_mechanism_config) FROM dual
ORDER BY 1;

-- 2. '|' 목록 펴기 누락 검사: 원소 수 합계 = 연결 테이블 행 수 ---------------------
--    정상: 0행 (원문 목록 원소 수와 정규화 행 수가 다르면 그 표가 나온다)
WITH chk AS (
    SELECT 'fact_proposition' AS bridge,
           (SELECT SUM(REGEXP_COUNT(source_prop_ids, '[^|]+')) FROM confirmed_fact) AS list_items,
           (SELECT COUNT(*) FROM fact_proposition) AS bridge_rows FROM dual
    UNION ALL SELECT 'identity_fact_ref',
           (SELECT SUM(REGEXP_COUNT(referenced_facts, '[^|]+')) FROM identity_register),
           (SELECT COUNT(*) FROM identity_fact_ref) FROM dual
    UNION ALL SELECT 'edge_basis_type',
           (SELECT SUM(REGEXP_COUNT(basis, '[^|]+')) FROM dag_edge),
           (SELECT COUNT(*) FROM edge_basis_type) FROM dual
    UNION ALL SELECT 'edge_source_basis',
           (SELECT SUM(REGEXP_COUNT(supporting, '[^|]+')) FROM dag_edge),
           (SELECT COUNT(*) FROM edge_source_basis) FROM dual
    UNION ALL SELECT 'edge_identity_condition',
           (SELECT NVL(SUM(REGEXP_COUNT(condition, '[^|]+')), 0) FROM dag_edge),
           (SELECT COUNT(*) FROM edge_identity_condition) FROM dual
    UNION ALL SELECT 'gap_anchor_node',
           (SELECT SUM(REGEXP_COUNT(between_nodes, '[^|]+')) FROM gap),
           (SELECT COUNT(*) FROM gap_anchor_node) FROM dual
    UNION ALL SELECT 'candidate_identity_condition',
           (SELECT NVL(SUM(REGEXP_COUNT(identity_conditions, '[^|]+')), 0) FROM latent_candidate),
           (SELECT COUNT(*) FROM candidate_identity_condition) FROM dual
    UNION ALL SELECT 'candidate_evidence',
           (SELECT NVL(SUM(REGEXP_COUNT(bridge_evidence, '[^|]+')), 0)
                 + NVL(SUM(REGEXP_COUNT(audit_attestation, '[^|]+')), 0) FROM latent_candidate),
           (SELECT COUNT(*) FROM candidate_evidence) FROM dual
    UNION ALL SELECT 'candidate_bridge_basis',
           (SELECT SUM(REGEXP_COUNT(bridge_basis, '[^|]+')) FROM latent_candidate),
           (SELECT COUNT(*) FROM candidate_bridge_basis) FROM dual
    UNION ALL SELECT 'world_candidate',
           (SELECT SUM(REGEXP_COUNT(latent_bridges, '[^|]+')) FROM narrative_world),
           (SELECT COUNT(*) FROM world_candidate) FROM dual
    UNION ALL SELECT 'world_unresolved_gap',
           (SELECT SUM(REGEXP_COUNT(unresolved_gaps, '[^|]+')) FROM narrative_world),
           (SELECT COUNT(*) FROM world_unresolved_gap) FROM dual
    UNION ALL SELECT 'world_identity',
           (SELECT NVL(SUM(REGEXP_COUNT(identity_conditions, '[^|]+')), 0)
                 + NVL(SUM(REGEXP_COUNT(resolved_identities, '[^|]+')), 0) FROM narrative_world),
           (SELECT COUNT(*) FROM world_identity) FROM dual
    UNION ALL SELECT 'intervention_candidate',
           (SELECT NVL(SUM(REGEXP_COUNT(removed, '[^|]+')), 0)
                 + NVL(SUM(REGEXP_COUNT(remaining, '[^|]+')), 0) FROM mechanism_intervention),
           (SELECT COUNT(*) FROM intervention_candidate) FROM dual
)
SELECT bridge, list_items, bridge_rows
  FROM chk
 WHERE list_items <> bridge_rows;

-- 3. episode_member 교차 검증 -----------------------------------------------------
--    DuckDB episode_members(Python이 직접 쓴 표)와 episode_nodes.member_fact_ids를 편 결과가 같아야 한다.
--    정상: 0행. MINUS를 양쪽으로 해서 '한쪽에만 있는 행'을 찾는다(대칭 차집합).
WITH from_csv AS (
    SELECT n.node_id AS episode_id, REGEXP_SUBSTR(n.member_fact_ids, '[^|]+', 1, seq.n) AS fact_id
      FROM dag_node n
      JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
        ON seq.n <= REGEXP_COUNT(n.member_fact_ids, '[^|]+')
)
SELECT 'only_in_episode_nodes.csv' AS side, episode_id, fact_id
  FROM (SELECT episode_id, fact_id FROM from_csv
        MINUS
        SELECT episode_id, fact_id FROM episode_member)
UNION ALL
SELECT 'only_in_duckdb_episode_members', episode_id, fact_id
  FROM (SELECT episode_id, fact_id FROM episode_member
        MINUS
        SELECT episode_id, fact_id FROM from_csv);

-- 4. 정규화로 뺀 중복 컬럼(메커니즘 이름)이 mechanism 표와 같은지 -----------------
--    정상: 0행
SELECT s.mechanism_a_id, s.mechanism_a_name, ma.mechanism_name AS expected_a,
       s.mechanism_b_id, s.mechanism_b_name, mb.mechanism_name AS expected_b
  FROM stg_mech_interactions s
  JOIN mechanism ma ON ma.mechanism_id = s.mechanism_a_id
  JOIN mechanism mb ON mb.mechanism_id = s.mechanism_b_id
 WHERE s.mechanism_a_name <> ma.mechanism_name
    OR s.mechanism_b_name <> mb.mechanism_name;

-- 5. world_mechanism_config의 latent_bridges(가로 표에도 있음)가 narrative_world와 같은지
--    정상: 0행
SELECT c.world_id, c.latent_bridges AS config_bridges, w.latent_bridges AS world_bridges
  FROM stg_world_mech_configs c
  JOIN narrative_world w ON w.world_id = c.world_id
 WHERE c.latent_bridges <> w.latent_bridges
    OR c.role_type <> w.status;

-- 6. 동결 기록과 실제 행 수 ---------------------------------------------------------
--    정상: 0행
SELECT f.freeze_name, f.n_nodes, f.n_edges, f.n_episode_nodes, f.n_env_nodes,
       (SELECT COUNT(*) FROM dag_node)                               AS actual_nodes,
       (SELECT COUNT(*) FROM dag_edge)                               AS actual_edges,
       (SELECT COUNT(*) FROM dag_node WHERE layer <> 'ENVIRONMENT')  AS actual_episode_nodes,
       (SELECT COUNT(*) FROM dag_node WHERE layer = 'ENVIRONMENT')   AS actual_env_nodes
  FROM dag_freeze f
 WHERE f.n_nodes         <> (SELECT COUNT(*) FROM dag_node)
    OR f.n_edges         <> (SELECT COUNT(*) FROM dag_edge)
    OR f.n_episode_nodes <> (SELECT COUNT(*) FROM dag_node WHERE layer <> 'ENVIRONMENT')
    OR f.n_env_nodes     <> (SELECT COUNT(*) FROM dag_node WHERE layer = 'ENVIRONMENT');

-- 7. 비활성화된 제약조건이 없는지 (적재 중 DISABLE 했다가 잊는 실수 방지) ------------
--    정상: 0행
SELECT table_name, constraint_name, constraint_type, status
  FROM user_constraints
 WHERE status <> 'ENABLED'
   AND table_name NOT LIKE 'STG\_%' ESCAPE '\'
   AND table_name NOT LIKE 'X\_%' ESCAPE '\';

-- 8. 적재 기록 확인 — DATE와 TIMESTAMP 표시 차이 --------------------------------------
SELECT load_step, table_name, row_count,
       TO_CHAR(load_day,  'YYYY-MM-DD HH24:MI:SS')    AS load_day_date,
       TO_CHAR(loaded_at, 'YYYY-MM-DD HH24:MI:SS.FF6') AS loaded_at_timestamp
  FROM load_log
 ORDER BY loaded_at, table_name;
