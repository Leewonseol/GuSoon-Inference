"""CSP 판정과 충돌집합이 보고서의 서술과 일치하는가."""


def ids(lst):
    return [sorted(x["id"] for x in s) for s in lst]


def test_mode_results(results):
    m = {k: v["result"] for k, v in results["csp_results"]["modes"].items()}
    assert m == {"H_SIM": "SAT", "H_SIL": "SAT", "H_BOTH": "UNSAT", "F_ON_H_SIM": "UNSAT", "F_ON_H_SIL": "SAT",
                 "F_SYNOPSIS_V4": "UNSAT", "F_ADAPT": "SAT"}


def test_both_sources_conflict(results):
    assert ids(results["csp_results"]["modes"]["H_BOTH"]["mus"]) == [["HT_SIL_CASE_1781", "HT_SIM_OKSA_1780_6"]]


def test_film_vs_simrok_core(results):
    mus = ids(results["csp_results"]["modes"]["F_ON_H_SIM"]["mus"])
    assert ["FR_ORDER", "HT_ACCUSE_40", "HT_JSJ_ARRIVE_SUMMER", "HT_SIM_OKSA_1780_6", "INST_POPHYEOM_DATES"] in mus
    mcs = ids(results["csp_results"]["modes"]["F_ON_H_SIM"]["mcs"])
    assert all(len(x) == 1 for x in mcs) and len(mcs) == 5


def test_synopsis_v4_conflicts_with_requirement(results):
    mus = ids(results["csp_results"]["modes"]["F_SYNOPSIS_V4"]["mus"])
    assert ["FR_ORDER", "FS_DEATH_1780_4_LATE", "FS_JSJ_ARRIVE_1780_6"] in mus


def test_mode_f_minimal_change(results):
    mcs = ids(results["csp_results"]["F_ADAPT_anchor_corrections"])
    assert mcs[0] == ["HT_SIM_OKSA_1780_6"]
    assert ["HT_ACCUSE_40", "HT_SIL_CASE_1781"] in mcs


def test_mus_is_minimal(cons, results):
    """MUS의 어느 원소를 빼도 만족 가능해야 한다(진짜 최소)."""
    md = results["csp_results"]["modes"]["F_ON_H_SIM"]
    hard_core = [c for c in md["hard"] if cons.CS_BY_ID[c].layer not in cons.SOFT_LAYERS]
    for mus in ids(md["mus"]):
        r, *_ = cons.check_ids(hard_core + mus)
        assert str(r) == "unsat"
        for c in mus:
            r, *_ = cons.check_ids(hard_core + [x for x in mus if x != c])
            assert str(r) == "sat", c


def test_every_constraint_has_basis(cons, claims, sources, variables):
    known = {c["claim_id"] for c in claims} | set(sources) | {v["id"] for v in variables}
    for c in cons.CS:
        assert c.basis, c.cid
        for b in c.basis:
            assert b in known, f"{c.cid}: 근거 {b} 없음"


def test_independence_of_jsj_authority(cons):
    """후임 이경양 재임 중에는 조상진이 재조사할 수 없다."""
    import z3
    r, *_ = cons.check_ids(["STR_SUCCESSOR", "STR_REINVEST_IN_TENURE", "STR_TENURE_JSJ"],
                           extra=[lambda t, b: t["JSJ_REINVEST"] > t["LKY_START"]])
    assert r == z3.unsat
