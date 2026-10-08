"""Bridge MemoryEngine artifacts into lifecycle traces.

The engine does not retain benchmark evidence IDs, so this adapter uses
content/source matching and records the engine IDs in stage details. It is
deliberately non-invasive: no benchmark-specific fields are written into the
memory engine itself.
"""
from __future__ import annotations

from typing import Any, Iterable

from tracing.lifecycle import match_evidence


def _artifact(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return dict(row)
    result = {}
    for key in ("id", "content", "session_id", "source", "timestamp", "memory_type", "status"):
        if hasattr(row, key):
            result[key] = getattr(row, key)
    return result


def artifacts_from_store(engine: Any, user_id: str) -> dict[str, list[dict[str, Any]]]:
    store = engine.store
    raw = store.all_raw(user_id)
    facts = store.active_facts(user_id, include_history=True)
    relations = store.relations(user_id) if hasattr(store, "relations") else []
    events = store.events(user_id)
    rules = store.rules(user_id) if hasattr(store, "rules") else []
    profiles = store.profiles(user_id) if hasattr(store, "profiles") else []

    def typed(rows, kind):
        output = []
        for row in rows:
            item = _artifact(row)
            item["memory_type"] = kind
            output.append(item)
        return output

    return {
        "raw": typed(raw, "raw"),
        "facts": typed(facts, "fact"),
        "relations": typed(relations, "relation"),
        "events": typed(events, "event"),
        "rules": typed(rules, "rule"),
        "profiles": typed(profiles, "profile"),
    }


def stage_match(gold: Iterable[dict[str, Any]], artifacts: Iterable[Any]) -> dict[str, Any]:
    result = match_evidence(gold, [_artifact(x) for x in artifacts])
    result["matches"] = {
        gid: _artifact(value) for gid, value in result.get("matches", {}).items()
    }
    return result


def retrieval_artifacts(results: Iterable[Any]) -> list[dict[str, Any]]:
    return [_artifact(x) for x in results]
