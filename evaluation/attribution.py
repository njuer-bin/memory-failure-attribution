"""Unified failure attribution — single implementation of the README protocol.

Category contract (canonical names, do not fork):

- F1_FORMATION .. F5_CONTEXT: first lifecycle boundary where required gold
  evidence disappears.
- F6_REASONING_CANDIDATE: all required evidence reaches the final context and
  the answer is still semantically incorrect with non-low judge confidence.
- E0_EVIDENCE_INSUFFICIENT: the benchmark gold evidence does not establish the
  reference answer for the exact question.
- EVAL_SEMANTIC_UNCERTAIN: the evaluator cannot support a stable attribution
  (judge error, missing semantic verdict, or low confidence).
- RC_REASONING_CONTROL_FAILURE: the oracle-context control's own wrong answer;
  not a memory failure.

Non-circularity rule (docs/research/2026-10-09-e0-gate-experiment-integration.md):
the evidence-sufficiency gate is judged against the *benchmark reference
answer*, never against the model's failed prediction.
"""
from __future__ import annotations

from typing import Any

from evaluation.answer_semantic_eval import evaluate_answer

F1_FORMATION = "F1_FORMATION"
F2_STORAGE = "F2_STORAGE"
F3_EVOLUTION = "F3_EVOLUTION"
F4_RETRIEVAL = "F4_RETRIEVAL"
F5_CONTEXT = "F5_CONTEXT"
F6_REASONING_CANDIDATE = "F6_REASONING_CANDIDATE"
E0_EVIDENCE_INSUFFICIENT = "E0_EVIDENCE_INSUFFICIENT"
EVAL_SEMANTIC_UNCERTAIN = "EVAL_SEMANTIC_UNCERTAIN"
RC_REASONING_CONTROL_FAILURE = "RC_REASONING_CONTROL_FAILURE"

STAGE_FAILURES: tuple[tuple[str, str], ...] = (
    ("formation", F1_FORMATION),
    ("storage", F2_STORAGE),
    ("evolution", F3_EVOLUTION),
    ("retrieval", F4_RETRIEVAL),
    ("rerank", F4_RETRIEVAL),
    ("context", F5_CONTEXT),
)


def _stage_measured(stages: dict[str, Any], stage: str) -> bool:
    entry = stages.get(stage)
    if not isinstance(entry, dict):
        # Legacy traces predate evolution measurement and carry no entry.
        return stage != "evolution"
    details = entry.get("details") or {}
    return details.get("measured", True) is not False


def first_missing_stage(stages: dict[str, Any], gold_ids: set[str]) -> str | None:
    for stage, label in STAGE_FAILURES:
        if not _stage_measured(stages, stage):
            continue
        found = {str(x) for x in (stages.get(stage) or {}).get("found", [])}
        if not gold_ids.issubset(found):
            return label
    return None


def evidence_sufficiency_gate(
    question: str, benchmark_answer: str, gold: list[dict[str, Any]]
) -> dict[str, Any]:
    """Judge whether the benchmark gold evidence establishes the reference answer."""
    if not gold:
        return {
            "status": "insufficient", "evidence_sufficient": False,
            "confidence": "high", "reason": "No benchmark gold evidence is available.",
            "adjudication": "no_gold_evidence",
        }
    try:
        verdict = evaluate_answer(
            question, str(benchmark_answer or ""), gold, candidate_is_reference=True
        )
    except Exception as exc:
        return {
            "status": "error", "evidence_sufficient": None, "confidence": "low",
            "reason": f"Evidence sufficiency judge failed: {type(exc).__name__}: {exc}",
            "adjudication": "semantic_judge_error",
        }
    sufficient = verdict.get("evidence_sufficient")
    confidence = str(verdict.get("confidence") or "medium").lower()
    if sufficient is False:
        status = "insufficient"
    elif sufficient is True and confidence != "low":
        status = "sufficient"
    else:
        status = "uncertain"
    return {
        "status": status,
        "evidence_sufficient": sufficient,
        "confidence": confidence,
        "reason": verdict.get("reason", ""),
        "adjudication": verdict.get("adjudication", "judge"),
        "adjudication_anchor": verdict.get("adjudication_anchor"),
        "model": verdict.get("model"),
    }


def attribute_failure(
    answer: dict[str, Any],
    gate: dict[str, Any],
    stages: dict[str, Any],
    gold_evidence: list[dict[str, Any]],
    mode: str | None = None,
) -> str | None:
    """Attribute one answer failure under the frozen protocol.

    `gate` must be a precomputed evidence-sufficiency gate (from
    `evidence_sufficiency_gate`); a missing or empty gate is an error so that
    no caller can silently bypass E0.
    """
    if not isinstance(gate, dict) or not gate.get("status"):
        raise ValueError(
            "attribute_failure requires a precomputed evidence_sufficiency gate; "
            "compute it with evidence_sufficiency_gate(question, benchmark_answer, gold)"
        )

    semantic_correct = answer.get("semantic_correct")
    if semantic_correct is True:
        return None
    if semantic_correct is None:
        # Lexical-only correctness is accepted when no semantic verdict exists
        # (the runner skips the judge for lexically correct answers). A
        # contradictory semantic verdict must never be overridden by lexical
        # token overlap.
        if answer.get("correct") is True:
            return None
        return EVAL_SEMANTIC_UNCERTAIN

    status = gate.get("status")
    if status == "insufficient":
        return E0_EVIDENCE_INSUFFICIENT
    if status != "sufficient":
        return EVAL_SEMANTIC_UNCERTAIN
    confidence = str(answer.get("semantic_confidence") or "").lower()
    if confidence not in {"medium", "high"}:
        return EVAL_SEMANTIC_UNCERTAIN

    if mode == "oracle_context":
        return RC_REASONING_CONTROL_FAILURE

    gold_ids = {
        str(x.get("evidence_id")) for x in (gold_evidence or []) if x.get("evidence_id")
    }
    if not gold_ids:
        return E0_EVIDENCE_INSUFFICIENT

    missing = first_missing_stage(stages, gold_ids)
    if missing:
        return missing
    return F6_REASONING_CANDIDATE
