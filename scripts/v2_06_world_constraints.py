#!/usr/bin/env python3
"""GuSoon v2 possible-world logical constraint layer (definitions only).

Defines world variables and logical constraints that separate allowed from
impossible combinations. It does not enumerate worlds, sample, compute
posteriors, merge candidates or create episodes / unknown events.

Three levels are kept apart:
  ATT_<EC>   attestation fact: the record of the statement exists (source-fixed TRUE)
  E_<EC>     object-level claim: what the candidate asserts, with its polarity,
             is historically true (free; never fixed by DENIED / findings)
  SAME_*, ID_*, REF_*  structural hypotheses (occurrence, person, referent identity)
plus interpretation / causal-level / open-set membership / time variables,
created only where a pair-stage relation depends on them.

DOUBTED candidates (EC0024) assert no polarity: E_EC0024 means "the
implausibility judgment is sound", which does not imply that no theft occurred.

Small truth-table checks over the handful of variables in each special test
verify constraint semantics; they are not a world enumeration.

Outputs:
  output/19_v2_world_variables.csv
  output/20_v2_logical_constraints.csv
  output/21_v2_world_constraint_audit.csv
  output/22_v2_impossible_combination_examples.csv
  output/23_v2_world_constraint_validation.csv
  logs/v2_world_constraints.log
  database/gusun_v2.duckdb: world_variables, logical_constraints,
                            world_constraint_audit, impossible_combination_examples
"""

import csv
import hashlib
import itertools
import logging
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "database" / "gusun_v2.duckdb"
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
SHA_PATH = RAW_DIR / "gusun_research_v2_SHA256SUMS.txt"

PROTECTED_TABLES = ["source_records", "source_faithful_propositions", "person_membership", "search_log",
                    "atomic_propositions", "entity_resolution_candidates", "open_set_normalized",
                    "event_projection_decisions", "historical_event_candidates", "event_candidate_support",
                    "candidate_pair_generation", "same_event_review", "conflict_group_summary"]

HARD, COND, NOTC, ANNO = "HARD_LOGICAL", "CONDITIONAL", "NOT_A_CONSTRAINT", "ANNOTATION"


# ---------------------------------------------------------------- formulas
def V(n):
    return ("var", n)


def Not(x):
    return ("not", x)


def And(*xs):
    return ("and",) + xs


def Imp(a, b):
    return ("imp", a, b)


def Iff(a, b):
    return ("iff", a, b)


def Eq(var, val):
    return ("eq", var, val)


def Lt(a, b):
    return ("lt", a, b)


def In(var, text):
    return ("in", var, text)


def render(f):
    k = f[0]
    if k == "var":
        return f[1]
    if k == "not":
        return "¬" + render(f[1])
    if k == "and":
        return "(" + " ∧ ".join(render(x) for x in f[1:]) + ")"
    if k == "imp":
        return f"({render(f[1])} → {render(f[2])})"
    if k == "iff":
        return f"({render(f[1])} ↔ {render(f[2])})"
    if k == "eq":
        return f"{f[1]} = {f[2]}"
    if k == "lt":
        return f"{f[1]} < {f[2]}"
    if k == "in":
        return f"{f[1]} ∈ [{f[2]}]"
    raise ValueError(k)


def variables_of(f):
    k = f[0]
    if k == "var":
        return {f[1]}
    if k in ("eq", "in"):
        return {f[1]}
    if k == "lt":
        return {f[1], f[2]}
    return set().union(*(variables_of(x) for x in f[1:]))


def evaluate(f, asg):
    """Three-valued: True / False / None (some variable unassigned or temporal)."""
    k = f[0]
    if k == "var":
        return asg.get(f[1])
    if k == "eq":
        return None if f[1] not in asg else asg[f[1]] == f[2]
    if k in ("lt", "in"):
        return None
    if k == "not":
        v = evaluate(f[1], asg)
        return None if v is None else not v
    if k == "and":
        vals = [evaluate(x, asg) for x in f[1:]]
        if any(v is False for v in vals):
            return False
        return None if any(v is None for v in vals) else True
    if k == "imp":
        a, b = evaluate(f[1], asg), evaluate(f[2], asg)
        if a is False or b is True:
            return True
        if a is True and b is False:
            return False
        return None
    if k == "iff":
        a, b = evaluate(f[1], asg), evaluate(f[2], asg)
        return None if a is None or b is None else a == b
    raise ValueError(k)


def same_var(a, b):
    a, b = sorted((a, b))
    return f"SAME_{a}_{b}"


# ---------------------------------------------------------------- identity variables (from output/08 + pair stage)
# (surface core, candidate core, scope prop ids) -> variable id
ID_VARS = [
    ("풍각 김생원", "김명신", "P0066|P0067|P0070", "ID_PUNGGAK_KIMSAENGWON__KIMMYEONGSIN"),
    ("흥덕 김생원", "김갑득", "P0066|P0068", "ID_HEUNGDEOK_KIMSAENGWON__KIMGAPDEUK"),
    ("풍각 김상제", "김명신", "P0096", "ID_PUNGGAK_KIMSANGJE__KIMMYEONGSIN"),
    ("풍각의 상주", "김명신", "P0072", "ID_PUNGGAK_SANGJU__KIMMYEONGSIN"),
    ("원돌", "정원돌", "P0097", "ID_WONDOL__JEONGWONDOL"),
    ("한가", "한재욱", "P0113", "ID_HANGA__HANJAEUK"),
    ("한 비장", "한재욱", "P0079|P0080|P0081|P0082|P0084", "ID_HANBIJANG__HANJAEUK"),
    ("한 비장", "한가", "P0079|P0080|P0081|P0082|P0084|P0113", "ID_HANBIJANG__HANGA"),
    ("재돌", "변재돌", "P0062|P0075|P0080", "ID_JAEDOL__BYEONJAEDOL"),
    ("남편", "재돌", "P0081", "ID_NAMPYEON__JAEDOL"),
    ("변가의 처", "자미덕", "P0043", "ID_BYEONGA_CHEO__JAMIDEOK"),
    ("병영의 하급 보조자", "한재욱", "P0027|P0028", "ID_HAGEUP_BOJOJA__HANJAEUK"),
    ("병영의 하급 보조자", "유제희", "P0027|P0028", "ID_HAGEUP_BOJOJA__YUJEHUI"),
    ("아전", "유제희", "P0101", "ID_AJEON_P0101__YUJEHUI"),
    ("병영 비장", "한가", "P0103", "ID_BIJANG_P0103__HANGA"),
    ("병영 비장", "한가", "P0012", "ID_BIJANG_P0012__HANGA"),
    ("병사", "이광섭", "P0069|P0074", "ID_BYEONGSA_SRC2_006__IGWANGSEOP"),
    ("병사", "이광섭", "P0027", "ID_BYEONGSA_P0027__IGWANGSEOP"),
    ("장교 일행", "이진욱 등 장교", "P0063", "ID_JANGGYO_ILHAENG_P0063__IJINUK_GROUP"),
    ("장교 일행", "이진욱 등 장교", "P0069", "ID_JANGGYO_ILHAENG_P0069__IJINUK_GROUP"),
]
EXTRA_ID_VARS = [("ID_JANGGYO_1MYEONG__JOGYEWAN", "장교 1명", "조계완",
                  "pair stage only (PR0741, 근거 없음); output/08에는 없음")]
ID_OF_DEP = {
    "한 비장=한재욱 (CANDIDATE)": "ID_HANBIJANG__HANJAEUK",
    "변가의 처=자미덕 (CANDIDATE)": "ID_BYEONGA_CHEO__JAMIDEOK",
    "병영의 하급 보조자=한재욱 (UNRESOLVED)": "ID_HAGEUP_BOJOJA__HANJAEUK",
    "풍각 김상제=김명신 (STRONGLY_SUPPORTED, identity assumption)": "ID_PUNGGAK_KIMSANGJE__KIMMYEONGSIN",
    "장교 1명=조계완 (근거 없음)": "ID_JANGGYO_1MYEONG__JOGYEWAN",
}

# ---------------------------------------------------------------- interpretation / causal-level / membership variables
INTERP_VARS = {
    "CAUSELEVEL_EC0038": ("CAUSAL_LEVEL", "EC0038", "이조원이 말한 '구순이 구성한 죄안 때문에 사망'의 원인 층위",
                          "{DIRECT_CAUSE, RESPONSIBILITY_ATTRIBUTION}", "PR0450|PR0452|PR0453 CONTRADICTORY_IF_SAME_CAUSAL_LEVEL"),
    "FABSCOPE_EC0012": ("INTERPRETATION", "EC0012", "응답자들이 말한 '구순이 도난 상황을 꾸밈'의 범위",
                        "{FULL_FABRICATION, EXAGGERATION_OR_PARTIAL}", "CONTRADICTORY_IF_FULL_FABRICATION (7 pairs)"),
    "FABSCOPE_EC0030": ("INTERPRETATION", "EC0030", "이조원이 말한 '구순이 도난 상황을 꾸밈'의 범위",
                        "{FULL_FABRICATION, EXAGGERATION_OR_PARTIAL}", "CONTRADICTORY_IF_FULL_FABRICATION (7 pairs)"),
    "TERM_EC0005_JOSA_INCLUDES_SINMUN": ("INTERPRETATION", "EC0005", "이형원 보고의 '조사함'이 신문을 포함하는 의미이다",
                                         "{TRUE, FALSE}", "PR0063 CONTRADICTORY_IF_JOSA_EQUALS_SINMUN"),
    "SAMELIST_EC0052_EC0118": ("INTERPRETATION", "EC0052|EC0118",
                               "구순이 써 준 이름들(윤노동)과 유제희가 직접 염탐했다는 '그 이름들'이 같은 명단이다",
                               "{TRUE, FALSE}", "PR0559 CONFLICT_IF_SAME_LIST"),
    "SENSE_EC0031": ("INTERPRETATION", "EC0031", "이조원의 '구순이 지세랑이라는 말을 만듦'의 의미",
                     "{COINED_TERM, FABRICATED_USE_IN_CASE}", "PR0378|PR0388|PR0389 재검토 (만들었다의 의미)"),
    "SENSE_EC0149": ("INTERPRETATION", "EC0149", "정조의 '그 죄를 면함'의 의미",
                     "{FACTUAL_NEGATION, LEGAL_CLEARANCE}", "PR0389 재검토 (면함의 의미)"),
    "SENSE_EC0132_EXCLUDES_LARGE_BAND": ("INTERPRETATION", "EC0132",
                                         "홍대협의 '큰 화적 사건이 아니라 좀도둑 수준' 평가가 30여 명 규모의 무리를 배제한다",
                                         "{TRUE, FALSE}", "PR0688 재검토 (규모 평가의 의미)"),
    "SENSE_EC0040": ("INTERPRETATION", "EC0040", "이조원의 '김명신이 죽은 뒤 따라 죽음'의 '따라'의 의미",
                     "{SEQUENCE_ONLY, CAUSAL_FOLLOWING_EXCLUDING_EPIDEMIC}", "EC0040–EC0145 REVIEW pair"),
    "MEMBER_KIMMYEONGSIN_IN_OS01": ("OPEN_SET_MEMBERSHIP", "OS01|EC0009",
                                    "김명신이 '모진 형벌을 받은 무고한 평민들'(P0007, open set) 구성원이다",
                                    "{TRUE, FALSE} (free; open set이므로 FALSE로 고정하지 않음)",
                                    "PR0093|PR0094 CONTRADICTORY_IF_OPEN_SET_MEMBER"),
    "MEMBER_KIMMYEONGSIN_IN_OS07": ("OPEN_SET_MEMBERSHIP", "OS07|EC0056",
                                    "김명신이 '참혹한 형벌을 받은 여러 죄수'(P0041, open set) 구성원이다",
                                    "{TRUE, FALSE} (free; open set이므로 FALSE로 고정하지 않음)",
                                    "PR0581|PR0582 CONTRADICTORY_IF_OPEN_SET_MEMBER"),
}

# theft hard-exclusion re-audit: (pair, a, b) -> criteria dict and verdict
NEG_THEFT = ("EC0022", "EC0046")
THEFT_HARD_TARGETS = {
    "EC0050": "구순이 '도적을 만났다'고 함(=도둑맞음으로 읽음, 해석 검토 필요)",
    "EC0070": "나복: 도적이 돈과 물품을 훔침",
    "EC0131": "홍대협: 약간의 도난이 실제였음",
    "EC0132": "홍대협: 도난이 좀도둑 수준이었음(도난 발생을 전제)",
    "EC0143": "정조(6/13): 도난이 실제로 있었음",
}
THEFT_NOT_CONSTRAINT = {
    "EC0066": "나복: 도적이 들어옴 — 침입은 '도난 없음'과 같은 의미 층위가 아님(침입했으나 훔치지 않은 세계를 논리적으로 배제할 수 없음)",
    "EC0067": "나복: 도적 30여 명 — 인원 서술은 '도난 없음'과 직접 모순되지 않음",
    "EC0068": "나복: 횃불을 들고 들어옴 — 침입 방식 서술은 '도난 없음'과 직접 모순되지 않음",
}
REVIEW_THEFT = {"EC0050", "EC0132"}

# relative temporal constraints: (claim, earlier, later, referent var, referent text, same-parent note)
TEMPORAL_REL = [
    ("EC0008", "EC0004", "EC0007", "REF_EC0008_DETENTION__EC0004", "EC0008의 '구금' = EC0004(같은 기록 SRC2_001, 다른 proposition)",
     "사망(EC0007)은 같은 부모 P0006"),
    ("EC0008", "EC0005", "EC0007", "REF_EC0008_INVESTIGATION__EC0005", "EC0008의 '조사' = EC0005(같은 기록 SRC2_001, 다른 proposition)",
     "사망(EC0007)은 같은 부모 P0006"),
    ("EC0040", "EC0036", "EC0039", "REF_EC0040_KIMDEATH__EC0036", "EC0040의 '김명신이 죽은 뒤'의 사망 = EC0036(같은 기록 SRC2_002)",
     "아내 사망(EC0039)은 같은 부모 P0026"),
    ("EC0073", "EC0072", "EC0073", "REF_EC0073_THEN__EC0072", "EC0073의 '그 뒤' = EC0072의 편지 힐책(같은 화자 명업, 같은 기록)", ""),
    ("EC0103", "EC0103", "EC0104", "REF_EC0103_ARREST__EC0104", "EC0103의 '자미덕 체포' = EC0104(같은 화자 자미덕, 같은 기록)",
     "재돌이 아산에 있던 상태가 체포 전"),
    ("EC0106", "EC0105", "EC0106", "REF_EC0106_INTERROGATION__EC0105", "EC0106의 '신문' = EC0105(같은 화자 자미덕, 같은 기록)", ""),
    ("EC0107", "EC0106", "EC0107", "REF_EC0107_AFTER__EC0106", "EC0107의 '그 후' = EC0106의 구류 이후(같은 화자 자미덕, 같은 기록)", ""),
]

# same-occurrence consistency: pairs whose predicates name different acts
DIFFERENT_ACTS = {
    ("EC0107", "EC0111"): "방으로 불러들임 vs 떡과 밥을 줌 — 다른 행위",
    ("EC0119", "EC0120"): "방안으로 부름 vs 남은 밥을 줌 — 다른 행위(같은 발화의 구성요소)",
    ("EC0107", "EC0120"): "방으로 불러들임 vs 남은 밥을 줌 — 다른 행위",
    ("EC0111", "EC0119"): "떡과 밥을 줌 vs 방안으로 부름 — 다른 행위",
}

log = logging.getLogger("v2_world_constraints")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def table_digest(con, table):
    cols = [c[0] for c in con.execute(f"DESCRIBE {table}").fetchall()]
    rows = con.execute(f"SELECT * FROM {table} ORDER BY ALL").fetchall()
    return hashlib.sha256(repr((cols, rows)).encode("utf-8")).hexdigest()


def fetch(con, sql):
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    return [{c: ("" if v is None else v) for c, v in zip(cols, row)} for row in cur.fetchall()]


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(LOG_DIR / "v2_world_constraints.log", mode="w", encoding="utf-8"),
                                  logging.StreamHandler(sys.stdout)])
    checks = []

    def check(cid, desc, ok, detail="", fail="ERROR"):
        checks.append([cid, desc, "PASS" if ok else fail, detail])
        if not ok:
            log.error("%s %s: %s", cid, desc, detail)

    expected_sha = {}
    for line in SHA_PATH.read_text(encoding="utf-8").splitlines():
        h, fn = line.split("  ", 1)
        expected_sha[fn] = h
    if not all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items()):
        log.error("Raw CSV differs from recorded SHA-256; stopping")
        sys.exit(1)

    con = duckdb.connect(str(DB_PATH))
    digests_before = {t: table_digest(con, t) for t in PROTECTED_TABLES}
    cands = {c["event_candidate_id"]: c for c in fetch(con, """
        SELECT c.*, s.speaker, s.speaker_chain, s.support_role
        FROM historical_event_candidates c JOIN event_candidate_support s USING (event_candidate_id)""")}
    pairs = fetch(con, "SELECT * FROM same_event_review ORDER BY pair_id")
    pair_by_key = {(p["candidate_a"], p["candidate_b"]): p for p in pairs}
    pair_ids = {p["pair_id"] for p in pairs}
    er = fetch(con, "SELECT * FROM entity_resolution_candidates")
    open_sets = {s["set_id"]: s for s in fetch(con, "SELECT * FROM open_set_normalized")}

    def pid(a, b):
        return pair_by_key[tuple(sorted((a, b)))]["pair_id"]

    # ---------------- variables
    variables = {}

    def var(vid, vtype, ref, desc, domain, basis, notes=""):
        assert vid not in variables, vid
        variables[vid] = [vid, vtype, ref, desc, domain, basis, notes]

    for ec, c in sorted(cands.items()):
        var(f"ATT_{ec}", "ATTESTATION_FACT", ec,
            f"{c['speaker_chain']}의 진술/기록이 존재한다: {c['subject_surface']} | {c['predicate']} ({c['polarity']})",
            "{TRUE} (source-fixed)", f"{c['origin_atomic_prop_id']} / {c['support_role']}",
            "기록의 존재만 고정. 내용의 참거짓은 E_ 변수.")
    for ec, c in sorted(cands.items()):
        if c["polarity"] == "DOUBTED":
            desc = (f"{c['speaker']}의 신빙성 판단이 타당하다: '{c['subject_surface']} {c['predicate']}'는 설명이 이치에 맞지 않음 "
                    "(발생 부정으로 읽지 않음)")
        elif c["polarity"] == "NEGATED":
            desc = f"주장 내용이 참이다: {c['subject_surface']} | {c['predicate']} — 하지 않았다/없었다 (NEGATED)"
        else:
            desc = f"주장 내용이 참이다: {c['subject_surface']} | {c['predicate']}"
        var(f"E_{ec}", "EVENT_TRUTH", ec, desc, "{TRUE, FALSE}", f"{c['epistemic_status']} via {c['speaker_chain']}",
            "DENIED/OFFICIAL/ROYAL 판단은 evidence이며 값을 고정하지 않음." if c["epistemic_status"] != "ORDERED"
            else "ORDERED: 명령 행위 자체(집행 아님).")
    er_status = {(e["surface_form"].split("(")[0], e["candidate_entity"].split("(")[0], e["source_prop_ids"]): e
                 for e in er}
    for sf, cand, scope, vid in ID_VARS:
        e = er_status[(sf, cand, scope)]
        var(vid, "IDENTITY", e["surface_form"], f"'{e['surface_form']}'와 '{e['candidate_entity']}'가 같은 인물/집단이다",
            "{TRUE, FALSE}", f"output/08 {e['resolution_status']} ({e['confidence']}); scope {scope}",
            "DIRECT라도 값은 고정하지 않음(가설 변수).")
    for vid, sf, cand, basis in EXTRA_ID_VARS:
        var(vid, "IDENTITY", sf, f"'{sf}'와 '{cand}'가 같은 인물이다", "{TRUE, FALSE}", basis)
    for vid, (vtype, ref, desc, domain, basis) in INTERP_VARS.items():
        var(vid, vtype, ref, desc, domain, basis)

    # same-occurrence variables: closure of each component of SAME candidate pairs
    so_pairs = [(p["candidate_a"], p["candidate_b"], p["pair_id"]) for p in pairs
                if p["primary_relation"] == "SAME_OCCURRENCE_CANDIDATE"]
    cond_so = [(p["candidate_a"], p["candidate_b"], p["pair_id"], p["entity_identity_dependency"]) for p in pairs
               if p["conditional_relation"] == "SAME_OCCURRENCE_IF_IDENTITY_HOLDS"]
    adj = {}
    for a, b, *_ in so_pairs + cond_so:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    components, seen = [], set()
    for n in sorted(adj):
        if n in seen:
            continue
        stack, comp = [n], set()
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x)
            stack.extend(adj[x] - comp)
        seen |= comp
        components.append(sorted(comp))
    so_basis = {tuple(sorted((a, b))): f"{p} SAME_OCCURRENCE_CANDIDATE" for a, b, p in so_pairs}
    so_basis.update({tuple(sorted((a, b))): f"{p} SAME_OCCURRENCE_IF_IDENTITY_HOLDS" for a, b, p, _ in cond_so})
    for comp in components:
        for a, b in itertools.combinations(comp, 2):
            basis = so_basis.get((a, b), "transitive closure of component " + "|".join(comp))
            var(same_var(a, b), "OCCURRENCE_IDENTITY", f"{a}|{b}",
                f"{a}와 {b}가 같은 역사적 occurrence를 가리킨다", "{TRUE, FALSE}", basis,
                "symmetric by construction (a<b); reflexive by definition")

    for claim, earlier, later, ref, text, _ in TEMPORAL_REL:
        var(ref, "REFERENT_IDENTITY", f"{claim}|{earlier if earlier != claim else later}", text, "{TRUE, FALSE}",
            f"{claim} relative_time_text")
    time_ecs = sorted({ec for ec, c in cands.items() if c["occurrence_lunar_text"] and c["occurrence_precision"] != "RELATIVE_ONLY"}
                      | {x for t in TEMPORAL_REL for x in (t[1], t[2])})
    for ec in time_ecs:
        var(f"T_{ec}", "TIME", ec, f"{ec}가 가리키는 사건·상태의 발생(시작) 시점", "lunar time point 1793 (ordinal)",
            cands[ec]["occurrence_lunar_text"] or "explicit date 없음", "다른 source의 날짜로 채우지 않음")

    # ---------------- constraints
    constraints = []

    def con_(ctype, antecedent, formula, kind, pairs_=(), dep_id="", dep_same="", dep_causal="", dep_interp="",
             reason="", review=False, tag=""):
        cid = f"LC{len(constraints) + 1:04d}"
        constraints.append(dict(
            constraint_id=cid, constraint_type=ctype, antecedent=render(antecedent) if antecedent else "",
            consequent_or_formula=render(formula) if formula else "", hard_or_conditional=kind,
            source_pair_ids="|".join(pairs_), depends_on_identity=dep_id, depends_on_same_occurrence=dep_same,
            depends_on_causal_level=dep_causal, depends_on_interpretation=dep_interp, reason=reason,
            manual_review_required="YES" if review else "NO", _formula=(Imp(antecedent, formula) if antecedent else formula),
            _tag=tag))
        return cid

    # 1. attested acts (orders, ministerial requests)
    for ec, c in sorted(cands.items()):
        if c["epistemic_status"] == "ORDERED" or (c["epistemic_status"] == "DIRECT_ACTION_RECORDED" and c["event_type"] == "REQUEST"):
            con_("ATTESTED_ACT_ANCHOR", None, Eq(f"E_{ec}", True), HARD,
                 reason=f"{c['epistemic_status']}: 기록이 곧 명령/건의 행위({c['predicate']}). 집행(EXECUTION)은 만들지 않음.",
                 tag="anchor")

    # 2. theft hard mutual exclusions (re-audited)
    audit = []
    for neg in NEG_THEFT:
        for tgt, desc in THEFT_HARD_TARGETS.items():
            p = pid(neg, tgt)
            cid = con_("MUTUAL_EXCLUSION", None, Not(And(V(f"E_{neg}"), V(f"E_{tgt}"))), HARD, [p],
                       reason=f"같은 구순 사건 도난에 대해 '도난이 없었다'({neg}, {cands[neg]['speaker']}) vs {desc}.",
                       review=tgt in REVIEW_THEFT, tag="theft_hard")
            audit.append(["CONSTRAINT", cid, p, "YES (구순이 정소한 도난, 사건 정의로 같은 대상)",
                          "YES (같은 도난 발생 여부)", "YES (판단 쪽 날짜 없음, 같은 사건 기준)",
                          "YES" if tgt not in REVIEW_THEFT else "YES, 해석 검토 필요", "YES", "JUSTIFIED_HARD",
                          "'방향' 표현(EC0022/EC0046)은 판단 강도 문제이며 내용 층위는 같음."])
        for tgt, desc in THEFT_NOT_CONSTRAINT.items():
            p = pid(neg, tgt)
            cid = con_("MUTUAL_EXCLUSION", None, None, NOTC, [p], reason=desc, tag="theft_downgrade")
            audit.append(["CONSTRAINT", cid, p, "YES", "NO (침입·인원·횃불 vs 도난 발생)", "YES", "NO", "YES",
                          "DOWNGRADED_FROM_PAIR_CONTRADICTION", "같은 발화의 절도 서술(EC0070)이 모순 제약을 담당."])

    # 3. downgraded contradictions -> conditional on interpretation
    cid = con_("CONDITIONAL_CONTRADICTION", Eq("SENSE_EC0132_EXCLUDES_LARGE_BAND", True),
               Not(And(V("E_EC0067"), V("E_EC0132"))), COND, [pid("EC0067", "EC0132")],
               dep_interp="SENSE_EC0132_EXCLUDES_LARGE_BAND",
               reason="'좀도둑 수준'이 무리의 규모까지 배제하는 뜻일 때만 '도적 30여 명'과 모순.", review=True)
    audit.append(["CONSTRAINT", cid, pid("EC0067", "EC0132"), "YES", "YES", "YES", "CONDITIONAL (규모 평가의 의미)", "YES",
                  "DOWNGRADED_TO_CONDITIONAL", ""])
    for tgt in ("EC0047", "EC0148"):
        cid = con_("CONDITIONAL_CONTRADICTION", Eq("SENSE_EC0031", "COINED_TERM"),
                   Not(And(V("E_EC0031"), V(f"E_{tgt}"))), COND, [pid("EC0031", tgt)], dep_interp="SENSE_EC0031",
                   reason="'만들었다'가 호칭을 새로 지어냈다는 뜻이면 예전 도적이 쓰던 말이라는 진술과 모순. 사건 속 사용을 꾸몄다는 뜻이면 양립.",
                   review=True)
        audit.append(["CONSTRAINT", cid, pid("EC0031", tgt), "YES", "YES", "YES", "CONDITIONAL ('만들었다'의 의미)", "YES",
                      "DOWNGRADED_TO_CONDITIONAL", ""])
    cid = con_("CONDITIONAL_CONTRADICTION", And(Eq("SENSE_EC0149", "FACTUAL_NEGATION"), Eq("SENSE_EC0031", "COINED_TERM")),
               Not(And(V("E_EC0031"), V("E_EC0149"))), COND, [pid("EC0031", "EC0149")],
               dep_interp="SENSE_EC0149|SENSE_EC0031",
               reason="'죄를 면함'이 사실 부정이고 '만들었다'가 창작일 때만 모순. 법적 혐의 불인정이면 양립.", review=True)
    audit.append(["CONSTRAINT", cid, pid("EC0031", "EC0149"), "YES", "YES", "YES",
                  "CONDITIONAL (면함=사실 부정/법적 불인정)", "YES", "DOWNGRADED_TO_CONDITIONAL", ""])

    # 4. pair-stage conditional relations
    for p in pairs:
        cond = p["conditional_relation"]
        a, b = p["candidate_a"], p["candidate_b"]
        if not cond:
            continue
        me = Not(And(V(f"E_{a}"), V(f"E_{b}")))
        if cond == "CONFLICT_IF_IDENTITY_HOLDS":
            idv = ID_OF_DEP[p["entity_identity_dependency"]]
            cid = con_("CONDITIONAL_CONTRADICTION", V(idv), me, COND, [p["pair_id"]], dep_id=idv,
                       reason=f"{idv}가 참인 세계에서만 두 claim 내용이 함께 참일 수 없음. 거짓인 세계에서는 적용하지 않음.",
                       review=True)
        elif cond == "SAME_OCCURRENCE_IF_IDENTITY_HOLDS":
            idv = ID_OF_DEP[p["entity_identity_dependency"]]
            cid = con_("IMPLICATION", V(same_var(a, b)), V(idv), COND, [p["pair_id"]], dep_id=idv,
                       dep_same=same_var(a, b), reason="같은 occurrence라면 행위자가 같은 인물이어야 함.", review=True)
        elif cond == "CONTRADICTORY_IF_FULL_FABRICATION":
            fab = a if a in ("EC0012", "EC0030") else b
            cid = con_("CONDITIONAL_CONTRADICTION", Eq(f"FABSCOPE_{fab}", "FULL_FABRICATION"), me, COND, [p["pair_id"]],
                       dep_interp=f"FABSCOPE_{fab}",
                       reason="'꾸밈'이 도난 전체의 조작일 때만 도난·침입 claim과 모순. 과장이면 양립.", review=True)
        elif cond == "CONTRADICTORY_IF_SAME_CAUSAL_LEVEL":
            cid = con_("CONDITIONAL_CONTRADICTION", Eq("CAUSELEVEL_EC0038", "DIRECT_CAUSE"), me, COND, [p["pair_id"]],
                       dep_causal="CAUSELEVEL_EC0038",
                       reason="'죄안 때문'이 직접 사인 주장일 때만 질병·전염병 직접 사인과 모순. 책임 귀속이면 양립.", review=True)
        elif cond == "CONTRADICTORY_IF_OPEN_SET_MEMBER":
            grp = a if a in ("EC0009", "EC0056") else b
            mv = "MEMBER_KIMMYEONGSIN_IN_OS01" if grp == "EC0009" else "MEMBER_KIMMYEONGSIN_IN_OS07"
            cid = con_("CONDITIONAL_CONTRADICTION", V(mv), me, COND, [p["pair_id"]], dep_interp=mv,
                       reason="김명신이 형벌 받은 open set의 구성원인 세계에서만 적용. 구성원 여부는 고정하지 않음(비구성원 추론 없음).",
                       review=True)
        elif cond == "CONTRADICTORY_IF_JOSA_EQUALS_SINMUN":
            cid = con_("CONDITIONAL_CONTRADICTION", V("TERM_EC0005_JOSA_INCLUDES_SINMUN"), me, COND, [p["pair_id"]],
                       dep_interp="TERM_EC0005_JOSA_INCLUDES_SINMUN",
                       reason="'조사함'이 신문을 포함하는 뜻일 때만 '평범한 신문도 받지 않음'과 모순.", review=True)
        elif cond == "CONFLICT_IF_SAME_LIST":
            cid = con_("CONDITIONAL_CONTRADICTION", V("SAMELIST_EC0052_EC0118"), me, COND, [p["pair_id"]],
                       dep_interp="SAMELIST_EC0052_EC0118",
                       reason="두 명단이 같은 명단일 때만 '구순이 써 줌'과 '직접 염탐'이 충돌.", review=True)
        else:
            raise ValueError(cond)
        audit.append(["CONSTRAINT", cid, p["pair_id"], "CONDITIONAL", "CONDITIONAL", "N/A", "CONDITIONAL",
                      "NO" if "IDENTITY" in cond else "YES", "JUSTIFIED_CONDITIONAL", cond])

    # 5. 따라 죽음 vs 전염병 (REVIEW pair, needs interpretation variable)
    cid = con_("CONDITIONAL_CONTRADICTION", Eq("SENSE_EC0040", "CAUSAL_FOLLOWING_EXCLUDING_EPIDEMIC"),
               Not(And(V("E_EC0040"), V("E_EC0145"))), COND, [pid("EC0040", "EC0145")], dep_interp="SENSE_EC0040",
               reason="'따라 죽음'이 전염병이 아닌 원인으로 뒤따라 죽었다는 뜻일 때만 정조의 '처가 전염병으로 죽음'과 모순.",
               review=True)
    audit.append(["CONSTRAINT", cid, pid("EC0040", "EC0145"), "YES", "YES", "N/A", "CONDITIONAL ('따라'의 의미)", "YES",
                  "JUSTIFIED_CONDITIONAL", "pair stage REVIEW"])

    # 6. same-occurrence structure
    for comp in components:
        for x, y, z in itertools.permutations(comp, 3):
            if x < z:  # each (premise pair set, conclusion) once
                cid = con_("TRANSITIVITY", And(V(same_var(x, y)), V(same_var(y, z))), V(same_var(x, z)), HARD,
                           dep_same=f"{same_var(x, y)}|{same_var(y, z)}",
                           reason="world 안에서 채택된 same-occurrence는 동치관계여야 함.", tag="transitivity")
    for (a, b), why in DIFFERENT_ACTS.items():
        con_("SAME_CONSISTENCY", None, Not(V(same_var(a, b))), HARD, [p for p in [pair_by_key.get(tuple(sorted((a, b))), {}).get("pair_id")] if p],
             dep_same=same_var(a, b), reason=f"양립 불가능한 속성: {why}. 같은 occurrence일 수 없음.", review=True,
             tag="same_consistency")
    for comp in components:
        for a, b in itertools.combinations(comp, 2):
            ca, cb = cands[a], cands[b]
            da, db = ca["occurrence_lunar_text"], cb["occurrence_lunar_text"]
            pa, pb = ca["historical_place"], cb["historical_place"]
            bad = []
            if da and db and da != db:
                bad.append(f"명시 날짜 {da} vs {db}")
            if pa and pb and pa not in pb and pb not in pa:
                bad.append(f"장소 {pa} vs {pb}")
            if ca["event_type"] != cb["event_type"]:
                bad.append(f"event_type {ca['event_type']} vs {cb['event_type']}")
            if ca["polarity"] != "AFFIRMED" or cb["polarity"] != "AFFIRMED":
                bad.append("polarity")
            if bad and (a, b) not in DIFFERENT_ACTS:
                con_("SAME_CONSISTENCY", None, Not(V(same_var(a, b))), HARD, dep_same=same_var(a, b),
                     reason="양립 불가능한 속성: " + "; ".join(bad), tag="same_consistency")
            if ca["subject_surface"] == cb["subject_surface"] and ca["predicate"] == cb["predicate"]:
                con_("IMPLICATION", V(same_var(a, b)), Iff(V(f"E_{a}"), V(f"E_{b}")), COND,
                     [p for p in [pair_by_key.get((a, b), {}).get("pair_id")] if p], dep_same=same_var(a, b),
                     reason="같은 occurrence이고 서술 내용이 같으면 두 claim의 참거짓이 같아야 함.")
    con_("SAME_CONSISTENCY", None, None, ANNO, dep_same="all SAME_* without exclusion",
         reason="나머지 SAME 가설은 날짜·장소·주체·유형 충돌이 없어 열어 둠. 세부 서술이 다르면 참거짓 동치는 강제하지 않음.")

    # 7. identity structure
    for x, y, z in [("ID_HANBIJANG__HANGA", "ID_HANGA__HANJAEUK", "ID_HANBIJANG__HANJAEUK"),
                    ("ID_HANBIJANG__HANJAEUK", "ID_HANGA__HANJAEUK", "ID_HANBIJANG__HANGA"),
                    ("ID_HANBIJANG__HANJAEUK", "ID_HANBIJANG__HANGA", "ID_HANGA__HANJAEUK")]:
        con_("TRANSITIVITY", And(V(x), V(y)), V(z), HARD, dep_id=f"{x}|{y}|{z}",
             reason="인물 동일성은 동치관계: 한 비장·한가·한재욱 중 두 동일성이 참이면 세 번째도 참.", tag="id_transitivity")
    con_("MUTUAL_EXCLUSION", None, Not(And(V("ID_HAGEUP_BOJOJA__HANJAEUK"), V("ID_HAGEUP_BOJOJA__YUJEHUI"))), HARD,
         dep_id="ID_HAGEUP_BOJOJA__HANJAEUK|ID_HAGEUP_BOJOJA__YUJEHUI",
         reason="한재욱과 유제희는 같은 진술(P0086)에 서로 다른 인물로 나오므로 하급 보조자가 둘 다일 수 없음.")

    # 8. temporal
    for ec in time_ecs:
        c = cands[ec]
        if c["occurrence_lunar_text"] and c["occurrence_precision"] != "RELATIVE_ONLY":
            con_("TEMPORAL_ANCHOR", V(f"E_{ec}"), In(f"T_{ec}", c["occurrence_lunar_text"]), HARD,
                 reason=f"candidate 자신의 명시 시간({c['occurrence_precision']}). 다른 source 날짜를 쓰지 않음.",
                 review=ec == "EC0065", tag="temporal")
    for claim, earlier, later, ref, text, note in TEMPORAL_REL:
        con_("TEMPORAL_ORDER", And(V(f"E_{claim}"), V(ref)), Lt(f"T_{earlier}", f"T_{later}"), COND, dep_same=ref,
             reason=f"{claim}의 상대 시간 표현. {text}. {note}".strip(), review=True, tag="temporal")
    con_("TEMPORAL_ORDER", None, None, NOTC,
         reason="EC0055 '체포·구금 뒤': 같은 기록(SRC2_005)에 체포·구금 candidate가 없어 referent를 다른 source에서 가져오지 않음(문자열로만 보존).")
    con_("TEMPORAL_ORDER", None, None, NOTC,
         reason="EC0153 '형장 친 뒤': 명령 내용 안의 순서이며 집행 기록이 아니므로 world 시간 제약이 아님.")

    # 9. not-a-constraint / annotation records
    doubted = {ec for ec, c in cands.items() if c["polarity"] == "DOUBTED"}
    for p in pairs:
        a, b = p["candidate_a"], p["candidate_b"]
        if (a in doubted or b in doubted):
            con_("MUTUAL_EXCLUSION", None, None, NOTC, [p["pair_id"]],
                 reason="DOUBTED(설명의 신빙성 부정)는 FALSE가 아니므로 세계를 제거하지 않음.", tag="doubted")
    con_("MUTUAL_EXCLUSION", None, None, NOTC, [pid("EC0048", "EC0049")],
         reason="같은 날 조사 명령과 안핵어사 차하: 같은 임명 행위인지 미정(REVIEW). 둘 다 ORDERED로 고정될 뿐 서로 배제하지 않음.")
    for sid in ("OS13", "OS14"):
        s = open_sets[sid]
        con_("MUTUAL_EXCLUSION", None, None, NOTC,
             reason=f"{sid}({s['parent_prop_id']}) open set: 명시 구성원({s['explicit_members']})만 구성원으로 사용. "
                    "명시되지 않은 인물을 비구성원으로 만드는 제약은 만들지 않음(예: 이집거가 유제희 명단에 명시되지 않음).",
             tag="open_set")
    for p in pairs:
        if "COMPATIBLE_CLAIMS" in (p["primary_relation"], p["secondary_relation"]):
            con_("COMPATIBILITY", None, None, ANNO, [p["pair_id"]],
                 reason=f"{p['candidate_a']}와 {p['candidate_b']}는 동시에 참이어도 모순 없음(제거 제약 아님).", tag="compat")

    # ---------------- validation
    c_hard = [c for c in constraints if c["hard_or_conditional"] == HARD]
    c_cond = [c for c in constraints if c["hard_or_conditional"] == COND]
    active = c_hard + c_cond

    def fixed_e_vars():
        out = {}
        for c in active:
            f = c["_formula"]
            if f[0] == "eq" and f[1].startswith("E_"):
                out[f[1]] = f[2]
            if f[0] == "not" and f[1][0] == "var" and f[1][1].startswith("E_"):
                out[f[1][1]] = False
            if f[0] == "var" and f[1].startswith("E_"):
                out[f[1]] = True
        return out

    fixed = fixed_e_vars()
    denied_fixed = [v for v in fixed if cands[v[2:]]["epistemic_status"] == "DENIED"]
    check("W01", "DENIED를 historical FALSE로 고정한 사례 0", not denied_fixed, "|".join(denied_fixed))
    royal_fixed = [v for v in fixed if cands[v[2:]]["epistemic_status"] in ("ROYAL_FINDING", "OFFICIAL_FINDING")]
    check("W02", "ROYAL_FINDING/OFFICIAL_FINDING을 historical TRUE로 고정한 사례 0", not royal_fixed, "|".join(royal_fixed))
    anchor_bad = [v for v in fixed if cands[v[2:]]["epistemic_status"] not in ("ORDERED", "DIRECT_ACTION_RECORDED")]
    check("W03", "값이 고정된 E 변수는 ORDERED/기록된 건의 행위뿐", not anchor_bad, f"fixed={len(fixed)}")
    doubt_bad = [c["constraint_id"] for c in active if any(f"E_{d}" in variables_of(c["_formula"]) for d in doubted)]
    check("W04", "DOUBTED를 FALSE로 변환하거나 제약에 사용한 사례 0", not doubt_bad, "|".join(doubt_bad))
    member_bad = [c["constraint_id"] for c in active
                  if any(v.startswith("MEMBER_") for v in variables_of(c["_formula"]))
                  and (c["_formula"][0] == "not" or c["hard_or_conditional"] == HARD)]
    member_bad += [v for v in variables if "NONMEMBER" in v or "NOT_MEMBER" in v]
    check("W05", "open-set nonmembership를 생성한 사례 0", not member_bad, "|".join(member_bad))
    id_pairs = {p["pair_id"] for p in pairs if p["conditional_relation"] in ("CONFLICT_IF_IDENTITY_HOLDS",
                                                                             "SAME_OCCURRENCE_IF_IDENTITY_HOLDS")}
    def touches_claims(c):
        return any(v.startswith("E_") for v in variables_of(c["_formula"])) if c["_formula"] else False

    # ¬SAME consistency rules from these pairs hold regardless of identity and touch no claim content.
    id_bad = [c["constraint_id"] for c in constraints if set(c["source_pair_ids"].split("|")) & id_pairs
              and c["hard_or_conditional"] in (HARD, COND) and touches_claims(c)
              and (c["hard_or_conditional"] != COND or not c["depends_on_identity"])]
    id_bad += [c["constraint_id"] for c in constraints if set(c["source_pair_ids"].split("|")) & id_pairs
               and c["constraint_type"] == "IMPLICATION" and not c["depends_on_identity"]]
    nondirect = {p["pair_id"] for p in pairs if any(t in p["entity_identity_dependency"]
                                                    for t in ("(CANDIDATE)", "(UNRESOLVED)", "근거 없음"))}
    id_bad += [c["constraint_id"] for c in c_hard if set(c["source_pair_ids"].split("|")) & nondirect and touches_claims(c)]
    check("W06", "conditional identity conflict를 unconditional로 만든 사례 0", not id_bad, "|".join(id_bad))
    cause_ecs = {ec for ec, c in cands.items() if c["event_type"] == "CAUSE_ATTRIBUTION"}
    cause_bad = [c["constraint_id"] for c in c_hard
                 if len({v[2:] for v in variables_of(c["_formula"]) if v.startswith("E_")} & cause_ecs) >= 2]
    check("W07", "direct/indirect cause를 자동 contradiction으로 만든 사례 0", not cause_bad, "|".join(cause_bad))
    same_names = [v for v in variables if v.startswith("SAME_")]
    sym_bad = [v for v in same_names if v.split("_")[1] >= v.split("_")[2]]
    used_same = set().union(*(variables_of(c["_formula"]) for c in active)) if active else set()
    sym_bad += [v for v in used_same if v.startswith("SAME_") and v not in variables]
    check("W08", "SAME occurrence symmetry 위반 0 (정규 이름 a<b, 역순 변수 없음)", not sym_bad, "|".join(sym_bad))
    trans_bad = []
    trans_set = {(c["antecedent"], c["consequent_or_formula"]) for c in constraints if c["_tag"] == "transitivity"}
    for comp in components:
        for a, b in itertools.combinations(comp, 2):
            if same_var(a, b) not in variables:
                trans_bad.append(f"missing {same_var(a, b)}")
        for x, y, z in itertools.permutations(comp, 3):
            key = (render(And(V(same_var(x, y)), V(same_var(y, z)))), render(V(same_var(x, z))))
            key2 = (render(And(V(same_var(z, y)), V(same_var(y, x)))), render(V(same_var(z, x))))
            if key not in trans_set and key2 not in trans_set:
                trans_bad.append(f"{x}-{y}-{z}")
    check("W09", "SAME occurrence transitivity 위반 가능 구조 0 (component 폐포 + 모든 삼각 규칙)", not trans_bad,
          "|".join(trans_bad[:10]))
    ref_bad = []
    for c in constraints:
        for p in filter(None, c["source_pair_ids"].split("|")):
            if p not in pair_ids:
                ref_bad.append(f"{c['constraint_id']}:{p}")
        for v in variables_of(c["_formula"]) if c["_formula"] else set():
            if v not in variables:
                ref_bad.append(f"{c['constraint_id']}:{v}")
    ref_bad += [v[0] for v in variables.values() if v[1] in ("ATTESTATION_FACT", "EVENT_TRUTH", "TIME") and v[2] not in cands]
    check("W10", "존재하지 않는 candidate/pair/variable 참조 0", not ref_bad, "|".join(ref_bad[:10]))
    exec_bad = [v for v in variables if "EXEC" in v] + [c["constraint_id"] for c in constraints if "EXECUTION" in c["constraint_type"]]
    check("W11", "ORDER → EXECUTION 추론 0", not exec_bad, "|".join(exec_bad))
    ct_pairs = {p["pair_id"] for p in pairs if "CONTRADICTORY_CLAIMS" in (p["primary_relation"], p["secondary_relation"])}
    cond_pairs = {p["pair_id"] for p in pairs if p["conditional_relation"]}
    covered = set()
    for c in constraints:
        covered |= set(filter(None, c["source_pair_ids"].split("|")))
    check("W12", "pair-stage contradiction 20건·conditional 36건이 모두 제약/비제약으로 처리됨",
          ct_pairs <= covered and cond_pairs <= covered and len(ct_pairs) == 20 and len(cond_pairs) == 36,
          f"ct={len(ct_pairs)} cond={len(cond_pairs)} missing={sorted((ct_pairs | cond_pairs) - covered)}")
    so_missing = [f"{a}-{b}" for a, b, _ in so_pairs if same_var(a, b) not in variables]
    check("W13", "SAME_OCCURRENCE_CANDIDATE 11건 모두 SAME 가설 변수로 표현(등호 아님)",
          not so_missing and len(so_pairs) == 11, "|".join(so_missing))

    # ---------------- special tests (local truth-table checks)
    def violated(asg):
        out = []
        for c in active:
            if not c["_formula"]:
                continue
            if variables_of(c["_formula"]) <= set(asg) and evaluate(c["_formula"], asg) is False:
                out.append(c["constraint_id"])
        return out

    examples = []

    def example(topic, sentence, asg, expect, simple):
        v = violated(asg)
        status = "IMPOSSIBLE" if v else "ALLOWED"
        examples.append([f"WX{len(examples) + 1:03d}", topic, sentence,
                         "; ".join(f"{k}={'TRUE' if x is True else 'FALSE' if x is False else x}" for k, x in asg.items()),
                         status, "|".join(v), simple])
        return status == expect

    tests = []
    tests.append(example("THEFT_REALITY", "이조원의 '화적 설명은 이치에 맞지 않는다'가 타당하고, 홍대협의 '약간의 도난은 있었다'도 참",
                         {"E_EC0024": True, "E_EC0131": True}, "ALLOWED",
                         "큰 도적떼 이야기가 의심스럽다는 말과 조금 도둑맞았다는 말은 함께 맞을 수 있어요."))
    tests.append(example("THEFT_REALITY", "정조(5/12)의 '도난이 없었다'와 정조(6/13)의 '도난이 있었다'가 둘 다 참",
                         {"E_EC0022": True, "E_EC0143": True}, "IMPOSSIBLE",
                         "같은 도둑 사건이 '있었다'와 '없었다'가 동시에 맞을 수는 없어요. 이런 세계는 빠져요."))
    tests.append(example("THEFT_REALITY", "정조(5/12)의 판단은 틀렸고(도난이 있었음) 6/13 판단은 맞음",
                         {"E_EC0022": False, "E_EC0143": True}, "ALLOWED",
                         "두 말 중 하나가 틀렸다고 보면 문제없어요. 두 기록이 있었다는 사실 자체는 그대로예요."))
    tests.append(example("THEFT_REALITY", "'도난 자체가 없었다'(EC0022)가 참이고 나복의 '도적이 들어왔다'(EC0066)도 참",
                         {"E_EC0022": True, "E_EC0066": True}, "ALLOWED",
                         "도둑이 들어왔지만 아무것도 훔치지 않았을 수도 있어서, 이것만으로는 세계를 지우지 않아요."))
    tests.append(example("THEFT_REALITY", "'도난이 없었다'(EC0046)가 참이고 나복의 '도적이 돈과 물품을 훔쳤다'(EC0070)도 참",
                         {"E_EC0046": True, "E_EC0070": True}, "IMPOSSIBLE",
                         "훔쳐 갔는데 도난이 없었다는 건 말이 안 되니까 이런 세계는 빠져요."))
    tests.append(example("DEATH_CAUSE", "직접 사인은 전염병(정조)이고, 이조원의 '죄안 때문'은 책임을 묻는 말(간접 원인)",
                         {"E_EC0144": True, "E_EC0038": True, "CAUSELEVEL_EC0038": "RESPONSIBILITY_ATTRIBUTION"}, "ALLOWED",
                         "병 때문에 죽었지만, 억울하게 갇힌 탓이라는 말도 함께 맞을 수 있어요."))
    tests.append(example("DEATH_CAUSE", "이조원의 '죄안 때문'이 직접 사인이라는 뜻인데, 직접 사인이 전염병이라는 정조 판단도 참",
                         {"E_EC0144": True, "E_EC0038": True, "CAUSELEVEL_EC0038": "DIRECT_CAUSE"}, "IMPOSSIBLE",
                         "바로 죽게 만든 원인이 두 가지로 서로 다르다고 하면 함께 맞을 수 없어서 빠져요."))
    tests.append(example("DEATH_CAUSE", "윤노동의 '병'과 정조의 '전염병'이 둘 다 참",
                         {"E_EC0054": True, "E_EC0144": True}, "ALLOWED",
                         "전염병도 병의 한 종류일 수 있으니 둘 다 맞을 수 있어요."))
    tests.append(example("COACHING", "한 비장=한재욱이 참이고, '한 비장이 거짓 발언을 지휘했다'와 '한재욱은 사주하지 않았다'가 둘 다 참",
                         {"ID_HANBIJANG__HANJAEUK": True, "E_EC0114": True, "E_EC0126": True}, "IMPOSSIBLE",
                         "같은 사람이라면 '시켰다'와 '안 시켰다'가 동시에 맞을 수 없어서 빠져요."))
    tests.append(example("COACHING", "한 비장≠한재욱이고, 두 claim이 둘 다 참",
                         {"ID_HANBIJANG__HANJAEUK": False, "E_EC0114": True, "E_EC0126": True}, "ALLOWED",
                         "다른 사람이라면 한 비장은 시키고 한재욱은 안 시켰을 수 있어요."))
    tests.append(example("COACHING", "자미덕의 진술 기록과 한재욱의 부인 기록이 둘 다 존재",
                         {"ATT_EC0114": True, "ATT_EC0126": True}, "ALLOWED",
                         "서로 다른 말을 했다는 기록은 둘 다 있을 수 있어요. 지워지는 건 내용끼리 부딪칠 때뿐이에요."))
    tests.append(example("COACHING", "한재욱이 실제로는 사주했음(부인 내용이 거짓)",
                         {"E_EC0126": False}, "ALLOWED",
                         "부인했다고 해서 정말 안 했다고 정해 두지 않아요."))
    tests.append(example("SAME_OCCURRENCE", "EC0007=EC0036, EC0036=EC0053을 고르고 EC0007≠EC0053",
                         {"SAME_EC0007_EC0036": True, "SAME_EC0036_EC0053": True, "SAME_EC0007_EC0053": False}, "IMPOSSIBLE",
                         "가=나이고 나=다라면 가=다여야 해요. 아니라고 하면 빠져요."))
    tests.append(example("SAME_OCCURRENCE", "세 김명신 사망 기록이 모두 같은 사망",
                         {"SAME_EC0007_EC0036": True, "SAME_EC0036_EC0053": True, "SAME_EC0007_EC0053": True}, "ALLOWED",
                         "셋이 모두 같은 일을 말한다고 보는 건 괜찮아요."))
    tests.append(example("SAME_OCCURRENCE", "EC0007=EC0036으로 골랐는데 한쪽 사망 claim만 참",
                         {"SAME_EC0007_EC0036": True, "E_EC0007": True, "E_EC0036": False}, "IMPOSSIBLE",
                         "같은 죽음을 말한다면 한쪽만 맞고 다른 쪽은 틀릴 수 없어요."))
    tests.append(example("SAME_OCCURRENCE", "한 비장의 '방으로 불러들임'=한재욱의 '방으로 부름', 그리고 한재욱의 '방으로 부름'=한 비장의 '떡과 밥'",
                         {"SAME_EC0107_EC0119": True, "SAME_EC0111_EC0119": True}, "IMPOSSIBLE",
                         "부른 일과 밥을 준 일은 다른 일이라 같은 일로 이을 수 없어서 빠져요."))
    tests.append(example("SAME_OCCURRENCE", "한 비장의 '방으로 불러들임'=한재욱의 '방으로 부름'인데 한 비장≠한재욱",
                         {"SAME_EC0107_EC0119": True, "ID_HANBIJANG__HANJAEUK": False}, "IMPOSSIBLE",
                         "같은 일이라고 하려면 부른 사람이 같은 사람이어야 해요."))
    tests.append(example("ORDER", "정조가 구순 신지도 정배를 명했다는 것이 거짓",
                         {"E_EC0151": False}, "IMPOSSIBLE",
                         "명령 기록 자체가 명령이라서 '명령이 없었다'는 세계는 빠져요. 실제로 섬에 도착했는지는 정하지 않아요."))
    tests.append(example("OPEN_SET", "이집거가 유제희 명단(P0087)에도 있었던 세계",
                         {}, "ALLOWED", "명단에 '등'이 붙어 있어서, 적히지 않은 사람이 빠졌다고 정하지 않아요."))
    check("W14", "특별 테스트(THEFT/DEATH/COACHING/SAME/ORDER/OPEN_SET) 기대 결과 일치", all(tests),
          f"{sum(tests)}/{len(tests)}")

    # ---------------- audit rows for structural constraints
    for c in constraints:
        if c["constraint_id"] in {a[1] for a in audit}:
            continue
        verdict = {"HARD_LOGICAL": "JUSTIFIED_HARD", "CONDITIONAL": "JUSTIFIED_CONDITIONAL",
                   "NOT_A_CONSTRAINT": "NOT_A_CONSTRAINT", "ANNOTATION": "ANNOTATION"}[c["hard_or_conditional"]]
        audit.append(["CONSTRAINT", c["constraint_id"], c["source_pair_ids"], "N/A", "N/A", "N/A", "N/A",
                      "NO" if c["depends_on_identity"] else "YES", verdict, c["constraint_type"] + ": " + c["reason"][:120]])

    # ---------------- write
    var_cols = ["variable_id", "variable_type", "referent_id", "description", "domain", "source_basis", "notes"]
    con_cols = ["constraint_id", "constraint_type", "antecedent", "consequent_or_formula", "hard_or_conditional",
                "source_pair_ids", "depends_on_identity", "depends_on_same_occurrence", "depends_on_causal_level",
                "depends_on_interpretation", "reason", "manual_review_required"]
    aud_cols = ["item_type", "constraint_id", "source_pair_ids", "same_target", "same_event", "same_time_range",
                "same_semantic_layer", "identity_independent", "verdict", "notes"]
    ex_cols = ["example_id", "topic", "world_description", "assignment", "world_status", "violated_constraints",
               "plain_explanation"]
    write_csv(OUT_DIR / "19_v2_world_variables.csv", var_cols, list(variables.values()))
    write_csv(OUT_DIR / "20_v2_logical_constraints.csv", con_cols, [[c[k] for k in con_cols] for c in constraints])
    write_csv(OUT_DIR / "21_v2_world_constraint_audit.csv", aud_cols, audit)
    write_csv(OUT_DIR / "22_v2_impossible_combination_examples.csv", ex_cols, examples)
    for table, fn in [("world_variables", "19_v2_world_variables.csv"), ("logical_constraints", "20_v2_logical_constraints.csv"),
                      ("world_constraint_audit", "21_v2_world_constraint_audit.csv"),
                      ("impossible_combination_examples", "22_v2_impossible_combination_examples.csv")]:
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv(?, header=true, all_varchar=true, "
                    f"quote='\"', escape='\"')", [str(OUT_DIR / fn)])
    digests_after = {t: table_digest(con, t) for t in PROTECTED_TABLES}
    con.close()
    changed = [t for t in PROTECTED_TABLES if digests_before[t] != digests_after[t]]
    check("W15", "raw·기존 derived table 불변", not changed, "|".join(changed))
    check("W16", "raw CSV SHA-256 불변", all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items()))
    write_csv(OUT_DIR / "23_v2_world_constraint_validation.csv", ["check_id", "description", "severity", "detail"], checks)

    vt = {}
    for v in variables.values():
        vt[v[1]] = vt.get(v[1], 0) + 1
    ct = {}
    for c in constraints:
        ct[(c["hard_or_conditional"], c["constraint_type"])] = ct.get((c["hard_or_conditional"], c["constraint_type"]), 0) + 1
    log.info("world variables: %d %s", len(variables), vt)
    log.info("hard: %d, conditional: %d, not-a-constraint: %d, annotation: %d", len(c_hard), len(c_cond),
             sum(1 for c in constraints if c["hard_or_conditional"] == NOTC),
             sum(1 for c in constraints if c["hard_or_conditional"] == ANNO))
    for k in sorted(ct):
        log.info("  %s / %s: %d", k[0], k[1], ct[k])
    me = [c for c in active if c["constraint_type"] in ("MUTUAL_EXCLUSION", "CONDITIONAL_CONTRADICTION")]
    log.info("mutual exclusion (hard %d + conditional %d)", sum(1 for c in me if c["hard_or_conditional"] == HARD),
             sum(1 for c in me if c["hard_or_conditional"] == COND))
    log.info("identity-dependent: %d", sum(1 for c in active if c["depends_on_identity"]))
    log.info("same-occurrence/referent-dependent: %d", sum(1 for c in active if c["depends_on_same_occurrence"]))
    log.info("temporal: %d", sum(1 for c in active if c["constraint_type"].startswith("TEMPORAL")))
    log.info("manual review: %d", sum(1 for c in constraints if c["manual_review_required"] == "YES"))
    n_err = sum(1 for c in checks if c[2] == "ERROR")
    log.info("validation: ERROR=%d WARNING=%d", n_err, sum(1 for c in checks if c[2] == "WARNING"))
    if n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
