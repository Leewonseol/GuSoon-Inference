# 02_load — canonical CSV를 Oracle로 넣기

> **실행 상태: Oracle runtime unavailable.** 이 저장소의 작업 환경에는 Oracle 서버·sqlplus·SQLcl이 없고 Docker 데몬도 꺼져 있어 아래 스크립트를 Oracle에서 실행하지 못했다. SQL 문법 검토와 DuckDB 논리 에뮬레이션(`../08_validation/duckdb_logic_check.py`)까지만 했다. 자세한 범위는 `../08_validation/validation_report.md`.

## 흐름

```
canonical CSV (25개, 읽기만)                       sql/02_load/
  gusun_clean_restart_csv_pack/*.csv  ─┐
  output/clean/*.csv                  ─┼─▶ STG_* (문자 그대로, 00_staging_tables.sql)
  sql/02_load/data/*.csv (DuckDB 추출) ─┘        │   방법 A external table / B SQL*Loader / C INSERT script
                                                 ▼
        02_insert_examples.sql 1부 ─▶ 참조·규칙 표(ref_*, rule_*)
                                                 ▼
        04_transform_to_canonical.sql ─▶ canonical 표(형 변환, '|' 목록 정규화, UNPIVOT, 제약 검사)
                                                 ▼
        03_load_validation.sql ─▶ 행 수·정규화 누락·교차 검증 (문제 행만 출력)
```

## 파일

| 파일 | 내용 | 생성 방식 |
|---|---|---|
| `generate_load_scripts.py` | 아래 생성물을 만드는 스크립트. canonical CSV header를 그대로 읽는다 | 손으로 작성 |
| `00_staging_tables.sql` | `STG_*` 25개. 모든 컬럼 `VARCHAR2(4000 BYTE)`, `narrative`만 `CLOB` | 생성 |
| `01_external_tables_or_sqlldr.sql` | 방법 A: `X_*` external table 25개(ORACLE_LOADER) + `INSERT INTO STG_* SELECT * FROM X_*` | 생성 |
| `ctl/stg_*.ctl` | 방법 B: SQL*Loader control file 25개 | 생성 |
| `generated/stg_inserts.sql` | 방법 C: `INSERT` 1,101행(서버 파일 접근 없이 SQL*Plus/SQLcl만으로) | 생성 |
| `data/episode_members.csv` | DuckDB `episode_members`(52행) 추출 — CSV로는 없던 Python 산출물 | 생성 |
| `data/py_audit_findings.csv` | DuckDB `audit_findings`(62행) 추출 — Python Audit 1–5 결과 | 생성 |
| `data/dag_freeze.csv` | `output/clean/observed_dag_freeze.json` 추출 — 동결 해시·집계 | 생성 |
| `02_insert_examples.sql` | 1부: 참조·규칙 표 INSERT(Python 상수 이식) / 2부: DML 연습(SAVEPOINT·ROLLBACK) | 손으로 작성 |
| `04_transform_to_canonical.sql` | STG → canonical | 손으로 작성 |
| `03_load_validation.sql` | 적재 검증 | 손으로 작성 |

생성물을 다시 만들려면 저장소 루트에서 `python3 sql/02_load/generate_load_scripts.py`(duckdb 모듈 필요). 입력이 같으면 출력도 같다.

## 실행 순서 (SQL*Plus / SQLcl, 스키마 사용자로 접속)

```sql
-- 0) 한 번만: 사용자와 권한 (DBA)
--    CREATE USER gusun IDENTIFIED BY ... QUOTA UNLIMITED ON USERS;
--    GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW TO gusun;
--    방법 A를 쓰면 CREATE ANY DIRECTORY 또는 DBA가 만든 DIRECTORY의 READ·WRITE 권한도 필요

@sql/01_schema/01_tables.sql
@sql/01_schema/02_constraints.sql
@sql/01_schema/03_indexes.sql
@sql/01_schema/04_comments.sql
@sql/02_load/00_staging_tables.sql

-- 아래 셋 중 하나
@sql/02_load/01_external_tables_or_sqlldr.sql      -- 방법 A (DIRECTORY 경로를 먼저 고칠 것)
--   또는 셸에서: for f in sql/02_load/ctl/*.ctl; do sqlldr userid=... control=$f; done   -- 방법 B
--   또는:       @sql/02_load/generated/stg_inserts.sql                                    -- 방법 C

@sql/02_load/02_insert_examples.sql                 -- 1부 참조·규칙 표 (2부 DML 연습은 끝에서 ROLLBACK)
@sql/02_load/04_transform_to_canonical.sql
@sql/02_load/03_load_validation.sql
```

`02_insert_examples.sql`의 2부(DML 연습)는 canonical 표가 채워진 뒤에야 의미가 있다. 처음 적재할 때는 1부만 실행되도록 2부 앞에서 끊거나, transform 뒤에 파일을 한 번 더 실행해도 된다(1부를 두 번 실행하면 PK 중복 오류가 나므로 2부 블록만 따로 실행할 것).

## 클라이언트 설정

- 한글: 클라이언트 문자셋을 UTF-8로 (`export NLS_LANG=AMERICAN_AMERICA.AL32UTF8`). DB 문자셋은 AL32UTF8을 가정한다(Oracle XE·Free 기본값).
- `SET DEFINE OFF`: 데이터에 `&`가 있다(05 명제 29행 등). INSERT script는 첫 줄에서 끈다.
- CSV 형식 실측: UTF-8, 줄 끝 CRLF, 첫 줄 header, pack 6개는 BOM 포함, 필드 안 줄바꿈·큰따옴표 없음. 그래서 `RECORDS DELIMITED BY 0x'0D0A'`, `SKIP 1`, `OPTIONALLY ENCLOSED BY '"'`로 충분하다(`FIELDS CSV WITH EMBEDDED`는 12.2+에서만 필요).

## 정규화 기법 — '|' 목록을 행으로

CSV의 다중 값 컬럼(`supporting`, `basis`, `latent_bridges` 등)은 연결 테이블로 편다.

```sql
SELECT e.edge_id, REGEXP_SUBSTR(e.supporting, '[^|]+', 1, seq.n) AS support_id
  FROM dag_edge e
  JOIN (SELECT LEVEL AS n FROM dual CONNECT BY LEVEL <= 20) seq      -- 1..20 행 생성기
    ON seq.n <= REGEXP_COUNT(e.supporting, '[^|]+');
```

원문 목록 컬럼은 canonical 표에도 그대로 남겨 두고(Python 산출물과 같은 값), `03_load_validation.sql` §2가 "원소 수 합계 = 연결 테이블 행 수"를 확인한다.
