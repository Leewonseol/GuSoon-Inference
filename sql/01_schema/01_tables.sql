-- =============================================================================
-- 01_tables.sql — 구순–김명신 사건(1793) canonical 데이터의 Oracle 관계형 모델
-- -----------------------------------------------------------------------------
-- * 컬럼 이름·의미는 canonical CSV(gusun_clean_restart_csv_pack/, output/clean/)와
--   DuckDB(database/gusun_clean.duckdb)의 실제 header를 그대로 따른다.
--   Oracle 예약어·한글 header만 바꿨다(between→between_nodes, desc→rule_desc,
--   audit→audit_name, 한글 컬럼 → 영문). 전체 대응표는 sql/README.md §4.
-- * 여기서는 컬럼·데이터형·NOT NULL·가상 컬럼만 정의한다.
--   PK·FK·UNIQUE·CHECK는 이름을 붙여 02_constraints.sql에서 ALTER TABLE로 추가한다.
-- * 한글이 들어가는 컬럼은 문자(CHAR) 길이 의미로 선언한다. VARCHAR2(100 CHAR)는 100글자.
--   (AL32UTF8에서 한글 1글자 = 3 byte. VARCHAR2 상한은 여전히 4000 byte)
-- * 날짜: 이 사건의 날짜는 모두 '음력' 1793년이고 '1793-02 초순', '1793-02-29'처럼
--   그레고리력 DATE로 옮길 수 없는 값이 섞여 있다(1793년 양력 2월에는 29일이 없다).
--   그래서 날짜 원문은 VARCHAR2로 보존하고, 정렬·비교는 Python과 같은 정수 MMDD
--   (t_min/t_max, 예: 3월 4일 = 304)로 한다. DATE/TIMESTAMP는 적재 기록(LOAD_LOG)에만 쓴다.
-- * Oracle runtime에서 실행 검증되지 않았다. sql/README.md §실행 상태 참고.
-- =============================================================================


-- =============================================================================
-- A. 원천 입력 pack (gusun_clean_restart_csv_pack/00–05)
-- =============================================================================

-- 00_INPUT_MANIFEST.csv : 입력 파일별 역할과 DAG 입력 허용 여부
CREATE TABLE input_manifest (
    file_name               VARCHAR2(100)        NOT NULL,
    role                    VARCHAR2(30)         NOT NULL,   -- PRIMARY_CASE_INPUT / AUDIT_ONLY / ...
    allowed_as_dag_input    VARCHAR2(3)          NOT NULL,   -- YES / NO
    purpose                 VARCHAR2(200 CHAR),
    important_rule          VARCHAR2(300 CHAR)
);

-- 04_source_records.csv : 사료 기사(출처) 단위
CREATE TABLE source_record (
    source_record_id        VARCHAR2(20)         NOT NULL,   -- SRC3_001 ...
    source_work             VARCHAR2(50 CHAR)    NOT NULL,   -- 조선왕조실록 정조실록 / 비변사등록 / 승정원일기
    record_lunar_date       VARCHAR2(10)         NOT NULL,   -- 기록일(음력, 'YYYY-MM-DD' 문자열)
    source_title            VARCHAR2(200 CHAR)   NOT NULL,
    source_url              VARCHAR2(300)        NOT NULL,
    source_domain           VARCHAR2(100),
    source_tier             VARCHAR2(20)         NOT NULL,
    case_role               VARCHAR2(200 CHAR),
    notes                   VARCHAR2(500 CHAR)
);

-- epistemic 등급 참조표 (scripts/gusun_clean/stage1_episodes.py EPISTEMIC_RANK + audits.py FAMILY를 옮긴 것)
CREATE TABLE ref_confirmation_level (
    confirmation_level      VARCHAR2(40)         NOT NULL,
    epistemic_rank          NUMBER(1)            NOT NULL,   -- 0(중첩 진술) ~ 4(공식 행위)
    epistemic_family        VARCHAR2(10)         NOT NULL    -- TESTIMONY / IDENT / OFFICIAL / ROYAL / COURT / MIXED
);

-- 01_confirmed_facts.csv : 확정 사실 50개. episode(=DAG node)의 유일한 근거
CREATE TABLE confirmed_fact (
    fact_id                 VARCHAR2(10)         NOT NULL,   -- CF001 ...
    chronology              VARCHAR2(50 CHAR)    NOT NULL,   -- 발생 시점 서술(음력)
    record_lunar_date       VARCHAR2(10)         NOT NULL,   -- 기록일(사료 날짜) — 발생일과 다르다
    occurrence_lunar_text   VARCHAR2(50 CHAR),               -- 발생일 원문(없으면 NULL — 임의 날짜를 만들지 않음)
    fact_category           VARCHAR2(40)         NOT NULL,
    confirmation_level      VARCHAR2(40)         NOT NULL,
    subject                 VARCHAR2(50 CHAR)    NOT NULL,
    confirmed_statement     VARCHAR2(400 CHAR)   NOT NULL,
    underlying_claim_status VARCHAR2(50)         NOT NULL,
    source_record_id        VARCHAR2(20)         NOT NULL,
    source_work             VARCHAR2(50 CHAR)    NOT NULL,
    source_url              VARCHAR2(300)        NOT NULL,
    source_prop_ids         VARCHAR2(100)        NOT NULL,   -- 원문 그대로의 '|' 목록. 정규화본은 fact_proposition
    notes                   VARCHAR2(300 CHAR)
);

-- 05_source_faithful_propositions_AUDIT_ONLY.csv : 감사(audit) 전용 명제. DAG 입력이 아니다
CREATE TABLE audit_proposition (
    prop_id                 VARCHAR2(10)         NOT NULL,   -- V3P0001 ...
    source_record_id        VARCHAR2(20)         NOT NULL,
    source_work             VARCHAR2(50 CHAR)    NOT NULL,
    record_lunar_date       VARCHAR2(10)         NOT NULL,
    reporting_actor         VARCHAR2(50 CHAR)    NOT NULL,
    attestation_mode        VARCHAR2(40)         NOT NULL,
    proposition_type        VARCHAR2(20)         NOT NULL,
    subject                 VARCHAR2(50 CHAR)    NOT NULL,
    predicate               VARCHAR2(200 CHAR)   NOT NULL,
    object_or_content       VARCHAR2(100 CHAR),
    occurrence_lunar_text   VARCHAR2(50 CHAR),
    occurrence_precision    VARCHAR2(20)         NOT NULL,
    historical_place        VARCHAR2(50 CHAR),
    place_status            VARCHAR2(30)         NOT NULL,
    named_entities          VARCHAR2(100 CHAR),
    epistemic_scope         VARCHAR2(40)         NOT NULL,
    claim_topic             VARCHAR2(40)         NOT NULL,
    conflict_group          VARCHAR2(40),
    set_status              VARCHAR2(30)         NOT NULL,   -- NOT_APPLICABLE / OPEN_SET / OPEN_SET_EXPLICIT_MEMBERS
    directness              VARCHAR2(20)         NOT NULL,
    source_url              VARCHAR2(300)        NOT NULL,
    notes                   VARCHAR2(300 CHAR)
);

-- confirmed_fact.source_prop_ids('V3P0049|V3P0050')를 행으로 편 연결 테이블 (M:N)
CREATE TABLE fact_proposition (
    fact_id                 VARCHAR2(10)         NOT NULL,
    prop_id                 VARCHAR2(10)         NOT NULL,
    prop_seq                NUMBER(2)            NOT NULL    -- 원문 목록 안의 순서(1부터)
);

-- 02_institutional_normative_features.csv : 1793년 제도 피쳐 F001–F020 (사건을 만들지 않는 제약조건)
CREATE TABLE institutional_feature (
    feature_id              VARCHAR2(10)         NOT NULL,
    layer                   VARCHAR2(20)         NOT NULL,
    feature_group           VARCHAR2(20 CHAR)    NOT NULL,
    feature_name            VARCHAR2(50 CHAR)    NOT NULL,
    operational_definition  VARCHAR2(200 CHAR)   NOT NULL,
    encoding_type           VARCHAR2(20)         NOT NULL,
    suggested_values        VARCHAR2(100)        NOT NULL,
    model_role              VARCHAR2(50)         NOT NULL,
    interpretation          VARCHAR2(200 CHAR)   NOT NULL,
    valid_from              NUMBER(4)            NOT NULL,   -- 연도(정수)
    valid_to                NUMBER(4)            NOT NULL,
    geo_scope               VARCHAR2(30 CHAR)    NOT NULL,
    source_name             VARCHAR2(50 CHAR)    NOT NULL,
    source_url              VARCHAR2(300)        NOT NULL,
    notes                   VARCHAR2(300 CHAR)
);

-- 03_environment_1793.csv : 외생 환경 E001–E004 (CONTEXT. 개인 사실을 만들지 않는다)
CREATE TABLE environment_context (
    env_id                  VARCHAR2(10)         NOT NULL,
    lunar_date              VARCHAR2(10)         NOT NULL,
    region_scope            VARCHAR2(20 CHAR)    NOT NULL,
    context_type            VARCHAR2(20 CHAR)    NOT NULL,
    attested_context        VARCHAR2(200 CHAR)   NOT NULL,
    feature_name            VARCHAR2(50)         NOT NULL,
    value                   NUMBER(1)            NOT NULL,
    model_role              VARCHAR2(50)         NOT NULL,
    source_url              VARCHAR2(300)        NOT NULL,
    notes                   VARCHAR2(200 CHAR)
);


-- =============================================================================
-- B. Observed partial DAG (output/clean/episode_nodes.csv, observed_edges.csv …) — Stage 3 동결본
-- =============================================================================

-- episode_nodes.csv : observed node 41개 = episode 37(EP01–EP37) + 환경 context 4(ENV01–ENV04)
CREATE TABLE dag_node (
    node_id                 VARCHAR2(10)         NOT NULL,
    node_status             VARCHAR2(10)         NOT NULL,   -- 동결 DAG에는 OBSERVED만 있다
    layer                   VARCHAR2(30)         NOT NULL,
    branch                  VARCHAR2(30)         NOT NULL,
    title                   VARCHAR2(100 CHAR)   NOT NULL,
    summary                 VARCHAR2(400 CHAR)   NOT NULL,
    caution                 VARCHAR2(600 CHAR),
    member_fact_ids         VARCHAR2(100),                   -- 원문 '|' 목록. 정규화본은 episode_member
    member_clauses          VARCHAR2(300 CHAR),
    confirmation_levels     VARCHAR2(200),
    epistemic_floor         VARCHAR2(40)         NOT NULL,
    claim_status            VARCHAR2(200),
    source_record_ids       VARCHAR2(100),
    source_prop_ids         VARCHAR2(200),
    attesting_actor         VARCHAR2(50 CHAR)    NOT NULL,
    occurrence_text         VARCHAR2(100 CHAR)   NOT NULL,
    t_min                   NUMBER(4),                       -- 발생 구간 시작(음력 MMDD). 모르면 NULL
    t_max                   NUMBER(4),                       -- 발생 구간 끝. 열린 구간('이후')이면 NULL
    record_lunar_date       VARCHAR2(10)         NOT NULL,   -- 기록일. 발생일(t_min/t_max)과 혼동 금지
    grouping_rationale      VARCHAR2(200 CHAR)   NOT NULL,
    identity_links          VARCHAR2(100),
    env_id                  VARCHAR2(10)                     -- 환경 node만 값이 있다
);

-- DuckDB episode_members (Python build.py가 EPISODES에서 직접 쓴 표) : episode ↔ confirmed fact (M:N)
CREATE TABLE episode_member (
    episode_id              VARCHAR2(10)         NOT NULL,
    fact_id                 VARCHAR2(10)         NOT NULL,
    member_seq              NUMBER(2)            NOT NULL,
    clause                  VARCHAR2(200 CHAR)               -- 문장 전체를 쓰면 NULL, 절 분할(CF040·CF045)이면 절 원문
);

-- identity_register.csv : 확정하지 않는 동일성 대장 ID01–ID11 (open set / unresolved 관계)
CREATE TABLE identity_register (
    identity_id             VARCHAR2(10)         NOT NULL,
    surface_a               VARCHAR2(100 CHAR)   NOT NULL,
    surface_b               VARCHAR2(100 CHAR)   NOT NULL,
    status                  VARCHAR2(30)         NOT NULL,   -- RESOLVED / UNRESOLVED / ACCEPTED_BY_PROVENANCE / DOCUMENTED
    resolved_by             VARCHAR2(10),                    -- USER (사용자 확정일 때만)
    resolution_basis        VARCHAR2(300 CHAR),
    unresolved_reason       VARCHAR2(300 CHAR),
    model_relevance         VARCHAR2(100 CHAR)   NOT NULL,
    manual_decision_required VARCHAR2(3)         NOT NULL,
    review_decision         VARCHAR2(200 CHAR),
    context                 VARCHAR2(200 CHAR)   NOT NULL,
    referenced_facts        VARCHAR2(100)
);

-- identity_register.referenced_facts를 행으로 편 연결 테이블
CREATE TABLE identity_fact_ref (
    identity_id             VARCHAR2(10)         NOT NULL,
    fact_id                 VARCHAR2(10)         NOT NULL,
    ref_seq                 NUMBER(2)            NOT NULL
);

-- observed_edges.csv : observed edge 68개 (OBSERVED 4 / DERIVED 64)
CREATE TABLE dag_edge (
    edge_id                 VARCHAR2(10)         NOT NULL,
    src                     VARCHAR2(10)         NOT NULL,
    dst                     VARCHAR2(10)         NOT NULL,
    edge_type               VARCHAR2(30)         NOT NULL,
    basis                   VARCHAR2(100)        NOT NULL,   -- 원문 '|' 목록. 정규화본은 edge_basis_type
    status                  VARCHAR2(10)         NOT NULL,   -- OBSERVED / DERIVED
    claim_level             VARCHAR2(5)          NOT NULL,   -- 'True' / 'False' (CSV 원문. BOOLEAN 컬럼은 쓰지 않음)
    condition               VARCHAR2(50),                    -- 미확정 동일성 ID. 정규화본은 edge_identity_condition
    supporting              VARCHAR2(100)        NOT NULL,   -- 근거 fact/env 목록. 정규화본은 edge_source_basis
    rationale               VARCHAR2(200 CHAR)   NOT NULL,
    caution                 VARCHAR2(400 CHAR),
    uncertainty_status      VARCHAR2(40),
    review_decision         VARCHAR2(200 CHAR)
);

-- dag_edge.basis를 행으로 편 표 (edge 1 : N basis)
CREATE TABLE edge_basis_type (
    edge_id                 VARCHAR2(10)         NOT NULL,
    basis_code              VARCHAR2(30)         NOT NULL,
    basis_seq               NUMBER(2)            NOT NULL
);

-- dag_edge.supporting을 행으로 편 표 : edge ↔ 근거(source basis)
-- 근거는 confirmed fact(CF…) 또는 환경 행(E…) 둘 중 하나다 → 배타적 관계(arc)를 가상 컬럼 2개로 표현.
CREATE TABLE edge_source_basis (
    edge_id                 VARCHAR2(10)         NOT NULL,
    support_id              VARCHAR2(10)         NOT NULL,
    support_seq             NUMBER(2)            NOT NULL,
    fact_id                 VARCHAR2(10) GENERATED ALWAYS AS
                                (CASE WHEN SUBSTR(support_id, 1, 2) = 'CF' THEN support_id END) VIRTUAL,
    env_id                  VARCHAR2(10) GENERATED ALWAYS AS
                                (CASE WHEN SUBSTR(support_id, 1, 1) = 'E' THEN support_id END) VIRTUAL
);

-- dag_edge.condition을 행으로 편 표 : edge가 기대는 미확정 동일성
CREATE TABLE edge_identity_condition (
    edge_id                 VARCHAR2(10)         NOT NULL,
    identity_id             VARCHAR2(10)         NOT NULL
);

-- node_feature_links.csv : 제도·환경 피쳐 → node/edge 적합성 평가 링크 (creates_event = NO)
-- 대상(node 또는 edge)과 피쳐(제도 F… 또는 환경 E…)가 각각 다형(polymorphic) → 가상 컬럼으로 FK를 건다.
CREATE TABLE node_feature_link (
    link_id                 VARCHAR2(10)         NOT NULL,
    target_kind             VARCHAR2(4)          NOT NULL,   -- NODE / EDGE
    target_id               VARCHAR2(10)         NOT NULL,
    feature_layer           VARCHAR2(20)         NOT NULL,   -- INSTITUTIONAL / ENVIRONMENT
    feature_id              VARCHAR2(10)         NOT NULL,
    dimension               VARCHAR2(40)         NOT NULL,
    assessment              VARCHAR2(30)         NOT NULL,
    creates_event           VARCHAR2(3)          NOT NULL,
    rationale               VARCHAR2(200 CHAR)   NOT NULL,
    target_node_id          VARCHAR2(10) GENERATED ALWAYS AS
                                (CASE WHEN target_kind = 'NODE' THEN target_id END) VIRTUAL,
    target_edge_id          VARCHAR2(10) GENERATED ALWAYS AS
                                (CASE WHEN target_kind = 'EDGE' THEN target_id END) VIRTUAL,
    inst_feature_id         VARCHAR2(10) GENERATED ALWAYS AS
                                (CASE WHEN feature_layer = 'INSTITUTIONAL' THEN feature_id END) VIRTUAL,
    env_feature_id          VARCHAR2(10) GENERATED ALWAYS AS
                                (CASE WHEN feature_layer = 'ENVIRONMENT' THEN feature_id END) VIRTUAL
);

-- observed_dag_freeze.json : Stage 3 동결 기록(해시·집계)
CREATE TABLE dag_freeze (
    freeze_name             VARCHAR2(100)        NOT NULL,
    sha256                  CHAR(64)             NOT NULL,
    structure_sha256        CHAR(64)             NOT NULL,
    topology_sha256         CHAR(64)             NOT NULL,
    n_nodes                 NUMBER(5)            NOT NULL,
    n_edges                 NUMBER(5)            NOT NULL,
    n_episode_nodes         NUMBER(5)            NOT NULL,
    n_env_nodes             NUMBER(5)            NOT NULL,
    latent_count            NUMBER(5)            NOT NULL
);


-- =============================================================================
-- C. Gap · LATENT 후보 (Stage 4) — 동결 DAG 밖의 가설. observed 표와 섞지 않는다
-- =============================================================================

-- gaps.csv : 관측 사이의 빈칸 G01–G13
CREATE TABLE gap (
    gap_id                  VARCHAR2(10)         NOT NULL,
    title                   VARCHAR2(100 CHAR)   NOT NULL,
    gap_type                VARCHAR2(40)         NOT NULL,
    between_nodes           VARCHAR2(50)         NOT NULL,   -- CSV 'between'(Oracle 예약어라 이름 변경)
    observed_anchor_facts   VARCHAR2(100 CHAR)   NOT NULL,
    why_gap                 VARCHAR2(300 CHAR)   NOT NULL,
    gap_status              VARCHAR2(20)         NOT NULL,   -- OPEN / OPEN_UNRESOLVED
    review_decision         VARCHAR2(200 CHAR)
);

-- gaps.between('EP03|EP04')을 행으로 편 표 : gap이 걸친 관측 node
CREATE TABLE gap_anchor_node (
    gap_id                  VARCHAR2(10)         NOT NULL,
    node_id                 VARCHAR2(10)         NOT NULL,
    anchor_seq              NUMBER(2)            NOT NULL
);

-- latent_candidates.csv : gap별 LATENT 후보 38개 (재감사 필드 포함)
CREATE TABLE latent_candidate (
    candidate_id            VARCHAR2(10)         NOT NULL,
    gap_id                  VARCHAR2(10)         NOT NULL,
    status                  VARCHAR2(10)         NOT NULL,   -- 항상 LATENT
    form                    VARCHAR2(10)         NOT NULL,   -- SINGLE / MINI_DAG
    label                   VARCHAR2(100 CHAR)   NOT NULL,
    description             VARCHAR2(400 CHAR)   NOT NULL,
    source_consistency      VARCHAR2(12)         NOT NULL,
    temporal_fit            VARCHAR2(12)         NOT NULL,
    institutional_fit       VARCHAR2(12)         NOT NULL,
    role_fit                VARCHAR2(12)         NOT NULL,
    information_flow_fit    VARCHAR2(12)         NOT NULL,
    environmental_fit       VARCHAR2(12)         NOT NULL,
    contradiction_risk      VARCHAR2(12)         NOT NULL,
    n_assumptions           NUMBER(2)            NOT NULL,
    extra_assumptions       VARCHAR2(300 CHAR)   NOT NULL,
    identity_conditions     VARCHAR2(50),
    overall                 VARCHAR2(12)         NOT NULL,   -- final 등급
    prune_decision          VARCHAR2(60 CHAR)    NOT NULL,
    supports                VARCHAR2(150 CHAR),
    conflicts               VARCHAR2(200 CHAR),
    audit_attestation       VARCHAR2(100),
    support_basis           VARCHAR2(30)         NOT NULL,
    notes                   VARCHAR2(600 CHAR),
    observed_left           VARCHAR2(150 CHAR)   NOT NULL,
    observed_right          VARCHAR2(150 CHAR)   NOT NULL,
    latent_bridge_claim     VARCHAR2(200 CHAR)   NOT NULL,
    bridge_directly_attested VARCHAR2(10)        NOT NULL,   -- YES / NO / PARTIAL
    endpoint_support        VARCHAR2(50 CHAR)    NOT NULL,
    source_support          VARCHAR2(10)         NOT NULL,
    bridge_evidence         VARCHAR2(100),
    bridge_basis            VARCHAR2(100)        NOT NULL,
    evidence_grade          VARCHAR2(10)         NOT NULL,
    plausibility_grade      VARCHAR2(12)         NOT NULL,
    source_consistency_v1   VARCHAR2(12)         NOT NULL,
    overall_v1              VARCHAR2(12)         NOT NULL,
    reaudit_reason          VARCHAR2(400 CHAR)   NOT NULL
);

-- latent_elements.csv : 후보 안의 LATENT node(47)·edge(72). 끝점(src/dst)은 관측 node 또는 같은 후보의 LN_ node
CREATE TABLE latent_element (
    element_id              VARCHAR2(20)         NOT NULL,
    candidate_id            VARCHAR2(10)         NOT NULL,
    kind                    VARCHAR2(4)          NOT NULL,   -- node / edge (CSV 원문 소문자)
    status                  VARCHAR2(10)         NOT NULL,   -- 항상 LATENT
    src                     VARCHAR2(20),
    dst                     VARCHAR2(20),
    edge_type               VARCHAR2(30),
    text                    VARCHAR2(200 CHAR)
);

-- latent_candidates.identity_conditions를 행으로 편 표
CREATE TABLE candidate_identity_condition (
    candidate_id            VARCHAR2(10)         NOT NULL,
    identity_id             VARCHAR2(10)         NOT NULL
);

-- latent_candidates.bridge_evidence / audit_attestation을 행으로 편 표
-- 근거는 confirmed fact(CF…) 또는 audit 명제(V3P…) → 배타적 관계(arc)를 가상 컬럼으로 표현
CREATE TABLE candidate_evidence (
    candidate_id            VARCHAR2(10)         NOT NULL,
    evidence_role           VARCHAR2(20)         NOT NULL,   -- BRIDGE_EVIDENCE / AUDIT_ATTESTATION
    evidence_id             VARCHAR2(10)         NOT NULL,
    evidence_seq            NUMBER(2)            NOT NULL,
    fact_id                 VARCHAR2(10) GENERATED ALWAYS AS
                                (CASE WHEN SUBSTR(evidence_id, 1, 2) = 'CF' THEN evidence_id END) VIRTUAL,
    prop_id                 VARCHAR2(10) GENERATED ALWAYS AS
                                (CASE WHEN SUBSTR(evidence_id, 1, 3) = 'V3P' THEN evidence_id END) VIRTUAL
);

-- latent_candidates.bridge_basis를 행으로 편 표
CREATE TABLE candidate_bridge_basis (
    candidate_id            VARCHAR2(10)         NOT NULL,
    basis_code              VARCHAR2(30)         NOT NULL
);


-- =============================================================================
-- D. Narrative world (Stage 5)
-- =============================================================================

-- narrative_worlds.csv : W1–W5 경쟁 설명, W6 배제된 설명
CREATE TABLE narrative_world (
    world_id                VARCHAR2(5)          NOT NULL,
    name                    VARCHAR2(100 CHAR)   NOT NULL,
    status                  VARCHAR2(30)         NOT NULL,   -- COMPETING_EXPLANATION / REJECTED
    latent_bridges          VARCHAR2(100)        NOT NULL,   -- 원문 목록. 정규화본은 world_candidate
    unresolved_gaps         VARCHAR2(100)        NOT NULL,
    institutional_fit       VARCHAR2(12)         NOT NULL,
    environmental_fit       VARCHAR2(12)         NOT NULL,
    n_assumptions           NUMBER(3)            NOT NULL,
    min_grade               VARCHAR2(12)         NOT NULL,
    main_assumptions        VARCHAR2(400 CHAR)   NOT NULL,
    main_weaknesses         VARCHAR2(600 CHAR)   NOT NULL,
    contradicted_evidence   VARCHAR2(300 CHAR)   NOT NULL,
    story_implication       VARCHAR2(300 CHAR)   NOT NULL,
    identity_conditions     VARCHAR2(50),
    resolved_identities     VARCHAR2(50),
    evidence_profile        VARCHAR2(50)         NOT NULL,
    work_role               VARCHAR2(200 CHAR)   NOT NULL,
    story_question          VARCHAR2(100 CHAR)   NOT NULL,
    difference              VARCHAR2(200 CHAR)   NOT NULL,
    unique_bridges          VARCHAR2(50),
    narrative               CLOB                 NOT NULL    -- 최대 3,248 byte. 긴 서술이라 CLOB
);

-- world ↔ 후보 (M:N). (candidate_id, gap_id)를 함께 들고 있어 "world마다 gap당 후보 1개"를 UNIQUE로 강제한다
CREATE TABLE world_candidate (
    world_id                VARCHAR2(5)          NOT NULL,
    candidate_id            VARCHAR2(10)         NOT NULL,
    gap_id                  VARCHAR2(10)         NOT NULL,
    bridge_seq              NUMBER(2)            NOT NULL
);

-- world가 메우지 않고 남긴 gap (narrative_worlds.unresolved_gaps)
CREATE TABLE world_unresolved_gap (
    world_id                VARCHAR2(5)          NOT NULL,
    gap_id                  VARCHAR2(10)         NOT NULL
);

-- world ↔ 동일성 (identity_conditions = CONDITION, resolved_identities = RESOLVED)
CREATE TABLE world_identity (
    world_id                VARCHAR2(5)          NOT NULL,
    identity_id             VARCHAR2(10)         NOT NULL,
    identity_role           VARCHAR2(10)         NOT NULL    -- CONDITION / RESOLVED
);


-- =============================================================================
-- E. Mechanism Super-DAG (Stage 6)
-- =============================================================================

-- mechanism_definitions.csv : 메커니즘 7개 (M1–M6, MB)
CREATE TABLE mechanism (
    mechanism_id            VARCHAR2(5)          NOT NULL,
    mechanism_name          VARCHAR2(50)         NOT NULL,
    easy_description        VARCHAR2(200 CHAR)   NOT NULL,   -- CSV '아주 쉬운 설명'
    related_candidates      VARCHAR2(100)        NOT NULL,   -- CSV '관련 candidate'
    related_observed_nodes  VARCHAR2(200)        NOT NULL,   -- CSV '관련 observed node'
    required_inst_features  VARCHAR2(100)        NOT NULL,   -- CSV '필요한 institutional feature'
    related_env_features    VARCHAR2(50)         NOT NULL,   -- CSV '관련 environment feature'
    evidence_status         VARCHAR2(150 CHAR)   NOT NULL,   -- CSV 'evidence status'
    remarks                 VARCHAR2(300 CHAR)   NOT NULL,   -- CSV '비고'
    n_candidates            NUMBER(3)            NOT NULL,
    branch                  VARCHAR2(20)         NOT NULL
);

-- 후보 → 메커니즘 매핑 (Super-DAG edge INSTANTIATED_BY / INSTANTIATED_BY_SECONDARY에서 추출)
CREATE TABLE candidate_mechanism (
    candidate_id            VARCHAR2(10)         NOT NULL,
    mechanism_id            VARCHAR2(5)          NOT NULL,
    mapping_role            VARCHAR2(10)         NOT NULL    -- PRIMARY / SECONDARY
);

-- world_mechanism_configurations.csv(가로 M1..MB 컬럼)를 UNPIVOT으로 세로로 편 표
CREATE TABLE world_mechanism_config (
    world_id                VARCHAR2(5)          NOT NULL,
    mechanism_id            VARCHAR2(5)          NOT NULL,
    config_value            VARCHAR2(12)         NOT NULL,   -- ON / OFF / PARTIAL / UNSPECIFIED
    config_basis            VARCHAR2(100 CHAR)   NOT NULL
);

-- mechanism_interaction_matrix.csv : 메커니즘 쌍의 공존 분석 (21쌍)
-- CSV의 mechanism_a/mechanism_b(이름)는 mechanism 표에서 얻을 수 있어 정규화(3NF)로 뺐다(staging에는 남음)
CREATE TABLE mechanism_interaction (
    mechanism_a_id          VARCHAR2(5)          NOT NULL,   -- CSV 'mechanism A'
    mechanism_b_id          VARCHAR2(5)          NOT NULL,   -- CSV 'mechanism B'
    coexistence             VARCHAR2(25)         NOT NULL,
    reason                  VARCHAR2(200 CHAR)   NOT NULL,   -- CSV '이유'
    conflicting_items       VARCHAR2(50 CHAR),               -- CSV '충돌하는 candidate/edge'
    explained_together      VARCHAR2(150 CHAR)   NOT NULL,   -- CSV '같이 있을 때 설명되는 것'
    relation                VARCHAR2(50)         NOT NULL,
    cooccur_worlds          VARCHAR2(50)
);

-- qualitative_structural_rules.csv : 질적 구조 변수 10개 (OR / AND / XOR / ANCHORED)
CREATE TABLE structural_rule (
    var_id                  VARCHAR2(30)         NOT NULL,   -- CSV 'var'
    gap                     VARCHAR2(20),
    target                  VARCHAR2(50)         NOT NULL,
    op                      VARCHAR2(10)         NOT NULL,
    inputs                  VARCHAR2(100)        NOT NULL,
    rule                    VARCHAR2(200 CHAR)   NOT NULL,
    rule_desc               VARCHAR2(200 CHAR)   NOT NULL,   -- CSV 'desc'(예약어)
    constraint_text         VARCHAR2(100 CHAR)   NOT NULL,   -- CSV 'constraint'
    input_candidates        VARCHAR2(100)
);

-- mechanism_interventions.csv : do(M=OFF) 질적 개입 결과 13건
CREATE TABLE mechanism_intervention (
    mechanism_id            VARCHAR2(5)          NOT NULL,   -- CSV 'mechanism'
    variable                VARCHAR2(30)         NOT NULL,
    target                  VARCHAR2(10)         NOT NULL,
    result                  VARCHAR2(15)         NOT NULL,   -- PATH_REMAINS / PATH_WEAKENS / PATH_BREAKS / UNKNOWN
    removed                 VARCHAR2(50)         NOT NULL,
    remaining               VARCHAR2(50),
    affected_worlds         VARCHAR2(50)         NOT NULL,
    note                    VARCHAR2(300 CHAR)   NOT NULL
);

-- 개입에서 제거된(REMOVED)·남은(REMAINING) 후보를 행으로 편 표
CREATE TABLE intervention_candidate (
    mechanism_id            VARCHAR2(5)          NOT NULL,
    variable                VARCHAR2(30)         NOT NULL,
    candidate_id            VARCHAR2(10)         NOT NULL,
    effect                  VARCHAR2(10)         NOT NULL    -- REMOVED / REMAINING
);

-- mechanism_super_dag_nodes.csv : Super-DAG node 122개
CREATE TABLE sd_node (
    node_id                 VARCHAR2(30)         NOT NULL,
    sd_status               VARCHAR2(20)         NOT NULL,   -- OBSERVED / LATENT_MECHANISM / CONTEXT / UNRESOLVED
    node_type               VARCHAR2(30)         NOT NULL,
    label                   VARCHAR2(100 CHAR)   NOT NULL,
    frozen_status           VARCHAR2(10),
    branch                  VARCHAR2(20),
    mechanism               VARCHAR2(5),
    worlds                  VARCHAR2(30 CHAR)    NOT NULL,
    detail                  VARCHAR2(400 CHAR)   NOT NULL
);

-- mechanism_super_dag_edges.csv : Super-DAG edge 205개 (FROZEN 68 + SUPER_DAG 137)
CREATE TABLE sd_edge (
    edge_id                 VARCHAR2(10)         NOT NULL,
    src                     VARCHAR2(30)         NOT NULL,
    dst                     VARCHAR2(30)         NOT NULL,
    edge_type               VARCHAR2(30)         NOT NULL,
    sd_status               VARCHAR2(20)         NOT NULL,   -- OBSERVED / DERIVED / LATENT_MECHANISM / CONTEXT / UNRESOLVED
    origin                  VARCHAR2(10)         NOT NULL,   -- FROZEN / SUPER_DAG
    note                    VARCHAR2(200 CHAR)   NOT NULL
);


-- =============================================================================
-- F. Audit 기록 (Python 결과 — Oracle 재검증의 비교 대상)
-- =============================================================================

-- warn_dispositions.csv : WARN 처리 내역
CREATE TABLE warn_disposition (
    warning_id              VARCHAR2(10)         NOT NULL,
    audit_stage             VARCHAR2(10)         NOT NULL,
    affected_item           VARCHAR2(10)         NOT NULL,
    warning_type            VARCHAR2(30)         NOT NULL,
    original_text           VARCHAR2(300 CHAR)   NOT NULL,
    generated_text          VARCHAR2(200 CHAR)   NOT NULL,
    risk                    VARCHAR2(200 CHAR)   NOT NULL,
    disposition             VARCHAR2(20)         NOT NULL,
    justification           VARCHAR2(400 CHAR)   NOT NULL,
    fixed_text              VARCHAR2(300 CHAR)   NOT NULL,
    final_status            VARCHAR2(20)         NOT NULL,
    final_classification    VARCHAR2(50 CHAR)    NOT NULL,
    unresolved_reason       VARCHAR2(300 CHAR)
);

-- DuckDB audit_findings : Python Audit 1–5가 낸 finding 62건
CREATE TABLE py_audit_finding (
    finding_seq             NUMBER(5)            NOT NULL,
    audit_name              VARCHAR2(10)         NOT NULL,   -- DuckDB 'audit'(예약어)
    check_name              VARCHAR2(40)         NOT NULL,
    severity                VARCHAR2(12)         NOT NULL,
    target                  VARCHAR2(40)         NOT NULL,
    message                 VARCHAR2(800 CHAR)   NOT NULL
);


-- =============================================================================
-- G. 규칙 참조표 — Python 상수를 옮긴 것(출처 파일·줄을 rule_source에 적는다)
--    Oracle audit SQL은 Python 코드를 호출하지 않고 이 표만 본다.
-- =============================================================================

-- 이름 붙은 집합(set) 상수. 예: 'TESTIMONY_LAYER' = {TESTIMONY, NESTED_TESTIMONY}
CREATE TABLE rule_set_member (
    rule_set                VARCHAR2(40)         NOT NULL,
    member_id               VARCHAR2(40)         NOT NULL,
    member_group            VARCHAR2(40 CHAR),
    rule_source             VARCHAR2(100)        NOT NULL
);

-- audits.py REQUIRED_RELATIONS : 반드시 있어야 하는 관계 17개
CREATE TABLE rule_required_relation (
    src                     VARCHAR2(10)         NOT NULL,
    dst                     VARCHAR2(10)         NOT NULL,
    edge_type               VARCHAR2(30)         NOT NULL,
    reason                  VARCHAR2(100 CHAR)   NOT NULL
);

-- audits.py IDENTITY_SENSITIVE : 이 node 쌍을 잇는 edge는 해당 동일성 condition이 필요
CREATE TABLE rule_identity_sensitive_pair (
    node_a                  VARCHAR2(10)         NOT NULL,
    node_b                  VARCHAR2(10)         NOT NULL,
    identity_id             VARCHAR2(10)         NOT NULL
);

-- stage5_worlds.py CONFLICT_PAIRS : 한 world에 함께 둘 수 없는 후보 쌍
CREATE TABLE rule_conflict_pair (
    candidate_a             VARCHAR2(10)         NOT NULL,
    candidate_b             VARCHAR2(10)         NOT NULL,
    reason                  VARCHAR2(200 CHAR)   NOT NULL
);

-- stage6_mechanisms.py CAND_MAP의 negates 열 : 후보가 부정하는 메커니즘
CREATE TABLE rule_candidate_negates (
    candidate_id            VARCHAR2(10)         NOT NULL,
    mechanism_id            VARCHAR2(5)          NOT NULL
);

-- audits.py IDENTITY_RULES : 원문 표면형 → 동일성 후보 이름
CREATE TABLE rule_identity_surface (
    surface_form            VARCHAR2(30 CHAR)    NOT NULL,
    resolved_name           VARCHAR2(30 CHAR)    NOT NULL,
    identity_id             VARCHAR2(10)         NOT NULL
);

-- audits.py의 정규식 규칙을 Oracle 정규식(POSIX ERE + \s \S \d)으로 옮긴 것
CREATE TABLE rule_text_pattern (
    pattern_id              VARCHAR2(30)         NOT NULL,
    check_name              VARCHAR2(40)         NOT NULL,
    oracle_regex            VARCHAR2(400 CHAR)   NOT NULL,
    python_regex            VARCHAR2(400 CHAR)   NOT NULL,
    note                    VARCHAR2(200 CHAR)
);


-- =============================================================================
-- H. 검증·적재 기록
-- =============================================================================

-- Python 산출물에서 읽은 기대값 (08_validation/expected_counts.sql이 채운다)
CREATE TABLE expected_count (
    metric_id               VARCHAR2(60)         NOT NULL,
    expected_value          NUMBER               NOT NULL,
    python_source           VARCHAR2(200)        NOT NULL,
    description             VARCHAR2(200 CHAR)
);

-- 적재 기록 : DATE와 TIMESTAMP의 차이를 보여 주는 유일한 표(사건 날짜와 무관)
CREATE TABLE load_log (
    load_step               VARCHAR2(60)         NOT NULL,
    table_name              VARCHAR2(30)         NOT NULL,
    row_count               NUMBER               NOT NULL,
    load_day                DATE          DEFAULT TRUNC(SYSDATE)  NOT NULL,   -- 초 단위까지(여기서는 날짜만)
    loaded_at               TIMESTAMP(6)  DEFAULT SYSTIMESTAMP    NOT NULL    -- 소수점 이하 초까지
);
