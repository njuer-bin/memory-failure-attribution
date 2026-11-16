"""Token-band matched analysis for the v2.9 experiment.

Usage: python -m experiments.analyze_token_band <run_dir> [--low 14] [--high 18]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluation.status_cue_metrics import cue_state

CONDITIONS = ("direct", "recursive", "rewrite_matched")


def load_records(run_dir: str | Path) -> list[dict]:
    path = Path(run_dir) / "records.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def final_tokens(row: dict, condition: str) -> int | None:
    return (row.get(f"{condition}_final_tokens") or {}).get("5")


def memory(row: dict, condition: str) -> str:
    return (row.get(f"{condition}_memories") or {}).get("5", "")


def eligible(row: dict) -> bool:
    return (bool(row.get("has_legitimate_update"))
            and row.get("dimension") in ("epistemic", "intentional"))


def token_stats(rows: list[dict], condition: str) -> dict | None:
    values = [t for row in rows if (t := final_tokens(row, condition)) is not None]
    if not values:
        return None
    return {"n": len(values), "mean": sum(values) / len(values),
            "min": min(values), "max": max(values)}


def band_stats(rows: list[dict], condition: str, low: int, high: int,
               in_band: bool = True, require_topic: bool = True) -> dict:
    items = []
    topic_lost = 0
    for row in rows:
        if not eligible(row):
            continue
        tokens = final_tokens(row, condition)
        if tokens is None:
            continue
        inside = low <= tokens <= high
        if inside != in_band:
            continue
        if require_topic and not (row.get(f"{condition}_topic_mention") or {}).get("5", False):
            topic_lost += 1
            continue
        items.append(row)
    absent = sum(1 for row in items
                 if cue_state(memory(row, condition), row["dimension"],
                              row["gold_status"]) == "ABSENT")
    return {"n": len(items), "absent": absent, "topic_lost": topic_lost,
            "rate": absent / len(items) if items else None}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir")
    parser.add_argument("--low", type=int, default=14)
    parser.add_argument("--high", type=int, default=18)
    args = parser.parse_args()
    rows = load_records(args.run_dir)

    print("=== achieved D5 writer tokens ===")
    for condition in CONDITIONS:
        print(f"{condition:<16} {token_stats(rows, condition)}")

    print(f"\n=== cue ABSENT in band [{args.low}, {args.high}] "
          f"(updated, topic-mentioned cases) ===")
    for condition in CONDITIONS:
        print(f"{condition:<16} {band_stats(rows, condition, args.low, args.high, True)}")

    print(f"\n=== cue ABSENT outside band [{args.low}, {args.high}] ===")
    for condition in CONDITIONS:
        print(f"{condition:<16} {band_stats(rows, condition, args.low, args.high, False)}")


if __name__ == "__main__":
    main()
