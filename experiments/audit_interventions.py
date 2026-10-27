"""Phase-0 (no new API calls) audit of the P2 intervention artifacts.

Everything here reads `interventions.jsonl` plus the baseline
`comparison.jsonl` that produced the routing labels. It answers the reviewer
questions that no new run can answer more cheaply:

- intention-to-treat effect (net flips / all questions, not just the subset);
- stale-label harm: do arm losses land on stored-failure questions that the
  fresh baseline already answers correctly?
- flip provenance: judge-decided vs deterministic-floor-decided flips;
- answer-length confound: length delta by flip direction;
- EVAL rows as a built-in negative control;
- Holm correction over the reported tests.

Usage:
    python -m experiments.audit_interventions \
        --interventions results/interventions_locomo_n200/interventions.jsonl \
        --baseline results/oracle_experiments_locomo_n200/comparison.jsonl
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any, Sequence

from experiments.analyze_interventions import by_question, common_questions, _load_jsonl

ALL_ARMS = ("first_loss", "path", "agnostic")
DETERMINISTIC = ("deterministic_temporal", "deterministic_numeric_range",
                 "deterministic_lexical", "lexical_anchor_override",
                 "ordering_refutation")


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values, same order as the input."""
    m = len(p_values)
    order = sorted(range(m), key=lambda i: p_values[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        value = (m - rank) * p_values[idx]
        running = max(running, value)
        adjusted[idx] = min(1.0, running)
    return adjusted


def _verdict(row: dict[str, Any], key: str) -> Any:
    return (row.get(key) or {}).get("semantic_correct")


def _len(row: dict[str, Any], key: str) -> int:
    return len(str((row.get(key) or {}).get("answer") or ""))


def _adjudication(row: dict[str, Any], key: str) -> str | None:
    return (row.get(key) or {}).get("semantic_adjudication")


def _targeted(grouped: dict[str, dict[str, Any]], arm: str) -> list[dict[str, Any]]:
    return [
        per_arm[arm]
        for per_arm in grouped.values()
        if arm in per_arm
        and not per_arm[arm].get("skipped")
        and per_arm[arm].get("target_stage")
        and _verdict(per_arm[arm], "baseline") is not None
        and _verdict(per_arm[arm], "repaired") is not None
    ]


def _failure_types(baseline_rows: list[dict[str, Any]]) -> dict[str, str]:
    return {
        str(row.get("question_id")): str(
            ((row.get("modes") or {}).get("real_memory") or {}).get("answer_failure_type") or ""
        )
        for row in baseline_rows
    }


def audit(
    rows: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]],
    arms: Sequence[str] = ALL_ARMS,
) -> dict[str, Any]:
    grouped = by_question(rows)
    total_questions = len(grouped) or len(baseline_rows)
    failure = _failure_types(baseline_rows)
    stale = set()

    per_arm: dict[str, Any] = {}
    for arm in arms:
        targeted = _targeted(grouped, arm)
        n01 = [r for r in targeted if _verdict(r, "baseline") is False and _verdict(r, "repaired") is True]
        n10 = [r for r in targeted if _verdict(r, "baseline") is True and _verdict(r, "repaired") is False]
        stale_qids = {
            str(r.get("question_id"))
            for r in targeted
            if r.get("stored_baseline_semantic_correct") is False
            and _verdict(r, "baseline") is True
        }
        stale.update(stale_qids)

        provenance = Counter()
        for r in n01:
            provenance[_adjudication(r, "repaired") or "unknown"] += 1
        for r in n10:
            provenance[_adjudication(r, "baseline") or "unknown"] += 1

        lengths = {
            "gained": [(_len(r, "repaired") - _len(r, "baseline")) for r in n01],
            "lost": [(_len(r, "repaired") - _len(r, "baseline")) for r in n10],
            "unchanged": [
                (_len(r, "repaired") - _len(r, "baseline"))
                for r in targeted if _verdict(r, "baseline") == _verdict(r, "repaired")
            ],
        }
        eval_rows = [r for r in targeted if failure.get(str(r.get("question_id"))) == "EVAL_SEMANTIC_UNCERTAIN"]

        per_arm[arm] = {
            "paired_rows": len(targeted),
            "net_flips": len(n01) - len(n10),
            "itt_accuracy_gain": (len(n01) - len(n10)) / total_questions,
            "stale_label_questions_targeted": len(stale_qids),
            "gains_on_stale_labels": sum(1 for r in n01 if str(r.get("question_id")) in stale_qids),
            "losses_on_stale_labels": sum(1 for r in n10 if str(r.get("question_id")) in stale_qids),
            "gain_losses_with_fresh_correct_baseline": len(n10),
            "flip_provenance": dict(provenance),
            "deterministic_flips": sum(v for k, v in provenance.items() if k in DETERMINISTIC),
            "answer_length_delta": {
                k: (mean(v) if v else None) for k, v in lengths.items()
            },
            "eval_negative_control": {
                "rows": len(eval_rows),
                "gains": sum(1 for r in eval_rows
                             if _verdict(r, "baseline") is False and _verdict(r, "repaired") is True),
                "losses": sum(1 for r in eval_rows
                              if _verdict(r, "baseline") is True and _verdict(r, "repaired") is False),
            },
        }

    # Pre-registered primary family: agnostic vs baseline, per benchmark.
    common = common_questions(grouped, arms)
    primary = {}
    for arm in arms:
        vals = [
            ((grouped[q][arm].get("baseline") or {}).get("semantic_correct"),
             (grouped[q][arm].get("repaired") or {}).get("semantic_correct"))
            for q in common
        ]
        vals = [(a, b) for a, b in vals if a is not None and b is not None]
        from evaluation.paired_stats import mcnemar_exact
        p = mcnemar_exact([a for a, _ in vals], [b for _, b in vals])["p_value"]
        primary[arm] = p
    adjusted = holm_adjust(list(primary.values()))
    primary_family = {
        arm: {"p_raw": primary[arm], "p_holm": adjusted[i]}
        for i, arm in enumerate(arms)
    }

    return {
        "questions": total_questions,
        "common_questions": len(common),
        "stale_label_questions": len(stale),
        "per_arm": per_arm,
        "primary_family_common_subset": primary_family,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interventions", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--arms", default=",".join(ALL_ARMS))
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    arms = tuple(a.strip() for a in args.arms.split(",") if a.strip())
    result = audit(
        _load_jsonl(Path(args.interventions)),
        _load_jsonl(Path(args.baseline)),
        arms,
    )
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
