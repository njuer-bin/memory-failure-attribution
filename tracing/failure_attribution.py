"""First-loss attribution across the memory lifecycle."""
from typing import Any, Dict, Optional

STAGE_TO_FAILURE = {"formation": "F1_FORMATION", "storage": "F2_STORAGE",
                    "evolution": "F3_EVOLUTION", "retrieval": "F4_RETRIEVAL",
                    "rerank": "F4_RETRIEVAL", "context": "F5_CONTEXT"}

def attribute_failure(trace: Dict[str, Any]) -> Optional[str]:
    gold = {str(x["evidence_id"]) for x in trace.get("gold_evidence", []) if "evidence_id" in x}
    if not gold:
        return None
    for stage in ("formation", "storage", "evolution", "retrieval", "rerank", "context"):
        found = set(map(str, trace.get(stage, {}).get("found", [])))
        if not gold.issubset(found):
            return STAGE_TO_FAILURE[stage]
    return "F6_REASONING" if trace.get("answer", {}).get("correct") is False else None
