"""Mechanism Super-DAG 산출물(CSV·Markdown·Mermaid)."""
import csv
from collections import Counter

from report import _cell, _counts_table, _findings_list, _verdict
from stage6_mechanisms import CAND_MAP, MAPPING_NOTES, MECHANISMS, ORDER, STRUCT_VARS, UNRESOLVED_ITEMS, usable

HEADER = ("> 이 문서는 질적 메커니즘 분석이다. 메커니즘은 역사적 사실이 아니라 분석 변수다. "
          "World는 메커니즘의 configuration, Observed fact는 고정, Context feature는 제약조건, Latent bridge는 가설, "
          "Outcome(재검토·판단·처분)은 confirmed backbone이다. 확률·SEM 계수·practice prior는 쓰지 않았다.")


def _w(path, rows, cols, headers=None):
    """headers가 있으면 열 이름을 요청 명세의 표 머리글로 바꿔 쓴다(값은 같은 key에서 읽음)."""
    headers = headers or {}
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([headers.get(c, c) for c in cols])
        for r in rows:
            w.writerow(["" if r.get(c) is None else r.get(c) for c in cols])


DEF_HEADERS = {"easy": "아주 쉬운 설명", "candidates": "관련 candidate", "observed_nodes": "관련 observed node",
               "institutional_features": "필요한 institutional feature", "environment_features": "관련 environment feature",
               "evidence_status": "evidence status", "note": "비고"}
INTERACTION_HEADERS = {"a": "mechanism A", "b": "mechanism B", "reason": "이유", "conflicting": "충돌하는 candidate/edge",
                       "explains_together": "같이 있을 때 설명되는 것"}


def definitions(sd, cands, nodes):
    cand = {c["candidate_id"]: c for c in cands}
    by = {n["node_id"]: n for n in nodes}
    rows = []
    for m in ORDER:
        d = MECHANISMS[m]
        cs = [cid for cid, v in CAND_MAP.items() if v[0] == m]
        sec = [cid for cid, v in CAND_MAP.items() if v[1] == m]
        obs = set(d.get("observed_anchor", []))
        for cid in cs:
            lids = {ln["id"] for ln in cand[cid]["latent_nodes"]}
            obs |= {x for le in cand[cid]["latent_edges"] for x in (le["src"], le["dst"]) if x not in lids and x in by}
        ev = Counter(cand[c]["source_support"] for c in cs if usable(cand[c]))
        excl = [c for c in cs if not usable(cand[c])]
        evs = " / ".join(f"{k} {ev[k]}" for k in ("HIGH", "MEDIUM", "LOW", "NONE") if ev[k])
        if m == "M5":
            evs = "관측 backbone 고정(OBSERVED) · 내부 세부 후보: " + (evs or "-")
        rows.append(dict(mechanism_id=m, mechanism_name=d["name"], easy=d["easy"],
                         candidates="|".join(cs) + (f" (보조: {'|'.join(sec)})" if sec else ""),
                         n_candidates=len(cs), observed_nodes="|".join(sorted(obs)),
                         institutional_features=d["features"], environment_features=d["envs"] or "-",
                         evidence_status=evs + (f" · 분석 제외 {'|'.join(excl)}" if excl else ""),
                         branch=d["branch"], note=d["note"]))
    return rows


def write_all(out, sd, cands, nodes, worlds, inst_rows):
    cand = {c["candidate_id"]: c for c in cands}
    _w(out / "mechanism_super_dag_nodes.csv", sd["nodes"],
       ["node_id", "sd_status", "node_type", "label", "frozen_status", "branch", "mechanism", "worlds", "detail"])
    _w(out / "mechanism_super_dag_edges.csv", sd["edges"], ["edge_id", "src", "dst", "edge_type", "sd_status", "origin", "note"])
    defs = definitions(sd, cands, nodes)
    _w(out / "mechanism_definitions.csv", defs,
       ["mechanism_id", "mechanism_name", "easy", "candidates", "observed_nodes", "institutional_features",
        "environment_features", "evidence_status", "note", "n_candidates", "branch"], DEF_HEADERS)
    crow = []
    for w in worlds:
        r = dict(world_id=w["world_id"], role_type=w["role_type"], latent_bridges="|".join(w["latent_bridges"]))
        for m in ORDER:
            r[m] = sd["configs"][w["world_id"]][m]
            r[m + "_basis"] = sd["whys"][w["world_id"]][m]
        crow.append(r)
    _w(out / "world_mechanism_configurations.csv", crow,
       ["world_id", "role_type"] + ORDER + [m + "_basis" for m in ORDER] + ["latent_bridges"])
    _w(out / "mechanism_interaction_matrix.csv", sd["interactions"],
       ["a", "b", "coexistence", "reason", "conflicting", "explains_together", "relation", "cooccur_worlds",
        "mechanism_a", "mechanism_b"], INTERACTION_HEADERS)
    write_rules(out / "qualitative_structural_rules.md", sd, cands)
    write_interventions(out / "mechanism_interventions.md", sd)
    # 같은 판단을 기계가 읽을 수 있게 CSV로도 낸다(값은 md와 같은 sd·STRUCT_VARS에서 읽음. 판단 변경 없음)
    _w(out / "mechanism_interventions.csv", sd["interventions"],
       ["mechanism", "variable", "target", "result", "removed", "remaining", "affected_worlds", "note"])
    _w(out / "qualitative_structural_rules.csv", structural_rule_rows(cands),
       ["var", "gap", "target", "op", "inputs", "rule", "desc", "constraint", "input_candidates"])
    write_overview(out / "mechanism_super_dag.md", sd, defs, worlds, cands, inst_rows)
    (out / "mechanism_super_dag.mmd").write_text(mermaid_full(sd) + "\n", encoding="utf-8")
    return defs, crow


def structural_rule_rows(cands):
    """STRUCT_VARS를 그대로 행으로 옮긴다. input_candidates는 write_rules의 '입력 후보' 열과 같은 계산."""
    rows = []
    for v in STRUCT_VARS:
        gaps = set(v["gap"].split("|")) if v["gap"] else set()
        ins = [c["candidate_id"] for c in cands if usable(c) and c["gap_id"] in gaps
               and (CAND_MAP[c["candidate_id"]][0] in v["inputs"] or CAND_MAP[c["candidate_id"]][1] in v["inputs"])]
        rows.append(dict(var=v["var"], gap=v["gap"], target=v["target"], op=v["op"], inputs="|".join(v["inputs"]),
                         rule=v["rule"], desc=v["desc"], constraint=v["constraint"], input_candidates="|".join(ins)))
    return rows


def write_rules(path, sd, cands):
    cand = {c["candidate_id"]: c for c in cands}
    L = ["# Qualitative Structural Rules (질적 구조방정식)", "", HEADER, "",
         "아래 식은 '실제로 그렇게 됐다'는 역사적 단정이 아니다. '이런 메커니즘 조합이면 현재 관측 경로를 설명할 수 있다'는 구조적 표현이다.",
         "OR = 어느 하나만 있어도 그 전이를 설명할 수 있음(대체 관계). AND = 모두 필요함. XOR = 서로 배타적인 설명. "
         "ANCHORED = 관측 backbone에 고정되어 world마다 달라지지 않음.", "",
         "| 구조 변수 | 설명하는 관측 전이 | 규칙 | 연산 | 입력 후보(분석 사용분, bridge 근거) | 제도·환경 제약 |", "|---|---|---|---|---|---|"]
    for v in STRUCT_VARS:
        gaps = set(v["gap"].split("|")) if v["gap"] else set()
        ins = [c for c in cands if usable(c) and c["gap_id"] in gaps
               and (CAND_MAP[c["candidate_id"]][0] in v["inputs"] or CAND_MAP[c["candidate_id"]][1] in v["inputs"])]
        L.append(f"| `{v['var']}` | {_cell(v['desc'])} → {v['target'].replace('|', ', ')} | {_cell(v['rule'])} | {v['op']} | "
                 f"{', '.join(c['candidate_id'] + '(' + CAND_MAP[c['candidate_id']][0] + ' ' + c['source_support'] + ')' for c in ins) or '-'} | "
                 f"{_cell(v['constraint'])} |")
    L += ["", "## 규칙 사이의 연결", "", "```",
          "V_COMPLAINT_TO_BARRACKS → V_COMMAND_SOURCE → V_INFO_TO_COMMANDER → V_ARREST_PATH ─┐",
          "                                                                                ├→ V_RESPONSIBILITY → V_SANCTION",
          "V_INITIAL_JUDGMENT_BASIS → (EP15, OBSERVED) → V_REVIEW_CORRECTION (M5, ANCHORED) ─┘",
          "",
          "V_CUSTODY_COURSE (MB, 사망 branch A) → EP13 사망 보고   ※ V_RESPONSIBILITY와 연결하지 않음",
          "```", "",
          "## 해석 원칙", "",
          "- 체포 지시(EP09)·체포(EP11)·5월 판단(EP15)·재검토·최종 판단·처분은 OBSERVED다. 규칙은 그 앞의 빈 전이만 설명한다.",
          "- `V_INFO_TO_COMMANDER`는 OR다. M1·M2·M3·M4 가운데 어느 것으로도 설명할 수 있다. 어느 쪽이 실제로 작동했는지는 사료가 결정하지 않는다(Audit 4 UNRESOLVED).",
          "- `V_COMMAND_SOURCE`는 XOR다. G02a(병사 지시, M1)와 G02b(상위 명령 없는 비장 자체 판단, M4)는 함께 참일 수 없다.",
          "- `INSTITUTIONALLY_COMPATIBLE`은 F007·F008(병사 → 장교 명령)의 제도 적합성이다. 이것이 참이라고 체포가 일어난 것은 아니다. 체포는 관측 사실이다.",
          "- M3(사적 통로)는 F007상 '명령'이 될 수 없다. 정보·영향 입력으로만 V_INFO_TO_COMMANDER에 들어간다(G04e INCOMPATIBLE).",
          "- 환경 E001–E004는 MB에 CONTEXT_COMPATIBLE로만 연결된다. 개인 감염 사건을 만들지 않는다.",
          "- 책임(V_RESPONSIBILITY)은 절차 branch에만 의존한다. 사인(V_CUSTODY_COURSE)과 서로 연결하지 않는다. 구순 → 김명신 사망의 직접 edge는 없다."]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def write_interventions(path, sd):
    L = ["# Qualitative Interventions — do(M = OFF)", "", HEADER, "",
         "정량 효과를 계산하지 않는다. 한 메커니즘을 끄면 같은 관측 전이를 설명하는 다른 경로가 남는지만 본다.", "",
         "- PATH_REMAINS: 다른 메커니즘 후보가 같은 전이를 채울 수 있고, bridge 근거가 같거나 더 강함",
         "- PATH_WEAKENS: 다른 경로가 남지만 남은 bridge 근거가 더 약함",
         "- PATH_BREAKS: 그 전이를 채우는 후보가 이 메커니즘뿐임(관측 사건은 그대로이고, 그 앞의 설명만 비게 됨)",
         "- UNKNOWN: 판단 근거 부족", "",
         "| intervention | 구조 변수 | 관측 대상 | 결과 | 사라지는 후보 | 남는 후보 | 영향받는 world | 설명 |", "|---|---|---|---|---|---|---|---|"]
    for i in sd["interventions"]:
        L.append(f"| do({i['mechanism']}=OFF) | `{i['variable']}` | {i['target'].replace('|', ', ')} | **{i['result']}** | "
                 f"{i['removed'].replace('|', ', ') or '-'} | {i['remaining'].replace('|', ', ') or '-'} | {i['affected_worlds']} | {_cell(i['note'])} |")
    L += ["", "## 메커니즘별 요약", "", "| intervention | 결과 요약 |", "|---|---|"]
    for m in ORDER:
        rs = [i for i in sd["interventions"] if i["mechanism"] == m]
        L.append(f"| do({m}=OFF) | " + "; ".join(f"{i['variable']}: {i['result']}" for i in rs) + " |")
    L += ["", "## world 안에서 보면", "",
          "각 world는 gap마다 bridge를 하나만 쓴다. 그래서 그 world가 기대는 메커니즘을 끄면 world 안의 해당 설명은 비게 된다(영향받는 world 열). "
          "Super-DAG 수준에서는 다른 메커니즘이 같은 전이를 대신 설명할 수 있는지를 본다. 두 수준을 섞지 않는다."]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def mermaid_context():
    L = ["flowchart LR"]
    for m in ORDER:
        L.append(f'  {m}["{m} {MECHANISMS[m]["short"]}"]')
    feats = sorted({f for m in ORDER for f in MECHANISMS[m]["features"].split("|")})
    for f in feats:
        L.append(f'  CTX_{f}(["{f}"])')
    for m in ORDER:
        for f in MECHANISMS[m]["features"].split("|"):
            L.append(f"  CTX_{f} -.->|CONSTRAINS| {m}")
    for e, n in [("E001", "ENV01"), ("E002", "ENV02"), ("E003", "ENV03"), ("E004", "ENV04")]:
        L.append(f'  {n}(["{e} 환경"]) -.->|CONTEXT_COMPATIBLE| MB')
    return "\n".join(L)


INVESTIGATION_PANEL = (["M1", "M2", "M3", "M4", "MB", "V_COMPLAINT_TO_BARRACKS", "V_COMMAND_SOURCE", "V_INFO_TO_COMMANDER",
                        "V_ARREST_PATH", "V_INVESTIGATION_SCOPE", "V_CUSTODY_COURSE", "CTX_F007", "CTX_F008"]
                       + ["EP03", "EP04", "EP05", "EP07", "EP08", "EP09", "EP10", "EP11", "EP13"])
REVIEW_PANEL = (["M2", "M5", "M6", "V_ARREST_PATH", "V_INITIAL_JUDGMENT_BASIS", "V_REVIEW_CORRECTION", "V_RESPONSIBILITY",
                 "V_SANCTION", "ENV01", "ENV02", "ENV03", "ENV04"] + [f"EP{i}" for i in range(13, 38)])
_OP = {"OR": "OR", "AND": "AND", "XOR": "XOR", "ANCHORED": "ANCHORED"}


def _mm_id(n):
    return n.replace("-", "_")


def _mermaid_panel(sd, keep, direction="TD"):
    """keep 안의 node 사이 edge만 그린다. 관측 edge는 frozen 그대로(type 표기), 메커니즘 → 구조 변수는
    그 메커니즘의 후보가 구조 변수에 기여할 때만(후보 id 표기). 손으로 쓴 edge는 없다."""
    keep = list(keep)
    ks = set(keep)
    by = {n["node_id"]: n for n in sd["nodes"]}
    ops = {v["var"]: v["op"] for v in STRUCT_VARS}
    L = [f"flowchart {direction}"]
    for n in keep:
        d = by.get(n)
        if d is None:
            continue
        st = d["sd_status"]
        if d["node_type"] == "MECHANISM":
            L.append(f'  {_mm_id(n)}["{n} {MECHANISMS[n]["short"]}"]')
        elif d["node_type"] == "STRUCTURAL_VARIABLE":
            L.append(f'  {_mm_id(n)}{{"{n} ({_OP.get(ops.get(n), ops.get(n))})"}}')
        elif st == "CONTEXT":
            L.append(f'  {_mm_id(n)}(["{n} {d["label"][:24].rstrip()}"])')
        else:
            L.append(f'  {_mm_id(n)}["{n} {d["label"][:26].rstrip()} ({st})"]')
    inst = {}
    for e in sd["edges"]:
        if e["edge_type"] == "INSTANTIATED_BY":
            inst[e["dst"]] = e["src"]
    via = {}
    for e in sd["edges"]:
        if e["edge_type"] == "CONTRIBUTES_TO" and e["src"] in inst:
            m = inst[e["src"]]
            if m in ks and e["dst"] in ks:
                via.setdefault((m, e["dst"]), []).append(e["src"])
    for (m, v), cs in via.items():
        L.append(f"  {_mm_id(m)} -->|{', '.join(cs)}| {_mm_id(v)}")
    for e in sd["edges"]:
        s, d, t = e["src"], e["dst"], e["edge_type"]
        if s not in ks or d not in ks or t in ("INSTANTIATED_BY", "INSTANTIATED_BY_SECONDARY", "CONTRIBUTES_TO"):
            continue
        arrow = "-.->" if e["sd_status"] in ("CONTEXT",) or t in ("CONSTRAINS", "CONTEXT_SUPPORTS", "CONTEXT_COMPATIBLE",
                                                                    "EXPLAINS_OBSERVED", "ANCHORED_TO") else "-->"
        L.append(f"  {_mm_id(s)} {arrow}|{t}| {_mm_id(d)}")
    return "\n".join(L)


def mermaid_investigation(sd):
    return _mermaid_panel(sd, INVESTIGATION_PANEL)


def mermaid_review(sd):
    return _mermaid_panel(sd, REVIEW_PANEL)


def mermaid_full(sd):
    parts = ["%% Mechanism Super-DAG (세 패널). 점선 = CONTEXT 제약·관측 고정, 실선 = 메커니즘·규칙·관측(frozen) 연결",
             "%% 모든 edge는 mechanism_super_dag_edges.csv에서 그렸다(관측 edge는 frozen 그대로).",
             "%% 1) context → mechanism", mermaid_context(), "",
             "%% 2) mechanism → investigation", mermaid_investigation(sd), "",
             "%% 3) review → judgment → sanction", mermaid_review(sd)]
    return "\n".join(parts)


def write_overview(path, sd, defs, worlds, cands, inst_rows):
    cand = {c["candidate_id"]: c for c in cands}
    st = Counter(n["sd_status"] for n in sd["nodes"])
    se = Counter(e["sd_status"] for e in sd["edges"])
    L = ["# Mechanism Super-DAG (Qualitative SCM)", "", HEADER, "",
         "```",
         "[Institutional Context F001–F020]  ── CONSTRAINS ──▶  [Mechanism Layer M1–M6, MB]",
         "                                                         │ INSTANTIATED_BY",
         "                                                         ▼",
         "                                              [LATENT 후보 38개 (기존, 등급 그대로)]",
         "                                                         │ CONTRIBUTES_TO",
         "                                                         ▼",
         "                                              [질적 구조 변수 V_*]",
         "                                                         │ EXPLAINS_TRANSITION_TO",
         "                                                         ▼",
         "[Observed Event Layer: 정보 전달 → 체포 → 구금 → 5월 판단 → 독립 재검토 → 6월 판단 수정 → 책임 귀속 → 처분]  (frozen, 그대로)",
         "[Environment Context E001–E004]  ── CONTEXT_COMPATIBLE ──▶ MB  /  (frozen) CONTEXT_SUPPORTS ──▶ 사인 판단 node",
         "```", "",
         f"- node: " + ", ".join(f"{k} {v}" for k, v in sorted(st.items())),
         f"- edge: " + ", ".join(f"{k} {v}" for k, v in sorted(se.items())),
         f"- frozen observed graph(node 41, edge 68)는 그대로 복사했다. 동결 해시 `{sd['frozen_hash'][:16]}…`. 환경 node는 Super-DAG에서 CONTEXT로 표시한다(frozen 표기는 OBSERVED 그대로).",
         "",
         "## 1. 메커니즘 정의", "",
         "| mechanism_id | mechanism_name | 아주 쉬운 설명 | 관련 candidate | 관련 observed node | 필요한 institutional feature | 관련 environment feature | evidence status | 비고 |",
         "|---|---|---|---|---|---|---|---|---|"]
    for d in defs:
        L.append(f"| {d['mechanism_id']} | {d['mechanism_name']} | {_cell(d['easy'])} | {_cell(d['candidates'])} | {d['observed_nodes'].replace('|', ', ')} | "
                 f"{d['institutional_features'].replace('|', ', ')} | {d['environment_features'].replace('|', ', ')} | {_cell(d['evidence_status'])} | {_cell(d['note'])} |")
    L += ["", "M6(초기 판단 근거)와 MB(구금·질병 경과)는 요청된 M1–M5 밖에서 추가했다. G07 계열과 G06·G12 계열이 반복되는 패턴이고, "
          "MB는 사망 branch A를 책임 branch와 분리하려면 별도 변수가 필요하기 때문이다. 새 후보나 새 사건은 만들지 않았다.", "",
          "후보 매핑 메모:", ""] + [f"- {k}: {v}" for k, v in MAPPING_NOTES.items()]
    feat_name = {r["feature_id"]: r["feature_name"] for r in inst_rows}
    L += ["", "## 2. 제도 피쳐가 제약하는 메커니즘", "", "| 피쳐 | 이름 | 제약하는 메커니즘 |", "|---|---|---|"]
    for f in sorted({f for m in ORDER for f in MECHANISMS[m]["features"].split("|")}):
        ms = [m for m in ORDER if f in MECHANISMS[m]["features"].split("|")]
        L.append(f"| {f} | {feat_name.get(f, '')} | {', '.join(ms)} |")
    unused = sorted(set(feat_name) - {f for m in ORDER for f in MECHANISMS[m]["features"].split("|")})
    L += ["", f"메커니즘에 연결하지 않은 제도 피쳐: {', '.join(unused) or '없음'}(이 사건 메커니즘의 가능성을 직접 제약하지 않음).", "",
          "## 3. World = 메커니즘 configuration", "",
          "값은 world의 실제 bridge 구성에서 규칙으로 계산했다(손으로 넣지 않음). ON: 핵심 gap을 그 메커니즘의 core 후보로 채움. PARTIAL: 보조 후보만 쓰거나 "
          "같은 world에 부정 후보가 함께 있음. OFF: 부정 후보만 있음. UNSPECIFIED: 관련 후보 없음(OFF가 아니다). M5는 관측 backbone에 고정되어 모든 world에서 ON이다.", "",
          "| World | 구분 | " + " | ".join(f"{m} {MECHANISMS[m]['short']}" for m in ORDER) + " | 비고 |", "|---|---|" + "---|" * (len(ORDER) + 1)]
    for w in worlds:
        cfg = sd["configs"][w["world_id"]]
        note = "검토했지만 배제된 설명. 공존·개입 분석에서 제외한 대조군" if w["role_type"] == "REJECTED" else w["story_question"]
        L.append(f"| {w['world_id']} | {w['role_type']} | " + " | ".join(cfg[m] for m in ORDER) + f" | {_cell(note)} |")
    L += ["", "판정 근거(world × 메커니즘):", ""]
    for w in worlds:
        L.append(f"- **{w['world_id']}**: " + " · ".join(f"{m} {sd['configs'][w['world_id']][m]} ({sd['whys'][w['world_id']][m]})" for m in ORDER))
    L += ["", "## 4. 공존 분석 (pairwise interaction matrix)", "",
          "기준: 기존 후보·상충 쌍·부정 관계·관측 graph·제도 제약만 썼다('그럴 법함'은 근거로 쓰지 않음). W6은 제외했다.", "",
          "| mechanism A | mechanism B | coexistence | 관계 | 이유 | 충돌하는 candidate/edge | 같이 있을 때 설명되는 것 | 함께 쓰는 world |",
          "|---|---|---|---|---|---|---|---|"]
    for x in sd["interactions"]:
        L.append(f"| {x['a']} | {x['b']} | **{x['coexistence']}** | {x['relation'].replace('|', ', ')} | {_cell(x['reason'])} | "
                 f"{_cell(x['conflicting']) or '-'} | {_cell(x['explains_together']) or '-'} | {x['cooccur_worlds'] or '-'} |")
    L += ["", "관계 표기: SUBSTITUTE = 같은 관측 전이를 다른 방식으로 설명(대체). EXCLUSIVE_ALTERNATIVE = 같은 전이를 서로 배타적으로 설명. "
          "COMPLEMENT = 한 world 안에서 서로 다른 전이를 함께 설명(보완). INDEPENDENT = 다른 branch나 관측 고정 메커니즘이라 서로 설명하지 않음.", "",
          "### 3-way 조합 (설명 가치가 있는 것만)", "", "| 조합 | coexistence | 설명 | 함께 쓰는 world | 충돌 |", "|---|---|---|---|---|"]
    for t in sd["triples"]:
        L.append(f"| {t['combo']} | **{t['coexistence']}** | {_cell(t['why'])} | {t['cooccur_worlds']} | {_cell(t['conflicts'])} |")
    L += ["", "## 5. 질적 구조 규칙과 개입", "", "`qualitative_structural_rules.md`, `mechanism_interventions.md` 참고.", "",
          "## 6. 사망 branch 분리", "",
          "- branch A(생물학적): MB → V_CUSTODY_COURSE → EP13. 환경 E001–E004 → MB(CONTEXT_COMPATIBLE). frozen CONTEXT_SUPPORTS → EP26·EP27(사인 판단).",
          "- branch B(절차·책임): M1–M4 → V_INFO_TO_COMMANDER → V_ARREST_PATH → V_RESPONSIBILITY → EP29·EP30.",
          "- 두 branch를 잇는 Super-DAG edge는 없다(Audit 4 `responsibility_to_biological` 검사). 구순 → 김명신 사망 직접 edge도 없다.", "",
          "## 7. UNRESOLVED 노드", "", "| node | 내용 | 영향 |", "|---|---|---|"]
    for u in UNRESOLVED_ITEMS:
        L.append(f"| {u['uid']} | {_cell(u['label'])} | 후보 {', '.join(u['affects']) or '-'} · {u['affects_observed']} |")
    L += ["", "## 8. Mermaid", "", "### context → mechanism", "", "```mermaid", mermaid_context(), "```", "",
          "### mechanism → investigation", "", "```mermaid", mermaid_investigation(sd), "```", "",
          "### review → judgment → sanction", "", "```mermaid", mermaid_review(sd), "```"]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def write_audit4(path, findings, sd, regression_results=()):
    from manual_review import AUDIT4_REVISIONS
    from report import _revlog
    L = ["# AUDIT 4 — Mechanism Super-DAG", "",
         "핵심 질문: **메커니즘 Super-DAG가 관측 사실을 바꾸거나, context로 사건을 만들거나, world·branch를 섞었는가?**", "",
         f"- 판정: {_verdict(findings)}", "",
         "## 자동 검사 요약", "", _counts_table(findings), "",
         "ERROR 검사: frozen_graph_changed, context_to_fact(새 관측 node 포함), observed_to_latent, latent_to_observed, world_latent_promoted, institution_to_event, "
         "environment_to_personal_fact, context_to_fact, causal_inflation, responsibility_to_biological, incompatible_coexistence, "
         "w6_reactivation, off_mechanism_alive, unspecified_as_off, config_value, world_merge, outcome_world_dependency, dangling_edge.", "",
         "UNRESOLVED(사료가 결정하지 않음, 허용): coexistence_undetermined, interaction_direction, multiple_explanations, unresolved_item.", "",
         "### ERROR", _findings_list(findings, "ERROR"), "", "### WARN", _findings_list(findings, "WARN"), "",
         "### UNRESOLVED", _findings_list(findings, "UNRESOLVED"), "", "### INFO", _findings_list(findings, "INFO"), "",
         "UNRESOLVED는 오류가 아니다. 사료가 결정하지 않는 것(어느 메커니즘이 실제로 작동했는지, 함께 작동했는지, 방향)과 "
         "사용자가 열어 두기로 한 항목(ID06·ID07·ID08·OE007·OE062·G10)이다. WARN으로 두지 않았다.", "",
         "## Regression (Audit 4)", "",
         "깨끗한 Super-DAG에서 ERROR 0을 확인한 뒤, 사본 하나만 바꿔 검사기에 넣었다. 기대한 check가 ERROR로 나와야 통과다.", "",
         "| rule | 넣은 결함 | 결과 | 나온 ERROR |", "|---|---|---|---|"]
    regs = [r for r in regression_results if r.get("audit") == "AUDIT4"]
    for r in regs:
        L.append(f"| `{r['rule']}` | {r['case']} | {'탐지' if r['caught'] else '**놓침**'} | {', '.join(r['detail'])} |")
    L += ["", "## 수정 이력", "", _revlog(AUDIT4_REVISIONS)]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def write_audit5(path, findings, ui, regression_results=()):
    from manual_review import AUDIT5_REVISIONS
    from report import _revlog
    m = ui["meta"]
    L = ["# AUDIT 5 — Interactive Visualization (Temporal DAG)", "",
         "핵심 질문: **탐색용 화면 데이터(docs/data)가 canonical 산출물을 바꾸거나, context·LATENT를 사건처럼 보이게 하거나, 시간 순서·world 결말을 깨뜨렸는가?**", "",
         f"- 판정: {_verdict(findings)}",
         f"- 화면 데이터: node {m['counts']['nodes']} · edge {m['counts']['edges']} (canonical `mechanism_super_dag_nodes.csv`·`mechanism_super_dag_edges.csv`와 같음)",
         f"- 동결 해시: `{m['frozen_hash']}`",
         "- 생성: `scripts/gusun_clean/build_visualization.py` → `docs/data/*.json` + `docs/data/bundle.js`(같은 내용, file:// 용)", "",
         "## 자동 검사 요약", "", _counts_table(findings), "",
         "ERROR 검사: ui_node_not_canonical·ui_node_missing·ui_node_altered(1), ui_edge_not_canonical·ui_edge_missing·ui_edge_altered(2), "
         "status_changed(3), w6_not_rejected(4), outcome_dropped(5), unspecified_as_off(6), context_as_event(7), environment_to_individual(8), "
         "responsibility_to_biological(9), temporal_order(10), candidate_grade_changed(11), intervention_changed(12), "
         "그리고 count_mismatch·frozen_graph_changed·stale_ui_data·bundle_mismatch·interaction_changed.", "",
         "관점별 View·가독성 검사(13): view_not_subset(View node·edge가 canonical 부분집합이고 edge = View node 사이 canonical edge 전부, 새 node·edge 없음), "
         "view_status_changed(View metadata에 상태·판정·해석 필드 없음, 좌표 항목은 x·y·lane만), "
         "view_hidden_notice_missing(subset View의 숨긴 OBSERVED 목록 = 관측 node − View node, '시각적 필터·삭제 아님·분석상 ON/OFF 아님' 안내와 그 안내를 그리는 코드), "
         "label_clipped(node label이 canonical 글자를 모두 담고 말줄임 없음, 가장 긴 줄 ≤ 글자 영역, 높이 ≥ 줄 수 × 줄 높이), "
         "font_too_small(node·edge label과 CSS의 모든 font-size ≥ 11pt), line_height_too_small(CSS·node label line-height ≥ 1.6), "
         "initial_label_unreadable(모든 View의 첫 화면 최소 배율 × node 글자 ≥ 11pt, lane·시간 구간 글자 포함), "
         "responsibility_to_biological(View edge에도 branch A↔B 직접 edge 없음), "
         "layout_nondeterministic(같은 입력으로 두 번 계산한 좌표가 같고 화면 데이터와도 같음), view_node_overlap(Overview·View 좌표에서 node 상자 겹침 0), "
         "temporal_order·context_as_event(View 좌표에서도 날짜 순서·context lane 유지). W6 REJECTED는 4번 검사가 그대로 본다.", "",
         "실행 시 빈 그래프 방지 검사(14): stale_asset_version(index.html이 싣는 css·js 주소의 `?v=`가 지금 파일 내용 해시와 같음 — "
         "배포 직후 새 index.html이 브라우저 캐시의 옛 app.js와 섞이지 않게), dom_id_missing(app.js가 찾는 DOM id가 index.html 또는 app.js가 만드는 HTML에 모두 있음), "
         "runtime_failsafe_missing(초기화 예외 시 그래프 영역에 '시각화 초기화 오류'를 보여 주는 `AUDIT5:RUNTIME_GUARD`, 보이는 node 0이면 안내 후 Overview로 1회 복구하는 "
         "`AUDIT5:EMPTY_VIEW_GUARD`). 실제 브라우저 렌더(첫 화면·A–J 각 View에서 보이는 node가 화면 창과 겹치고 그래프 영역 픽셀이 비어 있지 않음, console·pageerror 0)는 "
         "`scripts/gusun_clean/test_visualization.py`가 검사한다.", "",
         "### ERROR", _findings_list(findings, "ERROR"), "", "### WARN", _findings_list(findings, "WARN"), "",
         "### UNRESOLVED", _findings_list(findings, "UNRESOLVED"), "", "### INFO", _findings_list(findings, "INFO"), "",
         "## 화면 규칙(검사 대상)", "",
         "- 배치: 물리 시뮬레이션 없는 preset 좌표. 날짜 있는 관측 node는 정렬 기준일(t_max, 없으면 t_min) 순서로 왼쪽 → 오른쪽, "
         "같은 날짜 안에서는 frozen edge 깊이 순서. 시간 구간: 2월 → 3월 → 5월 → 6월 → 최종 판단·처분(6/13 이후 정조 판단·명령).",
         "- 날짜 없는 node(메커니즘·구조 변수·후보·context·UNRESOLVED)는 별도 lane. x는 연결된 node 근처일 뿐 날짜가 아니다.",
         "- world 선택(ALL·W1–W5·W6)은 worlds.json의 always_visible·dim·hideable·highlight 목록대로만 동작한다. 관측 node는 모든 선택에서 always_visible이고 "
         "app.js의 backbone 보호 규칙(`AUDIT5:BACKBONE_GUARD`)이 어떤 필터·world 선택·개입에서도 숨기지 않는다(관점별 View B–I의 범위 숨김은 아래 규칙).",
         "- W6은 REJECTED 배너와 함께 표시되고 공존·개입 패널의 world 목록에 들어가지 않는다(canonical과 같음).",
         "- 상태 필터와 메커니즘 필터는 화면 보이기/숨기기일 뿐 분석상 ON/OFF가 아니다. 개입 do(M=OFF)는 저장된 결과만 보여 준다.",
         "- 관점별 View(views.json): A 전체 Overview(전체), B–I 관점별 View(subset: View 밖 node 숨김, 숨긴 OBSERVED 개수·ID 안내, "
         "'전체 주변 맥락 표시'로 Overview 좌표에 흐리게 다시 표시), J LATENT·World 비교(dim: 밖의 OBSERVED는 흐리게만). "
         "View는 node·edge 부분집합과 표시 좌표만 담는다. 필터·world·개입은 여전히 OBSERVED를 숨기지 못한다(BACKBONE_GUARD). "
         "subset View의 범위 숨김만 OBSERVED를 숨길 수 있고(`AUDIT5:VIEW_SCOPE`), 그때는 안내(`AUDIT5:VIEW_HIDDEN_NOTICE`)가 항상 보인다.",
         "- 가독성: node label 16px(12pt)·line-height 1.6, UI 글자 15px(11.25pt) 이상·line-height 1.6. 모든 View의 첫 화면 배율 ≥ 0.95(node 글자 ≥ 15.2px). "
         "그보다 작게 축소하면(전체 지도) node는 ID만 크게 표시한다. node 폭은 종류별 고정, 높이는 줄 수로 정하고, label은 자르지 않고 줄바꿈한다.", "",
         "## Regression (Audit 5)", "",
         "깨끗한 화면 데이터에서 ERROR 0을 확인한 뒤, 사본 하나만 바꿔 검사기에 넣었다. 기대한 check가 ERROR로 나와야 통과다.", "",
         "| rule | 넣은 결함 | 결과 | 나온 ERROR |", "|---|---|---|---|"]
    for r in [r for r in regression_results if r.get("audit") == "AUDIT5"]:
        L.append(f"| `{r['rule']}` | {r['case']} | {'탐지' if r['caught'] else '**놓침**'} | {', '.join(r['detail'])} |")
    L += ["", "## 생성 근거 파일 (sha256)", "", "| 파일 | sha256 |", "|---|---|"]
    for k, v in sorted(m["generated_from"].items()):
        L.append(f"| `{k}` | `{v[:16]}…` |")
    L += ["", "## 수정 이력", "", _revlog(AUDIT5_REVISIONS)]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
