-- =============================================================================
-- audit_1_episode_fidelity.sql — AUDIT 1: episode가 확정 사실(01)을 충실히 옮겼는가
-- -----------------------------------------------------------------------------
-- 원본 Python: scripts/gusun_clean/audits.py audit1()
-- Python 코드를 문자열 번역하지 않고, 같은 '검사 의미'를 관계 연산(EXISTS/NOT EXISTS/
-- GROUP BY/HAVING/정규식)으로 다시 세웠다. 결과 형식은 Python과 같다:
--     (check_name, severity, target, message)   severity = ERROR | WARN | UNRESOLVED | INFO
-- 통과 기준(Python과 같음): ERROR 0, WARN 0.
-- Python Audit 1 결과(py_audit_finding): ERROR 0 / WARN 0 / UNRESOLVED 4 / INFO 13
--
-- NOT PORTED TO SQL (sql/README.md §8에 이유)
--   * semantic_weakening '원문 어휘 보존율'(토큰화·어간 1글자 절단 비율 계산)
--   * omission '절 분할 후 남은 원문' 계산(절마다 REPLACE를 반복하는 문자열 대수) — 절 분할 INFO만 옮김
-- =============================================================================

CREATE OR REPLACE VIEW v_sql_audit_1 AS
-- -----------------------------------------------------------------------------
-- A1-01 unsupported_episode
--   목적: 사건 episode는 확정 사실 1개 이상에서만 만든다.
--   정상: 0행 / 오류: 구성 fact가 없는 episode의 node_id
-- -----------------------------------------------------------------------------
SELECT 'unsupported_episode' AS check_name, 'ERROR' AS severity, n.node_id AS target,
       '구성 confirmed fact 없음' AS message
  FROM dag_node n
 WHERE n.layer <> 'ENVIRONMENT'
   AND NOT EXISTS (SELECT 1 FROM episode_member em WHERE em.episode_id = n.node_id)
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-02 omission
--   목적: 확정 사실 50개가 모두 어느 episode엔가 들어가야 한다(누락 금지). anti-join.
--   정상: 0행 / 오류: 빠진 fact_id
-- -----------------------------------------------------------------------------
SELECT 'omission', 'ERROR', cf.fact_id, '어느 episode에도 속하지 않음'
  FROM confirmed_fact cf
 WHERE NOT EXISTS (SELECT 1 FROM episode_member em WHERE em.fact_id = cf.fact_id)
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-03 clause_fidelity
--   목적: 절 분할(CF040·CF045)의 절은 원문 문장의 부분 문자열이어야 한다.
--   정상: 0행 / 오류: 원문에 없는 절을 가진 episode
-- -----------------------------------------------------------------------------
SELECT 'clause_fidelity', 'ERROR', em.episode_id,
       em.fact_id || ' 절이 원문 substring이 아님: ' || em.clause
  FROM episode_member em
  JOIN confirmed_fact cf ON cf.fact_id = em.fact_id
 WHERE em.clause IS NOT NULL
   AND INSTR(cf.confirmed_statement, em.clause) = 0
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-04 clause_split (INFO)
--   목적: 문장 전체가 아니라 절로만 쓰인 fact를 보고한다. COUNT(*)와 COUNT(clause)의 차이 이용
--         (COUNT(컬럼)은 NULL을 세지 않는다).
--   기대: INFO 2행 (CF040, CF045)
-- -----------------------------------------------------------------------------
SELECT 'clause_split', 'INFO', em.fact_id,
       COUNT(*) || '개 절로 분할'
  FROM episode_member em
 GROUP BY em.fact_id
HAVING COUNT(em.clause) = COUNT(*)
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-05 duplicate_membership (WARN)
--   목적: 같은 fact를 '문장 전체'와 '절'로 동시에 쓰면 이중 반영이다.
--   정상: 0행 / 오류: 해당 fact_id
-- -----------------------------------------------------------------------------
SELECT 'duplicate_membership', 'WARN', em.fact_id, '전체와 절이 동시에 쓰임'
  FROM episode_member em
 GROUP BY em.fact_id
HAVING COUNT(*) > 1
   AND COUNT(em.clause) < COUNT(*)
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-06 provenance
--   목적: 확정 사실의 출처(04)와 audit 명제(05)가 실제로 있어야 한다.
--         FK가 이미 막지만, FK를 DISABLE한 채 적재했을 때도 잡도록 anti-join으로 다시 본다.
--   정상: 0행 / 오류: 출처가 없는 fact_id
-- -----------------------------------------------------------------------------
SELECT 'provenance', 'ERROR', cf.fact_id, 'source_record_id가 04에 없음'
  FROM confirmed_fact cf
 WHERE NOT EXISTS (SELECT 1 FROM source_record sr WHERE sr.source_record_id = cf.source_record_id)
UNION ALL
SELECT 'provenance', 'ERROR', fp.fact_id, 'source_prop ' || fp.prop_id || '가 05에 없음'
  FROM fact_proposition fp
 WHERE NOT EXISTS (SELECT 1 FROM audit_proposition p WHERE p.prop_id = fp.prop_id)
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-07 over_merge (사료)
--   목적: 한 episode는 사료 기사 1건에서만 만든다.
--   정상: 0행 / 오류: 사료가 2건 이상 섞인 episode
-- -----------------------------------------------------------------------------
SELECT 'over_merge', 'ERROR', t.episode_id, '서로 다른 source record 병합: ' || t.n_sources || '건'
  FROM v_episode_text t
 WHERE t.n_sources > 1
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-08 over_merge (인식 계열)
--   목적: 진술·공식 보고·국왕 판단 같은 인식 계열을 한 episode에 섞지 않는다.
--         허용된 조합은 rule_set_member 'ALLOWED_FAMILY_MIX' = {TESTIMONY, IDENT} 하나뿐.
--         "계열 집합 = 허용 집합" 판정: 계열 수 = 허용 집합에 속하는 계열 수 = 허용 집합 크기
--   정상: ERROR 0행, 허용 혼합은 INFO (기대: INFO 1행, EP09)
-- -----------------------------------------------------------------------------
SELECT 'over_merge',
       CASE WHEN f.n_fam = f.n_in_mix
             AND f.n_in_mix = (SELECT COUNT(*) FROM rule_set_member WHERE rule_set = 'ALLOWED_FAMILY_MIX')
            THEN 'INFO' ELSE 'ERROR' END,
       f.episode_id,
       CASE WHEN f.n_fam = f.n_in_mix
             AND f.n_in_mix = (SELECT COUNT(*) FROM rule_set_member WHERE rule_set = 'ALLOWED_FAMILY_MIX')
            THEN '허용된 혼합 ' ELSE '인식 계열 혼합 ' END || f.families
  FROM (SELECT d.episode_id,
               COUNT(*)        AS n_fam,
               SUM(d.in_mix)   AS n_in_mix,
               LISTAGG(d.clause_family, ',') WITHIN GROUP (ORDER BY d.clause_family) AS families
          FROM (SELECT DISTINCT                                     -- 먼저 (episode, 계열) 중복 제거
                       m.episode_id,
                       m.clause_family,
                       CASE WHEN r.member_id IS NULL THEN 0 ELSE 1 END AS in_mix
                  FROM v_member_text m
                  LEFT JOIN rule_set_member r
                         ON r.rule_set = 'ALLOWED_FAMILY_MIX'
                        AND r.member_id = m.clause_family) d
         GROUP BY d.episode_id) f
 WHERE f.n_fam > 1
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-09 over_merge (진술자)
--   목적: 서로 다른 사람의 진술을 한 episode로 합치지 않는다.
--         진술자 = 문장 첫 주어(정규식 ^(\S+?)[은는]\s). 주어를 못 찾으면 '<NONE>'(Python None과 같게 셈)
--   정상: 0행 / 오류: 진술자가 2명 이상인 episode
-- -----------------------------------------------------------------------------
SELECT 'over_merge', 'ERROR', m.episode_id, '서로 다른 진술자 병합: ' || COUNT(DISTINCT NVL(m.testifier, '<NONE>')) || '명'
  FROM v_member_text m
 WHERE m.fact_family = 'TESTIMONY'
 GROUP BY m.episode_id
HAVING COUNT(DISTINCT NVL(m.testifier, '<NONE>')) > 1
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-10 order_execution_conflation
--   목적: 체포 지시(ARREST_ORDER)와 체포 실행(APPREHENSION)을 한 episode로 합치지 않는다.
--   정상: 0행 / 오류: 두 범주를 함께 가진 episode
-- -----------------------------------------------------------------------------
SELECT 'order_execution_conflation', 'ERROR', m.episode_id, '지시와 체포 실행을 한 episode로 병합'
  FROM v_member_text m
 GROUP BY m.episode_id
HAVING COUNT(CASE WHEN m.fact_category = 'ARREST_ORDER' THEN 1 END) > 0
   AND COUNT(CASE WHEN m.fact_category = 'APPREHENSION' THEN 1 END) > 0
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-11 semantic_strengthening / semantic_weakening (어휘 목록)
--   목적: 원문에 없는 강한 표현(STRONG_TERM)이 summary에 생기거나,
--         원문의 한정 표현(HEDGE_TERM)이 summary에서 사라지면 안 된다.
--   정상: 0행 / 오류: (episode, 어휘)
-- -----------------------------------------------------------------------------
SELECT 'semantic_strengthening', 'ERROR', t.episode_id, '원문에 없는 강한 표현 ''' || r.member_id || ''''
  FROM v_episode_text t
  JOIN rule_set_member r ON r.rule_set = 'STRONG_TERM'
 WHERE INSTR(t.summary, r.member_id) > 0
   AND NVL(INSTR(t.joined_text, r.member_id), 0) = 0
UNION ALL
SELECT 'semantic_weakening', 'ERROR', t.episode_id, '원문의 한정 표현 ''' || r.member_id || '''가 summary에서 사라짐'
  FROM v_episode_text t
  JOIN rule_set_member r ON r.rule_set = 'HEDGE_TERM'
 WHERE INSTR(t.joined_text, r.member_id) > 0
   AND INSTR(t.summary, r.member_id) = 0
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-12 epistemic_collapse / testimony_to_fact
--   목적: 진술 기반 episode를 공식 사실처럼 올리지 않는다(layer와 인식 하한 floor의 정합).
--         ref_confirmation_level.epistemic_rank: 0 중첩 진술, 1 진술, 2 보고·평가, 3 판단, 4 행위
--   정상: 0행 / 오류: 규칙을 어긴 episode
-- -----------------------------------------------------------------------------
SELECT 'epistemic_collapse', 'ERROR', t.episode_id, '진술 기반 episode인데 layer=' || t.layer
  FROM v_episode_text t
 WHERE t.floor_rank <= 1
   AND t.layer NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'TESTIMONY_LAYER')
UNION ALL
SELECT 'epistemic_collapse', 'ERROR', t.episode_id, '중첩 진술 포함인데 NESTED_TESTIMONY가 아님'
  FROM v_episode_text t
 WHERE t.floor_rank = 0
   AND t.layer <> 'NESTED_TESTIMONY'
UNION ALL
SELECT 'testimony_to_fact', 'ERROR', t.episode_id, '진술 episode의 summary에 진술 귀속 표현이 없음'
  FROM v_episode_text t
 WHERE t.layer IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'TESTIMONY_LAYER')
   AND NOT REGEXP_LIKE(t.summary, (SELECT oracle_regex FROM rule_text_pattern WHERE pattern_id = 'TESTIMONY_ATTRIBUTION'))
UNION ALL
SELECT 'epistemic_collapse', 'ERROR', t.episode_id, '공식 기록 episode의 summary에 기록 행위 표현이 없음'
  FROM v_episode_text t
 WHERE t.layer NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'TESTIMONY_LAYER')
   AND NOT REGEXP_LIKE(t.summary, (SELECT oracle_regex FROM rule_text_pattern WHERE pattern_id = 'OFFICIAL_RECORD_ACT'))
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-13 temporal_conflation
--   목적: 발생일이 다른 문장을 한 episode로 합치지 않고, 구성 문장의 발생일은 episode 시간 구간 안에 있어야 한다.
--         발생일 = occurrence_lunar_text의 '1793-MM-DD'(없으면 NULL → 검사 제외. 날짜를 만들지 않는다)
--   정상: 0행 / 오류: 발생일 폭이 1일 넘게 벌어진 episode, 구간 밖 member가 있는 episode
-- -----------------------------------------------------------------------------
SELECT 'temporal_conflation', 'ERROR', m.episode_id,
       '발생일이 다른 문장 병합: ' || MIN(m.occurrence_md) || '~' || MAX(m.occurrence_md)
  FROM v_member_text m
 GROUP BY m.episode_id
HAVING MAX(m.occurrence_md) - MIN(m.occurrence_md) > 1
UNION ALL
SELECT DISTINCT 'temporal_conflation', 'ERROR', m.episode_id,
       'member 날짜 ' || m.occurrence_md || '가 episode 범위 밖'
  FROM v_member_text m
  JOIN dag_node n ON n.node_id = m.episode_id
 WHERE m.occurrence_md IS NOT NULL
   AND (   (n.t_min IS NOT NULL AND m.occurrence_md < n.t_min)
        OR (n.t_max IS NOT NULL AND m.occurrence_md > n.t_max))
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-14 identity_forcing / surface_form_substitution
--   목적: 원문 표면형(예: '병사')을 summary에서 다른 이름(예: '이광섭')으로 바꾸지 않는다.
--         사용자 확정(RESOLVED) 동일성이어도 episode summary는 원문 표면형을 유지한다.
--         또 원문에 없는 인물 이름을 summary에 넣지 않는다.
--   정상: 0행 / 오류: (episode, 치환·삽입된 이름)
-- -----------------------------------------------------------------------------
SELECT CASE WHEN ir.status = 'RESOLVED' THEN 'surface_form_substitution' ELSE 'identity_forcing' END,
       'ERROR', t.episode_id,
       '''' || rs.surface_form || '''를 ''' || rs.resolved_name || '''로 치환(' || rs.identity_id || ')'
  FROM v_episode_text t
  JOIN rule_identity_surface rs ON INSTR(t.joined_text, rs.surface_form) > 0
  JOIN identity_register ir     ON ir.identity_id = rs.identity_id
 WHERE INSTR(t.summary, rs.resolved_name) > 0
   AND INSTR(t.joined_text, rs.resolved_name) = 0
UNION ALL
SELECT 'identity_forcing', 'ERROR', t.episode_id, '원문에 없는 인물 ''' || r.member_id || ''' 삽입'
  FROM v_episode_text t
  JOIN rule_set_member r ON r.rule_set = 'PERSON_NAME'
 WHERE INSTR(t.summary, r.member_id) > 0
   AND INSTR(t.joined_text, r.member_id) = 0
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-15 epistemic_marker_deletion
--   목적: 원문의 인식 표지('진술했', '보고했', '판단했' …) 개수가 summary에서 줄면 안 된다.
--         표지 13종 × episode를 JOIN해서 REGEXP_COUNT로 비교한다.
--   정상: 0행 / 오류: (episode, 표지, 원문 개수 → summary 개수)
-- -----------------------------------------------------------------------------
SELECT 'epistemic_marker_deletion', 'ERROR', t.episode_id,
       '''' || SUBSTR(p.pattern_id, 8) || ''' 표지 원문 ' || REGEXP_COUNT(t.joined_text, p.oracle_regex)
       || '회 → summary ' || REGEXP_COUNT(t.summary, p.oracle_regex) || '회'
  FROM v_episode_text t
  JOIN rule_text_pattern p ON p.check_name = 'epistemic_marker_deletion'
 WHERE REGEXP_COUNT(t.summary, p.oracle_regex) < REGEXP_COUNT(t.joined_text, p.oracle_regex)
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-16 testimony_to_fact (개수)
--   목적: 진술 member마다 summary에 '진술했'이 하나씩 남아야 한다(진술을 사실로 바꾸지 않음).
--   정상: 0행 / 오류: 진술 member 수 > summary의 '진술했' 수
-- -----------------------------------------------------------------------------
SELECT 'testimony_to_fact', 'ERROR', t.episode_id,
       '진술 member ' || t.n_testimony_members || '개인데 summary의 ''진술했'' '
       || REGEXP_COUNT(t.summary, '진술했') || '회'
  FROM v_episode_text t
 WHERE t.n_testimony_members > 0
   AND REGEXP_COUNT(t.summary, '진술했') < t.n_testimony_members
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-17 actor_substitution
--   목적: 각 member의 진술·기록 주체가 summary에 남고, '자신'이 다른 인물로 바뀌지 않으며,
--         summary의 첫 주어가 첫 member의 주체와 같아야 한다.
--   정상: 0행 / 오류: 주체가 사라지거나 바뀐 episode
-- -----------------------------------------------------------------------------
SELECT 'actor_substitution', 'ERROR', m.episode_id, m.fact_id || ' 주체 ''' || m.testifier || '''가 summary에 없음'
  FROM v_member_text m
  JOIN dag_node n ON n.node_id = m.episode_id
 WHERE m.testifier IS NOT NULL
   AND m.testifier <> '해당'
   AND INSTR(n.summary, m.testifier) = 0
UNION ALL
SELECT 'actor_substitution', 'ERROR', m.episode_id, m.fact_id || '의 ''자신''이 summary에서 치환됨'
  FROM v_member_text m
  JOIN dag_node n ON n.node_id = m.episode_id
 WHERE INSTR(m.member_text, '자신') > 0
   AND INSTR(n.summary, '자신') = 0
UNION ALL
SELECT 'actor_substitution', 'ERROR', m.episode_id,
       'summary 첫 주어 ''' || REGEXP_SUBSTR(n.summary, '^(\S+?)[은는]\s', 1, 1, NULL, 1)
       || ''' ≠ 원문 주체 ''' || m.testifier || ''''
  FROM v_member_text m
  JOIN dag_node n ON n.node_id = m.episode_id
 WHERE m.member_seq = 1
   AND m.testifier IS NOT NULL
   AND NVL(REGEXP_SUBSTR(n.summary, '^(\S+?)[은는]\s', 1, 1, NULL, 1), '<NONE>') <> m.testifier
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-18 occurrence_record_confusion
--   목적: 기록일(사료 날짜)을 발생 시점(t_min)으로 쓰지 않는다. t_min이 기록일과 같으면
--         원문 시점 서술(chronology·occurrence)에 그 날짜가 있거나 '공초'(공초일)여야 한다.
--   정상: 0행 / 오류: 기록일을 발생일로 쓴 episode
-- -----------------------------------------------------------------------------
SELECT DISTINCT 'occurrence_record_confusion', 'ERROR', t.episode_id,
       '기록일 ' || m.record_lunar_date || '을 발생 시점으로 사용'
  FROM v_episode_text t
  JOIN v_member_text m ON m.episode_id = t.episode_id
 WHERE t.t_min = m.record_md
   AND INSTR(t.chron_text, m.record_lunar_date) = 0
   AND INSTR(t.chron_text, '공초') = 0
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-19 responsibility_to_causation / environment_to_individual_fact
--   목적: 책임 판단을 직접 사인으로, 환경 context를 개인 사실로 단정하는 서술 금지.
--         정규식에 걸린 구절이 원문(joined_text)에도 그대로 있으면 원문 인용이므로 제외.
--   정상: 0행 / 오류: (episode, 걸린 구절)
-- -----------------------------------------------------------------------------
SELECT h.check_name, 'ERROR', h.episode_id, '''' || h.fragment || ''''
  FROM (SELECT p.check_name, t.episode_id, t.joined_text,
               REGEXP_SUBSTR(t.summary || ' ' || t.caution, p.oracle_regex) AS fragment
          FROM v_episode_text t
          JOIN rule_text_pattern p
            ON p.check_name IN ('responsibility_to_causation', 'environment_to_individual_fact')) h
 WHERE h.fragment IS NOT NULL
   AND NVL(INSTR(h.joined_text, h.fragment), 0) = 0
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-20 closed_set
--   목적: 원문의 열린 목록('… 등')을 닫힌 목록으로 바꾸지 않는다.
--         (1) '등' 표지 개수 보존. Python 정규식 (?<=\S) 등(?=[\s을의에이과은는]|$)에는 전후방 탐색이 있어
--             Oracle에서는 앞 글자·뒤 글자를 소비하는 \S 등([[:space:]을의에이과은는]|$)로 근사했다.
--         (2) 05 명제가 OPEN_SET이면 summary에 '등' 또는 '들'이 있어야 한다.
--   정상: 0행 / 오류: 열린 목록 표지가 사라진 episode
-- -----------------------------------------------------------------------------
SELECT 'closed_set', 'ERROR', t.episode_id,
       '''등'' ' || REGEXP_COUNT(t.joined_text, '\S 등([[:space:]을의에이과은는]|$)') || '회 → summary '
       || REGEXP_COUNT(t.summary, '\S 등([[:space:]을의에이과은는]|$)') || '회'
  FROM v_episode_text t
 WHERE REGEXP_COUNT(t.summary, '\S 등([[:space:]을의에이과은는]|$)')
     < REGEXP_COUNT(t.joined_text, '\S 등([[:space:]을의에이과은는]|$)')
UNION ALL
SELECT DISTINCT 'closed_set', 'ERROR', m.episode_id,
       fp.prop_id || ' set_status=' || p.set_status || '인데 열린 집합 표지가 없음'
  FROM v_member_text m
  JOIN fact_proposition fp  ON fp.fact_id = m.fact_id
  JOIN audit_proposition p  ON p.prop_id = fp.prop_id
  JOIN dag_node n           ON n.node_id = m.episode_id
 WHERE p.set_status LIKE 'OPEN\_SET%' ESCAPE '\'
   AND INSTR(n.summary, '등') = 0
   AND INSTR(n.summary, '들') = 0
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-21 clause_prop_alignment
--   목적: 절 분할한 절의 주어(첫 '은/는' 앞)가 05 명제의 보고자(reporting_actor)와 맞아야 한다.
--   정상: ERROR 0행, 맞는 짝은 INFO (기대: INFO 4행)
-- -----------------------------------------------------------------------------
SELECT 'clause_prop_alignment',
       CASE WHEN COUNT(p.prop_id) = 0 THEN 'ERROR' ELSE 'INFO' END,
       c.episode_id,
       c.fact_id || CASE WHEN COUNT(p.prop_id) = 0
                         THEN ' 절 주체 ' || c.actor || '와 맞는 prop 없음'
                         ELSE ' 절 → ' || LISTAGG(p.prop_id, ',') WITHIN GROUP (ORDER BY p.prop_id) END
  FROM (SELECT em.episode_id, em.fact_id, REGEXP_SUBSTR(em.clause, '^[^은는]*') AS actor
          FROM episode_member em
         WHERE em.clause IS NOT NULL) c
  LEFT JOIN fact_proposition fp ON fp.fact_id = c.fact_id
  LEFT JOIN audit_proposition p ON p.prop_id = fp.prop_id
                               AND p.reporting_actor = c.actor
 GROUP BY c.episode_id, c.fact_id, c.actor
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-22 identity_resolution / resolved_identity / unresolved_identity
--   목적: 동일성은 사용자 확정(RESOLVED + USER + 근거)이거나 UNRESOLVED로 보존한다.
--         UNRESOLVED는 오류가 아니라 '사료가 결정하지 않는 것'을 보존한 결과다.
--   기대: ERROR 0, INFO 5(ID01·02·03·05·11), UNRESOLVED 4(ID04·06·07·08)
-- -----------------------------------------------------------------------------
SELECT CASE WHEN ir.resolved_by = 'USER' AND ir.resolution_basis IS NOT NULL
            THEN 'resolved_identity' ELSE 'identity_resolution' END,
       CASE WHEN ir.resolved_by = 'USER' AND ir.resolution_basis IS NOT NULL
            THEN 'INFO' ELSE 'ERROR' END,
       ir.identity_id,
       ir.surface_a || ' = ' || ir.surface_b
  FROM identity_register ir
 WHERE ir.status = 'RESOLVED'
UNION ALL
SELECT 'unresolved_identity', 'UNRESOLVED', ir.identity_id,
       ir.surface_a || ' ↔ ' || ir.surface_b || ' · unresolved_reason: ' || ir.unresolved_reason
  FROM identity_register ir
 WHERE ir.status = 'UNRESOLVED'
UNION ALL
-- -----------------------------------------------------------------------------
-- A1-23 outside_confirmed_set (INFO)
--   목적: 확정 사실이 참조하지 않는 05 명제 수를 보고(DAG node로 쓰지 않음).
--   기대: INFO 1행
-- -----------------------------------------------------------------------------
SELECT 'outside_confirmed_set', 'INFO', '05',
       'CF가 참조하지 않는 prop ' || COUNT(*) || '개 — DAG node로 쓰지 않음'
  FROM audit_proposition p
 WHERE NOT EXISTS (SELECT 1 FROM fact_proposition fp WHERE fp.prop_id = p.prop_id);


-- 실행 예 ------------------------------------------------------------------------
-- 전체: 심각도 순
SELECT check_name, severity, target, message
  FROM v_sql_audit_1
 ORDER BY DECODE(severity, 'ERROR', 1, 'WARN', 2, 'UNRESOLVED', 3, 4), check_name, target;

-- 심각도별 개수 — 기대: UNRESOLVED 4, INFO 13 (ERROR·WARN 없음)
SELECT severity, COUNT(*) AS n
  FROM v_sql_audit_1
 GROUP BY severity
 ORDER BY severity;
