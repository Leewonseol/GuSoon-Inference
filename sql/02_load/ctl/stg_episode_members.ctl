-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/stg_episode_members.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'sql/02_load/data/episode_members.csv' "STR X'0D0A'"
APPEND
INTO TABLE STG_EPISODE_MEMBERS
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  "EPISODE_ID"                 CHAR(4000),
  "MEMBER_SEQ"                 CHAR(4000),
  "FACT_ID"                    CHAR(4000),
  "CLAUSE"                     CHAR(4000)
)
