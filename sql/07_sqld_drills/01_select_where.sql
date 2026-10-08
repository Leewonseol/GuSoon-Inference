-- =============================================================================
-- 07_sqld_drills / 01_select_where.sql — SELECT · WHERE · ORDER BY · Top-N
-- 형식: 문제 / 힌트 / 정답 SQL / 왜 맞는가 / 자주 틀리는 포인트 / 기대 결과
-- 기대 결과는 canonical 데이터 기준이다(실행 확인 방법은 sql/README.md §실행 상태).
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q1. [기본] 동결된 observed DAG(dag_node)에서 node_status가 OBSERVED인 node 수를 구하시오.
-- 힌트: WHERE로 거른 뒤 COUNT(*).
-- 정답 SQL:
SELECT COUNT(*) AS n_observed_nodes
  FROM dag_node
 WHERE node_status = 'OBSERVED';
-- 왜 맞는가: dag_node 한 행 = node 하나. 조건을 만족하는 행 수를 센다.
-- 자주 틀리는 포인트:
--   * Super-DAG(sd_node)의 OBSERVED는 37개다. 동결 DAG에서는 환경 context node 4개도 OBSERVED(관측된 환경 기록)지만,
--     Super-DAG에서는 같은 4개가 CONTEXT로 분류된다. '어느 표의 status인가'를 먼저 확인할 것.
--   * 문자열 비교는 대소문자를 구분한다('observed'로 쓰면 0).
-- 기대 결과: 41


-- -----------------------------------------------------------------------------
-- Q2. [기본] 음력 3월 4일 하루에 일어난 사건 node를 node_id 순으로 출력하시오(node_id, title).
-- 힌트: 발생 구간은 t_min·t_max(음력 MMDD 정수). 기록일(record_lunar_date)과 혼동하지 말 것.
-- 정답 SQL:
SELECT node_id, title
  FROM dag_node
 WHERE t_min = 304
   AND t_max = 304
 ORDER BY node_id;
-- 왜 맞는가: 하루짜리 사건은 시작과 끝이 같은 날(304)이다.
-- 자주 틀리는 포인트:
--   * record_lunar_date = '1793-03-04'로 찾으면 0행이다. 3/4 사건은 6/13 안핵 공초에서 기록되었다(기록일 ≠ 발생일).
--   * t_min = 304만 쓰면 3/4에 '시작'한 열린 구간 사건까지 섞일 수 있다.
-- 기대 결과: EP09, EP10, EP11 (3행)


-- -----------------------------------------------------------------------------
-- Q3. [기본] layer가 ROYAL_JUDGMENT이고 제목(title)에 '정조'가 들어간 node를 구하시오.
-- 힌트: LIKE '%…%'와 AND.
-- 정답 SQL:
SELECT node_id, title
  FROM dag_node
 WHERE layer = 'ROYAL_JUDGMENT'
   AND title LIKE '%정조%'
 ORDER BY node_id;
-- 왜 맞는가: %는 0글자 이상 아무 글자. 앞뒤에 붙이면 '포함'이 된다.
-- 자주 틀리는 포인트: LIKE '정조%'는 '정조로 시작'만 찾는다('5월 12일 정조 …'가 빠진다).
-- 기대 결과: EP15, EP25, EP27, EP28, EP29, EP30, EP32 (7행)


-- -----------------------------------------------------------------------------
-- Q4. [기본] LATENT 후보 중 추가 가정(n_assumptions)이 가장 많은 3개를 구하되, 3위와 동점인 후보도 모두 포함하시오.
-- 힌트: Oracle 12c+ FETCH FIRST … WITH TIES.
-- 정답 SQL:
SELECT candidate_id, n_assumptions
  FROM latent_candidate
 ORDER BY n_assumptions DESC
 FETCH FIRST 3 ROWS WITH TIES;
-- 왜 맞는가: WITH TIES는 마지막(3번째) 행과 정렬 값이 같은 행을 모두 더 돌려준다.
-- 자주 틀리는 포인트:
--   * WHERE ROWNUM <= 3 ORDER BY …는 '정렬 전에' 3행을 자른다. 11g 이하는 인라인 뷰에서 먼저 정렬한 뒤 ROWNUM.
--   * ONLY를 쓰면 동점이 잘린다.
-- 기대 결과: 6행 — 추가 가정 3개(최대)인 G01c, G02b, G03a, G04b, G04d, G09c (ONLY였다면 3행에서 잘림)
