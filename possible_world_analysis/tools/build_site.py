#!/usr/bin/env python3
"""《시곡》 분석 결과 → GitHub Pages 사이트 데이터(docs/sigok/data.js) + docs/index.html 자산 해시 갱신.

- 입력: sources.yaml, 01_claim_registry.csv, 02_variables.yaml, results/*.json, 03_constraints.py(제약·인과 그래프)
- 출력: docs/sigok/data.js  (window.SIGOK_DATA = {...}; file:// 로 열어도 동작하도록 fetch 대신 script)
- docs/index.html이 싣는 sigok/*·vendor/* 주소의 ?v=<내용 해시>를 맞춘다(브라우저 캐시의 옛 파일과 섞이지 않게).

사용: python tools/build_site.py [--check]   (--check: 파일을 쓰지 않고 최신 여부만 검사, 다르면 exit 1)
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import networkx as nx
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT.parent / "docs"
SITE = DOCS / "sigok"
sys.path.insert(0, str(ROOT / "tools"))

from loader import load_constraints  # noqa: E402

DATE_RE = re.compile(r"(\d{4})년 음력 (\d+)월 (\d+)일")
REPO = "https://github.com/Leewonseol/GuSoon-Inference/blob/HEAD/possible_world_analysis/"
ASSET_REF = re.compile(r'((?:src|href)=")((?:sigok|vendor)/[^"?]+)(?:\?v=[0-9a-f]*)?(")')


def parse_idx(cons, s):
    m = DATE_RE.search(s or "")
    return cons.L(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def jload(name):
    return json.loads((ROOT / "results" / name).read_text(encoding="utf-8"))


def graph_payload(cons):
    g = cons.build_graph()
    depth = {}
    for n in nx.topological_sort(g):
        preds = list(g.predecessors(n))
        depth[n] = 0 if not preds else 1 + max(depth[p] for p in preds)
    # 외생 변수는 첫 자식 바로 왼쪽 열에 두어 가로 폭을 줄인다
    for n in g.nodes:
        if g.nodes[n]["kind"] != "endo":
            kids = list(g.successors(n))
            depth[n] = max(0, min(depth[k] for k in kids) - 1) if kids else 0
    cols: dict[int, list[str]] = {}
    for n, d in depth.items():
        cols.setdefault(d, []).append(n)
    pos = {}
    for d, ns in cols.items():
        ns.sort(key=lambda n: (g.nodes[n]["kind"] != "endo", n))
        for i, n in enumerate(ns):
            pos[n] = {"x": d * 300, "y": (i - (len(ns) - 1) / 2) * 62}
    nodes = []
    for n in g.nodes:
        vid, _, desc = g.nodes[n]["label"].partition(" ")
        nodes.append({"id": n, "var": vid, "label": desc, "kind": g.nodes[n]["kind"], "pos": pos[n]})
    edges = [{"source": u, "target": v, "kind": d["kind"]} for u, v, d in g.edges(data=True)]
    return {"nodes": nodes, "edges": edges}


def build_data():
    cons = load_constraints()
    import report_writer  # CF_TEXT, COST_KO
    import build_readme  # US_KO, TV_KO

    src = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))["sources"]
    var = yaml.safe_load((ROOT / "02_variables.yaml").read_text(encoding="utf-8"))["variables"]
    with (ROOT / "01_claim_registry.csv").open(encoding="utf-8-sig") as f:
        claims = list(csv.DictReader(f))
    csp, worlds, cfs = jload("csp_results.json"), jload("worlds.json"), jload("counterfactuals.json")
    econ, link = jload("economic_scenarios.json"), jload("link_check.json")

    modes = {}
    for k, m in csp["modes"].items():
        e = {"desc": m["desc"], "result": m["result"], "hard": m["hard"]}
        if m["result"] == "UNSAT":
            e["mus"] = [[x["id"] for x in s] for s in m["mus"]]
            e["mcs"] = [[x["id"] for x in s] for s in m["mcs"]]
        else:
            e["windows"] = {ev: [parse_idx(cons, w[0]), parse_idx(cons, w[1])] for ev, w in m["windows"].items() if w}
        modes[k] = e

    def wit(w, relaxed):
        return {"relaxed": relaxed, "dropped_prefs": w["dropped_preferences"],
                "events": {ev: parse_idx(cons, s) for ev, s in w["events"].items()}}

    witnesses = [dict(id=f"F{i + 1}", label=f"MODE F 수정안 F{i + 1}", **wit(x["witness"], x["relaxed_anchors"]))
                 for i, x in enumerate(csp["F_ADAPT_witnesses"])]
    fc = csp["F_COMPRESSED"]
    witnesses.append(dict(id="FC", label="결말 압축 유지(F-압축)", **wit(fc["witness"], fc["witness_correction"])))

    rows = []
    for r in worlds["worlds"]:
        mk, mf, admin = cons.explain_world(r)
        rows.append({"world": r["world"], "pareto": r["pareto"], "proj": r["proj"], "flags": r["flags"],
                     "n_assump": r["n_assump"], "n_dates": r["n_dates"], "date_sets": r["date_sets"],
                     "assump": r["assump"], "vals": r["vals"], "murder": mk, "frame": mf, "admin": admin})

    anchors = [  # 사료 연대 앵커(시간 충돌 화면의 기준 표지)
        {"id": "HT_SIM_OKSA_1780_6", "at": [cons.L(1780, 6, 1), cons.L(1780, 6, 30)], "label": "심리록 성옥(경자 6월)"},
        {"id": "HT_SIL_CASE_1781", "at": [cons.L(1781, 1, 1), cons.L(1781, 12, 30)], "label": "실록 '事在辛丑'"},
        {"id": "HT_SIL_REVIEW_SPRING_1781", "at": [cons.L(1781, 1, 1), cons.L(1781, 3, 30)], "label": "재조사 지시(신축 봄)"},
        {"id": "HT_JSJ_IN_OFFICE_1781_9", "at": [cons.L(1781, 9, 29), cons.L(1781, 9, 29)], "label": "조상진 재임 확인"},
        {"id": "HT_SIM_HYEONGJO_1781_8", "at": [cons.L(1781, 8, 1), cons.L(1781, 8, 30)], "label": "형조 심리(신축 8월)"},
        {"id": "HT_LKY_BY_1782_4", "at": [cons.L(1782, 4, 23), cons.L(1782, 4, 23)], "label": "이경양 감사 확인"},
        {"id": "HT_JOKJAENG_1782_7", "at": [cons.L(1782, 7, 1), cons.L(1782, 7, 30)], "label": "조재정 격쟁"},
        {"id": "HT_JSJ_DAESASEONG_1783_5", "at": [cons.L(1783, 5, 9), cons.L(1783, 5, 9)], "label": "조상진 대사성"},
        {"id": "HT_FINAL_1783_6_3", "at": [cons.L(1783, 6, 3), cons.L(1783, 6, 3)], "label": "최종 판부"},
    ]
    exog = {k: {"var": v[0], "label": v[1], "layer": v[2]} for k, v in cons.EXOG.items()}
    import z3
    b = {k: z3.Bool(k) for k in list(cons.EXOG) + cons.ENDO_ORDER}
    endo = {k: {"var": d[0], "label": d[1], "kind": d[2], "parents": d[4]} for k, d in cons._endo_defs(b).items()}

    lc = {}
    for r in link["results"].values():
        lc[r["status"]] = lc.get(r["status"], 0) + 1
    return {
        "meta": {"checked_at": link["checked_at"], "index_note": csp["index_note"], "repo": REPO,
                 "counts": {"sources": len(src), "claims": len(claims), "variables": len(var), "constraints": len(cons.CS),
                            "feasible_worlds": worlds["n_feasible_projections"], "representatives": len(rows)},
                 "link_status": lc, "domain": [cons.LO, cons.HI], "base_year": cons.BASE_YEAR},
        "layers": report_writer.LAYER_KO, "cost": report_writer.COST_KO,
        "us_ko": build_readme.US_KO, "tv_ko": build_readme.TV_KO,
        "constraints": {c.cid: {"layer": c.layer, "text": c.text, "basis": c.basis, "status": c.status} for c in cons.CS},
        "events": {k: {"var": v[0], "label": v[1]} for k, v in cons.EVENTS.items()},
        "modes": modes, "witnesses": witnesses, "anchors": anchors,
        "compressed": {"forced": fc["forced_synopsis_choices"], "mcs": [[x["id"] for x in s] for s in fc["anchor_corrections"]]},
        "f_adapt_mcs": [[x["id"] for x in s] for s in csp["F_ADAPT_anchor_corrections"]],
        "worlds": {"n": worlds["n_feasible_projections"], "dims": worlds["dims"], "forced": worlds["forced_common_assumptions"],
                   "rows": rows},
        "cf": [dict(q, text=report_writer.CF_TEXT[q["qid"]][0], limit=report_writer.CF_TEXT[q["qid"]][1]) for q in cfs],
        "econ": econ, "exog": exog, "endo": endo, "graph": graph_payload(cons),
        "variables": var, "claims": claims, "sources": src,
    }


def asset_version(rel):
    return hashlib.sha256((DOCS / rel).read_bytes()).hexdigest()[:12]


def render():
    data = build_data()
    js = ("/* 자동 생성: possible_world_analysis/tools/build_site.py — 직접 수정하지 말 것 */\n"
          "window.SIGOK_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    return js


def stamped_index(data_js_text):
    html = (DOCS / "index.html").read_text(encoding="utf-8")

    def ver(rel):
        if rel == "sigok/data.js":
            return hashlib.sha256(data_js_text.encode("utf-8")).hexdigest()[:12]
        return asset_version(rel)
    return ASSET_REF.sub(lambda m: f"{m.group(1)}{m.group(2)}?v={ver(m.group(2))}{m.group(3)}", html)


def main(check=False):
    js = render()
    html = stamped_index(js)
    cur_js = (SITE / "data.js").read_text(encoding="utf-8") if (SITE / "data.js").exists() else ""
    cur_html = (DOCS / "index.html").read_text(encoding="utf-8")
    if check:
        ok = cur_js == js and cur_html == html
        print("site up to date" if ok else "site STALE: python tools/build_site.py")
        return 0 if ok else 1
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data.js").write_text(js, encoding="utf-8")
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote docs/sigok/data.js ({len(js.encode()) // 1024} KB) and stamped docs/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
