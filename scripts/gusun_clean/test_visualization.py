"""Interactive Temporal DAG(docs/) 헤드리스 브라우저 테스트.

실행(저장소 루트에서, build.py 실행 뒤):
    pip install playwright            # 한 번만. 브라우저가 없으면 `python3 -m playwright install chromium`
    python3 scripts/gusun_clean/test_visualization.py [--shots DIR]

docs/를 로컬 http 서버로 띄우고 Chromium으로 연다. 항목별 PASS/FAIL을 출력하고, 하나라도 실패하면 exit 1.
화면이 canonical 값을 그대로 보여 주는지(개수·configuration·후보 등급·개입 결과·공존 판정), OBSERVED backbone이
어떤 world·개입·필터에서도 사라지지 않는지(관점별 View의 숨김은 안내와 함께인지), 날짜 순서가 화면 좌표에서도 지켜지는지,
글자가 11pt·line-height 1.6 이상이고 node label이 잘리지 않는지, 첫 화면에서 label이 읽히는지 확인한다.
'DOM 요소가 있다'가 아니라 '화면 픽셀에 node가 그려졌다'를 본다: 첫 로드와 A–J 각 View에서 cytoscape 생성, 보이는 node가 화면 창과
겹치는지, canvas에 칠해진 픽셀, 그래프 영역 스크린샷이 흰색만이 아닌지, 옛 app.js가 캐시에서 섞여 초기화가 멈춰도 빈 흰 화면 대신
'시각화 초기화 오류'가 보이는지 확인한다.
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
        try:
            browser = p.chromium.launch()
        except Exception:  # noqa: BLE001 — Playwright 버전에 맞는 브라우저가 없으면 미리 설치된 Chromium 사용
            browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium"))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        page.on("requestfailed", lambda r: errors.append(f"requestfailed: {r.url}"))
        page.goto(url)
        try:
            page.wait_for_function("window.__viz && window.__viz.cy", timeout=10000)
        except Exception:  # noqa: BLE001 — 초기화 실패는 아래 '0 실제 렌더링' 검사가 FAIL로 기록한다
            pass
        page.wait_for_timeout(500)
        ev = page.evaluate
        boot_errors = list(errors)

        def render_probe(pg):
            """실제 화면 픽셀에 node가 그려졌는지: 보이는 node 수, 화면 창과 겹치는 node, 좌표 이상, cytoscape canvas에 칠해진 픽셀."""
            return pg.evaluate("""(() => {
              const v = window.__viz; if (!v || !v.cy) return {cy: false};
              const cy = v.cy, w = cy.width(), h = cy.height();
              const shown = cy.nodes().filter(n => n.style('display') !== 'none');
              const inView = shown.filter(n => { const b = n.renderedBoundingBox({includeLabels: false});
                return b.x2 > 0 && b.y2 > 0 && b.x1 < w && b.y1 < h; }).map(n => n.id());
              let bad = 0; cy.nodes().forEach(n => { const p = n.position();
                if (!Number.isFinite(p.x) || !Number.isFinite(p.y) || Math.abs(p.x) > 1e6 || Math.abs(p.y) > 1e6) bad++; });
              let painted = 0, total = 0;
              document.querySelectorAll('#cy canvas').forEach(c => { if (!c.width || !c.height) return;
                const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; total += d.length / 4;
                for (let i = 3; i < d.length; i += 16) if (d[i] > 0) painted += 4; });
              const el = document.getElementById('cy');
              return {cy: true, nodes: cy.nodes().length, edges: cy.edges().filter(e => !e.data('members')).length, visible: cy.nodes(':visible').length,
                      shown: shown.length, inView: inView.length, inViewIds: inView.slice(0, 6), badPos: bad,
                      painted: total ? painted / total : 0, w: el.offsetWidth, h: el.offsetHeight, zoom: cy.zoom(), pan: cy.pan(),
                      error: (() => { const e = document.getElementById('viz-error'); return e && !e.hidden ? e.textContent : ''; })()};
            })()""")

        def white_ratio(pg, sel="#cy"):
            """그래프 영역 스크린샷에서 거의 흰색(모든 채널 ≥ 245)인 픽셀 비율."""
            import io
            from PIL import Image
            img = Image.open(io.BytesIO(pg.locator(sel).screenshot())).convert("RGB")
            raw = img.tobytes()
            n = len(raw) // 3
            return sum(1 for i in range(0, len(raw), 3) if raw[i] >= 245 and raw[i + 1] >= 245 and raw[i + 2] >= 245) / max(1, n)

        def visible_ids(sel="node"):
            # visible()은 렌더 전까지 캐시될 수 있어 계산된 style(display)로 본다
            return set(ev(f"window.__viz.cy.$('{sel}').filter(e => e.style('display') !== 'none' && (e.isNode() || (e.source().style('display') !== 'none' && e.target().style('display') !== 'none'))).map(e => e.id())"))

        def classes(nid):
            return set(ev(f"window.__viz.cy.getElementById('{nid}').classes()"))

        def full():
            """기존 화면 기능 회귀 검사는 '전체' 표시 수준(예전 화면과 같은 node·edge 범위)에서 같은 기대값으로 돌린다."""
            ev("window.__viz.setLevel('full')")
            page.wait_for_timeout(60)

        def click_node(nid):
            pos = ev(f"""(() => {{ const cy = window.__viz.cy; const n = cy.getElementById('{nid}');
                cy.center(n); cy.zoom({{level: 1.0, position: n.position()}});
                const r = n.renderedPosition(); const b = document.getElementById('cy').getBoundingClientRect();
                return [b.left + r.x, b.top + r.y]; }})()""")
            page.wait_for_timeout(80)
            page.mouse.click(pos[0], pos[1])
            page.wait_for_timeout(120)

        @check("0 실제 렌더링(첫 로드: cy·개수·보이는 node·화면 창 교차·픽셀·필터 UI·View 탭·오류 0)")
        def t_render():
            r = render_probe(page)
            msgs = []
            if not r.get("cy"):
                return False, f"window.__viz.cy 없음 — 초기화 실패 ({'; '.join(boot_errors[:3]) or 'pageerror 없음'})"
            if r["nodes"] != len(sd_nodes) or r["edges"] != len(sd_edges):
                msgs.append(f"cy node {r['nodes']} / edge {r['edges']} ≠ {len(sd_nodes)} / {len(sd_edges)}")
            if r["visible"] <= 0 or r["shown"] <= 0:
                msgs.append(f"보이는 node {r['visible']}")
            if r["inView"] <= 0:
                msgs.append(f"화면 창과 겹치는 node 0 (zoom {r['zoom']:.2f}, pan {r['pan']})")
            if r["badPos"]:
                msgs.append(f"좌표 NaN·Infinity·극단값 node {r['badPos']}")
            if r["w"] <= 0 or r["h"] <= 0:
                msgs.append(f"그래프 영역 크기 {r['w']}×{r['h']}")
            if r["painted"] < 0.01:
                msgs.append(f"cytoscape canvas에 칠해진 픽셀 {r['painted']:.4f}")
            wr = white_ratio(page)
            if wr > 0.985:
                msgs.append(f"그래프 영역 스크린샷 {wr:.1%}가 흰색(빈 화면)")
            if r["error"]:
                msgs.append(f"오류 안내 표시: {r['error'][:60]}")
            st = page.locator("#status-filters input[data-status]").count()
            mf = page.locator("#mech-filters input[data-mech]").count()
            tabs = page.locator("#view-tabs [data-view]").count()
            nviews = len(json.loads((DOCS / "data" / "views.json").read_text(encoding="utf-8"))["order"])
            if st <= 0 or mf <= 0:
                msgs.append(f"Status 필터 {st}개 · Mechanism 필터 {mf}개")
            if tabs != nviews:
                msgs.append(f"View 탭 {tabs}개 ≠ {nviews}")
            if boot_errors:
                msgs.append("console·page error: " + "; ".join(boot_errors[:3]))
            if shots:
                page.screenshot(path=str(shots / "first_load.png"))
            return not msgs, (f"cy node {r['nodes']} · edge {r['edges']}, 보이는 node {r['visible']}, 첫 화면 창 안 node {r['inView']} "
                              f"({', '.join(r['inViewIds'])}), 좌표 이상 0, canvas 칠함 {r['painted']:.1%}, 흰 픽셀 {wr:.1%}, "
                              f"Status {st} · Mechanism {mf} · View 탭 {tabs}, 오류 0") if not msgs else "; ".join(msgs)

        @check("28 A–J 모든 View 실제 렌더링(보이는 node·화면 창 교차·좌표·픽셀)")
        def t_render_views():
            msgs, parts = [], []
            order = json.loads((DOCS / "data" / "views.json").read_text(encoding="utf-8"))["order"]
            n_err = len(errors)
            for i, vid in enumerate(order):
                ev(f"window.__viz.setView('{vid}')")
                page.wait_for_timeout(250)
                r = render_probe(page)
                wr = white_ratio(page)
                if r["shown"] <= 0 or r["inView"] <= 0 or r["badPos"] or r["painted"] < 0.01 or wr > 0.985 or r["error"]:
                    msgs.append(f"{vid}: 보이는 {r['shown']} · 창 안 {r['inView']} · 좌표 이상 {r['badPos']} · 칠함 {r['painted']:.3f} · 흰색 {wr:.1%} {r['error'][:30]}")
                parts.append(f"{'ABCDEFGHIJ'[i]} {vid} {r['shown']}/{r['inView']}")
                if shots:
                    page.screenshot(path=str(shots / f"render_{'ABCDEFGHIJ'[i]}_{vid}.png"))
            ev("window.__viz.setView('overview')")
            if len(errors) > n_err:
                msgs.append("JS 오류: " + "; ".join(errors[n_err:n_err + 3]))
            return not msgs, ("View별 보이는 node/첫 화면 창 안 node — " + ", ".join(parts) + ", JS 오류 0") if not msgs else "; ".join(msgs[:5])

        @check("29 배포 캐시 섞임 방지: css·js 주소 ?v=내용 해시, 옛 app.js가 멈추면 '시각화 초기화 오류' 표시")
        def t_stale():
            import hashlib
            import re as _re
            msgs = []
            html = page.content()
            for rel in ["css/app.css", "vendor/cytoscape/cytoscape.min.js", "data/bundle.js", "js/app.js"]:
                m = _re.search(_re.escape(rel) + r"\?v=([0-9a-f]+)", html)
                want = hashlib.sha256((DOCS / rel).read_bytes()).hexdigest()[:12]
                if not m or m.group(1) != want:
                    msgs.append(f"{rel}?v={m.group(1) if m else '(없음)'} ≠ {want}")
            # 25f81b6 배포 직후 상황 재현: 새 index.html + 캐시된 옛 app.js(없어진 #foot-note에 글자를 넣다가 멈춤)
            js = (DOCS / "js" / "app.js").read_text(encoding="utf-8").replace(
                "  // ------------------------------------------------------------------ cytoscape 요소",
                "  $('foot-note').textContent = META.role_note;\n  // ------------------------------------------------------------------ cytoscape 요소", 1)
            pg = browser.new_page(viewport={"width": 1440, "height": 900})
            perr = []
            pg.on("pageerror", lambda e: perr.append(str(e)))
            pg.route("**/js/app.js*", lambda route: route.fulfill(body=js, content_type="application/javascript"))
            pg.goto(url)
            pg.wait_for_timeout(500)
            shown = pg.is_visible("#viz-error")
            text = pg.inner_text("#viz-error") if shown else ""
            if not perr:
                msgs.append("옛 app.js 재현이 오류를 내지 않음")
            if not shown or "시각화 초기화 오류" not in text:
                msgs.append(f"오류 안내 없음(빈 흰 화면) {text[:40]!r}")
            if shots:
                pg.screenshot(path=str(shots / "stale_app_js_guard.png"))
            pg.close()
            return not msgs, f"index.html의 css·js 4개 주소 ?v= = 현재 내용 해시. 옛 app.js 재현(pageerror '{perr[0] if perr else ''}') → 그래프 영역에 '시각화 초기화 오류' 표시" if not msgs else "; ".join(msgs)

        @check("30 보이는 node 0인 View → 안내 후 Overview로 1회 복구")
        def t_empty_guard():
            pg = browser.new_page(viewport={"width": 1440, "height": 900})
            perr = []
            pg.on("pageerror", lambda e: perr.append(str(e)))
            pg.goto(url)
            pg.wait_for_function("window.__viz && window.__viz.cy")
            # 화면 메모리 사본에서만 I View 범위를 비운다(파일·canonical 변경 없음)
            pg.evaluate("(() => { const v = window.__viz.data.views.views.final; v.nodes = []; v.core = []; })()")
            pg.evaluate("window.__viz.setView('final')")
            pg.wait_for_timeout(300)
            text = pg.inner_text("#viz-error") if pg.is_visible("#viz-error") else ""
            st = pg.evaluate("window.__viz.getState().view")
            r = render_probe(pg)
            if shots:
                pg.screenshot(path=str(shots / "empty_view_guard.png"))
            pg.close()
            ok = "현재 View에서 표시할 그래프를 찾지 못했습니다" in text and "Overview로 복구" in text and st == "overview" and r["inView"] > 0 and not perr
            return ok, f"안내 '{text[:34]}…', 복구 후 View={st}, 첫 화면 창 안 node {r['inView']}, pageerror {len(perr)}"

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
            n, e = ev("window.__viz.cy.nodes().length"), ev("window.__viz.cy.edges().filter(e => !e.data('members')).length")
            return n == len(sd_nodes) and e == len(sd_edges), f"화면 node {n} / edge {e}, canonical {len(sd_nodes)} / {len(sd_edges)}"

        @check("4 W1–W5 선택")
        def t_worlds():
            msgs = []
            full()
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
                    if f"\n{wid}: {configs[wid][m]}" not in lab:
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
            full()
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
            full()
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
            full()
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

        VIEWS = json.loads((DOCS / "data" / "views.json").read_text(encoding="utf-8"))
        VORDER = VIEWS["order"]
        SUBSET = [v for v in VORDER if VIEWS["views"][v]["policy"] == "subset"]
        TYPO = json.loads((DOCS / "data" / "meta.json").read_text(encoding="utf-8"))["typography"]
        READ_PX = 11 * 96 / 72 - 0.01

        def set_view(vid):
            page.click(f"#view-tabs button[data-view='{vid}']")
            page.wait_for_timeout(150)

        @check("13 View A–J 전환·표시 범위")
        def t_views():
            msgs = []
            full()
            for vid in VORDER:
                set_view(vid)
                v = VIEWS["views"][vid]
                if page.get_attribute(f"#view-tabs button[data-view='{vid}']", "aria-selected") != "true":
                    msgs.append(f"{vid} 탭 선택 안 됨")
                vis = visible_ids()
                want = set(v["nodes"])
                if v["policy"] == "subset":
                    if vis != want:
                        msgs.append(f"{vid}: 보이는 node ≠ View node (+{sorted(vis - want)[:3]} −{sorted(want - vis)[:3]})")
                    ve = visible_ids("edge")
                    if ve != set(v["edges"]):
                        msgs.append(f"{vid}: 보이는 edge ≠ View edge ({len(ve)} vs {len(v['edges'])})")
                    cnt = page.inner_text("#hidden-observed-count") if page.locator("#hidden-observed-count").count() else ""
                    if cnt != str(len(v["hidden_observed"])) or "시각적 필터" not in page.inner_text("#banner-view"):
                        msgs.append(f"{vid}: 숨긴 OBSERVED 안내 없음/다름({cnt})")
                    if "분석상 ON/OFF 아님" not in page.inner_text("#banner-view"):
                        msgs.append(f"{vid}: 시각적 필터 문구 없음")
                    pos = ev("Object.fromEntries(window.__viz.cy.nodes().filter(n => n.style('display') !== 'none').map(n => [n.id(), n.position()]))")
                    moved = [k for k, p in pos.items() if (round(p["x"]), round(p["y"])) != (v["layout"]["positions"][k]["x"], v["layout"]["positions"][k]["y"])]
                    if moved:
                        msgs.append(f"{vid}: 좌표가 View 데이터와 다름 {moved[:3]}")
                else:
                    if not set(observed) <= vis:
                        msgs.append(f"{vid}: 관측 node 사라짐")
                    if vid == "overview" and vis != {n["node_id"] for n in sd_nodes}:
                        msgs.append("overview: 전체 node가 보이지 않음")
                if shots:
                    page.screenshot(path=str(shots / f"view_{vid}.png"))
            set_view("death")
            if "A↔B 직접 edge 0개" not in page.inner_text("#view-desc"):
                msgs.append("구금·사망 View의 A↔B 0개 표시 없음")
            ga, gb = set(VIEWS["views"]["death"]["groups"]["A"]), set(VIEWS["views"]["death"]["groups"]["B"])
            cross = [e["edge_id"] for e in sd_edges if (e["src"] in ga and e["dst"] in gb) or (e["src"] in gb and e["dst"] in ga)]
            if cross:
                msgs.append(f"A↔B edge {cross}")
            set_view("overview")
            return not msgs, f"View {len(VORDER)}개 전환: subset {len(SUBSET)}개는 View node·edge만 표시(숨긴 OBSERVED 수 안내), Overview·J는 관측 node 전부, A/B 직접 edge 0" if not msgs else "; ".join(msgs[:6])

        @check("14 OBSERVED backbone 유지(world × view × 개입 × 필터)")
        def t_backbone():
            res = ev("""(() => { const V = window.__viz, cy = V.cy, D = V.data, bad = [];
                const obs = cy.nodes().filter(n => n.data('status') === 'OBSERVED').map(n => n.id());
                const worlds = ['ALL','W1','W2','W3','W4','W5','W6'], views = D.views.order;
                const ivs = [null,'M1','M2','M3','M4','M5','M6','MB']; let n = 0;
                document.getElementById('hide-others').click();
                for (const st of ['LATENT','CONTEXT','UNRESOLVED','DERIVED']) document.querySelector(`input[data-status='${st}']`).click();
                for (const m of ['M1','M5','MB']) document.querySelector(`input[data-mech='${m}']`).click();
                for (const lv of ['simple', 'full']) for (const w of worlds) for (const v of views) for (const iv of ivs) for (const ctx of (D.views.views[v].policy === 'subset' ? [false, true] : [false])) {
                  V.setLevel(lv); V.setWorld(w); V.setView(v); if (ctx) V.setShowContext(true); V.setIntervention(iv); V.setFocusMech(iv ? 'MB' : null); n++;
                  const scope = D.views.views[v].policy === 'subset' && !ctx ? new Set(D.views.views[v].nodes) : null;
                  for (const id of obs) {
                    const shown = cy.getElementById(id).style('display') !== 'none';
                    if (scope ? (scope.has(id) !== shown) : !shown) bad.push(w + '/' + v + (ctx ? '+ctx' : '') + '/' + iv + '/' + id);
                  }
                }
                V.reset(); return {n: n, bad: bad.slice(0, 5), nbad: bad.length, nobs: obs.length}; })()""")
            return res["nbad"] == 0 and res["nobs"] == len(observed), \
                f"{res['n']}개 조합(표시 수준 간단히·전체 × world × View × 개입 × 메커니즘 펼치기, 숨기기·필터 켠 상태): Overview·J·전체 맥락 표시에서는 관측 node {res['nobs']}개 전부, subset View에서는 View 범위의 관측 node 전부 표시(필터·world·개입이 숨기지 않음)" + (f" — 실패 {res['bad']}" if res["nbad"] else "")

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

        @check("16 시간 순서(화면 좌표, Overview·View별)")
        def t_temporal():
            data = {n["id"]: n for n in json.loads((DOCS / "data" / "super_dag.json").read_text(encoding="utf-8"))["nodes"]}
            msgs = []
            key = {k: int(e["t_max"] or e["t_min"]) for k, e in eps.items() if (e["t_max"] or e["t_min"]) and k.startswith("EP")}
            tt = {"TEMPORAL_BEFORE", "PROCEDURAL_NEXT", "ORDER_TO_ACTION", "REVIEW_OF", "REVISES", "INFORMATION_FLOW", "RESPONSIBILITY_LINK"}
            for vid in ["overview"] + SUBSET:
                set_view(vid)
                pos = ev("Object.fromEntries(window.__viz.cy.nodes().filter(n => n.style('display') !== 'none').map(n => [n.id(), n.position()]))")
                if vid == "overview":
                    moved = [k for k, v in pos.items() if (round(v["x"]), round(v["y"])) != (data[k]["layout"]["x"], data[k]["layout"]["y"])]
                    if moved:
                        msgs.append(f"좌표가 데이터와 다름 {moved[:3]}")
                ks = sorted(k for k in key if k in pos)
                for a in ks:
                    for b in ks:
                        if key[a] < key[b] and pos[a]["x"] >= pos[b]["x"]:
                            msgs.append(f"{vid}: {a}({key[a]}) ≥ {b}({key[b]})")
                back = [e["edge_id"] for e in sd_edges if e["origin"] == "FROZEN" and e["edge_type"] in tt and e["src"] in pos and e["dst"] in pos
                        and e["src"] in key and e["dst"] in key and pos[e["src"]]["x"] >= pos[e["dst"]]["x"]]
                if back:
                    msgs.append(f"{vid}: 뒤로 가는 edge {back}")
            set_view("overview")
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
            return not msgs, f"Overview + subset View {len(SUBSET)}개: 날짜 있는 관측 node x 단조 증가, frozen 시간·절차 edge 역행 0, node 고정(드래그 불가)" if not msgs else "; ".join(msgs[:5])

        @check("17 reset")
        def t_reset():
            page.click("#world-buttons button[data-world='W3']")
            set_view("may_review")
            page.uncheck("input[data-status='LATENT']")
            page.click(".ptabs button[data-ptab='iv']")
            page.click("#p-iv button[data-iv='M2']")
            page.fill("#search", "EP1")
            page.click("#reset")
            page.wait_for_timeout(200)
            st = ev("window.__viz.getState()")
            ok = (st["world"] == "ALL" and st["view"] == "overview" and st["iv"] is None and not st["hideOthers"] and not st["showContext"]
                  and st["level"] == "simple" and st["hops"] == 1 and st["sel"] is None and st["focusMech"] is None
                  and visible_ids() == set(observed) and ev("window.__viz.cy.$('.dim').length") == 0
                  and page.input_value("#search") == "" and page.is_checked("input[data-status='LATENT']"))
            full()
            ok = ok and visible_ids() == {n["node_id"] for n in sd_nodes}
            return ok, "world·view·필터·개입·검색·표시 수준이 기본값(간단히·1-hop)으로 돌아오고 관측 사건 전부 표시, '전체'로 바꾸면 전체 node 표시"

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

        FONT_JS = """((minPx) => { const bad = []; let n = 0;
            const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            const seen = new Set();
            while (walk.nextNode()) {
              const t = walk.currentNode; if (!t.textContent.trim()) continue;
              const el = t.parentElement; if (!el || seen.has(el)) continue; seen.add(el);
              if (el.closest('[hidden]') || el.closest('svg') || el.tagName === 'OPTION' || el.tagName === 'SCRIPT' || el.tagName === 'STYLE') continue;
              const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
              const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
              const fs = parseFloat(cs.fontSize), lh = cs.lineHeight === 'normal' ? 0 : parseFloat(cs.lineHeight);
              n++;
              if (fs < minPx || lh / fs < 1.599) bad.push(el.tagName + '.' + el.className + ' fs=' + fs + ' lh=' + cs.lineHeight + ' "' + t.textContent.trim().slice(0, 20) + '"');
            }
            return {n: n, bad: bad.slice(0, 8), nbad: bad.length}; })""" + f"({READ_PX})"

        def font_check(pg, label):
            msgs, total = [], 0
            states = [("detail", None), ("world", None), ("inter", None), ("iv", None)]
            for pane, _ in states:
                pg.click(f".ptabs button[data-ptab='{pane}']")
                pg.wait_for_timeout(60)
                r = pg.evaluate(FONT_JS)
                total += r["n"]
                if r["nbad"]:
                    msgs.append(f"{label}/{pane}: {r['nbad']}개 {r['bad'][:3]}")
            pg.fill("#search", "김명신")
            pg.wait_for_timeout(80)
            r = pg.evaluate(FONT_JS)
            total += r["n"]
            if r["nbad"]:
                msgs.append(f"{label}/검색결과: {r['bad'][:3]}")
            pg.fill("#search", "")
            pg.evaluate("window.__viz.focusNode('EP23')")
            pg.wait_for_timeout(80)
            r = pg.evaluate(FONT_JS)
            total += r["n"]
            if r["nbad"]:
                msgs.append(f"{label}/node 상세: {r['bad'][:3]}")
            pg.evaluate("window.__viz.reset()")
            return msgs, total

        @check("19 UI 글자 크기 ≥ 11pt · line-height ≥ 160% (computed)")
        def t_fonts():
            msgs, total = font_check(page, "desktop")
            st = ev("""(() => { const n = window.__viz.cy.getElementById('EP23'), e = window.__viz.cy.getElementById('OE050');
                return [parseFloat(n.style('font-size')), parseFloat(n.style('line-height')), parseFloat(e.style('font-size'))]; })()""")
            if st[0] < READ_PX or st[1] < 1.6 or st[2] < READ_PX:
                msgs.append(f"그래프 label font {st}")
            return not msgs, f"보이는 글자 요소 {total}개(패널 4종·검색 결과·상세) 모두 ≥ 14.67px(11pt), line-height/font-size ≥ 1.6; node label {st[0]}px·line-height {st[1]}, edge label {st[2]}px" if not msgs else "; ".join(msgs[:4])

        LABEL_JS = """(() => { const cy = window.__viz.cy, bad = [], over = []; let n = 0;
            const vis = cy.nodes().filter(x => x.style('display') !== 'none');
            const boxes = vis.map(x => [x.id(), x.boundingBox({includeLabels: false, includeOverlays: false, includeUnderlays: false})]);
            vis.forEach(x => {
              n++;
              const b = x.boundingBox({includeLabels: false, includeOverlays: false, includeUnderlays: false});
              const l = x.boundingBox({includeNodes: false, includeEdges: false, includeLabels: true, includeOverlays: false, includeUnderlays: false});
              if (l.x1 < b.x1 - 0.5 || l.x2 > b.x2 + 0.5 || l.y1 < b.y1 - 0.5 || l.y2 > b.y2 + 0.5)
                bad.push(x.id() + ' label ' + [l.x1, l.y1, l.x2, l.y2].map(Math.round) + ' node ' + [b.x1, b.y1, b.x2, b.y2].map(Math.round));
            });
            for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
              const a = boxes[i][1], c = boxes[j][1];
              const ox = Math.min(a.x2, c.x2) - Math.max(a.x1, c.x1), oy = Math.min(a.y2, c.y2) - Math.max(a.y1, c.y1);
              if (ox > 2 && oy > 2) over.push(boxes[i][0] + '×' + boxes[j][0]);
            }
            return {n: n, bad: bad.slice(0, 5), nbad: bad.length, over: over.slice(0, 5), nover: over.length,
                    far: cy.nodes().filter(x => x.hasClass('far')).length}; })()"""

        @check("20 node label clipping 없음 · node 겹침 없음 (View별 렌더링)")
        def t_labels():
            msgs, total = [], 0
            full()
            for vid in VORDER:
                set_view(vid)
                if ev("window.__viz.cy.zoom()") < TYPO["read_zoom"]:
                    ev("window.__viz.cy.zoom(1)")
                r = ev(LABEL_JS)
                total += r["n"]
                if r["far"]:
                    msgs.append(f"{vid}: 축소 지도 모드라 전체 label 검사 불가")
                if r["nbad"]:
                    msgs.append(f"{vid}: label이 node 밖 {r['nbad']}개 {r['bad'][:2]}")
                if r["nover"]:
                    msgs.append(f"{vid}: node 겹침 {r['nover']}개 {r['over'][:3]}")
            # world·개입 표시 줄이 붙은 메커니즘 node도 잘리지 않는지
            set_view("overview")
            ev("window.__viz.setWorld('W5'); window.__viz.setIntervention('M3')")
            r = ev(LABEL_JS)
            if r["nbad"] or r["nover"]:
                msgs.append(f"W5 + do(M3): label 밖 {r['bad'][:2]} 겹침 {r['over'][:2]}")
            ev("window.__viz.reset()")
            return not msgs, f"View {len(VORDER)}개의 보이는 node {total}개: 렌더된 label 상자가 모두 node 상자 안(잘림·말줄임 없음), node 상자 겹침 0. world 값·do() 줄이 붙어도 같음" if not msgs else "; ".join(msgs[:5])

        @check("21 첫 화면에서 label이 읽히는 배율 (View별)")
        def t_initial():
            msgs, rows = [], []
            for vid in VORDER:
                set_view(vid)
                r = ev("""(() => { const cy = window.__viz.cy, z = cy.zoom(), W = cy.width(), H = cy.height();
                    const inv = cy.nodes().filter(n => n.style('display') !== 'none' && !n.hasClass('dim')).filter(n => {
                      const b = n.renderedBoundingBox({includeLabels: false}); return b.x1 >= 0 && b.y1 >= 0 && b.x2 <= W && b.y2 <= H; });
                    const svg = Array.from(document.querySelectorAll('#overlay text')).map(t => parseFloat(t.getAttribute('font-size')) * z);
                    return {z: z, px: parseFloat(cy.nodes()[0].style('font-size')) * z, inview: inv.map(n => n.id()), svgMin: Math.min.apply(null, svg),
                            far: cy.nodes().filter(n => n.hasClass('far')).length}; })()""")
                rows.append(f"{vid} {r['z']:.2f}×→{r['px']:.1f}px/{len(r['inview'])}개")
                if r["px"] < READ_PX or r["far"]:
                    msgs.append(f"{vid}: 첫 화면 node 글자 {r['px']:.1f}px")
                if r["svgMin"] < READ_PX:
                    msgs.append(f"{vid}: lane·시간 구간 글자 {r['svgMin']:.1f}px")
                core = set(VIEWS["views"][vid]["core"])
                if len(set(r["inview"]) & core) < min(2, len(core)):
                    msgs.append(f"{vid}: 첫 화면에 온전히 보이는 핵심 node {len(set(r['inview']) & core)}개")
            set_view("overview")
            return not msgs, "첫 화면 배율·node 글자·화면 안 node 수 — " + ", ".join(rows) if not msgs else "; ".join(msgs[:5])

        @check("22 검색 → 읽히는 배율로 이동·중앙·관련 edge 강조·상세 열림")
        def t_search_ux():
            msgs = []
            for vid, q in [("overview", "EP23"), ("may_review", "EP33"), ("barracks", "G02a")]:
                set_view(vid)
                page.fill("#search", q)
                page.wait_for_timeout(60)
                page.press("#search", "Enter")
                page.wait_for_timeout(250)
                r = ev(f"""(() => {{ const cy = window.__viz.cy, n = cy.getElementById('{q}'), p = n.renderedPosition();
                    const inc = n.connectedEdges().filter(e => e.style('display') !== 'none');
                    return {{z: cy.zoom(), px: parseFloat(n.style('font-size')) * cy.zoom(), dx: Math.abs(p.x - cy.width() / 2), dy: Math.abs(p.y - cy.height() / 2),
                            shown: n.style('display') !== 'none', sel: n.selected(),
                            inc: inc.length, incHl: inc.filter(e => e.hasClass('sel-in') || e.hasClass('sel-out')).length,
                            faded: cy.edges().difference(n.connectedEdges()).filter(e => e.hasClass('faded')).length,
                            others: cy.edges().difference(n.connectedEdges()).length, view: window.__viz.getState().view}}; }})()""")
                d = page.inner_text("#p-detail")
                if not r["shown"] or not r["sel"]:
                    msgs.append(f"{q}: 표시·선택 안 됨")
                if r["px"] < 1.1 * 16 - 0.01:
                    msgs.append(f"{q}: 이동 뒤 글자 {r['px']:.1f}px")
                if r["dx"] > 4 or r["dy"] > 4:
                    msgs.append(f"{q}: 중앙에서 {r['dx']:.0f},{r['dy']:.0f}px 떨어짐")
                if r["incHl"] != r["inc"] or r["faded"] != r["others"]:
                    msgs.append(f"{q}: 관련 edge 강조 {r['incHl']}/{r['inc']}, 흐림 {r['faded']}/{r['others']}")
                if q not in d or page.is_hidden("#p-detail"):
                    msgs.append(f"{q}: 상세 패널 미표시")
                if vid == "may_review" and r["view"] != "overview":
                    msgs.append("View 밖 node 검색 시 Overview로 전환 안 됨")
                if shots and q == "EP23":
                    page.screenshot(path=str(shots / "search_EP23.png"))
            page.fill("#search", "")
            ev("window.__viz.reset()")
            return not msgs, "EP23(Overview)·EP33(5월 재검토 View 밖 → Overview)·G02a(병영 View): 배율 ≥ 1.15(글자 ≥ 18px), 화면 중앙, 들어오고 나가는 edge 강조·나머지 흐림, 상세 패널 열림" if not msgs else "; ".join(msgs[:5])

        @check("23 Desktop 스크롤·이동·확대 (휠·Shift+휠·Ctrl+휠·끌기·미니맵)")
        def t_pan():
            msgs = []
            set_view("overview")
            box = page.locator("#graph-wrap").bounding_box()
            cx, cy_ = box["x"] + box["width"] * 0.6, box["y"] + box["height"] * 0.5
            vp = lambda: ev("({z: window.__viz.cy.zoom(), x: window.__viz.cy.pan().x, y: window.__viz.cy.pan().y, sy: window.scrollY})")
            a = vp()
            page.mouse.move(cx, cy_)
            page.mouse.wheel(0, 400)
            page.wait_for_timeout(120)
            b = vp()
            if not (abs(b["y"] - (a["y"] - 400)) < 1 and b["z"] == a["z"] and b["sy"] == a["sy"]):
                msgs.append(f"휠 세로 스크롤 {a} → {b}")
            page.keyboard.down("Shift")
            page.mouse.wheel(0, 300)
            page.keyboard.up("Shift")
            page.wait_for_timeout(120)
            c = vp()
            if not (abs(c["x"] - (b["x"] - 300)) < 1 and c["z"] == b["z"]):
                msgs.append(f"Shift+휠 가로 스크롤 {b} → {c}")
            page.keyboard.down("Control")
            page.mouse.wheel(0, -200)
            page.keyboard.up("Control")
            page.wait_for_timeout(150)
            d = vp()
            if not d["z"] > c["z"]:
                msgs.append(f"Ctrl+휠 확대 안 됨 {c['z']} → {d['z']}")
            ev("window.__viz.initialViewport()")
            e0 = vp()
            # 빈 배경 끌기: 첫 화면 왼쪽 위 lane 이름 칸 쪽에서 시작
            sx, sy = box["x"] + 30, box["y"] + 60
            page.mouse.move(sx, sy)
            page.mouse.down()
            page.mouse.move(sx + 150, sy + 90, steps=8)
            page.mouse.up()
            page.wait_for_timeout(120)
            e1 = vp()
            if abs((e1["x"] - e0["x"]) - 150) > 2 or abs((e1["y"] - e0["y"]) - 90) > 2:
                msgs.append(f"끌기 이동 {e0} → {e1}")
            if page.get_attribute("#toggle-minimap", "aria-pressed") != "true":
                page.click("#toggle-minimap")
            mmb = page.locator("#minimap").bounding_box()
            page.mouse.click(mmb["x"] + mmb["width"] * 0.8, mmb["y"] + mmb["height"] * 0.8)
            page.wait_for_timeout(120)
            f = vp()
            if f["x"] == e1["x"] and f["y"] == e1["y"]:
                msgs.append("미니맵 클릭 이동 안 됨")
            page.click("#zoom-fit")
            g_ = vp()
            far = ev("window.__viz.cy.nodes().filter(n => n.hasClass('far')).length")
            info = page.inner_text("#zoom-info")
            if not (g_["z"] < TYPO["read_zoom"] and far == len(sd_nodes) and "ID만" in info):
                msgs.append(f"전체 지도: zoom {g_['z']:.2f}, far {far}, '{info}'")
            page.click("#zoom-read")
            h_ = vp()
            if h_["z"] < 1:
                msgs.append(f"읽기 배율 {h_['z']}")
            page.click("#zoom-home")
            ev("window.__viz.reset()")
            return not msgs, "휠 = 세로 스크롤(배율·페이지 스크롤 그대로), Shift+휠 = 가로, Ctrl+휠 = 확대, 끌기 = 이동, 미니맵 클릭 = 이동, 전체 지도 = ID만 표시 안내, 읽기 배율 = 100%" if not msgs else "; ".join(msgs[:5])

        @check("24 전체 주변 맥락 표시(시각적 필터 해제)")
        def t_context():
            msgs = []
            set_view("barracks")
            v = VIEWS["views"]["barracks"]
            page.check("#show-context")
            page.wait_for_timeout(200)
            vis = visible_ids()
            if vis != {n["node_id"] for n in sd_nodes}:
                msgs.append(f"전체 node 표시 안 됨 ({len(vis)})")
            dimmed = set(ev("window.__viz.cy.nodes('.dim').map(n => n.id())"))
            if not (set(v["hidden_observed"]) <= dimmed) or dimmed & set(v["nodes"]):
                msgs.append("View 밖 node 흐림/View node 강조가 다름")
            if "흐리게" not in page.inner_text("#banner-view"):
                msgs.append("맥락 표시 안내 없음")
            if shots:
                page.screenshot(path=str(shots / "view_barracks_context.png"))
            page.uncheck("#show-context")
            page.wait_for_timeout(200)
            if visible_ids() != set(v["nodes"]):
                msgs.append("다시 끈 뒤 View 범위로 돌아오지 않음")
            set_view("overview")
            return not msgs, f"병영 View: 켜면 전체 {len(sd_nodes)}개 표시(View 밖 OBSERVED {len(v['hidden_observed'])}개 포함, 흐리게), 끄면 View node {len(v['nodes'])}개로 복귀" if not msgs else "; ".join(msgs)

        @check("25 상세 패널 구성(node·edge)")
        def t_detail_sections():
            msgs = []
            for nid, wants in [("EP23", ["EP23", "OBSERVED", "canonical summary", "Source fact ID", "CF", "관련 edge", "관련 Mechanism", "관련 World", "UNRESOLVED 의존", "날짜"]),
                               ("EP07", ["UNRESOLVED 의존", "U_OE007"]),
                               ("G04b", ["사료에 직접 적힌 사실이 아니라 빈칸을 설명하기 위한 가설", "U_OE007", "관련 World"]),
                               ("ENV03", ["사건 발생 자체를 증명하지 않음"]), ("CTX_F007", ["사건 발생 자체를 증명하지 않음"]),
                               ("M2", ["World configuration", "UNSPECIFIED ≠ OFF"])]:
                ev(f"window.__viz.focusNode('{nid}')")
                page.wait_for_timeout(80)
                d = page.inner_text("#p-detail")
                miss = [w for w in wants if w not in d]
                if miss:
                    msgs.append(f"{nid}: {miss}")
            ev("window.__viz.focusEdge('OE007')")
            page.wait_for_timeout(80)
            d = page.inner_text("#p-detail")
            miss = [w for w in ["OE007", "CONTRADICTS_AT_CLAIM_LEVEL", "DERIVED", "source basis", "caution"] if w not in d]
            if miss:
                msgs.append(f"OE007: {miss}")
            ev("window.__viz.focusEdge('SD058')")
            d = page.inner_text("#p-detail")
            if "LATENT 분석 edge" not in d:
                msgs.append("SD058 caution 없음")
            if shots:
                page.screenshot(path=str(shots / "detail_edge.png"))
            ev("window.__viz.reset()")
            return not msgs, "node: ID·status·날짜·label·canonical summary·CF ID·관련 edge·Mechanism·World·UNRESOLVED 의존, LATENT·CONTEXT 경고; edge: ID·type·status·source basis·caution" if not msgs else "; ".join(msgs[:5])

        @check("26 좁은 화면(420px): 글자 그대로·가로 넘침 없음·사용 가능")
        def t_narrow():
            pg = browser.new_page(viewport={"width": 420, "height": 860})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.goto(url)
            pg.wait_for_function("window.__viz && window.__viz.cy")
            msgs = []
            over = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            if over > 0:
                msgs.append(f"가로 넘침 {over}px")
            fm, total = font_check(pg, "420px")
            msgs += fm
            gw = pg.evaluate("window.__viz.cy.width()")
            if gw < 300:
                msgs.append(f"그래프 폭 {gw}px")
            for vid in ["timeline", "death", "final"]:
                pg.evaluate(f"window.__viz.setView('{vid}')")
                pg.wait_for_timeout(120)
                r = pg.evaluate("(() => { const cy = window.__viz.cy; return {px: parseFloat(cy.nodes()[0].style('font-size')) * cy.zoom(), far: cy.nodes('.far').length}; })()")
                if r["px"] < READ_PX or r["far"]:
                    msgs.append(f"420px {vid}: node 글자 {r['px']:.1f}px")
                over = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                if over > 0:
                    msgs.append(f"420px {vid}: 가로 넘침 {over}px")
                if shots:
                    pg.locator("#graph-wrap").scroll_into_view_if_needed()
                    pg.screenshot(path=str(shots / f"narrow_{vid}.png"))
            pg.evaluate("window.__viz.setView('overview')")
            if shots:
                pg.evaluate("window.scrollTo(0, 0)")
                pg.screenshot(path=str(shots / "narrow.png"), full_page=False)
            pg.close()
            return not msgs and not errs, f"가로 넘침 0px, 보이는 글자 {total}개 모두 ≥ 11pt·line-height ≥ 1.6, 그래프 폭 {gw}px, View 첫 화면 node 글자 ≥ 11pt, 오류 {len(errs)}" if not msgs and not errs else "; ".join((msgs + errs)[:5])

        # ------------------------------------------------------------------ 간단히 보기(시각화 UX 간소화) 검사
        META_J = json.loads((DOCS / "data" / "meta.json").read_text(encoding="utf-8"))
        SVJ = META_J["simple_view"]
        SPEC = {"record": {"INFORMATION_FLOW", "ORDER_TO_ACTION", "PROCEDURAL_NEXT", "RESPONSIBILITY_LINK", "REVIEW_OF", "REVISES",
                           "TEMPORAL_BEFORE", "CONTRADICTS_AT_CLAIM_LEVEL"},
                "analysis": {"ANCHORED_TO", "CONDITIONS", "CONTRIBUTES_TO", "EXPLAINS_OBSERVED", "EXPLAINS_TRANSITION_TO", "INSTANTIATED_BY",
                             "INSTANTIATED_BY_SECONDARY", "RULE_INPUT"},
                "context": {"CONTEXT_SUPPORTS", "CONSTRAINS", "CONTEXT_COMPATIBLE"}}
        ntype = {n["node_id"]: n["node_type"] for n in sd_nodes}
        nstat = {n["node_id"]: n["sd_status"] for n in sd_nodes}

        def py_redundant(edges, types=("TEMPORAL_BEFORE",)):
            """화면 코드와 따로 계산: 같은 추이적 유형만으로 된 길이 ≥ 2 경로가 있는 직접 edge."""
            out = set()
            for t in types:
                es = [e for e in edges if e["edge_type"] == t]
                succ = {}
                for e in es:
                    succ.setdefault(e["src"], []).append(e["dst"])
                for e in es:
                    stack, seen = [x for x in succ.get(e["src"], []) if x != e["dst"]], set()
                    while stack:
                        x = stack.pop()
                        if x == e["dst"]:
                            out.add(e["edge_id"])
                            break
                        if x in seen or x == e["src"]:
                            continue
                        seen.add(x)
                        stack += succ.get(x, [])
            return out

        def py_core(edges):
            red = py_redundant(edges)
            return {e["edge_id"] for e in edges if ntype.get(e["src"]) == "OBSERVED_EVENT" and ntype.get(e["dst"]) == "OBSERVED_EVENT"
                    and e["edge_type"] in SVJ["core_flow_types"] and e["edge_id"] not in red}

        def py_merge_count(edges):
            from collections import Counter
            disp = {t: k for k, v in SPEC.items() for t in v}
            c = Counter((e["src"], e["dst"], disp[e["edge_type"]], e["sd_status"]) for e in edges if e["edge_type"] not in SVJ["merge_exclude_types"])
            return sum(1 for v in c.values() if v > 1)

        def py_ball(nid, k):
            nodes, ring = {nid}, {nid}
            for _ in range(k):
                nxt = set()
                for e in sd_edges:
                    for a, b in ((e["src"], e["dst"]), (e["dst"], e["src"])):
                        if a in ring and b not in nodes:
                            nxt.add(b)
                nodes |= nxt
                ring = nxt
            return nodes

        def py_mech_scope(m):
            core = {m} | {e["dst"] for e in sd_edges if e["src"] == m and e["edge_type"] in ("INSTANTIATED_BY", "INSTANTIATED_BY_SECONDARY", "ANCHORED_TO")}
            core |= {e["dst"] for e in sd_edges if e["edge_type"] == "CONTRIBUTES_TO" and e["src"] in core}
            nodes = set(core)
            for e in sd_edges:
                if e["origin"] != "SUPER_DAG":
                    continue
                if (e["src"] in core and e["dst"] in core) or (e["src"] in core and ntype[e["dst"]] == "OBSERVED_EVENT") or \
                        (e["dst"] in core and nstat[e["src"]] in ("CONTEXT", "UNRESOLVED")):
                    nodes |= {e["src"], e["dst"]}
            return nodes

        def fresh_page(route_bundle_extra=None):
            pg = browser.new_page(viewport={"width": 1600, "height": 1000})
            perr = []
            pg.on("pageerror", lambda e: perr.append(str(e)))
            pg.on("console", lambda m: perr.append(m.text) if m.type == "error" else None)
            if route_bundle_extra:
                body = (DOCS / "data" / "bundle.js").read_text(encoding="utf-8") + route_bundle_extra
                pg.route("**/data/bundle.js*", lambda route: route.fulfill(body=body, content_type="application/javascript"))
            pg.goto(url)
            pg.wait_for_function("window.__viz && window.__viz.cy")
            pg.wait_for_timeout(300)
            return pg, perr

        def vis_in(pg, sel="node"):
            return set(pg.evaluate(f"window.__viz.cy.$('{sel}').filter(e => e.style('display') !== 'none' && (e.isNode() || (e.source().style('display') !== 'none' && e.target().style('display') !== 'none'))).map(e => e.id())"))

        @check("31 간단히 보기 기본 화면: 관측 사건 전부 + 핵심 흐름만, 접힌 개수 안내, 범례 단순화")
        def t_simple_default():
            pg, perr = fresh_page()
            msgs = []
            st = pg.evaluate("window.__viz.getState()")
            if st["level"] != "simple" or st["hops"] != 1:
                msgs.append(f"기본 상태 {st['level']}/{st['hops']}")
            vn, ve = vis_in(pg), vis_in(pg, "edge")
            want_e = py_core(sd_edges)
            if vn != set(observed):
                msgs.append(f"보이는 node ≠ 관측 사건 (+{sorted(vn - set(observed))[:3]} −{sorted(set(observed) - vn)[:3]})")
            if ve != want_e:
                msgs.append(f"보이는 edge ≠ 핵심 흐름 (+{sorted(ve - want_e)[:3]} −{sorted(want_e - ve)[:3]})")
            banner = pg.inner_text("#banner-view")
            cnt = pg.evaluate("window.__viz.counts()")
            for w in [f"보이는 node {len(observed)}개", f"관계 {len(want_e)}개", f"접힌 node {len(sd_nodes) - len(observed)}개",
                      f"관계 {len(sd_edges) - len(want_e)}개", "삭제가 아니라 화면에서만 접은 것"]:
                if w not in banner:
                    msgs.append(f"배너에 '{w}' 없음")
            ln, le = pg.locator("#legend-nodes .row").count(), pg.locator("#legend-edges .row").count()
            if (ln, le) != (4, 3):
                msgs.append(f"기본 범례 node {ln}·edge {le}행 ≠ 4·3")
            if pg.evaluate("document.getElementById('legend-detail').open"):
                msgs.append("상세 범례가 처음부터 펼쳐져 있음")
            pg.click("#legend-detail summary")
            det = pg.inner_text("#legend-detail")
            miss = [t for t in sorted(set().union(*SPEC.values())) if t not in det] + [w for w in ["UNRESOLVED (이중 테두리)", "선 굵기 = 증거 상태"] if w not in det]
            if miss:
                msgs.append(f"상세 범례에 없음 {miss[:4]}")
            if shots:
                pg.screenshot(path=str(shots / "simple_default.png"))
            pg.close()
            msgs += perr
            return not msgs, (f"첫 화면 node {len(observed)}/{len(sd_nodes)}(관측 사건 전부) · edge {len(want_e)}/{len(sd_edges)}(관측 사건 사이 핵심 시간·절차 흐름 = Python으로 따로 계산한 집합과 같음, "
                              f"시간 선후 중복 {cnt['reduced']}개), 배너에 접힌 node {cnt['collapsedNodes']}·관계 {cnt['collapsedEdges']}개와 '화면에서만 접음' 안내, "
                              f"범례 node 4·edge 3, 상세 범례에 관계 19종·이중 테두리 유지") if not msgs else "; ".join(msgs[:5])

        @check("32 표시 유형 3종: 19종 관계 → 기록·절차 실선 / 분석·추론 점선 / 맥락·제약 옅은 점선, 원래 관계·증거 상태 보존")
        def t_edge_types():
            pg, perr = fresh_page()
            pg.evaluate("window.__viz.setLevel('full')")
            msgs = []
            rows = pg.evaluate("""window.__viz.cy.edges().filter(e => !e.data('members')).map(e => ({id: e.id(), t: e.data('etype'), cat: e.data('cat'),
                ls: e.style('line-style'), lc: e.style('line-color'), w: parseFloat(e.style('width')), op: parseFloat(e.style('opacity')), sg: e.data('sgroup'),
                cls: e.classes().filter(c => c.startsWith('cat-'))}))""")
            canon_t = {e["edge_id"]: e["edge_type"] for e in sd_edges}
            if {r["id"]: r["t"] for r in rows} != canon_t:
                msgs.append("화면 edge의 관계 유형이 canonical과 다름")
            if len(set(canon_t.values())) != 19:
                msgs.append(f"관계 유형 {len(set(canon_t.values()))}종")
            looks = {}
            for r in rows:
                want = next(k for k, v in SPEC.items() if r["t"] in v)
                if r["cat"] != want or r["cls"] != ["cat-" + want]:
                    msgs.append(f"{r['id']} {r['t']} → {r['cat']} {r['cls']} ≠ {want}")
                looks.setdefault(want, set()).add((r["ls"], r["lc"]))
            if any(len(v) != 1 for v in looks.values()) or len({next(iter(v)) for v in looks.values()}) != 3:
                msgs.append(f"표시 유형별 선 모양·색이 하나로 모이지 않음 {looks}")
            if {k: next(iter(v))[0] for k, v in looks.items()} != {"record": "solid", "analysis": "dashed", "context": "dotted"}:
                msgs.append(f"선 모양 {looks}")
            wo = {r["w"] for r in rows if r["cat"] == "record" and r["sg"] == "OBSERVED"}
            wd = {r["w"] for r in rows if r["cat"] == "record" and r["sg"] == "DERIVED"}
            wa = {r["w"] for r in rows if r["cat"] == "analysis"}
            if not (min(wo) > max(wd) > max(wa)):
                msgs.append(f"굵기(증거 상태·유형) OBSERVED {wo} DERIVED {wd} 분석 {wa}")
            op = {k: {r["op"] for r in rows if r["cat"] == k} for k in SPEC}
            if not max(op["context"]) < min(op["record"]):
                msgs.append(f"맥락·제약이 옅지 않음 {op}")
            # 주장 수준 상충: 선택 시 원래 관계 의미, 다른 끝 모양
            pg.evaluate("window.__viz.focusEdge('OE007')")
            pg.wait_for_timeout(150)
            lab = pg.evaluate("window.__viz.cy.getElementById('OE007').style('label')")
            arrow = pg.evaluate("[window.__viz.cy.getElementById('OE007').style('target-arrow-shape'), window.__viz.cy.getElementById('OE008').style('target-arrow-shape')]")
            d = pg.inner_text("#p-detail")
            if "CONTRADICTS_AT_CLAIM_LEVEL" not in lab or "상충" not in lab:
                msgs.append(f"OE007 선택 label {lab!r}")
            if arrow[0] == arrow[1]:
                msgs.append(f"상충 edge 끝 모양이 흐름 edge와 같음 {arrow}")
            for w in ["원래 관계", "CONTRADICTS_AT_CLAIM_LEVEL", "주장 수준 상충", "화면 표시 유형", "기록·절차", "DERIVED"]:
                if w not in d:
                    msgs.append(f"OE007 상세에 '{w}' 없음")
            pg.evaluate("window.__viz.focusEdge('SD058')")
            d = pg.inner_text("#p-detail")
            if "분석·추론" not in d or "LATENT_MECHANISM" not in d:
                msgs.append("SD058 상세에 표시 유형·상태 없음")
            if shots:
                pg.screenshot(path=str(shots / "edge_contradicts.png"))
            pg.close()
            msgs += perr
            return not msgs, (f"edge {len(rows)}개 관계 유형 = canonical(19종), 표시 유형 기록·절차 {len(SPEC['record'])}종 실선 · 분석·추론 {len(SPEC['analysis'])}종 점선 · "
                              f"맥락·제약 {len(SPEC['context'])}종 옅은 점선(유형별 모양·색 하나), 굵기 OBSERVED {min(wo)} > DERIVED {max(wd)} > 분석 {max(wa)}, "
                              f"OE007 선택 시 '{lab[:40]}'·끝 모양 {arrow[0]}(흐름 {arrow[1]})·상세에 원래 관계 의미") if not msgs else "; ".join(msgs[:6])

        @check("33 선택 중심 펼치기: 1-hop 기본 · 2-hop · 해제, 상세 패널(관계·메커니즘·후보·출처·상태)")
        def t_select_expand():
            pg, perr = fresh_page()
            msgs = []
            pos = pg.evaluate("""(() => { const cy = window.__viz.cy; const n = cy.getElementById('EP09');
                cy.center(n); cy.zoom({level: 1.0, position: n.position()});
                const r = n.renderedPosition(); const b = document.getElementById('cy').getBoundingClientRect(); return [b.left + r.x, b.top + r.y]; })()""")
            pg.wait_for_timeout(80)
            pg.mouse.click(pos[0], pos[1])
            pg.wait_for_timeout(250)
            b1 = py_ball("EP09", 1)
            inc = {e["edge_id"] for e in sd_edges if "EP09" in (e["src"], e["dst"])}
            vn, ve = vis_in(pg), vis_in(pg, "edge")
            if vn != set(observed) | b1:
                msgs.append(f"1-hop 펼침 node 다름 (+{sorted(vn - set(observed) - b1)[:3]} −{sorted(b1 - vn)[:3]})")
            if not inc <= ve:
                msgs.append(f"EP09 직접 관계 중 안 보임 {sorted(inc - ve)[:4]}")
            hl = pg.evaluate("window.__viz.cy.getElementById('EP09').connectedEdges().filter(e => e.style('display') !== 'none' && !(e.hasClass('sel-in') || e.hasClass('sel-out'))).length")
            if hl:
                msgs.append(f"직접 관계 강조 빠짐 {hl}")
            d = pg.inner_text("#p-detail")
            for w in ["EP09", "OBSERVED", "관련 edge", "관련 Mechanism", "관련 LATENT 후보", "Source fact ID", "Source record", "관련 World", "UNRESOLVED 의존"] + \
                    eps["EP09"]["member_fact_ids"].split("|"):
                if w not in d:
                    msgs.append(f"상세에 '{w}' 없음")
            if "선택 EP09: 1-hop" not in pg.inner_text("#banner-view"):
                msgs.append("배너에 선택 펼침 안내 없음")
            pg.click("#hop-buttons button[data-hops='2']")
            pg.wait_for_timeout(200)
            b2 = py_ball("EP09", 2)
            vn2 = vis_in(pg)
            if vn2 != set(observed) | b2:
                msgs.append(f"2-hop 펼침 node 다름 (+{sorted(vn2 - set(observed) - b2)[:3]} −{sorted(b2 - vn2)[:3]})")
            n2 = pg.evaluate("window.__viz.cy.edges('.sel-2').length")
            if not n2:
                msgs.append("2-hop 관계 강조 없음")
            if shots:
                pg.screenshot(path=str(shots / "select_EP09_2hop.png"))
            box = pg.locator("#cy").bounding_box()
            pg.evaluate("window.__viz.cy.zoom(0.2)")
            pg.mouse.click(box["x"] + box["width"] - 20, box["y"] + box["height"] - 20)   # 빈 배경
            pg.wait_for_timeout(250)
            if vis_in(pg) != set(observed):
                msgs.append("배경을 눌러도 펼친 node가 접히지 않음")
            pg.close()
            msgs += perr
            return not msgs, (f"EP09 클릭 → 1-hop node {len(b1) - 1}개·직접 관계 {len(inc)}개 펼침·강조, 상세에 관계·메커니즘·후보·CF·출처·상태·World·UNRESOLVED, "
                              f"2-hop → node {len(b2) - 1}개(Python BFS와 같음)·2번째 고리 관계 {n2}개 강조, 배경 클릭 → 관측 사건 {len(observed)}개로 복귀") if not msgs else "; ".join(msgs[:5])

        @check("34 메커니즘 펼치기 M1–MB: 그 메커니즘 범위만 펼침·강조, 다른 메커니즘 데이터·world·개입 결과 그대로")
        def t_mech_focus():
            pg, perr = fresh_page()
            msgs, parts = [], []
            before = pg.evaluate("JSON.stringify(window.__viz.data)")
            pg.click(".ptabs button[data-ptab='world']")
            wtxt = pg.inner_text("#p-world")
            for m in mechs:
                pg.click(f"#mech-focus button[data-focus-mech='{m}']")
                pg.wait_for_timeout(150)
                scope = py_mech_scope(m)
                vn = vis_in(pg)
                if vn != set(observed) | scope:
                    msgs.append(f"{m}: 펼친 node 다름 (+{sorted(vn - set(observed) - scope)[:3]} −{sorted(scope - vn)[:3]})")
                mf = set(pg.evaluate("window.__viz.cy.nodes('.mfocus').map(n => n.id())"))
                if mf != scope - set(observed):
                    msgs.append(f"{m}: 강조 node 다름")
                if pg.get_attribute(f"#mech-focus button[data-focus-mech='{m}']", "aria-pressed") != "true":
                    msgs.append(f"{m}: 버튼 상태")
                parts.append(f"{m} {len(scope - set(observed))}")
            pg.click(f"#mech-focus button[data-focus-mech='MB']")
            pg.wait_for_timeout(150)
            if vis_in(pg) != set(observed):
                msgs.append("다시 눌러 해제해도 접히지 않음")
            # 전체 표시에서는 숨기지 않고 범위 밖 분석 node만 흐리게
            pg.evaluate("window.__viz.setLevel('full'); window.__viz.setFocusMech('M3')")
            pg.wait_for_timeout(150)
            if vis_in(pg) != {n["node_id"] for n in sd_nodes}:
                msgs.append("전체 표시에서 메커니즘 펼치기가 node를 숨김")
            dim = set(pg.evaluate("window.__viz.cy.nodes('.dim').map(n => n.id())"))
            out_scope = {n["node_id"] for n in sd_nodes if n["node_type"] != "OBSERVED_EVENT"} - py_mech_scope("M3")
            if dim != out_scope:
                msgs.append(f"전체 표시 흐림 범위 다름 ({len(dim)} vs {len(out_scope)})")
            pg.evaluate("window.__viz.setFocusMech(null)")
            pg.click(".ptabs button[data-ptab='world']")
            if pg.inner_text("#p-world") != wtxt:
                msgs.append("메커니즘 펼치기 뒤 World 구성 패널이 바뀜")
            if pg.evaluate("JSON.stringify(window.__viz.data)") != before:
                msgs.append("메커니즘 펼치기가 화면 데이터(canonical 값)를 바꿈")
            if shots:
                pg.evaluate("window.__viz.setLevel('simple'); window.__viz.setFocusMech('M1')")
                pg.wait_for_timeout(200)
                pg.screenshot(path=str(shots / "focus_M1.png"))
            pg.close()
            msgs += perr
            return not msgs, ("메커니즘별 펼친 분석 node 수(Python으로 따로 계산한 범위와 같음) — " + ", ".join(parts) +
                              "; 해제 시 관측 사건만, 전체 표시에서는 숨기지 않고 범위 밖 분석 node만 흐림, World 패널·화면 데이터 그대로") if not msgs else "; ".join(msgs[:5])

        @check("35 간단히 보기에서도 world 선택·W6 배제·개입 결과 그대로(전체 표시와 패널 내용 같음)")
        def t_simple_world_iv():
            pg, perr = fresh_page()
            msgs = []
            for wid in ["W1", "W2", "W3", "W4", "W5", "W6"]:
                txt = {}
                for lv in ["full", "simple"]:
                    pg.evaluate(f"window.__viz.setLevel('{lv}'); window.__viz.setWorld('{wid}')")
                    pg.click(".ptabs button[data-ptab='world']")
                    txt[lv] = pg.inner_text("#p-world")
                if txt["full"] != txt["simple"]:
                    msgs.append(f"{wid}: World 패널이 표시 수준에 따라 다름")
                bridges = set(filter(None, configs[wid]["latent_bridges"].split("|")))
                vn = vis_in(pg)
                if not set(observed) <= vn or not bridges <= vn:
                    msgs.append(f"{wid}: 간단히 보기에서 관측 사건·world 후보가 안 보임 {sorted(bridges - vn)[:3]}")
                cls = "hl-rej" if wid == "W6" else "hl"
                if not all(cls in set(pg.evaluate(f"window.__viz.cy.getElementById('{b}').classes()")) for b in bridges):
                    msgs.append(f"{wid}: 후보 강조({cls}) 없음")
                for m in mechs:
                    lab = pg.evaluate(f"window.__viz.cy.getElementById('{m}').data('label')")
                    if f"\n{wid}: {configs[wid][m]}" not in lab:
                        msgs.append(f"{wid}.{m} 표시 {lab!r}")
                if wid == "W6" and "REJECTED" not in (pg.inner_text("#banner-world") if pg.is_visible("#banner-world") else ""):
                    msgs.append("W6 REJECTED 배너 없음")
            pg.evaluate("window.__viz.setWorld('ALL')")
            for m in mechs:
                txt = {}
                for lv in ["full", "simple"]:
                    pg.evaluate(f"window.__viz.setLevel('{lv}'); window.__viz.setIntervention('{m}')")
                    txt[lv] = pg.inner_text("#iv-table")
                if txt["full"] != txt["simple"]:
                    msgs.append(f"do({m}): 개입 표가 표시 수준에 따라 다름")
                for r in [r for r in ivs if r["mechanism"] == m]:
                    path = {r["mechanism"], r["variable"], *filter(None, r["removed"].split("|")), *filter(None, r["remaining"].split("|")), *filter(None, r["target"].split("|"))}
                    if not path <= vis_in(pg):
                        msgs.append(f"do({m}): 간단히 보기에서 경로 node 안 보임 {sorted(path - vis_in(pg))[:3]}")
                    if "iv-" + r["result"] not in set(pg.evaluate(f"window.__viz.cy.getElementById('{r['variable']}').classes()")):
                        msgs.append(f"do({m}) {r['variable']} 결과 강조 없음")
                if not set(observed) <= vis_in(pg):
                    msgs.append(f"do({m}): 관측 node 사라짐")
            if shots:
                pg.evaluate("window.__viz.setIntervention('M1')")
                pg.screenshot(path=str(shots / "simple_iv_M1.png"))
            pg.close()
            msgs += perr
            return not msgs, "W1–W6 각각: World 패널 = 전체 표시와 같음, world 후보 펼침·강조(W6 hl-rej·REJECTED 배너), 메커니즘 값 = CSV; do(M=OFF) 7개: 개입 표 = 전체 표시와 같음, 경로 node 펼침·결과 강조, 관측 node 유지" if not msgs else "; ".join(msgs[:5])

        @check("36 같은 node 쌍 관계 묶음·시간 선후 중복 축소(시험용 관계를 메모리에만 주입)")
        def t_merge_reduce():
            extra = """
(function () { var E = window.GUSUN_DATA.super_dag.edges;
  function add(id, s, d, t, st, g, o) { E.push({id: id, status_group: g, canonical: {edge_id: id, src: s, dst: d, edge_type: t, sd_status: st, origin: o, note: 'TEST FIXTURE'}}); }
  add('X_DUP', 'EP09', 'EP10', 'REVIEW_OF', 'DERIVED', 'DERIVED', 'FROZEN');
  add('X_REV', 'EP10', 'EP09', 'INFORMATION_FLOW', 'DERIVED', 'DERIVED', 'FROZEN');
  add('X_CON', 'EP09', 'EP10', 'CONTRADICTS_AT_CLAIM_LEVEL', 'DERIVED', 'DERIVED', 'FROZEN');
  add('X_TB', 'EP01', 'EP03', 'TEMPORAL_BEFORE', 'DERIVED', 'DERIVED', 'FROZEN');
  add('X_RV', 'EP13', 'EP16', 'REVIEW_OF', 'DERIVED', 'DERIVED', 'FROZEN');
  add('X_RV2', 'EP15', 'EP16', 'REVIEW_OF', 'DERIVED', 'DERIVED', 'FROZEN');
})();
"""
            pg, perr = fresh_page(extra)
            msgs = []
            merged = pg.evaluate("window.__viz.display.merged.map(m => m.id)")
            red = sorted(pg.evaluate("Object.keys(window.__viz.display.redundant)"))
            fx = [dict(edge_id=i, src=s_, dst=d_, edge_type=t_) for i, s_, d_, t_ in [("X_DUP", "EP09", "EP10", "REVIEW_OF"), ("X_REV", "EP10", "EP09", "INFORMATION_FLOW"),
                  ("X_CON", "EP09", "EP10", "CONTRADICTS_AT_CLAIM_LEVEL"), ("X_TB", "EP01", "EP03", "TEMPORAL_BEFORE"), ("X_RV", "EP13", "EP16", "REVIEW_OF"),
                  ("X_RV2", "EP15", "EP16", "REVIEW_OF")]]
            want_red = sorted(py_redundant(sd_edges + fx))
            if sorted(merged) != ["MG~OE009~X_DUP", "MG~OE041~X_RV2"]:
                msgs.append(f"묶음 {merged}")
            if red != ["X_TB"] or want_red != ["X_TB"]:
                msgs.append(f"시간 선후 중복 {red} (Python {want_red}) ≠ ['X_TB'] — REVIEW_OF 지름길 X_RV는 줄이면 안 됨")
            ve = vis_in(pg, "edge")
            if "X_TB" in ve or "reduced" not in pg.evaluate("window.__viz.cy.getElementById('X_TB').classes()"):
                msgs.append("간단히 보기에서 중복 시간 선후 X_TB가 보이거나 reduced 표시 없음")
            if "X_RV" not in ve:
                msgs.append("추이적이 아닌 REVIEW_OF 지름길 X_RV가 숨겨짐")
            if "MG~OE009~X_DUP" not in ve or {"OE009", "X_DUP"} & ve:
                msgs.append("EP09→EP10 묶음 선이 하나로 그려지지 않음")
            pg.evaluate("window.__viz.setLevel('full')")
            pg.wait_for_timeout(120)
            ve = vis_in(pg, "edge")
            if not {"X_TB", "X_REV", "X_CON", "X_RV"} <= ve:
                msgs.append(f"전체 표시에서 따로 그려야 할 관계가 안 보임 {sorted({'X_TB', 'X_REV', 'X_CON', 'X_RV'} - ve)}")
            pg.evaluate("window.__viz.focusEdge('MG~OE009~X_DUP')")
            pg.wait_for_timeout(120)
            d = pg.inner_text("#p-detail")
            for w in ["관계 2개", "OE009", "PROCEDURAL_NEXT", "X_DUP", "REVIEW_OF", "원래 관계"]:
                if w not in d:
                    msgs.append(f"묶음 선 상세에 '{w}' 없음")
            pg.click("#merged-members [data-goto-edge='X_DUP']")
            pg.wait_for_timeout(120)
            d = pg.inner_text("#p-detail")
            sel = pg.evaluate("window.__viz.cy.$('edge:selected').map(e => e.id())")
            if "edge X_DUP" not in d or "REVIEW_OF" not in d or sel != ["MG~OE009~X_DUP"]:
                msgs.append(f"구성원 X_DUP 상세·선택 {sel}")
            pg.evaluate("window.__viz.setLevel('simple'); window.__viz.focusNode('EP01')")
            pg.wait_for_timeout(120)
            if "X_TB" not in vis_in(pg, "edge"):
                msgs.append("EP01을 고르면 중복 시간 선후 X_TB도 펼쳐져야 함")
            n = pg.evaluate("window.__viz.cy.edges().filter(e => !e.data('members')).length")
            if n != len(sd_edges) + 6:
                msgs.append(f"원본 edge {n} ≠ {len(sd_edges) + 6}(묶음이 원본 edge를 지움)")
            if shots:
                pg.evaluate("window.__viz.focusEdge('MG~OE009~X_DUP')")
                pg.screenshot(path=str(shots / "merged_fixture.png"))
            pg.close()
            msgs += perr
            return not msgs, ("주입한 6개 관계: EP09→EP10 PROCEDURAL_NEXT+REVIEW_OF(같은 방향·기록·절차·DERIVED) → 선 하나 '관계 2개', 누르면 둘 다·구성원 상세; "
                              "반대 방향 X_REV·상충 X_CON은 따로; TEMPORAL_BEFORE EP01→EP03(EP01→EP02→EP03 경로 있음)만 간단히 보기에서 접힘, "
                              "REVIEW_OF 지름길 EP13→EP16은 그대로, 전체 표시·EP01 선택 시 다시 보임, 원본 edge 수 그대로. "
                              f"실제 데이터에는 묶일 쌍 {py_merge_count(sd_edges)}개·중복 시간 선후 {len(py_redundant(sd_edges))}개") if not msgs else "; ".join(msgs[:5])

        @check("37 화면 조작 전후 원본 데이터 불변 · 숨긴 관계도 상세·분석에 그대로")
        def t_data_intact():
            pg, perr = fresh_page()
            msgs = []
            before = pg.evaluate("JSON.stringify(window.__viz.data)")
            disk = (DOCS / "data" / "bundle.js").read_text(encoding="utf-8")
            disk_data = json.loads(disk[disk.index("window.GUSUN_DATA = ") + len("window.GUSUN_DATA = "):].rstrip().rstrip(";"))
            if json.loads(before) != disk_data:
                msgs.append("화면 메모리 데이터 ≠ bundle.js")
            # 간단히 보기(아무것도 고르지 않음)에서 상세 패널은 숨긴 관계까지 모두 센다
            pg.evaluate("window.__viz.focusNode('EP23')")
            d = pg.inner_text("#p-detail")
            nin = sum(1 for e in sd_edges if e["dst"] == "EP23")
            nout = sum(1 for e in sd_edges if e["src"] == "EP23")
            if f"들어오는 edge ({nin})" not in d or f"나가는 edge ({nout})" not in d:
                msgs.append(f"EP23 상세 관계 수 ≠ canonical(in {nin} · out {nout})")
            ops = ["window.__viz.setLevel('records')", "window.__viz.setHops(2)", "window.__viz.focusNode('G04a')", "window.__viz.setFocusMech('M2')",
                   "window.__viz.setWorld('W6')", "window.__viz.setIntervention('M5')", "window.__viz.setPair('M1', 'M3')", "window.__viz.setView('death')",
                   "window.__viz.setView('overview')", "window.__viz.setLevel('simple')", "window.__viz.focusEdge('OE007')", "window.__viz.fitAll()",
                   "window.__viz.reset()"]
            for op in ops:
                pg.evaluate(op)
            pg.click("#mech-filters input[data-mech='M4']")
            pg.click("#status-filters input[data-status='CONTEXT']")
            after = pg.evaluate("JSON.stringify(window.__viz.data)")
            if after != before:
                msgs.append("화면 조작 뒤 window.__viz.data가 바뀜")
            n = pg.evaluate("[window.__viz.cy.nodes().length, window.__viz.cy.edges().filter(e => !e.data('members')).length]")
            if n != [len(sd_nodes), len(sd_edges)]:
                msgs.append(f"cy 원본 요소 {n}")
            pg.close()
            msgs += perr
            return not msgs, (f"화면 메모리 데이터 = bundle.js, 간단히 보기에서 EP23 상세 관계 in {nin}·out {nout}(숨긴 관계 포함 canonical 전부), "
                              f"표시 수준·2-hop·선택·메커니즘 펼치기·W6·개입·공존·View·필터 {len(ops) + 2}가지 조작 뒤 데이터 문자열 동일, cy node {n[0]}·edge {n[1]}") if not msgs else "; ".join(msgs[:5])

        @check("38 좁은 화면(420px) 간단히 보기 조작 UI: 가로 넘침 없음·글자 ≥ 11pt")
        def t_simple_narrow():
            pg = browser.new_page(viewport={"width": 420, "height": 860})
            perr = []
            pg.on("pageerror", lambda e: perr.append(str(e)))
            pg.goto(url)
            pg.wait_for_function("window.__viz && window.__viz.cy")
            pg.click("#legend-detail summary")
            pg.evaluate("window.__viz.focusNode('EP09'); window.__viz.setFocusMech('M1')")
            pg.wait_for_timeout(200)
            over = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            side = pg.evaluate("(() => { const s = document.getElementById('sidebar'); return s.scrollWidth - s.clientWidth; })()")
            r = pg.evaluate(FONT_JS)
            if shots:
                pg.screenshot(path=str(shots / "narrow_simple.png"), full_page=True)
            pg.close()
            ok = over <= 0 and side <= 0 and not r["nbad"] and not perr
            return ok, f"가로 넘침 문서 {over}px·사이드바 {side}px, 글자 요소 {r['n']}개 중 11pt·1.6 미만 {r['nbad']} {r['bad'][:2]}, 오류 {len(perr)}"

        @check("27 console error 없음")
        def t_console():
            return not errors, "console error·page error·요청 실패 0" if not errors else "; ".join(errors[:5])

        for t in [t_render, t_load, t_json, t_counts, t_worlds, t_w6, t_status, t_mech, t_node_detail, t_edge_detail, t_search, t_iv,
                  t_inter, t_views, t_backbone, t_outcome, t_temporal, t_reset, t_file, t_fonts, t_labels, t_initial,
                  t_search_ux, t_pan, t_context, t_detail_sections, t_narrow, t_render_views, t_stale, t_empty_guard,
                  t_simple_default, t_edge_types, t_select_expand, t_mech_focus, t_simple_world_iv, t_merge_reduce, t_data_intact,
                  t_simple_narrow]:
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
