"""Tests for the cross-system fingerprint aggregation."""

from experiments import analyze_systems as analyze


def _mode(answer, failure=None, gate="sufficient", found=("e0",), measured=True):
    return {
        "formation": {"found": list(found), "details": {"measured": measured}},
        "storage": {"found": list(found), "details": {"measured": measured}},
        "retrieval": {"found": list(found), "details": {"measured": measured}},
        "rerank": {"found": list(found), "details": {"measured": measured}},
        "context": {"found": list(found), "details": {"measured": measured}},
        "answer": answer,
        "evidence_sufficiency": {"status": gate},
        "answer_failure_type": failure,
    }


def _row(qid, mode, answer, failure=None):
    return {
        "question_id": qid,
        "gold_evidence": [{"evidence_id": "e0"}],
        "modes": {mode: _mode(answer, failure)},
    }


def test_accuracy_accepts_lexical_when_judge_is_skipped():
    rows = {
        "q1": _row("q1", "verbatim", {"semantic_correct": None, "correct": True}),
        "q2": _row("q2", "verbatim", {"semantic_correct": False, "correct": True}),
        "q3": _row("q3", "verbatim", {"semantic_correct": True, "correct": True}),
    }
    result = analyze.summarize(rows, "verbatim")
    assert result["n"] == 3
    assert result["attributed_accuracy"] == 2 / 3  # q2 stays incorrect
    assert result["semantic_judged"] == 2
    assert result["semantic_accuracy"] == 0.5


def test_failure_distribution_and_stage_recall():
    rows = {
        "q1": _row("q1", "verbatim", {"semantic_correct": False}, "F6_REASONING_CANDIDATE"),
        "q2": _row("q2", "verbatim", {"semantic_correct": True}),
    }
    result = analyze.summarize(rows, "verbatim")
    assert result["failure_distribution"] == {"F6_REASONING_CANDIDATE": 1, "none": 1}
    assert result["failure_share"]["none"] == 0.5
    assert result["stage_recall"]["formation"] == 1.0
    assert result["stage_recall"]["context"] == 1.0


def test_analyze_matches_semantic_questions_by_id():
    systems = {"q1": _row("q1", "verbatim", {"semantic_correct": True})}
    semantic = {
        "q1": _row("q1", "real_memory", {"semantic_correct": False}),
        "q9": _row("q9", "real_memory", {"semantic_correct": True}),
    }
    result = analyze.analyze(systems, semantic)
    assert result["semantic_questions_matched"] == 1
    assert result["systems"]["verbatim"]["n"] == 1
    assert result["systems"]["semantic"]["n"] == 1
    assert result["systems"]["semantic"]["attributed_accuracy"] == 0.0
