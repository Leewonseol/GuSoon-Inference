# 검증 보고 — Oracle SQL 레이어 (sql/)

작성 기준: 2026-10-07, 브랜치 `claude/confident-meitner-p96q4e`, 기준 커밋 `73b24f1`(작업 전 HEAD).

## 1. 실행 환경과 Oracle runtime

| 확인 | 결과 |
|---|---|
| `sqlplus`, `sql`(SQLcl) | 없음 |
| Docker | CLI는 있음(`/usr/bin/docker`). 데몬이 실행 중이 아니고(`/var/run/docker.sock` 없음), 데몬 기동은 작업 환경 정책에서 거부되었다. Oracle Free 컨테이너를 띄우지 않았다 |
| Oracle 설치 | 하지 않음(지시에 따라 무리하게 설치하지 않음) |
| **결론** | **Oracle runtime unavailable.** 이 레이어의 SQL은 Oracle에서 실행되지 않았다. 아래 검증은 문법 검토·스키마/참조 무결성 검토·기대 결과 대조까지다 |

## 2. 한 일과 결과

### 2-1. 문법 검토 (Oracle에서 실행한 것이 아님)

- `sqlglot` Oracle dialect 파서: 손으로 쓴 SQL과 생성 DDL의 **799개 문장 중 795개 파싱**(`generated/stg_inserts.sql` 1,101행은 생성기 출력이라 제외하고, 그 형식은 에뮬레이션에서 전부 실행됨).
- 파싱하지 못한 4개는 Oracle 문서상 유효한 문법이라 수동 검토했다: 가상 컬럼 `GENERATED ALWAYS AS (…) VIRTUAL` 3개(11g+), 재귀 WITH의 컬럼 목록 + `CYCLE … SET … DEFAULT` 절 1개(11gR2+).
- SQL*Plus 함정 점검: 문장 안 빈 줄 0, 문장 안 `&` 0(데이터의 `&`는 INSERT script 첫 줄 `SET DEFINE OFF`), 주석 끝 `;` 0.
- 금지 문법(`QUALIFY`, `FILTER`, `::`, `LIMIT`, BOOLEAN, `generate_series`, `WITH RECURSIVE`) 0건.
- 수동 검토로 고친 것: INSERT 생성기가 긴 문자열을 자를 때 `''`(작은따옴표 이스케이프)가 두 조각으로 갈라질 수 있던 문제, external table·SQL*Loader 필드 이름을 큰따옴표로 감싸 접근 파라미터 키워드(`VALUE` 등)와 충돌하지 않게 함, `CROSS JOIN LATERAL`(12c+)을 11g에서도 되는 `UNION` 형태로 바꿈, `LISTAGG(DISTINCT …)`(19c+)를 `DISTINCT` 인라인 뷰로 바꿈.

### 2-2. 스키마·참조 무결성 검토 — DuckDB 논리 에뮬레이션

도구: `sql/08_validation/duckdb_logic_check.py`. Oracle SQL을 텍스트 치환·`sqlglot` 변환·DuckDB 매크로(NVL·REGEXP_SUBSTR·TO_NUMBER 등)로 DuckDB 메모리 DB에서 돌린다. Oracle의 `''` = NULL 의미에 맞추려고 문자열 연결(`||`)은 NULL을 무시하는 `concat()`으로, `REGEXP_SUBSTR` 불일치는 NULL로 바꿨다. **Oracle 실행이 아니다.**

| 단계 | 결과 |
|---|---|
| STG 25표에 INSERT script 1,101행 적재 | 실패 0 |
| canonical 49표 생성(PK 49 · FK 52 = 일반 44 + 가상 컬럼 FK 8 · UNIQUE 6 · CHECK 76 · NOT NULL) 후 transform | 제약 위반 0 (실데이터가 모든 CHECK·복합 FK를 만족) |
| 가상 컬럼 FK 8개(DuckDB 미지원 → 같은 내용을 질의로) | 위반 0 |
| `03_load_validation.sql` | STG ↔ canonical 행 수 불일치 0, '\|' 목록 정규화 누락 0, DuckDB episode_members ↔ member_fact_ids 대칭 차집합 0행, 메커니즘 이름·world bridge 교차 일치 |
| 실행된 문장 | 238개 OK · FAILED 0 · CONNECT BY라 건너뜀 37 · Oracle 전용 함수라 건너뜀 13 |

건너뛴 Oracle 전용 13문장(04_queries·06_graph·drill 기준): PIVOT view 1, `ROWNUM` Top-N 1, `RATIO_TO_REPORT` 1, `LENGTHB` 1, `KEEP` 1, 재귀 WITH `CYCLE` 절 1, `LNNVL` 1, `TO_CHAR` 1, CONNECT BY로 만든 `v_dag_reachability`에 기대는 질의 5. 이와 별도로 `03_load_validation.sql`의 `user_constraints`·`TO_CHAR` 질의 2개도 건너뛰었다.

### 2-3. 기대 결과 대조 (Python ↔ SQL)

| 대조 | 결과 (에뮬레이션) |
|---|---|
| Audit 1–4 audit × severity | AUDIT1 UNRESOLVED 4 · INFO 13 / AUDIT2 5 · 1 / AUDIT3 1 · 11 / AUDIT4 20 · 2 — Python과 모두 일치, ERROR·WARN 0 |
| Audit 1–4 audit × check × severity | 불일치 0 |
| UNRESOLVED 대상 id(30건) 대칭 차집합 | 0행 |
| `expected_counts.sql` 지표 59개 | MATCH 56 · NOT PORTED 3(Audit 5) · DIFF 0 |
| `invariant_checks.sql` 불변식 20개 | 위반 0 |
| SQLD drill 37문제 | 비계층형 31문제: 에뮬레이션 결과와 문제의 '기대 결과'를 대조해 4곳(Q4·Q9·Q12·Q34)을 실제 값으로 고침. 계층형 6문제(Q22–Q26): 같은 edge 목록을 Python으로 따라가 기대 결과 확인 |

### 2-4. 결함 주입 — SQL audit가 결함을 실제로 잡는가

Python `regression.py`처럼, 정상 데이터에 결함을 하나씩 넣고(트랜잭션 안, 끝나면 ROLLBACK) SQL audit가 그 결함을 ERROR로 내는지 확인했다. 기준 상태 ERROR+WARN = 0.

| # | 주입한 결함 | 잡아야 할 검사 | 결과 |
|---|---|---|---|
| 1 | 필수 관계 OE056(EP15 REVISES EP25) 삭제 | AUDIT2 missing_relation | 탐지 1건 |
| 2 | EP01 → EP13 직접 RESPONSIBILITY_LINK | AUDIT2 causal_inflation | 탐지 2건(직접 사망 edge + 판단 아닌 대상) |
| 3 | EP37 → EP01 TEMPORAL_BEFORE | AUDIT2 acyclicity | 탐지 |
| 4 | 같은 결함 | AUDIT2 temporal_inversion | 탐지 |
| 5 | OE010의 ID08 condition 제거 | AUDIT2 identity_forcing | 탐지 |
| 6 | OE001 근거 삭제 | AUDIT2 unsupported_edge | 탐지 |
| 7 | 후보 G01a를 final HIGH로 | AUDIT3 bridge_support_inflation | 탐지 |
| 8 | EP01 summary '진술했' → '말했' | AUDIT1 testimony_to_fact | 탐지 2건 |
| 9 | EP29 caution에 '구순 때문에 김명신이 죽었다' | AUDIT1 responsibility_to_causation | 탐지 |
| 10 | EP07 summary '한 비장' → '한재욱' | AUDIT1 surface_form_substitution | 탐지 |
| 11 | W1이 OPEN_UNRESOLVED gap G10을 G10a로 채움 | AUDIT3 open_gap_filled | 탐지 |
| 12 | W5 narrative에서 [L] 표지 삭제 | AUDIT3 latent_as_observed | 탐지 |
| 13 | W1 M1 configuration을 UNSPECIFIED로 | AUDIT4 config_value | 탐지 |
| 14 | 제도 피쳐 → 관측 사건 Super-DAG edge | AUDIT4 institution_to_event | 탐지 |
| 15 | W6(REJECTED)을 개입 분석에 넣음 | AUDIT4 w6_reactivation | 탐지 |

**15/15 탐지.** (DuckDB는 FK가 걸린 부모 행 UPDATE를 막기 때문에 결함 주입은 FK를 뺀 사본 DB에서 했다.)

## 3. 기존 프로젝트 보호 확인

| 확인 | 결과 |
|---|---|
| 기존 Python build(`python3 scripts/gusun_clean/build.py`) 실행 | 작업 트리 사본(`sql/` 포함)에서 실행: regression 64/64 탐지, 모든 audit gate 통과 |
| Audit 1–5 결과 | AUDIT1 ERROR 0 · WARN 0 · INFO 13 · UNRESOLVED 4 / AUDIT2 0 · 0 · 1 · 5 / AUDIT3(world 포함) 0 · 0 · 11 · 1 / AUDIT4 0 · 0 · 2 · 20 / AUDIT5 0 · 0 · 5 · 0 — 작업 전과 같음 |
| frozen graph hash | `ccb7ec63763a715ae90c74dfff37d3ed7980fa705fd152f59de8bed2e31d4e0c` (structure `0b691344…`, topology `04c84b0e…`, 둘 다 unchanged = true) — 작업 전과 같음 |
| canonical node / edge | 41 / 68 — 같음 |
| 산출물 비교 | build가 다시 쓴 `output/`·`docs/`·`database/gusun_clean.duckdb`가 저장소 파일과 **바이트 단위로 같음**(`diff -rq`, `cmp`) |
| `git diff`(추적 파일) | 변경 0. 새로 생긴 것은 `sql/` 폴더뿐 |
| canonical CSV·Python 코드·DuckDB·docs·world/mechanism 정의·audit 판정·동결 graph·사료 해석 | 수정하지 않음 |

## 4. Oracle에서 확인해야 할 남은 것

1. `@sql/…` 실행 순서(`sql/README.md` §3) 그대로 Oracle Free 23ai 또는 XE 21c에서 실행.
2. `02_load/03_load_validation.sql`의 모든 '문제 행' 질의가 0행인지.
3. `05_audits/audit_summary.sql` §3·§4의 comparison이 모두 MATCH(Audit 5는 NOT PORTED)인지, §5·§6이 0행인지.
4. `08_validation/expected_counts.sql` 요약이 DIFF 0인지, `invariant_checks.sql` verdict가 모두 OK인지.
5. 06_graph·계층형 drill의 결과가 각 파일 주석의 '기대 결과'와 같은지 — 이 부분은 에뮬레이션으로 실행하지 못했다.
6. 가상 컬럼 FK가 거부되는 환경이면 `sql/README.md` §7의 대안(실제 컬럼 + CHECK)으로 바꾼다.
