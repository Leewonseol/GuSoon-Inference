"""가능세계·반사실 결과와 보고서 서술의 일치."""
import networkx as nx


def test_worlds_distinct_and_feasible(results, cons):
    w = results["worlds"]["worlds"]
    assert 1 <= len(w) <= 10
    projs = [tuple(x["proj"][d] for d, _ in cons.WORLD_DIMS) for x in w]
    assert len(set(projs)) == len(projs), "인과구조가 같은 세계가 중복"
    for x in w:
        assert x["vals"]["murder_by_residents"] and x["vals"]["oksa_formed"], "윤씨 살해와 조재항 무고 동시 성립 실패"


def test_no_probabilities_in_world_outputs(root):
    for f in ("05_possible_worlds.csv", "06_world_comparison.md", "12_final_research_report.md"):
        txt = (root / f).read_text(encoding="utf-8-sig")
        assert "%" not in txt.replace("100%", ""), f"{f}: 백분율 표기"


def test_pareto_claim_in_reports(results, root):
    nd = [x["world"] for x in results["worlds"]["worlds"] if x["pareto"]]
    for f in ("README.md", "12_final_research_report.md"):
        txt = (root / f).read_text(encoding="utf-8")
        assert "·".join(nd) in txt or ", ".join(nd) in txt, f"{f}: 파레토 세계 서술이 결과와 다름 {nd}"


def test_counterfactual_key_results(results):
    cf = {q["qid"]: q for q in results["counterfactuals"]}
    assert cf["Q1"]["intervened"]["econ_refusal"].startswith("불가능")
    assert cf["Q2"]["intervened"]["econ_refusal"].startswith("불가능")
    assert "lgw_selective" in cf["Q3"]["minimal_extra_assumptions"]["hostility_to_yun"]["necessary_beyond_baseline"]
    assert "u_jsj_supervisory_fear" in cf["Q5"]["minimal_extra_assumptions"]["jsj_cover_motive"]["necessary_beyond_baseline"]
    assert cf["Q5"]["conditioning_with_all_film_requirements_sat"] is False
    assert "u_lgw_extra_evidence" in cf["Q7"]["minimal_extra_assumptions"]["hwan_believes"]["necessary_beyond_baseline"]
    assert "lgw_reframes_reason" in cf["Q8"]["minimal_extra_assumptions"]["hwan_believes"]["necessary_beyond_baseline"]
    assert not cf["Q9"]["intervened"]["accusation"].startswith("불가능")
    assert cf["Q10"]["intervened"]["long_detention"].startswith("불가능")


def test_causal_graph_is_dag_and_typed(cons, root):
    g = cons.build_graph()
    assert nx.is_directed_acyclic_graph(g)
    assert {d["kind"] for *_, d in g.edges(data=True)} <= {"source", "theory", "film"}
    assert (root / "08_causal_graph.mmd").read_text(encoding="utf-8") == cons.mermaid(g)
