from tracing.lifecycle import match_evidence


def test_provenance_only_garbage_extraction_is_not_found():
    # Audit C3: an artifact from the gold turn whose content does not
    # represent the evidence must not count as found.
    gold = [{
        "evidence_id": "e0",
        "text": "I am planning a trip to Hawaii and want to make sure my new phone stays charged.",
        "turn_id": "D1:turn_2",
    }]
    garbage_same_turn = [{"id": "a1", "content": "I am a fan of hiking", "turn_id": "D1:turn_2"}]

    result = match_evidence(gold, garbage_same_turn)

    assert result["found"] == []
    assert result["missing"] == ["e0"]
    assert result["provenance_only"] == ["e0"]
    assert result["match_types"]["e0"] == "provenance_only"


def test_provenance_with_matching_content_is_found():
    gold = [{
        "evidence_id": "e0",
        "text": "I went to a LGBTQ support group yesterday and it was powerful.",
        "turn_id": "D1:turn_2",
    }]
    faithful = [{"id": "a1", "content": "I went to a LGBTQ support group yesterday and it was powerful.", "turn_id": "D1:turn_2"}]

    result = match_evidence(gold, faithful)

    assert result["found"] == ["e0"]
    # Content-exact matching outranks provenance under the C3 ladder.
    assert result["match_types"]["e0"] == "exact"
    assert result["provenance_only"] == []


def test_identical_text_from_another_turn_is_not_found():
    # Audit C3: duplicated text in a different turn must not be attributed to
    # the gold turn; provenance conflict overrides content identity.
    gold = [{
        "evidence_id": "e0",
        "text": "I adopted a dog named Biscuit.",
        "turn_id": "D1:turn_2",
    }]
    other_turn = [{"id": "a1", "content": "I adopted a dog named Biscuit.", "turn_id": "D1:turn_9"}]

    result = match_evidence(gold, other_turn)

    assert result["found"] == []
    assert result["missing"] == ["e0"]
    assert result["provenance_only"] == []


def test_artifact_without_provenance_is_matched_but_flagged():
    gold = [{
        "evidence_id": "e0",
        "text": "I adopted a dog named Biscuit.",
        "turn_id": "D1:turn_2",
    }]
    unprovenanced = [{"id": "a1", "content": "I adopted a dog named Biscuit."}]

    result = match_evidence(gold, unprovenanced)

    assert result["found"] == ["e0"]
    assert result["unverified_provenance"] == ["e0"]


def test_evolution_stage_is_not_in_attribution_chain():
    from evaluation import attribution
    assert all(stage != "evolution" for stage, _ in attribution.STAGE_FAILURES)


def test_evolution_recall_is_reported_as_unmeasured():
    from evaluation.lifecycle_metrics import stage_recall, first_loss_stage
    trace = {
        "gold_evidence": [{"evidence_id": "e0"}],
        "formation": {"found": ["e0"]},
        "storage": {"found": ["e0"]},
        "evolution": {"found": []},
        "retrieval": {"found": ["e0"]},
        "rerank": {"found": ["e0"]},
        "context": {"found": ["e0"]},
    }
    assert stage_recall(trace, "evolution") is None
    assert first_loss_stage(trace) is None
