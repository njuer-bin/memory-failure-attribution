"""Analyze token usage from a status-drift run.

Usage: python -m experiments.analyze_token_usage <run_dir> [<run_dir> ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from experiments.status_drift_recursive_pilot import summarize_usage


def load_usage(run_dir: str | Path) -> list[dict]:
    path = Path(run_dir) / "usage.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def token_ranges(entries: list[dict], tag: str, role: str | None = None) -> dict | None:
    values = [entry.get("eval_count") for entry in entries
              if entry.get("tag") == tag
              and (role is None or entry.get("role") == role)
              and entry.get("eval_count") is not None]
    if not values:
        return None
    return {
        "calls": len(values),
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def main(paths: list[str]) -> None:
    for run_dir in paths:
        entries = load_usage(run_dir)
        print(f"\n=== {run_dir} ({len(entries)} calls) ===")
        if not entries:
            print("no usage.jsonl (run predates token logging)")
            continue
        summary = summarize_usage(entries)
        for tag in sorted(summary):
            value = summary[tag]
            print(f"{tag:<28} calls={value['calls']:<4} "
                  f"prompt_tokens={value['prompt_tokens']:<7} "
                  f"completion_tokens={value['completion_tokens']}")
        print("final-depth writer completion tokens:")
        for tag in ("direct_d5", "recursive_d5", "rewrite_matched_d5_step5"):
            value = token_ranges(entries, tag, "writer")
            if value:
                print(f"  {tag:<28} calls={value['calls']:<3} "
                      f"min={value['min']} max={value['max']} mean={value['mean']:.1f}")


if __name__ == "__main__":
    main(sys.argv[1:])
