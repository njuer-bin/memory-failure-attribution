"""Build the V3 blind annotation calibration set from a P1c path-pilot run.

Usage:
    python -m experiments.make_v3_annotation_set \
        --records results/status_drift_v2_pilot/v3_path_pilot_p1c/records.jsonl \
        --out-dir results/status_drift_v2_pilot/v3_path_pilot_p1c/annotation

Outputs:
- annotation_items.csv: item_id, neutral target question, memory, dialogue.
- annotator_A.csv / annotator_B.csv: blank label fields, self-contained.
- condition_key.csv: curator-only mapping to path/gold (do not give to annotators).
- prevalence.json: dimension and gold-status counts.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

from evaluation.status_cue_metrics import cue_state
from experiments.status_drift_recursive_pilot import det_condition_status

PATHS = ("S1", "S2", "PEEK", "PARA", "TEMP1", "TEMP2")

LABEL_FIELDS = [
    "annotator_id", "proposition_identity", "primary_dimension",
    "status_expressed", "expressed_status", "evidence_support",
    "primary_judgment", "subtype", "rationale", "confidence",
    "turn_references",
]

ITEM_FIELDS = ["item_id", "target_proposition", "target_question",
               "memory_text", "dialogue"]

KEY_FIELDS = ["item_id", "trajectory_id", "dimension", "gold_status", "path",
              "topic_mentioned", "deterministic_state", "path_spec"]


def select_records(rows: list[dict]) -> list[dict]:
    selected = []
    for dimension, count in (("epistemic", 4), ("intentional", 3), ("conditional", 3)):
        group = [row for row in rows if row["dimension"] == dimension]
        selected.extend(group[:count])
    return selected


def deterministic_state(row: dict, memory: str) -> str:
    if row["dimension"] == "conditional":
        return det_condition_status(memory)
    return cue_state(memory, row["dimension"], row["gold_status"])


def target_question(row: dict) -> str:
    # Neutral: do not reveal the dimension or the gold state. Annotators mark
    # applicable dimensions themselves.
    return (f"目标命题：{row['proposition']}。"
            "请判断记忆是否保留该命题及其在对话中的状态。")


def build_items(rows: list[dict], seed: int = 20261116) -> list[dict]:
    items = []
    for row in select_records(rows):
        for path in PATHS:
            path_record = (row.get("paths") or {}).get(path)
            if not path_record or not path_record.get("memories"):
                continue
            memory = path_record["memories"][-1]
            items.append({
                "trajectory_id": row["sample_id"],
                "dimension": row["dimension"],
                "target_proposition": row["proposition"],
                "target_question": target_question(row),
                "memory_text": memory,
                "dialogue": row["dialogue"],
                "gold_status": row["gold_status"],
                "path": path,
                "path_spec": path_record.get("spec"),
                "topic_mentioned": path_record.get("topic_mentioned"),
                "deterministic_state": deterministic_state(row, memory),
            })
    random.Random(seed).shuffle(items)
    for index, item in enumerate(items, 1):
        item["item_id"] = f"V3C-{index:04d}"
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--seed", type=int, default=20261116)
    parser.add_argument("--key-out", default=None,
                        help="Curator-only condition key path. Keep it outside the "
                             "repository for blind annotation.")
    args = parser.parse_args()

    rows = [json.loads(line) for line in open(args.records, encoding="utf-8")
            if line.strip()]
    items = build_items(rows, args.seed)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    with (out / "annotation_items.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ITEM_FIELDS)
        writer.writeheader()
        writer.writerows([{key: item[key] for key in ITEM_FIELDS} for item in items])

    for annotator in ("A", "B"):
        with (out / f"annotator_{annotator}.csv").open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["item_id"] + LABEL_FIELDS + ITEM_FIELDS[1:])
            writer.writeheader()
            for item in items:
                row = {field: "" for field in ["item_id"] + LABEL_FIELDS + ITEM_FIELDS[1:]}
                row.update({
                    "item_id": item["item_id"],
                    "annotator_id": annotator,
                    "target_proposition": item["target_proposition"],
                    "target_question": item["target_question"],
                    "memory_text": item["memory_text"],
                    "dialogue": item["dialogue"],
                })
                writer.writerow(row)

    key_path = Path(args.key_out) if args.key_out else out / "condition_key.csv"
    key_path.parent.mkdir(parents=True, exist_ok=True)
    with key_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=KEY_FIELDS)
        writer.writeheader()
        for item in items:
            writer.writerow({
                "item_id": item["item_id"],
                "trajectory_id": item["trajectory_id"],
                "dimension": item["dimension"],
                "gold_status": item["gold_status"],
                "path": item["path"],
                "topic_mentioned": item["topic_mentioned"],
                "deterministic_state": item["deterministic_state"],
                "path_spec": json.dumps(item["path_spec"], ensure_ascii=False),
            })

    prevalence = {
        "n_items": len(items),
        "dimensions": dict(Counter(item["dimension"] for item in items)),
        "paths": dict(Counter(item["path"] for item in items)),
        "gold_status": dict(Counter(item["gold_status"] for item in items)),
    }
    (out / "prevalence.json").write_text(json.dumps(prevalence, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(f"items: {len(items)}; annotator files: 2; out: {out}")


if __name__ == "__main__":
    main()
