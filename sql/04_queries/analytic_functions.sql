-- =============================================================================
-- analytic_functions.sql — 분석(윈도우) 함수
-- -----------------------------------------------------------------------------
-- 형식: 함수() OVER (PARTITION BY 묶음 ORDER BY 순서 [ROWS|RANGE 창])
-- 집계 함수와 달리 행 수가 줄지 않는다. 각 행에 '그 행이 속한 묶음 기준 값'을 붙인다.
-- 이 사건의 날짜 정렬 키: 발생 시점 NVL(t_max, t_min)(음력 MMDD), 같은 값이면 node_id.
-- =============================================================================

-- 1. ROW_NUMBER — 같은 사건(도난 판단 branch)에 대한 판단 순서
--    왜: 동점이 있어도 1,2,3…으로 '순번'을 매겨야 할 때. 같은 날(6/13) 판단도 node_id로 갈라 순서를 준다.
SELECT n.node_id,
       n.layer,
       n.title,
       NVL(n.t_max, n.t_min) AS sort_key,
       ROW_NUMBER() OVER (PARTITION BY n.branch ORDER BY NVL(n.t_max, n.t_min), n.node_id) AS judgment_seq
  FROM dag_node n
 WHERE n.branch = 'THEFT_JUDGMENT'
 ORDER BY judgment_seq;

-- 2. RANK vs DENSE_RANK — 같은 날짜 사건의 순위 차이
--    왜: RANK는 동점 뒤 번호를 건너뛰고(1,1,3), DENSE_RANK는 건너뛰지 않는다(1,1,2).
--        6월 13일(613)에 판단 node가 몰려 있어 차이가 크게 드러난다.
SELECT n.node_id,
       NVL(n.t_max, n.t_min)                                         AS sort_key,
       RANK()       OVER (ORDER BY NVL(n.t_max, n.t_min))            AS rnk,
       DENSE_RANK() OVER (ORDER BY NVL(n.t_max, n.t_min))            AS dense_rnk,
       ROW_NUMBER() OVER (ORDER BY NVL(n.t_max, n.t_min), n.node_id) AS row_num
  FROM dag_node n
 WHERE n.t_min IS NOT NULL
 ORDER BY sort_key, n.node_id;

-- 3. LAG / LEAD — 직전 판단과 다음 판단
--    왜: 같은 묶음 안에서 앞·뒤 행 값을 자기 행에 가져와 '판단이 어떻게 바뀌었는가'를 한 줄에서 비교한다.
SELECT n.node_id,
       n.layer,
       n.title,
       LAG(n.node_id)  OVER (ORDER BY NVL(n.t_max, n.t_min), n.node_id) AS prev_judgment,
       LAG(n.layer)    OVER (ORDER BY NVL(n.t_max, n.t_min), n.node_id) AS prev_layer,
       LEAD(n.node_id) OVER (ORDER BY NVL(n.t_max, n.t_min), n.node_id) AS next_judgment
  FROM dag_node n
 WHERE n.branch = 'THEFT_JUDGMENT'
 ORDER BY NVL(n.t_max, n.t_min), n.node_id;

-- 4. 최신 판단 선택 — branch마다 가장 늦은 판단 1건 (ROW_NUMBER = 1 패턴)
--    왜: '그룹별 최신 1건'은 GROUP BY MAX로는 다른 컬럼을 같이 못 가져온다. 순번을 매긴 뒤 1번만 남긴다.
--    Oracle에는 QUALIFY가 없으므로 인라인 뷰로 감싼다.
SELECT branch, node_id, title, sort_key
  FROM (SELECT n.branch, n.node_id, n.title, NVL(n.t_max, n.t_min) AS sort_key,
               ROW_NUMBER() OVER (PARTITION BY n.branch
                                  ORDER BY NVL(n.t_max, n.t_min) DESC, n.node_id DESC) AS rn
          FROM dag_node n
         WHERE n.layer IN ('ROYAL_JUDGMENT', 'OFFICIAL_FINDING', 'OFFICIAL_EVALUATION', 'INSPECTOR_REPORT'))
 WHERE rn = 1
 ORDER BY branch;

-- 5. FIRST_VALUE / LAST_VALUE — branch의 첫 판단과 마지막 판단을 모든 행에
--    왜: 각 행 옆에 '처음 판단'과 '최종 판단'을 붙여 변화를 본다.
--    주의: ORDER BY가 있는 OVER의 기본 창은 'RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW'라서
--          LAST_VALUE가 '현재 행'을 돌려준다(단골 함정). 창을 끝까지 넓혀야 한다.
SELECT n.node_id,
       n.branch,
       FIRST_VALUE(n.node_id) OVER (PARTITION BY n.branch
                                    ORDER BY NVL(n.t_max, n.t_min), n.node_id)            AS first_in_branch,
       LAST_VALUE(n.node_id)  OVER (PARTITION BY n.branch
                                    ORDER BY NVL(n.t_max, n.t_min), n.node_id
                                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_in_branch,
       LAST_VALUE(n.node_id)  OVER (PARTITION BY n.branch
                                    ORDER BY NVL(n.t_max, n.t_min), n.node_id)            AS last_default_window
  FROM dag_node n
 WHERE n.branch IN ('THEFT_JUDGMENT', 'BIOLOGICAL', 'JISE')
 ORDER BY n.branch, NVL(n.t_max, n.t_min), n.node_id;

-- 6. COUNT OVER — source별 확정 사실 수를 각 행에 (행을 줄이지 않는 집계)
--    왜: 각 사실 옆에 '같은 사료에서 나온 사실이 몇 개인가'를 붙인다.
SELECT cf.fact_id,
       cf.source_record_id,
       COUNT(*) OVER (PARTITION BY cf.source_record_id) AS facts_in_same_source,
       COUNT(*) OVER ()                                 AS facts_total
  FROM confirmed_fact cf
 ORDER BY cf.source_record_id, cf.fact_id;

-- 7. SUM OVER (누적 합) — 기록일 순으로 쌓이는 확정 사실 수
--    왜: 사료 기사가 하나씩 더해질 때 확정 사실이 어떻게 늘어나는지(running total).
SELECT record_lunar_date,
       COUNT(*)                                        AS facts_on_date,
       SUM(COUNT(*)) OVER (ORDER BY record_lunar_date) AS cumulative_facts   -- 집계 결과에 다시 분석 함수
  FROM confirmed_fact
 GROUP BY record_lunar_date
 ORDER BY record_lunar_date;

-- 8. source별 검토 순서 — 같은 사료 안에서 audit 명제 순번
--    왜: 사료 기사마다 명제를 1번부터 다시 세어 '그 기사의 몇 번째 진술인가'를 본다.
SELECT p.source_record_id,
       p.prop_id,
       p.reporting_actor,
       ROW_NUMBER() OVER (PARTITION BY p.source_record_id ORDER BY p.prop_id) AS seq_in_source
  FROM audit_proposition p
 ORDER BY p.source_record_id, seq_in_source;

-- 9. 월별 기록 순서 — 기록 월(음력)마다 사료 기사 순번
SELECT SUBSTR(sr.record_lunar_date, 1, 7)                                     AS record_month,
       sr.source_record_id,
       sr.record_lunar_date,
       DENSE_RANK() OVER (PARTITION BY SUBSTR(sr.record_lunar_date, 1, 7)
                          ORDER BY sr.record_lunar_date)                      AS date_rank_in_month,
       ROW_NUMBER() OVER (PARTITION BY SUBSTR(sr.record_lunar_date, 1, 7)
                          ORDER BY sr.record_lunar_date, sr.source_record_id) AS seq_in_month
  FROM source_record sr
 ORDER BY record_month, seq_in_month;

-- 10. 동일 group 내 중복 제거 — (보고자, 주장 주제)마다 첫 명제만 남기기
--     왜: DISTINCT는 '모든 컬럼'이 같아야 지운다. 일부 컬럼 기준 중복 제거는 ROW_NUMBER로 한다.
SELECT source_record_id, reporting_actor, claim_topic, prop_id
  FROM (SELECT p.*,
               ROW_NUMBER() OVER (PARTITION BY p.reporting_actor, p.claim_topic ORDER BY p.prop_id) AS rn
          FROM audit_proposition p)
 WHERE rn = 1
 ORDER BY reporting_actor, claim_topic;

-- 11. 비율 — RATIO_TO_REPORT(Oracle)와 같은 값을 COUNT OVER로
SELECT edge_type,
       COUNT(*)                                          AS n,
       ROUND(RATIO_TO_REPORT(COUNT(*)) OVER () * 100, 1) AS pct_oracle,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 1)  AS pct_standard
  FROM dag_edge
 GROUP BY edge_type
 ORDER BY n DESC;

-- 12. 이동 창(ROWS BETWEEN): 기록일 순 3개 기사 이동 합 (자기 + 앞 2개)
SELECT source_record_id,
       record_lunar_date,
       n_props,
       SUM(n_props) OVER (ORDER BY record_lunar_date, source_record_id
                          ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_3_sum
  FROM (SELECT sr.source_record_id, sr.record_lunar_date, COUNT(p.prop_id) AS n_props
          FROM source_record sr
          LEFT JOIN audit_proposition p ON p.source_record_id = sr.source_record_id
         GROUP BY sr.source_record_id, sr.record_lunar_date)
 ORDER BY record_lunar_date, source_record_id;

-- 13. NTILE — 후보를 추가 가정 수로 3구간
SELECT candidate_id, n_assumptions,
       NTILE(3) OVER (ORDER BY n_assumptions, candidate_id) AS assumption_tier
  FROM latent_candidate
 ORDER BY assumption_tier, candidate_id;
