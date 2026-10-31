"""README: 참고문헌·근거표가 sources.yaml/02_variables.yaml과 일치, 상대 링크 실재."""
import re
import sys


def test_readme_blocks_current(root):
    sys.path.insert(0, str(root / "tools"))
    import build_readme
    cur = (root / "README.md").read_text(encoding="utf-8")
    assert build_readme.render(cur) == cur, "README 자동 블록이 최신이 아님: python tools/build_readme.py"


def test_reference_ids_match_sources(root, sources):
    txt = (root / "README.md").read_text(encoding="utf-8")
    refs = re.search(r"<!-- BEGIN:REFERENCES -->(.*?)<!-- END:REFERENCES -->", txt, re.S).group(1)
    in_readme = set(re.findall(r'<a id="src-([A-Za-z0-9_]+)"></a>', refs))
    assert in_readme == set(sources)


def test_evidence_map_covers_all_variables(root, variables):
    txt = (root / "README.md").read_text(encoding="utf-8")
    em = re.search(r"<!-- BEGIN:EVIDENCE_MAP -->(.*?)<!-- END:EVIDENCE_MAP -->", txt, re.S).group(1)
    for v in variables:
        assert f"[{v['id']}](#var-{v['id']})" in em, v["id"]


def test_internal_anchors_resolve(root):
    txt = (root / "README.md").read_text(encoding="utf-8")
    anchors = set(re.findall(r'<a id="([^"]+)"></a>', txt))
    for a in re.findall(r"\]\(#([^)]+)\)", txt):
        assert a in anchors, f"README 내부 링크 #{a} 대상 없음"


def test_relative_links_exist(root):
    for md in list(root.glob("*.md")) + list((root / "results").glob("*.md")) + [root / "source_extracts" / "README.md"]:
        txt = md.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", txt):
            if re.match(r"https?://", target):
                continue
            p = (md.parent / target).resolve()
            assert p.exists(), f"{md.name}: 상대 링크 {target} 없음"


def test_cross_doc_anchor(root):
    assert '<a id="references"></a>' in (root / "README.md").read_text(encoding="utf-8")
