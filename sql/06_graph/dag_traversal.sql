-- =============================================================================
-- dag_traversal.sql — Oracle 계층형 질의로 observed DAG 따라가기 (후손 방향)
-- -----------------------------------------------------------------------------
-- 계층형 질의 기본형
--   SELECT LEVEL, …
--     FROM dag_edge e
--    START WITH e.src = '출발 node'         -- 1단계(LEVEL 1)가 될 행
--  CONNECT BY NOCYCLE PRIOR e.dst = e.src    -- 부모 행의 dst = 자식 행의 src (앞으로 진행)
-- 표의 한 행 = edge 하나. LEVEL n의 행은 출발 node에서 n번째로 지나는 edge다.
-- DAG는 트리가 아니다: 한 node에 여러 경로로 도달하면 그 node가 여러 번(경로마다) 나온다.
-- NOCYCLE: DAG라 cycle이 없어야 하지만, 데이터가 잘못되어 cycle이 생겨도 질의가 멈추지 않게 둔다.
-- =============================================================================

-- Q1. 3월 4일 김명신 체포(EP11) 이후의 모든 후속 edge — 깊이·경로·잎 여부
--     LEVEL                : 출발점에서 몇 번째 edge인가
--     CONNECT_BY_ROOT      : 이 경로의 출발 행(뿌리)의 값
--     SYS_CONNECT_BY_PATH  : 뿌리부터 현재까지 값을 이어 붙인 경로 문자열
--     CONNECT_BY_ISLEAF    : 더 내려갈 자식이 없으면 1
--     ORDER SIBLINGS BY    : 계층 구조를 유지한 채 같은 부모 아래 형제끼리만 정렬
SELECT LEVEL                                        AS depth,
       CONNECT_BY_ROOT e.src                        AS root_node,
       LPAD(' ', 2 * (LEVEL - 1)) || e.dst          AS node_indented,
       e.edge_type,
       e.status,
       e.src || SYS_CONNECT_BY_PATH(e.dst, ' > ')   AS path,
       CONNECT_BY_ISLEAF                            AS is_leaf
  FROM dag_edge e
 START WITH e.src = 'EP11'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
 ORDER SIBLINGS BY e.dst;

-- Q2. EP11에서 닿는 node 목록(중복 제거)과 최단 깊이
--     같은 node가 여러 경로로 나오므로 GROUP BY + MIN(LEVEL)로 정리한다.
SELECT r.node_id,
       n.title,
       r.min_depth,
       r.n_paths
  FROM (SELECT e.dst AS node_id, MIN(LEVEL) AS min_depth, COUNT(*) AS n_paths
          FROM dag_edge e
         START WITH e.src = 'EP11'
       CONNECT BY NOCYCLE PRIOR e.dst = e.src
         GROUP BY e.dst) r
  JOIN dag_node n ON n.node_id = r.node_id
 ORDER BY r.min_depth, r.node_id;

-- Q3. 2월 22일 밤 도적 전언(EP02)에서 시작해 '잎'(더 나갈 곳 없는 끝 node)에 닿는 경로만
--     CONNECT_BY_ISLEAF = 1 조건은 WHERE에 둔다(계층을 다 만든 뒤 거른다).
SELECT LEVEL AS depth,
       'EP02' || SYS_CONNECT_BY_PATH(e.dst, ' > ') AS full_path
  FROM dag_edge e
 WHERE CONNECT_BY_ISLEAF = 1
 START WITH e.src = 'EP02'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
 ORDER BY depth, full_path;

-- Q4. WHERE 와 CONNECT BY 조건의 차이 (SQLD 단골)
--   (a) CONNECT BY에 조건: 정보 흐름(INFORMATION_FLOW) edge는 '따라가지 않는다' → 그 아래 가지 전체가 잘린다
SELECT LEVEL AS depth, e.src, e.dst, e.edge_type
  FROM dag_edge e
 START WITH e.src = 'EP09'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
       AND e.edge_type <> 'INFORMATION_FLOW'
 ORDER SIBLINGS BY e.dst;

--   (b) WHERE에 조건: 계층은 끝까지 만들고, 결과에서 INFORMATION_FLOW 행만 '숨긴다' → 그 아래 행은 남는다
SELECT LEVEL AS depth, e.src, e.dst, e.edge_type
  FROM dag_edge e
 WHERE e.edge_type <> 'INFORMATION_FLOW'
 START WITH e.src = 'EP09'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
 ORDER SIBLINGS BY e.dst;

-- Q5. 시작 node 자체(LEVEL 0 개념)를 함께 보이기: node 표에서 출발해 edge를 붙이는 2단계 형태
--     node를 루트 행으로 쓰고 싶으면 '루트 = node, 자식 = edge'인 합집합을 만든다.
WITH graph AS (
    SELECT NULL AS src, 'EP13' AS dst, 'ROOT' AS edge_type FROM dual      -- 가상의 뿌리 행
    UNION ALL
    SELECT src, dst, edge_type FROM dag_edge
)
SELECT LEVEL - 1                        AS hops_from_ep13,
       g.dst                            AS node_id,
       g.edge_type                      AS via_edge_type,
       SYS_CONNECT_BY_PATH(g.dst, '/')  AS path
  FROM graph g
 START WITH g.edge_type = 'ROOT'
CONNECT BY NOCYCLE PRIOR g.dst = g.src
 ORDER SIBLINGS BY g.dst;

-- Q6. 깊이(LEVEL)별 edge 수 — 계층 결과도 GROUP BY로 집계할 수 있다
SELECT LEVEL AS depth, COUNT(*) AS n_edges, COUNT(DISTINCT e.dst) AS n_distinct_nodes
  FROM dag_edge e
 START WITH e.src = 'EP01'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
 GROUP BY LEVEL
 ORDER BY depth;
