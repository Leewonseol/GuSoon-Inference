# Qualitative Interventions — do(M = OFF)

> 이 문서는 질적 메커니즘 분석이다. 메커니즘은 역사적 사실이 아니라 분석 변수다. World는 메커니즘의 configuration, Observed fact는 고정, Context feature는 제약조건, Latent bridge는 가설, Outcome(재검토·판단·처분)은 confirmed backbone이다. 확률·SEM 계수·practice prior는 쓰지 않았다.

정량 효과를 계산하지 않는다. 한 메커니즘을 끄면 같은 관측 전이를 설명하는 다른 경로가 남는지만 본다.

- PATH_REMAINS: 다른 메커니즘 후보가 같은 전이를 채울 수 있고, bridge 근거가 같거나 더 강함
- PATH_WEAKENS: 다른 경로가 남지만 남은 bridge 근거가 더 약함
- PATH_BREAKS: 그 전이를 채우는 후보가 이 메커니즘뿐임(관측 사건은 그대로이고, 그 앞의 설명만 비게 됨)
- UNKNOWN: 판단 근거 부족

| intervention | 구조 변수 | 관측 대상 | 결과 | 사라지는 후보 | 남는 후보 | 영향받는 world | 설명 |
|---|---|---|---|---|---|---|---|
| do(M1=OFF) | `V_COMPLAINT_TO_BARRACKS` | EP04 | **PATH_BREAKS** | G01a, G01b, G01c | - | W1, W2, W3, W4, W5 | 이 전이를 채우는 후보가 M1뿐이다(G01a, G01b, G01c). 관측 사건(EP04) 자체는 그대로지만, 그 앞의 설명 경로는 비게 된다(W5처럼 UNSPECIFIED). |
| do(M1=OFF) | `V_COMMAND_SOURCE` | EP04 | **PATH_WEAKENS** | G02a | G02b | W1, W2, W3, W4, W5 | 다른 메커니즘 후보(G02b)로 경로는 남지만, 남은 bridge 근거가 더 약하다 (제거 MEDIUM → 남은 최고 LOW). (XOR: G02a와 G02b는 서로 배타적이라 남은 쪽이 단독으로 설명한다.) |
| do(M1=OFF) | `V_INFO_TO_COMMANDER` | EP09 | **PATH_WEAKENS** | G03a, G03b, G04a | G03c, G04b, G04c, G04d | W1, W2, W3, W4, W5 | 다른 메커니즘 후보(G03c, G04b, G04c, G04d)로 경로는 남지만, 남은 bridge 근거가 더 약하다 (제거 MEDIUM → 남은 최고 LOW). |
| do(M2=OFF) | `V_INFO_TO_COMMANDER` | EP09 | **PATH_REMAINS** | G04b, G04d | G03a, G03b, G03c, G04a, G04c | W2, W4 | 다른 메커니즘 후보(G03a, G03b, G03c, G04a, G04c)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다. |
| do(M2=OFF) | `V_INVESTIGATION_SCOPE` | EP11 | **PATH_REMAINS** | G04b, G04d | G11a | W2, W4 | 다른 메커니즘 후보(G11a)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다. |
| do(M2=OFF) | `V_INITIAL_JUDGMENT_BASIS` | EP15 | **PATH_WEAKENS** | G07b, G07c | G07a | W2, W4 | 다른 메커니즘 후보(G07a)로 경로는 남지만, 남은 bridge 근거가 더 약하다 (제거 MEDIUM → 남은 최고 LOW). |
| do(M3=OFF) | `V_INFO_TO_COMMANDER` | EP09 | **PATH_REMAINS** | G04c | G03a, G03b, G03c, G04a, G04b, G04d | W1, W3 | 다른 메커니즘 후보(G03a, G03b, G03c, G04a, G04b, G04d)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다. |
| do(M4=OFF) | `V_COMMAND_SOURCE` | EP04 | **PATH_REMAINS** | G02b | G02a | W1, W2, W4 | 다른 메커니즘 후보(G02a)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다. (XOR: G02a와 G02b는 서로 배타적이라 남은 쪽이 단독으로 설명한다.) |
| do(M4=OFF) | `V_INFO_TO_COMMANDER` | EP09 | **PATH_REMAINS** | G03c | G03a, G03b, G04a, G04b, G04c, G04d | W1, W2, W4 | 다른 메커니즘 후보(G03a, G03b, G04a, G04b, G04c, G04d)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다. |
| do(M4=OFF) | `V_INVESTIGATION_SCOPE` | EP11 | **PATH_REMAINS** | G11a | G04b, G04d | W1, W2, W4 | 다른 메커니즘 후보(G04b, G04d)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다. |
| do(M5=OFF) | `V_REVIEW_CORRECTION` | EP25 | **PATH_BREAKS** | G08a, G08b, G13a | - | - | 재검토 경로는 관측 backbone(EP15 →REVISES→ EP25, EP23 → 판단·처분)이다. M5를 끄면 관측된 판단 수정·처분 경로를 설명할 수 없다. 관측 사실과 양립하지 않으므로 M5는 사실상 OFF로 둘 수 없다. |
| do(M6=OFF) | `V_INITIAL_JUDGMENT_BASIS` | EP15 | **PATH_REMAINS** | G07a | G07b, G07c | W1, W2, W3, W4, W5 | 다른 메커니즘 후보(G07b, G07c)가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다. |
| do(MB=OFF) | `V_CUSTODY_COURSE` | EP13 | **PATH_BREAKS** | G06a, G06b, G12a | - | W1, W2, W3, W4, W5 | 이 전이를 채우는 후보가 MB뿐이다(G06a, G06b, G12a). 관측 사건(EP13) 자체는 그대로지만, 그 앞의 설명 경로는 비게 된다(W5처럼 UNSPECIFIED). |

## 메커니즘별 요약

| intervention | 결과 요약 |
|---|---|
| do(M1=OFF) | V_COMPLAINT_TO_BARRACKS: PATH_BREAKS; V_COMMAND_SOURCE: PATH_WEAKENS; V_INFO_TO_COMMANDER: PATH_WEAKENS |
| do(M2=OFF) | V_INFO_TO_COMMANDER: PATH_REMAINS; V_INVESTIGATION_SCOPE: PATH_REMAINS; V_INITIAL_JUDGMENT_BASIS: PATH_WEAKENS |
| do(M3=OFF) | V_INFO_TO_COMMANDER: PATH_REMAINS |
| do(M4=OFF) | V_COMMAND_SOURCE: PATH_REMAINS; V_INFO_TO_COMMANDER: PATH_REMAINS; V_INVESTIGATION_SCOPE: PATH_REMAINS |
| do(M5=OFF) | V_REVIEW_CORRECTION: PATH_BREAKS |
| do(M6=OFF) | V_INITIAL_JUDGMENT_BASIS: PATH_REMAINS |
| do(MB=OFF) | V_CUSTODY_COURSE: PATH_BREAKS |

## world 안에서 보면

각 world는 gap마다 bridge를 하나만 쓴다. 그래서 그 world가 기대는 메커니즘을 끄면 world 안의 해당 설명은 비게 된다(영향받는 world 열). Super-DAG 수준에서는 다른 메커니즘이 같은 전이를 대신 설명할 수 있는지를 본다. 두 수준을 섞지 않는다.
