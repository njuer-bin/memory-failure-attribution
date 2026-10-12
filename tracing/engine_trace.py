"""Bridge MemoryEngine artifacts into lifecycle traces."""
from __future__ import annotations

from typing import Any, Iterable

from tracing.lifecycle import match_evidence


def _artifact(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return dict(row)
    result = {}
    for key in (
        "id", "content", "session_id", "source_id", "turn_id",
        "source_raw_id", "source_session_id", "source_turn_id", "timestamp", "memory_type", "status",
    ):
        if hasattr(row, key):
            result[key] = getattr(row, key)
    return result


def _artifact_turn_id(item: dict[str, Any]) -> str:
    return str(item.get("source_turn_id") or item.get("turn_id") or "")


def _gold_turn_id(item: dict[str, Any]) -> str:
    return str(item.get("turn_id") or item.get("turn") or "")


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
            # Raw records carry the benchmark session id. Semantic memories
            # carry persisted source session/turn provenance when available.
            if kind == "raw":
                item["source_id"] = item.get("session_id")
            else:
                item["source_id"] = item.get("source_session_id") or item.get("session_id")
                item["source_turn_id"] = item.get("source_turn_id")
                item["source_raw_id"] = item.get("source_raw_id")
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
    """Match lifecycle evidence by exact turn provenance.

    Semantic matching remains available as diagnostics, but it is never allowed
    to promote an artifact from another turn to ``found``. This prevents a
    representation from a semantically similar conversation turn from masking
    a formation/storage/retrieval loss and shifting attribution to a later stage.
    """
    gold_items = [dict(item) for item in gold]
    artifact_items = [_artifact(x) for x in artifacts]
    semantic = match_evidence(gold_items, artifact_items)

    found: list[str] = []
    missing: list[str] = []
    matches: dict[str, dict[str, Any]] = {}
    match_types: dict[str, str] = {}
    match_scores: dict[str, float] = {}
    wrong_source: dict[str, dict[str, Any]] = {}

    for evidence in gold_items:
        gid = str(evidence.get("evidence_id") or evidence.get("id") or "")
        if not gid:
            continue
        expected_turn = _gold_turn_id(evidence)
        exact = [item for item in artifact_items if expected_turn and _artifact_turn_id(item) == expected_turn]
        if exact:
            found.append(gid)
            matches[gid] = exact[0]
            match_types[gid] = "provenance"
            match_scores[gid] = 1.0
            continue

        missing.append(gid)
        semantic_match = semantic.get("matches", {}).get(gid)
        if semantic_match is not None:
            wrong_source[gid] = _artifact(semantic_match)

    semantic_match_types = semantic.get("match_types", {})
    semantic_match_scores = semantic.get("match_scores", {})

    return {
        "found": found,
        "missing": missing,
        "dropped": semantic.get("dropped", []),
        "observed_count": len(artifact_items),
        "match_types": match_types,
        "match_scores": match_scores,
        "matches": matches,
        "semantic_matches": wrong_source,
        "semantic_match_types": {
            gid: semantic_match_types[gid]
            for gid in wrong_source
            if gid in semantic_match_types
        },
        "semantic_match_scores": {
            gid: semantic_match_scores[gid]
            for gid in wrong_source
            if gid in semantic_match_scores
        },
    }


def retrieval_artifacts(results: Iterable[Any]) -> list[dict[str, Any]]:
    return [_artifact(x) for x in results]
