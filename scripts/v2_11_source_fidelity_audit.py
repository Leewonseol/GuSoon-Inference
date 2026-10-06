#!/usr/bin/env python3
"""GuSoon v2 SOURCE-FIDELITY / TRACEABILITY AUDIT (audit only).

Checks, in both directions, how the 117 immutable source-faithful propositions (data/raw) survive

  raw proposition -> atomic propositions -> event candidates / attestation-only / meta / review
                  -> claim-fact mapping (historical facts) / judgment states
                  -> DAG node / attribute / excluded-from-DAG -> explicit temporal edges

FORWARD:  raw -> derived (coverage, clause loss, actor/target, predicate, polarity, epistemic status,
          scope, open set, time, place, cause/responsibility, nested testimony, contradictions,
          split, merge/identity, judgment content, DAG projection, temporal edges).
BACKWARD: derived -> raw (provenance of atomic props, event candidates, historical facts, judgment
          states, interpretation/identity/same-occurrence variables, DAG nodes, explicit edges).

Automated detectors produce findings; every finding must be adjudicated by hand in ADJUDICATION
(severity CRITICAL / MAJOR / MINOR / NO_ISSUE, status CONFIRMED / REVIEW / NO_ISSUE, with a reason).
An unadjudicated finding is a validation ERROR — this is also how the mutation tests are caught.

Nothing is written to data/raw, to existing outputs or to the DuckDB file (opened read-only).
Only output/45–50 (or the next free block of six numbers) and a log are written.

Usage:
  python3 scripts/v2_11_source_fidelity_audit.py                 # audit + write reports
  python3 scripts/v2_11_source_fidelity_audit.py --mutation NAME # inject a fault in memory, validate, write nothing
"""

import argparse
import copy
import csv
import hashlib
import logging
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "database" / "gusun_v2.duckdb"
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
SHA_PATH = RAW_DIR / "gusun_research_v2_SHA256SUMS.txt"
RAW_FILES = {"source_records": "gusun_research_v2_source_records.csv",
             "source_faithful_propositions": "gusun_research_v2_source_faithful_propositions.csv",
             "person_membership": "gusun_research_v2_person_membership.csv",
             "search_log": "gusun_research_v2_search_log.csv"}
OUT_NAMES = ["raw_to_derived_traceability", "source_fidelity_audit", "derived_to_raw_provenance_audit",
             "fidelity_issues", "fidelity_validation", "fidelity_summary"]
MUTATIONS = ["false_statement_target", "open_set_closed", "force_hanbijang_identity", "doubted_to_false",
             "record_date_as_occurrence", "nested_to_object_fact", "drop_cause_attribute", "drop_raw_proposition",
             "add_unsupported_actor", "date_edge_to_causal"]

VERDICTS = ["PRESERVED", "PRESERVED_AS_ATTRIBUTE", "PRESERVED_AS_ATTESTATION_ONLY", "PRESERVED_AS_META_PROCEDURAL",
            "INTENTIONALLY_DEFERRED", "REVIEW_REQUIRED", "POSSIBLE_OMISSION"]
NODE_CLASSES = ("MATERIAL_EVENT_NODE", "INVESTIGATIVE_EVENT_NODE", "SPEECH_OR_JUDGMENT_EVENT_NODE", "ORDER_EVENT_NODE")
DATE_BASES = ("CLAIMED_DATE_ORDER", "COURT_ENTRY_DATE_ORDER", "CLAIMED_VS_COURT_DATE_ORDER")
COURT_MODES = ("MINISTERIAL_PROPOSAL", "ROYAL_ORDER", "ROYAL_JUDGMENT", "ROYAL_DISCUSSION", "DIRECT_STATEMENT",
               "COURT_DISCUSSION")
ALLOWED_EDGE_TYPES = ("TEMPORAL_BEFORE", "TEMPORAL_AFTER", "TEMPORAL_DURING", "PROCEDURAL_PRECEDES",
                      "PROCEDURAL_TRIGGER_IF_EXPLICIT")

# meaning-bearing words whose presence in a derived object must be supported by its raw provenance
# (key: word searched in the derived text; value: raw-text forms that support it)
LEXICON = {
    "지목": ["지목", "지명"], "사주": ["사주"], "조작": ["꾸미", "꾸몄", "꾸며", "조작"], "확정": ["확정"],
    "자백": ["자백"], "고문": ["고문"], "살해": ["살해", "죽였"], "처형": ["처형"], "집행": ["집행"],
    "화적": ["화적"], "질병": ["질병", "병들", "병이", "병으로", "병에"], "전염병": ["전염병"], "석방": ["석방"], "허위": ["허위", "거짓", "허황", "누명"],
    "거짓": ["거짓", "허황", "꾸며"], "무고": ["무고"], "누명": ["누명"], "회유": ["꾀", "회유"], "위협": ["위협"],
    "최종": ["최종"], "책임": ["책임", "죄안", "때문"], "인과": ["인과"], "명단": ["명단", "성명", "이름"],
}
DOUBT_MARKERS = ["이치에 맞지 않", "듯", "의심", "확정하지 못"]
NEG_MARKERS = ["없다", "없었", "없는", "없이", "않", "못", "모르", "면하"]
OPEN_GROUP_WORDS = ["평민들", "응답자들", "체포자들", "관련자들", "죄수", "일행", "사람들"]
SCOPE_WORDS = ["은밀히", "방향", "듯", "약간", "일부", "전적으로"]
TRIGGER_MARKERS = ["따라", "따른", "대로", "으로", "꾀어", "분부"]
CONTRADICTION_PAIRS = [  # (description, EC a, EC b) — both must survive in their original form
    ("5/12 도난 부재 방향 vs 6/13 도난 실재(정조)", "EC0022", "EC0143"),
    ("5/27 이조원 도난 부재 방향 vs 6/13 홍대협 약간의 도난 실재", "EC0046", "EC0131"),
    ("자미덕: 한 비장의 지휘 vs 한재욱: 은밀한 사주 부인", "EC0114", "EC0126"),
    ("이조원: 구순이 구성한 죄안 때문에 사망 vs 홍대협: 질병 때문", "EC0038", "EC0138"),
    ("이조원: 죄안 때문에 사망 vs 정조: 전염병", "EC0038", "EC0144"),
    ("이조원: 구순이 지세랑을 만듦 vs 정조: 예전부터 쓰던 말", "EC0031", "EC0148"),
    ("이조원: 구순이 지세랑을 만듦 vs 정조: 창작 죄 면함", "EC0031", "EC0149"),
    ("응답자들: 구순이 도난 상황을 꾸밈 vs 나복: 도적이 돈과 물품을 훔침", "EC0012", "EC0070"),
    ("이조원: 하급 보조자가 구순의 가객 vs 한재욱: 구순과 평생 모르는 사이", "EC0043", "EC0127"),
    ("명업: 처음 사실대로 말함 vs 명업: 도적이 없었다는 취지로 바꿈", "EC0077", "EC0079"),
]

# ---------------------------------------------------------------- manual adjudication of every automated finding
# key -> (severity, status, dimension, direction, note). status: CONFIRMED (real problem), REVIEW (needs a human
# decision; usually already flagged upstream), NO_ISSUE (detector hit explained, meaning preserved).
ADJUDICATION = {
    # ---- actor / target
    "ACTOR_INVERSION:DN_EC0009": ("CRITICAL", "CONFIRMED", "ACTOR", "INVERSION",
        "P0007 '무고한 평민들이 모진 형벌을 받았다'(피동). EC0009는 '모진 형벌을 받음'으로 맞지만 DAG node(36)는 "
        "subject_surface=평민들, action='형벌 가함(평민들)'이라 형벌을 받은 쪽이 행위 주체 칸에 놓임(materialize의 actor=subject). "
        "가한 쪽은 원문에 없음. EC/AP 층은 정상, DAG 층에서만 actor/target이 뒤집힘."),
    "ACTOR_INVERSION:DN_EC0056": ("CRITICAL", "CONFIRMED", "ACTOR", "INVERSION",
        "P0041 '여러 죄수가 참혹한 형벌을 받았다'(피동). DAG node는 subject=여러 죄수, action='형벌 가함(여러 죄수)'. "
        "EC0056은 정상. DN_EC0009와 같은 유형."),
    "IDENTITY_IN_EDGE:TE0010": ("MAJOR", "REVIEW", "TARGET", "IDENTITY_USED_AS_FIXED",
        "TE0010 지시(EC0096: '풍각 김생원·흥덕 김생원' 체포) → 체포(EC0097: '김명신·김갑득', '병사 분부에 따라'). "
        "두 node를 잇는 근거는 '분부'의 referent가 EC0096이라는 것과 풍각 김생원=김명신·흥덕 김생원=김갑득 동일성인데, "
        "활성 조건에는 ID_BYEONGSA_SRC2_006__IGWANGSEOP만 있고 ID_PUNGGAK_KIMSAENGWON__KIMMYEONGSIN·"
        "ID_HEUNGDEOK_KIMSAENGWON__KIMGAPDEUK(둘 다 FREE 가설)는 없음 → 동일성 가설이 이 edge에서는 확정처럼 쓰임. "
        "원문 직접 식별(P0067·P0068, HIGH)이라 위험은 낮지만 ERROR 후보로 보고."),
    # ---- predicate / scope (lexicon)
    "LEXICON:J:J_JEONGJO_17930512_THEFT": ("MAJOR", "CONFIRMED", "SCOPE", "STRENGTHENING",
        "P0016 원문은 '당시 장계·조사에 따라 도난 자체가 없었다는 방향을 받아들임'. judgment_states·DAG node·"
        "repaired_world_variables 설명(label)은 '이형원 장계·조사 결과(도난 조작 방향) 수용'으로, 응답자들(P0009)·"
        "이조원(P0021)의 '구순이 꾸몄다'를 정조 판단 내용에 옮김('도난 없음 방향' → '구순이 조작했다는 방향'). "
        "label만의 문제: 논리층(EC0022 ↔ ¬H, stance ACCEPTS/INTERMEDIATE, '종결된 판단이 아님')은 원문과 맞음.", ["P0016"]),
    "LEXICON:DAG:DN_J_JEONGJO_17930512_THEFT": ("MAJOR", "CONFIRMED", "SCOPE", "STRENGTHENING",
        "J_JEONGJO_17930512_THEFT label과 같은 문제(DAG node action_core에 복사됨).", ["P0016"]),
    "LEXICON:VAR:J_JEONGJO_17930512_THEFT": ("MAJOR", "CONFIRMED", "SCOPE", "STRENGTHENING",
        "J_JEONGJO_17930512_THEFT label과 같은 문제(repaired_world_variables notes에 복사됨).", ["P0016"]),
    "LEXICON:MAP:EC0067->H_GUSUN_LARGE_ARMED_BAND_INTRUDED": ("MAJOR", "REVIEW", "SCOPE", "STRENGTHENING",
        "RC0212 E_EC0067 → H_GUSUN_LARGE_ARMED_BAND_INTRUDED. P0049(나복→명업)는 '도적 30여 명'만 말함. H의 술어는 "
        "'큰 무리의 화적(도적떼)이 들었음'으로 규모(30여 명)와 성격(화적: 이조원 P0018·홍대협 P0099의 표현)을 한 사실에 합침. "
        "규모 claim만 참이어도 '화적'까지 참이 되도록 함의가 걸림. historical_facts.manual_review_required=YES로 이미 표시됨."),
    "LEXICON:MAP:EC0038->H_KIM_DEATH_DIRECT_CAUSE_CHARGE_NOT_DISEASE": ("MINOR", "REVIEW", "CAUSE", "STRENGTHENING",
        "CAUSELEVEL_EC0038=DIRECT_CAUSE 해석일 때 E_EC0038 ↔ H('직접 사인이 질병(전염병 포함)이 아니라 죄안에 따른 처우 자체'). "
        "P0025는 질병을 배제한다고 말하지 않음 — '직접 사인은 하나'라는 해석을 더해야 질병 배제가 나옴. 해석 가설 분기 안에서만 작동하고 "
        "RESPONSIBILITY 해석이 따로 있어 원인/책임 구분 자체는 보존됨."),
    "LEXICON:MAP:EC0040->H_KIM_WIFE_DEATH_CAUSE_EPIDEMIC": ("MINOR", "REVIEW", "CAUSE", "STRENGTHENING",
        "RC0229 SENSE_EC0040=CAUSAL_FOLLOWING_EXCLUDING_EPIDEMIC일 때 E_EC0040 → ¬H(아내 사인 전염병). P0026 '김명신이 죽은 뒤 따라 "
        "죽었다'는 전염병을 배제한다고 말하지 않음 — '따라'를 '전염병 아닌 원인으로 뒤따름'으로 읽는 해석 분기에서만 배제가 생김. "
        "SEQUENCE_ONLY 분기가 따로 있어 원문 의미 자체는 열려 있음."),
    # ---- polarity / epistemic / judgment strength
    "J_STRENGTH:J_IJOWON_17930527_THEFT": ("MINOR", "CONFIRMED", "EPISTEMIC", "STRENGTHENING",
        "J_IJOWON_17930527_THEFT stance=REJECTS/STRONG이 EC0024(DOUBTED: '이치에 맞지 않는다'), EC0046('도난이 없었다는 "
        "방향'), EC0030('꾸몄다고 주장')을 한 판단으로 묶음. 요약 강도가 의심·방향 표현보다 강함. claim 층(EC0024 DOUBTS·evidence only, "
        "EC0046 notes '방향')에는 원래 강도가 남아 있고 J는 world 제약이 없음.", ["P0018", "P0032"]),
    "SCOPE_IFF:EC0022": ("MINOR", "CONFIRMED", "SCOPE", "STRENGTHENING",
        "AP0024 '…도난 자체가 없었다는 방향을 받아들임' → EC0022 'STATE NEGATED 도난 자체 있었음', RC E_EC0022 ↔ ¬H. "
        "'방향'(중간 판단)이 EC 술어에서 빠짐. projection reason·claim_scope('방향·중간 판단')·J stance INTERMEDIATE에 보존."),
    "SCOPE_IFF:EC0046": ("MINOR", "CONFIRMED", "SCOPE", "STRENGTHENING",
        "AP0050 '도난이 없었다는 방향의 판단을 보고' → EC0046 'NEGATED 구순 사건의 도난 있었음', E ↔ ¬H. '방향'이 EC 술어에서 빠짐. "
        "projection reason·claim_scope에 보존."),
    "SCOPE_IFF:EC0126": ("MAJOR", "CONFIRMED", "SCOPE", "STRENGTHENING",
        "P0093 한재욱 '자미덕을 은밀히 사주한 일이 없다'. RC0235 E_EC0126 ↔ ¬H_HAN_JAEUK_INSTIGATED_JAMIDEOK인데 H의 술어는 "
        "'자미덕을 사주함'(은밀히 없음). 부인이 참이고(은밀한 사주는 없음) 공개적 사주는 있었던 world가 논리적으로 배제됨 → 부인 범위가 "
        "원문보다 넓어짐. 맞는 형태는 ¬H → E_EC0126 방향뿐. RC0235·RC0259–RC0261 reason에 '은밀히 범위 검토 필요'가 적혀 있으나 식은 IFF."),
    "EC_POLARITY_LABEL:EC0149": ("MINOR", "CONFIRMED", "EPISTEMIC", "STRENGTHENING",
        "P0109 '구순이 지세 호칭을 스스로 만들어냈다는 죄는 면하게 됐다고 판단'. EC0149는 'ACTION NEGATED 지세 호칭을 스스로 "
        "만들어냄'(사실 부정처럼 읽힘). 법적 면죄인지 사실 부정인지는 SENSE_EC0149(FACTUAL_NEGATION/LEGAL_CLEARANCE)로 보존되고 "
        "¬H 연결은 FACTUAL_NEGATION일 때만."),
    # ---- nested testimony (inner layer kept only at attestation level)
    "NESTED_INNER:P0008": ("MINOR", "CONFIRMED", "NESTED", "WEAKENING",
        "이형원 > 회동 조사 응답자들 > (원한). AP0012 depth 2·embedded_speaker 보존. CONTENT projection이라 EC0011은 내용(원한) "
        "자체이고 '응답자들이 그렇게 진술했다'(INNER)는 world 변수·DAG node가 없음. 세 층이 합쳐지지는 않음(ATT 고정, E 자유)."),
    "NESTED_INNER:P0009": ("MINOR", "CONFIRMED", "NESTED", "WEAKENING", "P0008과 같은 구조(AP0013 → EC0012)."),
    "NESTED_INNER:P0010": ("MINOR", "CONFIRMED", "NESTED", "WEAKENING", "P0008과 같은 구조(AP0014–AP0016 → EC0013–EC0015)."),
    "NESTED_INNER:P0011": ("MINOR", "CONFIRMED", "NESTED", "WEAKENING",
        "이형원 > 진술 주체 미상 > (체포자들 = 미워하던 사람들). AP0017 → EC0016 내용만."),
    "NESTED_INNER:P0039": ("MINOR", "CONFIRMED", "NESTED", "WEAKENING",
        "윤노동 > 구순('도적을 만났다'). AP0059 → EC0050 '구순 도적을 만남'(내용, INTERP_EC0050). 구순이 그렇게 말한 발화 "
        "행위는 node·변수가 없음(같은 구조의 P0003은 SPEECH_EVENT EC0002로 보존됨)."),
    "NESTED_INNER:P0049": ("MINOR", "CONFIRMED", "NESTED", "WEAKENING",
        "명업 > 나복 > (도적 30여 명·횃불·지세대감 자칭·돈과 물품). AP0075–AP0079 depth 2–3 보존, EC0066–EC0070은 내용. "
        "'명업의 진술 존재'(ATT 고정) ≠ '나복이 그렇게 말함'(변수 없음; 알림 행위 EC0065만 별도) ≠ '실제 30여 명'(E_EC0067 자유). "
        "합쳐지지는 않으나 INNER 층은 attestation에만 남음."),
    "NESTED_INNER:P0060": ("MINOR", "CONFIRMED", "NESTED", "WEAKENING",
        "이진욱 > 한재욱('처남매부', '힘이 세다'). AP0094·AP0095 → EC0085·EC0086 내용만. 경고 발언(EC0087)은 별도 SPEECH."),
    "NESTED_INNER:P0088": ("MINOR", "CONFIRMED", "NESTED", "WEAKENING",
        "한재욱 > 유제희('직접 염탐해 알아냈다'). AP0130 → EC0118 '염탐' 행위(내용). 유제희의 그 말은 변수가 없음."),
    "NESTED_DEPTH:P0071": ("NO_ISSUE", "NO_ISSUE", "NESTED", "",
        "조계완 > 구순의 질문. 진술자가 직접 들은 발화 행위라 depth 1(발화 행위가 보고된 사건)로 표기; 내용은 승격하지 않음(EC0099 "
        "SPEECH_ACT/ASSERTED). 같은 구조의 P0073(AP0112)은 depth 2로 표기 — 표기 관행 차이일 뿐 하류 영향 없음."),
    "NESTED_DEPTH:P0090": ("NO_ISSUE", "NO_ISSUE", "NESTED", "",
        "한재욱 > 유제희의 권고('다시 물어보라'). 한재욱이 직접 들은 발화라 AP0134 depth 1; 석단 공초 내용(AP0133)은 depth 3으로 "
        "따로 두고 승격하지 않음."),
    "OPEN_SET_CLOSED:AP0171": ("NO_ISSUE", "NO_ISSUE", "OPEN_SET", "",
        "P0117 '관찰사·비변사제조 등을 역임' — 관직 나열의 '등'이며 인물 membership 집합이 아님(2차 배경 자료)."),
    "OPEN_SET_CLOSED_RAW:P0117": ("NO_ISSUE", "NO_ISSUE", "OPEN_SET", "",
        "P0117 '관찰사·비변사제조 등을 역임' — 관직 나열의 '등'이며 인물 membership 집합이 아님(2차 배경 자료)."),
    "NESTED_DEPTH:P0074": ("NO_ISSUE", "NO_ISSUE", "NESTED", "",
        "조계완이 직접 겪은 행위(서찰을 건네며 요구함)라 depth 1이 맞음. raw NESTED_TESTIMONY는 '진술됨' 표기."),
    # ---- clause coverage (split audit)
    "CLAUSE:P0036:있어": ("MINOR", "CONFIRMED", "PREDICATE", "WEAKENING",
        "'예전 호중 화적도 사용한 적이 있어 이번에 처음 생긴 말이 아닌 듯' — 근거→추론(이유 연결) 구조가 AP0055(근거)·AP0056(추론, "
        "ATTESTATION_ONLY)로 나뉘고 연결은 shared_utterance_group UG_P0036과 projection reason에만 남음."),
    "CLAUSE:P0060:세니": ("MINOR", "CONFIRMED", "PREDICATE", "WEAKENING",
        "'변지돌이 힘이 세니 조심하라' — 이유 연결이 AP0095·AP0096 분리 후 UG_P0060에만 남음."),
    "CLAUSE:P0090:했으니": ("MINOR", "CONFIRMED", "PREDICATE", "WEAKENING",
        "'석단 공초에서 김명신이 도적 괴수라고 했으니 자미덕에게 다시 물어보라' — 이유 연결이 AP0133·AP0134 분리 후 UG_P0090에만 남음."),
    # ---- temporal
    "STATE_STRICT_EDGE:TE0005": ("MAJOR", "CONFIRMED", "TEMPORAL", "STRENGTHENING",
        "P0075 '(자미덕 체포 전) 재돌은 아산에 나가 있었다'. TE0005는 체류 상태(EC0103) TEMPORAL_BEFORE 체포(EC0104)이고 "
        "v2_09의 선후 edge 의미는 'a가 끝난 뒤 b 시작'. 원문은 체포 무렵(전) 재돌이 아산에 있었다는 뜻이며 체류가 체포 전에 끝났다는 "
        "뜻이 아님(체포 때도 아산에 있었을 가능성이 높음) → 시간 의미가 강해짐."),
    "STATE_STRICT_EDGE:TE0007": ("MAJOR", "CONFIRMED", "TEMPORAL", "STRENGTHENING",
        "P0079 '그 후 매일 자미덕을 방안으로 불러들였다'. TE0007은 구류 상태(EC0106) TEMPORAL_BEFORE 호출(EC0107) = '구류가 끝난 뒤 "
        "호출 시작'. 원문 흐름(다모방 구류 중 매일 방으로 불러들임)은 호출이 구류 기간 안이라는 뜻 → 원문과 충돌할 수 있는 강화. "
        "'그 후'의 기준점은 구류 시작."),
    "TRIGGER_NOT_EXPLICIT:TE0015": ("MINOR", "REVIEW", "TEMPORAL", "STRENGTHENING",
        "PROCEDURAL_TRIGGER_IF_EXPLICIT인데 근거 문구('내려가 자세히 조사해 오라', '안핵어사 홍대협 복명')에 '~에 따라' 같은 연결어가 "
        "없음. 선후(명령 5/28 → 안핵 신문)는 직함으로 지지되지만 edge 유형이 원문보다 강함. 37에서 manual_review_required=YES."),
    "TRIGGER_NOT_EXPLICIT:TE0016": ("MINOR", "REVIEW", "TEMPORAL", "STRENGTHENING", "TE0015와 같음('안핵어사')."),
    "REVISION_NOT_IN_RAW:TE0045": ("MINOR", "REVIEW", "TEMPORAL", "STRENGTHENING",
        "JR002(홍대협 5/28 → 6/13 지세) REVISED_BY는 원문에 '수정' 표현이 없음(P0036 유보 추론, P0100 기원 미확정). "
        "날짜 순서 자체는 기사일로 맞고, JR002 notes가 '수정인지 정밀화인지 REVIEW'로 표시."),
    "EDGE_PHRASE_PARAPHRASE:TE0011": ("NO_ISSUE", "NO_ISSUE", "TEMPORAL", "",
        "근거 문구 '그 소장으로'는 AP0084의 풀어쓰기. 원문 P0053 '소장을 올려 체포령이 내려졌다'와 뜻이 같음."),
    "EDGE_PHRASE_PARAPHRASE:TE0013": ("NO_ISSUE", "NO_ISSUE", "TEMPORAL", "",
        "근거 문구 '꾀어 그 공초를 내게 함'은 AP0069 표현. 원문 P0043 '변가의 처를 꾀어 … 공초를 내게 했다'."),
}


log = logging.getLogger("v2_source_fidelity_audit")


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
    return [{c: ("" if v is None else str(v)) for c, v in zip(cols, r)} for r in cur.fetchall()]


def read_raw(name):
    with open(RAW_DIR / RAW_FILES[name], encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, header, rows):
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing output {path}")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def norm(s):
    return re.sub(r"[\s·,./()'\"~\-]+", "", s or "")


def lcs_len(a, b):
    best = 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


ENDINGS = r"(했다고|하였다고|했으나|했다|하였다|하고|하며|하여|해서|하는|하던|한다|되었다고|되었다|됐다고|되어|된|됨|함|" \
          r"으로|에서|에게|이라고|라고|이라|이며|이고|이었다고|이었다|였다고|였다|을|를|이|가|은|는|의|와|과|도|만|에|로|고|며|다)$"
STOP = set("했다 하였다 했다고 진술 진술됨 진술했다고 보고 보고됨 주장 판단 평가 평가됨 말함 말했다고 그 이 등 및 함 됨 있다 없다".split())
INFLECT = {"잡아": "잡", "올려": "올", "불러": "부", "맡기": "맡", "통해": "통", "따라": "따"}


def content_tokens(s):
    out = []
    for w in re.split(r"[\s·,./()'\"~\-]+", s or ""):
        w = re.sub(ENDINGS, "", w)
        if len(w) >= 2 and w not in STOP:
            out.append(w)
    return out


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--mutation", default="")
    args = ap_.parse_args()
    mut = args.mutation
    LOG_DIR.mkdir(exist_ok=True)
    handlers = [logging.StreamHandler(sys.stdout)]
    if not mut:
        handlers.append(logging.FileHandler(LOG_DIR / "v2_source_fidelity_audit.log", mode="w", encoding="utf-8"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=handlers, force=True)
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
    existing = sorted(p.name for p in OUT_DIR.glob("*.csv"))
    used = {int(m[1]) for n in existing if (m := re.match(r"^(\d\d)_", n))}
    start = 45
    while any(n in used for n in range(start, start + len(OUT_NAMES))):
        start += 1
    out_files = {k: f"{start + i:02d}_v2_{k}.csv" for i, k in enumerate(OUT_NAMES)}
    out_before = {n: sha256(OUT_DIR / n) for n in existing}
    con = duckdb.connect(str(DB_PATH), read_only=True)
    tables = sorted(t[0] for t in con.execute("SHOW TABLES").fetchall())
    digests_before = {t: table_digest(con, t) for t in tables}

    # ---------------- load (raw from data/raw; derived from the DuckDB file)
    raw = {k: read_raw(k) for k in RAW_FILES}
    db_raw_ok = all(
        sorted(tuple(r.values()) for r in fetch(con, f"SELECT * FROM {k}")) ==
        sorted(tuple(("" if v is None else v) for v in r.values()) for r in raw[k]) for k in RAW_FILES)
    P = {r["prop_id"]: r for r in raw["source_faithful_propositions"]}
    SRC = {r["source_record_id"]: r for r in raw["source_records"]}
    D = dict(
        AP={r["atomic_prop_id"]: r for r in fetch(con, "SELECT * FROM atomic_propositions")},
        PD={r["atomic_prop_id"]: r for r in fetch(con, "SELECT * FROM event_projection_decisions")},
        EC={r["event_candidate_id"]: r for r in fetch(con, "SELECT * FROM historical_event_candidates")},
        SUP=fetch(con, "SELECT * FROM event_candidate_support"),
        MAP=fetch(con, "SELECT * FROM claim_fact_mapping"),
        H={r["historical_fact_id"]: r for r in fetch(con, "SELECT * FROM historical_facts")},
        J={r["judgment_state_id"]: r for r in fetch(con, "SELECT * FROM judgment_states")},
        JR={r["relation_id"]: r for r in fetch(con, "SELECT * FROM judgment_state_relations")},
        VAR={r["variable_id"]: r for r in fetch(con, "SELECT * FROM repaired_world_variables")},
        RC=fetch(con, "SELECT * FROM repaired_logical_constraints"),
        DN={r["dag_node_candidate_id"]: r for r in fetch(con, "SELECT * FROM dag_node_projection")},
        TE={r["edge_candidate_id"]: r for r in fetch(con, "SELECT * FROM temporal_edge_candidates")},
        EV=fetch(con, "SELECT * FROM temporal_edge_evidence"),
        ER=fetch(con, "SELECT * FROM entity_resolution_candidates"),
        OS={r["set_id"]: r for r in fetch(con, "SELECT * FROM open_set_normalized")},
    )
    clean = copy.deepcopy(D)

    # ---------------- mutations (in memory only)
    def mutate(D):
        if mut == "false_statement_target":
            D["EC"]["EC0113"]["predicate"] = "이집거와 대질할 때 거짓으로 이집거를 지목함"
        elif mut == "open_set_closed":
            for t, k in (("AP", "AP0120"), ("EC", "EC0109")):
                D[t][k]["set_status"] = "CLOSED_LIST"
                D[t][k]["predicate"] = D[t][k]["predicate"].replace(" 등", "")
            D["OS"]["OS13"]["is_open"] = "FALSE"
        elif mut == "force_hanbijang_identity":
            D["VAR"]["ID_HANBIJANG__HANJAEUK"]["fixed_or_free"] = "FIXED_TRUE (IDENTITY)"
            for k in ("EC0107", "EC0111"):
                D["EC"][k]["subject_surface"] = "한재욱"
                D["DN"]["DN_" + k]["subject_surface"] = "한재욱"
        elif mut == "doubted_to_false":
            D["EC"]["EC0024"]["polarity"] = "NEGATED"
            for m in D["MAP"]:
                if m["event_candidate_id"] == "EC0024":
                    m.update(claim_relation="ASSERTS_FALSE", claim_polarity="NEGATED", logical_form="E ↔ ¬H")
        elif mut == "record_date_as_occurrence":
            for k in ("EC0097", "EC0104"):
                D["EC"][k]["occurrence_lunar_text"] = D["AP"][D["EC"][k]["origin_atomic_prop_id"]]["record_lunar_date"]
        elif mut == "nested_to_object_fact":
            D["AP"]["AP0076"].update(attestation_depth="1", claim_level="OUTER_ATTESTATION", embedded_speaker="")
            D["EC"]["EC0067"]["epistemic_status"] = "OFFICIAL_FINDING"
            D["VAR"]["E_EC0067"]["fixed_or_free"] = "FIXED_TRUE (RECORD_ANCHOR)"
        elif mut == "drop_cause_attribute":
            del D["EC"]["EC0054"]
            D["MAP"] = [m for m in D["MAP"] if m["event_candidate_id"] != "EC0054"]
            del D["DN"]["DN_EC0054"]
        elif mut == "drop_raw_proposition":
            gone = [k for k, a in D["AP"].items() if a["parent_prop_id"] == "P0050"]
            for k in gone:
                del D["AP"][k]
                D["PD"].pop(k, None)
            for e in [e for e, r in D["EC"].items() if r["origin_atomic_prop_id"] in gone]:
                del D["EC"][e]
                D["DN"].pop("DN_" + e, None)
        elif mut == "add_unsupported_actor":
            D["EC"]["EC0112"]["subject_surface"] = "자미덕·이집거·한재욱"
        elif mut == "date_edge_to_causal":
            D["TE"]["TE0100"]["edge_type"] = "CAUSAL_CAUSES"

    if mut:
        mutate(D)
    AP, PD, EC, MAP, H, J, VAR, DN, TE = (D[k] for k in ("AP", "PD", "EC", "MAP", "H", "J", "VAR", "DN", "TE"))

    # ---------------- indexes
    aps_of = defaultdict(list)
    for a in AP.values():
        aps_of[a["parent_prop_id"]].append(a["atomic_prop_id"])
    ecs_of_ap = defaultdict(list)
    for e in EC.values():
        ecs_of_ap[e["origin_atomic_prop_id"]].append(e["event_candidate_id"])
    map_of = defaultdict(list)
    for m in MAP:
        map_of[m["event_candidate_id"]].append(m)
    j_of = defaultdict(list)
    for jid, j in J.items():
        for e in j["event_candidate_ids"].split("|"):
            if e:
                j_of[e].append(jid)
    for m in MAP:
        if m["judgment_state_id"] and m["judgment_state_id"] not in j_of[m["event_candidate_id"]]:
            j_of[m["event_candidate_id"]].append(m["judgment_state_id"])
    ev_of = defaultdict(list)
    for r in D["EV"]:
        ev_of[r["edge_candidate_id"]].append(r)
    edges_of_node = defaultdict(list)
    for t in TE.values():
        edges_of_node[t["from_node_candidate"]].append(t["edge_candidate_id"])
        edges_of_node[t["to_node_candidate"]].append(t["edge_candidate_id"])

    def is_date_only(eid):
        return all(r["basis_type"] in DATE_BASES for r in ev_of[eid])

    def parent_of_ec(e):
        return AP[EC[e]["origin_atomic_prop_id"]]["parent_prop_id"] if e in EC and EC[e]["origin_atomic_prop_id"] in AP else ""

    def rawtext(p):
        r = P[p]
        return " ".join((r["subject"], r["predicate"], r["object_or_content"], r["occurrence_lunar_text"],
                         r["historical_place"], r["named_entities"], r["notes"]))

    def raw_core(p):
        r = P[p]
        return " ".join((r["subject"], r["predicate"], r["object_or_content"], r["notes"]))

    def raw_of_j(jid):
        ps = {parent_of_ec(e) for e in J[jid]["event_candidate_ids"].split("|") if e and e in EC}
        for apid in re.findall(r"AP\d{4}", J[jid]["notes"]):
            if apid in AP:
                ps.add(AP[apid]["parent_prop_id"])
        return sorted(p for p in ps if p)

    findings = {}

    def find(key, detector, props, obj, dimension, detail):
        findings[key] = dict(key=key, detector=detector, props=sorted(set(p for p in props if p)), obj=obj,
                             dimension=dimension, detail=detail)

    # ================================================================ detectors
    # D01 coverage / omission (forward trace completeness)
    for p in P:
        if not aps_of[p]:
            find(f"OMISSION_NO_ATOMIC:{p}", "D01_COVERAGE", [p], p, "COVERAGE", "raw proposition에 atomic proposition이 없음")
    for a, r in AP.items():
        if r["parent_prop_id"] not in P:
            find(f"ATOMIC_WITHOUT_RAW:{a}", "D01_COVERAGE", [], a, "PROVENANCE", "parent_prop_id가 raw에 없음")
        if a not in PD:
            find(f"OMISSION_NO_PROJECTION:{a}", "D01_COVERAGE", [r["parent_prop_id"]], a, "COVERAGE", "projection 결정 없음")
        elif PD[a]["decision"] == "EVENT_PROJECTABLE" and not ecs_of_ap[a]:
            find(f"OMISSION_NO_EVENT:{a}", "D01_COVERAGE", [r["parent_prop_id"]], a, "COVERAGE",
                 f"EVENT_PROJECTABLE인데 event candidate 없음 (결정상 {PD[a]['event_candidate_id']})")
    for e, r in EC.items():
        if "DN_" + e not in DN:
            find(f"OMISSION_NO_DAG_ROW:{e}", "D01_COVERAGE", [parent_of_ec(e)], e, "COVERAGE", "DAG projection(36) 행 없음")
        if r["origin_atomic_prop_id"] not in AP:
            find(f"EVENT_WITHOUT_ATOMIC:{e}", "D01_COVERAGE", [], e, "PROVENANCE", "origin atomic prop 없음")
    used_vars = set()
    for c in D["RC"]:
        used_vars |= set(re.findall(r"E_EC\d{4}", (c["antecedent"] or "") + " " + c["formula"]))
    for t in TE.values():
        used_vars |= set(re.findall(r"E_EC\d{4}", t["activation_condition"]))
    retention = {}
    for e, r in EC.items():
        d = DN.get("DN_" + e)
        if d and d["node_class"] == "ATTRIBUTE_ONLY":
            anchored = bool(map_of[e]) or bool(j_of[e]) or "부착" in d["notes"] or f"E_{e}" in used_vars or \
                any(e in x["notes"] for x in DN.values() if x is not d)
            claim_var = VAR.get(f"E_{e}", {}).get("fixed_or_free") == "FREE" and f"ATT_{e}" in VAR
            retention[e] = "LINKED(mapping/judgment/부착/제약)" if anchored else (
                "CLAIM_VARIABLE_ONLY(E·ATT 변수로 world에 보존, DAG·H 연결 없음)" if claim_var else "DROPPED")
            if not anchored and not claim_var:
                find(f"ATTRIBUTE_DROPPED:{e}", "D01_COVERAGE", [parent_of_ec(e)], e, "COVERAGE",
                     "ATTRIBUTE_ONLY인데 mapping·judgment·부착·제약 어디에도 연결 없음(NOT_A_DAG_NODE가 DROPPED가 됨)")
    for p, r in P.items():  # every death-cause clause must survive as a cause attribute linked to a cause fact
        if r["claim_topic"] == "DEATH_CAUSE" or "병들어" in r["predicate"]:
            ecs = [e for a in aps_of[p] for e in ecs_of_ap[a]]
            if not any(EC[e]["event_type"] == "CAUSE_ATTRIBUTION" and any(H.get(m["historical_fact_id"], {}).get(
                    "fact_type") in ("CAUSE_ATTRIBUTE", "RESPONSIBILITY_ATTRIBUTE") for m in map_of[e]) for e in ecs):
                find(f"CAUSE_ATTRIBUTE_MISSING:{p}", "D01_COVERAGE", [p], p, "CAUSE", "사인/책임 귀속이 cause fact에 연결되지 않음")

    # D02 clause coverage (split audit): content words of the raw clause must survive in its atomic/event layer
    for p, r in P.items():
        blob = " ".join(" ".join((AP[a]["subject_surface"], AP[a]["predicate"], AP[a]["object_or_content"], AP[a]["notes"]))
                        for a in aps_of[p])
        blob += " " + " ".join(" ".join((EC[e]["predicate"], EC[e]["subject_surface"], EC[e]["object_surface"]))
                               for a in aps_of[p] for e in ecs_of_ap[a])
        if not aps_of[p]:
            continue
        for t in content_tokens(r["predicate"] + " " + r["object_or_content"] + " " + r["subject"]):
            stem = INFLECT.get(t, t[:2])
            if stem not in blob and t not in blob:
                find(f"CLAUSE:{p}:{t}", "D02_CLAUSE", [p], p, "PREDICATE", f"raw 어휘 '{t}'가 atomic/event 층에 없음")

    # D03 actor / target surface: derived subject must come from the raw text of its own proposition
    for e, r in EC.items():
        p = parent_of_ec(e)
        if not p:
            continue
        base = rawtext(p)
        for part in content_tokens(r["subject_surface"].replace("·", " ")):
            if part not in base and INFLECT.get(part, part[:2]) not in base:
                find(f"ACTOR_NOT_IN_RAW:{e}", "D03_ACTOR", [p], e, "ACTOR",
                     f"event subject '{r['subject_surface']}'의 '{part}'가 raw {p} 본문에 없음")
        d = DN.get("DN_" + e)
        if d and d["node_class"] in NODE_CLASSES and d["subject_surface"] != r["subject_surface"]:
            find(f"DAG_SUBJECT_CHANGED:{e}", "D03_ACTOR", [p], "DN_" + e, "ACTOR",
                 f"DAG subject '{d['subject_surface']}' ≠ event subject '{r['subject_surface']}'")
        if d and d["node_class"] in NODE_CLASSES and re.search(r"받았|받음|당했|맞았", P[p]["predicate"] + r["predicate"]) \
                and re.search(r"가함|가했|가하", d["action_core"]) and d["subject_surface"] == r["subject_surface"]:
            find(f"ACTOR_INVERSION:DN_{e}", "D03_ACTOR", [p], "DN_" + e, "ACTOR",
                 f"피동 '{P[p]['predicate']}'의 받는 쪽이 DAG action '{d['action_core']}'의 subject로 놓임")
    # target identity used across an edge without the identity hypothesis in the activation condition
    alias = {}
    for r in D["ER"]:
        alias[r["surface_form"]] = r["candidate_entity"]
    id_of = {}
    for v, r in VAR.items():
        if v.startswith("ID_"):
            m = re.search(r"scope (P\d{4}(?:\|P\d{4})*)", r["source_basis"])
            id_of[v] = r
    for eid, t in TE.items():
        a, b = t["from_node_candidate"][3:], t["to_node_candidate"][3:]
        if a not in EC or b not in EC or t["hard_or_conditional"] in ("EVIDENCE_ONLY", "REVIEW_REQUIRED"):
            continue
        oa, ob = EC[a]["object_surface"], EC[b]["object_surface"]
        for surf, ent in alias.items():
            if surf in oa and ent in ob and surf not in ob:
                key_part = {"풍각 김생원": "ID_PUNGGAK_KIMSAENGWON__KIMMYEONGSIN",
                            "흥덕 김생원": "ID_HEUNGDEOK_KIMSAENGWON__KIMGAPDEUK"}.get(surf, "")
                if not key_part or key_part not in t["activation_condition"]:
                    find(f"IDENTITY_IN_EDGE:{eid}", "D03_ACTOR", [parent_of_ec(b)], eid, "TARGET",
                         f"{a} 대상 '{surf}' ↔ {b} 대상 '{ent}'를 잇는데 활성 조건에 동일성 가설이 없음")

    # D04 meaning-bearing words must be supported by the raw provenance of the same object
    TOPIC_GLOSS = {"COACHING": "회유"}

    def lex_check(prefix, obj, text, props, extra=""):
        prov = " ".join(rawtext(p) + " " + TOPIC_GLOSS.get(P[p]["claim_topic"], "") for p in props if p in P) + " " + extra
        bad = [w for w, forms in LEXICON.items() if w in text and not any(f in prov for f in forms)]
        if bad:
            find(f"LEXICON:{prefix}:{obj}", "D04_LEXICON", props, obj, "PREDICATE",
                 f"{'·'.join(bad)} — {obj} 텍스트 '{text[:90]}'; provenance {','.join(props)}에 근거 형태 없음")

    for a, r in AP.items():
        lex_check("AP", a, r["predicate"] + " " + r["object_or_content"], [r["parent_prop_id"]])
    for e, r in EC.items():
        lex_check("EC", e, r["predicate"] + " " + r["object_surface"], [parent_of_ec(e)],
                  AP.get(r["origin_atomic_prop_id"], {}).get("predicate", ""))
    for nid, d in DN.items():
        src = d["source_candidate_ids"]
        if src.startswith("EC") and src in EC:
            lex_check("DAG", nid, d["action_core"], [parent_of_ec(src)])
        elif src in J:
            lex_check("DAG", nid, d["action_core"], raw_of_j(src))
    for jid, j in J.items():
        lex_check("J", jid, j["judgment_topic"], raw_of_j(jid))
        if jid in VAR:
            lex_check("VAR", jid, VAR[jid]["notes"], raw_of_j(jid))
    for m in MAP:
        e, hid = m["event_candidate_id"], m["historical_fact_id"]
        if e in EC and hid in H and m["claim_relation"] not in ("DOES_NOT_MAP_DIRECTLY", "DOUBTS"):
            lex_check("MAP", f"{e}->{hid}", H[hid]["predicate"], [parent_of_ec(e)], AP[EC[e]["origin_atomic_prop_id"]]["predicate"])

    # D05 polarity / doubt
    for e, r in EC.items():
        a = AP.get(r["origin_atomic_prop_id"])
        if not a:
            continue
        text = a["predicate"]
        if r["event_type"] != "SPEECH_ACT" and any(mk in text for mk in DOUBT_MARKERS):
            bad = r["polarity"] != "DOUBTED" or any(m["claim_relation"] not in ("DOUBTS", "DOES_NOT_MAP_DIRECTLY")
                                                    for m in map_of[e])
            if bad:
                find(f"DOUBT_CHANGED:{e}", "D05_POLARITY", [parent_of_ec(e)], e, "POLARITY",
                     f"의심 표현('{text}')인데 polarity={r['polarity']}, mapping="
                     f"{'|'.join(m['claim_relation'] for m in map_of[e])}")
        neg_raw = any(mk in text for mk in NEG_MARKERS)
        if r["event_type"] != "SPEECH_ACT":
            if neg_raw and r["polarity"] == "AFFIRMED" and not any(mk in r["predicate"] for mk in NEG_MARKERS):
                find(f"NEGATION_LOST:{e}", "D05_POLARITY", [parent_of_ec(e)], e, "POLARITY",
                     f"부정 표현('{text}')이 AFFIRMED '{r['predicate']}'로 바뀜")
            if r["polarity"] in ("NEGATED", "DENIED") and not neg_raw:
                find(f"NEGATION_ADDED:{e}", "D05_POLARITY", [parent_of_ec(e)], e, "POLARITY",
                     f"원문('{text}')에 부정이 없는데 polarity={r['polarity']}")
    for jid, j in J.items():  # judgment strength must not exceed the strength of its contents
        ecs = [e for e in j["event_candidate_ids"].split("|") if e in EC]
        if j["stance_strength"] in ("STRONG", "FINAL") and any(EC[e]["polarity"] == "DOUBTED" for e in ecs):
            find(f"J_STRENGTH:{jid}", "D05_POLARITY", raw_of_j(jid), jid, "EPISTEMIC",
                 f"stance {j['stance']}/{j['stance_strength']}인데 내용에 DOUBTED claim 포함")
        if j["stance_strength"] == "FINAL" and not any(P[p]["epistemic_scope"] == "FINAL_ROYAL_FINDING" for p in raw_of_j(jid)):
            find(f"J_FINAL_UNSUPPORTED:{jid}", "D05_POLARITY", raw_of_j(jid), jid, "EPISTEMIC",
                 "FINAL 판단인데 raw epistemic_scope에 FINAL_ROYAL_FINDING 없음")
    for e in ("EC0149",):  # legal clearance rendered with factual-negation polarity
        if e in EC and EC[e]["polarity"] == "NEGATED" and "면하" in AP[EC[e]["origin_atomic_prop_id"]]["predicate"] \
                and "면" not in EC[e]["predicate"]:
            find(f"EC_POLARITY_LABEL:{e}", "D05_POLARITY", [parent_of_ec(e)], e, "EPISTEMIC",
                 f"'죄를 면함'이 EC 술어 '{EC[e]['predicate']}' NEGATED로 표현됨")

    # D06 scope: biconditional mappings must not drop a scope-limiting word of the claim
    for m in MAP:
        e, hid = m["event_candidate_id"], m["historical_fact_id"]
        if e not in EC or hid not in H or "↔" not in m["logical_form"]:
            continue
        claim = AP[EC[e]["origin_atomic_prop_id"]]["predicate"] + " " + EC[e]["predicate"]
        for w in SCOPE_WORDS:
            if w in claim and w not in H[hid]["predicate"]:
                find(f"SCOPE_IFF:{e}", "D06_SCOPE", [parent_of_ec(e)], f"{e}<->{hid}", "SCOPE",
                     f"claim의 범위어 '{w}'가 IFF 상대 H 술어 '{H[hid]['predicate']}'에 없음")

    # D07 open set
    def has_open(text):
        return bool(re.search(r"(?<![가-힣])등(?=[의을를에 ]|$)", text)) or any(w in text for w in OPEN_GROUP_WORDS)

    for a, r in AP.items():
        text = " ".join((r["subject_surface"], r["predicate"], r["object_or_content"]))
        if has_open(text):
            if not r["set_status"].startswith("OPEN"):
                find(f"OPEN_SET_CLOSED:{a}", "D07_OPEN_SET", [r["parent_prop_id"]], a, "OPEN_SET",
                     f"'등'/비열거 집단 표현인데 set_status={r['set_status']}")
            for e in ecs_of_ap[a]:
                er = EC[e]
                if not er["set_status"].startswith("OPEN") or not er["open_set_ids"]:
                    find(f"OPEN_SET_CLOSED:{e}", "D07_OPEN_SET", [r["parent_prop_id"]], e, "OPEN_SET",
                         f"event set_status={er['set_status']} open_set_ids={er['open_set_ids']}")
                for os_id in er["open_set_ids"].split("|"):
                    if os_id and D["OS"].get(os_id, {}).get("is_open") != "TRUE":
                        find(f"OPEN_SET_CLOSED:{os_id}", "D07_OPEN_SET", [r["parent_prop_id"]], os_id, "OPEN_SET",
                             "open_set_normalized is_open ≠ TRUE")
                if re.search(r"(?<![가-힣])등(?=[의을를에 ]|$)", r["predicate"]) and \
                        not re.search(r"(?<![가-힣])등(?=[의을를에 ]|$)", er["predicate"] + " " + er["object_surface"]):
                    find(f"OPEN_SET_MARKER_DROPPED:{e}", "D07_OPEN_SET", [r["parent_prop_id"]], e, "OPEN_SET",
                         "atomic 술어의 '등'이 event 술어에서 빠짐")
    DEUNG = r"(?<![가-힣])등(?=[의을를에 ]|$)"
    for p, r in P.items():  # raw-anchored: the open marker in the immutable source must survive downstream
        rtext = " ".join((r["subject"], r["predicate"], r["object_or_content"]))
        if not has_open(rtext):
            continue
        aps = aps_of[p]
        apt = " ".join(" ".join((AP[a]["subject_surface"], AP[a]["predicate"], AP[a]["object_or_content"])) for a in aps)
        ect = " ".join(" ".join((EC[e]["subject_surface"], EC[e]["predicate"], EC[e]["object_surface"]))
                       for a in aps for e in ecs_of_ap[a])
        why = []
        if aps and not any(AP[a]["set_status"].startswith("OPEN") for a in aps):
            why.append("atomic set_status 모두 비개방")
        if re.search(DEUNG, rtext):
            if aps and not re.search(DEUNG, apt):
                why.append("atomic 층에서 '등' 소실")
            if ect and not re.search(DEUNG, ect):
                why.append("event 층에서 '등' 소실")
        for os_id, o in D["OS"].items():
            if o["parent_prop_id"] == p and o["is_open"] != "TRUE":
                why.append(f"{os_id} is_open={o['is_open']}")
        if why:
            find(f"OPEN_SET_CLOSED_RAW:{p}", "D07_OPEN_SET", [p], p, "OPEN_SET",
                 f"raw '{rtext[:60]}'의 개방 표지가 하류에서 닫힘: {'; '.join(why)}")
    for v, r in VAR.items():
        if v.startswith("MEMBER_") and r["fixed_or_free"] != "FREE":
            find(f"OPEN_SET_MEMBER_FIXED:{v}", "D07_OPEN_SET", [], v, "OPEN_SET", f"membership 변수 {r['fixed_or_free']}")
    for c in D["RC"]:
        if re.fullmatch(r"¬MEMBER_\w+", c["formula"].strip()):
            find(f"OPEN_SET_NONMEMBER_CONSTRAINT:{c['constraint_id']}", "D07_OPEN_SET", [], c["constraint_id"], "OPEN_SET",
                 "open set 비구성원 고정 제약")

    # D08 nested testimony / epistemic layering
    for a, r in AP.items():
        p = r["parent_prop_id"]
        if p not in P:
            continue
        nested_raw = P[p]["epistemic_scope"] == "NESTED_TESTIMONY"
        depth = int(r["attestation_depth"] or 1)
        if nested_raw and depth < 2 and r["claim_level"] != "EMBEDDED_ATTESTATION":
            find(f"NESTED_DEPTH:{p}", "D08_NESTED", [p], a, "NESTED", f"raw NESTED_TESTIMONY인데 {a} depth={depth}")
        for e in ecs_of_ap[a]:
            er = EC[e]
            if (depth >= 2 or nested_raw) and PD.get(a, {}).get("projection_mode") == "CONTENT":
                find(f"NESTED_INNER:{p}", "D08_NESTED", [p], a, "NESTED",
                     "CONTENT projection: INNER 발화 층은 attestation(AP depth·embedded_speaker)에만 남고 world 변수·DAG node 없음")
                if er["epistemic_status"] not in ("ASSERTED", "STATE_REPORTED", "DENIED"):
                    find(f"NESTED_PROMOTED:{e}", "D08_NESTED", [p], e, "EPISTEMIC",
                         f"중첩 진술 내용이 epistemic_status={er['epistemic_status']}로 승격")
    for v, r in VAR.items():
        lvl = r["variable_level"]
        if v.startswith(("E_", "J_", "H_", "ID_", "SAME_", "REF_", "INTERP_", "SENSE_", "FABSCOPE_", "CAUSELEVEL_")) \
                and r["fixed_or_free"] != "FREE":
            find(f"VARIABLE_ANCHORED:{v}", "D08_NESTED", [], v, "EPISTEMIC",
                 f"{lvl} 변수가 {r['fixed_or_free']} (claim/판단/사실/가설은 고정 금지)")
        if v.startswith(("ATT_", "CT_")) and not r["fixed_or_free"].startswith("FIXED"):
            find(f"RECORD_NOT_FIXED:{v}", "D08_NESTED", [], v, "EPISTEMIC", "기록 존재 변수가 고정되지 않음")

    # D09 time
    for e, r in EC.items():
        a = AP.get(r["origin_atomic_prop_id"])
        if not a:
            continue
        p = a["parent_prop_id"]
        raw_t = P[p]["occurrence_lunar_text"]
        if r["occurrence_lunar_text"] and r["occurrence_lunar_text"] not in (raw_t, a["occurrence_lunar_text"]):
            find(f"TIME_CHANGED:{e}", "D09_TIME", [p], e, "TEMPORAL",
                 f"event 시점 '{r['occurrence_lunar_text']}' ≠ raw '{raw_t}'")
        if r["occurrence_lunar_text"] and r["occurrence_lunar_text"] == a["record_lunar_date"] and raw_t != a["record_lunar_date"]:
            find(f"RECORD_DATE_AS_OCCURRENCE:{e}", "D09_TIME", [p], e, "TEMPORAL", "기록일이 사건 시점으로 복사됨")
        if r["relative_time_text"] and r["relative_time_text"] not in rawtext(p):
            find(f"RELATIVE_TIME_NOT_IN_RAW:{e}", "D09_TIME", [p], e, "TEMPORAL", f"'{r['relative_time_text']}'")
        d = DN.get("DN_" + e)
        if d:
            m = re.search(r"주장 날짜 (.+?)\(CT_", d["notes"])
            if m and m[1] != r["occurrence_lunar_text"]:
                find(f"DAG_CLAIMED_TIME_CHANGED:{e}", "D09_TIME", [p], d["dag_node_candidate_id"], "TEMPORAL",
                     f"DAG 주장 날짜 {m[1]} ≠ event {r['occurrence_lunar_text']}")
            if "조정 기사일" in d["notes"] and P[p]["attestation_mode"] not in COURT_MODES:
                find(f"COURT_ANCHOR_ON_REPORTED_EVENT:{e}", "D09_TIME", [p], d["dag_node_candidate_id"], "TEMPORAL",
                     f"보고된 사건({P[p]['attestation_mode']})에 기사일 anchor")
    # place: event place must come from its own raw proposition
    for e, r in EC.items():
        p = parent_of_ec(e)
        if p and r["historical_place"] and r["historical_place"] not in rawtext(p):
            find(f"PLACE_IMPORTED:{e}", "D09_TIME", [p], e, "PLACE", f"장소 '{r['historical_place']}'가 {p}에 없음")

    # D10 temporal edges
    for eid, t in TE.items():
        if t["edge_type"] not in ALLOWED_EDGE_TYPES:
            find(f"EDGE_TYPE_NOT_TEMPORAL:{eid}", "D10_EDGE", [], eid, "TEMPORAL", f"edge_type={t['edge_type']}")
        if is_date_only(eid) and t["edge_type"] != "TEMPORAL_BEFORE":
            find(f"DATE_EDGE_STRENGTHENED:{eid}", "D10_EDGE", [], eid, "TEMPORAL",
                 f"date-only edge가 {t['edge_type']}")
        if not is_date_only(eid) and t["hard_or_conditional"] not in ("EVIDENCE_ONLY", "REVIEW_REQUIRED"):
            props = set()
            refs_text = ""
            for r in ev_of[eid]:
                if r["basis_type"] in DATE_BASES:
                    continue
                for ref in r["basis_refs"].split("|"):
                    if ref.startswith("EC") and ref in EC:
                        props.add(parent_of_ec(ref))
                    elif ref.startswith("P0") and ref in P:
                        props.add(ref)
                    elif ref.startswith("SRC") and ref in SRC:
                        refs_text += " " + SRC[ref]["source_title"] + " " + SRC[ref]["notes"]
                    elif ref.startswith("JR") and ref in D["JR"]:
                        refs_text += " " + " ".join(D["JR"][ref].values())
            basis_props = sorted(props) or sorted(parent_of_ec(x) for x in (t["from_node_candidate"][3:],
                                                                            t["to_node_candidate"][3:]) if x in EC)
            for x in (t["from_node_candidate"][3:], t["to_node_candidate"][3:]):
                if x in EC:
                    props.add(parent_of_ec(x))
            raw_blob = " ".join(rawtext(p) for p in props if p) + refs_text
            ap_blob = " ".join(AP[a]["predicate"] for p in props if p for a in aps_of[p])
            for r in ev_of[eid]:
                if r["basis_type"] in DATE_BASES:
                    continue
                ph = r["basis_detail"]
                if r["basis_type"] == "JUDGMENT_REVISION":
                    jr = D["JR"].get(r["basis_refs"], {})
                    srcs = [x for x in (jr.get("from_judgment_state_id"), jr.get("to_judgment_state_id")) if x in J]
                    jraw = " ".join(rawtext(p) for s in srcs for p in raw_of_j(s))
                    if "수정" not in jraw:
                        find(f"REVISION_NOT_IN_RAW:{eid}", "D10_EDGE", [p for s in srcs for p in raw_of_j(s)], eid,
                             "TEMPORAL", f"{r['basis_refs']} REVISED_BY의 '수정'이 원문에 없음")
                    continue
                n = norm(ph)
                if n in norm(raw_blob) or lcs_len(n, norm(raw_blob)) >= 0.75 * len(n):
                    continue
                if n in norm(ap_blob) or lcs_len(n, norm(ap_blob)) >= 0.75 * len(n):
                    find(f"EDGE_PHRASE_PARAPHRASE:{eid}", "D10_EDGE", basis_props, eid, "TEMPORAL",
                         f"근거 문구 '{ph}'가 raw에는 그대로 없고 atomic 풀어쓰기에만 있음")
                else:
                    find(f"EDGE_PHRASE_NOT_IN_RAW:{eid}", "D10_EDGE", basis_props, eid, "TEMPORAL",
                         f"근거 문구 '{ph}'가 raw·atomic 어디에도 없음(서술 순서 edge 의심)")
            if t["edge_type"] == "PROCEDURAL_TRIGGER_IF_EXPLICIT":
                phrases = " ".join(r["basis_detail"] for r in ev_of[eid] if r["basis_type"] not in DATE_BASES)
                if not any(mk in phrases for mk in TRIGGER_MARKERS):
                    find(f"TRIGGER_NOT_EXPLICIT:{eid}", "D10_EDGE", basis_props, eid, "TEMPORAL",
                         f"TRIGGER edge의 근거 '{phrases}'에 명시 연결어 없음")
            fr = t["from_node_candidate"][3:]
            if t["edge_type"] in ("TEMPORAL_BEFORE", "PROCEDURAL_PRECEDES", "PROCEDURAL_TRIGGER_IF_EXPLICIT") and fr in EC \
                    and EC[fr]["event_type"] == "STATE" and "상태 개시" not in DN.get("DN_" + fr, {}).get("action_core", ""):
                find(f"STATE_STRICT_EDGE:{eid}", "D10_EDGE", basis_props, eid, "TEMPORAL",
                     f"상태 node {fr}에서 나가는 선후 edge(끝난 뒤 시작 의미)")
    for nid, d in DN.items():  # causal / latent never appear in the DAG layer
        if re.search(r"CAUS|LATENT|UNKNOWN|EPISODE", d["node_class"]):
            find(f"DAG_FORBIDDEN_CLASS:{nid}", "D10_EDGE", [], nid, "PROVENANCE", d["node_class"])

    # D11 contradiction preservation
    for desc, a, b in CONTRADICTION_PAIRS:
        for x in (a, b):
            ok = x in EC and VAR.get(f"E_{x}", {}).get("fixed_or_free") == "FREE" and \
                VAR.get(f"ATT_{x}", {}).get("fixed_or_free", "").startswith("FIXED_TRUE")
            if not ok:
                find(f"CONTRADICTION_SIDE_LOST:{x}", "D11_CONTRADICTION", [parent_of_ec(x) if x in EC else ""], x,
                     "COVERAGE", f"충돌 기록 한쪽이 원래 형태로 남지 않음: {desc}")

    # D12 identity hypotheses must stay hypotheses
    for v, r in VAR.items():
        if v.startswith("ID_") and r["fixed_or_free"] != "FREE":
            find(f"IDENTITY_FIXED:{v}", "D12_IDENTITY", [], v, "ACTOR", f"동일성 가설이 {r['fixed_or_free']}")

    # ================================================================ adjudication
    issues = []
    unadjudicated = []
    for k, fd in sorted(findings.items()):
        adj = ADJUDICATION.get(k)
        if adj is None:
            unadjudicated.append(k)
            continue
        sev, status, dim, direction, note = adj[:5]
        props = adj[5] if len(adj) > 5 else fd["props"]
        issues.append(dict(fd, props=props, severity=sev, status=status, dimension=dim, direction=direction, note=note))
    stale = sorted(k for k in ADJUDICATION if k not in findings)

    # ================================================================ forward trace + per-proposition verdicts
    issues_by_prop = defaultdict(list)
    for i in issues:
        for p in i["props"]:
            issues_by_prop[p].append(i)
    sev_rank = {"NO_ISSUE": 0, "MINOR": 1, "MAJOR": 2, "CRITICAL": 3}
    trace_rows, fid_rows, verdict = [], [], {}
    complete_trace = 0
    special = {
        "A_JAMIDEOK": {"P0081", "P0083", "P0084", "P0079", "P0080", "P0082", "P0076", "P0077", "P0078", "P0075"},
        "B_HANJAEUK": {"P0086", "P0087", "P0088", "P0089", "P0090", "P0091", "P0092", "P0093", "P0094", "P0113"},
        "C_KIM_MYEONGSIN": {"P0004", "P0006", "P0025", "P0026", "P0040", "P0066", "P0067", "P0069", "P0102", "P0106", "P0107"},
        "D_THEFT": {"P0002", "P0009", "P0016", "P0018", "P0021", "P0032", "P0048", "P0049", "P0098", "P0099", "P0105"},
        "E_JISE": {"P0022", "P0036", "P0049", "P0065", "P0100", "P0108", "P0109"},
    }
    for p in P:
        aps = sorted(aps_of[p])
        ecs = sorted(e for a in aps for e in ecs_of_ap[a])
        decisions = [PD.get(a, {}).get("decision", "MISSING") for a in aps]
        facts = sorted({m["historical_fact_id"] for e in ecs for m in map_of[e]})
        js = sorted({j for e in ecs for j in j_of[e]} | {jid for jid in J if p in raw_of_j(jid)})
        dns = sorted("DN_" + e for e in ecs if "DN_" + e in DN)
        dclass = {d: DN[d]["node_class"] for d in dns}
        edges_expl = sorted({x for d in dns for x in edges_of_node[d] if not is_date_only(x)})
        n_date = len({x for d in dns for x in edges_of_node[d] if is_date_only(x)})
        traced = bool(aps) and all(d != "MISSING" for d in decisions) and \
            all((PD[a]["decision"] != "EVENT_PROJECTABLE") or ecs_of_ap[a] for a in aps) and \
            all("DN_" + e in DN for e in ecs)
        complete_trace += traced
        for a in aps:
            rowecs = ecs_of_ap[a] or [""]
            for e in rowecs:
                d = DN.get("DN_" + e, {}) if e else {}
                tags = [c for c, s in special.items() if p in s]
                trace_rows.append([
                    p, P[p]["source_record_id"], a, AP[a]["split_component"], AP[a]["component_role"], AP[a]["claim_level"],
                    AP[a]["attestation_depth"], PD.get(a, {}).get("decision", "MISSING"), PD.get(a, {}).get("projection_mode", ""),
                    e, EC.get(e, {}).get("event_type", ""), EC.get(e, {}).get("polarity", ""),
                    EC.get(e, {}).get("epistemic_status", ""),
                    "; ".join(f"{m['historical_fact_id']}:{m['claim_relation']}:{m['logical_form']}"
                              + (f"[{m['condition']}]" if m["condition"] else "") for m in map_of.get(e, [])) if e else "",
                    "|".join(j_of.get(e, [])) if e else "", ("DN_" + e) if d else "", d.get("node_class", ""),
                    d.get("activation_condition", ""),
                    "|".join(x for x in edges_of_node.get("DN_" + e, []) if not is_date_only(x)) if e else "",
                    str(sum(1 for x in edges_of_node.get("DN_" + e, []) if is_date_only(x))) if e else "0",
                    "COMPLETE" if traced else "INCOMPLETE", "|".join(tags)])
        if not aps:
            trace_rows.append([p, P[p]["source_record_id"], "", "", "", "", "", "MISSING", "", "", "", "", "", "", "", "", "",
                               "", "", "0", "INCOMPLETE", ""])
        # coverage class
        if not aps or any(f["detector"] == "D01_COVERAGE" and f["props"] == [p] for f in findings.values()) and not traced:
            base_v = "POSSIBLE_OMISSION"
        elif P[p]["source_record_id"] in ("SRC2_008", "SRC2_009"):
            base_v = "INTENTIONALLY_DEFERRED"
        elif any(x == "REVIEW_REQUIRED" for x in decisions):
            base_v = "REVIEW_REQUIRED"
        elif any(c in NODE_CLASSES for c in dclass.values()):
            base_v = "PRESERVED"
        elif any(c == "REVIEW_REQUIRED" for c in dclass.values()):
            base_v = "REVIEW_REQUIRED"
        elif ecs:
            base_v = "PRESERVED_AS_ATTRIBUTE"
        elif decisions and all(x == "ATTESTATION_ONLY" for x in decisions):
            base_v = "PRESERVED_AS_ATTESTATION_ONLY"
        elif decisions and all(x in ("META_OR_PROCEDURAL", "ATTESTATION_ONLY") for x in decisions):
            base_v = "PRESERVED_AS_META_PROCEDURAL"
        else:
            base_v = "REVIEW_REQUIRED"
        pi = [i for i in issues_by_prop[p] if i["status"] != "NO_ISSUE"]
        worst = max((sev_rank[i["severity"]] for i in pi), default=0)
        final = base_v
        if base_v not in ("POSSIBLE_OMISSION",) and worst >= 2:
            final = "REVIEW_REQUIRED"
        verdict[p] = final
        sev = {0: "NO_ISSUE", 1: "MINOR", 2: "MAJOR", 3: "CRITICAL"}[worst]
        if not aps:
            coverage = "NONE"
        elif worst >= 2:
            coverage = "DISTORTED"
        elif worst == 1 or any(x == "REVIEW_REQUIRED" for x in decisions):
            coverage = "PARTIAL"
        else:
            coverage = "FULL"
        if final == "POSSIBLE_OMISSION":
            coverage = "NONE"

        def dim(*names):
            hits = [i for i in pi if i["dimension"] in names]
            if not hits:
                return "OK"
            w = max(hits, key=lambda i: sev_rank[i["severity"]])
            return f"{w['severity']}({w['status']}): {'; '.join(sorted({h['key'].split(':')[0] for h in hits}))}"

        notes = " / ".join(f"[{i['severity']}/{i['status']}] {i['note']}" for i in pi)
        if base_v == "REVIEW_REQUIRED" and not pi:
            why = [PD[a]["reason"] for a in aps if PD.get(a, {}).get("decision") == "REVIEW_REQUIRED"]
            why += [f"DAG {d}=REVIEW_REQUIRED: {DN[d]['notes'][:120]}" for d in dns if DN[d]["node_class"] == "REVIEW_REQUIRED"]
            notes = "REVIEW: " + " | ".join(why)
        elif base_v == "INTENTIONALLY_DEFERRED":
            notes = "2차 배경 자료(S3_BACKGROUND): META로 보존, 사건 사실 생성에는 쓰지 않음(provenance 유지)."
        fid_rows.append([
            p, P[p]["source_record_id"], f"[{P[p]['reporting_actor']}/{P[p]['attestation_mode']}] {P[p]['subject']} | "
            f"{P[p]['predicate']} | {P[p]['object_or_content']}", "|".join(aps), "|".join(ecs), "|".join(facts), "|".join(js),
            "|".join(f"{d}({dclass[d]})" for d in dns), "|".join(edges_expl) + (f" (+date-only {n_date})" if n_date else ""),
            coverage, dim("ACTOR"), dim("TARGET"), dim("PREDICATE"), dim("POLARITY"), dim("SCOPE", "CAUSE", "PLACE"),
            dim("TEMPORAL"), dim("EPISTEMIC", "NESTED"), dim("OPEN_SET"), final, sev, notes])

    # ================================================================ backward provenance
    prov_rows = []

    def prov(otype, oid, props, srcs, path, pclass, content="SUPPORTED", note=""):
        prov_rows.append([otype, oid, "|".join(sorted(set(p for p in props if p))), "|".join(sorted(set(s for s in srcs if s))),
                          path, pclass, content, note])

    content_issue = defaultdict(list)
    for i in issues:
        if i["status"] != "NO_ISSUE" and i["detector"] in ("D04_LEXICON", "D03_ACTOR", "D06_SCOPE"):
            content_issue[i["obj"].split("->")[0].split("<->")[0]].append(i["key"])
    for a, r in sorted(AP.items()):
        ok = r["parent_prop_id"] in P
        prov("ATOMIC_PROPOSITION", a, [r["parent_prop_id"]], [r["source_record_id"]], f"{r['parent_prop_id']}→{a}",
             ("SOURCE_DIRECT" if r["derivation"] != "SPLIT" else "SOURCE_SPLIT") if ok else "UNSUPPORTED_ADDITION",
             "CONTENT_FLAGGED: " + "|".join(content_issue[a]) if content_issue[a] else "SUPPORTED", r["component_role"])
    for e, r in sorted(EC.items()):
        p = parent_of_ec(e)
        flagged = content_issue[e] + content_issue["DN_" + e]
        prov("EVENT_CANDIDATE", e, [p], [AP.get(r["origin_atomic_prop_id"], {}).get("source_record_id", "")],
             f"{p}→{r['origin_atomic_prop_id']}→{e}", "SOURCE_DIRECT" if p else "UNSUPPORTED_ADDITION",
             "CONTENT_FLAGGED: " + "|".join(flagged) if flagged else "SUPPORTED",
             PD.get(r["origin_atomic_prop_id"], {}).get("projection_mode", ""))
    for hid, h in sorted(H.items()):
        ms = [m for m in MAP if m["historical_fact_id"] == hid]
        props = [parent_of_ec(m["event_candidate_id"]) for m in ms if m["event_candidate_id"] in EC]
        flagged = [k for k in content_issue if k.startswith(hid)] + [i["key"] for i in issues if hid in i["obj"] and
                                                                      i["status"] != "NO_ISSUE"]
        prov("HISTORICAL_FACT", hid, props, [], f"{len(ms)} mapping rows: " + ",".join(sorted({m['event_candidate_id'] for m in ms})),
             "SOURCE_DIRECT" if props else "UNSUPPORTED_ADDITION",
             "CONTENT_FLAGGED: " + "|".join(sorted(set(flagged))) if flagged else "SUPPORTED", h["derivation_basis"][:160])
    for jid, j in sorted(J.items()):
        props = raw_of_j(jid)
        flagged = [i["key"] for i in issues if jid in i["obj"] and i["status"] != "NO_ISSUE"]
        prov("JUDGMENT_STATE", jid, props, j["source_record_ids"].split("|"),
             f"{j['source_record_ids']}; EC {j['event_candidate_ids'] or '(none; notes)'}",
             "SOURCE_DIRECT" if props else "UNSUPPORTED_ADDITION",
             "CONTENT_FLAGGED: " + "|".join(sorted(set(flagged))) if flagged else "SUPPORTED", j["judgment_topic"])
    for v, r in sorted(VAR.items()):
        if v.startswith(("ATT_", "CT_", "E_", "T_", "H_", "J_")):
            continue
        sb = r["source_basis"]
        props = re.findall(r"P\d{4}", sb)
        if v.startswith("ID_"):
            pclass = "INTERPRETATION_HYPOTHESIS" if props else "DERIVED_BY_LOGIC"
        elif v.startswith("SAME_"):
            a_, b_ = v.split("_")[1:3]
            props = [parent_of_ec(a_), parent_of_ec(b_)]
            pclass = "INTERPRETATION_HYPOTHESIS"
        elif v.startswith("REF_"):
            props = [parent_of_ec(x) for x in re.findall(r"EC\d{4}", v)]
            pclass = "DERIVED_BY_LOGIC"
        elif v.startswith(("MEMBER_",)):
            props = [parent_of_ec(x) for x in re.findall(r"EC\d{4}", sb)]
            pclass = "INTERPRETATION_HYPOTHESIS"
        else:
            props = [parent_of_ec(x) for x in re.findall(r"EC\d{4}", v + " " + sb + " " + r["notes"])]
            pclass = "INTERPRETATION_HYPOTHESIS" if props else "DERIVED_BY_LOGIC"
        note = r["notes"] or sb
        if v == "ID_JANGGYO_1MYEONG__JOGYEWAN":
            note = "근거 없는 pair 단계 동일성 변수(값 자유). SAME_EC0076_EC0098 → 같은 행위자(RC0270)를 표현하려고 둔 논리 변수."
            props = [parent_of_ec("EC0076"), parent_of_ec("EC0098")]
        if v == "OCCURRENCE_GRANULARITY_ACT_LEVEL":
            note = "occurrence 개별화 단위(모델링 파라미터). 사료 내용이 아님."
        prov(r["variable_level"], v, props, [], sb, pclass, "SUPPORTED", note[:200])
    for nid, d in sorted(DN.items()):
        src = d["source_candidate_ids"]
        props = [parent_of_ec(src)] if src in EC else (raw_of_j(src) if src in J else [])
        flagged = [i["key"] for i in issues if i["obj"] == nid and i["status"] != "NO_ISSUE"]
        prov("DAG_NODE", nid, props, [], f"{src}→{nid} ({d['node_class']})",
             "SOURCE_DIRECT" if props else "UNSUPPORTED_ADDITION",
             "CONTENT_FLAGGED: " + "|".join(flagged) if flagged else "SUPPORTED", d["action_core"])
    for eid, t in sorted(TE.items()):
        if is_date_only(eid):
            continue
        refs = "|".join(f"{r['basis_type']}:'{r['basis_detail']}'({r['basis_refs']})" for r in ev_of[eid])
        props = set()
        for r in ev_of[eid]:
            for ref in r["basis_refs"].split("|"):
                if ref in EC:
                    props.add(parent_of_ec(ref))
                elif ref in P:
                    props.add(ref)
                elif ref in D["JR"]:
                    for s in (D["JR"][ref]["from_judgment_state_id"], D["JR"][ref]["to_judgment_state_id"]):
                        props |= set(raw_of_j(s))
        srcs = [ref for r in ev_of[eid] for ref in r["basis_refs"].split("|") if ref.startswith("SRC")]
        flagged = [i["key"] for i in issues if i["obj"] == eid and i["status"] != "NO_ISSUE"]
        prov("TEMPORAL_EDGE_EXPLICIT", eid, props, srcs, f"{t['from_node_candidate']} -{t['edge_type']}-> "
             f"{t['to_node_candidate']} [{t['hard_or_conditional']}] {refs}",
             "SOURCE_DIRECT" if (props or srcs) else "UNSUPPORTED_ADDITION",
             "CONTENT_FLAGGED: " + "|".join(flagged) if flagged else "SUPPORTED", t["notes"][:160])
    n_date_edges = sum(1 for eid in TE if is_date_only(eid))
    prov("TEMPORAL_EDGE_DATE_ONLY", f"{n_date_edges} edges", [], [], "두 node의 날짜(주장 날짜 claim 조건부 / 조정 기사일) 비교",
         "DERIVED_BY_LOGIC", "SUPPORTED" if not any(i["detector"] == "D10_EDGE" and i["key"].startswith(("DATE_EDGE",
                                                                                                      "EDGE_TYPE"))
                                                       for i in issues + [findings[k] for k in unadjudicated])
         else "CONTENT_FLAGGED", "모두 TEMPORAL_BEFORE·인과/trigger 아님")
    pclasses = Counter(r[5] for r in prov_rows)
    n_unsupported = pclasses.get("UNSUPPORTED_ADDITION", 0)
    n_latent = pclasses.get("LATENT_HYPOTHESIS", 0)
    n_content_flag = sum(1 for r in prov_rows if r[6].startswith("CONTENT_FLAGGED"))

    # ================================================================ validation
    raw_ok_end = all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items())
    check("F01", "data/raw SHA-256 시작·종료 일치", raw_ok_start and raw_ok_end, f"files={len(expected_sha)}")
    check("F02", "DuckDB raw table 4개 = data/raw CSV (immutable source layer 일치)", db_raw_ok)
    check("F03", "117개 raw proposition 모두 final verdict 하나", len(verdict) == 117 and all(v in VERDICTS for v in
                                                                                         verdict.values()),
          f"{len(verdict)}")
    vc = Counter(verdict.values())
    check("F04", "raw total = PRESERVED + ATTRIBUTE + ATTESTATION_ONLY + META + DEFERRED + REVIEW + OMISSION",
          sum(vc[v] for v in VERDICTS) == len(P) == 117, str({v: vc[v] for v in VERDICTS}))
    check("F05", "모든 자동 탐지 결과가 수동 판정(ADJUDICATION)을 가짐 — 미판정 = 새 왜곡", not unadjudicated,
          "|".join(unadjudicated[:12]))
    check("F06", "판정표의 모든 항목이 실제 탐지 결과와 대응", not stale, "|".join(stale), severity="WARNING")
    check("F07", "POSSIBLE_OMISSION = 0 (이유 없이 DROP된 raw proposition 없음)", vc["POSSIBLE_OMISSION"] == 0,
          str([p for p, v in verdict.items() if v == "POSSIBLE_OMISSION"]))
    check("F08", "backward provenance: UNSUPPORTED_ADDITION 객체 = 0", n_unsupported == 0, str(n_unsupported))
    check("F09", "LATENT_HYPOTHESIS 객체 = 0 (이번 단계에는 없어야 함)", n_latent == 0, str(n_latent))
    check("F10", "충돌 기록 양쪽 모두 원래 형태 보존(삭제·수정 없음, 기록 고정·내용 자유)",
          not any(k.startswith("CONTRADICTION_SIDE_LOST") for k in findings), f"pairs={len(CONTRADICTION_PAIRS)}")
    check("F11", "date-only edge는 모두 TEMPORAL_BEFORE, 인과·trigger 유형 없음",
          not any(k.startswith(("DATE_EDGE_STRENGTHENED", "EDGE_TYPE_NOT_TEMPORAL")) for k in findings),
          f"date-only={n_date_edges}")
    check("F12", "claim·판단·사실·동일성 변수 고정 없음(권위 anchoring 없음), 기록 존재만 고정",
          not any(k.startswith(("VARIABLE_ANCHORED", "IDENTITY_FIXED", "RECORD_NOT_FIXED")) for k in findings))
    check("F13", "모든 raw proposition 완전 추적(atomic→projection→event→DAG 분류)", complete_trace == 117,
          f"{complete_trace}/117")
    check("F14", "기존 output 01–44·DuckDB table 변경 없음(DB read-only)",
          all(sha256(OUT_DIR / n) == out_before[n] for n in existing) and
          all(table_digest(con, t) == digests_before[t] for t in tables), f"outputs={len(existing)} tables={len(tables)}")
    check("F15", "출력 번호 충돌 없음(기존 파일 덮어쓰지 않음)", not any((OUT_DIR / f).exists() for f in out_files.values()),
          ", ".join(out_files.values()))
    con.close()
    n_err = sum(1 for c in checks if c[2] == "ERROR")
    n_warn = sum(1 for c in checks if c[2] == "WARNING")
    if mut:
        log.info("mutation %s: validation ERROR=%d (%s); unadjudicated=%s", mut, n_err,
                 "|".join(c[0] for c in checks if c[2] == "ERROR"), "|".join(unadjudicated[:6]))
        sys.exit(0 if n_err else 3)

    # ================================================================ summary metrics
    real = [i for i in issues if i["status"] != "NO_ISSUE"]

    def props_with(pred):
        return sorted({p for i in real if pred(i) for p in i["props"]})

    metrics = [
        ("raw_proposition_total", len(P), ""),
        ("traced_raw_proposition_count", complete_trace, "atomic→projection→event→DAG 분류까지 끊김 없음"),
        ("completely_untraced_count", sum(1 for p in P if not aps_of[p]), ""),
        ("partially_preserved_count", sum(1 for r in fid_rows if r[9] == "PARTIAL"), "MINOR 손실 또는 REVIEW 대기(의미 일부만 한 층에 남음)"),
        ("possible_omission_count", vc["POSSIBLE_OMISSION"], ""),
    ]
    for v in VERDICTS:
        metrics.append((f"verdict:{v}", vc[v], ""))
    cat = [
        ("semantic_strengthening", lambda i: i["direction"] == "STRENGTHENING"),
        ("semantic_weakening", lambda i: i["direction"] == "WEAKENING"),
        ("polarity_distortion", lambda i: i["dimension"] == "POLARITY"),
        ("actor_target_mismatch", lambda i: i["dimension"] in ("ACTOR", "TARGET")),
        ("temporal_distortion", lambda i: i["dimension"] == "TEMPORAL"),
        ("open_set_distortion", lambda i: i["dimension"] == "OPEN_SET"),
        ("epistemic_or_nested_issue", lambda i: i["dimension"] in ("EPISTEMIC", "NESTED")),
        ("scope_or_cause_issue", lambda i: i["dimension"] in ("SCOPE", "CAUSE", "PLACE")),
    ]
    for name, pred in cat:
        conf = [i for i in real if pred(i) and i["status"] == "CONFIRMED"]
        rev = [i for i in real if pred(i) and i["status"] == "REVIEW"]
        metrics.append((f"{name}_issues", len(conf) + len(rev),
                        f"CONFIRMED={len(conf)} REVIEW={len(rev)}; "
                        f"by severity {dict(Counter(i['severity'] for i in conf + rev))}; props={','.join(props_with(pred))}"))
    metrics += [
        ("unsupported_derived_object_count", n_unsupported, "provenance가 전혀 없는 derived 객체"),
        ("derived_object_with_flagged_content", n_content_flag, "provenance는 있으나 내용 일부가 원문 근거 밖(48 참조)"),
        ("latent_hypothesis_count", n_latent, ""),
        ("review_required_propositions", vc["REVIEW_REQUIRED"], "final verdict 기준"),
        ("issues_total", len(real), f"CONFIRMED={sum(i['status'] == 'CONFIRMED' for i in real)} "
                                    f"REVIEW={sum(i['status'] == 'REVIEW' for i in real)}; "
                                    f"severity {dict(Counter(i['severity'] for i in real))}"),
        ("detector_hits_explained_no_issue", sum(1 for i in issues if i["status"] == "NO_ISSUE"), ""),
        ("provenance_classes", len(prov_rows), str(dict(pclasses))),
        ("validation_error", n_err, ""), ("validation_warning", n_warn, ""),
        ("raw_sha256_preserved", "YES" if raw_ok_start and raw_ok_end else "NO", ""),
    ]

    # ================================================================ write
    trace_cols = ["raw_prop_id", "source_record_id", "atomic_prop_id", "split_component", "component_role", "claim_level",
                  "attestation_depth", "projection_decision", "projection_mode", "event_candidate_id", "event_type",
                  "polarity", "epistemic_status", "historical_fact_mapping", "judgment_state_ids", "dag_node_id",
                  "dag_node_class", "dag_activation_condition", "explicit_edge_ids", "date_only_edge_count", "trace_status",
                  "special_case"]
    fid_cols = ["raw_proposition_id", "source_record_id", "raw_text_or_normalized_text", "atomic_ids", "event_candidate_ids",
                "historical_fact_ids", "judgment_state_ids", "dag_node_ids", "edge_ids", "coverage_status", "actor_fidelity",
                "target_fidelity", "predicate_fidelity", "polarity_fidelity", "scope_fidelity", "temporal_fidelity",
                "epistemic_fidelity", "open_set_fidelity", "final_verdict", "severity", "notes"]
    prov_cols = ["object_type", "object_id", "raw_prop_ids", "source_record_ids", "provenance_path", "provenance_class",
                 "content_check", "notes"]
    iss_cols = ["issue_id", "finding_key", "detector", "raw_prop_ids", "derived_object", "dimension", "direction", "severity",
                "status", "detected_detail", "adjudication"]
    real_sorted = sorted(real, key=lambda i: (-sev_rank[i["severity"]], i["status"] != "CONFIRMED", i["key"]))
    iss_rows = [[f"FI{n:03d}", i["key"], i["detector"], "|".join(i["props"]), i["obj"], i["dimension"], i["direction"],
                 i["severity"], i["status"], i["detail"], i["note"]] for n, i in enumerate(real_sorted, 1)]
    OUT_DIR.mkdir(exist_ok=True)
    write_csv(OUT_DIR / out_files["raw_to_derived_traceability"], trace_cols, trace_rows)
    write_csv(OUT_DIR / out_files["source_fidelity_audit"], fid_cols, fid_rows)
    write_csv(OUT_DIR / out_files["derived_to_raw_provenance_audit"], prov_cols, prov_rows)
    write_csv(OUT_DIR / out_files["fidelity_issues"], iss_cols, iss_rows)
    write_csv(OUT_DIR / out_files["fidelity_validation"], ["check_id", "description", "severity", "detail"], checks)
    write_csv(OUT_DIR / out_files["fidelity_summary"], ["metric", "value", "notes"], [list(m) for m in metrics])

    for m in metrics:
        log.info("%s = %s %s", m[0], m[1], f"({m[2]})" if m[2] else "")
    for r in iss_rows:
        log.info("%s %s/%s %s %s: %s", r[0], r[7], r[8], r[5], r[4], r[10][:160])
    # special cases, human readable
    for cname, props in special.items():
        log.info("=== special case %s", cname)
        for p in sorted(props):
            log.info("  %s [%s] %s | %s", p, verdict[p], P[p]["subject"], P[p]["predicate"])
            for a in sorted(aps_of[p]):
                for e in ecs_of_ap[a] or [""]:
                    d = DN.get("DN_" + e, {}) if e else {}
                    maps = "; ".join(f"{m['historical_fact_id']}:{m['logical_form']}" + (f"[{m['condition']}]" if m["condition"]
                                                                                          else "") for m in map_of.get(e, []))
                    log.info("     %s %s → %s %s %s → %s | %s", a, AP[a]["predicate"][:50], e or PD.get(a, {}).get("decision"),
                             EC.get(e, {}).get("polarity", ""), EC.get(e, {}).get("predicate", "")[:40],
                             d.get("node_class", "-"), maps)
            for i in issues_by_prop[p]:
                if i["status"] != "NO_ISSUE":
                    log.info("     ! %s/%s %s", i["severity"], i["status"], i["key"])
    log.info("validation: ERROR=%d WARNING=%d", n_err, n_warn)
    for c in checks:
        log.info("%s %s %s", c[0], c[2], c[3][:200])
    if n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
