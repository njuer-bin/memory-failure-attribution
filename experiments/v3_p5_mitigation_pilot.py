"""V3 P5 mitigation pilot.

12 trajectories x 6 writer strategies under one chained budget schedule.
Deterministic diagnostics only; no human status-fidelity claim.

Usage:
    python -m experiments.v3_p5_mitigation_pilot \
        --records results/status_drift_v3_p2/records.jsonl \
        --out-dir results/status_drift_v3_p5_pilot
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
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
STRATEGIES = ("neutral", "status_aware", "unknown_heavy", "source_peek",
              "evidence_anchored", "transition_verification")
ABSTENTION_MARKERS = ("状态不明", "无法判断")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def strategy_prompt(source: str, budget: int, style: str) -> list[dict[str, str]]:
    if style in ("neutral", "status_aware"):
        return writer_prompt(source, budget, style)
    if style == "unknown_heavy":
        system = ("你负责维护长期对话记忆。请把输入压缩成一条简洁记忆，保留命题和条件。"
                  "如果输入没有明确的状态，写‘状态不明’，不要猜测；不要输出解释。")
    elif style == "evidence_anchored":
        system = ("你负责维护长期对话记忆。请把输入压缩成一条简洁记忆，保留命题、"
                  "确定性和条件状态。在记忆末尾用（依据：Turn X）标注支持该状态的轮次。"
                  "不得改变状态，不得补充推断；不要输出解释。")
    else:
        system = ("你负责维护长期对话记忆。请把输入压缩成一条简洁记忆，保留命题和重要信息。"
                  "不要输出解释。")
    user = f"请将以下内容压缩为不超过约 {budget} 个中文字符的一条记忆：\n\n{source}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def verifier_prompt(dialogue: str, memory: str, budget: int) -> list[dict[str, str]]:
    system = ("你是状态核对员。根据原始对话核对记忆是否保留命题、确定性和条件状态。"
              "若丢失或改变，按原文修正；否则原样返回。只输出记忆，不要解释。")
    user = (f"原始对话：\n{dialogue}\n\n待核对记忆：\n{memory}\n\n"
            f"请输出不超过约 {budget} 个中文字符的修正记忆。")
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _call(messages: list[dict[str, str]], args: argparse.Namespace,
          tag: str) -> dict[str, Any]:
    text = chat(args.base_url, args.writer_model, messages, args.timeout,
                args.retries, args.seed, tag, "writer", temperature=0.0)
    usage = USAGE_LOG[-1] if USAGE_LOG else {}
    return {"memory": text, "size": text_size(text),
            "eval_count": usage.get("eval_count"),
            "prompt_eval_count": usage.get("prompt_eval_count")}


def run_chain(row: dict[str, Any], strategy: str,
              args: argparse.Namespace) -> dict[str, Any]:
    memory = row["dialogue"]
    stages = []
    for index, budget in enumerate(SCHEDULE, 1):
        source = memory
        if strategy in ("source_peek", "evidence_anchored") and index > 1:
            source = memory + "\n\n[原始对话]\n" + row["dialogue"]
        writer = _call(strategy_prompt(source, budget, strategy), args,
                       f"{row['sample_id']}_{strategy}_s{index}")
        stage = {"stage": index, "budget": budget, "writer": writer,
                 "verifier": None, "final": writer["memory"]}
        if strategy == "transition_verification":
            verifier = _call(verifier_prompt(row["dialogue"], writer["memory"], budget),
                             args, f"{row['sample_id']}_{strategy}_v{index}")
            stage["verifier"] = verifier
            stage["final"] = verifier["memory"]
        stages.append(stage)
        memory = stage["final"]
    final = stages[-1]["final"]
    state = normalized_state(row, final)
    gold = row["gold_status"]
    relation = ("MATCH" if state == gold else
                "ABSENT" if state == "ABSENT" else
                "AMBIGUOUS" if state == "AMBIGUOUS" else "OPPOSITE")
    keywords = (row.get("proposition_keywords")
                or P2_KEYWORDS.get(row["proposition"], [row["proposition"]]))
    return {
        "strategy": strategy,
        "stages": stages,
        "final": final,
        "final_size": text_size(final),
        "state": state,
        "state_relation": relation,
        "topic_mentioned": any(keyword in final for keyword in keywords),
        "abstention": any(marker in final for marker in ABSTENTION_MARKERS),
        "writer_tokens": [stage["writer"].get("eval_count") for stage in stages],
        "verifier_tokens": [stage["verifier"].get("eval_count")
                            if stage["verifier"] else None for stage in stages],
        "timestamp": now(),
    }


def select_trajectories(rows: list[dict], limit: int) -> list[dict]:
    selected = []
    for dimension in ("epistemic", "intentional", "conditional"):
        group = [row for row in rows if row["dimension"] == dimension][:limit]
        selected.extend(group)
    return selected


def summarize(records: list[dict]) -> dict[str, Any]:
    by_strategy: dict[str, Any] = {}
    neutral_chars = None
    for strategy in STRATEGIES:
        entries = [record["conditions"][strategy] for record in records
                   if strategy in record["conditions"]]
        chars = [entry["final_size"]["characters"] for entry in entries]
        tokens = [token for entry in entries for token in entry["writer_tokens"]
                  if isinstance(token, int)]
        states = Counter(entry["state_relation"] for entry in entries)
        by_strategy[strategy] = {
            "n": len(entries),
            "state_relation": dict(states),
            "topic_mentioned_rate": (sum(1 for entry in entries
                                         if entry["topic_mentioned"]) / len(entries)
                                     if entries else None),
            "abstention_rate": (sum(1 for entry in entries
                                    if entry["abstention"]) / len(entries)
                                if entries else None),
            "mean_final_chars": statistics.mean(chars) if chars else None,
            "mean_writer_eval_tokens": statistics.mean(tokens) if tokens else None,
        }
        if strategy == "neutral":
            neutral_chars = by_strategy[strategy]["mean_final_chars"]
    if neutral_chars:
        for strategy, entry in by_strategy.items():
            entry["budget_inflation_vs_neutral"] = (
                entry["mean_final_chars"] / neutral_chars
                if entry["mean_final_chars"] is not None else None)
    by_dimension = {}
    for dimension in ("epistemic", "intentional", "conditional"):
        group = [record for record in records if record["dimension"] == dimension]
        by_dimension[dimension] = {
            strategy: dict(Counter(record["conditions"][strategy]["state_relation"]
                                   for record in group
                                   if strategy in record["conditions"]))
            for strategy in STRATEGIES
        }
    expected = len(records) * len(STRATEGIES)
    complete = sum(entry["n"] for entry in by_strategy.values())
    return {
        "protocol": "v3_p5_mitigation_pilot",
        "n_trajectories": len(records),
        "expected_conditions": expected,
        "complete_conditions": complete,
        "by_strategy": by_strategy,
        "by_dimension": by_dimension,
        "gate": {
            "all_trajectories_present": len(records) == 12,
            "all_strategies_complete": complete == expected,
            "max_budget_inflation": max(
                (entry.get("budget_inflation_vs_neutral") or 0)
                for entry in by_strategy.values()),
        },
        "warnings": [
            "Deterministic status cues are diagnostics, not human labels.",
            "Topic mention is a weak proposition proxy.",
            "unknown_heavy is a trivial-abstention control, not a mitigation.",
            "Pilot only; do not pool with P2/P3/P4 or v2.x.",
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
    rows = select_trajectories(rows, args.per_dimension)
    if args.limit:
        rows = rows[:args.limit]

    config = {
        "protocol": "v3_p5_mitigation_pilot",
        "frozen_protocol": "docs/research/V3_P5_PILOT_PROTOCOL.md",
        "writer_model": args.writer_model,
        "base_url": args.base_url,
        "schedule": SCHEDULE,
        "strategies": STRATEGIES,
        "abstention_markers": ABSTENTION_MARKERS,
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
        for strategy in STRATEGIES:
            result = run_chain(row, strategy, args)
            record["conditions"][strategy] = result
            print(f"  {strategy}: {result['state_relation']} "
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
    parser.add_argument("--writer-model", default="qwen2.5:7b")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--per-dimension", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
