-- =============================================================================
-- 07_sqld_drills / 08_set_operators.sql — UNION / UNION ALL / INTERSECT / MINUS
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q30. [기본] edge 조건(edge_identity_condition)이나 후보 조건(candidate_identity_condition)에 쓰인 동일성 ID를
--      (a) 중복 없이 (b) 중복 포함으로 구하시오.
-- 정답 SQL:
-- (a)
SELECT identity_id FROM edge_identity_condition
UNION
SELECT identity_id FROM candidate_identity_condition
ORDER BY 1;
-- (b)
SELECT identity_id FROM edge_identity_condition
UNION ALL
SELECT identity_id FROM candidate_identity_condition
ORDER BY 1;
-- 왜 맞는가: UNION은 합친 뒤 중복을 지우고(정렬 비용), UNION ALL은 그대로 붙인다.
-- 자주 틀리는 포인트: ORDER BY는 맨 마지막 SELECT 뒤에 한 번만. 컬럼 이름·위치는 첫 SELECT 기준.
-- 기대 결과: (a) ID02, ID03, ID06, ID07, ID08, ID09 (6행)   (b) 8행 (ID06·ID07이 양쪽에 한 번씩)


-- -----------------------------------------------------------------------------
-- Q31. [중간] world W1과 W2가 공통으로 쓰는 후보(bridge)를 INTERSECT로 구하시오.
-- 정답 SQL:
SELECT candidate_id FROM world_candidate WHERE world_id = 'W1'
INTERSECT
SELECT candidate_id FROM world_candidate WHERE world_id = 'W2'
ORDER BY 1;
-- 왜 맞는가: INTERSECT는 양쪽에 모두 있는 행(중복 제거)만 남긴다.
-- 자주 틀리는 포인트: 같은 결과를 JOIN으로 쓸 때 중복 행이 있으면 INTERSECT와 결과 행 수가 다를 수 있다.
-- 기대 결과: G01a, G03a, G08a, G09a, G12a (5행)


-- -----------------------------------------------------------------------------
-- Q32. [중간] world W1에만 있고 최소 가정 world W5에는 없는 후보를 MINUS로 구하시오.
-- 정답 SQL:
SELECT candidate_id FROM world_candidate WHERE world_id = 'W1'
MINUS
SELECT candidate_id FROM world_candidate WHERE world_id = 'W5'
ORDER BY 1;
-- 왜 맞는가: MINUS(표준 SQL의 EXCEPT)는 첫 결과에서 둘째 결과에 있는 행을 뺀다. 순서를 바꾸면 결과가 다르다.
-- 자주 틀리는 포인트: Oracle은 MINUS. EXCEPT는 Oracle 21c부터 동의어로 지원된다(그 이전은 오류).
-- 기대 결과: G02a, G03a, G04a, G05a, G09a, G11a, G12a, G13a (8행)


-- -----------------------------------------------------------------------------
-- Q33. [어려움] 동결 observed edge(dag_edge)와 Super-DAG에 복사된 FROZEN edge(sd_edge, origin = 'FROZEN')가
--      (edge_id, src, dst, edge_type, 상태) 단위로 완전히 같은지 대칭 차집합으로 확인하시오.
-- 정답 SQL:
(SELECT edge_id, src, dst, edge_type, status   AS st FROM dag_edge
 MINUS
 SELECT edge_id, src, dst, edge_type, sd_status       FROM sd_edge WHERE origin = 'FROZEN')
UNION ALL
(SELECT edge_id, src, dst, edge_type, sd_status       FROM sd_edge WHERE origin = 'FROZEN'
 MINUS
 SELECT edge_id, src, dst, edge_type, status          FROM dag_edge);
-- 왜 맞는가: A − B와 B − A를 합치면 '한쪽에만 있는 행'(대칭 차집합)이다. 0행이면 두 집합이 같다(Audit 4).
-- 자주 틀리는 포인트:
--   * 한 방향 MINUS만 하면 Super-DAG에 '추가된' frozen edge를 놓친다.
--   * 괄호 없이 쓰면 MINUS·UNION ALL이 왼쪽부터 차례로 적용되어 의도와 다른 결과가 된다.
-- 기대 결과: 0행
