"""Build the blind annotation sheets for the 18 unannotated writer-replication
trajectories (v3.2.5 protocol).

The first 12 trajectories are already annotated in
`results/status_drift_v3_replication_writer/annotation_v325/`. This script
builds the matching sheets for the remaining 18 (126 items = 18 x 7
conditions), continuing the item numbering. Condition and gold status stay in a
separate `key.csv`; the annotator sheets contain no condition or gold columns.

Usage:
    G:/aconda/python.exe -m experiments.make_replication_annotation_remaining

Then hand `annotator_A.csv` and `annotator_B.csv` to two independent annotators.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import Counter
from pathlib import Path

DEFAULT_RECORDS = Path("results/status_drift_v3_replication_writer/records.jsonl")
DEFAULT_DONE = Path("results/status_drift_v3_replication_writer/annotation_v325/adjudication.csv")
DEFAULT_OUT = Path("results/status_drift_v3_replication_writer/annotation_v325_remaining")
SEED = 20261119

CONDITIONS = ("direct", "recursive", "rewrite_matched", "repeated_direct",
              "neutral_source", "status_aware", "status_aware_source")
LABEL_FIELDS = (
    "proposition_identity", "primary_dimension", "status_expressed",
    "expressed_status", "action_status", "evidence_support", "primary_judgment",
    "subtype", "rationale", "confidence", "turn_references",
)
SHEET_FIELDS = ["item_id", "annotator_id", *LABEL_FIELDS,
                "target_proposition", "target_question", "memory_text", "dialogue"]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def done_trajectories(path: Path) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {row["trajectory_id"] for row in csv.DictReader(handle)}


def next_index(path: Path) -> int:
    """Highest existing REPR-nnnn number, so the new sheet continues the series."""
    pattern = re.compile(r"REPR-(\d+)")
    highest = 0
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            match = pattern.fullmatch(row.get("item_id", ""))
            if match:
                highest = max(highest, int(match.group(1)))
    return highest


def build_items(records: list[dict], done: set[str], start: int) -> tuple[list[dict], int]:
    items = []
    number = start
    for record in records:
        if record["sample_id"] in done:
            continue
        for condition in CONDITIONS:
            block = record["conditions"][condition]
            number += 1
            items.append({
                "item_id": f"REPR-{number:04d}",
                "trajectory_id": record["sample_id"],
                "dimension": record["dimension"],
                "gold_status": record["gold_status"],
                "condition": condition,
                "target_proposition": record["proposition"],
                "target_question": (
                    f"目标命题：{record['proposition']}。"
                    "请判断记忆是否保留该命题及其在对话中的状态。"
                ),
                "memory_text": block["final"],
                "dialogue": record["dialogue"],
            })
    return items, number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--done", type=Path, default=DEFAULT_DONE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    records = load_jsonl(args.records)
    done = done_trajectories(args.done)
    items, _ = build_items(records, done, next_index(args.done))

    random.Random(SEED).shuffle(items)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    with (args.out_dir / "annotation_items.csv").open(
            "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "item_id", "target_proposition", "target_question", "memory_text", "dialogue"])
        writer.writeheader()
        writer.writerows({k: item[k] for k in writer.fieldnames} for item in items)

    for annotator in ("A", "B"):
        with (args.out_dir / f"annotator_{annotator}.csv").open(
                "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=SHEET_FIELDS)
            writer.writeheader()
            for item in items:
                row = {field: "" for field in SHEET_FIELDS}
                row.update({
                    "item_id": item["item_id"],
                    "annotator_id": annotator,
                    "target_proposition": item["target_proposition"],
                    "target_question": item["target_question"],
                    "memory_text": item["memory_text"],
                    "dialogue": item["dialogue"],
                })
                writer.writerow(row)

    with (args.out_dir / "key.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "item_id", "trajectory_id", "condition", "dimension", "gold_status"])
        writer.writeheader()
        writer.writerows({k: item[k] for k in writer.fieldnames} for item in items)

    prevalence = {
        "n_items": len(items),
        "n_trajectories": len({item["trajectory_id"] for item in items}),
        "gold_status_counts": dict(Counter(item["gold_status"] for item in items)),
        "condition_counts": dict(Counter(item["condition"] for item in items)),
        "item_id_range": [min(i["item_id"] for i in items),
                          max(i["item_id"] for i in items)] if items else [],
        "seed": SEED,
    }
    (args.out_dir / "prevalence.json").write_text(
        json.dumps(prevalence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(prevalence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
