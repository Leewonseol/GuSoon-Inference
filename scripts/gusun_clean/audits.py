"""Audit 1 / 2 / 3 — 원본 pack과 다시 비교하는 자동 검사.

각 검사는 findings(dict: check, severity, target, message)를 낸다.
severity: ERROR(통과 불가) | WARN(검토 필요 — disposition 없이는 통과 불가) | UNRESOLVED(사료 자체 모호성, 허용) | INFO(보고만)
"""
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
                        out.append(F("world_integrity", "ERROR", w["world_id"], f"retained world가 대조용 후보 {b} 사용"))
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
        retained = [w for w in worlds if not w.get("rejected")]
        for g in sorted(gap_ids):
            if retained and all(g in w["unresolved_gaps"] for w in retained):
                gi = next(x for x in gaps if x["gap_id"] == g)
                cs = ", ".join(f"{c['candidate_id']}={c['overall']}" for c in by_gap[g])
                out.append(F("unresolved_gap", "UNRESOLVED", g,
                             f"{gi.get('gap_status') or 'OPEN'} — 어느 retained world도 이 gap을 메우지 않음 (후보 {cs}) · "
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
                     f"world {len(worlds)}개 (retained {sum(not w.get('rejected') for w in worlds)}, "
                     f"rejected {sum(bool(w.get('rejected')) for w in worlds)}) — 쌍별 gap 차이 ≥2 확인"))
    return out
