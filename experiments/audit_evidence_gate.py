"""Audit E0 evidence-sufficiency decisions from an oracle experiment.

This is a post-hoc diagnostic tool. It does not call any model. It extracts
E0 samples from comparison.jsonl so the evidence gate can be calibrated on a
larger sample before running additional benchmark scale.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("_status", "ok") == "ok":
            rows.append(row)
    return rows


def gate(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("modes", {}).get("real_memory", {}).get("evidence_sufficiency") or {}


def stage_recall(row: dict[str, Any], mode: str) -> dict[str, float]:
    gold = {
        str(x["evidence_id"])
        for x in row.get("gold_evidence", [])
        if x.get("evidence_id")
    }
    result: dict[str, float] = {}
    for stage in ("formation", "storage", "evolution", "retrieval", "rerank", "context"):
        found = {
            str(x)
            for x in (row.get("modes", {}).get(mode, {}).get(stage) or {}).get("found", [])
        }
        result[stage] = len(gold & found) / len(gold) if gold else 1.0
    return result


def answer(row: dict[str, Any], mode: str) -> dict[str, Any]:
    return row.get("modes", {}).get(mode, {}).get("answer") or {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit E0 evidence-sufficiency decisions")
    parser.add_argument(
        "--input",
        default="results/oracle_experiments/comparison.jsonl",
        help="Path to comparison.jsonl",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Maximum number of E0 rows to print; 0 means all",
    )
    args = parser.parse_args()

    rows = load_rows(Path(args.input))
    e0 = [r for r in rows if gate(r).get("status") == "insufficient"]
    sufficient = [r for r in rows if gate(r).get("status") == "sufficient"]
    uncertain = [
        r for r in rows
        if gate(r).get("status") not in {"insufficient", "sufficient"}
    ]

    print("=" * 72)
    print("Evidence Gate Audit")
    print("=" * 72)
    print(f"Rows: {len(rows)}")
    print(f"E0 / insufficient: {len(e0)} ({len(e0) / len(rows):.1%})" if rows else "E0 / insufficient: 0")
    print(f"Sufficient: {len(sufficient)} ({len(sufficient) / len(rows):.1%})" if rows else "Sufficient: 0")
    print(f"Uncertain/error: {len(uncertain)}")

    reasons = Counter((gate(r).get("reason") or "(no reason)").strip() for r in e0)
    print("\n=== E0 REASON DISTRIBUTION ===")
    for reason, count in reasons.most_common():
        print(f"{count:>3} | {reason}")

    print("\n=== E0 SAMPLE AUDIT ===")
    selected = e0 if args.limit <= 0 else e0[: args.limit]
    for i, row in enumerate(selected, 1):
        qid = row.get("question_id")
        q = row.get("question", "")
        gold_answer = row.get("gold_answer", "")
        g = gate(row)
        real = answer(row, "real_memory")
        oracle = answer(row, "oracle_context")
        recall = stage_recall(row, "real_memory")

        print(f"\n[{i}] {qid}")
        print(f"Q: {q}")
        print(f"Gold answer: {gold_answer}")
        print(
            "Gate: "
            f"status={g.get('status')} confidence={g.get('confidence')} "
            f"adjudication={g.get('adjudication')}"
        )
        print(f"Reason: {g.get('reason', '')}")
        print(f"Real answer: {real.get('answer')!r}; correct={real.get('correct')}")
        print(f"Oracle context: {oracle.get('answer')!r}; correct={oracle.get('correct')}")
        print("Real stage recall:", ", ".join(f"{k}={v:.2f}" for k, v in recall.items()))
        print("Gold evidence:")
        evidence = row.get("gold_evidence", [])
        if not evidence:
            print("  (none)")
        else:
            for item in evidence:
                print(f"  - {item.get('text', '')}")

    print("\n=== E0 SUMMARY BY ORACLE-CONTEXT ANSWER ===")
    buckets = Counter()
    for row in e0:
        correct = answer(row, "oracle_context").get("correct")
        if correct is True:
            buckets["oracle_context_correct"] += 1
        elif correct is False:
            buckets["oracle_context_wrong"] += 1
        else:
            buckets["oracle_context_unscored"] += 1
    for key, count in buckets.items():
        print(f"{key}: {count}")

    print("\nInterpretation rule:")
    print("- This script does not relabel E0 automatically.")
    print("- oracle_context_correct inside E0 is a high-priority false-E0 candidate.")
    print("- oracle_context_wrong is consistent with evidence insufficiency, but still requires evidence inspection.")
    print("- Use this audit before changing the gate or scaling beyond the current sample.")


if __name__ == "__main__":
    main()
