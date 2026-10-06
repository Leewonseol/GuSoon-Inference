#!/usr/bin/env python3
"""GuSoon v2 world-aware temporal DAG sparsification (transitive reduction of the edge template).

Input: the DAG template of v2_09 (output/36–38, tables dag_node_projection / temporal_edge_candidates).
The template is captured exactly as v2_09 builds it (v2_09 is run in its no-write mode and the
template passed to materialize() is taken), and cross-checked against the DB tables.

Each of the 969 edge candidates is classified as
  PRIMITIVE_EDGE            must be kept: some world needs it.
  DERIVED_TRANSITIVE_EDGE   in EVERY world in which the edge is active, the kept (primitive) edges
                            alone already give a from -> to path.
  REVIEW_REQUIRED           EVIDENCE_ONLY / REVIEW_REQUIRED edges of the template (never active in
                            any world, so they are not reduction material).

World-aware derivability (sound over every partial or total assignment, logically valid or not):
an edge e = a -> b with activation literals L(e) = cond(e) ∪ act(a) ∪ act(b) (the endpoint literal is
dropped when the endpoint is a SAME-pair member, because its collapsed class can be active through a
partner) is DERIVED only if a path of kept strict edges a -> x1 -> ... -> b exists such that
  - every path edge's condition literals ⊆ L(e)      (HARD and CONDITIONAL are never mixed: a
                                                      conditional edge counts only if e's own
                                                      activation already guarantees its condition)
  - every intermediate node's activation ⊆ L(e)      (an intermediate that can vanish in some world
                                                      where e is active blocks the derivation)
All conditions in the template are conjunctions of positive literals, so ⊆ is exact entailment.
Explicit relative-time / procedural / order->execution / REVISED_BY edges are never reduced
(kept as primitive by policy). DURING (containment) edges are not order edges: kept, never used
as path edges. Only date-only edges are reduction candidates.

Every PRIMITIVE strict edge gets a witness world: L(e) TRUE, every other free boolean FALSE,
record anchors fixed, open-set membership left UNDETERMINED, no SAME TRUE. In it e is active and,
without e, from -> to is unreachable in the primitive template. The witness worlds are
deterministic validation probes, not samples and not an enumeration of the world space.

Nothing here changes the DAG's meaning: no node, no new edge, no causal edge, no date is added,
dropped or moved; evidence (basis rows) is kept separately from topology (temporal_edge_evidence).

Usage:
  python3 scripts/v2_10_temporal_edge_reduction.py                 # classify + validate + write
  python3 scripts/v2_10_temporal_edge_reduction.py --mutation NAME # inject a fault, validate, write nothing
"""

import argparse
import csv
import hashlib
import importlib.util
import logging
import re
import sys
from collections import Counter, deque
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "database" / "gusun_v2.duckdb"
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
SHA_PATH = RAW_DIR / "gusun_research_v2_SHA256SUMS.txt"
OUT_AUDIT, OUT_PRIM, OUT_DER, OUT_VALID = ("41_v2_temporal_edge_reduction_audit.csv", "42_v2_primitive_temporal_edges.csv",
                                           "43_v2_derived_temporal_edges.csv", "44_v2_temporal_reduction_validation.csv")
NEW_TABLES = ["temporal_edge_reduction_audit", "primitive_temporal_edges", "derived_temporal_edges",
              "temporal_edge_evidence"]
MUTATIONS = ["naive_reduction", "ignore_vanishing_intermediate", "mix_hard_conditional", "anchor_court_acts",
             "derive_explicit_edge", "drop_during_edge", "review_edge_as_primitive", "derive_via_derived_edge"]
CAPTURE = "__v2_10_capture__"

PRIM, DER, REVW = "PRIMITIVE_EDGE", "DERIVED_TRANSITIVE_EDGE", "REVIEW_REQUIRED"

_spec = importlib.util.spec_from_file_location("v2_09", ROOT / "scripts" / "v2_09_dag_template.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

log = logging.getLogger("v2_temporal_reduction")


# ---------------------------------------------------------------- helpers
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def fetch(con, sql):
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    return [{c: ("" if v is None else v) for c, v in zip(cols, r)} for r in cur.fetchall()]


def lits(f):
    """Literal set of a conjunction of positive literals; None if the formula is not of that shape."""
    if f is None:
        return frozenset()
    k = f[0]
    if k == "var":
        return frozenset([(f[1], True)])
    if k == "eq":
        return frozenset([(f[1], f[2])])
    if k == "and":
        out = set()
        for x in f[1:]:
            s = lits(x)
            if s is None:
                return None
            out |= s
        return frozenset(out)
    return None


def lit_text(lt):
    v, val = lt
    return v if val is True else f"{v} = {val}"


def capture_template():
    """Run v2_09 in its no-write mutation mode with a no-op mutation name and take the template that
    v2_09 itself passes to materialize(). v2_09 opens the DB read-only and writes nothing in that mode."""
    cap = {}
    orig = D.materialize

    def wrap(world, tmpl, assignment=None, transitive=True):
        cap.setdefault("tmpl", tmpl)
        return orig(world, tmpl, assignment, transitive)

    D.materialize = wrap
    D.MUTATIONS = list(D.MUTATIONS) + [CAPTURE]
    argv = sys.argv
    sys.argv = ["v2_09_dag_template.py", "--mutation", CAPTURE]
    logging.disable(logging.CRITICAL)
    code = None
    try:
        D.main()
    except SystemExit as e:
        code = e.code
    finally:
        logging.disable(logging.NOTSET)
        sys.argv = argv
        D.materialize = orig
    return cap.get("tmpl"), code


# ---------------------------------------------------------------- world-level graph helpers
def strict_closure(r):
    """Reachability pairs over the strict (order) edges of a materialized world."""
    adj = {}
    for a, b, t, _ in r["edges"]:
        if t in D.STRICT_TYPES:
            adj.setdefault(a, set()).add(b)
        elif t == D.AFTER:
            adj.setdefault(b, set()).add(a)
    return {(a, b) for a in r["wnodes"] for b in D.reachable(adj, a)}, adj


def closure_assignment_conflicts(r, closure, assignment):
    """Temporal-assignment check against the transitive order (not only the direct edges): required once
    shortcut edges may be absent from a template."""
    if not assignment:
        return []
    val = {}
    for nid, txt in assignment.items():
        val[r["rep"][nid]] = D.interval(txt)[0]
    return sorted(f"{a}->{b}" for a, b in closure if a in val and b in val and not val[a] < val[b])


def world_reduction_size(closure, adj, wnodes):
    """Size of the (unique) transitive reduction of an acyclic world DAG: edge a->b is kept iff b is not
    reachable from any other direct successor of a."""
    if any((a, a) in closure for a in wnodes):
        return None
    n = 0
    for a, succ in adj.items():
        for b in succ:
            if not any(b == c or (c, b) in closure for c in succ if c != b):
                n += 1
    return n


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--mutation", default="")
    args = ap_.parse_args()
    mut = args.mutation
    LOG_DIR.mkdir(exist_ok=True)

    tmpl, cap_code = capture_template()

    handlers = [logging.StreamHandler(sys.stdout)]
    if not mut:
        handlers.append(logging.FileHandler(LOG_DIR / "v2_temporal_edge_reduction.log", mode="w", encoding="utf-8"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=handlers,
                        force=True)
    if mut and mut not in MUTATIONS:
        log.error("unknown mutation %s (known: %s)", mut, ", ".join(MUTATIONS))
        sys.exit(2)

    checks = []

    def check(cid, desc, ok, detail="", severity="ERROR"):
        checks.append([cid, desc, "PASS" if ok else severity, detail])
        if not ok:
            (log.error if severity == "ERROR" else log.warning)("%s %s: %s", cid, desc, detail)

    # ---------------- integrity at start
    expected_sha = {}
    for line in SHA_PATH.read_text(encoding="utf-8").splitlines():
        h, fn = line.split("  ", 1)
        expected_sha[fn] = h
    raw_ok_start = all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items())
    preserved = sorted(p.name for p in OUT_DIR.glob("*.csv") if re.match(r"^(0[1-9]|[123]\d|40)_", p.name))
    out_before = {n: sha256(OUT_DIR / n) for n in preserved}
    con = duckdb.connect(str(DB_PATH), read_only=bool(mut))
    tables = sorted(t[0] for t in con.execute("SHOW TABLES").fetchall())
    protected = [t for t in tables if t not in NEW_TABLES]
    digests_before = {t: D.table_digest(con, t) for t in protected}

    check("R00", "v2_09 template capture (v2_09 no-write mode, ERROR=0 → exit 3)", tmpl is not None and cap_code == 3,
          f"exit={cap_code}")
    if tmpl is None:
        for c in checks:
            log.error("%s", c)
        sys.exit(1)
    nodes, edges = tmpl["nodes"], tmpl["edges"]
    by_id = {e["id"]: e for e in edges}

    # ---------------- cross-check with the persisted template (output/36–37 tables)
    db_edges = {r["edge_candidate_id"]: r for r in fetch(con, "SELECT * FROM temporal_edge_candidates")}
    db_nodes = {r["dag_node_candidate_id"]: r for r in fetch(con, "SELECT * FROM dag_node_projection")}
    rvars = {r["variable_id"]: r for r in fetch(con, "SELECT * FROM repaired_world_variables")}

    def cond_text(e):
        if e["kind"] == D.EVID:
            return "NEVER (EVIDENCE_ONLY: 시간 제약으로 강제하지 않음)"
        if e["kind"] == D.REVE:
            return "NEVER (REVIEW_REQUIRED: 검토 전 비활성)"
        base = f"active({e['frm']}) ∧ active({e['to']})"
        return base if e["cond"] is None else f"{base} ∧ {D.render(e['cond'])}"

    mism = []
    if set(db_edges) != set(by_id):
        mism.append(f"edge id sets differ ({len(db_edges)} vs {len(by_id)})")
    for eid, e in by_id.items():
        r = db_edges.get(eid)
        if r is None:
            continue
        if (r["from_node_candidate"], r["to_node_candidate"], r["edge_type"], r["hard_or_conditional"],
                r["activation_condition"]) != (e["frm"], e["to"], e["etype"], e["kind"], cond_text(e)):
            mism.append(eid)
    for nid, n in nodes.items():
        r = db_nodes.get(nid)
        if r is None or r["node_class"] != n["cls"]:
            mism.append(nid)
        elif n["cls"] in D.NODE_CLASSES and r["activation_condition"] != D.render(n["act"]):
            mism.append(nid)
    check("R01", "captured template = persisted template (37 ids·endpoints·type·kind·activation, 36 class·activation)",
          not mism, "|".join(mism[:10]) or f"edges={len(edges)} nodes={len(nodes)}")
    opaque = [e["id"] for e in edges if lits(e["cond"]) is None] + \
             [n for n, x in nodes.items() if x["act"] is not None and lits(x["act"]) is None]
    check("R02", "모든 edge 조건·node 활성 조건이 양의 literal 연언 (⊆ 검사가 정확한 함의)", not opaque, "|".join(opaque[:10]))

    # ---------------- classification inputs
    same_members = {a for _, a, b in tmpl["same_pairs"]} | {b for _, a, b in tmpl["same_pairs"]}

    def is_node(x):
        return nodes[x]["cls"] in D.NODE_CLASSES and nodes[x]["act"] is not None

    def act_lits(x):
        return lits(nodes[x]["act"]) if is_node(x) else None

    def L(e, endpoint_all=False):
        s = set(lits(e["cond"]))
        for k in ("frm", "to"):
            x = e[k]
            if is_node(x) and (endpoint_all or x not in same_members):
                s |= act_lits(x)
        return frozenset(s)

    def btypes(e):
        return [bt for bt, _, _ in e["bases"]]

    def evidence_type(e):
        bts = sorted(set(btypes(e)))
        if e["kind"] in D.NEVER_KINDS:
            return "NONACTIVE:" + "|".join(bts)
        if all(b in D.DATE_BASES for b in bts):
            return "DATE_ONLY:" + "|".join(bts)
        if any(b in D.DATE_BASES for b in bts):
            return "EXPLICIT_AND_DATE:" + "|".join(bts)
        return "EXPLICIT:" + "|".join(bts)

    def is_explicit(e):
        return any(b in D.TEXT_BASES or b == "JUDGMENT_REVISION" for b in btypes(e))

    def is_strict(e):
        return e["etype"] in D.STRICT_TYPES and e["kind"] not in D.NEVER_KINDS

    def date_span(e):
        def when(x):
            k, t = nodes[x]["time"]
            return D.interval(t) if k in ("COURT_ENTRY_DATE", "CLAIMED_DATE") else None
        a, b = when(e["frm"]), when(e["to"])
        return (b[0] - a[1]) if a and b else -1

    check_conds = mut not in ("naive_reduction", "mix_hard_conditional")
    court_like = {x for x, n in nodes.items() if n["time"][0] == "COURT_ENTRY_DATE" or x.startswith("DN_J_")}
    check_inter = mut not in ("naive_reduction", "ignore_vanishing_intermediate")

    def find_path(e, kept, need_cond=True, need_inter=True):
        """BFS for a from->to path over kept strict edges (excluding e) that is guaranteed in every world
        where e is active. Returns (path edge ids, missing literals) or None."""
        Ls = L(e)
        src, dst = e["frm"], e["to"]
        adj = {}
        for x in kept:
            if x == e["id"]:
                continue
            ex = by_id[x]
            if need_cond and not lits(ex["cond"]) <= Ls:
                continue
            adj.setdefault(ex["frm"], []).append(ex)
        prev, q = {src: None}, deque([src])
        while q:
            u = q.popleft()
            for ex in sorted(adj.get(u, []), key=lambda z: z["id"]):
                v = ex["to"]
                if v in prev:
                    continue
                if v != dst and need_inter:
                    have = Ls | lits(ex["cond"]) if mut == "mix_hard_conditional" and need_cond is False else Ls
                    anchored = mut == "anchor_court_acts" and v in court_like
                    if not is_node(v) or (not anchored and not act_lits(v) <= have):
                        continue
                elif v != dst and not is_node(v):
                    continue
                prev[v] = ex
                q.append(v)
        if dst not in prev:
            return None
        path, v = [], dst
        while v != src:
            ex = prev[v]
            path.append(ex["id"])
            v = ex["frm"]
        path.reverse()
        missing = set()
        for pid in path:
            missing |= set(lits(by_id[pid]["cond"])) - Ls
        for pid in path[:-1]:
            missing |= set(act_lits(by_id[pid]["to"])) - Ls
        return path, sorted(missing)

    # ---------------- reduction (date-only strict edges; longest date span first)
    cls, reason = {}, {}
    for e in edges:
        if e["kind"] in D.NEVER_KINDS:
            cls[e["id"]], reason[e["id"]] = REVW, "TEMPLATE_NEVER_ACTIVE"
        elif e["etype"] == D.DURING:
            cls[e["id"]], reason[e["id"]] = PRIM, "DURING_CONTAINMENT_NOT_ORDER"
        elif is_explicit(e):
            cls[e["id"]], reason[e["id"]] = PRIM, "EXPLICIT_TEXT_OR_PROCEDURAL_KEPT"
    kept = {e["id"] for e in edges if is_strict(e)}
    candidates = sorted((e for e in edges if e["id"] not in cls), key=lambda e: (-date_span(e), e["id"]))
    derived_order = []
    for e in candidates:
        p = find_path(e, kept, check_conds, check_inter)
        if p is not None:
            cls[e["id"]] = DER
            kept.discard(e["id"])
            derived_order.append(e["id"])
        else:
            cls[e["id"]] = PRIM
    # ---------------- classification-level mutations
    if mut == "derive_explicit_edge":
        cls["TE0001"] = DER
        kept.discard("TE0001")
    elif mut == "drop_during_edge":
        for e in edges:
            if e["etype"] == D.DURING and e["kind"] not in D.NEVER_KINDS:
                cls[e["id"]] = DER
    elif mut == "review_edge_as_primitive":
        for e in edges:
            if e["kind"] in D.NEVER_KINDS:
                cls[e["id"]] = PRIM
                kept.add(e["id"])
    primitive = {eid for eid, c in cls.items() if c == PRIM}
    prim_strict = {eid for eid in primitive if is_strict(by_id[eid])}

    derived_order = sorted(eid for eid, c in cls.items() if c == DER)
    # alternative paths for DERIVED edges, recomputed on the FINAL primitive set
    alt = {}
    for eid in derived_order:
        e = by_id[eid]
        alt[eid] = find_path(e, prim_strict, check_conds, check_inter)
    if mut == "derive_via_derived_edge" and len(derived_order) < 2:
        # build a fake chain: claim an edge is derived through another derived edge
        cand_e = next(e for e in edges if cls[e["id"]] == PRIM and evidence_type(e).startswith("DATE_ONLY")
                      and e["kind"] == D.HARD)
        cls[cand_e["id"]] = DER
        derived_order.append(cand_e["id"])
        alt[cand_e["id"]] = ([cand_e["id"]], [])
        primitive.discard(cand_e["id"])
        prim_strict.discard(cand_e["id"])

    # diagnostics for PRIMITIVE date-only edges: why they cannot be derived (on the final primitive set)
    diag = {}
    for e in edges:
        if cls[e["id"]] != PRIM or not is_strict(e) or is_explicit(e):
            continue
        full = find_path(e, prim_strict, True, True)
        if full is not None:
            diag[e["id"]] = ("PRIMITIVE_DESPITE_GUARANTEED_PATH", full)
            continue
        cond_only = find_path(e, prim_strict, True, False)
        if cond_only is not None:
            diag[e["id"]] = ("INTERMEDIATE_NODE_MAY_VANISH", cond_only)
            continue
        naive = find_path(e, prim_strict, False, False)
        if naive is not None:
            diag[e["id"]] = ("PATH_EDGE_CONDITION_NOT_GUARANTEED", naive)
        else:
            diag[e["id"]] = ("NO_ALTERNATIVE_PATH", None)

    # ---------------- reduced template + validation worlds
    def tmpl_with(edge_ids):
        t = dict(tmpl)
        t["edges"] = [by_id[x] for x in sorted(edge_ids)]
        return t

    full_t = tmpl
    prim_t = tmpl_with(primitive)

    free_bool = [v for v, r in rvars.items() if r["fixed_or_free"] == "FREE" and r["domain"].startswith("{TRUE, FALSE}")
                 and not v.startswith(("MEMBER_", "SAMELIST_"))]
    fixed = {}
    for v, r in rvars.items():
        if r["fixed_or_free"].startswith("FIXED_TRUE"):
            fixed[v] = True
        elif r["fixed_or_free"].startswith("FIXED"):
            fixed[v] = r["domain"].strip("{}")

    def base_world(default):
        w = dict(fixed)
        for v in free_bool:
            w[v] = default
        return w

    def witness_raw(e):
        """L(e) TRUE, every other free boolean FALSE (may violate repaired constraints)."""
        w = base_world(False)
        for v, val in L(e, endpoint_all=True):
            w[v] = val
        return w

    # logically valid witness: chronological backtracking over the free booleans with Kleene checks of the
    # repaired constraints; L(e) forced TRUE; every other variable prefers FALSE (so intermediates vanish).
    logic = tmpl["logic"]
    by_var = {}
    for cid, f in logic:
        for v in D.vars_of(f):
            by_var.setdefault(v, []).append((cid, f))
    order_vars = sorted(free_bool, key=lambda v: (-len(by_var.get(v, ())), v))

    def solve(forced, prefer_false=True, limit=200000):
        asg = dict(fixed)
        asg.update(forced)
        if any(D.evaluate(f, asg) is False for _, f in logic):
            return None
        todo = [v for v in order_vars if v not in asg]
        steps = [0]
        sys.setrecursionlimit(max(10000, sys.getrecursionlimit()))

        def ok(v):
            return all(D.evaluate(f, asg) is not False for _, f in by_var.get(v, ()))

        def rec(i):
            if i == len(todo):
                return True
            v = todo[i]
            for val in ((False, True) if prefer_false else (True, False)):
                steps[0] += 1
                if steps[0] > limit:
                    return False
                asg[v] = val
                if ok(v) and rec(i + 1):
                    return True
            del asg[v]
            return False

        return asg if rec(0) else None

    def witness(e):
        w = solve(dict(L(e, endpoint_all=True)))
        return (w, True) if w is not None else (witness_raw(e), False)

    def compare(name, world, asg):
        r0 = D.materialize(world, full_t, asg)
        r1 = D.materialize(world, prim_t, asg)
        c0, adj0 = strict_closure(r0)
        c1, _ = strict_closure(r1)
        diff = []
        if set(r0["wnodes"]) != set(r1["wnodes"]):
            diff.append("nodes")
        if c0 != c1:
            missing = sorted(c0 - c1)[:3]
            extra = sorted(c1 - c0)[:3]
            diff.append(f"reach(-{len(c0 - c1)} {missing} +{len(c1 - c0)} {extra})")
        cyc0 = sorted(sorted(c) for c in r0["cycles"])
        cyc1 = sorted(sorted(c) for c in r1["cycles"])
        if cyc0 != cyc1:
            diff.append(f"cycles {cyc0} vs {cyc1}")
        if sorted(r0["during_conflicts"]) != sorted(r1["during_conflicts"]):
            diff.append("during_conflicts")
        dur0 = sorted((a, b) for a, b, t, _ in r0["edges"] if t == D.DURING)
        dur1 = sorted((a, b) for a, b, t, _ in r1["edges"] if t == D.DURING)
        if dur0 != dur1:
            diff.append("during_edges")
        if (r0["logic"], r0["anchor_conflicts"]) != (r1["logic"], r1["anchor_conflicts"]):
            diff.append("logic/anchor")
        ca0 = closure_assignment_conflicts(r0, c0, asg)
        ca1 = closure_assignment_conflicts(r1, c1, asg)
        t0 = "INVALID" if (r0["cycles"] or r0["during_conflicts"] or r0["anchor_conflicts"] or ca0) else "VALID"
        t1 = "INVALID" if (r1["cycles"] or r1["during_conflicts"] or r1["anchor_conflicts"] or ca1) else "VALID"
        if t0 != t1:
            diff.append(f"temporal(closure) {t0} vs {t1}")
        raw_same = r0["temporal"] == r1["temporal"]
        return dict(name=name, r0=r0, r1=r1, c0=c0, adj0=adj0, diff=diff, t0=t0, t1=t1, raw_same=raw_same,
                    raw0=r0["temporal"], raw1=r1["temporal"])

    # ---------------- validation: structural
    n_all = len(edges)
    cnt = Counter(cls.values())
    check("R03", "969 edge 모두 정확히 하나의 reduction_class", len(cls) == n_all == len(db_edges) and
          set(cnt) <= {PRIM, DER, REVW}, f"{dict(cnt)}")
    never_bad = [e["id"] for e in edges if (e["kind"] in D.NEVER_KINDS) != (cls[e["id"]] == REVW)]
    check("R04", "EVIDENCE_ONLY·REVIEW_REQUIRED edge = REVIEW_REQUIRED (primitive/derived에 넣지 않음)", not never_bad,
          "|".join(never_bad[:10]))
    expl_bad = [e["id"] for e in edges if is_explicit(e) and e["kind"] not in D.NEVER_KINDS and cls[e["id"]] != PRIM]
    n_expl = sum(1 for e in edges if is_explicit(e) and e["kind"] not in D.NEVER_KINDS)
    check("R05", "명시적 상대시간·절차·명령→집행·REVISED_BY edge는 모두 PRIMITIVE", not expl_bad,
          "|".join(expl_bad) or f"explicit kept={n_expl}")
    dur_bad = [e["id"] for e in edges if e["etype"] == D.DURING and e["kind"] not in D.NEVER_KINDS and cls[e["id"]] != PRIM]
    check("R06", "DURING(포함) edge는 PRIMITIVE이며 선후 path에 쓰지 않음", not dur_bad, "|".join(dur_bad))
    der_bad = []
    for eid in derived_order:
        e = by_id[eid]
        if not evidence_type(e).startswith("DATE_ONLY"):
            der_bad.append(f"{eid}:not date-only")
        p = alt.get(eid)
        if p is None:
            der_bad.append(f"{eid}:no path in final primitive set")
            continue
        path, missing = p
        if any(x not in prim_strict for x in path):
            der_bad.append(f"{eid}:path uses non-primitive {','.join(x for x in path if x not in prim_strict)}")
        Ls = L(e)
        for x in path:
            if not lits(by_id[x]["cond"]) <= Ls:
                der_bad.append(f"{eid}:{x} condition not implied")
        for x in path[:-1]:
            if not act_lits(by_id[x]["to"]) <= Ls:
                der_bad.append(f"{eid}:intermediate {by_id[x]['to']} may vanish")
    check("R07", "DERIVED edge마다 최종 PRIMITIVE edge만으로 된 path가 있고, path edge 조건·중간 node 활성이 모두 그 edge의 "
          "활성 조건에 함의됨 (HARD/CONDITIONAL 혼합 없음)", not der_bad, "|".join(der_bad[:8]) or f"derived={len(derived_order)}")
    new_bad = [x for x in primitive | set(derived_order) if x not in db_edges]
    check("R08", "primitive·derived edge ⊆ 37의 edge (새 edge·node·causal·narrative edge 없음)", not new_bad, "|".join(new_bad))
    ev_rows = []
    for e in edges:
        for i, (bt, phrase, refs) in enumerate(e["bases"], 1):
            detail = (f"{nodes[refs[0]]['time'][1]} < {nodes[refs[1]]['time'][1]}" if bt in D.DATE_BASES
                      else phrase)
            ev_rows.append([f"{e['id']}#{i}", e["id"], bt, detail, "|".join(refs), cls[e["id"]]])
    ev_cover = {r[1] for r in ev_rows}
    check("R09", "시간 정보 보존: 969 edge 전부 basis(evidence) 행을 temporal_edge_evidence에 유지 (DERIVED 포함)",
          ev_cover == set(by_id) and len(ev_rows) >= n_all, f"evidence rows={len(ev_rows)}")

    # ---------------- validation: witness worlds (necessity of each PRIMITIVE strict edge)
    wit_fail, wit_logic_invalid, wit_logic_ids, wit_count, wit_unsolved, wit_world = [], [], Counter(), 0, [], {}
    explicit_redundant = []
    for eid in sorted(prim_strict):
        e = by_id[eid]
        w, solved = witness(e)
        wit_world[eid] = (w, solved)
        if not solved:
            wit_unsolved.append(eid)
        r_full = D.materialize(w, prim_t)
        act_ok = any(x[3] == eid for x in r_full["edges"]) or any(
            (x[0], x[1]) == (r_full["rep"][e["frm"]], r_full["rep"][e["to"]]) for x in r_full["edges"])
        r_minus = D.materialize(w, tmpl_with(primitive - {eid}))
        c_minus, _ = strict_closure(r_minus)
        need = (r_minus["rep"][e["frm"]], r_minus["rep"][e["to"]]) not in c_minus
        wit_count += 1
        if not (act_ok and need):
            (explicit_redundant if is_explicit(e) else wit_fail).append(f"{eid}(active={act_ok},needed={need})")
        if r_full["logic"] == "INVALID":
            wit_logic_invalid.append(eid)
            for cid in r_full["logic_violations"]:
                wit_logic_ids[cid] += 1
    check("R10", "PRIMITIVE date-only edge마다 witness world 존재: 그 edge가 활성이고, 빼면 from→to 도달 불가 (필요성 증명)",
          not wit_fail, "|".join(wit_fail[:8]) or f"witnessed={wit_count - len(explicit_redundant)}/{wit_count}")
    check("R11", "명시적 edge 중 world-aware로는 중복이지만 정책상 PRIMITIVE로 둔 것", True,
          "|".join(explicit_redundant) or "0 (명시 edge도 모두 witness world에서 필요)")
    n_wit_valid = wit_count - len(wit_logic_invalid)
    check("R12", "witness world가 논리적으로 가능한 world (repaired constraint 위반 없음; L(e) 강제, 나머지는 FALSE 우선 탐색)", not wit_logic_invalid,
          f"valid={n_wit_valid}/{wit_count}; unsolved={len(wit_unsolved)}; violated={dict(wit_logic_ids.most_common(5))}",
          severity="WARNING")

    # ---------------- validation: reachability / cycle / temporal equality
    probe = []
    for name, desc, world, asg, _ in D.TEST_WORLDS:
        probe.append((name, world, asg, "TEST"))
    probe.append(("PW_ALL_TRUE", base_world(True), None, "PROBE"))
    probe.append(("PW_ALL_TRUE_NO_SAME", {**base_world(True), **{v: False for v in rvars if v.startswith("SAME_")}},
                  None, "PROBE"))
    act_vars = sorted({lt[0] for x in nodes if is_node(x) for lt in act_lits(x)})
    for v in act_vars:
        w = {**base_world(True), **{s: False for s in rvars if s.startswith("SAME_")}, v: False}
        probe.append((f"PW_ALL_BUT_{v}", w, None, "PROBE"))
    for eid in sorted(prim_strict | set(derived_order)):
        probe.append((f"PW_WITNESS_{eid}", witness(by_id[eid])[0], None, "PROBE"))
        probe.append((f"PW_RAWWITNESS_{eid}", witness_raw(by_id[eid]), None, "PROBE"))
    results = {}
    probe_bad, raw_diff = [], []
    for name, world, asg, kind in probe:
        res = compare(name, world, asg)
        results[name] = res
        if kind == "TEST":
            r0 = res["r0"]
            check(f"T{name[2:4]}", f"{name}: reachability·cycle·DURING·temporal 판정 동일 (원 969 vs primitive, collapse 후)",
                  not res["diff"], "|".join(res["diff"]) or
                  f"logic={r0['logic']} temporal={res['t0']} wnodes={len(r0['wnodes'])} reach_pairs={len(res['c0'])} "
                  f"cycles={len(r0['cycles'])} collapsed={len(r0['classes'])}")
        elif res["diff"]:
            probe_bad.append(f"{name}:{'|'.join(res['diff'])}")
        if not res["raw_same"]:
            raw_diff.append(f"{name}:{res['raw0']}->{res['raw1']}")
    n_probe = sum(1 for p in probe if p[3] == "PROBE")
    check("R13", "결정적 probe world(전부 참·SAME 없음·node 하나씩 제거·edge별 witness)에서 reachability·cycle 동일",
          not probe_bad, "|".join(probe_bad[:5]) or f"probe worlds={n_probe}")
    check("R14", "v2_09 materialize의 원래 temporal 판정(직접 edge 기준 할당 검사)도 동일", not raw_diff,
          "|".join(raw_diff[:5]) or "all test/probe worlds identical", severity="WARNING")
    cyc_worlds = [n for n, r in results.items() if r["r0"]["cycles"]]
    # cycle probe: the same synthetic back-edges are added to BOTH templates (as v2_09's cycle_abca mutation) so
    # that cycles actually occur; SCCs (incl. after SAME collapse) must be identical.
    back = [dict(id="TE9101", frm="DN_EC0107", to="DN_EC0105", etype=D.BEFORE, kind=D.CTEMP,
                 cond=("and", ("var", "E_EC0105"), ("var", "E_EC0107")), bases=[], strength="", review=False, note=""),
            dict(id="TE9102", frm="DN_J_JEONGJO_17930613_THEFT", to="DN_J_JEONGJO_17930512_THEFT", etype=D.BEFORE,
                 kind=D.HARD, cond=None, bases=[], strength="", review=False, note=""),
            dict(id="TE9103", frm="DN_EC0063", to="DN_EC0007", etype=D.BEFORE, kind=D.HARD, cond=None, bases=[],
                 strength="", review=False, note="")]
    full_c = dict(tmpl, edges=list(edges) + back)
    prim_c = dict(tmpl, edges=[by_id[x] for x in sorted(primitive)] + back)
    cyc_probe, cyc_bad, n_cyc = [], [], 0
    for name, world, asg, kind in probe[:12] + [p for p in probe if p[0].startswith("PW_ALL_BUT_")]:
        r0 = D.materialize(world, full_c, asg)
        r1 = D.materialize(world, prim_c, asg)
        s0 = sorted(sorted(c) for c in r0["cycles"])
        s1 = sorted(sorted(c) for c in r1["cycles"])
        if s0:
            n_cyc += 1
            cyc_probe.append(f"{name}:{len(s0)}scc/{sum(len(c) for c in s0)}nodes")
        if s0 != s1 or r0["temporal"] != r1["temporal"]:
            cyc_bad.append(name)
    check("R15", "cycle 판정 동일: 기존 world의 cycle 유무 + 양쪽에 같은 역방향 edge를 넣은 cycle probe에서 SCC(collapse 후) 동일",
          all(not results[n]["diff"] for n in cyc_worlds) and not cyc_bad and n_cyc > 0,
          "|".join(cyc_bad[:5]) or f"worlds with cycles: original={len(cyc_worlds)}, cycle-probe={n_cyc} "
                                   f"({', '.join(cyc_probe[:6])})")

    # ---------------- info: naive vs world-aware, world-level sparse view
    naive_red = [eid for eid, (rs, _) in diag.items() if rs != "NO_ALTERNATIVE_PATH"]
    by_reason = Counter(rs for rs, _ in diag.values())
    check("I01", "date-only PRIMITIVE edge의 차단 이유 분포 (naive reduction이면 지워질 shortcut 포함)", True,
          f"{dict(by_reason)}; naive-redundant={len(naive_red)}")
    wr = []
    for name, _, _, _, _ in D.TEST_WORLDS:
        res = results[name]
        n_act = sum(1 for a, b, t, _ in res["r0"]["edges"] if t in D.STRICT_TYPES)
        red = world_reduction_size(res["c0"], res["adj0"], res["r0"]["wnodes"])
        wr.append(f"{name[:4]}:{n_act}→{red if red is not None else 'cyclic'}")
    check("I02", "world 단위(materialize 후) 전이 축약 크기: 활성 선후 edge → 그 world의 최소 edge (참고)", True, " ".join(wr))

    # ---------------- integrity at end
    digests_after = {t: D.table_digest(con, t) for t in protected}
    changed = [t for t in protected if digests_before[t] != digests_after[t]]
    check("R16", "기존 DuckDB table 변경 없음", not changed, "|".join(changed) or f"protected={len(protected)}")
    out_changed = [n for n in preserved if sha256(OUT_DIR / n) != out_before[n]]
    check("R17", "output 01–40 변경 없음", not out_changed and len(preserved) == 40, "|".join(out_changed) or
          f"preserved={len(preserved)}")
    raw_ok_end = all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items())
    check("R18", "data/raw SHA-256 시작·종료 일치", raw_ok_start and raw_ok_end, f"files={len(expected_sha)}")

    n_err = sum(1 for c in checks if c[2] == "ERROR")
    n_warn = sum(1 for c in checks if c[2] == "WARNING")
    if mut:
        log.info("mutation %s: derived=%d validation ERROR=%d (%s)", mut, len(derived_order), n_err,
                 "|".join(c[0] for c in checks if c[2] == "ERROR"))
        con.close()
        sys.exit(0 if n_err else 3)

    # ---------------- rows
    def path_text(p):
        if not p:
            return ""
        return " → ".join([by_id[p[0]]["frm"]] + [by_id[x]["to"] for x in p]) + " [" + ", ".join(p) + "]"

    def path_conds(e, p):
        if not p:
            return ""
        parts = []
        for x in p:
            c = by_id[x]["cond"]
            parts.append(f"{x}:{D.render(c) if c is not None else 'HARD(조건 없음)'}")
        for x in p[:-1]:
            v = by_id[x]["to"]
            parts.append(f"active({v}):{D.render(nodes[v]['act'])}")
        return "; ".join(parts)

    def primitive_reason(e):
        eid = e["id"]
        if eid in diag:
            rs, p = diag[eid]
            if rs == "NO_ALTERNATIVE_PATH":
                return "NO_ALTERNATIVE_PATH: 다른 보존 edge로 from→to path 없음"
            missing = ", ".join(lit_text(x) for x in p[1])
            if rs == "INTERMEDIATE_NODE_MAY_VANISH":
                return f"INTERMEDIATE_NODE_MAY_VANISH: 이 edge가 활성인 world에서도 중간 node가 없을 수 있음 (보장 안 되는 조건: {missing})"
            if rs == "PATH_EDGE_CONDITION_NOT_GUARANTEED":
                return f"PATH_EDGE_CONDITION_NOT_GUARANTEED: path의 edge 조건·중간 node가 보장되지 않음 ({missing})"
            return rs
        return reason.get(eid, "")

    def notes(e):
        eid = e["id"]
        out = []
        if cls[eid] == DER:
            out.append("전이 관계: 이 edge가 활성인 모든 world에서 alternative_path가 활성 (시간 정보는 temporal_edge_evidence에 유지)")
        elif eid in diag and diag[eid][0] != "NO_ALTERNATIVE_PATH":
            out.append("조건부 중복: alternative_path_conditions가 모두 참인 world에서만 shortcut이 중복(그 world의 materialize 단계에서만 생략 가능); "
                       "42의 witness_world(논리적으로 가능한 world)에서는 이 edge 없이 from→to 도달 불가")
        elif cls[eid] == PRIM and is_strict(e):
            out.append("42의 witness_world에서 이 edge 없이 from→to 도달 불가")
        if cls[eid] == REVW:
            out.append("template에서 어떤 world에도 활성화되지 않음 → reduction 대상 아님")
        if e["review"]:
            out.append("37 manual_review_required=YES 유지")
        if e["frm"] in same_members or e["to"] in same_members:
            out.append("endpoint가 SAME 후보: collapse된 class로 활성될 수 있어 그 endpoint의 활성 literal은 L(e)에서 제외")
        return " / ".join(out)

    audit_cols = ["edge_candidate_id", "from_node", "to_node", "original_edge_type", "activation_condition", "evidence_type",
                  "reduction_class", "alternative_path", "alternative_path_conditions", "primitive_reason", "notes"]
    audit = []
    for e in edges:
        eid = e["id"]
        p = alt.get(eid, (None, None))[0] if cls[eid] == DER else (diag[eid][1][0] if eid in diag and diag[eid][1] else None)
        audit.append([eid, e["frm"], e["to"], e["etype"], cond_text(e), evidence_type(e), cls[eid], path_text(p),
                      path_conds(e, p), primitive_reason(e) if cls[eid] == PRIM else ("" if cls[eid] == DER else
                      "EVIDENCE_ONLY/REVIEW_REQUIRED edge (template 비활성)"), notes(e)])
    prim_cols = ["edge_candidate_id", "from_node", "to_node", "edge_type", "hard_or_conditional", "activation_condition",
                 "evidence_type", "primitive_reason", "conditionally_redundant_path", "redundant_only_if", "witness_world"]
    prim_rows = []
    for e in edges:
        eid = e["id"]
        if cls[eid] != PRIM:
            continue
        p = diag[eid][1] if eid in diag and diag[eid][1] else None
        wtxt = ""
        if eid in wit_world:
            w, solved = wit_world[eid]
            Le = L(e, endpoint_all=True)
            extra = sorted(v for v in free_bool if w.get(v) is True and (v, True) not in Le)
            wtxt = ("L(e) TRUE = " + " ∧ ".join(lit_text(x) for x in sorted(Le)) +
                    ("; 논리 제약 충족을 위해 추가 TRUE = " + ", ".join(extra) if extra else "") +
                    "; 나머지 자유 boolean FALSE; 기록 anchor 고정; open-set membership 미정" +
                    ("" if solved else " (논리 제약 미충족 raw witness)"))
        prim_rows.append([eid, e["frm"], e["to"], e["etype"], e["kind"], cond_text(e), evidence_type(e), primitive_reason(e),
                          path_text(p[0]) if p else "", " ∧ ".join(lit_text(x) for x in p[1]) if p else "", wtxt])
    der_cols = ["edge_candidate_id", "from_node", "to_node", "edge_type", "hard_or_conditional", "activation_condition",
                "evidence_type", "alternative_path", "alternative_path_conditions"]
    der_rows = [[eid, by_id[eid]["frm"], by_id[eid]["to"], by_id[eid]["etype"], by_id[eid]["kind"], cond_text(by_id[eid]),
                 evidence_type(by_id[eid]), path_text(alt[eid][0]), path_conds(by_id[eid], alt[eid][0])]
                for eid in sorted(derived_order)]
    ev_cols = ["evidence_id", "edge_candidate_id", "basis_type", "basis_detail", "basis_refs", "reduction_class"]

    OUT_DIR.mkdir(exist_ok=True)
    write_csv(OUT_DIR / OUT_AUDIT, audit_cols, audit)
    write_csv(OUT_DIR / OUT_PRIM, prim_cols, prim_rows)
    write_csv(OUT_DIR / OUT_DER, der_cols, der_rows)
    for table, cols, rows in (("temporal_edge_reduction_audit", audit_cols, audit),
                              ("primitive_temporal_edges", prim_cols, prim_rows),
                              ("derived_temporal_edges", der_cols, der_rows),
                              ("temporal_edge_evidence", ev_cols, ev_rows)):
        con.execute(f"CREATE OR REPLACE TABLE {table} ({', '.join(f'{c} VARCHAR' for c in cols)})")
        if rows:
            con.executemany(f"INSERT INTO {table} VALUES ({', '.join('?' for _ in cols)})", [[str(x) for x in r] for r in rows])
    tbl_counts = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in NEW_TABLES}
    check("R19", "새 DuckDB table 행 수 = CSV 행 수", tbl_counts == {
        "temporal_edge_reduction_audit": len(audit), "primitive_temporal_edges": len(prim_rows),
        "derived_temporal_edges": len(der_rows), "temporal_edge_evidence": len(ev_rows)}, str(tbl_counts))
    digests_final = {t: D.table_digest(con, t) for t in protected}
    check("R20", "새 table 작성 후에도 기존 table 변경 없음", digests_final == digests_before, "")
    n_err = sum(1 for c in checks if c[2] == "ERROR")
    n_warn = sum(1 for c in checks if c[2] == "WARNING")
    write_csv(OUT_DIR / OUT_VALID, ["check_id", "description", "severity", "detail"], checks)
    con.close()

    # ---------------- log: counts and cases
    hard_p = sum(1 for e in edges if cls[e["id"]] == PRIM and e["kind"] == D.HARD)
    cond_p = sum(1 for e in edges if cls[e["id"]] == PRIM and e["kind"] in D.COND_KINDS)
    date_only = [e for e in edges if evidence_type(e).startswith("DATE_ONLY")]
    log.info("edges=%d PRIMITIVE=%d DERIVED_TRANSITIVE=%d REVIEW_REQUIRED=%d", n_all, cnt[PRIM], cnt[DER], cnt[REVW])
    log.info("PRIMITIVE: HARD=%d CONDITIONAL=%d (CTEMP=%d CID=%d)", hard_p, cond_p,
             sum(1 for e in edges if cls[e["id"]] == PRIM and e["kind"] == D.CTEMP),
             sum(1 for e in edges if cls[e["id"]] == PRIM and e["kind"] == D.CID))
    log.info("date-only edges=%d removed(DERIVED)=%d kept=%d; explicit edges kept=%d", len(date_only),
             sum(1 for e in date_only if cls[e["id"]] == DER), sum(1 for e in date_only if cls[e["id"]] == PRIM), n_expl)
    log.info("date-only primitive reasons: %s", dict(by_reason))
    log.info("by evidence: %s", dict(Counter((evidence_type(e).split(":")[0] + ":" + e["kind"], cls[e["id"]]) for e in edges)))
    blockers = Counter()
    for eid, (rs, p) in diag.items():
        if rs == "INTERMEDIATE_NODE_MAY_VANISH":
            for x in p[1]:
                blockers[lit_text(x)] += 1
    log.info("most frequent vanishing-intermediate blockers: %s", blockers.most_common(12))
    log.info("witness worlds logically valid: %d/%d; violated constraints: %s", n_wit_valid, wit_count,
             wit_logic_ids.most_common(8))
    log.info("world-level reduction (참고): %s", " ".join(wr))

    cases = {
        "A_KIM_MYEONGSIN": ["DN_EC0096", "DN_EC0097", "DN_EC0003", "DN_EC0004", "DN_EC0005", "DN_EC0007", "DN_EC0036",
                            "DN_EC0053"],
        "B_THEFT_JUDGMENT_CHAIN": ["DN_J_LEEHYEONGWON_17930512_THEFT", "DN_J_JEONGJO_17930512_THEFT",
                                   "DN_J_IJOWON_17930527_THEFT", "DN_EC0048", "DN_EC0049", "DN_EC0063", "DN_EC0061",
                                   "DN_J_HONG_17930613_THEFT", "DN_J_JEONGJO_17930613_THEFT"],
        "C_JAMIDEOK": ["DN_EC0089", "DN_EC0104", "DN_EC0103", "DN_EC0105", "DN_EC0106", "DN_EC0107", "DN_EC0111",
                       "DN_EC0119", "DN_EC0120", "DN_EC0112", "DN_EC0113", "DN_EC0114"],
    }
    for cname, cn in cases.items():
        s = set(cn)
        log.info("=== case %s nodes=%s", cname, ",".join(x[3:] for x in cn))
        for e in edges:
            if e["frm"] in s and e["to"] in s:
                extra = ""
                if e["id"] in diag and diag[e["id"]][1]:
                    extra = (f" naive-path={path_text(diag[e['id']][1][0])} 보장 안 됨={','.join(lit_text(x) for x in diag[e['id']][1][1])}")
                log.info("  %s %s -%s-> %s [%s] %s %s%s", e["id"], e["frm"][3:], e["etype"], e["to"][3:], e["kind"],
                         cls[e["id"]], evidence_type(e), extra)
        out_date = [e for e in edges if (e["frm"] in s) != (e["to"] in s) and evidence_type(e).startswith("DATE_ONLY")]
        log.info("  (case 밖 node와의 date-only edge %d개: DERIVED %d, PRIMITIVE %d, 그중 naive-redundant %d)", len(out_date),
                 sum(1 for e in out_date if cls[e["id"]] == DER), sum(1 for e in out_date if cls[e["id"]] == PRIM),
                 sum(1 for e in out_date if e["id"] in diag and diag[e["id"]][0] != "NO_ALTERNATIVE_PATH"))
    log.info("validation: ERROR=%d WARNING=%d", n_err, n_warn)
    for c in checks:
        log.info("%s %s %s", c[0], c[2], c[3][:300])
    if n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
