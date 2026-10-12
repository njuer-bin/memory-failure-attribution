"""Analyze conditional lifecycle survival from an existing oracle comparison.

The strict provenance evaluator makes each stage a causal boundary. Raw stage
recall is still confounded by upstream losses, so this module reports:
1. stage recall across eligible samples;
2. adjacent transition survival given success at the previous stage; and
3. cumulative upstream transition survival, which is the primary causal view.

No model calls are made.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

STAGES = ("formation", "storage", "evolution", "retrieval", "rerank", "context")


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("_status", "ok") == "ok":
                rows.append(row)
    return rows


def gold_ids(row: dict[str, Any]) -> set[str]:
    return {
        str(item["evidence_id"])
        for item in row.get("gold_evidence", [])
        if item.get("evidence_id")
    }


def found_ids(row: dict[str, Any], stage: str) -> set[str]:
    mode = row.get("modes", {}).get("real_memory", {})
    return {str(x) for x in (mode.get(stage) or {}).get("found", [])}


def stage_all_pass(row: dict[str, Any], stage: str) -> bool:
    gold = gold_ids(row)
    return bool(gold) and gold.issubset(found_ids(row, stage))


def stage_chain_pass(row: dict[str, Any], through_stage: str) -> bool:
    """Return whether every stage up to and including ``through_stage`` passes."""
    if through_stage not in STAGES:
        raise ValueError(f"unknown stage: {through_stage}")
    end = STAGES.index(through_stage)
    return all(stage_all_pass(row, stage) for stage in STAGES[: end + 1])


def gate_status(row: dict[str, Any]) -> str:
    return str(
        row.get("modes", {})
        .get("real_memory", {})
        .get("evidence_sufficiency", {})
        .get("status", "unknown")
    )


def transition_stats(rows: list[dict[str, Any]], gate_sufficient_only: bool = False) -> dict[str, Any]:
    eligible = [
        row for row in rows
        if gold_ids(row)
        and (not gate_sufficient_only or gate_status(row) == "sufficient")
    ]
    result: dict[str, Any] = {
        "eligible_rows": len(eligible),
        "gate_sufficient_only": gate_sufficient_only,
        "stage": {},
        "transitions": {},
        "cumulative_transitions": {},
    }

    for stage in STAGES:
        passed = sum(stage_all_pass(row, stage) for row in eligible)
        result["stage"][stage] = {
            "passed": passed,
            "total": len(eligible),
            "rate": passed / len(eligible) if eligible else None,
        }

    # Adjacent transitions are retained as descriptive diagnostics.
    for previous, current in zip(STAGES, STAGES[1:]):
        conditional_rows = [row for row in eligible if stage_all_pass(row, previous)]
        survived = sum(stage_all_pass(row, current) for row in conditional_rows)
        result["transitions"][f"{previous}_to_{current}"] = {
            "previous_stage": previous,
            "current_stage": current,
            "eligible_after_previous": len(conditional_rows),
            "survived_current": survived,
            "conditional_survival": survived / len(conditional_rows) if conditional_rows else None,
            "conditional_failure": (
                1 - survived / len(conditional_rows) if conditional_rows else None
            ),
        }

    # Primary causal view: require all upstream stages to have passed before
    # asking whether the next stage also survives. This avoids treating rows
    # that already failed upstream as if they were valid denominators.
    for index in range(1, len(STAGES)):
        previous = STAGES[index - 1]
        current = STAGES[index]
        eligible_chain = [
            row for row in eligible if stage_chain_pass(row, previous)
        ]
        survived = sum(stage_all_pass(row, current) for row in eligible_chain)
        result["cumulative_transitions"][f"{current}_given_upstream"] = {
            "upstream_through": previous,
            "current_stage": current,
            "eligible_after_upstream": len(eligible_chain),
            "survived_current": survived,
            "conditional_survival": survived / len(eligible_chain) if eligible_chain else None,
            "conditional_failure": (
                1 - survived / len(eligible_chain) if eligible_chain else None
            ),
        }
    return result


def evidence_level_transition_stats(rows: list[dict[str, Any]], gate_sufficient_only: bool = False) -> dict[str, Any]:
    """Compute the same transitions per Gold Evidence item, not per question.

    This is useful because multi-evidence questions can hide partial lifecycle
    loss behind an all-evidence question-level pass/fail decision.
    """
    pairs = []
    for row in rows:
        if gate_sufficient_only and gate_status(row) != "sufficient":
            continue
        for evidence_id in gold_ids(row):
            pairs.append((row, evidence_id))

    def passed(row: dict[str, Any], evidence_id: str, stage: str) -> bool:
        return evidence_id in found_ids(row, stage)

    def chain_passed(row: dict[str, Any], evidence_id: str, through_stage: str) -> bool:
        if through_stage not in STAGES:
            raise ValueError(f"unknown stage: {through_stage}")
        end = STAGES.index(through_stage)
        return all(passed(row, evidence_id, stage) for stage in STAGES[: end + 1])

    result: dict[str, Any] = {
        "eligible_evidence": len(pairs),
        "transitions": {},
        "cumulative_transitions": {},
    }
    for previous, current in zip(STAGES, STAGES[1:]):
        eligible = [(r, e) for r, e in pairs if passed(r, e, previous)]
        survived = sum(passed(r, e, current) for r, e in eligible)
        result["transitions"][f"{previous}_to_{current}"] = {
            "eligible_after_previous": len(eligible),
            "survived_current": survived,
            "conditional_survival": survived / len(eligible) if eligible else None,
            "conditional_failure": 1 - survived / len(eligible) if eligible else None,
        }

    for index in range(1, len(STAGES)):
        previous = STAGES[index - 1]
        current = STAGES[index]
        eligible = [
            (row, evidence_id)
            for row, evidence_id in pairs
            if chain_passed(row, evidence_id, previous)
        ]
        survived = sum(passed(row, evidence_id, current) for row, evidence_id in eligible)
        result["cumulative_transitions"][f"{current}_given_upstream"] = {
            "upstream_through": previous,
            "current_stage": current,
            "eligible_after_upstream": len(eligible),
            "survived_current": survived,
            "conditional_survival": survived / len(eligible) if eligible else None,
            "conditional_failure": (
                1 - survived / len(eligible) if eligible else None
            ),
        }
    return result


def _fmt_rate(value: float | None) -> str:
    return "NA" if value is None else f"{value:.3f}"


def print_report(rows: list[dict[str, Any]]) -> None:
    for gate_only in (False, True):
        label = "gate-sufficient rows" if gate_only else "all rows"
        report = transition_stats(rows, gate_only)
        print(f"\n=== QUESTION-LEVEL TRANSITIONS ({label}) ===")
        print(f"Eligible rows: {report['eligible_rows']}")
        print("Stage\tPASS\tTOTAL\tRATE")
        for stage in STAGES:
            item = report["stage"][stage]
            print(f"{stage}\t{item['passed']}\t{item['total']}\t{_fmt_rate(item['rate'])}")
        print("\nAdjacent transition\tEligible\tSurvived\tConditional survival\tConditional failure")
        for name, item in report["transitions"].items():
            print(
                f"{name}\t{item['eligible_after_previous']}\t{item['survived_current']}\t"
                f"{_fmt_rate(item['conditional_survival'])}\t{_fmt_rate(item['conditional_failure'])}"
            )
        print("\nCUMULATIVE UPSTREAM CONDITIONALS (PRIMARY)\nTransition\tEligible after upstream\tSurvived\tConditional survival\tConditional failure")
        for name, item in report["cumulative_transitions"].items():
            print(
                f"{name}\t{item['eligible_after_upstream']}\t{item['survived_current']}\t"
                f"{_fmt_rate(item['conditional_survival'])}\t{_fmt_rate(item['conditional_failure'])}"
            )

        evidence = evidence_level_transition_stats(rows, gate_only)
        print(f"\n=== EVIDENCE-LEVEL TRANSITIONS ({label}) ===")
        print(f"Eligible evidence items: {evidence['eligible_evidence']}")
        print("Adjacent transition\tEligible\tSurvived\tConditional survival\tConditional failure")
        for name, item in evidence["transitions"].items():
            print(
                f"{name}\t{item['eligible_after_previous']}\t{item['survived_current']}\t"
                f"{_fmt_rate(item['conditional_survival'])}\t{_fmt_rate(item['conditional_failure'])}"
            )
        print("\nCUMULATIVE UPSTREAM CONDITIONALS (PRIMARY)\nTransition\tEligible after upstream\tSurvived\tConditional survival\tConditional failure")
        for name, item in evidence["cumulative_transitions"].items():
            print(
                f"{name}\t{item['eligible_after_upstream']}\t{item['survived_current']}\t"
                f"{_fmt_rate(item['conditional_survival'])}\t{_fmt_rate(item['conditional_failure'])}"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="results/oracle_experiments/comparison.jsonl",
        help="Path to strict-provenance comparison.jsonl",
    )
    parser.add_argument(
        "--output",
        default="results/oracle_experiments/transition_analysis.json",
        help="Output JSON path",
    )
    args = parser.parse_args()
    rows = load_rows(Path(args.input))
    print(f"Loaded {len(rows)} successful rows from {args.input}")
    if not rows:
        return

    all_rows = transition_stats(rows, False)
    sufficient_rows = transition_stats(rows, True)
    all_evidence = evidence_level_transition_stats(rows, False)
    sufficient_evidence = evidence_level_transition_stats(rows, True)
    result = {
        "input": args.input,
        "rows": len(rows),
        "question_level": {
            "all_rows": all_rows,
            "gate_sufficient_only": sufficient_rows,
        },
        "evidence_level": {
            "all_rows": all_evidence,
            "gate_sufficient_only": sufficient_evidence,
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print_report(rows)
    print(f"\nSaved JSON: {output}")


if __name__ == "__main__":
    main()
