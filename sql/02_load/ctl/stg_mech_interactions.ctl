-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_mech_interactions.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/mechanism_interaction_matrix.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_MECH_INTERACTIONS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "MECHANISM_A_ID"             CHAR(4000),
  "MECHANISM_B_ID"             CHAR(4000),
  "COEXISTENCE"                CHAR(4000),
  "REASON"                     CHAR(4000),
  "CONFLICTING_ITEMS"          CHAR(4000),
  "EXPLAINED_TOGETHER"         CHAR(4000),
  "RELATION"                   CHAR(4000),
  "COOCCUR_WORLDS"             CHAR(4000),
  "MECHANISM_A_NAME"           CHAR(4000),
  "MECHANISM_B_NAME"           CHAR(4000)
)
