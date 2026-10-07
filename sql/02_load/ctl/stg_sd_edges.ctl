-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_sd_edges.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/mechanism_super_dag_edges.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_SD_EDGES
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "EDGE_ID"                    CHAR(4000),
  "SRC"                        CHAR(4000),
  "DST"                        CHAR(4000),
  "EDGE_TYPE"                  CHAR(4000),
  "SD_STATUS"                  CHAR(4000),
  "ORIGIN"                     CHAR(4000),
  "NOTE"                       CHAR(4000)
)
