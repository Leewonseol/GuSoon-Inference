#!/usr/bin/env python3
"""GuSoon v2 historical event candidate layer (candidates, not facts).

atomic_propositions (APxxxx) → historical_event_candidates (ECxxxx)
                              + event_candidate_support

- Every atomic proposition gets one projection decision. A projectable one
  yields exactly one candidate built only from that proposition's own words,
  date and place (nothing merged across propositions, no same-event merge).
- historical_status is UNRESOLVED for every candidate. Whether candidates
  are about the same matter (and so CONTESTED) is the next stage's question.
- Raw tables and the earlier derived tables are never modified.

Projection modes
  DIRECT        depth-1 proposition: the outer speaker's own claim.
  CONTENT       embedded factual claim, attributed to the embedded speaker
                (depth 2), e.g. 나복 → '도적이 들어옴'.
  SPEECH_EVENT  the first embedded speaker's utterance itself as the event,
                attributed to the outer speaker (depth 1). Used when the
                embedded content is not a factual assertion (condition,
                promise, accusation, answer, written list).

epistemic_status (who stands behind the candidate, not whether it is true)
  ORDERED                 ROYAL_ORDER rows only
  ROYAL_FINDING           ROYAL_JUDGMENT
  OFFICIAL_FINDING        reports/findings/evaluations of officials and inspectors
  DIRECT_ACTION_RECORDED  the source records the speaker's own act (proposals, 홍대협's arrival)
  ASSERTED / STATE_REPORTED / DENIED   testimony or embedded claims
polarity: AFFIRMED / NEGATED (the source says it did not happen) / DOUBTED
  (the source finds the claim implausible without saying it did not happen).
support_strength is attestation distance, not a truth weight.

Outputs:
  output/11_v2_event_projection_decisions.csv
  output/12_v2_historical_event_candidates.csv
  output/13_v2_event_candidate_support.csv
  output/14_v2_event_candidate_validation.csv
  logs/v2_event_candidates.log
  database/gusun_v2.duckdb: event_projection_decisions, historical_event_candidates,
                            event_candidate_support
"""

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

PROTECTED_TABLES = ["source_records", "source_faithful_propositions", "person_membership", "search_log",
                    "atomic_propositions", "entity_resolution_candidates", "open_set_normalized"]

_spec = importlib.util.spec_from_file_location("v2_03", ROOT / "scripts" / "v2_03_atomic_normalization.py")
_v2_03 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v2_03)
surface_forms = _v2_03.surface_forms

DECISIONS = {"P": "EVENT_PROJECTABLE", "A": "ATTESTATION_ONLY", "M": "META_OR_PROCEDURAL", "R": "REVIEW_REQUIRED"}
MODES = {"D": "DIRECT", "C": "CONTENT", "S": "SPEECH_EVENT"}
POLARITY = {"+": "AFFIRMED", "-": "NEGATED", "?": "DOUBTED"}
EVENT_TYPES = {"ACTION", "STATE", "SPEECH_ACT", "ORDER", "REQUEST", "DEATH", "CAUSE_ATTRIBUTION",
               "TEMPORAL_ATTRIBUTION", "PLACE_ATTRIBUTION", "PURPOSE_ATTRIBUTION"}
EPISTEMIC = {"ASSERTED", "DENIED", "OFFICIAL_FINDING", "ROYAL_FINDING", "ORDERED", "DIRECT_ACTION_RECORDED",
             "STATE_REPORTED", "CONTESTED", "UNRESOLVED"}
ROLE_OF = {"ASSERTED": "ASSERTS_EVENT", "STATE_REPORTED": "REPORTS_STATE", "DENIED": "DENIES_EVENT",
           "OFFICIAL_FINDING": "OFFICIAL_FINDING", "ROYAL_FINDING": "ROYAL_FINDING",
           "ORDERED": "ORDERS_EVENT", "DIRECT_ACTION_RECORDED": "RECORDS_ACTION"}
OFFICIAL_MODES = {"OFFICIAL_REPORT", "INSPECTOR_REPORT", "OFFICIAL_FINDING", "OFFICIAL_EVALUATION"}

SPEC = {}


def P(ap, mode, etype, pol, pred, subj=None, obj=None, rel="", status=None, note=""):
    assert ap not in SPEC, ap
    SPEC[ap] = dict(decision="P", mode=mode, etype=etype, pol=pol, pred=pred, subj=subj, obj=obj,
                    rel=rel, status=status, note=note, reason="")


def X(ap, decision, reason):
    assert ap not in SPEC, ap
    SPEC[ap] = dict(decision=decision, reason=reason)


# ---- SRC2_001 이형원 장계 (1793-05-12) ----
P("AP0001", "D", "STATE", "+", "청주 덕평에 거주")
X("AP0002", "R", "05 수동검토 대상: '보고됨'이 이형원 자신의 판단인지 구순 측 피해 주장의 전달인지 불명. 같은 장계를 근거로 정조가 "
  "'도난 자체가 없었다는 방향'을 받아들인 기록(AP0024)이 있어, OFFICIAL_FINDING으로 구조화하면 의미가 뒤집힐 수 있음.")
P("AP0003", "S", "SPEECH_ACT", "+", "김명신을 도적 괴수라고 말함", subj="구순")
P("AP0004", "D", "ACTION", "+", "김명신을 잡음")
P("AP0005", "D", "ACTION", "+", "김명신을 달포 이상 구금함")
P("AP0006", "D", "ACTION", "+", "김명신을 조사함")
P("AP0007", "D", "ACTION", "-", "확실한 장물을 찾음")
P("AP0008", "D", "DEATH", "+", "사망")
P("AP0009", "D", "TEMPORAL_ATTRIBUTION", "+", "사망이 구금·조사 뒤였음", rel="구금·조사 뒤")
P("AP0010", "D", "ACTION", "+", "모진 형벌을 받음")
P("AP0011", "D", "STATE", "+", "무고함")
P("AP0012", "C", "STATE", "+", "사이에 원한이 있었음", subj="구순과 김명신")
P("AP0013", "C", "ACTION", "+", "도난 상황을 꾸밈", subj="구순")
P("AP0014", "C", "ACTION", "+", "김명신에게 도적 괴수 누명을 씌움", subj="구순", obj="김명신")
P("AP0015", "C", "ACTION", "+", "그 누명을 씌우는 데 행랑 하인을 통함", subj="구순", obj="행랑 하인",
  note="'그 누명'은 같은 부모(P0010)의 AP0014 내용. 연결 relation은 만들지 않음.")
P("AP0016", "C", "ACTION", "+", "그 누명을 씌우는 데 교졸을 통함", subj="구순", obj="교졸",
  note="'그 누명'은 같은 부모(P0010)의 AP0014 내용. 연결 relation은 만들지 않음.")
P("AP0017", "C", "STATE", "+", "구순 집에서 미워하던 사람들이었음")
P("AP0018", "D", "ACTION", "+", "수사를 병영 비장에게 전적으로 맡김", obj="병영 비장")
X("AP0019", "A", "'방관'은 이문협의 행위에 대한 평가적 성격 규정. 맡김 행위(AP0018)와 별도인 사건을 만들면 평가를 사건으로 바꾸게 됨.")
P("AP0020", "D", "STATE", "+", "허황한 말이었음", subj="이광섭이 믿은 말")
P("AP0021", "D", "ACTION", "+", "무고한 사람을 잘못 잡음")
P("AP0022", "D", "REQUEST", "+", "이광섭 파직·나문·엄한 감죄를 청함")
P("AP0023", "D", "ORDER", "+", "이광섭 처분 요청을 윤허함")
P("AP0024", "D", "STATE", "-", "있었음", subj="도난 자체",
  note="원문: '당시 장계·조사에 따라 도난 자체가 없었다는 방향을 받아들임'. '방향' 표현의 판단 강도에 유의.")
P("AP0025", "D", "ORDER", "+", "구순을 의금부에 잡아 가두고 엄히 조사하도록 명함")

# ---- SRC2_002 / SRC2_003 이조원 (1793-05-27) ----
P("AP0026", "D", "ACTION", "?", "화적이 들었음", subj="구순 집",
  note="원문: 그런 설명이 이치에 맞지 않는다고 판단 — 발생 부정 단정이 아니라 신빙성 부정.")
P("AP0027", "D", "STATE", "+", "구순의 이웃으로 삶")
P("AP0028", "D", "ACTION", "+", "구순의 행실을 비판함")
P("AP0029", "D", "STATE", "+", "앙심을 품음")
P("AP0030", "D", "CAUSE_ATTRIBUTION", "+", "그 앙심이 김명신의 비판 때문이었음")
P("AP0031", "D", "STATE", "+", "김명신을 모함하려 함")
P("AP0032", "D", "ACTION", "+", "도난 상황을 꾸밈")
P("AP0033", "D", "ACTION", "+", "지세랑이라는 말을 만듦")
P("AP0034", "D", "ACTION", "+", "지세랑이라는 말을 퍼뜨림")
P("AP0035", "D", "ACTION", "+", "작은 궤짝의 돈을 도둑맞았다고 꾸밈")
P("AP0036", "D", "STATE", "+", "부스럼 흔적이었음")
P("AP0037", "D", "ACTION", "+", "하인의 흔적을 창상으로 꾸밈")
P("AP0038", "D", "DEATH", "+", "사망")
P("AP0039", "D", "PLACE_ATTRIBUTION", "+", "사망 장소가 병영 옥이었음")
P("AP0040", "D", "CAUSE_ATTRIBUTION", "+", "구순이 구성한 죄안 때문에 사망함")
X("AP0041", "A", "'원통하게'는 죽음에 대한 도덕적·법적 평가. 사망 자체는 AP0038에서 별도 candidate.")
P("AP0042", "D", "DEATH", "+", "사망")
P("AP0043", "D", "TEMPORAL_ATTRIBUTION", "+", "김명신이 죽은 뒤 따라 죽음", rel="김명신이 죽은 뒤",
  note="'따라'가 단순 선후인지 인과적 의미인지 미판정.")
P("AP0044", "D", "ACTION", "-", "사건을 자세히 조사함")
P("AP0045", "D", "ACTION", "+", "사건을 하급 보조자에게 맡김", obj="하급 보조자")
P("AP0046", "D", "STATE", "+", "구순의 가객이었음")
X("AP0047", "R", "부모 P0029가 AMBIGUOUS/REVIEW: 발화 주체(정조/비변사 당상) 미확정.")
P("AP0048", "D", "ORDER", "+", "이조원을 파직하도록 명함")
P("AP0049", "D", "ORDER", "+", "구순을 의금부에 엄히 가두고 반복 신문하도록 명함")
P("AP0050", "D", "STATE", "-", "있었음", subj="구순 사건의 도난", note="원문: '도난이 없었다는 방향의 판단을 보고'.")
X("AP0051", "M", "안핵관 이조원의 조사 방식에 대한 국왕의 문제 제기(조사 절차 메타 정보).")
X("AP0052", "M", "안핵관 이조원의 서계 작성 방식에 대한 국왕의 문제 제기(조사 절차 메타 정보).")

# ---- SRC2_004 승정원일기 (1793-05-28) ----
X("AP0053", "M", "국왕이 안핵 쟁점을 묻는 조정 문답(절차).")
X("AP0054", "M", "안핵어사의 사전 지식 상태(조사 절차 메타 정보).")
P("AP0055", "D", "ACTION", "+", "지세랑 호칭을 사용한 적이 있음", subj="예전 호중 화적")
X("AP0056", "A", "'~아닌 듯'은 홍대협의 유보적 추론. 근거(AP0055)와 별도인 사건이 없음.")
P("AP0057", "D", "ORDER", "+", "홍대협에게 내려가 자세히 조사해 오라고 명함")
P("AP0058", "D", "ORDER", "+", "홍대협을 충청도 공주 안핵어사로 차하함")

# ---- SRC2_005 윤노동 별단 (1793-06-11) ----
P("AP0059", "C", "ACTION", "+", "도적을 만남", subj="구순")
P("AP0060", "D", "ACTION", "+", "영교를 부름", obj="영교")
P("AP0061", "D", "ACTION", "+", "김명신 등의 이름을 써 줌")
P("AP0062", "D", "DEATH", "+", "사망")
P("AP0063", "D", "CAUSE_ATTRIBUTION", "+", "사망 원인이 병이었음")
P("AP0064", "D", "TEMPORAL_ATTRIBUTION", "+", "사망이 체포·구금 뒤였음", rel="체포·구금 뒤")
P("AP0065", "D", "ACTION", "+", "참혹한 형벌을 받음")
P("AP0066", "D", "ACTION", "-", "진정한 장물을 얻음")
P("AP0067", "D", "ACTION", "+", "변가의 처를 꾐", obj="변가의 처")
P("AP0068", "S", "SPEECH_ACT", "+", "김명신이 도적 괴수라는 취지의 공초를 냄", subj="변가의 처")
P("AP0069", "D", "ACTION", "+", "변가의 처를 꾀어 그 공초를 내게 함", obj="변가의 처")
P("AP0070", "D", "REQUEST", "+", "홍대협의 안핵 복명 전이므로 윤노동 별단의 구순 사건 처리를 보류할 것을 청함")
P("AP0071", "D", "ORDER", "+", "비변사의 보류 요청을 윤허함")

# ---- SRC2_006 홍대협 복명·정조 처분 (1793-06-13) ----
P("AP0072", "D", "ACTION", "+", "공주목에 도착해 관련자들을 차례로 신문함", status="DIRECT_ACTION_RECORDED")
P("AP0073", "D", "STATE", "+", "구순 집 계집종의 남편이며 바깥사랑에 거주함")
P("AP0074", "S", "SPEECH_ACT", "+", "명업에게 도적이 들었다고 알림", subj="나복", obj="명업",
  note="시간이 알림 시점인지 침입 시점인지 원문에서 구분되지 않아 AP 값 그대로 둠.")
P("AP0075", "C", "ACTION", "+", "들어옴", subj="도적", note="시간은 부모 P0049의 값(나복 진술 기준).")
P("AP0076", "C", "STATE", "+", "30여 명이었음", subj="들어온 도적", note="시간은 부모 P0049의 값(나복 진술 기준).")
P("AP0077", "C", "ACTION", "+", "횃불을 들고 들어옴", subj="도적", note="시간은 부모 P0049의 값(나복 진술 기준).")
P("AP0078", "C", "SPEECH_ACT", "+", "지세대감이라 자칭함", subj="도적",
  note="도적의 자칭은 나복이 전한 발화. 시간은 부모 P0049의 값(나복 진술 기준).")
P("AP0079", "C", "ACTION", "+", "돈과 물품을 훔침", subj="도적", note="시간은 부모 P0049의 값(나복 진술 기준).")
P("AP0080", "D", "STATE", "+", "본래 구순과 친숙하여 날마다 왕래함")
P("AP0081", "D", "ACTION", "+", "2월 초 박거사 일로 구순에게 편지를 보내 힐책함", obj="구순")
P("AP0082", "D", "STATE", "+", "왕래가 끊김", rel="그 뒤")
P("AP0083", "D", "ACTION", "+", "소장을 올림")
P("AP0084", "D", "ORDER", "+", "그 소장으로 내려짐", subj="체포령",
  note="증언 속에 언급된 명령. 명령 기록 자체가 아니므로 ORDERED가 아니라 ASSERTED.")
P("AP0085", "D", "ACTION", "+", "찾아온 장교 한 명을 안행랑으로 불러 조용히 대화함")
P("AP0086", "D", "SPEECH_ACT", "+", "병영 뜰 공초에서 처음에는 사실대로 말함", note="'사실대로'는 진술자 본인의 평가.")
P("AP0087", "D", "STATE", "+", "위협이 두려웠음")
P("AP0088", "D", "SPEECH_ACT", "+", "도적이 없었다는 취지로 진술을 바꿈",
  note="'도적이 없었다'는 바뀐 진술의 내용이며 이 candidate가 부정하는 사건이 아님.")
P("AP0089", "D", "CAUSE_ATTRIBUTION", "+", "위협이 두려워 진술을 바꿈")
P("AP0090", "D", "ACTION", "+", "이진욱을 비장청으로 부름")
P("AP0091", "D", "ORDER", "+", "이진욱·조계완 등에게 덕평으로 가도록 지시함")
P("AP0092", "D", "ORDER", "+", "변지돌과 정원돌을 잡아오라고 지시함")
P("AP0093", "D", "ACTION", "+", "철편 네 개를 만들어 줌")
P("AP0094", "C", "STATE", "+", "처남매부 사이임", subj="변지돌과 정원돌")
P("AP0095", "C", "STATE", "+", "힘이 셈", subj="변지돌")
P("AP0096", "D", "SPEECH_ACT", "+", "조심하라고 말함")
P("AP0097", "D", "STATE", "+", "이미 공주진에서 잡혀간 상태였음")
P("AP0098", "D", "ACTION", "+", "자미덕을 잡음")
P("AP0099", "D", "STATE", "+", "잡은 사람이 자미덕뿐이었음")
P("AP0100", "D", "STATE", "+", "재돌의 처임")
P("AP0101", "D", "STATE", "+", "변지돌의 아우임")
P("AP0102", "D", "ACTION", "+", "자미덕을 데리고 구순 집으로 가 도난 상황을 물음")
P("AP0103", "S", "SPEECH_ACT", "+", "잃은 물건들을 열거함", subj="구순")
P("AP0104", "S", "SPEECH_ACT", "+", "도적이 스스로 지세대사라고 자칭했다고 말함", subj="구순",
  note="시간·장소는 구순이 말한 장면(2월 29일 구순 집)의 것이므로 도적의 자칭 자체를 candidate로 만들지 않음.")
P("AP0105", "D", "ORDER", "+", "3월 4일 풍각 김생원과 흥덕 김생원을 잡아오라고 지시함")
X("AP0106", "M", "식별 진술(풍각 김생원=김명신)은 entity resolution 근거(08)로 다루며 사건이 아님.")
X("AP0107", "M", "식별 진술(흥덕 김생원=김갑득)은 entity resolution 근거(08)로 다루며 사건이 아님.")
P("AP0108", "D", "ACTION", "+", "병사 분부에 따라 김명신과 김갑득을 잡아옴")
P("AP0109", "D", "ACTION", "+", "풍각 김생원을 잡으러 가는 길에 구순 집에 들름")
P("AP0110", "S", "SPEECH_ACT", "+", "왜 다시 왔는지 물음", subj="구순")
P("AP0111", "S", "SPEECH_ACT", "+", "풍각의 상주를 잡으러 왔다고 답함", subj="조계완")
P("AP0112", "S", "SPEECH_ACT", "+", "이제야 도적 다스리는 일이 바른 길을 얻었다는 취지로 말함", subj="구순")
P("AP0113", "D", "ACTION", "+", "서찰 한 장을 건네며 병사에게 전해달라고 요구함")
P("AP0114", "D", "STATE", "+", "아산에 나가 있었음", rel="자미덕 체포 전")
P("AP0115", "D", "ACTION", "+", "자미덕을 병영으로 붙잡아 감")
P("AP0116", "D", "ACTION", "+", "자미덕을 도적이라고 하며 한 차례 신문함")
P("AP0117", "D", "STATE", "+", "신문 뒤 비장청 다모방에 구류됨", rel="신문 뒤")
P("AP0118", "D", "ACTION", "+", "그 후 매일 자미덕을 방안으로 불러들임", rel="그 후")
P("AP0119", "S", "SPEECH_ACT", "+", "자미덕의 남편 재돌이 이미 체포되었다고 말함", subj="한 비장",
  note="발화 내용(재돌 체포)은 candidate로 승격하지 않음.")
P("AP0120", "S", "SPEECH_ACT", "+", "'정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적들이라고 말하면'이라는 조건을 말함",
  subj="한 비장", note="조건문의 앞부분. 명령·지목 요구로 바꾸지 않음. 대상은 open set(명시 5명 + '등').")
P("AP0121", "S", "SPEECH_ACT", "+", "그 조건을 충족하면 자미덕과 남편을 다음 날 석방하겠다고 말함", subj="한 비장",
  note="조건문의 뒷부분. 석방 실행 여부는 candidate로 만들지 않음.")
P("AP0122", "D", "ACTION", "+", "자미덕에게 떡과 밥을 줌")
P("AP0123", "D", "ACTION", "+", "서로 대질함", note="대질의 목적·혐의·주관자는 원문에 없으므로 추가하지 않음.")
P("AP0124", "D", "SPEECH_ACT", "+", "이집거와 대질할 때 거짓으로 꾸며 말함",
  note="거짓 발언의 내용·대상은 원문에 없으므로 생성하지 않음.")
P("AP0125", "D", "ACTION", "+", "자미덕의 그 거짓 발언을 지휘함", subj="한 비장",
  note="자미덕 진술(AP0125)이 유일한 근거. '그 거짓 발언'은 같은 부모(P0084)의 AP0124 내용.")
X("AP0126", "R", "부모 P0085가 AMBIGUOUS/REVIEW: 종속절('~정소된 뒤였다')만 있어 주절이 무엇인지 미상.")
P("AP0127", "D", "ACTION", "+", "병영 아전 유제희를 내보냄")
P("AP0128", "D", "PURPOSE_ATTRIBUTION", "+", "유제희를 내보낸 목적이 도적 진상 탐지였음")
P("AP0129", "S", "ACTION", "+", "변지돌·변재돌·정원돌·김명신·김성손·김흥득·김흥길 등의 성명을 적어 옴", subj="유제희",
  note="한재욱이 전한 유제희의 기록 행위. 명단은 open set(명시 7명 + '등')이며 구성원이 실제 도적이라는 뜻이 아님.")
P("AP0130", "C", "ACTION", "+", "그 이름들을 직접 염탐해 알아냄", subj="유제희")
P("AP0131", "D", "ACTION", "+", "자미덕을 방안으로 부름")
P("AP0132", "D", "ACTION", "+", "자미덕에게 남은 밥을 줌")
P("AP0133", "S", "SPEECH_ACT", "+", "석단 공초에서 김명신이 도적 괴수라고 했다고 말함", subj="유제희",
  note="석단의 공초 내용은 candidate로 승격하지 않음(3단 중첩).")
P("AP0134", "D", "SPEECH_ACT", "+", "자미덕에게 다시 물어보라고 말함")
P("AP0135", "D", "ACTION", "+", "자미덕에게 다시 물음")
P("AP0136", "D", "CAUSE_ATTRIBUTION", "+", "다시 물은 것이 유제희 말에 따른 것이었음")
P("AP0137", "S", "SPEECH_ACT", "+", "재질문에 모른다고 답함", subj="자미덕")
P("AP0138", "D", "ACTION", "-", "자미덕을 은밀히 사주함",
  note="한재욱의 부인 진술. '사주했다'는 발생 사실로 만들지 않음.")
P("AP0139", "D", "STATE", "-", "구순과 아는 사이임", note="원문: 구순과 평생 모르는 사이.")
P("AP0140", "D", "ACTION", "+", "당초 현지에 가서 탐문함")
P("AP0141", "S", "SPEECH_ACT", "+", "풍각 김상제도 극히 수상하다고 말함", subj="구순")
P("AP0142", "D", "ACTION", "+", "그 말을 원돌 등의 이름과 함께 기록해 올림")
P("AP0143", "D", "STATE", "+", "실제였음", subj="약간의 도난")
P("AP0144", "D", "STATE", "+", "큰 화적 사건이 아니라 보통 좀도둑 수준이었음", subj="도난")
X("AP0145", "M", "지세 호칭 기원을 확정하지 못했다는 조사 상태 정보.")
P("AP0146", "D", "ACTION", "+", "과장함")
P("AP0147", "D", "ACTION", "+", "거짓 보고를 함")
P("AP0148", "D", "STATE", "+", "구순의 과장과 아전의 거짓 보고를 믿음")
P("AP0149", "D", "ACTION", "+", "장물이 없는 상태에서 판단함")
P("AP0150", "D", "ACTION", "+", "큰 도적으로 판단함")
P("AP0151", "D", "CAUSE_ATTRIBUTION", "+", "죽음이 질병 때문이었음")
P("AP0152", "D", "ACTION", "-", "장물부터 확보함")
P("AP0153", "D", "ACTION", "+", "장교·나졸을 풀어 평민을 잡음")
P("AP0154", "D", "ACTION", "+", "지휘함", subj="병영 비장")
P("AP0155", "D", "ACTION", "+", "병영 비장 지휘대로 죄를 얽음")
X("AP0156", "M", "안핵 쟁점을 세 의안으로 나눈 국왕의 분류 행위(절차 메타 정보).")
P("AP0157", "D", "STATE", "+", "실제로 있었음", subj="도난")
P("AP0158", "D", "CAUSE_ATTRIBUTION", "+", "전염병에 걸려 죽음", subj="김명신")
P("AP0159", "D", "CAUSE_ATTRIBUTION", "+", "전염병에 걸려 죽음", subj="김명신 부처 중 처")
P("AP0160", "D", "ACTION", "-", "곤장을 맞음", subj="김명신")
P("AP0161", "D", "ACTION", "-", "평범한 신문을 받음", subj="김명신")
P("AP0162", "D", "ACTION", "+", "지세대감·지세대사·지세랑 호칭을 씀", subj="예전 무식한 좀도둑들")
P("AP0163", "D", "ACTION", "-", "지세 호칭을 스스로 만들어냄", subj="구순",
  note="원문: 그런 죄는 면하게 됐다고 판단(창작 혐의 불인정).")
P("AP0164", "D", "ORDER", "+", "구순을 사형에서 감해 외딴 섬으로 정배하도록 명함")
P("AP0165", "D", "ORDER", "+", "구순을 신지도에 정배하는 처분을 내림", note="왕명 기록. 집행 기록이 아님.")
P("AP0166", "D", "ORDER", "+", "이광섭을 영동현에 유배하는 처분을 내림", note="왕명 기록. 집행 기록이 아님.")
P("AP0167", "D", "ORDER", "+", "병영 비장 한가를 도백이 엄히 세 차례 형장 친 뒤 먼 섬의 종으로 보내도록 명함",
  rel="형장 친 뒤", note="'형장 친 뒤'는 명령 내용 안의 순서. 왕명 기록이며 집행 기록이 아님.")
P("AP0168", "D", "ORDER", "+", "충청도 관찰사 이형원을 파직하도록 명함")
P("AP0169", "D", "ORDER", "+", "전 충청도 관찰사 이형원을 유임하는 처분을 내림")
X("AP0170", "M", "2차 배경 자료(source_records: 사건 F 생성에는 사용하지 않음).")
X("AP0171", "M", "2차 배경 자료(source_records: 사건 F 생성에는 사용하지 않음).")

# AP predicates whose negation words are not negations of the projected event.
NEGATION_EXEMPT = {
    "AP0088": "부정어는 바뀐 진술의 내용",
    "AP0137": "부정어는 응답 내용('모른다'); 응답 자체가 candidate",
    "AP0144": "'~가 아니라 ~수준'은 규모 서술",
    "AP0149": "'장물이 없는 상태에서'는 판단 행위의 조건",
}
NEGATION_RE = re.compile(r"없|않|(?<!잘)못|아니|모르는 사이|면하게")

log = logging.getLogger("v2_event_candidates")


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


def epistemic(mode_attest, depth, etype, pol, override):
    if override:
        return override
    if depth >= 2 or mode_attest in ("TESTIMONY", "DIRECT_STATEMENT"):
        if pol == "NEGATED":
            return "DENIED"
        return "STATE_REPORTED" if etype == "STATE" else "ASSERTED"
    if mode_attest == "ROYAL_ORDER":
        return "ORDERED"
    if mode_attest == "ROYAL_JUDGMENT":
        return "ROYAL_FINDING"
    if mode_attest == "MINISTERIAL_PROPOSAL":
        return "DIRECT_ACTION_RECORDED"
    if mode_attest in OFFICIAL_MODES:
        return "OFFICIAL_FINDING"
    raise ValueError(f"no epistemic rule for {mode_attest}")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(LOG_DIR / "v2_event_candidates.log", mode="w", encoding="utf-8"),
                  logging.StreamHandler(sys.stdout)],
    )
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
    atomic = fetch(con, "SELECT * FROM atomic_propositions ORDER BY atomic_prop_id")
    raw = {r["prop_id"]: r for r in fetch(con, "SELECT * FROM source_faithful_propositions")}
    er = fetch(con, "SELECT * FROM entity_resolution_candidates")
    sets = fetch(con, "SELECT * FROM open_set_normalized ORDER BY set_id")
    sources = {r["source_record_id"]: r for r in fetch(con, "SELECT * FROM source_records")}
    membership = [r["person"] for r in fetch(con, "SELECT person FROM person_membership")]
    ap_by_id = {a["atomic_prop_id"]: a for a in atomic}

    missing = sorted(set(ap_by_id) - set(SPEC))
    extra = sorted(set(SPEC) - set(ap_by_id))
    if missing or extra:
        log.error("SPEC coverage mismatch: missing=%s extra=%s", missing, extra)
        sys.exit(1)

    lexicon = set(membership)
    for a in atomic:
        lexicon.update(x for x in a["entity_surface_forms"].split("|") if x)
    for r in raw.values():
        lexicon.update(x for x in r["named_entities"].split("|") if x)
    lexicon.update(e["candidate_entity"].split("(")[0] for e in er)
    lexicon.add("도적")
    lexicon = sorted(lexicon, key=len, reverse=True)

    set_of_ap = {}
    for s in sets:
        for ap in s["atomic_prop_ids"].split("|"):
            set_of_ap.setdefault(ap, []).append(s["set_id"])

    def er_rows_for(parent, text):
        return [e for e in er if parent in e["source_prop_ids"].split("|")
                and e["surface_form"].split("(")[0] in text]

    decisions, candidates, support = [], [], []
    for a in atomic:
        ap = a["atomic_prop_id"]
        s = SPEC[ap]
        if s["decision"] != "P":
            decisions.append([ap, a["parent_prop_id"], DECISIONS[s["decision"]], "", "", s["reason"]])
            continue
        mode = MODES[s["mode"]]
        chain = [a["outer_speaker"]] + ([x.split("(")[0].strip() for x in a["embedded_speaker"].split(" > ")]
                                        if a["embedded_speaker"] else [])
        if mode == "CONTENT":
            speaker, depth = chain[1], 2
            speaker_chain = " > ".join(chain[:2])
        else:
            speaker, depth = chain[0], 1
            speaker_chain = chain[0]
        if mode == "CONTENT" and int(a["attestation_depth"]) < 2:
            log.error("%s CONTENT mode on a depth-1 atomic proposition", ap)
            sys.exit(1)
        if mode == "SPEECH_EVENT" and int(a["attestation_depth"]) < 2 and s["etype"] != "SPEECH_ACT":
            log.error("%s SPEECH_EVENT mode needs an embedded speech", ap)
            sys.exit(1)
        pol = POLARITY[s["pol"]]
        status = epistemic(a["attestation_mode"], depth, s["etype"], pol, s["status"])
        subj = s["subj"] if s["subj"] is not None else a["subject_surface"]
        obj = s["obj"] if s["obj"] is not None else a["object_or_content"]
        text = " ".join([subj, s["pred"], obj])
        ers = er_rows_for(a["parent_prop_id"], text)
        er_status = "; ".join(f"{e['surface_form'].split('(')[0]}→{e['candidate_entity']}:{e['resolution_status']}"
                              for e in ers) or "NONE_NEEDED"
        normalized = "; ".join(f"{e['surface_form'].split('(')[0]}={e['candidate_entity']}" for e in ers
                               if e["resolution_status"] == "DIRECTLY_IDENTIFIED_IN_SOURCE")
        ec = f"EC{len(candidates) + 1:04d}"
        notes = " ".join(x for x in [s["note"], "historical_status는 사실 판정이 아님(다음 단계에서 비교)."] if x)
        candidates.append(dict(
            event_candidate_id=ec, origin_atomic_prop_id=ap, event_type=s["etype"], polarity=pol,
            subject_surface=subj, predicate=s["pred"], object_surface=obj,
            historical_place=a["historical_place"], place_status=a["place_status"],
            occurrence_lunar_text=a["occurrence_lunar_text"], occurrence_precision=a["occurrence_precision"],
            relative_time_text=s["rel"], epistemic_status=status, historical_status="UNRESOLVED",
            claim_topic=a["claim_topic"], conflict_group=a["conflict_group"], set_status=a["set_status"],
            open_set_ids="|".join(set_of_ap.get(ap, [])), shared_utterance_group=a["shared_utterance_group"],
            entity_resolution_status=er_status, normalized_names=normalized, notes=notes,
        ))
        if depth == 1 and speaker in text:
            strength = "FIRST_HAND_PARTICIPANT"
        elif status == "ORDERED":
            strength = "RECORDED_ORDER"
        elif status in ("ROYAL_FINDING", "OFFICIAL_FINDING"):
            strength = "RECORDED_JUDGMENT"
        elif status == "DIRECT_ACTION_RECORDED":
            strength = "RECORDED_ACT"
        elif depth == 1:
            strength = "REPORTED_BY_SPEAKER"
        else:
            strength = "EMBEDDED_HEARSAY"
        support.append([ec, ap, ROLE_OF[status], speaker, depth, speaker_chain, a["source_record_id"],
                        sources[a["source_record_id"]]["source_tier"], strength,
                        f"projection={mode}; atomic claim_level={a['claim_level']}, depth={a['attestation_depth']}"])
        decisions.append([ap, a["parent_prop_id"], "EVENT_PROJECTABLE", mode, ec, s["note"]])

    # ---- validation ----
    ec_ids = {c["event_candidate_id"] for c in candidates}
    sup_count = {}
    for r in support:
        sup_count[r[0]] = sup_count.get(r[0], 0) + 1
    check("V01", "모든 event candidate에 supporting atomic proposition 1개 이상", all(sup_count.get(e) for e in ec_ids),
          f"candidates={len(ec_ids)}")
    dangling = [r[1] for r in support if r[1] not in ap_by_id] + [d[0] for d in decisions if d[0] not in ap_by_id]
    check("V02", "dangling atomic_prop_id 0", not dangling, "|".join(dangling))
    check("V03", "171개 atomic 모두 판정 1건씩", len(decisions) == len(atomic) == len({d[0] for d in decisions}),
          f"decisions={len(decisions)} atomic={len(atomic)}")
    proj = [d for d in decisions if d[2] == "EVENT_PROJECTABLE"]
    check("V04", "EVENT_PROJECTABLE 수 = candidate 수(1:1, merge 없음)",
          len(proj) == len(candidates) == len({c["origin_atomic_prop_id"] for c in candidates}),
          f"projectable={len(proj)} candidates={len(candidates)}")

    date_re = re.compile(r"\d{4}|\d+월|\d+일")
    place_terms = set()
    for r in raw.values():
        if r["historical_place"]:
            place_terms.add(r["historical_place"])
            place_terms.update(w for w in r["historical_place"].split() if len(w) > 1 and w != "구순")
    person_bad, date_bad, place_bad = [], [], []
    for c in candidates:
        a = ap_by_id[c["origin_atomic_prop_id"]]
        r = raw[a["parent_prop_id"]]
        ap_text = " ".join([a["subject_surface"], a["predicate"], a["object_or_content"]])
        raw_text = " ".join([r["subject"], r["predicate"], r["object_or_content"], r["occurrence_lunar_text"]])
        c_text = " ".join([c["subject_surface"], c["predicate"], c["object_surface"], c["relative_time_text"]])
        for name in surface_forms(c_text, lexicon):
            if name not in raw_text:
                person_bad.append(f"{c['event_candidate_id']}:{name}")
        for d in date_re.findall(c_text):
            if d not in ap_text:
                date_bad.append(f"{c['event_candidate_id']}:{d}")
        if (c["occurrence_lunar_text"], c["occurrence_precision"]) != (a["occurrence_lunar_text"], a["occurrence_precision"]):
            date_bad.append(f"{c['event_candidate_id']}:occurrence")
        if c["relative_time_text"] and c["relative_time_text"] not in ap_text + " " + a["occurrence_lunar_text"]:
            date_bad.append(f"{c['event_candidate_id']}:relative '{c['relative_time_text']}'")
        if c["historical_place"] != a["historical_place"]:
            place_bad.append(f"{c['event_candidate_id']}:historical_place")
        for p in place_terms:
            if p in c_text and p not in ap_text:
                place_bad.append(f"{c['event_candidate_id']}:{p}")
    check("V05", "raw proposition에서 지원되지 않는 인물 추가 0", not person_bad, "|".join(person_bad))
    check("V06", "지원되지 않는 날짜 추가 0", not date_bad, "|".join(date_bad))
    check("V07", "지원되지 않는 장소 추가 0", not place_bad, "|".join(place_bad))

    id_bad = []
    for c in candidates:
        a = ap_by_id[c["origin_atomic_prop_id"]]
        ap_text = " ".join([a["subject_surface"], a["predicate"], a["object_or_content"]])
        c_text = " ".join([c["subject_surface"], c["predicate"], c["object_surface"]])
        for e in er:
            if a["parent_prop_id"] not in e["source_prop_ids"].split("|"):
                continue
            cand = e["candidate_entity"].split("(")[0]
            if cand in c_text and cand not in ap_text:
                id_bad.append(f"{c['event_candidate_id']}:{cand}")
        for pair in filter(None, c["normalized_names"].split("; ")):
            sf, cand = pair.split("=")
            if not any(e["surface_form"].split("(")[0] == sf and e["candidate_entity"] == cand
                       and e["resolution_status"] == "DIRECTLY_IDENTIFIED_IN_SOURCE" for e in er):
                id_bad.append(f"{c['event_candidate_id']}:normalized {pair}")
    check("V08", "candidate identity를 확정값으로 승격한 사례 0 (surface 대체·비DIRECT 병기 없음)", not id_bad,
          "|".join(id_bad))

    set_bad = []
    for s in sets:
        for ap in s["atomic_prop_ids"].split("|"):
            if SPEC[ap]["decision"] != "P":
                set_bad.append(f"{s['set_id']}:{ap} 미투영")
                continue
            c = next(x for x in candidates if x["origin_atomic_prop_id"] == ap)
            if s["set_id"] not in c["open_set_ids"].split("|") or c["set_status"] != ap_by_id[ap]["set_status"]:
                set_bad.append(f"{s['set_id']}:{c['event_candidate_id']}")
            c_text = " ".join([c["subject_surface"], c["predicate"], c["object_surface"]])
            if s["open_marker"] == "등":
                for m in s["explicit_members"].split("|"):
                    if m and m not in c_text:
                        set_bad.append(f"{s['set_id']}:{c['event_candidate_id']} 구성원 {m} 누락")
                if "등" not in c_text:
                    set_bad.append(f"{s['set_id']}:{c['event_candidate_id']} '등' 누락")
    check("V09", "OPEN_SET 손실 0 (set_id·set_status·명시 구성원·'등' 보존)", not set_bad, "|".join(set_bad))

    deny_bad = []
    for c in candidates:
        a = ap_by_id[c["origin_atomic_prop_id"]]
        negated_text = bool(NEGATION_RE.search(a["predicate"]))
        exempt = c["origin_atomic_prop_id"] in NEGATION_EXEMPT
        if negated_text and not exempt and c["polarity"] == "AFFIRMED":
            deny_bad.append(f"{c['event_candidate_id']}:부정 진술이 AFFIRMED")
        if c["epistemic_status"] == "DENIED" and c["polarity"] != "NEGATED":
            deny_bad.append(f"{c['event_candidate_id']}:DENIED인데 NEGATED 아님")
        if c["polarity"] != "AFFIRMED" and not negated_text:
            deny_bad.append(f"{c['event_candidate_id']}:부정어 없는 진술을 부정")
    check("V10", "DENIED/부정 proposition을 발생 사실로 바꾼 사례 0", not deny_bad, "|".join(deny_bad))

    order_bad = []
    for c in candidates:
        a = ap_by_id[c["origin_atomic_prop_id"]]
        if c["event_type"] not in EVENT_TYPES:
            order_bad.append(f"{c['event_candidate_id']}:event_type {c['event_type']}")
        if a["attestation_mode"] == "ROYAL_ORDER" and (c["event_type"] != "ORDER" or c["epistemic_status"] != "ORDERED"):
            order_bad.append(f"{c['event_candidate_id']}:왕명이 ORDER/ORDERED 아님")
        if c["epistemic_status"] == "ORDERED" and a["attestation_mode"] != "ROYAL_ORDER":
            order_bad.append(f"{c['event_candidate_id']}:ROYAL_ORDER 아닌데 ORDERED")
    check("V11", "ORDER를 EXECUTED event로 바꾼 사례 0 (EXECUTION 유형 없음, ORDERED는 왕명 기록만)", not order_bad,
          "|".join(order_bad))

    status_bad = [c["event_candidate_id"] for c in candidates
                  if c["epistemic_status"] not in EPISTEMIC or c["historical_status"] != "UNRESOLVED"]
    check("V12", "FACT 자동 승격 0 (historical_status 전부 UNRESOLVED, epistemic_status 허용값)", not status_bad,
          "|".join(status_bad))
    ug_bad = [c["event_candidate_id"] for c in candidates
              if c["shared_utterance_group"] != ap_by_id[c["origin_atomic_prop_id"]]["shared_utterance_group"]]
    check("V13", "shared_utterance_group 보존", not ug_bad, "|".join(ug_bad))
    bg = [c["event_candidate_id"] for c in candidates if sources[ap_by_id[c["origin_atomic_prop_id"]]["source_record_id"]]
          ["source_tier"] != "S1_PRIMARY"]
    check("V14", "2차 배경 자료(S3)에서 candidate 생성 0", not bg, "|".join(bg))
    review_ok = all(SPEC[ap]["decision"] == "R" for ap in ap_by_id
                    if raw[ap_by_id[ap]["parent_prop_id"]]["prop_id"] in ("P0029", "P0085"))
    check("V15", "05에서 REVIEW였던 부모(P0029·P0085)의 atomic은 REVIEW_REQUIRED", review_ok)

    # ---- write ----
    dec_cols = ["atomic_prop_id", "parent_prop_id", "decision", "projection_mode", "event_candidate_id", "reason"]
    cand_cols = ["event_candidate_id", "origin_atomic_prop_id", "event_type", "polarity", "subject_surface",
                 "predicate", "object_surface", "historical_place", "place_status", "occurrence_lunar_text",
                 "occurrence_precision", "relative_time_text", "epistemic_status", "historical_status",
                 "claim_topic", "conflict_group", "set_status", "open_set_ids", "shared_utterance_group",
                 "entity_resolution_status", "normalized_names", "notes"]
    sup_cols = ["event_candidate_id", "atomic_prop_id", "support_role", "speaker", "attestation_depth",
                "speaker_chain", "source_record_id", "source_tier", "support_strength", "notes"]
    write_csv(OUT_DIR / "11_v2_event_projection_decisions.csv", dec_cols, decisions)
    write_csv(OUT_DIR / "12_v2_historical_event_candidates.csv", cand_cols,
              [[c[k] for k in cand_cols] for c in candidates])
    write_csv(OUT_DIR / "13_v2_event_candidate_support.csv", sup_cols, support)

    for table, fn in [("event_projection_decisions", "11_v2_event_projection_decisions.csv"),
                      ("historical_event_candidates", "12_v2_historical_event_candidates.csv"),
                      ("event_candidate_support", "13_v2_event_candidate_support.csv")]:
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv(?, header=true, all_varchar=true, "
                    f"quote='\"', escape='\"')", [str(OUT_DIR / fn)])
    counts = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
              for t in ("event_projection_decisions", "historical_event_candidates", "event_candidate_support")}
    check("V16", "derived table 행 수가 CSV와 일치",
          counts == {"event_projection_decisions": len(decisions), "historical_event_candidates": len(candidates),
                     "event_candidate_support": len(support)}, str(counts))
    digests_after = {t: table_digest(con, t) for t in PROTECTED_TABLES}
    con.close()
    changed = [t for t in PROTECTED_TABLES if digests_before[t] != digests_after[t]]
    check("V17", "raw table·기존 derived table 불변", not changed, "|".join(changed))
    check("V18", "raw CSV SHA-256 불변", all(sha256(RAW_DIR / fn) == h for fn, h in expected_sha.items()))
    write_csv(OUT_DIR / "14_v2_event_candidate_validation.csv", ["check_id", "description", "severity", "detail"],
              checks)

    by_dec = {v: sum(1 for d in decisions if d[2] == v) for v in DECISIONS.values()}
    by_status = {}
    for c in candidates:
        by_status[c["epistemic_status"]] = by_status.get(c["epistemic_status"], 0) + 1
    by_pol = {}
    for c in candidates:
        by_pol[c["polarity"]] = by_pol.get(c["polarity"], 0) + 1
    log.info("atomic propositions: %d", len(atomic))
    log.info("decisions: %s", by_dec)
    log.info("event candidates: %d", len(candidates))
    log.info("epistemic_status: %s", by_status)
    log.info("polarity: %s", by_pol)
    n_err = sum(1 for c in checks if c[2] == "ERROR")
    n_warn = sum(1 for c in checks if c[2] == "WARNING")
    log.info("validation: ERROR=%d WARNING=%d", n_err, n_warn)
    if n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
