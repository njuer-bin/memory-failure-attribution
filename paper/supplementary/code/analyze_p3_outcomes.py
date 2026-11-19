"""Analyze V3 P3 human labels from the adjudicated P2 annotation set.

Reads `annotation/adjudication.csv`, writes summary tables under
`analysis/`. All rates report counts and denominators. Paired contrasts use
trajectory-level differences with a cluster bootstrap.

Usage:
    python -m experiments.analyze_p3_outcomes \
        --adjudication results/status_drift_v3_p2/annotation/adjudication.csv \
        --out-dir results/status_drift_v3_p2/analysis
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

CONDITIONS = ["raw", "direct", "recursive", "rewrite_matched", "repeated_direct",
              "source_peek", "para", "temp1", "temp2", "path_s2", "retrieval"]
CONTRASTS = [name for name in CONDITIONS if name != "recursive"]
OUTCOMES = ("loss", "unsupported", "omission", "faithful", "no_distortion", "lua")
SEED = 20261118


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def outcome(row: dict) -> dict[str, bool]:
    identity = row["adj_proposition_identity"]
    judgment = row["adj_primary_judgment"]
    preserved = identity == "PRESERVED"
    return {
        "preserved": preserved,
        "loss": identity in ("PARTIAL", "LOST", "AMBIGUOUS"),
        "unsupported": judgment == "UNSUPPORTED_STATUS_DISTORTION",
        "omission": judgment == "STATUS_OMISSION",
        "faithful": judgment in ("NO_DISTORTION", "LEGITIMATE_UPDATE"),
        "no_distortion": judgment == "NO_DISTORTION",
        "lua": judgment == "LEGITIMATE_UPDATE",
        "ambiguous": judgment == "AMBIGUOUS_UNASSESSABLE",
    }


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if n == 0:
        return None, None
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def rate(rows: list[dict], key: str, denominator: str = "n") -> dict:
    values = [outcome(row) for row in rows]
    if denominator == "preserved":
        denom = sum(1 for value in values if value["preserved"])
        count = sum(1 for value in values if value["preserved"] and value[key])
    else:
        denom = len(values)
        count = sum(1 for value in values if value[key])
    low, high = wilson(count, denom)
    return {"count": count, "denominator": denom,
            "rate": count / denom if denom else None,
            "wilson_low": low, "wilson_high": high}


def joint_category(row: dict) -> str:
    value = outcome(row)
    if value["loss"]:
        return "proposition_loss"
    if value["ambiguous"]:
        return "ambiguous_unassessable"
    if value["unsupported"]:
        return "preserved_unsupported"
    if value["omission"]:
        return "preserved_omission"
    if value["faithful"]:
        return "preserved_faithful"
    return "other"


def condition_table(rows: list[dict]) -> list[dict]:
    table = []
    for condition in CONDITIONS:
        group = [row for row in rows if row["condition"] == condition]
        entry = {"condition": condition, "n": len(group)}
        entry["identity"] = dict(Counter(row["adj_proposition_identity"] for row in group))
        entry["judgment"] = dict(Counter(row["adj_primary_judgment"] for row in group))
        entry["joint"] = dict(Counter(joint_category(row) for row in group))
        for key, denom in (("loss", "n"), ("unsupported", "preserved"),
                           ("omission", "preserved"), ("faithful", "preserved"),
                           ("no_distortion", "preserved"), ("lua", "preserved")):
            entry[key] = rate(group, key, denom)
        table.append(entry)
    return table


def dimension_table(rows: list[dict]) -> list[dict]:
    table = []
    for dimension in sorted({row["dimension"] for row in rows}):
        group = [row for row in rows if row["dimension"] == dimension]
        entry = {"dimension": dimension, "n": len(group)}
        entry["judgment"] = dict(Counter(row["adj_primary_judgment"] for row in group))
        for key, denom in (("loss", "n"), ("unsupported", "preserved"),
                           ("omission", "preserved"), ("faithful", "preserved")):
            entry[key] = rate(group, key, denom)
        table.append(entry)
    return table


def bootstrap_ci(diffs: list[float], n_boot: int = 10000,
                 seed: int = SEED) -> tuple[float, float]:
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        sample = [diffs[rng.randrange(len(diffs))] for _ in diffs]
        means.append(sum(sample) / len(sample))
    means.sort()
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot)]


def paired_contrasts(rows: list[dict]) -> list[dict]:
    by_trajectory: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        by_trajectory[row["trajectory_id"]][row["condition"]] = row
    results = []
    for condition in CONTRASTS:
        for outcome_key in ("loss", "unsupported", "omission", "faithful"):
            diffs = []
            for trajectory, conditions in by_trajectory.items():
                if condition not in conditions or "recursive" not in conditions:
                    continue
                left = outcome(conditions[condition])[outcome_key]
                right = outcome(conditions["recursive"])[outcome_key]
                diffs.append(float(left) - float(right))
            if not diffs:
                continue
            mean = sum(diffs) / len(diffs)
            low, high = bootstrap_ci(diffs)
            results.append({
                "condition": condition, "reference": "recursive",
                "outcome": outcome_key, "n_pairs": len(diffs),
                "mean_difference": mean,
                "bootstrap_low": low, "bootstrap_high": high,
                "n_condition_positive": sum(1 for value in diffs if value > 0),
                "n_reference_positive": sum(1 for value in diffs if value < 0),
                "n_ties": sum(1 for value in diffs if value == 0),
            })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adjudication", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    rows = load(args.adjudication)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    overall = {
        "n_items": len(rows),
        "identity": dict(Counter(row["adj_proposition_identity"] for row in rows)),
        "judgment": dict(Counter(row["adj_primary_judgment"] for row in rows)),
        "joint": dict(Counter(joint_category(row) for row in rows)),
        "by_condition": condition_table(rows),
        "by_dimension": dimension_table(rows),
        "paired_contrasts": paired_contrasts(rows),
        "warnings": [
            "Adjudication is model-assisted; original A/B labels are preserved.",
            "USDR/omission/faithful rates use PRESERVED as the denominator.",
            "PLR uses all items as the denominator.",
            "Paired contrasts are trajectory-level intention-to-treat differences.",
            "Unsupported distortion is rare; do not interpret a null as equivalence.",
            "P2 is not pooled with v2.x or P1.",
        ],
    }
    (out / "p3_summary.json").write_text(
        json.dumps(overall, ensure_ascii=False, indent=2), encoding="utf-8")

    with (out / "condition_table.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["condition", "n", "prop_loss_n", "prop_loss_rate",
                         "unsupported_n", "preserved_n", "usdr",
                         "omission_n", "omission_rate", "faithful_n",
                         "faithful_rate", "lua_n", "no_distortion_n"])
        for entry in overall["by_condition"]:
            writer.writerow([
                entry["condition"], entry["n"],
                entry["loss"]["count"], entry["loss"]["rate"],
                entry["unsupported"]["count"], entry["unsupported"]["denominator"],
                entry["unsupported"]["rate"],
                entry["omission"]["count"], entry["omission"]["rate"],
                entry["faithful"]["count"], entry["faithful"]["rate"],
                entry["lua"]["count"], entry["no_distortion"]["count"],
            ])

    with (out / "paired_contrasts.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(overall["paired_contrasts"][0]))
        writer.writeheader()
        writer.writerows(overall["paired_contrasts"])

    print(json.dumps({key: overall[key] for key in
                      ("n_items", "identity", "judgment", "joint")},
                     ensure_ascii=False, indent=2))
    print(f"\nwrote {out / 'p3_summary.json'}")


if __name__ == "__main__":
    main()
