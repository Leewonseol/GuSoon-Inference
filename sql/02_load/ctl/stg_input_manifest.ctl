-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_input_manifest.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'gusun_clean_restart_csv_pack/00_INPUT_MANIFEST.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_INPUT_MANIFEST
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "FILE_NAME"                  CHAR(4000),
  "ROLE"                       CHAR(4000),
  "ALLOWED_AS_DAG_INPUT"       CHAR(4000),
  "PURPOSE"                    CHAR(4000),
  "IMPORTANT_RULE"             CHAR(4000)
)
