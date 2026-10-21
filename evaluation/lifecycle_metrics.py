"""Metrics for stage-wise memory failure attribution."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


# Per-trace ``details.measured`` decides whether a stage participates. Runs
# before the controlled evolution probe set ``measured: false`` on evolution,
# preserving their first-loss results; traces from the probe set it true, so
# F3 can fire there.
MEASURED_STAGES = ("formation", "storage", "retrieval", "rerank", "context")
UNMEASURED_STAGES = ("evolution",)
STAGES = ("formation", "storage", "evolution", "retrieval", "rerank", "context")


def _set(value: Any) -> set[str]:
    return {str(x) for x in (value or [])}


def _is_measured(trace: dict[str, Any], stage: str) -> bool:
    entry = trace.get(stage)
    if not isinstance(entry, dict):
        # Legacy traces predate evolution measurement and carry no entry.
        return stage != "evolution"
    details = entry.get("details") or {}
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
    for stage in STAGES:
        if not _is_measured(trace, stage):
            continue
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
    unmeasured = [
        stage for stage in STAGES
        if not any(_is_measured(t, stage) for t in rows)
    ] if rows else list(UNMEASURED_STAGES)
    return {
        "count": len(rows),
        "stage_recall": recalls,
        "unmeasured_stages": unmeasured,
        "first_loss_distribution": dict(losses),
    }
