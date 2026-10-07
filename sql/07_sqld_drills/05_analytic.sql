-- =============================================================================
-- 07_sqld_drills / 05_analytic.sql — 분석(윈도우) 함수
-- 정렬 키: 발생 시점 NVL(t_max, t_min) (음력 MMDD)
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q17. [기본] 같은 사건(도난 판단, branch = 'THEFT_JUDGMENT')에 대한 판단 순서를 ROW_NUMBER로 구하시오.
--      같은 날이면 node_id 순.
-- 정답 SQL:
SELECT node_id,
       layer,
       NVL(t_max, t_min) AS sort_key,
       ROW_NUMBER() OVER (ORDER BY NVL(t_max, t_min), node_id) AS judgment_seq
  FROM dag_node
 WHERE branch = 'THEFT_JUDGMENT'
 ORDER BY judgment_seq;
-- 왜 맞는가: ROW_NUMBER는 동점이 있어도 1,2,3,4로 유일한 순번을 준다. 동점 순서를 정하려면 ORDER BY에 두 번째 키가 필요하다.
-- 자주 틀리는 포인트: 두 번째 키(node_id)를 빼면 6/13 두 판단(EP24·EP25)의 순번이 실행마다 바뀔 수 있다.
-- 기대 결과: EP15(1, 5/12 정조 1차) → EP17(2, 5/27 이조원) → EP24(3, 홍대협) → EP25(4, 정조 최종)


-- -----------------------------------------------------------------------------
-- Q18. [중간] 국왕 판단·명령 node(layer IN ROYAL_JUDGMENT, ROYAL_ORDER)를 발생 시점으로 순위 매길 때
--      RANK와 DENSE_RANK 결과 차이를 보이시오.
-- 정답 SQL:
SELECT node_id,
       NVL(t_max, t_min)                               AS sort_key,
       RANK()       OVER (ORDER BY NVL(t_max, t_min))  AS rnk,
       DENSE_RANK() OVER (ORDER BY NVL(t_max, t_min))  AS dense_rnk
  FROM dag_node
 WHERE layer IN ('ROYAL_JUDGMENT', 'ROYAL_ORDER')
 ORDER BY sort_key, node_id;
-- 왜 맞는가: 같은 날(동점)은 같은 순위. RANK는 동점 수만큼 다음 순위를 건너뛰고 DENSE_RANK는 건너뛰지 않는다.
-- 자주 틀리는 포인트: 동점 처리를 ROW_NUMBER와 혼동. ROW_NUMBER는 동점에도 다른 번호.
-- 기대 결과: 5/12 두 건(EP15·EP16) 둘 다 1 / 5/27 EP19: RANK 3, DENSE 2 / 5/28 EP20: 4, 3 /
--            6/13 10건: RANK 5, DENSE 4 / 6/16 EP37: RANK 15, DENSE 5


-- -----------------------------------------------------------------------------
-- Q19. [중간] 도난 판단 branch에서 직전 판단과 layer(판단 주체 층위)가 달라진 지점을 찾으시오.
-- 힌트: LAG로 직전 행 값을 가져온 뒤 인라인 뷰 밖에서 비교한다.
-- 정답 SQL:
SELECT node_id, prev_node, prev_layer, layer
  FROM (SELECT node_id,
               layer,
               LAG(node_id) OVER (ORDER BY NVL(t_max, t_min), node_id) AS prev_node,
               LAG(layer)   OVER (ORDER BY NVL(t_max, t_min), node_id) AS prev_layer
          FROM dag_node
         WHERE branch = 'THEFT_JUDGMENT')
 WHERE prev_layer <> layer
 ORDER BY node_id;
-- 왜 맞는가: 분석 함수는 WHERE보다 나중에 계산되므로 분석 결과로 거르려면 한 겹 감싸야 한다.
-- 자주 틀리는 포인트:
--   * WHERE LAG(layer) OVER (…) <> layer → ORA-30483(window functions are not allowed here).
--   * 첫 행은 prev_layer가 NULL → '<>' 비교가 UNKNOWN이라 자동으로 빠진다(의도한 동작).
-- 기대 결과: EP17(ROYAL_JUDGMENT→INSPECTOR_REPORT), EP24(→OFFICIAL_FINDING), EP25(→ROYAL_JUDGMENT) 3행


-- -----------------------------------------------------------------------------
-- Q20. [어려움] branch마다 '가장 늦은 판단' 1건을 고르시오. 판단 = layer가 ROYAL_JUDGMENT·OFFICIAL_FINDING·
--      OFFICIAL_EVALUATION·INSPECTOR_REPORT. 같은 날이면 node_id가 큰 것. (Oracle에는 QUALIFY가 없다)
-- 정답 SQL:
SELECT branch, node_id, sort_key
  FROM (SELECT branch, node_id, NVL(t_max, t_min) AS sort_key,
               ROW_NUMBER() OVER (PARTITION BY branch
                                  ORDER BY NVL(t_max, t_min) DESC, node_id DESC) AS rn
          FROM dag_node
         WHERE layer IN ('ROYAL_JUDGMENT', 'OFFICIAL_FINDING', 'OFFICIAL_EVALUATION', 'INSPECTOR_REPORT'))
 WHERE rn = 1
 ORDER BY branch;
-- 왜 맞는가: PARTITION BY가 묶음을 나누고, 묶음 안에서 내림차순 1번이 최신이다.
-- 자주 틀리는 포인트:
--   * GROUP BY branch + MAX(sort_key)는 '최신 날짜'만 주고 node_id를 같이 못 준다(MAX(node_id)는 다른 행일 수 있음).
--   * RANK를 쓰면 동점일 때 2건 이상이 1위가 된다.
-- 기대 결과: branch별 1행 (예: THEFT_JUDGMENT → EP25, BIOLOGICAL → EP27, JISE → EP32)


-- -----------------------------------------------------------------------------
-- Q21. [어려움] 각 판단 옆에 그 branch의 '첫 판단'과 '마지막 판단'을 붙이시오(BIOLOGICAL·THEFT_JUDGMENT·JISE).
--      LAST_VALUE의 기본 창 함정을 피할 것.
-- 정답 SQL:
SELECT node_id,
       branch,
       FIRST_VALUE(node_id) OVER (PARTITION BY branch ORDER BY NVL(t_max, t_min), node_id) AS first_judgment,
       LAST_VALUE(node_id)  OVER (PARTITION BY branch ORDER BY NVL(t_max, t_min), node_id
                                  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_judgment
  FROM dag_node
 WHERE branch IN ('BIOLOGICAL', 'THEFT_JUDGMENT', 'JISE')
 ORDER BY branch, NVL(t_max, t_min), node_id;
-- 왜 맞는가: ORDER BY가 있는 OVER의 기본 창은 '처음 ~ 현재 행'(RANGE … CURRENT ROW)이다.
--   LAST_VALUE가 묶음 전체의 마지막을 보려면 창을 UNBOUNDED FOLLOWING까지 넓혀야 한다.
-- 자주 틀리는 포인트: 창 지정 없이 LAST_VALUE를 쓰면 각 행 자신(또는 동점 묶음의 마지막)이 나온다.
-- 기대 결과: THEFT_JUDGMENT 4행 모두 first=EP15, last=EP25 / BIOLOGICAL first=EP26, last=EP27 / JISE first=EP31, last=EP32
