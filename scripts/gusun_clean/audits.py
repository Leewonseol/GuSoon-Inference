"""Audit 1 / 2 / 3 — 원본 pack과 다시 비교하는 자동 검사.

각 검사는 findings(dict: check, severity, target, message)를 낸다.
severity: ERROR(통과 불가) | WARN(검토 필요 — disposition 없이는 통과 불가) | UNRESOLVED(사료 자체 모호성, 허용) | INFO(보고만)
"""
import json
import re
from collections import defaultdict

from stage1_episodes import EPISODES, EPISTEMIC_RANK, IDENTITY_REGISTER, RESOLVED_IDS, UNRESOLVED_IDS

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

# [regression] 원문 문장마다 붙은 인식 표지. summary에서 개수가 줄면 epistemic marker 삭제로 본다.
EPISTEMIC_MARKERS = {
    "진술": re.compile(r"진술했"), "보고": re.compile(r"보고했"), "평가": re.compile(r"평가했"),
    "판단": re.compile(r"판단했"), "명": re.compile(r"명했|명하고"), "받아들": re.compile(r"받아들였"),
    "윤허": re.compile(r"윤허했"), "청": re.compile(r"청했"), "식별": re.compile(r"식별된"),
    "인정": re.compile(r"인정했|인정하지"), "차하": re.compile(r"차하했"), "복명": re.compile(r"복명하"),
    "확정못함": re.compile(r"확정하지 못했"),
}
# [regression] 책임 판단 → 직접 사인 단정
RESP_TO_CAUSE = [re.compile(p) for p in (
    r"구순(?:이|의|으로)?[^.。]{0,25}(?:때문에|탓에|으로 인해|로 인해)[^.。]{0,12}(?:죽었|사망했)",
    r"구순이[^.。]{0,25}(?:죽게 했|죽였|사망하게)",
    r"(?:사인|사망 원인)[은는이]?[^.。]{0,15}구순")]
# [regression] 환경 context → 개인 사실 단정
ENV_TO_INDIVIDUAL = [re.compile(p) for p in (
    r"(?:호서 전염병|전염병 창궐|E00\d|환경)[^.。]{0,30}(?:때문에|으로 인해|로 인해|원인)[^.。]{0,30}(?:김명신|아내|부처)",
    r"(?:김명신|아내|부처)[^.。]{0,30}(?:호서 전염병|E00\d|환경)[^.。]{0,10}(?:때문에|으로 인해|로 인해)")]


def text_regressions(text, source_text=""):
    """책임→직접 인과, 환경→개인 사실 단정. 원문(source_text)에 같은 표현이 있으면 제외."""
    hits = []
    for rx in RESP_TO_CAUSE:
        m = rx.search(text)
        if m and m.group(0) not in source_text:
            hits.append(("responsibility_to_causation", m.group(0)))
    for rx in ENV_TO_INDIVIDUAL:
        m = rx.search(text)
        if m and m.group(0) not in source_text:
            hits.append(("environment_to_individual_fact", m.group(0)))
    return hits


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
            out.append(F("over_merge", "ERROR", eid, f"서로 다른 source record 병합: {sorted(srcs)}"))
        fams = {clause_family(r, c) for r, c in rows}
        if len(fams) > 1 and fams not in ALLOWED_FAMILY_MIX:
            out.append(F("over_merge", "ERROR", eid, f"인식 계열 혼합: {sorted(fams)}"))
        elif len(fams) > 1:
            out.append(F("over_merge", "INFO", eid, f"허용된 혼합 {sorted(fams)} — 근거: {ep['grouping_rationale']}"))
        tfs = {testifier(member_text(r, c)) for r, c in rows if FAMILY[r["confirmation_level"]] == "TESTIMONY"}
        if len(tfs) > 1:
            out.append(F("over_merge", "ERROR", eid, f"서로 다른 진술자 병합: {sorted(map(str, tfs))}"))
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
                if iid in RESOLVED_IDS:  # 사용자 확정 동일성이어도 episode summary는 원문 표면형을 유지한다
                    out.append(F("surface_form_substitution", "ERROR", eid, f"'{a}'를 '{b}'로 치환({iid} 확정이지만 원문 표면형 유지 필요)"))
                else:
                    out.append(F("identity_forcing", "ERROR", eid, f"'{a}'를 '{b}'로 치환({iid} 미확정)"))
        for nm in PERSON_NAMES:
            if nm in summ and nm not in joined:
                out.append(F("identity_forcing", "ERROR", eid, f"원문에 없는 인물 '{nm}' 삽입"))

        # [regression] epistemic marker 삭제: 표지별 개수 보존
        for nm, rx in EPISTEMIC_MARKERS.items():
            a, b = len(rx.findall(joined)), len(rx.findall(summ))
            if b < a:
                out.append(F("epistemic_marker_deletion", "ERROR", eid, f"'{nm}' 표지 원문 {a}회 → summary {b}회"))
        # [regression] testimony → objective fact: 진술 문장마다 진술 귀속이 남아야 한다
        n_testi = sum(1 for r, c in rows if FAMILY[r["confirmation_level"]] == "TESTIMONY")
        if n_testi and len(re.findall(r"진술했", summ)) < n_testi:
            out.append(F("testimony_to_fact", "ERROR", eid, f"진술 member {n_testi}개인데 summary의 '진술했' {len(re.findall(r'진술했', summ))}회"))
        # [regression] actor substitution: 각 member의 진술·기록 주체가 summary에 남고, '자신'은 진술자 이외 인물로 바뀌지 않는다
        for r, c in rows:
            t = testifier(member_text(r, c))
            if t and t not in ("해당",) and t not in summ:
                out.append(F("actor_substitution", "ERROR", eid, f"{r['fact_id']} 주체 '{t}'가 summary에 없음"))
            if "자신" in member_text(r, c) and "자신" not in summ:
                out.append(F("actor_substitution", "ERROR", eid, f"{r['fact_id']}의 '자신'이 summary에서 치환됨 — 지시 대상 보존 필요"))
        lead_src = testifier(member_text(rows[0][0], rows[0][1])) if rows else None
        lead_sum = testifier(summ)
        if lead_src and lead_sum != lead_src:
            out.append(F("actor_substitution", "ERROR", eid, f"summary 첫 주어 '{lead_sum}' ≠ 원문 주체 '{lead_src}'"))
        # [regression] occurrence date ↔ record date 혼동
        recs = {parse_md(r["record_lunar_date"]) for r, _ in rows} - {None}
        chron = " ".join(r["chronology"] + " " + r["occurrence_lunar_text"] for r, _ in rows)
        for rd in recs:
            rd_txt = f"1793-{rd // 100:02d}-{rd % 100:02d}"
            if ep["t_min"] == rd and rd_txt not in chron and "공초" not in chron:
                out.append(F("occurrence_record_confusion", "ERROR", eid, f"기록일 {rd_txt}을 발생 시점으로 사용"))
        # [regression] 책임 → 직접 인과 / 환경 → 개인 사실
        for chk, frag in text_regressions(summ + " " + ep.get("caution", ""), joined):
            out.append(F(chk, "ERROR", eid, f"'{frag}'"))

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

    # 사료 모호성으로 남긴 동일성 — UNRESOLVED (데이터에 condition·caution으로 보존)
    for i in IDENTITY_REGISTER:
        if i["status"] == "RESOLVED":
            if i.get("resolved_by") != "USER" or not i.get("resolution_basis"):
                out.append(F("identity_resolution", "ERROR", i["identity_id"], "RESOLVED인데 사용자 확정 근거가 없음"))
            else:
                out.append(F("resolved_identity", "INFO", i["identity_id"],
                             f"{i['surface_a']} = {i['surface_b']} · 사용자 확정 · episode summary는 원문 표면형 유지"))
            continue
        if i["status"] != "UNRESOLVED":
            continue
        refs = set(filter(None, i["referenced_facts"].split("|")))
        eps = sorted({e["episode_id"] for e in episodes for f, _ in e["members"] if f in refs})
        ref_note = " · 참고용(model_relevance=NONE, manual_decision_required=NO)" if i.get("model_relevance") == "NONE" else ""
        out.append(F("unresolved_identity", "UNRESOLVED", i["identity_id"],
                     f"{i['surface_a']} ↔ {i['surface_b']} · 관련 episode {', '.join(eps) or '없음(DAG 미사용)'}{ref_note} · "
                     f"unresolved_reason: {i['unresolved_reason']}"))

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
        if need and need in UNRESOLVED_IDS and need not in conds:
            out.append(F("identity_forcing", "ERROR", eid, f"{need} 미확정 동일성에 기대는데 condition 누락"))
        for c in sorted(conds & RESOLVED_IDS):
            out.append(F("stale_identity_condition", "ERROR", eid, f"{c}는 사용자 확정(RESOLVED)인데 condition에 남아 있음"))
        for c in sorted(conds):
            if c not in iden:
                out.append(F("identity_forcing", "ERROR", eid, f"알 수 없는 identity {c}"))
            elif iden[c]["status"] == "UNRESOLVED":
                out.append(F("conditional_edge", "UNRESOLVED", eid,
                             f"{c} 미확정 — edge는 condition으로만 성립 · unresolved_reason: {iden[c]['unresolved_reason']}"))
        # [regression] 근거 문구가 두 표면형을 함께 쓰면 해당 identity가 condition이나 문구에 있어야 한다
        etext = e["rationale"] + " " + e["caution"]
        for iid in sorted(_identity_needs(etext) - conds - RESOLVED_IDS):
            if iid not in etext:
                out.append(F("identity_forcing", "ERROR", eid, f"근거 문구가 {iid} 동일성에 기대는데 condition 없음"))
        if "PARTIAL" in e["caution"]:
            label = e.get("uncertainty_status") or "PARTIAL"
            out.append(F("partial_tension", "UNRESOLVED", eid,
                         f"{label} — 원문 표현의 범위가 같은지 사료로 확정할 수 없어 보존 · "
                         + (f"review_decision: {e['review_decision']} · " if e.get("review_decision") else "")
                         + "unresolved_reason: " + e["caution"]))
            if e["edge_type"] == "CONTRADICTS_AT_CLAIM_LEVEL" and not e.get("uncertainty_status"):
                out.append(F("uncertainty_status", "ERROR", eid, "부분 충돌 edge에 uncertainty_status가 없음"))
        for chk, frag in text_regressions(etext):
            out.append(F(chk, "ERROR", eid, f"'{frag}'"))

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

# 후보·world 서술에 두 표면형이 함께 나오면 해당 identity 조건(IDxx)이 명시되어야 한다.
IDENTITY_TEXT_RULES = [
    ("ID01", re.compile(r"병사(?!\s*\(病)"), re.compile(r"이광섭")),
    ("ID02", re.compile(r"한 비장"), re.compile(r"한재욱")),
    ("ID03", re.compile(r"한가"), re.compile(r"한재욱")),
    ("ID04", re.compile(r"하급 보조자"), re.compile(r"한재욱")),
    ("ID05", re.compile(r"김상제"), re.compile(r"김명신|풍각 김생원")),
    ("ID06", re.compile(r"염탐 담당자"), re.compile(r"유제희")),
    ("ID07", re.compile(r"철편"), re.compile(r"철퇴")),
    ("ID11", re.compile(r"(?<!정)원돌"), re.compile(r"정원돌")),
]
FORBIDDEN_IDENTITIES = {"ID01", "ID02", "ID03", "ID04"}


# [regression] 열린 목록 닫힘: CF016·CF020·05 OPEN_SET 명단의 인물을 3명 이상 나열하면서 '등'을 빼면 안 된다
OPEN_LIST_NAMES = "정원돌|이집거|김갑득|김성손|김흥득|변지돌|변재돌|김흥길|원돌"
OPEN_LIST_RE = re.compile(rf"((?:{OPEN_LIST_NAMES})(?:·(?:{OPEN_LIST_NAMES})){{2,}})(?!·)(?!\s*[\x27\x22\u2018\u2019\u201c\u201d]?등)")


def open_set_closures(text):
    return [m.group(1) for m in OPEN_LIST_RE.finditer(text)]


def _identity_needs(text):
    return {iid for iid, a, b in IDENTITY_TEXT_RULES if a.search(text) and b.search(text)}


EVIDENCE_LEVELS = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}


def bridge_support_checks(c, nodes):
    """[regression] LATENT bridge 근거 부풀리기 검사. source_support는 bridge 자체의 근거만 평가해야 한다."""
    out = []
    cid = c["candidate_id"]
    req = ["observed_left", "observed_right", "latent_bridge_claim", "bridge_directly_attested", "source_support",
           "bridge_basis", "evidence_grade", "plausibility_grade", "reaudit_reason"]
    miss = [k for k in req if k not in c or c[k] in (None, "")]
    if miss:
        return [F("bridge_reaudit_missing", "ERROR", cid, f"재감사 필드 누락: {miss}")]
    att, sup = c["bridge_directly_attested"], c["source_support"]
    if att not in {"YES", "NO", "PARTIAL"} or sup not in EVIDENCE_LEVELS:
        out.append(F("bridge_reaudit_missing", "ERROR", cid, f"값 오류 attested={att} source_support={sup}"))
        return out
    lvl = EVIDENCE_LEVELS[sup]
    basis = set(filter(None, c["bridge_basis"].split("|")))
    ev = set(filter(None, c["bridge_evidence"].split("|")))
    if att == "YES":
        out.append(F("latent_classification", "ERROR", cid, "bridge가 사료에 직접 있음(YES) — LATENT 분류를 점검할 것"))
    # LATENT bridge support inflation
    if att == "NO" and lvl >= 3:
        out.append(F("bridge_support_inflation", "ERROR", cid, "bridge 직접 근거가 없는데(NO) source_support=HIGH"))
    if lvl >= 2 and not ev:
        out.append(F("bridge_support_inflation", "ERROR", cid, f"bridge_evidence 없이 source_support={sup}"))
    # temporal inflation
    if lvl >= 2 and basis <= {"TEMPORAL", "ENDPOINT_ONLY"}:
        out.append(F("temporal_inflation", "ERROR", cid, f"시간 인접·endpoint 내용만으로 source_support={sup}"))
    # institutional inflation
    if lvl >= 2 and basis <= {"INSTITUTIONAL", "ENVIRONMENT", "TEMPORAL"}:
        out.append(F("institutional_inflation", "ERROR", cid, f"제도·환경 가능성만으로 source_support={sup}"))
    # audit-only 상한
    if lvl >= 3 and "CONFIRMED_NON_ENDPOINT" not in basis:
        out.append(F("bridge_support_inflation", "ERROR", cid, "confirmed 비-endpoint 근거 없이 HIGH"))
    # endpoint leakage: endpoint node의 구성 fact를 bridge 근거로 인용
    by = {n["node_id"]: n for n in nodes}
    lids = {ln["id"] for ln in c["latent_nodes"]}
    ends = {x for e in c["latent_edges"] for x in (e["src"], e["dst"]) if x not in lids}
    efacts = {f for x in ends if x in by for f in str(by[x].get("member_fact_ids", "")).split("|") if f}
    leak = sorted(ev & efacts)
    if leak:
        out.append(F("endpoint_leakage", "ERROR", cid, f"endpoint 구성 fact {leak}를 bridge 근거로 인용"))
    # final grade 일관성
    if c["overall"] == "HIGH" and not (sup == "HIGH" and c["plausibility_grade"] == "HIGH"):
        out.append(F("bridge_support_inflation", "ERROR", cid, "evidence·plausibility가 모두 HIGH가 아닌데 final HIGH"))
    if sup == "NONE" and c["overall"] not in {"LOW", "INCOMPATIBLE"}:
        out.append(F("bridge_support_inflation", "ERROR", cid, "source_support NONE인데 final이 LOW보다 높음"))
    return out


OUTCOME_WORLD_RE = re.compile(r"W\d\s*(?:에서는|에서|의 경우)[^.。]{0,40}(?:정배|유배|파직|유임|처분|형장|처벌)")


def outcome_dependency_checks(worlds, candidates, nodes):
    """[regression] 확정 판단·처분은 모든 world에 공통인 OBSERVED 결말이다. world마다 결말이 달라지는 서술·구조를 막는다."""
    from stage5_worlds import COMMON_OUTCOME_NODES
    out = []
    nid = {n["node_id"]: n for n in nodes}
    outcome_ids = {x for ids in COMMON_OUTCOME_NODES.values() for x in ids}
    for x in sorted(outcome_ids):
        if x not in nid or nid[x]["node_status"] != "OBSERVED":
            out.append(F("outcome_world_dependency", "ERROR", x, "공통 결말 node가 observed graph에 없음"))
    cand = {c["candidate_id"]: c for c in candidates}
    for w in worlds:
        if w.get("role_type") not in ("COMPETING_EXPLANATION", "REJECTED"):
            out.append(F("outcome_world_dependency", "ERROR", w["world_id"], f"role_type 오류: {w.get('role_type')}"))
        for fld in ("narrative", "story_implication", "work_role", "difference", "story_question"):
            m = OUTCOME_WORLD_RE.search(w.get(fld, ""))
            if m:
                out.append(F("outcome_world_dependency", "ERROR", w["world_id"], f"{fld}: 결말을 world에 종속시킴 '{m.group(0)}'"))
        for b in w["latent_bridges"]:
            for le in cand[b]["latent_edges"]:
                if le["dst"] in outcome_ids and le["edge_type"] == "ORDER_TO_ACTION":
                    out.append(F("outcome_world_dependency", "ERROR", w["world_id"], f"{b}가 공통 결말 {le['dst']}를 latent 명령의 실행으로 만듦"))
    out.append(F("outcome_world_dependency", "INFO", "worlds",
                 f"공통 결말 node {len(outcome_ids)}개는 모든 world에 공통인 OBSERVED다. 경쟁 설명 "
                 f"{sum(w.get('role_type') == 'COMPETING_EXPLANATION' for w in worlds)}개, 배제된 설명 "
                 f"{sum(w.get('role_type') == 'REJECTED' for w in worlds)}개"))
    return out


def audit3(nodes, edges, frozen_hash, current_hash, gaps, candidates, props, worlds=None):
    from stage2_graph import EDGE_TYPES
    out = []
    nid = {n["node_id"] for n in nodes}
    layer = {n["node_id"]: n["layer"] for n in nodes}
    prop_ids = {p["prop_id"] for p in props}
    for i in IDENTITY_REGISTER:
        # 모델은 동일성을 스스로 확정하지 않는다. UNRESOLVED 또는 사용자 확정(RESOLVED + resolved_by=USER + 근거)만 허용
        if i["identity_id"] in FORBIDDEN_IDENTITIES | {"ID05", "ID06", "ID07", "ID08", "ID11"}:
            ok = i["status"] == "UNRESOLVED" or (i["status"] == "RESOLVED" and i.get("resolved_by") == "USER"
                                                and i.get("resolution_basis"))
            if not ok:
                out.append(F("identity_forcing", "ERROR", i["identity_id"], f"사용자 확정 근거 없는 status={i['status']}"))
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
                # [regression] OBSERVED/LATENT 혼동: 관측 node끼리 직접 잇는 latent edge는 관측 관계처럼 읽힌다
                out.append(F("latent_as_observed", "ERROR", cid,
                             f"관측 node 사이 직접 latent edge {le['src']}->{le['dst']} — latent node를 사이에 둘 것"))
            if le.get("status") != "LATENT":
                out.append(F("latent_as_observed", "ERROR", cid, "latent edge status가 LATENT가 아님"))
            if le.get("edge_type") == "CAUSES":
                out.append(F("causal_inflation", "ERROR", cid, f"CAUSES edge {le['src']}->{le['dst']}"))
            elif le.get("edge_type") not in EDGE_TYPES:
                out.append(F("unsupported_edge", "ERROR", cid, f"허용되지 않은 edge type {le.get('edge_type')}"))
            if le["src"] in layer and layer[le["src"]] == "ENVIRONMENT" and le.get("edge_type") != "CONTEXT_SUPPORTS":
                out.append(F("environmental_leakage", "ERROR", cid, "환경 node에서 CONTEXT_SUPPORTS 아닌 latent edge"))
            if le.get("edge_type") == "RESPONSIBILITY_LINK" and le["dst"] in layer and layer[le["dst"]] != "ROYAL_JUDGMENT":
                out.append(F("causal_inflation", "ERROR", cid, f"latent RESPONSIBILITY_LINK가 판단 아닌 observed node {le['dst']}로"))
        for p in c.get("audit_attestation", "").split("|"):
            if p and p not in prop_ids:
                out.append(F("provenance", "ERROR", cid, f"audit prop {p} 없음"))
        if c.get("audit_attestation") and c["status"] != "LATENT":
            out.append(F("latent_as_observed", "ERROR", cid, "audit-only 근거로 승격"))
        if c["overall"] == "HIGH" and c["source_consistency"] != "HIGH":
            out.append(F("grading", "ERROR", cid, "source_consistency가 HIGH가 아닌데 overall HIGH"))
        if c["overall"] == "HIGH" and c["n_assumptions"] >= 3:
            out.append(F("grading", "ERROR", cid, "추가 가정 3개 이상인데 HIGH"))
        out.extend(bridge_support_checks(c, nodes))
        env_only = c.get("support_basis") == "ENVIRONMENTAL_CONTEXT"
        if env_only and any(ln.get("individual_level") for ln in c["latent_nodes"]):
            out.append(F("environmental_leakage", "ERROR", cid, "환경만으로 개인 수준 사건 생성"))
        if env_only and c["overall"] in {"HIGH", "MEDIUM"}:
            out.append(F("environmental_leakage", "ERROR", cid, "환경 context만으로 MEDIUM 이상"))
        inst_only = c.get("support_basis") == "INSTITUTIONAL_COMPATIBILITY"
        if inst_only and c["overall"] in {"HIGH", "MEDIUM"}:
            out.append(F("institutional_overreach", "ERROR", cid, "제도 compatibility만으로 MEDIUM 이상"))
        if (env_only or inst_only) and c["overall"] == "LOW":
            out.append(F("support_basis_cap", "INFO", cid, f"{c['support_basis']}만 근거 → LOW 상한 적용"))
        conds = set(filter(None, c.get("identity_conditions", "").split("|")))
        import stage4_latent
        neg = stage4_latent.negates_resolved(c)
        if neg and c["overall"] != "INCOMPATIBLE":
            out.append(F("resolved_identity_conflict", "ERROR", cid, f"사용자 확정 {neg}을 불성립으로 전제하는데 INCOMPATIBLE이 아님"))
        elif neg:
            out.append(F("resolved_identity_conflict", "INFO", cid, f"사용자 확정 {neg}과 충돌 → INCOMPATIBLE·PRUNED"))
        for r in sorted((conds & RESOLVED_IDS) - set(neg)):
            out.append(F("stale_identity_condition", "ERROR", cid, f"{r}는 사용자 확정인데 추가 가정으로 남아 있음"))
        conds = conds & UNRESOLVED_IDS
        if conds and c["overall"] == "HIGH":
            out.append(F("identity_forcing", "ERROR", cid, f"미확정 동일성 {sorted(conds)}에 기대는데 HIGH"))
        text = " ".join([c["label"], c["description"]] + [ln["text"] for ln in c["latent_nodes"]])
        for iid in sorted(_identity_needs(text) - conds - RESOLVED_IDS):
            out.append(F("identity_forcing", "ERROR", cid, f"서술이 {iid} 동일성에 기대는데 가정·조건에 없음"))
        for chk, frag in text_regressions(text):
            out.append(F(chk, "ERROR", cid, f"'{frag}'"))
        for frag in open_set_closures(text):
            out.append(F("open_set_closure", "ERROR", cid, f"열린 목록이 '등' 없이 나열됨: '{frag}'"))
        if c.get("audit_attestation") and not c.get("supports"):
            out.append(F("audit_only_support", "INFO", cid, "confirmed 지지 없이 05 흔적만 있음 — LATENT 유지"))
    for g, cs in by_gap.items():
        if not 1 <= len(cs) <= 5:
            out.append(F("candidate_budget", "ERROR", g, f"후보 {len(cs)}개 (허용 1~5)"))
    for g in gap_ids - set(by_gap):
        out.append(F("candidate_budget", "ERROR", g, "후보 없음"))
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
            if not w.get("rejected"):
                for b in w["latent_bridges"]:
                    if b in cand and cand[b]["contradiction_risk"] == "HIGH":
                        out.append(F("world_integrity", "ERROR", w["world_id"], f"경쟁 설명 world가 대조용 후보 {b} 사용"))
            from stage5_worlds import CONFLICT_PAIRS
            for a, b, why in CONFLICT_PAIRS:
                if a in w["latent_bridges"] and b in w["latent_bridges"]:
                    out.append(F("world_integrity", "ERROR", w["world_id"], f"상충 후보 {a}+{b}"))
            if w["latent_bridges"] and "[L]" not in w.get("narrative", ""):
                out.append(F("latent_as_observed", "ERROR", w["world_id"], "서술에 [L] 표지 없음"))
            n_l = w.get("narrative", "").count("[L]")
            if n_l < len(w["latent_bridges"]):
                out.append(F("latent_as_observed", "WARN", w["world_id"], f"[L] 표지 {n_l}개 < bridge {len(w['latent_bridges'])}개"))
            for fld in ("narrative", "story_implication"):
                txt = w.get(fld, "")
                for chk, frag in text_regressions(txt):
                    out.append(F(chk, "ERROR", w["world_id"], f"{fld}: '{frag}'"))
                for frag in open_set_closures(txt):
                    out.append(F("open_set_closure", "ERROR", w["world_id"], f"{fld}: '{frag}'"))
                for iid in sorted(_identity_needs(txt) - RESOLVED_IDS):
                    if iid not in txt:
                        out.append(F("identity_forcing", "ERROR", w["world_id"], f"{fld}가 {iid} 동일성을 표시 없이 사용"))
        for i, a in enumerate(worlds):
            for b in worlds[i + 1:]:
                pa = {cand[x]["gap_id"]: x for x in a["latent_bridges"] if x in cand}
                pb = {cand[x]["gap_id"]: x for x in b["latent_bridges"] if x in cand}
                diff = sum(pa.get(g) != pb.get(g) for g in gap_ids)
                if diff < 2:
                    out.append(F("world_integrity", "ERROR", f"{a['world_id']}/{b['world_id']}", f"차이 gap {diff}개 < 2"))
        out.extend(outcome_dependency_checks(worlds, candidates, nodes))
        retained = [w for w in worlds if not w.get("rejected")]
        for g in sorted(gap_ids):
            if retained and all(g in w["unresolved_gaps"] for w in retained):
                gi = next(x for x in gaps if x["gap_id"] == g)
                cs = ", ".join(f"{c['candidate_id']}={c['overall']}" for c in by_gap[g])
                out.append(F("unresolved_gap", "UNRESOLVED", g,
                             f"{gi.get('gap_status') or 'OPEN'} — 어느 경쟁 설명 world도 이 gap을 메우지 않음 (후보 {cs}) · "
                             + (f"review_decision: {gi['review_decision']} · " if gi.get("review_decision") else "")
                             + f"unresolved_reason: {gi['why_gap']} 관측 근거({gi['observed_anchor_facts']})에 사유를 적은 문장이 없음"))
        # [regression] 사용자가 열어 두기로 한 gap(OPEN_UNRESOLVED)은 어떤 world도 채우면 안 된다
        for gi in gaps:
            if gi.get("gap_status") == "OPEN_UNRESOLVED":
                for w in worlds:
                    used = [b for b in w["latent_bridges"] if b in cand and cand[b]["gap_id"] == gi["gap_id"]]
                    if used:
                        out.append(F("open_gap_filled", "ERROR", w["world_id"], f"{gi['gap_id']}은 OPEN_UNRESOLVED인데 {used} 사용"))
        out.append(F("world_integrity", "INFO", "worlds",
                     f"world {len(worlds)}개 (경쟁 설명 {sum(not w.get('rejected') for w in worlds)}, "
                     f"rejected {sum(bool(w.get('rejected')) for w in worlds)}) — 쌍별 gap 차이 ≥2 확인"))
    return out


# ============================================================================
# AUDIT 4 — Mechanism Super-DAG
# ============================================================================

def audit4(sd, nodes, edges, frozen_hash, graph_hash_fn, worlds, candidates):
    from stage6_mechanisms import BRANCH_A, BRANCH_B, CAND_MAP, MECHANISMS, ORDER, OBSERVED_ANCHORED, STRUCT_VARS, usable
    from stage5_worlds import COMMON_OUTCOME_NODES
    out = []
    sdn = {n["node_id"]: n for n in sd["nodes"]}
    cand = {c["candidate_id"]: c for c in candidates}
    # 1. frozen observed graph 보존
    if graph_hash_fn(nodes, edges) != frozen_hash:
        out.append(F("frozen_graph_changed", "ERROR", "observed_dag", "frozen observed graph 해시가 바뀜"))
    for n in nodes:
        s = sdn.get(n["node_id"])
        want = "CONTEXT" if n["layer"] == "ENVIRONMENT" else "OBSERVED"
        if not s:
            out.append(F("frozen_graph_changed", "ERROR", n["node_id"], "frozen node가 Super-DAG에 없음"))
        elif s["sd_status"] != want or s["label"] != n["title"]:
            out.append(F("observed_to_latent", "ERROR", n["node_id"], f"frozen node 상태·내용 변경: {s['sd_status']}"))
    frozen_ids = {n["node_id"] for n in nodes}
    for n in sd["nodes"]:
        if n["node_id"] not in frozen_ids and (n["sd_status"] == "OBSERVED" or n["node_type"] == "OBSERVED_EVENT"):
            out.append(F("context_to_fact", "ERROR", n["node_id"],
                         "frozen graph에 없는 관측 사건 node가 Super-DAG에서 새로 생김(새 역사적 사실 생성)"))
    fe = {(e["edge_id"], e["src"], e["dst"], e["edge_type"], e["status"]) for e in edges}
    se = {(e["edge_id"], e["src"], e["dst"], e["edge_type"], e["sd_status"]) for e in sd["edges"] if e["origin"] == "FROZEN"}
    if fe != se:
        out.append(F("frozen_graph_changed", "ERROR", "edges", f"frozen edge 불일치 {len(fe ^ se)}건"))
    # 2. LATENT → OBSERVED 둔갑
    for n in sd["nodes"]:
        if n["node_type"] in ("MECHANISM", "STRUCTURAL_VARIABLE", "CANDIDATE_BRIDGE") and n["sd_status"] != "LATENT_MECHANISM":
            out.append(F("latent_to_observed", "ERROR", n["node_id"], f"{n['node_type']}인데 status={n['sd_status']}"))
        if n["node_type"] == "CANDIDATE_BRIDGE" and "ALL" in n["worlds"]:
            out.append(F("world_latent_promoted", "ERROR", n["node_id"], "world별 LATENT 후보가 모든 world 공통으로 표시됨"))
    # 3–6. context·environment·institution leakage, 책임 → 생물학 사인
    for e in sd["edges"]:
        s, d = sdn.get(e["src"]), sdn.get(e["dst"])
        if not s or not d:
            out.append(F("dangling_edge", "ERROR", e["edge_id"], f"{e['src']}→{e['dst']}"))
            continue
        if e["edge_type"] == "CAUSES":
            out.append(F("causal_inflation", "ERROR", e["edge_id"], "CAUSES edge"))
        if s["node_type"] == "INSTITUTIONAL_CONTEXT" and d["node_type"] in ("OBSERVED_EVENT", "CANDIDATE_BRIDGE"):
            out.append(F("institution_to_event", "ERROR", e["edge_id"], f"제도 피쳐 {e['src']}가 사건·후보 {e['dst']}를 직접 만듦"))
        if s["node_type"] == "ENV_CONTEXT" and e["origin"] != "FROZEN":
            if d["node_type"] in ("OBSERVED_EVENT", "CANDIDATE_BRIDGE"):
                out.append(F("environment_to_personal_fact", "ERROR", e["edge_id"], f"환경 {e['src']}가 개인 사건·후보 {e['dst']}에 직접 연결"))
            if d["node_type"] == "MECHANISM" and e["edge_type"] != "CONTEXT_COMPATIBLE":
                out.append(F("environment_to_personal_fact", "ERROR", e["edge_id"], "환경 → 메커니즘은 CONTEXT_COMPATIBLE만 허용"))
        if s["sd_status"] == "CONTEXT" and e["origin"] != "FROZEN" and e["edge_type"] not in ("CONSTRAINS", "CONTEXT_COMPATIBLE"):
            out.append(F("context_to_fact", "ERROR", e["edge_id"], f"context edge type {e['edge_type']}"))
        if e["origin"] != "FROZEN":
            sb = e["src"] in BRANCH_B or (s["node_type"] == "CANDIDATE_BRIDGE" and s["branch"] == "B_PROCEDURAL")
            da = e["dst"] in BRANCH_A or (d["node_type"] == "CANDIDATE_BRIDGE" and d["branch"] == "A_BIOLOGICAL")
            sa = e["src"] in BRANCH_A or (s["node_type"] == "CANDIDATE_BRIDGE" and s["branch"] == "A_BIOLOGICAL")
            db = e["dst"] in BRANCH_B or (d["node_type"] == "CANDIDATE_BRIDGE" and d["branch"] == "B_PROCEDURAL")
            if (sb and da) or (sa and db):
                out.append(F("responsibility_to_biological", "ERROR", e["edge_id"], f"책임 branch와 생물학 branch를 연결 {e['src']}→{e['dst']}"))
    # 7–10. world configuration
    from stage5_worlds import WORLD_ROLES
    pair = {(x["a"], x["b"]): x for x in sd["interactions"]}
    rejected = {k for k, v in WORLD_ROLES.items() if v["role_type"] == "REJECTED"}
    for w in worlds:
        wid = w["world_id"]
        cfg = sd["configs"][wid]
        if wid in rejected and w["role_type"] != "REJECTED":
            out.append(F("w6_reactivation", "ERROR", wid, f"REJECTED로 정한 world가 {w['role_type']}로 되살아남"))
            continue
        if w["role_type"] == "REJECTED":
            if any(wid in x["cooccur_worlds"].split(", ") for x in sd["interactions"]):
                out.append(F("w6_reactivation", "ERROR", wid, "REJECTED world가 공존 분석에 들어감"))
            if any(wid in i["affected_worlds"].split(", ") for i in sd["interventions"]):
                out.append(F("w6_reactivation", "ERROR", wid, "REJECTED world가 개입 분석에 들어감"))
            continue
        if w["role_type"] != "COMPETING_EXPLANATION":
            out.append(F("world_merge", "ERROR", wid, f"role_type {w['role_type']}"))
        for m in ORDER:
            v = cfg[m]
            if v not in ("ON", "OFF", "PARTIAL", "UNSPECIFIED"):
                out.append(F("config_value", "ERROR", wid, f"{m}={v}"))
            prim = [b for b in w["latent_bridges"] if CAND_MAP[b][0] == m]
            neg = [b for b in w["latent_bridges"] if CAND_MAP[b][3] == m]
            if v == "OFF" and prim:
                out.append(F("off_mechanism_alive", "ERROR", wid, f"{m}=OFF인데 {prim}가 살아 있음"))
            if v == "OFF" and not neg:
                out.append(F("unspecified_as_off", "ERROR", wid, f"{m}=OFF인데 부정 후보가 없음(UNSPECIFIED여야 함)"))
            if v == "UNSPECIFIED" and (prim or neg) and m not in OBSERVED_ANCHORED:
                out.append(F("config_value", "ERROR", wid, f"{m}=UNSPECIFIED인데 관련 후보 {prim + neg} 사용"))
        for i, a in enumerate(ORDER):
            for b in ORDER[i + 1:]:
                p = pair[(a, b)]
                if p["coexistence"] == "INCOMPATIBLE" and cfg[a] == "ON" and cfg[b] == "ON":
                    out.append(F("incompatible_coexistence", "ERROR", wid, f"{a}·{b}가 INCOMPATIBLE인데 둘 다 ON"))
        from stage5_worlds import CONFLICT_PAIRS
        for x, y, _ in CONFLICT_PAIRS:
            if x in w["latent_bridges"] and y in w["latent_bridges"]:
                out.append(F("world_merge", "ERROR", wid, f"상충 후보 {x}+{y}가 한 world에 있음"))
    bridges = {w["world_id"]: tuple(w["latent_bridges"]) for w in worlds}
    if len(set(bridges.values())) != len(bridges):
        out.append(F("world_merge", "ERROR", "worlds", "서로 다른 world의 bridge 구성이 같음(병합 의심)"))
    # 11. 공통 결말
    outcome = {x for ids in COMMON_OUTCOME_NODES.values() for x in ids}
    for x in outcome:
        n = sdn.get(x)
        if not n or n["sd_status"] != "OBSERVED" or n["worlds"] != "ALL (공통)":
            out.append(F("outcome_world_dependency", "ERROR", x, "공통 결말이 OBSERVED·모든 world 공통으로 표시되지 않음"))
    for e in sd["edges"]:
        if e["dst"] in outcome and sdn.get(e["src"], {}).get("node_type") == "CANDIDATE_BRIDGE" and e["edge_type"] == "ORDER_TO_ACTION":
            out.append(F("outcome_world_dependency", "ERROR", e["edge_id"], "후보가 공통 결말을 명령 실행으로 만듦"))
    # UNRESOLVED: 사료가 결정하지 않는 것
    for x in sd["interactions"]:
        if x["a"] in OBSERVED_ANCHORED or x["b"] in OBSERVED_ANCHORED or "MB" in (x["a"], x["b"]):
            continue
        if not x["cooccur_worlds"]:
            out.append(F("coexistence_undetermined", "UNRESOLVED", f"{x['a']}×{x['b']}",
                         f"{x['coexistence']} — 충돌 근거는 없지만 어느 경쟁 world도 둘을 함께 쓰지 않아, 함께 작동했는지는 사료로 결정되지 않음"))
        elif "COMPLEMENT" in x["relation"]:
            out.append(F("interaction_direction", "UNRESOLVED", f"{x['a']}×{x['b']}",
                         f"함께 쓰이는 world({x['cooccur_worlds']})가 있지만 어느 메커니즘이 다른 쪽을 이끌었는지(방향)는 사료에 없음"))
    for v in STRUCT_VARS:
        ins = [m for m in v["inputs"] if m in MECHANISMS]
        if v["op"] in ("OR", "XOR") and len(ins) >= 2:
            gaps = set(v["gap"].split("|"))
            ms = sorted({CAND_MAP[c["candidate_id"]][0] for c in candidates if usable(c) and c["gap_id"] in gaps
                         and CAND_MAP[c["candidate_id"]][0] in ins})
            if len(ms) >= 2:
                out.append(F("multiple_explanations", "UNRESOLVED", v["var"],
                             f"{v['op']}: {', '.join(ms)}가 같은 관측 전이({v['target']})를 설명할 수 있음. 어느 쪽이 실제로 작동했는지는 사료로 결정되지 않음"))
    for n in sd["nodes"]:
        if n["sd_status"] == "UNRESOLVED":
            out.append(F("unresolved_item", "UNRESOLVED", n["node_id"], n["label"]))
    from collections import Counter
    out.append(F("super_dag_summary", "INFO", "super_dag",
                 "node " + ", ".join(f"{k} {v}" for k, v in sorted(Counter(n["sd_status"] for n in sd["nodes"]).items()))
                 + " · edge " + ", ".join(f"{k} {v}" for k, v in sorted(Counter(e["sd_status"] for e in sd["edges"]).items()))))
    out.append(F("frozen_graph_changed", "INFO", "observed_dag", f"동결 해시 일치 {frozen_hash[:12]}"))
    return out


# ============================================================================
# AUDIT 5 — Interactive visualization (docs/data/*.json ↔ canonical)
# ============================================================================
UI_TEMPORAL_EDGE_TYPES = {"TEMPORAL_BEFORE", "PROCEDURAL_NEXT", "ORDER_TO_ACTION", "REVIEW_OF", "REVISES",
                          "INFORMATION_FLOW", "RESPONSIBILITY_LINK"}
UI_STATUS_GROUPS = {"OBSERVED": "OBSERVED", "DERIVED": "DERIVED", "LATENT_MECHANISM": "LATENT",
                    "CONTEXT": "CONTEXT", "UNRESOLVED": "UNRESOLVED"}
UI_BACKBONE_GUARD = "AUDIT5:BACKBONE_GUARD"


UI_VIEW_NOTICE_MARK = "AUDIT5:VIEW_HIDDEN_NOTICE"
UI_VIEW_SCOPE_MARK = "AUDIT5:VIEW_SCOPE"
UI_READ_PX = 11 * 96 / 72 - 1e-6       # 11pt = 14.667px
UI_MIN_LINE_HEIGHT = 1.6
_REMAKE_CACHE = {}


def _css_px(value, root_vars):
    """CSS font-size 값 → px. var(--x)는 :root 값으로 푼다. 모르는 단위는 None."""
    v = value.strip()
    m = re.fullmatch(r"var\((--[\w-]+)\)", v)
    if m:
        v = root_vars.get(m.group(1), "").strip()
    m = re.fullmatch(r"([\d.]+)(px|pt)", v)
    if not m:
        return None
    return float(m.group(1)) * (96 / 72 if m.group(2) == "pt" else 1)


def _css_lh(value, root_vars):
    v = value.strip()
    m = re.fullmatch(r"var\((--[\w-]+)\)", v)
    if m:
        v = root_vars.get(m.group(1), "").strip()
    return float(v) if re.fullmatch(r"[\d.]+", v) else None


def audit5_views(ui, canon, app_js=None, app_css=None):
    """관점별 View가 canonical의 부분집합인지, 글자·줄 간격·첫 화면 배율이 가독성 기준을 지키는지, 좌표가 결정적인지 본다."""
    import build_visualization as bv
    from stage6_mechanisms import BRANCH_A, BRANCH_B
    out = []
    sd = ui["super_dag"]
    cn = {r["node_id"]: r for r in canon["sd_nodes"]}
    ce = {r["edge_id"]: r for r in canon["sd_edges"]}
    observed = {k for k, r in cn.items() if r["node_type"] == "OBSERVED_EVENT"}
    eps = {r["node_id"]: r for r in canon["episodes"]}
    views = ui["views"]["views"]
    typo = ui["meta"].get("typography", {})
    boxes = {n["id"]: n.get("display", {}) for n in sd["nodes"]}
    # 13-1·2. View = canonical node·edge 부분집합, 새 node·edge 없음
    if set(ui["views"].get("order", [])) != set(views):
        out.append(F("view_not_subset", "ERROR", "views.order", "View 순서 목록과 View 정의가 다름"))
    for vid, v in views.items():
        nodes = set(v.get("nodes", []))
        bad_n = sorted(nodes - set(cn))
        if bad_n:
            out.append(F("view_not_subset", "ERROR", f"view:{vid}", f"canonical에 없는 node {bad_n[:5]}"))
        bad_e = sorted(set(v.get("edges", [])) - set(ce))
        if bad_e:
            out.append(F("view_not_subset", "ERROR", f"view:{vid}", f"canonical에 없는 edge {bad_e[:5]}"))
        want_e = sorted(k for k, e in ce.items() if e["src"] in nodes and e["dst"] in nodes)
        if sorted(v.get("edges", [])) != want_e:
            out.append(F("view_not_subset", "ERROR", f"view:{vid}", "View edge 목록이 'View node 사이의 canonical edge 전부'와 다름"))
        if not set(v.get("core", [])) | set(v.get("context", [])) == nodes:
            out.append(F("view_not_subset", "ERROR", f"view:{vid}", "core·context 합이 View node 목록과 다름"))
        if v.get("policy") == "subset":
            if sorted(v.get("hidden_observed", [])) != sorted(observed - nodes):
                out.append(F("view_hidden_notice_missing", "ERROR", f"view:{vid}", "숨긴 OBSERVED 목록이 실제(관측 node − View node)와 다름"))
            pos = v.get("layout", {}).get("positions", {})
            if set(pos) != nodes:
                out.append(F("view_not_subset", "ERROR", f"view:{vid}", "View 좌표가 View node 목록과 다름(없는 node 좌표 또는 좌표 없는 node)"))
        elif v.get("policy") == "all" and nodes != set(cn):
            out.append(F("view_not_subset", "ERROR", f"view:{vid}", "Overview가 canonical node 전부를 담지 않음"))
        elif v.get("policy") not in ("all", "subset", "dim"):
            out.append(F("view_not_subset", "ERROR", f"view:{vid}", f"알 수 없는 표시 정책 {v.get('policy')}"))
    if not any(v.get("policy") == "all" for v in views.values()):
        out.append(F("view_not_subset", "ERROR", "views", "전체 Overview View가 없음"))
    # 13-3. View metadata에 상태·판정·해석 필드가 없음(표시 범위·좌표만)
    allowed = getattr(bv, "VIEW_KEYS", set())
    banned = re.compile(r"(status|grade|overall|config|coexist|result|worlds|interpret|important|turning|story)", re.I)
    for vid, v in views.items():
        extra = sorted(set(v) - allowed)
        if extra:
            out.append(F("view_status_changed", "ERROR", f"view:{vid}", f"View metadata에 허용되지 않은 필드 {extra}"))
        for nid, p in v.get("layout", {}).get("positions", {}).items():
            if set(p) != {"x", "y", "lane"}:
                out.append(F("view_status_changed", "ERROR", f"view:{vid}:{nid}", f"View 좌표 항목에 좌표 외 필드 {sorted(set(p) - {'x', 'y', 'lane'})}"))
                break
        for k in v:
            if banned.search(k):
                out.append(F("view_status_changed", "ERROR", f"view:{vid}", f"View metadata 필드 '{k}'가 상태·판정·해석을 담을 수 있음"))
    # 13-4. 숨긴 OBSERVED가 사라진 것으로 읽히지 않게 하는 표시
    for vid, v in views.items():
        if v.get("policy") != "subset":
            continue
        note = v.get("notice", "")
        if not ("시각적 필터" in note and "삭제" in note and "ON/OFF" in note):
            out.append(F("view_hidden_notice_missing", "ERROR", f"view:{vid}", "subset View에 '시각적 필터·삭제 아님·분석상 ON/OFF 아님' 안내가 없음"))
    if app_js is not None:
        i = app_js.find(UI_VIEW_NOTICE_MARK)
        if i < 0 or "hidden_observed" not in app_js[i:i + 2500] or "show-context" not in app_js[i:i + 2500]:
            out.append(F("view_hidden_notice_missing", "ERROR", "app.js", "숨긴 OBSERVED 개수·전체 맥락 표시 안내를 그리는 코드가 없음"))
        j = app_js.find(UI_VIEW_SCOPE_MARK)
        if j < 0 or "if (outside) hide = true" not in app_js[j:j + 300] or "isSubsetMode()" not in app_js:
            out.append(F("view_hidden_notice_missing", "ERROR", "app.js", "View 범위 숨김이 subset View로 한정되지 않음"))
    # 13-5. node label clipping(잘림·말줄임·글자 누락·크기 부족)
    line_px = typo.get("line_px", 0)
    for nid, d in boxes.items():
        c = cn.get(nid)
        if c is None or not d:
            out.append(F("label_clipped", "ERROR", nid, "node 표시 정보(display)가 없음"))
            continue
        head, body = bv.node_text(c)
        want = re.sub(r"\s+", "", head + body)
        got = re.sub(r"\s+", "", "".join(d.get("lines", [])))
        if got != want:
            out.append(F("label_clipped", "ERROR", nid, f"node label이 canonical 글자를 모두 담지 않음('{''.join(d.get('lines', []))[:30]}')"))
        if d.get("label") != "\n".join(d.get("lines", [])):
            out.append(F("label_clipped", "ERROR", nid, "표시 label과 줄 목록이 다름"))
        if ("…" in d.get("label", "") and "…" not in head + body) or ("..." in d.get("label", "") and "..." not in head + body):
            out.append(F("label_clipped", "ERROR", nid, "node label에 말줄임(…)이 들어감"))
        widest = max([bv.text_px(x, typo.get("node_font_px", bv.NODE_FONT)) for x in d.get("lines", [""])] or [0])
        if widest > d.get("text_w", 0) + 0.01 or d.get("w", 0) - 2 * d.get("pad_x", 0) < d.get("text_w", 0) - 0.01:
            out.append(F("label_clipped", "ERROR", nid, f"가장 긴 줄 {widest:.0f}px > 글자 영역 {d.get('text_w')}px"))
        if d.get("h", 0) + 0.6 < len(d.get("lines", [])) * line_px + 2 * d.get("pad_y", 0):
            out.append(F("label_clipped", "ERROR", nid, f"node 높이 {d.get('h')}px가 {len(d.get('lines', []))}줄을 담지 못함"))
    # 13-6. node·edge label 글자 크기
    for k in ("node_font_px", "edge_font_px", "far_id_font_px"):
        if typo.get(k, 0) < UI_READ_PX:
            out.append(F("font_too_small", "ERROR", f"typography.{k}", f"{typo.get(k)}px < 11pt(14.667px)"))
    if app_js is not None:
        for m in re.finditer(r"'font-size':\s*([\d.]+)", app_js):
            if float(m.group(1)) < UI_READ_PX:
                out.append(F("font_too_small", "ERROR", "app.js", f"그래프 글자 크기 {m.group(1)}px < 11pt"))
        if "'font-size': TY.node_font_px" not in app_js:
            out.append(F("font_too_small", "ERROR", "app.js", "node label 글자 크기가 typography.node_font_px를 쓰지 않음"))
    # 13-7. UI 글자 크기
    if app_css is not None:
        root = dict(re.findall(r"(--[\w-]+):\s*([^;]+);", app_css.split("}")[0]))
        for m in re.finditer(r"font-size:\s*([^;}\n]+)", app_css):
            px = _css_px(m.group(1), root)
            if px is None or px < UI_READ_PX:
                out.append(F("font_too_small", "ERROR", "app.css", f"font-size {m.group(1).strip()} < 11pt 또는 확인할 수 없는 단위"))
        if not re.search(r"body\s*\{[^}]*font-size:\s*var\(--fs\)", app_css) or (_css_px("var(--fs)", root) or 0) < UI_READ_PX:
            out.append(F("font_too_small", "ERROR", "app.css", "body 기본 글자 크기가 11pt 이상으로 정해지지 않음"))
        # 13-8. line-height
        for m in re.finditer(r"line-height:\s*([^;}\n]+)", app_css):
            lh = _css_lh(m.group(1), root)
            if lh is None or lh < UI_MIN_LINE_HEIGHT:
                out.append(F("line_height_too_small", "ERROR", "app.css", f"line-height {m.group(1).strip()} < 1.6 또는 단위 있는 값"))
        if not re.search(r"body\s*\{[^}]*line-height:", app_css):
            out.append(F("line_height_too_small", "ERROR", "app.css", "body line-height가 없음"))
    if typo.get("line_height", 0) < UI_MIN_LINE_HEIGHT:
        out.append(F("line_height_too_small", "ERROR", "typography.line_height", f"{typo.get('line_height')} < 1.6"))
    if app_js is not None and "'line-height': TY.line_height" not in app_js:
        out.append(F("line_height_too_small", "ERROR", "app.js", "node label line-height가 typography.line_height를 쓰지 않음"))
    # 13-9. 첫 화면에서 label이 읽히는 배율
    overlay_min = min([typo.get(k, 0) for k in ("lane_font_px", "lane_sub_font_px", "band_font_px", "band_sub_font_px", "tick_font_px")] or [0])
    for vid, v in views.items():
        z = v.get("initial", {}).get("min_zoom", 0)
        if z * typo.get("node_font_px", 0) < UI_READ_PX:
            out.append(F("initial_label_unreadable", "ERROR", f"view:{vid}",
                         f"첫 화면 최소 배율 {z} × node 글자 {typo.get('node_font_px')}px = {z * typo.get('node_font_px', 0):.1f}px < 11pt"))
        if z * overlay_min < UI_READ_PX:
            out.append(F("initial_label_unreadable", "ERROR", f"view:{vid}", f"첫 화면에서 lane·시간 구간 글자 {z * overlay_min:.1f}px < 11pt"))
    if typo.get("read_zoom", 0) * typo.get("node_font_px", 0) < UI_READ_PX:
        out.append(F("initial_label_unreadable", "ERROR", "typography.read_zoom", "축소 지도 전환 배율에서 label이 11pt보다 작음"))
    # 13-10. branch A ↔ B 직접 edge(관점별 View 포함)
    for vid, v in views.items():
        nodes = set(v.get("nodes", []))
        for eid in v.get("edges", []):
            e = ce.get(eid)
            if e and ((e["src"] in BRANCH_A and e["dst"] in BRANCH_B) or (e["src"] in BRANCH_B and e["dst"] in BRANCH_A)):
                out.append(F("responsibility_to_biological", "ERROR", f"view:{vid}", f"branch A/B 직접 edge {eid}"))
        if v.get("groups"):
            ga, gb = set(v["groups"].get("A", [])), set(v["groups"].get("B", []))
            if not (ga | gb) <= nodes or ga & gb:
                out.append(F("responsibility_to_biological", "ERROR", f"view:{vid}", "branch 묶음이 View node 밖에 있거나 서로 겹침"))
    # 13-11. W6 REJECTED는 audit5 본문 4절에서 검사한다(View가 world 값을 바꾸지 않음은 13-3).
    # 13-12. 좌표: 결정적·겹침 없음·View 안에서도 시간 순서
    key = (id(canon), json.dumps(sorted((p["key"], f["check"], f["severity"], f["message"]) for p in ui["interactions"]["pairs"]
                                        for f in p["audit4"]), ensure_ascii=False))
    if key not in _REMAKE_CACHE:
        findings = [dict(check=f["check"], severity=f["severity"], target=p["key"], message=f["message"])
                    for p in ui["interactions"]["pairs"] for f in p["audit4"]]
        r1, r2 = bv.make_ui(canon, findings), bv.make_ui(canon, findings)
        _REMAKE_CACHE.clear()
        _REMAKE_CACHE[key] = (r1, r2)
    r1, r2 = _REMAKE_CACHE[key]

    def coords(u):
        return (json.dumps({n["id"]: n["layout"] for n in u["super_dag"]["nodes"]}, sort_keys=True),
                json.dumps([u["super_dag"][k] for k in ("lanes", "bands", "ticks", "extent", "anchor")], sort_keys=True),
                json.dumps({vid: v.get("layout") for vid, v in u["views"]["views"].items()}, sort_keys=True))
    if coords(r1) != coords(r2):
        out.append(F("layout_nondeterministic", "ERROR", "layout", "같은 입력으로 두 번 계산한 좌표가 다름"))
    elif coords(ui) != coords(r1):
        out.append(F("layout_nondeterministic", "ERROR", "layout", "화면 데이터의 좌표가 canonical 입력에서 다시 계산한 좌표와 다름"))
    layouts = [("overview", {n["id"]: n["layout"] for n in sd["nodes"]})]
    layouts += [(vid, v["layout"]["positions"]) for vid, v in views.items() if v.get("layout", {}).get("positions")]
    for vid, pos in layouts:
        ids = sorted(pos)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                pa, pb, A, B = pos[a], pos[b], boxes.get(a, {}), boxes.get(b, {})
                if abs(pa["x"] - pb["x"]) * 2 < A.get("w", 0) + B.get("w", 0) and abs(pa["y"] - pb["y"]) * 2 < A.get("h", 0) + B.get("h", 0):
                    out.append(F("view_node_overlap", "ERROR", f"view:{vid}", f"{a}와 {b}의 node 상자가 겹침"))
        dated = sorted((int(eps[k].get("t_max") or eps[k].get("t_min")), pos[k]["x"], k) for k in ids
                       if k in observed and (eps[k].get("t_max") or eps[k].get("t_min")))
        for i in range(len(dated)):
            for j in range(i + 1, len(dated)):
                if dated[i][0] < dated[j][0] and dated[i][1] >= dated[j][1]:
                    out.append(F("temporal_order", "ERROR", f"view:{vid}", f"{dated[i][2]}가 {dated[j][2]}보다 이른데 오른쪽(또는 같은 열)에 놓임"))
        if vid != "overview":
            lanes = {l["id"]: l for l in views[vid]["layout"]["lanes"]}
            for k in ids:
                if cn.get(k, {}).get("sd_status") == "CONTEXT" and lanes.get(pos[k]["lane"], {}).get("kind") != "context":
                    out.append(F("context_as_event", "ERROR", f"view:{vid}:{k}", "View 좌표에서 context가 context lane 밖(사건 lane)에 놓임"))
    n_sub = sum(1 for v in views.values() if v.get("policy") == "subset")
    out.append(F("view_summary", "INFO", "views",
                 f"View {len(views)}개(subset {n_sub}) 모두 canonical node·edge 부분집합, 좌표 결정적·겹침 0. node 글자 {typo.get('node_font_px')}px·"
                 f"line-height {typo.get('line_height')}·첫 화면 배율 ≥ {min(v['initial']['min_zoom'] for v in views.values())}"))
    return out


UI_RUNTIME_GUARD = "AUDIT5:RUNTIME_GUARD"
UI_EMPTY_VIEW_GUARD = "AUDIT5:EMPTY_VIEW_GUARD"
_ASSET_REF = re.compile(r'(?:src|href)="((?:css|js|data|vendor)/[^"?]+)(?:\?v=([0-9a-f]*))?"')
REQUIRED_ASSETS = ("css/app.css", "vendor/cytoscape/cytoscape.min.js", "data/bundle.js", "js/app.js")


def audit5_runtime(index_html, app_js, asset_versions):
    """실행 시 그래프가 빈 화면이 되지 않게 하는 조건(배포 캐시·DOM 계약·fail-safe)을 본다.
    index_html: docs/index.html 문자열. asset_versions: {경로: 지금 파일 내용 해시(build_visualization.asset_version)}."""
    out = []
    # 14-1. index.html이 싣는 css·js 주소에 현재 내용 해시(?v=)가 붙어 있어야 새 HTML이 캐시된 옛 app.js와 섞이지 않는다
    refs = {m.group(1): m.group(2) for m in _ASSET_REF.finditer(index_html)}
    for rel in REQUIRED_ASSETS:
        if rel not in refs:
            out.append(F("stale_asset_version", "ERROR", "index.html", f"{rel}을 싣지 않음"))
    for rel, v in sorted(refs.items()):
        want = (asset_versions or {}).get(rel)
        if not v or v != want:
            out.append(F("stale_asset_version", "ERROR", "index.html",
                         f"{rel}?v={v or '(없음)'} ≠ 현재 내용 해시 {want} — 배포 직후 브라우저가 옛 파일과 섞어 초기화가 멈출 수 있음"))
    # 14-2. app.js가 찾는 DOM id가 index.html(또는 app.js가 직접 만드는 HTML)에 모두 있어야 한다(없으면 null 접근으로 초기화 중단)
    have = set(re.findall(r'id="([\w-]+)"', index_html)) | set(re.findall(r'id="([\w-]+)"', app_js or ""))
    want_ids = set(re.findall(r"\$\('([\w-]+)'\)", app_js or "")) | set(re.findall(r"getElementById\('([\w-]+)'\)", app_js or ""))
    for i in sorted(want_ids - have):
        out.append(F("dom_id_missing", "ERROR", "app.js", f"#{i}를 찾지만 index.html에 없음 — 초기화가 그 줄에서 멈춰 빈 그래프가 됨"))
    # 14-3. fail-safe: 초기화 예외 → '시각화 초기화 오류', 보이는 node 0 → 안내 + Overview 1회 복구
    i = index_html.find(UI_RUNTIME_GUARD)
    tail = index_html[index_html.find('src="js/app.js'):] if 'src="js/app.js' in index_html else ""
    if (i < 0 or i > index_html.find('src="vendor/') or 'id="viz-error"' not in index_html
            or "시각화 초기화 오류" not in tail or "window.__viz" not in tail):
        out.append(F("runtime_failsafe_missing", "ERROR", "index.html", "app.js 초기화 예외 시 그래프 영역에 '시각화 초기화 오류'를 보여 주는 guard가 없음"))
    j = (app_js or "").find(UI_EMPTY_VIEW_GUARD)
    seg = (app_js or "")[j:j + 1500] if j >= 0 else ""
    if (not seg or "현재 View에서 표시할 그래프를 찾지 못했습니다" not in seg or "setView('overview')" not in seg
            or "initialViewport();\n  guardEmptyView();" not in (app_js or "")):
        out.append(F("runtime_failsafe_missing", "ERROR", "app.js", "보이는 node가 0일 때 안내하고 Overview로 복구하는 guard가 없음"))
    return out


def audit5(ui, canon, frozen_hash, app_js=None, app_css=None, index_html=None, asset_versions=None):
    """화면 데이터가 canonical 값을 그대로 옮겼는지, 화면 규칙이 관측·LATENT·context 경계를 지키는지 본다.
    ui: docs/data/*.json을 읽은 dict(+ '_bundle': bundle.js 문자열). canon: build_visualization.load_canonical() 결과.
    app_js·app_css: 화면 코드(주어지면 backbone·View 숨김 안내·글자 크기·line-height도 검사).
    index_html·asset_versions: 주어지면 실행 시 빈 그래프 방지 조건(audit5_runtime)도 검사."""
    import json as _json
    from stage5_worlds import COMMON_OUTCOME_NODES, WORLD_ROLES
    from stage6_mechanisms import BRANCH_A, BRANCH_B
    out = []
    sd = ui["super_dag"]
    cn = {r["node_id"]: r for r in canon["sd_nodes"]}
    ce = {r["edge_id"]: r for r in canon["sd_edges"]}
    un = {n["id"]: n for n in sd["nodes"]}
    ue = {e["id"]: e for e in sd["edges"]}
    eps = {r["node_id"]: r for r in canon["episodes"]}
    oes = {r["edge_id"]: r for r in canon["observed_edges"]}
    # 0. 해시·출처·개수
    if not (ui["meta"].get("frozen_hash") == canon["freeze"]["sha256"] == frozen_hash):
        out.append(F("frozen_graph_changed", "ERROR", "meta", f"화면 데이터의 동결 해시 {ui['meta'].get('frozen_hash', '')[:16]} ≠ {frozen_hash[:16]}"))
    if ui["meta"].get("generated_from") != canon["_hashes"]:
        out.append(F("stale_ui_data", "ERROR", "meta", "화면 데이터가 현재 canonical 파일(sha256)에서 만들어지지 않음"))
    if len(sd["nodes"]) != len(cn) or ui["meta"]["counts"]["nodes"] != len(cn) or sd.get("node_count") != len(cn):
        out.append(F("count_mismatch", "ERROR", "nodes", f"화면 node {len(sd['nodes'])} ≠ canonical {len(cn)}"))
    if len(sd["edges"]) != len(ce) or ui["meta"]["counts"]["edges"] != len(ce) or sd.get("edge_count") != len(ce):
        out.append(F("count_mismatch", "ERROR", "edges", f"화면 edge {len(sd['edges'])} ≠ canonical {len(ce)}"))
    if "_bundle" in ui:
        b = ui["_bundle"]
        try:
            payload = _json.loads(b[b.index("window.GUSUN_DATA = ") + len("window.GUSUN_DATA = "):].rstrip().rstrip(";"))
            if payload != {k: ui[k] for k in payload} or set(payload) != {k for k in ui if not k.startswith("_")}:
                out.append(F("bundle_mismatch", "ERROR", "bundle.js", "bundle.js 내용이 data/*.json과 다름"))
        except (ValueError, KeyError) as ex:
            out.append(F("bundle_mismatch", "ERROR", "bundle.js", f"bundle.js를 읽을 수 없음: {ex}"))
    # 1. node
    for nid, n in un.items():
        if nid not in cn:
            out.append(F("ui_node_not_canonical", "ERROR", nid, "canonical Super-DAG에 없는 node가 화면 데이터에 있음"))
        elif n["canonical"] != cn[nid]:
            out.append(F("ui_node_altered", "ERROR", nid, "화면 node의 canonical 필드가 CSV와 다름"))
        if nid in eps and n.get("observed") != eps[nid] and n["canonical"].get("node_type") == "OBSERVED_EVENT":
            out.append(F("ui_node_altered", "ERROR", nid, "관측 node의 episode 필드가 episode_nodes.csv와 다름"))
    for nid in cn:
        if nid not in un:
            out.append(F("ui_node_missing", "ERROR", nid, "canonical node가 화면 데이터에 없음"))
    for vid, v in ui["views"]["views"].items():
        for x in v["nodes"] + v.get("emphasis", []):
            if x not in cn:
                out.append(F("ui_node_not_canonical", "ERROR", f"view:{vid}", f"view가 canonical에 없는 node {x}를 씀"))
    # 2. edge
    for eid, e in ue.items():
        if eid not in ce:
            out.append(F("ui_edge_not_canonical", "ERROR", eid, f"canonical에 없는 edge {e['canonical'].get('src')}→{e['canonical'].get('dst')} "
                                                                f"({e['canonical'].get('edge_type')})"))
        elif e["canonical"] != ce[eid]:
            out.append(F("ui_edge_altered", "ERROR", eid, "화면 edge의 canonical 필드가 CSV와 다름"))
        if e["canonical"].get("origin") == "FROZEN" and e.get("frozen") != oes.get(eid):
            out.append(F("ui_edge_altered", "ERROR", eid, "frozen edge 필드가 observed_edges.csv와 다름"))
        if e["canonical"].get("edge_type") == "CAUSES":
            out.append(F("ui_edge_not_canonical", "ERROR", eid, "CAUSES edge"))
    for eid in ce:
        if eid not in ue:
            out.append(F("ui_edge_missing", "ERROR", eid, "canonical edge가 화면 데이터에 없음"))
    # 3. 상태
    if ui["meta"].get("status_groups") != UI_STATUS_GROUPS:
        out.append(F("status_changed", "ERROR", "meta.status_groups", "표시 상태 그룹이 canonical status와 1:1이 아님"))
    for nid, n in un.items():
        c = cn.get(nid)
        if c and (n["canonical"]["sd_status"] != c["sd_status"] or n["status_group"] != UI_STATUS_GROUPS.get(c["sd_status"])):
            out.append(F("status_changed", "ERROR", nid, f"{c['sd_status']} → 화면 {n['canonical']['sd_status']}/{n['status_group']}"))
    for eid, e in ue.items():
        c = ce.get(eid)
        if c and (e["canonical"]["sd_status"] != c["sd_status"] or e["status_group"] != UI_STATUS_GROUPS.get(c["sd_status"])):
            out.append(F("status_changed", "ERROR", eid, f"{c['sd_status']} → 화면 {e['canonical']['sd_status']}/{e['status_group']}"))
    # 4. W6 REJECTED
    w = ui["worlds"]
    cfg = {r["world_id"]: r for r in canon["configs"]}
    rejected = sorted({k for k, v in WORLD_ROLES.items() if v["role_type"] == "REJECTED"} | {k for k, r in cfg.items() if r["role_type"] == "REJECTED"})
    if "W6" not in rejected:
        out.append(F("w6_not_rejected", "ERROR", "W6", "canonical에서 W6이 REJECTED가 아님"))
    for wid in rejected:
        s = w["selections"].get(wid, {})
        if (w["configurations"].get(wid, {}).get("role_type") != "REJECTED" or not s.get("rejected") or not s.get("banner")
                or wid not in w.get("rejected", []) or wid not in ui["interactions"].get("excluded_worlds", [])):
            out.append(F("w6_not_rejected", "ERROR", wid, "REJECTED world가 화면에서 REJECTED로 표시되지 않음(배너·제외 목록·role_type)"))
        for p in ui["interactions"]["pairs"]:
            if wid in [x.strip() for x in p["canonical"]["cooccur_worlds"].split(",")]:
                out.append(F("w6_not_rejected", "ERROR", wid, f"REJECTED world가 공존 분석 {p['key']}에 들어감"))
        for r in ui["interventions"]["rows"]:
            if wid in [x.strip() for x in r["canonical"]["affected_worlds"].split(",")]:
                out.append(F("w6_not_rejected", "ERROR", wid, "REJECTED world가 개입 분석에 들어감"))
    for wid, s in w["selections"].items():
        if wid != "ALL" and wid not in rejected and s.get("rejected"):
            out.append(F("w6_not_rejected", "ERROR", wid, "경쟁 설명 world가 REJECTED로 표시됨"))
    # 5. 공통 결말·관측 backbone이 어떤 world 선택에서도 사라지지 않는가
    outcome = sorted({x for ids in COMMON_OUTCOME_NODES.values() for x in ids})
    observed = sorted(k for k, r in cn.items() if r["sd_status"] == "OBSERVED")
    if sorted(w.get("backbone", [])) != observed:
        out.append(F("outcome_dropped", "ERROR", "worlds.backbone", "화면 backbone이 canonical OBSERVED node 집합과 다름"))
    if {k: list(v) for k, v in COMMON_OUTCOME_NODES.items()} != w.get("common_outcome_nodes"):
        out.append(F("outcome_dropped", "ERROR", "worlds.common_outcome_nodes", "공통 결말 목록이 stage5 COMMON_OUTCOME_NODES와 다름"))
    for x in outcome:
        if x not in un or not un[x].get("common_outcome"):
            out.append(F("outcome_dropped", "ERROR", x, "공통 결말 node가 화면 데이터에 없거나 표시되지 않음"))
    for wid in ["ALL"] + list(cfg):
        s = w["selections"].get(wid)
        if s is None:
            out.append(F("outcome_dropped", "ERROR", wid, "world 선택 규칙이 없음"))
            continue
        vis, hid, dim = set(s["always_visible"]), set(s["hideable"]), set(s["dim"])
        for x in observed:
            if x not in vis or x in hid or x in dim:
                out.append(F("outcome_dropped", "ERROR", f"{wid}:{x}",
                             ("공통 결말" if x in outcome else "관측 node") + "이 world 선택에서 숨김·흐림 대상이 됨"))
    if app_js is not None:
        i = app_js.find(UI_BACKBONE_GUARD)
        if i < 0 or "hide = false" not in app_js[i:i + 300]:
            out.append(F("outcome_dropped", "ERROR", "app.js", "backbone 보호 규칙(어떤 선택에서도 OBSERVED node를 숨기지 않음)이 화면 코드에 없음"))
    # 6. UNSPECIFIED ≠ OFF
    from stage6_mechanisms import ORDER
    disp = w.get("config_display", {})
    for v in ("ON", "PARTIAL", "UNSPECIFIED", "OFF"):
        if disp.get(v, {}).get("label") != v:
            out.append(F("unspecified_as_off", "ERROR", f"config_display.{v}", f"표시 이름이 값과 다름: {disp.get(v, {}).get('label')}"))
    if disp.get("UNSPECIFIED", {}).get("css") == disp.get("OFF", {}).get("css"):
        out.append(F("unspecified_as_off", "ERROR", "config_display", "UNSPECIFIED와 OFF가 같은 모양으로 표시됨"))
    n_off = 0
    for wid, r in cfg.items():
        for m in ORDER:
            n_off += r[m] == "OFF"
            uv = w["configurations"].get(wid, {}).get(m)
            sv = w["selections"].get(wid, {}).get("mechanism_state", {}).get(m)
            if uv != r[m] or sv != r[m]:
                out.append(F("unspecified_as_off", "ERROR", f"{wid}.{m}", f"canonical {r[m]} → 화면 {uv}/{sv}"))
        if w["configurations"].get(wid) != r:
            out.append(F("unspecified_as_off", "ERROR", wid, "world configuration 행이 CSV와 다름"))
    if w.get("off_count") != n_off:
        out.append(F("unspecified_as_off", "ERROR", "worlds.off_count", f"OFF 개수 {w.get('off_count')} ≠ canonical {n_off}"))
    # 7. context를 사건처럼 표시
    lanes = {l["id"]: l for l in sd["lanes"]}
    for nid, n in un.items():
        c = cn.get(nid, n["canonical"])
        if c["sd_status"] != "CONTEXT" and n["canonical"].get("sd_status") != "CONTEXT":
            continue
        lay = n["layout"]
        bad = []
        if n["canonical"].get("node_type") not in ("INSTITUTIONAL_CONTEXT", "ENV_CONTEXT"):
            bad.append(f"node_type {n['canonical'].get('node_type')}")
        if n["status_group"] != "CONTEXT":
            bad.append(f"status_group {n['status_group']}")
        if lay.get("dated") or lay.get("date_key") is not None or lay.get("band") is not None:
            bad.append("날짜 축(시간 구간)에 놓임")
        if lanes.get(lay.get("lane"), {}).get("kind") != "context":
            bad.append(f"context lane이 아님({lay.get('lane')})")
        if nid in w.get("backbone", []) or n.get("common_outcome"):
            bad.append("관측 backbone으로 표시됨")
        if bad:
            out.append(F("context_as_event", "ERROR", nid, "context를 역사적 사건처럼 표시: " + "; ".join(bad)))
    # 8·9. 환경 → 개인 감염, 책임 → 생물학 사인
    ntype = {k: v["canonical"].get("node_type") for k, v in un.items()}
    nbranch = {k: v["canonical"].get("branch") for k, v in un.items()}
    for eid, e in ue.items():
        c = e["canonical"]
        s, d, t = c.get("src"), c.get("dst"), c.get("edge_type")
        if ntype.get(s) == "ENV_CONTEXT":
            if ntype.get(d) == "CANDIDATE_BRIDGE" or t not in ("CONTEXT_SUPPORTS", "CONTEXT_COMPATIBLE") or \
                    (ntype.get(d) == "OBSERVED_EVENT" and t != "CONTEXT_SUPPORTS") or (ntype.get(d) == "MECHANISM" and d != "MB"):
                out.append(F("environment_to_individual", "ERROR", eid, f"환경 context {s}가 개인 수준 사건·후보 {d}에 {t}로 연결"))
        sb = s in BRANCH_B or (ntype.get(s) == "CANDIDATE_BRIDGE" and nbranch.get(s) == "B_PROCEDURAL")
        da = d in BRANCH_A or (ntype.get(d) == "CANDIDATE_BRIDGE" and nbranch.get(d) == "A_BIOLOGICAL")
        sa = s in BRANCH_A or (ntype.get(s) == "CANDIDATE_BRIDGE" and nbranch.get(s) == "A_BIOLOGICAL")
        db = d in BRANCH_B or (ntype.get(d) == "CANDIDATE_BRIDGE" and nbranch.get(d) == "B_PROCEDURAL")
        if (sb and da) or (sa and db):
            out.append(F("responsibility_to_biological", "ERROR", eid, f"책임 branch와 생물학 사인 branch를 직접 연결 {s}→{d}"))
    death = ui["views"]["views"].get("death", {})
    ga, gb = set(death.get("groups", {}).get("A", [])), set(death.get("groups", {}).get("B", []))
    cross = sorted(eid for eid, e in ue.items() if (e["canonical"]["src"] in ga and e["canonical"]["dst"] in gb)
                   or (e["canonical"]["src"] in gb and e["canonical"]["dst"] in ga))
    if not ga or not gb or cross or death.get("cross_edges"):
        out.append(F("responsibility_to_biological", "ERROR", "view:death",
                     f"질병·사망 view의 A/B branch 분리 실패(직접 edge {cross or death.get('cross_edges')})"))
    # 10. 시간 순서
    bands = {b["id"]: b for b in sd["bands"]}
    dated = []
    for nid, n in un.items():
        if n["canonical"].get("node_type") != "OBSERVED_EVENT":
            continue
        ep = eps.get(nid, {})
        want = int(ep.get("t_max") or ep.get("t_min") or 0) or None
        lay = n["layout"]
        if lay.get("date_key") != want or bool(lay.get("dated")) != (want is not None):
            out.append(F("temporal_order", "ERROR", nid, f"정렬 기준일 {lay.get('date_key')} ≠ episode t_max/t_min {want}"))
        b = bands.get(lay.get("band"))
        if b is None or not (b["x0"] <= lay["x"] <= b["x1"]) or bool(b["dated"]) != (want is not None):
            out.append(F("temporal_order", "ERROR", nid, f"시간 구간 {lay.get('band')} 밖에 놓임(x={lay['x']})"))
        if want is not None:
            dated.append((want, lay["x"], nid))
    dated.sort()
    for i in range(len(dated)):
        for j in range(i + 1, len(dated)):
            (ka, xa, a), (kb, xb, bnid) = dated[i], dated[j]
            if ka < kb and xa >= xb:
                out.append(F("temporal_order", "ERROR", f"{a}/{bnid}", f"{a}({ka})가 {bnid}({kb})보다 이른데 오른쪽(또는 같은 열)에 놓임"))
    order_ids = [b["id"] for b in sd["bands"]]
    for p, q in zip(order_ids, order_ids[1:]):
        if bands[p]["x1"] > bands[q]["x0"]:
            out.append(F("temporal_order", "ERROR", f"{p}/{q}", "시간 구간이 왼쪽 → 오른쪽 순서가 아님"))
    xs = {nid: n["layout"]["x"] for nid, n in un.items()}
    dk = {nid: n["layout"].get("date_key") for nid, n in un.items()}
    for eid, e in ue.items():
        c = e["canonical"]
        if c.get("origin") == "FROZEN" and c.get("edge_type") in UI_TEMPORAL_EDGE_TYPES and dk.get(c["src"]) and dk.get(c["dst"]):
            if xs[c["src"]] >= xs[c["dst"]]:
                out.append(F("temporal_order", "ERROR", eid, f"{c['edge_type']} {c['src']}→{c['dst']}가 화면에서 뒤로(또는 같은 열로) 감"))
    # 11. 후보 등급
    crow = {r["candidate_id"]: r for r in canon["candidates"]}
    for cid, r in crow.items():
        u = ui["candidates"]["rows"].get(cid)
        if u is None:
            out.append(F("candidate_grade_changed", "ERROR", cid, "후보가 화면 데이터에 없음"))
            continue
        diff = [k for k in r if u.get(k) != r[k]]
        if diff or set(u) != set(r):
            out.append(F("candidate_grade_changed", "ERROR", cid, f"후보 값이 canonical과 다름: {', '.join(diff) or '필드 구성'}"))
    for cid in ui["candidates"]["rows"]:
        if cid not in crow:
            out.append(F("candidate_grade_changed", "ERROR", cid, "canonical에 없는 후보"))
    # 12. 개입 결과
    rows = ui["interventions"]["rows"]
    if len(rows) != len(canon["interventions"]):
        out.append(F("intervention_changed", "ERROR", "interventions", f"개입 행 수 {len(rows)} ≠ canonical {len(canon['interventions'])}"))
    for i, (u, r) in enumerate(zip(rows, canon["interventions"])):
        if u["canonical"] != r:
            out.append(F("intervention_changed", "ERROR", f"do({r['mechanism']}=OFF)/{r['variable']}",
                         f"개입 결과가 canonical과 다름: {r['result']} → 화면 {u['canonical'].get('result')}"))
        for x in u.get("path_nodes", []):
            if x not in cn:
                out.append(F("intervention_changed", "ERROR", f"do({r['mechanism']}=OFF)", f"강조 경로에 canonical에 없는 node {x}"))
    # (추가) 공존 판정
    prow = canon["interactions"]
    if len(ui["interactions"]["pairs"]) != len(prow) or any(u["canonical"] != r for u, r in zip(ui["interactions"]["pairs"], prow)):
        out.append(F("interaction_changed", "ERROR", "interactions", "공존 판정이 mechanism_interaction_matrix.csv와 다름"))
    if [dict(r) for r in canon["rules"]] != ui["interactions"].get("rules"):
        out.append(F("interaction_changed", "ERROR", "rules", "구조 규칙이 qualitative_structural_rules.csv와 다름"))
    # 13. 관점별 View·가독성(시각화 개선 검사)
    out += audit5_views(ui, canon, app_js, app_css)
    # 14. 실행 시 빈 그래프 방지(배포 캐시·DOM 계약·fail-safe)
    if index_html is not None:
        out += audit5_runtime(index_html, app_js, asset_versions)
    # INFO
    und = sorted(nid for nid, n in un.items() if n["canonical"].get("node_type") == "OBSERVED_EVENT" and not n["layout"].get("dated"))
    out.append(F("ui_summary", "INFO", "docs/data",
                 f"node {len(un)} · edge {len(ue)} · 후보 {len(ui['candidates']['rows'])} · world 선택 {len(w['selections'])} · "
                 f"view {len(ui['views']['views'])} · 개입 행 {len(rows)} · 공존 쌍 {len(ui['interactions']['pairs'])} (canonical과 같음)"))
    out.append(F("temporal_order", "INFO", "layout",
                 f"날짜 있는 관측 node {len(dated)}개가 기준일 순서대로 왼쪽 → 오른쪽에 놓임. 날짜 미기록 node {', '.join(und) or '없음'}는 "
                 "시간 축 밖 '날짜 미기록' 구간에 두었다(위치가 날짜를 뜻하지 않음)."))
    out.append(F("responsibility_to_biological", "INFO", "view:death",
                 f"A branch {len(ga)}개 · B branch {len(gb)}개 node 사이 직접 edge 0개"))
    out.append(F("frozen_graph_changed", "INFO", "observed_dag", f"동결 해시 일치 {frozen_hash[:12]}"))
    return out
