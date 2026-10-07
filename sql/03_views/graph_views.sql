-- =============================================================================
-- graph_views.sql — observed DAG를 그래프로 읽기 위한 view
-- =============================================================================

-- 1. v_node_degree — node별 진입·진출 차수 (0/0이면 고립 node)
--    두 집계를 따로 만든 뒤 LEFT JOIN: edge가 없는 node도 0으로 남는다.
CREATE OR REPLACE VIEW v_node_degree AS
SELECT n.node_id,
       n.layer,
       NVL(o.out_degree, 0)                          AS out_degree,
       NVL(i.in_degree, 0)                           AS in_degree,
       NVL(o.out_degree, 0) + NVL(i.in_degree, 0)    AS total_degree,
       CASE
           WHEN NVL(i.in_degree, 0) = 0 AND NVL(o.out_degree, 0) = 0 THEN 'ISOLATED'
           WHEN NVL(i.in_degree, 0) = 0                               THEN 'SOURCE'   -- 들어오는 edge 없음(DAG의 시작점)
           WHEN NVL(o.out_degree, 0) = 0                              THEN 'SINK'     -- 나가는 edge 없음(DAG의 끝점)
           ELSE 'INTERNAL'
       END                                           AS position
  FROM dag_node n
  LEFT JOIN (SELECT src AS node_id, COUNT(*) AS out_degree FROM dag_edge GROUP BY src) o
         ON o.node_id = n.node_id
  LEFT JOIN (SELECT dst AS node_id, COUNT(*) AS in_degree FROM dag_edge GROUP BY dst) i
         ON i.node_id = n.node_id;

-- 2. v_node_allowed_support — node가 edge 근거로 내놓을 수 있는 근거 id
--    사건 node: 구성 confirmed fact / 환경 node: env_id (Audit 2 'endpoint 밖의 근거 fact' 기준)
CREATE OR REPLACE VIEW v_node_allowed_support AS
SELECT em.episode_id AS node_id, em.fact_id AS support_id
  FROM episode_member em
UNION
SELECT n.node_id, n.env_id
  FROM dag_node n
 WHERE n.env_id IS NOT NULL;

-- 3. v_edge_support_check — edge 근거 한 줄마다 '양 끝 node의 구성 근거인가' 표시
CREATE OR REPLACE VIEW v_edge_support_check AS
SELECT esb.edge_id,
       e.edge_type,
       e.status,
       e.src,
       e.dst,
       esb.support_id,
       CASE WHEN EXISTS (SELECT 1
                           FROM v_node_allowed_support a
                          WHERE a.support_id = esb.support_id
                            AND a.node_id IN (e.src, e.dst))
            THEN 'Y' ELSE 'N'
       END AS in_endpoint
  FROM edge_source_basis esb
  JOIN dag_edge e ON e.edge_id = esb.edge_id;

-- 4. v_edge_support_summary — edge별 근거 수, endpoint 근거 수, endpoint 밖 근거 목록
CREATE OR REPLACE VIEW v_edge_support_summary AS
SELECT e.edge_id,
       e.edge_type,
       e.status,
       COUNT(c.support_id)                                          AS n_support,
       COUNT(CASE WHEN c.in_endpoint = 'Y' THEN 1 END)              AS n_in_endpoint,
       LISTAGG(CASE WHEN c.in_endpoint = 'N' THEN c.support_id END, ',')
           WITHIN GROUP (ORDER BY c.support_id)                     AS outside_supports
  FROM dag_edge e
  LEFT JOIN v_edge_support_check c ON c.edge_id = e.edge_id
 GROUP BY e.edge_id, e.edge_type, e.status;

-- 5. v_edge_basis_flags — basis 목록을 컬럼 플래그로 (GROUP BY + CASE 피벗)
CREATE OR REPLACE VIEW v_edge_basis_flags AS
SELECT b.edge_id,
       COUNT(*)                                                                AS n_basis,
       MAX(CASE WHEN b.basis_code = 'SOURCE_DIRECT'               THEN 'Y' END) AS has_source_direct,
       MAX(CASE WHEN b.basis_code = 'TEMPORAL'                    THEN 'Y' END) AS has_temporal,
       MAX(CASE WHEN b.basis_code = 'PROCEDURAL'                  THEN 'Y' END) AS has_procedural,
       MAX(CASE WHEN b.basis_code = 'ENVIRONMENTAL_CONTEXT'       THEN 'Y' END) AS has_env_context,
       MAX(CASE WHEN b.basis_code = 'INSTITUTIONAL_COMPATIBILITY' THEN 'Y' END) AS has_institutional
  FROM edge_basis_type b
 GROUP BY b.edge_id;

-- 6. 관점별 edge 묶음 — 계층형 질의(06_graph)가 출발점으로 쓴다 -------------------
-- 판단 검토·번복·충돌 사슬 (review / revision chain)
CREATE OR REPLACE VIEW v_review_edges AS
SELECT edge_id, src, dst, edge_type, status
  FROM dag_edge
 WHERE edge_type IN ('REVIEW_OF', 'REVISES', 'CONTRADICTS_AT_CLAIM_LEVEL');

-- 책임 귀속 사슬 (RESPONSIBILITY_LINK는 정조 판단 node로만 들어간다)
CREATE OR REPLACE VIEW v_responsibility_edges AS
SELECT edge_id, src, dst, edge_type, status
  FROM dag_edge
 WHERE edge_type = 'RESPONSIBILITY_LINK';

-- 정보 흐름·지시·절차 사슬 (information-flow chain)
CREATE OR REPLACE VIEW v_flow_edges AS
SELECT edge_id, src, dst, edge_type, status
  FROM dag_edge
 WHERE edge_type IN ('INFORMATION_FLOW', 'ORDER_TO_ACTION', 'PROCEDURAL_NEXT', 'TEMPORAL_BEFORE');
