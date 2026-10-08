-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_py_audit_findings.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'sql/02_load/data/py_audit_findings.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_PY_AUDIT_FINDINGS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "FINDING_SEQ"                CHAR(4000),
  "AUDIT_NAME"                 CHAR(4000),
  "CHECK_NAME"                 CHAR(4000),
  "SEVERITY"                   CHAR(4000),
  "TARGET"                     CHAR(4000),
  "MESSAGE"                    CHAR(4000)
)
