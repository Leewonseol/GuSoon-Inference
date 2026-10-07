-- =============================================================================
-- 07_sqld_drills / 06_hierarchical.sql — 계층형 질의 (START WITH / CONNECT BY / PRIOR …)
-- 교과서 EMP 대신 이 사건의 판단·절차 DAG를 쓴다. 한 행 = edge 하나.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q22. [중간] 5월 12일 정조 1차 판단(EP15)에서 시작해 6월 판단까지 이어지는 검토·번복 사슬(revision chain)을
--      계층형 질의로 출력하시오. 판단 관계 edge(REVIEW_OF, REVISES, CONTRADICTS_AT_CLAIM_LEVEL)만 따라간다.
-- 정답 SQL:
SELECT LEVEL                                        AS depth,
       e.edge_type,
       e.dst,
       'EP15' || SYS_CONNECT_BY_PATH(e.dst, ' > ')  AS path
  FROM dag_edge e
 START WITH e.src = 'EP15'
        AND e.edge_type IN ('REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL')
CONNECT BY NOCYCLE PRIOR e.dst = e.src
       AND e.edge_type IN ('REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL')
 ORDER SIBLINGS BY e.dst;
-- 왜 맞는가: 'PRIOR dst = src'는 부모 edge의 도착 node에서 출발하는 edge를 자식으로 잇는다(시간 순방향).
--   type 조건을 START WITH와 CONNECT BY 양쪽에 둬야 '판단 관계로만' 이어진다.
-- 자주 틀리는 포인트:
--   * type 조건을 WHERE에만 두면 EP15→EP16(PROCEDURAL_NEXT) 가지를 따라 내려간 뒤 행만 숨긴다 → 아래 행이 섞인다.
--   * PRIOR를 반대쪽(PRIOR e.src = e.dst)에 쓰면 조상 방향으로 거슬러 올라간다.
-- 기대 결과: depth1 CONTRADICTS→EP24, depth2 REVIEW_OF→EP25 (경로 EP15>EP24>EP25), depth1 REVISES→EP25 (경로 EP15>EP25)


-- -----------------------------------------------------------------------------
-- Q23. [중간] 3월 4일 체포(EP11) 이후 더 나갈 곳이 없는 끝(leaf) node까지의 경로를 모두 구하시오.
-- 정답 SQL:
SELECT LEVEL AS depth, 'EP11' || SYS_CONNECT_BY_PATH(e.dst, ' > ') AS path_to_leaf
  FROM dag_edge e
 WHERE CONNECT_BY_ISLEAF = 1
 START WITH e.src = 'EP11'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
 ORDER BY depth, path_to_leaf;
-- 왜 맞는가: CONNECT_BY_ISLEAF는 계층을 다 만든 뒤 '자식이 없는 행'에 1을 준다. WHERE는 그 뒤에 걸러진다.
-- 자주 틀리는 포인트: CONNECT BY 절에 CONNECT_BY_ISLEAF = 1을 넣으면 오류이거나 의미가 달라진다.
-- 기대 결과: 14행. 끝 node는 EP19, EP28, EP32, EP33, EP34, EP35, EP37 (예: EP11 > EP13 > EP15 > EP16 > EP19)


-- -----------------------------------------------------------------------------
-- Q24. [어려움] 정조 구순 책임 판단(EP29)의 조상 node를 모두 구하고, 바로 연결된 조상(LEVEL 1)과
--      간접 조상(LEVEL ≥ 2)을 구분하시오. 같은 조상이 여러 경로로 나오면 최단 거리만.
-- 정답 SQL:
SELECT ancestor_id,
       MIN(depth)                                                AS min_hops,
       CASE WHEN MIN(depth) = 1 THEN 'DIRECT' ELSE 'INDIRECT' END AS relation
  FROM (SELECT e.src AS ancestor_id, LEVEL AS depth
          FROM dag_edge e
         START WITH e.dst = 'EP29'
       CONNECT BY NOCYCLE PRIOR e.src = e.dst)
 GROUP BY ancestor_id
 ORDER BY min_hops, ancestor_id;
-- 왜 맞는가: 'PRIOR src = dst'는 거꾸로 올라간다. DAG에서는 한 조상이 여러 경로로 나오므로 GROUP BY로 정리.
-- 자주 틀리는 포인트: 트리라고 생각하고 DISTINCT 없이 세면 조상 수가 부풀려진다.
-- 기대 결과: 6행. DIRECT = EP01, EP08, EP11, EP13 (RESPONSIBILITY_LINK 4건) / INDIRECT = EP09, EP10 (min_hops 2)


-- -----------------------------------------------------------------------------
-- Q25. [어려움] 실제 DAG에는 cycle이 없음을 확인하고, '6/16 유임(EP37) → 관계 변화(EP01)' 가짜 edge를 WITH로
--      더했을 때 CONNECT_BY_ISCYCLE이 cycle을 잡아내는지 보이시오.
-- 정답 SQL:
-- (a) 실제 데이터 — 기대 0행
SELECT e.src || SYS_CONNECT_BY_PATH(e.dst, '>') AS cycle_path
  FROM dag_edge e
 WHERE CONNECT_BY_ISCYCLE = 1
CONNECT BY NOCYCLE PRIOR e.dst = e.src;
-- (b) 가짜 edge 추가 — 기대 1행 이상
WITH g AS (
    SELECT src, dst FROM dag_edge
    UNION ALL
    SELECT 'EP37', 'EP01' FROM dual
)
SELECT g.src || SYS_CONNECT_BY_PATH(g.dst, '>') AS cycle_path
  FROM g
 WHERE CONNECT_BY_ISCYCLE = 1
 START WITH g.src = 'EP37'
CONNECT BY NOCYCLE PRIOR g.dst = g.src;
-- 왜 맞는가: NOCYCLE은 cycle에서 멈추고, 멈춘 지점 행에 CONNECT_BY_ISCYCLE = 1을 표시한다.
--   EP01 → EP23(정보 흐름) → EP36(파직) → EP37(유임) → (가짜) EP01 로 닫힌다.
-- 자주 틀리는 포인트: NOCYCLE 없이 CONNECT_BY_ISCYCLE을 쓰면 오류(ORA-30930). cycle이 있는데 NOCYCLE이 없으면 ORA-01436.


-- -----------------------------------------------------------------------------
-- Q26. [어려움] 관계 변화(EP01)에서 닿을 수 있는 node 가운데 판단 layer(ROYAL_JUDGMENT·OFFICIAL_FINDING·
--      OFFICIAL_EVALUATION) node만 중복 없이 구하시오. 직접 edge가 있는 판단은 표시하시오.
-- 정답 SQL:
SELECT r.node_id,
       n.layer,
       CASE WHEN EXISTS (SELECT 1 FROM dag_edge d WHERE d.src = 'EP01' AND d.dst = r.node_id)
            THEN 'Y' ELSE 'N' END AS direct_edge
  FROM (SELECT DISTINCT e.dst AS node_id
          FROM dag_edge e
         START WITH e.src = 'EP01'
       CONNECT BY NOCYCLE PRIOR e.dst = e.src) r
  JOIN dag_node n ON n.node_id = r.node_id
 WHERE n.layer IN ('ROYAL_JUDGMENT', 'OFFICIAL_FINDING', 'OFFICIAL_EVALUATION')
 ORDER BY r.node_id;
-- 왜 맞는가: 계층형 질의 결과를 인라인 뷰로 감싸면 일반 표처럼 조인·필터할 수 있다.
-- 자주 틀리는 포인트: '닿을 수 있다(경로)'와 '직접 연결(edge)'은 다르다. EP01에서 사인 판단(EP26·EP27)에는
--   홍대협 신문(EP23)을 거쳐 닿지만 직접 edge는 없다(Audit 2 FORBIDDEN_DIRECT 규칙).
-- 기대 결과: 9행 — EP24, EP25, EP26, EP27, EP28, EP29, EP30, EP31, EP32. 직접 edge = EP29만 'Y'
