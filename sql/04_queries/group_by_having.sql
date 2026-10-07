-- =============================================================================
-- group_by_having.sql — 집계 함수 · GROUP BY · HAVING · ROLLUP · CUBE · GROUPING SETS
-- =============================================================================

-- 1. status별 edge 수 (OBSERVED 4 / DERIVED 64)
SELECT status, COUNT(*) AS n_edges
  FROM dag_edge
 GROUP BY status
 ORDER BY status;

-- 2. edge type × status 교차 집계
SELECT edge_type, status, COUNT(*) AS n
  FROM dag_edge
 GROUP BY edge_type, status
 ORDER BY edge_type, status;

-- 3. HAVING: source별 episode 수가 3개 이상인 source만 (WHERE는 그룹 전, HAVING은 그룹 후)
SELECT es.source_record_id, sr.source_work, COUNT(*) AS n_episodes
  FROM v_episode_source es
  JOIN source_record sr ON sr.source_record_id = es.source_record_id
 GROUP BY es.source_record_id, sr.source_work
HAVING COUNT(*) >= 3
 ORDER BY n_episodes DESC;

-- 4. COUNT(*) · COUNT(컬럼) · COUNT(DISTINCT 컬럼) 의 차이
SELECT COUNT(*)                    AS n_rows,           -- 모든 행 41
       COUNT(t_max)                AS n_t_max_known,    -- NULL 제외
       COUNT(DISTINCT t_min)       AS n_distinct_t_min, -- 중복·NULL 제외
       COUNT(env_id)               AS n_env_nodes
  FROM dag_node;

-- 5. MIN / MAX / AVG / SUM: 후보의 추가 가정 수 통계 (gap별)
SELECT gap_id,
       COUNT(*)                     AS n_candidates,
       MIN(n_assumptions)           AS min_asm,
       MAX(n_assumptions)           AS max_asm,
       ROUND(AVG(n_assumptions), 2) AS avg_asm,
       SUM(n_assumptions)           AS sum_asm
  FROM latent_candidate
 GROUP BY gap_id
 ORDER BY gap_id;

-- 6. 조건부 집계(CASE를 집계 함수 안에): 후보 final 등급 분포를 gap별 한 줄로 (= 수동 PIVOT)
SELECT gap_id,
       COUNT(CASE WHEN overall = 'MEDIUM'       THEN 1 END) AS n_medium,
       COUNT(CASE WHEN overall = 'LOW'          THEN 1 END) AS n_low,
       COUNT(CASE WHEN overall = 'INCOMPATIBLE' THEN 1 END) AS n_incompatible
  FROM latent_candidate
 GROUP BY gap_id
 ORDER BY gap_id;

-- 7. ROLLUP: layer·status 소계와 총계 (Super-DAG node)
--    GROUPING(col) = 1 이면 그 행에서 col은 '소계로 묶인 자리'(원래 NULL이 아니라 집계 표시)
SELECT DECODE(GROUPING(sd_status), 1, '(전체)', sd_status) AS sd_status,
       DECODE(GROUPING(node_type), 1, '(소계)', node_type) AS node_type,
       COUNT(*) AS n
  FROM sd_node
 GROUP BY ROLLUP (sd_status, node_type)
 ORDER BY GROUPING(sd_status), sd_status, GROUPING(node_type), node_type;

-- 8. CUBE: origin × sd_status 모든 조합의 소계 (Super-DAG edge)
SELECT origin, sd_status, COUNT(*) AS n, GROUPING_ID(origin, sd_status) AS gid
  FROM sd_edge
 GROUP BY CUBE (origin, sd_status)
 ORDER BY gid, origin, sd_status;

-- 9. GROUPING SETS: 필요한 집계만 골라서 한 번에 (status별, edge_type별)
SELECT status, edge_type, COUNT(*) AS n
  FROM dag_edge
 GROUP BY GROUPING SETS ((status), (edge_type))
 ORDER BY status NULLS LAST, edge_type NULLS LAST;

-- 10. world별 bridge 수와 메커니즘별 bridge 수 (HAVING으로 2개 이상만)
SELECT wc.world_id, cm.mechanism_id, COUNT(*) AS n_bridges
  FROM world_candidate wc
  JOIN candidate_mechanism cm ON cm.candidate_id = wc.candidate_id AND cm.mapping_role = 'PRIMARY'
 GROUP BY wc.world_id, cm.mechanism_id
HAVING COUNT(*) >= 2
 ORDER BY wc.world_id, cm.mechanism_id;

-- 11. 중복 탐지(duplicate detection): 같은 (보고자, 주장 주제, 사료)를 가진 audit 명제
SELECT source_record_id, reporting_actor, claim_topic, COUNT(*) AS n,
       LISTAGG(prop_id, ',') WITHIN GROUP (ORDER BY prop_id) AS prop_ids
  FROM audit_proposition
 GROUP BY source_record_id, reporting_actor, claim_topic
HAVING COUNT(*) > 1
 ORDER BY n DESC, source_record_id;

-- 12. KEEP (DENSE_RANK FIRST/LAST) — Oracle 집계: gap마다 '추가 가정이 가장 적은' 후보 id
SELECT gap_id,
       MIN(n_assumptions)                                                   AS min_asm,
       MIN(candidate_id) KEEP (DENSE_RANK FIRST ORDER BY n_assumptions)     AS fewest_assumption_candidate
  FROM latent_candidate
 GROUP BY gap_id
 ORDER BY gap_id;
