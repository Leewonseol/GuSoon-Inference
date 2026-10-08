-- =============================================================================
-- audit_views.sql — Audit SQL(05_audits)이 공통으로 쓰는 보조 view
-- -----------------------------------------------------------------------------
-- Python audits.py의 보조 함수에 해당하는 계산을 view로 둔다.
--   member_text()   → v_member_text.member_text   (절이 있으면 절, 없으면 문장 전체)
--   clause_family() → v_member_text.clause_family (MIXED 문장의 절은 주어로 ROYAL/OFFICIAL 판정)
--   testifier()     → v_member_text.testifier     (정규식 ^(\S+?)[은는]\s 의 1번 그룹)
--   parse_md()      → *_md 컬럼                   (1793-MM-DD → MM*100+DD)
--   joined          → v_episode_text.joined_text   (구성 원문을 member 순서대로 이은 것)
-- =============================================================================

-- 1. v_member_text — episode 구성원 한 줄 = (episode, fact) + 원문·인식 등급·주체
CREATE OR REPLACE VIEW v_member_text AS
SELECT em.episode_id,
       em.fact_id,
       em.member_seq,
       em.clause,
       NVL(em.clause, cf.confirmed_statement)                          AS member_text,
       cf.confirmation_level,
       rc.epistemic_rank,
       rc.epistemic_family                                             AS fact_family,
       CASE
           WHEN rc.epistemic_family = 'MIXED' AND em.clause LIKE '정조%'   THEN 'ROYAL'
           WHEN rc.epistemic_family = 'MIXED' AND em.clause LIKE '홍대협%' THEN 'OFFICIAL'
           ELSE rc.epistemic_family
       END                                                             AS clause_family,
       REGEXP_SUBSTR(NVL(em.clause, cf.confirmed_statement),
                     '^(\S+?)[은는]\s', 1, 1, NULL, 1)                AS testifier,
       cf.source_record_id,
       cf.fact_category,
       cf.chronology,
       cf.occurrence_lunar_text,
       cf.record_lunar_date,
       TO_NUMBER(REGEXP_SUBSTR(cf.occurrence_lunar_text, '1793-([0-9]{2})-([0-9]{2})', 1, 1, NULL, 1)) * 100
         + TO_NUMBER(REGEXP_SUBSTR(cf.occurrence_lunar_text, '1793-([0-9]{2})-([0-9]{2})', 1, 1, NULL, 2))
                                                                       AS occurrence_md,
       TO_NUMBER(REGEXP_SUBSTR(cf.record_lunar_date, '1793-([0-9]{2})-([0-9]{2})', 1, 1, NULL, 1)) * 100
         + TO_NUMBER(REGEXP_SUBSTR(cf.record_lunar_date, '1793-([0-9]{2})-([0-9]{2})', 1, 1, NULL, 2))
                                                                       AS record_md
  FROM episode_member em
  JOIN confirmed_fact cf         ON cf.fact_id = em.fact_id
  JOIN ref_confirmation_level rc ON rc.confirmation_level = cf.confirmation_level;

-- 2. v_episode_text — episode 단위 집계: 원문 합본, 진술 member 수, 인식 하한(floor) 등
CREATE OR REPLACE VIEW v_episode_text AS
SELECT n.node_id                                                         AS episode_id,
       n.layer,
       n.summary,
       n.caution,
       n.t_min,
       n.t_max,
       LISTAGG(m.member_text, ' ') WITHIN GROUP (ORDER BY m.member_seq)   AS joined_text,
       LISTAGG(m.chronology || ' ' || m.occurrence_lunar_text, ' ')
           WITHIN GROUP (ORDER BY m.member_seq)                           AS chron_text,
       COUNT(m.fact_id)                                                   AS n_members,
       COUNT(CASE WHEN m.fact_family = 'TESTIMONY' THEN 1 END)           AS n_testimony_members,
       MIN(m.epistemic_rank)                                              AS floor_rank,
       COUNT(DISTINCT m.source_record_id)                                 AS n_sources,
       COUNT(DISTINCT m.clause_family)                                    AS n_families
  FROM dag_node n
  LEFT JOIN v_member_text m ON m.episode_id = n.node_id
 WHERE n.layer <> 'ENVIRONMENT'
 GROUP BY n.node_id, n.layer, n.summary, n.caution, n.t_min, n.t_max;

-- 3. v_candidate_level — 후보 등급을 숫자로 (stage4_latent.py SCORE / EVIDENCE_SCORE)
--    DECODE는 Oracle 전용 CASE 축약형이다(SQLD 단골).
CREATE OR REPLACE VIEW v_candidate_level AS
SELECT c.candidate_id,
       c.gap_id,
       c.overall,
       c.source_support,
       DECODE(c.source_support, 'HIGH', 3, 'MEDIUM', 2, 'LOW', 1, 'NONE', 0)            AS support_level,
       DECODE(c.overall, 'HIGH', 3, 'MEDIUM', 2, 'LOW', 1, 'INCOMPATIBLE', 0)           AS overall_level,
       c.bridge_directly_attested,
       c.plausibility_grade,
       c.contradiction_risk,
       c.support_basis,
       c.n_assumptions
  FROM latent_candidate c;

-- 4. v_candidate_endpoint — 후보의 LATENT edge가 닿는 관측 node(= endpoint)
--    endpoint = latent edge의 src/dst 중 같은 후보의 latent node id(LN_…)가 아닌 것
CREATE OR REPLACE VIEW v_candidate_endpoint AS
--    UNION(중복 제거)으로 src와 dst를 한 컬럼에 모은 뒤 NOT EXISTS로 latent node를 뺀다
SELECT ends.candidate_id, ends.node_id
  FROM (SELECT candidate_id, src AS node_id FROM latent_element WHERE kind = 'edge'
        UNION
        SELECT candidate_id, dst FROM latent_element WHERE kind = 'edge') ends
 WHERE NOT EXISTS (SELECT 1
                     FROM latent_element ln
                    WHERE ln.candidate_id = ends.candidate_id
                      AND ln.kind = 'node'
                      AND ln.element_id = ends.node_id);

-- 5. v_candidate_usable — 분석에 쓰는 후보 (stage6_mechanisms.py usable())
--    INCOMPATIBLE·대조용(contradiction_risk HIGH)·null 변형 후보를 뺀다
CREATE OR REPLACE VIEW v_candidate_usable AS
SELECT c.candidate_id, c.gap_id, cm.mechanism_id AS primary_mechanism
  FROM latent_candidate c
  JOIN candidate_mechanism cm
    ON cm.candidate_id = c.candidate_id
   AND cm.mapping_role = 'PRIMARY'
 WHERE c.overall <> 'INCOMPATIBLE'
   AND c.contradiction_risk <> 'HIGH'
   AND c.candidate_id NOT IN (SELECT member_id FROM rule_set_member WHERE rule_set = 'NULL_VARIANT');

-- 6. v_python_audit_summary — Python Audit 결과의 audit × severity 개수(비교 기준)
CREATE OR REPLACE VIEW v_python_audit_summary AS
SELECT audit_name,
       COUNT(CASE WHEN severity = 'ERROR'      THEN 1 END) AS n_error,
       COUNT(CASE WHEN severity = 'WARN'       THEN 1 END) AS n_warn,
       COUNT(CASE WHEN severity = 'UNRESOLVED' THEN 1 END) AS n_unresolved,
       COUNT(CASE WHEN severity = 'INFO'       THEN 1 END) AS n_info
  FROM py_audit_finding
 GROUP BY audit_name;
