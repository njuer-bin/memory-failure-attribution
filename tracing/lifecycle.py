"""Evidence matching across memory-lifecycle stages."""
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


def _tokens(text: str) -> set[str]:
    # Character bigrams make the matcher useful for Chinese without requiring
    # a heavyweight tokenizer; word tokens are retained for Latin text.
    value = normalize_text(text)
    chars = {value[i:i + 2] for i in range(max(0, len(value) - 1))}
    words = set(re.findall(r"[a-z0-9_]+", value))
    return chars | words


def _semantic_similarity(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, min(len(ta), len(tb)))


def text_similarity(a: str, b: str) -> float:
    """Public alias used by interventions that need the tracer's match metric."""
    return _semantic_similarity(a, b)


def _provenance_relation(evidence: dict[str, Any], artifact: Any) -> str:
    """Classify provenance as ``match``, ``conflict``, or ``unknown``.

    Audit C3: provenance must be checked for *conflict* rather than treated as
    proof of availability. A record from the gold turn with unrelated content
    is provenance-only; a record with the gold content but a conflicting turn
    is a different fact and must not satisfy the gold evidence. Artifacts that
    carry no provenance (common for extracted events) can only be matched by
    content, so they are ``unknown`` rather than rejected.
    """
    if not isinstance(artifact, dict):
        return "conflict"

    evidence_turn = evidence.get("turn_id") or evidence.get("source_turn_id")
    artifact_turn = artifact.get("turn_id") or artifact.get("source_turn_id")
    if evidence_turn and artifact_turn:
        return "match" if str(evidence_turn) == str(artifact_turn) else "conflict"

    evidence_raw = evidence.get("source_raw_id") or evidence.get("raw_id")
    artifact_raw = artifact.get("source_raw_id") or artifact.get("raw_id")
    if evidence_raw and artifact_raw:
        return "match" if str(evidence_raw) == str(artifact_raw) else "conflict"

    evidence_source = evidence.get("source_id") or evidence.get("source")
    artifact_source = (
        artifact.get("source_id")
        or artifact.get("source_session_id")
        or artifact.get("session_id")
    )
    if evidence_source and artifact_source:
        return "match" if str(evidence_source) == str(artifact_source) else "conflict"

    return "unknown"


def match_evidence(
    gold: Iterable[dict[str, Any]],
    observed: Iterable[Any],
    *,
    semantic_threshold: float = 0.55,
) -> dict[str, Any]:
    """Match gold evidence using content plus provenance constraints.

    Content exactness is the primary availability signal. Provenance is used
    as a constraint: an artifact whose turn/session conflicts with the gold
    evidence cannot satisfy it, which prevents duplicated text in another turn
    from being attributed to the gold turn. Provenance agreement without
    content agreement is reported as ``provenance_only`` and does not count as
    found (audit C3). Artifacts without provenance are matched by content and
    flagged in ``unverified_provenance`` so their share is measurable.
    """
    observed_list = list(observed)
    found: list[str] = []
    missing: list[str] = []
    provenance_only: list[str] = []
    unverified_provenance: list[str] = []
    matches: dict[str, Any] = {}
    match_types: dict[str, str] = {}
    match_scores: dict[str, float] = {}

    for idx, evidence in enumerate(gold):
        evidence_id = str(evidence.get("evidence_id") or f"gold_{idx}")
        gold_text = str(evidence.get("text") or "")
        norm_gold = normalize_text(gold_text)

        provenance_matches: list[Any] = []
        eligible: list[Any] = []
        for artifact in observed_list:
            relation = _provenance_relation(evidence, artifact)
            if relation == "match":
                provenance_matches.append(artifact)
                eligible.append(artifact)
            elif relation == "unknown":
                eligible.append(artifact)

        best = None
        best_type = None
        best_score = 0.0

        # 1. Exact text among provenance-compatible artifacts.
        if norm_gold:
            for artifact in eligible:
                if normalize_text(_text(artifact)) == norm_gold:
                    best, best_type, best_score = artifact, "exact", 1.0
                    break

        # 2. Semantic representation among provenance-compatible artifacts.
        if best is None and gold_text:
            for artifact in eligible:
                score = _semantic_similarity(gold_text, _text(artifact))
                if score > best_score:
                    best, best_type, best_score = artifact, "semantic", score
            if best_score < semantic_threshold:
                best, best_type, best_score = None, None, 0.0

        if best is not None:
            found.append(evidence_id)
            matches[evidence_id] = best
            match_types[evidence_id] = best_type
            match_scores[evidence_id] = round(best_score, 4)
            has_provenance = (
                evidence.get("turn_id")
                or evidence.get("source_turn_id")
                or evidence.get("source_raw_id")
                or evidence.get("raw_id")
                or evidence.get("source_id")
                or evidence.get("source")
            )
            if has_provenance and not any(best is c for c in provenance_matches):
                unverified_provenance.append(evidence_id)
        elif provenance_matches:
            # Same turn/session, but the stored content does not represent the
            # required evidence. This is precisely the C3 failure mode.
            candidate = provenance_matches[0]
            provenance_only.append(evidence_id)
            matches[evidence_id] = candidate
            match_types[evidence_id] = "provenance_only"
            match_scores[evidence_id] = round(
                _semantic_similarity(gold_text, _text(candidate)), 4
            )
            missing.append(evidence_id)
        else:
            missing.append(evidence_id)

    return {
        "found": sorted(found),
        "missing": sorted(missing),
        "provenance_only": sorted(provenance_only),
        "unverified_provenance": sorted(unverified_provenance),
        "matches": matches,
        "match_types": match_types,
        "match_scores": match_scores,
        "observed_count": len(observed_list),
    }


def stage_from_observed(gold: Iterable[dict[str, Any]], observed: Iterable[Any]) -> dict[str, Any]:
    result = match_evidence(gold, observed)
    return {k: v for k, v in result.items() if k != "matches"}
