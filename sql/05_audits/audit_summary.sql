-- =============================================================================
-- audit_summary.sql — SQL Audit 1–4 결과 요약과 Python Audit 결과 대조
-- -----------------------------------------------------------------------------
-- 선행: audit_1 ~ audit_4 파일(각 view 생성)
-- AUDIT 5(interactive visualization: docs/data JSON·CSS·화면 배치)는 관계형 데이터가 아니라
-- NOT PORTED TO SQL. 대조표에서는 Python 값만 보이고 SQL 값은 NULL이다.
-- =============================================================================

-- 1. 네 audit view를 하나로 (UNION ALL은 중복을 지우지 않는다 — 개수 비교에 필요)
CREATE OR REPLACE VIEW v_sql_audit_all AS
SELECT 'AUDIT1' AS audit_name, check_name, severity, target, message FROM v_sql_audit_1
UNION ALL
SELECT 'AUDIT2', check_name, severity, target, message FROM v_sql_audit_2
UNION ALL
SELECT 'AUDIT3', check_name, severity, target, message FROM v_sql_audit_3
UNION ALL
SELECT 'AUDIT4', check_name, severity, target, message FROM v_sql_audit_4;

-- 2. audit × severity 요약 (SQL) — 통과 기준: ERROR 0, WARN 0
SELECT audit_name,
       COUNT(CASE WHEN severity = 'ERROR'      THEN 1 END) AS n_error,
       COUNT(CASE WHEN severity = 'WARN'       THEN 1 END) AS n_warn,
       COUNT(CASE WHEN severity = 'UNRESOLVED' THEN 1 END) AS n_unresolved,
       COUNT(CASE WHEN severity = 'INFO'       THEN 1 END) AS n_info,
       CASE WHEN COUNT(CASE WHEN severity IN ('ERROR', 'WARN') THEN 1 END) = 0
            THEN 'PASS' ELSE 'FAIL' END                   AS verdict
  FROM v_sql_audit_all
 GROUP BY audit_name
 ORDER BY audit_name;

-- 3. Python ↔ SQL 대조 (audit × severity) — FULL OUTER JOIN: 한쪽에만 있는 조합도 남긴다
--    기대(Python): AUDIT1 UNRESOLVED 4 / INFO 13, AUDIT2 UNRESOLVED 5 / INFO 1,
--                  AUDIT3 UNRESOLVED 1 / INFO 11, AUDIT4 UNRESOLVED 20 / INFO 2, AUDIT5 INFO 5(SQL 없음)
WITH py AS (
    SELECT audit_name, severity, COUNT(*) AS n FROM py_audit_finding GROUP BY audit_name, severity
), sq AS (
    SELECT audit_name, severity, COUNT(*) AS n FROM v_sql_audit_all GROUP BY audit_name, severity
)
SELECT COALESCE(py.audit_name, sq.audit_name)     AS audit_name,
       COALESCE(py.severity, sq.severity)         AS severity,
       py.n                                       AS python_n,
       sq.n                                       AS sql_n,
       CASE WHEN COALESCE(py.audit_name, sq.audit_name) = 'AUDIT5' THEN 'NOT PORTED'
            WHEN NVL(py.n, 0) = NVL(sq.n, 0)                       THEN 'MATCH'
            ELSE 'DIFF' END                       AS comparison
  FROM py
  FULL OUTER JOIN sq
    ON sq.audit_name = py.audit_name
   AND sq.severity = py.severity
 ORDER BY 1, 2;

-- 4. 더 자세한 대조: audit × check × severity
--    DIFF 행이 있으면 그 check의 SQL 이식 범위(README §8 NOT PORTED)와 함께 본다.
WITH py AS (
    SELECT audit_name, check_name, severity, COUNT(*) AS n
      FROM py_audit_finding
     WHERE audit_name <> 'AUDIT5'
     GROUP BY audit_name, check_name, severity
), sq AS (
    SELECT audit_name, check_name, severity, COUNT(*) AS n
      FROM v_sql_audit_all
     GROUP BY audit_name, check_name, severity
)
SELECT COALESCE(py.audit_name, sq.audit_name) AS audit_name,
       COALESCE(py.check_name, sq.check_name) AS check_name,
       COALESCE(py.severity, sq.severity)     AS severity,
       NVL(py.n, 0)                           AS python_n,
       NVL(sq.n, 0)                           AS sql_n,
       CASE WHEN NVL(py.n, 0) = NVL(sq.n, 0) THEN 'MATCH' ELSE 'DIFF' END AS comparison
  FROM py
  FULL OUTER JOIN sq
    ON sq.audit_name = py.audit_name
   AND sq.check_name = py.check_name
   AND sq.severity = py.severity
 ORDER BY 1, 2, 3;

-- 5. UNRESOLVED 대상 자체가 같은가 (target 단위 대칭 차집합) — 기대: 0행
--    개수만 같고 대상이 다르면 여기서 드러난다.
(SELECT audit_name, check_name, target FROM py_audit_finding WHERE severity = 'UNRESOLVED'
 MINUS
 SELECT audit_name, check_name, target FROM v_sql_audit_all WHERE severity = 'UNRESOLVED')
UNION ALL
(SELECT audit_name, check_name, target FROM v_sql_audit_all WHERE severity = 'UNRESOLVED'
 MINUS
 SELECT audit_name, check_name, target FROM py_audit_finding WHERE severity = 'UNRESOLVED');

-- 6. ERROR·WARN 상세 (있을 때만 행이 나온다) — 기대: 0행
SELECT audit_name, check_name, severity, target, message
  FROM v_sql_audit_all
 WHERE severity IN ('ERROR', 'WARN')
 ORDER BY audit_name, check_name, target;
