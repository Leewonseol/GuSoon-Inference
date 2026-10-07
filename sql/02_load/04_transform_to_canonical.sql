-- =============================================================================
-- 04_transform_to_canonical.sql — STG_*(문자 그대로) → canonical 표(형 변환·정규화·제약 검사)
-- -----------------------------------------------------------------------------
-- 선행: 01_schema/*.sql, 00_staging_tables.sql, STG 적재(방법 A/B/C 중 하나), 02_insert_examples.sql 1부
-- FK 부모 → 자식 순서로 넣는다. 제약 위반이 있으면 해당 INSERT가 실패한다(= 적재 단계 검증).
--
-- '|' 목록 펴기(정규화) 공통 기법 ― SQLD 계층형 질의의 응용
--   (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) : 1..20 행 생성기
--   REGEXP_COUNT(col, '[^|]+')       : 목록 원소 수
--   REGEXP_SUBSTR(col, '[^|]+', 1, n): n번째 원소
-- 목록 길이는 실측 최대 12(latent_bridges)라 20이면 충분하다. 03_load_validation.sql이 누락 없음을 확인한다.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- A. 원천 입력 pack
-- -----------------------------------------------------------------------------
INSERT INTO input_manifest (file_name, role, allowed_as_dag_input, purpose, important_rule)
SELECT file_name, role, allowed_as_dag_input, purpose, important_rule
  FROM stg_input_manifest;

INSERT INTO source_record
      (source_record_id, source_work, record_lunar_date, source_title, source_url,
       source_domain, source_tier, case_role, notes)
SELECT source_record_id, source_work, record_lunar_date, source_title, source_url,
       source_domain, source_tier, case_role, notes
  FROM stg_source_records;

INSERT INTO confirmed_fact
      (fact_id, chronology, record_lunar_date, occurrence_lunar_text, fact_category, confirmation_level,
       subject, confirmed_statement, underlying_claim_status, source_record_id, source_work, source_url,
       source_prop_ids, notes)
SELECT fact_id, chronology, record_lunar_date, occurrence_lunar_text, fact_category, confirmation_level,
       subject, confirmed_statement, underlying_claim_status, source_record_id, source_work, source_url,
       source_prop_ids, notes
  FROM stg_confirmed_facts;

INSERT INTO audit_proposition
      (prop_id, source_record_id, source_work, record_lunar_date, reporting_actor, attestation_mode,
       proposition_type, subject, predicate, object_or_content, occurrence_lunar_text, occurrence_precision,
       historical_place, place_status, named_entities, epistemic_scope, claim_topic, conflict_group,
       set_status, directness, source_url, notes)
SELECT prop_id, source_record_id, source_work, record_lunar_date, reporting_actor, attestation_mode,
       proposition_type, subject, predicate, object_or_content, occurrence_lunar_text, occurrence_precision,
       historical_place, place_status, named_entities, epistemic_scope, claim_topic, conflict_group,
       set_status, directness, source_url, notes
  FROM stg_audit_propositions;

-- confirmed_fact.source_prop_ids → fact_proposition
INSERT INTO fact_proposition (fact_id, prop_id, prop_seq)
SELECT cf.fact_id,
       REGEXP_SUBSTR(cf.source_prop_ids, '[^|]+', 1, seq.n) AS prop_id,
       seq.n
  FROM confirmed_fact cf
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(cf.source_prop_ids, '[^|]+');

INSERT INTO institutional_feature
      (feature_id, layer, feature_group, feature_name, operational_definition, encoding_type,
       suggested_values, model_role, interpretation, valid_from, valid_to, geo_scope, source_name,
       source_url, notes)
SELECT feature_id, layer, feature_group, feature_name, operational_definition, encoding_type,
       suggested_values, model_role, interpretation,
       TO_NUMBER(valid_from), TO_NUMBER(valid_to),
       geo_scope, source_name, source_url, notes
  FROM stg_institutional_features;

INSERT INTO environment_context
      (env_id, lunar_date, region_scope, context_type, attested_context, feature_name, value,
       model_role, source_url, notes)
SELECT env_id, lunar_date, region_scope, context_type, attested_context, feature_name,
       TO_NUMBER(value), model_role, source_url, notes
  FROM stg_environment_1793;

-- -----------------------------------------------------------------------------
-- B. Observed DAG
-- -----------------------------------------------------------------------------
INSERT INTO dag_node
      (node_id, node_status, layer, branch, title, summary, caution, member_fact_ids, member_clauses,
       confirmation_levels, epistemic_floor, claim_status, source_record_ids, source_prop_ids,
       attesting_actor, occurrence_text, t_min, t_max, record_lunar_date, grouping_rationale,
       identity_links, env_id)
SELECT node_id, node_status, layer, branch, title, summary, caution, member_fact_ids, member_clauses,
       confirmation_levels, epistemic_floor, claim_status, source_record_ids, source_prop_ids,
       attesting_actor, occurrence_text,
       TO_NUMBER(t_min), TO_NUMBER(t_max),          -- '' → NULL → TO_NUMBER(NULL) = NULL
       record_lunar_date, grouping_rationale, identity_links, env_id
  FROM stg_episode_nodes;

INSERT INTO episode_member (episode_id, fact_id, member_seq, clause)
SELECT episode_id, fact_id, TO_NUMBER(member_seq), clause
  FROM stg_episode_members;

INSERT INTO identity_register
      (identity_id, surface_a, surface_b, status, resolved_by, resolution_basis, unresolved_reason,
       model_relevance, manual_decision_required, review_decision, context, referenced_facts)
SELECT identity_id, surface_a, surface_b, status, resolved_by, resolution_basis, unresolved_reason,
       model_relevance, manual_decision_required, review_decision, context, referenced_facts
  FROM stg_identity_register;

INSERT INTO identity_fact_ref (identity_id, fact_id, ref_seq)
SELECT ir.identity_id,
       REGEXP_SUBSTR(ir.referenced_facts, '[^|]+', 1, seq.n),
       seq.n
  FROM identity_register ir
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(ir.referenced_facts, '[^|]+');   -- referenced_facts가 NULL이면 0행

INSERT INTO dag_edge
      (edge_id, src, dst, edge_type, basis, status, claim_level, condition, supporting, rationale,
       caution, uncertainty_status, review_decision)
SELECT edge_id, src, dst, edge_type, basis, status, claim_level, condition, supporting, rationale,
       caution, uncertainty_status, review_decision
  FROM stg_observed_edges;

INSERT INTO edge_basis_type (edge_id, basis_code, basis_seq)
SELECT e.edge_id, REGEXP_SUBSTR(e.basis, '[^|]+', 1, seq.n), seq.n
  FROM dag_edge e
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(e.basis, '[^|]+');

INSERT INTO edge_source_basis (edge_id, support_id, support_seq)     -- fact_id/env_id는 가상 컬럼(자동 계산)
SELECT e.edge_id, REGEXP_SUBSTR(e.supporting, '[^|]+', 1, seq.n), seq.n
  FROM dag_edge e
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(e.supporting, '[^|]+');

INSERT INTO edge_identity_condition (edge_id, identity_id)
SELECT e.edge_id, REGEXP_SUBSTR(e.condition, '[^|]+', 1, seq.n)
  FROM dag_edge e
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(e.condition, '[^|]+');

INSERT INTO node_feature_link
      (link_id, target_kind, target_id, feature_layer, feature_id, dimension, assessment,
       creates_event, rationale)
SELECT link_id, target_kind, target_id, feature_layer, feature_id, dimension, assessment,
       creates_event, rationale
  FROM stg_node_feature_links;

INSERT INTO dag_freeze
      (freeze_name, sha256, structure_sha256, topology_sha256, n_nodes, n_edges, n_episode_nodes,
       n_env_nodes, latent_count)
SELECT freeze_name, sha256, structure_sha256, topology_sha256,
       TO_NUMBER(n_nodes), TO_NUMBER(n_edges), TO_NUMBER(n_episode_nodes),
       TO_NUMBER(n_env_nodes), TO_NUMBER(latent_count)
  FROM stg_dag_freeze;

-- -----------------------------------------------------------------------------
-- C. Gap · LATENT 후보
-- -----------------------------------------------------------------------------
INSERT INTO gap
      (gap_id, title, gap_type, between_nodes, observed_anchor_facts, why_gap, gap_status, review_decision)
SELECT gap_id, title, gap_type, between_nodes, observed_anchor_facts, why_gap, gap_status, review_decision
  FROM stg_gaps;

INSERT INTO gap_anchor_node (gap_id, node_id, anchor_seq)
SELECT g.gap_id, REGEXP_SUBSTR(g.between_nodes, '[^|]+', 1, seq.n), seq.n
  FROM gap g
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(g.between_nodes, '[^|]+');

INSERT INTO latent_candidate
      (candidate_id, gap_id, status, form, label, description, source_consistency, temporal_fit,
       institutional_fit, role_fit, information_flow_fit, environmental_fit, contradiction_risk,
       n_assumptions, extra_assumptions, identity_conditions, overall, prune_decision, supports,
       conflicts, audit_attestation, support_basis, notes, observed_left, observed_right,
       latent_bridge_claim, bridge_directly_attested, endpoint_support, source_support,
       bridge_evidence, bridge_basis, evidence_grade, plausibility_grade, source_consistency_v1,
       overall_v1, reaudit_reason)
SELECT candidate_id, gap_id, status, form, label, description, source_consistency, temporal_fit,
       institutional_fit, role_fit, information_flow_fit, environmental_fit, contradiction_risk,
       TO_NUMBER(n_assumptions), extra_assumptions, identity_conditions, overall, prune_decision, supports,
       conflicts, audit_attestation, support_basis, notes, observed_left, observed_right,
       latent_bridge_claim, bridge_directly_attested, endpoint_support, source_support,
       bridge_evidence, bridge_basis, evidence_grade, plausibility_grade, source_consistency_v1,
       overall_v1, reaudit_reason
  FROM stg_latent_candidates;

INSERT INTO latent_element (element_id, candidate_id, kind, status, src, dst, edge_type, text)
SELECT element_id, candidate_id, kind, status, src, dst, edge_type, text
  FROM stg_latent_elements;

INSERT INTO candidate_identity_condition (candidate_id, identity_id)
SELECT c.candidate_id, REGEXP_SUBSTR(c.identity_conditions, '[^|]+', 1, seq.n)
  FROM latent_candidate c
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(c.identity_conditions, '[^|]+');

-- 두 목록(bridge_evidence, audit_attestation)을 UNION ALL로 한 표에 모은다
INSERT INTO candidate_evidence (candidate_id, evidence_role, evidence_id, evidence_seq)
SELECT c.candidate_id, 'BRIDGE_EVIDENCE', REGEXP_SUBSTR(c.bridge_evidence, '[^|]+', 1, seq.n), seq.n
  FROM latent_candidate c
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(c.bridge_evidence, '[^|]+')
UNION ALL
SELECT c.candidate_id, 'AUDIT_ATTESTATION', REGEXP_SUBSTR(c.audit_attestation, '[^|]+', 1, seq.n), seq.n
  FROM latent_candidate c
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(c.audit_attestation, '[^|]+');

INSERT INTO candidate_bridge_basis (candidate_id, basis_code)
SELECT c.candidate_id, REGEXP_SUBSTR(c.bridge_basis, '[^|]+', 1, seq.n)
  FROM latent_candidate c
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(c.bridge_basis, '[^|]+');

-- -----------------------------------------------------------------------------
-- D. Narrative world
-- -----------------------------------------------------------------------------
INSERT INTO narrative_world
      (world_id, name, status, latent_bridges, unresolved_gaps, institutional_fit, environmental_fit,
       n_assumptions, min_grade, main_assumptions, main_weaknesses, contradicted_evidence,
       story_implication, identity_conditions, resolved_identities, evidence_profile, work_role,
       story_question, difference, unique_bridges, narrative)
SELECT world_id, name, status, latent_bridges, unresolved_gaps, institutional_fit, environmental_fit,
       TO_NUMBER(n_assumptions), min_grade, main_assumptions, main_weaknesses, contradicted_evidence,
       story_implication, identity_conditions, resolved_identities, evidence_profile, work_role,
       story_question, difference, unique_bridges, narrative
  FROM stg_narrative_worlds;

-- world ↔ 후보: gap_id는 후보 표에서 가져온다(복합 FK가 짝을 다시 검사)
INSERT INTO world_candidate (world_id, candidate_id, gap_id, bridge_seq)
SELECT w.world_id, lc.candidate_id, lc.gap_id, b.n
  FROM narrative_world w
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) b
    ON b.n <= REGEXP_COUNT(w.latent_bridges, '[^|]+')
  JOIN latent_candidate lc
    ON lc.candidate_id = REGEXP_SUBSTR(w.latent_bridges, '[^|]+', 1, b.n);

INSERT INTO world_unresolved_gap (world_id, gap_id)
SELECT w.world_id, REGEXP_SUBSTR(w.unresolved_gaps, '[^|]+', 1, seq.n)
  FROM narrative_world w
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(w.unresolved_gaps, '[^|]+');

INSERT INTO world_identity (world_id, identity_id, identity_role)
SELECT w.world_id, REGEXP_SUBSTR(w.identity_conditions, '[^|]+', 1, seq.n), 'CONDITION'
  FROM narrative_world w
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(w.identity_conditions, '[^|]+')
UNION ALL
SELECT w.world_id, REGEXP_SUBSTR(w.resolved_identities, '[^|]+', 1, seq.n), 'RESOLVED'
  FROM narrative_world w
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(w.resolved_identities, '[^|]+');

-- -----------------------------------------------------------------------------
-- E. Mechanism Super-DAG
-- -----------------------------------------------------------------------------
INSERT INTO mechanism
      (mechanism_id, mechanism_name, easy_description, related_candidates, related_observed_nodes,
       required_inst_features, related_env_features, evidence_status, remarks, n_candidates, branch)
SELECT mechanism_id, mechanism_name, easy_description, related_candidates, related_observed_nodes,
       required_inst_features, related_env_features, evidence_status, remarks,
       TO_NUMBER(n_candidates), branch
  FROM stg_mechanism_definitions;

-- Super-DAG edge 'M → 후보 (INSTANTIATED_BY)'를 후보 → 메커니즘 매핑으로 뒤집는다
INSERT INTO candidate_mechanism (candidate_id, mechanism_id, mapping_role)
SELECT e.dst AS candidate_id,
       e.src AS mechanism_id,
       CASE e.edge_type
            WHEN 'INSTANTIATED_BY'           THEN 'PRIMARY'
            WHEN 'INSTANTIATED_BY_SECONDARY' THEN 'SECONDARY'
       END AS mapping_role
  FROM stg_sd_edges e
 WHERE e.edge_type IN ('INSTANTIATED_BY', 'INSTANTIATED_BY_SECONDARY');

-- 가로(M1..MB 컬럼) → 세로(world, mechanism) : UNPIVOT (Oracle 11g+)
INSERT INTO world_mechanism_config (world_id, mechanism_id, config_value, config_basis)
SELECT world_id, mechanism_id, config_value, config_basis
  FROM stg_world_mech_configs
UNPIVOT ((config_value, config_basis)
         FOR mechanism_id IN ((m1, m1_basis) AS 'M1',
                              (m2, m2_basis) AS 'M2',
                              (m3, m3_basis) AS 'M3',
                              (m4, m4_basis) AS 'M4',
                              (m5, m5_basis) AS 'M5',
                              (m6, m6_basis) AS 'M6',
                              (mb, mb_basis) AS 'MB'));

INSERT INTO mechanism_interaction
      (mechanism_a_id, mechanism_b_id, coexistence, reason, conflicting_items, explained_together,
       relation, cooccur_worlds)
SELECT mechanism_a_id, mechanism_b_id, coexistence, reason, conflicting_items, explained_together,
       relation, cooccur_worlds
  FROM stg_mech_interactions;

INSERT INTO structural_rule
      (var_id, gap, target, op, inputs, rule, rule_desc, constraint_text, input_candidates)
SELECT var_id, gap, target, op, inputs, rule, rule_desc, constraint_text, input_candidates
  FROM stg_structural_rules;

INSERT INTO mechanism_intervention
      (mechanism_id, variable, target, result, removed, remaining, affected_worlds, note)
SELECT mechanism, variable, target, result, removed, remaining, affected_worlds, note
  FROM stg_mech_interventions;

INSERT INTO intervention_candidate (mechanism_id, variable, candidate_id, effect)
SELECT mi.mechanism_id, mi.variable, REGEXP_SUBSTR(mi.removed, '[^|]+', 1, seq.n), 'REMOVED'
  FROM mechanism_intervention mi
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(mi.removed, '[^|]+')
UNION ALL
SELECT mi.mechanism_id, mi.variable, REGEXP_SUBSTR(mi.remaining, '[^|]+', 1, seq.n), 'REMAINING'
  FROM mechanism_intervention mi
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq
    ON seq.n <= REGEXP_COUNT(mi.remaining, '[^|]+');

INSERT INTO sd_node
      (node_id, sd_status, node_type, label, frozen_status, branch, mechanism, worlds, detail)
SELECT node_id, sd_status, node_type, label, frozen_status, branch, mechanism, worlds, detail
  FROM stg_sd_nodes;

INSERT INTO sd_edge (edge_id, src, dst, edge_type, sd_status, origin, note)
SELECT edge_id, src, dst, edge_type, sd_status, origin, note
  FROM stg_sd_edges;

-- -----------------------------------------------------------------------------
-- F. Audit 기록
-- -----------------------------------------------------------------------------
INSERT INTO warn_disposition
      (warning_id, audit_stage, affected_item, warning_type, original_text, generated_text, risk,
       disposition, justification, fixed_text, final_status, final_classification, unresolved_reason)
SELECT warning_id, audit_stage, affected_item, warning_type, original_text, generated_text, risk,
       disposition, justification, fixed_text, final_status, final_classification, unresolved_reason
  FROM stg_warn_dispositions;

INSERT INTO py_audit_finding (finding_seq, audit_name, check_name, severity, target, message)
SELECT TO_NUMBER(finding_seq), audit_name, check_name, severity, target, message
  FROM stg_py_audit_findings;

-- -----------------------------------------------------------------------------
-- 적재 기록 (DATE/TIMESTAMP 기본값이 자동으로 채워진다)
-- -----------------------------------------------------------------------------
INSERT INTO load_log (load_step, table_name, row_count)
SELECT 'TRANSFORM', table_name, row_count
  FROM (SELECT 'DAG_NODE'          AS table_name, COUNT(*) AS row_count FROM dag_node          UNION ALL
        SELECT 'DAG_EDGE',                        COUNT(*)              FROM dag_edge          UNION ALL
        SELECT 'CONFIRMED_FACT',                  COUNT(*)              FROM confirmed_fact    UNION ALL
        SELECT 'LATENT_CANDIDATE',                COUNT(*)              FROM latent_candidate  UNION ALL
        SELECT 'NARRATIVE_WORLD',                 COUNT(*)              FROM narrative_world   UNION ALL
        SELECT 'SD_NODE',                         COUNT(*)              FROM sd_node           UNION ALL
        SELECT 'SD_EDGE',                         COUNT(*)              FROM sd_edge);

COMMIT;
