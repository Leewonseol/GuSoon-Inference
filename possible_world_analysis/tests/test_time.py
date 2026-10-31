"""음력 서수 인덱스와 시간 계산."""
import inspect
import re

import pytest


def test_index_roundtrip(cons):
    assert cons.L(1780, 1, 1) == 0
    assert cons.L(1780, 6, 15) == 5 * 30 + 14
    assert cons.L(1781, 1, 1) - cons.L(1780, 12, 30) == 1
    assert cons.fmt(cons.L(1783, 6, 3)).startswith("1783년 음력 6월 3일")
    with pytest.raises(ValueError):
        cons.L(1780, 13, 1)


def test_pophyeom_days_are_june_december(cons):
    for d in cons.pophyeom_days(range(1780, 1782)):
        assert cons.fmt_month(d)[-3:] in ("L06", "L12")


def test_no_solar_conversion(root):
    src = (root / "03_constraints.py").read_text(encoding="utf-8")
    assert not re.search(r"import\s+(lunardate|korean_lunar_calendar|convertdate)|solar|gregorian|datetime\(", src, re.I) \
        or "양력 변환이 아니다" in src
    assert not re.search(r"from\s+(lunardate|korean_lunar_calendar|convertdate)", src)


def test_death_window_under_sim(results, cons):
    w = results["csp_results"]["modes"]["H_SIM"]["windows"]["DEATH"]
    assert w[1].startswith("1780년 음력 5월")


def test_compressed_requires_oksa_outside_both_sources(results):
    m = [[x["id"] for x in s] for s in results["csp_results"]["F_COMPRESSED"]["anchor_corrections"]]
    assert all("HT_SIL_CASE_1781" in s for s in m)
    assert all(("HT_SIM_OKSA_1780_6" in s) or ("HT_ACCUSE_40" in s) for s in m)
