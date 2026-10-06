#!/usr/bin/env python3
"""GuSoon v2 proposition atomicity audit (report only).

Checks whether each of the source_faithful_propositions rows expresses a
single independent proposition. The per-row judgments below are manual
readings of the v2 CSV only (no v1 material, no external sources); this
script attaches them to the current DuckDB rows and writes the reports.

- Reads database/gusun_v2.duckdb read-only. Never modifies raw CSVs or the DB.
- Splits nothing and creates no events, relations, episodes, DAGs or inferences.

Conventions
- outer_speaker: the reporting_actor whose statement/report/judgment/order the
  source records (the source layer itself is implicit on every row).
- embedded_speaker: a party whose own speech (assertion, question, directive,
  written list) is reported inside the outer statement with its content at
  least summarised. A speaker's own earlier utterance counts when its content
  is recorded ("본인 과거 발화").
- independent_claim_count: claims at the content level that can be true or
  false independently; attribution layers (who said what) are not counted.
- split_recommended: YES = components of different kinds or ones that other
  rows contradict independently; OPTIONAL = separable but low risk (one
  directive with several measures, arrival + activity, reason clauses);
  REVIEW = decide after checking the source; NO = keep as is.
- object_level_event_claim_present:
  OUTER_ASSERTED      outer speaker directly asserts a world event/state
  EMBEDDED_ONLY       a world event/state appears only inside embedded speech
  OUTER_AND_EMBEDDED  both
  AS_JUDGMENT         as the content of an evaluation/finding/judgment
  NONE_SPEECH_ACT     order, request, question or permission only

Outputs:
  output/05_v2_proposition_atomicity_audit.csv
  output/06_v2_open_set_audit.csv
  logs/v2_proposition_atomicity_audit.log
"""

import csv
import hashlib
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

CLASS = {
    "A": "ATOMIC",
    "C": "COMPOUND",
    "N": "NESTED_CLAIM",
    "CN": "COMPOUND_AND_NESTED",
    "AM": "AMBIGUOUS",
}
OBJ = {
    "O": "OUTER_ASSERTED",
    "E": "EMBEDDED_ONLY",
    "OE": "OUTER_AND_EMBEDDED",
    "J": "AS_JUDGMENT",
    "S": "NONE_SPEECH_ACT",
}

AUDIT = {}


def R(pid, cls, emb, emb_claim, obj, n, split, proposal, reason, review=False, priority=None):
    assert pid not in AUDIT, pid
    AUDIT[pid] = dict(cls=CLASS[cls], emb=emb, emb_claim="YES" if emb_claim else "NO",
                      obj=OBJ[obj], n=n, split=split, proposal=proposal, reason=reason,
                      review="YES" if review else "NO", priority=priority)


# ---- SRC2_001 (1793-05-12, 이형원 장계·정조 처분) ----
R("P0001", "A", "", 0, "O", 1, "NO", "", "거주지 하나만 서술(STATE).")
R("P0002", "A", "", 0, "O", 1, "NO", "",
  "도난 피해 1개 명제. 다만 '보고됨'이 이형원 자신의 단정인지 구순 측 주장을 전한 것인지 CSV만으로 구분 불가하며, "
  "THEFT_REALITY conflict_group에 속하므로 outer/embedded 판정이 결과에 영향.", True)
R("P0003", "N", "구순", 1, "E", 1, "NO", "",
  "이형원 보고(outer) 안에 구순의 발언(김명신=도적 괴수)이 embedded. embedded claim을 사실로 승격하지 말 것.")
R("P0004", "C", "", 0, "O", 3, "YES",
  "(a) 병영이 김명신을 체포 (b) 달포 이상 구금 (c) 조사·신문 실시",
  "체포·구금기간·조사는 각각 독립적으로 참/거짓 가능. 특히 (c)는 P0107(평범한 신문도 받지 않음)과 독립적으로 충돌할 수 있어 분리 필요.",
  priority=7)
R("P0005", "A", "", 0, "O", 1, "NO", "", "확실한 장물 미발견 1개.")
R("P0006", "C", "", 0, "O", 2, "YES",
  "(a) 김명신 사망 (b) 사망 시점이 구금·조사 이후",
  "사망 occurrence와 '구금·조사 뒤'라는 시간 앵커가 결합. 앵커는 P0004의 조사 전제를 함께 끌고 와 P0107과 충돌 가능. "
  "사인은 포함하지 않음(notes와 일치).", priority=24)
R("P0007", "C", "", 0, "O", 2, "YES",
  "(a) 평민들이 모진 형벌을 받음 (b) 그들이 무고했다는 평가",
  "'무고한'은 피형자 집합을 규정하는 평가로, 형벌 사실과 독립적으로 참/거짓 가능.", priority=23)
R("P0008", "N", "회동 조사 응답자들", 1, "E", 1, "NO", "",
  "이형원 보고 안의 응답자 진술(구순-김명신 원한). 단일 embedded claim.")
R("P0009", "N", "회동 조사 응답자들", 1, "E", 1, "NO", "",
  "이형원 보고 안의 응답자 진술(도난 조작). 단일 embedded claim. THEFT_REALITY에서 층위 구분 필요.")
R("P0010", "CN", "회동 조사 응답자들", 1, "E", 3, "YES",
  "embedded 층에서 (a) 구순이 김명신에게 도적 괴수 누명을 씌움 (b) 행랑 하인을 통함 (c) 교졸을 통함",
  "누명 행위와 두 경로(행랑 하인·교졸)가 한 진술에 결합. 경로는 각각 독립적으로 거짓일 수 있음. '누명'은 김명신 무고 판단도 함축.",
  priority=19)
R("P0011", "N", "미상(진술 주체 불명시)", 1, "E", 1, "NO", "",
  "'진술됐다고 보고됨' — embedded 진술자가 명시되지 않음. 단일 claim(전후 체포자=구순 집이 미워하던 사람).", True)
R("P0012", "C", "", 0, "J", 2, "YES",
  "(a) 이문협이 수사를 병영 비장에게 전적으로 맡김(행위) (b) 방관했다는 평가",
  "위임 사실과 '방관' 평가가 결합. 위임은 사실 차원, 방관은 평가 차원으로 독립 판정 가능.", priority=28)
R("P0013", "C", "", 0, "J", 3, "YES",
  "(a) 이광섭이 특정 말을 믿음 (b) 그 말이 허황함 (c) 무고한 사람을 잘못 체포함",
  "신뢰 행위·말의 허황성·체포 대상의 무고성이 각각 독립.", priority=21)
R("P0014", "C", "", 0, "S", 3, "OPTIONAL",
  "건의 행위 1개 유지 + 처분 3종(파직·나문·엄한 감죄)을 다중값 속성으로",
  "하나의 건의(speech act)에 처분 목록이 담김. 행위를 쪼개면 한 번의 건의가 3건으로 부풀므로 행위 단위 유지 권장.")
R("P0015", "A", "", 0, "S", 1, "NO", "", "윤허 1개. 대상은 P0014 요청 전체(anaphoric).")
R("P0016", "A", "", 0, "J", 1, "NO", "",
  "도난 부재 방향을 수용한 판단 1개. '당시 장계·조사에 따라'는 근거 한정어. '방향' 표현은 판단 강도를 흐리므로 원문 대조 시 유의.")
R("P0017", "C", "", 0, "S", 2, "OPTIONAL",
  "명령 1개 유지 + 내용 목록 (a) 의금부에 잡아 가둠 (b) 엄히 조사",
  "하나의 명령 발화에 두 조치. 이행 여부는 별개지만 명령 자체는 단일.")

# ---- SRC2_002 (1793-05-27, 비변사등록 이조원) ----
R("P0018", "N", "미상('설명' 주체 불명시)", 1, "J", 1, "NO", "",
  "이조원이 '구순 집에 화적이 들었다는 설명'을 이치에 맞지 않는다고 판단. embedded claim(화적 침입)은 판단 대상일 뿐 주장되지 않음. "
  "설명의 주체는 명시되지 않음.")
R("P0019", "C", "", 0, "O", 2, "YES",
  "(a) 김명신이 구순의 이웃으로 거주 (b) 김명신이 구순의 행실을 비판",
  "거주 관계(STATE)와 비판 행위(ACTION)는 독립. P0050(친숙·날마다 왕래)과 관계 서술이 달라 분리 보존 가치 큼.", priority=26)
R("P0020", "C", "", 0, "O", 3, "YES",
  "(a) 구순이 앙심을 품음 (b) 그 원인이 김명신의 비판 (c) 구순이 김명신을 모함하려 함",
  "심리 상태·인과·의도 3개가 결합된 MOTIVE 주장. 각각 독립 반박 가능.", priority=17)
R("P0021", "A", "", 0, "O", 1, "NO", "", "도난 상황 조작 주장 1개.")
R("P0022", "C", "", 0, "O", 2, "YES",
  "(a) 구순이 '지세랑'이라는 말을 만들어냄 (b) 구순이 그 말을 퍼뜨림",
  "창작과 유포는 독립. JISE_ORIGIN의 P0036·P0108·P0109는 (a)만 다루므로 분리하지 않으면 비교가 흐려짐.", priority=15)
R("P0023", "A", "", 0, "O", 1, "NO", "",
  "작은 궤짝 돈 도난을 꾸몄다는 주장 1개. 구순이 그런 피해를 말했다는 전제는 포함되나 독립 명제로 쪼갤 실익 적음.")
R("P0024", "C", "", 0, "O", 2, "YES",
  "(a) 하인 몸의 흔적이 부스럼이었음 (b) 구순이 그것을 창상으로 꾸밈",
  "흔적의 실제 성격과 조작 행위는 독립적으로 참/거짓 가능.", priority=29)
R("P0025", "C", "", 0, "O", 4, "YES",
  "(a) 김명신 사망 (b) 사망 장소=병영 옥 (c) 사망이 구순이 구성한 죄안 때문 (d) 원통한(부당한) 죽음이라는 평가",
  "claim_topic=DEATH_CAUSE이지만 사망 occurrence·장소·인과·평가가 한 row에 결합. P0102/P0106(질병·전염병 사인)과는 (c)만 충돌하므로 분리 필수.",
  priority=2)
R("P0026", "C", "", 0, "O", 2, "YES",
  "(a) 김명신의 아내 사망 (b) 그 사망이 김명신 사망 이후",
  "'따라 죽었다'가 단순 선후인지 인과적 의미(뒤따라 목숨을 끊음 등)인지 CSV만으로 불명. P0106(부처 전염병)과 해석이 갈리므로 검토 필요.",
  True, priority=20)
R("P0027", "C", "", 0, "O", 2, "YES",
  "(a) 병사가 사건을 자세히 조사하지 않음 (b) 하급 보조자에게 맡김",
  "부작위와 위임은 독립. '하급 보조자'의 신원은 미상으로 유지.", priority=27)
R("P0028", "A", "", 0, "O", 1, "NO", "",
  "하급 보조자=구순의 가객이라는 주장 1개. 하급 보조자의 신원은 특정하지 않음(한재욱과 동일시하지 않음).")
R("P0029", "AM", "", 0, "J", 2, "REVIEW",
  "원문 확인 후: 발화 주체(정조/비변사 당상)별로 나눌지 결정; 비판 대상 사실(현장 직접 안핵 안 함)과 비판 행위 구분",
  "reporting_actor가 '정조/비변사 당상'으로 두 주체를 묶어 하나의 비판인지 각자의 발언인지 판정 불가. 내용도 사실(직접 안핵하지 않음)과 비판이 결합.",
  True)
R("P0030", "A", "", 0, "S", 1, "NO", "", "파직 명령 1개.")
R("P0031", "C", "", 0, "S", 2, "OPTIONAL",
  "명령 1개 유지 + 내용 목록 (a) 의금부에 엄히 가둠 (b) 반복 신문",
  "하나의 명령 발화에 두 조치(P0017과 같은 구조).")

# ---- SRC2_003 (1793-05-27, 실록 이조원) ----
R("P0032", "A", "", 0, "J", 1, "NO", "",
  "도난 부재 방향의 판단 보고 1개. P0018과 같은 단계의 교차기록이지만 이 단계에서는 연결하지 않음.")
R("P0033", "C", "", 0, "J", 3, "YES",
  "(a) 이조원이 직접 안핵하지 않음 (b) 전해 들은 말을 서계에 붙임 (c) 정조가 이를 문제 삼음",
  "문제 삼은 사유 두 가지는 독립적으로 참/거짓 가능.", priority=31)

# ---- SRC2_004 (1793-05-28, 승정원일기 홍대협 차하) ----
R("P0034", "C", "", 0, "S", 2, "OPTIONAL",
  "질문 행위 1개 + 질문 주제 2개(구순 사건, 지세랑 호칭)",
  "한 질문 장면에 두 주제. proposition_type=ASSERTION이지만 내용은 질문.")
R("P0035", "A", "", 0, "O", 1, "NO", "", "귀로에 사건 개요를 조금 들었다는 자기 진술 1개. 들은 내용·출처 미기재.")
R("P0036", "C", "", 0, "O", 2, "YES",
  "(a) 예전 호중 화적이 지세랑 호칭을 사용함(근거) (b) 이번에 처음 생긴 말이 아닐 것(추론, '~인 듯')",
  "사실 근거와 유보적 결론이 결합. 근거가 참이어도 결론은 별도로 평가될 수 있음.", priority=18)
R("P0037", "A", "", 0, "S", 1, "NO", "", "조사 명령 1개.")
R("P0038", "A", "", 0, "S", 1, "NO", "", "안핵어사 차하 1개.")

# ---- SRC2_005 (1793-06-11, 윤노동 별단) ----
R("P0039", "CN", "구순", 1, "OE", 3, "YES",
  "(a) 구순이 도적을 만났다고 말함[embedded] (b) 구순이 영교를 부름 (c) 구순이 김명신 등의 이름을 써 줌",
  "embedded 피해 주장·소환 행위·명단 작성 행위가 결합. (c)는 명단 출처(SUSPECT_LIST_ORIGIN)의 핵심이므로 독립 보존 필요.",
  priority=11)
R("P0040", "C", "", 0, "O", 3, "YES",
  "(a) 김명신 사망 (b) 사인=병 (c) 사망 시점이 체포·구금 이후",
  "claim_topic=DEATH_OCCURRENCE이지만 '병들어'가 사인을 포함 → occurrence와 cause가 섞임. 분리 필수.", priority=1)
R("P0041", "A", "", 0, "O", 1, "NO", "", "여러 죄수가 참혹한 형벌을 받았다는 1개(정도 한정어 포함).")
R("P0042", "A", "", 0, "O", 1, "NO", "", "진정한 장물 미획득 1개.")
R("P0043", "CN", "변가의 처(공초)", 1, "OE", 3, "YES",
  "(a) 한재욱이 변가의 처를 꾀어냄 (b) 변가의 처가 '김명신=도적 괴수' 취지로 공초함[embedded] (c) (b)가 (a)의 결과",
  "유도 행위·공초 존재·인과가 독립. '변가의 처'는 이 row에서 자미덕으로 특정되지 않음. "
  "참고(관계 생성 아님): P0081 명시 목록에 김명신 없음, P0092는 '모른다' 응답.", True, priority=6)
R("P0044", "C", "", 0, "S", 2, "OPTIONAL",
  "(a) 보류 건의 (b) 사유: 홍대협 복명 전",
  "사유절은 사실 주장(복명 전)이지만 충돌 위험 낮음.")
R("P0045", "A", "", 0, "S", 1, "NO", "", "보류 윤허 1개.")

# ---- SRC2_006 (1793-06-13, 홍대협 복명·정조 최종 처분) ----
R("P0046", "C", "", 0, "O", 2, "OPTIONAL",
  "(a) 공주목 도착 (b) 관련자들을 차례로 신문",
  "도착과 신문은 분리 가능하나 위험 낮음. '관련자들'은 비열거 집단.")
R("P0047", "C", "", 0, "O", 2, "OPTIONAL",
  "(a) 명업=구순 집 계집종의 남편 (b) 바깥사랑에 거주",
  "신분 관계와 거주지는 독립이나 충돌 위험 낮음.")
R("P0048", "N", "나복", 1, "E", 1, "NO", "",
  "3층 구조: 명업 진술(확실) / 나복의 알림(embedded) / 실제 도적 침입(object-level). "
  "날짜(2월 22일 밤)가 알림 시점인지 침입 시점인지 CSV에서 구분되지 않음.", True)
R("P0049", "CN", "나복 (+2차: 도적의 '지세대감' 자칭)", 1, "E", 5, "YES",
  "embedded 층에서 (a) 도적 30여 명 (b) 횃불 지참 (c) 침입 (d) '지세대감' 자칭 (e) 돈·물품 절도 를 분리; "
  "명업 진술(outer)·나복 발언(embedded)·object-level 층 구분 유지",
  "인원·횃불·자칭·절도는 독립적으로 참/거짓 가능(예: P0099는 규모를 좀도둑 수준으로 평가). 자칭은 도적의 발화로 2차 중첩.",
  priority=3)
R("P0050", "C", "", 0, "O", 2, "OPTIONAL",
  "(a) 본래 친숙한 관계 (b) 날마다 왕래",
  "관계와 그 근거 행동. 분리 가능하나 위험 낮음.")
R("P0051", "A", "", 0, "O", 1, "NO", "",
  "2월 초 박거사 일로 편지를 보내 힐책한 행위 1개(시점·주제·매체는 속성).")
R("P0052", "A", "", 0, "O", 1, "NO", "", "왕래 단절 상태 1개. '그 뒤'는 P0051에 대한 anaphoric 시간 앵커.")
R("P0053", "C", "구순(소장, 내용 미기재)", 0, "O", 2, "YES",
  "(a) 구순이 소장을 올림 (b) 체포령이 내려짐",
  "행위 주체가 다름(구순 vs 관). '올려'가 인과를 함축. 체포령 대상 미기재.", priority=30)
R("P0054", "C", "", 0, "O", 2, "OPTIONAL",
  "(a) 장교 1명이 찾아옴 (b) 구순이 그를 안행랑으로 불러 조용히 대화",
  "한 장면의 연속 행위. 분리 가능하나 위험 낮음.")
R("P0055", "CN", "명업(본인 과거 병영 공초)", 1, "OE", 4, "YES",
  "(a) 처음 공초에서 사실대로 말함 (b) 위협을 받음/두려워함 (c) '도적이 없었다'는 취지로 진술을 바꿈 (d) 변경 원인=위협",
  "진술 번복의 경위와 원인이 결합. '사실대로'는 현재 시점의 자기 평가. 과거 진술 내용(도적 없음)은 embedded claim으로 별도 층.",
  priority=10)
R("P0056", "A", "", 0, "O", 1, "NO", "", "비장청 소환 1개.")
R("P0057", "N", "한재욱(지시)", 0, "S", 1, "NO", "",
  "이진욱 진술 속 한재욱의 지시 1개. 수령자 '이진욱·조계완 등'은 open set인데 set_status=NOT_APPLICABLE(06 참조).")
R("P0058", "N", "한재욱(지시)", 0, "S", 1, "NO", "", "체포 지시 1개(대상 2인 폐쇄 목록).")
R("P0059", "A", "", 0, "O", 1, "NO", "",
  "철편 4개를 만들어 준 행위 1개. notes상 주어(한재욱)는 문맥 판독이므로 주어 귀속 확인 필요.", True)
R("P0060", "CN", "한재욱", 1, "E", 3, "YES",
  "embedded 층에서 (a) 변지돌·정원돌=처남매부 (b) 변지돌이 힘이 셈 (c) 조심하라는 주의",
  "친족관계 주장·힘 묘사·주의 지시는 독립. 친족관계는 인물 식별에 쓰일 수 있어 분리 가치 큼.", priority=22)
R("P0061", "A", "", 0, "O", 1, "NO", "", "변지돌이 이미 공주진에 잡혀간 상태 1개.")
R("P0062", "C", "", 0, "O", 3, "YES",
  "(a) 장교들이 자미덕을 체포 (b) 자미덕만 잡음(다른 대상 미체포) (c) 자미덕=재돌의 처, 재돌=변지돌의 아우",
  "체포 사실과 친족 식별이 결합. (c)는 person_membership의 변재돌/재돌 동일성 문제와 직결되므로 별도 명제로 분리 권장(동일시는 하지 않음).",
  priority=12)
R("P0063", "C", "", 0, "O", 2, "OPTIONAL",
  "(a) 자미덕을 데리고 구순 집으로 감 (b) 구순에게 도난 상황을 물음",
  "이동과 질문. 분리 가능하나 위험 낮음.")
R("P0064", "N", "구순", 1, "E", 1, "NO", "", "구순이 잃은 물건을 열거함(목록 내용 미기재).")
R("P0065", "N", "구순 (+2차: 도적의 '지세대사' 자칭)", 1, "E", 1, "NO", "",
  "3층: 이진욱 진술 / 구순 발언 / 도적의 자칭. P0049('지세대감')와 호칭이 다르므로 층위를 섞지 말 것.")
R("P0066", "N", "이광섭(지시)", 0, "S", 1, "NO", "",
  "이광섭의 체포 지시 1개. object_or_content는 '김명신·김갑득'으로 해소돼 있으나 predicate는 '풍각/흥덕 김생원'; "
  "식별은 P0067/P0068에 따로 있어 object 필드에 식별 결과가 선반영됨.", True)
R("P0067", "A", "", 0, "O", 1, "NO", "",
  "식별 1개(풍각 김생원=김명신). '식별됨'의 주체(이진욱 진술인지 기사 서술인지)가 CSV에서 불명.", True)
R("P0068", "A", "", 0, "O", 1, "NO", "",
  "식별 1개(흥덕 김생원=김갑득). '식별됨'의 주체가 CSV에서 불명.", True)
R("P0069", "C", "", 0, "O", 2, "OPTIONAL",
  "(a) 김명신·김갑득을 잡아옴 (b) 병사 분부에 따름(권한 근거)",
  "체포 사실과 권한 근거. 두 사람의 체포도 각각 독립이나 같은 행위로 유지 가능.")
R("P0070", "C", "", 0, "O", 2, "OPTIONAL",
  "(a) 구순 집에 들름 (b) 풍각 김생원을 잡으러 가는 길(목적)",
  "방문과 목적. 분리 가능하나 위험 낮음.")
R("P0071", "N", "구순(질문)", 0, "S", 1, "NO", "",
  "구순의 질문 1개. '다시'는 앞선 방문을 전제.")
R("P0072", "N", "조계완(본인 과거 발화)", 1, "E", 1, "NO", "",
  "자신의 과거 답변(풍각 상주를 잡으러 옴)을 재진술. 답변 내용은 embedded.")
R("P0073", "N", "구순", 1, "E", 1, "NO", "", "구순의 반응 발언 1개('취지로' 의역).")
R("P0074", "CN", "구순(요구)", 0, "O", 2, "OPTIONAL",
  "(a) 서찰 1장을 건넴 (b) 병사에게 전해달라고 요구",
  "전달 행위와 요구 발화. 서찰 내용 미기재.")
R("P0075", "A", "", 0, "O", 1, "NO", "", "재돌이 아산에 나가 있었다는 상태 1개.")
R("P0076", "A", "", 0, "O", 1, "NO", "", "자미덕을 병영으로 붙잡아 감 1개.")
R("P0077", "CN", "병영(도적 지목)", 1, "OE", 2, "OPTIONAL",
  "(a) 한 차례 신문 (b) 신문 측이 자미덕을 도적이라 함",
  "신문 행위와 지목 발화. 지목 내용(자미덕=도적)은 embedded.")
R("P0078", "A", "", 0, "O", 1, "NO", "", "신문 뒤 비장청 다모방 구류 1개.")
R("P0079", "A", "", 0, "O", 1, "NO", "",
  "매일 불러들인 반복 행위 1개. '한 비장'이 성씨 한(韓)인지 '어떤 비장'인지는 CSV만으로 확정하지 않음(named_entities도 '한 비장'으로 별도 표기).")
R("P0080", "N", "한 비장", 1, "E", 1, "NO", "",
  "embedded claim(재돌이 이미 체포됨)을 사실로 승격 금지. P0075(재돌 아산 체류)와 층위가 다름.")
R("P0081", "CN", "한 비장 (+조건절 속 자미덕의 가정적 진술)", 1, "E", 2, "YES",
  "(a) 조건/유도: 자미덕이 정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적이라고 말할 것 [대상 명단은 하나의 OPEN_SET_EXPLICIT_MEMBERS로 유지] "
  "(b) 대가: 자미덕과 남편을 다음 날 석방하겠다는 약속; 두 부분이 하나의 조건문 발화였다는 연결은 보존",
  "회유 조건(대상 명단)과 대가(석방 약속)는 독립적으로 참/거짓 가능. 원 발화가 조건문이므로 '요구'는 해석이며, 분리해도 같은 발화에서 나왔음을 표시해야 함. "
  "재돌(남편)은 수혜 대상이지 대상 명단 구성원이 아님. '등'이 있어 OPEN_SET_EXPLICIT_MEMBERS 적절.", priority=4)
R("P0082", "A", "", 0, "O", 1, "NO", "", "떡과 밥을 준 행위 1개.")
R("P0083", "A", "", 0, "O", 1, "NO", "",
  "자미덕·이집거 양자가 참여한 대질 1건으로 원자적(단방향 actor-target로 축약하지 않음). 주관자·시점·장소 미기재. "
  "근거가 자미덕 진술이므로 object-level 사건으로 확정된 것은 아님.")
R("P0084", "C", "자미덕(본인 과거 대질 발언, 내용 미기재)", 0, "O", 3, "YES",
  "(a) 대질에서 자미덕이 발언함 (b) 그 발언이 거짓으로 꾸며진 것 (c) 한 비장의 지휘에 따른 것",
  "'거짓 발언'(자기 번복)과 '한 비장의 지휘'(타인 행위 귀속)는 독립 claim: 스스로 거짓말했을 수도, 지휘는 있었으나 내용은 참일 수도 있음. "
  "거짓의 내용은 미기재라 embedded claim으로 떼어낼 내용은 없음.", priority=5)
R("P0085", "AM", "", 0, "O", 1, "REVIEW",
  "원문 확인 후 독립 명제('구순 집 도난이 진영에 정소됨')로 재진술할지, P0086의 시간 한정어로 둘지 결정",
  "predicate가 '~정소된 뒤였다'는 종속절 형태로, 무엇이 그 뒤였는지(주절)는 P0086에 있음. 단독으로 명제 경계 판정 곤란.", True)
R("P0086", "C", "", 0, "O", 2, "YES",
  "(a) 한재욱이 병영 아전 유제희를 내보냄 (b) 목적=도적 진상 탐지",
  "파견 사실과 진술자 본인이 밝힌 목적은 독립. 목적은 피진술자 측 자기정당화일 수 있어 COACHING 판단과 분리 보존 필요.", priority=25)
R("P0087", "N", "유제희(기록 명단)", 1, "E", 1, "NO",
  "명단 1건 유지(OPEN_SET_EXPLICIT_MEMBERS) + 필요 시 prop_id를 참조하는 파생 member index(비권위적)",
  "유제희가 명단을 적어온 행위는 1건. 인물별 7개 row로 쪼개면 ①한 번의 기록 행위가 7건 증거로 부풀고 ②'등'(미명시 구성원)을 표현할 수 없으며 "
  "③명단에 없는 인물=비구성원이라는 오독 위험. 장점(인물별 질의·교차 비교)은 파생 index로 얻을 수 있음. 명단의 성격(용의자 명단 등)은 predicate에 명시되지 않음.")
R("P0088", "N", "유제희", 1, "E", 1, "NO", "",
  "명단 출처 주장(직접 염탐). P0096/P0097(구순의 말을 함께 기록)과 출처 서술이 달라 층위 보존 필요.")
R("P0089", "C", "", 0, "O", 2, "YES",
  "(a) 자미덕을 방안으로 부름 (b) 남은 밥을 줌",
  "부분 인정 2개. P0079(매일 불러들임)·P0082(떡과 밥)와 빈도·음식에서 차이가 있어 분리 시 비교가 명확.", priority=32)
R("P0090", "CN", "유제희 (+2차: 석단 공초)", 1, "E", 2, "YES",
  "(a) 유제희가 '석단 공초에서 김명신=도적 괴수'라고 전함[2차 embedded] (b) 유제희가 자미덕에게 다시 물어보라고 권함",
  "석단의 공초 내용은 한재욱→유제희→석단 3단 중첩. 정보 전달과 권유는 독립.", priority=13)
R("P0091", "C", "", 0, "O", 2, "YES",
  "(a) 한재욱이 자미덕에게 다시 물음 (b) 그 이유=유제희의 말",
  "재질문 사실과 책임 귀속(유제희 말에 따름)은 독립. 귀속은 자기변호일 수 있음.", priority=33)
R("P0092", "N", "자미덕", 1, "E", 1, "NO", "", "자미덕의 '모른다' 응답 1개.")
R("P0093", "A", "", 0, "O", 1, "NO", "",
  "사주 부인 1개로 독립 claim. 부인 범위가 '은밀히 사주'로 한정됨. P0089(부분 인정)와 논리적으로 양립 가능하므로 별도 row 유지가 적절.")
R("P0094", "A", "", 0, "O", 1, "NO", "", "구순과 모르는 사이라는 진술 1개.")
R("P0095", "A", "", 0, "O", 1, "NO", "", "현지 탐문 1개.")
R("P0096", "N", "구순", 1, "E", 1, "NO", "",
  "구순 발언(풍각 김상제도 극히 수상) 1개. '도'는 다른 수상자의 존재를 전제. object_or_content는 '김명신'으로 해소돼 있으나 "
  "predicate는 '풍각 김상제' — 식별 선반영.", True)
R("P0097", "CN", "구순('그 말', 내용은 P0096)", 1, "E", 2, "OPTIONAL",
  "(a) 구순의 말을 기록 (b) 원돌 등의 이름을 기록 — 문서 1건으로 유지 가능",
  "한 문서에 구순 발언과 이름 목록이 함께 담김. named_entities는 '원돌'을 정원돌로 해소(predicate는 '원돌'). "
  "set_status=OPEN_SET이나 명시 구성원(원돌)이 있음(06 참조).", True)
R("P0098", "C", "", 0, "J", 2, "OPTIONAL",
  "(a) 도난 실재 (b) 규모 '약간'",
  "규모는 P0099가 따로 담으므로 이 row를 실재 판단으로 한정하면 중복 회피.")
R("P0099", "A", "", 0, "J", 1, "NO", "", "규모 평가(좀도둑 수준) 1개. 도난 실재는 전제.")
R("P0100", "A", "", 0, "J", 1, "NO", "", "지세 호칭 기원 미확정 1개(조사 경위는 한정어).")
R("P0101", "C", "", 0, "J", 5, "YES",
  "(a) 구순이 과장함 (b) 아전이 거짓 보고함 (c) 이광섭이 그것을 믿음 (d) 장물 없음 (e) 이광섭이 큰 도적으로 판단",
  "책임이 구순·아전·이광섭 3자에 나뉘어 귀속. '아전'은 이 row에서 특정되지 않음(유제희로 동일시하지 않음).", priority=14)
R("P0102", "A", "", 0, "J", 1, "NO", "",
  "사인(질병) 판단만 담음. 사망 occurrence는 전제일 뿐 별도 주장 없음 — 섞이지 않음.")
R("P0103", "C", "", 0, "J", 4, "YES",
  "(a) 이문협이 장물부터 확보하지 않음 (b) 장교·나졸을 풀어 평민을 잡음 (c) 병영 비장의 지휘가 있었음 (d) 그 지휘대로 죄를 얽음",
  "이문협 행위 평가와 '병영 비장 지휘'라는 제3자 행위 주장이 결합. 비장은 특정되지 않음.", priority=16)
R("P0104", "A", "", 0, "J", 1, "NO", "", "쟁점을 세 의안으로 나눈 행위 1개(내용은 쟁점 목록).")
R("P0105", "A", "", 0, "J", 1, "NO", "", "도난 실재 판단 1개.")
R("P0106", "C", "", 0, "J", 2, "YES",
  "(a) 김명신 사인=전염병 (b) 김명신 아내 사인=전염병",
  "'부처'로 두 사람의 사인을 묶음. 사망 occurrence는 전제로만 존재(섞이지 않음). 아내 쪽은 P0026('따라 죽었다')과 해석이 갈릴 수 있어 인물별 분리 필요. "
  "P0102의 '질병'과 표현 수준이 다름.", priority=9)
R("P0107", "C", "", 0, "J", 2, "YES",
  "(a) 곤장을 맞지 않음 (b) 평범한 신문도 받지 않음",
  "두 부정 명제는 독립. (b)는 P0004/P0006의 '조사' 서술과 따로 충돌.", priority=8)
R("P0108", "C", "", 0, "J", 3, "OPTIONAL",
  "호칭별 (a) 지세대감 (b) 지세대사 (c) 지세랑 이 예전 좀도둑들도 쓰던 말",
  "세 호칭을 한 계열로 묶는 판단도 함축. 호칭별로 근거가 다를 수 있음.")
R("P0109", "A", "", 0, "J", 1, "NO", "", "지세 호칭 창작 죄를 면한다는 판단 1개.")
R("P0110", "A", "", 0, "S", 1, "NO", "",
  "감형 후 외딴 섬 정배 처분 1개. P0111(신지도 정배)과 같은 처분의 두 표현일 가능성 — 이 단계에서는 연결하지 않음.", True)
R("P0111", "A", "", 0, "S", 1, "NO", "", "신지도 정배 1개.")
R("P0112", "A", "", 0, "S", 1, "NO", "", "영동현 유배 1개.")
R("P0113", "C", "", 0, "S", 2, "OPTIONAL",
  "명령 1개 유지 + 내용 (a) 도백이 세 차례 엄히 형장 (b) 먼 섬의 종으로 보냄",
  "명령 내용이 두 조치. named_entities가 '한가'를 한재욱으로 해소(predicate는 '한가') — 식별 선반영 여부 확인 필요.", True)
R("P0114", "A", "", 0, "S", 1, "NO", "", "파직 명령 1개.")
R("P0115", "A", "", 0, "S", 1, "NO", "", "유임 명령 1개.")

# ---- SRC2_008 / SRC2_009 (secondary background) ----
R("P0116", "C", "", 0, "O", 2, "OPTIONAL",
  "(a) 1750년 출생 (b) 1793년 호서안핵어사 역임",
  "2차 배경 서술. 생년과 관력은 독립이나 사건 판단에 쓰지 않는 row.")
R("P0117", "C", "", 0, "O", 2, "OPTIONAL",
  "(a) 생몰 1739~1798 (b) 관찰사·비변사제조 등 역임",
  "2차 배경 서술. 생몰과 관력은 독립.")


# ---- open-set audit (06) ----
# set_description, explicit_members, open_marker_present, recommended, notes
OPEN_SETS = {
    "P0007": ("형벌을 받은 '무고한 평민들'", "", "NO(비열거 복수 집단)", "OPEN_SET",
              "현행 유지. 집합이 '무고한'이라는 평가로 규정됨(05의 P0007 분리 제안 참조)."),
    "P0008": ("회동 조사 응답자들(진술 주체 집단)", "", "NO(비열거 복수 집단)", "OPEN_SET",
              "P0007/P0011/P0041은 비열거 복수 집단을 OPEN_SET으로 표기하나 같은 성격의 이 row는 NOT_APPLICABLE — 표기 기준 통일 여부 결정 필요."),
    "P0009": ("회동 조사 응답자들(진술 주체 집단)", "", "NO(비열거 복수 집단)", "OPEN_SET", "P0008과 같음."),
    "P0010": ("회동 조사 응답자들(진술 주체 집단)", "", "NO(비열거 복수 집단)", "OPEN_SET", "P0008과 같음."),
    "P0011": ("구순 집이 미워하던 사람들이라 진술된 '전후 체포자들'", "", "NO(비열거 복수 집단)", "OPEN_SET", "현행 유지."),
    "P0039": ("구순이 영교에게 써 준 이름들", "김명신", "YES('김명신 등')", "OPEN_SET_EXPLICIT_MEMBERS",
              "명시 구성원(김명신)이 있으므로 P0081/P0087과 같은 값이 일관됨."),
    "P0041": ("참혹한 형벌을 받은 '여러 죄수'", "", "NO(비열거 복수 집단)", "OPEN_SET", "현행 유지."),
    "P0046": ("홍대협이 차례로 신문한 '관련자들'", "", "NO(비열거 복수 집단)", "OPEN_SET",
              "predicate 안의 비열거 집단. set_status가 어느 논항(주어/목적어)을 가리키는지 스키마에 없음."),
    "P0057": ("한재욱 지시의 수령자", "이진욱|조계완", "YES('이진욱·조계완 등')", "OPEN_SET_EXPLICIT_MEMBERS",
              "object_or_content에 '등'이 있으나 NOT_APPLICABLE로 표기됨."),
    "P0062": ("자미덕을 잡은 '이진욱 등 장교'(주어 집합)", "이진욱", "YES('이진욱 등')", "OPEN_SET_EXPLICIT_MEMBERS",
              "열린 집합이 주어 쪽에 있음. 현 set_status는 논항 위치를 구분하지 못함."),
    "P0063": ("'장교 일행'(주어 집합)", "", "NO(비열거 복수 집단)", "OPEN_SET",
              "P0062의 '이진욱 등 장교'와 같은 집단인지 이 단계에서 연결하지 않음."),
    "P0069": ("'장교 일행'(주어 집합)", "", "NO(비열거 복수 집단)", "OPEN_SET",
              "목적어 '김명신·김갑득'은 '등' 없는 2인 폐쇄 목록. 열린 집합은 주어 쪽."),
    "P0081": ("자미덕 진술: 한 비장이 큰 도적이라고 말하라고 한 대상", "정원돌|이집거|김갑득|김성손|김흥득", "YES('등')",
              "OPEN_SET_EXPLICIT_MEMBERS", None),
    "P0087": ("한재욱 진술: 유제희가 성명을 적어온 명단", "변지돌|변재돌|정원돌|김명신|김성손|김흥득|김흥길", "YES('등')",
              "OPEN_SET_EXPLICIT_MEMBERS", None),
    "P0097": ("유제희가 구순의 말과 함께 기록한 이름들", "원돌", "YES('원돌 등')", "OPEN_SET_EXPLICIT_MEMBERS",
              "명시 구성원(원돌)이 있음. named_entities는 '정원돌'로 해소했으나 predicate 표기는 '원돌' — 해소 근거 확인 필요."),
    "P0117": ("이형원이 역임한 관직 목록", "관찰사|비변사제조", "YES('등')", "NOT_APPLICABLE",
              "'등'이 인물이 아니라 관직 목록에 붙음. 인물 집합용 set_status 대상이 아니므로 현행 유지."),
}

PRIORITY_TOP = 15

log = logging.getLogger("v2_atomicity")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "v2_proposition_atomicity_audit.log", mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    expected_sha = {}
    for line in SHA_PATH.read_text(encoding="utf-8").splitlines():
        h, fn = line.split("  ", 1)
        expected_sha[fn] = h
    for fn, h in expected_sha.items():
        if sha256(RAW_DIR / fn) != h:
            log.error("Raw CSV differs from recorded SHA-256: %s", fn)
            sys.exit(1)
    log.info("Raw CSV SHA-256 match recorded values (%d files)", len(expected_sha))

    con = duckdb.connect(str(DB_PATH), read_only=True)
    cur = con.execute("SELECT * FROM source_faithful_propositions ORDER BY prop_id")
    cols = [d[0] for d in cur.description]
    props = [{c: ("" if v is None else v) for c, v in zip(cols, row)} for row in cur.fetchall()]
    cur = con.execute("SELECT * FROM person_membership")
    mcols = [d[0] for d in cur.description]
    membership = [dict(zip(mcols, row)) for row in cur.fetchall()]
    con.close()

    ids = [p["prop_id"] for p in props]
    missing = sorted(set(ids) - set(AUDIT))
    extra = sorted(set(AUDIT) - set(ids))
    if missing or extra:
        log.error("Audit coverage mismatch: missing=%s extra=%s", missing, extra)
        sys.exit(1)
    log.info("Audited %d / %d propositions", len(AUDIT), len(props))

    # ---- 05 atomicity audit ----
    rows05 = []
    for p in props:
        a = AUDIT[p["prop_id"]]
        rows05.append([
            p["prop_id"], a["cls"], p["subject"], p["predicate"], p["object_or_content"],
            p["reporting_actor"], a["emb"], a["emb_claim"], a["obj"], a["n"], a["split"],
            a["proposal"], a["reason"], a["review"],
        ])
    write_csv(OUT_DIR / "05_v2_proposition_atomicity_audit.csv",
              ["prop_id", "atomicity_class", "current_subject", "current_predicate",
               "current_object_or_content", "outer_speaker", "embedded_speaker",
               "embedded_claim_present", "object_level_event_claim_present",
               "independent_claim_count", "split_recommended", "proposed_split_description",
               "reason", "manual_review_required"],
              rows05)

    # ---- 06 open-set audit ----
    by_id = {p["prop_id"]: p for p in props}
    sets = {pid: set(v[1].split("|")) for pid, v in OPEN_SETS.items() if pid in ("P0081", "P0087")}
    a_set, b_set = sets["P0081"], sets["P0087"]
    inter = sorted(a_set & b_set)
    a_only = sorted(a_set - b_set)
    b_only = sorted(b_set - a_set)

    def members_present(pid, members):
        text = by_id[pid]["predicate"] + " " + by_id[pid]["object_or_content"]
        return [m for m in members if m not in text]

    def membership_match(col, members):
        direct = {m["person"] for m in membership if m[col] == "DIRECT"}
        return direct == set(members), sorted(direct - set(members)), sorted(set(members) - direct)

    compare = (f"[A=P0081 vs B=P0087, 이름 문자열 기준 비교일 뿐 인물 동일성·관계를 만들지 않음] "
               f"교집합={'·'.join(inter)}; A에만={'·'.join(a_only)}; B에만={'·'.join(b_only)}. "
               f"두 집합 모두 '등'으로 열려 있으므로 '한쪽에만 명시'는 다른 쪽 비구성원을 뜻하지 않음.")
    ok_a, xa, ya = membership_match("jamideok_big_thief_list", a_set)
    ok_b, xb, yb = membership_match("yu_jehee_list", b_set)
    auto_notes = {
        "P0081": (f"{compare} 집합 성격: 한 비장이 자미덕에게 큰 도적이라 말하게 한 대상(조건절 안의 발화 내용). "
                  f"수혜자(자미덕·남편 재돌)는 구성원이 아님. person_membership.jamideok_big_thief_list=DIRECT와 "
                  f"{'일치' if ok_a else f'불일치(+{xa} -{ya})'}."),
        "P0087": (f"{compare} 집합 성격: 유제희가 적어온 성명 목록(한재욱 진술 속 embedded). 목록의 용도는 predicate에 명시되지 않음. "
                  f"변재돌과 P0062/P0080의 '재돌'은 동일시하지 않음. person_membership.yu_jehee_list=DIRECT와 "
                  f"{'일치' if ok_b else f'불일치(+{xb} -{yb})'}."),
    }
    rows06 = []
    for pid in sorted(OPEN_SETS):
        desc, members, marker, rec, note = OPEN_SETS[pid]
        p = by_id[pid]
        if pid in ("P0081", "P0087"):
            absent = members_present(pid, members.split("|"))
            if absent:
                log.error("%s explicit members not found in predicate: %s", pid, absent)
                sys.exit(1)
        rows06.append([pid, desc, members, marker, p["set_status"], rec, note or auto_notes[pid]])
    write_csv(OUT_DIR / "06_v2_open_set_audit.csv",
              ["prop_id", "set_description", "explicit_members", "open_marker_present",
               "set_status_current", "set_status_recommended", "notes"],
              rows06)

    # ---- summary ----
    counts = {c: 0 for c in CLASS.values()}
    splits = {}
    for a in AUDIT.values():
        counts[a["cls"]] += 1
        splits[a["split"]] = splits.get(a["split"], 0) + 1
    for c, n in counts.items():
        log.info("%s: %d", c, n)
    log.info("split_recommended: %s", splits)
    log.info("manual_review_required=YES: %d", sum(1 for a in AUDIT.values() if a["review"] == "YES"))
    log.info("open-set audit rows: %d (set_status changes recommended: %d)", len(rows06),
             sum(1 for r in rows06 if r[4] != r[5]))
    log.info("Set comparison: %s", compare)
    ranked = sorted((a["priority"], pid) for pid, a in AUDIT.items() if a["priority"] is not None)
    log.info("Top %d split candidates:", PRIORITY_TOP)
    for rank, (_, pid) in enumerate(ranked[:PRIORITY_TOP], 1):
        a = AUDIT[pid]
        log.info("  %2d. %s [%s, claims=%d] %s", rank, pid, a["cls"], a["n"], a["proposal"])


if __name__ == "__main__":
    main()
