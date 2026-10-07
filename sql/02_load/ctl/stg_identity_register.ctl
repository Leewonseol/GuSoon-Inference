-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_identity_register.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/identity_register.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_IDENTITY_REGISTER
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
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
