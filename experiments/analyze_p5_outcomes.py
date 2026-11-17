"""Analyze V3 P5 human labels from the adjudicated mitigation pilot.

Usage:
    python -m experiments.analyze_p5_outcomes \
        --adjudication results/status_drift_v3_p5_pilot/annotation/adjudication.csv \
        --out-dir results/status_drift_v3_p5_pilot/analysis
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

STRATEGIES = ("neutral", "status_aware", "unknown_heavy", "source_peek",
              "evidence_anchored", "transition_verification")
OUTCOMES = ("faithful", "omission", "unsupported", "loss", "lua")
SEED = 20261119


def outcome(row: dict) -> dict[str, bool]:
    identity = row["adj_proposition_identity"]
    judgment = row["adj_primary_judgment"]
    return {
        "preserved": identity == "PRESERVED",
        "loss": identity in ("PARTIAL", "LOST", "AMBIGUOUS"),
        "faithful": judgment in ("NO_DISTORTION", "LEGITIMATE_UPDATE"),
        "omission": judgment == "STATUS_OMISSION",
        "unsupported": judgment == "UNSUPPORTED_STATUS_DISTORTION",
        "lua": judgment == "LEGITIMATE_UPDATE",
    }


def rate(rows: list[dict], key: str) -> dict:
    values = [outcome(row) for row in rows]
    if key in ("omission", "unsupported", "faithful", "lua"):
        denominator = sum(1 for value in values if value["preserved"])
        count = sum(1 for value in values if value["preserved"] and value[key])
    else:
        denominator = len(values)
        count = sum(1 for value in values if value[key])
    return {"count": count, "denominator": denominator,
            "rate": count / denominator if denominator else None}


def bootstrap_ci(diffs: list[float], n_boot: int = 10000,
                 seed: int = SEED) -> tuple[float, float]:
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        sample = [diffs[rng.randrange(len(diffs))] for _ in diffs]
        means.append(sum(sample) / len(sample))
    means.sort()
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adjudication", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    with open(args.adjudication, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    by_strategy = {}
    for strategy in STRATEGIES:
        group = [row for row in rows if row["strategy"] == strategy]
        by_strategy[strategy] = {
            "n": len(group),
            "identity": dict(Counter(row["adj_proposition_identity"] for row in group)),
            "judgment": dict(Counter(row["adj_primary_judgment"] for row in group)),
            **{key: rate(group, key) for key in OUTCOMES},
        }

    by_trajectory: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        by_trajectory[row["trajectory_id"]][row["strategy"]] = row
    contrasts = []
    for strategy in STRATEGIES:
        if strategy == "neutral":
            continue
        for key in ("faithful", "omission", "unsupported", "loss"):
            diffs = []
            for trajectory, conditions in by_trajectory.items():
                if strategy not in conditions or "neutral" not in conditions:
                    continue
                diffs.append(float(outcome(conditions[strategy])[key])
                             - float(outcome(conditions["neutral"])[key]))
            if not diffs:
                continue
            low, high = bootstrap_ci(diffs)
            contrasts.append({
                "strategy": strategy, "reference": "neutral", "outcome": key,
                "n_pairs": len(diffs), "mean_difference": sum(diffs) / len(diffs),
                "bootstrap_low": low, "bootstrap_high": high,
                "n_strategy_positive": sum(1 for value in diffs if value > 0),
                "n_reference_positive": sum(1 for value in diffs if value < 0),
                "n_ties": sum(1 for value in diffs if value == 0),
            })

    summary = {
        "protocol": "v3_p5_human",
        "n_items": len(rows),
        "by_strategy": by_strategy,
        "contrasts": contrasts,
        "warnings": [
            "Adjudication is model-assisted; original A/B labels are preserved.",
            "Rates are over PRESERVED for omission/unsupported/faithful/lua; loss over all items.",
            "n=12 per strategy; paired pilot estimates only, no power claim.",
            "The mitigation claim requires the P5 confirmatory design.",
        ],
    }
    (out / "p5_human_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    with (out / "strategy_table.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["strategy", "n", "preserved", "loss_n", "faithful_n",
                         "faithful_rate", "omission_n", "omission_rate",
                         "unsupported_n", "unsupported_rate", "lua_n"])
        for strategy, entry in by_strategy.items():
            writer.writerow([
                strategy, entry["n"],
                entry["n"] - entry["loss"]["count"], entry["loss"]["count"],
                entry["faithful"]["count"], entry["faithful"]["rate"],
                entry["omission"]["count"], entry["omission"]["rate"],
                entry["unsupported"]["count"], entry["unsupported"]["rate"],
                entry["lua"]["count"],
            ])

    with (out / "paired_contrasts.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(contrasts[0]))
        writer.writeheader()
        writer.writerows(contrasts)

    print(json.dumps({strategy: {
        "faithful": entry["faithful"], "omission": entry["omission"],
        "unsupported": entry["unsupported"], "loss": entry["loss"]}
        for strategy, entry in by_strategy.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
