-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_latent_elements.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/latent_elements.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_LATENT_ELEMENTS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "ELEMENT_ID"                 CHAR(4000),
  "CANDIDATE_ID"               CHAR(4000),
  "KIND"                       CHAR(4000),
  "STATUS"                     CHAR(4000),
  "SRC"                        CHAR(4000),
  "DST"                        CHAR(4000),
  "EDGE_TYPE"                  CHAR(4000),
  "TEXT"                       CHAR(4000)
)
