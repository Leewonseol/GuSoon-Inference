# 07. 반사실 분석 (자동 생성)

> 생성기: `03_constraints.py`. 결과는 **가능성 의미론**(어떤 외생 조건 조합에서 성립할 수 있는가)이며 확률이 아니다. 관찰 자료가 없으므로 모든 결론은 `03_constraints.py`의 구조방정식(SCM)에 종속된다.

## 방법

- **개입(do)**: 개입 변수가 내생이면 그 구조방정식을 절단하고 값을 고정한다(Pearl, 2009). 외생이면 값만 고정한다.
- **관찰 조건화**: 구조방정식과 극중 필수 조건을 모두 유지한 채 값을 '관찰'로 추가한다. 개입과 결과가 다를 수 있으며, 아래에 함께 표시한다.
- **유지 제약**: 모형 구조(STR) 전부 + 사료 인과 사실(HIST_C)·극중 필수(FILM_REQ) 중 개입 변수의 후손이나 질문한 결과를 직접 고정하지 않는 것.
- **추가 가정**: 결과가 참이 되려면 *반드시* 참이어야 하는 극중 가정 중, 기준선에서 이미 필요한 것을 뺀 것.

## Q1. 조재항이 최상층 토호여서 권분을 회피할 수 있었다면?

- 변경한 변수: `e5_cannot_evade`=False (외생변수 값 설정(do))
- 고정(유지)한 제약: 모형 구조 15개, 사료 인과 사실 HC_SONG, HC_INSTIGATION, HC_ACCUSATION, HC_OKSA, HC_NO_DIRECT_REINVEST, HC_HWAN_ILL, HC_BOKGEOM_NOT_CORRECTED, HC_CHOGEOM_ERROR, 극중 필수 FR_ORDER, FR_EVALUATOR, FR_RELIEF_BEFORE_POPHYEOM, FR_HOSTILITY_BEFORE_DEATH, FR_HWAN_ACCUSES, FR_JSJ_MOTIVE
- 이 질문을 위해 풀어 둔 제약: 극중 필수 FR_DUAL_OUTCOME, FR_INVESTIGABLE / 사료 인과 사실 없음
- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.
- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: 성립

| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |
|---|---|---|---|
| `burden_concentrated` | 가능(참·거짓 모두 성립) | 불가능(필연적으로 거짓) | 해당 없음(불가능) |
| `econ_refusal` | 가능(참·거짓 모두 성립) | 불가능(필연적으로 거짓) | 해당 없음(불가능) |
| `yun_refuses` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `u_yun_other_reason`(윤씨의 비경제적 거절 사유) |
| `hostility_to_yun` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `u_yun_other_reason`(윤씨의 비경제적 거절 사유) |
| `murder_by_residents` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `u_trigger`(살인을 촉발한 구체적 사건), `u_yun_other_reason`(윤씨의 비경제적 거절 사유) |

**모형상 결과**: 조재항이 회피 가능한 최상층 토호라면 모형상 '부담 집중'과 '경제적 거절 사유'는 사라진다. 윤씨에 대한 책임 전가는 여전히 가능하지만, 그 경우 거절 사유를 비경제적 동기(`u_yun_other_reason`)로 새로 만들어야 한다.

**해석 한계**: 부담 집중 식(`u_shortage ∧ e5 ∧ u_elite_evade`)은 이세영(2009)의 계층별 부담 차이 '요약'에 기댄 극중 가정이며 논문 원문은 미열람이다.

## Q2. 조재항에게 부담이 집중되지 않았다면(부담 집중에 직접 개입)?

- 변경한 변수: `burden_concentrated`=False (do() 개입(내생변수: 구조방정식 절단))
- 고정(유지)한 제약: 모형 구조 15개, 사료 인과 사실 HC_SONG, HC_INSTIGATION, HC_ACCUSATION, HC_OKSA, HC_NO_DIRECT_REINVEST, HC_HWAN_ILL, HC_BOKGEOM_NOT_CORRECTED, HC_CHOGEOM_ERROR, 극중 필수 FR_ORDER, FR_EVALUATOR, FR_RELIEF_BEFORE_POPHYEOM, FR_HOSTILITY_BEFORE_DEATH, FR_HWAN_ACCUSES, FR_JSJ_MOTIVE
- 이 질문을 위해 풀어 둔 제약: 극중 필수 FR_DUAL_OUTCOME, FR_INVESTIGABLE / 사료 인과 사실 없음
- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.
- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: 성립

| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |
|---|---|---|---|
| `econ_refusal` | 가능(참·거짓 모두 성립) | 불가능(필연적으로 거짓) | 해당 없음(불가능) |
| `yun_refuses` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `u_yun_other_reason`(윤씨의 비경제적 거절 사유) |
| `hostility_to_yun` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `u_yun_other_reason`(윤씨의 비경제적 거절 사유) |

**모형상 결과**: 부담 집중에 직접 개입하면 경제적 거절 사유는 불가능해진다. 거절·적대는 비경제적 거절 사유를 추가해야만 남는다.

**해석 한계**: 구조방정식 절단(do)과 관찰 조건화의 차이: 관찰로 '부담 집중 없음'을 보면 그 원인(회피 가능성 등)도 함께 갱신되지만, 개입은 원인을 그대로 둔다.

## Q3. 권중립이 자발적 권분만 시행했다면?

- 변경한 변수: `kjr_coercive`=False (외생변수 값 설정(do))
- 고정(유지)한 제약: 모형 구조 15개, 사료 인과 사실 HC_SONG, HC_INSTIGATION, HC_ACCUSATION, HC_OKSA, HC_NO_DIRECT_REINVEST, HC_HWAN_ILL, HC_BOKGEOM_NOT_CORRECTED, HC_CHOGEOM_ERROR, 극중 필수 FR_ORDER, FR_EVALUATOR, FR_RELIEF_BEFORE_POPHYEOM, FR_HOSTILITY_BEFORE_DEATH, FR_HWAN_ACCUSES, FR_JSJ_MOTIVE
- 이 질문을 위해 풀어 둔 제약: 극중 필수 FR_DUAL_OUTCOME, FR_INVESTIGABLE / 사료 인과 사실 없음
- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.
- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: 성립

| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |
|---|---|---|---|
| `entitlement_framing` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `lgw_selective`(이가원의 선택적 정보 공개) |
| `hostility_to_yun` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `lgw_selective`(이가원의 선택적 정보 공개) |
| `kjr_cover_motive` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | 없음 |
| `murder_by_residents` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `lgw_selective`(이가원의 선택적 정보 공개), `u_trigger`(살인을 촉발한 구체적 사건) |

**모형상 결과**: 자발적 권분만 시행해도 적대는 성립할 수 있으나, 그 경우 주민의 '관의 뜻' 명분은 이가원의 선택적 정보 공개(`lgw_selective`)가 필요조건이 된다. 권중립의 방어 동기도 실적 과장·책임 전가 경로로 남을 수 있다.

**해석 한계**: 명분(entitlement_framing) 식은 이론적 제안이다. 1780년 배천에서 강제 권분이 있었다는 직접 사료는 없다.

## Q4. 권중립이 윤씨에게 책임을 전가하지 않았다면?

- 변경한 변수: `kjr_shifts_blame`=False (외생변수 값 설정(do))
- 고정(유지)한 제약: 모형 구조 15개, 사료 인과 사실 HC_SONG, HC_INSTIGATION, HC_ACCUSATION, HC_OKSA, HC_NO_DIRECT_REINVEST, HC_HWAN_ILL, HC_BOKGEOM_NOT_CORRECTED, HC_CHOGEOM_ERROR, 극중 필수 FR_ORDER, FR_EVALUATOR, FR_RELIEF_BEFORE_POPHYEOM, FR_HOSTILITY_BEFORE_DEATH, FR_HWAN_ACCUSES, FR_JSJ_MOTIVE
- 이 질문을 위해 풀어 둔 제약: 극중 필수 FR_DUAL_OUTCOME, FR_INVESTIGABLE / 사료 인과 사실 없음
- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.
- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: 성립

| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |
|---|---|---|---|
| `blame_path` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | 없음 |
| `hostility_to_yun` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | 없음 |
| `murder_by_residents` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `u_trigger`(살인을 촉발한 구체적 사건) |

**모형상 결과**: 권중립이 책임을 전가하지 않아도 이가원의 선택적 정보나 주민 간 소문이라는 별도 경로가 있어 적대·살해는 모형상 여전히 가능하다. 살해에는 촉발 사건(`u_trigger`)이 추가로 필요하다.

**해석 한계**: 대체 경로들 역시 모두 미입증 창작이다. '권중립 없이도 성립'은 그 대체 가정을 받아들일 때에만 참이다.

## Q5. 조상진이 좋은 포폄을 내리지 않았다면?

- 변경한 변수: `jsj_good_pophyeom`=False (외생변수 값 설정(do))
- 고정(유지)한 제약: 모형 구조 15개, 사료 인과 사실 HC_SONG, HC_INSTIGATION, HC_ACCUSATION, HC_OKSA, HC_NO_DIRECT_REINVEST, HC_HWAN_ILL, HC_BOKGEOM_NOT_CORRECTED, HC_CHOGEOM_ERROR, 극중 필수 FR_ORDER, FR_RELIEF_BEFORE_POPHYEOM, FR_HOSTILITY_BEFORE_DEATH, FR_DUAL_OUTCOME, FR_HWAN_ACCUSES, FR_INVESTIGABLE
- 이 질문을 위해 풀어 둔 제약: 극중 필수 FR_EVALUATOR, FR_JSJ_MOTIVE / 사료 인과 사실 없음
- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.
- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: **불성립**

| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |
|---|---|---|---|
| `jsj_cover_motive` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `u_jsj_supervisory_fear`(감독 책임 추궁에 대한 우려(포폄과 무관)) |
| `reinvest_motivated` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `u_jsj_supervisory_fear`(감독 책임 추궁에 대한 우려(포폄과 무관)) |
| `kjr_career_stake` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `u_kjr_reward_expect`(권중립의 인사상 이익 기대(포폄 외 경로)) |
| `kjr_cover_motive` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `u_kjr_reward_expect`(권중립의 인사상 이익 기대(포폄 외 경로)) |

**모형상 결과**: 좋은 포폄이 없으면 조상진의 방어 동기는 포폄과 무관한 감독책임 우려(`u_jsj_supervisory_fear`)가 있어야만 성립한다. 권중립의 인사상 이해도 포폄 외 보상 기대(`u_kjr_reward_expect`)가 필요하다. 관찰 조건화(극중 필수 조건 전체 유지)로는 이 세계가 불성립한다(필수 조건이 좋은 포폄을 요구하므로).

**해석 한계**: 포폄계본·등급·사유는 미확보다. 실록이 비판한 것은 '직접 조사하지 않음'(과실형 서술)이며 동기는 기록되지 않았다.

## Q6. 조상진이 포폄 당시 강제 권분을 몰랐다면?

- 변경한 변수: `jsj_knew_at_pophyeom`=False (외생변수 값 설정(do))
- 고정(유지)한 제약: 모형 구조 15개, 사료 인과 사실 HC_SONG, HC_INSTIGATION, HC_ACCUSATION, HC_OKSA, HC_NO_DIRECT_REINVEST, HC_HWAN_ILL, HC_BOKGEOM_NOT_CORRECTED, HC_CHOGEOM_ERROR, 극중 필수 FR_ORDER, FR_EVALUATOR, FR_RELIEF_BEFORE_POPHYEOM, FR_HOSTILITY_BEFORE_DEATH, FR_DUAL_OUTCOME, FR_HWAN_ACCUSES, FR_INVESTIGABLE
- 이 질문을 위해 풀어 둔 제약: 극중 필수 FR_JSJ_MOTIVE / 사료 인과 사실 없음
- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.
- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: 성립

| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |
|---|---|---|---|
| `jsj_cover_motive` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | 없음 |
| `reinvest_motivated` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | 없음 |
| `jsj_learned_later_no_correct` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `jsj_learned_later_no_correct`(포폄 후 인지했으나 정정하지 않음) |

**모형상 결과**: 포폄 당시 몰랐어도 '사후 인지·미정정' 또는 감독책임 우려 경로로 방어 동기는 남는다. 책임의 종류가 바뀐다: 사전 인지 → 평가의 공모적 왜곡 / 사후 인지 → 정정 의무 위반 / 감독책임만 → 자기 보호형 부실 / 동기 없음 → 단순 과실(실록 서술과 가장 가까움).

**해석 한계**: 책임 유형 구분은 모형의 분류이며 법적 평가가 아니다.

## Q7. 조환이 조재항을 신뢰했다면?

- 변경한 변수: `hwan_trusts_jjh`=True (외생변수 값 설정(do))
- 고정(유지)한 제약: 모형 구조 15개, 사료 인과 사실 HC_SONG, HC_INSTIGATION, HC_NO_DIRECT_REINVEST, HC_HWAN_ILL, HC_BOKGEOM_NOT_CORRECTED, HC_CHOGEOM_ERROR, 극중 필수 FR_ORDER, FR_EVALUATOR, FR_RELIEF_BEFORE_POPHYEOM, FR_HOSTILITY_BEFORE_DEATH, FR_JSJ_MOTIVE, FR_INVESTIGABLE
- 이 질문을 위해 풀어 둔 제약: 극중 필수 FR_DUAL_OUTCOME, FR_HWAN_ACCUSES / 사료 인과 사실 HC_ACCUSATION, HC_OKSA
- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.
- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: 성립

| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |
|---|---|---|---|
| `hwan_believes` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `lgw_reports_quarrel`(이가원이 조환에게 부부 언쟁 정보를 제공), `u_lgw_extra_evidence`(이가원의 추가 '증거'(가장된 목격담·혈의 주장 등)) |
| `hwan_accepts` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | 없음 |
| `accusation` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | 없음 |

**모형상 결과**: 조환이 조재항을 신뢰했다면, 믿음 경로로 고발을 끌어내기 위해 이가원은 부부 언쟁 정보 제공에 더해 추가 '증거'(`u_lgw_extra_evidence`, 예: 가장된 목격담·혈의 주장)를 내놓아야 한다. 금전 이해 경로로는 신뢰와 무관하게 수용이 가능하다.

**해석 한계**: 실록은 '피 묻은 옷의 행방이 없다'고 판단했다(CL-SIL-05). 혈의를 이가원 측 '증거'로 쓰는 것은 이 기록을 극적으로 연결하는 추론이며, 혈의가 누구의 주장이었는지는 원문 확인이 필요하다.

## Q8. 조환이 윤씨의 권분 반대 이유를 알고 있었다면?

- 변경한 변수: `hwan_knows_reason`=True (외생변수 값 설정(do))
- 고정(유지)한 제약: 모형 구조 15개, 사료 인과 사실 HC_SONG, HC_INSTIGATION, HC_NO_DIRECT_REINVEST, HC_HWAN_ILL, HC_BOKGEOM_NOT_CORRECTED, HC_CHOGEOM_ERROR, 극중 필수 FR_ORDER, FR_EVALUATOR, FR_RELIEF_BEFORE_POPHYEOM, FR_HOSTILITY_BEFORE_DEATH, FR_JSJ_MOTIVE, FR_INVESTIGABLE
- 이 질문을 위해 풀어 둔 제약: 극중 필수 FR_DUAL_OUTCOME, FR_HWAN_ACCUSES / 사료 인과 사실 HC_ACCUSATION, HC_OKSA
- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.
- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: 성립

| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |
|---|---|---|---|
| `hwan_believes` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | `lgw_reframes_reason`(이가원이 거절 이유를 부부 갈등으로 재구성), `lgw_reports_quarrel`(이가원이 조환에게 부부 언쟁 정보를 제공) |
| `hwan_accepts` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | 없음 |

**모형상 결과**: 조환이 윤씨의 거절 이유를 알았다면, 믿음 경로에는 이가원이 그 이유를 '부부 갈등'으로 재구성하는 조작(`lgw_reframes_reason`)이 추가로 필요하다 → 사주가 더 어려워진다.

**해석 한계**: 가족체계이론은 정보 왜곡의 구조를 설명하는 틀일 뿐 조환의 실제 동기를 입증하지 않는다.

## Q9. 이가원이 실제 살해범을 몰랐다면?

- 변경한 변수: `lgw_knows_killers`=False, `lgw_prior_involvement`=False (외생변수 값 설정(do))
- 고정(유지)한 제약: 모형 구조 15개, 사료 인과 사실 HC_INSTIGATION, HC_NO_DIRECT_REINVEST, HC_HWAN_ILL, HC_BOKGEOM_NOT_CORRECTED, HC_CHOGEOM_ERROR, 극중 필수 FR_ORDER, FR_EVALUATOR, FR_RELIEF_BEFORE_POPHYEOM, FR_HOSTILITY_BEFORE_DEATH, FR_HWAN_ACCUSES, FR_JSJ_MOTIVE, FR_INVESTIGABLE
- 이 질문을 위해 풀어 둔 제약: 극중 필수 FR_DUAL_OUTCOME / 사료 인과 사실 HC_SONG, HC_ACCUSATION, HC_OKSA
- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.
- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: 성립

| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |
|---|---|---|---|
| `song_fabricated` | 가능(참·거짓 모두 성립) | 가능(참·거짓 모두 성립) | 없음 |
| `accusation` | 필연적으로 참 | 필연적으로 참 | 없음 |
| `oksa_formed` | 필연적으로 참 | 필연적으로 참 | 없음 |

**모형상 결과**: 이가원이 실제 살해범을 몰라도 농요 조작·고발·성옥은 모형상 성립한다. 사료의 무고 서술(사후 금전 요구 → 사주 → 농요)은 살해범 인지를 요구하지 않는다.

**해석 한계**: 사전 관여 세계는 사료의 '사후 무고' 서술을 넘어서는 창작이므로 별도 표시가 필요하다.

## Q10. 이우배가 초검의 오류를 바로잡았다면?

- 변경한 변수: `bokgeom_corrects`=True (외생변수 값 설정(do))
- 고정(유지)한 제약: 모형 구조 15개, 사료 인과 사실 HC_SONG, HC_INSTIGATION, HC_ACCUSATION, HC_NO_DIRECT_REINVEST, HC_HWAN_ILL, HC_CHOGEOM_ERROR, 극중 필수 FR_ORDER, FR_EVALUATOR, FR_RELIEF_BEFORE_POPHYEOM, FR_HOSTILITY_BEFORE_DEATH, FR_HWAN_ACCUSES, FR_JSJ_MOTIVE, FR_INVESTIGABLE
- 이 질문을 위해 풀어 둔 제약: 극중 필수 FR_DUAL_OUTCOME / 사료 인과 사실 HC_OKSA, HC_BOKGEOM_NOT_CORRECTED
- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.
- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: **불성립**

| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |
|---|---|---|---|
| `oksa_formed` | 가능(참·거짓 모두 성립) | 불가능(필연적으로 거짓) | 해당 없음(불가능) |
| `long_detention` | 가능(참·거짓 모두 성립) | 불가능(필연적으로 거짓) | 해당 없음(불가능) |

**모형상 결과**: 복검이 초검 오류를 바로잡으면 모형상 옥사 성립과 장기 구금은 불가능하다.

**해석 한계**: 모형은 '복검 교정 → 성옥 불성립'을 단순화했다. 실제로는 감사·형조 단계에서 다른 판단이 날 수 있으므로 결론은 이 구조방정식에 종속된다.

