"""docs/index.html(《시곡》 사이트)가 분석 결과와 일치하고 실제로 그려지는가."""
import re
import subprocess
import sys

import pytest


@pytest.fixture(scope="module")
def docs(root):
    return root.parent / "docs"


def test_site_data_current(root):
    r = subprocess.run([sys.executable, str(root / "tools" / "build_site.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, "docs/sigok/data.js 또는 index.html 자산 해시가 최신이 아님: python tools/build_site.py\n" + r.stdout


def test_dom_ids_exist(docs):
    html = (docs / "index.html").read_text(encoding="utf-8")
    js = (docs / "sigok" / "sigok.js").read_text(encoding="utf-8")
    have = set(re.findall(r'id="([\w-]+)"', html))
    want = set(re.findall(r"\$\('#([\w-]+)'\)", js)) | set(re.findall(r"getElementById\('([\w-]+)'\)", js))
    assert want <= have, want - have


def test_assets_versioned_and_legacy_viewer_kept(docs):
    html = (docs / "index.html").read_text(encoding="utf-8")
    for rel in ("sigok/sigok.css", "sigok/sigok.js", "sigok/data.js", "vendor/cytoscape/cytoscape.min.js"):
        assert re.search(re.escape(rel) + r"\?v=[0-9a-f]{12}\"", html), rel
    assert (docs / "gusun.html").exists() and 'href="gusun.html"' in html


def test_site_renders(docs):
    pw = pytest.importorskip("playwright.sync_api")
    routes = ["overview", "time/F_ON_H_SIM", "time/FC", "worlds/W07", "cf/Q10", "graph/W07", "evidence/T16", "refs/SIM"]
    with pw.sync_playwright() as p:
        b = p.chromium.launch()
        for vw in (1280, 390):
            pg = b.new_page(viewport={"width": vw, "height": 900})
            errs = []
            pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto((docs / "index.html").as_uri())
            assert pg.evaluate("window.__sigok && window.__sigok.ready")
            for r in routes:
                pg.evaluate(f"location.hash = '{r}'")
                pg.wait_for_timeout(250)
                txt = pg.evaluate("[...document.querySelectorAll('.pane')].filter(p => !p.hidden).map(p => p.innerText.length)")
                assert txt and txt[0] > 200, (vw, r, txt)
                ov = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                assert ov <= 0, f"{vw}px {r}: 가로 넘침 {ov}px"
            assert pg.evaluate("window.__sigok.cy.nodes().length") > 0
            assert not pg.evaluate("[...document.querySelectorAll('.viz-error')].some(e => e.offsetParent !== null)"), "오류 상자가 보임"
            assert not errs, errs
        b.close()
