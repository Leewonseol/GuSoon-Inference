-- =============================================================================
-- subqueries.sql — 스칼라 · 인라인 뷰 · 상관 서브쿼리 · EXISTS / NOT EXISTS · IN / ANY / ALL · WITH
-- =============================================================================

-- 1. 스칼라 서브쿼리(SELECT 절, 한 행 한 값): node마다 나가는 edge 수
SELECT n.node_id,
       n.title,
       (SELECT COUNT(*) FROM dag_edge e WHERE e.src = n.node_id) AS out_edges
  FROM dag_node n
 ORDER BY out_edges DESC, n.node_id;

-- 2. 인라인 뷰(FROM 절): layer별 node 수를 먼저 구하고 2개 이상인 layer만
SELECT v.layer, v.n_nodes
  FROM (SELECT layer, COUNT(*) AS n_nodes FROM dag_node GROUP BY layer) v
 WHERE v.n_nodes >= 2
 ORDER BY v.n_nodes DESC;

-- 3. EXISTS (semi-join): 미확정 동일성에 기대는 edge가 하나라도 있는 동일성
SELECT ir.identity_id, ir.surface_a, ir.surface_b
  FROM identity_register ir
 WHERE ir.status = 'UNRESOLVED'
   AND EXISTS (SELECT 1 FROM edge_identity_condition c WHERE c.identity_id = ir.identity_id);

-- 4. NOT EXISTS (anti-join): source와 연결되지 않은 node — 구성 fact가 없고 환경 근거도 없는 node
SELECT n.node_id, n.layer
  FROM dag_node n
 WHERE NOT EXISTS (SELECT 1 FROM episode_member em WHERE em.episode_id = n.node_id)
   AND n.env_id IS NULL;
-- 기대: 0행 (환경 node 4개는 env_id로 근거를 가진다)

-- 5. IN 서브쿼리: 경쟁 설명 world 중 하나라도 쓰는 후보
SELECT candidate_id, overall, label
  FROM latent_candidate
 WHERE candidate_id IN (SELECT wc.candidate_id
                          FROM world_candidate wc
                          JOIN narrative_world w ON w.world_id = wc.world_id
                         WHERE w.status = 'COMPETING_EXPLANATION')
 ORDER BY candidate_id;

-- 6. NOT IN의 NULL 함정: 하위 결과에 NULL이 하나라도 있으면 NOT IN은 아무 행도 돌려주지 않는다
--    world_identity에는 NULL이 없지만, NULL이 섞일 수 있는 컬럼(dag_node.env_id)으로 보이면:
SELECT COUNT(*) AS n_env_rows_not_used
  FROM environment_context ec
 WHERE ec.env_id NOT IN (SELECT n.env_id FROM dag_node n);           -- env_id에 NULL 37개 → 결과 0
SELECT COUNT(*) AS n_env_rows_not_used
  FROM environment_context ec
 WHERE NOT EXISTS (SELECT 1 FROM dag_node n WHERE n.env_id = ec.env_id);   -- 안전한 형태
-- 두 결과 모두 0이지만 이유가 다르다: 앞은 NULL 때문에 '항상' 0, 뒤는 실제로 모두 쓰여서 0.

-- 7. 상관 서브쿼리: 같은 gap 후보들 중 final 등급 점수가 그 gap 평균보다 높은 후보
SELECT c.gap_id, c.candidate_id, c.overall
  FROM latent_candidate c
 WHERE DECODE(c.overall, 'HIGH', 3, 'MEDIUM', 2, 'LOW', 1, 0)
     > (SELECT AVG(DECODE(x.overall, 'HIGH', 3, 'MEDIUM', 2, 'LOW', 1, 0))
          FROM latent_candidate x
         WHERE x.gap_id = c.gap_id)
 ORDER BY c.gap_id, c.candidate_id;

-- 8. ANY / ALL: 모든 환경 기록(ENV)보다 늦게 시작한 판단 node (> ALL)
SELECT node_id, t_min, title
  FROM dag_node
 WHERE layer = 'ROYAL_JUDGMENT'
   AND t_min > ALL (SELECT t_min FROM dag_node WHERE layer = 'ENVIRONMENT')
 ORDER BY node_id;

-- 9. 다중 컬럼 IN: 필수 관계(src, dst, type)가 실제 edge에 있는지
SELECT r.src, r.dst, r.edge_type, r.reason
  FROM rule_required_relation r
 WHERE (r.src, r.dst, r.edge_type) IN (SELECT e.src, e.dst, e.edge_type FROM dag_edge e)
 ORDER BY r.src, r.dst;

-- 10. WITH 절(공통 테이블 식): 진술 기반 episode와 그 진술자를 먼저 정의하고 재사용
WITH testimony_member AS (
    SELECT episode_id, fact_id, testifier
      FROM v_member_text
     WHERE fact_family = 'TESTIMONY'
),
testifier_count AS (
    SELECT testifier, COUNT(DISTINCT episode_id) AS n_episodes
      FROM testimony_member
     GROUP BY testifier
)
SELECT tc.testifier, tc.n_episodes
  FROM testifier_count tc
 ORDER BY tc.n_episodes DESC, tc.testifier;

-- 11. 서브쿼리로 UPDATE 대상 정하기 (실행하지 말고 읽기만 — 실습은 02_load/02_insert_examples.sql 2부)
-- UPDATE latent_candidate c
--    SET c.notes = c.notes || ' [검토]'
--  WHERE c.candidate_id IN (SELECT wc.candidate_id FROM world_candidate wc WHERE wc.world_id = 'W5');
