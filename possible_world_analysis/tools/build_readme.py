#!/usr/bin/env python3
"""README.md의 자동 생성 블록을 갱신한다.

블록: REFERENCES(APA 참고문헌) · EVIDENCE_MAP(변수별 근거 추적표) · VARIABLES(변수 정의) · LINKCHECK(링크 검사 요약)
README의 <!-- BEGIN:X --> … <!-- END:X --> 사이만 교체한다. tests/test_readme.py가 블록이 최신인지 검사한다.

사용: python tools/build_readme.py [--check]
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

CAT_TITLE = {
    "primary": "A-1. 1차 사료",
    "scholarship": "A-2. 학술연구",
    "theory_institutional": "A-3. 이론·제도·방법 해설",
    "internal": "A-4. 프로젝트 내부 자료 (증거 아님 — 추적용)",
}
TV_KO = {
    "ORIGINAL_VERIFIED": "원문(본문) 직접 확인",
    "INDIRECT_TRANSCRIPTION": "원문 구절은 사용자 데이터셋 전사본으로만 확인 — **원문 검증 미완료**",
    "SECONDARY_SUMMARY": "사용자 문서의 요약으로만 확인 — **원문 검증 미완료**",
    "BIBLIOGRAPHIC_ONLY": "서지만 확인(본문 미열람) — **검증 미완료**",
    "NOT_VERIFIED": "미검증 — **검증 미완료**",
    "URL_ONLY": "URL만 확인(본문 미열람) — **원문 검증 미완료**",
}
US_KO = {
    "OK": "URL 확인(응답 정상)",
    "AUTH_REQUIRED": "URL 응답: 인증·구독 필요",
    "NOT_FOUND": "URL 응답: 404/410 (링크 오류 가능; 자료 부재를 뜻하지 않음)",
    "NETWORK_BLOCKED": "URL 미확인: 실행 환경 네트워크 정책이 접속 차단(자료 부재 아님)",
    "ERROR": "URL 미확인: 기타 오류",
    "NO_URL": "원문 링크 없음",
    "NOT_CHECKED": "URL 미검사",
}


def load():
    src = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))["sources"]
    var = yaml.safe_load((ROOT / "02_variables.yaml").read_text(encoding="utf-8"))["variables"]
    with (ROOT / "01_claim_registry.csv").open(encoding="utf-8-sig") as f:
        claims = {r["claim_id"]: r for r in csv.DictReader(f)}
    return src, var, claims


def apa_line(s):
    title = s["title"]
    link = f"[{title}]({s['url']})" if s.get("url") else f"*{title}*"
    txt = s["apa"].replace("{title_link}", link).replace("{title}", title)
    return txt


def references(src):
    out = []
    for cat, ttl in CAT_TITLE.items():
        out += [f"### {ttl}", ""]
        for s in [x for x in src if x["category"] == cat]:
            uc = s.get("url_check", {}) or {}
            st = uc.get("status", "NOT_CHECKED")
            meta = [f"사건 날짜: {s.get('event_date', '')}", f"편찬·작성 시기: {s.get('source_date', '')}",
                    US_KO.get(st, st) + (f" ({uc.get('checked_at')})" if uc.get("checked_at") else ""),
                    TV_KO.get(s["text_verification"], s["text_verification"])]
            if not s.get("url"):
                meta.append(f"링크 비어 있는 이유: {s.get('url_missing_reason', '')}")
            if s.get("alt_urls"):
                meta.append("대체 링크: " + ", ".join(f"<{u}>" for u in s["alt_urls"]))
            if s.get("url_conflict"):
                meta.append("링크 불일치: " + s["url_conflict"])
            if s.get("missing_fields"):
                meta.append("확인 못 한 서지 요소: " + ", ".join(s["missing_fields"]))
            if s.get("local_copy"):
                meta.append("로컬 위치: " + ", ".join(f"`{p.strip()}`" for p in s["local_copy"].split(";")))
            out.append(f'<a id="src-{s["source_id"]}"></a>**[{s["source_id"]}]** {apa_line(s)}  ')
            out.append("<sub>" + " · ".join(meta) + "</sub>")
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def evidence_map(src, var, claims):
    smap = {s["source_id"]: s for s in src}
    rows = ["| 변수 ID | 변수 또는 주장 | 근거 문헌 | 원문 링크 | 근거 유형 | 검증 상태 |", "|---|---|---|---|---|---|"]
    for v in var:
        sids = v["source_ids"]
        lit = ", ".join(f"[{sid}](#src-{sid})" for sid in sids) if sids else "없음"
        urls = []
        for cid in v["claim_ids"] + v["context_claim_ids"]:
            u = claims.get(cid, {}).get("url", "")
            if u and u not in urls:
                urls.append(u)
        for sid in sids:
            u = smap.get(sid, {}).get("url", "")
            if u and u not in urls:
                urls.append(u)
        link = " ".join(f"[↗{i + 1}]({u})" for i, u in enumerate(urls[:4])) if urls else "없음"
        ctx = " (비교·후대 맥락 포함)" if v["context_claim_ids"] else ""
        rows.append(f"| [{v['id']}](#var-{v['id']}) | {v['name']} | {lit} | {link} | {v['basis_type']}{ctx} | {v['evidence_status']} |")
    return "\n".join(rows) + "\n"


def variables_block(var):
    out = []
    for g, ttl in (("T", "T군 — 시간·관직·사건 순서"), ("E", "E군 — 경제·농업·계층"), ("A", "A군 — 권분·포폄·행정 책임"),
                   ("S", "S군 — 희생양화·책임 귀인·집단폭력"), ("F", "F군 — 가족체계와 조환 사주"),
                   ("M", "M군 — 이가원의 금전 요구와 무고"), ("J", "J군 — 검험·무고·재조사·책임 은폐")):
        out += [f"#### {ttl}", ""]
        for v in [x for x in var if x["group"] == g]:
            srcs = ", ".join(f"[{s}](#src-{s})" for s in v["source_ids"]) or "없음"
            cl = ", ".join(v["claim_ids"]) or "없음"
            ctx = f" · 맥락 주장: {', '.join(v['context_claim_ids'])}" if v["context_claim_ids"] else ""
            sym = f" · 모형 기호: `{'`, `'.join(v['model_symbols'])}`" if v["model_symbols"] else ""
            note = f" · 주: {v['note']}" if v["note"] else ""
            out.append(f'- <a id="var-{v["id"]}"></a>**{v["id"]} {v["name"]}** — {v["definition"]} '
                       f"〔값: {v['domain']} · 층위: {v['layer']} · {v['evidence_status']}〕 출처: {srcs} · 주장: {cl}{ctx}{sym}{note}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def linkcheck_block():
    p = ROOT / "results" / "link_check.json"
    if not p.exists():
        return "링크 검사 결과 없음. `python tools/check_links.py --write` 실행.\n"
    d = json.loads(p.read_text(encoding="utf-8"))
    counts = {}
    for r in d["results"].values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    lines = [f"검사 시각: {d['checked_at']} · 결과 파일: [`results/link_check.json`](results/link_check.json)", "",
             "| 상태 | 개수 | 의미 |", "|---|---|---|"]
    for k, n in sorted(counts.items()):
        lines.append(f"| `{k}` | {n} | {US_KO.get(k, k)} |")
    return "\n".join(lines) + "\n"


def render(text):
    src, var, claims = load()
    blocks = {"REFERENCES": references(src), "EVIDENCE_MAP": evidence_map(src, var, claims),
              "VARIABLES": variables_block(var), "LINKCHECK": linkcheck_block()}
    for k, body in blocks.items():
        pat = re.compile(rf"(<!-- BEGIN:{k} -->\n).*?(<!-- END:{k} -->)", re.S)
        if not pat.search(text):
            raise SystemExit(f"README에 {k} 블록 표지가 없습니다")
        text = pat.sub(lambda m: m.group(1) + body + m.group(2), text)
    return text


if __name__ == "__main__":
    cur = README.read_text(encoding="utf-8")
    new = render(cur)
    if "--check" in sys.argv:
        sys.exit(0 if new == cur else 1)
    README.write_text(new, encoding="utf-8")
    print("README blocks updated")
