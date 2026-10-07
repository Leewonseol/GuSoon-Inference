-- =============================================================================
-- 07_sqld_drills / 09_comprehensive.sql — 종합 (어려움)
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q34. [어려움] world 쌍마다 '선택이 다른 gap 수'를 구하고, 가장 비슷한(차이가 가장 작은) 쌍을 찾으시오.
--      gap을 비워 둔 것(후보 없음)도 하나의 선택으로 본다. (Audit 3 규칙: 모든 쌍이 2개 이상 달라야 함)
-- 힌트: world × gap 격자(CROSS JOIN + LEFT JOIN) → 격자 자기 조인(a.world_id < b.world_id) → NVL로 NULL 비교.
-- 정답 SQL:
WITH grid AS (
    SELECT w.world_id, g.gap_id, wc.candidate_id
      FROM narrative_world w
     CROSS JOIN gap g
      LEFT JOIN world_candidate wc
             ON wc.world_id = w.world_id
            AND wc.gap_id = g.gap_id
),
pair_diff AS (
    SELECT a.world_id AS world_a,
           b.world_id AS world_b,
           SUM(CASE WHEN NVL(a.candidate_id, '-') <> NVL(b.candidate_id, '-') THEN 1 ELSE 0 END) AS n_diff
      FROM grid a
      JOIN grid b ON b.gap_id = a.gap_id AND a.world_id < b.world_id
     GROUP BY a.world_id, b.world_id
)
SELECT world_a, world_b, n_diff
  FROM pair_diff
 WHERE n_diff = (SELECT MIN(n_diff) FROM pair_diff)
 ORDER BY world_a, world_b;
-- 왜 맞는가: 비교하려면 두 world가 같은 gap 줄에 나란히 있어야 한다. 빈 gap은 LEFT JOIN으로 NULL이 되고,
--   NULL <> NULL은 UNKNOWN이라 NVL로 같은 표시('-')를 넣어야 '둘 다 비움 = 같음'이 된다.
-- 자주 틀리는 포인트: a.world_id <> b.world_id로 조인하면 (W1,W2)와 (W2,W1)이 둘 다 나온다(중복 쌍).
-- 기대 결과: (W3, W5) 5, (W5, W6) 5 — 최소 차이도 5라 Audit 3 기준(≥ 2)을 넉넉히 통과


-- -----------------------------------------------------------------------------
-- Q35. [어려움] 경쟁 설명 world에서 메커니즘 configuration이 OFF 또는 UNSPECIFIED인데 그 메커니즘을
--      주(PRIMARY) 메커니즘으로 하는 후보를 world가 쓰고 있는 모순을 찾으시오(관측 고정 M5는 예외).
-- 정답 SQL:
SELECT cfg.world_id, cfg.mechanism_id, cfg.config_value,
       LISTAGG(wc.candidate_id, ',') WITHIN GROUP (ORDER BY wc.candidate_id) AS conflicting_bridges
  FROM world_mechanism_config cfg
  JOIN narrative_world w      ON w.world_id = cfg.world_id
                             AND w.status = 'COMPETING_EXPLANATION'
  JOIN world_candidate wc     ON wc.world_id = cfg.world_id
  JOIN candidate_mechanism cm ON cm.candidate_id = wc.candidate_id
                             AND cm.mapping_role = 'PRIMARY'
                             AND cm.mechanism_id = cfg.mechanism_id
 WHERE cfg.config_value IN ('OFF', 'UNSPECIFIED')
   AND cfg.mechanism_id NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'OBSERVED_ANCHORED')
 GROUP BY cfg.world_id, cfg.mechanism_id, cfg.config_value;
-- 왜 맞는가: 'UNSPECIFIED/OFF인데 관련 후보가 살아 있다'는 configuration 계산 규칙 위반(Audit 4)이다.
-- 자주 틀리는 포인트: UNSPECIFIED를 OFF와 같다고 보면 안 된다(UNSPECIFIED = 작동 여부를 말하지 않음).
--   이 질의는 둘 다 '주 후보가 있으면 안 됨'이라는 공통 조건만 본다.
-- 기대 결과: 0행


-- -----------------------------------------------------------------------------
-- Q36. [어려움] OR/XOR 구조 변수 중, 그 변수의 gap을 채울 수 있는 '쓸 수 있는' 후보들의 주 메커니즘이
--      변수 입력(inputs)에 2개 이상 들어 있는 변수를 찾으시오(= 같은 관측 전이를 여러 메커니즘이 설명).
--      쓸 수 있는 후보 = overall ≠ INCOMPATIBLE, contradiction_risk ≠ HIGH, null 변형(NULL_VARIANT) 아님.
-- 정답 SQL:
WITH rule_gap AS (                                   -- structural_rule.gap('G03|G04')을 행으로 편다
    SELECT r.var_id, r.op, r.target, r.inputs,
           REGEXP_SUBSTR(r.gap, '[^|]+', 1, seq.n) AS gap_id
      FROM structural_rule r
      JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 10) seq
        ON seq.n <= REGEXP_COUNT(r.gap, '[^|]+')
     WHERE r.op IN ('OR', 'XOR')
),
usable AS (
    SELECT c.candidate_id, c.gap_id, cm.mechanism_id
      FROM latent_candidate c
      JOIN candidate_mechanism cm ON cm.candidate_id = c.candidate_id AND cm.mapping_role = 'PRIMARY'
     WHERE c.overall <> 'INCOMPATIBLE'
       AND c.contradiction_risk <> 'HIGH'
       AND c.candidate_id NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'NULL_VARIANT')
)
SELECT rg.var_id, rg.op, rg.target,
       COUNT(DISTINCT u.mechanism_id) AS n_mechanisms
  FROM rule_gap rg
  JOIN usable u
    ON u.gap_id = rg.gap_id
   AND '|' || rg.inputs || '|' LIKE '%|' || u.mechanism_id || '|%'    -- 목록 안의 정확한 원소 검색
 GROUP BY rg.var_id, rg.op, rg.target
HAVING COUNT(DISTINCT u.mechanism_id) >= 2
 ORDER BY rg.var_id;
-- 왜 맞는가: '|' 목록을 행으로 편 뒤(정규화), 경계 문자 '|'를 양쪽에 붙여 LIKE로 정확히 비교한다
--   ('M1'이 'M10'에 잘못 걸리는 것 방지).
-- 자주 틀리는 포인트: INSTR(inputs, mechanism_id) > 0은 부분 문자열도 맞다고 본다.
-- 기대 결과: V_COMMAND_SOURCE(2), V_INFO_TO_COMMANDER(4), V_INITIAL_JUDGMENT_BASIS(2), V_INVESTIGATION_SCOPE(2)
--            = Python Audit 4 multiple_explanations UNRESOLVED 4건


-- -----------------------------------------------------------------------------
-- Q37. [어려움] Python Audit 결과(py_audit_finding)와 SQL Audit 결과(v_sql_audit_all)를 audit × severity로 맞대어
--      한쪽에만 있거나 개수가 다른 조합을 찾으시오. Audit 5는 SQL로 옮기지 않았으므로 제외.
--      (05_audits/*.sql 실행 뒤)
-- 정답 SQL:
SELECT COALESCE(p.audit_name, s.audit_name) AS audit_name,
       COALESCE(p.severity, s.severity)     AS severity,
       NVL(p.n, 0)                          AS python_n,
       NVL(s.n, 0)                          AS sql_n
  FROM (SELECT audit_name, severity, COUNT(*) AS n
          FROM py_audit_finding
         WHERE audit_name <> 'AUDIT5'
         GROUP BY audit_name, severity) p
  FULL OUTER JOIN
       (SELECT audit_name, severity, COUNT(*) AS n
          FROM v_sql_audit_all
         GROUP BY audit_name, severity) s
    ON s.audit_name = p.audit_name
   AND s.severity = p.severity
 WHERE NVL(p.n, 0) <> NVL(s.n, 0);
-- 왜 맞는가: FULL OUTER JOIN은 양쪽의 짝 없는 행을 모두 남긴다. NVL(…, 0)로 '없음'을 0개로 바꿔 비교한다.
-- 자주 틀리는 포인트: WHERE p.n <> s.n만 쓰면 한쪽이 NULL인 행(한쪽에만 있는 조합)이 UNKNOWN으로 빠진다.
-- 기대 결과: 0행 (Audit 1–4: ERROR 0 / WARN 0 / UNRESOLVED 4·5·1·20 / INFO 13·1·11·2가 양쪽에서 같음)
