# SQLD 문제집 — 구순–김명신 사건(1793) 데이터로 푸는 37문제

교과서의 EMP·DEPT 대신 이 프로젝트의 실제 표(확정 사실, observed DAG, LATENT 후보, world, 메커니즘)를 쓴다.
각 문제는 **문제 / 힌트 / 정답 SQL / 왜 맞는가 / 자주 틀리는 포인트 / 기대 결과** 순서다.

- 선행: `sql/01_schema` → `sql/02_load` → `sql/03_views` (Q37·Q8 일부는 `sql/05_audits` 뒤)
- 기대 결과는 canonical 데이터 기준이다. 계층형(CONNECT BY) 문제를 뺀 문제는 DuckDB 논리 에뮬레이션으로 결과를 확인했고, 계층형 문제의 기대 결과는 같은 그래프를 Python으로 따라가 확인했다. Oracle에서 직접 실행한 결과는 아니다(`sql/README.md` §실행 상태).
- 풀 때는 정답 SQL을 가리고 문제와 힌트만 보고 먼저 써 볼 것.

## 난이도 분포

| 난이도 | 문제 수 | 문제 |
|---|---|---|
| 기본 | 12 | Q1 Q2 Q3 Q4 Q5 Q9 Q10 Q13 Q17 Q27 Q28 Q30 |
| 중간 | 14 | Q6 Q7 Q8 Q11 Q12 Q14 Q15 Q18 Q19 Q22 Q23 Q29 Q31 Q32 |
| 어려움 | 11 | Q16 Q20 Q21 Q24 Q25 Q26 Q33 Q34 Q35 Q36 Q37 |
| 합계 | 37 | |

## 문제 목록

| 번호 | 파일 | 난이도 | SQLD 개념 | 프로젝트 질문 |
|---|---|---|---|---|
| Q1 | 01_select_where | 기본 | WHERE, COUNT | OBSERVED status인 node 수 |
| Q2 | 01_select_where | 기본 | 비교, AND | 음력 3/4 하루 사건 (발생일 ≠ 기록일) |
| Q3 | 01_select_where | 기본 | LIKE | 제목에 '정조'가 든 국왕 판단 |
| Q4 | 01_select_where | 기본 | FETCH FIRST WITH TIES, ROWNUM 함정 | 추가 가정 최다 후보 Top-3(동점 포함) |
| Q5 | 02_join | 기본 | INNER JOIN | UNRESOLVED 동일성에 의존하는 edge |
| Q6 | 02_join | 중간 | 같은 표 두 번 조인 | REVIEW_OF의 검토 대상·검토자 제목 |
| Q7 | 02_join | 중간 | LEFT JOIN + COUNT(col) | 제도 피쳐별 링크 수(0 포함) |
| Q8 | 02_join | 중간 | M:N 다중 조인 | W2의 bridge와 주 메커니즘 |
| Q9 | 03_group_by | 기본 | GROUP BY, HAVING, COUNT(DISTINCT) | source별 episode 수 ≥ 3 |
| Q10 | 03_group_by | 기본 | GROUP BY 규칙 | world별 latent candidate 수 |
| Q11 | 03_group_by | 중간 | 조건부 집계, ROLLUP, GROUPING | edge type별 OBSERVED/DERIVED + 합계 |
| Q12 | 03_group_by | 중간 | HAVING 복합 조건 | 후보 ≥ 3인데 MEDIUM 없는 gap |
| Q13 | 04_subquery | 기본 | NOT EXISTS | source와 연결되지 않은 node |
| Q14 | 04_subquery | 중간 | NOT EXISTS, NOT IN 함정 | source basis 없는 DERIVED edge |
| Q15 | 04_subquery | 중간 | anti-join + 조인 서브쿼리 | 후보 없는 world / 아무도 안 메운 gap |
| Q16 | 04_subquery | 어려움 | 관계 나눗셈(이중 NOT EXISTS) | W5 bridge를 모두 포함하는 world |
| Q17 | 05_analytic | 기본 | ROW_NUMBER | 같은 사건의 판단 순서 |
| Q18 | 05_analytic | 중간 | RANK vs DENSE_RANK | 같은 날짜 판단의 순위 차이 |
| Q19 | 05_analytic | 중간 | LAG, 인라인 뷰 | 직전 판단과 layer가 바뀐 지점 |
| Q20 | 05_analytic | 어려움 | ROW_NUMBER = 1 (QUALIFY 없이) | branch별 최신 판단 |
| Q21 | 05_analytic | 어려움 | FIRST_VALUE/LAST_VALUE, 창 함정 | branch의 첫·마지막 판단 |
| Q22 | 06_hierarchical | 중간 | START WITH, CONNECT BY, PRIOR, SYS_CONNECT_BY_PATH | 5월 → 6월 revision chain |
| Q23 | 06_hierarchical | 중간 | CONNECT_BY_ISLEAF | 3/4 체포 이후 끝 node까지 경로 |
| Q24 | 06_hierarchical | 어려움 | 역방향 계층 + GROUP BY | 책임 판단의 직접·간접 조상 |
| Q25 | 06_hierarchical | 어려움 | NOCYCLE, CONNECT_BY_ISCYCLE | 가짜 edge로 cycle 검출 |
| Q26 | 06_hierarchical | 어려움 | 계층 결과를 인라인 뷰로 조인 | EP01에서 닿는 판단(경로 vs 직접 edge) |
| Q27 | 07_null_case | 기본 | COUNT(*) − COUNT(col) | t_max 없는 node 수 |
| Q28 | 07_null_case | 기본 | 단순 CASE + GROUP BY | Super-DAG 상태 5분류 |
| Q29 | 07_null_case | 중간 | NOT IN + NULL 함정 | 쓰이지 않은 환경 행 |
| Q30 | 08_set_operators | 기본 | UNION vs UNION ALL | 조건에 쓰인 동일성 ID |
| Q31 | 08_set_operators | 중간 | INTERSECT | W1·W2 공통 bridge |
| Q32 | 08_set_operators | 중간 | MINUS | W1에만 있고 W5에는 없는 bridge |
| Q33 | 08_set_operators | 어려움 | 대칭 차집합(MINUS 양방향) | frozen edge ↔ Super-DAG FROZEN edge |
| Q34 | 09_comprehensive | 어려움 | CROSS JOIN 격자 + 자기 조인 + NVL | world 쌍의 gap 차이 |
| Q35 | 09_comprehensive | 어려움 | 다중 조인 + LISTAGG | configuration과 후보 사용의 모순 |
| Q36 | 09_comprehensive | 어려움 | WITH + 행 생성기 + LIKE 경계 검색 | 여러 메커니즘이 설명하는 구조 변수 |
| Q37 | 09_comprehensive | 어려움 | FULL OUTER JOIN + NVL | Python vs SQL audit 대조 |

## 자주 나오는 Oracle 오류 번호 (문제 해설에 나온 것)

| 오류 | 뜻 | 나온 문제 |
|---|---|---|
| ORA-00918 | column ambiguously defined (별칭 없이 같은 컬럼명) | Q6 |
| ORA-00934 | group function is not allowed here (WHERE에 집계) | Q9 |
| ORA-00979 | not a GROUP BY expression | Q10 |
| ORA-00904 | invalid identifier (GROUP BY에 SELECT 별칭, 23ai 이전) | Q28 |
| ORA-30483 | window functions are not allowed here (WHERE에 분석 함수) | Q19 |
| ORA-01436 | CONNECT BY loop in user data (NOCYCLE 없이 cycle) | Q25 |
| ORA-30930 | NOCYCLE keyword is required with CONNECT_BY_ISCYCLE | Q25 |
