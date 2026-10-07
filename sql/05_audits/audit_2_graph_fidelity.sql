-- =============================================================================
-- audit_2_graph_fidelity.sql — AUDIT 2: observed DAG의 edge·node가 근거를 가지는가
-- -----------------------------------------------------------------------------
-- 원본 Python: scripts/gusun_clean/audits.py audit2()
-- 결과 형식: (check_name, severity, target, message)
-- Python Audit 2 결과: ERROR 0 / WARN 0 / UNRESOLVED 5 / INFO 1
--
-- NOT PORTED TO SQL
--   * identity_forcing의 '근거 문구 정규식' 검사(IDENTITY_TEXT_RULES): (?!\s*\(病), (?<!정) 같은
--     전후방 탐색을 쓰는데 Oracle 정규식에는 전후방 탐색이 없다. node 쌍 기반 검사(IDENTITY_SENSITIVE)는 옮겼다.
-- =============================================================================

CREATE OR REPLACE VIEW v_sql_audit_2 AS
-- -----------------------------------------------------------------------------
-- A2-01 unsupported_edge (끝점)
--   목적: edge의 양 끝 node가 observed DAG에 있어야 한다(orphan edge 금지). LEFT JOIN … IS NULL 형 anti-join.
--   정상: 0행 / 오류: 끝점이 없는 edge
-- -----------------------------------------------------------------------------
SELECT 'unsupported_edge' AS check_name, 'ERROR' AS severity, e.edge_id AS target,
       'endpoint 없음: ' || e.src || '->' || e.dst AS message
  FROM dag_edge e
  LEFT JOIN dag_node s ON s.node_id = e.src
  LEFT JOIN dag_node d ON d.node_id = e.dst
 WHERE s.node_id IS NULL
    OR d.node_id IS NULL
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-02 unsupported_edge (type) / causal_inflation (CAUSES)
--   목적: edge type은 허용 목록(stage2_graph.py EDGE_TYPES)에만 있어야 하고 CAUSES는 쓰지 않는다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT CASE WHEN e.edge_type = 'CAUSES' THEN 'causal_inflation' ELSE 'unsupported_edge' END,
       'ERROR', e.edge_id, '허용되지 않은 edge type ' || e.edge_type
  FROM dag_edge e
 WHERE e.edge_type NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'EDGE_TYPE')
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-03 unsupported_edge (basis)
--   목적: 모든 edge는 basis가 1개 이상이고, 모두 허용 basis(stage2_graph.py BASES)여야 한다.
--   정상: 0행 / 오류: basis가 없거나 모르는 basis를 쓴 edge
-- -----------------------------------------------------------------------------
SELECT 'unsupported_edge', 'ERROR', e.edge_id, 'basis 누락/오류: ' || e.basis
  FROM dag_edge e
 WHERE NOT EXISTS (SELECT 1 FROM edge_basis_type b WHERE b.edge_id = e.edge_id)
    OR EXISTS (SELECT 1
                 FROM edge_basis_type b
                WHERE b.edge_id = e.edge_id
                  AND b.basis_code NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'EDGE_BASIS'))
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-04 latent_leak (edge)
--   목적: observed DAG의 edge는 OBSERVED 또는 DERIVED뿐(LATENT 금지).
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'latent_leak', 'ERROR', e.edge_id, 'observed DAG에 status=' || e.status
  FROM dag_edge e
 WHERE e.status NOT IN ('OBSERVED', 'DERIVED')
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-05 unsupported_edge (근거 fact 없음) — 'source basis가 하나도 없는 DERIVED edge' 포함
--   목적: 모든 edge는 근거(confirmed fact 또는 환경 행)가 1개 이상 있어야 한다.
--   정상: 0행 / 오류: 근거 없는 edge
-- -----------------------------------------------------------------------------
SELECT 'unsupported_edge', 'ERROR', e.edge_id, '근거 fact 없음 (status=' || e.status || ')'
  FROM dag_edge e
 WHERE NOT EXISTS (SELECT 1 FROM edge_source_basis esb WHERE esb.edge_id = e.edge_id)
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-06 unsupported_edge (endpoint 밖 근거)
--   목적: 근거 fact는 양 끝 node의 구성 fact여야 한다. 예외: REVIEW_OF가 안핵 명령(CF035)을 절차 근거로
--         인용하는 경우(rule_set 'EXTRA_SUPPORT_OK') → INFO.
--   정상: ERROR 0행, INFO 1행(Python과 같음)
-- -----------------------------------------------------------------------------
SELECT 'unsupported_edge',
       CASE WHEN COUNT(CASE WHEN ok.member_id IS NULL THEN 1 END) > 0 THEN 'ERROR' ELSE 'INFO' END,
       c.edge_id,
       CASE WHEN COUNT(CASE WHEN ok.member_id IS NULL THEN 1 END) > 0
            THEN 'endpoint 밖의 근거 fact: '
            ELSE '절차 근거로 endpoint 밖 fact 인용: ' END
       || LISTAGG(c.support_id, ',') WITHIN GROUP (ORDER BY c.support_id)
  FROM v_edge_support_check c
  LEFT JOIN rule_set_member ok
         ON ok.rule_set = 'EXTRA_SUPPORT_OK'
        AND ok.member_id = c.support_id
        AND ok.member_group = c.edge_type
 WHERE c.in_endpoint = 'N'
 GROUP BY c.edge_id
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-07 unsupported_edge (근거가 endpoint와 무관)
--   목적: 근거 중 적어도 하나는 양 끝 node의 구성 근거여야 한다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'unsupported_edge', 'ERROR', e.edge_id, '근거 fact가 endpoint와 무관'
  FROM dag_edge e
 WHERE EXISTS (SELECT 1 FROM edge_source_basis esb WHERE esb.edge_id = e.edge_id)
   AND NOT EXISTS (SELECT 1 FROM v_edge_support_check c WHERE c.edge_id = e.edge_id AND c.in_endpoint = 'Y')
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-08 institutional_overreach
--   목적: 제도 compatibility만을 근거로 만든 edge 금지(제도는 사건을 만들지 않는다).
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'institutional_overreach', 'ERROR', f.edge_id, '제도 compatibility만으로 만든 edge'
  FROM v_edge_basis_flags f
 WHERE f.n_basis = 1
   AND f.has_institutional = 'Y'
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-09 environmental_leakage (environment → individual fact leakage)
--   목적: 환경 node는 판단·보고 node로 가는 CONTEXT_SUPPORTS의 출발점으로만 쓰고,
--         basis는 ENVIRONMENTAL_CONTEXT 하나뿐이며, 환경 basis는 사건 사이 edge에 쓰지 않는다.
--   정상: 0행 / 오류: 규칙을 어긴 edge
-- -----------------------------------------------------------------------------
SELECT 'environmental_leakage', 'ERROR', d.edge_id, '환경 node는 CONTEXT_SUPPORTS의 source로만 쓸 수 있음'
  FROM v_edge_detail d
 WHERE (d.src_layer = 'ENVIRONMENT' OR d.dst_layer = 'ENVIRONMENT')
   AND (d.edge_type <> 'CONTEXT_SUPPORTS' OR d.src_layer <> 'ENVIRONMENT')
UNION ALL
SELECT 'environmental_leakage', 'ERROR', d.edge_id, '환경 context가 판단/보고 아닌 node(' || d.dst_layer || ')로 연결'
  FROM v_edge_detail d
 WHERE (d.src_layer = 'ENVIRONMENT' OR d.dst_layer = 'ENVIRONMENT')
   AND d.dst_layer NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'JUDGMENT_LAYER')
UNION ALL
SELECT 'environmental_leakage', 'ERROR', d.edge_id, '환경 edge basis가 ENVIRONMENTAL_CONTEXT가 아님'
  FROM v_edge_detail d
  JOIN v_edge_basis_flags f ON f.edge_id = d.edge_id
 WHERE (d.src_layer = 'ENVIRONMENT' OR d.dst_layer = 'ENVIRONMENT')
   AND NOT (f.n_basis = 1 AND f.has_env_context = 'Y')
UNION ALL
SELECT 'environmental_leakage', 'ERROR', d.edge_id, '환경 basis를 사건 사이 edge에 사용'
  FROM v_edge_detail d
  JOIN v_edge_basis_flags f ON f.edge_id = d.edge_id
 WHERE f.has_env_context = 'Y'
   AND d.src_layer <> 'ENVIRONMENT'
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-10 temporal_inversion (reversed temporal edge)
--   목적: edge의 출발 node가 도착 node보다 늦게 시작하면 안 된다(src.t_min > dst.t_max 금지).
--         CONTRADICTS_AT_CLAIM_LEVEL은 방향이 '제시 순서'라 제외. 날짜가 NULL이면 비교하지 않는다.
--   정상: 0행 / 오류: (edge, src 시작일, dst 끝일)
-- -----------------------------------------------------------------------------
SELECT 'temporal_inversion', 'ERROR', d.edge_id,
       d.src || '(' || d.src_t_min || ') > ' || d.dst || '(' || d.dst_t_max || ')'
  FROM v_edge_detail d
 WHERE d.edge_type <> 'CONTRADICTS_AT_CLAIM_LEVEL'
   AND d.src_t_min > d.dst_t_max            -- NULL과의 비교는 UNKNOWN → 행이 걸러진다
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-11 testimony_to_fact (claim_level)
--   목적: 진술 node 사이의 사건 순서 edge는 '진술 내용 속 순서'(claim_level = True)로 표시해야 한다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'testimony_to_fact', 'ERROR', d.edge_id, '진술 node 사이 사건 순서 edge인데 claim_level 표시 없음'
  FROM v_edge_detail d
 WHERE d.src_layer IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'TESTIMONY_LAYER')
   AND d.dst_layer IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'TESTIMONY_LAYER')
   AND d.edge_type IN ('TEMPORAL_BEFORE', 'PROCEDURAL_NEXT', 'ORDER_TO_ACTION')
   AND d.claim_level = 'False'
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-12 causal_inflation (책임 귀속)
--   목적: RESPONSIBILITY_LINK는 국왕 판단 node(ROYAL_JUDGMENT)로만 들어간다(책임 ≠ 직접 인과).
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'causal_inflation', 'ERROR', d.edge_id, 'RESPONSIBILITY_LINK의 target이 royal judgment가 아님'
  FROM v_edge_detail d
 WHERE d.edge_type = 'RESPONSIBILITY_LINK'
   AND d.dst_layer <> 'ROYAL_JUDGMENT'
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-13 order_execution_conflation (self-loop)
--   목적: 자기 자신으로 가는 ORDER_TO_ACTION 금지(CHECK ck_dag_edge_no_self_loop도 막는다).
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'order_execution_conflation', 'ERROR', e.edge_id, '자기 자신으로의 ORDER_TO_ACTION'
  FROM dag_edge e
 WHERE e.edge_type = 'ORDER_TO_ACTION'
   AND e.src = e.dst
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-14 identity_forcing (unresolved identity forcing)
--   목적: 미확정 동일성에 기대는 node 쌍(rule_identity_sensitive_pair, 방향 무관)을 잇는 edge는
--         그 동일성을 condition으로 달아야 한다.
--   정상: 0행 / 오류: condition이 빠진 edge
-- -----------------------------------------------------------------------------
SELECT 'identity_forcing', 'ERROR', e.edge_id, rp.identity_id || ' 미확정 동일성에 기대는데 condition 누락'
  FROM dag_edge e
  JOIN rule_identity_sensitive_pair rp
    ON (rp.node_a = e.src AND rp.node_b = e.dst)
    OR (rp.node_a = e.dst AND rp.node_b = e.src)
  JOIN identity_register ir ON ir.identity_id = rp.identity_id
 WHERE ir.status = 'UNRESOLVED'
   AND NOT EXISTS (SELECT 1
                     FROM edge_identity_condition c
                    WHERE c.edge_id = e.edge_id
                      AND c.identity_id = rp.identity_id)
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-15 stale_identity_condition / identity_forcing(모르는 ID) / conditional_edge(UNRESOLVED)
--   목적: 사용자 확정(RESOLVED) ID가 condition에 남아 있으면 안 되고, 모르는 ID도 안 된다.
--         미확정 ID에 기대는 edge는 UNRESOLVED로 보고한다(오류 아님 — 조건부로만 성립).
--   기대: ERROR 0, UNRESOLVED 3 (OE010 ID08, OE071 ID06, OE080 ID07)
-- -----------------------------------------------------------------------------
SELECT CASE WHEN ir.identity_id IS NULL      THEN 'identity_forcing'
            WHEN ir.status = 'RESOLVED'      THEN 'stale_identity_condition'
            ELSE 'conditional_edge' END,
       CASE WHEN ir.identity_id IS NULL OR ir.status = 'RESOLVED' THEN 'ERROR' ELSE 'UNRESOLVED' END,
       c.edge_id,
       c.identity_id || CASE WHEN ir.identity_id IS NULL THEN ' 알 수 없는 identity'
                             WHEN ir.status = 'RESOLVED' THEN '는 사용자 확정(RESOLVED)인데 condition에 남아 있음'
                             ELSE ' 미확정 — edge는 condition으로만 성립 · unresolved_reason: ' || ir.unresolved_reason END
  FROM edge_identity_condition c
  LEFT JOIN identity_register ir ON ir.identity_id = c.identity_id
 WHERE ir.identity_id IS NULL
    OR ir.status IN ('RESOLVED', 'UNRESOLVED')
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-16 partial_tension (UNRESOLVED) / uncertainty_status 누락
--   목적: caution에 'PARTIAL'이 적힌 부분 충돌은 UNRESOLVED로 보존하고,
--         그런 CONTRADICTS edge는 uncertainty_status가 있어야 한다.
--   기대: UNRESOLVED 2 (OE007, OE062), ERROR 0
-- -----------------------------------------------------------------------------
SELECT 'partial_tension', 'UNRESOLVED', e.edge_id,
       NVL(e.uncertainty_status, 'PARTIAL') || ' — 원문 표현의 범위가 같은지 사료로 확정할 수 없어 보존'
  FROM dag_edge e
 WHERE INSTR(e.caution, 'PARTIAL') > 0
UNION ALL
SELECT 'uncertainty_status', 'ERROR', e.edge_id, '부분 충돌 edge에 uncertainty_status가 없음'
  FROM dag_edge e
 WHERE INSTR(e.caution, 'PARTIAL') > 0
   AND e.edge_type = 'CONTRADICTS_AT_CLAIM_LEVEL'
   AND e.uncertainty_status IS NULL
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-17 responsibility_to_causation / environment_to_individual_fact (edge 근거 문구)
--   목적: edge rationale·caution이 책임을 직접 사인으로, 환경을 개인 사실로 단정하지 않는다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT h.check_name, 'ERROR', h.edge_id, '''' || h.fragment || ''''
  FROM (SELECT p.check_name, e.edge_id,
               REGEXP_SUBSTR(e.rationale || ' ' || e.caution, p.oracle_regex) AS fragment
          FROM dag_edge e
          JOIN rule_text_pattern p
            ON p.check_name IN ('responsibility_to_causation', 'environment_to_individual_fact')) h
 WHERE h.fragment IS NOT NULL
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-18 causal_inflation (direct causal death edge 금지)
--   목적: 구순 관련 node(FORBIDDEN_DIRECT_SRC) → 김명신 사망·사인 node(FORBIDDEN_DIRECT_DST) 직접 edge 금지.
--         사망은 생물학 branch A와 절차·책임 branch B로만 이어진다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'causal_inflation', 'ERROR', e.edge_id, '구순 관련 node → 김명신 사망/사인 node 직접 연결 금지'
  FROM dag_edge e
  JOIN rule_set_member s ON s.rule_set = 'FORBIDDEN_DIRECT_SRC' AND s.member_id = e.src
  JOIN rule_set_member d ON d.rule_set = 'FORBIDDEN_DIRECT_DST' AND d.member_id = e.dst
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-19 missing_relation (필수 관계)
--   목적: 판단 번복·충돌·검토·책임 귀속의 필수 관계 17개가 그대로 있어야 한다.
--   정상: 0행 / 오류: 사라진 (src, dst, type)
-- -----------------------------------------------------------------------------
SELECT 'missing_relation', 'ERROR', r.src || '->' || r.dst, '필수 관계 ' || r.edge_type || ' 없음 (' || r.reason || ')'
  FROM rule_required_relation r
 WHERE NOT EXISTS (SELECT 1
                     FROM dag_edge e
                    WHERE e.src = r.src
                      AND e.dst = r.dst
                      AND e.edge_type = r.edge_type)
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-20 missing_relation (orphan node = 고립 node, WARN)
--   목적: edge가 하나도 없는 node는 그래프에서 떨어져 나간 것이다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'missing_relation', 'WARN', g.node_id, '고립 node'
  FROM v_node_degree g
 WHERE g.total_degree = 0
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-21 judgment_flattening
--   목적: 판단 node(5월·6월 판단, 홍대협·정조 판단 등)가 지워지면 안 된다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'judgment_flattening', 'ERROR', r.member_id, '판단 node 삭제됨'
  FROM rule_set_member r
 WHERE r.rule_set = 'JUDGMENT_NODE'
   AND NOT EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = r.member_id)
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-22 unsupported_node / latent_leak (node)
--   목적: 환경 node는 03 환경 행에서, 사건 node는 확정 사실에서 나와야 하고, 모두 OBSERVED여야 한다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'unsupported_node', 'ERROR', n.node_id,
       CASE WHEN n.layer = 'ENVIRONMENT' THEN '환경 행 없음' ELSE '근거 fact 없음' END
  FROM dag_node n
 WHERE (n.layer = 'ENVIRONMENT'
        AND NOT EXISTS (SELECT 1 FROM environment_context ec WHERE ec.env_id = n.env_id))
    OR (n.layer <> 'ENVIRONMENT' AND n.member_fact_ids IS NULL)
UNION ALL
SELECT 'latent_leak', 'ERROR', n.node_id, 'observed DAG에 OBSERVED 아닌 node'
  FROM dag_node n
 WHERE n.node_status <> 'OBSERVED'
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-23 institutional_overreach (feature link)
--   목적: 제도·환경 feature link는 사건을 만들지 않고(creates_event = NO), 대상이 실제로 있어야 한다.
--   정상: 0행
-- -----------------------------------------------------------------------------
SELECT 'institutional_overreach', 'ERROR', l.link_id,
       CASE WHEN l.creates_event <> 'NO' THEN 'feature link가 사건을 생성' ELSE '존재하지 않는 대상' END
  FROM node_feature_link l
 WHERE l.creates_event <> 'NO'
    OR (    NOT EXISTS (SELECT 1 FROM dag_node n WHERE n.node_id = l.target_id)
        AND NOT EXISTS (SELECT 1 FROM dag_edge e WHERE e.edge_id = l.target_id))
UNION ALL
-- -----------------------------------------------------------------------------
-- A2-24 acyclicity (cycle)
--   목적: observed graph는 DAG여야 한다. CONNECT BY NOCYCLE로 모든 node에서 내려가며
--         CONNECT_BY_ISCYCLE = 1(다음 단계가 조상으로 돌아감)인 행이 있으면 cycle이다.
--   정상: 0행 / 오류: 'graph' 한 행과 cycle을 닫는 node
-- -----------------------------------------------------------------------------
SELECT 'acyclicity', 'ERROR', 'graph', 'cycle: ' || MIN(cyc.path)
  FROM (SELECT SYS_CONNECT_BY_PATH(e.src, '>') || '>' || e.dst AS path
          FROM dag_edge e
         WHERE CONNECT_BY_ISCYCLE = 1
       CONNECT BY NOCYCLE PRIOR e.dst = e.src) cyc
HAVING COUNT(*) > 0;


-- 실행 예 ------------------------------------------------------------------------
SELECT check_name, severity, target, message
  FROM v_sql_audit_2
 ORDER BY DECODE(severity, 'ERROR', 1, 'WARN', 2, 'UNRESOLVED', 3, 4), check_name, target;

-- 기대: UNRESOLVED 5, INFO 1 (ERROR·WARN 없음)
SELECT severity, COUNT(*) AS n FROM v_sql_audit_2 GROUP BY severity ORDER BY severity;
