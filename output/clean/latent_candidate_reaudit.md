# LATENT 후보 재감사 — bridge 자체의 사료 근거

문제: 일부 후보는 양끝 OBSERVED 사실이 확실하다는 이유로, 그 사이에 넣은 LATENT bridge의 source support까지 높게 받았다. 이번 재감사는 38개 후보 전부에 대해 **후보가 새로 추가한 내용 자체**의 사료 근거만 다시 평가했다. 새 역사적 사실은 만들지 않았고, OBSERVED·DERIVED·LATENT 경계도 바꾸지 않았다.

## 평가 원칙

- source support의 근거가 아닌 것: 양끝 OBSERVED 사건의 확실성(→ endpoint_support), 시간 인접성(→ temporal_fit), 제도상 가능성(→ institutional_fit), 정보 경로의 자연스러움(→ information_flow_fit), 정조 최종 판단과의 정합.
- endpoint node의 구성 fact는 bridge 근거로 쓰지 않는다(endpoint leakage는 Audit 3 ERROR).
- HIGH: bridge 내용 자체가 사료 문장으로 강하게 지지된다(이 경우 LATENT 분류부터 다시 점검). MEDIUM: bridge 자체는 없지만 같은 사건의 비-endpoint 사료나 직접 연결되는 진술이 상당히 지지한다(audit-only 근거만 있으면 상한). LOW: 직접 근거 없이 시간·제도·주변 사실에서 나온 추론이다. NONE: 제도상 가능성이나 이야기상 자연스러움 말고는 근거가 없다.
- 최종 등급 = min(evidence_grade, plausibility_grade) + 충돌·근거유형·동일성 상한. 확률 수치는 만들지 않았다.

## 요약

- source support가 바뀐 후보: **30개 / 38개**
- final grade가 바뀐 후보: **16개** (G01a, G01b, G02b, G03b, G04b, G05a, G06a, G06b, G07a, G07c, G08a, G08b, G09a, G11a, G12a, G13a)
- HIGH 후보(final): 4개 → **0개**

| 등급 | source support 이전 | source support 이후 | final 이전 | final 이후 |
|---|---|---|---|---|
| HIGH | 7 | 0 | 4 | 0 |
| MEDIUM | 14 | 7 | 17 | 7 |
| LOW | 16 | 18 | 14 | 28 |
| NONE | 0 | 13 | 0 | 0 |
| INCOMPATIBLE | 1 | 0 | 3 | 3 |

이전 source 값에는 NONE 등급이 없었다. 이전의 INCOMPATIBLE 1개는 G04e의 source 칸 값이다.

## 집중 재검토 4건 (이전 HIGH)

| 후보 | observed_left | observed_right | latent_bridge_claim | bridge 직접? | endpoint support | source support | final | 사유 |
|---|---|---|---|---|---|---|---|---|
| G01a | EP03 구순의 소장과 체포령 | EP04 2월 28일 밤 병영 출동 준비 | 소장이 청주 진영에 접수되었고, 진영이 수사를 병영 비장 쪽에 넘겼으며, 그것이 2/28 이전이었다 | PARTIAL | MEDIUM (진술 기록 endpoint 포함) | HIGH → **MEDIUM** | HIGH → **MEDIUM** | '진영 → 병영 비장 위임'은 endpoint가 아닌 CF026(이형원 평가: 이문협이 수사를 병영 비장에게 맡김)이 지지한다. 그러나 '접수처 = 청주 진영'은 05 audit-only(V3P0084 한재욱 공초)에만 있고 이관 시점도 없다. 일부만 지지되므로 MEDIUM이다. |
| G06a | EP11 3월 4일 김명신·김갑득 체포 | EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고 | 김명신의 발병이 3/4 체포 이후 구금 중에 시작되었고 5/12 보고 이전에 죽었다 | PARTIAL | MEDIUM (진술 기록 endpoint 포함) | HIGH → **MEDIUM** | HIGH → **MEDIUM** | endpoint가 아닌 CF029(윤노동 별단: '보수·구금 중 병들어 죽었다')가 구금 중 발병·사망을 보고 수준에서 지지한다. 다만 이것은 암행어사의 보고이고, 발병이 체포 '이후' 시작되었다는 시점 자체를 따로 확인한 문장은 없다. 그래서 HIGH가 아니라 MEDIUM이다. |
| G07a | EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고 | EP15 5월 12일 정조 1차 판단: 도난 부재 방향 | 5월 단계의 '도난 없음' 판단은 장물 미발견을 근거로 한 추론이었다 | NO | HIGH (공식 보고·판단·명령 endpoint) | HIGH → **LOW** | HIGH → **LOW** | '장물 못 찾음'(CF027, EP13)과 '도난 없음 방향 수용'(CF030, EP15)은 각각 endpoint다. CF030의 '장계와 조사에 따라'라는 연결은 이미 observed edge OE040(REVIEW_OF)이 담고 있다. 이 후보가 새로 더한 것은 '그중 장물 부재가 이유였다'는 추론인데, 이를 적은 사료는 없다. |
| G08a | EP18 5월 27일 정조의 이조원 비판·파직 | EP20 5월 28일 홍대협 공주 안핵어사 차하 | 5/27 이조원의 직접 안핵 부재에 대한 정조의 비판이 5/28 홍대협 차하의 동기였다 | NO | HIGH (공식 보고·판단·명령 endpoint) | HIGH → **LOW** | HIGH → **LOW** | 두 행위(CF033 비판, CF035 차하)는 모두 endpoint다. 동기 문장은 01·04·05 어디에도 없다. 05 V3P0028도 비판 내용(endpoint와 같은 내용)일 뿐이다. 하루 차이라는 시간 인접성과 두 endpoint 내용의 주제 대응만으로는 bridge 근거가 되지 않는다. |

## 38개 후보 before / after

| candidate | old source support | new source support | old final grade | new final grade | changed? | reason |
|---|---|---|---|---|---|---|
| G01a | HIGH | MEDIUM | HIGH | MEDIUM | YES (source·final) | '진영 → 병영 비장 위임'은 endpoint가 아닌 CF026(이형원 평가: 이문협이 수사를 병영 비장에게 맡김)이 지지한다. 그러나 '접수처 = 청주 진영'은 05 audit-only(V3P0084 한재욱 공초)에만 있고 이관 시점도 없다. 일부만 지지되므로 MEDIUM이다. |
| G01b | MEDIUM | NONE | MEDIUM | LOW | YES (source·final) | 접수처를 병영으로 적은 사료가 없다. 근거로 든 CF006은 endpoint(EP03) 자체이고, 05 V3P0084는 오히려 진영 정소를 말한다. |
| G01c | LOW | NONE | LOW | LOW | YES (source) | 제도 피쳐(F005·F006)상 가능한 경로라는 것 말고는 사료 근거가 없다. |
| G02a | HIGH | MEDIUM | MEDIUM | MEDIUM | YES (source) | endpoint가 아닌 CF044(정조: 이광섭이 철퇴 네 개를 만들게 함)가 '제작 지시' 부분을 royal judgment 수준에서 지지한다. 다만 철퇴=철편은 ID07 미확정이고, 덕평 출동까지 이광섭의 지시였다는 부분은 사료에 없다. |
| G02b | MEDIUM | LOW | MEDIUM | LOW | YES (source·final) | CF026·CF044의 '비장에게 맡겼다'는 평가는 위임 일반을 말할 뿐, '상위 명령 없이'와 '사후 묵인'은 어디에도 없다. 평가 문구를 지휘 공백으로 읽은 추론이다. |
| G02c | LOW | NONE | LOW | LOW | YES (source) | 지지 근거가 없고 CF026(이문협은 맡기고 '방관')과 충돌한다. |
| G03a | MEDIUM | MEDIUM | MEDIUM | MEDIUM | no | 파견과 명단 작성은 05 한재욱 공초(V3P0085–V3P0087)에 진술로 있다. 그러나 audit-only이고 기록 시점·수신자는 없다. CF009·CF020은 endpoint(EP04·EP08)라 bridge 근거로 쓰지 않았다. audit-only 상한으로 MEDIUM이다. |
| G03b | MEDIUM | LOW | MEDIUM | LOW | YES (source·final) | CF043(정조: 성명 제공 → 횡액)은 정보가 사건으로 이어졌다는 판단일 뿐 시점·직접 촉발을 말하지 않는다. ID11 확정으로 원돌(=정원돌)이 2/28 대상이었으므로 시점 가정과 긴장한다. |
| G03c | LOW | NONE | LOW | LOW | YES (source) | 지지 근거가 없고 05 V3P0085(한재욱이 유제희를 내보냈다)와 긴장한다. |
| G04a | HIGH | MEDIUM | MEDIUM | MEDIUM | YES (source) | endpoint가 아닌 CF043(정조: 구순이 병영의 염탐 담당자에게 성명을 적어 주었고 그것이 횡액으로 이어졌다)이 '구순의 정보가 체포로 이어졌다'는 연결을 판단 수준에서 지지한다. '비장 계통 → 병사' 경로는 사료에 없고, 염탐 담당자=유제희는 ID06 미확정이다. |
| G04b | MEDIUM | LOW | MEDIUM | LOW | YES (source·final) | CF023(김갑득이 김명신과 함께 체포)은 이름이 겹친다는 정황일 뿐이다. 05 윤노동 주장은 회유 공초를 말하지만 그 공초가 병사에게 보고되어 지시 근거가 되었다는 내용은 없다. 보고·근거 연결 자체는 사료에 없다. |
| G04c | LOW | LOW | LOW | LOW | no | CF024(3/4 서찰)는 지시 이후의 일이고, CF044('구순 편을 듦')는 관계 판단이다. 3/4 이전 접촉을 적은 사료는 없다. |
| G04d | LOW | LOW | LOW | LOW | no | 05 한재욱 공초 속 유제희 발언(중첩, audit-only)에 석단 공초가 언급될 뿐, 시점·보고는 없다. |
| G04e | INCOMPATIBLE | NONE | INCOMPATIBLE | INCOMPATIBLE | YES (source) | 근거가 없고 CF023('병사의 분부에 따라')·제도(F007·F008)와 충돌한다. |
| G05a | MEDIUM | LOW | MEDIUM | LOW | YES (source·final) | 전달 여부와 서찰 내용은 어디에도 없다. CF024(서찰 수령·'바른 길' 발언)와 CF044(구순 편)는 endpoint(EP10·EP30)라 bridge 근거가 아니다. endpoint가 아닌 CF025(이형원: 허황한 말을 믿고)는 간접 정황일 뿐이다. |
| G05b | LOW | NONE | LOW | LOW | YES (source) | 지지 근거가 없고 CF024의 맥락과 어울리지 않는다. |
| G06a | HIGH | MEDIUM | HIGH | MEDIUM | YES (source·final) | endpoint가 아닌 CF029(윤노동 별단: '보수·구금 중 병들어 죽었다')가 구금 중 발병·사망을 보고 수준에서 지지한다. 다만 이것은 암행어사의 보고이고, 발병이 체포 '이후' 시작되었다는 시점 자체를 따로 확인한 문장은 없다. 그래서 HIGH가 아니라 MEDIUM이다. |
| G06b | MEDIUM | LOW | MEDIUM | LOW | YES (source·final) | 발병 부분은 CF029가 보고하지만, 이 후보가 새로 넣은 '반복 조사 압박'은 근거가 CF027('구금·조사', endpoint EP13)뿐이다. 게다가 CF041(평범한 신문 없음)과 긴장한다. |
| G06c | LOW | LOW | LOW | LOW | no | CF029의 '여러 죄수 참혹한 형벌'은 열린 집합이라 김명신 포함을 지지하지 않는다. CF041(곤장 없음)과 정면 충돌한다. |
| G07a | HIGH | LOW | HIGH | LOW | YES (source·final) | '장물 못 찾음'(CF027, EP13)과 '도난 없음 방향 수용'(CF030, EP15)은 각각 endpoint다. CF030의 '장계와 조사에 따라'라는 연결은 이미 observed edge OE040(REVIEW_OF)이 담고 있다. 이 후보가 새로 더한 것은 '그중 장물 부재가 이유였다'는 추론인데, 이를 적은 사료는 없다. |
| G07b | MEDIUM | MEDIUM | MEDIUM | MEDIUM | no | 05의 같은 장계 기사(SRC3_001)에 응답자 진술이 장계 내용으로 실려 있다(audit-only). 판단이 그 진술을 채택했다는 문장은 없지만 같은 기록 안의 연결이라 audit-only 상한인 MEDIUM이다. |
| G07c | MEDIUM | LOW | MEDIUM | LOW | YES (source·final) | 번복 자체는 05의 명업 공초(audit-only)에 있지만, 그것이 장계나 5월 판단 자료에 들어갔다는 내용은 없다. |
| G07d | LOW | LOW | LOW | LOW | no | 이조원·윤노동의 05 주장뿐이다. CF038·CF039(최종 판단)와 정면 충돌한다. |
| G08a | HIGH | LOW | HIGH | LOW | YES (source·final) | 두 행위(CF033 비판, CF035 차하)는 모두 endpoint다. 동기 문장은 01·04·05 어디에도 없다. 05 V3P0028도 비판 내용(endpoint와 같은 내용)일 뿐이다. 하루 차이라는 시간 인접성과 두 endpoint 내용의 주제 대응만으로는 bridge 근거가 되지 않는다. |
| G08b | MEDIUM | LOW | MEDIUM | LOW | YES (source·final) | 05 승정원일기 대화(V3P0033·V3P0035)는 5/28에 지세랑 호칭이 화제였음을 보이지만 '주목적'이라고 하지는 않는다. V3P0103(세 의안 분리)에 비추면 과장이다. |
| G09a | MEDIUM | LOW | MEDIUM | LOW | YES (source·final) | 처분 근거를 적은 문장이 없다. CF016·CF017·CF018·CF048은 endpoint(EP07·EP35 등)라 근거가 아니다. CF044와 05 윤노동 주장은 비장·회유를 말할 뿐 한가 처분과 연결하지 않는다. |
| G09b | LOW | NONE | INCOMPATIBLE | INCOMPATIBLE | YES (source) | 근거가 없고 사용자 확정 ID02와 충돌한다(INCOMPATIBLE). |
| G09c | LOW | NONE | INCOMPATIBLE | INCOMPATIBLE | YES (source) | 근거가 없고 사용자 확정 ID03과 충돌한다(INCOMPATIBLE). |
| G10a | MEDIUM | MEDIUM | MEDIUM | MEDIUM | no | 같은 6/13 기사에서 정조가 '도신 장계와 안핵어사 보고가 도난 여부에서 현격히 달랐다'고 지적했다(05 V3P0152, audit-only). 파직 사유라고 명시한 것은 아니므로 MEDIUM이다. G10은 사용자 검토로 OPEN_UNRESOLVED이며 어느 world에도 쓰지 않는다. |
| G10b | LOW | NONE | LOW | LOW | YES (source) | 환경 피쳐(E002·E003)만 근거이고 6월 상황을 적은 사료가 없다. |
| G10c | LOW | NONE | LOW | LOW | YES (source) | 제도상 관행이라는 일반론뿐이다. |
| G11a | MEDIUM | LOW | MEDIUM | LOW | YES (source·final) | endpoint가 아닌 CF009(2/28 변지돌 체포 지시)는 변지돌이 이 사건 혐의자였음을 보여 줄 뿐이다. 공주진이 누구 판단으로 왜 잡았는지는 없다. CF011('이미 잡혀간 상태')은 endpoint(EP05)다. |
| G11b | LOW | NONE | LOW | LOW | YES (source) | 근거가 없고 CF009(2/28에 새로 체포 지시)와 긴장한다. |
| G11c | LOW | NONE | LOW | LOW | YES (source) | 근거가 없다. |
| G12a | HIGH | LOW | MEDIUM | LOW | YES (source·final) | 아내의 사망 원인을 적은 것은 endpoint인 정조 판단(CF040, EP27) 자체뿐이다. 이 후보는 그 판단 내용을 사건으로 옮긴 것이라 endpoint 인용을 bridge 근거로 쓸 수 없다(판단 → 사실 전환 금지). 05 이조원 보고는 아내의 사망은 전하지만 원인은 '따라 죽었다'로 다르다. |
| G12b | LOW | LOW | LOW | LOW | no | 05 이조원 보고뿐이다. CF040(부처 전염병)과 정면 충돌한다. |
| G13a | MEDIUM | LOW | MEDIUM | LOW | YES (source·final) | 명령(CF031·CF034)과 6/13 판단(CF045)은 endpoint다. 실행을 적은 사료가 없다. 05 V3P0137(홍대협: 의금부 국문이 필요하다)은 결론이 없었다는 정황일 뿐 실행 근거는 아니다. |
| G13b | LOW | NONE | LOW | LOW | YES (source) | 근거가 없고 CF034(반복 신문 명)와 긴장한다. |

## 38개 후보 전체 재감사표

| candidate_id | gap_id | observed_left | observed_right | latent_bridge_claim | bridge_directly_attested | endpoint_support | source_support | institutional_fit | temporal_fit | information_flow_fit | assumption_cost | contradiction_risk | final_grade | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G01a | G01 | EP03 구순의 소장과 체포령 | EP04 2월 28일 밤 병영 출동 준비 | 소장이 청주 진영에 접수되었고, 진영이 수사를 병영 비장 쪽에 넘겼으며, 그것이 2/28 이전이었다 | PARTIAL | MEDIUM (진술 기록 endpoint 포함) | MEDIUM | HIGH | HIGH | HIGH | 2 | LOW | MEDIUM | evidence MEDIUM · plausibility HIGH · 근거 CF026/V3P0084/V3P0102 — '진영 → 병영 비장 위임'은 endpoint가 아닌 CF026(이형원 평가: 이문협이 수사를 병영 비장에게 맡김)이 지지한다. 그러나 '접수처 = 청주 진영'은 05 audit-only(V3P0084 한재욱 공초)에만 있고 이관 시점도 없다. 일부만 지지되므로 MEDIUM이다. |
| G01b | G01 | EP03 구순의 소장과 체포령 | EP04 2월 28일 밤 병영 출동 준비 | 소장이 병영에 직접 접수되었고 병영이 체포령을 냈다 | NO | MEDIUM (진술 기록 endpoint 포함) | NONE | HIGH | HIGH | MEDIUM | 1 | MEDIUM | LOW | evidence NONE · plausibility MEDIUM · 근거 없음 — 접수처를 병영으로 적은 사료가 없다. 근거로 든 CF006은 endpoint(EP03) 자체이고, 05 V3P0084는 오히려 진영 정소를 말한다. |
| G01c | G01 | EP03 구순의 소장과 체포령 | EP04 2월 28일 밤 병영 출동 준비 | 소장이 청주목 수령에게 접수되어 관찰사를 거쳐 병영으로 이첩되었다 | NO | MEDIUM (진술 기록 endpoint 포함) | NONE | HIGH | MEDIUM | MEDIUM | 3 | MEDIUM | LOW | evidence NONE · plausibility MEDIUM · 근거 없음 — 제도 피쳐(F005·F006)상 가능한 경로라는 것 말고는 사료 근거가 없다. |
| G02a | G02 | (없음 — 위쪽 원인 가설) | EP04 2월 28일 밤 병영 출동 준비 | 이광섭이 2/28 출동과 철퇴(=철편) 네 개 제작을 지시했고 한재욱이 그것을 전달·집행했다 | PARTIAL | MEDIUM (진술 기록 endpoint 포함) | MEDIUM | HIGH | HIGH | HIGH | 2 | LOW | MEDIUM | evidence MEDIUM · plausibility MEDIUM · 근거 CF044/CF025 — endpoint가 아닌 CF044(정조: 이광섭이 철퇴 네 개를 만들게 함)가 '제작 지시' 부분을 royal judgment 수준에서 지지한다. 다만 철퇴=철편은 ID07 미확정이고, 덕평 출동까지 이광섭의 지시였다는 부분은 사료에 없다. |
| G02b | G02 | EP04 2월 28일 밤 병영 출동 준비 | EP04 2월 28일 밤 병영 출동 준비 | 한재욱이 상위 명령 없이 자기 판단으로 출동을 지시했고 병영 지휘관이 사후 승인·묵인했다 | NO | MEDIUM (진술 기록 endpoint 포함) | LOW | MEDIUM | HIGH | MEDIUM | 3 | MEDIUM | LOW | evidence LOW · plausibility MEDIUM · 근거 CF026/CF044 — CF026·CF044의 '비장에게 맡겼다'는 평가는 위임 일반을 말할 뿐, '상위 명령 없이'와 '사후 묵인'은 어디에도 없다. 평가 문구를 지휘 공백으로 읽은 추론이다. |
| G02c | G02 | (없음 — 위쪽 원인 가설) | EP04 2월 28일 밤 병영 출동 준비 | 청주 영장 이문협이 2/28 출동을 직접 지휘했다 | NO | MEDIUM (진술 기록 endpoint 포함) | NONE | MEDIUM | MEDIUM | LOW | 1 | HIGH | LOW | evidence NONE · plausibility LOW · 근거 없음 — 지지 근거가 없고 CF026(이문협은 맡기고 '방관')과 충돌한다. |
| G03a | G03 | EP08 유제희의 현지 탐문과 구순 발언 기록 | EP04 2월 28일 밤 병영 출동 준비; EP08 유제희의 현지 탐문과 구순 발언 기록 | 한재욱이 유제희를 탐문에 보냈고, 유제희 기록이 2/28 이전 한재욱에게 올라가 2/28 체포 대상 선정에 쓰였다 | PARTIAL | MEDIUM (진술 기록 endpoint 포함) | MEDIUM | HIGH | MEDIUM | HIGH | 3 | LOW | MEDIUM | evidence MEDIUM · plausibility MEDIUM · 근거 V3P0085/V3P0086/V3P0087 — 파견과 명단 작성은 05 한재욱 공초(V3P0085–V3P0087)에 진술로 있다. 그러나 audit-only이고 기록 시점·수신자는 없다. CF009·CF020은 endpoint(EP04·EP08)라 bridge 근거로 쓰지 않았다. audit-only 상한으로 MEDIUM이다. |
| G03b | G03 | EP08 유제희의 현지 탐문과 구순 발언 기록 | EP09 3월 4일 병사의 김생원 체포 지시 | 유제희 탐문이 2/29~3/4 사이였고 김상제 언급이 3/4 지시를 직접 촉발했다 | NO | MEDIUM (진술 기록 endpoint 포함) | LOW | HIGH | MEDIUM | HIGH | 2 | MEDIUM | LOW | evidence LOW · plausibility MEDIUM · 근거 CF043 — CF043(정조: 성명 제공 → 횡액)은 정보가 사건으로 이어졌다는 판단일 뿐 시점·직접 촉발을 말하지 않는다. ID11 확정으로 원돌(=정원돌)이 2/28 대상이었으므로 시점 가정과 긴장한다. |
| G03c | G03 | EP08 유제희의 현지 탐문과 구순 발언 기록 | EP09 3월 4일 병사의 김생원 체포 지시 | 유제희가 비장을 건너뛰고 병사에게 직접 보고했다 | NO | MEDIUM (진술 기록 endpoint 포함) | NONE | MEDIUM | MEDIUM | MEDIUM | 2 | MEDIUM | LOW | evidence NONE · plausibility MEDIUM · 근거 없음 — 지지 근거가 없고 05 V3P0085(한재욱이 유제희를 내보냈다)와 긴장한다. |
| G04a | G04 | EP08 유제희의 현지 탐문과 구순 발언 기록 | EP09 3월 4일 병사의 김생원 체포 지시 | 유제희 기록이 비장 계통을 거쳐 3/4 이전 병사에게 보고되어 체포 지시의 근거가 되었다 | PARTIAL | MEDIUM (진술 기록 endpoint 포함) | MEDIUM | HIGH | MEDIUM | HIGH | 2 | LOW | MEDIUM | evidence MEDIUM · plausibility MEDIUM · 근거 CF043/CF044/V3P0038 — endpoint가 아닌 CF043(정조: 구순이 병영의 염탐 담당자에게 성명을 적어 주었고 그것이 횡액으로 이어졌다)이 '구순의 정보가 체포로 이어졌다'는 연결을 판단 수준에서 지지한다. '비장 계통 → 병사' 경로는 사료에 없고, 염탐 담당자=유제희는 ID06 미확정이다. |
| G04b | G04 | EP07 한 비장의 석방 조건 제시와 대질 시 거짓 진술 | EP09 3월 4일 병사의 김생원 체포 지시 | 자미덕의 대질 진술이 3/4 이전 병사에게 보고되어 김생원 체포 지시의 근거가 되었다 | NO | MEDIUM (진술 기록 endpoint 포함) | LOW | MEDIUM | MEDIUM | MEDIUM | 3 | MEDIUM | LOW | evidence LOW · plausibility MEDIUM · 근거 CF023/V3P0042/V3P0128 — CF023(김갑득이 김명신과 함께 체포)은 이름이 겹친다는 정황일 뿐이다. 05 윤노동 주장은 회유 공초를 말하지만 그 공초가 병사에게 보고되어 지시 근거가 되었다는 내용은 없다. 보고·근거 연결 자체는 사료에 없다. |
| G04c | G04 | EP01 구순–김명신 관계 변화 | EP09 3월 4일 병사의 김생원 체포 지시 | 3/4 이전 구순이 병사에게 사적으로 김명신을 의심 대상으로 알렸다 | NO | MEDIUM (진술 기록 endpoint 포함) | LOW | LOW | MEDIUM | LOW | 2 | MEDIUM | LOW | evidence LOW · plausibility LOW · 근거 CF024/CF044/V3P0053/V3P0148 — CF024(3/4 서찰)는 지시 이후의 일이고, CF044('구순 편을 듦')는 관계 판단이다. 3/4 이전 접촉을 적은 사료는 없다. |
| G04d | G04 | (없음 — 위쪽 원인 가설) | EP09 3월 4일 병사의 김생원 체포 지시 | 석단 공초가 3/4 이전 병사에게 보고되어 김명신 체포 지시로 이어졌다 | NO | MEDIUM (진술 기록 endpoint 포함) | LOW | MEDIUM | LOW | MEDIUM | 3 | MEDIUM | LOW | evidence LOW · plausibility LOW · 근거 V3P0089 — 05 한재욱 공초 속 유제희 발언(중첩, audit-only)에 석단 공초가 언급될 뿐, 시점·보고는 없다. |
| G04e | G04 | (없음 — 위쪽 원인 가설) | EP11 3월 4일 김명신·김갑득 체포 | 구순이 장교에게 직접 공식 체포 명령을 내렸다 | NO | MEDIUM (진술 기록 endpoint 포함) | NONE | INCOMPATIBLE | MEDIUM | LOW | 1 | HIGH | INCOMPATIBLE | evidence NONE · plausibility INCOMPATIBLE · 근거 없음 — 근거가 없고 CF023('병사의 분부에 따라')·제도(F007·F008)와 충돌한다. |
| G05a | G05 | EP10 3월 4일 조계완의 구순 집 방문과 서찰 | EP30 정조: 이광섭 책임 판단 | 조계완이 서찰을 병사에게 전달했고, 서찰 내용은 체포 지지·의혹 제기였다 | NO | MEDIUM (진술 기록 endpoint 포함) | LOW | MEDIUM | HIGH | MEDIUM | 2 | LOW | LOW | evidence LOW · plausibility MEDIUM · 근거 CF025 — 전달 여부와 서찰 내용은 어디에도 없다. CF024(서찰 수령·'바른 길' 발언)와 CF044(구순 편)는 endpoint(EP10·EP30)라 bridge 근거가 아니다. endpoint가 아닌 CF025(이형원: 허황한 말을 믿고)는 간접 정황일 뿐이다. |
| G05b | G05 | EP10 3월 4일 조계완의 구순 집 방문과 서찰 | (없음 — 위쪽 원인 가설) | 서찰은 전달되었으나 사건과 무관한 인사·사례였다 | NO | MEDIUM (진술 기록 endpoint 포함) | NONE | MEDIUM | HIGH | MEDIUM | 2 | LOW | LOW | evidence NONE · plausibility MEDIUM · 근거 없음 — 지지 근거가 없고 CF024의 맥락과 어울리지 않는다. |
| G06a | G06 | EP11 3월 4일 김명신·김갑득 체포 | EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고 | 김명신의 발병이 3/4 체포 이후 구금 중에 시작되었고 5/12 보고 이전에 죽었다 | PARTIAL | MEDIUM (진술 기록 endpoint 포함) | MEDIUM | HIGH | HIGH | HIGH | 1 | LOW | MEDIUM | evidence MEDIUM · plausibility HIGH · 근거 CF029/CF040/CF041 — endpoint가 아닌 CF029(윤노동 별단: '보수·구금 중 병들어 죽었다')가 구금 중 발병·사망을 보고 수준에서 지지한다. 다만 이것은 암행어사의 보고이고, 발병이 체포 '이후' 시작되었다는 시점 자체를 따로 확인한 문장은 없다. 그래서 HIGH가 아니라 MEDIUM이다. |
| G06b | G06 | EP11 3월 4일 김명신·김갑득 체포 | EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고 | 형장 없는 반복 조사 압박이 있었고 이어 발병해 죽었다 | NO | MEDIUM (진술 기록 endpoint 포함) | LOW | HIGH | HIGH | HIGH | 2 | MEDIUM | LOW | evidence LOW · plausibility HIGH · 근거 CF029 — 발병 부분은 CF029가 보고하지만, 이 후보가 새로 넣은 '반복 조사 압박'은 근거가 CF027('구금·조사', endpoint EP13)뿐이다. 게다가 CF041(평범한 신문 없음)과 긴장한다. |
| G06c | G06 | EP11 3월 4일 김명신·김갑득 체포 | EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고; EP27 정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음 | 김명신이 구금 중 형장을 받아 쇠약해진 뒤 죽었다 | NO | MEDIUM (진술 기록 endpoint 포함) | LOW | LOW | HIGH | MEDIUM | 2 | HIGH | LOW | evidence LOW · plausibility LOW · 근거 CF029/V3P0024 — CF029의 '여러 죄수 참혹한 형벌'은 열린 집합이라 김명신 포함을 지지하지 않는다. CF041(곤장 없음)과 정면 충돌한다. |
| G07a | G07 | EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고 | EP15 5월 12일 정조 1차 판단: 도난 부재 방향 | 5월 단계의 '도난 없음' 판단은 장물 미발견을 근거로 한 추론이었다 | NO | HIGH (공식 보고·판단·명령 endpoint) | LOW | HIGH | HIGH | HIGH | 1 | LOW | LOW | evidence LOW · plausibility HIGH · 근거 없음 — '장물 못 찾음'(CF027, EP13)과 '도난 없음 방향 수용'(CF030, EP15)은 각각 endpoint다. CF030의 '장계와 조사에 따라'라는 연결은 이미 observed edge OE040(REVIEW_OF)이 담고 있다. 이 후보가 새로 더한 것은 '그중 장물 부재가 이유였다'는 추론인데, 이를 적은 사료는 없다. |
| G07b | G07 | (없음 — 위쪽 원인 가설) | EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고; EP15 5월 12일 정조 1차 판단: 도난 부재 방향 | 이형원 회동 조사의 응답자 진술('구순이 꾸몄다')이 장계와 5/12 판단에 반영되었다 | PARTIAL | HIGH (공식 보고·판단·명령 endpoint) | MEDIUM | HIGH | HIGH | HIGH | 1 | LOW | MEDIUM | evidence MEDIUM · plausibility HIGH · 근거 V3P0009/V3P0115/V3P0116/V3P0117 — 05의 같은 장계 기사(SRC3_001)에 응답자 진술이 장계 내용으로 실려 있다(audit-only). 판단이 그 진술을 채택했다는 문장은 없지만 같은 기록 안의 연결이라 audit-only 상한인 MEDIUM이다. |
| G07c | G07 | (없음 — 위쪽 원인 가설) | EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고 | 명업 등의 번복 진술이 5월 판단 자료에 들어갔다 | NO | HIGH (공식 보고·판단·명령 endpoint) | LOW | MEDIUM | MEDIUM | MEDIUM | 2 | LOW | LOW | evidence LOW · plausibility MEDIUM · 근거 V3P0054/V3P0132 — 번복 자체는 05의 명업 공초(audit-only)에 있지만, 그것이 장계나 5월 판단 자료에 들어갔다는 내용은 없다. |
| G07d | G07 | (없음 — 위쪽 원인 가설) | EP15 5월 12일 정조 1차 판단: 도난 부재 방향; EP25 정조 최종 도난 판단: 실재 | 도난은 실제로 없었고 구순이 꾸몄다 | NO | HIGH (공식 보고·판단·명령 endpoint) | LOW | HIGH | HIGH | MEDIUM | 1 | HIGH | LOW | evidence LOW · plausibility MEDIUM · 근거 V3P0020/V3P0127 — 이조원·윤노동의 05 주장뿐이다. CF038·CF039(최종 판단)와 정면 충돌한다. |
| G08a | G08 | EP18 5월 27일 정조의 이조원 비판·파직 | EP20 5월 28일 홍대협 공주 안핵어사 차하 | 5/27 이조원의 직접 안핵 부재에 대한 정조의 비판이 5/28 홍대협 차하의 동기였다 | NO | HIGH (공식 보고·판단·명령 endpoint) | LOW | HIGH | HIGH | HIGH | 1 | LOW | LOW | evidence LOW · plausibility HIGH · 근거 V3P0028 — 두 행위(CF033 비판, CF035 차하)는 모두 endpoint다. 동기 문장은 01·04·05 어디에도 없다. 05 V3P0028도 비판 내용(endpoint와 같은 내용)일 뿐이다. 하루 차이라는 시간 인접성과 두 endpoint 내용의 주제 대응만으로는 bridge 근거가 되지 않는다. |
| G08b | G08 | (없음 — 위쪽 원인 가설) | EP20 5월 28일 홍대협 공주 안핵어사 차하 | 홍대협 차하의 주목적은 지세 호칭의 출처를 밝히는 것이었다 | NO | HIGH (공식 보고·판단·명령 endpoint) | LOW | HIGH | HIGH | HIGH | 1 | LOW | LOW | evidence LOW · plausibility HIGH · 근거 V3P0033/V3P0035 — 05 승정원일기 대화(V3P0033·V3P0035)는 5/28에 지세랑 호칭이 화제였음을 보이지만 '주목적'이라고 하지는 않는다. V3P0103(세 의안 분리)에 비추면 과장이다. |
| G09a | G09 | EP04 2월 28일 밤 병영 출동 준비; EP07 한 비장의 석방 조건 제시와 대질 시 거짓 진술 | EP35 병영 비장 한가 처분 | 한가(=한재욱) 처분의 근거는 자미덕이 진술한 회유·대질 지휘와 출동 운영이었다 | NO | MEDIUM (진술 기록 endpoint 포함) | LOW | HIGH | HIGH | HIGH | 1 | MEDIUM | LOW | evidence LOW · plausibility HIGH · 근거 CF044/V3P0042/V3P0128 — 처분 근거를 적은 문장이 없다. CF016·CF017·CF018·CF048은 endpoint(EP07·EP35 등)라 근거가 아니다. CF044와 05 윤노동 주장은 비장·회유를 말할 뿐 한가 처분과 연결하지 않는다. |
| G09b | G09 | EP04 2월 28일 밤 병영 출동 준비; EP07 한 비장의 석방 조건 제시와 대질 시 거짓 진술 | EP35 병영 비장 한가 처분 | 자미덕 진술의 '한 비장'은 한재욱과 다른 사람이고 한가 처분 근거는 출동 운영뿐이다 | NO | MEDIUM (진술 기록 endpoint 포함) | NONE | MEDIUM | HIGH | MEDIUM | 2 | MEDIUM | INCOMPATIBLE | evidence NONE · plausibility MEDIUM · 근거 없음 — 근거가 없고 사용자 확정 ID02와 충돌한다(INCOMPATIBLE). |
| G09c | G09 | (없음 — 위쪽 원인 가설) | EP35 병영 비장 한가 처분 | 한가는 한재욱이 아닌 다른 '한' 성 비장이다 | NO | HIGH (공식 보고·판단·명령 endpoint) | NONE | MEDIUM | HIGH | LOW | 3 | MEDIUM | INCOMPATIBLE | evidence NONE · plausibility LOW · 근거 없음 — 근거가 없고 사용자 확정 ID03과 충돌한다(INCOMPATIBLE). |
| G10a | G10 | EP25 정조 최종 도난 판단: 실재 | EP36 이형원 파직 | 이형원 파직 사유는 5/12 장계가 6/13 안핵 결과와 도난 여부에서 크게 달랐던 데 있다 | PARTIAL | HIGH (공식 보고·판단·명령 endpoint) | MEDIUM | HIGH | HIGH | HIGH | 1 | LOW | MEDIUM | evidence MEDIUM · plausibility HIGH · 근거 V3P0152 — 같은 6/13 기사에서 정조가 '도신 장계와 안핵어사 보고가 도난 여부에서 현격히 달랐다'고 지적했다(05 V3P0152, audit-only). 파직 사유라고 명시한 것은 아니므로 MEDIUM이다. G10은 사용자 검토로 OPEN_UNRESOLVED이며 어느 world에도 쓰지 않는다. |
| G10b | G10 | (없음 — 위쪽 원인 가설) | EP37 6월 16일 이형원 유임 | 유임 사유는 구휼·전염병 행정의 연속성이었다 | NO | HIGH (공식 보고·판단·명령 endpoint) | NONE | MEDIUM | MEDIUM | N/A | 2 | LOW | LOW | evidence NONE · plausibility MEDIUM · 근거 없음 — 환경 피쳐(E002·E003)만 근거이고 6월 상황을 적은 사료가 없다. |
| G10c | G10 | EP36 이형원 파직 | EP37 6월 16일 이형원 유임 | 파직 → 유임은 처분의 형식적 경감이었다 | NO | HIGH (공식 보고·판단·명령 endpoint) | NONE | MEDIUM | HIGH | N/A | 1 | LOW | LOW | evidence NONE · plausibility MEDIUM · 근거 없음 — 제도상 관행이라는 일반론뿐이다. |
| G11a | G11 | (없음 — 위쪽 원인 가설) | EP05 2월 29일 덕평 체포 활동 | 공주진이 같은 도난 사건 혐의로 변지돌을 2/29 이전에 먼저 체포했다 | NO | MEDIUM (진술 기록 endpoint 포함) | LOW | HIGH | HIGH | MEDIUM | 2 | LOW | LOW | evidence LOW · plausibility MEDIUM · 근거 CF009 — endpoint가 아닌 CF009(2/28 변지돌 체포 지시)는 변지돌이 이 사건 혐의자였음을 보여 줄 뿐이다. 공주진이 누구 판단으로 왜 잡았는지는 없다. CF011('이미 잡혀간 상태')은 endpoint(EP05)다. |
| G11b | G11 | (없음 — 위쪽 원인 가설) | EP05 2월 29일 덕평 체포 활동 | 병영이 2/28 이전 공주진에 변지돌 체포를 의뢰했다 | NO | MEDIUM (진술 기록 endpoint 포함) | NONE | HIGH | MEDIUM | MEDIUM | 2 | MEDIUM | LOW | evidence NONE · plausibility MEDIUM · 근거 없음 — 근거가 없고 CF009(2/28에 새로 체포 지시)와 긴장한다. |
| G11c | G11 | (없음 — 위쪽 원인 가설) | EP05 2월 29일 덕평 체포 활동 | 변지돌은 별건으로 공주진에 구금되어 있었다 | NO | MEDIUM (진술 기록 endpoint 포함) | NONE | HIGH | HIGH | N/A | 1 | LOW | LOW | evidence NONE · plausibility MEDIUM · 근거 없음 — 근거가 없다. |
| G12a | G12 | (없음 — 위쪽 원인 가설) | EP27 정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음 | 김명신의 아내도 전염병으로 죽었다(사건 수준) | PARTIAL | HIGH (공식 보고·판단·명령 endpoint) | LOW | N/A | MEDIUM | MEDIUM | 1 | LOW | LOW | evidence LOW · plausibility MEDIUM · 근거 V3P0025/V3P0123 — 아내의 사망 원인을 적은 것은 endpoint인 정조 판단(CF040, EP27) 자체뿐이다. 이 후보는 그 판단 내용을 사건으로 옮긴 것이라 endpoint 인용을 bridge 근거로 쓸 수 없다(판단 → 사실 전환 금지). 05 이조원 보고는 아내의 사망은 전하지만 원인은 '따라 죽었다'로 다르다. |
| G12b | G12 | (없음 — 위쪽 원인 가설) | EP27 정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음 | 아내는 전염병이 아니라 비통 속에 따라 죽었다 | NO | HIGH (공식 보고·판단·명령 endpoint) | LOW | N/A | MEDIUM | LOW | 1 | HIGH | LOW | evidence LOW · plausibility LOW · 근거 V3P0025/V3P0123 — 05 이조원 보고뿐이다. CF040(부처 전염병)과 정면 충돌한다. |
| G13a | G13 | EP16 5월 12일 정조 명: 구순 의금부 구금·엄사; EP19 5월 27일 정조 명: 구순 의금부 엄수·반복 신문 | EP32 정조: 구순 지세 호칭 날조 죄 불인정 | 의금부 구금·신문이 실제로 실행되었고, 지세 문제는 6/13까지 결론이 나지 않았다 | NO | HIGH (공식 보고·판단·명령 endpoint) | LOW | HIGH | HIGH | HIGH | 2 | LOW | LOW | evidence LOW · plausibility HIGH · 근거 V3P0137 — 명령(CF031·CF034)과 6/13 판단(CF045)은 endpoint다. 실행을 적은 사료가 없다. 05 V3P0137(홍대협: 의금부 국문이 필요하다)은 결론이 없었다는 정황일 뿐 실행 근거는 아니다. |
| G13b | G13 | EP16 5월 12일 정조 명: 구순 의금부 구금·엄사 | (없음 — 위쪽 원인 가설) | 의금부 신문은 6/13 이전에 실질적으로 진행되지 않았다 | NO | HIGH (공식 보고·판단·명령 endpoint) | NONE | MEDIUM | MEDIUM | MEDIUM | 1 | MEDIUM | LOW | evidence NONE · plausibility MEDIUM · 근거 없음 — 근거가 없고 CF034(반복 신문 명)와 긴장한다. |

## Narrative world 영향

| world | 최저 등급 이전 → 이후 | bridge 근거 등급 분포(이후) | bridge 구성 | 비고 |
|---|---|---|---|---|
| W1 | MEDIUM → LOW | MEDIUM 5 / LOW 7 | 그대로 |  |
| W2 | MEDIUM → LOW | MEDIUM 2 / LOW 7 | 그대로 |  |
| W3 | LOW → LOW | MEDIUM 2 / LOW 5 / NONE 1 | 그대로 |  |
| W4 | LOW → LOW | MEDIUM 3 / LOW 4 / NONE 1 | 그대로 |  |
| W5 | HIGH → LOW | MEDIUM 2 / LOW 2 | 그대로 | 설명 수정: 'HIGH 후보만' → '추가 가정이 가장 적은 world' |
| W6 | LOW → LOW | LOW 3 | 그대로 |  |

## 추가한 regression 규칙 (Audit 3)

- `bridge_support_inflation`: bridge 직접 근거가 없는데(NO) source support가 HIGH인 경우. bridge_evidence 없이 MEDIUM 이상인 경우. confirmed 비-endpoint 근거 없이 HIGH인 경우. final HIGH인데 evidence·plausibility가 모두 HIGH가 아닌 경우
- `temporal_inflation`: 근거 유형이 시간 인접·endpoint 내용뿐인데 MEDIUM 이상인 경우
- `institutional_inflation`: 근거 유형이 제도·환경 가능성뿐인데 MEDIUM 이상인 경우
- `endpoint_leakage`: endpoint node의 구성 fact를 bridge 근거로 인용한 경우
- `latent_classification`: bridge가 사료에 직접 있는(YES) LATENT 후보 — 분류 점검 대상

regression 케이스로 재감사 이전 값(예: G08a source HIGH)을 다시 넣으면 위 규칙이 ERROR를 내는지 build 때마다 확인한다.
