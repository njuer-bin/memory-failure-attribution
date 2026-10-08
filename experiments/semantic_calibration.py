"""Post-hoc semantic evaluation of an existing oracle experiment.

This avoids re-running memory ingestion and answer generation. It reads the
existing comparison.jsonl, asks the local Ollama judge to evaluate each
already-generated answer against the question and Gold Evidence, then writes a
new comparison_semantic.jsonl and semantic_summary.json.

The purpose is to calibrate answer-level attribution before scaling the
benchmark.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.answer_semantic_eval import evaluate_answer


MODES = ("real_memory", "oracle_memory", "oracle_context")


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("_status", "ok") == "ok":
                rows.append(row)
    return rows


def judge_context(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": str(e.get("evidence_id") or ""),
            "content": str(e.get("text") or ""),
        }
        for e in row.get("gold_evidence", [])
        if e.get("text")
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="results/oracle_experiments/comparison.jsonl",
    )
    parser.add_argument(
        "--output",
        default="results/oracle_experiments/comparison_semantic.jsonl",
    )
    parser.add_argument(
        "--summary",
        default="results/oracle_experiments/semantic_summary.json",
    )
    args = parser.parse_args()

    rows = load_rows(Path(args.input))
    output = Path(args.output)
    summary_path = Path(args.summary)
    output.parent.mkdir(parents=True, exist_ok=True)

    counts = {
        mode: {"scored": 0, "correct": 0, "incorrect": 0, "errors": 0}
        for mode in MODES
    }
    attribution = {}

    with output.open("w", encoding="utf-8") as out:
        for i, row in enumerate(rows, 1):
            question = str(row.get("question") or "")
            evidence = judge_context(row)
            new_row = json.loads(json.dumps(row))

            print(f"[{i}/{len(rows)}] {row.get('question_id')}", flush=True)

            for mode in MODES:
                answer = new_row["modes"][mode].get("answer") or {}
                candidate = str(answer.get("answer") or "")
                try:
                    verdict = evaluate_answer(question, candidate, evidence)
                    answer["semantic_correct"] = verdict["correct"]
                    answer["semantic_reason"] = verdict["reason"]
                    answer["semantic_judge_model"] = verdict["model"]
                    counts[mode]["scored"] += 1
                    if verdict["correct"]:
                        counts[mode]["correct"] += 1
                    else:
                        counts[mode]["incorrect"] += 1
                except Exception as exc:
                    answer["semantic_correct"] = None
                    answer["semantic_error"] = f"{type(exc).__name__}: {exc}"
                    counts[mode]["errors"] += 1

                new_row["modes"][mode]["answer"] = answer

            # Recompute answer-level attribution using semantic correctness.
            real = new_row["modes"]["real_memory"]
            semantic_correct = real["answer"].get("semantic_correct")
            if semantic_correct is True:
                failure = None
            elif semantic_correct is False:
                gold_ids = {
                    str(e.get("evidence_id"))
                    for e in new_row.get("gold_evidence", [])
                    if e.get("evidence_id")
                }
                if not gold_ids:
                    failure = "F6_REASONING_CANDIDATE"
                else:
                    failure = None
                    for stage, label in (
                        ("formation", "F1_FORMATION"),
                        ("storage", "F2_STORAGE"),
                        ("evolution", "F3_EVOLUTION"),
                        ("retrieval", "F4_RETRIEVAL"),
                        ("rerank", "F4_RETRIEVAL"),
                        ("context", "F5_CONTEXT"),
                    ):
                        found = {
                            str(x)
                            for x in (real.get(stage) or {}).get("found", [])
                        }
                        if not gold_ids.issubset(found):
                            failure = label
                            break
                    if failure is None:
                        failure = "F6_REASONING_CANDIDATE"
            else:
                failure = None

            real["semantic_answer_failure_type"] = failure
            if failure:
                attribution[failure] = attribution.get(failure, 0) + 1

            out.write(json.dumps(new_row, ensure_ascii=False) + "\n")
            out.flush()

    summary = {
        "input": args.input,
        "output": args.output,
        "records": len(rows),
        "judge_model": counts["real_memory"].get("model"),
        "modes": counts,
        "real_memory_semantic_failure_distribution": attribution,
        "note": (
            "Semantic correctness is judged from question + Gold Evidence, "
            "without requiring lexical overlap with a benchmark reference answer. "
            "F6_REASONING_CANDIDATE is intentionally named as a candidate because "
            "semantic judge error and benchmark ambiguity cannot be fully eliminated."
        ),
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
