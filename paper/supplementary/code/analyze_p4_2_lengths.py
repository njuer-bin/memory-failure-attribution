"""V3.1 P4.2 variant-length check.

Recomputes the memory-variant length statistics quoted in the paper from the
frozen records, so the numbers have a reproducible artifact instead of being
typed into the manuscript.

Token unit: whitespace-separated tokens of the record's `memory` field (the
exact string handed to the agent). Each (scenario, variant) appears in both
request forms with the same memory, so the neutral form is read once.

The paper's length sentence is about the 34 over-commitment scenarios, so the
primary block uses that stratum. `all_54` is reported too: the earlier
manuscript values (15.7 / 9.4 / 10.3) reproduce only on this wider stratum,
which mixes in the 20 authorized controls and is the wrong denominator for the
over-commitment result.

Usage:
    python -m experiments.analyze_p4_2_lengths
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

DEFAULT_RUN = Path("results/status_drift_v3_p4_2_v3_v31/run")
DEFAULT_OUT = Path("results/status_drift_v3_p4_2_v3_v31/analysis/variant_length_check.json")
VARIANTS = ("present", "omitted", "distorted")


def load_records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def tokens(text: str) -> int:
    return len(text.split())


def rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = average
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float:
    rx, ry = rank(xs), rank(ys)
    n = len(rx)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def summarize(records: list[dict], label: str) -> dict:
    rows = [r for r in records if r["request_condition"] == "neutral"]
    lengths: dict[str, list[int]] = defaultdict(list)
    executed: dict[str, bool] = {}
    per_scenario: dict[str, dict[str, int]] = defaultdict(dict)
    for r in rows:
        if r["variant"] not in VARIANTS:
            continue
        n = tokens(r["memory"])
        lengths[r["variant"]].append(n)
        per_scenario[r["scenario_id"]][r["variant"]] = n
        if r["variant"] == "distorted":
            executed[r["scenario_id"]] = bool(r["unauthorized_execute"])

    means = {
        variant: {
            "mean_tokens": round(sum(v) / len(v), 3),
            "min": min(v),
            "max": max(v),
            "n": len(v),
        }
        for variant, v in lengths.items()
    }

    paired = [
        sid for sid, mem in per_scenario.items()
        if all(v in mem for v in VARIANTS) and sid in executed
    ]
    diffs = [per_scenario[sid]["distorted"] - per_scenario[sid]["present"] for sid in paired]
    outcomes = [1 if executed[sid] else 0 for sid in paired]
    return {
        "stratum": label,
        "n_scenarios": len(paired),
        "variants": means,
        "present_minus_distorted_tokens": round(
            means["present"]["mean_tokens"] - means["distorted"]["mean_tokens"], 3
        ),
        "spearman_length_diff_vs_distorted_execution": round(spearman(diffs, outcomes), 3),
        "distorted_executions": sum(outcomes),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--model", default="gemma3:12b")
    args = parser.parse_args()

    slug = args.model.replace(":", "_").replace(".", "_")
    path = args.run_dir / f"records_{slug}.jsonl"
    records = load_records(path)

    over = [r for r in records if r["control_type"] == "over_commitment"]
    result = {
        "source": str(path),
        "model": args.model,
        "token_unit": "whitespace tokens of the record memory field",
        "request_form": "neutral",
        "over_commitment": summarize(over, "over_commitment (paper denominator)"),
        "all_54": summarize(records, "all 54 scenarios incl. 20 controls"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
