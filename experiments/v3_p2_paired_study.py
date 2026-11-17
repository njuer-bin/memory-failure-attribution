"""V3 P2 — paired transformation study.

Frozen confirmatory generation. Every trajectory is generated under all
predeclared conditions; see docs/research/V3_P2_PROTOCOL.md.

Usage:
    python -m experiments.v3_p2_paired_study --out-dir results/status_drift_v3_p2
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.status_drift_recursive_pilot import (
    DIMENSIONS,
    USAGE_LOG,
    chat,
    text_size,
    writer_prompt,
)

P2_TOPICS = ["换一份工作", "开始健身", "开一家网店", "学会游泳", "考驾照"]
P2_KEYWORDS = {
    "换一份工作": ["换一份工作", "换工作", "跳槽"],
    "开始健身": ["健身"],
    "开一家网店": ["开一家网店", "开网店", "网店"],
    "学会游泳": ["游泳"],
    "考驾照": ["驾照"],
}

FINAL_BUDGET = 100
STANDARD_SCHEDULE = [220, 180, 140, 120, 100]
PATH_S2_SCHEDULE = [220, 160, 150, 120, 100]

CONDITIONS: dict[str, dict[str, Any]] = {
    "direct": {"kind": "direct", "budget": FINAL_BUDGET, "style": "neutral",
               "temperature": 0.0, "seed": 42},
    "recursive": {"kind": "chain", "schedule": STANDARD_SCHEDULE,
                  "source_peek": False, "style": "neutral",
                  "temperature": 0.0, "seed": 42},
    "rewrite_matched": {"kind": "chain", "schedule": [220, 220, 220, 220, 100],
                        "source_peek": False, "style": "neutral",
                        "temperature": 0.0, "seed": 42},
    "repeated_direct": {"kind": "repeat_direct", "n": 5,
                        "budget": FINAL_BUDGET, "style": "neutral",
                        "temperature": 0.0, "seed": 42},
    "source_peek": {"kind": "chain", "schedule": STANDARD_SCHEDULE,
                    "source_peek": True, "style": "neutral",
                    "temperature": 0.0, "seed": 42},
    "para": {"kind": "chain", "schedule": STANDARD_SCHEDULE,
             "source_peek": False, "style": "neutral_paraphrase",
             "temperature": 0.0, "seed": 42},
    "temp1": {"kind": "chain", "schedule": STANDARD_SCHEDULE,
              "source_peek": False, "style": "neutral",
              "temperature": 0.7, "seed": 42},
    "temp2": {"kind": "chain", "schedule": STANDARD_SCHEDULE,
              "source_peek": False, "style": "neutral",
              "temperature": 0.7, "seed": 43},
    "path_s2": {"kind": "chain", "schedule": PATH_S2_SCHEDULE,
                "source_peek": False, "style": "neutral",
                "temperature": 0.0, "seed": 42},
    "retrieval": {"kind": "retrieval", "budget": FINAL_BUDGET},
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def prompt_hash(style: str) -> str:
    payload = json.dumps(writer_prompt("", FINAL_BUDGET, style),
                         ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def model_info(base_url: str, model: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/api/tags", timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        for entry in data.get("models", []):
            if entry.get("name") == model:
                return {"name": entry.get("name"), "digest": entry.get("digest"),
                        "modified_at": entry.get("modified_at")}
    except Exception as exc:
        return {"name": model, "error": f"{type(exc).__name__}: {exc}"}
    return {"name": model, "error": "model not listed"}


def _make_p2_row(dimension: str, action: str, updated: bool,
                 sample_id: str) -> dict[str, Any]:
    if dimension == "epistemic":
        initial = f"我可能会{action}，但现在还不能确定。"
        final = (f"我已经确认会{action}，这不是猜测了。" if updated
                 else f"目前仍然只是可能，我还没有确认会{action}。")
        gold, labels = ("CERTAIN" if updated else "POSSIBLE"), ("POSSIBLE", "CERTAIN")
    elif dimension == "intentional":
        initial = f"我正在考虑{action}，还没有作出决定。"
        final = (f"我已经决定要{action}，会按这个计划推进。" if updated
                 else f"我仍然只是在考虑{action}，没有作出承诺。")
        gold, labels = ("COMMITTED" if updated else "CONSIDERING"), ("CONSIDERING", "COMMITTED")
    else:
        initial = f"如果拿到奖学金，我才考虑{action}。"
        final = ("我已经拿到奖学金了，条件已经满足。" if updated
                 else "奖学金还没有结果，条件尚未满足。")
        gold, labels = (
            "CONDITION_SATISFIED" if updated else "CONDITION_ACTIVE",
            ("CONDITION_ACTIVE", "CONDITION_SATISFIED"),
        )
    turns = [
        {"turn_id": 1, "text": initial},
        {"turn_id": 2, "text": "顺便说一下，最近天气变化很大，我还在整理日程。"},
        {"turn_id": 3, "text": final},
        {"turn_id": 4, "text": "今天还处理了课程作业和一些日常事务。"},
    ]
    return {
        "sample_id": sample_id, "dimension": dimension, "proposition": action,
        "proposition_keywords": P2_KEYWORDS[action],
        "has_legitimate_update": updated, "gold_status": gold,
        "allowed_labels": list(labels), "evidence_turn_ids": [3] if updated else [1, 3],
        "turns": turns,
        "dialogue": "\n".join(f"[Turn {t['turn_id']}] {t['text']}" for t in turns),
    }


def build_trajectories() -> list[dict[str, Any]]:
    rows = []
    for topic_idx, action in enumerate(P2_TOPICS):
        for updated in (False, True):
            for dimension in DIMENSIONS:
                variant = "U" if updated else "S"
                rows.append(_make_p2_row(dimension, action, updated,
                                         f"p2_{dimension}_{topic_idx:02d}_{variant}"))
    return rows


def topic_mentioned(row: dict[str, Any], memory: str) -> bool:
    return any(keyword in memory for keyword in row["proposition_keywords"])


def _call(row: dict[str, Any], source: str, budget: int, style: str,
          temperature: float, seed: int, args: argparse.Namespace,
          tag: str) -> dict[str, Any]:
    memory = chat(args.base_url, args.writer_model,
                  writer_prompt(source, budget, style), args.timeout, args.retries,
                  seed, tag, "writer", temperature=temperature)
    usage = USAGE_LOG[-1] if USAGE_LOG else {}
    return {
        "memory": memory,
        "size": text_size(memory),
        "prompt_eval_count": usage.get("prompt_eval_count"),
        "eval_count": usage.get("eval_count"),
        "total_duration_ns": usage.get("total_duration_ns"),
        "prompt_hash": prompt_hash(style),
        "prompt_style": style,
        "budget": budget,
        "temperature": temperature,
        "seed": seed,
        "timestamp": now(),
    }


def lexical_retrieval(row: dict[str, Any], budget: int) -> dict[str, Any]:
    scored = []
    for turn in row["turns"]:
        score = sum(1 for keyword in row["proposition_keywords"]
                    if keyword in turn["text"])
        scored.append((score, turn["turn_id"], turn["text"]))
    ordered = sorted(scored, key=lambda item: (-item[0], item[1]))
    selected: list[tuple[int, str]] = []
    total = 0
    for score, turn_id, text in ordered:
        if score == 0 and selected:
            continue
        remaining = budget - total
        if remaining <= 0:
            break
        piece = text if len(text) <= remaining else text[:remaining]
        selected.append((turn_id, piece))
        total += len(piece)
    if not selected:
        selected = [(row["turns"][0]["turn_id"], row["turns"][0]["text"][:budget])]
    selected.sort()
    memory = "\n".join(f"[Turn {turn_id}] {text}" for turn_id, text in selected)
    return {
        "memory": memory,
        "size": text_size(memory),
        "retrieved_turn_ids": [turn_id for turn_id, _ in selected],
        "prompt_eval_count": None,
        "eval_count": None,
        "total_duration_ns": None,
        "prompt_hash": None,
        "prompt_style": "lexical_retrieval",
        "budget": budget,
        "temperature": None,
        "seed": None,
        "timestamp": now(),
    }


def run_condition(row: dict[str, Any], name: str, spec: dict[str, Any],
                  args: argparse.Namespace) -> dict[str, Any]:
    record: dict[str, Any] = {"spec": spec, "stages": [], "final": None,
                              "error": None, "complete": False}
    try:
        if name == "raw":
            record.update({"final": row["dialogue"], "complete": True,
                           "stages": [{"memory": row["dialogue"],
                                       "size": text_size(row["dialogue"])}]})
            return record
        if spec["kind"] == "direct":
            stage = _call(row, row["dialogue"], spec["budget"], spec["style"],
                          spec["temperature"], spec["seed"], args, f"{row['sample_id']}_{name}")
            record["stages"] = [stage]
            record["final"] = stage["memory"]
        elif spec["kind"] == "repeat_direct":
            stages = []
            for attempt in range(1, spec["n"] + 1):
                stages.append(_call(row, row["dialogue"], spec["budget"], spec["style"],
                                    spec["temperature"], spec["seed"], args,
                                    f"{row['sample_id']}_{name}_{attempt}"))
            record["stages"] = stages
            record["final"] = stages[-1]["memory"]
        elif spec["kind"] == "retrieval":
            stage = lexical_retrieval(row, spec["budget"])
            record["stages"] = [stage]
            record["final"] = stage["memory"]
        elif spec["kind"] == "chain":
            memory = row["dialogue"]
            stages = []
            for stage_index, budget in enumerate(spec["schedule"], 1):
                source = memory
                if spec.get("source_peek") and stage_index > 1:
                    source = memory + "\n\n[原始对话]\n" + row["dialogue"]
                stage = _call(row, source, budget, spec["style"],
                              spec["temperature"], spec["seed"], args,
                              f"{row['sample_id']}_{name}_stage{stage_index}")
                stages.append(stage)
                memory = stage["memory"]
            record["stages"] = stages
            record["final"] = stages[-1]["memory"]
        else:
            raise ValueError(f"unknown condition kind: {spec['kind']}")
        record["complete"] = bool(record["final"])
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
        if record["stages"]:
            record["final"] = record["stages"][-1].get("memory")
    return record


def run(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    records_path = out_dir / "records.jsonl"

    done: dict[str, dict[str, Any]] = {}
    if args.resume and records_path.exists():
        for line in records_path.open(encoding="utf-8"):
            if line.strip():
                record = json.loads(line)
                done[record["sample_id"]] = record

    trajectories = build_trajectories()
    if args.limit:
        trajectories = trajectories[:args.limit]
    config = {
        "protocol": "v3_p2_paired_study",
        "frozen_protocol": "docs/research/V3_P2_PROTOCOL.md",
        "annotation_guide": "docs/research/V3_ANNOTATION_GUIDELINES.md (v3.2.3)",
        "writer_model": args.writer_model,
        "model_info": model_info(args.base_url, args.writer_model),
        "base_url": args.base_url,
        "conditions": CONDITIONS,
        "final_budget": FINAL_BUDGET,
        "prompt_hashes": {style: prompt_hash(style)
                          for style in ("neutral", "neutral_paraphrase")},
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "started_at": now(),
        "n_trajectories": len(trajectories),
    }
    (out_dir / "run_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    records = []
    for index, row in enumerate(trajectories, 1):
        if row["sample_id"] in done:
            records.append(done[row["sample_id"]])
            print(f"[{index}/{len(trajectories)}] {row['sample_id']} (resumed)", flush=True)
            continue
        print(f"[{index}/{len(trajectories)}] {row['sample_id']}", flush=True)
        record: dict[str, Any] = {
            "sample_id": row["sample_id"], "dimension": row["dimension"],
            "proposition": row["proposition"], "gold_status": row["gold_status"],
            "has_legitimate_update": row["has_legitimate_update"],
            "dialogue": row["dialogue"], "conditions": {}, "raw": {},
        }
        record["raw"] = {"memory": row["dialogue"], "size": text_size(row["dialogue"]),
                         "topic_mentioned": topic_mentioned(row, row["dialogue"])}
        for name, spec in CONDITIONS.items():
            started = time.time()
            result = run_condition(row, name, spec, args)
            result["wall_time_s"] = round(time.time() - started, 3)
            result["topic_mentioned"] = (topic_mentioned(row, result["final"])
                                         if result["final"] else False)
            record["conditions"][name] = result
            print(f"  {name}: complete={result['complete']} "
                  f"error={result['error']}", flush=True)
        records.append(record)
        with records_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    summary = summarize(records)
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_condition: dict[str, dict[str, Any]] = {}
    for name in CONDITIONS:
        entries = [row["conditions"].get(name) for row in records]
        complete = [entry for entry in entries if entry and entry.get("complete")]
        errors = [entry["error"] for entry in entries if entry and entry.get("error")]
        sizes = [entry["final"] and entry["stages"][-1]["size"]["characters"]
                 for entry in complete]
        tokens = [entry["stages"][-1].get("eval_count") for entry in complete]
        token_values = [value for value in tokens if isinstance(value, int)]
        by_condition[name] = {
            "n": len(entries),
            "complete": len(complete),
            "missing": sum(1 for entry in entries if entry is None),
            "errors": len(errors),
            "error_examples": errors[:3],
            "mean_final_chars": statistics.mean(sizes) if sizes else None,
            "mean_final_eval_tokens": (statistics.mean(token_values)
                                       if token_values else None),
            "topic_mentioned_rate": (sum(1 for entry in complete
                                         if entry.get("topic_mentioned")) / len(complete)
                                     if complete else None),
        }
    expected = len(records) * len(CONDITIONS)
    complete_total = sum(value["complete"] for value in by_condition.values())
    return {
        "protocol": "v3_p2_paired_study",
        "n_trajectories": len(records),
        "expected_generated_conditions": expected,
        "complete_generated_conditions": complete_total,
        "missing_conditions": expected - complete_total,
        "raw_references": len(records),
        "by_condition": by_condition,
        "gate": {
            "all_trajectories_present": len(records) == 30,
            "all_conditions_complete": complete_total == expected,
            "error_rate": (sum(value["errors"] for value in by_condition.values())
                           / expected if expected else None),
        },
        "warnings": [
            "Topic mention is a lexical diagnostic, not proposition retention.",
            "Deterministic status cues are diagnostics; P3 human labels are primary.",
            "Do not drop outputs by length or content.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--writer-model", default="qwen2.5:7b")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--limit", type=int, default=0,
                        help="Debug only: generate the first N trajectories. "
                             "The confirmatory run uses all 30.")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
