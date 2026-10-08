-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_world_mech_configs.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/world_mechanism_configurations.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_WORLD_MECH_CONFIGS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "WORLD_ID"                   CHAR(4000),
  "ROLE_TYPE"                  CHAR(4000),
  "M1"                         CHAR(4000),
  "M2"                         CHAR(4000),
  "M3"                         CHAR(4000),
  "M4"                         CHAR(4000),
  "M5"                         CHAR(4000),
  "M6"                         CHAR(4000),
  "MB"                         CHAR(4000),
  "M1_BASIS"                   CHAR(4000),
  "M2_BASIS"                   CHAR(4000),
  "M3_BASIS"                   CHAR(4000),
  "M4_BASIS"                   CHAR(4000),
  "M5_BASIS"                   CHAR(4000),
  "M6_BASIS"                   CHAR(4000),
  "MB_BASIS"                   CHAR(4000),
  "LATENT_BRIDGES"             CHAR(4000)
)
