from experiments.analyze_ladder import analyze_ladder


def _row(qid, real, om, oc):
    return {
        "question_id": qid,
        "gold_evidence": [],
        "modes": {
            "real_memory": {"answer": real, "answer_failure_type": None},
            "oracle_memory": {"answer": om, "answer_failure_type": None},
            "oracle_context": {"answer": oc, "answer_failure_type": None},
        },
    }


def test_semantic_accuracy_uses_judged_rows_only():
    rows = {
        "q1": _row(
            "q1",
            {"semantic_correct": True},
            {"semantic_correct": None, "correct": True},
            {"semantic_correct": False},
        )
    }
    result = analyze_ladder(rows)
    systems = result["systems"]
    # Judged-row definition: the unjudged OM row is excluded from the denominator.
    assert systems["real_memory"]["semantic_accuracy"] == 1.0
    assert systems["real_memory"]["semantic_judged"] == 1
    assert systems["oracle_memory"]["semantic_accuracy"] is None
    assert systems["oracle_memory"]["semantic_judged"] == 0
    # Attributed fallback keeps the lexically correct unjudged row.
    assert systems["oracle_memory"]["attributed_accuracy"] == 1.0
    assert systems["oracle_context"]["semantic_accuracy"] == 0.0


def test_paired_pairs_follow_canonical_order():
    rows = {
        f"q{i}": _row(
            f"q{i}", {"semantic_correct": True}, {"semantic_correct": False}, {"semantic_correct": True}
        )
        for i in range(4)
    }
    result = analyze_ladder(rows)
    assert list(result["paired_accuracy"]) == [
        "real_memory_vs_oracle_memory",
        "real_memory_vs_oracle_context",
        "oracle_memory_vs_oracle_context",
    ]
    assert "real_memory_vs_oracle_memory" in result["stage_distribution_tests"]
