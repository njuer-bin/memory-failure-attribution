"""Analyze a Real → Oracle-Memory → Oracle-Context ladder without model calls.

Combines the per-mode summaries and paired stage-distribution tests from
``experiments.analyze_systems`` with paired accuracy tests (McNemar exact +
paired bootstrap) on the same rows. Works on stored runs and on
abstention-corrected copies alike; ``semantic_correct`` is the label source.

Usage:
    python -m experiments.analyze_ladder \
        --comparison results/_corrected_comparison_locomo_n200.jsonl \
        --out results/analysis_ladder_locomo_n200_corrected.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.paired_stats import compare_modes
from experiments.analyze_systems import analyze


def _load(path: Path) -> dict[str, dict[str, Any]]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict) and row.get("question_id"):
            rows[str(row["question_id"])] = row
    return rows


def analyze_ladder(rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ordered = [row for row in rows.values()]
    present = {mode for row in ordered for mode in (row.get("modes") or {})}
    canonical = ["real_memory", "oracle_memory", "oracle_context"]
    modes = [m for m in canonical if m in present] + sorted(present - set(canonical))
    result = analyze(rows, systems=tuple(modes))
    paired = {}
    for i, mode_a in enumerate(modes):
        for mode_b in modes[i + 1:]:
            pair = compare_modes(ordered, mode_a, mode_b)
            paired[f"{mode_a}_vs_{mode_b}"] = {
                "table": pair["table"],
                "mcnemar": pair["mcnemar"],
                "bootstrap": pair["bootstrap"],
            }
    result["paired_accuracy"] = paired
    result["rows"] = len(ordered)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = analyze_ladder(_load(Path(args.comparison)))
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
