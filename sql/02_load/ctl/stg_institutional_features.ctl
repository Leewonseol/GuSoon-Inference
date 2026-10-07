-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_institutional_features.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'gusun_clean_restart_csv_pack/02_institutional_normative_features.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_INSTITUTIONAL_FEATURES
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "FEATURE_ID"                 CHAR(4000),
  "LAYER"                      CHAR(4000),
  "FEATURE_GROUP"              CHAR(4000),
  "FEATURE_NAME"               CHAR(4000),
  "OPERATIONAL_DEFINITION"     CHAR(4000),
  "ENCODING_TYPE"              CHAR(4000),
  "SUGGESTED_VALUES"           CHAR(4000),
  "MODEL_ROLE"                 CHAR(4000),
  "INTERPRETATION"             CHAR(4000),
  "VALID_FROM"                 CHAR(4000),
  "VALID_TO"                   CHAR(4000),
  "GEO_SCOPE"                  CHAR(4000),
  "SOURCE_NAME"                CHAR(4000),
  "SOURCE_URL"                 CHAR(4000),
  "NOTES"                      CHAR(4000)
)
