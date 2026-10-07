-- =============================================================================
-- hierarchical_queries.sql — SQLD 계층형 질의 요점 정리 (자세한 그래프 질의는 06_graph/)
-- -----------------------------------------------------------------------------
--  START WITH        : 뿌리(LEVEL 1) 행 조건
--  CONNECT BY PRIOR  : PRIOR가 붙은 쪽 = 부모 행. 'PRIOR 자식키 = 부모키' 방향이 위→아래인지 아래→위인지 결정
--  LEVEL             : 뿌리 1부터의 깊이
--  CONNECT_BY_ROOT   : 뿌리 행의 컬럼 값
--  SYS_CONNECT_BY_PATH(col, '구분자') : 뿌리부터 현재까지 col 값을 이은 문자열
--  CONNECT_BY_ISLEAF : 자식이 없으면 1
--  CONNECT_BY_ISCYCLE: (NOCYCLE과 함께) 다음 자식이 조상으로 돌아가면 1
--  NOCYCLE           : cycle이 있어도 오류(ORA-01436) 없이 멈춘다
--  ORDER SIBLINGS BY : 계층 모양을 유지하며 형제끼리만 정렬
-- 처리 순서: (조인) → START WITH → CONNECT BY → WHERE → (GROUP BY) → ORDER BY
-- =============================================================================

-- 1. 순방향(위→아래): 소장·체포령(EP03) 이후
SELECT LEVEL, e.src, e.dst, e.edge_type
  FROM dag_edge e
 START WITH e.src = 'EP03'
CONNECT BY PRIOR e.dst = e.src;            -- PRIOR가 dst 쪽: 부모의 도착 = 자식의 출발

-- 2. 역방향(아래→위): 정조 이광섭 책임 판단(EP30)의 조상
SELECT LEVEL, e.src, e.dst, e.edge_type
  FROM dag_edge e
 START WITH e.dst = 'EP30'
CONNECT BY PRIOR e.src = e.dst;            -- PRIOR가 src 쪽: 부모의 출발 = 자식의 도착

-- 3. 모든 계층 의사 컬럼을 한 번에 — 5월 판단(EP15) 이후
SELECT LEVEL                                       AS lvl,
       CONNECT_BY_ROOT e.src                       AS root,
       e.dst,
       'EP15' || SYS_CONNECT_BY_PATH(e.dst, '/')   AS path,
       CONNECT_BY_ISLEAF                           AS is_leaf,
       CONNECT_BY_ISCYCLE                          AS is_cycle
  FROM dag_edge e
 START WITH e.src = 'EP15'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
 ORDER SIBLINGS BY e.dst;

-- 4. 복합 CONNECT BY 조건: 같은 후보 안에서만 LATENT mini-DAG를 따라간다
--    PRIOR e.candidate_id = e.candidate_id 가 없으면 다른 후보의 latent edge로 건너갈 수 있다.
SELECT e.candidate_id,
       LEVEL                                          AS step,
       e.src || SYS_CONNECT_BY_PATH(e.dst, ' → ')     AS latent_path,
       e.edge_type
  FROM latent_element e
 WHERE e.candidate_id IN ('G01a', 'G06a')
 START WITH e.kind = 'edge'
        AND e.src NOT LIKE 'LN\_%' ESCAPE '\'                   -- 관측 node에서 출발하는 latent edge
CONNECT BY NOCYCLE PRIOR e.dst = e.src
       AND PRIOR e.candidate_id = e.candidate_id
       AND e.kind = 'edge'
 ORDER SIBLINGS BY e.dst;

-- 5. 계층형 질의 + 집계: 출발 node별 도달 가능한 node 수 (전이 폐쇄 크기)
SELECT CONNECT_BY_ROOT e.src AS start_node, COUNT(DISTINCT e.dst) AS n_reachable
  FROM dag_edge e
CONNECT BY NOCYCLE PRIOR e.dst = e.src
 GROUP BY CONNECT_BY_ROOT e.src
 ORDER BY n_reachable DESC, start_node;

-- 6. 행 생성기(row generator): CONNECT BY LEVEL <= n
--    '|' 목록 펴기(02_load/04_transform_to_canonical.sql)와 같은 원리. world W1의 bridge 목록을 행으로
SELECT w.world_id,
       seq.n                                          AS bridge_no,
       REGEXP_SUBSTR(w.latent_bridges, '[^|]+', 1, seq.n) AS candidate_id
  FROM narrative_world w
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(w.latent_bridges, '[^|]+')
 WHERE w.world_id = 'W1'
 ORDER BY bridge_no;

-- 7. 표준 SQL의 재귀 WITH(Oracle 11gR2+)로 같은 결과 — 참고용(시험은 주로 CONNECT BY)
--    재귀 WITH는 반드시 컬럼 목록을 적고, UNION ALL 아래에서 자기 자신을 참조한다.
WITH descendants (src, dst, depth, path) AS (
    SELECT e.src, e.dst, 1, e.src || '>' || e.dst
      FROM dag_edge e
     WHERE e.src = 'EP03'
    UNION ALL
    SELECT e.src, e.dst, d.depth + 1, d.path || '>' || e.dst
      FROM descendants d
      JOIN dag_edge e ON e.src = d.dst
)
CYCLE dst SET is_cycle TO 'Y' DEFAULT 'N'
SELECT depth, src, dst, path
  FROM descendants
 ORDER BY depth, path;
