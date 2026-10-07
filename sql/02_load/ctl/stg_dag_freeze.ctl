-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_dag_freeze.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'sql/02_load/data/dag_freeze.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_DAG_FREEZE
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "FREEZE_NAME"                CHAR(4000),
  "SHA256"                     CHAR(4000),
  "STRUCTURE_SHA256"           CHAR(4000),
  "TOPOLOGY_SHA256"            CHAR(4000),
  "N_NODES"                    CHAR(4000),
  "N_EDGES"                    CHAR(4000),
  "N_EPISODE_NODES"            CHAR(4000),
  "N_ENV_NODES"                CHAR(4000),
  "LATENT_COUNT"               CHAR(4000)
)
