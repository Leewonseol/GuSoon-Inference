-- =============================================================================
-- ancestor_descendant.sql — 조상(거슬러 올라가기)·후손·전이 폐쇄(transitive closure)
-- -----------------------------------------------------------------------------
-- 거꾸로 올라가려면 PRIOR의 위치를 바꾼다:
--   CONNECT BY PRIOR e.src = e.dst   -- 부모 행의 src = 자식 행의 dst (뒤로 진행)
-- =============================================================================

-- Q1. 정조 최종 도난 판단(EP25)의 모든 조상 — 어떤 관측이 이 판단에 이어지는가
SELECT LEVEL                                       AS hops_back,
       LPAD(' ', 2 * (LEVEL - 1)) || e.src         AS ancestor_indented,
       e.edge_type,
       n.title                                     AS ancestor_title,
       'EP25' || SYS_CONNECT_BY_PATH(e.src, ' < ') AS back_path
  FROM dag_edge e
  JOIN dag_node n ON n.node_id = e.src
 START WITH e.dst = 'EP25'
CONNECT BY NOCYCLE PRIOR e.src = e.dst
 ORDER SIBLINGS BY e.src;
-- 참고: 계층형 질의에 JOIN을 쓰면 Oracle은 JOIN을 먼저 하고 그 결과에 계층을 만든다.

-- Q2. 정조 구순 책임 판단(EP29)의 조상 node 목록(중복 제거, 최단 거리)
--     책임 판단은 RESPONSIBILITY_LINK로만 들어온다 — 어떤 관측이 책임 판단의 근거로 연결되었는가
SELECT a.ancestor_id, n.layer, n.title, a.min_hops
  FROM (SELECT e.src AS ancestor_id, MIN(LEVEL) AS min_hops
          FROM dag_edge e
         START WITH e.dst = 'EP29'
       CONNECT BY NOCYCLE PRIOR e.src = e.dst
         GROUP BY e.src) a
  JOIN dag_node n ON n.node_id = a.ancestor_id
 ORDER BY a.min_hops, a.ancestor_id;

-- Q3. 전이 폐쇄: 모든 (조상, 후손) 쌍 — START WITH 없이 모든 행을 뿌리로 쓴다
--     CONNECT_BY_ROOT e.src = 그 경로가 시작된 조상
CREATE OR REPLACE VIEW v_dag_reachability AS
SELECT DISTINCT
       CONNECT_BY_ROOT e.src AS ancestor_id,
       e.dst                 AS descendant_id
  FROM dag_edge e
CONNECT BY NOCYCLE PRIOR e.dst = e.src;

-- Q4. node별 후손 수·조상 수 (전이 폐쇄 view 집계) — 영향 범위가 넓은 관측 순서
SELECT n.node_id,
       n.title,
       (SELECT COUNT(*) FROM v_dag_reachability r WHERE r.ancestor_id = n.node_id)   AS n_descendants,
       (SELECT COUNT(*) FROM v_dag_reachability r WHERE r.descendant_id = n.node_id) AS n_ancestors
  FROM dag_node n
 ORDER BY n_descendants DESC, n.node_id;

-- Q5. 두 판단의 공통 조상: 도난 최종 판단(EP25)과 사인 판단(EP27) — INTERSECT
SELECT ancestor_id FROM v_dag_reachability WHERE descendant_id = 'EP25'
INTERSECT
SELECT ancestor_id FROM v_dag_reachability WHERE descendant_id = 'EP27'
ORDER BY 1;

-- Q6. 한쪽 판단에만 이어지는 조상 — MINUS
SELECT ancestor_id AS only_theft_judgment_ancestor FROM v_dag_reachability WHERE descendant_id = 'EP25'
MINUS
SELECT ancestor_id FROM v_dag_reachability WHERE descendant_id = 'EP27'
ORDER BY 1;

-- Q7. '구순 쪽 node(EP01)가 사망·사인 node(EP26·EP27)의 조상인가'와 '직접 edge가 있는가'는 다른 질문이다
--     경로는 있을 수 있지만(홍대협 신문·복명 EP23을 거침) 직접 edge는 없어야 한다(Audit 2 FORBIDDEN_DIRECT).
SELECT t.target_id,
       CASE WHEN EXISTS (SELECT 1 FROM v_dag_reachability r
                          WHERE r.ancestor_id = 'EP01' AND r.descendant_id = t.target_id)
            THEN 'Y' ELSE 'N' END AS reachable_from_ep01,
       CASE WHEN EXISTS (SELECT 1 FROM dag_edge e
                          WHERE e.src = 'EP01' AND e.dst = t.target_id)
            THEN 'Y' ELSE 'N' END AS direct_edge_from_ep01
  FROM (SELECT 'EP13' AS target_id FROM dual
        UNION ALL SELECT 'EP26' FROM dual
        UNION ALL SELECT 'EP27' FROM dual) t;
