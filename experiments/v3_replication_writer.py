"""V3 replication — writer side with a second model (gemma3:12b).

12 trajectories x 7 conditions covering the P2 mechanism contrasts and the P5
prompt/source 2x2. Deterministic diagnostics plus a blind annotation set.

Usage:
    python -m experiments.v3_replication_writer \
        --records results/status_drift_v3_p2/records.jsonl \
        --out-dir results/status_drift_v3_replication_writer
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.status_drift_recursive_pilot import (
    USAGE_LOG,
    chat,
    text_size,
    writer_prompt,
)
from experiments.v3_path_pilot import normalized_state
from experiments.v3_p2_paired_study import P2_KEYWORDS

SCHEDULE = [220, 180, 140, 120, 100]
CONDITIONS = {
    "direct": {"kind": "direct", "prompt": "neutral", "source_access": False},
    "recursive": {"kind": "chain", "prompt": "neutral", "source_access": False},
    "rewrite_matched": {"kind": "chain", "prompt": "neutral", "source_access": False,
                        "schedule": [220, 220, 220, 220, 100]},
    "repeated_direct": {"kind": "repeat_direct", "prompt": "neutral",
                        "source_access": False},
    "neutral_source": {"kind": "chain", "prompt": "neutral", "source_access": True},
    "status_aware": {"kind": "chain", "prompt": "status_aware",
                     "source_access": False},
    "status_aware_source": {"kind": "chain", "prompt": "status_aware",
                            "source_access": True},
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _call(row: dict[str, Any], source: str, budget: int, style: str,
          args: argparse.Namespace, tag: str) -> dict[str, Any]:
    text = chat(args.base_url, args.writer_model,
                writer_prompt(source, budget, style), args.timeout, args.retries,
                args.seed, tag, "writer", temperature=0.0)
    usage = USAGE_LOG[-1] if USAGE_LOG else {}
    return {"memory": text, "size": text_size(text),
            "eval_count": usage.get("eval_count"),
            "prompt_eval_count": usage.get("prompt_eval_count")}


def run_condition(row: dict[str, Any], name: str, spec: dict[str, Any],
                  args: argparse.Namespace) -> dict[str, Any]:
    stages = []
    if spec["kind"] == "direct":
        stage = _call(row, row["dialogue"], 100, spec["prompt"], args,
                      f"{row['sample_id']}_{name}")
        stages = [dict(stage, stage=1, budget=100)]
    elif spec["kind"] == "repeat_direct":
        for index in range(1, 6):
            stage = _call(row, row["dialogue"], 100, spec["prompt"], args,
                          f"{row['sample_id']}_{name}_{index}")
            stages.append(dict(stage, stage=index, budget=100))
    else:
        memory = row["dialogue"]
        schedule = spec.get("schedule") or SCHEDULE
        for index, budget in enumerate(schedule, 1):
            source = memory
            if spec["source_access"] and index > 1:
                source = memory + "\n\n[原始对话]\n" + row["dialogue"]
            stage = _call(row, source, budget, spec["prompt"], args,
                          f"{row['sample_id']}_{name}_s{index}")
            stages.append(dict(stage, stage=index, budget=budget))
            memory = stage["memory"]
    final = stages[-1]["memory"]
    state = normalized_state(row, final)
    gold = row["gold_status"]
    relation = ("MATCH" if state == gold else
                "ABSENT" if state == "ABSENT" else
                "AMBIGUOUS" if state == "AMBIGUOUS" else "OPPOSITE")
    keywords = (row.get("proposition_keywords")
                or P2_KEYWORDS.get(row["proposition"], [row["proposition"]]))
    return {
        "spec": spec,
        "stages": stages,
        "final": final,
        "final_size": text_size(final),
        "state": state,
        "state_relation": relation,
        "topic_mentioned": any(keyword in final for keyword in keywords),
        "timestamp": now(),
    }


def summarize(records: list[dict]) -> dict[str, Any]:
    by_condition = {}
    neutral_chars = None
    for name in CONDITIONS:
        entries = [record["conditions"][name] for record in records]
        chars = [entry["final_size"]["characters"] for entry in entries]
        tokens = [entry["stages"][-1].get("eval_count") for entry in entries
                  if isinstance(entry["stages"][-1].get("eval_count"), int)]
        by_condition[name] = {
            "n": len(entries),
            "state_relation": dict(Counter(entry["state_relation"] for entry in entries)),
            "topic_mentioned_rate": (sum(1 for entry in entries
                                         if entry["topic_mentioned"]) / len(entries)),
            "mean_final_chars": statistics.mean(chars) if chars else None,
            "mean_final_eval_tokens": statistics.mean(tokens) if tokens else None,
        }
        if name == "recursive":
            neutral_chars = by_condition[name]["mean_final_chars"]
    if neutral_chars:
        for entry in by_condition.values():
            entry["budget_inflation_vs_recursive"] = (
                entry["mean_final_chars"] / neutral_chars
                if entry["mean_final_chars"] is not None else None)
    expected = len(records) * len(CONDITIONS)
    complete = sum(entry["n"] for entry in by_condition.values())
    return {
        "protocol": "v3_replication_writer_gemma3_12b",
        "n_trajectories": len(records),
        "expected_conditions": expected,
        "complete_conditions": complete,
        "by_condition": by_condition,
        "gate": {
            "all_trajectories_present": len(records) == 12,
            "all_conditions_complete": complete == expected,
        },
        "warnings": [
            "Deterministic status cues are diagnostics, not human labels.",
            "Replication cohort: first 12 P2 trajectories.",
            "Do not pool with the qwen confirmatory runs.",
        ],
    }


def run(args: argparse.Namespace) -> None:
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    records_path = out / "records.jsonl"
    done: dict[str, dict] = {}
    if args.resume and records_path.exists():
        for line in records_path.open(encoding="utf-8"):
            if line.strip():
                record = json.loads(line)
                done[record["sample_id"]] = record

    rows = [json.loads(line) for line in open(args.records, encoding="utf-8")
            if line.strip()]
    if args.limit:
        rows = rows[:args.limit]

    config = {
        "protocol": "v3_replication_writer_gemma3_12b",
        "frozen_protocol": "docs/research/V3_REPLICATION_PROTOCOL.md",
        "writer_model": args.writer_model,
        "base_url": args.base_url,
        "conditions": CONDITIONS,
        "schedule": SCHEDULE,
        "seed": args.seed,
        "started_at": now(),
        "n_trajectories": len(rows),
    }
    (out / "run_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    records = []
    for index, row in enumerate(rows, 1):
        if row["sample_id"] in done:
            records.append(done[row["sample_id"]])
            print(f"[{index}/{len(rows)}] {row['sample_id']} (resumed)", flush=True)
            continue
        print(f"[{index}/{len(rows)}] {row['sample_id']}", flush=True)
        record = {"sample_id": row["sample_id"], "dimension": row["dimension"],
                  "proposition": row["proposition"], "gold_status": row["gold_status"],
                  "has_legitimate_update": row["has_legitimate_update"],
                  "dialogue": row["dialogue"], "conditions": {}}
        for name, spec in CONDITIONS.items():
            result = run_condition(row, name, spec, args)
            record["conditions"][name] = result
            print(f"  {name}: {result['state_relation']} "
                  f"chars={result['final_size']['characters']}", flush=True)
        records.append(record)
        with records_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    summary = summarize(records)
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--writer-model", default="gemma3:12b")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
