-- =============================================================================
-- 02_insert_examples.sql — INSERT script
-- -----------------------------------------------------------------------------
-- 1부(필수): 참조표·규칙표를 채운다. 값은 Python 코드의 상수를 그대로 옮겼다(출처 = rule_source).
--            Oracle audit SQL은 Python을 호출하지 않고 이 표만 읽는다.
-- 2부(연습): SQLD DML 연습 — INSERT ALL / UPDATE / DELETE / MERGE / SAVEPOINT / ROLLBACK.
--            모든 변경은 마지막에 ROLLBACK 되므로 canonical 데이터는 바뀌지 않는다.
-- 실행 순서: 01_schema → 00_staging_tables → (적재) → 이 파일 1부 → 04_transform_to_canonical
--           (ref_confirmation_level은 confirmed_fact의 FK 부모라 transform보다 먼저 넣는다)
-- =============================================================================
SET DEFINE OFF

-- =============================================================================
-- 1부. 참조표·규칙표
-- =============================================================================

-- stage1_episodes.py EPISTEMIC_RANK + audits.py FAMILY ------------------------
-- INSERT ALL … SELECT * FROM dual : Oracle 23ai 이전에는 VALUES 여러 행을 한 문장에 못 쓴다(SQLD 단골)
INSERT ALL
    INTO ref_confirmation_level VALUES ('RECORDED_NESTED_TESTIMONY',              0, 'TESTIMONY')
    INTO ref_confirmation_level VALUES ('RECORDED_TESTIMONY',                     1, 'TESTIMONY')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_OFFICIAL_EVALUATION',         2, 'OFFICIAL')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_OFFICIAL_REPORT',             2, 'OFFICIAL')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_INSPECTOR_REPORT',            2, 'OFFICIAL')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_OFFICIAL_FINDING',            3, 'OFFICIAL')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT', 3, 'MIXED')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_ROYAL_JUDGMENT',              3, 'ROYAL')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_ROYAL_JUDGMENT_AND_ORDER',    4, 'ROYAL')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_ROYAL_ORDER',                 4, 'ROYAL')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_COURT_ACTION',                4, 'COURT')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_OFFICIAL_ACTION',             4, 'OFFICIAL')
    INTO ref_confirmation_level VALUES ('DOCUMENTED_SOURCE_IDENTIFICATION',       4, 'IDENT')
SELECT * FROM dual;

-- 이름 붙은 집합 상수 ----------------------------------------------------------
INSERT ALL
    -- audits.py TESTIMONY_LAYERS
    INTO rule_set_member VALUES ('TESTIMONY_LAYER', 'TESTIMONY',        NULL, 'audits.py TESTIMONY_LAYERS')
    INTO rule_set_member VALUES ('TESTIMONY_LAYER', 'NESTED_TESTIMONY', NULL, 'audits.py TESTIMONY_LAYERS')
    -- audits.py JUDGMENT_LAYERS (환경 context가 들어갈 수 있는 판단·보고 layer)
    INTO rule_set_member VALUES ('JUDGMENT_LAYER', 'ROYAL_JUDGMENT',           NULL, 'audits.py JUDGMENT_LAYERS')
    INTO rule_set_member VALUES ('JUDGMENT_LAYER', 'ROYAL_JUDGMENT_AND_ORDER', NULL, 'audits.py JUDGMENT_LAYERS')
    INTO rule_set_member VALUES ('JUDGMENT_LAYER', 'OFFICIAL_EVALUATION',      NULL, 'audits.py JUDGMENT_LAYERS')
    INTO rule_set_member VALUES ('JUDGMENT_LAYER', 'OFFICIAL_FINDING',         NULL, 'audits.py JUDGMENT_LAYERS')
    INTO rule_set_member VALUES ('JUDGMENT_LAYER', 'OFFICIAL_REPORT',          NULL, 'audits.py JUDGMENT_LAYERS')
    INTO rule_set_member VALUES ('JUDGMENT_LAYER', 'INSPECTOR_REPORT',         NULL, 'audits.py JUDGMENT_LAYERS')
    -- audits.py ALLOWED_FAMILY_MIX: 한 episode 안에서 섞여도 되는 인식 계열 조합
    INTO rule_set_member VALUES ('ALLOWED_FAMILY_MIX', 'TESTIMONY', 'MIX1', 'audits.py ALLOWED_FAMILY_MIX')
    INTO rule_set_member VALUES ('ALLOWED_FAMILY_MIX', 'IDENT',     'MIX1', 'audits.py ALLOWED_FAMILY_MIX')
    -- audits.py FORBIDDEN_DIRECT: 구순 관련 node → 김명신 사망/사인 node 직접 연결 금지
    INTO rule_set_member VALUES ('FORBIDDEN_DIRECT_SRC', 'EP01', NULL, 'audits.py FORBIDDEN_DIRECT')
    INTO rule_set_member VALUES ('FORBIDDEN_DIRECT_SRC', 'EP08', NULL, 'audits.py FORBIDDEN_DIRECT')
    INTO rule_set_member VALUES ('FORBIDDEN_DIRECT_SRC', 'EP10', NULL, 'audits.py FORBIDDEN_DIRECT')
    INTO rule_set_member VALUES ('FORBIDDEN_DIRECT_SRC', 'EP29', NULL, 'audits.py FORBIDDEN_DIRECT')
    INTO rule_set_member VALUES ('FORBIDDEN_DIRECT_DST', 'EP13', NULL, 'audits.py FORBIDDEN_DIRECT')
    INTO rule_set_member VALUES ('FORBIDDEN_DIRECT_DST', 'EP26', NULL, 'audits.py FORBIDDEN_DIRECT')
    INTO rule_set_member VALUES ('FORBIDDEN_DIRECT_DST', 'EP27', NULL, 'audits.py FORBIDDEN_DIRECT')
    -- audits.py audit2 judgment_flattening: 지워지면 안 되는 판단 node
    INTO rule_set_member VALUES ('JUDGMENT_NODE', 'EP15', NULL, 'audits.py audit2 judgment_flattening')
    INTO rule_set_member VALUES ('JUDGMENT_NODE', 'EP17', NULL, 'audits.py audit2 judgment_flattening')
    INTO rule_set_member VALUES ('JUDGMENT_NODE', 'EP24', NULL, 'audits.py audit2 judgment_flattening')
    INTO rule_set_member VALUES ('JUDGMENT_NODE', 'EP25', NULL, 'audits.py audit2 judgment_flattening')
    INTO rule_set_member VALUES ('JUDGMENT_NODE', 'EP26', NULL, 'audits.py audit2 judgment_flattening')
    INTO rule_set_member VALUES ('JUDGMENT_NODE', 'EP27', NULL, 'audits.py audit2 judgment_flattening')
    INTO rule_set_member VALUES ('JUDGMENT_NODE', 'EP28', NULL, 'audits.py audit2 judgment_flattening')
    INTO rule_set_member VALUES ('JUDGMENT_NODE', 'EP29', NULL, 'audits.py audit2 judgment_flattening')
    INTO rule_set_member VALUES ('JUDGMENT_NODE', 'EP30', NULL, 'audits.py audit2 judgment_flattening')
    -- audits.py audit2: endpoint 밖이어도 REVIEW_OF 근거로 허용되는 fact(안핵 명령)
    INTO rule_set_member VALUES ('EXTRA_SUPPORT_OK', 'CF035', 'REVIEW_OF', 'audits.py audit2 extra_ok')
SELECT * FROM dual;

INSERT ALL
    -- stage5_worlds.py COMMON_OUTCOME_NODES: 모든 world에 공통인 OBSERVED 결말
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP15', '재검토 과정', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP16', '재검토 과정', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP17', '재검토 과정', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP18', '재검토 과정', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP19', '재검토 과정', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP20', '재검토 과정', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP21', '재검토 과정', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP22', '재검토 과정', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP23', '재검토 과정', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP24', '최종 판단', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP25', '최종 판단', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP26', '최종 판단', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP27', '최종 판단', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP28', '최종 판단', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP29', '최종 판단', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP30', '최종 판단', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP31', '최종 판단', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP32', '최종 판단', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP33', '처분', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP34', '처분', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP35', '처분', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP36', '처분', 'stage5_worlds.py COMMON_OUTCOME_NODES')
    INTO rule_set_member VALUES ('COMMON_OUTCOME', 'EP37', '처분', 'stage5_worlds.py COMMON_OUTCOME_NODES')
SELECT * FROM dual;

INSERT ALL
    -- stage6_mechanisms.py BRANCH_A(생물학적 사인) / BRANCH_B(절차·책임)
    INTO rule_set_member VALUES ('BRANCH_A', 'MB',               NULL, 'stage6_mechanisms.py BRANCH_A')
    INTO rule_set_member VALUES ('BRANCH_A', 'V_CUSTODY_COURSE', NULL, 'stage6_mechanisms.py BRANCH_A')
    INTO rule_set_member VALUES ('BRANCH_A', 'EP26',             NULL, 'stage6_mechanisms.py BRANCH_A')
    INTO rule_set_member VALUES ('BRANCH_A', 'EP27',             NULL, 'stage6_mechanisms.py BRANCH_A')
    INTO rule_set_member VALUES ('BRANCH_B', 'M1',                      NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'M2',                      NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'M3',                      NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'M4',                      NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'V_INFO_TO_COMMANDER',     NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'V_ARREST_PATH',           NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'V_RESPONSIBILITY',        NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'V_COMMAND_SOURCE',        NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'V_COMPLAINT_TO_BARRACKS', NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'V_INVESTIGATION_SCOPE',   NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'EP29',                    NULL, 'stage6_mechanisms.py BRANCH_B')
    INTO rule_set_member VALUES ('BRANCH_B', 'EP30',                    NULL, 'stage6_mechanisms.py BRANCH_B')
    -- stage6_mechanisms.py OBSERVED_ANCHORED: 관측 backbone에 고정된 메커니즘(모든 world ON)
    INTO rule_set_member VALUES ('OBSERVED_ANCHORED', 'M5', NULL, 'stage6_mechanisms.py OBSERVED_ANCHORED')
    -- stage6_mechanisms.py NULL_VARIANTS: '작동하지 않았다'는 null 변형 후보
    INTO rule_set_member VALUES ('NULL_VARIANT', 'G05b', NULL, 'stage6_mechanisms.py NULL_VARIANTS')
    INTO rule_set_member VALUES ('NULL_VARIANT', 'G11c', NULL, 'stage6_mechanisms.py NULL_VARIANTS')
    INTO rule_set_member VALUES ('NULL_VARIANT', 'G13b', NULL, 'stage6_mechanisms.py NULL_VARIANTS')
    -- audits.py audit3: 모델이 스스로 확정하면 안 되는 동일성(FORBIDDEN_IDENTITIES | {ID05–ID08, ID11})
    INTO rule_set_member VALUES ('MODEL_CONTROLLED_IDENTITY', 'ID01', NULL, 'audits.py audit3 identity_forcing')
    INTO rule_set_member VALUES ('MODEL_CONTROLLED_IDENTITY', 'ID02', NULL, 'audits.py audit3 identity_forcing')
    INTO rule_set_member VALUES ('MODEL_CONTROLLED_IDENTITY', 'ID03', NULL, 'audits.py audit3 identity_forcing')
    INTO rule_set_member VALUES ('MODEL_CONTROLLED_IDENTITY', 'ID04', NULL, 'audits.py audit3 identity_forcing')
    INTO rule_set_member VALUES ('MODEL_CONTROLLED_IDENTITY', 'ID05', NULL, 'audits.py audit3 identity_forcing')
    INTO rule_set_member VALUES ('MODEL_CONTROLLED_IDENTITY', 'ID06', NULL, 'audits.py audit3 identity_forcing')
    INTO rule_set_member VALUES ('MODEL_CONTROLLED_IDENTITY', 'ID07', NULL, 'audits.py audit3 identity_forcing')
    INTO rule_set_member VALUES ('MODEL_CONTROLLED_IDENTITY', 'ID08', NULL, 'audits.py audit3 identity_forcing')
    INTO rule_set_member VALUES ('MODEL_CONTROLLED_IDENTITY', 'ID11', NULL, 'audits.py audit3 identity_forcing')
SELECT * FROM dual;

-- 어휘·이름 집합 (audits.py·stage2_graph.py 상수에서 생성해 붙인 것) -----------------------
-- EDGE_TYPE·EDGE_BASIS는 CHECK 제약과 같은 목록이다. audit SQL은 제약이 꺼져 있어도 이 표로 다시 검사한다.
-- stage2_graph.py EDGE_TYPES
INSERT ALL
    INTO rule_set_member VALUES ('EDGE_TYPE', 'CONTEXT_SUPPORTS', NULL, 'stage2_graph.py EDGE_TYPES')
    INTO rule_set_member VALUES ('EDGE_TYPE', 'CONTRADICTS_AT_CLAIM_LEVEL', NULL, 'stage2_graph.py EDGE_TYPES')
    INTO rule_set_member VALUES ('EDGE_TYPE', 'INFORMATION_FLOW', NULL, 'stage2_graph.py EDGE_TYPES')
    INTO rule_set_member VALUES ('EDGE_TYPE', 'ORDER_TO_ACTION', NULL, 'stage2_graph.py EDGE_TYPES')
    INTO rule_set_member VALUES ('EDGE_TYPE', 'PROCEDURAL_NEXT', NULL, 'stage2_graph.py EDGE_TYPES')
    INTO rule_set_member VALUES ('EDGE_TYPE', 'RESPONSIBILITY_LINK', NULL, 'stage2_graph.py EDGE_TYPES')
    INTO rule_set_member VALUES ('EDGE_TYPE', 'REVIEW_OF', NULL, 'stage2_graph.py EDGE_TYPES')
    INTO rule_set_member VALUES ('EDGE_TYPE', 'REVISES', NULL, 'stage2_graph.py EDGE_TYPES')
    INTO rule_set_member VALUES ('EDGE_TYPE', 'TEMPORAL_BEFORE', NULL, 'stage2_graph.py EDGE_TYPES')
SELECT * FROM dual;

-- stage2_graph.py BASES
INSERT ALL
    INTO rule_set_member VALUES ('EDGE_BASIS', 'ENVIRONMENTAL_CONTEXT', NULL, 'stage2_graph.py BASES')
    INTO rule_set_member VALUES ('EDGE_BASIS', 'INFORMATION_FLOW', NULL, 'stage2_graph.py BASES')
    INTO rule_set_member VALUES ('EDGE_BASIS', 'INSTITUTIONAL_COMPATIBILITY', NULL, 'stage2_graph.py BASES')
    INTO rule_set_member VALUES ('EDGE_BASIS', 'PROCEDURAL', NULL, 'stage2_graph.py BASES')
    INTO rule_set_member VALUES ('EDGE_BASIS', 'SOURCE_DIRECT', NULL, 'stage2_graph.py BASES')
    INTO rule_set_member VALUES ('EDGE_BASIS', 'TEMPORAL', NULL, 'stage2_graph.py BASES')
SELECT * FROM dual;

-- audits.py STRONG_TERMS
INSERT ALL
    INTO rule_set_member VALUES ('STRONG_TERM', '범인', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '거짓 지목', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '지목했', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '누명', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '모함', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '날조', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '살해', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '고문', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '때문에 죽', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '사주했다', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '결탁', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '공모', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '원인이 되', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '확실하다고 판단', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '감염되었', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '옥중 감염', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '죽게 했', NULL, 'audits.py STRONG_TERMS')
    INTO rule_set_member VALUES ('STRONG_TERM', '죽였', NULL, 'audits.py STRONG_TERMS')
SELECT * FROM dual;

-- audits.py HEDGES
INSERT ALL
    INTO rule_set_member VALUES ('HEDGE_TERM', '극히 수상', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '거짓으로 꾸며', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '은밀히', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '약간의', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '십분 확실', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '취지로', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '방향', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '달포 이상', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '확실한 장물', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '진정한 장물', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '보통 좀도둑', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '스스로 만들어냈다는 죄', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '크게 다르지 않다', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '평생 모르는', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '한 차례', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '이미', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '표기된', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '병들어', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '전염병', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '질병', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '부처', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '직접', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '횡액', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '원통하게', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '사적인 감정', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '성명을 적어', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '전해 들은', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '보류', NULL, 'audits.py HEDGES')
    INTO rule_set_member VALUES ('HEDGE_TERM', '자세히', NULL, 'audits.py HEDGES')
SELECT * FROM dual;

-- audits.py PERSON_NAMES
INSERT ALL
    INTO rule_set_member VALUES ('PERSON_NAME', '구순', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '김명신', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '명업', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '나복', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '이진욱', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '한재욱', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '조계완', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '변지돌', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '정원돌', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '자미덕', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '재돌', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '이집거', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '김갑득', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '김성손', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '김흥득', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '유제희', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '김상제', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '이광섭', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '이문협', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '이형원', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '정조', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '이조원', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '홍대협', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '윤노동', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '한가', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '박거사', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '원돌', NULL, 'audits.py PERSON_NAMES')
    INTO rule_set_member VALUES ('PERSON_NAME', '김생원', NULL, 'audits.py PERSON_NAMES')
SELECT * FROM dual;

-- audits.py REQUIRED_RELATIONS (17) --------------------------------------------
INSERT ALL
    INTO rule_required_relation VALUES ('EP15',  'EP25', 'REVISES',                    '5월→6월 도난 판단 번복 보존')
    INTO rule_required_relation VALUES ('EP15',  'EP24', 'CONTRADICTS_AT_CLAIM_LEVEL', '5/12 판단 vs 홍대협')
    INTO rule_required_relation VALUES ('EP17',  'EP24', 'CONTRADICTS_AT_CLAIM_LEVEL', '이조원 vs 홍대협')
    INTO rule_required_relation VALUES ('EP24',  'EP25', 'REVIEW_OF',                  '홍대협 → 정조')
    INTO rule_required_relation VALUES ('EP26',  'EP27', 'REVIEW_OF',                  'branch A: 홍대협 질병 → 정조 전염병')
    INTO rule_required_relation VALUES ('ENV01', 'EP27', 'CONTEXT_SUPPORTS',           'branch A: 전염병 context')
    INTO rule_required_relation VALUES ('ENV03', 'EP27', 'CONTEXT_SUPPORTS',           'branch A: 전염병 지속 context')
    INTO rule_required_relation VALUES ('EP01',  'EP29', 'RESPONSIBILITY_LINK',        'branch B: 관계 악화')
    INTO rule_required_relation VALUES ('EP08',  'EP29', 'RESPONSIBILITY_LINK',        'branch B: 발언·성명')
    INTO rule_required_relation VALUES ('EP11',  'EP29', 'RESPONSIBILITY_LINK',        'branch B: 체포')
    INTO rule_required_relation VALUES ('EP13',  'EP29', 'RESPONSIBILITY_LINK',        'branch B: 구금·사망')
    INTO rule_required_relation VALUES ('EP04',  'EP30', 'RESPONSIBILITY_LINK',        '이광섭 branch: 병영 출동 준비')
    INTO rule_required_relation VALUES ('EP09',  'EP30', 'RESPONSIBILITY_LINK',        '이광섭 branch: 병사 지시')
    INTO rule_required_relation VALUES ('EP14',  'EP30', 'REVIEW_OF',                  '이광섭 branch: 5/12 평가')
    INTO rule_required_relation VALUES ('EP09',  'EP11', 'ORDER_TO_ACTION',            '3/4 지시 → 실행')
    INTO rule_required_relation VALUES ('EP21',  'EP22', 'REVIEW_OF',                  '윤노동 → 비변사 보류')
    INTO rule_required_relation VALUES ('EP36',  'EP37', 'REVISES',                    '파직 → 유임')
SELECT * FROM dual;

-- audits.py IDENTITY_SENSITIVE (9) ---------------------------------------------
INSERT ALL
    INTO rule_identity_sensitive_pair VALUES ('EP07', 'EP12', 'ID02')
    INTO rule_identity_sensitive_pair VALUES ('EP07', 'EP35', 'ID02')
    INTO rule_identity_sensitive_pair VALUES ('EP12', 'EP35', 'ID03')
    INTO rule_identity_sensitive_pair VALUES ('EP09', 'EP30', 'ID01')
    INTO rule_identity_sensitive_pair VALUES ('EP11', 'EP30', 'ID01')
    INTO rule_identity_sensitive_pair VALUES ('EP09', 'EP34', 'ID01')
    INTO rule_identity_sensitive_pair VALUES ('EP08', 'EP29', 'ID06')
    INTO rule_identity_sensitive_pair VALUES ('EP04', 'EP30', 'ID07')
    INTO rule_identity_sensitive_pair VALUES ('EP10', 'EP11', 'ID08')
SELECT * FROM dual;

-- stage5_worlds.py CONFLICT_PAIRS (3) ------------------------------------------
INSERT INTO rule_conflict_pair VALUES ('G03b', 'G04b',
    '둘 다 3/4 지시의 직접 계기를 2/29~3/4에 두면서 정보원을 다르게 잡는다(유제희 기록 vs 자미덕 대질 진술)');
INSERT INTO rule_conflict_pair VALUES ('G03c', 'G04a',
    '유제희 기록의 경로가 비장 우회 직접 보고(G03c)와 비장 계통 경유(G04a)로 서로 배타적');
INSERT INTO rule_conflict_pair VALUES ('G01a', 'G02c',
    'G01a는 진영이 수사를 병영 비장에게 넘겼다고, G02c는 영장이 출동을 직접 지휘했다고 본다');

-- stage6_mechanisms.py CAND_MAP negates 열 (3) ---------------------------------
INSERT INTO rule_candidate_negates VALUES ('G02b', 'M1');
INSERT INTO rule_candidate_negates VALUES ('G05b', 'M3');
INSERT INTO rule_candidate_negates VALUES ('G13b', 'M5');

-- audits.py IDENTITY_RULES (6) -------------------------------------------------
INSERT INTO rule_identity_surface VALUES ('병사',       '이광섭', 'ID01');
INSERT INTO rule_identity_surface VALUES ('한 비장',    '한재욱', 'ID02');
INSERT INTO rule_identity_surface VALUES ('한가',       '한재욱', 'ID03');
INSERT INTO rule_identity_surface VALUES ('김상제',     '김명신', 'ID05');
INSERT INTO rule_identity_surface VALUES ('염탐 담당자', '유제희', 'ID06');
INSERT INTO rule_identity_surface VALUES ('원돌',       '정원돌', 'ID11');

-- audits.py 정규식 → Oracle 정규식 ---------------------------------------------
-- 바꾼 점: Oracle 정규식에는 비포획 그룹 (?:…)과 전후방 탐색 (?<=…) (?=…)이 없다.
--         (?:…)는 일반 그룹 (…)으로 바꿨다(일치 여부는 같다). 전후방 탐색이 필요한 규칙은 옮기지 않았다(NOT PORTED).
INSERT INTO rule_text_pattern VALUES ('RESP_TO_CAUSE_1', 'responsibility_to_causation',
    '구순(이|의|으로)?[^.。]{0,25}(때문에|탓에|으로 인해|로 인해)[^.。]{0,12}(죽었|사망했)',
    '구순(?:이|의|으로)?[^.。]{0,25}(?:때문에|탓에|으로 인해|로 인해)[^.。]{0,12}(?:죽었|사망했)',
    '책임 판단 → 직접 사인 단정');
INSERT INTO rule_text_pattern VALUES ('RESP_TO_CAUSE_2', 'responsibility_to_causation',
    '구순이[^.。]{0,25}(죽게 했|죽였|사망하게)',
    '구순이[^.。]{0,25}(?:죽게 했|죽였|사망하게)', NULL);
INSERT INTO rule_text_pattern VALUES ('RESP_TO_CAUSE_3', 'responsibility_to_causation',
    '(사인|사망 원인)[은는이]?[^.。]{0,15}구순',
    '(?:사인|사망 원인)[은는이]?[^.。]{0,15}구순', NULL);
INSERT INTO rule_text_pattern VALUES ('ENV_TO_INDIV_1', 'environment_to_individual_fact',
    '(호서 전염병|전염병 창궐|E00[0-9]|환경)[^.。]{0,30}(때문에|으로 인해|로 인해|원인)[^.。]{0,30}(김명신|아내|부처)',
    '(?:호서 전염병|전염병 창궐|E00\d|환경)[^.。]{0,30}(?:때문에|으로 인해|로 인해|원인)[^.。]{0,30}(?:김명신|아내|부처)',
    '환경 context → 개인 사실 단정');
INSERT INTO rule_text_pattern VALUES ('ENV_TO_INDIV_2', 'environment_to_individual_fact',
    '(김명신|아내|부처)[^.。]{0,30}(호서 전염병|E00[0-9]|환경)[^.。]{0,10}(때문에|으로 인해|로 인해)',
    '(?:김명신|아내|부처)[^.。]{0,30}(?:호서 전염병|E00\d|환경)[^.。]{0,10}(?:때문에|으로 인해|로 인해)', NULL);
INSERT INTO rule_text_pattern VALUES ('TESTIFIER', 'actor_substitution',
    '^(\S+?)[은는]\s', '^(\S+?)[은는]\s', '문장 첫 주어(진술·기록 주체). 1번 그룹이 주어');
INSERT INTO rule_text_pattern VALUES ('TESTIMONY_ATTRIBUTION', 'testimony_to_fact',
    '진술|따르면', '진술|따르면', '진술 episode summary에 남아야 하는 귀속 표현');
INSERT INTO rule_text_pattern VALUES ('OFFICIAL_RECORD_ACT', 'epistemic_collapse',
    '보고|평가|판단|받아들|인정|명|청|신문|복명|식별|유임|정배|유배',
    '보고|평가|판단|받아들|인정|명|청|신문|복명|식별|유임|정배|유배', '공식 기록 episode summary의 기록 행위 표현');
INSERT INTO rule_text_pattern VALUES ('OUTCOME_WORLD', 'outcome_world_dependency',
    'W[0-9]\s*(에서는|에서|의 경우)[^.。]{0,40}(정배|유배|파직|유임|처분|형장|처벌)',
    'W\d\s*(?:에서는|에서|의 경우)[^.。]{0,40}(?:정배|유배|파직|유임|처분|형장|처벌)', '결말을 world에 종속시키는 서술');
INSERT INTO rule_text_pattern VALUES ('LUNAR_MD', 'parse_md',
    '1793-([0-9]{2})-([0-9]{2})', '1793-(\d{2})-(\d{2})', 'audits.py parse_md: 월*100+일');
-- audits.py EPISTEMIC_MARKERS (13): 원문 표지 개수가 summary에서 줄면 epistemic_marker_deletion
INSERT INTO rule_text_pattern VALUES ('MARKER_진술',     'epistemic_marker_deletion', '진술했',             '진술했', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_보고',     'epistemic_marker_deletion', '보고했',             '보고했', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_평가',     'epistemic_marker_deletion', '평가했',             '평가했', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_판단',     'epistemic_marker_deletion', '판단했',             '판단했', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_명',       'epistemic_marker_deletion', '명했|명하고',        '명했|명하고', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_받아들',   'epistemic_marker_deletion', '받아들였',           '받아들였', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_윤허',     'epistemic_marker_deletion', '윤허했',             '윤허했', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_청',       'epistemic_marker_deletion', '청했',               '청했', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_식별',     'epistemic_marker_deletion', '식별된',             '식별된', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_인정',     'epistemic_marker_deletion', '인정했|인정하지',    '인정했|인정하지', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_차하',     'epistemic_marker_deletion', '차하했',             '차하했', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_복명',     'epistemic_marker_deletion', '복명하',             '복명하', NULL);
INSERT INTO rule_text_pattern VALUES ('MARKER_확정못함', 'epistemic_marker_deletion', '확정하지 못했',      '확정하지 못했', NULL);

COMMIT;


-- =============================================================================
-- 2부. SQLD DML 연습 (04_transform_to_canonical.sql 실행 뒤에 돌린다. 끝에서 모두 ROLLBACK)
-- =============================================================================
-- 아래 블록은 canonical 데이터를 바꾸지 않는다. SAVEPOINT로 시작해 ROLLBACK으로 끝난다.

SAVEPOINT sp_dml_practice;

-- (1) INSERT … VALUES : 연습용 경고 처리 한 건 (warn_disposition은 다른 표가 참조하지 않는다)
INSERT INTO warn_disposition (warning_id, audit_stage, affected_item, warning_type, original_text,
                              generated_text, risk, disposition, justification, fixed_text,
                              final_status, final_classification, unresolved_reason)
VALUES ('PRACTICE', 'AUDIT2', 'OE001', 'semantic_weakening', '연습용 원문', '연습용 생성문',
        '연습', 'RECLASSIFIED_INFO', '연습용 근거', '연습용 수정문', 'RESOLVED', 'OBSERVED', NULL);

-- (2) UPDATE … WHERE : 방금 넣은 행만 고친다(WHERE를 빼면 전체 행이 바뀐다 — 단골 실수)
UPDATE warn_disposition
   SET disposition = 'UNRESOLVED',
       unresolved_reason = '연습: UNRESOLVED는 오류가 아니라 보존된 불확실성'
 WHERE warning_id = 'PRACTICE';

-- (3) MERGE : 있으면 UPDATE, 없으면 INSERT (Oracle 9i+)
MERGE INTO load_log tgt
USING (SELECT 'DML_PRACTICE' AS load_step, 'WARN_DISPOSITION' AS table_name,
              COUNT(*) AS row_count
         FROM warn_disposition) src
   ON (tgt.load_step = src.load_step AND tgt.table_name = src.table_name)
 WHEN MATCHED THEN
      UPDATE SET tgt.row_count = src.row_count
 WHEN NOT MATCHED THEN
      INSERT (load_step, table_name, row_count)
      VALUES (src.load_step, src.table_name, src.row_count);

-- (4) DELETE : 연습 행 삭제
DELETE FROM warn_disposition WHERE warning_id = 'PRACTICE';

-- (5) 제약조건이 막는 INSERT — 주석을 풀고 실행하면 오류가 난다(어떤 제약이 막는지 확인)
-- INSERT INTO dag_edge (edge_id, src, dst, edge_type, basis, status, claim_level, supporting, rationale)
-- VALUES ('OE999', 'EP01', 'EP13', 'CAUSES', 'SOURCE_DIRECT', 'DERIVED', 'False', 'CF001', '연습');
--   → ORA-02290 check constraint (CK_DAG_EDGE_TYPE) violated : CAUSES edge 금지
-- INSERT INTO dag_edge (edge_id, src, dst, edge_type, basis, status, claim_level, supporting, rationale)
-- VALUES ('OE999', 'EP01', 'EP01', 'TEMPORAL_BEFORE', 'TEMPORAL', 'DERIVED', 'False', 'CF001', '연습');
--   → ORA-02290 (CK_DAG_EDGE_NO_SELF_LOOP) : self-loop 금지
-- INSERT INTO dag_edge (edge_id, src, dst, edge_type, basis, status, claim_level, supporting, rationale)
-- VALUES ('OE999', 'EP01', 'EP99', 'TEMPORAL_BEFORE', 'TEMPORAL', 'DERIVED', 'False', 'CF001', '연습');
--   → ORA-02291 integrity constraint (FK_DAG_EDGE_DST) violated - parent key not found
-- INSERT INTO dag_node (node_id, node_status, layer, branch, title, summary, epistemic_floor,
--                       attesting_actor, occurrence_text, record_lunar_date, grouping_rationale, member_fact_ids)
-- VALUES ('EP99', 'LATENT', 'TESTIMONY', 'X', '연습', '연습', 'RECORDED_TESTIMONY', 'X', 'X', '1793-06-13', 'X', 'CF001');
--   → ORA-02290 (CK_DAG_NODE_STATUS) : 동결 DAG에 LATENT node 금지
-- INSERT INTO world_candidate (world_id, candidate_id, gap_id, bridge_seq) VALUES ('W1', 'G01b', 'G01', 99);
--   → ORA-00001 unique constraint (UK_WORLD_CANDIDATE_GAP) violated : W1은 이미 G01에 G01a를 쓴다
-- INSERT INTO identity_register (identity_id, surface_a, surface_b, status, model_relevance,
--                                manual_decision_required, context)
-- VALUES ('ID99', 'A', 'B', 'RESOLVED', 'NONE', 'NO', '연습');
--   → ORA-02290 (CK_IDENTITY_RESOLUTION) : 사용자 확정 근거 없는 RESOLVED 금지

ROLLBACK TO SAVEPOINT sp_dml_practice;
-- 확인: 0이어야 한다
SELECT COUNT(*) AS practice_rows_left FROM warn_disposition WHERE warning_id = 'PRACTICE';
