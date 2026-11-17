"""Build the V3 P5 confirmatory blind annotation set.

Usage:
    python -m experiments.make_p5_confirmatory_set \
        --records results/status_drift_v3_p5/records.jsonl \
        --out-dir results/status_drift_v3_p5/annotation \
        --key-out G:/memory_failure_backup/v3_p5_confirmatory_key.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

LABEL_FIELDS = [
    "annotator_id", "proposition_identity", "primary_dimension",
    "status_expressed", "expressed_status", "action_status",
    "evidence_support", "primary_judgment", "subtype", "rationale",
    "confidence", "turn_references",
]
ITEM_FIELDS = ["item_id", "target_proposition", "target_question",
               "memory_text", "dialogue"]
KEY_FIELDS = ["item_id", "trajectory_id", "dimension", "topic", "gold_status",
              "has_legitimate_update", "condition", "final_chars", "eval_count",
              "topic_mentioned", "state", "state_relation"]


def target_question(proposition: str) -> str:
    return (f"目标命题：{proposition}。"
            "请判断记忆是否保留该命题及其在对话中的状态。")


def build_items(records: list[dict], seed: int = 20261120,
                prefix: str = "P5C") -> list[dict]:
    items = []
    for record in records:
        for condition, entry in record["conditions"].items():
            final = entry.get("final")
            if not final:
                continue
            stage = (entry.get("stages") or [{}])[-1]
            items.append({
                "trajectory_id": record["sample_id"],
                "dimension": record["dimension"],
                "topic": record["proposition"],
                "gold_status": record["gold_status"],
                "has_legitimate_update": record["has_legitimate_update"],
                "target_proposition": record["proposition"],
                "target_question": target_question(record["proposition"]),
                "memory_text": final,
                "dialogue": record["dialogue"],
                "condition": condition,
                "final_chars": entry.get("final_size", {}).get("characters"),
                "eval_count": stage.get("eval_count"),
                "topic_mentioned": entry.get("topic_mentioned"),
                "state": entry.get("state"),
                "state_relation": entry.get("state_relation"),
            })
    random.Random(seed).shuffle(items)
    for index, item in enumerate(items, 1):
        item["item_id"] = f"{prefix}-{index:04d}"
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--seed", type=int, default=20261120)
    parser.add_argument("--prefix", default="P5C")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--key-out", default=None)
    args = parser.parse_args()

    records = [json.loads(line) for line in open(args.records, encoding="utf-8")
               if line.strip()]
    if args.limit:
        records = records[:args.limit]
    items = build_items(records, args.seed, args.prefix)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    with (out / "annotation_items.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ITEM_FIELDS)
        writer.writeheader()
        writer.writerows([{key: item[key] for key in ITEM_FIELDS} for item in items])

    for annotator in ("A", "B"):
        with (out / f"annotator_{annotator}.csv").open("w", encoding="utf-8-sig",
                                                       newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["item_id"] + LABEL_FIELDS + ITEM_FIELDS[1:])
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
    with key_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=KEY_FIELDS)
        writer.writeheader()
        for item in items:
            writer.writerow({key: item[key] for key in KEY_FIELDS})

    prevalence = {
        "n_items": len(items),
        "conditions": dict(Counter(item["condition"] for item in items)),
        "dimensions": dict(Counter(item["dimension"] for item in items)),
        "gold_status": dict(Counter(item["gold_status"] for item in items)),
    }
    (out / "prevalence.json").write_text(
        json.dumps(prevalence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"items: {len(items)}; out: {out}; key: {key_path}")


if __name__ == "__main__":
    main()
