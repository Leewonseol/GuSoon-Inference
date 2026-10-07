# Qualitative Structural Rules (질적 구조방정식)

> 이 문서는 질적 메커니즘 분석이다. 메커니즘은 역사적 사실이 아니라 분석 변수다. World는 메커니즘의 configuration, Observed fact는 고정, Context feature는 제약조건, Latent bridge는 가설, Outcome(재검토·판단·처분)은 confirmed backbone이다. 확률·SEM 계수·practice prior는 쓰지 않았다.

아래 식은 '실제로 그렇게 됐다'는 역사적 단정이 아니다. '이런 메커니즘 조합이면 현재 관측 경로를 설명할 수 있다'는 구조적 표현이다.
OR = 어느 하나만 있어도 그 전이를 설명할 수 있음(대체 관계). AND = 모두 필요함. XOR = 서로 배타적인 설명. ANCHORED = 관측 backbone에 고정되어 world마다 달라지지 않음.

| 구조 변수 | 설명하는 관측 전이 | 규칙 | 연산 | 입력 후보(분석 사용분, bridge 근거) | 제도·환경 제약 |
|---|---|---|---|---|---|
| `V_COMPLAINT_TO_BARRACKS` | 소장·체포령(EP03)이 2/28 병영 출동(EP04)으로 이어지는 경로 → EP04 | V_COMPLAINT_TO_BARRACKS = M1_OFFICIAL_INFORMATION_ROUTE | OR | G01a(M1 MEDIUM), G01b(M1 NONE), G01c(M1 NONE) | F005·F006·F010(접수·이첩 경로의 제도 가능성) |
| `V_COMMAND_SOURCE` | 2/28 출동 지시의 상위 출처 → EP04 | V_COMMAND_SOURCE = M1_OFFICIAL_INFORMATION_ROUTE(G02a: 병사 지시) XOR M4_DISTRIBUTED_INSTITUTIONAL_ACTION(G02b: 비장 자체 판단) | XOR | G02a(M1 MEDIUM), G02b(M4 LOW) | F007·F008·F009(병사 → 비장·장교 지휘의 제도 가능성) |
| `V_INFO_TO_COMMANDER` | 구순 쪽 정보·진술이 3/4 병사의 체포 지시(EP09)에 닿는 경로 → EP09 | V_INFO_TO_COMMANDER = M1 OR M2 OR M3 OR M4  (각각 G04a·G03a·G03b / G04b·G04d / G04c / G03c) | OR | G03a(M1 MEDIUM), G03b(M1 LOW), G03c(M4 NONE), G04a(M1 MEDIUM), G04b(M2 LOW), G04c(M3 LOW), G04d(M2 LOW) | F007·F020(구순은 명령 불가, 정보 제공만) · F008(보고 경로) |
| `V_ARREST_PATH` | 체포 지시(EP09, OBSERVED) → 체포 실행(EP11, OBSERVED) → EP11 | V_ARREST_PATH = V_INFO_TO_COMMANDER AND INSTITUTIONALLY_COMPATIBLE(F007·F008: 병사 → 장교 명령) | AND | - | F007·F008 |
| `V_INVESTIGATION_SCOPE` | 수사 범위가 여러 혐의자로 넓어지는 구조(김갑득 동시 체포, 공주진 선행 체포 등) → EP11 | V_INVESTIGATION_SCOPE = M2_TESTIMONY_AMPLIFICATION OR M4_DISTRIBUTED_INSTITUTIONAL_ACTION | OR | G04b(M2 LOW), G04d(M2 LOW), G11a(M4 LOW) | F010(도적 수색 관할) · F002(진술 획득 방식의 규범) |
| `V_INITIAL_JUDGMENT_BASIS` | 5/12 '도난 없음 방향' 판단(EP15, OBSERVED)의 근거 형성 → EP15 | V_INITIAL_JUDGMENT_BASIS = M6_INITIAL_JUDGMENT_BASIS OR M2_TESTIMONY_AMPLIFICATION(보조: G07b·G07c) | OR | G07a(M6 LOW), G07b(M2 MEDIUM), G07c(M2 LOW) | F006·F020(장계 → 국왕 판단) |
| `V_REVIEW_CORRECTION` | 5/12 판단 → 5/27 → 5/28 → 6/11 → 6/13 → 처분으로 이어진 독립 재검토·판단 수정(OBSERVED backbone) → EP25 | V_REVIEW_CORRECTION = M5_REVIEW_AND_CORRECTION  (관측 backbone: EP15 →REVISES→ EP25 등. world마다 달라지지 않음) | ANCHORED | G08a(M5 LOW), G08b(M5 LOW), G13a(M5 LOW) | F012·F013·F014·F017·F018 |
| `V_RESPONSIBILITY` | 정조의 책임 귀속(EP29·EP30, OBSERVED) → EP29, EP30 | V_RESPONSIBILITY = V_REVIEW_CORRECTION AND V_ARREST_PATH  (책임 판단은 절차 branch B에만 의존, 사인과 무관) | AND | - | F018 |
| `V_SANCTION` | 처분(OBSERVED, 모든 world 공통) → EP33, EP34, EP35, EP36, EP37 | V_SANCTION = V_RESPONSIBILITY  (처분은 관측 사실. G10 사유는 OPEN_UNRESOLVED) | ANCHORED | - | F001·F006·F018 |
| `V_CUSTODY_COURSE` | 구금 중 발병·사망 경과(사망 branch A). 책임 branch와 연결하지 않음 → EP13 | V_CUSTODY_COURSE = MB_CUSTODY_BIOLOGICAL_COURSE  (환경 E001–E004는 호환성 context. 개인 감염 확정 아님) | OR | G06a(MB MEDIUM), G06b(MB LOW), G12a(MB LOW) | F002·F003·F004·F015·F016 / E001–E004(context) |

## 규칙 사이의 연결

```
V_COMPLAINT_TO_BARRACKS → V_COMMAND_SOURCE → V_INFO_TO_COMMANDER → V_ARREST_PATH ─┐
                                                                                ├→ V_RESPONSIBILITY → V_SANCTION
V_INITIAL_JUDGMENT_BASIS → (EP15, OBSERVED) → V_REVIEW_CORRECTION (M5, ANCHORED) ─┘

V_CUSTODY_COURSE (MB, 사망 branch A) → EP13 사망 보고   ※ V_RESPONSIBILITY와 연결하지 않음
```

## 해석 원칙

- 체포 지시(EP09)·체포(EP11)·5월 판단(EP15)·재검토·최종 판단·처분은 OBSERVED다. 규칙은 그 앞의 빈 전이만 설명한다.
- `V_INFO_TO_COMMANDER`는 OR다. M1·M2·M3·M4 가운데 어느 것으로도 설명할 수 있다. 어느 쪽이 실제로 작동했는지는 사료가 결정하지 않는다(Audit 4 UNRESOLVED).
- `V_COMMAND_SOURCE`는 XOR다. G02a(병사 지시, M1)와 G02b(상위 명령 없는 비장 자체 판단, M4)는 함께 참일 수 없다.
- `INSTITUTIONALLY_COMPATIBLE`은 F007·F008(병사 → 장교 명령)의 제도 적합성이다. 이것이 참이라고 체포가 일어난 것은 아니다. 체포는 관측 사실이다.
- M3(사적 통로)는 F007상 '명령'이 될 수 없다. 정보·영향 입력으로만 V_INFO_TO_COMMANDER에 들어간다(G04e INCOMPATIBLE).
- 환경 E001–E004는 MB에 CONTEXT_COMPATIBLE로만 연결된다. 개인 감염 사건을 만들지 않는다.
- 책임(V_RESPONSIBILITY)은 절차 branch에만 의존한다. 사인(V_CUSTODY_COURSE)과 서로 연결하지 않는다. 구순 → 김명신 사망의 직접 edge는 없다.
