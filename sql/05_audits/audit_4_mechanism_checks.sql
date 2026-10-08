-- =============================================================================
-- audit_4_mechanism_checks.sql — AUDIT 4: mechanism Super-DAG(질적 SCM) 검사
-- -----------------------------------------------------------------------------
-- 원본 Python: scripts/gusun_clean/audits.py audit4()
-- 결과 형식: (check_name, severity, target, message)
-- Python Audit 4 결과: ERROR 0 / WARN 0 / UNRESOLVED 20 / INFO 2
--   UNRESOLVED 20 = interaction_direction 8 + coexistence_undetermined 2 + multiple_explanations 4 + unresolved_item 6
--
-- NOT PORTED TO SQL
--   * frozen_graph_changed의 sha256 재계산(Audit 3과 같은 이유). 대신 frozen node·edge 집합을 MINUS로 대조한다.
--   * world configuration 값의 재계산(stage6_mechanisms.world_config): 후보의 core/보조 구분(CAND_MAP 3열)과
--     메커니즘별 key gap은 CSV로 내보내지 않았다. 계산 결과(world_mechanism_config)가 규칙과 모순되지 않는지만 본다.
-- =============================================================================

CREATE OR REPLACE VIEW v_sql_audit_4 AS
-- -----------------------------------------------------------------------------
-- A4-01 frozen node 보존 (observed_to_latent / frozen_graph_changed)
--   목적: 동결 node 41개가 Super-DAG에 그대로 있어야 한다. 환경 node는 CONTEXT, 사건 node는 OBSERVED,
--         label = 동결 title.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT CASE WHEN s.node_id IS NULL THEN 'frozen_graph_changed' ELSE 'observed_to_latent' END AS check_name,
       'ERROR' AS severity, n.node_id AS target,
       CASE WHEN s.node_id IS NULL THEN 'frozen node가 Super-DAG에 없음'
            ELSE 'frozen node 상태·내용 변경: ' || s.sd_status END AS message
  FROM dag_node n
  LEFT JOIN sd_node s ON s.node_id = n.node_id
 WHERE s.node_id IS NULL
    OR s.sd_status <> CASE WHEN n.layer = 'ENVIRONMENT' THEN 'CONTEXT' ELSE 'OBSERVED' END
    OR s.label <> n.title
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-02 context_to_fact (새 관측 사건 생성 금지)
--   목적: 동결 graph에 없는 OBSERVED·OBSERVED_EVENT node가 Super-DAG에서 새로 생기면 안 된다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'context_to_fact', 'ERROR', s.node_id, 'frozen graph에 없는 관측 사건 node가 Super-DAG에서 새로 생김'
  FROM sd_node s
 WHERE (s.sd_status = 'OBSERVED' OR s.node_type = 'OBSERVED_EVENT')
   AND NOT EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = s.node_id)
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-03 frozen edge 집합 대조 (MINUS 양방향 = 대칭 차집합)
--   목적: Super-DAG의 FROZEN edge(id·끝점·type·상태)가 동결 edge와 정확히 같아야 한다.
--   정상: 0행 / 오류: 한쪽에만 있는 edge 수
-- -----------------------------------------------------------------------------
SELECT 'frozen_graph_changed', 'ERROR', 'edges', 'frozen edge 불일치 ' || COUNT(*) || '건'
  FROM ((SELECT edge_id, src, dst, edge_type, status FROM dag_edge
         MINUS
         SELECT edge_id, src, dst, edge_type, sd_status FROM sd_edge WHERE origin = 'FROZEN')
        UNION ALL
        (SELECT edge_id, src, dst, edge_type, sd_status FROM sd_edge WHERE origin = 'FROZEN'
         MINUS
         SELECT edge_id, src, dst, edge_type, status FROM dag_edge))
HAVING COUNT(*) > 0
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-04 latent_to_observed / world_latent_promoted
--   목적: 메커니즘·구조 변수·후보 node는 LATENT_MECHANISM이어야 하고,
--         world별 후보가 '모든 world 공통(ALL)'으로 표시되면 안 된다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'latent_to_observed', 'ERROR', s.node_id, s.node_type || '인데 status=' || s.sd_status
  FROM sd_node s
 WHERE s.node_type IN ('MECHANISM', 'STRUCTURAL_VARIABLE', 'CANDIDATE_BRIDGE')
   AND s.sd_status <> 'LATENT_MECHANISM'
UNION ALL
SELECT 'world_latent_promoted', 'ERROR', s.node_id, 'world별 LATENT 후보가 모든 world 공통으로 표시됨'
  FROM sd_node s
 WHERE s.node_type = 'CANDIDATE_BRIDGE'
   AND INSTR(s.worlds, 'ALL') > 0
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-05 Super-DAG edge 검사 (dangling · CAUSES · 제도/환경 → 사건 · context edge type)
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'dangling_edge', 'ERROR', e.edge_id, e.src || '→' || e.dst
  FROM sd_edge e
 WHERE NOT EXISTS (SELECT 1 FROM sd_node s WHERE s.node_id = e.src)
    OR NOT EXISTS (SELECT 1 FROM sd_node d WHERE d.node_id = e.dst)
UNION ALL
SELECT 'causal_inflation', 'ERROR', e.edge_id, 'CAUSES edge'
  FROM sd_edge e WHERE e.edge_type = 'CAUSES'
UNION ALL
SELECT 'institution_to_event', 'ERROR', e.edge_id, '제도 피쳐 ' || e.src || '가 사건·후보 ' || e.dst || '를 직접 만듦'
  FROM sd_edge e
  JOIN sd_node s ON s.node_id = e.src
  JOIN sd_node d ON d.node_id = e.dst
 WHERE s.node_type = 'INSTITUTIONAL_CONTEXT'
   AND d.node_type IN ('OBSERVED_EVENT', 'CANDIDATE_BRIDGE')
UNION ALL
SELECT 'environment_to_personal_fact', 'ERROR', e.edge_id,
       CASE WHEN d.node_type IN ('OBSERVED_EVENT', 'CANDIDATE_BRIDGE')
            THEN '환경 ' || e.src || '가 개인 사건·후보 ' || e.dst || '에 직접 연결'
            ELSE '환경 → 메커니즘은 CONTEXT_COMPATIBLE만 허용' END
  FROM sd_edge e
  JOIN sd_node s ON s.node_id = e.src
  JOIN sd_node d ON d.node_id = e.dst
 WHERE s.node_type = 'ENV_CONTEXT'
   AND e.origin <> 'FROZEN'
   AND (   d.node_type IN ('OBSERVED_EVENT', 'CANDIDATE_BRIDGE')
        OR (d.node_type = 'MECHANISM' AND e.edge_type <> 'CONTEXT_COMPATIBLE'))
UNION ALL
SELECT 'context_to_fact', 'ERROR', e.edge_id, 'context edge type ' || e.edge_type
  FROM sd_edge e
  JOIN sd_node s ON s.node_id = e.src
 WHERE s.sd_status = 'CONTEXT'
   AND e.origin <> 'FROZEN'
   AND e.edge_type NOT IN ('CONSTRAINS', 'CONTEXT_COMPATIBLE')
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-06 responsibility_to_biological
--   목적: 책임 branch B(M1–M4, 책임 변수, EP29·EP30)와 생물학 branch A(MB, 구금 경과, EP26·EP27)를
--         잇는 Super-DAG edge 금지. 후보 node는 자기 branch 값으로 판정한다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'responsibility_to_biological', 'ERROR', x.edge_id, '책임 branch와 생물학 branch를 연결 ' || x.src || '→' || x.dst
  FROM (SELECT e.edge_id, e.src, e.dst,
               CASE WHEN e.src IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'BRANCH_B')
                      OR (s.node_type = 'CANDIDATE_BRIDGE' AND s.branch = 'B_PROCEDURAL') THEN 'B'
                    WHEN e.src IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'BRANCH_A')
                      OR (s.node_type = 'CANDIDATE_BRIDGE' AND s.branch = 'A_BIOLOGICAL') THEN 'A'
               END AS src_branch,
               CASE WHEN e.dst IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'BRANCH_B')
                      OR (d.node_type = 'CANDIDATE_BRIDGE' AND d.branch = 'B_PROCEDURAL') THEN 'B'
                    WHEN e.dst IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'BRANCH_A')
                      OR (d.node_type = 'CANDIDATE_BRIDGE' AND d.branch = 'A_BIOLOGICAL') THEN 'A'
               END AS dst_branch
          FROM sd_edge e
          JOIN sd_node s ON s.node_id = e.src
          JOIN sd_node d ON d.node_id = e.dst
         WHERE e.origin <> 'FROZEN') x
 WHERE (x.src_branch = 'B' AND x.dst_branch = 'A')
    OR (x.src_branch = 'A' AND x.dst_branch = 'B')
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-07 w6_reactivation (REJECTED world)
--   목적: 배제된 world(W6)는 공존 분석·개입 분석에 들어가면 안 된다.
--         목록 문자열 'W1, W2' 안의 정확한 원소 검색: ', ' || 목록 || ', ' LIKE '%, W6, %'
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'w6_reactivation', 'ERROR', w.world_id, 'REJECTED world가 공존 분석에 들어감'
  FROM narrative_world w
 WHERE w.status = 'REJECTED'
   AND EXISTS (SELECT 1 FROM mechanism_interaction mi
                WHERE ', ' || mi.cooccur_worlds || ', ' LIKE '%, ' || w.world_id || ', %')
UNION ALL
SELECT 'w6_reactivation', 'ERROR', w.world_id, 'REJECTED world가 개입 분석에 들어감'
  FROM narrative_world w
 WHERE w.status = 'REJECTED'
   AND EXISTS (SELECT 1 FROM mechanism_intervention mi
                WHERE ', ' || mi.affected_worlds || ', ' LIKE '%, ' || w.world_id || ', %')
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-08 world configuration 규칙 (경쟁 설명 world만)
--   OFF  인데 그 메커니즘이 주(PRIMARY)인 후보를 world가 쓰면 off_mechanism_alive
--   OFF  인데 그 메커니즘을 부정하는 후보가 없으면 unspecified_as_off (근거 없는 OFF = UNSPECIFIED여야 함)
--   UNSPECIFIED 인데 관련 후보(주 또는 부정)가 있으면 config_value (관측 고정 M5는 예외)
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT CASE WHEN u.config_value = 'OFF' AND u.n_primary_bridges > 0 THEN 'off_mechanism_alive'
            WHEN u.config_value = 'OFF'                            THEN 'unspecified_as_off'
            ELSE 'config_value' END,
       'ERROR', u.world_id,
       u.mechanism_id || '=' || u.config_value || ' (주 후보 ' || u.n_primary_bridges
       || ', 부정 후보 ' || u.n_negating_bridges || ')'
  FROM v_world_mechanism_usage u
  JOIN narrative_world w ON w.world_id = u.world_id
 WHERE w.status = 'COMPETING_EXPLANATION'
   AND (   (u.config_value = 'OFF' AND (u.n_primary_bridges > 0 OR u.n_negating_bridges = 0))
        OR (    u.config_value = 'UNSPECIFIED'
            AND u.n_primary_bridges + u.n_negating_bridges > 0
            AND u.mechanism_id NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'OBSERVED_ANCHORED')))
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-09 incompatible_coexistence
--   목적: 공존 불가(INCOMPATIBLE)인 메커니즘 쌍이 한 world에서 둘 다 ON이면 안 된다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'incompatible_coexistence', 'ERROR', ca.world_id,
       mi.mechanism_a_id || '·' || mi.mechanism_b_id || '가 INCOMPATIBLE인데 둘 다 ON'
  FROM mechanism_interaction mi
  JOIN world_mechanism_config ca ON ca.mechanism_id = mi.mechanism_a_id AND ca.config_value = 'ON'
  JOIN world_mechanism_config cb ON cb.mechanism_id = mi.mechanism_b_id AND cb.config_value = 'ON'
                                AND cb.world_id = ca.world_id
  JOIN narrative_world w         ON w.world_id = ca.world_id AND w.status = 'COMPETING_EXPLANATION'
 WHERE mi.coexistence = 'INCOMPATIBLE'
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-10 world_merge
--   목적: 상충 후보 쌍을 한 world에 넣지 않고, 서로 다른 world의 bridge 구성이 같으면 안 된다(병합 의심).
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'world_merge', 'ERROR', a.world_id, '상충 후보 ' || cp.candidate_a || '+' || cp.candidate_b || '가 한 world에 있음'
  FROM rule_conflict_pair cp
  JOIN world_candidate a ON a.candidate_id = cp.candidate_a
  JOIN world_candidate b ON b.candidate_id = cp.candidate_b AND b.world_id = a.world_id
  JOIN narrative_world w ON w.world_id = a.world_id AND w.status = 'COMPETING_EXPLANATION'
UNION ALL
SELECT 'world_merge', 'ERROR', 'worlds', '서로 다른 world의 bridge 구성이 같음: ' || x.worlds
  FROM (SELECT LISTAGG(world_id, ',') WITHIN GROUP (ORDER BY world_id) AS worlds
          FROM narrative_world
         GROUP BY latent_bridges
        HAVING COUNT(*) > 1) x
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-11 outcome_world_dependency (Super-DAG)
--   목적: 공통 결말 node는 Super-DAG에서도 OBSERVED이고 worlds = 'ALL (공통)'이어야 하며,
--         후보 bridge가 공통 결말을 명령 실행(ORDER_TO_ACTION)으로 만들면 안 된다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'outcome_world_dependency', 'ERROR', r.member_id, '공통 결말이 OBSERVED·모든 world 공통으로 표시되지 않음'
  FROM rule_set_member r
  LEFT JOIN sd_node s ON s.node_id = r.member_id
 WHERE r.rule_set = 'COMMON_OUTCOME'
   AND (s.node_id IS NULL OR s.sd_status <> 'OBSERVED' OR s.worlds <> 'ALL (공통)')
UNION ALL
SELECT 'outcome_world_dependency', 'ERROR', e.edge_id, '후보가 공통 결말을 명령 실행으로 만듦'
  FROM sd_edge e
  JOIN sd_node s         ON s.node_id = e.src AND s.node_type = 'CANDIDATE_BRIDGE'
  JOIN rule_set_member r ON r.rule_set = 'COMMON_OUTCOME' AND r.member_id = e.dst
 WHERE e.edge_type = 'ORDER_TO_ACTION'
UNION ALL
-- =============================================================================
-- UNRESOLVED: 사료가 결정해 주지 않는 것 (오류 아님 — 보존)
-- =============================================================================
-- A4-12 coexistence_undetermined / interaction_direction
--   대상: 관측 고정 메커니즘(M5)과 생물학 메커니즘(MB)을 뺀 쌍
--   - 어느 경쟁 world도 둘을 함께 쓰지 않으면(cooccur_worlds NULL) → 공존 여부 미결
--   - 함께 쓰는 world가 있고 relation에 COMPLEMENT가 있으면 → 방향(누가 누구를 이끌었는가) 미결
--   기대: coexistence_undetermined 2 (M2×M3, M3×M4), interaction_direction 8
-- -----------------------------------------------------------------------------
SELECT CASE WHEN mi.cooccur_worlds IS NULL THEN 'coexistence_undetermined' ELSE 'interaction_direction' END,
       'UNRESOLVED',
       mi.mechanism_a_id || '×' || mi.mechanism_b_id,
       CASE WHEN mi.cooccur_worlds IS NULL
            THEN mi.coexistence || ' — 어느 경쟁 world도 둘을 함께 쓰지 않아 함께 작동했는지는 사료로 결정되지 않음'
            ELSE '함께 쓰이는 world(' || mi.cooccur_worlds || ')가 있지만 방향은 사료에 없음' END
  FROM mechanism_interaction mi
 WHERE mi.mechanism_a_id NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'OBSERVED_ANCHORED')
   AND mi.mechanism_b_id NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'OBSERVED_ANCHORED')
   AND 'MB' NOT IN (mi.mechanism_a_id, mi.mechanism_b_id)
   AND (mi.cooccur_worlds IS NULL OR INSTR(mi.relation, 'COMPLEMENT') > 0)
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-13 multiple_explanations
--   목적: OR/XOR 구조 변수에서, 그 변수의 gap을 채우는 '쓸 수 있는' 후보들의 주 메커니즘이
--         변수 입력 중 2개 이상이면 → 같은 관측 전이를 여러 메커니즘이 설명할 수 있음(미결).
--   기대: UNRESOLVED 4 (V_COMMAND_SOURCE, V_INFO_TO_COMMANDER, V_INVESTIGATION_SCOPE, V_INITIAL_JUDGMENT_BASIS)
-- -----------------------------------------------------------------------------
SELECT 'multiple_explanations', 'UNRESOLVED', x.var_id,
       x.op || ': ' || x.mechanisms || '가 같은 관측 전이(' || x.target || ')를 설명할 수 있음'
  FROM (SELECT sr.var_id, sr.op, sr.target,
               COUNT(DISTINCT u.primary_mechanism) AS n_mech,
               LISTAGG(u.primary_mechanism, ', ') WITHIN GROUP (ORDER BY u.primary_mechanism) AS mechanisms
          FROM structural_rule sr
          JOIN (SELECT DISTINCT r.var_id, cu.primary_mechanism
                  FROM structural_rule r
                  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) gi
                    ON gi.n <= REGEXP_COUNT(r.gap, '[^|]+')
                  JOIN v_candidate_usable cu
                    ON cu.gap_id = REGEXP_SUBSTR(r.gap, '[^|]+', 1, gi.n)
                 WHERE '|' || r.inputs || '|' LIKE '%|' || cu.primary_mechanism || '|%') u
            ON u.var_id = sr.var_id
         WHERE sr.op IN ('OR', 'XOR')
         GROUP BY sr.var_id, sr.op, sr.target) x
 WHERE x.n_mech >= 2
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-14 unresolved_item — Super-DAG의 UNRESOLVED node
--   기대: UNRESOLVED 6 (U_ID06, U_ID07, U_ID08, U_OE007, U_OE062, U_G10)
-- -----------------------------------------------------------------------------
SELECT 'unresolved_item', 'UNRESOLVED', s.node_id, s.label
  FROM sd_node s
 WHERE s.sd_status = 'UNRESOLVED'
UNION ALL
-- -----------------------------------------------------------------------------
-- A4-15 super_dag_summary / frozen_graph_changed (INFO 2)
-- -----------------------------------------------------------------------------
SELECT 'super_dag_summary', 'INFO', 'super_dag',
       'node ' || (SELECT LISTAGG(sd_status || ' ' || cnt, ', ') WITHIN GROUP (ORDER BY sd_status)
                     FROM (SELECT sd_status, COUNT(*) AS cnt FROM sd_node GROUP BY sd_status))
       || ' · edge ' || (SELECT LISTAGG(sd_status || ' ' || cnt, ', ') WITHIN GROUP (ORDER BY sd_status)
                           FROM (SELECT sd_status, COUNT(*) AS cnt FROM sd_edge GROUP BY sd_status))
  FROM dual
UNION ALL
SELECT 'frozen_graph_changed', 'INFO', 'observed_dag',
       'frozen node ' || (SELECT COUNT(*) FROM dag_node) || '·edge ' || (SELECT COUNT(*) FROM dag_edge)
       || ' Super-DAG 대조 완료 (sha256 ' || SUBSTR(f.sha256, 1, 12) || ' 재계산은 Python에서)'
  FROM dag_freeze f;


-- 실행 예 ------------------------------------------------------------------------
SELECT check_name, severity, target, message
  FROM v_sql_audit_4
 ORDER BY DECODE(severity, 'ERROR', 1, 'WARN', 2, 'UNRESOLVED', 3, 4), check_name, target;

-- 기대: UNRESOLVED 20, INFO 2 (ERROR·WARN 없음)
SELECT severity, COUNT(*) AS n FROM v_sql_audit_4 GROUP BY severity ORDER BY severity;

-- UNRESOLVED 종류별 — 기대: interaction_direction 8, coexistence_undetermined 2,
--                          multiple_explanations 4, unresolved_item 6
SELECT check_name, COUNT(*) AS n
  FROM v_sql_audit_4
 WHERE severity = 'UNRESOLVED'
 GROUP BY check_name
 ORDER BY check_name;
