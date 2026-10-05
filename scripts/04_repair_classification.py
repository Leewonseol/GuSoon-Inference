#!/usr/bin/env python3
"""Stage 4: repair classification of the 303 audit findings (report only, no data changes).

Every row of output/audit_master_summary.csv gets exactly one repair class:
  INTERNAL_FIX            - the fix is fully decidable from the 5 raw CSVs (exact new value given)
  SOURCE_RECHECK_REQUIRED - provenance missing / CSVs conflict; resolvable only by re-reading the
                            original source. The current value is KEPT (never proposed for deletion).
  SCHEMA_CHANGE_REQUIRED  - no row-level fix; the data model must change.

Core principle: "현재 CSV에 근거가 없다" != "역사적으로 사실이 아니다".
Evidence is limited to the 5 raw CSVs and the earlier audit outputs. source_url is a metadata
string only (never fetched). No web access, no external knowledge, no new events / merges /
relations / episodes / UNKNOWN interface / causal inference. Split or move proposals are
proposals only (승인 전 생성 금지). Raw CSVs are never written; SHA-256 is checked before/after.

The per-issue decisions are encoded below as data, each with its reason (decision_basis).
Where the lead's rubric did not cover a row, the default rule is applied and recorded
(DEFAULT_USED) in decision_basis and in the log.
"""

import csv
import hashlib
import logging
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "output"
LOGS = ROOT / "logs"
FILES = {
    "events": "gusun_events_v1.csv",
    "attestations": "gusun_attestations_v1.csv",
    "event_relations": "gusun_event_relations_v1.csv",
    "event_families": "gusun_event_families_v1.csv",
    "source_records": "gusun_source_records_v1.csv",
}
IF, SR, SC = "INTERNAL_FIX", "SOURCE_RECHECK_REQUIRED", "SCHEMA_CHANGE_REQUIRED"
CLASSES = {IF, SR, SC}
PRIO_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

log = logging.getLogger("repair")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_raw(name):
    with (RAW / FILES[name]).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def load_out(name):
    with (OUT / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write(name, cols, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    log.info("wrote output/%s (%d rows)", name, len(rows))


PRESERVE = "기존 값은 notes에 '원 값: …'으로 보존(삭제 없음)."

# =====================================================================
# Family proposals (used to compute member_count net effect)
#   DEFINITE: family change of an existing row (INTERNAL_FIX)
#   CONDITIONAL: family of a proposed new row from a split (only if the split is approved)
# =====================================================================
FAMILY_MOVES = [  # (event_id, from_family, to_family, audit ref)
    ("AT0008", "EF_ACT_RECORD_REPORT", "EF_ACT_INQUIRE_SEARCH", "A-005"),
    ("AT0010", "EF_ACT_RECORD_REPORT", "EF_ACT_DEATH", "A-006"),
]
SPLIT_NEW_ROWS = [  # (source event, family of proposed new row, audit ref)
    ("AT0012", "EF_ORDER_INVESTIGATE", "A-007/B-001"),
    ("AT0068", "EF_SPEECH_CLAIM_REPORT", "B-005"),
    ("AT0068", "EF_SPEECH_CLAIM_REPORT", "B-005"),
    ("AT0068", "EF_SPEECH_CLAIM_REPORT", "B-005"),
    ("AT0043", "EF_ACT_DEATH", "B-002"),
    ("AT0153", "EF_JUDGE_FINAL", "B-019"),
    ("AT0154", "EF_JUDGE_FINAL", "B-020"),
    ("AT0119", "EF_SPEECH_CLAIM_REPORT", "B-016"),
    ("AT0078", "EF_SPEECH_CLAIM_REPORT", "B-006"),
    ("AT0079", "EF_STATE_OTHER", "B-007"),
    ("AT0080", "EF_SPEECH_CLAIM_REPORT", "B-008"),
    ("AT0131", "EF_ACT_OTHER", "B-017"),
]

# =====================================================================
# Source recheck questions (one queue row per distinct thing to check in the source).
# members: (event_id, field) pairs, or relation ids via rels; priority fixed per rubric.
# =====================================================================
Q = OrderedDict()


def q(key, priority, problem, check, members=(), rels=(), field=None, current=None, events=None):
    Q[key] = dict(priority=priority, problem=problem, check=check, members=list(members),
                  rels=list(rels), field=field, current=current, events=events)


def rng(a, b):
    return [f"AT{n:04d}" for n in range(a, b + 1)]


# ---------------- HIGH ----------------
q("HAN_IDENTITY", "HIGH",
  "ATT0045는 '병영 보조자'라고만 하고, 그 보조자가 한재욱이라는 명제는 어떤 attestation에도 없음. REL0082(CONFLICTING_ACCOUNTS_OF_SAME_RELATION)와 AT0045.claim_topic/conflict_group 'HAN_GUSUN_RELATION'(AT0132에서 옮겨옴)은 이 동일시를 전제로만 성립.",
  "SRC002(이조원 보고) 원문에서 구순의 가객이라고 한 '병영 보조자'의 이름이 적혀 있는지, 적혀 있다면 한재욱인지 확인. SRC004에서 한재욱이 그 보조자(비장)와 같은 인물로 지칭되는지 확인.",
  members=[("AT0045", "claim_topic"), ("AT0045", "conflict_group")], rels=["REL0082"],
  field="REL0082(relation);AT0045.claim_topic;AT0045.conflict_group;인물 동일성(병영 보조자/비장/한재욱)")
q("AT0122_LIST", "HIGH",
  "ATT0122는 '여러 사람의 이름을 적었다'고만 함. AT0122.target_or_content의 7명 중 변재돌·김성손·김흥득·김흥길은 어떤 attestation에도 없음(변지돌·정원돌·김명신만 다른 attestation에 나옴).",
  "SRC004 한재욱 공초 원문에서 유제희가 적은 이름들이 열거되어 있는지, 열거되어 있다면 정확한 이름·인원(변지돌·변재돌·정원돌·김명신·김성손·김흥득·김흥길 7명과 일치하는지)과 '등' 같은 열린 표현의 유무를 확인.",
  members=[("AT0122", "target_or_content")])
q("ICHIPGEO_ROLE", "HIGH",
  "이집거는 ATT0118·ATT0119에서 자미덕의 대질 상대로만 등장. 명단·체포 명령·체포·구금·신문·지목 근거가 CSV에 없음. 이집거가 대질에 이르게 된 경로를 CSV가 설명하지 않음.",
  "SRC004 원문에서 이집거가 어떤 인물로 소개되는지(신분·역할), 어떤 경위로 자미덕과 대질하게 되었는지 서술이 있는지 확인. 서술이 없으면 '없음'으로 기록하고 추론으로 채우지 않음.",
  members=[("AT0118", "actor"), ("AT0119", "target_or_content")], field="인물 역할(이집거)")
q("AT0036_TARGET", "HIGH",
  "AT0036.target_or_content의 '김명신의 형'·'접촉 불허'는 ATT0036('피우 관련 일에서 구순과 김명신 사이에 갈등이 있었다')에 없음.",
  "SRC002 이조원 보고 원문에 피우 관련 일의 구체 내용(누가 피우하러 왔는지, 김명신의 형이 등장하는지, 구순이 무엇을 허락하지 않았는지)이 적혀 있는지 확인.",
  members=[("AT0036", "target_or_content")])
q("CHEOLPYEON_ACTOR", "HIGH",
  "ATT0086·ATT0087은 수동형('철편 네 개가 만들어졌다/제공됐다')으로 행위자가 없음. actor '한재욱 측'은 CSV 근거 없이 한재욱 쪽에 귀속.",
  "SRC004 이진욱 공초 원문에서 철편을 만든 사람·제공한 사람(또는 그것을 지시한 사람)이 명시되어 있는지 확인.",
  members=[("AT0086", "actor"), ("AT0087", "actor")])
q("JAMIDEOK_DATES", "HIGH",
  "AT0110–AT0117 occurrence_lunar_start '1793-02-29'는 이진욱 진술 AT0092의 날짜가 후보 연결 REL0077(SAME_EVENT_CANDIDATE)을 통해 옮겨온 값. 자미덕 진술 ATT0110–ATT0117에는 날짜 없음.",
  "SRC004 자미덕 공초 원문에 자신이 붙잡힌 날짜(또는 날짜 표지)와 그 이후 구류·신문·한재욱 관련 일의 날짜 표지가 있는지 확인. 없으면 값은 유지하되 이진욱 진술 기준 값임을 표시.",
  members=[(e, "occurrence_lunar_start") for e in rng(110, 117)])
q("SRC001_DATES", "HIGH",
  "AT0006–AT0009 occurrence_lunar_start '1793-03-04'는 SRC004 이진욱 진술(AT0097/AT0101)의 날짜. ATT0006–ATT0009(이형원, SRC001)에는 날짜가 없고 '달포 이상'만 있음.",
  "SRC001 이형원 장계 원문에 병영의 김명신 체포·구금·조사(및 증거 미확보)의 시작 날짜가 적혀 있는지 확인.",
  members=[(e, "occurrence_lunar_start") for e in rng(6, 9)])
q("AT0007_PLACE", "HIGH",
  "AT0007.historical_place '충청병영': ATT0007은 구금 장소를 말하지 않음. '병영 옥'은 ATT0042(이조원, SRC002)에만 있음.",
  "SRC001 이형원 장계 원문에 김명신이 구금된 장소가 적혀 있는지 확인.",
  members=[("AT0007", "historical_place")])
q("AT0010_PLACE", "HIGH",
  "AT0010.historical_place '충청병영 옥': ATT0010에 장소 없음. '병영 옥'은 ATT0042(이조원, SRC002)의 표현이며 REL0083로만 연결됨.",
  "SRC001 이형원 장계 원문에 김명신이 죽은 장소가 적혀 있는지 확인.",
  members=[("AT0010", "historical_place")])
q("REL0032_CONTENT", "HIGH",
  "REL0032 basis '대질 때 거짓 지목'의 '지목'은 ATT0119('거짓으로 말했다')에 없는 행위. 거짓말의 내용·대상은 CSV에 없음.",
  "SRC004 자미덕 공초 원문에서 이집거와 대질할 때 거짓으로 말한 내용이 무엇이었는지(누구에 대해 무엇이라 말했는지), '지목'에 해당하는 표현이 있는지 확인.",
  rels=["REL0032"], field="basis_or_rationale(거짓 진술의 내용)")

# ---------------- MEDIUM ----------------
q("UPPER_MYEONGEOP", "MEDIUM",
  "AT0073–AT0077 occurrence_lunar_end '1793-02-28'(BEFORE_FEB_28): ATT0073–ATT0077(명업 진술)에 날짜 근거 없음.",
  "SRC004 명업 공초 원문에서 소장 제출·체포령·장교 도착·안행랑 호출·대화가 2월 28일 이전이라는 날짜 표지가 있는지 확인.",
  members=[(e, "occurrence_lunar_end") for e in rng(73, 77)])
q("UPPER_HAN", "MEDIUM",
  "AT0120–AT0124 occurrence_lunar_end '1793-02-28'(BEFORE_FEB28): ATT0120–ATT0124(한재욱 진술)에 날짜 근거 없음.",
  "SRC004 한재욱 공초 원문에서 정소·유제희 파견·이름 기록·귀환·보고가 2월 28일 이전이라는 날짜 표지가 있는지 확인.",
  members=[(e, "occurrence_lunar_end") for e in rng(120, 124)])
q("UPPER_YOO", "MEDIUM",
  "AT0133–AT0136 occurrence_lunar_end '1793-02-28'(BEFORE_FEB28): ATT0133–ATT0136(유제희 진술)에 날짜 근거 없음.",
  "SRC004 유제희 공초 원문에서 현지 탐문·구순 발언 청취·기록·상신이 2월 28일 이전이라는 날짜 표지가 있는지 확인.",
  members=[(e, "occurrence_lunar_end") for e in rng(133, 136)])
q("JOGYEWAN_DATES", "MEDIUM",
  "AT0103–AT0108 날짜 '1793-03-04'는 이진욱 진술(AT0097)의 날짜. ATT0103–ATT0108(조계완 진술)에는 날짜 없음.",
  "SRC004 조계완 공초 원문에 구순 집에 들른 날짜(3월 4일 등) 표지가 있는지 확인.",
  members=[(e, f) for e in rng(103, 108) for f in ("occurrence_lunar_start", "occurrence_lunar_end")])
q("AT0073_TARGET_PLACE", "MEDIUM",
  "AT0073 target '도난 사건'·place '진영'은 ATT0073('구순이 소장을 올렸다')에 없고 AT0120(한재욱 진술)에서 REL0073로 옮겨온 값.",
  "SRC004 명업 공초 원문에서 구순이 올린 소장의 내용(도난)과 제출처(진영)가 적혀 있는지 확인.",
  members=[("AT0073", "target_or_content"), ("AT0073", "historical_place")])
q("AT0120_ACTOR", "MEDIUM",
  "AT0120.actor '구순': ATT0120('구순 집 도난이 진영에 정소된 뒤')에는 정소 주체가 없음. AT0073(명업 진술)에서 REL0073로 옮겨온 값.",
  "SRC004 한재욱 공초 원문에서 진영에 정소한 사람이 구순으로 명시되는지 확인.",
  members=[("AT0120", "actor")])
q("AT0012_PLACE", "MEDIUM",
  "AT0012.historical_place '충청도': ATT0012에 장소 없음. AT0172(충청도 관찰사)에서 옮겨온 것으로 보임.",
  "SRC001 이형원 장계 원문에 각 진영 영장들의 회동 조사 장소가 적혀 있는지 확인.",
  members=[("AT0012", "historical_place")])
q("PLACE_IJW_DEOKPYEONG", "MEDIUM",
  "AT0032·AT0034 historical_place '청주 덕평': ATT0032·ATT0034(이조원 보고)에 지명 없음. AT0001(이형원 장계)에서 옮겨옴.",
  "SRC002 이조원 보고 원문에 구순 집·김명신 거주지의 지명(청주 덕평)이 적혀 있는지 확인.",
  members=[("AT0032", "historical_place"), ("AT0034", "historical_place")])
q("PLACE_MYEONGEOP_DEOKPYEONG", "MEDIUM",
  "AT0069·AT0072 historical_place '청주 덕평': ATT0069·ATT0072(명업 진술)에 지명 없음. AT0001에서 옮겨옴.",
  "SRC004 명업 공초 원문에 구순·김명신 관계(상종·왕래 단절)의 장소 표현이 있는지 확인.",
  members=[("AT0069", "historical_place"), ("AT0072", "historical_place")])
q("YOO_INQUIRY_PLACE", "MEDIUM",
  "유제희 탐문 장소 값(AT0121 place '덕평 방면', AT0133 target '덕평 일대'·place '덕평', AT0134 place '덕평')은 ATT0121·ATT0133·ATT0134('현지', '탐문 중')에 지명이 없고 AT0001·AT0083에서 옮겨온 값.",
  "SRC004 한재욱·유제희 공초 원문에서 유제희가 탐문하러 간 곳의 지명이 적혀 있는지 확인.",
  members=[("AT0121", "historical_place"), ("AT0133", "target_or_content"), ("AT0133", "historical_place"),
           ("AT0134", "historical_place")])
q("HAN_BIJANG_PLACE", "MEDIUM",
  "AT0125–AT0131 historical_place '비장청': ATT0125–ATT0131(한재욱 진술)에 장소 없음. AT0125·AT0126은 AT0113(자미덕 진술)에서 REL0078/REL0079로 옮겨옴.",
  "SRC004 한재욱 공초 원문에서 자미덕을 불러들이고 밥을 주고 유제희와 말하고 재질문한 장소가 적혀 있는지 확인.",
  members=[(e, "historical_place") for e in rng(125, 131)])
q("JAMIDEOK_ARREST_PLACE", "MEDIUM",
  "AT0110.historical_place '병영': ATT0110('병영 장교가 갑자기 찾아와 자신을 붙잡았다')에서 '병영'은 장교의 소속이며 체포 장소가 아님. AT0111(병영으로 데려감)에서 옮겨온 것으로 보임.",
  "SRC004 자미덕 공초 원문에 자신이 붙잡힌 장소가 적혀 있는지 확인.",
  members=[("AT0110", "historical_place")])
q("CONFRONT_PLACE", "MEDIUM",
  "AT0118·AT0119 historical_place '병영': ATT0118·ATT0119에 대질 장소 없음.",
  "SRC004 자미덕 공초 원문에 이집거와의 대질 장소가 적혀 있는지 확인.",
  members=[("AT0118", "historical_place"), ("AT0119", "historical_place")])
q("LIST_PLACE", "MEDIUM",
  "유제희 명단 관련 행의 historical_place '병영'(AT0122·AT0124·AT0135·AT0136): 명제에 기록·보고 장소 없음. AT0123(병영으로 돌아옴)에서 옮겨온 값.",
  "SRC004 한재욱·유제희 공초 원문에서 이름을 기록한 장소와 보고·상신한 장소가 적혀 있는지 확인.",
  members=[("AT0122", "historical_place"), ("AT0124", "historical_place"), ("AT0135", "historical_place"),
           ("AT0136", "historical_place")])
q("HOSEO_PLACE", "MEDIUM",
  "홍대협 탐문·채탐 행의 historical_place '호서 이동 중'/'호서'(AT0137·AT0138·AT0144·AT0145): 명제에 지명 없음('내려가는 길', '별도 채탐'). '호서'는 AT0055(전년 호서 화적)에서 옮겨온 것으로 보임.",
  "SRC004 홍대협 서계 원문에 이동 중 탐문과 별도 채탐의 장소가 적혀 있는지 확인.",
  members=[("AT0137", "historical_place"), ("AT0138", "historical_place"), ("AT0144", "historical_place"),
           ("AT0145", "historical_place")])
q("ISSUE_LABELS", "MEDIUM",
  "ATT0149는 '세 가지 의안으로 분리했다'고만 하고 의안 이름이 없음. AT0149.target(도난 여부·김명신 사망원인·지세 호칭 날조 여부)과 REL0060–REL0062 basis의 의안 이름은 CSV 근거 없음. REL0062는 '날조 여부' 의안을 '호칭의 기원' 판단(AT0155)과 연결.",
  "SRC004 원문에서 정조가 분리한 세 가지 의안의 이름·내용이 명시되는지, 각 최종 판단(AT0150·AT0151·AT0155)이 어느 의안에 대한 것인지 확인.",
  members=[("AT0149", "target_or_content")], rels=["REL0060", "REL0061", "REL0062"],
  field="AT0149.target_or_content;REL0060-REL0062 basis_or_rationale")
q("AT0171_ESA", "MEDIUM",
  "AT0171.target '이형원의 장계와 홍대협의 안핵': ATT0171은 '도신 장계와 어사 보고'라고만 함. 어사가 누구인지 명제에 없음.",
  "SRC004 원문에서 정조가 언급한 '어사 보고'의 어사가 누구인지(홍대협인지) 확인.",
  members=[("AT0171", "target_or_content")])
q("REL0010", "MEDIUM",
  "REL0010 EXECUTION_OF_ORDER(HIGH), basis '유제희가 실제 현지 탐문을 수행': ATT0133(유제희)은 누가 자신을 보냈는지 말하지 않음. 같은 쌍이 COREFERENCE 층에서는 SAME_EPISODE_CANDIDATE(REL0074).",
  "SRC004 유제희 공초 원문에서 자신이 누구의 지시(한재욱/병영)로 현지에 갔다고 말하는지 확인.",
  rels=["REL0010"])
q("REL0089", "MEDIUM",
  "REL0089 '이름 제공 episode': ATT0134/0135(유제희)는 구순이 말하고 유제희가 기록, ATT0158(정조)은 구순이 이름을 적어 주었다고 함. 누가 이름을 적었는지가 다름.",
  "SRC004 원문에서 김명신의 이름을 적은 주체가 구순인지 유제희인지(유제희 공초와 정조 판단 각각의 표현) 확인.",
  rels=["REL0089"])
q("REL0077", "MEDIUM",
  "REL0077 basis '같은 자미덕 체포를 각자 회고'는 단정형이나 relation_type은 SAME_EVENT_CANDIDATE. 이 후보 연결로 이진욱 진술 날짜(2/29)가 자미덕 진술 행 8개로 옮겨짐.",
  "SRC004 이진욱·자미덕 공초의 체포 서술이 같은 체포를 가리킨다고 볼 원문 표지(날짜·장소·체포자 표현)가 있는지 확인.",
  rels=["REL0077"])
q("AT0116_REPEAT", "MEDIUM",
  "AT0116 time_precision 'REPEATED_AFTER_ARREST'이나 ATT0116에 반복 표현 없음(AT0114의 '매일'이 옮겨온 것으로 보임).",
  "SRC004 자미덕 공초 원문에서 한재욱의 석방 조건 회유가 한 번인지 매일/여러 차례인지 표지 확인.",
  members=[("AT0116", "time_precision")])
q("ALIAS_JAEDOL", "MEDIUM",
  "'재돌'(ATT0092·ATT0109·ATT0115)과 AT0122 target의 '변재돌'이 같은 사람인지 CSV에 명시 없음. 명단에는 '변지돌'과 '변재돌'이 따로 있음.",
  "SRC004 원문에서 자미덕의 남편 '재돌'의 성(변씨 여부)과 유제희 명단의 '변재돌'이 같은 인물로 서술되는지 확인.",
  members=[("AT0092", "target_or_content"), ("AT0109", "actor"), ("AT0115", "target_or_content"),
           ("AT0122", "target_or_content")], field="인물 표기(재돌/변재돌)", current="재돌 / 변재돌")
q("ALIAS_WONDOL", "MEDIUM",
  "ATT0135(유제희)의 '원돌'과 ATT0085(이진욱)·AT0122 target의 '정원돌'이 같은 사람인지 CSV에 명시 없음.",
  "SRC004 유제희 공초의 '원돌'과 이진욱 공초의 '정원돌'이 같은 인물·표기인지 원문 확인.",
  members=[("AT0085", "target_or_content"), ("AT0122", "target_or_content"), ("AT0135", "target_or_content")],
  field="인물 표기(원돌/정원돌)", current="원돌 / 정원돌")
q("ALIAS_KIM", "MEDIUM",
  "ATT0099는 '풍각 김생원=김명신'만 명시. ATT0134의 '풍각 김상제', ATT0105의 '풍각 상주'를 김명신으로 보는 근거는 ATT0135(구순 말을 듣고 김명신을 기록)의 간접 연결뿐. REL0088 basis도 김상제를 김명신으로 읽음.",
  "SRC004 원문에서 '풍각 김상제'(유제희 공초)·'풍각 상주'(조계완 공초)가 김명신을 가리킨다고 명시되는지 확인.",
  members=[("AT0097", "target_or_content"), ("AT0099", "actor"), ("AT0105", "target_or_content"),
           ("AT0134", "target_or_content"), ("AT0135", "target_or_content")], rels=["REL0088"],
  field="인물 표기(풍각 김생원/풍각 김상제/풍각 상주/김명신)",
  current="풍각 김생원 / 풍각 김상제 / 풍각 상주 / 김명신")

# ---------------- LOW ----------------
for _src in ("SRC001", "SRC002", "SRC003", "SRC004"):
    q(f"HANYANG_{_src}", "LOW",
      f"{_src} 기록 행위의 historical_place '한양': 해당 attestation 명제에 장소 표현 없음(UNSUPPORTED). 조정 행위라서 한양으로 적은 것으로 보이나 CSV 근거 없음.",
      f"{_src} 원문에 해당 복계·윤허·명령·입시·판단·처분이 이루어진 장소 표현이 있는지 확인. 없으면 값은 유지하되 근거 없음으로 표시(SC-05).",
      members=[])  # filled from data below
q("ACTOR_INST_PLACE", "LOW",
  "historical_place '충청병영'(AT0006·AT0008·AT0097·AT0098)은 행위 주체 기관(병영/병사)을 장소로 옮긴 것으로 보임. 명제에 행위 장소 없음.",
  "SRC001(AT0006·AT0008)·SRC004(AT0097·AT0098) 원문에 체포·조사·체포 명령이 이루어진 장소가 적혀 있는지 확인.",
  members=[("AT0006", "historical_place"), ("AT0008", "historical_place"), ("AT0097", "historical_place"),
           ("AT0098", "historical_place")])
q("PLACE_MYEONGEOP_HOUSE", "LOW",
  "AT0065–AT0068 historical_place '구순 집': ATT0065–ATT0068(명업 진술)에 장소가 명시되지 않거나 인접 행에서 옮겨옴.",
  "SRC004 명업 공초 원문에서 나복이 찾아와 부르고 말하고 명업이 들어간 장소가 구순 집으로 적혀 있는지 확인.",
  members=[(e, "historical_place") for e in rng(65, 68)])
q("PLACE_CHEOLPYEON", "LOW",
  "AT0086–AT0088 historical_place('충청병영'/'충청병영 비장청'): 명제에 장소 없음. AT0083 등 인접 행에서 옮겨옴.",
  "SRC004 이진욱 공초 원문에서 철편 제작·제공과 한재욱의 주의 발언 장소가 적혀 있는지 확인.",
  members=[("AT0086", "historical_place"), ("AT0087", "historical_place"), ("AT0088", "historical_place")])
q("PLACE_JAMIDEOK_ROOM", "LOW",
  "AT0115–AT0117 historical_place('비장청 방'/'비장청'): ATT0115–ATT0117에 장소 없음. AT0114 등에서 옮겨옴.",
  "SRC004 자미덕 공초 원문에서 한재욱의 발언·회유·음식 제공 장소가 적혀 있는지 확인.",
  members=[("AT0115", "historical_place"), ("AT0116", "historical_place"), ("AT0117", "historical_place")])
q("PLACE_GONGJU", "LOW",
  "AT0140–AT0143 historical_place '공주목': 명제에 장소 없음. AT0061(공주목 도착)에서 옮겨온 것으로 보임.",
  "SRC004 홍대협 서계 원문에서 도난 판단·규모 판단·지세 호칭 반복 조사의 장소가 적혀 있는지 확인.",
  members=[(e, "historical_place") for e in rng(140, 143)])
q("DATES_AT0017_19", "LOW",
  "AT0017–AT0019 날짜 '1793-05-12'는 SRC001 기록일. 이형원의 평가·건의는 장계 작성 시점(기록일 이전)일 수 있음.",
  "SRC001 원문에서 이형원 장계(평가·건의)의 작성·도착 날짜가 기록일과 구별되어 적혀 있는지 확인.",
  members=[(e, f) for e in rng(17, 19) for f in ("occurrence_lunar_start", "occurrence_lunar_end")])
q("DATE_AT0068", "LOW",
  "AT0068 날짜 '1793-02-22': ATT0068에 날짜 없음. AT0065(2월 22일 밤)에서 옮겨옴. REL0066도 이 날짜를 비교에 씀.",
  "SRC004 명업 공초 원문에서 나복의 도적 묘사 발언이 2월 22일 밤의 같은 발화로 서술되는지 확인.",
  members=[("AT0068", "occurrence_lunar_start"), ("AT0068", "occurrence_lunar_end")])
q("DATE_AT0069", "LOW",
  "AT0069 occurrence_lunar_end '1793-02-EARLY': ATT0069에 날짜 없음. AT0070(2월 초 편지)에서 옮겨옴.",
  "SRC004 명업 공초 원문에서 '본래 친숙하여 날마다 상종'한 상태가 2월 초 편지 이전까지로 서술되는지 확인.",
  members=[("AT0069", "occurrence_lunar_end")])
q("DATE_AT0088", "LOW",
  "AT0088 날짜 '1793-02-28'~'1793-02-29': ATT0088에 날짜 없음. 인접 행에서 옮겨옴.",
  "SRC004 이진욱 공초 원문에서 한재욱의 주의 발언 시점이 2월 28일 밤으로 서술되는지 확인.",
  members=[("AT0088", "occurrence_lunar_start"), ("AT0088", "occurrence_lunar_end")])
q("DATE_AT0101_0102", "LOW",
  "AT0101·AT0102 날짜 '1793-03-04'는 체포 명령(AT0097·AT0098) 날짜. ATT0101·ATT0102에 잡아온 날짜 없음.",
  "SRC004 이진욱 공초 원문에 김명신·김갑득을 잡아온 날짜가 명령 날짜와 구별되어 적혀 있는지 확인.",
  members=[(e, f) for e in ("AT0101", "AT0102") for f in ("occurrence_lunar_start", "occurrence_lunar_end")])
q("AT0016_SPEAKER", "LOW",
  "ATT0016은 '진술이 실려 있다'로 진술자를 밝히지 않음. actor '회동 조사 응답자들'은 인접 행(AT0013–AT0015)에서 옮겨옴.",
  "SRC001 원문에서 '김명신 외 전후 체포자들도 구순 집에서 미워하던 사람들이었다'는 진술의 진술자가 회동 조사 응답자들인지 확인.",
  members=[("AT0016", "actor")])
q("REPEAT_AT0115_0117", "LOW",
  "AT0115·AT0117 time_precision 'REPEATED_AFTER_ARREST'이나 ATT0115·ATT0117에 반복 표현 없음.",
  "SRC004 자미덕 공초 원문에서 재돌 체포 발언과 떡·밥 제공이 반복된 일로 서술되는지 확인.",
  members=[("AT0115", "time_precision"), ("AT0117", "time_precision")])
q("KIM_S5_CONFLICT", "LOW",
  "김명신 신문(S5) 충돌: ATT0008 '달포 이상 조사'(이형원, SRC001) vs ATT0153 '곤장이나 평범한 신문을 받지 않았다'(정조, SRC004). 충돌은 보존하며 어느 쪽도 사실로 승격하지 않음.",
  "SRC001·SRC004 원문에서 '조사'와 '신문'에 해당하는 원어 표현을 각각 확인(표현 범위 차이인지 판단 자료로만 기록). 확인 결과로 어느 한쪽을 확정하지 않음.",
  members=[("AT0008", "action"), ("AT0153", "target_or_content")], field="action;target_or_content(신문 여부 충돌)")
q("ALIAS_BYEONGSA", "LOW",
  "attestation은 '병사'만 언급하고 '이광섭'과 연결하는 근거는 source_records.source_title뿐(SRC001·SRC004 제목).",
  "SRC004 이진욱 공초 본문에서 '병사'가 이광섭으로 명시되는지 확인(기사 제목 메타데이터는 이미 연결).",
  members=[("AT0097", "actor"), ("AT0098", "actor")], field="인물 표기(병사/이광섭)", current="병사 이광섭 (actor)")
q("REL0050", "LOW",
  "REL0050 PROPOSAL_RESPONSE: ATT0049 '파직하도록 했다'는 비변사 당상들의 건의에 대한 응답이라고 말하지 않음.",
  "SRC002 원문에서 정조의 이조원 파직 명령이 비변사 당상들의 건의에 응답한 것으로 서술되는지(윤허 등 응답 표지) 확인.",
  rels=["REL0050"])
NARRATIVE_ORDER_RELS = ["REL0003", "REL0007", "REL0008", "REL0014", "REL0015", "REL0016", "REL0017",
                        "REL0018", "REL0023", "REL0029", "REL0041"]
for _r in NARRATIVE_ORDER_RELS:
    q(f"ORDER_{_r}", "LOW", None, None, rels=[_r])  # problem/check filled from audit F below

# =====================================================================
# Decisions per audit row. Keys: (section letter, record_id).
# Each value: dict(cls, sec, basis, change, field, srq=[keys], sc=[ids], cur=custom current text)
# =====================================================================
D = {}


def d(sec_letter, rid, cls, basis, change, field, sec="", srq=(), sc=(), cur=None):
    D[(sec_letter, rid)] = dict(cls=cls, sec=sec, basis=basis, change=change, field=field,
                                srq=list(srq), sc=list(sc), cur=cur)


# ---------------- Audit A ----------------
MARKER_MAP = {
    "지목했다고 보고됨": "지목", "체포했다고 보고됨": "체포", "구금 상태라고 보고됨": "구금 상태",
    "조사했다고 보고됨": "조사", "사망했다고 보고됨": "사망", "입지라고 보고됨": "입지",
    "말했다고 전해짐": "말함", "편지로 힐책했다고 전해짐": "편지로 힐책", "주의를 줬다고 전해짐": "주의를 줌",
    "응답했다고 전해짐": "응답", "질문했다고 전해짐": "질문", "서찰을 건넸다고 전해짐": "서찰을 건넴",
    "요청했다고 전해짐": "요청", "정소했다고 전해짐": "정소", "보고했다고 전해짐": "보고",
    "전달했다고 전해짐": "전달", "재확인 요청했다고 전해짐": "재확인 요청", "답변했다고 전해짐": "답변",
}
CONTESTED_POST_SCHEMA = {"AT0114": "매일 불러들임", "AT0115": "말함", "AT0116": "회유", "AT0117": "떡·밥을 줌"}
AT0012_SPLIT = ("AT0012 재원자화 제안(승인 전 생성 금지): (a) [신규 행 제안] semantic_class=ORDER, event_family_id=EF_ORDER_INVESTIGATE, "
                "actor='이형원', action='조사 지시', target_or_content='각 진영 영장들에게 함께 조사하게 함'; "
                "(b) AT0012 유지·수정: actor '이형원/각 진영 영장'→'각 진영 영장', action '회동 조사 실시했다고 보고됨'→'회동 조사', "
                "target_or_content '관련자' 유지(ATT0012에 대상이 없음을 뜻하는 자리표시자로 notes에 명시), event_family_id=EF_ACT_INQUIRE_SEARCH 유지. "
                "(a)(b) 모두 ATT0012(이형원 보고)를 근거로 가리킴. 시간·장소 필드는 두 행 모두 현 AT0012 값 유지(place '충청도'는 원문 재확인 대상). "
                "보고 경로는 ATT0012(speaker=이형원, OFFICIAL_REPORT, CLAIM_WITHIN_OFFICIAL_REPORT)가 이미 보존. " + PRESERVE)
FAMILY_NOTE = "{FAMILY_NOTE}"  # replaced after counts are computed


def a_marker_change(e, a):
    new = MARKER_MAP[e["action"]]
    return (f"action '{e['action']}' → '{new}'. 보고·전언 경로는 이미 {a['attestation_id']}"
            f"(speaker={a['speaker_or_reporting_actor']}, attestation_mode={a['attestation_mode']}, "
            f"embedded_claim_status={a['embedded_claim_status']})가 보존하므로 정보 손실 없음. {PRESERVE}")


A_MARKER_BASIS = ("REPORTING_MARKER_IN_ACTION이고 embedded_claim_status가 CLAIM_CONTESTED가 아님 → 보고/전언 표지를 빼도 "
                  "attestation 층(speaker·attestation_mode·embedded_claim_status)이 같은 정보를 보존하므로 5개 CSV만으로 새 값 결정 가능.")

d("A", "AT0004", IF,
  "ATT0004와 ATT0005는 같은 SRC001 문장(이형원 장계 속 구순의 김명신 괴수 발언)을 보고층(AT0004)·사건층(AT0005)으로 이중 기록. 두 행의 관계는 CSV 안에서 결정 가능하며 삭제 없이 note로 표시 가능.",
  "AT0004·AT0005 두 행 모두 유지(삭제·병합 없음). AT0004.notes에 'AT0005와 같은 SRC001 문장(ATT0004/ATT0005)의 보고층 기록. 보고된 발언 자체는 AT0005가 사건층으로 표현' 추가. AT0005.notes에 '보고층 기록: AT0004' 추가.",
  "notes", cur="AT0004.action='장계' | AT0004.target_or_content='구순이 김명신을 도적 괴수라고 말했다는 내용' | AT0005.action='지목했다고 보고됨'")
d("A", "AT0119", IF,
  "Audit B(B-016)와 같은 행. 나중 진술 행위와 과거 대질 중 발화가 한 행에 섞인 것은 ATT0119 명제만으로 분리안 작성 가능. 층 구분을 영구적으로 표현하려면 SC-02 필요.",
  "B-016의 제안과 동일(AT0119를 나중 진술 행위로 유지 + 과거 alleged 사건 행 별도 제안 + REL0032 DURING 이동). 상세는 B-016 행 참조.",
  "action;target_or_content;historical_place;time_precision", sec=SC, sc=["SC-02"])
for _e in ("AT0114", "AT0115", "AT0116", "AT0117"):
    d("A", _e, SC,
      "embedded_claim_status=CLAIM_CONTESTED. '주장됨'은 events 테이블 안에서 유일한 미확정 표지이므로(TR-07) event 수준 주장·인식 상태 필드(SC-03)가 생기기 전에는 action에서 뺄 수 없음.",
      f"SC-03 도입 후: event 수준 claim_status=CONTESTED(자미덕 주장, ATT{_e[2:]} CLAIM_CONTESTED) 설정과 함께 action → '{CONTESTED_POST_SCHEMA[_e]}'. SC-03 이전에는 현 값 유지. {PRESERVE}",
      "action", sec=IF, sc=["SC-03"])
d("A", "AT0063", IF,
  "STATE 행 action에 진술 행위('진술')가 들어감. 진술 행위는 ATT0063(명업, TESTIMONY, CLAIM_BY_TESTIMONY)이 이미 보존.",
  f"action '신분 진술' → '신분'. 진술 행위·시점은 ATT0063(speaker=명업, attestation_mode=TESTIMONY, report_lunar_date=1793-06-13)이 보존. {PRESERVE}",
  "action")
d("A", "AT0064", IF,
  "STATE 행 action에 진술 행위('진술')가 들어감. 진술 행위는 ATT0064(명업, TESTIMONY, CLAIM_BY_TESTIMONY)이 이미 보존.",
  f"action '거주 상태 진술' → '거주 상태'. 진술 행위·시점은 ATT0064(speaker=명업, attestation_mode=TESTIMONY, report_lunar_date=1793-06-13)이 보존. {PRESERVE}",
  "action")

# ---------------- Audit B ----------------
STATEMENT_LAYER = ("{e}는 나중 진술 행위({who}의 안핵 공초, SRC004)로 유지: action 유지, 시간 상한=attestation 보고일 → occurrence_lunar_end='1793-06-13', "
                   "time_precision='BEFORE_OR_BY_REPORT'(현 값 '{tp}'는 아래 과거 사건 행으로 이동). historical_place('{pl}')는 진술 장소가 아니므로 값은 그대로 두고 "
                   "'설명 대상 과거 사건의 장소로 보임(진술 장소 미기재)'으로 notes에 표시. 별도 과거 사건 행 제안(승인 전 생성 금지, 명제 밖 내용 추가 없음): {past}. ")
d("B", "AT0119", IF,
  "BOTH: family/action은 나중 진술 층, place/time/REL0032(DURING)는 과거 대질 층. ATT0119 명제('이집거와 대질할 때 한재욱의 지휘에 따라 거짓으로 말했다')만으로 두 층 분리안 작성 가능. 영구 표현은 SC-02 필요.",
  STATEMENT_LAYER.format(e="AT0119", who="자미덕", tp="UNDATED_DURING_DETENTION", pl="병영",
                         past="actor='자미덕', semantic_class=ASSERTION, event_family_id=EF_SPEECH_CLAIM_REPORT, action='거짓으로 말했다고 주장됨'(SC-03 도입 후 '거짓으로 말함'+claim_status=CONTESTED), "
                              "target_or_content='이집거와 대질할 때 한재욱의 지휘에 따라', time_precision='UNDATED_DURING_DETENTION', historical_place='병영'(원문 재확인 대상), claim_topic/conflict_group=COACHING, 근거 ATT0119")
  + "REL0032(AT0118→AT0119 DURING)의 to_event를 신규 과거 사건 행으로 옮기는 안(REL0081은 진술 간 충돌이므로 AT0119에 유지). 관계 삭제 없음.",
  "action;target_or_content;historical_place;time_precision", sec=SC, sc=["SC-02"])
d("B", "AT0078", IF,
  "MULTIPLE_TIME_LAYERS: action은 나중 설명 행위, place/time은 설명 대상인 과거 병영 공초. ATT0078 명제만으로 분리안 작성 가능. 영구 표현은 SC-02 필요.",
  STATEMENT_LAYER.format(e="AT0078", who="명업", tp="UNDATED_DURING_INVESTIGATION", pl="충청병영",
                         past="actor='명업', semantic_class=ASSERTION, event_family_id=EF_SPEECH_CLAIM_REPORT, action='처음에 사실대로 말함', target_or_content='병영 뜰 공초', time_precision='UNDATED_DURING_INVESTIGATION', historical_place='충청병영', 근거 ATT0078"),
  "action;historical_place;time_precision", sec=SC, sc=["SC-02"])
d("B", "AT0079", IF,
  "MULTIPLE_TIME_LAYERS: 과거의 '위협을 두려워함' 상태와 나중 설명 행위가 한 행. ATT0079 명제만으로 분리안 작성 가능. 영구 표현은 SC-02 필요.",
  STATEMENT_LAYER.format(e="AT0079", who="명업", tp="UNDATED_DURING_INVESTIGATION", pl="충청병영",
                         past="actor='명업', semantic_class=STATE, event_family_id=EF_STATE_OTHER, action='위협을 두려워함', target_or_content='', time_precision='UNDATED_DURING_INVESTIGATION', historical_place='충청병영'(ATT0079 '병영에서'), 근거 ATT0079"),
  "action;historical_place;time_precision", sec=SC, sc=["SC-02"])
d("B", "AT0080", IF,
  "MULTIPLE_TIME_LAYERS: 과거 진술 변경과 나중 설명이 한 행. ATT0080 명제만으로 분리안 작성 가능. 영구 표현은 SC-02 필요.",
  STATEMENT_LAYER.format(e="AT0080", who="명업", tp="UNDATED_DURING_INVESTIGATION", pl="충청병영",
                         past="actor='명업', semantic_class=ASSERTION, event_family_id=EF_SPEECH_CLAIM_REPORT, action='진술을 바꿈', target_or_content='도적을 맞지 않은 것으로', time_precision='UNDATED_DURING_INVESTIGATION', historical_place='충청병영'(원문 재확인 대상), 근거 ATT0080"),
  "action;historical_place;time_precision", sec=SC, sc=["SC-02"])
d("B", "AT0131", IF,
  "MULTIPLE_TIME_LAYERS: action '부인'은 안핵 공초 시점 발화, place/time은 부인 대상(주장된 사주)의 과거 시점·장소. ATT0131 명제만으로 분리안 작성 가능. 사주 여부는 UNKNOWN/CONTESTED 유지(TR-18).",
  STATEMENT_LAYER.format(e="AT0131", who="한재욱", tp="UNDATED_DURING_DETENTION", pl="비장청",
                         past="부인 대상 행 — actor='한재욱', semantic_class=ACTION, event_family_id=EF_ACT_OTHER, action='자미덕을 은밀히 사주했다고 주장됨(한재욱 부인)', target_or_content='자미덕', time_precision='UNDATED_DURING_DETENTION', 근거 ATT0131(CONTESTED_DENIAL). "
                              "이 행은 사주가 있었다는 사실이 아니라 '부인된 주장 대상'을 나타내므로 SC-03(claim_status=DENIED/CONTESTED) 도입 전에는 생성 보류 권장")
  + "REL0080·REL0081은 진술 간 충돌이므로 AT0131에 유지.",
  "action;historical_place;time_precision", sec=SC, sc=["SC-02"])
d("B", "AT0132", SC,
  "action '부인'(공초 시점 발화)과 time_precision UNDATED_STATE(부인 내용인 관계 상태의 시간 성격)가 섞임. 부인 발화 시점과 부인된 상태의 시간층을 따로 둘 필드가 없음(행 수준 수정 불가).",
  "SC-02(진술 사건과 그 대상 상태의 연결)·SC-01(발화 시점 vs 상태 시간) 도입 후 time_precision을 진술 층(BEFORE_OR_BY_REPORT)과 대상 상태 층(UNDATED_STATE)으로 분리. 그 전까지 현 값 유지.",
  "time_precision", sc=["SC-02", "SC-01"])
d("B", "AT0012", IF,
  "MULTIPLE_EVENTS: ATT0012 '이형원은 각 진영의 영장들에게 함께 조사하게 했다' = 이형원의 지시 + 영장들의 조사 수행. 명제만으로 분할안 작성 가능.",
  "A-007과 같은 분할안: " + AT0012_SPLIT, "actor;action")
d("B", "AT0068", IF,
  "MULTIPLE_EVENTS: ATT0068 한 발화에 '30여 명의 도적, 횃불, 지세대감 자칭, 금품 절취' 네 명제가 묶임. 명제 문자열만으로 분할 가능.",
  "AT0068 분할 제안(승인 전 생성 금지; 4행 모두 actor='나복', action='말함'(A-012 적용 시), 근거 ATT0068, 시간·장소는 현 AT0068 값 유지): "
  "(1) AT0068 유지: target_or_content='도적 30여 명', claim_topic=THEFT_DESCRIPTION, conflict_group=THEFT_REALITY; "
  "(2) [신규] target_or_content='횃불', claim_topic=THEFT_DESCRIPTION, conflict_group=THEFT_REALITY; "
  "(3) [신규] target_or_content='도적들이 지세대감이라 자칭', claim_topic=JISE_ORIGIN, conflict_group=JISE_ORIGIN(AT0096 등과 같은 쟁점 코드); "
  "(4) [신규] target_or_content='금품 절취', claim_topic=THEFT_DESCRIPTION, conflict_group=THEFT_REALITY. "
  "최소안: (3)만 분리하고 나머지는 AT0068에 유지. " + PRESERVE + " " + FAMILY_NOTE,
  "target_or_content;claim_topic")
d("B", "AT0043", IF,
  "MULTIPLE_EVENTS: ATT0043 '김명신이 죽은 뒤 그의 아내도 사망했다'에 두 사망과 순서가 묶이고 아내 사망은 별도 행 없음. 명제만으로 분할안 작성 가능.",
  "AT0043 유지(이조원의 보고 행위, target '김명신 사망 뒤 아내도 사망'은 보고된 순서 내용으로 유지). [신규 행 제안, 승인 전 생성 금지] actor='김명신의 아내', semantic_class=ACTION, "
  "event_family_id=EF_ACT_DEATH, action='사망', target_or_content='', occurrence_lunar_end='1793-05-27', time_precision='BEFORE_OR_BY_REPORT', 근거 ATT0043(이조원 보고). "
  "AT0152 등 다른 아내 사망 관련 행과의 동일성 연결·병합은 제안하지 않음. " + FAMILY_NOTE,
  "target_or_content")
d("B", "AT0153", IF,
  "MULTIPLE_EVENTS: ATT0153 '곤장이나 평범한 신문을 받지 않았다'에 두 판단 명제. AT0151/AT0152는 같은 판결에서 분리되어 있어 같은 방식 적용 가능.",
  "AT0153 분할 제안(승인 전 생성 금지; 둘 다 actor='정조', action='최종 판단', claim_topic=TREATMENT_OF_KIM, 근거 ATT0153): "
  "(a) AT0153 수정: target_or_content='김명신이 곤장을 받지 않았다고 판단'; (b) [신규] target_or_content='김명신이 평범한 신문을 받지 않았다고 판단'. "
  "현 target의 '한 대도' 표현은 ATT0153 명제에 없으므로 원 target 전체를 notes에 보존(삭제 없음). " + FAMILY_NOTE,
  "target_or_content")
d("B", "AT0154", IF,
  "MULTIPLE_EVENTS: ATT0154는 '김명신 부처의 죽음'(두 사람)에 대한 판단인데 한 행이고 target에서 대상이 빠짐. AT0151/AT0152의 인물별 분리 방식 적용 가능.",
  "AT0154 분할 제안(승인 전 생성 금지; 둘 다 actor='정조', action='최종 판단', claim_topic/conflict_group=DEATH_CAUSE, 근거 ATT0154): "
  "(a) AT0154 수정: target_or_content='김명신의 죽음을 구순 때문에 직접 발생한 것으로 단정하기 어렵다고 판단'; "
  "(b) [신규] target_or_content='김명신 아내의 죽음을 구순 때문에 직접 발생한 것으로 단정하기 어렵다고 판단'. "
  "분할 미승인 시 대안: E-169의 target 주어 복원만 적용. " + PRESERVE + " " + FAMILY_NOTE,
  "target_or_content")
for _e, _why in (("AT0091", "'이미 붙잡혀 있었다'는 2/29 이전에 시작된 상태인데 occurrence는 이진욱이 확인한 시점. 상태 시작 시점과 관찰 시점을 따로 둘 필드가 없음."),
                 ("AT0099", "인물 식별(풍각 김생원=김명신)은 시점 없는 진술 내용인데 체포 지시 날짜가 붙음. 시점 없는(timeless) 동일성 진술을 표현할 필드가 없음."),
                 ("AT0100", "인물 식별(흥덕 김생원=김갑득)에 체포 지시 날짜가 붙음. 시점 없는 동일성 진술을 표현할 필드가 없음."),
                 ("AT0114", "'매일 불러들였다' = 반복 사건 계열을 한 행으로 표현. 반복 계열(횟수·개별 발생)을 표현할 구조가 없음.")):
    d("B", _e, SC, _why + " 행 수준에서 맞는 값을 고를 수 없음(값을 비우면 정보 손실).",
      "SC-01 도입 후 시간 필드를 사건 발생 시간·진술 시간·관찰 시간(및 상태 시작/관찰, 시점 없는 동일성, 반복 계열)으로 나눠 재기록. 그 전까지 현 값 유지.",
      "occurrence_lunar_start;occurrence_lunar_end;time_precision", sc=["SC-01"])
d("B", "AT0115", SR,
  "time_precision REPEATED_AFTER_ARREST의 반복 표지가 ATT0115에 없음. 반복 여부는 원문에서만 확인 가능. 현 값 유지.",
  "현 값 유지. 원문 재확인 결과 반복 표지가 없으면 time_precision을 반복 아님(예: UNDATED_DURING_DETENTION)으로 정렬하는 안을 그때 제시.",
  "time_precision", srq=["REPEAT_AT0115_0117"])
d("B", "AT0116", SR,
  "time_precision REPEATED_AFTER_ARREST의 반복 표지가 ATT0116에 없음. 회유가 1회인지 반복인지 원문에서만 확인 가능. 현 값 유지.",
  "현 값 유지. 원문 재확인 결과에 따라 time_precision 정렬 여부 결정.",
  "time_precision", srq=["AT0116_REPEAT"])
d("B", "AT0117", SR,
  "time_precision REPEATED_AFTER_ARREST의 반복 표지가 ATT0117에 없음. 반복 여부는 원문에서만 확인 가능. 현 값 유지.",
  "현 값 유지. 원문 재확인 결과 반복 표지가 없으면 time_precision 정렬 안을 그때 제시.",
  "time_precision", srq=["REPEAT_AT0115_0117"])
for _e in ("AT0161", "AT0168", "AT0170"):
    d("B", _e, SC,
      "historical_place가 처분 결정 장소가 아니라 유배 목적지를 뜻함(같은 family의 다른 처분 행은 결정 장소 한양). 장소의 역할을 구분할 필드가 없어 행 수준 수정 불가.",
      "SC-09 도입 후 목적지 값을 place_role=DESTINATION으로 재기록하고 결정 장소와 분리. 그 전까지 현 값 유지(값 삭제 없음).",
      "historical_place", sc=["SC-09"])
# B-003/B-004 (AT0063/AT0064) are not named in the rubric's Audit B list -> DEFAULT_USED: same fix as A-009/A-010.
for _e, _new in (("AT0063", "신분"), ("AT0064", "거주 상태")):
    d("B", _e, IF,
      f"DEFAULT_USED(지침의 Audit B 목록에 없음): 같은 행의 Audit A 지적(A-009/A-010)과 같은 원인(STATE 행 action에 진술 행위). 진술 시점 층은 ATT{_e[2:].zfill(4)}(report_lunar_date=1793-06-13)이 보존하므로 action만 상태로 바꾸면 시간층 혼합이 해소됨.",
      f"A-009/A-010과 같은 수정: action → '{_new}'(상태 서술만 남김). time_precision UNDATED_STATE 유지. {PRESERVE}",
      "action")

# ---------------- Audit C ----------------
for _e, _why in (("AT0012", "지시자(이형원)와 수행자(영장들)의 역할이 다른데 한 actor('/' 구분자)."),
                 ("AT0069", "대칭 관계 상태(상호 친숙)를 한 actor 문자열로 저장."),
                 ("AT0072", "대칭 관계 상태(왕래 단절)를 한 actor 문자열로 저장."),
                 ("AT0077", "쌍방 대화를 한 actor로 저장. 장교의 신원은 CSV에 없음."),
                 ("AT0118", "대질은 복수 참여자 사건이고 ATT0118 '자미덕은 이집거와 대질했다'(공동격 '와')로 방향성 없음.")):
    extra = (" 안 A(actor=자미덕, target=이집거)는 제안하지 않음(TR-15: 방향성 없는 공동격을 주체·대상으로 바꾸는 해석이 됨). participant 테이블이 생길 때까지 actor 현 값 유지."
             if _e == "AT0118" else "")
    d("C", _e, SC, "MULTIPLE_PARTICIPANTS_STORED_AS_ONE_ACTOR: " + _why + " actor/participant 구분 구조가 없어 행 수준에서 고칠 수 없음." + extra,
      "SC-04 도입 후 event_participants(event_id, participant, role, role_basis, provenance)로 참여자별 역할 분리. 그 전까지 actor 현 값 유지." + extra,
      "actor", sc=["SC-04"])
for _e in ("AT0089", "AT0090", "AT0092", "AT0093", "AT0094"):
    d("C", _e, SC,
      "GROUP_ACTOR(LOW): 같은 집단이 '이진욱·조계완 등'(AT0089·AT0090), '병영 장교 일행'(AT0092–AT0094), '장교 일행'(AT0101·AT0102)으로 다르게 표기됨. 같은 집단인지 CSV로 확정할 수 없고 집단 구성원을 표현할 구조가 없음(표기 통일은 동일성 판단이 되므로 행 수준 수정 아님).",
      "SC-04(participant·집단 구성원 테이블) 도입 후 집단 행위자를 구성원(이름 있는 구성원 + 미상 구성원 표지)과 함께 기록. 표기 통일·동일시는 하지 않음. 그 전까지 현 값 유지.",
      "actor", sc=["SC-04"])
d("C", "AT0016", SR,
  "GROUP_ACTOR: ATT0016은 '진술이 실려 있다'로 진술자를 밝히지 않음. actor '회동 조사 응답자들'은 인접 행에서 옮겨온 값이며 진술자는 원문에서만 확인 가능. 현 값 유지.",
  "현 값 유지. 원문 재확인 결과 진술자가 다르면 그때 수정안 제시.", "actor", srq=["AT0016_SPEAKER"])
d("C", "AT0074", IF,
  "ATT0074는 수동형('체포령이 내려졌다')으로 발령 주체 미상. '미상 관서'는 주체가 기록되지 않았음을 뜻하는 자리표시자로 해석 가능하며 CSV 안에서 결정 가능.",
  "값 '미상 관서' 그대로 유지. notes에 'ATT0074 수동형(체포령이 내려졌다): 발령 주체가 명제에 없음을 뜻하는 자리표시자' 명시.",
  "actor")
for _e in ("AT0086", "AT0087"):
    d("C", _e, IF,
      f"ATT{_e[2:].zfill(4)}는 수동형('철편 네 개가 {'만들어졌다' if _e == 'AT0086' else '제공됐다'}')으로 행위자가 없음. '한재욱 측'은 CSV 근거 없는 귀속이므로 CSV만으로 '미상'이 맞는 값임은 결정 가능. 원문이 행위자를 밝히는지는 별도 재확인.",
      f"actor '한재욱 측' → '미상'(attestation 수동형). 기존 값은 notes에 '원 actor: 한재욱 측(근거 미확인, 원문 재확인 대상)'으로 보존(삭제 없음). 원문에서 행위자가 확인되면 그 값으로 교체.",
      "actor", sec=SR, srq=["CHEOLPYEON_ACTOR"])
d("C", "AT0121", IF,
  "PERSON_AND_INSTITUTION: ATT0121 '한재욱은 … 병영 아전 유제희를 내보냈다'에서 '병영'은 유제희의 소속으로만 나오고 행위 주체는 한재욱. CSV만으로 결정 가능.",
  f"actor '한재욱/병영' → '한재욱'. '병영'은 유제희의 소속(병영 아전)이며 SC-04 도입 시 participant(유제희, role=dispatched, affiliation=병영)로 기록. {PRESERVE}",
  "actor", sec=SC, sc=["SC-04"])
ALIAS = {
    "병영 보조자 / 비장 / 한재욱": ("HIGH", "HAN_IDENTITY", "ATT0045 '병영 보조자'가 한재욱이라는 명제는 어떤 attestation에도 없고 REL0082만 둘을 동일시함."),
    "재돌 / 변재돌": ("MEDIUM", "ALIAS_JAEDOL", "'재돌'과 '변재돌'의 동일성이 CSV에 명시 없음."),
    "원돌 / 정원돌": ("MEDIUM", "ALIAS_WONDOL", "'원돌'과 '정원돌'의 동일성이 CSV에 명시 없음."),
    "풍각 김생원 / 풍각 김상제 / 풍각 상주 / 김명신": ("MEDIUM", "ALIAS_KIM", "ATT0099는 '풍각 김생원=김명신'만 명시. 김상제·상주와의 연결은 간접적."),
    "병사 / 이광섭": ("LOW", "ALIAS_BYEONGSA", "attestation은 '병사'만 언급. source_records.source_title 메타데이터는 이미 이광섭과 연결."),
}
for _k, (_p, _q, _why) in ALIAS.items():
    d("C", _k, SR,
      f"ALIAS_UNRESOLVED: {_why} 동일인 여부는 원문에서만 확인 가능(우선순위 {_p}). 확인 전까지 별개 표기로 유지, 자동 병합 금지. 인물·별칭을 표현할 구조도 필요(SC-04).",
      "현 표기 모두 유지(병합·통일 없음). 원문 확인 결과는 SC-04의 person/alias 테이블에 identity_status(CONFIRMED/CANDIDATE)와 근거로 기록.",
      "actor;target_or_content(인물 표기)", sec=SC, srq=[_q], sc=["SC-04"], cur=_k)

# ---------------- Audit D ----------------
d("D", "audit_04_person_set_membership", SC,
  "INFO: 인물×집합 UNKNOWN 칸은 추론으로 채우면 안 되며, 열린 집합('여러 사람', '등', '특정 인물들')의 소속 상태를 표현할 구조가 없음.",
  "SC-06 도입 후 집합(closure_status OPEN/CLOSED, 열린 표지 원문) + 소속 행(DIRECT/ABSENT/UNKNOWN, 근거)으로 기록. UNKNOWN 칸은 그대로 UNKNOWN으로 보존(추론으로 채우지 않음).",
  "membership(표)", sc=["SC-06"], cur=None)
d("D", "AT0122", SR,
  "유제희 명단 7명은 AT0122.target_or_content에만 있고 ATT0122는 '여러 사람'만 말함. 4명은 어떤 attestation에도 없음. 명단은 원문에서만 확인 가능. 현 값 유지(삭제 없음).",
  "현 값 유지. 원문 재확인 전까지 S1 근거를 EVENT_FIELD_ONLY로 표시(SC-05/SC-06). 원문 확인 결과에 따라 명단·열린 표지 기록.",
  "target_or_content", sec=SC, srq=["AT0122_LIST"], sc=["SC-06"])
d("D", "김명신", SR,
  "S5(신문) 충돌: ATT0008(이형원) vs ATT0153(정조). 두 attestation 모두 보존 대상이며 충돌은 원문 표현 확인으로만 성격을 기록할 수 있음. 충돌은 보존하며 어느 쪽도 사실로 승격하지 않음.",
  "변경 없음. 충돌 보존(어느 쪽도 승격하지 않음). 원문 표현 확인 결과는 note로만 기록.",
  "action;target_or_content", srq=["KIM_S5_CONFLICT"],
  cur="AT0008.action='조사했다고 보고됨' | AT0153.target_or_content='김명신이 곤장 한 대도 맞지 않았고 평범한 신문도 받지 않았다고 판단'")
d("D", "이집거", SR,
  "이집거는 대질 상대로만 DIRECT. 이집거의 역할과 대질에 이른 경위는 CSV에 없고 원문에서만 확인 가능. 이집거를 '지목 대상'·'용의자'로 다루는 파생 금지.",
  "변경 없음. 원문 재확인 전까지 이집거 관련 파생 데이터 생성 금지.", "actor", srq=["ICHIPGEO_ROLE"],
  cur="AT0118.actor='자미덕·이집거' | ATT0119 '이집거와 대질할 때'")

# ---------------- Audit E ----------------
E_INTERNAL = {
    ("AT0010", "claim_topic"): (
        "ATT0010 '구금·조사 뒤 죽었다'에는 원인 진술이 없고 순서만 있음(TR-03). 원인이 아닌 사망 관련 기존 코드는 DEATH_SEQUENCE(AT0043)뿐이며 ATT0010은 순서 진술이므로 CSV 안에서 결정 가능.",
        "claim_topic 'DEATH_CAUSE' → 'DEATH_SEQUENCE'(원인이 아닌 순서 주제; 신규 코드 DEATH_OCCURRENCE 도입은 사용자 결정, TR-03). ATT0010.claim_topic도 같은 값으로 정렬. 기존 값은 notes에 '원 claim_topic: DEATH_CAUSE'로 보존(삭제 없음). 원인 주장 행(AT0042·AT0148·AT0151·AT0154)은 DEATH_CAUSE 유지.",
        "", [], []),
    ("AT0010", "conflict_group"): (
        "ATT0010에는 원인 진술이 없어 DEATH_CAUSE 충돌 그룹에 들어갈 근거가 없음(TR-03). CSV 안에서 결정 가능.",
        "conflict_group 'DEATH_CAUSE' → 빈 값(DEATH_CAUSE 충돌 그룹에서 제외). ATT0010.conflict_group도 정렬. 기존 값은 notes에 '원 conflict_group: DEATH_CAUSE'로 보존(삭제 없음). REL0083(AT0010↔AT0042)은 유지.",
        "", [], []),
    ("AT0026", "target_or_content"): (
        "target '도난 자체가 없었다는 방향'은 ATT0026('구순이 도난을 꾸몄다는 방향을 받아들였다')보다 넓은 표현. 명제 수준으로 바로 정렬 가능.",
        "target_or_content → '구순이 도난을 꾸몄다는 방향을 받아들임'. " + PRESERVE, "", [], []),
    ("AT0116", "target_or_content"): (
        "target '여러 사람'과 ATT0116 명제 '특정 인물들'의 표현 차이(TR-09). 명제 표현으로 정렬 가능.",
        "target_or_content '여러 사람을 큰 도적이라 말하면 부부를 석방하겠다는 조건' → '특정 인물들을 큰 도적이라 말하면 부부를 석방하겠다는 조건'. 열린 집합 표지 '특정 인물들'은 SC-06에서 closure_status=OPEN으로 기록. " + PRESERVE,
        SC, [], ["SC-06"]),
    ("AT0119", "target_or_content"): (
        "target '거짓말을 꾸몄다'는 ATT0119('거짓으로 말했다')보다 강하고 '이집거와 대질할 때'가 빠짐. 명제 수준으로 정렬 가능.",
        "target_or_content → '이집거와 대질할 때 한재욱의 지휘에 따라 거짓으로 말했다고 주장'. (B-016 분할 승인 시 이 내용은 과거 사건 행의 target으로 이동.) " + PRESERVE,
        "", [], []),
    ("AT0154", "target_or_content"): (
        "ATT0154의 대상 '김명신 부처의 죽음'이 target에서 빠짐. 명제에서 주어 복원 가능.",
        "target_or_content → '김명신 부처의 죽음을 구순 때문에 직접 발생한 것으로 단정하기 어렵다고 판단'(B-020 분할 승인 시 인물별 문구 사용). " + PRESERVE,
        "", [], []),
    ("AT0012", "action"): (
        "action '회동 조사 실시'는 ATT0012의 사역(지시)과 수행을 합침. A-007/B-001 분할안으로 해결.",
        "A-007/B-001 분할안 적용: (a) 이형원 '조사 지시' (신규 행 제안), (b) AT0012 action → '회동 조사'. " + PRESERVE, "", [], []),
    ("AT0012", "target_or_content"): (
        "'관련자'는 ATT0012에 없는 자리표시자. 분할안에서 자리표시자임을 명시하면 CSV 안에서 해결.",
        "A-007/B-001 분할안 적용: (b) AT0012 target_or_content '관련자' 유지, notes에 'ATT0012에 조사 대상이 없음을 뜻하는 자리표시자' 명시. (a) 신규 ORDER 행 target='각 진영 영장들에게 함께 조사하게 함'.",
        "", [], []),
    ("AT0086", "actor"): (
        "ATT0086 수동형('만들어졌다'). '한재욱 측'은 근거 없는 귀속. C-007과 같은 판단.",
        "actor '한재욱 측' → '미상'. 기존 값은 notes에 '원 actor: 한재욱 측(근거 미확인, 원문 재확인 대상)'으로 보존(삭제 없음).",
        SR, ["CHEOLPYEON_ACTOR"], []),
    ("AT0087", "actor"): (
        "ATT0087 수동형('제공됐다'). '한재욱 측'은 근거 없는 귀속. C-008과 같은 판단.",
        "actor '한재욱 측' → '미상'. 기존 값은 notes에 '원 actor: 한재욱 측(근거 미확인, 원문 재확인 대상)'으로 보존(삭제 없음).",
        SR, ["CHEOLPYEON_ACTOR"], []),
    ("AT0121", "actor"): (
        "ATT0121에서 '병영'은 유제희의 소속일 뿐 행위 주체가 아님. C-015와 같은 판단.",
        "actor '한재욱/병영' → '한재욱'. " + PRESERVE, SC, [], ["SC-04"]),
    ("AT0074", "target_or_content"): (
        "'관련 대상'은 ATT0074에 체포 대상이 없음을 뜻하는 자리표시자. CSV 안에서 결정 가능.",
        "값 '관련 대상' 그대로 유지. notes에 'ATT0074에 체포 대상이 명시되지 않음을 뜻하는 자리표시자' 명시. 열린 표지로 SC-06에 기록.",
        SC, [], ["SC-06"]),
    ("AT0089", "target_or_content"): (
        "'출발 시점'은 ATT0089('날이 밝아 새벽을 기다렸다')의 기다림 대상을 나타낸 자리표시자. CSV 안에서 결정 가능.",
        "값 '출발 시점' 그대로 유지. notes에 'ATT0089에 기다림의 대상이 명시되지 않음을 뜻하는 자리표시자' 명시.",
        "", [], []),
    # AT0074.actor: not named in the Audit E rubric; resolved consistently with the Audit C rubric (C-005).
    ("AT0074", "actor"): (
        "Audit E 목록에 없음 → Audit C 지침(C-005, 같은 행·같은 필드)과 일관되게 처리. ATT0074 수동형('체포령이 내려졌다'): '미상 관서'는 주체 미상 자리표시자.",
        "값 '미상 관서' 그대로 유지. notes에 'ATT0074 수동형: 발령 주체가 명제에 없음을 뜻하는 자리표시자' 명시.",
        "", [], []),
}
E_SCHEMA = {}
for _e in ("AT0114", "AT0115", "AT0117", "AT0125", "AT0126"):
    for _f in ("claim_topic", "conflict_group"):
        E_SCHEMA[(_e, _f)] = (
            "COACHING 값은 해당 attestation이 사주를 직접 주장하는 것이 아니라 AT0116/REL0078/REL0079 맥락에서 묶인 것. conflict_group이 '직접 다투어지는 주장'인지 '맥락상 묶음'인지 정의가 없어 행 수준에서 맞는 값을 고를 수 없음.",
            "SC-08(conflict_group 의미 구분: direct claim / contextual grouping) 도입 후 COACHING을 해당 의미로 재분류. 그 전까지 현 값 유지.", ["SC-08"])
for _e in ("AT0099", "AT0100"):
    for _f in ("occurrence_lunar_start", "occurrence_lunar_end"):
        E_SCHEMA[(_e, _f)] = (
            "시점 없는 인물 식별 진술에 체포 지시 날짜(AT0097)가 붙음. 시점 없는(timeless) 동일성을 표현할 시간 필드가 없어, 비우면 정보 손실이고 두면 과잉 주장.",
            "SC-01 도입 후 timeless identity로 표시하고 날짜는 '진술 대상 체포 지시의 날짜' 층으로 분리. 그 전까지 현 값 유지.", ["SC-01"])
E_SCHEMA[("AT0170", "historical_place")] = (
    "'원도'는 '먼 섬'의 범주어이며 목적지 의미. 장소 역할 구분 필드가 없어 행 수준 수정 불가.",
    "SC-09 도입 후 place_role=DESTINATION, 값 성격=범주어(지명 아님)로 기록. 그 전까지 현 값 유지.", ["SC-09"])

# Audit E SOURCE groups -> which queue key; the queue key's priority is the rubric priority.
E_SOURCE_GROUPS = ["AT0122_LIST", "AT0036_TARGET", "HAN_IDENTITY", "JAMIDEOK_DATES", "SRC001_DATES",
                   "AT0007_PLACE", "AT0010_PLACE",
                   "UPPER_MYEONGEOP", "UPPER_HAN", "UPPER_YOO", "JOGYEWAN_DATES", "AT0073_TARGET_PLACE",
                   "AT0120_ACTOR", "AT0012_PLACE", "PLACE_IJW_DEOKPYEONG", "PLACE_MYEONGEOP_DEOKPYEONG",
                   "YOO_INQUIRY_PLACE", "HAN_BIJANG_PLACE", "JAMIDEOK_ARREST_PLACE", "CONFRONT_PLACE",
                   "LIST_PLACE", "HOSEO_PLACE", "ISSUE_LABELS", "AT0171_ESA",
                   "HANYANG_SRC001", "HANYANG_SRC002", "HANYANG_SRC003", "HANYANG_SRC004",
                   "ACTOR_INST_PLACE", "PLACE_MYEONGEOP_HOUSE", "PLACE_CHEOLPYEON", "PLACE_JAMIDEOK_ROOM",
                   "PLACE_GONGJU", "DATES_AT0017_19", "DATE_AT0068", "DATE_AT0069", "DATE_AT0088",
                   "DATE_AT0101_0102", "AT0016_SPEAKER"]
# (event, field) explicitly NOT named in the rubric -> default rule applied (recorded).
E_DEFAULT_USED = {("AT0133", "target_or_content")}
# rubric priority of a row when it shares a queue question with higher-priority rows
E_RUBRIC_PRIO = {("AT0124", "historical_place"): "LOW", ("AT0007", "historical_place"): "HIGH"}
# schema refs for Audit E SOURCE rows: SC-05 always (keep the unsupported value with provenance);
# SC-07 when the value travelled over a candidate/coreference relation; SC-09 when actor institution became place;
# SC-01 when the date is a record date standing in for an act/statement time.
E_EXTRA_SC = {
    "JAMIDEOK_DATES": ["SC-07"], "AT0010_PLACE": ["SC-07"], "AT0073_TARGET_PLACE": ["SC-07"],
    "AT0120_ACTOR": ["SC-07"], "HAN_IDENTITY": ["SC-04"], "ACTOR_INST_PLACE": ["SC-09"],
    "DATES_AT0017_19": ["SC-01"], "AT0122_LIST": ["SC-06"],
}

# ---------------- Audit F ----------------
F_INTERNAL = {
    "REL0032": ("자미덕은 이집거와 대질할 때 한재욱의 지휘에 따라 거짓으로 말했다고 진술",
                "basis의 '거짓 지목'은 ATT0119('거짓으로 말했다')에 없는 '지목' 행위를 추가한 문구 강화. 명제 수준으로 바꾸는 것은 CSV 안에서 결정 가능. 거짓말의 내용은 원문에서만 확인 가능(보조 SOURCE). DURING이 진술 행(AT0119)에 붙은 문제는 B-016/SC-02로 처리.",
                SR, ["REL0032_CONTENT"], ["SC-02"],
                " B-016 분할 승인 시 to_event를 신규 과거 사건 행으로 이동(관계 삭제 없음)."),
    "REL0020": ("이진욱은 체포 작전을 위해 철편 네 개가 제공됐다고 진술하고, 날이 밝아 새벽을 기다렸다고 진술(진술 서술 순서)",
                "basis '철편 준비 사이'는 두 명제 어디에도 없고 '사이'(겹침)는 relation_type BEFORE와 맞지 않음. 해당 구절을 빼면 basis/type 불일치 해소.",
                "", [], [], " relation_type BEFORE 유지(겹침 표현 제거로 type과 basis 불일치 해소). 순서 근거가 서술 순서임은 SC-07 order_basis=NARRATIVE_ORDER로 표시."),
    "REL0022": ("이진욱은 새벽에 일행이 나갔다고 진술하고, 현장에 나갔을 때 변지돌이 이미 공주진에 붙잡혀 있었다고 진술(체포 상태는 출발 시점에 이미 존재)",
                "basis '변지돌의 기존 체포 상태 확인'은 상태를 '확인 행위'로 바꿔 읽음. 명제 수준 문구로 바꾸는 것은 CSV 안에서 가능. 상태 시작/관찰 시간층 분리는 SC-01 필요.",
                SC, [], ["SC-01"], " relation_type BEFORE는 관찰(현장 도착)에만 성립하므로 SC-01 도입 시 상태→관찰 관계로 재검토."),
    "REL0040": ("조계완은 풍각의 상주를 잡으러 왔다고 구순에게 답했다고 진술하고, 구순이 수사가 이제야 바른 길을 얻었다는 취지로 말했다고 진술",
                "basis '구순 반응'은 ATT0106을 답변에 대한 반응으로 규정(연결 표지 없음). 문구 강화이므로 명제 수준으로 낮추면 해결.", "", [], [], ""),
    "REL0046": ("정조는 당시 도 장계와 조사 문건을 근거로 구순이 도난을 꾸몄다는 방향을 받아들였고, 구순을 의금부로 잡아오라고 명함(판단을 명령의 근거로 했다는 표지는 없음)",
                "basis '당시 판단 뒤 구순 체포 명령'은 판단→명령 연결을 암시. 명제 수준 문구로 바꾸면 해결.", "", [], [], ""),
    "REL0047": ("정조는 구순을 의금부로 잡아오라고 명하고, 구순을 수금하라고 명함(두 행 모두 명령이며 집행 기록 아님)",
                "basis '잡아온 뒤 수금'은 명령을 집행으로 서술. 두 행 모두 명령이므로 명제 수준으로 바꾸면 해결.", "", [], [], ""),
    "REL0048": ("정조는 구순을 수금하라고 명하고, 구순을 엄히 조사하라고 명함(두 행 모두 명령이며 집행 기록 아님)",
                "basis '수금 뒤 엄한 조사'는 명령을 집행으로 서술. 명제 수준으로 바꾸면 해결.", "", [], [], ""),
    "REL0051": ("정조는 이조원이 중대한 사안을 직접 조사하지 않고 전해 들은 말을 보고한 조사 방식을 비판했고, 이조원을 파직하도록 함(비판을 파직의 근거로 했다는 표지는 없음)",
                "basis '조사방식 비판 뒤 파직'은 근거 관계를 암시. 명제 수준으로 바꾸면 해결.", "", [], [], ""),
    "REL0053": ("홍대협은 전년 호서 화적들이 지세랑 호칭을 쓴 적이 있다고 들었다고 답하고, 지세랑 호칭이 이번 사건에서 처음 생긴 말은 아닌 듯하다고 의견을 밝힘(전언을 의견의 근거로 했다는 표지는 없음)",
                "basis '토대로'는 ATT0056에 없는 근거 관계를 추가한 문구. 명제 수준으로 바꾸면 해결.", "", [], [],
                " relation_type EVIDENCE_TO_INFERENCE는 유지하되 근거 관계가 명시되지 않았음을 basis에 표시."),
    "REL0057": ("홍대협은 응당 신문할 사람들을 차례로 신문했다고 서계하고, 정식 조사 결과 약간의 도난은 실제였다고 판단",
                "basis '재신문'은 ATT0062('차례로 신문')에 없는 앞선 신문을 전제. 명제 수준으로 바꾸면 해결.", "", [], [], ""),
    "REL0063": ("정조는 안핵 서계를 토대로 도난이 실제로 있었다고 판단하고, 구순을 감하여 외딴 섬에 정배하라고 명함(처분이 어느 판단에 근거했는지는 명시 없음)",
                "basis '최종 심리 뒤 구순 처분'은 AT0150을 처분 근거로 고른 것처럼 읽힘. 명제 수준 문구 + 근거 미명시 표시로 해결.", "", [], [], ""),
    "REL0064": ("정조는 이광섭이 비장에게 일을 맡겼다고 평가하고, 이광섭을 먼 곳에 무기한 정배하라고 명함(처분이 어느 평가에 근거했는지는 명시 없음)",
                "basis '이광섭 책임 평가 뒤 정배'는 AT0166만을 근거로 고름. 명제 수준 문구 + 근거 미명시 표시로 해결.", "", [], [], ""),
    "REL0065": ("구순의 도난 여부에 관해 도신 장계와 어사 보고가 크게 달랐다는 지적 뒤 이형원 파직",
                "basis '도신 장계 오류 평가'는 ATT0171('크게 달랐다')에 없는 잘못의 귀속을 추가. '오류'와 근거 주장을 빼면 해결.", "", [], [], ""),
    "REL0066": ("기재된 음력 날짜 비교: 2/22 < 2/28 (AT0068 날짜는 ATT0068에 없고 AT0065에서 옮겨온 값)",
                "basis의 '확정'은 근거 없는 강화(AT0068 날짜는 Audit E AMBIGUOUS). '확정'을 빼면 해결. 날짜 자체는 Audit E 원문 재확인 대상.", "", [], [], ""),
    "REL0067": ("기재된 음력 날짜 비교: 2/29 < 3/4 (AT0092 날짜는 ATT0092에 없고 relation 사슬·날짜 계산으로 얻은 값)",
                "basis의 '확정'은 근거 없는 강화. '확정'을 빼면 해결. 날짜 자체는 Audit E 대상.", "", [], [], ""),
    "REL0068": ("기재된 음력 날짜 비교: 3/4 < 5/12 (AT0101 날짜는 체포 명령 날짜이며 ATT0101에 집행 날짜 없음)",
                "basis의 '확정'은 근거 없는 강화. '확정'을 빼면 해결. 날짜 자체는 Audit E 원문 재확인 대상.", "", [], [], ""),
    "REL0080": ("자미덕은 석방 조건 회유를 주장하고 한재욱은 사주를 부인",
                "basis '회유·사주를 주장'은 한재욱 부인(ATT0131)의 단어 '사주'를 자미덕 주장에 부여. 명제 수준으로 바꾸면 해결.", "", [], [],
                " relation_type의 'SAME_ALLEGED_EVENT' 명칭 문제는 TR-19(사용자 결정)로 남김."),
    "REL0085": ("홍대협과 정조가 같은 사망 사건의 사인을 질병/전염병으로 판단",
                "basis의 '직접'은 ATT0148·ATT0151 어디에도 없는 강화. '직접'을 빼면 해결.", "", [], [], ""),
    "REL0088": ("이형원 장계에는 구순이 김명신을 도적의 괴수라고 말했다고 적혀 있고, 유제희는 탐문 중 구순이 풍각 김상제가 매우 수상하다고 말했다고 진술(동일 발화 여부와 김상제=김명신 여부는 미확인)",
                "basis는 '수상하다'를 '지목'으로 강화. '수상하다고 말함' 수준으로 낮추는 것은 CSV 안에서 가능. 김상제=김명신 동일성은 원문에서만 확인 가능(보조 SOURCE MEDIUM).",
                SR, ["ALIAS_KIM"], [], ""),
}
F_SOURCE = {
    "REL0082": ("HAN_IDENTITY", IF,
                "이조원은 병영 보조자가 구순의 가객이었다고 주장하고, 한재욱은 구순과 평생 모르는 사이라고 진술(병영 보조자와 한재욱의 동일인 여부 미확인)",
                "NEW_INFORMATION_ADDED: 병영 보조자=한재욱 동일성은 어떤 attestation에도 없음. 동일성은 원문에서만 확인 가능(HIGH). 확인 전 임시로 basis를 동일인 여부 미확인으로 낮추는 안(보조 INTERNAL)."),
    "REL0010": ("REL0010", IF,
                "한재욱은 도적의 진상을 탐지하려고 병영 아전 유제희를 내보냈다고 진술하고, 유제희는 당초 현지에 가서 탐문했다고 진술(파견의 집행인지는 미확인; 같은 쌍의 REL0074는 후보 연결)",
                "유제희 탐문이 한재욱 파견의 집행인지는 ATT0133에 없음. 원문 확인 필요(MEDIUM). 확인 전 임시 hedged basis 제안(보조 INTERNAL)."),
    "REL0089": ("REL0089", IF,
                "유제희는 탐문 중 구순이 풍각 김상제가 매우 수상하다고 말했다고 진술하고, 정조는 구순이 병영의 탐문자에게 김명신의 이름을 적어 주었다고 판단(누가 이름을 적었는지는 두 명제가 다름)",
                "누가 이름을 적었는지가 두 명제에서 다름. 원문 확인 필요(MEDIUM). 확인 전 임시 hedged basis 제안(보조 INTERNAL)."),
    "REL0060": ("ISSUE_LABELS", IF,
                "정조는 공주목 안핵의 핵심을 세 가지 의안으로 분리했고, 안핵 서계를 토대로 도난이 실제로 있었다고 판단(이 판단이 어느 의안에 해당하는지는 ATT0149에 명시 없음)",
                "의안 이름은 ATT0149에 없음. 원문 확인 필요(MEDIUM). 확인 전 임시 hedged basis 제안(보조 INTERNAL)."),
    "REL0061": ("ISSUE_LABELS", IF,
                "정조는 공주목 안핵의 핵심을 세 가지 의안으로 분리했고, 김명신이 전염병에 걸려 죽은 것으로 판단(이 판단이 어느 의안에 해당하는지는 ATT0149에 명시 없음)",
                "의안 이름은 ATT0149에 없음. 원문 확인 필요(MEDIUM). 확인 전 임시 hedged basis 제안(보조 INTERNAL)."),
    "REL0062": ("ISSUE_LABELS", IF,
                "정조는 공주목 안핵의 핵심을 세 가지 의안으로 분리했고, 지세 계열 호칭이 이전부터 무식한 좀도둑들이 쓰던 말이라고 판단(이 판단이 어느 의안에 해당하는지는 ATT0149에 명시 없음)",
                "의안 이름은 ATT0149에 없고, AT0149 target의 '날조 여부'와 AT0155의 '기원' 판단이 어긋남. 원문 확인 필요(MEDIUM). 확인 전 임시 hedged basis 제안(보조 INTERNAL)."),
    "REL0073": (["AT0073_TARGET_PLACE", "AT0120_ACTOR"], IF,
                "명업은 구순이 소장을 올렸다고 진술하고, 한재욱은 구순 집 도난이 진영에 정소된 뒤라고 진술(두 진술의 세부 결합은 미확인)",
                "basis '구순의 진영 정소'는 두 진술의 세부(명업: 정소 주체, 한재욱: 진영)를 합침. 각 진술이 그 세부를 갖는지는 원문 확인 필요(MEDIUM). 확인 전 임시 hedged basis 제안(보조 INTERNAL)."),
    "REL0077": ("REL0077", IF,
                "이진욱은 변지돌 대신 재돌의 처 자미덕만을 잡았다고 진술하고, 자미덕은 병영 장교가 갑자기 찾아와 자신을 붙잡았다고 진술(같은 체포인지 미확인 후보)",
                "basis '같은 자미덕 체포'는 후보 relation을 단정형으로 씀. 같은 체포인지는 원문 확인 필요(MEDIUM). 확인 전 임시 hedged basis 제안(보조 INTERNAL). 이 연결을 통한 날짜 전파 문제는 SC-07.")
    ,
    "REL0050": ("REL0050", "", None,
                "PROPOSAL_RESPONSE(건의→명령 응답)는 ATT0049에 응답 표지가 없음. 원문에서만 확인 가능(LOW). basis 문구 자체는 이미 중립적이라 보조 수정 없음."),
}
for _r in NARRATIVE_ORDER_RELS:
    F_SOURCE[_r] = (f"ORDER_{_r}", SC, None,
                    "선후 근거가 진술 서술 순서뿐(명시적 순서 표지 없음). 원문에 순서 표지가 있는지는 원문에서만 확인 가능(LOW). 순서 근거 유형을 표현할 필드가 필요(SC-07 order_basis).")

# =====================================================================


def main():
    LOGS.mkdir(exist_ok=True)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(LOGS / "repair_classification.log", mode="w", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.setLevel(logging.INFO)
    log.addHandler(fh)
    log.addHandler(sh)

    before = {f: sha(RAW / f) for f in FILES.values()}
    for f, h in before.items():
        log.info("sha256 before %s %s", f, h)

    ev = {e["event_id"]: e for e in load_raw("events")}
    at = {a["event_id"]: a for a in load_raw("attestations")}
    rels = {r["relation_id"]: r for r in load_raw("event_relations")}
    fams = {f["event_family_id"]: f for f in load_raw("event_families")}
    src = {s["source_record_id"]: s for s in load_raw("source_records")}
    master = load_out("audit_master_summary.csv")
    audit_f = {r["relation_id"]: r for r in load_out("audit_06_relation_meaning_overreach.csv")}
    audit_e = load_out("audit_05_field_level_provenance.csv")
    membership = load_out("audit_04_person_set_membership.csv")
    assert len(master) == 303, len(master)
    assert len({m["audit_id"] for m in master}) == 303

    # ---------- family member_count net effect ----------
    actual = Counter(e["event_family_id"] for e in ev.values())
    for fid, f in fams.items():
        assert int(f["member_count"]) == actual.get(fid, 0), f"member_count mismatch {fid}"
    definite = Counter(actual)
    for eid, frm, to, _ in FAMILY_MOVES:
        assert ev[eid]["event_family_id"] == frm
        definite[frm] -= 1
        definite[to] += 1
    cond = Counter(definite)
    for _, fid, _ in SPLIT_NEW_ROWS:
        assert fid in fams
        cond[fid] += 1
    def_txt = ", ".join(f"{k} {actual.get(k, 0)}→{definite[k]}" for k in sorted(fams) if definite[k] != actual.get(k, 0))
    cond_txt = ", ".join(f"{k} {actual.get(k, 0)}→{cond[k]}" for k in sorted(fams) if cond[k] != actual.get(k, 0))
    family_note = (f"member_count 순효과(이 분류의 family 제안 전체 기준): 확정 제안(AT0008·AT0010 family 이동) {def_txt}; "
                   f"분할 제안까지 모두 승인 시 {cond_txt}. 같은 버전에서 함께 갱신.")
    log.info("family net effect definite: %s", def_txt)
    log.info("family net effect incl. approved splits: %s", cond_txt)

    # A decisions that need raw data (reporting-marker rows) + family extras
    for m in master:
        if m["audit_id"].startswith("A-") and ("A", m["record_id"]) not in D:
            e, a = ev[m["record_id"]], at[m["record_id"]]
            assert "REPORTING_MARKER_IN_ACTION" in m["finding"], m["audit_id"]
            assert a["embedded_claim_status"] != "CLAIM_CONTESTED"
            eid = e["event_id"]
            if eid == "AT0012":
                d("A", eid, IF, A_MARKER_BASIS + " 단 '회동 조사 실시'는 지시와 수행을 합친 값이라 표지 제거만으로는 부족 → 재원자화. actor/participant 구조는 SC-04.",
                  AT0012_SPLIT, "actor;action;target_or_content", sec=SC, sc=["SC-04"])
                continue
            change = a_marker_change(e, a)
            field = "action"
            if eid == "AT0008":
                change += " 추가: event_family_id EF_ACT_RECORD_REPORT → EF_ACT_INQUIRE_SEARCH('조사' 행위는 기록·보고가 아니라 탐문·조사 family). " + FAMILY_NOTE
                field = "action;event_family_id"
            if eid == "AT0010":
                change += (" 추가: event_family_id EF_ACT_RECORD_REPORT → EF_ACT_DEATH(기존 family, member_count 0, semantic_class=ACTION 일치; TR-01/TR-02). "
                           "target_or_content 빈 값 유지(사망은 target 불요, TR-16). " + FAMILY_NOTE)
                field = "action;event_family_id"
            d("A", eid, IF, A_MARKER_BASIS, change, field)

    # ---------- fill queue members that depend on data ----------
    hanyang = [(eid, "historical_place") for eid, e in ev.items() if e["historical_place"] == "한양"]
    e_master = {m["record_id"]: m for m in master if m["audit_id"].startswith("E-")}
    for eid, f in hanyang:
        if f"{eid}.{f}" in e_master:
            Q[f"HANYANG_{at[eid]['source_record_id']}"]["members"].append((eid, f))
    for r in NARRATIVE_ORDER_RELS:
        af = audit_f[r]
        Q[f"ORDER_{r}"]["problem"] = f"{r} {rels[r]['relation_type']}: {af['finding']}"
        sid = at[rels[r]["to_event_id"]]["source_record_id"]
        Q[f"ORDER_{r}"]["check"] = (f"{sid} 원문의 해당 진술({at[rels[r]['from_event_id']]['speaker_or_reporting_actor']} 공초) 구간에 "
                                    f"두 행위 사이의 명시적 순서 표지('뒤', '후', '그 뒤', '이어' 등)가 있는지 확인. 없으면 서술 순서 근거로 표시(SC-07).")

    member_to_q = {}
    for k, v in Q.items():
        for mem in v["members"]:
            if k in E_SOURCE_GROUPS:
                assert mem not in member_to_q, f"duplicate member {mem} in {k} and {member_to_q[mem]}"
                member_to_q[mem] = k

    # ---------- build repair rows ----------
    rows = []
    default_used = []

    def cur_val(eid, fields):
        vals = [(f, ev[eid][f]) for f in fields.split(";") if f in ev[eid]]
        if len(vals) == 1:
            return vals[0][1]
        return " | ".join(f"{f}='{v}'" for f, v in vals)

    for i, m in enumerate(master, 1):
        aid, sec_letter, rid = m["audit_id"], m["audit_id"][0], m["record_id"]
        if sec_letter == "E":
            eid, field = rid.split(".")
            cls_tag = re.match(r"\[([A-Z_]+)\]", m["finding"]).group(1)
            current = ev[eid][field]
            assert f"{field}='{current}'" in m["finding"], aid
            key = (eid, field)
            if key in E_INTERNAL:
                basis, change, sec, srq, scs = E_INTERNAL[key]
                dec = dict(cls=IF, sec=sec, basis=basis, change=change, field=field, srq=srq, sc=scs, cur=current)
            elif key in E_SCHEMA:
                basis, change, scs = E_SCHEMA[key]
                dec = dict(cls=SC, sec="", basis=basis, change=change, field=field, srq=[], sc=scs, cur=current)
            else:
                qk = member_to_q.get(key)
                if key in E_DEFAULT_USED:
                    prio = "MEDIUM" if cls_tag in ("IMPORTED_FROM_OTHER_ATTESTATION", "UNSUPPORTED") else "LOW"
                    qk = "YOO_INQUIRY_PLACE"
                    Q[qk]["members"].append(key)
                    assert PRIO_ORDER[Q[qk]["priority"]] <= PRIO_ORDER[prio]
                    default_used.append(f"{aid} {rid} ({cls_tag} → SOURCE {prio}, 기본 규칙)")
                    note = f" DEFAULT_USED: 지침의 Audit E 목록에 없음 → 기본 규칙({cls_tag} → SOURCE_RECHECK_REQUIRED {prio}) 적용. 같은 원문 질문(유제희 탐문 장소)과 묶음."
                else:
                    assert qk, f"Audit E row not covered: {aid} {rid}"
                    note = ""
                prio = E_RUBRIC_PRIO.get(key, Q[qk]["priority"])
                if prio != Q[qk]["priority"]:
                    note += f" 지침 우선순위 {prio}; 같은 원문 질문을 묻는 행과 묶여 큐에서는 {Q[qk]['priority']}."
                scs = ["SC-05"] + E_EXTRA_SC.get(qk, [])
                basis = (f"[{cls_tag}] 값의 근거가 해당 attestation({at[eid]['attestation_id']}) 명제에 없음. "
                         f"현재 CSV에 근거가 없다는 것이 역사적으로 틀렸다는 뜻은 아니므로 값은 유지하고 원문 재확인(우선순위 {prio}). "
                         f"근거 없는 값을 삭제 없이 유지하려면 field_provenance(SC-05) 필요." + note)
                change = "현 값 유지(삭제 제안 없음). 원문 재확인 결과에 따라 근거 표시 또는 값 정렬. 그 전까지 provenance_class를 field_provenance에 기록."
                dec = dict(cls=SR, sec=SC, basis=basis, change=change, field=field, srq=[qk], sc=scs, cur=current)
        elif sec_letter == "F":
            r = rels[rid]
            current = f"{r['relation_type']} | {r['basis_or_rationale']}"
            if rid in F_INTERNAL:
                new, basis, sec, srq, scs, extra = F_INTERNAL[rid]
                change = (f"basis_or_rationale '{r['basis_or_rationale']}' → '{new}'. relation 유지(삭제·병합 없음), 새 단어·사실 추가 없음."
                          f" 기존 basis는 note에 보존.{extra}")
                dec = dict(cls=IF, sec=sec, basis=basis, change=change, field="basis_or_rationale", srq=srq, sc=scs, cur=current)
            else:
                assert rid in F_SOURCE, f"Audit F row not covered: {aid} {rid}"
                qk, sec, hedge, basis = F_SOURCE[rid]
                qks = qk if isinstance(qk, list) else [qk]
                if sec == IF:
                    change = (f"현 relation·basis 유지(삭제·병합 없음). 원문 재확인 전 임시안(보조 INTERNAL): basis_or_rationale '{r['basis_or_rationale']}' → '{hedge}'. "
                              "원문 확인 후 확정 문구로 교체. 기존 basis는 note에 보존.")
                    scs = []
                elif sec == SC:
                    change = "현 relation·basis 유지(삭제·병합 없음). 원문에 순서 표지가 있으면 order_basis=EXPLICIT_MARKER, 없으면 NARRATIVE_ORDER로 기록(SC-07)."
                    scs = ["SC-07"]
                else:
                    change = "현 relation·basis 유지(삭제·병합 없음). 원문 확인 결과에 따라 relation_type 표시 여부 결정."
                    scs = []
                dec = dict(cls=SR, sec=sec, basis=basis, change=change, field="relation_type;basis_or_rationale",
                           srq=qks, sc=scs, cur=current)
        else:
            dkey = (sec_letter, rid)
            assert dkey in D, f"row not covered: {aid} {rid}"
            dec = dict(D[dkey])
            if dec["cur"] is None:
                if sec_letter == "D" and rid == "audit_04_person_set_membership":
                    persons = [p for p in membership if not p["person"].startswith("[")]
                    unknown = sum(1 for p in persons for k, v in p.items() if k.endswith("_value") and v == "UNKNOWN")
                    n_sets = sum(1 for k in membership[0] if k.endswith("_value"))
                    assert f"인물 {len(persons)}명 × 집합 {n_sets}개 중 UNKNOWN {unknown}칸" in m["finding"], m["finding"]
                    dec["cur"] = f"UNKNOWN {unknown}칸 / 인물 {len(persons)}명 × 집합 {n_sets}개 (audit_04_person_set_membership)"
                else:
                    dec["cur"] = cur_val(rid, dec["field"])
            if "DEFAULT_USED" in dec["basis"]:
                default_used.append(f"{aid} {rid} (지침 목록 밖 → 같은 행 Audit A 판단 준용)")
        assert dec["cls"] in CLASSES and dec["sec"] in CLASSES | {""} and dec["sec"] != dec["cls"], aid
        rows.append(dict(
            repair_issue_id=f"RC-{i:03d}", audit_id=aid, audit_type=m["audit_type"], record_type=m["record_type"],
            record_id=rid, field_name=dec["field"], audit_severity=m["severity"], repair_class=dec["cls"],
            secondary_class=dec["sec"], decision_basis=dec["basis"], current_value=dec["cur"],
            proposed_change=dec["change"].replace(FAMILY_NOTE, family_note), _srq=dec["srq"], _sc=dec["sc"],
            requires_user_approval="NO" if m["severity"] == "INFO" else "YES"))

    # ---------- queue ----------
    used_q = OrderedDict()
    for r in rows:
        if SR in (r["repair_class"], r["secondary_class"]):
            assert r["_srq"], r["audit_id"]
        else:
            assert not r["_srq"], r["audit_id"]
        for k in r["_srq"]:
            assert k in Q, k
            used_q.setdefault(k, []).append(r["repair_issue_id"])
    unused = [k for k in Q if k not in used_q]
    assert not unused, f"unused queue keys {unused}"
    order = sorted(Q, key=lambda k: (PRIO_ORDER[Q[k]["priority"]], list(Q).index(k)))
    qid = {k: f"SRQ-{n:03d}" for n, k in enumerate(order, 1)}
    queue = []
    for k in order:
        v = Q[k]
        events, fields = [], []
        for eid, f in v["members"]:
            if eid not in events:
                events.append(eid)
            if f not in fields:
                fields.append(f)
        rel_labels = [f"{r} ({rels[r]['from_event_id']}→{rels[r]['to_event_id']})" for r in v["rels"]]
        att_events = list(events)
        for r in v["rels"]:
            for e2 in (rels[r]["from_event_id"], rels[r]["to_event_id"]):
                if e2 not in att_events:
                    att_events.append(e2)
        if v["rels"] and not v["members"]:
            event_id = ";".join(rel_labels)
        elif v["rels"]:
            endpoints = {e2 for r in v["rels"] for e2 in (rels[r]["from_event_id"], rels[r]["to_event_id"])}
            event_id = ";".join(rel_labels + [e2 for e2 in events if e2 not in endpoints])
        else:
            event_id = ";".join(events)
        if v["current"]:
            current = v["current"]
        else:
            parts = [f"{r}: {rels[r]['relation_type']} | {rels[r]['basis_or_rationale']}" for r in v["rels"]]
            vals = [ev[e][f] for e, f in v["members"]]
            if v["members"] and len(set(vals)) == 1 and not v["rels"]:
                parts.append(vals[0])
            else:
                parts += [f"{e}.{f}='{ev[e][f]}'" for e, f in v["members"]]
            current = " / ".join(parts)
        srcs = []
        for e2 in att_events:
            s = at[e2]["source_record_id"]
            if s not in srcs:
                srcs.append(s)
        queue.append(dict(
            issue_id=qid[k], event_id=event_id,
            attestation_id=";".join(at[e2]["attestation_id"] for e2 in att_events),
            field_name=v["field"] or (";".join(fields) if fields else "relation_type;basis_or_rationale"),
            current_value=current,
            current_attestation_text=" || ".join(f"{at[e2]['attestation_id']}: {at[e2]['proposition_ko']}" for e2 in att_events),
            problem=v["problem"], what_must_be_checked_in_source=v["check"],
            source_record_id=";".join(srcs),
            source_url_metadata=";".join(src[s]["source_url"] for s in srcs),
            priority=v["priority"], related_repair_issue_ids=";".join(used_q[k])))
    for r in rows:
        r["source_recheck_ref"] = ";".join(qid[k] for k in r["_srq"])

    # ---------- schema proposals ----------
    sc_refs = Counter()
    sc_samples = {}
    for r in rows:
        if SC in (r["repair_class"], r["secondary_class"]) or r["_sc"]:
            if SC in (r["repair_class"], r["secondary_class"]):
                assert r["_sc"], r["audit_id"]
        for s in r["_sc"]:
            sc_refs[s] += 1
            sc_samples.setdefault(s, [])
            if r["record_id"] not in sc_samples[s]:
                sc_samples[s].append(r["record_id"])
        r["schema_proposal_ref"] = ";".join(r["_sc"])
    e_cls = Counter(r["classification"] for r in audit_e)
    proposals = schema_proposals(e_cls, len(audit_e))
    assert [p["proposal_id"] for p in proposals] == ["SC-05", "SC-02", "SC-03", "SC-01", "SC-07", "SC-04", "SC-06", "SC-09", "SC-08"]
    assert set(sc_refs) <= {p["proposal_id"] for p in proposals}
    for p in proposals:
        p["affected_issue_count"] = sc_refs.get(p["proposal_id"], 0)
        p["affected_records_sample"] = ";".join(sc_samples.get(p["proposal_id"], [])[:10])
        assert p["affected_issue_count"] > 0, p["proposal_id"]

    # ---------- checks ----------
    no_delete = re.compile(r"삭제(?!\s*(없음|하지|제안 없음|·병합 없음|·병합 금지|금지|아님))")
    for r in rows:
        assert not no_delete.search(r["proposed_change"]), (r["audit_id"], r["proposed_change"])
        if r["repair_class"] == IF:
            assert r["proposed_change"], r["audit_id"]
    assert {r["audit_id"] for r in rows} == {m["audit_id"] for m in master} and len(rows) == 303

    cols = ["repair_issue_id", "audit_id", "audit_type", "record_type", "record_id", "field_name", "audit_severity",
            "repair_class", "secondary_class", "decision_basis", "current_value", "proposed_change",
            "source_recheck_ref", "schema_proposal_ref", "requires_user_approval"]
    write("repair_classification.csv", cols, [{c: r[c] for c in cols} for r in rows])
    write("source_recheck_queue.csv", ["issue_id", "event_id", "attestation_id", "field_name", "current_value",
                                       "current_attestation_text", "problem", "what_must_be_checked_in_source",
                                       "source_record_id", "source_url_metadata", "priority",
                                       "related_repair_issue_ids"], queue)
    write("schema_change_proposals.csv", ["proposal_id", "priority_rank", "title", "problem", "affected_issue_count",
                                          "affected_records_sample", "current_limitation", "proposed_model",
                                          "migration_notes", "risks", "depends_on"], proposals)

    after = {f: sha(RAW / f) for f in FILES.values()}
    for f in FILES.values():
        log.info("sha256 after  %s %s %s", f, after[f], "UNCHANGED" if after[f] == before[f] else "CHANGED")
    assert after == before, "raw CSV changed"

    log.info("rows %d (audit_master_summary 1:1)", len(rows))
    log.info("primary class %s", dict(Counter(r["repair_class"] for r in rows)))
    log.info("secondary class %s", dict(Counter(r["secondary_class"] or "(none)" for r in rows)))
    log.info("primary x section %s", dict(Counter((r["audit_id"][0], r["repair_class"]) for r in rows)))
    log.info("primary or secondary SOURCE rows %d", sum(1 for r in rows if SR in (r["repair_class"], r["secondary_class"])))
    log.info("queue rows %d by priority %s", len(queue), dict(Counter(q_["priority"] for q_ in queue)))
    log.info("schema refs %s", {p["proposal_id"]: p["affected_issue_count"] for p in proposals})
    log.info("requires_user_approval %s", dict(Counter(r["requires_user_approval"] for r in rows)))
    for x in default_used:
        log.info("DEFAULT_USED %s", x)
    log.info("note: E-066 AT0074.actor not in the Audit E rubric list; resolved consistently with C-005 (INTERNAL keep-as-is placeholder)")


def schema_proposals(e_cls, e_total):
    seed = ", ".join(f"{k} {v}" for k, v in sorted(e_cls.items()))
    P = [
        dict(proposal_id="SC-05", title="필드 수준 출처(field_provenance) 테이블",
             problem="events의 각 필드 값이 어느 attestation/relation에서 왔는지 표현할 곳이 없어, 근거 없는·옮겨온 값을 삭제 없이 '근거 미확인'으로 유지할 수 없음.",
             current_limitation="provenance는 행(event) 단위 attestation 1건뿐. 필드 값이 다른 attestation·relation·계산에서 왔는지 구별 불가. attestations.event_id 1:1이라 한 attestation이 분할된 두 event를 지지하는 구조(AT0012 분할안)도 표현 불가.",
             proposed_model="field_provenance(event_id, field_name, value, provenance_class[DIRECTLY_SUPPORTED/DERIVED_FROM_LINKED_STRUCTURE/IMPORTED_FROM_OTHER_ATTESTATION/UNSUPPORTED/AMBIGUOUS], evidence_attestation_ids, evidence_relation_ids, derivation_rule, source_recheck_ref)",
             migration_notes=f"output/audit_05_field_level_provenance.csv({e_total}행: {seed})를 그대로 초기 적재. source_recheck_ref에 source_recheck_queue의 SRQ id 연결. 원문 재확인 결과는 provenance_class 갱신으로만 반영(값 삭제 없음).",
             risks="필드 값 변경 시 provenance 행 동기화 누락 위험. provenance_class를 사실 판정으로 오독할 위험(UNSUPPORTED ≠ 틀림).",
             depends_on=""),
        dict(proposal_id="SC-02", title="과거 사건과 나중의 회고·메타 진술 분리",
             problem="경위 설명·부인 등 나중 진술 행위와 그 진술이 가리키는 과거(주장된) 사건이 한 행에 섞여 시간·장소·relation이 어느 층에 속하는지 불명.",
             current_limitation="statement 행과 described 사건을 잇는 명시적 연결이 없어 REL0032(DURING) 같은 관계가 진술 행에 붙음. 시간·장소 필드가 한 벌뿐.",
             proposed_model="진술 사건(statement event)과 그것이 서술하는 alleged 과거 사건을 별도 행으로 두고 statement_links(statement_event_id, described_event_id, link_type[DESCRIBES/REFERS_TO/DENIES], attestation_id)로 연결. 시간·장소 필드는 각 층에 따로 기록(진술 층: report_lunar_date 이하).",
             migration_notes="대상: AT0119, AT0078–AT0080, AT0131, AT0132 및 REL0032. repair_classification의 B-016·B-006–B-008·B-017 분할안을 승인 후 적재. REL0032 to_event는 과거 사건 행으로 이동(관계 삭제 없음).",
             risks="alleged 과거 사건 행이 사실로 오독될 위험 → SC-03 claim_status와 함께 도입해야 함. 부인 대상 행(AT0131)은 특히 주의.",
             depends_on="SC-05;SC-03"),
        dict(proposal_id="SC-03", title="event 수준 주장·인식 상태(claim/epistemic status)",
             problem="CLAIM_CONTESTED 행에서 '주장됨'이 events 테이블 안의 유일한 미확정 표지라 action 문자열에서 뺄 수 없음.",
             current_limitation="epistemic_scope는 출처 범위만 표시하고 행 자체의 다툼·부인·인정 상태를 표현하지 못함. 상태가 attestation(embedded_claim_status)에만 있음.",
             proposed_model="events.claim_status[ASSERTED/CONTESTED/DENIED/ADMITTED/OFFICIALLY_FOUND/LATER_REVISED] + claim_status_basis(attestation_ids). action에는 행위만 기록.",
             migration_notes="대상: AT0114–AT0117(CONTESTED 자미덕 주장), 분할안의 alleged 과거 사건 행(AT0119·AT0131 계열). 도입 후 A-021–A-024의 보조 INTERNAL 값(매일 불러들임/말함/회유/떡·밥을 줌) 적용.",
             risks="claim_status를 하나로 단정하면 다수 화자 충돌(REL0078–REL0081)이 사라질 위험 → 화자별 attestation은 그대로 두고 status는 요약으로만 사용.",
             depends_on="SC-05"),
        dict(proposal_id="SC-01", title="발생 시간·진술 시간·관찰 시간 분리(상태 시작/관찰, 시점 없는 동일성, 반복 계열)",
             problem="occurrence_lunar_* 한 벌에 사건 발생 시점, 진술·보고 시점, 관찰 시점이 섞임. 상태 시작과 관찰, 시점 없는 동일성 진술, 반복 계열을 구분할 수 없음.",
             current_limitation="time_precision 코드(UNDATED_STATE, REPEATED_AFTER_ARREST 등)로만 일부 암시. 인물 식별에 체포 지시 날짜가 붙는 등 과잉 주장 발생.",
             proposed_model="time_layers(event_id, layer[OCCURRENCE/STATEMENT/OBSERVATION/STATE_ONSET], lunar_start, lunar_end, precision, basis) + events.temporal_kind[POINT/STATE/TIMELESS_IDENTITY/REPEATED_SERIES] + series 정보(반복 표지 원문).",
             migration_notes="대상: AT0091, AT0099, AT0100, AT0114, AT0132, REL0022 및 기록일이 행위 시점처럼 쓰인 AT0017–AT0019. 현 값은 OCCURRENCE 층으로 옮기되 provenance(SC-05) 유지.",
             risks="층을 나누는 과정에서 없는 시점을 채워 넣을 위험 → 근거 없는 층은 비워 둠.",
             depends_on="SC-02"),
        dict(proposal_id="SC-07", title="relation 출처와 순서 근거(order_basis), 후보/확정 상태",
             problem="BEFORE 등 순서 relation의 근거가 명시 표지인지 서술 순서인지 구별되지 않고, 후보 coreference 연결을 통해 날짜 같은 필드 값이 전파됨.",
             current_limitation="confidence와 basis 문장뿐. relation_type이 CANDIDATE여도 하류 계산에서 확정처럼 쓰임(REL0077 → 자미덕 진술 행 8개의 날짜).",
             proposed_model="event_relations.order_basis[EXPLICIT_MARKER/TYPE_ENTAILED/NARRATIVE_ORDER/DATE_COMPARISON] + link_status[CANDIDATE/CONFIRMED] + evidence_attestation_ids. 규칙: CANDIDATE coreference 연결은 날짜 등 필드 값을 전파하지 않음.",
             migration_notes="서술 순서 relation(REL0003·REL0007·REL0008·REL0014–REL0018·REL0023·REL0029·REL0041)은 원문 재확인 전 NARRATIVE_ORDER로 표시. REL0066–REL0071은 DATE_COMPARISON. REL0072–REL0091은 CANDIDATE.",
             risks="NARRATIVE_ORDER를 일괄 낮추면 실제 명시 표지가 있는 관계까지 약해짐 → 원문 재확인 결과로 개별 갱신.",
             depends_on="SC-05"),
        dict(proposal_id="SC-04", title="actor와 participant 분리 + 인물 엔티티·별칭 테이블",
             problem="복수 참여자·집단·인물+기관이 actor 문자열 하나에 저장되고, 같은 인물의 다른 표기(별칭)를 동일시할지 표현할 곳이 없음.",
             current_limitation="actor는 자유 문자열('·', '/', '등' 혼용). 인물 동일성은 relation basis 문장에만 암묵적으로 존재(REL0082).",
             proposed_model="event_participants(event_id, participant, role, role_basis, provenance) + persons(person_id, canonical_label) + person_aliases(alias, person_id, identity_status[CONFIRMED/CANDIDATE], evidence_attestation_ids, source_recheck_ref).",
             migration_notes="대상: AT0012, AT0069, AT0072, AT0077, AT0118(안 A 채택 안 함), AT0089·AT0090·AT0092–AT0094 집단 표기, AT0121, 별칭 5건(병영 보조자/한재욱, 재돌/변재돌, 원돌/정원돌, 풍각 김생원 계열, 병사/이광섭). 별칭은 원문 재확인 전 모두 CANDIDATE.",
             risks="정규화 과정에서 집단 표기를 통일하면 근거 없는 동일시가 생김 → CANDIDATE로만 연결.",
             depends_on="SC-05"),
        dict(proposal_id="SC-06", title="열린 집합 소속 상태 표현(open-set membership)",
             problem="'여러 사람', '등', '특정 인물들', '관련 대상'처럼 열린 표현으로 기록된 집합의 구성원 여부를 표현할 곳이 없어 UNKNOWN 칸을 추론으로 채우거나 이름 목록을 확정처럼 쓰게 됨.",
             current_limitation="명단은 target_or_content 문자열(AT0122)에만 있고, 집합이 닫혀 있는지 열려 있는지 표시 불가.",
             proposed_model="sets(set_id, label, closure_status[OPEN/CLOSED], open_marker_text, evidence_attestation_ids) + set_membership(set_id, person_id, status[DIRECT/ABSENT/UNKNOWN], evidence). 이는 소속 상태를 기록하는 표현일 뿐이며 UNKNOWN 인터페이스나 추론 기능이 아님(UNKNOWN은 '기록 없음'을 그대로 보존).",
             migration_notes="output/audit_04_person_set_membership.csv(인물×집합 표)를 초기 적재. AT0122 명단은 원문 재확인 전 EVENT_FIELD_ONLY 근거로 표시. AT0116 '특정 인물들', AT0074 '관련 대상'은 OPEN 표지로 기록.",
             risks="ABSENT와 UNKNOWN 혼동 위험(열린 명단에 없다고 ABSENT로 쓰면 안 됨).",
             depends_on="SC-04"),
        dict(proposal_id="SC-09", title="장소 역할 구분(발생 장소·목적지·행위자 소속)",
             problem="historical_place 한 칸에 발생 장소, 유배 목적지, 행위자 기관(소속)이 섞임.",
             current_limitation="AT0161·AT0168·AT0170은 목적지, AT0006·AT0008·AT0097·AT0098은 행위자 기관이 장소로 들어감. '원도'처럼 지명이 아닌 범주어도 구분 불가.",
             proposed_model="event_places(event_id, place, place_role[OCCURRENCE/DESTINATION/ACTOR_AFFILIATION/ORIGIN], place_kind[TOPONYM/CATEGORY], provenance).",
             migration_notes="현 historical_place 값은 OCCURRENCE로 옮기고, 목적지·소속으로 판명된 행만 역할 변경. 값 삭제 없음.",
             risks="역할 판정 자체가 해석이 될 수 있음 → 명제에 표지가 있는 경우만 변경.",
             depends_on="SC-05"),
        dict(proposal_id="SC-08", title="conflict_group 의미 구분(직접 다툼 vs 맥락상 묶음)",
             problem="conflict_group이 '해당 행이 직접 다투어지는 주장을 담음'인지 '같은 쟁점 맥락으로 묶음'인지 정의가 없어 COACHING 같은 값의 근거 판정이 불가.",
             current_limitation="AT0114·AT0115·AT0117·AT0125·AT0126은 사주를 직접 주장하지 않는데 COACHING에 묶임.",
             proposed_model="conflict_membership(event_id, conflict_group, membership_type[DIRECT_CLAIM/CONTEXTUAL], basis_attestation_ids, basis_relation_ids).",
             migration_notes="현 claim_topic/conflict_group 값은 유지하고 membership_type만 추가. COACHING 5행은 원래 판정(CONTEXTUAL 후보)을 사용자 승인 후 기록.",
             risks="CONTEXTUAL로 낮춘 행이 쟁점 분석에서 빠질 위험 → 필터 기본값은 둘 다 포함.",
             depends_on="SC-03"),
    ]
    for n, p in enumerate(P, 1):
        p["priority_rank"] = n
    return P


if __name__ == "__main__":
    main()
