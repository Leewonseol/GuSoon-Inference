-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_confirmed_facts.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'gusun_clean_restart_csv_pack/01_confirmed_facts.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_CONFIRMED_FACTS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
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
