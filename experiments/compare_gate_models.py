"""Compare evidence-sufficiency judgments across semantic judge models.

This experiment reuses the existing oracle_experiments/comparison.jsonl output and
reruns ONLY the evidence-sufficiency gate for a curated set of manually audited
false-E0 candidates. The underlying memory traces and gold evidence are unchanged.

Usage:
    python -m experiments.compare_gate_models
    python -m experiments.compare_gate_models --models qwen2.5:7b gemma3:12b
    python -m experiments.compare_gate_models --ids q0000 q0002

The script intentionally does not modify the original comparison.jsonl results.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation import answer_semantic_eval as semantic_eval

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "oracle_experiments" / "comparison.jsonl"
OUT_DIR = ROOT / "results" / "gate_model_comparison"

# Manually audited E0 cases where the gold evidence appears directly relevant.
# Keep this list explicit so the sensitivity experiment is reproducible and does
# not silently change when the main experiment output changes.
AUDITED_FALSE_E0_IDS = {
    "conv-26#q0000",
    "conv-26#q0002",
    "conv-26#q0003",
    "conv-26#q0006",
    "conv-26#q0007",
    "conv-26#q0010",
    "conv-26#q0011",
    "conv-26#q0013",
    "conv-26#q0015",
    "conv-26#q0017",
    "conv-26#q0029",
    "conv-26#q0036",
    "conv-26#q0042",
    "conv-26#q0044",
    "conv-26#q0045",
    "conv-26#q0046",
    "conv-26#q0047",
    "conv-26#q0048",
}


def _load_rows() -> list[dict[str, Any]]:
    if not INPUT.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT}")
    rows: list[dict[str, Any]] = []
    with INPUT.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _question_id(row: dict[str, Any]) -> str:
    return str(row.get("question_id") or row.get("id") or "")


def _gold_evidence(row: dict[str, Any]) -> list[dict[str, Any]]:
    # Gold evidence is stored at the top level in the experiment rows. Be
    # defensive because older result files may have it nested under a mode.
    evidence = row.get("gold_evidence")
    if evidence is None:
        evidence = (row.get("modes", {}).get("real_memory", {}) or {}).get("gold_evidence")
    result: list[dict[str, Any]] = []
    for item in evidence or []:
        if isinstance(item, dict):
            result.append(item)
    return result


def _is_existing_e0(row: dict[str, Any]) -> bool:
    mode = (row.get("modes", {}).get("real_memory", {}) or {})
    gate = mode.get("evidence_sufficiency") or {}
    return gate.get("status") == "insufficient"


def _evaluate_row(row: dict[str, Any], model: str) -> dict[str, Any]:
    question = str(row.get("question") or "")
    reference = str(row.get("answer") or row.get("gold_answer") or "")
    evidence = _gold_evidence(row)

    # answer_semantic_eval reads MODEL at import time. For this controlled A/B
    # experiment, changing only this module-level value is equivalent to running
    # the same gate code with SEMANTIC_JUDGE_MODEL set before process startup.
    semantic_eval.MODEL = model
    try:
        verdict = semantic_eval.evaluate_answer(question, reference, evidence)
        return {
            "status": "sufficient" if verdict.get("evidence_sufficient") is True else (
                "insufficient" if verdict.get("evidence_sufficient") is False else "uncertain"
            ),
            "evidence_sufficient": verdict.get("evidence_sufficient"),
            "confidence": verdict.get("confidence"),
            "reason": verdict.get("reason", ""),
            "adjudication": verdict.get("adjudication"),
            "adjudication_anchor": verdict.get("adjudication_anchor"),
            "correct": verdict.get("correct"),
            "judge_correct": verdict.get("judge_correct"),
            "model": model,
            "error": None,
        }
    except Exception as exc:
        return {
            "status": "error",
            "evidence_sufficient": None,
            "confidence": "low",
            "reason": f"{type(exc).__name__}: {exc}",
            "adjudication": "semantic_judge_error",
            "adjudication_anchor": None,
            "correct": None,
            "judge_correct": None,
            "model": model,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _print_summary(results: list[dict[str, Any]], models: list[str]) -> None:
    print("\n============================================================")
    print("Evidence Gate Model Sensitivity Comparison")
    print("============================================================")
    print(f"Audited cases: {len(results)}")
    print(f"Models: {', '.join(models)}")

    for model in models:
        rows = [r["models"][model] for r in results]
        counts = {"sufficient": 0, "insufficient": 0, "uncertain": 0, "error": 0}
        for item in rows:
            counts[item["status"]] = counts.get(item["status"], 0) + 1
        print(f"\n{model}")
        print(f"  sufficient:   {counts['sufficient']}")
        print(f"  insufficient: {counts['insufficient']}")
        print(f"  uncertain:    {counts['uncertain']}")
        print(f"  error:        {counts['error']}")

    if len(models) >= 2:
        baseline = models[0]
        for challenger in models[1:]:
            changed = []
            for row in results:
                a = row["models"][baseline]["status"]
                b = row["models"][challenger]["status"]
                if a != b:
                    changed.append((row["question_id"], a, b))
            print(f"\n{baseline} -> {challenger} status changes: {len(changed)}")
            for question_id, before, after in changed:
                print(f"  {question_id}: {before} -> {after}")

    print("\n============================================================")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models",
        nargs="+",
        default=["qwen2.5:7b", "gemma3:12b"],
        help="Ollama semantic-judge models to compare (default: qwen2.5:7b gemma3:12b)",
    )
    parser.add_argument(
        "--ids",
        nargs="*",
        default=None,
        help="Optional question IDs; defaults to the 18 manually audited false-E0 cases.",
    )
    args = parser.parse_args()

    rows = _load_rows()
    requested = set(args.ids) if args.ids else AUDITED_FALSE_E0_IDS
    selected = [
        row for row in rows
        if _question_id(row) in requested and _is_existing_e0(row)
    ]
    selected.sort(key=lambda row: _question_id(row))

    missing = sorted(requested - {_question_id(row) for row in selected})
    if missing:
        print("WARNING: requested IDs missing or no longer E0:")
        for item in missing:
            print(f"  {item}")

    if not selected:
        raise RuntimeError("No selected E0 cases were found in comparison.jsonl")

    print(f"Loaded {len(selected)} audited E0 cases from {INPUT}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for index, row in enumerate(selected, start=1):
        question_id = _question_id(row)
        print(f"\n[{index}/{len(selected)}] {question_id}")
        result = {
            "question_id": question_id,
            "question": row.get("question"),
            "reference_answer": row.get("answer") or row.get("gold_answer"),
            "models": {},
        }
        for model in args.models:
            print(f"  [{model}] judging...")
            verdict = _evaluate_row(row, model)
            result["models"][model] = verdict
            print(f"    -> {verdict['status']} ({verdict.get('confidence')})")
            if verdict.get("reason"):
                print(f"       {verdict['reason']}")
        results.append(result)

    output = OUT_DIR / "gate_model_comparison.json"
    output.write_text(json.dumps({
        "input": str(INPUT),
        "models": args.models,
        "case_selection": "manually_audited_false_e0",
        "case_count": len(results),
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    for model in args.models:
        model_rows = [{"question_id": r["question_id"], **r["models"][model]} for r in results]
        (OUT_DIR / f"{model.replace(':', '_')}.jsonl").write_text(
            "\n".join(json.dumps(item, ensure_ascii=False) for item in model_rows) + "\n",
            encoding="utf-8",
        )

    _print_summary(results, args.models)
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
