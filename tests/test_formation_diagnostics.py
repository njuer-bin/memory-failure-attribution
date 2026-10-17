"""Regression tests for evidence-based Formation diagnostics."""
from experiments.run_oracle_experiments import _formation_diagnostics


GOLD_TEXT = "Melanie ran a charity race last Saturday for mental health."
EVIDENCE = [{
    "evidence_id": "e0",
    "text": GOLD_TEXT,
    "source_id": "D1",
    "turn_id": "D1:turn_2",
}]


def _stored(raw=None, facts=None):
    return {
        "raw": raw or [],
        "facts": facts or [],
        "relations": [],
        "events": [],
        "rules": [],
        "profiles": [],
    }


def _raw(turn_id="D1:turn_2"):
    return {
        "id": "raw-1",
        "content": GOLD_TEXT,
        "session_id": "D1",
        "source_id": "D1",
        "source_turn_id": turn_id,
        "memory_type": "raw",
    }


def _memory(content, turn_id="D1:turn_2"):
    return {
        "id": "mem-1",
        "content": content,
        "source_session_id": "D1",
        "source_turn_id": turn_id,
        "memory_type": "fact",
    }


def test_unrelated_memory_in_same_session_is_not_representation_mismatch():
    result = _formation_diagnostics(
        EVIDENCE,
        _stored(raw=[_raw()], facts=[_memory("Melanie plans to go camping this summer.")]),
    )[0]

    assert result["classification"] == "F1a_EXTRACTOR_MISS"
    assert result["semantic_memory_count_same_session"] == 1
    assert result["semantic_memory_match_same_session"]["matched"] is False


def test_matching_semantic_memory_at_source_turn_is_formation_ok():
    result = _formation_diagnostics(
        EVIDENCE,
        _stored(raw=[_raw()], facts=[_memory(GOLD_TEXT)]),
    )[0]

    assert result["classification"] == "FORMATION_OK"
    assert result["semantic_memory_match_same_turn"]["matched"] is True


def test_matching_semantic_memory_in_other_turn_is_representation_mismatch():
    result = _formation_diagnostics(
        EVIDENCE,
        _stored(raw=[_raw()], facts=[_memory(GOLD_TEXT, turn_id="D1:turn_5")]),
    )[0]

    assert result["classification"] == "F1c_REPRESENTATION_MISMATCH"
    assert result["semantic_memory_match_same_turn"]["matched"] is False
    assert result["semantic_memory_match_same_session"]["matched"] is True


def test_turn_evidence_does_not_match_raw_message_from_other_turn_in_same_session():
    result = _formation_diagnostics(
        EVIDENCE,
        _stored(raw=[_raw(turn_id="D1:turn_1")], facts=[]),
    )[0]

    assert result["classification"] == "F1d_UNKNOWN"
    assert result["source_message_found"] is False
