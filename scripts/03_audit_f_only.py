#!/usr/bin/env python3
"""Stage 3: F-only transfer audit (report only, no data changes).

Checks whether information from the attestations was carried into
events / attestations / event_relations without
  1. mixing different layers in one row,
  2. losing information,
  3. strengthening meaning,
  4. misplacing actor / target / time / place.

Evidence is limited to the 5 raw CSVs. source_url is treated as a string only.
No web access, no external knowledge, no new events, no merges, no new relations,
no episode / UNKNOWN-interface / causal / SMC work. Raw CSVs are never written.

Judgments below were made by reading every row; each override carries its reason.
Default classifications apply only where a row was read and nothing was found.
"""

import csv
import hashlib
import logging
import re
import sys
from collections import Counter, defaultdict
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

log = logging.getLogger("audit")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(name):
    with (RAW / FILES[name]).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write(name, cols, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    log.info("wrote output/%s (%d rows)", name, len(rows))


# =====================================================================
# AUDIT A: event / attestation separation
# =====================================================================
MARKER_RE = re.compile(r"(보고됨|주장됨|전해짐|했다고 함|라고 함|되었다고|라고 보고)")
TESTIMONY_ACT_IN_STATE = {"AT0063", "AT0064"}  # action '...진술' on a STATE row
A_OVERRIDES = {
    "AT0004": ("AMBIGUOUS", "REPORT_LAYER_DUPLICATE",
               "이형원의 '장계' 행위를 event로 만들었고, 같은 장계 문장의 하위 내용(구순의 김명신 괴수 발언)은 AT0005로 별도 event화됨. ATT0004와 ATT0005의 명제가 사실상 동일(같은 SRC001 문장)이라 같은 정보가 보고층·사건층 두 event로 이중 기록됨."),
    "AT0119": ("AMBIGUOUS", "META_TESTIMONY_WITH_PAST_ANCHOR",
               "family/action은 나중의 진술 행위(경위 설명=attestation 층)를 가리키지만 REL0032(DURING)·장소·시점은 과거 대질 중 발화를 가리킴. 한 행이 attestation 층 행위와 과거 사건 층을 동시에 대표함."),
}
CONTESTED_NOTE = ("단, 이 행은 CLAIM_CONTESTED라서 '주장됨'이 events 테이블 안에서 유일한 미확정 표지임. "
                  "상태 표시 수단(예: 별도 status 컬럼) 없이 표지만 제거하면 확정 사실처럼 읽힐 위험.")


def audit_a(ev, at):
    rows = []
    for e in ev:
        k = e["event_id"]
        a = at[k]
        marker = ";".join(sorted(set(MARKER_RE.findall(e["action"]))))
        tgt_marker = ";".join(sorted(set(MARKER_RE.findall(e["target_or_content"]))))
        self_att = e["actor"] == a["speaker_or_reporting_actor"]
        sev, direction = "INFO", "변경 불필요"
        if k in A_OVERRIDES:
            cls, pattern, finding = A_OVERRIDES[k]
            sev = "MEDIUM_REVIEW" if k == "AT0004" else "HIGH_REVIEW"
            direction = ("AT0004: 보고 행위 자체를 별도 사건으로 유지할지, AT0005와 함께 하나의 사건(구순의 발언)+하나의 attestation(이형원 장계)로 볼지 사용자 결정"
                         if k == "AT0004" else
                         "과거 사건(대질 중 거짓 진술, 주장됨)과 나중 진술(경위 설명)을 구분하는 방향 검토. 자동 분리 금지.")
        elif marker:
            cls, pattern = "EVENT_AND_ATTESTATION_MIXED", "REPORTING_MARKER_IN_ACTION"
            finding = (f"action '{e['action']}'에 보고/전언 표지({marker})가 들어 있음. "
                       f"보고·전언 경로는 이미 {a['attestation_id']}(speaker={a['speaker_or_reporting_actor']}, "
                       f"mode={a['attestation_mode']}, embedded={a['embedded_claim_status']})에 기록되어 있어 같은 정보가 두 층에 중복됨.")
            if k == "AT0008":
                finding += " 또한 family=EF_ACT_RECORD_REPORT로 '조사' 행위가 기록·보고 family에 분류됨."
            if k == "AT0010":
                finding += " 또한 family=EF_ACT_RECORD_REPORT(기존 EF_ACT_DEATH 미사용)."
            if k == "AT0012":
                finding += " 보고자(이형원)가 actor에도 포함된 자기 보고 행."
            direction = "action에서 보고/전언 표지를 빼고 행위만 남기는 방향 검토(보고 정보는 attestation에 이미 있음)."
            sev = "MEDIUM_REVIEW"
            if a["embedded_claim_status"] == "CLAIM_CONTESTED":
                finding += " " + CONTESTED_NOTE
                direction += " 단 contested 행은 상태 표시 수단을 먼저 마련한 뒤에만."
        elif k in TESTIMONY_ACT_IN_STATE:
            cls, pattern = "EVENT_AND_ATTESTATION_MIXED", "TESTIMONY_ACT_IN_STATE_ACTION"
            finding = (f"STATE family 행인데 action '{e['action']}'이 진술 행위(attestation 층)를 이름으로 씀. "
                       "상태(신분/거주)와 그 상태를 진술한 행위가 한 행에 섞임.")
            direction = "action을 상태 서술로 두고 '진술'은 attestation(TESTIMONY)에 맡기는 방향 검토."
            sev = "LOW_REVIEW"
        else:
            cls = "CLEAN_EVENT"
            pattern = "SELF_ATTESTED_SPEECH_OR_OFFICIAL_ACT" if self_att else "NONE"
            finding = ("actor=attestation speaker인 발화·판단·명령 행. 사건이 곧 기록된 발화 행위이므로 층 혼합 아님."
                       if self_att else "행위와 보고 경로가 분리되어 있음.")
            if tgt_marker:
                finding += f" target에 '{tgt_marker}' 표현이 있으나 발화 내용 자체(화자 본인의 말)라 혼합 아님."
        rows.append({
            "event_id": k, "attestation_id": a["attestation_id"], "actor": e["actor"],
            "action": e["action"], "target_or_content": e["target_or_content"],
            "event_family_id": e["event_family_id"],
            "speaker_or_reporting_actor": a["speaker_or_reporting_actor"],
            "attestation_mode": a["attestation_mode"],
            "embedded_claim_status": a["embedded_claim_status"],
            "proposition_ko": a["proposition_ko"],
            "detected_marker": marker, "pattern": pattern, "classification": cls,
            "finding": finding, "suggested_direction_no_auto_fix": direction, "severity": sev,
        })
    return rows


# =====================================================================
# AUDIT B: atomicity / temporal layers
# =====================================================================
B_OVERRIDES = {
    "AT0119": ("BOTH", "HIGH_REVIEW",
               "과거 층: 대질 중 자미덕의 발화(+한재욱의 지휘라는 별개 주장 행위). 나중 층: 자미덕이 안핵 공초(SRC004, 1793-06-13 보고)에서 그것을 설명한 행위. "
               "family=EF_SPEECH_TESTIMONY_META·action='과거 진술 경위 설명'은 나중 층, historical_place=병영·time_precision=UNDATED_DURING_DETENTION·REL0032(AT0118→AT0119 DURING)는 과거 층. "
               "target에는 한재욱의 지휘(다른 행위자의 행위)까지 들어 있어 사건도 둘 이상."),
    "AT0078": ("MULTIPLE_TIME_LAYERS_IN_ONE_ROW", "MEDIUM_REVIEW",
               "action='과거 진술 경위 설명'(안핵 공초 시점의 설명 행위)인데 place=충청병영·time=UNDATED_DURING_INVESTIGATION은 설명 대상인 과거 병영 공초를 가리킴."),
    "AT0079": ("MULTIPLE_TIME_LAYERS_IN_ONE_ROW", "MEDIUM_REVIEW",
               "action='진술 경위 설명'(나중)인데 place/time은 과거 병영 조사 시점. 과거의 '위협을 두려워함' 상태와 나중의 설명 행위가 섞임."),
    "AT0080": ("MULTIPLE_TIME_LAYERS_IN_ONE_ROW", "MEDIUM_REVIEW",
               "action='과거 진술 변경 설명'(나중)인데 place/time은 과거 병영 조사 시점. 과거 진술 변경과 나중 설명이 섞임."),
    "AT0131": ("MULTIPLE_TIME_LAYERS_IN_ONE_ROW", "MEDIUM_REVIEW",
               "action='부인'은 한재욱의 안핵 공초 시점 발화인데 place=비장청·time=UNDATED_DURING_DETENTION은 부인 대상(주장된 사주)의 과거 시점·장소."),
    "AT0132": ("MULTIPLE_TIME_LAYERS_IN_ONE_ROW", "LOW_REVIEW",
               "action='부인'(공초 시점 발화)인데 time_precision=UNDATED_STATE는 부인 내용(관계 상태)의 시간 성격."),
    "AT0063": ("MULTIPLE_TIME_LAYERS_IN_ONE_ROW", "LOW_REVIEW",
               "family=STATE_IDENTITY·UNDATED_STATE(상태)인데 action='신분 진술'(공초 시점의 진술 행위)."),
    "AT0064": ("MULTIPLE_TIME_LAYERS_IN_ONE_ROW", "LOW_REVIEW",
               "family=STATE_RESIDENCE·UNDATED_STATE(상태)인데 action='거주 상태 진술'(공초 시점의 진술 행위)."),
    "AT0012": ("MULTIPLE_EVENTS_IN_ONE_ROW", "MEDIUM_REVIEW",
               "ATT0012 '이형원은 각 진영의 영장들에게 함께 조사하게 했다' = 이형원의 지시 + 영장들의 조사 수행. actor '이형원/각 진영 영장'과 action '회동 조사 실시'가 지시자와 수행자를 한 사건으로 합침."),
    "AT0068": ("MULTIPLE_EVENTS_IN_ONE_ROW", "MEDIUM_REVIEW",
               "나복의 한 발화에 도적 수(30여 명)·횃불·'지세대감' 자칭·금품 절취 네 명제가 묶임. 이 중 '지세' 호칭은 다른 행(AT0096 등)에서 별도 쟁점(JISE_ORIGIN)인데 이 행은 claim_topic=THEFT_DESCRIPTION 하나만 가짐."),
    "AT0043": ("MULTIPLE_EVENTS_IN_ONE_ROW", "LOW_REVIEW",
               "'김명신이 죽은 뒤 그의 아내도 사망' = 두 사망과 그 순서가 한 주장에 묶임. 아내 사망은 별도 event 없음."),
    "AT0153": ("MULTIPLE_EVENTS_IN_ONE_ROW", "LOW_REVIEW",
               "'곤장을 받지 않음'과 '평범한 신문을 받지 않음' 두 판단 명제가 한 행. (AT0151/AT0152는 같은 판결문에서 인물별로 분리된 것과 대조)"),
    "AT0154": ("MULTIPLE_EVENTS_IN_ONE_ROW", "MEDIUM_REVIEW",
               "ATT0154는 '김명신 부처의 죽음'(두 사람)에 대한 판단인데 한 행. AT0151/AT0152는 인물별로 분리됨. 게다가 target에서는 대상('김명신 부처')이 빠짐."),
    "AT0091": ("MULTIPLE_TIME_LAYERS_IN_ONE_ROW", "LOW_REVIEW",
               "'이미 공주진에 붙잡혀 있었다'는 2/29 이전에 시작된 상태인데 occurrence=1793-02-29 DAY는 이진욱이 그것을 확인한 시점. 상태 시작 시점과 관찰 시점이 한 행에 섞임(REL0022 참조)."),
    "AT0099": ("AMBIGUOUS", "LOW_REVIEW",
               "인물 식별(풍각 김생원=김명신)은 시점 없는 진술 내용인데 1793-03-04 DAY가 붙음(체포 지시 날짜가 옮겨옴)."),
    "AT0100": ("AMBIGUOUS", "LOW_REVIEW",
               "인물 식별(흥덕 김생원=김갑득)에 체포 지시 날짜 1793-03-04 DAY가 붙음."),
    "AT0114": ("AMBIGUOUS", "LOW_REVIEW",
               "'매일 불러들였다' = 반복 사건 계열을 한 행으로 표현(REPEATED_AFTER_ARREST). 횟수·개별 발생은 구분 불가."),
    "AT0115": ("AMBIGUOUS", "LOW_REVIEW",
               "time_precision=REPEATED_AFTER_ARREST이지만 ATT0115에는 반복 표현이 없음(AT0114의 '매일'이 옮겨온 것으로 보임)."),
    "AT0116": ("AMBIGUOUS", "MEDIUM_REVIEW",
               "time_precision=REPEATED_AFTER_ARREST이지만 ATT0116에는 반복 표현이 없음. 회유가 1회인지 반복인지 원문 명제로 확인 불가."),
    "AT0117": ("AMBIGUOUS", "LOW_REVIEW",
               "time_precision=REPEATED_AFTER_ARREST이지만 ATT0117에는 반복 표현이 없음."),
    "AT0161": ("AMBIGUOUS", "LOW_REVIEW",
               "처분 결정(1793-06-13 기사)과 유배지(신지도)를 한 행에 둠. historical_place가 결정 장소가 아닌 목적지를 뜻해 AT0160(place=한양)과 의미가 다름."),
    "AT0168": ("AMBIGUOUS", "LOW_REVIEW",
               "처분 결정 시점과 유배지(영동현)가 한 행. place 의미가 결정 장소가 아닌 목적지."),
    "AT0170": ("AMBIGUOUS", "LOW_REVIEW",
               "place='원도'는 '먼 섬'의 범주어로 지명이 아니며 목적지 의미."),
}
B_NOTES = {
    "AT0004": "같은 SRC001 문장이 AT0004(보고층)와 AT0005(발언층) 두 행으로 기록됨(한 사건의 이중 기록; Audit A 참조).",
    "AT0005": "AT0004와 같은 명제의 이중 기록.",
    "AT0139": "AT0140과 사실상 같은 명제('약간의 도난은 실제' vs '실제 도난이 있었다')가 두 행에 있음.",
    "AT0140": "AT0139와 사실상 중복.",
    "AT0026": "notes에 1793-06-13 최종 안핵의 수정 내용(나중 시점 정보)이 들어 있음(필드 외 메모).",
    "AT0033": "notes에 1793-06-13 안핵의 수정 내용(나중 시점 정보)이 들어 있음.",
    "AT0010": "보고 층 혼합은 Audit A에서 다룸.",
    "AT0092": "ATT0092의 '변지돌 대신'·'만을' 정보가 event 필드에 없음(정보 누락).",
}


def audit_b(ev, at, rel_by_event):
    rows = []
    for e in ev:
        k = e["event_id"]
        a = at[k]
        cls, sev, finding = B_OVERRIDES.get(k, ("ATOMIC", "INFO", "단일 사건·단일 시간층으로 판단."))
        rows.append({
            "event_id": k, "event_family_id": e["event_family_id"], "actor": e["actor"],
            "action": e["action"], "target_or_content": e["target_or_content"],
            "historical_place": e["historical_place"],
            "occurrence_lunar_start": e["occurrence_lunar_start"],
            "occurrence_lunar_end": e["occurrence_lunar_end"],
            "time_precision": e["time_precision"],
            "atomicity_status": e["atomicity_status"], "parent_fact_id": e["parent_fact_id"],
            "report_lunar_date": a["report_lunar_date"], "proposition_ko": a["proposition_ko"],
            "linked_relations": ";".join(rel_by_event.get(k, [])),
            "classification": cls, "finding": finding, "note": B_NOTES.get(k, ""), "severity": sev,
        })
    return rows


# =====================================================================
# AUDIT C: actor / participant structure
# =====================================================================
C_TABLE = {
    # event_id: (classification, actor_kind, components, role_issue, participant_table_needed, severity)
    "AT0012": ("MULTIPLE_PARTICIPANTS_STORED_AS_ONE_ACTOR", "PERSON+GROUP", "이형원 | 각 진영 영장",
               "지시자(이형원)와 수행자(영장들)의 역할이 다른데 한 actor로 저장. '/' 구분자.", "YES", "MEDIUM_REVIEW"),
    "AT0069": ("MULTIPLE_PARTICIPANTS_STORED_AS_ONE_ACTOR", "PERSON+PERSON", "구순 | 김명신",
               "대칭 관계 상태(상호 친숙)를 한 actor 문자열로 저장.", "YES", "LOW_REVIEW"),
    "AT0072": ("MULTIPLE_PARTICIPANTS_STORED_AS_ONE_ACTOR", "PERSON+PERSON", "구순 | 김명신",
               "대칭 관계 상태(왕래 단절)를 한 actor 문자열로 저장.", "YES", "LOW_REVIEW"),
    "AT0077": ("MULTIPLE_PARTICIPANTS_STORED_AS_ONE_ACTOR", "PERSON+ROLE", "구순 | 장교(1명, 이름 없음)",
               "쌍방 대화를 한 actor로 저장. 장교의 신원은 CSV에 없음.", "YES", "LOW_REVIEW"),
    "AT0118": ("MULTIPLE_PARTICIPANTS_STORED_AS_ONE_ACTOR", "PERSON+PERSON", "자미덕 | 이집거",
               "대질은 복수 참여자 사건. ATT0118 '자미덕은 이집거와 대질했다'(공동격 '와')로 방향성 없음. actor 문자열 그룹화 시 자미덕 행 집계에서 빠지고 이집거는 이 복합값으로만 존재. target_or_content는 비어 있음.", "YES", "MEDIUM_REVIEW"),
    "AT0121": ("PERSON_AND_INSTITUTION", "PERSON+INSTITUTION", "한재욱 | 병영",
               "ATT0121에서 '병영'은 유제희의 소속(병영 아전)으로 나올 뿐 행위 주체로 나오지 않음. '/병영'이 추가된 형태.", "YES", "LOW_REVIEW"),
    "AT0075": ("GROUP_ACTOR", "GROUP", "장교 | 나졸", "역할이 다른 두 집단(이름 없음).", "NO", "INFO"),
    "AT0089": ("GROUP_ACTOR", "GROUP(named members + 등)", "이진욱 | 조계완 | 등",
               "이름 있는 구성원+미상 구성원. 같은 집단이 AT0092~AT0094에서는 '병영 장교 일행', AT0101~AT0102에서는 '장교 일행'으로 다르게 표기됨.", "YES", "LOW_REVIEW"),
    "AT0090": ("GROUP_ACTOR", "GROUP(named members + 등)", "이진욱 | 조계완 | 등",
               "AT0089와 같음. 집단 표기 불일치.", "YES", "LOW_REVIEW"),
    "AT0086": ("AMBIGUOUS", "UNSUPPORTED_GROUP", "한재욱 측",
               "ATT0086은 수동형('철편 네 개가 만들어졌다')으로 행위자가 없음. '한재욱 측'은 CSV 근거 없이 행위를 한재욱 쪽에 귀속시킴.", "NO", "HIGH_REVIEW"),
    "AT0087": ("AMBIGUOUS", "UNSUPPORTED_GROUP", "한재욱 측",
               "ATT0087은 수동형('제공됐다'). 행위자 귀속 근거 없음.", "NO", "HIGH_REVIEW"),
    "AT0074": ("AMBIGUOUS", "PLACEHOLDER", "미상 관서", "ATT0074는 수동형('체포령이 내려졌다'). 발령 주체 미상.", "NO", "LOW_REVIEW"),
    "AT0092": ("GROUP_ACTOR", "GROUP", "병영 장교 일행", "ATT0092 주어는 화자 이진욱(암묵). AT0089/AT0090의 '이진욱·조계완 등'과 같은 집단인지 표기상 불명.", "NO", "LOW_REVIEW"),
    "AT0093": ("GROUP_ACTOR", "GROUP", "병영 장교 일행", "AT0092와 같음.", "NO", "LOW_REVIEW"),
    "AT0094": ("GROUP_ACTOR", "GROUP", "병영 장교 일행", "AT0092와 같음.", "NO", "LOW_REVIEW"),
    "AT0101": ("GROUP_ACTOR", "GROUP", "장교 일행", "", "NO", "INFO"),
    "AT0102": ("GROUP_ACTOR", "GROUP", "장교 일행", "", "NO", "INFO"),
    "AT0013": ("GROUP_ACTOR", "GROUP", "회동 조사 응답자들", "", "NO", "INFO"),
    "AT0014": ("GROUP_ACTOR", "GROUP", "회동 조사 응답자들", "", "NO", "INFO"),
    "AT0015": ("GROUP_ACTOR", "GROUP", "회동 조사 응답자들", "", "NO", "INFO"),
    "AT0016": ("GROUP_ACTOR", "GROUP", "회동 조사 응답자들",
               "ATT0016은 '진술이 실려 있다'로 진술자를 밝히지 않음. 응답자들로 귀속한 근거는 같은 보고의 인접 행(AT0013~AT0015)뿐.", "NO", "LOW_REVIEW"),
    "AT0046": ("GROUP_ACTOR", "GROUP", "비변사 당상들", "attestation speaker='정민시 등'.", "NO", "INFO"),
    "AT0047": ("GROUP_ACTOR", "GROUP", "비변사 당상들", "attestation speaker='정민시 등'.", "NO", "INFO"),
    "AT0138": ("GROUP_ACTOR", "GROUP", "탐문 대상자들", "", "NO", "INFO"),
}
INSTITUTIONS = {"충청병영", "병영", "비변사"}
NON_AGENT = {"수사": "PROCESS", "지세 호칭 조사": "PROCESS", "별도 채탐": "PROCESS", "구순 집": "PLACE"}


def audit_c(ev):
    rows = []
    for e in ev:
        k, actor = e["event_id"], e["actor"]
        if k in C_TABLE:
            cls, kind, comps, issue, need, sev = C_TABLE[k]
        else:
            cls, need, sev = "SINGLE_ACTOR", "NO", "INFO"
            comps, issue = actor, ""
            if actor in INSTITUTIONS:
                kind = "INSTITUTION"
            elif actor in NON_AGENT:
                kind = NON_AGENT[actor]
                issue = "행위자가 아닌 상태 주어(과정/장소)."
            elif actor in ("병사 이광섭",):
                kind = "PERSON"
                issue = "ATT0097/0098은 '병사'만 언급. 이름 '이광섭'은 source_records 제목(SRC001 '충청도 병마 절도사 이광섭')으로만 연결됨."
            elif actor in ("풍각 김생원", "흥덕 김생원"):
                kind = "PERSON_BY_TITLE"
            elif actor == "병영 장교":
                kind = "ROLE"
                issue = "인원수 불명. 같은 체포 후보(REL0077)인 AT0092는 '병영 장교 일행'."
            elif actor == "병영":
                kind = "INSTITUTION"
            else:
                kind = "PERSON"
        rows.append({
            "event_id": k, "actor": actor, "action": e["action"],
            "target_or_content": e["target_or_content"], "event_family_id": e["event_family_id"],
            "classification": cls, "actor_kind": kind, "components": comps,
            "role_or_structure_issue": issue, "participant_table_needed": need, "severity": sev,
        })
    return rows


ALIAS_FINDINGS = [
    ("재돌 / 변재돌", "AT0092;AT0109;AT0115;AT0122",
     "'재돌'(ATT0092·ATT0109·ATT0115)과 AT0122 target의 '변재돌'이 같은 사람인지 CSV에 명시 없음. AT0122 명단에는 '변지돌'과 '변재돌'이 따로 있음."),
    ("원돌 / 정원돌", "AT0085;AT0122;AT0135",
     "ATT0135(유제희)의 '원돌'과 ATT0085(이진욱)·AT0122 target의 '정원돌'이 같은 사람인지 CSV에 명시 없음."),
    ("풍각 김생원 / 풍각 김상제 / 풍각 상주 / 김명신", "AT0097;AT0099;AT0105;AT0134;AT0135",
     "ATT0099는 '풍각 김생원=김명신'만 명시. ATT0134의 '풍각 김상제', ATT0105의 '풍각 상주'를 김명신과 같은 사람으로 보는 근거는 ATT0135(구순 말을 듣고 김명신을 기록)라는 간접 연결뿐."),
    ("병사 / 이광섭", "AT0097;AT0098",
     "attestation은 '병사'만 언급하고, '이광섭'과 연결하는 근거는 source_records.source_title뿐."),
    ("병영 보조자 / 비장 / 한재욱", "AT0044;AT0045;AT0166;AT0169;REL0082",
     "ATT0045의 '병영 보조자'가 한재욱이라는 명제는 어떤 attestation에도 없음. REL0082만 둘을 동일시함."),
]


# =====================================================================
# AUDIT D: person set membership
# =====================================================================
SETS = [
    ("S1", "유제희가 기록한 사람 명단"),
    ("S2", "체포 명령 대상"),
    ("S3", "실제 체포된 사람"),
    ("S4", "구금이 확인된 사람"),
    ("S5", "신문을 받은 사람"),
    ("S6", "자미덕이 직접 지목한 것으로 명시된 사람"),
    ("S7", "자미덕이 '큰 도적이라고 말하라고 요구받았다'고 주장한 대상"),
    ("S8", "자미덕과 대질한 사람"),
]
OPEN_SET_NOTE = {
    "S1": "열린 집합: ATT0122 '여러 사람', ATT0135 '원돌 등'. 7명 명단은 AT0122.target_or_content에만 있음(attestation 명제에는 이름 없음).",
    "S2": "열린 집합: AT0074 체포령 대상 '관련 대상'(미상).",
    "S3": "열린 집합: ATT0016 '김명신 외 전후 체포자들', ATT0147 '사람부터 잡았다'(이름 없음).",
    "S4": "명시된 구금: 김명신(AT0007), 자미덕(AT0113), 변지돌(AT0091, 공주진). 나머지는 언급 없음.",
    "S5": "열린 집합: ATT0062 '응당 신문할 사람들'(이름 없음).",
    "S6": "정의상 '명시된' 사람만 포함. 자미덕이 누구를 지목했다고 적은 attestation 없음. REL0032 basis의 '거짓 지목'은 relation 주석이며 대상도 없음.",
    "S7": "ATT0116 '특정 인물들'은 이름이 전혀 없음.",
    "S8": "CSV에 기록된 대질은 AT0118 하나. 다른 대질이 없었다는 명시도 없음.",
}
U = "UNKNOWN"
PERSONS = ["변지돌", "변재돌", "재돌", "정원돌", "원돌", "김명신", "김성손", "김흥득", "김흥길", "김갑득", "이집거", "자미덕"]
# (value, evidence_ids, basis/note)
FIELD_ONLY = "EVENT_FIELD_ONLY: AT0122.target_or_content에만 있음, ATT0122 명제('여러 사람의 이름을 적었다')에는 이름 없음"
MEMB = {
    "변지돌": {"S1": ("DIRECT", "AT0122", FIELD_ONLY), "S2": ("DIRECT", "AT0084", "ATT0084 한재욱이 변지돌을 잡아오라고 지시(이진욱 진술)"),
              "S3": ("DIRECT", "AT0091", "ATT0091 이미 공주진에 붙잡혀 있었다(이진욱 진술). 병영이 아닌 공주진."),
              "S4": ("DIRECT", "AT0091", "ATT0091 '붙잡혀 있었다'(EF_STATE_CUSTODY)"),
              "S5": (U, "", "신문 언급 없음"), "S6": ("ABSENT", "", ""), "S7": (U, "AT0116", ""), "S8": (U, "", "")},
    "변재돌": {"S1": ("DIRECT", "AT0122", FIELD_ONLY), "S2": (U, "", "체포 지시 언급 없음"), "S3": (U, "", "체포 언급 없음"),
              "S4": (U, "", ""), "S5": (U, "", ""), "S6": ("ABSENT", "", ""), "S7": (U, "AT0116", ""), "S8": (U, "", "")},
    "재돌": {"S1": (U, "AT0122", "'변재돌'과 동일인 여부 미명시"), "S2": (U, "", "체포 지시 언급 없음"),
            "S3": (U, "AT0115;AT0109", "ATT0115: 자미덕이 '한재욱이 재돌이 이미 체포되었다고 말했다'고 진술(다툼 있는 전언). ATT0109: 재돌은 아산에 나가 있었다. 체포 사실의 직접 근거 아님."),
            "S4": (U, "", ""), "S5": (U, "", ""), "S6": ("ABSENT", "", ""),
            "S7": (U, "AT0116", "ATT0116에서 남편은 석방 대상으로 언급됨. 지목 대상 여부는 명시 없음."), "S8": (U, "", "")},
    "정원돌": {"S1": ("DIRECT", "AT0122", FIELD_ONLY + ". ATT0135의 '원돌'과 동일인 여부 미명시"),
              "S2": ("DIRECT", "AT0085", "ATT0085 한재욱이 정원돌을 잡아오라고 지시(이진욱 진술)"),
              "S3": (U, "", "실제 체포 언급 없음"), "S4": (U, "", ""), "S5": (U, "", ""), "S6": ("ABSENT", "", ""),
              "S7": (U, "AT0116", ""), "S8": (U, "", "")},
    "원돌": {"S1": ("DIRECT", "AT0135", "ATT0135 '김명신을 원돌 등의 이름과 함께 기록'(유제희 진술)"),
            "S2": (U, "AT0085", "'정원돌'과 동일인 여부 미명시"), "S3": (U, "", ""), "S4": (U, "", ""), "S5": (U, "", ""),
            "S6": ("ABSENT", "", ""), "S7": (U, "AT0116", ""), "S8": (U, "", "")},
    "김명신": {"S1": ("DIRECT", "AT0135;AT0122", "ATT0135 유제희 본인 진술(attestation 근거 있음)"),
              "S2": ("DIRECT", "AT0097;AT0099", "ATT0097 '풍각 김생원을 잡아오라' + ATT0099 '풍각 김생원=김명신'(같은 화자 이진욱)"),
              "S3": ("DIRECT", "AT0006;AT0101", "ATT0006(이형원 보고), ATT0101(이진욱 진술)"),
              "S4": ("DIRECT", "AT0007", "ATT0007 '달포 이상 구금'(이형원 보고)"),
              "S5": (U, "AT0008;AT0153", "충돌: ATT0008 '병영이 김명신을 달포 이상 조사'(이형원) vs ATT0153 '곤장이나 평범한 신문을 받지 않았다'(정조 판단). '조사'와 '신문'의 관계도 CSV에 정의 없음."),
              "S6": ("ABSENT", "", ""), "S7": (U, "AT0116", ""), "S8": (U, "", "")},
    "김성손": {"S1": ("DIRECT", "AT0122", FIELD_ONLY + ". 이 이름은 어떤 attestation에도 없음"), "S2": (U, "", ""), "S3": (U, "", ""),
              "S4": (U, "", ""), "S5": (U, "", ""), "S6": ("ABSENT", "", ""), "S7": (U, "AT0116", ""), "S8": (U, "", "")},
    "김흥득": {"S1": ("DIRECT", "AT0122", FIELD_ONLY + ". 이 이름은 어떤 attestation에도 없음"), "S2": (U, "", ""), "S3": (U, "", ""),
              "S4": (U, "", ""), "S5": (U, "", ""), "S6": ("ABSENT", "", ""), "S7": (U, "AT0116", ""), "S8": (U, "", "")},
    "김흥길": {"S1": ("DIRECT", "AT0122", FIELD_ONLY + ". 이 이름은 어떤 attestation에도 없음"), "S2": (U, "", ""), "S3": (U, "", ""),
              "S4": (U, "", ""), "S5": (U, "", ""), "S6": ("ABSENT", "", ""), "S7": (U, "AT0116", ""), "S8": (U, "", "")},
    "김갑득": {"S1": (U, "", "AT0122 7명 명단·ATT0135에 이름 없음. 명단이 열린 집합이라 제외 단정 불가"),
              "S2": ("DIRECT", "AT0098;AT0100", "ATT0098 '흥덕 김생원을 잡아오라' + ATT0100 '흥덕 김생원=김갑득'"),
              "S3": ("DIRECT", "AT0102", "ATT0102 장교 일행이 김갑득을 잡아왔다"),
              "S4": (U, "", "구금 언급 없음"), "S5": (U, "", ""), "S6": ("ABSENT", "", ""), "S7": (U, "AT0116", ""), "S8": (U, "", "")},
    "이집거": {"S1": (U, "", "AT0122 7명 명단·ATT0135에 이름 없음. 명단이 열린 집합이라 제외 단정 불가"),
              "S2": (U, "", "체포 지시 언급 없음"), "S3": (U, "", "체포 언급 없음"), "S4": (U, "", "구금 언급 없음"),
              "S5": (U, "AT0118", "대질 상대로만 등장. 대질을 신문으로 볼 근거는 CSV에 없음"),
              "S6": ("ABSENT", "AT0119;REL0032", "ATT0119는 '거짓으로 말했다'만 진술, 지목 대상 미명시"),
              "S7": (U, "AT0116", "'특정 인물들' 이름 없음. AT0116과 AT0118/AT0119를 잇는 relation 없음"),
              "S8": ("DIRECT", "AT0118;AT0119", "ATT0118 '자미덕은 이집거와 대질했다'(자미덕 단독 진술)")},
    "자미덕": {"S1": (U, "", "명단에 이름 없음"), "S2": (U, "AT0092", "ATT0092 '변지돌 대신 … 자미덕만을 잡았다'. 자미덕에 대한 체포 명령 언급 없음"),
              "S3": ("DIRECT", "AT0092;AT0110", "ATT0092(이진욱), ATT0110(자미덕)"),
              "S4": ("DIRECT", "AT0113", "ATT0113 비장청 다모방 구류"),
              "S5": ("DIRECT", "AT0112;AT0129", "ATT0112 도적 혐의 신문 1회(자미덕 진술), ATT0129 한재욱 재질문(한재욱 진술)"),
              "S6": ("ABSENT", "", "본인"), "S7": (U, "AT0116", "본인은 석방 대상으로 언급됨. 대상 여부 명시 없음"),
              "S8": ("ABSENT", "AT0118", "본인(대질 당사자)")},
}

KEY_QUESTIONS = [
    ("Q1", "김흥득은 유제희 명단에 있었는가?", "PARTIAL: event 필드에만 있음",
     "DIRECT (EVENT_FIELD_ONLY)", "AT0122;AT0135",
     "AT0122.target_or_content '변지돌·변재돌·정원돌·김명신·김성손·김흥득·김흥길'에 있음. 그러나 ATT0122 명제는 '한재욱은 유제희가 여러 사람의 이름을 적었다고 진술했다'로 이름이 없고, 유제희 본인 진술 ATT0135는 '김명신을 원돌 등'만 언급. '김흥득'은 어떤 attestation 명제에도 나오지 않음.",
     "명단 이름의 출처가 attestation으로 추적되지 않음(Audit E: AT0122 target UNSUPPORTED)."),
    ("Q2", "김흥득이 실제로 체포되거나 구금됐다는 직접 근거가 있는가?", "NO",
     "UNKNOWN", "",
     "김흥득은 AT0122 target 외 어떤 event/attestation/relation에도 나오지 않음.",
     "명단에 있으니 체포됐을 것이라는 추론 금지."),
    ("Q3", "자미덕 진술의 '특정 인물들'이 누구인지 현재 CSV에 이름이 남아 있는가?", "NO",
     "UNKNOWN", "AT0116",
     "ATT0116 '…특정 인물들을 큰 도적이라고 말하면…', AT0116 target '여러 사람을 큰 도적이라 말하면…'. 이름 없음. AT0116에 연결된 relation은 REL0080(→AT0131 부인)뿐.",
     "target('여러 사람')과 명제('특정 인물들')의 표현도 서로 다름."),
    ("Q4", "이집거가 그 '특정 인물들' 중 하나라고 직접 적힌 근거가 있는가?", "NO",
     "UNKNOWN", "AT0116;AT0118;AT0119;AT0131;REL0032;REL0080;REL0081",
     "AT0116과 AT0118/AT0119 사이 직접 relation 없음. 유일한 경로는 AT0116–REL0080–AT0131–REL0081–AT0119–REL0032–AT0118로, 같은 부인에 대한 충돌 연결일 뿐 대상자 동일성 relation이 아님.",
     "REL0032 basis의 '거짓 지목'은 원문보다 강한 표현(Audit F NEW_INFORMATION_ADDED)이라 근거로 쓰면 안 됨."),
    ("Q5", "이집거는 유제희 명단에 포함되어 있는가?", "NO (명시적으로 포함되지 않음)",
     "UNKNOWN (열린 명단)", "AT0122;AT0135",
     "AT0122 7명 명단에도, ATT0135 '김명신을 원돌 등'에도 이집거 없음.",
     "명단 attestation이 '여러 사람', '등'으로 열린 표현이라 포함되지 않았다고 단정할 수도 없음."),
    ("Q6", "이집거가 어떤 경로로 수사 대상이 되었는지 현재 CSV가 설명하고 있는가?", "NO",
     "UNKNOWN", "AT0118;AT0119",
     "이집거는 ATT0118·ATT0119에서 자미덕의 대질 상대로만 등장. 체포 명령·체포·구금·신문·명단·지목 행이 하나도 없음.",
     "'수사 대상이었다'는 전제 자체도 CSV에서 확인되지 않음."),
]


def audit_d():
    rows = []
    for p in PERSONS:
        r = {"person": p}
        for sid, sname in SETS:
            v, ev_ids, note = MEMB[p][sid]
            assert v in ("DIRECT", "ABSENT", "UNKNOWN"), (p, sid)
            r[f"{sid}_value"] = v
            r[f"{sid}_evidence_ids"] = ev_ids
            r[f"{sid}_note"] = note
        rows.append(r)
    cols = ["person"] + [f"{s}_{x}" for s, _ in SETS for x in ("value", "evidence_ids", "note")]
    legend = {"person": "[SET_DEFINITIONS]"}
    for sid, sname in SETS:
        legend[f"{sid}_value"] = sname
        legend[f"{sid}_evidence_ids"] = ""
        legend[f"{sid}_note"] = OPEN_SET_NOTE[sid]
    rows.append(legend)
    qrows = [dict(zip(["question_id", "question", "answer", "membership_value", "evidence_ids",
                       "evidence_text", "caveat"], q)) for q in KEY_QUESTIONS]
    return rows, cols, qrows


# =====================================================================
# AUDIT E: field-level provenance
# =====================================================================
D, DER, IMP, UNS, AMB = ("DIRECTLY_SUPPORTED", "DERIVED_FROM_LINKED_STRUCTURE",
                         "IMPORTED_FROM_OTHER_ATTESTATION", "UNSUPPORTED", "AMBIGUOUS")
HANYANG_REASON = "'한양'은 어떤 attestation 명제·source_records에도 없음. 조정 기록이라는 배경지식으로 채운 값."
PLACE = {
    "AT0001": (D, "", "ATT0001 '청주 덕평'"),
    "AT0002": (DER, "AT0001", "ATT0002는 '구순 집 이웃'만 말함. 같은 SRC001 보고의 ATT0001(구순 거주지)에서 이어짐."),
    "AT0006": (AMB, "", "ATT0006 '병영이 김명신을 잡았다': '병영'은 행위 주체. 체포 장소는 명시 없음(행위자 기관을 장소로 옮긴 것)."),
    "AT0007": (IMP, "AT0042", "ATT0007은 구금 장소를 말하지 않음. '병영 옥'은 ATT0042(이조원, SRC002)에만 있음."),
    "AT0008": (AMB, "", "ATT0008 '병영이 … 조사했다': 기관 주체를 장소로 옮긴 것으로 보임."),
    "AT0009": (DER, "AT0008", "같은 보고·같은 조사 결과 상태. 단 AT0008의 장소 자체가 AMBIGUOUS."),
    "AT0010": (IMP, "AT0042;REL0083", "ATT0010에는 장소 없음. '병영 옥'은 ATT0042(이조원, SRC002)의 표현으로, REL0083로만 연결됨."),
    "AT0012": (IMP, "AT0172", "ATT0012는 '각 진영'만 말함. 이형원이 충청도 관찰사라는 정보는 ATT0172(SRC004)에 있음."),
    "AT0032": (IMP, "AT0001", "ATT0032(이조원, SRC002)는 '구순 집 앞'만 말함. '청주 덕평'은 ATT0001(SRC001)에서 옴."),
    "AT0034": (IMP, "AT0001;REL0072", "ATT0034(SRC002)에는 지명 없음. ATT0001(SRC001)에서 옴."),
    "AT0042": (D, "", "ATT0042 '병영 옥에서'('충청' 접두는 정규화)"),
    "AT0061": (D, "", "ATT0061 '공주목'"),
    "AT0062": (DER, "AT0061;REL0055", "같은 서계의 ATT0061(공주목 도착)에서 이어짐."),
    "AT0063": (D, "", "ATT0063 '구순 집 계집종의 남편'"),
    "AT0064": (D, "", "ATT0064 '구순 집 바깥 사랑'"),
    "AT0065": (AMB, "AT0064", "ATT0065는 장소를 말하지 않음. 명업 거주지(ATT0064)에서 추정한 값이나 relation 연결 없음."),
    "AT0066": (AMB, "AT0065;REL0003", "장소 명시 없음. AT0065의 장소 자체가 AMBIGUOUS."),
    "AT0067": (AMB, "AT0066;REL0004", "ATT0067 '집 안으로 들어갔다': 누구 집인지 명시 없음."),
    "AT0068": (AMB, "", "장소 명시 없음. AT0065~0067과 relation 연결 없음."),
    "AT0069": (IMP, "AT0001", "ATT0069(명업, SRC004)에는 지명 없음. '청주 덕평'은 ATT0001(이형원, SRC001)에서 옴."),
    "AT0072": (IMP, "AT0001", "ATT0072(명업)에는 지명 없음. ATT0001(SRC001)에서 옴."),
    "AT0073": (IMP, "AT0120;REL0073", "ATT0073(명업)은 '소장을 올렸다'만 말함. '진영'은 ATT0120(한재욱)에만 있고 REL0073은 후보(candidate) 연결."),
    "AT0075": (D, "", "ATT0075 '구순 집에 왔다'"),
    "AT0076": (D, "", "ATT0076 '안행랑'"),
    "AT0077": (DER, "AT0076;REL0008", "같은 명업 진술의 AT0076에서 이어짐."),
    "AT0078": (D, "", "ATT0078 '병영 뜰'"),
    "AT0079": (D, "", "ATT0079 '병영에서'"),
    "AT0080": (DER, "AT0079", "같은 parent_fact(F060)의 AT0079에서 이어짐."),
    "AT0081": (D, "", "ATT0081 '병영에서 … 비장청으로'"),
    "AT0082": (DER, "AT0081;REL0014", "ATT0082 '비장청 방안'. '충청병영'은 AT0081에서."),
    "AT0083": (DER, "AT0082;REL0015", "장소 명시 없음. 같은 진술 흐름의 AT0082에서."),
    "AT0084": (DER, "AT0082;REL0016", "같음."),
    "AT0085": (DER, "AT0082;REL0017", "같음."),
    "AT0086": (AMB, "AT0083;REL0018", "ATT0086은 장소·행위자 없는 수동형."),
    "AT0087": (AMB, "AT0086;REL0019", "같음."),
    "AT0088": (AMB, "", "장소 명시 없음. 다른 행과 relation 연결 없음."),
    "AT0089": (DER, "AT0083;REL0020", "'덕평'은 같은 화자의 ATT0083('덕평으로 가라')에서."),
    "AT0090": (DER, "AT0083;REL0021", "같음."),
    "AT0091": (D, "", "ATT0091 '공주진'"),
    "AT0093": (D, "", "ATT0093 '구순 집으로 갔다'"),
    "AT0094": (D, "", "ATT0094 '구순 집에서'"),
    "AT0095": (DER, "AT0094;REL0026", "같은 문답 흐름."),
    "AT0096": (DER, "AT0094;REL0027", "같은 문답 흐름."),
    "AT0097": (AMB, "", "ATT0097은 명령 장소를 말하지 않음. 병사→병영은 배경지식."),
    "AT0098": (AMB, "", "같음."),
    "AT0103": (D, "", "ATT0103 '구순 집에 들렀다'"),
    "AT0104": (DER, "AT0103;REL0038", "같은 조계완 진술 흐름."),
    "AT0105": (DER, "AT0104;REL0039", "같음."),
    "AT0106": (DER, "AT0105;REL0040", "같음."),
    "AT0107": (DER, "AT0106;REL0041", "같음."),
    "AT0108": (DER, "AT0107;REL0042", "같음."),
    "AT0109": (D, "", "ATT0109 '아산'"),
    "AT0110": (UNS, "AT0111", "ATT0110 '병영 장교가 갑자기 찾아와 자신을 붙잡았다': '병영'은 장교의 소속. ATT0111 '병영으로 데려갔다'는 체포 장소가 병영이 아님을 시사 → 값이 같은 화자의 다음 진술과 긴장."),
    "AT0111": (D, "", "ATT0111 '병영으로 데려갔다'(목적지)"),
    "AT0112": (DER, "AT0111;REL0029", "이송 뒤 신문. 신문 장소는 명시 없음."),
    "AT0113": (DER, "AT0081", "ATT0113 '비장청 다모방'. '충청병영' 접두는 ATT0081에서."),
    "AT0114": (DER, "AT0113;REL0031", "ATT0114 '방안으로'. 비장청은 AT0113에서."),
    "AT0115": (AMB, "AT0114", "장소 명시 없음. AT0114와 relation 없음."),
    "AT0116": (AMB, "AT0114", "장소 명시 없음. AT0114와 relation 없음."),
    "AT0117": (AMB, "", "장소 명시 없음."),
    "AT0118": (UNS, "", "대질 장소는 어떤 attestation에도 없음. AT0118은 구금 행들과 relation 연결도 없음."),
    "AT0119": (UNS, "", "같음(대질 장소 미상)."),
    "AT0120": (D, "", "ATT0120 '진영에 정소된'"),
    "AT0121": (IMP, "AT0001;AT0083", "ATT0121(한재욱)은 '내보냈다'만 말함. '덕평'은 ATT0001(SRC001)·ATT0083(이진욱)에만 있음."),
    "AT0122": (UNS, "AT0123", "ATT0122에는 장소 없음. 같은 화자의 ATT0123 '이름을 적어 병영으로 돌아왔다'는 기록이 병영 밖에서 이루어졌음을 시사 → 값과 긴장."),
    "AT0123": (D, "", "ATT0123 '병영으로 돌아왔다'"),
    "AT0124": (AMB, "AT0123", "장소 명시 없음. AT0123과 relation 없음."),
    "AT0125": (IMP, "AT0113;REL0078", "ATT0125(한재욱)는 '방 안'만 말함. '비장청'은 자미덕 진술(ATT0113)에서, 후보 연결 REL0078을 통해 옴."),
    "AT0126": (IMP, "AT0113;REL0079", "같음(REL0079 후보 연결)."),
    "AT0127": (UNS, "", "한재욱 진술 흐름(REL0033~0035) 어디에도 장소 없음."),
    "AT0128": (UNS, "", "같음."),
    "AT0129": (UNS, "", "같음."),
    "AT0130": (UNS, "", "같음."),
    "AT0131": (UNS, "", "부인 발화의 장소는 안핵 공초 자리. '비장청'은 주장된 사주의 장소로 보이나 그것도 명시 없음."),
    "AT0133": (IMP, "AT0001;AT0083;REL0010", "ATT0133은 '현지'만 말함. '덕평'은 다른 화자의 attestation에서."),
    "AT0134": (IMP, "AT0001;AT0083", "같음."),
    "AT0135": (UNS, "AT0123", "ATT0135에는 장소 없음. ATT0123(한재욱) '적어 병영으로 돌아왔다'와 긴장."),
    "AT0136": (IMP, "AT0123;REL0076", "ATT0136 '위에 올렸다'. '병영'은 한재욱의 ATT0123에서 후보 연결 REL0076으로."),
    "AT0137": (UNS, "AT0055", "ATT0137 '내려가는 길에'. '호서'는 ATT0055의 다른 맥락('전년 호서 화적')에만 있음."),
    "AT0138": (UNS, "AT0055", "같음."),
    "AT0139": (DER, "AT0062;REL0057", "정식 조사(AT0062, 공주목)에서 이어짐."),
    "AT0140": (AMB, "", "판단 장소 명시 없음. relation 없음."),
    "AT0141": (AMB, "", "같음."),
    "AT0142": (AMB, "", "같음(REL0058은 AT0143과만 연결)."),
    "AT0143": (AMB, "AT0142;REL0058", "같음."),
    "AT0144": (UNS, "AT0055", "'호서'는 다른 맥락에만 있음."),
    "AT0145": (UNS, "AT0055", "같음."),
    "AT0161": (D, "", "ATT0161 '신지도'(목적지 의미; Audit B 참조)"),
    "AT0168": (D, "", "ATT0168 '영동현'(목적지 의미)"),
    "AT0170": (AMB, "", "'원도'는 ATT0170 '먼 섬'의 범주어. 지명 아님."),
}
ACTOR = {
    "AT0014": (DER, "AT0013", "ATT0014 '응답자들이'. '회동 조사' 수식은 같은 보고의 AT0012/AT0013에서."),
    "AT0015": (DER, "AT0013", "같음."),
    "AT0016": (AMB, "AT0013", "ATT0016 '…진술이 실려 있다': 진술자 미명시."),
    "AT0072": (DER, "AT0071;REL0002", "ATT0072 '두 사람이'."),
    "AT0074": (AMB, "", "ATT0074 수동형 '체포령이 내려졌다'. '미상 관서'는 자리표시자."),
    "AT0086": (UNS, "", "ATT0086 수동형 '철편 네 개가 만들어졌다'. 행위자를 한재욱 쪽에 귀속할 근거 없음."),
    "AT0087": (UNS, "", "ATT0087 수동형 '제공됐다'. 근거 없음."),
    "AT0089": (DER, "AT0083", "ATT0089는 '이진욱은 … 기다렸다'. '조계완 등'은 ATT0083에서."),
    "AT0090": (DER, "AT0083", "ATT0090 '일행이 나갔다'. 구성원은 ATT0083에서."),
    "AT0092": (DER, "AT0101", "ATT0092 주어는 화자 이진욱(암묵). '장교 일행'은 ATT0101 표현."),
    "AT0093": (DER, "AT0092;REL0024", "같음."),
    "AT0094": (DER, "AT0093;REL0025", "같음."),
    "AT0097": (DER, "SRC001(source_title)", "ATT0097은 '병사'만 말함. '이광섭'은 source_records.source_title에서."),
    "AT0098": (DER, "SRC001(source_title)", "같음."),
    "AT0112": (DER, "AT0111;REL0029", "ATT0112 수동형 '신문을 받았다'. 신문 주체 미명시, 이송지(병영)에서 이어짐."),
    "AT0120": (IMP, "AT0073;REL0073", "ATT0120(한재욱) '구순 집 도난이 진영에 정소된 뒤': 정소 주체 미명시. '구순'은 ATT0073(명업)에서 후보 연결로."),
    "AT0121": (AMB, "", "ATT0121의 '병영'은 유제희 소속(병영 아전)이지 행위 주체가 아님. '/병영' 추가."),
    "AT0161": (DER, "AT0160;REL0090", "ATT0161 '기사의 최종 처분에는 …'. 처분 주체 미명시."),
    "AT0168": (DER, "AT0167;REL0091", "같음."),
}
ACTION = {
    "AT0012": (AMB, "", "ATT0012 '영장들에게 함께 조사하게 했다'(사역=지시) → action '회동 조사 실시'는 지시와 수행을 합침."),
    "AT0008": (D, "", "'조사' 행위 자체는 직접 근거. 단 family=EF_ACT_RECORD_REPORT 분류는 행위와 맞지 않음."),
}
TARGET = {
    "AT0012": (AMB, "", "'관련자'는 ATT0012에 없는 자리표시자."),
    "AT0026": (AMB, "", "ATT0026 '구순이 도난을 꾸몄다는 방향을 받아들였다' vs target '도난 자체가 없었다는 방향'. 구순의 조작 행위(주체)가 빠지고 '도난 부재'로 바뀜."),
    "AT0033": (D, "", "ATT0033과 같음. 단 명제의 근거('주변 환경과 목격자 부재')가 target에서 빠짐."),
    "AT0036": (UNS, "", "ATT0036은 '피우 관련 일에서 구순과 김명신 사이에 갈등이 있었다'만 말함. target의 '김명신의 형', '접촉 불허'는 어떤 attestation에도 없음."),
    "AT0073": (IMP, "AT0120;REL0073", "ATT0073 '소장을 올렸다'(내용 미명시). '도난 사건'은 ATT0120(한재욱)에서."),
    "AT0074": (AMB, "", "'관련 대상'은 자리표시자."),
    "AT0089": (AMB, "", "'출발 시점'은 자리표시자."),
    "AT0090": (DER, "AT0083", "'덕평 방면'은 같은 화자의 ATT0083에서."),
    "AT0094": (DER, "AT0095;REL0026", "ATT0094는 질문 대상을 명시하지 않음. '구순에게'는 응답자(AT0095)에서."),
    "AT0097": (DER, "AT0099", "'(김명신)'은 같은 화자의 식별 진술 ATT0099에서."),
    "AT0098": (DER, "AT0100", "'(김갑득)'은 ATT0100에서."),
    "AT0116": (AMB, "", "ATT0116 '특정 인물들' vs target '여러 사람'. 지시 대상의 성격 표현이 다름."),
    "AT0119": (AMB, "", "ATT0119 '거짓으로 말했다' vs target '거짓말을 꾸몄다'. 표현이 강해지고 '이집거와 대질할 때' 맥락이 빠짐."),
    "AT0122": (UNS, "AT0135;AT0084;AT0085", "ATT0122 '여러 사람의 이름을 적었다'에는 이름 없음. 7명 중 변재돌·김성손·김흥득·김흥길은 어떤 attestation에도 없고, 김명신·원돌은 ATT0135(유제희, REL0075 후보 연결), 변지돌·정원돌은 이진욱 진술(체포 지시 대상)에만 있음."),
    "AT0133": (IMP, "AT0001;AT0083", "ATT0133 '현지'. '덕평 일대'는 다른 화자의 attestation에서."),
    "AT0149": (AMB, "REL0060;REL0061;REL0062", "ATT0149 '세 가지 의안으로 분리했다'(의안 내용 없음). target의 세 의안 이름은 relation basis와 연결된 판단 행에서 역으로 구성됨. 'REL0062'가 가리키는 AT0155는 '날조 여부'가 아니라 호칭의 기원."),
    "AT0154": (AMB, "", "ATT0154 '김명신 부처의 죽음을 …'. target에서 대상('김명신 부처')이 빠짐."),
    "AT0171": (AMB, "", "ATT0171 '도신 장계와 어사 보고'. target은 '이형원', '홍대협'으로 특정했으나 '어사'는 이조원일 수도 있음(CSV에 두 어사 존재). 쟁점('구순의 도난 여부')도 빠짐."),
}
TOPIC = {
    "AT0010": (UNS, "", "ATT0010에는 원인 진술 없음(시간 순서 '구금·조사 뒤'만). DEATH_CAUSE는 근거 없음."),
    "AT0045": (IMP, "AT0132;REL0082", "ATT0045는 '병영 보조자'라고만 함. '한재욱'과의 관계 쟁점(HAN_GUSUN_RELATION)은 REL0082의 동일시를 통해서만 생김."),
    "AT0070": (DER, "AT0071;REL0001", "편지 송부 자체는 갈등이 아님. 같은 편지의 내용(AT0071)에서 옴."),
    "AT0114": (AMB, "AT0116", "ATT0114 '매일 방안으로 불러들였다'는 사주를 말하지 않음. COACHING은 해석적 묶음."),
    "AT0115": (AMB, "AT0116", "ATT0115는 사주를 말하지 않음."),
    "AT0117": (AMB, "AT0116", "ATT0117 '떡과 밥을 주었다'는 사주를 말하지 않음."),
    "AT0122": (DER, "AT0121", "명단을 '용의자 명단'으로 보는 것은 ATT0121 '도적의 진상을 탐지하려고'에서."),
    "AT0123": (DER, "AT0121", "같음."),
    "AT0124": (DER, "AT0121", "같음."),
    "AT0125": (AMB, "REL0078", "한재욱이 인정한 '방 안으로 불러들인 사실'을 사주 충돌 그룹(COACHING)에 넣음. 인정된 중립 행위가 사주 쟁점으로 묶임."),
    "AT0126": (AMB, "REL0079", "한재욱이 인정한 '남은 밥을 준 사실'을 COACHING에 넣음."),
}
CONFLICT = {k: v for k, v in TOPIC.items() if k in ("AT0010", "AT0045", "AT0114", "AT0115", "AT0117", "AT0125", "AT0126")}
DATE = {
    # (field, event_id): (class, evidence, reason). Missing entries are resolved by rule or raise.
}
for k in ("AT0006", "AT0007", "AT0008", "AT0009"):
    DATE[("start", k)] = (IMP, "AT0097;AT0101", "1793-03-04는 이진욱 진술(SRC004)의 날짜. ATT%s(이형원, SRC001)에는 날짜 없음." % k[2:])
for k in ("AT0061", "AT0062", "AT0137", "AT0138", "AT0139", "AT0140", "AT0141", "AT0142",
          "AT0143", "AT0144", "AT0145", "AT0146", "AT0147", "AT0148"):
    DATE[("start", k)] = (DER, "SRC003;REL0054;REL0071", "하한 1793-05-28은 안핵어사 임명 기록(SRC003) 날짜.")
DATE[("start", "AT0065")] = (D, "", "ATT0065 '2월 22일 밤'")
DATE[("end", "AT0065")] = (D, "", "ATT0065 '2월 22일 밤'")
for k, r in (("AT0066", "REL0003"), ("AT0067", "REL0004")):
    DATE[("start", k)] = DATE[("end", k)] = (DER, "AT0065;" + r, "AT0065의 날짜에서 relation으로 이어짐.")
DATE[("start", "AT0068")] = DATE[("end", "AT0068")] = (AMB, "AT0065", "ATT0068에는 날짜 없음. AT0065~0067과 relation 연결도 없음(REL0066은 이 날짜를 '확정'으로 사용).")
DATE[("end", "AT0069")] = (AMB, "AT0070", "ATT0069 '본래 친숙'. 2월 초 이전이라는 상한은 relation 없이 AT0070에서 추정.")
DATE[("start", "AT0070")] = DATE[("end", "AT0070")] = (D, "", "ATT0070 '2월 초'")
DATE[("start", "AT0071")] = DATE[("end", "AT0071")] = (DER, "AT0070;REL0001", "같은 편지.")
DATE[("start", "AT0072")] = (DER, "AT0071;REL0002", "ATT0072 '그 편지 이후'.")
for k in ("AT0073", "AT0074", "AT0075", "AT0076", "AT0077", "AT0120", "AT0121", "AT0122", "AT0123",
          "AT0124", "AT0133", "AT0134", "AT0135", "AT0136"):
    DATE[("end", k)] = (UNS, "", "상한 1793-02-28을 주는 attestation이 없고, 날짜가 있는 사건(AT0081 등)으로 가는 relation 경로도 없음.")
DATE[("start", "AT0081")] = DATE[("end", "AT0081")] = (D, "", "ATT0081 '2월 28일 밤'")
for k, r in (("AT0082", "REL0014"), ("AT0083", "REL0015"), ("AT0084", "REL0016"), ("AT0085", "REL0017")):
    DATE[("start", k)] = DATE[("end", k)] = (DER, "AT0081;" + r, "AT0081에서 relation으로 이어짐.")
for k, r in (("AT0086", "REL0018"), ("AT0087", "REL0019")):
    DATE[("start", k)] = (DER, "AT0081;" + r, "AT0081 이후.")
    DATE[("end", k)] = (DER, "AT0089;REL0020", "새벽(AT0089) 이전.")
DATE[("start", "AT0088")] = DATE[("end", "AT0088")] = (AMB, "", "ATT0088에는 날짜 없음. relation 연결 없음.")
for k in ("AT0089", "AT0090", "AT0091", "AT0092", "AT0093", "AT0094", "AT0095", "AT0096"):
    DATE[("start", k)] = DATE[("end", k)] = (DER, "AT0081;REL0020-REL0027",
                                             "2/28 밤(AT0081) → '날이 밝아' 새벽 → relation 사슬. 2/28 다음 날을 2/29로 본 날짜 계산 포함.")
DATE[("start", "AT0097")] = DATE[("end", "AT0097")] = (D, "", "ATT0097 '3월 4일'")
DATE[("start", "AT0098")] = DATE[("end", "AT0098")] = (D, "", "ATT0098 '3월 4일'")
for k in ("AT0099", "AT0100"):
    DATE[("start", k)] = DATE[("end", k)] = (AMB, "AT0097", "시점 없는 식별 진술에 명령 날짜를 붙임.")
for k, r in (("AT0101", "REL0036"), ("AT0102", "REL0037")):
    DATE[("start", k)] = DATE[("end", k)] = (AMB, r, "명령(3/4) 뒤 집행이라는 하한만 근거. 같은 날 집행했다는 진술 없음.")
for k in ("AT0103", "AT0104", "AT0105", "AT0106", "AT0107", "AT0108"):
    DATE[("start", k)] = DATE[("end", k)] = (IMP, "AT0097", "조계완 진술에는 날짜 없음. 3/4는 이진욱 진술(ATT0097)의 날짜이며 조계완 행과 relation 연결 없음.")
for k in ("AT0110", "AT0111", "AT0112", "AT0113", "AT0114", "AT0115", "AT0116", "AT0117"):
    DATE[("start", k)] = (IMP, "AT0092;REL0077", "자미덕 진술에는 날짜 없음. 1793-02-29는 이진욱 진술(AT0092)에서 후보 연결 REL0077(SAME_EVENT_CANDIDATE)을 통해 옴.")
for k in ("AT0017", "AT0018", "AT0019"):
    DATE[("start", k)] = DATE[("end", k)] = (AMB, "SRC001", "이형원 장계 안의 평가·건의를 기록일(1793-05-12)에 DAY 정밀도로 고정. 장계 작성일은 기록에 없음.")

DATE_LITERAL_EVENTS = {"AT0065", "AT0070", "AT0081", "AT0097", "AT0098"}
OFFICIAL_MODES = {"ROYAL_ORDER", "ROYAL_JUDGMENT", "MINISTERIAL_PROPOSAL", "DIRECT_OFFICIAL_ACTION",
                  "DIRECT_RECORDED_SPEECH", "OFFICIAL_REPORT", "OFFICIAL_EVALUATION"}


def classify_date(field, e, a, src):
    v = e[f"occurrence_lunar_{field}"]
    key = (field, e["event_id"])
    if key in DATE:
        return DATE[key]
    rec = src[a["source_record_id"]]["record_date_lunar"]
    if v == rec and a["attestation_mode"] in OFFICIAL_MODES:
        if field == "end" and e["time_precision"] == "BEFORE_OR_BY_REPORT":
            return (DER, a["source_record_id"], "보고 기록일을 상한으로 사용(source_records.record_date_lunar).")
        return (DER, a["source_record_id"], "공식 행위·발화의 기록일(source_records.record_date_lunar).")
    if v == rec and field == "end":
        return (DER, a["source_record_id"], "기록일을 상한으로 사용.")
    raise KeyError(f"unclassified date {key}={v}")


def audit_e(ev, at, src):
    rows = []
    for e in ev:
        k, a = e["event_id"], at[e["event_id"]]
        for field in ("actor", "action", "target_or_content", "historical_place",
                      "occurrence_lunar_start", "occurrence_lunar_end", "claim_topic", "conflict_group"):
            v = e[field]
            if not v:
                continue
            if field == "actor":
                c = ACTOR.get(k, (D, "", "attestation 명제(또는 화자)에 같은 행위자가 나옴."))
            elif field == "action":
                c = ACTION.get(k, (D, "", "attestation 명제의 서술어를 옮기거나 같은 뜻으로 줄인 것."))
            elif field == "target_or_content":
                c = TARGET.get(k, (D, "", "attestation 명제에 같은 내용이 있음."))
            elif field == "historical_place":
                if v == "한양":
                    c = (UNS, "", HANYANG_REASON)
                else:
                    c = PLACE[k]
            elif field.startswith("occurrence"):
                c = classify_date(field.split("_")[-1], e, a, src)
            elif field == "claim_topic":
                c = TOPIC.get(k, (D, "", "attestation 명제의 주제와 같고, attestation.claim_topic과도 일치."))
            else:
                c = CONFLICT.get(k, (D, "", "attestation 명제의 주제와 같고, attestation.conflict_group과도 일치."))
            rows.append({
                "event_id": k, "attestation_id": a["attestation_id"],
                "source_record_id": a["source_record_id"],
                "speaker_or_reporting_actor": a["speaker_or_reporting_actor"],
                "field": field, "value": v, "classification": c[0],
                "evidence_ids": c[1], "explanation": c[2], "proposition_ko": a["proposition_ko"],
            })
    return rows


# =====================================================================
# AUDIT F: relation meaning overreach
# =====================================================================
SM, SS, MS, NI = "SAME_MEANING", "SAFE_SUMMARY", "MORE_SPECIFIC_THAN_SOURCE", "NEW_INFORMATION_ADDED"
ORDER_ONLY = "선후(서술 순서만 근거)"
F = {
    "REL0001": (SS, "", "INFO", "편지와 그 내용. 새 정보 없음."),
    "REL0002": (SM, "", "INFO", "ATT0072 '그 편지 이후'."),
    "REL0003": (MS, ORDER_ONLY, "LOW_REVIEW", "ATT0065/0066 어디에도 '부른 뒤 알렸다'는 순서 표지 없음. 진술 서술 순서를 선후로 바꿈."),
    "REL0004": (SM, "", "INFO", "ATT0067 '나복의 말을 듣고'."),
    "REL0005": (SM, "", "INFO", "ATT0074 '소장 제출 뒤 체포령'."),
    "REL0006": (SM, "", "INFO", "ATT0075 '체포령 뒤'."),
    "REL0007": (MS, ORDER_ONLY + "; 동일성(불러들인 장교=도착한 장교 중 1명)", "LOW_REVIEW", "ATT0076에 순서 표지 없음."),
    "REL0008": (MS, ORDER_ONLY, "LOW_REVIEW", "ATT0077에 순서 표지 없음."),
    "REL0009": (SM, "", "INFO", "ATT0120 '정소된 뒤라고 진술'."),
    "REL0010": (MS, "동일성·집행(파견=실제 수행)", "MEDIUM_REVIEW",
                "ATT0133(유제희)은 누가 보냈는지 말하지 않음. COREFERENCE 층에서는 같은 쌍을 SAME_EPISODE_CANDIDATE(REL0074)로 두었는데, TEMPORAL 층에서는 HIGH 'EXECUTION_OF_ORDER'·basis '실제 … 수행'으로 확정함."),
    "REL0011": (SM, "", "INFO", "ATT0134 '탐문 중'."),
    "REL0012": (SM, "", "INFO", "ATT0135 '구순의 말을 듣고'."),
    "REL0013": (SM, "", "INFO", "ATT0136 '기록한 이름들을 위에 올렸다'."),
    "REL0014": (MS, ORDER_ONLY, "LOW_REVIEW", "ATT0081/0082에 순서 표지 없음."),
    "REL0015": (MS, ORDER_ONLY, "LOW_REVIEW", "ATT0083에 순서 표지 없음."),
    "REL0016": (MS, ORDER_ONLY, "LOW_REVIEW", "ATT0084에 순서 표지 없음."),
    "REL0017": (MS, ORDER_ONLY, "LOW_REVIEW", "ATT0085에 순서 표지 없음."),
    "REL0018": (MS, ORDER_ONLY, "LOW_REVIEW", "ATT0086 '체포 작전을 위해'는 목적만 말함. confidence=MEDIUM으로 이미 낮춤."),
    "REL0019": (SS, "", "INFO", "만든 뒤 제공(논리적 선후)."),
    "REL0020": (MS, "선후 + '철편 준비 사이'(동시성 정보)", "MEDIUM_REVIEW",
                "basis '철편 준비 사이 날이 밝아'는 두 행 명제 어디에도 없고, '사이'(겹침)는 relation_type BEFORE와도 맞지 않음."),
    "REL0021": (SS, "", "INFO", "기다린 뒤 출발(ATT0090 '새벽에')."),
    "REL0022": (AMB, "선후(상태의 시작 시점)", "MEDIUM_REVIEW",
                "ATT0091 '이미 붙잡혀 있었다' = 출발 전에 시작된 상태. BEFORE(출발→상태)는 상태를 '확인 행위'로 바꿔 읽어야 성립(basis '확인'). event 행은 확인이 아니라 상태."),
    "REL0023": (MS, "선후(서술 순서 → 사건 순서)", "LOW_REVIEW", "basis 스스로 '서술 순서'라고 밝힘. relation_type BEFORE는 사건 순서를 주장."),
    "REL0024": (SM, "", "INFO", "ATT0093 '자미덕을 잡은 뒤'."),
    "REL0025": (SS, "", "INFO", "구순 집으로 간 뒤 그 집에서 질문."),
    "REL0026": (SS, "", "INFO", "질문-응답(유형상 선후)."),
    "REL0027": (SS, "", "INFO", "질문-응답."),
    "REL0028": (SS, "", "INFO", "붙잡은 뒤 데려감."),
    "REL0029": (MS, ORDER_ONLY, "LOW_REVIEW", "ATT0112에 순서·장소 표지 없음."),
    "REL0030": (SM, "", "INFO", "ATT0113 '신문 뒤'."),
    "REL0031": (SM, "", "INFO", "ATT0114 '이후 매일'."),
    "REL0032": (NI, "발화 내용·지목 행위('거짓 지목')", "HIGH_REVIEW",
                "ATT0119는 '거짓으로 말했다'만 진술. basis '거짓 지목'은 거짓말의 내용을 '지목'으로 특정함(누구를 지목했는지는 없지만, 지목이라는 행위 자체가 원문에 없음). 또한 DURING이 '경위 설명' 행(AT0119)에 붙음."),
    "REL0033": (SS, "", "INFO", "ATT0128 '다시 확인해 보라'."),
    "REL0034": (SM, "", "INFO", "ATT0129 '유제희의 말을 따라'."),
    "REL0035": (SM, "", "INFO", "ATT0130 '재질문에'."),
    "REL0036": (SM, "", "INFO", "ATT0101 '병사의 분부에 따라'."),
    "REL0037": (SM, "", "INFO", "ATT0102 '병사의 분부에 따라'."),
    "REL0038": (SS, "", "INFO", "들른 뒤 '왜 다시 왔느냐'."),
    "REL0039": (SM, "", "INFO", "ATT0105 '구순에게 답했다'."),
    "REL0040": (MS, ORDER_ONLY + "; 반응(응답 관계)", "LOW_REVIEW", "basis '구순 반응'은 ATT0106을 조계완 답변에 대한 반응으로 규정. 원문에 그런 연결 표지 없음."),
    "REL0041": (MS, ORDER_ONLY, "LOW_REVIEW", "ATT0107에 순서 표지 없음."),
    "REL0042": (SS, "", "INFO", "ATT0108 '그 서찰을'."),
    "REL0043": (SM, "", "INFO", "ATT0023 '파직 요청을 윤허'."),
    "REL0044": (SM, "", "INFO", "ATT0024 '나문 요청을 윤허'."),
    "REL0045": (SM, "", "INFO", "ATT0025 '감죄 요청을 윤허'."),
    "REL0046": (MS, "선후 + 판단→명령 연결(근거 암시)", "LOW_REVIEW", "ATT0027에 판단을 근거로 했다는 표지 없음."),
    "REL0047": (MS, "명령을 집행으로 서술('잡아온 뒤')", "LOW_REVIEW", "두 행은 모두 '명령'. basis는 체포가 실제 집행된 것처럼 씀."),
    "REL0048": (MS, "명령을 집행으로 서술('수금 뒤')", "LOW_REVIEW", "두 행 모두 명령."),
    "REL0049": (SS, "", "INFO", "ATT0031 '입시 자리에서'."),
    "REL0050": (MS, "응답 관계(건의→명령)", "LOW_REVIEW", "ATT0049 '파직하도록 했다'는 건의에 대한 응답이라고 말하지 않음."),
    "REL0051": (MS, "근거 관계(비판→파직)", "LOW_REVIEW", "ATT0049에 근거 표지 없음. 같은 명령에 REL0050과 두 개의 선행 근거가 붙음."),
    "REL0052": (SM, "", "INFO", "질문-답변."),
    "REL0053": (MS, "추론 근거('토대로')", "MEDIUM_REVIEW", "ATT0056은 의견만 말함. 그것이 ATT0055의 전언을 토대로 했다는 진술은 없음(원인/근거 추가)."),
    "REL0054": (SS, "", "INFO", "임명 뒤 도착(날짜로 뒷받침)."),
    "REL0055": (SS, "", "INFO", "같은 서계, 도착 뒤 신문."),
    "REL0056": (SM, "", "INFO", "ATT0138 '이동 중 탐문에서는'."),
    "REL0057": (MS, "'재'신문", "LOW_REVIEW", "ATT0062는 '차례로 신문'. '재신문'(앞선 신문 전제)은 원문에 없음."),
    "REL0058": (SM, "", "INFO", "ATT0143 '끝내 단서를 얻지 못했다'."),
    "REL0059": (SM, "", "INFO", "ATT0145 '별도 채탐에서 나온 말들'."),
    "REL0060": (MS, "의안 이름('도난 여부 의안')", "MEDIUM_REVIEW", "ATT0149는 '세 가지 의안'만 말하고 의안 이름이 없음."),
    "REL0061": (MS, "의안 이름('사망원인 의안')", "MEDIUM_REVIEW", "같음."),
    "REL0062": (MS, "의안 이름('지세 호칭 의안')", "MEDIUM_REVIEW", "같음. AT0149 target은 이 의안을 '날조 여부'로 적었는데 연결된 AT0155는 '호칭의 기원' 판단."),
    "REL0063": (MS, "처분의 근거 선택(AT0150)", "MEDIUM_REVIEW", "ATT0160 '감하여 정배'는 어느 판단에 근거했는지 말하지 않음. 같은 날 판단 행(AT0150~AT0159) 중 AT0150을 근거로 고름."),
    "REL0064": (MS, "처분의 근거 선택(AT0166)", "MEDIUM_REVIEW", "ATT0167은 근거를 말하지 않음. AT0162~AT0166 중 AT0166만 연결."),
    "REL0065": (MS, "평가 강화('달랐다'→'오류') + 처분 근거", "MEDIUM_REVIEW", "ATT0171은 장계와 어사 보고가 '크게 달랐다'고만 함. basis '도신 장계 오류 평가'는 잘못의 귀속을 추가."),
    "REL0066": (MS, "'확정' 날짜", "LOW_REVIEW", "AT0068의 날짜(2/22)는 ATT0068에 없음(Audit E AMBIGUOUS). 선후 자체는 AT0065 기준으로 성립 가능."),
    "REL0067": (MS, "'확정' 날짜", "LOW_REVIEW", "AT0092의 2/29는 relation 사슬과 날짜 계산으로 얻은 값이며 ATT0092에 없음."),
    "REL0068": (MS, "'확정' 날짜", "LOW_REVIEW", "AT0101의 3/4는 명령 날짜이며 ATT0101에 집행 날짜 없음. 선후 자체는 성립."),
    "REL0069": (SM, "", "INFO", "두 기록일."),
    "REL0070": (SM, "", "INFO", "두 기록일."),
    "REL0071": (SM, "", "INFO", "두 기록일."),
    "REL0072": (SM, "", "INFO", "두 보고 모두 이웃이라고 함."),
    "REL0073": (MS, "세부 결합('구순의 진영 정소')", "MEDIUM_REVIEW", "명업(ATT0073)은 진영을, 한재욱(ATT0120)은 정소 주체를 말하지 않음. basis는 두 진술의 세부를 합쳐 둘 다 '구순의 진영 정소'를 회고했다고 씀."),
    "REL0074": (SM, "", "INFO", "두 진술을 각각 정확히 요약."),
    "REL0075": (SS, "", "INFO", "'가능성이 높음'으로 유보."),
    "REL0076": (SS, "", "INFO", "'가능성'으로 유보."),
    "REL0077": (MS, "동일성 단정('같은 자미덕 체포')", "MEDIUM_REVIEW", "relation_type은 후보(CANDIDATE)인데 basis는 단정형. 이 연결로 이진욱 진술의 날짜(2/29)가 자미덕 진술 행 8개로 옮겨짐(Audit E)."),
    "REL0078": (SS, "", "INFO", "'특정 1회 동일성은 불명'으로 유보."),
    "REL0079": (SM, "", "INFO", "두 진술을 정확히 요약."),
    "REL0080": (MS, "'사주'라는 규정을 자미덕 주장에 부여", "MEDIUM_REVIEW", "ATT0116은 '회유'. '사주'는 한재욱 부인(ATT0131)의 단어. basis '회유·사주를 주장'은 자미덕이 사주를 주장한 것처럼 씀. type도 회유와 부인된 사주를 '같은 주장된 사건'으로 묶음."),
    "REL0081": (SS, "", "LOW_REVIEW", "basis는 두 명제를 정확히 요약. 단 type 'SAME_ALLEGED_EVENT'는 '지휘'와 '사주'를 같은 사건으로 묶는 틀."),
    "REL0082": (NI, "행위자 동일성(병영 보조자=한재욱)", "HIGH_REVIEW", "ATT0045는 '병영 보조자'라고만 함. 그 보조자가 한재욱이라는 명제는 어떤 attestation에도 없음. 충돌 관계는 이 동일시를 전제로만 성립."),
    "REL0083": (SS, "", "INFO", "둘 다 김명신 사망을 다룸."),
    "REL0084": (SS, "", "INFO", "같은 사망의 서로 다른 서술."),
    "REL0085": (MS, "'직접 사인'", "LOW_REVIEW", "ATT0148 '질병 때문', ATT0151 '전염병에 걸려'. '직접'은 두 명제에 없음."),
    "REL0086": (SS, "", "LOW_REVIEW", "'실제 도난을 인정'에서 '약간의'가 빠짐."),
    "REL0087": (SM, "", "INFO", "둘 다 도난이 실제였다고 판단."),
    "REL0088": (MS, "'지목'(수상하다→지목), 대상 특정(김상제→김명신)", "MEDIUM_REVIEW", "ATT0134는 '풍각 김상제가 매우 수상하다'. 김명신으로 읽는 근거는 ATT0135의 간접 연결뿐이며 '수상하다'를 '지목'으로 강화."),
    "REL0089": (MS, "에피소드 동일성('이름 제공')", "MEDIUM_REVIEW", "ATT0134/0135(유제희): 구순이 말하고 유제희가 기록. ATT0158(정조): 구순이 이름을 적어 주었다. 누가 적었는지의 차이를 '이름 제공 episode'로 덮음."),
    "REL0090": (SS, "", "INFO", "정배 명령과 구체 유배지."),
    "REL0091": (SS, "", "INFO", "같음."),
}


def audit_f(rels, at):
    rows = []
    for r in rels:
        rid = r["relation_id"]
        cls, added, sev, finding = F[rid]
        rows.append({
            "relation_id": rid, "relation_layer": r["relation_layer"], "relation_type": r["relation_type"],
            "confidence": r["confidence"], "from_event_id": r["from_event_id"], "to_event_id": r["to_event_id"],
            "basis_or_rationale": r["basis_or_rationale"],
            "from_proposition": at[r["from_event_id"]]["proposition_ko"],
            "to_proposition": at[r["to_event_id"]]["proposition_ko"],
            "classification": cls, "added_element": added, "finding": finding, "severity": sev,
        })
    return rows


# =====================================================================
# master summary
# =====================================================================
def master(a_rows, b_rows, c_rows, d_rows, e_rows, f_rows):
    out = []
    n = Counter()

    def add(prefix, atype, rtype, rid, sev, finding, ev_ids, action, approval):
        n[prefix] += 1
        out.append({"audit_id": f"{prefix}-{n[prefix]:03d}", "audit_type": atype, "record_type": rtype,
                    "record_id": rid, "severity": sev, "finding": finding, "evidence_ids": ev_ids,
                    "recommended_action": action, "requires_user_approval": approval})

    for r in a_rows:
        if r["classification"] != "CLEAN_EVENT":
            add("A", "EVENT_ATTESTATION_SEPARATION", "event", r["event_id"], r["severity"],
                f"[{r['classification']}/{r['pattern']}] {r['finding']}", r["attestation_id"],
                r["suggested_direction_no_auto_fix"], "YES")
    for r in b_rows:
        if r["classification"] != "ATOMIC":
            add("B", "ATOMICITY_TEMPORAL_LAYERS", "event", r["event_id"], r["severity"],
                f"[{r['classification']}] {r['finding']}", r["linked_relations"],
                "행 분리 또는 시간/장소 필드의 기준 층 명시 여부를 사용자와 결정. 자동 분리 금지.", "YES")
    for r in c_rows:
        if r["classification"] != "SINGLE_ACTOR" and r["severity"] != "INFO":
            add("C", "ACTOR_PARTICIPANT", "event", r["event_id"], r["severity"],
                f"[{r['classification']}] actor='{r['actor']}'. {r['role_or_structure_issue']}", "",
                "actor 값은 유지. 향후 event_participants(event_id, participant, role) 정규화 검토."
                if r["participant_table_needed"] == "YES" else
                "actor 귀속 근거 확인. 근거 없으면 '미상'으로 두는 방향 검토.", "YES")
    for name, ids, finding in ALIAS_FINDINGS:
        add("C", "ACTOR_PARTICIPANT", "alias", name, "MEDIUM_REVIEW", f"[ALIAS_UNRESOLVED] {finding}", ids,
            "동일인 여부를 확인할 수 있는 근거가 생기기 전까지 별개 인물로 취급. 자동 병합 금지.", "YES")
    unknown_cells = sum(1 for r in d_rows if r["person"] != "[SET_DEFINITIONS]"
                        for s, _ in SETS if r[f"{s}_value"] == "UNKNOWN")
    add("D", "PERSON_SET_MEMBERSHIP", "table", "audit_04_person_set_membership", "INFO",
        f"인물 {len(PERSONS)}명 × 집합 {len(SETS)}개 중 UNKNOWN {unknown_cells}칸.", "",
        "UNKNOWN 칸을 추론으로 채우지 말 것.", "NO")
    add("D", "PERSON_SET_MEMBERSHIP", "event", "AT0122", "HIGH_REVIEW",
        "유제희 명단 7명은 AT0122.target_or_content에만 있음. ATT0122는 '여러 사람'이라고만 하고, 변재돌·김성손·김흥득·김흥길은 어떤 attestation에도 없음.",
        "AT0122;AT0135", "명단 이름의 출처를 사용자가 원문으로 확인할 때까지 S1 근거를 EVENT_FIELD_ONLY로 표시.", "YES")
    add("D", "PERSON_SET_MEMBERSHIP", "person", "김명신", "MEDIUM_REVIEW",
        "S5(신문) 충돌: ATT0008 '달포 이상 조사'(이형원) vs ATT0153 '곤장이나 평범한 신문을 받지 않았다'(정조).",
        "AT0008;AT0153", "충돌로 보존. 어느 쪽도 사실로 승격하지 않음.", "NO")
    add("D", "PERSON_SET_MEMBERSHIP", "person", "이집거", "HIGH_REVIEW",
        "이집거는 대질 상대(S8)로만 DIRECT. 명단·체포 명령·체포·구금·신문·지목 근거 없음. 수사 대상이 된 경로를 CSV가 설명하지 않음.",
        "AT0118;AT0119", "이집거를 '큰 도적 지목 대상'이나 '용의자'로 다루는 파생 데이터 생성 금지.", "NO")
    sev_e = {IMP: "MEDIUM_REVIEW", UNS: "MEDIUM_REVIEW", AMB: "LOW_REVIEW"}
    high_e = {("AT0122", "target_or_content"), ("AT0036", "target_or_content"), ("AT0086", "actor"),
              ("AT0087", "actor"), ("AT0010", "historical_place"), ("AT0045", "claim_topic"),
              ("AT0045", "conflict_group"), ("AT0120", "actor"), ("AT0010", "claim_topic"),
              ("AT0010", "conflict_group")}
    for r in e_rows:
        if r["classification"] in (IMP, UNS, AMB):
            if (r["event_id"], r["field"]) in high_e or (r["field"] == "occurrence_lunar_start" and r["event_id"] in
                                                           {"AT0110", "AT0111", "AT0112", "AT0113", "AT0114", "AT0115", "AT0116", "AT0117",
                                                            "AT0006", "AT0007", "AT0008", "AT0009"}):
                sev = "HIGH_REVIEW"
            elif r["field"] == "historical_place" and r["value"] == "한양":
                sev = "LOW_REVIEW"
            else:
                sev = sev_e[r["classification"]]
            add("E", "FIELD_PROVENANCE", "event_field", f"{r['event_id']}.{r['field']}", sev,
                f"[{r['classification']}] {r['field']}='{r['value']}'. {r['explanation']}", r["evidence_ids"],
                "값을 유지하되 근거 출처를 표시하거나, 근거가 없으면 비우는 방향 검토. 자동 수정 금지.", "YES")
    for r in f_rows:
        if r["classification"] in (MS, NI, AMB):
            add("F", "RELATION_MEANING_OVERREACH", "relation", r["relation_id"], r["severity"],
                f"[{r['classification']}] {r['added_element']}: {r['finding']}",
                f"{r['from_event_id']};{r['to_event_id']}",
                "relation은 유지(삭제·병합 금지). basis 문구를 원문 수준으로 낮추거나 type을 후보/서술순서로 표시하는 방향 검토.", "YES")
    return out, unknown_cells


AMB = "AMBIGUOUS"


def main():
    LOGS.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(LOGS / "audit_f_only.log", mode="w", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.setLevel(logging.INFO)
    log.addHandler(fh)
    log.addHandler(sh)

    before = {f: sha(RAW / f) for f in FILES.values()}
    for f, h in before.items():
        log.info("sha256 before %s %s", f, h)

    ev = load("events")
    at = {a["event_id"]: a for a in load("attestations")}
    rels = load("event_relations")
    src = {s["source_record_id"]: s for s in load("source_records")}
    rel_by_event = defaultdict(list)
    for r in rels:
        rel_by_event[r["from_event_id"]].append(r["relation_id"])
        rel_by_event[r["to_event_id"]].append(r["relation_id"])
    assert set(F) == {r["relation_id"] for r in rels}, "every relation must be judged"

    a_rows = audit_a(ev, at)
    write("audit_01_event_attestation_separation.csv", list(a_rows[0]), a_rows)
    b_rows = audit_b(ev, at, rel_by_event)
    write("audit_02_atomicity_temporal_layers.csv", list(b_rows[0]), b_rows)
    c_rows = audit_c(ev)
    write("audit_03_actor_participant_structure.csv", list(c_rows[0]), c_rows)
    d_rows, d_cols, q_rows = audit_d()
    write("audit_04_person_set_membership.csv", d_cols, d_rows)
    write("audit_04_key_questions.csv", list(q_rows[0]), q_rows)
    e_rows = audit_e(ev, at, src)
    write("audit_05_field_level_provenance.csv", list(e_rows[0]), e_rows)
    f_rows = audit_f(rels, at)
    write("audit_06_relation_meaning_overreach.csv", list(f_rows[0]), f_rows)
    m_rows, unknown_cells = master(a_rows, b_rows, c_rows, d_rows, e_rows, f_rows)
    write("audit_master_summary.csv", list(m_rows[0]), m_rows)

    after = {f: sha(RAW / f) for f in FILES.values()}
    for f in FILES.values():
        log.info("sha256 after  %s %s %s", f, after[f], "UNCHANGED" if after[f] == before[f] else "CHANGED")
    assert after == before, "raw CSV changed"

    ca = Counter(r["classification"] for r in a_rows)
    cb = Counter(r["classification"] for r in b_rows)
    cc = Counter(r["classification"] for r in c_rows)
    ce = Counter(r["classification"] for r in e_rows)
    cf = Counter(r["classification"] for r in f_rows)
    cm = Counter(r["severity"] for r in m_rows)
    log.info("A %s", dict(ca))
    log.info("B %s", dict(cb))
    log.info("C %s", dict(cc))
    log.info("D unknown cells %d / %d", unknown_cells, len(PERSONS) * len(SETS))
    log.info("E %s (field rows %d)", dict(ce), len(e_rows))
    log.info("E by field/class %s", dict(Counter((r["field"], r["classification"]) for r in e_rows
                                                  if r["classification"] != D)))
    log.info("F %s", dict(cf))
    log.info("F MORE_SPECIFIC by severity %s", dict(Counter(r["severity"] for r in f_rows if r["classification"] == MS)))
    log.info("master severity %s (rows %d)", dict(cm), len(m_rows))


if __name__ == "__main__":
    main()
