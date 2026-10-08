-- =============================================================================
-- temporal_queries.sql — 발생 시점과 기록 시점을 섞지 않는 시간 질의
-- -----------------------------------------------------------------------------
-- 이 프로젝트의 시간 컬럼 (모두 음력 1793년)
--   confirmed_fact.chronology            : 사건 흐름상 시점 서술(문자열)
--   confirmed_fact.occurrence_lunar_text : 발생일 원문(있을 때만. '1793-02 초순' 같은 정밀도 낮은 값 포함)
--   confirmed_fact.record_lunar_date     : 기록일 = 사료 기사 날짜 (source_record.record_lunar_date와 같아야 함)
--   dag_node.t_min / t_max               : episode 발생 구간, 음력 MMDD 정수. 모르면 NULL
--   dag_node.record_lunar_date           : episode가 기록된 날짜
-- 원칙: 날짜가 없는 사건(EP08)에 날짜를 만들지 않는다. NULL은 비교에서 빠진다.
-- =============================================================================

-- 1. 발생일 vs 기록일 나란히 — 발생은 2~3월인데 기록은 5~6월인 공초 진술이 대부분이다
SELECT t.node_id,
       t.t_min,
       t.t_max,
       t.time_shape,
       t.record_lunar_date,
       t.record_md,
       t.record_md - NVL(t.t_max, t.t_min) AS record_minus_occurrence_md   -- MMDD 차(일수 아님, 지연 크기 감)
  FROM v_node_timeline t
 ORDER BY t.sort_key NULLS LAST, t.node_id;

-- 2. temporal inversion — edge의 출발이 도착보다 늦은 경우 (CONTRADICTS 제외). 기대: 0행
SELECT d.edge_id, d.edge_type, d.src, d.src_t_min, d.dst, d.dst_t_max
  FROM v_edge_detail d
 WHERE d.edge_type <> 'CONTRADICTS_AT_CLAIM_LEVEL'
   AND d.src_t_min > d.dst_t_max;

-- 3. occurrence vs record date confusion — 기록일이 발생 시점(t_min)으로 쓰였는지
--    t_min = 기록일인데 원문 시점 서술(chronology·occurrence)에 그 날짜가 없고 공초도 아니면 혼동. 기대: 0행
SELECT DISTINCT t.episode_id, t.t_min, m.record_lunar_date, t.chron_text
  FROM v_episode_text t
  JOIN v_member_text m ON m.episode_id = t.episode_id
 WHERE t.t_min = m.record_md
   AND INSTR(t.chron_text, m.record_lunar_date) = 0
   AND INSTR(t.chron_text, '공초') = 0;

-- 3-1. 반대로 정상 사례: 기록일과 발생일이 같은 공식 기록(장계·판단은 기록일 = 행위일)
SELECT n.node_id, n.layer, n.t_min, n.record_lunar_date
  FROM v_node_timeline n
 WHERE n.t_min = n.record_md
 ORDER BY n.node_id;

-- 4. 확정 사실의 기록일이 출처 기사의 기록일과 같은가 (fact ↔ source 정합). 기대: 0행
SELECT cf.fact_id, cf.record_lunar_date AS fact_record_date, sr.record_lunar_date AS source_date
  FROM confirmed_fact cf
  JOIN source_record sr ON sr.source_record_id = cf.source_record_id
 WHERE cf.record_lunar_date <> sr.record_lunar_date;

-- 5. 날짜 없는 사건은 '날짜 미기록'으로 남긴다 (임의 날짜 금지)
SELECT node_id, title, occurrence_text,
       NVL(TO_CHAR(t_min), '날짜 미기록') AS t_min_display
  FROM dag_node
 WHERE t_min IS NULL;

-- 6. review sequence — 검토(REVIEW_OF)는 검토 대상보다 같거나 늦게 기록되어야 한다. 기대: 0행
SELECT d.edge_id, d.src, s.record_md AS src_record_md, d.dst, t.record_md AS dst_record_md
  FROM v_edge_detail d
  JOIN v_node_timeline s ON s.node_id = d.src
  JOIN v_node_timeline t ON t.node_id = d.dst
 WHERE d.edge_type IN ('REVIEW_OF', 'REVISES')
   AND s.record_md > t.record_md;

-- 7. May → June revision order — 5월 판단이 6월 판단에 의해 번복(REVISES)되었는지와 순서
SELECT e.edge_id,
       e.src, s.record_lunar_date AS src_record,
       e.dst, d.record_lunar_date AS dst_record,
       CASE WHEN s.record_lunar_date < d.record_lunar_date THEN 'MAY_BEFORE_JUNE' ELSE 'CHECK' END AS order_check
  FROM dag_edge e
  JOIN dag_node s ON s.node_id = e.src
  JOIN dag_node d ON d.node_id = e.dst
 WHERE e.edge_type = 'REVISES'
 ORDER BY e.edge_id;
-- 'YYYY-MM-DD' 고정 길이 문자열은 사전순 비교가 날짜순과 같다(이 프로젝트가 DATE 대신 문자열을 쓰는 이유 중 하나).

-- 8. arrest → detention → review → final judgment 순서 (절차 단계를 고정 목록으로 두고 LAG로 검사)
WITH stage AS (
    SELECT 1 AS stage_no, 'EP09' AS node_id, 'arrest order (3/4 체포 지시)'       AS stage_name FROM dual UNION ALL
    SELECT 2, 'EP11', 'arrest (3/4 체포)'                                         FROM dual UNION ALL
    SELECT 3, 'EP13', 'detention·death report (5/12 구금·사망 보고)'             FROM dual UNION ALL
    SELECT 4, 'EP15', 'first review (5/12 정조 1차 판단)'                        FROM dual UNION ALL
    SELECT 5, 'EP23', 're-investigation (6/13 홍대협 신문·복명)'                 FROM dual UNION ALL
    SELECT 6, 'EP25', 'final judgment (6/13 정조 최종 판단)'                     FROM dual
)
SELECT st.stage_no,
       st.stage_name,
       n.t_min,
       n.t_max,
       LAG(NVL(n.t_max, n.t_min)) OVER (ORDER BY st.stage_no)                 AS prev_stage_time,
       CASE WHEN n.t_min < LAG(NVL(n.t_max, n.t_min)) OVER (ORDER BY st.stage_no)
            THEN 'OUT_OF_ORDER' ELSE 'OK' END                                AS order_check
  FROM stage st
  JOIN dag_node n ON n.node_id = st.node_id
 ORDER BY st.stage_no;

-- 9. 같은 기록일에 몇 개의 판단이 나왔나 — 6월 13일 하루에 판단·처분이 몰린 것을 확인
SELECT record_lunar_date, layer, COUNT(*) AS n
  FROM dag_node
 WHERE layer LIKE 'ROYAL%' OR layer LIKE 'OFFICIAL%'
 GROUP BY record_lunar_date, layer
 ORDER BY record_lunar_date, layer;

-- 10. 환경 context는 판단 시점 '이전' 것만 맥락이 된다 — CONTEXT_SUPPORTS edge의 시간 검사. 기대: 0행
SELECT d.edge_id, d.src, d.src_t_min, d.dst, d.dst_t_max
  FROM v_edge_detail d
 WHERE d.edge_type = 'CONTEXT_SUPPORTS'
   AND d.src_layer = 'ENVIRONMENT'
   AND d.src_t_min > d.dst_t_max;

-- 11. 발생 정밀도 — audit 명제의 occurrence_precision 분포 (정밀도 낮은 값을 '일' 단위로 바꾸지 않는다)
SELECT occurrence_precision, COUNT(*) AS n,
       COUNT(occurrence_lunar_text) AS n_with_text
  FROM audit_proposition
 GROUP BY occurrence_precision
 ORDER BY n DESC;
