"""Analyze the full 30-trajectory second-writer replication cohort.

The first 12 trajectories are the pre-registered cohort (``annotation_v325``);
the remaining 18 were annotated after the run (``annotation_v325_remaining``)
and form a post-hoc sensitivity cohort. Both adjudication files were completed
by a model third-reviewer simulation, so this analysis is not independent human
adjudication and must not be pooled with the primary qwen writer result.

Usage:
    python -m experiments.analyze_replication_n30 \
        --out-dir results/status_drift_v3_replication_writer/analysis_v325_full
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path("results/status_drift_v3_replication_writer")
COHORTS = {
    "n12_pre_registered": BASE / "annotation_v325",
    "n18_post_hoc": BASE / "annotation_v325_remaining",
}
CONDITIONS = ("direct", "recursive", "rewrite_matched", "repeated_direct",
              "neutral_source", "status_aware", "status_aware_source")
FIELDS = ("proposition_identity", "primary_dimension", "status_expressed",
          "expressed_status", "action_status", "evidence_support",
          "primary_judgment", "confidence")


def load(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def outcome(row: dict) -> dict[str, bool]:
    preserved = row["adj_proposition_identity"] == "PRESERVED"
    judgment = row["adj_primary_judgment"]
    return {
        "preserved": preserved,
        "loss": row["adj_proposition_identity"] in ("PARTIAL", "LOST", "AMBIGUOUS"),
        "faithful": preserved and judgment in ("NO_DISTORTION", "LEGITIMATE_UPDATE"),
        "omission": preserved and judgment == "STATUS_OMISSION",
        "unsupported": preserved and judgment == "UNSUPPORTED_STATUS_DISTORTION",
        "ambiguous": judgment == "AMBIGUOUS_UNASSESSABLE",
    }


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denominator
    return (max(0.0, centre - half), min(1.0, centre + half))


def agreement(a_rows: list[dict], b_rows: list[dict]) -> dict:
    from collections import Counter

    from experiments.check_v3_annotations import agreement as compute

    result = compute(a_rows, b_rows)
    a_map = {row["item_id"]: row for row in a_rows}
    b_map = {row["item_id"]: row for row in b_rows}
    common = sorted(set(a_map) & set(b_map))
    kept = {}
    for field, value in result["fields"].items():
        pairs = []
        for key in common:
            left, right = a_map[key], b_map[key]
            if not (left.get(field) or "").strip() or not (right.get(field) or "").strip():
                continue
            if field == "expressed_status" and (
                    (left.get("primary_dimension") or "").strip()
                    != (right.get("primary_dimension") or "").strip()):
                continue
            pairs.append((left[field].strip(), right[field].strip()))
        confusion: dict[str, dict[str, int]] = {}
        for label_a, label_b in pairs:
            confusion.setdefault(label_a, {})
            confusion[label_a][label_b] = confusion[label_a].get(label_b, 0) + 1
        kept[field] = {
            "n_pairs": value["n_pairs"],
            "raw_agreement": value["raw_agreement"],
            "cohen_kappa": value["cohen_kappa"],
            "label_counts_a": dict(Counter(label_a for label_a, _ in pairs)),
            "label_counts_b": dict(Counter(label_b for _, label_b in pairs)),
            "confusion_matrix": confusion,
        }
    return {"n_common_items": result["n_common_items"], "fields": kept}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default="results/status_drift_v3_replication_writer/analysis_v325_full",
    )
    args = parser.parse_args()

    rows: list[dict] = []
    cohort_counts = {}
    for name, directory in COHORTS.items():
        cohort_rows = load(directory / "adjudication.csv")
        for row in cohort_rows:
            row["cohort"] = name
        cohort_counts[name] = len(cohort_rows)
        rows.extend(cohort_rows)

    trajectories = {row["trajectory_id"] for row in rows}
    conditions = sorted({row["condition"] for row in rows})
    assert len(rows) == 210, len(rows)
    assert len(trajectories) == 30, len(trajectories)
    assert conditions == sorted(CONDITIONS), conditions

    by_condition = defaultdict(list)
    for row in rows:
        by_condition[row["condition"]].append(row)

    # Raw-to-summary reconciliation: every condition must hold 30 distinct
    # item ids, and the five reported categories must partition those items.
    reconciliation = {"conditions": {}, "checks": {}}
    seen_ids = [row["item_id"] for row in rows]
    reconciliation["checks"]["unique_item_ids"] = len(set(seen_ids)) == len(seen_ids)
    reconciliation["checks"]["item_count"] = len(rows)
    reconciliation["checks"]["trajectory_count"] = len(trajectories)
    reconciliation["checks"]["cohort_split"] = cohort_counts
    per_trajectory = defaultdict(set)
    for row in rows:
        per_trajectory[row["trajectory_id"]].add(row["condition"])
    reconciliation["checks"]["trajectories_complete"] = all(
        len(conditions) == len(CONDITIONS) for conditions in per_trajectory.values())

    table = []
    for condition in CONDITIONS:
        group = by_condition[condition]
        values = [outcome(row) for row in group]
        n = len(group)
        faithful_n = sum(value["faithful"] for value in values)
        loss_n = sum(value["loss"] for value in values)
        ambiguous_n = sum(value["ambiguous"] for value in values)
        category_sum = (faithful_n
                        + sum(value["omission"] for value in values)
                        + sum(value["unsupported"] for value in values)
                        + ambiguous_n + loss_n)
        preserved_n = n - loss_n
        joint_low, joint_high = wilson(faithful_n, n)
        cond_low, cond_high = wilson(faithful_n, preserved_n)
        reconciliation["conditions"][condition] = {
            "n": n,
            "distinct_item_ids": len({row["item_id"] for row in group}),
            "category_sum": category_sum,
            "partition_ok": category_sum == n,
            "preserved_n": preserved_n,
            "ambiguous_ids": [row["item_id"] for row, value in zip(group, values)
                              if value["ambiguous"]],
            "loss_ids": [row["item_id"] for row, value in zip(group, values)
                         if value["loss"]],
            "faithful_ids": [row["item_id"] for row, value in zip(group, values)
                             if value["faithful"]],
        }
        table.append({
            "condition": condition,
            "n": n,
            "faithful_n": faithful_n,
            "faithful_rate": faithful_n / n,
            "joint_fidelity_low": joint_low,
            "joint_fidelity_high": joint_high,
            "omission_n": sum(value["omission"] for value in values),
            "unsupported_n": sum(value["unsupported"] for value in values),
            "ambiguous_n": ambiguous_n,
            "loss_n": loss_n,
            "preserved_n": preserved_n,
            "conditional_status_fidelity": (faithful_n / preserved_n
                                            if preserved_n else None),
            "conditional_low": cond_low,
            "conditional_high": cond_high,
        })
    reconciliation["checks"]["all_conditions_30"] = all(
        entry["n"] == 30 for entry in reconciliation["conditions"].values())
    reconciliation["checks"]["all_partitions_ok"] = all(
        entry["partition_ok"] for entry in reconciliation["conditions"].values())

    a_rows = []
    b_rows = []
    agreement_by_cohort = {}
    for name, directory in COHORTS.items():
        cohort_a = load(directory / "annotator_A.csv")
        cohort_b = load(directory / "annotator_B.csv")
        agreement_by_cohort[name] = agreement(cohort_a, cohort_b)
        a_rows.extend(cohort_a)
        b_rows.extend(cohort_b)
    agreement_by_cohort["full_210"] = agreement(a_rows, b_rows)

    reliability = {}
    for name, data in agreement_by_cohort.items():
        field = data["fields"]["primary_judgment"]
        disagreements = sorted(
            ((label_a, label_b, count)
             for label_a, row in field["confusion_matrix"].items()
             for label_b, count in row.items() if label_a != label_b),
            key=lambda entry: -entry[2])
        reliability[name] = {
            "n_pairs": field["n_pairs"],
            "raw_agreement": field["raw_agreement"],
            "cohen_kappa": field["cohen_kappa"],
            "label_counts_a": field["label_counts_a"],
            "label_counts_b": field["label_counts_b"],
            "top_disagreements": disagreements[:8],
        }

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    with open(out / "condition_table.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)

    summary = {
        "cohort": "full 30 trajectories x 7 conditions = 210 items",
        "cohorts": cohort_counts,
        "judgment": dict(Counter(row["adj_primary_judgment"] for row in rows)),
        "identity": dict(Counter(row["adj_proposition_identity"] for row in rows)),
        "adjudicators": dict(Counter(row["adjudicator"] for row in rows)),
        "agreement_pre_adjudication": agreement_by_cohort["full_210"],
        "agreement_by_cohort": agreement_by_cohort,
        "reliability_by_cohort": reliability,
        "reconciliation": reconciliation,
        "warnings": [
            "n = 12 is the pre-registered cohort; n = 30 adds 18 post-hoc trajectories.",
            "Adjudication is a model third-reviewer simulation; 50 disputes were resolved to A.",
            "Not independent human adjudication; not poolable with the primary qwen writer.",
            "Condition counts partition all 30 items per condition; the ambiguous "
            "category is reported separately and must not be dropped from the table.",
        ],
    }
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "reconciliation.json").write_text(
        json.dumps(reconciliation, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "reliability_by_cohort.json").write_text(
        json.dumps(reliability, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote {out / 'condition_table.csv'} and {out / 'summary.json'}")
    for row in table:
        print(row)


if __name__ == "__main__":
    main()
