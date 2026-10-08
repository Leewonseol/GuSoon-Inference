-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_sd_nodes.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/mechanism_super_dag_nodes.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_SD_NODES
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "NODE_ID"                    CHAR(4000),
  "SD_STATUS"                  CHAR(4000),
  "NODE_TYPE"                  CHAR(4000),
  "LABEL"                      CHAR(4000),
  "FROZEN_STATUS"              CHAR(4000),
  "BRANCH"                     CHAR(4000),
  "MECHANISM"                  CHAR(4000),
  "WORLDS"                     CHAR(4000),
  "DETAIL"                     CHAR(4000)
)
