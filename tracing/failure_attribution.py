"""First-loss attribution across the memory lifecycle."""
from typing import Any, Dict, Optional


STAGE_TO_FAILURE = {
    "formation": "F1_FORMATION",
    "storage": "F2_STORAGE",
    "evolution": "F3_EVOLUTION",
    "retrieval": "F4_RETRIEVAL",
    "rerank": "F4_RETRIEVAL",
    "context": "F5_CONTEXT",
}


def attribute_failure(trace: Dict[str, Any]) -> Optional[str]:
    """Attribute a failure only after the benchmark evidence is answerable.

    The evidence-sufficiency gate is intentionally checked before lifecycle
    boundaries. If the benchmark's own gold evidence cannot answer the question,
    the case is E0 rather than a memory failure. If the gate is unavailable or
    uncertain, attribution is withheld as EVAL instead of manufacturing F6.
    """
    answer = trace.get("answer", {}) or {}
    if answer.get("correct") is not False:
        return None

    sufficiency = trace.get("evidence_sufficiency")
    if sufficiency:
        sufficient = sufficiency.get("evidence_sufficient")
        status = str(sufficiency.get("status") or "").lower()
        if sufficient is False or status == "insufficient":
            return "E0_EVIDENCE_INSUFFICIENCY"
        if sufficient is not True or status in {"uncertain", "error"}:
            return "EVAL_EVIDENCE_SUFFICIENCY"

    gold = {
        str(x["evidence_id"])
        for x in trace.get("gold_evidence", [])
        if "evidence_id" in x
    }
    if not gold:
        return "E0_EVIDENCE_INSUFFICIENCY"

    for stage in ("formation", "storage", "evolution", "retrieval", "rerank", "context"):
        found = set(map(str, trace.get(stage, {}).get("found", [])))
        if not gold.issubset(found):
            return STAGE_TO_FAILURE[stage]

    return "F6_REASONING"
