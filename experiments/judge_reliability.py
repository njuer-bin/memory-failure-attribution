"""Independently re-judge stored answers to measure judge reliability (audit I2).

The semantic judge is the instrument that decides F6, so its reliability must be
measured rather than assumed. This script re-runs the judge over the answers already
stored in a run's comparison.jsonl and reports agreement and Cohen's kappa against the
stored verdicts, plus the adjudication path and question each flip belongs to.

Two verdicts are compared separately, because they answer different questions:

- ``correct_verdict``: the protocol verdict (``semantic_correct``), i.e. what
  attribution actually consumed, including deterministic repairs.
- ``raw_judge``: the judge's own boolean (``judge_correct``), before repairs.

The evidence-sufficiency gate is re-judged with ``candidate_is_reference=True``, the
same prompt role the runner used. Comparing it against a model-answer-prompt verdict
would be a prompt-role confound, not a reliability estimate.

Gold evidence is passed to the judge exactly as the runner passed it (the stored
``gold_evidence`` list), so a re-judgment differs from the stored verdict only through
judge nondeterminism.

It never re-runs memory ingestion or answer generation. Set SEMANTIC_JUDGE_MODEL (or
--model, if the judge module honours it) to a different model than the one that produced
the stored verdicts to obtain a cross-model reliability estimate; running with the same
model and temperature 0 measures self-consistency only.

Usage:
    python -m experiments.judge_reliability --input results/oracle_experiments_n50_repaired/comparison.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.answer_semantic_eval import evaluate_answer
from evaluation.paired_stats import agreement, cohens_kappa

MODES = ("real_memory", "oracle_memory", "oracle_context")


def reliability_summary(
    stored: list[Any], rerun: list[Any]
) -> dict[str, Any]:
    """Agreement between stored and re-judged verdicts, skipping missing values."""
    return {
        "n": sum(1 for a, b in zip(stored, rerun) if a is not None and b is not None),
        "agreement": agreement(stored, rerun),
        "kappa": cohens_kappa(stored, rerun),
        "n_stored_true": sum(1 for a in stored if a is True),
        "n_rerun_true": sum(1 for b in rerun if b is True),
    }


def _stored_gate(row: dict[str, Any]) -> dict[str, Any]:
    """The gate is question-level, so any mode's copy is the same verdict."""
    gates = [
        (row.get("modes", {}).get(mode, {}) or {}).get("evidence_sufficiency")
        for mode in MODES
    ]
    for gate in gates:
        if isinstance(gate, dict) and gate.get("status"):
            return gate
    return {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/oracle_experiments/comparison.jsonl")
    parser.add_argument("--output", default="results/oracle_experiments/judge_reliability.json")
    parser.add_argument("--limit", type=int, default=0, help="0 = all rows")
    args = parser.parse_args()

    rows = [json.loads(line) for line in Path(args.input).read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.limit:
        rows = rows[: args.limit]

    stored_correct: list[Any] = []
    rerun_correct: list[Any] = []
    stored_judge: list[Any] = []
    rerun_judge: list[Any] = []
    stored_sufficient: list[Any] = []
    rerun_sufficient: list[Any] = []
    flips: list[dict[str, Any]] = []
    gate_flips: list[dict[str, Any]] = []
    errors = 0
    gate_errors = 0
    lexically_skipped = 0
    unjudged = 0
    judge_models: set[str] = set()

    def _record_skip(stored: Any, stored_j: Any) -> None:
        stored_correct.append(stored)
        rerun_correct.append(None)
        stored_judge.append(stored_j)
        rerun_judge.append(None)

    for i, row in enumerate(rows, 1):
        question = str(row.get("question") or "")
        evidence = list(row.get("gold_evidence") or [])
        print(f"[{i}/{len(rows)}] {row.get('question_id')}", flush=True)
        for mode in MODES:
            mode_entry = row.get("modes", {}).get(mode) or {}
            if not mode_entry:
                _record_skip(None, None)
                continue
            answer = mode_entry.get("answer") or {}
            candidate = str(answer.get("answer") or "")
            stored = answer.get("semantic_correct")
            stored_j = answer.get("semantic_judge_correct")
            if stored is None and stored_j is None:
                # Distinguish "the runner skipped the judge because the answer was
                # already lexically correct" from "there is no verdict at all"
                # (empty/absent answer, judge error). Neither is a judge datapoint.
                if answer.get("correct") is True:
                    lexically_skipped += 1
                else:
                    unjudged += 1
                _record_skip(stored, stored_j)
                continue
            if not candidate.strip() or answer.get("model_error") or answer.get("semantic_error"):
                unjudged += 1
                _record_skip(stored, stored_j)
                continue
            try:
                verdict = evaluate_answer(
                    question, candidate, evidence,
                    reference_answer=str(row.get("gold_answer") or ""),
                )
            except Exception:  # judge unavailable -> not an agreement datapoint
                errors += 1
                _record_skip(stored, stored_j)
                continue
            if verdict.get("model"):
                judge_models.add(str(verdict["model"]))
            stored_correct.append(stored)
            rerun_correct.append(verdict["correct"])
            stored_judge.append(stored_j)
            rerun_judge.append(verdict.get("judge_correct"))
            if stored is not None and stored != verdict["correct"]:
                flips.append({
                    "question_id": row.get("question_id"),
                    "mode": mode,
                    "stored_correct": stored,
                    "rerun_correct": verdict["correct"],
                    "stored_reason": answer.get("semantic_reason"),
                    "rerun_reason": verdict["reason"],
                    "adjudication": verdict["adjudication"],
                })

        gate = _stored_gate(row)
        stored_g = gate.get("evidence_sufficient")
        if not evidence or stored_g is None:
            stored_sufficient.append(stored_g)
            rerun_sufficient.append(None)
            continue
        try:
            gate_verdict = evaluate_answer(
                question, str(row.get("gold_answer") or ""), evidence,
                candidate_is_reference=True,
            )
        except Exception:
            gate_errors += 1
            stored_sufficient.append(stored_g)
            rerun_sufficient.append(None)
            continue
        if gate_verdict.get("model"):
            judge_models.add(str(gate_verdict["model"]))
        stored_sufficient.append(stored_g)
        rerun_sufficient.append(gate_verdict.get("evidence_sufficient"))
        if stored_g != gate_verdict.get("evidence_sufficient"):
            gate_flips.append({
                "question_id": row.get("question_id"),
                "stored_status": gate.get("status"),
                "stored_evidence_sufficient": stored_g,
                "rerun_evidence_sufficient": gate_verdict.get("evidence_sufficient"),
                "stored_reason": gate.get("reason"),
                "rerun_reason": gate_verdict.get("reason"),
            })

    summary = {
        "input": args.input,
        "records": len(rows),
        "judge_errors": errors,
        "gate_judge_errors": gate_errors,
        "lexically_skipped_judgments": lexically_skipped,
        "unjudged_answers": unjudged,
        "judge_models": sorted(judge_models),
        "prompt_roles": {
            "answer_judge": "model_generated_answer",
            "gate_judge": "benchmark_reference",
        },
        "correct_verdict": reliability_summary(stored_correct, rerun_correct),
        "raw_judge": reliability_summary(stored_judge, rerun_judge),
        "evidence_sufficiency": reliability_summary(stored_sufficient, rerun_sufficient),
        "n_flips": len(flips),
        "n_gate_flips": len(gate_flips),
        "flips": flips,
        "gate_flips": gate_flips,
    }
    Path(args.output).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(
        {k: v for k, v in summary.items() if k not in ("flips", "gate_flips")},
        ensure_ascii=False, indent=2,
    ), flush=True)


if __name__ == "__main__":
    main()
