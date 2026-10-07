"""Markdown / CSV / Mermaid 출력."""
import csv
from collections import Counter, defaultdict

from manual_review import (AUDIT1_MANUAL, AUDIT1_REVISIONS, AUDIT2_MANUAL, AUDIT2_REVISIONS, AUDIT3_MANUAL,
                           AUDIT3_REVISIONS, WARN_DISPOSITIONS)

DISPOSITION_COLS = ["warning_id", "audit_stage", "affected_item", "warning_type", "original_text", "generated_text", "risk",
                    "disposition", "justification", "fixed_text", "final_status", "final_classification", "unresolved_reason"]
SEVS = ["ERROR", "WARN", "UNRESOLVED", "INFO"]


def _cell(x):
    return str(x).replace("|", "/").replace("\n", " ")


def _disposition_table(stage):
    ds = [d for d in WARN_DISPOSITIONS if d["audit_stage"] == stage]
    lines = ["모든 WARN은 FIXED / RECLASSIFIED_INFO / UNRESOLVED / ESCALATED_ERROR 중 하나로 처리했다. disposition이 없는 WARN이 남으면 "
             "build.py가 멈춘다. 전체 표는 `warn_dispositions.csv`에 있다.", ""]
    if not ds:
        return "\n".join(lines + ["_이 audit에서는 처리 대상 WARN이 발생하지 않았다(모든 실행에서 WARN 0)._"])
    cols = ["warning_id", "audit_stage", "affected_item", "warning_type", "original_text", "generated_text", "risk",
            "disposition", "justification", "final_status"]
    lines += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for d in ds:
        lines.append("| " + " | ".join(_cell(d[c]) for c in cols) + " |")
    lines += ["", "수정 후 문구 / 최종 분류:", ""]
    for d in ds:
        lines.append(f"- **{d['warning_id']}** → {_cell(d['fixed_text'])} · 최종 분류: {d['final_classification']}")
    return "\n".join(lines)


def _unresolved_list(findings):
    fs = [f for f in findings if f["severity"] == "UNRESOLVED"]
    if not fs:
        return "_없음_"
    return "\n".join(f"- `{f['check']}` **{f['target']}** — {_cell(f['message'])}" for f in fs)


def _counts_table(findings):
    c = defaultdict(Counter)
    for f in findings:
        c[f["check"]][f["severity"]] += 1
    lines = ["| check | ERROR | WARN | UNRESOLVED | INFO |", "|---|---|---|---|---|"]
    for k in sorted(c):
        lines.append(f"| {k} | {c[k]['ERROR']} | {c[k]['WARN']} | {c[k]['UNRESOLVED']} | {c[k]['INFO']} |")
    t = Counter(f["severity"] for f in findings)
    lines.append(f"| **합계** | **{t['ERROR']}** | **{t['WARN']}** | **{t['UNRESOLVED']}** | **{t['INFO']}** |")
    return "\n".join(lines)


def _findings_list(findings, sev):
    fs = [f for f in findings if f["severity"] == sev]
    if not fs:
        return "_없음_"
    return "\n".join(f"- `{f['check']}` **{f['target']}** — {f['message']}" for f in fs)


def _verdict(findings):
    c = Counter(f["severity"] for f in findings)
    if c["ERROR"] == 0 and c["WARN"] == 0:
        return f"**PASS** (ERROR 0 · WARN 0 · UNRESOLVED {c['UNRESOLVED']} · INFO {c['INFO']})"
    return f"**FAIL** (ERROR {c['ERROR']} · WARN {c['WARN']})"


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
    lines += ["", "## 3-1. WARN disposition", "", _disposition_table("AUDIT1"), "",
              "## 3-2. UNRESOLVED (사료 자체의 모호성 — 허용, 데이터에 보존)", "", _unresolved_list(findings), ""]
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
    lines += ["", "## 2-1. WARN disposition", "", _disposition_table("AUDIT2"), "",
              "## 2-2. UNRESOLVED (사료 자체의 모호성 — 허용, 데이터에 보존)", "", _unresolved_list(findings), ""]
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
             "등급은 확률이 아니다. LATENT 재감사 이후 두 축으로 나누어 평가한다(자세한 before/after는 `latent_candidate_reaudit.md`).", "",
             "- **source support (evidence_grade)**: 후보가 새로 추가한 bridge 내용 자체를 사료가 얼마나 직접 지지하는가(HIGH/MEDIUM/LOW/NONE). "
             "양끝 OBSERVED 사실의 확실성, 시간 인접성, 제도 가능성은 근거가 아니다. endpoint node의 구성 fact는 bridge 근거로 쓰지 않는다. "
             "audit-only 근거만 있으면 MEDIUM이 상한이다.",
             "- **plausibility_grade**: 시간·제도·역할·정보흐름·환경 적합의 최소값. 추가 가정 3개 이상이면 MEDIUM 상한, 5개 이상이면 LOW 상한이다. "
             "미확정 동일성에 기대면 MEDIUM 상한이다.",
             "- **overall(final)** = min(evidence, plausibility). evidence NONE은 LOW로 친다. contradiction_risk가 HIGH면 LOW 상한, MEDIUM이면 MEDIUM 상한이다. "
             "제도·환경만 근거이면 LOW 상한이다. 사용자 확정 동일성을 부정하는 후보는 INCOMPATIBLE이다. "
             "HIGH는 evidence와 plausibility가 모두 HIGH일 때만 나온다.", "",
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
        lines += ["| 후보 | 요약 | bridge 직접? | source support | temp | inst | role | info | env | 충돌위험 | 가정 | evidence | plausibility | overall | 처리 |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for c in by[g["gap_id"]]:
            lines.append(f"| {c['candidate_id']} | {c['label']} | {c['bridge_directly_attested']} | {c['source_support']} | {c['temporal_fit']} | "
                         f"{c['institutional_fit']} | {c['role_fit']} | {c['information_flow_fit']} | {c['environmental_fit']} | "
                         f"{c['contradiction_risk']} | {c['n_assumptions']} | {c['evidence_grade']} | {c['plausibility_grade']} | "
                         f"**{c['overall']}** | {c['prune_decision']} |")
        for c in by[g["gap_id"]]:
            lines += ["", f"### {c['candidate_id']} [LATENT · {c['form']}] {c['label']}", "", c["description"], ""]
            if c["latent_nodes"] or c["latent_edges"]:
                lines.append("latent 요소:")
                for ln in c["latent_nodes"]:
                    lines.append(f"- `{ln['id']}` {ln['text']}")
                for le in c["latent_edges"]:
                    lines.append(f"- `{le['src']}` —{le['edge_type']}→ `{le['dst']}` (LATENT)")
            lines += ["", f"- observed_left: {c['observed_left']}", f"- observed_right: {c['observed_right']}",
                      f"- latent_bridge_claim: {c['latent_bridge_claim']}",
                      f"- bridge 직접 근거: {c['bridge_directly_attested']} · source support {c['source_support']} "
                      f"(근거: {c['bridge_evidence'].replace('|', ', ') or '없음'} · 유형 {c['bridge_basis'].replace('|', ', ')}) · "
                      f"endpoint support {c['endpoint_support']}",
                      f"- 재감사 사유: {c['reaudit_reason']}"]
            lines += ["", f"- 추가 가정: " + ("; ".join(c["extra_assumptions"]) if c["extra_assumptions"] else "없음"),
                      f"- 지지 fact: {c['supports'] or '-'} · 긴장/충돌 fact: {c['conflicts'] or '-'}",
                      f"- audit_attestation (05, AUDIT_ONLY): {c['audit_attestation'] or '-'}",
                      f"- 미확정 동일성 조건: {c['identity_conditions'] or '없음'}",
                      f"- 주 근거 유형: {c['support_basis']}",
                      f"- 메모: {c['notes']}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _outcome_rows(nodes):
    from stage5_worlds import COMMON_OUTCOME_NODES
    by = {n["node_id"]: n for n in nodes}
    rows = []
    for phase, ids in COMMON_OUTCOME_NODES.items():
        for x in ids:
            n = by[x]
            rows.append((phase, x, n["occurrence_text"], n["summary"], n["member_fact_ids"].replace("|", ", ")))
    return rows


def _usage_section():
    return ["## Narrative Worlds를 작품에서 사용하는 방식", "",
            "### 원칙 1 — 세계들은 서로 다른 설명 가설이다",
            "W1–W5는 같은 OBSERVED 골격 위에서, 사료가 알려 주지 않은 중간 과정을 서로 다르게 채운 가설이다. "
            "하나의 정답 후보가 아니라 경쟁하는 사건 설명으로 함께 보존한다. 서로 배타적이거나 긴장하는 LATENT 가설은 각 world 안에서만 유지하고, "
            "여러 world의 가설을 동시에 역사적 사실로 합치지 않는다.", "",
            "### 원칙 2 — 조사 단계에 따라 서로 다른 world가 차례로 제시될 수 있다",
            "아래는 구조 설명용 예시다. 새 사건을 만들지 않는다.", "",
            "| 작품 속 단계 | 제시될 수 있는 설명 |", "|---|---|",
            "| 초기 조사 | W2처럼 보임: 구류·대질 진술이 수사를 넓힌 듯한 인상 |",
            "| 다른 증언 검토 | W3 가능성이 제기됨: 기록되지 않은 사적 통로의 의심 |",
            "| 기관별 기록 비교 | W4 가능성이 드러남: 진영·병영·공주진·의금부가 따로 움직인 흔적 |",
            "| 정조 최종 판단 | W1과 가까운 책임 구조가 제시됨: 구순·이광섭 책임 판단(CF043·CF044) |",
            "| 끝까지 확인되지 않는 부분 | W5처럼 빈칸으로 남김 |", "",
            "### 원칙 3 — 한 world가 다른 world를 이긴다고 쓰지 않는다",
            "비교는 다음 축으로만 한다: 어떤 설명은 bridge의 사료 근거가 더 강하다(evidence). 어떤 설명은 제도적으로 더 자연스럽다(plausibility). "
            "어떤 설명은 가정이 더 적다(가정 수). 어떤 설명은 특정 증언을 더 많이 활용한다.", "",
            "### 원칙 4 — 사료가 결정하지 않은 부분은 끝까지 '확정되지 않음'으로 남길 수 있다",
            "UNRESOLVED 동일성(ID06·ID07·ID08), 부분 충돌(OE007), 범위 미확정(OE062), 열린 gap(G10)은 어느 world에서도 확정하지 않는다.", ""]


def write_worlds(path, worlds, cands, gaps, nodes):
    cand = {c["candidate_id"]: c for c in cands}
    gap_t = {g["gap_id"]: g["title"] for g in gaps}
    comp = [w for w in worlds if w["role_type"] == "COMPETING_EXPLANATION"]
    rej = [w for w in worlds if w["role_type"] == "REJECTED"]
    lines = ["# STAGE 5 — Narrative Worlds (경쟁하는 사건 설명)", "",
             "이 문서는 world 하나를 승자로 고르기 위한 것이 아니다. W1–W5는 작품에서 함께 쓸 수 있는 **경쟁하는 사건 설명**이고, "
             "W6은 **검토했지만 배제된 설명**이다.", "",
             "```",
             "[확정된 OBSERVED 사건]            ← 모든 world 공통",
             "        ↓",
             "[사료가 알려주지 않은 중간 과정]   ← world마다 다른 LATENT bridge",
             "        ├─ W1  ├─ W2  ├─ W3  ├─ W4  └─ W5",
             "        ↓",
             "[확정된 재검토·책임 판단·처분]      ← 모든 world 공통 (결말은 world마다 바뀌지 않는다)",
             "```", "",
             f"- 모든 world는 같은 동결 observed graph(node {len(nodes)}개)를 공유한다. LATENT bridge만 다르다.",
             "- 서로 다른 world의 LATENT 가설을 하나로 합치지 않는다. 각 가설은 그 world 안에서만 유지된다.",
             "- 구성 방식: 전수 조합이 아니다. 설명 축이 서로 다르도록 직접 골랐다. 같은 gap에 후보 2개 이상 금지, INCOMPATIBLE 금지, "
             "world 사이 최소 2개 gap에서 차이가 나도록 했다. SMC·MCMC·posterior sampling은 쓰지 않았다.", "",
             "## 모든 world에 공통인 OBSERVED 결말", "",
             "아래 재검토·판단·처분은 world별 결과가 아니다. 모든 world에 공통인 관측 사실이고, world들은 여기에 이르기 전의 미확인 경로만 다르게 설명한다.", "",
             "| 단계 | node | 시점 | 기록 내용 | 근거 fact |", "|---|---|---|---|---|"]
    for phase, x, t, summ, facts in _outcome_rows(nodes):
        lines.append(f"| {phase} | {x} | {_cell(t)} | {_cell(summ)} | {facts} |")
    lines += ["", "## 경쟁하는 설명 W1–W5 비교", "",
              "| World | 작품에서의 역할 | 공통 OBSERVED 골격 | 이 world만 추가하는 LATENT | 추가 가정 수 | evidence 분포 | 가장 약한 점 | 다른 world와 다른 점 | 작품에서 보여주는 질문 |",
              "|---|---|---|---|---|---|---|---|---|"]
    for w in comp:
        uniq = ", ".join(f"{b}({cand[b]['evidence_grade']})" for b in w["unique_bridges"]) or "없음(다른 world와 공유하는 bridge만 사용)"
        weak = w["main_weaknesses"][0] if w["main_weaknesses"] else ""
        lines.append(f"| {w['world_id']} | {_cell(w['work_role'])} | 동결 observed graph 전체 + 공통 결말 | {uniq} | {w['n_assumptions']} | "
                     f"{w.get('evidence_profile', '')} | {_cell(weak)} | {_cell(w['difference'])} | {_cell(w['story_question'])} |")
    lines += ["", "## 검토했지만 배제된 설명", "", "| World | status | 역할 | 사용 bridge | 배제 이유 |", "|---|---|---|---|---|"]
    for w in rej:
        lines.append(f"| {w['world_id']} | REJECTED | {_cell(w['work_role'])} | {' '.join(w['latent_bridges'])} | {_cell(w['contradicted_evidence'])} |")
    lines += [""] + _usage_section()
    lines += ["## 수치 비교 (참고)", "", "| world | 이름 | bridge 수 | 미해결 gap | 제도 적합 | 환경 적합 | 가정 수 | bridge 근거 등급 분포 | 최저 후보 등급 | 구분 |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for w in worlds:
        lines.append(f"| {w['world_id']} | {w['name']} | {len(w['latent_bridges'])} | {len(w['unresolved_gaps'])} | "
                     f"{w['institutional_fit']} | {w['environmental_fit']} | {w['n_assumptions']} | {w.get('evidence_profile', '')} | {w['min_grade']} | "
                     f"{w['role_type']} |")
    for w in worlds:
        lines += ["", f"## {w['world_id']} — {w['name']}" + (" (REJECTED — 검토했지만 배제된 설명)" if w.get("rejected") else " (경쟁하는 설명)"), "",
                  f"**작품에서의 역할** — {w['work_role']}", "",
                  f"**작품에서 보여주는 질문** — {w['story_question']}", "",
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
    lines += ["", "## 3-1. WARN disposition", "", _disposition_table("AUDIT3"), "",
              "## 3-2. UNRESOLVED (사료 자체의 모호성 — 허용, 데이터에 보존)", "", _unresolved_list(findings), ""]
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
        w.writerow(["gap_id", "title", "gap_type", "between", "observed_anchor_facts", "why_gap", "gap_status", "review_decision"])
        for g in gaps:
            w.writerow([g["gap_id"], g["title"], g["gap_type"], "|".join(g["between"]), g["observed_anchor_facts"], g["why_gap"],
                        g.get("gap_status", ""), g.get("review_decision", "")])
    cols = ["candidate_id", "gap_id", "status", "form", "label", "description", "source_consistency", "temporal_fit",
            "institutional_fit", "role_fit", "information_flow_fit", "environmental_fit", "contradiction_risk",
            "n_assumptions", "extra_assumptions", "identity_conditions", "overall", "prune_decision", "supports", "conflicts",
            "audit_attestation", "support_basis", "notes", "observed_left", "observed_right", "latent_bridge_claim",
            "bridge_directly_attested", "endpoint_support", "source_support", "bridge_evidence", "bridge_basis", "evidence_grade",
            "plausibility_grade", "source_consistency_v1", "overall_v1", "reaudit_reason"]
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
                    "contradicted_evidence", "story_implication", "identity_conditions", "resolved_identities", "evidence_profile",
                    "work_role", "story_question", "difference", "unique_bridges", "narrative"])
        for x in worlds:
            w.writerow([x["world_id"], x["name"], x["role_type"],
                        "|".join(x["latent_bridges"]), "|".join(x["unresolved_gaps"]), x["institutional_fit"],
                        x["environmental_fit"], x["n_assumptions"], x["min_grade"], " / ".join(x["main_assumptions"]),
                        " / ".join(x["main_weaknesses"]), x["contradicted_evidence"], x["story_implication"],
                        x.get("identity_conditions", ""), x.get("resolved_identities", ""), x.get("evidence_profile", ""),
                        x["work_role"], x["story_question"], x["difference"], "|".join(x["unique_bridges"]), x.get("narrative", "")])


def write_validation_summary(path, audits_by_name, freeze, worlds, cands=None):
    import regression
    lines = ["# Validation Summary", "",
             "통과 조건: 각 Audit의 ERROR = 0, WARN = 0. INFO와 UNRESOLVED는 허용하되, UNRESOLVED는 사료 자체의 불확실성 때문에 남은 것이어야 한다.", "",
             "```"]
    ok = True
    for name, fs in audits_by_name.items():
        c = Counter(f["severity"] for f in fs)
        ok &= c["ERROR"] == 0 and c["WARN"] == 0
        lines += [f"{name}:", f"ERROR = {c['ERROR']}", f"WARN = {c['WARN']}", f"INFO = {c['INFO']}",
                  f"UNRESOLVED = {c['UNRESOLVED']}", ""]
    lines += ["```", "", f"판정: **{'PASS' if ok else 'FAIL'}**", "",
              "## WARN disposition 집계", "", "| disposition | 건수 | 항목 |", "|---|---|---|"]
    by = defaultdict(list)
    for d in WARN_DISPOSITIONS:
        by[d["disposition"]].append(d["warning_id"])
    for k in ["FIXED", "RECLASSIFIED_INFO", "UNRESOLVED", "ESCALATED_ERROR"]:
        lines.append(f"| {k} | {len(by[k])} | {', '.join(by[k]) or '-'} |")
    idr = list(csv.DictReader(open(path.parent / "identity_register.csv", encoding="utf-8")))
    cnt = Counter(r["status"] for r in idr)
    lines += ["", "## 동일성 상태", "",
              f"RESOLVED(사용자 확정) {cnt['RESOLVED']}개 · UNRESOLVED {cnt['UNRESOLVED']}개 "
              f"(그중 사용자 판단 필요 {sum(r['status'] == 'UNRESOLVED' and r['manual_decision_required'] == 'YES' for r in idr)}개) · "
              f"기타 {len(idr) - cnt['RESOLVED'] - cnt['UNRESOLVED']}개", "",
              "| ID | 동일성 | status | 모델 사용처 | 사용자 판단 필요 | 검토 결정 |", "|---|---|---|---|---|---|"]
    for r in idr:
        lines.append(f"| {r['identity_id']} | {_cell(r['surface_a'])} ↔ {_cell(r['surface_b'])} | {r['status']} | "
                     f"{_cell(r['model_relevance'])} | {r['manual_decision_required']} | {_cell(r.get('review_decision', ''))} |")
    if cands:
        from collections import Counter as C
        sa, fa = C(c["source_support"] for c in cands), C(c["overall"] for c in cands)
        lines += ["", "## LATENT 후보 재감사 (bridge 자체의 사료 근거)", "",
                  f"- source support: HIGH {sa['HIGH']} · MEDIUM {sa['MEDIUM']} · LOW {sa['LOW']} · NONE {sa['NONE']}",
                  f"- final grade: HIGH {fa['HIGH']} · MEDIUM {fa['MEDIUM']} · LOW {fa['LOW']} · INCOMPATIBLE {fa['INCOMPATIBLE']}",
                  f"- source support가 바뀐 후보 {sum(c['source_consistency_v1'] != c['source_support'] for c in cands)}개, "
                  f"final이 바뀐 후보 {sum(c['overall_v1'] != c['overall'] for c in cands)}개. 상세: `latent_candidate_reaudit.md`",
                  "- 검사: bridge_support_inflation · temporal_inflation · institutional_inflation · endpoint_leakage · latent_classification (모두 ERROR 0)"]
    lines += ["", "## UNRESOLVED 목록", ""]
    for name, fs in audits_by_name.items():
        lines += [f"### {name}", "", _unresolved_list(fs), ""]
    res = regression.run()
    lines += ["## Regression validation rules", "",
              f"build.py는 Audit 1 전에 아래 케이스를 검사기에 넣어 모두 ERROR로 잡히는지 확인한다({sum(r['caught'] for r in res)}/{len(res)} 탐지).", "",
              "| rule | 케이스 | 탐지 |", "|---|---|---|"]
    for r in res:
        lines.append(f"| {r['rule']} | {_cell(r['case'])} | {'OK' if r['caught'] else 'MISSED'} |")
    lines += ["", "## 동결 그래프", "",
              f"- 현재 sha256: `{freeze['sha256']}`",
              f"- 직전 sha256(앞자리): `{freeze['previous_sha256_prefix']}…`",
              f"- 구조 sha256(문구 제외): `{freeze['structure_sha256']}` — 이전과 "
              f"{'동일' if freeze['structure_unchanged'] else '다름'}",
              f"- topology sha256(id·끝점·type): `{freeze['topology_sha256']}` — 이전과 {'동일' if freeze['topology_unchanged'] else '다름'}",
              f"- 변경 내용: {freeze['change_note']}",
              "", "## Narrative worlds", "", "| world | 상태 | bridge | 최저 등급 | bridge 근거 등급 분포 | 가정 수 | 미확정 동일성 의존 | 미해결 gap |", "|---|---|---|---|---|---|---|---|"]
    for w in worlds:
        lines.append(f"| {w['world_id']} | {w['role_type']} | {' '.join(w['latent_bridges'])} | "
                     f"{w['min_grade']} | {w.get('evidence_profile', '')} | {w['n_assumptions']} | {w['identity_conditions'].replace('|', ', ') or '0'} | "
                     f"{', '.join(w['unresolved_gaps']) or '-'} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reaudit(path, cands, worlds_new, worlds_old):
    from collections import Counter as C
    lv = ["HIGH", "MEDIUM", "LOW", "NONE", "INCOMPATIBLE"]
    sb, sa = C(c["source_consistency_v1"] for c in cands), C(c["source_support"] for c in cands)
    fb, fa = C(c["overall_v1"] for c in cands), C(c["overall"] for c in cands)
    ch_s = [c for c in cands if c["source_consistency_v1"] != c["source_support"]]
    ch_f = [c for c in cands if c["overall_v1"] != c["overall"]]
    L = ["# LATENT 후보 재감사 — bridge 자체의 사료 근거", "",
         "문제: 일부 후보는 양끝 OBSERVED 사실이 확실하다는 이유로, 그 사이에 넣은 LATENT bridge의 source support까지 높게 받았다. "
         "이번 재감사는 38개 후보 전부에 대해 **후보가 새로 추가한 내용 자체**의 사료 근거만 다시 평가했다. "
         "새 역사적 사실은 만들지 않았고, OBSERVED·DERIVED·LATENT 경계도 바꾸지 않았다.", "",
         "## 평가 원칙", "",
         "- source support의 근거가 아닌 것: 양끝 OBSERVED 사건의 확실성(→ endpoint_support), 시간 인접성(→ temporal_fit), "
         "제도상 가능성(→ institutional_fit), 정보 경로의 자연스러움(→ information_flow_fit), 정조 최종 판단과의 정합.",
         "- endpoint node의 구성 fact는 bridge 근거로 쓰지 않는다(endpoint leakage는 Audit 3 ERROR).",
         "- HIGH: bridge 내용 자체가 사료 문장으로 강하게 지지된다(이 경우 LATENT 분류부터 다시 점검). MEDIUM: bridge 자체는 없지만 같은 사건의 "
         "비-endpoint 사료나 직접 연결되는 진술이 상당히 지지한다(audit-only 근거만 있으면 상한). LOW: 직접 근거 없이 시간·제도·주변 사실에서 나온 추론이다. "
         "NONE: 제도상 가능성이나 이야기상 자연스러움 말고는 근거가 없다.",
         "- 최종 등급 = min(evidence_grade, plausibility_grade) + 충돌·근거유형·동일성 상한. 확률 수치는 만들지 않았다.", "",
         "## 요약", "",
         f"- source support가 바뀐 후보: **{len(ch_s)}개 / {len(cands)}개**",
         f"- final grade가 바뀐 후보: **{len(ch_f)}개** ({', '.join(c['candidate_id'] for c in ch_f)})",
         f"- HIGH 후보(final): {fb['HIGH']}개 → **{fa['HIGH']}개**", "",
         "| 등급 | source support 이전 | source support 이후 | final 이전 | final 이후 |", "|---|---|---|---|---|"]
    for k in lv:
        L.append(f"| {k} | {sb[k]} | {sa[k]} | {fb[k]} | {fa[k]} |")
    L += ["", "이전 source 값에는 NONE 등급이 없었다. 이전의 INCOMPATIBLE 1개는 G04e의 source 칸 값이다.", "",
          "## 집중 재검토 4건 (이전 HIGH)", "",
          "| 후보 | observed_left | observed_right | latent_bridge_claim | bridge 직접? | endpoint support | source support | final | 사유 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for cid in ("G01a", "G06a", "G07a", "G08a"):
        c = next(x for x in cands if x["candidate_id"] == cid)
        L.append(f"| {cid} | {_cell(c['observed_left'])} | {_cell(c['observed_right'])} | {_cell(c['latent_bridge_claim'])} | "
                 f"{c['bridge_directly_attested']} | {_cell(c['endpoint_support'])} | {c['source_consistency_v1']} → **{c['source_support']}** | "
                 f"{c['overall_v1']} → **{c['overall']}** | {_cell(c['reaudit_reason'])} |")
    L += ["", "## 38개 후보 before / after", "",
          "| candidate | old source support | new source support | old final grade | new final grade | changed? | reason |",
          "|---|---|---|---|---|---|---|"]
    for c in cands:
        chg = []
        if c["source_consistency_v1"] != c["source_support"]:
            chg.append("source")
        if c["overall_v1"] != c["overall"]:
            chg.append("final")
        L.append(f"| {c['candidate_id']} | {c['source_consistency_v1']} | {c['source_support']} | {c['overall_v1']} | {c['overall']} | "
                 f"{'YES (' + '·'.join(chg) + ')' if chg else 'no'} | {_cell(c['reaudit_reason'])} |")
    L += ["", "## 38개 후보 전체 재감사표", "",
          "| candidate_id | gap_id | observed_left | observed_right | latent_bridge_claim | bridge_directly_attested | endpoint_support | "
          "source_support | institutional_fit | temporal_fit | information_flow_fit | assumption_cost | contradiction_risk | final_grade | reason |",
          "|" + "---|" * 15]
    for c in cands:
        L.append("| " + " | ".join(_cell(x) for x in [
            c["candidate_id"], c["gap_id"], c["observed_left"], c["observed_right"], c["latent_bridge_claim"],
            c["bridge_directly_attested"], c["endpoint_support"], c["source_support"], c["institutional_fit"], c["temporal_fit"],
            c["information_flow_fit"], c["n_assumptions"], c["contradiction_risk"], c["overall"],
            f"evidence {c['evidence_grade']} · plausibility {c['plausibility_grade']} · 근거 {c['bridge_evidence'] or '없음'} — {c['reaudit_reason']}"]) + " |")
    L += ["", "## Narrative world 영향", "",
          "| world | 최저 등급 이전 → 이후 | bridge 근거 등급 분포(이후) | bridge 구성 | 비고 |", "|---|---|---|---|---|"]
    old = {w["world_id"]: w for w in worlds_old}
    for w in worlds_new:
        o = old.get(w["world_id"], {})
        same = o.get("latent_bridges") == "|".join(w["latent_bridges"])
        note = "설명 수정: 'HIGH 후보만' → '추가 가정이 가장 적은 world'" if w["world_id"] == "W5" else ""
        L.append(f"| {w['world_id']} | {o.get('min_grade', '?')} → {w['min_grade']} | {w.get('evidence_profile', '')} | "
                 f"{'그대로' if same else '변경'} | {note} |")
    L += ["", "## 추가한 regression 규칙 (Audit 3)", "",
          "- `bridge_support_inflation`: bridge 직접 근거가 없는데(NO) source support가 HIGH인 경우. bridge_evidence 없이 MEDIUM 이상인 경우. "
          "confirmed 비-endpoint 근거 없이 HIGH인 경우. final HIGH인데 evidence·plausibility가 모두 HIGH가 아닌 경우",
          "- `temporal_inflation`: 근거 유형이 시간 인접·endpoint 내용뿐인데 MEDIUM 이상인 경우",
          "- `institutional_inflation`: 근거 유형이 제도·환경 가능성뿐인데 MEDIUM 이상인 경우",
          "- `endpoint_leakage`: endpoint node의 구성 fact를 bridge 근거로 인용한 경우",
          "- `latent_classification`: bridge가 사료에 직접 있는(YES) LATENT 후보 — 분류 점검 대상",
          "", "regression 케이스로 재감사 이전 값(예: G08a source HIGH)을 다시 넣으면 위 규칙이 ERROR를 내는지 build 때마다 확인한다."]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def write_story_matrix(path, worlds, cands, gaps, nodes, identity_rows, edges):
    cand = {c["candidate_id"]: c for c in cands}
    by = {n["node_id"]: n for n in nodes}
    comp = [w for w in worlds if w["role_type"] == "COMPETING_EXPLANATION"]
    from stage5_worlds import COMMON_OUTCOME_NODES
    outcome_ids = {x for ids in COMMON_OUTCOME_NODES.values() for x in ids}
    L = ["# Narrative World Story Matrix — 무엇이 사실이고 무엇이 가설인가", "",
         "- **OBSERVED** = 사료(01 confirmed facts)에서 확인된 내용. 모든 world에 공통이다. 진술·보고·판단은 그 인식 수준(진술/보고/판단)을 그대로 유지한다.",
         "- **LATENT** = 사료가 비워 둔 중간 과정을 설명하려는 가설. world마다 다르고, 그 world 안에서만 유지한다. 여러 world의 가설을 합쳐 사실로 쓰지 않는다.",
         "- W1–W5 = 경쟁하는 사건 설명(함께 보존). W6 = 검토했지만 배제된 설명(REJECTED).", "",
         "# 1. 모든 world에 공통인 OBSERVED 사실", "",
         "결말(재검토·판단·처분)은 8장에 따로 모았다. 여기에는 그 앞 단계의 관측 사실을 둔다. '진술'은 진술된 내용이지 객관 사실이 아니다.", "",
         "| node | 시점 | 인식 수준 | 내용 | 근거 fact |", "|---|---|---|---|---|"]
    for n in nodes:
        if n["layer"] == "ENVIRONMENT" or n["node_id"] in outcome_ids:
            continue
        L.append(f"| {n['node_id']} | {_cell(n['occurrence_text'])} | {n['layer']} | {_cell(n['summary'])} | {n['member_fact_ids'].replace('|', ', ')} |")
    L += ["", "환경 context(사건이 아님): " + "; ".join(f"{n['node_id']} {n['title']}" for n in nodes if n["layer"] == "ENVIRONMENT"), ""]
    titles = {"W1": "2", "W2": "3", "W3": "4", "W4": "5"}
    for w in comp:
        if w["world_id"] == "W5":
            continue
        josa = {"W1": "이"}.get(w["world_id"], "가")
        L += [f"# {titles[w['world_id']]}. {w['world_id']}{josa} 추가하는 LATENT", "",
              f"**역할** — {w['work_role']}", "", f"**보여주는 질문** — {w['story_question']}", "",
              f"이 world만 쓰는 가설: {', '.join(w['unique_bridges']) or '없음'} · 다른 world와 다른 점: {w['difference']}", "",
              "| 후보 | gap | LATENT 가설 (bridge claim) | bridge 근거 | final | 다른 경쟁 world와 공유 |", "|---|---|---|---|---|---|"]
        for b in w["latent_bridges"]:
            c = cand[b]
            share = [o["world_id"] for o in comp if o is not w and b in o["latent_bridges"]]
            L.append(f"| {b} | {c['gap_id']} | [LATENT] {_cell(c['latent_bridge_claim'])} | {c['source_support']} | {c['overall']} | "
                     f"{', '.join(share) or '이 world만'} |")
        L += ["", f"비워 둔 gap: {', '.join(w['unresolved_gaps']) or '없음'}", ""]
    w5 = next(w for w in comp if w["world_id"] == "W5")
    L += ["# 6. W5가 비워 두는 부분", "", f"**역할** — {w5['work_role']}", "", f"**보여주는 질문** — {w5['story_question']}", "",
          "W5가 쓰는 최소 bridge(모두 다른 world와 공유):", "",
          "| 후보 | gap | LATENT 가설 | bridge 근거 | final |", "|---|---|---|---|---|"]
    for b in w5["latent_bridges"]:
        c = cand[b]
        L.append(f"| {b} | {c['gap_id']} | [LATENT] {_cell(c['latent_bridge_claim'])} | {c['source_support']} | {c['overall']} |")
    L += ["", "W5가 채우지 않고 빈칸으로 두는 gap:", "", "| gap | 무엇이 비어 있나 | 다른 world는 어떻게 채우나 |", "|---|---|---|"]
    for g in gaps:
        if g["gap_id"] in w5["unresolved_gaps"]:
            fills = [f"{o['world_id']}:{b}" for o in comp for b in o["latent_bridges"] if cand[b]["gap_id"] == g["gap_id"]]
            L.append(f"| {g['gap_id']} | {_cell(g['title'])} — {_cell(g['why_gap'])} | {', '.join(fills) or '어느 world도 채우지 않음'} |")
    L += ["", "# 7. World 간 차이 비교표", "",
          "칸의 값은 그 world가 해당 gap에 놓은 LATENT 후보다(괄호는 bridge 근거 등급). '·'는 비워 둠. W6은 배제된 설명이라 마지막 열에 따로 둔다.", "",
          "| gap | " + " | ".join(w["world_id"] for w in comp) + " | W6 (REJECTED) |", "|---|" + "---|" * (len(comp) + 1)]
    rej = [w for w in worlds if w["role_type"] == "REJECTED"]
    for g in gaps:
        row = []
        for w in comp + rej:
            pick = [b for b in w["latent_bridges"] if cand[b]["gap_id"] == g["gap_id"]]
            row.append(f"{pick[0]}({cand[pick[0]]['source_support']})" if pick else "·")
        L.append(f"| {g['gap_id']} {_cell(g['title'])} | " + " | ".join(row) + " |")
    L += ["", "| World | 추가 가정 수 | evidence 분포 | 최저 등급 | 작품에서 보여주는 질문 |", "|---|---|---|---|---|"]
    for w in comp + rej:
        L.append(f"| {w['world_id']} ({w['role_type']}) | {w['n_assumptions']} | {w.get('evidence_profile', '')} | {w['min_grade']} | {_cell(w['story_question'])} |")
    L += ["", "# 8. 최종 판단·처분 중 모든 world에 공통인 것", "",
          "아래는 world별 결과가 아니다. 모든 world에 공통된 관측 사실이고, world들은 여기에 이르기 전의 미확인 사건 경로만 다르게 설명한다. "
          "(예: 구순의 신지도 정배는 모든 world에 공통된 관측 사실이다.)", "",
          "| 단계 | node | 시점 | 기록 내용 | 근거 fact |", "|---|---|---|---|---|"]
    for phase, x, t, summ, facts in _outcome_rows(nodes):
        L.append(f"| {phase} | {x} | {_cell(t)} | {_cell(summ)} | {facts} |")
    L += ["", "참고: 처분문의 '한가'는 한재욱이다(ID03, 사용자 확정). 이형원은 6/13 파직 뒤 6/16 유임되었고, 그 이유는 열린 gap(G10)으로 남는다.", "",
          "# 9. 끝까지 UNRESOLVED로 남는 것", "",
          "| 항목 | 상태 | 내용 | 모델에서의 보존 형태 |", "|---|---|---|---|"]
    for r in identity_rows:
        if r["status"] == "UNRESOLVED":
            L.append(f"| {r['identity_id']} | UNRESOLVED | {_cell(r['surface_a'])} ↔ {_cell(r['surface_b'])} | "
                     f"{_cell(r['model_relevance'])} · {_cell(r.get('review_decision', ''))} |")
    for e in edges:
        if e.get("uncertainty_status") in ("PARTIAL_CONFLICT", "UNRESOLVED_SCOPE"):
            L.append(f"| {e['edge_id']} | {e['uncertainty_status']} | {_cell(e['rationale'])} | {_cell(e.get('review_decision', ''))} |")
    for g in gaps:
        if g.get("gap_status") == "OPEN_UNRESOLVED":
            L.append(f"| {g['gap_id']} | OPEN_UNRESOLVED | {_cell(g['title'])} | {_cell(g.get('review_decision', ''))} |")
    L += ["", "이 항목들은 어느 world에서도 확정하지 않는다. 사료가 결정하지 못한 불확실성이며 오류가 아니다."]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
