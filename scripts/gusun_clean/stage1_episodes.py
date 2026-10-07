"""STAGE 1 — confirmed sentence → episode grouping.

규칙
- 새로운 사건을 만들지 않는다. 각 episode는 01_confirmed_facts.csv의 행(또는 행의 절)만 묶는다.
- confirmed_statement를 원자 명제로 다시 쪼개지 않는다. 예외는 CF040·CF045 두 건이다.
  한 행 안에 official(홍대협) 판단과 royal(정조) 판단이 함께 있어서 판단 주체 경계에서만
  절로 나눈다. 각 절은 원문 substring이어야 한다(Audit 1이 검사).
- 동일성(병사=이광섭 등)은 IDENTITY_REGISTER에만 기록하고, summary에서 치환하지 않는다.
- summary는 원문 어휘를 유지한다. 해석·주의사항은 caution에 따로 적는다.

시간 표기: 음력 1793년 월*100+일 (예: 2월 22일 = 222). None = 사료에 없음.
"""

# (fact_id, clause) — clause가 None이면 confirmed_statement 전체
EPISODES = [
    # ---------------- 관계 ----------------
    dict(
        episode_id="EP01", title="구순–김명신 관계 변화",
        members=[("CF001", None), ("CF002", None), ("CF003", None)],
        summary="명업은 김명신이 본래 구순과 친숙하여 날마다 왕래했다고 진술했고, "
                "김명신이 박거사 일로 구순에게 편지를 보내 힐책했다고 진술했으며, "
                "그 뒤 구순과 김명신의 왕래가 끊겼다고 진술했다.",
        caution="세 행 모두 명업 진술(NOT_INDEPENDENTLY_VERIFIED). 힐책은 2월 초순, 단절은 그 이후로 "
                "내부 순서를 보존한다. 힐책의 구체 내용(박거사 일)은 더 해석하지 않는다.",
        occurrence_text="1793-02 초순 이전 → 02 초순(힐책) → 02 초순 이후(단절)",
        t_min=201, t_max=210, t_anchor_note="anchor=CF002 힐책(2월 초순)",
        attesting_actor="명업", layer="TESTIMONY", branch="RELATION",
        grouping_rationale="동일 진술자·동일 인물쌍·연속된 관계 변화 단계(사용자 예시와 동일)."),
    # ---------------- 도난 ----------------
    dict(
        episode_id="EP02", title="2월 22일 밤 도적 침입 전언",
        members=[("CF004", None), ("CF005", None)],
        summary="명업은 나복이 2월 22일 밤 도적이 들었다고 자신에게 알렸다고 진술했다. "
                "명업은 나복이 도적 30여 명, 횃불, 지세대감 자칭, 돈과 물품 도난을 말했다고 진술했다.",
        caution="30여 명·횃불·지세대감은 명업이 전한 나복 발언(중첩 진술)의 내용이며 객관적 사실로 확정하지 않음. "
                "episode 인식 수준은 구성원 중 가장 약한 RECORDED_NESTED_TESTIMONY로 둔다.",
        occurrence_text="1793-02-22 밤", t_min=222, t_max=222,
        attesting_actor="명업(나복 발언 전달)", layer="NESTED_TESTIMONY", branch="THEFT",
        grouping_rationale="동일 시점·동일 전언(나복→명업)의 신고 사실과 신고 내용. 혼합 인식 수준은 floor로 처리."),
    dict(
        episode_id="EP03", title="구순의 소장과 체포령",
        members=[("CF006", None)],
        summary="명업은 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다.",
        caution="소장 접수 기관과 체포령 발령 주체는 이 행에 나타나지 않는다. 체포령과 2/28 병영 출동 사이 관계는 미기록(gap).",
        occurrence_text="도난 신고 이후", t_min=222, t_max=None,
        attesting_actor="명업", layer="TESTIMONY", branch="THEFT",
        grouping_rationale="독립된 행정 행위(소장→체포령). 단독 episode."),
    # ---------------- 병영 2월 ----------------
    dict(
        episode_id="EP04", title="2월 28일 밤 병영 출동 준비",
        members=[("CF007", None), ("CF008", None), ("CF009", None), ("CF010", None)],
        summary="이진욱은 2월 28일 밤 병영에서 자신을 비장청으로 불렀다고 진술했고, "
                "한재욱이 자신과 조계완 등에게 덕평으로 가도록 지시했다고 진술했으며, "
                "한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했고, "
                "한재욱이 철편 네 개를 만들어 주었다고 진술했다.",
        caution="모두 이진욱 진술. '조계완 등'은 열린 목록. 철편은 28일 밤~29일 새벽. 한재욱의 지시 위 상위 명령 출처는 "
                "기록되지 않음(gap). 정조 판단(CF044)의 '철퇴 네 개'와 대응 여부는 ID07로 따로 관리한다.",
        occurrence_text="1793-02-28 밤 ~ 29 새벽", t_min=228, t_max=229,
        attesting_actor="이진욱", layer="TESTIMONY", branch="BARRACKS_OPERATION",
        grouping_rationale="동일 시점·동일 기관(병영 비장청)·동일 행위자 집단·동일 절차 단계(출동 준비)."),
    dict(
        episode_id="EP05", title="2월 29일 덕평 체포 활동",
        members=[("CF011", None), ("CF012", None)],
        summary="이진욱은 2월 29일 변지돌이 이미 공주진에서 잡혀간 상태였다고 진술했고, "
                "장교 일행이 재돌의 처 자미덕을 붙잡았다고 진술했다.",
        caution="정원돌 체포 여부는 기록되지 않음. 변지돌을 공주진에서 잡아간 주체·경위는 미기록(gap).",
        occurrence_text="1793-02-29", t_min=229, t_max=229,
        attesting_actor="이진욱", layer="TESTIMONY", branch="BARRACKS_OPERATION",
        grouping_rationale="동일 날짜·동일 진술자·동일 출동의 현장 결과."),
    dict(
        episode_id="EP06", title="자미덕의 병영 압송·신문·구류",
        members=[("CF013", None), ("CF014", None), ("CF015", None)],
        summary="자미덕은 병영 장교에게 붙잡혀 병영으로 끌려갔다고 진술했고, "
                "병영에서 도적 혐의로 한 차례 신문을 받았다고 진술했으며, "
                "신문 뒤 비장청 다모방에 구류되었다고 진술했다.",
        caution="진술자가 자미덕으로 EP05(이진욱)와 다르므로 분리. 두 진술이 같은 체포를 가리키는지는 확정하지 않고 순서만 연결한다.",
        occurrence_text="자미덕 체포 뒤 → 신문 뒤", t_min=229, t_max=None,
        attesting_actor="자미덕", layer="TESTIMONY", branch="BARRACKS_OPERATION",
        grouping_rationale="동일 진술자·연속 절차(압송→신문→구류)."),
    dict(
        episode_id="EP07", title="한 비장의 석방 조건 제시와 대질 시 거짓 진술",
        members=[("CF016", None), ("CF017", None)],
        summary="자미덕은 한 비장이 정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적이라고 말하면 "
                "자신과 남편을 다음 날 석방하겠다고 말했다고 진술했고, 자미덕은 이집거와 대질했으며, "
                "그때 한 비장의 지휘에 따라 거짓으로 꾸며 말했다고 진술했다.",
        caution="'등'이 있으므로 명시된 5명은 닫힌 목록이 아님. 김명신은 명시 명단에 없으나 열린 목록이라 배제도 확정하지 않음. "
                "'거짓으로 꾸며 말했다'는 거짓 지목으로 강화하지 않음(거짓말의 구체 내용 미특정). '한 비장'=한재욱은 ID02로 사용자 확정(RESOLVED)이며, summary는 원문 표면형 '한 비장'을 유지한다. 동일성 확정은 사주 주장이 사실이라는 뜻이 아니다(EP12의 부인과 별개 진술로 유지).",
        occurrence_text="구류 중/그 후 → 대질 때", t_min=229, t_max=None,
        attesting_actor="자미덕", layer="TESTIMONY", branch="BARRACKS_OPERATION",
        grouping_rationale="동일 진술자·동일 행위자(한 비장)·동일 절차 단계(구류 중 회유→대질)."),
    # ---------------- 탐문 ----------------
    dict(
        episode_id="EP08", title="유제희의 현지 탐문과 구순 발언 기록",
        members=[("CF020", None)],
        summary="유제희는 현지 탐문 중 구순이 풍각 김상제도 극히 수상하다고 말했고, "
                "자신이 그 말을 원돌 등의 이름과 함께 기록해 올렸다고 진술했다.",
        caution="'극히 수상하다'는 범인 지목이 아님. 기록한 사람은 유제희 자신(정조 CF043의 '구순이 성명을 적어 주었다'와 "
                "claim-level 차이). 탐문 시점·파견자·기록 수신자는 미기록(gap). 풍각 김상제=김명신은 ID05로 사용자 확정(RESOLVED, 표면형은 유지), "
                "유제희=병영의 염탐 담당자는 ID06로 미확정. '원돌 등'은 열린 목록이며 원돌=정원돌은 ID11로 사용자 확정(RESOLVED, 표면형은 유지).",
        occurrence_text="현지 탐문(날짜 미기록)", t_min=None, t_max=None,
        attesting_actor="유제희", layer="TESTIMONY", branch="SUSPECT_INFORMATION",
        grouping_rationale="독립된 정보 수집 행위. 날짜가 없어 다른 episode와 병합하지 않음."),
    # ---------------- 3월 4일 ----------------
    dict(
        episode_id="EP09", title="3월 4일 병사의 김생원 체포 지시",
        members=[("CF021", None), ("CF022", None)],
        summary="이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했다고 진술했다. "
                "해당 기사에서 풍각 김생원은 김명신, 흥덕 김생원은 김갑득으로 식별된다.",
        caution="공초 문장의 표면 주어는 '병사'. 병사=이광섭은 ID01로 사용자 확정(RESOLVED)이지만 summary는 원문 표면형을 유지한다. 지시 행위 자체는 이진욱 진술로만 확인된다. 김생원 식별(CF022)은 사료의 직접 식별이므로 그대로 둔다.",
        occurrence_text="1793-03-04", t_min=304, t_max=304,
        attesting_actor="이진욱 / 기사 식별", layer="TESTIMONY", branch="BARRACKS_OPERATION",
        grouping_rationale="지시 행위와 지시 대상의 사료 식별은 같은 문장 단위로 묶는다. 실행(EP11)은 분리."),
    dict(
        episode_id="EP10", title="3월 4일 조계완의 구순 집 방문과 서찰",
        members=[("CF024", None)],
        summary="조계완은 김명신을 잡으러 가는 길에 구순 집에 들렀고, 구순이 이제 도적 다스리는 일이 바른 길을 얻었다는 "
                "취지로 말한 뒤 병사에게 전할 서찰 한 장을 건넸다고 진술했다.",
        caution="서찰의 전달 여부와 내용은 기록되지 않음(gap). 조계완이 3/4 '장교 일행'의 일원인지는 ID08로 미확정.",
        occurrence_text="1793-03-04 (체포 가는 길)", t_min=304, t_max=304,
        attesting_actor="조계완", layer="TESTIMONY", branch="SUSPECT_INFORMATION",
        grouping_rationale="진술자·행위(사적 접촉·서찰)가 체포 지시·체포 실행과 달라 분리."),
    dict(
        episode_id="EP11", title="3월 4일 김명신·김갑득 체포",
        members=[("CF023", None)],
        summary="이진욱은 장교 일행이 병사의 분부에 따라 김명신과 김갑득을 잡아왔다고 진술했다.",
        caution="명령(EP09)과 실행을 분리 보존. 체포 뒤 구금 시작일을 이 행이 주장하지는 않는다.",
        occurrence_text="1793-03-04", t_min=304, t_max=304,
        attesting_actor="이진욱", layer="TESTIMONY", branch="BARRACKS_OPERATION",
        grouping_rationale="실행 단계. ORDER_TO_ACTION을 명시적으로 표현하려고 지시와 분리."),
    # ---------------- 반론 공초 ----------------
    dict(
        episode_id="EP12", title="한재욱의 안핵 공초",
        members=[("CF018", None), ("CF019", None)],
        summary="한재욱은 자미덕을 방으로 불러 남은 밥을 준 사실은 인정했지만, 자미덕을 은밀히 사주한 일은 없다고 진술했고, "
                "구순과 평생 모르는 사이라고 진술했다.",
        caution="부인의 범위는 '은밀히 사주'에 한정된다. '어떤 형태의 사주도 없었다'로 넓히지 않는다. 진술 행위 시점은 안핵 공초.",
        occurrence_text="안핵 공초(1793-05-28 차하 ~ 06-13 복명 사이)", t_min=528, t_max=613,
        attesting_actor="한재욱", layer="TESTIMONY", branch="BARRACKS_OPERATION",
        grouping_rationale="동일 진술자·동일 공초 자리의 자기 변호 진술."),
    # ---------------- 5월 12일 ----------------
    dict(
        episode_id="EP13", title="5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고",
        members=[("CF027", None), ("CF028", None)],
        summary="이형원의 5월 12일 장계는 충청병영이 김명신을 달포 이상 구금·조사했으나 확실한 장물을 찾지 못했고, "
                "김명신이 그 뒤 사망했다고 보고했으며, 무고한 평민들이 모진 형벌을 받았다고 보고했다.",
        caution="사망 장소·직접 사인은 이 보고에 없음. '무고한 평민들'은 열린 집합이므로 김명신 포함 여부를 확정하지 않음. "
                "구금 시작일(3/4)은 이 보고가 주장하지 않음.",
        occurrence_text="보고 1793-05-12 (구금·사망은 그 이전)", t_min=512, t_max=512,
        attesting_actor="이형원(충청도 관찰사)", layer="OFFICIAL_REPORT", branch="DETENTION_DEATH",
        grouping_rationale="동일 장계 안의 보고 사항(인식 수준 FACT_OF_OFFICIAL_REPORT 동일)."),
    dict(
        episode_id="EP14", title="5월 12일 이형원의 지휘 계통 평가",
        members=[("CF025", None), ("CF026", None)],
        summary="5월 12일 기사에서 이광섭은 사건의 병사 지휘 책임자로 심리되며, 이형원은 이광섭이 허황한 말을 믿고 "
                "무고한 사람을 잘못 잡았다고 평가했고, 청주 영장 이문협이 수사를 병영 비장에게 전적으로 맡기고 방관했다고 평가했다.",
        caution="보고(EP13)와 인식 수준(OFFICIAL_EVALUATION)이 달라 분리. 이 행의 '병사 지휘 책임자'는 5/12 기사 차원의 식별이다. "
                "3/4 공초의 '병사'=이광섭은 ID01로 사용자 확정(RESOLVED)이다. 이 행의 문구는 바꾸지 않는다.",
        occurrence_text="1793-05-12", t_min=512, t_max=512,
        attesting_actor="이형원", layer="OFFICIAL_EVALUATION", branch="COMMAND_RESPONSIBILITY",
        grouping_rationale="동일 평가자·동일 날짜·지휘 계통(병사·영장) 평가."),
    dict(
        episode_id="EP15", title="5월 12일 정조 1차 판단: 도난 부재 방향",
        members=[("CF030", None)],
        summary="정조는 당시 장계와 조사에 따라 도난 자체가 없었다는 방향을 받아들였다.",
        caution="6/13 최종 판단(EP25)에서 수정된다. 최종 판단으로 덮어쓰지 않고 REVISES로 보존한다.",
        occurrence_text="1793-05-12", t_min=512, t_max=512,
        attesting_actor="정조", layer="ROYAL_JUDGMENT", branch="THEFT_JUDGMENT",
        grouping_rationale="royal judgment. 같은 날의 royal order(EP16)와 분리."),
    dict(
        episode_id="EP16", title="5월 12일 정조 명: 구순 의금부 구금·엄사",
        members=[("CF031", None)],
        summary="정조는 구순을 의금부에 잡아 가두고 엄히 조사하도록 명했다.",
        caution="명령. 실행 경과(의금부 신문 결과)는 confirmed set에 없음.",
        occurrence_text="1793-05-12", t_min=512, t_max=512,
        attesting_actor="정조", layer="ROYAL_ORDER", branch="REINVESTIGATION",
        grouping_rationale="royal order 단독."),
    # ---------------- 5월 27–28일 ----------------
    dict(
        episode_id="EP17", title="5월 27일 암행어사 이조원 보고: 도난 부재 방향",
        members=[("CF032", None)],
        summary="이조원은 구순 사건을 도난이 없었다는 방향으로 보고했다.",
        caution="암행어사 보고. 6/13 판단과 claim-level로 충돌한다.",
        occurrence_text="1793-05-27", t_min=527, t_max=527,
        attesting_actor="이조원(암행어사)", layer="INSPECTOR_REPORT", branch="THEFT_JUDGMENT",
        grouping_rationale="inspector report 단독."),
    dict(
        episode_id="EP18", title="5월 27일 정조의 이조원 비판·파직",
        members=[("CF033", None)],
        summary="정조는 이조원이 중대 사실을 직접 안핵하지 않고 전해 들은 말을 서계에 붙인 점을 문제 삼았고, "
                "이조원을 파직하도록 명했다.",
        caution="판단과 명령이 한 행에 함께 있으나 주체(정조)·대상(이조원)·날짜가 같아 원문 그대로 유지.",
        occurrence_text="1793-05-27", t_min=527, t_max=527,
        attesting_actor="정조", layer="ROYAL_JUDGMENT_AND_ORDER", branch="REVIEW",
        grouping_rationale="원문 행 단위 보존."),
    dict(
        episode_id="EP19", title="5월 27일 정조 명: 구순 의금부 엄수·반복 신문",
        members=[("CF034", None)],
        summary="정조는 구순을 의금부에 엄히 가두고 반복 신문하도록 명했다.",
        caution="5/12 명령(EP16)과 날짜·출처(SRC3_002)가 달라 별도 episode.",
        occurrence_text="1793-05-27", t_min=527, t_max=527,
        attesting_actor="정조", layer="ROYAL_ORDER", branch="REINVESTIGATION",
        grouping_rationale="royal order 단독."),
    dict(
        episode_id="EP20", title="5월 28일 홍대협 공주 안핵어사 차하",
        members=[("CF035", None)],
        summary="정조는 홍대협에게 사건을 자세히 조사해 오라고 명하고 그를 충청도 공주 안핵어사로 차하했다.",
        caution="5/27 이조원 비판과의 동기 연결은 사료에 명시되지 않음(gap).",
        occurrence_text="1793-05-28", t_min=528, t_max=528,
        attesting_actor="정조", layer="ROYAL_ORDER", branch="REVIEW",
        grouping_rationale="royal order 단독."),
    # ---------------- 6월 11일 ----------------
    dict(
        episode_id="EP21", title="6월 11일 윤노동 별단",
        members=[("CF029", None)],
        summary="윤노동의 6월 11일 별단은 김명신이 보수·구금 중 병들어 죽었고, 여러 죄수가 참혹한 형벌을 받았으며, "
                "진정한 장물을 얻지 못했다고 보고했다.",
        caution="'여러 죄수'는 열린 집합. 김명신이 형벌을 받았다는 주장은 이 행에 없음.",
        occurrence_text="보고 1793-06-11", t_min=611, t_max=611,
        attesting_actor="윤노동(암행어사)", layer="INSPECTOR_REPORT", branch="DETENTION_DEATH",
        grouping_rationale="inspector report 단독."),
    dict(
        episode_id="EP22", title="6월 11일 비변사 처리 보류 청·윤허",
        members=[("CF036", None)],
        summary="비변사는 홍대협의 안핵 복명 전까지 윤노동 별단에 따른 처리를 보류할 것을 청했고, 정조는 이를 윤허했다.",
        caution="청과 윤허가 한 행. 같은 절차 단계이므로 유지.",
        occurrence_text="1793-06-11", t_min=611, t_max=611,
        attesting_actor="비변사·정조", layer="COURT_ACTION", branch="REVIEW",
        grouping_rationale="court action 단독."),
    # ---------------- 6월 13일 ----------------
    dict(
        episode_id="EP23", title="6월 13일 홍대협 공주목 신문·복명",
        members=[("CF037", None)],
        summary="홍대협은 공주목에서 관련자들을 차례로 신문한 뒤 호서 안핵어사로 복명하여 편전에서 정조에게 보고했다.",
        caution="SRC3_006의 공초(EP01–EP12)는 이 신문을 통해 기록되었다.",
        occurrence_text="신문(5/28 이후) → 복명 1793-06-13", t_min=528, t_max=613,
        attesting_actor="홍대협(안핵어사)", layer="OFFICIAL_ACTION", branch="REVIEW",
        grouping_rationale="official action 단독."),
    dict(
        episode_id="EP24", title="홍대협 도난 판단: 약간의 실제 도난, 좀도둑 수준",
        members=[("CF038", None)],
        summary="홍대협은 약간의 실제 도난은 있었지만 큰 화적 사건이 아니라 보통 좀도둑 수준이었다고 판단했다.",
        caution="'약간의'를 삭제하지 않음.",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="홍대협", layer="OFFICIAL_FINDING", branch="THEFT_JUDGMENT",
        grouping_rationale="official finding. royal judgment(EP25)와 분리."),
    dict(
        episode_id="EP25", title="정조 최종 도난 판단: 실재",
        members=[("CF039", None)],
        summary="정조는 최종적으로 도난은 실제로 있었다고 판단했다.",
        caution="5/12 판단(EP15)을 지우지 않고 REVISES 관계로 보존.",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="정조", layer="ROYAL_JUDGMENT", branch="THEFT_JUDGMENT",
        grouping_rationale="royal judgment 단독."),
    dict(
        episode_id="EP26", title="홍대협 사인 평가: 질병",
        members=[("CF040", "홍대협은 김명신의 죽음을 질병 때문이라고 평가했고")],
        summary="홍대협은 김명신의 죽음을 질병 때문이라고 평가했다.",
        caution="CF040의 홍대협 절. 정조 절(EP27)과 판단 주체가 달라 분리.",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="홍대협", layer="OFFICIAL_EVALUATION", branch="BIOLOGICAL",
        grouping_rationale="official/royal 경계 분리(사용자 지정 branch A 구조)."),
    dict(
        episode_id="EP27", title="정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음",
        members=[("CF040", "정조는 김명신 부처가 전염병에 걸려 죽은 것으로 판단했다."), ("CF041", None)],
        summary="정조는 김명신 부처가 전염병에 걸려 죽은 것으로 판단했고, 김명신이 곤장을 맞지 않았고 "
                "평범한 신문도 받지 않았다고 판단했다.",
        caution="royal judgment 자체로 보존. 5/12 장계의 '구금·조사'와 긴장이 있다(CF041 notes). 판단 대상이 '부처'(아내 포함)로 넓어진 점을 보존.",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="정조", layer="ROYAL_JUDGMENT", branch="BIOLOGICAL",
        grouping_rationale="동일 주체·동일 날짜·같은 생물학적/신체 처우 쟁점의 royal judgment."),
    dict(
        episode_id="EP28", title="정조: 구순→김명신 직접 사망 인과 불확실",
        members=[("CF042", None)],
        summary="정조는 김명신이 구순 때문에 직접 죽었다는 인과가 십분 확실하다고 할 수 없다고 판단했다.",
        caution="직접 인과에 대한 판단. 절차적 책임 판단(EP29)과 합치지 않는다.",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="정조", layer="ROYAL_JUDGMENT", branch="CAUSATION_BOUNDARY",
        grouping_rationale="branch A/B 경계에 있는 판단이므로 단독."),
    dict(
        episode_id="EP29", title="정조: 구순 책임 연결 판단",
        members=[("CF043", None)],
        summary="정조는 구순이 김명신에게 사적인 감정을 품고 갈등을 일으켰고, 병영의 염탐 담당자에게 김명신의 성명을 "
                "적어 주었으며, 그 과정이 김명신이 횡액을 입고 원통하게 죽는 결과로 이어졌다고 책임을 연결해 판단했다.",
        caution="책임 귀속 사슬(royal judgment)이지 직접 사인이 아님. '병영의 염탐 담당자'=유제희는 ID06로 미확정.",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="정조", layer="ROYAL_JUDGMENT", branch="RESPONSIBILITY",
        grouping_rationale="royal judgment 단독."),
    dict(
        episode_id="EP30", title="정조: 이광섭 책임 판단",
        members=[("CF044", None)],
        summary="정조는 이광섭이 구순 편을 들고, 철퇴 네 개를 만들게 했으며, 아전들의 거짓을 제대로 살피지 않은 채 "
                "비장에게 일을 맡겼다고 비판하고, 김명신 사망 책임에서 구순과 이광섭의 책임이 크게 다르지 않다고 판단했다.",
        caution="'철퇴 네 개'와 이진욱 진술의 '철편 네 개'(EP04) 대응은 ID07. '비장'이 누구인지 특정하지 않음.",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="정조", layer="ROYAL_JUDGMENT", branch="COMMAND_RESPONSIBILITY",
        grouping_rationale="royal judgment 단독."),
    dict(
        episode_id="EP31", title="홍대협: 지세 호칭 기원 미확정",
        members=[("CF045", "홍대협은 여러 차례 신문과 별도 탐문에도 지세 호칭의 기원을 확정하지 못했고")],
        summary="홍대협은 여러 차례 신문과 별도 탐문에도 지세 호칭의 기원을 확정하지 못했다.",
        caution="CF045의 홍대협 절.",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="홍대협", layer="OFFICIAL_FINDING", branch="JISE",
        grouping_rationale="official/royal 경계 분리."),
    dict(
        episode_id="EP32", title="정조: 구순 지세 호칭 날조 죄 불인정",
        members=[("CF045", "정조는 구순이 지세 호칭을 스스로 만들어냈다는 죄는 인정하지 않았다.")],
        summary="정조는 구순이 지세 호칭을 스스로 만들어냈다는 죄는 인정하지 않았다.",
        caution="CF045의 정조 절. '불인정'을 '구순은 지세와 무관'으로 강화하지 않음.",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="정조", layer="ROYAL_JUDGMENT", branch="JISE",
        grouping_rationale="official/royal 경계 분리."),
    # ---------------- 처분 ----------------
    dict(
        episode_id="EP33", title="구순 신지도 정배",
        members=[("CF046", None)],
        summary="정조는 구순을 신지도에 정배했다.",
        caution="", occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="정조", layer="ROYAL_ORDER", branch="DISPOSITION",
        grouping_rationale="처분 대상별로 책임 연결이 달라 분리."),
    dict(
        episode_id="EP34", title="이광섭 영동현 유배",
        members=[("CF047", None)],
        summary="정조는 이광섭을 영동현에 유배했다.",
        caution="", occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="정조", layer="ROYAL_ORDER", branch="DISPOSITION",
        grouping_rationale="처분 대상별 분리."),
    dict(
        episode_id="EP35", title="병영 비장 한가 처분",
        members=[("CF048", None)],
        summary="정조는 병영 비장으로 표기된 한가를 도백이 엄히 세 차례 형장 친 뒤 먼 섬의 종으로 보내도록 명했다.",
        caution="처분문 표면형은 '한가'. 한가=한재욱은 ID03으로 사용자 확정(RESOLVED)이며 summary는 표면형을 유지한다. 처분 근거가 된 행위는 confirmed set에 없음(gap G09).",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="정조", layer="ROYAL_ORDER", branch="DISPOSITION",
        grouping_rationale="처분 대상별 분리."),
    dict(
        episode_id="EP36", title="이형원 파직",
        members=[("CF049", None)],
        summary="정조는 충청도 관찰사 이형원을 파직하도록 명했다.",
        caution="파직 사유는 confirmed set에 명시되지 않음.",
        occurrence_text="1793-06-13", t_min=613, t_max=613,
        attesting_actor="정조", layer="ROYAL_ORDER", branch="DISPOSITION",
        grouping_rationale="처분 대상별 분리."),
    dict(
        episode_id="EP37", title="6월 16일 이형원 유임",
        members=[("CF050", None)],
        summary="정조는 6월 16일 전 충청도 관찰사 이형원을 유임했다.",
        caution="6/13 파직과 별개의 인사 조치. 사유는 미기록(gap).",
        occurrence_text="1793-06-16", t_min=616, t_max=616,
        attesting_actor="정조", layer="ROYAL_ORDER", branch="DISPOSITION",
        grouping_rationale="날짜가 달라 분리."),
]

# 동일성 대장. UNRESOLVED는 episode/edge에서 condition으로만 참조한다.
# RESOLVED는 사용자가 수동 검토에서 확정한 것만 해당한다(resolved_by=USER). 모델이 스스로 확정하지 않는다.
# episode summary는 확정 여부와 관계없이 원문 표면형을 유지한다.
IDENTITY_REGISTER = [
    dict(identity_id="ID01", surface_a="공초의 '병사' (CF021·CF023·CF024)", surface_b="이광섭",
         status="RESOLVED", resolved_by="USER", resolution_basis="사용자 확정: 병사는 병마절도사의 약칭이고, 이 사건에서 충청도 병마절도사로 이광섭이 특정되어 있다(CF025 기사 제목·심리 대상).", context="CF025: 5/12 기사가 이광섭을 사건의 병사 지휘 책임자로 심리(기사 제목: 충청도 병마절도사). "
         "강한 맥락이지만 공초 문장 자체는 '병사'만 씀.", referenced_facts="CF021|CF023|CF024|CF025|CF044|CF047"),
    dict(identity_id="ID02", surface_a="'한 비장' (CF016·CF017)", surface_b="한재욱",
         status="RESOLVED", resolved_by="USER", resolution_basis="사용자 확정: 자미덕 공초의 '한 비장'과 이어지는 한재욱의 공방(CF018: 자미덕을 방으로 불러 남은 밥을 준 사실 인정, 은밀한 사주 부인)이 같은 인물을 가리킨다. 사주 주장과 부인은 서로 다른 진술로 유지한다.", context="CF018: 한재욱이 자미덕을 방으로 불러 밥을 준 사실을 인정. 동일인 확정 문장은 없음.",
         referenced_facts="CF016|CF017|CF018"),
    dict(identity_id="ID03", surface_a="처분문의 '한가' (CF048)", surface_b="한재욱",
         status="RESOLVED", resolved_by="USER", resolution_basis="사용자 확정: 처분문(CF048)의 '병영 비장 한가'는 한재욱이다.", context="CF048 notes: 처분문 표면형은 한가.", referenced_facts="CF048|CF008|CF018"),
    dict(identity_id="ID04", surface_a="'병영의 하급 보조자' (audit-only V3P0026·V3P0027·V3P0124)", surface_b="한재욱",
         status="UNRESOLVED", model_relevance="NONE", manual_decision_required="NO", context="confirmed set 밖(이조원 주장). DAG에서는 사용하지 않음.", referenced_facts=""),
    dict(identity_id="ID05", surface_a="'풍각 김상제' (CF020)", surface_b="김명신",
         status="RESOLVED", resolved_by="USER", resolution_basis="사용자 확정: 같은 '풍각' 지명·호칭 맥락이고 같은 사건의 수사선상에서 등장한다. "
         "'김상제'와 '김생원'은 이름이 아니라 서로 다른 호칭 표현이므로 호칭 차이만으로 별개 인물로 볼 이유가 없다(CF020·CF022).", context="CF022는 '풍각 김생원'=김명신을 직접 식별. 김상제(상주 호칭)와의 동일성은 confirmed 문장에 없음 "
         "(audit V3P0095 object 필드는 김명신).", referenced_facts="CF020|CF022"),
    dict(identity_id="ID06", surface_a="'병영의 염탐 담당자' (CF043)", surface_b="유제희",
         status="UNRESOLVED", context="CF020: 유제희가 현지 탐문 중 구순 발언을 기록해 올림. 정조 판단은 직책 표현만 씀.",
         referenced_facts="CF043|CF020"),
    dict(identity_id="ID07", surface_a="'철편 네 개' (CF010, 이진욱: 한재욱이 만들어 줌)",
         surface_b="'철퇴 네 개' (CF044, 정조: 이광섭이 만들게 함)",
         status="UNRESOLVED", context="개수·사건이 같아 대응 가능성이 높음. 행위 층위(제작·지급 vs 제작 지시)가 다르므로 모순으로도 동일 행위로도 확정하지 않음.",
         referenced_facts="CF010|CF044"),
    dict(identity_id="ID08", surface_a="3/4 '장교 일행' (CF023)", surface_b="조계완 포함 여부 (CF024)",
         status="UNRESOLVED", context="CF008: 2/28 지시 대상에 '조계완 등' 포함. 3/4 구성원은 미기록.",
         referenced_facts="CF023|CF024|CF008"),
    dict(identity_id="ID09", surface_a="CF030 '당시 장계'", surface_b="이형원 5/12 장계(CF027)",
         status="ACCEPTED_BY_PROVENANCE", context="같은 기사 SRC3_001(제목: 이형원 장계 및 정조 처분).",
         referenced_facts="CF030|CF027"),
    dict(identity_id="ID10", surface_a="풍각 김생원 / 흥덕 김생원", surface_b="김명신 / 김갑득",
         status="DOCUMENTED", context="CF022 DOCUMENTED_SOURCE_IDENTIFICATION.", referenced_facts="CF022"),
    dict(identity_id="ID11", surface_a="'원돌' (CF020 '원돌 등의 이름')", surface_b="정원돌 (CF009·CF016)",
         status="RESOLVED", resolved_by="USER", resolution_basis="사용자 확정: 유제희 기록의 '원돌'(CF020)은 정원돌(CF009·CF016)이다.", context="이름 일부가 겹치지만 confirmed 문장은 같은 사람이라고 하지 않는다.",
         referenced_facts="CF020|CF009|CF016"),
]

# 인식 수준 floor 계산용 순위(낮을수록 약함). 서로 다른 종류의 기록을 우열로 매기려는 것이 아니다.
# 혼합 episode가 더 강한 지위로 둔갑하지 않게 하는 용도다.
EPISTEMIC_RANK = {
    "RECORDED_NESTED_TESTIMONY": 0,
    "RECORDED_TESTIMONY": 1,
    "DOCUMENTED_OFFICIAL_EVALUATION": 2,
    "DOCUMENTED_OFFICIAL_REPORT": 2,
    "DOCUMENTED_INSPECTOR_REPORT": 2,
    "DOCUMENTED_OFFICIAL_FINDING": 3,
    "DOCUMENTED_OFFICIAL_AND_ROYAL_JUDGMENT": 3,
    "DOCUMENTED_ROYAL_JUDGMENT": 3,
    "DOCUMENTED_ROYAL_JUDGMENT_AND_ORDER": 4,
    "DOCUMENTED_ROYAL_ORDER": 4,
    "DOCUMENTED_COURT_ACTION": 4,
    "DOCUMENTED_OFFICIAL_ACTION": 4,
    "DOCUMENTED_SOURCE_IDENTIFICATION": 4,
}


# 사료 자체의 모호성 때문에 남기는 동일성의 사유. identity_register.csv와 audit UNRESOLVED 항목에 그대로 쓴다.
UNRESOLVED_REASONS = {
    "ID01": "공초 문장의 주어는 '병사'라는 직함뿐이다. 이광섭을 병사로 다루는 것은 5/12 기사(CF025)이고, 3/4 공초가 같은 사람을 가리킨다고 쓴 문장은 없다.",
    "ID02": "자미덕은 성(한)과 직함(비장)만 말했다. 한재욱 공초(CF018)는 자미덕을 방으로 부른 사실을 인정하지만 자신이 '한 비장'이라고 하지는 않는다.",
    "ID03": "처분문(CF048)은 '한가'라는 성 표기만 쓴다. 이름과 직함을 함께 적은 처분 문장이 없다.",
    "ID04": "'하급 보조자'는 이조원 보고(05, audit-only)에만 나오며 confirmed set에는 없다.",
    "ID05": "'풍각 김상제'(상주 호칭)와 '풍각 김생원'(=김명신, CF022)은 다른 호칭이다. 둘을 같은 사람으로 적은 confirmed 문장이 없다.",
    "ID06": "정조 판단(CF043)은 직책 표현('병영의 염탐 담당자')만 쓰고 이름을 적지 않았다.",
    "ID07": "개수(네 개)와 사건은 같지만 물건 이름(철편/철퇴)과 행위 층위(제작·지급/제작 지시)가 다르다.",
    "ID08": "3/4 '장교 일행'의 구성원은 기록되지 않았다.",
    "ID11": "'원돌'과 '정원돌'은 이름 일부만 겹친다. 같은 사람이라는 문장이 없다.",
}
UNRESOLVED_REASONS["ID04"] = ("audit-only 자료(05, 이조원 주장)에만 있고 인명이 직접 나오지 않는다. 현재 DAG·후보·world 어디에도 쓰이지 않아 "
                              "결정해도 모델 결과가 바뀌지 않는다(참고용 미해결).")
for _i in IDENTITY_REGISTER:
    _i["unresolved_reason"] = UNRESOLVED_REASONS.get(_i["identity_id"], "") if _i["status"] == "UNRESOLVED" else ""
    _i.setdefault("resolved_by", "")
    _i.setdefault("resolution_basis", "")

RESOLVED_IDS = {i["identity_id"] for i in IDENTITY_REGISTER if i["status"] == "RESOLVED"}
UNRESOLVED_IDS = {i["identity_id"] for i in IDENTITY_REGISTER if i["status"] == "UNRESOLVED"}
