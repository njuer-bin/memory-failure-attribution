"""First-loss attribution across the memory lifecycle."""
from typing import Any, Dict, Optional

from evaluation.answer_semantic_eval import evaluate_answer


STAGE_TO_FAILURE = {
    "formation": "F1_FORMATION",
    "storage": "F2_STORAGE",
    "evolution": "F3_EVOLUTION",
    "retrieval": "F4_RETRIEVAL",
    "rerank": "F4_RETRIEVAL",
    "context": "F5_CONTEXT",
}


def _gold_evidence(trace: Dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "evidence_id": str(item.get("evidence_id")),
            "content": str(item.get("text") or item.get("content") or ""),
            "source_id": item.get("source_id") or item.get("source"),
            "turn_id": item.get("turn_id") or item.get("turn"),
            "timestamp": item.get("timestamp"),
        }
        for item in trace.get("gold_evidence", [])
        if item.get("evidence_id")
    ]


def _ensure_evidence_sufficiency(trace: Dict[str, Any]) -> dict[str, Any]:
    """Check Gold Evidence against the benchmark reference, not the prediction.

    Using the generated answer to decide whether the evidence is sufficient
    would make E0 depend on the system failure being diagnosed. If the
    reference answer is unavailable, attribution is conservatively deferred
    to the evaluation-uncertain category.
    """
    existing = trace.get("evidence_sufficiency")
    if isinstance(existing, dict):
        return existing

    evidence = _gold_evidence(trace)
    answer = trace.get("answer") or {}
    reference = trace.get("reference_answer") or answer.get("reference_answer") or answer.get("reference")
    question = str(trace.get("question") or "")
    if not evidence:
        return {
            "status": "insufficient",
            "evidence_sufficient": False,
            "confidence": "high",
            "reason": "No benchmark gold evidence is available.",
            "adjudication": "no_gold_evidence",
        }
    if not isinstance(reference, str) or not reference.strip():
        return {
            "status": "uncertain",
            "evidence_sufficient": None,
            "confidence": "low",
            "reason": "Benchmark reference answer is unavailable; evidence sufficiency cannot be assessed independently of the prediction.",
            "adjudication": "missing_reference_answer",
        }

    try:
        verdict = evaluate_answer(question, reference, evidence)
    except Exception as exc:
        return {
            "status": "error",
            "evidence_sufficient": None,
            "confidence": "low",
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


def attribute_failure(trace: Dict[str, Any]) -> Optional[str]:
    """Attribute a failure only after evidence sufficiency has been validated.

    Attribution order:
    1. E0 when the supplied gold evidence cannot answer the question.
    2. EVAL when evidence sufficiency is uncertain or the judge fails.
    3. F1-F5 at the earliest lifecycle boundary where gold evidence disappears.
    4. F6 only when all gold evidence reaches final context and the answer is
       still wrong according to the benchmark answer scorer.
    """
    answer = trace.get("answer", {}) or {}
    if answer.get("correct") is not False:
        return None

    sufficiency = _ensure_evidence_sufficiency(trace)
    trace["evidence_sufficiency"] = sufficiency

    if sufficiency.get("status") == "insufficient":
        return "E0_EVIDENCE_INSUFFICIENCY"
    if sufficiency.get("status") != "sufficient":
        return "EVAL_EVIDENCE_SUFFICIENCY"

    gold = {str(x["evidence_id"]) for x in _gold_evidence(trace)}
    if not gold:
        return "E0_EVIDENCE_INSUFFICIENCY"

    for stage in ("formation", "storage", "evolution", "retrieval", "rerank", "context"):
        found = set(map(str, trace.get(stage, {}).get("found", [])))
        if not gold.issubset(found):
            return STAGE_TO_FAILURE[stage]

    return "F6_REASONING"
