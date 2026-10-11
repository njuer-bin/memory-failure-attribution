"""Post-hoc audit view for F6 candidates in an existing oracle experiment.

No model calls are made. The script only reads comparison.jsonl and prints the
fields needed to manually distinguish genuine downstream reasoning failures
from answer-scorer artifacts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("_status", "ok") == "ok":
                rows.append(row)
    return rows


def answer(row: dict[str, Any], mode: str) -> dict[str, Any]:
    return row.get("modes", {}).get(mode, {}).get("answer") or {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="results/oracle_experiments/comparison.jsonl",
        help="Path to comparison.jsonl",
    )
    args = parser.parse_args()

    rows = load_rows(Path(args.input))
    candidates = [
        row
        for row in rows
        if row.get("modes", {}).get("real_memory", {}).get("answer_failure_type")
        == "F6_REASONING"
    ]

    print(f"Loaded {len(rows)} successful rows; F6 candidates={len(candidates)}")
    print("=" * 88)

    for index, row in enumerate(candidates, 1):
        print(f"\n[{index}/{len(candidates)}] {row.get('question_id')}")
        print("QUESTION:", row.get("question", ""))
        print("REFERENCE:", row.get("gold_answer", "(not stored)"))

        print("GOLD EVIDENCE:")
        for evidence in row.get("gold_evidence", []):
            print(
                "  -",
                evidence.get("evidence_id"),
                "|",
                evidence.get("text", evidence.get("content", "")),
                "| timestamp=",
                evidence.get("timestamp"),
            )

        print("ANSWERS / SCORING:")
        for mode in ("real_memory", "oracle_memory", "oracle_context"):
            a = answer(row, mode)
            print(
                f"  {mode}: answer={a.get('answer')!r} "
                f"correct={a.get('correct')} "
                f"EM={a.get('exact_match')} "
                f"F1={a.get('token_f1')} "
                f"temporal={a.get('temporal_equivalent')} "
                f"anchor={a.get('temporal_anchor_date')} "
                f"phrase={a.get('phrase_match')}"
            )

        gate = row.get("modes", {}).get("real_memory", {}).get("evidence_sufficiency") or {}
        print("EVIDENCE GATE:")
        print(
            "  status=",
            gate.get("status"),
            "confidence=",
            gate.get("confidence"),
            "adjudication=",
            gate.get("adjudication"),
        )
        print("  reason=", gate.get("reason", ""))

        real = row.get("modes", {}).get("real_memory", {})
        print("LIFECYCLE:")
        for stage in ("formation", "storage", "evolution", "retrieval", "rerank", "context"):
            found = (real.get(stage) or {}).get("found", [])
            print(f"  {stage}: found={len(found)}")

        print("FINAL CONTEXT (real_memory):")
        context = real.get("context") or real.get("final_context") or []
        if isinstance(context, list):
            for item in context:
                if isinstance(item, dict):
                    text = item.get("content") or item.get("text") or ""
                    print("  -", text)
                else:
                    print("  -", item)
        else:
            print("  ", context)
        print("-" * 88)


if __name__ == "__main__":
    main()
