#!/usr/bin/env python3
"""GuSoon v2 atomic proposition normalization (derived layer only).

source_faithful_propositions (raw, P0001~P0117)  →  atomic_propositions (APxxxx)

- Raw CSVs and the raw DuckDB tables are never modified (checked before/after).
- Only rows with split_recommended=YES in output/05 are split; every other
  row is copied 1:1 with its subject/predicate unchanged.
- Split components are written by hand below. Each one may only reuse the
  parent's own wording, date and place; nothing is taken from other rows.
- Identity readings (풍각 김생원 → 김명신, 한가 → 한재욱, ...) are kept out of
  the propositions: surface forms stay as written, candidates go to output/08.
- No events, merges, relations, episodes, DAGs or inference.

Layer conventions
- attestation_depth: length of the speaker chain to the content asserted
  (1 = reporting_actor's own claim, 2 = a speaker embedded in it, 3 = a
  speaker embedded in that). The source record itself is the implicit layer 0.
- claim_level: OUTER_ATTESTATION (depth 1) or EMBEDDED_ATTESTATION (depth >= 2).
  OBJECT_LEVEL_CLAIM is never produced here: every row stays an attestation,
  and whether the attested thing happened is left to a later stage.
- A reported directive/question (not true/false by itself) stays an outer
  attestation of the speech act; its issuer is named in notes.

Outputs:
  output/07_v2_atomic_propositions.csv
  output/08_v2_entity_resolution_candidates.csv
  output/09_v2_open_set_normalized.csv
  output/10_v2_atomic_validation.csv
  logs/v2_atomic_normalization.log
  database/gusun_v2.duckdb: atomic_propositions, entity_resolution_candidates,
                            open_set_normalized (raw tables untouched)
"""

import csv
import hashlib
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
AUDIT_05 = OUT_DIR / "05_v2_proposition_atomicity_audit.csv"
AUDIT_06 = OUT_DIR / "06_v2_open_set_audit.csv"

RAW_TABLES = ["source_records", "source_faithful_propositions", "person_membership", "search_log"]

OUTER = "OUTER_ATTESTATION"
EMB = "EMBEDDED_ATTESTATION"

# Embedded speaker per parent, cleaned of the audit's explanatory suffixes.
EMBEDDED_SPEAKER = {
    "P0003": "구순", "P0008": "회동 조사 응답자들", "P0009": "회동 조사 응답자들",
    "P0010": "회동 조사 응답자들", "P0011": "미상(진술 주체 불명시)", "P0039": "구순",
    "P0043": "변가의 처", "P0048": "나복", "P0049": "나복", "P0060": "한재욱",
    "P0064": "구순", "P0065": "구순 > 도적(자칭)", "P0072": "조계완(본인 과거 발화)",
    "P0073": "구순", "P0080": "한 비장", "P0081": "한 비장", "P0087": "유제희(기록 명단)",
    "P0088": "유제희", "P0090": "유제희", "P0092": "자미덕", "P0096": "구순",
}
DEPTH_OVERRIDE = {"P0065": 3}

# Notes added to 1:1 copies whose layer needs explaining.
COPY_NOTES = {
    "P0018": "'구순 집에 화적이 들었다는 설명'(주체 미명시)은 이조원 판단의 대상일 뿐 이 row가 주장하지 않음.",
    "P0057": "보고된 지시 발화자: 한재욱(지시는 참/거짓 명제가 아님).",
    "P0058": "보고된 지시 발화자: 한재욱(지시는 참/거짓 명제가 아님).",
    "P0066": "보고된 지시 발화자: 이광섭.",
    "P0071": "보고된 질문 발화자: 구순.",
    "P0074": "보고된 요구 발화자: 구순. OPTIONAL이라 미분리.",
    "P0077": "embedded 발화(병영이 자미덕을 도적이라 함) 포함. OPTIONAL이라 미분리.",
    "P0097": "기록에 구순의 '그 말'(P0096)이 포함됨. OPTIONAL이라 미분리.",
}
# 1:1 copies whose raw object_or_content holds a resolved identity rather than
# the surface form in the predicate: keep the surface form here, move the
# identity to output/08.
OBJECT_SURFACE = {
    "P0066": ("풍각 김생원·흥덕 김생원", "김명신·김갑득"),
    "P0096": ("풍각 김상제", "김명신"),
}


def C(role, pred, **kw):
    kw.update(role=role, pred=pred)
    return kw


# Split components for split_recommended=YES rows.
# keys: subj (default parent subject), obj ('inherit' or text, default ''),
#       time/place ('inherit' default or '' to drop), set ('inherit' or 'NA'),
#       level/depth/emb (default from parent), topic/cg (existing vocab only), note
SPLITS = {
    "P0004": [
        C("ARREST", "김명신을 잡았다고 보고됨", obj="inherit", topic="APPREHENSION"),
        C("DETENTION_DURATION", "김명신을 달포 이상 구금했다고 보고됨", obj="inherit"),
        C("INVESTIGATION", "김명신을 조사했다고 보고됨", obj="inherit", topic="INTERROGATION"),
    ],
    "P0006": [
        C("DEATH_OCCURRENCE", "사망했다고 보고됨"),
        C("DEATH_TIMING", "사망이 구금·조사 뒤였다고 보고됨"),
    ],
    "P0007": [
        C("PUNISHMENT_RECEIVED", "모진 형벌을 받았다고 보고됨", subj="평민들"),
        C("INNOCENCE_EVALUATION", "무고했다고 보고됨", subj="형벌을 받은 평민들"),
    ],
    "P0010": [
        C("FRAME_UP", "구순이 김명신에게 도적 괴수 누명을 씌웠다고 진술했다고 보고됨"),
        C("MEANS_SERVANT", "구순이 그 누명을 씌우는 데 행랑 하인을 통했다고 진술했다고 보고됨"),
        C("MEANS_GYOJOL", "구순이 그 누명을 씌우는 데 교졸을 통했다고 진술했다고 보고됨"),
    ],
    "P0012": [
        C("DELEGATION", "수사를 병영 비장에게 전적으로 맡겼다고 평가됨"),
        C("PASSIVITY_EVALUATION", "수사를 방관했다고 평가됨"),
    ],
    "P0013": [
        C("RELIANCE_ON_FALSE_WORDS", "믿은 말이 허황한 말이었다고 평가됨",
          note="05 제안의 (a)믿음 (b)허황성은 '믿은 말이 허황했다'로 함께 둠(믿음 자체는 전제)."),
        C("WRONGFUL_ARREST", "무고한 사람을 잘못 잡았다고 평가됨"),
    ],
    "P0019": [
        C("NEIGHBOR_RELATION", "구순의 이웃으로 살았다고 보고"),
        C("CRITICISM", "구순의 행실을 비판했다고 보고", topic="RELATIONSHIP_CONFLICT"),
    ],
    "P0020": [
        C("GRUDGE", "앙심을 품었다고 주장"),
        C("GRUDGE_CAUSE", "그 앙심이 김명신의 비판 때문이었다고 주장", obj="inherit"),
        C("FRAME_INTENT", "김명신을 모함하려 했다고 주장", obj="inherit"),
    ],
    "P0022": [
        C("TERM_INVENTION", "지세랑이라는 말을 만들었다고 주장"),
        C("TERM_SPREAD", "지세랑이라는 말을 퍼뜨렸다고 주장"),
    ],
    "P0024": [
        C("MARK_NATURE", "부스럼 흔적이었다고 주장", subj="하인의 흔적"),
        C("WOUND_FABRICATION", "하인의 흔적을 창상으로 꾸몄다고 주장"),
    ],
    "P0025": [
        C("DEATH_OCCURRENCE", "죽었다고 주장", place="", topic="DEATH_OCCURRENCE", cg=""),
        C("DEATH_PLACE", "죽은 곳이 병영 옥이었다고 주장", topic="DEATH_OCCURRENCE", cg=""),
        C("DEATH_CAUSE_ATTRIBUTION", "구순이 구성한 죄안 때문에 죽었다고 주장", place=""),
        C("WRONGFUL_DEATH_EVALUATION", "원통하게 죽었다고 주장", place=""),
    ],
    "P0026": [
        C("SPOUSE_DEATH_OCCURRENCE", "죽었다고 보고"),
        C("SPOUSE_DEATH_SEQUENCE", "김명신이 죽은 뒤 따라 죽었다고 보고",
          note="'따라'가 단순 선후인지 인과적 의미인지 미판정(원문 표현 유지)."),
    ],
    "P0027": [
        C("NO_DETAILED_INVESTIGATION", "사건을 자세히 조사하지 않았다고 주장"),
        C("DELEGATION_TO_SUBORDINATE", "사건을 하급 보조자에게 맡겼다고 주장",
          note="하급 보조자의 신원은 미상(08 참조, 동일시하지 않음)."),
    ],
    "P0033": [
        C("NO_DIRECT_ANHAEK", "이조원이 직접 안핵하지 않은 점을 문제 삼음"),
        C("HEARSAY_IN_SEOGYE", "이조원이 전해 들은 말을 서계에 붙인 점을 문제 삼음"),
    ],
    "P0036": [
        C("PRIOR_USAGE", "지세랑 호칭은 예전 호중 화적도 사용한 적이 있다고 말함"),
        C("NOT_NEW_INFERENCE", "지세랑 호칭이 이번에 처음 생긴 말이 아닌 듯하다고 말함"),
    ],
    "P0039": [
        C("ROBBERY_STATEMENT", "도적을 만났다고 말했다고 주장", level=EMB, depth=2, emb="구순",
          topic="THEFT_REALITY", set="NA"),
        C("SUMMON_YEONGGYO", "영교를 불렀다고 주장", set="NA"),
        C("NAMES_WRITTEN", "김명신 등의 이름을 써 주었다고 주장", obj="김명신 등"),
    ],
    "P0040": [
        C("DEATH_OCCURRENCE", "죽었다고 보고"),
        C("DEATH_CAUSE_ILLNESS", "사망 원인이 병이었다고 보고(원문: 병들어 죽었다)",
          topic="DEATH_CAUSE", cg="DEATH_CAUSE"),
        C("DEATH_TIMING", "사망이 체포·구금 뒤였다고 보고"),
    ],
    "P0043": [
        C("INDUCEMENT", "변가의 처를 꾀었다고 주장"),
        C("TESTIMONY_CONTENT", "김명신이 도적 괴수라는 취지의 공초를 냈다고 주장", subj="변가의 처",
          level=EMB, depth=2, emb="변가의 처", topic="SUSPECT_IDENTIFICATION", cg=""),
        C("INDUCED_TESTIMONY", "변가의 처를 꾀어 그 공초를 내게 했다고 주장"),
    ],
    "P0049": [
        C("THIEVES_ENTERED", "도적이 들어왔다고 말했다고 진술됨"),
        C("THIEF_COUNT", "들어온 도적이 30여 명이었다고 말했다고 진술됨"),
        C("TORCHES", "도적이 횃불을 들고 들어왔다고 말했다고 진술됨"),
        C("SELF_DESIGNATION", "도적이 지세대감이라 자칭했다고 말했다고 진술됨", depth=3,
          emb="나복 > 도적(자칭)", topic="JISE_ORIGIN", cg="JISE_ORIGIN"),
        C("THEFT_OF_GOODS", "도적이 돈과 물품을 훔쳤다고 말했다고 진술됨"),
    ],
    "P0053": [
        C("COMPLAINT_FILED", "소장을 올렸다고 진술", topic="COMPLAINT"),
        C("ARREST_ORDER_FROM_COMPLAINT", "그 소장으로 체포령이 내려졌다고 진술"),
    ],
    "P0055": [
        C("INITIAL_TRUTHFUL_TESTIMONY", "병영 뜰 공초에서 처음에는 사실대로 말했다고 진술"),
        C("FEAR_OF_THREAT", "위협이 두려웠다고 진술", place=""),
        C("TESTIMONY_CHANGED", "도적이 없었다는 취지로 진술을 바꾸었다고 진술", obj="도적이 없었다는 취지"),
        C("CHANGE_CAUSE", "위협이 두려워 진술을 바꾸었다고 진술", place=""),
    ],
    "P0060": [
        C("KINSHIP", "변지돌과 정원돌이 처남매부 사이라고 말했다고 진술", level=EMB, depth=2, emb="한재욱",
          topic="IDENTITY_RELATION"),
        C("STRENGTH", "변지돌이 힘이 세다고 말했다고 진술", level=EMB, depth=2, emb="한재욱"),
        C("CAUTION_DIRECTIVE", "조심하라고 말했다고 진술", level=OUTER, depth=1, emb="",
          note="보고된 지시 발화자: 한재욱(주의 지시는 참/거짓 명제가 아님)."),
    ],
    "P0062": [
        C("APPREHENSION", "자미덕을 잡았다고 진술", obj="inherit"),
        C("ONLY_JAMIDEOK", "잡은 사람이 자미덕뿐이었다고 진술", obj="inherit"),
        C("KINSHIP_WIFE_OF_JAEDOL", "재돌의 처라고 진술", subj="자미덕", time="", set="NA",
          topic="IDENTITY_RELATION"),
        C("KINSHIP_BROTHER_OF_BYEONJIDOL", "변지돌의 아우라고 진술", subj="재돌", time="", set="NA",
          topic="IDENTITY_RELATION"),
    ],
    "P0081": [
        C("CONDITION", "'정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적들이라고 말하면'이라는 조건을 말했다고 진술",
          note="명시 구성원 5명 + '등'(open set). 조건문의 앞부분이며 명령·지목 요구로 바꾸지 않음."),
        C("RELEASE_PROMISE", "그 조건을 충족하면 자미덕과 남편을 다음 날 석방하겠다고 말했다고 진술", set="NA",
          note="조건문의 뒷부분. 수혜자(자미덕·남편)는 대상 명단 구성원이 아님."),
    ],
    "P0084": [
        C("FALSE_STATEMENT_ADMISSION", "이집거와 대질할 때 자신이 거짓으로 꾸며 말했다고 진술",
          note="거짓 발언의 구체 내용·대상은 원문에 없으므로 생성하지 않음."),
        C("DIRECTED_BY_HAN_BIJANG", "그 거짓 발언이 한 비장의 지휘에 따른 것이었다고 진술"),
    ],
    "P0086": [
        C("DISPATCH", "병영 아전 유제희를 내보냈다고 진술", obj="inherit"),
        C("DISPATCH_PURPOSE", "유제희를 내보낸 목적이 도적 진상 탐지였다고 진술", obj="inherit"),
    ],
    "P0089": [
        C("CALLED_INTO_ROOM", "자미덕을 방안으로 불렀다고 인정", obj="inherit"),
        C("GAVE_LEFTOVER_RICE", "자미덕에게 남은 밥을 주었다고 인정", obj="inherit"),
    ],
    "P0090": [
        C("SEOKDAN_TESTIMONY_REPORT", "석단 공초에서 김명신이 도적 괴수라고 했다고 말했다고 진술됨",
          depth=3, emb="유제희 > 석단(공초)"),
        C("REASK_SUGGESTION", "자미덕에게 다시 물어보라고 말했다고 진술됨", level=OUTER, depth=1, emb="",
          topic="INTERROGATION",
          note="보고된 권유 발화자: 유제희(권유는 참/거짓 명제가 아님)."),
    ],
    "P0091": [
        C("REASKED", "자미덕에게 다시 물었다고 진술", obj="inherit"),
        C("REASK_BASIS", "다시 물은 것이 유제희 말에 따른 것이었다고 진술", obj="inherit"),
    ],
    "P0101": [
        C("EXAGGERATION", "과장했다고 평가", subj="구순"),
        C("FALSE_REPORT", "거짓 보고를 했다고 평가", subj="아전",
          note="'아전'은 이 row에서 특정되지 않음(08 참조)."),
        C("BELIEVED", "구순의 과장과 아전의 거짓 보고를 믿었다고 평가"),
        C("NO_STOLEN_GOODS", "장물이 없는 상태에서 판단했다고 평가", topic="EVIDENCE"),
        C("JUDGED_BIG_THIEVES", "큰 도적으로 판단했다고 평가"),
    ],
    "P0103": [
        C("NO_GOODS_SECURED", "장물부터 확보하지 않았다고 평가"),
        C("ARRESTED_COMMONERS", "장교·나졸을 풀어 평민을 잡았다고 평가"),
        C("BIJANG_DIRECTION", "병영 비장의 지휘가 있었다고 평가", subj="병영 비장",
          note="병영 비장은 이 row에서 특정되지 않음(08 참조)."),
        C("CHARGES_PER_DIRECTION", "병영 비장 지휘대로 죄를 얽었다고 평가"),
    ],
    "P0106": [
        C("KIM_CAUSE_EPIDEMIC", "김명신이 전염병에 걸려 죽은 것으로 판단"),
        C("WIFE_CAUSE_EPIDEMIC", "김명신 부처 중 처가 전염병에 걸려 죽은 것으로 판단",
          note="원문 '김명신 부처'의 처 쪽. P0026과 해석이 다를 수 있음(관계는 만들지 않음)."),
    ],
    "P0107": [
        C("NOT_BEATEN", "김명신이 곤장을 맞지 않았다고 판단"),
        C("NOT_INTERROGATED", "김명신이 평범한 신문도 받지 않았다고 판단"),
    ],
}

# surface_form, candidate, source_prop_ids, status, basis, confidence, review
ENTITY_RESOLUTION = [
    ("풍각 김생원", "김명신", "P0066|P0067|P0070", "DIRECTLY_IDENTIFIED_IN_SOURCE",
     "P0067(SRC2_006): '풍각 김생원, 김명신으로 식별됨'. 식별 문장이 이진욱 진술인지 기사 서술인지는 CSV에서 불명.", "HIGH", True),
    ("흥덕 김생원", "김갑득", "P0066|P0068", "DIRECTLY_IDENTIFIED_IN_SOURCE",
     "P0068(SRC2_006): '흥덕 김생원, 김갑득으로 식별됨'. 식별 주체는 P0067과 같은 문제.", "HIGH", True),
    ("풍각 김상제", "김명신", "P0096", "STRONGLY_SUPPORTED",
     "같은 기록(SRC2_006)에서 '풍각'+김씨가 P0067의 풍각 김생원=김명신과 맞고, 상제(상중인 사람) 표현이 P0072 '풍각의 상주'와 부합. "
     "source가 김상제=김명신을 직접 말하지는 않음. raw object_or_content만 '김명신'으로 해소.", "MEDIUM", True),
    ("풍각의 상주", "김명신", "P0072", "STRONGLY_SUPPORTED",
     "같은 진술자(조계완)의 P0070 '풍각 김생원을 잡으러 가는 길'과 같은 장면이며 P0067에서 풍각 김생원=김명신. 직접 동일시는 없음.",
     "MEDIUM", True),
    ("원돌", "정원돌", "P0097", "STRONGLY_SUPPORTED",
     "'원돌'이 정원돌의 이름 부분과 같고, 같은 유제희 명단을 다룬 P0087에 정원돌이 명시. 직접 동일시는 없음. raw named_entities만 '정원돌'로 해소.",
     "MEDIUM", True),
    ("한가(병영 비장 한가)", "한재욱", "P0113", "STRONGLY_SUPPORTED",
     "같은 기록(SRC2_006) 처분문. 한재욱은 병영 측에서 유제희를 내보내고(P0086) 자미덕을 방에 불러 밥을 준 것을 인정(P0089)했고 성씨가 일치. "
     "source가 한가=한재욱을 직접 말하지 않음. raw named_entities만 '한재욱'으로 해소.", "MEDIUM", True),
    ("한 비장", "한재욱", "P0079|P0080|P0081|P0082|P0084", "CANDIDATE",
     "자미덕이 말한 한 비장의 행위(방으로 불러들임·떡과 밥)가 한재욱의 부분 인정(P0089)과 겹침. "
     "그러나 '한 비장'이 성씨 한(韓)인지 '어떤 비장'인지 CSV만으로 불확정.", "MEDIUM", True),
    ("한 비장", "한가(P0113의 병영 비장 한가)", "P0079|P0080|P0081|P0082|P0084|P0113", "CANDIDATE",
     "둘 다 '비장'이며 '한'이 붙음. P0113 notes가 연결을 언급하나 처분문 표현은 '한가'.", "MEDIUM", True),
    ("재돌", "변재돌", "P0062|P0075|P0080", "STRONGLY_SUPPORTED",
     "P0062: 재돌=변지돌의 아우(형제이므로 성씨 변 추정). P0087 명단에 변지돌·변재돌이 나란히 기재. 직접 동일시 없음(person_membership도 별도 검토로 둠).",
     "MEDIUM", True),
    ("남편(자미덕과 남편)", "재돌", "P0081", "DIRECTLY_IDENTIFIED_IN_SOURCE",
     "P0080 '자미덕의 남편 재돌', P0062 '재돌의 처 자미덕'(같은 기록 SRC2_006).", "HIGH", False),
    ("변가의 처", "자미덕", "P0043", "CANDIDATE",
     "지지: 자미덕은 변지돌의 아우 재돌의 처(P0062)라 '변가의 처'에 해당할 수 있고, 한재욱 관련 회유 주장(P0081 등)과 주제가 겹침. "
     "반대: 다른 기록(SRC2_005 윤노동 별단)이며, P0081 명시 목록에 김명신이 없고 P0092는 '모른다' 응답. 변지돌의 처 등 다른 '변가의 처' 가능성 배제 불가.",
     "LOW", True),
    ("병영의 하급 보조자", "한재욱", "P0027|P0028", "UNRESOLVED",
     "동일시할 직접·간접 근거 없음(P0028 notes도 동일시하지 않음).", "NONE", True),
    ("병영의 하급 보조자", "유제희", "P0027|P0028", "UNRESOLVED",
     "유제희가 병영 아전(P0086)이라는 점 외에 근거 없음.", "NONE", True),
    ("아전(아전의 거짓 보고)", "유제희", "P0101", "CANDIDATE",
     "유제희가 병영 아전으로 명단을 적어 올림(P0086·P0087·P0097). 다른 아전 배제 불가.", "MEDIUM", True),
    ("병영 비장(병영 비장 지휘)", "한가(P0113의 병영 비장 한가)", "P0103", "CANDIDATE",
     "같은 기록(SRC2_006)에서 처분 대상이 '병영 비장 한가'. 이 row의 비장은 이름이 없음.", "LOW", True),
    ("병영 비장(수사를 병영 비장에게 맡김)", "한가(P0113의 병영 비장 한가)", "P0012", "UNRESOLVED",
     "다른 기록(SRC2_001 이형원 장계)이며 비장 이름 없음. 연결 근거 없음.", "NONE", True),
    ("병사", "이광섭", "P0069|P0074", "STRONGLY_SUPPORTED",
     "같은 기록(SRC2_006)의 P0066에 '병사 이광섭'이라는 동격 표현이 있음. 이 두 row 자체는 '병사'만 씀.", "HIGH", False),
    ("병사", "이광섭", "P0027", "STRONGLY_SUPPORTED",
     "다른 기록(SRC2_002 이조원)이지만 같은 사건에서 병사로 불린 인물은 P0066의 '병사 이광섭'; P0013도 이광섭의 체포 판단을 다룸.", "MEDIUM", True),
    ("장교 일행", "이진욱 등 장교", "P0063", "STRONGLY_SUPPORTED",
     "같은 진술자(이진욱)가 P0062에서 '이진욱 등 장교'가 자미덕을 잡았다고 한 뒤 이어서 '장교 일행'이 자미덕을 데리고 감. 집단 동일성은 직접 진술되지 않음.",
     "MEDIUM", True),
    ("장교 일행", "이진욱 등 장교", "P0069", "CANDIDATE",
     "같은 진술자(이진욱)지만 다른 날짜(3월 4일)의 체포. 구성원이 같다는 근거 없음.", "LOW", True),
]

UNENUMERATED_GROUPS = {"P0007", "P0008", "P0009", "P0010", "P0011", "P0041", "P0046", "P0063", "P0069"}

log = logging.getLogger("v2_atomic")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv_dicts(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def table_digest(con, table):
    cols = [c[0] for c in con.execute(f"DESCRIBE {table}").fetchall()]
    rows = con.execute(f"SELECT * FROM {table} ORDER BY ALL").fetchall()
    return hashlib.sha256(repr((cols, rows)).encode("utf-8")).hexdigest()


def surface_forms(text, lexicon):
    """Longest-match scan so that '정원돌' does not also yield '원돌'."""
    found, i = [], 0
    while i < len(text):
        for term in lexicon:
            if text.startswith(term, i):
                if term not in found:
                    found.append(term)
                i += len(term)
                break
        else:
            i += 1
    return found


def main():
    OUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "v2_atomic_normalization.log", mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    checks = []  # check_id, description, severity, status, detail

    def check(cid, desc, ok, detail="", fail_severity="ERROR"):
        checks.append([cid, desc, "PASS" if ok else fail_severity, detail])
        if not ok:
            log.error("%s %s: %s", cid, desc, detail)

    # ---- raw integrity before ----
    expected_sha = {}
    for line in SHA_PATH.read_text(encoding="utf-8").splitlines():
        h, fn = line.split("  ", 1)
        expected_sha[fn] = h
    raw_sha_ok = all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items())
    if not raw_sha_ok:
        log.error("Raw CSV differs from recorded SHA-256; stopping")
        sys.exit(1)

    con = duckdb.connect(str(DB_PATH))
    digests_before = {t: table_digest(con, t) for t in RAW_TABLES}

    cur = con.execute("SELECT * FROM source_faithful_propositions ORDER BY prop_id")
    cols = [d[0] for d in cur.description]
    props = [{c: ("" if v is None else v) for c, v in zip(cols, row)} for row in cur.fetchall()]
    by_id = {p["prop_id"]: p for p in props}
    membership_people = [r[0] for r in con.execute("SELECT person FROM person_membership").fetchall()]

    audit05 = {r["prop_id"]: r for r in read_csv_dicts(AUDIT_05)}
    audit06 = {r["prop_id"]: r for r in read_csv_dicts(AUDIT_06)}
    yes_ids = {pid for pid, r in audit05.items() if r["split_recommended"] == "YES"}
    if yes_ids != set(SPLITS):
        log.error("SPLITS keys differ from 05 split YES rows: missing=%s extra=%s",
                  sorted(yes_ids - set(SPLITS)), sorted(set(SPLITS) - yes_ids))
        sys.exit(1)

    topics = {p["claim_topic"] for p in props}
    groups = {p["conflict_group"] for p in props}
    set_values = {p["set_status"] for p in props}

    def norm_set(pid):
        return audit06[pid]["set_status_recommended"] if pid in audit06 else by_id[pid]["set_status"]

    # Entity lexicon: names in raw named_entities, membership and actors, plus
    # surface forms whose normalization differs.
    lexicon = set(membership_people)
    for p in props:
        lexicon.update(x for x in p["named_entities"].split("|") if x)
        lexicon.update(x for x in p["reporting_actor"].split("/") if x)
    lexicon.update(["변가의 처", "한 비장", "한가", "풍각 김생원", "흥덕 김생원", "풍각 김상제", "풍각의 상주",
                    "원돌", "재돌", "병영의 하급 보조자", "하급 보조자", "김명신의 아내", "김명신 부처",
                    "영교", "아전", "병영 비장", "병사", "장교 일행", "남편", "석단", "나복", "명업"])
    lexicon = sorted(lexicon, key=len, reverse=True)

    # ---- build atomic rows ----
    atomic = []
    n = 0

    def emit(parent, comp, role, level, depth, emb, subj, pred, obj, time, prec, place, pstat,
             topic, cg, set_status, group, derivation, notes):
        nonlocal n
        n += 1
        text = " ".join([subj, pred, obj])
        atomic.append(dict(
            atomic_prop_id=f"AP{n:04d}", parent_prop_id=parent["prop_id"], split_component=comp,
            component_role=role, derivation=derivation,
            source_record_id=parent["source_record_id"], record_lunar_date=parent["record_lunar_date"],
            reporting_actor=parent["reporting_actor"], attestation_mode=parent["attestation_mode"],
            claim_level=level, attestation_depth=depth, outer_speaker=parent["reporting_actor"],
            embedded_speaker=emb, subject_surface=subj, predicate=pred, object_or_content=obj,
            occurrence_lunar_text=time, occurrence_precision=prec, historical_place=place,
            place_status=pstat, epistemic_scope=parent["epistemic_scope"], claim_topic=topic,
            conflict_group=cg, set_status=set_status, shared_utterance_group=group,
            directness=parent["directness"], entity_surface_forms="|".join(surface_forms(text, lexicon)),
            notes=notes,
        ))

    for p in props:
        pid = p["prop_id"]
        a = audit05[pid]
        base_level = EMB if a["object_level_event_claim_present"] == "EMBEDDED_ONLY" and pid != "P0097" else OUTER
        base_depth = DEPTH_OVERRIDE.get(pid, 2) if base_level == EMB else 1
        base_emb = EMBEDDED_SPEAKER.get(pid, "") if base_level == EMB else ""
        set_note = ""
        if norm_set(pid) != p["set_status"]:
            set_note = f"set_status 정규화: raw {p['set_status']} → {norm_set(pid)} (06 근거)."

        if pid not in SPLITS:
            obj, obj_note = p["object_or_content"], ""
            if pid in OBJECT_SURFACE:
                obj, resolved = OBJECT_SURFACE[pid]
                obj_note = (f"object_or_content: raw 값 '{resolved}'는 신원 해소 결과이므로 predicate의 surface form "
                            f"'{obj}'로 둠(08 참조).")
            notes = " ".join(x for x in [p["notes"], COPY_NOTES.get(pid, ""), set_note, obj_note] if x)
            emit(p, "1:1", "", base_level, base_depth, base_emb, p["subject"], p["predicate"], obj,
                 p["occurrence_lunar_text"], p["occurrence_precision"], p["historical_place"], p["place_status"],
                 p["claim_topic"], p["conflict_group"], norm_set(pid), "", "COPY", notes)
            continue

        group = f"UG_{pid}"
        for i, c in enumerate(SPLITS[pid]):
            comp = f"{pid}-{chr(ord('a') + i)}"
            level = c.get("level", base_level)
            depth = c.get("depth", base_depth if level == base_level else (1 if level == OUTER else 2))
            emb = c.get("emb", base_emb if level == base_level else "")
            obj = p["object_or_content"] if c.get("obj") == "inherit" else c.get("obj", "")
            keep_time = c.get("time", "inherit") == "inherit"
            keep_place = c.get("place", "inherit") == "inherit"
            set_status = "NOT_APPLICABLE" if c.get("set") == "NA" else norm_set(pid)
            notes = " ".join(x for x in [
                f"{pid}에서 분리({comp}, {c['role']}).", p["notes"], c.get("note", ""),
                set_note if set_status != "NOT_APPLICABLE" else ""] if x)
            emit(p, comp, c["role"], level, depth, emb, c.get("subj", p["subject"]), c["pred"], obj,
                 p["occurrence_lunar_text"] if keep_time else "",
                 p["occurrence_precision"] if keep_time else "UNSPECIFIED",
                 p["historical_place"] if keep_place else "",
                 p["place_status"] if keep_place else "UNSPECIFIED",
                 c.get("topic", p["claim_topic"]), c.get("cg", p["conflict_group"]), set_status, group,
                 "SPLIT", notes)

    # ---- 08 entity resolution ----
    er_rows = [[sf, cand, ids, status, basis, conf, "YES" if rev else "NO"]
               for sf, cand, ids, status, basis, conf, rev in ENTITY_RESOLUTION]

    # ---- 09 open sets ----
    a_set = set(audit06["P0081"]["explicit_members"].split("|"))
    b_set = set(audit06["P0087"]["explicit_members"].split("|"))
    os_rows = []
    for pid in sorted(audit06):
        r = audit06[pid]
        if r["set_status_recommended"] == "NOT_APPLICABLE":
            log.info("Open-set audit row %s not normalized as a person set (%s)", pid, r["notes"])
            continue
        carriers = [x["atomic_prop_id"] for x in atomic
                    if x["parent_prop_id"] == pid and x["set_status"] != "NOT_APPLICABLE"]
        members = r["explicit_members"]
        if pid in UNENUMERATED_GROUPS:
            marker = "복수 집단 표현(비열거)"
            interp = ("MEMBERSHIP_UNKNOWN_FOR_ALL_INDIVIDUALS: 구성원이 열거되지 않았으므로 어떤 개인도 "
                      "이 row만으로 구성원·비구성원으로 판정하지 않음.")
        else:
            marker = "등"
            interp = ("EXPLICIT_MEMBERS_PLUS_UNLISTED: 명시 구성원은 이 진술상 구성원이고, '등'이 있으므로 "
                      "명시되지 않은 인물의 구성원 여부는 미정(비구성원으로 해석하지 않음). "
                      "구성원이라는 것은 진술 내용일 뿐 실제 행위 여부를 뜻하지 않음.")
        notes = r["notes"]
        if pid == "P0081":
            notes += (f" 이 집합에만 명시: {'·'.join(sorted(a_set - b_set))} — 유제희 명단(P0087)에 명시되지 않았다는 것이 "
                      f"그 명단의 비구성원이라는 뜻은 아님.")
        if pid == "P0087":
            notes += (f" 이 집합에만 명시: {'·'.join(sorted(b_set - a_set))} — 자미덕 진술 대상(P0081)에 명시되지 않았다는 것이 "
                      f"그 대상의 비구성원이라는 뜻은 아님.")
        os_rows.append([f"OS{len(os_rows) + 1:02d}", pid, "|".join(carriers), r["set_description"], members,
                        marker, "TRUE", interp, notes])

    # ---- validation ----
    raw_ids = {p["prop_id"] for p in props}
    children = {}
    for x in atomic:
        children.setdefault(x["parent_prop_id"], []).append(x)

    bad_parent = [x["atomic_prop_id"] for x in atomic if x["parent_prop_id"] not in raw_ids]
    check("A", "모든 atomic의 parent_prop_id가 P0001~P0117 중 하나", not bad_parent, "|".join(bad_parent))

    orphan = sorted(raw_ids - set(children))
    check("B", "117개 raw proposition 모두 최소 1개 atomic에 연결", not orphan and len(raw_ids) == 117,
          f"raw={len(raw_ids)} orphan={'|'.join(orphan)}")

    under = [pid for pid in yes_ids if len(children.get(pid, [])) < 2]
    check("C", "split YES 33건이 각각 2개 이상의 atomic을 가짐", not under and len(yes_ids) == 33,
          f"yes={len(yes_ids)} under={'|'.join(sorted(under))}")

    not_split = [pid for pid, r in audit05.items() if r["split_recommended"] in ("OPTIONAL", "REVIEW")]
    auto_split = [pid for pid in not_split if len(children[pid]) != 1
                  or children[pid][0]["predicate"] != by_id[pid]["predicate"]
                  or children[pid][0]["subject_surface"] != by_id[pid]["subject"]]
    check("D", "OPTIONAL/REVIEW row가 분리·변경되지 않음", not auto_split,
          f"optional_review={len(not_split)} changed={'|'.join(auto_split)}")

    date_re = re.compile(r"\d{4}|\d+월|\d+일")
    # whole place values and their parts ('청주 덕평' → '덕평'), skipping generic '집'
    place_terms = set()
    for q in props:
        if q["historical_place"]:
            place_terms.add(q["historical_place"])
            place_terms.update(w for w in q["historical_place"].split() if len(w) > 1 and w != "구순")
    e_issues = []
    for x in atomic:
        p = by_id[x["parent_prop_id"]]
        parent_text = " ".join([p["subject"], p["predicate"], p["object_or_content"]])
        child_text = " ".join([x["subject_surface"], x["predicate"], x["object_or_content"]])
        for name in surface_forms(child_text, lexicon):
            if name not in parent_text:
                e_issues.append(f"{x['atomic_prop_id']}:인물 '{name}'")
        for d in date_re.findall(child_text):
            if d not in parent_text:
                e_issues.append(f"{x['atomic_prop_id']}:날짜 '{d}'")
        if x["occurrence_lunar_text"] not in ("", p["occurrence_lunar_text"]):
            e_issues.append(f"{x['atomic_prop_id']}:occurrence")
        if x["historical_place"] not in ("", p["historical_place"]):
            e_issues.append(f"{x['atomic_prop_id']}:place")
        for place in place_terms:
            if place in child_text and place not in parent_text:
                e_issues.append(f"{x['atomic_prop_id']}:장소 '{place}'")
    check("E", "부모에 없는 인물·날짜·장소가 추가되지 않음", not e_issues, "|".join(e_issues))

    p81 = children["P0081"]
    cond = [x for x in p81 if x["component_role"] == "CONDITION"]
    explicit = ["정원돌", "이집거", "김갑득", "김성손", "김흥득"]
    f_ok = (len(cond) == 1 and all(m in cond[0]["predicate"] for m in explicit) and "등" in cond[0]["predicate"]
            and cond[0]["set_status"] == "OPEN_SET_EXPLICIT_MEMBERS"
            and len({x["shared_utterance_group"] for x in p81}) == 1 and p81[0]["shared_utterance_group"]
            and all(x["claim_level"] == EMB and x["embedded_speaker"] == "한 비장" for x in p81)
            and not any(w in x["predicate"] for x in p81 for w in ("명령", "지목", "요구"))
            and any(r[1] == "P0081" and r[4] == "|".join(explicit) and r[6] == "TRUE" for r in os_rows))
    check("F", "P0081 open set·조건/약속 분리·shared_utterance_group 보존", f_ok,
          f"group={p81[0]['shared_utterance_group']} components={len(p81)}")

    p84 = children["P0084"]
    g_bad = [x["atomic_prop_id"] for x in p84
             if any(w in x["predicate"] + x["object_or_content"] for w in ("지목", "이집거를", "이집거가", "도적"))
             or x["object_or_content"]]
    check("G", "P0084에서 거짓 지목 등 새 내용이 생성되지 않음", not g_bad and len(p84) == 2, "|".join(g_bad))

    p43 = children["P0043"]
    h_bad = [x["atomic_prop_id"] for x in p43
             if "자미덕" in " ".join([x["subject_surface"], x["predicate"], x["object_or_content"], x["embedded_speaker"]])
             or "변가의 처" not in x["entity_surface_forms"]]
    er_43 = [r for r in er_rows if r[0] == "변가의 처" and r[1] == "자미덕"]
    h_ok = not h_bad and len(er_43) == 1 and er_43[0][3] != "DIRECTLY_IDENTIFIED_IN_SOURCE"
    check("H", "P0043에서 '변가의 처 = 자미덕'이 확정되지 않음", h_ok,
          f"rows={len(p43)} er_status={er_43[0][3] if er_43 else 'missing'}")

    # supplementary checks
    copies = [x for x in atomic if x["derivation"] == "COPY"]
    copy_changed = [x["atomic_prop_id"] for x in copies
                    if x["predicate"] != by_id[x["parent_prop_id"]]["predicate"]
                    or x["subject_surface"] != by_id[x["parent_prop_id"]]["subject"]]
    check("I1", "1:1 copy의 subject/predicate가 부모와 동일", not copy_changed, "|".join(copy_changed))
    obj_changed = sorted(x["parent_prop_id"] for x in copies
                         if x["object_or_content"] != by_id[x["parent_prop_id"]]["object_or_content"])
    checks.append(["I2", "1:1 copy object_or_content 변경은 surface form 복원(OBJECT_SURFACE)뿐",
                   "PASS" if set(obj_changed) == set(OBJECT_SURFACE) else "ERROR",
                   "변경=" + "|".join(obj_changed)])
    lvl_bad = [x["atomic_prop_id"] for x in atomic
               if (x["claim_level"] == OUTER and (x["attestation_depth"] != 1 or x["embedded_speaker"]))
               or (x["claim_level"] == EMB and (x["attestation_depth"] < 2 or not x["embedded_speaker"]))
               or x["claim_level"] not in (OUTER, EMB)]
    check("I3", "claim_level·attestation_depth·embedded_speaker 정합", not lvl_bad, "|".join(lvl_bad))
    vocab_bad = [x["atomic_prop_id"] for x in atomic
                 if x["claim_topic"] not in topics or x["conflict_group"] not in groups
                 or x["set_status"] not in set_values]
    check("I4", "claim_topic·conflict_group·set_status가 기존 vocabulary 안의 값", not vocab_bad, "|".join(vocab_bad))
    ug_bad = [pid for pid in SPLITS if len({x["shared_utterance_group"] for x in children[pid]}) != 1]
    check("I5", "분리된 부모의 자식들이 하나의 shared_utterance_group을 공유", not ug_bad, "|".join(ug_bad))
    direct_bad = []
    for sf, cand, ids, status, basis, _, _ in ENTITY_RESOLUTION:
        for pid in ids.split("|"):
            if pid not in raw_ids:
                direct_bad.append(f"{sf}:{pid} 없음")
        if status == "DIRECTLY_IDENTIFIED_IN_SOURCE":
            core = sf.split("(")[0]
            basis_ids = re.findall(r"P\d{4}", basis)
            if not any(core in " ".join([by_id[b]["subject"], by_id[b]["predicate"]]) and
                       cand in " ".join([by_id[b]["subject"], by_id[b]["predicate"]]) for b in basis_ids):
                direct_bad.append(f"{sf}→{cand}: 근거 row에 직접 동일시 문장 없음")
    check("I6", "DIRECT 판정은 근거 row에 surface form과 후보가 함께 기재된 경우만", not direct_bad, "|".join(direct_bad))
    resolved_leak = [x["atomic_prop_id"] for x in atomic if x["parent_prop_id"] in ("P0066", "P0096")
                     and "김명신" in x["object_or_content"]]
    check("I7", "식별 결과가 atomic object에 선반영되지 않음(P0066·P0096)", not resolved_leak, "|".join(resolved_leak))
    obj_level = [x for x in atomic if x["claim_level"] == "OBJECT_LEVEL_CLAIM"]
    checks.append(["I8", "OBJECT_LEVEL_CLAIM row 미생성(역사적 사실 승격 없음)",
                   "PASS" if not obj_level else "ERROR", f"count={len(obj_level)}"])
    review_n = sum(1 for r in er_rows if r[6] == "YES")
    checks.append(["I9", "entity resolution 수동 검토 필요 행", "INFO", f"{review_n}/{len(er_rows)}"])

    # ---- write CSVs ----
    atomic_cols = ["atomic_prop_id", "parent_prop_id", "split_component", "component_role", "derivation",
                   "source_record_id", "record_lunar_date", "reporting_actor", "attestation_mode",
                   "claim_level", "attestation_depth", "outer_speaker", "embedded_speaker",
                   "subject_surface", "predicate", "object_or_content", "occurrence_lunar_text",
                   "occurrence_precision", "historical_place", "place_status", "epistemic_scope",
                   "claim_topic", "conflict_group", "set_status", "shared_utterance_group", "directness",
                   "entity_surface_forms", "notes"]
    er_cols = ["surface_form", "candidate_entity", "source_prop_ids", "resolution_status", "basis",
               "confidence", "manual_review_required"]
    os_cols = ["set_id", "parent_prop_id", "atomic_prop_ids", "set_description", "explicit_members",
               "open_marker", "is_open", "membership_interpretation", "notes"]
    write_csv(OUT_DIR / "07_v2_atomic_propositions.csv", atomic_cols,
              [[x[c] for c in atomic_cols] for x in atomic])
    write_csv(OUT_DIR / "08_v2_entity_resolution_candidates.csv", er_cols, er_rows)
    write_csv(OUT_DIR / "09_v2_open_set_normalized.csv", os_cols, os_rows)

    # ---- DuckDB derived tables (raw tables untouched) ----
    for table, path in [("atomic_propositions", "07_v2_atomic_propositions.csv"),
                        ("entity_resolution_candidates", "08_v2_entity_resolution_candidates.csv"),
                        ("open_set_normalized", "09_v2_open_set_normalized.csv")]:
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv(?, header=true, "
                    f"all_varchar=true, quote='\"', escape='\"')", [str(OUT_DIR / path)])
    db_counts = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                 for t in ("atomic_propositions", "entity_resolution_candidates", "open_set_normalized")}
    check("J1", "derived table 행 수가 CSV와 일치",
          db_counts == {"atomic_propositions": len(atomic), "entity_resolution_candidates": len(er_rows),
                        "open_set_normalized": len(os_rows)}, str(db_counts))
    digests_after = {t: table_digest(con, t) for t in RAW_TABLES}
    con.close()
    changed = [t for t in RAW_TABLES if digests_before[t] != digests_after[t]]
    check("J2", "DuckDB raw table 4개 내용 불변", not changed, "|".join(changed))
    check("J3", "raw CSV SHA-256 불변",
          all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items()), "")

    write_csv(OUT_DIR / "10_v2_atomic_validation.csv", ["check_id", "description", "severity", "detail"], checks)

    # ---- summary ----
    n_err = sum(1 for c in checks if c[2] == "ERROR")
    n_warn = sum(1 for c in checks if c[2] == "WARNING")
    log.info("raw propositions: %d", len(props))
    log.info("atomic propositions: %d", len(atomic))
    log.info("split parents: %d, 1:1 parents: %d", len(SPLITS), len(props) - len(SPLITS))
    log.info("claim_level: %s", {lv: sum(1 for x in atomic if x["claim_level"] == lv) for lv in (OUTER, EMB)})
    log.info("entity resolution candidates: %d (unresolved %d)", len(er_rows),
             sum(1 for r in er_rows if r[3] == "UNRESOLVED"))
    log.info("normalized open sets: %d", len(os_rows))
    log.info("validation: ERROR=%d WARNING=%d", n_err, n_warn)
    if n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
