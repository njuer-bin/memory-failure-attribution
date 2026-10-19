import pytest

from evaluation import attribution


def _gold():
    return [
        {
            "evidence_id": "e0",
            "text": "I went to a LGBTQ support group yesterday.",
            "source_id": "D1",
            "turn_id": "D1:turn_2",
        }
    ]


def _stages(found="e0"):
    return {stage: {"found": [found]} for stage, _ in attribution.STAGE_FAILURES}


def _gate(status="sufficient", confidence="high"):
    return {
        "status": status,
        "evidence_sufficient": status == "sufficient",
        "confidence": confidence,
        "reason": "gate",
        "adjudication": "judge",
    }


def test_gate_missing_raises():
    with pytest.raises(ValueError):
        attribution.attribute_failure({"correct": False, "semantic_correct": False}, {}, _stages(), _gold())


def test_correct_answer_has_no_failure():
    assert attribution.attribute_failure(
        {"correct": True}, _gate(), _stages(), _gold()
    ) is None
    assert attribution.attribute_failure(
        {"correct": False, "semantic_correct": True}, _gate(), _stages(), _gold()
    ) is None


def test_insufficient_evidence_is_e0():
    answer = {"correct": False, "semantic_correct": False, "semantic_confidence": "high"}
    assert attribution.attribute_failure(answer, _gate("insufficient"), _stages(), _gold()) == \
        attribution.E0_EVIDENCE_INSUFFICIENT


def test_uncertain_gate_is_eval():
    answer = {"correct": False, "semantic_correct": False, "semantic_confidence": "medium"}
    assert attribution.attribute_failure(answer, _gate("uncertain"), _stages(), _gold()) == \
        attribution.EVAL_SEMANTIC_UNCERTAIN


def test_low_confidence_is_eval():
    answer = {"correct": False, "semantic_correct": False, "semantic_confidence": "low"}
    assert attribution.attribute_failure(answer, _gate(), _stages(), _gold()) == \
        attribution.EVAL_SEMANTIC_UNCERTAIN


def test_judge_error_is_eval():
    answer = {"correct": False, "semantic_correct": None, "semantic_error": "RuntimeError: boom"}
    assert attribution.attribute_failure(answer, _gate(), _stages(), _gold()) == \
        attribution.EVAL_SEMANTIC_UNCERTAIN


def test_first_missing_stage_is_reported():
    stages = _stages()
    stages["retrieval"] = {"found": []}
    stages["rerank"] = {"found": []}
    stages["context"] = {"found": []}
    answer = {"correct": False, "semantic_correct": False, "semantic_confidence": "high"}
    assert attribution.attribute_failure(answer, _gate(), stages, _gold()) == \
        attribution.F4_RETRIEVAL


def test_f6_when_all_evidence_reaches_context():
    answer = {"correct": False, "semantic_correct": False, "semantic_confidence": "high"}
    assert attribution.attribute_failure(answer, _gate(), _stages(), _gold()) == \
        attribution.F6_REASONING_CANDIDATE


def test_oracle_context_failure_is_rc_control():
    answer = {"correct": False, "semantic_correct": False, "semantic_confidence": "high"}
    assert attribution.attribute_failure(answer, _gate(), _stages(), _gold(), mode="oracle_context") == \
        attribution.RC_REASONING_CONTROL_FAILURE


# Regression: the two calibration-phase judge false-negative shapes. A judge
# that contradicts its own reasoning (bbf86515) or overrides a matching answer
# (c8090214) must not turn a correct answer into F6 — semantic_correct is the
# verdict the protocol consumes, so a deterministic repair upstream that sets
# semantic_correct=True suppresses the failure.
def test_calibration_false_negatives_are_not_f6():
    for candidate in ("4", "7 days"):
        answer = {"correct": False, "semantic_correct": True, "semantic_confidence": "high"}
        assert attribution.attribute_failure(answer, _gate(), _stages(), _gold()) is None


def test_lexical_correct_does_not_override_semantic_incorrect():
    # Audit C1: F6 must be driven by semantic incorrectness. A lexical
    # token-overlap false positive cannot suppress a semantic failure.
    answer = {"correct": True, "semantic_correct": False, "semantic_confidence": "high"}
    assert attribution.attribute_failure(answer, _gate(), _stages(), _gold()) == \
        attribution.F6_REASONING_CANDIDATE


def test_missing_semantic_confidence_is_uncertain():
    answer = {"correct": False, "semantic_correct": False}
    assert attribution.attribute_failure(answer, _gate(), _stages(), _gold()) == \
        attribution.EVAL_SEMANTIC_UNCERTAIN


def test_gate_is_judged_against_benchmark_answer_not_model_answer():
    # Non-circularity: the gate's evaluate_answer call must receive the
    # benchmark reference, never the model's failed prediction.
    seen = {}

    def fake_gate_eval(question, candidate, evidence, **kwargs):
        seen["candidate"] = candidate
        seen["candidate_is_reference"] = kwargs.get("candidate_is_reference")
        return {"evidence_sufficient": True, "confidence": "high", "reason": "", "adjudication": "judge"}

    original = attribution.evaluate_answer
    attribution.evaluate_answer = fake_gate_eval
    try:
        gate = attribution.evidence_sufficiency_gate("Q?", "benchmark reference", _gold())
    finally:
        attribution.evaluate_answer = original
    assert seen["candidate"] == "benchmark reference"
    assert seen["candidate_is_reference"] is True
    assert gate["status"] == "sufficient"
