"""Metrics for stage-wise memory failure attribution."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


# Audit C4: no evolution operation is applied by the tracing layer, so an
# evolution recall computed by copying formation is a structural artifact.
# It is kept in the output shape as ``None`` and excluded from first-loss.
MEASURED_STAGES = ("formation", "storage", "retrieval", "rerank", "context")
UNMEASURED_STAGES = ("evolution",)
STAGES = MEASURED_STAGES + UNMEASURED_STAGES


def _set(value: Any) -> set[str]:
    return {str(x) for x in (value or [])}


def _is_measured(trace: dict[str, Any], stage: str) -> bool:
    if stage in UNMEASURED_STAGES:
        return False
    details = (trace.get(stage) or {}).get("details") or {}
    return details.get("measured", True) is not False


def stage_recall(trace: dict[str, Any], stage: str) -> float | None:
    if not _is_measured(trace, stage):
        return None
    gold = {str(x.get("evidence_id")) for x in trace.get("gold_evidence", []) if x.get("evidence_id")}
    found = _set((trace.get(stage) or {}).get("found"))
    return len(gold & found) / len(gold) if gold else 1.0


def first_loss_stage(trace: dict[str, Any]) -> str | None:
    gold = {str(x.get("evidence_id")) for x in trace.get("gold_evidence", []) if x.get("evidence_id")}
    if not gold:
        return None
    for stage in MEASURED_STAGES:
        if not gold.issubset(_set((trace.get(stage) or {}).get("found"))):
            return stage
    return None


def summarize_traces(traces: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(traces)
    recalls = {}
    for stage in STAGES:
        values = [stage_recall(t, stage) for t in rows]
        measured = [v for v in values if v is not None]
        recalls[stage] = sum(measured) / len(measured) if measured else None
    losses = Counter(first_loss_stage(t) or "none" for t in rows)
    return {
        "count": len(rows),
        "stage_recall": recalls,
        "unmeasured_stages": list(UNMEASURED_STAGES),
        "first_loss_distribution": dict(losses),
    }
