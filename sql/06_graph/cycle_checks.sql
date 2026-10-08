-- =============================================================================
-- cycle_checks.sql — DAG 무결성: cycle · self-loop · 2-cycle · 중복 edge
-- -----------------------------------------------------------------------------
-- 각 질의는 문제 행만 돌려준다. 정상: 0행.
-- =============================================================================

-- Q1. observed DAG cycle 검출 — NOCYCLE + CONNECT_BY_ISCYCLE
--     CONNECT_BY_ISCYCLE = 1 : 이 행의 자식 중 하나가 이미 경로 위(조상)에 있다 = cycle을 닫는 지점
--     NOCYCLE이 없으면 cycle이 있을 때 ORA-01436(CONNECT BY loop in user data)으로 실패한다.
SELECT CONNECT_BY_ROOT e.src                  AS start_node,
       e.src || SYS_CONNECT_BY_PATH(e.dst, '>') AS path_to_cycle,
       LEVEL                                  AS depth
  FROM dag_edge e
 WHERE CONNECT_BY_ISCYCLE = 1
CONNECT BY NOCYCLE PRIOR e.dst = e.src;

-- Q2. Super-DAG cycle 검출 (122 node / 205 edge)
SELECT CONNECT_BY_ROOT e.src                  AS start_node,
       e.src || SYS_CONNECT_BY_PATH(e.dst, '>') AS path_to_cycle
  FROM sd_edge e
 WHERE CONNECT_BY_ISCYCLE = 1
CONNECT BY NOCYCLE PRIOR e.dst = e.src;

-- Q3. (연습) 일부러 cycle을 하나 넣은 가상 graph에서 검출이 되는지 확인
--     WITH 절에 '6월 16일 유임(EP37) → 관계 변화(EP01)' 가짜 edge를 더한다. 실제 데이터는 바뀌지 않는다.
--     기대: 1행 이상(가짜 edge가 닫는 cycle 경로)
WITH g AS (
    SELECT src, dst FROM dag_edge
    UNION ALL
    SELECT 'EP37', 'EP01' FROM dual          -- 가짜 edge (cycle을 만든다)
)
SELECT CONNECT_BY_ROOT g.src                 AS start_node,
       g.src || SYS_CONNECT_BY_PATH(g.dst, '>') AS path_to_cycle
  FROM g
 WHERE CONNECT_BY_ISCYCLE = 1
 START WITH g.src = 'EP37'
CONNECT BY NOCYCLE PRIOR g.dst = g.src;

-- Q4. self-loop (src = dst) — CHECK ck_dag_edge_no_self_loop가 막지만 질의로도 확인
SELECT edge_id, src, dst, edge_type FROM dag_edge WHERE src = dst
UNION ALL
SELECT edge_id, src, dst, edge_type FROM sd_edge WHERE src = dst;

-- Q5. 2-cycle (A→B와 B→A가 동시에) — 자기 조인. CONTRADICTS는 방향이 '제시 순서'라도 쌍으로 있으면 보고
SELECT e1.edge_id AS edge_forward, e2.edge_id AS edge_backward, e1.src, e1.dst
  FROM dag_edge e1
  JOIN dag_edge e2
    ON e2.src = e1.dst
   AND e2.dst = e1.src
 WHERE e1.edge_id < e2.edge_id;

-- Q6. 중복 edge — 같은 (src, dst, edge_type)이 2번 이상 (Python audit에는 없는 SQL 추가 점검)
SELECT src, dst, edge_type, COUNT(*) AS n, LISTAGG(edge_id, ',') WITHIN GROUP (ORDER BY edge_id) AS edge_ids
  FROM dag_edge
 GROUP BY src, dst, edge_type
HAVING COUNT(*) > 1;

-- Q7. 같은 두 node 사이에 type이 다른 edge가 여러 개인 경우 (중복은 아니지만 해석 주의 — INFO)
SELECT src, dst, COUNT(*) AS n_types, LISTAGG(edge_type, ',') WITHIN GROUP (ORDER BY edge_type) AS edge_types
  FROM dag_edge
 GROUP BY src, dst
HAVING COUNT(*) > 1;

-- Q8. 위상 순서(topological depth): 들어오는 edge가 없는 node(SOURCE)에서의 최장 깊이
--     DAG에서만 의미가 있다. Q1이 0행일 때 실행한다.
SELECT d.node_id, n.title, d.max_depth
  FROM (SELECT e.dst AS node_id, MAX(LEVEL) AS max_depth
          FROM dag_edge e
         START WITH e.src IN (SELECT node_id FROM v_node_degree WHERE position = 'SOURCE')
       CONNECT BY NOCYCLE PRIOR e.dst = e.src
         GROUP BY e.dst
        UNION ALL
        SELECT node_id, 0 FROM v_node_degree WHERE position = 'SOURCE') d
  JOIN dag_node n ON n.node_id = d.node_id
 ORDER BY d.max_depth, d.node_id;
