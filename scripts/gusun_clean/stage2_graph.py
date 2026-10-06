"""STAGE 2 — Audit 1을 통과한 episode + 제도 피쳐 + 환경 피쳐 → observed partial DAG.

- LATENT node/edge는 여기서 만들지 않는다.
- 모든 edge에 basis와 근거 fact(supporting)를 붙인다.
- CAUSES는 쓰지 않는다. 정조가 명시한 책임 귀속은 RESPONSIBILITY_LINK로 표시하고, 판단 node(EP29/EP30)로만 들어간다.
- claim_level=True: 진술 내용 속 시간·절차를 연결한 edge(객관적 사건 순서로 확정한 것이 아님).
- condition: 미확정 identity(ID0x)에 기대는 edge.
"""

ENV_NODES = [
    dict(node_id="ENV01", env_id="E001", title="1793-01-22 호서 전염병 사망자 치계·구료 단속", t_min=122, t_max=122),
    dict(node_id="ENV02", env_id="E002", title="1793-01-22 호서 기근 구휼 한창", t_min=122, t_max=122),
    dict(node_id="ENV03", env_id="E003", title="1793-04-10 호서·영남 전염병 창궐(여제)", t_min=410, t_max=410),
    dict(node_id="ENV04", env_id="E004", title="1793-05-12 경외 전염병 옥수 치료 명", t_min=512, t_max=512),
]

EDGE_TYPES = {
    "TEMPORAL_BEFORE", "PROCEDURAL_NEXT", "INFORMATION_FLOW", "ORDER_TO_ACTION", "REVIEW_OF",
    "REVISES", "CONTRADICTS_AT_CLAIM_LEVEL", "RESPONSIBILITY_LINK", "CONTEXT_SUPPORTS",
}
BASES = {"SOURCE_DIRECT", "TEMPORAL", "PROCEDURAL", "INFORMATION_FLOW",
         "INSTITUTIONAL_COMPATIBILITY", "ENVIRONMENTAL_CONTEXT"}


def E(edge_id, src, dst, etype, basis, status, supporting, rationale,
      claim_level=False, condition="", caution=""):
    return dict(edge_id=edge_id, src=src, dst=dst, edge_type=etype, basis=basis, status=status,
                supporting=supporting, claim_level=claim_level, condition=condition,
                rationale=rationale, caution=caution)


EDGES = [
    # ---------- 관계 → 도난 → 병영 2월 (진술 속 시간; claim-level) ----------
    E("OE001", "EP01", "EP02", "TEMPORAL_BEFORE", "TEMPORAL", "DERIVED", "CF002|CF004",
      "명업 진술상 힐책(2월 초순)이 2월 22일 밤 도적 전언보다 앞선다.", claim_level=True,
      caution="시간 선후일 뿐 원인 관계가 아님."),
    E("OE002", "EP02", "EP03", "TEMPORAL_BEFORE", "TEMPORAL", "DERIVED", "CF004|CF006",
      "CF006 chronology '도난 신고 이후'.", claim_level=True),
    E("OE003", "EP02", "EP04", "TEMPORAL_BEFORE", "TEMPORAL", "DERIVED", "CF004|CF007",
      "2/22 밤 → 2/28 밤 (서로 다른 진술자의 명시 날짜).", claim_level=True,
      caution="소장·체포령(EP03)과 2/28 출동 사이 연결은 미기록 → G01."),
    E("OE004", "EP04", "EP05", "ORDER_TO_ACTION", "SOURCE_DIRECT|TEMPORAL", "DERIVED", "CF008|CF011|CF012",
      "같은 이진욱 진술 흐름에서 덕평 출동 지시(2/28) 뒤 2/29 장교 일행의 현장 체포 활동이 이어진다.", claim_level=True,
      caution="실행이 확인되는 것은 출동 부분뿐이다. 변지돌·정원돌 체포 지시는 실행되지 않음(변지돌 기체포, 정원돌 미기록). "
              "체포 대상이 자미덕으로 바뀐 경위는 기록되지 않았다."),
    E("OE005", "EP05", "EP06", "PROCEDURAL_NEXT", "TEMPORAL", "DERIVED", "CF012|CF013",
      "CF013 chronology '자미덕 체포 뒤': 병영 압송·신문·구류.", claim_level=True,
      caution="두 진술(이진욱·자미덕)이 같은 체포 장면을 가리키는지는 확정하지 않는다."),
    E("OE006", "EP06", "EP07", "PROCEDURAL_NEXT", "TEMPORAL", "DERIVED", "CF015|CF016|CF017",
      "CF016 chronology '구류 중/그 후', CF017 '대질 때'.", claim_level=True),
    E("OE007", "EP07", "EP12", "CONTRADICTS_AT_CLAIM_LEVEL", "SOURCE_DIRECT", "DERIVED", "CF017|CF018",
      "자미덕: 한 비장의 지휘에 따라 거짓으로 꾸며 말함 ↔ 한재욱: 자미덕을 은밀히 사주한 일 없음.",
      claim_level=True, condition="ID02",
      caution="충돌은 '한 비장=한재욱'(미확정)일 때만 성립한다. 한재욱의 부인 범위는 '은밀한 사주'에 한정되므로 PARTIAL 충돌이다."),
    # ---------- 3월 4일 ----------
    E("OE008", "EP09", "EP11", "ORDER_TO_ACTION", "SOURCE_DIRECT", "OBSERVED", "CF021|CF023",
      "CF023 '병사의 분부에 따라' — 지시와 실행의 연결이 원문에 있다.", claim_level=True),
    E("OE009", "EP09", "EP10", "PROCEDURAL_NEXT", "SOURCE_DIRECT|TEMPORAL", "DERIVED", "CF021|CF024",
      "조계완은 '김명신을 잡으러 가는 길에' 구순 집에 들렀다. 체포 임무가 먼저 주어져 있었음을 전제로 한다.", claim_level=True,
      caution="조계완이 3/4 장교 일행의 일원인지는 ID08로 미확정."),
    E("OE010", "EP10", "EP11", "TEMPORAL_BEFORE", "SOURCE_DIRECT", "DERIVED", "CF024|CF023",
      "'잡으러 가는 길에' → 방문이 체포보다 앞선다.", claim_level=True, condition="ID08"),
    E("OE011", "EP11", "EP13", "PROCEDURAL_NEXT", "PROCEDURAL", "DERIVED", "CF023|CF027",
      "3/4 체포된 김명신 → 충청병영의 달포 이상 구금·조사 → 사망(5/12 보고).",
      caution="CF027은 구금 시작일을 3/4로 주장하지 않는다. 같은 사람에 대한 체포→구금 절차 순서만 연결한다."),
    # ---------- 진술 → 안핵 (정보 흐름) ----------
    *[E(f"OE0{20+i:02d}", ep, "EP23", "INFORMATION_FLOW", "SOURCE_DIRECT", "DERIVED", f"{cf}|CF037",
        "SRC3_006 공초는 홍대협의 공주목 신문(CF037)을 통해 기록되어 복명에 실렸다.",
        caution="진술 내용의 진위가 아니라 '진술이 안핵 기록에 들어갔다'는 정보 흐름이다.")
      for i, (ep, cf) in enumerate([
          ("EP01", "CF001"), ("EP02", "CF004"), ("EP03", "CF006"), ("EP04", "CF007"),
          ("EP05", "CF011"), ("EP06", "CF013"), ("EP07", "CF016"), ("EP08", "CF020"),
          ("EP09", "CF021"), ("EP10", "CF024"), ("EP11", "CF023"), ("EP12", "CF018")])],
    E("OE013", "EP02", "EP24", "CONTRADICTS_AT_CLAIM_LEVEL", "SOURCE_DIRECT", "DERIVED", "CF005|CF038",
      "중첩 진술의 '도적 30여 명·횃불' ↔ 홍대협 '큰 화적 사건이 아니라 보통 좀도둑 수준'.", claim_level=True,
      caution="도난 존재 자체는 두 쪽 모두 인정한다. 충돌은 규모에 관한 것이다."),
    # ---------- 5월 판단 ----------
    E("OE040", "EP13", "EP15", "REVIEW_OF", "SOURCE_DIRECT", "DERIVED", "CF027|CF030",
      "CF030 '당시 장계와 조사에 따라' 도난 부재 방향을 받아들임.", condition="ID09",
      caution="CF027 자체는 '확실한 장물 없음'만 보고하고 '도난 없음'을 직접 주장하지는 않는다."),
    E("OE041", "EP15", "EP16", "PROCEDURAL_NEXT", "SOURCE_DIRECT|TEMPORAL", "DERIVED", "CF030|CF031",
      "같은 날 같은 기사(SRC3_001)의 판단 뒤 명령.",
      caution="판단이 명령의 사유라는 문장은 confirmed set에 없다. 절차 순서만 연결한다."),
    E("OE042", "EP16", "EP19", "TEMPORAL_BEFORE", "TEMPORAL", "DERIVED", "CF031|CF034",
      "5/12 의금부 구금 명 → 5/27 의금부 엄수·반복 신문 명."),
    E("OE043", "EP17", "EP18", "REVIEW_OF", "SOURCE_DIRECT", "OBSERVED", "CF032|CF033",
      "CF033: 정조가 이조원 서계의 조사 방식을 문제 삼음."),
    E("OE044", "EP17", "EP19", "PROCEDURAL_NEXT", "SOURCE_DIRECT", "DERIVED", "CF032|CF034",
      "CF034 출처 SRC3_002 제목 '이조원이 구순 사건을 아뢰고 엄핵을 청함'.",
      caution="CF032(SRC3_003)와 CF034(SRC3_002)는 같은 날 다른 기록이다. 기록을 병합하지 않는다."),
    E("OE045", "EP18", "EP20", "TEMPORAL_BEFORE", "TEMPORAL", "DERIVED", "CF033|CF035",
      "5/27 이조원 비판 → 5/28 홍대협 차하.", caution="동기 연결은 사료에 없음 → G08."),
    E("OE046", "EP20", "EP23", "ORDER_TO_ACTION", "SOURCE_DIRECT|PROCEDURAL", "DERIVED", "CF035|CF037",
      "'사건을 자세히 조사해 오라'·안핵어사 차하 → 공주목 신문·안핵어사 복명(같은 인물, 같은 직함)."),
    E("OE047", "EP21", "EP22", "REVIEW_OF", "SOURCE_DIRECT", "OBSERVED", "CF029|CF036",
      "CF036: 윤노동 별단에 따른 처리 보류."),
    E("OE048", "EP22", "EP23", "PROCEDURAL_NEXT", "SOURCE_DIRECT", "OBSERVED", "CF036|CF037",
      "CF036 '홍대협의 안핵 복명 전까지' 보류 → 복명."),
    # ---------- 6월 13일 안핵 결과 ----------
    E("OE050", "EP23", "EP24", "PROCEDURAL_NEXT", "SOURCE_DIRECT", "DERIVED", "CF037|CF038", "복명 속 도난 판단."),
    E("OE051", "EP23", "EP26", "PROCEDURAL_NEXT", "SOURCE_DIRECT", "DERIVED", "CF037|CF040", "복명 속 사인 평가."),
    E("OE052", "EP23", "EP31", "PROCEDURAL_NEXT", "SOURCE_DIRECT", "DERIVED", "CF037|CF045", "복명 속 지세 호칭 조사 결과."),
    # 판단 변화(5월 → 6월) 보존
    E("OE053", "EP15", "EP24", "CONTRADICTS_AT_CLAIM_LEVEL", "SOURCE_DIRECT", "DERIVED", "CF030|CF038",
      "5/12 '도난 자체가 없었다는 방향' ↔ 6/13 홍대협 '약간의 실제 도난'."),
    E("OE054", "EP17", "EP24", "CONTRADICTS_AT_CLAIM_LEVEL", "SOURCE_DIRECT", "DERIVED", "CF032|CF038",
      "5/27 이조원 '도난이 없었다는 방향' ↔ 6/13 홍대협 '약간의 실제 도난'."),
    E("OE055", "EP24", "EP25", "REVIEW_OF", "SOURCE_DIRECT", "DERIVED", "CF038|CF039",
      "같은 복명 기사에서 정조가 안핵 판단을 검토해 최종 판단."),
    E("OE056", "EP15", "EP25", "REVISES", "SOURCE_DIRECT|TEMPORAL", "DERIVED", "CF030|CF039",
      "같은 주체(정조)의 도난 판단: 5/12 부재 방향 → 6/13 실재.",
      caution="최종 판단만 남기지 않는다. 두 판단 node를 모두 유지한다."),
    # ---------- Branch A: biological / death-cause ----------
    E("OE060", "EP13", "EP26", "REVIEW_OF", "PROCEDURAL", "DERIVED", "CF027|CF035|CF040",
      "5/12 장계는 사인 없이 사망만 보고 → 안핵어사(사건 자세히 조사 명)가 사인을 질병으로 평가."),
    E("OE061", "EP26", "EP27", "REVIEW_OF", "SOURCE_DIRECT", "DERIVED", "CF040",
      "홍대협 '질병' → 정조 '부처가 전염병'. 대상이 부처로, 병명이 전염병으로 구체화된다."),
    E("OE062", "EP13", "EP27", "CONTRADICTS_AT_CLAIM_LEVEL", "SOURCE_DIRECT", "DERIVED", "CF027|CF041",
      "5/12 장계 '구금·조사' ↔ 6/13 정조 '평범한 신문도 받지 않았다'.",
      caution="PARTIAL_TENSION: '조사'가 곧 '신문'이라고 확정할 수 없다. CF028의 '무고한 평민들 모진 형벌'은 김명신 포함 여부가 "
              "열린 집합이므로 충돌 근거로 쓰지 않는다."),
    E("OE063", "EP27", "EP28", "CONTEXT_SUPPORTS", "SOURCE_DIRECT", "DERIVED", "CF040|CF041|CF042",
      "같은 날 정조 판단 안에서 전염병 사망·무장형 판단과 '직접 인과 불확실' 판단이 함께 놓인다.",
      caution="앞 판단이 뒤 판단의 사유라는 문장은 confirmed set에 없다. 양립·맥락 관계로만 둔다."),
    # ---------- Branch B: procedural / responsibility (구순) ----------
    E("OE070", "EP01", "EP29", "RESPONSIBILITY_LINK", "SOURCE_DIRECT", "DERIVED", "CF043|CF002|CF003",
      "정조 판단 '사적인 감정을 품고 갈등을 일으켰고' ↔ 명업 진술의 힐책·왕래 단절.",
      caution="CF043은 박거사 일을 직접 언급하지 않는다. 판단 속 '갈등'을 EP01과 대응시킨 것은 DERIVED다."),
    E("OE071", "EP08", "EP29", "RESPONSIBILITY_LINK", "SOURCE_DIRECT", "DERIVED", "CF043|CF020",
      "정조 판단 '병영의 염탐 담당자에게 김명신의 성명을 적어 주었으며' ↔ 유제희 진술.",
      condition="ID05|ID06",
      caution="claim-level 차이: 정조는 '구순이 적어 주었다', 유제희는 '구순이 말했고 자신이 기록했다'. 두 행위를 합치지 않는다."),
    E("OE072", "EP11", "EP29", "RESPONSIBILITY_LINK", "SOURCE_DIRECT", "DERIVED", "CF043|CF023",
      "정조 판단의 '횡액' ↔ 3/4 체포.", caution="'횡액'을 체포·구금과 대응시킨 것은 해석이다."),
    E("OE073", "EP13", "EP29", "RESPONSIBILITY_LINK", "SOURCE_DIRECT", "DERIVED", "CF043|CF027",
      "정조 판단의 '원통하게 죽는 결과' ↔ 구금 뒤 사망 보고.",
      caution="책임 귀속이며 직접 사인 주장이 아니다(EP28 참조)."),
    E("OE074", "EP29", "EP33", "PROCEDURAL_NEXT", "SOURCE_DIRECT", "DERIVED", "CF043|CF046",
      "같은 기사에서 책임 판단 뒤 정배 처분.", caution="처분 사유 문장(V3P0147)은 confirmed set 밖이다."),
    # ---------- Branch B': 병영 지휘 → 이광섭 책임 ----------
    E("OE080", "EP04", "EP30", "RESPONSIBILITY_LINK", "SOURCE_DIRECT", "DERIVED", "CF010|CF044",
      "정조 비판 '철퇴 네 개를 만들게 했으며' ↔ 이진욱 진술 '한재욱이 철편 네 개를 만들어 주었다'.",
      condition="ID07",
      caution="행위 층위 차이(제작 지시 vs 제작·지급). 모순으로도 동일 행위로도 확정하지 않는다."),
    E("OE081", "EP09", "EP30", "RESPONSIBILITY_LINK", "SOURCE_DIRECT", "DERIVED", "CF021|CF044",
      "3/4 '병사'의 체포 지시 ↔ 정조의 이광섭 지휘 책임 판단.", condition="ID01",
      caution="병사=이광섭이 성립할 때만 직접 대응한다."),
    E("OE082", "EP14", "EP30", "REVIEW_OF", "PROCEDURAL", "DERIVED", "CF025|CF026|CF044",
      "5/12 이형원의 이광섭·이문협 평가 → 6/13 정조의 이광섭 책임 재평가.",
      caution="'비장에게 맡김'은 5/12에는 이문협, 6/13에는 이광섭에 대한 비판으로 나온다. 주체를 합치지 않는다."),
    E("OE083", "EP29", "EP30", "RESPONSIBILITY_LINK", "SOURCE_DIRECT", "DERIVED", "CF043|CF044",
      "CF044 '구순과 이광섭의 책임이 크게 다르지 않다' — 두 책임 판단의 비교."),
    E("OE084", "EP30", "EP34", "PROCEDURAL_NEXT", "SOURCE_DIRECT", "DERIVED", "CF044|CF047", "책임 판단 뒤 유배 처분."),
    # ---------- 지세 호칭 ----------
    E("OE090", "EP02", "EP31", "REVIEW_OF", "SOURCE_DIRECT", "DERIVED", "CF005|CF045",
      "중첩 진술의 '지세대감 자칭' → 홍대협 기원 미확정.", claim_level=True),
    E("OE091", "EP31", "EP32", "REVIEW_OF", "SOURCE_DIRECT", "DERIVED", "CF045",
      "홍대협 미확정 → 정조의 날조 죄 불인정."),
    # ---------- 처분 ----------
    E("OE095", "EP23", "EP35", "PROCEDURAL_NEXT", "SOURCE_DIRECT", "DERIVED", "CF037|CF048",
      "안핵 복명 뒤 처분.", caution="한가 처분의 근거 행위는 미기록 → G09."),
    E("OE096", "EP23", "EP36", "PROCEDURAL_NEXT", "SOURCE_DIRECT", "DERIVED", "CF037|CF049",
      "안핵 복명 뒤 처분.", caution="파직 사유는 미기록."),
    E("OE097", "EP36", "EP37", "REVISES", "TEMPORAL|SOURCE_DIRECT", "DERIVED", "CF049|CF050",
      "6/13 파직 → 6/16 유임(같은 인물의 관직 상태 변경).", caution="사유 미기록 → G10. 6/13 처분 자체를 지우지 않는다."),
    E("OE098", "EP25", "EP36", "TEMPORAL_BEFORE", "TEMPORAL", "DERIVED", "CF039|CF049",
      "같은 날 최종 도난 판단과 이형원 파직.",
      caution="최종 판단(도난 실재)이 5/12 장계와 어긋난다는 점이 파직 사유인지는 confirmed set에 없다 → G10."),
    # ---------- 환경 context (CONTEXT_SUPPORTS only, 판단/보고 node로만) ----------
    E("OE100", "ENV01", "EP26", "CONTEXT_SUPPORTS", "ENVIRONMENTAL_CONTEXT", "DERIVED", "E001|CF040",
      "1월 호서 전염병 사망 치계 — 질병 사망 평가와 시대적으로 부합."),
    E("OE101", "ENV03", "EP26", "CONTEXT_SUPPORTS", "ENVIRONMENTAL_CONTEXT", "DERIVED", "E003|CF040",
      "4월 호서 전염병 창궐 — 구금(3/4~)·사망(5/12 이전) 기간과 겹치는 지역 환경."),
    E("OE102", "ENV01", "EP27", "CONTEXT_SUPPORTS", "ENVIRONMENTAL_CONTEXT", "DERIVED", "E001|CF040",
      "정조의 '부처 전염병 사망' 판단과 부합하는 지역 환경."),
    E("OE103", "ENV03", "EP27", "CONTEXT_SUPPORTS", "ENVIRONMENTAL_CONTEXT", "DERIVED", "E003|CF040",
      "전염병 지속 — 정조 판단과 부합."),
    E("OE104", "ENV04", "EP27", "CONTEXT_SUPPORTS", "ENVIRONMENTAL_CONTEXT", "DERIVED", "E004|CF040",
      "5/12 옥수 전염병 치료 정책 — 옥중 전염병이 조정의 현안이었다는 custody-health context.",
      caution="정책일(5/12)은 김명신 사망 보고와 같은 날이고 사망 이후다. 김명신 처우에 영향을 준 것으로 연결하지 않는다."),
    E("OE105", "ENV02", "EP27", "CONTEXT_SUPPORTS", "ENVIRONMENTAL_CONTEXT", "DERIVED", "E002|CF040",
      "기근·구휼 — 영양·행정 부담이라는 거시 맥락(약함).", caution="직접 사인으로 쓰지 않는다(E002 notes)."),
    E("OE106", "ENV01", "EP21", "CONTEXT_SUPPORTS", "ENVIRONMENTAL_CONTEXT", "DERIVED", "E001|CF029",
      "윤노동 별단 '보수·구금 중 병들어 죽었다'는 보고와 부합하는 환경."),
    E("OE107", "ENV03", "EP21", "CONTEXT_SUPPORTS", "ENVIRONMENTAL_CONTEXT", "DERIVED", "E003|CF029",
      "윤노동 보고와 부합하는 전염병 지속 환경."),
]

# ---------------------------------------------------------------------------
# 제도·규범 피쳐 링크 (compatibility layer; creates_event는 항상 NO)
# dimension: legal_available | jurisdictionally_possible | role_compatible |
#            procedure_available | review_available | information_flow_compatible
# assessment: COMPATIBLE | COMPATIBLE_WITH_CAVEAT | LOW | UNDETERMINED
# ---------------------------------------------------------------------------

def L(target, fid, dim, assess, why):
    return dict(target_id=target, feature_id=fid, dimension=dim, assessment=assess, rationale=why)


FEATURE_LINKS = [
    L("EP03", "F010", "jurisdictionally_possible", "COMPATIBLE_WITH_CAVEAT",
      "도적 사건에 진영장·수령 겸임 토포사가 개입할 수 있다. 소장 접수 기관은 미기록이다."),
    L("EP03", "F005", "procedure_available", "COMPATIBLE_WITH_CAVEAT", "군현 수령 경로도 제도상 가능하다. 실제 경로는 미확정."),
    L("EP04", "F007", "role_compatible", "COMPATIBLE", "병마절도사 지휘 아래 병영 장교 출동은 제도상 가능하다."),
    L("EP04", "F008", "procedure_available", "COMPATIBLE", "병영 내부 명령·집행 경로가 존재한다."),
    L("EP04", "F009", "role_compatible", "COMPATIBLE_WITH_CAVEAT",
      "비장청 호출과 비장의 실무 지휘는 막료 관행과 부합한다. 한재욱의 직함은 이 episode에 명시되어 있지 않다."),
    L("EP04", "F002", "legal_available", "UNDETERMINED",
      "흠휼전칙은 형구 규격을 정하지만, pack에는 철편의 지위를 판정할 정보가 없다. 정조는 철퇴를 과도하다고 비판했다(CF044)."),
    L("EP05", "F010", "jurisdictionally_possible", "COMPATIBLE_WITH_CAVEAT",
      "공주진의 변지돌 체포는 진·토포 경로와 양립한다. 경위는 미기록이다."),
    L("EP06", "F004", "legal_available", "UNDETERMINED", "구금 도구 기준은 있으나 자미덕의 구류 방식(다모방) 판정 자료가 없다."),
    L("EP06", "F009", "role_compatible", "COMPATIBLE_WITH_CAVEAT", "비장청 공간 사용은 막료 실무와 부합한다."),
    L("EP07", "F002", "legal_available", "LOW",
      "석방을 조건으로 특정 진술을 요구하는 것을 허용하는 제도 피쳐는 pack에 없다. 주장된 행위의 합법성은 낮다."),
    L("EP07", "F009", "role_compatible", "COMPATIBLE", "비장이 구류자를 다루는 실무 위치에 있을 수 있다."),
    L("EP08", "F008", "role_compatible", "COMPATIBLE_WITH_CAVEAT", "병영 소속 인원의 탐문은 병영 체계와 양립한다. 유제희의 직함은 confirmed set에 없다."),
    L("EP08", "F020", "information_flow_compatible", "COMPATIBLE_WITH_CAVEAT",
      "'기록해 올렸다'는 상향 문서 보고 구조와 부합한다. 수신자는 미기록이다."),
    L("EP09", "F007", "role_compatible", "COMPATIBLE", "병사(兵使)가 장교에게 체포를 지시하는 것은 도 단위 군사지휘와 양립한다."),
    L("EP09", "F010", "jurisdictionally_possible", "COMPATIBLE_WITH_CAVEAT", "도적 사건 체포 관할과 양립한다. 양반(생원) 체포의 특별 요건은 pack에 없다."),
    L("EP10", "F020", "information_flow_compatible", "LOW",
      "구순(전 부사)→병사 서찰은 공식 보고 경로(장계·서계)가 아니다. 공식 지휘 명령으로서는 LOW이고, 사적 정보 전달로서만 가능하다."),
    L("EP10", "F007", "role_compatible", "LOW", "구순에게 병영 장교를 지휘할 공식 권한은 확인되지 않는다."),
    L("EP11", "F008", "procedure_available", "COMPATIBLE", "병사 분부에 따른 장교 일행의 체포 집행 경로가 존재한다."),
    L("EP12", "F014", "review_available", "COMPATIBLE", "안핵어사 공초는 독립 재조사 경로다."),
    L("EP13", "F006", "information_flow_compatible", "COMPATIBLE", "관찰사 장계는 중앙 직계 보고 경로다."),
    L("EP13", "F020", "information_flow_compatible", "COMPATIBLE", "장계 문서 보고 구조."),
    L("EP14", "F006", "review_available", "COMPATIBLE", "관찰사의 하급 기관 감독·평가 경로."),
    L("EP15", "F018", "legal_available", "COMPATIBLE", "국왕의 사건별 판단·명령."),
    L("EP16", "F012", "procedure_available", "COMPATIBLE", "의금부의 왕명 기반 구금·신문."),
    L("EP17", "F013", "review_available", "COMPATIBLE", "암행어사의 지방 탐문 보고."),
    L("EP18", "F013", "review_available", "COMPATIBLE_WITH_CAVEAT", "어사 보고에 대한 국왕의 검토·징계. 사목 범위는 사건별 확인이 필요하다(F013 notes)."),
    L("EP19", "F012", "procedure_available", "COMPATIBLE", "의금부 반복 신문."),
    L("EP20", "F014", "review_available", "COMPATIBLE", "안핵어사 차하는 정조대 실제 운용 사례가 있다."),
    L("EP21", "F013", "review_available", "COMPATIBLE", "암행어사 별단."),
    L("EP22", "F017", "review_available", "COMPATIBLE", "비변사의 처분 보류 심의."),
    L("EP23", "F014", "review_available", "COMPATIBLE", "안핵 복명."),
    L("EP23", "F020", "information_flow_compatible", "COMPATIBLE", "복명·서계 구조."),
    L("EP26", "F015", "procedure_available", "COMPATIBLE_WITH_CAVEAT",
      "사인 판단에는 초검·복검 구조가 있다. 실제 검험 시행 여부는 confirmed set에 없다."),
    L("EP26", "F016", "procedure_available", "COMPATIBLE_WITH_CAVEAT", "1792 증수무원록 지침이 같은 시기에 존재한다. 적용 여부는 미기록이다."),
    L("EP27", "F002", "legal_available", "COMPATIBLE", "곤장·신문 여부 판단은 흠휼전칙의 형구 사용 제한과 같은 차원의 쟁점이다."),
    L("EP27", "F003", "legal_available", "COMPATIBLE_WITH_CAVEAT", "군문 중곤 제한(사형죄 한정). 김명신에 대한 형구 사용은 정조가 부정했다."),
    L("EP29", "F018", "legal_available", "COMPATIBLE", "국왕의 책임 판단."),
    L("EP30", "F007", "role_compatible", "COMPATIBLE", "병마절도사 지휘 책임 귀속은 지휘체계와 부합한다."),
    L("EP30", "F009", "role_compatible", "COMPATIBLE", "비장에게 일을 맡긴 것에 대한 비판은 막료 체계를 전제한다."),
    L("EP33", "F001", "legal_available", "COMPATIBLE", "정배는 법전상 형벌 체계 안에 있다."),
    L("EP34", "F001", "legal_available", "COMPATIBLE", "유배."),
    L("EP35", "F006", "jurisdictionally_possible", "COMPATIBLE", "도백(관찰사)이 형장을 집행하도록 한 명은 관찰사 관할과 부합한다."),
    L("EP35", "F002", "legal_available", "COMPATIBLE_WITH_CAVEAT", "형장 세 차례는 형정 규범 안에서 판단할 사항이다. 규격 정보는 pack에 없다."),
    L("EP36", "F018", "legal_available", "COMPATIBLE", "국왕의 파직 명."),
    L("EP37", "F018", "legal_available", "COMPATIBLE", "국왕의 인사 명."),
    # edge 단위 평가
    L("OE008", "F007", "role_compatible", "COMPATIBLE", "병사→장교 체포 명령→실행 경로는 제도상 compatible하다(사용자 예시)."),
    L("OE046", "F014", "procedure_available", "COMPATIBLE", "안핵어사 차하 → 현지 신문 → 복명."),
    L("OE047", "F017", "review_available", "COMPATIBLE", "비변사 보류."),
    L("OE040", "F006", "information_flow_compatible", "COMPATIBLE", "장계 → 국왕 판단."),
]

# 환경 피쳐 → node의 environmental_fit (CONTEXT ONLY)
ENV_FIT_LINKS = [
    L("EP26", "E001", "environmental_fit", "COMPATIBLE", "질병 사망 평가와 호서 전염병 환경이 부합한다. 개인 감염의 증명은 아니다."),
    L("EP26", "E003", "environmental_fit", "COMPATIBLE", "구금 기간에 전염병이 지속되었다."),
    L("EP27", "E001", "environmental_fit", "COMPATIBLE", "전염병 사망 판단과 부합."),
    L("EP27", "E003", "environmental_fit", "COMPATIBLE", "전염병 사망 판단과 부합."),
    L("EP27", "E004", "environmental_fit", "COMPATIBLE_WITH_CAVEAT", "옥수 전염병이 정책 현안이었음. 날짜가 사망 이후라 context로만 쓴다."),
    L("EP27", "E002", "environmental_fit", "COMPATIBLE_WITH_CAVEAT", "기근은 거시 스트레스 맥락이다. 직접 사인이 아니다."),
    L("EP21", "E001", "environmental_fit", "COMPATIBLE", "병사(病死) 보고와 부합."),
    L("EP21", "E003", "environmental_fit", "COMPATIBLE", "병사(病死) 보고와 부합."),
]
