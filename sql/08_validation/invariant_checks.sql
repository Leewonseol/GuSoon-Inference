-- =============================================================================
-- invariant_checks.sql — DAG 무결성 불변식 한눈에 보기
-- -----------------------------------------------------------------------------
-- 각 불변식의 '위반 행 수'를 센다. 정상: 모든 violations = 0 → verdict = 'OK'
-- 규칙의 출처는 Python audit(audits.py)이고, 'SQL 추가'라고 적은 것은 Python에 없는 SQL 쪽 추가 점검이다.
-- 선행: 01_schema, 02_load, 03_views
-- =============================================================================

CREATE OR REPLACE VIEW v_invariant_check AS
SELECT 'INV01' AS invariant_id, 'orphan node (edge가 하나도 없는 node)' AS description, 'Audit 2 missing_relation(WARN)' AS rule_source,
       (SELECT COUNT(*) FROM v_node_degree WHERE total_degree = 0) AS violations
  FROM dual
UNION ALL
SELECT 'INV02', 'orphan edge (끝점 node가 없는 edge)', 'Audit 2 unsupported_edge',
       (SELECT COUNT(*) FROM dag_edge e
         WHERE NOT EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = e.src)
            OR NOT EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = e.dst))
  FROM dual
UNION ALL
SELECT 'INV03', 'missing source basis (근거 fact·환경 행이 없는 edge)', 'Audit 2 unsupported_edge',
       (SELECT COUNT(*) FROM dag_edge e
         WHERE NOT EXISTS (SELECT 1 FROM edge_source_basis b WHERE b.edge_id = e.edge_id))
  FROM dual
UNION ALL
SELECT 'INV04', 'self-loop (src = dst)', 'Audit 2 acyclicity / CHECK',
       (SELECT COUNT(*) FROM dag_edge WHERE src = dst)
  FROM dual
UNION ALL
SELECT 'INV05', 'duplicate edge (같은 src·dst·type 2개 이상)', 'SQL 추가',
       (SELECT COUNT(*) FROM (SELECT src, dst, edge_type FROM dag_edge
                               GROUP BY src, dst, edge_type HAVING COUNT(*) > 1))
  FROM dual
UNION ALL
SELECT 'INV06', 'reversed temporal edge (src.t_min > dst.t_max, CONTRADICTS 제외)', 'Audit 2 temporal_inversion',
       (SELECT COUNT(*) FROM v_edge_detail
         WHERE edge_type <> 'CONTRADICTS_AT_CLAIM_LEVEL' AND src_t_min > dst_t_max)
  FROM dual
UNION ALL
SELECT 'INV07', 'cycle (CONNECT_BY_ISCYCLE = 1인 행)', 'Audit 2 acyclicity',
       (SELECT COUNT(*) FROM (SELECT 1 FROM dag_edge WHERE CONNECT_BY_ISCYCLE = 1 CONNECT BY NOCYCLE PRIOR dst = src))
  FROM dual
UNION ALL
SELECT 'INV08', 'unresolved identity forcing (민감 node 쌍 edge에 미확정 ID condition 누락)', 'Audit 2 identity_forcing',
       (SELECT COUNT(*) FROM dag_edge e
          JOIN rule_identity_sensitive_pair rp
            ON (rp.node_a = e.src AND rp.node_b = e.dst) OR (rp.node_a = e.dst AND rp.node_b = e.src)
          JOIN identity_register ir ON ir.identity_id = rp.identity_id AND ir.status = 'UNRESOLVED'
         WHERE NOT EXISTS (SELECT 1 FROM edge_identity_condition c
                            WHERE c.edge_id = e.edge_id AND c.identity_id = rp.identity_id))
  FROM dual
UNION ALL
SELECT 'INV09', 'stale identity condition (사용자 확정 ID가 edge condition에 남음)', 'Audit 2 stale_identity_condition',
       (SELECT COUNT(*) FROM edge_identity_condition c
          JOIN identity_register ir ON ir.identity_id = c.identity_id
         WHERE ir.status = 'RESOLVED')
  FROM dual
UNION ALL
SELECT 'INV10', 'LATENT → OBSERVED 오분류 (동결 표의 비관측 node·edge, LATENT 아닌 후보)', 'Audit 3 latent_as_observed',
       (SELECT COUNT(*) FROM dag_node WHERE node_status <> 'OBSERVED')
     + (SELECT COUNT(*) FROM dag_edge WHERE status NOT IN ('OBSERVED', 'DERIVED'))
     + (SELECT COUNT(*) FROM latent_candidate WHERE status <> 'LATENT')
     + (SELECT COUNT(*) FROM latent_element WHERE status <> 'LATENT')
  FROM dual
UNION ALL
SELECT 'INV11', 'latent node id가 관측 node id와 충돌', 'Audit 3 latent_as_observed',
       (SELECT COUNT(*) FROM latent_element le
         WHERE le.kind = 'node' AND EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = le.element_id))
  FROM dual
UNION ALL
SELECT 'INV12', 'direct causal death edge (구순 관련 node → 사망·사인 node)', 'Audit 2 FORBIDDEN_DIRECT',
       (SELECT COUNT(*) FROM dag_edge e
          JOIN rule_set_member s ON s.rule_set = 'FORBIDDEN_DIRECT_SRC' AND s.member_id = e.src
          JOIN rule_set_member d ON d.rule_set = 'FORBIDDEN_DIRECT_DST' AND d.member_id = e.dst)
  FROM dual
UNION ALL
SELECT 'INV13', 'CAUSES edge (observed DAG + Super-DAG + latent)', 'Audit 2·3·4 causal_inflation',
       (SELECT COUNT(*) FROM dag_edge WHERE edge_type = 'CAUSES')
     + (SELECT COUNT(*) FROM sd_edge WHERE edge_type = 'CAUSES')
     + (SELECT COUNT(*) FROM latent_element WHERE edge_type = 'CAUSES')
  FROM dual
UNION ALL
SELECT 'INV14', 'environment → individual fact leakage (환경 node가 CONTEXT_SUPPORTS 출발점이 아니거나 판단 아닌 node로)', 'Audit 2 environmental_leakage',
       (SELECT COUNT(*) FROM v_edge_detail d
         WHERE (d.src_layer = 'ENVIRONMENT' OR d.dst_layer = 'ENVIRONMENT')
           AND (   d.edge_type <> 'CONTEXT_SUPPORTS'
                OR d.src_layer <> 'ENVIRONMENT'
                OR d.dst_layer NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'JUDGMENT_LAYER')))
  FROM dual
UNION ALL
SELECT 'INV15', 'environment → personal fact (Super-DAG: 환경이 사건·후보에 직접 연결)', 'Audit 4 environment_to_personal_fact',
       (SELECT COUNT(*) FROM sd_edge e
          JOIN sd_node s ON s.node_id = e.src AND s.node_type = 'ENV_CONTEXT'
          JOIN sd_node d ON d.node_id = e.dst
         WHERE e.origin <> 'FROZEN'
           AND d.node_type IN ('OBSERVED_EVENT', 'CANDIDATE_BRIDGE'))
  FROM dual
UNION ALL
SELECT 'INV16', 'RESPONSIBILITY_LINK가 국왕 판단 아닌 node로', 'Audit 2 causal_inflation',
       (SELECT COUNT(*) FROM v_edge_detail WHERE edge_type = 'RESPONSIBILITY_LINK' AND dst_layer <> 'ROYAL_JUDGMENT')
  FROM dual
UNION ALL
SELECT 'INV17', '필수 관계 누락 (REQUIRED_RELATIONS 17개)', 'Audit 2 missing_relation',
       (SELECT COUNT(*) FROM rule_required_relation r
         WHERE NOT EXISTS (SELECT 1 FROM dag_edge e
                            WHERE e.src = r.src AND e.dst = r.dst AND e.edge_type = r.edge_type))
  FROM dual
UNION ALL
SELECT 'INV18', '동결 집계 불일치 (dag_freeze ↔ 실제 node·edge 수)', 'Audit 3 freeze_violation(집계)',
       (SELECT COUNT(*) FROM dag_freeze f
         WHERE f.n_nodes <> (SELECT COUNT(*) FROM dag_node)
            OR f.n_edges <> (SELECT COUNT(*) FROM dag_edge)
            OR f.latent_count <> 0)
  FROM dual
UNION ALL
SELECT 'INV19', 'frozen edge ↔ Super-DAG FROZEN edge 대칭 차집합', 'Audit 4 frozen_graph_changed',
       (SELECT COUNT(*) FROM ((SELECT edge_id, src, dst, edge_type, status FROM dag_edge
                               MINUS
                               SELECT edge_id, src, dst, edge_type, sd_status FROM sd_edge WHERE origin = 'FROZEN')
                              UNION ALL
                              (SELECT edge_id, src, dst, edge_type, sd_status FROM sd_edge WHERE origin = 'FROZEN'
                               MINUS
                               SELECT edge_id, src, dst, edge_type, status FROM dag_edge)))
  FROM dual
UNION ALL
SELECT 'INV20', 'world 한 gap에 후보 2개 이상 / 상충 후보 쌍 동시 사용', 'Audit 3 world_integrity',
       (SELECT COUNT(*) FROM (SELECT world_id, gap_id FROM world_candidate GROUP BY world_id, gap_id HAVING COUNT(*) > 1))
     + (SELECT COUNT(*) FROM rule_conflict_pair cp
          JOIN world_candidate a ON a.candidate_id = cp.candidate_a
          JOIN world_candidate b ON b.candidate_id = cp.candidate_b AND b.world_id = a.world_id)
  FROM dual;

-- 결과 — 기대: 모든 행 verdict = 'OK'
SELECT invariant_id,
       description,
       rule_source,
       violations,
       CASE WHEN violations = 0 THEN 'OK' ELSE 'VIOLATION' END AS verdict
  FROM v_invariant_check
 ORDER BY invariant_id;
