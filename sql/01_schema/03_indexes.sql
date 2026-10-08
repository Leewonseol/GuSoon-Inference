-- =============================================================================
-- 03_indexes.sql — 인덱스
-- -----------------------------------------------------------------------------
-- * PK·UNIQUE 제약은 Oracle이 인덱스를 자동으로 만든다. 여기에는 그 밖의 인덱스만 둔다.
-- * Oracle은 FK 컬럼에 인덱스를 자동으로 만들지 않는다(SQLD 단골). 부모 행 DELETE/UPDATE 때
--   자식 표 전체 잠금을 피하고 JOIN·CONNECT BY를 빠르게 하려고 FK 컬럼에 인덱스를 둔다.
--   (FK 컬럼이 PK·UK의 선두 컬럼이면 이미 인덱스가 있으므로 생략)
-- * 데이터가 수백 행이라 성능상 필요는 크지 않다. 학습용으로 '어디에 왜'를 보여 주는 것이 목적이다.
-- =============================================================================

-- 계층형 질의(CONNECT BY PRIOR dst = src / PRIOR src = dst)의 탐색 컬럼
CREATE INDEX ix_dag_edge_src ON dag_edge (src);
CREATE INDEX ix_dag_edge_dst ON dag_edge (dst);
CREATE INDEX ix_dag_edge_type ON dag_edge (edge_type, status);
CREATE INDEX ix_sd_edge_src ON sd_edge (src);
CREATE INDEX ix_sd_edge_dst ON sd_edge (dst);

-- FK 컬럼 인덱스 (PK 선두가 아닌 것)
CREATE INDEX ix_cf_source_record ON confirmed_fact (source_record_id);
CREATE INDEX ix_cf_confirmation_level ON confirmed_fact (confirmation_level);
CREATE INDEX ix_prop_source_record ON audit_proposition (source_record_id);
CREATE INDEX ix_factprop_prop ON fact_proposition (prop_id);
CREATE INDEX ix_dag_node_env ON dag_node (env_id);
CREATE INDEX ix_epmember_fact ON episode_member (fact_id);
CREATE INDEX ix_idref_fact ON identity_fact_ref (fact_id);
CREATE INDEX ix_esb_fact ON edge_source_basis (fact_id);        -- 가상 컬럼 인덱스
CREATE INDEX ix_esb_env ON edge_source_basis (env_id);          -- 가상 컬럼 인덱스
CREATE INDEX ix_eic_identity ON edge_identity_condition (identity_id);
CREATE INDEX ix_nfl_node ON node_feature_link (target_node_id);
CREATE INDEX ix_nfl_edge ON node_feature_link (target_edge_id);
CREATE INDEX ix_nfl_inst ON node_feature_link (inst_feature_id);
CREATE INDEX ix_nfl_env ON node_feature_link (env_feature_id);
CREATE INDEX ix_gapanchor_node ON gap_anchor_node (node_id);
CREATE INDEX ix_candidate_gap ON latent_candidate (gap_id);
CREATE INDEX ix_latelem_candidate ON latent_element (candidate_id);
CREATE INDEX ix_cic_identity ON candidate_identity_condition (identity_id);
CREATE INDEX ix_cev_fact ON candidate_evidence (fact_id);
CREATE INDEX ix_cev_prop ON candidate_evidence (prop_id);
CREATE INDEX ix_wc_candidate_gap ON world_candidate (candidate_id, gap_id);
CREATE INDEX ix_wug_gap ON world_unresolved_gap (gap_id);
CREATE INDEX ix_wi_identity ON world_identity (identity_id);
CREATE INDEX ix_cm_mechanism ON candidate_mechanism (mechanism_id);
CREATE INDEX ix_wmc_mechanism ON world_mechanism_config (mechanism_id);
CREATE INDEX ix_mi_b ON mechanism_interaction (mechanism_b_id);
CREATE INDEX ix_mint_variable ON mechanism_intervention (variable);
CREATE INDEX ix_mint_target ON mechanism_intervention (target);
CREATE INDEX ix_ic_candidate ON intervention_candidate (candidate_id);
CREATE INDEX ix_sd_node_mechanism ON sd_node (mechanism);

-- 함수 기반 UNIQUE 인덱스(Oracle 기법): 후보마다 PRIMARY 메커니즘은 정확히 하나
-- (stage6_mechanisms.py CAND_MAP의 첫 열 = primary). CASE가 NULL을 돌려주는 SECONDARY 행은
-- 인덱스에 들어가지 않으므로 PRIMARY 행끼리만 유일성이 검사된다.
CREATE UNIQUE INDEX ux_cm_one_primary
    ON candidate_mechanism (CASE WHEN mapping_role = 'PRIMARY' THEN candidate_id END);

-- 대소문자·표기 흔들림 없이 검색하는 예: UPPER(edge_type) 함수 기반 인덱스
CREATE INDEX ix_sd_edge_type_upper ON sd_edge (UPPER(edge_type));
