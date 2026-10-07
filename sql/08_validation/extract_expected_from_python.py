"""Python 산출물에서 기대값을 읽어 sql/08_validation/expected_counts.sql을 만든다.

기대값의 출처는 모두 Python 파이프라인이 이미 쓴 산출물이다(읽기만 한다).
  output/clean/*.csv, output/clean/observed_dag_freeze.json, database/gusun_clean.duckdb(audit_findings)
값을 손으로 적지 않는다. 다시 실행하면 같은 파일이 나온다(결정적).

실행: python3 sql/08_validation/extract_expected_from_python.py   (저장소 루트, duckdb 모듈 필요)
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "clean"
PACK = ROOT / "gusun_clean_restart_csv_pack"
DB = ROOT / "database" / "gusun_clean.duckdb"
TARGET = ROOT / "sql" / "08_validation" / "expected_counts.sql"


def rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    import duckdb
    nodes = rows(OUT / "episode_nodes.csv")
    edges = rows(OUT / "observed_edges.csv")
    sd_nodes = rows(OUT / "mechanism_super_dag_nodes.csv")
    sd_edges = rows(OUT / "mechanism_super_dag_edges.csv")
    worlds = rows(OUT / "narrative_worlds.csv")
    cands = rows(OUT / "latent_candidates.csv")
    ident = rows(OUT / "identity_register.csv")
    gaps = rows(OUT / "gaps.csv")
    mechs = rows(OUT / "mechanism_definitions.csv")
    freeze = json.loads((OUT / "observed_dag_freeze.json").read_text(encoding="utf-8"))
    con = duckdb.connect(str(DB), read_only=True)
    findings = con.execute("SELECT audit, check_name, severity FROM audit_findings").fetchall()
    con.close()
    fcount = Counter((a, s) for a, _, s in findings)
    ccount = Counter(c for _, c, s in findings if s == "ERROR")

    forbidden_src, forbidden_dst = {"EP01", "EP08", "EP10", "EP29"}, {"EP13", "EP26", "EP27"}  # audits.py FORBIDDEN_DIRECT
    dup = Counter((e["src"], e["dst"], e["edge_type"]) for e in edges)
    m = []  # (metric_id, value, source, description)

    def add(mid, val, src, desc):
        m.append((mid, int(val), src, desc))

    add("canonical_node_count", len(nodes), "output/clean/episode_nodes.csv", "동결 observed node 수")
    add("canonical_edge_count", len(edges), "output/clean/observed_edges.csv", "동결 observed edge 수")
    add("freeze_n_nodes", freeze["n_nodes"], "output/clean/observed_dag_freeze.json", "동결 기록의 node 수")
    add("freeze_n_edges", freeze["n_edges"], "output/clean/observed_dag_freeze.json", "동결 기록의 edge 수")
    add("episode_count", sum(n["layer"] != "ENVIRONMENT" for n in nodes), "output/clean/episode_nodes.csv", "episode node 수(EP)")
    add("env_context_node_count", sum(n["layer"] == "ENVIRONMENT" for n in nodes), "output/clean/episode_nodes.csv", "환경 context node 수(ENV)")
    for st, n in sorted(Counter(n["node_status"] for n in nodes).items()):
        add(f"node_status_{st}", n, "output/clean/episode_nodes.csv", f"동결 node status={st}")
    for st, n in sorted(Counter(e["status"] for e in edges).items()):
        add(f"edge_status_{st}", n, "output/clean/observed_edges.csv", f"동결 edge status={st}")
    for st, n in sorted(Counter(n["sd_status"] for n in sd_nodes).items()):
        add(f"sd_node_status_{st}", n, "output/clean/mechanism_super_dag_nodes.csv", f"Super-DAG node status={st}")
    for st, n in sorted(Counter(e["sd_status"] for e in sd_edges).items()):
        add(f"sd_edge_status_{st}", n, "output/clean/mechanism_super_dag_edges.csv", f"Super-DAG edge status={st}")
    add("source_count", len(rows(PACK / "04_source_records.csv")), "gusun_clean_restart_csv_pack/04_source_records.csv", "사료 기사 수")
    add("confirmed_fact_count", len(rows(PACK / "01_confirmed_facts.csv")), "gusun_clean_restart_csv_pack/01_confirmed_facts.csv", "확정 사실 수")
    add("audit_proposition_count", len(rows(PACK / "05_source_faithful_propositions_AUDIT_ONLY.csv")),
        "gusun_clean_restart_csv_pack/05_…AUDIT_ONLY.csv", "audit 전용 명제 수")
    add("world_count", len(worlds), "output/clean/narrative_worlds.csv", "world 수")
    add("world_competing_count", sum(w["status"] == "COMPETING_EXPLANATION" for w in worlds), "output/clean/narrative_worlds.csv", "경쟁 설명 world 수")
    add("world_rejected_count", sum(w["status"] == "REJECTED" for w in worlds), "output/clean/narrative_worlds.csv", "배제된 world 수")
    add("world_bridge_total", sum(len(w["latent_bridges"].split("|")) for w in worlds), "output/clean/narrative_worlds.csv", "world bridge 합계")
    add("candidate_count", len(cands), "output/clean/latent_candidates.csv", "LATENT 후보 수")
    add("candidate_status_LATENT", sum(c["status"] == "LATENT" for c in cands), "output/clean/latent_candidates.csv", "status=LATENT 후보 수")
    add("candidate_overall_HIGH", sum(c["overall"] == "HIGH" for c in cands), "output/clean/latent_candidates.csv", "final HIGH 후보 수(재감사 후 0)")
    add("gap_count", len(gaps), "output/clean/gaps.csv", "gap 수")
    add("mechanism_count", len(mechs), "output/clean/mechanism_definitions.csv", "메커니즘 수")
    add("identity_unresolved_count", sum(i["status"] == "UNRESOLVED" for i in ident), "output/clean/identity_register.csv", "UNRESOLVED 동일성 수")
    add("identity_resolved_count", sum(i["status"] == "RESOLVED" for i in ident), "output/clean/identity_register.csv", "사용자 확정 동일성 수")
    add("gap_open_unresolved_count", sum(g["gap_status"] == "OPEN_UNRESOLVED" for g in gaps), "output/clean/gaps.csv", "OPEN_UNRESOLVED gap 수")
    add("edge_uncertainty_count", sum(bool(e["uncertainty_status"]) for e in edges), "output/clean/observed_edges.csv", "uncertainty_status가 있는 edge 수")
    add("duplicate_edge_count", sum(1 for k, v in dup.items() if v > 1), "output/clean/observed_edges.csv", "(src,dst,type) 중복 묶음 수")
    add("self_loop_count", sum(e["src"] == e["dst"] for e in edges), "output/clean/observed_edges.csv", "self-loop edge 수")
    add("cycle_count", ccount["acyclicity"], "database/gusun_clean.duckdb audit_findings", "Python Audit 2 acyclicity ERROR 수")
    add("unsupported_derived_edge_count", sum(e["status"] == "DERIVED" and not e["supporting"] for e in edges),
        "output/clean/observed_edges.csv", "근거(supporting) 없는 DERIVED edge 수")
    add("causes_edge_count", sum(e["edge_type"] == "CAUSES" for e in edges), "output/clean/observed_edges.csv", "CAUSES edge 수")
    add("direct_causal_death_edge_count",
        sum(e["src"] in forbidden_src and e["dst"] in forbidden_dst for e in edges),
        "output/clean/observed_edges.csv + audits.py FORBIDDEN_DIRECT", "구순 관련 node → 사망·사인 node 직접 edge 수")
    for (a, s), n in sorted(fcount.items()):
        add(f"py_{a.lower()}_{s.lower()}", n, "database/gusun_clean.duckdb audit_findings", f"Python {a} {s} finding 수")
    for a in ["AUDIT1", "AUDIT2", "AUDIT3", "AUDIT4", "AUDIT5"]:
        for s in ["ERROR", "WARN"]:
            if (a, s) not in fcount:
                add(f"py_{a.lower()}_{s.lower()}", 0, "database/gusun_clean.duckdb audit_findings", f"Python {a} {s} finding 수")

    lines = [HEADER.format(sha=freeze["sha256"])]
    lines.append("DELETE FROM expected_count;\n")
    for mid, val, src, desc in sorted(m):
        lines.append(f"INSERT INTO expected_count (metric_id, expected_value, python_source, description)\n"
                     f"VALUES ('{mid}', {val}, '{src}', '{desc}');")
    lines.append("COMMIT;\n")
    lines.append(ACTUAL)
    TARGET.write_text("\n".join(lines), encoding="utf-8")
    for mid, val, _, _ in sorted(m):
        print(f"{mid:<40} {val}")


HEADER = """-- =============================================================================
-- expected_counts.sql — Python 산출물에서 읽은 기대값 + Oracle에서 독립 계산한 실제값 비교
-- -----------------------------------------------------------------------------
-- 1부(INSERT)는 sql/08_validation/extract_expected_from_python.py가 Python 산출물을 읽어 생성했다.
--   값을 손으로 적지 않았다. 동결 해시(참고): {sha}
-- 2부(비교 질의)는 Oracle canonical 표에서 같은 지표를 다시 센다(Python 결과를 참조하지 않음).
-- 선행: 01_schema, 02_load, 03_views, 05_audits (py_* 지표 비교에는 v_sql_audit_all이 필요)
-- 정상: 마지막 질의의 comparison 컬럼이 모두 MATCH (py_audit5_*는 NOT PORTED)
-- =============================================================================
"""

ACTUAL = """-- =============================================================================
-- 2부. Oracle 실제값 (canonical 표에서 독립 계산)
-- =============================================================================
CREATE OR REPLACE VIEW v_oracle_actual_count AS
SELECT 'canonical_node_count' AS metric_id, COUNT(*) AS actual_value FROM dag_node
UNION ALL SELECT 'canonical_edge_count',   COUNT(*) FROM dag_edge
UNION ALL SELECT 'freeze_n_nodes',         MAX(n_nodes) FROM dag_freeze
UNION ALL SELECT 'freeze_n_edges',         MAX(n_edges) FROM dag_freeze
UNION ALL SELECT 'episode_count',          COUNT(*) FROM dag_node WHERE layer <> 'ENVIRONMENT'
UNION ALL SELECT 'env_context_node_count', COUNT(*) FROM dag_node WHERE layer = 'ENVIRONMENT'
UNION ALL SELECT 'node_status_' || node_status, COUNT(*) FROM dag_node GROUP BY node_status
UNION ALL SELECT 'edge_status_' || status, COUNT(*) FROM dag_edge GROUP BY status
UNION ALL SELECT 'sd_node_status_' || sd_status, COUNT(*) FROM sd_node GROUP BY sd_status
UNION ALL SELECT 'sd_edge_status_' || sd_status, COUNT(*) FROM sd_edge GROUP BY sd_status
UNION ALL SELECT 'source_count',            COUNT(*) FROM source_record
UNION ALL SELECT 'confirmed_fact_count',    COUNT(*) FROM confirmed_fact
UNION ALL SELECT 'audit_proposition_count', COUNT(*) FROM audit_proposition
UNION ALL SELECT 'world_count',             COUNT(*) FROM narrative_world
UNION ALL SELECT 'world_competing_count',   COUNT(*) FROM narrative_world WHERE status = 'COMPETING_EXPLANATION'
UNION ALL SELECT 'world_rejected_count',    COUNT(*) FROM narrative_world WHERE status = 'REJECTED'
UNION ALL SELECT 'world_bridge_total',      COUNT(*) FROM world_candidate
UNION ALL SELECT 'candidate_count',         COUNT(*) FROM latent_candidate
UNION ALL SELECT 'candidate_status_LATENT', COUNT(*) FROM latent_candidate WHERE status = 'LATENT'
UNION ALL SELECT 'candidate_overall_HIGH',  COUNT(*) FROM latent_candidate WHERE overall = 'HIGH'
UNION ALL SELECT 'gap_count',               COUNT(*) FROM gap
UNION ALL SELECT 'mechanism_count',         COUNT(*) FROM mechanism
UNION ALL SELECT 'identity_unresolved_count', COUNT(*) FROM identity_register WHERE status = 'UNRESOLVED'
UNION ALL SELECT 'identity_resolved_count',   COUNT(*) FROM identity_register WHERE status = 'RESOLVED'
UNION ALL SELECT 'gap_open_unresolved_count', COUNT(*) FROM gap WHERE gap_status = 'OPEN_UNRESOLVED'
UNION ALL SELECT 'edge_uncertainty_count',    COUNT(uncertainty_status) FROM dag_edge
UNION ALL SELECT 'duplicate_edge_count',      COUNT(*)
            FROM (SELECT src, dst, edge_type FROM dag_edge GROUP BY src, dst, edge_type HAVING COUNT(*) > 1)
UNION ALL SELECT 'self_loop_count',           COUNT(*) FROM dag_edge WHERE src = dst
UNION ALL SELECT 'cycle_count',               COUNT(*)
            FROM (SELECT 1 FROM dag_edge WHERE CONNECT_BY_ISCYCLE = 1 CONNECT BY NOCYCLE PRIOR dst = src)
UNION ALL SELECT 'unsupported_derived_edge_count', COUNT(*)
            FROM dag_edge e
           WHERE e.status = 'DERIVED'
             AND NOT EXISTS (SELECT 1 FROM edge_source_basis b WHERE b.edge_id = e.edge_id)
UNION ALL SELECT 'causes_edge_count',         COUNT(*) FROM dag_edge WHERE edge_type = 'CAUSES'
UNION ALL SELECT 'direct_causal_death_edge_count', COUNT(*)
            FROM dag_edge e
            JOIN rule_set_member s ON s.rule_set = 'FORBIDDEN_DIRECT_SRC' AND s.member_id = e.src
            JOIN rule_set_member d ON d.rule_set = 'FORBIDDEN_DIRECT_DST' AND d.member_id = e.dst
UNION ALL SELECT 'py_' || LOWER(audit_name) || '_' || LOWER(severity), COUNT(*)
            FROM v_sql_audit_all GROUP BY audit_name, severity;

-- 비교 — FULL OUTER JOIN: 기대값만 있는 지표(SQL이 0건이라 행이 없는 py_*_error 등)도 남긴다
SELECT COALESCE(x.metric_id, a.metric_id)              AS metric_id,
       x.expected_value,
       NVL(a.actual_value, 0)                           AS oracle_value,
       CASE WHEN COALESCE(x.metric_id, a.metric_id) LIKE 'py\\_audit5\\_%' ESCAPE '\\' THEN 'NOT PORTED'
            WHEN x.metric_id IS NULL                                            THEN 'ORACLE_ONLY'
            WHEN x.expected_value = NVL(a.actual_value, 0)                      THEN 'MATCH'
            ELSE 'DIFF' END                             AS comparison,
       x.python_source
  FROM expected_count x
  FULL OUTER JOIN v_oracle_actual_count a ON a.metric_id = x.metric_id
 ORDER BY CASE WHEN COALESCE(x.metric_id, a.metric_id) LIKE 'py\\_%' ESCAPE '\\' THEN 2 ELSE 1 END,
          1;

-- 요약 — 기대: DIFF 0
SELECT comparison, COUNT(*) AS n_metrics
  FROM (SELECT CASE WHEN COALESCE(x.metric_id, a.metric_id) LIKE 'py\\_audit5\\_%' ESCAPE '\\' THEN 'NOT PORTED'
                    WHEN x.metric_id IS NULL                                            THEN 'ORACLE_ONLY'
                    WHEN x.expected_value = NVL(a.actual_value, 0)                      THEN 'MATCH'
                    ELSE 'DIFF' END AS comparison
          FROM expected_count x
          FULL OUTER JOIN v_oracle_actual_count a ON a.metric_id = x.metric_id)
 GROUP BY comparison
 ORDER BY comparison;
"""

if __name__ == "__main__":
    main()
