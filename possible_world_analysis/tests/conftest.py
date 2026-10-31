import csv
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


@pytest.fixture(scope="session")
def root():
    return ROOT


@pytest.fixture(scope="session")
def sources():
    return {s["source_id"]: s for s in yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))["sources"]}


@pytest.fixture(scope="session")
def claims():
    with (ROOT / "01_claim_registry.csv").open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="session")
def variables():
    return yaml.safe_load((ROOT / "02_variables.yaml").read_text(encoding="utf-8"))["variables"]


@pytest.fixture(scope="session")
def cons():
    from loader import load_constraints
    return load_constraints()


@pytest.fixture(scope="session")
def results():
    return {n: json.loads((ROOT / "results" / f"{n}.json").read_text(encoding="utf-8"))
            for n in ("csp_results", "worlds", "counterfactuals", "economic_scenarios", "link_check")}
