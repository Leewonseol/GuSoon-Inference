#!/usr/bin/env python3
"""GuSoon v2 same-event / same-issue review of event candidates (no merging).

- Generates candidate pairs from shared features only: shared_utterance_group,
  conflict_group, claim_topic, open-set id, place, time, subject entity + event
  type, entity + keyword concept, or the hand-assigned issue tag below.
  event_type alone, a keyword concept alone or an entity alone is not a
  pairing key: each pairs most candidates with unrelated ones.
- Classifies each pair with a primary / secondary relation. Inputs are the
  hand-assigned issue tags and narrative-chain stages below, plus explicit pair
  overrides. Nothing is merged, deleted, ordered or linked causally.
- Identity: DIRECTLY_IDENTIFIED_IN_SOURCE may be used as identity;
  STRONGLY_SUPPORTED only for pair generation and flagged as an identity
  assumption; CANDIDATE/UNRESOLVED never resolve a pair (conditional relations
  such as CONFLICT_IF_IDENTITY_HOLDS are used instead).
- Open sets: an unlisted name is never read as a non-member.

Outputs:
  output/15_v2_candidate_pair_generation.csv
  output/16_v2_same_event_review.csv
  output/17_v2_conflict_group_summary.csv
  output/18_v2_same_event_validation.csv
  logs/v2_same_event_review.log
  database/gusun_v2.duckdb: candidate_pair_generation, same_event_review, conflict_group_summary
"""

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

PROTECTED_TABLES = ["source_records", "source_faithful_propositions", "person_membership", "search_log",
                    "atomic_propositions", "entity_resolution_candidates", "open_set_normalized",
                    "event_projection_decisions", "historical_event_candidates", "event_candidate_support"]

_spec = importlib.util.spec_from_file_location("v2_03", ROOT / "scripts" / "v2_03_atomic_normalization.py")
_v2_03 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v2_03)
surface_forms = _v2_03.surface_forms

SO, SI, CP, CT, SU, TR, DI, RV = ("SAME_OCCURRENCE_CANDIDATE", "SAME_ISSUE_DIFFERENT_CLAIM", "COMPATIBLE_CLAIMS",
                                  "CONTRADICTORY_CLAIMS", "SAME_UTTERANCE_COMPONENT",
                                  "TEMPORALLY_RELATED_BUT_DISTINCT", "DISTINCT", "REVIEW_REQUIRED")
RELATIONS = {SO, SI, CP, CT, SU, TR, DI, RV}

# Identity strings used in entity_identity_dependency (status from output/08).
ID_HAN = "한 비장=한재욱 (CANDIDATE)"
ID_BYEON = "변가의 처=자미덕 (CANDIDATE)"
ID_HELPER = "병영의 하급 보조자=한재욱 (UNRESOLVED)"
ID_SANGJE = "풍각 김상제=김명신 (STRONGLY_SUPPORTED, identity assumption)"
ID_BYEONGSA = "병사=이광섭 (STRONGLY_SUPPORTED, identity assumption)"
NON_DIRECT_TAGS = ("(CANDIDATE)", "(UNRESOLVED)", "(STRONGLY_SUPPORTED")

# ---- analytic issue tags: candidate -> (issue, kind) ----
ISSUE = {}


def tag(issue, kind, *ecs):
    for ec in ecs:
        assert ec not in ISSUE, ec
        ISSUE[ec] = (issue, kind)


tag("THEFT_REALITY", "POS_JUDGE", "EC0131", "EC0143")
tag("THEFT_REALITY", "POS_ACT", "EC0050", "EC0070")
tag("THEFT_REALITY", "NEG", "EC0022", "EC0046")
tag("THEFT_REALITY", "DOUBT", "EC0024")
tag("THEFT_REALITY", "FAB", "EC0012", "EC0030")
tag("THEFT_REALITY", "DETAIL_ENTRY", "EC0066")
tag("THEFT_REALITY", "DETAIL_TORCH", "EC0068")
tag("THEFT_REALITY", "DETAIL_COUNT", "EC0067")
tag("THEFT_REALITY", "SCALE_SMALL", "EC0132")
tag("THEFT_REALITY", "SPEECH", "EC0065", "EC0094", "EC0079")
tag("EVIDENCE_FABRICATION", "FAB_MONEY", "EC0033")
tag("EVIDENCE_FABRICATION", "WOUND_BASE", "EC0034")
tag("EVIDENCE_FABRICATION", "FAB_WOUND", "EC0035")
tag("STOLEN_GOODS", "NOT_FOUND", "EC0006", "EC0057")
tag("STOLEN_GOODS", "JUDGED_WITHOUT", "EC0136")
tag("STOLEN_GOODS", "NOT_SECURED", "EC0139")
tag("DEATH", "KIM_OCC", "EC0007", "EC0036", "EC0053")
tag("DEATH", "KIM_CAUSE_CHARGE", "EC0038")
tag("DEATH", "KIM_CAUSE_BYEONG", "EC0054")
tag("DEATH", "KIM_CAUSE_JILBYEONG", "EC0138")
tag("DEATH", "KIM_CAUSE_EPIDEMIC", "EC0144")
tag("DEATH", "KIM_TIME", "EC0008", "EC0055")
tag("DEATH", "KIM_PLACE", "EC0037")
tag("DEATH", "WIFE_OCC", "EC0039")
tag("DEATH", "WIFE_TIME", "EC0040")
tag("DEATH", "WIFE_CAUSE_EPIDEMIC", "EC0145")
tag("TREATMENT", "NOT_BEATEN", "EC0146")
tag("TREATMENT", "NOT_INTERROGATED", "EC0147")
tag("TREATMENT", "INVESTIGATED", "EC0005")
tag("TREATMENT", "OPENSET_PUNISHED", "EC0009", "EC0056")
tag("TREATMENT", "INNOCENCE", "EC0010")
tag("JISE_ORIGIN", "INVENT_POS", "EC0031")
tag("JISE_ORIGIN", "INVENT_NEG", "EC0149")
tag("JISE_ORIGIN", "SPREAD", "EC0032")
tag("JISE_ORIGIN", "PRIOR", "EC0047", "EC0148")
tag("JISE_ORIGIN", "SELFNAME", "EC0069", "EC0095")
tag("COACHING", "HB_CONTACT", "EC0107", "EC0111")
tag("COACHING", "HB_PRESSURE", "EC0108")
tag("COACHING", "HB_OFFER", "EC0109", "EC0110")
tag("COACHING", "HB_DIRECT", "EC0114")
tag("COACHING", "SELF_LIE", "EC0113")
tag("COACHING", "HAN_ADMIT_ROOM", "EC0119")
tag("COACHING", "HAN_ADMIT_FOOD", "EC0120")
tag("COACHING", "HAN_DENY", "EC0126")
tag("COACHING", "YOON", "EC0058", "EC0060")
tag("COACHING", "YOON_TESTIMONY", "EC0059")
tag("MOTIVE", "ENMITY", "EC0011", "EC0027")
tag("MOTIVE", "GRUDGE_CAUSE", "EC0028")
tag("MOTIVE", "INTENT", "EC0029")
tag("MOTIVE", "NEIGHBOR", "EC0025")
tag("MOTIVE", "CRITICISM", "EC0026")
tag("MOTIVE", "INTIMATE", "EC0071")
tag("MOTIVE", "LETTER", "EC0072")
tag("MOTIVE", "BREAK", "EC0073")
tag("HAN_GUSUN_RELATION", "HAN_DENY_ACQ", "EC0127")
tag("HAN_GUSUN_RELATION", "HELPER_GUEST", "EC0043")
tag("SUSPECT", "SPEECH_KIM_CHIEF", "EC0002", "EC0121")
tag("SUSPECT", "SUSPICION", "EC0129")
tag("SUSPECT", "FRAME", "EC0013", "EC0014", "EC0015")
tag("SUSPECT", "LIST_GUSUN", "EC0052")
tag("SUSPECT", "SUMMON_YEONGGYO", "EC0051")
tag("SUSPECT", "LIST_YU", "EC0117")
tag("SUSPECT", "LIST_YU_RECORD", "EC0130")
tag("SUSPECT", "LIST_SOURCE_SELF", "EC0118")
tag("SUSPECT", "TARGETS", "EC0016")
tag("REASK", "SUGGEST", "EC0122")
tag("REASK", "REASKED", "EC0123")
tag("REASK", "BASIS", "EC0124")
tag("REASK", "ANSWER", "EC0125")
tag("INVESTIGATION_CONDUCT", "MUNHYEOP", "EC0017", "EC0140", "EC0142")
tag("INVESTIGATION_CONDUCT", "BIJANG_DIRECTION", "EC0141")
tag("INVESTIGATION_CONDUCT", "BYEONGSA", "EC0041", "EC0042")
tag("INVESTIGATION_CONDUCT", "GWANGSEOP", "EC0018", "EC0019", "EC0135", "EC0137")
tag("INVESTIGATION_CONDUCT", "BLAME_OTHERS", "EC0133", "EC0134")

# ---- narrative chains: candidate -> (chain, stage); different stages => TEMPORALLY_RELATED_BUT_DISTINCT ----
CHAIN = {}
for chain, stages in {
    "KIM_CUSTODY": {"EC0096": 1, "EC0098": 2, "EC0099": 2.1, "EC0100": 2.2, "EC0101": 2.3, "EC0102": 2.4,
                    "EC0003": 3, "EC0097": 3, "EC0004": 4, "EC0005": 5, "EC0007": 6, "EC0036": 6, "EC0053": 6,
                    "EC0039": 7},
    "JAMIDEOK_CUSTODY": {"EC0081": 1, "EC0082": 2, "EC0083": 3, "EC0084": 3.1, "EC0085": 3.2, "EC0086": 3.3,
                         "EC0087": 3.4, "EC0088": 4, "EC0089": 5, "EC0104": 5, "EC0090": 5.1, "EC0093": 6,
                         "EC0094": 6.1, "EC0095": 6.2, "EC0105": 7, "EC0106": 8, "EC0107": 9, "EC0108": 9.1,
                         "EC0109": 9.2, "EC0110": 9.3, "EC0111": 9.4, "EC0112": 10, "EC0113": 10.1, "EC0114": 10.2},
    "YU_DISPATCH": {"EC0115": 1, "EC0116": 1.1, "EC0128": 2, "EC0129": 2.5, "EC0117": 3, "EC0130": 3,
                    "EC0118": 3.1, "EC0121": 4, "EC0122": 4.1, "EC0123": 5, "EC0124": 5.1, "EC0125": 6},
    "ADMIN_IGWANGSEOP": {"EC0020": 1, "EC0021": 2, "EC0152": 3},
    "ADMIN_HOLD": {"EC0061": 1, "EC0062": 2},
    "ADMIN_GUSUN_CONFINE": {"EC0023": 1, "EC0045": 2},
    "ADMIN_IHYEONGWON": {"EC0154": 1, "EC0155": 2},
}.items():
    for ec, st in stages.items():
        CHAIN[ec] = (chain, st)


def R(primary, secondary="", conf="MEDIUM", cond="", dep="", review=None, note="", open_set=False):
    return dict(primary=primary, secondary=secondary, conf=conf, cond=cond, dep=dep,
                review=review, note=note, open_set=open_set)


# ---- issue-level kind rules (unordered kind pairs) ----
def K(a, b):
    return frozenset((a, b))


ISSUE_RULES = {
    "THEFT_REALITY": {
        K("POS_ACT", "POS_ACT"): R(SO, conf="MEDIUM", note="도적을 만남(구순) vs 도적이 훔침(나복): 같은 도난 행위를 말할 가능성. 규모 서술 차이는 별도 비교."),
        K("POS_JUDGE", "POS_JUDGE"): R(CP, conf="HIGH", note="둘 다 도난이 실제 있었다고 판단(홍대협 '약간의 도난', 정조)."),
        K("POS_ACT", "POS_JUDGE"): R(SI, CP, "MEDIUM", note="도난 행위 claim과 도난 실재 판단: 양립하나 다른 명제(판단은 규모를 낮춤)."),
        K("NEG", "NEG"): R(CP, conf="HIGH", note="둘 다 도난 부재 방향(같은 판단의 서로 다른 기록)."),
        K("POS_JUDGE", "NEG"): R(SI, CT, "HIGH", note="도난 있었다 vs 없었다(판단끼리)."),
        K("POS_ACT", "NEG"): R(SI, CT, "MEDIUM", note="도적이 훔쳤다/만났다 vs 도난이 없었다."),
        K("DOUBT", "NEG"): R(SI, CP, "MEDIUM", note="'화적이 들었다는 설명이 이치에 맞지 않음'(DOUBTED)은 부정 판단과 양립하지만 같은 명제는 아님."),
        K("DOUBT", "POS_JUDGE"): R(SI, CP, "MEDIUM", note="의심 대상은 '화적' 설명이며, '약간의 도난이 실제였다'는 판단과 양립."),
        K("DOUBT", "POS_ACT"): R(SI, RV, "LOW", note="의심 대상인 '화적' 설명과 구순·나복의 도적 서술: DOUBTED는 부정 단정이 아님."),
        K("DOUBT", "DETAIL_ENTRY"): R(SI, RV, "LOW", note="의심 대상인 '화적' 설명과 나복의 침입 서술: DOUBTED는 부정 단정이 아님."),
        K("DOUBT", "DETAIL_TORCH"): R(SI, RV, "LOW", note="의심 대상인 '화적' 설명과 나복의 횃불 서술: DOUBTED는 부정 단정이 아님."),
        K("DOUBT", "DETAIL_COUNT"): R(SI, RV, "LOW", note="의심 대상인 '화적' 설명과 나복의 30여 명 서술: DOUBTED는 부정 단정이 아님."),
        K("DOUBT", "SCALE_SMALL"): R(SI, CP, "MEDIUM", note="화적 설명을 의심하는 것과 '좀도둑 수준' 평가는 양립."),
        K("DOUBT", "FAB"): R(SI, CP, "MEDIUM"),
        K("FAB", "FAB"): R(SO, conf="MEDIUM", note="'구순이 도난 상황을 꾸밈'을 서로 다른 화자가 말함."),
        K("FAB", "NEG"): R(SI, CP, "MEDIUM"),
        K("FAB", "POS_JUDGE"): R(SI, RV, "LOW", cond="CONTRADICTORY_IF_FULL_FABRICATION",
                                 note="'꾸밈'이 도난 전체 조작인지 과장인지 미정(홍대협은 과장으로 평가)."),
        K("FAB", "POS_ACT"): R(SI, RV, "LOW", cond="CONTRADICTORY_IF_FULL_FABRICATION",
                               note="'꾸밈'이 도난 전체 조작인지 과장인지 미정."),
        K("FAB", "DETAIL_ENTRY"): R(SI, RV, "LOW", cond="CONTRADICTORY_IF_FULL_FABRICATION"),
        K("FAB", "DETAIL_TORCH"): R(SI, RV, "LOW", cond="CONTRADICTORY_IF_FULL_FABRICATION"),
        K("FAB", "DETAIL_COUNT"): R(SI, RV, "LOW", cond="CONTRADICTORY_IF_FULL_FABRICATION"),
        K("FAB", "SCALE_SMALL"): R(SI, CP, "MEDIUM"),
        K("NEG", "DETAIL_ENTRY"): R(SI, CT, "MEDIUM", note="도난 부재 판단과 도적 침입 서술."),
        K("NEG", "DETAIL_TORCH"): R(SI, CT, "MEDIUM"),
        K("NEG", "DETAIL_COUNT"): R(SI, CT, "MEDIUM"),
        K("NEG", "SCALE_SMALL"): R(SI, CT, "MEDIUM", note="'좀도둑 수준' 평가는 도난 발생을 전제."),
        K("POS_ACT", "DETAIL_ENTRY"): R(SI, CP, "MEDIUM"),
        K("POS_ACT", "DETAIL_TORCH"): R(SI, CP, "LOW"),
        K("POS_ACT", "DETAIL_COUNT"): R(SI, CP, "LOW"),
        K("POS_ACT", "SCALE_SMALL"): R(SI, CP, "MEDIUM"),
        K("POS_JUDGE", "DETAIL_ENTRY"): R(SI, CP, "MEDIUM"),
        K("POS_JUDGE", "DETAIL_TORCH"): R(SI, RV, "LOW", note="'약간의 도난/좀도둑' 판단과 횃불 지참 서술: 규모 해석이 갈릴 수 있음."),
        K("POS_JUDGE", "DETAIL_COUNT"): R(SI, RV, "LOW", note="'약간의 도난' 판단과 도적 30여 명 서술: 규모 해석이 갈림(SCALE 쌍 참조)."),
        K("POS_JUDGE", "SCALE_SMALL"): R(SI, CP, "HIGH"),
        K("DETAIL_COUNT", "SCALE_SMALL"): R(SI, CT, "MEDIUM", note="도적 30여 명 vs 큰 화적이 아닌 좀도둑 수준."),
        K("DETAIL_TORCH", "SCALE_SMALL"): R(SI, RV, "LOW", note="횃불 지참만으로 규모가 정해지지 않음."),
        K("DETAIL_ENTRY", "SCALE_SMALL"): R(SI, CP, "MEDIUM"),
    },
    "EVIDENCE_FABRICATION": {},
    "STOLEN_GOODS": {K("NOT_FOUND", "NOT_FOUND"): R(CP, conf="HIGH", note="둘 다 장물을 찾지 못함(NEGATED)으로 일치.")},
    "DEATH": {
        K("KIM_OCC", "KIM_OCC"): R(SO, conf="HIGH", note="서로 다른 사료가 각각 김명신 사망을 기록."),
        K("KIM_TIME", "KIM_TIME"): R(CP, conf="MEDIUM", note="'구금·조사 뒤' vs '체포·구금 뒤': 같은 시간 귀속의 다른 표현. 시간 edge는 만들지 않음."),
        K("KIM_CAUSE_BYEONG", "KIM_CAUSE_JILBYEONG"): R(SI, CP, "MEDIUM", review=True,
                                                         note="'병' vs '질병': 표현상 근접하나 동일 claim으로 확정하지 않음(taxonomy 미정)."),
        K("KIM_CAUSE_BYEONG", "KIM_CAUSE_EPIDEMIC"): R(SI, CP, "LOW", review=True,
                                                        note="'병' vs '전염병': 전염병이 병의 하위 개념일 수 있으나 taxonomy 미정."),
        K("KIM_CAUSE_JILBYEONG", "KIM_CAUSE_EPIDEMIC"): R(SI, CP, "LOW", review=True,
                                                           note="'질병' vs '전염병': 전염병이 질병의 하위 개념일 수 있으나 taxonomy 미정."),
        K("KIM_CAUSE_CHARGE", "KIM_CAUSE_BYEONG"): R(SI, RV, "LOW", cond="CONTRADICTORY_IF_SAME_CAUSAL_LEVEL",
                                                      note="'구순이 구성한 죄안 때문'은 책임 귀속일 수 있고 '병'은 직접 사인일 수 있음."),
        K("KIM_CAUSE_CHARGE", "KIM_CAUSE_JILBYEONG"): R(SI, RV, "LOW", cond="CONTRADICTORY_IF_SAME_CAUSAL_LEVEL",
                                                         note="책임 귀속(죄안) vs 직접 사인(질병) 층위가 다를 수 있음."),
        K("KIM_CAUSE_CHARGE", "KIM_CAUSE_EPIDEMIC"): R(SI, RV, "LOW", cond="CONTRADICTORY_IF_SAME_CAUSAL_LEVEL",
                                                        note="책임 귀속(죄안) vs 직접 사인(전염병) 층위가 다를 수 있음."),
        K("KIM_OCC", "WIFE_OCC"): R(TR, conf="MEDIUM", note="다른 인물의 사망. 선후는 EC0040이 말할 뿐 edge는 만들지 않음."),
        K("WIFE_TIME", "WIFE_CAUSE_EPIDEMIC"): R(SI, RV, "LOW", note="'따라 죽었다'의 의미(단순 선후/인과) 미판정이라 전염병 사인과의 관계를 정하지 않음."),
        K("WIFE_OCC", "WIFE_CAUSE_EPIDEMIC"): R(DI, conf="HIGH", note="occurrence vs cause attribution(같은 사망을 대상으로 할 수 있으나 다른 semantic object)."),
        K("WIFE_OCC", "WIFE_TIME"): R(DI, conf="HIGH", note="occurrence vs temporal attribution."),
    },
    "TREATMENT": {
        K("NOT_INTERROGATED", "INVESTIGATED"): R(SI, RV, "LOW", cond="CONTRADICTORY_IF_JOSA_EQUALS_SINMUN",
                                                  note="'조사함'과 '평범한 신문도 받지 않음'은 용어 범위가 다를 수 있음."),
        K("NOT_BEATEN", "INVESTIGATED"): R(SI, CP, "MEDIUM"),
        K("NOT_BEATEN", "OPENSET_PUNISHED"): R(RV, conf="LOW", cond="CONTRADICTORY_IF_OPEN_SET_MEMBER", open_set=True,
                                               note="형벌 받은 집단은 비열거 open set — 김명신의 구성원 여부를 추론하지 않음."),
        K("NOT_INTERROGATED", "OPENSET_PUNISHED"): R(RV, conf="LOW", cond="CONTRADICTORY_IF_OPEN_SET_MEMBER", open_set=True,
                                                     note="형벌 받은 집단은 비열거 open set — 김명신의 구성원 여부를 추론하지 않음."),
        K("OPENSET_PUNISHED", "OPENSET_PUNISHED"): R(SO, conf="LOW", review=True, open_set=True,
                                                     note="평민들/여러 죄수의 형벌: 같은 피해를 말할 수 있으나 두 집합 모두 비열거라 구성원 대응 불가."),
    },
    "JISE_ORIGIN": {
        K("INVENT_POS", "INVENT_NEG"): R(SI, CT, "HIGH", note="구순이 호칭을 만들었다 vs 그 죄를 면함(창작 혐의 불인정)."),
        K("INVENT_POS", "PRIOR"): R(SI, CT, "MEDIUM", note="예전부터 쓰이던 호칭이면 구순이 새로 만들었다는 주장과 충돌('만들었다'를 창작으로 읽을 때)."),
        K("INVENT_NEG", "PRIOR"): R(SI, CP, "HIGH"),
        K("PRIOR", "PRIOR"): R(CP, conf="MEDIUM", note="둘 다 예전 도적이 쓰던 호칭이라고 함(호중 화적 vs 무식한 좀도둑들)."),
        K("SPREAD", "INVENT_NEG"): R(SI, CP, "MEDIUM", note="창작 혐의 불인정은 유포 여부를 다루지 않음."),
        K("SPREAD", "PRIOR"): R(SI, CP, "MEDIUM"),
        K("SELFNAME", "INVENT_POS"): R(SI, RV, "LOW", note="구순 창작설이면 도적 자칭 서술이 흔들리나 호칭도 다름(지세랑 vs 지세대감/지세대사)."),
        K("SELFNAME", "INVENT_NEG"): R(SI, CP, "MEDIUM"),
        K("SELFNAME", "PRIOR"): R(SI, CP, "MEDIUM"),
        K("SELFNAME", "SELFNAME"): R(SI, RV, "LOW", note="나복이 전한 도적 자칭('지세대감') vs 구순의 발화('지세대사' 자칭을 말함): 호칭·층위가 다름."),
        K("SELFNAME", "SPREAD"): R(SI, CP, "LOW"),
    },
    "COACHING": {
        K("HB_CONTACT", "HAN_ADMIT_ROOM"): R(SI, RV, "LOW", cond="SAME_OCCURRENCE_IF_IDENTITY_HOLDS", dep=ID_HAN),
        K("HB_CONTACT", "HAN_ADMIT_FOOD"): R(SI, RV, "LOW", cond="SAME_OCCURRENCE_IF_IDENTITY_HOLDS", dep=ID_HAN),
        K("HB_OFFER", "HAN_DENY"): R(SI, RV, "LOW", cond="CONFLICT_IF_IDENTITY_HOLDS", dep=ID_HAN,
                                     note="자미덕이 말한 한 비장의 조건문 vs 한재욱의 은밀한 사주 부인."),
        K("HB_DIRECT", "HAN_DENY"): R(SI, RV, "LOW", cond="CONFLICT_IF_IDENTITY_HOLDS", dep=ID_HAN,
                                      note="한 비장이 거짓 발언을 지휘했다는 자미덕 진술 vs 한재욱의 사주 부인."),
        K("HB_PRESSURE", "HAN_DENY"): R(SI, RV, "LOW", cond="CONFLICT_IF_IDENTITY_HOLDS", dep=ID_HAN),
        K("HB_CONTACT", "HAN_DENY"): R(SI, CP, "LOW", dep=ID_HAN, note="방으로 부르거나 음식을 준 일은 사주 부인과 양립."),
        K("SELF_LIE", "HAN_DENY"): R(SI, CP, "MEDIUM", note="자미덕이 거짓말했다는 것 자체는 사주 부인과 양립(지휘 귀속은 EC0114)."),
        K("HAN_ADMIT_ROOM", "HAN_DENY"): R(SI, CP, "HIGH", note="같은 화자: 접촉 인정과 사주 부인."),
        K("HAN_ADMIT_FOOD", "HAN_DENY"): R(SI, CP, "HIGH", note="같은 화자: 접촉 인정과 사주 부인."),
        K("YOON", "HAN_DENY"): R(SI, RV, "LOW", cond="CONFLICT_IF_IDENTITY_HOLDS", dep=ID_BYEON,
                                 note="윤노동: 한재욱이 변가의 처를 꾐 vs 한재욱: 자미덕을 사주한 일 없음."),
        K("YOON_TESTIMONY", "HAN_DENY"): R(SI, CP, "LOW", dep=ID_BYEON),
        K("YOON", "HB_CONTACT"): R(SI, RV, "LOW", dep=f"{ID_HAN}; {ID_BYEON}"),
        K("YOON", "HB_PRESSURE"): R(SI, RV, "LOW", dep=f"{ID_HAN}; {ID_BYEON}"),
        K("YOON", "HB_OFFER"): R(SI, RV, "LOW", dep=f"{ID_HAN}; {ID_BYEON}",
                                 note="윤노동의 공초 내용(김명신=괴수)과 자미덕이 말한 조건문 대상(정원돌 등, open set)이 다름 — 김명신을 비구성원으로 추론하지 않음.",
                                 open_set=True),
        K("YOON", "HB_DIRECT"): R(SI, RV, "LOW", dep=f"{ID_HAN}; {ID_BYEON}"),
        K("YOON", "SELF_LIE"): R(SI, RV, "LOW", dep=ID_BYEON),
        K("YOON", "HAN_ADMIT_ROOM"): R(SI, CP, "LOW", dep=ID_BYEON),
        K("YOON", "HAN_ADMIT_FOOD"): R(SI, CP, "LOW", dep=ID_BYEON),
        K("YOON_TESTIMONY", "HB_OFFER"): R(SI, RV, "LOW", dep=f"{ID_HAN}; {ID_BYEON}", open_set=True,
                                           note="조건문 대상 명단은 open set이라 김명신 미명시를 비구성원으로 해석하지 않음."),
        K("YOON_TESTIMONY", "SELF_LIE"): R(SI, RV, "LOW", dep=ID_BYEON),
    },
    "MOTIVE": {
        K("ENMITY", "ENMITY"): R(CP, conf="MEDIUM", note="구순·김명신 사이의 원한(응답자들) vs 구순의 앙심(이조원): 일치 방향."),
        K("CRITICISM", "LETTER"): R(SO, conf="MEDIUM", review=True,
                                    note="'행실 비판'(이조원) vs '박거사 일로 편지 힐책'(명업): 같은 비판 행위일 가능성. 주제 표현이 달라 검토 필요."),
        K("INTIMATE", "BREAK"): R(TR, conf="MEDIUM", note="친숙·왕래 → 왕래 단절(시점이 다름)."),
        K("LETTER", "BREAK"): R(TR, conf="MEDIUM", note="편지 힐책 → '그 뒤' 왕래 단절. edge는 만들지 않음."),
        K("INTIMATE", "LETTER"): R(TR, conf="LOW"),
    },
    "HAN_GUSUN_RELATION": {
        K("HAN_DENY_ACQ", "HELPER_GUEST"): R(SI, RV, "LOW", cond="CONFLICT_IF_IDENTITY_HOLDS", dep=ID_HELPER,
                                             note="하급 보조자의 신원이 미해결이라 충돌 여부를 정하지 않음."),
    },
    "SUSPECT": {
        K("LIST_YU", "LIST_YU_RECORD"): R(SO, conf="MEDIUM", open_set=True,
                                          note="유제희가 이름을 적어 옴(한재욱) vs 유제희가 이름을 기록해 올림(유제희). 명단 구성원 비교는 원돌=정원돌(STRONGLY_SUPPORTED, identity assumption)에 의존하며 두 명단 모두 open set."),
        K("LIST_SOURCE_SELF", "LIST_YU_RECORD"): R(SI, RV, "LOW", note="출처 서술 차이: 직접 염탐 vs 구순의 말과 함께 기록."),
        K("LIST_SOURCE_SELF", "SUSPICION"): R(SI, RV, "LOW", cond="CONFLICT_IF_IDENTITY_HOLDS", dep=ID_SANGJE,
                                              note="김명신이 '그 이름들'에 포함되고 김상제=김명신이면 '직접 염탐' 서술과 충돌."),
        K("LIST_SOURCE_SELF", "LIST_GUSUN"): R(SI, RV, "LOW", cond="CONFLICT_IF_SAME_LIST",
                                               note="윤노동: 구순이 이름을 써 줌 vs 유제희: 직접 염탐. 같은 명단인지 미정."),
        K("LIST_GUSUN", "LIST_YU"): R(SI, RV, "LOW", open_set=True,
                                      note="명단 작성자가 다름(구순 vs 유제희). 두 명단 모두 open set이며 김명신만 공통 명시."),
        K("SPEECH_KIM_CHIEF", "SPEECH_KIM_CHIEF"): R(DI, conf="MEDIUM", note="같은 내용(김명신=도적 괴수)의 서로 다른 발화자·발화."),
        K("SPEECH_KIM_CHIEF", "SUSPICION"): R(SI, CP, "LOW", dep=ID_SANGJE),
    },
    "REASK": {
        K("SUGGEST", "REASKED"): R(TR, conf="MEDIUM", note="권유 → 재질문(같은 화자 한재욱의 서술)."),
        K("SUGGEST", "BASIS"): R(SI, CP, "HIGH", note="같은 화자: 유제희의 권유와 그에 따랐다는 귀속."),
        K("REASKED", "ANSWER"): R(TR, conf="MEDIUM", note="재질문 → '모른다' 응답."),
    },
    "INVESTIGATION_CONDUCT": {
        K("BYEONGSA", "GWANGSEOP"): R(SI, CP, "LOW", dep=ID_BYEONGSA),
    },
}
ISSUE_DEFAULT = R(SI, CP, "LOW", note="같은 쟁점의 서로 다른 claim으로 상충 근거 없음.")
for _k in ("POS_JUDGE", "POS_ACT", "NEG", "DOUBT", "FAB", "DETAIL_ENTRY", "DETAIL_TORCH", "DETAIL_COUNT",
           "SCALE_SMALL", "SPEECH"):
    ISSUE_RULES["THEFT_REALITY"][K("SPEECH", _k)] = R(
        DI, conf="MEDIUM", note="발화 사건(누가 도난을 말함/진술을 바꿈)과 도난 claim은 다른 대상 — 발화는 도난 실재 여부와 독립.")

# ---- explicit pair overrides (ordered tuple a<b) ----
OVERRIDES = {
    ("EC0003", "EC0097"): R(SO, conf="MEDIUM", note="김명신 체포: 병영이 잡음(이형원) vs 장교 일행이 김명신·김갑득을 잡아옴(이진욱, 3월 4일)."),
    ("EC0089", "EC0104"): R(SO, conf="HIGH", note="자미덕 체포: 이진욱 등 장교가 잡음(이진욱) vs 병영 장교가 붙잡아 감(자미덕)."),
    ("EC0150", "EC0151"): R(SO, conf="MEDIUM", review=True,
                            note="같은 날 구순 처분: '외딴 섬 정배'와 '신지도 정배'는 같은 왕명의 두 표현일 가능성. 집행 기록 아님."),
    ("EC0048", "EC0049"): R(RV, conf="LOW", note="같은 날 같은 문답의 조사 명령과 안핵어사 차하: 하나의 임명 행위인지 별개 명령인지 원문 확인 필요."),
    ("EC0076", "EC0098"): R(RV, conf="LOW", cond="SAME_OCCURRENCE_IF_IDENTITY_HOLDS", dep="장교 1명=조계완 (근거 없음)",
                            note="명업이 말한 '찾아온 장교 한 명'과 조계완의 구순 집 방문: 동일인 근거가 없어 판정 보류."),
    ("EC0012", "EC0013"): R(SU, CP, "MEDIUM"),
    ("EC0154", "EC0155"): R(TR, conf="HIGH", note="6/13 파직 → 6/16 유임: 서로 다른 처분이며 모순이 아님."),
    ("EC0023", "EC0045"): R(TR, conf="MEDIUM", note="5/12와 5/27의 의금부 구금·신문 왕명: 반복 명령."),
    ("EC0112", "EC0113"): R(TR, conf="MEDIUM", note="대질 사건과 그 대질 중의 거짓 발언(구성 사건). 같은 event로 묶지 않음."),
    ("EC0018", "EC0135"): R(CP, conf="MEDIUM", note="이광섭이 믿은 말이 허황(이형원) vs 구순의 과장·아전의 거짓 보고를 믿음(홍대협): 일치 방향."),
    ("EC0019", "EC0137"): R(SI, CP, "MEDIUM"),
    ("EC0017", "EC0142"): R(SI, CP, "MEDIUM", note="이문협이 병영 비장에게 수사를 맡김(이형원) vs 병영 비장 지휘대로 죄를 얽음(홍대협)."),
}

CONCEPTS = {
    "THEFT": ["도난", "도적", "화적", "좀도둑", "훔침", "잃은 물건", "도둑"],
    "DEATH": ["사망", "죽"], "JISE": ["지세"], "GOODS": ["장물"], "ARREST": ["잡", "체포", "붙잡"],
    "INTERROGATION": ["신문", "조사", "물음", "물었"], "PUNISH": ["정배", "유배", "파직", "형장", "감죄", "처분"],
    "COACH": ["사주", "지휘", "꾀", "석방", "거짓"], "MOTIVE": ["앙심", "원한", "모함", "미워"],
    "CONFRONT": ["대질"], "LIST": ["이름", "성명"], "FOOD": ["밥", "떡"], "ROOM": ["방안"],
    "RELATION": ["왕래", "친숙", "이웃", "비판", "힐책", "아는 사이", "가객"],
}
ATTRIBUTION_TYPES = {"CAUSE_ATTRIBUTION", "TEMPORAL_ATTRIBUTION", "PLACE_ATTRIBUTION", "PURPOSE_ATTRIBUTION"}
SUMMARY_GROUPS = ["THEFT_REALITY", "DEATH_CAUSE", "JISE_ORIGIN", "COACHING", "MOTIVE", "HAN_GUSUN_RELATION"]
ISSUE_FOR_SUMMARY = {"THEFT_REALITY": "THEFT_REALITY", "DEATH_CAUSE": "DEATH", "JISE_ORIGIN": "JISE_ORIGIN",
                     "COACHING": "COACHING", "MOTIVE": "MOTIVE", "HAN_GUSUN_RELATION": "HAN_GUSUN_RELATION"}
PENDING = {"AP0002": "THEFT_REALITY", "AP0047": "THEFT_REALITY", "AP0126": "THEFT_REALITY"}

log = logging.getLogger("v2_same_event")


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


def compat(a, b):
    if not a and not b:
        return "BOTH_UNSPECIFIED"
    if not a or not b:
        return "ONE_UNSPECIFIED"
    return "SAME" if a == b else f"DIFFERENT({a} / {b})"


def polarity_relation(pa, pb):
    if pa == pb:
        return f"SAME({pa})"
    if {pa, pb} == {"AFFIRMED", "NEGATED"}:
        return "OPPOSITE(AFFIRMED/NEGATED)"
    return f"MIXED({pa}/{pb})"


def main():
    OUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(LOG_DIR / "v2_same_event_review.log", mode="w", encoding="utf-8"),
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
    cands = fetch(con, """SELECT c.*, s.speaker, s.speaker_chain, s.attestation_depth AS support_depth,
                                 a.parent_prop_id, a.record_lunar_date, a.attestation_mode
                          FROM historical_event_candidates c
                          JOIN event_candidate_support s USING (event_candidate_id)
                          JOIN atomic_propositions a ON a.atomic_prop_id = c.origin_atomic_prop_id
                          ORDER BY c.event_candidate_id""")
    er = fetch(con, "SELECT * FROM entity_resolution_candidates")
    raw = fetch(con, "SELECT named_entities FROM source_faithful_propositions")
    membership = [r["person"] for r in fetch(con, "SELECT person FROM person_membership")]
    by_id = {c["event_candidate_id"]: c for c in cands}

    unknown_tags = sorted((set(ISSUE) | set(CHAIN)) - set(by_id))
    if unknown_tags:
        log.error("Tags refer to unknown candidates: %s", unknown_tags)
        sys.exit(1)

    lexicon = set(membership)
    for r in raw:
        lexicon.update(x for x in r["named_entities"].split("|") if x)
    for e in er:
        lexicon.add(e["surface_form"].split("(")[0])
        lexicon.add(e["candidate_entity"].split("(")[0])
    lexicon.update(["도적", "정조", "병영", "충청병영"])
    lexicon = sorted(lexicon, key=len, reverse=True)

    def entities(c, field_text):
        out = set()
        assumed = set()
        for sf in surface_forms(field_text, lexicon):
            name = sf
            for e in er:
                if e["surface_form"].split("(")[0] == sf and c["parent_prop_id"] in e["source_prop_ids"].split("|"):
                    if e["resolution_status"] == "DIRECTLY_IDENTIFIED_IN_SOURCE":
                        name = e["candidate_entity"]
                    elif e["resolution_status"] == "STRONGLY_SUPPORTED":
                        assumed.add(f"{sf}={e['candidate_entity']}")
                        out.add(e["candidate_entity"].split("(")[0])
            out.add(name)
        return out, assumed

    feats = {}
    for c in cands:
        subj, subj_assumed = entities(c, c["subject_surface"])
        allent, all_assumed = entities(c, " ".join([c["subject_surface"], c["predicate"], c["object_surface"]]))
        text = c["subject_surface"] + " " + c["predicate"] + " " + c["object_surface"]
        concepts = {k for k, words in CONCEPTS.items() if any(w in text for w in words)}
        feats[c["event_candidate_id"]] = dict(subj=subj, ent=allent, assumed=subj_assumed | all_assumed,
                                              concepts=concepts)

    # ---- pair generation ----
    pairs = []
    for a, b in itertools.combinations(sorted(by_id), 2):
        ca, cb, fa, fb = by_id[a], by_id[b], feats[a], feats[b]
        reasons = []
        if ca["shared_utterance_group"] and ca["shared_utterance_group"] == cb["shared_utterance_group"]:
            reasons.append(f"SHARED_UTTERANCE_GROUP:{ca['shared_utterance_group']}")
        if ca["conflict_group"] and ca["conflict_group"] == cb["conflict_group"]:
            reasons.append(f"CONFLICT_GROUP:{ca['conflict_group']}")
        if ca["claim_topic"] == cb["claim_topic"]:
            reasons.append(f"CLAIM_TOPIC:{ca['claim_topic']}")
        shared_open = set(filter(None, ca["open_set_ids"].split("|"))) & set(filter(None, cb["open_set_ids"].split("|")))
        if shared_open:
            reasons.append(f"OPEN_SET:{'|'.join(sorted(shared_open))}")
        if ca["historical_place"] and ca["historical_place"] == cb["historical_place"]:
            reasons.append(f"PLACE:{ca['historical_place']}")
        if ca["occurrence_lunar_text"] and ca["occurrence_lunar_text"] == cb["occurrence_lunar_text"]:
            reasons.append(f"TIME:{ca['occurrence_lunar_text']}")
        shared_concepts = fa["concepts"] & fb["concepts"]
        shared_subj = (fa["subj"] & fb["subj"]) - {"정조"}
        shared_ent = (fa["ent"] & fb["ent"]) - {"정조"}
        if shared_subj and ca["event_type"] == cb["event_type"]:
            reasons.append(f"SUBJECT+EVENT_TYPE:{'|'.join(sorted(shared_subj))}/{ca['event_type']}")
        if shared_ent and shared_concepts:
            reasons.append(f"ENTITY+CONCEPT:{'|'.join(sorted(shared_ent))}/{'|'.join(sorted(shared_concepts))}")
        if ISSUE.get(a, (None,))[0] and ISSUE.get(a, (None,))[0] == ISSUE.get(b, (None,))[0] and not reasons:
            reasons.append("ANALYTIC_ISSUE_TAG_ONLY")
        if reasons:
            pairs.append((a, b, reasons))

    # ---- classification ----
    gen_rows, review_rows = [], []
    for i, (a, b, reasons) in enumerate(pairs, 1):
        pid = f"PR{i:04d}"
        ca, cb, fa, fb = by_id[a], by_id[b], feats[a], feats[b]
        same_ug = bool(ca["shared_utterance_group"]) and ca["shared_utterance_group"] == cb["shared_utterance_group"]
        same_parent = ca["parent_prop_id"] == cb["parent_prop_id"]
        ia, ib = ISSUE.get(a), ISSUE.get(b)
        cha, chb = CHAIN.get(a), CHAIN.get(b)
        basis = ""
        rule = None
        if (a, b) in OVERRIDES:
            rule, basis = OVERRIDES[(a, b)], "PAIR_OVERRIDE"
        elif ia and ib and ia[0] == ib[0]:
            rule = ISSUE_RULES.get(ia[0], {}).get(K(ia[1], ib[1]))
            basis = f"ISSUE:{ia[0]}({ia[1]}~{ib[1]})"
            if rule is None and ia[1] != ib[1] and ia[0] == "DEATH":
                rule = R(DI, conf="HIGH", note="occurrence/cause/time/place 중 서로 다른 facet이거나 다른 인물 — 같은 event로 묶지 않음.")
            if rule is None:
                rule = ISSUE_DEFAULT
        elif cha and chb and cha[0] == chb[0]:
            basis = f"CHAIN:{cha[0]}({cha[1]}~{chb[1]})"
            rule = R(TR, conf="MEDIUM", note="같은 서술 흐름 안의 다른 단계. 시간 edge는 만들지 않음.") if cha[1] != chb[1] \
                else R(RV, conf="LOW", note="같은 단계로 태그되었으나 개별 판정 규칙 없음.")
        else:
            basis = "DEFAULT"
            rule = R(DI, conf="MEDIUM", note="공유 특징은 있으나 같은 사건·쟁점 근거 없음.")

        primary, secondary = rule["primary"], rule["secondary"]
        if same_ug and primary != SU:
            secondary = secondary or (primary if primary not in (SO,) else DI)
            if primary == SO:
                secondary = DI
            primary = SU
            basis += "+SHARED_UTTERANCE_GROUP"
        elif same_ug and primary == SU and not secondary:
            secondary = DI

        dep = rule["dep"]
        id_assumption = sorted(fa["assumed"] | fb["assumed"]) if any(r.startswith("SUBJECT") or r.startswith("ENTITY")
                                                                       for r in reasons) else []
        if id_assumption and not dep:
            dep = ("pair generation only used STRONGLY_SUPPORTED identity (classification does not depend on it): "
                   + ", ".join(id_assumption))
        if primary == SO and dep.startswith("pair generation only"):
            rule = dict(rule, review=True)
        review = rule["review"] if rule["review"] is not None else (
            primary == RV or secondary == RV or bool(rule["cond"]) or any(t in dep for t in NON_DIRECT_TAGS))

        subj_status = "SAME_SURFACE" if ca["subject_surface"] == cb["subject_surface"] else (
            "SAME_ENTITY" if fa["subj"] & fb["subj"] else "DIFFERENT")
        if subj_status == "SAME_ENTITY" and (fa["assumed"] | fb["assumed"]):
            subj_status = "SAME_IF_IDENTITY_ASSUMED"
        et = "SAME" if ca["event_type"] == cb["event_type"] else f"DIFFERENT({ca['event_type']}/{cb['event_type']})"
        if ia and ib and ia[0] == ib[0]:
            issue_status = "SAME_ISSUE" if ia[1] == ib[1] or primary not in (DI,) else f"RELATED_FACET({ia[1]}/{ib[1]})"
        elif ia or ib:
            issue_status = "DIFFERENT_OR_UNTAGGED"
        else:
            issue_status = "UNTAGGED"
        time_c = compat(ca["occurrence_lunar_text"], cb["occurrence_lunar_text"])
        rel_a, rel_b = ca["relative_time_text"], cb["relative_time_text"]
        if rel_a or rel_b:
            time_c += f"; relative({rel_a or '-'} / {rel_b or '-'})"
        place_c = compat(ca["historical_place"], cb["historical_place"])
        note_parts = [rule["note"], f"basis={basis}"]
        if same_parent:
            note_parts.append(f"SAME_PARENT_PROPOSITION={ca['parent_prop_id']}")
        relation_class = primary + (f"+{secondary}" if secondary else "")
        gen_rows.append([pid, a, b, "; ".join(reasons)])
        review_rows.append(dict(
            pair_id=pid, candidate_a=a, candidate_b=b, relation_class=relation_class, primary_relation=primary,
            secondary_relation=secondary, conditional_relation=rule["cond"],
            same_parent_proposition="TRUE" if same_parent else "FALSE", same_subject_status=subj_status,
            same_event_type_status=et, same_issue_status=issue_status,
            polarity_relation=polarity_relation(ca["polarity"], cb["polarity"]),
            entity_identity_dependency=dep or "NONE", time_compatibility=time_c, place_compatibility=place_c,
            reason=" ".join(x for x in note_parts if x), confidence=rule["conf"],
            manual_review_required="YES" if review else "NO", _open_set=rule["open_set"],
        ))

    # ---- conflict group summary ----
    summary = []
    for group in SUMMARY_GROUPS:
        issue = ISSUE_FOR_SUMMARY[group]
        members = [c for c in cands if c["conflict_group"] == group or ISSUE.get(c["event_candidate_id"], ("",))[0] == issue]
        if group == "DEATH_CAUSE":
            members = [c for c in members if c["conflict_group"] == "DEATH_CAUSE" or
                       ISSUE.get(c["event_candidate_id"], ("", ""))[1].startswith(("KIM_", "WIFE_"))]
        for c in members:
            mode = c["attestation_mode"]
            depth = int(c["support_depth"])
            src_type = ("ROYAL" if mode.startswith("ROYAL") else
                        "OFFICIAL" if depth == 1 and mode in ("OFFICIAL_REPORT", "INSPECTOR_REPORT", "OFFICIAL_FINDING",
                                                              "OFFICIAL_EVALUATION") else
                        "EMBEDDED_TESTIMONY" if depth >= 2 else "TESTIMONY")
            basis = "RAW_CONFLICT_GROUP" if c["conflict_group"] == group else f"ANALYTIC_ISSUE_TAG({ISSUE[c['event_candidate_id']][1]})"
            if c["conflict_group"] == group and c["event_candidate_id"] in ISSUE:
                basis += f"; kind={ISSUE[c['event_candidate_id']][1]}"
            summary.append([group, c["event_candidate_id"], c["record_lunar_date"], c["speaker_chain"], c["event_type"],
                            f"{c['subject_surface']} | {c['predicate']}", c["polarity"], src_type,
                            f"{c['epistemic_status']}; membership={basis}"])
        for ap, g in PENDING.items():
            if g == group:
                summary.append([group, "", "", "", "", "", "", "",
                                f"projection-stage review pending: {ap} (event candidate 없음, 이번 분석 제외)"])

    # ---- validation ----
    ids = set(by_id)
    bad_ref = [r["pair_id"] for r in review_rows if r["candidate_a"] not in ids or r["candidate_b"] not in ids]
    check("S01", "존재하지 않는 candidate 참조 0", not bad_ref, "|".join(bad_ref))
    selfp = [r["pair_id"] for r in review_rows if r["candidate_a"] == r["candidate_b"]]
    check("S02", "self-pair 0", not selfp, "|".join(selfp))
    keys = [frozenset((r["candidate_a"], r["candidate_b"])) for r in review_rows]
    check("S03", "동일 pair 중복 0", len(keys) == len(set(keys)), f"pairs={len(keys)}")
    pol_bad = [r["pair_id"] for r in review_rows
               if r["polarity_relation"] != polarity_relation(by_id[r["candidate_a"]]["polarity"],
                                                              by_id[r["candidate_b"]]["polarity"])
               or (r["primary_relation"] == SO and (by_id[r["candidate_a"]]["polarity"] != "AFFIRMED"
                                                    or by_id[r["candidate_b"]]["polarity"] != "AFFIRMED"))
               or (CT in (r["primary_relation"], r["secondary_relation"])
                   and "DOUBTED" in r["polarity_relation"])]
    check("S04", "polarity 손실 0 (SAME_OCCURRENCE는 AFFIRMED끼리만, DOUBTED를 모순 근거로 쓰지 않음)", not pol_bad,
          "|".join(pol_bad))
    id_bad = [r["pair_id"] for r in review_rows
              if any(t in r["entity_identity_dependency"] for t in ("(CANDIDATE)", "(UNRESOLVED)", "근거 없음"))
              and (r["primary_relation"] in (SO, CT) or r["secondary_relation"] == CT
                   or r["manual_review_required"] != "YES")]
    id_bad += [r["pair_id"] for r in review_rows if "STRONGLY_SUPPORTED, identity assumption" in r["entity_identity_dependency"]
               and r["manual_review_required"] != "YES"]
    id_bad += [r["pair_id"] for r in review_rows if r["entity_identity_dependency"].startswith("pair generation only")
               and CT in (r["primary_relation"], r["secondary_relation"])]
    id_bad += [r["pair_id"] for r in review_rows if r["entity_identity_dependency"].startswith("pair generation only")
               and r["primary_relation"] == SO and r["manual_review_required"] != "YES"]
    check("S05", "entity candidate를 자동 확정한 사례 0", not id_bad, "|".join(id_bad))
    occ_bad = [r["pair_id"] for r in review_rows if r["primary_relation"] == SO and (
        by_id[r["candidate_a"]]["event_type"] != by_id[r["candidate_b"]]["event_type"]
        or by_id[r["candidate_a"]]["event_type"] in ATTRIBUTION_TYPES)]
    check("S06", "occurrence와 attribution을 같은 event로 오분류 0", not occ_bad, "|".join(occ_bad))
    su_bad = [r["pair_id"] for r in review_rows
              if by_id[r["candidate_a"]]["shared_utterance_group"]
              and by_id[r["candidate_a"]]["shared_utterance_group"] == by_id[r["candidate_b"]]["shared_utterance_group"]
              and (r["primary_relation"] != SU or r["secondary_relation"] == SO)]
    check("S07", "shared utterance component를 same occurrence로 오분류 0", not su_bad, "|".join(su_bad))
    os_bad = [r["pair_id"] for r in review_rows if r["_open_set"] and
              (CT in (r["primary_relation"], r["secondary_relation"]) or "비구성원이다" in r["reason"])]
    check("S08", "OPEN_SET 때문에 비구성원 추론 0 (open-set 근거 pair에서 CONTRADICTORY 없음)", not os_bad, "|".join(os_bad))
    rel_bad = [r["pair_id"] for r in review_rows if r["primary_relation"] not in RELATIONS
               or (r["secondary_relation"] and r["secondary_relation"] not in RELATIONS)]
    check("S09", "relation 값이 정의된 집합 안", not rel_bad, "|".join(rel_bad))
    miss_summary = [f"{g}:{c['event_candidate_id']}" for g in SUMMARY_GROUPS for c in cands
                    if c["conflict_group"] == g and not any(s[0] == g and s[1] == c["event_candidate_id"] for s in summary)]
    check("S10", "raw conflict_group candidate가 모두 17 요약에 포함", not miss_summary, "|".join(miss_summary))
    check("S11", "REVIEW_REQUIRED projection 3건은 candidate 없이 pending으로만 기록",
          sum(1 for s in summary if s[8].startswith("projection-stage review pending")) == 3 and
          not any(c["origin_atomic_prop_id"] in PENDING for c in cands))
    stale = sorted(k for k in OVERRIDES if frozenset(k) not in set(keys))
    checks.append(["S12", "생성되지 않은 pair에 대한 override", "INFO" if stale else "PASS", "|".join(f"{a}-{b}" for a, b in stale)])

    # ---- write ----
    rev_cols = ["pair_id", "candidate_a", "candidate_b", "relation_class", "primary_relation", "secondary_relation",
                "conditional_relation", "same_parent_proposition", "same_subject_status", "same_event_type_status",
                "same_issue_status", "polarity_relation", "entity_identity_dependency", "time_compatibility",
                "place_compatibility", "reason", "confidence", "manual_review_required"]
    write_csv(OUT_DIR / "15_v2_candidate_pair_generation.csv",
              ["pair_id", "candidate_a", "candidate_b", "pair_generation_reason"], gen_rows)
    write_csv(OUT_DIR / "16_v2_same_event_review.csv", rev_cols, [[r[k] for k in rev_cols] for r in review_rows])
    write_csv(OUT_DIR / "17_v2_conflict_group_summary.csv",
              ["conflict_group", "candidate_id", "source_date", "speaker", "event_type", "predicate", "polarity",
               "epistemic_source_type", "notes"], summary)
    for table, fn in [("candidate_pair_generation", "15_v2_candidate_pair_generation.csv"),
                      ("same_event_review", "16_v2_same_event_review.csv"),
                      ("conflict_group_summary", "17_v2_conflict_group_summary.csv")]:
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv(?, header=true, all_varchar=true, "
                    f"quote='\"', escape='\"')", [str(OUT_DIR / fn)])
    digests_after = {t: table_digest(con, t) for t in PROTECTED_TABLES}
    con.close()
    changed = [t for t in PROTECTED_TABLES if digests_before[t] != digests_after[t]]
    check("S13", "raw·기존 derived table 불변", not changed, "|".join(changed))
    check("S14", "raw CSV SHA-256 불변", all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items()))
    checks.append(["S15", "projection-stage review pending", "INFO", "AP0002|AP0047|AP0126 — 이번 분석 제외"])
    write_csv(OUT_DIR / "18_v2_same_event_validation.csv", ["check_id", "description", "severity", "detail"], checks)

    count = {}
    for r in review_rows:
        count[r["primary_relation"]] = count.get(r["primary_relation"], 0) + 1
    sec = {}
    for r in review_rows:
        if r["secondary_relation"]:
            sec[r["secondary_relation"]] = sec.get(r["secondary_relation"], 0) + 1
    log.info("generated pairs: %d", len(pairs))
    log.info("primary: %s", dict(sorted(count.items())))
    log.info("secondary: %s", dict(sorted(sec.items())))
    log.info("manual review: %d", sum(1 for r in review_rows if r["manual_review_required"] == "YES"))
    n_err = sum(1 for c in checks if c[2] == "ERROR")
    log.info("validation: ERROR=%d WARNING=%d", n_err, sum(1 for c in checks if c[2] == "WARNING"))
    if n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
