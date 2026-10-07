-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_source_records.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'gusun_clean_restart_csv_pack/04_source_records.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_SOURCE_RECORDS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
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
