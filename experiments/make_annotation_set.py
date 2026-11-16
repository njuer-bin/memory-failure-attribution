"""Build the v2.4 human-annotation reliability set.

Usage:
    python -m experiments.make_annotation_set \
        --records results/status_drift_v2_pilot/v24_full/records.jsonl \
        --out-dir results/status_drift_v2_pilot/v24_full/annotation

Outputs:
- annotation_items.csv: one row per item, with memory and dialogue text.
- annotator_A.csv / annotator_B.csv: template rows with blank label fields.
- prevalence.json: gold-status counts for the reliability set.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

CONDITIONS = (("raw", None), ("direct", "5"), ("recursive", "5"), ("rewrite_matched", "5"))

TEMPLATE_FIELDS = [
    "trajectory_id", "dimension", "target_proposition", "condition", "depth",
    "annotator_id", "proposition_identity", "polarity", "epistemic_status",
    "intention_status", "action_status", "condition_status",
    "gold_final_status_from_dialogue", "evidence_turn_ids",
    "unsupported_status_change", "notes", "memory_text", "dialogue",
]


def reliability_items(rows: list[dict]) -> list[dict]:
    items = []
    for row in rows:
        for condition, depth in CONDITIONS:
            if condition == "raw":
                memory = row["dialogue"]
            else:
                memory = (row.get(f"{condition}_memories") or {}).get(depth, "")
            if not memory:
                continue
            items.append({
                "trajectory_id": row["sample_id"],
                "dimension": row["dimension"],
                "target_proposition": row["proposition"],
                "condition": condition,
                "depth": depth or "raw",
                "gold_final_status_from_dialogue": row["gold_status"],
                "evidence_turn_ids": ",".join(str(t) for t in row.get("evidence_turn_ids", [])),
                "memory_text": memory,
                "dialogue": row["dialogue"],
            })
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    rows = [json.loads(line) for line in open(args.records, encoding="utf-8") if line.strip()]
    items = reliability_items(rows)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    item_fields = ["trajectory_id", "dimension", "target_proposition", "condition",
                   "depth", "gold_final_status_from_dialogue", "evidence_turn_ids",
                   "memory_text", "dialogue"]
    with (out / "annotation_items.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=item_fields)
        writer.writeheader()
        writer.writerows(items)

    for annotator in ("A", "B"):
        with (out / f"annotator_{annotator}.csv").open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=TEMPLATE_FIELDS)
            writer.writeheader()
            for item in items:
                row = {field: "" for field in TEMPLATE_FIELDS}
                row.update({
                    "trajectory_id": item["trajectory_id"],
                    "dimension": item["dimension"],
                    "target_proposition": item["target_proposition"],
                    "condition": item["condition"],
                    "depth": item["depth"],
                    "annotator_id": annotator,
                    "gold_final_status_from_dialogue": item["gold_final_status_from_dialogue"],
                    "evidence_turn_ids": item["evidence_turn_ids"],
                    "memory_text": item["memory_text"],
                    "dialogue": item["dialogue"],
                })
                writer.writerow(row)

    prevalence = Counter(item["gold_final_status_from_dialogue"] for item in items)
    (out / "prevalence.json").write_text(
        json.dumps({"n_items": len(items), "gold_status_counts": dict(prevalence)},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"items: {len(items)}; annotator files: 2; out: {out}")


if __name__ == "__main__":
    main()
