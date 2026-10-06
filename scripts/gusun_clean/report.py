"""Markdown / CSV / Mermaid 출력."""
import csv
from collections import Counter, defaultdict

from manual_review import AUDIT1_MANUAL, AUDIT1_REVISIONS, AUDIT2_MANUAL, AUDIT2_REVISIONS, AUDIT3_MANUAL, AUDIT3_REVISIONS


def _counts_table(findings):
    c = defaultdict(Counter)
    for f in findings:
        c[f["check"]][f["severity"]] += 1
    lines = ["| check | ERROR | WARN | INFO |", "|---|---|---|---|"]
    for k in sorted(c):
        lines.append(f"| {k} | {c[k]['ERROR']} | {c[k]['WARN']} | {c[k]['INFO']} |")
    return "\n".join(lines)


def _findings_list(findings, sev):
    fs = [f for f in findings if f["severity"] == sev]
    if not fs:
        return "_없음_"
    return "\n".join(f"- `{f['check']}` **{f['target']}** — {f['message']}" for f in fs)


def _verdict(findings):
    n = sum(f["severity"] == "ERROR" for f in findings)
    return "**PASS** (ERROR 0)" if n == 0 else f"**FAIL** (ERROR {n})"


def _revlog(revs):
    if not revs:
        return "_수정 이력 없음_"
    lines = ["| 회차 | 발견 | 조치 |", "|---|---|---|"]
    for r in revs:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} |")
    return "\n".join(lines)


def write_audit1(path, findings, outside, ep_rows, cf):
    traced = {f for e in ep_rows for f in e["member_fact_ids"].split("|")}
    lines = [
        "# AUDIT 1 — Episode Fidelity Audit",
        "",
        "핵심 질문: **문장들을 episode로 묶으면서 원래 내용이 바뀌었는가?**",
        "",
        f"- 판정: {_verdict(findings)}",
        f"- confirmed fact {len(cf)}개 중 episode로 추적 가능: {len(traced)}개",
        f"- episode {len(ep_rows)}개 — 모두 confirmed fact로 역추적됨 (unsupported episode = "
        f"{sum(f['check']=='unsupported_episode' and f['severity']=='ERROR' for f in findings)})",
        "",
        "## 1. 자동 검사 요약",
        "",
        _counts_table(findings),
        "",
        "검사 항목: omission, unsupported_episode, clause_fidelity, over_merge, order_execution_conflation, "
        "semantic_strengthening, semantic_weakening(한정 표현 보존 + 원문 어휘 보존율), epistemic_collapse, testimony_to_fact, "
        "temporal_conflation, identity_forcing, closed_set, clause_prop_alignment(05 대조), provenance(04·05 대조).",
        "",
        "### ERROR", _findings_list(findings, "ERROR"), "",
        "### WARN (수동 판정은 §3)", _findings_list(findings, "WARN"), "",
        "### INFO", _findings_list(findings, "INFO"), "",
        "## 2. Fact → Episode 추적표", "",
        "| episode | 제목 | 구성 fact | 인식 floor | 진술/기록 주체 |", "|---|---|---|---|---|",
    ]
    for e in ep_rows:
        cl = f" (절: {e['member_clauses']})" if e["member_clauses"] else ""
        lines.append(f"| {e['episode_id']} | {e['title']} | {e['member_fact_ids'].replace('|', ', ')}{cl} | "
                     f"{e['epistemic_floor']} | {e['attesting_actor']} |")
    lines += ["", "## 3. 수동 의미 검토 (원본 CSV 대조)", "",
              "자동 검사로 잡기 어려운 의미 변화는 episode마다 원문 `confirmed_statement`, `notes`, 대응 05 prop과 대조해 판정했다.", "",
              "| 대상 | 검사 | 판정 | 근거 |", "|---|---|---|---|"]
    for row in AUDIT1_MANUAL:
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## 4. 수정 이력 (Audit → 수정 → 재검사)", "", _revlog(AUDIT1_REVISIONS), "",
              "## 5. confirmed set 밖의 사료 내용 (05에만 있음 — DAG node로 쓰지 않음)", "",
              f"CF가 참조하지 않는 05 prop {len(outside)}개. Stage 4에서는 latent 후보의 `audit_attestation`으로만 인용하고, "
              "인용하더라도 후보는 LATENT로 유지한다.", "",
              "| prop | 기록 | 진술/보고자 | 내용 |", "|---|---|---|---|"]
    for p in outside:
        content = f"{p['subject']} — {p['predicate']}" + (f" ({p['object_or_content']})" if p["object_or_content"] else "")
        lines.append(f"| {p['prop_id']} | {p['source_record_id']} | {p['reporting_actor']} | {content} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit2(path, findings, nodes, edges, links):
    st = Counter(e["status"] for e in edges)
    ty = Counter(e["edge_type"] for e in edges)
    lines = [
        "# AUDIT 2 — Graph Fidelity Audit",
        "",
        "핵심 질문: **원본 사실들을 연결하는 과정에서 원본보다 더 많은 관계를 주장했는가?**",
        "",
        f"- 판정: {_verdict(findings)}",
        f"- node {len(nodes)}개 (episode {sum(n['layer']!='ENVIRONMENT' for n in nodes)}, 환경 context "
        f"{sum(n['layer']=='ENVIRONMENT' for n in nodes)}) · edge {len(edges)}개 · feature link {len(links)}개",
        f"- edge status: {dict(st)}",
        f"- edge type: {dict(ty)}",
        f"- CAUSES edge: {ty.get('CAUSES', 0)}개",
        f"- claim-level edge: {sum(bool(e['claim_level']) for e in edges)}개 · 조건부(identity) edge: "
        f"{sum(bool(e['condition']) for e in edges)}개",
        "",
        "## 1. 자동 검사 요약", "", _counts_table(findings), "",
        "검사 항목: unsupported_edge(근거 fact가 endpoint 구성 fact인지), causal_inflation(CAUSES 금지, 책임은 판단 node로만, "
        "구순→사망 직접 연결 금지), institutional_overreach, environmental_leakage, missing_relation(필수 관계 17개), "
        "judgment_flattening, temporal_inversion, order_execution_conflation, testimony_to_fact(claim_level), "
        "identity_forcing(조건부 edge), acyclicity, latent_leak.",
        "", "### ERROR", _findings_list(findings, "ERROR"), "",
        "### WARN", _findings_list(findings, "WARN"), "",
        "### INFO", _findings_list(findings, "INFO"), "",
        "## 2. 수동 관계 검토 (원본 CSV 대조)", "",
        "| 대상 | 검사 | 판정 | 근거 |", "|---|---|---|---|",
    ]
    for row in AUDIT2_MANUAL:
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## 3. 수정 이력", "", _revlog(AUDIT2_REVISIONS), "",
              "## 4. Edge 전체 목록", "",
              "| edge | src → dst | type | basis | status | claim | cond | 근거 |", "|---|---|---|---|---|---|---|---|"]
    for e in edges:
        lines.append(f"| {e['edge_id']} | {e['src']} → {e['dst']} | {e['edge_type']} | {e['basis'].replace('|', ' + ')} | {e['status']} | "
                     f"{'Y' if e['claim_level'] else ''} | {e['condition'].replace('|', ', ')} | {e['supporting'].replace('|', ', ')} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_mermaid(path, nodes, edges):
    style = {"TEMPORAL_BEFORE": "-.->", "CONTRADICTS_AT_CLAIM_LEVEL": "x--x", "CONTEXT_SUPPORTS": "-.->"}
    lines = ["# Validated Observed Partial DAG (동결본)", "",
             "OBSERVED·DERIVED만 포함한다. LATENT 없음. 점선은 시간·context, x--x는 claim-level 충돌, "
             "실선은 절차·정보·명령·검토·책임 연결이다.", "", "```mermaid", "flowchart TD"]
    by_branch = defaultdict(list)
    for n in nodes:
        by_branch[n["branch"]].append(n)
    for b, ns in by_branch.items():
        lines.append(f"  subgraph {b}")
        for n in ns:
            t = n["title"].replace('"', "'")
            lines.append(f'    {n["node_id"]}["{n["node_id"]} {t}"]')
        lines.append("  end")
    for e in edges:
        arrow = style.get(e["edge_type"], "-->")
        lab = e["edge_type"] + (" ?" + e["condition"].replace("|", ",") if e["condition"] else "")
        if arrow == "x--x":
            lines.append(f"  {e['src']} x--x|{lab}| {e['dst']}")
        else:
            lines.append(f"  {e['src']} {arrow}|{lab}| {e['dst']}")
    lines.append("```")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ----------------------------------------------------------------- Stage 4/5
def _title(nodes, nid):
    for n in nodes:
        if n["node_id"] == nid:
            return f"{nid} {n['title']}"
    return nid


def write_gaps(path, gaps, cands, nodes):
    by = defaultdict(list)
    for c in cands:
        by[c["gap_id"]].append(c)
    lines = ["# STAGE 4 — Gap Detection + Latent Bridge Candidates", "",
             "동결된 observed DAG에서 설명이 실제로 끊기는 곳만 gap으로 지정했다. **아래 후보는 모두 LATENT**이며 사료에서 확인된 사실이 아니다.", "",
             "등급: HIGH / MEDIUM / LOW / INCOMPATIBLE. 확률이 아니다. overall은 다음 규칙으로 기계적으로 정한다. "
             "(1) 평가 차원 중 최소값, (2) contradiction_risk가 HIGH면 LOW 상한, MEDIUM이면 MEDIUM 상한, "
             "(3) 추가 가정 3개 이상이면 MEDIUM 상한, 5개 이상이면 LOW 상한, (4) HIGH는 source_consistency=HIGH일 때만, "
             "(5) 제도 compatibility 또는 환경 context만 근거인 후보는 LOW 상한, "
             "(6) 미확정 동일성(IDxx)에 기대는 후보는 MEDIUM 상한(동일성을 확정하지 않기 위해).", "",
             "`audit_attestation`은 05(AUDIT_ONLY)에 그런 진술·주장이 **기록되어 있다**는 표시일 뿐이다. 후보를 OBSERVED로 올리지 않는다.", "",
             "## Gap 요약", "", "| gap | 유형 | 끊긴 구간 | 후보 수 | 최고 등급 |", "|---|---|---|---|---|"]
    order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "INCOMPATIBLE": 0}
    for g in gaps:
        cs = by[g["gap_id"]]
        best = max((c["overall"] for c in cs), key=lambda x: order[x])
        lines.append(f"| {g['gap_id']} | {g['gap_type']} | {' ↔ '.join(g['between'])} | {len(cs)} | {best} |")
    for g in gaps:
        lines += ["", f"## {g['gap_id']} — {g['title']}", "",
                  f"- 유형: {g['gap_type']}",
                  f"- 끊긴 구간: " + " / ".join(_title(nodes, x) for x in g["between"]),
                  f"- 관측 근거: {g['observed_anchor_facts']}",
                  f"- 왜 gap인가: {g['why_gap']}", ""]
        lines += ["| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for c in by[g["gap_id"]]:
            lines.append(f"| {c['candidate_id']} | {c['label']} | {c['source_consistency']} | {c['temporal_fit']} | "
                         f"{c['institutional_fit']} | {c['role_fit']} | {c['information_flow_fit']} | {c['environmental_fit']} | "
                         f"{c['contradiction_risk']} | {c['n_assumptions']} | **{c['overall']}** | {c['prune_decision']} |")
        for c in by[g["gap_id"]]:
            lines += ["", f"### {c['candidate_id']} [LATENT · {c['form']}] {c['label']}", "", c["description"], ""]
            if c["latent_nodes"] or c["latent_edges"]:
                lines.append("latent 요소:")
                for ln in c["latent_nodes"]:
                    lines.append(f"- `{ln['id']}` {ln['text']}")
                for le in c["latent_edges"]:
                    lines.append(f"- `{le['src']}` —{le['edge_type']}→ `{le['dst']}` (LATENT)")
            lines += ["", f"- 추가 가정: " + ("; ".join(c["extra_assumptions"]) if c["extra_assumptions"] else "없음"),
                      f"- 지지 fact: {c['supports'] or '-'} · 긴장/충돌 fact: {c['conflicts'] or '-'}",
                      f"- audit_attestation (05, AUDIT_ONLY): {c['audit_attestation'] or '-'}",
                      f"- 미확정 동일성 조건: {c['identity_conditions'] or '없음'}",
                      f"- 주 근거 유형: {c['support_basis']}",
                      f"- 메모: {c['notes']}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_worlds(path, worlds, cands, gaps, nodes):
    cand = {c["candidate_id"]: c for c in cands}
    gap_t = {g["gap_id"]: g["title"] for g in gaps}
    lines = ["# STAGE 5 — Narrative Worlds", "",
             "동결된 observed backbone 위에 검증된 latent 후보를 **제한적으로** 얹은 설명 경로다. 하나의 정답 세계를 고르려는 것이 아니다. "
             f"모든 world는 같은 observed backbone(node {len(nodes)}개 · 동결 해시 동일)을 공유하고, latent bridge만 다르다.", "",
             "구성 방식: 전수 조합이 아니다. gap별 후보(최대 5개) 가운데 설명 축(정보 경로, 강요 진술, 사적 경로, 지휘 분산, 최소 가정)이 "
             "서로 다르도록 직접 고른 뒤, 같은 gap에 후보 2개 이상 금지, INCOMPATIBLE 사용 금지, world 사이 최소 2개 gap에서 차이를 검사했다. "
             "SMC·MCMC·posterior sampling은 쓰지 않았다.", "",
             "## 비교표", "", "| world | 이름 | bridge 수 | 미해결 gap | 제도 적합 | 환경 적합 | 가정 수 | 최저 후보 등급 | 상태 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for w in worlds:
        lines.append(f"| {w['world_id']} | {w['name']} | {len(w['latent_bridges'])} | {len(w['unresolved_gaps'])} | "
                     f"{w['institutional_fit']} | {w['environmental_fit']} | {w['n_assumptions']} | {w['min_grade']} | "
                     f"{'REJECTED' if w.get('rejected') else 'RETAINED'} |")
    for w in worlds:
        lines += ["", f"## {w['world_id']} — {w['name']}" + (" (REJECTED — 대조용)" if w.get("rejected") else ""), "",
                  f"**story_implication** — {w['story_implication']}", "",
                  f"- observed_backbone: {w['observed_backbone']}",
                  "- latent_bridges (모두 LATENT):"]
        for b in w["latent_bridges"]:
            c = cand[b]
            lines.append(f"  - `{b}` [{c['overall']}] ({c['gap_id']} {gap_t[c['gap_id']]}) {c['label']}")
        lines += [f"- 미해결로 남긴 gap: {', '.join(w['unresolved_gaps']) or '없음'}",
                  f"- institutional_fit: {w['institutional_fit']} — {w['institutional_note']}",
                  f"- environmental_fit: {w['environmental_fit']} — {w['environmental_note']}",
                  "- main_assumptions:"] + [f"  - {a}" for a in w["main_assumptions"]] + \
                 ["- main_weaknesses:"] + [f"  - {a}" for a in w["main_weaknesses"]] + \
                 [f"- contradicted_evidence: {w['contradicted_evidence']}"]
        if w.get("narrative"):
            lines += ["", "서술 (`[L]` = LATENT bridge, 나머지는 observed backbone):", "", w["narrative"]]
    from stage5_worlds import ADJUSTMENTS, CONFLICT_PAIRS
    lines += ["", "## 상충 후보 쌍 (서로 다른 gap이지만 한 world에 함께 쓰지 않음)", "", "| 후보 A | 후보 B | 이유 |", "|---|---|---|"]
    lines += [f"| {a} | {b} | {why} |" for a, b, why in CONFLICT_PAIRS]
    lines += ["", "## 처음 지정한 구성 대비 조정", "", "| world | 조정·확인 |", "|---|---|"]
    lines += [f"| {w} | {t} |" for w, t in ADJUSTMENTS]
    lines += ["", "## world 사이 차이 (gap별 선택)", "", "| gap | " + " | ".join(w["world_id"] for w in worlds) + " |",
              "|---|" + "---|" * len(worlds)]
    for g in gaps:
        row = []
        for w in worlds:
            pick = [b for b in w["latent_bridges"] if cand[b]["gap_id"] == g["gap_id"]]
            row.append(pick[0] if pick else "·")
        lines.append(f"| {g['gap_id']} | " + " | ".join(row) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit3(path, findings, nodes, edges, gaps, cands, worlds, frozen):
    st_n = Counter(n["node_status"] for n in nodes)
    st_e = Counter(e["status"] for e in edges)
    n_ln = sum(len(c["latent_nodes"]) for c in cands)
    n_le = sum(len(c["latent_edges"]) for c in cands)
    leaks = sum(f["check"] == "latent_as_observed" and f["severity"] == "ERROR" for f in findings)
    lines = ["# AUDIT 3 — Observed / Derived / Latent Separation", "",
             "핵심 질문: **추론한 것을 사료에서 확인된 사실처럼 표시했는가?**", "",
             f"- 판정: {_verdict(findings)}",
             f"- LATENT → OBSERVED 둔갑: **{leaks}건**",
             f"- 동결 해시: `{frozen}` (Stage 4·5 뒤에도 observed DAG 변경 없음)", "",
             "## 1. 분류 집계", "",
             "| 층 | node | edge | 위치 |", "|---|---|---|---|",
             f"| OBSERVED | {st_n['OBSERVED']} (episode·환경 행) | {st_e['OBSERVED']} | episode_nodes.csv / observed_edges.csv |",
             f"| DERIVED | 0 (node는 만들지 않음) | {st_e['DERIVED']} | observed_edges.csv (status=DERIVED) |",
             f"| LATENT | {n_ln} | {n_le} | latent_candidates.csv / latent_elements.csv / gap_candidates.md |", "",
             "DERIVED는 원본에 한 문장으로 쓰여 있지는 않지만 원본 정보에서 안전하게 도출되는 구조적 관계만 가리킨다"
             "(명시 날짜의 시간 순서, 같은 기사 안의 절차 순서, 판단 문구와 episode의 대응). "
             "모든 episode node는 OBSERVED이며 원본 CF에서만 만들었다.", "",
             "## 2. 자동 검사 요약", "", _counts_table(findings), "",
             "### ERROR", _findings_list(findings, "ERROR"), "", "### WARN", _findings_list(findings, "WARN"), "",
             "### INFO", _findings_list(findings, "INFO"), "",
             "## 3. 수동 검토", "", "| 대상 | 검사 | 판정 | 근거 |", "|---|---|---|---|"]
    for row in AUDIT3_MANUAL:
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## 4. 수정 이력", "", _revlog(AUDIT3_REVISIONS), "",
              "## 5. 전체 요소 분류표", "", "| id | 종류 | 분류 | 출처 |", "|---|---|---|---|"]
    for n in nodes:
        lines.append(f"| {n['node_id']} | node | OBSERVED | {n['member_fact_ids'].replace('|', ', ') or n.get('env_id')} |")
    for e in edges:
        lines.append(f"| {e['edge_id']} | edge | {e['status']} | {e['supporting'].replace('|', ', ')} |")
    for c in cands:
        for ln in c["latent_nodes"]:
            lines.append(f"| {ln['id']} | node | LATENT | {c['candidate_id']} |")
        for i, le in enumerate(c["latent_edges"], 1):
            lines.append(f"| {c['candidate_id']}.e{i} | edge | LATENT | {le['src']}→{le['dst']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_latent_csv(out, gaps, cands, worlds):
    with open(out / "gaps.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gap_id", "title", "gap_type", "between", "observed_anchor_facts", "why_gap"])
        for g in gaps:
            w.writerow([g["gap_id"], g["title"], g["gap_type"], "|".join(g["between"]), g["observed_anchor_facts"], g["why_gap"]])
    cols = ["candidate_id", "gap_id", "status", "form", "label", "description", "source_consistency", "temporal_fit",
            "institutional_fit", "role_fit", "information_flow_fit", "environmental_fit", "contradiction_risk",
            "n_assumptions", "extra_assumptions", "identity_conditions", "overall", "prune_decision", "supports", "conflicts",
            "audit_attestation", "support_basis", "notes"]
    with open(out / "latent_candidates.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for c in cands:
            w.writerow([("; ".join(c[k]) if k == "extra_assumptions" else c[k]) for k in cols])
    with open(out / "latent_elements.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["element_id", "candidate_id", "kind", "status", "src", "dst", "edge_type", "text"])
        for c in cands:
            for ln in c["latent_nodes"]:
                w.writerow([ln["id"], c["candidate_id"], "node", "LATENT", "", "", "", ln["text"]])
            for i, le in enumerate(c["latent_edges"], 1):
                w.writerow([f"{c['candidate_id']}.e{i}", c["candidate_id"], "edge", "LATENT", le["src"], le["dst"],
                            le["edge_type"], ""])
    with open(out / "narrative_worlds.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["world_id", "name", "status", "latent_bridges", "unresolved_gaps", "institutional_fit",
                    "environmental_fit", "n_assumptions", "min_grade", "main_assumptions", "main_weaknesses",
                    "contradicted_evidence", "story_implication", "identity_conditions", "narrative"])
        for x in worlds:
            w.writerow([x["world_id"], x["name"], "REJECTED" if x.get("rejected") else "RETAINED",
                        "|".join(x["latent_bridges"]), "|".join(x["unresolved_gaps"]), x["institutional_fit"],
                        x["environmental_fit"], x["n_assumptions"], x["min_grade"], " / ".join(x["main_assumptions"]),
                        " / ".join(x["main_weaknesses"]), x["contradicted_evidence"], x["story_implication"],
                        x.get("identity_conditions", ""), x.get("narrative", "")])
