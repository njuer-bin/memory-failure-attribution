"""Helpers for matching benchmark evidence to memory-engine artifacts."""
from __future__ import annotations

import re
from typing import Any, Iterable


def normalize_text(text: Any) -> str:
    value = str(text or "").strip().lower()
    return re.sub(r"\s+", "", value)


def _text(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("content") or item.get("text") or "")
    return str(item or "")


def match_evidence(gold: Iterable[dict[str, Any]], observed: Iterable[Any]) -> dict[str, Any]:
    """Match gold evidence to observed memory objects by normalized text.

    Benchmark source IDs and engine-generated memory IDs are intentionally kept
    separate. This makes the attribution layer benchmark-agnostic and avoids
    pretending that a raw benchmark turn ID is an internal memory ID.
    """
    observed_list = list(observed)
    buckets: dict[str, list[Any]] = {}
    for item in observed_list:
        key = normalize_text(_text(item))
        if key:
            buckets.setdefault(key, []).append(item)

    found, missing = [], []
    matches = {}
    for idx, evidence in enumerate(gold):
        evidence_id = str(evidence.get("evidence_id") or f"gold_{idx}")
        key = normalize_text(evidence.get("text"))
        hit = bool(key and buckets.get(key))
        if hit:
            found.append(evidence_id)
            matches[evidence_id] = buckets[key][0]
        else:
            missing.append(evidence_id)

    return {
        "found": sorted(found),
        "missing": sorted(missing),
        "matches": matches,
        "observed_count": len(observed_list),
    }


def stage_from_observed(
    gold: Iterable[dict[str, Any]], observed: Iterable[Any]
) -> dict[str, Any]:
    result = match_evidence(gold, observed)
    return {k: v for k, v in result.items() if k != "matches"}
