"""Freeze a reviewed multi-hop CSV into a structure-aware derived dataset.

The original human annotation CSV is never modified. This script adds an
explicit evidence_structure field so relational chains are not conflated with
multi-evidence aggregation.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

CHAIN_IDS = {"conv-26#q0011", "conv-26#q0059"}
AMBIGUOUS_IDS = {"conv-26#q0041"}


def classify(row: dict[str, str]) -> tuple[str, str]:
    """Return (structure, adjudication_note) without changing source labels."""
    question_id = row["question_id"]
    human_label = row["human_is_multi_hop"].strip().lower()

    if question_id in CHAIN_IDS:
        return "chain", "Confirmed relational/co-reference chain from human review."
    if question_id in AMBIGUOUS_IDS:
        return "uncertain", "Requires adjudication: supplied text evidence does not establish the image-dependent answer/path."
    if human_label == "yes":
        return "aggregation", "Multiple independent evidence items jointly support enumeration/counting/set-style answer; not a relational chain."
    if human_label == "uncertain":
        return "uncertain", "Human review marked evidence/path as uncertain; do not infer a chain."
    if human_label == "no":
        return "single", "Human review found no multi-evidence relational dependency."
    raise ValueError(f"Unsupported human_is_multi_hop value: {row['human_is_multi_hop']!r}")


def freeze(input_path: Path, output_path: Path) -> int:
    with input_path.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header")
        required = {"question_id", "human_is_multi_hop", "human_hop_count", "human_hop_type"}
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        rows = list(reader)

    fieldnames = list(reader.fieldnames)
    insert_at = fieldnames.index("human_is_multi_hop") + 1
    for name in ("evidence_structure", "structure_adjudication"):
        if name in fieldnames:
            fieldnames.remove(name)
    fieldnames[insert_at:insert_at] = ["evidence_structure", "structure_adjudication"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            structure, note = classify(row)
            row["evidence_structure"] = structure
            row["structure_adjudication"] = note
            writer.writerow(row)

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="results/multihop_candidates/locomo_refined_public_human_review_annotated.csv",
    )
    parser.add_argument(
        "--output",
        default="results/multihop_candidates/locomo_refined_public_human_review_frozen.csv",
    )
    args = parser.parse_args()
    count = freeze(Path(args.input), Path(args.output))
    print(f"Frozen {count} rows -> {args.output}")


if __name__ == "__main__":
    main()
