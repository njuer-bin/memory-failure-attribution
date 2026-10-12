from experiments.generate_multihop_candidates import candidate_record


def test_two_evidence_items_are_candidates_but_not_labeled_multihop():
    record = {
        "dataset": "locomo_refined_public",
        "family": "LoCoMo-Refined",
        "example_id": "x:0",
        "question_id": "q1",
        "question": "What did Alice do later?",
        "answer": "She joined the club.",
        "gold_evidence": [
            {"evidence_id": "e1", "source_id": "D1", "turn_id": "D1:turn_1", "text": "Alice moved."},
            {"evidence_id": "e2", "source_id": "D2", "turn_id": "D2:turn_2", "text": "Alice joined the club."},
        ],
        "task_type": [],
    }
    candidate = candidate_record(record)
    assert candidate is not None
    assert "multiple_gold_evidence_items" in candidate["candidate_reasons"]
    assert candidate["review"]["hop_count"] is None
    assert candidate["review"]["ordered_path"] == []
    assert candidate["review"]["relations"] == []


def test_single_evidence_without_question_signal_is_not_candidate():
    record = {
        "dataset": "locomo_refined_public",
        "family": "LoCoMo-Refined",
        "example_id": "x:1",
        "question_id": "q2",
        "question": "What is Alice's hobby?",
        "answer": "Running.",
        "gold_evidence": [
            {"evidence_id": "e1", "source_id": "D1", "turn_id": "D1:turn_1", "text": "Alice likes running."},
        ],
        "task_type": [],
    }
    assert candidate_record(record) is None


def test_temporal_and_benchmark_multihop_signals_are_recorded_separately():
    record = {
        "dataset": "locomo_refined_public",
        "family": "LoCoMo-Refined",
        "example_id": "x:2",
        "question_id": "q3",
        "question": "When did Bob move after the meeting?",
        "answer": "In July.",
        "gold_evidence": [
            {"evidence_id": "e1", "source_id": "D1", "turn_id": "D1:turn_1", "text": "They had a meeting."},
        ],
        "task_type": ["multi_hop"],
    }
    candidate = candidate_record(record)
    assert candidate is not None
    assert "temporal_question_signal" in candidate["candidate_reasons"]
    assert "benchmark_task_type_multi_hop" in candidate["candidate_reasons"]
    assert candidate["review"]["hop_type"] == "unknown"
