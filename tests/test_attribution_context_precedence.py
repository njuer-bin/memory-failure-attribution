"""Regression tests for the context-availability precedence in attribution.

The documented attribution rule is: "Gold Evidence reaches final context?
yes -> F6_REASONING_CANDIDATE". The stage walk (F1-F5) applies only when the
evidence never reached the final context. An upstream semantic miss that was
recovered before the final context (e.g. raw-channel retrieval) must not be
reported as an F1-F5 answer failure.
"""
from experiments.run_oracle_experiments import _answer_failure_type


def _mode(**overrides):
    base = {
        "mode": "real_memory",
        "gold_evidence": [{"evidence_id": "q:e0"}],
        "answer": {"correct": False},
        "evidence_sufficiency": {"status": "sufficient"},
        "formation": {"found": []},
        "storage": {"found": ["q:e0"]},
        "evolution": {"found": []},
        "retrieval": {"found": ["q:e0"]},
        "rerank": {"found": ["q:e0"]},
        "context": {"found": ["q:e0"]},
    }
    base.update(overrides)
    return base


def test_full_context_with_formation_miss_is_f6_not_f1():
    # Evidence missing at formation/evolution but fully present in the final
    # context: the wrong answer is not explained by the memory pipeline.
    assert _answer_failure_type(_mode()) == "F6_REASONING"


def test_context_miss_after_formation_miss_is_f1():
    mode = _mode(context={"found": []}, rerank={"found": []}, retrieval={"found": []})
    assert _answer_failure_type(mode) == "F1_FORMATION"


def test_context_miss_with_intact_formation_is_f5():
    mode = _mode(
        formation={"found": ["q:e0"]},
        evolution={"found": ["q:e0"]},
        retrieval={"found": ["q:e0"]},
        rerank={"found": ["q:e0"]},
        context={"found": []},
    )
    assert _answer_failure_type(mode) == "F5_CONTEXT"


def test_retrieval_miss_with_intact_formation_is_f4():
    mode = _mode(
        formation={"found": ["q:e0"]},
        evolution={"found": ["q:e0"]},
        retrieval={"found": []},
        rerank={"found": []},
        context={"found": []},
    )
    assert _answer_failure_type(mode) == "F4_RETRIEVAL"


def test_e0_gate_precedes_attribution():
    mode = _mode(evidence_sufficiency={"status": "insufficient"})
    assert _answer_failure_type(mode) == "E0_EVIDENCE_INSUFFICIENCY"


def test_correct_answer_has_no_failure_type():
    mode = _mode(answer={"correct": True})
    assert _answer_failure_type(mode) is None


def test_oracle_context_wrong_answer_is_reasoning_control():
    mode = _mode(mode="oracle_context")
    assert _answer_failure_type(mode) == "RC_REASONING_CONTROL_FAILURE"
