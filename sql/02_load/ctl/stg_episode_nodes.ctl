-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_episode_nodes.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/episode_nodes.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_EPISODE_NODES
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
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
