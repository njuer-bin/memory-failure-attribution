"""Aggregate cross-system Failure Fingerprints from comparison artifacts.

Inputs are a systems run (multiple modes per row) and optionally the semantic
engine run for the same questions. The output is one row per system:
attributed accuracy, answer-failure distribution, stage recall and gate
distribution.

Usage:
    python -m experiments.analyze_systems \
        --systems results/systems_longmemeval_n50/comparison.jsonl \
        --semantic results/oracle_experiments_longmemeval_n200/comparison.jsonl \
        --semantic-mode real_memory
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

STAGES = ("formation", "storage", "retrieval", "rerank", "context")


def _load(path: Path) -> dict[str, dict[str, Any]]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict) and row.get("question_id"):
            rows[str(row["question_id"])] = row
    return rows


def _correct(answer: dict[str, Any]) -> bool:
    if answer.get("semantic_correct") is True:
        return True
    return answer.get("semantic_correct") is None and answer.get("correct") is True


def _stage_recall(mode: dict[str, Any], gold: list[dict[str, Any]], stage: str) -> float | None:
    entry = mode.get(stage)
    if not isinstance(entry, dict):
        return None
    if (entry.get("details") or {}).get("measured", True) is False:
        return None
    ids = {str(e.get("evidence_id")) for e in gold if e.get("evidence_id")}
    if not ids:
        return None
    found = {str(x) for x in (entry.get("found") or [])}
    return len(ids & found) / len(ids)


def _wilson(correct: int, n: int, z: float = 1.96) -> dict[str, float] | None:
    """95% Wilson interval for a binomial proportion (accuracy)."""
    if n <= 0:
        return None
    p = correct / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    margin = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denominator
    return {"low": max(0.0, centre - margin), "high": min(1.0, centre + margin)}


def summarize(rows: dict[str, dict[str, Any]], mode: str) -> dict[str, Any]:
    usable = [row for row in rows.values() if mode in (row.get("modes") or {})]
    n = len(usable)
    if not n:
        return {"n": 0}
    answers = [((row["modes"][mode].get("answer")) or {}) for row in usable]
    failures = [row["modes"][mode].get("answer_failure_type") or "none" for row in usable]
    gates = [((row["modes"][mode].get("evidence_sufficiency")) or {}).get("status") or "unknown"
             for row in usable]
    recalls = {}
    for stage in STAGES:
        values = [_stage_recall(row["modes"][mode], row.get("gold_evidence") or [], stage)
                  for row in usable]
        measured = [v for v in values if v is not None]
        recalls[stage] = sum(measured) / len(measured) if measured else None
    judged = [a for a in answers if a.get("semantic_correct") is not None]
    correct = sum(1 for a in answers if _correct(a))
    return {
        "n": n,
        "attributed_accuracy": correct / n,
        "accuracy_ci95": _wilson(correct, n),
        "semantic_judged": len(judged),
        "semantic_accuracy": (
            sum(1 for a in judged if a.get("semantic_correct")) / len(judged)
            if judged else None
        ),
        "failure_distribution": {
            label: failures.count(label) for label in sorted(set(failures))
        },
        "failure_share": {
            label: failures.count(label) / n for label in sorted(set(failures))
        },
        "gate_distribution": {label: gates.count(label) for label in sorted(set(gates))},
        "stage_recall": recalls,
    }


def analyze(systems_rows: dict[str, dict[str, Any]],
            semantic_rows: dict[str, dict[str, Any]] | None = None,
            semantic_mode: str = "real_memory",
            systems: tuple[str, ...] | None = None) -> dict[str, Any]:
    modes = systems
    if modes is None:
        modes = sorted({
            mode
            for row in systems_rows.values()
            for mode in (row.get("modes") or {})
        })
    result = {"systems": {}}
    for mode in modes:
        result["systems"][mode] = summarize(systems_rows, mode)
    if semantic_rows:
        shared = {qid: row for qid, row in semantic_rows.items() if qid in systems_rows}
        result["systems"]["semantic"] = summarize(shared, semantic_mode)
        result["semantic_questions_matched"] = len(shared)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--systems", required=True)
    parser.add_argument("--semantic", default=None)
    parser.add_argument("--semantic-mode", default="real_memory")
    parser.add_argument("--modes", default=None)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    systems = tuple(m.strip() for m in args.modes.split(",")) if args.modes else None
    result = analyze(
        _load(Path(args.systems)),
        _load(Path(args.semantic)) if args.semantic else None,
        args.semantic_mode,
        systems,
    )
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
