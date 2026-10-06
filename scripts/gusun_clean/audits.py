"""Audit 1 / 2 / 3 — 원본 pack과 다시 비교하는 자동 검사.

각 검사는 findings(dict: check, severity, target, message)를 낸다.
severity: ERROR(통과 불가) | WARN(검토 필요, 수동 판정 기록) | INFO(보고만)
"""
import re
from collections import defaultdict

from stage1_episodes import EPISTEMIC_RANK, IDENTITY_REGISTER

PERSON_NAMES = ["구순", "김명신", "명업", "나복", "이진욱", "한재욱", "조계완", "변지돌", "정원돌", "자미덕",
                "재돌", "이집거", "김갑득", "김성손", "김흥득", "유제희", "김상제", "이광섭", "이문협", "이형원",
                "정조", "이조원", "홍대협", "윤노동", "한가", "박거사", "원돌", "김생원"]

# 원문에 없는데 summary에 나오면 강화(strengthening)로 보는 어휘
STRONG_TERMS = ["범인", "거짓 지목", "지목했", "누명", "모함", "날조", "살해", "고문", "때문에 죽", "사주했다",
                "결탁", "공모", "원인이 되", "확실하다고 판단", "감염되었", "옥중 감염", "죽게 했", "죽였"]

# 원문에 있으면 summary에도 반드시 남아야 하는 한정·완화 표현(weakening 방지)
HEDGES = ["극히 수상", "거짓으로 꾸며", "은밀히", "약간의", "십분 확실", "취지로", "방향", "달포 이상", "확실한 장물",
          "진정한 장물", "보통 좀도둑", "스스로 만들어냈다는 죄", "크게 다르지 않다", "평생 모르는", "한 차례", "이미",
          "표기된", "병들어", "전염병", "질병", "부처", "직접", "횡액", "원통하게", "사적인 감정", "성명을 적어",
          "전해 들은", "보류", "자세히"]

IDENTITY_RULES = [("병사", "이광섭", "ID01"), ("한 비장", "한재욱", "ID02"), ("한가", "한재욱", "ID03"),
                  ("김상제", "김명신", "ID05"), ("염탐 담당자", "유제희", "ID06"), ("원돌", "정원돌", "ID11")]

FAMILY = {
    "RECORDED_TESTIMONY": "TESTIMONY", "RECORDED_NESTED_TESTIMONY": "TESTIMONY",
    "DOCUMENTED_SOURCE_IDENTIFICATION": "IDENT",
    "DOCUMENTED_OFFICIAL_REPORT": "OFFICIAL", "DOCUMENTED_OFFICIAL_EVALUATION": "OFFICIAL",
    "DOCUMENTED_INSPECTOR_REPORT": "OFFICIAL", "DOCUMENTED_OFFICIAL_FINDING": "OFFICIAL",
    "DOCUMENTED_OFFICIAL_ACTION": "OFFICIAL",
    "DOCUMENTED_ROYAL_JUDGMENT": "ROYAL", "DOCUMENTED_ROYAL_ORDER": "ROYAL",
    "DOCUMENTED_ROYAL_JUDGMENT_AND_ORDER": "ROYAL",
    "DOCUMENTED_COURT_ACTION": "COURT",
    "DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT": "MIXED",
}
ALLOWED_FAMILY_MIX = [{"TESTIMONY", "IDENT"}]
TESTIMONY_LAYERS = {"TESTIMONY", "NESTED_TESTIMONY"}
JUDGMENT_LAYERS = {"ROYAL_JUDGMENT", "ROYAL_JUDGMENT_AND_ORDER", "OFFICIAL_EVALUATION", "OFFICIAL_FINDING",
                   "OFFICIAL_REPORT", "INSPECTOR_REPORT"}

ETC_RE = re.compile(r"(?<=\S) 등(?=[\s을의에이과은는]|$)")


def F(check, severity, target, message):
    return dict(check=check, severity=severity, target=target, message=message)


def member_text(cf_row, clause):
    return clause if clause else cf_row["confirmed_statement"]


def clause_family(cf_row, clause):
    fam = FAMILY[cf_row["confirmation_level"]]
    if fam == "MIXED" and clause:
        if clause.startswith("정조"):
            return "ROYAL"
        if clause.startswith("홍대협"):
            return "OFFICIAL"
    return fam


def parse_md(text):
    m = re.search(r"1793-(\d{2})-(\d{2})", str(text or ""))
    return int(m.group(1)) * 100 + int(m.group(2)) if m else None


def testifier(stmt):
    m = re.match(r"^(\S+?)[은는]\s", stmt)
    return m.group(1) if m else None


# ============================================================================
# AUDIT 1 — Episode fidelity
# ============================================================================

def audit1(episodes, cf, props, sources):
    out = []
    cf_by = {r["fact_id"]: r for r in cf}
    prop_by = {r["prop_id"]: r for r in props}
    src_ids = {r["source_record_id"] for r in sources}

    # 1. omission / back-trace
    covered = defaultdict(list)
    for ep in episodes:
        if not ep["members"]:
            out.append(F("unsupported_episode", "ERROR", ep["episode_id"], "구성 confirmed fact 없음"))
        for fid, clause in ep["members"]:
            if fid not in cf_by:
                out.append(F("unsupported_episode", "ERROR", ep["episode_id"], f"존재하지 않는 fact {fid}"))
                continue
            covered[fid].append(clause)
            if clause and clause not in cf_by[fid]["confirmed_statement"]:
                out.append(F("clause_fidelity", "ERROR", ep["episode_id"], f"{fid} 절이 원문 substring이 아님: {clause}"))
    for fid, row in cf_by.items():
        if fid not in covered:
            out.append(F("omission", "ERROR", fid, "어느 episode에도 속하지 않음"))
            continue
        clauses = covered[fid]
        if None not in clauses:  # 절 분할 → 합쳐서 원문을 덮는지
            rest = row["confirmed_statement"]
            for c in clauses:
                rest = rest.replace(c, "")
            if re.sub(r"[\s,.]", "", rest):
                out.append(F("omission", "ERROR", fid, f"절 분할 후 누락된 부분: '{rest}'"))
            else:
                out.append(F("clause_split", "INFO", fid, f"{len(clauses)}개 절로 분할 — 합치면 원문 전체를 덮음"))
        if len(clauses) > 1 and None in clauses:
            out.append(F("duplicate_membership", "WARN", fid, "전체와 절이 동시에 쓰임"))
    for fid, row in cf_by.items():
        if row["source_record_id"] not in src_ids:
            out.append(F("provenance", "ERROR", fid, "source_record_id가 04에 없음"))
        for p in row["source_prop_ids"].split("|"):
            if p not in prop_by:
                out.append(F("provenance", "ERROR", fid, f"source_prop {p}가 05에 없음"))

    for ep in episodes:
        eid = ep["episode_id"]
        rows = [(cf_by[f], c) for f, c in ep["members"] if f in cf_by]
        texts = [member_text(r, c) for r, c in rows]
        joined = " ".join(texts)
        summ = ep["summary"]

        # 2. over-merge
        srcs = {r["source_record_id"] for r, _ in rows}
        if len(srcs) > 1:
            out.append(F("over_merge", "ERROR", eid, f"서로 다른 source record 병합: {srcs}"))
        fams = {clause_family(r, c) for r, c in rows}
        if len(fams) > 1 and fams not in ALLOWED_FAMILY_MIX:
            out.append(F("over_merge", "ERROR", eid, f"인식 계열 혼합: {fams}"))
        elif len(fams) > 1:
            out.append(F("over_merge", "INFO", eid, f"허용된 혼합 {fams} — 근거: {ep['grouping_rationale']}"))
        tfs = {testifier(member_text(r, c)) for r, c in rows if FAMILY[r["confirmation_level"]] == "TESTIMONY"}
        if len(tfs) > 1:
            out.append(F("over_merge", "ERROR", eid, f"서로 다른 진술자 병합: {tfs}"))
        cats = {r["fact_category"] for r, _ in rows}
        if "ARREST_ORDER" in cats and "APPREHENSION" in cats:
            out.append(F("order_execution_conflation", "ERROR", eid, "지시와 체포 실행을 한 episode로 병합"))

        # 3. semantic strengthening
        for t in STRONG_TERMS:
            if t in summ and t not in joined:
                out.append(F("semantic_strengthening", "ERROR", eid, f"원문에 없는 강한 표현 '{t}'"))

        # 4. semantic weakening
        for h in HEDGES:
            if h in joined and h not in summ:
                out.append(F("semantic_weakening", "ERROR", eid, f"원문의 한정 표현 '{h}'가 summary에서 사라짐"))
        toks = [re.sub(r"[,.·()'\"]", "", t) for t in joined.split()]
        toks = [t for t in toks if len(t) >= 2]
        stems = [t[:-1] if len(t) > 2 else t for t in toks]  # 조사 1글자 완화
        hit = sum(1 for s in stems if s in summ)
        cov = hit / max(1, len(stems))
        if cov < 0.6:
            out.append(F("semantic_weakening", "ERROR", eid, f"원문 어휘 보존율 {cov:.2f} < 0.60"))
        elif cov < 0.8:
            out.append(F("semantic_weakening", "WARN", eid, f"원문 어휘 보존율 {cov:.2f} < 0.80 — 수동 검토"))

        # 5. epistemic collapse
        ranks = [EPISTEMIC_RANK[r["confirmation_level"]] for r, _ in rows]
        floor = min(ranks)
        if floor <= 1 and ep["layer"] not in TESTIMONY_LAYERS:
            out.append(F("epistemic_collapse", "ERROR", eid, f"진술 기반 episode인데 layer={ep['layer']}"))
        if floor == 0 and ep["layer"] != "NESTED_TESTIMONY":
            out.append(F("epistemic_collapse", "ERROR", eid, "중첩 진술 포함인데 NESTED_TESTIMONY가 아님"))
        if ep["layer"] in TESTIMONY_LAYERS and not re.search(r"진술|따르면", summ):
            out.append(F("testimony_to_fact", "ERROR", eid, "진술 episode의 summary에 진술 귀속 표현이 없음"))
        if ep["layer"] not in TESTIMONY_LAYERS and not re.search(r"보고|평가|판단|받아들|인정|명|청|신문|복명|식별|유임|정배|유배", summ):
            out.append(F("epistemic_collapse", "ERROR", eid, "공식 기록 episode의 summary에 기록 행위 표현이 없음"))

        # 6. temporal conflation
        dates = {parse_md(r["occurrence_lunar_text"]) for r, _ in rows} - {None}
        if dates and max(dates) - min(dates) > 1:
            out.append(F("temporal_conflation", "ERROR", eid, f"발생일이 다른 문장 병합: {sorted(dates)}"))
        for d in dates:
            if ep["t_min"] is not None and d < ep["t_min"] or ep["t_max"] is not None and d > ep["t_max"]:
                out.append(F("temporal_conflation", "ERROR", eid, f"member 날짜 {d}가 episode 범위 밖"))

        # 7. identity forcing
        for a, b, iid in IDENTITY_RULES:
            if a in joined and b in summ and b not in joined:
                out.append(F("identity_forcing", "ERROR", eid, f"'{a}'를 '{b}'로 치환({iid})"))
        for nm in PERSON_NAMES:
            if nm in summ and nm not in joined:
                out.append(F("identity_forcing", "ERROR", eid, f"원문에 없는 인물 '{nm}' 삽입"))

        # 8. closed-set
        n_src = len(ETC_RE.findall(joined))
        n_sum = len(ETC_RE.findall(summ))
        if n_sum < n_src:
            out.append(F("closed_set", "ERROR", eid, f"'등' {n_src}회 → summary {n_sum}회"))
        for r, c in rows:
            for p in r["source_prop_ids"].split("|"):
                pr = prop_by.get(p)
                if pr and str(pr["set_status"]).startswith("OPEN_SET") and "등" not in summ and "들" not in summ:
                    out.append(F("closed_set", "ERROR", eid, f"{p} set_status={pr['set_status']}인데 열린 집합 표지가 없음"))

        # 05 audit 대조: 절 분할의 prop 귀속
        for r, c in rows:
            if c:
                actor = c.split("은")[0].split("는")[0]
                ps = [prop_by[p] for p in r["source_prop_ids"].split("|") if p in prop_by]
                match = [p["prop_id"] for p in ps if p["reporting_actor"] == actor]
                if not match:
                    out.append(F("clause_prop_alignment", "ERROR", eid, f"{r['fact_id']} 절 주체 {actor}와 맞는 prop 없음"))
                else:
                    out.append(F("clause_prop_alignment", "INFO", eid, f"{r['fact_id']} 절 → {','.join(match)}"))

    # confirmed set 밖 사료 내용 (DAG 미반영)
    used = {p for r in cf for p in r["source_prop_ids"].split("|")}
    outside = [p for p in props if p["prop_id"] not in used]
    out.append(F("outside_confirmed_set", "INFO", "05", f"CF가 참조하지 않는 prop {len(outside)}개 — DAG node로 쓰지 않음"))
    return out, outside


# ============================================================================
# AUDIT 2 — Graph fidelity
# ============================================================================

REQUIRED_RELATIONS = [
    ("EP15", "EP25", "REVISES", "5월→6월 도난 판단 번복 보존"),
    ("EP15", "EP24", "CONTRADICTS_AT_CLAIM_LEVEL", "5/12 판단 vs 홍대협"),
    ("EP17", "EP24", "CONTRADICTS_AT_CLAIM_LEVEL", "이조원 vs 홍대협"),
    ("EP24", "EP25", "REVIEW_OF", "홍대협 → 정조"),
    ("EP26", "EP27", "REVIEW_OF", "branch A: 홍대협 질병 → 정조 전염병"),
    ("ENV01", "EP27", "CONTEXT_SUPPORTS", "branch A: 전염병 context"),
    ("ENV03", "EP27", "CONTEXT_SUPPORTS", "branch A: 전염병 지속 context"),
    ("EP01", "EP29", "RESPONSIBILITY_LINK", "branch B: 관계 악화"),
    ("EP08", "EP29", "RESPONSIBILITY_LINK", "branch B: 발언·성명"),
    ("EP11", "EP29", "RESPONSIBILITY_LINK", "branch B: 체포"),
    ("EP13", "EP29", "RESPONSIBILITY_LINK", "branch B: 구금·사망"),
    ("EP04", "EP30", "RESPONSIBILITY_LINK", "이광섭 branch: 병영 출동 준비"),
    ("EP09", "EP30", "RESPONSIBILITY_LINK", "이광섭 branch: 병사 지시"),
    ("EP14", "EP30", "REVIEW_OF", "이광섭 branch: 5/12 평가"),
    ("EP09", "EP11", "ORDER_TO_ACTION", "3/4 지시 → 실행"),
    ("EP21", "EP22", "REVIEW_OF", "윤노동 → 비변사 보류"),
    ("EP36", "EP37", "REVISES", "파직 → 유임"),
]

# 이 node 쌍을 잇는 edge는 identity condition이 필요하다
IDENTITY_SENSITIVE = {("EP07", "EP12"): "ID02", ("EP07", "EP35"): "ID02", ("EP12", "EP35"): "ID03",
                      ("EP09", "EP30"): "ID01", ("EP11", "EP30"): "ID01", ("EP09", "EP34"): "ID01",
                      ("EP08", "EP29"): "ID06", ("EP04", "EP30"): "ID07", ("EP10", "EP11"): "ID08"}

FORBIDDEN_DIRECT = [({"EP01", "EP08", "EP10", "EP29"}, {"EP13", "EP26", "EP27"},
                     "구순 관련 node → 김명신 사망/사인 node 직접 연결 금지")]


def audit2(nodes, edges, episodes, feature_links, env_rows, edge_types, bases):
    out = []
    nid = {n["node_id"]: n for n in nodes}
    ep_facts = {e["episode_id"]: {f for f, _ in e["members"]} for e in episodes}
    env_ids = {r["env_id"] for r in env_rows}
    for n in nodes:
        if n["layer"] == "ENVIRONMENT":
            ep_facts[n["node_id"]] = {n["env_id"]}
    iden = {i["identity_id"]: i for i in IDENTITY_REGISTER}

    for e in edges:
        eid = e["edge_id"]
        if e["src"] not in nid or e["dst"] not in nid:
            out.append(F("unsupported_edge", "ERROR", eid, "endpoint 없음"))
            continue
        if e["edge_type"] not in edge_types:
            out.append(F("unsupported_edge", "ERROR", eid, f"허용되지 않은 edge type {e['edge_type']}"))
        if e["edge_type"] == "CAUSES":
            out.append(F("causal_inflation", "ERROR", eid, "CAUSES edge"))
        bs = set(e["basis"].split("|")) if e["basis"] else set()
        if not bs or not bs <= bases:
            out.append(F("unsupported_edge", "ERROR", eid, f"basis 누락/오류: {e['basis']}"))
        if e["status"] not in {"OBSERVED", "DERIVED"}:
            out.append(F("latent_leak", "ERROR", eid, f"observed DAG에 status={e['status']}"))
        sup = set(e["supporting"].split("|")) if e["supporting"] else set()
        if not sup:
            out.append(F("unsupported_edge", "ERROR", eid, "근거 fact 없음"))
        allowed = ep_facts.get(e["src"], set()) | ep_facts.get(e["dst"], set())
        extra = sup - allowed
        # 근거 fact는 양 끝 node의 구성 fact여야 한다. 예외: 판단 경로를 명시하는 CF035(안핵 명령)
        extra_ok = {x for x in extra if x in {"CF035"} and e["edge_type"] == "REVIEW_OF"}
        if extra - extra_ok:
            out.append(F("unsupported_edge", "ERROR", eid, f"endpoint 밖의 근거 fact: {sorted(extra - extra_ok)}"))
        elif extra_ok:
            out.append(F("unsupported_edge", "INFO", eid, f"절차 근거로 endpoint 밖 fact 인용: {sorted(extra_ok)}"))
        if not sup & allowed:
            out.append(F("unsupported_edge", "ERROR", eid, "근거 fact가 endpoint와 무관"))

        # institutional overreach
        if bs == {"INSTITUTIONAL_COMPATIBILITY"}:
            out.append(F("institutional_overreach", "ERROR", eid, "제도 compatibility만으로 만든 edge"))

        # environmental leakage
        s, d = nid[e["src"]], nid[e["dst"]]
        if s["layer"] == "ENVIRONMENT" or d["layer"] == "ENVIRONMENT":
            if e["edge_type"] != "CONTEXT_SUPPORTS" or s["layer"] != "ENVIRONMENT":
                out.append(F("environmental_leakage", "ERROR", eid, "환경 node는 CONTEXT_SUPPORTS의 source로만 쓸 수 있음"))
            if d["layer"] not in JUDGMENT_LAYERS:
                out.append(F("environmental_leakage", "ERROR", eid, f"환경 context가 판단/보고 아닌 node({d['layer']})로 연결"))
            if bs != {"ENVIRONMENTAL_CONTEXT"}:
                out.append(F("environmental_leakage", "ERROR", eid, "환경 edge basis가 ENVIRONMENTAL_CONTEXT가 아님"))
            if s["t_min"] is not None and d["t_max"] is not None and s["t_min"] > d["t_max"]:
                out.append(F("temporal_inversion", "ERROR", eid, "환경 시점이 판단보다 뒤"))
        if "ENVIRONMENTAL_CONTEXT" in bs and s["layer"] != "ENVIRONMENT":
            out.append(F("environmental_leakage", "ERROR", eid, "환경 basis를 사건 사이 edge에 사용"))

        # temporal inversion (충돌 edge는 방향=제시 순서라 제외)
        if e["edge_type"] != "CONTRADICTS_AT_CLAIM_LEVEL":
            if s["t_min"] is not None and d["t_max"] is not None and s["t_min"] > d["t_max"]:
                out.append(F("temporal_inversion", "ERROR", eid, f"{e['src']}({s['t_min']}) > {e['dst']}({d['t_max']})"))

        # testimony → objective fact conversion
        if s["layer"] in TESTIMONY_LAYERS and d["layer"] in TESTIMONY_LAYERS and \
                e["edge_type"] in {"TEMPORAL_BEFORE", "PROCEDURAL_NEXT", "ORDER_TO_ACTION"} and not e["claim_level"]:
            out.append(F("testimony_to_fact", "ERROR", eid, "진술 node 사이 사건 순서 edge인데 claim_level 표시 없음"))

        # responsibility는 판단 수준에서만
        if e["edge_type"] == "RESPONSIBILITY_LINK" and d["layer"] != "ROYAL_JUDGMENT":
            out.append(F("causal_inflation", "ERROR", eid, "RESPONSIBILITY_LINK의 target이 royal judgment가 아님"))

        # order → execution
        if e["edge_type"] == "ORDER_TO_ACTION" and e["src"] == e["dst"]:
            out.append(F("order_execution_conflation", "ERROR", eid, "자기 자신으로의 ORDER_TO_ACTION"))

        # identity forcing
        key = (e["src"], e["dst"])
        need = IDENTITY_SENSITIVE.get(key) or IDENTITY_SENSITIVE.get((e["dst"], e["src"]))
        conds = set(filter(None, e["condition"].split("|")))
        if need and need not in conds:
            out.append(F("identity_forcing", "ERROR", eid, f"{need} 미확정 동일성에 기대는데 condition 누락"))
        for c in conds:
            if c not in iden:
                out.append(F("identity_forcing", "ERROR", eid, f"알 수 없는 identity {c}"))
            elif iden[c]["status"] == "UNRESOLVED":
                out.append(F("identity_forcing", "INFO", eid, f"조건부 edge — {c} 미확정 상태 유지"))

        for srcset, dstset, msg in FORBIDDEN_DIRECT:
            if e["src"] in srcset and e["dst"] in dstset:
                out.append(F("causal_inflation", "ERROR", eid, msg))

    # missing relation / judgment flattening
    have = {(e["src"], e["dst"], e["edge_type"]) for e in edges}
    for s, d, t, why in REQUIRED_RELATIONS:
        if (s, d, t) not in have:
            out.append(F("missing_relation", "ERROR", f"{s}->{d}", f"필수 관계 {t} 없음 ({why})"))
    deg = defaultdict(int)
    for e in edges:
        deg[e["src"]] += 1
        deg[e["dst"]] += 1
    for n in nodes:
        if deg[n["node_id"]] == 0:
            out.append(F("missing_relation", "WARN", n["node_id"], "고립 node"))
    for jid in ["EP15", "EP17", "EP24", "EP25", "EP26", "EP27", "EP28", "EP29", "EP30"]:
        if jid not in nid:
            out.append(F("judgment_flattening", "ERROR", jid, "판단 node 삭제됨"))

    # node 생성 출처: 모든 node가 CF 또는 환경 행에서 나왔는지
    for n in nodes:
        if n["layer"] == "ENVIRONMENT" and n["env_id"] not in env_ids:
            out.append(F("unsupported_node", "ERROR", n["node_id"], "환경 행 없음"))
        if n["layer"] != "ENVIRONMENT" and not n.get("member_fact_ids"):
            out.append(F("unsupported_node", "ERROR", n["node_id"], "근거 fact 없음"))
        if n.get("node_status") != "OBSERVED":
            out.append(F("latent_leak", "ERROR", n["node_id"], "observed DAG에 OBSERVED 아닌 node"))

    # feature links
    for l in feature_links:
        if l.get("creates_event") != "NO":
            out.append(F("institutional_overreach", "ERROR", l["link_id"], "feature link가 사건을 생성"))
        if l["target_id"] not in nid and l["target_id"] not in {e["edge_id"] for e in edges}:
            out.append(F("institutional_overreach", "ERROR", l["link_id"], "존재하지 않는 대상"))

    # acyclicity
    adj = defaultdict(list)
    for e in edges:
        adj[e["src"]].append(e["dst"])
    color = {}

    def dfs(u, stack):
        color[u] = 1
        for v in adj[u]:
            if color.get(v) == 1:
                return stack + [u, v]
            if v not in color:
                r = dfs(v, stack + [u])
                if r:
                    return r
        color[u] = 2
        return None
    for n in nodes:
        if n["node_id"] not in color:
            cyc = dfs(n["node_id"], [])
            if cyc:
                out.append(F("acyclicity", "ERROR", "graph", f"cycle: {cyc}"))
                break
    return out


# ============================================================================
# AUDIT 3 — Observed / Derived / Latent separation
# ============================================================================

def audit3(nodes, edges, frozen_hash, current_hash, gaps, candidates, props, worlds=None):
    out = []
    nid = {n["node_id"] for n in nodes}
    prop_ids = {p["prop_id"] for p in props}
    if frozen_hash != current_hash:
        out.append(F("freeze_violation", "ERROR", "observed_dag", "동결 이후 observed DAG가 변경됨"))
    else:
        out.append(F("freeze_violation", "INFO", "observed_dag", f"동결 해시 일치 {frozen_hash[:12]}"))
    for n in nodes:
        if n["node_status"] != "OBSERVED":
            out.append(F("latent_as_observed", "ERROR", n["node_id"], "observed 표에 비관측 node"))
    for e in edges:
        if e["status"] not in {"OBSERVED", "DERIVED"}:
            out.append(F("latent_as_observed", "ERROR", e["edge_id"], "observed 표에 LATENT edge"))
    gap_ids = {g["gap_id"] for g in gaps}
    by_gap = defaultdict(list)
    for c in candidates:
        cid = c["candidate_id"]
        by_gap[c["gap_id"]].append(c)
        if c["status"] != "LATENT":
            out.append(F("latent_as_observed", "ERROR", cid, f"후보 status={c['status']}"))
        if c["gap_id"] not in gap_ids:
            out.append(F("orphan_candidate", "ERROR", cid, "gap 없음"))
        for ln in c["latent_nodes"]:
            if ln["id"] in nid:
                out.append(F("latent_as_observed", "ERROR", cid, f"latent node id가 observed id와 충돌 {ln['id']}"))
            if not ln["id"].startswith("LN_"):
                out.append(F("latent_as_observed", "ERROR", cid, f"latent node id 접두어 오류 {ln['id']}"))
            if not ln.get("text", "").startswith("[LATENT]"):
                out.append(F("latent_as_observed", "ERROR", cid, f"{ln['id']} 서술에 [LATENT] 표지 없음"))
        lids = {ln["id"] for ln in c["latent_nodes"]}
        for le in c["latent_edges"]:
            if le["src"] not in nid | lids or le["dst"] not in nid | lids:
                out.append(F("dangling_latent_edge", "ERROR", cid, f"{le['src']}->{le['dst']}"))
            if le["src"] in nid and le["dst"] in nid:
                out.append(F("latent_as_observed", "WARN", cid,
                             f"관측 node 사이 직접 latent edge {le['src']}->{le['dst']} — LATENT 표지 확인"))
            if le.get("status") != "LATENT":
                out.append(F("latent_as_observed", "ERROR", cid, "latent edge status가 LATENT가 아님"))
            if le.get("edge_type") == "CAUSES" and le["src"].startswith("ENV"):
                out.append(F("environmental_leakage", "ERROR", cid, "환경 → CAUSES"))
        for p in c.get("audit_attestation", "").split("|"):
            if p and p not in prop_ids:
                out.append(F("provenance", "ERROR", cid, f"audit prop {p} 없음"))
        if c.get("audit_attestation") and c["status"] != "LATENT":
            out.append(F("latent_as_observed", "ERROR", cid, "audit-only 근거로 승격"))
        if c["overall"] == "HIGH" and c["source_consistency"] != "HIGH":
            out.append(F("grading", "ERROR", cid, "source_consistency가 HIGH가 아닌데 overall HIGH"))
        if c["overall"] == "HIGH" and c["n_assumptions"] >= 3:
            out.append(F("grading", "ERROR", cid, "추가 가정 3개 이상인데 HIGH"))
        env_only = c.get("support_basis") == "ENVIRONMENTAL_CONTEXT"
        if env_only and any(ln.get("individual_level") for ln in c["latent_nodes"]):
            out.append(F("environmental_leakage", "ERROR", cid, "환경만으로 개인 수준 사건 생성"))
        inst_only = c.get("support_basis") == "INSTITUTIONAL_COMPATIBILITY"
        if inst_only and c["overall"] in {"HIGH", "MEDIUM"}:
            out.append(F("institutional_overreach", "ERROR", cid, "제도 compatibility만으로 MEDIUM 이상"))
    for g, cs in by_gap.items():
        if not 1 <= len(cs) <= 5:
            out.append(F("candidate_budget", "ERROR", g, f"후보 {len(cs)}개 (허용 1~5)"))
    if worlds:
        cand = {c["candidate_id"]: c for c in candidates}
        for w in worlds:
            for b in w["latent_bridges"]:
                if b not in cand:
                    out.append(F("world_integrity", "ERROR", w["world_id"], f"알 수 없는 bridge {b}"))
                elif cand[b]["overall"] == "INCOMPATIBLE" and not w.get("rejected"):
                    out.append(F("world_integrity", "ERROR", w["world_id"], f"INCOMPATIBLE 후보 {b} 사용"))
            gs = [cand[b]["gap_id"] for b in w["latent_bridges"] if b in cand]
            if len(gs) != len(set(gs)):
                out.append(F("world_integrity", "ERROR", w["world_id"], "한 gap에 후보 2개 이상"))
    return out
