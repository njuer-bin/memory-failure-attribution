"""Same-sample analysis of P2 intervention runs.

``run_interventions`` reports each arm on its own targeted subset, and those
subsets differ because routing depends on the per-question diagnostic path.
Cross-arm claims therefore have to be made on the intersection of questions
that were actually scored in every arm. This script recomputes both views from
``interventions.jsonl`` without re-running any model:

- per-arm targeted paired statistics (reproduces ``summary.json``);
- the common subset of questions scored in all requested arms;
- pairwise arm comparisons (repaired verdicts) on that common subset.

Usage:
    python -m experiments.analyze_interventions \
        --interventions results/interventions_longmemeval_n200/interventions.jsonl \
        --arms first_loss,path,agnostic
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

from evaluation.paired_stats import mcnemar_exact, paired_bootstrap_diff

ALL_ARMS = ("first_loss", "path", "agnostic")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and row.get("question_id"):
            rows.append(row)
    return rows


def _paired(row: dict[str, Any], key: str) -> Any:
    return ((row.get(key) or {}).get("semantic_correct"))


def _scored(row: dict[str, Any]) -> bool:
    return (
        not row.get("skipped")
        and bool(row.get("target_stage"))
        and _paired(row, "baseline") is not None
        and _paired(row, "repaired") is not None
    )


def by_question(rows: Iterable[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["question_id"]), {})[str(row.get("arm"))] = row
    return grouped


def common_questions(
    grouped: dict[str, dict[str, dict[str, Any]]], arms: Sequence[str]
) -> list[str]:
    return sorted(
        qid
        for qid, per_arm in grouped.items()
        if all(arm in per_arm and _scored(per_arm[arm]) for arm in arms)
    )


def _arm_table(qids: Sequence[str], per_q: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
    a = [_paired(per_q[qid], "baseline") for qid in qids]
    b = [_paired(per_q[qid], key) for qid in qids]
    return {
        "pairs": len(qids),
        "baseline_correct": sum(1 for x in a if x),
        "compared_correct": sum(1 for y in b if y),
        "baseline_accuracy": sum(1 for x in a if x) / len(qids) if qids else None,
        "compared_accuracy": sum(1 for y in b if y) / len(qids) if qids else None,
        "mcnemar": mcnemar_exact(a, b),
        "bootstrap_baseline_minus_compared": paired_bootstrap_diff(a, b),
    }


def analyze(rows: list[dict[str, Any]], arms: Sequence[str]) -> dict[str, Any]:
    grouped = by_question(rows)
    common = common_questions(grouped, arms)
    common_rows = {qid: grouped[qid] for qid in common}

    per_arm: dict[str, Any] = {}
    for arm in arms:
        arm_rows = [r for r in rows if str(r.get("arm")) == arm and _scored(r)]
        targeted = [r for r in arm_rows if r.get("target_stage")]
        per_arm[arm] = {
            "targeted_rows": len(targeted),
            "targeted": _arm_table(
                [str(r["question_id"]) for r in targeted],
                {str(r["question_id"]): r for r in targeted},
                "repaired",
            ),
            "common_subset": _arm_table(common, {q: common_rows[q][arm] for q in common}, "repaired"),
        }

    pairwise: dict[str, Any] = {}
    for i, arm_a in enumerate(arms):
        for arm_b in arms[i + 1:]:
            a = [_paired(common_rows[q][arm_a], "repaired") for q in common]
            b = [_paired(common_rows[q][arm_b], "repaired") for q in common]
            pairwise[f"{arm_a}_vs_{arm_b}"] = {
                "pairs": len(common),
                "accuracy_a": sum(1 for x in a if x) / len(common) if common else None,
                "accuracy_b": sum(1 for y in b if y) / len(common) if common else None,
                "mcnemar": mcnemar_exact(a, b),
                "bootstrap_a_minus_b": paired_bootstrap_diff(a, b),
            }

    return {
        "arms": list(arms),
        "questions_in_file": len(grouped),
        "common_questions": len(common),
        "per_arm": per_arm,
        "pairwise_common_subset": pairwise,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interventions", required=True)
    parser.add_argument("--arms", default=",".join(ALL_ARMS))
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    arms = tuple(a.strip() for a in args.arms.split(",") if a.strip())
    rows = _load_jsonl(Path(args.interventions))
    result = analyze(rows, arms)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
