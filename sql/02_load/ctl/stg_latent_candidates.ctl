-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_latent_candidates.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'output/clean/latent_candidates.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_LATENT_CANDIDATES
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "CANDIDATE_ID"               CHAR(4000),
  "GAP_ID"                     CHAR(4000),
  "STATUS"                     CHAR(4000),
  "FORM"                       CHAR(4000),
  "LABEL"                      CHAR(4000),
  "DESCRIPTION"                CHAR(4000),
  "SOURCE_CONSISTENCY"         CHAR(4000),
  "TEMPORAL_FIT"               CHAR(4000),
  "INSTITUTIONAL_FIT"          CHAR(4000),
  "ROLE_FIT"                   CHAR(4000),
  "INFORMATION_FLOW_FIT"       CHAR(4000),
  "ENVIRONMENTAL_FIT"          CHAR(4000),
  "CONTRADICTION_RISK"         CHAR(4000),
  "N_ASSUMPTIONS"              CHAR(4000),
  "EXTRA_ASSUMPTIONS"          CHAR(4000),
  "IDENTITY_CONDITIONS"        CHAR(4000),
  "OVERALL"                    CHAR(4000),
  "PRUNE_DECISION"             CHAR(4000),
  "SUPPORTS"                   CHAR(4000),
  "CONFLICTS"                  CHAR(4000),
  "AUDIT_ATTESTATION"          CHAR(4000),
  "SUPPORT_BASIS"              CHAR(4000),
  "NOTES"                      CHAR(4000),
  "OBSERVED_LEFT"              CHAR(4000),
  "OBSERVED_RIGHT"             CHAR(4000),
  "LATENT_BRIDGE_CLAIM"        CHAR(4000),
  "BRIDGE_DIRECTLY_ATTESTED"   CHAR(4000),
  "ENDPOINT_SUPPORT"           CHAR(4000),
  "SOURCE_SUPPORT"             CHAR(4000),
  "BRIDGE_EVIDENCE"            CHAR(4000),
  "BRIDGE_BASIS"               CHAR(4000),
  "EVIDENCE_GRADE"             CHAR(4000),
  "PLAUSIBILITY_GRADE"         CHAR(4000),
  "SOURCE_CONSISTENCY_V1"      CHAR(4000),
  "OVERALL_V1"                 CHAR(4000),
  "REAUDIT_REASON"             CHAR(4000)
)
