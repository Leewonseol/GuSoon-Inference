-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_structural_rules.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/qualitative_structural_rules.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_STRUCTURAL_RULES
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "VAR_ID"                     CHAR(4000),
  "GAP"                        CHAR(4000),
  "TARGET"                     CHAR(4000),
  "OP"                         CHAR(4000),
  "INPUTS"                     CHAR(4000),
  "RULE"                       CHAR(4000),
  "RULE_DESC"                  CHAR(4000),
  "CONSTRAINT_TEXT"            CHAR(4000),
  "INPUT_CANDIDATES"           CHAR(4000)
)
