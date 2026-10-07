-- =============================================================================
-- 07_sqld_drills / 02_join.sql — 조인
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q5. [기본] 미확정(UNRESOLVED) 동일성에 의존하는 edge를 구하시오(edge_id, identity_id, surface_a, surface_b).
-- 힌트: edge_identity_condition(edge ↔ 동일성)과 identity_register를 조인하고 status로 거른다.
-- 정답 SQL:
SELECT c.edge_id, c.identity_id, ir.surface_a, ir.surface_b
  FROM edge_identity_condition c
  JOIN identity_register ir ON ir.identity_id = c.identity_id
 WHERE ir.status = 'UNRESOLVED'
 ORDER BY c.edge_id;
-- 왜 맞는가: 연결 테이블이 '어느 edge가 어느 동일성에 기대는지'를 행으로 갖고 있다. 상태는 대장 쪽에만 있다.
-- 자주 틀리는 포인트:
--   * dag_edge.condition IS NOT NULL만 보면 4건(OE040의 ID09 포함)이 나온다. ID09는 ACCEPTED_BY_PROVENANCE로
--     '미확정'이 아니다. 상태를 대장에서 확인해야 한다.
-- 기대 결과: OE010(ID08), OE071(ID06), OE080(ID07) — 3행 (Python Audit 2 conditional_edge UNRESOLVED 3건과 같음)


-- -----------------------------------------------------------------------------
-- Q6. [중간] REVIEW_OF edge마다 '검토 대상 node 제목'과 '검토한 node 제목'을 함께 출력하시오.
-- 힌트: dag_node를 두 번(별칭 2개) 조인한다.
-- 정답 SQL:
SELECT e.edge_id,
       src.title AS reviewed_title,
       dst.title AS reviewer_title,
       e.status
  FROM dag_edge e
  JOIN dag_node src ON src.node_id = e.src
  JOIN dag_node dst ON dst.node_id = e.dst
 WHERE e.edge_type = 'REVIEW_OF'
 ORDER BY e.edge_id;
-- 왜 맞는가: 한 행에 두 node의 속성이 필요하면 같은 표를 다른 별칭으로 두 번 조인한다(자기 조인과 같은 원리).
-- 자주 틀리는 포인트: 별칭 없이 dag_node를 두 번 쓰면 ORA-00918(column ambiguously defined).
-- 기대 결과: 9행 (OBSERVED 2: OE043, OE047 / DERIVED 7)


-- -----------------------------------------------------------------------------
-- Q7. [중간] 제도 피쳐 20개(F001–F020) 각각이 평가한 node·edge 링크 수를 구하시오. 링크가 없는 피쳐도 0으로 출력.
-- 힌트: institutional_feature 기준 LEFT JOIN. node_feature_link.inst_feature_id는 제도 피쳐일 때만 값이 있는 가상 컬럼.
-- 정답 SQL:
SELECT f.feature_id, f.feature_name, COUNT(l.link_id) AS n_links
  FROM institutional_feature f
  LEFT JOIN node_feature_link l ON l.inst_feature_id = f.feature_id
 GROUP BY f.feature_id, f.feature_name
 ORDER BY f.feature_id;
-- 왜 맞는가: 짝이 없는 피쳐 행도 남기려면 피쳐 쪽을 보존(LEFT)해야 하고, 개수는 오른쪽 컬럼으로 센다.
-- 자주 틀리는 포인트:
--   * COUNT(*)로 세면 링크 없는 피쳐가 0이 아니라 1이 된다(NULL로 채운 한 행도 행이다).
--   * INNER JOIN이면 링크 없는 피쳐가 사라진다.
-- 기대 결과: 20행, n_links 합계 = 49 (제도 링크 45 + edge 링크 4)


-- -----------------------------------------------------------------------------
-- Q8. [중간] world W2가 쓰는 bridge(후보)를 bridge 순서대로, 후보의 final 등급과 주(PRIMARY) 메커니즘 이름과 함께 출력하시오.
-- 힌트: narrative_world → world_candidate → latent_candidate / candidate_mechanism → mechanism.
-- 정답 SQL:
SELECT wc.bridge_seq, wc.candidate_id, lc.overall, m.mechanism_name
  FROM world_candidate wc
  JOIN latent_candidate lc    ON lc.candidate_id = wc.candidate_id
  JOIN candidate_mechanism cm ON cm.candidate_id = wc.candidate_id
                             AND cm.mapping_role = 'PRIMARY'
  JOIN mechanism m            ON m.mechanism_id = cm.mechanism_id
 WHERE wc.world_id = 'W2'
 ORDER BY wc.bridge_seq;
-- 왜 맞는가: M:N 관계(world↔후보, 후보↔메커니즘)는 연결 테이블을 거쳐 조인한다.
-- 자주 틀리는 포인트: mapping_role 조건을 빼면 G07c처럼 보조(SECONDARY) 메커니즘이 있는 후보가 두 번 나온다.
-- 기대 결과: 9행 — G01a(M1) G02b(M4) G03a(M1) G04b(M2) G06b(MB) G07c(M2) G08a(M5) G09a(M5) G12a(MB)
