#!/usr/bin/env python3
"""GuSoon v2 world-aware temporal / procedural DAG template (no sampling).

The DAG is not a possible world. It is one component of a world W: given W's
historical facts, identity / same-occurrence / interpretation hypotheses and
judgment states, it says which real occurrences exist and how they are ordered
in time or procedure.

This stage builds only a template:
  - node candidates (output/36): every one of the 155 event candidates is
    classified, plus one judgment-ACT node per judgment state (17). Historical
    fact booleans H_* are never nodes; they are activation conditions of the
    occurrence nodes that realize them. Attributes (cause, scale, place, time,
    responsibility, evaluation, list membership, judgment content) are never
    nodes. Same-occurrence candidates and uncertain identities are never merged
    in the template.
  - edge candidates (output/37): temporal / procedural only (no causal edge).
    Every edge has an explicit basis: a claimed date, a court-entry date of a
    court act, a relative-time phrase that is in the text, an explicit
    procedural link, or an explicit order->execution link. Narrative order is
    never a basis. "HARD" means "no condition beyond the existence of both
    nodes"; it is used only between court / procedural act nodes.
  - world materialization rules (output/38) and materialize(world), validated
    on hand-specified test worlds (not sampling, not enumeration).

Record date, claimed occurrence time and historical occurrence time are kept
apart. A record date is used as a time anchor only for a court act whose act IS
the dated entry (a royal order / ministerial request / judgment / in-court
report recorded in that day's entry). It is never copied onto an event that the
record merely reports.

Usage:
  python3 scripts/v2_09_dag_template.py                 # build + validate + write
  python3 scripts/v2_09_dag_template.py --mutation NAME # inject a fault, validate, write nothing
"""

import argparse
import csv
import hashlib
import importlib.util
import logging
import re
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "database" / "gusun_v2.duckdb"
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
SHA_PATH = RAW_DIR / "gusun_research_v2_SHA256SUMS.txt"
NEW_TABLES = ["dag_node_projection", "temporal_edge_candidates", "world_dag_materialization_rules"]
OUT_NODES, OUT_EDGES, OUT_RULES = ("36_v2_dag_node_projection.csv", "37_v2_temporal_edge_candidates.csv",
                                   "38_v2_world_dag_materialization_rules.csv")
OUT_VALID, OUT_SUMMARY = "39_v2_dag_validation.csv", "40_v2_dag_template_summary.csv"
MUTATIONS = ["cause_as_node", "record_date_copied", "narrative_order_edge", "exile_execution_node",
             "force_merge_hanbijang", "cycle_abca", "same_nontransitive"]

_spec = importlib.util.spec_from_file_location("v2_07", ROOT / "scripts" / "v2_07_world_logic_reaudit.py")
_v2_07 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v2_07)
parse_formula = _v2_07.parse

MAT, INV, SPJ, ORD = ("MATERIAL_EVENT_NODE", "INVESTIGATIVE_EVENT_NODE", "SPEECH_OR_JUDGMENT_EVENT_NODE",
                      "ORDER_EVENT_NODE")
ATTR, REV = "ATTRIBUTE_ONLY", "REVIEW_REQUIRED"
NODE_CLASSES = (MAT, INV, SPJ, ORD)
ALL_CLASSES = NODE_CLASSES + (ATTR, REV)

BEFORE, AFTER, DURING, PREC, TRIG = ("TEMPORAL_BEFORE", "TEMPORAL_AFTER", "TEMPORAL_DURING", "PROCEDURAL_PRECEDES",
                                     "PROCEDURAL_TRIGGER_IF_EXPLICIT")
EDGE_TYPES = (BEFORE, AFTER, DURING, PREC, TRIG)
STRICT_TYPES = (BEFORE, PREC, TRIG)  # a -> b means a ends before b starts (AFTER is normalized away)
HARD, CTEMP, CID, CSAME, EVID, REVE = ("HARD_TEMPORAL", "CONDITIONAL_TEMPORAL", "CONDITIONAL_ON_IDENTITY",
                                       "CONDITIONAL_ON_SAME_OCCURRENCE", "EVIDENCE_ONLY", "REVIEW_REQUIRED")
EDGE_KINDS = (HARD, CTEMP, CID, CSAME, EVID, REVE)
COND_KINDS = (CTEMP, CID, CSAME)
NEVER_KINDS = (EVID, REVE)

# basis types. Activatable edges need one of ACTIVE_BASES; REVIEW / EVIDENCE edges cite NONACTIVE_BASES.
TEXT_BASES = ("RELATIVE_TIME_TEXT", "PROCEDURAL_EXPLICIT", "ORDER_EXECUTION_EXPLICIT")
DATE_BASES = ("CLAIMED_DATE_ORDER", "COURT_ENTRY_DATE_ORDER", "CLAIMED_VS_COURT_DATE_ORDER")
ACTIVE_BASES = TEXT_BASES + DATE_BASES + ("JUDGMENT_REVISION",)
NONACTIVE_BASES = ("SERIAL_CONNECTIVE", "REPLY_REFERENCE", "ANAPHORIC_REFERENCE", "SAME_DAY_COURT_SEQUENCE",
                   "REFERENT_NOT_IN_OWN_SOURCE", "ROLE_LINK_WITHOUT_TIME_WORD")
HARD_BASES = ("COURT_ENTRY_DATE_ORDER", "PROCEDURAL_EXPLICIT", "JUDGMENT_REVISION")


# ---------------------------------------------------------------- formulas (same conventions as v2_08)
def V(n):
    return ("var", n)


def Not(x):
    return ("not", x)


def And(*xs):
    return ("and",) + xs


def Imp(a, b):
    return ("imp", a, b)


def Eq(v, val):
    return ("eq", v, val)


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
        return f"{f[1]} = {'TRUE' if f[2] is True else 'FALSE' if f[2] is False else f[2]}"
    if k == "lt":
        return f"{f[1]} < {f[2]}"
    if k == "in":
        return f"{f[1]} ∈ [{f[2]}]"
    raise ValueError(k)


def render_old(f):
    """Render exactly as v2_08 wrote output/33 (for the parse round-trip check)."""
    k = f[0]
    if k == "eq":
        return f"{f[1]} = {f[2]}"
    if k in ("var", "lt", "in"):
        return render(f)
    if k == "not":
        return "¬" + render_old(f[1])
    if k == "and":
        return "(" + " ∧ ".join(render_old(x) for x in f[1:]) + ")"
    if k == "imp":
        return f"({render_old(f[1])} → {render_old(f[2])})"
    if k == "iff":
        return f"({render_old(f[1])} ↔ {render_old(f[2])})"
    raise ValueError(k)


def vars_of(f):
    k = f[0]
    if k in ("var", "eq", "in"):
        return {f[1]}
    if k == "lt":
        return {f[1], f[2]}
    return set().union(*(vars_of(x) for x in f[1:]))


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


# ---------------------------------------------------------------- lunar time intervals (minutes, 1793)
def day_base(m, d):
    return ((m - 1) * 31 + (d - 1)) * 1440


INF = 10 ** 9


def interval(text):
    """Interval [start, end) for a lunar time text. '밤' = that date's evening to midnight; '새벽' = after
    midnight (the source writes '2월 28일 밤~29일 새벽' separately, EC0084). DAY = the whole date."""
    t = text.strip()
    m = re.fullmatch(r"1793-(\d\d)-(\d\d)", t)
    if m:
        b = day_base(int(m[1]), int(m[2]))
        return (b, b + 1440)
    m = re.fullmatch(r"1793-(\d\d)-(\d\d) 밤", t)
    if m:
        b = day_base(int(m[1]), int(m[2]))
        return (b + 18 * 60, b + 1440)
    m = re.fullmatch(r"1793-(\d\d)-(\d\d) 밤~(\d\d) 새벽", t)
    if m:
        b = day_base(int(m[1]), int(m[2]))
        return (b + 18 * 60, day_base(int(m[1]), int(m[3])) + 6 * 60)
    m = re.fullmatch(r"1793-(\d\d) 초순", t)
    if m:
        return (day_base(int(m[1]), 1), day_base(int(m[1]), 10) + 1440)
    m = re.fullmatch(r"1793-(\d\d) 초순 이후", t)
    if m:
        return (day_base(int(m[1]), 1), INF)
    raise ValueError(f"unparsed time text: {text}")


def strictly_before(a, b):
    return a[1] <= b[0]


# ---------------------------------------------------------------- node classification (hand-assigned)
# ec: (class, action_core, note). ATTRIBUTE_ONLY notes say what the attribute attaches to.
CLASS = {
    "EC0001": (ATTR, "거주지 속성", "구순의 인물 속성(거주). 부착: 구순."),
    "EC0002": (SPJ, "고발 발언(김명신=도적 괴수)", "발언 행위만 node. '도적 괴수'라는 내용은 node 아님."),
    "EC0003": (MAT, "체포(김명신)", "충청병영의 체포. 날짜 주장 없음."),
    "EC0004": (MAT, "구금(김명신, 병영)", "occurrence는 H_KIM_DETAINED_BY_BYEONGYEONG가 참인 world에만. '달포 이상' 기간은 E_EC0004의 속성."),
    "EC0005": (INV, "조사(김명신)", "병영의 조사 행위."),
    "EC0006": (ATTR, "수사 결과 속성(확실한 장물 미발견)", "부정 서술: 일어난 occurrence가 아님. 부착: 병영 수사."),
    "EC0007": (MAT, "사망(김명신)", "이형원 기록의 사망 referent."),
    "EC0008": (ATTR, "시간 귀속(사망이 구금·조사 뒤)", "시간 속성. 독립 node가 아니라 구금·조사 → 사망 conditional edge의 조건(E_EC0008)."),
    "EC0009": (MAT, "형벌 가함(평민들)", "'모진'은 평가 속성."),
    "EC0010": (ATTR, "평가(형벌 받은 평민들이 무고)", "평가 상태. 부착: EC0009."),
    "EC0011": (ATTR, "관계 상태(구순·김명신 원한)", "관계·동기 속성."),
    "EC0012": (REV, "도난 상황 꾸밈(주장된 행위)", "FABSCOPE_EC0012: 전체 조작이면 별도 행위, 과장이면 구순 정소의 속성 → node/attribute 결정 보류."),
    "EC0013": (ATTR, "평가(누명 = 허위 고발)", "고발 행위 자체는 DN_EC0002. '누명'(허위성)은 그 행위의 속성."),
    "EC0014": (ATTR, "수단 속성(행랑 하인을 통함)", "부착: 누명 씌우기(EC0013) 방식."),
    "EC0015": (ATTR, "수단 속성(교졸을 통함)", "부착: 누명 씌우기(EC0013) 방식."),
    "EC0016": (ATTR, "집단 속성(체포자들 = 미워하던 사람들)", "명단·집단 membership 속성."),
    "EC0017": (INV, "수사 위임(이문협 → 병영 비장)", "'병영 비장'→한가 UNRESOLVED: 동일성은 W에서만."),
    "EC0018": (ATTR, "평가(이광섭이 믿은 말이 허황)", "평가 상태."),
    "EC0019": (MAT, "체포(이광섭 지휘, 대상 미특정)", "'무고한·잘못'은 평가 속성. 대상이 특정되지 않은 체포."),
    "EC0020": (SPJ, "계청(이광섭 파직·나문 요청)", "비변사의 조정 발언 행위."),
    "EC0021": (ORD, "윤허(이광섭 처분)", "명령 행위만. 집행 기록 없음 → 집행 node 없음."),
    "EC0022": (ATTR, "판단 내용(도난 자체가 없었다는 방향)", "판단 내용. 부착: DN_J_JEONGJO_17930512_THEFT(판단 act)."),
    "EC0023": (ORD, "명령(구순 의금부 수금·엄사)", "명령 행위만. 집행 기록 없음 → 집행 node 없음."),
    "EC0024": (ATTR, "판단 내용(화적 설명 의심)", "DOUBTED. 부착: DN_J_IJOWON_17930527_THEFT."),
    "EC0025": (ATTR, "관계 상태(이웃)", "관계 속성."),
    "EC0026": (SPJ, "비판 발언(김명신 → 구순 행실)", "SAME 후보 EC0072(편지 힐책)와는 W에서만 collapse."),
    "EC0027": (ATTR, "심리 상태(앙심)", "동기 속성."),
    "EC0028": (ATTR, "원인 귀속(앙심이 비판 때문)", "원인 속성."),
    "EC0029": (ATTR, "의도 상태(모함하려 함)", "동기 속성."),
    "EC0030": (REV, "도난 상황 꾸밈(주장된 행위)", "FABSCOPE_EC0030: EC0012와 같은 이유로 node/attribute 결정 보류."),
    "EC0031": (MAT, "지세랑 호칭 창작(주장된 행위)", "SENSE_EC0031=COINED_TERM일 때만 H_JISE_TERM_COINED_BY_GUSUN과 연결되므로 활성 조건은 E_EC0031."),
    "EC0032": (SPJ, "호칭 유포 발언", "유포 행위."),
    "EC0033": (MAT, "궤짝 돈 도난 위장(주장된 행위)", "특정 위장 행위 주장."),
    "EC0034": (ATTR, "상태(하인 흔적 = 부스럼)", "부착: EC0035 대상."),
    "EC0035": (MAT, "흔적 위장(부스럼 → 창상)", "특정 위장 행위 주장."),
    "EC0036": (MAT, "사망(김명신)", "이조원 기록의 사망 referent."),
    "EC0037": (ATTR, "장소 속성(사망 장소 병영 옥)", "부착: 김명신 사망 node. H_KIM_DEATH_IN_BYEONGYEONG_PRISON."),
    "EC0038": (ATTR, "원인·책임 귀속(구순이 구성한 죄안 때문)", "사인/책임 속성. 부착: 김명신 사망 node. CAUSELEVEL_EC0038에 따라 다른 사실."),
    "EC0039": (MAT, "사망(김명신의 아내)", "occurrence는 H_KIM_WIFE_DIED가 참인 world에만."),
    "EC0040": (ATTR, "시간 귀속(김명신이 죽은 뒤)", "시간 속성. 김명신 사망 → 아내 사망 conditional edge의 조건(E_EC0040)."),
    "EC0041": (ATTR, "부정된 행위(병사가 자세히 조사함)", "부정 서술: occurrence 아님."),
    "EC0042": (INV, "수사 위임(병사 → 하급 보조자)", "하급 보조자 동일성은 미정(UNRESOLVED)."),
    "EC0043": (ATTR, "관계 상태(하급 보조자가 구순의 가객)", "관계 속성."),
    "EC0044": (ORD, "명령(이조원 파직)", "명령 행위만. 집행 기록 없음."),
    "EC0045": (ORD, "명령(구순 의금부 수금·반복 신문)", "명령 행위만. 집행 기록 없음."),
    "EC0046": (ATTR, "판단 내용(도난이 없었다는 방향)", "부착: DN_J_IJOWON_17930527_THEFT."),
    "EC0047": (ATTR, "판단 내용(예전 호중 화적도 지세랑 사용)", "습관적 사용(상태) 내용. 부착: DN_J_HONG_17930528_JISE."),
    "EC0048": (ORD, "명령(홍대협에게 내려가 조사해 오라)", "안핵 명령."),
    "EC0049": (ORD, "명령(홍대협 공주 안핵어사 차하)", "안핵 임명."),
    "EC0050": (MAT, "도적을 만남(구순)", "INTERP_EC0050_MEANS_ROBBED가 참일 때만 도난 사실과 연결 → 활성 조건은 E_EC0050."),
    "EC0051": (MAT, "호출(구순 → 영교)", ""),
    "EC0052": (MAT, "명단 작성·교부(김명신 등)", "명단 membership은 속성."),
    "EC0053": (MAT, "사망(김명신)", "윤노동 기록의 사망 referent."),
    "EC0054": (ATTR, "사인 귀속(병)", "사인 속성. 부착: 김명신 사망 node."),
    "EC0055": (ATTR, "시간 귀속(체포·구금 뒤)", "같은 기록(SRC2_005)에 체포·구금 candidate가 없어 referent 변수 없음 → EVIDENCE_ONLY edge만."),
    "EC0056": (MAT, "형벌 가함(여러 죄수)", "'참혹한'은 평가 속성."),
    "EC0057": (ATTR, "부정된 결과(진정한 장물 없음)", "부정 서술: occurrence 아님."),
    "EC0058": (MAT, "회유(한재욱 → 변가의 처)", "occurrence는 H_HAN_JAEUK_COAXED_BYEONGA_CHEO가 참인 world에만. 변가의 처=자미덕은 CANDIDATE."),
    "EC0059": (SPJ, "공초 진술(변가의 처)", "공초 발언 행위. 내용('김명신이 도적 괴수')은 node 아님."),
    "EC0060": (ATTR, "결과 귀속(꾀어 그 공초를 내게 함)", "회유 → 공초의 연결 claim. edge 조건(E_EC0060)으로만 쓰며 인과 edge로 만들지 않음."),
    "EC0061": (SPJ, "계청(복명 전 처리 보류)", "비변사의 조정 발언 행위."),
    "EC0062": (ORD, "윤허(보류)", "명령 행위만."),
    "EC0063": (INV, "안핵 신문(홍대협, 공주목)", "복명(6/13) 안의 서술. 6/13은 이 신문의 날짜가 아님."),
    "EC0064": (ATTR, "인물 관계 상태(명업)", "인물 속성."),
    "EC0065": (SPJ, "알림 발언(나복 → 명업)", "주장 날짜는 INTERP_EC0065_DATE_IS_TELLING_TIME가 참일 때만 이 발화의 시점."),
    "EC0066": (MAT, "침입(도적)", "도난과 독립(침입했으나 훔치지 않은 world 가능)."),
    "EC0067": (ATTR, "규모 속성(도적 30여 명)", "부착: 침입 node. H_GUSUN_LARGE_ARMED_BAND_INTRUDED."),
    "EC0068": (ATTR, "방식 속성(횃불을 들고)", "부착: 침입 node."),
    "EC0069": (SPJ, "자칭 발언(도적: 지세대감)", "발언 행위."),
    "EC0070": (MAT, "도난(돈·물품)", "THEFT_OCCURRENCE_NODE. 존재 여부는 H_GUSUN_THEFT_OCCURRED가 결정. '돈과 물품'·'2/22 밤'은 E_EC0070의 내용."),
    "EC0071": (ATTR, "관계 상태(친숙·왕래)", "관계 속성."),
    "EC0072": (MAT, "서찰 발송·힐책(김명신 → 구순)", "서찰 전달 occurrence."),
    "EC0073": (MAT, "왕래 단절(상태 개시)", "상태가 시작된 시점을 갖는 node('그 뒤'의 대상). 상태 구간 node로 둠."),
    "EC0074": (SPJ, "정소(소장 제출)", "구순의 정소 행위."),
    "EC0075": (ORD, "체포령 발령", "명령 행위만. 발령 주체 미상."),
    "EC0076": (MAT, "사적 접촉(구순 ↔ 장교 1명)", "장교 1명=조계완은 ID_JANGGYO_1MYEONG__JOGYEWAN(근거 약함)."),
    "EC0077": (SPJ, "공초 진술(명업, 처음 사실대로)", ""),
    "EC0078": (ATTR, "심리 상태(위협이 두려움)", "부착: 명업."),
    "EC0079": (SPJ, "진술 번복(명업)", "번복 발언 행위. 내용('도적이 없었다')은 node 아님."),
    "EC0080": (ATTR, "원인 귀속(위협이 두려워 번복)", "원인 속성."),
    "EC0081": (MAT, "호출(병영 → 이진욱)", ""),
    "EC0082": (ORD, "지시(덕평으로 출동)", "명령 행위만."),
    "EC0083": (ORD, "지시(변지돌·정원돌 체포)", "명령 행위만. 실제로는 자미덕만 잡힘(EC0089) → 이 명령의 집행 node 없음."),
    "EC0084": (MAT, "철편 제작·지급", ""),
    "EC0085": (ATTR, "인물 관계(처남매부)", "인물 속성."),
    "EC0086": (ATTR, "인물 속성(힘이 셈)", "인물 속성."),
    "EC0087": (SPJ, "경고 발언(조심하라)", ""),
    "EC0088": (ATTR, "구금 상태(변지돌 이미 잡혀감)", "앞선 체포 사건은 candidate가 없으므로 node를 만들지 않음(latent event 금지)."),
    "EC0089": (MAT, "체포(자미덕)", "이진욱 진술의 체포 referent."),
    "EC0090": (ATTR, "범위 속성(잡은 사람이 자미덕뿐)", "membership 속성."),
    "EC0091": (ATTR, "인물 관계(재돌의 처)", "인물 속성."),
    "EC0092": (ATTR, "인물 관계(변지돌의 아우)", "인물 속성."),
    "EC0093": (INV, "현장 탐문(구순 집, 도난 상황 질문)", ""),
    "EC0094": (SPJ, "피해 진술 발언(잃은 물건 열거)", "발언 행위."),
    "EC0095": (SPJ, "전언 발언(도적이 지세대사라 자칭)", "발언 행위."),
    "EC0096": (ORD, "지시(풍각·흥덕 김생원 체포)", "풍각 김생원=김명신, 흥덕 김생원=김갑득은 원문 직접 식별(DIRECTLY_IDENTIFIED)이라 그대로 사용."),
    "EC0097": (MAT, "체포(김명신·김갑득)", "'병사 분부에 따라' → EC0096 명령의 실행 기록."),
    "EC0098": (MAT, "방문(조계완 → 구순 집)", ""),
    "EC0099": (SPJ, "질문 발언(구순: 왜 다시 왔나)", ""),
    "EC0100": (SPJ, "응답 발언(조계완: 풍각의 상주를 잡으러)", ""),
    "EC0101": (SPJ, "반응 발언(구순)", ""),
    "EC0102": (MAT, "서찰 전달 요구·교부(구순 → 조계완)", "서찰 전달 occurrence."),
    "EC0103": (MAT, "체류 상태(재돌 아산)", "상태 구간 node('자미덕 체포 전'의 주체)."),
    "EC0104": (MAT, "체포·압송(자미덕)", "자미덕 진술의 체포 referent. SAME 후보 EC0089와는 W에서만 collapse."),
    "EC0105": (INV, "신문(자미덕)", ""),
    "EC0106": (MAT, "구류(자미덕, 다모방)", ""),
    "EC0107": (MAT, "호출 접촉(한 비장 → 자미덕, 매일)", "한 비장=한재욱은 CANDIDATE(ID_HANBIJANG__HANJAEUK). 행위자 통합은 W에서만."),
    "EC0108": (SPJ, "발언(남편 재돌 체포 고지)", "내용 속 '재돌 체포'는 node 아님."),
    "EC0109": (SPJ, "회유 발화(조건부 석방 제안)", "UG_P0081 한 발화의 act node. occurrence는 H_HANBIJANG_CONDITIONAL_RELEASE_OFFER(조건·약속 둘 다 참)가 결정."),
    "EC0110": (ATTR, "발화 구성요소(석방 약속 부분)", "같은 발화(UG_P0081)의 약속 부분. 부착: DN_EC0109. 약속된 '다음 날 석방'은 집행 기록이 없어 node 아님."),
    "EC0111": (MAT, "음식 제공(한 비장 → 자미덕)", ""),
    "EC0112": (MAT, "대질(자미덕 ↔ 이집거)", "occurrence는 H_JAMIDEOK_IJIPGEO_CONFRONTATION가 참인 world에만."),
    "EC0113": (SPJ, "거짓 진술(대질 중, 자미덕)", "occurrence는 H_JAMIDEOK_FALSE_STATEMENT_AT_CONFRONTATION가 참인 world에만."),
    "EC0114": (MAT, "지휘(한 비장 → 자미덕 거짓 발언)", "occurrence는 H_HANBIJANG_DIRECTED_JAMIDEOK_FALSE_STATEMENT가 참인 world에만."),
    "EC0115": (INV, "파견(한재욱 → 유제희)", "탐문 파견."),
    "EC0116": (ATTR, "목적 귀속(도적 진상 탐지)", "목적 속성. 부착: DN_EC0115."),
    "EC0117": (INV, "명단 작성·보고(유제희)", "명단 membership은 속성."),
    "EC0118": (INV, "염탐(유제희)", ""),
    "EC0119": (MAT, "호출 접촉(한재욱 → 자미덕)", ""),
    "EC0120": (MAT, "음식 제공(한재욱 → 자미덕)", ""),
    "EC0121": (SPJ, "전언 발언(유제희: 석단 공초 내용)", ""),
    "EC0122": (SPJ, "권고 발언(유제희: 자미덕에게 다시 물어보라)", ""),
    "EC0123": (INV, "재질문(한재욱 → 자미덕)", ""),
    "EC0124": (ATTR, "원인 귀속(재질문이 유제희 말에 따름)", "EC0122 → EC0123 procedural edge의 조건(E_EC0124)으로만 사용."),
    "EC0125": (SPJ, "응답 발언(자미덕: 모른다)", ""),
    "EC0126": (ATTR, "부인 내용(은밀한 사주 없음)", "DENIED 내용. 부착: DN_J_HANJAEUK_17930613_COACHING."),
    "EC0127": (ATTR, "부인 내용(구순과 모르는 사이)", "DENIED 내용. 부착: DN_J_HANJAEUK_17930613_COACHING."),
    "EC0128": (INV, "탐문(유제희, 현지)", ""),
    "EC0129": (SPJ, "발언(구순: 풍각 김상제 수상)", ""),
    "EC0130": (INV, "기록·보고(유제희)", ""),
    "EC0131": (ATTR, "판단 내용(약간의 도난은 실제)", "부착: DN_J_HONG_17930613_THEFT."),
    "EC0132": (ATTR, "판단 내용(좀도둑 수준)", "규모 평가. 부착: DN_J_HONG_17930613_THEFT."),
    "EC0133": (ATTR, "평가(구순이 과장함)", "구순 정소의 방식 평가."),
    "EC0134": (SPJ, "보고 행위(아전)", "'거짓'은 그 보고의 속성. 아전=유제희는 CANDIDATE."),
    "EC0135": (ATTR, "심리 상태(이광섭이 믿음)", "부착: 이광섭."),
    "EC0136": (ATTR, "상황 속성(장물 없는 상태에서)", "부착: DN_EC0137 판단 행위."),
    "EC0137": (SPJ, "판단 행위(이광섭: 큰 도적으로 판단)", "판단 act만 node. '큰 도적'이라는 내용은 node 아님."),
    "EC0138": (ATTR, "사인 귀속(질병)", "사인 속성. 부착: 김명신 사망 node."),
    "EC0139": (ATTR, "부정된 행위(장물부터 확보함)", "부정 서술: occurrence 아님."),
    "EC0140": (MAT, "체포(평민, 장교·나졸 동원)", ""),
    "EC0141": (INV, "수사 지휘(병영 비장)", "병영 비장=한가는 CANDIDATE."),
    "EC0142": (INV, "죄안 구성(이문협)", "'얽음'은 평가 속성."),
    "EC0143": (ATTR, "판단 내용(도난이 실제로 있었음)", "부착: DN_J_JEONGJO_17930613_THEFT."),
    "EC0144": (ATTR, "사인 귀속(전염병)", "사인 속성. 부착: 김명신 사망 node."),
    "EC0145": (ATTR, "사인 귀속(아내, 전염병)", "사인 속성. 부착: 아내 사망 node."),
    "EC0146": (ATTR, "판단 내용(곤장 맞지 않음)", "부정 내용. 부착: DN_J_JEONGJO_17930613_KIM_DEATH."),
    "EC0147": (ATTR, "판단 내용(평범한 신문도 받지 않음)", "부정 내용. 부착: DN_J_JEONGJO_17930613_KIM_DEATH."),
    "EC0148": (ATTR, "판단 내용(예전 좀도둑도 쓰던 말)", "부착: DN_J_JEONGJO_17930613_JISE."),
    "EC0149": (ATTR, "판단 내용(호칭 창작 죄 면함)", "부착: DN_J_JEONGJO_17930613_JISE."),
    "EC0150": (ORD, "처분 명령(구순 감사 정배)", "명령 행위만. 정배 집행 기록 없음 → 집행 node 없음."),
    "EC0151": (ORD, "처분 명령(구순 신지도 정배)", "명령 행위만. 정배 집행 기록 없음 → 집행 node 없음."),
    "EC0152": (ORD, "처분 명령(이광섭 영동현 유배)", "명령 행위만. 집행 기록 없음."),
    "EC0153": (ORD, "처분 명령(한가 형장 후 노비)", "명령 내용 속 '형장 친 뒤'는 미래 집행 순서이므로 edge 근거가 아님. 집행 node 없음."),
    "EC0154": (ORD, "명령(이형원 파직)", "명령 행위만."),
    "EC0155": (ORD, "처분(이형원 유임)", "명령 행위만."),
}

# occurrence candidates whose node is keyed by a historical occurrence fact (activation H = TRUE).
# Only unconditional ASSERTS_TRUE mappings (E ↔ H, E → H, or the conjunctive utterance) to EVENT_OCCURRENCE facts.
FACT_KEY = {
    "EC0004": "H_KIM_DETAINED_BY_BYEONGYEONG", "EC0007": "H_KIM_MYEONGSIN_DIED", "EC0036": "H_KIM_MYEONGSIN_DIED",
    "EC0053": "H_KIM_MYEONGSIN_DIED", "EC0039": "H_KIM_WIFE_DIED", "EC0070": "H_GUSUN_THEFT_OCCURRED",
    "EC0058": "H_HAN_JAEUK_COAXED_BYEONGA_CHEO", "EC0109": "H_HANBIJANG_CONDITIONAL_RELEASE_OFFER",
    "EC0112": "H_JAMIDEOK_IJIPGEO_CONFRONTATION", "EC0113": "H_JAMIDEOK_FALSE_STATEMENT_AT_CONFRONTATION",
    "EC0114": "H_HANBIJANG_DIRECTED_JAMIDEOK_FALSE_STATEMENT",
}

# judgment-act nodes: (is the record date the date of the act itself?, reason)
J_TIME = {
    "J_LEEHYEONGWON_17930512_THEFT": (False, "장계는 충청도에서 작성·발송된 문서. 1793-05-12는 실록이 장계 접수·처분을 기록한 날이며 장계 작성(판단) 시점은 그 이전일 수 있어 날짜 anchor로 쓰지 않음."),
    "J_LEEHYEONGWON_17930512_KIM_DEATH": (False, "장계는 충청도에서 작성·발송된 문서. 1793-05-12는 접수·처분 기록일이라 날짜 anchor로 쓰지 않음."),
    "J_JEONGJO_17930512_THEFT": (True, "실록 1793-05-12 기사 자체가 정조의 이 판단 행위 기록."),
    "J_IJOWON_17930527_THEFT": (True, "비변사등록·실록 1793-05-27 기사가 이조원이 조정에 아뢴 행위(복명) 자체를 기록."),
    "J_IJOWON_17930527_KIM_DEATH": (True, "비변사등록 1793-05-27 기사가 이조원이 아뢴 행위 자체를 기록."),
    "J_IJOWON_17930527_JISE": (True, "비변사등록 1793-05-27 기사가 이조원이 아뢴 행위 자체를 기록."),
    "J_HONG_17930528_JISE": (True, "승정원일기 1793-05-28 조정 문답 기록(발언 행위 자체)."),
    "J_YUNNODONG_17930611_KIM_DEATH": (False, "별단은 문서. 1793-06-11은 비변사가 별단을 처리한 기록일이며 별단 작성·제출 시점은 그 이전일 수 있음."),
    "J_YUNNODONG_17930611_COACHING": (False, "별단은 문서. 1793-06-11은 비변사가 별단을 처리한 기록일."),
    "J_HONG_17930613_THEFT": (True, "실록 1793-06-13 '안핵어사 홍대협 복명' 기사 자체가 복명 행위 기록."),
    "J_HONG_17930613_KIM_DEATH": (True, "실록 1793-06-13 복명 기사 자체가 복명 행위 기록."),
    "J_HONG_17930613_JISE": (True, "실록 1793-06-13 복명 기사 자체가 복명 행위 기록."),
    "J_JEONGJO_17930613_THEFT": (True, "실록 1793-06-13 기사 자체가 정조의 최종 심리 행위 기록."),
    "J_JEONGJO_17930613_KIM_DEATH": (True, "실록 1793-06-13 기사 자체가 정조의 최종 심리 행위 기록."),
    "J_JEONGJO_17930613_JISE": (True, "실록 1793-06-13 기사 자체가 정조의 최종 심리 행위 기록."),
    "J_JAMIDEOK_17930613_COACHING": (False, "공초는 안핵 중 받은 진술. 6/13은 복명에 수록된 기록일(공초 시점은 그 이전)."),
    "J_HANJAEUK_17930613_COACHING": (False, "공초는 안핵 중 받은 진술. 6/13은 복명에 수록된 기록일(공초 시점은 그 이전)."),
}
# court-act candidates whose act IS the dated entry (royal order / ministerial request recorded that day)
COURT_EC = ["EC0020", "EC0021", "EC0023", "EC0044", "EC0045", "EC0048", "EC0049", "EC0061", "EC0062",
            "EC0150", "EC0151", "EC0152", "EC0153", "EC0154", "EC0155"]

# display-only actor aliases applied in materialize() when the identity is TRUE in W
ID_ALIAS = {
    "ID_HANBIJANG__HANJAEUK": ("한 비장", "한재욱"), "ID_HANBIJANG__HANGA": ("한 비장", "한가"),
    "ID_HANGA__HANJAEUK": ("한가", "한재욱"), "ID_BYEONGSA_SRC2_006__IGWANGSEOP": ("병사", "이광섭"),
    "ID_BYEONGA_CHEO__JAMIDEOK": ("변가의 처", "자미덕"), "ID_BIJANG_P0103__HANGA": ("병영 비장", "한가"),
}


PERSON_PRIORITY = ["한재욱", "이광섭", "자미덕", "김명신", "김갑득", "한가"]  # display name for an identity class


def dn(x):
    return "DN_" + x


def E(ec):
    return V(f"E_{ec}")


# ---------------------------------------------------------------- explicit edges (hand-assigned)
# (from, to, type, kind, condition or None, [(basis_type, phrase, refs)], strength, review, note)
def explicit_edges():
    J = lambda s: dn(s)  # noqa: E731
    HONG13 = ["J_HONG_17930613_THEFT", "J_HONG_17930613_KIM_DEATH", "J_HONG_17930613_JISE"]
    JEONGJO13 = ["J_JEONGJO_17930613_THEFT", "J_JEONGJO_17930613_KIM_DEATH", "J_JEONGJO_17930613_JISE"]
    out = []

    def add(frm, to, etype, kind, cond, bases, strength, review, note):
        out.append(dict(frm=frm, to=to, etype=etype, kind=kind, cond=cond, bases=bases, strength=strength,
                        review=review, note=note))

    # relative-time claims (mirror RC0324–RC0330; claim TRUE ∧ referent hypothesis TRUE)
    rel = [("EC0004", "EC0007", "EC0008", "REF_EC0008_DETENTION__EC0004", "구금·조사 뒤", "RC0324"),
           ("EC0005", "EC0007", "EC0008", "REF_EC0008_INVESTIGATION__EC0005", "구금·조사 뒤", "RC0325"),
           ("EC0036", "EC0039", "EC0040", "REF_EC0040_KIMDEATH__EC0036", "김명신이 죽은 뒤", "RC0326"),
           ("EC0072", "EC0073", "EC0073", "REF_EC0073_THEN__EC0072", "그 뒤", "RC0327"),
           ("EC0103", "EC0104", "EC0103", "REF_EC0103_ARREST__EC0104", "자미덕 체포 전", "RC0328"),
           ("EC0105", "EC0106", "EC0106", "REF_EC0106_INTERROGATION__EC0105", "신문 뒤", "RC0329"),
           ("EC0106", "EC0107", "EC0107", "REF_EC0107_AFTER__EC0106", "그 후", "RC0330")]
    for a, b, claim, ref, phrase, rc in rel:
        add(dn(a), dn(b), BEFORE, CTEMP, And(E(claim), V(ref)), [("RELATIVE_TIME_TEXT", phrase, [claim])], "MEDIUM", True,
            f"{claim}의 상대시간 표현이 (referent {ref} 포함) 참인 world에서만. 정확한 날짜는 만들지 않음. 논리층 {rc}와 같은 조건.")
    add(dn("EC0077"), dn("EC0079"), BEFORE, CTEMP, And(E("EC0077"), E("EC0079")),
        [("RELATIVE_TIME_TEXT", "처음에는", ["EC0077"])], "MEDIUM", True,
        "같은 명제(P0055) 안 '처음에는 … 바꾸었다'. referent 변수가 따로 없어 검토 표시.")
    add(dn("EC0113"), dn("EC0112"), DURING, CTEMP, V("H_JAMIDEOK_FALSE_STATEMENT_AT_CONFRONTATION"),
        [("RELATIVE_TIME_TEXT", "이집거와 대질할 때", ["EC0113"])], "MEDIUM", False,
        "거짓 진술이 대질 중에 일어났다는 사실(H)이 참일 때. DURING은 포함 관계이며 선후 edge가 아님.")
    # explicit order -> execution / procedural links inside testimonies (conditional on the claims)
    add(dn("EC0096"), dn("EC0097"), TRIG, CID, And(E("EC0096"), E("EC0097"), V("ID_BYEONGSA_SRC2_006__IGWANGSEOP")),
        [("ORDER_EXECUTION_EXPLICIT", "병사 분부에 따라", ["EC0097"])], "MEDIUM", False,
        "명령 → 그 명령에 따른 체포. EC0097의 '병사'=이광섭(STRONGLY_SUPPORTED)은 가설이므로 조건에 포함. 대상(풍각·흥덕 김생원=김명신·김갑득)은 원문 직접 식별.")
    add(dn("EC0074"), dn("EC0075"), TRIG, CTEMP, And(E("EC0074"), E("EC0075")),
        [("PROCEDURAL_EXPLICIT", "그 소장으로", ["EC0075"])], "MEDIUM", False, "정소 → 그 소장에 따른 체포령(명업 진술).")
    add(dn("EC0122"), dn("EC0123"), TRIG, CTEMP, And(E("EC0122"), E("EC0123"), E("EC0124")),
        [("PROCEDURAL_EXPLICIT", "유제희 말에 따른", ["EC0124"])], "MEDIUM", False,
        "유제희의 권고 → 그 말에 따른 재질문. 연결 자체가 claim(EC0124)이라 조건에 포함.")
    add(dn("EC0058"), dn("EC0059"), TRIG, CTEMP, E("EC0060"),
        [("PROCEDURAL_EXPLICIT", "꾀어 그 공초를 내게 함", ["EC0060"])], "MEDIUM", False,
        "회유 → 그 공초. 연결 claim(EC0060)이 참일 때만. 시간 순서만 표현하며 인과 edge가 아님.")
    add(dn("EC0141"), dn("EC0142"), TRIG, CTEMP, And(E("EC0141"), E("EC0142")),
        [("PROCEDURAL_EXPLICIT", "병영 비장 지휘대로", ["EC0142"])], "MEDIUM", False, "지휘 → 지휘대로 한 죄안 구성(홍대협 평가).")
    add(dn("EC0048"), dn("EC0063"), TRIG, CTEMP, And(E("EC0048"), E("EC0063")),
        [("ORDER_EXECUTION_EXPLICIT", "내려가 자세히 조사해 오라", ["EC0048"]),
         ("ORDER_EXECUTION_EXPLICIT", "안핵어사 홍대협 복명", ["SRC2_006"])], "MEDIUM", True,
        "안핵 명령 → 안핵 신문. 신문은 복명(6/13) 안의 서술이고 날짜가 없으므로 claim 조건부. '명에 따라' 같은 직접 표현 대신 직함·복명 연결.")
    add(dn("EC0049"), dn("EC0063"), TRIG, CTEMP, And(E("EC0049"), E("EC0063")),
        [("ORDER_EXECUTION_EXPLICIT", "안핵어사", ["EC0049", "SRC2_006"])], "MEDIUM", True,
        "공주 안핵어사 차하 → 공주목 안핵 신문.")
    for h in HONG13:
        add(dn("EC0063"), J(h), PREC, CTEMP, E("EC0063"),
            [("PROCEDURAL_EXPLICIT", "안핵 복명", ["EC0061", "SRC2_006"])], "MEDIUM", False,
            "안핵(신문)을 마친 뒤 복명. 신문의 날짜는 만들지 않음(6/13 기록일을 복사하지 않음).")
    # court / procedural chain (HARD: no condition beyond the existence of both act nodes)
    for j in ("J_LEEHYEONGWON_17930512_THEFT", "J_LEEHYEONGWON_17930512_KIM_DEATH"):
        add(J(j), J("J_JEONGJO_17930512_THEFT"), PREC, HARD, None,
            [("PROCEDURAL_EXPLICIT", "장계·조사에 따라", ["P0016"])], "STRONG", False,
            "정조 5/12 판단은 이형원 장계·조사에 따른 것(장계 → 판단). 장계 자체의 날짜는 만들지 않음.")
    for j in ("J_YUNNODONG_17930611_KIM_DEATH", "J_YUNNODONG_17930611_COACHING"):
        add(J(j), dn("EC0061"), PREC, HARD, None,
            [("PROCEDURAL_EXPLICIT", "윤노동 별단의 구순 사건 처리를 보류", ["EC0061"])], "STRONG", False,
            "별단 → 그 별단의 처리 보류 계청.")
    add(dn("EC0020"), dn("EC0021"), PREC, HARD, None, [("PROCEDURAL_EXPLICIT", "처분 요청을 윤허", ["EC0021"])], "STRONG",
        False, "같은 날(5/12) 계청 → 윤허. 윤허가 그 요청을 직접 가리킴.")
    add(dn("EC0061"), dn("EC0062"), PREC, HARD, None, [("PROCEDURAL_EXPLICIT", "보류 요청을 윤허", ["EC0062"])], "STRONG",
        False, "같은 날(6/11) 계청 → 윤허.")
    for h in HONG13:
        add(dn("EC0061"), J(h), BEFORE, HARD, None, [("PROCEDURAL_EXPLICIT", "안핵 복명 전", ["EC0061"])], "STRONG", False,
            "6/11 보류 계청은 홍대협 복명 전.")
        for o in ("EC0048", "EC0049"):
            add(dn(o), J(h), PREC, HARD, None, [("PROCEDURAL_EXPLICIT", "안핵어사 홍대협 복명", ["SRC2_006"])], "STRONG", False,
                "5/28 안핵 명령 → 6/13 그 안핵의 복명.")
        for g in JEONGJO13:
            add(J(h), J(g), PREC, HARD, None,
                [("PROCEDURAL_EXPLICIT", "복명과 정조의 최종 심리", ["SRC2_006"]),
                 ("PROCEDURAL_EXPLICIT", "공주목 안핵의 핵심을", ["P0104"])], "STRONG", False,
                "같은 날(6/13) 복명 → 그 안핵에 대한 정조의 심리. 같은 날 순서의 근거는 기사 구조가 '복명에 대한 심리'라는 명시.")
    add(J("J_JEONGJO_17930512_THEFT"), J("J_JEONGJO_17930613_THEFT"), PREC, HARD, None,
        [("JUDGMENT_REVISION", "REVISED_BY", ["JR001"])], "STRONG", False,
        "판단 act의 수정 관계(내용끼리 연결하지 않음). 5/12 판단 act → 6/13 판단 act.")
    add(J("J_HONG_17930528_JISE"), J("J_HONG_17930613_JISE"), PREC, HARD, None,
        [("JUDGMENT_REVISION", "REVISED_BY", ["JR002"])], "STRONG", True,
        "판단 act의 수정 관계. 수정인지 정밀화인지는 JR002에서 REVIEW(시간 순서는 기사일로 고정).")
    add(dn("EC0154"), dn("EC0155"), BEFORE, HARD, None, [("PROCEDURAL_EXPLICIT", "파직 후", ["P0115"])], "STRONG", False,
        "6/13 파직 → 6/16 유임.")
    # EVIDENCE_ONLY: the source states an order but it cannot be enforced
    for a in ("EC0003", "EC0004"):
        add(dn(a), dn("EC0053"), BEFORE, EVID, None,
            [("REFERENT_NOT_IN_OWN_SOURCE", "체포·구금 뒤", ["EC0055"])], "WEAK", True,
            "윤노동(SRC2_005)의 '체포·구금 뒤'. 그 기록 안에 체포·구금 candidate가 없어 referent 변수가 없음 → 시간 제약으로 강제하지 않음.")
    # REVIEW_REQUIRED: plausible order, but no explicit time word / referent variable
    rv = [("EC0003", "EC0004", "SERIAL_CONNECTIVE", "잡아 달포 이상 구금", ["P0004"], "연결어미 '-아'의 계기 의미뿐(상대시간 단어 아님)."),
          ("EC0003", "EC0005", "SERIAL_CONNECTIVE", "잡아 달포 이상 구금·조사", ["P0004"], "연결어미 '-아'의 계기 의미뿐."),
          ("EC0051", "EC0052", "SERIAL_CONNECTIVE", "영교를 불러 김명신 등의 이름을 써 주었다", ["P0039"], "연결어미 '-어'의 계기 의미뿐."),
          ("EC0119", "EC0120", "SERIAL_CONNECTIVE", "방안으로 불러 남은 밥을 주었다", ["P0089"],
           "연결어미 '-어'의 계기 의미뿐. 두 node는 같은 SAME component라 장면 단위 collapse 시 self-loop가 됨."),
          ("EC0099", "EC0100", "REPLY_REFERENCE", "답함", ["EC0100"], "응답이 어느 질문을 가리키는지 referent 변수가 없음(같은 날)."),
          ("EC0123", "EC0125", "REPLY_REFERENCE", "재질문에 모른다고 답함", ["EC0125"], "'재질문'=EC0123 referent 변수가 없음."),
          ("EC0089", "EC0093", "SERIAL_CONNECTIVE", "자미덕을 데리고", ["P0063"], "같은 날(2/29). '데리고'는 시간 단어가 아님."),
          ("EC0114", "EC0113", "SERIAL_CONNECTIVE", "한 비장의 지휘에 따라", ["P0084"], "지휘가 발언보다 앞섰는지 동시였는지 불명."),
          ("EC0098", "EC0097", "ROLE_LINK_WITHOUT_TIME_WORD", "잡으러 가는 길에", ["EC0098"],
           "들른 뒤 잡으러 간 체포가 EC0097인지, 조계완이 '장교 일행'에 속하는지(open set) 미정."),
          ("EC0129", "EC0130", "ANAPHORIC_REFERENCE", "그 말을", ["EC0130"], "'그 말'=EC0129 referent 변수가 없음."),
          ("EC0115", "EC0128", "ROLE_LINK_WITHOUT_TIME_WORD", "당초", ["EC0128"], "서로 다른 공초(한재욱·유제희). 같은 파견인지 미정.")]
    for a, b, bt, phrase, refs, why in rv:
        add(dn(a), dn(b), BEFORE, REVE, None, [(bt, phrase, refs)], "WEAK", True, why)
    for j in ("J_JAMIDEOK_17930613_COACHING", "J_HANJAEUK_17930613_COACHING"):
        add(J(j), dn("EC0063"), DURING, REVE, None, [("ROLE_LINK_WITHOUT_TIME_WORD", "관련자들을 차례로 신문함", ["EC0063"])],
            "WEAK", True, "이 공초가 홍대협 안핵 신문 중에 받은 것인지 명시 없음(공초 시점은 6/13 이전으로만 기록).")
    add(J("J_IJOWON_17930527_THEFT"), dn("EC0044"), PREC, REVE, None,
        [("SAME_DAY_COURT_SEQUENCE", "직접 안핵하지 않은 점", ["P0029"])], "WEAK", True,
        "같은 날(5/27). 복명에 대한 처분으로 보이나 명시 연결어가 없고 P0029(AP0047)는 projection REVIEW.")
    add(J("J_IJOWON_17930527_THEFT"), dn("EC0045"), PREC, REVE, None,
        [("SAME_DAY_COURT_SEQUENCE", "엄핵을 청함", ["SRC2_002"])], "WEAK", True,
        "같은 날(5/27). '엄핵 청함' 발언은 candidate가 없음.")
    add(J("J_JEONGJO_17930613_JISE"), dn("EC0150"), PREC, REVE, None,
        [("SAME_DAY_COURT_SEQUENCE", "사형에서 감해", ["P0110"])], "WEAK", True,
        "같은 날(6/13). '죄를 면함' 판단에 따른 감형 처분으로 보이나 명시 연결어 없음.")
    return out


# ---------------------------------------------------------------- hand-specified test worlds (validation only)
T, F = True, False
W_DEATH = {
    "H_KIM_MYEONGSIN_DIED": T, "E_EC0007": T, "E_EC0036": T, "E_EC0053": T,
    "SAME_EC0007_EC0036": T, "SAME_EC0007_EC0053": T, "SAME_EC0036_EC0053": T,
    "H_KIM_DETAINED_BY_BYEONGYEONG": T, "E_EC0004": T, "E_EC0003": T, "E_EC0005": T,
    "E_EC0096": T, "E_EC0097": T, "SAME_EC0003_EC0097": T, "ID_BYEONGSA_SRC2_006__IGWANGSEOP": T,
    "E_EC0008": T, "H_KIM_DEATH_AFTER_DETENTION": T, "REF_EC0008_DETENTION__EC0004": T,
    "REF_EC0008_INVESTIGATION__EC0005": T, "E_EC0055": T,
    "H_KIM_WIFE_DIED": T, "E_EC0039": T, "E_EC0040": T, "H_KIM_WIFE_DIED_AFTER_KIM": T, "REF_EC0040_KIMDEATH__EC0036": T,
    "E_EC0054": T, "E_EC0138": T, "H_KIM_DEATH_CAUSE_DISEASE": T, "E_EC0144": T, "H_KIM_DEATH_CAUSE_EPIDEMIC": T,
    "E_EC0037": T, "H_KIM_DEATH_IN_BYEONGYEONG_PRISON": T,
    "J_LEEHYEONGWON_17930512_KIM_DEATH": T, "J_IJOWON_17930527_KIM_DEATH": T, "J_YUNNODONG_17930611_KIM_DEATH": T,
    "J_HONG_17930613_KIM_DEATH": T, "J_JEONGJO_17930613_KIM_DEATH": T,
}
W_THEFT_COMMON = {
    "J_LEEHYEONGWON_17930512_THEFT": T, "J_JEONGJO_17930512_THEFT": T, "J_IJOWON_17930527_THEFT": T,
    "J_HONG_17930613_THEFT": T, "J_JEONGJO_17930613_THEFT": T,
    "E_EC0023": T, "E_EC0044": T, "E_EC0045": T, "E_EC0048": T, "E_EC0049": T, "E_EC0063": T, "E_EC0061": T,
    "E_EC0062": T, "E_EC0150": T, "E_EC0151": T, "SAME_EC0150_EC0151": T,
    "E_EC0065": T, "INTERP_EC0065_DATE_IS_TELLING_TIME": T,
}
W_THEFT_TRUE = dict(W_THEFT_COMMON, **{
    "H_GUSUN_THEFT_OCCURRED": T, "E_EC0070": T, "E_EC0066": T, "E_EC0069": T, "E_EC0143": T, "E_EC0022": F,
    "E_EC0046": F, "E_EC0131": T, "E_EC0132": T})
W_THEFT_FALSE = dict(W_THEFT_COMMON, **{
    "H_GUSUN_THEFT_OCCURRED": F, "E_EC0070": F, "E_EC0066": F, "E_EC0069": F, "E_EC0143": F, "E_EC0022": T,
    "E_EC0046": T, "E_EC0131": F, "E_EC0132": F})
W_JAMI = {
    "E_EC0081": T, "E_EC0082": T, "E_EC0083": T, "E_EC0089": T, "E_EC0103": T, "REF_EC0103_ARREST__EC0104": T,
    "E_EC0104": T, "SAME_EC0089_EC0104": T, "E_EC0105": T, "E_EC0106": T, "REF_EC0106_INTERROGATION__EC0105": T,
    "E_EC0107": T, "REF_EC0107_AFTER__EC0106": T, "E_EC0108": T, "E_EC0109": T, "E_EC0110": T,
    "H_HANBIJANG_CONDITIONAL_RELEASE_OFFER": T, "E_EC0111": T, "E_EC0112": T, "H_JAMIDEOK_IJIPGEO_CONFRONTATION": T,
    "E_EC0113": T, "H_JAMIDEOK_FALSE_STATEMENT_AT_CONFRONTATION": T, "E_EC0114": T,
    "H_HANBIJANG_DIRECTED_JAMIDEOK_FALSE_STATEMENT": T, "E_EC0119": T, "E_EC0120": T, "E_EC0122": T, "E_EC0123": T,
    "E_EC0124": T, "E_EC0125": T, "J_JAMIDEOK_17930613_COACHING": T, "J_HANJAEUK_17930613_COACHING": T,
    "E_EC0153": T, "OCCURRENCE_GRANULARITY_ACT_LEVEL": F, "SAME_EC0107_EC0111": F, "SAME_EC0119_EC0120": F,
}
W_JAMI_ID_TRUE = dict(W_JAMI, **{
    "ID_HANBIJANG__HANJAEUK": T, "ID_HANGA__HANJAEUK": T, "ID_HANBIJANG__HANGA": T,
    "SAME_EC0107_EC0119": T, "SAME_EC0111_EC0120": T, "SAME_EC0107_EC0120": F, "SAME_EC0111_EC0119": F,
    "H_HAN_JAEUK_INSTIGATED_JAMIDEOK": T, "E_EC0126": F})
W_JAMI_ID_FALSE = dict(W_JAMI, **{
    "ID_HANBIJANG__HANJAEUK": F, "ID_HANGA__HANJAEUK": T, "ID_HANBIJANG__HANGA": F,
    "SAME_EC0107_EC0119": F, "SAME_EC0111_EC0120": F, "SAME_EC0107_EC0120": F, "SAME_EC0111_EC0119": F,
    "H_HAN_JAEUK_INSTIGATED_JAMIDEOK": F, "E_EC0126": T})

# name: (description, world, temporal assignment, expectations)
TEST_WORLDS = [
    ("TW01_KIM_DEATH", "김명신 사망 skeleton: 사망 3 referent SAME, 구금 뒤 사망 claim 참", W_DEATH, None, dict(
        logic="VALID", temporal="VALID",
        classes=[["DN_EC0007", "DN_EC0036", "DN_EC0053"], ["DN_EC0003", "DN_EC0097"]],
        edges=[("DN_EC0004", "DN_EC0007"), ("DN_EC0005", "DN_EC0007"), ("DN_EC0036", "DN_EC0039"),
               ("DN_EC0096", "DN_EC0003"), ("DN_J_IJOWON_17930527_KIM_DEATH", "DN_J_HONG_17930613_KIM_DEATH"),
               ("DN_J_HONG_17930613_KIM_DEATH", "DN_J_JEONGJO_17930613_KIM_DEATH"),
               ("DN_EC0097", "DN_J_IJOWON_17930527_KIM_DEATH")],
        no_edges=[("DN_EC0003", "DN_EC0004")],
        inactive=["DN_EC0054", "DN_EC0138", "DN_EC0144", "DN_EC0037", "DN_EC0038", "DN_EC0008", "DN_EC0055"],
        no_link=[("DN_EC0007", "J_")])),
    ("TW02_KIM_DEATH_AFTER_FALSE", "'구금 뒤 사망' claim이 거짓인 world: 구금·사망 선후 모름", dict(
        W_DEATH, **{"E_EC0008": F, "H_KIM_DEATH_AFTER_DETENTION": F, "E_EC0055": F}), None, dict(
        logic="VALID", temporal="VALID", classes=[["DN_EC0007", "DN_EC0036", "DN_EC0053"]],
        no_edges=[("DN_EC0004", "DN_EC0007"), ("DN_EC0007", "DN_EC0004")])),
    ("TW03_SAME_TRANSITIVE", "SAME(7,36)·SAME(36,53)만 지정: 추이적 closure로 셋이 한 node", {
        "H_KIM_MYEONGSIN_DIED": T, "E_EC0007": T, "E_EC0036": T, "E_EC0053": T,
        "SAME_EC0007_EC0036": T, "SAME_EC0036_EC0053": T}, None, dict(
        logic="VALID", temporal="VALID", classes=[["DN_EC0007", "DN_EC0036", "DN_EC0053"]])),
    ("TW04_SAME_TRANSITIVITY_VIOLATED", "SAME(7,36)·SAME(36,53) 참인데 SAME(7,53) 거짓: 논리 위반", {
        "H_KIM_MYEONGSIN_DIED": T, "E_EC0007": T, "E_EC0036": T, "E_EC0053": T,
        "SAME_EC0007_EC0036": T, "SAME_EC0036_EC0053": T, "SAME_EC0007_EC0053": F}, None, dict(
        logic="INVALID", temporal="VALID", classes=[["DN_EC0007", "DN_EC0036", "DN_EC0053"]])),
    ("TW05_THEFT_TRUE", "도난 실재 world: 도난 occurrence + 이형원→정조→이조원→홍대협→정조 절차", W_THEFT_TRUE, None, dict(
        logic="VALID", temporal="VALID", classes=[["DN_EC0150", "DN_EC0151"]],
        active=["DN_EC0070", "DN_EC0066"],
        edges=[("DN_J_LEEHYEONGWON_17930512_THEFT", "DN_J_JEONGJO_17930512_THEFT"),
               ("DN_J_JEONGJO_17930512_THEFT", "DN_J_IJOWON_17930527_THEFT"),
               ("DN_J_IJOWON_17930527_THEFT", "DN_EC0048"), ("DN_EC0048", "DN_EC0063"),
               ("DN_EC0063", "DN_J_HONG_17930613_THEFT"), ("DN_EC0061", "DN_J_HONG_17930613_THEFT"),
               ("DN_J_HONG_17930613_THEFT", "DN_J_JEONGJO_17930613_THEFT"),
               ("DN_J_JEONGJO_17930512_THEFT", "DN_J_JEONGJO_17930613_THEFT"),
               ("DN_EC0070", "DN_J_JEONGJO_17930512_THEFT")],
        no_edges=[("DN_EC0066", "DN_EC0070"), ("DN_EC0070", "DN_EC0066"),
                  ("DN_J_JEONGJO_17930613_THEFT", "DN_EC0150")],
        inactive=["DN_EC0143", "DN_EC0022", "DN_EC0131", "DN_EC0132"])),
    ("TW06_THEFT_FALSE", "도난 부재 world: 도난 node 없음, 판단·명령 act 절차는 그대로", W_THEFT_FALSE, None, dict(
        logic="VALID", temporal="VALID", inactive=["DN_EC0070", "DN_EC0143", "DN_EC0022"],
        active=["DN_J_JEONGJO_17930512_THEFT", "DN_J_JEONGJO_17930613_THEFT", "DN_J_HONG_17930613_THEFT"],
        edges=[("DN_J_HONG_17930613_THEFT", "DN_J_JEONGJO_17930613_THEFT"),
               ("DN_J_JEONGJO_17930512_THEFT", "DN_J_JEONGJO_17930613_THEFT")])),
    ("TW07_JAMIDEOK_ID_TRUE", "한 비장=한재욱 참: 접촉 node collapse 허용, 행위자 chain 통합", W_JAMI_ID_TRUE, None, dict(
        logic="VALID", temporal="VALID",
        classes=[["DN_EC0089", "DN_EC0104"], ["DN_EC0107", "DN_EC0119"], ["DN_EC0111", "DN_EC0120"]],
        edges=[("DN_EC0081", "DN_EC0089"), ("DN_EC0082", "DN_EC0104"), ("DN_EC0103", "DN_EC0089"),
               ("DN_EC0105", "DN_EC0106"), ("DN_EC0106", "DN_EC0119"), ("DN_EC0122", "DN_EC0123"),
               ("DN_EC0089", "DN_EC0153")],
        during=[("DN_EC0113", "DN_EC0112")], no_edges=[("DN_EC0081", "DN_EC0082"), ("DN_EC0082", "DN_EC0081")],
        separate=[("DN_EC0081", "DN_EC0082")], actor=("DN_EC0107", "한재욱"))),
    ("TW08_JAMIDEOK_ID_FALSE", "한 비장≠한재욱: SAME 불가, 한 비장·한재욱 행위가 별개 node", W_JAMI_ID_FALSE, None, dict(
        logic="VALID", temporal="VALID", classes=[["DN_EC0089", "DN_EC0104"]],
        separate=[("DN_EC0107", "DN_EC0119"), ("DN_EC0111", "DN_EC0120")],
        edges=[("DN_EC0106", "DN_EC0107"), ("DN_EC0103", "DN_EC0089")],
        no_edges=[("DN_EC0106", "DN_EC0119")], actor=("DN_EC0107", "한 비장"))),
    ("TW09_ID_FALSE_SAME_TRUE", "한 비장≠한재욱인데 SAME(107,119) 참: 논리 위반(RC0271)", dict(
        W_JAMI_ID_FALSE, SAME_EC0107_EC0119=T), None, dict(logic="INVALID", temporal="VALID")),
    ("TW10_TEMPORAL_ASSIGNMENT_CYCLE", "TW01 + 시간 할당 사망(3/1) < 구금(3/10): 논리 VALID·시간 INVALID", W_DEATH,
     {"DN_EC0007": "1793-03-01", "DN_EC0004": "1793-03-10"}, dict(logic="VALID", temporal="INVALID")),
]


STEP_RULES = [
    ["MR_S1", "STEP1", "NODE_ACTIVATION", "(all activation variables)", "", "", "",
     "36의 activation_condition이 W에서 TRUE인 node만 활성. H_* 사건 사실 → 그 사실을 표현하는 occurrence node, E_* → claim 고유 occurrence/act, J_* → 판단 act.",
     "비활성(그 world에 없음). 미할당 변수는 UNDETERMINED로 두고 활성화하지 않음.",
     "ATTRIBUTE_ONLY·REVIEW_REQUIRED는 어떤 world에서도 활성화하지 않음. H_* 자체는 node가 아님."],
    ["MR_S2", "STEP2", "IDENTITY_APPLICATION", "ID_*", "IDENTITY_HYPOTHESIS", "", "",
     "W에서 TRUE인 동일성만 적용: 행위자 label·actor chain 통합, CONDITIONAL_ON_IDENTITY edge 조건 충족.",
     "적용하지 않음: surface form 그대로 별개 행위자.",
     "동일성만으로 node를 합치지 않음(합치기는 STEP3–4의 SAME으로만). DIRECTLY_IDENTIFIED(풍각 김생원=김명신, 흥덕 김생원=김갑득, 남편=재돌)만 template 서술에서 바로 사용."],
    ["MR_S3", "STEP3", "SAME_EQUIVALENCE_CLOSURE", "SAME_*", "SAME_OCCURRENCE_HYPOTHESIS", "", "",
     "TRUE인 SAME 쌍으로 반사·대칭·추이 closure(union-find) 계산.",
     "FALSE로 할당된 SAME 쌍이 closure 안에 들어가면 LOGICALLY_INVALID(RC0275–RC0289 추이성).",
     "OCCURRENCE_GRANULARITY_ACT_LEVEL이 참이면 행위가 다른 SAME 쌍은 거짓이어야 함(RC0290–RC0293)."],
    ["MR_S4", "STEP4", "COLLAPSE (CONDITIONAL_ON_SAME_OCCURRENCE)", "SAME_*", "SAME_OCCURRENCE_HYPOTHESIS", "", "",
     "같은 class의 candidate node를 하나의 world occurrence node로 collapse. 구성원 중 하나라도 활성이면 활성. 시간 anchor는 교집합(같은 occurrence는 T 하나, RC0331–RC0348).",
     "collapse 없음(각 referent가 별개 node).",
     "anchor 교집합이 비면 TEMPORALLY_INVALID. 같은 사건 사실 템플릿의 referent가 SAME 없이 둘 이상 활성이면 TEMPLATE_SPLIT_REVIEW 표시(무효 처리는 하지 않음)."],
    ["MR_S5", "STEP5", "EDGE_ACTIVATION", "(edge condition variables)", "", "", "",
     "두 endpoint(collapse 후)가 활성이고 조건이 TRUE인 edge만 활성. HARD는 node 존재 외 조건 없음. collapse된 endpoint로 다시 연결.",
     "비활성. 조건이 미정이면 UNDETERMINED로 두고 활성화하지 않음.",
     "EVIDENCE_ONLY·REVIEW_REQUIRED edge는 어떤 world에서도 활성화하지 않음."],
    ["MR_S6", "STEP6", "SELF_LOOP_REMOVAL", "SAME_*", "SAME_OCCURRENCE_HYPOTHESIS", "", "",
     "collapse로 양 끝이 같은 node가 된 edge 제거.", "", "제거 목록은 materialize 결과에 기록."],
    ["MR_S7", "STEP7", "CYCLE_CHECK (POSSIBLE_WORLD_FILTER)", "(world + temporal assignment)", "", "", "",
     "선후 edge(BEFORE·PROCEDURAL)로 cycle이 생기면, DURING 포함과 선후가 충돌하면, 시간 할당이 활성 edge·anchor와 어긋나면 그 world + temporal assignment는 TEMPORALLY_INVALID.",
     "", "LOGICALLY_VALID이면서 TEMPORALLY_INVALID인 world가 있을 수 있으며 이 filter로 제거할 수 있음."],
    ["MR_S8", "ALL", "NO_EDGE_SEMANTICS", "", "", "", "",
     "edge 없음 = 현재 자료로 선후를 모름.", "",
     "동시성도, 누락 사건도 뜻하지 않음. 날짜쌍 edge는 전이적 축약을 하지 않음(중간 node가 없는 world가 있으므로)."],
]


log = logging.getLogger("v2_dag_template")


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


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def fetch(con, sql):
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    return [{c: ("" if v is None else v) for c, v in zip(cols, r)} for r in cur.fetchall()]


# ---------------------------------------------------------------- materialization (Steps 1–7)
def same_classes(true_pairs, members, transitive=True):
    """Equivalence classes of the SAME relation chosen TRUE in W.
    transitive=True: reflexive + symmetric + transitive closure (union-find)."""
    parent = {m: m for m in members}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    if transitive:
        for a, b in true_pairs:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
        groups = {}
        for m in members:
            groups.setdefault(find(m), []).append(m)
    else:  # deliberately wrong pairwise grouping (mutation same_nontransitive)
        grp, groups = {}, {}
        for a, b in sorted(true_pairs):
            if a not in grp and b not in grp:
                grp[a] = grp[b] = a
        for m in members:
            groups.setdefault(grp.get(m, m), []).append(m)
    return [sorted(g) for g in groups.values()]


def sccs(nodes, adj):
    index, low, stack, on, out, counter = {}, {}, [], set(), [], [0]

    def strong(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in adj.get(v, ()):
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            out.append(comp)

    sys.setrecursionlimit(10000)
    for v in sorted(nodes):
        if v not in index:
            strong(v)
    return out


def reachable(adj, src):
    seen, todo = set(), [src]
    while todo:
        x = todo.pop()
        for y in adj.get(x, ()):
            if y not in seen:
                seen.add(y)
                todo.append(y)
    return seen


def materialize(world, tmpl, assignment=None, transitive=True):
    """Materialize the world-specific DAG of W from the template.
    tmpl: dict(nodes, edges, same_pairs, logic, anchors). Unassigned variables are UNDETERMINED (never TRUE)."""
    nodes, edges = tmpl["nodes"], tmpl["edges"]
    r = dict(flags=[])
    # logical consistency of W (repaired constraints, three-valued over the assigned variables)
    r["logic_violations"] = [cid for cid, f in tmpl["logic"] if evaluate(f, world) is False]
    # Step 1: activate nodes
    active, undetermined = set(), set()
    for nid, n in nodes.items():
        if n["cls"] not in NODE_CLASSES or n["act"] is None:
            continue
        v = evaluate(n["act"], world)
        if v is True:
            active.add(nid)
        elif v is None:
            undetermined.add(nid)
    r["active"], r["undetermined"] = active, undetermined
    # Step 2: identities TRUE in W (actor labels / actor chain; never a merge by themselves)
    ids_true = sorted(v for v, val in world.items() if v.startswith("ID_") and val is True)
    alias = {}
    for i in ids_true:
        if i in ID_ALIAS:
            s, c = ID_ALIAS[i]
            alias.setdefault(s, {s}).add(c)
            alias.setdefault(c, {c}).add(s)
    actor = {}
    for nid in active:
        subj = nodes[nid]["subject"]
        group = {subj} | reachable({k: v - {k} for k, v in alias.items()}, subj) if subj in alias else {subj}
        named = [p for p in PERSON_PRIORITY if p in group]
        actor[nid] = named[0] if named else subj
    r["ids_true"], r["actor"] = ids_true, actor
    # Step 3: SAME equivalence classes
    true_pairs = [(a, b) for var, a, b in tmpl["same_pairs"] if world.get(var) is True]
    members = sorted(nodes)
    classes = same_classes(true_pairs, members, transitive)
    rep = {}
    for g in classes:
        for m in g:
            rep[m] = g[0]
    for var, a, b in tmpl["same_pairs"]:
        if world.get(var) is False and rep[a] == rep[b]:
            r["flags"].append(f"SAME_TRANSITIVITY_VIOLATION:{var}")
    # Step 4: collapse (class active if any member active); time anchors must intersect
    wnodes = {}
    for g in classes:
        act = [m for m in g if m in active]
        if act:
            wnodes[g[0]] = act
    anchors, anchor_conflicts = {}, []
    for rp, mem in wnodes.items():
        iv = None
        for m in mem:
            a = tmpl["anchors"](m, world)
            if a is None:
                continue
            iv = a if iv is None else (max(iv[0], a[0]), min(iv[1], a[1]))
        if iv is not None and iv[0] >= iv[1]:
            anchor_conflicts.append(rp)
        anchors[rp] = iv
    fact_cls = {}
    for rp, mem in wnodes.items():
        for m in mem:
            if nodes[m].get("fact"):
                fact_cls.setdefault(nodes[m]["fact"], set()).add(rp)
    for fact, reps in sorted(fact_cls.items()):
        if len(reps) > 1:
            r["flags"].append(f"TEMPLATE_SPLIT_REVIEW:{fact}:{'|'.join(sorted(reps))}")
    r["classes"] = [g for g in classes if len(g) > 1 and any(m in active for m in g)]
    r["wnodes"], r["rep"] = wnodes, rep
    # Step 5: activate edges whose endpoints are active and whose condition is TRUE
    act_edges, self_loops, und_edges, seen = [], [], [], set()
    for e in edges:
        if e["kind"] in NEVER_KINDS:
            continue
        a, b = rep[e["frm"]], rep[e["to"]]
        if a not in wnodes or b not in wnodes:
            continue
        c = True if e["cond"] is None else evaluate(e["cond"], world)
        if c is None:
            und_edges.append(e["id"])
            continue
        if c is not True:
            continue
        if a == b:  # Step 6: self-loop removal
            self_loops.append(e["id"])
            continue
        key = (a, b, e["etype"] == DURING)
        if key not in seen:
            seen.add(key)
            act_edges.append((a, b, e["etype"], e["id"]))
    r["edges"], r["self_loops"], r["undetermined_edges"] = act_edges, self_loops, und_edges
    # Step 7: cycle check (strict edges), DURING conflicts, temporal assignment
    adj = {}
    for a, b, t, _ in act_edges:
        if t in STRICT_TYPES:
            adj.setdefault(a, set()).add(b)
        elif t == AFTER:
            adj.setdefault(b, set()).add(a)
    r["cycles"] = [sorted(c) for c in sccs(set(wnodes), adj) if len(c) > 1]
    during_conf = []
    for a, b, t, eid in act_edges:
        if t == DURING and (b in reachable(adj, a) or a in reachable(adj, b)):
            during_conf.append(eid)
    assign_conf = []
    if assignment:
        val = {}
        for nid, txt in assignment.items():
            iv = interval(txt)
            rp = rep[nid]
            if rp in val and val[rp] != iv[0]:
                assign_conf.append(f"SAME_TIME_MISMATCH:{rp}")
            val[rp] = iv[0]
            if anchors.get(rp) and not (anchors[rp][0] <= iv[0] < anchors[rp][1]):
                assign_conf.append(f"ANCHOR:{rp}")
        for a, b, t, eid in act_edges:
            if t in STRICT_TYPES and a in val and b in val and not val[a] < val[b]:
                assign_conf.append(f"{eid}:{a}->{b}")
    r["during_conflicts"], r["anchor_conflicts"], r["assignment_conflicts"] = during_conf, anchor_conflicts, assign_conf
    r["logic"] = "INVALID" if r["logic_violations"] or any(f.startswith("SAME_TRANS") for f in r["flags"]) else "VALID"
    r["temporal"] = "INVALID" if (r["cycles"] or during_conf or anchor_conflicts or assign_conf) else "VALID"
    return r


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--mutation", default="")
    args = ap_.parse_args()
    mut = args.mutation
    LOG_DIR.mkdir(exist_ok=True)
    handlers = [logging.StreamHandler(sys.stdout)]
    if not mut:
        handlers.append(logging.FileHandler(LOG_DIR / "v2_dag_template.log", mode="w", encoding="utf-8"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=handlers)
    if mut and mut not in MUTATIONS:
        log.error("unknown mutation %s (known: %s)", mut, ", ".join(MUTATIONS))
        sys.exit(2)

    checks = []

    def check(cid, desc, ok, detail="", severity="ERROR"):
        checks.append([cid, desc, "PASS" if ok else severity, detail])
        if not ok:
            (log.error if severity == "ERROR" else log.warning)("%s %s: %s", cid, desc, detail)

    # ---------------- integrity at start
    expected_sha = {}
    for line in SHA_PATH.read_text(encoding="utf-8").splitlines():
        h, fn = line.split("  ", 1)
        expected_sha[fn] = h
    raw_ok_start = all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items())
    preserved = sorted(p.name for p in OUT_DIR.glob("*.csv") if re.match(r"^(0[1-9]|[12]\d|3[0-5])_", p.name))
    out_before = {n: sha256(OUT_DIR / n) for n in preserved}
    con = duckdb.connect(str(DB_PATH), read_only=bool(mut))
    tables = sorted(t[0] for t in con.execute("SHOW TABLES").fetchall())
    protected = [t for t in tables if t not in NEW_TABLES]
    digests_before = {t: table_digest(con, t) for t in protected}

    cand = {r["event_candidate_id"]: r for r in fetch(con, "SELECT * FROM historical_event_candidates")}
    aps = {r["atomic_prop_id"]: r for r in fetch(con, "SELECT * FROM atomic_propositions")}
    props = {r["prop_id"]: r for r in fetch(con, "SELECT * FROM source_faithful_propositions")}
    srcs = {r["source_record_id"]: r for r in fetch(con, "SELECT * FROM source_records")}
    facts = {r["historical_fact_id"]: r for r in fetch(con, "SELECT * FROM historical_facts")}
    cmap = fetch(con, "SELECT * FROM claim_fact_mapping")
    judg = {r["judgment_state_id"]: r for r in fetch(con, "SELECT * FROM judgment_states")}
    jrel = {r["relation_id"]: r for r in fetch(con, "SELECT * FROM judgment_state_relations")}
    rvars = {r["variable_id"]: r for r in fetch(con, "SELECT * FROM repaired_world_variables")}
    rcons = fetch(con, "SELECT * FROM repaired_logical_constraints ORDER BY constraint_id")
    projection = {r["atomic_prop_id"]: r for r in fetch(con, "SELECT * FROM event_projection_decisions")}

    def ap_of(ec):
        return aps[cand[ec]["origin_atomic_prop_id"]]

    def text_of(ref):
        if ref.startswith("EC"):
            c, a = cand[ref], ap_of(ref)
            p = props.get(a["parent_prop_id"], {})
            return " ".join(str(x) for x in (c["predicate"], c["relative_time_text"], c["subject_surface"],
                                             c["object_surface"], a["predicate"], p.get("predicate", ""),
                                             p.get("notes", "")))
        if ref.startswith("J_"):
            j = judg[ref]
            return " ".join((j["judgment_topic"], j["notes"], j["judgment_date"]))
        if ref.startswith("SRC"):
            s = srcs[ref]
            return " ".join((s["source_title"], s["notes"], s["case_role"]))
        if ref.startswith("P0"):
            return " ".join((props[ref]["predicate"], props[ref]["notes"]))
        if ref.startswith("JR"):
            return " ".join(jrel[ref].values())
        raise KeyError(ref)

    # SAME components
    same_vars = sorted(v for v in rvars if v.startswith("SAME_"))
    comp_adj = {}
    for sv in same_vars:
        a, b = sv.split("_")[1:]
        comp_adj.setdefault(a, set()).add(b)
        comp_adj.setdefault(b, set()).add(a)
    component = {}
    for x in sorted(comp_adj):
        if x in component:
            continue
        comp = {x} | reachable(comp_adj, x)
        for y in comp:
            component[y] = sorted(comp)

    # ---------------- nodes
    nodes = {}
    for ec in sorted(cand):
        cls, action, note = CLASS[ec]
        c = cand[ec]
        a = ap_of(ec)
        fact = FACT_KEY.get(ec, "") if cls in NODE_CLASSES else ""
        attr_fact = ""
        if cls in (ATTR, REV):
            ms = [m for m in cmap if m["event_candidate_id"] == ec]
            attr_fact = ms[0]["historical_fact_id"] if ms else ""
        if cls in NODE_CLASSES:
            act = Eq(fact, True) if fact else Eq(f"E_{ec}", True)
        else:
            act = None
        if ec in COURT_EC:
            time = ("COURT_ENTRY_DATE", a["record_lunar_date"])
        elif c["occurrence_lunar_text"] and c["occurrence_precision"] != "RELATIVE_ONLY" and cls in NODE_CLASSES:
            time = ("CLAIMED_DATE", c["occurrence_lunar_text"])
        elif c["relative_time_text"] and cls in NODE_CLASSES:
            time = ("RELATIVE_ONLY", c["relative_time_text"])
        else:
            time = ("NONE", "")
        nodes[dn(ec)] = dict(id=dn(ec), sources=[ec], cls=cls, subject=c["subject_surface"], action=action,
                             object=c["object_surface"], fact=fact, attr_fact=attr_fact, act=act,
                             same=component.get(ec, []), note=note, time=time, ec=ec,
                             record_date=a["record_lunar_date"], source=a["source_record_id"])
    for jid in judg:
        j = judg[jid]
        entry, why = J_TIME[jid]
        time = ("COURT_ENTRY_DATE", j["judgment_date"]) if entry else ("NONE", "")
        contents = [x for x in j["event_candidate_ids"].split("|") if x]
        nodes[dn(jid)] = dict(id=dn(jid), sources=[jid], cls=SPJ, subject=j["judge_or_actor"],
                              action=f"판단 행위({j['judgment_topic']})", object="", fact="", attr_fact="",
                              act=Eq(jid, True), same=[], ec="", record_date=j["judgment_date"],
                              source=j["source_record_ids"], time=time,
                              note=("판단 act node: 이 판단·진술 행위가 있었는지만 나타냄(판단 내용의 참·거짓과 무관, 내용은 node 아님). "
                                    + ("이 판단이 다루는 candidate(각자 따로 분류·활성): "
                                       + "|".join(f"{x}({CLASS[x][0]})" for x in contents) + "."
                                       if contents else "다루는 event candidate 없음.")))
    court_acts = {dn(x) for x in COURT_EC} | {dn(j) for j, (e, _) in J_TIME.items() if e}
    proc_acts = {dn(x) for x in COURT_EC} | {dn(j) for j in judg}

    # ---------------- node-level mutations
    if mut == "cause_as_node":
        n = nodes["DN_EC0054"]
        n.update(cls=MAT, action="사망 원인(병)", act=Eq("E_EC0054", True))
    elif mut == "record_date_copied":
        nodes["DN_EC0097"]["time"] = ("COURT_ENTRY_DATE", "1793-06-13")
        court_acts.add("DN_EC0097")
        proc_acts.add("DN_EC0097")
    elif mut == "exile_execution_node":
        nodes["DN_EXEC_EC0151"] = dict(id="DN_EXEC_EC0151", sources=["EC0151"], cls=MAT, subject="구순",
                                       action="정배 집행(구순 신지도)", object="신지도", fact="", attr_fact="",
                                       act=Eq("E_EC0151", True), same=[], ec="EC0151", record_date="1793-06-13",
                                       source="SRC2_006", time=("NONE", ""), note="")
    elif mut == "force_merge_hanbijang":
        n = nodes["DN_EC0107"]
        n.update(sources=["EC0107", "EC0119"], subject="한재욱")
        del nodes["DN_EC0119"]

    def anchor(nid, world):
        n = nodes.get(nid)
        if n is None:
            return None
        kind, txt = n["time"]
        if kind == "COURT_ENTRY_DATE":
            return interval(txt)
        if kind == "CLAIMED_DATE":
            cond = E(n["ec"]) if n["ec"] != "EC0065" else And(E("EC0065"), V("INTERP_EC0065_DATE_IS_TELLING_TIME"))
            return interval(txt) if evaluate(cond, world) is True else None
        return None

    def claim_cond(nid):
        ec = nodes[nid]["ec"]
        return [E(ec)] if ec != "EC0065" else [E("EC0065"), V("INTERP_EC0065_DATE_IS_TELLING_TIME")]

    def conj(xs):
        return xs[0] if len(xs) == 1 else And(*xs)

    # ---------------- edges
    raw_edges = explicit_edges()
    claimed = sorted(n for n, x in nodes.items() if x["time"][0] == "CLAIMED_DATE" and x["cls"] in NODE_CLASSES)
    court = sorted(n for n in court_acts if n in nodes)
    when = {n: interval(nodes[n]["time"][1]) for n in claimed + court}
    for a in claimed:
        for b in claimed:
            if a != b and strictly_before(when[a], when[b]):
                raw_edges.append(dict(frm=a, to=b, etype=BEFORE, kind=CTEMP, cond=conj(claim_cond(a) + claim_cond(b)),
                                      bases=[("CLAIMED_DATE_ORDER", "", [a, b])], strength="MEDIUM", review=False,
                                      note="주장 날짜쌍: 두 claim이 날짜까지 참인 world에서만(실제 시점 T는 world가 결정)."))
        for b in court:
            if strictly_before(when[a], when[b]):
                raw_edges.append(dict(frm=a, to=b, etype=BEFORE, kind=CTEMP, cond=conj(claim_cond(a)),
                                      bases=[("CLAIMED_VS_COURT_DATE_ORDER", "", [a, b])], strength="MEDIUM",
                                      review=False,
                                      note="주장 날짜 vs 조정 행위 기사일: 앞 claim이 날짜까지 참일 때만."))
    for a in court:
        for b in court:
            if a != b and strictly_before(when[a], when[b]):
                raw_edges.append(dict(frm=a, to=b, etype=BEFORE, kind=HARD, cond=None,
                                      bases=[("COURT_ENTRY_DATE_ORDER", "", [a, b])], strength="STRONG", review=False,
                                      note="두 조정 행위의 기사일(행위 자체의 기록일) 순서. HARD = node 존재 외 조건 없음."))
    # merge parallel candidates (same ordered pair, same strictness): explicit first, bases concatenated
    merged, index = [], {}
    for e in raw_edges:
        key = (e["frm"], e["to"], e["etype"] == DURING, e["kind"])
        if key in index:
            m = merged[index[key]]
            m["bases"] = m["bases"] + e["bases"]
            continue
        index[key] = len(merged)
        merged.append(dict(e))
    edges = []
    for i, e in enumerate(merged, 1):
        e["id"] = f"TE{i:04d}"
        edges.append(e)

    # ---------------- edge-level mutations
    if mut == "narrative_order_edge":
        edges.append(dict(id="TE9001", frm="DN_EC0104", to="DN_EC0105", etype=BEFORE, kind=CTEMP,
                          cond=And(E("EC0104"), E("EC0105")), bases=[("NARRATIVE_ORDER", "자미덕 공초 서술 순서", ["EC0104"])],
                          strength="MEDIUM", review=False, note=""))
    elif mut == "exile_execution_node":
        edges.append(dict(id="TE9002", frm="DN_EC0151", to="DN_EXEC_EC0151", etype=TRIG, kind=CTEMP,
                          cond=And(E("EC0151")), bases=[("ORDER_EXECUTION_EXPLICIT", "신지도에 정배", ["EC0151"])],
                          strength="MEDIUM", review=False, note=""))
    elif mut == "cycle_abca":
        edges.append(dict(id="TE9003", frm="DN_EC0107", to="DN_EC0105", etype=BEFORE, kind=CTEMP,
                          cond=And(E("EC0105"), E("EC0107")), bases=[("RELATIVE_TIME_TEXT", "그 후", ["EC0107"])],
                          strength="MEDIUM", review=False, note=""))
    elif mut == "force_merge_hanbijang":
        for e in edges:
            for k in ("frm", "to"):
                if e[k] == "DN_EC0119":
                    e[k] = "DN_EC0107"

    # ---------------- logic constraints (for the world-validity part of materialization)
    logic = []
    parse_bad = []
    for c in rcons:
        f = parse_formula(c["formula"])
        a = parse_formula(c["antecedent"]) if c["antecedent"] else None
        if render_old(f) != c["formula"] or (a and render_old(a) != c["antecedent"]):
            parse_bad.append(c["constraint_id"])
        logic.append((c["constraint_id"], Imp(a, f) if a else f))
    same_pairs = []
    for sv in same_vars:
        a, b = sv.split("_")[1:]
        if dn(a) in nodes and dn(b) in nodes and nodes[dn(a)]["cls"] in NODE_CLASSES and nodes[dn(b)]["cls"] in NODE_CLASSES:
            same_pairs.append((sv, dn(a), dn(b)))
    tmpl = dict(nodes=nodes, edges=edges, same_pairs=same_pairs, logic=logic, anchors=anchor)
    transitive = mut != "same_nontransitive"

    # ---------------- validation
    node_rows = [n for n in nodes.values()]
    is_node = {n["id"]: n["cls"] in NODE_CLASSES for n in node_rows}
    fact_type = {k: v["fact_type"] for k, v in facts.items()}
    attr_fact_types = {"CAUSE_ATTRIBUTE", "RESPONSIBILITY_ATTRIBUTE", "TEMPORAL_ATTRIBUTE", "PLACE_ATTRIBUTE",
                       "EVENT_ATTRIBUTE", "STATE"}

    def must_be_attribute(ec):
        c = cand[ec]
        why = []
        if c["event_type"] in ("CAUSE_ATTRIBUTION", "PLACE_ATTRIBUTION", "TEMPORAL_ATTRIBUTION", "PURPOSE_ATTRIBUTION"):
            why.append(c["event_type"])
        if c["polarity"] in ("NEGATED", "DOUBTED"):
            why.append(c["polarity"])
        if c["claim_topic"] in ("DEATH_CAUSE", "THEFT_SCALE") or (c["claim_topic"] == "THEFT_REALITY" and c["event_type"] == "STATE"):
            why.append(c["claim_topic"])
        for m in cmap:
            if m["event_candidate_id"] == ec and fact_type.get(m["historical_fact_id"]) in attr_fact_types:
                why.append(fact_type[m["historical_fact_id"]])
        return why

    endpoints = {}
    for e in edges:
        for k in ("frm", "to"):
            endpoints.setdefault(e[k], []).append(e["id"])
    results = {}
    for name, desc, world, asg, exp in TEST_WORLDS:
        results[name] = materialize(world, tmpl, asg, transitive)

    # V01 ATTRIBUTE_ONLY never a node
    detector = {ec: must_be_attribute(ec) for ec in cand}
    det_bad = [f"{ec}({'/'.join(w)})→{nodes[dn(ec)]['cls'] if dn(ec) in nodes else '?'}" for ec, w in detector.items()
               if w and (dn(ec) not in nodes or nodes[dn(ec)]["cls"] != ATTR)]
    attr_active = [n["id"] for n in node_rows if n["cls"] == ATTR and n["act"] is not None]
    attr_endpoint = [f"{n['id']}:{'|'.join(endpoints[n['id']])}" for n in node_rows if n["cls"] in (ATTR, REV)
                     and n["id"] in endpoints]
    attr_in_world = sorted({m for r in results.values() for mem in r["wnodes"].values() for m in mem
                            if nodes[m]["cls"] not in NODE_CLASSES})
    check("V01", "ATTRIBUTE_ONLY가 DAG node가 된 사례 = 0 (구조 탐지 속성 candidate가 모두 ATTRIBUTE_ONLY, 활성 조건·edge·world graph 없음)",
          not (det_bad or attr_active or attr_endpoint or attr_in_world),
          "|".join(det_bad + attr_active + attr_endpoint + attr_in_world))
    # V02 death-cause claims never independent nodes
    cause_facts = {k for k in facts if k.startswith(("H_KIM_DEATH_CAUSE", "H_KIM_DEATH_RESPONSIBILITY",
                                                       "H_KIM_DEATH_DIRECT_CAUSE", "H_KIM_WIFE_DEATH_CAUSE"))}
    cause_ecs = {m["event_candidate_id"] for m in cmap if m["historical_fact_id"] in cause_facts}
    cause_ecs |= {ec for ec, c in cand.items() if c["claim_topic"] == "DEATH_CAUSE"}
    cause_bad = [ec for ec in sorted(cause_ecs) if is_node.get(dn(ec), True)]
    cause_bad += [n["id"] for n in node_rows if n["ec"] and n["cls"] in NODE_CLASSES and re.search(r"사인|사망 원인", n["action"])]
    tw = results["TW01_KIM_DEATH"]
    cause_bad += [dn(ec) for ec in cause_ecs if dn(ec) in tw["active"]]
    check("V02", "사망 원인 claim이 독립 event node가 된 사례 = 0", not cause_bad and len(cause_ecs) >= 6,
          "|".join(cause_bad) or f"cause claims={len(cause_ecs)}")
    # V03 judgment content vs judgment act
    j_bad = []
    for jid in judg:
        n = nodes.get(dn(jid))
        if not n or n["cls"] != SPJ or n["act"] != Eq(jid, True) or n["fact"] or n["sources"] != [jid]:
            j_bad.append(dn(jid))
    j_bad += [n["id"] for n in node_rows if n["act"] and n["id"][3:] not in judg
              and any(v.startswith("J_") for v in vars_of(n["act"]))]
    j_bad += [e["id"] for e in edges if e["cond"] and any(v.startswith("J_") for v in vars_of(e["cond"]))]
    content = [m["event_candidate_id"] for m in cmap if m["judgment_state_id"]
               and fact_type.get(m["historical_fact_id"]) != "EVENT_OCCURRENCE" and m["logical_form"] != "(논리 연결 없음; evidence only)"]
    content += [ec for ec, c in cand.items() if c["claim_topic"] == "THEFT_REALITY" and c["event_type"] == "STATE"]
    j_bad += [ec for ec in sorted(set(content)) if is_node.get(dn(ec), True)]
    t_false = results["TW06_THEFT_FALSE"]
    act_indep = "DN_EC0070" not in t_false["active"] and "DN_J_JEONGJO_17930613_THEFT" in t_false["active"]
    check("V03", "judgment content를 judgment act와 혼동한 사례 = 0 (J act node는 J_=TRUE로만 활성, 내용 candidate는 ATTRIBUTE_ONLY)",
          not j_bad and act_indep, "|".join(j_bad) + ("" if act_indep else " act가 내용에 종속"))
    # V04 record date never used as historical occurrence date of a reported event
    r_bad = []
    for n in node_rows:
        kind, txt = n["time"]
        if kind == "COURT_ENTRY_DATE":
            if n["id"] not in court_acts:
                r_bad.append(f"{n['id']}:not-court-act")
            if n["ec"]:
                a = ap_of(n["ec"])
                if not (cand[n["ec"]]["event_type"] in ("ORDER", "REQUEST") and a["attestation_mode"] in
                        ("ROYAL_ORDER", "MINISTERIAL_PROPOSAL") and a["claim_level"] == "OUTER_ATTESTATION"
                        and txt == a["record_lunar_date"]):
                    r_bad.append(f"{n['id']}:reported-event({a['attestation_mode']})")
            else:
                j = judg.get(n["sources"][0])
                srcd = {srcs[s]["record_lunar_date"] for s in j["source_record_ids"].split("|")} if j else set()
                if not j or not re.fullmatch(r"\d{4}-\d\d-\d\d", j["judgment_date"]) or srcd != {txt}:
                    r_bad.append(f"{n['id']}:judgment-date")
        elif kind == "CLAIMED_DATE":
            if txt != cand[n["ec"]]["occurrence_lunar_text"] or txt == n["record_date"]:
                r_bad.append(f"{n['id']}:claimed≠occurrence_text")
    for x in court_acts:
        if nodes.get(x, {}).get("time", ("",))[0] != "COURT_ENTRY_DATE":
            r_bad.append(f"{x}:court-act-without-entry")
    for e in edges:
        for bt, _, refs in e["bases"]:
            if bt == "COURT_ENTRY_DATE_ORDER" and not (e["frm"] in court_acts and e["to"] in court_acts):
                r_bad.append(f"{e['id']}:court-date-basis")
            if bt == "CLAIMED_DATE_ORDER" and not all(nodes[x]["time"][0] == "CLAIMED_DATE" for x in (e["frm"], e["to"])):
                r_bad.append(f"{e['id']}:claimed-basis")
    tw7 = results["TW07_JAMIDEOK_ID_TRUE"]
    if tmpl["anchors"]("DN_EC0089", {"E_EC0089": False}) is not None:
        r_bad.append("anchor-without-claim")
    check("V04", "record date를 historical occurrence date로 자동 사용한 사례 = 0 (기사일 anchor는 조정 행위 자체에만, 보고된 사건은 주장 날짜+claim 조건)",
          not r_bad, "|".join(r_bad[:12]))
    # V05 no edge from narrative order alone
    n_bad = []
    for e in edges:
        if not e["bases"]:
            n_bad.append(f"{e['id']}:no-basis")
        for bt, phrase, refs in e["bases"]:
            allowed = ACTIVE_BASES if e["kind"] not in NEVER_KINDS else ACTIVE_BASES + NONACTIVE_BASES
            if bt not in allowed:
                n_bad.append(f"{e['id']}:{bt}")
                continue
            if bt in DATE_BASES:
                if not strictly_before(interval(nodes[e["frm"]]["time"][1]), interval(nodes[e["to"]]["time"][1])):
                    n_bad.append(f"{e['id']}:date-not-ordered")
            elif bt == "JUDGMENT_REVISION":
                rel = jrel.get(refs[0])
                if not rel or dn(rel["from_judgment_state_id"]) != e["frm"] or dn(rel["to_judgment_state_id"]) != e["to"]:
                    n_bad.append(f"{e['id']}:revision-mismatch")
            else:
                if not phrase or not any(phrase in text_of(r) for r in refs):
                    n_bad.append(f"{e['id']}:phrase-not-in-text({phrase})")
    check("V05", "서술 순서만으로 temporal edge 생성 = 0 (모든 edge 근거가 허용 유형이고 문구는 원문에, 날짜는 실제로 선후)",
          not n_bad, "|".join(n_bad[:12]))
    # V06 no EXECUTION node for orders without an execution record
    e_bad = [n["id"] for n in node_rows if not re.fullmatch(r"DN_(EC\d{4}|J_[A-Z0-9_]+)", n["id"])
             or "EXEC" in n["id"] or "집행" in n["action"]]
    e_bad += [n["id"] for n in node_rows if n["ec"] and n["id"] != dn(n["ec"])]
    e_bad += [e["id"] for e in edges if e["etype"] == TRIG and not (re.fullmatch(r"DN_EC\d{4}", e["to"])
                                                                    and nodes[e["to"]]["cls"] in NODE_CLASSES)]
    orders = [n["id"] for n in node_rows if n["cls"] == ORD]
    no_exec = [o for o in orders if not any(e["frm"] == o and e["etype"] == TRIG for e in edges)]
    check("V06", "ORDER만 있는데 EXECUTION node 생성 = 0 (모든 node가 실제 candidate/judgment state, 실행 edge는 실행 기록 candidate로만)",
          not e_bad, "|".join(e_bad) or f"ORDER {len(orders)}개 중 실행 기록 연결 {len(orders) - len(no_exec)}개, 나머지는 명령 node만")
    # V07 no global identity merge
    i_bad = [n["id"] for n in node_rows if len(n["sources"]) != 1]
    i_bad += [n["id"] for n in node_rows if n["ec"] and n["subject"] != cand[n["ec"]]["subject_surface"]]
    used = [s for n in node_rows for s in n["sources"]]
    i_bad += [f"missing:{x}" for x in sorted(set(cand) | set(judg)) if used.count(x) != 1]
    i_bad += [e["id"] for e in edges if e["kind"] == CID and not any(v.startswith("ID_") for v in vars_of(e["cond"]))]
    w8 = results["TW08_JAMIDEOK_ID_FALSE"]
    if w8["rep"].get("DN_EC0107") == w8["rep"].get("DN_EC0119", "x"):
        i_bad.append("TW08:한 비장·한재욱 node 합쳐짐")
    check("V07", "미확정 identity를 전역 merge = 0 (node당 candidate 1개, surface form 보존, 동일성은 W에서만)",
          not i_bad, "|".join(i_bad))
    # V08 no global SAME merge
    s_bad = []
    for sv in same_vars:
        a, b = sv.split("_")[1:]
        holders = [n["id"] for n in node_rows if a in n["sources"] and b in n["sources"]]
        if holders or dn(a) not in nodes or dn(b) not in nodes:
            s_bad.append(sv)
    check("V08", "SAME_OCCURRENCE_CANDIDATE를 전역 merge = 0 (18개 SAME 쌍의 두 referent가 template에서 모두 별도 row)",
          not s_bad and len(same_vars) == 18, "|".join(s_bad) or f"SAME vars={len(same_vars)}")
    # V09 conditional edge never promoted to hard
    h_bad = []
    for e in edges:
        if e["kind"] == HARD:
            if e["cond"] is not None or e["frm"] not in proc_acts or e["to"] not in proc_acts:
                h_bad.append(f"{e['id']}:hard-endpoint/cond")
            if any(bt not in HARD_BASES for bt, _, _ in e["bases"]):
                h_bad.append(f"{e['id']}:hard-basis")
        elif e["kind"] in COND_KINDS:
            if e["cond"] is None or not any(v.startswith(("E_", "H_", "REF_", "ID_", "SAME_", "INTERP_")) for v in vars_of(e["cond"])):
                h_bad.append(f"{e['id']}:empty-cond")
        elif e["cond"] is not None:
            h_bad.append(f"{e['id']}:never-edge-with-cond")
    pair_kinds = {}
    for e in edges:
        if e["kind"] not in NEVER_KINDS:
            pair_kinds.setdefault((e["frm"], e["to"]), set()).add(e["kind"])
    h_bad += [f"kind-clash:{a_}->{b_}" for (a_, b_), ks in pair_kinds.items() if len(ks) > 1]
    rc_lt = [c for c in rcons if " < " in c["formula"]]
    for c in rc_lt:
        a_, b_ = [x.strip()[2:] for x in c["formula"].split(" < ")]
        ante = vars_of(parse_formula(c["antecedent"]))
        if not any(e["frm"] == dn(a_) and e["to"] == dn(b_) and e["kind"] == CTEMP and e["cond"] and vars_of(e["cond"]) == ante
                   for e in edges):
            h_bad.append(f"{c['constraint_id']}:not-mirrored")
    check("V09", "conditional edge가 조건 없이 hard edge로 승격 = 0 (HARD는 절차 act node 사이·기사일/명시 절차/판단 수정만)",
          not h_bad and len(rc_lt) == 7, "|".join(h_bad[:12]) or f"논리층 상대시간 제약 {len(rc_lt)}개 모두 conditional edge로 반영")
    # V10 same-occurrence transitivity cannot be violated in materialization
    t3, t4 = results["TW03_SAME_TRANSITIVE"], results["TW04_SAME_TRANSITIVITY_VIOLATED"]
    tri = {"DN_EC0007", "DN_EC0036", "DN_EC0053"}
    ok10 = (len({t3["rep"].get(x, "?" + x) for x in tri}) == 1 and t4["logic"] == "INVALID"
            and len({results["TW01_KIM_DEATH"]["rep"].get(x, "?" + x) for x in tri}) == 1)
    check("V10", "world materialization에서 same-occurrence 추이성 위반 가능 = 0 (union-find closure; SAME(A,B)∧SAME(B,C)면 A,C 한 node)",
          ok10, f"TW03 classes={t3['classes']} TW04 logic={t4['logic']}")
    # V11 cycle rule exists and works
    toy_nodes = {k: dict(id=k, sources=[k], cls=MAT, subject="", action="", object="", fact="", act=V("X"), time=("NONE", ""),
                         ec="") for k in ("TA", "TB", "TC")}
    toy_cycle = dict(nodes=toy_nodes, same_pairs=[], logic=[], anchors=lambda n, w: None,
                     edges=[dict(id=f"X{i}", frm=a, to=b, etype=BEFORE, kind=HARD, cond=None)
                            for i, (a, b) in enumerate([("TA", "TB"), ("TB", "TC"), ("TC", "TA")])])
    toy_loop = dict(nodes=toy_nodes, same_pairs=[("SAME_TA_TB", "TA", "TB")], logic=[], anchors=lambda n, w: None,
                    edges=[dict(id="X9", frm="TA", to="TB", etype=BEFORE, kind=HARD, cond=None)])
    rc_ = materialize({"X": True}, toy_cycle)
    rl_ = materialize({"X": True, "SAME_TA_TB": True}, toy_loop)
    all_true = {**{f"E_{ec}": True for ec in cand}, **{h: True for h in facts}, **{j: True for j in judg},
                **{v: True for v in rvars if v.startswith(("REF_", "ID_", "INTERP_"))}}
    maxg = materialize(all_true, tmpl, None, transitive)
    rule_ok = any(r_[0] == "MR_S7" and "TEMPORALLY_INVALID" in r_[7] for r_ in STEP_RULES)
    exp_bad = []
    for name, desc, world, asg, exp in TEST_WORLDS:
        r = results[name]
        if r["logic"] != exp["logic"] or r["temporal"] != exp["temporal"]:
            exp_bad.append(f"{name}:{r['logic']}/{r['temporal']}≠{exp['logic']}/{exp['temporal']}")
    ok11 = (rule_ok and rc_["temporal"] == "INVALID" and rc_["cycles"] and rl_["temporal"] == "VALID"
            and rl_["self_loops"] == ["X9"] and results["TW10_TEMPORAL_ASSIGNMENT_CYCLE"]["temporal"] == "INVALID"
            and results["TW10_TEMPORAL_ASSIGNMENT_CYCLE"]["logic"] == "VALID" and not maxg["cycles"] and not exp_bad)
    check("V11", "world-specific graph가 cycle이면 INVALID 처리하는 규칙 존재 (toy A→B→C→A INVALID, self-loop 제거, 시간 할당 충돌 INVALID, 기대 VALID world는 VALID)",
          ok11, f"toy={rc_['temporal']} loop={rl_['self_loops']} TW10={results['TW10_TEMPORAL_ASSIGNMENT_CYCLE']['temporal']} "
                f"all-true template cycles={len(maxg['cycles'])} " + "|".join(exp_bad))
    # V12 no edge != simultaneity
    sim_bad = [e["id"] for e in edges if e["etype"] not in EDGE_TYPES]
    for name, r in results.items():
        tp = [(a, b) for v, a, b in same_pairs if TEST_WORLDS_D[name].get(v) is True]
        induced = sum(1 for g in same_classes(tp, sorted(nodes), True) if len(g) > 1)
        if transitive and len(r["classes"]) > induced:
            sim_bad.append(f"{name}:extra-collapse")
    a81, a82 = tw7["rep"]["DN_EC0081"], tw7["rep"]["DN_EC0082"]
    if a81 == a82 or any({x[0], x[1]} == {a81, a82} for x in tw7["edges"]):
        sim_bad.append("TW07:같은 밤 두 node가 합쳐지거나 순서가 생김")
    check("V12", "edge 없음이 simultaneity로 해석된 사례 = 0 (동시 edge 유형 없음, collapse는 SAME으로만, 같은 날짜 쌍은 무순서·별도 node)",
          not sim_bad, "|".join(sim_bad))
    # V13 temporal/procedural edges only
    c_bad = [e["id"] for e in edges if e["etype"] not in EDGE_TYPES or e["kind"] not in EDGE_KINDS]
    check("V13", "인과 edge(CAUSAL_CAUSES/MOTIVATES/ENABLES/RESPONSIBLE_FOR) = 0, edge 유형은 시간·절차 5종만", not c_bad, "|".join(c_bad))
    # V14 reference integrity
    ref_bad = [f"edge:{e['id']}" for e in edges if e["frm"] not in nodes or e["to"] not in nodes
               or not is_node.get(e["frm"]) or not is_node.get(e["to"])]
    allvars = set()
    for n in node_rows:
        if n["act"]:
            allvars |= vars_of(n["act"])
    for e in edges:
        if e["cond"]:
            allvars |= vars_of(e["cond"])
    ref_bad += [f"var:{v}" for v in sorted(allvars) if v not in rvars]
    ref_bad += [f"fact:{n['id']}" for n in node_rows if n["fact"] and fact_type.get(n["fact"]) != "EVENT_OCCURRENCE"]
    for ec, fid in FACT_KEY.items():
        if not any(m["event_candidate_id"] == ec and m["historical_fact_id"] == fid and not m["condition"]
                   and m["claim_relation"] == "ASSERTS_TRUE" for m in cmap):
            ref_bad.append(f"factkey:{ec}")
    ref_bad += [f"class:{ec}" for ec in cand if ec not in CLASS] + [f"class:{ec}" for ec in CLASS if ec not in cand]
    ref_bad += [f"jtime:{j}" for j in judg if j not in J_TIME] + [f"parse:{x}" for x in parse_bad]
    ref_bad += [f"rel:{rid}" for rid in jrel if not any(("JUDGMENT_REVISION", "REVISED_BY", [rid]) in e["bases"] for e in edges)]
    ref_bad += [f"hid:{n['id']}" for n in node_rows if n["id"].startswith(("DN_H_", "H_"))]
    check("V14", "참조 무결성: node source·edge endpoint·변수·H fact·judgment relation·논리 제약 parse가 모두 유효",
          not ref_bad and len(cand) == 155 and len(judg) == 17, "|".join(ref_bad[:12]))
    # V15 forbidden constructs (§24)
    f_bad = [n["id"] for n in node_rows if re.search(r"UNKNOWN|LATENT|EPISODE|MISSING", n["id"] + n["action"], re.I)]
    check("V15", "UNKNOWN interface·latent/missing event·Episode·sampling 없음 (node는 candidate/judgment state에서만)", not f_bad,
          "|".join(f_bad))
    # V16 review projections without candidates
    rev_ap = sorted(k for k, v in projection.items() if v["decision"] == "REVIEW_REQUIRED")
    rp_bad = [k for k in rev_ap if any(cand[ec]["origin_atomic_prop_id"] == k for ec in cand)]
    check("V16", "projection REVIEW atomic prop(AP0002·AP0047·AP0126)에 node를 만들지 않음", rev_ap == ["AP0002", "AP0047", "AP0126"]
          and not rp_bad, "|".join(rev_ap))
    check("V17", "raw CSV SHA-256 일치(시작 시점)", raw_ok_start)
    # per-world expectations
    for name, desc, world, asg, exp in TEST_WORLDS:
        r = results[name]
        bad = []
        if r["logic"] != exp["logic"] or r["temporal"] != exp["temporal"]:
            bad.append(f"verdict {r['logic']}/{r['temporal']}")
        for g in exp.get("classes", []):
            if len({r["rep"].get(x, "?" + x) for x in g}) != 1 or not any(set(g) <= set(c) for c in r["classes"]):
                bad.append(f"class {g}")
        eset = {(a, b) for a, b, t, _ in r["edges"] if t != DURING}
        dset = {(a, b) for a, b, t, _ in r["edges"] if t == DURING}
        for a, b in exp.get("edges", []):
            if (r["rep"].get(a), r["rep"].get(b)) not in eset:
                bad.append(f"edge {a}->{b}")
        for a, b in exp.get("no_edges", []):
            if any(eid for x, y, t, eid in r["edges"] if x == r["rep"].get(a) and y == r["rep"].get(b)):
                bad.append(f"unexpected {a}->{b}")
        for a, b in exp.get("during", []):
            if (r["rep"].get(a), r["rep"].get(b)) not in dset:
                bad.append(f"during {a}⊂{b}")
        for x in exp.get("inactive", []):
            if x in r["active"] or (x in r["rep"] and r["rep"][x] in r["wnodes"] and x in r["wnodes"][r["rep"][x]]):
                bad.append(f"active {x}")
        for x in exp.get("active", []):
            if x not in r["active"]:
                bad.append(f"inactive {x}")
        for a, b in exp.get("separate", []):
            if r["rep"].get(a) == r["rep"].get(b):
                bad.append(f"merged {a},{b}")
        if "actor" in exp:
            nid, who = exp["actor"]
            if r["actor"].get(nid) != who:
                bad.append(f"actor {nid}={r['actor'].get(nid)}")
        for x, pref in exp.get("no_link", []):
            rx = r["rep"].get(x, "?" + x)
            if any((a == rx and b.startswith("DN_" + pref)) or (b == rx and a.startswith("DN_" + pref)) for a, b, t, _ in r["edges"]):
                bad.append(f"link {x}~{pref}*")
        check(f"W{name[2:4]}", f"test world {name}: {desc}", not bad,
              "|".join(bad) or f"{r['logic']}/{r['temporal']} nodes={len(r['wnodes'])} edges={len(r['edges'])} "
                               f"collapsed={r['classes']} viol={r['logic_violations'][:3]}")

    n_err = sum(1 for c in checks if c[2] == "ERROR")
    if mut:
        log.info("mutation %s: validation ERROR=%d (%s)", mut, n_err, "|".join(c[0] for c in checks if c[2] == "ERROR"))
        con.close()
        sys.exit(0 if n_err else 3)

    # ---------------- rows: 36 nodes
    def act_text(n):
        if n["cls"] == ATTR:
            return "해당 없음(ATTRIBUTE_ONLY: node 아님)"
        if n["cls"] == REV:
            return "검토 전 비활성(REVIEW_REQUIRED)"
        return render(n["act"])

    def time_text(n):
        kind, txt = n["time"]
        if not n["ec"] and n["sources"][0] in J_TIME:
            why = J_TIME[n["sources"][0]][1]
            return f"[시간] 조정 기사일 {txt}: {why}" if kind == "COURT_ENTRY_DATE" else f"[시간] 날짜 anchor 없음: {why}"
        if kind == "COURT_ENTRY_DATE":
            return f"[시간] 조정 기사일 {txt} = 이 조정 행위 자체의 기록일."
        if kind == "CLAIMED_DATE":
            return (f"[시간] 주장 날짜 {txt}(CT_{n['ec']}). E_{n['ec']}가 참일 때만 실제 시점 T_{n['ec']}의 범위. "
                    f"기록일 {n['record_date']}는 사건 날짜가 아님.")
        if kind == "RELATIVE_ONLY":
            return f"[시간] 상대시간만('{txt}'). 기록일 {n['record_date']}는 사건 날짜가 아님."
        if n["cls"] in NODE_CLASSES:
            return f"[시간] 날짜 없음. 기록일 {n['record_date'] or '미상'}는 사건 날짜로 쓰지 않음."
        return ""

    node_cols = ["dag_node_candidate_id", "source_candidate_ids", "node_class", "subject_surface", "action_core",
                 "object_surface", "historical_fact_id", "activation_condition", "same_occurrence_group_candidates", "notes"]
    nrows = []
    for n in sorted(node_rows, key=lambda x: (0 if x["ec"] else 1, x["id"])):
        hf = n["fact"] or n.get("attr_fact", "")
        same = "|".join(n["same"])
        note = " ".join(x for x in (n["note"], time_text(n)) if x)
        if n["cls"] in (ATTR, REV) and hf:
            note += f" [사실] 이 속성·내용이 다루는 사실 {hf}(H_ 자체는 node도 활성 조건도 아님)."
        nrows.append([n["id"], "|".join(n["sources"]), n["cls"], n["subject"], n["action"], n["object"], hf,
                      act_text(n), same, note])

    # ---------------- rows: 37 edges
    def basis_text(e):
        parts = []
        for bt, phrase, refs in e["bases"]:
            if bt in DATE_BASES:
                parts.append(f"{bt}: {nodes[refs[0]]['time'][1]} < {nodes[refs[1]]['time'][1]}")
            elif bt == "JUDGMENT_REVISION":
                parts.append(f"{bt}: {refs[0]} {phrase}")
            else:
                parts.append(f"{bt}: '{phrase}' ({'|'.join(refs)})")
        return "; ".join(parts)

    def ctb(e):
        out = []
        for x in (e["frm"], e["to"]):
            kind, txt = nodes[x]["time"]
            if kind == "COURT_ENTRY_DATE" and any(bt in DATE_BASES for bt, _, _ in e["bases"]):
                out.append(f"{x}: 조정 기사일 {txt}(행위 자체 기록일)")
            elif kind == "CLAIMED_DATE" and any(bt in DATE_BASES for bt, _, _ in e["bases"]):
                out.append(f"{x}: 주장 날짜 {txt}(claim 참일 때만)")
        return " / ".join(out) if out else "날짜 사용 안 함(상대 순서만; 기록일 미사용)"

    def cond_text(e):
        if e["kind"] == EVID:
            return "NEVER (EVIDENCE_ONLY: 시간 제약으로 강제하지 않음)"
        if e["kind"] == REVE:
            return "NEVER (REVIEW_REQUIRED: 검토 전 비활성)"
        base = f"active({e['frm']}) ∧ active({e['to']})"
        return base if e["cond"] is None else f"{base} ∧ {render(e['cond'])}"

    edge_cols = ["edge_candidate_id", "from_node_candidate", "to_node_candidate", "edge_type", "edge_strength",
                 "activation_condition", "source_basis", "claimed_time_basis", "hard_or_conditional",
                 "manual_review_required", "notes"]
    erows = [[e["id"], e["frm"], e["to"], e["etype"], e["strength"], cond_text(e), basis_text(e), ctb(e), e["kind"],
              "YES" if e["review"] else "NO", e["note"]] for e in edges]

    # ---------------- rows: 38 materialization rules
    rule_cols = ["rule_id", "step", "rule_type", "world_variable", "variable_level", "affected_node_candidates",
                 "affected_edge_candidates", "effect_if_true", "effect_if_false", "notes"]
    rules = [list(r_) for r_ in STEP_RULES]
    var_nodes, var_edges = {}, {}
    for n in node_rows:
        if n["act"] is not None and n["cls"] in NODE_CLASSES:
            for v in vars_of(n["act"]):
                var_nodes.setdefault(v, []).append(n["id"])
    for e in edges:
        if e["cond"] is not None:
            for v in vars_of(e["cond"]):
                var_edges.setdefault(v, []).append(e["id"])
    k = 0
    for v in sorted(set(var_nodes) | set(var_edges)):
        lvl = rvars[v]["variable_level"]
        if v in var_nodes:
            k += 1
            rules.append([f"MR{k:04d}", "STEP1", "NODE_ACTIVATION", v, lvl, "|".join(var_nodes[v]), "",
                          f"{', '.join(var_nodes[v])} 활성", "해당 node 비활성",
                          "H_* = occurrence 존재 여부 변수(node 아님)." if v.startswith("H_") else
                          "판단 act가 있었는지(내용의 참과 무관)." if v.startswith("J_") else "claim 고유 occurrence/act."])
        if v in var_edges:
            k += 1
            step = "STEP2" if v.startswith("ID_") else "STEP5"
            rtype = "IDENTITY_EDGE_CONDITION" if v.startswith("ID_") else "EDGE_CONDITION"
            rules.append([f"MR{k:04d}", step, rtype, v, lvl, "", "|".join(var_edges[v]),
                          f"edge {len(var_edges[v])}개의 조건 충족(다른 조건도 참이어야 함)", "해당 edge 비활성(선후 모름)",
                          "주장 날짜/상대시간 claim의 참." if v.startswith("E_") else
                          "상대시간 referent 가설." if v.startswith("REF_") else ""])
    for sv in same_vars:
        a, b = sv.split("_")[1:]
        k += 1
        pre = [c["formula"] for c in rcons if c["antecedent"] == sv and c["formula"].startswith("ID_")]
        gran = any(c["formula"] == f"¬{sv}" for c in rcons)
        live = any(sv == p[0] for p in same_pairs)
        rules.append([f"MR{k:04d}", "STEP3-4", "COLLAPSE", sv, "SAME_OCCURRENCE_HYPOTHESIS", f"{dn(a)}|{dn(b)}", "",
                      f"{dn(a)}·{dn(b)} 같은 class(추이 closure 포함) → 하나의 world node로 collapse, 실제 시점 공유"
                      if live else "효과 없음(두 referent 모두 node가 아님)",
                      "별개 occurrence로 유지(선후는 edge가 있을 때만)",
                      (f"전제: {pre[0]}가 참이어야 함(거짓이면 LOGICALLY_INVALID). " if pre else "")
                      + ("OCCURRENCE_GRANULARITY_ACT_LEVEL이 참이면 거짓이어야 함. " if gran else "")
                      + ("두 referent가 모두 node가 아니라(REVIEW) collapse 효과 없음." if not any(sv == p[0] for p in same_pairs) else "")])
    for v in sorted(ID_ALIAS):
        k += 1
        s, c = ID_ALIAS[v]
        same_dep = sorted({c_["antecedent"] for c_ in rcons if c_["formula"] == v and c_["antecedent"].startswith("SAME_")})
        rules.append([f"MR{k:04d}", "STEP2", "IDENTITY_APPLICATION", v, "IDENTITY_HYPOTHESIS",
                      "|".join(n["id"] for n in node_rows if n["subject"] == s and n["cls"] in NODE_CLASSES), "",
                      f"행위자 '{s}' → '{c}' 통합(actor chain)", f"행위자 '{s}' 별개로 유지",
                      ("이 동일성이 거짓이면 " + ", ".join(same_dep) + "는 거짓이어야 함(SAME→ID 전제). " if same_dep else "")
                      + "동일성만으로 node를 합치지 않음."])
    k += 1
    rules.append([f"MR{k:04d}", "STEP3", "GRANULARITY", "OCCURRENCE_GRANULARITY_ACT_LEVEL", "INTERPRETATION_HYPOTHESIS",
                  "DN_EC0107|DN_EC0111|DN_EC0119|DN_EC0120", "",
                  "행위 단위 개별화: 부르기·음식 주기 같은 다른 행위의 SAME은 거짓(RC0290–RC0293)", "장면 단위 collapse 허용", ""])

    # ---------------- write 36–38, tables
    write_csv(OUT_DIR / OUT_NODES, node_cols, nrows)
    write_csv(OUT_DIR / OUT_EDGES, edge_cols, erows)
    write_csv(OUT_DIR / OUT_RULES, rule_cols, rules)
    for table, fn in zip(NEW_TABLES, (OUT_NODES, OUT_EDGES, OUT_RULES)):
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv(?, header=true, all_varchar=true, "
                    f"quote='\"', escape='\"')", [str(OUT_DIR / fn)])
    db_counts = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in NEW_TABLES}
    digests_after = {t: table_digest(con, t) for t in protected}
    con.close()
    check("V18", "새 DuckDB table 3개 행 수 = CSV 행 수", db_counts == {NEW_TABLES[0]: len(nrows), NEW_TABLES[1]: len(erows),
                                                                    NEW_TABLES[2]: len(rules)}, str(db_counts))
    changed = [t for t in protected if digests_before[t] != digests_after[t]]
    check("V19", f"기존 DuckDB table {len(protected)}개 불변(시작·끝 digest)", not changed and len(protected) == 23, "|".join(changed))
    out_changed = [n for n in preserved if sha256(OUT_DIR / n) != out_before[n]]
    check("V20", f"기존 output 01~35 불변({len(preserved)}개)", not out_changed and len(preserved) == 35, "|".join(out_changed))
    check("V21", "raw CSV SHA-256 일치(끝 시점)", all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items()))
    write_csv(OUT_DIR / OUT_VALID, ["check_id", "description", "severity", "detail"], checks)

    # ---------------- summary 40
    cls_count = {c: sum(1 for n in node_rows if n["cls"] == c) for c in ALL_CLASSES}
    kind_count = {k_: sum(1 for e in edges if e["kind"] == k_) for k_ in EDGE_KINDS}
    type_count = {t: sum(1 for e in edges if e["etype"] == t) for t in EDGE_TYPES}
    basis_count = {}
    for e in edges:
        key = "+".join(sorted({bt for bt, _, _ in e["bases"]}))
        basis_count[key] = basis_count.get(key, 0) + 1
    date_only = sum(1 for e in edges if all(bt in DATE_BASES for bt, _, _ in e["bases"]))
    n_err = sum(1 for c in checks if c[2] == "ERROR")
    n_warn = sum(1 for c in checks if c[2] == "WARNING")
    summ = [["node_candidate_rows", len(node_rows), "event candidate 155 + judgment act 17"],
            ["dag_node_candidates(A–D)", sum(cls_count[c] for c in NODE_CLASSES), "ATTRIBUTE_ONLY·REVIEW 제외"]]
    summ += [[f"class:{c}", cls_count[c], ""] for c in ALL_CLASSES]
    summ += [["edge_candidates", len(edges), f"명시 근거 edge {len(edges) - date_only}, 날짜쌍만 근거 {date_only}"]]
    summ += [[f"kind:{k_}", kind_count[k_], ""] for k_ in EDGE_KINDS]
    summ += [["kind:CONDITIONAL(합계)", sum(kind_count[k_] for k_ in COND_KINDS), "CONDITIONAL_TEMPORAL+ON_IDENTITY+ON_SAME"]]
    summ += [[f"type:{t}", type_count[t], ""] for t in EDGE_TYPES]
    summ += [[f"basis:{b}", c, ""] for b, c in sorted(basis_count.items())]
    summ += [["court_act_nodes(기사일 anchor)", len(court_acts), "|".join(sorted(court_acts))],
             ["claimed_date_nodes", len(claimed), "|".join(claimed)],
             ["order_nodes_with_execution_record", len(orders) - len(no_exec), "|".join(o for o in orders if o not in no_exec)],
             ["order_nodes_without_execution(명령 node만)", len(no_exec), "|".join(no_exec)],
             ["materialization_rules", len(rules), "STEP 8행 + 변수별 행"],
             ["all_true_template_cycles", len(maxg["cycles"]), "모든 node·조건 참, collapse 없음"],
             ["review_atomic_props_without_nodes", "AP0002|AP0047|AP0126", "node를 만들지 않음(AP0126 '정소된 뒤'는 상대시간이지만 candidate 없음)"]]
    for name, desc, world, asg, exp in TEST_WORLDS:
        r = results[name]
        summ.append([f"test_world:{name}", f"{r['logic']}/{r['temporal']}",
                     f"active nodes {len(r['active'])}, world nodes {len(r['wnodes'])}, edges {len(r['edges'])}, "
                     f"collapsed {r['classes']}, cycles {len(r['cycles'])}, self-loops {len(r['self_loops'])}, flags {r['flags']}"])
    summ += [["raw_sha256", "UNCHANGED" if all(c[2] == "PASS" for c in checks if c[0] in ("V17", "V21")) else "CHANGED", ""],
             ["validation_error", n_err, ""], ["validation_warning", n_warn, ""]]
    write_csv(OUT_DIR / OUT_SUMMARY, ["metric", "value", "notes"], summ)

    # ---------------- log + special reports (§23)
    for row in summ:
        log.info("%s = %s %s", row[0], row[1], f"({row[2]})" if row[2] and len(str(row[2])) < 200 else "")

    def label(rp, r):
        mem = r["wnodes"][rp]
        n = nodes[rp]
        who = r["actor"].get(rp, n["subject"])
        return f"{n['action']}[{who}]{{{','.join(m[3:] for m in mem)}}}"

    for name in ("TW01_KIM_DEATH", "TW02_KIM_DEATH_AFTER_FALSE", "TW05_THEFT_TRUE", "TW06_THEFT_FALSE",
                 "TW07_JAMIDEOK_ID_TRUE", "TW08_JAMIDEOK_ID_FALSE", "TW09_ID_FALSE_SAME_TRUE", "TW10_TEMPORAL_ASSIGNMENT_CYCLE"):
        r = results[name]
        log.info("=== %s: logic=%s temporal=%s violations=%s flags=%s", name, r["logic"], r["temporal"],
                 r["logic_violations"], r["flags"])
        for rp in sorted(r["wnodes"]):
            log.info("  node %s", label(rp, r))
        by_id = {e["id"]: e for e in edges}
        n_date = 0
        for a, b, t, eid in sorted(r["edges"], key=lambda x: x[3]):
            bt = by_id[eid]
            if all(x in DATE_BASES for x, _, _ in bt["bases"]):
                n_date += 1
                continue
            log.info("  edge %s %s -%s-> %s [%s]", eid, label(a, r), t, label(b, r), bt["kind"])
        log.info("  (+ 날짜쌍만 근거인 활성 edge %d개)", n_date)
        if r["cycles"] or r["assignment_conflicts"]:
            log.info("  cycles=%s assignment_conflicts=%s", r["cycles"], r["assignment_conflicts"])
    log.info("validation: ERROR=%d WARNING=%d", n_err, n_warn)
    if n_err:
        sys.exit(1)


TEST_WORLDS_D = {name: world for name, _, world, _, _ in TEST_WORLDS}

if __name__ == "__main__":
    main()
