"""Generate Stage 2 LSF/SSF calibration memories and a blind annotation sheet.

Selects 15 gold items (10 intentional, 5 epistemic) from the 40-item
calibration set, generates direct / recursive / source-peek memories with the
local writer, and writes a blind sheet plus a key outside the repository.

Usage:
    G:/aconda/python.exe -m experiments.stage2_lsf_ssf_generator
    G:/aconda/python.exe -m experiments.stage2_lsf_ssf_generator --limit-items 1 \
        --out-dir results/status_drift_v3_real_audit/stage2_lsf_ssf_smoke
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

from experiments.status_drift_recursive_pilot import USAGE_LOG, chat

SEED = 20261121
BUDGETS = [80, 60, 50, 45, 40]
DIRECT_BUDGET = 40
INTENTIONAL_N = 14
EPISTEMIC_N = 1
EXCLUDE_ITEMS = {"S2IE-003", "S2IE-021", "S2IE-026"}

SYSTEM_PROMPT = (
    "You maintain a long-term memory for a conversation. Compress the input "
    "into one concise English memory. Preserve important facts, the speaker's "
    "actions, and any conditions. Do not add advice or interpretations. "
    "Output only the memory."
)


def norm(value: str) -> str:
    return (value or "").strip()


def load_gold(root: Path) -> dict[str, dict[str, Any]]:
    rows_a = list(csv.DictReader((root / "annotator_A.csv").open(encoding="utf-8-sig")))
    rows_b = list(csv.DictReader((root / "annotator_B.csv").open(encoding="utf-8-sig")))
    b_map = {row["item_id"]: row for row in rows_b}
    adjudication = {}
    adj_path = root / "adjudication" / "adjudication_sheet.csv"
    if adj_path.exists():
        for row in csv.DictReader(adj_path.open(encoding="utf-8-sig")):
            adjudication[row["item_id"]] = row
    gold = {}
    for row in rows_a:
        item_id = row["item_id"]
        other = b_map[item_id]
        if item_id in adjudication:
            adj = adjudication[item_id]
            dimension = norm(adj["adjudicated_dimension"])
            status = norm(adj["adjudicated_status"])
            strength = norm(adj["adjudicated_strength"])
        elif (norm(row["gold_dimension"]) == norm(other["gold_dimension"])
              and norm(row["gold_status"]) == norm(other["gold_status"])):
            dimension = norm(row["gold_dimension"])
            status = norm(row["gold_status"])
            strength = norm(row["gold_strength"])
        else:
            continue
        if item_id in EXCLUDE_ITEMS:
            continue
        if dimension not in ("intentional", "epistemic"):
            continue
        if status.lower() in ("n/a", ""):
            continue
        gold[item_id] = {
            "item_id": item_id,
            "dimension": dimension,
            "status": status,
            "strength": strength,
            "target_sentence": row["target_sentence"],
            "context": row["context"],
            "later_mention": row.get("later_mention", ""),
        }
    return gold


def select(gold: dict[str, dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    buckets = {"intentional": [], "epistemic": []}
    for row in gold.values():
        buckets[row["dimension"]].append(row)
    for bucket in buckets.values():
        bucket.sort(key=lambda r: r["item_id"])
    chosen = []
    for dimension, n in (("intentional", INTENTIONAL_N), ("epistemic", EPISTEMIC_N)):
        pool = buckets[dimension][:]
        rng.shuffle(pool)
        chosen.extend(pool[:n])
    rng.shuffle(chosen)
    return chosen


def call_writer(source: str, budget: int, args: argparse.Namespace,
                tag: str, source_peek: bool = False,
                focus: bool = False) -> dict[str, Any]:
    focus_line = ""
    if focus:
        focus_line = (" The target turn in the conversation is marked with "
                      ">>; focus the memory on that turn's statement.")
    if source_peek:
        user = (
            f"Previous memory:\n{source}\n\n"
            "Rewrite the memory as one concise English memory. Use the original "
            "conversation below to keep the speaker's status accurate.\n\n"
            f"Original conversation:\n{args._dialogue}\n\n"
            f"At most {budget} words.{focus_line} Output only the memory."
        )
    elif args._rewrite:
        user = (
            f"Previous memory:\n{source}\n\n"
            f"Rewrite it as one concise English memory of at most {budget} words."
            f"{focus_line} Output only the memory."
        )
    else:
        user = (
            f"Conversation:\n{source}\n\n"
            f"Write one concise English memory of at most {budget} words."
            f"{focus_line} Output only the memory."
        )
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user}]
    memory = chat(args.base_url, args.writer_model, messages, args.timeout,
                  args.retries, args.seed, tag, "writer", temperature=0.0)
    usage = USAGE_LOG[-1] if USAGE_LOG else {}
    return {"memory": memory, "prompt_eval_count": usage.get("prompt_eval_count"),
            "eval_count": usage.get("eval_count"), "budget": budget}


def conditions(item: dict[str, Any], args: argparse.Namespace) -> dict[str, dict]:
    out = {}
    args._rewrite = False
    args._dialogue = item["context"]
    out["direct"] = call_writer(item["context"], DIRECT_BUDGET, args,
                                f"{item['item_id']}_direct", focus=True)
    memory = item["context"]
    stages = []
    for index, budget in enumerate(BUDGETS, 1):
        args._rewrite = index > 1
        stage = call_writer(memory, budget, args,
                            f"{item['item_id']}_recursive_{index}",
                            focus=(index == 1))
        stages.append(stage)
        memory = stage["memory"]
    out["recursive"] = {"memory": memory, "stages": stages}
    memory = item["context"]
    stages = []
    for index, budget in enumerate(BUDGETS, 1):
        args._rewrite = index > 1
        stage = call_writer(memory, budget, args,
                            f"{item['item_id']}_source_peek_{index}",
                            source_peek=(index > 1), focus=True)
        stages.append(stage)
        memory = stage["memory"]
    out["source_peek"] = {"memory": memory, "stages": stages}
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path("results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi")
    parser.add_argument("--gold-dir", type=Path, default=root)
    parser.add_argument("--out-dir", type=Path,
                        default=Path("results/status_drift_v3_real_audit/stage2_lsf_ssf"))
    parser.add_argument("--key", type=Path,
                        default=Path("G:/memory_failure_backup/stage2_lsf_ssf_key_2026-11-18.csv"))
    parser.add_argument("--writer-model", default="qwen2.5:7b")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--limit-items", type=int, default=0)
    args = parser.parse_args()

    gold = load_gold(args.gold_dir)
    chosen = select(gold, args.seed)
    if args.limit_items:
        chosen = chosen[:args.limit_items]
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    records = []
    for index, item in enumerate(chosen, 1):
        print(f"[{index}/{len(chosen)}] {item['item_id']}", flush=True)
        generated = conditions(item, args)
        for condition, result in generated.items():
            records.append({
                "source_item_id": item["item_id"],
                "condition": condition,
                "memory": result["memory"],
                "gold_dimension": item["dimension"],
                "gold_status": item["status"],
                "gold_strength": item["strength"],
                "target_sentence": item["target_sentence"],
                "context": item["context"],
                "later_mention": item["later_mention"],
                "stages": result.get("stages"),
            })
    with (out / "memories.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    rng = random.Random(args.seed + 1)
    rng.shuffle(records)
    sheet_columns = ["memory_id", "target_sentence", "context", "memory",
                     "lsf_outcome", "lexical_cue_in_memory", "ssf_outcome",
                     "status_assigned_from_memory", "proposition_identity_in_memory",
                     "ambiguity_reason", "notes"]
    key_rows, sheet_rows = [], []
    for index, record in enumerate(records, 1):
        memory_id = f"S2M-{index:03d}"
        sheet_rows.append({"memory_id": memory_id, **{k: record[k] for k in
                           ["target_sentence", "context", "memory"]},
                           "lsf_outcome": "", "lexical_cue_in_memory": "",
                           "ssf_outcome": "", "status_assigned_from_memory": "",
                           "proposition_identity_in_memory": "",
                           "ambiguity_reason": "", "notes": ""})
        key_rows.append({"memory_id": memory_id,
                         "source_item_id": record["source_item_id"],
                         "condition": record["condition"],
                         "gold_dimension": record["gold_dimension"],
                         "gold_status": record["gold_status"],
                         "gold_strength": record["gold_strength"],
                         "target_sentence": record["target_sentence"]})
    for name in ("sheet.csv", "annotator_A.csv", "annotator_B.csv"):
        with (out / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=sheet_columns)
            writer.writeheader()
            writer.writerows(sheet_rows)
    args.key.parent.mkdir(parents=True, exist_ok=True)
    with args.key.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(key_rows[0]))
        writer.writeheader()
        writer.writerows(key_rows)

    summary = {
        "items": len(chosen),
        "memories": len(records),
        "conditions": dict(Counter(record["condition"] for record in records)),
        "gold_dimensions": dict(Counter(record["gold_dimension"] for record in records)),
        "writer_model": args.writer_model,
        "budgets": {"direct": DIRECT_BUDGET, "chain": BUDGETS},
        "seed": args.seed,
        "key_sha256": hashlib.sha256(args.key.read_bytes()).hexdigest(),
        "note": "Blind memory sheet; condition and gold labels are only in the key.",
    }
    (out / "analysis").mkdir(exist_ok=True)
    (out / "analysis" / "generation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
