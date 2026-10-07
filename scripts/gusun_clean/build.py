"""구순–김명신 사건 clean 재구성 파이프라인.

STAGE 1 → AUDIT 1 → STAGE 2 → AUDIT 2 → STAGE 3(동결) → STAGE 4 → AUDIT 3 → STAGE 5 → AUDIT 3(world 포함)
→ STAGE 6(mechanism Super-DAG, 질적 SCM) → AUDIT 4 → STAGE 7(interactive temporal DAG 데이터, docs/data) → AUDIT 5
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
from stage2_graph import BASES, EDGE_TYPES, EDGE_UNCERTAINTY, EDGES, ENV_FIT_LINKS, ENV_NODES, FEATURE_LINKS  # noqa: E402

ROOT = HERE.parents[1]
PACK = ROOT / "gusun_clean_restart_csv_pack"
OUT = ROOT / "output" / "clean"
DB = ROOT / "database" / "gusun_clean.duckdb"
DOCS = ROOT / "docs"


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
            grouping_rationale=ep["grouping_rationale"],
            identity_links=identity_links(ep)))
    return rows


def identity_links(ep):
    """episode 구성 fact가 동일성 대장의 referenced_facts에 있으면 그 ID와 상태를 적는다(summary는 원문 표면형 유지)."""
    fids = {f for f, _ in ep["members"]}
    out = []
    for i in IDENTITY_REGISTER:
        if i["status"] in ("RESOLVED", "UNRESOLVED") and fids & set(filter(None, i["referenced_facts"].split("|"))):
            out.append(f"{i['identity_id']}:{i['status']}")
    return "|".join(out)


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
    for e in edges:
        st, note = EDGE_UNCERTAINTY.get(e["edge_id"], ("", ""))
        e["uncertainty_status"], e["review_decision"] = st, note
    links = []
    for i, l in enumerate(FEATURE_LINKS + ENV_FIT_LINKS, 1):
        layer = "ENVIRONMENT" if l["feature_id"].startswith("E") else "INSTITUTIONAL"
        kind = "EDGE" if l["target_id"].startswith("OE") else "NODE"
        links.append(dict(link_id=f"FL{i:03d}", target_kind=kind, feature_layer=layer, creates_event="NO", **l))
    return nodes, edges, links


# 직전 동결본(커밋 1f7710c: WARN 처리 후, 사용자 동일성 확정 전)
PREVIOUS_FREEZE = dict(sha256="ccb7ec63763a715a", structure_sha256="0b69134457880767285c3516e1e9c962bb9b778a5c6f4e85b248c6b16b01c80d",
                       topology_sha256="04c84b0e24af31f5605800ae30bc2750563a1aeb3e72390aa6d6643676b68e84")  # 커밋 d069d2c 이후 구조 동일(9dd68aa에서도 변경 없음)


def topology_hash(nodes, edges):
    """node id·층과 edge의 id·끝점·type만 본 해시. condition·문구 변화와 그래프 모양 변화를 구분하기 위함."""
    payload = json.dumps([sorted((n["node_id"], n["layer"]) for n in nodes),
                          sorted((e["edge_id"], e["src"], e["dst"], e["edge_type"]) for e in edges)], ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


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
             "grouping_rationale", "identity_links", "env_id"]
EDGE_COLS = ["edge_id", "src", "dst", "edge_type", "basis", "status", "claim_level", "condition", "supporting",
             "rationale", "caution", "uncertainty_status", "review_decision"]
LINK_COLS = ["link_id", "target_kind", "target_id", "feature_layer", "feature_id", "dimension", "assessment",
             "creates_event", "rationale"]


IDENTITY_COLS = ["identity_id", "surface_a", "surface_b", "status", "resolved_by", "resolution_basis", "unresolved_reason",
                 "model_relevance", "manual_decision_required", "review_decision", "context", "referenced_facts"]


def identity_relevance(edges, cands, worlds):
    """각 동일성이 현재 모델 어디에 쓰이는지 계산한다(조건부 edge, 후보 가정, world)."""
    rows = []
    for i in IDENTITY_REGISTER:
        iid = i["identity_id"]
        use = [e["edge_id"] for e in edges if iid in e["condition"].split("|")]
        use += [c["candidate_id"] for c in cands if iid in c["identity_conditions"].split("|")]
        use += [w["world_id"] for w in worlds if iid in w["identity_conditions"].split("|")]
        r = dict(i)
        if i["status"] == "RESOLVED":
            cs = [c["candidate_id"] for c in cands if iid in c["identity_conditions"].split("|")]
            r["model_relevance"] = "조건부 사용 없음(RESOLVED)" + (f"; 확정과 충돌해 PRUNED된 후보: {', '.join(cs)}" if cs else "")
        else:
            r["model_relevance"] = i.get("model_relevance") or (", ".join(use) if use else "NONE")
        if i["status"] == "UNRESOLVED":
            r["manual_decision_required"] = i.get("manual_decision_required") or ("YES" if use else "NO")
        else:
            r["manual_decision_required"] = "NO"
        rows.append(r)
    return rows


# LATENT 재감사 이전(커밋 9dd68aa) world 상태 — before/after 비교 기준
WORLDS_BEFORE_REAUDIT = {'W1': ('MEDIUM', 'G01a|G02a|G03a|G04a|G05a|G06a|G07a|G08a|G09a|G11a|G12a|G13a'), 'W2': ('MEDIUM', 'G01a|G02b|G03a|G04b|G06b|G07c|G08a|G09a|G12a'), 'W3': ('LOW', 'G01b|G02a|G04c|G05a|G06a|G07a|G08a|G12a'), 'W4': ('LOW', 'G01a|G02b|G03c|G06a|G07b|G08b|G11a|G13a'), 'W5': ('HIGH', 'G01a|G06a|G07a|G08a'), 'W6': ('LOW', 'G06c|G07d|G12b')}


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
    reg = regression.run_or_exit()
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
    write_csv(OUT / "identity_register.csv", IDENTITY_REGISTER, IDENTITY_COLS)
    frozen = graph_hash(nodes, edges)
    freeze = dict(name="Validated Observed Partial DAG", sha256=frozen, structure_sha256=structure_hash(nodes, edges),
                  previous_sha256_prefix=PREVIOUS_FREEZE["sha256"],
                  previous_structure_sha256=PREVIOUS_FREEZE["structure_sha256"],
                  structure_unchanged=structure_hash(nodes, edges) == PREVIOUS_FREEZE["structure_sha256"],
                  topology_sha256=topology_hash(nodes, edges),
                  previous_topology_sha256=PREVIOUS_FREEZE["topology_sha256"],
                  topology_unchanged=topology_hash(nodes, edges) == PREVIOUS_FREEZE["topology_sha256"],
                  change_note="narrative world 사용 방식 재정리(경쟁하는 설명으로 병렬 보존). observed graph는 손대지 않음 — "
                              "node·edge·condition·끝점·type 모두 그대로",
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
    worlds_before = [dict(world_id=k, min_grade=v[0], latent_bridges=v[1]) for k, v in WORLDS_BEFORE_REAUDIT.items()]
    report.write_reaudit(OUT / "latent_candidate_reaudit.md", cands, worlds, worlds_before)
    report.write_gaps(OUT / "gap_candidates.md", gaps, cands, nodes)
    report.write_worlds(OUT / "narrative_worlds.md", worlds, cands, gaps, nodes)
    report.write_story_matrix(OUT / "narrative_world_story_matrix.md", worlds, cands, gaps, nodes,
                              identity_relevance(edges, cands, worlds), edges)
    report.write_latent_csv(OUT, gaps, cands, worlds)

    # STAGE 6 — mechanism Super-DAG(질적 SCM) + AUDIT 4
    import stage6_mechanisms
    import report_mech
    sd = stage6_mechanisms.build(nodes, edges, cands, worlds, inst, env, frozen)
    a4 = audits.audit4(sd, nodes, edges, frozen, graph_hash, worlds, cands)
    apply_dispositions("AUDIT4", a4)
    report_mech.write_all(OUT, sd, cands, nodes, worlds, inst)
    report_mech.write_audit4(OUT / "audit_4_mechanism_super_dag.md", a4, sd, reg)
    gate("AUDIT 4 (mechanism super-DAG)", a4)
    write_csv(OUT / "identity_register.csv", identity_relevance(edges, cands, worlds), IDENTITY_COLS)

    # STAGE 7 — Interactive Temporal DAG 데이터(docs/data) + AUDIT 5
    import build_visualization
    canon, ui = build_visualization.build(DOCS, OUT, PACK, a4)
    a5 = audits.audit5(ui, canon, frozen, (DOCS / "js" / "app.js").read_text(encoding="utf-8"),
                       (DOCS / "css" / "app.css").read_text(encoding="utf-8"))
    apply_dispositions("AUDIT5", a5)
    report_mech.write_audit5(OUT / "audit_5_interactive_visualization.md", a5, ui, reg)
    gate("AUDIT 5 (interactive visualization)", a5)
    print(f"[STAGE 7] docs/data 작성 node={ui['meta']['counts']['nodes']} edges={ui['meta']['counts']['edges']}")
    report.write_validation_summary(OUT / "validation_summary.md",
                                    {"Audit 1": a1, "Audit 2": a2, "Audit 3": a3w, "Audit 4": a4, "Audit 5": a5}, freeze, worlds, cands)
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
                    ("warn_dispositions", "warn_dispositions.csv"),
                    ("mechanism_super_dag_nodes", "mechanism_super_dag_nodes.csv"),
                    ("mechanism_super_dag_edges", "mechanism_super_dag_edges.csv"),
                    ("mechanism_definitions", "mechanism_definitions.csv"),
                    ("world_mechanism_configurations", "world_mechanism_configurations.csv"),
                    ("mechanism_interaction_matrix", "mechanism_interaction_matrix.csv"),
                    ("mechanism_interventions", "mechanism_interventions.csv"),
                    ("qualitative_structural_rules", "qualitative_structural_rules.csv")]:
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
                     for a, fs in [("AUDIT1", a1), ("AUDIT2", a2), ("AUDIT3", a3w), ("AUDIT4", a4), ("AUDIT5", a5)] for f in fs])
    con.close()
    print(f"[DB] {DB.relative_to(ROOT)} 작성 완료")


if __name__ == "__main__":
    main()
