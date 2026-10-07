-- =============================================================================
-- LOAD 방법 A — EXTERNAL TABLE(ORACLE_LOADER) → STG_* / 방법 B — SQL*Loader(ctl/)
-- 이 파일은 sql/02_load/generate_load_scripts.py가 canonical CSV header로 생성했다. 손으로 고치지 말 것.
-- Oracle runtime에서 실행 검증되지 않았다(Oracle runtime unavailable) — sql/README.md §실행 상태 참고.
-- =============================================================================

-- 준비(DBA 권한, 한 번만). 경로는 Oracle 서버(또는 컨테이너) 안에서 보이는 경로로 바꾼다.
--   예: docker run -v $PWD:/repo ... gvenzl/oracle-free  → '/repo/...'
-- CREATE OR REPLACE DIRECTORY GUSUN_PACK_DIR    AS '/repo/gusun_clean_restart_csv_pack';
-- CREATE OR REPLACE DIRECTORY GUSUN_OUT_DIR     AS '/repo/output/clean';
-- CREATE OR REPLACE DIRECTORY GUSUN_SQLDATA_DIR AS '/repo/sql/02_load/data';
-- GRANT READ, WRITE ON DIRECTORY GUSUN_PACK_DIR    TO gusun;
-- GRANT READ, WRITE ON DIRECTORY GUSUN_OUT_DIR     TO gusun;
-- GRANT READ, WRITE ON DIRECTORY GUSUN_SQLDATA_DIR TO gusun;
--
-- CSV 형식(실측): UTF-8, 줄 끝 CRLF(0x0D0A), 첫 줄 header, pack 6개 파일은 BOM 포함(header 줄이라 SKIP 1로 건너뜀),
--                 필드 안 줄바꿈 없음, 필드 안 큰따옴표 없음 → 'FIELDS CSV WITH EMBEDDED'(12.2+) 없이도 읽힌다.
-- REJECT LIMIT 0: 한 줄이라도 못 읽으면 SELECT가 실패한다(조용한 누락 방지).

-- gusun_clean_restart_csv_pack/00_INPUT_MANIFEST.csv
CREATE TABLE X_INPUT_MANIFEST (
    FILE_NAME                  VARCHAR2(4000 BYTE),
    ROLE                       VARCHAR2(4000 BYTE),
    ALLOWED_AS_DAG_INPUT       VARCHAR2(4000 BYTE),
    PURPOSE                    VARCHAR2(4000 BYTE),
    IMPORTANT_RULE             VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_PACK_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "FILE_NAME"                  CHAR(4000),
            "ROLE"                       CHAR(4000),
            "ALLOWED_AS_DAG_INPUT"       CHAR(4000),
            "PURPOSE"                    CHAR(4000),
            "IMPORTANT_RULE"             CHAR(4000)
        )
    )
    LOCATION ('00_INPUT_MANIFEST.csv')
)
REJECT LIMIT 0;

-- gusun_clean_restart_csv_pack/01_confirmed_facts.csv
CREATE TABLE X_CONFIRMED_FACTS (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_PACK_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "FACT_ID"                    CHAR(4000),
            "CHRONOLOGY"                 CHAR(4000),
            "RECORD_LUNAR_DATE"          CHAR(4000),
            "OCCURRENCE_LUNAR_TEXT"      CHAR(4000),
            "FACT_CATEGORY"              CHAR(4000),
            "CONFIRMATION_LEVEL"         CHAR(4000),
            "SUBJECT"                    CHAR(4000),
            "CONFIRMED_STATEMENT"        CHAR(4000),
            "UNDERLYING_CLAIM_STATUS"    CHAR(4000),
            "SOURCE_RECORD_ID"           CHAR(4000),
            "SOURCE_WORK"                CHAR(4000),
            "SOURCE_URL"                 CHAR(4000),
            "SOURCE_PROP_IDS"            CHAR(4000),
            "NOTES"                      CHAR(4000)
        )
    )
    LOCATION ('01_confirmed_facts.csv')
)
REJECT LIMIT 0;

-- gusun_clean_restart_csv_pack/02_institutional_normative_features.csv
CREATE TABLE X_INSTITUTIONAL_FEATURES (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_PACK_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "FEATURE_ID"                 CHAR(4000),
            "LAYER"                      CHAR(4000),
            "FEATURE_GROUP"              CHAR(4000),
            "FEATURE_NAME"               CHAR(4000),
            "OPERATIONAL_DEFINITION"     CHAR(4000),
            "ENCODING_TYPE"              CHAR(4000),
            "SUGGESTED_VALUES"           CHAR(4000),
            "MODEL_ROLE"                 CHAR(4000),
            "INTERPRETATION"             CHAR(4000),
            "VALID_FROM"                 CHAR(4000),
            "VALID_TO"                   CHAR(4000),
            "GEO_SCOPE"                  CHAR(4000),
            "SOURCE_NAME"                CHAR(4000),
            "SOURCE_URL"                 CHAR(4000),
            "NOTES"                      CHAR(4000)
        )
    )
    LOCATION ('02_institutional_normative_features.csv')
)
REJECT LIMIT 0;

-- gusun_clean_restart_csv_pack/03_environment_1793.csv
CREATE TABLE X_ENVIRONMENT_1793 (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_PACK_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "ENV_ID"                     CHAR(4000),
            "LUNAR_DATE"                 CHAR(4000),
            "REGION_SCOPE"               CHAR(4000),
            "CONTEXT_TYPE"               CHAR(4000),
            "ATTESTED_CONTEXT"           CHAR(4000),
            "FEATURE_NAME"               CHAR(4000),
            "VALUE"                      CHAR(4000),
            "MODEL_ROLE"                 CHAR(4000),
            "SOURCE_URL"                 CHAR(4000),
            "NOTES"                      CHAR(4000)
        )
    )
    LOCATION ('03_environment_1793.csv')
)
REJECT LIMIT 0;

-- gusun_clean_restart_csv_pack/04_source_records.csv
CREATE TABLE X_SOURCE_RECORDS (
    SOURCE_RECORD_ID           VARCHAR2(4000 BYTE),
    SOURCE_WORK                VARCHAR2(4000 BYTE),
    RECORD_LUNAR_DATE          VARCHAR2(4000 BYTE),
    SOURCE_TITLE               VARCHAR2(4000 BYTE),
    SOURCE_URL                 VARCHAR2(4000 BYTE),
    SOURCE_DOMAIN              VARCHAR2(4000 BYTE),
    SOURCE_TIER                VARCHAR2(4000 BYTE),
    CASE_ROLE                  VARCHAR2(4000 BYTE),
    NOTES                      VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_PACK_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "SOURCE_RECORD_ID"           CHAR(4000),
            "SOURCE_WORK"                CHAR(4000),
            "RECORD_LUNAR_DATE"          CHAR(4000),
            "SOURCE_TITLE"               CHAR(4000),
            "SOURCE_URL"                 CHAR(4000),
            "SOURCE_DOMAIN"              CHAR(4000),
            "SOURCE_TIER"                CHAR(4000),
            "CASE_ROLE"                  CHAR(4000),
            "NOTES"                      CHAR(4000)
        )
    )
    LOCATION ('04_source_records.csv')
)
REJECT LIMIT 0;

-- gusun_clean_restart_csv_pack/05_source_faithful_propositions_AUDIT_ONLY.csv
CREATE TABLE X_AUDIT_PROPOSITIONS (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_PACK_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "PROP_ID"                    CHAR(4000),
            "SOURCE_RECORD_ID"           CHAR(4000),
            "SOURCE_WORK"                CHAR(4000),
            "RECORD_LUNAR_DATE"          CHAR(4000),
            "REPORTING_ACTOR"            CHAR(4000),
            "ATTESTATION_MODE"           CHAR(4000),
            "PROPOSITION_TYPE"           CHAR(4000),
            "SUBJECT"                    CHAR(4000),
            "PREDICATE"                  CHAR(4000),
            "OBJECT_OR_CONTENT"          CHAR(4000),
            "OCCURRENCE_LUNAR_TEXT"      CHAR(4000),
            "OCCURRENCE_PRECISION"       CHAR(4000),
            "HISTORICAL_PLACE"           CHAR(4000),
            "PLACE_STATUS"               CHAR(4000),
            "NAMED_ENTITIES"             CHAR(4000),
            "EPISTEMIC_SCOPE"            CHAR(4000),
            "CLAIM_TOPIC"                CHAR(4000),
            "CONFLICT_GROUP"             CHAR(4000),
            "SET_STATUS"                 CHAR(4000),
            "DIRECTNESS"                 CHAR(4000),
            "SOURCE_URL"                 CHAR(4000),
            "NOTES"                      CHAR(4000)
        )
    )
    LOCATION ('05_source_faithful_propositions_AUDIT_ONLY.csv')
)
REJECT LIMIT 0;

-- output/clean/episode_nodes.csv
CREATE TABLE X_EPISODE_NODES (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "NODE_ID"                    CHAR(4000),
            "NODE_STATUS"                CHAR(4000),
            "LAYER"                      CHAR(4000),
            "BRANCH"                     CHAR(4000),
            "TITLE"                      CHAR(4000),
            "SUMMARY"                    CHAR(4000),
            "CAUTION"                    CHAR(4000),
            "MEMBER_FACT_IDS"            CHAR(4000),
            "MEMBER_CLAUSES"             CHAR(4000),
            "CONFIRMATION_LEVELS"        CHAR(4000),
            "EPISTEMIC_FLOOR"            CHAR(4000),
            "CLAIM_STATUS"               CHAR(4000),
            "SOURCE_RECORD_IDS"          CHAR(4000),
            "SOURCE_PROP_IDS"            CHAR(4000),
            "ATTESTING_ACTOR"            CHAR(4000),
            "OCCURRENCE_TEXT"            CHAR(4000),
            "T_MIN"                      CHAR(4000),
            "T_MAX"                      CHAR(4000),
            "RECORD_LUNAR_DATE"          CHAR(4000),
            "GROUPING_RATIONALE"         CHAR(4000),
            "IDENTITY_LINKS"             CHAR(4000),
            "ENV_ID"                     CHAR(4000)
        )
    )
    LOCATION ('episode_nodes.csv')
)
REJECT LIMIT 0;

-- output/clean/observed_edges.csv
CREATE TABLE X_OBSERVED_EDGES (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "EDGE_ID"                    CHAR(4000),
            "SRC"                        CHAR(4000),
            "DST"                        CHAR(4000),
            "EDGE_TYPE"                  CHAR(4000),
            "BASIS"                      CHAR(4000),
            "STATUS"                     CHAR(4000),
            "CLAIM_LEVEL"                CHAR(4000),
            "CONDITION"                  CHAR(4000),
            "SUPPORTING"                 CHAR(4000),
            "RATIONALE"                  CHAR(4000),
            "CAUTION"                    CHAR(4000),
            "UNCERTAINTY_STATUS"         CHAR(4000),
            "REVIEW_DECISION"            CHAR(4000)
        )
    )
    LOCATION ('observed_edges.csv')
)
REJECT LIMIT 0;

-- output/clean/node_feature_links.csv
CREATE TABLE X_NODE_FEATURE_LINKS (
    LINK_ID                    VARCHAR2(4000 BYTE),
    TARGET_KIND                VARCHAR2(4000 BYTE),
    TARGET_ID                  VARCHAR2(4000 BYTE),
    FEATURE_LAYER              VARCHAR2(4000 BYTE),
    FEATURE_ID                 VARCHAR2(4000 BYTE),
    DIMENSION                  VARCHAR2(4000 BYTE),
    ASSESSMENT                 VARCHAR2(4000 BYTE),
    CREATES_EVENT              VARCHAR2(4000 BYTE),
    RATIONALE                  VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "LINK_ID"                    CHAR(4000),
            "TARGET_KIND"                CHAR(4000),
            "TARGET_ID"                  CHAR(4000),
            "FEATURE_LAYER"              CHAR(4000),
            "FEATURE_ID"                 CHAR(4000),
            "DIMENSION"                  CHAR(4000),
            "ASSESSMENT"                 CHAR(4000),
            "CREATES_EVENT"              CHAR(4000),
            "RATIONALE"                  CHAR(4000)
        )
    )
    LOCATION ('node_feature_links.csv')
)
REJECT LIMIT 0;

-- output/clean/identity_register.csv
CREATE TABLE X_IDENTITY_REGISTER (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "IDENTITY_ID"                CHAR(4000),
            "SURFACE_A"                  CHAR(4000),
            "SURFACE_B"                  CHAR(4000),
            "STATUS"                     CHAR(4000),
            "RESOLVED_BY"                CHAR(4000),
            "RESOLUTION_BASIS"           CHAR(4000),
            "UNRESOLVED_REASON"          CHAR(4000),
            "MODEL_RELEVANCE"            CHAR(4000),
            "MANUAL_DECISION_REQUIRED"   CHAR(4000),
            "REVIEW_DECISION"            CHAR(4000),
            "CONTEXT"                    CHAR(4000),
            "REFERENCED_FACTS"           CHAR(4000)
        )
    )
    LOCATION ('identity_register.csv')
)
REJECT LIMIT 0;

-- output/clean/gaps.csv
CREATE TABLE X_GAPS (
    GAP_ID                     VARCHAR2(4000 BYTE),
    TITLE                      VARCHAR2(4000 BYTE),
    GAP_TYPE                   VARCHAR2(4000 BYTE),
    BETWEEN_NODES              VARCHAR2(4000 BYTE),
    OBSERVED_ANCHOR_FACTS      VARCHAR2(4000 BYTE),
    WHY_GAP                    VARCHAR2(4000 BYTE),
    GAP_STATUS                 VARCHAR2(4000 BYTE),
    REVIEW_DECISION            VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "GAP_ID"                     CHAR(4000),
            "TITLE"                      CHAR(4000),
            "GAP_TYPE"                   CHAR(4000),
            "BETWEEN_NODES"              CHAR(4000),
            "OBSERVED_ANCHOR_FACTS"      CHAR(4000),
            "WHY_GAP"                    CHAR(4000),
            "GAP_STATUS"                 CHAR(4000),
            "REVIEW_DECISION"            CHAR(4000)
        )
    )
    LOCATION ('gaps.csv')
)
REJECT LIMIT 0;

-- output/clean/latent_candidates.csv
CREATE TABLE X_LATENT_CANDIDATES (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "CANDIDATE_ID"               CHAR(4000),
            "GAP_ID"                     CHAR(4000),
            "STATUS"                     CHAR(4000),
            "FORM"                       CHAR(4000),
            "LABEL"                      CHAR(4000),
            "DESCRIPTION"                CHAR(4000),
            "SOURCE_CONSISTENCY"         CHAR(4000),
            "TEMPORAL_FIT"               CHAR(4000),
            "INSTITUTIONAL_FIT"          CHAR(4000),
            "ROLE_FIT"                   CHAR(4000),
            "INFORMATION_FLOW_FIT"       CHAR(4000),
            "ENVIRONMENTAL_FIT"          CHAR(4000),
            "CONTRADICTION_RISK"         CHAR(4000),
            "N_ASSUMPTIONS"              CHAR(4000),
            "EXTRA_ASSUMPTIONS"          CHAR(4000),
            "IDENTITY_CONDITIONS"        CHAR(4000),
            "OVERALL"                    CHAR(4000),
            "PRUNE_DECISION"             CHAR(4000),
            "SUPPORTS"                   CHAR(4000),
            "CONFLICTS"                  CHAR(4000),
            "AUDIT_ATTESTATION"          CHAR(4000),
            "SUPPORT_BASIS"              CHAR(4000),
            "NOTES"                      CHAR(4000),
            "OBSERVED_LEFT"              CHAR(4000),
            "OBSERVED_RIGHT"             CHAR(4000),
            "LATENT_BRIDGE_CLAIM"        CHAR(4000),
            "BRIDGE_DIRECTLY_ATTESTED"   CHAR(4000),
            "ENDPOINT_SUPPORT"           CHAR(4000),
            "SOURCE_SUPPORT"             CHAR(4000),
            "BRIDGE_EVIDENCE"            CHAR(4000),
            "BRIDGE_BASIS"               CHAR(4000),
            "EVIDENCE_GRADE"             CHAR(4000),
            "PLAUSIBILITY_GRADE"         CHAR(4000),
            "SOURCE_CONSISTENCY_V1"      CHAR(4000),
            "OVERALL_V1"                 CHAR(4000),
            "REAUDIT_REASON"             CHAR(4000)
        )
    )
    LOCATION ('latent_candidates.csv')
)
REJECT LIMIT 0;

-- output/clean/latent_elements.csv
CREATE TABLE X_LATENT_ELEMENTS (
    ELEMENT_ID                 VARCHAR2(4000 BYTE),
    CANDIDATE_ID               VARCHAR2(4000 BYTE),
    KIND                       VARCHAR2(4000 BYTE),
    STATUS                     VARCHAR2(4000 BYTE),
    SRC                        VARCHAR2(4000 BYTE),
    DST                        VARCHAR2(4000 BYTE),
    EDGE_TYPE                  VARCHAR2(4000 BYTE),
    TEXT                       VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "ELEMENT_ID"                 CHAR(4000),
            "CANDIDATE_ID"               CHAR(4000),
            "KIND"                       CHAR(4000),
            "STATUS"                     CHAR(4000),
            "SRC"                        CHAR(4000),
            "DST"                        CHAR(4000),
            "EDGE_TYPE"                  CHAR(4000),
            "TEXT"                       CHAR(4000)
        )
    )
    LOCATION ('latent_elements.csv')
)
REJECT LIMIT 0;

-- output/clean/narrative_worlds.csv
CREATE TABLE X_NARRATIVE_WORLDS (
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
    NARRATIVE                  VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "WORLD_ID"                   CHAR(4000),
            "NAME"                       CHAR(4000),
            "STATUS"                     CHAR(4000),
            "LATENT_BRIDGES"             CHAR(4000),
            "UNRESOLVED_GAPS"            CHAR(4000),
            "INSTITUTIONAL_FIT"          CHAR(4000),
            "ENVIRONMENTAL_FIT"          CHAR(4000),
            "N_ASSUMPTIONS"              CHAR(4000),
            "MIN_GRADE"                  CHAR(4000),
            "MAIN_ASSUMPTIONS"           CHAR(4000),
            "MAIN_WEAKNESSES"            CHAR(4000),
            "CONTRADICTED_EVIDENCE"      CHAR(4000),
            "STORY_IMPLICATION"          CHAR(4000),
            "IDENTITY_CONDITIONS"        CHAR(4000),
            "RESOLVED_IDENTITIES"        CHAR(4000),
            "EVIDENCE_PROFILE"           CHAR(4000),
            "WORK_ROLE"                  CHAR(4000),
            "STORY_QUESTION"             CHAR(4000),
            "DIFFERENCE"                 CHAR(4000),
            "UNIQUE_BRIDGES"             CHAR(4000),
            "NARRATIVE"                  CHAR(4000)
        )
    )
    LOCATION ('narrative_worlds.csv')
)
REJECT LIMIT 0;

-- output/clean/warn_dispositions.csv
CREATE TABLE X_WARN_DISPOSITIONS (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "WARNING_ID"                 CHAR(4000),
            "AUDIT_STAGE"                CHAR(4000),
            "AFFECTED_ITEM"              CHAR(4000),
            "WARNING_TYPE"               CHAR(4000),
            "ORIGINAL_TEXT"              CHAR(4000),
            "GENERATED_TEXT"             CHAR(4000),
            "RISK"                       CHAR(4000),
            "DISPOSITION"                CHAR(4000),
            "JUSTIFICATION"              CHAR(4000),
            "FIXED_TEXT"                 CHAR(4000),
            "FINAL_STATUS"               CHAR(4000),
            "FINAL_CLASSIFICATION"       CHAR(4000),
            "UNRESOLVED_REASON"          CHAR(4000)
        )
    )
    LOCATION ('warn_dispositions.csv')
)
REJECT LIMIT 0;

-- output/clean/mechanism_super_dag_nodes.csv
CREATE TABLE X_SD_NODES (
    NODE_ID                    VARCHAR2(4000 BYTE),
    SD_STATUS                  VARCHAR2(4000 BYTE),
    NODE_TYPE                  VARCHAR2(4000 BYTE),
    LABEL                      VARCHAR2(4000 BYTE),
    FROZEN_STATUS              VARCHAR2(4000 BYTE),
    BRANCH                     VARCHAR2(4000 BYTE),
    MECHANISM                  VARCHAR2(4000 BYTE),
    WORLDS                     VARCHAR2(4000 BYTE),
    DETAIL                     VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "NODE_ID"                    CHAR(4000),
            "SD_STATUS"                  CHAR(4000),
            "NODE_TYPE"                  CHAR(4000),
            "LABEL"                      CHAR(4000),
            "FROZEN_STATUS"              CHAR(4000),
            "BRANCH"                     CHAR(4000),
            "MECHANISM"                  CHAR(4000),
            "WORLDS"                     CHAR(4000),
            "DETAIL"                     CHAR(4000)
        )
    )
    LOCATION ('mechanism_super_dag_nodes.csv')
)
REJECT LIMIT 0;

-- output/clean/mechanism_super_dag_edges.csv
CREATE TABLE X_SD_EDGES (
    EDGE_ID                    VARCHAR2(4000 BYTE),
    SRC                        VARCHAR2(4000 BYTE),
    DST                        VARCHAR2(4000 BYTE),
    EDGE_TYPE                  VARCHAR2(4000 BYTE),
    SD_STATUS                  VARCHAR2(4000 BYTE),
    ORIGIN                     VARCHAR2(4000 BYTE),
    NOTE                       VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "EDGE_ID"                    CHAR(4000),
            "SRC"                        CHAR(4000),
            "DST"                        CHAR(4000),
            "EDGE_TYPE"                  CHAR(4000),
            "SD_STATUS"                  CHAR(4000),
            "ORIGIN"                     CHAR(4000),
            "NOTE"                       CHAR(4000)
        )
    )
    LOCATION ('mechanism_super_dag_edges.csv')
)
REJECT LIMIT 0;

-- output/clean/mechanism_definitions.csv
CREATE TABLE X_MECHANISM_DEFINITIONS (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "MECHANISM_ID"               CHAR(4000),
            "MECHANISM_NAME"             CHAR(4000),
            "EASY_DESCRIPTION"           CHAR(4000),
            "RELATED_CANDIDATES"         CHAR(4000),
            "RELATED_OBSERVED_NODES"     CHAR(4000),
            "REQUIRED_INST_FEATURES"     CHAR(4000),
            "RELATED_ENV_FEATURES"       CHAR(4000),
            "EVIDENCE_STATUS"            CHAR(4000),
            "REMARKS"                    CHAR(4000),
            "N_CANDIDATES"               CHAR(4000),
            "BRANCH"                     CHAR(4000)
        )
    )
    LOCATION ('mechanism_definitions.csv')
)
REJECT LIMIT 0;

-- output/clean/world_mechanism_configurations.csv
CREATE TABLE X_WORLD_MECH_CONFIGS (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "WORLD_ID"                   CHAR(4000),
            "ROLE_TYPE"                  CHAR(4000),
            "M1"                         CHAR(4000),
            "M2"                         CHAR(4000),
            "M3"                         CHAR(4000),
            "M4"                         CHAR(4000),
            "M5"                         CHAR(4000),
            "M6"                         CHAR(4000),
            "MB"                         CHAR(4000),
            "M1_BASIS"                   CHAR(4000),
            "M2_BASIS"                   CHAR(4000),
            "M3_BASIS"                   CHAR(4000),
            "M4_BASIS"                   CHAR(4000),
            "M5_BASIS"                   CHAR(4000),
            "M6_BASIS"                   CHAR(4000),
            "MB_BASIS"                   CHAR(4000),
            "LATENT_BRIDGES"             CHAR(4000)
        )
    )
    LOCATION ('world_mechanism_configurations.csv')
)
REJECT LIMIT 0;

-- output/clean/mechanism_interaction_matrix.csv
CREATE TABLE X_MECH_INTERACTIONS (
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
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "MECHANISM_A_ID"             CHAR(4000),
            "MECHANISM_B_ID"             CHAR(4000),
            "COEXISTENCE"                CHAR(4000),
            "REASON"                     CHAR(4000),
            "CONFLICTING_ITEMS"          CHAR(4000),
            "EXPLAINED_TOGETHER"         CHAR(4000),
            "RELATION"                   CHAR(4000),
            "COOCCUR_WORLDS"             CHAR(4000),
            "MECHANISM_A_NAME"           CHAR(4000),
            "MECHANISM_B_NAME"           CHAR(4000)
        )
    )
    LOCATION ('mechanism_interaction_matrix.csv')
)
REJECT LIMIT 0;

-- output/clean/mechanism_interventions.csv
CREATE TABLE X_MECH_INTERVENTIONS (
    MECHANISM                  VARCHAR2(4000 BYTE),
    VARIABLE                   VARCHAR2(4000 BYTE),
    TARGET                     VARCHAR2(4000 BYTE),
    RESULT                     VARCHAR2(4000 BYTE),
    REMOVED                    VARCHAR2(4000 BYTE),
    REMAINING                  VARCHAR2(4000 BYTE),
    AFFECTED_WORLDS            VARCHAR2(4000 BYTE),
    NOTE                       VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "MECHANISM"                  CHAR(4000),
            "VARIABLE"                   CHAR(4000),
            "TARGET"                     CHAR(4000),
            "RESULT"                     CHAR(4000),
            "REMOVED"                    CHAR(4000),
            "REMAINING"                  CHAR(4000),
            "AFFECTED_WORLDS"            CHAR(4000),
            "NOTE"                       CHAR(4000)
        )
    )
    LOCATION ('mechanism_interventions.csv')
)
REJECT LIMIT 0;

-- output/clean/qualitative_structural_rules.csv
CREATE TABLE X_STRUCTURAL_RULES (
    VAR_ID                     VARCHAR2(4000 BYTE),
    GAP                        VARCHAR2(4000 BYTE),
    TARGET                     VARCHAR2(4000 BYTE),
    OP                         VARCHAR2(4000 BYTE),
    INPUTS                     VARCHAR2(4000 BYTE),
    RULE                       VARCHAR2(4000 BYTE),
    RULE_DESC                  VARCHAR2(4000 BYTE),
    CONSTRAINT_TEXT            VARCHAR2(4000 BYTE),
    INPUT_CANDIDATES           VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_OUT_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "VAR_ID"                     CHAR(4000),
            "GAP"                        CHAR(4000),
            "TARGET"                     CHAR(4000),
            "OP"                         CHAR(4000),
            "INPUTS"                     CHAR(4000),
            "RULE"                       CHAR(4000),
            "RULE_DESC"                  CHAR(4000),
            "CONSTRAINT_TEXT"            CHAR(4000),
            "INPUT_CANDIDATES"           CHAR(4000)
        )
    )
    LOCATION ('qualitative_structural_rules.csv')
)
REJECT LIMIT 0;

-- sql/02_load/data/episode_members.csv
CREATE TABLE X_EPISODE_MEMBERS (
    EPISODE_ID                 VARCHAR2(4000 BYTE),
    MEMBER_SEQ                 VARCHAR2(4000 BYTE),
    FACT_ID                    VARCHAR2(4000 BYTE),
    CLAUSE                     VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_SQLDATA_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "EPISODE_ID"                 CHAR(4000),
            "MEMBER_SEQ"                 CHAR(4000),
            "FACT_ID"                    CHAR(4000),
            "CLAUSE"                     CHAR(4000)
        )
    )
    LOCATION ('episode_members.csv')
)
REJECT LIMIT 0;

-- sql/02_load/data/py_audit_findings.csv
CREATE TABLE X_PY_AUDIT_FINDINGS (
    FINDING_SEQ                VARCHAR2(4000 BYTE),
    AUDIT_NAME                 VARCHAR2(4000 BYTE),
    CHECK_NAME                 VARCHAR2(4000 BYTE),
    SEVERITY                   VARCHAR2(4000 BYTE),
    TARGET                     VARCHAR2(4000 BYTE),
    MESSAGE                    VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_SQLDATA_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "FINDING_SEQ"                CHAR(4000),
            "AUDIT_NAME"                 CHAR(4000),
            "CHECK_NAME"                 CHAR(4000),
            "SEVERITY"                   CHAR(4000),
            "TARGET"                     CHAR(4000),
            "MESSAGE"                    CHAR(4000)
        )
    )
    LOCATION ('py_audit_findings.csv')
)
REJECT LIMIT 0;

-- sql/02_load/data/dag_freeze.csv
CREATE TABLE X_DAG_FREEZE (
    FREEZE_NAME                VARCHAR2(4000 BYTE),
    SHA256                     VARCHAR2(4000 BYTE),
    STRUCTURE_SHA256           VARCHAR2(4000 BYTE),
    TOPOLOGY_SHA256            VARCHAR2(4000 BYTE),
    N_NODES                    VARCHAR2(4000 BYTE),
    N_EDGES                    VARCHAR2(4000 BYTE),
    N_EPISODE_NODES            VARCHAR2(4000 BYTE),
    N_ENV_NODES                VARCHAR2(4000 BYTE),
    LATENT_COUNT               VARCHAR2(4000 BYTE)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY GUSUN_SQLDATA_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
            "FREEZE_NAME"                CHAR(4000),
            "SHA256"                     CHAR(4000),
            "STRUCTURE_SHA256"           CHAR(4000),
            "TOPOLOGY_SHA256"            CHAR(4000),
            "N_NODES"                    CHAR(4000),
            "N_EDGES"                    CHAR(4000),
            "N_EPISODE_NODES"            CHAR(4000),
            "N_ENV_NODES"                CHAR(4000),
            "LATENT_COUNT"               CHAR(4000)
        )
    )
    LOCATION ('dag_freeze.csv')
)
REJECT LIMIT 0;

-- external table → staging (컬럼 순서가 같으므로 SELECT * 가능)
INSERT INTO STG_INPUT_MANIFEST SELECT * FROM X_INPUT_MANIFEST;
INSERT INTO STG_CONFIRMED_FACTS SELECT * FROM X_CONFIRMED_FACTS;
INSERT INTO STG_INSTITUTIONAL_FEATURES SELECT * FROM X_INSTITUTIONAL_FEATURES;
INSERT INTO STG_ENVIRONMENT_1793 SELECT * FROM X_ENVIRONMENT_1793;
INSERT INTO STG_SOURCE_RECORDS SELECT * FROM X_SOURCE_RECORDS;
INSERT INTO STG_AUDIT_PROPOSITIONS SELECT * FROM X_AUDIT_PROPOSITIONS;
INSERT INTO STG_EPISODE_NODES SELECT * FROM X_EPISODE_NODES;
INSERT INTO STG_OBSERVED_EDGES SELECT * FROM X_OBSERVED_EDGES;
INSERT INTO STG_NODE_FEATURE_LINKS SELECT * FROM X_NODE_FEATURE_LINKS;
INSERT INTO STG_IDENTITY_REGISTER SELECT * FROM X_IDENTITY_REGISTER;
INSERT INTO STG_GAPS SELECT * FROM X_GAPS;
INSERT INTO STG_LATENT_CANDIDATES SELECT * FROM X_LATENT_CANDIDATES;
INSERT INTO STG_LATENT_ELEMENTS SELECT * FROM X_LATENT_ELEMENTS;
INSERT INTO STG_NARRATIVE_WORLDS SELECT * FROM X_NARRATIVE_WORLDS;
INSERT INTO STG_WARN_DISPOSITIONS SELECT * FROM X_WARN_DISPOSITIONS;
INSERT INTO STG_SD_NODES SELECT * FROM X_SD_NODES;
INSERT INTO STG_SD_EDGES SELECT * FROM X_SD_EDGES;
INSERT INTO STG_MECHANISM_DEFINITIONS SELECT * FROM X_MECHANISM_DEFINITIONS;
INSERT INTO STG_WORLD_MECH_CONFIGS SELECT * FROM X_WORLD_MECH_CONFIGS;
INSERT INTO STG_MECH_INTERACTIONS SELECT * FROM X_MECH_INTERACTIONS;
INSERT INTO STG_MECH_INTERVENTIONS SELECT * FROM X_MECH_INTERVENTIONS;
INSERT INTO STG_STRUCTURAL_RULES SELECT * FROM X_STRUCTURAL_RULES;
INSERT INTO STG_EPISODE_MEMBERS SELECT * FROM X_EPISODE_MEMBERS;
INSERT INTO STG_PY_AUDIT_FINDINGS SELECT * FROM X_PY_AUDIT_FINDINGS;
INSERT INTO STG_DAG_FREEZE SELECT * FROM X_DAG_FREEZE;
COMMIT;

-- 방법 B: SQL*Loader (서버 DIRECTORY 권한이 없을 때). 저장소 루트에서 실행한다.
--   sqlldr userid=gusun/비밀번호@//localhost:1521/FREEPDB1 control=sql/02_load/ctl/stg_confirmed_facts.ctl
--   (ctl 파일 25개. 각 파일은 같은 STG_* 테이블에 APPEND한다.)
-- 방법 C: 순수 INSERT script — @sql/02_load/generated/stg_inserts.sql (파일 접근·sqlldr 없이 SQL*Plus/SQLcl만으로)
