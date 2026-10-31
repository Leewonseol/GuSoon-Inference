"""변수표: 출처 연결·가상 변수 라벨·1782년 이후 사건의 소급 금지·모형 기호 일치."""
import re

EXPECTED = {"T": 20, "E": 15, "A": 15, "S": 12, "F": 12, "M": 14, "J": 15}


def _year(s):
    m = re.search(r"(1[67]\d\d)", s or "")
    return int(m.group(1)) if m else None


def test_counts(variables):
    for g, n in EXPECTED.items():
        assert sum(v["group"] == g for v in variables) == n, g


def test_refs_exist(variables, claims, sources):
    cids = {c["claim_id"] for c in claims}
    for v in variables:
        for c in v["claim_ids"] + v["context_claim_ids"]:
            assert c in cids, f"{v['id']}: 없는 주장 {c}"
        for s in v["source_ids"]:
            assert s in sources, f"{v['id']}: 없는 출처 {s}"


def test_scenario_not_labeled_historical(variables):
    for v in variables:
        if v["layer"] == "scenario":
            assert v["evidence_status"] not in ("원문 확인", "간접 확인"), f"{v['id']}: 가상 변수에 사실 라벨"
            assert v["basis_type"] in ("극중 설정", "극중 가설"), v["id"]


def test_historical_layer_needs_noninternal_source(variables, sources):
    for v in variables:
        if v["layer"] == "historical" and not (v["evidence_status"] == "미확인" and "사료 미확보" in v["note"]):
            assert any(sources[s]["category"] != "internal" for s in v["source_ids"]), f"{v['id']}: 역사 변수에 사료 없음"


def test_post_1782_events_not_used_as_1780_observation(variables, claims):
    """1782년 이후 사건은 context_claim_ids에만 둘 수 있고, E·A·S군(1780 배천 상황) 변수의 직접 근거가 될 수 없다."""
    cm = {c["claim_id"]: c for c in claims}
    for v in variables:
        if v["group"] in ("E", "A", "S"):
            for cid in v["claim_ids"]:
                c = cm[cid]
                y = _year(c["event_date"])
                if c["evidence_role"] in ("later_context", "comparative"):
                    raise AssertionError(f"{v['id']}: 비교·후대 주장 {cid}를 직접 근거로 사용")
                # 사건 기록 자체(심리록·실록 판부·추관지)가 앞선 사건을 서술하는 것은 소급이 아니다.
                if y and y >= 1782 and c["claim_type"] == "직접 사실" and c["source_id"] not in ("SIM", "SIL1783", "CHUG"):
                    raise AssertionError(f"{v['id']}: {y}년 사건 {cid}를 1780년 관측으로 소급")


def test_model_symbols_exist(variables, cons):
    known = set(cons.EVENTS) | set(cons.EXOG) | set(cons.ENDO_ORDER)
    for v in variables:
        for s in v["model_symbols"]:
            assert s in known, f"{v['id']}: 모형에 없는 기호 {s}"


def test_model_variable_ids_defined(variables, cons):
    ids = {v["id"] for v in variables}
    used = {x[0] for x in cons.EVENTS.values()} | {x[0] for x in cons.EXOG.values()}
    import z3
    b = {k: z3.Bool(k) for k in list(cons.EXOG) + cons.ENDO_ORDER}
    used |= {d[0] for d in cons._endo_defs(b).values()}
    assert used <= ids, used - ids
