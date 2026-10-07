-- =============================================================================
-- null_and_case.sql — NULL 처리와 CASE / DECODE
-- -----------------------------------------------------------------------------
-- Oracle의 NULL 규칙 (SQLD 단골)
--   * ''(빈 문자열)은 NULL이다. CSV의 빈 칸은 적재 후 NULL이 된다.
--   * NULL과의 비교(=, <>, >, <)는 UNKNOWN → WHERE에서 걸러진다. 반드시 IS NULL / IS NOT NULL.
--   * 산술에 NULL이 끼면 결과 NULL. 단, 문자열 연결(||)은 NULL을 빈 문자열처럼 다룬다(Oracle 특유).
--   * 집계 함수는 NULL을 무시한다(COUNT(*)만 예외).
-- =============================================================================

-- 1. IS NULL: 발생 끝(t_max)이 열린 구간인 사건 — '이후' 같은 열린 표현이라 끝을 정하지 않았다
SELECT node_id, t_min, t_max, occurrence_text
  FROM dag_node
 WHERE t_max IS NULL
 ORDER BY node_id;

-- 2. '= NULL'은 아무것도 찾지 못한다 (UNKNOWN). 결과 0행
SELECT node_id FROM dag_node WHERE t_max = NULL;

-- 3. NVL / NVL2 / COALESCE / NULLIF
SELECT node_id,
       t_min,
       t_max,
       NVL(t_max, t_min)                       AS sort_key,          -- t_max 없으면 t_min
       NVL2(t_max, '닫힌 구간', '열린 구간')   AS interval_kind,      -- NULL 아님/NULL에 따라 다른 값
       COALESCE(t_max, t_min, 9999)            AS key_or_unknown,     -- 처음으로 NULL이 아닌 값
       NULLIF(t_min, t_max)                    AS t_min_if_range      -- 같으면 NULL(점 사건이면 NULL)
  FROM dag_node
 ORDER BY node_id;

-- 4. COUNT(*) vs COUNT(col): edge의 condition(미확정 동일성) 유무
SELECT COUNT(*)            AS n_edges,
       COUNT(condition)    AS n_conditional,
       COUNT(*) - COUNT(condition) AS n_unconditional
  FROM dag_edge;

-- 5. NULL을 포함한 문자열 연결 — Oracle에서 'A' || NULL = 'A'
SELECT edge_id,
       edge_type || ' / ' || condition           AS concat_result,    -- condition이 NULL이어도 앞부분은 남는다
       CONCAT(edge_type, condition)              AS concat_fn          -- CONCAT 함수(인자 2개)
  FROM dag_edge
 WHERE edge_id IN ('OE001', 'OE010');

-- 6. 단순 CASE: status 분류를 한국어 설명으로
SELECT edge_id,
       status,
       CASE status
           WHEN 'OBSERVED' THEN '사료에 직접 적힌 관계'
           WHEN 'DERIVED'  THEN '관측 사실에서 규칙으로 이은 관계'
           ELSE '기타'
       END AS status_ko
  FROM dag_edge
 ORDER BY edge_id;

-- 7. 검색 CASE: Super-DAG node를 OBSERVED / DERIVED / LATENT / CONTEXT / UNRESOLVED 다섯 그룹으로
SELECT node_id,
       sd_status,
       node_type,
       CASE
           WHEN sd_status = 'OBSERVED'                                THEN 'OBSERVED (고정 관측)'
           WHEN sd_status = 'CONTEXT' AND node_type = 'ENV_CONTEXT'   THEN 'CONTEXT (환경)'
           WHEN sd_status = 'CONTEXT'                                 THEN 'CONTEXT (제도)'
           WHEN sd_status = 'LATENT_MECHANISM'                        THEN 'LATENT (가설·분석 변수)'
           WHEN sd_status = 'UNRESOLVED'                              THEN 'UNRESOLVED (보존된 불확실성)'
           ELSE 'OTHER'
       END AS status_class
  FROM sd_node
 ORDER BY status_class, node_id;

-- 8. DECODE(Oracle 전용): CASE의 축약형. 등급 → 점수
SELECT candidate_id,
       overall,
       DECODE(overall, 'HIGH', 3, 'MEDIUM', 2, 'LOW', 1, 'INCOMPATIBLE', 0, -1) AS overall_score
  FROM latent_candidate
 ORDER BY overall_score DESC, candidate_id;
-- DECODE는 NULL = NULL을 '같다'고 본다(CASE WHEN col = NULL은 거짓). 차이를 기억할 것.

-- 9. CASE + 집계: 동일성 상태별 개수를 한 행에
SELECT COUNT(CASE WHEN status = 'RESOLVED'               THEN 1 END) AS n_resolved,
       COUNT(CASE WHEN status = 'UNRESOLVED'             THEN 1 END) AS n_unresolved,
       COUNT(CASE WHEN status = 'ACCEPTED_BY_PROVENANCE' THEN 1 END) AS n_accepted,
       COUNT(CASE WHEN status = 'DOCUMENTED'             THEN 1 END) AS n_documented
  FROM identity_register;

-- 10. ORDER BY의 NULL 위치: Oracle 오름차순 기본은 NULLS LAST, 내림차순 기본은 NULLS FIRST
SELECT node_id, t_min FROM dag_node ORDER BY t_min;                      -- EP08(NULL)이 맨 뒤
SELECT node_id, t_min FROM dag_node ORDER BY t_min DESC;                 -- EP08(NULL)이 맨 앞
SELECT node_id, t_min FROM dag_node ORDER BY t_min DESC NULLS LAST;      -- 명시

-- 11. 집계와 NULL: AVG는 NULL을 빼고 평균 낸다 → NVL로 0을 넣으면 값이 달라진다
SELECT AVG(t_max)          AS avg_known_only,
       AVG(NVL(t_max, 0))  AS avg_null_as_zero
  FROM dag_node;

-- 12. '' = NULL 확인 (Oracle): 결과 'empty is null'
SELECT CASE WHEN '' IS NULL THEN 'empty is null' ELSE 'empty is not null' END AS oracle_empty_string
  FROM dual;

-- 13. LNNVL(조건): 조건이 FALSE 또는 UNKNOWN이면 TRUE (Oracle). NULL을 '조건 불충족' 쪽에 포함시킬 때
SELECT node_id, t_max
  FROM dag_node
 WHERE LNNVL(t_max >= 600)          -- t_max < 600 이거나 t_max IS NULL
 ORDER BY node_id;
