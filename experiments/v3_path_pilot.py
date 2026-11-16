"""V3 P1a — within-condition path-replicate pilot.

For each trajectory, generate the same final budget through three different
intermediate schedules plus a direct reference. Measure whether final states
diverge across paths with the same source and final budget.

Usage:
    python -m experiments.v3_path_pilot --limit 12 --out-dir results/status_drift_v2_pilot/v3_path_pilot
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

from evaluation.status_cue_metrics import cue_state
from experiments.status_drift_recursive_pilot import (
    DIMENSIONS,
    TOPICS,
    _make_row,
    chat,
    det_condition_status,
    text_size,
    writer_prompt,
)

SCHEDULES = {
    "A": [220, 180, 140, 120, 100],
    "B": [220, 200, 160, 130, 100],
    "C": [220, 160, 150, 120, 100],
}
FINAL_BUDGET = 100


def build_trajectories(topics_count: int = 2) -> list[dict[str, Any]]:
    rows = []
    for dimension in DIMENSIONS:
        for topic_idx, action in enumerate(TOPICS[:topics_count]):
            for updated in (False, True):
                sample_id = f"{dimension}_{topic_idx:02d}_{'U' if updated else 'S'}"
                rows.append(_make_row(dimension, action, updated, sample_id, "v22"))
    return rows


def normalized_state(row: dict[str, Any], memory: str) -> str | None:
    dimension = row["dimension"]
    gold = row["gold_status"]
    if dimension == "conditional":
        status = det_condition_status(memory)
        return {"SATISFIED": "SATISFIED", "ACTIVE": "ACTIVE",
                "AMBIGUOUS": "AMBIGUOUS", "OMITTED": "ABSENT"}.get(status, status)
    state = cue_state(memory, dimension, gold)
    if state == "MATCH":
        return gold
    if state == "MIXED":
        return "AMBIGUOUS"
    if state == "OPPOSITE":
        opposite = {
            "CERTAIN": "POSSIBLE", "POSSIBLE": "CERTAIN",
            "COMMITTED": "CONSIDERING", "CONSIDERING": "COMMITTED",
        }
        return opposite.get(gold)
    return "ABSENT"


def path_divergence(states: list[str]) -> dict[str, Any]:
    n = len(states)
    if n < 2:
        return {"n": n, "pairwise_disagreement": None, "distinct": n,
                "path_dependence_index": None}
    pairs = list(itertools.combinations(states, 2))
    disagree = sum(a != b for a, b in pairs)
    counts = Counter(states)
    return {
        "n": n,
        "pairwise_disagreement": disagree / len(pairs),
        "distinct": len(counts),
        "path_dependence_index": 1 - max(counts.values()) / n,
    }


def run_schedule(dialogue: str, schedule: list[int], args, tag_prefix: str) -> list[str]:
    memory = dialogue
    memories = []
    for stage, budget in enumerate(schedule, 1):
        memory = chat(args.base_url, args.writer_model,
                      writer_prompt(memory, budget, args.writer_style),
                      args.timeout, args.retries, args.seed,
                      f"{tag_prefix}_stage{stage}", "writer")
        memories.append(memory)
    return memories


def topic_mentioned(row: dict[str, Any], memory: str) -> bool:
    keywords = row.get("proposition_keywords") or [row["proposition"]]
    return any(keyword in memory for keyword in keywords)


def run(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    trajectories = build_trajectories(args.topics)[:args.limit]
    records = []
    for index, row in enumerate(trajectories, 1):
        print(f"[{index}/{len(trajectories)}] {row['sample_id']}", flush=True)
        record: dict[str, Any] = {
            "sample_id": row["sample_id"], "dimension": row["dimension"],
            "proposition": row["proposition"], "gold_status": row["gold_status"],
            "has_legitimate_update": row["has_legitimate_update"],
            "dialogue": row["dialogue"], "paths": {}, "direct": {},
        }
        for name, schedule in SCHEDULES.items():
            memories = run_schedule(row["dialogue"], schedule, args, f"path_{name}")
            final = memories[-1]
            record["paths"][name] = {
                "memories": memories,
                "sizes": [text_size(memory) for memory in memories],
                "final_state": normalized_state(row, final),
                "topic_mentioned": topic_mentioned(row, final),
            }
        direct_memory = chat(args.base_url, args.writer_model,
                             writer_prompt(row["dialogue"], FINAL_BUDGET, args.writer_style),
                             args.timeout, args.retries, args.seed, "direct", "writer")
        record["direct"] = {
            "memory": direct_memory, "size": text_size(direct_memory),
            "final_state": normalized_state(row, direct_memory),
            "topic_mentioned": topic_mentioned(row, direct_memory),
        }
        path_states = [value["final_state"] for value in record["paths"].values()
                       if value["topic_mentioned"] and value["final_state"] is not None]
        record["path_divergence"] = path_divergence(path_states)
        record["path_states"] = {
            name: value["final_state"] for name, value in record["paths"].items()
        }
        record["direct_vs_paths"] = path_divergence(
            ([record["direct"]["final_state"]] if record["direct"]["topic_mentioned"] else [])
            + path_states)
        records.append(record)
        with (out_dir / "records.jsonl").open("a", encoding="utf-8") as out:
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    summary = summarize(records, args)
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def summarize(records: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    by_dimension = {}
    for dimension in DIMENSIONS:
        group = [row for row in records if row["dimension"] == dimension]
        divergences = [row["path_divergence"]["pairwise_disagreement"] for row in group
                       if row["path_divergence"]["pairwise_disagreement"] is not None]
        by_dimension[dimension] = {
            "n": len(group),
            "n_with_path_divergence": len(divergences),
            "mean_pairwise_disagreement": (sum(divergences) / len(divergences)
                                           if divergences else None),
            "any_divergence": sum(d > 0 for d in divergences),
            "topic_lost_paths": sum(1 for row in group
                                    for value in row["paths"].values()
                                    if not value["topic_mentioned"]),
        }
    all_divergences = [row["path_divergence"]["pairwise_disagreement"] for row in records
                       if row["path_divergence"]["pairwise_disagreement"] is not None]
    direct_divergences = [row["direct_vs_paths"]["pairwise_disagreement"] for row in records
                          if row["direct_vs_paths"]["pairwise_disagreement"] is not None]
    return {
        "protocol": "v3_path_replicate_pilot_v0",
        "writer_model": args.writer_model, "writer_style": args.writer_style,
        "seed": args.seed, "schedules": SCHEDULES, "final_budget": FINAL_BUDGET,
        "n_trajectories": len(records),
        "mean_pairwise_path_disagreement": (sum(all_divergences) / len(all_divergences)
                                            if all_divergences else None),
        "n_with_path_divergence": len(all_divergences),
        "any_path_divergence": sum(d > 0 for d in all_divergences),
        "mean_direct_vs_paths_disagreement": (sum(direct_divergences) / len(direct_divergences)
                                              if direct_divergences else None),
        "by_dimension": by_dimension,
        "warnings": [
            "Path divergence is measured by deterministic status cues, not human labels.",
            "Topic mention is a weak proposition proxy; topic-lost paths are excluded and counted.",
            "Schedules differ in intermediate budgets but share the final budget and source.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--topics", type=int, default=2)
    parser.add_argument("--writer-model", default="qwen2.5:7b")
    parser.add_argument("--writer-style", choices=("neutral", "status_aware"), default="neutral")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    (out_dir / "records.jsonl").unlink(missing_ok=True)
    run(args)


if __name__ == "__main__":
    main()
