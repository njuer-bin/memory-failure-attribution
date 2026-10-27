"""Stage-targeted repairs for the P2 intervention experiment.

The attribution protocol reports a *first-loss* stage. This module asks a
different question: if we repair the stage the diagnosis points at, does the
answer improve? Three routing arms are supported:

- ``first_loss``: route by the stored attribution label (F1->formation,
  F4->retrieval, F5->context, F6->reasoning).
- ``path``: route by whether the evidence actually reaches the final context.
  If it does, the failure is reasoning-side; otherwise repair the deepest
  stage where it dropped out. This differs from ``first_loss`` whenever a
  formation miss is recovered by verbatim storage downstream.
- ``agnostic``: apply every repair to every attributable failure, the
  stage-agnostic baseline.
- ``placebo``: regenerate the baseline answer without any repair. This bounds
  the provider/judge nondeterminism floor that every arm contrast sits on.

Repairs are deterministic except the reasoning repair, which is one extra
temperature-0 answer-model call (draft verification).
"""
from __future__ import annotations

from typing import Any

from memory_engine.analyzer import Event
from memory_engine.models import fingerprint, new_id
from tracing.lifecycle import text_similarity

MEASURED_STAGES = ("formation", "storage", "retrieval", "rerank", "context")

FIRST_LOSS_TARGET = {
    "F1_FORMATION": "formation",
    "F2_STORAGE": "storage",
    "F4_RETRIEVAL": "retrieval",
    "F5_CONTEXT": "context",
    "F6_REASONING_CANDIDATE": "reasoning",
}

# Repair levers. "retrieval" widens the candidate pool; "context" widens the
# final context; "formation" writes verbatim evidence into semantic memory;
# "reasoning" verifies the draft answer against the same evidence.
REPAIR_STAGES = {"formation", "retrieval", "context", "reasoning", "all"}


def gold_ids(row: dict[str, Any]) -> set[str]:
    return {
        str(item.get("evidence_id"))
        for item in (row.get("gold_evidence") or [])
        if item.get("evidence_id")
    }


def _found(mode_data: dict[str, Any], stage: str) -> set[str]:
    return {str(x) for x in (mode_data.get(stage) or {}).get("found", [])}


def missing_stages(mode_data: dict[str, Any], ids: set[str]) -> list[str]:
    return [stage for stage in MEASURED_STAGES if not ids.issubset(_found(mode_data, stage))]


def path_target(mode_data: dict[str, Any], ids: set[str]) -> str | None:
    """Route by the evidence path to the final context, not by first loss.

    ``None`` means the row is not a repair target (no gold ids or a correct
    answer). If context contains every required item the memory path is
    intact and the only remaining repair is answer-time verification.
    """
    if not ids:
        return None
    missing = set(missing_stages(mode_data, ids))
    if "context" not in missing:
        # The evidence reaches the answer context, so no memory-side repair can
        # help even if an earlier stage (e.g. semantic formation) missed it.
        return "reasoning"
    if "rerank" in missing:
        return "retrieval"
    return "context"


def first_loss_target(mode_data: dict[str, Any]) -> str | None:
    return FIRST_LOSS_TARGET.get(str(mode_data.get("answer_failure_type") or ""))


def arm_target(row: dict[str, Any], arm: str, mode: str = "real_memory") -> str | None:
    """Return the repair lever an arm applies to this row, or ``None``."""
    mode_data = (row.get("modes") or {}).get(mode) or {}
    answer = mode_data.get("answer") or {}
    if answer.get("semantic_correct") is not False:
        return None
    if arm == "placebo":
        # Same population as first_loss, but the "repair" is a no-op.
        return "placebo" if first_loss_target(mode_data) else None
    if arm == "first_loss":
        return first_loss_target(mode_data)
    if arm == "path":
        # E0/EVAL rows are not attributable failures and get no repair.
        if not first_loss_target(mode_data):
            return None
        return path_target(mode_data, gold_ids(row))
    if arm == "agnostic":
        return "all" if first_loss_target(mode_data) else None
    raise ValueError(f"unknown intervention arm: {arm!r}")


def _semantic_rows(store: Any, user_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for getter, include_history in (
        (store.active_facts, True),
        (store.events, None),
        (store.relations, None),
        (store.rules, None),
        (store.profiles, None),
    ):
        if include_history:
            rows.extend(getter(user_id, include_history=True))
        else:
            rows.extend(getter(user_id))
    return rows


def write_through_verbatim(engine: Any, user_id: str, threshold: float = 0.55) -> int:
    """Formation repair: give every unrepresented turn a provenance-carrying
    verbatim semantic memory.

    A turn counts as represented when a semantic artifact from that same turn
    matches its text at the tracer's semantic threshold. The repair therefore
    targets exactly the F1a extractor-miss mechanism measured by the
    diagnostics; it never consults gold evidence.
    """
    store = engine.store
    represented: dict[str, list[str]] = {}
    for item in _semantic_rows(store, user_id):
        turn = item.get("source_turn_id")
        if turn:
            represented.setdefault(str(turn), []).append(str(item.get("content") or ""))

    written = 0
    for raw in store.all_raw(user_id):
        turn = raw.get("source_turn_id")
        content = str(raw.get("content") or "").strip()
        if not turn or not content:
            continue
        if any(text_similarity(content, seen) >= threshold
               for seen in represented.get(str(turn), [])):
            continue
        event = Event(
            id=new_id("verbatim"),
            user_id=user_id,
            event="verbatim",
            content=content,
            timestamp=int(raw["timestamp"]),
            fingerprint=fingerprint(user_id, "verbatim", raw["id"]),
            source_raw_id=raw["id"],
            source_session_id=raw.get("session_id"),
            source_turn_id=str(turn),
        )
        store.insert_event(event)
        vector = engine.embedder.embed(content)
        store.embed(event.id, user_id, vector)
        engine.vector_index.add(user_id, event.id, vector)
        written += 1
    return written
