-- =============================================================================
-- joins.sql — INNER / OUTER / SELF / NON-EQUI / CROSS / USING / Oracle (+) 조인
-- =============================================================================

-- 1. INNER JOIN: edge ↔ 근거(source basis) ↔ 확정 사실 — "이 edge는 어떤 사실에 기대는가"
SELECT e.edge_id, e.edge_type, esb.support_id, cf.confirmation_level, cf.subject
  FROM dag_edge e
  JOIN edge_source_basis esb ON esb.edge_id = e.edge_id
  JOIN confirmed_fact cf     ON cf.fact_id = esb.fact_id          -- 가상 컬럼 fact_id(CF…일 때만 값)
 ORDER BY e.edge_id, esb.support_seq;

-- 2. 같은 질의를 Oracle 전통 문법(WHERE 조인)으로
SELECT e.edge_id, e.edge_type, esb.support_id, cf.confirmation_level
  FROM dag_edge e, edge_source_basis esb, confirmed_fact cf
 WHERE esb.edge_id = e.edge_id
   AND cf.fact_id = esb.fact_id
 ORDER BY e.edge_id, esb.support_seq;

-- 3. LEFT OUTER JOIN: 모든 node와 (있으면) 연결된 제도·환경 피쳐 링크 수
SELECT n.node_id, n.title, COUNT(l.link_id) AS n_feature_links
  FROM dag_node n
  LEFT OUTER JOIN node_feature_link l ON l.target_node_id = n.node_id
 GROUP BY n.node_id, n.title
 ORDER BY n_feature_links DESC, n.node_id;

-- 3-1. 같은 외부 조인을 Oracle (+) 표기로: (+)는 '모자라는 쪽'(NULL이 채워질 쪽)에 붙인다
SELECT n.node_id, COUNT(l.link_id) AS n_feature_links
  FROM dag_node n, node_feature_link l
 WHERE l.target_node_id (+) = n.node_id
 GROUP BY n.node_id
 ORDER BY n.node_id;

-- 3-2. 외부 조인 함정: ON 조건과 WHERE 조건의 차이
--   (a) ON에 조건 → 모든 node가 남고, 제도(INSTITUTIONAL) 링크만 센다
SELECT n.node_id, COUNT(l.link_id) AS n_inst_links
  FROM dag_node n
  LEFT JOIN node_feature_link l
         ON l.target_node_id = n.node_id
        AND l.feature_layer = 'INSTITUTIONAL'
 GROUP BY n.node_id
 ORDER BY n.node_id;
--   (b) WHERE에 조건 → NULL 행(링크 없는 node)이 걸러져 사실상 INNER JOIN이 된다
SELECT n.node_id, COUNT(l.link_id) AS n_inst_links
  FROM dag_node n
  LEFT JOIN node_feature_link l ON l.target_node_id = n.node_id
 WHERE l.feature_layer = 'INSTITUTIONAL'
 GROUP BY n.node_id
 ORDER BY n.node_id;

-- 4. SELF JOIN (같은 표 두 번): edge의 출발·도착 node 이름을 함께 — dag_node를 s, d 두 별칭으로
SELECT e.edge_id, s.title AS src_title, e.edge_type, d.title AS dst_title
  FROM dag_edge e
  JOIN dag_node s ON s.node_id = e.src
  JOIN dag_node d ON d.node_id = e.dst
 WHERE e.edge_type = 'REVIEW_OF'
 ORDER BY e.edge_id;

-- 4-1. SELF JOIN으로 2단계 경로: A → B → C (판단을 검토한 판단을 다시 검토)
SELECT e1.src AS a, e1.dst AS b, e2.dst AS c, e1.edge_type || ' / ' || e2.edge_type AS types
  FROM dag_edge e1
  JOIN dag_edge e2 ON e2.src = e1.dst
 WHERE e1.edge_type IN ('REVIEW_OF', 'REVISES')
   AND e2.edge_type IN ('REVIEW_OF', 'REVISES')
 ORDER BY a, b, c;

-- 5. NON-EQUI JOIN: 환경 context 시점(t_min)이 판단 node 시점 이전인 모든 조합 (부등호 조인)
--    판단 시점에 '이미 있었던' 환경 기록만 맥락이 될 수 있다.
SELECT j.node_id AS judgment, j.t_min AS judgment_md, env.node_id AS env_node, env.t_min AS env_md
  FROM dag_node j
  JOIN dag_node env
    ON env.layer = 'ENVIRONMENT'
   AND env.t_min <= j.t_min
 WHERE j.layer = 'ROYAL_JUDGMENT'
 ORDER BY j.node_id, env.node_id;

-- 6. CROSS JOIN (카티션 곱): world 6 × gap 13 = 78행 격자 — 어느 칸이 비었는지 보려면 LEFT JOIN을 덧붙인다
SELECT w.world_id, g.gap_id, wc.candidate_id
  FROM narrative_world w
 CROSS JOIN gap g
  LEFT JOIN world_candidate wc
         ON wc.world_id = w.world_id
        AND wc.gap_id = g.gap_id
 ORDER BY w.world_id, g.gap_id;

-- 7. USING: 조인 컬럼 이름이 같을 때. USING 컬럼에는 테이블 별칭을 붙이지 않는다(붙이면 ORA-25154)
SELECT candidate_id, c.overall, cm.mechanism_id, cm.mapping_role
  FROM latent_candidate c
  JOIN candidate_mechanism cm USING (candidate_id)
 ORDER BY candidate_id, cm.mapping_role;

-- 8. FULL OUTER JOIN: Python audit finding과 SQL audit finding을 (audit, check) 단위로 맞대기
--    (05_audits/audit_summary.sql 실행 뒤)
SELECT COALESCE(p.audit_name, s.audit_name) AS audit_name,
       COALESCE(p.check_name, s.check_name) AS check_name,
       p.n AS python_n,
       s.n AS sql_n
  FROM (SELECT audit_name, check_name, COUNT(*) AS n FROM py_audit_finding GROUP BY audit_name, check_name) p
  FULL OUTER JOIN
       (SELECT audit_name, check_name, COUNT(*) AS n FROM v_sql_audit_all GROUP BY audit_name, check_name) s
    ON s.audit_name = p.audit_name
   AND s.check_name = p.check_name
 ORDER BY 1, 2;

-- 9. 다대다(M:N) 해소 표를 통한 조인: world ↔ 후보 ↔ 메커니즘
SELECT w.world_id, wc.candidate_id, cm.mechanism_id, m.mechanism_name
  FROM narrative_world w
  JOIN world_candidate wc     ON wc.world_id = w.world_id
  JOIN candidate_mechanism cm ON cm.candidate_id = wc.candidate_id AND cm.mapping_role = 'PRIMARY'
  JOIN mechanism m            ON m.mechanism_id = cm.mechanism_id
 WHERE w.world_id = 'W2'
 ORDER BY wc.bridge_seq;

-- 10. 복합 FK 조인: world_candidate (candidate_id, gap_id) = latent_candidate (candidate_id, gap_id)
SELECT wc.world_id, wc.gap_id, lc.candidate_id, lc.label
  FROM world_candidate wc
  JOIN latent_candidate lc
    ON lc.candidate_id = wc.candidate_id
   AND lc.gap_id = wc.gap_id
 WHERE wc.world_id = 'W5'
 ORDER BY wc.bridge_seq;
