-- =============================================================================
-- world_mechanism_views.sql — world · 후보 · 메커니즘 관계 view
-- -----------------------------------------------------------------------------
-- World = configuration, Mechanism = 분석 변수, LATENT 후보 = 가설.
-- view는 이 관계를 보여 주기만 한다. 서로 다른 world의 LATENT 가설을 합치지 않는다.
-- =============================================================================

-- 1. v_world_candidate_detail — world가 쓰는 후보(bridge)와 그 등급·주 메커니즘
CREATE OR REPLACE VIEW v_world_candidate_detail AS
SELECT w.world_id,
       w.status                AS world_status,
       wc.bridge_seq,
       wc.gap_id,
       c.candidate_id,
       c.overall,
       c.source_support,
       c.contradiction_risk,
       cm.mechanism_id         AS primary_mechanism
  FROM narrative_world w
  JOIN world_candidate wc     ON wc.world_id = w.world_id
  JOIN latent_candidate c     ON c.candidate_id = wc.candidate_id
  LEFT JOIN candidate_mechanism cm
         ON cm.candidate_id = c.candidate_id
        AND cm.mapping_role = 'PRIMARY';

-- 2. v_world_gap_grid — world × gap 전체 격자 (CROSS JOIN 후 LEFT JOIN)
--    world가 그 gap을 어떤 후보로 메웠는지, 아니면 비워 두었는지(NULL)를 한 표로 본다.
CREATE OR REPLACE VIEW v_world_gap_grid AS
SELECT w.world_id,
       w.status AS world_status,
       g.gap_id,
       g.gap_status,
       wc.candidate_id,
       CASE WHEN wc.candidate_id IS NULL THEN 'EMPTY' ELSE 'FILLED' END AS fill_state
  FROM narrative_world w
 CROSS JOIN gap g
  LEFT JOIN world_candidate wc
         ON wc.world_id = w.world_id
        AND wc.gap_id = g.gap_id;

-- 3. v_world_pair_gap_diff — world 쌍마다 서로 다른 gap 수 (Audit 3: 2개 이상이어야 함)
--    같은 격자를 두 번 쓰는 자기 조인. NVL로 NULL(빈 gap)끼리도 비교한다.
CREATE OR REPLACE VIEW v_world_pair_gap_diff AS
SELECT a.world_id AS world_a,
       b.world_id AS world_b,
       SUM(CASE WHEN NVL(a.candidate_id, '-') <> NVL(b.candidate_id, '-') THEN 1 ELSE 0 END) AS n_diff_gaps
  FROM v_world_gap_grid a
  JOIN v_world_gap_grid b
    ON b.gap_id = a.gap_id
   AND a.world_id < b.world_id
 GROUP BY a.world_id, b.world_id;

-- 4. v_world_mechanism_matrix — 세로 config를 다시 가로로 (PIVOT, Oracle 11g+)
--    world_mechanism_configurations.csv와 같은 모양이 나와야 한다.
CREATE OR REPLACE VIEW v_world_mechanism_matrix AS
SELECT *
  FROM (SELECT world_id, mechanism_id, config_value
          FROM world_mechanism_config)
 PIVOT (MAX(config_value)
        FOR mechanism_id IN ('M1' AS m1, 'M2' AS m2, 'M3' AS m3, 'M4' AS m4,
                             'M5' AS m5, 'M6' AS m6, 'MB' AS mb));

-- 5. v_mechanism_candidate_count — 메커니즘별 후보 수 (PRIMARY / SECONDARY)와 mechanism.n_candidates 비교
CREATE OR REPLACE VIEW v_mechanism_candidate_count AS
SELECT m.mechanism_id,
       m.mechanism_name,
       m.branch,
       m.n_candidates                                               AS declared_n_candidates,
       COUNT(CASE WHEN cm.mapping_role = 'PRIMARY'   THEN 1 END)    AS n_primary,
       COUNT(CASE WHEN cm.mapping_role = 'SECONDARY' THEN 1 END)    AS n_secondary
  FROM mechanism m
  LEFT JOIN candidate_mechanism cm ON cm.mechanism_id = m.mechanism_id
 GROUP BY m.mechanism_id, m.mechanism_name, m.branch, m.n_candidates;

-- 6. v_world_mechanism_usage — world마다 메커니즘별로 쓰는 후보 수와 config 값
CREATE OR REPLACE VIEW v_world_mechanism_usage AS
SELECT cfg.world_id,
       cfg.mechanism_id,
       cfg.config_value,
       (SELECT COUNT(*)
          FROM world_candidate wc
          JOIN candidate_mechanism cm
            ON cm.candidate_id = wc.candidate_id
           AND cm.mapping_role = 'PRIMARY'
         WHERE wc.world_id = cfg.world_id
           AND cm.mechanism_id = cfg.mechanism_id)       AS n_primary_bridges,
       (SELECT COUNT(*)
          FROM world_candidate wc
          JOIN rule_candidate_negates ng ON ng.candidate_id = wc.candidate_id
         WHERE wc.world_id = cfg.world_id
           AND ng.mechanism_id = cfg.mechanism_id)       AS n_negating_bridges,
       cfg.config_basis
  FROM world_mechanism_config cfg;
