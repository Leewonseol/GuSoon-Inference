-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_mechanism_definitions.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/mechanism_definitions.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_MECHANISM_DEFINITIONS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
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
