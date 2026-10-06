"""구순–김명신 사건 clean 재구성 파이프라인.

STAGE 1 → AUDIT 1 → STAGE 2 → AUDIT 2 → STAGE 3(동결) → STAGE 4 → AUDIT 3 → STAGE 5 → AUDIT 3(world 포함)
각 audit에 ERROR가 하나라도 있으면 다음 stage로 넘어가지 않고 종료한다(exit 1).

실행: python3 scripts/gusun_clean/build.py   (저장소 루트에서)
SMC / MCMC / particle filtering / posterior sampling / 전수 조합은 사용하지 않는다.
"""
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import audits  # noqa: E402
import report  # noqa: E402
import regression  # noqa: E402
from manual_review import WARN_DISPOSITIONS  # noqa: E402
from stage1_episodes import EPISODES, EPISTEMIC_RANK, IDENTITY_REGISTER  # noqa: E402
from stage2_graph import BASES, EDGE_TYPES, EDGES, ENV_FIT_LINKS, ENV_NODES, FEATURE_LINKS  # noqa: E402

ROOT = HERE.parents[1]
PACK = ROOT / "gusun_clean_restart_csv_pack"
OUT = ROOT / "output" / "clean"
DB = ROOT / "database" / "gusun_clean.duckdb"


def read_csv(name):
    with open(PACK / name, encoding="utf-8-sig", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(path, rows, cols):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})


def apply_dispositions(stage, findings):
    """WARN은 manual_review.WARN_DISPOSITIONS의 명시적 처리 없이는 통과하지 못한다.
    RECLASSIFIED_INFO → INFO, UNRESOLVED → UNRESOLVED, ESCALATED_ERROR → ERROR. FIXED는 이력이며 현재 WARN을 지우지 않는다."""
    table = {(d["audit_stage"], d["warning_type"], d["affected_item"]): d for d in WARN_DISPOSITIONS}
    sev = {"RECLASSIFIED_INFO": "INFO", "UNRESOLVED": "UNRESOLVED", "ESCALATED_ERROR": "ERROR"}
    for f in findings:
        if f["severity"] != "WARN":
            continue
        d = table.get((stage, f["check"], f["target"]))
        if d and d["disposition"] in sev:
            f["severity"] = sev[d["disposition"]]
            f["message"] += f" [disposition {d['warning_id']}: {d['disposition']}]"
    return findings


def gate(name, findings):
    c = Counter(f["severity"] for f in findings)
    print(f"[{name}] ERROR={c['ERROR']} WARN={c['WARN']} INFO={c['INFO']} UNRESOLVED={c['UNRESOLVED']}")
    if c["ERROR"] or c["WARN"]:
        for f in findings:
            if f["severity"] in ("ERROR", "WARN"):
                print("  ", f["severity"], f["check"], f["target"], f["message"])
        print(f"[{name}] 실패 — ERROR·WARN이 0이 아니므로 다음 stage로 진행하지 않음")
        sys.exit(1)


# --------------------------------------------------------------------------- STAGE 1
def stage1(cf):
    cf_by = {r["fact_id"]: r for r in cf}
    rows = []
    for ep in EPISODES:
        ms = [(cf_by[f], c) for f, c in ep["members"]]
        floor = min(ms, key=lambda m: EPISTEMIC_RANK[m[0]["confirmation_level"]])[0]["confirmation_level"]
        rows.append(dict(
            node_id=ep["episode_id"], episode_id=ep["episode_id"], node_status="OBSERVED", layer=ep["layer"],
            branch=ep["branch"], title=ep["title"], summary=ep["summary"], caution=ep["caution"],
            member_fact_ids="|".join(f for f, _ in ep["members"]),
            member_clauses="|".join(f"{f}:{c}" for f, c in ep["members"] if c),
            confirmation_levels="|".join(dict.fromkeys(m[0]["confirmation_level"] for m in ms)),
            epistemic_floor=floor,
            claim_status="|".join(dict.fromkeys(m[0]["underlying_claim_status"] for m in ms)),
            source_record_ids="|".join(dict.fromkeys(m[0]["source_record_id"] for m in ms)),
            source_prop_ids="|".join(dict.fromkeys(p for m in ms for p in m[0]["source_prop_ids"].split("|"))),
            attesting_actor=ep["attesting_actor"], occurrence_text=ep["occurrence_text"],
            t_min=ep["t_min"], t_max=ep["t_max"],
            record_lunar_date="|".join(dict.fromkeys(m[0]["record_lunar_date"] for m in ms)),
            grouping_rationale=ep["grouping_rationale"]))
    return rows


# --------------------------------------------------------------------------- STAGE 2
def stage2(ep_rows, env):
    env_by = {r["env_id"]: r for r in env}
    nodes = list(ep_rows)
    for n in ENV_NODES:
        r = env_by[n["env_id"]]
        nodes.append(dict(node_id=n["node_id"], env_id=n["env_id"], node_status="OBSERVED", layer="ENVIRONMENT",
                          branch="ENVIRONMENT", title=n["title"], summary=r["attested_context"], caution=r["notes"],
                          member_fact_ids="", source_record_ids="", source_prop_ids="", attesting_actor="03_environment_1793",
                          occurrence_text=r["lunar_date"], t_min=n["t_min"], t_max=n["t_max"],
                          record_lunar_date=r["lunar_date"], epistemic_floor="EXTERNAL_CONTEXT",
                          confirmation_levels="EXTERNAL_CONTEXT", grouping_rationale="환경 context node (사건 아님)"))
    edges = [dict(e) for e in EDGES]
    links = []
    for i, l in enumerate(FEATURE_LINKS + ENV_FIT_LINKS, 1):
        layer = "ENVIRONMENT" if l["feature_id"].startswith("E") else "INSTITUTIONAL"
        kind = "EDGE" if l["target_id"].startswith("OE") else "NODE"
        links.append(dict(link_id=f"FL{i:03d}", target_kind=kind, feature_layer=layer, creates_event="NO", **l))
    return nodes, edges, links


PREVIOUS_FREEZE = dict(sha256="86a529da3baff8f3", structure_sha256="7b4d97185d70baa95a2efdb55492b854a0d39dcf26411b70a1bf830f0b79a1b3")  # WARN 처리 이전(커밋 712d536) 동결 해시 앞자리


def structure_hash(nodes, edges):
    """문구(summary)를 뺀 구조 해시: node 구성·층·시간, edge 전체. 문구 수정과 구조 변경을 구분하기 위함."""
    keys_n = ["node_id", "node_status", "layer", "member_fact_ids", "t_min", "t_max"]
    keys_e = ["edge_id", "src", "dst", "edge_type", "basis", "status", "supporting", "condition", "claim_level"]
    payload = json.dumps([[{k: n.get(k) for k in keys_n} for n in nodes],
                          [{k: e.get(k) for k in keys_e} for e in edges]], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def graph_hash(nodes, edges):
    keys_n = ["node_id", "node_status", "layer", "summary", "member_fact_ids", "t_min", "t_max"]
    keys_e = ["edge_id", "src", "dst", "edge_type", "basis", "status", "supporting", "condition", "claim_level"]
    payload = json.dumps([[{k: n.get(k) for k in keys_n} for n in nodes],
                          [{k: e.get(k) for k in keys_e} for e in edges]], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


NODE_COLS = ["node_id", "node_status", "layer", "branch", "title", "summary", "caution", "member_fact_ids",
             "member_clauses", "confirmation_levels", "epistemic_floor", "claim_status", "source_record_ids",
             "source_prop_ids", "attesting_actor", "occurrence_text", "t_min", "t_max", "record_lunar_date",
             "grouping_rationale", "env_id"]
EDGE_COLS = ["edge_id", "src", "dst", "edge_type", "basis", "status", "claim_level", "condition", "supporting",
             "rationale", "caution"]
LINK_COLS = ["link_id", "target_kind", "target_id", "feature_layer", "feature_id", "dimension", "assessment",
             "creates_event", "rationale"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    DB.parent.mkdir(parents=True, exist_ok=True)
    manifest = read_csv("00_INPUT_MANIFEST.csv")
    cf = read_csv("01_confirmed_facts.csv")
    inst = read_csv("02_institutional_normative_features.csv")
    env = read_csv("03_environment_1793.csv")
    src = read_csv("04_source_records.csv")
    props = read_csv("05_source_faithful_propositions_AUDIT_ONLY.csv")
    print(f"input rows: manifest={len(manifest)} cf={len(cf)} inst={len(inst)} env={len(env)} src={len(src)} props={len(props)}")

    # STAGE 1 + AUDIT 1
    ep_rows = stage1(cf)
    regression.run_or_exit()
    a1, outside = audits.audit1(EPISODES, cf, props, src)
    apply_dispositions("AUDIT1", a1)
    report.write_audit1(OUT / "audit_1_episode_fidelity.md", a1, outside, ep_rows, cf)
    gate("AUDIT 1", a1)

    # STAGE 2 + AUDIT 2
    nodes, edges, links = stage2(ep_rows, env)
    a2 = audits.audit2(nodes, edges, EPISODES, links, env, EDGE_TYPES, BASES)
    apply_dispositions("AUDIT2", a2)
    report.write_audit2(OUT / "audit_2_graph_fidelity.md", a2, nodes, edges, links)
    gate("AUDIT 2", a2)

    # STAGE 3 — 동결
    write_csv(OUT / "episode_nodes.csv", nodes, NODE_COLS)
    write_csv(OUT / "observed_edges.csv", edges, EDGE_COLS)
    write_csv(OUT / "node_feature_links.csv", links, LINK_COLS)
    write_csv(OUT / "identity_register.csv", IDENTITY_REGISTER,
              ["identity_id", "surface_a", "surface_b", "status", "unresolved_reason", "context", "referenced_facts"])
    frozen = graph_hash(nodes, edges)
    freeze = dict(name="Validated Observed Partial DAG", sha256=frozen, structure_sha256=structure_hash(nodes, edges),
                  previous_sha256_prefix=PREVIOUS_FREEZE["sha256"],
                  previous_structure_sha256=PREVIOUS_FREEZE["structure_sha256"],
                  structure_unchanged=structure_hash(nodes, edges) == PREVIOUS_FREEZE["structure_sha256"],
                  change_note="WARN 처리(A1-W1–W4, A1-E1)로 EP01·EP04·EP05·EP06·EP07 summary 문구만 바뀜. node·edge 구조는 그대로",
                  n_nodes=len(nodes), n_edges=len(edges),
                  n_episode_nodes=len(ep_rows), n_env_nodes=len(ENV_NODES),
                  edge_status=dict(Counter(e["status"] for e in edges)),
                  edge_types=dict(Counter(e["edge_type"] for e in edges)), latent_count=0)
    (OUT / "observed_dag_freeze.json").write_text(json.dumps(freeze, ensure_ascii=False, indent=2))
    report.write_mermaid(OUT / "observed_dag.md", nodes, edges)
    print(f"[STAGE 3] frozen {frozen[:16]} nodes={len(nodes)} edges={len(edges)}")

    # STAGE 4 + AUDIT 3
    import stage4_latent
    gaps, cands = stage4_latent.build(nodes, edges)
    a3 = audits.audit3(nodes, edges, frozen, graph_hash(nodes, edges), gaps, cands, props)
    apply_dispositions("AUDIT3", a3)
    gate("AUDIT 3 (latent)", a3)

    # STAGE 5 + AUDIT 3 재검사(world 포함)
    import stage5_worlds
    worlds = stage5_worlds.build(nodes, edges, gaps, cands)
    a3w = audits.audit3(nodes, edges, frozen, graph_hash(nodes, edges), gaps, cands, props, worlds)
    apply_dispositions("AUDIT3", a3w)
    report.write_audit3(OUT / "audit_3_observed_latent_separation.md", a3w, nodes, edges, gaps, cands, worlds, frozen)
    gate("AUDIT 3 (worlds)", a3w)
    report.write_gaps(OUT / "gap_candidates.md", gaps, cands, nodes)
    report.write_worlds(OUT / "narrative_worlds.md", worlds, cands, gaps, nodes)
    report.write_latent_csv(OUT, gaps, cands, worlds)
    report.write_validation_summary(OUT / "validation_summary.md",
                                    {"Audit 1": a1, "Audit 2": a2, "Audit 3": a3w}, freeze, worlds)
    write_csv(OUT / "warn_dispositions.csv", WARN_DISPOSITIONS, report.DISPOSITION_COLS)

    # canonical DB
    import duckdb
    if DB.exists():
        DB.unlink()
    con = duckdb.connect(str(DB))
    for name, f in [("raw_manifest", "00_INPUT_MANIFEST.csv"), ("raw_confirmed_facts", "01_confirmed_facts.csv"),
                    ("raw_institutional_features", "02_institutional_normative_features.csv"),
                    ("raw_environment_1793", "03_environment_1793.csv"), ("raw_source_records", "04_source_records.csv"),
                    ("raw_audit_propositions", "05_source_faithful_propositions_AUDIT_ONLY.csv")]:
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_csv_auto(?, header=true, all_varchar=true)",
                    [str(PACK / f)])
    for name, f in [("episode_nodes", "episode_nodes.csv"), ("observed_edges", "observed_edges.csv"),
                    ("node_feature_links", "node_feature_links.csv"), ("identity_register", "identity_register.csv"),
                    ("gaps", "gaps.csv"), ("latent_candidates", "latent_candidates.csv"),
                    ("latent_elements", "latent_elements.csv"), ("narrative_worlds", "narrative_worlds.csv"),
                    ("warn_dispositions", "warn_dispositions.csv")]:
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_csv_auto(?, header=true, all_varchar=true)",
                    [str(OUT / f)])
    con.execute("CREATE TABLE episode_members (episode_id VARCHAR, fact_id VARCHAR, clause VARCHAR)")
    con.executemany("INSERT INTO episode_members VALUES (?,?,?)",
                    [(e["episode_id"], f, c) for e in EPISODES for f, c in e["members"]])
    con.execute("CREATE TABLE dag_freeze (name VARCHAR, sha256 VARCHAR, n_nodes INT, n_edges INT, latent_count INT)")
    con.execute("INSERT INTO dag_freeze VALUES (?,?,?,?,?)",
                [freeze["name"], frozen, len(nodes), len(edges), 0])
    con.execute("CREATE TABLE audit_findings (audit VARCHAR, check_name VARCHAR, severity VARCHAR, target VARCHAR, message VARCHAR)")
    con.executemany("INSERT INTO audit_findings VALUES (?,?,?,?,?)",
                    [(a, f["check"], f["severity"], f["target"], f["message"])
                     for a, fs in [("AUDIT1", a1), ("AUDIT2", a2), ("AUDIT3", a3w)] for f in fs])
    con.close()
    print(f"[DB] {DB.relative_to(ROOT)} 작성 완료")


if __name__ == "__main__":
    main()
