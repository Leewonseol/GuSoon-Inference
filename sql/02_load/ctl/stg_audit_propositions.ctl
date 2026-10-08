-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_audit_propositions.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'gusun_clean_restart_csv_pack/05_source_faithful_propositions_AUDIT_ONLY.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_AUDIT_PROPOSITIONS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "PROP_ID"                    CHAR(4000),
  "SOURCE_RECORD_ID"           CHAR(4000),
  "SOURCE_WORK"                CHAR(4000),
  "RECORD_LUNAR_DATE"          CHAR(4000),
  "REPORTING_ACTOR"            CHAR(4000),
  "ATTESTATION_MODE"           CHAR(4000),
  "PROPOSITION_TYPE"           CHAR(4000),
  "SUBJECT"                    CHAR(4000),
  "PREDICATE"                  CHAR(4000),
  "OBJECT_OR_CONTENT"          CHAR(4000),
  "OCCURRENCE_LUNAR_TEXT"      CHAR(4000),
  "OCCURRENCE_PRECISION"       CHAR(4000),
  "HISTORICAL_PLACE"           CHAR(4000),
  "PLACE_STATUS"               CHAR(4000),
  "NAMED_ENTITIES"             CHAR(4000),
  "EPISTEMIC_SCOPE"            CHAR(4000),
  "CLAIM_TOPIC"                CHAR(4000),
  "CONFLICT_GROUP"             CHAR(4000),
  "SET_STATUS"                 CHAR(4000),
  "DIRECTNESS"                 CHAR(4000),
  "SOURCE_URL"                 CHAR(4000),
  "NOTES"                      CHAR(4000)
)
