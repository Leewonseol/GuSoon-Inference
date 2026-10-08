-- =============================================================================
-- STAGING 테이블 STG_* — CSV를 문자 그대로 받는 착지(landing) 영역
-- 이 파일은 sql/02_load/generate_load_scripts.py가 canonical CSV header로 생성했다. 손으로 고치지 말 것.
-- Oracle runtime에서 실행 검증되지 않았다(Oracle runtime unavailable) — sql/README.md §실행 상태 참고.
-- =============================================================================

-- 원칙
--   * 모든 컬럼은 VARCHAR2(4000 BYTE)로 받는다(형 변환은 04_transform_to_canonical.sql에서 한다).
--   * 길이가 4000 byte에 가까운 서술(narrative_worlds.narrative)만 CLOB.
--   * CSV의 빈 문자열('')은 Oracle에서 NULL이 된다. Oracle은 ''와 NULL을 구분하지 않는다(SQLD 단골 함정).
--   * 제약조건은 걸지 않는다. 검증은 canonical 테이블의 제약과 03_load_validation.sql이 맡는다.

-- 원본: gusun_clean_restart_csv_pack/00_INPUT_MANIFEST.csv  (5행)
CREATE TABLE STG_INPUT_MANIFEST (
    FILE_NAME                  VARCHAR2(4000 BYTE),
    ROLE                       VARCHAR2(4000 BYTE),
    ALLOWED_AS_DAG_INPUT       VARCHAR2(4000 BYTE),
    PURPOSE                    VARCHAR2(4000 BYTE),
    IMPORTANT_RULE             VARCHAR2(4000 BYTE)
);

-- 원본: gusun_clean_restart_csv_pack/01_confirmed_facts.csv  (50행)
CREATE TABLE STG_CONFIRMED_FACTS (
    FACT_ID                    VARCHAR2(4000 BYTE),
    CHRONOLOGY                 VARCHAR2(4000 BYTE),
    RECORD_LUNAR_DATE          VARCHAR2(4000 BYTE),
    OCCURRENCE_LUNAR_TEXT      VARCHAR2(4000 BYTE),
    FACT_CATEGORY              VARCHAR2(4000 BYTE),
    CONFIRMATION_LEVEL         VARCHAR2(4000 BYTE),
    SUBJECT                    VARCHAR2(4000 BYTE),
    CONFIRMED_STATEMENT        VARCHAR2(4000 BYTE),
    UNDERLYING_CLAIM_STATUS    VARCHAR2(4000 BYTE),
    SOURCE_RECORD_ID           VARCHAR2(4000 BYTE),
    SOURCE_WORK                VARCHAR2(4000 BYTE),
    SOURCE_URL                 VARCHAR2(4000 BYTE),
    SOURCE_PROP_IDS            VARCHAR2(4000 BYTE),
    NOTES                      VARCHAR2(4000 BYTE)
);

-- 원본: gusun_clean_restart_csv_pack/02_institutional_normative_features.csv  (20행)
CREATE TABLE STG_INSTITUTIONAL_FEATURES (
    FEATURE_ID                 VARCHAR2(4000 BYTE),
    LAYER                      VARCHAR2(4000 BYTE),
    FEATURE_GROUP              VARCHAR2(4000 BYTE),
    FEATURE_NAME               VARCHAR2(4000 BYTE),
    OPERATIONAL_DEFINITION     VARCHAR2(4000 BYTE),
    ENCODING_TYPE              VARCHAR2(4000 BYTE),
    SUGGESTED_VALUES           VARCHAR2(4000 BYTE),
    MODEL_ROLE                 VARCHAR2(4000 BYTE),
    INTERPRETATION             VARCHAR2(4000 BYTE),
    VALID_FROM                 VARCHAR2(4000 BYTE),
    VALID_TO                   VARCHAR2(4000 BYTE),
    GEO_SCOPE                  VARCHAR2(4000 BYTE),
    SOURCE_NAME                VARCHAR2(4000 BYTE),
    SOURCE_URL                 VARCHAR2(4000 BYTE),
    NOTES                      VARCHAR2(4000 BYTE)
);

-- 원본: gusun_clean_restart_csv_pack/03_environment_1793.csv  (4행)
CREATE TABLE STG_ENVIRONMENT_1793 (
    ENV_ID                     VARCHAR2(4000 BYTE),
    LUNAR_DATE                 VARCHAR2(4000 BYTE),
    REGION_SCOPE               VARCHAR2(4000 BYTE),
    CONTEXT_TYPE               VARCHAR2(4000 BYTE),
    ATTESTED_CONTEXT           VARCHAR2(4000 BYTE),
    FEATURE_NAME               VARCHAR2(4000 BYTE),
    VALUE                      VARCHAR2(4000 BYTE),
    MODEL_ROLE                 VARCHAR2(4000 BYTE),
    SOURCE_URL                 VARCHAR2(4000 BYTE),
    NOTES                      VARCHAR2(4000 BYTE)
);

-- 원본: gusun_clean_restart_csv_pack/04_source_records.csv  (8행)
CREATE TABLE STG_SOURCE_RECORDS (
    SOURCE_RECORD_ID           VARCHAR2(4000 BYTE),
    SOURCE_WORK                VARCHAR2(4000 BYTE),
    RECORD_LUNAR_DATE          VARCHAR2(4000 BYTE),
    SOURCE_TITLE               VARCHAR2(4000 BYTE),
    SOURCE_URL                 VARCHAR2(4000 BYTE),
    SOURCE_DOMAIN              VARCHAR2(4000 BYTE),
    SOURCE_TIER                VARCHAR2(4000 BYTE),
    CASE_ROLE                  VARCHAR2(4000 BYTE),
    NOTES                      VARCHAR2(4000 BYTE)
);

-- 원본: gusun_clean_restart_csv_pack/05_source_faithful_propositions_AUDIT_ONLY.csv  (156행)
CREATE TABLE STG_AUDIT_PROPOSITIONS (
    PROP_ID                    VARCHAR2(4000 BYTE),
    SOURCE_RECORD_ID           VARCHAR2(4000 BYTE),
    SOURCE_WORK                VARCHAR2(4000 BYTE),
    RECORD_LUNAR_DATE          VARCHAR2(4000 BYTE),
    REPORTING_ACTOR            VARCHAR2(4000 BYTE),
    ATTESTATION_MODE           VARCHAR2(4000 BYTE),
    PROPOSITION_TYPE           VARCHAR2(4000 BYTE),
    SUBJECT                    VARCHAR2(4000 BYTE),
    PREDICATE                  VARCHAR2(4000 BYTE),
    OBJECT_OR_CONTENT          VARCHAR2(4000 BYTE),
    OCCURRENCE_LUNAR_TEXT      VARCHAR2(4000 BYTE),
    OCCURRENCE_PRECISION       VARCHAR2(4000 BYTE),
    HISTORICAL_PLACE           VARCHAR2(4000 BYTE),
    PLACE_STATUS               VARCHAR2(4000 BYTE),
    NAMED_ENTITIES             VARCHAR2(4000 BYTE),
    EPISTEMIC_SCOPE            VARCHAR2(4000 BYTE),
    CLAIM_TOPIC                VARCHAR2(4000 BYTE),
    CONFLICT_GROUP             VARCHAR2(4000 BYTE),
    SET_STATUS                 VARCHAR2(4000 BYTE),
    DIRECTNESS                 VARCHAR2(4000 BYTE),
    SOURCE_URL                 VARCHAR2(4000 BYTE),
    NOTES                      VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/episode_nodes.csv  (41행)
CREATE TABLE STG_EPISODE_NODES (
    NODE_ID                    VARCHAR2(4000 BYTE),
    NODE_STATUS                VARCHAR2(4000 BYTE),
    LAYER                      VARCHAR2(4000 BYTE),
    BRANCH                     VARCHAR2(4000 BYTE),
    TITLE                      VARCHAR2(4000 BYTE),
    SUMMARY                    VARCHAR2(4000 BYTE),
    CAUTION                    VARCHAR2(4000 BYTE),
    MEMBER_FACT_IDS            VARCHAR2(4000 BYTE),
    MEMBER_CLAUSES             VARCHAR2(4000 BYTE),
    CONFIRMATION_LEVELS        VARCHAR2(4000 BYTE),
    EPISTEMIC_FLOOR            VARCHAR2(4000 BYTE),
    CLAIM_STATUS               VARCHAR2(4000 BYTE),
    SOURCE_RECORD_IDS          VARCHAR2(4000 BYTE),
    SOURCE_PROP_IDS            VARCHAR2(4000 BYTE),
    ATTESTING_ACTOR            VARCHAR2(4000 BYTE),
    OCCURRENCE_TEXT            VARCHAR2(4000 BYTE),
    T_MIN                      VARCHAR2(4000 BYTE),
    T_MAX                      VARCHAR2(4000 BYTE),
    RECORD_LUNAR_DATE          VARCHAR2(4000 BYTE),
    GROUPING_RATIONALE         VARCHAR2(4000 BYTE),
    IDENTITY_LINKS             VARCHAR2(4000 BYTE),
    ENV_ID                     VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/observed_edges.csv  (68행)
CREATE TABLE STG_OBSERVED_EDGES (
    EDGE_ID                    VARCHAR2(4000 BYTE),
    SRC                        VARCHAR2(4000 BYTE),
    DST                        VARCHAR2(4000 BYTE),
    EDGE_TYPE                  VARCHAR2(4000 BYTE),
    BASIS                      VARCHAR2(4000 BYTE),
    STATUS                     VARCHAR2(4000 BYTE),
    CLAIM_LEVEL                VARCHAR2(4000 BYTE),
    CONDITION                  VARCHAR2(4000 BYTE),
    SUPPORTING                 VARCHAR2(4000 BYTE),
    RATIONALE                  VARCHAR2(4000 BYTE),
    CAUTION                    VARCHAR2(4000 BYTE),
    UNCERTAINTY_STATUS         VARCHAR2(4000 BYTE),
    REVIEW_DECISION            VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/node_feature_links.csv  (57행)
CREATE TABLE STG_NODE_FEATURE_LINKS (
    LINK_ID                    VARCHAR2(4000 BYTE),
    TARGET_KIND                VARCHAR2(4000 BYTE),
    TARGET_ID                  VARCHAR2(4000 BYTE),
    FEATURE_LAYER              VARCHAR2(4000 BYTE),
    FEATURE_ID                 VARCHAR2(4000 BYTE),
    DIMENSION                  VARCHAR2(4000 BYTE),
    ASSESSMENT                 VARCHAR2(4000 BYTE),
    CREATES_EVENT              VARCHAR2(4000 BYTE),
    RATIONALE                  VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/identity_register.csv  (11행)
CREATE TABLE STG_IDENTITY_REGISTER (
    IDENTITY_ID                VARCHAR2(4000 BYTE),
    SURFACE_A                  VARCHAR2(4000 BYTE),
    SURFACE_B                  VARCHAR2(4000 BYTE),
    STATUS                     VARCHAR2(4000 BYTE),
    RESOLVED_BY                VARCHAR2(4000 BYTE),
    RESOLUTION_BASIS           VARCHAR2(4000 BYTE),
    UNRESOLVED_REASON          VARCHAR2(4000 BYTE),
    MODEL_RELEVANCE            VARCHAR2(4000 BYTE),
    MANUAL_DECISION_REQUIRED   VARCHAR2(4000 BYTE),
    REVIEW_DECISION            VARCHAR2(4000 BYTE),
    CONTEXT                    VARCHAR2(4000 BYTE),
    REFERENCED_FACTS           VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/gaps.csv  (13행)
CREATE TABLE STG_GAPS (
    GAP_ID                     VARCHAR2(4000 BYTE),
    TITLE                      VARCHAR2(4000 BYTE),
    GAP_TYPE                   VARCHAR2(4000 BYTE),
    BETWEEN_NODES              VARCHAR2(4000 BYTE),
    OBSERVED_ANCHOR_FACTS      VARCHAR2(4000 BYTE),
    WHY_GAP                    VARCHAR2(4000 BYTE),
    GAP_STATUS                 VARCHAR2(4000 BYTE),
    REVIEW_DECISION            VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/latent_candidates.csv  (38행)
CREATE TABLE STG_LATENT_CANDIDATES (
    CANDIDATE_ID               VARCHAR2(4000 BYTE),
    GAP_ID                     VARCHAR2(4000 BYTE),
    STATUS                     VARCHAR2(4000 BYTE),
    FORM                       VARCHAR2(4000 BYTE),
    LABEL                      VARCHAR2(4000 BYTE),
    DESCRIPTION                VARCHAR2(4000 BYTE),
    SOURCE_CONSISTENCY         VARCHAR2(4000 BYTE),
    TEMPORAL_FIT               VARCHAR2(4000 BYTE),
    INSTITUTIONAL_FIT          VARCHAR2(4000 BYTE),
    ROLE_FIT                   VARCHAR2(4000 BYTE),
    INFORMATION_FLOW_FIT       VARCHAR2(4000 BYTE),
    ENVIRONMENTAL_FIT          VARCHAR2(4000 BYTE),
    CONTRADICTION_RISK         VARCHAR2(4000 BYTE),
    N_ASSUMPTIONS              VARCHAR2(4000 BYTE),
    EXTRA_ASSUMPTIONS          VARCHAR2(4000 BYTE),
    IDENTITY_CONDITIONS        VARCHAR2(4000 BYTE),
    OVERALL                    VARCHAR2(4000 BYTE),
    PRUNE_DECISION             VARCHAR2(4000 BYTE),
    SUPPORTS                   VARCHAR2(4000 BYTE),
    CONFLICTS                  VARCHAR2(4000 BYTE),
    AUDIT_ATTESTATION          VARCHAR2(4000 BYTE),
    SUPPORT_BASIS              VARCHAR2(4000 BYTE),
    NOTES                      VARCHAR2(4000 BYTE),
    OBSERVED_LEFT              VARCHAR2(4000 BYTE),
    OBSERVED_RIGHT             VARCHAR2(4000 BYTE),
    LATENT_BRIDGE_CLAIM        VARCHAR2(4000 BYTE),
    BRIDGE_DIRECTLY_ATTESTED   VARCHAR2(4000 BYTE),
    ENDPOINT_SUPPORT           VARCHAR2(4000 BYTE),
    SOURCE_SUPPORT             VARCHAR2(4000 BYTE),
    BRIDGE_EVIDENCE            VARCHAR2(4000 BYTE),
    BRIDGE_BASIS               VARCHAR2(4000 BYTE),
    EVIDENCE_GRADE             VARCHAR2(4000 BYTE),
    PLAUSIBILITY_GRADE         VARCHAR2(4000 BYTE),
    SOURCE_CONSISTENCY_V1      VARCHAR2(4000 BYTE),
    OVERALL_V1                 VARCHAR2(4000 BYTE),
    REAUDIT_REASON             VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/latent_elements.csv  (119행)
CREATE TABLE STG_LATENT_ELEMENTS (
    ELEMENT_ID                 VARCHAR2(4000 BYTE),
    CANDIDATE_ID               VARCHAR2(4000 BYTE),
    KIND                       VARCHAR2(4000 BYTE),
    STATUS                     VARCHAR2(4000 BYTE),
    SRC                        VARCHAR2(4000 BYTE),
    DST                        VARCHAR2(4000 BYTE),
    EDGE_TYPE                  VARCHAR2(4000 BYTE),
    TEXT                       VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/narrative_worlds.csv  (6행)
CREATE TABLE STG_NARRATIVE_WORLDS (
    WORLD_ID                   VARCHAR2(4000 BYTE),
    NAME                       VARCHAR2(4000 BYTE),
    STATUS                     VARCHAR2(4000 BYTE),
    LATENT_BRIDGES             VARCHAR2(4000 BYTE),
    UNRESOLVED_GAPS            VARCHAR2(4000 BYTE),
    INSTITUTIONAL_FIT          VARCHAR2(4000 BYTE),
    ENVIRONMENTAL_FIT          VARCHAR2(4000 BYTE),
    N_ASSUMPTIONS              VARCHAR2(4000 BYTE),
    MIN_GRADE                  VARCHAR2(4000 BYTE),
    MAIN_ASSUMPTIONS           VARCHAR2(4000 BYTE),
    MAIN_WEAKNESSES            VARCHAR2(4000 BYTE),
    CONTRADICTED_EVIDENCE      VARCHAR2(4000 BYTE),
    STORY_IMPLICATION          VARCHAR2(4000 BYTE),
    IDENTITY_CONDITIONS        VARCHAR2(4000 BYTE),
    RESOLVED_IDENTITIES        VARCHAR2(4000 BYTE),
    EVIDENCE_PROFILE           VARCHAR2(4000 BYTE),
    WORK_ROLE                  VARCHAR2(4000 BYTE),
    STORY_QUESTION             VARCHAR2(4000 BYTE),
    DIFFERENCE                 VARCHAR2(4000 BYTE),
    UNIQUE_BRIDGES             VARCHAR2(4000 BYTE),
    NARRATIVE                  CLOB
);

-- 원본: output/clean/warn_dispositions.csv  (6행)
CREATE TABLE STG_WARN_DISPOSITIONS (
    WARNING_ID                 VARCHAR2(4000 BYTE),
    AUDIT_STAGE                VARCHAR2(4000 BYTE),
    AFFECTED_ITEM              VARCHAR2(4000 BYTE),
    WARNING_TYPE               VARCHAR2(4000 BYTE),
    ORIGINAL_TEXT              VARCHAR2(4000 BYTE),
    GENERATED_TEXT             VARCHAR2(4000 BYTE),
    RISK                       VARCHAR2(4000 BYTE),
    DISPOSITION                VARCHAR2(4000 BYTE),
    JUSTIFICATION              VARCHAR2(4000 BYTE),
    FIXED_TEXT                 VARCHAR2(4000 BYTE),
    FINAL_STATUS               VARCHAR2(4000 BYTE),
    FINAL_CLASSIFICATION       VARCHAR2(4000 BYTE),
    UNRESOLVED_REASON          VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/mechanism_super_dag_nodes.csv  (122행)
CREATE TABLE STG_SD_NODES (
    NODE_ID                    VARCHAR2(4000 BYTE),
    SD_STATUS                  VARCHAR2(4000 BYTE),
    NODE_TYPE                  VARCHAR2(4000 BYTE),
    LABEL                      VARCHAR2(4000 BYTE),
    FROZEN_STATUS              VARCHAR2(4000 BYTE),
    BRANCH                     VARCHAR2(4000 BYTE),
    MECHANISM                  VARCHAR2(4000 BYTE),
    WORLDS                     VARCHAR2(4000 BYTE),
    DETAIL                     VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/mechanism_super_dag_edges.csv  (205행)
CREATE TABLE STG_SD_EDGES (
    EDGE_ID                    VARCHAR2(4000 BYTE),
    SRC                        VARCHAR2(4000 BYTE),
    DST                        VARCHAR2(4000 BYTE),
    EDGE_TYPE                  VARCHAR2(4000 BYTE),
    SD_STATUS                  VARCHAR2(4000 BYTE),
    ORIGIN                     VARCHAR2(4000 BYTE),
    NOTE                       VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/mechanism_definitions.csv  (7행)
CREATE TABLE STG_MECHANISM_DEFINITIONS (
    MECHANISM_ID               VARCHAR2(4000 BYTE),
    MECHANISM_NAME             VARCHAR2(4000 BYTE),
    EASY_DESCRIPTION           VARCHAR2(4000 BYTE),
    RELATED_CANDIDATES         VARCHAR2(4000 BYTE),
    RELATED_OBSERVED_NODES     VARCHAR2(4000 BYTE),
    REQUIRED_INST_FEATURES     VARCHAR2(4000 BYTE),
    RELATED_ENV_FEATURES       VARCHAR2(4000 BYTE),
    EVIDENCE_STATUS            VARCHAR2(4000 BYTE),
    REMARKS                    VARCHAR2(4000 BYTE),
    N_CANDIDATES               VARCHAR2(4000 BYTE),
    BRANCH                     VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/world_mechanism_configurations.csv  (6행)
CREATE TABLE STG_WORLD_MECH_CONFIGS (
    WORLD_ID                   VARCHAR2(4000 BYTE),
    ROLE_TYPE                  VARCHAR2(4000 BYTE),
    M1                         VARCHAR2(4000 BYTE),
    M2                         VARCHAR2(4000 BYTE),
    M3                         VARCHAR2(4000 BYTE),
    M4                         VARCHAR2(4000 BYTE),
    M5                         VARCHAR2(4000 BYTE),
    M6                         VARCHAR2(4000 BYTE),
    MB                         VARCHAR2(4000 BYTE),
    M1_BASIS                   VARCHAR2(4000 BYTE),
    M2_BASIS                   VARCHAR2(4000 BYTE),
    M3_BASIS                   VARCHAR2(4000 BYTE),
    M4_BASIS                   VARCHAR2(4000 BYTE),
    M5_BASIS                   VARCHAR2(4000 BYTE),
    M6_BASIS                   VARCHAR2(4000 BYTE),
    MB_BASIS                   VARCHAR2(4000 BYTE),
    LATENT_BRIDGES             VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/mechanism_interaction_matrix.csv  (21행)
CREATE TABLE STG_MECH_INTERACTIONS (
    MECHANISM_A_ID             VARCHAR2(4000 BYTE),
    MECHANISM_B_ID             VARCHAR2(4000 BYTE),
    COEXISTENCE                VARCHAR2(4000 BYTE),
    REASON                     VARCHAR2(4000 BYTE),
    CONFLICTING_ITEMS          VARCHAR2(4000 BYTE),
    EXPLAINED_TOGETHER         VARCHAR2(4000 BYTE),
    RELATION                   VARCHAR2(4000 BYTE),
    COOCCUR_WORLDS             VARCHAR2(4000 BYTE),
    MECHANISM_A_NAME           VARCHAR2(4000 BYTE),
    MECHANISM_B_NAME           VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/mechanism_interventions.csv  (13행)
CREATE TABLE STG_MECH_INTERVENTIONS (
    MECHANISM                  VARCHAR2(4000 BYTE),
    VARIABLE                   VARCHAR2(4000 BYTE),
    TARGET                     VARCHAR2(4000 BYTE),
    RESULT                     VARCHAR2(4000 BYTE),
    REMOVED                    VARCHAR2(4000 BYTE),
    REMAINING                  VARCHAR2(4000 BYTE),
    AFFECTED_WORLDS            VARCHAR2(4000 BYTE),
    NOTE                       VARCHAR2(4000 BYTE)
);

-- 원본: output/clean/qualitative_structural_rules.csv  (10행)
CREATE TABLE STG_STRUCTURAL_RULES (
    VAR_ID                     VARCHAR2(4000 BYTE),
    GAP                        VARCHAR2(4000 BYTE),
    TARGET                     VARCHAR2(4000 BYTE),
    OP                         VARCHAR2(4000 BYTE),
    INPUTS                     VARCHAR2(4000 BYTE),
    RULE                       VARCHAR2(4000 BYTE),
    RULE_DESC                  VARCHAR2(4000 BYTE),
    CONSTRAINT_TEXT            VARCHAR2(4000 BYTE),
    INPUT_CANDIDATES           VARCHAR2(4000 BYTE)
);

-- 원본: sql/02_load/data/episode_members.csv  (52행)
CREATE TABLE STG_EPISODE_MEMBERS (
    EPISODE_ID                 VARCHAR2(4000 BYTE),
    MEMBER_SEQ                 VARCHAR2(4000 BYTE),
    FACT_ID                    VARCHAR2(4000 BYTE),
    CLAUSE                     VARCHAR2(4000 BYTE)
);

-- 원본: sql/02_load/data/py_audit_findings.csv  (62행)
CREATE TABLE STG_PY_AUDIT_FINDINGS (
    FINDING_SEQ                VARCHAR2(4000 BYTE),
    AUDIT_NAME                 VARCHAR2(4000 BYTE),
    CHECK_NAME                 VARCHAR2(4000 BYTE),
    SEVERITY                   VARCHAR2(4000 BYTE),
    TARGET                     VARCHAR2(4000 BYTE),
    MESSAGE                    VARCHAR2(4000 BYTE)
);

-- 원본: sql/02_load/data/dag_freeze.csv  (1행)
CREATE TABLE STG_DAG_FREEZE (
    FREEZE_NAME                VARCHAR2(4000 BYTE),
    SHA256                     VARCHAR2(4000 BYTE),
    STRUCTURE_SHA256           VARCHAR2(4000 BYTE),
    TOPOLOGY_SHA256            VARCHAR2(4000 BYTE),
    N_NODES                    VARCHAR2(4000 BYTE),
    N_EDGES                    VARCHAR2(4000 BYTE),
    N_EPISODE_NODES            VARCHAR2(4000 BYTE),
    N_ENV_NODES                VARCHAR2(4000 BYTE),
    LATENT_COUNT               VARCHAR2(4000 BYTE)
);
