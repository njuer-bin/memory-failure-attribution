"""Analyze V3 P5 confirmatory human labels (2x2 prompt x source).

Usage:
    python -m experiments.analyze_p5_confirmatory_outcomes \
        --adjudication results/status_drift_v3_p5/annotation/adjudication.csv \
        --out-dir results/status_drift_v3_p5/analysis
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

CONDITIONS = ("neutral", "status_aware", "neutral_source", "status_aware_source")
OUTCOMES = ("faithful", "omission", "unsupported", "loss", "ambiguous")
CONTRASTS = (
    ("status_aware", "neutral"),
    ("neutral_source", "neutral"),
    ("status_aware_source", "status_aware"),
    ("status_aware_source", "neutral_source"),
    ("status_aware_source", "neutral"),
)
SEED = 20261120


def outcome(row: dict) -> dict[str, bool]:
    identity = row["adj_proposition_identity"]
    judgment = row["adj_primary_judgment"]
    return {
        "preserved": identity == "PRESERVED",
        "loss": identity in ("PARTIAL", "LOST", "AMBIGUOUS"),
        "faithful": judgment in ("NO_DISTORTION", "LEGITIMATE_UPDATE"),
        "omission": judgment == "STATUS_OMISSION",
        "unsupported": judgment == "UNSUPPORTED_STATUS_DISTORTION",
        "ambiguous": judgment == "AMBIGUOUS_UNASSESSABLE",
    }


def rate(rows: list[dict], key: str) -> dict:
    values = [outcome(row) for row in rows]
    if key in ("faithful", "omission", "unsupported", "ambiguous"):
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

    by_condition = {}
    for condition in CONDITIONS:
        group = [row for row in rows if row["condition"] == condition]
        by_condition[condition] = {
            "n": len(group),
            "identity": dict(Counter(row["adj_proposition_identity"] for row in group)),
            "judgment": dict(Counter(row["adj_primary_judgment"] for row in group)),
            **{key: rate(group, key) for key in OUTCOMES},
        }

    by_trajectory: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        by_trajectory[row["trajectory_id"]][row["condition"]] = row

    contrasts = []
    for condition, reference in CONTRASTS:
        for key in ("faithful", "omission", "unsupported", "loss"):
            diffs = []
            for trajectory, conditions in by_trajectory.items():
                if condition not in conditions or reference not in conditions:
                    continue
                diffs.append(float(outcome(conditions[condition])[key])
                             - float(outcome(conditions[reference])[key]))
            if not diffs:
                continue
            low, high = bootstrap_ci(diffs)
            contrasts.append({
                "condition": condition, "reference": reference, "outcome": key,
                "n_pairs": len(diffs), "mean_difference": sum(diffs) / len(diffs),
                "bootstrap_low": low, "bootstrap_high": high,
                "n_condition_positive": sum(1 for value in diffs if value > 0),
                "n_reference_positive": sum(1 for value in diffs if value < 0),
                "n_ties": sum(1 for value in diffs if value == 0),
            })

    # Interaction on faithful: (status_aware_source - status_aware) - (neutral_source - neutral)
    interaction_diffs = []
    for trajectory, conditions in by_trajectory.items():
        if not all(name in conditions for name in CONDITIONS):
            continue
        sa_source = float(outcome(conditions["status_aware_source"])["faithful"])
        sa = float(outcome(conditions["status_aware"])["faithful"])
        source = float(outcome(conditions["neutral_source"])["faithful"])
        neutral = float(outcome(conditions["neutral"])["faithful"])
        interaction_diffs.append((sa_source - sa) - (source - neutral))
    if interaction_diffs:
        low, high = bootstrap_ci(interaction_diffs)
        contrasts.append({
            "condition": "interaction", "reference": "faithful",
            "outcome": "faithful", "n_pairs": len(interaction_diffs),
            "mean_difference": sum(interaction_diffs) / len(interaction_diffs),
            "bootstrap_low": low, "bootstrap_high": high,
            "n_condition_positive": sum(1 for value in interaction_diffs if value > 0),
            "n_reference_positive": sum(1 for value in interaction_diffs if value < 0),
            "n_ties": sum(1 for value in interaction_diffs if value == 0),
        })

    summary = {
        "protocol": "v3_p5_confirmatory_human",
        "n_items": len(rows),
        "by_condition": by_condition,
        "contrasts": contrasts,
        "warnings": [
            "Adjudication is model-assisted; original A/B labels are preserved.",
            "Primary-judgment kappa 0.689 is below the calibration gate; treat as provisional.",
            "Rates over PRESERVED for faithful/omission/unsupported/ambiguous; loss over all items.",
            "Paired by trajectory (30 clusters); no power claim.",
            "Do not pool with P2/P3/P4 or the P5 pilot.",
        ],
    }
    (out / "p5_confirmatory_human_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    with (out / "condition_table.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["condition", "n", "preserved", "loss_n", "faithful_n",
                         "faithful_rate", "omission_n", "omission_rate",
                         "unsupported_n", "unsupported_rate", "ambiguous_n"])
        for condition, entry in by_condition.items():
            writer.writerow([
                condition, entry["n"],
                entry["n"] - entry["loss"]["count"], entry["loss"]["count"],
                entry["faithful"]["count"], entry["faithful"]["rate"],
                entry["omission"]["count"], entry["omission"]["rate"],
                entry["unsupported"]["count"], entry["unsupported"]["rate"],
                entry["ambiguous"]["count"],
            ])

    with (out / "paired_contrasts.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(contrasts[0]))
        writer.writeheader()
        writer.writerows(contrasts)

    print(json.dumps({condition: {
        "faithful": entry["faithful"], "omission": entry["omission"],
        "unsupported": entry["unsupported"], "loss": entry["loss"],
        "ambiguous": entry["ambiguous"]}
        for condition, entry in by_condition.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
