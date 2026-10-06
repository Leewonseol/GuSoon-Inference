"""STAGE 5 — 소수의 narrative world.

- 전수 조합을 만들지 않는다. 설명 축이 서로 다른 world를 직접 골랐다(retained 5 + 기각 대조 1).
- 모든 world는 동결된 observed DAG를 그대로 공유하고, gap마다 latent bridge를 최대 1개 얹는다.
- world의 institutional_fit / environmental_fit / min_grade / n_assumptions는 구성 후보에서 기계적으로 계산한다.
- 서술(narrative)에서 [L]은 LATENT bridge 부분이다. 진술은 '…라고 진술했다'로 남기고, 미확정 동일성은 IDxx로 표시한다.
- SMC / MCMC / posterior sampling을 쓰지 않는다.
"""
from itertools import combinations

SCORE = {"INCOMPATIBLE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
NAME = {v: k for k, v in SCORE.items()}

# 한 world 안에 함께 둘 수 없는 후보 쌍 (서로 다른 gap이지만 내용이 부딪힘)
CONFLICT_PAIRS = [
    ("G03b", "G04b", "둘 다 3/4 지시의 '직접' 계기를 2/29~3/4의 같은 4일 안에 두면서 정보원을 다르게 잡는다"
                     "(유제희 기록 vs 자미덕 대질 진술). 함께 쓰면 시간 가정이 겹치고 '직접 촉발'이 서로를 부정한다."),
    ("G03c", "G04a", "유제희 기록의 경로가 '비장 우회 직접 보고'(G03c)와 '비장 계통 경유'(G04a)로 서로 배타적이다."),
    ("G01a", "G02c", "G01a는 진영이 수사를 병영 비장에게 넘겼다고, G02c는 영장이 출동을 직접 지휘했다고 본다."),
]

# 처음 지정된 world 구성 대비 조정 내역 (근거와 함께)
ADJUSTMENTS = [
    ("W5", "HIGH 후보만 쓰도록 지정됨. 계산 결과 HIGH는 G01a·G06a·G07a·G08a 네 개뿐이다. G02a는 ID07(철편=철퇴)에 기대므로 "
           "grade 규칙 (6)에 따라 MEDIUM이 되어 W5에서 빠졌다."),
    ("W1", "지정 목록 그대로. 다만 G02a·G03a·G04a·G05a·G09a·G11a·G12a·G13a가 MEDIUM이라 world 최저 등급은 MEDIUM이다. "
           "G04b·G05a의 institutional_fit은 '정보 전달 경로' 기준으로 MEDIUM이다(관측 행위의 합법성 LOW는 observed feature link에 남김)."),
    ("W2", "지정 목록 그대로. G03a(2/28 이전 기록)와 G04b(대질 진술 → 3/4 지시)는 시간상 양립한다. "
           "G03b와 G04b는 상충 쌍이라서 G03b 대신 G03a를 유지했다."),
    ("W3", "지정 목록 그대로. G04c가 LOW라 world 최저 등급과 제도 적합이 LOW다(약한 world로 명시)."),
    ("W4", "지정 목록 그대로. G03c가 LOW라 world 최저 등급이 LOW다. G03c는 G04a와 상충하므로 W4는 G04를 비워 둔다."),
    ("W6", "지정 목록 그대로(G06c·G07d·G12b). 모두 contradiction_risk HIGH인 대조 후보라 REJECTED로 둔다."),
]

WORLDS = [
    dict(
        world_id="W1", name="공식 정보 경로 (정조 최종 판단과 정합)",
        latent_bridges=["G01a", "G02a", "G03a", "G04a", "G05a", "G06a", "G07a", "G08a", "G09a", "G11a", "G12a", "G13a"],
        inst_note="사적 서찰(G05a)만 공식 보고 경로가 아니어서 MEDIUM이다. 나머지는 진영·병영·비장·의금부·안핵어사의 제도 경로 안에 있다.",
        env_note="환경은 G06a·G12a의 environmental_fit 평가에만 썼다(E001·E003 전염병 context). 개인 감염 사건을 환경에서 만들지 않았다.",
        main_assumptions=[
            "소장이 청주 진영에 접수되어 병영 비장 쪽으로 넘어감(G01a)",
            "이광섭이 출동·철퇴 제작을 지시하고 한재욱이 전달(G02a, ID07 조건)",
            "유제희 기록이 2/28 이전 한재욱에게, 이후 비장 계통을 거쳐 병사에게 올라감(G03a·G04a)",
            "구순 서찰이 병사에게 전달되어 체포를 지지함(G05a)",
            "김명신은 구금 중 발병해 5/12 이전 사망, 처우는 CF041 판단을 따름(G06a)",
        ],
        main_weaknesses=[
            "bridge 12개로 가장 많이 채운 world다. 추가 가정 합계가 가장 크다.",
            "미확정 동일성 7개(ID01·ID02·ID03·ID05·ID06·ID07·ID11)를 조건으로 깐다. 하나라도 불성립이면 해당 구간이 끊긴다.",
            "유제희 기록이 2/28 이전이었다면 풍각 김생원 체포가 왜 3/4로 늦었는지 설명하지 못한다(G03a).",
            "정조의 '구순이 성명을 적어 주었다'(CF043)와 유제희의 '자신이 기록했다'(CF020)의 claim-level 차이를 해소하지 않은 채 둘 다 쓴다.",
        ],
        contradicted_evidence="직접 충돌하는 confirmed fact 없음. 긴장: CF027('달포 이상 구금·조사') ↔ G06a가 따르는 CF041('평범한 신문도 받지 않았다') — PARTIAL. "
                              "CF018(한재욱의 '은밀한 사주' 부인) ↔ G09a의 회유 근거 — claim-level, ID02 조건부.",
        story_implication="구순의 사적 갈등이 '의혹 정보'로 공식 수사 경로(진영 → 병영 비장 → 병영 지휘)에 들어갔고, 병영은 장물 없이 체포·구금을 진행했다. "
                          "김명신은 구금 중 병으로 죽었다. 정조의 최종 판단(도난 실재, 전염병 사망, 직접 인과 불확실, 그런데도 구순과 이광섭의 책임)과 "
                          "가장 넓게 정합하는 경로지만, 그만큼 가정이 많다.",
        narrative=(
            "명업은 김명신이 2월 초순 박거사 일로 구순에게 편지를 보내 힐책했고 그 뒤 왕래가 끊겼다고 진술했다. 명업은 또 나복이 2월 22일 밤 도적이 들었다고 "
            "알렸고, 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다. "
            "[L] 소장은 청주 진영에 접수되었고 진영은 수사를 병영 비장 쪽에 넘겼다(G01a). "
            "[L] 이광섭이 출동과 철퇴 제작을 지시하고 한재욱이 이를 전달했다. 철퇴와 철편이 같은 물건일 때(ID07)만 성립한다(G02a). "
            "[L] 그보다 앞서 한재욱이 보낸 유제희의 탐문 기록이 한재욱에게 올라가 있었다. 기록 속 원돌이 정원돌이라는 가정(ID11)이 필요하다(G03a). "
            "이진욱은 2월 28일 밤 한재욱이 덕평 출동과 변지돌·정원돌 체포를 지시하고 철편 네 개를 만들어 주었다고 진술했다. "
            "[L] 변지돌은 공주진이 같은 사건으로 먼저 잡아갔다(G11a). "
            "자미덕은 병영에 끌려가 한 차례 신문받고 구류되었으며, 한 비장이 정원돌 등을 큰 도적이라고 말하면 다음 날 석방하겠다고 말했고 대질 때 그 지휘에 따라 거짓으로 꾸며 말했다고 진술했다. "
            "[L] 유제희 기록 속 '풍각 김상제도 극히 수상하다'는 구순의 말이 비장 계통을 거쳐 병사에게 보고되었다. 김상제가 김명신이라는 가정(ID05)이 필요하다(G04a). "
            "이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원(사료 식별: 김명신·김갑득)을 잡아오라고 지시했고 장교 일행이 그 분부에 따라 잡아왔다고 진술했다. "
            "조계완은 잡으러 가는 길에 구순에게서 병사에게 전할 서찰을 받았다고 진술했다. "
            "[L] 그 서찰은 병사에게 전달되었고 체포를 지지하는 내용이었다. 정조 판단의 이광섭과 잇는 것은 병사=이광섭(ID01) 조건이다(G05a). "
            "[L] 김명신은 구금 중 병이 났고 5월 12일 보고 이전에 죽었다(G06a). 윤노동 별단은 김명신이 보수·구금 중 병들어 죽었다고 보고했다. "
            "5월 12일 이형원 장계(달포 이상 구금·조사, 확실한 장물 없음, 사망)를 받은 정조는 도난 자체가 없었다는 방향을 받아들였다. "
            "[L] 그 방향은 장물 미발견에서 나온 추론이었다(G07a). "
            "[L] 의금부에서 구순 신문이 실행되었으나 지세 호칭 문제는 결론이 나지 않았다(G13a). "
            "[L] 정조는 이조원이 직접 안핵하지 않은 점을 문제 삼은 다음 날 홍대협을 안핵어사로 보냈다(G08a). "
            "6월 13일 홍대협은 약간의 실제 도난이 있었으나 보통 좀도둑 수준이라고 판단했고 김명신의 죽음을 질병 때문이라고 평가했다. 정조는 도난 실재, 부처의 전염병 사망, 곤장·평문 없음, "
            "직접 인과는 십분 확실하지 않음을 판단하면서도 구순과 이광섭의 책임이 크게 다르지 않다고 판단했다. "
            "[L] 김명신의 아내도 전염병으로 죽었다(G12a). "
            "[L] 한 비장=한재욱(ID02)과 한가=한재욱(ID03)이 모두 성립한다면, 한가 처분의 근거는 회유·대질 지휘와 출동 운영이다(G09a)."),
    ),
    dict(
        world_id="W2", name="대질 진술 증폭 경로 (구류·회유 진술이 체포를 넓힘)",
        latent_bridges=["G01a", "G02b", "G03a", "G04b", "G06b", "G07c", "G08a", "G09a", "G12a"],
        inst_note="비장의 자체 판단 출동(G02b)과 대질 진술의 보고(G04b)가 MEDIUM이다. 회유 행위 자체의 합법성 LOW(F002)는 observed node EP07에 붙어 있다.",
        env_note="환경은 G06b·G12a의 environmental_fit 평가에만 썼다.",
        main_assumptions=[
            "한재욱이 상위 명령 없이 출동을 지시하고 병영 지휘관은 사후 승인·묵인(G02b)",
            "유제희의 초기 기록이 2/28 이전 한재욱에게 올라감(G03a, ID11 조건)",
            "자미덕의 대질 진술이 3/4 이전 병사에게 보고되어 체포 근거가 됨(G04b)",
            "구금 중 형장 없는 조사 압박 뒤 발병·사망(G06b)",
            "명업 등의 번복 진술이 5월 판단 자료에 들어감(G07c)",
        ],
        main_weaknesses=[
            "G06b는 정조의 CF041 판단('평범한 신문도 받지 않았다')과 긴장한다.",
            "열린 목록 '등'에 풍각 김생원이 들어 있었다는 가정은 05의 윤노동 주장(audit-only)에만 흔적이 있다.",
            "G04b의 시간 창(2/29 자미덕 체포 ~ 3/4 지시)이 4일뿐이다.",
            "한 비장·한가를 한재욱과 잇는 G09a는 ID02·ID03 조건부다.",
        ],
        contradicted_evidence="직접 충돌하는 confirmed fact 없음. 긴장: CF041(royal judgment: 평범한 신문 없음) ↔ G06b. "
                              "CF018(은밀한 사주 부인) ↔ G04b·G09a — claim-level, ID02 조건부.",
        story_implication="사건의 추진력을 구류·회유·대질 진술(자미덕의 진술)에서 찾는다. 유제희의 초기 명단이 자미덕의 대질 진술로 넓어져 3/4 김생원 체포로 "
                          "이어지고, 5월의 도난 부재 방향은 구순 집 사람들의 번복 진술에서 나온다. 정조의 처우 판단(CF041)과는 긴장 관계에 있다.",
        narrative=(
            "명업은 김명신과 구순의 왕래가 힐책 뒤 끊겼고, 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다. "
            "[L] 소장은 청주 진영에 접수되었고 진영은 수사를 병영 비장 쪽에 넘겼다(G01a). "
            "[L] 한재욱은 위에서 구체적 명령을 받지 않고 2월 28일 출동을 지시했고 병영 지휘관은 나중에 묵인했다(G02b). "
            "[L] 유제희의 초기 기록이 2월 28일 이전 한재욱에게 올라가 있었다. 원돌이 정원돌이라는 가정(ID11)이 필요하다(G03a). "
            "이진욱은 한재욱이 변지돌·정원돌 체포를 지시했고, 2월 29일 변지돌은 이미 공주진에 잡혀가 장교 일행이 자미덕을 붙잡았다고 진술했다. "
            "자미덕은 한 비장이 정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적이라고 말하면 석방하겠다고 했고, 대질 때 그 지휘에 따라 거짓으로 꾸며 말했다고 진술했다. "
            "한재욱은 자미덕에게 남은 밥을 준 사실은 인정했지만 은밀히 사주한 일은 없다고 진술했다. 두 진술의 충돌은 한 비장=한재욱(ID02)일 때만 성립한다. "
            "[L] 자미덕의 대질 진술이 3월 4일 이전 병사에게 보고되어 김생원 체포 지시의 근거가 되었다(G04b). "
            "이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했고 장교 일행이 그 분부에 따라 김명신과 김갑득을 잡아왔다고 진술했다. "
            "[L] 김명신은 구금 중 형장은 받지 않았으나 반복 조사 압박을 받았고 이어 발병해 죽었다(G06b). 정조의 '평범한 신문도 받지 않았다'는 판단과 긴장한다. "
            "[L] 명업 등이 병영에서 '도적이 없었다'는 취지로 진술을 바꾸었고 그 번복이 5월 판단 자료에 들어갔다(G07c). "
            "5월 12일 정조는 장계와 조사에 따라 도난 자체가 없었다는 방향을 받아들였다. "
            "[L] 정조는 이조원의 전문 의존을 문제 삼은 다음 날 홍대협을 보냈다(G08a). "
            "6월 13일 홍대협은 약간의 실제 도난을 판단하고 김명신의 죽음을 질병 때문이라고 평가했으며, 정조는 도난 실재와 부처의 전염병 사망을 판단했다. "
            "[L] 김명신의 아내도 전염병으로 죽었다(G12a). "
            "[L] 한 비장=한재욱(ID02)과 한가=한재욱(ID03)이 모두 성립한다면, 한가 처분의 근거는 회유·대질 지휘와 출동 운영이다(G09a)."),
    ),
    dict(
        world_id="W3", name="사적 후원 경로 (구순 ↔ 병영 지휘관, 약함)",
        latent_bridges=["G01b", "G02a", "G04c", "G05a", "G06a", "G07a", "G08a", "G12a"],
        inst_note="핵심 bridge G04c가 LOW다. 구순에게는 병영 장교를 지휘할 공식 권한이 없어서(F007) 이 경로는 사적 정보 제공으로만 표현했다. "
                  "G05a의 사적 서찰도 공식 보고 경로가 아니다(F020).",
        env_note="환경은 G06a·G12a의 environmental_fit 평가에만 썼다.",
        main_assumptions=[
            "소장이 병영에 직접 접수(G01b)",
            "3/4 이전 구순이 병사에게 사적으로 김명신을 의심 대상으로 알림(G04c)",
            "3/4 서찰이 전달되어 체포를 지지(G05a)",
            "병사 = 이광섭(ID01), 철퇴 = 철편(ID07)",
        ],
        main_weaknesses=[
            "LOW bridge(G04c)에 기댄다. 3/4 이전 접촉을 보여 주는 confirmed fact가 없고, 05 흔적(V3P0053·V3P0148)도 audit-only다. retained world 가운데 가장 약하다.",
            "G01b는 CF026(진영 영장 이문협의 위임·방관 평가)을 설명하지 못한다.",
            "구순은 공식 지휘권이 없으므로 이 경로는 정보 제공일 뿐 명령 경로가 아니다. 체포 지시의 공식 주체는 여전히 병사다(CF023).",
            "ID01·ID07에 기댄다.",
        ],
        contradicted_evidence="직접 충돌하는 confirmed fact 없음. 약한 반증: CF026(진영 영장이 수사를 병영 비장에게 맡김)은 병영 직접 접수(G01b)와 잘 맞지 않는다.",
        story_implication="구순과 병영 지휘관 사이의 사적 통로(3/4 이전 접촉과 3/4 서찰)를 사건의 축으로 본다. 정조가 이광섭이 '구순 편을 들었다'고 한 판단을 "
                          "가장 직접적으로 풀어 쓰지만, 핵심 bridge가 LOW라서 retained world 가운데 가장 약하다.",
        narrative=(
            "명업은 김명신이 구순을 힐책한 뒤 왕래가 끊겼고, 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다. "
            "[L] 소장은 병영에 직접 접수되었고 병영이 체포령을 내렸다(G01b). "
            "[L] 이광섭이 출동과 철퇴 제작을 지시했다. 철퇴와 철편이 같은 물건일 때(ID07)만 성립한다(G02a). "
            "이진욱은 2월 28일 밤 한재욱이 덕평 출동을 지시하고 철편 네 개를 만들어 주었다고 진술했다. "
            "[L] 3월 4일 이전 구순이 병사에게 사적으로 김명신을 의심 대상으로 알렸다(G04c, LOW). 공식 명령이 아니라 정보 제공이다. "
            "이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했다고 진술했다. "
            "조계완은 김명신을 잡으러 가는 길에 구순이 '이제 도적 다스리는 일이 바른 길을 얻었다'는 취지로 말하고 병사에게 전할 서찰을 건넸다고 진술했다. "
            "[L] 서찰은 병사에게 전달되었고 체포를 지지했다. 정조가 말한 이광섭과 잇는 것은 병사=이광섭(ID01) 조건이다(G05a). "
            "[L] 김명신은 구금 중 발병해 5월 12일 보고 이전에 죽었다(G06a). "
            "[L] 5월의 도난 부재 방향은 장물 미발견에서 나온 추론이었다(G07a). "
            "[L] 정조는 이조원 비판 다음 날 홍대협을 보냈다(G08a). "
            "6월 13일 정조는 이광섭이 구순 편을 들었다고 비판하고 구순과 이광섭의 책임이 크게 다르지 않다고 판단했다. "
            "[L] 김명신의 아내도 전염병으로 죽었다(G12a)."),
    ),
    dict(
        world_id="W4", name="분산 지휘 (단일 명령 계통 없음)",
        latent_bridges=["G01a", "G02b", "G03c", "G06a", "G07b", "G08b", "G11a", "G13a"],
        inst_note="비장의 자체 판단(G02b)과 비장을 건너뛴 직접 보고(G03c)가 MEDIUM이다. 제도상 불가능하지는 않지만 정상 경로도 아니다.",
        env_note="환경은 G06a의 environmental_fit 평가에만 썼다.",
        main_assumptions=[
            "진영 → 병영 비장 이관(G01a)",
            "비장의 자체 판단 출동과 병영 지휘관의 사후 묵인(G02b)",
            "유제희가 비장을 건너뛰고 병사에게 직접 보고(G03c, ID05 조건)",
            "5월 판단은 회동 조사 응답자 진술을 채택(G07b)",
            "홍대협 차하의 주목적은 지세 의문(G08b)",
        ],
        main_weaknesses=[
            "G03c는 LOW이며 05 V3P0085(한재욱이 유제희를 내보냈다는 공초, audit-only)와 긴장한다.",
            "G08b의 '주목적'은 정조가 세 의안을 나누었다는 05 기록(V3P0103)에 비추어 과장일 수 있다.",
            "G07b의 근거(회동 조사 응답)는 05에만 있는 중첩 진술이다.",
            "G04(구순 발언 → 3/4 지시)를 비워 두므로 정조의 구순 책임 사슬(CF043)을 event 수준으로 설명하지 못한다.",
        ],
        contradicted_evidence="직접 충돌하는 confirmed fact 없음. 긴장: 05 V3P0085(audit-only) ↔ G03c.",
        story_implication="명확한 단일 명령 계통 없이 여러 행위자가 각자 움직인 경로다. 비장은 자체 판단으로 출동을 지시했고, 유제희는 비장을 건너뛰어 병사에게 "
                          "직접 보고했으며, 공주진은 독자적으로 변지돌을 잡았다. 정조의 '비장에게 일을 맡겼다'(CF044)와 이형원의 '방관'(CF026) 평가를 "
                          "지휘 공백으로 읽는다.",
        narrative=(
            "명업은 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다. "
            "[L] 소장은 청주 진영에 접수되었고 진영은 수사를 병영 비장 쪽에 넘겼다(G01a). 이형원은 영장 이문협이 수사를 병영 비장에게 전적으로 맡기고 방관했다고 평가했다. "
            "[L] 한재욱은 위의 구체적 명령 없이 2월 28일 출동을 지시했고 병영 지휘관은 나중에 묵인했다(G02b). "
            "이진욱은 한재욱이 덕평 출동과 체포를 지시했다고 진술했다. "
            "[L] 변지돌은 공주진이 독자 판단으로 먼저 잡아갔다(G11a). "
            "유제희는 현지 탐문 중 구순이 '풍각 김상제도 극히 수상하다'고 말했고 자신이 그 말을 원돌 등의 이름과 함께 기록해 올렸다고 진술했다. "
            "[L] 유제희는 그 기록을 비장을 건너뛰고 병사에게 직접 올렸다. 3월 4일 지시와 잇는 것은 김상제가 김명신이라는 가정(ID05) 아래서다(G03c, LOW). "
            "이진욱은 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했다고 진술했다. "
            "[L] 김명신은 구금 중 발병해 5월 12일 보고 이전에 죽었다(G06a). "
            "[L] 5월 12일 판단은 회동 조사 응답자들이 '구순이 도난 상황을 꾸몄다'고 한 진술을 채택한 것이었다(G07b). 응답 내용의 진위는 다루지 않는다. "
            "[L] 의금부에서 구순 신문이 실행되었으나 지세 문제는 결론이 나지 않았다(G13a). "
            "[L] 정조가 홍대협을 보낸 주목적은 지세 호칭의 출처를 밝히는 것이었다(G08b). "
            "6월 13일 정조는 이광섭이 아전들의 거짓을 제대로 살피지 않은 채 비장에게 일을 맡겼다고 비판했다. "
            "공초의 병사와 이광섭을 같은 사람으로 읽는 것은 ID01 조건이며 확정하지 않는다."),
    ),
    dict(
        world_id="W5", name="최소 가정 (HIGH 후보만)",
        latent_bridges=["G01a", "G06a", "G07a", "G08a"],
        inst_note="네 bridge 모두 제도 경로(진영·병영 비장, 병영 구금, 장계 → 국왕 판단, 안핵어사 차하) 안에 있다.",
        env_note="환경은 G06a의 environmental_fit 평가에만 썼다.",
        main_assumptions=[
            "소장 접수처 = 청주 진영, 2/28 이전 병영 비장 쪽 이관(G01a)",
            "김명신의 발병은 체포 이후(G06a)",
            "장물 부재가 5월 도난 부재 추론의 근거(G07a)",
            "5/27 비판이 5/28 차하의 동기(G08a)",
        ],
        main_weaknesses=[
            "사건의 핵심 정보 경로(G03·G04·G05)를 비워 두므로 정조의 구순 책임 판단(CF043)이 event 수준에서 어떻게 성립하는지 말하지 못한다.",
            "설명력은 가장 낮고, 가정 비용도 가장 낮다.",
        ],
        contradicted_evidence="직접 충돌하는 confirmed fact 없음. 긴장: CF027('구금·조사') ↔ G06a가 따르는 CF041(평문 없음) — PARTIAL.",
        story_implication="HIGH 후보만 얹고 나머지 gap은 비워 둔 world다. 소장 → 진영 → 병영 비장 이관, 구금 중 발병·사망, 장물 미발견에서 나온 5월 도난 부재 판단, "
                          "이조원 비판 뒤 독립 안핵이라는 네 다리만 놓는다. 구순의 말이 어떻게 3/4 체포 지시에 닿았는지는 미해결로 남긴다.",
        narrative=(
            "명업은 구순이 소장을 올린 뒤 체포령이 내려졌다고 진술했다. "
            "[L] 소장은 청주 진영에 접수되었고 진영은 수사를 병영 비장 쪽에 넘겼다(G01a). "
            "이진욱은 2월 28일 밤 한재욱이 덕평 출동을 지시했고, 3월 4일 병사가 풍각 김생원과 흥덕 김생원을 잡아오라고 지시해 장교 일행이 잡아왔다고 진술했다. "
            "유제희의 기록이 그 지시에 어떻게 닿았는지는 비워 둔다(G03·G04 미해결). "
            "[L] 김명신은 구금 중 발병해 5월 12일 보고 이전에 죽었다(G06a). "
            "[L] 5월 12일 정조가 받아들인 도난 부재 방향은 장물 미발견에서 나온 추론이었다(G07a). "
            "[L] 정조는 이조원이 직접 안핵하지 않은 점을 문제 삼은 다음 날 홍대협을 보냈다(G08a). "
            "6월 13일 정조는 도난 실재와 부처의 전염병 사망을 판단했고, 직접 인과는 십분 확실하지 않다고 하면서도 구순의 책임을 판단했다."),
    ),
    dict(
        world_id="W6", name="모함·장형 사망 (이조원·윤노동 쪽 주장) — 기각 대조",
        latent_bridges=["G06c", "G07d", "G12b"], rejected=True,
        inst_note="G06c(형장)는 F002·F003 형정 제한과 정조 판단 모두에서 낮다.",
        env_note="G06c·G12b는 전염병 환경과 어긋나는 사인을 가정하므로 environmental_fit이 MEDIUM에 그친다.",
        main_assumptions=[
            "도난 자체가 없었고 구순이 상황을 꾸밈(G07d)",
            "김명신이 열린 집합('무고한 평민들', '여러 죄수')의 형장 대상에 포함(G06c)",
            "아내는 전염병이 아닌 원인으로 따라 죽음(G12b)",
        ],
        main_weaknesses=[
            "세 bridge 모두 contradiction_risk HIGH, overall LOW다.",
            "열린 집합에 김명신을 넣어야 G06c가 성립한다(closed-set 오류 위험).",
            "근거가 05 audit-only 주장(V3P0020·V3P0024·V3P0025·V3P0127)뿐이다.",
        ],
        contradicted_evidence="CF038(홍대협: 약간의 실제 도난), CF039(정조: 도난 실재), CF040(홍대협 질병 평가·정조 부처 전염병 사망 판단), "
                              "CF041(정조: 곤장·평문 없음).",
        story_implication="이조원·윤노동 쪽 주장(05)을 따른 world다. 도난은 없었고 구순이 꾸몄으며, 김명신은 형장 뒤 쇠약해져 죽었고, 아내는 전염병이 아닌 "
                          "원인으로 따라 죽었다고 본다. 최종 official·royal finding과 정면으로 충돌하므로 기각하고 대조용으로만 남긴다.",
        narrative=(
            "[L] 도난은 없었고 구순이 상황을 꾸몄다(G07d). 그러나 홍대협은 약간의 실제 도난을, 정조는 도난 실재를 판단했다. "
            "[L] 김명신은 구금 중 형장을 받고 쇠약해져 죽었다(G06c). 그러나 정조는 김명신이 곤장을 맞지 않았고 평범한 신문도 받지 않았다고 판단했다. "
            "[L] 아내는 전염병이 아닌 원인으로 따라 죽었다(G12b). 그러나 정조는 부처가 전염병에 걸려 죽은 것으로 판단했다."),
    ),
]


def _min_grade(vals):
    vals = [v for v in vals if v and v != "N/A"]
    return NAME[min(SCORE[v] for v in vals)] if vals else "N/A"


def build(nodes, edges, gaps, cands):
    cand = {c["candidate_id"]: c for c in cands}
    gap_ids = [g["gap_id"] for g in gaps]
    obs = {n["node_id"] for n in nodes}
    out = []
    for w in WORLDS:
        bridges = w["latent_bridges"]
        cs = [cand[b] for b in bridges]
        rejected = bool(w.get("rejected"))
        # --- 무결성 검사 (assert) ---
        gs = [c["gap_id"] for c in cs]
        assert len(gs) == len(set(gs)), f"{w['world_id']}: 한 gap에 후보 2개 이상"
        for c in cs:
            assert c["status"] == "LATENT", f"{w['world_id']}: {c['candidate_id']} LATENT 아님"
            if not rejected:
                assert c["overall"] != "INCOMPATIBLE", f"{w['world_id']}: INCOMPATIBLE 후보 {c['candidate_id']}"
                assert c["contradiction_risk"] != "HIGH", f"{w['world_id']}: 대조용 후보 {c['candidate_id']}"
        for a, b, why in CONFLICT_PAIRS:
            assert not (a in bridges and b in bridges), f"{w['world_id']}: 상충 후보 {a}+{b} — {why}"
        # --- 기계적 계산 ---
        inst = _min_grade([c[k] for c in cs for k in ("institutional_fit", "role_fit")])
        env = _min_grade([c["environmental_fit"] for c in cs])
        low_inst = [f"{c['candidate_id']}({min((c['institutional_fit'], c['role_fit']), key=lambda v: SCORE.get(v, 9))})"
                    for c in cs if inst != "N/A" and SCORE[inst] in
                    [SCORE.get(c["institutional_fit"], 9), SCORE.get(c["role_fit"], 9)]]
        env_rated = [f"{c['candidate_id']}({c['environmental_fit']})" for c in cs if c["environmental_fit"] != "N/A"]
        ids = sorted({i for c in cs for i in c["identity_conditions"].split("|") if i})
        touch = sorted({x for c in cs for le in c["latent_edges"] for x in (le["src"], le["dst"]) if x in obs})
        out.append(dict(
            world_id=w["world_id"], name=w["name"], rejected=rejected,
            observed_backbone=f"동결 observed DAG 전체 공유(node {len(nodes)}, edge {len(edges)}, LATENT 0). "
                              f"bridge가 닿는 observed node: {', '.join(touch) or '없음'}",
            latent_bridges=list(bridges),
            unresolved_gaps=[g for g in gap_ids if g not in gs],
            institutional_fit=inst,
            institutional_note=f"bridge의 institutional·role fit 최소값. 최저 bridge: {', '.join(low_inst) or '-'}. {w['inst_note']}",
            environmental_fit=env,
            environmental_note=f"환경 평가가 있는 bridge: {', '.join(env_rated) or '없음'}. {w['env_note']}",
            n_assumptions=sum(c["n_assumptions"] for c in cs),
            min_grade=_min_grade([c["overall"] for c in cs]),
            main_assumptions=list(w["main_assumptions"]) + ([f"미확정 동일성 조건: {', '.join(ids)} (확정하지 않음)"] if ids else []),
            main_weaknesses=list(w["main_weaknesses"]),
            contradicted_evidence=w["contradicted_evidence"],
            story_implication=w["story_implication"],
            narrative=w["narrative"],
            identity_conditions="|".join(ids),
        ))
    # world 사이 최소 2개 gap에서 차이
    for a, b in combinations(out, 2):
        pa = {cand[x]["gap_id"]: x for x in a["latent_bridges"]}
        pb = {cand[x]["gap_id"]: x for x in b["latent_bridges"]}
        diff = sum(pa.get(g) != pb.get(g) for g in gap_ids)
        assert diff >= 2, f"{a['world_id']}·{b['world_id']} 차이 gap {diff}개 < 2"
    assert 3 <= len(out) <= 7
    return out
