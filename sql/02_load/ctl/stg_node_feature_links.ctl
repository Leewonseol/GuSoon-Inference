-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_node_feature_links.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/node_feature_links.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_NODE_FEATURE_LINKS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "LINK_ID"                    CHAR(4000),
  "TARGET_KIND"                CHAR(4000),
  "TARGET_ID"                  CHAR(4000),
  "FEATURE_LAYER"              CHAR(4000),
  "FEATURE_ID"                 CHAR(4000),
  "DIMENSION"                  CHAR(4000),
  "ASSESSMENT"                 CHAR(4000),
  "CREATES_EVENT"              CHAR(4000),
  "RATIONALE"                  CHAR(4000)
)
