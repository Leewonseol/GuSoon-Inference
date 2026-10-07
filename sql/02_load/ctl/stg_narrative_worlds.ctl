-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_narrative_worlds.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/narrative_worlds.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_NARRATIVE_WORLDS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "WORLD_ID"                   CHAR(4000),
  "NAME"                       CHAR(4000),
  "STATUS"                     CHAR(4000),
  "LATENT_BRIDGES"             CHAR(4000),
  "UNRESOLVED_GAPS"            CHAR(4000),
  "INSTITUTIONAL_FIT"          CHAR(4000),
  "ENVIRONMENTAL_FIT"          CHAR(4000),
  "N_ASSUMPTIONS"              CHAR(4000),
  "MIN_GRADE"                  CHAR(4000),
  "MAIN_ASSUMPTIONS"           CHAR(4000),
  "MAIN_WEAKNESSES"            CHAR(4000),
  "CONTRADICTED_EVIDENCE"      CHAR(4000),
  "STORY_IMPLICATION"          CHAR(4000),
  "IDENTITY_CONDITIONS"        CHAR(4000),
  "RESOLVED_IDENTITIES"        CHAR(4000),
  "EVIDENCE_PROFILE"           CHAR(4000),
  "WORK_ROLE"                  CHAR(4000),
  "STORY_QUESTION"             CHAR(4000),
  "DIFFERENCE"                 CHAR(4000),
  "UNIQUE_BRIDGES"             CHAR(4000),
  "NARRATIVE"                  CHAR(4000)
)
