-- =============================================================================
-- 04_comments.sql — 데이터 사전(COMMENT ON). USER_TAB_COMMENTS / USER_COL_COMMENTS로 조회한다.
--   SELECT table_name, comments FROM user_tab_comments ORDER BY table_name;
-- =============================================================================

-- A. 원천 입력 pack
COMMENT ON TABLE input_manifest IS '00_INPUT_MANIFEST.csv: 입력 파일 역할과 DAG 입력 허용 여부';
COMMENT ON TABLE source_record IS '04_source_records.csv: 사료 기사 8건(실록·비변사등록·승정원일기)';
COMMENT ON TABLE ref_confirmation_level IS 'stage1_episodes.py EPISTEMIC_RANK + audits.py FAMILY: 확인 수준별 인식 등급·계열';
COMMENT ON TABLE confirmed_fact IS '01_confirmed_facts.csv: 확정 사실 50개. episode node의 유일한 근거';
COMMENT ON TABLE audit_proposition IS '05_source_faithful_propositions_AUDIT_ONLY.csv: 감사 전용 명제 156개. DAG 입력 아님';
COMMENT ON TABLE fact_proposition IS 'confirmed_fact.source_prop_ids 정규화: 확정 사실 ↔ audit 명제 (M:N)';
COMMENT ON TABLE institutional_feature IS '02 제도 피쳐 F001–F020: 가능성 경계(제약조건). 사건을 만들지 않음';
COMMENT ON TABLE environment_context IS '03 환경 E001–E004: CONTEXT. 개인 수준 사실을 만들지 않음';

COMMENT ON COLUMN confirmed_fact.record_lunar_date IS '기록일(사료 날짜, 음력). 발생일과 다르다';
COMMENT ON COLUMN confirmed_fact.occurrence_lunar_text IS '발생일 원문(음력). 사료에 없으면 NULL — 임의 날짜를 만들지 않는다';
COMMENT ON COLUMN confirmed_fact.chronology IS '사건 흐름상 시점 서술(음력). 정렬용 정수는 dag_node.t_min/t_max';
COMMENT ON COLUMN audit_proposition.set_status IS 'OPEN_SET이면 원문이 열린 목록(…등)이다. 닫힌 목록으로 바꾸면 안 됨';

-- B. Observed DAG
COMMENT ON TABLE dag_node IS 'episode_nodes.csv: 동결된 observed node 41개(episode 37 + 환경 4). 모두 OBSERVED';
COMMENT ON COLUMN dag_node.t_min IS '발생 구간 시작, 음력 MMDD 정수(예: 2월 28일 = 228). 모르면 NULL';
COMMENT ON COLUMN dag_node.t_max IS '발생 구간 끝, 음력 MMDD 정수. 열린 구간(…이후)이면 NULL';
COMMENT ON COLUMN dag_node.record_lunar_date IS '기록일. 발생 시점(t_min/t_max)으로 쓰면 occurrence_record_confusion';
COMMENT ON COLUMN dag_node.env_id IS '환경 node(layer=ENVIRONMENT)만 값이 있다';
COMMENT ON TABLE episode_member IS 'DuckDB episode_members: episode ↔ confirmed fact. clause는 절 분할(CF040·CF045)일 때만';
COMMENT ON TABLE identity_register IS 'identity_register.csv: 동일성 대장. UNRESOLVED는 오류가 아니라 보존된 불확실성';
COMMENT ON COLUMN identity_register.status IS 'RESOLVED(사용자 확정) / UNRESOLVED / ACCEPTED_BY_PROVENANCE / DOCUMENTED';
COMMENT ON TABLE identity_fact_ref IS 'identity_register.referenced_facts 정규화';
COMMENT ON TABLE dag_edge IS 'observed_edges.csv: observed edge 68개. CAUSES edge 없음';
COMMENT ON COLUMN dag_edge.claim_level IS '''True''면 진술 내용 속 순서를 이은 edge(객관적 사건 순서로 확정한 것 아님)';
COMMENT ON COLUMN dag_edge.condition IS '이 edge가 기대는 미확정 동일성 ID. 값이 있으면 조건부로만 성립';
COMMENT ON COLUMN dag_edge.supporting IS '근거 confirmed fact / 환경 행 목록(원문). 정규화본: edge_source_basis';
COMMENT ON TABLE edge_basis_type IS 'dag_edge.basis 정규화: SOURCE_DIRECT / TEMPORAL / PROCEDURAL / ENVIRONMENTAL_CONTEXT …';
COMMENT ON TABLE edge_source_basis IS 'dag_edge.supporting 정규화: edge ↔ 근거(fact 또는 환경). 가상 컬럼 fact_id/env_id로 배타적 FK';
COMMENT ON TABLE edge_identity_condition IS 'dag_edge.condition 정규화: edge ↔ 미확정 동일성';
COMMENT ON TABLE node_feature_link IS 'node_feature_links.csv: 제도·환경 피쳐 적합성 평가 링크(creates_event = NO)';
COMMENT ON TABLE dag_freeze IS 'observed_dag_freeze.json: Stage 3 동결 해시와 집계';

-- C. Gap · LATENT
COMMENT ON TABLE gap IS 'gaps.csv: 관측 사이의 빈칸 13개';
COMMENT ON COLUMN gap.between_nodes IS 'CSV between(예약어라 이름 변경): gap이 걸친 관측 node 목록';
COMMENT ON TABLE gap_anchor_node IS 'gap.between_nodes 정규화';
COMMENT ON TABLE latent_candidate IS 'latent_candidates.csv: gap별 LATENT 후보 38개. 관측 사실이 아니다';
COMMENT ON COLUMN latent_candidate.overall IS 'final 등급 = min(evidence_grade, plausibility_grade). 재감사 뒤 HIGH 0개';
COMMENT ON COLUMN latent_candidate.source_support IS 'bridge 자체의 사료 근거만 평가(endpoint·시간 인접·제도 가능성 제외)';
COMMENT ON TABLE latent_element IS 'latent_elements.csv: 후보 안의 LATENT node·edge. id 접두어 LN_';
COMMENT ON TABLE candidate_identity_condition IS 'latent_candidate.identity_conditions 정규화';
COMMENT ON TABLE candidate_evidence IS 'bridge_evidence / audit_attestation 정규화: 후보 ↔ fact 또는 audit 명제';
COMMENT ON TABLE candidate_bridge_basis IS 'latent_candidate.bridge_basis 정규화';

-- D. World
COMMENT ON TABLE narrative_world IS 'narrative_worlds.csv: W1–W5 경쟁 설명(COMPETING_EXPLANATION), W6 배제(REJECTED)';
COMMENT ON COLUMN narrative_world.narrative IS '서사 본문(CLOB). [L] 표지가 LATENT 부분';
COMMENT ON TABLE world_candidate IS 'world ↔ 후보 bridge. UNIQUE(world_id, gap_id)로 gap당 후보 1개';
COMMENT ON TABLE world_unresolved_gap IS 'world가 메우지 않고 남긴 gap';
COMMENT ON TABLE world_identity IS 'world ↔ 동일성(CONDITION: 미확정 가정, RESOLVED: 사용자 확정 사용)';

-- E. Mechanism
COMMENT ON TABLE mechanism IS 'mechanism_definitions.csv: 메커니즘 M1–M6, MB (분석 변수, LATENT_MECHANISM)';
COMMENT ON TABLE candidate_mechanism IS 'Super-DAG INSTANTIATED_BY(_SECONDARY) edge에서 뽑은 후보 → 메커니즘 매핑';
COMMENT ON TABLE world_mechanism_config IS 'world_mechanism_configurations.csv를 UNPIVOT: world × 메커니즘 = ON/OFF/PARTIAL/UNSPECIFIED';
COMMENT ON COLUMN world_mechanism_config.config_value IS 'UNSPECIFIED는 OFF가 아니다(작동 여부를 말하지 않음)';
COMMENT ON TABLE mechanism_interaction IS 'mechanism_interaction_matrix.csv: 메커니즘 쌍 공존 분석 21쌍';
COMMENT ON TABLE structural_rule IS 'qualitative_structural_rules.csv: 질적 구조 변수(OR/AND/XOR/ANCHORED)';
COMMENT ON TABLE mechanism_intervention IS 'mechanism_interventions.csv: do(M=OFF) 질적 개입 결과';
COMMENT ON TABLE intervention_candidate IS '개입으로 제거된(REMOVED)·남은(REMAINING) 후보';
COMMENT ON TABLE sd_node IS 'mechanism_super_dag_nodes.csv: Super-DAG node 122개';
COMMENT ON TABLE sd_edge IS 'mechanism_super_dag_edges.csv: Super-DAG edge 205개(FROZEN 68 = 동결 edge 복사)';

-- F. Audit 기록
COMMENT ON TABLE warn_disposition IS 'warn_dispositions.csv: WARN 처리 내역(FIXED / RECLASSIFIED_INFO / UNRESOLVED / ESCALATED_ERROR)';
COMMENT ON TABLE py_audit_finding IS 'DuckDB audit_findings: Python Audit 1–5 결과. Oracle audit SQL 결과와 비교하는 대상';

-- G. 규칙
COMMENT ON TABLE rule_set_member IS 'Python 집합 상수(TESTIMONY_LAYERS, FORBIDDEN_DIRECT, BRANCH_A/B …)를 옮긴 표';
COMMENT ON TABLE rule_required_relation IS 'audits.py REQUIRED_RELATIONS';
COMMENT ON TABLE rule_identity_sensitive_pair IS 'audits.py IDENTITY_SENSITIVE';
COMMENT ON TABLE rule_conflict_pair IS 'stage5_worlds.py CONFLICT_PAIRS';
COMMENT ON TABLE rule_candidate_negates IS 'stage6_mechanisms.py CAND_MAP negates 열';
COMMENT ON TABLE rule_identity_surface IS 'audits.py IDENTITY_RULES';
COMMENT ON TABLE rule_text_pattern IS 'audits.py 정규식을 Oracle 정규식으로 옮긴 표(원문 Python 정규식 병기)';

-- H. 검증·적재
COMMENT ON TABLE expected_count IS 'Python 산출물에서 읽은 기대값. 08_validation/expected_counts.sql';
COMMENT ON TABLE load_log IS '적재 기록. load_day(DATE)와 loaded_at(TIMESTAMP) 비교용';
COMMENT ON COLUMN load_log.load_day IS 'DATE: 연월일 + 시분초(초 이하 없음). 여기서는 TRUNC로 날짜만';
COMMENT ON COLUMN load_log.loaded_at IS 'TIMESTAMP(6): 마이크로초까지';
