-- =============================================================================
-- basic_select.sql — SELECT · WHERE · ORDER BY · DISTINCT · LIKE · BETWEEN · IN · Top-N
-- =============================================================================

-- 1. 확정 사실 50개 중 RECORDED_TESTIMONY(진술 기록)만 — 비교 연산자 =
SELECT fact_id, subject, confirmed_statement
  FROM confirmed_fact
 WHERE confirmation_level = 'RECORDED_TESTIMONY'
 ORDER BY fact_id;

-- 2. 열 별칭(AS)과 연결 연산자(||): "[CF001] 김명신·구순" 형태
SELECT '[' || fact_id || '] ' || subject AS fact_label,
       record_lunar_date                 AS "기록일"         -- 큰따옴표 별칭: 한글·공백 허용
  FROM confirmed_fact
 ORDER BY fact_id;

-- 3. DISTINCT: 확정 사실이 나온 사료 기사 목록
SELECT DISTINCT source_record_id, source_work
  FROM confirmed_fact
 ORDER BY source_record_id;

-- 4. LIKE: 이름에 '정조'가 들어간 판단 episode, 와일드카드 % (여러 글자) / _ (한 글자)
SELECT node_id, layer, title
  FROM dag_node
 WHERE title LIKE '%정조%'
 ORDER BY node_id;

-- 4-1. ESCAPE: 밑줄(_) 자체를 찾을 때. layer 값 중 '_AND_'가 들어간 것
SELECT DISTINCT layer
  FROM dag_node
 WHERE layer LIKE '%\_AND\_%' ESCAPE '\';

-- 5. BETWEEN: 음력 2월 22일(222) ~ 3월 4일(304) 사이에 시작한 사건 (양 끝 포함)
SELECT node_id, t_min, t_max, title
  FROM dag_node
 WHERE t_min BETWEEN 222 AND 304
 ORDER BY t_min, node_id;

-- 6. IN: 판단·평가 layer만
SELECT node_id, layer, title
  FROM dag_node
 WHERE layer IN ('ROYAL_JUDGMENT', 'OFFICIAL_EVALUATION', 'OFFICIAL_FINDING')
 ORDER BY layer, node_id;

-- 7. 여러 정렬 기준과 DESC: edge type별, 같은 type 안에서는 edge_id 내림차순
SELECT edge_id, edge_type, src, dst
  FROM dag_edge
 ORDER BY edge_type ASC, edge_id DESC;

-- 8. ORDER BY에 별칭·위치 번호 사용 (SELECT 다음에 처리되므로 별칭을 쓸 수 있다)
SELECT node_id, NVL(t_max, t_min) AS sort_key, title
  FROM dag_node
 ORDER BY sort_key NULLS LAST, 1;

-- 9. Top-N (12c+): 후보 중 추가 가정이 가장 많은 3개
SELECT candidate_id, n_assumptions, label
  FROM latent_candidate
 ORDER BY n_assumptions DESC, candidate_id
 FETCH FIRST 3 ROWS ONLY;

-- 9-1. 동점 포함 (WITH TIES): 3번째와 추가 가정 수가 같은 후보도 모두
SELECT candidate_id, n_assumptions
  FROM latent_candidate
 ORDER BY n_assumptions DESC
 FETCH FIRST 3 ROWS WITH TIES;

-- 9-2. 11g 이하 Top-N: ROWNUM은 ORDER BY 전에 붙으므로 인라인 뷰에서 먼저 정렬해야 한다(단골 함정)
SELECT candidate_id, n_assumptions
  FROM (SELECT candidate_id, n_assumptions
          FROM latent_candidate
         ORDER BY n_assumptions DESC, candidate_id)
 WHERE ROWNUM <= 3;

-- 9-3. 틀린 예 (주석): 정렬 전에 ROWNUM 3개를 자른 뒤 정렬한다 → '아무' 3행의 정렬
-- SELECT candidate_id, n_assumptions FROM latent_candidate WHERE ROWNUM <= 3 ORDER BY n_assumptions DESC;

-- 10. 산술 연산과 함수: t_min(MMDD)을 월·일로 나누기 — TRUNC, MOD
SELECT node_id,
       t_min,
       TRUNC(t_min / 100) AS lunar_month,
       MOD(t_min, 100)    AS lunar_day
  FROM dag_node
 WHERE t_min IS NOT NULL
 ORDER BY t_min, node_id;

-- 11. 문자 함수: SUBSTR / INSTR / LENGTH / REPLACE / UPPER
SELECT source_record_id,
       SUBSTR(source_record_id, 1, 4)                 AS prefix,
       INSTR(source_url, '/', -1)                     AS last_slash_pos,   -- 뒤에서부터 찾기
       SUBSTR(source_url, INSTR(source_url, '/', -1) + 1) AS url_tail,
       LENGTH(source_title)                           AS title_chars,
       LENGTHB(source_title)                          AS title_bytes       -- 한글 1글자 = 3 byte(AL32UTF8)
  FROM source_record
 ORDER BY source_record_id;
