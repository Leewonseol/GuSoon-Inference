"""Interactive Temporal DAG(docs/) 헤드리스 브라우저 테스트.

실행(저장소 루트에서, build.py 실행 뒤):
    pip install playwright            # 한 번만. 브라우저가 없으면 `python3 -m playwright install chromium`
    python3 scripts/gusun_clean/test_visualization.py [--shots DIR]

docs/를 로컬 http 서버로 띄우고 Chromium으로 연다. 항목별 PASS/FAIL을 출력하고, 하나라도 실패하면 exit 1.
화면이 canonical 값을 그대로 보여 주는지(개수·configuration·후보 등급·개입 결과·공존 판정), OBSERVED backbone이
어떤 world·view·개입·필터에서도 사라지지 않는지, 날짜 순서가 화면 좌표에서도 지켜지는지 확인한다.
"""
import argparse
import csv
import functools
import http.server
import json
import os
import socketserver
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
DOCS = ROOT / "docs"
OUT = ROOT / "output" / "clean"
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")


def rd(name):
    with open(OUT / name, encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    handler = functools.partial(Quiet, directory=str(DOCS))
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


RESULTS = []


def check(name):
    def deco(fn):
        def run(*a, **k):
            try:
                ok, detail = fn(*a, **k)
            except Exception as ex:  # noqa: BLE001
                ok, detail = False, f"예외: {type(ex).__name__}: {ex}"
            RESULTS.append((name, ok, detail))
            print(f"[{'PASS' if ok else 'FAIL'}] {name} — {detail}")
            return ok
        return run
    return deco


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default="", help="스크린샷 저장 폴더(선택)")
    args = ap.parse_args()
    from playwright.sync_api import sync_playwright

    sd_nodes = rd("mechanism_super_dag_nodes.csv")
    sd_edges = rd("mechanism_super_dag_edges.csv")
    configs = {r["world_id"]: r for r in rd("world_mechanism_configurations.csv")}
    cands = {r["candidate_id"]: r for r in rd("latent_candidates.csv")}
    ivs = rd("mechanism_interventions.csv")
    inter = rd("mechanism_interaction_matrix.csv")
    eps = {r["node_id"]: r for r in rd("episode_nodes.csv")}
    observed = sorted(n["node_id"] for n in sd_nodes if n["sd_status"] == "OBSERVED")
    from stage5_worlds import COMMON_OUTCOME_NODES
    outcome = sorted({x for v in COMMON_OUTCOME_NODES.values() for x in v})
    mechs = ["M1", "M2", "M3", "M4", "M5", "M6", "MB"]
    shots = Path(args.shots) if args.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)

    srv, url = serve()
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        page.on("requestfailed", lambda r: errors.append(f"requestfailed: {r.url}"))
        page.goto(url)
        page.wait_for_function("window.__viz && window.__viz.cy")
        page.wait_for_timeout(300)
        ev = page.evaluate

        def visible_ids(sel="node"):
            # visible()은 렌더 전까지 캐시될 수 있어 계산된 style(display)로 본다
            return set(ev(f"window.__viz.cy.$('{sel}').filter(e => e.style('display') !== 'none' && (e.isNode() || (e.source().style('display') !== 'none' && e.target().style('display') !== 'none'))).map(e => e.id())"))

        def classes(nid):
            return set(ev(f"window.__viz.cy.getElementById('{nid}').classes()"))

        def click_node(nid):
            pos = ev(f"""(() => {{ const cy = window.__viz.cy; const n = cy.getElementById('{nid}');
                cy.center(n); cy.zoom({{level: 1.0, position: n.position()}});
                const r = n.renderedPosition(); const b = document.getElementById('cy').getBoundingClientRect();
                return [b.left + r.x, b.top + r.y]; }})()""")
            page.wait_for_timeout(80)
            page.mouse.click(pos[0], pos[1])
            page.wait_for_timeout(120)

        @check("1 page load")
        def t_load():
            title = page.inner_text("#app-title")
            desc = page.inner_text("#app-desc")
            ok = title == "구순–김명신 사건 Mechanism Super-DAG" and desc.startswith("확정된 사건은 고정하고")
            return ok, f"제목·설명 표시, cytoscape 초기화 ({title})"

        @check("2 CSV → JSON 생성(현재 canonical과 일치)")
        def t_json():
            import build_visualization as bv
            canon = bv.load_canonical()
            a4 = json.loads((DOCS / "data" / "interactions.json").read_text(encoding="utf-8"))
            findings = [dict(check=f["check"], severity=f["severity"], target=pp["key"], message=f["message"])
                        for pp in a4["pairs"] for f in pp["audit4"]]
            ui = bv.make_ui(canon, findings)
            bad = [k for k in bv.DATA_FILES if bv._dump(ui[k]) != (DOCS / "data" / f"{k}.json").read_text(encoding="utf-8")]
            bundle = (DOCS / "data" / "bundle.js").read_text(encoding="utf-8") == bv.bundle_text(ui)
            return not bad and bundle, f"data/*.json {len(bv.DATA_FILES)}개 + bundle.js가 canonical CSV에서 다시 만든 값과 같음" + (f" (다름: {bad})" if bad else "")

        @check("3 node·edge 개수 = canonical")
        def t_counts():
            n, e = ev("window.__viz.cy.nodes().length"), ev("window.__viz.cy.edges().length")
            return n == len(sd_nodes) and e == len(sd_edges), f"화면 node {n} / edge {e}, canonical {len(sd_nodes)} / {len(sd_edges)}"

        @check("4 W1–W5 선택")
        def t_worlds():
            msgs = []
            for wid in ["W1", "W2", "W3", "W4", "W5"]:
                page.click(f"#world-buttons button[data-world='{wid}']")
                page.wait_for_timeout(60)
                if page.get_attribute(f"#world-buttons button[data-world='{wid}']", "aria-checked") != "true":
                    msgs.append(f"{wid} 버튼 선택 안 됨")
                bridges = set(filter(None, configs[wid]["latent_bridges"].split("|")))
                for b in bridges:
                    if "hl" not in classes(b):
                        msgs.append(f"{wid}: {b} 강조 안 됨")
                for c in cands:
                    if c not in bridges and "dim" not in classes(c):
                        msgs.append(f"{wid}: {c} 흐림 안 됨")
                for m in mechs:
                    lab = ev(f"window.__viz.cy.getElementById('{m}').data('label')")
                    if f"[{wid}: {configs[wid][m]}]" not in lab:
                        msgs.append(f"{wid}.{m} 표시 {lab!r} ≠ {configs[wid][m]}")
                if not set(observed) <= visible_ids():
                    msgs.append(f"{wid}: 관측 node 사라짐")
                if not page.is_hidden("#banner-world"):
                    msgs.append(f"{wid}: REJECTED 배너가 보임")
                chips = page.locator("#p-world .chip").all_inner_texts()
                if "OFF" in chips or [c for c in chips if c in ("ON", "PARTIAL", "UNSPECIFIED")] != [configs[wid][m] for m in mechs]:
                    msgs.append(f"{wid}: world 패널 값 {chips} ≠ CSV")
            if shots:
                page.screenshot(path=str(shots / "world_W2.png"))
            page.click("#world-buttons button[data-world='ALL']")
            return not msgs, "W1–W5 각각 bridge 강조·나머지 흐림·메커니즘 값 = CSV·관측 node 유지" if not msgs else "; ".join(msgs[:6])

        @check("5 W6 REJECTED 배너")
        def t_w6():
            page.click("#world-buttons button[data-world='W6']")
            page.wait_for_timeout(80)
            banner = page.inner_text("#banner-world") if page.is_visible("#banner-world") else ""
            bridges = set(filter(None, configs["W6"]["latent_bridges"].split("|")))
            rej = all("hl-rej" in classes(b) for b in bridges)
            wp = page.inner_text("#p-world")
            ok = "REJECTED" in banner and rej and "REJECTED" in wp and set(observed) <= visible_ids()
            if shots:
                page.screenshot(path=str(shots / "world_W6.png"))
            page.click("#world-buttons button[data-world='ALL']")
            return ok, f"배너='{banner[:40]}…', W6 bridge {sorted(bridges)} 배제 표시, 관측 node 유지"

        @check("6 status filter")
        def t_status():
            msgs = []
            latent = {n["node_id"] for n in sd_nodes if n["sd_status"] == "LATENT_MECHANISM"}
            ctx = {n["node_id"] for n in sd_nodes if n["sd_status"] == "CONTEXT"}
            derived = {e["edge_id"] for e in sd_edges if e["sd_status"] == "DERIVED"}
            page.uncheck("input[data-status='LATENT']")
            v = visible_ids()
            if v & latent or not set(observed) <= v:
                msgs.append("LATENT 숨김 실패 또는 관측 node 사라짐")
            page.check("input[data-status='LATENT']")
            page.uncheck("input[data-status='CONTEXT']")
            if visible_ids() & ctx:
                msgs.append("CONTEXT 숨김 실패")
            page.check("input[data-status='CONTEXT']")
            page.uncheck("input[data-status='DERIVED']")
            if visible_ids("edge") & derived:
                msgs.append("DERIVED edge 숨김 실패")
            page.check("input[data-status='DERIVED']")
            if not page.is_disabled("input[data-status='OBSERVED']"):
                msgs.append("OBSERVED 체크박스가 잠겨 있지 않음")
            if visible_ids() != {n["node_id"] for n in sd_nodes}:
                msgs.append("다시 켠 뒤 전체가 보이지 않음")
            return not msgs, "LATENT·CONTEXT node, DERIVED edge 숨김/복원, OBSERVED 고정" if not msgs else "; ".join(msgs)

        @check("7 mechanism filter")
        def t_mech():
            page.uncheck("input[data-mech='M1']")
            m1c = {n["node_id"] for n in sd_nodes if n["node_type"] == "CANDIDATE_BRIDGE" and n["mechanism"] == "M1"}
            v = visible_ids()
            ok = "M1" not in v and not (v & m1c) and "M2" in v and set(observed) <= v
            page.check("input[data-mech='M1']")
            ok = ok and {"M1"} | m1c <= visible_ids()
            return ok, f"M1과 M1 후보 {len(m1c)}개 숨김 → 복원, 다른 메커니즘·관측 node 유지"

        @check("8 node 상세 패널")
        def t_node_detail():
            msgs = []
            click_node("EP09")
            d = page.inner_text("#p-detail")
            for want in ["EP09", "OBSERVED", "모든 world 공통"] + eps["EP09"]["member_fact_ids"].split("|") + eps["EP09"]["source_record_ids"].split("|"):
                if want not in d:
                    msgs.append(f"EP09 상세에 {want} 없음")
            click_node("G04a")
            d = page.inner_text("#p-detail")
            c = cands["G04a"]
            for want in ["사료에 직접 적힌 사실이 아니라 빈칸을 설명하기 위한 가설", "G04a", c["gap_id"], c["source_support"], c["plausibility_grade"],
                         c["overall"], c["bridge_directly_attested"], c["latent_bridge_claim"][:20]]:
                if want not in d:
                    msgs.append(f"G04a 상세에 {want} 없음")
            click_node("CTX_F007")
            d = page.inner_text("#p-detail")
            if "사건 발생 자체를 증명하지 않음" not in d or "F007" not in d:
                msgs.append("context 상세 문구 없음")
            click_node("ENV03")
            if "사건 발생 자체를 증명하지 않음" not in page.inner_text("#p-detail"):
                msgs.append("환경 context 상세 문구 없음")
            click_node("M3")
            if "UNSPECIFIED ≠ OFF" not in page.inner_text("#p-detail"):
                msgs.append("메커니즘 상세에 UNSPECIFIED ≠ OFF 없음")
            if shots:
                page.screenshot(path=str(shots / "detail_M3.png"))
            return not msgs, "OBSERVED(EP09)·LATENT(G04a)·CONTEXT(F007, ENV03)·MECHANISM(M3) 클릭 → canonical 값 표시" if not msgs else "; ".join(msgs)

        @check("9 edge 상세 패널")
        def t_edge_detail():
            pos = ev("""(() => { const cy = window.__viz.cy; const e = cy.getElementById('OE008');
                cy.zoom(1.0); cy.center(e); const r = e.renderedMidpoint(); const b = document.getElementById('cy').getBoundingClientRect();
                return [b.left + r.x, b.top + r.y]; })()""")
            page.wait_for_timeout(80)
            page.mouse.click(pos[0], pos[1])
            page.wait_for_timeout(120)
            d = page.inner_text("#p-detail")
            ok = "OE008" in d and "ORDER_TO_ACTION" in d and "EP09" in d and "EP11" in d
            return ok, "OE008(EP09 → EP11, ORDER_TO_ACTION) 클릭 → edge 상세 표시"

        @check("10 search")
        def t_search():
            msgs = []
            for q, want in [("CF021", None), ("G04a", "G04a"), ("M3", "M3"), ("이광섭", None), ("EP33", "EP33")]:
                page.fill("#search", q)
                page.wait_for_timeout(60)
                items = page.locator("#search-results li[data-id]").all_inner_texts()
                if not items:
                    msgs.append(f"'{q}' 결과 없음")
                    continue
                page.press("#search", "Enter")
                page.wait_for_timeout(350)
                sel = ev("window.__viz.cy.$('node:selected').map(n => n.id())")
                if want and sel != [want]:
                    msgs.append(f"'{q}' 선택 {sel}")
                if not sel or sel[0] not in page.inner_text("#p-detail"):
                    msgs.append(f"'{q}' 상세 패널 미표시")
                if q == "CF021" and sel and "CF021" not in eps.get(sel[0], {}).get("member_fact_ids", ""):
                    msgs.append(f"CF021 검색이 {sel}로 감")
            return not msgs, "CF ID·후보 ID·메커니즘 ID·인물·node ID 검색 → focus + 상세" if not msgs else "; ".join(msgs)

        @check("11 intervention")
        def t_iv():
            msgs = []
            page.click(".ptabs button[data-ptab='iv']")
            for m in mechs:
                page.click(f"#p-iv button[data-iv='{m}']")
                page.wait_for_timeout(80)
                rows = [r for r in ivs if r["mechanism"] == m]
                txt = page.inner_text("#iv-table")
                for r in rows:
                    if r["variable"] not in txt or r["result"] not in txt:
                        msgs.append(f"do({m}) {r['variable']} {r['result']} 표시 안 됨")
                    if "iv-" + r["result"] not in classes(r["variable"]):
                        msgs.append(f"do({m}) {r['variable']} 강조 없음")
                    for x in filter(None, r["removed"].split("|")):
                        if "iv-removed" not in classes(x):
                            msgs.append(f"do({m}) {x} 제거 표시 없음")
                shown = page.locator("#iv-table .iv-row").count()
                if shown != len(rows):
                    msgs.append(f"do({m}) 행 {shown} ≠ {len(rows)}")
                if not set(observed) <= visible_ids():
                    msgs.append(f"do({m}) 중 관측 node 사라짐")
                if "역사적 사실을 지우지 않는다" not in page.inner_text("#banner-iv"):
                    msgs.append("개입 배너 문구 없음")
            if shots:
                page.click("#p-iv button[data-iv='M1']")
                page.wait_for_timeout(400)
                page.screenshot(path=str(shots / "intervention_M1.png"))
            page.click("#p-iv button[data-iv='']")
            return not msgs, f"do(M=OFF) 7개 → 저장된 결과 {len(ivs)}행 그대로, 경로 강조, 관측 node 유지" if not msgs else "; ".join(msgs[:6])

        @check("12 interaction panel")
        def t_inter():
            msgs = []
            page.click(".ptabs button[data-ptab='inter']")
            for r in inter:
                a, b = r["mechanism A"], r["mechanism B"]
                page.select_option("#pair-a", a)
                page.select_option("#pair-b", b)
                page.wait_for_timeout(30)
                txt = page.inner_text("#p-inter")
                if r["coexistence"] not in txt or r["relation"].split("|")[0] not in txt:
                    msgs.append(f"{a}×{b} 판정 표시 다름")
            page.select_option("#pair-a", "M1")
            page.select_option("#pair-b", "M2")
            txt = page.inner_text("#p-inter")
            if "Audit 4" not in txt or "coexistence_undetermined" not in txt and "interaction_direction" not in txt:
                msgs.append("Audit 4 UNRESOLVED 표시 없음")
            for wtxt in ["V_INFO_TO_COMMANDER", "V_COMMAND_SOURCE"]:
                if wtxt not in txt:
                    msgs.append(f"{wtxt} 규칙 없음")
            if shots:
                page.screenshot(path=str(shots / "interaction.png"))
            return not msgs, f"공존 {len(inter)}쌍 판정·relation = CSV, Audit 4 UNRESOLVED·OR/XOR 규칙 표시" if not msgs else "; ".join(msgs[:5])

        @check("13 views 1–4")
        def t_views():
            msgs = []
            views = json.loads((DOCS / "data" / "views.json").read_text(encoding="utf-8"))["views"]
            for vid in ["overview", "investigation", "review", "death"]:
                page.click(f"#view-tabs button[data-view='{vid}']")
                page.wait_for_timeout(120)
                if page.get_attribute(f"#view-tabs button[data-view='{vid}']", "aria-selected") != "true":
                    msgs.append(f"{vid} 탭 선택 안 됨")
                v = visible_ids()
                want = set(views[vid]["nodes"])
                if not want <= v:
                    msgs.append(f"{vid}: view node 일부가 안 보임 {sorted(want - v)[:3]}")
                extra = {x for x in v - want if x not in observed}
                if extra:
                    msgs.append(f"{vid}: view 밖 비관측 node 표시 {sorted(extra)[:3]}")
                if not set(observed) <= v:
                    msgs.append(f"{vid}: 관측 node 사라짐")
                if shots:
                    page.screenshot(path=str(shots / f"view_{vid}.png"))
            if "A↔B 직접 edge 0개" not in page.inner_text("#view-desc"):
                msgs.append("질병·사망 view의 A↔B 0개 표시 없음")
            ga, gb = set(views["death"]["groups"]["A"]), set(views["death"]["groups"]["B"])
            cross = [e["edge_id"] for e in sd_edges if (e["src"] in ga and e["dst"] in gb) or (e["src"] in gb and e["dst"] in ga)]
            if cross:
                msgs.append(f"A↔B edge {cross}")
            page.click("#view-tabs button[data-view='overview']")
            return not msgs, "Overview·수사 확대·재검토·판단·처분·질병·사망 branch 전환, view node 표시, A/B 직접 edge 0" if not msgs else "; ".join(msgs[:5])

        @check("14 OBSERVED backbone 유지(world × view × 개입 × 필터)")
        def t_backbone():
            res = ev("""(() => { const V = window.__viz, cy = V.cy, bad = [];
                const obs = cy.nodes().filter(n => n.data('status') === 'OBSERVED').map(n => n.id());
                const worlds = ['ALL','W1','W2','W3','W4','W5','W6'], views = ['overview','investigation','review','death'];
                const ivs = [null,'M1','M2','M3','M4','M5','M6','MB']; let n = 0;
                document.getElementById('hide-others').click();
                for (const st of ['LATENT','CONTEXT','UNRESOLVED','DERIVED']) document.querySelector(`input[data-status='${st}']`).click();
                for (const m of ['M1','M5','MB']) document.querySelector(`input[data-mech='${m}']`).click();
                for (const w of worlds) for (const v of views) for (const iv of ivs) {
                  V.setWorld(w); V.setView(v); V.setIntervention(iv); n++;
                  for (const id of obs) { if (cy.getElementById(id).style('display') === 'none') bad.push(w + '/' + v + '/' + iv + '/' + id); }
                }
                V.reset(); return {n: n, bad: bad.slice(0, 5), nbad: bad.length, nobs: obs.length}; })()""")
            return res["nbad"] == 0 and res["nobs"] == len(observed), \
                f"{res['n']}개 조합(숨기기·필터 켠 상태) 모두 관측 node {res['nobs']}개 표시" + (f" — 실패 {res['bad']}" if res["nbad"] else "")

        @check("15 공통 결말 유지")
        def t_outcome():
            bad = []
            for wid in ["ALL", "W1", "W2", "W3", "W4", "W5", "W6"]:
                page.click(f"#world-buttons button[data-world='{wid}']")
                page.check("#hide-others")
                if not set(outcome) <= visible_ids():
                    bad.append(wid)
                page.uncheck("#hide-others")
            page.click("#world-buttons button[data-world='ALL']")
            return not bad, f"공통 결말 {len(outcome)}개(홍대협 안핵·정조 최종 판단·책임 판단·처분 등) 모든 world에서 표시" + (f" 실패 {bad}" if bad else "")

        @check("16 시간 순서(화면 좌표)")
        def t_temporal():
            pos = ev("Object.fromEntries(window.__viz.cy.nodes().map(n => [n.id(), n.position()]))")
            data = {n["id"]: n for n in json.loads((DOCS / "data" / "super_dag.json").read_text(encoding="utf-8"))["nodes"]}
            msgs = []
            moved = [k for k, v in pos.items() if (round(v["x"]), round(v["y"])) != (data[k]["layout"]["x"], data[k]["layout"]["y"])]
            if moved:
                msgs.append(f"좌표가 데이터와 다름 {moved[:3]}")
            key = {k: int(e["t_max"] or e["t_min"]) for k, e in eps.items() if (e["t_max"] or e["t_min"]) and k.startswith("EP")}
            ks = sorted(key)
            for a in ks:
                for b in ks:
                    if key[a] < key[b] and pos[a]["x"] >= pos[b]["x"]:
                        msgs.append(f"{a}({key[a]}) ≥ {b}({key[b]})")
            tt = {"TEMPORAL_BEFORE", "PROCEDURAL_NEXT", "ORDER_TO_ACTION", "REVIEW_OF", "REVISES", "INFORMATION_FLOW", "RESPONSIBILITY_LINK"}
            back = [e["edge_id"] for e in sd_edges if e["origin"] == "FROZEN" and e["edge_type"] in tt and e["src"] in key and e["dst"] in key
                    and pos[e["src"]]["x"] >= pos[e["dst"]]["x"]]
            if back:
                msgs.append(f"뒤로 가는 edge {back}")
            # node를 끌어도 움직이지 않는지
            before = ev("window.__viz.cy.getElementById('EP09').position()")
            click_node("EP09")
            r = ev("""(() => { const n = window.__viz.cy.getElementById('EP09'); const r = n.renderedPosition();
                const b = document.getElementById('cy').getBoundingClientRect(); return [b.left + r.x, b.top + r.y]; })()""")
            page.mouse.move(r[0], r[1])
            page.mouse.down()
            page.mouse.move(r[0] + 180, r[1] + 120, steps=6)
            page.mouse.up()
            after = ev("window.__viz.cy.getElementById('EP09').position()")
            if before != after:
                msgs.append("node가 끌려 움직임")
            return not msgs, f"날짜 있는 관측 node {len(ks)}개 x 단조 증가, frozen 시간·절차 edge 역행 0, node 고정(드래그 불가)" if not msgs else "; ".join(msgs[:5])

        @check("17 reset")
        def t_reset():
            page.click("#world-buttons button[data-world='W3']")
            page.click("#view-tabs button[data-view='review']")
            page.uncheck("input[data-status='LATENT']")
            page.click(".ptabs button[data-ptab='iv']")
            page.click("#p-iv button[data-iv='M2']")
            page.fill("#search", "EP1")
            page.click("#reset")
            page.wait_for_timeout(200)
            st = ev("window.__viz.getState()")
            ok = (st["world"] == "ALL" and st["view"] == "overview" and st["iv"] is None and not st["hideOthers"]
                  and visible_ids() == {n["node_id"] for n in sd_nodes} and ev("window.__viz.cy.$('.dim').length") == 0
                  and page.input_value("#search") == "" and page.is_checked("input[data-status='LATENT']"))
            return ok, "world·view·필터·개입·검색이 기본값으로 돌아오고 전체 node 표시"

        @check("18 file:// 열기(bundle.js)")
        def t_file():
            pg = browser.new_page(viewport={"width": 1280, "height": 900})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.goto((DOCS / "index.html").as_uri())
            pg.wait_for_function("window.__viz && window.__viz.cy")
            n = pg.evaluate("window.__viz.cy.nodes().length")
            pg.close()
            return n == len(sd_nodes) and not errs, f"file:// 에서 node {n}개, 오류 {len(errs)}"

        @check("19 좁은 화면(420px)")
        def t_narrow():
            pg = browser.new_page(viewport={"width": 420, "height": 860})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(url)
            pg.wait_for_function("window.__viz && window.__viz.cy")
            over = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            if shots:
                pg.screenshot(path=str(shots / "narrow.png"), full_page=False)
            pg.close()
            return over <= 0 and not errs, f"가로 넘침 {over}px, 오류 {len(errs)}"

        @check("20 console error 없음")
        def t_console():
            return not errors, "console error·page error·요청 실패 0" if not errors else "; ".join(errors[:5])

        for t in [t_load, t_json, t_counts, t_worlds, t_w6, t_status, t_mech, t_node_detail, t_edge_detail, t_search, t_iv,
                  t_inter, t_views, t_backbone, t_outcome, t_temporal, t_reset, t_file, t_narrow]:
            t()
        if shots:
            page.click("#reset")
            page.wait_for_timeout(300)
            page.screenshot(path=str(shots / "overview.png"))
        t_console()
        browser.close()
    srv.shutdown()
    fails = [r for r in RESULTS if not r[1]]
    print(f"\n[UI TEST] {len(RESULTS) - len(fails)}/{len(RESULTS)} PASS")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
