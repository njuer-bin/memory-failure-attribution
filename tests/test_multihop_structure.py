from evaluation.multihop_schema import EvidenceNode, MultiHopGoldEvidence
from experiments.freeze_multihop_structure import classify


def test_aggregation_is_not_multi_hop_chain():
    row = {"question_id": "conv-26#q0016", "human_is_multi_hop": "yes"}
    structure, _ = classify(row)
    assert structure == "aggregation"


def test_known_relational_cases_are_chains():
    for question_id in ("conv-26#q0011", "conv-26#q0059"):
        structure, _ = classify({"question_id": question_id, "human_is_multi_hop": "yes"})
        assert structure == "chain"


def test_q0041_remains_uncertain():
    structure, note = classify({"question_id": "conv-26#q0041", "human_is_multi_hop": "yes"})
    assert structure == "uncertain"
    assert "adjudication" in note


def test_chain_requires_ordered_path_and_multiple_hops():
    evidence = [EvidenceNode("e0", "home country"), EvidenceNode("e1", "Sweden")]
    item = MultiHopGoldEvidence(
        question_id="q",
        question="Where?",
        reference_answer="Sweden",
        gold_evidence=evidence,
        hop_count=2,
        hop_type="entity",
        evidence_structure="chain",
        ordered_path=["e0", "e1"],
    )
    assert item.validate() == []
    assert item.is_multi_hop


def test_aggregation_has_no_relational_path():
    item = MultiHopGoldEvidence(
        question_id="q",
        question="Where?",
        reference_answer="beach, forest",
        gold_evidence=[EvidenceNode("e0"), EvidenceNode("e1")],
        hop_count=1,
        hop_type="multi_hop",
        evidence_structure="aggregation",
    )
    assert item.validate() == []
    assert not item.is_multi_hop
    assert item.is_aggregation
