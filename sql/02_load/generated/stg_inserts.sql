-- =============================================================================
-- LOAD 방법 C — STG_* INSERT script (서버 파일 접근 없이 실행)
-- 이 파일은 sql/02_load/generate_load_scripts.py가 canonical CSV header로 생성했다. 손으로 고치지 말 것.
-- Oracle runtime에서 실행 검증되지 않았다(Oracle runtime unavailable) — sql/README.md §실행 상태 참고.
-- =============================================================================

SET DEFINE OFF
SET SQLBLANKLINES ON
-- 클라이언트 문자셋이 UTF-8이어야 한글이 깨지지 않는다(예: export NLS_LANG=AMERICAN_AMERICA.AL32UTF8).
-- 빈 CSV 값은 NULL로 넣는다(Oracle에서 ''는 NULL과 같다).

-- gusun_clean_restart_csv_pack/00_INPUT_MANIFEST.csv (5행)
INSERT INTO STG_INPUT_MANIFEST (FILE_NAME, ROLE, ALLOWED_AS_DAG_INPUT, PURPOSE, IMPORTANT_RULE)
VALUES (
    '01_confirmed_facts.csv',
    'PRIMARY_CASE_INPUT',
    'YES',
    '문장/사건묶음(meso) DAG 노드의 기본 입력',
    'confirmed_statement를 원자 명제로 다시 쪼개지 말 것. 필요할 때만 같은 episode로 묶기.'
);
INSERT INTO STG_INPUT_MANIFEST (FILE_NAME, ROLE, ALLOWED_AS_DAG_INPUT, PURPOSE, IMPORTANT_RULE)
VALUES (
    '02_institutional_normative_features.csv',
    'INSTITUTIONAL_CONSTRAINT',
    'YES',
    '1793년 당시 제도상 가능성·관할·역할 적합성 제약',
    '행동 빈도 prior가 아님. 새로운 사건을 생성하지 말 것.'
);
INSERT INTO STG_INPUT_MANIFEST (FILE_NAME, ROLE, ALLOWED_AS_DAG_INPUT, PURPOSE, IMPORTANT_RULE)
VALUES (
    '03_environment_1793.csv',
    'EXTERNAL_CONTEXT',
    'YES',
    '1793년 호서 전염병·구휼·옥수 치료 등 외생 환경',
    'CONTEXT_SUPPORTS로만 사용. 김명신 개인 감염 같은 미관측 사실을 생성하지 말 것.'
);
INSERT INTO STG_INPUT_MANIFEST (FILE_NAME, ROLE, ALLOWED_AS_DAG_INPUT, PURPOSE, IMPORTANT_RULE)
VALUES (
    '04_source_records.csv',
    'PROVENANCE',
    'NO',
    '출처 레코드 추적·링크',
    'DAG 의미 생성에 직접 사용하지 않고 provenance 검증용.'
);
INSERT INTO STG_INPUT_MANIFEST (FILE_NAME, ROLE, ALLOWED_AS_DAG_INPUT, PURPOSE, IMPORTANT_RULE)
VALUES (
    '05_source_faithful_propositions_AUDIT_ONLY.csv',
    'AUDIT_ONLY',
    'NO',
    '문장 노드가 사료 의미를 왜곡하지 않았는지 역추적',
    '원자 proposition을 DAG node로 재사용하지 말 것.'
);

-- gusun_clean_restart_csv_pack/01_confirmed_facts.csv (50행)
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF001',
    '1793-02 초순 이전',
    '1793-06-13',
    NULL,
    'RELATIONSHIP',
    'RECORDED_TESTIMONY',
    '김명신·구순',
    '명업은 김명신이 본래 구순과 친숙하여 날마다 왕래했다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0049',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF002',
    '1793-02 초순',
    '1793-06-13',
    '1793-02 초순',
    'RELATIONSHIP_CONFLICT',
    'RECORDED_TESTIMONY',
    '김명신',
    '명업은 김명신이 박거사 일로 구순에게 편지를 보내 힐책했다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0050',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF003',
    '1793-02 초순 이후',
    '1793-06-13',
    '1793-02 초순 이후',
    'RELATIONSHIP_CONFLICT',
    'RECORDED_TESTIMONY',
    '김명신·구순',
    '명업은 그 뒤 구순과 김명신의 왕래가 끊겼다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0051',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF004',
    '1793-02-22 밤',
    '1793-06-13',
    '1793-02-22 밤',
    'THEFT_REPORT',
    'RECORDED_TESTIMONY',
    '나복→명업',
    '명업은 나복이 2월 22일 밤 도적이 들었다고 자신에게 알렸다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0047',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF005',
    '1793-02-22 밤',
    '1793-06-13',
    '1793-02-22 밤',
    'THEFT_DESCRIPTION',
    'RECORDED_NESTED_TESTIMONY',
    '나복→명업',
    '명업은 나복이 도적 30여 명, 횃불, 지세대감 자칭, 돈과 물품 도난을 말했다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0048',
    '30여 명·횃불·지세대감은 중첩 진술의 내용이며 객관적 사실로 확정하지 않음.'
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF006',
    '도난 신고 이후',
    '1793-06-13',
    NULL,
    'COMPLAINT',
    'RECORDED_TESTIMONY',
    '구순',
    '명업은 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0052',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF007',
    '1793-02-28 밤',
    '1793-06-13',
    '1793-02-28 밤',
    'BARRACKS_PROCEDURE',
    'RECORDED_TESTIMONY',
    '병영',
    '이진욱은 2월 28일 밤 병영에서 자신을 비장청으로 불렀다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0055',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF008',
    '1793-02-28 밤',
    '1793-06-13',
    '1793-02-28 밤',
    'BARRACKS_ORDER',
    'RECORDED_TESTIMONY',
    '한재욱',
    '이진욱은 한재욱이 자신과 조계완 등에게 덕평으로 가도록 지시했다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0056',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF009',
    '1793-02-28 밤',
    '1793-06-13',
    '1793-02-28 밤',
    'BARRACKS_ORDER',
    'RECORDED_TESTIMONY',
    '한재욱',
    '이진욱은 한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0057',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF010',
    '1793-02-28 밤~29 새벽',
    '1793-06-13',
    '1793-02-28 밤~29 새벽',
    'BARRACKS_PREPARATION',
    'RECORDED_TESTIMONY',
    '한재욱',
    '이진욱은 한재욱이 철편 네 개를 만들어 주었다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0058',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF011',
    '1793-02-29',
    '1793-06-13',
    '1793-02-29',
    'CUSTODY',
    'RECORDED_TESTIMONY',
    '변지돌',
    '이진욱은 변지돌이 이미 공주진에서 잡혀간 상태였다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0060',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF012',
    '1793-02-29',
    '1793-06-13',
    '1793-02-29',
    'APPREHENSION',
    'RECORDED_TESTIMONY',
    '이진욱 등 장교',
    '이진욱은 장교 일행이 재돌의 처 자미덕을 붙잡았다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0061',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF013',
    '자미덕 체포 뒤',
    '1793-06-13',
    NULL,
    'APPREHENSION',
    'RECORDED_TESTIMONY',
    '병영 장교',
    '자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0075',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF014',
    '자미덕 체포 뒤',
    '1793-06-13',
    NULL,
    'INTERROGATION',
    'RECORDED_TESTIMONY',
    '병영',
    '자미덕은 병영에서 도적 혐의로 한 차례 신문을 받았다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0076',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF015',
    '신문 뒤',
    '1793-06-13',
    NULL,
    'DETENTION',
    'RECORDED_TESTIMONY',
    '자미덕',
    '자미덕은 신문 뒤 비장청 다모방에 구류되었다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0077',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF016',
    '구류 중/그 후',
    '1793-06-13',
    NULL,
    'COACHING_ALLEGATION',
    'RECORDED_TESTIMONY',
    '한 비장',
    '자미덕은 한 비장이 정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적이라고 말하면 자신과 남편을 다음 날 석방하겠다고 말했다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0080',
    '''등''이 있으므로 명시된 5명을 닫힌 목록으로 취급하지 않음.'
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF017',
    '대질 때',
    '1793-06-13',
    NULL,
    'CONFRONTATION_AND_TESTIMONY',
    'RECORDED_TESTIMONY',
    '자미덕·이집거',
    '자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0082|V3P0083',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF018',
    '안핵 공초',
    '1793-06-13',
    NULL,
    'HAN_JAEUK_TESTIMONY',
    'RECORDED_TESTIMONY',
    '한재욱',
    '한재욱은 자미덕을 방으로 불러 남은 밥을 준 사실은 인정했지만, 자미덕을 은밀히 사주한 일은 없다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0088|V3P0092',
    '''은밀히''의 범위를 삭제하지 않음.'
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF019',
    '안핵 공초',
    '1793-06-13',
    NULL,
    'HAN_GUSUN_RELATION',
    'RECORDED_TESTIMONY',
    '한재욱',
    '한재욱은 구순과 평생 모르는 사이라고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0093',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF020',
    '현지 탐문',
    '1793-06-13',
    NULL,
    'SUSPECT_LIST',
    'RECORDED_TESTIMONY',
    '유제희',
    '유제희는 현지 탐문 중 구순이 풍각 김상제도 극히 수상하다고 말했고, 자신이 그 말을 원돌 등의 이름과 함께 기록해 올렸다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0094|V3P0095|V3P0096',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF021',
    '1793-03-04',
    '1793-06-13',
    '1793-03-04',
    'ARREST_ORDER',
    'RECORDED_TESTIMONY',
    '병사',
    '이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0065',
    '해당 공초 문장의 표면 주어는 병사이며 이 행 자체에서 병사=이광섭을 치환하지 않음.'
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF022',
    '1793-03-04',
    '1793-06-13',
    '1793-03-04',
    'IDENTITY',
    'DOCUMENTED_SOURCE_IDENTIFICATION',
    '풍각 김생원·흥덕 김생원',
    '해당 기사에서 풍각 김생원은 김명신, 흥덕 김생원은 김갑득으로 식별된다.',
    'DIRECTLY_DOCUMENTED_SOURCE_IDENTIFICATION',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0066|V3P0067',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF023',
    '1793-03-04',
    '1793-06-13',
    '1793-03-04',
    'APPREHENSION',
    'RECORDED_TESTIMONY',
    '장교 일행',
    '이진욱은 장교 일행이 병사의 분부에 따라 김명신과 김갑득을 잡아왔다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0068',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF024',
    '1793-03-04',
    '1793-06-13',
    '1793-03-04',
    'GUSUN_CONTACT',
    'RECORDED_TESTIMONY',
    '구순·조계완',
    '조계완은 김명신을 잡으러 가는 길에 구순 집에 들렀고, 구순이 이제 도적 다스리는 일이 바른 길을 얻었다는 취지로 말한 뒤 병사에게 전할 서찰 한 장을 건넸다고 진술했다.',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0069|V3P0072|V3P0073',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF025',
    '1793-05-12 기사',
    '1793-05-12',
    NULL,
    'MILITARY_COMMAND',
    'DOCUMENTED_OFFICIAL_EVALUATION',
    '이광섭',
    '5월 12일 기사에서 이광섭은 사건의 병사 지휘 책임자로 심리되며, 이형원은 이광섭이 허황한 말을 믿고 무고한 사람을 잘못 잡았다고 평가했다.',
    'FACT_OF_OFFICIAL_EVALUATION',
    'SRC3_001',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    'V3P0013',
    '기사 제목은 이광섭을 충청도 병마절도사로 명시함.'
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF026',
    '1793-05-12',
    '1793-05-12',
    NULL,
    'BARRACKS_CHAIN',
    'DOCUMENTED_OFFICIAL_EVALUATION',
    '이문협',
    '이형원은 청주 영장 이문협이 수사를 병영 비장에게 전적으로 맡기고 방관했다고 평가했다.',
    'FACT_OF_OFFICIAL_EVALUATION',
    'SRC3_001',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    'V3P0012',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF027',
    '1793-05-12 보고',
    '1793-05-12',
    NULL,
    'KIM_DETENTION_DEATH',
    'DOCUMENTED_OFFICIAL_REPORT',
    '김명신',
    '이형원의 5월 12일 장계는 충청병영이 김명신을 달포 이상 구금·조사했으나 확실한 장물을 찾지 못했고, 김명신이 그 뒤 사망했다고 보고했다.',
    'FACT_OF_OFFICIAL_REPORT',
    'SRC3_001',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    'V3P0004|V3P0005|V3P0006',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF028',
    '1793-05-12 보고',
    '1793-05-12',
    NULL,
    'INVESTIGATION_HARM',
    'DOCUMENTED_OFFICIAL_REPORT',
    '무고한 평민들',
    '이형원의 장계는 무고한 평민들이 모진 형벌을 받았다고 보고했다.',
    'FACT_OF_OFFICIAL_REPORT',
    'SRC3_001',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    'V3P0007',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF029',
    '1793-06-11 보고',
    '1793-06-11',
    NULL,
    'KIM_DETENTION_DEATH',
    'DOCUMENTED_INSPECTOR_REPORT',
    '김명신·여러 죄수',
    '윤노동의 6월 11일 별단은 김명신이 보수·구금 중 병들어 죽었고, 여러 죄수가 참혹한 형벌을 받았으며, 진정한 장물을 얻지 못했다고 보고했다.',
    'FACT_OF_OFFICIAL_REPORT',
    'SRC3_005',
    '비변사등록',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    'V3P0039|V3P0040|V3P0041',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF030',
    '1793-05-12',
    '1793-05-12',
    NULL,
    'THEFT_JUDGMENT',
    'DOCUMENTED_ROYAL_JUDGMENT',
    '정조',
    '정조는 당시 장계와 조사에 따라 도난 자체가 없었다는 방향을 받아들였다.',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_001',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    'V3P0016',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF031',
    '1793-05-12',
    '1793-05-12',
    NULL,
    'REINVESTIGATION',
    'DOCUMENTED_ROYAL_ORDER',
    '정조',
    '정조는 구순을 의금부에 잡아 가두고 엄히 조사하도록 명했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_001',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    'V3P0017',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF032',
    '1793-05-27',
    '1793-05-27',
    NULL,
    'THEFT_JUDGMENT',
    'DOCUMENTED_INSPECTOR_REPORT',
    '이조원',
    '이조원은 구순 사건을 도난이 없었다는 방향으로 보고했다.',
    'FACT_OF_OFFICIAL_REPORT',
    'SRC3_003',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11705027_002',
    'V3P0031',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF033',
    '1793-05-27',
    '1793-05-27',
    NULL,
    'INSPECTOR_REVIEW',
    'DOCUMENTED_ROYAL_JUDGMENT_AND_ORDER',
    '정조',
    '정조는 이조원이 중대 사실을 직접 안핵하지 않고 전해 들은 말을 서계에 붙인 점을 문제 삼았고, 이조원을 파직하도록 명했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_003',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11705027_002',
    'V3P0032|V3P0029',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF034',
    '1793-05-27',
    '1793-05-27',
    NULL,
    'REINVESTIGATION',
    'DOCUMENTED_ROYAL_ORDER',
    '정조',
    '정조는 구순을 의금부에 엄히 가두고 반복 신문하도록 명했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_002',
    '비변사등록',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    'V3P0030',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF035',
    '1793-05-28',
    '1793-05-28',
    NULL,
    'ANHAEK_APPOINTMENT',
    'DOCUMENTED_ROYAL_ORDER',
    '정조·홍대협',
    '정조는 홍대협에게 사건을 자세히 조사해 오라고 명하고 그를 충청도 공주 안핵어사로 차하했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_004',
    '승정원일기',
    'https://sjw.history.go.kr/search/inspectionDayList.do?wday=17930528L0',
    'V3P0036|V3P0037',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF036',
    '1793-06-11',
    '1793-06-11',
    NULL,
    'PROCEDURAL_HOLD',
    'DOCUMENTED_COURT_ACTION',
    '비변사·정조',
    '비변사는 홍대협의 안핵 복명 전까지 윤노동 별단에 따른 처리를 보류할 것을 청했고, 정조는 이를 윤허했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_005',
    '비변사등록',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    'V3P0043|V3P0044',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF037',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'ANHAEK_REPORT',
    'DOCUMENTED_OFFICIAL_ACTION',
    '홍대협',
    '홍대협은 공주목에서 관련자들을 차례로 신문한 뒤 호서 안핵어사로 복명하여 편전에서 정조에게 보고했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0045|V3P0130',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF038',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'THEFT_FINAL_FINDING',
    'DOCUMENTED_OFFICIAL_FINDING',
    '홍대협',
    '홍대협은 약간의 실제 도난은 있었지만 큰 화적 사건이 아니라 보통 좀도둑 수준이었다고 판단했다.',
    'FACT_OF_OFFICIAL_FINDING',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0097|V3P0098',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF039',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'THEFT_FINAL_JUDGMENT',
    'DOCUMENTED_ROYAL_JUDGMENT',
    '정조',
    '정조는 최종적으로 도난은 실제로 있었다고 판단했다.',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0104',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF040',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'DEATH_CAUSE_JUDGMENT',
    'DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT',
    '김명신',
    '홍대협은 김명신의 죽음을 질병 때문이라고 평가했고, 정조는 김명신 부처가 전염병에 걸려 죽은 것으로 판단했다.',
    'FACT_OF_OFFICIAL_JUDGMENT',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0101|V3P0105',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF041',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'TREATMENT_JUDGMENT',
    'DOCUMENTED_ROYAL_JUDGMENT',
    '정조',
    '정조는 김명신이 곤장을 맞지 않았고 평범한 신문도 받지 않았다고 판단했다.',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0106',
    '5월 12일 장계의 구금·조사 보고와 긴장이 있으므로 이 행은 최종 왕실 판단 자체로 보존.'
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF042',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'DIRECT_CAUSATION',
    'DOCUMENTED_ROYAL_JUDGMENT',
    '정조',
    '정조는 김명신이 구순 때문에 직접 죽었다는 인과가 십분 확실하다고 할 수 없다고 판단했다.',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0141',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF043',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'GUSUN_RESPONSIBILITY',
    'DOCUMENTED_ROYAL_JUDGMENT',
    '구순',
    '정조는 구순이 김명신에게 사적인 감정을 품고 갈등을 일으켰고, 병영의 염탐 담당자에게 김명신의 성명을 적어 주었으며, 그 과정이 김명신이 횡액을 입고 원통하게 죽는 결과로 이어졌다고 책임을 연결해 판단했다.',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0142|V3P0143|V3P0144',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF044',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'LEE_GWANGSEOP_RESPONSIBILITY',
    'DOCUMENTED_ROYAL_JUDGMENT',
    '이광섭',
    '정조는 이광섭이 구순 편을 들고, 철퇴 네 개를 만들게 했으며, 아전들의 거짓을 제대로 살피지 않은 채 비장에게 일을 맡겼다고 비판하고, 김명신 사망 책임에서 구순과 이광섭의 책임이 크게 다르지 않다고 판단했다.',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0148|V3P0149|V3P0150|V3P0151',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF045',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'JISE_FINAL_JUDGMENT',
    'DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT',
    '지세 호칭',
    '홍대협은 여러 차례 신문과 별도 탐문에도 지세 호칭의 기원을 확정하지 못했고, 정조는 구순이 지세 호칭을 스스로 만들어냈다는 죄는 인정하지 않았다.',
    'FACT_OF_OFFICIAL_JUDGMENT',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0136|V3P0146',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF046',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'PUNISHMENT',
    'DOCUMENTED_ROYAL_ORDER',
    '구순',
    '정조는 구순을 신지도에 정배했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0110',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF047',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'PUNISHMENT',
    'DOCUMENTED_ROYAL_ORDER',
    '이광섭',
    '정조는 이광섭을 영동현에 유배했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0111',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF048',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'PUNISHMENT',
    'DOCUMENTED_ROYAL_ORDER',
    '병영 비장 한가',
    '정조는 병영 비장으로 표기된 한가를 도백이 엄히 세 차례 형장 친 뒤 먼 섬의 종으로 보내도록 명했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0153',
    '처분문 표면형은 한가. 한가=한재욱은 이 행에서 확정하지 않음.'
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF049',
    '1793-06-13',
    '1793-06-13',
    NULL,
    'PUNISHMENT',
    'DOCUMENTED_ROYAL_ORDER',
    '이형원',
    '정조는 충청도 관찰사 이형원을 파직하도록 명했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_006',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'V3P0113',
    NULL
);
INSERT INTO STG_CONFIRMED_FACTS (FACT_ID, CHRONOLOGY, RECORD_LUNAR_DATE, OCCURRENCE_LUNAR_TEXT, FACT_CATEGORY, CONFIRMATION_LEVEL, SUBJECT, CONFIRMED_STATEMENT, UNDERLYING_CLAIM_STATUS, SOURCE_RECORD_ID, SOURCE_WORK, SOURCE_URL, SOURCE_PROP_IDS, NOTES)
VALUES (
    'CF050',
    '1793-06-16',
    '1793-06-16',
    NULL,
    'POST_CASE_APPOINTMENT',
    'DOCUMENTED_ROYAL_ORDER',
    '이형원',
    '정조는 6월 16일 전 충청도 관찰사 이형원을 유임했다.',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_008',
    '조선왕조실록 정조실록',
    'https://sillok.history.go.kr/id/kva_11706016_002',
    'V3P0114',
    NULL
);

-- gusun_clean_restart_csv_pack/02_institutional_normative_features.csv (20행)
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F001',
    'NORMATIVE',
    '법전',
    '대전통편 현행',
    '1793년 당시 통합 법전이 현행이었는가',
    'binary',
    '0/1',
    'hard gate / legal affordance',
    '법적·절차적 가능성의 경계만 제공',
    '1786',
    '1793',
    '전국',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0014748',
    '1785 편찬, 1786부터 운용. 행동 개연성 자체의 빈도 prior로 사용하지 않음.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F002',
    'NORMATIVE',
    '형정',
    '흠휼전칙 현행',
    '형구·구금·군문 곤형의 규격과 사용 제한이 현행이었는가',
    'binary',
    '0/1',
    'hard gate / procedural affordance',
    '허용 형구·구금 방식 및 제한',
    '1778',
    '1793',
    '전국',
    '정조실록/한국사DB',
    'https://sillok.history.go.kr/id/kva_10201012_002',
    '정조 2년 1월 완성.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F003',
    'NORMATIVE',
    '형정',
    '군문 중곤 사용 제한',
    '병사·감사 등 군문 지휘자가 중곤을 사용할 수 있는 조건',
    'categorical',
    'death_only / not_death / unknown',
    'hard constraint',
    '비사형죄에 중곤 사용을 낮은 적합도로 처리',
    '1778',
    '1793',
    '전국 군문',
    '흠휼전칙',
    'https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_470_0020',
    '중곤은 사형죄를 다스릴 때에 한해 병사·감사 등에게 허용.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F004',
    'NORMATIVE',
    '형정',
    '구금 도구 기준',
    '사형·유배·장죄 등 죄급별 가·뉴·쇄 사용 기준',
    'categorical',
    'death / exile / beating / status_exception',
    'hard constraint',
    '구금 장치의 제도 적합성',
    '1778',
    '1793',
    '전국',
    '흠휼전칙',
    'https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_470_0100',
    '경외 동일 기준.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F005',
    'NORMATIVE',
    '지방행정',
    '수령의 군현 통치',
    '군현 수령이 해당 고을 행정을 담당하는 기본 구조',
    'binary',
    '0/1',
    'institutional affordance',
    '지방 조사·행정·사법 행위의 가능한 주체',
    '1776',
    '1793',
    '전국 군현',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0031317',
    '모든 수령은 관찰사 관할하에 있음.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F006',
    'NORMATIVE',
    '지방행정',
    '관찰사의 수령 감독·직계',
    '관찰사가 수령을 감독하고 중앙에 직접 보고할 수 있는 구조',
    'binary',
    '0/1',
    'institutional affordance',
    '하급 판단의 상향 보고·감독 경로',
    '1776',
    '1793',
    '도 단위',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0005013',
    '지방-중앙 연결 기능.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F007',
    'NORMATIVE',
    '군사치안',
    '병마절도사 도 단위 군사지휘',
    '병마절도사가 도의 군사 지휘권을 가진 구조',
    'binary',
    '0/1',
    'institutional affordance',
    '병사→영·진→장교의 공식 지휘 가능성',
    '1776',
    '1793',
    '각 도',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0023089',
    '병사(兵使)로 약칭.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F008',
    'NORMATIVE',
    '군사치안',
    '병영 지휘체계',
    '병영이 병마절도사 주둔 관서이며 하위 진·장교 체계가 존재',
    'binary',
    '0/1',
    'institutional affordance',
    '병영 내부 명령·집행 경로의 가능성',
    '1776',
    '1793',
    '도/병영',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0023123',
    '주진-거진-제진 구조.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F009',
    'NORMATIVE',
    '군사치안',
    '비장 막료 체계',
    '감사·절도사 등이 비장을 막료로 둘 수 있는 관행',
    'binary',
    '0/1',
    'institutional affordance',
    '비장이 장관의 실무 집행에 관여할 가능성',
    '1776',
    '1793',
    '지방 장관 관아',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0025230',
    '비장은 감사·절도사 등의 막료.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F010',
    'NORMATIVE',
    '군사치안',
    '토포사 제도',
    '도적 수색·체포를 위해 수령 또는 진영장이 토포사를 겸임할 수 있음',
    'binary',
    '0/1',
    'institutional affordance',
    '도적사건에서 진·수령·군사조직 개입 가능성',
    '1776',
    '1793',
    '지방',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0059221',
    '도적 수색·체포 목적의 특수관직.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F011',
    'NORMATIVE',
    '중앙사법',
    '형조 심리·회계',
    '형조가 중앙 형사행정과 사건 심리에 관여할 수 있는 구조',
    'binary',
    '0/1',
    'review affordance',
    '지방 옥사에 대한 중앙 검토 경로',
    '1776',
    '1793',
    '중앙',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0063559',
    '의금부·한성부와 삼법사.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F012',
    'NORMATIVE',
    '중앙사법',
    '의금부 특별사법·재심',
    '왕명에 따라 중요범죄 심문·재심을 수행할 수 있는 구조',
    'binary',
    '0/1',
    'review affordance',
    '왕명 기반 재신문·특별조사 경로',
    '1776',
    '1793',
    '중앙',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0043138',
    '왕명 추국, 재심·삼심 기능 포함.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F013',
    'NORMATIVE',
    '감찰',
    '암행어사',
    '왕이 지방에 비밀 파견해 수령·민폐를 탐문할 수 있는 제도',
    'binary',
    '0/1',
    'independent review affordance',
    '기존 지방 판단 밖의 정보 획득 경로',
    '1776',
    '1793',
    '지방',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0035165',
    '사건별 실제 권한 범위는 사목과 왕명 확인 필요.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F014',
    'NORMATIVE',
    '감찰',
    '안핵어사',
    '특정 사건을 별도로 조사하는 왕명 특별 조사관의 운용',
    'binary',
    '0/1',
    'independent review affordance',
    '독립 재조사·기존 판단 반전 경로',
    '1776',
    '1793',
    '사건별',
    '정조실록 사례',
    'https://sillok.history.go.kr/id/kva_10206108_002',
    '1778 인천 안핵어사 사례로 정조대 실제 운용 확인.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F015',
    'NORMATIVE',
    '검험',
    '초검-복검-추가검',
    '살인·변사에서 초검 후 복검, 의심 시 삼검·사검까지 가능',
    'categorical',
    '1st/2nd/3rd/4th',
    'hard/soft constraint',
    '사인 판단의 반복검증 구조',
    '1776',
    '1793',
    '전국',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0002110',
    '외방에서는 수령·인근 수령 등이 검험.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F016',
    'NORMATIVE',
    '검험',
    '증수무원록 개정 지침',
    '1792년 개정·간행된 법의학 지침의 존재',
    'binary',
    '0/1',
    'forensic affordance',
    '1792~1793 사인 판단의 contemporaneous manual',
    '1792',
    '1793',
    '전국',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0054038',
    '살인사건 지침서로 법률과 다름없이 적용되었다고 설명.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F017',
    'NORMATIVE',
    '중앙행정',
    '비변사 심의',
    '비변사가 국정·군사·지방 사안을 중앙에서 심의할 수 있음',
    'binary',
    '0/1',
    'review affordance',
    '지방 사건의 중앙 심의·처분 보류 가능성',
    '1776',
    '1793',
    '중앙',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0025147',
    '정조대에도 상설 최고 협의기구로 기능.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F018',
    'NORMATIVE',
    '법원',
    '수교의 법적 성격',
    '국왕이 특정 사안에 법적 성격의 명령을 내릴 수 있음',
    'binary',
    '0/1',
    'dynamic rule affordance',
    '법전 외 사건별 규칙·절차 수정 가능성',
    '1776',
    '1793',
    '중앙/감영',
    '한국민족문화대백과사전',
    'https://encykorea.aks.ac.kr/Article/E0031225',
    '수교는 승정원을 통해 전달되는 법적 성격 명령.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F019',
    'NORMATIVE',
    '신원',
    '격쟁·상언 등 상향 호소',
    '하급 판단에 불복해 상위 권력에 호소하는 경로의 존재',
    'binary',
    '0/1',
    'review affordance',
    '독립 재조사 촉발 가능성',
    '1776',
    '1793',
    '전국',
    '심리록 사례',
    'https://www.moleg.go.kr/mpbleg/mpblegInfo.mo?mid=a10402020000&mpb_leg_pst_seq=125283',
    '1789 통진 박순좌 옥사에서 격쟁 후 도백 재조사 명령.'
);
INSERT INTO STG_INSTITUTIONAL_FEATURES (FEATURE_ID, LAYER, FEATURE_GROUP, FEATURE_NAME, OPERATIONAL_DEFINITION, ENCODING_TYPE, SUGGESTED_VALUES, MODEL_ROLE, INTERPRETATION, VALID_FROM, VALID_TO, GEO_SCOPE, SOURCE_NAME, SOURCE_URL, NOTES)
VALUES (
    'F020',
    'NORMATIVE',
    '문서행정',
    '장계·서계·계문·회계',
    '지방·특사·중앙 관청이 문서로 상향 보고·심리하는 구조',
    'binary',
    '0/1',
    'information-flow affordance',
    '관계없는 기관 간 직접 연결보다 공식 보고 경로 선호',
    '1776',
    '1793',
    '전국',
    '정조실록/비변사등록',
    'https://sillok.history.go.kr/id/kva_11603014_004',
    '안핵어사의 복명·서계가 실제 운용됨.'
);

-- gusun_clean_restart_csv_pack/03_environment_1793.csv (4행)
INSERT INTO STG_ENVIRONMENT_1793 (ENV_ID, LUNAR_DATE, REGION_SCOPE, CONTEXT_TYPE, ATTESTED_CONTEXT, FEATURE_NAME, VALUE, MODEL_ROLE, SOURCE_URL, NOTES)
VALUES (
    'E001',
    '1793-01-22',
    '호서',
    '전염병',
    '호서 도신이 전염병 사망자 수를 치계했고 정조가 구료를 각별히 단속하라고 명함',
    'epidemic_active',
    '1',
    'soft context prior',
    'https://sillok.history.go.kr/id/kva_11701022_002',
    '김명신 개인 감염을 증명하지 않음.'
);
INSERT INTO STG_ENVIRONMENT_1793 (ENV_ID, LUNAR_DATE, REGION_SCOPE, CONTEXT_TYPE, ATTESTED_CONTEXT, FEATURE_NAME, VALUE, MODEL_ROLE, SOURCE_URL, NOTES)
VALUES (
    'E002',
    '1793-01-22',
    '호서',
    '기근·구휼',
    '같은 기사에서 굶주림 구휼이 한창이라고 명시',
    'famine_relief_active',
    '1',
    'macro stress/context',
    'https://sillok.history.go.kr/id/kva_11701022_002',
    '영양·행정 부담 맥락. 직접 사인으로 쓰지 않음.'
);
INSERT INTO STG_ENVIRONMENT_1793 (ENV_ID, LUNAR_DATE, REGION_SCOPE, CONTEXT_TYPE, ATTESTED_CONTEXT, FEATURE_NAME, VALUE, MODEL_ROLE, SOURCE_URL, NOTES)
VALUES (
    'E003',
    '1793-04-10',
    '호서·영남',
    '전염병 지속',
    '정조실록 일별 목록에 ''호서 영남에 전염병이 창궐하므로 여제를 지내게 하다'' 기사 확인',
    'epidemic_persisting',
    '1',
    'soft temporal persistence',
    'https://sillok.history.go.kr/search/inspectionDayList.do?did=kva_11704010&id=kva_117040',
    '이번 단계에서는 기사 제목 수준 확인. 개별 감염 추론 금지.'
);
INSERT INTO STG_ENVIRONMENT_1793 (ENV_ID, LUNAR_DATE, REGION_SCOPE, CONTEXT_TYPE, ATTESTED_CONTEXT, FEATURE_NAME, VALUE, MODEL_ROLE, SOURCE_URL, NOTES)
VALUES (
    'E004',
    '1793-05-12',
    '경외 옥',
    '옥수 전염병 치료',
    '형조 판서 이득신 건의에 따라 서울·지방 전염병 옥수에게 약을 주어 치료하도록 명함',
    'prison_epidemic_treatment_policy',
    '1',
    'custody-health context',
    'https://sillok.history.go.kr/id/kva_11705012_001',
    '구순 사건 기사와 같은 날의 독립 기사.'
);

-- gusun_clean_restart_csv_pack/04_source_records.csv (8행)
INSERT INTO STG_SOURCE_RECORDS (SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, SOURCE_TITLE, SOURCE_URL, SOURCE_DOMAIN, SOURCE_TIER, CASE_ROLE, NOTES)
VALUES (
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '전 부사 구순 사건에 대한 충청도 관찰사 이형원 장계 및 정조 처분',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    'sillok.history.go.kr',
    'S1_PRIMARY',
    '이형원 회동조사 장계·정조 1차 판단·재조사 명령',
    '기사 전체의 구순 사건 부분을 재대조. 5월 판단은 후일 6월 13일 안핵 결과와 구분.'
);
INSERT INTO STG_SOURCE_RECORDS (SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, SOURCE_TITLE, SOURCE_URL, SOURCE_DOMAIN, SOURCE_TIER, CASE_ROLE, NOTES)
VALUES (
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '충청도 암행어사 이조원이 구순 사건을 아뢰고 엄핵을 청함',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    'db.history.go.kr',
    'S1_PRIMARY',
    '이조원 복명·비변사/조정 논의',
    '실록 동일보도보다 일부 배경이 더 구체적이어서 별도 attestation으로 보존.'
);
INSERT INTO STG_SOURCE_RECORDS (SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, SOURCE_TITLE, SOURCE_URL, SOURCE_DOMAIN, SOURCE_TIER, CASE_ROLE, NOTES)
VALUES (
    'SRC3_003',
    '조선왕조실록 정조실록',
    '1793-05-27',
    '호서 암행어사 이조원이 현지의 여러 폐단과 구순 사건을 알림',
    'https://sillok.history.go.kr/id/kva_11705027_002',
    'sillok.history.go.kr',
    'S1_PRIMARY',
    '이조원 복명 교차확인·정조의 어사 비판',
    '동일 단계의 실록 attestation. 비변사등록과 병합하지 않음.'
);
INSERT INTO STG_SOURCE_RECORDS (SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, SOURCE_TITLE, SOURCE_URL, SOURCE_DOMAIN, SOURCE_TIER, CASE_ROLE, NOTES)
VALUES (
    'SRC3_004',
    '승정원일기',
    '1793-05-28',
    '정조가 홍대협에게 구순 사건을 묻고 공주 안핵어사로 차하함',
    'https://sjw.history.go.kr/search/inspectionDayList.do?wday=17930528L0',
    'sjw.history.go.kr',
    'S1_PRIMARY',
    '독립 안핵 임명·지세랑 선행 사용 가능성',
    '정조-홍대협 직접 대화와 안핵어사 차하를 보존.'
);
INSERT INTO STG_SOURCE_RECORDS (SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, SOURCE_TITLE, SOURCE_URL, SOURCE_DOMAIN, SOURCE_TIER, CASE_ROLE, NOTES)
VALUES (
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '충청도 암행어사 윤노동의 별단 중 구순 사건과 비변사의 보류',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    'db.history.go.kr',
    'S1_PRIMARY',
    '윤노동 별단·안핵 복명 전 처분 보류',
    '윤노동의 강한 모함/상해 평가와 비변사의 보류 결정을 분리.'
);
INSERT INTO STG_SOURCE_RECORDS (SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, SOURCE_TITLE, SOURCE_URL, SOURCE_DOMAIN, SOURCE_TIER, CASE_ROLE, NOTES)
VALUES (
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '호서 안핵어사 홍대협의 구순 사건 복명과 정조의 최종 심리',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    'sillok.history.go.kr',
    'S1_PRIMARY',
    '증인 공초·홍대협 안핵 판단·정조 최종 판단과 처분',
    '핵심 원자료. 인물관계→갈등→의심→수사선상→체포·구금→사망→재검증의 연결고리를 누락하지 않도록 재추출.'
);
INSERT INTO STG_SOURCE_RECORDS (SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, SOURCE_TITLE, SOURCE_URL, SOURCE_DOMAIN, SOURCE_TIER, CASE_ROLE, NOTES)
VALUES (
    'SRC3_007',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자기 담당 외 지역을 사찰한 호서 어사 윤노동을 파직함',
    'https://sillok.history.go.kr/id/kva_11706013_001',
    'sillok.history.go.kr',
    'S1_PRIMARY',
    '암행어사 조사범위·절차 통제',
    '구순 사건 사실 자체보다 이조원·윤노동의 조사범위 일탈을 다루는 절차 관련 기사.'
);
INSERT INTO STG_SOURCE_RECORDS (SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, SOURCE_TITLE, SOURCE_URL, SOURCE_DOMAIN, SOURCE_TIER, CASE_ROLE, NOTES)
VALUES (
    'SRC3_008',
    '조선왕조실록 정조실록',
    '1793-06-16',
    '전 충청도 관찰사 이형원을 유임함',
    'https://sillok.history.go.kr/id/kva_11706016_002',
    'sillok.history.go.kr',
    'S1_PRIMARY',
    '6월 13일 파직 뒤 인사 후속조치',
    '6월 13일 파직과 별개의 6월 16일 인사 조치.'
);

-- gusun_clean_restart_csv_pack/05_source_faithful_propositions_AUDIT_ONLY.csv (156행)
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0001',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'STATE',
    '구순',
    '거주',
    '청주 덕평',
    NULL,
    'UNSPECIFIED',
    '청주 덕평',
    'EXPLICIT',
    '구순',
    'CLAIM_WITHIN_OFFICIAL_REPORT',
    'PERSON_LOCATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0002',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '구순',
    '도난 피해를 입었다고 보고됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순',
    'CLAIM_WITHIN_OFFICIAL_REPORT',
    'THEFT_REALITY',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0003',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '구순',
    '김명신을 도적 괴수라고 말했다고 보고됨',
    '김명신',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'CLAIM_WITHIN_OFFICIAL_REPORT',
    'SUSPECT_IDENTIFICATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0004',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '충청병영',
    '김명신을 잡아 달포 이상 구금·조사했다고 보고됨',
    '김명신',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '김명신|충청병영',
    'CLAIM_WITHIN_OFFICIAL_REPORT',
    'DETENTION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    '기사 자체에는 3월 4일 시작일을 부여하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0005',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '수사',
    '확실한 장물을 찾지 못했다고 보고됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '김명신',
    'CLAIM_WITHIN_OFFICIAL_REPORT',
    'EVIDENCE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0006',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '김명신',
    '구금·조사 뒤 사망했다고 보고됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '김명신',
    'CLAIM_WITHIN_OFFICIAL_REPORT',
    'DEATH_OCCURRENCE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    '사망 장소와 직접 사인은 이 명제에 추가하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0007',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '무고한 평민들',
    '모진 형벌을 받았다고 보고됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    NULL,
    'CLAIM_WITHIN_OFFICIAL_REPORT',
    'INVESTIGATION_HARM',
    NULL,
    'OPEN_SET',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0008',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '회동 조사 응답자들',
    '구순과 김명신 사이에 원한이 있었다고 진술했다고 보고됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'NESTED_TESTIMONY',
    'MOTIVE',
    'MOTIVE',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0009',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '회동 조사 응답자들',
    '구순이 도난 상황을 꾸몄다고 진술했다고 보고됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순',
    'NESTED_TESTIMONY',
    'THEFT_FABRICATION',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0010',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '회동 조사 응답자들',
    '구순이 행랑 하인과 교졸을 통해 김명신에게 도적 괴수 누명을 씌웠다고 진술했다고 보고됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'NESTED_TESTIMONY',
    'FRAME_UP_ALLEGATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0011',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '전후 체포자들',
    '구순 집에서 미워하던 사람들이었다고 진술됐다고 보고됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순',
    'NESTED_TESTIMONY',
    'TARGET_SELECTION',
    NULL,
    'OPEN_SET',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0012',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_EVALUATION',
    'JUDGMENT',
    '이문협',
    '수사를 병영 비장에게 전적으로 맡기고 방관했다고 평가됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '이문협',
    'OFFICIAL_EVALUATION',
    'INSTITUTIONAL_FAILURE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0013',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_EVALUATION',
    'JUDGMENT',
    '이광섭',
    '허황한 말을 믿고 무고한 사람을 잘못 잡았다고 평가됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '이광섭',
    'OFFICIAL_EVALUATION',
    'COMMAND_FAILURE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0014',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '비변사',
    'MINISTERIAL_PROPOSAL',
    'ORDER',
    '비변사',
    '이광섭 파직·나문·엄한 감죄를 청함',
    '이광섭',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '이광섭',
    'DIRECT_OFFICIAL_ACTION',
    'PUNISHMENT_PROPOSAL',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0015',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '이광섭 처분 요청을 윤허함',
    '이광섭',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|이광섭',
    'ROYAL_ORDER',
    'ROYAL_ORDER',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0016',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '당시 장계·조사에 따라 도난 자체가 없었다는 방향을 받아들임',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|구순',
    'ROYAL_JUDGMENT',
    'THEFT_REALITY',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    '6월 13일 최종 안핵에서 실제 약간의 도난이 있었던 것으로 수정.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0017',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '구순을 의금부에 잡아 가두고 엄히 조사하도록 명함',
    '구순',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|구순',
    'ROYAL_ORDER',
    'REINVESTIGATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0018',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '이조원',
    '구순 집에 화적이 들었다는 설명이 이치에 맞지 않는다고 판단',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '이조원|구순',
    'INSPECTOR_CLAIM',
    'THEFT_REALITY',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0019',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '구순',
    '김명신의 비판 때문에 앙심을 품고 모함하려 했다고 주장',
    '김명신',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'INSPECTOR_CLAIM',
    'MOTIVE',
    'MOTIVE',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0020',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '구순',
    '도난 상황을 꾸몄다고 주장',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순',
    'INSPECTOR_CLAIM',
    'THEFT_FABRICATION',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0021',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '구순',
    '지세랑이라는 말을 만들어 퍼뜨렸다고 주장',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순',
    'INSPECTOR_CLAIM',
    'JISE_ORIGIN',
    'JISE_ORIGIN',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0022',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '구순',
    '작은 궤짝의 돈을 도둑맞았다고 꾸몄다고 주장',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순',
    'INSPECTOR_CLAIM',
    'FABRICATED_EVIDENCE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0023',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '구순',
    '하인의 부스럼 흔적을 창상으로 꾸몄다고 주장',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순',
    'INSPECTOR_CLAIM',
    'FABRICATED_EVIDENCE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0024',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '김명신',
    '구순이 구성한 죄안으로 병영 옥에서 원통하게 죽었다고 주장',
    NULL,
    NULL,
    'UNSPECIFIED',
    '병영 옥',
    'EXPLICIT_IN_THIS_SOURCE',
    '구순|김명신',
    'INSPECTOR_CLAIM',
    'DEATH_CAUSE',
    'DEATH_CAUSE',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0025',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '김명신의 아내',
    '김명신이 죽은 뒤 따라 죽었다고 보고',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '김명신',
    'INSPECTOR_CLAIM',
    'SPOUSE_DEATH',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0026',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '병사',
    '사건을 자세히 조사하지 않고 하급 보조자에게 맡겼다고 주장',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    NULL,
    'INSPECTOR_CLAIM',
    'COMMAND_FAILURE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0027',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '병영의 하급 보조자',
    '구순의 가객이었다고 주장',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순',
    'INSPECTOR_CLAIM',
    'OFFICIAL_GUEST_RELATION',
    'OFFICIAL_GUEST_RELATION',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    '이 행만으로 하급 보조자를 한재욱으로 동일시하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0028',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '정조/비변사 당상',
    'COURT_DISCUSSION',
    'JUDGMENT',
    '이조원',
    '도난 진위와 중대 사실을 현장에서 직접 안핵하지 않은 점을 비판받음',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '이조원',
    'COURT_EVALUATION',
    'INSPECTOR_FAILURE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0029',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '이조원을 파직하도록 명함',
    '이조원',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|이조원',
    'ROYAL_ORDER',
    'PUNISHMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0030',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '구순을 의금부에 엄히 가두고 반복 신문하도록 명함',
    '구순',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|구순',
    'ROYAL_ORDER',
    'REINVESTIGATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0031',
    'SRC3_003',
    '조선왕조실록 정조실록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '이조원',
    '구순 사건에 대해 도난이 없었다는 방향의 판단을 보고',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '이조원|구순',
    'INSPECTOR_CLAIM',
    'THEFT_REALITY',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705027_002',
    '비변사등록 5월 27일과 같은 단계의 판단을 교차확인.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0032',
    'SRC3_003',
    '조선왕조실록 정조실록',
    '1793-05-27',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '이조원이 직접 안핵하지 않고 전해 들은 말을 서계에 붙인 점을 문제 삼음',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|이조원',
    'ROYAL_JUDGMENT',
    'INSPECTOR_FAILURE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11705027_002',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0033',
    'SRC3_004',
    '승정원일기',
    '1793-05-28',
    '정조',
    'ROYAL_DISCUSSION',
    'ASSERTION',
    '정조',
    '구순 사건과 지세랑 호칭을 홍대협에게 물음',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|구순|홍대협',
    'DIRECT_COURT_DIALOGUE',
    'ANHAEK_ASSIGNMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sjw.history.go.kr/search/inspectionDayList.do?wday=17930528L0',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0034',
    'SRC3_004',
    '승정원일기',
    '1793-05-28',
    '홍대협',
    'DIRECT_STATEMENT',
    'ASSERTION',
    '홍대협',
    '귀로에 사건 개요를 조금 들었다고 말함',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '홍대협|구순',
    'DIRECT_COURT_DIALOGUE',
    'PRIOR_KNOWLEDGE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sjw.history.go.kr/search/inspectionDayList.do?wday=17930528L0',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0035',
    'SRC3_004',
    '승정원일기',
    '1793-05-28',
    '홍대협',
    'DIRECT_STATEMENT',
    'ASSERTION',
    '홍대협',
    '지세랑 호칭은 예전 호중 화적도 사용한 적이 있어 이번에 처음 생긴 말이 아닌 듯하다고 말함',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '홍대협',
    'DIRECT_COURT_DIALOGUE',
    'JISE_ORIGIN',
    'JISE_ORIGIN',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sjw.history.go.kr/search/inspectionDayList.do?wday=17930528L0',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0036',
    'SRC3_004',
    '승정원일기',
    '1793-05-28',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '홍대협에게 내려가 자세히 조사해 오라고 명함',
    '홍대협',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|홍대협',
    'ROYAL_ORDER',
    'ANHAEK_ASSIGNMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sjw.history.go.kr/search/inspectionDayList.do?wday=17930528L0',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0037',
    'SRC3_004',
    '승정원일기',
    '1793-05-28',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '홍대협을 충청도 공주 안핵어사로 차하함',
    '홍대협',
    NULL,
    'UNSPECIFIED',
    '공주',
    'EXPLICIT',
    '정조|홍대협',
    'ROYAL_ORDER',
    'ANHAEK_ASSIGNMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sjw.history.go.kr/search/inspectionDayList.do?wday=17930528L0',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0038',
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '윤노동',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '구순',
    '도적을 만났다고 말하고 영교를 불러 김명신 등의 이름을 써 주었다고 주장',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'INSPECTOR_CLAIM',
    'SUSPECT_LIST_ORIGIN',
    NULL,
    'OPEN_SET',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0039',
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '윤노동',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '김명신',
    '보수·구금 중 병들어 죽었다고 보고',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '김명신',
    'INSPECTOR_CLAIM',
    'DEATH_OCCURRENCE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    '윤노동 별단의 ''保囚病死'' 취지. 직접 사인과 책임 귀속은 별도 명제로 분리.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0040',
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '윤노동',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '여러 죄수',
    '참혹한 형벌을 받았다고 보고',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    NULL,
    'INSPECTOR_CLAIM',
    'INVESTIGATION_HARM',
    NULL,
    'OPEN_SET',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0041',
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '윤노동',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '수사',
    '진정한 장물을 얻지 못했다고 보고',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    NULL,
    'INSPECTOR_CLAIM',
    'EVIDENCE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0042',
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '윤노동',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '한재욱',
    '변가의 처를 꾀어 김명신이 도적 괴수라는 취지의 공초를 내게 했다고 주장',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '한재욱|김명신|변가의 처',
    'INSPECTOR_CLAIM',
    'COACHING',
    'COACHING',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0043',
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '비변사',
    'MINISTERIAL_PROPOSAL',
    'ORDER',
    '비변사',
    '홍대협의 안핵 복명 전이므로 윤노동 별단의 구순 사건 처리를 보류할 것을 청함',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '홍대협|윤노동|구순',
    'DIRECT_OFFICIAL_ACTION',
    'PROCEDURAL_HOLD',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0044',
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '비변사의 보류 요청을 윤허함',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조',
    'ROYAL_ORDER',
    'PROCEDURAL_HOLD',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0045',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_REPORT',
    'ACTION',
    '홍대협',
    '공주목에 도착해 관련자들을 차례로 신문함',
    NULL,
    NULL,
    'UNSPECIFIED',
    '공주목',
    'EXPLICIT',
    '홍대협',
    'OFFICIAL_REPORT',
    'ANHAEK',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0046',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '명업',
    'TESTIMONY',
    'ASSERTION',
    '명업',
    '구순 집 계집종의 남편이며 바깥사랑에 거주했다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '명업|구순',
    'TESTIMONY',
    'IDENTITY_RELATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0047',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '명업',
    'TESTIMONY',
    'ASSERTION',
    '나복',
    '2월 22일 밤 명업에게 도적이 들었다고 알렸다고 진술됨',
    NULL,
    '1793-02-22 밤',
    'DAY_NIGHT',
    NULL,
    'UNSPECIFIED',
    '명업|나복|구순',
    'NESTED_TESTIMONY',
    'THEFT_REALITY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0048',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '명업',
    'TESTIMONY',
    'ASSERTION',
    '나복',
    '도적 30여 명이 횃불을 들고 들어와 지세대감이라 자칭하고 돈과 물품을 훔쳤다고 말했다고 진술됨',
    NULL,
    '1793-02-22 밤',
    'DAY_NIGHT',
    NULL,
    'UNSPECIFIED',
    '나복|구순',
    'NESTED_TESTIMONY',
    'THEFT_DESCRIPTION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '도적 수·자칭·피해 규모는 나복 발언을 명업이 전한 중첩 진술.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0049',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '명업',
    'TESTIMONY',
    'ASSERTION',
    '김명신',
    '본래 구순과 친숙하여 날마다 왕래했다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '김명신|구순',
    'TESTIMONY',
    'RELATIONSHIP',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0050',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '명업',
    'TESTIMONY',
    'ASSERTION',
    '김명신',
    '2월 초 박거사 일로 구순에게 편지를 보내 힐책했다고 진술',
    NULL,
    '1793-02 초순',
    'EARLY_MONTH',
    NULL,
    'UNSPECIFIED',
    '김명신|구순',
    'TESTIMONY',
    'RELATIONSHIP_CONFLICT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0051',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '명업',
    'TESTIMONY',
    'STATE',
    '구순·김명신',
    '그 뒤 왕래가 끊겼다고 진술',
    NULL,
    '1793-02 초순 이후',
    'AFTER_EARLY_MONTH',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'TESTIMONY',
    'RELATIONSHIP_CONFLICT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0052',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '명업',
    'TESTIMONY',
    'ASSERTION',
    '구순',
    '소장을 올려 체포령이 내려졌다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순',
    'TESTIMONY',
    'COMPLAINT_ARREST_ORDER',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0053',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '명업',
    'TESTIMONY',
    'ACTION',
    '구순',
    '찾아온 장교 한 명을 안행랑으로 불러 조용히 대화했다고 진술',
    '장교 1명',
    NULL,
    'UNSPECIFIED',
    '구순 집 안행랑',
    'EXPLICIT',
    '구순',
    'TESTIMONY',
    'PRIVATE_CONTACT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0054',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '명업',
    'TESTIMONY',
    'ASSERTION',
    '명업',
    '병영 뜰 공초에서 처음에는 사실대로 말했으나 위협이 두려워 도적이 없었다는 취지로 바꾸었다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    '병영 뜰',
    'EXPLICIT',
    '명업',
    'TESTIMONY',
    'TESTIMONY_CHANGE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0055',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ACTION',
    '병영',
    '2월 28일 밤 이진욱을 비장청으로 부름',
    '이진욱',
    '1793-02-28 밤',
    'DAY_NIGHT',
    '비장청',
    'EXPLICIT',
    '이진욱',
    'TESTIMONY',
    'SUMMON',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0056',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ORDER',
    '한재욱',
    '이진욱·조계완 등에게 덕평으로 가도록 지시했다고 진술',
    '이진욱·조계완 등',
    '1793-02-28 밤',
    'DAY_NIGHT',
    '비장청',
    'EXPLICIT',
    '한재욱|이진욱|조계완',
    'TESTIMONY',
    'DISPATCH',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0057',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ORDER',
    '한재욱',
    '변지돌과 정원돌을 잡아오라고 지시했다고 진술',
    '변지돌·정원돌',
    '1793-02-28 밤',
    'DAY_NIGHT',
    NULL,
    'UNSPECIFIED',
    '한재욱|변지돌|정원돌',
    'TESTIMONY',
    'ARREST_ORDER',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0058',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ACTION',
    '한재욱',
    '철편 네 개를 만들어 주었다고 진술',
    '철편 4개',
    '1793-02-28 밤~29 새벽',
    'OVERNIGHT',
    NULL,
    'UNSPECIFIED',
    '한재욱|이진욱',
    'TESTIMONY',
    'OPERATION_PREP',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '원문 주어는 문맥상 한재욱 공초가 아니라 이진욱 공초 안의 한재욱 행위로 읽힘.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0059',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ASSERTION',
    '한재욱',
    '변지돌과 정원돌이 처남매부 사이이며 변지돌이 힘이 세니 조심하라고 말했다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '한재욱|변지돌|정원돌',
    'TESTIMONY',
    'ARREST_PRECAUTION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0060',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'STATE',
    '변지돌',
    '이미 공주진에서 잡혀간 상태였다고 진술',
    NULL,
    '1793-02-29',
    'DAY',
    '공주진',
    'EXPLICIT',
    '변지돌',
    'TESTIMONY',
    'CUSTODY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0061',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ACTION',
    '이진욱 등 장교',
    '변지돌의 아우 재돌의 처 자미덕만 잡았다고 진술',
    '자미덕',
    '1793-02-29',
    'DAY',
    NULL,
    'UNSPECIFIED',
    '이진욱|자미덕|재돌|변지돌',
    'TESTIMONY',
    'APPREHENSION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0062',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ACTION',
    '장교 일행',
    '자미덕을 데리고 구순 집으로 가 도난 상황을 물었다고 진술',
    '구순',
    '1793-02-29',
    'DAY',
    '구순 집',
    'EXPLICIT',
    '자미덕|구순|이진욱',
    'TESTIMONY',
    'INTERROGATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0063',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ASSERTION',
    '구순',
    '잃은 물건들을 열거했다고 진술됨',
    NULL,
    '1793-02-29',
    'DAY',
    '구순 집',
    'EXPLICIT',
    '구순',
    'NESTED_TESTIMONY',
    'THEFT_DESCRIPTION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0064',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ASSERTION',
    '구순',
    '도적이 스스로 지세대사라고 자칭했다고 말했다고 진술됨',
    NULL,
    '1793-02-29',
    'DAY',
    '구순 집',
    'EXPLICIT',
    '구순',
    'NESTED_TESTIMONY',
    'JISE_ORIGIN',
    'JISE_ORIGIN',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0065',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ORDER',
    '병사',
    '3월 4일 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했다고 진술',
    '풍각 김생원(김명신)·흥덕 김생원(김갑득)',
    '1793-03-04',
    'DAY',
    NULL,
    'UNSPECIFIED',
    '이광섭|김명신|김갑득',
    'TESTIMONY',
    'ARREST_ORDER',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '해당 문장 표면 주어는 ''병사''. 이 행 자체에서 병사=이광섭을 새로 추론하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0066',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'STATE',
    '풍각 김생원',
    '김명신으로 식별됨',
    NULL,
    '1793-03-04',
    'DAY',
    NULL,
    'UNSPECIFIED',
    '김명신',
    'TESTIMONY',
    'IDENTITY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0067',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'STATE',
    '흥덕 김생원',
    '김갑득으로 식별됨',
    NULL,
    '1793-03-04',
    'DAY',
    NULL,
    'UNSPECIFIED',
    '김갑득',
    'TESTIMONY',
    'IDENTITY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0068',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '이진욱',
    'TESTIMONY',
    'ACTION',
    '장교 일행',
    '병사 분부에 따라 김명신과 김갑득을 잡아왔다고 진술',
    '김명신·김갑득',
    '1793-03-04',
    'DAY',
    NULL,
    'UNSPECIFIED',
    '김명신|김갑득|이광섭',
    'TESTIMONY',
    'APPREHENSION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0069',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '조계완',
    'TESTIMONY',
    'ACTION',
    '조계완',
    '풍각 김생원을 잡으러 가는 길에 구순 집에 들렀다고 진술',
    NULL,
    '1793-03-04',
    'DAY',
    '구순 집',
    'EXPLICIT',
    '조계완|구순|김명신',
    'TESTIMONY',
    'PRIVATE_CONTACT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0070',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '조계완',
    'TESTIMONY',
    'ASSERTION',
    '구순',
    '왜 다시 왔는지 물었다고 진술됨',
    '조계완',
    '1793-03-04',
    'DAY',
    NULL,
    'UNSPECIFIED',
    '구순|조계완',
    'NESTED_TESTIMONY',
    'QUESTION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0071',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '조계완',
    'TESTIMONY',
    'ASSERTION',
    '조계완',
    '풍각의 상주를 잡으러 왔다고 답했다고 진술',
    NULL,
    '1793-03-04',
    'DAY',
    NULL,
    'UNSPECIFIED',
    '조계완|김명신',
    'TESTIMONY',
    'RESPONSE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0072',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '조계완',
    'TESTIMONY',
    'ASSERTION',
    '구순',
    '이제야 도적 다스리는 일이 바른 길을 얻었다는 취지로 말했다고 진술됨',
    NULL,
    '1793-03-04',
    'DAY',
    NULL,
    'UNSPECIFIED',
    '구순|조계완',
    'NESTED_TESTIMONY',
    'REACTION_TO_ARREST',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0073',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '조계완',
    'TESTIMONY',
    'ACTION',
    '구순',
    '서찰 한 장을 건네며 병사에게 전해달라고 요구했다고 진술됨',
    '조계완',
    '1793-03-04',
    'DAY',
    NULL,
    'UNSPECIFIED',
    '구순|조계완|이광섭',
    'NESTED_TESTIMONY',
    'DOCUMENT_TRANSFER',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0074',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자미덕',
    'TESTIMONY',
    'STATE',
    '재돌',
    '아산에 나가 있었다고 진술',
    NULL,
    '자미덕 체포 전',
    'RELATIVE_ONLY',
    '아산',
    'EXPLICIT',
    '재돌|자미덕',
    'TESTIMONY',
    'PERSON_LOCATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0075',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자미덕',
    'TESTIMONY',
    'ACTION',
    '병영 장교',
    '자미덕을 병영으로 붙잡아 갔다고 진술',
    '자미덕',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '자미덕',
    'TESTIMONY',
    'APPREHENSION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0076',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자미덕',
    'TESTIMONY',
    'ACTION',
    '병영',
    '자미덕을 도적이라고 하며 한 차례 신문했다고 진술',
    '자미덕',
    NULL,
    'UNSPECIFIED',
    '병영',
    'EXPLICIT',
    '자미덕',
    'TESTIMONY',
    'INTERROGATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0077',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자미덕',
    'TESTIMONY',
    'STATE',
    '자미덕',
    '신문 뒤 비장청 다모방에 구류되었다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    '비장청 다모방',
    'EXPLICIT',
    '자미덕',
    'TESTIMONY',
    'DETENTION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0078',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자미덕',
    'TESTIMONY',
    'ACTION',
    '한 비장',
    '그 후 매일 자미덕을 방안으로 불러들였다고 진술',
    '자미덕',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '자미덕|한 비장',
    'TESTIMONY',
    'COACHING',
    'COACHING',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0079',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자미덕',
    'TESTIMONY',
    'ASSERTION',
    '한 비장',
    '자미덕의 남편 재돌이 이미 체포되었다고 말했다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '자미덕|재돌|한 비장',
    'TESTIMONY',
    'COACHING',
    'COACHING',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0080',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자미덕',
    'TESTIMONY',
    'ASSERTION',
    '한 비장',
    '정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적들이라고 말하면 자미덕과 남편을 다음 날 석방하겠다고 말했다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '한 비장|자미덕|재돌|정원돌|이집거|김갑득|김성손|김흥득',
    'TESTIMONY',
    'COACHING',
    'COACHING',
    'OPEN_SET_EXPLICIT_MEMBERS',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '''등''이 있으므로 명시된 5명 외 추가 대상 가능성을 닫지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0081',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자미덕',
    'TESTIMONY',
    'ACTION',
    '한 비장',
    '자미덕에게 떡과 밥을 주었다고 진술',
    '자미덕',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '한 비장|자미덕',
    'TESTIMONY',
    'COACHING',
    'COACHING',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0082',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자미덕',
    'TESTIMONY',
    'ACTION',
    '자미덕·이집거',
    '서로 대질했다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '자미덕|이집거',
    'TESTIMONY',
    'CONFRONTATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '대질은 두 당사자가 참여하는 사건으로 보존; 단방향 actor-target로 축약하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0083',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '자미덕',
    'TESTIMONY',
    'ASSERTION',
    '자미덕',
    '이집거와 대질할 때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '자미덕|이집거|한 비장',
    'TESTIMONY',
    'COACHING',
    'COACHING',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '거짓말의 구체 내용이 무엇인지 이 문장만으로 추가 특정하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0084',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '한재욱',
    'TESTIMONY',
    'ASSERTION',
    '구순',
    '구순 집 도난이 진영에 정소된 뒤였다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '구순|한재욱',
    'TESTIMONY',
    'COMPLAINT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0085',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '한재욱',
    'TESTIMONY',
    'ACTION',
    '한재욱',
    '도적 진상을 탐지하려고 병영 아전 유제희를 내보냈다고 진술',
    '유제희',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '한재욱|유제희',
    'TESTIMONY',
    'DISPATCH',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0086',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '한재욱',
    'TESTIMONY',
    'ASSERTION',
    '유제희',
    '변지돌·변재돌·정원돌·김명신·김성손·김흥득·김흥길 등의 성명을 적어왔다고 진술됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '유제희|변지돌|변재돌|정원돌|김명신|김성손|김흥득|김흥길',
    'NESTED_TESTIMONY',
    'SUSPECT_LIST',
    NULL,
    'OPEN_SET_EXPLICIT_MEMBERS',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '''등''이 있으므로 7명이 명시되지만 폐쇄형 완전 명단으로 보지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0087',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '한재욱',
    'TESTIMONY',
    'ASSERTION',
    '유제희',
    '그 이름들을 자신이 직접 염탐해 알아냈다고 말했다고 진술됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '유제희|한재욱',
    'NESTED_TESTIMONY',
    'SUSPECT_LIST_ORIGIN',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0088',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '한재욱',
    'TESTIMONY',
    'ACTION',
    '한재욱',
    '자미덕을 방안으로 불러 남은 밥을 주었다고 인정',
    '자미덕',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '한재욱|자미덕',
    'TESTIMONY',
    'COACHING',
    'COACHING',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0089',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '한재욱',
    'TESTIMONY',
    'ASSERTION',
    '유제희',
    '석단 공초에서 김명신이 도적 괴수라고 했으니 자미덕에게 다시 물어보라고 말했다고 진술됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '유제희|석단|김명신|자미덕|한재욱',
    'NESTED_TESTIMONY',
    'SEOKDAN_INFORMATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0090',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '한재욱',
    'TESTIMONY',
    'ACTION',
    '한재욱',
    '유제희 말에 따라 자미덕에게 다시 물었다고 진술',
    '자미덕',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '한재욱|유제희|자미덕',
    'TESTIMONY',
    'INTERROGATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0091',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '한재욱',
    'TESTIMONY',
    'ASSERTION',
    '자미덕',
    '재질문에 모른다고 답했다고 진술됨',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '한재욱|자미덕',
    'NESTED_TESTIMONY',
    'RESPONSE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0092',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '한재욱',
    'TESTIMONY',
    'ASSERTION',
    '한재욱',
    '자미덕을 은밀히 사주한 일이 없다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '한재욱|자미덕',
    'TESTIMONY',
    'COACHING',
    'COACHING',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0093',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '한재욱',
    'TESTIMONY',
    'ASSERTION',
    '한재욱',
    '구순과 평생 모르는 사이라고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '한재욱|구순',
    'TESTIMONY',
    'HAN_GUSUN_RELATION',
    'HAN_GUSUN_RELATION',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0094',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '유제희',
    'TESTIMONY',
    'ACTION',
    '유제희',
    '당초 현지에 가서 탐문했다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '유제희',
    'TESTIMONY',
    'INQUIRY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0095',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '유제희',
    'TESTIMONY',
    'ASSERTION',
    '구순',
    '풍각 김상제도 극히 수상하다고 말했다고 진술됨',
    '김명신',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '유제희|구순|김명신',
    'NESTED_TESTIMONY',
    'SUSPECT_IDENTIFICATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0096',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '유제희',
    'TESTIMONY',
    'ACTION',
    '유제희',
    '그 말을 원돌 등의 이름과 함께 기록해 올렸다고 진술',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '유제희|구순|김명신|정원돌',
    'TESTIMONY',
    'SUSPECT_LIST_ORIGIN',
    NULL,
    'OPEN_SET',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0097',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_FINDING',
    'JUDGMENT',
    '홍대협',
    '약간의 도난은 실제였다고 판단',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '홍대협|구순',
    'OFFICIAL_FINDING',
    'THEFT_REALITY',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0098',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_FINDING',
    'JUDGMENT',
    '홍대협',
    '도난은 큰 화적 사건이 아니라 보통 좀도둑 수준이었다고 평가',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    NULL,
    'OFFICIAL_FINDING',
    'THEFT_SCALE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0099',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_FINDING',
    'STATE',
    '지세 호칭 조사',
    '여러 차례 조사와 별도 탐문에도 기원을 확정하지 못함',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    NULL,
    'OFFICIAL_FINDING',
    'JISE_ORIGIN',
    'JISE_ORIGIN',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0100',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_EVALUATION',
    'JUDGMENT',
    '이광섭',
    '구순의 과장과 아전의 거짓 보고를 믿고 장물 없이 큰 도적으로 판단했다고 평가',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '홍대협|이광섭|구순',
    'OFFICIAL_EVALUATION',
    'COMMAND_FAILURE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0101',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_EVALUATION',
    'JUDGMENT',
    '김명신',
    '죽음은 질병 때문이었다고 평가',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '홍대협|김명신',
    'OFFICIAL_EVALUATION',
    'DEATH_CAUSE',
    'DEATH_CAUSE',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0102',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_EVALUATION',
    'JUDGMENT',
    '이문협',
    '장물부터 확보하지 않고 장교·나졸을 풀어 평민을 잡고 병영 비장 지휘대로 죄를 얽었다고 평가',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '홍대협|이문협',
    'OFFICIAL_EVALUATION',
    'INVESTIGATION_METHOD',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0103',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '공주목 안핵의 핵심을 도난 여부·김명신 사망 원인·지세 호칭 날조 여부의 세 의안으로 분리',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|구순|김명신',
    'ROYAL_JUDGMENT',
    'ISSUE_FRAMING',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0104',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '도난은 실제로 있었다고 판단',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|구순',
    'FINAL_ROYAL_FINDING',
    'THEFT_REALITY',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0105',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '김명신 부처가 전염병에 걸려 죽은 것으로 판단',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|김명신',
    'FINAL_ROYAL_FINDING',
    'DEATH_CAUSE',
    'DEATH_CAUSE',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0106',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '김명신이 곤장을 맞지 않았고 평범한 신문도 받지 않았다고 판단',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|김명신',
    'FINAL_ROYAL_FINDING',
    'TREATMENT_OF_KIM',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0107',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '지세대감·지세대사·지세랑 호칭은 예전 무식한 좀도둑들도 쓰던 말이라고 판단',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|구순',
    'FINAL_ROYAL_FINDING',
    'JISE_ORIGIN',
    'JISE_ORIGIN',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0108',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '구순이 지세 호칭을 스스로 만들어냈다는 죄는 면하게 됐다고 판단',
    NULL,
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|구순',
    'FINAL_ROYAL_FINDING',
    'JISE_ORIGIN',
    'JISE_ORIGIN',
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0109',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '구순을 사형에서 감해 외딴 섬으로 정배하도록 명함',
    '구순',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|구순',
    'ROYAL_ORDER',
    'PUNISHMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0110',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '구순을 신지도에 정배함',
    '구순',
    NULL,
    'UNSPECIFIED',
    '신지도',
    'EXPLICIT',
    '정조|구순',
    'ROYAL_ORDER',
    'PUNISHMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0111',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '이광섭을 영동현에 유배함',
    '이광섭',
    NULL,
    'UNSPECIFIED',
    '영동현',
    'EXPLICIT',
    '정조|이광섭',
    'ROYAL_ORDER',
    'PUNISHMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0112',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '병영 비장 한가를 도백이 엄히 세 차례 형장 친 뒤 먼 섬의 종으로 보내도록 명함',
    '한가',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|한재욱',
    'ROYAL_ORDER',
    'PUNISHMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '기사 앞부분의 ''한 비장/한재욱''과 연결되지만, 처분문 자체는 ''한가''로 표현.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0113',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '충청도 관찰사 이형원을 파직하도록 명함',
    '이형원',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|이형원',
    'ROYAL_ORDER',
    'PUNISHMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0114',
    'SRC3_008',
    '조선왕조실록 정조실록',
    '1793-06-16',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '전 충청도 관찰사 이형원을 유임함',
    '이형원',
    NULL,
    'UNSPECIFIED',
    NULL,
    'UNSPECIFIED',
    '정조|이형원',
    'ROYAL_ORDER',
    'POST_CASE_APPOINTMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECTLY_STATED',
    'https://sillok.history.go.kr/id/kva_11706016_002',
    '6월 13일 파직 후 6월 16일의 별도 인사 조치.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0115',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '회동 조사 응답자들',
    '구순이 김명신에게 원한이 있어 해치려는 마음을 품었다고 진술했다고 보고됨',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'NESTED_TESTIMONY',
    'RELATION_CONFLICT',
    NULL,
    'NOT_APPLICABLE',
    'NESTED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    '5/12 장계 속 회동 조사 응답자들의 주장. 역사적 사실로 확정하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0116',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '회동 조사 응답자들',
    '구순이 행랑 하인들에게 당부해 밖으로 소문을 퍼뜨렸다고 진술했다고 보고됨',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순',
    'NESTED_TESTIMONY',
    'RUMOR_PROPAGATION',
    NULL,
    'NOT_APPLICABLE',
    'NESTED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0117',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '이형원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '회동 조사 응답자들',
    '구순이 교졸들과 결탁해 성명을 써 주고 김명신에게 도적 괴수 누명을 씌웠다고 진술했다고 보고됨',
    '김명신',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'NESTED_TESTIMONY',
    'NAME_SUPPLY_AND_FRAMING',
    NULL,
    'NOT_APPLICABLE',
    'NESTED',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0118',
    'SRC3_001',
    '조선왕조실록 정조실록',
    '1793-05-12',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '김명신이 병으로 죽었는지와 별개로 원통함을 품고 죽었다는 점과 구순에게서 비롯되었다는 점을 당시 사실로 받아들임',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'ROYAL_JUDGMENT',
    'RESPONSIBILITY_5M',
    'DEATH_RESPONSIBILITY',
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11705012_003',
    '5/12 시점의 판단. 6/13 최종 판단에서 직접 사망원인과 책임을 다시 구분함.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0119',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '구순의 집',
    '앞이 큰길에 접하고 마을이 조밀하여 화적이 들어오기 어려운 곳이라고 이조원이 판단',
    NULL,
    NULL,
    'UNKNOWN',
    '청주 덕평',
    'SOURCE_ATTESTED',
    NULL,
    'INSPECTOR_CLAIM',
    'THEFT_PLAUSIBILITY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    '도난 부재 판단의 근거 중 하나.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0120',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '이조원',
    '화적이 들었다면 사방 이웃과 노복이 알아야 하는데 한 마을에서 목격자가 없다는 점을 불합리하다고 판단',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    NULL,
    'INSPECTOR_CLAIM',
    'THEFT_PLAUSIBILITY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0121',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '김명신',
    '구순이 거상 중 조석의 상식에 참여하지 않은 일을 비판했다고 보고',
    '구순',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '김명신|구순',
    'INSPECTOR_CLAIM',
    'PRIOR_CONFLICT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    '비변사등록 국역의 구체 사유를 보존. 단순 ''행실 비판''으로 축약하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0122',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '김명신',
    '피우와 관련해 구순의 형이 용접하는 것을 허락하지 않은 일 등을 비판했다고 보고',
    '구순',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '김명신|구순',
    'INSPECTOR_CLAIM',
    'PRIOR_CONFLICT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    '비변사등록 번역 표현을 보수적으로 보존. ''피우''의 구체 관계를 이 행에서 추가 해석하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0123',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '이조원',
    '김명신 사후 그 아내도 따라 죽었고 사건 뒤 도 전체의 공분이 컸다고 보고',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '김명신|김명신의 아내',
    'INSPECTOR_CLAIM',
    'PUBLIC_REACTION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0124',
    'SRC3_002',
    '비변사등록',
    '1793-05-27',
    '이조원',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '병영의 하급 보조자',
    '구순의 가객이어서 구순의 부탁을 따라 옥안을 단련했다고 이조원이 주장',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순',
    'INSPECTOR_CLAIM',
    'BARRACKS_AIDE_RELATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_05_0510&type=joseon',
    '이 행만으로 하급 보조자=한재욱을 확정하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0125',
    'SRC3_003',
    '조선왕조실록 정조실록',
    '1793-05-27',
    '이조원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '김명신',
    '구순과 이웃해 살며 구순의 불효한 행실을 늘 비판했다고 실록에 보고됨',
    '구순',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '김명신|구순',
    'INSPECTOR_CLAIM',
    'PRIOR_CONFLICT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11705027_002',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0126',
    'SRC3_003',
    '조선왕조실록 정조실록',
    '1793-05-27',
    '이조원',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '이조원',
    '구순 집의 입지·마을 상황과 목격 부재를 들어 화적 설명이 이치에 맞지 않는다고 판단',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    NULL,
    'INSPECTOR_CLAIM',
    'THEFT_PLAUSIBILITY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11705027_002',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0127',
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '윤노동',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '윤노동',
    '구순이 도난을 칭탁하고 양민을 얽어 무고해 목숨을 상하게 한 일이 있다고 평가',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'INSPECTOR_CLAIM',
    'FRAMEUP_AND_HARM',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECT',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    '윤노동 별단의 강한 평가이며 역사적 사실로 자동 승격하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0128',
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '윤노동',
    'INSPECTOR_REPORT',
    'ASSERTION',
    '한재욱',
    '변가의 처를 여러 방식으로 꾀어 김명신이 확실한 도적 괴수라는 내용의 공초를 내게 했다고 주장',
    '변가의 처',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '한재욱|김명신',
    'INSPECTOR_CLAIM',
    'COACHING',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0129',
    'SRC3_005',
    '비변사등록',
    '1793-06-11',
    '윤노동',
    'INSPECTOR_REPORT',
    'JUDGMENT',
    '윤노동',
    '구순 사건 관계자를 법에 따라 처단해 도 전체의 분함을 풀어야 한다고 건의',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    NULL,
    'INSPECTOR_RECOMMENDATION',
    'PUNISHMENT_RECOMMENDATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://db.history.go.kr/common/compareViewer.do?levelId=bb_181r_001_06_0070&type=joseon',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0130',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '실록 편찬 기록',
    'CHRONICLE',
    'ACTION',
    '홍대협',
    '호서 안핵어사로 복명하고 편전에서 정조에게 보고함',
    NULL,
    NULL,
    'UNKNOWN',
    '편전',
    'SOURCE_ATTESTED',
    '홍대협|정조',
    'DIRECT_OFFICIAL_ACTION',
    'PROCEDURE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0131',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '홍대협',
    '내려가는 길에 널리 탐문했을 때에는 사람들이 애당초 도난이 없었다고 말했다고 보고',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    NULL,
    'OFFICIAL_REPORT_OF_HEARSAY',
    'THEFT_REALITY',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '정식 안핵 공초와 구분되는 사전 탐문 결과.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0132',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_FINDING',
    'JUDGMENT',
    '홍대협',
    '정식 조사에서는 명업 등 세 사람의 공초가 분명해 약간의 실제 도난이 있었다고 판단',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '명업',
    'OFFICIAL_FINDING',
    'THEFT_REALITY',
    'THEFT_REALITY',
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0133',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_FINDING',
    'JUDGMENT',
    '홍대협',
    '실제 도난은 보통 좀도둑의 소행에 불과하다고 평가',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    NULL,
    'OFFICIAL_FINDING',
    'THEFT_SCALE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0134',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_EVALUATION',
    'JUDGMENT',
    '구순',
    '사실대로 고발할 수 있었는데도 과장하고 의혹을 키우다가 미운 사람에게 악감을 행사해 날조된 옥사를 사주해 이루기에 이르렀다고 평가',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'OFFICIAL_EVALUATION',
    'RESENTMENT_TO_FABRICATED_CASE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '홍대협의 평가. ''修隙媢嫉之人, 嗾成構捏之獄'' 취지를 보존.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0135',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_REPORT',
    'ASSERTION',
    '사람들',
    '구순 사건의 전개에 놀라고 분개했다고 홍대협이 보고',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    NULL,
    'OFFICIAL_REPORT',
    'PUBLIC_REACTION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0136',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_FINDING',
    'STATE',
    '지세 호칭의 기원',
    '여러 차례 신문과 별도 탐문에도 단서를 얻지 못했고 서로 다른 말이 나와 확정되지 않음',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    NULL,
    'OFFICIAL_FINDING',
    'JISE_ORIGIN',
    'JISE_ORIGIN',
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0137',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_RECOMMENDATION',
    'JUDGMENT',
    '홍대협',
    '지세 호칭의 실정을 밝히려면 구순을 의금부에서 엄히 국문할 필요가 있다고 건의',
    '구순',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '홍대협|구순',
    'OFFICIAL_RECOMMENDATION',
    'JISE_INVESTIGATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0138',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_EVALUATION',
    'JUDGMENT',
    '이광섭',
    '평민을 일부러 해치려는 의도에서 나온 것은 아니라고 보면서도 결과적으로 옥안을 강제로 만든 책임은 피하기 어렵다고 평가',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '이광섭',
    'OFFICIAL_EVALUATION',
    'COMMANDER_INTENT_VS_OUTCOME',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0139',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_EVALUATION',
    'JUDGMENT',
    '김명신',
    '질병으로 죽었더라도 사람들이 원통하게 죽었다고 말하는 것은 정황상 그럴 만하다고 평가',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '김명신',
    'OFFICIAL_EVALUATION',
    'DEATH_RESPONSIBILITY',
    'DEATH_RESPONSIBILITY',
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0140',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '홍대협',
    'OFFICIAL_EVALUATION',
    'JUDGMENT',
    '이광섭',
    '한쪽 말만 듣고 잘못 판결한 죄는 중하게 다스려야 한다고 평가',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '이광섭',
    'OFFICIAL_EVALUATION',
    'COMMANDER_RESPONSIBILITY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0141',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '김명신이 구순 때문에 죽었다고 하는 직접 인과는 십분 확실하다고 할 수 없다고 판단',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'FINAL_ROYAL_FINDING',
    'DIRECT_DEATH_CAUSATION',
    'DEATH_RESPONSIBILITY',
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '전염병·무장형/평문 부재 판단과 연결되지만 구순의 절차적 책임 판단과 별개.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0142',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '구순',
    '김명신에게 사적인 감정을 품고 갈등을 일으켰다고 판단',
    '김명신',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'FINAL_ROYAL_FINDING',
    'PRIVATE_GRIEVANCE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0143',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '구순',
    '병영의 염탐 담당자에게 김명신의 성명을 적어 주었다고 판단',
    '김명신',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'FINAL_ROYAL_FINDING',
    'NAME_SUPPLY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0144',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '구순의 사적 감정·갈등과 성명 제공을 거쳐 김명신이 횡액을 입고 원통하게 죽는 결과에 이르렀다고 책임을 연결해 판단',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순|김명신',
    'FINAL_ROYAL_FINDING',
    'RESPONSIBILITY_CHAIN',
    'DEATH_RESPONSIBILITY',
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '직접 사망원인=구순으로 단순화하지 않음. 정조의 책임 귀속 사슬을 그대로 보존.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0145',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '구순',
    '사건이 이렇게 된 원인을 구순의 무상함과 불량함에 돌려 책임을 물음',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순',
    'FINAL_ROYAL_FINDING',
    'CULPABILITY',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0146',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '지세 대감·대사 등의 말을 구순이 스스로 만들어냈다는 죄는 인정하지 않음',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순',
    'FINAL_ROYAL_FINDING',
    'JISE_ORIGIN',
    'JISE_ORIGIN',
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0147',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '구순을 감형해 외딴 섬에 정배하여 김명신 부처의 원한에 사죄하도록 명함',
    '구순',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '정조|구순|김명신',
    'ROYAL_ORDER',
    'PUNISHMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0148',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '이광섭',
    '구순과의 오래된 혐의를 막 씻은 뒤 곧 구순 편을 들었다고 판단',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '이광섭|구순',
    'FINAL_ROYAL_FINDING',
    'COMMANDER_GUSUN_RELATION',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0149',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '이광섭',
    '철퇴 네 개를 밤새 만들게 한 일을 과도한 조치로 비판',
    '철퇴 4개',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '이광섭',
    'FINAL_ROYAL_FINDING',
    'INVESTIGATION_CONDUCT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0150',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '이광섭',
    '아전들의 거짓을 살피지 않고 비장에게 맡겨 구순의 지시만 기다리는 듯 처리했다고 비판',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '이광섭|구순',
    'FINAL_ROYAL_FINDING',
    'INVESTIGATION_CONDUCT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0151',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '김명신 사망의 책임을 따지면 구순과 이광섭의 책임이 서로 크게 다르지 않다고 판단',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '구순|이광섭|김명신',
    'FINAL_ROYAL_FINDING',
    'RESPONSIBILITY_COMPARISON',
    'DEATH_RESPONSIBILITY',
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0152',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '정조',
    '도신 장계와 안핵어사 보고가 구순의 도난 여부에서 현격히 달랐다고 지적',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '이형원|홍대협|구순',
    'FINAL_ROYAL_FINDING',
    'REINVESTIGATION_DISAGREEMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0153',
    'SRC3_006',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '병영 비장 한가를 도백이 엄히 세 차례 형장 친 뒤 먼 섬의 종으로 보내도록 명함',
    '한가',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '한가',
    'ROYAL_ORDER',
    'PUNISHMENT',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_003',
    '처분문 표면형은 ''한가''. 한재욱과의 동일성은 이 행에서 확정하지 않음.'
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0154',
    'SRC3_007',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '이조원',
    '담당 이외 고을을 두루 살핀 것은 어사 사목에 어긋난다고 앞서 판단했음',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '이조원',
    'ROYAL_JUDGMENT',
    'INSPECTOR_SCOPE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_001',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0155',
    'SRC3_007',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_JUDGMENT',
    'JUDGMENT',
    '윤노동',
    '담당 외 지역을 자의로 조사하고 다른 어사 출도 지역까지 거듭 들어간 점 등을 사명 위반으로 판단',
    NULL,
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '윤노동',
    'ROYAL_JUDGMENT',
    'INSPECTOR_SCOPE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_001',
    NULL
);
INSERT INTO STG_AUDIT_PROPOSITIONS (PROP_ID, SOURCE_RECORD_ID, SOURCE_WORK, RECORD_LUNAR_DATE, REPORTING_ACTOR, ATTESTATION_MODE, PROPOSITION_TYPE, SUBJECT, PREDICATE, OBJECT_OR_CONTENT, OCCURRENCE_LUNAR_TEXT, OCCURRENCE_PRECISION, HISTORICAL_PLACE, PLACE_STATUS, NAMED_ENTITIES, EPISTEMIC_SCOPE, CLAIM_TOPIC, CONFLICT_GROUP, SET_STATUS, DIRECTNESS, SOURCE_URL, NOTES)
VALUES (
    'V3P0156',
    'SRC3_007',
    '조선왕조실록 정조실록',
    '1793-06-13',
    '정조',
    'ROYAL_ORDER',
    'ORDER',
    '정조',
    '윤노동을 파직하고 불서의 법을 시행하도록 명함',
    '윤노동',
    NULL,
    'UNKNOWN',
    NULL,
    'UNSPECIFIED',
    '정조|윤노동',
    'ROYAL_ORDER',
    'INSPECTOR_DISCIPLINE',
    NULL,
    'NOT_APPLICABLE',
    'DIRECT',
    'https://sillok.history.go.kr/id/kva_11706013_001',
    NULL
);

-- output/clean/episode_nodes.csv (41행)
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP01',
    'OBSERVED',
    'TESTIMONY',
    'RELATION',
    '구순–김명신 관계 변화',
    '명업은 김명신이 본래 구순과 친숙하여 날마다 왕래했다고 진술했고, 김명신이 박거사 일로 구순에게 편지를 보내 힐책했다고 진술했으며, 그 뒤 구순과 김명신의 왕래가 끊겼다고 진술했다.',
    '세 행 모두 명업 진술(NOT_INDEPENDENTLY_VERIFIED). 힐책은 2월 초순, 단절은 그 이후로 내부 순서를 보존한다. 힐책의 구체 내용(박거사 일)은 더 해석하지 않는다.',
    'CF001|CF002|CF003',
    NULL,
    'RECORDED_TESTIMONY',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0049|V3P0050|V3P0051',
    '명업',
    '1793-02 초순 이전 → 02 초순(힐책) → 02 초순 이후(단절)',
    '201',
    '210',
    '1793-06-13',
    '동일 진술자·동일 인물쌍·연속된 관계 변화 단계(사용자 예시와 동일).',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP02',
    'OBSERVED',
    'NESTED_TESTIMONY',
    'THEFT',
    '2월 22일 밤 도적 침입 전언',
    '명업은 나복이 2월 22일 밤 도적이 들었다고 자신에게 알렸다고 진술했다. 명업은 나복이 도적 30여 명, 횃불, 지세대감 자칭, 돈과 물품 도난을 말했다고 진술했다.',
    '30여 명·횃불·지세대감은 명업이 전한 나복 발언(중첩 진술)의 내용이며 객관적 사실로 확정하지 않음. episode 인식 수준은 구성원 중 가장 약한 RECORDED_NESTED_TESTIMONY로 둔다.',
    'CF004|CF005',
    NULL,
    'RECORDED_TESTIMONY|RECORDED_NESTED_TESTIMONY',
    'RECORDED_NESTED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0047|V3P0048',
    '명업(나복 발언 전달)',
    '1793-02-22 밤',
    '222',
    '222',
    '1793-06-13',
    '동일 시점·동일 전언(나복→명업)의 신고 사실과 신고 내용. 혼합 인식 수준은 floor로 처리.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP03',
    'OBSERVED',
    'TESTIMONY',
    'THEFT',
    '구순의 소장과 체포령',
    '명업은 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다.',
    '소장 접수 기관과 체포령 발령 주체는 이 행에 나타나지 않는다. 체포령과 2/28 병영 출동 사이 관계는 미기록(gap).',
    'CF006',
    NULL,
    'RECORDED_TESTIMONY',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0052',
    '명업',
    '도난 신고 이후',
    '222',
    NULL,
    '1793-06-13',
    '독립된 행정 행위(소장→체포령). 단독 episode.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP04',
    'OBSERVED',
    'TESTIMONY',
    'BARRACKS_OPERATION',
    '2월 28일 밤 병영 출동 준비',
    '이진욱은 2월 28일 밤 병영에서 자신을 비장청으로 불렀다고 진술했고, 한재욱이 자신과 조계완 등에게 덕평으로 가도록 지시했다고 진술했으며, 한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했고, 한재욱이 철편 네 개를 만들어 주었다고 진술했다.',
    '모두 이진욱 진술. ''조계완 등''은 열린 목록. 철편은 28일 밤~29일 새벽. 한재욱의 지시 위 상위 명령 출처는 기록되지 않음(gap). 정조 판단(CF044)의 ''철퇴 네 개''와 대응 여부는 ID07로 따로 관리한다.',
    'CF007|CF008|CF009|CF010',
    NULL,
    'RECORDED_TESTIMONY',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0055|V3P0056|V3P0057|V3P0058',
    '이진욱',
    '1793-02-28 밤 ~ 29 새벽',
    '228',
    '229',
    '1793-06-13',
    '동일 시점·동일 기관(병영 비장청)·동일 행위자 집단·동일 절차 단계(출동 준비).',
    'ID03:RESOLVED|ID07:UNRESOLVED|ID08:UNRESOLVED|ID11:RESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP05',
    'OBSERVED',
    'TESTIMONY',
    'BARRACKS_OPERATION',
    '2월 29일 덕평 체포 활동',
    '이진욱은 2월 29일 변지돌이 이미 공주진에서 잡혀간 상태였다고 진술했고, 장교 일행이 재돌의 처 자미덕을 붙잡았다고 진술했다.',
    '정원돌 체포 여부는 기록되지 않음. 변지돌을 공주진에서 잡아간 주체·경위는 미기록(gap).',
    'CF011|CF012',
    NULL,
    'RECORDED_TESTIMONY',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0060|V3P0061',
    '이진욱',
    '1793-02-29',
    '229',
    '229',
    '1793-06-13',
    '동일 날짜·동일 진술자·동일 출동의 현장 결과.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP06',
    'OBSERVED',
    'TESTIMONY',
    'BARRACKS_OPERATION',
    '자미덕의 병영 압송·신문·구류',
    '자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔다고 진술했고, 병영에서 도적 혐의로 한 차례 신문을 받았다고 진술했으며, 신문 뒤 비장청 다모방에 구류되었다고 진술했다.',
    '진술자가 자미덕으로 EP05(이진욱)와 다르므로 분리. 두 진술이 같은 체포를 가리키는지는 확정하지 않고 순서만 연결한다.',
    'CF013|CF014|CF015',
    NULL,
    'RECORDED_TESTIMONY',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0075|V3P0076|V3P0077',
    '자미덕',
    '자미덕 체포 뒤 → 신문 뒤',
    '229',
    NULL,
    '1793-06-13',
    '동일 진술자·연속 절차(압송→신문→구류).',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP07',
    'OBSERVED',
    'TESTIMONY',
    'BARRACKS_OPERATION',
    '한 비장의 석방 조건 제시와 대질 시 거짓 진술',
    '자미덕은 한 비장이 정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적이라고 말하면 자신과 남편을 다음 날 석방하겠다고 말했다고 진술했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술했다.',
    '''등''이 있으므로 명시된 5명은 닫힌 목록이 아님. 김명신은 명시 명단에 없으나 열린 목록이라 배제도 확정하지 않음. ''거짓으로 꾸며 말했다''는 거짓 지목으로 강화하지 않음(거짓말의 구체 내용 미특정). ''한 비장''=한재욱은 ID02로 사용자 확정(RESOLVED)이며, summary는 원문 표면형 ''한 비장''을 유지한다. 동일성 확정은 사주 주장이 사실이'
        || '라는 뜻이 아니다(EP12의 부인과 별개 진술로 유지).',
    'CF016|CF017',
    NULL,
    'RECORDED_TESTIMONY',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0080|V3P0082|V3P0083',
    '자미덕',
    '구류 중/그 후 → 대질 때',
    '229',
    NULL,
    '1793-06-13',
    '동일 진술자·동일 행위자(한 비장)·동일 절차 단계(구류 중 회유→대질).',
    'ID02:RESOLVED|ID11:RESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP08',
    'OBSERVED',
    'TESTIMONY',
    'SUSPECT_INFORMATION',
    '유제희의 현지 탐문과 구순 발언 기록',
    '유제희는 현지 탐문 중 구순이 풍각 김상제도 극히 수상하다고 말했고, 자신이 그 말을 원돌 등의 이름과 함께 기록해 올렸다고 진술했다.',
    '''극히 수상하다''는 범인 지목이 아님. 기록한 사람은 유제희 자신(정조 CF043의 ''구순이 성명을 적어 주었다''와 claim-level 차이). 탐문 시점·파견자·기록 수신자는 미기록(gap). 풍각 김상제=김명신은 ID05로 사용자 확정(RESOLVED, 표면형은 유지), 유제희=병영의 염탐 담당자는 ID06로 미확정. ''원돌 등''은 열린 목록이며 원돌'
        || '=정원돌은 ID11로 사용자 확정(RESOLVED, 표면형은 유지).',
    'CF020',
    NULL,
    'RECORDED_TESTIMONY',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0094|V3P0095|V3P0096',
    '유제희',
    '현지 탐문(날짜 미기록)',
    NULL,
    NULL,
    '1793-06-13',
    '독립된 정보 수집 행위. 날짜가 없어 다른 episode와 병합하지 않음.',
    'ID05:RESOLVED|ID06:UNRESOLVED|ID11:RESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP09',
    'OBSERVED',
    'TESTIMONY',
    'BARRACKS_OPERATION',
    '3월 4일 병사의 김생원 체포 지시',
    '이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했다고 진술했다. 해당 기사에서 풍각 김생원은 김명신, 흥덕 김생원은 김갑득으로 식별된다.',
    '공초 문장의 표면 주어는 ''병사''. 병사=이광섭은 ID01로 사용자 확정(RESOLVED)이지만 summary는 원문 표면형을 유지한다. 지시 행위 자체는 이진욱 진술로만 확인된다. 김생원 식별(CF022)은 사료의 직접 식별이므로 그대로 둔다.',
    'CF021|CF022',
    NULL,
    'RECORDED_TESTIMONY|DOCUMENTED_SOURCE_IDENTIFICATION',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED|DIRECTLY_DOCUMENTED_SOURCE_IDENTIFICATION',
    'SRC3_006',
    'V3P0065|V3P0066|V3P0067',
    '이진욱 / 기사 식별',
    '1793-03-04',
    '304',
    '304',
    '1793-06-13',
    '지시 행위와 지시 대상의 사료 식별은 같은 문장 단위로 묶는다. 실행(EP11)은 분리.',
    'ID01:RESOLVED|ID05:RESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP10',
    'OBSERVED',
    'TESTIMONY',
    'SUSPECT_INFORMATION',
    '3월 4일 조계완의 구순 집 방문과 서찰',
    '조계완은 김명신을 잡으러 가는 길에 구순 집에 들렀고, 구순이 이제 도적 다스리는 일이 바른 길을 얻었다는 취지로 말한 뒤 병사에게 전할 서찰 한 장을 건넸다고 진술했다.',
    '서찰의 전달 여부와 내용은 기록되지 않음(gap). 조계완이 3/4 ''장교 일행''의 일원인지는 ID08로 미확정.',
    'CF024',
    NULL,
    'RECORDED_TESTIMONY',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0069|V3P0072|V3P0073',
    '조계완',
    '1793-03-04 (체포 가는 길)',
    '304',
    '304',
    '1793-06-13',
    '진술자·행위(사적 접촉·서찰)가 체포 지시·체포 실행과 달라 분리.',
    'ID01:RESOLVED|ID08:UNRESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP11',
    'OBSERVED',
    'TESTIMONY',
    'BARRACKS_OPERATION',
    '3월 4일 김명신·김갑득 체포',
    '이진욱은 장교 일행이 병사의 분부에 따라 김명신과 김갑득을 잡아왔다고 진술했다.',
    '명령(EP09)과 실행을 분리 보존. 체포 뒤 구금 시작일을 이 행이 주장하지는 않는다.',
    'CF023',
    NULL,
    'RECORDED_TESTIMONY',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0068',
    '이진욱',
    '1793-03-04',
    '304',
    '304',
    '1793-06-13',
    '실행 단계. ORDER_TO_ACTION을 명시적으로 표현하려고 지시와 분리.',
    'ID01:RESOLVED|ID08:UNRESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP12',
    'OBSERVED',
    'TESTIMONY',
    'BARRACKS_OPERATION',
    '한재욱의 안핵 공초',
    '한재욱은 자미덕을 방으로 불러 남은 밥을 준 사실은 인정했지만, 자미덕을 은밀히 사주한 일은 없다고 진술했고, 구순과 평생 모르는 사이라고 진술했다.',
    '부인의 범위는 ''은밀히 사주''에 한정된다. ''어떤 형태의 사주도 없었다''로 넓히지 않는다. 진술 행위 시점은 안핵 공초.',
    'CF018|CF019',
    NULL,
    'RECORDED_TESTIMONY',
    'RECORDED_TESTIMONY',
    'NOT_INDEPENDENTLY_VERIFIED',
    'SRC3_006',
    'V3P0088|V3P0092|V3P0093',
    '한재욱',
    '안핵 공초(1793-05-28 차하 ~ 06-13 복명 사이)',
    '528',
    '613',
    '1793-06-13',
    '동일 진술자·동일 공초 자리의 자기 변호 진술.',
    'ID02:RESOLVED|ID03:RESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP13',
    'OBSERVED',
    'OFFICIAL_REPORT',
    'DETENTION_DEATH',
    '5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고',
    '이형원의 5월 12일 장계는 충청병영이 김명신을 달포 이상 구금·조사했으나 확실한 장물을 찾지 못했고, 김명신이 그 뒤 사망했다고 보고했으며, 무고한 평민들이 모진 형벌을 받았다고 보고했다.',
    '사망 장소·직접 사인은 이 보고에 없음. ''무고한 평민들''은 열린 집합이므로 김명신 포함 여부를 확정하지 않음. 구금 시작일(3/4)은 이 보고가 주장하지 않음.',
    'CF027|CF028',
    NULL,
    'DOCUMENTED_OFFICIAL_REPORT',
    'DOCUMENTED_OFFICIAL_REPORT',
    'FACT_OF_OFFICIAL_REPORT',
    'SRC3_001',
    'V3P0004|V3P0005|V3P0006|V3P0007',
    '이형원(충청도 관찰사)',
    '보고 1793-05-12 (구금·사망은 그 이전)',
    '512',
    '512',
    '1793-05-12',
    '동일 장계 안의 보고 사항(인식 수준 FACT_OF_OFFICIAL_REPORT 동일).',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP14',
    'OBSERVED',
    'OFFICIAL_EVALUATION',
    'COMMAND_RESPONSIBILITY',
    '5월 12일 이형원의 지휘 계통 평가',
    '5월 12일 기사에서 이광섭은 사건의 병사 지휘 책임자로 심리되며, 이형원은 이광섭이 허황한 말을 믿고 무고한 사람을 잘못 잡았다고 평가했고, 청주 영장 이문협이 수사를 병영 비장에게 전적으로 맡기고 방관했다고 평가했다.',
    '보고(EP13)와 인식 수준(OFFICIAL_EVALUATION)이 달라 분리. 이 행의 ''병사 지휘 책임자''는 5/12 기사 차원의 식별이다. 3/4 공초의 ''병사''=이광섭은 ID01로 사용자 확정(RESOLVED)이다. 이 행의 문구는 바꾸지 않는다.',
    'CF025|CF026',
    NULL,
    'DOCUMENTED_OFFICIAL_EVALUATION',
    'DOCUMENTED_OFFICIAL_EVALUATION',
    'FACT_OF_OFFICIAL_EVALUATION',
    'SRC3_001',
    'V3P0013|V3P0012',
    '이형원',
    '1793-05-12',
    '512',
    '512',
    '1793-05-12',
    '동일 평가자·동일 날짜·지휘 계통(병사·영장) 평가.',
    'ID01:RESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP15',
    'OBSERVED',
    'ROYAL_JUDGMENT',
    'THEFT_JUDGMENT',
    '5월 12일 정조 1차 판단: 도난 부재 방향',
    '정조는 당시 장계와 조사에 따라 도난 자체가 없었다는 방향을 받아들였다.',
    '6/13 최종 판단(EP25)에서 수정된다. 최종 판단으로 덮어쓰지 않고 REVISES로 보존한다.',
    'CF030',
    NULL,
    'DOCUMENTED_ROYAL_JUDGMENT',
    'DOCUMENTED_ROYAL_JUDGMENT',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_001',
    'V3P0016',
    '정조',
    '1793-05-12',
    '512',
    '512',
    '1793-05-12',
    'royal judgment. 같은 날의 royal order(EP16)와 분리.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP16',
    'OBSERVED',
    'ROYAL_ORDER',
    'REINVESTIGATION',
    '5월 12일 정조 명: 구순 의금부 구금·엄사',
    '정조는 구순을 의금부에 잡아 가두고 엄히 조사하도록 명했다.',
    '명령. 실행 경과(의금부 신문 결과)는 confirmed set에 없음.',
    'CF031',
    NULL,
    'DOCUMENTED_ROYAL_ORDER',
    'DOCUMENTED_ROYAL_ORDER',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_001',
    'V3P0017',
    '정조',
    '1793-05-12',
    '512',
    '512',
    '1793-05-12',
    'royal order 단독.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP17',
    'OBSERVED',
    'INSPECTOR_REPORT',
    'THEFT_JUDGMENT',
    '5월 27일 암행어사 이조원 보고: 도난 부재 방향',
    '이조원은 구순 사건을 도난이 없었다는 방향으로 보고했다.',
    '암행어사 보고. 6/13 판단과 claim-level로 충돌한다.',
    'CF032',
    NULL,
    'DOCUMENTED_INSPECTOR_REPORT',
    'DOCUMENTED_INSPECTOR_REPORT',
    'FACT_OF_OFFICIAL_REPORT',
    'SRC3_003',
    'V3P0031',
    '이조원(암행어사)',
    '1793-05-27',
    '527',
    '527',
    '1793-05-27',
    'inspector report 단독.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP18',
    'OBSERVED',
    'ROYAL_JUDGMENT_AND_ORDER',
    'REVIEW',
    '5월 27일 정조의 이조원 비판·파직',
    '정조는 이조원이 중대 사실을 직접 안핵하지 않고 전해 들은 말을 서계에 붙인 점을 문제 삼았고, 이조원을 파직하도록 명했다.',
    '판단과 명령이 한 행에 함께 있으나 주체(정조)·대상(이조원)·날짜가 같아 원문 그대로 유지.',
    'CF033',
    NULL,
    'DOCUMENTED_ROYAL_JUDGMENT_AND_ORDER',
    'DOCUMENTED_ROYAL_JUDGMENT_AND_ORDER',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_003',
    'V3P0032|V3P0029',
    '정조',
    '1793-05-27',
    '527',
    '527',
    '1793-05-27',
    '원문 행 단위 보존.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP19',
    'OBSERVED',
    'ROYAL_ORDER',
    'REINVESTIGATION',
    '5월 27일 정조 명: 구순 의금부 엄수·반복 신문',
    '정조는 구순을 의금부에 엄히 가두고 반복 신문하도록 명했다.',
    '5/12 명령(EP16)과 날짜·출처(SRC3_002)가 달라 별도 episode.',
    'CF034',
    NULL,
    'DOCUMENTED_ROYAL_ORDER',
    'DOCUMENTED_ROYAL_ORDER',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_002',
    'V3P0030',
    '정조',
    '1793-05-27',
    '527',
    '527',
    '1793-05-27',
    'royal order 단독.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP20',
    'OBSERVED',
    'ROYAL_ORDER',
    'REVIEW',
    '5월 28일 홍대협 공주 안핵어사 차하',
    '정조는 홍대협에게 사건을 자세히 조사해 오라고 명하고 그를 충청도 공주 안핵어사로 차하했다.',
    '5/27 이조원 비판과의 동기 연결은 사료에 명시되지 않음(gap).',
    'CF035',
    NULL,
    'DOCUMENTED_ROYAL_ORDER',
    'DOCUMENTED_ROYAL_ORDER',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_004',
    'V3P0036|V3P0037',
    '정조',
    '1793-05-28',
    '528',
    '528',
    '1793-05-28',
    'royal order 단독.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP21',
    'OBSERVED',
    'INSPECTOR_REPORT',
    'DETENTION_DEATH',
    '6월 11일 윤노동 별단',
    '윤노동의 6월 11일 별단은 김명신이 보수·구금 중 병들어 죽었고, 여러 죄수가 참혹한 형벌을 받았으며, 진정한 장물을 얻지 못했다고 보고했다.',
    '''여러 죄수''는 열린 집합. 김명신이 형벌을 받았다는 주장은 이 행에 없음.',
    'CF029',
    NULL,
    'DOCUMENTED_INSPECTOR_REPORT',
    'DOCUMENTED_INSPECTOR_REPORT',
    'FACT_OF_OFFICIAL_REPORT',
    'SRC3_005',
    'V3P0039|V3P0040|V3P0041',
    '윤노동(암행어사)',
    '보고 1793-06-11',
    '611',
    '611',
    '1793-06-11',
    'inspector report 단독.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP22',
    'OBSERVED',
    'COURT_ACTION',
    'REVIEW',
    '6월 11일 비변사 처리 보류 청·윤허',
    '비변사는 홍대협의 안핵 복명 전까지 윤노동 별단에 따른 처리를 보류할 것을 청했고, 정조는 이를 윤허했다.',
    '청과 윤허가 한 행. 같은 절차 단계이므로 유지.',
    'CF036',
    NULL,
    'DOCUMENTED_COURT_ACTION',
    'DOCUMENTED_COURT_ACTION',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_005',
    'V3P0043|V3P0044',
    '비변사·정조',
    '1793-06-11',
    '611',
    '611',
    '1793-06-11',
    'court action 단독.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP23',
    'OBSERVED',
    'OFFICIAL_ACTION',
    'REVIEW',
    '6월 13일 홍대협 공주목 신문·복명',
    '홍대협은 공주목에서 관련자들을 차례로 신문한 뒤 호서 안핵어사로 복명하여 편전에서 정조에게 보고했다.',
    'SRC3_006의 공초(EP01–EP12)는 이 신문을 통해 기록되었다.',
    'CF037',
    NULL,
    'DOCUMENTED_OFFICIAL_ACTION',
    'DOCUMENTED_OFFICIAL_ACTION',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_006',
    'V3P0045|V3P0130',
    '홍대협(안핵어사)',
    '신문(5/28 이후) → 복명 1793-06-13',
    '528',
    '613',
    '1793-06-13',
    'official action 단독.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP24',
    'OBSERVED',
    'OFFICIAL_FINDING',
    'THEFT_JUDGMENT',
    '홍대협 도난 판단: 약간의 실제 도난, 좀도둑 수준',
    '홍대협은 약간의 실제 도난은 있었지만 큰 화적 사건이 아니라 보통 좀도둑 수준이었다고 판단했다.',
    '''약간의''를 삭제하지 않음.',
    'CF038',
    NULL,
    'DOCUMENTED_OFFICIAL_FINDING',
    'DOCUMENTED_OFFICIAL_FINDING',
    'FACT_OF_OFFICIAL_FINDING',
    'SRC3_006',
    'V3P0097|V3P0098',
    '홍대협',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    'official finding. royal judgment(EP25)와 분리.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP25',
    'OBSERVED',
    'ROYAL_JUDGMENT',
    'THEFT_JUDGMENT',
    '정조 최종 도난 판단: 실재',
    '정조는 최종적으로 도난은 실제로 있었다고 판단했다.',
    '5/12 판단(EP15)을 지우지 않고 REVISES 관계로 보존.',
    'CF039',
    NULL,
    'DOCUMENTED_ROYAL_JUDGMENT',
    'DOCUMENTED_ROYAL_JUDGMENT',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_006',
    'V3P0104',
    '정조',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    'royal judgment 단독.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP26',
    'OBSERVED',
    'OFFICIAL_EVALUATION',
    'BIOLOGICAL',
    '홍대협 사인 평가: 질병',
    '홍대협은 김명신의 죽음을 질병 때문이라고 평가했다.',
    'CF040의 홍대협 절. 정조 절(EP27)과 판단 주체가 달라 분리.',
    'CF040',
    'CF040:홍대협은 김명신의 죽음을 질병 때문이라고 평가했고',
    'DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT',
    'DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT',
    'FACT_OF_OFFICIAL_JUDGMENT',
    'SRC3_006',
    'V3P0101|V3P0105',
    '홍대협',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    'official/royal 경계 분리(사용자 지정 branch A 구조).',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP27',
    'OBSERVED',
    'ROYAL_JUDGMENT',
    'BIOLOGICAL',
    '정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음',
    '정조는 김명신 부처가 전염병에 걸려 죽은 것으로 판단했고, 김명신이 곤장을 맞지 않았고 평범한 신문도 받지 않았다고 판단했다.',
    'royal judgment 자체로 보존. 5/12 장계의 ''구금·조사''와 긴장이 있다(CF041 notes). 판단 대상이 ''부처''(아내 포함)로 넓어진 점을 보존.',
    'CF040|CF041',
    'CF040:정조는 김명신 부처가 전염병에 걸려 죽은 것으로 판단했다.',
    'DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT|DOCUMENTED_ROYAL_JUDGMENT',
    'DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT',
    'FACT_OF_OFFICIAL_JUDGMENT|FACT_OF_ROYAL_JUDGMENT',
    'SRC3_006',
    'V3P0101|V3P0105|V3P0106',
    '정조',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    '동일 주체·동일 날짜·같은 생물학적/신체 처우 쟁점의 royal judgment.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP28',
    'OBSERVED',
    'ROYAL_JUDGMENT',
    'CAUSATION_BOUNDARY',
    '정조: 구순→김명신 직접 사망 인과 불확실',
    '정조는 김명신이 구순 때문에 직접 죽었다는 인과가 십분 확실하다고 할 수 없다고 판단했다.',
    '직접 인과에 대한 판단. 절차적 책임 판단(EP29)과 합치지 않는다.',
    'CF042',
    NULL,
    'DOCUMENTED_ROYAL_JUDGMENT',
    'DOCUMENTED_ROYAL_JUDGMENT',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_006',
    'V3P0141',
    '정조',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    'branch A/B 경계에 있는 판단이므로 단독.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP29',
    'OBSERVED',
    'ROYAL_JUDGMENT',
    'RESPONSIBILITY',
    '정조: 구순 책임 연결 판단',
    '정조는 구순이 김명신에게 사적인 감정을 품고 갈등을 일으켰고, 병영의 염탐 담당자에게 김명신의 성명을 적어 주었으며, 그 과정이 김명신이 횡액을 입고 원통하게 죽는 결과로 이어졌다고 책임을 연결해 판단했다.',
    '책임 귀속 사슬(royal judgment)이지 직접 사인이 아님. ''병영의 염탐 담당자''=유제희는 ID06로 미확정.',
    'CF043',
    NULL,
    'DOCUMENTED_ROYAL_JUDGMENT',
    'DOCUMENTED_ROYAL_JUDGMENT',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_006',
    'V3P0142|V3P0143|V3P0144',
    '정조',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    'royal judgment 단독.',
    'ID06:UNRESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP30',
    'OBSERVED',
    'ROYAL_JUDGMENT',
    'COMMAND_RESPONSIBILITY',
    '정조: 이광섭 책임 판단',
    '정조는 이광섭이 구순 편을 들고, 철퇴 네 개를 만들게 했으며, 아전들의 거짓을 제대로 살피지 않은 채 비장에게 일을 맡겼다고 비판하고, 김명신 사망 책임에서 구순과 이광섭의 책임이 크게 다르지 않다고 판단했다.',
    '''철퇴 네 개''와 이진욱 진술의 ''철편 네 개''(EP04) 대응은 ID07. ''비장''이 누구인지 특정하지 않음.',
    'CF044',
    NULL,
    'DOCUMENTED_ROYAL_JUDGMENT',
    'DOCUMENTED_ROYAL_JUDGMENT',
    'FACT_OF_ROYAL_JUDGMENT',
    'SRC3_006',
    'V3P0148|V3P0149|V3P0150|V3P0151',
    '정조',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    'royal judgment 단독.',
    'ID01:RESOLVED|ID07:UNRESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP31',
    'OBSERVED',
    'OFFICIAL_FINDING',
    'JISE',
    '홍대협: 지세 호칭 기원 미확정',
    '홍대협은 여러 차례 신문과 별도 탐문에도 지세 호칭의 기원을 확정하지 못했다.',
    'CF045의 홍대협 절.',
    'CF045',
    'CF045:홍대협은 여러 차례 신문과 별도 탐문에도 지세 호칭의 기원을 확정하지 못했고',
    'DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT',
    'DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT',
    'FACT_OF_OFFICIAL_JUDGMENT',
    'SRC3_006',
    'V3P0136|V3P0146',
    '홍대협',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    'official/royal 경계 분리.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP32',
    'OBSERVED',
    'ROYAL_JUDGMENT',
    'JISE',
    '정조: 구순 지세 호칭 날조 죄 불인정',
    '정조는 구순이 지세 호칭을 스스로 만들어냈다는 죄는 인정하지 않았다.',
    'CF045의 정조 절. ''불인정''을 ''구순은 지세와 무관''으로 강화하지 않음.',
    'CF045',
    'CF045:정조는 구순이 지세 호칭을 스스로 만들어냈다는 죄는 인정하지 않았다.',
    'DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT',
    'DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT',
    'FACT_OF_OFFICIAL_JUDGMENT',
    'SRC3_006',
    'V3P0136|V3P0146',
    '정조',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    'official/royal 경계 분리.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP33',
    'OBSERVED',
    'ROYAL_ORDER',
    'DISPOSITION',
    '구순 신지도 정배',
    '정조는 구순을 신지도에 정배했다.',
    NULL,
    'CF046',
    NULL,
    'DOCUMENTED_ROYAL_ORDER',
    'DOCUMENTED_ROYAL_ORDER',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_006',
    'V3P0110',
    '정조',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    '처분 대상별로 책임 연결이 달라 분리.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP34',
    'OBSERVED',
    'ROYAL_ORDER',
    'DISPOSITION',
    '이광섭 영동현 유배',
    '정조는 이광섭을 영동현에 유배했다.',
    NULL,
    'CF047',
    NULL,
    'DOCUMENTED_ROYAL_ORDER',
    'DOCUMENTED_ROYAL_ORDER',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_006',
    'V3P0111',
    '정조',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    '처분 대상별 분리.',
    'ID01:RESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP35',
    'OBSERVED',
    'ROYAL_ORDER',
    'DISPOSITION',
    '병영 비장 한가 처분',
    '정조는 병영 비장으로 표기된 한가를 도백이 엄히 세 차례 형장 친 뒤 먼 섬의 종으로 보내도록 명했다.',
    '처분문 표면형은 ''한가''. 한가=한재욱은 ID03으로 사용자 확정(RESOLVED)이며 summary는 표면형을 유지한다. 처분 근거가 된 행위는 confirmed set에 없음(gap G09).',
    'CF048',
    NULL,
    'DOCUMENTED_ROYAL_ORDER',
    'DOCUMENTED_ROYAL_ORDER',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_006',
    'V3P0153',
    '정조',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    '처분 대상별 분리.',
    'ID03:RESOLVED',
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP36',
    'OBSERVED',
    'ROYAL_ORDER',
    'DISPOSITION',
    '이형원 파직',
    '정조는 충청도 관찰사 이형원을 파직하도록 명했다.',
    '파직 사유는 confirmed set에 명시되지 않음.',
    'CF049',
    NULL,
    'DOCUMENTED_ROYAL_ORDER',
    'DOCUMENTED_ROYAL_ORDER',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_006',
    'V3P0113',
    '정조',
    '1793-06-13',
    '613',
    '613',
    '1793-06-13',
    '처분 대상별 분리.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'EP37',
    'OBSERVED',
    'ROYAL_ORDER',
    'DISPOSITION',
    '6월 16일 이형원 유임',
    '정조는 6월 16일 전 충청도 관찰사 이형원을 유임했다.',
    '6/13 파직과 별개의 인사 조치. 사유는 미기록(gap).',
    'CF050',
    NULL,
    'DOCUMENTED_ROYAL_ORDER',
    'DOCUMENTED_ROYAL_ORDER',
    'DIRECTLY_DOCUMENTED_OFFICIAL_ACTION',
    'SRC3_008',
    'V3P0114',
    '정조',
    '1793-06-16',
    '616',
    '616',
    '1793-06-16',
    '날짜가 달라 분리.',
    NULL,
    NULL
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'ENV01',
    'OBSERVED',
    'ENVIRONMENT',
    'ENVIRONMENT',
    '1793-01-22 호서 전염병 사망자 치계·구료 단속',
    '호서 도신이 전염병 사망자 수를 치계했고 정조가 구료를 각별히 단속하라고 명함',
    '김명신 개인 감염을 증명하지 않음.',
    NULL,
    NULL,
    'EXTERNAL_CONTEXT',
    'EXTERNAL_CONTEXT',
    NULL,
    NULL,
    NULL,
    '03_environment_1793',
    '1793-01-22',
    '122',
    '122',
    '1793-01-22',
    '환경 context node (사건 아님)',
    NULL,
    'E001'
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'ENV02',
    'OBSERVED',
    'ENVIRONMENT',
    'ENVIRONMENT',
    '1793-01-22 호서 기근 구휼 한창',
    '같은 기사에서 굶주림 구휼이 한창이라고 명시',
    '영양·행정 부담 맥락. 직접 사인으로 쓰지 않음.',
    NULL,
    NULL,
    'EXTERNAL_CONTEXT',
    'EXTERNAL_CONTEXT',
    NULL,
    NULL,
    NULL,
    '03_environment_1793',
    '1793-01-22',
    '122',
    '122',
    '1793-01-22',
    '환경 context node (사건 아님)',
    NULL,
    'E002'
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'ENV03',
    'OBSERVED',
    'ENVIRONMENT',
    'ENVIRONMENT',
    '1793-04-10 호서·영남 전염병 창궐(여제)',
    '정조실록 일별 목록에 ''호서 영남에 전염병이 창궐하므로 여제를 지내게 하다'' 기사 확인',
    '이번 단계에서는 기사 제목 수준 확인. 개별 감염 추론 금지.',
    NULL,
    NULL,
    'EXTERNAL_CONTEXT',
    'EXTERNAL_CONTEXT',
    NULL,
    NULL,
    NULL,
    '03_environment_1793',
    '1793-04-10',
    '410',
    '410',
    '1793-04-10',
    '환경 context node (사건 아님)',
    NULL,
    'E003'
);
INSERT INTO STG_EPISODE_NODES (NODE_ID, NODE_STATUS, LAYER, BRANCH, TITLE, SUMMARY, CAUTION, MEMBER_FACT_IDS, MEMBER_CLAUSES, CONFIRMATION_LEVELS, EPISTEMIC_FLOOR, CLAIM_STATUS, SOURCE_RECORD_IDS, SOURCE_PROP_IDS, ATTESTING_ACTOR, OCCURRENCE_TEXT, T_MIN, T_MAX, RECORD_LUNAR_DATE, GROUPING_RATIONALE, IDENTITY_LINKS, ENV_ID)
VALUES (
    'ENV04',
    'OBSERVED',
    'ENVIRONMENT',
    'ENVIRONMENT',
    '1793-05-12 경외 전염병 옥수 치료 명',
    '형조 판서 이득신 건의에 따라 서울·지방 전염병 옥수에게 약을 주어 치료하도록 명함',
    '구순 사건 기사와 같은 날의 독립 기사.',
    NULL,
    NULL,
    'EXTERNAL_CONTEXT',
    'EXTERNAL_CONTEXT',
    NULL,
    NULL,
    NULL,
    '03_environment_1793',
    '1793-05-12',
    '512',
    '512',
    '1793-05-12',
    '환경 context node (사건 아님)',
    NULL,
    'E004'
);

-- output/clean/observed_edges.csv (68행)
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE001',
    'EP01',
    'EP02',
    'TEMPORAL_BEFORE',
    'TEMPORAL',
    'DERIVED',
    'True',
    NULL,
    'CF002|CF004',
    '명업 진술상 힐책(2월 초순)이 2월 22일 밤 도적 전언보다 앞선다.',
    '시간 선후일 뿐 원인 관계가 아님.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE002',
    'EP02',
    'EP03',
    'TEMPORAL_BEFORE',
    'TEMPORAL',
    'DERIVED',
    'True',
    NULL,
    'CF004|CF006',
    'CF006 chronology ''도난 신고 이후''.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE003',
    'EP02',
    'EP04',
    'TEMPORAL_BEFORE',
    'TEMPORAL',
    'DERIVED',
    'True',
    NULL,
    'CF004|CF007',
    '2/22 밤 → 2/28 밤 (서로 다른 진술자의 명시 날짜).',
    '소장·체포령(EP03)과 2/28 출동 사이 연결은 미기록 → G01.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE004',
    'EP04',
    'EP05',
    'ORDER_TO_ACTION',
    'SOURCE_DIRECT|TEMPORAL',
    'DERIVED',
    'True',
    NULL,
    'CF008|CF011|CF012',
    '같은 이진욱 진술 흐름에서 덕평 출동 지시(2/28) 뒤 2/29 장교 일행의 현장 체포 활동이 이어진다.',
    '실행이 확인되는 것은 출동 부분뿐이다. 변지돌·정원돌 체포 지시는 실행되지 않음(변지돌 기체포, 정원돌 미기록). 체포 대상이 자미덕으로 바뀐 경위는 기록되지 않았다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE005',
    'EP05',
    'EP06',
    'PROCEDURAL_NEXT',
    'TEMPORAL',
    'DERIVED',
    'True',
    NULL,
    'CF012|CF013',
    'CF013 chronology ''자미덕 체포 뒤'': 병영 압송·신문·구류.',
    '두 진술(이진욱·자미덕)이 같은 체포 장면을 가리키는지는 확정하지 않는다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE006',
    'EP06',
    'EP07',
    'PROCEDURAL_NEXT',
    'TEMPORAL',
    'DERIVED',
    'True',
    NULL,
    'CF015|CF016|CF017',
    'CF016 chronology ''구류 중/그 후'', CF017 ''대질 때''.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE007',
    'EP07',
    'EP12',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    'SOURCE_DIRECT',
    'DERIVED',
    'True',
    NULL,
    'CF017|CF018',
    '자미덕: 한 비장의 지휘에 따라 거짓으로 꾸며 말함 ↔ 한재욱: 자미덕을 은밀히 사주한 일 없음.',
    '''한 비장''=한재욱은 ID02 사용자 확정(RESOLVED)이라 같은 인물에 대한 두 진술이다. 사주 주장(자미덕)과 은밀한 사주 부인(한재욱)은 서로 다른 진술로 유지하며 어느 쪽도 객관적 사실로 확정하지 않는다. 한재욱의 부인 범위는 ''은밀한 사주''에 한정되므로 PARTIAL 충돌이다.',
    'PARTIAL_CONFLICT',
    '사용자 검토: 정면 충돌로 승격하지 않음. 자미덕의 ''지휘'' 주장과 한재욱의 ''은밀한 사주'' 부인은 범위가 완전히 같지 않다.'
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE008',
    'EP09',
    'EP11',
    'ORDER_TO_ACTION',
    'SOURCE_DIRECT',
    'OBSERVED',
    'True',
    NULL,
    'CF021|CF023',
    'CF023 ''병사의 분부에 따라'' — 지시와 실행의 연결이 원문에 있다.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE009',
    'EP09',
    'EP10',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT|TEMPORAL',
    'DERIVED',
    'True',
    NULL,
    'CF021|CF024',
    '조계완은 ''김명신을 잡으러 가는 길에'' 구순 집에 들렀다. 체포 임무가 먼저 주어져 있었음을 전제로 한다.',
    '조계완이 3/4 장교 일행의 일원인지는 ID08로 미확정.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE010',
    'EP10',
    'EP11',
    'TEMPORAL_BEFORE',
    'SOURCE_DIRECT',
    'DERIVED',
    'True',
    'ID08',
    'CF024|CF023',
    '''잡으러 가는 길에'' → 방문이 체포보다 앞선다.',
    NULL,
    'CONDITIONAL_UNRESOLVED_IDENTITY',
    'ID08 KEEP_UNRESOLVED (사용자 수동 검토: 추가 사료 없이 확정하지 않고 현재 불확실성 유지)'
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE011',
    'EP11',
    'EP13',
    'PROCEDURAL_NEXT',
    'PROCEDURAL',
    'DERIVED',
    'False',
    NULL,
    'CF023|CF027',
    '3/4 체포된 김명신 → 충청병영의 달포 이상 구금·조사 → 사망(5/12 보고).',
    'CF027은 구금 시작일을 3/4로 주장하지 않는다. 같은 사람에 대한 체포→구금 절차 순서만 연결한다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE020',
    'EP01',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF001|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE021',
    'EP02',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF004|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE022',
    'EP03',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF006|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE023',
    'EP04',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF007|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE024',
    'EP05',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF011|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE025',
    'EP06',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF013|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE026',
    'EP07',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF016|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE027',
    'EP08',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF020|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE028',
    'EP09',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF021|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE029',
    'EP10',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF024|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE030',
    'EP11',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF023|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE031',
    'EP12',
    'EP23',
    'INFORMATION_FLOW',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF018|CF037',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.',
    '진술 내용의 진위가 아니라 ''진술이 안핵 기록에 들어갔다''는 정보 흐름이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE013',
    'EP02',
    'EP24',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    'SOURCE_DIRECT',
    'DERIVED',
    'True',
    NULL,
    'CF005|CF038',
    '중첩 진술의 ''도적 30여 명·횃불'' ↔ 홍대협 ''큰 화적 사건이 아니라 보통 좀도둑 수준''.',
    '도난 존재 자체는 두 쪽 모두 인정한다. 충돌은 규모에 관한 것이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE040',
    'EP13',
    'EP15',
    'REVIEW_OF',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    'ID09',
    'CF027|CF030',
    'CF030 ''당시 장계와 조사에 따라'' 도난 부재 방향을 받아들임.',
    'CF027 자체는 ''확실한 장물 없음''만 보고하고 ''도난 없음''을 직접 주장하지는 않는다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE041',
    'EP15',
    'EP16',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT|TEMPORAL',
    'DERIVED',
    'False',
    NULL,
    'CF030|CF031',
    '같은 날 같은 기사(SRC3_001)의 판단 뒤 명령.',
    '판단이 명령의 사유라는 문장은 confirmed set에 없다. 절차 순서만 연결한다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE042',
    'EP16',
    'EP19',
    'TEMPORAL_BEFORE',
    'TEMPORAL',
    'DERIVED',
    'False',
    NULL,
    'CF031|CF034',
    '5/12 의금부 구금 명 → 5/27 의금부 엄수·반복 신문 명.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE043',
    'EP17',
    'EP18',
    'REVIEW_OF',
    'SOURCE_DIRECT',
    'OBSERVED',
    'False',
    NULL,
    'CF032|CF033',
    'CF033: 정조가 이조원 서계의 조사 방식을 문제 삼음.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE044',
    'EP17',
    'EP19',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF032|CF034',
    'CF034 출처 SRC3_002 제목 ''이조원이 구순 사건을 아뢰고 엄핵을 청함''.',
    'CF032(SRC3_003)와 CF034(SRC3_002)는 같은 날 다른 기록이다. 기록을 병합하지 않는다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE045',
    'EP18',
    'EP20',
    'TEMPORAL_BEFORE',
    'TEMPORAL',
    'DERIVED',
    'False',
    NULL,
    'CF033|CF035',
    '5/27 이조원 비판 → 5/28 홍대협 차하.',
    '동기 연결은 사료에 없음 → G08.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE046',
    'EP20',
    'EP23',
    'ORDER_TO_ACTION',
    'SOURCE_DIRECT|PROCEDURAL',
    'DERIVED',
    'False',
    NULL,
    'CF035|CF037',
    '''사건을 자세히 조사해 오라''·안핵어사 차하 → 공주목 신문·안핵어사 복명(같은 인물, 같은 직함).',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE047',
    'EP21',
    'EP22',
    'REVIEW_OF',
    'SOURCE_DIRECT',
    'OBSERVED',
    'False',
    NULL,
    'CF029|CF036',
    'CF036: 윤노동 별단에 따른 처리 보류.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE048',
    'EP22',
    'EP23',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT',
    'OBSERVED',
    'False',
    NULL,
    'CF036|CF037',
    'CF036 ''홍대협의 안핵 복명 전까지'' 보류 → 복명.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE050',
    'EP23',
    'EP24',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF037|CF038',
    '복명 속 도난 판단.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE051',
    'EP23',
    'EP26',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF037|CF040',
    '복명 속 사인 평가.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE052',
    'EP23',
    'EP31',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF037|CF045',
    '복명 속 지세 호칭 조사 결과.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE053',
    'EP15',
    'EP24',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF030|CF038',
    '5/12 ''도난 자체가 없었다는 방향'' ↔ 6/13 홍대협 ''약간의 실제 도난''.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE054',
    'EP17',
    'EP24',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF032|CF038',
    '5/27 이조원 ''도난이 없었다는 방향'' ↔ 6/13 홍대협 ''약간의 실제 도난''.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE055',
    'EP24',
    'EP25',
    'REVIEW_OF',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF038|CF039',
    '같은 복명 기사에서 정조가 안핵 판단을 검토해 최종 판단.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE056',
    'EP15',
    'EP25',
    'REVISES',
    'SOURCE_DIRECT|TEMPORAL',
    'DERIVED',
    'False',
    NULL,
    'CF030|CF039',
    '같은 주체(정조)의 도난 판단: 5/12 부재 방향 → 6/13 실재.',
    '최종 판단만 남기지 않는다. 두 판단 node를 모두 유지한다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE060',
    'EP13',
    'EP26',
    'REVIEW_OF',
    'PROCEDURAL',
    'DERIVED',
    'False',
    NULL,
    'CF027|CF035|CF040',
    '5/12 장계는 사인 없이 사망만 보고 → 안핵어사(사건 자세히 조사 명)가 사인을 질병으로 평가.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE061',
    'EP26',
    'EP27',
    'REVIEW_OF',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF040',
    '홍대협 ''질병'' → 정조 ''부처가 전염병''. 대상이 부처로, 병명이 전염병으로 구체화된다.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE062',
    'EP13',
    'EP27',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF027|CF041',
    '5/12 장계 ''구금·조사'' ↔ 6/13 정조 ''평범한 신문도 받지 않았다''.',
    'PARTIAL_TENSION: ''조사''가 곧 ''신문''이라고 확정할 수 없다. CF028의 ''무고한 평민들 모진 형벌''은 김명신 포함 여부가 열린 집합이므로 충돌 근거로 쓰지 않는다.',
    'UNRESOLVED_SCOPE',
    '사용자 검토: 5월 장계의 ''조사''와 정조의 ''평범한 신문''이 같은 범위인지 확정하지 않음. 부분 긴장 유지.'
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE063',
    'EP27',
    'EP28',
    'CONTEXT_SUPPORTS',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF040|CF041|CF042',
    '같은 날 정조 판단 안에서 전염병 사망·무장형 판단과 ''직접 인과 불확실'' 판단이 함께 놓인다.',
    '앞 판단이 뒤 판단의 사유라는 문장은 confirmed set에 없다. 양립·맥락 관계로만 둔다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE070',
    'EP01',
    'EP29',
    'RESPONSIBILITY_LINK',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF043|CF002|CF003',
    '정조 판단 ''사적인 감정을 품고 갈등을 일으켰고'' ↔ 명업 진술의 힐책·왕래 단절.',
    'CF043은 박거사 일을 직접 언급하지 않는다. 판단 속 ''갈등''을 EP01과 대응시킨 것은 DERIVED다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE071',
    'EP08',
    'EP29',
    'RESPONSIBILITY_LINK',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    'ID06',
    'CF043|CF020',
    '정조 판단 ''병영의 염탐 담당자에게 김명신의 성명을 적어 주었으며'' ↔ 유제희 진술.',
    '풍각 김상제=김명신은 ID05 사용자 확정(RESOLVED). 염탐 담당자=유제희(ID06)는 미확정이라 condition으로 남긴다. claim-level 차이: 정조는 ''구순이 적어 주었다'', 유제희는 ''구순이 말했고 자신이 기록했다''. 두 행위를 합치지 않는다.',
    'CONDITIONAL_UNRESOLVED_IDENTITY',
    'ID06 KEEP_UNRESOLVED (사용자 수동 검토: 추가 사료 없이 확정하지 않고 현재 불확실성 유지)'
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE072',
    'EP11',
    'EP29',
    'RESPONSIBILITY_LINK',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF043|CF023',
    '정조 판단의 ''횡액'' ↔ 3/4 체포.',
    '''횡액''을 체포·구금과 대응시킨 것은 해석이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE073',
    'EP13',
    'EP29',
    'RESPONSIBILITY_LINK',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF043|CF027',
    '정조 판단의 ''원통하게 죽는 결과'' ↔ 구금 뒤 사망 보고.',
    '책임 귀속이며 직접 사인 주장이 아니다(EP28 참조).',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE074',
    'EP29',
    'EP33',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF043|CF046',
    '같은 기사에서 책임 판단 뒤 정배 처분.',
    '처분 사유 문장(V3P0147)은 confirmed set 밖이다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE080',
    'EP04',
    'EP30',
    'RESPONSIBILITY_LINK',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    'ID07',
    'CF010|CF044',
    '정조 비판 ''철퇴 네 개를 만들게 했으며'' ↔ 이진욱 진술 ''한재욱이 철편 네 개를 만들어 주었다''.',
    '행위 층위 차이(제작 지시 vs 제작·지급). 모순으로도 동일 행위로도 확정하지 않는다.',
    'CONDITIONAL_UNRESOLVED_IDENTITY',
    'ID07 KEEP_UNRESOLVED (사용자 수동 검토: 추가 사료 없이 확정하지 않고 현재 불확실성 유지)'
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE081',
    'EP09',
    'EP30',
    'RESPONSIBILITY_LINK',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF021|CF044',
    '3/4 ''병사''의 체포 지시 ↔ 정조의 이광섭 지휘 책임 판단.',
    '병사=이광섭은 ID01 사용자 확정(RESOLVED)이라 직접 대응한다. 다만 3/4 지시 행위 자체는 이진욱 진술(CF021)로만 확인되며, 동일성 확정이 그 행위를 관측 사실로 올리지는 않는다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE082',
    'EP14',
    'EP30',
    'REVIEW_OF',
    'PROCEDURAL',
    'DERIVED',
    'False',
    NULL,
    'CF025|CF026|CF044',
    '5/12 이형원의 이광섭·이문협 평가 → 6/13 정조의 이광섭 책임 재평가.',
    '''비장에게 맡김''은 5/12에는 이문협, 6/13에는 이광섭에 대한 비판으로 나온다. 주체를 합치지 않는다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE083',
    'EP29',
    'EP30',
    'RESPONSIBILITY_LINK',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF043|CF044',
    'CF044 ''구순과 이광섭의 책임이 크게 다르지 않다'' — 두 책임 판단의 비교.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE084',
    'EP30',
    'EP34',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF044|CF047',
    '책임 판단 뒤 유배 처분.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE090',
    'EP02',
    'EP31',
    'REVIEW_OF',
    'SOURCE_DIRECT',
    'DERIVED',
    'True',
    NULL,
    'CF005|CF045',
    '중첩 진술의 ''지세대감 자칭'' → 홍대협 기원 미확정.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE091',
    'EP31',
    'EP32',
    'REVIEW_OF',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF045',
    '홍대협 미확정 → 정조의 날조 죄 불인정.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE095',
    'EP23',
    'EP35',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF037|CF048',
    '안핵 복명 뒤 처분.',
    '한가 처분의 근거 행위는 미기록 → G09.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE096',
    'EP23',
    'EP36',
    'PROCEDURAL_NEXT',
    'SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF037|CF049',
    '안핵 복명 뒤 처분.',
    '파직 사유는 미기록.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE097',
    'EP36',
    'EP37',
    'REVISES',
    'TEMPORAL|SOURCE_DIRECT',
    'DERIVED',
    'False',
    NULL,
    'CF049|CF050',
    '6/13 파직 → 6/16 유임(같은 인물의 관직 상태 변경).',
    '사유 미기록 → G10. 6/13 처분 자체를 지우지 않는다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE098',
    'EP25',
    'EP36',
    'TEMPORAL_BEFORE',
    'TEMPORAL',
    'DERIVED',
    'False',
    NULL,
    'CF039|CF049',
    '같은 날 최종 도난 판단과 이형원 파직.',
    '최종 판단(도난 실재)이 5/12 장계와 어긋난다는 점이 파직 사유인지는 confirmed set에 없다 → G10.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE100',
    'ENV01',
    'EP26',
    'CONTEXT_SUPPORTS',
    'ENVIRONMENTAL_CONTEXT',
    'DERIVED',
    'False',
    NULL,
    'E001|CF040',
    '1월 호서 전염병 사망 치계 — 질병 사망 평가와 시대적으로 부합.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE101',
    'ENV03',
    'EP26',
    'CONTEXT_SUPPORTS',
    'ENVIRONMENTAL_CONTEXT',
    'DERIVED',
    'False',
    NULL,
    'E003|CF040',
    '4월 호서 전염병 창궐 — 구금(3/4~)·사망(5/12 이전) 기간과 겹치는 지역 환경.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE102',
    'ENV01',
    'EP27',
    'CONTEXT_SUPPORTS',
    'ENVIRONMENTAL_CONTEXT',
    'DERIVED',
    'False',
    NULL,
    'E001|CF040',
    '정조의 ''부처 전염병 사망'' 판단과 부합하는 지역 환경.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE103',
    'ENV03',
    'EP27',
    'CONTEXT_SUPPORTS',
    'ENVIRONMENTAL_CONTEXT',
    'DERIVED',
    'False',
    NULL,
    'E003|CF040',
    '전염병 지속 — 정조 판단과 부합.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE104',
    'ENV04',
    'EP27',
    'CONTEXT_SUPPORTS',
    'ENVIRONMENTAL_CONTEXT',
    'DERIVED',
    'False',
    NULL,
    'E004|CF040',
    '5/12 옥수 전염병 치료 정책 — 옥중 전염병이 조정의 현안이었다는 custody-health context.',
    '정책일(5/12)은 김명신 사망 보고와 같은 날이고 사망 이후다. 김명신 처우에 영향을 준 것으로 연결하지 않는다.',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE105',
    'ENV02',
    'EP27',
    'CONTEXT_SUPPORTS',
    'ENVIRONMENTAL_CONTEXT',
    'DERIVED',
    'False',
    NULL,
    'E002|CF040',
    '기근·구휼 — 영양·행정 부담이라는 거시 맥락(약함).',
    '직접 사인으로 쓰지 않는다(E002 notes).',
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE106',
    'ENV01',
    'EP21',
    'CONTEXT_SUPPORTS',
    'ENVIRONMENTAL_CONTEXT',
    'DERIVED',
    'False',
    NULL,
    'E001|CF029',
    '윤노동 별단 ''보수·구금 중 병들어 죽었다''는 보고와 부합하는 환경.',
    NULL,
    NULL,
    NULL
);
INSERT INTO STG_OBSERVED_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, BASIS, STATUS, CLAIM_LEVEL, CONDITION, SUPPORTING, RATIONALE, CAUTION, UNCERTAINTY_STATUS, REVIEW_DECISION)
VALUES (
    'OE107',
    'ENV03',
    'EP21',
    'CONTEXT_SUPPORTS',
    'ENVIRONMENTAL_CONTEXT',
    'DERIVED',
    'False',
    NULL,
    'E003|CF029',
    '윤노동 보고와 부합하는 전염병 지속 환경.',
    NULL,
    NULL,
    NULL
);

-- output/clean/node_feature_links.csv (57행)
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL001',
    'NODE',
    'EP03',
    'INSTITUTIONAL',
    'F010',
    'jurisdictionally_possible',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '도적 사건에 진영장·수령 겸임 토포사가 개입할 수 있다. 소장 접수 기관은 미기록이다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL002',
    'NODE',
    'EP03',
    'INSTITUTIONAL',
    'F005',
    'procedure_available',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '군현 수령 경로도 제도상 가능하다. 실제 경로는 미확정.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL003',
    'NODE',
    'EP04',
    'INSTITUTIONAL',
    'F007',
    'role_compatible',
    'COMPATIBLE',
    'NO',
    '병마절도사 지휘 아래 병영 장교 출동은 제도상 가능하다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL004',
    'NODE',
    'EP04',
    'INSTITUTIONAL',
    'F008',
    'procedure_available',
    'COMPATIBLE',
    'NO',
    '병영 내부 명령·집행 경로가 존재한다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL005',
    'NODE',
    'EP04',
    'INSTITUTIONAL',
    'F009',
    'role_compatible',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '비장청 호출과 비장의 실무 지휘는 막료 관행과 부합한다. 한재욱의 직함은 이 episode에 명시되어 있지 않다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL006',
    'NODE',
    'EP04',
    'INSTITUTIONAL',
    'F002',
    'legal_available',
    'UNDETERMINED',
    'NO',
    '흠휼전칙은 형구 규격을 정하지만, pack에는 철편의 지위를 판정할 정보가 없다. 정조는 철퇴를 과도하다고 비판했다(CF044).'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL007',
    'NODE',
    'EP05',
    'INSTITUTIONAL',
    'F010',
    'jurisdictionally_possible',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '공주진의 변지돌 체포는 진·토포 경로와 양립한다. 경위는 미기록이다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL008',
    'NODE',
    'EP06',
    'INSTITUTIONAL',
    'F004',
    'legal_available',
    'UNDETERMINED',
    'NO',
    '구금 도구 기준은 있으나 자미덕의 구류 방식(다모방) 판정 자료가 없다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL009',
    'NODE',
    'EP06',
    'INSTITUTIONAL',
    'F009',
    'role_compatible',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '비장청 공간 사용은 막료 실무와 부합한다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL010',
    'NODE',
    'EP07',
    'INSTITUTIONAL',
    'F002',
    'legal_available',
    'LOW',
    'NO',
    '석방을 조건으로 특정 진술을 요구하는 것을 허용하는 제도 피쳐는 pack에 없다. 주장된 행위의 합법성은 낮다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL011',
    'NODE',
    'EP07',
    'INSTITUTIONAL',
    'F009',
    'role_compatible',
    'COMPATIBLE',
    'NO',
    '비장이 구류자를 다루는 실무 위치에 있을 수 있다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL012',
    'NODE',
    'EP08',
    'INSTITUTIONAL',
    'F008',
    'role_compatible',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '병영 소속 인원의 탐문은 병영 체계와 양립한다. 유제희의 직함은 confirmed set에 없다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL013',
    'NODE',
    'EP08',
    'INSTITUTIONAL',
    'F020',
    'information_flow_compatible',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '''기록해 올렸다''는 상향 문서 보고 구조와 부합한다. 수신자는 미기록이다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL014',
    'NODE',
    'EP09',
    'INSTITUTIONAL',
    'F007',
    'role_compatible',
    'COMPATIBLE',
    'NO',
    '병사(兵使)가 장교에게 체포를 지시하는 것은 도 단위 군사지휘와 양립한다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL015',
    'NODE',
    'EP09',
    'INSTITUTIONAL',
    'F010',
    'jurisdictionally_possible',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '도적 사건 체포 관할과 양립한다. 양반(생원) 체포의 특별 요건은 pack에 없다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL016',
    'NODE',
    'EP10',
    'INSTITUTIONAL',
    'F020',
    'information_flow_compatible',
    'LOW',
    'NO',
    '구순(전 부사)→병사 서찰은 공식 보고 경로(장계·서계)가 아니다. 공식 지휘 명령으로서는 LOW이고, 사적 정보 전달로서만 가능하다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL017',
    'NODE',
    'EP10',
    'INSTITUTIONAL',
    'F007',
    'role_compatible',
    'LOW',
    'NO',
    '구순에게 병영 장교를 지휘할 공식 권한은 확인되지 않는다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL018',
    'NODE',
    'EP11',
    'INSTITUTIONAL',
    'F008',
    'procedure_available',
    'COMPATIBLE',
    'NO',
    '병사 분부에 따른 장교 일행의 체포 집행 경로가 존재한다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL019',
    'NODE',
    'EP12',
    'INSTITUTIONAL',
    'F014',
    'review_available',
    'COMPATIBLE',
    'NO',
    '안핵어사 공초는 독립 재조사 경로다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL020',
    'NODE',
    'EP13',
    'INSTITUTIONAL',
    'F006',
    'information_flow_compatible',
    'COMPATIBLE',
    'NO',
    '관찰사 장계는 중앙 직계 보고 경로다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL021',
    'NODE',
    'EP13',
    'INSTITUTIONAL',
    'F020',
    'information_flow_compatible',
    'COMPATIBLE',
    'NO',
    '장계 문서 보고 구조.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL022',
    'NODE',
    'EP14',
    'INSTITUTIONAL',
    'F006',
    'review_available',
    'COMPATIBLE',
    'NO',
    '관찰사의 하급 기관 감독·평가 경로.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL023',
    'NODE',
    'EP15',
    'INSTITUTIONAL',
    'F018',
    'legal_available',
    'COMPATIBLE',
    'NO',
    '국왕의 사건별 판단·명령.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL024',
    'NODE',
    'EP16',
    'INSTITUTIONAL',
    'F012',
    'procedure_available',
    'COMPATIBLE',
    'NO',
    '의금부의 왕명 기반 구금·신문.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL025',
    'NODE',
    'EP17',
    'INSTITUTIONAL',
    'F013',
    'review_available',
    'COMPATIBLE',
    'NO',
    '암행어사의 지방 탐문 보고.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL026',
    'NODE',
    'EP18',
    'INSTITUTIONAL',
    'F013',
    'review_available',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '어사 보고에 대한 국왕의 검토·징계. 사목 범위는 사건별 확인이 필요하다(F013 notes).'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL027',
    'NODE',
    'EP19',
    'INSTITUTIONAL',
    'F012',
    'procedure_available',
    'COMPATIBLE',
    'NO',
    '의금부 반복 신문.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL028',
    'NODE',
    'EP20',
    'INSTITUTIONAL',
    'F014',
    'review_available',
    'COMPATIBLE',
    'NO',
    '안핵어사 차하는 정조대 실제 운용 사례가 있다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL029',
    'NODE',
    'EP21',
    'INSTITUTIONAL',
    'F013',
    'review_available',
    'COMPATIBLE',
    'NO',
    '암행어사 별단.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL030',
    'NODE',
    'EP22',
    'INSTITUTIONAL',
    'F017',
    'review_available',
    'COMPATIBLE',
    'NO',
    '비변사의 처분 보류 심의.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL031',
    'NODE',
    'EP23',
    'INSTITUTIONAL',
    'F014',
    'review_available',
    'COMPATIBLE',
    'NO',
    '안핵 복명.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL032',
    'NODE',
    'EP23',
    'INSTITUTIONAL',
    'F020',
    'information_flow_compatible',
    'COMPATIBLE',
    'NO',
    '복명·서계 구조.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL033',
    'NODE',
    'EP26',
    'INSTITUTIONAL',
    'F015',
    'procedure_available',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '사인 판단에는 초검·복검 구조가 있다. 실제 검험 시행 여부는 confirmed set에 없다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL034',
    'NODE',
    'EP26',
    'INSTITUTIONAL',
    'F016',
    'procedure_available',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '1792 증수무원록 지침이 같은 시기에 존재한다. 적용 여부는 미기록이다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL035',
    'NODE',
    'EP27',
    'INSTITUTIONAL',
    'F002',
    'legal_available',
    'COMPATIBLE',
    'NO',
    '곤장·신문 여부 판단은 흠휼전칙의 형구 사용 제한과 같은 차원의 쟁점이다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL036',
    'NODE',
    'EP27',
    'INSTITUTIONAL',
    'F003',
    'legal_available',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '군문 중곤 제한(사형죄 한정). 김명신에 대한 형구 사용은 정조가 부정했다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL037',
    'NODE',
    'EP29',
    'INSTITUTIONAL',
    'F018',
    'legal_available',
    'COMPATIBLE',
    'NO',
    '국왕의 책임 판단.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL038',
    'NODE',
    'EP30',
    'INSTITUTIONAL',
    'F007',
    'role_compatible',
    'COMPATIBLE',
    'NO',
    '병마절도사 지휘 책임 귀속은 지휘체계와 부합한다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL039',
    'NODE',
    'EP30',
    'INSTITUTIONAL',
    'F009',
    'role_compatible',
    'COMPATIBLE',
    'NO',
    '비장에게 일을 맡긴 것에 대한 비판은 막료 체계를 전제한다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL040',
    'NODE',
    'EP33',
    'INSTITUTIONAL',
    'F001',
    'legal_available',
    'COMPATIBLE',
    'NO',
    '정배는 법전상 형벌 체계 안에 있다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL041',
    'NODE',
    'EP34',
    'INSTITUTIONAL',
    'F001',
    'legal_available',
    'COMPATIBLE',
    'NO',
    '유배.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL042',
    'NODE',
    'EP35',
    'INSTITUTIONAL',
    'F006',
    'jurisdictionally_possible',
    'COMPATIBLE',
    'NO',
    '도백(관찰사)이 형장을 집행하도록 한 명은 관찰사 관할과 부합한다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL043',
    'NODE',
    'EP35',
    'INSTITUTIONAL',
    'F002',
    'legal_available',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '형장 세 차례는 형정 규범 안에서 판단할 사항이다. 규격 정보는 pack에 없다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL044',
    'NODE',
    'EP36',
    'INSTITUTIONAL',
    'F018',
    'legal_available',
    'COMPATIBLE',
    'NO',
    '국왕의 파직 명.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL045',
    'NODE',
    'EP37',
    'INSTITUTIONAL',
    'F018',
    'legal_available',
    'COMPATIBLE',
    'NO',
    '국왕의 인사 명.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL046',
    'EDGE',
    'OE008',
    'INSTITUTIONAL',
    'F007',
    'role_compatible',
    'COMPATIBLE',
    'NO',
    '병사→장교 체포 명령→실행 경로는 제도상 compatible하다(사용자 예시).'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL047',
    'EDGE',
    'OE046',
    'INSTITUTIONAL',
    'F014',
    'procedure_available',
    'COMPATIBLE',
    'NO',
    '안핵어사 차하 → 현지 신문 → 복명.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL048',
    'EDGE',
    'OE047',
    'INSTITUTIONAL',
    'F017',
    'review_available',
    'COMPATIBLE',
    'NO',
    '비변사 보류.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL049',
    'EDGE',
    'OE040',
    'INSTITUTIONAL',
    'F006',
    'information_flow_compatible',
    'COMPATIBLE',
    'NO',
    '장계 → 국왕 판단.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL050',
    'NODE',
    'EP26',
    'ENVIRONMENT',
    'E001',
    'environmental_fit',
    'COMPATIBLE',
    'NO',
    '질병 사망 평가와 호서 전염병 환경이 부합한다. 개인 감염의 증명은 아니다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL051',
    'NODE',
    'EP26',
    'ENVIRONMENT',
    'E003',
    'environmental_fit',
    'COMPATIBLE',
    'NO',
    '구금 기간에 전염병이 지속되었다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL052',
    'NODE',
    'EP27',
    'ENVIRONMENT',
    'E001',
    'environmental_fit',
    'COMPATIBLE',
    'NO',
    '전염병 사망 판단과 부합.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL053',
    'NODE',
    'EP27',
    'ENVIRONMENT',
    'E003',
    'environmental_fit',
    'COMPATIBLE',
    'NO',
    '전염병 사망 판단과 부합.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL054',
    'NODE',
    'EP27',
    'ENVIRONMENT',
    'E004',
    'environmental_fit',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '옥수 전염병이 정책 현안이었음. 날짜가 사망 이후라 context로만 쓴다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL055',
    'NODE',
    'EP27',
    'ENVIRONMENT',
    'E002',
    'environmental_fit',
    'COMPATIBLE_WITH_CAVEAT',
    'NO',
    '기근은 거시 스트레스 맥락이다. 직접 사인이 아니다.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL056',
    'NODE',
    'EP21',
    'ENVIRONMENT',
    'E001',
    'environmental_fit',
    'COMPATIBLE',
    'NO',
    '병사(病死) 보고와 부합.'
);
INSERT INTO STG_NODE_FEATURE_LINKS (LINK_ID, TARGET_KIND, TARGET_ID, FEATURE_LAYER, FEATURE_ID, DIMENSION, ASSESSMENT, CREATES_EVENT, RATIONALE)
VALUES (
    'FL057',
    'NODE',
    'EP21',
    'ENVIRONMENT',
    'E003',
    'environmental_fit',
    'COMPATIBLE',
    'NO',
    '병사(病死) 보고와 부합.'
);

-- output/clean/identity_register.csv (11행)
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID01',
    '공초의 ''병사'' (CF021·CF023·CF024)',
    '이광섭',
    'RESOLVED',
    'USER',
    '사용자 확정: 병사는 병마절도사의 약칭이고, 이 사건에서 충청도 병마절도사로 이광섭이 특정되어 있다(CF025 기사 제목·심리 대상).',
    NULL,
    '조건부 사용 없음(RESOLVED)',
    'NO',
    'RESOLVED_BY_USER',
    'CF025: 5/12 기사가 이광섭을 사건의 병사 지휘 책임자로 심리(기사 제목: 충청도 병마절도사). 강한 맥락이지만 공초 문장 자체는 ''병사''만 씀.',
    'CF021|CF023|CF024|CF025|CF044|CF047'
);
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID02',
    '''한 비장'' (CF016·CF017)',
    '한재욱',
    'RESOLVED',
    'USER',
    '사용자 확정: 자미덕 공초의 ''한 비장''과 이어지는 한재욱의 공방(CF018: 자미덕을 방으로 불러 남은 밥을 준 사실 인정, 은밀한 사주 부인)이 같은 인물을 가리킨다. 사주 주장과 부인은 서로 다른 진술로 유지한다.',
    NULL,
    '조건부 사용 없음(RESOLVED); 확정과 충돌해 PRUNED된 후보: G09b',
    'NO',
    'RESOLVED_BY_USER',
    'CF018: 한재욱이 자미덕을 방으로 불러 밥을 준 사실을 인정. 동일인 확정 문장은 없음.',
    'CF016|CF017|CF018'
);
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID03',
    '처분문의 ''한가'' (CF048)',
    '한재욱',
    'RESOLVED',
    'USER',
    '사용자 확정: 처분문(CF048)의 ''병영 비장 한가''는 한재욱이다.',
    NULL,
    '조건부 사용 없음(RESOLVED); 확정과 충돌해 PRUNED된 후보: G09c',
    'NO',
    'RESOLVED_BY_USER',
    'CF048 notes: 처분문 표면형은 한가.',
    'CF048|CF008|CF018'
);
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID04',
    '''병영의 하급 보조자'' (audit-only V3P0026·V3P0027·V3P0124)',
    '한재욱',
    'UNRESOLVED',
    NULL,
    NULL,
    'audit-only 자료(05, 이조원 주장)에만 있고 인명이 직접 나오지 않는다. 현재 DAG·후보·world 어디에도 쓰이지 않아 결정해도 모델 결과가 바뀌지 않는다(참고용 미해결).',
    'NONE',
    'NO',
    'REFERENCE_ONLY (모델 미사용)',
    'confirmed set 밖(이조원 주장). DAG에서는 사용하지 않음.',
    NULL
);
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID05',
    '''풍각 김상제'' (CF020)',
    '김명신',
    'RESOLVED',
    'USER',
    '사용자 확정: 같은 ''풍각'' 지명·호칭 맥락이고 같은 사건의 수사선상에서 등장한다. ''김상제''와 ''김생원''은 이름이 아니라 서로 다른 호칭 표현이므로 호칭 차이만으로 별개 인물로 볼 이유가 없다(CF020·CF022).',
    NULL,
    '조건부 사용 없음(RESOLVED)',
    'NO',
    'RESOLVED_BY_USER',
    'CF022는 ''풍각 김생원''=김명신을 직접 식별. 김상제(상주 호칭)와의 동일성은 confirmed 문장에 없음 (audit V3P0095 object 필드는 김명신).',
    'CF020|CF022'
);
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID06',
    '''병영의 염탐 담당자'' (CF043)',
    '유제희',
    'UNRESOLVED',
    NULL,
    NULL,
    '정조 판단(CF043)은 직책 표현(''병영의 염탐 담당자'')만 쓰고 이름을 적지 않았다.',
    'OE071, G04a, W1',
    'NO',
    'KEEP_UNRESOLVED (사용자 수동 검토: 추가 사료 없이 확정하지 않고 현재 불확실성 유지)',
    'CF020: 유제희가 현지 탐문 중 구순 발언을 기록해 올림. 정조 판단은 직책 표현만 씀.',
    'CF043|CF020'
);
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID07',
    '''철편 네 개'' (CF010, 이진욱: 한재욱이 만들어 줌)',
    '''철퇴 네 개'' (CF044, 정조: 이광섭이 만들게 함)',
    'UNRESOLVED',
    NULL,
    NULL,
    '개수(네 개)와 사건은 같지만 물건 이름(철편/철퇴)과 행위 층위(제작·지급/제작 지시)가 다르다.',
    'OE080, G02a, W1, W3',
    'NO',
    'KEEP_UNRESOLVED (사용자 수동 검토: 추가 사료 없이 확정하지 않고 현재 불확실성 유지)',
    '개수·사건이 같아 대응 가능성이 높음. 행위 층위(제작·지급 vs 제작 지시)가 다르므로 모순으로도 동일 행위로도 확정하지 않음.',
    'CF010|CF044'
);
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID08',
    '3/4 ''장교 일행'' (CF023)',
    '조계완 포함 여부 (CF024)',
    'UNRESOLVED',
    NULL,
    NULL,
    '3/4 ''장교 일행''의 구성원은 기록되지 않았다.',
    'OE010',
    'NO',
    'KEEP_UNRESOLVED (사용자 수동 검토: 추가 사료 없이 확정하지 않고 현재 불확실성 유지)',
    'CF008: 2/28 지시 대상에 ''조계완 등'' 포함. 3/4 구성원은 미기록.',
    'CF023|CF024|CF008'
);
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID09',
    'CF030 ''당시 장계''',
    '이형원 5/12 장계(CF027)',
    'ACCEPTED_BY_PROVENANCE',
    NULL,
    NULL,
    NULL,
    'OE040',
    'NO',
    NULL,
    '같은 기사 SRC3_001(제목: 이형원 장계 및 정조 처분).',
    'CF030|CF027'
);
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID10',
    '풍각 김생원 / 흥덕 김생원',
    '김명신 / 김갑득',
    'DOCUMENTED',
    NULL,
    NULL,
    NULL,
    'NONE',
    'NO',
    NULL,
    'CF022 DOCUMENTED_SOURCE_IDENTIFICATION.',
    'CF022'
);
INSERT INTO STG_IDENTITY_REGISTER (IDENTITY_ID, SURFACE_A, SURFACE_B, STATUS, RESOLVED_BY, RESOLUTION_BASIS, UNRESOLVED_REASON, MODEL_RELEVANCE, MANUAL_DECISION_REQUIRED, REVIEW_DECISION, CONTEXT, REFERENCED_FACTS)
VALUES (
    'ID11',
    '''원돌'' (CF020 ''원돌 등의 이름'')',
    '정원돌 (CF009·CF016)',
    'RESOLVED',
    'USER',
    '사용자 확정: 유제희 기록의 ''원돌''(CF020)은 정원돌(CF009·CF016)이다.',
    NULL,
    '조건부 사용 없음(RESOLVED)',
    'NO',
    'RESOLVED_BY_USER',
    '이름 일부가 겹치지만 confirmed 문장은 같은 사람이라고 하지 않는다.',
    'CF020|CF009|CF016'
);

-- output/clean/gaps.csv (13행)
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G01',
    '소장 접수 → 체포령 → 2/28 병영 출동의 연결',
    'PROCEDURAL / INFORMATION_FLOW',
    'EP03|EP04',
    'CF006, CF007–CF010, CF026',
    '체포령(CF006)의 발령 기관과 2/28 병영 비장청 출동(CF007–010) 사이를 잇는 절차가 confirmed set에 없다. observed DAG에는 시간 edge(OE003)만 있다.',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G02',
    '2/28 출동 지시의 상위 명령 출처',
    'ORDER_CHAIN',
    'EP04|EP30',
    'CF008–CF010, CF044, CF025, CF026',
    '이진욱 진술에서는 한재욱이 지시했다. 정조 판단에서는 이광섭이 철퇴를 만들게 했다. 한재욱 위에서 누가 명령했는지는 기록되지 않았다.',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G03',
    '유제희 탐문의 시점·파견자·기록 수신자',
    'INFORMATION_FLOW / TEMPORAL',
    'EP08|EP04|EP09',
    'CF020, CF009, CF021',
    'CF020에는 날짜·파견자·수신자가 없다. 그래서 2/28 체포 대상 선정, 3/4 김생원 체포 지시와의 선후를 정할 수 없다.',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G04',
    '구순의 발언·성명 → 3/4 병사 체포 지시까지의 정보 경로',
    'INFORMATION_FLOW (핵심)',
    'EP08|EP07|EP10|EP09',
    'CF020, CF016, CF021, CF043',
    '정조는 ''성명 제공 → 횡액''의 책임 사슬을 판단했다(CF043). 그러나 observed DAG에서 EP08(구순 발언 기록)과 EP09(병사 지시) 사이에는 event 수준 edge가 없다. 사용자 지정 branch B의 ''→ 병영 수사선상'' 단계가 여기서 끊긴다.',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G05',
    '3/4 구순 서찰의 전달과 내용',
    'INFORMATION_FLOW',
    'EP10|EP30',
    'CF024, CF044',
    '서찰을 건넨 사실(CF024)과 ''이광섭이 구순 편을 들었다''는 판단(CF044) 사이에 전달·내용이 기록되지 않았다.',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G06',
    '3/4 체포 ~ 사망(5/12 보고 이전) 사이 구금 경과',
    'TEMPORAL / PROCEDURAL',
    'EP11|EP13|EP21|EP27',
    'CF023, CF027, CF029, CF040, CF041',
    '체포일(3/4)과 사망 보고(5/12) 사이 약 두 달 동안 발병 시점, 처우, 사망 시점·장소가 기록되지 않았다. 5/12 ''구금·조사''와 6/13 ''평범한 신문도 없음''이 긴장 관계다.',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G07',
    '5월 ''도난 없음 방향'' 판단의 형성 경로',
    'REVIEW / JUDGMENT_FORMATION',
    'EP13|EP15|EP17|EP24',
    'CF027, CF030, CF032, CF038',
    '5/12·5/27 판단이 왜 ''도난 없음'' 쪽으로 기울었는지(6/13에 번복됨) 근거 경로가 confirmed set에 없다. 이조원은 전문(傳聞) 의존(CF033)이 관측되어 있으나 이형원 장계 쪽 경로는 비어 있다.',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G08',
    '5/27 이조원 비판 → 5/28 홍대협 차하의 동기',
    'PROCEDURAL',
    'EP18|EP20',
    'CF033, CF035',
    '하루 차이의 두 royal action 사이에 동기 연결 문장이 없다(OE045는 시간 edge뿐).',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G09',
    '처분문 ''한가''의 처분 근거와 동일성',
    'IDENTITY / RESPONSIBILITY',
    'EP35|EP07|EP12|EP04',
    'CF048, CF016, CF017, CF018, CF008',
    '한가 처분(CF048)에 연결된 책임 판단 node가 없다. 한가=한재욱=한 비장은 사용자 확정(ID02·ID03 RESOLVED)이지만, 한가 처분의 근거 행위는 기록되지 않았다.',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G10',
    '이형원 6/13 파직 → 6/16 유임',
    'DISPOSITION',
    'EP36|EP37',
    'CF049, CF050',
    '파직과 3일 뒤 유임의 사유가 모두 기록되지 않았다.',
    'OPEN_UNRESOLVED',
    '사용자 검토: latent bridge를 채택하지 않음. 이유를 억지로 채우지 않고 gap을 열어 둔다(world에서도 비움).'
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G11',
    '변지돌의 공주진 선행 체포 경위',
    'PROCEDURAL',
    'EP04|EP05',
    'CF009, CF011',
    '2/28 체포 지시 대상(변지돌)이 2/29에는 이미 공주진에 잡혀가 있었다. 누가 왜 잡았는지 비어 있다.',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G12',
    '김명신 아내의 사망 경로',
    'TEMPORAL / BIOLOGICAL',
    'EP27',
    'CF040',
    '정조는 ''부처''가 전염병으로 죽었다고 판단했으나 아내의 사망은 다른 어떤 observed node에도 나오지 않는다.',
    'OPEN',
    NULL
);
INSERT INTO STG_GAPS (GAP_ID, TITLE, GAP_TYPE, BETWEEN_NODES, OBSERVED_ANCHOR_FACTS, WHY_GAP, GAP_STATUS, REVIEW_DECISION)
VALUES (
    'G13',
    '구순 의금부 구금·신문 명령의 실행',
    'ORDER_TO_ACTION',
    'EP16|EP19|EP29',
    'CF031, CF034, CF043',
    '5/12·5/27 두 차례 명령(order)은 관측되지만 실행·신문 결과(action)는 confirmed set에 없다.',
    'OPEN',
    NULL
);

-- output/clean/latent_candidates.csv (38행)
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G01a',
    'G01',
    'LATENT',
    'MINI_DAG',
    '청주 진영 정소 → 진영이 병영 비장 쪽에 수사를 넘김 → 2/28 출동',
    '구순의 소장이 청주 진영(영장 이문협)에 접수되었고, 진영은 수사를 병영 비장 쪽에 맡겼으며, 이것이 2/28 비장청 출동으로 이어졌다.',
    'MEDIUM',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'LOW',
    '2',
    '소장 접수처 = 청주 진영; 진영→병영 이관이 2/28 이전에 이루어짐',
    NULL,
    'MEDIUM',
    'KEPT',
    'CF006, CF026(이문협이 수사를 병영 비장에게 전적으로 맡기고 방관)',
    NULL,
    'V3P0084|V3P0102',
    'SOURCE_DIRECT',
    '등급의 근거는 confirmed CF026이다(진영 영장이 수사를 병영 비장에게 맡김). 05의 V3P0084(한재욱 공초: ''진영에 정소된 뒤'')와 V3P0102(홍대협: 이문협이 병영 비장 지휘대로 죄를 얽음)는 audit-only 흔적이며 후보를 OBSERVED로 올리지 않는다.',
    'EP03 구순의 소장과 체포령',
    'EP04 2월 28일 밤 병영 출동 준비',
    '소장이 청주 진영에 접수되었고, 진영이 수사를 병영 비장 쪽에 넘겼으며, 그것이 2/28 이전이었다',
    'PARTIAL',
    'MEDIUM (진술 기록 endpoint 포함)',
    'MEDIUM',
    'CF026|V3P0084|V3P0102',
    'CONFIRMED_NON_ENDPOINT|AUDIT_ONLY',
    'MEDIUM',
    'HIGH',
    'HIGH',
    'HIGH',
    '''진영 → 병영 비장 위임''은 endpoint가 아닌 CF026(이형원 평가: 이문협이 수사를 병영 비장에게 맡김)이 지지한다. 그러나 ''접수처 = 청주 진영''은 05 audit-only(V3P0084 한재욱 공초)에만 있고 이관 시점도 없다. 일부만 지지되므로 MEDIUM이다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G01b',
    'G01',
    'LATENT',
    'SINGLE',
    '소장이 병영에 직접 접수',
    '구순이 소장을 병영에 직접 올렸고, 병영이 체포령을 내려 2/28 출동했다.',
    'NONE',
    'HIGH',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'MEDIUM',
    '1',
    '소장 접수처 = 병영',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF006',
    'CF026(진영 영장 이문협이 왜 위임·방관으로 평가되었는지 설명되지 않음); 05 V3P0084(한재욱: ''진영에 정소된 뒤'' — audit-only, 반대 방향)',
    NULL,
    'SOURCE_DIRECT',
    '이 후보에서는 진영 영장 이문협이 왜 평가 대상이 되었는지 설명되지 않는다.',
    'EP03 구순의 소장과 체포령',
    'EP04 2월 28일 밤 병영 출동 준비',
    '소장이 병영에 직접 접수되었고 병영이 체포령을 냈다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'NONE',
    NULL,
    'NONE',
    'NONE',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    '접수처를 병영으로 적은 사료가 없다. 근거로 든 CF006은 endpoint(EP03) 자체이고, 05 V3P0084는 오히려 진영 정소를 말한다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G01c',
    'G01',
    'LATENT',
    'MINI_DAG',
    '청주목 수령 → 관찰사 → 병영 이첩',
    '소장이 청주목 수령에게 접수되었고, 관찰사를 거쳐 병영으로 이첩되었다.',
    'NONE',
    'MEDIUM',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'MEDIUM',
    '3',
    '접수처 = 수령; 관찰사 경유; 관찰사의 병영 이첩이 6일 안에 이루어짐',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    '(제도 피쳐 F005·F006만)',
    'CF027·CF025(이형원 장계에 자기 선행 관여 언급이 없음 — 약한 반증)',
    NULL,
    'INSTITUTIONAL_COMPATIBILITY',
    '제도적으로는 가능하지만 사료 지지가 없다. ''제도 가능 ≠ 실제 발생''을 보여 주는 대조 후보다.',
    'EP03 구순의 소장과 체포령',
    'EP04 2월 28일 밤 병영 출동 준비',
    '소장이 청주목 수령에게 접수되어 관찰사를 거쳐 병영으로 이첩되었다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'NONE',
    NULL,
    'INSTITUTIONAL',
    'NONE',
    'MEDIUM',
    'LOW',
    'LOW',
    '제도 피쳐(F005·F006)상 가능한 경로라는 것 말고는 사료 근거가 없다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G02a',
    'G02',
    'LATENT',
    'SINGLE',
    '이광섭이 출동·철퇴 제작을 지시하고 한재욱이 실무 전달 (ID07 조건)',
    '이광섭(CF025의 지휘 책임자)이 2/28 출동과 철퇴 네 개 제작을 지시했고, 한재욱은 그 지시를 장교들에게 전달·집행했다. 정조가 말한 ''철퇴 네 개''(CF044)와 이진욱이 말한 ''철편 네 개''(CF010)가 같은 물건일 때(ID07)만 성립한다.',
    'MEDIUM',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'LOW',
    '2',
    '철퇴 네 개(CF044) = 철편 네 개(CF010) (ID07); 철퇴 제작 지시와 같은 때 덕평 출동도 이광섭의 지시였음',
    'ID07',
    'MEDIUM',
    'KEPT',
    'CF044(이광섭이 철퇴 네 개를 만들게 함), CF025, CF010',
    NULL,
    'V3P0149',
    'SOURCE_DIRECT',
    '정조 판단의 행위자(이광섭)와 진술의 행위자(한재욱)를 명령/집행 층위로 나누어 양쪽을 모두 살린다. V3P0149(05: ''밤새 만들게 한'')는 audit-only 흔적이다. 미확정 동일성(ID07)에 기대므로 MEDIUM 상한.',
    '(없음 — 위쪽 원인 가설)',
    'EP04 2월 28일 밤 병영 출동 준비',
    '이광섭이 2/28 출동과 철퇴(=철편) 네 개 제작을 지시했고 한재욱이 그것을 전달·집행했다',
    'PARTIAL',
    'MEDIUM (진술 기록 endpoint 포함)',
    'MEDIUM',
    'CF044|CF025',
    'CONFIRMED_NON_ENDPOINT',
    'MEDIUM',
    'MEDIUM',
    'HIGH',
    'MEDIUM',
    'endpoint가 아닌 CF044(정조: 이광섭이 철퇴 네 개를 만들게 함)가 ''제작 지시'' 부분을 royal judgment 수준에서 지지한다. 다만 철퇴=철편은 ID07 미확정이고, 덕평 출동까지 이광섭의 지시였다는 부분은 사료에 없다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G02b',
    'G02',
    'LATENT',
    'SINGLE',
    '한재욱이 상위 명령 없이 출동 지시, 병영 지휘관은 사후 승인·묵인',
    '한재욱이 위에서 구체적인 명령을 받지 않고 자기 판단으로 2/28 출동을 지시했고, 병영 지휘관은 사후에 승인하거나 묵인했다. CF026·CF044의 ''비장에게 맡김'' 비판을 지휘 공백으로 읽는 후보다.',
    'LOW',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'MEDIUM',
    '3',
    '한재욱이 CF026·CF044가 말하는 ''비장''의 위치에 있었음(직함은 confirmed set에 없음); 비장이 상위 명령 없이 출동을 지시할 수 있었음; 병영 지휘관의 사후 승인·묵인',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF026(비장에게 전적으로 맡김), CF044(비장에게 일을 맡겼다)',
    'CF044(이광섭이 철퇴를 만들게 했다 — ID07이 성립하면 사전 관여를 시사)',
    NULL,
    'SOURCE_DIRECT',
    NULL,
    'EP04 2월 28일 밤 병영 출동 준비',
    'EP04 2월 28일 밤 병영 출동 준비',
    '한재욱이 상위 명령 없이 자기 판단으로 출동을 지시했고 병영 지휘관이 사후 승인·묵인했다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'LOW',
    'CF026|CF044',
    'CONFIRMED_NON_ENDPOINT',
    'LOW',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'CF026·CF044의 ''비장에게 맡겼다''는 평가는 위임 일반을 말할 뿐, ''상위 명령 없이''와 ''사후 묵인''은 어디에도 없다. 평가 문구를 지휘 공백으로 읽은 추론이다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G02c',
    'G02',
    'LATENT',
    'SINGLE',
    '청주 영장 이문협이 직접 출동 지휘',
    '진영 영장 이문협이 2/28 출동을 직접 지휘했다.',
    'NONE',
    'MEDIUM',
    'MEDIUM',
    'LOW',
    'LOW',
    'N/A',
    'HIGH',
    '1',
    '영장이 병영 비장청 인원을 직접 지휘',
    NULL,
    'LOW',
    'KEPT_AS_CONTRAST (관측·최종 판단과 충돌)',
    NULL,
    'CF026(이문협은 비장에게 맡기고 ''방관''했다고 평가됨)',
    NULL,
    'SOURCE_DIRECT',
    '관측된 평가와 정면으로 충돌한다. 대조용.',
    '(없음 — 위쪽 원인 가설)',
    'EP04 2월 28일 밤 병영 출동 준비',
    '청주 영장 이문협이 2/28 출동을 직접 지휘했다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'NONE',
    NULL,
    'NONE',
    'NONE',
    'LOW',
    'LOW',
    'LOW',
    '지지 근거가 없고 CF026(이문협은 맡기고 ''방관'')과 충돌한다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G03a',
    'G03',
    'LATENT',
    'MINI_DAG',
    '한재욱이 유제희를 탐문에 보내고, 2/28 이전 기록이 한재욱에게 올라감',
    '한재욱이 유제희를 현지 탐문에 내보냈고, 유제희는 2/28 이전에 구순의 ''풍각 김상제도 극히 수상하다''는 말을 원돌 등의 이름과 함께 기록해 한재욱에게 올렸다. 2/28 체포 대상(변지돌·정원돌) 선정에 이 기록이 쓰였다.',
    'MEDIUM',
    'MEDIUM',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'LOW',
    '3',
    '파견자 = 한재욱 (05 V3P0085에만 있음); 탐문·기록 시점이 2/28 이전; 기록 수신자 = 한재욱',
    NULL,
    'MEDIUM',
    'KEPT',
    'CF020(''원돌 등의 이름과 함께''), CF009(정원돌 체포 지시)',
    NULL,
    'V3P0085|V3P0086|V3P0087',
    'SOURCE_DIRECT',
    '05 한재욱 공초(V3P0085–V3P0087, audit-only)는 자신이 유제희를 내보냈고 유제희가 변지돌·변재돌·정원돌·김명신 등의 성명을 적어 왔다고 진술한다. 이 후보는 그 진술을 사실로 올리지 않고 연결 가설로만 쓴다. 기록이 2/28 이전이라면 3/4 김생원 체포가 왜 2/28 대상에 없었는지는 이 후보로 설명되지 않는다. 원돌=정원돌은 ID'
        || '11 사용자 확정(RESOLVED)이라 가정에서 뺐다(가정 4→3). 후보 자체는 여전히 LATENT이며 source_consistency(MEDIUM)는 그대로다.',
    'EP08 유제희의 현지 탐문과 구순 발언 기록',
    'EP04 2월 28일 밤 병영 출동 준비; EP08 유제희의 현지 탐문과 구순 발언 기록',
    '한재욱이 유제희를 탐문에 보냈고, 유제희 기록이 2/28 이전 한재욱에게 올라가 2/28 체포 대상 선정에 쓰였다',
    'PARTIAL',
    'MEDIUM (진술 기록 endpoint 포함)',
    'MEDIUM',
    'V3P0085|V3P0086|V3P0087',
    'AUDIT_ONLY',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    '파견과 명단 작성은 05 한재욱 공초(V3P0085–V3P0087)에 진술로 있다. 그러나 audit-only이고 기록 시점·수신자는 없다. CF009·CF020은 endpoint(EP04·EP08)라 bridge 근거로 쓰지 않았다. audit-only 상한으로 MEDIUM이다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G03b',
    'G03',
    'LATENT',
    'SINGLE',
    '탐문은 2/29~3/4 사이, 김상제(=김명신) 언급이 3/4 지시를 직접 촉발',
    '유제희의 탐문과 기록은 2/29 이후 3/4 이전에 있었고, 기록 속 ''풍각 김상제'' 언급이 3/4 풍각 김생원 체포 지시를 직접 촉발했다.',
    'LOW',
    'MEDIUM',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'MEDIUM',
    '2',
    '탐문 시점 2/29~3/4; 기록이 병사 지시 판단에 쓰임',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF043, CF020',
    'CF020(''원돌 등''과 한 기록 — ID11 확정: 원돌(=정원돌)은 이미 2/28 체포 대상이었으므로 기록이 2/28 이전이라는 쪽과 긴장)',
    'V3P0095',
    'SOURCE_DIRECT',
    NULL,
    'EP08 유제희의 현지 탐문과 구순 발언 기록',
    'EP09 3월 4일 병사의 김생원 체포 지시',
    '유제희 탐문이 2/29~3/4 사이였고 김상제 언급이 3/4 지시를 직접 촉발했다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'LOW',
    'CF043',
    'CONFIRMED_NON_ENDPOINT|TEMPORAL',
    'LOW',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'CF043(정조: 성명 제공 → 횡액)은 정보가 사건으로 이어졌다는 판단일 뿐 시점·직접 촉발을 말하지 않는다. ID11 확정으로 원돌(=정원돌)이 2/28 대상이었으므로 시점 가정과 긴장한다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G03c',
    'G03',
    'LATENT',
    'SINGLE',
    '유제희가 병사에게 직접 보고(비장 우회)',
    '유제희가 탐문 결과를 비장을 거치지 않고 병사에게 직접 올렸다.',
    'NONE',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'MEDIUM',
    '2',
    '수신자 = 병사; 비장 계통 우회',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    NULL,
    '05 V3P0085(한재욱: 유제희를 자신이 내보냈다 — audit-only)와 긴장',
    NULL,
    'SOURCE_DIRECT',
    NULL,
    'EP08 유제희의 현지 탐문과 구순 발언 기록',
    'EP09 3월 4일 병사의 김생원 체포 지시',
    '유제희가 비장을 건너뛰고 병사에게 직접 보고했다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'NONE',
    NULL,
    'NONE',
    'NONE',
    'MEDIUM',
    'LOW',
    'LOW',
    '지지 근거가 없고 05 V3P0085(한재욱이 유제희를 내보냈다)와 긴장한다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G04a',
    'G04',
    'LATENT',
    'MINI_DAG',
    '공식 정보 경로: 유제희 기록 → 비장 계통 → 병사 → 3/4 지시',
    '구순이 ''풍각 김상제도 극히 수상하다''고 한 말이 유제희의 기록으로 병영 비장 계통에 들어갔고, 비장 계통이 병사에게 보고해 3/4 풍각 김생원 체포 지시의 근거가 되었다. 풍각 김상제=김명신은 ID05 사용자 확정이다. 보고 경로는 가설이다.',
    'MEDIUM',
    'MEDIUM',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'LOW',
    '2',
    '병영의 염탐 담당자 = 유제희 (ID06) — 정조 판단(CF043)과 대응시킬 때; 기록이 3/4 이전 비장 계통을 거쳐 병사에게 보고됨',
    'ID06',
    'MEDIUM',
    'KEPT',
    'CF043(성명 제공 → 횡액), CF020, CF044(비장에게 일을 맡김)',
    NULL,
    'V3P0038|V3P0095',
    'SOURCE_DIRECT',
    '정조의 책임 사슬(CF043)을 event 수준으로 펼친 것이다. 정조는 ''구순이 적어 주었다'', 유제희는 ''자신이 기록했다''고 했다. 이 차이는 해소하지 않는다.',
    'EP08 유제희의 현지 탐문과 구순 발언 기록',
    'EP09 3월 4일 병사의 김생원 체포 지시',
    '유제희 기록이 비장 계통을 거쳐 3/4 이전 병사에게 보고되어 체포 지시의 근거가 되었다',
    'PARTIAL',
    'MEDIUM (진술 기록 endpoint 포함)',
    'MEDIUM',
    'CF043|CF044|V3P0038',
    'CONFIRMED_NON_ENDPOINT|AUDIT_ONLY',
    'MEDIUM',
    'MEDIUM',
    'HIGH',
    'MEDIUM',
    'endpoint가 아닌 CF043(정조: 구순이 병영의 염탐 담당자에게 성명을 적어 주었고 그것이 횡액으로 이어졌다)이 ''구순의 정보가 체포로 이어졌다''는 연결을 판단 수준에서 지지한다. ''비장 계통 → 병사'' 경로는 사료에 없고, 염탐 담당자=유제희는 ID06 미확정이다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G04b',
    'G04',
    'LATENT',
    'MINI_DAG',
    '자미덕 대질 진술 경로: 회유 주장 진술(열린 목록) → 병사 지시',
    '자미덕은 구류 중 한 비장이 정원돌·이집거·김갑득·김성손·김흥득 ''등''을 큰 도적이라고 말하라고 했고, 대질 때 그 지휘에 따라 거짓으로 꾸며 말했다고 진술했다(EP07). 이 후보는 그 대질 진술이 3/4 이전 병사에게 보고되어 흥덕 김생원(김갑득)과 풍각 김생원 체포 지시의 근거가 되었다고 가정한다.',
    'LOW',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'MEDIUM',
    '3',
    '대질 진술이 3/4 이전에 있었음; 그 진술이 병사에게 보고됨; 열린 목록 ''등''에 풍각 김생원이 들어 있었음(05 V3P0042·V3P0128 윤노동 주장, audit-only)',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF016(김갑득이 명시 명단에 있고, 3/4 김명신과 함께 체포됨 — CF023)',
    'CF018(한재욱: 은밀한 사주 부인 — claim-level. ID02 확정으로 같은 인물에 대한 서로 다른 진술)',
    'V3P0042|V3P0089|V3P0128',
    'SOURCE_DIRECT',
    '제도 평가: 진술 → 보고 → 지시라는 정보 경로 자체는 F008·F020과 양립하므로 institutional_fit은 MEDIUM이다. 회유 행위의 합법성 LOW(F002)는 observed node EP07의 feature link에 이미 붙어 있다. 윤노동 별단(05)은 한재욱이 변가의 처를 꾀어 김명신이 도적 괴수라는 공초를 내게 했다고 주장하지만'
        || ' audit-only이며, 이 후보는 그 주장을 사실로 올리지 않는다.',
    'EP07 한 비장의 석방 조건 제시와 대질 시 거짓 진술',
    'EP09 3월 4일 병사의 김생원 체포 지시',
    '자미덕의 대질 진술이 3/4 이전 병사에게 보고되어 김생원 체포 지시의 근거가 되었다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'LOW',
    'CF023|V3P0042|V3P0128',
    'CONFIRMED_NON_ENDPOINT|AUDIT_ONLY',
    'LOW',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'CF023(김갑득이 김명신과 함께 체포)은 이름이 겹친다는 정황일 뿐이다. 05 윤노동 주장은 회유 공초를 말하지만 그 공초가 병사에게 보고되어 지시 근거가 되었다는 내용은 없다. 보고·근거 연결 자체는 사료에 없다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G04c',
    'G04',
    'LATENT',
    'SINGLE',
    '사적 경로: 3/4 이전 구순→병사 사적 접촉으로 김명신을 의심 대상으로 알림',
    '3/4 이전에 구순이 병사에게 사적 서신이나 접촉으로 김명신을 의심 대상으로 알렸고, 병사가 그 정보에 기대어 체포를 지시했다.',
    'LOW',
    'MEDIUM',
    'LOW',
    'LOW',
    'LOW',
    'N/A',
    'MEDIUM',
    '2',
    '3/4 이전의 미기록 서신·접촉 존재; 그 내용에 김명신 지목',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF024(3/4 서찰 — 사적 통로가 있었음을 보여 줌), CF044(구순 편을 듦)',
    NULL,
    'V3P0053|V3P0148',
    'SOURCE_DIRECT',
    'CF024의 서찰은 ''잡으러 가는 길''에 건넨 것이라 3/4 지시보다 뒤다. 그래서 이 후보는 그보다 앞선, 기록되지 않은 접촉을 따로 가정해야 한다. 05의 V3P0053(명업: 구순이 찾아온 장교 한 명과 안행랑에서 조용히 대화)과 V3P0148(정조: 이광섭이 구순과의 오래된 혐의를 씻은 뒤 구순 편을 듦)은 audit-only 흔적이다. 구순에게는 '
        || '공식 지휘권이 없으므로 ''명령''이 아니라 정보 제공으로만 표현했다(F007·F020 LOW).',
    'EP01 구순–김명신 관계 변화',
    'EP09 3월 4일 병사의 김생원 체포 지시',
    '3/4 이전 구순이 병사에게 사적으로 김명신을 의심 대상으로 알렸다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'LOW',
    'CF024|CF044|V3P0053|V3P0148',
    'CONFIRMED_NON_ENDPOINT|AUDIT_ONLY',
    'LOW',
    'LOW',
    'LOW',
    'LOW',
    'CF024(3/4 서찰)는 지시 이후의 일이고, CF044(''구순 편을 듦'')는 관계 판단이다. 3/4 이전 접촉을 적은 사료는 없다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G04d',
    'G04',
    'LATENT',
    'SINGLE',
    '석단 공초 경로: 다른 피의자 공초가 김명신을 도적 괴수로 지목',
    '석단이라는 피의자의 공초에서 김명신이 도적 괴수로 언급되었고, 이것이 병사 지시로 이어졌다.',
    'LOW',
    'LOW',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'MEDIUM',
    '3',
    '석단 공초 시점이 3/4 이전; 석단 공초 내용(유제희 발언의 중첩 진술); 병사에게 보고',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    NULL,
    NULL,
    'V3P0089',
    'SOURCE_DIRECT',
    'confirmed set에 석단은 나오지 않는다. 05의 한재욱 공초 속 유제희 발언(중첩)이 유일한 흔적이다.',
    '(없음 — 위쪽 원인 가설)',
    'EP09 3월 4일 병사의 김생원 체포 지시',
    '석단 공초가 3/4 이전 병사에게 보고되어 김명신 체포 지시로 이어졌다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'LOW',
    'V3P0089',
    'AUDIT_ONLY',
    'LOW',
    'LOW',
    'LOW',
    'LOW',
    '05 한재욱 공초 속 유제희 발언(중첩, audit-only)에 석단 공초가 언급될 뿐, 시점·보고는 없다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G04e',
    'G04',
    'LATENT',
    'SINGLE',
    '구순이 장교에게 직접 공식 체포 명령',
    '구순이 장교들에게 김명신 체포를 직접 명령했다.',
    'NONE',
    'MEDIUM',
    'INCOMPATIBLE',
    'INCOMPATIBLE',
    'LOW',
    'N/A',
    'HIGH',
    '1',
    '전 부사 구순이 병영 장교 지휘권 보유',
    NULL,
    'INCOMPATIBLE',
    'PRUNED (incompatible)',
    NULL,
    'CF023(장교 일행은 ''병사의 분부에 따라'' 체포)',
    NULL,
    'NONE',
    '제도(F007·F008)와 관측(CF023) 모두와 충돌한다. pruning 예시(사용자 지정: 구순→장교 공식 체포명령 low).',
    '(없음 — 위쪽 원인 가설)',
    'EP11 3월 4일 김명신·김갑득 체포',
    '구순이 장교에게 직접 공식 체포 명령을 내렸다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'NONE',
    NULL,
    'NONE',
    'NONE',
    'INCOMPATIBLE',
    'INCOMPATIBLE',
    'INCOMPATIBLE',
    '근거가 없고 CF023(''병사의 분부에 따라'')·제도(F007·F008)와 충돌한다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G05a',
    'G05',
    'LATENT',
    'SINGLE',
    '서찰이 병사에게 전달, 체포 지지·추가 의혹 내용',
    '조계완이 서찰을 병사에게 전달했고, 서찰 내용은 김명신 체포를 지지하거나 의혹을 덧붙이는 것이었다. 병사=이광섭(ID01, 사용자 확정)이므로 이 서찰은 정조가 말한 ''이광섭이 구순 편을 들었다''(CF044)의 한 배경이 된다. 전달과 내용은 가설이다.',
    'LOW',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'LOW',
    '2',
    '서찰 전달됨; 서찰 내용이 사건 관련',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF024(''바른 길을 얻었다''는 반응), CF044(구순 편을 듦), CF025(허황한 말을 믿고)',
    NULL,
    NULL,
    'SOURCE_DIRECT',
    '사적 서찰은 공식 보고 경로(장계·서계)가 아니다. 공식 명령으로서는 LOW(F020)지만, 이 후보는 ''사적 정보 전달''만 가정하므로 institutional_fit을 MEDIUM으로 둔다(전달을 막는 제도도, 공식 경로라는 근거도 없음).',
    'EP10 3월 4일 조계완의 구순 집 방문과 서찰',
    'EP30 정조: 이광섭 책임 판단',
    '조계완이 서찰을 병사에게 전달했고, 서찰 내용은 체포 지지·의혹 제기였다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'LOW',
    'CF025',
    'CONFIRMED_NON_ENDPOINT',
    'LOW',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    '전달 여부와 서찰 내용은 어디에도 없다. CF024(서찰 수령·''바른 길'' 발언)와 CF044(구순 편)는 endpoint(EP10·EP30)라 bridge 근거가 아니다. endpoint가 아닌 CF025(이형원: 허황한 말을 믿고)는 간접 정황일 뿐이다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G05b',
    'G05',
    'LATENT',
    'SINGLE',
    '서찰은 전달되었으나 사건과 무관한 인사·사례',
    '서찰은 전달되었지만 내용은 인사나 사례 정도였고 수사에는 영향을 주지 않았다.',
    'NONE',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'LOW',
    '2',
    '서찰 전달됨; 내용 무관',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    NULL,
    'CF024의 맥락(체포 직전 ''도적 다스리는 일이 바른 길을 얻었다'')과 어울리지 않음',
    NULL,
    'SOURCE_DIRECT',
    NULL,
    'EP10 3월 4일 조계완의 구순 집 방문과 서찰',
    '(없음 — 위쪽 원인 가설)',
    '서찰은 전달되었으나 사건과 무관한 인사·사례였다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'NONE',
    NULL,
    'NONE',
    'NONE',
    'MEDIUM',
    'LOW',
    'LOW',
    '지지 근거가 없고 CF024의 맥락과 어울리지 않는다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G06a',
    'G06',
    'LATENT',
    'MINI_DAG',
    '구금 중 발병 → 보수·구금 상태에서 사망 (처우는 CF041 판단을 따름)',
    '김명신은 3/4 체포 뒤 병영 구금 중 병이 났고, 보수·구금 상태에서 5/12 보고 이전에 죽었다. 처우는 정조 판단(CF041: 곤장·평문 없음)을 따른다.',
    'MEDIUM',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'LOW',
    '1',
    '발병이 체포 이후',
    NULL,
    'MEDIUM',
    'KEPT',
    'CF029(보수·구금 중 병들어 죽음), CF040, CF041',
    'CF027(''구금·조사'' — PARTIAL)',
    NULL,
    'SOURCE_DIRECT',
    '개인 발병의 근거는 관측 보고 CF029(윤노동)와 판단 CF040이다. 환경(E001·E003)은 environmental_fit 평가에만 썼고 발병 node를 만들지 않았다. ''보수''의 법적 의미는 해석하지 않는다.',
    'EP11 3월 4일 김명신·김갑득 체포',
    'EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고',
    '김명신의 발병이 3/4 체포 이후 구금 중에 시작되었고 5/12 보고 이전에 죽었다',
    'PARTIAL',
    'MEDIUM (진술 기록 endpoint 포함)',
    'MEDIUM',
    'CF029|CF040|CF041',
    'CONFIRMED_NON_ENDPOINT',
    'MEDIUM',
    'HIGH',
    'HIGH',
    'HIGH',
    'endpoint가 아닌 CF029(윤노동 별단: ''보수·구금 중 병들어 죽었다'')가 구금 중 발병·사망을 보고 수준에서 지지한다. 다만 이것은 암행어사의 보고이고, 발병이 체포 ''이후'' 시작되었다는 시점 자체를 따로 확인한 문장은 없다. 그래서 HIGH가 아니라 MEDIUM이다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G06b',
    'G06',
    'LATENT',
    'MINI_DAG',
    '형장 없는 조사 압박 + 발병 → 사망',
    '김명신은 형장은 받지 않았지만 구금 중 반복 조사 압박을 받았고, 이어 발병해 죽었다.',
    'LOW',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'MEDIUM',
    '2',
    '반복 조사 압박; 발병이 체포 이후',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF027(달포 이상 구금·조사), CF029',
    'CF041(평범한 신문도 받지 않았다 — royal judgment)',
    NULL,
    'SOURCE_DIRECT',
    NULL,
    'EP11 3월 4일 김명신·김갑득 체포',
    'EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고',
    '형장 없는 반복 조사 압박이 있었고 이어 발병해 죽었다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'LOW',
    'CF029',
    'CONFIRMED_NON_ENDPOINT',
    'LOW',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    '발병 부분은 CF029가 보고하지만, 이 후보가 새로 넣은 ''반복 조사 압박''은 근거가 CF027(''구금·조사'', endpoint EP13)뿐이다. 게다가 CF041(평범한 신문 없음)과 긴장한다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G06c',
    'G06',
    'LATENT',
    'MINI_DAG',
    '형장(곤장) → 쇠약 → 사망',
    '김명신은 구금 중 형장을 받아 쇠약해졌고, 그 뒤 죽었다.',
    'LOW',
    'HIGH',
    'LOW',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'HIGH',
    '2',
    '김명신이 형장 대상에 포함; 형장이 사망 경과에 관여',
    NULL,
    'LOW',
    'KEPT_AS_CONTRAST (관측·최종 판단과 충돌)',
    'CF028·CF029(평민·여러 죄수의 혹형 — 열린 집합)',
    'CF041(곤장을 맞지 않았다), CF040',
    'V3P0024',
    'SOURCE_DIRECT',
    '열린 집합(''무고한 평민들'', ''여러 죄수'')에 김명신을 넣어야 성립한다. 최종 royal judgment와 정면으로 충돌한다.',
    'EP11 3월 4일 김명신·김갑득 체포',
    'EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고; EP27 정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음',
    '김명신이 구금 중 형장을 받아 쇠약해진 뒤 죽었다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'LOW',
    'CF029|V3P0024',
    'CONFIRMED_NON_ENDPOINT|AUDIT_ONLY',
    'LOW',
    'LOW',
    'LOW',
    'LOW',
    'CF029의 ''여러 죄수 참혹한 형벌''은 열린 집합이라 김명신 포함을 지지하지 않는다. CF041(곤장 없음)과 정면 충돌한다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G07a',
    'G07',
    'LATENT',
    'SINGLE',
    '장물 미발견을 근거로 ''도난 없음''을 추론',
    '5월 단계의 조사자들은 확실한 장물을 찾지 못한 것을 근거로 도난 자체가 없었다고 추론했고, 정조가 이를 받아들였다.',
    'LOW',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'LOW',
    '1',
    '장물 부재가 도난 부재 추론의 근거로 쓰임',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF027(확실한 장물을 찾지 못함), CF030(장계와 조사에 따라)',
    NULL,
    NULL,
    'SOURCE_DIRECT',
    NULL,
    'EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고',
    'EP15 5월 12일 정조 1차 판단: 도난 부재 방향',
    '5월 단계의 ''도난 없음'' 판단은 장물 미발견을 근거로 한 추론이었다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'LOW',
    NULL,
    'ENDPOINT_ONLY',
    'LOW',
    'HIGH',
    'HIGH',
    'HIGH',
    '''장물 못 찾음''(CF027, EP13)과 ''도난 없음 방향 수용''(CF030, EP15)은 각각 endpoint다. CF030의 ''장계와 조사에 따라''라는 연결은 이미 observed edge OE040(REVIEW_OF)이 담고 있다. 이 후보가 새로 더한 것은 ''그중 장물 부재가 이유였다''는 추론인데, 이를 적은 사료는 없다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G07b',
    'G07',
    'LATENT',
    'SINGLE',
    '회동 조사 응답자들의 ''구순이 꾸몄다'' 진술 채택',
    '이형원의 회동 조사에서 응답자들이 구순이 도난 상황을 꾸몄다고 진술했고(05 V3P0009, audit-only), 장계와 5/12 판단이 그 진술을 채택했다.',
    'MEDIUM',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'LOW',
    '1',
    '회동 조사 응답 내용이 판단 근거로 쓰임',
    NULL,
    'MEDIUM',
    'KEPT',
    'CF030(''조사에 따라'')',
    NULL,
    'V3P0009|V3P0115|V3P0116|V3P0117',
    'SOURCE_DIRECT',
    '응답 내용은 05에만 있다(중첩 진술). 응답 내용의 진위는 다루지 않는다. 도난 부재 쪽 결론은 6/13 판단으로 수정된다(CF038·CF039).',
    '(없음 — 위쪽 원인 가설)',
    'EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고; EP15 5월 12일 정조 1차 판단: 도난 부재 방향',
    '이형원 회동 조사의 응답자 진술(''구순이 꾸몄다'')이 장계와 5/12 판단에 반영되었다',
    'PARTIAL',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'MEDIUM',
    'V3P0009|V3P0115|V3P0116|V3P0117',
    'AUDIT_ONLY',
    'MEDIUM',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    '05의 같은 장계 기사(SRC3_001)에 응답자 진술이 장계 내용으로 실려 있다(audit-only). 판단이 그 진술을 채택했다는 문장은 없지만 같은 기록 안의 연결이라 audit-only 상한인 MEDIUM이다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G07c',
    'G07',
    'LATENT',
    'SINGLE',
    '구순 집 사람들의 진술 번복이 5월 자료에 들어감',
    '명업 등 구순 집 사람들이 병영 뜰 공초에서 ''도적이 없었다''는 취지로 진술을 바꾸었고(명업은 위협이 두려워서였다고 진술 — 05), 그 번복 진술이 5월 판단 자료에 들어갔다.',
    'LOW',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'LOW',
    '2',
    '번복 진술이 장계 자료에 포함; 번복 시점이 5/12 이전',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF038(정식 안핵에서 약간의 실제 도난 확인)',
    NULL,
    'V3P0054|V3P0132',
    'SOURCE_DIRECT',
    '''위협'' 부분은 명업 자신의 진술(05 V3P0054)이며 사실로 올리지 않는다.',
    '(없음 — 위쪽 원인 가설)',
    'EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고',
    '명업 등의 번복 진술이 5월 판단 자료에 들어갔다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'LOW',
    'V3P0054|V3P0132',
    'AUDIT_ONLY',
    'LOW',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    '번복 자체는 05의 명업 공초(audit-only)에 있지만, 그것이 장계나 5월 판단 자료에 들어갔다는 내용은 없다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G07d',
    'G07',
    'LATENT',
    'SINGLE',
    '도난은 실제로 없었고 구순이 꾸몄다 (이조원·윤노동 주장)',
    '도난 자체가 없었고 구순이 상황을 꾸며 김명신을 얽었다(이조원·윤노동의 05 주장).',
    'LOW',
    'HIGH',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'HIGH',
    '1',
    '도난 날조',
    NULL,
    'LOW',
    'KEPT_AS_CONTRAST (관측·최종 판단과 충돌)',
    NULL,
    'CF038(약간의 실제 도난), CF039(정조 최종: 도난 실재)',
    'V3P0020|V3P0127',
    'SOURCE_DIRECT',
    '5월 단계 판단과 같은 방향이다. 최종 official·royal finding과 정면으로 충돌하므로 대조용으로만 둔다.',
    '(없음 — 위쪽 원인 가설)',
    'EP15 5월 12일 정조 1차 판단: 도난 부재 방향; EP25 정조 최종 도난 판단: 실재',
    '도난은 실제로 없었고 구순이 꾸몄다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'LOW',
    'V3P0020|V3P0127',
    'AUDIT_ONLY',
    'LOW',
    'MEDIUM',
    'LOW',
    'LOW',
    '이조원·윤노동의 05 주장뿐이다. CF038·CF039(최종 판단)와 정면 충돌한다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G08a',
    'G08',
    'LATENT',
    'MINI_DAG',
    '직접 안핵 부재 비판 → 독립 안핵 결정',
    '정조는 이조원이 직접 안핵하지 않은 점을 문제 삼았고(관측, CF033), 그 판단이 다음 날 독립 안핵어사 차하(관측, CF035)의 동기가 되었다는 연결만 LATENT다.',
    'LOW',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'LOW',
    '1',
    '5/27 비판이 5/28 차하의 동기',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF033(직접 안핵하지 않은 점 문제 삼음), CF035(자세히 조사해 오라)',
    NULL,
    'V3P0028',
    'SOURCE_DIRECT',
    '동기 연결은 원본(CF033·CF035·SRC3_004)에 문장으로 없으므로 LATENT다. 관측 node끼리 직접 잇지 않고 latent 판단 node를 사이에 둔다(Audit 3 WARN A3-W1 처리). observed DAG의 OE045(TEMPORAL_BEFORE, DERIVED)는 그대로다.',
    'EP18 5월 27일 정조의 이조원 비판·파직',
    'EP20 5월 28일 홍대협 공주 안핵어사 차하',
    '5/27 이조원의 직접 안핵 부재에 대한 정조의 비판이 5/28 홍대협 차하의 동기였다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'LOW',
    'V3P0028',
    'ENDPOINT_ONLY|TEMPORAL',
    'LOW',
    'HIGH',
    'HIGH',
    'HIGH',
    '두 행위(CF033 비판, CF035 차하)는 모두 endpoint다. 동기 문장은 01·04·05 어디에도 없다. 05 V3P0028도 비판 내용(endpoint와 같은 내용)일 뿐이다. 하루 차이라는 시간 인접성과 두 endpoint 내용의 주제 대응만으로는 bridge 근거가 되지 않는다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G08b',
    'G08',
    'LATENT',
    'SINGLE',
    '지세 호칭 의문 해소가 주목적',
    '정조가 홍대협을 보낸 주목적은 지세 호칭의 출처를 밝히는 것이었다.',
    'LOW',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'LOW',
    '1',
    '지세 의문이 차하의 주목적',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF045(지세 기원 조사)',
    NULL,
    'V3P0033|V3P0035|V3P0103',
    'SOURCE_DIRECT',
    '정조가 6/13에 세 의안(도난·사인·지세)을 나누었으므로(V3P0103) ''주목적''이라고 하면 과장일 수 있다.',
    '(없음 — 위쪽 원인 가설)',
    'EP20 5월 28일 홍대협 공주 안핵어사 차하',
    '홍대협 차하의 주목적은 지세 호칭의 출처를 밝히는 것이었다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'LOW',
    'V3P0033|V3P0035',
    'AUDIT_ONLY',
    'LOW',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    '05 승정원일기 대화(V3P0033·V3P0035)는 5/28에 지세랑 호칭이 화제였음을 보이지만 ''주목적''이라고 하지는 않는다. V3P0103(세 의안 분리)에 비추면 과장이다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G09a',
    'G09',
    'LATENT',
    'SINGLE',
    '한가(=한재욱) 처분 근거 = 자미덕이 진술한 회유·대질 지휘와 출동 운영',
    'ID02(한 비장=한재욱)와 ID03(한가=한재욱)은 사용자 확정(RESOLVED)이다. 따라서 처분문의 병영 비장 한가, 자미덕 진술 속 ''한 비장'', 2/28 출동을 지시한 한재욱은 같은 사람이다. 처분 근거가 자미덕이 진술한 회유·대질 지휘와 출동 운영이라는 것만 가설이다. 회유는 자미덕의 진술이고 한재욱은 은밀한 사주를 부인했으므로(CF018), 사'
        || '주를 사실로 확정하지 않는다.',
    'LOW',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'MEDIUM',
    '1',
    '처분 근거 행위 = 자미덕이 진술한 회유·대질 지휘와 출동 운영',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF048(병영 비장 한가), CF016·CF017(한 비장), CF018(한재욱이 자미덕을 방으로 부름)',
    'CF018(은밀한 사주 부인 — claim-level)',
    'V3P0042|V3P0112|V3P0128',
    'SOURCE_DIRECT',
    'ID02·ID03 사용자 확정으로 동일성 가정 2개를 뺐다(가정 3→1). source_consistency MEDIUM과 contradiction_risk MEDIUM 때문에 등급은 MEDIUM 그대로다.',
    'EP04 2월 28일 밤 병영 출동 준비; EP07 한 비장의 석방 조건 제시와 대질 시 거짓 진술',
    'EP35 병영 비장 한가 처분',
    '한가(=한재욱) 처분의 근거는 자미덕이 진술한 회유·대질 지휘와 출동 운영이었다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'LOW',
    'CF044|V3P0042|V3P0128',
    'CONFIRMED_NON_ENDPOINT|AUDIT_ONLY',
    'LOW',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    '처분 근거를 적은 문장이 없다. CF016·CF017·CF018·CF048은 endpoint(EP07·EP35 등)라 근거가 아니다. CF044와 05 윤노동 주장은 비장·회유를 말할 뿐 한가 처분과 연결하지 않는다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G09b',
    'G09',
    'LATENT',
    'MINI_DAG',
    '한가 = 한재욱, ''한 비장''은 다른 사람 (ID02 확정과 충돌)',
    '한가=한재욱이고 자미덕을 회유했다는 ''한 비장''은 별인이라고 가정한다. 그 경우 처분 근거는 출동·철편 운영이다. 이 전제(ID02 불성립)는 사용자가 확정한 ID02(한 비장=한재욱)와 충돌한다.',
    'NONE',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'MEDIUM',
    '2',
    '한 비장 ≠ 한재욱 (ID02 불성립, 별도 인물 존재); 처분 근거 = 출동 운영만',
    'ID02',
    'INCOMPATIBLE',
    'PRUNED (사용자 확정 동일성 ID02과 충돌)',
    NULL,
    'CF018(한재욱이 자미덕을 방으로 불렀다고 인정 — 한 비장과의 대응을 시사)',
    NULL,
    'SOURCE_DIRECT',
    NULL,
    'EP04 2월 28일 밤 병영 출동 준비; EP07 한 비장의 석방 조건 제시와 대질 시 거짓 진술',
    'EP35 병영 비장 한가 처분',
    '자미덕 진술의 ''한 비장''은 한재욱과 다른 사람이고 한가 처분 근거는 출동 운영뿐이다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'NONE',
    NULL,
    'NONE',
    'NONE',
    'MEDIUM',
    'LOW',
    'INCOMPATIBLE',
    '근거가 없고 사용자 확정 ID02와 충돌한다(INCOMPATIBLE).'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G09c',
    'G09',
    'LATENT',
    'SINGLE',
    '한가는 한재욱이 아닌 다른 ''한'' 성 비장 (ID03 확정과 충돌)',
    '처분된 한가는 한재욱이 아닌, 기록되지 않은 다른 ''한'' 성 비장이다. 이 전제(ID03 불성립)는 사용자가 확정한 ID03(한가=한재욱)과 충돌한다.',
    'NONE',
    'HIGH',
    'MEDIUM',
    'LOW',
    'LOW',
    'N/A',
    'MEDIUM',
    '3',
    '한가 ≠ 한재욱 (ID03 불성립); 미기록 인물 존재; 그 인물의 처분 근거 행위',
    'ID03',
    'INCOMPATIBLE',
    'PRUNED (사용자 확정 동일성 ID03과 충돌)',
    NULL,
    NULL,
    NULL,
    'SOURCE_DIRECT',
    '새 인물을 도입해야 하므로 가정 비용이 크다.',
    '(없음 — 위쪽 원인 가설)',
    'EP35 병영 비장 한가 처분',
    '한가는 한재욱이 아닌 다른 ''한'' 성 비장이다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'NONE',
    NULL,
    'NONE',
    'NONE',
    'LOW',
    'LOW',
    'INCOMPATIBLE',
    '근거가 없고 사용자 확정 ID03과 충돌한다(INCOMPATIBLE).'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G10a',
    'G10',
    'LATENT',
    'SINGLE',
    '파직 사유 = 장계와 안핵 결과의 차이',
    '이형원의 5/12 장계가 6/13 안핵 결과와 도난 여부에서 크게 달랐던 것이 파직 사유였다. 유임 사유는 남겨 둔다.',
    'MEDIUM',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'LOW',
    '1',
    '장계 오류가 파직 사유',
    NULL,
    'MEDIUM',
    'KEPT',
    'CF030→CF039 판단 번복, CF049',
    NULL,
    'V3P0152',
    'SOURCE_DIRECT',
    'V3P0152(05: 정조가 도신 장계와 안핵 보고가 현격히 달랐다고 지적)는 audit-only다. 그 지적이 파직 사유라는 문장은 어디에도 없다.',
    'EP25 정조 최종 도난 판단: 실재',
    'EP36 이형원 파직',
    '이형원 파직 사유는 5/12 장계가 6/13 안핵 결과와 도난 여부에서 크게 달랐던 데 있다',
    'PARTIAL',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'MEDIUM',
    'V3P0152',
    'AUDIT_ONLY',
    'MEDIUM',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    '같은 6/13 기사에서 정조가 ''도신 장계와 안핵어사 보고가 도난 여부에서 현격히 달랐다''고 지적했다(05 V3P0152, audit-only). 파직 사유라고 명시한 것은 아니므로 MEDIUM이다. G10은 사용자 검토로 OPEN_UNRESOLVED이며 어느 world에도 쓰지 않는다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G10b',
    'G10',
    'LATENT',
    'SINGLE',
    '유임 사유 = 구휼·전염병 행정 연속성',
    '구휼과 전염병 대응이 진행 중이어서 행정 연속성을 위해 3일 만에 유임했다.',
    'NONE',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'MEDIUM',
    'LOW',
    '2',
    '6월에도 구휼·전염병 행정 부담 지속; 그것이 유임 판단에 쓰임',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    NULL,
    NULL,
    NULL,
    'ENVIRONMENTAL_CONTEXT',
    '환경 피쳐(E002는 1월, E003은 4월)만 근거다. 6월 지속 여부는 pack에 없다. 환경만 근거이므로 LOW 상한이며, 개인 수준 사건이 아닌 판단 사유 가설(individual_level=False)이다.',
    '(없음 — 위쪽 원인 가설)',
    'EP37 6월 16일 이형원 유임',
    '유임 사유는 구휼·전염병 행정의 연속성이었다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'NONE',
    NULL,
    'ENVIRONMENT',
    'NONE',
    'MEDIUM',
    'LOW',
    'LOW',
    '환경 피쳐(E002·E003)만 근거이고 6월 상황을 적은 사료가 없다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G10c',
    'G10',
    'LATENT',
    'SINGLE',
    '파직 → 유임은 처분의 형식적 경감',
    '파직은 문책의 형식이었고 곧바로 유임으로 실무를 이어가게 했다.',
    'NONE',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'N/A',
    'LOW',
    '1',
    '형식적 처분 관행',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    NULL,
    NULL,
    NULL,
    'INSTITUTIONAL_COMPATIBILITY',
    '제도 compatibility(F018 수교)만 근거이므로 LOW 상한.',
    'EP36 이형원 파직',
    'EP37 6월 16일 이형원 유임',
    '파직 → 유임은 처분의 형식적 경감이었다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'NONE',
    NULL,
    'INSTITUTIONAL',
    'NONE',
    'MEDIUM',
    'LOW',
    'LOW',
    '제도상 관행이라는 일반론뿐이다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G11a',
    'G11',
    'LATENT',
    'SINGLE',
    '공주진이 같은 도난 사건으로 먼저 체포',
    '공주진이 같은 도난 사건의 혐의로 변지돌을 2/29 이전에 먼저 체포했다.',
    'LOW',
    'HIGH',
    'HIGH',
    'HIGH',
    'MEDIUM',
    'N/A',
    'LOW',
    '2',
    '같은 사건 혐의; 공주진의 독자 판단',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF011(이미 잡혀간 상태), CF009(변지돌이 체포 대상)',
    NULL,
    NULL,
    'SOURCE_DIRECT',
    NULL,
    '(없음 — 위쪽 원인 가설)',
    'EP05 2월 29일 덕평 체포 활동',
    '공주진이 같은 도난 사건 혐의로 변지돌을 2/29 이전에 먼저 체포했다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'LOW',
    'CF009',
    'CONFIRMED_NON_ENDPOINT',
    'LOW',
    'MEDIUM',
    'MEDIUM',
    'MEDIUM',
    'endpoint가 아닌 CF009(2/28 변지돌 체포 지시)는 변지돌이 이 사건 혐의자였음을 보여 줄 뿐이다. 공주진이 누구 판단으로 왜 잡았는지는 없다. CF011(''이미 잡혀간 상태'')은 endpoint(EP05)다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G11b',
    'G11',
    'LATENT',
    'SINGLE',
    '병영이 2/28 이전 공주진에 체포 의뢰',
    '병영이 2/28 이전에 공주진에 변지돌 체포를 의뢰했다.',
    'NONE',
    'MEDIUM',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    'N/A',
    'MEDIUM',
    '2',
    '병영의 선행 의뢰; 2/28에 이미 의뢰한 사람을 다시 체포 지시',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    NULL,
    'CF009(2/28에 변지돌 체포를 새로 지시 — 의뢰 사실을 몰랐다는 것과 긴장)',
    NULL,
    'SOURCE_DIRECT',
    NULL,
    '(없음 — 위쪽 원인 가설)',
    'EP05 2월 29일 덕평 체포 활동',
    '병영이 2/28 이전 공주진에 변지돌 체포를 의뢰했다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'NONE',
    NULL,
    'NONE',
    'NONE',
    'MEDIUM',
    'LOW',
    'LOW',
    '근거가 없고 CF009(2/28에 새로 체포 지시)와 긴장한다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G11c',
    'G11',
    'LATENT',
    'SINGLE',
    '변지돌은 별건으로 공주진에 구금 중',
    '변지돌은 이 도난과 무관한 별건으로 이미 공주진에 잡혀 있었다.',
    'NONE',
    'HIGH',
    'HIGH',
    'MEDIUM',
    'N/A',
    'N/A',
    'LOW',
    '1',
    '별건 혐의 존재',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    NULL,
    NULL,
    NULL,
    'SOURCE_DIRECT',
    NULL,
    '(없음 — 위쪽 원인 가설)',
    'EP05 2월 29일 덕평 체포 활동',
    '변지돌은 별건으로 공주진에 구금되어 있었다',
    'NO',
    'MEDIUM (진술 기록 endpoint 포함)',
    'NONE',
    NULL,
    'NONE',
    'NONE',
    'MEDIUM',
    'LOW',
    'LOW',
    '근거가 없다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G12a',
    'G12',
    'LATENT',
    'SINGLE',
    '아내도 전염병으로 사망(시점 미상)',
    '김명신의 아내도 같은 시기 전염병에 걸려 죽었다. 감염 경로와 정확한 시점은 남겨 둔다.',
    'LOW',
    'MEDIUM',
    'N/A',
    'N/A',
    'MEDIUM',
    'HIGH',
    'LOW',
    '1',
    '아내의 사망이 남편 사망과 같은 시기(전후 미상)',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF040(정조: 김명신 부처가 전염병으로 죽음)',
    NULL,
    'V3P0025|V3P0123',
    'SOURCE_DIRECT',
    'royal judgment를 event 수준으로 옮긴 최소 후보다. 개인 사건의 근거는 CF040(판단)이며 환경은 environmental_fit에만 쓴다. 이조원(05)은 ''따라 죽었다''고 표현했다.',
    '(없음 — 위쪽 원인 가설)',
    'EP27 정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음',
    '김명신의 아내도 전염병으로 죽었다(사건 수준)',
    'PARTIAL',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'LOW',
    'V3P0025|V3P0123',
    'AUDIT_ONLY|ENDPOINT_ONLY',
    'LOW',
    'MEDIUM',
    'HIGH',
    'MEDIUM',
    '아내의 사망 원인을 적은 것은 endpoint인 정조 판단(CF040, EP27) 자체뿐이다. 이 후보는 그 판단 내용을 사건으로 옮긴 것이라 endpoint 인용을 bridge 근거로 쓸 수 없다(판단 → 사실 전환 금지). 05 이조원 보고는 아내의 사망은 전하지만 원인은 ''따라 죽었다''로 다르다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G12b',
    'G12',
    'LATENT',
    'SINGLE',
    '아내는 남편 사망 뒤 비통 속에 ''따라 죽음''(전염병 아님)',
    '아내는 남편의 죽음 뒤 비통 속에 따라 죽었고, 전염병 때문이 아니었다.',
    'LOW',
    'MEDIUM',
    'N/A',
    'N/A',
    'LOW',
    'MEDIUM',
    'HIGH',
    '1',
    '사망 원인이 전염병이 아님',
    NULL,
    'LOW',
    'KEPT_AS_CONTRAST (관측·최종 판단과 충돌)',
    NULL,
    'CF040(부처 전염병 사망 — royal judgment)',
    'V3P0025|V3P0123',
    'SOURCE_DIRECT',
    NULL,
    '(없음 — 위쪽 원인 가설)',
    'EP27 정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음',
    '아내는 전염병이 아니라 비통 속에 따라 죽었다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'LOW',
    'V3P0025|V3P0123',
    'AUDIT_ONLY',
    'LOW',
    'LOW',
    'LOW',
    'LOW',
    '05 이조원 보고뿐이다. CF040(부처 전염병)과 정면 충돌한다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G13a',
    'G13',
    'LATENT',
    'SINGLE',
    '의금부 구금·신문 실행, 지세 문제는 6/13까지 결론 없음',
    '구순은 의금부에 구금되어 신문을 받았지만, 지세 호칭 문제는 6/13까지 결론이 나지 않았다.',
    'LOW',
    'HIGH',
    'HIGH',
    'HIGH',
    'HIGH',
    'N/A',
    'LOW',
    '2',
    '명령이 실행됨; 신문 결과가 6/13 판단에 쓰임',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    'CF031, CF034, CF045',
    NULL,
    'V3P0137',
    'SOURCE_DIRECT',
    '홍대협이 6/13에 ''지세 실정을 밝히려면 의금부 엄한 국문이 필요하다''고 건의했다(05). 그때까지 결론이 없었음을 시사한다.',
    'EP16 5월 12일 정조 명: 구순 의금부 구금·엄사; EP19 5월 27일 정조 명: 구순 의금부 엄수·반복 신문',
    'EP32 정조: 구순 지세 호칭 날조 죄 불인정',
    '의금부 구금·신문이 실제로 실행되었고, 지세 문제는 6/13까지 결론이 나지 않았다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'LOW',
    'V3P0137',
    'AUDIT_ONLY',
    'LOW',
    'HIGH',
    'MEDIUM',
    'MEDIUM',
    '명령(CF031·CF034)과 6/13 판단(CF045)은 endpoint다. 실행을 적은 사료가 없다. 05 V3P0137(홍대협: 의금부 국문이 필요하다)은 결론이 없었다는 정황일 뿐 실행 근거는 아니다.'
);
INSERT INTO STG_LATENT_CANDIDATES (CANDIDATE_ID, GAP_ID, STATUS, FORM, LABEL, DESCRIPTION, SOURCE_CONSISTENCY, TEMPORAL_FIT, INSTITUTIONAL_FIT, ROLE_FIT, INFORMATION_FLOW_FIT, ENVIRONMENTAL_FIT, CONTRADICTION_RISK, N_ASSUMPTIONS, EXTRA_ASSUMPTIONS, IDENTITY_CONDITIONS, OVERALL, PRUNE_DECISION, SUPPORTS, CONFLICTS, AUDIT_ATTESTATION, SUPPORT_BASIS, NOTES, OBSERVED_LEFT, OBSERVED_RIGHT, LATENT_BRIDGE_CLAIM, BRIDGE_DIRECTLY_ATTESTED, ENDPOINT_SUPPORT, SOURCE_SUPPORT, BRIDGE_EVIDENCE, BRIDGE_BASIS, EVIDENCE_GRADE, PLAUSIBILITY_GRADE, SOURCE_CONSISTENCY_V1, OVERALL_V1, REAUDIT_REASON)
VALUES (
    'G13b',
    'G13',
    'LATENT',
    'SINGLE',
    '의금부 신문은 6/13 이전에 실질적으로 진행되지 않음',
    '구순은 구금되었으나 안핵 결과를 기다리느라 본격 신문은 이루어지지 않았다.',
    'NONE',
    'MEDIUM',
    'MEDIUM',
    'HIGH',
    'MEDIUM',
    'N/A',
    'MEDIUM',
    '1',
    '신문 보류',
    NULL,
    'LOW',
    'KEPT_LOW (사용 시 약점 명시)',
    NULL,
    'CF034(반복 신문하도록 명함)',
    NULL,
    'SOURCE_DIRECT',
    NULL,
    'EP16 5월 12일 정조 명: 구순 의금부 구금·엄사',
    '(없음 — 위쪽 원인 가설)',
    '의금부 신문은 6/13 이전에 실질적으로 진행되지 않았다',
    'NO',
    'HIGH (공식 보고·판단·명령 endpoint)',
    'NONE',
    NULL,
    'NONE',
    'NONE',
    'MEDIUM',
    'LOW',
    'LOW',
    '근거가 없고 CF034(반복 신문 명)와 긴장한다.'
);

-- output/clean/latent_elements.csv (119행)
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G01a_1',
    'G01a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 구순의 소장이 청주 진영에 접수됨'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G01a_2',
    'G01a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 진영이 도적 수사를 병영 비장 쪽에 넘김'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G01a.e1',
    'G01a',
    'edge',
    'LATENT',
    'EP03',
    'LN_G01a_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G01a.e2',
    'G01a',
    'edge',
    'LATENT',
    'LN_G01a_1',
    'LN_G01a_2',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G01a.e3',
    'G01a',
    'edge',
    'LATENT',
    'LN_G01a_2',
    'EP04',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G01b_1',
    'G01b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 구순의 소장이 병영에 직접 접수되고 병영이 체포령 발령'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G01b.e1',
    'G01b',
    'edge',
    'LATENT',
    'EP03',
    'LN_G01b_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G01b.e2',
    'G01b',
    'edge',
    'LATENT',
    'LN_G01b_1',
    'EP04',
    'ORDER_TO_ACTION',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G01c_1',
    'G01c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 소장이 청주목 수령에게 접수'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G01c_2',
    'G01c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 관찰사가 병영에 이첩'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G01c.e1',
    'G01c',
    'edge',
    'LATENT',
    'EP03',
    'LN_G01c_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G01c.e2',
    'G01c',
    'edge',
    'LATENT',
    'LN_G01c_1',
    'LN_G01c_2',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G01c.e3',
    'G01c',
    'edge',
    'LATENT',
    'LN_G01c_2',
    'EP04',
    'ORDER_TO_ACTION',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G02a_1',
    'G02a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 이광섭이 2/28 출동과 철퇴 네 개 제작을 지시'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G02a.e1',
    'G02a',
    'edge',
    'LATENT',
    'LN_G02a_1',
    'EP04',
    'ORDER_TO_ACTION',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G02b_1',
    'G02b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 한재욱이 상위 명령 없이 자체 판단으로 출동 지시'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G02b_2',
    'G02b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 병영 지휘관의 사후 승인·묵인'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G02b.e1',
    'G02b',
    'edge',
    'LATENT',
    'LN_G02b_1',
    'EP04',
    'ORDER_TO_ACTION',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G02b.e2',
    'G02b',
    'edge',
    'LATENT',
    'EP04',
    'LN_G02b_2',
    'REVIEW_OF',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G02c_1',
    'G02c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 이문협이 2/28 출동 직접 지휘'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G02c.e1',
    'G02c',
    'edge',
    'LATENT',
    'LN_G02c_1',
    'EP04',
    'ORDER_TO_ACTION',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G03a_1',
    'G03a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 한재욱이 유제희를 현지 탐문에 파견'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G03a_2',
    'G03a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 유제희 기록이 2/28 이전 한재욱에게 전달'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G03a.e1',
    'G03a',
    'edge',
    'LATENT',
    'LN_G03a_1',
    'EP08',
    'ORDER_TO_ACTION',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G03a.e2',
    'G03a',
    'edge',
    'LATENT',
    'EP08',
    'LN_G03a_2',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G03a.e3',
    'G03a',
    'edge',
    'LATENT',
    'LN_G03a_2',
    'EP04',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G03b_1',
    'G03b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 유제희 기록이 2/29~3/4 사이에 병영에 보고'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G03b.e1',
    'G03b',
    'edge',
    'LATENT',
    'EP08',
    'LN_G03b_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G03b.e2',
    'G03b',
    'edge',
    'LATENT',
    'LN_G03b_1',
    'EP09',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G03c_1',
    'G03c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 유제희 기록이 병사에게 직접 보고'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G03c.e1',
    'G03c',
    'edge',
    'LATENT',
    'EP08',
    'LN_G03c_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G03c.e2',
    'G03c',
    'edge',
    'LATENT',
    'LN_G03c_1',
    'EP09',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G04a_1',
    'G04a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 유제희 기록이 비장 계통을 거쳐 병사에게 보고됨'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G04a.e1',
    'G04a',
    'edge',
    'LATENT',
    'EP08',
    'LN_G04a_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G04a.e2',
    'G04a',
    'edge',
    'LATENT',
    'LN_G04a_1',
    'EP09',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G04b_1',
    'G04b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 자미덕의 대질 진술이 3/4 이전 병사에게 보고됨'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G04b.e1',
    'G04b',
    'edge',
    'LATENT',
    'EP07',
    'LN_G04b_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G04b.e2',
    'G04b',
    'edge',
    'LATENT',
    'LN_G04b_1',
    'EP09',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G04c_1',
    'G04c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 3/4 이전 구순이 병사에게 사적으로 김명신을 의심 대상으로 알림'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G04c.e1',
    'G04c',
    'edge',
    'LATENT',
    'EP01',
    'LN_G04c_1',
    'CONTEXT_SUPPORTS',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G04c.e2',
    'G04c',
    'edge',
    'LATENT',
    'LN_G04c_1',
    'EP09',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G04d_1',
    'G04d',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 석단 공초가 3/4 이전에 병사에게 보고됨'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G04d.e1',
    'G04d',
    'edge',
    'LATENT',
    'LN_G04d_1',
    'EP09',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G04e_1',
    'G04e',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 구순이 장교에게 체포 명령'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G04e.e1',
    'G04e',
    'edge',
    'LATENT',
    'LN_G04e_1',
    'EP11',
    'ORDER_TO_ACTION',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G05a_1',
    'G05a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 조계완이 서찰을 병사에게 전달'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G05a_2',
    'G05a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 서찰 내용 = 체포 지지·의혹 제기'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G05a.e1',
    'G05a',
    'edge',
    'LATENT',
    'EP10',
    'LN_G05a_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G05a.e2',
    'G05a',
    'edge',
    'LATENT',
    'LN_G05a_1',
    'LN_G05a_2',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G05a.e3',
    'G05a',
    'edge',
    'LATENT',
    'LN_G05a_2',
    'EP30',
    'CONTEXT_SUPPORTS',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G05b_1',
    'G05b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 서찰 전달, 내용은 사건 무관'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G05b.e1',
    'G05b',
    'edge',
    'LATENT',
    'EP10',
    'LN_G05b_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G06a_1',
    'G06a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 김명신이 구금 중 발병'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G06a_2',
    'G06a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 보수·구금 상태에서 5/12 이전 사망'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G06a.e1',
    'G06a',
    'edge',
    'LATENT',
    'EP11',
    'LN_G06a_1',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G06a.e2',
    'G06a',
    'edge',
    'LATENT',
    'LN_G06a_1',
    'LN_G06a_2',
    'TEMPORAL_BEFORE',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G06a.e3',
    'G06a',
    'edge',
    'LATENT',
    'LN_G06a_2',
    'EP13',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G06b_1',
    'G06b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 형장 없는 조사 압박'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G06b_2',
    'G06b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 구금 중 발병·사망'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G06b.e1',
    'G06b',
    'edge',
    'LATENT',
    'EP11',
    'LN_G06b_1',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G06b.e2',
    'G06b',
    'edge',
    'LATENT',
    'LN_G06b_1',
    'LN_G06b_2',
    'TEMPORAL_BEFORE',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G06b.e3',
    'G06b',
    'edge',
    'LATENT',
    'LN_G06b_2',
    'EP13',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G06c_1',
    'G06c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 김명신이 구금 중 형장을 받음'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G06c_2',
    'G06c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 쇠약 후 사망'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G06c.e1',
    'G06c',
    'edge',
    'LATENT',
    'EP11',
    'LN_G06c_1',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G06c.e2',
    'G06c',
    'edge',
    'LATENT',
    'LN_G06c_1',
    'LN_G06c_2',
    'TEMPORAL_BEFORE',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G06c.e3',
    'G06c',
    'edge',
    'LATENT',
    'LN_G06c_2',
    'EP13',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G06c.e4',
    'G06c',
    'edge',
    'LATENT',
    'LN_G06c_1',
    'EP27',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G07a_1',
    'G07a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 장물 부재 → 도난 부재 추론'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G07a.e1',
    'G07a',
    'edge',
    'LATENT',
    'EP13',
    'LN_G07a_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G07a.e2',
    'G07a',
    'edge',
    'LATENT',
    'LN_G07a_1',
    'EP15',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G07b_1',
    'G07b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 회동 조사 응답자 진술이 장계에 반영'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G07b.e1',
    'G07b',
    'edge',
    'LATENT',
    'LN_G07b_1',
    'EP13',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G07b.e2',
    'G07b',
    'edge',
    'LATENT',
    'LN_G07b_1',
    'EP15',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G07c_1',
    'G07c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 명업 등의 번복 진술이 5월 판단 자료에 포함'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G07c.e1',
    'G07c',
    'edge',
    'LATENT',
    'LN_G07c_1',
    'EP13',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G07d_1',
    'G07d',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 도난 부재·구순이 상황을 꾸밈'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G07d.e1',
    'G07d',
    'edge',
    'LATENT',
    'LN_G07d_1',
    'EP15',
    'CONTEXT_SUPPORTS',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G07d.e2',
    'G07d',
    'edge',
    'LATENT',
    'LN_G07d_1',
    'EP25',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G08a_1',
    'G08a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 정조가 이조원 서계의 직접 안핵 부재를 근거로 현지 직접 안핵이 필요하다고 판단'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G08a.e1',
    'G08a',
    'edge',
    'LATENT',
    'EP18',
    'LN_G08a_1',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G08a.e2',
    'G08a',
    'edge',
    'LATENT',
    'LN_G08a_1',
    'EP20',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G08b_1',
    'G08b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 정조의 지세 호칭 의문'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G08b.e1',
    'G08b',
    'edge',
    'LATENT',
    'LN_G08b_1',
    'EP20',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G09a_1',
    'G09a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 한가(=한재욱) 처분 근거 = 자미덕이 진술한 회유·대질 지휘와 출동 운영'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G09a.e1',
    'G09a',
    'edge',
    'LATENT',
    'EP07',
    'LN_G09a_1',
    'RESPONSIBILITY_LINK',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G09a.e2',
    'G09a',
    'edge',
    'LATENT',
    'EP04',
    'LN_G09a_1',
    'RESPONSIBILITY_LINK',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G09a.e3',
    'G09a',
    'edge',
    'LATENT',
    'LN_G09a_1',
    'EP35',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G09b_1',
    'G09b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 자미덕 진술 속 ''한 비장''은 별도의 ''한'' 성 비장'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G09b_2',
    'G09b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 한가 처분 근거 = 출동·철편 운영'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G09b.e1',
    'G09b',
    'edge',
    'LATENT',
    'EP07',
    'LN_G09b_1',
    'CONTEXT_SUPPORTS',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G09b.e2',
    'G09b',
    'edge',
    'LATENT',
    'EP04',
    'LN_G09b_2',
    'RESPONSIBILITY_LINK',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G09b.e3',
    'G09b',
    'edge',
    'LATENT',
    'LN_G09b_2',
    'EP35',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G09c_1',
    'G09c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 기록되지 않은 다른 ''한'' 성 비장'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G09c.e1',
    'G09c',
    'edge',
    'LATENT',
    'LN_G09c_1',
    'EP35',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G10a_1',
    'G10a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 파직 사유 = 장계 판단 오류'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G10a.e1',
    'G10a',
    'edge',
    'LATENT',
    'EP25',
    'LN_G10a_1',
    'REVIEW_OF',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G10a.e2',
    'G10a',
    'edge',
    'LATENT',
    'LN_G10a_1',
    'EP36',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G10b_1',
    'G10b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 유임 사유 = 행정 연속성'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G10b.e1',
    'G10b',
    'edge',
    'LATENT',
    'LN_G10b_1',
    'EP37',
    'CONTEXT_SUPPORTS',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G10c_1',
    'G10c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 형식적 파직 후 유임'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G10c.e1',
    'G10c',
    'edge',
    'LATENT',
    'EP36',
    'LN_G10c_1',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G10c.e2',
    'G10c',
    'edge',
    'LATENT',
    'LN_G10c_1',
    'EP37',
    'PROCEDURAL_NEXT',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G11a_1',
    'G11a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 공주진의 변지돌 선행 체포(같은 사건)'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G11a.e1',
    'G11a',
    'edge',
    'LATENT',
    'LN_G11a_1',
    'EP05',
    'TEMPORAL_BEFORE',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G11b_1',
    'G11b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 병영→공주진 체포 의뢰'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G11b.e1',
    'G11b',
    'edge',
    'LATENT',
    'LN_G11b_1',
    'EP05',
    'TEMPORAL_BEFORE',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G11c_1',
    'G11c',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 변지돌 별건 구금'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G11c.e1',
    'G11c',
    'edge',
    'LATENT',
    'LN_G11c_1',
    'EP05',
    'TEMPORAL_BEFORE',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G12a_1',
    'G12a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 김명신 아내의 전염병 사망'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G12a.e1',
    'G12a',
    'edge',
    'LATENT',
    'LN_G12a_1',
    'EP27',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G12b_1',
    'G12b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 아내의 비전염병 사망'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G12b.e1',
    'G12b',
    'edge',
    'LATENT',
    'LN_G12b_1',
    'EP27',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G13a_1',
    'G13a',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 구순 의금부 구금·신문 실행'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G13a.e1',
    'G13a',
    'edge',
    'LATENT',
    'EP16',
    'LN_G13a_1',
    'ORDER_TO_ACTION',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G13a.e2',
    'G13a',
    'edge',
    'LATENT',
    'EP19',
    'LN_G13a_1',
    'ORDER_TO_ACTION',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G13a.e3',
    'G13a',
    'edge',
    'LATENT',
    'LN_G13a_1',
    'EP32',
    'INFORMATION_FLOW',
    NULL
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'LN_G13b_1',
    'G13b',
    'node',
    'LATENT',
    NULL,
    NULL,
    NULL,
    '[LATENT] 의금부 구금만 되고 신문은 보류'
);
INSERT INTO STG_LATENT_ELEMENTS (ELEMENT_ID, CANDIDATE_ID, KIND, STATUS, SRC, DST, EDGE_TYPE, TEXT)
VALUES (
    'G13b.e1',
    'G13b',
    'edge',
    'LATENT',
    'EP16',
    'LN_G13b_1',
    'ORDER_TO_ACTION',
    NULL
);

-- output/clean/narrative_worlds.csv (6행)
INSERT INTO STG_NARRATIVE_WORLDS (WORLD_ID, NAME, STATUS, LATENT_BRIDGES, UNRESOLVED_GAPS, INSTITUTIONAL_FIT, ENVIRONMENTAL_FIT, N_ASSUMPTIONS, MIN_GRADE, MAIN_ASSUMPTIONS, MAIN_WEAKNESSES, CONTRADICTED_EVIDENCE, STORY_IMPLICATION, IDENTITY_CONDITIONS, RESOLVED_IDENTITIES, EVIDENCE_PROFILE, WORK_ROLE, STORY_QUESTION, DIFFERENCE, UNIQUE_BRIDGES, NARRATIVE)
VALUES (
    'W1',
    '공식 정보 경로 (정조 최종 판단과 정합)',
    'COMPETING_EXPLANATION',
    'G01a|G02a|G03a|G04a|G05a|G06a|G07a|G08a|G09a|G11a|G12a|G13a',
    'G10',
    'MEDIUM',
    'HIGH',
    '20',
    'LOW',
    '소장이 청주 진영에 접수되어 병영 비장 쪽으로 넘어감(G01a) / 이광섭이 출동·철퇴 제작을 지시하고 한재욱이 전달(G02a, ID07 조건) / 유제희 기록이 2/28 이전 한재욱에게, 이후 비장 계통을 거쳐 병사에게 올라감(G03a·G04a) / 구순 서찰이 병사에게 전달되어 체포를 지지함(G05a) / 김명신은 구금 중 발병해 5/12 이전 사망, '
        || '처우는 CF041 판단을 따름(G06a) / 미확정 동일성 조건: ID06, ID07 (확정하지 않음)',
    'bridge 12개로 가장 많이 채운 world다. 추가 가정 합계가 가장 크다. / 미확정 동일성 2개(ID06·ID07)를 조건으로 깐다. 하나라도 불성립이면 해당 구간이 끊긴다(ID01·ID02·ID03·ID05·ID11은 사용자 확정). / 유제희 기록이 2/28 이전이었다면 풍각 김생원 체포가 왜 3/4로 늦었는지 설명하지 못한다(G03a). / '
        || '정조의 ''구순이 성명을 적어 주었다''(CF043)와 유제희의 ''자신이 기록했다''(CF020)의 claim-level 차이를 해소하지 않은 채 둘 다 쓴다. / 재감사: bridge 자체의 사료 근거가 LOW·NONE인 후보 — G05a(LOW), G07a(LOW), G08a(LOW), G09a(LOW), G11a(LOW), G12a(LOW), G13a(LO'
        || 'W). 이 부분은 양끝 사실이 확실해도 연결 자체는 추정이다.',
    '직접 충돌하는 confirmed fact 없음. 긴장: CF027(''달포 이상 구금·조사'') ↔ G06a가 따르는 CF041(''평범한 신문도 받지 않았다'') — PARTIAL. CF018(한재욱의 ''은밀한 사주'' 부인) ↔ G09a의 회유 근거 — claim-level(ID02 확정: 같은 인물에 대한 서로 다른 진술).',
    '구순의 사적 갈등이 ''의혹 정보''로 공식 수사 경로(진영 → 병영 비장 → 병영 지휘)에 들어갔고, 병영은 장물 없이 체포·구금을 진행했다. 김명신은 구금 중 병으로 죽었다. 정조의 최종 판단(도난 실재, 전염병 사망, 직접 인과 불확실, 그런데도 구순과 이광섭의 책임)과 가장 넓게 정합하는 경로지만, 그만큼 가정이 많다.',
    'ID06|ID07',
    'ID01|ID02|ID03|ID05|ID11',
    'MEDIUM 5 / LOW 7',
    '정조의 최종 책임 판단(CF043·CF044)과 가장 가까운 방향으로 중간 경로를 재구성한 버전. ''정조가 왜 이런 사람들에게 책임을 물었는가''를 가장 적극적으로 설명한다. 가장 참인 world라는 뜻은 아니다.',
    '정조는 어떤 책임 구조를 보고 처분했는가?',
    '빈칸 12개를 공식 정보 경로(진영 → 병영 비장 → 병사)로 가장 많이 채운다. 구순의 의혹 발언이 비장 계통을 거쳐 병사에게 보고되었다는 G04a를 이 world만 쓴다.',
    'G04a',
    TO_CLOB('명업은 김명신이 2월 초순 박거사 일로 구순에게 편지를 보내 힐책했고 그 뒤 왕래가 끊겼다고 진술했다. 명업은 또 나복이 2월 22일 밤 도적이 들었다고 알렸고, 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다. [L] 소장은 청주 진영에 접수되었고 진영은 수사를 병영 비장 쪽에 넘겼다(G01a). [L] 이광섭이 출동과 철퇴 제작을 지시하고 한재욱이 ')
        || TO_CLOB('이를 전달했다. 철퇴와 철편이 같은 물건일 때(ID07)만 성립한다(G02a). [L] 그보다 앞서 한재욱이 보낸 유제희의 탐문 기록이 한재욱에게 올라가 있었다. 기록 속 원돌은 정원돌이다(ID11, 사용자 확정)(G03a). 이진욱은 2월 28일 밤 한재욱이 덕평 출동과 변지돌·정원돌 체포를 지시하고 철편 네 개를 만들어 주었다고 진술했다. [L] 변지돌')
        || TO_CLOB('은 공주진이 같은 사건으로 먼저 잡아갔다(G11a). 자미덕은 병영에 끌려가 한 차례 신문받고 구류되었으며, 한 비장이 정원돌 등을 큰 도적이라고 말하면 다음 날 석방하겠다고 말했고 대질 때 그 지휘에 따라 거짓으로 꾸며 말했다고 진술했다. [L] 유제희 기록 속 ''풍각 김상제도 극히 수상하다''는 구순의 말이 비장 계통을 거쳐 병사에게 보고되었다. 김상제는')
        || TO_CLOB(' 김명신이다(ID05, 사용자 확정)(G04a). 이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원(사료 식별: 김명신·김갑득)을 잡아오라고 지시했고 장교 일행이 그 분부에 따라 잡아왔다고 진술했다. 조계완은 잡으러 가는 길에 구순에게서 병사에게 전할 서찰을 받았다고 진술했다. [L] 그 서찰은 병사에게 전달되었고 체포를 지지하는 내용이었다. 병사는 이')
        || TO_CLOB('광섭이다(ID01, 사용자 확정)(G05a). [L] 김명신은 구금 중 병이 났고 5월 12일 보고 이전에 죽었다(G06a). 윤노동 별단은 김명신이 보수·구금 중 병들어 죽었다고 보고했다. 5월 12일 이형원 장계(달포 이상 구금·조사, 확실한 장물 없음, 사망)를 받은 정조는 도난 자체가 없었다는 방향을 받아들였다. [L] 그 방향은 장물 미발견에서 나')
        || TO_CLOB('온 추론이었다(G07a). [L] 의금부에서 구순 신문이 실행되었으나 지세 호칭 문제는 결론이 나지 않았다(G13a). [L] 정조는 이조원이 직접 안핵하지 않은 점을 문제 삼은 다음 날 홍대협을 안핵어사로 보냈다(G08a). 6월 13일 홍대협은 약간의 실제 도난이 있었으나 보통 좀도둑 수준이라고 판단했고 김명신의 죽음을 질병 때문이라고 평가했다. 정조는')
        || TO_CLOB(' 도난 실재, 부처의 전염병 사망, 곤장·평문 없음, 직접 인과는 십분 확실하지 않음을 판단하면서도 구순과 이광섭의 책임이 크게 다르지 않다고 판단했다. [L] 김명신의 아내도 전염병으로 죽었다(G12a). 한 비장과 한가는 한재욱이다(ID02·ID03, 사용자 확정). [L] 한가 처분의 근거는 자미덕이 진술한 회유·대질 지휘와 출동 운영이다(G09a).')
        || TO_CLOB(' 회유는 자미덕의 진술이며 한재욱은 은밀한 사주를 부인했다.')
);
INSERT INTO STG_NARRATIVE_WORLDS (WORLD_ID, NAME, STATUS, LATENT_BRIDGES, UNRESOLVED_GAPS, INSTITUTIONAL_FIT, ENVIRONMENTAL_FIT, N_ASSUMPTIONS, MIN_GRADE, MAIN_ASSUMPTIONS, MAIN_WEAKNESSES, CONTRADICTED_EVIDENCE, STORY_IMPLICATION, IDENTITY_CONDITIONS, RESOLVED_IDENTITIES, EVIDENCE_PROFILE, WORK_ROLE, STORY_QUESTION, DIFFERENCE, UNIQUE_BRIDGES, NARRATIVE)
VALUES (
    'W2',
    '대질 진술 증폭 경로 (구류·회유 진술이 체포를 넓힘)',
    'COMPETING_EXPLANATION',
    'G01a|G02b|G03a|G04b|G06b|G07c|G08a|G09a|G12a',
    'G05|G10|G11|G13',
    'MEDIUM',
    'HIGH',
    '18',
    'LOW',
    '한재욱이 상위 명령 없이 출동을 지시하고 병영 지휘관은 사후 승인·묵인(G02b) / 유제희의 초기 기록이 2/28 이전 한재욱에게 올라감(G03a) / 자미덕의 대질 진술이 3/4 이전 병사에게 보고되어 체포 근거가 됨(G04b) / 구금 중 형장 없는 조사 압박 뒤 발병·사망(G06b) / 명업 등의 번복 진술이 5월 판단 자료에 들어감(G07c)',
    'G06b는 정조의 CF041 판단(''평범한 신문도 받지 않았다'')과 긴장한다. / 열린 목록 ''등''에 풍각 김생원이 들어 있었다는 가정은 05의 윤노동 주장(audit-only)에만 흔적이 있다. / G04b의 시간 창(2/29 자미덕 체포 ~ 3/4 지시)이 4일뿐이다. / G09a의 처분 근거(회유·대질 지휘)는 자미덕 진술에 기대며, 한재욱은 은밀한 '
        || '사주를 부인했다(CF018). / 재감사: bridge 자체의 사료 근거가 LOW·NONE인 후보 — G02b(LOW), G04b(LOW), G06b(LOW), G07c(LOW), G08a(LOW), G09a(LOW), G12a(LOW). 이 부분은 양끝 사실이 확실해도 연결 자체는 추정이다.',
    '직접 충돌하는 confirmed fact 없음. 긴장: CF041(royal judgment: 평범한 신문 없음) ↔ G06b. CF018(은밀한 사주 부인) ↔ G04b·G09a — claim-level(ID02 확정: 같은 인물에 대한 서로 다른 진술).',
    '사건의 추진력을 구류·회유·대질 진술(자미덕의 진술)에서 찾는다. 유제희의 초기 명단이 자미덕의 대질 진술로 넓어져 3/4 김생원 체포로 이어지고, 5월의 도난 부재 방향은 구순 집 사람들의 번복 진술에서 나온다. 정조의 처우 판단(CF041)과는 긴장 관계에 있다.',
    NULL,
    'ID02|ID03|ID11',
    'MEDIUM 2 / LOW 7',
    '자미덕의 구류·대질 진술이 수사 확대에 영향을 주었다고 보는 버전. 증언이 수사 방향을 어떻게 키웠을 수 있는지 보여 준다.',
    '자미덕의 진술은 수사를 얼마나 확대시켰을 수 있는가?',
    '체포 근거를 대질 진술(G04b)에서, 5월 판단을 구순 집 사람들의 진술 번복(G07c)에서 찾는다. 구금 경과는 형장 없는 조사 압박(G06b)으로 본다. 세 가설 모두 이 world만 쓴다.',
    'G04b|G06b|G07c',
    TO_CLOB('명업은 김명신과 구순의 왕래가 힐책 뒤 끊겼고, 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다. [L] 소장은 청주 진영에 접수되었고 진영은 수사를 병영 비장 쪽에 넘겼다(G01a). [L] 한재욱은 위에서 구체적 명령을 받지 않고 2월 28일 출동을 지시했고 병영 지휘관은 나중에 묵인했다(G02b). [L] 유제희의 초기 기록이 2월 28일 이전 한')
        || TO_CLOB('재욱에게 올라가 있었다. 원돌은 정원돌이다(ID11, 사용자 확정)(G03a). 이진욱은 한재욱이 변지돌·정원돌 체포를 지시했고, 2월 29일 변지돌은 이미 공주진에 잡혀가 장교 일행이 자미덕을 붙잡았다고 진술했다. 자미덕은 한 비장이 정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적이라고 말하면 석방하겠다고 했고, 대질 때 그 지휘에 따라 거짓으로 꾸며 ')
        || TO_CLOB('말했다고 진술했다. 한재욱은 자미덕에게 남은 밥을 준 사실은 인정했지만 은밀히 사주한 일은 없다고 진술했다. 한 비장은 한재욱이므로(ID02, 사용자 확정) 두 진술은 같은 인물에 대한 서로 다른 진술이며, 어느 쪽도 사실로 확정하지 않는다. [L] 자미덕의 대질 진술이 3월 4일 이전 병사에게 보고되어 김생원 체포 지시의 근거가 되었다(G04b). 이진욱')
        || TO_CLOB('은 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했고 장교 일행이 그 분부에 따라 김명신과 김갑득을 잡아왔다고 진술했다. [L] 김명신은 구금 중 형장은 받지 않았으나 반복 조사 압박을 받았고 이어 발병해 죽었다(G06b). 정조의 ''평범한 신문도 받지 않았다''는 판단과 긴장한다. [L] 명업 등이 병영에서 ''도적이 없었다''는 취지로 진술을')
        || TO_CLOB(' 바꾸었고 그 번복이 5월 판단 자료에 들어갔다(G07c). 5월 12일 정조는 장계와 조사에 따라 도난 자체가 없었다는 방향을 받아들였다. [L] 정조는 이조원의 전문 의존을 문제 삼은 다음 날 홍대협을 보냈다(G08a). 6월 13일 홍대협은 약간의 실제 도난을 판단하고 김명신의 죽음을 질병 때문이라고 평가했으며, 정조는 도난 실재와 부처의 전염병 사망')
        || TO_CLOB('을 판단했다. [L] 김명신의 아내도 전염병으로 죽었다(G12a). 한 비장과 한가는 한재욱이다(ID02·ID03, 사용자 확정). [L] 한가 처분의 근거는 자미덕이 진술한 회유·대질 지휘와 출동 운영이다(G09a). 회유는 자미덕의 진술이며 한재욱은 은밀한 사주를 부인했다.')
);
INSERT INTO STG_NARRATIVE_WORLDS (WORLD_ID, NAME, STATUS, LATENT_BRIDGES, UNRESOLVED_GAPS, INSTITUTIONAL_FIT, ENVIRONMENTAL_FIT, N_ASSUMPTIONS, MIN_GRADE, MAIN_ASSUMPTIONS, MAIN_WEAKNESSES, CONTRADICTED_EVIDENCE, STORY_IMPLICATION, IDENTITY_CONDITIONS, RESOLVED_IDENTITIES, EVIDENCE_PROFILE, WORK_ROLE, STORY_QUESTION, DIFFERENCE, UNIQUE_BRIDGES, NARRATIVE)
VALUES (
    'W3',
    '사적 후원 경로 (구순 ↔ 병영 지휘관, 약함)',
    'COMPETING_EXPLANATION',
    'G01b|G02a|G04c|G05a|G06a|G07a|G08a|G12a',
    'G03|G09|G10|G11|G13',
    'LOW',
    'HIGH',
    '11',
    'LOW',
    '소장이 병영에 직접 접수(G01b) / 3/4 이전 구순이 병사에게 사적으로 김명신을 의심 대상으로 알림(G04c) / 3/4 서찰이 전달되어 체포를 지지(G05a) / 철퇴 = 철편(ID07). 병사 = 이광섭은 ID01 사용자 확정 / 미확정 동일성 조건: ID07 (확정하지 않음)',
    'LOW bridge(G04c)에 기댄다. 3/4 이전 접촉을 보여 주는 confirmed fact가 없고, 05 흔적(V3P0053·V3P0148)도 audit-only다. 경쟁 설명 world 가운데 가장 약하다. / G01b는 CF026(진영 영장 이문협의 위임·방관 평가)을 설명하지 못한다. / 구순은 공식 지휘권이 없으므로 이 경로는 정보 제공일 뿐'
        || ' 명령 경로가 아니다. 체포 지시의 공식 주체는 여전히 병사다(CF023). / 미확정 동일성 ID07에 기댄다(ID01은 사용자 확정). / 재감사: bridge 자체의 사료 근거가 LOW·NONE인 후보 — G01b(NONE), G04c(LOW), G05a(LOW), G07a(LOW), G08a(LOW), G12a(LOW). 이 부분은 양끝 사실이 확실'
        || '해도 연결 자체는 추정이다.',
    '직접 충돌하는 confirmed fact 없음. 약한 반증: CF026(진영 영장이 수사를 병영 비장에게 맡김)은 병영 직접 접수(G01b)와 잘 맞지 않는다.',
    '구순과 병영 지휘관 사이의 사적 통로(3/4 이전 접촉과 3/4 서찰)를 사건의 축으로 본다. 정조가 이광섭이 ''구순 편을 들었다''고 한 판단을 가장 직접적으로 풀어 쓰지만, 핵심 bridge가 LOW라서 경쟁 설명 world 가운데 가장 약하다.',
    'ID07',
    'ID01',
    'MEDIUM 2 / LOW 5 / NONE 1',
    '구순과 병영 사이에 사료에 기록되지 않은 사적 통로가 있었을 가능성을 시험하는 버전. 핵심 bridge의 근거가 약하다(G04c LOW, G01b NONE).',
    '구순의 사적 영향력이 별도로 작동했을 가능성이 있는가?',
    '소장의 병영 직접 접수(G01b)와 3/4 이전 사적 접촉(G04c)을 이 world만 쓴다. 공식 정보 경로(G03·G04a)는 쓰지 않는다.',
    'G01b|G04c',
    TO_CLOB('명업은 김명신이 구순을 힐책한 뒤 왕래가 끊겼고, 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다. [L] 소장은 병영에 직접 접수되었고 병영이 체포령을 내렸다(G01b). [L] 이광섭이 출동과 철퇴 제작을 지시했다. 철퇴와 철편이 같은 물건일 때(ID07)만 성립한다(G02a). 이진욱은 2월 28일 밤 한재욱이 덕평 출동을 지시하고 철편 네 개를 ')
        || TO_CLOB('만들어 주었다고 진술했다. [L] 3월 4일 이전 구순이 병사에게 사적으로 김명신을 의심 대상으로 알렸다(G04c, LOW). 공식 명령이 아니라 정보 제공이다. 이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했다고 진술했다. 조계완은 김명신을 잡으러 가는 길에 구순이 ''이제 도적 다스리는 일이 바른 길을 얻었다''는 취지로 말하고 병')
        || TO_CLOB('사에게 전할 서찰을 건넸다고 진술했다. [L] 서찰은 병사에게 전달되었고 체포를 지지했다. 병사는 이광섭이다(ID01, 사용자 확정)(G05a). [L] 김명신은 구금 중 발병해 5월 12일 보고 이전에 죽었다(G06a). [L] 5월의 도난 부재 방향은 장물 미발견에서 나온 추론이었다(G07a). [L] 정조는 이조원 비판 다음 날 홍대협을 보냈다(G08')
        || TO_CLOB('a). 6월 13일 정조는 이광섭이 구순 편을 들었다고 비판하고 구순과 이광섭의 책임이 크게 다르지 않다고 판단했다. [L] 김명신의 아내도 전염병으로 죽었다(G12a).')
);
INSERT INTO STG_NARRATIVE_WORLDS (WORLD_ID, NAME, STATUS, LATENT_BRIDGES, UNRESOLVED_GAPS, INSTITUTIONAL_FIT, ENVIRONMENTAL_FIT, N_ASSUMPTIONS, MIN_GRADE, MAIN_ASSUMPTIONS, MAIN_WEAKNESSES, CONTRADICTED_EVIDENCE, STORY_IMPLICATION, IDENTITY_CONDITIONS, RESOLVED_IDENTITIES, EVIDENCE_PROFILE, WORK_ROLE, STORY_QUESTION, DIFFERENCE, UNIQUE_BRIDGES, NARRATIVE)
VALUES (
    'W4',
    '분산 지휘 (단일 명령 계통 없음)',
    'COMPETING_EXPLANATION',
    'G01a|G02b|G03c|G06a|G07b|G08b|G11a|G13a',
    'G04|G05|G09|G10|G12',
    'MEDIUM',
    'HIGH',
    '14',
    'LOW',
    '진영 → 병영 비장 이관(G01a) / 비장의 자체 판단 출동과 병영 지휘관의 사후 묵인(G02b) / 유제희가 비장을 건너뛰고 병사에게 직접 보고(G03c) / 5월 판단은 회동 조사 응답자 진술을 채택(G07b) / 홍대협 차하의 주목적은 지세 의문(G08b)',
    'G03c는 LOW이며 05 V3P0085(한재욱이 유제희를 내보냈다는 공초, audit-only)와 긴장한다. / G08b의 ''주목적''은 정조가 세 의안을 나누었다는 05 기록(V3P0103)에 비추어 과장일 수 있다. / G07b의 근거(회동 조사 응답)는 05에만 있는 중첩 진술이다. / G04(구순 발언 → 3/4 지시)를 비워 두므로 정조의 구순 책'
        || '임 사슬(CF043)을 event 수준으로 설명하지 못한다. / 재감사: bridge 자체의 사료 근거가 LOW·NONE인 후보 — G02b(LOW), G03c(NONE), G08b(LOW), G11a(LOW), G13a(LOW). 이 부분은 양끝 사실이 확실해도 연결 자체는 추정이다.',
    '직접 충돌하는 confirmed fact 없음. 긴장: 05 V3P0085(audit-only) ↔ G03c.',
    '명확한 단일 명령 계통 없이 여러 행위자가 각자 움직인 경로다. 비장은 자체 판단으로 출동을 지시했고, 유제희는 비장을 건너뛰어 병사에게 직접 보고했으며, 공주진은 독자적으로 변지돌을 잡았다. 정조의 ''비장에게 일을 맡겼다''(CF044)와 이형원의 ''방관''(CF026) 평가를 지휘 공백으로 읽는다.',
    NULL,
    'ID01|ID05',
    'MEDIUM 3 / LOW 4 / NONE 1',
    '하나의 중앙 지휘 경로가 아니라 여러 기관·실무자가 분산적으로 움직였다고 보는 버전. 사건이 한 사람의 설계가 아니라 기관별 판단의 누적으로 커졌을 가능성을 보여 준다.',
    '한 명의 지휘자가 아니라 여러 기관의 판단 누적이 사건을 키웠는가?',
    '유제희의 병사 직보(G03c), 회동 조사 진술 채택(G07b), 지세 의문이 차하의 주목적(G08b)을 이 world만 쓴다. 구순 발언 → 3/4 지시 경로(G04)는 비워 둔다.',
    'G03c|G07b|G08b',
    TO_CLOB('명업은 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다. [L] 소장은 청주 진영에 접수되었고 진영은 수사를 병영 비장 쪽에 넘겼다(G01a). 이형원은 영장 이문협이 수사를 병영 비장에게 전적으로 맡기고 방관했다고 평가했다. [L] 한재욱은 위의 구체적 명령 없이 2월 28일 출동을 지시했고 병영 지휘관은 나중에 묵인했다(G02b). 이진욱은 한재욱이')
        || TO_CLOB(' 덕평 출동과 체포를 지시했다고 진술했다. [L] 변지돌은 공주진이 독자 판단으로 먼저 잡아갔다(G11a). 유제희는 현지 탐문 중 구순이 ''풍각 김상제도 극히 수상하다''고 말했고 자신이 그 말을 원돌 등의 이름과 함께 기록해 올렸다고 진술했다. [L] 유제희는 그 기록을 비장을 건너뛰고 병사에게 직접 올렸다. 김상제는 김명신이다(ID05, 사용자 확정)(')
        || TO_CLOB('G03c, LOW). 이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했다고 진술했다. [L] 김명신은 구금 중 발병해 5월 12일 보고 이전에 죽었다(G06a). [L] 5월 12일 판단은 회동 조사 응답자들이 ''구순이 도난 상황을 꾸몄다''고 한 진술을 채택한 것이었다(G07b). 응답 내용의 진위는 다루지 않는다. [L] 의금부에서')
        || TO_CLOB(' 구순 신문이 실행되었으나 지세 문제는 결론이 나지 않았다(G13a). [L] 정조가 홍대협을 보낸 주목적은 지세 호칭의 출처를 밝히는 것이었다(G08b). 6월 13일 정조는 이광섭이 아전들의 거짓을 제대로 살피지 않은 채 비장에게 일을 맡겼다고 비판했다. 공초의 병사는 이광섭이다(ID01, 사용자 확정).')
);
INSERT INTO STG_NARRATIVE_WORLDS (WORLD_ID, NAME, STATUS, LATENT_BRIDGES, UNRESOLVED_GAPS, INSTITUTIONAL_FIT, ENVIRONMENTAL_FIT, N_ASSUMPTIONS, MIN_GRADE, MAIN_ASSUMPTIONS, MAIN_WEAKNESSES, CONTRADICTED_EVIDENCE, STORY_IMPLICATION, IDENTITY_CONDITIONS, RESOLVED_IDENTITIES, EVIDENCE_PROFILE, WORK_ROLE, STORY_QUESTION, DIFFERENCE, UNIQUE_BRIDGES, NARRATIVE)
VALUES (
    'W5',
    '최소 가정 (추가 가정 수가 가장 적은 world)',
    'COMPETING_EXPLANATION',
    'G01a|G06a|G07a|G08a',
    'G02|G03|G04|G05|G09|G10|G11|G12|G13',
    'HIGH',
    'HIGH',
    '5',
    'LOW',
    '소장 접수처 = 청주 진영, 2/28 이전 병영 비장 쪽 이관(G01a) / 김명신의 발병은 체포 이후(G06a) / 장물 부재가 5월 도난 부재 추론의 근거(G07a) / 5/27 비판이 5/28 차하의 동기(G08a)',
    '사건의 핵심 정보 경로(G03·G04·G05)를 비워 두므로 정조의 구순 책임 판단(CF043)이 event 수준에서 어떻게 성립하는지 말하지 못한다. / 설명력은 가장 낮고, 가정 비용도 가장 낮다. / LATENT 재감사 뒤 W5는 더 이상 ''HIGH 후보만 쓴 world''가 아니다. 네 bridge 중 G01a·G06a는 MEDIUM, G07a·G08'
        || 'a는 LOW다. G07a·G08a는 두 관측 사실 사이의 이유·동기만 추정한 bridge이고, 그 이유·동기를 적은 사료가 없다. 참고로 G07에서는 G07b(MEDIUM)의 근거 등급이 G07a(LOW)보다 높지만, world 구성은 바꾸지 않았다. / 재감사: bridge 자체의 사료 근거가 LOW·NONE인 후보 — G07a(LOW), G08a(LOW'
        || '). 이 부분은 양끝 사실이 확실해도 연결 자체는 추정이다.',
    '직접 충돌하는 confirmed fact 없음. 긴장: CF027(''구금·조사'') ↔ G06a가 따르는 CF041(평문 없음) — PARTIAL.',
    '추가 가정이 가장 적은 bridge 4개만 얹고 나머지 gap은 비워 둔 world다. 소장 → 진영 → 병영 비장 이관(MEDIUM), 구금 중 발병·사망(MEDIUM), 장물 미발견에서 나온 5월 도난 부재 판단(LOW), 이조원 비판 뒤 독립 안핵(LOW)이라는 네 다리만 놓는다. 구순의 말이 어떻게 3/4 체포 지시에 닿았는지는 미해결로 남긴다.',
    NULL,
    NULL,
    'MEDIUM 2 / LOW 2',
    '최소가정 버전. 사료에 없는 중간 과정을 최대한 채우지 않고 확정 사실 사이의 빈칸을 가능한 한 그대로 둔다.',
    '사료에 없는 것을 거의 채우지 않으면 무엇만 남는가?',
    '고유한 bridge가 없다. 다른 world와 공유하는 bridge 4개(G01a·G06a·G07a·G08a)만 쓰고 나머지 9개 gap은 비워 둔다.',
    NULL,
    TO_CLOB('명업은 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다. [L] 소장은 청주 진영에 접수되었고 진영은 수사를 병영 비장 쪽에 넘겼다(G01a). 이진욱은 2월 28일 밤 한재욱이 덕평 출동을 지시했고, 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시해 장교 일행이 잡아왔다고 진술했다. 유제희의 기록이 그 지시에 어떻게 닿았는지는 비워 둔다')
        || TO_CLOB('(G03·G04 미해결). [L] 김명신은 구금 중 발병해 5월 12일 보고 이전에 죽었다(G06a). [L] 5월 12일 정조가 받아들인 도난 부재 방향은 장물 미발견에서 나온 추론이었다(G07a). [L] 정조는 이조원이 직접 안핵하지 않은 점을 문제 삼은 다음 날 홍대협을 보냈다(G08a). 6월 13일 정조는 도난 실재와 부처의 전염병 사망을 판단했')
        || TO_CLOB('고, 직접 인과는 십분 확실하지 않다고 하면서도 구순의 책임을 판단했다.')
);
INSERT INTO STG_NARRATIVE_WORLDS (WORLD_ID, NAME, STATUS, LATENT_BRIDGES, UNRESOLVED_GAPS, INSTITUTIONAL_FIT, ENVIRONMENTAL_FIT, N_ASSUMPTIONS, MIN_GRADE, MAIN_ASSUMPTIONS, MAIN_WEAKNESSES, CONTRADICTED_EVIDENCE, STORY_IMPLICATION, IDENTITY_CONDITIONS, RESOLVED_IDENTITIES, EVIDENCE_PROFILE, WORK_ROLE, STORY_QUESTION, DIFFERENCE, UNIQUE_BRIDGES, NARRATIVE)
VALUES (
    'W6',
    '모함·장형 사망 (이조원·윤노동 쪽 주장) — 기각 대조',
    'REJECTED',
    'G06c|G07d|G12b',
    'G01|G02|G03|G04|G05|G08|G09|G10|G11|G13',
    'LOW',
    'MEDIUM',
    '4',
    'LOW',
    '도난 자체가 없었고 구순이 상황을 꾸밈(G07d) / 김명신이 열린 집합(''무고한 평민들'', ''여러 죄수'')의 형장 대상에 포함(G06c) / 아내는 전염병이 아닌 원인으로 따라 죽음(G12b)',
    '세 bridge 모두 contradiction_risk HIGH, overall LOW다. / 열린 집합에 김명신을 넣어야 G06c가 성립한다(closed-set 오류 위험). / 근거가 05 audit-only 주장(V3P0020·V3P0024·V3P0025·V3P0127)뿐이다. / 재감사: bridge 자체의 사료 근거가 LOW·NONE인 후보 — G'
        || '06c(LOW), G07d(LOW), G12b(LOW). 이 부분은 양끝 사실이 확실해도 연결 자체는 추정이다.',
    'CF038(홍대협: 약간의 실제 도난), CF039(정조: 도난 실재), CF040(홍대협 질병 평가·정조 부처 전염병 사망 판단), CF041(정조: 곤장·평문 없음).',
    '이조원·윤노동 쪽 주장(05)을 따른 world다. 도난은 없었고 구순이 꾸몄으며, 김명신은 형장 뒤 쇠약해져 죽었고, 아내는 전염병이 아닌 원인으로 따라 죽었다고 본다. 최종 official·royal finding과 정면으로 충돌하므로 기각하고 대조용으로만 남긴다.',
    NULL,
    NULL,
    'LOW 3',
    '검토했지만 배제된 설명. 이조원·윤노동 쪽 주장(도난 날조, 형장 뒤 사망)을 따른다. confirmed fact와 정조 최종 판단(CF038–CF041)과 충돌한다.',
    '5월 단계의 ''도난 날조·장형 사망'' 주장은 왜 최종 판단에서 받아들여지지 않았는가?',
    '세 bridge 모두 contradiction_risk HIGH인 대조 후보다. 경쟁 설명이 아니라 배제된 설명으로만 남긴다.',
    'G06c|G07d|G12b',
    TO_CLOB('[L] 도난은 없었고 구순이 상황을 꾸몄다(G07d). 그러나 홍대협은 약간의 실제 도난을, 정조는 도난 실재를 판단했다. [L] 김명신은 구금 중 형장을 받고 쇠약해져 죽었다(G06c). 그러나 정조는 김명신이 곤장을 맞지 않았고 평범한 신문도 받지 않았다고 판단했다. [L] 아내는 전염병이 아닌 원인으로 따라 죽었다(G12b). 그러나 정조는 부처가 전')
        || TO_CLOB('염병에 걸려 죽은 것으로 판단했다.')
);

-- output/clean/warn_dispositions.csv (6행)
INSERT INTO STG_WARN_DISPOSITIONS (WARNING_ID, AUDIT_STAGE, AFFECTED_ITEM, WARNING_TYPE, ORIGINAL_TEXT, GENERATED_TEXT, RISK, DISPOSITION, JUSTIFICATION, FIXED_TEXT, FINAL_STATUS, FINAL_CLASSIFICATION, UNRESOLVED_REASON)
VALUES (
    'A1-W1',
    'AUDIT1',
    'EP01',
    'semantic_weakening',
    'CF001 명업은 김명신이 본래 구순과 친숙하여 날마다 왕래했다고 진술했다. / CF002 명업은 김명신이 박거사 일로 구순에게 편지를 보내 힐책했다고 진술했다. / CF003 명업은 그 뒤 구순과 김명신의 왕래가 끊겼다고 진술했다.',
    '명업의 진술에 따르면, 김명신은 본래 구순과 친숙하여 날마다 왕래했으나, 박거사 일로 구순에게 편지를 보내 힐책했고, 그 뒤 구순과 김명신의 왕래가 끊겼다.',
    '원문 어휘 보존율 0.78. 세 진술의 ''진술했다'' 표지가 하나의 ''따르면''으로 합쳐져 뒤쪽 절(힐책·단절)이 사실 서술처럼 읽힐 수 있음',
    'FIXED',
    '원문 대조 결과 진술자(명업)·대상(김명신·구순)·내부 순서는 그대로였다. 그러나 뒤쪽 절의 귀속이 약해지므로 표현 차이로 넘기지 않고 세 진술 각각에 ''진술했다''를 복원했다. 재실행 결과 WARN 사라짐(보존율 1.00).',
    '명업은 김명신이 본래 구순과 친숙하여 날마다 왕래했다고 진술했고, 김명신이 박거사 일로 구순에게 편지를 보내 힐책했다고 진술했으며, 그 뒤 구순과 김명신의 왕래가 끊겼다고 진술했다.',
    'RESOLVED',
    'OBSERVED (RECORDED_TESTIMONY 유지)',
    NULL
);
INSERT INTO STG_WARN_DISPOSITIONS (WARNING_ID, AUDIT_STAGE, AFFECTED_ITEM, WARNING_TYPE, ORIGINAL_TEXT, GENERATED_TEXT, RISK, DISPOSITION, JUSTIFICATION, FIXED_TEXT, FINAL_STATUS, FINAL_CLASSIFICATION, UNRESOLVED_REASON)
VALUES (
    'A1-W2',
    'AUDIT1',
    'EP04',
    'semantic_weakening',
    'CF007 이진욱은 2월 28일 밤 병영에서 자신을 비장청으로 불렀다고 진술했다. / CF008 이진욱은 한재욱이 자신과 조계완 등에게 덕평으로 가도록 지시했다고 진술했다. / CF009 이진욱은 한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했다. / CF010 이진욱은 한재욱이 철편 네 개를 만들어 주었다고 진술했다.',
    '이진욱의 진술에 따르면, 2월 28일 밤 병영에서 이진욱을 비장청으로 불렀고, 한재욱이 이진욱과 조계완 등에게 덕평으로 가도록 지시하고 변지돌과 정원돌을 잡아오라고 지시했으며, 한재욱이 철편 네 개를 만들어 주었다.',
    '보존율 0.71. (1) 네 진술의 ''진술했다'' 표지 삭제. (2) ''자신''이 ''이진욱''으로 치환됨. 치환이 주체를 바꾸었는지 확인 필요',
    'FIXED',
    '''자신''의 지시 대상은 원문에서도 진술자 이진욱이라 주체는 바뀌지 않았다. 그래도 대명사 치환은 actor 정규화이므로 자동 INFO로 넘기지 않고, ''자신''을 원문대로 되돌리고 네 진술 각각에 ''진술했다''를 복원했다. 재실행 결과 WARN 사라짐.',
    '이진욱은 2월 28일 밤 병영에서 자신을 비장청으로 불렀다고 진술했고, 한재욱이 자신과 조계완 등에게 덕평으로 가도록 지시했다고 진술했으며, 한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했고, 한재욱이 철편 네 개를 만들어 주었다고 진술했다.',
    'RESOLVED',
    'OBSERVED (RECORDED_TESTIMONY 유지)',
    NULL
);
INSERT INTO STG_WARN_DISPOSITIONS (WARNING_ID, AUDIT_STAGE, AFFECTED_ITEM, WARNING_TYPE, ORIGINAL_TEXT, GENERATED_TEXT, RISK, DISPOSITION, JUSTIFICATION, FIXED_TEXT, FINAL_STATUS, FINAL_CLASSIFICATION, UNRESOLVED_REASON)
VALUES (
    'A1-W3',
    'AUDIT1',
    'EP05',
    'semantic_weakening',
    'CF011 이진욱은 변지돌이 이미 공주진에서 잡혀간 상태였다고 진술했다. / CF012 이진욱은 장교 일행이 재돌의 처 자미덕을 붙잡았다고 진술했다.',
    '이진욱의 진술에 따르면, 2월 29일 변지돌은 이미 공주진에서 잡혀간 상태였고, 장교 일행이 재돌의 처 자미덕을 붙잡았다.',
    '보존율 0.79. 두 진술의 ''진술했다'' 표지가 합쳐져 체포 사실이 객관 사실처럼 읽힐 수 있음',
    'FIXED',
    '진술자·대상·날짜(2/29, chronology 열)는 유지되었다. 표지 복원으로 처리했다. 재실행 결과 WARN 사라짐.',
    '이진욱은 2월 29일 변지돌이 이미 공주진에서 잡혀간 상태였다고 진술했고, 장교 일행이 재돌의 처 자미덕을 붙잡았다고 진술했다.',
    'RESOLVED',
    'OBSERVED (RECORDED_TESTIMONY 유지)',
    NULL
);
INSERT INTO STG_WARN_DISPOSITIONS (WARNING_ID, AUDIT_STAGE, AFFECTED_ITEM, WARNING_TYPE, ORIGINAL_TEXT, GENERATED_TEXT, RISK, DISPOSITION, JUSTIFICATION, FIXED_TEXT, FINAL_STATUS, FINAL_CLASSIFICATION, UNRESOLVED_REASON)
VALUES (
    'A1-W4',
    'AUDIT1',
    'EP06',
    'semantic_weakening',
    'CF013 자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔다고 진술했다. / CF014 자미덕은 병영에서 도적 혐의로 한 차례 신문을 받았다고 진술했다. / CF015 자미덕은 신문 뒤 비장청 다모방에 구류되었다고 진술했다.',
    '자미덕의 진술에 따르면, 자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔고, 병영에서 도적 혐의로 한 차례 신문을 받았으며, 신문 뒤 비장청 다모방에 구류되었다.',
    '보존율 0.76. 세 진술 표지 삭제로 신문·구류가 관측 사실처럼 읽힐 수 있음',
    'FIXED',
    '진술자·대상·''한 차례''는 유지되었다. 표지 복원으로 처리했다. 재실행 결과 WARN 사라짐.',
    '자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔다고 진술했고, 병영에서 도적 혐의로 한 차례 신문을 받았다고 진술했으며, 신문 뒤 비장청 다모방에 구류되었다고 진술했다.',
    'RESOLVED',
    'OBSERVED (RECORDED_TESTIMONY 유지)',
    NULL
);
INSERT INTO STG_WARN_DISPOSITIONS (WARNING_ID, AUDIT_STAGE, AFFECTED_ITEM, WARNING_TYPE, ORIGINAL_TEXT, GENERATED_TEXT, RISK, DISPOSITION, JUSTIFICATION, FIXED_TEXT, FINAL_STATUS, FINAL_CLASSIFICATION, UNRESOLVED_REASON)
VALUES (
    'A1-E1',
    'AUDIT1',
    'EP07',
    'testimony_to_fact',
    'CF016 자미덕은 한 비장이 … 등을 큰 도적이라고 말하면 자신과 남편을 다음 날 석방하겠다고 말했다고 진술했다. / CF017 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술했다.',
    '자미덕의 진술에 따르면, 한 비장이 … 석방하겠다고 말했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다.',
    '이전 실행에서는 보존율 0.80 이상이라 WARN이 아니었다. 이번에 추가한 regression 규칙(epistemic_marker_deletion·testimony_to_fact)이 같은 결함 유형을 찾아냄. 대질·거짓 진술이 객관 사실처럼 읽힐 위험',
    'ESCALATED_ERROR',
    'A1-W1–W4와 같은 결함 유형이므로 ERROR로 올리고 다음 stage 진행 전에 고쳤다. 두 진술 각각에 ''진술했다''를 복원했다. ''한 비장''·''등''·''거짓으로 꾸며''는 그대로 두었다. 재실행 ERROR 0.',
    '자미덕은 한 비장이 … 석방하겠다고 말했다고 진술했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술했다.',
    'RESOLVED',
    'OBSERVED (RECORDED_TESTIMONY 유지)',
    NULL
);
INSERT INTO STG_WARN_DISPOSITIONS (WARNING_ID, AUDIT_STAGE, AFFECTED_ITEM, WARNING_TYPE, ORIGINAL_TEXT, GENERATED_TEXT, RISK, DISPOSITION, JUSTIFICATION, FIXED_TEXT, FINAL_STATUS, FINAL_CLASSIFICATION, UNRESOLVED_REASON)
VALUES (
    'A3-W1',
    'AUDIT3',
    'G08a',
    'latent_as_observed',
    'CF033 정조는 이조원이 중대 사실을 직접 안핵하지 않고 전해 들은 말을 서계에 붙인 점을 문제 삼았고 이조원을 파직하도록 명했다. / CF035 정조는 홍대협에게 사건을 자세히 조사해 오라고 명하고 그를 충청도 공주 안핵어사로 차하했다. (둘 사이 동기 문장 없음; SRC3_004·V3P0033도 없음)',
    'latent node 없이 관측 node EP18 → EP20을 LATENT PROCEDURAL_NEXT로 직접 연결',
    '관측 node 둘을 잇는 edge는 표·그림에서 관측 관계처럼 읽힐 수 있음(LATENT → OBSERVED/DERIVED 승격 위험)',
    'FIXED',
    '원본 대조 결과 두 행위는 각각 OBSERVED이고, 둘 사이 동기 연결은 어느 CSV에도 없다 → 분류 LATENT. DERIVED의 근거(명시 시간순서 등)는 이미 OE045(TEMPORAL_BEFORE)가 담고 있다. latent 판단 node LN_G08a_1을 사이에 둔 mini-DAG(EP18 → LN_G08a_1 → EP20)로 바꾸고, 관측 '
        || 'node끼리 직접 잇는 latent edge는 이제 ERROR로 막는다. 재실행 결과 WARN 사라짐.',
    'EP18 —INFORMATION_FLOW→ LN_G08a_1 [LATENT] 정조가 이조원 서계의 직접 안핵 부재를 근거로 현지 직접 안핵이 필요하다고 판단 —PROCEDURAL_NEXT→ EP20',
    'RESOLVED',
    'LATENT',
    NULL
);

-- output/clean/mechanism_super_dag_nodes.csv (122행)
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP01',
    'OBSERVED',
    'OBSERVED_EVENT',
    '구순–김명신 관계 변화',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '명업은 김명신이 본래 구순과 친숙하여 날마다 왕래했다고 진술했고, 김명신이 박거사 일로 구순에게 편지를 보내 힐책했다고 진술했으며, 그 뒤 구순과 김명신의 왕래가 끊겼다고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP02',
    'OBSERVED',
    'OBSERVED_EVENT',
    '2월 22일 밤 도적 침입 전언',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '명업은 나복이 2월 22일 밤 도적이 들었다고 자신에게 알렸다고 진술했다. 명업은 나복이 도적 30여 명, 횃불, 지세대감 자칭, 돈과 물품 도난을 말했다고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP03',
    'OBSERVED',
    'OBSERVED_EVENT',
    '구순의 소장과 체포령',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '명업은 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP04',
    'OBSERVED',
    'OBSERVED_EVENT',
    '2월 28일 밤 병영 출동 준비',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '이진욱은 2월 28일 밤 병영에서 자신을 비장청으로 불렀다고 진술했고, 한재욱이 자신과 조계완 등에게 덕평으로 가도록 지시했다고 진술했으며, 한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했고, 한재욱이 철편 네 개를 만들어 주었다고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP05',
    'OBSERVED',
    'OBSERVED_EVENT',
    '2월 29일 덕평 체포 활동',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '이진욱은 2월 29일 변지돌이 이미 공주진에서 잡혀간 상태였다고 진술했고, 장교 일행이 재돌의 처 자미덕을 붙잡았다고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP06',
    'OBSERVED',
    'OBSERVED_EVENT',
    '자미덕의 병영 압송·신문·구류',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔다고 진술했고, 병영에서 도적 혐의로 한 차례 신문을 받았다고 진술했으며, 신문 뒤 비장청 다모방에 구류되었다고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP07',
    'OBSERVED',
    'OBSERVED_EVENT',
    '한 비장의 석방 조건 제시와 대질 시 거짓 진술',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '자미덕은 한 비장이 정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적이라고 말하면 자신과 남편을 다음 날 석방하겠다고 말했다고 진술했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP08',
    'OBSERVED',
    'OBSERVED_EVENT',
    '유제희의 현지 탐문과 구순 발언 기록',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '유제희는 현지 탐문 중 구순이 풍각 김상제도 극히 수상하다고 말했고, 자신이 그 말을 원돌 등의 이름과 함께 기록해 올렸다고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP09',
    'OBSERVED',
    'OBSERVED_EVENT',
    '3월 4일 병사의 김생원 체포 지시',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했다고 진술했다. 해당 기사에서 풍각 김생원은 김명신, 흥덕 김생원은 김갑득으로 식별된다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP10',
    'OBSERVED',
    'OBSERVED_EVENT',
    '3월 4일 조계완의 구순 집 방문과 서찰',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '조계완은 김명신을 잡으러 가는 길에 구순 집에 들렀고, 구순이 이제 도적 다스리는 일이 바른 길을 얻었다는 취지로 말한 뒤 병사에게 전할 서찰 한 장을 건넸다고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP11',
    'OBSERVED',
    'OBSERVED_EVENT',
    '3월 4일 김명신·김갑득 체포',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '이진욱은 장교 일행이 병사의 분부에 따라 김명신과 김갑득을 잡아왔다고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP12',
    'OBSERVED',
    'OBSERVED_EVENT',
    '한재욱의 안핵 공초',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '한재욱은 자미덕을 방으로 불러 남은 밥을 준 사실은 인정했지만, 자미덕을 은밀히 사주한 일은 없다고 진술했고, 구순과 평생 모르는 사이라고 진술했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP13',
    'OBSERVED',
    'OBSERVED_EVENT',
    '5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '이형원의 5월 12일 장계는 충청병영이 김명신을 달포 이상 구금·조사했으나 확실한 장물을 찾지 못했고, 김명신이 그 뒤 사망했다고 보고했으며, 무고한 평민들이 모진 형벌을 받았다고 보고했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP14',
    'OBSERVED',
    'OBSERVED_EVENT',
    '5월 12일 이형원의 지휘 계통 평가',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '5월 12일 기사에서 이광섭은 사건의 병사 지휘 책임자로 심리되며, 이형원은 이광섭이 허황한 말을 믿고 무고한 사람을 잘못 잡았다고 평가했고, 청주 영장 이문협이 수사를 병영 비장에게 전적으로 맡기고 방관했다고 평가했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP15',
    'OBSERVED',
    'OBSERVED_EVENT',
    '5월 12일 정조 1차 판단: 도난 부재 방향',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 당시 장계와 조사에 따라 도난 자체가 없었다는 방향을 받아들였다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP16',
    'OBSERVED',
    'OBSERVED_EVENT',
    '5월 12일 정조 명: 구순 의금부 구금·엄사',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 구순을 의금부에 잡아 가두고 엄히 조사하도록 명했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP17',
    'OBSERVED',
    'OBSERVED_EVENT',
    '5월 27일 암행어사 이조원 보고: 도난 부재 방향',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '이조원은 구순 사건을 도난이 없었다는 방향으로 보고했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP18',
    'OBSERVED',
    'OBSERVED_EVENT',
    '5월 27일 정조의 이조원 비판·파직',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 이조원이 중대 사실을 직접 안핵하지 않고 전해 들은 말을 서계에 붙인 점을 문제 삼았고, 이조원을 파직하도록 명했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP19',
    'OBSERVED',
    'OBSERVED_EVENT',
    '5월 27일 정조 명: 구순 의금부 엄수·반복 신문',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 구순을 의금부에 엄히 가두고 반복 신문하도록 명했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP20',
    'OBSERVED',
    'OBSERVED_EVENT',
    '5월 28일 홍대협 공주 안핵어사 차하',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 홍대협에게 사건을 자세히 조사해 오라고 명하고 그를 충청도 공주 안핵어사로 차하했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP21',
    'OBSERVED',
    'OBSERVED_EVENT',
    '6월 11일 윤노동 별단',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '윤노동의 6월 11일 별단은 김명신이 보수·구금 중 병들어 죽었고, 여러 죄수가 참혹한 형벌을 받았으며, 진정한 장물을 얻지 못했다고 보고했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP22',
    'OBSERVED',
    'OBSERVED_EVENT',
    '6월 11일 비변사 처리 보류 청·윤허',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '비변사는 홍대협의 안핵 복명 전까지 윤노동 별단에 따른 처리를 보류할 것을 청했고, 정조는 이를 윤허했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP23',
    'OBSERVED',
    'OBSERVED_EVENT',
    '6월 13일 홍대협 공주목 신문·복명',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '홍대협은 공주목에서 관련자들을 차례로 신문한 뒤 호서 안핵어사로 복명하여 편전에서 정조에게 보고했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP24',
    'OBSERVED',
    'OBSERVED_EVENT',
    '홍대협 도난 판단: 약간의 실제 도난, 좀도둑 수준',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '홍대협은 약간의 실제 도난은 있었지만 큰 화적 사건이 아니라 보통 좀도둑 수준이었다고 판단했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP25',
    'OBSERVED',
    'OBSERVED_EVENT',
    '정조 최종 도난 판단: 실재',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 최종적으로 도난은 실제로 있었다고 판단했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP26',
    'OBSERVED',
    'OBSERVED_EVENT',
    '홍대협 사인 평가: 질병',
    'OBSERVED',
    'A_BIOLOGICAL',
    NULL,
    'ALL (공통)',
    '홍대협은 김명신의 죽음을 질병 때문이라고 평가했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP27',
    'OBSERVED',
    'OBSERVED_EVENT',
    '정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음',
    'OBSERVED',
    'A_BIOLOGICAL',
    NULL,
    'ALL (공통)',
    '정조는 김명신 부처가 전염병에 걸려 죽은 것으로 판단했고, 김명신이 곤장을 맞지 않았고 평범한 신문도 받지 않았다고 판단했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP28',
    'OBSERVED',
    'OBSERVED_EVENT',
    '정조: 구순→김명신 직접 사망 인과 불확실',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 김명신이 구순 때문에 직접 죽었다는 인과가 십분 확실하다고 할 수 없다고 판단했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP29',
    'OBSERVED',
    'OBSERVED_EVENT',
    '정조: 구순 책임 연결 판단',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 구순이 김명신에게 사적인 감정을 품고 갈등을 일으켰고, 병영의 염탐 담당자에게 김명신의 성명을 적어 주었으며, 그 과정이 김명신이 횡액을 입고 원통하게 죽는 결과로 이어졌다고 책임을 연결해 판단했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP30',
    'OBSERVED',
    'OBSERVED_EVENT',
    '정조: 이광섭 책임 판단',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 이광섭이 구순 편을 들고, 철퇴 네 개를 만들게 했으며, 아전들의 거짓을 제대로 살피지 않은 채 비장에게 일을 맡겼다고 비판하고, 김명신 사망 책임에서 구순과 이광섭의 책임이 크게 다르지 않다고 판단했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP31',
    'OBSERVED',
    'OBSERVED_EVENT',
    '홍대협: 지세 호칭 기원 미확정',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '홍대협은 여러 차례 신문과 별도 탐문에도 지세 호칭의 기원을 확정하지 못했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP32',
    'OBSERVED',
    'OBSERVED_EVENT',
    '정조: 구순 지세 호칭 날조 죄 불인정',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 구순이 지세 호칭을 스스로 만들어냈다는 죄는 인정하지 않았다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP33',
    'OBSERVED',
    'OBSERVED_EVENT',
    '구순 신지도 정배',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 구순을 신지도에 정배했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP34',
    'OBSERVED',
    'OBSERVED_EVENT',
    '이광섭 영동현 유배',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 이광섭을 영동현에 유배했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP35',
    'OBSERVED',
    'OBSERVED_EVENT',
    '병영 비장 한가 처분',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 병영 비장으로 표기된 한가를 도백이 엄히 세 차례 형장 친 뒤 먼 섬의 종으로 보내도록 명했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP36',
    'OBSERVED',
    'OBSERVED_EVENT',
    '이형원 파직',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 충청도 관찰사 이형원을 파직하도록 명했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'EP37',
    'OBSERVED',
    'OBSERVED_EVENT',
    '6월 16일 이형원 유임',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조는 6월 16일 전 충청도 관찰사 이형원을 유임했다.'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'ENV01',
    'CONTEXT',
    'ENV_CONTEXT',
    '1793-01-22 호서 전염병 사망자 치계·구료 단속',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '호서 도신이 전염병 사망자 수를 치계했고 정조가 구료를 각별히 단속하라고 명함'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'ENV02',
    'CONTEXT',
    'ENV_CONTEXT',
    '1793-01-22 호서 기근 구휼 한창',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '같은 기사에서 굶주림 구휼이 한창이라고 명시'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'ENV03',
    'CONTEXT',
    'ENV_CONTEXT',
    '1793-04-10 호서·영남 전염병 창궐(여제)',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '정조실록 일별 목록에 ''호서 영남에 전염병이 창궐하므로 여제를 지내게 하다'' 기사 확인'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'ENV04',
    'CONTEXT',
    'ENV_CONTEXT',
    '1793-05-12 경외 전염병 옥수 치료 명',
    'OBSERVED',
    NULL,
    NULL,
    'ALL (공통)',
    '형조 판서 이득신 건의에 따라 서울·지방 전염병 옥수에게 약을 주어 치료하도록 명함'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F001',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F001 대전통편 현행',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '1793년 당시 통합 법전이 현행이었는가'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F002',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F002 흠휼전칙 현행',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '형구·구금·군문 곤형의 규격과 사용 제한이 현행이었는가'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F003',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F003 군문 중곤 사용 제한',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '병사·감사 등 군문 지휘자가 중곤을 사용할 수 있는 조건'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F004',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F004 구금 도구 기준',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '사형·유배·장죄 등 죄급별 가·뉴·쇄 사용 기준'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F005',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F005 수령의 군현 통치',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '군현 수령이 해당 고을 행정을 담당하는 기본 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F006',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F006 관찰사의 수령 감독·직계',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '관찰사가 수령을 감독하고 중앙에 직접 보고할 수 있는 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F007',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F007 병마절도사 도 단위 군사지휘',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '병마절도사가 도의 군사 지휘권을 가진 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F008',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F008 병영 지휘체계',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '병영이 병마절도사 주둔 관서이며 하위 진·장교 체계가 존재'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F009',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F009 비장 막료 체계',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '감사·절도사 등이 비장을 막료로 둘 수 있는 관행'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F010',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F010 토포사 제도',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '도적 수색·체포를 위해 수령 또는 진영장이 토포사를 겸임할 수 있음'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F011',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F011 형조 심리·회계',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '형조가 중앙 형사행정과 사건 심리에 관여할 수 있는 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F012',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F012 의금부 특별사법·재심',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '왕명에 따라 중요범죄 심문·재심을 수행할 수 있는 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F013',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F013 암행어사',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '왕이 지방에 비밀 파견해 수령·민폐를 탐문할 수 있는 제도'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F014',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F014 안핵어사',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '특정 사건을 별도로 조사하는 왕명 특별 조사관의 운용'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F015',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F015 초검-복검-추가검',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '살인·변사에서 초검 후 복검, 의심 시 삼검·사검까지 가능'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F016',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F016 증수무원록 개정 지침',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '1792년 개정·간행된 법의학 지침의 존재'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F017',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F017 비변사 심의',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '비변사가 국정·군사·지방 사안을 중앙에서 심의할 수 있음'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F018',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F018 수교의 법적 성격',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '국왕이 특정 사안에 법적 성격의 명령을 내릴 수 있음'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F019',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F019 격쟁·상언 등 상향 호소',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '하급 판단에 불복해 상위 권력에 호소하는 경로의 존재'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'CTX_F020',
    'CONTEXT',
    'INSTITUTIONAL_CONTEXT',
    'F020 장계·서계·계문·회계',
    NULL,
    NULL,
    NULL,
    'ALL (제약조건)',
    '지방·특사·중앙 관청이 문서로 상향 보고·심리하는 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'M1',
    'LATENT_MECHANISM',
    'MECHANISM',
    'M1_OFFICIAL_INFORMATION_ROUTE',
    NULL,
    'B_PROCEDURAL',
    'M1',
    'config별',
    '구순 쪽 소장·정보가 진영·병영 비장·병사로 이어지는 공식 보고·지휘 경로를 따라 이동하는 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'M2',
    'LATENT_MECHANISM',
    'MECHANISM',
    'M2_TESTIMONY_AMPLIFICATION',
    NULL,
    'B_PROCEDURAL',
    'M2',
    'config별',
    '자미덕 등의 진술·대질·번복이 수사 범위나 판단 자료를 키우거나 바꾸는 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'M3',
    'LATENT_MECHANISM',
    'MECHANISM',
    'M3_PRIVATE_INFLUENCE_CHANNEL',
    NULL,
    'B_PROCEDURAL',
    'M3',
    'config별',
    '구순과 병영 지휘관 사이의 비공식·사적 통로(서신·접촉)를 통해 정보나 영향이 전달되는 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'M4',
    'LATENT_MECHANISM',
    'MECHANISM',
    'M4_DISTRIBUTED_INSTITUTIONAL_ACTION',
    NULL,
    'B_PROCEDURAL',
    'M4',
    'config별',
    '하나의 중앙 지휘가 아니라 비장·아전·진(鎭) 등 여러 기관·실무자의 판단이 따로 쌓이는 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'M5',
    'LATENT_MECHANISM',
    'MECHANISM',
    'M5_REVIEW_AND_CORRECTION',
    NULL,
    'REVIEW',
    'M5',
    'config별',
    '초기 판단을 암행어사·안핵어사·비변사·국왕 심리가 따로 다시 검토하고 고치는 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'M6',
    'LATENT_MECHANISM',
    'MECHANISM',
    'M6_INITIAL_JUDGMENT_BASIS',
    NULL,
    'REVIEW',
    'M6',
    'config별',
    '5월 단계의 ''도난 없음 방향'' 판단이 어떤 자료·추론에서 형성되었는지에 관한 구조'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'MB',
    'LATENT_MECHANISM',
    'MECHANISM',
    'MB_CUSTODY_BIOLOGICAL_COURSE',
    NULL,
    'A_BIOLOGICAL',
    'MB',
    'config별',
    '체포 뒤 구금 중 발병·사망 경과에 관한 구조(사망 branch A: 생물학적 사인)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'V_COMPLAINT_TO_BARRACKS',
    'LATENT_MECHANISM',
    'STRUCTURAL_VARIABLE',
    'V_COMPLAINT_TO_BARRACKS',
    NULL,
    'B_PROCEDURAL',
    NULL,
    'config별',
    'V_COMPLAINT_TO_BARRACKS = M1_OFFICIAL_INFORMATION_ROUTE'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'V_COMMAND_SOURCE',
    'LATENT_MECHANISM',
    'STRUCTURAL_VARIABLE',
    'V_COMMAND_SOURCE',
    NULL,
    'B_PROCEDURAL',
    NULL,
    'config별',
    'V_COMMAND_SOURCE = M1_OFFICIAL_INFORMATION_ROUTE(G02a: 병사 지시) XOR M4_DISTRIBUTED_INSTITUTIONAL_ACTION(G02b: 비장 자체 판단)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'V_INFO_TO_COMMANDER',
    'LATENT_MECHANISM',
    'STRUCTURAL_VARIABLE',
    'V_INFO_TO_COMMANDER',
    NULL,
    'B_PROCEDURAL',
    NULL,
    'config별',
    'V_INFO_TO_COMMANDER = M1 OR M2 OR M3 OR M4  (각각 G04a·G03a·G03b / G04b·G04d / G04c / G03c)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'V_ARREST_PATH',
    'LATENT_MECHANISM',
    'STRUCTURAL_VARIABLE',
    'V_ARREST_PATH',
    NULL,
    'B_PROCEDURAL',
    NULL,
    'config별',
    'V_ARREST_PATH = V_INFO_TO_COMMANDER AND INSTITUTIONALLY_COMPATIBLE(F007·F008: 병사 → 장교 명령)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'V_INVESTIGATION_SCOPE',
    'LATENT_MECHANISM',
    'STRUCTURAL_VARIABLE',
    'V_INVESTIGATION_SCOPE',
    NULL,
    'B_PROCEDURAL',
    NULL,
    'config별',
    'V_INVESTIGATION_SCOPE = M2_TESTIMONY_AMPLIFICATION OR M4_DISTRIBUTED_INSTITUTIONAL_ACTION'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'V_INITIAL_JUDGMENT_BASIS',
    'LATENT_MECHANISM',
    'STRUCTURAL_VARIABLE',
    'V_INITIAL_JUDGMENT_BASIS',
    NULL,
    'B_PROCEDURAL',
    NULL,
    'config별',
    'V_INITIAL_JUDGMENT_BASIS = M6_INITIAL_JUDGMENT_BASIS OR M2_TESTIMONY_AMPLIFICATION(보조: G07b·G07c)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'V_REVIEW_CORRECTION',
    'LATENT_MECHANISM',
    'STRUCTURAL_VARIABLE',
    'V_REVIEW_CORRECTION',
    NULL,
    'REVIEW',
    NULL,
    'config별',
    'V_REVIEW_CORRECTION = M5_REVIEW_AND_CORRECTION  (관측 backbone: EP15 →REVISES→ EP25 등. world마다 달라지지 않음)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'V_RESPONSIBILITY',
    'LATENT_MECHANISM',
    'STRUCTURAL_VARIABLE',
    'V_RESPONSIBILITY',
    NULL,
    'B_PROCEDURAL',
    NULL,
    'config별',
    'V_RESPONSIBILITY = V_REVIEW_CORRECTION AND V_ARREST_PATH  (책임 판단은 절차 branch B에만 의존, 사인과 무관)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'V_SANCTION',
    'LATENT_MECHANISM',
    'STRUCTURAL_VARIABLE',
    'V_SANCTION',
    NULL,
    'REVIEW',
    NULL,
    'config별',
    'V_SANCTION = V_RESPONSIBILITY  (처분은 관측 사실. G10 사유는 OPEN_UNRESOLVED)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'V_CUSTODY_COURSE',
    'LATENT_MECHANISM',
    'STRUCTURAL_VARIABLE',
    'V_CUSTODY_COURSE',
    NULL,
    'A_BIOLOGICAL',
    NULL,
    'config별',
    'V_CUSTODY_COURSE = MB_CUSTODY_BIOLOGICAL_COURSE  (환경 E001–E004는 호환성 context. 개인 감염 확정 아님)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G01a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '청주 진영 정소 → 진영이 병영 비장 쪽에 수사를 넘김 → 2/28 출동',
    NULL,
    'B_PROCEDURAL',
    'M1',
    'W1, W2, W4, W5',
    '[LATENT] 소장이 청주 진영에 접수되었고, 진영이 수사를 병영 비장 쪽에 넘겼으며, 그것이 2/28 이전이었다 · evidence MEDIUM · final MEDIUM'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G01b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '소장이 병영에 직접 접수',
    NULL,
    'B_PROCEDURAL',
    'M1',
    'W3',
    '[LATENT] 소장이 병영에 직접 접수되었고 병영이 체포령을 냈다 · evidence NONE · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G01c',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '청주목 수령 → 관찰사 → 병영 이첩',
    NULL,
    'B_PROCEDURAL',
    'M1',
    '(world 미사용)',
    '[LATENT] 소장이 청주목 수령에게 접수되어 관찰사를 거쳐 병영으로 이첩되었다 · evidence NONE · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G02a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '이광섭이 출동·철퇴 제작을 지시하고 한재욱이 실무 전달 (ID07 조건)',
    NULL,
    'B_PROCEDURAL',
    'M1',
    'W1, W3',
    '[LATENT] 이광섭이 2/28 출동과 철퇴(=철편) 네 개 제작을 지시했고 한재욱이 그것을 전달·집행했다 · evidence MEDIUM · final MEDIUM'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G02b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '한재욱이 상위 명령 없이 출동 지시, 병영 지휘관은 사후 승인·묵인',
    NULL,
    'B_PROCEDURAL',
    'M4',
    'W2, W4',
    '[LATENT] 한재욱이 상위 명령 없이 자기 판단으로 출동을 지시했고 병영 지휘관이 사후 승인·묵인했다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G02c',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '청주 영장 이문협이 직접 출동 지휘',
    NULL,
    'B_PROCEDURAL',
    'M4',
    '(world 미사용)',
    '[LATENT] 청주 영장 이문협이 2/28 출동을 직접 지휘했다 · evidence NONE · final LOW · 분석 제외(INCOMPATIBLE 또는 대조용)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G03a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '한재욱이 유제희를 탐문에 보내고, 2/28 이전 기록이 한재욱에게 올라감',
    NULL,
    'B_PROCEDURAL',
    'M1',
    'W1, W2',
    '[LATENT] 한재욱이 유제희를 탐문에 보냈고, 유제희 기록이 2/28 이전 한재욱에게 올라가 2/28 체포 대상 선정에 쓰였다 · evidence MEDIUM · final MEDIUM'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G03b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '탐문은 2/29~3/4 사이, 김상제(=김명신) 언급이 3/4 지시를 직접 촉발',
    NULL,
    'B_PROCEDURAL',
    'M1',
    '(world 미사용)',
    '[LATENT] 유제희 탐문이 2/29~3/4 사이였고 김상제 언급이 3/4 지시를 직접 촉발했다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G03c',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '유제희가 병사에게 직접 보고(비장 우회)',
    NULL,
    'B_PROCEDURAL',
    'M4',
    'W4',
    '[LATENT] 유제희가 비장을 건너뛰고 병사에게 직접 보고했다 · evidence NONE · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G04a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '공식 정보 경로: 유제희 기록 → 비장 계통 → 병사 → 3/4 지시',
    NULL,
    'B_PROCEDURAL',
    'M1',
    'W1',
    '[LATENT] 유제희 기록이 비장 계통을 거쳐 3/4 이전 병사에게 보고되어 체포 지시의 근거가 되었다 · evidence MEDIUM · final MEDIUM'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G04b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '자미덕 대질 진술 경로: 회유 주장 진술(열린 목록) → 병사 지시',
    NULL,
    'B_PROCEDURAL',
    'M2',
    'W2',
    '[LATENT] 자미덕의 대질 진술이 3/4 이전 병사에게 보고되어 김생원 체포 지시의 근거가 되었다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G04c',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '사적 경로: 3/4 이전 구순→병사 사적 접촉으로 김명신을 의심 대상으로 알림',
    NULL,
    'B_PROCEDURAL',
    'M3',
    'W3',
    '[LATENT] 3/4 이전 구순이 병사에게 사적으로 김명신을 의심 대상으로 알렸다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G04d',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '석단 공초 경로: 다른 피의자 공초가 김명신을 도적 괴수로 지목',
    NULL,
    'B_PROCEDURAL',
    'M2',
    '(world 미사용)',
    '[LATENT] 석단 공초가 3/4 이전 병사에게 보고되어 김명신 체포 지시로 이어졌다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G04e',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '구순이 장교에게 직접 공식 체포 명령',
    NULL,
    'B_PROCEDURAL',
    'M3',
    '(world 미사용)',
    '[LATENT] 구순이 장교에게 직접 공식 체포 명령을 내렸다 · evidence NONE · final INCOMPATIBLE · 분석 제외(INCOMPATIBLE 또는 대조용)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G05a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '서찰이 병사에게 전달, 체포 지지·추가 의혹 내용',
    NULL,
    'B_PROCEDURAL',
    'M3',
    'W1, W3',
    '[LATENT] 조계완이 서찰을 병사에게 전달했고, 서찰 내용은 체포 지지·의혹 제기였다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G05b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '서찰은 전달되었으나 사건과 무관한 인사·사례',
    NULL,
    'B_PROCEDURAL',
    'M3',
    '(world 미사용)',
    '[LATENT] 서찰은 전달되었으나 사건과 무관한 인사·사례였다 · evidence NONE · final LOW · 분석 제외(INCOMPATIBLE 또는 대조용)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G06a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '구금 중 발병 → 보수·구금 상태에서 사망 (처우는 CF041 판단을 따름)',
    NULL,
    'A_BIOLOGICAL',
    'MB',
    'W1, W3, W4, W5',
    '[LATENT] 김명신의 발병이 3/4 체포 이후 구금 중에 시작되었고 5/12 보고 이전에 죽었다 · evidence MEDIUM · final MEDIUM'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G06b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '형장 없는 조사 압박 + 발병 → 사망',
    NULL,
    'A_BIOLOGICAL',
    'MB',
    'W2',
    '[LATENT] 형장 없는 반복 조사 압박이 있었고 이어 발병해 죽었다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G06c',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '형장(곤장) → 쇠약 → 사망',
    NULL,
    'A_BIOLOGICAL',
    'MB',
    'W6',
    '[LATENT] 김명신이 구금 중 형장을 받아 쇠약해진 뒤 죽었다 · evidence LOW · final LOW · 분석 제외(INCOMPATIBLE 또는 대조용)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G07a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '장물 미발견을 근거로 ''도난 없음''을 추론',
    NULL,
    'REVIEW',
    'M6',
    'W1, W3, W5',
    '[LATENT] 5월 단계의 ''도난 없음'' 판단은 장물 미발견을 근거로 한 추론이었다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G07b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '회동 조사 응답자들의 ''구순이 꾸몄다'' 진술 채택',
    NULL,
    'B_PROCEDURAL',
    'M2',
    'W4',
    '[LATENT] 이형원 회동 조사의 응답자 진술(''구순이 꾸몄다'')이 장계와 5/12 판단에 반영되었다 · evidence MEDIUM · final MEDIUM'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G07c',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '구순 집 사람들의 진술 번복이 5월 자료에 들어감',
    NULL,
    'B_PROCEDURAL',
    'M2',
    'W2',
    '[LATENT] 명업 등의 번복 진술이 5월 판단 자료에 들어갔다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G07d',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '도난은 실제로 없었고 구순이 꾸몄다 (이조원·윤노동 주장)',
    NULL,
    'REVIEW',
    'M6',
    'W6',
    '[LATENT] 도난은 실제로 없었고 구순이 꾸몄다 · evidence LOW · final LOW · 분석 제외(INCOMPATIBLE 또는 대조용)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G08a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '직접 안핵 부재 비판 → 독립 안핵 결정',
    NULL,
    'REVIEW',
    'M5',
    'W1, W2, W3, W5',
    '[LATENT] 5/27 이조원의 직접 안핵 부재에 대한 정조의 비판이 5/28 홍대협 차하의 동기였다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G08b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '지세 호칭 의문 해소가 주목적',
    NULL,
    'REVIEW',
    'M5',
    'W4',
    '[LATENT] 홍대협 차하의 주목적은 지세 호칭의 출처를 밝히는 것이었다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G09a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '한가(=한재욱) 처분 근거 = 자미덕이 진술한 회유·대질 지휘와 출동 운영',
    NULL,
    'REVIEW',
    'M5',
    'W1, W2',
    '[LATENT] 한가(=한재욱) 처분의 근거는 자미덕이 진술한 회유·대질 지휘와 출동 운영이었다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G09b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '한가 = 한재욱, ''한 비장''은 다른 사람 (ID02 확정과 충돌)',
    NULL,
    'REVIEW',
    'M5',
    '(world 미사용)',
    '[LATENT] 자미덕 진술의 ''한 비장''은 한재욱과 다른 사람이고 한가 처분 근거는 출동 운영뿐이다 · evidence NONE · final INCOMPATIBLE · 분석 제외(INCOMPATIBLE 또는 대조용)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G09c',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '한가는 한재욱이 아닌 다른 ''한'' 성 비장 (ID03 확정과 충돌)',
    NULL,
    'REVIEW',
    'M5',
    '(world 미사용)',
    '[LATENT] 한가는 한재욱이 아닌 다른 ''한'' 성 비장이다 · evidence NONE · final INCOMPATIBLE · 분석 제외(INCOMPATIBLE 또는 대조용)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G10a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '파직 사유 = 장계와 안핵 결과의 차이',
    NULL,
    'REVIEW',
    'M5',
    '(world 미사용)',
    '[LATENT] 이형원 파직 사유는 5/12 장계가 6/13 안핵 결과와 도난 여부에서 크게 달랐던 데 있다 · evidence MEDIUM · final MEDIUM'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G10b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '유임 사유 = 구휼·전염병 행정 연속성',
    NULL,
    'REVIEW',
    'M5',
    '(world 미사용)',
    '[LATENT] 유임 사유는 구휼·전염병 행정의 연속성이었다 · evidence NONE · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G10c',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '파직 → 유임은 처분의 형식적 경감',
    NULL,
    'REVIEW',
    'M5',
    '(world 미사용)',
    '[LATENT] 파직 → 유임은 처분의 형식적 경감이었다 · evidence NONE · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G11a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '공주진이 같은 도난 사건으로 먼저 체포',
    NULL,
    'B_PROCEDURAL',
    'M4',
    'W1, W4',
    '[LATENT] 공주진이 같은 도난 사건 혐의로 변지돌을 2/29 이전에 먼저 체포했다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G11b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '병영이 2/28 이전 공주진에 체포 의뢰',
    NULL,
    'B_PROCEDURAL',
    'M1',
    '(world 미사용)',
    '[LATENT] 병영이 2/28 이전 공주진에 변지돌 체포를 의뢰했다 · evidence NONE · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G11c',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '변지돌은 별건으로 공주진에 구금 중',
    NULL,
    'B_PROCEDURAL',
    'M4',
    '(world 미사용)',
    '[LATENT] 변지돌은 별건으로 공주진에 구금되어 있었다 · evidence NONE · final LOW · 분석 제외(INCOMPATIBLE 또는 대조용)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G12a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '아내도 전염병으로 사망(시점 미상)',
    NULL,
    'A_BIOLOGICAL',
    'MB',
    'W1, W2, W3',
    '[LATENT] 김명신의 아내도 전염병으로 죽었다(사건 수준) · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G12b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '아내는 남편 사망 뒤 비통 속에 ''따라 죽음''(전염병 아님)',
    NULL,
    'A_BIOLOGICAL',
    'MB',
    'W6',
    '[LATENT] 아내는 전염병이 아니라 비통 속에 따라 죽었다 · evidence LOW · final LOW · 분석 제외(INCOMPATIBLE 또는 대조용)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G13a',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '의금부 구금·신문 실행, 지세 문제는 6/13까지 결론 없음',
    NULL,
    'REVIEW',
    'M5',
    'W1, W4',
    '[LATENT] 의금부 구금·신문이 실제로 실행되었고, 지세 문제는 6/13까지 결론이 나지 않았다 · evidence LOW · final LOW'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'G13b',
    'LATENT_MECHANISM',
    'CANDIDATE_BRIDGE',
    '의금부 신문은 6/13 이전에 실질적으로 진행되지 않음',
    NULL,
    'REVIEW',
    'M5',
    '(world 미사용)',
    '[LATENT] 의금부 신문은 6/13 이전에 실질적으로 진행되지 않았다 · evidence NONE · final LOW · 분석 제외(INCOMPATIBLE 또는 대조용)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'U_ID06',
    'UNRESOLVED',
    'UNRESOLVED_ITEM',
    'ID06 병영의 염탐 담당자 = 유제희?',
    NULL,
    NULL,
    NULL,
    'ALL (확정하지 않음)',
    'OE071(condition ID06)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'U_ID07',
    'UNRESOLVED',
    'UNRESOLVED_ITEM',
    'ID07 철편 네 개 = 철퇴 네 개?',
    NULL,
    NULL,
    NULL,
    'ALL (확정하지 않음)',
    'OE080(condition ID07)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'U_ID08',
    'UNRESOLVED',
    'UNRESOLVED_ITEM',
    'ID08 3/4 장교 일행에 조계완 포함?',
    NULL,
    NULL,
    NULL,
    'ALL (확정하지 않음)',
    'OE010(condition ID08)'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'U_OE007',
    'UNRESOLVED',
    'UNRESOLVED_ITEM',
    'OE007 자미덕 ''지휘'' 주장 ↔ 한재욱 ''은밀한 사주'' 부인 (PARTIAL_CONFLICT)',
    NULL,
    NULL,
    NULL,
    'ALL (확정하지 않음)',
    'OE007'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'U_OE062',
    'UNRESOLVED',
    'UNRESOLVED_ITEM',
    'OE062 5월 ''조사'' = 정조 ''평범한 신문''? (UNRESOLVED_SCOPE)',
    NULL,
    NULL,
    NULL,
    'ALL (확정하지 않음)',
    'OE062'
);
INSERT INTO STG_SD_NODES (NODE_ID, SD_STATUS, NODE_TYPE, LABEL, FROZEN_STATUS, BRANCH, MECHANISM, WORLDS, DETAIL)
VALUES (
    'U_G10',
    'UNRESOLVED',
    'UNRESOLVED_ITEM',
    'G10 이형원 파직 → 유임 이유 (OPEN_UNRESOLVED)',
    NULL,
    NULL,
    NULL,
    'ALL (확정하지 않음)',
    'EP36→EP37'
);

-- output/clean/mechanism_super_dag_edges.csv (205행)
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE001',
    'EP01',
    'EP02',
    'TEMPORAL_BEFORE',
    'DERIVED',
    'FROZEN',
    '명업 진술상 힐책(2월 초순)이 2월 22일 밤 도적 전언보다 앞선다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE002',
    'EP02',
    'EP03',
    'TEMPORAL_BEFORE',
    'DERIVED',
    'FROZEN',
    'CF006 chronology ''도난 신고 이후''.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE003',
    'EP02',
    'EP04',
    'TEMPORAL_BEFORE',
    'DERIVED',
    'FROZEN',
    '2/22 밤 → 2/28 밤 (서로 다른 진술자의 명시 날짜).'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE004',
    'EP04',
    'EP05',
    'ORDER_TO_ACTION',
    'DERIVED',
    'FROZEN',
    '같은 이진욱 진술 흐름에서 덕평 출동 지시(2/28) 뒤 2/29 장교 일행의 현장 체포 활동이 이어진다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE005',
    'EP05',
    'EP06',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    'CF013 chronology ''자미덕 체포 뒤'': 병영 압송·신문·구류.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE006',
    'EP06',
    'EP07',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    'CF016 chronology ''구류 중/그 후'', CF017 ''대질 때''.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE007',
    'EP07',
    'EP12',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    'DERIVED',
    'FROZEN',
    '자미덕: 한 비장의 지휘에 따라 거짓으로 꾸며 말함 ↔ 한재욱: 자미덕을 은밀히 사주한 일 없음.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE008',
    'EP09',
    'EP11',
    'ORDER_TO_ACTION',
    'OBSERVED',
    'FROZEN',
    'CF023 ''병사의 분부에 따라'' — 지시와 실행의 연결이 원문에 있다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE009',
    'EP09',
    'EP10',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    '조계완은 ''김명신을 잡으러 가는 길에'' 구순 집에 들렀다. 체포 임무가 먼저 주어져 있었음을 전제로 한다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE010',
    'EP10',
    'EP11',
    'TEMPORAL_BEFORE',
    'DERIVED',
    'FROZEN',
    '''잡으러 가는 길에'' → 방문이 체포보다 앞선다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE011',
    'EP11',
    'EP13',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    '3/4 체포된 김명신 → 충청병영의 달포 이상 구금·조사 → 사망(5/12 보고).'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE020',
    'EP01',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE021',
    'EP02',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE022',
    'EP03',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE023',
    'EP04',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE024',
    'EP05',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE025',
    'EP06',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE026',
    'EP07',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE027',
    'EP08',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE028',
    'EP09',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE029',
    'EP10',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE030',
    'EP11',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE031',
    'EP12',
    'EP23',
    'INFORMATION_FLOW',
    'DERIVED',
    'FROZEN',
    'SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE013',
    'EP02',
    'EP24',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    'DERIVED',
    'FROZEN',
    '중첩 진술의 ''도적 30여 명·횃불'' ↔ 홍대협 ''큰 화적 사건이 아니라 보통 좀도둑 수준''.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE040',
    'EP13',
    'EP15',
    'REVIEW_OF',
    'DERIVED',
    'FROZEN',
    'CF030 ''당시 장계와 조사에 따라'' 도난 부재 방향을 받아들임.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE041',
    'EP15',
    'EP16',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    '같은 날 같은 기사(SRC3_001)의 판단 뒤 명령.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE042',
    'EP16',
    'EP19',
    'TEMPORAL_BEFORE',
    'DERIVED',
    'FROZEN',
    '5/12 의금부 구금 명 → 5/27 의금부 엄수·반복 신문 명.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE043',
    'EP17',
    'EP18',
    'REVIEW_OF',
    'OBSERVED',
    'FROZEN',
    'CF033: 정조가 이조원 서계의 조사 방식을 문제 삼음.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE044',
    'EP17',
    'EP19',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    'CF034 출처 SRC3_002 제목 ''이조원이 구순 사건을 아뢰고 엄핵을 청함''.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE045',
    'EP18',
    'EP20',
    'TEMPORAL_BEFORE',
    'DERIVED',
    'FROZEN',
    '5/27 이조원 비판 → 5/28 홍대협 차하.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE046',
    'EP20',
    'EP23',
    'ORDER_TO_ACTION',
    'DERIVED',
    'FROZEN',
    '''사건을 자세히 조사해 오라''·안핵어사 차하 → 공주목 신문·안핵어사 복명(같은 인물, 같은 직함).'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE047',
    'EP21',
    'EP22',
    'REVIEW_OF',
    'OBSERVED',
    'FROZEN',
    'CF036: 윤노동 별단에 따른 처리 보류.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE048',
    'EP22',
    'EP23',
    'PROCEDURAL_NEXT',
    'OBSERVED',
    'FROZEN',
    'CF036 ''홍대협의 안핵 복명 전까지'' 보류 → 복명.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE050',
    'EP23',
    'EP24',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    '복명 속 도난 판단.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE051',
    'EP23',
    'EP26',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    '복명 속 사인 평가.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE052',
    'EP23',
    'EP31',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    '복명 속 지세 호칭 조사 결과.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE053',
    'EP15',
    'EP24',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    'DERIVED',
    'FROZEN',
    '5/12 ''도난 자체가 없었다는 방향'' ↔ 6/13 홍대협 ''약간의 실제 도난''.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE054',
    'EP17',
    'EP24',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    'DERIVED',
    'FROZEN',
    '5/27 이조원 ''도난이 없었다는 방향'' ↔ 6/13 홍대협 ''약간의 실제 도난''.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE055',
    'EP24',
    'EP25',
    'REVIEW_OF',
    'DERIVED',
    'FROZEN',
    '같은 복명 기사에서 정조가 안핵 판단을 검토해 최종 판단.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE056',
    'EP15',
    'EP25',
    'REVISES',
    'DERIVED',
    'FROZEN',
    '같은 주체(정조)의 도난 판단: 5/12 부재 방향 → 6/13 실재.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE060',
    'EP13',
    'EP26',
    'REVIEW_OF',
    'DERIVED',
    'FROZEN',
    '5/12 장계는 사인 없이 사망만 보고 → 안핵어사(사건 자세히 조사 명)가 사인을 질병으로 평가.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE061',
    'EP26',
    'EP27',
    'REVIEW_OF',
    'DERIVED',
    'FROZEN',
    '홍대협 ''질병'' → 정조 ''부처가 전염병''. 대상이 부처로, 병명이 전염병으로 구체화된다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE062',
    'EP13',
    'EP27',
    'CONTRADICTS_AT_CLAIM_LEVEL',
    'DERIVED',
    'FROZEN',
    '5/12 장계 ''구금·조사'' ↔ 6/13 정조 ''평범한 신문도 받지 않았다''.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE063',
    'EP27',
    'EP28',
    'CONTEXT_SUPPORTS',
    'DERIVED',
    'FROZEN',
    '같은 날 정조 판단 안에서 전염병 사망·무장형 판단과 ''직접 인과 불확실'' 판단이 함께 놓인다.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE070',
    'EP01',
    'EP29',
    'RESPONSIBILITY_LINK',
    'DERIVED',
    'FROZEN',
    '정조 판단 ''사적인 감정을 품고 갈등을 일으켰고'' ↔ 명업 진술의 힐책·왕래 단절.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE071',
    'EP08',
    'EP29',
    'RESPONSIBILITY_LINK',
    'DERIVED',
    'FROZEN',
    '정조 판단 ''병영의 염탐 담당자에게 김명신의 성명을 적어 주었으며'' ↔ 유제희 진술.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE072',
    'EP11',
    'EP29',
    'RESPONSIBILITY_LINK',
    'DERIVED',
    'FROZEN',
    '정조 판단의 ''횡액'' ↔ 3/4 체포.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE073',
    'EP13',
    'EP29',
    'RESPONSIBILITY_LINK',
    'DERIVED',
    'FROZEN',
    '정조 판단의 ''원통하게 죽는 결과'' ↔ 구금 뒤 사망 보고.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE074',
    'EP29',
    'EP33',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    '같은 기사에서 책임 판단 뒤 정배 처분.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE080',
    'EP04',
    'EP30',
    'RESPONSIBILITY_LINK',
    'DERIVED',
    'FROZEN',
    '정조 비판 ''철퇴 네 개를 만들게 했으며'' ↔ 이진욱 진술 ''한재욱이 철편 네 개를 만들어 주었다''.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE081',
    'EP09',
    'EP30',
    'RESPONSIBILITY_LINK',
    'DERIVED',
    'FROZEN',
    '3/4 ''병사''의 체포 지시 ↔ 정조의 이광섭 지휘 책임 판단.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE082',
    'EP14',
    'EP30',
    'REVIEW_OF',
    'DERIVED',
    'FROZEN',
    '5/12 이형원의 이광섭·이문협 평가 → 6/13 정조의 이광섭 책임 재평가.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE083',
    'EP29',
    'EP30',
    'RESPONSIBILITY_LINK',
    'DERIVED',
    'FROZEN',
    'CF044 ''구순과 이광섭의 책임이 크게 다르지 않다'' — 두 책임 판단의 비교.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE084',
    'EP30',
    'EP34',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    '책임 판단 뒤 유배 처분.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE090',
    'EP02',
    'EP31',
    'REVIEW_OF',
    'DERIVED',
    'FROZEN',
    '중첩 진술의 ''지세대감 자칭'' → 홍대협 기원 미확정.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE091',
    'EP31',
    'EP32',
    'REVIEW_OF',
    'DERIVED',
    'FROZEN',
    '홍대협 미확정 → 정조의 날조 죄 불인정.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE095',
    'EP23',
    'EP35',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    '안핵 복명 뒤 처분.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE096',
    'EP23',
    'EP36',
    'PROCEDURAL_NEXT',
    'DERIVED',
    'FROZEN',
    '안핵 복명 뒤 처분.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE097',
    'EP36',
    'EP37',
    'REVISES',
    'DERIVED',
    'FROZEN',
    '6/13 파직 → 6/16 유임(같은 인물의 관직 상태 변경).'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE098',
    'EP25',
    'EP36',
    'TEMPORAL_BEFORE',
    'DERIVED',
    'FROZEN',
    '같은 날 최종 도난 판단과 이형원 파직.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE100',
    'ENV01',
    'EP26',
    'CONTEXT_SUPPORTS',
    'DERIVED',
    'FROZEN',
    '1월 호서 전염병 사망 치계 — 질병 사망 평가와 시대적으로 부합.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE101',
    'ENV03',
    'EP26',
    'CONTEXT_SUPPORTS',
    'DERIVED',
    'FROZEN',
    '4월 호서 전염병 창궐 — 구금(3/4~)·사망(5/12 이전) 기간과 겹치는 지역 환경.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE102',
    'ENV01',
    'EP27',
    'CONTEXT_SUPPORTS',
    'DERIVED',
    'FROZEN',
    '정조의 ''부처 전염병 사망'' 판단과 부합하는 지역 환경.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE103',
    'ENV03',
    'EP27',
    'CONTEXT_SUPPORTS',
    'DERIVED',
    'FROZEN',
    '전염병 지속 — 정조 판단과 부합.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE104',
    'ENV04',
    'EP27',
    'CONTEXT_SUPPORTS',
    'DERIVED',
    'FROZEN',
    '5/12 옥수 전염병 치료 정책 — 옥중 전염병이 조정의 현안이었다는 custody-health context.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE105',
    'ENV02',
    'EP27',
    'CONTEXT_SUPPORTS',
    'DERIVED',
    'FROZEN',
    '기근·구휼 — 영양·행정 부담이라는 거시 맥락(약함).'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE106',
    'ENV01',
    'EP21',
    'CONTEXT_SUPPORTS',
    'DERIVED',
    'FROZEN',
    '윤노동 별단 ''보수·구금 중 병들어 죽었다''는 보고와 부합하는 환경.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'OE107',
    'ENV03',
    'EP21',
    'CONTEXT_SUPPORTS',
    'DERIVED',
    'FROZEN',
    '윤노동 보고와 부합하는 전염병 지속 환경.'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD001',
    'CTX_F005',
    'M1',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD002',
    'CTX_F006',
    'M1',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD003',
    'CTX_F007',
    'M1',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD004',
    'CTX_F008',
    'M1',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD005',
    'CTX_F009',
    'M1',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD006',
    'CTX_F010',
    'M1',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD007',
    'CTX_F020',
    'M1',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD008',
    'CTX_F002',
    'M2',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD009',
    'CTX_F004',
    'M2',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD010',
    'CTX_F009',
    'M2',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD011',
    'CTX_F020',
    'M2',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD012',
    'CTX_F007',
    'M3',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD013',
    'CTX_F020',
    'M3',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD014',
    'CTX_F006',
    'M4',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD015',
    'CTX_F008',
    'M4',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD016',
    'CTX_F009',
    'M4',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD017',
    'CTX_F010',
    'M4',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD018',
    'CTX_F006',
    'M5',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD019',
    'CTX_F011',
    'M5',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD020',
    'CTX_F012',
    'M5',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD021',
    'CTX_F013',
    'M5',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD022',
    'CTX_F014',
    'M5',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD023',
    'CTX_F017',
    'M5',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD024',
    'CTX_F018',
    'M5',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD025',
    'CTX_F020',
    'M5',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD026',
    'CTX_F006',
    'M6',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD027',
    'CTX_F020',
    'M6',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD028',
    'CTX_F002',
    'MB',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD029',
    'CTX_F003',
    'MB',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD030',
    'CTX_F004',
    'MB',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD031',
    'CTX_F015',
    'MB',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD032',
    'CTX_F016',
    'MB',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD033',
    'ENV01',
    'MB',
    'CONTEXT_COMPATIBLE',
    'CONTEXT',
    'SUPER_DAG',
    '질병·사망 설명의 환경적 호환성만(개인 감염 확정 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD034',
    'ENV02',
    'MB',
    'CONTEXT_COMPATIBLE',
    'CONTEXT',
    'SUPER_DAG',
    '질병·사망 설명의 환경적 호환성만(개인 감염 확정 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD035',
    'ENV03',
    'MB',
    'CONTEXT_COMPATIBLE',
    'CONTEXT',
    'SUPER_DAG',
    '질병·사망 설명의 환경적 호환성만(개인 감염 확정 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD036',
    'ENV04',
    'MB',
    'CONTEXT_COMPATIBLE',
    'CONTEXT',
    'SUPER_DAG',
    '질병·사망 설명의 환경적 호환성만(개인 감염 확정 아님)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD037',
    'CTX_F007',
    'V_ARREST_PATH',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '병사 → 장교 체포 명령의 제도 적합성(INSTITUTIONALLY_COMPATIBLE)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD038',
    'CTX_F008',
    'V_ARREST_PATH',
    'CONSTRAINS',
    'CONTEXT',
    'SUPER_DAG',
    '병사 → 장교 체포 명령의 제도 적합성(INSTITUTIONALLY_COMPATIBLE)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD039',
    'M1',
    'G01a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD040',
    'G01a',
    'V_COMPLAINT_TO_BARRACKS',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD041',
    'M1',
    'G01b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD042',
    'G01b',
    'V_COMPLAINT_TO_BARRACKS',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD043',
    'M1',
    'G01c',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD044',
    'G01c',
    'V_COMPLAINT_TO_BARRACKS',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD045',
    'M1',
    'G02a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD046',
    'G02a',
    'V_COMMAND_SOURCE',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD047',
    'M4',
    'G02b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD048',
    'G02b',
    'V_COMMAND_SOURCE',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD049',
    'M4',
    'G02c',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD050',
    'M1',
    'G03a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD051',
    'G03a',
    'V_INFO_TO_COMMANDER',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD052',
    'M1',
    'G03b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD053',
    'G03b',
    'V_INFO_TO_COMMANDER',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD054',
    'M4',
    'G03c',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD055',
    'G03c',
    'V_INFO_TO_COMMANDER',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD056',
    'M1',
    'G04a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD057',
    'G04a',
    'V_INFO_TO_COMMANDER',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD058',
    'M2',
    'G04b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD059',
    'G04b',
    'V_INFO_TO_COMMANDER',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD060',
    'G04b',
    'V_INVESTIGATION_SCOPE',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD061',
    'M3',
    'G04c',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD062',
    'G04c',
    'V_INFO_TO_COMMANDER',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD063',
    'M2',
    'G04d',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD064',
    'G04d',
    'V_INFO_TO_COMMANDER',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD065',
    'G04d',
    'V_INVESTIGATION_SCOPE',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD066',
    'M3',
    'G04e',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD067',
    'M3',
    'G05a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD068',
    'M3',
    'G05b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD069',
    'MB',
    'G06a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD070',
    'G06a',
    'V_CUSTODY_COURSE',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD071',
    'MB',
    'G06b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD072',
    'G06b',
    'V_CUSTODY_COURSE',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD073',
    'MB',
    'G06c',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD074',
    'M6',
    'G07a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD075',
    'G07a',
    'V_INITIAL_JUDGMENT_BASIS',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD076',
    'M2',
    'G07b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD077',
    'M6',
    'G07b',
    'INSTANTIATED_BY_SECONDARY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조 메커니즘'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD078',
    'G07b',
    'V_INITIAL_JUDGMENT_BASIS',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD079',
    'M2',
    'G07c',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD080',
    'M6',
    'G07c',
    'INSTANTIATED_BY_SECONDARY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조 메커니즘'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD081',
    'G07c',
    'V_INITIAL_JUDGMENT_BASIS',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD082',
    'M6',
    'G07d',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD083',
    'M5',
    'G08a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD084',
    'G08a',
    'V_REVIEW_CORRECTION',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD085',
    'M5',
    'G08b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'core'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD086',
    'G08b',
    'V_REVIEW_CORRECTION',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD087',
    'M5',
    'G09a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD088',
    'M5',
    'G09b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD089',
    'M5',
    'G09c',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD090',
    'M5',
    'G10a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD091',
    'M5',
    'G10b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD092',
    'M5',
    'G10c',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD093',
    'M4',
    'G11a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD094',
    'G11a',
    'V_INVESTIGATION_SCOPE',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD095',
    'M1',
    'G11b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD096',
    'M4',
    'G11c',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD097',
    'MB',
    'G12a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD098',
    'G12a',
    'V_CUSTODY_COURSE',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD099',
    'MB',
    'G12b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD100',
    'M5',
    'G13a',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD101',
    'G13a',
    'V_REVIEW_CORRECTION',
    'CONTRIBUTES_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 규칙 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD102',
    'M5',
    'G13b',
    'INSTANTIATED_BY',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '보조'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD103',
    'M5',
    'V_REVIEW_CORRECTION',
    'ANCHORED_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    'M5는 관측 재검토 backbone에 고정'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD104',
    'V_REVIEW_CORRECTION',
    'EP18',
    'EXPLAINS_OBSERVED',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '관측 재검토 사건을 설명(사건 자체는 OBSERVED 그대로)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD105',
    'V_REVIEW_CORRECTION',
    'EP20',
    'EXPLAINS_OBSERVED',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '관측 재검토 사건을 설명(사건 자체는 OBSERVED 그대로)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD106',
    'V_REVIEW_CORRECTION',
    'EP22',
    'EXPLAINS_OBSERVED',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '관측 재검토 사건을 설명(사건 자체는 OBSERVED 그대로)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD107',
    'V_REVIEW_CORRECTION',
    'EP23',
    'EXPLAINS_OBSERVED',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '관측 재검토 사건을 설명(사건 자체는 OBSERVED 그대로)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD108',
    'V_REVIEW_CORRECTION',
    'EP25',
    'EXPLAINS_OBSERVED',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '관측 재검토 사건을 설명(사건 자체는 OBSERVED 그대로)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD109',
    'V_COMPLAINT_TO_BARRACKS',
    'EP04',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '소장·체포령(EP03)이 2/28 병영 출동(EP04)으로 이어지는 경로'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD110',
    'V_COMMAND_SOURCE',
    'EP04',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '2/28 출동 지시의 상위 출처'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD111',
    'V_INFO_TO_COMMANDER',
    'EP09',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '구순 쪽 정보·진술이 3/4 병사의 체포 지시(EP09)에 닿는 경로'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD112',
    'V_ARREST_PATH',
    'EP11',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '체포 지시(EP09, OBSERVED) → 체포 실행(EP11, OBSERVED)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD113',
    'V_INVESTIGATION_SCOPE',
    'EP11',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '수사 범위가 여러 혐의자로 넓어지는 구조(김갑득 동시 체포, 공주진 선행 체포 등)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD114',
    'V_INITIAL_JUDGMENT_BASIS',
    'EP15',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '5/12 ''도난 없음 방향'' 판단(EP15, OBSERVED)의 근거 형성'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD115',
    'V_RESPONSIBILITY',
    'EP29',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '정조의 책임 귀속(EP29·EP30, OBSERVED)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD116',
    'V_RESPONSIBILITY',
    'EP30',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '정조의 책임 귀속(EP29·EP30, OBSERVED)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD117',
    'V_SANCTION',
    'EP33',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '처분(OBSERVED, 모든 world 공통)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD118',
    'V_SANCTION',
    'EP34',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '처분(OBSERVED, 모든 world 공통)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD119',
    'V_SANCTION',
    'EP35',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '처분(OBSERVED, 모든 world 공통)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD120',
    'V_SANCTION',
    'EP36',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '처분(OBSERVED, 모든 world 공통)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD121',
    'V_SANCTION',
    'EP37',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '처분(OBSERVED, 모든 world 공통)'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD122',
    'V_CUSTODY_COURSE',
    'EP13',
    'EXPLAINS_TRANSITION_TO',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '구금 중 발병·사망 경과(사망 branch A). 책임 branch와 연결하지 않음'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD123',
    'V_INFO_TO_COMMANDER',
    'V_ARREST_PATH',
    'RULE_INPUT',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 구조 규칙의 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD124',
    'V_ARREST_PATH',
    'V_RESPONSIBILITY',
    'RULE_INPUT',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 구조 규칙의 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD125',
    'V_REVIEW_CORRECTION',
    'V_RESPONSIBILITY',
    'RULE_INPUT',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 구조 규칙의 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD126',
    'V_RESPONSIBILITY',
    'V_SANCTION',
    'RULE_INPUT',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 구조 규칙의 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD127',
    'V_COMPLAINT_TO_BARRACKS',
    'V_COMMAND_SOURCE',
    'RULE_INPUT',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 구조 규칙의 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD128',
    'V_COMMAND_SOURCE',
    'V_INFO_TO_COMMANDER',
    'RULE_INPUT',
    'LATENT_MECHANISM',
    'SUPER_DAG',
    '질적 구조 규칙의 입력'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD129',
    'U_ID06',
    'G04a',
    'CONDITIONS',
    'UNRESOLVED',
    'SUPER_DAG',
    '확정하지 않은 동일성·범위·사유. 이 후보의 성립 조건으로만 남는다'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD130',
    'U_ID07',
    'G02a',
    'CONDITIONS',
    'UNRESOLVED',
    'SUPER_DAG',
    '확정하지 않은 동일성·범위·사유. 이 후보의 성립 조건으로만 남는다'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD131',
    'U_OE007',
    'G04b',
    'CONDITIONS',
    'UNRESOLVED',
    'SUPER_DAG',
    '확정하지 않은 동일성·범위·사유. 이 후보의 성립 조건으로만 남는다'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD132',
    'U_OE007',
    'G09a',
    'CONDITIONS',
    'UNRESOLVED',
    'SUPER_DAG',
    '확정하지 않은 동일성·범위·사유. 이 후보의 성립 조건으로만 남는다'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD133',
    'U_OE062',
    'G06a',
    'CONDITIONS',
    'UNRESOLVED',
    'SUPER_DAG',
    '확정하지 않은 동일성·범위·사유. 이 후보의 성립 조건으로만 남는다'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD134',
    'U_OE062',
    'G06b',
    'CONDITIONS',
    'UNRESOLVED',
    'SUPER_DAG',
    '확정하지 않은 동일성·범위·사유. 이 후보의 성립 조건으로만 남는다'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD135',
    'U_G10',
    'G10a',
    'CONDITIONS',
    'UNRESOLVED',
    'SUPER_DAG',
    '확정하지 않은 동일성·범위·사유. 이 후보의 성립 조건으로만 남는다'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD136',
    'U_G10',
    'G10b',
    'CONDITIONS',
    'UNRESOLVED',
    'SUPER_DAG',
    '확정하지 않은 동일성·범위·사유. 이 후보의 성립 조건으로만 남는다'
);
INSERT INTO STG_SD_EDGES (EDGE_ID, SRC, DST, EDGE_TYPE, SD_STATUS, ORIGIN, NOTE)
VALUES (
    'SD137',
    'U_G10',
    'G10c',
    'CONDITIONS',
    'UNRESOLVED',
    'SUPER_DAG',
    '확정하지 않은 동일성·범위·사유. 이 후보의 성립 조건으로만 남는다'
);

-- output/clean/mechanism_definitions.csv (7행)
INSERT INTO STG_MECHANISM_DEFINITIONS (MECHANISM_ID, MECHANISM_NAME, EASY_DESCRIPTION, RELATED_CANDIDATES, RELATED_OBSERVED_NODES, REQUIRED_INST_FEATURES, RELATED_ENV_FEATURES, EVIDENCE_STATUS, REMARKS, N_CANDIDATES, BRANCH)
VALUES (
    'M1',
    'M1_OFFICIAL_INFORMATION_ROUTE',
    '구순 쪽 소장·정보가 진영·병영 비장·병사로 이어지는 공식 보고·지휘 경로를 따라 이동하는 구조',
    'G01a|G01b|G01c|G02a|G03a|G03b|G04a|G11b',
    'EP03|EP04|EP05|EP08|EP09',
    'F005|F006|F007|F008|F009|F010|F020',
    '-',
    'MEDIUM 4 / LOW 1 / NONE 3',
    '공식 경로가 제도상 가능하다는 것(F007·F008)은 경로가 실제로 쓰였다는 근거가 아니다.',
    '8',
    'B_PROCEDURAL'
);
INSERT INTO STG_MECHANISM_DEFINITIONS (MECHANISM_ID, MECHANISM_NAME, EASY_DESCRIPTION, RELATED_CANDIDATES, RELATED_OBSERVED_NODES, REQUIRED_INST_FEATURES, RELATED_ENV_FEATURES, EVIDENCE_STATUS, REMARKS, N_CANDIDATES, BRANCH)
VALUES (
    'M2',
    'M2_TESTIMONY_AMPLIFICATION',
    '자미덕 등의 진술·대질·번복이 수사 범위나 판단 자료를 키우거나 바꾸는 구조',
    'G04b|G04d|G07b|G07c',
    'EP07|EP09|EP13|EP15',
    'F002|F004|F009|F020',
    '-',
    'MEDIUM 1 / LOW 3',
    '회유 행위 자체의 합법성은 LOW(F002, EP07 feature link)다. 진술이 보고 경로를 탄다는 정보 흐름만 MEDIUM이다.',
    '4',
    'B_PROCEDURAL'
);
INSERT INTO STG_MECHANISM_DEFINITIONS (MECHANISM_ID, MECHANISM_NAME, EASY_DESCRIPTION, RELATED_CANDIDATES, RELATED_OBSERVED_NODES, REQUIRED_INST_FEATURES, RELATED_ENV_FEATURES, EVIDENCE_STATUS, REMARKS, N_CANDIDATES, BRANCH)
VALUES (
    'M3',
    'M3_PRIVATE_INFLUENCE_CHANNEL',
    '구순과 병영 지휘관 사이의 비공식·사적 통로(서신·접촉)를 통해 정보나 영향이 전달되는 구조',
    'G04c|G04e|G05a|G05b',
    'EP01|EP09|EP10|EP11|EP30',
    'F007|F020',
    '-',
    'LOW 2 · 분석 제외 G04e|G05b',
    '구순(전 부사)에게는 병영 지휘권이 없다(F007 role LOW). 그래서 M3는 ''명령''이 아니라 ''정보·영향 제공''으로만 쓸 수 있다(G04e INCOMPATIBLE).',
    '4',
    'B_PROCEDURAL'
);
INSERT INTO STG_MECHANISM_DEFINITIONS (MECHANISM_ID, MECHANISM_NAME, EASY_DESCRIPTION, RELATED_CANDIDATES, RELATED_OBSERVED_NODES, REQUIRED_INST_FEATURES, RELATED_ENV_FEATURES, EVIDENCE_STATUS, REMARKS, N_CANDIDATES, BRANCH)
VALUES (
    'M4',
    'M4_DISTRIBUTED_INSTITUTIONAL_ACTION',
    '하나의 중앙 지휘가 아니라 비장·아전·진(鎭) 등 여러 기관·실무자의 판단이 따로 쌓이는 구조',
    'G02b|G02c|G03c|G11a|G11c',
    'EP04|EP05|EP08|EP09',
    'F006|F008|F009|F010',
    '-',
    'LOW 2 / NONE 1 · 분석 제외 G02c|G11c',
    'F006(관찰사 감독)·F009(비장 막료)는 분산 실무의 여지를 주지만, 그 자체가 분산 행동의 근거는 아니다.',
    '5',
    'B_PROCEDURAL'
);
INSERT INTO STG_MECHANISM_DEFINITIONS (MECHANISM_ID, MECHANISM_NAME, EASY_DESCRIPTION, RELATED_CANDIDATES, RELATED_OBSERVED_NODES, REQUIRED_INST_FEATURES, RELATED_ENV_FEATURES, EVIDENCE_STATUS, REMARKS, N_CANDIDATES, BRANCH)
VALUES (
    'M5',
    'M5_REVIEW_AND_CORRECTION',
    '초기 판단을 암행어사·안핵어사·비변사·국왕 심리가 따로 다시 검토하고 고치는 구조',
    'G08a|G08b|G09a|G09b|G09c|G10a|G10b|G10c|G13a|G13b',
    'EP04|EP07|EP15|EP16|EP17|EP18|EP19|EP20|EP21|EP22|EP23|EP24|EP25|EP26|EP27|EP28|EP29|EP30|EP31|EP32|EP33|EP34|EP35|EP36|EP37',
    'F006|F011|F012|F013|F014|F017|F018|F020',
    '-',
    '관측 backbone 고정(OBSERVED) · 내부 세부 후보: MEDIUM 1 / LOW 4 / NONE 2 · 분석 제외 G09b|G09c|G13b',
    '재검토 과정 자체(5/12 → 5/27 → 5/28 → 6/11 → 6/13 → 처분)는 OBSERVED backbone이다. M5는 그 backbone을 설명하는 분석 변수이고, LATENT 후보(G08·G09·G10·G13)는 동기·근거·실행 같은 내부 세부만 다룬다. 관측 사건을 LATENT로 바꾸지 않는다.',
    '10',
    'REVIEW'
);
INSERT INTO STG_MECHANISM_DEFINITIONS (MECHANISM_ID, MECHANISM_NAME, EASY_DESCRIPTION, RELATED_CANDIDATES, RELATED_OBSERVED_NODES, REQUIRED_INST_FEATURES, RELATED_ENV_FEATURES, EVIDENCE_STATUS, REMARKS, N_CANDIDATES, BRANCH)
VALUES (
    'M6',
    'M6_INITIAL_JUDGMENT_BASIS',
    '5월 단계의 ''도난 없음 방향'' 판단이 어떤 자료·추론에서 형성되었는지에 관한 구조',
    'G07a|G07d (보조: G07b|G07c)',
    'EP13|EP15|EP25',
    'F006|F020',
    '-',
    'LOW 1 · 분석 제외 G07d',
    'G07 계열이 반복되는 패턴이라 추가했다. 5월 판단 자체(EP15)는 OBSERVED이고, 그 근거만 LATENT다.',
    '2',
    'REVIEW'
);
INSERT INTO STG_MECHANISM_DEFINITIONS (MECHANISM_ID, MECHANISM_NAME, EASY_DESCRIPTION, RELATED_CANDIDATES, RELATED_OBSERVED_NODES, REQUIRED_INST_FEATURES, RELATED_ENV_FEATURES, EVIDENCE_STATUS, REMARKS, N_CANDIDATES, BRANCH)
VALUES (
    'MB',
    'MB_CUSTODY_BIOLOGICAL_COURSE',
    '체포 뒤 구금 중 발병·사망 경과에 관한 구조(사망 branch A: 생물학적 사인)',
    'G06a|G06b|G06c|G12a|G12b',
    'EP11|EP13|EP27',
    'F002|F003|F004|F015|F016',
    'E001|E002|E003|E004',
    'MEDIUM 1 / LOW 2 · 분석 제외 G06c|G12b',
    '환경 피쳐는 질병·사망 설명의 호환성만 제약한다. 김명신 개인의 감염을 확정하지 않는다. 책임 branch(M1–M4)와 연결하지 않는다.',
    '5',
    'A_BIOLOGICAL'
);

-- output/clean/world_mechanism_configurations.csv (6행)
INSERT INTO STG_WORLD_MECH_CONFIGS (WORLD_ID, ROLE_TYPE, M1, M2, M3, M4, M5, M6, MB, M1_BASIS, M2_BASIS, M3_BASIS, M4_BASIS, M5_BASIS, M6_BASIS, MB_BASIS, LATENT_BRIDGES)
VALUES (
    'W1',
    'COMPETING_EXPLANATION',
    'ON',
    'UNSPECIFIED',
    'PARTIAL',
    'PARTIAL',
    'ON',
    'ON',
    'ON',
    'core G01a, G02a, G03a, G04a',
    '관련 후보 없음',
    '보조 G05a',
    '보조 G11a',
    '관측 재검토 backbone(EP15–EP37)에 고정; 내부 세부 G08a, G09a, G13a',
    'core G07a',
    'core G06a; 보조 G12a',
    'G01a|G02a|G03a|G04a|G05a|G06a|G07a|G08a|G09a|G11a|G12a|G13a'
);
INSERT INTO STG_WORLD_MECH_CONFIGS (WORLD_ID, ROLE_TYPE, M1, M2, M3, M4, M5, M6, MB, M1_BASIS, M2_BASIS, M3_BASIS, M4_BASIS, M5_BASIS, M6_BASIS, MB_BASIS, LATENT_BRIDGES)
VALUES (
    'W2',
    'COMPETING_EXPLANATION',
    'PARTIAL',
    'ON',
    'UNSPECIFIED',
    'ON',
    'ON',
    'PARTIAL',
    'ON',
    'core G01a, G03a; 부정 G02b',
    'core G04b; 보조 G07c',
    '관련 후보 없음',
    'core G02b',
    '관측 재검토 backbone(EP15–EP37)에 고정; 내부 세부 G08a, G09a',
    '보조 G07c',
    'core G06b; 보조 G12a',
    'G01a|G02b|G03a|G04b|G06b|G07c|G08a|G09a|G12a'
);
INSERT INTO STG_WORLD_MECH_CONFIGS (WORLD_ID, ROLE_TYPE, M1, M2, M3, M4, M5, M6, MB, M1_BASIS, M2_BASIS, M3_BASIS, M4_BASIS, M5_BASIS, M6_BASIS, MB_BASIS, LATENT_BRIDGES)
VALUES (
    'W3',
    'COMPETING_EXPLANATION',
    'PARTIAL',
    'UNSPECIFIED',
    'ON',
    'UNSPECIFIED',
    'ON',
    'ON',
    'ON',
    'core G01b, G02a',
    '관련 후보 없음',
    'core G04c; 보조 G05a',
    '관련 후보 없음',
    '관측 재검토 backbone(EP15–EP37)에 고정; 내부 세부 G08a',
    'core G07a',
    'core G06a; 보조 G12a',
    'G01b|G02a|G04c|G05a|G06a|G07a|G08a|G12a'
);
INSERT INTO STG_WORLD_MECH_CONFIGS (WORLD_ID, ROLE_TYPE, M1, M2, M3, M4, M5, M6, MB, M1_BASIS, M2_BASIS, M3_BASIS, M4_BASIS, M5_BASIS, M6_BASIS, MB_BASIS, LATENT_BRIDGES)
VALUES (
    'W4',
    'COMPETING_EXPLANATION',
    'PARTIAL',
    'PARTIAL',
    'UNSPECIFIED',
    'ON',
    'ON',
    'PARTIAL',
    'ON',
    'core G01a; 부정 G02b',
    '보조 G07b',
    '관련 후보 없음',
    'core G02b, G03c; 보조 G11a',
    '관측 재검토 backbone(EP15–EP37)에 고정; 내부 세부 G08b, G13a',
    '보조 G07b',
    'core G06a',
    'G01a|G02b|G03c|G06a|G07b|G08b|G11a|G13a'
);
INSERT INTO STG_WORLD_MECH_CONFIGS (WORLD_ID, ROLE_TYPE, M1, M2, M3, M4, M5, M6, MB, M1_BASIS, M2_BASIS, M3_BASIS, M4_BASIS, M5_BASIS, M6_BASIS, MB_BASIS, LATENT_BRIDGES)
VALUES (
    'W5',
    'COMPETING_EXPLANATION',
    'PARTIAL',
    'UNSPECIFIED',
    'UNSPECIFIED',
    'UNSPECIFIED',
    'ON',
    'ON',
    'ON',
    'core G01a',
    '관련 후보 없음',
    '관련 후보 없음',
    '관련 후보 없음',
    '관측 재검토 backbone(EP15–EP37)에 고정; 내부 세부 G08a',
    'core G07a',
    'core G06a',
    'G01a|G06a|G07a|G08a'
);
INSERT INTO STG_WORLD_MECH_CONFIGS (WORLD_ID, ROLE_TYPE, M1, M2, M3, M4, M5, M6, MB, M1_BASIS, M2_BASIS, M3_BASIS, M4_BASIS, M5_BASIS, M6_BASIS, MB_BASIS, LATENT_BRIDGES)
VALUES (
    'W6',
    'REJECTED',
    'UNSPECIFIED',
    'UNSPECIFIED',
    'UNSPECIFIED',
    'UNSPECIFIED',
    'ON',
    'ON',
    'ON',
    '관련 후보 없음',
    '관련 후보 없음',
    '관련 후보 없음',
    '관련 후보 없음',
    '관측 재검토 backbone(EP15–EP37)에 고정',
    'core G07d',
    'core G06c; 보조 G12b',
    'G06c|G07d|G12b'
);

-- output/clean/mechanism_interaction_matrix.csv (21행)
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M1',
    'M2',
    'PARTIALLY_COMPATIBLE',
    '일부 후보 쌍이 충돌하지만(G03b×G04b), 다른 후보로는 W2에서 함께 쓰인다. 같은 전이(G04)를 서로 다른 방식으로 설명하는 후보가 있다.',
    'G03b×G04b',
    '공식 보고 경로로 들어온 정보에 대질 진술이 더해져 3/4 지시의 근거가 되는 경우(어느 world도 두 입력을 함께 쓰지 않음)',
    'SUBSTITUTE|COMPLEMENT',
    'W2',
    'M1_OFFICIAL_INFORMATION_ROUTE',
    'M2_TESTIMONY_AMPLIFICATION'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M1',
    'M3',
    'COMPATIBLE',
    '충돌하는 후보·edge가 없고, W1, W3에서 함께 쓰인다. 같은 전이(G04)를 서로 다른 방식으로 설명하는 후보가 있다.',
    NULL,
    '공식 지휘·이관(G01·G02) 위에 사적 통로가 겹쳐 병사의 판단에 영향을 주는 경우(W3)',
    'SUBSTITUTE|COMPLEMENT',
    'W1, W3',
    'M1_OFFICIAL_INFORMATION_ROUTE',
    'M3_PRIVATE_INFLUENCE_CHANNEL'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M1',
    'M4',
    'PARTIALLY_COMPATIBLE',
    '일부 후보 쌍이 충돌하지만(G03c×G04a; G02b(→M1 부정)), 다른 후보로는 W1, W2, W4에서 함께 쓰인다. 같은 전이(G02, G03, G11)를 서로 다른 방식으로 설명하는 후보가 있다.',
    'G03c×G04a; G02b(→M1 부정)',
    '소장 이관은 공식 경로로, 출동 지시는 비장의 자체 판단으로 이루어지는 경우(W2·W4). 병사 지시(G02a)와 비장 자체 판단(G02b)은 함께 쓸 수 없다',
    'EXCLUSIVE_ALTERNATIVE|COMPLEMENT',
    'W1, W2, W4',
    'M1_OFFICIAL_INFORMATION_ROUTE',
    'M4_DISTRIBUTED_INSTITUTIONAL_ACTION'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M1',
    'M5',
    'COMPATIBLE',
    'M5는 관측 재검토 backbone에 고정되어 있어 다른 메커니즘과 함께 존재한다. 다른 메커니즘은 재검토 이전의 경로를 설명한다.',
    NULL,
    '초기 판단의 형성과 그 독립 재검토·수정이 한 흐름으로 설명된다',
    'INDEPENDENT',
    'W1, W2, W3, W4, W5',
    'M1_OFFICIAL_INFORMATION_ROUTE',
    'M5_REVIEW_AND_CORRECTION'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M1',
    'M6',
    'COMPATIBLE',
    '충돌하는 후보·edge가 없고, W1, W3, W5에서 함께 쓰인다.',
    NULL,
    '공식 경로로 진행된 수사의 결과(장물 부재)가 5월 판단의 근거가 되는 경우(W1·W3·W5)',
    'COMPLEMENT',
    'W1, W3, W5',
    'M1_OFFICIAL_INFORMATION_ROUTE',
    'M6_INITIAL_JUDGMENT_BASIS'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M1',
    'MB',
    'COMPATIBLE',
    'MB는 사망 branch A(생물학적 경과)다. 절차·책임 메커니즘과 연결되지 않으므로 함께 있어도 충돌하지 않는다.',
    NULL,
    '책임 경로와 사인 경로가 따로 설명된다(서로를 설명하지 않음)',
    'INDEPENDENT',
    'W1, W2, W3, W4, W5',
    'M1_OFFICIAL_INFORMATION_ROUTE',
    'MB_CUSTODY_BIOLOGICAL_COURSE'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M2',
    'M3',
    'COMPATIBLE',
    '충돌하는 후보 쌍·부정 관계·제도 제약이 없다. 다만 어느 world도 둘을 함께 쓰지 않아, 함께 작동했는지는 사료로 결정되지 않는다(UNRESOLVED). 같은 전이(G04)를 서로 다른 방식으로 설명하는 후보가 있다.',
    NULL,
    '진술 증폭과 사적 통로가 각각 3/4 지시의 입력이 되는 경우(어느 world도 함께 쓰지 않음)',
    'SUBSTITUTE',
    NULL,
    'M2_TESTIMONY_AMPLIFICATION',
    'M3_PRIVATE_INFLUENCE_CHANNEL'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M2',
    'M4',
    'COMPATIBLE',
    '충돌하는 후보·edge가 없고, W2, W4에서 함께 쓰인다.',
    NULL,
    '분산된 실무 안에서 대질 진술이 수사 범위를 넓히는 경우(W2·W4)',
    'COMPLEMENT',
    'W2, W4',
    'M2_TESTIMONY_AMPLIFICATION',
    'M4_DISTRIBUTED_INSTITUTIONAL_ACTION'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M2',
    'M5',
    'COMPATIBLE',
    'M5는 관측 재검토 backbone에 고정되어 있어 다른 메커니즘과 함께 존재한다. 다른 메커니즘은 재검토 이전의 경로를 설명한다.',
    NULL,
    '초기 판단의 형성과 그 독립 재검토·수정이 한 흐름으로 설명된다',
    'INDEPENDENT',
    'W2, W4',
    'M2_TESTIMONY_AMPLIFICATION',
    'M5_REVIEW_AND_CORRECTION'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M2',
    'M6',
    'COMPATIBLE',
    '충돌하는 후보·edge가 없고, W2에서 함께 쓰인다. 같은 전이(G07)를 서로 다른 방식으로 설명하는 후보가 있다.',
    NULL,
    '5월 판단의 근거가 장물 부재 추론과 진술 자료(회동 응답·번복)로 함께 형성되는 경우',
    'SUBSTITUTE|COMPLEMENT',
    'W2',
    'M2_TESTIMONY_AMPLIFICATION',
    'M6_INITIAL_JUDGMENT_BASIS'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M2',
    'MB',
    'COMPATIBLE',
    'MB는 사망 branch A(생물학적 경과)다. 절차·책임 메커니즘과 연결되지 않으므로 함께 있어도 충돌하지 않는다.',
    NULL,
    '책임 경로와 사인 경로가 따로 설명된다(서로를 설명하지 않음)',
    'INDEPENDENT',
    'W2, W4',
    'M2_TESTIMONY_AMPLIFICATION',
    'MB_CUSTODY_BIOLOGICAL_COURSE'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M3',
    'M4',
    'COMPATIBLE',
    '충돌하는 후보 쌍·부정 관계·제도 제약이 없다. 다만 어느 world도 둘을 함께 쓰지 않아, 함께 작동했는지는 사료로 결정되지 않는다(UNRESOLVED).',
    NULL,
    '분산된 실무와 사적 통로가 동시에 있는 경우(어느 world도 함께 쓰지 않음)',
    'NO_SHARED_TRANSITION',
    NULL,
    'M3_PRIVATE_INFLUENCE_CHANNEL',
    'M4_DISTRIBUTED_INSTITUTIONAL_ACTION'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M3',
    'M5',
    'COMPATIBLE',
    'M5는 관측 재검토 backbone에 고정되어 있어 다른 메커니즘과 함께 존재한다. 다른 메커니즘은 재검토 이전의 경로를 설명한다.',
    NULL,
    '초기 판단의 형성과 그 독립 재검토·수정이 한 흐름으로 설명된다',
    'INDEPENDENT',
    'W1, W3',
    'M3_PRIVATE_INFLUENCE_CHANNEL',
    'M5_REVIEW_AND_CORRECTION'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M3',
    'M6',
    'COMPATIBLE',
    '충돌하는 후보·edge가 없고, W1, W3에서 함께 쓰인다.',
    NULL,
    '사적 통로와 5월 판단 근거 형성은 서로 다른 단계를 설명한다(W3)',
    'COMPLEMENT',
    'W1, W3',
    'M3_PRIVATE_INFLUENCE_CHANNEL',
    'M6_INITIAL_JUDGMENT_BASIS'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M3',
    'MB',
    'COMPATIBLE',
    'MB는 사망 branch A(생물학적 경과)다. 절차·책임 메커니즘과 연결되지 않으므로 함께 있어도 충돌하지 않는다.',
    NULL,
    '책임 경로와 사인 경로가 따로 설명된다(서로를 설명하지 않음)',
    'INDEPENDENT',
    'W1, W3',
    'M3_PRIVATE_INFLUENCE_CHANNEL',
    'MB_CUSTODY_BIOLOGICAL_COURSE'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M4',
    'M5',
    'COMPATIBLE',
    'M5는 관측 재검토 backbone에 고정되어 있어 다른 메커니즘과 함께 존재한다. 다른 메커니즘은 재검토 이전의 경로를 설명한다.',
    NULL,
    '초기 판단의 형성과 그 독립 재검토·수정이 한 흐름으로 설명된다',
    'INDEPENDENT',
    'W1, W2, W4',
    'M4_DISTRIBUTED_INSTITUTIONAL_ACTION',
    'M5_REVIEW_AND_CORRECTION'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M4',
    'M6',
    'COMPATIBLE',
    '충돌하는 후보·edge가 없고, W1, W2, W4에서 함께 쓰인다.',
    NULL,
    '분산 실무와 5월 판단 근거 형성은 서로 다른 단계를 설명한다(W4)',
    'COMPLEMENT',
    'W1, W2, W4',
    'M4_DISTRIBUTED_INSTITUTIONAL_ACTION',
    'M6_INITIAL_JUDGMENT_BASIS'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M4',
    'MB',
    'COMPATIBLE',
    'MB는 사망 branch A(생물학적 경과)다. 절차·책임 메커니즘과 연결되지 않으므로 함께 있어도 충돌하지 않는다.',
    NULL,
    '책임 경로와 사인 경로가 따로 설명된다(서로를 설명하지 않음)',
    'INDEPENDENT',
    'W1, W2, W4',
    'M4_DISTRIBUTED_INSTITUTIONAL_ACTION',
    'MB_CUSTODY_BIOLOGICAL_COURSE'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M5',
    'M6',
    'COMPATIBLE',
    'M5는 관측 재검토 backbone에 고정되어 있어 다른 메커니즘과 함께 존재한다. 다른 메커니즘은 재검토 이전의 경로를 설명한다.',
    NULL,
    '초기 판단의 형성과 그 독립 재검토·수정이 한 흐름으로 설명된다',
    'INDEPENDENT',
    'W1, W2, W3, W4, W5',
    'M5_REVIEW_AND_CORRECTION',
    'M6_INITIAL_JUDGMENT_BASIS'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M5',
    'MB',
    'COMPATIBLE',
    'M5는 관측 재검토 backbone에 고정되어 있어 다른 메커니즘과 함께 존재한다. 다른 메커니즘은 재검토 이전의 경로를 설명한다.',
    NULL,
    '초기 판단의 형성과 그 독립 재검토·수정이 한 흐름으로 설명된다',
    'INDEPENDENT',
    'W1, W2, W3, W4, W5',
    'M5_REVIEW_AND_CORRECTION',
    'MB_CUSTODY_BIOLOGICAL_COURSE'
);
INSERT INTO STG_MECH_INTERACTIONS (MECHANISM_A_ID, MECHANISM_B_ID, COEXISTENCE, REASON, CONFLICTING_ITEMS, EXPLAINED_TOGETHER, RELATION, COOCCUR_WORLDS, MECHANISM_A_NAME, MECHANISM_B_NAME)
VALUES (
    'M6',
    'MB',
    'COMPATIBLE',
    'MB는 사망 branch A(생물학적 경과)다. 절차·책임 메커니즘과 연결되지 않으므로 함께 있어도 충돌하지 않는다.',
    NULL,
    '책임 경로와 사인 경로가 따로 설명된다(서로를 설명하지 않음)',
    'INDEPENDENT',
    'W1, W2, W3, W4, W5',
    'M6_INITIAL_JUDGMENT_BASIS',
    'MB_CUSTODY_BIOLOGICAL_COURSE'
);

-- output/clean/mechanism_interventions.csv (13행)
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M1',
    'V_COMPLAINT_TO_BARRACKS',
    'EP04',
    'PATH_BREAKS',
    'G01a|G01b|G01c',
    NULL,
    'W1, W2, W3, W4, W5',
    '이 전이를 채우는 후보가 M1뿐이다(G01a, G01b, G01c). 관측 사건(EP04) 자체는 그대로지만, 그 앞의 설명 경로는 비게 된다(W5처럼 UNSPECIFIED).'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M1',
    'V_COMMAND_SOURCE',
    'EP04',
    'PATH_WEAKENS',
    'G02a',
    'G02b',
    'W1, W2, W3, W4, W5',
    '다른 메커니즘 후보(G02b)로 경로는 남지만, 남은 bridge 근거가 더 약하다 (제거 MEDIUM → 남은 최고 LOW). (XOR: G02a와 G02b는 서로 배타적이라 남은 쪽이 단독으로 설명한다.)'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M1',
    'V_INFO_TO_COMMANDER',
    'EP09',
    'PATH_WEAKENS',
    'G03a|G03b|G04a',
    'G03c|G04b|G04c|G04d',
    'W1, W2, W3, W4, W5',
    '다른 메커니즘 후보(G03c, G04b, G04c, G04d)로 경로는 남지만, 남은 bridge 근거가 더 약하다 (제거 MEDIUM → 남은 최고 LOW).'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M2',
    'V_INFO_TO_COMMANDER',
    'EP09',
    'PATH_REMAINS',
    'G04b|G04d',
    'G03a|G03b|G03c|G04a|G04c',
    'W2, W4',
    '다른 메커니즘 후보(G03a, G03b, G03c, G04a, G04c)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다.'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M2',
    'V_INVESTIGATION_SCOPE',
    'EP11',
    'PATH_REMAINS',
    'G04b|G04d',
    'G11a',
    'W2, W4',
    '다른 메커니즘 후보(G11a)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다.'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M2',
    'V_INITIAL_JUDGMENT_BASIS',
    'EP15',
    'PATH_WEAKENS',
    'G07b|G07c',
    'G07a',
    'W2, W4',
    '다른 메커니즘 후보(G07a)로 경로는 남지만, 남은 bridge 근거가 더 약하다 (제거 MEDIUM → 남은 최고 LOW).'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M3',
    'V_INFO_TO_COMMANDER',
    'EP09',
    'PATH_REMAINS',
    'G04c',
    'G03a|G03b|G03c|G04a|G04b|G04d',
    'W1, W3',
    '다른 메커니즘 후보(G03a, G03b, G03c, G04a, G04b, G04d)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다.'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M4',
    'V_COMMAND_SOURCE',
    'EP04',
    'PATH_REMAINS',
    'G02b',
    'G02a',
    'W1, W2, W4',
    '다른 메커니즘 후보(G02a)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다. (XOR: G02a와 G02b는 서로 배타적이라 남은 쪽이 단독으로 설명한다.)'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M4',
    'V_INFO_TO_COMMANDER',
    'EP09',
    'PATH_REMAINS',
    'G03c',
    'G03a|G03b|G04a|G04b|G04c|G04d',
    'W1, W2, W4',
    '다른 메커니즘 후보(G03a, G03b, G04a, G04b, G04c, G04d)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다.'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M4',
    'V_INVESTIGATION_SCOPE',
    'EP11',
    'PATH_REMAINS',
    'G11a',
    'G04b|G04d',
    'W1, W2, W4',
    '다른 메커니즘 후보(G04b, G04d)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다.'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M5',
    'V_REVIEW_CORRECTION',
    'EP25',
    'PATH_BREAKS',
    'G08a|G08b|G13a',
    NULL,
    '-',
    '재검토 경로는 관측 backbone(EP15 →REVISES→ EP25, EP23 → 판단·처분)이다. M5를 끄면 관측된 판단 수정·처분 경로를 설명할 수 없다. 관측 사실과 양립하지 않으므로 M5는 사실상 OFF로 둘 수 없다.'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'M6',
    'V_INITIAL_JUDGMENT_BASIS',
    'EP15',
    'PATH_REMAINS',
    'G07a',
    'G07b|G07c',
    'W1, W2, W3, W4, W5',
    '다른 메커니즘 후보(G07b, G07c)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다.'
);
INSERT INTO STG_MECH_INTERVENTIONS (MECHANISM, VARIABLE, TARGET, RESULT, REMOVED, REMAINING, AFFECTED_WORLDS, NOTE)
VALUES (
    'MB',
    'V_CUSTODY_COURSE',
    'EP13',
    'PATH_BREAKS',
    'G06a|G06b|G12a',
    NULL,
    'W1, W2, W3, W4, W5',
    '이 전이를 채우는 후보가 MB뿐이다(G06a, G06b, G12a). 관측 사건(EP13) 자체는 그대로지만, 그 앞의 설명 경로는 비게 된다(W5처럼 UNSPECIFIED).'
);

-- output/clean/qualitative_structural_rules.csv (10행)
INSERT INTO STG_STRUCTURAL_RULES (VAR_ID, GAP, TARGET, OP, INPUTS, RULE, RULE_DESC, CONSTRAINT_TEXT, INPUT_CANDIDATES)
VALUES (
    'V_COMPLAINT_TO_BARRACKS',
    'G01',
    'EP04',
    'OR',
    'M1',
    'V_COMPLAINT_TO_BARRACKS = M1_OFFICIAL_INFORMATION_ROUTE',
    '소장·체포령(EP03)이 2/28 병영 출동(EP04)으로 이어지는 경로',
    'F005·F006·F010(접수·이첩 경로의 제도 가능성)',
    'G01a|G01b|G01c'
);
INSERT INTO STG_STRUCTURAL_RULES (VAR_ID, GAP, TARGET, OP, INPUTS, RULE, RULE_DESC, CONSTRAINT_TEXT, INPUT_CANDIDATES)
VALUES (
    'V_COMMAND_SOURCE',
    'G02',
    'EP04',
    'XOR',
    'M1|M4',
    'V_COMMAND_SOURCE = M1_OFFICIAL_INFORMATION_ROUTE(G02a: 병사 지시) XOR M4_DISTRIBUTED_INSTITUTIONAL_ACTION(G02b: 비장 자체 판단)',
    '2/28 출동 지시의 상위 출처',
    'F007·F008·F009(병사 → 비장·장교 지휘의 제도 가능성)',
    'G02a|G02b'
);
INSERT INTO STG_STRUCTURAL_RULES (VAR_ID, GAP, TARGET, OP, INPUTS, RULE, RULE_DESC, CONSTRAINT_TEXT, INPUT_CANDIDATES)
VALUES (
    'V_INFO_TO_COMMANDER',
    'G03|G04',
    'EP09',
    'OR',
    'M1|M2|M3|M4',
    'V_INFO_TO_COMMANDER = M1 OR M2 OR M3 OR M4  (각각 G04a·G03a·G03b / G04b·G04d / G04c / G03c)',
    '구순 쪽 정보·진술이 3/4 병사의 체포 지시(EP09)에 닿는 경로',
    'F007·F020(구순은 명령 불가, 정보 제공만) · F008(보고 경로)',
    'G03a|G03b|G03c|G04a|G04b|G04c|G04d'
);
INSERT INTO STG_STRUCTURAL_RULES (VAR_ID, GAP, TARGET, OP, INPUTS, RULE, RULE_DESC, CONSTRAINT_TEXT, INPUT_CANDIDATES)
VALUES (
    'V_ARREST_PATH',
    NULL,
    'EP11',
    'AND',
    'V_INFO_TO_COMMANDER|INSTITUTIONALLY_COMPATIBLE',
    'V_ARREST_PATH = V_INFO_TO_COMMANDER AND INSTITUTIONALLY_COMPATIBLE(F007·F008: 병사 → 장교 명령)',
    '체포 지시(EP09, OBSERVED) → 체포 실행(EP11, OBSERVED)',
    'F007·F008',
    NULL
);
INSERT INTO STG_STRUCTURAL_RULES (VAR_ID, GAP, TARGET, OP, INPUTS, RULE, RULE_DESC, CONSTRAINT_TEXT, INPUT_CANDIDATES)
VALUES (
    'V_INVESTIGATION_SCOPE',
    'G04|G11',
    'EP11',
    'OR',
    'M2|M4',
    'V_INVESTIGATION_SCOPE = M2_TESTIMONY_AMPLIFICATION OR M4_DISTRIBUTED_INSTITUTIONAL_ACTION',
    '수사 범위가 여러 혐의자로 넓어지는 구조(김갑득 동시 체포, 공주진 선행 체포 등)',
    'F010(도적 수색 관할) · F002(진술 획득 방식의 규범)',
    'G04b|G04d|G11a'
);
INSERT INTO STG_STRUCTURAL_RULES (VAR_ID, GAP, TARGET, OP, INPUTS, RULE, RULE_DESC, CONSTRAINT_TEXT, INPUT_CANDIDATES)
VALUES (
    'V_INITIAL_JUDGMENT_BASIS',
    'G07',
    'EP15',
    'OR',
    'M6|M2',
    'V_INITIAL_JUDGMENT_BASIS = M6_INITIAL_JUDGMENT_BASIS OR M2_TESTIMONY_AMPLIFICATION(보조: G07b·G07c)',
    '5/12 ''도난 없음 방향'' 판단(EP15, OBSERVED)의 근거 형성',
    'F006·F020(장계 → 국왕 판단)',
    'G07a|G07b|G07c'
);
INSERT INTO STG_STRUCTURAL_RULES (VAR_ID, GAP, TARGET, OP, INPUTS, RULE, RULE_DESC, CONSTRAINT_TEXT, INPUT_CANDIDATES)
VALUES (
    'V_REVIEW_CORRECTION',
    'G08|G13',
    'EP25',
    'ANCHORED',
    'M5',
    'V_REVIEW_CORRECTION = M5_REVIEW_AND_CORRECTION  (관측 backbone: EP15 →REVISES→ EP25 등. world마다 달라지지 않음)',
    '5/12 판단 → 5/27 → 5/28 → 6/11 → 6/13 → 처분으로 이어진 독립 재검토·판단 수정(OBSERVED backbone)',
    'F012·F013·F014·F017·F018',
    'G08a|G08b|G13a'
);
INSERT INTO STG_STRUCTURAL_RULES (VAR_ID, GAP, TARGET, OP, INPUTS, RULE, RULE_DESC, CONSTRAINT_TEXT, INPUT_CANDIDATES)
VALUES (
    'V_RESPONSIBILITY',
    'G09',
    'EP29|EP30',
    'AND',
    'V_REVIEW_CORRECTION|V_ARREST_PATH',
    'V_RESPONSIBILITY = V_REVIEW_CORRECTION AND V_ARREST_PATH  (책임 판단은 절차 branch B에만 의존, 사인과 무관)',
    '정조의 책임 귀속(EP29·EP30, OBSERVED)',
    'F018',
    NULL
);
INSERT INTO STG_STRUCTURAL_RULES (VAR_ID, GAP, TARGET, OP, INPUTS, RULE, RULE_DESC, CONSTRAINT_TEXT, INPUT_CANDIDATES)
VALUES (
    'V_SANCTION',
    'G10',
    'EP33|EP34|EP35|EP36|EP37',
    'ANCHORED',
    'V_RESPONSIBILITY',
    'V_SANCTION = V_RESPONSIBILITY  (처분은 관측 사실. G10 사유는 OPEN_UNRESOLVED)',
    '처분(OBSERVED, 모든 world 공통)',
    'F001·F006·F018',
    NULL
);
INSERT INTO STG_STRUCTURAL_RULES (VAR_ID, GAP, TARGET, OP, INPUTS, RULE, RULE_DESC, CONSTRAINT_TEXT, INPUT_CANDIDATES)
VALUES (
    'V_CUSTODY_COURSE',
    'G06|G12',
    'EP13',
    'OR',
    'MB',
    'V_CUSTODY_COURSE = MB_CUSTODY_BIOLOGICAL_COURSE  (환경 E001–E004는 호환성 context. 개인 감염 확정 아님)',
    '구금 중 발병·사망 경과(사망 branch A). 책임 branch와 연결하지 않음',
    'F002·F003·F004·F015·F016 / E001–E004(context)',
    'G06a|G06b|G12a'
);

-- sql/02_load/data/episode_members.csv (52행)
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP01',
    '1',
    'CF001',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP01',
    '2',
    'CF002',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP01',
    '3',
    'CF003',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP02',
    '1',
    'CF004',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP02',
    '2',
    'CF005',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP03',
    '1',
    'CF006',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP04',
    '1',
    'CF007',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP04',
    '2',
    'CF008',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP04',
    '3',
    'CF009',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP04',
    '4',
    'CF010',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP05',
    '1',
    'CF011',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP05',
    '2',
    'CF012',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP06',
    '1',
    'CF013',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP06',
    '2',
    'CF014',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP06',
    '3',
    'CF015',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP07',
    '1',
    'CF016',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP07',
    '2',
    'CF017',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP08',
    '1',
    'CF020',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP09',
    '1',
    'CF021',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP09',
    '2',
    'CF022',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP10',
    '1',
    'CF024',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP11',
    '1',
    'CF023',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP12',
    '1',
    'CF018',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP12',
    '2',
    'CF019',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP13',
    '1',
    'CF027',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP13',
    '2',
    'CF028',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP14',
    '1',
    'CF025',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP14',
    '2',
    'CF026',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP15',
    '1',
    'CF030',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP16',
    '1',
    'CF031',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP17',
    '1',
    'CF032',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP18',
    '1',
    'CF033',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP19',
    '1',
    'CF034',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP20',
    '1',
    'CF035',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP21',
    '1',
    'CF029',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP22',
    '1',
    'CF036',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP23',
    '1',
    'CF037',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP24',
    '1',
    'CF038',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP25',
    '1',
    'CF039',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP26',
    '1',
    'CF040',
    '홍대협은 김명신의 죽음을 질병 때문이라고 평가했고'
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP27',
    '1',
    'CF040',
    '정조는 김명신 부처가 전염병에 걸려 죽은 것으로 판단했다.'
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP27',
    '2',
    'CF041',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP28',
    '1',
    'CF042',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP29',
    '1',
    'CF043',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP30',
    '1',
    'CF044',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP31',
    '1',
    'CF045',
    '홍대협은 여러 차례 신문과 별도 탐문에도 지세 호칭의 기원을 확정하지 못했고'
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP32',
    '1',
    'CF045',
    '정조는 구순이 지세 호칭을 스스로 만들어냈다는 죄는 인정하지 않았다.'
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP33',
    '1',
    'CF046',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP34',
    '1',
    'CF047',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP35',
    '1',
    'CF048',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP36',
    '1',
    'CF049',
    NULL
);
INSERT INTO STG_EPISODE_MEMBERS (EPISODE_ID, MEMBER_SEQ, FACT_ID, CLAUSE)
VALUES (
    'EP37',
    '1',
    'CF050',
    NULL
);

-- sql/02_load/data/py_audit_findings.csv (62행)
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '1',
    'AUDIT1',
    'clause_split',
    'INFO',
    'CF040',
    '2개 절로 분할 — 합치면 원문 전체를 덮음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '2',
    'AUDIT1',
    'clause_split',
    'INFO',
    'CF045',
    '2개 절로 분할 — 합치면 원문 전체를 덮음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '3',
    'AUDIT1',
    'over_merge',
    'INFO',
    'EP09',
    '허용된 혼합 [''IDENT'', ''TESTIMONY''] — 근거: 지시 행위와 지시 대상의 사료 식별은 같은 문장 단위로 묶는다. 실행(EP11)은 분리.'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '4',
    'AUDIT1',
    'clause_prop_alignment',
    'INFO',
    'EP26',
    'CF040 절 → V3P0101'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '5',
    'AUDIT1',
    'clause_prop_alignment',
    'INFO',
    'EP27',
    'CF040 절 → V3P0105'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '6',
    'AUDIT1',
    'clause_prop_alignment',
    'INFO',
    'EP31',
    'CF045 절 → V3P0136'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '7',
    'AUDIT1',
    'clause_prop_alignment',
    'INFO',
    'EP32',
    'CF045 절 → V3P0146'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '8',
    'AUDIT1',
    'resolved_identity',
    'INFO',
    'ID01',
    '공초의 ''병사'' (CF021·CF023·CF024) = 이광섭 · 사용자 확정 · episode summary는 원문 표면형 유지'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '9',
    'AUDIT1',
    'resolved_identity',
    'INFO',
    'ID02',
    '''한 비장'' (CF016·CF017) = 한재욱 · 사용자 확정 · episode summary는 원문 표면형 유지'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '10',
    'AUDIT1',
    'resolved_identity',
    'INFO',
    'ID03',
    '처분문의 ''한가'' (CF048) = 한재욱 · 사용자 확정 · episode summary는 원문 표면형 유지'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '11',
    'AUDIT1',
    'unresolved_identity',
    'UNRESOLVED',
    'ID04',
    '''병영의 하급 보조자'' (audit-only V3P0026·V3P0027·V3P0124) ↔ 한재욱 · 관련 episode 없음(DAG 미사용) · 참고용(model_relevance=NONE, manual_decision_required=NO) · unresolved_reason: audit-only 자료(05, 이조원 주장)에만 있고 인명이 직접 나오지'
        || ' 않는다. 현재 DAG·후보·world 어디에도 쓰이지 않아 결정해도 모델 결과가 바뀌지 않는다(참고용 미해결).'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '12',
    'AUDIT1',
    'resolved_identity',
    'INFO',
    'ID05',
    '''풍각 김상제'' (CF020) = 김명신 · 사용자 확정 · episode summary는 원문 표면형 유지'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '13',
    'AUDIT1',
    'unresolved_identity',
    'UNRESOLVED',
    'ID06',
    '''병영의 염탐 담당자'' (CF043) ↔ 유제희 · 관련 episode EP08, EP29 · unresolved_reason: 정조 판단(CF043)은 직책 표현(''병영의 염탐 담당자'')만 쓰고 이름을 적지 않았다.'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '14',
    'AUDIT1',
    'unresolved_identity',
    'UNRESOLVED',
    'ID07',
    '''철편 네 개'' (CF010, 이진욱: 한재욱이 만들어 줌) ↔ ''철퇴 네 개'' (CF044, 정조: 이광섭이 만들게 함) · 관련 episode EP04, EP30 · unresolved_reason: 개수(네 개)와 사건은 같지만 물건 이름(철편/철퇴)과 행위 층위(제작·지급/제작 지시)가 다르다.'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '15',
    'AUDIT1',
    'unresolved_identity',
    'UNRESOLVED',
    'ID08',
    '3/4 ''장교 일행'' (CF023) ↔ 조계완 포함 여부 (CF024) · 관련 episode EP04, EP10, EP11 · unresolved_reason: 3/4 ''장교 일행''의 구성원은 기록되지 않았다.'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '16',
    'AUDIT1',
    'resolved_identity',
    'INFO',
    'ID11',
    '''원돌'' (CF020 ''원돌 등의 이름'') = 정원돌 (CF009·CF016) · 사용자 확정 · episode summary는 원문 표면형 유지'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '17',
    'AUDIT1',
    'outside_confirmed_set',
    'INFO',
    '05',
    'CF가 참조하지 않는 prop 83개 — DAG node로 쓰지 않음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '18',
    'AUDIT2',
    'partial_tension',
    'UNRESOLVED',
    'OE007',
    'PARTIAL_CONFLICT — 원문 표현의 범위가 같은지 사료로 확정할 수 없어 보존 · review_decision: 사용자 검토: 정면 충돌로 승격하지 않음. 자미덕의 ''지휘'' 주장과 한재욱의 ''은밀한 사주'' 부인은 범위가 완전히 같지 않다. · unresolved_reason: ''한 비장''=한재욱은 ID02 사용자 확정(RESOLVED)이라 같은 '
        || '인물에 대한 두 진술이다. 사주 주장(자미덕)과 은밀한 사주 부인(한재욱)은 서로 다른 진술로 유지하며 어느 쪽도 객관적 사실로 확정하지 않는다. 한재욱의 부인 범위는 ''은밀한 사주''에 한정되므로 PARTIAL 충돌이다.'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '19',
    'AUDIT2',
    'conditional_edge',
    'UNRESOLVED',
    'OE010',
    'ID08 미확정 — edge는 condition으로만 성립 · unresolved_reason: 3/4 ''장교 일행''의 구성원은 기록되지 않았다.'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '20',
    'AUDIT2',
    'unsupported_edge',
    'INFO',
    'OE060',
    '절차 근거로 endpoint 밖 fact 인용: [''CF035'']'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '21',
    'AUDIT2',
    'partial_tension',
    'UNRESOLVED',
    'OE062',
    'UNRESOLVED_SCOPE — 원문 표현의 범위가 같은지 사료로 확정할 수 없어 보존 · review_decision: 사용자 검토: 5월 장계의 ''조사''와 정조의 ''평범한 신문''이 같은 범위인지 확정하지 않음. 부분 긴장 유지. · unresolved_reason: PARTIAL_TENSION: ''조사''가 곧 ''신문''이라고 확정할 수 없다. CF028'
        || '의 ''무고한 평민들 모진 형벌''은 김명신 포함 여부가 열린 집합이므로 충돌 근거로 쓰지 않는다.'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '22',
    'AUDIT2',
    'conditional_edge',
    'UNRESOLVED',
    'OE071',
    'ID06 미확정 — edge는 condition으로만 성립 · unresolved_reason: 정조 판단(CF043)은 직책 표현(''병영의 염탐 담당자'')만 쓰고 이름을 적지 않았다.'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '23',
    'AUDIT2',
    'conditional_edge',
    'UNRESOLVED',
    'OE080',
    'ID07 미확정 — edge는 condition으로만 성립 · unresolved_reason: 개수(네 개)와 사건은 같지만 물건 이름(철편/철퇴)과 행위 층위(제작·지급/제작 지시)가 다르다.'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '24',
    'AUDIT3',
    'freeze_violation',
    'INFO',
    'observed_dag',
    '동결 해시 일치 ccb7ec63763a'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '25',
    'AUDIT3',
    'support_basis_cap',
    'INFO',
    'G01c',
    'INSTITUTIONAL_COMPATIBILITY만 근거 → LOW 상한 적용'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '26',
    'AUDIT3',
    'audit_only_support',
    'INFO',
    'G04d',
    'confirmed 지지 없이 05 흔적만 있음 — LATENT 유지'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '27',
    'AUDIT3',
    'audit_only_support',
    'INFO',
    'G07d',
    'confirmed 지지 없이 05 흔적만 있음 — LATENT 유지'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '28',
    'AUDIT3',
    'resolved_identity_conflict',
    'INFO',
    'G09b',
    '사용자 확정 [''ID02'']과 충돌 → INCOMPATIBLE·PRUNED'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '29',
    'AUDIT3',
    'resolved_identity_conflict',
    'INFO',
    'G09c',
    '사용자 확정 [''ID03'']과 충돌 → INCOMPATIBLE·PRUNED'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '30',
    'AUDIT3',
    'support_basis_cap',
    'INFO',
    'G10b',
    'ENVIRONMENTAL_CONTEXT만 근거 → LOW 상한 적용'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '31',
    'AUDIT3',
    'support_basis_cap',
    'INFO',
    'G10c',
    'INSTITUTIONAL_COMPATIBILITY만 근거 → LOW 상한 적용'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '32',
    'AUDIT3',
    'audit_only_support',
    'INFO',
    'G12b',
    'confirmed 지지 없이 05 흔적만 있음 — LATENT 유지'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '33',
    'AUDIT3',
    'outcome_world_dependency',
    'INFO',
    'worlds',
    '공통 결말 node 23개는 모든 world에 공통인 OBSERVED다. 경쟁 설명 5개, 배제된 설명 1개'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '34',
    'AUDIT3',
    'unresolved_gap',
    'UNRESOLVED',
    'G10',
    'OPEN_UNRESOLVED — 어느 경쟁 설명 world도 이 gap을 메우지 않음 (후보 G10a=MEDIUM, G10b=LOW, G10c=LOW) · review_decision: 사용자 검토: latent bridge를 채택하지 않음. 이유를 억지로 채우지 않고 gap을 열어 둔다(world에서도 비움). · unresolved_reason: 파직과'
        || ' 3일 뒤 유임의 사유가 모두 기록되지 않았다. 관측 근거(CF049, CF050)에 사유를 적은 문장이 없음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '35',
    'AUDIT3',
    'world_integrity',
    'INFO',
    'worlds',
    'world 6개 (경쟁 설명 5, rejected 1) — 쌍별 gap 차이 ≥2 확인'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '36',
    'AUDIT4',
    'interaction_direction',
    'UNRESOLVED',
    'M1×M2',
    '함께 쓰이는 world(W2)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '37',
    'AUDIT4',
    'interaction_direction',
    'UNRESOLVED',
    'M1×M3',
    '함께 쓰이는 world(W1, W3)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '38',
    'AUDIT4',
    'interaction_direction',
    'UNRESOLVED',
    'M1×M4',
    '함께 쓰이는 world(W1, W2, W4)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '39',
    'AUDIT4',
    'interaction_direction',
    'UNRESOLVED',
    'M1×M6',
    '함께 쓰이는 world(W1, W3, W5)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '40',
    'AUDIT4',
    'coexistence_undetermined',
    'UNRESOLVED',
    'M2×M3',
    'COMPATIBLE — 충돌 근거는 없지만 어느 경쟁 world도 둘을 함께 쓰지 않아, 함께 작동했는지는 사료로 결정되지 않음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '41',
    'AUDIT4',
    'interaction_direction',
    'UNRESOLVED',
    'M2×M4',
    '함께 쓰이는 world(W2, W4)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '42',
    'AUDIT4',
    'interaction_direction',
    'UNRESOLVED',
    'M2×M6',
    '함께 쓰이는 world(W2)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '43',
    'AUDIT4',
    'coexistence_undetermined',
    'UNRESOLVED',
    'M3×M4',
    'COMPATIBLE — 충돌 근거는 없지만 어느 경쟁 world도 둘을 함께 쓰지 않아, 함께 작동했는지는 사료로 결정되지 않음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '44',
    'AUDIT4',
    'interaction_direction',
    'UNRESOLVED',
    'M3×M6',
    '함께 쓰이는 world(W1, W3)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '45',
    'AUDIT4',
    'interaction_direction',
    'UNRESOLVED',
    'M4×M6',
    '함께 쓰이는 world(W1, W2, W4)가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '46',
    'AUDIT4',
    'multiple_explanations',
    'UNRESOLVED',
    'V_COMMAND_SOURCE',
    'XOR: M1, M4가 같은 관측 전이(EP04)를 설명할 수 있음. 어느 쪽이 실제로 작동했는지는 사료로 결정되지 않음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '47',
    'AUDIT4',
    'multiple_explanations',
    'UNRESOLVED',
    'V_INFO_TO_COMMANDER',
    'OR: M1, M2, M3, M4가 같은 관측 전이(EP09)를 설명할 수 있음. 어느 쪽이 실제로 작동했는지는 사료로 결정되지 않음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '48',
    'AUDIT4',
    'multiple_explanations',
    'UNRESOLVED',
    'V_INVESTIGATION_SCOPE',
    'OR: M2, M4가 같은 관측 전이(EP11)를 설명할 수 있음. 어느 쪽이 실제로 작동했는지는 사료로 결정되지 않음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '49',
    'AUDIT4',
    'multiple_explanations',
    'UNRESOLVED',
    'V_INITIAL_JUDGMENT_BASIS',
    'OR: M2, M6가 같은 관측 전이(EP15)를 설명할 수 있음. 어느 쪽이 실제로 작동했는지는 사료로 결정되지 않음'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '50',
    'AUDIT4',
    'unresolved_item',
    'UNRESOLVED',
    'U_ID06',
    'ID06 병영의 염탐 담당자 = 유제희?'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '51',
    'AUDIT4',
    'unresolved_item',
    'UNRESOLVED',
    'U_ID07',
    'ID07 철편 네 개 = 철퇴 네 개?'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '52',
    'AUDIT4',
    'unresolved_item',
    'UNRESOLVED',
    'U_ID08',
    'ID08 3/4 장교 일행에 조계완 포함?'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '53',
    'AUDIT4',
    'unresolved_item',
    'UNRESOLVED',
    'U_OE007',
    'OE007 자미덕 ''지휘'' 주장 ↔ 한재욱 ''은밀한 사주'' 부인 (PARTIAL_CONFLICT)'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '54',
    'AUDIT4',
    'unresolved_item',
    'UNRESOLVED',
    'U_OE062',
    'OE062 5월 ''조사'' = 정조 ''평범한 신문''? (UNRESOLVED_SCOPE)'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '55',
    'AUDIT4',
    'unresolved_item',
    'UNRESOLVED',
    'U_G10',
    'G10 이형원 파직 → 유임 이유 (OPEN_UNRESOLVED)'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '56',
    'AUDIT4',
    'super_dag_summary',
    'INFO',
    'super_dag',
    'node CONTEXT 24, LATENT_MECHANISM 55, OBSERVED 37, UNRESOLVED 6 · edge CONTEXT 38, DERIVED 64, LATENT_MECHANISM 90, OBSERVED 4, UNRESOLVED 9'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '57',
    'AUDIT4',
    'frozen_graph_changed',
    'INFO',
    'observed_dag',
    '동결 해시 일치 ccb7ec63763a'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '58',
    'AUDIT5',
    'view_summary',
    'INFO',
    'views',
    'View 10개(subset 8) 모두 canonical node·edge 부분집합, 좌표 결정적·겹침 0. node 글자 16px·line-height 1.6·첫 화면 배율 ≥ 0.95'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '59',
    'AUDIT5',
    'ui_summary',
    'INFO',
    'docs/data',
    'node 122 · edge 205 · 후보 38 · world 선택 7 · view 10 · 개입 행 13 · 공존 쌍 21 (canonical과 같음)'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '60',
    'AUDIT5',
    'temporal_order',
    'INFO',
    'layout',
    '날짜 있는 관측 node 36개가 기준일 순서대로 왼쪽 → 오른쪽에 놓임. 날짜 미기록 node EP08는 시간 축 밖 ''날짜 미기록'' 구간에 두었다(위치가 날짜를 뜻하지 않음).'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '61',
    'AUDIT5',
    'responsibility_to_biological',
    'INFO',
    'view:death',
    'A branch 13개 · B branch 5개 node 사이 직접 edge 0개'
);
INSERT INTO STG_PY_AUDIT_FINDINGS (FINDING_SEQ, AUDIT_NAME, CHECK_NAME, SEVERITY, TARGET, MESSAGE)
VALUES (
    '62',
    'AUDIT5',
    'frozen_graph_changed',
    'INFO',
    'observed_dag',
    '동결 해시 일치 ccb7ec63763a'
);

-- sql/02_load/data/dag_freeze.csv (1행)
INSERT INTO STG_DAG_FREEZE (FREEZE_NAME, SHA256, STRUCTURE_SHA256, TOPOLOGY_SHA256, N_NODES, N_EDGES, N_EPISODE_NODES, N_ENV_NODES, LATENT_COUNT)
VALUES (
    'Validated Observed Partial DAG',
    'ccb7ec63763a715ae90c74dfff37d3ed7980fa705fd152f59de8bed2e31d4e0c',
    '0b69134457880767285c3516e1e9c962bb9b778a5c6f4e85b248c6b16b01c80d',
    '04c84b0e24af31f5605800ae30bc2750563a1aeb3e72390aa6d6643676b68e84',
    '41',
    '68',
    '37',
    '4',
    '0'
);

COMMIT;
-- 합계 1101행
