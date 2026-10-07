-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_gaps.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/gaps.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_GAPS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
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
