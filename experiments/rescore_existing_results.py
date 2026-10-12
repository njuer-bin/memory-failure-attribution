"""Re-score existing oracle experiment rows without rerunning memory or LLM inference.

This utility is intentionally evaluator-only: it reads the persisted
``comparison.jsonl`` rows, applies the current deterministic answer scorer to
the already generated answers, recomputes answer failure attribution, and
writes a new aggregate. It does not rebuild MemoryEngine or call Ollama.
"""
from __future__ import annotations

import argparse
import copy
import json
from datetime import date
from pathlib import Path
from typing import Any

from evaluation.answer_generation import score_answer
from experiments.run_oracle_experiments import _answer_failure_type, _build_summary

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "oracle_experiments" / "comparison.jsonl"
DEFAULT_OUTPUT = ROOT / "results" / "oracle_experiments" / "comparison_rescored.jsonl"
DEFAULT_SUMMARY = ROOT / "results" / "oracle_experiments" / "summary_rescored.json"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _score_with_persisted_anchor(
    prediction: str,
    reference: str,
    previous_answer: dict[str, Any],
) -> dict[str, Any]:
    """Re-score while preserving the old context-derived anchor when available.

    Existing comparison rows do not persist the full final-context payload.
    They do persist ``temporal_anchor_date``. Reconstructing that date here
    preserves the old scorer's context anchor for ordinary relative-date cases,
    while the current scorer can additionally resolve explicit anchors contained
    in the benchmark reference itself (e.g. ``before 20 July 2023``).
    """
    anchor = previous_answer.get("temporal_anchor_date")
    context: list[dict[str, Any]] = []
    if anchor:
        context = [{"timestamp": str(anchor)}]
    return score_answer(prediction, reference, context=context)


def _rescore_mode(mode_data: dict[str, Any], reference: str) -> None:
    previous = copy.deepcopy(mode_data.get("answer") or {})
    prediction = previous.get("answer")
    if prediction is None:
        return

    scored = _score_with_persisted_anchor(str(prediction), reference, previous)
    for key in (
        "exact_match",
        "token_f1",
        "threshold",
        "temporal_equivalent",
        "temporal_anchor_date",
        "phrase_match",
        "explicit_date_mismatch",
        "correct",
    ):
        mode_data.setdefault("answer", {})[key] = scored.get(key)


def _recompute_failure_types(row: dict[str, Any]) -> None:
    gold = row.get("gold_evidence", [])
    for mode in ("real_memory", "oracle_memory", "oracle_context"):
        mode_data = row.get("modes", {}).get(mode)
        if not isinstance(mode_data, dict):
            continue
        mode_data["answer_failure_type"] = _answer_failure_type(
            {"gold_evidence": gold, "mode": mode, **mode_data}
        )


def rescore(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    summary_path: Path = DEFAULT_SUMMARY,
    *,
    dataset: str = "locomo_refined_public",
) -> dict[str, Any]:
    rows = _load_jsonl(input_path)
    rescored: list[dict[str, Any]] = []

    for row in rows:
        updated = copy.deepcopy(row)
        reference = str(updated.get("gold_answer") or "")
        modes = updated.get("modes") or {}
        for mode in ("real_memory", "oracle_memory", "oracle_context"):
            mode_data = modes.get(mode)
            if isinstance(mode_data, dict):
                _rescore_mode(mode_data, reference)
        _recompute_failure_types(updated)
        rescored.append(updated)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rescored:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = _build_summary(dataset, len(rescored), rescored, 0)
    summary["rescore"] = {
        "input": str(input_path),
        "output": str(output_path),
        "method": "deterministic answer-only rescore; no MemoryEngine or Ollama rerun",
        "scorer": "current evaluation.answer_generation.score_answer",
        "anchor_policy": "reuse persisted temporal_anchor_date when available; otherwise rely on explicit reference anchors",
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--dataset", default="locomo_refined_public")
    args = parser.parse_args()

    summary = rescore(
        Path(args.input),
        Path(args.output),
        Path(args.summary),
        dataset=args.dataset,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
