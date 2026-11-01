#!/usr/bin/env python3
"""Historical claims are constraints on testimony/judgments, not proof of latent events.

Enumerate explicitly declared story hypotheses with a finite-domain CSP. No
probabilities, causal effects, or historical likelihoods are estimated.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_sources(model: dict, registry: Path) -> dict:
    with registry.open(encoding="utf-8-sig", newline="") as f:
        found = {r["claim_id"]: r for r in csv.DictReader(f)}
    missing = set(model["source_claim_ids"]) - set(found)
    if missing:
        raise ValueError(f"Missing original claim IDs: {sorted(missing)}")
    return {key: found[key] for key in model["source_claim_ids"]}


def satisfies(world: dict, condition: dict) -> bool:
    for variable, allowed in condition.items():
        if not isinstance(allowed, list):
            allowed = [allowed]
        if world[variable] not in allowed:
            return False
    return True


def validate_model(model: dict) -> None:
    variables = model["world_variables"]
    for rule in model["rules"]:
        for side in ("if", "then"):
            for name, value in rule[side].items():
                choices = value if isinstance(value, list) else [value]
                if name not in variables or any(v not in variables.get(name, []) for v in choices):
                    raise ValueError(f"Malformed rule {rule['id']}: {name} = {choices}")
    for target, condition in model["narrative_targets"].items():
        for name, value in condition.items():
            choices = value if isinstance(value, list) else [value]
            if name not in variables or any(v not in variables[name] for v in choices):
                raise ValueError(f"Malformed target {target}: {name} = {choices}")


def assignments(model: dict):
    dimensions = model["world_variables"]
    names = list(dimensions)
    for values in itertools.product(*(dimensions[name] for name in names)):
        world = dict(zip(names, values))
        if all(not satisfies(world, rule["if"]) or satisfies(world, rule["then"])
               for rule in model["rules"]):
            yield world


def ordinal(y: int, m: int, d: int) -> int:
    """30-day lunar-month *index approximation*, NOT calendar conversion."""
    return ((y - 1780) * 12 + m - 1) * 30 + d


def chronology_checks() -> list:
    """Test explicitly labeled source-interpretation alternatives.

    A 1781 spring review necessarily presupposes a formed case, but
    '事在辛丑' does not itself state that the original case formed in June.
    """
    first_spring_review = ordinal(1781, 1, 1)
    last_spring_review = ordinal(1781, 3, 30)
    assumed_pophyeom = [ordinal(y, m, 15) for y in (1780, 1781) for m in (6, 12)]
    checks = []
    for code, y, m, interpretation in (
        ("SIM_1780_JUNE", 1780, 6, "Take 庚子六月成獄 as the month of case formation"),
        ("SIL_1781_JUNE_HYPOTHESIS", 1781, 6,
         "Hypothetically assume 事在辛丑 also means the ORIGINAL case formed in June 1781"),
    ):
        first_case, last_case = ordinal(y, m, 1), ordinal(y, m, 30)
        historical_ok = first_case < last_spring_review
        # Assumptions: 1780 summer arrival (earliest 4/1); 6/12/15 evaluations,
        # and at least 35 model-index days from death to accusation/formation.
        conditional_plot_ok = any(
            ordinal(1780, 4, 1) < p and p + 36 <= last_case
            for p in assumed_pophyeom
        )
        checks.append({
            "case": code,
            "interpretation": interpretation,
            "case_month": f"{y}-{m:02d}",
            "original_case_before_1781_spring_review": historical_ok,
            "film_pophyeom_before_death_plus_35_days": conditional_plot_ok,
            "both_requirements": historical_ok and conditional_plot_ok,
            "assumptions_for_film_check": [
                "조상진 1780년 음력 4~6월 부임(미확인; 부임 하한 4월 1일 사용)",
                "권중립에 대한 정기 포폄이 6월/12월 15일이라고 가정(원문 미확인)",
                "포폄 이후 윤씨 사망, 사망 후 최소 35 모형일 경과하여 성옥",
                "음력 월을 30일로 처리하는 기존 서수 근사; 실제 음력 날짜 계산 아님"
            ]
        })
    return checks


def analyze(model: dict, claims: dict) -> tuple[list, dict]:
    validate_model(model)
    worlds = list(assignments(model))
    targets = {name: sum(satisfies(w, test) for w in worlds)
               for name, test in model["narrative_targets"].items()}
    # These are *constructed combinations*. Counts depend on vocabulary choices.
    report = {
        "method": "finite-domain constraint satisfaction and source-interpretation checks",
        "sampling": "none; exhausts explicitly listed categorical combinations only",
        "candidate_assignments": len(worlds),
        "target_counts": targets,
        "chronology": chronology_checks(),
        "source_audit": [
            {
                "claim_id": claim_id,
                "claim": row["claim"],
                "verification_status": row["verification_status"],
                "evidence_role": row["evidence_role"],
                "url": row["url"]
            }
            for claim_id, row in claims.items()
        ],
        "source_assertions_preserved": [
            "정조가 조재항 방면을 명령했다 (명령의 존재; 집행 완료일 아님)",
            "정조가 이가원의 농요 조작·사주를 지적했다 (왕의 판단; 직접 관찰과 구분)",
            "정조가 조상진의 직접 재조사 부재를 질책했다 (고의적 증거 은폐를 뜻하지 않음)"
        ],
        "not_inferred_as_fact": [
            "윤씨를 살해한 실제 행위자", "1780년 배천에서의 권분과 강제성",
            "윤씨 살해 동기", "이가원의 사전 살해 공모", "조환의 심리 상태",
            "이우배의 구체적 실수 원인", "조상진의 고의적 은폐"
        ],
        "limitations": [
            "This is a logical compatibility screen over declared hypotheses, not probabilistic inference.",
            "Values not_established/not_modeled denote unresolved/partial templates, not full possible histories.",
            "The historical constraints on testimony and orders do not independently identify murder motives.",
            "The 1781 June original-case hypothesis is an interpretive stress test, not a claim made in the source.",
            "No archival passage is treated as newly verified merely because it appears in the GitHub registry."
        ],
    }
    return worlds, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=HERE / "model.json")
    parser.add_argument("--registry", type=Path, help="Original 01_claim_registry.csv")
    parser.add_argument("--out", type=Path, default=HERE / "results")
    args = parser.parse_args()
    model = json.loads(args.model.read_text(encoding="utf-8"))
    registry = args.registry or (args.model.parent / model["source_registry"]).resolve()
    claims = read_sources(model, registry)
    worlds, report = analyze(model, claims)
    args.out.mkdir(parents=True, exist_ok=True)
    fields = ["world_id", *model["world_variables"], *model["narrative_targets"]]
    with (args.out / "candidate_worlds.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i, world in enumerate(worlds, 1):
            writer.writerow({
                "world_id": f"CW{i:05d}", **world,
                **{key: int(satisfies(world, condition))
                   for key, condition in model["narrative_targets"].items()}
            })
    (args.out / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "candidate_assignments": len(worlds),
        "target_counts": report["target_counts"],
        "chronology": [{
            "case": item["case"],
            "original_case_before_review": item["original_case_before_1781_spring_review"],
            "plot_with_35day_gap": item["film_pophyeom_before_death_plus_35_days"]
        } for item in report["chronology"]]
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
