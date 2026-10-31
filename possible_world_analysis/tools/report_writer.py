"""03_constraints.py의 계산 결과를 Markdown 보고서로 옮긴다(06·07·results/csp_report.md).

해석 문장은 계산 결과와 어긋나지 않도록 tests/test_reports.py가 핵심 결과를 다시 검사한다.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LAYER_KO = {"STR": "모형 구조", "INST": "제도 규칙", "HIST_TEN": "인사 연표(사료)", "HIST_T": "사료 연대",
            "HIST_C": "사료 인과 사실", "FILM_REQ": "극중 필수", "FILM_SYN": "시놉시스 v4 선택"}
COST_KO = {  # 각색 비용의 '종류'(점수 아님)
    "HIST_T": "사료에 기록된 날짜를 바꿈 → 자막·홍보에서 '각색'으로 명시해야 함",
    "HIST_TEN": "실존 관리의 재임 연표를 바꿈 → 인물 고증 비용이 큼",
    "INST": "제도 운용을 비정규적으로 설정(예: 정기 포폄이 아닌 수시 포상 장계) → 극중 설명 장면 필요",
    "FILM_REQ": "사용자가 정한 극중 필수 조건을 포기 → 작품 설계 자체 변경",
    "FILM_SYN": "시놉시스 v4의 날짜 선택을 바꿈 → 각본 수정만 필요",
}


def _c(x):
    return f"`{x['id']}` ({LAYER_KO.get(x['layer'], x['layer'])}) — {x['text']} · 근거: {', '.join(x['basis'])}" + \
        (f" · 상태: {x['status']}" if x.get("status") else "")


def csp_report(res):
    L = ["# CSP·시간제약 계산 결과 (자동 생성)", "",
         "> 생성기: `03_constraints.py` → `tools/report_writer.py`. 날짜는 **음력 서수 근사**(30일 월, 윤달 미반영)이며 양력 변환이 아니다.",
         "> SAT는 '논리적으로 모순이 없다'는 뜻일 뿐 역사적으로 그랬을 가능성을 뜻하지 않는다.", "",
         "## 1. 모드별 판정", "", "| 모드 | 설명 | 결과 |", "|---|---|---|"]
    for k, v in res["modes"].items():
        L.append(f"| `{k}` | {v['desc']} | **{v['result']}** |")
    for k, v in res["modes"].items():
        L += ["", f"## `{k}` — {v['result']}", ""]
        if v["result"] == "UNSAT":
            L.append("**최소 충돌조건 집합(MUS)** — 이 집합의 조건을 모두 유지하면 해가 없고, 하나라도 빼면 그 집합의 충돌은 풀린다.")
            for i, m in enumerate(v["mus"], 1):
                L.append(f"\n{i}. MUS {i}")
                L += [f"   - {_c(x)}" for x in m]
            L += ["", "**최소 수정집합(MCS)** — 아래 중 한 집합만 완화하면 해가 생긴다. 비용은 점수가 아니라 종류로 표시한다.", ""]
            for i, m in enumerate(v["mcs"], 1):
                L.append(f"- 수정안 {i}: " + " + ".join(f"`{x['id']}`" for x in m) + " → " +
                         " / ".join(sorted({COST_KO.get(x['layer'], x['layer']) for x in m})))
        else:
            L += ["사건 시점의 모형상 가능 구간(최소~최대). 구간 끝이 1778·1784년이면 '사료가 그 방향을 제약하지 않음'을 뜻한다.", "",
                  "| 사건 | 최소 | 최대 |", "|---|---|---|"]
            for e, w in v["windows"].items():
                if w:
                    L.append(f"| {e} | {w[0]} | {w[1]} |")
    L += ["", "## MODE F — 사료 연대 앵커의 최소 수정 (극중 필수 + 제도 + 인사 연표 유지)", ""]
    for i, m in enumerate(res["F_ADAPT_anchor_corrections"], 1):
        L.append(f"- 수정안 F{i}: " + " + ".join(f"`{x['id']}`" for x in m))
    for w in res["F_ADAPT_witnesses"]:
        ww = w["witness"]
        L += ["", f"### 예시 해 — 완화: {', '.join(w['relaxed_anchors'])}", "",
              "유일해가 아니다. 시놉시스 v4의 선택을 개수 기준으로 최대한 보존한 하나의 해다. "
              f"보존 못 한 시놉시스 선택: {', '.join(ww['dropped_preferences']) or '없음'}", "", "| 사건 | 예시 시점 |", "|---|---|"]
        for e in ("JSJ_ARRIVE", "POPHYEOM", "DEATH", "BURIAL", "ACCUSE", "CHOGEOM", "BOKGEOM", "OKSA", "REVIEW_ORDER",
                  "JSJ_REINVEST", "HYEONGJO_1781_8", "JOKJAENG", "FINAL", "JSJ_END"):
            L.append(f"| {e} | {ww['events'][e]} |")
    L += ["", "윤씨 사망의 가능 구간(수정안별):", ""]
    for k, w in res["F_ADAPT_death_window_per_correction"].items():
        L.append(f"- {k}: {w[0]} ~ {w[1]}")
    fc = res["F_COMPRESSED"]
    L += ["", "## MODE F-압축 — 시놉시스의 결말 압축을 강제할 때", "",
          f"강제한 시놉시스 선택: {', '.join(fc['forced_synopsis_choices'])} → 기본 판정 {fc['base_result']}", "",
          "필요한 사료 연대 앵커 수정(최소 수정집합):", ""]
    for i, m in enumerate(fc["anchor_corrections"], 1):
        L.append(f"- 수정안 C{i}: " + " + ".join(f"`{x['id']}`" for x in m))
    ww = fc["witness"]
    L += ["", f"예시 해(완화: {', '.join(fc['witness_correction'])}):", "", "| 사건 | 예시 시점 |", "|---|---|"]
    for e in ("JSJ_ARRIVE", "POPHYEOM", "DEATH", "BURIAL", "ACCUSE", "CHOGEOM", "BOKGEOM", "OKSA", "REVIEW_ORDER",
              "JSJ_REINVEST", "JOKJAENG", "FINAL"):
        L.append(f"| {e} | {ww['events'][e]} |")
    (ROOT / "results" / "csp_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


FLAG_KEYS = ["경제적 인과성", "희생양화(행위자 경로)", "행정적 인과성", "가족체계 설명력", "사법적 인과성", "수사 가능성"]


def world_comparison(rows, nproj, forced):
    from loader import load_constraints
    cons = load_constraints()
    L = ["# 06. 대표 가능세계 비교 (자동 생성)", "",
         "> 생성기: `03_constraints.py`. 각 세계는 **논리적으로 성립**할 뿐이며 역사적 진실 가능성의 순위가 아니다. 확률·백분율·가중 점수를 쓰지 않는다.", "",
         "## 1. 생성 방법", "",
         f"- 모드: `F_ADAPT` (극중 필수 + 제도 규칙 + 인사 연표 + 사료 인과 사실 유지, 사료 연대 앵커는 세계마다 최소 수정 계산).",
         f"- 13+1개 핵심 인과 차원(`WORLD_DIMS`)으로 투영했을 때 성립하는 서로 다른 인과구조: **{nproj}개**.",
         "- 대표 10개 선택: 시놉시스 v4·사용자 가설에 가장 가까운 세계(W01)에서 출발해, 이미 고른 세계들과의 최소 해밍거리가 가장 큰 세계를 차례로 추가(결정적 알고리즘). 이름이나 날짜만 다른 세계는 같은 투영으로 묶이므로 중복되지 않는다.",
         "- 투영 밖 변수는 '극중 가정(creative)으로 참이 되는 외생변수의 개수'를 최소화해 채웠다(가장 적은 가정으로 완성).",
         f"- 모든 세계에 공통으로 강제되는 극중 가정(극중 필수 조건의 귀결): {', '.join(f'`{x}`' for x in forced)} — 세계별 '미확인 가정 수'에서는 제외했다.", "",
         "## 2. 대표 세계 표 (지시문 §13 형식)", "",
         "| 세계 | 주요 가정(행정) | 시간제약 | 사료 변경 | 살해 동기 | 무고 동기 | 추가 검증 필요(변수) |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        mk, mf, admin = cons.explain_world(r)
        need = ", ".join(sorted({cons.EXOG[a][0] for a in r["assump"]}))
        dates = " 또는 ".join("+".join(s) for s in r["date_sets"])
        L.append(f"| {r['world']} | {admin} | 극중 필수 순서 충족 | 최소 {r['n_dates']}개: {dates} | {mk} | {mf} | {need} |")
    L += ["", "## 3. 인과 차원 값", "", "| 세계 | " + " | ".join(lbl for _, lbl in cons.WORLD_DIMS) + " |",
          "|---|" + "---|" * len(cons.WORLD_DIMS)]
    for r in rows:
        L.append(f"| {r['world']} | " + " | ".join("●" if r["proj"][d] else "○" for d, _ in cons.WORLD_DIMS) + " |")
    L += ["", "## 4. 비교 기준 (지시문 §15)", "",
          "### 4.1 계산 가능한 기준", "",
          "| 세계 | 미확인 가정 수(세계 고유) | 연대 변경 수 | " + " | ".join(FLAG_KEYS) + " | 파레토 비지배 |",
          "|---|---|---|" + "---|" * len(FLAG_KEYS) + "---|"]
    for r in rows:
        L.append(f"| {r['world']} | {r['n_assump']} | {r['n_dates']} | " + " | ".join("○" if not r["flags"][k] else "●" for k in FLAG_KEYS)
                 + f" | {'**예**' if r['pareto'] else '아니오'} |")
    nd = [r["world"] for r in rows if r["pareto"]]
    L += ["", f"파레토 비지배 세계: **{', '.join(nd)}** — 다른 어떤 세계도 '가정 수·연대 변경 수가 같거나 적으면서 모든 설명 기준을 같거나 더 많이 충족'하지 못한다. "
          "가중치를 두지 않았으므로 이들 사이의 우열은 정하지 않는다.", "",
          "판정 기준의 정의(불리언, 모형 내부 정의):", "",
          "- 경제적 인과성: `econ_refusal` (부담 집중 ∧ 추가 요구 > 가용량)",
          "- 희생양화(행위자 경로): 적대가 성립하고, 그 경로에 권중립 책임 전가 또는 이가원 선택적 정보가 있음(주민 간 자생적 소문만으로 성립한 경우 제외)",
          "- 행정적 인과성: 권중립·조상진 모두 방어 동기가 있고, 조상진의 동기가 포폄과 인지(사전 또는 사후)에서 나옴",
          "- 가족체계 설명력: 조환이 이가원의 주장을 '믿는' 경로가 있음(금전 이해만으로 수용하면 ○)",
          "- 사법적 인과성: 농요 조작 ∧ 고발 ∧ 옥사 성립",
          "- 수사 가능성: 독립 조사 ∧ 반대자 증인 ∧ 주민 살해(결말에서 살해범 식별 가능)",
          "", "### 4.2 연구자의 질적 판단이 필요한 기준(모형이 판정하지 않음)", "",
          "- **사료 충실성**: 모든 세계가 사료 인과 사실(HIST_C)을 유지하지만, 사료가 침묵하는 영역(살해 경위·권분 시행)을 얼마나 넓게 채우는지는 '미확인 가정 수'로만 근사된다. 가정의 *질*(예: 이가원 사전 관여는 사료의 '사후 무고' 서술과 긴장)은 연구자가 판단해야 한다.",
          "- **연대 변경 비용**: 모든 대표 세계의 최소 변경은 같다(아래 5절). 차이는 결말 압축을 얼마나 하느냐(작가 선택)에서 생긴다.",
          "- **희생양화의 개연성**: 지라르 틀과 실험사회심리학(책임 전가) 사이의 구분은 07·11 문서에서 다룬다. 모형은 경로의 존재만 판정한다.",
          "", "## 5. 시간제약과 사료 변경", "",
          "모든 대표 세계에서 극중 필수 순서를 유지하는 최소 사료 연대 수정은 동일하다(세계의 인과 차원과 시간 앵커가 직접 충돌하지 않음). "
          "세부 날짜와 수정 대안은 `results/csp_report.md`와 `04_historical_conflicts.md`를 본다.", ""]
    (ROOT / "06_world_comparison.md").write_text("\n".join(L) + "\n", encoding="utf-8")


CF_TEXT = {  # 질문별 해석과 한계(계산 결과와 함께 출력)
    "Q1": ("조재항이 회피 가능한 최상층 토호라면 모형상 '부담 집중'과 '경제적 거절 사유'는 사라진다. 윤씨에 대한 책임 전가는 여전히 가능하지만, 그 경우 거절 사유를 비경제적 동기(`u_yun_other_reason`)로 새로 만들어야 한다.",
           "부담 집중 식(`u_shortage ∧ e5 ∧ u_elite_evade`)은 이세영(2009)의 계층별 부담 차이 '요약'에 기댄 극중 가정이며 논문 원문은 미열람이다."),
    "Q2": ("부담 집중에 직접 개입하면 경제적 거절 사유는 불가능해진다. 거절·적대는 비경제적 거절 사유를 추가해야만 남는다.",
           "구조방정식 절단(do)과 관찰 조건화의 차이: 관찰로 '부담 집중 없음'을 보면 그 원인(회피 가능성 등)도 함께 갱신되지만, 개입은 원인을 그대로 둔다."),
    "Q3": ("자발적 권분만 시행해도 적대는 성립할 수 있으나, 그 경우 주민의 '관의 뜻' 명분은 이가원의 선택적 정보 공개(`lgw_selective`)가 필요조건이 된다. 권중립의 방어 동기도 실적 과장·책임 전가 경로로 남을 수 있다.",
           "명분(entitlement_framing) 식은 이론적 제안이다. 1780년 배천에서 강제 권분이 있었다는 직접 사료는 없다."),
    "Q4": ("권중립이 책임을 전가하지 않아도 이가원의 선택적 정보나 주민 간 소문이라는 별도 경로가 있어 적대·살해는 모형상 여전히 가능하다. 살해에는 촉발 사건(`u_trigger`)이 추가로 필요하다.",
           "대체 경로들 역시 모두 미입증 창작이다. '권중립 없이도 성립'은 그 대체 가정을 받아들일 때에만 참이다."),
    "Q5": ("좋은 포폄이 없으면 조상진의 방어 동기는 포폄과 무관한 감독책임 우려(`u_jsj_supervisory_fear`)가 있어야만 성립한다. 권중립의 인사상 이해도 포폄 외 보상 기대(`u_kjr_reward_expect`)가 필요하다. 관찰 조건화(극중 필수 조건 전체 유지)로는 이 세계가 불성립한다(필수 조건이 좋은 포폄을 요구하므로).",
           "포폄계본·등급·사유는 미확보다. 실록이 비판한 것은 '직접 조사하지 않음'(과실형 서술)이며 동기는 기록되지 않았다."),
    "Q6": ("포폄 당시 몰랐어도 '사후 인지·미정정' 또는 감독책임 우려 경로로 방어 동기는 남는다. 책임의 종류가 바뀐다: 사전 인지 → 평가의 공모적 왜곡 / 사후 인지 → 정정 의무 위반 / 감독책임만 → 자기 보호형 부실 / 동기 없음 → 단순 과실(실록 서술과 가장 가까움).",
           "책임 유형 구분은 모형의 분류이며 법적 평가가 아니다."),
    "Q7": ("조환이 조재항을 신뢰했다면, 믿음 경로로 고발을 끌어내기 위해 이가원은 부부 언쟁 정보 제공에 더해 추가 '증거'(`u_lgw_extra_evidence`, 예: 가장된 목격담·혈의 주장)를 내놓아야 한다. 금전 이해 경로로는 신뢰와 무관하게 수용이 가능하다.",
           "실록은 '피 묻은 옷의 행방이 없다'고 판단했다(CL-SIL-05). 혈의를 이가원 측 '증거'로 쓰는 것은 이 기록을 극적으로 연결하는 추론이며, 혈의가 누구의 주장이었는지는 원문 확인이 필요하다."),
    "Q8": ("조환이 윤씨의 거절 이유를 알았다면, 믿음 경로에는 이가원이 그 이유를 '부부 갈등'으로 재구성하는 조작(`lgw_reframes_reason`)이 추가로 필요하다 → 사주가 더 어려워진다.",
           "가족체계이론은 정보 왜곡의 구조를 설명하는 틀일 뿐 조환의 실제 동기를 입증하지 않는다."),
    "Q9": ("이가원이 실제 살해범을 몰라도 농요 조작·고발·성옥은 모형상 성립한다. 사료의 무고 서술(사후 금전 요구 → 사주 → 농요)은 살해범 인지를 요구하지 않는다.",
           "사전 관여 세계는 사료의 '사후 무고' 서술을 넘어서는 창작이므로 별도 표시가 필요하다."),
    "Q10": ("복검이 초검 오류를 바로잡으면 모형상 옥사 성립과 장기 구금은 불가능하다.",
            "모형은 '복검 교정 → 성옥 불성립'을 단순화했다. 실제로는 감사·형조 단계에서 다른 판단이 날 수 있으므로 결론은 이 구조방정식에 종속된다."),
}


def counterfactual_report(cfs):
    from loader import load_constraints
    cons = load_constraints()
    L = ["# 07. 반사실 분석 (자동 생성)", "",
         "> 생성기: `03_constraints.py`. 결과는 **가능성 의미론**(어떤 외생 조건 조합에서 성립할 수 있는가)이며 확률이 아니다. "
         "관찰 자료가 없으므로 모든 결론은 `03_constraints.py`의 구조방정식(SCM)에 종속된다.", "",
         "## 방법", "",
         "- **개입(do)**: 개입 변수가 내생이면 그 구조방정식을 절단하고 값을 고정한다(Pearl, 2009). 외생이면 값만 고정한다.",
         "- **관찰 조건화**: 구조방정식과 극중 필수 조건을 모두 유지한 채 값을 '관찰'로 추가한다. 개입과 결과가 다를 수 있으며, 아래에 함께 표시한다.",
         "- **유지 제약**: 모형 구조(STR) 전부 + 사료 인과 사실(HIST_C)·극중 필수(FILM_REQ) 중 개입 변수의 후손이나 질문한 결과를 직접 고정하지 않는 것.",
         "- **추가 가정**: 결과가 참이 되려면 *반드시* 참이어야 하는 극중 가정 중, 기준선에서 이미 필요한 것을 뺀 것.", ""]
    for q in cfs:
        expl, lim = CF_TEXT[q["qid"]]
        L += [f"## {q['qid']}. {q['question']}", "",
              f"- 변경한 변수: " + ", ".join(f"`{k}`={v}" for k, v in q["changed"].items()) + f" ({q['operation']})",
              f"- 고정(유지)한 제약: 모형 구조 {sum(1 for c in q['kept_constraints'] if c.startswith('STR'))}개, "
              f"사료 인과 사실 {', '.join(c for c in q['kept_constraints'] if c.startswith('HC_')) or '없음'}, "
              f"극중 필수 {', '.join(c for c in q['kept_constraints'] if c.startswith('FR_')) or '없음'}",
              f"- 이 질문을 위해 풀어 둔 제약: 극중 필수 {', '.join(q['dropped_film_requirements']) or '없음'} / 사료 인과 사실 {', '.join(q['dropped_historical_facts']) or '없음'}",
              f"- 유지한 역사적 제약: 시간 앵커는 이 분석에 쓰지 않음(인과 구조만 비교). 사료 인과 사실은 위 목록대로 유지.",
              f"- 관찰 조건화(극중 필수 조건 전부 유지) 시 성립 여부: {'성립' if q['conditioning_with_all_film_requirements_sat'] else '**불성립**'}", "",
              "| 결과 변수 | 기준선 | 개입 후 | 결과를 위해 추가로 반드시 필요한 가정 |", "|---|---|---|---|"]
        for o in q["intervened"]:
            ex = q["minimal_extra_assumptions"].get(o)
            need = "해당 없음(불가능)" if ex is None else (", ".join(f"`{x}`({cons.EXOG[x][1]})" for x in ex["necessary_beyond_baseline"]) or "없음")
            L.append(f"| `{o}` | {q['baseline'][o]} | {q['intervened'][o]} | {need} |")
        L += ["", f"**모형상 결과**: {expl}", "", f"**해석 한계**: {lim}", ""]
    (ROOT / "07_counterfactual_analysis.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def write_all(res, rows, nproj, cfs):
    csp_report(res)
    forced = json.loads((ROOT / "results" / "worlds.json").read_text(encoding="utf-8"))["forced_common_assumptions"]
    world_comparison(rows, nproj, forced)
    counterfactual_report(cfs)
