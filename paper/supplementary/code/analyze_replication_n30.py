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


def agreement(a_rows: list[dict], b_rows: list[dict]) -> dict:
    from experiments.check_v3_annotations import agreement as compute

    result = compute(a_rows, b_rows)
    kept = {}
    for field, value in result["fields"].items():
        kept[field] = {
            "n_pairs": value["n_pairs"],
            "raw_agreement": value["raw_agreement"],
            "cohen_kappa": value["cohen_kappa"],
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

    table = []
    for condition in CONDITIONS:
        group = by_condition[condition]
        values = [outcome(row) for row in group]
        n = len(group)
        table.append({
            "condition": condition,
            "n": n,
            "faithful_n": sum(value["faithful"] for value in values),
            "faithful_rate": sum(value["faithful"] for value in values) / n,
            "omission_n": sum(value["omission"] for value in values),
            "unsupported_n": sum(value["unsupported"] for value in values),
            "ambiguous_n": sum(value["ambiguous"] for value in values),
            "loss_n": sum(value["loss"] for value in values),
        })

    a_rows = []
    b_rows = []
    for name, directory in COHORTS.items():
        a_rows.extend(load(directory / "annotator_A.csv"))
        b_rows.extend(load(directory / "annotator_B.csv"))

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
        "agreement_pre_adjudication": agreement(a_rows, b_rows),
        "warnings": [
            "n = 12 is the pre-registered cohort; n = 30 adds 18 post-hoc trajectories.",
            "Adjudication is a model third-reviewer simulation; 50 disputes were resolved to A.",
            "Not independent human adjudication; not poolable with the primary qwen writer.",
        ],
    }
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote {out / 'condition_table.csv'} and {out / 'summary.json'}")
    for row in table:
        print(row)


if __name__ == "__main__":
    main()
