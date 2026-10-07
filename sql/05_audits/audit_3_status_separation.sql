-- =============================================================================
-- audit_3_status_separation.sql — AUDIT 3: OBSERVED / DERIVED / LATENT 분리
-- -----------------------------------------------------------------------------
-- 원본 Python: scripts/gusun_clean/audits.py audit3() + bridge_support_checks() + outcome_dependency_checks()
-- 결과 형식: (check_name, severity, target, message)
-- Python Audit 3(world 포함) 결과: ERROR 0 / WARN 0 / UNRESOLVED 1 / INFO 11
--
-- NOT PORTED TO SQL
--   * freeze_violation의 sha256 재계산: Python json.dumps 직렬화를 바이트 단위로 재현해야 한다.
--     대신 동결 기록(dag_freeze)의 node·edge·latent 수와 실제 표를 비교한다(INFO/ERROR 1행).
--   * environmental_leakage '환경만으로 개인 수준 latent node': latent node의 individual_level 값은
--     CSV로 내보내지 않았다(Python 내부 필드).
--   * identity_forcing '서술 정규식'(_identity_needs)·open_set_closure: 전후방 탐색 정규식이라 옮기지 않음.
-- =============================================================================

CREATE OR REPLACE VIEW v_sql_audit_3 AS
-- -----------------------------------------------------------------------------
-- A3-01 identity_forcing (동일성 대장)
--   목적: 모델은 동일성을 스스로 확정하지 않는다. 관리 대상 ID는 UNRESOLVED이거나 사용자 확정이어야 한다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'identity_forcing' AS check_name, 'ERROR' AS severity, ir.identity_id AS target,
       '사용자 확정 근거 없는 status=' || ir.status AS message
  FROM identity_register ir
  JOIN rule_set_member r ON r.rule_set = 'MODEL_CONTROLLED_IDENTITY' AND r.member_id = ir.identity_id
 WHERE NOT (   ir.status = 'UNRESOLVED'
            OR (ir.status = 'RESOLVED' AND ir.resolved_by = 'USER' AND ir.resolution_basis IS NOT NULL))
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-02 freeze_violation (집계 비교 — 해시 재계산은 NOT PORTED)
--   목적: 동결 이후 observed DAG의 node·edge 수가 그대로이고 LATENT가 0인지 확인.
--   기대: INFO 1행 ('동결 집계 일치')
-- -----------------------------------------------------------------------------
SELECT 'freeze_violation',
       CASE WHEN f.n_nodes = (SELECT COUNT(*) FROM dag_node)
             AND f.n_edges = (SELECT COUNT(*) FROM dag_edge)
             AND f.latent_count = 0
            THEN 'INFO' ELSE 'ERROR' END,
       'observed_dag',
       CASE WHEN f.n_nodes = (SELECT COUNT(*) FROM dag_node)
             AND f.n_edges = (SELECT COUNT(*) FROM dag_edge)
             AND f.latent_count = 0
            THEN '동결 집계 일치 (sha256 ' || SUBSTR(f.sha256, 1, 12) || ' — 해시 재계산은 Python에서)'
            ELSE '동결 이후 observed DAG 집계가 바뀜' END
  FROM dag_freeze f
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-03 latent_as_observed (LATENT → OBSERVED 오분류)
--   목적: observed 표에는 OBSERVED node·OBSERVED/DERIVED edge만, 후보 표에는 LATENT만 있어야 한다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'latent_as_observed', 'ERROR', n.node_id, 'observed 표에 비관측 node'
  FROM dag_node n WHERE n.node_status <> 'OBSERVED'
UNION ALL
SELECT 'latent_as_observed', 'ERROR', e.edge_id, 'observed 표에 LATENT edge'
  FROM dag_edge e WHERE e.status NOT IN ('OBSERVED', 'DERIVED')
UNION ALL
SELECT 'latent_as_observed', 'ERROR', c.candidate_id, '후보 status=' || c.status
  FROM latent_candidate c WHERE c.status <> 'LATENT'
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-04 orphan_candidate
--   목적: 후보는 존재하는 gap에 속해야 한다.  정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'orphan_candidate', 'ERROR', c.candidate_id, 'gap 없음'
  FROM latent_candidate c
 WHERE NOT EXISTS (SELECT 1 FROM gap g WHERE g.gap_id = c.gap_id)
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-05 latent node 표지
--   목적: latent node는 관측 node id와 겹치지 않고(LN_ 접두어), 서술이 '[LATENT]'로 시작해야 한다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'latent_as_observed', 'ERROR', le.candidate_id,
       CASE WHEN EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = le.element_id)
                 THEN 'latent node id가 observed id와 충돌 ' || le.element_id
            WHEN SUBSTR(le.element_id, 1, 3) <> 'LN_'
                 THEN 'latent node id 접두어 오류 ' || le.element_id
            ELSE le.element_id || ' 서술에 [LATENT] 표지 없음' END
  FROM latent_element le
 WHERE le.kind = 'node'
   AND (   EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = le.element_id)
        OR SUBSTR(le.element_id, 1, 3) <> 'LN_'
        OR SUBSTR(le.text, 1, 8) <> '[LATENT]'
        OR le.text IS NULL)
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-06 latent edge 검사
--   목적: latent edge는 (1) 관측 node나 같은 후보의 latent node만 잇고(dangling 금지),
--         (2) 관측 node끼리 직접 잇지 않으며(관측 관계처럼 읽히므로), (3) status=LATENT,
--         (4) CAUSES·허용 밖 type 금지, (5) 환경 node에서는 CONTEXT_SUPPORTS만,
--         (6) RESPONSIBILITY_LINK는 국왕 판단 node로만.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'dangling_latent_edge', 'ERROR', le.candidate_id, le.src || '->' || le.dst
  FROM latent_element le
 WHERE le.kind = 'edge'
   AND (   (    NOT EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = le.src)
            AND NOT EXISTS (SELECT 1 FROM latent_element x
                             WHERE x.candidate_id = le.candidate_id AND x.kind = 'node' AND x.element_id = le.src))
        OR (    NOT EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = le.dst)
            AND NOT EXISTS (SELECT 1 FROM latent_element x
                             WHERE x.candidate_id = le.candidate_id AND x.kind = 'node' AND x.element_id = le.dst)))
UNION ALL
SELECT 'latent_as_observed', 'ERROR', le.candidate_id,
       '관측 node 사이 직접 latent edge ' || le.src || '->' || le.dst || ' — latent node를 사이에 둘 것'
  FROM latent_element le
  JOIN dag_node s ON s.node_id = le.src
  JOIN dag_node d ON d.node_id = le.dst
 WHERE le.kind = 'edge'
UNION ALL
SELECT 'latent_as_observed', 'ERROR', le.candidate_id, 'latent edge status가 LATENT가 아님'
  FROM latent_element le
 WHERE le.kind = 'edge' AND le.status <> 'LATENT'
UNION ALL
SELECT CASE WHEN le.edge_type = 'CAUSES' THEN 'causal_inflation' ELSE 'unsupported_edge' END,
       'ERROR', le.candidate_id, '허용되지 않은 latent edge type ' || le.edge_type
  FROM latent_element le
 WHERE le.kind = 'edge'
   AND le.edge_type NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'EDGE_TYPE')
UNION ALL
SELECT 'environmental_leakage', 'ERROR', le.candidate_id, '환경 node에서 CONTEXT_SUPPORTS 아닌 latent edge'
  FROM latent_element le
  JOIN dag_node s ON s.node_id = le.src
 WHERE le.kind = 'edge'
   AND s.layer = 'ENVIRONMENT'
   AND le.edge_type <> 'CONTEXT_SUPPORTS'
UNION ALL
SELECT 'causal_inflation', 'ERROR', le.candidate_id,
       'latent RESPONSIBILITY_LINK가 판단 아닌 observed node ' || le.dst || '로'
  FROM latent_element le
  JOIN dag_node d ON d.node_id = le.dst
 WHERE le.kind = 'edge'
   AND le.edge_type = 'RESPONSIBILITY_LINK'
   AND d.layer <> 'ROYAL_JUDGMENT'
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-07 provenance / audit-only 승격
--   목적: audit_attestation이 가리키는 05 명제가 있어야 하고, 05 근거만으로 LATENT를 벗어나면 안 된다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'provenance', 'ERROR', ce.candidate_id, 'audit prop ' || ce.evidence_id || ' 없음'
  FROM candidate_evidence ce
 WHERE ce.evidence_role = 'AUDIT_ATTESTATION'
   AND NOT EXISTS (SELECT 1 FROM audit_proposition p WHERE p.prop_id = ce.evidence_id)
UNION ALL
SELECT 'latent_as_observed', 'ERROR', c.candidate_id, 'audit-only 근거로 승격'
  FROM latent_candidate c
 WHERE c.audit_attestation IS NOT NULL
   AND c.status <> 'LATENT'
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-08 grading
--   목적: final HIGH는 source_consistency HIGH이고 추가 가정이 3개 미만일 때만.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'grading', 'ERROR', c.candidate_id,
       CASE WHEN c.source_consistency <> 'HIGH' THEN 'source_consistency가 HIGH가 아닌데 overall HIGH'
            ELSE '추가 가정 3개 이상인데 HIGH' END
  FROM latent_candidate c
 WHERE c.overall = 'HIGH'
   AND (c.source_consistency <> 'HIGH' OR c.n_assumptions >= 3)
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-09 bridge 근거 재감사 (bridge_support_checks)
--   목적: LATENT bridge의 source_support는 bridge 자체의 사료 근거만으로 매겨야 한다.
--     a) bridge가 사료에 직접 있으면(YES) LATENT 분류를 다시 볼 것
--     b) 직접 근거가 없는데(NO) HIGH 금지
--     c) MEDIUM 이상인데 bridge_evidence 없음 금지
--     d) 시간 인접·endpoint 내용만(basis ⊆ {TEMPORAL, ENDPOINT_ONLY})으로 MEDIUM 이상 금지
--     e) 제도·환경·시간 가능성만(basis ⊆ {INSTITUTIONAL, ENVIRONMENT, TEMPORAL})으로 MEDIUM 이상 금지
--     f) confirmed 비-endpoint 근거 없이 HIGH 금지
--   'A ⊆ S'는 "S 밖의 basis가 하나도 없다" = NOT EXISTS로 쓴다(관계 대수의 나눗셈 응용).
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'latent_classification', 'ERROR', v.candidate_id, 'bridge가 사료에 직접 있음(YES) — LATENT 분류를 점검할 것'
  FROM v_candidate_level v WHERE v.bridge_directly_attested = 'YES'
UNION ALL
SELECT 'bridge_support_inflation', 'ERROR', v.candidate_id, 'bridge 직접 근거가 없는데(NO) source_support=HIGH'
  FROM v_candidate_level v WHERE v.bridge_directly_attested = 'NO' AND v.support_level >= 3
UNION ALL
SELECT 'bridge_support_inflation', 'ERROR', v.candidate_id, 'bridge_evidence 없이 source_support=' || v.source_support
  FROM v_candidate_level v
 WHERE v.support_level >= 2
   AND NOT EXISTS (SELECT 1 FROM candidate_evidence ce
                    WHERE ce.candidate_id = v.candidate_id AND ce.evidence_role = 'BRIDGE_EVIDENCE')
UNION ALL
SELECT 'temporal_inflation', 'ERROR', v.candidate_id, '시간 인접·endpoint 내용만으로 source_support=' || v.source_support
  FROM v_candidate_level v
 WHERE v.support_level >= 2
   AND NOT EXISTS (SELECT 1 FROM candidate_bridge_basis b
                    WHERE b.candidate_id = v.candidate_id
                      AND b.basis_code NOT IN ('TEMPORAL', 'ENDPOINT_ONLY'))
UNION ALL
SELECT 'institutional_inflation', 'ERROR', v.candidate_id, '제도·환경 가능성만으로 source_support=' || v.source_support
  FROM v_candidate_level v
 WHERE v.support_level >= 2
   AND NOT EXISTS (SELECT 1 FROM candidate_bridge_basis b
                    WHERE b.candidate_id = v.candidate_id
                      AND b.basis_code NOT IN ('INSTITUTIONAL', 'ENVIRONMENT', 'TEMPORAL'))
UNION ALL
SELECT 'bridge_support_inflation', 'ERROR', v.candidate_id, 'confirmed 비-endpoint 근거 없이 HIGH'
  FROM v_candidate_level v
 WHERE v.support_level >= 3
   AND NOT EXISTS (SELECT 1 FROM candidate_bridge_basis b
                    WHERE b.candidate_id = v.candidate_id AND b.basis_code = 'CONFIRMED_NON_ENDPOINT')
UNION ALL
-- g) endpoint_leakage: endpoint 관측 node의 구성 fact를 bridge 근거로 인용하면 안 된다
SELECT 'endpoint_leakage', 'ERROR', ce.candidate_id,
       'endpoint 구성 fact ' || ce.evidence_id || '를 bridge 근거로 인용'
  FROM candidate_evidence ce
 WHERE ce.evidence_role = 'BRIDGE_EVIDENCE'
   AND EXISTS (SELECT 1
                 FROM v_candidate_endpoint ep
                 JOIN episode_member em ON em.episode_id = ep.node_id
                WHERE ep.candidate_id = ce.candidate_id
                  AND em.fact_id = ce.evidence_id)
UNION ALL
-- h) final 등급 일관성
SELECT 'bridge_support_inflation', 'ERROR', v.candidate_id,
       CASE WHEN v.overall = 'HIGH' THEN 'evidence·plausibility가 모두 HIGH가 아닌데 final HIGH'
            ELSE 'source_support NONE인데 final이 LOW보다 높음' END
  FROM v_candidate_level v
 WHERE (v.overall = 'HIGH' AND NOT (v.source_support = 'HIGH' AND v.plausibility_grade = 'HIGH'))
    OR (v.source_support = 'NONE' AND v.overall NOT IN ('LOW', 'INCOMPATIBLE'))
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-10 support_basis 상한
--   목적: 환경 context만, 또는 제도 compatibility만 근거인 후보는 LOW 상한이다.
--   기대: ERROR 0, INFO 3 (G01c, G10b, G10c)
-- -----------------------------------------------------------------------------
SELECT CASE WHEN c.support_basis = 'ENVIRONMENTAL_CONTEXT' THEN 'environmental_leakage' ELSE 'institutional_overreach' END,
       'ERROR', c.candidate_id, c.support_basis || '만으로 ' || c.overall
  FROM latent_candidate c
 WHERE c.support_basis IN ('ENVIRONMENTAL_CONTEXT', 'INSTITUTIONAL_COMPATIBILITY')
   AND c.overall IN ('HIGH', 'MEDIUM')
UNION ALL
SELECT 'support_basis_cap', 'INFO', c.candidate_id, c.support_basis || '만 근거 → LOW 상한 적용'
  FROM latent_candidate c
 WHERE c.support_basis IN ('ENVIRONMENTAL_CONTEXT', 'INSTITUTIONAL_COMPATIBILITY')
   AND c.overall = 'LOW'
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-11 resolved_identity_conflict / stale_identity_condition / identity_forcing
--   목적: 추가 가정이 사용자 확정 동일성을 '불성립'으로 전제하면 그 후보는 INCOMPATIBLE이어야 한다.
--         확정 ID가 (불성립 전제가 아닌) 일반 조건으로 남거나, 미확정 ID에 기대는 후보가 HIGH면 안 된다.
--   기대: ERROR 0, INFO 2 (G09b ID02, G09c ID03)
-- -----------------------------------------------------------------------------
SELECT 'resolved_identity_conflict',
       CASE WHEN c.overall <> 'INCOMPATIBLE' THEN 'ERROR' ELSE 'INFO' END,
       c.candidate_id,
       '사용자 확정 ' || ng.identity_id
       || CASE WHEN c.overall <> 'INCOMPATIBLE' THEN '을 불성립으로 전제하는데 INCOMPATIBLE이 아님'
               ELSE '과 충돌 → INCOMPATIBLE·PRUNED' END
  FROM latent_candidate c
  JOIN (SELECT DISTINCT x.candidate_id,
               REGEXP_SUBSTR(x.extra_assumptions, '(ID[0-9]{2}) 불성립', 1, seq.n, NULL, 1) AS identity_id
          FROM latent_candidate x
          JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
            ON seq.n <= REGEXP_COUNT(x.extra_assumptions, 'ID[0-9]{2} 불성립')) ng
    ON ng.candidate_id = c.candidate_id
  JOIN identity_register ir ON ir.identity_id = ng.identity_id AND ir.status = 'RESOLVED'
UNION ALL
SELECT 'stale_identity_condition', 'ERROR', cic.candidate_id, cic.identity_id || '는 사용자 확정인데 추가 가정으로 남아 있음'
  FROM candidate_identity_condition cic
  JOIN identity_register ir ON ir.identity_id = cic.identity_id
  JOIN latent_candidate c   ON c.candidate_id = cic.candidate_id
 WHERE ir.status = 'RESOLVED'
   AND INSTR(c.extra_assumptions, cic.identity_id || ' 불성립') = 0
UNION ALL
SELECT 'identity_forcing', 'ERROR', cic.candidate_id, '미확정 동일성 ' || cic.identity_id || '에 기대는데 HIGH'
  FROM candidate_identity_condition cic
  JOIN identity_register ir ON ir.identity_id = cic.identity_id
  JOIN latent_candidate c   ON c.candidate_id = cic.candidate_id
 WHERE ir.status = 'UNRESOLVED'
   AND c.overall = 'HIGH'
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-12 후보 서술의 책임→인과 / 환경→개인 단정
--   서술 = label + description + latent node 서술들 (LISTAGG)
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT h.check_name, 'ERROR', h.candidate_id, '''' || h.fragment || ''''
  FROM (SELECT p.check_name, t.candidate_id, REGEXP_SUBSTR(t.full_text, p.oracle_regex) AS fragment
          FROM (SELECT c.candidate_id,
                       c.label || ' ' || c.description || ' ' ||
                       (SELECT LISTAGG(le.text, ' ') WITHIN GROUP (ORDER BY le.element_id)
                          FROM latent_element le
                         WHERE le.candidate_id = c.candidate_id AND le.kind = 'node') AS full_text
                  FROM latent_candidate c) t
          JOIN rule_text_pattern p
            ON p.check_name IN ('responsibility_to_causation', 'environment_to_individual_fact')) h
 WHERE h.fragment IS NOT NULL
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-13 audit_only_support (INFO)
--   목적: confirmed 지지(supports) 없이 05 흔적(audit_attestation)만 있는 후보 — LATENT 유지 보고
--   기대: INFO 3 (G04d, G07d, G12b)
-- -----------------------------------------------------------------------------
SELECT 'audit_only_support', 'INFO', c.candidate_id, 'confirmed 지지 없이 05 흔적만 있음 — LATENT 유지'
  FROM latent_candidate c
 WHERE c.audit_attestation IS NOT NULL
   AND c.supports IS NULL
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-14 candidate_budget
--   목적: gap마다 후보는 1~5개. 후보가 없는 gap도 오류.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'candidate_budget', 'ERROR', g.gap_id, '후보 ' || COUNT(c.candidate_id) || '개 (허용 1~5)'
  FROM gap g
  LEFT JOIN latent_candidate c ON c.gap_id = g.gap_id
 GROUP BY g.gap_id
HAVING COUNT(c.candidate_id) NOT BETWEEN 1 AND 5
UNION ALL
-- =============================================================================
-- World 검사 (Stage 5 이후)
-- =============================================================================
-- A3-15 world_integrity
--   목적: (a) 경쟁 설명 world는 INCOMPATIBLE·대조용(contradiction HIGH) 후보를 쓰지 않는다
--         (b) 한 world에서 gap당 후보 1개 (c) 상충 후보 쌍을 함께 쓰지 않는다
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'world_integrity', 'ERROR', d.world_id,
       CASE WHEN d.overall = 'INCOMPATIBLE' THEN 'INCOMPATIBLE 후보 ' || d.candidate_id || ' 사용'
            ELSE '경쟁 설명 world가 대조용 후보 ' || d.candidate_id || ' 사용' END
  FROM v_world_candidate_detail d
 WHERE d.world_status <> 'REJECTED'
   AND (d.overall = 'INCOMPATIBLE' OR d.contradiction_risk = 'HIGH')
UNION ALL
SELECT 'world_integrity', 'ERROR', wc.world_id, '한 gap(' || wc.gap_id || ')에 후보 2개 이상'
  FROM world_candidate wc
 GROUP BY wc.world_id, wc.gap_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 'world_integrity', 'ERROR', a.world_id, '상충 후보 ' || cp.candidate_a || '+' || cp.candidate_b
  FROM rule_conflict_pair cp
  JOIN world_candidate a ON a.candidate_id = cp.candidate_a
  JOIN world_candidate b ON b.candidate_id = cp.candidate_b AND b.world_id = a.world_id
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-16 [L] 표지 (CLOB 검색)
--   목적: world 서사(narrative, CLOB)에서 LATENT 부분은 [L]로 표시한다. bridge 수만큼 있어야 한다.
--   정상: 0행 / 오류: 표지가 없음(ERROR) 또는 bridge보다 적음(WARN)
-- -----------------------------------------------------------------------------
SELECT 'latent_as_observed',
       CASE WHEN REGEXP_COUNT(w.narrative, '\[L\]') = 0 THEN 'ERROR' ELSE 'WARN' END,
       w.world_id,
       '[L] 표지 ' || REGEXP_COUNT(w.narrative, '\[L\]') || '개 < bridge ' || b.n_bridges || '개'
  FROM narrative_world w
  JOIN (SELECT world_id, COUNT(*) AS n_bridges FROM world_candidate GROUP BY world_id) b
    ON b.world_id = w.world_id
 WHERE REGEXP_COUNT(w.narrative, '\[L\]') < b.n_bridges
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-17 world 서술의 책임→인과 / 환경→개인 단정 (narrative는 CLOB, story_implication은 VARCHAR2)
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT p.check_name, 'ERROR', w.world_id, 'narrative: 정규식 ' || p.pattern_id || ' 일치'
  FROM narrative_world w
  JOIN rule_text_pattern p
    ON p.check_name IN ('responsibility_to_causation', 'environment_to_individual_fact')
 WHERE REGEXP_LIKE(w.narrative, p.oracle_regex)
UNION ALL
SELECT p.check_name, 'ERROR', w.world_id, 'story_implication: ''' || REGEXP_SUBSTR(w.story_implication, p.oracle_regex) || ''''
  FROM narrative_world w
  JOIN rule_text_pattern p
    ON p.check_name IN ('responsibility_to_causation', 'environment_to_individual_fact')
 WHERE REGEXP_LIKE(w.story_implication, p.oracle_regex)
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-18 world_integrity (world 쌍 차이)
--   목적: world 쌍마다 2개 이상 gap에서 선택이 달라야 한다(사실상 같은 world 금지).
--   정상: 0행 / 오류: (world_a/world_b, 차이 gap 수)
-- -----------------------------------------------------------------------------
SELECT 'world_integrity', 'ERROR', p.world_a || '/' || p.world_b, '차이 gap ' || p.n_diff_gaps || '개 < 2'
  FROM v_world_pair_gap_diff p
 WHERE p.n_diff_gaps < 2
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-19 outcome_world_dependency
--   목적: 재검토·최종 판단·처분(공통 결말 23개)은 모든 world에 공통인 OBSERVED다.
--         (a) 공통 결말 node가 observed graph에 있어야 하고 (b) world 서술이 결말을 world에 종속시키면 안 되고
--         (c) 후보의 latent 명령이 공통 결말을 '실행'으로 만들면 안 된다.
--   기대: ERROR 0, INFO 1 (요약)
-- -----------------------------------------------------------------------------
SELECT 'outcome_world_dependency', 'ERROR', r.member_id, '공통 결말 node가 observed graph에 없음'
  FROM rule_set_member r
 WHERE r.rule_set = 'COMMON_OUTCOME'
   AND NOT EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = r.member_id AND n.node_status = 'OBSERVED')
UNION ALL
SELECT 'outcome_world_dependency', 'ERROR', w.world_id, '결말을 world에 종속시킴'
  FROM narrative_world w
 WHERE REGEXP_LIKE(w.narrative,         (SELECT oracle_regex FROM rule_text_pattern WHERE pattern_id = 'OUTCOME_WORLD'))
    OR REGEXP_LIKE(w.story_implication, (SELECT oracle_regex FROM rule_text_pattern WHERE pattern_id = 'OUTCOME_WORLD'))
    OR REGEXP_LIKE(w.work_role,         (SELECT oracle_regex FROM rule_text_pattern WHERE pattern_id = 'OUTCOME_WORLD'))
    OR REGEXP_LIKE(w.difference,        (SELECT oracle_regex FROM rule_text_pattern WHERE pattern_id = 'OUTCOME_WORLD'))
    OR REGEXP_LIKE(w.story_question,    (SELECT oracle_regex FROM rule_text_pattern WHERE pattern_id = 'OUTCOME_WORLD'))
UNION ALL
SELECT 'outcome_world_dependency', 'ERROR', wc.world_id,
       wc.candidate_id || '가 공통 결말 ' || le.dst || '를 latent 명령의 실행으로 만듦'
  FROM world_candidate wc
  JOIN latent_element le  ON le.candidate_id = wc.candidate_id AND le.kind = 'edge'
  JOIN rule_set_member r  ON r.rule_set = 'COMMON_OUTCOME' AND r.member_id = le.dst
 WHERE le.edge_type = 'ORDER_TO_ACTION'
UNION ALL
SELECT 'outcome_world_dependency', 'INFO', 'worlds',
       '공통 결말 node ' || (SELECT COUNT(*) FROM rule_set_member WHERE rule_set = 'COMMON_OUTCOME')
       || '개는 모든 world에 공통인 OBSERVED다. 경쟁 설명 '
       || COUNT(CASE WHEN w.status = 'COMPETING_EXPLANATION' THEN 1 END) || '개, 배제된 설명 '
       || COUNT(CASE WHEN w.status = 'REJECTED' THEN 1 END) || '개'
  FROM narrative_world w
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-20 unresolved_gap (UNRESOLVED) — 관계 나눗셈(division)
--   목적: 어느 경쟁 설명 world도 메우지 않는 gap = "모든 경쟁 world의 unresolved 목록에 들어 있는 gap".
--         '모든'은 SQL에 없으므로 이중 NOT EXISTS로 쓴다:
--         "그 gap을 unresolved로 두지 않은 경쟁 world가 존재하지 않는다"
--   기대: UNRESOLVED 1 (G10)
-- -----------------------------------------------------------------------------
SELECT 'unresolved_gap', 'UNRESOLVED', g.gap_id,
       g.gap_status || ' — 어느 경쟁 설명 world도 이 gap을 메우지 않음 · unresolved_reason: ' || g.why_gap
  FROM gap g
 WHERE EXISTS (SELECT 1 FROM narrative_world w WHERE w.status <> 'REJECTED')
   AND NOT EXISTS (SELECT 1
                     FROM narrative_world w
                    WHERE w.status <> 'REJECTED'
                      AND NOT EXISTS (SELECT 1
                                        FROM world_unresolved_gap u
                                       WHERE u.world_id = w.world_id
                                         AND u.gap_id = g.gap_id))
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-21 open_gap_filled
--   목적: 사용자가 열어 두기로 한 gap(OPEN_UNRESOLVED)은 어떤 world도 채우면 안 된다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'open_gap_filled', 'ERROR', wc.world_id, g.gap_id || '은 OPEN_UNRESOLVED인데 ' || wc.candidate_id || ' 사용'
  FROM gap g
  JOIN world_candidate wc ON wc.gap_id = g.gap_id
 WHERE g.gap_status = 'OPEN_UNRESOLVED'
UNION ALL
-- -----------------------------------------------------------------------------
-- A3-22 world_integrity 요약 (INFO 1)
-- -----------------------------------------------------------------------------
SELECT 'world_integrity', 'INFO', 'worlds',
       'world ' || COUNT(*) || '개 (경쟁 설명 ' || COUNT(CASE WHEN status <> 'REJECTED' THEN 1 END)
       || ', rejected ' || COUNT(CASE WHEN status = 'REJECTED' THEN 1 END) || ')'
  FROM narrative_world;


-- 실행 예 ------------------------------------------------------------------------
SELECT check_name, severity, target, message
  FROM v_sql_audit_3
 ORDER BY DECODE(severity, 'ERROR', 1, 'WARN', 2, 'UNRESOLVED', 3, 4), check_name, target;

-- 기대: UNRESOLVED 1, INFO 11 (ERROR·WARN 없음)
SELECT severity, COUNT(*) AS n FROM v_sql_audit_3 GROUP BY severity ORDER BY severity;
