#!/usr/bin/env python3
"""GuSoon v2 repair of the possible-world logic layer (no enumeration).

Repairs the findings of output/24-27 without discarding the existing layer:
outputs 19-27 and the DuckDB tables world_variables / logical_constraints
stay untouched; the repaired layer is written alongside them.

Four layers are kept apart:
  OBSERVED_RECORD  ATT_<EC> (a record of the statement exists), CT_<EC> (the
                   date the record claims)                    -> fixed
  JUDGMENT_STATE   J_<actor>_<date>_<topic>: an actor's stance at a time -> free,
                   never logically tied to history; revisions are relations,
                   not contradictions
  CLAIM_CONTENT    E_<EC>: the content of one claim is true. Mapped claims are
                   defined by the shared historical fact they talk about.
  HISTORICAL_STATE H_*: what actually happened (binary, excluded middle)
plus identity / same-occurrence / interpretation hypotheses and historical
occurrence times T_<EC> (never equal to a claimed date by fiat).

Usage:
  python3 scripts/v2_08_world_repair.py                 # build + validate + write
  python3 scripts/v2_08_world_repair.py --mutation NAME # inject a fault, validate, write nothing
"""

import argparse
import csv
import hashlib
import importlib.util
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
PRESERVED_OUTPUTS = [f"{n}_v2_{s}.csv" for n, s in [
    (19, "world_variables"), (20, "logical_constraints"), (21, "world_constraint_audit"),
    (22, "impossible_combination_examples"), (23, "world_constraint_validation"),
    (24, "world_variable_level_audit"), (25, "hard_constraint_reaudit"), (26, "conditional_constraint_reaudit"),
    (27, "world_logic_reaudit_summary")]]
PROTECTED_TABLES = ["source_records", "source_faithful_propositions", "person_membership", "search_log",
                    "atomic_propositions", "entity_resolution_candidates", "open_set_normalized",
                    "event_projection_decisions", "historical_event_candidates", "event_candidate_support",
                    "candidate_pair_generation", "same_event_review", "conflict_group_summary",
                    "world_variables", "logical_constraints", "world_constraint_audit",
                    "impossible_combination_examples"]

_spec = importlib.util.spec_from_file_location("v2_07", ROOT / "scripts" / "v2_07_world_logic_reaudit.py")
_v2_07 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v2_07)
parse_old = _v2_07.parse

HARD, COND = "HARD_LOGICAL", "CONDITIONAL"


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


def Eq(v, val):
    return ("eq", v, val)


def EqV(a, b):
    return ("eqv", a, b)


def Lt(a, b):
    return ("lt", a, b)


def In(v, text):
    return ("in", v, text)


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
    if k == "eqv":
        return f"{f[1]} = {f[2]}"
    if k == "lt":
        return f"{f[1]} < {f[2]}"
    if k == "in":
        return f"{f[1]} ∈ [{f[2]}]"
    raise ValueError(k)


def vars_of(f):
    k = f[0]
    if k in ("var",):
        return {f[1]}
    if k in ("eq", "in"):
        return {f[1]}
    if k in ("lt", "eqv"):
        return {f[1], f[2]}
    return set().union(*(vars_of(x) for x in f[1:]))


def evaluate(f, asg):
    k = f[0]
    if k == "var":
        return asg.get(f[1])
    if k == "eq":
        return None if f[1] not in asg else asg[f[1]] == f[2]
    if k in ("lt", "in", "eqv"):
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


# ---------------------------------------------------------------- historical facts
# id: (fact_type, subject, predicate, object, referent_scope, basis, review)
FACTS = {
    "H_GUSUN_THEFT_OCCURRED": ("EVENT_OCCURRENCE", "구순 집", "도난이 실제로 발생함", "",
                               "구순이 정소한 구순 집 도난(구순 사건의 도난; 1793-02-22 밤으로 진술됨)",
                               "THEFT_REALITY: 5/12·5/27·6/13 판단과 구순·나복 서술이 같은 사건의 도난 여부를 다룸", False),
    "H_GUSUN_LARGE_ARMED_BAND_INTRUDED": ("EVENT_ATTRIBUTE", "구순 집", "큰 무리의 화적(도적떼)이 들었음", "",
                                          "같은 도난 사건의 침입자 규모·성격",
                                          "나복 '30여 명'(EC0067), 홍대협 '큰 화적 사건이 아님'(EC0132), 이조원 '화적 설명 의심'(EC0024)",
                                          True),
    "H_KIM_MYEONGSIN_DIED": ("EVENT_OCCURRENCE", "김명신", "사망함", "", "구순 사건의 김명신 사망(한 사람은 한 번 죽음)",
                             "이형원·이조원·윤노동이 각각 사망을 기록(EC0007·EC0036·EC0053)", False),
    "H_KIM_DETAINED_BY_BYEONGYEONG": ("EVENT_OCCURRENCE", "김명신", "병영에 구금됨", "", "구순 사건으로 인한 김명신 구금",
                                      "이형원 '달포 이상 구금'(EC0004); 사망 시점 귀속(EC0008·EC0055)의 전제", False),
    "H_KIM_DEATH_AFTER_DETENTION": ("TEMPORAL_ATTRIBUTE", "김명신 사망", "구금 이후에 일어남", "", "김명신 사망과 구금의 선후",
                                    "이형원 '구금·조사 뒤'(EC0008), 윤노동 '체포·구금 뒤'(EC0055)", False),
    "H_KIM_DEATH_IN_BYEONGYEONG_PRISON": ("PLACE_ATTRIBUTE", "김명신 사망", "병영 옥에서 일어남", "병영 옥", "김명신 사망 장소",
                                          "이조원(EC0037)", False),
    "H_KIM_DEATH_CAUSE_DISEASE": ("CAUSE_ATTRIBUTE", "김명신 사망", "직접 사인이 병(질병)", "", "김명신 직접 사인",
                                  "윤노동 '병'(EC0054), 홍대협 '질병'(EC0138) — 병/질병을 같은 술어로 봄(검토 필요)", True),
    "H_KIM_DEATH_CAUSE_EPIDEMIC": ("CAUSE_ATTRIBUTE", "김명신 사망", "직접 사인이 전염병", "", "김명신 직접 사인", "정조(EC0144)", False),
    "H_KIM_DEATH_RESPONSIBILITY_WRONGFUL_CHARGE": ("RESPONSIBILITY_ATTRIBUTE", "김명신 사망", "구순이 구성한 죄안에 책임이 있음",
                                                   "", "김명신 사망의 책임 원인",
                                                   "이조원(EC0038)을 책임 귀속으로 읽을 때", True),
    "H_KIM_DEATH_DIRECT_CAUSE_CHARGE_NOT_DISEASE": ("CAUSE_ATTRIBUTE", "김명신 사망",
                                                    "직접 사인이 질병(전염병 포함)이 아니라 죄안에 따른 처우 자체", "", "김명신 직접 사인",
                                                    "이조원(EC0038)을 직접 사인 주장으로 읽을 때", True),
    "H_KIM_WIFE_DIED": ("EVENT_OCCURRENCE", "김명신의 아내", "사망함", "", "김명신 아내의 사망", "이조원(EC0039)", False),
    "H_KIM_WIFE_DEATH_CAUSE_EPIDEMIC": ("CAUSE_ATTRIBUTE", "김명신 아내 사망", "직접 사인이 전염병", "", "김명신 아내 직접 사인",
                                        "정조(EC0145); 이조원 '따라 죽음'(EC0040)의 해석에 따라 반대 claim", True),
    "H_KIM_WIFE_DIED_AFTER_KIM": ("TEMPORAL_ATTRIBUTE", "김명신 아내 사망", "김명신 사망 이후에 일어남", "", "두 사망의 선후",
                                  "이조원(EC0040)", True),
    "H_JISE_TERM_PRIOR_USE": ("STATE", "지세 호칭(지세랑 포함)", "이번 사건 이전에도 도적들이 쓰던 말임", "", "지세 호칭의 기원",
                              "홍대협(EC0047), 정조(EC0148)", False),
    "H_JISE_TERM_COINED_BY_GUSUN": ("EVENT_OCCURRENCE", "구순", "지세 호칭을 새로 지어냄", "", "지세 호칭의 기원",
                                    "이조원(EC0031), 정조(EC0149) — 각 claim의 의미 해석에 따라 연결", True),
    "H_HANBIJANG_DIRECTED_JAMIDEOK_FALSE_STATEMENT": ("EVENT_OCCURRENCE", "한 비장", "대질 때 자미덕의 거짓 발언을 지휘함", "자미덕",
                                                      "자미덕–이집거 대질", "자미덕(EC0114)", False),
    "H_HANBIJANG_CONDITIONAL_RELEASE_OFFER": ("EVENT_OCCURRENCE", "한 비장",
                                              "특정인들을 큰 도적이라 말하면 자미덕과 남편을 석방하겠다는 조건문을 말함", "자미덕",
                                              "한 비장의 회유 발화(UG_P0081)", "자미덕(EC0109 조건 + EC0110 약속)", False),
    "H_HAN_JAEUK_INSTIGATED_JAMIDEOK": ("EVENT_OCCURRENCE", "한재욱", "자미덕을 사주함", "자미덕", "자미덕 공초에 대한 사주",
                                        "한재욱 부인(EC0126); 한 비장·변가의 처 동일성이 참이면 다른 claim과 연결", True),
    "H_HAN_JAEUK_COAXED_BYEONGA_CHEO": ("EVENT_OCCURRENCE", "한재욱", "변가의 처를 꾀어 공초를 내게 함", "변가의 처",
                                        "윤노동이 말한 회유", "윤노동(EC0058, EC0060)", False),
    "H_JAMIDEOK_FALSE_STATEMENT_AT_CONFRONTATION": ("EVENT_OCCURRENCE", "자미덕", "이집거와 대질할 때 거짓으로 꾸며 말함", "",
                                                    "자미덕–이집거 대질 중 발언", "자미덕(EC0113)", False),
    "H_JAMIDEOK_IJIPGEO_CONFRONTATION": ("EVENT_OCCURRENCE", "자미덕·이집거", "서로 대질함", "", "자미덕–이집거 대질",
                                         "자미덕(EC0112)", False),
    "H_HAN_JAEUK_ACQUAINTED_WITH_GUSUN": ("STATE", "한재욱", "구순과 아는 사이였음", "구순", "한재욱–구순 관계",
                                          "한재욱 부인(EC0127); 하급 보조자=한재욱이면 이조원의 '가객' 주장(EC0043)과 연결", True),
}

# claim -> fact mappings
# (ec, fact, relation, form, condition, scope, confidence, review, judgment_state, note)
#  form: IFF (E ↔ H or ¬H), IMPLIES (E → H or ¬H), CONJ (H ↔ conjunction of claims), NONE (no logical link)
MAP = [
    ("EC0022", "H_GUSUN_THEFT_OCCURRED", "ASSERTS_FALSE", "IFF", None, "'도난 자체가 없었다는 방향'을 받아들임(방향·중간 판단)",
     "MEDIUM", True, "J_JEONGJO_17930512_THEFT", "판단 강도는 judgment state에 둠. 같은 날 의금부 재조사 명령(EC0023)."),
    ("EC0046", "H_GUSUN_THEFT_OCCURRED", "ASSERTS_FALSE", "IFF", None, "'도난이 없었다는 방향의 판단'(실록)",
     "MEDIUM", True, "J_IJOWON_17930527_THEFT", ""),
    ("EC0143", "H_GUSUN_THEFT_OCCURRED", "ASSERTS_TRUE", "IFF", None, "'도난이 실제로 있었다'", "HIGH", False,
     "J_JEONGJO_17930613_THEFT", ""),
    ("EC0131", "H_GUSUN_THEFT_OCCURRED", "ASSERTS_TRUE", "IMPLIES", None, "'약간의 도난'이 실제였음(규모 한정 포함)", "HIGH", False,
     "J_HONG_17930613_THEFT", "'약간'이라는 추가 내용 때문에 한 방향 함의."),
    ("EC0132", "H_GUSUN_THEFT_OCCURRED", "ASSERTS_TRUE", "IMPLIES", None, "규모 평가가 도난 발생을 전제(presupposition)",
     "MEDIUM", False, "J_HONG_17930613_THEFT", ""),
    ("EC0070", "H_GUSUN_THEFT_OCCURRED", "ASSERTS_TRUE", "IMPLIES", None, "나복(명업 진술 속): 도적이 돈과 물품을 훔침",
     "MEDIUM", True, "", "같은 구순 사건 도난을 가리킨다고 봄(사건 정의)."),
    ("EC0050", "H_GUSUN_THEFT_OCCURRED", "ASSERTS_TRUE", "IMPLIES", ("INTERP_EC0050_MEANS_ROBBED", True),
     "구순(윤노동 보고 속): '도적을 만났다'", "LOW", True, "", "'만남'이 도둑맞음을 뜻할 때만 연결."),
    ("EC0012", "H_GUSUN_THEFT_OCCURRED", "ASSERTS_FALSE", "IMPLIES", ("FABSCOPE_EC0012", "FULL_FABRICATION"),
     "응답자들(이형원 보고 속): 구순이 도난 상황을 꾸밈", "LOW", True, "J_LEEHYEONGWON_17930512_THEFT",
     "'꾸밈'이 전체 조작일 때만 도난 부정."),
    ("EC0030", "H_GUSUN_THEFT_OCCURRED", "ASSERTS_FALSE", "IMPLIES", ("FABSCOPE_EC0030", "FULL_FABRICATION"),
     "이조원: 구순이 도난 상황을 꾸밈", "LOW", True, "J_IJOWON_17930527_THEFT", "'꾸밈'이 전체 조작일 때만 도난 부정."),
    ("EC0024", "H_GUSUN_LARGE_ARMED_BAND_INTRUDED", "DOUBTS", "NONE", None, "'화적이 들었다는 설명이 이치에 맞지 않음'",
     "HIGH", False, "J_IJOWON_17930527_THEFT", "DOUBTED는 FALSE가 아니므로 논리 연결 없음(evidence만)."),
    ("EC0067", "H_GUSUN_LARGE_ARMED_BAND_INTRUDED", "ATTRIBUTES_SCALE", "IMPLIES", None, "나복: 들어온 도적이 30여 명",
     "MEDIUM", True, "", "30여 명 규모를 '큰 무리'로 봄."),
    ("EC0132", "H_GUSUN_LARGE_ARMED_BAND_INTRUDED", "ATTRIBUTES_SCALE", "IMPLIES_NEG",
     ("SENSE_EC0132_EXCLUDES_LARGE_BAND", True), "홍대협: 큰 화적 사건이 아니라 좀도둑 수준", "LOW", True,
     "J_HONG_17930613_THEFT", "규모 평가가 무리 규모까지 배제하는 뜻일 때만."),
    ("EC0066", "H_GUSUN_THEFT_OCCURRED", "DOES_NOT_MAP_DIRECTLY", "NONE", None, "도적 침입 서술", "HIGH", False, "",
     "침입했으나 훔치지 않은 세계를 배제할 수 없음."),
    ("EC0068", "H_GUSUN_LARGE_ARMED_BAND_INTRUDED", "DOES_NOT_MAP_DIRECTLY", "NONE", None, "횃불 지참 서술", "HIGH", False, "",
     "횃불만으로 규모가 정해지지 않음."),
    ("EC0065", "H_GUSUN_THEFT_OCCURRED", "DOES_NOT_MAP_DIRECTLY", "NONE", None, "나복이 명업에게 알린 발화 사건", "HIGH", False,
     "", "발화 사건은 도난 여부와 독립."),
    ("EC0094", "H_GUSUN_THEFT_OCCURRED", "DOES_NOT_MAP_DIRECTLY", "NONE", None, "구순이 잃은 물건을 열거한 발화 사건", "HIGH", False,
     "", "발화 사건은 도난 여부와 독립."),
    ("EC0079", "H_GUSUN_THEFT_OCCURRED", "DOES_NOT_MAP_DIRECTLY", "NONE", None, "명업이 진술을 바꾼 발화 사건", "HIGH", False,
     "", "바뀐 진술의 내용은 이 claim이 주장하는 사실이 아님."),
    ("EC0007", "H_KIM_MYEONGSIN_DIED", "ASSERTS_TRUE", "IFF", None, "이형원: 사망", "HIGH", False,
     "J_LEEHYEONGWON_17930512_KIM_DEATH", ""),
    ("EC0036", "H_KIM_MYEONGSIN_DIED", "ASSERTS_TRUE", "IFF", None, "이조원: 사망", "HIGH", False,
     "J_IJOWON_17930527_KIM_DEATH", ""),
    ("EC0053", "H_KIM_MYEONGSIN_DIED", "ASSERTS_TRUE", "IFF", None, "윤노동: 사망", "HIGH", False,
     "J_YUNNODONG_17930611_KIM_DEATH", ""),
    ("EC0004", "H_KIM_DETAINED_BY_BYEONGYEONG", "ASSERTS_TRUE", "IMPLIES", None, "이형원: 달포 이상 구금(기간 포함)", "HIGH",
     False, "J_LEEHYEONGWON_17930512_KIM_DEATH", ""),
    ("EC0008", "H_KIM_DEATH_AFTER_DETENTION", "ATTRIBUTES_TIME", "IMPLIES", None, "이형원: 사망이 구금·조사 뒤(조사 포함)",
     "MEDIUM", False, "J_LEEHYEONGWON_17930512_KIM_DEATH", ""),
    ("EC0055", "H_KIM_DEATH_AFTER_DETENTION", "ATTRIBUTES_TIME", "IMPLIES", None, "윤노동: 사망이 체포·구금 뒤(체포 포함)",
     "MEDIUM", False, "J_YUNNODONG_17930611_KIM_DEATH", ""),
    ("EC0037", "H_KIM_DEATH_IN_BYEONGYEONG_PRISON", "ATTRIBUTES_PLACE", "IFF", None, "이조원: 사망 장소 병영 옥", "HIGH", False,
     "J_IJOWON_17930527_KIM_DEATH", ""),
    ("EC0054", "H_KIM_DEATH_CAUSE_DISEASE", "ATTRIBUTES_CAUSE", "IFF", None, "윤노동: 사인이 병", "MEDIUM", True,
     "J_YUNNODONG_17930611_KIM_DEATH", "'병'='질병'(EC0138)을 같은 술어로 봄."),
    ("EC0138", "H_KIM_DEATH_CAUSE_DISEASE", "ATTRIBUTES_CAUSE", "IFF", None, "홍대협: 죽음이 질병 때문", "HIGH", False,
     "J_HONG_17930613_KIM_DEATH", ""),
    ("EC0144", "H_KIM_DEATH_CAUSE_EPIDEMIC", "ATTRIBUTES_CAUSE", "IFF", None, "정조: 전염병에 걸려 죽음", "HIGH", False,
     "J_JEONGJO_17930613_KIM_DEATH", ""),
    ("EC0038", "H_KIM_DEATH_RESPONSIBILITY_WRONGFUL_CHARGE", "ATTRIBUTES_CAUSE", "IFF",
     ("CAUSELEVEL_EC0038", "RESPONSIBILITY_ATTRIBUTION"), "이조원: 구순이 구성한 죄안 때문에 사망(책임 귀속으로 읽을 때)",
     "MEDIUM", True, "J_IJOWON_17930527_KIM_DEATH", ""),
    ("EC0038", "H_KIM_DEATH_DIRECT_CAUSE_CHARGE_NOT_DISEASE", "ATTRIBUTES_CAUSE", "IFF", ("CAUSELEVEL_EC0038", "DIRECT_CAUSE"),
     "이조원: 구순이 구성한 죄안 때문에 사망(직접 사인으로 읽을 때)", "MEDIUM", True, "J_IJOWON_17930527_KIM_DEATH", ""),
    ("EC0039", "H_KIM_WIFE_DIED", "ASSERTS_TRUE", "IFF", None, "이조원: 김명신의 아내 사망", "HIGH", False,
     "J_IJOWON_17930527_KIM_DEATH", ""),
    ("EC0145", "H_KIM_WIFE_DEATH_CAUSE_EPIDEMIC", "ATTRIBUTES_CAUSE", "IFF", None, "정조: 처가 전염병에 걸려 죽음", "HIGH", False,
     "J_JEONGJO_17930613_KIM_DEATH", ""),
    ("EC0040", "H_KIM_WIFE_DIED_AFTER_KIM", "ATTRIBUTES_TIME", "IFF", None, "이조원: 김명신이 죽은 뒤 따라 죽음", "MEDIUM", True,
     "J_IJOWON_17930527_KIM_DEATH", ""),
    ("EC0040", "H_KIM_WIFE_DEATH_CAUSE_EPIDEMIC", "ATTRIBUTES_CAUSE", "IMPLIES_NEG",
     ("SENSE_EC0040", "CAUSAL_FOLLOWING_EXCLUDING_EPIDEMIC"), "'따라'가 전염병 아닌 원인으로 뒤따른 죽음일 때", "LOW", True,
     "J_IJOWON_17930527_KIM_DEATH", ""),
    ("EC0047", "H_JISE_TERM_PRIOR_USE", "ASSERTS_TRUE", "IMPLIES", None, "홍대협: 예전 호중 화적도 지세랑 호칭을 썼음", "MEDIUM",
     False, "J_HONG_17930528_JISE", ""),
    ("EC0148", "H_JISE_TERM_PRIOR_USE", "ASSERTS_TRUE", "IMPLIES", None, "정조: 지세대감·지세대사·지세랑은 예전 좀도둑들도 쓰던 말",
     "HIGH", False, "J_JEONGJO_17930613_JISE", ""),
    ("EC0031", "H_JISE_TERM_COINED_BY_GUSUN", "ASSERTS_TRUE", "IFF", ("SENSE_EC0031", "COINED_TERM"),
     "이조원: 구순이 지세랑이라는 말을 만듦('새로 지어냄'으로 읽을 때)", "LOW", True, "J_IJOWON_17930527_JISE", ""),
    ("EC0149", "H_JISE_TERM_COINED_BY_GUSUN", "ASSERTS_FALSE", "IFF", ("SENSE_EC0149", "FACTUAL_NEGATION"),
     "정조: 그 죄를 면함('사실 부정'으로 읽을 때)", "LOW", True, "J_JEONGJO_17930613_JISE", ""),
    ("EC0114", "H_HANBIJANG_DIRECTED_JAMIDEOK_FALSE_STATEMENT", "ASSERTS_TRUE", "IFF", None, "자미덕: 한 비장이 거짓 발언을 지휘",
     "MEDIUM", False, "J_JAMIDEOK_17930613_COACHING", ""),
    ("EC0109", "H_HANBIJANG_CONDITIONAL_RELEASE_OFFER", "ASSERTS_TRUE", "CONJ", None, "자미덕: 조건문의 조건 부분", "MEDIUM", False,
     "J_JAMIDEOK_17930613_COACHING", "H ↔ (E_EC0109 ∧ E_EC0110): 두 구성요소의 참거짓을 서로 묶지 않음."),
    ("EC0110", "H_HANBIJANG_CONDITIONAL_RELEASE_OFFER", "ASSERTS_TRUE", "CONJ", None, "자미덕: 조건문의 약속 부분", "MEDIUM", False,
     "J_JAMIDEOK_17930613_COACHING", "H ↔ (E_EC0109 ∧ E_EC0110)."),
    ("EC0126", "H_HAN_JAEUK_INSTIGATED_JAMIDEOK", "ASSERTS_FALSE", "IFF", None, "한재욱: 자미덕을 은밀히 사주한 일이 없다",
     "MEDIUM", True, "J_HANJAEUK_17930613_COACHING", "부인 범위가 '은밀히'로 한정됨."),
    ("EC0058", "H_HAN_JAEUK_COAXED_BYEONGA_CHEO", "ASSERTS_TRUE", "IFF", None, "윤노동: 한재욱이 변가의 처를 꾐", "MEDIUM", False,
     "J_YUNNODONG_17930611_COACHING", ""),
    ("EC0060", "H_HAN_JAEUK_COAXED_BYEONGA_CHEO", "ASSERTS_TRUE", "IMPLIES", None, "윤노동: 꾀어 그 공초를 내게 함(결과 포함)",
     "MEDIUM", False, "J_YUNNODONG_17930611_COACHING", ""),
    ("EC0113", "H_JAMIDEOK_FALSE_STATEMENT_AT_CONFRONTATION", "ASSERTS_TRUE", "IFF", None, "자미덕: 대질 때 거짓으로 꾸며 말함",
     "MEDIUM", False, "J_JAMIDEOK_17930613_COACHING", ""),
    ("EC0112", "H_JAMIDEOK_IJIPGEO_CONFRONTATION", "ASSERTS_TRUE", "IFF", None, "자미덕: 이집거와 대질함", "HIGH", False,
     "J_JAMIDEOK_17930613_COACHING", ""),
    ("EC0108", "H_HAN_JAEUK_INSTIGATED_JAMIDEOK", "DOES_NOT_MAP_DIRECTLY", "NONE", None, "한 비장: '남편이 이미 체포됐다'고 말함",
     "HIGH", False, "J_JAMIDEOK_17930613_COACHING", "그 말 자체는 사주가 아님(감사 결과 반영)."),
    ("EC0107", "H_HAN_JAEUK_INSTIGATED_JAMIDEOK", "DOES_NOT_MAP_DIRECTLY", "NONE", None, "한 비장이 방으로 불러들임", "HIGH",
     False, "J_JAMIDEOK_17930613_COACHING", "접촉은 사주가 아님."),
    ("EC0111", "H_HAN_JAEUK_INSTIGATED_JAMIDEOK", "DOES_NOT_MAP_DIRECTLY", "NONE", None, "한 비장이 떡과 밥을 줌", "HIGH",
     False, "J_JAMIDEOK_17930613_COACHING", "접촉은 사주가 아님."),
    ("EC0119", "H_HAN_JAEUK_INSTIGATED_JAMIDEOK", "DOES_NOT_MAP_DIRECTLY", "NONE", None, "한재욱: 방으로 부름(인정)", "HIGH",
     False, "J_HANJAEUK_17930613_COACHING", "접촉 인정은 사주 인정이 아님."),
    ("EC0120", "H_HAN_JAEUK_INSTIGATED_JAMIDEOK", "DOES_NOT_MAP_DIRECTLY", "NONE", None, "한재욱: 남은 밥을 줌(인정)", "HIGH",
     False, "J_HANJAEUK_17930613_COACHING", "접촉 인정은 사주 인정이 아님."),
    ("EC0127", "H_HAN_JAEUK_ACQUAINTED_WITH_GUSUN", "ASSERTS_FALSE", "IFF", None, "한재욱: 구순과 평생 모르는 사이", "MEDIUM",
     False, "J_HANJAEUK_17930613_COACHING", ""),
    ("EC0043", "H_HAN_JAEUK_ACQUAINTED_WITH_GUSUN", "ASSERTS_TRUE", "IMPLIES", ("ID_HAGEUP_BOJOJA__HANJAEUK", True),
     "이조원: 병영의 하급 보조자가 구순의 가객(하급 보조자=한재욱일 때)", "LOW", True, "", "동일성이 거짓이면 연결 없음."),
]

# judgment states
# id: (actor, date, topic, stance, strength, source_records, candidates, fact_ids, supersedes, notes)
JUDGMENTS = {
    "J_LEEHYEONGWON_17930512_THEFT": ("이형원", "1793-05-12", "구순 집 도난 조사 결과(장계)", "OTHER", "INTERMEDIATE", "SRC2_001",
                                      "EC0012|EC0013", "H_GUSUN_THEFT_OCCURRED", "",
                                      "회동 조사 응답자들의 '구순이 도난을 꾸밈' 진술을 보고. 이형원 자신의 도난 판단(AP0002)은 projection 검토 대기."),
    "J_JEONGJO_17930512_THEFT": ("정조", "1793-05-12", "이형원 장계·조사 결과(도난 조작 방향) 수용", "ACCEPTS", "INTERMEDIATE",
                                 "SRC2_001", "EC0022|EC0023", "H_GUSUN_THEFT_OCCURRED", "",
                                 "이형원 조사 결과를 상당히 신뢰. 같은 날 구순을 의금부에 가두고 엄히 조사하라고 명함(EC0023) — 종결된 판단이 아님."),
    "J_IJOWON_17930527_THEFT": ("이조원", "1793-05-27", "구순 집 도난의 실재", "REJECTS", "STRONG", "SRC2_002|SRC2_003",
                                "EC0024|EC0030|EC0046", "H_GUSUN_THEFT_OCCURRED|H_GUSUN_LARGE_ARMED_BAND_INTRUDED", "",
                                "한 판단 상태를 두 기록(비변사등록·실록)이 전함: 화적 설명 의심(DOUBTS), 구순의 꾸밈 주장, 도난 부재 방향."),
    "J_HONG_17930613_THEFT": ("홍대협", "1793-06-13", "구순 집 도난의 실재와 규모", "PARTIALLY_ACCEPTS", "STRONG", "SRC2_006",
                              "EC0131|EC0132", "H_GUSUN_THEFT_OCCURRED|H_GUSUN_LARGE_ARMED_BAND_INTRUDED", "",
                              "약간의 도난은 실제(발생 인정), 큰 화적 사건은 아님(규모 부정)."),
    "J_JEONGJO_17930613_THEFT": ("정조", "1793-06-13", "구순 집 도난의 실재", "FINAL_FINDING", "FINAL", "SRC2_006", "EC0143",
                                 "H_GUSUN_THEFT_OCCURRED", "J_JEONGJO_17930512_THEFT",
                                 "홍대협 안핵 결과를 받아 도난이 실제 있었다고 판단. FINAL은 절차상 최종이라는 뜻이며 역사적 참이라는 뜻이 아님."),
    "J_LEEHYEONGWON_17930512_KIM_DEATH": ("이형원", "1793-05-12", "김명신 구금·사망", "ACCEPTS", "INTERMEDIATE", "SRC2_001",
                                          "EC0004|EC0007|EC0008",
                                          "H_KIM_DETAINED_BY_BYEONGYEONG|H_KIM_MYEONGSIN_DIED|H_KIM_DEATH_AFTER_DETENTION", "", ""),
    "J_IJOWON_17930527_KIM_DEATH": ("이조원", "1793-05-27", "김명신 사망·장소·책임, 아내 사망", "ACCEPTS", "STRONG", "SRC2_002",
                                    "EC0036|EC0037|EC0038|EC0039|EC0040",
                                    "H_KIM_MYEONGSIN_DIED|H_KIM_DEATH_IN_BYEONGYEONG_PRISON|H_KIM_DEATH_RESPONSIBILITY_WRONGFUL_CHARGE|"
                                    "H_KIM_DEATH_DIRECT_CAUSE_CHARGE_NOT_DISEASE|H_KIM_WIFE_DIED|H_KIM_WIFE_DIED_AFTER_KIM", "",
                                    "죄안 사인 claim은 원인 층위(CAUSELEVEL_EC0038)에 따라 다른 사실에 연결."),
    "J_YUNNODONG_17930611_KIM_DEATH": ("윤노동", "1793-06-11", "김명신 사망·사인·시점", "ACCEPTS", "STRONG", "SRC2_005",
                                       "EC0053|EC0054|EC0055",
                                       "H_KIM_MYEONGSIN_DIED|H_KIM_DEATH_CAUSE_DISEASE|H_KIM_DEATH_AFTER_DETENTION", "", ""),
    "J_HONG_17930613_KIM_DEATH": ("홍대협", "1793-06-13", "김명신 사인", "ACCEPTS", "STRONG", "SRC2_006", "EC0138",
                                  "H_KIM_DEATH_CAUSE_DISEASE", "", ""),
    "J_JEONGJO_17930613_KIM_DEATH": ("정조", "1793-06-13", "김명신 부처 사인", "FINAL_FINDING", "FINAL", "SRC2_006",
                                     "EC0144|EC0145", "H_KIM_DEATH_CAUSE_EPIDEMIC|H_KIM_WIFE_DEATH_CAUSE_EPIDEMIC", "",
                                     "절차상 최종 판단."),
    "J_IJOWON_17930527_JISE": ("이조원", "1793-05-27", "지세 호칭의 기원", "ACCEPTS", "STRONG", "SRC2_002", "EC0031|EC0032",
                               "H_JISE_TERM_COINED_BY_GUSUN", "", "'만들었다'의 의미는 SENSE_EC0031."),
    "J_HONG_17930528_JISE": ("홍대협", "1793-05-28", "지세 호칭의 기원", "DOUBTS", "TENTATIVE", "SRC2_004", "EC0047",
                             "H_JISE_TERM_PRIOR_USE|H_JISE_TERM_COINED_BY_GUSUN", "",
                             "예전 호중 화적도 썼다며 '이번에 처음 생긴 말이 아닌 듯'(AP0056, 유보적 추론)."),
    "J_HONG_17930613_JISE": ("홍대협", "1793-06-13", "지세 호칭의 기원", "SUSPENDS_JUDGMENT", "INTERMEDIATE", "SRC2_006", "",
                             "H_JISE_TERM_COINED_BY_GUSUN", "J_HONG_17930528_JISE",
                             "여러 차례 조사에도 기원을 확정하지 못함(AP0145, META — event candidate 없음)."),
    "J_JEONGJO_17930613_JISE": ("정조", "1793-06-13", "지세 호칭의 기원", "FINAL_FINDING", "FINAL", "SRC2_006", "EC0148|EC0149",
                                "H_JISE_TERM_PRIOR_USE|H_JISE_TERM_COINED_BY_GUSUN", "",
                                "예전 좀도둑들도 쓰던 말이라 구순의 창작 죄를 면함."),
    "J_JAMIDEOK_17930613_COACHING": ("자미덕", "1793-06-13 기록(공초 시점은 그 이전)", "한 비장의 회유·지휘", "OTHER",
                                     "INTERMEDIATE", "SRC2_006", "EC0107|EC0108|EC0109|EC0110|EC0111|EC0112|EC0113|EC0114",
                                     "H_HANBIJANG_DIRECTED_JAMIDEOK_FALSE_STATEMENT|H_HANBIJANG_CONDITIONAL_RELEASE_OFFER|"
                                     "H_JAMIDEOK_FALSE_STATEMENT_AT_CONFRONTATION|H_JAMIDEOK_IJIPGEO_CONFRONTATION", "",
                                     "공초 진술(stance=OTHER: 진술 주장). 판정 주체가 아니라 당사자 진술."),
    "J_HANJAEUK_17930613_COACHING": ("한재욱", "1793-06-13 기록(공초 시점은 그 이전)", "자미덕 사주 여부·구순과의 관계", "REJECTS",
                                     "INTERMEDIATE", "SRC2_006", "EC0119|EC0120|EC0126|EC0127",
                                     "H_HAN_JAEUK_INSTIGATED_JAMIDEOK|H_HAN_JAEUK_ACQUAINTED_WITH_GUSUN", "",
                                     "접촉은 인정, 은밀한 사주와 구순과의 친분은 부인."),
    "J_YUNNODONG_17930611_COACHING": ("윤노동", "1793-06-11", "한재욱의 회유", "ACCEPTS", "STRONG", "SRC2_005", "EC0058|EC0059|EC0060",
                                      "H_HAN_JAEUK_COAXED_BYEONGA_CHEO", "", "'변가의 처'는 surface form 그대로."),
}
RELATIONS = [
    ("JR001", "J_JEONGJO_17930512_THEFT", "J_JEONGJO_17930613_THEFT", "REVISED_BY", "정조", "구순 집 도난의 실재",
     "5/12 이형원 조사 결과 수용(중간) → 6/13 홍대협 안핵 후 도난 실재 판단(최종). 판단 수정이며 historical contradiction이 아님. "
     "앞선 기록은 삭제되거나 거짓 기록이 되지 않음."),
    ("JR002", "J_HONG_17930528_JISE", "J_HONG_17930613_JISE", "REVISED_BY", "홍대협", "지세 호칭의 기원",
     "5/28 '예전에도 쓰인 말인 듯'(유보) → 6/13 '기원을 확정하지 못함'(판단 보류). 같은 사람의 판단 변화. REVIEW: 수정인지 정밀화인지."),
]

# new interpretation variables
NEW_INTERP = {
    "INTERP_EC0050_MEANS_ROBBED": ("EC0050", "구순의 '도적을 만났다'가 도둑맞았다는 뜻이다", "{TRUE, FALSE}",
                                   "hard REVIEW LC0021/LC0026 재처리"),
    "INTERP_EC0065_DATE_IS_TELLING_TIME": ("EC0065", "EC0065의 '2월 22일 밤'이 나복이 알린 시점이다(침입 시점이 아니라)",
                                           "{TRUE, FALSE}", "hard REVIEW EC0065 temporal anchor 재처리"),
    "INTERP_SAME_SCOPE_EC0012_EC0030": ("EC0012|EC0030", "두 '꾸밈' claim의 범위가 같다", "{TRUE, FALSE}",
                                        "LC0095 INVALID coupling 재처리"),
    "OCCURRENCE_GRANULARITY_ACT_LEVEL": ("global", "occurrence를 단일 행위 단위로 개별화한다(장면 단위가 아님)", "{TRUE, FALSE}",
                                         "hard REVIEW SAME_CONSISTENCY 4건 재처리"),
    "TAXON_EPIDEMIC_IS_DISEASE": ("H_KIM_DEATH_CAUSE_EPIDEMIC", "전염병 사인은 질병 사인의 한 경우이다", "{TRUE, FALSE}",
                                  "병/질병/전염병 taxonomy 미정"),
}

log = logging.getLogger("v2_world_repair")


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


def read(name):
    with open(OUT_DIR / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutation", default="")
    args = ap.parse_args()
    LOG_DIR.mkdir(exist_ok=True)
    logname = "v2_world_repair.log" if not args.mutation else f"v2_world_repair_mutation_{args.mutation}.log"
    handlers = [logging.StreamHandler(sys.stdout)]
    if not args.mutation:
        handlers.append(logging.FileHandler(LOG_DIR / logname, mode="w", encoding="utf-8"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=handlers)

    out_before = {n: sha256(OUT_DIR / n) for n in PRESERVED_OUTPUTS}
    expected_sha = {}
    for line in SHA_PATH.read_text(encoding="utf-8").splitlines():
        h, fn = line.split("  ", 1)
        expected_sha[fn] = h

    con = duckdb.connect(str(DB_PATH), read_only=bool(args.mutation))
    digests_before = {t: table_digest(con, t) for t in PROTECTED_TABLES}
    cur = con.execute("SELECT * FROM historical_event_candidates")
    cols = [d[0] for d in cur.description]
    cand = {r[0]: {c: ("" if v is None else v) for c, v in zip(cols, r)} for r in cur.fetchall()}
    cur = con.execute("SELECT a.atomic_prop_id, a.record_lunar_date, a.source_record_id FROM atomic_propositions a")
    ap_meta = {r[0]: (r[1] or "", r[2]) for r in cur.fetchall()}

    old_vars = read("19_v2_world_variables.csv")
    old_cons = read("20_v2_logical_constraints.csv")
    audit = {r["constraint_id"]: r for r in read("25_v2_hard_constraint_reaudit.csv") + read("26_v2_conditional_constraint_reaudit.csv")}

    # ---------------- variables
    LEVEL = {"ATTESTATION_FACT": "OBSERVED_RECORD", "EVENT_TRUTH": "CLAIM_CONTENT", "IDENTITY": "IDENTITY_HYPOTHESIS",
             "OCCURRENCE_IDENTITY": "SAME_OCCURRENCE_HYPOTHESIS", "REFERENT_IDENTITY": "SAME_OCCURRENCE_HYPOTHESIS",
             "CAUSAL_LEVEL": "INTERPRETATION_HYPOTHESIS", "INTERPRETATION": "INTERPRETATION_HYPOTHESIS",
             "OPEN_SET_MEMBERSHIP": "INTERPRETATION_HYPOTHESIS", "TIME": "TEMPORAL_STATE"}
    mapped_ecs = {m[0] for m in MAP if m[3] != "NONE"}
    variables = {}

    def var(vid, level, vtype, ref, domain, fixed, basis, notes, status):
        assert vid not in variables, vid
        variables[vid] = [vid, level, vtype, ref, domain, fixed, basis, notes, status]

    for v in old_vars:
        vid, vtype = v["variable_id"], v["variable_type"]
        level = LEVEL[vtype]
        fixed = "FIXED_TRUE (RECORD_ANCHOR)" if vtype == "ATTESTATION_FACT" else "FREE"
        notes = v["notes"]
        status = "EXISTING_RELEVELED"
        if vtype == "ATTESTATION_FACT":
            ec = v["referent_id"]
            rd, src = ap_meta[cand[ec]["origin_atomic_prop_id"]]
            notes = f"record_date={rd or '미상'} source={src}. 기록 존재만 고정."
        elif vtype == "EVENT_TRUTH":
            ec = v["referent_id"]
            if ec in mapped_ecs:
                notes = "CLAIM_CONTENT: 이 claim 내용이 참인지. claim_fact_mapping으로 공유 historical fact에 정의됨."
            else:
                notes = ("CLAIM_CONTENT(공유 사실 없음): 이 claim 고유 명제의 참거짓이며 다른 claim과 공유하는 historical fact가 "
                         "아직 없음. 사료 유형으로 값을 고정하지 않음(왕명·건의 포함).")
        elif vtype == "TIME":
            notes = "HISTORICAL_OCCURRENCE_TIME: 실제 발생 시점. 기록이 주장한 날짜(CT_)와 동일시하지 않음."
        var(vid, level, vtype, v["referent_id"], v["domain"], fixed, v["source_basis"], notes, status)

    for fid, (ftype, subj, pred, obj, scope, basis, review) in FACTS.items():
        var(fid, "HISTORICAL_STATE", "HISTORICAL_FACT", subj, "{TRUE, FALSE}", "FREE", basis,
            f"{subj} | {pred}" + (f" | {obj}" if obj else "") + f" — scope: {scope}", "NEW")
    for jid, j in JUDGMENTS.items():
        var(jid, "JUDGMENT_STATE", "JUDGMENT_STATE", j[0], "{TRUE, FALSE}", "FREE", j[5],
            f"{j[0]} {j[1]}: {j[2]} ({j[3]}/{j[4]}). historical state를 결정하지 않음.", "NEW")
    for iid, (ref, desc, domain, basis) in NEW_INTERP.items():
        var(iid, "INTERPRETATION_HYPOTHESIS", "INTERPRETATION", ref, domain, "FREE", basis, desc, "NEW")
    dated = sorted(ec for ec, c in cand.items() if c["occurrence_lunar_text"] and c["occurrence_precision"] != "RELATIVE_ONLY")
    for ec in dated:
        var(f"CT_{ec}", "OBSERVED_RECORD", "CLAIMED_OCCURRENCE_TIME", ec, f"{{{cand[ec]['occurrence_lunar_text']}}}",
            "FIXED (RECORD_ANCHOR)", cand[ec]["origin_atomic_prop_id"],
            "기록이 주장한 발생 시점(record_date와도, 실제 발생 시점 T_와도 다름).", "NEW")
    same_vars = sorted(v for v in variables if v.startswith("SAME_"))
    for sv in same_vars:
        for ec in sv.split("_")[1:]:
            if f"T_{ec}" not in variables:
                var(f"T_{ec}", "TEMPORAL_STATE", "TIME", ec, "lunar time point 1793 (ordinal)", "FREE", "SAME component",
                    "HISTORICAL_OCCURRENCE_TIME: SAME 가설 시점 공유 규칙용.", "NEW")

    # ---------------- constraints
    cons, changes = [], []

    def add(cls, antecedent, formula, kind, source="", dep_id="", dep_same="", dep_interp="", reason="", review=False):
        cid = f"RC{len(cons) + 1:04d}"
        cons.append(dict(constraint_id=cid, constraint_class=cls, antecedent=render(antecedent) if antecedent else "",
                         formula=render(formula), hard_or_conditional=kind, source=source, depends_on_identity=dep_id,
                         depends_on_same_occurrence=dep_same, depends_on_interpretation=dep_interp, reason=reason,
                         manual_review_required="YES" if review else "NO",
                         _f=Imp(antecedent, formula) if antecedent else formula))
        return cid

    # record anchors
    for v in sorted(variables):
        if v.startswith("ATT_"):
            add("RECORD_ANCHOR", None, Eq(v, True), HARD, reason="기록 존재(관측 데이터)만 고정.")
        elif v.startswith("CT_"):
            add("RECORD_ANCHOR", None, Eq(v, cand[v[3:]]["occurrence_lunar_text"]), HARD,
                reason="기록이 주장한 날짜(관측 데이터)만 고정. 실제 발생 시점은 T_.")
    # excluded middle
    for fid in FACTS:
        add("HISTORICAL_EXCLUDED_MIDDLE", None, In(fid, "TRUE, FALSE"), HARD,
            reason="하나의 world에서 이 역사 상태는 TRUE 또는 FALSE 중 하나(UNKNOWN은 인식 상태이지 world의 값이 아님).")
    # claim -> fact mapping
    for ec, fid, rel, form, condition, scope, conf, review, jid, note in MAP:
        if form == "NONE":
            continue
        e = V(f"E_{ec}")
        h = V(fid)
        ante = None
        dep_interp = dep_id = ""
        if condition:
            cv, val = condition
            ante = V(cv) if val is True else Eq(cv, val)
            if cv.startswith("ID_"):
                dep_id = cv
            else:
                dep_interp = cv
        if form == "IFF":
            f = Iff(e, h) if rel != "ASSERTS_FALSE" else Iff(e, Not(h))
        elif form == "IMPLIES":
            f = Imp(e, h) if rel != "ASSERTS_FALSE" else Imp(e, Not(h))
        elif form == "IMPLIES_NEG":
            f = Imp(e, Not(h))
        elif form == "CONJ":
            continue
        add("CLAIM_FACT_MAPPING", ante, f, COND if ante else HARD, source=f"{ec}→{fid}", dep_id=dep_id,
            dep_interp=dep_interp, reason=f"{rel} ({scope}). claim 내용의 참이 historical fact로 정의됨. {note}".strip(),
            review=review)
    add("CLAIM_FACT_MAPPING", None, Iff(V("H_HANBIJANG_CONDITIONAL_RELEASE_OFFER"), And(V("E_EC0109"), V("E_EC0110"))), HARD,
        source="EC0109|EC0110→H_HANBIJANG_CONDITIONAL_RELEASE_OFFER",
        reason="조건문 발화(UG_P0081)는 조건·약속 두 구성요소가 모두 참일 때 성립. 두 구성요소끼리의 참거짓은 묶지 않음.")
    # prerequisites
    PREREQ = [
        ("H_KIM_DEATH_CAUSE_DISEASE", "H_KIM_MYEONGSIN_DIED"), ("H_KIM_DEATH_CAUSE_EPIDEMIC", "H_KIM_MYEONGSIN_DIED"),
        ("H_KIM_DEATH_RESPONSIBILITY_WRONGFUL_CHARGE", "H_KIM_MYEONGSIN_DIED"),
        ("H_KIM_DEATH_DIRECT_CAUSE_CHARGE_NOT_DISEASE", "H_KIM_MYEONGSIN_DIED"),
        ("H_KIM_DEATH_AFTER_DETENTION", "H_KIM_MYEONGSIN_DIED"), ("H_KIM_DEATH_AFTER_DETENTION", "H_KIM_DETAINED_BY_BYEONGYEONG"),
        ("H_KIM_DEATH_IN_BYEONGYEONG_PRISON", "H_KIM_MYEONGSIN_DIED"),
        ("H_KIM_WIFE_DEATH_CAUSE_EPIDEMIC", "H_KIM_WIFE_DIED"), ("H_KIM_WIFE_DIED_AFTER_KIM", "H_KIM_WIFE_DIED"),
        ("H_KIM_WIFE_DIED_AFTER_KIM", "H_KIM_MYEONGSIN_DIED"),
        ("H_HANBIJANG_DIRECTED_JAMIDEOK_FALSE_STATEMENT", "H_JAMIDEOK_FALSE_STATEMENT_AT_CONFRONTATION"),
        ("H_JAMIDEOK_FALSE_STATEMENT_AT_CONFRONTATION", "H_JAMIDEOK_IJIPGEO_CONFRONTATION"),
    ]
    for a, b in PREREQ:
        add("PREREQUISITE", None, Imp(V(a), V(b)), HARD,
            reason=f"{a}가 참이려면 그 대상 occurrence({b})가 있어야 함. 반대 방향 함의는 두지 않음.")
    # historical mutual exclusions
    for a, b, why in [("H_KIM_DEATH_DIRECT_CAUSE_CHARGE_NOT_DISEASE", "H_KIM_DEATH_CAUSE_DISEASE", "직접 사인이 질병이 아님 vs 질병"),
                      ("H_KIM_DEATH_DIRECT_CAUSE_CHARGE_NOT_DISEASE", "H_KIM_DEATH_CAUSE_EPIDEMIC", "직접 사인이 질병(전염병 포함)이 아님 vs 전염병"),
                      ("H_JISE_TERM_PRIOR_USE", "H_JISE_TERM_COINED_BY_GUSUN", "예전부터 쓰던 말 vs 구순이 새로 지어냄")]:
        add("HISTORICAL_MUTUAL_EXCLUSION", None, Not(And(V(a), V(b))), HARD, reason=f"정의상 양립 불가: {why}.")
    add("CONDITIONAL_CONSTRAINT", V("TAXON_EPIDEMIC_IS_DISEASE"),
        Imp(V("H_KIM_DEATH_CAUSE_EPIDEMIC"), V("H_KIM_DEATH_CAUSE_DISEASE")), COND, dep_interp="TAXON_EPIDEMIC_IS_DISEASE",
        reason="전염병이 질병의 한 경우라는 분류를 채택할 때만. 병과 전염병은 언제나 함께 참일 수 있음.", review=True)
    # coaching links (identity-conditional)
    for idv, src, why in [("ID_HANBIJANG__HANJAEUK", "H_HANBIJANG_DIRECTED_JAMIDEOK_FALSE_STATEMENT", "거짓 발언 지휘"),
                          ("ID_HANBIJANG__HANJAEUK", "H_HANBIJANG_CONDITIONAL_RELEASE_OFFER", "석방 조건 회유"),
                          ("ID_BYEONGA_CHEO__JAMIDEOK", "H_HAN_JAEUK_COAXED_BYEONGA_CHEO", "변가의 처 회유")]:
        add("CONDITIONAL_CONSTRAINT", V(idv), Imp(V(src), V("H_HAN_JAEUK_INSTIGATED_JAMIDEOK")), COND, dep_id=idv,
            reason=f"{idv}가 참인 world에서만 '{why}'가 한재욱의 자미덕 사주에 해당. 거짓이면 두 사실은 무관. "
                   "'은밀히' 범위 문제로 검토 필요.", review=True)

    # carry over / repair old constraints
    replaced_note = {}
    for c in old_cons:
        cid, kind = c["constraint_id"], c["hard_or_conditional"]
        if kind not in ("HARD_LOGICAL", "CONDITIONAL"):
            continue
        ctype = c["constraint_type"]
        old_text = (c["antecedent"] + " → " if c["antecedent"] else "") + c["consequent_or_formula"]
        finding = audit[cid]["problem_class"]
        f_old = parse_old(c["consequent_or_formula"])
        a_old = parse_old(c["antecedent"]) if c["antecedent"] else None
        evs = sorted(x[2:] for x in vars_of(Imp(a_old, f_old) if a_old else f_old) if x.startswith("E_"))

        def log_change(new_behavior, reason, new_ids=""):
            changes.append([cid, f"{ctype}: {old_text}", new_behavior + (f" [{new_ids}]" if new_ids else ""), reason, finding])

        if ctype == "ATTESTED_ACT_ANCHOR":
            log_change("REMOVED: E 변수는 free. ATT_ RECORD_ANCHOR만 유지", "기록 존재 ≠ 실제 명령·건의 발생 ≠ 집행. 사료 권위로 고정하지 않음.")
        elif ctype == "MUTUAL_EXCLUSION" and any(x.startswith("ID_") for x in vars_of(f_old)):
            nid = add("IDENTITY_STRUCTURE", None, f_old, HARD, source=cid, dep_id="|".join(sorted(vars_of(f_old))),
                      reason=c["reason"])
            log_change("KEPT", "구조 가설끼리의 배제(사료 내용 고정 아님).", nid)
        elif ctype == "MUTUAL_EXCLUSION":
            log_change("REPLACED_BY_CLAIM_FACT_MAPPING", "pairwise claim 배제 대신 두 claim을 H_GUSUN_THEFT_OCCURRED에 연결 — "
                       "배중률과 함께 같은 결론이 도출되고 '둘 다 거짓' world도 막힘. EC0050은 해석 조건부 연결.")
        elif ctype == "SAME_CONSISTENCY":
            sv = next(iter(vars_of(f_old)))
            nid = add("CONDITIONAL_CONSTRAINT", V("OCCURRENCE_GRANULARITY_ACT_LEVEL"), f_old, COND, source=cid, dep_same=sv,
                      dep_interp="OCCURRENCE_GRANULARITY_ACT_LEVEL",
                      reason="단일 행위 단위로 occurrence를 볼 때만 서로 다른 행위는 같은 occurrence가 아님.", review=True)
            log_change("DOWNGRADED_TO_CONDITIONAL", "불확실한 granularity 해석을 hard로 두지 않음.", nid)
        elif ctype == "TEMPORAL_ANCHOR":
            ec = evs[0]
            tvar = f"T_{ec}"
            if ec == "EC0065":
                nid = add("TEMPORAL_CONSTRAINT", And(V(f"E_{ec}"), V("INTERP_EC0065_DATE_IS_TELLING_TIME")),
                          In(tvar, cand[ec]["occurrence_lunar_text"]), COND, source=cid,
                          dep_interp="INTERP_EC0065_DATE_IS_TELLING_TIME",
                          reason="날짜가 알림 시점일 때만 이 발화 사건의 시점으로 적용.", review=True)
                log_change("DOWNGRADED_TO_CONDITIONAL", "날짜 귀속이 불확실.", nid)
            else:
                nid = add("TEMPORAL_CONSTRAINT", V(f"E_{ec}"), In(tvar, cand[ec]["occurrence_lunar_text"]), HARD, source=cid,
                          reason="claim이 (날짜를 포함해) 참일 때만 실제 시점이 주장된 날짜(CT_)와 같음. claim이 거짓이면 무제약.")
                log_change("KEPT_AS_TEMPORAL_CONSTRAINT", "claimed date(CT_)와 historical time(T_)을 분리; 조건부 함의는 유지.", nid)
        elif ctype == "TRANSITIVITY":
            cls = "SAME_OCCURRENCE_EQUIVALENCE" if any(x.startswith("SAME_") for x in vars_of(f_old)) else "IDENTITY_STRUCTURE"
            nid = add(cls, a_old, f_old, HARD, source=cid, dep_same=c["depends_on_same_occurrence"],
                      dep_id=c["depends_on_identity"], reason="관계 자체의 추이성. truth value는 묶지 않음.")
            log_change("KEPT", "동치관계 조건.", nid)
        elif ctype == "CONDITIONAL_CONTRADICTION":
            pair = set(evs)
            interp = c["depends_on_interpretation"] or c["depends_on_causal_level"]
            if "EC0126" in pair and pair & {"EC0114", "EC0109", "EC0110", "EC0058", "EC0060"}:
                log_change("REPLACED_BY_FACT_STRUCTURE", "claim→fact mapping + 동일성 조건부 연결(ID → (H_x → H_HAN_JAEUK_INSTIGATED))로 대체.")
            elif pair == {"EC0108", "EC0126"}:
                log_change("REMOVED: NO_CONSTRAINT_YET", "'남편이 체포됐다'는 말 자체는 사주가 아님.")
            elif pair == {"EC0043", "EC0127"}:
                log_change("REPLACED_BY_FACT_STRUCTURE", "H_HAN_JAEUK_ACQUAINTED_WITH_GUSUN에 대한 mapping(EC0043은 동일성 조건부)으로 대체.")
            elif pair == {"EC0118", "EC0129"}:
                log_change("REMOVED: NO_CONSTRAINT_YET", "유제희가 탐문 중 구순의 말을 들었을 수 있어 모순 근거 없음.")
            elif interp.startswith("MEMBER_"):
                log_change("REMOVED: NO_CONSTRAINT_YET", "집단 구성원이라는 것만으로 개인의 곤장·신문을 추론하지 않음(open-set/group inference 금지).")
            elif interp.startswith("FABSCOPE_") and pair & {"EC0050", "EC0070", "EC0131", "EC0143"}:
                log_change("REPLACED_BY_CLAIM_FACT_MAPPING", "FABSCOPE=FULL → (E_FAB → ¬H_GUSUN_THEFT_OCCURRED)와 상대 claim의 mapping으로 대체.")
            elif interp.startswith("CAUSELEVEL_"):
                log_change("REPLACED_BY_FACT_STRUCTURE", "EC0038을 원인 층위에 따라 책임/직접 사인 사실에 연결하고, 직접 사인 사실끼리 배제.")
            elif interp in ("SENSE_EC0031", "SENSE_EC0149|SENSE_EC0031"):
                log_change("REPLACED_BY_FACT_STRUCTURE", "H_JISE_TERM_PRIOR_USE / H_JISE_TERM_COINED_BY_GUSUN과 의미 조건부 mapping으로 대체.")
            elif interp == "SENSE_EC0132_EXCLUDES_LARGE_BAND":
                log_change("REPLACED_BY_FACT_STRUCTURE", "H_GUSUN_LARGE_ARMED_BAND_INTRUDED에 대한 mapping으로 대체.")
            elif interp == "SENSE_EC0040":
                log_change("REPLACED_BY_FACT_STRUCTURE", "EC0040 → ¬H_KIM_WIFE_DEATH_CAUSE_EPIDEMIC(의미 조건부) mapping으로 대체.")
            else:
                nid = add("CONDITIONAL_CONSTRAINT", a_old, f_old, COND, source=cid, dep_id=c["depends_on_identity"],
                          dep_interp=interp, reason=c["reason"], review=True)
                log_change("KEPT", "공유 사실이 없는 claim끼리의 조건부 배제(조건이 거짓이면 무제약).", nid)
        elif ctype == "IMPLICATION":
            if f_old[0] == "iff":
                if set(evs) == {"EC0012", "EC0030"}:
                    nid = add("SAME_PROPOSITION_TRUTH_EQUIVALENCE",
                              And(V("SAME_EC0012_EC0030"), V("INTERP_SAME_SCOPE_EC0012_EC0030")), f_old, COND, source=cid,
                              dep_same="SAME_EC0012_EC0030", dep_interp="INTERP_SAME_SCOPE_EC0012_EC0030",
                              reason="같은 occurrence이고 '꾸밈'의 범위가 같다고 볼 때만 같은 명제.", review=True)
                    log_change("MODIFIED: scope 조건 추가", "same occurrence만으로 truth를 묶지 않음.", nid)
                else:
                    log_change("REPLACED_BY_CLAIM_FACT_MAPPING", "사망 claim 셋이 H_KIM_MYEONGSIN_DIED에 각각 정의되어 SAME 없이도 "
                               "같은 명제로 연결(한 사람은 한 번 죽음). SAME 가설에서 truth equivalence를 끌어내지 않음.")
            else:
                nid = add("CONDITIONAL_CONSTRAINT", a_old, f_old, COND, source=cid, dep_id=c["depends_on_identity"],
                          dep_same=c["depends_on_same_occurrence"], reason=c["reason"], review=True)
                log_change("KEPT", "같은 occurrence라면 행위자도 같아야 한다는 구조 조건(truth 결합 아님).", nid)
        elif ctype == "TEMPORAL_ORDER":
            nid = add("TEMPORAL_CONSTRAINT", a_old, f_old, COND, source=cid, dep_same=c["depends_on_same_occurrence"],
                      reason=c["reason"] + " T_는 실제 발생 시점.", review=True)
            log_change("KEPT", "referent 가설 조건부 시간 순서.", nid)
        else:
            raise ValueError(ctype)

    # same occurrence shares one historical time
    for sv in same_vars:
        a, b = sv.split("_")[1:]
        add("TEMPORAL_CONSTRAINT", V(sv), EqV(f"T_{a}", f"T_{b}"), COND, dep_same=sv,
            reason="같은 occurrence라면 실제 발생 시점은 하나. 각 기록의 주장 날짜(CT_)는 달라도 됨(기록 충돌일 뿐 world 탈락 사유 아님).")

    # ---------------- mutation injection (validator self-test)
    mut = args.mutation
    if mut == "j0512_fixes_theft_false":
        add("CONDITIONAL_CONSTRAINT", V("J_JEONGJO_17930512_THEFT"), Not(V("H_GUSUN_THEFT_OCCURRED")), COND)
    elif mut == "j0613_fixes_theft_true":
        add("CONDITIONAL_CONSTRAINT", V("J_JEONGJO_17930613_THEFT"), V("H_GUSUN_THEFT_OCCURRED"), COND)
    elif mut == "judgment_change_removes_world":
        add("HISTORICAL_MUTUAL_EXCLUSION", None, Not(And(V("J_JEONGJO_17930512_THEFT"), V("J_JEONGJO_17930613_THEFT"))), HARD)
    elif mut == "order_record_fixes_history":
        add("RECORD_ANCHOR", None, Eq("E_EC0151", True), HARD)
    elif mut == "cause_true_death_false":
        cons[:] = [c for c in cons if not (c["constraint_class"] == "PREREQUISITE" and "H_KIM_DEATH_CAUSE_DISEASE" in c["formula"])]
    elif mut == "same_couples_cause_and_death":
        add("SAME_PROPOSITION_TRUTH_EQUIVALENCE", V("SAME_EC0036_EC0053"), Iff(V("E_EC0038"), V("E_EC0053")), COND)
    elif mut == "date_difference_removes_same":
        add("CONDITIONAL_CONSTRAINT", None, Not(V("SAME_EC0089_EC0104")), HARD, reason="claimed date differs")
    elif mut == "doubted_to_false":
        add("CLAIM_FACT_MAPPING", None, Iff(V("E_EC0024"), Not(V("H_GUSUN_LARGE_ARMED_BAND_INTRUDED"))), HARD)
    elif mut == "record_existence_false":
        add("CONDITIONAL_CONSTRAINT", None, Not(And(V("ATT_EC0022"), V("ATT_EC0143"))), HARD)
    elif mut:
        log.error("unknown mutation %s", mut)
        sys.exit(2)

    # ---------------- validation
    checks = []

    def check(cid, desc, ok, detail=""):
        checks.append([cid, desc, "PASS" if ok else "ERROR", detail])
        if not ok:
            log.error("%s %s: %s", cid, desc, detail)

    def violated(asg):
        return [c["constraint_id"] for c in cons if vars_of(c["_f"]) <= set(asg) and evaluate(c["_f"], asg) is False]

    def all_vars(c):
        return vars_of(c["_f"])

    def unary_fixed(c):
        f = c["_f"]
        if f[0] == "eq":
            return f[1]
        if f[0] == "var":
            return f[1]
        if f[0] == "not" and f[1][0] == "var":
            return f[1][1]
        return None

    fixed = [unary_fixed(c) for c in cons if unary_fixed(c)]
    bad_fixed = [v for v in fixed if not (v.startswith("ATT_") or v.startswith("CT_"))
                 and not (v.startswith("SAME_") and False)]
    check("R01", "사료 권위만으로 historical/claim 변수 TRUE·FALSE 고정 = 0 (고정은 ATT_/CT_ 기록뿐)", not bad_fixed,
          "|".join(bad_fixed))
    att_misuse = [c["constraint_id"] for c in cons if c["constraint_class"] != "RECORD_ANCHOR"
                  and any(v.startswith(("ATT_", "CT_")) for v in all_vars(c))]
    check("R02", "5월·6월 정조 판단 기록이 동시에 존재 가능 (기록 변수는 RECORD_ANCHOR 외 사용 안 함)",
          not att_misuse and not violated({"ATT_EC0022": True, "ATT_EC0143": True}), "|".join(att_misuse))
    j_cons = [c["constraint_id"] for c in cons if any(v.startswith("J_") for v in all_vars(c))]
    check("R03", "5월·6월 judgment state가 서로 다를 수 있음 (J_를 쓰는 제약 0)",
          not j_cons and not violated({"J_JEONGJO_17930512_THEFT": True, "J_JEONGJO_17930613_THEFT": True}), "|".join(j_cons))
    rel_types = {r[3] for r in RELATIONS}
    check("R04", "judgment revision을 historical contradiction으로 처리하지 않음 (revision은 relation 표에만)",
          not j_cons and rel_types <= {"REVISED_BY", "SUPERSEDED_BY", "REFINED_BY", "NOT_DIRECTLY_COMPARABLE", "REVIEW_REQUIRED"})
    jh = [c["constraint_id"] for c in cons if any(v.startswith("J_") for v in all_vars(c))
          and any(v.startswith("H_") for v in all_vars(c))]
    w_free = all(not violated({"J_JEONGJO_17930613_THEFT": True, "H_GUSUN_THEFT_OCCURRED": h}) for h in (True, False))
    check("R05", "JUDGMENT_STATE가 HISTORICAL_STATE를 자동 결정하지 않음", not jh and w_free, "|".join(jh))
    same_truth = []
    for c in cons:
        a = c["_f"][1] if c["_f"][0] == "imp" else None
        if a is None or not any(v.startswith("SAME_") for v in vars_of(a)):
            continue
        cons_part = c["_f"][2]
        truth_vars = [v for v in vars_of(cons_part) if v.startswith(("E_", "H_"))]
        if truth_vars:
            ok = (c["constraint_class"] == "SAME_PROPOSITION_TRUTH_EQUIVALENCE"
                  and any(v.startswith("INTERP_SAME_SCOPE") for v in vars_of(a)))
            evs = [v[2:] for v in truth_vars if v.startswith("E_")]
            if len(evs) == 2:
                ca, cb = cand[evs[0]], cand[evs[1]]
                ok = ok and ca["event_type"] == cb["event_type"] and ca["predicate"] == cb["predicate"]
            if not ok:
                same_truth.append(c["constraint_id"])
    check("R06", "same occurrence만으로 다른 proposition truth를 묶은 사례 = 0", not same_truth, "|".join(same_truth))
    s_ok = all(sv.split("_")[1] < sv.split("_")[2] for sv in same_vars)
    trans = {(c["antecedent"], c["formula"]) for c in cons if c["constraint_class"] == "SAME_OCCURRENCE_EQUIVALENCE"}
    comps, seen = [], set()
    adj = {}
    for sv in same_vars:
        a, b = sv.split("_")[1:]
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    for n in sorted(adj):
        if n in seen:
            continue
        stack, comp = [n], set()
        while stack:
            x = stack.pop()
            if x not in comp:
                comp.add(x)
                stack.extend(adj[x] - comp)
        seen |= comp
        comps.append(sorted(comp))
    missing_t = []
    for comp in comps:
        for x, y, z in itertools.permutations(comp, 3):
            k1 = (render(And(V(same_var(x, y)), V(same_var(y, z)))), render(V(same_var(x, z))))
            k2 = (render(And(V(same_var(z, y)), V(same_var(y, x)))), render(V(same_var(z, x))))
            if k1 not in trans and k2 not in trans:
                missing_t.append(f"{x}-{y}-{z}")
    tri = {"SAME_EC0007_EC0036": True, "SAME_EC0036_EC0053": True, "SAME_EC0007_EC0053": False}
    check("R07", "SAME relation symmetry/transitivity 유지", s_ok and not missing_t and bool(violated(tri)),
          "|".join(missing_t[:5]))

    def impossible_for_all(fixed_asg, free_vars):
        for vals in itertools.product([True, False], repeat=len(free_vars)):
            if not violated({**fixed_asg, **dict(zip(free_vars, vals))}):
                return False
        return True

    check("R08", "death-cause TRUE / death FALSE 세계 금지",
          bool(violated({"H_KIM_DEATH_CAUSE_DISEASE": True, "H_KIM_MYEONGSIN_DIED": False}))
          and impossible_for_all({"E_EC0054": True, "E_EC0053": False}, ["H_KIM_DEATH_CAUSE_DISEASE", "H_KIM_MYEONGSIN_DIED"]))
    check("R09", "death-time attribution TRUE / death FALSE 세계 금지",
          bool(violated({"H_KIM_DEATH_AFTER_DETENTION": True, "H_KIM_MYEONGSIN_DIED": False})))
    check("R10", "THEFT history variable binary: 상보 claim이 둘 다 거짓인 world 금지(도난이 있지도 없지도 않은 world 없음)",
          impossible_for_all({"E_EC0022": False, "E_EC0143": False}, ["H_GUSUN_THEFT_OCCURRED"])
          and any(c["constraint_class"] == "HISTORICAL_EXCLUDED_MIDDLE" and "H_GUSUN_THEFT_OCCURRED" in c["formula"] for c in cons))
    doubted = [ec for ec, c in cand.items() if c["polarity"] == "DOUBTED"]
    d_bad = [c["constraint_id"] for c in cons if any(v == f"E_{d}" for d in doubted for v in all_vars(c))]
    check("R11", "DOUBTED를 historical FALSE로 고정·연결 = 0", not d_bad, "|".join(d_bad))
    denied = [ec for ec, c in cand.items() if c["epistemic_status"] == "DENIED"]
    den_bad = [v for v in fixed if v[2:] in denied or v.startswith("H_")]
    den_free = all(not violated({"ATT_EC0126": True, "H_HAN_JAEUK_INSTIGATED_JAMIDEOK": h}) for h in (True, False))
    check("R12", "DENIED를 historical FALSE로 고정 = 0", not den_bad and den_free, "|".join(den_bad))
    exec_bad = [v for v in variables if "EXEC" in v] + [c["constraint_id"] for c in cons if "EXEC" in c["formula"]]
    check("R13", "ORDER_RECORDED → ORDER_EXECUTED 추론 = 0", not exec_bad, "|".join(exec_bad))
    mem_bad = [c["constraint_id"] for c in cons if any(v.startswith("MEMBER_") for v in all_vars(c))]
    check("R14", "open-set 비명시 인물을 nonmember로 처리 = 0 (MEMBER 제약 0)", not mem_bad, "|".join(mem_bad))
    date_bad = [c["constraint_id"] for c in cons if c["_f"][0] == "in" and c["_f"][1].startswith("T_")]
    date_bad += [c["constraint_id"] for c in cons if c["_f"][0] == "not" and c["_f"][1][0] == "var"
                 and c["_f"][1][1].startswith("SAME_")]
    date_bad += [c["constraint_id"] for c in cons if c["_f"][0] == "imp" and c["_f"][2][0] == "not"
                 and c["_f"][2][1][0] == "var" and c["_f"][2][1][1].startswith("SAME_")
                 and "OCCURRENCE_GRANULARITY_ACT_LEVEL" not in vars_of(c["_f"][1])]
    check("R15", "record/claimed date와 historical time 동일시 = 0 (T_ 무조건 고정 없음, 날짜 차이로 ¬SAME 없음)",
          not date_bad, "|".join(date_bad))
    covered = {ch[0] for ch in changes}
    old_active = {c["constraint_id"] for c in old_cons if c["hard_or_conditional"] in ("HARD_LOGICAL", "CONDITIONAL")}
    check("R16", "기존 활성 제약 125개 모두 change log에 처리 기록", old_active == covered and len(old_active) == 125,
          f"{len(covered)}/{len(old_active)}")
    unknown = sorted({v for c in cons for v in all_vars(c) if v not in variables})
    check("R17", "제약이 참조하는 변수가 모두 정의됨", not unknown, "|".join(unknown[:10]))
    map_bad = [m[0] for m in MAP if m[0] not in cand or m[1] not in FACTS or (m[8] and m[8] not in JUDGMENTS)]
    check("R18", "claim_fact_mapping의 candidate·fact·judgment state 참조 유효", not map_bad, "|".join(map_bad))
    hard_review = [c["constraint_id"] for c in cons if c["hard_or_conditional"] == HARD and c["manual_review_required"] == "YES"
                   and c["constraint_class"] != "CLAIM_FACT_MAPPING"]
    check("R19", "불확실한 해석을 hard로 둔 구조 제약 0 (hard는 기록·정의·구조·mapping뿐)", not hard_review, "|".join(hard_review))
    pre_ok = all(not violated({"H_KIM_MYEONGSIN_DIED": True, f: False}) for f in
                 ("H_KIM_DEATH_CAUSE_DISEASE", "H_KIM_DEATH_CAUSE_EPIDEMIC", "H_KIM_DEATH_AFTER_DETENTION"))
    check("R20", "역방향 함의 없음: 사망이 참이어도 각 사인·시점 사실은 거짓일 수 있음", pre_ok)

    n_err = sum(1 for c in checks if c[2] == "ERROR")
    if mut:
        log.info("mutation %s: validation ERROR=%d (%s)", mut, n_err, "|".join(c[0] for c in checks if c[2] == "ERROR"))
        con.close()
        sys.exit(0 if n_err else 3)

    # ---------------- write
    var_cols = ["variable_id", "variable_level", "variable_type", "referent", "domain", "fixed_or_free", "source_basis",
                "notes", "status"]
    fact_cols = ["historical_fact_id", "fact_type", "subject", "predicate", "object", "domain", "referent_scope",
                 "derivation_basis", "manual_review_required"]
    map_cols = ["event_candidate_id", "historical_fact_id", "claim_relation", "claim_polarity", "claim_scope",
                "judgment_state_id", "logical_form", "condition", "mapping_confidence", "manual_review_required", "notes"]
    j_cols = ["judgment_state_id", "judge_or_actor", "judgment_date", "judgment_topic", "stance", "stance_strength",
              "source_record_ids", "event_candidate_ids", "historical_fact_id", "supersedes_or_revises", "notes"]
    rel_cols = ["relation_id", "from_judgment_state_id", "to_judgment_state_id", "relation_type", "actor", "topic", "notes"]
    con_cols = ["constraint_id", "constraint_class", "antecedent", "formula", "hard_or_conditional", "source",
                "depends_on_identity", "depends_on_same_occurrence", "depends_on_interpretation", "reason",
                "manual_review_required"]
    fact_rows = [[fid, f[0], f[1], f[2], f[3], "{TRUE, FALSE}", f[4], f[5], "YES" if f[6] else "NO"] for fid, f in FACTS.items()]
    map_rows = []
    for ec, fid, rel, form, condition, scope, conf, review, jid, note in MAP:
        cond_text = "" if not condition else (condition[0] if condition[1] is True else f"{condition[0]} = {condition[1]}")
        logical = {"IFF": "E ↔ H" if rel != "ASSERTS_FALSE" else "E ↔ ¬H",
                   "IMPLIES": "E → H" if rel != "ASSERTS_FALSE" else "E → ¬H", "IMPLIES_NEG": "E → ¬H",
                   "CONJ": "H ↔ (E_EC0109 ∧ E_EC0110)", "NONE": "(논리 연결 없음; evidence only)"}[form]
        map_rows.append([ec, fid, rel, cand[ec]["polarity"], scope, jid, logical, cond_text, conf, "YES" if review else "NO", note])
    j_rows = [[jid, *j[:6], j[6], j[7], j[8], j[9]] for jid, j in JUDGMENTS.items()]
    write_csv(OUT_DIR / "28_v2_repaired_world_variables.csv", var_cols, list(variables.values()))
    write_csv(OUT_DIR / "29_v2_historical_facts.csv", fact_cols, fact_rows)
    write_csv(OUT_DIR / "30_v2_claim_fact_mapping.csv", map_cols, map_rows)
    write_csv(OUT_DIR / "31_v2_judgment_states.csv", j_cols, j_rows)
    write_csv(OUT_DIR / "32_v2_judgment_state_relations.csv", rel_cols, RELATIONS)
    write_csv(OUT_DIR / "33_v2_repaired_logical_constraints.csv", con_cols, [[c[k] for k in con_cols] for c in cons])
    write_csv(OUT_DIR / "35_v2_world_repair_change_log.csv",
              ["old_constraint_id", "old_behavior", "new_behavior", "reason", "audit_finding"], changes)
    for table, fn in [("repaired_world_variables", "28_v2_repaired_world_variables.csv"),
                      ("historical_facts", "29_v2_historical_facts.csv"),
                      ("claim_fact_mapping", "30_v2_claim_fact_mapping.csv"),
                      ("judgment_states", "31_v2_judgment_states.csv"),
                      ("judgment_state_relations", "32_v2_judgment_state_relations.csv"),
                      ("repaired_logical_constraints", "33_v2_repaired_logical_constraints.csv")]:
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv(?, header=true, all_varchar=true, "
                    f"quote='\"', escape='\"')", [str(OUT_DIR / fn)])
    digests_after = {t: table_digest(con, t) for t in PROTECTED_TABLES}
    con.close()
    changed = [t for t in PROTECTED_TABLES if digests_before[t] != digests_after[t]]
    check("R21", "raw·기존 derived table(world_variables/logical_constraints 포함) 불변", not changed, "|".join(changed))
    out_changed = [n for n in PRESERVED_OUTPUTS if sha256(OUT_DIR / n) != out_before[n]]
    check("R22", "기존 output 19~27 불변", not out_changed, "|".join(out_changed))
    check("R23", "raw CSV SHA-256 불변", all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items()))
    write_csv(OUT_DIR / "34_v2_world_repair_validation.csv", ["check_id", "description", "severity", "detail"], checks)

    by_class = {}
    for c in cons:
        by_class[(c["hard_or_conditional"], c["constraint_class"])] = by_class.get((c["hard_or_conditional"], c["constraint_class"]), 0) + 1
    log.info("old variables: %d; repaired variables: %d", len(old_vars), len(variables))
    log.info("historical facts: %d; judgment states: %d; relations: %d", len(FACTS), len(JUDGMENTS), len(RELATIONS))
    log.info("claim->fact mappings: %d (logical %d, evidence-only %d)", len(MAP), sum(1 for m in MAP if m[3] != "NONE"),
             sum(1 for m in MAP if m[3] == "NONE"))
    for k in sorted(by_class):
        log.info("  %s / %s: %d", k[0], k[1], by_class[k])
    log.info("change log: %s", {k: sum(1 for ch in changes if ch[2].split(":")[0].split(" [")[0] == k)
                                for k in sorted({ch[2].split(":")[0].split(" [")[0] for ch in changes})})
    log.info("manual review: %d", sum(1 for c in cons if c["manual_review_required"] == "YES"))
    n_err = sum(1 for c in checks if c[2] == "ERROR")
    log.info("validation: ERROR=%d WARNING=%d", n_err, sum(1 for c in checks if c[2] == "WARNING"))
    if n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
