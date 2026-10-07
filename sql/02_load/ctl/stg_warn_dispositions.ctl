-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_warn_dispositions.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/warn_dispositions.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_WARN_DISPOSITIONS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
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
