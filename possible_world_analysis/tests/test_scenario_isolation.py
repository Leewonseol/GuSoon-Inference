"""가상 곡식 수량은 시나리오 계층에만 있어야 한다."""
import re

import yaml


def test_scenario_values_marked_fictional(root):
    p = yaml.safe_load((root / "scenario" / "scenario_parameters.yaml").read_text(encoding="utf-8"))
    assert p["status"] == "FICTIONAL_SCENARIO_VALUES"
    assert "가상" in p["unit"] and "석" not in p["unit"]


def test_historical_files_have_no_grain_quantities(root):
    pat = re.compile(r"\d+\s*(석|斗|두|섬|u\b|가상 단위)")
    for f in ("01_claim_registry.csv", "sources.yaml"):
        txt = (root / f).read_text(encoding="utf-8-sig")
        for m in pat.finditer(txt):
            ctx = txt[max(0, m.start() - 80):m.end() + 40]
            assert "환상곡" not in ctx, ctx
            raise AssertionError(f"{f}: 곡식 수량처럼 보이는 값 '{m.group(0)}' — {ctx}")


def test_economic_scenarios_computed(results):
    e = results["economic_scenarios"]
    assert e["ECON_A"]["u_extra_exceeds"] is True and e["ECON_B"]["u_extra_exceeds"] is False
    for v in e.values():
        assert "가상" in v["status"]
