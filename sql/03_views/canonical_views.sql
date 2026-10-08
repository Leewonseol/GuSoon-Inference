-- =============================================================================
-- canonical_views.sql — canonical 표를 읽기 쉽게 묶은 view
-- -----------------------------------------------------------------------------
-- view는 저장된 SELECT다. 데이터를 복사하지 않으므로 canonical 표가 바뀌면 결과도 따라 바뀐다.
-- 이 파일의 view는 새 사실·판단을 만들지 않는다(조인·집계·표시용 계산만).
-- =============================================================================

-- 1. v_episode — 사건 episode만 (환경 context node 제외) -------------------------
CREATE OR REPLACE VIEW v_episode AS
SELECT n.node_id AS episode_id,
       n.layer,
       n.branch,
       n.title,
       n.summary,
       n.attesting_actor,
       n.occurrence_text,
       n.t_min,
       n.t_max,
       n.record_lunar_date,
       n.epistemic_floor
  FROM dag_node n
 WHERE n.layer <> 'ENVIRONMENT';

-- 2. v_episode_source — episode ↔ 사료 기사 (episode_member → confirmed_fact → source_record)
--    한 episode는 원칙상 사료 1건에서만 나온다(Audit 1 over_merge). DISTINCT로 중복 행 제거.
CREATE OR REPLACE VIEW v_episode_source AS
SELECT DISTINCT
       em.episode_id,
       sr.source_record_id,
       sr.source_work,
       sr.record_lunar_date AS source_record_date,
       sr.source_title
  FROM episode_member em
  JOIN confirmed_fact cf ON cf.fact_id = em.fact_id
  JOIN source_record  sr ON sr.source_record_id = cf.source_record_id;

-- 3. v_fact_coverage — 확정 사실마다 몇 개 episode에 들어갔는가 (0이면 누락 = omission)
--    LEFT OUTER JOIN + COUNT(컬럼): 짝이 없는 fact도 0으로 남긴다.
CREATE OR REPLACE VIEW v_fact_coverage AS
SELECT cf.fact_id,
       cf.source_record_id,
       cf.confirmation_level,
       COUNT(em.episode_id)                         AS n_episodes,
       COUNT(em.clause)                             AS n_clause_memberships,
       LISTAGG(em.episode_id, ',') WITHIN GROUP (ORDER BY em.episode_id) AS episodes
  FROM confirmed_fact cf
  LEFT OUTER JOIN episode_member em ON em.fact_id = cf.fact_id
 GROUP BY cf.fact_id, cf.source_record_id, cf.confirmation_level;

-- 4. v_node_timeline — 시간 정렬용 값 (발생 시점과 기록 시점을 나란히)
--    sort_key: Python 화면(build_visualization.py)과 같은 규칙 = t_max, 없으면 t_min. 둘 다 없으면 NULL(임의 날짜 없음)
--    record_md: 기록일 'YYYY-MM-DD'를 같은 MMDD 정수로 바꾼 값(비교용)
CREATE OR REPLACE VIEW v_node_timeline AS
SELECT n.node_id,
       n.layer,
       n.title,
       n.t_min,
       n.t_max,
       NVL(n.t_max, n.t_min)                                         AS sort_key,
       n.occurrence_text,
       n.record_lunar_date,
       TO_NUMBER(SUBSTR(n.record_lunar_date, 6, 2)) * 100
         + TO_NUMBER(SUBSTR(n.record_lunar_date, 9, 2))              AS record_md,
       CASE
           WHEN n.t_min IS NULL AND n.t_max IS NULL THEN 'UNDATED'
           WHEN n.t_max IS NULL                     THEN 'OPEN_ENDED'
           WHEN n.t_min = n.t_max                   THEN 'POINT'
           ELSE 'RANGE'
       END                                                           AS time_shape
  FROM dag_node n;

-- 5. v_edge_detail — edge에 양 끝 node의 제목·layer·시간을 붙인 표 (자기 조인과 같은 원리: dag_node를 두 번 조인)
CREATE OR REPLACE VIEW v_edge_detail AS
SELECT e.edge_id,
       e.edge_type,
       e.status,
       e.claim_level,
       e.condition,
       e.src,
       s.title   AS src_title,
       s.layer   AS src_layer,
       s.t_min   AS src_t_min,
       s.t_max   AS src_t_max,
       e.dst,
       d.title   AS dst_title,
       d.layer   AS dst_layer,
       d.t_min   AS dst_t_min,
       d.t_max   AS dst_t_max,
       e.basis,
       e.supporting,
       e.uncertainty_status
  FROM dag_edge e
  JOIN dag_node s ON s.node_id = e.src
  JOIN dag_node d ON d.node_id = e.dst;

-- 6. v_identity_usage — 동일성 하나가 모델 어디에 쓰이는가 (edge condition / 후보 가정 / world)
--    스칼라 서브쿼리로 개수를 센다. identity_register.model_relevance 문자열과 비교해 볼 수 있다.
CREATE OR REPLACE VIEW v_identity_usage AS
SELECT ir.identity_id,
       ir.status,
       ir.surface_a,
       ir.surface_b,
       (SELECT COUNT(*) FROM edge_identity_condition c WHERE c.identity_id = ir.identity_id)      AS n_conditional_edges,
       (SELECT COUNT(*) FROM candidate_identity_condition c WHERE c.identity_id = ir.identity_id) AS n_candidate_conditions,
       (SELECT COUNT(*) FROM world_identity w
         WHERE w.identity_id = ir.identity_id AND w.identity_role = 'CONDITION')                   AS n_world_conditions,
       (SELECT COUNT(*) FROM identity_fact_ref r WHERE r.identity_id = ir.identity_id)            AS n_referenced_facts
  FROM identity_register ir;

-- 7. v_source_coverage — 사료 기사별 확정 사실·audit 명제·episode 수 (source coverage)
CREATE OR REPLACE VIEW v_source_coverage AS
SELECT sr.source_record_id,
       sr.source_work,
       sr.record_lunar_date,
       (SELECT COUNT(*) FROM confirmed_fact cf WHERE cf.source_record_id = sr.source_record_id)      AS n_confirmed_facts,
       (SELECT COUNT(*) FROM audit_proposition p WHERE p.source_record_id = sr.source_record_id)      AS n_audit_props,
       (SELECT COUNT(*) FROM v_episode_source es WHERE es.source_record_id = sr.source_record_id)     AS n_episodes
  FROM source_record sr;
