-- =============================================================================
-- 07_sqld_drills / 03_group_by.sql — GROUP BY · HAVING · 조건부 집계
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Q9. [기본] 사료 기사(source)별 episode 수를 구하고, 3개 이상인 source만 많은 순으로 출력하시오.
-- 힌트: episode ↔ source는 episode_member → confirmed_fact → source_record. 한 episode가 같은 source의
--       fact 여러 개로 이루어질 수 있으니 episode를 '중복 없이' 센다.
-- 정답 SQL:
SELECT cf.source_record_id, COUNT(DISTINCT em.episode_id) AS n_episodes
  FROM episode_member em
  JOIN confirmed_fact cf ON cf.fact_id = em.fact_id
 GROUP BY cf.source_record_id
HAVING COUNT(DISTINCT em.episode_id) >= 3
 ORDER BY n_episodes DESC, cf.source_record_id;
-- 왜 맞는가: 그룹 조건(개수 ≥ 3)은 GROUP BY 뒤에 걸러야 하므로 HAVING이다.
-- 자주 틀리는 포인트:
--   * WHERE COUNT(*) >= 3 → ORA-00934(group function is not allowed here).
--   * COUNT(*)로 세면 member 행 수(= fact 수)를 센다. episode 수가 아니다.
-- 기대 결과: SRC3_006(26), SRC3_001(4) — 2행. 홍대협 복명·정조 최종 심리 기사(SRC3_006, 6/13)에 공초 진술과 최종 판단 episode가 몰려 있다


-- -----------------------------------------------------------------------------
-- Q10. [기본] world별로 포함된 LATENT 후보(bridge) 수를 구하시오. world 상태(status)도 함께.
-- 정답 SQL:
SELECT w.world_id, w.status, COUNT(wc.candidate_id) AS n_bridges
  FROM narrative_world w
  LEFT JOIN world_candidate wc ON wc.world_id = w.world_id
 GROUP BY w.world_id, w.status
 ORDER BY w.world_id;
-- 왜 맞는가: SELECT에 쓴 집계 아닌 컬럼(world_id, status)은 모두 GROUP BY에 있어야 한다.
-- 자주 틀리는 포인트: GROUP BY에 status를 빼면 ORA-00979(not a GROUP BY expression).
-- 기대 결과: W1 12 / W2 9 / W3 8 / W4 8 / W5 4 / W6(REJECTED) 3


-- -----------------------------------------------------------------------------
-- Q11. [중간] edge type마다 OBSERVED 수와 DERIVED 수를 한 행에 출력하고, 마지막에 전체 합계 행을 붙이시오.
-- 힌트: COUNT(CASE …) 조건부 집계 + GROUP BY ROLLUP. 합계 행은 GROUPING()으로 이름을 붙인다.
-- 정답 SQL:
SELECT CASE WHEN GROUPING(edge_type) = 1 THEN '(합계)' ELSE edge_type END AS edge_type,
       COUNT(CASE WHEN status = 'OBSERVED' THEN 1 END) AS n_observed,
       COUNT(CASE WHEN status = 'DERIVED'  THEN 1 END) AS n_derived,
       COUNT(*)                                        AS n_total
  FROM dag_edge
 GROUP BY ROLLUP (edge_type)
 ORDER BY GROUPING(edge_type), edge_type;
-- 왜 맞는가: CASE가 조건에 맞지 않으면 NULL → COUNT가 세지 않는다. ROLLUP(col)은 col별 + 전체 합계 행.
-- 자주 틀리는 포인트: SUM(CASE … THEN 1 ELSE 0 END)도 맞다. COUNT(CASE … ELSE 0 END)는 틀린다(0도 센다).
-- 기대 결과: 9개 type + 합계 1행. 합계 행 = OBSERVED 4 / DERIVED 64 / 68


-- -----------------------------------------------------------------------------
-- Q12. [중간] 후보가 3개 이상인 gap 중에서 final 등급(overall)이 MEDIUM인 후보가 하나도 없는 gap을 구하시오.
-- 정답 SQL:
SELECT gap_id,
       COUNT(*)                                         AS n_candidates,
       COUNT(CASE WHEN overall = 'MEDIUM' THEN 1 END)   AS n_medium
  FROM latent_candidate
 GROUP BY gap_id
HAVING COUNT(*) >= 3
   AND COUNT(CASE WHEN overall = 'MEDIUM' THEN 1 END) = 0
 ORDER BY gap_id;
-- 왜 맞는가: HAVING에는 집계 조건을 AND로 여러 개 걸 수 있다.
-- 자주 틀리는 포인트: WHERE overall <> 'MEDIUM'을 먼저 걸면 MEDIUM이 있는 gap도 '남은 후보'로 살아남는다.
-- 기대 결과: G09(후보 3, MEDIUM 0), G11(후보 3, MEDIUM 0) — 2행
