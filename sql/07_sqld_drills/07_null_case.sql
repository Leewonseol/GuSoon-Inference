-- =============================================================================
-- 07_sqld_drills / 07_null_case.sql — NULL · CASE · DECODE
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q27. [기본] 발생 끝 시점(t_max)이 기록되지 않은 node 수를 COUNT 함수만으로 구하시오.
-- 정답 SQL:
SELECT COUNT(*) - COUNT(t_max) AS n_open_or_undated
  FROM dag_node;
-- 왜 맞는가: COUNT(*)는 모든 행, COUNT(t_max)는 NULL이 아닌 행만 센다.
-- 자주 틀리는 포인트: WHERE t_max = NULL은 항상 0행. NULL은 IS NULL로만 찾는다.
-- 기대 결과: 4 (EP03·EP06·EP07은 '…이후' 열린 구간, EP08은 날짜 미기록 — 임의 날짜를 만들지 않음)


-- -----------------------------------------------------------------------------
-- Q28. [기본] Super-DAG node를 상태별로 CASE로 다섯 분류(OBSERVED / LATENT / CONTEXT / UNRESOLVED / 기타)하고
--      분류별 개수를 구하시오. LATENT_MECHANISM은 'LATENT'로 표시.
-- 정답 SQL:
SELECT status_class, COUNT(*) AS n
  FROM (SELECT CASE sd_status
                   WHEN 'OBSERVED'         THEN 'OBSERVED'
                   WHEN 'LATENT_MECHANISM' THEN 'LATENT'
                   WHEN 'CONTEXT'          THEN 'CONTEXT'
                   WHEN 'UNRESOLVED'       THEN 'UNRESOLVED'
                   ELSE '기타'
               END AS status_class
          FROM sd_node)
 GROUP BY status_class
 ORDER BY status_class;
-- 왜 맞는가: 단순 CASE는 한 컬럼 값을 차례로 비교한다. 분류한 결과로 묶으려면 인라인 뷰로 감싸거나
--   GROUP BY에 CASE 식 전체를 똑같이 적는다(SELECT 별칭은 GROUP BY에서 못 쓴다).
-- 자주 틀리는 포인트: GROUP BY status_class(별칭)를 바로 쓰면 ORA-00904(Oracle 23ai 이전).
-- 기대 결과: CONTEXT 24 / LATENT 55 / OBSERVED 37 / UNRESOLVED 6 (Python Audit 4 super_dag_summary와 같음)


-- -----------------------------------------------------------------------------
-- Q29. [중간] '어느 node에도 쓰이지 않은 환경 행'을 NOT IN으로 찾았더니 결과가 0행이었다.
--      (1) 왜 NOT IN이 위험한지 설명하고 (2) 안전한 SQL로 다시 쓰시오.
-- 위험한 SQL:
SELECT ec.env_id
  FROM environment_context ec
 WHERE ec.env_id NOT IN (SELECT n.env_id FROM dag_node n);
-- 정답 SQL (둘 다 맞음):
SELECT ec.env_id
  FROM environment_context ec
 WHERE ec.env_id NOT IN (SELECT n.env_id FROM dag_node n WHERE n.env_id IS NOT NULL);

SELECT ec.env_id
  FROM environment_context ec
 WHERE NOT EXISTS (SELECT 1 FROM dag_node n WHERE n.env_id = ec.env_id);
-- 왜 맞는가: dag_node.env_id는 사건 node 37개에서 NULL이다. x NOT IN (…, NULL)은 x <> NULL이 UNKNOWN이라
--   어떤 x도 참이 되지 못한다. NULL을 빼거나 NOT EXISTS(NULL과 무관)를 쓴다.
-- 자주 틀리는 포인트: 위험한 SQL과 안전한 SQL이 '이번 데이터에서는' 둘 다 0행이라 차이를 못 느낀다.
--   환경 행 하나를 node에서 지워 보면(연습) 위험한 SQL만 여전히 0행이다.
-- 기대 결과: 세 SQL 모두 0행 (E001–E004 모두 ENV01–ENV04로 쓰임). 단, 첫 SQL은 '항상' 0행.
