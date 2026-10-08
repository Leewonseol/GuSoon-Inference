-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_mech_interventions.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/mechanism_interventions.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_MECH_INTERVENTIONS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "MECHANISM"                  CHAR(4000),
  "VARIABLE"                   CHAR(4000),
  "TARGET"                     CHAR(4000),
  "RESULT"                     CHAR(4000),
  "REMOVED"                    CHAR(4000),
  "REMAINING"                  CHAR(4000),
  "AFFECTED_WORLDS"            CHAR(4000),
  "NOTE"                       CHAR(4000)
)
