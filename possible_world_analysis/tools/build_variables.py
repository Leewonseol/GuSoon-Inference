#!/usr/bin/env python3
"""02_variables.yaml 생성기.

layer:   historical(사료가 직접 다루는 변수) | institutional(제도) | context(비교·후대 맥락)
         | theory(이론 해석틀) | scenario(극중 설정·가설: 역사적 사실 아님)
status:  원문 확인 | 간접 확인 | 미확인 | 사료 간 충돌 | 극중 설정 | 미입증
basis:   1차 사료 | 1차 사료(비교·후대) | 학술연구 | 이론 | 제도 해설 | 극중 설정 | 극중 가설 | 모형 추론
claim_ids        : 이 변수를 직접 제약하는 주장(01_claim_registry.csv)
context_claim_ids: 비교·후대 맥락으로만 쓰는 주장(1780년 배천의 관측 근거로 쓰면 안 됨)
"""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
V = []


def v(id, name, definition, domain, layer, basis, status, claims="", ctx="", sources="", symbols="", note=""):
    sp = lambda s: [x for x in s.split(";") if x] if s else []
    V.append({"id": id, "group": id[0], "name": name, "definition": definition, "domain": domain, "layer": layer,
              "basis_type": basis, "evidence_status": status, "claim_ids": sp(claims), "context_claim_ids": sp(ctx),
              "source_ids": sp(sources), "model_symbols": sp(symbols), "note": note})


# ── T군: 시간·관직·사건 순서 ──
v("T1", "권중립의 백천군수 재임 구간", "권중립이 백천군수로 재임한 음력 시작·종료 시점", "[KJR_START, KJR_END] (음력 서수)",
  "historical", "1차 사료", "미확인", "CL-SIM-07", "", "SIM", "KJR_START;KJR_END",
  "초검관이었다는 간접 기록만 있음 → 초검 시점에 재임했다는 제약만 사용. 부임·이임 기사 미확보")
v("T2", "조상진의 황해감사 재임 구간", "조상진이 황해감사로 재임한 구간", "[JSJ_ARRIVE, JSJ_END]", "historical", "1차 사료", "간접 확인",
  "CL-OFF-04;CL-OFF-01;CL-OFF-03;CL-SIL-09", "", "SIGOK_PDF;BIB1781;SIL1783M;SIL1783", "JSJ_ARRIVE;JSJ_END",
  "부임(1780 여름)은 미확인, 1781 L9 재임·1783 L5 대사성은 간접 확인")
v("T3", "이경양의 황해감사 부임 및 재임", "후임 감사 이경양의 부임 시점", "LKY_START ≤ 1782 L4 23", "historical", "1차 사료", "간접 확인",
  "CL-OFF-02", "", "SIL178204", "LKY_START", "정확한 부임일 미확인")
v("T4", "권중립·조상진 재임 중첩 여부", "두 관리의 재임 구간이 겹치는가", "bool (T1 ∩ T2 ≠ ∅)", "historical", "모형 추론", "미확인",
  "CL-OFF-04;CL-SIM-07", "", "SIM;SIGOK_PDF", "", "T1이 미확인이므로 판정 불가. 극중 필수 조건은 중첩을 요구")
v("T5", "권중립의 포폄 시점", "조상진(또는 다른 감사)이 권중립을 평가한 시점", "음력 6·12월(정기) 또는 수시", "institutional", "제도 해설", "미확인",
  "CL-INST-01;CL-FILM-REQ-01", "", "GYDJ_POPHYEOM", "POPHYEOM", "실제 포폄계본 미확보")
v("T6", "포폄의 평가자", "포폄을 내린 관찰사", "{조상진, 윤방 등 전임, 미상}", "scenario", "극중 설정", "미확인",
  "CL-FILM-REQ-01;CL-INST-01", "", "GYDJ_POPHYEOM", "pophyeom_by_jsj", "윤방 등 전임 감사의 성명·재임은 이번 실행에서 확인하지 못함")
v("T7", "권중립의 포폄 등급", "상·중·하 등 평가 등급", "{상, 중, 하, 미상}", "scenario", "극중 가설", "미확인",
  "CL-FILM-REQ-02", "", "", "jsj_good_pophyeom", "포폄계본 미확보")
v("T8", "윤씨 사망 시점", "윤씨가 사망한 음력 시점", "음력 서수", "historical", "1차 사료", "사료 간 충돌",
  "CL-SIM-01;CL-SIL-01;CL-SIM-06;CL-FILM-03", "", "SIM;SIL1783;SIGOK_PDF", "DEATH",
  "사료가 사망일을 직접 주지 않음. 성옥 연대(1780/1781) 채택에 따라 가능 구간이 달라짐")
v("T9", "윤씨 매장 시점", "사망 후 매장까지", "사망 + 4~5일", "historical", "1차 사료", "간접 확인", "CL-CHUG-01;CL-SIM-06", "", "CHUG;SIM", "BURIAL",
  "원문 일수 표현 미확보")
v("T10", "이가원의 금전 요구 시점", "이가원이 조재항에게 금품을 요구한 시점", "> 사망", "historical", "1차 사료", "간접 확인", "CL-CHUG-02", "", "CHUG", "MONEY_DEMAND")
v("T11", "농요 제작·유포 시점", "이가원이 농요를 만들어 퍼뜨리기 시작한 시점", "> 사망", "historical", "1차 사료", "간접 확인", "CL-SIL-03;CL-CHUG-04", "",
  "SIL1783;CHUG", "SONG")
v("T12", "조환 사주 시점", "이가원이 조환을 사주한 시점", "사망 < T12 < 고발", "historical", "1차 사료", "간접 확인", "CL-CHUG-03", "", "CHUG", "INSTIGATE")
v("T13", "공식 고발 시점", "관아에 고발이 접수된 시점", "사망 + 약 40일(35~45 허용)", "historical", "1차 사료", "간접 확인",
  "CL-SIM-06;CL-CHUG-04;CL-SIL-13", "", "SIM;CHUG;SIL1783", "ACCUSE")
v("T14", "권중립 초검 시점", "초검 실시 시점", "≥ 고발", "historical", "1차 사료", "간접 확인", "CL-SIM-07;CL-SIM-06", "", "SIM", "CHOGEOM")
v("T15", "이우배 복검 시점", "복검 실시 시점", "> 초검", "historical", "1차 사료", "간접 확인", "CL-SIM-07", "", "SIM", "BOKGEOM")
v("T16", "옥사 성립 시점", "살인 옥사가 성립한 시점", "1780 L6(심리록) vs 1781(실록 회고)", "historical", "1차 사료", "사료 간 충돌",
  "CL-SIM-01;CL-SIL-01", "", "SIM;SIL1783", "OKSA", "04_historical_conflicts.md 참조")
v("T17", "조재항 구금 시작·종료", "구금 구간", "[초검 이후, 방면 판부 이후]", "historical", "1차 사료", "간접 확인", "CL-SIL-07;CL-SIL-11", "",
  "SIL1783", "DETAIN_START;DETAIN_END", "석방 집행일 미상")
v("T18", "정조의 재조사 명령", "조상진에게 재조사를 명한 시점", "1781 봄(실록 회고) / 극중 1780 L12", "historical", "1차 사료", "사료 간 충돌",
  "CL-SIL-02;CL-SIM-03;CL-FILM-07", "", "SIL1783;SIM;SIGOK_PDF", "REVIEW_ORDER;HYEONGJO_1781_8",
  "시곡 PDF 부록은 1780 L12 명령을 '역사에 근거'로 분류하나 근거 구절을 제시하지 않음")
v("T19", "조재정 격쟁", "격쟁 시점", "1782 L7", "historical", "1차 사료", "간접 확인", "CL-SIM-04;CL-FILM-10", "", "SIM", "JOKJAENG")
v("T20", "최종 판부", "방면·정배·파직 판부", "1783 L6 3", "historical", "1차 사료", "간접 확인", "CL-SIL-07;CL-SIL-08;CL-SIL-09", "", "SIL1783", "FINAL")

# ── E군: 경제·농업·계층 ──
v("E1", "1780~1781년 배천의 농업 상황", "배천의 작황·구휼 수요", "{양호, 부분 부족, 흉작, 미상}", "context", "1차 사료(비교·후대)", "미확인",
  "CL-ECON-01", "CL-ECON-03;CL-ECON-06", "SIL1780J;BIB178207;SIL1793", "", "1780년 배천 직접 기록 없음. 1779 전국 회복 평가는 전면 흉년 가정을 제약")
v("E2", "가구별 식량 접근성 격차", "가용성과 접근성의 가구 간 차이", "정성", "theory", "이론", "미확인", "CL-THY-06;CL-ECON-07", "", "FAO2008;NIKH_NH36", "")
v("E3", "상층 양반지주·토호지주의 경제력", "고을 내 최상층 지주의 경제력", "정성", "context", "학술연구", "미확인", "CL-LEE-01;CL-ECON-07", "",
  "LEE2009;NIKH_NH36", "", "배천 개별 자료 없음")
v("E4", "조재항의 경제적 지위", "조재항 가호의 재력", "{넉넉함(사료), 정확한 규모 미상}", "historical", "1차 사료", "간접 확인", "CL-CHUG-05", "", "CHUG", "",
  "'넉넉하게 살았다'까지만. 토지·곡식 규모 없음")
v("E5", "조재항의 영향력·강제 권분 회피 능력", "서민지주·요호부민으로서 권분 요구를 회피하기 어려웠는가", "bool", "scenario", "극중 설정", "미입증",
  "CL-FILM-REQ-03;CL-LEE-01", "", "LEE2009", "e5_cannot_evade", "계층 규정은 창작")
v("E6", "서민지주·부농·요호부민의 출연 부담", "부담이 조재항에게 집중되는가", "bool", "scenario", "극중 가설", "미입증", "CL-LEE-01", "CL-CMP-03",
  "LEE2009;BIB1741", "burden_concentrated")
v("E7", "상층 지주들의 권분 회피 여부", "상층 지주가 출연을 회피했는가", "bool", "scenario", "극중 가설", "미입증", "CL-LEE-01", "", "LEE2009", "u_elite_evade")
v("E8", "조재항의 최초 출연량", "최초 출연 곡식량", "가상 단위(scenario/scenario_parameters.yaml)", "scenario", "극중 설정", "극중 설정", "", "", "", "",
  "가상 실험값 전용. 역사 데이터셋에 넣지 않음")
v("E9", "추가 출연 요구량", "추가 요구량과 가용량의 비교", "가상 단위; u_extra_exceeds", "scenario", "극중 설정", "극중 설정", "", "", "", "u_extra_exceeds",
  "ECON_A(초과)/ECON_B(이내) 시나리오")
v("E10", "식솔의 양식과 종자 비축량", "G_양식·G_종자", "가상 단위", "scenario", "극중 설정", "극중 설정", "CL-FILM-01", "", "SIGOK_PDF", "", "가상 실험값 전용")
v("E11", "소작농과 관련된 부담", "소작 관계에서 생기는 양식·종자 부담", "정성", "scenario", "극중 설정", "미입증", "CL-FILM-01", "", "SIGOK_PDF", "")
v("E12", "다음 수확 전까지의 생계 위험", "G_가용 < 추가 요구일 때의 위험", "bool", "scenario", "극중 가설", "미입증", "", "", "", "econ_refusal")
v("E13", "빈농·몰락 소농의 식량 부족", "일부 가구의 당장의 부족", "bool", "scenario", "극중 가설", "미입증", "CL-THY-06", "CL-ECON-02;CL-ECON-03",
  "FAO2008;BIB178206;BIB178207", "u_shortage", "1782년 배천 기록을 1780년으로 소급 금지")
v("E14", "공곡·환곡과 민간 권분의 관계", "가분(관곡)과 권분(부민 출연)의 병존·대체", "정성", "context", "1차 사료(비교·후대)", "미확인", "", "CL-ECON-02;CL-ECON-03",
  "BIB178206;BIB178207", "", "加分 ≠ 勸分")
v("E15", "지역 내 구휼 대상 가호의 규모", "구휼 대상 호수", "미상", "context", "1차 사료(비교·후대)", "미확인", "", "CL-ECON-05", "HOGU", "",
  "1789 호구를 1780년 값으로 쓰지 않음")

# ── A군: 권분·포폄·행정 ──
v("A1", "권분의 자발성", "출연이 권유에 그쳤는가", "bool", "scenario", "극중 가설", "미입증", "CL-LEE-02;CL-FILM-01", "CL-CMP-03;CL-CMP-04",
  "LEE2009;SIL1783A;BIB1741", "entitlement_framing")
v("A2", "늑분 발생 여부", "강제 권분(늑분)이 있었는가", "bool", "scenario", "극중 가설", "미입증", "CL-LEE-02", "CL-CMP-01;CL-CMP-02;CL-CMP-05",
  "LEE2009;BIB1727;BIB1731;SIL1783O", "kjr_coercive", "제도적 선례는 있으나 1780 배천 직접 기록 없음")
v("A3", "관봉(官封) 발생 여부", "관아가 부민 곡식을 봉함했는가", "bool", "scenario", "극중 가설", "미확인", "", "CL-REQ-01;CL-CMP-01", "BIB1727", "",
  "1782 서명선 비판 기사 미확보")
v("A4", "강제 대부 및 상환 여부", "강제 대부·상환", "bool", "scenario", "극중 가설", "미확인", "", "CL-REQ-01", "", "", "1782 서명선 비판 기사 미확보(비교 사례 후보)")
v("A5", "권중립의 실제 구휼 실적", "실적의 실재·과장 여부", "{실재, 과장, 미상}", "scenario", "극중 설정", "미입증", "CL-FILM-01;CL-FILM-14", "", "SIGOK_PDF",
  "a5_inflated;RELIEF_ADMIN")
v("A6", "권중립의 인사상 이익", "포폄·포상을 통한 이익 기대", "bool", "scenario", "극중 가설", "미확인", "", "CL-REQ-02;CL-CMP-03", "BIB1741",
  "u_kjr_reward_expect;kjr_career_stake")
v("A7", "조상진의 포폄 등급 및 근거", "긍정 포폄 여부와 근거", "bool", "scenario", "극중 가설", "미확인", "CL-FILM-REQ-02;CL-INST-01", "", "GYDJ_POPHYEOM",
  "jsj_good_pophyeom", "포폄계본 미확보")
v("A8", "포폄계본의 사실 정확성", "평가 근거 보고가 강압·부담을 포함했는가", "bool", "scenario", "극중 가설", "미확인", "CL-FILM-14", "CL-ECON-04",
  "SIGOK_PDF;SIL178204", "a5_inflated", "1782 이경양 농황 보고 질책은 '보고 부실'의 후대 비교 사례일 뿐")
v("A9", "강제 권분 관련 주민 항의", "항의가 관아에 접수되었는가", "bool + 시점", "scenario", "극중 설정", "미입증", "CL-FILM-14", "CL-CMP-05",
  "SIGOK_PDF;SIL1783O", "COMPLAINT")
v("A10", "권중립의 강압 인지", "권중립이 강압을 알았는가", "bool", "scenario", "극중 가설", "미입증", "", "", "", "kjr_knew_coercion")
v("A11", "조상진의 강압 인지 시점", "포폄 전 / 포폄 후 / 모름", "{사전, 사후, 미인지}", "scenario", "극중 가설", "미입증", "CL-FILM-06", "", "SIGOK_PDF",
  "jsj_knew_at_pophyeom;jsj_learned_later_no_correct;JSJ_LEARN")
v("A12", "권중립의 책임 전가", "구휼 실패 책임을 윤씨에게 돌리는가(행정 동기 측면)", "bool", "scenario", "극중 가설", "미입증", "", "", "", "kjr_cover_motive")
v("A13", "조상진의 평가 방어", "포폄·감독 책임을 방어할 동기", "bool", "scenario", "극중 가설", "미입증", "CL-SIL-06;CL-FILM-08", "", "SIL1783;SIGOK_PDF",
  "jsj_cover_motive;u_jsj_supervisory_fear", "실록은 '직접 조사하지 않음'만 기록. 동기는 기록 없음")
v("A14", "장부 누락·변조·허위 보고", "의도적 문서 조작 여부", "bool", "scenario", "극중 설정", "미입증", "CL-FILM-08;CL-FILM-14", "", "SIGOK_PDF", "",
  "1787 관리 비위 사례(CL-REQ-03)는 출처 미특정")
v("A15", "정조의 재조사 명령에 대한 대응", "조상진의 재조사 수행 방식", "{직접 조사, 수령 위임}", "historical", "1차 사료", "간접 확인",
  "CL-SIL-06;CL-SIL-09", "", "SIL1783", "reinvest_motivated", "수령 위임은 간접 확인, '고의'는 극중 설정")

# ── S군: 희생양화·집단폭력 ──
v("S1", "주민들의 최초 불만 대상", "불만이 처음 향한 대상(수령·부민·윤씨)", "범주", "scenario", "극중 가설", "미입증", "CL-THY-01", "", "GIRARD1986", "u_resident_rumor")
v("S2", "권중립의 책임 전가", "권중립이 윤씨에게 책임을 전가하는 정보 행위", "bool", "scenario", "극중 가설", "미입증", "CL-THY-03", "", "ROTHSCHILD2012", "kjr_shifts_blame")
v("S3", "이가원의 선택적 정보 공개", "출연량·종자 몫을 숨기고 '곳간에 곡식이 있다'만 알림", "bool", "scenario", "극중 설정", "미입증", "CL-FILM-01", "CL-CMP-02",
  "SIGOK_PDF;BIB1731", "lgw_selective")
v("S4", "윤씨의 기존 출연에 대한 주민 인지", "주민이 기존 협조를 알았는가", "bool", "scenario", "극중 가설", "미입증", "", "", "", "s4_prior_known")
v("S5", "윤씨의 거절 이유에 대한 주민 정보", "주민에게 전달된 거절 사유 정보", "범주", "scenario", "극중 가설", "미입증", "", "", "", "blame_path")
v("S6", "윤씨에게 식량난 책임을 돌리는 정도", "책임 귀인의 집중", "bool", "theory", "이론", "미입증", "CL-THY-01;CL-THY-03", "", "GIRARD1986;ROTHSCHILD2012",
  "hostility_to_yun", "분노 ≠ 살인")
v("S7", "주민들의 집단적 분노", "적대감의 형성", "bool + 시점", "theory", "이론", "미입증", "CL-THY-01;CL-THY-02;CL-THY-04", "",
  "GIRARD1986;LEEJW2015;JEDWAB2019", "HOSTILITY")
v("S8", "폭력에 동조한 사람들의 범위", "실행자·동조자의 규모", "범주", "scenario", "극중 설정", "미입증", "CL-FILM-03", "", "SIGOK_PDF", "")
v("S9", "실제 살해를 계획한 사람", "사전 결의 vs 현장 의도", "{사전, 현장}", "scenario", "극중 설정", "미입증", "CL-FILM-03;CL-THY-02;CL-CMP-08", "",
  "SIGOK_PDF;LEEJW2015;DMYJ_MOSAL", "premeditated;u_spont_intent;murder_by_residents")
v("S10", "실행자·방관자·반대자의 구분", "가담 거부 주민의 존재", "bool", "scenario", "극중 설정", "미입증", "CL-FILM-03;CL-CMP-08;CL-SIL-10", "",
  "SIGOK_PDF;DMYJ_MOSAL", "witness_dissenter", "실록의 '從輕重決罪'는 무고 관련인 처벌이지 살해범 처벌이 아님")
v("S11", "살인을 촉발한 구체적 사건", "밤길의 요구·거절 등", "bool", "scenario", "극중 설정", "미입증", "CL-FILM-03", "", "SIGOK_PDF", "u_trigger")
v("S12", "시신 이동과 범행 후 침묵", "시신 이동·침묵 강제", "bool", "scenario", "극중 설정", "미입증", "CL-FILM-04", "", "SIGOK_PDF", "")

# ── F군: 가족체계 ──
v("F1", "조재항과 윤씨의 부부관계", "관계의 질", "정성", "scenario", "극중 설정", "미입증", "CL-SIM-02", "", "SIM", "",
  "사료의 '밥 한 사발' 폭행은 혐의일 뿐")
v("F2", "권분 문제로 발생한 부부 갈등", "출연을 둘러싼 이견", "bool", "scenario", "극중 설정", "미입증", "CL-SIM-02;CL-FILM-01", "", "SIM;SIGOK_PDF",
  "yun_refuses;u_yun_other_reason")
v("F3", "윤씨와 외숙부 조환의 정서적 관계", "친밀도", "정성", "scenario", "극중 설정", "미입증", "CL-FILM-13", "", "SIGOK_PDF", "",
  "'외숙부'는 사용자 지시문. PDF는 '윤씨의 친족'")
v("F4", "조환이 윤씨의 경제적 판단을 알았는가", "거절 이유 인지", "bool", "scenario", "극중 가설", "미입증", "", "", "", "hwan_knows_reason")
v("F5", "조환과 조재항 사이의 신뢰", "기존 신뢰", "bool", "scenario", "극중 가설", "미입증", "CL-THY-05", "", "BOWEN1978", "hwan_trusts_jjh")
v("F6", "조환의 병환과 정보 접근성", "병환 및 정보 의존", "bool", "historical", "1차 사료", "간접 확인", "CL-CHUG-03", "", "CHUG", "hwan_ill;u_hwan_isolated",
  "병환은 간접 확인, 정보 의존은 추론")
v("F7", "윤씨 여동생의 최초 인식", "여동생이 아는 마지막 행적", "정성", "scenario", "극중 설정", "미입증", "", "", "", "")
v("F8", "윤씨 사망 이후 가족의 정서적 반응", "애도·의심", "정성", "scenario", "극중 설정", "미입증", "", "", "", "")
v("F9", "이가원이 조환에게 제공한 정보", "부부 언쟁·거절 이유의 재구성", "bool", "scenario", "극중 가설", "미입증", "CL-FILM-13", "", "SIGOK_PDF",
  "lgw_reports_quarrel;lgw_reframes_reason")
v("F10", "조환의 고발 동기", "죄책감·가족 의무·금전", "범주", "scenario", "극중 가설", "미입증", "CL-THY-05", "", "BOWEN1978;KERR1988",
  "hwan_guilt;u_family_duty;hwan_money_interest;hwan_accepts")
v("F11", "가족 내부의 삼각관계", "윤씨–조재항–조환 등 삼각관계", "정성", "theory", "이론", "미입증", "CL-THY-05", "", "BOWEN1978;KERR1988", "",
  "09_family_systems.mmd")
v("F12", "조환이 이가원의 주장을 믿게 되는 조건", "믿음 성립 조건", "bool", "theory", "이론", "미입증", "CL-THY-05", "", "BOWEN1978",
  "hwan_believes;u_lgw_extra_evidence")

# ── M군: 이가원 ──
v("M1", "이가원의 실제 경제적 위치", "이가원의 재산·생계", "미상", "historical", "1차 사료", "미확인", "", "", "", "", "사료 미확보: 원문 확인 전까지 값 없음(10_evidence_gaps.md)")
v("M2", "조재항(또는 윤씨)과의 친족관계", "이가원의 친족 위치", "범주", "historical", "1차 사료", "사료 간 충돌", "CL-SIL-12", "", "SIL1783;SIGOK_PDF", "",
  "3사례 보고서: 조재항의 먼 인척 / PDF: 윤씨 친족관계")
v("M3", "극중 호방 직책", "관아 호방 여부", "bool", "scenario", "극중 설정", "극중 설정", "CL-FILM-02", "", "SIGOK_PDF", "", "사료 미확인")
v("M4", "권분 정보 접근 가능성", "출연 장부 접근", "bool", "scenario", "극중 설정", "미입증", "CL-FILM-02", "CL-CMP-02", "SIGOK_PDF;BIB1731", "")
v("M5", "윤씨 생전 갈등에 대한 인지", "부부 갈등을 알았는가", "bool", "scenario", "극중 가설", "미입증", "CL-SIM-02", "", "SIM", "lgw_reports_quarrel")
v("M6", "실제 살해범 인지 여부", "이가원이 살해범을 아는가·사전 관여", "{모름, 사후 인지, 사전 관여}", "scenario", "극중 가설", "미입증", "", "", "",
  "lgw_knows_killers;lgw_prior_involvement;LGW_PRE_CONTACT", "사전 관여는 사료의 '사후 무고' 서술을 넘어섬")
v("M7", "금전 요구의 내용", "요구한 금품", "미상", "historical", "1차 사료", "간접 확인", "CL-CHUG-02", "", "CHUG", "")
v("M8", "금전 요구 거절 이후의 행동", "거절 → 사주로의 전환", "bool", "historical", "1차 사료", "간접 확인", "CL-CHUG-02;CL-CHUG-03", "", "CHUG",
  "lgw_money_refused;u_lgw_other_motive;lgw_motive", "'거절'은 무고로 이어진 정황에서의 추론")
v("M9", "조환 사주", "이가원의 조환 사주", "bool", "historical", "1차 사료", "간접 확인", "CL-CHUG-03;CL-SIL-13", "", "CHUG;SIL1783", "lgw_instigates")
v("M10", "이봉의 고발 참여", "조환 외 고발자", "bool", "historical", "1차 사료", "미확인", "", "", "", "u_other_accuser", "사료 미확보: 시놉시스 v4(p.6)만 언급. 원문 확인 필요(10_evidence_gaps.md P8)")
v("M11", "농요 제작과 최초 유포", "농요 조작", "bool", "historical", "1차 사료", "간접 확인", "CL-SIL-03;CL-SIL-04;CL-CHUG-04", "", "SIL1783;CHUG",
  "song_fabricated;lgw_song_choice")
v("M12", "목격담과 전언의 구분", "직접 목격 vs 전언", "범주", "historical", "1차 사료", "간접 확인", "CL-SIL-05", "", "SIL1783", "")
v("M13", "허위증언의 전파", "농요·전언의 확산", "정성", "historical", "1차 사료", "간접 확인", "CL-SIL-04", "", "SIL1783", "")
v("M14", "조재항에게 살인 혐의를 집중시키는 과정", "고발·혐의 집중", "bool", "historical", "1차 사료", "간접 확인",
  "CL-SIM-02;CL-SIL-08;CL-SIM-05;CL-CMP-09", "", "SIM;SIL1783;DMYJ_MUGO", "accusation")

# ── J군: 검험·재조사 ──
v("J1", "권중립 초검의 정확성", "초검 결론의 오류", "bool", "historical", "모형 추론", "간접 확인", "CL-SIM-07;CL-SIL-05;CL-SIL-13", "", "SIM;SIL1783",
  "chogeom_error;oksa_formed", "최종 판부에서 혐의가 무너졌다는 데서의 추론. 고의성은 극중 설정")
v("J2", "이우배 복검의 독립성", "복검이 독립 증거를 썼는가", "{진술원 공유, 검증 소홀, 교정}", "scenario", "극중 가설", "미입증", "CL-SIM-07", "", "SIM",
  "bokgeom_shared_sources;bokgeom_negligent;bokgeom_corrects")
v("J3", "상흔 해석", "발길질 상흔 해석", "정성", "historical", "1차 사료", "간접 확인", "CL-SIM-02;CL-SIL-05", "", "SIM;SIL1783", "")
v("J4", "직접 목격과 전언의 구분", "수사 단계의 증언 구분", "정성", "historical", "1차 사료", "간접 확인", "CL-SIL-05", "", "SIL1783", "")
v("J5", "최초 수사에서 권분 갈등 조사 여부", "초검이 권분 갈등을 조사했는가", "bool", "scenario", "극중 설정", "미입증", "CL-FILM-05", "", "SIGOK_PDF", "")
v("J6", "실제 범행 장소와 시신 발견 장소", "두 장소의 동일 여부", "bool", "scenario", "극중 설정", "미입증", "CL-FILM-03;CL-FILM-04", "", "SIGOK_PDF", "")
v("J7", "조재항 구금", "장기 구금", "bool", "historical", "1차 사료", "간접 확인", "CL-SIL-11;CL-SIL-07", "", "SIL1783", "long_detention")
v("J8", "정조의 재조사 명령", "재조사 명령·형조 심리", "bool + 시점", "historical", "1차 사료", "간접 확인", "CL-SIL-02;CL-SIM-03;CL-SIL-11", "", "SIL1783;SIM",
  "HYEONGJO_1781_8")
v("J9", "조상진의 재조사 수행", "직접 조사 여부", "bool", "historical", "1차 사료", "간접 확인", "CL-SIL-06;CL-OFF-01", "CL-CMP-07", "SIL1783;BIB1781;TGJS",
  "jsj_direct_investigation;reinvest_nonindependent;JSJ_REINVEST")
v("J10", "원본 기록과 감영 보고의 차이", "이득준 원본 vs 감영 보고", "bool", "scenario", "극중 설정", "미입증", "CL-FILM-08", "", "SIGOK_PDF", "records_preserved")
v("J11", "이득준의 극중 재조사 역할", "사관 지정", "bool", "scenario", "극중 설정", "미확인", "CL-OFF-05", "CL-CMP-07", "SJW1780;TGJS", "",
  "1780 L3 평산부사 임명은 미확인, 재조사 참여는 창작")
v("J12", "심낙수의 극중 독립 조사", "암행어사 파견", "bool", "scenario", "극중 설정", "극중 설정", "CL-FILM-09;CL-OFF-06", "CL-CMP-06", "SIGOK_PDF;YJSIL1742",
  "independent_investigator;truth_recoverable")
v("J13", "조재정 격쟁", "격쟁", "bool + 시점", "historical", "1차 사료", "간접 확인", "CL-SIM-04", "", "SIM", "JOKJAENG")
v("J14", "조재항의 방면", "방면 명령", "bool", "historical", "1차 사료", "간접 확인", "CL-SIL-07", "", "SIL1783", "")
v("J15", "실제 살해범 확인 및 처벌", "살해범 식별", "bool", "scenario", "극중 설정", "극중 설정", "CL-CMP-08;CL-SIL-10", "", "DMYJ_MOSAL", "killers_identifiable",
  "사료는 실제 살해범을 확정하지 않음")


def main():
    out = ROOT / "02_variables.yaml"
    header = ("# 02_variables.yaml — tools/build_variables.py가 생성. 직접 수정하지 말고 생성기를 고칠 것.\n"
              "# layer=scenario 인 변수는 극중 설정·가설이며 역사적 사실이 아니다.\n"
              "# 가상 수치(곡식량 등)는 scenario/scenario_parameters.yaml에만 있다.\n")
    out.write_text(header + yaml.safe_dump({"variables": V}, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")
    print(f"wrote {len(V)} variables")


if __name__ == "__main__":
    main()
