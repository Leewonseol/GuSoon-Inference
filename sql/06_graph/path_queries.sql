-- =============================================================================
-- path_queries.sql — 두 node 사이의 경로, 책임 사슬, 정보 흐름 사슬, 절차 순서
-- =============================================================================

-- Q1. 관계 변화(EP01) → 정조 구순 책임 판단(EP29)의 모든 경로
--     START WITH로 출발점을 고정하고, WHERE로 '도착점이 EP29인 행'만 남긴다.
SELECT LEVEL                                      AS n_edges,
       'EP01' || SYS_CONNECT_BY_PATH(e.dst, ' > ') AS path,
       SYS_CONNECT_BY_PATH(e.edge_type, ' / ')     AS edge_types
  FROM dag_edge e
 WHERE e.dst = 'EP29'
 START WITH e.src = 'EP01'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
 ORDER BY n_edges, path;

-- Q2. 도적 전언(EP02) → 정조 최종 도난 판단(EP25)의 최단 경로 길이와 그 경로들
--     분석 함수 MIN() OVER ()로 '최단 길이'를 모든 행에 붙인 뒤 같은 길이만 남긴다.
SELECT n_edges, path
  FROM (SELECT LEVEL                                      AS n_edges,
               'EP02' || SYS_CONNECT_BY_PATH(e.dst, ' > ') AS path,
               MIN(LEVEL) OVER ()                          AS shortest
          FROM dag_edge e
         WHERE e.dst = 'EP25'
         START WITH e.src = 'EP02'
       CONNECT BY NOCYCLE PRIOR e.dst = e.src)
 WHERE n_edges = shortest;

-- Q3. responsibility chain — 책임 판단(EP29, EP30)과 그 처분(EP33, EP34)까지
--     RESPONSIBILITY_LINK로 판단에 들어온 관측 → 판단 → PROCEDURAL_NEXT로 처분.
--     출발 = 책임 link의 출발 관측, 진행은 RESPONSIBILITY_LINK·PROCEDURAL_NEXT만 따라간다.
SELECT CONNECT_BY_ROOT e.src                     AS observed_basis,
       LEVEL                                     AS step,
       e.src || ' -[' || e.edge_type || ']-> ' || e.dst AS step_text,
       CONNECT_BY_ROOT e.src || SYS_CONNECT_BY_PATH(e.dst, ' > ') AS chain,
       CONNECT_BY_ISLEAF                         AS is_end
  FROM dag_edge e
 START WITH e.edge_type = 'RESPONSIBILITY_LINK'
        AND e.src NOT IN ('EP29')                -- 판단 → 판단(EP29→EP30) link는 출발점에서 뺀다
CONNECT BY NOCYCLE PRIOR e.dst = e.src
       AND e.edge_type IN ('RESPONSIBILITY_LINK', 'PROCEDURAL_NEXT')
 ORDER SIBLINGS BY e.dst;

-- Q4. information-flow chain — 홍대협 공주목 신문·복명(EP23)으로 모인 정보원
--     INFORMATION_FLOW edge만 거꾸로 1단계. 조사(EP23)가 어떤 관측들을 다시 들여다보았는가.
SELECT e.src                 AS information_source,
       n.title,
       n.t_min,
       n.record_lunar_date
  FROM dag_edge e
  JOIN dag_node n ON n.node_id = e.src
 WHERE e.dst = 'EP23'
   AND e.edge_type = 'INFORMATION_FLOW'
 ORDER BY n.t_min NULLS LAST, e.src;

-- Q5. arrest → detention → review → final judgment 순서
--     3/4 체포 지시(EP09)에서 정조 최종 도난 판단(EP25)까지의 경로를 따라 node의 발생 시점(t_min)이
--     뒤로 가지 않는지 확인한다. 경로 문자열을 다시 행으로 펴서(REGEXP_SUBSTR) 순번을 붙인다.
WITH paths AS (
    SELECT ROWNUM                                    AS path_no,
           'EP09' || SYS_CONNECT_BY_PATH(e.dst, '>') AS path
      FROM dag_edge e
     WHERE e.dst = 'EP25'
     START WITH e.src = 'EP09'
   CONNECT BY NOCYCLE PRIOR e.dst = e.src
), steps AS (
    SELECT p.path_no,
           s.n                                        AS step_no,
           REGEXP_SUBSTR(p.path, '[^>]+', 1, s.n)     AS node_id
      FROM paths p
      JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) s
        ON s.n <= REGEXP_COUNT(p.path, '[^>]+')
)
SELECT st.path_no,
       st.step_no,
       st.node_id,
       n.layer,
       n.t_min,
       LAG(n.t_min) OVER (PARTITION BY st.path_no ORDER BY st.step_no)    AS prev_t_min,
       CASE WHEN n.t_min < LAG(n.t_min) OVER (PARTITION BY st.path_no ORDER BY st.step_no)
            THEN 'INVERSION' ELSE 'OK' END                               AS order_check
  FROM steps st
  JOIN dag_node n ON n.node_id = st.node_id
 ORDER BY st.path_no, st.step_no;

-- Q6. 사망 branch 분리 — 생물학 branch A(EP26→EP27)와 책임 branch B(→EP29)가 공유하는 조상은 있지만
--     A의 node에서 B의 node로(또는 반대로) 가는 경로는 없어야 한다.
SELECT r.ancestor_id, r.descendant_id
  FROM v_dag_reachability r
 WHERE (r.ancestor_id IN ('EP26', 'EP27') AND r.descendant_id IN ('EP29', 'EP30'))
    OR (r.ancestor_id IN ('EP29', 'EP30') AND r.descendant_id IN ('EP26', 'EP27'));
-- 기대: 0행

-- Q7. 경로 길이 분포 — EP01에서 출발하는 모든 경로의 끝 node(잎)별 경로 수와 길이 범위
SELECT leaf_node,
       COUNT(*)      AS n_paths,
       MIN(n_edges)  AS shortest,
       MAX(n_edges)  AS longest
  FROM (SELECT e.dst AS leaf_node, LEVEL AS n_edges
          FROM dag_edge e
         WHERE CONNECT_BY_ISLEAF = 1
         START WITH e.src = 'EP01'
       CONNECT BY NOCYCLE PRIOR e.dst = e.src)
 GROUP BY leaf_node
 ORDER BY n_paths DESC, leaf_node;
