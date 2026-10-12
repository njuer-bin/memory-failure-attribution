from evaluation.multihop_schema import (
    EvidenceNode,
    EvidenceRelation,
    MultiHopGoldEvidence,
    from_locomo_record,
)


def test_multiple_evidence_items_do_not_imply_multi_hop():
    record = {
        "question_id": "q1",
        "question": "What did Alice buy?",
        "answer": "A book and coffee.",
        "evidence_messages": [
            {"id": "D1:1", "text": "Alice bought a book."},
            {"id": "D1:2", "text": "Alice bought coffee."},
        ],
    }
    item = from_locomo_record(record)

    assert item.hop_count == 1
    assert item.is_multi_hop is False
    assert item.annotation_status == "unreviewed"
    assert item.validate() == []


def test_valid_two_hop_path_and_bridge():
    item = MultiHopGoldEvidence(
        question_id="q2",
        question="Why did Alice leave?",
        reference_answer="She moved for a new job.",
        gold_evidence=[
            EvidenceNode("D1:1", "Alice got a new job."),
            EvidenceNode("D2:4", "Alice moved because of the new job."),
        ],
        hop_count=2,
        hop_type="causal",
        ordered_path=["D1:1", "D2:4"],
        relations=[EvidenceRelation("D1:1", "D2:4", "causes", 1)],
        bridge_evidence=["D1:1"],
        annotation_status="human_reviewed",
    )

    assert item.validate() == []
    assert item.is_multi_hop is True


def test_invalid_path_reference_is_rejected():
    item = MultiHopGoldEvidence(
        question_id="q3",
        question="How did the event happen?",
        reference_answer="...",
        gold_evidence=[EvidenceNode("D1:1", "A")],
        hop_count=2,
        hop_type="multi_hop",
        ordered_path=["D1:1", "D1:99"],
    )

    errors = item.validate()
    assert any("unknown evidence ids" in error for error in errors)


def test_record_loader_does_not_guess_relations_or_hops():
    record = {
        "question_id": "q4",
        "question": "When did Bob join?",
        "answer": "In July.",
        "evidence_messages": [
            {"id": "D3:2", "text": "Bob joined in July."},
        ],
    }
    item = from_locomo_record(record)

    assert item.hop_count == 1
    assert item.ordered_path == []
    assert item.relations == []
    assert item.bridge_evidence == []
    assert item.annotation_status == "unreviewed"
