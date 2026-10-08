-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_environment_1793.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'gusun_clean_restart_csv_pack/03_environment_1793.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_ENVIRONMENT_1793
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
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
