"""수동 의미 검토와 수정 이력.

자동 검사(audits.py)가 잡기 어려운 의미 변화를 원본 CSV(01 confirmed_statement·notes, 05 prop, 03 notes)와 직접 대조한 결과다.
- *_MANUAL: (대상, 검사, 판정, 근거)
- *_REVISIONS: (회차, 발견, 조치) — 실제 실행에서 나온 결과와 실제로 한 조치만 적는다.
markdown 표에 들어가므로 문자열에 세로 막대를 쓰지 않는다.
"""

# ============================================================================ AUDIT 1
AUDIT1_MANUAL = [
    ("CF001–CF050 → EP01–EP37", "omission / unsupported_episode", "PASS",
     "CF 50개가 모두 1개 이상 episode에 속하고, episode 37개가 모두 CF로 역추적된다. unsupported episode 0. "
     "CF가 참조하지 않는 05 prop 83개는 §5에 목록만 두고 node로 쓰지 않았다."),
    ("EP08 (CF020)", "semantic_strengthening", "PASS",
     "summary가 '풍각 김상제도 극히 수상하다고 말했고'를 그대로 둔다. '범인 지목'·'고발'로 바꾸지 않았고 caution에 '범인 지목이 아님'을 적었다."),
    ("EP07 (CF017)", "semantic_strengthening", "PASS",
     "'한 비장의 지휘에 따라 거짓으로 꾸며 말했다'를 유지했다. 무엇을 거짓으로 말했는지(누구를 지목했는지)는 원문에 없으므로 '거짓 지목'으로 쓰지 않았다."),
    ("EP12 (CF018)", "semantic_weakening (부인 범위 확대)", "PASS",
     "'은밀히 사주한 일은 없다'를 유지했다. '어떤 사주도 없었다'로 넓히지 않았고, '남은 밥을 준 사실은 인정'도 함께 남겨 인정과 부인의 경계를 지켰다."),
    ("EP04 '조계완 등' · EP07 '김흥득 등' · EP08 '원돌 등'", "closed_set", "PASS",
     "세 '등'이 summary에 그대로 남는다. 05 set_status(V3P0080 OPEN_SET_EXPLICIT_MEMBERS, V3P0096 OPEN_SET)와 일치한다. "
     "EP07 caution은 김명신이 명시 명단에 없지만 열린 목록이라 배제도 확정하지 않는다고 적었다."),
    ("EP13 '무고한 평민들' · EP21 '여러 죄수'", "closed_set", "PASS",
     "05 V3P0007·V3P0040은 OPEN_SET이다. summary는 복수 표현을 유지하고 caution에 김명신 포함 여부를 확정하지 않는다고 적었다. "
     "'김명신이 형벌을 받았다'는 문장은 어디에도 만들지 않았다."),
    ("EP09·EP11 (공초의 '병사')", "surface form (ID01, 사용자 확정)", "PASS",
     "ID01(병사=이광섭)은 사용자 확정(RESOLVED)이다. 그래도 summary는 원문 표면형 '병사'를 유지한다(surface_form_substitution 검사). "
     "동일성 확정은 3/4 지시 행위를 관측 사실로 올리지 않는다(이진욱 진술 그대로)."),
    ("EP07 '한 비장'", "surface form (ID02, 사용자 확정)", "PASS",
     "ID02(한 비장=한재욱)는 사용자 확정이다. summary는 '한 비장'을 유지한다. OE007은 condition 없이 같은 인물에 대한 두 진술(사주 주장 ↔ 은밀한 사주 부인)의 "
     "PARTIAL 충돌로 남고, 사주를 사실로 확정하지 않는다."),
    ("EP35 '한가'", "surface form (ID03, 사용자 확정)", "PASS",
     "ID03(한가=한재욱)은 사용자 확정이다. 처분문 표면형 '병영 비장으로 표기된 한가'를 유지했고(CF048 notes), 연결은 동일성 대장과 identity_links 컬럼에 둔다. "
     "처분 근거 행위는 confirmed set에 없어 G09 gap으로 남는다."),
    ("'병영의 하급 보조자'", "identity_forcing (ID04, 참고용 미해결)", "PASS",
     "이 표현은 05(이조원 V3P0026·V3P0027·V3P0124)에만 있다. confirmed set에 없으므로 episode·edge 어디에도 쓰지 않았다. "
     "UNRESOLVED로 두되 model_relevance=NONE, manual_decision_required=NO다."),
    ("EP08 '풍각 김상제' · EP29 '병영의 염탐 담당자'", "surface form (ID05 사용자 확정) · identity_forcing (ID06)", "PASS",
     "EP08은 '풍각 김상제'를 김명신으로, EP29는 '염탐 담당자'를 유제희로 바꾸지 않았다. 05 V3P0095의 object 필드(김명신)는 audit용 주석이라 "
     "summary에 반영하지 않았다. ID05(풍각 김상제=김명신)는 사용자 확정이지만 summary는 표면형을 유지한다. 두 node를 잇는 OE071은 condition=ID06만 남는다."),
    ("EP04 '철편 네 개' · EP30 '철퇴 네 개'", "identity_forcing (ID07)", "PASS",
     "물건 이름과 행위자(이진욱: 한재욱이 만들어 줌 / 정조: 이광섭이 만들게 함)를 각 원문대로 두었다. 대응 edge OE080은 condition=ID07이다."),
    ("EP08 '원돌 등' ↔ EP04·EP07 '정원돌'", "identity_forcing (ID11)", "PASS (수정 후)",
     "Stage 4 준비 중 찾은 미등록 동일성이다. summary는 원문 그대로였지만 동일성 대장에 없었다. ID11(UNRESOLVED)을 추가하고 "
     "EP08 caution과 identity 검사 규칙에 넣은 뒤 Audit 1을 다시 돌렸다."),
    ("EP02 (CF004·CF005)", "epistemic_collapse (중첩 진술)", "PASS",
     "layer=NESTED_TESTIMONY, epistemic_floor=RECORDED_NESTED_TESTIMONY. '명업은 나복이 … 말했다고 진술했다'로 이중 귀속을 유지했다. "
     "30여 명·횃불·지세대감은 CF005 notes대로 caution에서 객관적 사실이 아니라고 적었다."),
    ("EP09 (CF021 + CF022)", "over_merge / epistemic_collapse", "PASS",
     "진술(이진욱)과 사료 식별(CF022)을 한 episode로 묶었지만 floor는 더 약한 RECORDED_TESTIMONY다. 지시(EP09)와 실행(EP11)은 분리했다. "
     "허용 혼합 {TESTIMONY, IDENT}로 INFO 처리했다."),
    ("CF040 → EP26·EP27, CF045 → EP31·EP32", "over_merge (절 분할)", "PASS",
     "판단 주체가 다른 홍대협(official)과 정조(royal)의 경계에서만 나눴다. 두 절은 원문 substring이고 합치면 원문 전체를 덮는다. "
     "05 대조: CF040 절 → V3P0101(홍대협)·V3P0105(정조), CF045 절 → V3P0136(홍대협)·V3P0146(정조)."),
    ("EP27 (CF040 정조 절 + CF041)", "over_merge", "PASS",
     "같은 주체(정조)·같은 날·같은 기사(SRC3_006)·같은 사인/처우 쟁점이다. 판단 대상이 '부처'(아내 포함)로 넓어진 점을 summary와 caution에 남겼다."),
    ("EP27 (CF041) ↔ EP13 (CF027)", "semantic 긴장 보존", "PASS",
     "5/12 장계의 '구금·조사'와 6/13 정조의 '평범한 신문도 받지 않았다'를 어느 쪽으로도 맞추지 않았다. CF041 notes대로 royal judgment 자체로 보존하고, "
     "긴장은 OE062(CONTRADICTS_AT_CLAIM_LEVEL, PARTIAL_TENSION)로 남겼다. CF028의 열린 집합은 충돌 근거로 쓰지 않았다."),
    ("EP29 (CF043) · EP28 (CF042)", "semantic_strengthening", "PASS",
     "'책임을 연결해 판단했다'를 유지했고 '구순 때문에 죽었다'(직접 인과)로 바꾸지 않았다. 정조의 직접 인과 유보('십분 확실하다고 할 수 없다')는 EP28로 따로 두었다."),
    ("EP32 (CF045 정조 절)", "semantic_strengthening", "PASS",
     "'스스로 만들어냈다는 죄는 인정하지 않았다'를 '구순은 지세와 무관'으로 강화하지 않았다."),
    ("EP15 (CF030) · EP24 (CF038) · EP13 (CF027)", "semantic_weakening", "PASS",
     "'도난 자체가 없었다는 방향을 받아들였다'의 '방향', '약간의 실제 도난'·'보통 좀도둑 수준', '달포 이상'·'확실한 장물'을 모두 유지했다."),
    ("EP01·EP04·EP05·EP06 (A1-W1–W4)", "semantic_weakening / epistemic marker", "FIXED",
     "이전 판정은 'PASS(수동)'였으나 재검토에서 표현 차이로 넘기지 않았다. 여러 진술을 '…의 진술에 따르면' 하나로 귀속하면 뒤쪽 절이 사실 서술처럼 읽힐 수 있다. "
     "그래서 원문 문장마다 '진술했다'를 복원하고 EP04의 '자신'을 원문대로 되돌렸다. 진술자·대상·시간·동일성은 수정 전후 모두 원문과 같다. 재실행 결과 WARN 0."),
    ("EP07 (A1-E1)", "testimony_to_fact (새 regression 규칙)", "FIXED",
     "보존율로는 WARN이 아니었으나 새 규칙 epistemic_marker_deletion·testimony_to_fact가 같은 유형을 ERROR로 잡았다. 두 진술 각각에 '진술했다'를 복원했다."),
    ("EP01–EP12 (진술 episode 전체)", "actor_substitution / testimony_to_fact (새 규칙)", "PASS",
     "summary 첫 주어가 원문 첫 문장의 진술자와 같고, '진술했' 개수가 진술 member 수 이상이며, 원문의 '자신'이 그대로 남는 것을 자동 검사로 확인했다."),
    ("EP01 (CF001–CF003) · EP04 (CF007–CF010)", "temporal_conflation", "PASS",
     "EP01은 친숙·왕래(2월 초순 이전) → 힐책(2월 초순) → 단절(그 이후)의 순서를 summary 어순으로 보존한다. "
     "EP04는 28일 밤의 호출·지시와 28일 밤~29일 새벽의 철편 제작을 한 출동 준비 단계로 묶고 시간 범위(228–229)를 남겼다."),
    ("EP12 · EP23", "temporal_conflation (진술 시점 vs 내용 시점)", "PASS",
     "공초 진술 행위는 안핵 기간(5/28–6/13)으로, 진술 내용 속 사건 시점은 각 episode의 occurrence_text로 따로 기록했다(preflight §4)."),
    ("AUDIT 1 1차 실행 ERROR 2건 (EP15·EP32)", "epistemic_collapse 오탐", "오탐 확인",
     "EP15 '받아들였다', EP32 '인정하지 않았다'는 원문 그대로의 royal judgment 동사다. 검사기의 기록 행위 어휘에 없어 ERROR가 났다. "
     "내용은 고치지 않고 검사기 정규식에 '받아들'·'인정'을 추가했다."),
]

AUDIT1_REVISIONS = [
    ("1차 실행", "ERROR 2건: EP15 '받아들였다', EP32 '인정하지 않았다'가 epistemic_collapse로 잡힘. 검사기의 기록 행위 어휘에 빠져 있던 오탐",
     "episode 내용은 그대로 두고 검사기 정규식에 '받아들'·'인정'을 추가"),
    ("2차 실행", "ERROR 0, WARN 4 (EP01·EP04·EP05·EP06 원문 어휘 보존율 0.71–0.79)",
     "원문 대조 수동 검토: 빠진 토큰은 진술 어미와 '자신'→진술자 이름뿐이라 왜곡 없음 → PASS (§3)"),
    ("Stage 4 준비 중", "미등록 동일성 발견: CF020 '원돌 등' ↔ CF009·CF016 '정원돌'",
     "IDENTITY_REGISTER에 ID11(UNRESOLVED) 추가, EP08 caution 보강, identity 검사 규칙에 (원돌, 정원돌, ID11) 추가"),
    ("3차 실행 (ID11 반영)", "ERROR 0, WARN 4 (같은 4건). 이후 모든 전체 실행에서 같은 결과",
     "수동 판정 유지 → PASS"),
    ("WARN 0 작업 — 4차", "WARN 4건을 다시 검토: 진술자·대상·시간은 유지되었으나 '진술했다' 표지가 합쳐져 testimony가 사실처럼 읽힐 위험",
     "자동 INFO 강등 대신 FIXED: EP01·EP04·EP05·EP06 문장마다 '진술했다' 복원, EP04 '자신' 원문 복원 → ERROR 0, WARN 0"),
    ("WARN 0 작업 — 5차", "새 regression 규칙(epistemic_marker_deletion·testimony_to_fact·actor_substitution·occurrence_record_confusion·"
     "responsibility_to_causation·environment_to_individual_fact) 추가 후 ERROR 2건: EP07 '진술' 표지 2→0",
     "ESCALATED_ERROR로 처리하고 EP07 문장마다 '진술했다' 복원 → ERROR 0, WARN 0"),
    ("WARN 0 작업 — 6차", "regression 케이스 15개 중 '진술자 바꿔치기' 1개를 검사기가 놓침(이름이 summary 어딘가에 있으면 통과하던 약점)",
     "actor_substitution에 'summary 첫 주어 = 원문 첫 주어' 검사를 추가 → 15/15 탐지. 최종 ERROR 0, WARN 0, UNRESOLVED 9(동일성), INFO 8"),
    ("사용자 동일성 확정 반영", "사용자가 ID01·ID02·ID03·ID11을 확정",
     "동일성 대장 status=RESOLVED(resolved_by=USER, 근거 기록). summary는 원문 표면형 유지. 확정 ID 치환은 surface_form_substitution, "
     "미확정 ID 치환은 identity_forcing으로 구분. 재실행 ERROR 0, WARN 0, UNRESOLVED 9→5(ID04 참고용 포함), INFO 8→12(resolved_identity 4)"),
    ("사용자 동일성 확정 반영 (ID05)", "사용자가 ID05(풍각 김상제=김명신)를 확정",
     "status=RESOLVED(resolved_by=USER, 근거 기록). EP08 summary는 표면형 '풍각 김상제' 유지. 재실행 ERROR 0, WARN 0, UNRESOLVED 5→4"),
    ("사용자 검토: 불확실성 유지", "사용자가 ID06·ID07·ID08을 추가 사료 없이 확정하지 않기로 함",
     "status UNRESOLVED 유지, review_decision=KEEP_UNRESOLVED, manual_decision_required=NO. 구조 변경 없음. ERROR 0, WARN 0"),
]

# ============================================================================ AUDIT 2
AUDIT2_MANUAL = [
    ("OE001–OE107 (68개)", "unsupported_edge", "PASS",
     "모든 edge의 supporting fact가 양 끝 node의 구성 CF 또는 환경 행이다. 예외는 OE060 하나로, 안핵 명령 CF035를 절차 근거로 인용했고 INFO로 표시했다."),
    ("edge type 전체", "causal_inflation", "PASS",
     "CAUSES 0개. 정조의 책임 귀속은 RESPONSIBILITY_LINK 7개로 표현했고 모두 royal judgment node(EP29·EP30)로만 들어간다. "
     "구순 관련 node(EP01·EP08·EP10·EP29)에서 사망·사인 node(EP13·EP26·EP27)로 가는 edge는 없다."),
    ("Branch A (생물학적)", "missing_relation (지정 구조)", "PASS",
     "EP13 → EP26(REVIEW_OF) → EP27(REVIEW_OF), ENV01·ENV03 → EP26·EP27(CONTEXT_SUPPORTS). 홍대협 질병 평가와 정조 부처 전염병 판단이 별개 node다."),
    ("Branch B (절차·책임)", "missing_relation (지정 구조)", "PASS",
     "구순 쪽: EP01(관계 악화)·EP08(발언 기록)·EP11(체포)·EP13(구금·사망 보고) → EP29. 이광섭 쪽: EP04(출동·철편, ID07)·EP09(병사 지시, ID01) → EP30, "
     "EP14(5/12 평가) → EP30(REVIEW_OF). 두 사슬은 EP29 → EP30(책임 비교)에서만 만난다. 구순 → 김명신 사망 단일 edge는 없다."),
    ("EP15 → EP25 (REVISES) · EP15·EP17 ↔ EP24", "judgment_flattening (5월 → 6월)", "PASS",
     "5/12 도난 부재 방향(EP15)과 5/27 이조원 보고(EP17)를 지우지 않았다. 6/13 판단(EP24·EP25)과 CONTRADICTS_AT_CLAIM_LEVEL·REVIEW_OF·REVISES로 잇는다. "
     "판단 node 9개가 모두 남아 있다."),
    ("OE100–OE107 (환경 8개)", "environmental_leakage", "PASS",
     "모두 ENV → 판단·보고 node(EP21 윤노동 별단, EP26 홍대협 평가, EP27 정조 판단)의 CONTEXT_SUPPORTS이고 basis는 ENVIRONMENTAL_CONTEXT 하나다. "
     "김명신 개인 감염 node는 없다."),
    ("OE104 (ENV04 = E004 → EP27)", "environmental_leakage / temporal", "PASS",
     "E004(5/12 옥수 전염병 치료 명)는 김명신 사망 보고와 같은 날이고 사망보다 뒤다. 처우나 사망에 영향을 준 것으로 잇지 않고 6/13 판단 node의 "
     "custody-health context로만 두었다(caution 명시)."),
    ("feature link 57개", "institutional_overreach", "PASS",
     "creates_event=NO로 고정했다. basis가 INSTITUTIONAL_COMPATIBILITY 하나뿐인 edge는 0개다. 예: 3/4 병사 → 장교 체포 지시(OE008)는 F007 COMPATIBLE, "
     "구순 → 병사 서찰(EP10)은 공식 경로로서 F020·F007 LOW."),
    ("OE008 (EP09 → EP11)", "order_execution_conflation", "PASS",
     "CF023 '병사의 분부에 따라'가 지시와 실행을 원문에서 잇는다. ORDER_TO_ACTION 가운데 유일한 OBSERVED edge이고 EP09·EP11은 별개 node다."),
    ("OE004 (EP04 → EP05)", "order_execution_conflation", "PASS (주의)",
     "DERIVED ORDER_TO_ACTION. 실행이 확인되는 것은 덕평 출동뿐이고 변지돌·정원돌 체포 지시는 실행되지 않았다(변지돌 기체포, 정원돌 미기록). 이 한계를 caution에 적었다."),
    ("EP16·EP19 (의금부 명)", "order_execution_conflation", "PASS",
     "명령만 관측된다. 실행 node를 만들지 않고 G13 gap으로 넘겼다."),
    ("claim_level 표시 edge 12개", "testimony_to_fact", "PASS",
     "진술 내용 속 순서를 잇는 edge 9개(OE001–OE006, OE008–OE010)와 진술이 끼는 충돌·검토 edge 3개(OE007·OE013·OE090)에 claim_level을 표시했다. "
     "객관적 사건 순서로 확정한 것이 아니다."),
    ("OE020–OE031 (진술 → EP23)", "testimony_to_fact", "PASS",
     "'진술이 안핵 기록에 들어갔다'는 정보 흐름이며 진술 내용의 진위를 주장하지 않는다(caution 명시)."),
    ("조건부 edge 4개 (OE010·OE040·OE071·OE080)", "identity_forcing", "PASS",
     "미확정 동일성에 기대는 edge는 condition 컬럼에 ID08·ID09·ID06·ID07을 적었다. ID09는 같은 기사 provenance로 ACCEPTED_BY_PROVENANCE다. "
     "OE007(ID02)·OE081(ID01)과 OE071의 ID05는 사용자 확정으로 condition을 지웠고, 확정 ID가 condition에 남으면 stale_identity_condition ERROR가 난다."),
    ("OE080 (EP04 → EP30, 철편/철퇴)", "identity_forcing (ID07)", "PASS",
     "RESPONSIBILITY_LINK는 condition=ID07일 때만 성립한다. 제작·지급(한재욱)과 제작 지시(이광섭)는 행위 층위가 달라 모순으로도 동일 행위로도 확정하지 않는다."),
    ("OE071 (EP08 → EP29)", "identity_forcing / claim-level 차이", "PASS",
     "정조의 '구순이 성명을 적어 주었다'와 유제희의 '구순이 말했고 자신이 기록했다'를 하나로 합치지 않았다. condition=ID06(ID05는 사용자 확정으로 제거)."),
    ("OE082 (EP14 → EP30)", "judgment_flattening (주체 혼동)", "PASS",
     "'비장에게 맡김'은 5/12에는 이문협, 6/13에는 이광섭에 대한 비판이다. 주체를 합치지 않고 REVIEW_OF로만 이었다."),
    ("OE063 (EP27 → EP28)", "causal_inflation", "PASS (주의)",
     "같은 날 정조 판단 안의 두 판단을 CONTEXT_SUPPORTS(basis SOURCE_DIRECT)로 잇는다. 앞 판단이 뒤 판단의 사유라는 문장은 없으므로 원인이 아니라 양립 관계로만 둔다."),
    ("OE013 (EP02 ↔ EP24)", "testimony_to_fact", "PASS",
     "중첩 진술의 '30여 명·횃불'과 홍대협의 '보통 좀도둑' 사이의 충돌은 규모에 관한 것이다. 도난 존재 자체는 양쪽이 인정한다(caution)."),
    ("OE097 (EP36 → EP37)", "judgment_flattening", "PASS",
     "6/13 파직과 6/16 유임을 모두 node로 남기고 REVISES로 이었다. 사유는 G10 gap이다."),
    ("전체 edge", "temporal_inversion / acyclicity", "PASS",
     "CONTRADICTS 외의 edge는 모두 src.t_min ≤ dst.t_max이고 cycle이 없다. 날짜가 없는 EP08은 시간 edge 없이 INFORMATION_FLOW(OE027)·RESPONSIBILITY_LINK(OE071)에만 참여한다."),
    ("고립 node", "missing_relation", "PASS",
     "고립 node 0개. 처분 node(EP33–EP37)는 책임 판단·복명과 PROCEDURAL_NEXT로 이어진다."),
]

AUDIT2_REVISIONS_PRE = [
    ("이 세션 이전 전체 실행 (인계 기록)", "ERROR 0으로 통과", "수정 없음"),
    ("이 세션 재실행 (ID11 반영 뒤, 이후 모든 실행 동일)",
     "ERROR 0, WARN 0, INFO 7 (조건부 edge INFO 6개, endpoint 밖 절차 근거 OE060 INFO 1개). ID11은 어느 edge condition에도 쓰이지 않음",
     "INFO를 하나씩 수동 검토(§2) — 수정 없음. 동결 해시 86a529da3baf… 유지"),
]

AUDIT2_REVISIONS = AUDIT2_REVISIONS_PRE + [
    ("WARN 0 작업", "WARN은 원래 0. 조건부 identity edge 6개를 INFO로 두던 것이 사료 모호성 성격이라 UNRESOLVED로 재분류했다. "
     "PARTIAL 충돌 edge 2개(OE007·OE062)도 UNRESOLVED로 표시했다. 근거 문구의 동일성 표면형 쌍 검사와 책임→직접 인과·환경→개인 사실 문구 검사를 추가",
     "edge 데이터는 변경 없음. 최종 ERROR 0, WARN 0, UNRESOLVED 8, INFO 1(OE060 절차 근거)"),
    ("사용자 동일성 확정 반영", "OE007(ID02)·OE081(ID01)의 condition이 확정 ID를 가리킴",
     "condition 제거, caution을 '같은 인물에 대한 서로 다른 진술'·'행위는 진술로만 확인'으로 수정. 확정 ID가 condition에 남으면 ERROR(stale_identity_condition). "
     "재실행 ERROR 0, WARN 0, UNRESOLVED 8→6, INFO 1"),
    ("사용자 동일성 확정 반영 (ID05)", "OE071 condition에 확정 ID05가 남음",
     "condition을 ID06만 남기고 caution 수정. 재실행 ERROR 0, WARN 0, UNRESOLVED 6→5"),
    ("사용자 검토: 불확실성 유지", "OE007 부분 충돌·OE062 범위 미확정을 결정하지 않기로 함",
     "observed_edges.csv에 uncertainty_status(OE007=PARTIAL_CONFLICT, OE062=UNRESOLVED_SCOPE, OE010·OE071·OE080=CONDITIONAL_UNRESOLVED_IDENTITY)와 "
     "review_decision 컬럼 추가. condition·끝점·type은 그대로. 부분 충돌 edge에 상태가 없으면 ERROR. ERROR 0, WARN 0"),
]

# ============================================================================ AUDIT 3
AUDIT3_MANUAL = [
    ("LATENT 후보 38개 전부", "bridge support 재감사", "FIXED",
     "이전 source_consistency는 양끝 OBSERVED 사실의 확실성까지 섞어 평가했다. 재감사는 후보가 새로 추가한 bridge 내용 자체의 근거만 본다. "
     "endpoint 구성 fact는 근거에서 뺐고, 시간·제도·환경 적합은 plausibility로 분리했다. 결과: source support HIGH 7 → 0, final HIGH 4 → 0. "
     "G01a·G06a HIGH → MEDIUM(비-endpoint 근거 CF026·CF029가 일부만 지지). G07a·G08a HIGH → LOW(이유·동기를 적은 사료 없음, endpoint 내용뿐)."),
    ("후보 38개 · latent node 46 · latent edge 71", "latent_as_observed", "PASS",
     "모든 후보는 status=LATENT다. latent node id는 LN_ 접두어를 쓰고 서술은 [LATENT]로 시작한다(C() helper). "
     "observed 표(episode_nodes.csv·observed_edges.csv)에는 LATENT가 하나도 없다."),
    ("audit_attestation이 있는 후보 19개", "audit-only 승격 금지", "PASS",
     "05 prop을 인용한 후보도 모두 LATENT다. G04d(석단 공초)·G07d·G12b는 confirmed 지지 없이 05 흔적만 있어 INFO로 표시했고 LOW에 머문다. "
     "05 prop은 node로도 edge로도 쓰지 않았다."),
    ("G08a (A3-W1)", "OBSERVED/DERIVED/LATENT 분류", "FIXED → LATENT",
     "원본 대조: CF033(이조원 비판·파직)과 CF035(홍대협 차하)는 각각 OBSERVED다. 둘 사이 동기를 적은 문장은 01·05·04 어디에도 없다(SRC3_004의 V3P0033은 "
     "정조가 사건을 물었다는 내용뿐). 명시 시간순서는 이미 OE045(DERIVED)가 담고 있으므로 동기 연결은 DERIVED가 아니라 LATENT다. "
     "관측 node끼리 직접 잇던 latent edge를 latent 판단 node LN_G08a_1을 사이에 둔 mini-DAG로 바꿨다. 당시 등급(HIGH)과 world 구성은 변하지 않았다. 이후 LATENT 재감사에서 동기 bridge 근거가 없다는 이유로 source support·final 모두 LOW가 되었다."),
    ("G09b (원안 EP04 → EP35 RESPONSIBILITY_LINK)", "causal_inflation", "PASS (수정 후)",
     "원안은 observed 처분 node(royal order)로 RESPONSIBILITY_LINK를 바로 걸었다. 책임 귀속은 판단 수준이어야 하므로 latent 근거 node LN_G09b_2를 사이에 두고 "
     "처분에는 PROCEDURAL_NEXT로 잇게 고쳤다."),
    ("G10b (환경만) · G01c·G10c (제도만)", "support_basis 상한", "PASS",
     "근거가 환경 context 하나 또는 제도 compatibility 하나뿐인 후보는 grade 규칙 (5)로 LOW 상한이다. G10b의 latent node는 판단 사유 가설(individual_level=False)이고, "
     "환경에서 개인 사건을 만들지 않았다."),
    ("G06a·G06b·G12a (개인 발병·사망)", "environmental_leakage", "PASS",
     "개인 수준 latent node의 근거는 CF029(윤노동: '병들어 죽었다')와 CF040(정조: '부처가 전염병')이다. E001·E003은 environmental_fit 평가에만 썼고 "
     "ENV node에서 나가는 latent edge는 없다."),
    ("동일성에 기대는 후보 10개", "identity_forcing", "PASS",
     "가정에 IDxx가 있으면 identity_conditions로 모으고 MEDIUM 상한을 적용했다(grade 규칙 6). 그래서 G02a(ID07)가 HIGH에서 MEDIUM으로 내려갔다(재감사 뒤에도 MEDIUM: CF044가 제작 지시 부분만 지지). "
     "ID01·ID02·ID03·ID11은 사용자 확정(resolved_by=USER, 근거 기록)이고 ID04–ID08은 UNRESOLVED다. 모델이 스스로 확정한 동일성은 없다(자동 검사). "
     "확정된 ID는 MEDIUM 상한(규칙 6)에서 빠지지만 G03a·G05a·G09a는 source_consistency MEDIUM이라 등급이 그대로다."),
    ("G09b·G09c", "resolved_identity_conflict", "PRUNED",
     "G09b는 'ID02 불성립', G09c는 'ID03 불성립'을 전제한다. 사용자 확정과 충돌하므로 규칙 7로 INCOMPATIBLE·PRUNED 처리했다. 두 후보는 원래 어느 world에도 쓰이지 않았다."),
    ("G02a·G03a·G09c 원안 서술", "identity_forcing", "PASS (수정 후)",
     "원안 G02a는 '병사(이광섭)'로 ID01을 사실처럼 썼다. G03a는 '김상제' 언급 뒤 '김명신 체포'를 이어 ID05에 기댔고, G09c는 '한가 ≠ 한재욱'을 ID03 표시 없이 썼다. "
     "서술을 조건형으로 고치고 가정에 IDxx를 넣었다. 보강한 검사를 원안에 다시 돌려 이 세 건이 ERROR로 잡히는 것을 확인했다."),
    ("G04b·G07b·G07c 서술", "testimony_to_fact", "PASS",
     "'회유된 자미덕'처럼 진술 내용을 사실로 쓰던 원안 문구를 '자미덕은 …라고 진술했다'로 바꿨다. G07b의 '꾸몄다'와 G07c의 '위협'은 05 진술 내용으로만 귀속한다."),
    ("G06c·G07d·G12b (대조 후보)", "contradiction 표시", "PASS",
     "원안은 최종 판단과 부딪히는 latent 주장을 CONTEXT_SUPPORTS로 이었다. 충돌 대상(EP27·EP25)으로 CONTRADICTS_AT_CLAIM_LEVEL latent edge를 두도록 고쳤다. "
     "세 후보 모두 contradiction_risk HIGH → LOW, KEPT_AS_CONTRAST이며 기각 world W6에만 쓴다."),
    ("G04e", "pruning", "PASS",
     "구순 → 장교 공식 체포 명령. F007·F008(지휘권)과 CF023('병사의 분부에 따라')에 모두 어긋나 INCOMPATIBLE, PRUNED. 어느 world에도 쓰지 않는다."),
    ("G04b·G05a institutional_fit", "grading 판단", "PASS (판단 기록)",
     "원안은 관측 행위의 합법성 평가(EP07 회유 F002 LOW, EP10 서찰 F020 LOW)를 bridge 등급에 그대로 옮겼다. bridge가 가정하는 것은 '진술·서찰이 전달되었다'는 "
     "정보 흐름뿐이므로 MEDIUM으로 두고 근거를 notes에 적었다. 관측 행위의 LOW 평가는 node_feature_links.csv에 그대로 있다."),
    ("gap별 후보 수", "candidate_budget", "PASS",
     "gap 13개, 후보 2–5개(G04만 5개). 모든 gap에 후보가 있다."),
    ("W1–W6", "world_integrity", "PASS",
     "한 gap에 후보 1개, retained world에 INCOMPATIBLE·대조용 후보 0, 상충 쌍(G03b+G04b, G03c+G04a, G01a+G02c) 동시 사용 0, world 쌍마다 2개 이상 gap에서 다르다. "
     "모든 서술에 [L] 표지가 bridge 수 이상 있다."),
    ("W1–W6 서술", "identity_forcing / testimony_to_fact", "PASS",
     "두 표면형(병사·이광섭, 한 비장·한재욱, 한가·한재욱, 김상제·김명신, 철편·철퇴, 원돌·정원돌)이 함께 나오면 같은 서술 안에 IDxx 조건을 적었다(자동 검사). "
     "관측 부분은 '…라고 진술했다/보고했다/판단했다'로 남겼다."),
    ("latent edge 71개", "causal_inflation", "PASS",
     "CAUSES 0개. latent edge type은 모두 Stage 2의 허용 목록 안에 있다."),
    ("동결 해시", "freeze_violation", "PASS",
     "Stage 3 해시 86a529da3baf…가 Stage 4 뒤와 Stage 5 뒤에 다시 계산한 값과 같다. observed DAG(41 node · 68 edge)는 바뀌지 않았다."),
]

AUDIT3_REVISIONS = [
    ("1차 실행 (Stage 4 첫 실행)", "ERROR 2건: G01b·G03c의 audit_attestation에 'V3P0084(반대 방향)'처럼 주석이 붙어 prop id 검증 실패",
     "주석을 attestation에서 빼고 반대 방향 근거는 conflicts 문구로 옮김"),
    ("1차 뒤 수동 의미 검토", "자동 검사가 못 잡은 문제: G02a '병사(이광섭)'(ID01 단정), G02b '한재욱(비장)'(직함 단정), G03a의 ID05 암묵 의존, "
     "G09c의 ID03 표시 누락, G09b의 latent RESPONSIBILITY_LINK가 royal order node(EP35)로 직접 감, G04b '회유된 자미덕'(진술의 사실화), "
     "G06c·G07d·G12b가 충돌 대상에 CONTEXT_SUPPORTS 사용, G02a가 ID07에 기대면서 HIGH",
     "서술을 조건형·진술 귀속형으로 고침. G09b에 근거 node 추가. 대조 후보에 CONTRADICTS_AT_CLAIM_LEVEL 사용. grade 규칙 (6) 추가(미확정 동일성 → MEDIUM 상한, "
     "G02a HIGH → MEDIUM). G01a·G08a의 latent edge type을 PROCEDURAL_NEXT로 정정. G04b·G05a institutional_fit을 정보 흐름 기준 MEDIUM으로 조정"),
    ("검사기 보강", "위 문제를 자동으로 잡도록 audit3에 검사 추가: 서술 속 동일성 표면형 쌍 ↔ IDxx 조건, latent RESPONSIBILITY_LINK 대상, 모든 CAUSES 금지, "
     "환경만 근거 후보의 MEDIUM 이상 금지, 동일성 의존 후보의 HIGH 금지, 금지 동일성 status, world 상충 쌍·[L] 표지·쌍별 차이",
     "보강한 검사를 원안 후보에 다시 돌려 ERROR 6건(provenance 2, identity_forcing 3, causal_inflation 1)이 잡히는 것을 확인"),
    ("2차 실행", "ERROR 0, WARN 1 (G08a 관측 node 사이 latent edge)", "수동 검토 PASS (§3)"),
    ("Stage 5 작성 중", "W4 서술에 '병사'와 '이광섭'이 ID01 표시 없이 함께 나옴(실행 전 자체 검토)", "W4 서술에 ID01 조건 문장 추가"),
    ("3차 실행 (world 포함 재검사)", "ERROR 0, WARN 1 (같은 G08a)",
     "PASS. 이후 서술 문구 두 곳(자미덕 진술 인용, 홍대협의 '평가' 동사)을 원문에 맞게 다듬고 재실행 — 결과 동일"),
    ("WARN 0 작업 — 4차", "A3-W1(G08a) 원본 재대조: 동기 연결은 원본에 없음 → LATENT. 관측 node 사이 직접 latent edge는 관측 관계로 읽힐 위험",
     "FIXED: LN_G08a_1을 둔 mini-DAG로 변경, 같은 형태를 WARN에서 ERROR로 승격 → WARN 0"),
    ("WARN 0 작업 — 5차", "새 open_set_closure 검사가 G04b를 ERROR로 잡음. 원문 확인 결과 G04b는 \'등\'을 따옴표로 감싸 열린 목록을 표시하고 있어 검사기 오탐",
     "후보 내용은 그대로 두고 정규식이 따옴표 붙은 '등'과 목록 중간 절단을 처리하도록 수정 → ERROR 0"),
    ("WARN 0 작업 — 6차", "UNRESOLVED 문구 검토: G10 사유가 '모든 후보가 사료 지지 없음'으로 적혀 G10a(MEDIUM)와 어긋남",
     "후보 등급과 gap 근거에서 문구를 생성하도록 수정. 최종 ERROR 0, WARN 0, UNRESOLVED 1(G10), INFO 8"),
    ("사용자 동일성 확정 반영", "G03a(ID11)·G04c·G05a(ID01)·G09a(ID02·ID03)의 확정 ID 가정, G09b·G09c의 확정 ID 부정 전제, world 서술의 조건문",
     "확정 ID 가정을 빼고(G03a 4→3, G04c 3→2, G05a 3→2, G09a 3→1, 등급 변화 없음), G09b·G09c는 규칙 7로 INCOMPATIBLE·PRUNED(world 미사용). "
     "world 서술의 'IDxx가 성립한다면'을 '(IDxx, 사용자 확정)'으로 바꿈. world 구성·bridge·미해결 gap은 그대로. 재실행 ERROR 0, WARN 0, UNRESOLVED 1"),
    ("사용자 동일성 확정 반영 (ID05)", "G03b·G03c·G04a 가정과 W1·W4 서술의 ID05 조건",
     "확정 ID 가정 제거(G03b 3→2, G03c 3→2, G04a 3→2, 등급 변화 없음). W1·W4 서술을 '(ID05, 사용자 확정)'으로 수정. world 구성 그대로"),
    ("사용자 검토: 불확실성 유지", "G10(이형원 파직→유임 이유)에 latent bridge를 채택하지 않기로 함",
     "gaps.csv에 gap_status=OPEN_UNRESOLVED와 review_decision 기록. 어떤 world든 G10 후보를 쓰면 ERROR(open_gap_filled). 후보 등급·world 구성 변경 없음"),
    ("LATENT 재감사", "endpoint의 확실성이 bridge의 source support로 새어 들어간 문제(G01a·G06a·G07a·G08a 등)",
     "38개 후보 재평가(stage4_reaudit.py): observed_left·observed_right·latent_bridge_claim·bridge_directly_attested·bridge_evidence 분리, "
     "evidence_grade와 plausibility_grade 분리, final=min. 새 ERROR 규칙: bridge_support_inflation·temporal_inflation·institutional_inflation·"
     "endpoint_leakage·latent_classification. 재감사 이전 값을 넣으면 ERROR가 나는지 regression으로 확인. W5 설명을 '추가 가정이 가장 적은 world'로 수정(bridge 구성 그대로). "
     "observed graph 해시 변화 없음. 재실행 ERROR 0, WARN 0"),
]


AUDIT4_REVISIONS = [
    ("Stage 6 설계", "메커니즘 M1–M5만으로는 G07 계열(5월 판단 근거)과 G06·G12 계열(구금·질병 경과)을 담을 곳이 없음",
     "기존 후보를 묶기만 해서 M6_INITIAL_JUDGMENT_BASIS와 MB_CUSTODY_BIOLOGICAL_COURSE를 추가. 새 후보·사건·등급 변경 없음"),
    ("configuration 규칙 검토(실행 전)", "부정 후보(G02b·G05b·G13b)만 있는 world를 OFF로, 후보가 없는 world도 OFF로 읽을 위험",
     "OFF는 '부정 후보만 있음', UNSPECIFIED는 '관련 후보 없음'으로 분리. 내용상 '작동하지 않았다'는 주장만 하는 G05b·G11c·G13b는 "
     "null variant로 두어 공존·개입 분석의 근거에서 뺌"),
    ("공존 규칙 검토(실행 전)", "두 메커니즘이 한 world에서 모두 PARTIAL이기만 해도 '함께 쓰인다'로 셈",
     "함께 쓰임은 적어도 한쪽이 ON일 때만 인정. 함께 쓰는 world가 없으면 COMPATIBLE이라도 UNRESOLVED(coexistence_undetermined)로 기록"),
    ("1차 실행", "ERROR 0, WARN 0. 수동 검토에서 mechanism → investigation·review Mermaid의 관측 edge 일부를 손으로 쓴 것이 frozen edge와 다름을 발견"
     "(EP15→EP18, EP23→EP25 등은 frozen graph에 없음. 실제는 EP17 REVIEW_OF EP18, EP24 REVIEW_OF EP25)",
     "Mermaid 패널을 mechanism_super_dag_edges.csv에서 생성하도록 바꿈(관측 edge는 frozen type 그대로). 손으로 쓴 edge 0"),
    ("검사기 보강", "frozen graph에 없는 관측 사건 node가 Super-DAG에 새로 생겨도 잡는 검사가 없었고, W6의 role_type을 바꾸면 되살아나도 모름",
     "context_to_fact에 '새 관측 node 생성'을 추가, WORLD_ROLES에서 REJECTED로 정한 world가 다른 role로 바뀌면 w6_reactivation ERROR"),
    ("regression 추가", "요청된 Audit 4 regression 10건(context→사실, 환경→개인 감염, 제도→사건, world 병합, W6 재활성, 책임→생물학 사인, "
     "OFF인데 후보 생존, UNSPECIFIED를 OFF로, world 전용 LATENT 공통화, 결말의 world 종속)",
     "깨끗한 Super-DAG에서 ERROR 0을 먼저 확인한 뒤 사본만 바꿔 넣음. 10건 모두 ERROR로 잡힘(전체 36/36)"),
    ("2차 실행", "ERROR 0, WARN 0, UNRESOLVED 20(방향 미결 8, 공존 미결 2, 복수 설명 4, 기존 미해결 6), INFO 2",
     "PASS. 동결 해시 ccb7ec63763a 그대로"),
]

# ============================================================================ WARN dispositions
# 모든 WARN은 아래 네 상태 중 하나로 처리한다: FIXED / RECLASSIFIED_INFO / UNRESOLVED / ESCALATED_ERROR.
# build.py는 disposition이 없는 WARN이 남으면 멈춘다. FIXED는 이력이며, 같은 WARN이 다시 나오면 다시 처리해야 한다.
WARN_DISPOSITIONS = [
    dict(warning_id="A1-W1", audit_stage="AUDIT1", affected_item="EP01", warning_type="semantic_weakening",
         original_text="CF001 명업은 김명신이 본래 구순과 친숙하여 날마다 왕래했다고 진술했다. / CF002 명업은 김명신이 박거사 일로 구순에게 "
                       "편지를 보내 힐책했다고 진술했다. / CF003 명업은 그 뒤 구순과 김명신의 왕래가 끊겼다고 진술했다.",
         generated_text="명업의 진술에 따르면, 김명신은 본래 구순과 친숙하여 날마다 왕래했으나, 박거사 일로 구순에게 편지를 보내 힐책했고, "
                        "그 뒤 구순과 김명신의 왕래가 끊겼다.",
         risk="원문 어휘 보존율 0.78. 세 진술의 '진술했다' 표지가 하나의 '따르면'으로 합쳐져 뒤쪽 절(힐책·단절)이 사실 서술처럼 읽힐 수 있음",
         disposition="FIXED",
         justification="원문 대조 결과 진술자(명업)·대상(김명신·구순)·내부 순서는 그대로였다. 그러나 뒤쪽 절의 귀속이 약해지므로 표현 차이로 넘기지 않고 "
                       "세 진술 각각에 '진술했다'를 복원했다. 재실행 결과 WARN 사라짐(보존율 1.00).",
         fixed_text="명업은 김명신이 본래 구순과 친숙하여 날마다 왕래했다고 진술했고, 김명신이 박거사 일로 구순에게 편지를 보내 힐책했다고 진술했으며, "
                    "그 뒤 구순과 김명신의 왕래가 끊겼다고 진술했다.",
         final_status="RESOLVED", final_classification="OBSERVED (RECORDED_TESTIMONY 유지)", unresolved_reason=""),
    dict(warning_id="A1-W2", audit_stage="AUDIT1", affected_item="EP04", warning_type="semantic_weakening",
         original_text="CF007 이진욱은 2월 28일 밤 병영에서 자신을 비장청으로 불렀다고 진술했다. / CF008 이진욱은 한재욱이 자신과 조계완 등에게 "
                       "덕평으로 가도록 지시했다고 진술했다. / CF009 이진욱은 한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했다. / "
                       "CF010 이진욱은 한재욱이 철편 네 개를 만들어 주었다고 진술했다.",
         generated_text="이진욱의 진술에 따르면, 2월 28일 밤 병영에서 이진욱을 비장청으로 불렀고, 한재욱이 이진욱과 조계완 등에게 덕평으로 가도록 "
                        "지시하고 변지돌과 정원돌을 잡아오라고 지시했으며, 한재욱이 철편 네 개를 만들어 주었다.",
         risk="보존율 0.71. (1) 네 진술의 '진술했다' 표지 삭제. (2) '자신'이 '이진욱'으로 치환됨. 치환이 주체를 바꾸었는지 확인 필요",
         disposition="FIXED",
         justification="'자신'의 지시 대상은 원문에서도 진술자 이진욱이라 주체는 바뀌지 않았다. 그래도 대명사 치환은 actor 정규화이므로 자동 INFO로 넘기지 않고, "
                       "'자신'을 원문대로 되돌리고 네 진술 각각에 '진술했다'를 복원했다. 재실행 결과 WARN 사라짐.",
         fixed_text="이진욱은 2월 28일 밤 병영에서 자신을 비장청으로 불렀다고 진술했고, 한재욱이 자신과 조계완 등에게 덕평으로 가도록 지시했다고 "
                    "진술했으며, 한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했고, 한재욱이 철편 네 개를 만들어 주었다고 진술했다.",
         final_status="RESOLVED", final_classification="OBSERVED (RECORDED_TESTIMONY 유지)", unresolved_reason=""),
    dict(warning_id="A1-W3", audit_stage="AUDIT1", affected_item="EP05", warning_type="semantic_weakening",
         original_text="CF011 이진욱은 변지돌이 이미 공주진에서 잡혀간 상태였다고 진술했다. / CF012 이진욱은 장교 일행이 재돌의 처 자미덕을 "
                       "붙잡았다고 진술했다.",
         generated_text="이진욱의 진술에 따르면, 2월 29일 변지돌은 이미 공주진에서 잡혀간 상태였고, 장교 일행이 재돌의 처 자미덕을 붙잡았다.",
         risk="보존율 0.79. 두 진술의 '진술했다' 표지가 합쳐져 체포 사실이 객관 사실처럼 읽힐 수 있음",
         disposition="FIXED",
         justification="진술자·대상·날짜(2/29, chronology 열)는 유지되었다. 표지 복원으로 처리했다. 재실행 결과 WARN 사라짐.",
         fixed_text="이진욱은 2월 29일 변지돌이 이미 공주진에서 잡혀간 상태였다고 진술했고, 장교 일행이 재돌의 처 자미덕을 붙잡았다고 진술했다.",
         final_status="RESOLVED", final_classification="OBSERVED (RECORDED_TESTIMONY 유지)", unresolved_reason=""),
    dict(warning_id="A1-W4", audit_stage="AUDIT1", affected_item="EP06", warning_type="semantic_weakening",
         original_text="CF013 자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔다고 진술했다. / CF014 자미덕은 병영에서 도적 혐의로 한 차례 신문을 "
                       "받았다고 진술했다. / CF015 자미덕은 신문 뒤 비장청 다모방에 구류되었다고 진술했다.",
         generated_text="자미덕의 진술에 따르면, 자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔고, 병영에서 도적 혐의로 한 차례 신문을 받았으며, "
                        "신문 뒤 비장청 다모방에 구류되었다.",
         risk="보존율 0.76. 세 진술 표지 삭제로 신문·구류가 관측 사실처럼 읽힐 수 있음",
         disposition="FIXED",
         justification="진술자·대상·'한 차례'는 유지되었다. 표지 복원으로 처리했다. 재실행 결과 WARN 사라짐.",
         fixed_text="자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔다고 진술했고, 병영에서 도적 혐의로 한 차례 신문을 받았다고 진술했으며, "
                    "신문 뒤 비장청 다모방에 구류되었다고 진술했다.",
         final_status="RESOLVED", final_classification="OBSERVED (RECORDED_TESTIMONY 유지)", unresolved_reason=""),
    dict(warning_id="A1-E1", audit_stage="AUDIT1", affected_item="EP07", warning_type="testimony_to_fact",
         original_text="CF016 자미덕은 한 비장이 … 등을 큰 도적이라고 말하면 자신과 남편을 다음 날 석방하겠다고 말했다고 진술했다. / "
                       "CF017 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술했다.",
         generated_text="자미덕의 진술에 따르면, 한 비장이 … 석방하겠다고 말했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다.",
         risk="이전 실행에서는 보존율 0.80 이상이라 WARN이 아니었다. 이번에 추가한 regression 규칙(epistemic_marker_deletion·testimony_to_fact)이 "
              "같은 결함 유형을 찾아냄. 대질·거짓 진술이 객관 사실처럼 읽힐 위험",
         disposition="ESCALATED_ERROR",
         justification="A1-W1–W4와 같은 결함 유형이므로 ERROR로 올리고 다음 stage 진행 전에 고쳤다. 두 진술 각각에 '진술했다'를 복원했다. "
                       "'한 비장'·'등'·'거짓으로 꾸며'는 그대로 두었다. 재실행 ERROR 0.",
         fixed_text="자미덕은 한 비장이 … 석방하겠다고 말했다고 진술했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술했다.",
         final_status="RESOLVED", final_classification="OBSERVED (RECORDED_TESTIMONY 유지)", unresolved_reason=""),
    dict(warning_id="A3-W1", audit_stage="AUDIT3", affected_item="G08a", warning_type="latent_as_observed",
         original_text="CF033 정조는 이조원이 중대 사실을 직접 안핵하지 않고 전해 들은 말을 서계에 붙인 점을 문제 삼았고 이조원을 파직하도록 명했다. / "
                       "CF035 정조는 홍대협에게 사건을 자세히 조사해 오라고 명하고 그를 충청도 공주 안핵어사로 차하했다. (둘 사이 동기 문장 없음; SRC3_004·V3P0033도 없음)",
         generated_text="latent node 없이 관측 node EP18 → EP20을 LATENT PROCEDURAL_NEXT로 직접 연결",
         risk="관측 node 둘을 잇는 edge는 표·그림에서 관측 관계처럼 읽힐 수 있음(LATENT → OBSERVED/DERIVED 승격 위험)",
         disposition="FIXED",
         justification="원본 대조 결과 두 행위는 각각 OBSERVED이고, 둘 사이 동기 연결은 어느 CSV에도 없다 → 분류 LATENT. DERIVED의 근거(명시 시간순서 등)는 "
                       "이미 OE045(TEMPORAL_BEFORE)가 담고 있다. latent 판단 node LN_G08a_1을 사이에 둔 mini-DAG(EP18 → LN_G08a_1 → EP20)로 바꾸고, "
                       "관측 node끼리 직접 잇는 latent edge는 이제 ERROR로 막는다. 재실행 결과 WARN 사라짐.",
         fixed_text="EP18 —INFORMATION_FLOW→ LN_G08a_1 [LATENT] 정조가 이조원 서계의 직접 안핵 부재를 근거로 현지 직접 안핵이 필요하다고 판단 "
                    "—PROCEDURAL_NEXT→ EP20",
         final_status="RESOLVED", final_classification="LATENT", unresolved_reason=""),
]
