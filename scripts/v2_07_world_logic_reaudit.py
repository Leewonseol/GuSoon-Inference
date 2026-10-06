#!/usr/bin/env python3
"""GuSoon v2 re-audit of the possible-world logic layer (audit only).

Re-reads output/19 (variables) and output/20 (constraints) and checks every
variable and every HARD_LOGICAL / CONDITIONAL constraint for three confusions:
  1. record exists  vs  record content is historically true
  2. same occurrence  vs  same proposition
  3. sources disagree  vs  one possible world is self-contradictory
Formulas are parsed back from their rendered text and evaluated on a few
hand-picked assignments to answer the audit questions; this is not world
enumeration.

Nothing earlier is modified: no variable or constraint is deleted or changed,
and the DuckDB file is not opened for writing.

Outputs:
  output/24_v2_world_variable_level_audit.csv
  output/25_v2_hard_constraint_reaudit.csv
  output/26_v2_conditional_constraint_reaudit.csv
  output/27_v2_world_logic_reaudit_summary.csv
  logs/v2_world_logic_reaudit.log
"""

import csv
import hashlib
import logging
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
INPUTS = ["19_v2_world_variables.csv", "20_v2_logical_constraints.csv", "21_v2_world_constraint_audit.csv",
          "22_v2_impossible_combination_examples.csv", "23_v2_world_constraint_validation.csv",
          "12_v2_historical_event_candidates.csv", "13_v2_event_candidate_support.csv",
          "16_v2_same_event_review.csv"]

VALID_HARD = "VALID_HARD_WORLD_CONSTRAINT"
VALID_COND = "VALID_CONDITIONAL_WORLD_CONSTRAINT"
EVIDENCE_ONLY = "EVIDENCE_DISAGREEMENT_ONLY"
BAD_COUPLING = "INVALID_SAME_OCCURRENCE_TRUTH_COUPLING"
OVERANCHOR = "SOURCE_AUTHORITY_OVERANCHOR"
REVIEW = "REVIEW_REQUIRED"

LEVEL_OF_TYPE = {
    "ATTESTATION_FACT": "OBSERVED_RECORD",
    "EVENT_TRUTH": "OBJECT_LEVEL_HISTORY",
    "IDENTITY": "IDENTITY_HYPOTHESIS",
    "OCCURRENCE_IDENTITY": "SAME_OCCURRENCE_HYPOTHESIS",
    "REFERENT_IDENTITY": "SAME_OCCURRENCE_HYPOTHESIS",
    "CAUSAL_LEVEL": "INTERPRETATION_HYPOTHESIS",
    "INTERPRETATION": "INTERPRETATION_HYPOTHESIS",
    "OPEN_SET_MEMBERSHIP": "OTHER",
    "TIME": "TEMPORAL_HYPOTHESIS",
}

log = logging.getLogger("v2_world_reaudit")


# ---------------------------------------------------------------- parse rendered formulas back
def split_top(s, op):
    depth, parts, cur, i = 0, [], "", 0
    while i < len(s):
        ch = s[i]
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if depth == 0 and s.startswith(op, i):
            parts.append(cur)
            cur = ""
            i += len(op)
            continue
        cur += ch
        i += 1
    parts.append(cur)
    return [p.strip() for p in parts]


def parse(s):
    s = s.strip()
    if not s:
        return None
    if s.startswith("¬"):
        return ("not", parse(s[1:]))
    if s.startswith("(") and s.endswith(")"):
        depth = 0
        for i, ch in enumerate(s):
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0 and i < len(s) - 1:
                break
        else:
            inner = s[1:-1]
            for op, tag in ((" → ", "imp"), (" ↔ ", "iff"), (" ∧ ", "and")):
                parts = split_top(inner, op)
                if len(parts) > 1:
                    return (tag,) + tuple(parse(p) for p in parts)
            return parse(inner)
    if " ∈ [" in s:
        v, rest = s.split(" ∈ [", 1)
        return ("in", v.strip(), rest.rstrip("]"))
    if " < " in s:
        a, b = s.split(" < ")
        return ("lt", a.strip(), b.strip())
    if " = " in s:
        v, val = s.split(" = ", 1)
        val = {"True": True, "False": False}.get(val.strip(), val.strip())
        return ("eq", v.strip(), val)
    return ("var", s)


def evaluate(f, asg):
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


VAR_RE = re.compile(r"\b(?:ATT|E|T|SAME|ID|REF|MEMBER|CAUSELEVEL|FABSCOPE|TERM|SAMELIST|SENSE)_[A-Za-z0-9_]+")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read(name):
    with open(OUT_DIR / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


# ---------------------------------------------------------------- per-constraint judgments
# theft exclusions: which partner needs an interpretation step before it entails "a theft occurred"
THEFT_PARTNER_NOTE = {
    "EC0143": "정조(6/13) '도난이 실제로 있었음' — '도난 없음'과 정확히 상보 명제.",
    "EC0131": "홍대협 '약간의 도난이 실제였음' — 도난 발생을 함의.",
    "EC0070": "나복 '도적이 돈과 물품을 훔침' — 같은 구순 집 도난을 가리키면 도난 발생을 함의.",
    "EC0132": "홍대협 '도난이 좀도둑 수준' — 도난 발생을 전제(presupposition).",
    "EC0050": "구순 '도적을 만남' — '도둑맞음'으로 읽을 때만 도난 발생을 함의(만났으나 잃지 않은 세계 가능).",
}
COND_REVIEW = {
    ("EC0108", "EC0126"): ("자미덕 남편이 이미 체포됐다는 한 비장의 말은 그 자체로 사주가 아니므로, 동일 인물이어도 "
                           "'사주한 일 없음'과 함께 참일 수 있음. 동일성만으로는 모순이 성립하지 않음.",
                           "(ID_HANBIJANG__HANJAEUK ∧ INTERP_EC0108_PART_OF_INSTIGATION) → ¬(E_EC0108 ∧ E_EC0126)"),
    ("EC0118", "EC0129"): ("구순이 김상제를 수상하다고 말한 것과 유제희가 이름을 직접 염탐했다는 것은, 김상제=김명신이어도 "
                           "유제희가 탐문 중 구순의 말을 들었을 수 있어 함께 참일 수 있음.",
                           "(ID_PUNGGAK_KIMSANGJE__KIMMYEONGSIN ∧ INTERP_EC0118_NAMES_NOT_FROM_GUSUN) → ¬(E_EC0118 ∧ E_EC0129)"),
}
MEMBER_REVIEW = ("김명신이 형벌 받은 집단의 구성원이어도 '모진/참혹한 형벌'이 곤장·신문을 반드시 포함한다는 보장이 없음. "
                 "구성원 여부만으로는 모순이 성립하지 않음(분배적 해석과 형벌 범위 해석이 추가로 필요).")


def judge(c, cand, var_level):
    """Return (problem_class, keep_or_change, recommended_type, recommended_formula, reason, review)."""
    ctype = c["constraint_type"]
    formula = (c["antecedent"] + " → " if c["antecedent"] else "") + c["consequent_or_formula"]
    names = sorted(set(VAR_RE.findall(formula)))
    e_vars = [n for n in names if n.startswith("E_")]
    if any(n.startswith("ATT_") for n in names):
        return (EVIDENCE_ONLY, "CHANGE", "NONE", "(제거)", "기록 존재 변수를 제약에 사용 — 사료 충돌을 world 제거로 바꿈.", True)

    if ctype == "ATTESTED_ACT_ANCHOR":
        ec = e_vars[0][2:]
        st = cand[ec]["epistemic_status"]
        return (OVERANCHOR, "CHANGE", "NONE (world constraint 아님)",
                f"(없음) ATT_{ec} = TRUE 유지; E_{ec}는 free; 명령/건의 실재는 posterior 단계 evidence로 가중",
                f"{st} 기록이 있다는 사실(ATT)만 관측 사실이고, 실제로 그 명령·건의가 있었다는 것(E)은 역사적 claim. "
                "사료 유형만으로 논리적 공리로 고정할 근거가 없음. 집행(EXECUTION)은 원래부터 만들지 않았음.", False)

    if ctype == "MUTUAL_EXCLUSION":
        if any(n.startswith("ID_") for n in names):
            return (VALID_HARD, "KEEP", ctype, formula,
                    "구조 가설끼리의 배제: 한재욱과 유제희는 같은 진술(P0086)에 서로 다른 사람으로 나오므로 "
                    "하급 보조자가 둘 다일 수 없음. 사료 내용을 사실로 고정하지 않음.", False)
        neg = [v for v in e_vars if v[2:] in ("EC0022", "EC0046")][0][2:]
        other = [v for v in e_vars if v[2:] not in ("EC0022", "EC0046")][0][2:]
        note = THEFT_PARTNER_NOTE[other]
        if other == "EC0050":
            return (REVIEW, "CHANGE", "CONDITIONAL_CONTRADICTION",
                    f"INTERP_EC0050_MEANS_ROBBED → ¬(E_{neg} ∧ E_EC0050)",
                    f"object-level 배제이지만 함의에 해석 단계가 필요: {note}", True)
        return (VALID_HARD, "KEEP", ctype, formula,
                f"두 기록(ATT)은 모두 존재 가능하며 제거되지 않음. 제거되는 것은 같은 world에서 '도난이 없었다'({neg} 내용)와 "
                f"'도난이 있었다'를 함의하는 내용이 함께 참인 경우뿐. {note} "
                "단, 현재 표현은 claim별 변수끼리의 배제라서 '둘 다 거짓' world도 막지 못함(공유 사실 변수 부재, 요약 참조).",
                other == "EC0132")

    if ctype == "SAME_CONSISTENCY":
        return (REVIEW, "KEEP_PENDING_REVIEW", ctype, formula,
                "사료 내용이 아니라 두 서술의 행위 유형(불러들임 vs 밥을 줌)이 달라 같은 occurrence 가설을 배제함. "
                "occurrence를 '단일 행위'로 볼 때만 타당하고, 한 번의 방문 같은 '장면' 단위로 보면 같은 occurrence일 수 있음 — "
                "occurrence granularity 정의 필요.", True)

    if ctype == "TEMPORAL_ANCHOR":
        ec = e_vars[0][2:]
        review = ec == "EC0065"
        return (REVIEW if review else VALID_HARD, "KEEP", ctype, formula,
                ("candidate 자신의 명시 시간이 그 claim의 일부: claim이 참이면 그 시점이어야 함(claim이 거짓인 world에서는 무제약). "
                 "사료 날짜를 사실로 고정하지 않음.")
                + (" EC0065는 날짜가 알림 시점인지 침입 시점인지 미구분이라 검토 필요." if review else ""), review)

    if ctype == "TRANSITIVITY":
        kind = "인물 동일성" if names and names[0].startswith("ID_") else "same-occurrence"
        return (VALID_HARD, "KEEP", ctype, formula,
                f"{kind} 관계 자체의 동치관계 조건. truth value를 묶지 않음(same referent ≠ same proposition).", False)

    if ctype == "CONDITIONAL_CONTRADICTION":
        pair = tuple(sorted(v[2:] for v in e_vars))
        if pair in COND_REVIEW:
            why, rec = COND_REVIEW[pair]
            return (REVIEW, "CHANGE", ctype, rec, why, True)
        if any(n.startswith("MEMBER_") for n in names):
            mem = [n for n in names if n.startswith("MEMBER_")][0]
            return (REVIEW, "CHANGE", ctype,
                    f"({mem} ∧ INTERP_DISTRIBUTIVE_PUNISHMENT ∧ INTERP_PUNISHMENT_COVERS_TREATMENT) → {c['consequent_or_formula']}",
                    MEMBER_REVIEW, True)
        dep = c["depends_on_identity"] or c["depends_on_causal_level"] or c["depends_on_interpretation"]
        return (VALID_COND, "KEEP", ctype, formula,
                f"antecedent({dep})가 거짓인 world에서는 적용되지 않음(조건부 유지 확인). 두 기록은 언제나 함께 존재 가능.", True)

    if ctype == "IMPLICATION":
        if "↔" in c["consequent_or_formula"]:
            a, b = [v[2:] for v in e_vars]
            ca, cb = cand[a], cand[b]
            same_prop = (ca["event_type"] == cb["event_type"] and ca["polarity"] == cb["polarity"]
                         and ca["predicate"] == cb["predicate"] and ca["subject_surface"] == cb["subject_surface"]
                         and "ATTRIBUTION" not in ca["event_type"])
            if {a, b} == {"EC0012", "EC0030"}:
                return (BAD_COUPLING, "CHANGE", "IMPLICATION",
                        "(SAME_EC0012_EC0030 ∧ FABSCOPE_EC0012 = FABSCOPE_EC0030) → (E_EC0012 ↔ E_EC0030)",
                        "문자열은 같지만('구순이 도난 상황을 꾸밈') 두 claim은 '꾸밈'의 범위 해석 변수가 따로 있어, 범위가 다르면 다른 "
                        "명제가 됨. 같은 occurrence라는 것만으로 truth를 묶으면 안 됨.", True)
            if same_prop:
                return (VALID_COND, "KEEP", "IMPLICATION", formula,
                        f"같은 occurrence이고 의미 유형·polarity·predicate가 같으며 attribution이 아닌 occurrence 자체의 claim"
                        f"({ca['predicate']}) — 같은 명제이므로 truth equivalence 허용(5조건 충족).", False)
            return (BAD_COUPLING, "CHANGE", "IMPLICATION", "(제거)", "명제가 달라 truth equivalence 불가.", True)
        return (VALID_COND, "KEEP", "IMPLICATION", formula,
                "같은 occurrence라면 행위자도 같아야 한다는 구조 조건. truth value는 묶지 않으며 SAME이 거짓이면 무제약.", True)

    if ctype == "TEMPORAL_ORDER":
        return (VALID_COND, "KEEP", ctype, formula,
                "claim이 참이고 같은 기록 안의 referent 가설(REF)이 참일 때만 순서가 적용됨. 다른 source의 날짜를 쓰지 않음. "
                "T_x는 해당 사건이 실제 있었을 때만 의미가 있음(사건 존재와 시점 변수의 연결은 미표현).", True)

    return (REVIEW, "REVIEW", ctype, formula, "규칙 없음", True)


def main():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(LOG_DIR / "v2_world_logic_reaudit.log", mode="w", encoding="utf-8"),
                                  logging.StreamHandler(sys.stdout)])
    before = {n: sha256(OUT_DIR / n) for n in INPUTS}
    db_before = sha256(ROOT / "database" / "gusun_v2.duckdb")

    variables = read("19_v2_world_variables.csv")
    constraints = read("20_v2_logical_constraints.csv")
    cand = {c["event_candidate_id"]: c for c in read("12_v2_historical_event_candidates.csv")}
    var_level = {v["variable_id"]: LEVEL_OF_TYPE[v["variable_type"]] for v in variables}
    active = [c for c in constraints if c["hard_or_conditional"] in ("HARD_LOGICAL", "CONDITIONAL")]
    parsed = {}
    for c in active:
        f = parse(c["consequent_or_formula"])
        parsed[c["constraint_id"]] = ("imp", parse(c["antecedent"]), f) if c["antecedent"] else f

    def violated(asg):
        return [cid for cid, f in parsed.items()
                if set(VAR_RE.findall(str(f))) <= set(asg) and evaluate(f, asg) is False]

    # ---------------- variable level audit
    anchored = {}
    for c in active:
        if c["constraint_type"] == "ATTESTED_ACT_ANCHOR":
            anchored[VAR_RE.findall(c["consequent_or_formula"])[0]] = c["constraint_id"]
    same_forced_false = {}
    for c in active:
        if c["constraint_type"] == "SAME_CONSISTENCY":
            same_forced_false[VAR_RE.findall(c["consequent_or_formula"])[0]] = c["constraint_id"]
    var_rows = []
    for v in variables:
        vid, vtype = v["variable_id"], v["variable_type"]
        level = var_level[vid]
        review, fixed = "NO", "FREE"
        if vtype == "ATTESTATION_FACT":
            fixed = "FIXED_TRUE (source-faithful record)"
            reason = "기록 존재는 관측 데이터로 고정 가능. 어떤 제약도 이 변수를 사용하지 않음(사료 충돌로 world 제거 없음)."
        elif vid in anchored:
            fixed = f"FIXED_TRUE by {anchored[vid]}"
            review = "YES"
            reason = (f"SOURCE_AUTHORITY_OVERANCHOR: {cand[vid[2:]]['epistemic_status']} 내용(명령·건의가 실제로 있었음)을 "
                      "사료 유형만으로 TRUE에 고정함. 기록 존재(ATT)와 분리해 free로 두어야 함.")
        elif vtype == "EVENT_TRUTH" and cand[vid[2:]]["polarity"] == "DOUBTED":
            level = "OTHER"
            review = "YES"
            reason = ("이 변수는 역사 사실이 아니라 '이조원의 신빙성 판단이 타당하다'는 평가 변수. 제약에 쓰이지 않아 피해는 없으나, "
                      "object-level 사실(구순 집에 화적이 들었음)은 별도 변수가 없음.")
        elif vtype == "EVENT_TRUTH":
            reason = ("claim 내용의 역사적 참거짓(free). 같은 사실을 여러 claim이 말할 때 이를 묶는 공유 사실 변수는 없음 — "
                      "complementary claim이 '둘 다 거짓'인 world가 막히지 않음(요약 참조).")
        elif vid in same_forced_false:
            fixed = f"FORCED_FALSE by {same_forced_false[vid]}"
            review = "YES"
            reason = "다른 행위 유형이라 같은 occurrence 가설을 배제. occurrence granularity 정의에 의존."
        elif vtype == "TIME":
            reason = ("candidate별 시점 변수. 같은 occurrence 가설(SAME)이 참일 때 T를 같게 하는 규칙은 없음 "
                      "(현재 두 쪽 모두 T가 있는 SAME 쌍이 없어 영향 0).")
        else:
            reason = "가설 변수(free). 어떤 제약도 단독으로 값을 고정하지 않음."
        var_rows.append([vid, vtype, level, fixed, reason, review])

    # ---------------- constraint re-audit
    hard_rows, cond_rows = [], []
    for c in active:
        formula = (c["antecedent"] + " → " if c["antecedent"] else "") + c["consequent_or_formula"]
        names = sorted(set(VAR_RE.findall(formula)))
        levels = sorted({var_level.get(n, "UNKNOWN") for n in names})
        problem, keep, rtype, rformula, reason, review = judge(c, cand, var_level)
        row = [c["constraint_id"], c["constraint_type"], "|".join(names), "|".join(levels), formula, problem, keep,
               rtype, rformula, reason, "YES" if review else "NO"]
        (hard_rows if c["hard_or_conditional"] == "HARD_LOGICAL" else cond_rows).append(row)

    # ---------------- question checks (hand-picked assignments)
    att_used = [c["constraint_id"] for c in active if any(n.startswith("ATT_") for n in VAR_RE.findall(
        c["antecedent"] + " " + c["consequent_or_formula"]))]
    q = {}
    q["Q1"] = (not att_used and not violated({"ATT_EC0022": True, "ATT_EC0143": True, "ATT_EC0114": True,
                                              "ATT_EC0126": True}),
               f"ATT 변수를 쓰는 제약 {len(att_used)}개. 상충 기록 쌍(5/12·6/13 정조, 자미덕·한재욱)의 ATT=TRUE 동시 배정에서 위반 0.")
    coupling = [r for r in cond_rows if "↔" in r[4]]
    bad_coupling = [r[0] for r in coupling if r[5] == BAD_COUPLING]
    q["Q2"] = (not bad_coupling,
               f"truth equivalence 제약 {len(coupling)}개 중 {len(bad_coupling)}개가 다른 명제를 묶을 수 있음: {'|'.join(bad_coupling)} "
               "(EC0012–EC0030). 나머지 3개는 김명신 '사망' 동일 명제.")
    q["Q3"] = (not anchored, f"고정된 object-level 변수 {len(anchored)}개(왕명 13, 비변사 건의 2): {'|'.join(sorted(anchored))}")
    tri = {"SAME_EC0007_EC0036": True, "SAME_EC0036_EC0053": True, "SAME_EC0007_EC0053": False}
    tri_ok = bool(violated(tri)) and not violated({**tri, "SAME_EC0007_EC0053": True})
    no_truth = not violated({"SAME_EC0007_EC0036": True, "SAME_EC0036_EC0053": True, "SAME_EC0007_EC0053": True,
                             "E_EC0054": True, "E_EC0053": True, "E_EC0055": False})
    q["Q4"] = (tri_ok and no_truth,
               "A=B, B=C, A≠C 배정은 제거되고, 셋 다 같음은 허용. 같은 occurrence여도 사망·사인·시점 claim의 참거짓은 따로 둘 수 있음.")
    w1 = violated({"ATT_EC0022": True, "ATT_EC0143": True, "E_EC0022": False, "E_EC0143": True})
    w2 = violated({"ATT_EC0022": True, "ATT_EC0143": True, "E_EC0022": True, "E_EC0143": False})
    w_both_true = violated({"E_EC0022": True, "E_EC0143": True})
    w_both_false = violated({"E_EC0022": False, "E_EC0143": False})
    q["Q5"] = (not w1 and not w2 and bool(w_both_true),
               f"W1(5월 판단 틀림)·W2(6월 판단 틀림) 허용, 둘 다 참은 제거({'|'.join(w_both_true)}). "
               f"단 '둘 다 거짓'(도난이 있지도 없지도 않음) world도 위반 {len(w_both_false)}건으로 허용됨 — 공유 사실 변수 부재로 인한 gap.")
    q["Q6"] = (not violated({"ATT_EC0114": True, "ATT_EC0126": True}),
               "자미덕·한재욱의 반대 진술 기록 존재(ATT)는 동시에 TRUE 가능. 내용 충돌은 한 비장=한재욱일 때만 조건부.")
    death_same = {r[0] for r in coupling if "EC0007" in r[4] or "EC0036" in r[4] or "EC0053" in r[4]}
    death_types = {cand[e]["event_type"] for e in ("EC0007", "EC0036", "EC0053")}
    cause_linked = [r[0] for r in coupling if any(f"E_{e}" in r[4] for e in ("EC0038", "EC0054", "EC0138", "EC0144",
                                                                           "EC0008", "EC0055", "EC0037"))]
    presup_gap = not violated({"E_EC0054": True, "E_EC0053": False})
    q["Q7"] = (not cause_linked and death_types == {"DEATH"},
               f"truth를 묶는 제약은 사망 occurrence 3건끼리뿐({'|'.join(sorted(death_same))}, 모두 DEATH '사망'). "
               "사인·시점·장소·책임 claim은 SAME 변수에도 truth 결합에도 들어가지 않음. "
               + ("다만 '사인=병'이 참인데 같은 보고의 '사망'은 거짓인 world도 막지 못함(전제 관계 미표현)." if presup_gap else ""))
    for k, (ok, detail) in q.items():
        log.info("%s %s — %s", k, "OK" if ok else "ISSUE", detail)

    # ---------------- summary
    all_rows = hard_rows + cond_rows

    def ids(pred):
        return [r[0] for r in all_rows if pred(r)]

    summary = [
        ["ATTESTATION_DISAGREEMENT_AS_WORLD_REMOVAL (ERROR_TYPE_A)", 0, "", "NONE",
         "없음. 기록 존재 변수(ATT)를 쓰는 제약이 하나도 없고, 상충 기록 쌍의 동시 존재가 허용됨."],
        ["SOURCE_AUTHORITY_OVERANCHOR (ERROR_TYPE_B)", len(ids(lambda r: r[5] == OVERANCHOR)),
         "|".join(ids(lambda r: r[5] == OVERANCHOR)), "HIGH",
         "ATTESTED_ACT_ANCHOR 15개 제거. ATT만 고정하고 E(명령·건의가 실제로 있었음)는 free로; 공식성은 posterior 단계 evidence. "
         "직전 단계 지시(ORDERED를 world constraint로 사용 가능)에 따라 만든 것이나 이번 원칙과 충돌. "
         "예시 WX018('명령이 없었다'=IMPOSSIBLE)도 함께 무효."],
        ["INVALID_SAME_OCCURRENCE_TRUTH_COUPLING (ERROR_TYPE_C)", len(ids(lambda r: r[5] == BAD_COUPLING)),
         "|".join(ids(lambda r: r[5] == BAD_COUPLING)), "MEDIUM",
         "EC0012–EC0030 truth equivalence에 FABSCOPE 일치 조건을 추가. 사망 3건 결합은 5조건을 충족해 유지."],
        ["MISSING_SHARED_OBJECT_FACT_VARIABLE", len(ids(lambda r: r[1] == "MUTUAL_EXCLUSION" and "EC0022" in r[4] or
                                                        r[1] == "MUTUAL_EXCLUSION" and "EC0046" in r[4])),
         "|".join(ids(lambda r: r[1] == "MUTUAL_EXCLUSION" and ("EC0022" in r[4] or "EC0046" in r[4]))), "HIGH",
         "object-level 사실이 claim별 E 변수로만 표현되어, 같은 사실 X를 말하는 claim들을 묶는 H_X가 없음. 그 결과 "
         "(a) 상보 claim('도난 없음' vs '도난 있음')이 둘 다 거짓인 world, (b) '사인=병'은 참인데 '사망'은 거짓인 world가 막히지 않음. "
         "H_THEFT_GUSUN, H_KIM_DIED 같은 공유 사실 변수를 두고 각 E를 H에 대한 정의식(E_EC0022 ↔ ¬H_THEFT_GUSUN 등)으로 연결하면 "
         "pairwise 배제와 사망 truth 결합이 이 정의식으로 대체됨. 사료를 거르는 문제는 아니지만 world 정의가 불완전함."],
        ["HARD_EXCLUSION_NEEDS_INTERPRETATION", len(ids(lambda r: r[1] == "MUTUAL_EXCLUSION" and r[5] == REVIEW)),
         "|".join(ids(lambda r: r[1] == "MUTUAL_EXCLUSION" and r[5] == REVIEW)), "MEDIUM",
         "'도적을 만남'(EC0050)이 도둑맞음을 뜻한다는 해석 변수를 두고 CONDITIONAL로 내림."],
        ["CONDITIONAL_ANTECEDENT_INSUFFICIENT", len(ids(lambda r: r[1] == "CONDITIONAL_CONTRADICTION" and r[5] == REVIEW)),
         "|".join(ids(lambda r: r[1] == "CONDITIONAL_CONTRADICTION" and r[5] == REVIEW)), "MEDIUM",
         "동일성/구성원 조건만으로는 모순이 성립하지 않는 6개(EC0108 vs EC0126, EC0118 vs EC0129, 형벌 open set 4개): "
         "해석 변수를 antecedent에 추가하거나 EVIDENCE_DISAGREEMENT_ONLY로 내림."],
        ["SAME_CONSISTENCY_GRANULARITY", len(ids(lambda r: r[1] == "SAME_CONSISTENCY")),
         "|".join(ids(lambda r: r[1] == "SAME_CONSISTENCY")), "LOW",
         "occurrence 단위(단일 행위 vs 장면)를 정의한 뒤 유지/조건부화 결정. 사료 내용을 거르지는 않음."],
        ["LATENT_RULE_DATE_CONFLICT_REMOVES_SAME", 0, "", "LOW",
         "v2_06의 일반 규칙은 명시 날짜·장소가 다르면 ¬SAME을 만들게 되어 있음(현재 발동 0건). 이는 기록된 날짜를 사실로 믿는 셈이므로 "
         "규칙을 SAME → ¬(E_A ∧ E_B)로 바꿔야 함."],
        ["MISSING_SAME_TIME_COUPLING", 0, "", "LOW",
         "SAME_A_B가 참이면 실제 발생 시점 T_A = T_B여야 하나 규칙이 없음(현재 두 쪽 모두 T가 있는 SAME 쌍 0건)."],
        ["DOUBTED_VARIABLE_SEMANTICS", 1, "E_EC0024", "LOW",
         "E_EC0024는 평가 타당성 변수. 화적 침입 사실은 공유 사실 변수로 따로 두고 DOUBTED는 evidence로만 사용."],
        ["TEMPORAL_ANCHOR_DATE_ATTACHMENT", len(ids(lambda r: r[1] == "TEMPORAL_ANCHOR" and r[5] == REVIEW)),
         "|".join(ids(lambda r: r[1] == "TEMPORAL_ANCHOR" and r[5] == REVIEW)), "LOW",
         "EC0065 날짜가 알림 시점인지 침입 시점인지 원문 확인."],
        ["VALIDATION_GAP_IN_V2_06", 2, "W03|W14", "LOW",
         "W03은 ORDERED/건의 고정을 '허용'으로 검사했고, 특별 테스트는 '둘 다 거짓' world를 검사하지 않음. 재구축 시 검증 추가."],
        ["VALID_TRANSITIVITY", len(ids(lambda r: r[1] == "TRANSITIVITY")), "", "OK",
         "same-occurrence 15개 + 인물 동일성 3개: 관계의 동치 조건만 강제하고 truth를 묶지 않음. 유지."],
        ["VALID_HARD_OTHER", len(ids(lambda r: r[5] == VALID_HARD and r[1] not in ("TRANSITIVITY",))), "", "OK",
         "도난 배제 8, 하급 보조자 구별 1, 명시 시간 앵커 24 유지."],
        ["VALID_CONDITIONAL", len(ids(lambda r: r[5] == VALID_COND)), "", "OK",
         "antecedent가 거짓인 world에서 적용되지 않음을 확인. 유지."],
        ["NOT_A_CONSTRAINT_AND_ANNOTATION", sum(1 for c in constraints if c["hard_or_conditional"] in ("NOT_A_CONSTRAINT", "ANNOTATION")),
         "", "OK", "formula가 비어 있어 어떤 world도 제거하지 않음(확인)."],
        ["OVERALL_ASSESSMENT", "", "", "MAJOR_LOGIC_REPAIR_REQUIRED",
         "사료 필터링(ERROR_TYPE_A)은 0건이고 기록/내용/구조 가설 3층 분리와 추이성은 유지됨 — 재구축은 불필요. "
         "그러나 (1) 사료 권위로 고정한 object-level 변수 15개, (2) 공유 사실 변수가 없어 '둘 다 거짓'·전제 위반 world가 남는 구조 결함, "
         "(3) 해석 조건이 빠진 제약 8개, (4) 잘못된 truth 결합 1개가 있어 논리 수정이 필요."],
    ]
    nc_bad = [c["constraint_id"] for c in constraints if c["hard_or_conditional"] in ("NOT_A_CONSTRAINT", "ANNOTATION")
              and c["consequent_or_formula"]]
    if nc_bad:
        log.error("NOT_A_CONSTRAINT/ANNOTATION rows with formulas: %s", nc_bad)
        sys.exit(1)
    for k, (ok, detail) in q.items():
        summary.append([f"QUESTION_{k}", "", "", "OK" if ok else "ISSUE", detail])

    cols = ["constraint_id", "current_type", "variables_involved", "variable_levels", "current_formula", "problem_class",
            "keep_or_change", "recommended_type", "recommended_formula", "reason", "manual_review_required"]
    write_csv(OUT_DIR / "24_v2_world_variable_level_audit.csv",
              ["variable_id", "current_variable_type", "recommended_level", "fixed_or_free", "reason",
               "manual_review_required"], var_rows)
    write_csv(OUT_DIR / "25_v2_hard_constraint_reaudit.csv", cols, hard_rows)
    write_csv(OUT_DIR / "26_v2_conditional_constraint_reaudit.csv", cols, cond_rows)
    write_csv(OUT_DIR / "27_v2_world_logic_reaudit_summary.csv",
              ["issue_type", "count", "affected_constraint_ids", "severity", "recommended_action"], summary)

    after = {n: sha256(OUT_DIR / n) for n in INPUTS}
    unchanged = before == after and db_before == sha256(ROOT / "database" / "gusun_v2.duckdb")
    log.info("inputs and database unchanged: %s", unchanged)
    if len(hard_rows) != 73 or len(cond_rows) != 52 or len(var_rows) != 402 or not unchanged:
        log.error("coverage/unchanged check failed: hard=%d cond=%d vars=%d unchanged=%s",
                  len(hard_rows), len(cond_rows), len(var_rows), unchanged)
        sys.exit(1)
    for name, rows in (("hard", hard_rows), ("conditional", cond_rows)):
        counts = {}
        for r in rows:
            counts[r[5]] = counts.get(r[5], 0) + 1
        log.info("%s: %s", name, counts)
    vl = {}
    for r in var_rows:
        vl[(r[2], r[3].split(" ")[0])] = vl.get((r[2], r[3].split(" ")[0]), 0) + 1
    log.info("variable levels: %s", vl)


if __name__ == "__main__":
    main()
