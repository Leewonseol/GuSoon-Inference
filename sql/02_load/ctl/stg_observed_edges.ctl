-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_observed_edges.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/observed_edges.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_OBSERVED_EDGES
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
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
