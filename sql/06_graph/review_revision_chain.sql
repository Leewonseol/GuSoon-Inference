-- =============================================================================
-- review_revision_chain.sql — 판단의 검토·번복 사슬 (5월 → 6월)과 Super-DAG 설명 사슬
-- -----------------------------------------------------------------------------
-- 이 사건의 판단 변화는 지우지 않고 node로 남는다:
--   EP15 5/12 정조 1차 판단(도난 부재 방향)  ─REVISES─▶ EP25 6/13 정조 최종 판단(도난 실재)
--   EP15 ─CONTRADICTS_AT_CLAIM_LEVEL─▶ EP24 홍대협 도난 판단 ─REVIEW_OF─▶ EP25
--   EP17 5/27 이조원 보고 ─CONTRADICTS─▶ EP24
-- =============================================================================

-- Q1. 5월 1차 판단(EP15)에서 시작하는 검토·번복·충돌 사슬
--     CONNECT BY에 edge_type 조건을 넣어 '판단 관계' edge만 따라간다(절차 edge는 따라가지 않음).
SELECT LEVEL                                                 AS depth,
       LPAD(' ', 2 * (LEVEL - 1)) || e.edge_type || ' → ' || e.dst AS chain_step,
       d.title                                               AS judged_node,
       d.record_lunar_date                                   AS record_date,
       'EP15' || SYS_CONNECT_BY_PATH(e.dst, ' > ')           AS path
  FROM dag_edge e
  JOIN dag_node d ON d.node_id = e.dst
 START WITH e.src = 'EP15'
        AND e.edge_type IN ('REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL')
CONNECT BY NOCYCLE PRIOR e.dst = e.src
       AND e.edge_type IN ('REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL')
 ORDER SIBLINGS BY e.dst;

-- Q2. May → June revision order: 5월 기록 판단에서 출발해 6월 기록 판단으로 가는 판단 사슬 전부
--     START WITH에 서브쿼리 조건을 쓸 수 있다. 출발 node의 기록일(5월)과 도착 node의 기록일(6월)을 함께 본다.
SELECT CONNECT_BY_ROOT e.src                        AS may_node,
       CONNECT_BY_ROOT s.record_lunar_date          AS may_record_date,
       e.dst                                        AS june_node,
       d.record_lunar_date                          AS june_record_date,
       LEVEL                                        AS steps,
       CONNECT_BY_ROOT e.src || SYS_CONNECT_BY_PATH(e.dst, ' > ') AS path
  FROM dag_edge e
  JOIN dag_node s ON s.node_id = e.src
  JOIN dag_node d ON d.node_id = e.dst
 WHERE d.record_lunar_date LIKE '1793-06-%'
 START WITH e.edge_type IN ('REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL')
        AND s.record_lunar_date LIKE '1793-05-%'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
       AND e.edge_type IN ('REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL')
 ORDER BY may_node, steps, june_node;

-- Q3. 최종 도난 판단(EP25)을 만든 검토 계보 — 조상 방향, 판단 관계만
SELECT LEVEL                                        AS hops_back,
       LPAD(' ', 2 * (LEVEL - 1)) || e.src          AS reviewed_node,
       e.edge_type,
       s.layer,
       s.record_lunar_date
  FROM dag_edge e
  JOIN dag_node s ON s.node_id = e.src
 START WITH e.dst = 'EP25'
        AND e.edge_type IN ('REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL')
CONNECT BY NOCYCLE PRIOR e.src = e.dst
       AND e.edge_type IN ('REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL')
 ORDER SIBLINGS BY e.src;

-- Q4. 사인 판단 사슬(branch A): 이형원 장계(EP13) → 홍대협 질병 평가(EP26) → 정조 전염병 판단(EP27)
--     환경 context(ENV…)는 CONTEXT_SUPPORTS로 판단에만 들어온다 — 사슬의 출발점이 아니라 곁가지로 표시.
SELECT LEVEL AS depth,
       e.src || ' -[' || e.edge_type || ']-> ' || e.dst AS step,
       CONNECT_BY_ISLEAF AS is_leaf
  FROM dag_edge e
 START WITH e.dst = 'EP27'
CONNECT BY NOCYCLE PRIOR e.src = e.dst
       AND e.edge_type IN ('REVIEW_OF', 'CONTEXT_SUPPORTS', 'CONTRADICTS_AT_CLAIM_LEVEL')
 ORDER SIBLINGS BY e.src;

-- Q5. 처분의 번복: 이형원 파직(EP36) → 6/16 유임(EP37). 사유는 OPEN_UNRESOLVED(gap G10)
SELECT e.src, s.title AS from_title, e.edge_type, e.dst, d.title AS to_title,
       g.gap_id, g.gap_status
  FROM dag_edge e
  JOIN dag_node s ON s.node_id = e.src
  JOIN dag_node d ON d.node_id = e.dst
  LEFT JOIN gap_anchor_node ga ON ga.node_id = e.dst
  LEFT JOIN gap g              ON g.gap_id = ga.gap_id
 WHERE e.edge_type = 'REVISES'
 ORDER BY e.edge_id;

-- Q6. Super-DAG 설명 사슬: 메커니즘 M1 → 후보 → 구조 변수 → 관측 전이
--     sd_edge도 같은 방식으로 계층형 질의를 쓸 수 있다. node_type을 경로에 함께 적는다.
SELECT LEVEL                                                  AS depth,
       LPAD(' ', 2 * (LEVEL - 1)) || e.dst                    AS node_indented,
       d.node_type,
       d.sd_status,
       e.edge_type
  FROM sd_edge e
  JOIN sd_node d ON d.node_id = e.dst
 START WITH e.src = 'M1'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
       AND e.origin = 'SUPER_DAG'                             -- frozen edge로는 넘어가지 않는다
 ORDER SIBLINGS BY e.dst;

-- Q7. 구조 변수 규칙의 입력 계층: V_RESPONSIBILITY가 어떤 변수·메커니즘에 기대는가 (RULE_INPUT 등 역방향)
SELECT LEVEL AS depth,
       LPAD(' ', 2 * (LEVEL - 1)) || e.src AS input_node,
       s.node_type,
       e.edge_type
  FROM sd_edge e
  JOIN sd_node s ON s.node_id = e.src
 START WITH e.dst = 'V_RESPONSIBILITY'
CONNECT BY NOCYCLE PRIOR e.src = e.dst
       AND e.edge_type IN ('RULE_INPUT', 'CONTRIBUTES_TO', 'INSTANTIATED_BY', 'ANCHORED_TO')
 ORDER SIBLINGS BY e.src;

-- Q8. UNRESOLVED 항목이 조건으로 걸린 후보와 그 메커니즘 — 미확정 동일성이 어디까지 영향을 주는가
SELECT CONNECT_BY_ROOT e.src                         AS unresolved_item,
       LEVEL                                          AS depth,
       e.dst                                          AS affected_node,
       d.node_type,
       CONNECT_BY_ROOT e.src || SYS_CONNECT_BY_PATH(e.dst, ' > ') AS path
  FROM sd_edge e
  JOIN sd_node d ON d.node_id = e.dst
 START WITH e.edge_type = 'CONDITIONS'
CONNECT BY NOCYCLE PRIOR e.dst = e.src
       AND e.edge_type IN ('CONTRIBUTES_TO', 'EXPLAINS_TRANSITION_TO', 'EXPLAINS_OBSERVED')
 ORDER BY unresolved_item, depth, affected_node;
