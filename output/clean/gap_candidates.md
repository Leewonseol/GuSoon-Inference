# STAGE 4 — Gap Detection + Latent Bridge Candidates

동결된 observed DAG에서 설명이 실제로 끊기는 곳만 gap으로 지정했다. **아래 후보는 모두 LATENT**이며 사료에서 확인된 사실이 아니다.

등급: HIGH / MEDIUM / LOW / INCOMPATIBLE. 확률이 아니다. overall은 다음 규칙으로 기계적으로 정한다. (1) 평가 차원 중 최소값, (2) contradiction_risk가 HIGH면 LOW 상한, MEDIUM이면 MEDIUM 상한, (3) 추가 가정 3개 이상이면 MEDIUM 상한, 5개 이상이면 LOW 상한, (4) HIGH는 source_consistency=HIGH일 때만, (5) 제도 compatibility 또는 환경 context만 근거인 후보는 LOW 상한, (6) 미확정 동일성(IDxx)에 기대는 후보는 MEDIUM 상한(동일성을 확정하지 않기 위해).

`audit_attestation`은 05(AUDIT_ONLY)에 그런 진술·주장이 **기록되어 있다**는 표시일 뿐이다. 후보를 OBSERVED로 올리지 않는다.

## Gap 요약

| gap | 유형 | 끊긴 구간 | 후보 수 | 최고 등급 |
|---|---|---|---|---|
| G01 | PROCEDURAL / INFORMATION_FLOW | EP03 ↔ EP04 | 3 | HIGH |
| G02 | ORDER_CHAIN | EP04 ↔ EP30 | 3 | MEDIUM |
| G03 | INFORMATION_FLOW / TEMPORAL | EP08 ↔ EP04 ↔ EP09 | 3 | MEDIUM |
| G04 | INFORMATION_FLOW (핵심) | EP08 ↔ EP07 ↔ EP10 ↔ EP09 | 5 | MEDIUM |
| G05 | INFORMATION_FLOW | EP10 ↔ EP30 | 2 | MEDIUM |
| G06 | TEMPORAL / PROCEDURAL | EP11 ↔ EP13 ↔ EP21 ↔ EP27 | 3 | HIGH |
| G07 | REVIEW / JUDGMENT_FORMATION | EP13 ↔ EP15 ↔ EP17 ↔ EP24 | 4 | HIGH |
| G08 | PROCEDURAL | EP18 ↔ EP20 | 2 | HIGH |
| G09 | IDENTITY / RESPONSIBILITY | EP35 ↔ EP07 ↔ EP12 ↔ EP04 | 3 | MEDIUM |
| G10 | DISPOSITION | EP36 ↔ EP37 | 3 | MEDIUM |
| G11 | PROCEDURAL | EP04 ↔ EP05 | 3 | MEDIUM |
| G12 | TEMPORAL / BIOLOGICAL | EP27 | 2 | MEDIUM |
| G13 | ORDER_TO_ACTION | EP16 ↔ EP19 ↔ EP29 | 2 | MEDIUM |

## G01 — 소장 접수 → 체포령 → 2/28 병영 출동의 연결

- 유형: PROCEDURAL / INFORMATION_FLOW
- 끊긴 구간: EP03 구순의 소장과 체포령 / EP04 2월 28일 밤 병영 출동 준비
- 관측 근거: CF006, CF007–CF010, CF026
- 왜 gap인가: 체포령(CF006)의 발령 기관과 2/28 병영 비장청 출동(CF007–010) 사이를 잇는 절차가 confirmed set에 없다. observed DAG에는 시간 edge(OE003)만 있다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G01a | 청주 진영 정소 → 진영이 병영 비장 쪽에 수사를 넘김 → 2/28 출동 | HIGH | HIGH | HIGH | HIGH | HIGH | N/A | LOW | 2 | **HIGH** | KEPT |
| G01b | 소장이 병영에 직접 접수 | MEDIUM | HIGH | HIGH | MEDIUM | MEDIUM | N/A | MEDIUM | 1 | **MEDIUM** | KEPT |
| G01c | 청주목 수령 → 관찰사 → 병영 이첩 | LOW | MEDIUM | HIGH | MEDIUM | MEDIUM | N/A | MEDIUM | 3 | **LOW** | KEPT_LOW (사용 시 약점 명시) |

### G01a [LATENT · MINI_DAG] 청주 진영 정소 → 진영이 병영 비장 쪽에 수사를 넘김 → 2/28 출동

구순의 소장이 청주 진영(영장 이문협)에 접수되었고, 진영은 수사를 병영 비장 쪽에 맡겼으며, 이것이 2/28 비장청 출동으로 이어졌다.

latent 요소:
- `LN_G01a_1` [LATENT] 구순의 소장이 청주 진영에 접수됨
- `LN_G01a_2` [LATENT] 진영이 도적 수사를 병영 비장 쪽에 넘김
- `EP03` —INFORMATION_FLOW→ `LN_G01a_1` (LATENT)
- `LN_G01a_1` —PROCEDURAL_NEXT→ `LN_G01a_2` (LATENT)
- `LN_G01a_2` —PROCEDURAL_NEXT→ `EP04` (LATENT)

- 추가 가정: 소장 접수처 = 청주 진영; 진영→병영 이관이 2/28 이전에 이루어짐
- 지지 fact: CF006, CF026(이문협이 수사를 병영 비장에게 전적으로 맡기고 방관) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0084|V3P0102
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 등급의 근거는 confirmed CF026이다(진영 영장이 수사를 병영 비장에게 맡김). 05의 V3P0084(한재욱 공초: '진영에 정소된 뒤')와 V3P0102(홍대협: 이문협이 병영 비장 지휘대로 죄를 얽음)는 audit-only 흔적이며 후보를 OBSERVED로 올리지 않는다.

### G01b [LATENT · SINGLE] 소장이 병영에 직접 접수

구순이 소장을 병영에 직접 올렸고, 병영이 체포령을 내려 2/28 출동했다.

latent 요소:
- `LN_G01b_1` [LATENT] 구순의 소장이 병영에 직접 접수되고 병영이 체포령 발령
- `EP03` —INFORMATION_FLOW→ `LN_G01b_1` (LATENT)
- `LN_G01b_1` —ORDER_TO_ACTION→ `EP04` (LATENT)

- 추가 가정: 소장 접수처 = 병영
- 지지 fact: CF006 · 긴장/충돌 fact: CF026(진영 영장 이문협이 왜 위임·방관으로 평가되었는지 설명되지 않음); 05 V3P0084(한재욱: '진영에 정소된 뒤' — audit-only, 반대 방향)
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 이 후보에서는 진영 영장 이문협이 왜 평가 대상이 되었는지 설명되지 않는다.

### G01c [LATENT · MINI_DAG] 청주목 수령 → 관찰사 → 병영 이첩

소장이 청주목 수령에게 접수되었고, 관찰사를 거쳐 병영으로 이첩되었다.

latent 요소:
- `LN_G01c_1` [LATENT] 소장이 청주목 수령에게 접수
- `LN_G01c_2` [LATENT] 관찰사가 병영에 이첩
- `EP03` —INFORMATION_FLOW→ `LN_G01c_1` (LATENT)
- `LN_G01c_1` —INFORMATION_FLOW→ `LN_G01c_2` (LATENT)
- `LN_G01c_2` —ORDER_TO_ACTION→ `EP04` (LATENT)

- 추가 가정: 접수처 = 수령; 관찰사 경유; 관찰사의 병영 이첩이 6일 안에 이루어짐
- 지지 fact: (제도 피쳐 F005·F006만) · 긴장/충돌 fact: CF027·CF025(이형원 장계에 자기 선행 관여 언급이 없음 — 약한 반증)
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: INSTITUTIONAL_COMPATIBILITY
- 메모: 제도적으로는 가능하지만 사료 지지가 없다. '제도 가능 ≠ 실제 발생'을 보여 주는 대조 후보다.

## G02 — 2/28 출동 지시의 상위 명령 출처

- 유형: ORDER_CHAIN
- 끊긴 구간: EP04 2월 28일 밤 병영 출동 준비 / EP30 정조: 이광섭 책임 판단
- 관측 근거: CF008–CF010, CF044, CF025, CF026
- 왜 gap인가: 이진욱 진술에서는 한재욱이 지시했다. 정조 판단에서는 이광섭이 철퇴를 만들게 했다. 한재욱 위에서 누가 명령했는지는 기록되지 않았다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G02a | 이광섭이 출동·철퇴 제작을 지시하고 한재욱이 실무 전달 (ID07 조건) | HIGH | HIGH | HIGH | HIGH | HIGH | N/A | LOW | 2 | **MEDIUM** | KEPT |
| G02b | 한재욱이 상위 명령 없이 출동 지시, 병영 지휘관은 사후 승인·묵인 | MEDIUM | HIGH | MEDIUM | MEDIUM | MEDIUM | N/A | MEDIUM | 3 | **MEDIUM** | KEPT |
| G02c | 청주 영장 이문협이 직접 출동 지휘 | LOW | MEDIUM | MEDIUM | LOW | LOW | N/A | HIGH | 1 | **LOW** | KEPT_AS_CONTRAST (관측·최종 판단과 충돌) |

### G02a [LATENT · SINGLE] 이광섭이 출동·철퇴 제작을 지시하고 한재욱이 실무 전달 (ID07 조건)

이광섭(CF025의 지휘 책임자)이 2/28 출동과 철퇴 네 개 제작을 지시했고, 한재욱은 그 지시를 장교들에게 전달·집행했다. 정조가 말한 '철퇴 네 개'(CF044)와 이진욱이 말한 '철편 네 개'(CF010)가 같은 물건일 때(ID07)만 성립한다.

latent 요소:
- `LN_G02a_1` [LATENT] 이광섭이 2/28 출동과 철퇴 네 개 제작을 지시
- `LN_G02a_1` —ORDER_TO_ACTION→ `EP04` (LATENT)

- 추가 가정: 철퇴 네 개(CF044) = 철편 네 개(CF010) (ID07); 철퇴 제작 지시와 같은 때 덕평 출동도 이광섭의 지시였음
- 지지 fact: CF044(이광섭이 철퇴 네 개를 만들게 함), CF025, CF010 · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0149
- 미확정 동일성 조건: ID07
- 주 근거 유형: SOURCE_DIRECT
- 메모: 정조 판단의 행위자(이광섭)와 진술의 행위자(한재욱)를 명령/집행 층위로 나누어 양쪽을 모두 살린다. V3P0149(05: '밤새 만들게 한')는 audit-only 흔적이다. 미확정 동일성(ID07)에 기대므로 MEDIUM 상한.

### G02b [LATENT · SINGLE] 한재욱이 상위 명령 없이 출동 지시, 병영 지휘관은 사후 승인·묵인

한재욱이 위에서 구체적인 명령을 받지 않고 자기 판단으로 2/28 출동을 지시했고, 병영 지휘관은 사후에 승인하거나 묵인했다. CF026·CF044의 '비장에게 맡김' 비판을 지휘 공백으로 읽는 후보다.

latent 요소:
- `LN_G02b_1` [LATENT] 한재욱이 상위 명령 없이 자체 판단으로 출동 지시
- `LN_G02b_2` [LATENT] 병영 지휘관의 사후 승인·묵인
- `LN_G02b_1` —ORDER_TO_ACTION→ `EP04` (LATENT)
- `EP04` —REVIEW_OF→ `LN_G02b_2` (LATENT)

- 추가 가정: 한재욱이 CF026·CF044가 말하는 '비장'의 위치에 있었음(직함은 confirmed set에 없음); 비장이 상위 명령 없이 출동을 지시할 수 있었음; 병영 지휘관의 사후 승인·묵인
- 지지 fact: CF026(비장에게 전적으로 맡김), CF044(비장에게 일을 맡겼다) · 긴장/충돌 fact: CF044(이광섭이 철퇴를 만들게 했다 — ID07이 성립하면 사전 관여를 시사)
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

### G02c [LATENT · SINGLE] 청주 영장 이문협이 직접 출동 지휘

진영 영장 이문협이 2/28 출동을 직접 지휘했다.

latent 요소:
- `LN_G02c_1` [LATENT] 이문협이 2/28 출동 직접 지휘
- `LN_G02c_1` —ORDER_TO_ACTION→ `EP04` (LATENT)

- 추가 가정: 영장이 병영 비장청 인원을 직접 지휘
- 지지 fact: - · 긴장/충돌 fact: CF026(이문협은 비장에게 맡기고 '방관'했다고 평가됨)
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 관측된 평가와 정면으로 충돌한다. 대조용.

## G03 — 유제희 탐문의 시점·파견자·기록 수신자

- 유형: INFORMATION_FLOW / TEMPORAL
- 끊긴 구간: EP08 유제희의 현지 탐문과 구순 발언 기록 / EP04 2월 28일 밤 병영 출동 준비 / EP09 3월 4일 병사의 김생원 체포 지시
- 관측 근거: CF020, CF009, CF021
- 왜 gap인가: CF020에는 날짜·파견자·수신자가 없다. 그래서 2/28 체포 대상 선정, 3/4 김생원 체포 지시와의 선후를 정할 수 없다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G03a | 한재욱이 유제희를 탐문에 보내고, 2/28 이전 기록이 한재욱에게 올라감 | MEDIUM | MEDIUM | HIGH | HIGH | HIGH | N/A | LOW | 3 | **MEDIUM** | KEPT |
| G03b | 탐문은 2/29~3/4 사이, 김상제(=김명신) 언급이 3/4 지시를 직접 촉발 | MEDIUM | MEDIUM | HIGH | HIGH | HIGH | N/A | MEDIUM | 2 | **MEDIUM** | KEPT |
| G03c | 유제희가 병사에게 직접 보고(비장 우회) | LOW | MEDIUM | MEDIUM | MEDIUM | MEDIUM | N/A | MEDIUM | 2 | **LOW** | KEPT_LOW (사용 시 약점 명시) |

### G03a [LATENT · MINI_DAG] 한재욱이 유제희를 탐문에 보내고, 2/28 이전 기록이 한재욱에게 올라감

한재욱이 유제희를 현지 탐문에 내보냈고, 유제희는 2/28 이전에 구순의 '풍각 김상제도 극히 수상하다'는 말을 원돌 등의 이름과 함께 기록해 한재욱에게 올렸다. 2/28 체포 대상(변지돌·정원돌) 선정에 이 기록이 쓰였다.

latent 요소:
- `LN_G03a_1` [LATENT] 한재욱이 유제희를 현지 탐문에 파견
- `LN_G03a_2` [LATENT] 유제희 기록이 2/28 이전 한재욱에게 전달
- `LN_G03a_1` —ORDER_TO_ACTION→ `EP08` (LATENT)
- `EP08` —INFORMATION_FLOW→ `LN_G03a_2` (LATENT)
- `LN_G03a_2` —INFORMATION_FLOW→ `EP04` (LATENT)

- 추가 가정: 파견자 = 한재욱 (05 V3P0085에만 있음); 탐문·기록 시점이 2/28 이전; 기록 수신자 = 한재욱
- 지지 fact: CF020('원돌 등의 이름과 함께'), CF009(정원돌 체포 지시) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0085|V3P0086|V3P0087
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 05 한재욱 공초(V3P0085–V3P0087, audit-only)는 자신이 유제희를 내보냈고 유제희가 변지돌·변재돌·정원돌·김명신 등의 성명을 적어 왔다고 진술한다. 이 후보는 그 진술을 사실로 올리지 않고 연결 가설로만 쓴다. 기록이 2/28 이전이라면 3/4 김생원 체포가 왜 2/28 대상에 없었는지는 이 후보로 설명되지 않는다. 원돌=정원돌은 ID11 사용자 확정(RESOLVED)이라 가정에서 뺐다(가정 4→3). 후보 자체는 여전히 LATENT이며 source_consistency(MEDIUM)는 그대로다.

### G03b [LATENT · SINGLE] 탐문은 2/29~3/4 사이, 김상제(=김명신) 언급이 3/4 지시를 직접 촉발

유제희의 탐문과 기록은 2/29 이후 3/4 이전에 있었고, 기록 속 '풍각 김상제' 언급이 3/4 풍각 김생원 체포 지시를 직접 촉발했다.

latent 요소:
- `LN_G03b_1` [LATENT] 유제희 기록이 2/29~3/4 사이에 병영에 보고
- `EP08` —INFORMATION_FLOW→ `LN_G03b_1` (LATENT)
- `LN_G03b_1` —INFORMATION_FLOW→ `EP09` (LATENT)

- 추가 가정: 탐문 시점 2/29~3/4; 기록이 병사 지시 판단에 쓰임
- 지지 fact: CF043, CF020 · 긴장/충돌 fact: CF020('원돌 등'과 한 기록 — ID11 확정: 원돌(=정원돌)은 이미 2/28 체포 대상이었으므로 기록이 2/28 이전이라는 쪽과 긴장)
- audit_attestation (05, AUDIT_ONLY): V3P0095
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

### G03c [LATENT · SINGLE] 유제희가 병사에게 직접 보고(비장 우회)

유제희가 탐문 결과를 비장을 거치지 않고 병사에게 직접 올렸다.

latent 요소:
- `LN_G03c_1` [LATENT] 유제희 기록이 병사에게 직접 보고
- `EP08` —INFORMATION_FLOW→ `LN_G03c_1` (LATENT)
- `LN_G03c_1` —INFORMATION_FLOW→ `EP09` (LATENT)

- 추가 가정: 수신자 = 병사; 비장 계통 우회
- 지지 fact: - · 긴장/충돌 fact: 05 V3P0085(한재욱: 유제희를 자신이 내보냈다 — audit-only)와 긴장
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

## G04 — 구순의 발언·성명 → 3/4 병사 체포 지시까지의 정보 경로

- 유형: INFORMATION_FLOW (핵심)
- 끊긴 구간: EP08 유제희의 현지 탐문과 구순 발언 기록 / EP07 한 비장의 석방 조건 제시와 대질 시 거짓 진술 / EP10 3월 4일 조계완의 구순 집 방문과 서찰 / EP09 3월 4일 병사의 김생원 체포 지시
- 관측 근거: CF020, CF016, CF021, CF043
- 왜 gap인가: 정조는 '성명 제공 → 횡액'의 책임 사슬을 판단했다(CF043). 그러나 observed DAG에서 EP08(구순 발언 기록)과 EP09(병사 지시) 사이에는 event 수준 edge가 없다. 사용자 지정 branch B의 '→ 병영 수사선상' 단계가 여기서 끊긴다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G04a | 공식 정보 경로: 유제희 기록 → 비장 계통 → 병사 → 3/4 지시 | HIGH | MEDIUM | HIGH | HIGH | HIGH | N/A | LOW | 2 | **MEDIUM** | KEPT |
| G04b | 자미덕 대질 진술 경로: 회유 주장 진술(열린 목록) → 병사 지시 | MEDIUM | MEDIUM | MEDIUM | MEDIUM | MEDIUM | N/A | MEDIUM | 3 | **MEDIUM** | KEPT |
| G04c | 사적 경로: 3/4 이전 구순→병사 사적 접촉으로 김명신을 의심 대상으로 알림 | LOW | MEDIUM | LOW | LOW | LOW | N/A | MEDIUM | 2 | **LOW** | KEPT_LOW (사용 시 약점 명시) |
| G04d | 석단 공초 경로: 다른 피의자 공초가 김명신을 도적 괴수로 지목 | LOW | LOW | MEDIUM | MEDIUM | MEDIUM | N/A | MEDIUM | 3 | **LOW** | KEPT_LOW (사용 시 약점 명시) |
| G04e | 구순이 장교에게 직접 공식 체포 명령 | INCOMPATIBLE | MEDIUM | INCOMPATIBLE | INCOMPATIBLE | LOW | N/A | HIGH | 1 | **INCOMPATIBLE** | PRUNED (incompatible) |

### G04a [LATENT · MINI_DAG] 공식 정보 경로: 유제희 기록 → 비장 계통 → 병사 → 3/4 지시

구순이 '풍각 김상제도 극히 수상하다'고 한 말이 유제희의 기록으로 병영 비장 계통에 들어갔고, 비장 계통이 병사에게 보고해 3/4 풍각 김생원 체포 지시의 근거가 되었다. 풍각 김상제=김명신은 ID05 사용자 확정이다. 보고 경로는 가설이다.

latent 요소:
- `LN_G04a_1` [LATENT] 유제희 기록이 비장 계통을 거쳐 병사에게 보고됨
- `EP08` —INFORMATION_FLOW→ `LN_G04a_1` (LATENT)
- `LN_G04a_1` —INFORMATION_FLOW→ `EP09` (LATENT)

- 추가 가정: 병영의 염탐 담당자 = 유제희 (ID06) — 정조 판단(CF043)과 대응시킬 때; 기록이 3/4 이전 비장 계통을 거쳐 병사에게 보고됨
- 지지 fact: CF043(성명 제공 → 횡액), CF020, CF044(비장에게 일을 맡김) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0038|V3P0095
- 미확정 동일성 조건: ID06
- 주 근거 유형: SOURCE_DIRECT
- 메모: 정조의 책임 사슬(CF043)을 event 수준으로 펼친 것이다. 정조는 '구순이 적어 주었다', 유제희는 '자신이 기록했다'고 했다. 이 차이는 해소하지 않는다.

### G04b [LATENT · MINI_DAG] 자미덕 대질 진술 경로: 회유 주장 진술(열린 목록) → 병사 지시

자미덕은 구류 중 한 비장이 정원돌·이집거·김갑득·김성손·김흥득 '등'을 큰 도적이라고 말하라고 했고, 대질 때 그 지휘에 따라 거짓으로 꾸며 말했다고 진술했다(EP07). 이 후보는 그 대질 진술이 3/4 이전 병사에게 보고되어 흥덕 김생원(김갑득)과 풍각 김생원 체포 지시의 근거가 되었다고 가정한다.

latent 요소:
- `LN_G04b_1` [LATENT] 자미덕의 대질 진술이 3/4 이전 병사에게 보고됨
- `EP07` —INFORMATION_FLOW→ `LN_G04b_1` (LATENT)
- `LN_G04b_1` —INFORMATION_FLOW→ `EP09` (LATENT)

- 추가 가정: 대질 진술이 3/4 이전에 있었음; 그 진술이 병사에게 보고됨; 열린 목록 '등'에 풍각 김생원이 들어 있었음(05 V3P0042·V3P0128 윤노동 주장, audit-only)
- 지지 fact: CF016(김갑득이 명시 명단에 있고, 3/4 김명신과 함께 체포됨 — CF023) · 긴장/충돌 fact: CF018(한재욱: 은밀한 사주 부인 — claim-level. ID02 확정으로 같은 인물에 대한 서로 다른 진술)
- audit_attestation (05, AUDIT_ONLY): V3P0042|V3P0089|V3P0128
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 제도 평가: 진술 → 보고 → 지시라는 정보 경로 자체는 F008·F020과 양립하므로 institutional_fit은 MEDIUM이다. 회유 행위의 합법성 LOW(F002)는 observed node EP07의 feature link에 이미 붙어 있다. 윤노동 별단(05)은 한재욱이 변가의 처를 꾀어 김명신이 도적 괴수라는 공초를 내게 했다고 주장하지만 audit-only이며, 이 후보는 그 주장을 사실로 올리지 않는다.

### G04c [LATENT · SINGLE] 사적 경로: 3/4 이전 구순→병사 사적 접촉으로 김명신을 의심 대상으로 알림

3/4 이전에 구순이 병사에게 사적 서신이나 접촉으로 김명신을 의심 대상으로 알렸고, 병사가 그 정보에 기대어 체포를 지시했다.

latent 요소:
- `LN_G04c_1` [LATENT] 3/4 이전 구순이 병사에게 사적으로 김명신을 의심 대상으로 알림
- `EP01` —CONTEXT_SUPPORTS→ `LN_G04c_1` (LATENT)
- `LN_G04c_1` —INFORMATION_FLOW→ `EP09` (LATENT)

- 추가 가정: 3/4 이전의 미기록 서신·접촉 존재; 그 내용에 김명신 지목
- 지지 fact: CF024(3/4 서찰 — 사적 통로가 있었음을 보여 줌), CF044(구순 편을 듦) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0053|V3P0148
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: CF024의 서찰은 '잡으러 가는 길'에 건넨 것이라 3/4 지시보다 뒤다. 그래서 이 후보는 그보다 앞선, 기록되지 않은 접촉을 따로 가정해야 한다. 05의 V3P0053(명업: 구순이 찾아온 장교 한 명과 안행랑에서 조용히 대화)과 V3P0148(정조: 이광섭이 구순과의 오래된 혐의를 씻은 뒤 구순 편을 듦)은 audit-only 흔적이다. 구순에게는 공식 지휘권이 없으므로 '명령'이 아니라 정보 제공으로만 표현했다(F007·F020 LOW).

### G04d [LATENT · SINGLE] 석단 공초 경로: 다른 피의자 공초가 김명신을 도적 괴수로 지목

석단이라는 피의자의 공초에서 김명신이 도적 괴수로 언급되었고, 이것이 병사 지시로 이어졌다.

latent 요소:
- `LN_G04d_1` [LATENT] 석단 공초가 3/4 이전에 병사에게 보고됨
- `LN_G04d_1` —INFORMATION_FLOW→ `EP09` (LATENT)

- 추가 가정: 석단 공초 시점이 3/4 이전; 석단 공초 내용(유제희 발언의 중첩 진술); 병사에게 보고
- 지지 fact: - · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0089
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: confirmed set에 석단은 나오지 않는다. 05의 한재욱 공초 속 유제희 발언(중첩)이 유일한 흔적이다.

### G04e [LATENT · SINGLE] 구순이 장교에게 직접 공식 체포 명령

구순이 장교들에게 김명신 체포를 직접 명령했다.

latent 요소:
- `LN_G04e_1` [LATENT] 구순이 장교에게 체포 명령
- `LN_G04e_1` —ORDER_TO_ACTION→ `EP11` (LATENT)

- 추가 가정: 전 부사 구순이 병영 장교 지휘권 보유
- 지지 fact: - · 긴장/충돌 fact: CF023(장교 일행은 '병사의 분부에 따라' 체포)
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: NONE
- 메모: 제도(F007·F008)와 관측(CF023) 모두와 충돌한다. pruning 예시(사용자 지정: 구순→장교 공식 체포명령 low).

## G05 — 3/4 구순 서찰의 전달과 내용

- 유형: INFORMATION_FLOW
- 끊긴 구간: EP10 3월 4일 조계완의 구순 집 방문과 서찰 / EP30 정조: 이광섭 책임 판단
- 관측 근거: CF024, CF044
- 왜 gap인가: 서찰을 건넨 사실(CF024)과 '이광섭이 구순 편을 들었다'는 판단(CF044) 사이에 전달·내용이 기록되지 않았다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G05a | 서찰이 병사에게 전달, 체포 지지·추가 의혹 내용 | MEDIUM | HIGH | MEDIUM | MEDIUM | MEDIUM | N/A | LOW | 2 | **MEDIUM** | KEPT |
| G05b | 서찰은 전달되었으나 사건과 무관한 인사·사례 | LOW | HIGH | MEDIUM | MEDIUM | MEDIUM | N/A | LOW | 2 | **LOW** | KEPT_LOW (사용 시 약점 명시) |

### G05a [LATENT · SINGLE] 서찰이 병사에게 전달, 체포 지지·추가 의혹 내용

조계완이 서찰을 병사에게 전달했고, 서찰 내용은 김명신 체포를 지지하거나 의혹을 덧붙이는 것이었다. 병사=이광섭(ID01, 사용자 확정)이므로 이 서찰은 정조가 말한 '이광섭이 구순 편을 들었다'(CF044)의 한 배경이 된다. 전달과 내용은 가설이다.

latent 요소:
- `LN_G05a_1` [LATENT] 조계완이 서찰을 병사에게 전달
- `LN_G05a_2` [LATENT] 서찰 내용 = 체포 지지·의혹 제기
- `EP10` —INFORMATION_FLOW→ `LN_G05a_1` (LATENT)
- `LN_G05a_1` —INFORMATION_FLOW→ `LN_G05a_2` (LATENT)
- `LN_G05a_2` —CONTEXT_SUPPORTS→ `EP30` (LATENT)

- 추가 가정: 서찰 전달됨; 서찰 내용이 사건 관련
- 지지 fact: CF024('바른 길을 얻었다'는 반응), CF044(구순 편을 듦), CF025(허황한 말을 믿고) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 사적 서찰은 공식 보고 경로(장계·서계)가 아니다. 공식 명령으로서는 LOW(F020)지만, 이 후보는 '사적 정보 전달'만 가정하므로 institutional_fit을 MEDIUM으로 둔다(전달을 막는 제도도, 공식 경로라는 근거도 없음).

### G05b [LATENT · SINGLE] 서찰은 전달되었으나 사건과 무관한 인사·사례

서찰은 전달되었지만 내용은 인사나 사례 정도였고 수사에는 영향을 주지 않았다.

latent 요소:
- `LN_G05b_1` [LATENT] 서찰 전달, 내용은 사건 무관
- `EP10` —INFORMATION_FLOW→ `LN_G05b_1` (LATENT)

- 추가 가정: 서찰 전달됨; 내용 무관
- 지지 fact: - · 긴장/충돌 fact: CF024의 맥락(체포 직전 '도적 다스리는 일이 바른 길을 얻었다')과 어울리지 않음
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

## G06 — 3/4 체포 ~ 사망(5/12 보고 이전) 사이 구금 경과

- 유형: TEMPORAL / PROCEDURAL
- 끊긴 구간: EP11 3월 4일 김명신·김갑득 체포 / EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고 / EP21 6월 11일 윤노동 별단 / EP27 정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음
- 관측 근거: CF023, CF027, CF029, CF040, CF041
- 왜 gap인가: 체포일(3/4)과 사망 보고(5/12) 사이 약 두 달 동안 발병 시점, 처우, 사망 시점·장소가 기록되지 않았다. 5/12 '구금·조사'와 6/13 '평범한 신문도 없음'이 긴장 관계다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G06a | 구금 중 발병 → 보수·구금 상태에서 사망 (처우는 CF041 판단을 따름) | HIGH | HIGH | HIGH | HIGH | HIGH | HIGH | LOW | 1 | **HIGH** | KEPT |
| G06b | 형장 없는 조사 압박 + 발병 → 사망 | MEDIUM | HIGH | HIGH | HIGH | HIGH | HIGH | MEDIUM | 2 | **MEDIUM** | KEPT |
| G06c | 형장(곤장) → 쇠약 → 사망 | LOW | HIGH | LOW | MEDIUM | MEDIUM | MEDIUM | HIGH | 2 | **LOW** | KEPT_AS_CONTRAST (관측·최종 판단과 충돌) |

### G06a [LATENT · MINI_DAG] 구금 중 발병 → 보수·구금 상태에서 사망 (처우는 CF041 판단을 따름)

김명신은 3/4 체포 뒤 병영 구금 중 병이 났고, 보수·구금 상태에서 5/12 보고 이전에 죽었다. 처우는 정조 판단(CF041: 곤장·평문 없음)을 따른다.

latent 요소:
- `LN_G06a_1` [LATENT] 김명신이 구금 중 발병
- `LN_G06a_2` [LATENT] 보수·구금 상태에서 5/12 이전 사망
- `EP11` —PROCEDURAL_NEXT→ `LN_G06a_1` (LATENT)
- `LN_G06a_1` —TEMPORAL_BEFORE→ `LN_G06a_2` (LATENT)
- `LN_G06a_2` —INFORMATION_FLOW→ `EP13` (LATENT)

- 추가 가정: 발병이 체포 이후
- 지지 fact: CF029(보수·구금 중 병들어 죽음), CF040, CF041 · 긴장/충돌 fact: CF027('구금·조사' — PARTIAL)
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 개인 발병의 근거는 관측 보고 CF029(윤노동)와 판단 CF040이다. 환경(E001·E003)은 environmental_fit 평가에만 썼고 발병 node를 만들지 않았다. '보수'의 법적 의미는 해석하지 않는다.

### G06b [LATENT · MINI_DAG] 형장 없는 조사 압박 + 발병 → 사망

김명신은 형장은 받지 않았지만 구금 중 반복 조사 압박을 받았고, 이어 발병해 죽었다.

latent 요소:
- `LN_G06b_1` [LATENT] 형장 없는 조사 압박
- `LN_G06b_2` [LATENT] 구금 중 발병·사망
- `EP11` —PROCEDURAL_NEXT→ `LN_G06b_1` (LATENT)
- `LN_G06b_1` —TEMPORAL_BEFORE→ `LN_G06b_2` (LATENT)
- `LN_G06b_2` —INFORMATION_FLOW→ `EP13` (LATENT)

- 추가 가정: 반복 조사 압박; 발병이 체포 이후
- 지지 fact: CF027(달포 이상 구금·조사), CF029 · 긴장/충돌 fact: CF041(평범한 신문도 받지 않았다 — royal judgment)
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

### G06c [LATENT · MINI_DAG] 형장(곤장) → 쇠약 → 사망

김명신은 구금 중 형장을 받아 쇠약해졌고, 그 뒤 죽었다.

latent 요소:
- `LN_G06c_1` [LATENT] 김명신이 구금 중 형장을 받음
- `LN_G06c_2` [LATENT] 쇠약 후 사망
- `EP11` —PROCEDURAL_NEXT→ `LN_G06c_1` (LATENT)
- `LN_G06c_1` —TEMPORAL_BEFORE→ `LN_G06c_2` (LATENT)
- `LN_G06c_2` —INFORMATION_FLOW→ `EP13` (LATENT)
- `LN_G06c_1` —CONTRADICTS_AT_CLAIM_LEVEL→ `EP27` (LATENT)

- 추가 가정: 김명신이 형장 대상에 포함; 형장이 사망 경과에 관여
- 지지 fact: CF028·CF029(평민·여러 죄수의 혹형 — 열린 집합) · 긴장/충돌 fact: CF041(곤장을 맞지 않았다), CF040
- audit_attestation (05, AUDIT_ONLY): V3P0024
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 열린 집합('무고한 평민들', '여러 죄수')에 김명신을 넣어야 성립한다. 최종 royal judgment와 정면으로 충돌한다.

## G07 — 5월 '도난 없음 방향' 판단의 형성 경로

- 유형: REVIEW / JUDGMENT_FORMATION
- 끊긴 구간: EP13 5월 12일 이형원 장계: 구금·무장물·사망·혹형 보고 / EP15 5월 12일 정조 1차 판단: 도난 부재 방향 / EP17 5월 27일 암행어사 이조원 보고: 도난 부재 방향 / EP24 홍대협 도난 판단: 약간의 실제 도난, 좀도둑 수준
- 관측 근거: CF027, CF030, CF032, CF038
- 왜 gap인가: 5/12·5/27 판단이 왜 '도난 없음' 쪽으로 기울었는지(6/13에 번복됨) 근거 경로가 confirmed set에 없다. 이조원은 전문(傳聞) 의존(CF033)이 관측되어 있으나 이형원 장계 쪽 경로는 비어 있다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G07a | 장물 미발견을 근거로 '도난 없음'을 추론 | HIGH | HIGH | HIGH | HIGH | HIGH | N/A | LOW | 1 | **HIGH** | KEPT |
| G07b | 회동 조사 응답자들의 '구순이 꾸몄다' 진술 채택 | MEDIUM | HIGH | HIGH | HIGH | HIGH | N/A | LOW | 1 | **MEDIUM** | KEPT |
| G07c | 구순 집 사람들의 진술 번복이 5월 자료에 들어감 | MEDIUM | MEDIUM | MEDIUM | MEDIUM | MEDIUM | N/A | LOW | 2 | **MEDIUM** | KEPT |
| G07d | 도난은 실제로 없었고 구순이 꾸몄다 (이조원·윤노동 주장) | LOW | HIGH | HIGH | MEDIUM | MEDIUM | N/A | HIGH | 1 | **LOW** | KEPT_AS_CONTRAST (관측·최종 판단과 충돌) |

### G07a [LATENT · SINGLE] 장물 미발견을 근거로 '도난 없음'을 추론

5월 단계의 조사자들은 확실한 장물을 찾지 못한 것을 근거로 도난 자체가 없었다고 추론했고, 정조가 이를 받아들였다.

latent 요소:
- `LN_G07a_1` [LATENT] 장물 부재 → 도난 부재 추론
- `EP13` —INFORMATION_FLOW→ `LN_G07a_1` (LATENT)
- `LN_G07a_1` —INFORMATION_FLOW→ `EP15` (LATENT)

- 추가 가정: 장물 부재가 도난 부재 추론의 근거로 쓰임
- 지지 fact: CF027(확실한 장물을 찾지 못함), CF030(장계와 조사에 따라) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

### G07b [LATENT · SINGLE] 회동 조사 응답자들의 '구순이 꾸몄다' 진술 채택

이형원의 회동 조사에서 응답자들이 구순이 도난 상황을 꾸몄다고 진술했고(05 V3P0009, audit-only), 장계와 5/12 판단이 그 진술을 채택했다.

latent 요소:
- `LN_G07b_1` [LATENT] 회동 조사 응답자 진술이 장계에 반영
- `LN_G07b_1` —INFORMATION_FLOW→ `EP13` (LATENT)
- `LN_G07b_1` —INFORMATION_FLOW→ `EP15` (LATENT)

- 추가 가정: 회동 조사 응답 내용이 판단 근거로 쓰임
- 지지 fact: CF030('조사에 따라') · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0009|V3P0115|V3P0116|V3P0117
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 응답 내용은 05에만 있다(중첩 진술). 응답 내용의 진위는 다루지 않는다. 도난 부재 쪽 결론은 6/13 판단으로 수정된다(CF038·CF039).

### G07c [LATENT · SINGLE] 구순 집 사람들의 진술 번복이 5월 자료에 들어감

명업 등 구순 집 사람들이 병영 뜰 공초에서 '도적이 없었다'는 취지로 진술을 바꾸었고(명업은 위협이 두려워서였다고 진술 — 05), 그 번복 진술이 5월 판단 자료에 들어갔다.

latent 요소:
- `LN_G07c_1` [LATENT] 명업 등의 번복 진술이 5월 판단 자료에 포함
- `LN_G07c_1` —INFORMATION_FLOW→ `EP13` (LATENT)

- 추가 가정: 번복 진술이 장계 자료에 포함; 번복 시점이 5/12 이전
- 지지 fact: CF038(정식 안핵에서 약간의 실제 도난 확인) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0054|V3P0132
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: '위협' 부분은 명업 자신의 진술(05 V3P0054)이며 사실로 올리지 않는다.

### G07d [LATENT · SINGLE] 도난은 실제로 없었고 구순이 꾸몄다 (이조원·윤노동 주장)

도난 자체가 없었고 구순이 상황을 꾸며 김명신을 얽었다(이조원·윤노동의 05 주장).

latent 요소:
- `LN_G07d_1` [LATENT] 도난 부재·구순이 상황을 꾸밈
- `LN_G07d_1` —CONTEXT_SUPPORTS→ `EP15` (LATENT)
- `LN_G07d_1` —CONTRADICTS_AT_CLAIM_LEVEL→ `EP25` (LATENT)

- 추가 가정: 도난 날조
- 지지 fact: - · 긴장/충돌 fact: CF038(약간의 실제 도난), CF039(정조 최종: 도난 실재)
- audit_attestation (05, AUDIT_ONLY): V3P0020|V3P0127
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 5월 단계 판단과 같은 방향이다. 최종 official·royal finding과 정면으로 충돌하므로 대조용으로만 둔다.

## G08 — 5/27 이조원 비판 → 5/28 홍대협 차하의 동기

- 유형: PROCEDURAL
- 끊긴 구간: EP18 5월 27일 정조의 이조원 비판·파직 / EP20 5월 28일 홍대협 공주 안핵어사 차하
- 관측 근거: CF033, CF035
- 왜 gap인가: 하루 차이의 두 royal action 사이에 동기 연결 문장이 없다(OE045는 시간 edge뿐).

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G08a | 직접 안핵 부재 비판 → 독립 안핵 결정 | HIGH | HIGH | HIGH | HIGH | HIGH | N/A | LOW | 1 | **HIGH** | KEPT |
| G08b | 지세 호칭 의문 해소가 주목적 | MEDIUM | HIGH | HIGH | HIGH | HIGH | N/A | LOW | 1 | **MEDIUM** | KEPT |

### G08a [LATENT · MINI_DAG] 직접 안핵 부재 비판 → 독립 안핵 결정

정조는 이조원이 직접 안핵하지 않은 점을 문제 삼았고(관측, CF033), 그 판단이 다음 날 독립 안핵어사 차하(관측, CF035)의 동기가 되었다는 연결만 LATENT다.

latent 요소:
- `LN_G08a_1` [LATENT] 정조가 이조원 서계의 직접 안핵 부재를 근거로 현지 직접 안핵이 필요하다고 판단
- `EP18` —INFORMATION_FLOW→ `LN_G08a_1` (LATENT)
- `LN_G08a_1` —PROCEDURAL_NEXT→ `EP20` (LATENT)

- 추가 가정: 5/27 비판이 5/28 차하의 동기
- 지지 fact: CF033(직접 안핵하지 않은 점 문제 삼음), CF035(자세히 조사해 오라) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0028
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 동기 연결은 원본(CF033·CF035·SRC3_004)에 문장으로 없으므로 LATENT다. 관측 node끼리 직접 잇지 않고 latent 판단 node를 사이에 둔다(Audit 3 WARN A3-W1 처리). observed DAG의 OE045(TEMPORAL_BEFORE, DERIVED)는 그대로다.

### G08b [LATENT · SINGLE] 지세 호칭 의문 해소가 주목적

정조가 홍대협을 보낸 주목적은 지세 호칭의 출처를 밝히는 것이었다.

latent 요소:
- `LN_G08b_1` [LATENT] 정조의 지세 호칭 의문
- `LN_G08b_1` —INFORMATION_FLOW→ `EP20` (LATENT)

- 추가 가정: 지세 의문이 차하의 주목적
- 지지 fact: CF045(지세 기원 조사) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0033|V3P0035|V3P0103
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 정조가 6/13에 세 의안(도난·사인·지세)을 나누었으므로(V3P0103) '주목적'이라고 하면 과장일 수 있다.

## G09 — 처분문 '한가'의 처분 근거와 동일성

- 유형: IDENTITY / RESPONSIBILITY
- 끊긴 구간: EP35 병영 비장 한가 처분 / EP07 한 비장의 석방 조건 제시와 대질 시 거짓 진술 / EP12 한재욱의 안핵 공초 / EP04 2월 28일 밤 병영 출동 준비
- 관측 근거: CF048, CF016, CF017, CF018, CF008
- 왜 gap인가: 한가 처분(CF048)에 연결된 책임 판단 node가 없다. 한가=한재욱=한 비장은 사용자 확정(ID02·ID03 RESOLVED)이지만, 한가 처분의 근거 행위는 기록되지 않았다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G09a | 한가(=한재욱) 처분 근거 = 자미덕이 진술한 회유·대질 지휘와 출동 운영 | MEDIUM | HIGH | HIGH | HIGH | HIGH | N/A | MEDIUM | 1 | **MEDIUM** | KEPT |
| G09b | 한가 = 한재욱, '한 비장'은 다른 사람 (ID02 확정과 충돌) | LOW | HIGH | MEDIUM | MEDIUM | MEDIUM | N/A | MEDIUM | 2 | **INCOMPATIBLE** | PRUNED (사용자 확정 동일성 ID02과 충돌) |
| G09c | 한가는 한재욱이 아닌 다른 '한' 성 비장 (ID03 확정과 충돌) | LOW | HIGH | MEDIUM | LOW | LOW | N/A | MEDIUM | 3 | **INCOMPATIBLE** | PRUNED (사용자 확정 동일성 ID03과 충돌) |

### G09a [LATENT · SINGLE] 한가(=한재욱) 처분 근거 = 자미덕이 진술한 회유·대질 지휘와 출동 운영

ID02(한 비장=한재욱)와 ID03(한가=한재욱)은 사용자 확정(RESOLVED)이다. 따라서 처분문의 병영 비장 한가, 자미덕 진술 속 '한 비장', 2/28 출동을 지시한 한재욱은 같은 사람이다. 처분 근거가 자미덕이 진술한 회유·대질 지휘와 출동 운영이라는 것만 가설이다. 회유는 자미덕의 진술이고 한재욱은 은밀한 사주를 부인했으므로(CF018), 사주를 사실로 확정하지 않는다.

latent 요소:
- `LN_G09a_1` [LATENT] 한가(=한재욱) 처분 근거 = 자미덕이 진술한 회유·대질 지휘와 출동 운영
- `EP07` —RESPONSIBILITY_LINK→ `LN_G09a_1` (LATENT)
- `EP04` —RESPONSIBILITY_LINK→ `LN_G09a_1` (LATENT)
- `LN_G09a_1` —PROCEDURAL_NEXT→ `EP35` (LATENT)

- 추가 가정: 처분 근거 행위 = 자미덕이 진술한 회유·대질 지휘와 출동 운영
- 지지 fact: CF048(병영 비장 한가), CF016·CF017(한 비장), CF018(한재욱이 자미덕을 방으로 부름) · 긴장/충돌 fact: CF018(은밀한 사주 부인 — claim-level)
- audit_attestation (05, AUDIT_ONLY): V3P0042|V3P0112|V3P0128
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: ID02·ID03 사용자 확정으로 동일성 가정 2개를 뺐다(가정 3→1). source_consistency MEDIUM과 contradiction_risk MEDIUM 때문에 등급은 MEDIUM 그대로다.

### G09b [LATENT · MINI_DAG] 한가 = 한재욱, '한 비장'은 다른 사람 (ID02 확정과 충돌)

한가=한재욱이고 자미덕을 회유했다는 '한 비장'은 별인이라고 가정한다. 그 경우 처분 근거는 출동·철편 운영이다. 이 전제(ID02 불성립)는 사용자가 확정한 ID02(한 비장=한재욱)와 충돌한다.

latent 요소:
- `LN_G09b_1` [LATENT] 자미덕 진술 속 '한 비장'은 별도의 '한' 성 비장
- `LN_G09b_2` [LATENT] 한가 처분 근거 = 출동·철편 운영
- `EP07` —CONTEXT_SUPPORTS→ `LN_G09b_1` (LATENT)
- `EP04` —RESPONSIBILITY_LINK→ `LN_G09b_2` (LATENT)
- `LN_G09b_2` —PROCEDURAL_NEXT→ `EP35` (LATENT)

- 추가 가정: 한 비장 ≠ 한재욱 (ID02 불성립, 별도 인물 존재); 처분 근거 = 출동 운영만
- 지지 fact: - · 긴장/충돌 fact: CF018(한재욱이 자미덕을 방으로 불렀다고 인정 — 한 비장과의 대응을 시사)
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: ID02
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

### G09c [LATENT · SINGLE] 한가는 한재욱이 아닌 다른 '한' 성 비장 (ID03 확정과 충돌)

처분된 한가는 한재욱이 아닌, 기록되지 않은 다른 '한' 성 비장이다. 이 전제(ID03 불성립)는 사용자가 확정한 ID03(한가=한재욱)과 충돌한다.

latent 요소:
- `LN_G09c_1` [LATENT] 기록되지 않은 다른 '한' 성 비장
- `LN_G09c_1` —PROCEDURAL_NEXT→ `EP35` (LATENT)

- 추가 가정: 한가 ≠ 한재욱 (ID03 불성립); 미기록 인물 존재; 그 인물의 처분 근거 행위
- 지지 fact: - · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: ID03
- 주 근거 유형: SOURCE_DIRECT
- 메모: 새 인물을 도입해야 하므로 가정 비용이 크다.

## G10 — 이형원 6/13 파직 → 6/16 유임

- 유형: DISPOSITION
- 끊긴 구간: EP36 이형원 파직 / EP37 6월 16일 이형원 유임
- 관측 근거: CF049, CF050
- 왜 gap인가: 파직과 3일 뒤 유임의 사유가 모두 기록되지 않았다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G10a | 파직 사유 = 장계와 안핵 결과의 차이 | MEDIUM | HIGH | HIGH | HIGH | HIGH | N/A | LOW | 1 | **MEDIUM** | KEPT |
| G10b | 유임 사유 = 구휼·전염병 행정 연속성 | LOW | MEDIUM | MEDIUM | MEDIUM | N/A | MEDIUM | LOW | 2 | **LOW** | KEPT_LOW (사용 시 약점 명시) |
| G10c | 파직 → 유임은 처분의 형식적 경감 | LOW | HIGH | MEDIUM | MEDIUM | N/A | N/A | LOW | 1 | **LOW** | KEPT_LOW (사용 시 약점 명시) |

### G10a [LATENT · SINGLE] 파직 사유 = 장계와 안핵 결과의 차이

이형원의 5/12 장계가 6/13 안핵 결과와 도난 여부에서 크게 달랐던 것이 파직 사유였다. 유임 사유는 남겨 둔다.

latent 요소:
- `LN_G10a_1` [LATENT] 파직 사유 = 장계 판단 오류
- `EP25` —REVIEW_OF→ `LN_G10a_1` (LATENT)
- `LN_G10a_1` —PROCEDURAL_NEXT→ `EP36` (LATENT)

- 추가 가정: 장계 오류가 파직 사유
- 지지 fact: CF030→CF039 판단 번복, CF049 · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0152
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: V3P0152(05: 정조가 도신 장계와 안핵 보고가 현격히 달랐다고 지적)는 audit-only다. 그 지적이 파직 사유라는 문장은 어디에도 없다.

### G10b [LATENT · SINGLE] 유임 사유 = 구휼·전염병 행정 연속성

구휼과 전염병 대응이 진행 중이어서 행정 연속성을 위해 3일 만에 유임했다.

latent 요소:
- `LN_G10b_1` [LATENT] 유임 사유 = 행정 연속성
- `LN_G10b_1` —CONTEXT_SUPPORTS→ `EP37` (LATENT)

- 추가 가정: 6월에도 구휼·전염병 행정 부담 지속; 그것이 유임 판단에 쓰임
- 지지 fact: - · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: ENVIRONMENTAL_CONTEXT
- 메모: 환경 피쳐(E002는 1월, E003은 4월)만 근거다. 6월 지속 여부는 pack에 없다. 환경만 근거이므로 LOW 상한이며, 개인 수준 사건이 아닌 판단 사유 가설(individual_level=False)이다.

### G10c [LATENT · SINGLE] 파직 → 유임은 처분의 형식적 경감

파직은 문책의 형식이었고 곧바로 유임으로 실무를 이어가게 했다.

latent 요소:
- `LN_G10c_1` [LATENT] 형식적 파직 후 유임
- `EP36` —PROCEDURAL_NEXT→ `LN_G10c_1` (LATENT)
- `LN_G10c_1` —PROCEDURAL_NEXT→ `EP37` (LATENT)

- 추가 가정: 형식적 처분 관행
- 지지 fact: - · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: INSTITUTIONAL_COMPATIBILITY
- 메모: 제도 compatibility(F018 수교)만 근거이므로 LOW 상한.

## G11 — 변지돌의 공주진 선행 체포 경위

- 유형: PROCEDURAL
- 끊긴 구간: EP04 2월 28일 밤 병영 출동 준비 / EP05 2월 29일 덕평 체포 활동
- 관측 근거: CF009, CF011
- 왜 gap인가: 2/28 체포 지시 대상(변지돌)이 2/29에는 이미 공주진에 잡혀가 있었다. 누가 왜 잡았는지 비어 있다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G11a | 공주진이 같은 도난 사건으로 먼저 체포 | MEDIUM | HIGH | HIGH | HIGH | MEDIUM | N/A | LOW | 2 | **MEDIUM** | KEPT |
| G11b | 병영이 2/28 이전 공주진에 체포 의뢰 | LOW | MEDIUM | HIGH | MEDIUM | MEDIUM | N/A | MEDIUM | 2 | **LOW** | KEPT_LOW (사용 시 약점 명시) |
| G11c | 변지돌은 별건으로 공주진에 구금 중 | LOW | HIGH | HIGH | MEDIUM | N/A | N/A | LOW | 1 | **LOW** | KEPT_LOW (사용 시 약점 명시) |

### G11a [LATENT · SINGLE] 공주진이 같은 도난 사건으로 먼저 체포

공주진이 같은 도난 사건의 혐의로 변지돌을 2/29 이전에 먼저 체포했다.

latent 요소:
- `LN_G11a_1` [LATENT] 공주진의 변지돌 선행 체포(같은 사건)
- `LN_G11a_1` —TEMPORAL_BEFORE→ `EP05` (LATENT)

- 추가 가정: 같은 사건 혐의; 공주진의 독자 판단
- 지지 fact: CF011(이미 잡혀간 상태), CF009(변지돌이 체포 대상) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

### G11b [LATENT · SINGLE] 병영이 2/28 이전 공주진에 체포 의뢰

병영이 2/28 이전에 공주진에 변지돌 체포를 의뢰했다.

latent 요소:
- `LN_G11b_1` [LATENT] 병영→공주진 체포 의뢰
- `LN_G11b_1` —TEMPORAL_BEFORE→ `EP05` (LATENT)

- 추가 가정: 병영의 선행 의뢰; 2/28에 이미 의뢰한 사람을 다시 체포 지시
- 지지 fact: - · 긴장/충돌 fact: CF009(2/28에 변지돌 체포를 새로 지시 — 의뢰 사실을 몰랐다는 것과 긴장)
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

### G11c [LATENT · SINGLE] 변지돌은 별건으로 공주진에 구금 중

변지돌은 이 도난과 무관한 별건으로 이미 공주진에 잡혀 있었다.

latent 요소:
- `LN_G11c_1` [LATENT] 변지돌 별건 구금
- `LN_G11c_1` —TEMPORAL_BEFORE→ `EP05` (LATENT)

- 추가 가정: 별건 혐의 존재
- 지지 fact: - · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

## G12 — 김명신 아내의 사망 경로

- 유형: TEMPORAL / BIOLOGICAL
- 끊긴 구간: EP27 정조 사인·처우 판단: 부처 전염병 사망, 곤장·평문 없음
- 관측 근거: CF040
- 왜 gap인가: 정조는 '부처'가 전염병으로 죽었다고 판단했으나 아내의 사망은 다른 어떤 observed node에도 나오지 않는다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G12a | 아내도 전염병으로 사망(시점 미상) | HIGH | MEDIUM | N/A | N/A | MEDIUM | HIGH | LOW | 1 | **MEDIUM** | KEPT |
| G12b | 아내는 남편 사망 뒤 비통 속에 '따라 죽음'(전염병 아님) | LOW | MEDIUM | N/A | N/A | LOW | MEDIUM | HIGH | 1 | **LOW** | KEPT_AS_CONTRAST (관측·최종 판단과 충돌) |

### G12a [LATENT · SINGLE] 아내도 전염병으로 사망(시점 미상)

김명신의 아내도 같은 시기 전염병에 걸려 죽었다. 감염 경로와 정확한 시점은 남겨 둔다.

latent 요소:
- `LN_G12a_1` [LATENT] 김명신 아내의 전염병 사망
- `LN_G12a_1` —INFORMATION_FLOW→ `EP27` (LATENT)

- 추가 가정: 아내의 사망이 남편 사망과 같은 시기(전후 미상)
- 지지 fact: CF040(정조: 김명신 부처가 전염병으로 죽음) · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0025|V3P0123
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: royal judgment를 event 수준으로 옮긴 최소 후보다. 개인 사건의 근거는 CF040(판단)이며 환경은 environmental_fit에만 쓴다. 이조원(05)은 '따라 죽었다'고 표현했다.

### G12b [LATENT · SINGLE] 아내는 남편 사망 뒤 비통 속에 '따라 죽음'(전염병 아님)

아내는 남편의 죽음 뒤 비통 속에 따라 죽었고, 전염병 때문이 아니었다.

latent 요소:
- `LN_G12b_1` [LATENT] 아내의 비전염병 사망
- `LN_G12b_1` —CONTRADICTS_AT_CLAIM_LEVEL→ `EP27` (LATENT)

- 추가 가정: 사망 원인이 전염병이 아님
- 지지 fact: - · 긴장/충돌 fact: CF040(부처 전염병 사망 — royal judgment)
- audit_attestation (05, AUDIT_ONLY): V3P0025|V3P0123
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 

## G13 — 구순 의금부 구금·신문 명령의 실행

- 유형: ORDER_TO_ACTION
- 끊긴 구간: EP16 5월 12일 정조 명: 구순 의금부 구금·엄사 / EP19 5월 27일 정조 명: 구순 의금부 엄수·반복 신문 / EP29 정조: 구순 책임 연결 판단
- 관측 근거: CF031, CF034, CF043
- 왜 gap인가: 5/12·5/27 두 차례 명령(order)은 관측되지만 실행·신문 결과(action)는 confirmed set에 없다.

| 후보 | 요약 | src | temp | inst | role | info | env | 충돌위험 | 가정 | overall | 처리 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G13a | 의금부 구금·신문 실행, 지세 문제는 6/13까지 결론 없음 | MEDIUM | HIGH | HIGH | HIGH | HIGH | N/A | LOW | 2 | **MEDIUM** | KEPT |
| G13b | 의금부 신문은 6/13 이전에 실질적으로 진행되지 않음 | LOW | MEDIUM | MEDIUM | HIGH | MEDIUM | N/A | MEDIUM | 1 | **LOW** | KEPT_LOW (사용 시 약점 명시) |

### G13a [LATENT · SINGLE] 의금부 구금·신문 실행, 지세 문제는 6/13까지 결론 없음

구순은 의금부에 구금되어 신문을 받았지만, 지세 호칭 문제는 6/13까지 결론이 나지 않았다.

latent 요소:
- `LN_G13a_1` [LATENT] 구순 의금부 구금·신문 실행
- `EP16` —ORDER_TO_ACTION→ `LN_G13a_1` (LATENT)
- `EP19` —ORDER_TO_ACTION→ `LN_G13a_1` (LATENT)
- `LN_G13a_1` —INFORMATION_FLOW→ `EP32` (LATENT)

- 추가 가정: 명령이 실행됨; 신문 결과가 6/13 판단에 쓰임
- 지지 fact: CF031, CF034, CF045 · 긴장/충돌 fact: -
- audit_attestation (05, AUDIT_ONLY): V3P0137
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 홍대협이 6/13에 '지세 실정을 밝히려면 의금부 엄한 국문이 필요하다'고 건의했다(05). 그때까지 결론이 없었음을 시사한다.

### G13b [LATENT · SINGLE] 의금부 신문은 6/13 이전에 실질적으로 진행되지 않음

구순은 구금되었으나 안핵 결과를 기다리느라 본격 신문은 이루어지지 않았다.

latent 요소:
- `LN_G13b_1` [LATENT] 의금부 구금만 되고 신문은 보류
- `EP16` —ORDER_TO_ACTION→ `LN_G13b_1` (LATENT)

- 추가 가정: 신문 보류
- 지지 fact: - · 긴장/충돌 fact: CF034(반복 신문하도록 명함)
- audit_attestation (05, AUDIT_ONLY): -
- 미확정 동일성 조건: 없음
- 주 근거 유형: SOURCE_DIRECT
- 메모: 
