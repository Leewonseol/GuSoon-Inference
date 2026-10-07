-- =============================================================================
-- 02_constraints.sql — PK / UNIQUE / FK / CHECK (모두 이름 붙인 제약조건)
-- -----------------------------------------------------------------------------
-- 이름 규칙: PK_표, UK_표_내용, FK_자식_부모(또는 의미), CK_표_내용
-- CHECK의 값 목록은 모두 canonical 데이터·Python 코드에 이미 있는 값이다.
-- 새 규칙을 만들지 않았다. 각 CHECK 옆 주석에 출처를 적었다.
-- 규칙 참조표(rule_*)는 데이터 표에 FK를 걸지 않는다: 규칙은 데이터와 독립이어야
-- '필수 node가 사라졌다' 같은 결함을 audit SQL이 잡을 수 있다.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- A. 원천 입력 pack
-- -----------------------------------------------------------------------------
ALTER TABLE input_manifest ADD CONSTRAINT pk_input_manifest PRIMARY KEY (file_name);
ALTER TABLE input_manifest ADD CONSTRAINT ck_manifest_role
    CHECK (role IN ('PRIMARY_CASE_INPUT', 'INSTITUTIONAL_CONSTRAINT', 'EXTERNAL_CONTEXT',
                    'PROVENANCE', 'AUDIT_ONLY'));
ALTER TABLE input_manifest ADD CONSTRAINT ck_manifest_dag_input
    CHECK (allowed_as_dag_input IN ('YES', 'NO'));
-- manifest 규칙: AUDIT_ONLY 파일은 DAG 입력이 아니다 (00_INPUT_MANIFEST.csv)
ALTER TABLE input_manifest ADD CONSTRAINT ck_manifest_audit_only
    CHECK (role <> 'AUDIT_ONLY' OR allowed_as_dag_input = 'NO');

ALTER TABLE source_record ADD CONSTRAINT pk_source_record PRIMARY KEY (source_record_id);
ALTER TABLE source_record ADD CONSTRAINT uk_source_record_url UNIQUE (source_url);
ALTER TABLE source_record ADD CONSTRAINT ck_source_record_date
    CHECK (REGEXP_LIKE(record_lunar_date, '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'));

ALTER TABLE ref_confirmation_level ADD CONSTRAINT pk_ref_confirmation_level PRIMARY KEY (confirmation_level);
ALTER TABLE ref_confirmation_level ADD CONSTRAINT ck_ref_conf_rank CHECK (epistemic_rank BETWEEN 0 AND 4);
ALTER TABLE ref_confirmation_level ADD CONSTRAINT ck_ref_conf_family
    CHECK (epistemic_family IN ('TESTIMONY', 'IDENT', 'OFFICIAL', 'ROYAL', 'COURT', 'MIXED'));

ALTER TABLE confirmed_fact ADD CONSTRAINT pk_confirmed_fact PRIMARY KEY (fact_id);
ALTER TABLE confirmed_fact ADD CONSTRAINT fk_cf_source_record
    FOREIGN KEY (source_record_id) REFERENCES source_record (source_record_id);
ALTER TABLE confirmed_fact ADD CONSTRAINT fk_cf_confirmation_level
    FOREIGN KEY (confirmation_level) REFERENCES ref_confirmation_level (confirmation_level);
ALTER TABLE confirmed_fact ADD CONSTRAINT ck_cf_record_date
    CHECK (REGEXP_LIKE(record_lunar_date, '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'));
-- 01_confirmed_facts.csv에 나오는 underlying_claim_status 전체
ALTER TABLE confirmed_fact ADD CONSTRAINT ck_cf_claim_status
    CHECK (underlying_claim_status IN (
        'NOT_INDEPENDENTLY_VERIFIED', 'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
        'DIRECTLY_DOCUMENTED_SOURCE_IDENTIFICATION', 'FACT_OF_OFFICIAL_EVALUATION',
        'FACT_OF_OFFICIAL_FINDING', 'FACT_OF_OFFICIAL_JUDGMENT', 'FACT_OF_OFFICIAL_REPORT',
        'FACT_OF_ROYAL_JUDGMENT'));

ALTER TABLE audit_proposition ADD CONSTRAINT pk_audit_proposition PRIMARY KEY (prop_id);
ALTER TABLE audit_proposition ADD CONSTRAINT fk_prop_source_record
    FOREIGN KEY (source_record_id) REFERENCES source_record (source_record_id);
ALTER TABLE audit_proposition ADD CONSTRAINT ck_prop_type
    CHECK (proposition_type IN ('ACTION', 'ASSERTION', 'JUDGMENT', 'ORDER', 'STATE'));
ALTER TABLE audit_proposition ADD CONSTRAINT ck_prop_precision
    CHECK (occurrence_precision IN ('AFTER_EARLY_MONTH', 'DAY', 'DAY_NIGHT', 'EARLY_MONTH',
                                    'OVERNIGHT', 'RELATIVE_ONLY', 'UNKNOWN', 'UNSPECIFIED'));
ALTER TABLE audit_proposition ADD CONSTRAINT ck_prop_place_status
    CHECK (place_status IN ('EXPLICIT', 'EXPLICIT_IN_THIS_SOURCE', 'SOURCE_ATTESTED', 'UNSPECIFIED'));
ALTER TABLE audit_proposition ADD CONSTRAINT ck_prop_set_status
    CHECK (set_status IN ('NOT_APPLICABLE', 'OPEN_SET', 'OPEN_SET_EXPLICIT_MEMBERS'));
ALTER TABLE audit_proposition ADD CONSTRAINT ck_prop_directness
    CHECK (directness IN ('DIRECT', 'DIRECTLY_STATED', 'NESTED'));

ALTER TABLE fact_proposition ADD CONSTRAINT pk_fact_proposition PRIMARY KEY (fact_id, prop_id);
ALTER TABLE fact_proposition ADD CONSTRAINT fk_factprop_fact
    FOREIGN KEY (fact_id) REFERENCES confirmed_fact (fact_id);
ALTER TABLE fact_proposition ADD CONSTRAINT fk_factprop_prop
    FOREIGN KEY (prop_id) REFERENCES audit_proposition (prop_id);

ALTER TABLE institutional_feature ADD CONSTRAINT pk_institutional_feature PRIMARY KEY (feature_id);
ALTER TABLE institutional_feature ADD CONSTRAINT ck_inst_encoding
    CHECK (encoding_type IN ('binary', 'categorical'));
ALTER TABLE institutional_feature ADD CONSTRAINT ck_inst_valid_range
    CHECK (valid_from <= valid_to);

ALTER TABLE environment_context ADD CONSTRAINT pk_environment_context PRIMARY KEY (env_id);
ALTER TABLE environment_context ADD CONSTRAINT uk_env_feature_name UNIQUE (feature_name);
ALTER TABLE environment_context ADD CONSTRAINT ck_env_date
    CHECK (REGEXP_LIKE(lunar_date, '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'));

-- -----------------------------------------------------------------------------
-- B. Observed DAG
-- -----------------------------------------------------------------------------
ALTER TABLE dag_node ADD CONSTRAINT pk_dag_node PRIMARY KEY (node_id);
-- Audit 2 latent_leak / Audit 3 latent_as_observed: 동결 DAG에는 OBSERVED node만 있다
ALTER TABLE dag_node ADD CONSTRAINT ck_dag_node_status CHECK (node_status = 'OBSERVED');
ALTER TABLE dag_node ADD CONSTRAINT ck_dag_node_layer
    CHECK (layer IN ('COURT_ACTION', 'ENVIRONMENT', 'INSPECTOR_REPORT', 'NESTED_TESTIMONY',
                     'OFFICIAL_ACTION', 'OFFICIAL_EVALUATION', 'OFFICIAL_FINDING', 'OFFICIAL_REPORT',
                     'ROYAL_JUDGMENT', 'ROYAL_JUDGMENT_AND_ORDER', 'ROYAL_ORDER', 'TESTIMONY'));
-- 시간 표기: 음력 MMDD 정수(audits.py parse_md: month*100 + day)
ALTER TABLE dag_node ADD CONSTRAINT ck_dag_node_tmin
    CHECK (t_min IS NULL OR (TRUNC(t_min / 100) BETWEEN 1 AND 12 AND MOD(t_min, 100) BETWEEN 1 AND 30));
ALTER TABLE dag_node ADD CONSTRAINT ck_dag_node_tmax
    CHECK (t_max IS NULL OR (TRUNC(t_max / 100) BETWEEN 1 AND 12 AND MOD(t_max, 100) BETWEEN 1 AND 30));
ALTER TABLE dag_node ADD CONSTRAINT ck_dag_node_trange
    CHECK (t_min IS NULL OR t_max IS NULL OR t_min <= t_max);
-- Audit 2 unsupported_node: 환경 node는 env_id로, 사건 node는 구성 fact로 근거를 가진다
ALTER TABLE dag_node ADD CONSTRAINT ck_dag_node_env
    CHECK ((layer = 'ENVIRONMENT' AND env_id IS NOT NULL)
        OR (layer <> 'ENVIRONMENT' AND env_id IS NULL AND member_fact_ids IS NOT NULL));
ALTER TABLE dag_node ADD CONSTRAINT fk_dag_node_env
    FOREIGN KEY (env_id) REFERENCES environment_context (env_id);

ALTER TABLE episode_member ADD CONSTRAINT pk_episode_member PRIMARY KEY (episode_id, fact_id);
ALTER TABLE episode_member ADD CONSTRAINT uk_episode_member_seq UNIQUE (episode_id, member_seq);
ALTER TABLE episode_member ADD CONSTRAINT fk_epmember_node
    FOREIGN KEY (episode_id) REFERENCES dag_node (node_id);
ALTER TABLE episode_member ADD CONSTRAINT fk_epmember_fact
    FOREIGN KEY (fact_id) REFERENCES confirmed_fact (fact_id);

ALTER TABLE identity_register ADD CONSTRAINT pk_identity_register PRIMARY KEY (identity_id);
ALTER TABLE identity_register ADD CONSTRAINT ck_identity_status
    CHECK (status IN ('RESOLVED', 'UNRESOLVED', 'ACCEPTED_BY_PROVENANCE', 'DOCUMENTED'));
ALTER TABLE identity_register ADD CONSTRAINT ck_identity_resolved_by CHECK (resolved_by IN ('USER'));
ALTER TABLE identity_register ADD CONSTRAINT ck_identity_manual CHECK (manual_decision_required IN ('YES', 'NO'));
-- Audit 1 identity_resolution: RESOLVED는 사용자 확정(resolved_by=USER)과 근거가 있어야 한다
ALTER TABLE identity_register ADD CONSTRAINT ck_identity_resolution
    CHECK (status <> 'RESOLVED' OR (resolved_by = 'USER' AND resolution_basis IS NOT NULL));

ALTER TABLE identity_fact_ref ADD CONSTRAINT pk_identity_fact_ref PRIMARY KEY (identity_id, fact_id);
ALTER TABLE identity_fact_ref ADD CONSTRAINT fk_idref_identity
    FOREIGN KEY (identity_id) REFERENCES identity_register (identity_id);
ALTER TABLE identity_fact_ref ADD CONSTRAINT fk_idref_fact
    FOREIGN KEY (fact_id) REFERENCES confirmed_fact (fact_id);

ALTER TABLE dag_edge ADD CONSTRAINT pk_dag_edge PRIMARY KEY (edge_id);
ALTER TABLE dag_edge ADD CONSTRAINT fk_dag_edge_src FOREIGN KEY (src) REFERENCES dag_node (node_id);
ALTER TABLE dag_edge ADD CONSTRAINT fk_dag_edge_dst FOREIGN KEY (dst) REFERENCES dag_node (node_id);
-- stage2_graph.py EDGE_TYPES (CAUSES는 목록에 없다 → CAUSES edge는 넣을 수 없다)
ALTER TABLE dag_edge ADD CONSTRAINT ck_dag_edge_type
    CHECK (edge_type IN ('TEMPORAL_BEFORE', 'PROCEDURAL_NEXT', 'INFORMATION_FLOW', 'ORDER_TO_ACTION',
                         'REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL', 'RESPONSIBILITY_LINK',
                         'CONTEXT_SUPPORTS'));
-- Audit 2 latent_leak: observed DAG edge는 OBSERVED 또는 DERIVED
ALTER TABLE dag_edge ADD CONSTRAINT ck_dag_edge_status CHECK (status IN ('OBSERVED', 'DERIVED'));
ALTER TABLE dag_edge ADD CONSTRAINT ck_dag_edge_claim_level CHECK (claim_level IN ('True', 'False'));
ALTER TABLE dag_edge ADD CONSTRAINT ck_dag_edge_uncertainty
    CHECK (uncertainty_status IN ('PARTIAL_CONFLICT', 'UNRESOLVED_SCOPE', 'CONDITIONAL_UNRESOLVED_IDENTITY'));
-- Audit 2 acyclicity(자기 자신으로 가는 edge도 cycle) · order_execution_conflation
ALTER TABLE dag_edge ADD CONSTRAINT ck_dag_edge_no_self_loop CHECK (src <> dst);

ALTER TABLE edge_basis_type ADD CONSTRAINT pk_edge_basis_type PRIMARY KEY (edge_id, basis_code);
ALTER TABLE edge_basis_type ADD CONSTRAINT fk_edgebasis_edge FOREIGN KEY (edge_id) REFERENCES dag_edge (edge_id);
-- stage2_graph.py BASES
ALTER TABLE edge_basis_type ADD CONSTRAINT ck_edgebasis_code
    CHECK (basis_code IN ('SOURCE_DIRECT', 'TEMPORAL', 'PROCEDURAL', 'INFORMATION_FLOW',
                          'INSTITUTIONAL_COMPATIBILITY', 'ENVIRONMENTAL_CONTEXT'));

ALTER TABLE edge_source_basis ADD CONSTRAINT pk_edge_source_basis PRIMARY KEY (edge_id, support_id);
ALTER TABLE edge_source_basis ADD CONSTRAINT fk_esb_edge FOREIGN KEY (edge_id) REFERENCES dag_edge (edge_id);
ALTER TABLE edge_source_basis ADD CONSTRAINT fk_esb_fact FOREIGN KEY (fact_id) REFERENCES confirmed_fact (fact_id);
ALTER TABLE edge_source_basis ADD CONSTRAINT fk_esb_env FOREIGN KEY (env_id) REFERENCES environment_context (env_id);
-- 배타적 관계(arc): 근거는 confirmed fact 또는 환경 행, 둘 중 정확히 하나
ALTER TABLE edge_source_basis ADD CONSTRAINT ck_esb_arc
    CHECK (SUBSTR(support_id, 1, 2) = 'CF' OR SUBSTR(support_id, 1, 1) = 'E');

ALTER TABLE edge_identity_condition ADD CONSTRAINT pk_edge_identity_condition PRIMARY KEY (edge_id, identity_id);
ALTER TABLE edge_identity_condition ADD CONSTRAINT fk_eic_edge FOREIGN KEY (edge_id) REFERENCES dag_edge (edge_id);
ALTER TABLE edge_identity_condition ADD CONSTRAINT fk_eic_identity
    FOREIGN KEY (identity_id) REFERENCES identity_register (identity_id);

ALTER TABLE node_feature_link ADD CONSTRAINT pk_node_feature_link PRIMARY KEY (link_id);
ALTER TABLE node_feature_link ADD CONSTRAINT ck_nfl_target_kind CHECK (target_kind IN ('NODE', 'EDGE'));
ALTER TABLE node_feature_link ADD CONSTRAINT ck_nfl_feature_layer CHECK (feature_layer IN ('INSTITUTIONAL', 'ENVIRONMENT'));
ALTER TABLE node_feature_link ADD CONSTRAINT ck_nfl_dimension
    CHECK (dimension IN ('environmental_fit', 'information_flow_compatible', 'jurisdictionally_possible',
                         'legal_available', 'procedure_available', 'review_available', 'role_compatible'));
ALTER TABLE node_feature_link ADD CONSTRAINT ck_nfl_assessment
    CHECK (assessment IN ('COMPATIBLE', 'COMPATIBLE_WITH_CAVEAT', 'LOW', 'UNDETERMINED'));
-- manifest·Audit 2 institutional_overreach: 피쳐는 사건을 만들지 않는다
ALTER TABLE node_feature_link ADD CONSTRAINT ck_nfl_creates_event CHECK (creates_event = 'NO');
ALTER TABLE node_feature_link ADD CONSTRAINT fk_nfl_node FOREIGN KEY (target_node_id) REFERENCES dag_node (node_id);
ALTER TABLE node_feature_link ADD CONSTRAINT fk_nfl_edge FOREIGN KEY (target_edge_id) REFERENCES dag_edge (edge_id);
ALTER TABLE node_feature_link ADD CONSTRAINT fk_nfl_inst
    FOREIGN KEY (inst_feature_id) REFERENCES institutional_feature (feature_id);
ALTER TABLE node_feature_link ADD CONSTRAINT fk_nfl_env
    FOREIGN KEY (env_feature_id) REFERENCES environment_context (env_id);

ALTER TABLE dag_freeze ADD CONSTRAINT pk_dag_freeze PRIMARY KEY (freeze_name);
ALTER TABLE dag_freeze ADD CONSTRAINT ck_dag_freeze_hash CHECK (REGEXP_LIKE(sha256, '^[0-9a-f]{64}$'));
-- build.py: 동결 DAG의 latent_count는 0
ALTER TABLE dag_freeze ADD CONSTRAINT ck_dag_freeze_latent CHECK (latent_count = 0);

-- -----------------------------------------------------------------------------
-- C. Gap · LATENT 후보
-- -----------------------------------------------------------------------------
ALTER TABLE gap ADD CONSTRAINT pk_gap PRIMARY KEY (gap_id);
ALTER TABLE gap ADD CONSTRAINT ck_gap_status CHECK (gap_status IN ('OPEN', 'OPEN_UNRESOLVED'));

ALTER TABLE gap_anchor_node ADD CONSTRAINT pk_gap_anchor_node PRIMARY KEY (gap_id, node_id);
ALTER TABLE gap_anchor_node ADD CONSTRAINT fk_gapanchor_gap FOREIGN KEY (gap_id) REFERENCES gap (gap_id);
ALTER TABLE gap_anchor_node ADD CONSTRAINT fk_gapanchor_node FOREIGN KEY (node_id) REFERENCES dag_node (node_id);

ALTER TABLE latent_candidate ADD CONSTRAINT pk_latent_candidate PRIMARY KEY (candidate_id);
-- world_candidate의 복합 FK 대상(후보와 gap의 짝)
ALTER TABLE latent_candidate ADD CONSTRAINT uk_latent_candidate_gap UNIQUE (candidate_id, gap_id);
ALTER TABLE latent_candidate ADD CONSTRAINT fk_candidate_gap FOREIGN KEY (gap_id) REFERENCES gap (gap_id);
-- Audit 3 latent_as_observed: 후보는 언제나 LATENT
ALTER TABLE latent_candidate ADD CONSTRAINT ck_candidate_status CHECK (status = 'LATENT');
ALTER TABLE latent_candidate ADD CONSTRAINT ck_candidate_form CHECK (form IN ('SINGLE', 'MINI_DAG'));
-- 등급 어휘: stage4_latent.py SCORE(INCOMPATIBLE/LOW/MEDIUM/HIGH), EVIDENCE_SCORE(NONE/LOW/MEDIUM/HIGH), 'N/A'
ALTER TABLE latent_candidate ADD CONSTRAINT ck_candidate_grades
    CHECK (    source_consistency    IN ('HIGH', 'MEDIUM', 'LOW', 'NONE')
           AND temporal_fit          IN ('HIGH', 'MEDIUM', 'LOW')
           AND institutional_fit     IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE', 'N/A')
           AND role_fit              IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE', 'N/A')
           AND information_flow_fit  IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE', 'N/A')
           AND environmental_fit     IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE', 'N/A')
           AND contradiction_risk    IN ('HIGH', 'MEDIUM', 'LOW')
           AND overall               IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE')
           AND source_support        IN ('HIGH', 'MEDIUM', 'LOW', 'NONE')
           AND evidence_grade        IN ('HIGH', 'MEDIUM', 'LOW', 'NONE')
           AND plausibility_grade    IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE')
           AND source_consistency_v1 IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE')
           AND overall_v1            IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE'));
ALTER TABLE latent_candidate ADD CONSTRAINT ck_candidate_attested
    CHECK (bridge_directly_attested IN ('YES', 'NO', 'PARTIAL'));
ALTER TABLE latent_candidate ADD CONSTRAINT ck_candidate_support_basis
    CHECK (support_basis IN ('SOURCE_DIRECT', 'INSTITUTIONAL_COMPATIBILITY', 'ENVIRONMENTAL_CONTEXT', 'NONE'));
ALTER TABLE latent_candidate ADD CONSTRAINT ck_candidate_n_assumptions CHECK (n_assumptions >= 0);

ALTER TABLE latent_element ADD CONSTRAINT pk_latent_element PRIMARY KEY (element_id);
ALTER TABLE latent_element ADD CONSTRAINT fk_latelem_candidate
    FOREIGN KEY (candidate_id) REFERENCES latent_candidate (candidate_id);
ALTER TABLE latent_element ADD CONSTRAINT ck_latelem_kind CHECK (kind IN ('node', 'edge'));
ALTER TABLE latent_element ADD CONSTRAINT ck_latelem_status CHECK (status = 'LATENT');
-- node 행은 서술(text)만, edge 행은 끝점·type만 가진다 (latent_elements.csv 구조)
ALTER TABLE latent_element ADD CONSTRAINT ck_latelem_shape
    CHECK ((kind = 'node' AND src IS NULL AND dst IS NULL AND edge_type IS NULL AND text IS NOT NULL)
        OR (kind = 'edge' AND src IS NOT NULL AND dst IS NOT NULL AND edge_type IS NOT NULL));
ALTER TABLE latent_element ADD CONSTRAINT ck_latelem_edge_type
    CHECK (edge_type IN ('TEMPORAL_BEFORE', 'PROCEDURAL_NEXT', 'INFORMATION_FLOW', 'ORDER_TO_ACTION',
                         'REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL', 'RESPONSIBILITY_LINK',
                         'CONTEXT_SUPPORTS'));

ALTER TABLE candidate_identity_condition ADD CONSTRAINT pk_candidate_identity_condition
    PRIMARY KEY (candidate_id, identity_id);
ALTER TABLE candidate_identity_condition ADD CONSTRAINT fk_cic_candidate
    FOREIGN KEY (candidate_id) REFERENCES latent_candidate (candidate_id);
ALTER TABLE candidate_identity_condition ADD CONSTRAINT fk_cic_identity
    FOREIGN KEY (identity_id) REFERENCES identity_register (identity_id);

ALTER TABLE candidate_evidence ADD CONSTRAINT pk_candidate_evidence
    PRIMARY KEY (candidate_id, evidence_role, evidence_id);
ALTER TABLE candidate_evidence ADD CONSTRAINT fk_cev_candidate
    FOREIGN KEY (candidate_id) REFERENCES latent_candidate (candidate_id);
ALTER TABLE candidate_evidence ADD CONSTRAINT fk_cev_fact FOREIGN KEY (fact_id) REFERENCES confirmed_fact (fact_id);
ALTER TABLE candidate_evidence ADD CONSTRAINT fk_cev_prop FOREIGN KEY (prop_id) REFERENCES audit_proposition (prop_id);
ALTER TABLE candidate_evidence ADD CONSTRAINT ck_cev_role CHECK (evidence_role IN ('BRIDGE_EVIDENCE', 'AUDIT_ATTESTATION'));
ALTER TABLE candidate_evidence ADD CONSTRAINT ck_cev_arc
    CHECK (SUBSTR(evidence_id, 1, 2) = 'CF' OR SUBSTR(evidence_id, 1, 3) = 'V3P');

ALTER TABLE candidate_bridge_basis ADD CONSTRAINT pk_candidate_bridge_basis PRIMARY KEY (candidate_id, basis_code);
ALTER TABLE candidate_bridge_basis ADD CONSTRAINT fk_cbb_candidate
    FOREIGN KEY (candidate_id) REFERENCES latent_candidate (candidate_id);
ALTER TABLE candidate_bridge_basis ADD CONSTRAINT ck_cbb_code
    CHECK (basis_code IN ('AUDIT_ONLY', 'ENDPOINT_ONLY', 'CONFIRMED_NON_ENDPOINT', 'TEMPORAL',
                          'ENVIRONMENT', 'INSTITUTIONAL', 'NONE'));

-- -----------------------------------------------------------------------------
-- D. Narrative world
-- -----------------------------------------------------------------------------
ALTER TABLE narrative_world ADD CONSTRAINT pk_narrative_world PRIMARY KEY (world_id);
ALTER TABLE narrative_world ADD CONSTRAINT ck_world_status CHECK (status IN ('COMPETING_EXPLANATION', 'REJECTED'));
ALTER TABLE narrative_world ADD CONSTRAINT ck_world_grades
    CHECK (    institutional_fit IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE')
           AND environmental_fit IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE')
           AND min_grade         IN ('HIGH', 'MEDIUM', 'LOW', 'INCOMPATIBLE'));

ALTER TABLE world_candidate ADD CONSTRAINT pk_world_candidate PRIMARY KEY (world_id, candidate_id);
-- Audit 3 world_integrity "한 gap에 후보 2개 이상" 금지를 제약으로
ALTER TABLE world_candidate ADD CONSTRAINT uk_world_candidate_gap UNIQUE (world_id, gap_id);
ALTER TABLE world_candidate ADD CONSTRAINT fk_wc_world FOREIGN KEY (world_id) REFERENCES narrative_world (world_id);
-- 복합 FK: 후보와 gap의 짝이 latent_candidate와 일치해야 한다
ALTER TABLE world_candidate ADD CONSTRAINT fk_wc_candidate_gap
    FOREIGN KEY (candidate_id, gap_id) REFERENCES latent_candidate (candidate_id, gap_id);

ALTER TABLE world_unresolved_gap ADD CONSTRAINT pk_world_unresolved_gap PRIMARY KEY (world_id, gap_id);
ALTER TABLE world_unresolved_gap ADD CONSTRAINT fk_wug_world FOREIGN KEY (world_id) REFERENCES narrative_world (world_id);
ALTER TABLE world_unresolved_gap ADD CONSTRAINT fk_wug_gap FOREIGN KEY (gap_id) REFERENCES gap (gap_id);

ALTER TABLE world_identity ADD CONSTRAINT pk_world_identity PRIMARY KEY (world_id, identity_id, identity_role);
ALTER TABLE world_identity ADD CONSTRAINT fk_wi_world FOREIGN KEY (world_id) REFERENCES narrative_world (world_id);
ALTER TABLE world_identity ADD CONSTRAINT fk_wi_identity FOREIGN KEY (identity_id) REFERENCES identity_register (identity_id);
ALTER TABLE world_identity ADD CONSTRAINT ck_wi_role CHECK (identity_role IN ('CONDITION', 'RESOLVED'));

-- -----------------------------------------------------------------------------
-- E. Mechanism Super-DAG
-- -----------------------------------------------------------------------------
ALTER TABLE mechanism ADD CONSTRAINT pk_mechanism PRIMARY KEY (mechanism_id);
ALTER TABLE mechanism ADD CONSTRAINT uk_mechanism_name UNIQUE (mechanism_name);
ALTER TABLE mechanism ADD CONSTRAINT ck_mechanism_branch CHECK (branch IN ('A_BIOLOGICAL', 'B_PROCEDURAL', 'REVIEW'));

ALTER TABLE candidate_mechanism ADD CONSTRAINT pk_candidate_mechanism PRIMARY KEY (candidate_id, mechanism_id);
ALTER TABLE candidate_mechanism ADD CONSTRAINT fk_cm_candidate
    FOREIGN KEY (candidate_id) REFERENCES latent_candidate (candidate_id);
ALTER TABLE candidate_mechanism ADD CONSTRAINT fk_cm_mechanism FOREIGN KEY (mechanism_id) REFERENCES mechanism (mechanism_id);
ALTER TABLE candidate_mechanism ADD CONSTRAINT ck_cm_role CHECK (mapping_role IN ('PRIMARY', 'SECONDARY'));

ALTER TABLE world_mechanism_config ADD CONSTRAINT pk_world_mechanism_config PRIMARY KEY (world_id, mechanism_id);
ALTER TABLE world_mechanism_config ADD CONSTRAINT fk_wmc_world FOREIGN KEY (world_id) REFERENCES narrative_world (world_id);
ALTER TABLE world_mechanism_config ADD CONSTRAINT fk_wmc_mechanism FOREIGN KEY (mechanism_id) REFERENCES mechanism (mechanism_id);
-- Audit 4 config_value
ALTER TABLE world_mechanism_config ADD CONSTRAINT ck_wmc_value CHECK (config_value IN ('ON', 'OFF', 'PARTIAL', 'UNSPECIFIED'));

ALTER TABLE mechanism_interaction ADD CONSTRAINT pk_mechanism_interaction PRIMARY KEY (mechanism_a_id, mechanism_b_id);
ALTER TABLE mechanism_interaction ADD CONSTRAINT fk_mi_a FOREIGN KEY (mechanism_a_id) REFERENCES mechanism (mechanism_id);
ALTER TABLE mechanism_interaction ADD CONSTRAINT fk_mi_b FOREIGN KEY (mechanism_b_id) REFERENCES mechanism (mechanism_id);
ALTER TABLE mechanism_interaction ADD CONSTRAINT ck_mi_pair CHECK (mechanism_a_id <> mechanism_b_id);
ALTER TABLE mechanism_interaction ADD CONSTRAINT ck_mi_coexistence
    CHECK (coexistence IN ('COMPATIBLE', 'PARTIALLY_COMPATIBLE', 'INCOMPATIBLE', 'UNKNOWN'));

ALTER TABLE structural_rule ADD CONSTRAINT pk_structural_rule PRIMARY KEY (var_id);
ALTER TABLE structural_rule ADD CONSTRAINT ck_srule_op CHECK (op IN ('OR', 'AND', 'XOR', 'ANCHORED'));

ALTER TABLE mechanism_intervention ADD CONSTRAINT pk_mechanism_intervention PRIMARY KEY (mechanism_id, variable);
ALTER TABLE mechanism_intervention ADD CONSTRAINT fk_mint_mechanism FOREIGN KEY (mechanism_id) REFERENCES mechanism (mechanism_id);
ALTER TABLE mechanism_intervention ADD CONSTRAINT fk_mint_variable FOREIGN KEY (variable) REFERENCES structural_rule (var_id);
ALTER TABLE mechanism_intervention ADD CONSTRAINT fk_mint_target FOREIGN KEY (target) REFERENCES dag_node (node_id);
ALTER TABLE mechanism_intervention ADD CONSTRAINT ck_mint_result
    CHECK (result IN ('PATH_REMAINS', 'PATH_WEAKENS', 'PATH_BREAKS', 'UNKNOWN'));

ALTER TABLE intervention_candidate ADD CONSTRAINT pk_intervention_candidate
    PRIMARY KEY (mechanism_id, variable, candidate_id);
ALTER TABLE intervention_candidate ADD CONSTRAINT fk_ic_intervention
    FOREIGN KEY (mechanism_id, variable) REFERENCES mechanism_intervention (mechanism_id, variable);
ALTER TABLE intervention_candidate ADD CONSTRAINT fk_ic_candidate
    FOREIGN KEY (candidate_id) REFERENCES latent_candidate (candidate_id);
ALTER TABLE intervention_candidate ADD CONSTRAINT ck_ic_effect CHECK (effect IN ('REMOVED', 'REMAINING'));

ALTER TABLE sd_node ADD CONSTRAINT pk_sd_node PRIMARY KEY (node_id);
ALTER TABLE sd_node ADD CONSTRAINT fk_sd_node_mechanism FOREIGN KEY (mechanism) REFERENCES mechanism (mechanism_id);
-- Super-DAG 상태 어휘 (mechanism_super_dag_*.csv, README '상태 5종')
ALTER TABLE sd_node ADD CONSTRAINT ck_sd_node_status
    CHECK (sd_status IN ('OBSERVED', 'DERIVED', 'LATENT_MECHANISM', 'CONTEXT', 'UNRESOLVED'));
ALTER TABLE sd_node ADD CONSTRAINT ck_sd_node_type
    CHECK (node_type IN ('OBSERVED_EVENT', 'ENV_CONTEXT', 'INSTITUTIONAL_CONTEXT', 'MECHANISM',
                         'STRUCTURAL_VARIABLE', 'CANDIDATE_BRIDGE', 'UNRESOLVED_ITEM'));
ALTER TABLE sd_node ADD CONSTRAINT ck_sd_node_branch CHECK (branch IN ('A_BIOLOGICAL', 'B_PROCEDURAL', 'REVIEW'));

ALTER TABLE sd_edge ADD CONSTRAINT pk_sd_edge PRIMARY KEY (edge_id);
ALTER TABLE sd_edge ADD CONSTRAINT fk_sd_edge_src FOREIGN KEY (src) REFERENCES sd_node (node_id);
ALTER TABLE sd_edge ADD CONSTRAINT fk_sd_edge_dst FOREIGN KEY (dst) REFERENCES sd_node (node_id);
ALTER TABLE sd_edge ADD CONSTRAINT ck_sd_edge_status
    CHECK (sd_status IN ('OBSERVED', 'DERIVED', 'LATENT_MECHANISM', 'CONTEXT', 'UNRESOLVED'));
ALTER TABLE sd_edge ADD CONSTRAINT ck_sd_edge_origin CHECK (origin IN ('FROZEN', 'SUPER_DAG'));
-- stage6_mechanisms.py가 만드는 edge type 전체(frozen 9종 + Super-DAG 10종). CAUSES 없음
ALTER TABLE sd_edge ADD CONSTRAINT ck_sd_edge_type
    CHECK (edge_type IN ('TEMPORAL_BEFORE', 'PROCEDURAL_NEXT', 'INFORMATION_FLOW', 'ORDER_TO_ACTION',
                         'REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL', 'RESPONSIBILITY_LINK',
                         'CONTEXT_SUPPORTS', 'ANCHORED_TO', 'CONDITIONS', 'CONSTRAINS', 'CONTEXT_COMPATIBLE',
                         'CONTRIBUTES_TO', 'EXPLAINS_OBSERVED', 'EXPLAINS_TRANSITION_TO', 'INSTANTIATED_BY',
                         'INSTANTIATED_BY_SECONDARY', 'RULE_INPUT'));
ALTER TABLE sd_edge ADD CONSTRAINT ck_sd_edge_no_self_loop CHECK (src <> dst);

-- -----------------------------------------------------------------------------
-- F. Audit 기록
-- -----------------------------------------------------------------------------
ALTER TABLE warn_disposition ADD CONSTRAINT pk_warn_disposition PRIMARY KEY (warning_id);
ALTER TABLE warn_disposition ADD CONSTRAINT ck_warn_stage
    CHECK (audit_stage IN ('AUDIT1', 'AUDIT2', 'AUDIT3', 'AUDIT4', 'AUDIT5'));
-- build.py apply_dispositions / manual_review.py
ALTER TABLE warn_disposition ADD CONSTRAINT ck_warn_disposition
    CHECK (disposition IN ('FIXED', 'RECLASSIFIED_INFO', 'UNRESOLVED', 'ESCALATED_ERROR'));

ALTER TABLE py_audit_finding ADD CONSTRAINT pk_py_audit_finding PRIMARY KEY (finding_seq);
ALTER TABLE py_audit_finding ADD CONSTRAINT ck_paf_audit
    CHECK (audit_name IN ('AUDIT1', 'AUDIT2', 'AUDIT3', 'AUDIT4', 'AUDIT5'));
-- audits.py 머리말: ERROR | WARN | UNRESOLVED | INFO
ALTER TABLE py_audit_finding ADD CONSTRAINT ck_paf_severity
    CHECK (severity IN ('ERROR', 'WARN', 'UNRESOLVED', 'INFO'));

-- -----------------------------------------------------------------------------
-- G. 규칙 참조표 (데이터 표에 FK 없음 — 위 머리말 참고)
-- -----------------------------------------------------------------------------
ALTER TABLE rule_set_member ADD CONSTRAINT pk_rule_set_member PRIMARY KEY (rule_set, member_id);
ALTER TABLE rule_required_relation ADD CONSTRAINT pk_rule_required_relation PRIMARY KEY (src, dst, edge_type);
ALTER TABLE rule_identity_sensitive_pair ADD CONSTRAINT pk_rule_identity_sensitive PRIMARY KEY (node_a, node_b);
ALTER TABLE rule_conflict_pair ADD CONSTRAINT pk_rule_conflict_pair PRIMARY KEY (candidate_a, candidate_b);
ALTER TABLE rule_candidate_negates ADD CONSTRAINT pk_rule_candidate_negates PRIMARY KEY (candidate_id, mechanism_id);
ALTER TABLE rule_identity_surface ADD CONSTRAINT pk_rule_identity_surface PRIMARY KEY (identity_id);
ALTER TABLE rule_text_pattern ADD CONSTRAINT pk_rule_text_pattern PRIMARY KEY (pattern_id);

-- -----------------------------------------------------------------------------
-- H. 검증·적재 기록
-- -----------------------------------------------------------------------------
ALTER TABLE expected_count ADD CONSTRAINT pk_expected_count PRIMARY KEY (metric_id);
ALTER TABLE load_log ADD CONSTRAINT pk_load_log PRIMARY KEY (load_step, table_name);
