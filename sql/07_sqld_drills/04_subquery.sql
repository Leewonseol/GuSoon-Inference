-- =============================================================================
-- 07_sqld_drills / 04_subquery.sql — EXISTS / NOT EXISTS / IN / 관계 나눗셈
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q13. [기본] NOT EXISTS를 사용하여 확정 사실(source)과 연결되지 않은 node를 찾으시오.
-- 힌트: node ↔ 확정 사실 연결은 episode_member.
-- 정답 SQL:
SELECT n.node_id, n.layer, n.env_id
  FROM dag_node n
 WHERE NOT EXISTS (SELECT 1
                     FROM episode_member em
                    WHERE em.episode_id = n.node_id)
 ORDER BY n.node_id;
-- 왜 맞는가: 상관 서브쿼리가 한 행도 못 찾으면 NOT EXISTS가 참이다(anti-join).
-- 자주 틀리는 포인트: 결과 4행은 오류가 아니다. 환경 context node(ENV01–ENV04)는 확정 사실이 아니라
--   03 환경 행(env_id)을 근거로 한다. 'source 없는 사건 node'를 찾으려면 AND n.env_id IS NULL을 더한다(→ 0행).
-- 기대 결과: ENV01, ENV02, ENV03, ENV04 (4행, 모두 env_id 있음)


-- -----------------------------------------------------------------------------
-- Q14. [중간] source basis(근거)가 하나도 없는 DERIVED edge를 찾으시오.
-- 정답 SQL:
SELECT e.edge_id, e.edge_type, e.src, e.dst
  FROM dag_edge e
 WHERE e.status = 'DERIVED'
   AND NOT EXISTS (SELECT 1
                     FROM edge_source_basis esb
                    WHERE esb.edge_id = e.edge_id);
-- 왜 맞는가: DERIVED edge는 관측 사실에서 규칙으로 이은 관계라 근거 fact가 반드시 있어야 한다(Audit 2 unsupported_edge).
-- 자주 틀리는 포인트:
--   * LEFT JOIN 후 WHERE esb.support_id IS NULL도 정답이다. 하지만 COUNT(*) = 0으로 세면 1이 나와 못 찾는다.
--   * NOT IN (SELECT edge_id FROM …)은 하위 결과에 NULL이 있으면 전부 거짓이 된다(이 표는 NOT NULL이라 괜찮다).
-- 기대 결과: 0행 (68개 edge 모두 근거 있음)


-- -----------------------------------------------------------------------------
-- Q15. [중간] (a) LATENT 후보를 하나도 쓰지 않는 world를 찾으시오.
--             (b) 어떤 경쟁 설명(COMPETING_EXPLANATION) world도 메우지 않은 gap을 찾으시오.
-- 정답 SQL:
-- (a)
SELECT w.world_id
  FROM narrative_world w
 WHERE NOT EXISTS (SELECT 1 FROM world_candidate wc WHERE wc.world_id = w.world_id);
-- (b)
SELECT g.gap_id, g.gap_status, g.title
  FROM gap g
 WHERE NOT EXISTS (SELECT 1
                     FROM world_candidate wc
                     JOIN narrative_world w ON w.world_id = wc.world_id
                    WHERE wc.gap_id = g.gap_id
                      AND w.status = 'COMPETING_EXPLANATION');
-- 왜 맞는가: '하나도 없다' = NOT EXISTS. (b)는 서브쿼리 안에서 조인해 경쟁 world만 본다.
-- 자주 틀리는 포인트: (b)에서 REJECTED world(W6)까지 세면 W6이 쓰는 gap(G06·G07·G12)이 '메워졌다'고 잘못 본다.
-- 기대 결과: (a) 0행 (모든 world가 bridge 3개 이상)   (b) G10 1행 — 사용자가 열어 둔 OPEN_UNRESOLVED gap


-- -----------------------------------------------------------------------------
-- Q16. [어려움] 최소 가정 world W5의 bridge를 '모두' 포함하는 world를 구하시오(W5 자신 제외). — 관계 나눗셈
-- 힌트: "W5의 bridge 중에 그 world에 없는 것이 존재하지 않는다" → NOT EXISTS 두 번.
-- 정답 SQL:
SELECT w.world_id
  FROM narrative_world w
 WHERE w.world_id <> 'W5'
   AND NOT EXISTS (SELECT 1
                     FROM world_candidate w5
                    WHERE w5.world_id = 'W5'
                      AND NOT EXISTS (SELECT 1
                                        FROM world_candidate x
                                       WHERE x.world_id = w.world_id
                                         AND x.candidate_id = w5.candidate_id));
-- 왜 맞는가: '모든 A에 대해 B'는 SQL에 직접 없다. '그렇지 않은 A가 존재하지 않는다'로 바꾼다(이중 부정).
-- 다른 정답(집계형): W5 bridge와 겹치는 개수 = W5 bridge 전체 개수
-- SELECT wc.world_id FROM world_candidate wc
--  WHERE wc.candidate_id IN (SELECT candidate_id FROM world_candidate WHERE world_id = 'W5')
--    AND wc.world_id <> 'W5'
--  GROUP BY wc.world_id
-- HAVING COUNT(*) = (SELECT COUNT(*) FROM world_candidate WHERE world_id = 'W5');
-- 자주 틀리는 포인트: IN만 쓰면 'W5 bridge를 하나라도' 가진 world가 모두 나온다(존재 ≠ 전부).
-- 기대 결과: W1 (W5 = {G01a, G06a, G07a, G08a}를 W1이 모두 쓴다. W3는 G01b, W2는 G06b, W4는 G07b·G08b를 쓴다)
