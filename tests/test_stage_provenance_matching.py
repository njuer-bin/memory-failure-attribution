from tracing import engine_trace


def test_stage_match_rejects_semantic_match_from_wrong_turn(monkeypatch):
    monkeypatch.setattr(
        engine_trace,
        "match_evidence",
        lambda gold, artifacts: {
            "found": [gold[0]["evidence_id"]],
            "missing": [],
            "dropped": [],
            "matches": {gold[0]["evidence_id"]: artifacts[0]},
            "match_types": {gold[0]["evidence_id"]: "semantic"},
            "match_scores": {gold[0]["evidence_id"]: 0.66},
        },
    )

    result = engine_trace.stage_match(
        [{"evidence_id": "e0", "turn_id": "D1:turn_8"}],
        [{"id": "wrong", "source_turn_id": "D4:turn_14", "content": "semantically similar"}],
    )

    assert result["found"] == []
    assert result["missing"] == ["e0"]
    assert result["matches"] == {}
    assert result["match_types"] == {}
    assert result["semantic_matches"]["e0"]["id"] == "wrong"
    assert result["semantic_match_types"]["e0"] == "semantic"
    assert result["semantic_match_scores"]["e0"] == 0.66


def test_stage_match_accepts_exact_turn_provenance(monkeypatch):
    monkeypatch.setattr(
        engine_trace,
        "match_evidence",
        lambda gold, artifacts: {
            "found": [],
            "missing": [gold[0]["evidence_id"]],
            "dropped": [],
            "matches": {},
            "match_types": {},
            "match_scores": {},
        },
    )

    result = engine_trace.stage_match(
        [{"evidence_id": "e0", "turn_id": "D1:turn_8"}],
        [{"id": "correct", "source_turn_id": "D1:turn_8", "content": "exact source"}],
    )

    assert result["found"] == ["e0"]
    assert result["missing"] == []
    assert result["matches"]["e0"]["id"] == "correct"
    assert result["match_types"]["e0"] == "provenance"
    assert result["match_scores"]["e0"] == 1.0
    assert result["semantic_matches"] == {}


def test_stage_match_requires_all_gold_turns(monkeypatch):
    monkeypatch.setattr(
        engine_trace,
        "match_evidence",
        lambda gold, artifacts: {
            "found": [],
            "missing": [item["evidence_id"] for item in gold],
            "dropped": [],
            "matches": {},
            "match_types": {},
            "match_scores": {},
        },
    )

    result = engine_trace.stage_match(
        [
            {"evidence_id": "e0", "turn_id": "D1:turn_8"},
            {"evidence_id": "e1", "turn_id": "D1:turn_10"},
        ],
        [{"id": "correct-e0", "source_turn_id": "D1:turn_8"}],
    )

    assert result["found"] == ["e0"]
    assert result["missing"] == ["e1"]
