#!/usr/bin/env python3
"""《시곡》 가능세계 계산기 — 제약충족(CSP)·시간제약네트워크(TCN)·구조적 인과모형(SCM).

실행:  python 03_constraints.py          (results/, 05~08 산출물 생성)

설계 원칙
---------
1. 시간: 음력 '서수 인덱스' L(y,m,d) = ((y-1780)*12 + (m-1))*30 + (d-1).
   - 양력 변환이 아니다. 실제 월 길이(29/30일)와 윤달을 반영하지 않으므로 L 간의 차이는
     ±1일(월 경계), 윤달이 끼면 ±30일 수준의 오차를 가질 수 있다. '약 40일' 같은 사료 표현은
     허용 구간으로만 쓴다. 해석 결과 날짜는 항상 "음력 서수 근사"로 표기한다.
2. 모든 제약은 ID·층위(layer)·근거(claim/source ID)를 가진다. 층위:
     STR       모형 구조(사건 정의상 순서)                → 항상 강제
     INST      제도 규칙(포폄 시기·평가자 등)             → 분석에서 완화 가능
     HIST_T    사료 연대 앵커(성옥·격쟁·판부 등)          → 모드별 채택/완화
     HIST_TEN  인사 연표 앵커(부임·재임·후임)             → 모드별 채택/완화
     HIST_C    사료가 서술한 인과적 사실(무고·농요 등)     → H·F 모두 유지
     FILM_REQ  사용자가 정한 극중 필수 조건               → F 모드 강제
     FILM_SYN  시놉시스 v4의 구체적 선택(날짜 등)         → 비교용(완화 가능)
     SCM       구조방정식(이론·극중 가정에 의한 인과 연결) → 항상 강제(개입 시 해당 식만 절단)
     COUPLE    인과 변수와 시간의 연결                   → 항상 강제
3. 확률·가중치를 쓰지 않는다. 비교는 SAT/UNSAT, 최소 충돌집합(MUS), 최소 수정집합(MCS),
   개수(카디널리티) 최소화와 파레토 비지배로만 한다.
"""
from __future__ import annotations

import csv
import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import networkx as nx
import z3

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

# ───────────────────────────── 1. 음력 서수 인덱스 ─────────────────────────────
BASE_YEAR = 1780


def L(y: int, m: int, d: int = 1) -> int:
    """음력 (년, 월, 일) → 서수 인덱스. 양력 변환 아님."""
    if not (1 <= m <= 12 and 1 <= d <= 30):
        raise ValueError((y, m, d))
    return ((y - BASE_YEAR) * 12 + (m - 1)) * 30 + (d - 1)


def month_range(y: int, m: int) -> tuple[int, int]:
    return L(y, m, 1), L(y, m, 30)


def fmt(idx: int) -> str:
    mi, d = divmod(idx, 30)
    y, m = divmod(mi, 12)
    return f"{BASE_YEAR + y}년 음력 {m + 1}월 {d + 1}일(서수 근사)"


def fmt_month(idx: int) -> str:
    mi, _ = divmod(idx, 30)
    y, m = divmod(mi, 12)
    return f"{BASE_YEAR + y}-L{m + 1:02d}"


LO, HI = L(1778, 1, 1), L(1785, 12, 30)

EVENTS = {  # 이벤트명: (변수 ID, 설명)
    "KJR_START": ("T1", "권중립 백천군수 재임 시작"),
    "KJR_END": ("T1", "권중립 백천군수 재임 종료"),
    "JSJ_ARRIVE": ("T2", "조상진 황해감사 부임"),
    "JSJ_END": ("T2", "조상진 황해감사 재임 종료"),
    "LKY_START": ("T3", "이경양 황해감사 재임 확인 시점 이전의 부임"),
    "RELIEF_ADMIN": ("A5", "권중립의 구휼 행정(평가 대상) 시행"),
    "COMPLAINT": ("A9", "강제 권분 관련 주민 항의가 관아에 접수"),
    "POPHYEOM": ("T5", "권중립에 대한 포폄(평가) 시점"),
    "HOSTILITY": ("S7", "주민의 윤씨 적대감 형성"),
    "DEATH": ("T8", "윤씨 사망"),
    "BURIAL": ("T9", "윤씨 매장"),
    "MONEY_DEMAND": ("T10", "이가원의 금전 요구"),
    "SONG": ("T11", "이가원의 농요 제작·유포 시작"),
    "INSTIGATE": ("T12", "조환 사주"),
    "ACCUSE": ("T13", "공식 고발"),
    "CHOGEOM": ("T14", "권중립 초검"),
    "BOKGEOM": ("T15", "이우배 복검"),
    "OKSA": ("T16", "옥사 성립"),
    "DETAIN_START": ("T17", "조재항 구금 시작"),
    "REVIEW_ORDER": ("T18", "정조의 재조사 명령"),
    "JSJ_REINVEST": ("J9", "조상진 주관 재조사 수행"),
    "HYEONGJO_1781_8": ("J8", "형조 심리·판부(심리록 신축 8월)"),
    "JOKJAENG": ("T19", "조재정 격쟁"),
    "FINAL": ("T20", "최종 판부(방면)"),
    "DETAIN_END": ("T17", "조재항 구금 종료"),
    "JSJ_LEARN": ("A11", "조상진이 강압을 알게 된 시점"),
    "LGW_PRE_CONTACT": ("M6", "이가원과 살해 주도자의 사전 접촉(사전 관여 세계에서만)"),
}

# ───────────────────────────── 2. 인과 변수(SCM) ─────────────────────────────
# 외생 변수: (변수 ID, 설명, 층위)  층위 = 'creative'(극중 가정) | 'hist'(사료가 직접 서술) | 'inference'(사료로부터의 추론)
EXOG = {
    "u_shortage": ("E13", "일부 가구의 식량 부족", "creative"),
    "u_elite_evade": ("E7", "상층 지주의 권분 회피", "creative"),
    "e5_cannot_evade": ("E5", "조재항의 강제 권분 회피 불가(서민지주·요호부민 설정)", "creative"),
    "u_extra_exceeds": ("E9", "추가 요구량 > 가용량 (시나리오 산술)", "creative"),
    "u_yun_other_reason": ("F2", "윤씨의 비경제적 거절 사유", "creative"),
    "kjr_coercive": ("A2", "권중립 권분 운영의 강압성(늑분)", "creative"),
    "kjr_knew_coercion": ("A10", "권중립이 강압을 인지", "creative"),
    "a5_inflated": ("A5", "구휼 실적 과장", "creative"),
    "kjr_shifts_blame": ("S2", "권중립의 책임 전가", "creative"),
    "lgw_selective": ("S3", "이가원의 선택적 정보 공개", "creative"),
    "u_resident_rumor": ("S1", "주민 간 자생적 비난 소문", "creative"),
    "s4_prior_known": ("S4", "윤씨의 기존 출연이 주민에게 널리 알려짐", "creative"),
    "u_trigger": ("S11", "살인을 촉발한 구체적 사건", "creative"),
    "premeditated": ("S9", "일부 주도자의 사전 살해 결의", "creative"),
    "u_spont_intent": ("S9", "현장에서 형성된 살해 의도", "creative"),
    "jsj_good_pophyeom": ("A7", "조상진의 권중립 긍정 포폄", "creative"),
    "pophyeom_by_jsj": ("T6", "포폄 평가자가 조상진", "creative"),
    "jsj_knew_at_pophyeom": ("A11", "포폄 당시 조상진의 강압 인지", "creative"),
    "jsj_learned_later_no_correct": ("A11", "포폄 후 인지했으나 정정하지 않음", "creative"),
    "u_jsj_supervisory_fear": ("A13", "감독 책임 추궁에 대한 우려(포폄과 무관)", "creative"),
    "u_kjr_reward_expect": ("A6", "권중립의 인사상 이익 기대(포폄 외 경로)", "creative"),
    "jsj_direct_investigation": ("J9", "조상진의 직접 조사", "hist"),
    "lgw_money_refused": ("M8", "이가원의 금전 요구가 거절됨", "inference"),
    "u_lgw_other_motive": ("M8", "금전 외 이가원의 동기", "creative"),
    "lgw_song_choice": ("M11", "이가원의 농요 수단 선택", "hist"),
    "lgw_knows_killers": ("M6", "이가원의 실제 살해범 인지", "creative"),
    "lgw_prior_involvement": ("M6", "이가원의 범행 사전 관여", "creative"),
    "lgw_reports_quarrel": ("F9", "이가원이 조환에게 부부 언쟁 정보를 제공", "creative"),
    "hwan_ill": ("F6", "조환의 병환", "hist"),
    "u_hwan_isolated": ("F6", "조환의 정보 고립(병환 외)", "creative"),
    "hwan_trusts_jjh": ("F5", "조환의 조재항 신뢰", "creative"),
    "hwan_knows_reason": ("F4", "조환이 윤씨의 거절 이유를 앎", "creative"),
    "lgw_reframes_reason": ("F9", "이가원이 거절 이유를 부부 갈등으로 재구성", "creative"),
    "u_lgw_extra_evidence": ("F12", "이가원의 추가 '증거'(가장된 목격담·혈의 주장 등)", "creative"),
    "hwan_guilt": ("F10", "조카의 죽음에 대한 조환의 죄책감", "creative"),
    "u_family_duty": ("F10", "가족 보호 의무감", "creative"),
    "hwan_money_interest": ("F10", "조환의 금전적 이해관계", "creative"),
    "u_other_accuser": ("M10", "조환 외 고발자(이봉 등)", "creative"),
    "chogeom_error": ("J1", "초검 결론의 오류", "inference"),
    "bokgeom_shared_sources": ("J2", "복검이 초검과 같은 진술원에 의존", "creative"),
    "bokgeom_negligent": ("J2", "복검관의 검증 소홀", "creative"),
    "bokgeom_corrects": ("J2", "복검이 초검 오류를 바로잡음", "hist"),
    "independent_investigator": ("J12", "독립 조사관(암행어사)의 조사", "creative"),
    "witness_dissenter": ("S10", "가담을 거부한 주민 증인의 존재", "creative"),
    "records_preserved": ("J10", "이득준 원본 조사기록 보존", "creative"),
}

# 내생 변수 구조방정식: 이름 → (변수 ID, 설명, 근거 유형, 식)
# 근거 유형: theory(이론 제안) | film(극중 추가 가정) | source(사료에 나타난 관계)
ENDO_ORDER = [
    "burden_concentrated", "econ_refusal", "yun_refuses", "entitlement_framing", "blame_path",
    "hostility_to_yun", "murder_by_residents", "kjr_career_stake", "kjr_cover_motive",
    "jsj_cover_motive", "reinvest_nonindependent", "reinvest_motivated", "hwan_believes",
    "hwan_accepts", "lgw_motive", "lgw_instigates", "song_fabricated", "accusation",
    "oksa_formed", "long_detention", "truth_recoverable", "killers_identifiable",
]


def _endo_defs(b):
    A, O, N = z3.And, z3.Or, z3.Not
    return {
        "burden_concentrated": ("E6", "권분 부담의 조재항 집중", "theory",
                                A(b["u_shortage"], b["e5_cannot_evade"], b["u_elite_evade"]),
                                ["u_shortage", "e5_cannot_evade", "u_elite_evade"]),
        "econ_refusal": ("E12", "경제적으로 합리적인 거절 사유(종자·양식 위협)", "film",
                         A(b["burden_concentrated"], b["u_extra_exceeds"]),
                         ["burden_concentrated", "u_extra_exceeds"]),
        "yun_refuses": ("F2", "윤씨의 추가 출연 거부", "film",
                        O(b["econ_refusal"], b["u_yun_other_reason"]),
                        ["econ_refusal", "u_yun_other_reason"]),
        "entitlement_framing": ("A1", "주민이 '관의 뜻'으로 출연을 요구할 명분", "theory",
                                O(b["kjr_coercive"], b["lgw_selective"]),
                                ["kjr_coercive", "lgw_selective"]),
        "blame_path": ("S5", "윤씨에게 책임이 귀인되는 정보 경로", "theory",
                       O(b["kjr_shifts_blame"], b["lgw_selective"], b["u_resident_rumor"]),
                       ["kjr_shifts_blame", "lgw_selective", "u_resident_rumor"]),
        "hostility_to_yun": ("S6", "윤씨에 대한 집단적 책임 귀인·적대", "theory",
                             A(b["yun_refuses"], b["entitlement_framing"], b["blame_path"], N(b["s4_prior_known"])),
                             ["yun_refuses", "entitlement_framing", "blame_path", "s4_prior_known"]),
        "murder_by_residents": ("S9", "일부 주민의 윤씨 살해(분노 ≠ 살인: 촉발 사건·의도 필요)", "film",
                                A(b["hostility_to_yun"], b["u_trigger"], O(b["premeditated"], b["u_spont_intent"])),
                                ["hostility_to_yun", "u_trigger", "premeditated", "u_spont_intent"]),
        "kjr_career_stake": ("A6", "권중립의 인사상 이해", "film",
                             O(b["jsj_good_pophyeom"], b["u_kjr_reward_expect"]),
                             ["jsj_good_pophyeom", "u_kjr_reward_expect"]),
        "kjr_cover_motive": ("A12", "권중립의 책임 회피 동기", "film",
                             A(O(A(b["kjr_coercive"], b["kjr_knew_coercion"]), b["a5_inflated"], b["kjr_shifts_blame"]),
                               b["kjr_career_stake"]),
                             ["kjr_coercive", "kjr_knew_coercion", "a5_inflated", "kjr_shifts_blame", "kjr_career_stake"]),
        "jsj_cover_motive": ("A13", "조상진의 평가·감독 방어 동기", "film",
                             O(A(b["jsj_good_pophyeom"], O(b["jsj_knew_at_pophyeom"], b["jsj_learned_later_no_correct"])),
                               b["u_jsj_supervisory_fear"]),
                             ["jsj_good_pophyeom", "jsj_knew_at_pophyeom", "jsj_learned_later_no_correct", "u_jsj_supervisory_fear"]),
        "reinvest_nonindependent": ("J9", "재조사의 비독립성(직접 조사 없음)", "source",
                                    N(b["jsj_direct_investigation"]), ["jsj_direct_investigation"]),
        "reinvest_motivated": ("A15", "동기에 의한(고의적) 재조사 왜곡", "film",
                               A(b["reinvest_nonindependent"], b["jsj_cover_motive"]),
                               ["reinvest_nonindependent", "jsj_cover_motive"]),
        "hwan_believes": ("F12", "조환이 이가원의 주장을 믿음", "theory",
                          A(O(b["hwan_ill"], b["u_hwan_isolated"]), b["lgw_reports_quarrel"],
                            O(N(b["hwan_trusts_jjh"]), b["u_lgw_extra_evidence"]),
                            O(N(b["hwan_knows_reason"]), b["lgw_reframes_reason"])),
                          ["hwan_ill", "u_hwan_isolated", "lgw_reports_quarrel", "hwan_trusts_jjh",
                           "u_lgw_extra_evidence", "hwan_knows_reason", "lgw_reframes_reason"]),
        "hwan_accepts": ("F10", "조환의 사주 수용", "theory",
                         O(A(b["hwan_believes"], O(b["hwan_guilt"], b["u_family_duty"])), b["hwan_money_interest"]),
                         ["hwan_believes", "hwan_guilt", "u_family_duty", "hwan_money_interest"]),
        "lgw_motive": ("M8", "이가원의 무고 동기", "source",
                       O(b["lgw_money_refused"], b["u_lgw_other_motive"]),
                       ["lgw_money_refused", "u_lgw_other_motive"]),
        "lgw_instigates": ("M9", "이가원의 사주", "source", b["lgw_motive"], ["lgw_motive"]),
        "song_fabricated": ("M11", "농요 조작", "source", A(b["lgw_instigates"], b["lgw_song_choice"]),
                            ["lgw_instigates", "lgw_song_choice"]),
        "accusation": ("M14", "조재항에 대한 공식 고발", "source",
                       A(b["lgw_instigates"], O(b["hwan_accepts"], b["u_other_accuser"])),
                       ["lgw_instigates", "hwan_accepts", "u_other_accuser"]),
        "oksa_formed": ("J1", "살인 옥사 성립", "source",
                        A(b["accusation"], b["chogeom_error"], N(b["bokgeom_corrects"])),
                        ["accusation", "chogeom_error", "bokgeom_corrects"]),
        "long_detention": ("J7", "장기 구금", "source",
                           A(b["oksa_formed"], b["reinvest_nonindependent"]),
                           ["oksa_formed", "reinvest_nonindependent"]),
        "truth_recoverable": ("J12", "독립 조사로 진상 접근 가능", "film",
                              A(b["independent_investigator"], O(b["witness_dissenter"], b["records_preserved"])),
                              ["independent_investigator", "witness_dissenter", "records_preserved"]),
        "killers_identifiable": ("J15", "실제 살해범 식별 가능", "film",
                                 A(b["truth_recoverable"], b["witness_dissenter"], b["murder_by_residents"]),
                                 ["truth_recoverable", "witness_dissenter", "murder_by_residents"]),
    }


# ───────────────────────────── 3. 제약 정의 ─────────────────────────────
@dataclass
class C:
    cid: str
    layer: str
    text: str
    basis: list[str]
    build: Callable[[dict, dict], z3.BoolRef]
    status: str = ""  # 근거 검증 상태 요약


def between(x, lo, hi):
    return z3.And(x >= lo, x <= hi)


def in_month(x, y, m):
    a, b_ = month_range(y, m)
    return between(x, a, b_)


def pophyeom_days(years=range(1778, 1785)):
    return [L(y, m, 15) for y in years for m in (6, 12)]


def constraints() -> list[C]:
    cs: list[C] = []
    add = cs.append
    # ── STR: 사건 정의상 순서 ──
    add(C("STR_TENURE_JSJ", "STR", "조상진 부임 < 재임 종료", ["T2"], lambda t, b: t["JSJ_ARRIVE"] < t["JSJ_END"]))
    add(C("STR_SUCCESSOR", "STR", "후임 이경양 부임 ≥ 조상진 재임 종료(후임 시기에 조상진은 감사 권한 없음)", ["T3", "CL-OFF-02"],
          lambda t, b: t["LKY_START"] >= t["JSJ_END"]))
    add(C("STR_TENURE_KJR", "STR", "권중립 재임 시작 < 종료", ["T1"], lambda t, b: t["KJR_START"] < t["KJR_END"]))
    add(C("STR_BURIAL_AFTER_DEATH", "STR", "매장 > 사망", ["T9"], lambda t, b: t["BURIAL"] > t["DEATH"]))
    add(C("STR_EXAM_ORDER", "STR", "고발 ≤ 초검 < 복검 ≤ 성옥", ["J1", "J2", "CL-SIM-07"],
          lambda t, b: z3.And(t["ACCUSE"] <= t["CHOGEOM"], t["CHOGEOM"] < t["BOKGEOM"], t["BOKGEOM"] <= t["OKSA"])))
    add(C("STR_DEATH_BEFORE_ACCUSE", "STR", "사망 < 고발", ["T8", "T13"], lambda t, b: t["DEATH"] < t["ACCUSE"]))
    add(C("STR_DETAIN", "STR", "초검 ≤ 구금 시작 < 최종 판부 ≤ 구금 종료", ["T17"],
          lambda t, b: z3.And(t["CHOGEOM"] <= t["DETAIN_START"], t["DETAIN_START"] < t["FINAL"],
                              t["FINAL"] <= t["DETAIN_END"])))
    add(C("STR_REVIEW_AFTER_OKSA", "STR", "성옥 < 재조사 명령 < 조상진 재조사 수행", ["T18", "J9"],
          lambda t, b: z3.And(t["OKSA"] < t["REVIEW_ORDER"], t["REVIEW_ORDER"] < t["JSJ_REINVEST"])))
    add(C("STR_REINVEST_IN_TENURE", "STR", "조상진 재조사는 그의 감사 재임 중(실록 '該道臣趙尙鎭')", ["CL-SIL-09", "CL-SIL-06"],
          lambda t, b: between(t["JSJ_REINVEST"], t["JSJ_ARRIVE"], t["JSJ_END"])))
    add(C("STR_KJR_EXAMINER", "STR", "권중립은 초검 시 백천군수 재임 중", ["CL-SIM-07"],
          lambda t, b: between(t["CHOGEOM"], t["KJR_START"], t["KJR_END"])))
    add(C("STR_LATE_ORDER", "STR", "재조사 수행·격쟁·형조 심리는 성옥 이후·최종 판부 이전", ["T19", "T20"],
          lambda t, b: z3.And(t["OKSA"] < t["HYEONGJO_1781_8"], t["HYEONGJO_1781_8"] < t["FINAL"], t["JSJ_REINVEST"] < t["FINAL"],
                              t["JOKJAENG"] < t["FINAL"], t["OKSA"] < t["JOKJAENG"])))
    add(C("STR_POSTHUMOUS", "STR", "금전 요구·농요·사주는 윤씨 사망 이후(사후 무고)", ["CL-CHUG-02", "CL-SIL-03", "CL-CHUG-03"],
          lambda t, b: z3.And(t["MONEY_DEMAND"] > t["DEATH"], t["SONG"] > t["DEATH"], t["INSTIGATE"] > t["DEATH"])))
    add(C("STR_INSTIGATE_BEFORE_ACCUSE", "STR", "사주 < 공식 고발", ["T12", "T13"], lambda t, b: t["INSTIGATE"] < t["ACCUSE"]))
    add(C("STR_RELIEF_BY_KJR", "STR", "평가 대상 구휼 행정은 권중립 재임 중", ["T1", "A5"],
          lambda t, b: between(t["RELIEF_ADMIN"], t["KJR_START"], t["KJR_END"])))
    add(C("STR_COMPLAINT_AFTER_RELIEF", "STR", "강제 권분 항의는 구휼 행정 이후", ["A9"], lambda t, b: t["COMPLAINT"] > t["RELIEF_ADMIN"]))

    # ── INST: 제도 규칙 ──
    add(C("INST_POPHYEOM_DATES", "INST", "정기 포폄은 음력 6월·12월 (15일로 대표)", ["CL-INST-01", "GYDJ_POPHYEOM"],
          lambda t, b: z3.Or([t["POPHYEOM"] == v for v in pophyeom_days()]), status="미확인(조문 원문 미확보)"))
    add(C("INST_POPHYEOM_SITTING", "INST", "포폄은 평가 기간 중 재임한 수령에 대해, 평가자가 조상진이면 그의 재임 중",
          ["T6", "CL-INST-01"],
          lambda t, b: z3.And(between(t["POPHYEOM"], t["KJR_START"], t["KJR_END"]),
                              z3.Implies(b["pophyeom_by_jsj"], between(t["POPHYEOM"], t["JSJ_ARRIVE"], t["JSJ_END"]))),
          status="제도 추론"))

    # ── HIST_TEN: 인사 연표 앵커 ──
    add(C("HT_JSJ_ARRIVE_SUMMER", "HIST_TEN", "조상진 1780년 여름(음력 4~6월) 부임", ["CL-OFF-04"],
          lambda t, b: between(t["JSJ_ARRIVE"], L(1780, 4, 1), L(1780, 6, 30)), status="미확인"))
    add(C("HT_JSJ_IN_OFFICE_1781_9", "HIST_TEN", "조상진 1781 L9 29 재임", ["CL-OFF-01", "BIB1781"],
          lambda t, b: z3.And(t["JSJ_ARRIVE"] <= L(1781, 9, 29), t["JSJ_END"] >= L(1781, 9, 29)), status="간접 확인"))
    add(C("HT_LKY_BY_1782_4", "HIST_TEN", "이경양 1782 L4 23 황해감사 재임", ["CL-OFF-02", "SIL178204"],
          lambda t, b: t["LKY_START"] <= L(1782, 4, 23), status="간접 확인"))
    add(C("HT_JSJ_DAESASEONG_1783_5", "HIST_TEN", "조상진 1783 L5 9 대사성(그 이전 감사직 종료)", ["CL-OFF-03", "SIL1783M"],
          lambda t, b: t["JSJ_END"] <= L(1783, 5, 9), status="간접 확인"))

    # ── HIST_T: 사료 연대 앵커 ──
    add(C("HT_SIM_OKSA_1780_6", "HIST_T", "《심리록》 경자(1780) 6월 성옥", ["CL-SIM-01", "SIM"],
          lambda t, b: in_month(t["OKSA"], 1780, 6), status="사료 간 충돌"))
    add(C("HT_SIL_CASE_1781", "HIST_T", "《정조실록》 '事在辛丑' → 성옥이 신축(1781)년", ["CL-SIL-01", "SIL1783"],
          lambda t, b: between(t["OKSA"], L(1781, 1, 1), L(1781, 12, 30)), status="사료 간 충돌·지시 대상 해석 필요"))
    add(C("HT_SIL_REVIEW_SPRING_1781", "HIST_T", "재조사 지시: 신축(1781) 봄 심리 때", ["CL-SIL-02", "SIL1783"],
          lambda t, b: between(t["REVIEW_ORDER"], L(1781, 1, 1), L(1781, 3, 30)), status="간접 확인"))
    add(C("HT_SIM_HYEONGJO_1781_8", "HIST_T", "《심리록》 신축 8월 형조 심리", ["CL-SIM-03", "SIM"],
          lambda t, b: in_month(t["HYEONGJO_1781_8"], 1781, 8), status="간접 확인"))
    add(C("HT_JOKJAENG_1782_7", "HIST_T", "조재정 격쟁 1782 L7", ["CL-SIM-04", "SIM"],
          lambda t, b: in_month(t["JOKJAENG"], 1782, 7), status="간접 확인"))
    add(C("HT_FINAL_1783_6_3", "HIST_T", "최종 판부 1783 L6 3", ["CL-SIL-07", "SIL1783"],
          lambda t, b: t["FINAL"] == L(1783, 6, 3), status="간접 확인"))
    add(C("HT_BURIAL_5", "HIST_T", "사망 5일 만의 매장(닷새째: +4~+5)", ["CL-CHUG-01", "CL-SIM-06"],
          lambda t, b: between(t["BURIAL"] - t["DEATH"], 4, 5), status="간접 확인(원문 미확보)"))
    add(C("HT_ACCUSE_40", "HIST_T", "사망 후 약 40일 고발·검험(허용 35~45일)", ["CL-SIM-06", "CL-CHUG-04"],
          lambda t, b: between(t["ACCUSE"] - t["DEATH"], 35, 45), status="간접 확인(원문 미확보)"))

    # ── HIST_C: 사료가 서술한 인과적 사실 ──
    hc = [
        ("HC_SONG", "농요 조작(정조 판단)", ["CL-SIL-03"], "song_fabricated", True),
        ("HC_INSTIGATION", "이가원의 사주(정조 판단·추관지)", ["CL-SIL-13", "CL-CHUG-03"], "lgw_instigates", True),
        ("HC_ACCUSATION", "조재항 고발", ["CL-SIM-02"], "accusation", True),
        ("HC_OKSA", "옥사 성립", ["CL-SIM-01", "CL-SIL-01"], "oksa_formed", True),
        ("HC_NO_DIRECT_REINVEST", "조상진의 직접 조사 없음", ["CL-SIL-06"], "jsj_direct_investigation", False),
        ("HC_HWAN_ILL", "조환의 병환", ["CL-CHUG-03"], "hwan_ill", True),
        ("HC_BOKGEOM_NOT_CORRECTED", "복검이 오류를 바로잡지 못함(옥사 3년 지속)", ["CL-SIL-11"], "bokgeom_corrects", False),
        ("HC_CHOGEOM_ERROR", "초검 결론은 최종 판부에서 유지되지 않음(추론)", ["CL-SIL-05", "CL-SIL-07"], "chogeom_error", True),
    ]
    for cid, txt, basis, var, val in hc:
        add(C(cid, "HIST_C", txt, basis, (lambda var=var, val=val: (lambda t, b: b[var] == val))(), status="간접 확인"))

    # ── FILM_REQ: 사용자가 정한 극중 필수 조건 ──
    add(C("FR_ORDER", "FILM_REQ", "조상진 부임 < 포폄 < 윤씨 사망 < 옥사 성립", ["CL-FILM-REQ-01"],
          lambda t, b: z3.And(t["JSJ_ARRIVE"] < t["POPHYEOM"], t["POPHYEOM"] < t["DEATH"], t["DEATH"] < t["OKSA"])))
    add(C("FR_EVALUATOR", "FILM_REQ", "포폄 평가자 = 현직 감사 조상진, 등급 긍정", ["CL-FILM-REQ-02"],
          lambda t, b: z3.And(b["pophyeom_by_jsj"], b["jsj_good_pophyeom"])))
    add(C("FR_RELIEF_BEFORE_POPHYEOM", "FILM_REQ", "구휼 행정 < 포폄", ["CL-FILM-REQ-01"],
          lambda t, b: t["RELIEF_ADMIN"] < t["POPHYEOM"]))
    add(C("FR_HOSTILITY_BEFORE_DEATH", "FILM_REQ", "구휼 이후·사망 이전에 적대감 형성", ["CL-FILM-REQ-01"],
          lambda t, b: z3.And(t["RELIEF_ADMIN"] < t["HOSTILITY"], t["HOSTILITY"] < t["DEATH"])))
    add(C("FR_DUAL_OUTCOME", "FILM_REQ", "윤씨 피살(주민)과 조재항 무고가 동시에 성립", ["CL-FILM-03"],
          lambda t, b: z3.And(b["murder_by_residents"], b["oksa_formed"])))
    add(C("FR_HWAN_ACCUSES", "FILM_REQ", "조환이 사주를 수용하여 고발", ["CL-FILM-13"], lambda t, b: b["hwan_accepts"]))
    add(C("FR_JSJ_MOTIVE", "FILM_REQ", "조상진에게 사후 방어 동기가 있음", ["CL-FILM-08"], lambda t, b: b["jsj_cover_motive"]))
    add(C("FR_INVESTIGABLE", "FILM_REQ", "독립 조사로 살해범 식별 가능(결말)", ["CL-FILM-09"], lambda t, b: b["killers_identifiable"]))

    # ── FILM_SYN: 시놉시스 v4의 구체적 선택 ──
    add(C("FS_DEATH_1780_4_LATE", "FILM_SYN", "윤씨 사망 1780 L4 하순", ["CL-FILM-03"],
          lambda t, b: between(t["DEATH"], L(1780, 4, 21), L(1780, 4, 30))))
    add(C("FS_CHOGEOM_1780_6", "FILM_SYN", "초검 1780 L6", ["CL-FILM-05"], lambda t, b: in_month(t["CHOGEOM"], 1780, 6)))
    add(C("FS_JSJ_ARRIVE_1780_6", "FILM_SYN", "조상진 1780 L6 부임", ["CL-FILM-06"], lambda t, b: in_month(t["JSJ_ARRIVE"], 1780, 6)))
    add(C("FS_REVIEW_1780_12", "FILM_SYN", "재조사 명령 1780 L12", ["CL-FILM-07"], lambda t, b: in_month(t["REVIEW_ORDER"], 1780, 12)))
    add(C("FS_JOKJAENG_1781_SPRING", "FILM_SYN", "격쟁 1781 봄", ["CL-FILM-10"],
          lambda t, b: between(t["JOKJAENG"], L(1781, 1, 1), L(1781, 3, 30))))
    add(C("FS_FINAL_1781_H1", "FILM_SYN", "결말(최종 판부) 1781 상반기", ["CL-FILM-12"],
          lambda t, b: between(t["FINAL"], L(1781, 1, 1), L(1781, 6, 30))))
    add(C("FS_OFFICIALS_IN_OFFICE_AT_END", "FILM_SYN", "결말 시 조상진·권중립 모두 현직", ["CL-FILM-11", "CL-FILM-12"],
          lambda t, b: z3.And(t["FINAL"] <= t["JSJ_END"], t["FINAL"] <= t["KJR_END"])))
    return cs


def coupling(t, b):
    """인과 변수와 시간의 연결(항상 강제)."""
    I, A = z3.Implies, z3.And
    return [
        I(b["jsj_knew_at_pophyeom"], A(b["pophyeom_by_jsj"], t["COMPLAINT"] < t["POPHYEOM"])),
        I(b["jsj_learned_later_no_correct"],
          A(t["POPHYEOM"] < t["JSJ_LEARN"], t["JSJ_LEARN"] <= t["JSJ_REINVEST"], z3.Not(b["jsj_knew_at_pophyeom"]))),
        I(b["jsj_good_pophyeom"], b["pophyeom_by_jsj"]),
        I(b["kjr_knew_coercion"], b["kjr_coercive"]),
        I(b["hostility_to_yun"], t["HOSTILITY"] < t["DEATH"]),
        I(b["lgw_prior_involvement"], A(b["lgw_knows_killers"], t["LGW_PRE_CONTACT"] < t["DEATH"])),
        I(b["bokgeom_corrects"], A(z3.Not(b["bokgeom_shared_sources"]), z3.Not(b["bokgeom_negligent"]))),
        I(z3.Not(b["bokgeom_corrects"]), z3.Or(b["bokgeom_shared_sources"], b["bokgeom_negligent"])),
        I(b["premeditated"], z3.Not(b["u_spont_intent"])),
    ]


# ───────────────────────────── 4. 모형 조립 ─────────────────────────────
def make_vars():
    t = {e: z3.Int(e) for e in EVENTS}
    b = {v: z3.Bool(v) for v in list(EXOG) + ENDO_ORDER}
    return t, b


def domain(t):
    return [between(x, LO, HI) for x in t.values()]


def scm(b, cut: set[str] = frozenset()):
    defs = _endo_defs(b)
    return [b[v] == defs[v][3] for v in ENDO_ORDER if v not in cut]


CS = constraints()
CS_BY_ID = {c.cid: c for c in CS}


def layer_ids(*layers, exclude=()):
    return [c.cid for c in CS if c.layer in layers and c.cid not in exclude]


MODES = {
    "H_SIM": {"desc": "역사 고정(《심리록》 경자 6월 성옥 채택)",
              "hard": layer_ids("STR", "INST", "HIST_TEN", "HIST_C") + layer_ids("HIST_T", exclude=("HT_SIL_CASE_1781",))},
    "H_SIL": {"desc": "역사 고정(《정조실록》 '事在辛丑'을 성옥 연도로 해석해 채택)",
              "hard": layer_ids("STR", "INST", "HIST_TEN", "HIST_C") + layer_ids("HIST_T", exclude=("HT_SIM_OKSA_1780_6",))},
    "H_BOTH": {"desc": "상충 사료를 모두 절대 사실로 고정(금지된 방식의 시연)",
               "hard": layer_ids("STR", "INST", "HIST_TEN", "HIST_C", "HIST_T")},
    "F_ON_H_SIM": {"desc": "극중 필수 제약 + H_SIM 전체",
                   "hard": layer_ids("STR", "INST", "HIST_TEN", "HIST_C", "FILM_REQ") + layer_ids("HIST_T", exclude=("HT_SIL_CASE_1781",))},
    "F_ON_H_SIL": {"desc": "극중 필수 제약 + H_SIL 전체",
                   "hard": layer_ids("STR", "INST", "HIST_TEN", "HIST_C", "FILM_REQ") + layer_ids("HIST_T", exclude=("HT_SIM_OKSA_1780_6",))},
    "F_SYNOPSIS_V4": {"desc": "극중 필수 제약 + 인사 연표 + 시놉시스 v4 날짜 선택(사료 연대 앵커 미적용)",
                      "hard": layer_ids("STR", "INST", "HIST_TEN", "HIST_C", "FILM_REQ", "FILM_SYN")},
    "F_ADAPT": {"desc": "MODE F: 극중 필수 + 제도 + 인사 연표 유지, 사료 연대 앵커는 최소 수정 대상",
                "hard": layer_ids("STR", "INST", "HIST_TEN", "HIST_C", "FILM_REQ")},
}

# MUS/MCS 분석에서 '수정 가능(soft)'로 둘 층위
SOFT_LAYERS = ("INST", "HIST_TEN", "HIST_T", "FILM_REQ", "FILM_SYN")


def base_solver(extra_cut=frozenset()):
    t, b = make_vars()
    s = z3.Solver()
    s.add(domain(t))
    s.add(scm(b, extra_cut))
    s.add(coupling(t, b))
    return s, t, b


def check_ids(ids, extra=()):
    s, t, b = base_solver()
    for cid in ids:
        s.add(CS_BY_ID[cid].build(t, b))
    for e in extra:
        s.add(e(t, b))
    r = s.check()
    return r, (s.model() if r == z3.sat else None), t, b


# ── MUS / MCS 열거 (MARCO; Liffiton et al., 2016) ──
def marco(hard_ids, soft_ids, limit=40):
    s, t, b = base_solver()
    for cid in hard_ids:
        s.add(CS_BY_ID[cid].build(t, b))
    sel = {cid: z3.Bool(f"sel_{cid}") for cid in soft_ids}
    for cid, p in sel.items():
        s.add(z3.Implies(p, CS_BY_ID[cid].build(t, b)))
    mp = z3.Solver()
    muses, mcses = [], []

    def is_sat(subset):
        return s.check([sel[c] for c in subset]) == z3.sat

    while len(muses) + len(mcses) < limit and mp.check() == z3.sat:
        m = mp.model()
        seed = [c for c in soft_ids if not z3.is_false(m.eval(sel[c], model_completion=True))]
        if is_sat(seed):
            mss = list(seed)  # grow
            for c in soft_ids:
                if c not in mss and is_sat(mss + [c]):
                    mss.append(c)
            mcs = [c for c in soft_ids if c not in mss]
            mcses.append(sorted(mcs))
            mp.add(z3.Or([sel[c] for c in mcs]) if mcs else z3.BoolVal(False))
        else:
            mus = list(seed)  # shrink
            for c in list(mus):
                trial = [x for x in mus if x != c]
                if not is_sat(trial):
                    mus = trial
            muses.append(sorted(mus))
            mp.add(z3.Or([z3.Not(sel[c]) for c in mus]))
    return muses, mcses


def window(hard_ids, event, extra=()):
    """사건 이벤트의 가능 구간 [최소, 최대] (모형상)."""
    out = []
    for sense in ("min", "max"):
        o = z3.Optimize()
        t, b = make_vars()
        o.add(domain(t)); o.add(scm(b)); o.add(coupling(t, b))
        for cid in hard_ids:
            o.add(CS_BY_ID[cid].build(t, b))
        for e in extra:
            o.add(e(t, b))
        (o.minimize if sense == "min" else o.maximize)(t[event])
        if o.check() != z3.sat:
            return None
        out.append(o.model().eval(t[event]).as_long())
    return out


def witness(hard_ids, prefer_ids=(), extra=()):
    """예시 해: hard를 만족하면서 prefer(시놉시스 선택 등)를 가능한 한 많이(개수 기준) 만족. 유일해 아님."""
    o = z3.Optimize()
    t, b = make_vars()
    o.add(domain(t)); o.add(scm(b)); o.add(coupling(t, b))
    for cid in hard_ids:
        o.add(CS_BY_ID[cid].build(t, b))
    for e in extra:
        o.add(e(t, b))
    for cid in prefer_ids:
        o.add_soft(CS_BY_ID[cid].build(t, b), 1, id="pref")
    if o.check() != z3.sat:
        return None
    m = o.model()
    kept = [cid for cid in prefer_ids if z3.is_true(m.eval(CS_BY_ID[cid].build(t, b), model_completion=True))]
    return {
        "events": {e: fmt(m.eval(t[e], model_completion=True).as_long()) for e in EVENTS},
        "kept_preferences": kept,
        "dropped_preferences": [c for c in prefer_ids if c not in kept],
    }


# ───────────────────────────── 5. 가능세계 생성 ─────────────────────────────
WORLD_DIMS = [  # §13의 핵심 인과 차원
    ("econ_refusal", "윤씨 거절의 경제적 사유(부담 집중×가용량 초과)"),
    ("kjr_coercive", "권분 강제"),
    ("kjr_knew_coercion", "권중립 강압 인지"),
    ("a5_inflated", "실적 과장(포폄 근거 부정확)"),
    ("jsj_knew_at_pophyeom", "조상진 사전 인지"),
    ("jsj_learned_later_no_correct", "조상진 사후 인지·미정정"),
    ("kjr_shifts_blame", "권중립 책임 전가"),
    ("lgw_selective", "이가원 선택적 정보"),
    ("premeditated", "살해 사전 결의"),
    ("lgw_knows_killers", "이가원 살해범 인지"),
    ("lgw_prior_involvement", "이가원 사전 관여"),
    ("hwan_believes", "조환: 믿음 경로"),
    ("hwan_money_interest", "조환: 금전 경로"),
    ("bokgeom_shared_sources", "복검 오류: 진술원 공유"),
]
SYNOPSIS_SEED = {  # 시놉시스 v4 + 사용자 가설에 가장 가까운 세계(선택 시작점)
    "econ_refusal": True, "kjr_coercive": True, "kjr_knew_coercion": True, "a5_inflated": False, "jsj_knew_at_pophyeom": False,
    "jsj_learned_later_no_correct": True, "kjr_shifts_blame": True, "lgw_selective": True, "premeditated": True,
    "lgw_knows_killers": False, "lgw_prior_involvement": False, "hwan_believes": True, "hwan_money_interest": True,
    "bokgeom_shared_sources": True,
}


def enumerate_world_projections(hard_ids):
    s, t, b = base_solver()
    for cid in hard_ids:
        s.add(CS_BY_ID[cid].build(t, b))
    out = []
    while s.check() == z3.sat:
        m = s.model()
        proj = {d: z3.is_true(m.eval(b[d], model_completion=True)) for d, _ in WORLD_DIMS}
        out.append(proj)
        s.add(z3.Or([b[d] != proj[d] for d, _ in WORLD_DIMS]))
    return out


def hamming(a, c):
    return sum(a[k] != c[k] for k, _ in WORLD_DIMS)


def select_representatives(projs, k=10):
    seed = min(projs, key=lambda p: (hamming(p, SYNOPSIS_SEED), tuple(p[d] for d, _ in WORLD_DIMS)))
    chosen = [seed]
    while len(chosen) < min(k, len(projs)):
        best = max((p for p in projs if p not in chosen),
                   key=lambda p: (min(hamming(p, c) for c in chosen), -hamming(p, SYNOPSIS_SEED),
                                  tuple(not p[d] for d, _ in WORLD_DIMS)))
        chosen.append(best)
    return chosen


def complete_world(hard_ids, proj):
    """투영된 차원을 고정하고 나머지 '극중 가정(creative)' 외생 변수의 참 개수를 최소화해 세계를 완성."""
    o = z3.Optimize()
    t, b = make_vars()
    o.add(domain(t)); o.add(scm(b)); o.add(coupling(t, b))
    for cid in hard_ids:
        o.add(CS_BY_ID[cid].build(t, b))
    for d, v in proj.items():
        o.add(b[d] == v)
    creative = [v for v, (_, _, lay) in EXOG.items() if lay == "creative"]
    o.minimize(z3.Sum([z3.If(b[v], 1, 0) for v in creative]))
    assert o.check() == z3.sat
    m = o.model()
    vals = {v: z3.is_true(m.eval(b[v], model_completion=True)) for v in list(EXOG) + ENDO_ORDER}
    return vals


def min_date_changes(world_vals, base_hard, soft_ids):
    """세계의 인과 값을 고정했을 때 필요한 사료 연대 앵커 수정의 최소 개수 집합들."""
    fixed = [(lambda v=v, val=val: (lambda t, b: b[v] == val))() for v, val in world_vals.items() if v in EXOG]
    s, t, b = base_solver()
    for cid in base_hard:
        s.add(CS_BY_ID[cid].build(t, b))
    for f in fixed:
        s.add(f(t, b))
    sel = {cid: z3.Bool(f"s_{cid}") for cid in soft_ids}
    for cid, p in sel.items():
        s.add(z3.Implies(p, CS_BY_ID[cid].build(t, b)))
    o = z3.Optimize()
    o.add(s.assertions())
    o.maximize(z3.Sum([z3.If(p, 1, 0) for p in sel.values()]))
    assert o.check() == z3.sat
    m = o.model()
    best = sum(z3.is_true(m.eval(p)) for p in sel.values())
    # 같은 최소 크기의 모든 수정집합 열거
    sets = []
    s2 = z3.Solver(); s2.add(s.assertions())
    s2.add(z3.Sum([z3.If(p, 1, 0) for p in sel.values()]) == best)
    while s2.check() == z3.sat and len(sets) < 8:
        mm = s2.model()
        dropped = sorted(c for c, p in sel.items() if not z3.is_true(mm.eval(p, model_completion=True)))
        sets.append(dropped)
        s2.add(z3.Or([sel[c] if c in dropped else z3.Not(sel[c]) for c in soft_ids]))
    return sets


def forced_assumptions(hard_ids):
    """모든 가능세계에서 참이어야 하는 극중 가정(= 극중 필수 조건이 강제하는 공통 가정)."""
    forced = []
    for v, (_, _, lay) in EXOG.items():
        if lay != "creative":
            continue
        s, t, b = base_solver()
        for cid in hard_ids:
            s.add(CS_BY_ID[cid].build(t, b))
        s.add(z3.Not(b[v]))
        if s.check() == z3.unsat:
            forced.append(v)
    return sorted(forced)


FORCED: list[str] = []


def world_metrics(v):
    creative_true = sorted(k for k, (_, _, lay) in EXOG.items() if lay == "creative" and v[k] and k not in FORCED)
    flags = {
        "경제적 인과성": v["econ_refusal"],
        "희생양화(행위자 경로)": v["hostility_to_yun"] and (v["kjr_shifts_blame"] or v["lgw_selective"]),
        "행정적 인과성": v["kjr_cover_motive"] and v["jsj_cover_motive"] and v["jsj_good_pophyeom"]
        and (v["jsj_knew_at_pophyeom"] or v["jsj_learned_later_no_correct"]),
        "가족체계 설명력": v["hwan_believes"],
        "사법적 인과성": v["oksa_formed"] and v["song_fabricated"] and v["accusation"],
        "수사 가능성": v["killers_identifiable"],
    }
    return creative_true, flags


def pareto(rows):
    """최소화: 미확인 가정 수, 날짜 수정 수 / 최대화: 각 설명 기준(불리언). 가중치 없음."""
    def vec(r):
        return [-r["n_assump"], -r["n_dates"]] + [int(x) for x in r["flags"].values()]
    nd = []
    for r in rows:
        dominated = any(all(a >= b_ for a, b_ in zip(vec(o), vec(r))) and any(a > b_ for a, b_ in zip(vec(o), vec(r)))
                        for o in rows if o is not r)
        nd.append(not dominated)
    return nd


# ───────────────────────────── 6. 반사실 분석 ─────────────────────────────
CF_QUESTIONS = [
    ("Q1", "조재항이 최상층 토호여서 권분을 회피할 수 있었다면?", {"e5_cannot_evade": False},
     ["burden_concentrated", "econ_refusal", "yun_refuses", "hostility_to_yun", "murder_by_residents"]),
    ("Q2", "조재항에게 부담이 집중되지 않았다면(부담 집중에 직접 개입)?", {"burden_concentrated": False},
     ["econ_refusal", "yun_refuses", "hostility_to_yun"]),
    ("Q3", "권중립이 자발적 권분만 시행했다면?", {"kjr_coercive": False},
     ["entitlement_framing", "hostility_to_yun", "kjr_cover_motive", "murder_by_residents"]),
    ("Q4", "권중립이 윤씨에게 책임을 전가하지 않았다면?", {"kjr_shifts_blame": False},
     ["blame_path", "hostility_to_yun", "murder_by_residents"]),
    ("Q5", "조상진이 좋은 포폄을 내리지 않았다면?", {"jsj_good_pophyeom": False},
     ["jsj_cover_motive", "reinvest_motivated", "kjr_career_stake", "kjr_cover_motive"]),
    ("Q6", "조상진이 포폄 당시 강제 권분을 몰랐다면?", {"jsj_knew_at_pophyeom": False},
     ["jsj_cover_motive", "reinvest_motivated", "jsj_learned_later_no_correct"]),
    ("Q7", "조환이 조재항을 신뢰했다면?", {"hwan_trusts_jjh": True},
     ["hwan_believes", "hwan_accepts", "accusation"]),
    ("Q8", "조환이 윤씨의 권분 반대 이유를 알고 있었다면?", {"hwan_knows_reason": True},
     ["hwan_believes", "hwan_accepts"]),
    ("Q9", "이가원이 실제 살해범을 몰랐다면?", {"lgw_knows_killers": False, "lgw_prior_involvement": False},
     ["song_fabricated", "accusation", "oksa_formed"]),
    ("Q10", "이우배가 초검의 오류를 바로잡았다면?", {"bokgeom_corrects": True},
     ["oksa_formed", "long_detention"]),
]

# 반사실에서 유지하는 제약: 사료 인과 사실(HIST_C) + 극중 필수 중 결과변수를 직접 고정하지 않는 것
FR_PINS = {  # FILM_REQ가 직접 고정하는 변수
    "FR_DUAL_OUTCOME": {"murder_by_residents", "oksa_formed"},
    "FR_HWAN_ACCUSES": {"hwan_accepts"},
    "FR_JSJ_MOTIVE": {"jsj_cover_motive"},
    "FR_INVESTIGABLE": {"killers_identifiable", "murder_by_residents"},
    "FR_EVALUATOR": {"jsj_good_pophyeom", "pophyeom_by_jsj"},
}
HC_PINS = {"HC_SONG": {"song_fabricated"}, "HC_INSTIGATION": {"lgw_instigates"}, "HC_ACCUSATION": {"accusation"},
           "HC_OKSA": {"oksa_formed"}, "HC_NO_DIRECT_REINVEST": {"jsj_direct_investigation"}, "HC_HWAN_ILL": {"hwan_ill"},
           "HC_BOKGEOM_NOT_CORRECTED": {"bokgeom_corrects"}, "HC_CHOGEOM_ERROR": {"chogeom_error"}}


def _kept_ids(do_vars, outcomes):
    """개입 변수와 그 후손(인과 그래프 기준), 그리고 질문한 결과변수를 고정하는 제약은 제외한다.
    (결과를 미리 고정해 둔 채 '결과가 유지되는가'를 물을 수는 없으므로.)"""
    g = build_graph()
    touched = set(do_vars) | set(outcomes)
    for d in do_vars:
        if d in g:
            touched |= nx.descendants(g, d)
    kept = [c for c in layer_ids("STR")]
    kept += [c for c in layer_ids("HIST_C") if not (HC_PINS.get(c, set()) & touched)]
    kept += [c for c in layer_ids("FILM_REQ") if not (FR_PINS.get(c, set()) & touched)]
    return kept


def possible_values(kept, do, var, cut):
    res = {}
    for val in (True, False):
        s, t, b = base_solver(extra_cut=cut)
        for cid in kept:
            s.add(CS_BY_ID[cid].build(t, b))
        for k, v in do.items():
            s.add(b[k] == v)
        s.add(b[var] == val)
        res[val] = s.check() == z3.sat
    if res[True] and res[False]:
        return "가능(참·거짓 모두 성립)"
    if res[True]:
        return "필연적으로 참"
    if res[False]:
        return "불가능(필연적으로 거짓)"
    return "모형 불성립"


def necessary_assumptions(kept, do, target, cut):
    """target=True가 되려면 반드시 참이어야 하는 극중 가정(creative 외생변수).
    기준선(target 미지정)에서 이미 필요한 것은 빼서 '결과를 위해 추가로 필요한 것'만 남긴다."""
    creative = [v for v, (_, _, lay) in EXOG.items() if lay == "creative" and v not in do]

    def nec(with_target):
        out = []
        for v in creative:
            s, t, b = base_solver(extra_cut=cut)
            for cid in kept:
                s.add(CS_BY_ID[cid].build(t, b))
            for k, val in do.items():
                s.add(b[k] == val)
            if with_target:
                s.add(b[target])
            s.add(z3.Not(b[v]))
            if s.check() == z3.unsat:
                out.append(v)
        return set(out)
    base = nec(False)
    return sorted(nec(True) - base)


def minimal_extra_assumptions(kept, do, target, cut, max_sets=4):
    """target=True가 되기 위해 반드시 참이어야 하는 극중 가정(creative 외생변수)의 최소 집합들."""
    creative = [v for v, (_, _, lay) in EXOG.items() if lay == "creative" and v not in do]
    o_base = []
    s, t, b = base_solver(extra_cut=cut)
    for cid in kept:
        s.add(CS_BY_ID[cid].build(t, b))
    for k, v in do.items():
        s.add(b[k] == v)
    s.add(b[target])
    if s.check() != z3.sat:
        return None
    o = z3.Optimize(); o.add(s.assertions())
    o.minimize(z3.Sum([z3.If(b[v], 1, 0) for v in creative]))
    o.check()
    best = sum(z3.is_true(o.model().eval(b[v], model_completion=True)) for v in creative)
    s.add(z3.Sum([z3.If(b[v], 1, 0) for v in creative]) == best)
    sets = []
    while s.check() == z3.sat and len(sets) < max_sets:
        m = s.model()
        on = sorted(v for v in creative if z3.is_true(m.eval(b[v], model_completion=True)))
        sets.append(on)
        s.add(z3.Or([z3.Not(b[v]) for v in on]))
    # 모든 최소 집합에 공통으로 필요한 가정
    common = sorted(set.intersection(*map(set, sets))) if sets else []
    return {"min_count": best, "examples": sets, "always_required": common}


def run_counterfactuals():
    out = []
    for qid, question, do, outcomes in CF_QUESTIONS:
        cut = {k for k in do if k in ENDO_ORDER}  # 내생 변수 개입 = 구조방정식 절단(do 연산)
        kept = _kept_ids(do.keys(), outcomes)
        baseline = {o: possible_values(kept, {}, o, set()) for o in outcomes}
        intervened = {o: possible_values(kept, do, o, cut) for o in outcomes}
        # 조건화(관찰): 극중 필수 전체 유지 + do 변수 값을 '관찰'로 추가 (식 절단 없음)
        s, t, b = base_solver()
        for cid in layer_ids("STR", "HIST_C", "FILM_REQ"):
            s.add(CS_BY_ID[cid].build(t, b))
        for k, v in do.items():
            s.add(b[k] == v)
        conditioning_sat = s.check() == z3.sat
        extras = {}
        for o in outcomes:
            if intervened[o].startswith("가능") or intervened[o].startswith("필연적으로 참"):
                extras[o] = {"necessary_beyond_baseline": necessary_assumptions(kept, do, o, cut)}
        out.append({
            "qid": qid, "question": question,
            "changed": {k: v for k, v in do.items()},
            "operation": "do() 개입(내생변수: 구조방정식 절단)" if cut else "외생변수 값 설정(do)",
            "kept_constraints": kept,
            "dropped_film_requirements": [c for c in layer_ids("FILM_REQ") if c not in kept],
            "dropped_historical_facts": [c for c in layer_ids("HIST_C") if c not in kept],
            "baseline": baseline, "intervened": intervened,
            "conditioning_with_all_film_requirements_sat": conditioning_sat,
            "minimal_extra_assumptions": extras,
        })
    return out


# ───────────────────────────── 7. 인과 그래프 ─────────────────────────────
EDGE_KIND = {"source": "사료에 나타난 관계", "theory": "이론이 제안한 인과", "film": "극중 추가 가정"}
TEMPORAL_EDGES = [  # 시간 선후(인과 아님)
    ("JSJ_ARRIVE", "POPHYEOM"), ("POPHYEOM", "DEATH"), ("DEATH", "BURIAL"), ("DEATH", "ACCUSE"),
    ("ACCUSE", "CHOGEOM"), ("CHOGEOM", "BOKGEOM"), ("BOKGEOM", "OKSA"), ("OKSA", "REVIEW_ORDER"),
    ("REVIEW_ORDER", "JSJ_REINVEST"), ("JSJ_REINVEST", "JOKJAENG"), ("JOKJAENG", "FINAL"),
]


def build_graph():
    b = {v: z3.Bool(v) for v in list(EXOG) + ENDO_ORDER}
    defs = _endo_defs(b)
    g = nx.DiGraph()
    for v in ENDO_ORDER:
        vid, desc, kind, _, parents = defs[v]
        g.add_node(v, label=f"{vid} {desc}", kind="endo")
        for p in parents:
            if p in EXOG:
                g.add_node(p, label=f"{EXOG[p][0]} {EXOG[p][1]}", kind=EXOG[p][2])
            g.add_edge(p, v, kind=kind)
    return g


def mermaid(g):
    lines = ["%% 08_causal_graph.mmd — 03_constraints.py가 생성. 수정 시 생성기를 고칠 것.",
             "%% 굵은 화살표(==>) 사료에 나타난 관계 / 화살표(-->) 이론이 제안한 인과 / 점선 화살표(-.->) 극중 추가 가정 / 화살촉 없는 선(---|선후|) 시간 선후(인과 아님)",
             "flowchart LR"]
    sid = {n: f"n{i}" for i, n in enumerate(sorted(g.nodes))}
    for n in sorted(g.nodes):
        lab = g.nodes[n]["label"].replace('"', "'")
        k = g.nodes[n]["kind"]
        shape = ("[\"" + lab + "\"]") if k == "endo" else ("([\"" + lab + "\"])")
        lines.append(f"  {sid[n]}{shape}:::{k}")
    arrow = {"source": "==>", "theory": "-->", "film": "-.->"}
    for u, v, d in sorted(g.edges(data=True)):
        lines.append(f"  {sid[u]} {arrow[d['kind']]} {sid[v]}")
    lines.append("  subgraph TIME[\"시간 선후(인과 아님)\"]")
    for e in EVENTS:
        if any(e in p for p in TEMPORAL_EDGES):
            lines.append(f"    t_{e}[\"{EVENTS[e][0]} {EVENTS[e][1]}\"]")
    for a, c in TEMPORAL_EDGES:
        lines.append(f"    t_{a} ---|선후| t_{c}")
    lines.append("  end")
    lines += ["  classDef endo fill:#eef,stroke:#446;", "  classDef creative fill:#fee,stroke:#a44,stroke-dasharray:3;",
              "  classDef hist fill:#efe,stroke:#363;", "  classDef inference fill:#ffd,stroke:#984;"]
    return "\n".join(lines) + "\n"


# ───────────────────────────── 8. 경제 시나리오(가상 수치) ─────────────────────────────
def economic_scenarios():
    import yaml
    p = yaml.safe_load((ROOT / "scenario" / "scenario_parameters.yaml").read_text(encoding="utf-8"))
    out = {}
    for sid, sc in p["economic_scenarios"].items():
        avail = sc["G_hold"] - sc["G_food"] - sc["G_seed"] - sc["G_other"]
        out[sid] = {"label": sc["label"], "G_available": avail, "extra_demand": sc["extra_demand"],
                    "u_extra_exceeds": sc["extra_demand"] > avail,
                    "unit": p["unit"], "status": "가상 실험값(역사적 관측치 아님)"}
    return out


# ───────────────────────────── 9. 실행 ─────────────────────────────
def describe(cids):
    return [{"id": c, "layer": CS_BY_ID[c].layer, "text": CS_BY_ID[c].text, "basis": CS_BY_ID[c].basis,
             "status": CS_BY_ID[c].status} for c in cids]


def main():
    RESULTS.mkdir(exist_ok=True)
    res = {"index_note": "날짜는 음력 서수 인덱스(30일 월·윤달 미반영) 근사이며 양력 변환이 아님", "modes": {}}
    for name, md in MODES.items():
        r, m, t, b = check_ids(md["hard"])
        entry = {"desc": md["desc"], "result": str(r).upper(), "hard": md["hard"]}
        if r == z3.unsat:
            hard_core = [c for c in md["hard"] if CS_BY_ID[c].layer not in SOFT_LAYERS]
            soft = [c for c in md["hard"] if CS_BY_ID[c].layer in SOFT_LAYERS]
            muses, mcses = marco(hard_core, soft)
            entry["mus"] = [describe(x) for x in muses]
            entry["mcs"] = [describe(x) for x in sorted(mcses, key=lambda x: (len(x), x))]
        else:
            entry["windows"] = {e: [fmt(x) for x in (window(md["hard"], e) or [])]
                                for e in ("JSJ_ARRIVE", "POPHYEOM", "DEATH", "ACCUSE", "OKSA", "REVIEW_ORDER", "JSJ_END")}
        res["modes"][name] = entry
        print(f"{name:14s} {entry['result']}")

    # MODE F: 사료 연대 앵커의 최소 수정 + 시놉시스 선택을 최대한 보존한 예시 해
    f_hard = MODES["F_ADAPT"]["hard"]
    hist_t = layer_ids("HIST_T")
    _, mcs_f = marco(f_hard, hist_t, limit=60)
    mcs_f = sorted(mcs_f, key=lambda x: (len(x), x))
    res["F_ADAPT_anchor_corrections"] = [describe(x) for x in mcs_f]
    res["F_ADAPT_witnesses"] = []
    for mcs in mcs_f[:6]:
        keep = [c for c in hist_t if c not in mcs]
        w = witness(f_hard + keep, prefer_ids=layer_ids("FILM_SYN"))
        res["F_ADAPT_witnesses"].append({"relaxed_anchors": mcs, "kept_anchors": keep, "witness": w})
    res["F_ADAPT_death_window_per_correction"] = {
        "+".join(m): [fmt(x) for x in (window(f_hard + [c for c in hist_t if c not in m], "DEATH") or [])] for m in mcs_f[:6]}
    # MODE F-압축: 시놉시스의 결말 압축(재조사 1780 L12·격쟁 1781 봄·결말 1781 상반기·현직 처벌)을 강제하고
    # 사료 연대 앵커 중 무엇을 바꿔야 하는지 계산. 사망·부임 날짜 선택(FS_DEATH·FS_JSJ_ARRIVE)은 극중 필수 순서와
    # 충돌하므로(F_SYNOPSIS_V4 참고) 여기서는 강제하지 않는다.
    comp_req = ["FS_REVIEW_1780_12", "FS_JOKJAENG_1781_SPRING", "FS_FINAL_1781_H1", "FS_OFFICIALS_IN_OFFICE_AT_END"]
    r_c, _, _, _ = check_ids(f_hard + comp_req)
    _, mcs_c = marco(f_hard + comp_req, hist_t, limit=60)
    mcs_c = sorted(mcs_c, key=lambda x: (len(x), x))
    res["F_COMPRESSED"] = {"forced_synopsis_choices": comp_req, "base_result": str(r_c).upper(),
                           "anchor_corrections": [describe(x) for x in mcs_c],
                           "witness_correction": (pick := next((m for m in mcs_c if "HT_ACCUSE_40" not in m and "HT_BURIAL_5" not in m),
                                                              mcs_c[0] if mcs_c else [])),
                           "witness": witness(f_hard + comp_req + [c for c in hist_t if c not in pick],
                                              prefer_ids=["FS_CHOGEOM_1780_6", "FS_JSJ_ARRIVE_1780_6"])}
    (RESULTS / "csp_results.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

    # 가능세계
    base_world_hard = f_hard  # 사료 연대 앵커는 세계별 최소 수정으로 별도 계산
    FORCED[:] = forced_assumptions(base_world_hard)
    projs = enumerate_world_projections(base_world_hard)
    reps = select_representatives(projs, 10)
    rows = []
    for i, p in enumerate(reps, 1):
        v = complete_world(base_world_hard, p)
        creative_true, flags = world_metrics(v)
        dsets = min_date_changes(v, base_world_hard, hist_t)
        rows.append({"world": f"W{i:02d}", "proj": p, "vals": v, "assump": creative_true, "n_assump": len(creative_true),
                     "date_sets": dsets, "n_dates": len(dsets[0]), "flags": flags})
    for r, nd in zip(rows, pareto(rows)):
        r["pareto"] = nd
    (RESULTS / "worlds.json").write_text(json.dumps({"n_feasible_projections": len(projs), "dims": WORLD_DIMS,
                                                     "forced_common_assumptions": FORCED,
                                                     "worlds": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_worlds_csv(rows)
    cfs = run_counterfactuals()
    (RESULTS / "counterfactuals.json").write_text(json.dumps(cfs, ensure_ascii=False, indent=2), encoding="utf-8")
    g = build_graph()
    assert nx.is_directed_acyclic_graph(g)
    (ROOT / "08_causal_graph.mmd").write_text(mermaid(g), encoding="utf-8")
    (RESULTS / "economic_scenarios.json").write_text(json.dumps(economic_scenarios(), ensure_ascii=False, indent=2), encoding="utf-8")
    import report_writer  # noqa: E402  (같은 폴더의 보고서 생성기)
    report_writer.write_all(res, rows, len(projs), cfs)
    print(f"feasible world projections: {len(projs)}; representatives: {len(rows)}")


def explain_world(r):
    v = r["vals"]
    murder = ("일부 주도자의 사전 결의" if v["premeditated"] else "현장에서 형성된 살해 의도") + "와 촉발 사건(S11)"
    path = [n for n, k in (("권중립 책임 전가", "kjr_shifts_blame"), ("이가원 선택적 정보", "lgw_selective"),
                           ("주민 간 자생적 소문", "u_resident_rumor")) if v[k]]
    refusal = "종자·양식을 위협하는 추가 요구(경제적 거절)" if v["econ_refusal"] else "비경제적 거절 사유(창작 필요)"
    motive_kill = f"{refusal} → 책임 귀인 경로[{', '.join(path)}] → {murder}"
    hw = []
    if v["hwan_believes"]:
        emo = ", ".join(x for x, k in (("죄책감", "hwan_guilt"), ("가족 의무", "u_family_duty")) if v[k])
        hw.append(f"믿음({emo})" if emo else "믿음(정서적 수용 동기 없음)")
    if v["hwan_money_interest"]:
        hw.append("금전 이해")
    lg = "살해범 인지·사전 관여" if v["lgw_prior_involvement"] else ("사후 살해범 인지" if v["lgw_knows_killers"] else "살해범 모름")
    motive_frame = f"이가원: 금전 요구 거절 후 사주({lg}) / 조환: {' + '.join(hw)}"
    admin = []
    admin.append("강압적 권분" if v["kjr_coercive"] else "자발적 권분")
    if v["kjr_coercive"]:
        admin.append("권중립 인지" if v["kjr_knew_coercion"] else "권중립 미인지(이가원 단독 강압)")
    if v["a5_inflated"]:
        admin.append("실적 과장")
    if v["jsj_knew_at_pophyeom"]:
        admin.append("조상진 포폄 시 인지")
    elif v["jsj_learned_later_no_correct"]:
        admin.append("조상진 사후 인지·미정정")
    else:
        admin.append("조상진 미인지(감독책임 우려만)" if v["u_jsj_supervisory_fear"] else "조상진 미인지")
    admin.append("복검: 진술원 공유" if v["bokgeom_shared_sources"] else "복검: 검증 소홀")
    return motive_kill, motive_frame, "; ".join(admin)


def write_worlds_csv(rows):
    fields = ["world", "pareto_nondominated", "주요 가정", "시간제약(최소 사료 연대 수정)", "사료 변경", "살해 동기",
              "무고 동기", "추가 검증 필요", "미확인 가정 수", "날짜 수정 수"] + [d for d, _ in WORLD_DIMS] + \
             ["econ", "scapegoat", "admin", "family", "judicial", "investigable"]
    with (ROOT / "05_possible_worlds.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for r in rows:
            mk, mf, admin = explain_world(r)
            dates = " | ".join("+".join(s) for s in r["date_sets"])
            need = sorted({EXOG[a][0] for a in r["assump"]})
            w.writerow([r["world"], r["pareto"], admin, f"극중 필수 순서 충족; 수정 후보: {dates}",
                        f"{r['n_dates']}개 앵커 수정(대안 {len(r['date_sets'])}종)", mk, mf,
                        "변수 " + ", ".join(need), r["n_assump"], r["n_dates"]] +
                       [r["proj"][d] for d, _ in WORLD_DIMS] + [int(x) for x in r["flags"].values()])


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    main()
