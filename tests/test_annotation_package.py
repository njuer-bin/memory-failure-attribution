"""Tests for the annotation package and scoring."""

import random

from experiments import build_annotation_package as build_pkg
from experiments import score_annotations as scoring


def _row(qid, correct, gate="sufficient", answer="a", gold="evidence"):
    return {
        "question_id": qid,
        "question": f"question {qid}",
        "gold_answer": "a",
        "gold_evidence": [{"evidence_id": f"{qid}:e0", "text": gold}],
        "modes": {"real_memory": {
            "answer": {"answer": answer, "semantic_correct": correct},
            "evidence_sufficiency": {"status": gate},
            "answer_failure_type": "F1_FORMATION" if correct is False else None,
        }},
    }


def test_stratified_sample_is_deterministic_and_bounded():
    rows = ([_row(f"c{i}", True) for i in range(10)]
            + [_row(f"w{i}", False) for i in range(10)]
            + [_row(f"e{i}", None, gate="insufficient") for i in range(10)])
    first = build_pkg.stratified_sample(rows, 9, random.Random(7))
    second = build_pkg.stratified_sample(rows, 9, random.Random(7))
    assert [r["question_id"] for r in first] == [r["question_id"] for r in second]
    assert len(first) == 9
    strata = {build_pkg._stratum(r) for r in first}
    assert strata == {"correct|sufficient", "incorrect|sufficient", "unjudged|insufficient"}


def test_build_separates_annotations_from_the_hidden_key():
    annotations, key = build_pkg.build("bench", [_row("q1", False)], 1, random.Random(1))
    assert len(annotations) == 1 and len(key) == 1
    assert "semantic_correct" not in annotations[0]
    assert key[0]["stored_semantic_correct"] == "False"
    assert annotations[0]["model_answer"] == "a"


def test_precision_recall_f1_handles_missing_classes():
    assert scoring.precision_recall_f1([True, True], [True, True]) == {
        "tp": 2, "fp": 0, "fn": 0, "precision": 1.0, "recall": 1.0, "f1": 1.0, "n": 2,
    }
    result = scoring.precision_recall_f1([False, False], [True, False])
    assert result["precision"] == 0.0
    assert result["recall"] is None


def test_score_uses_human_labels_and_reports_disagreements():
    key = {
        "s1": {"stored_semantic_correct": "True", "gate_status": "sufficient"},
        "s2": {"stored_semantic_correct": "False", "gate_status": "insufficient"},
        "s3": {"stored_semantic_correct": "True", "gate_status": "sufficient"},
    }
    a = {
        "s1": {"answer_correct_yes_no_uncertain": "yes",
               "evidence_sufficient_yes_no_uncertain": "yes"},
        "s2": {"answer_correct_yes_no_uncertain": "no",
               "evidence_sufficient_yes_no_uncertain": "no"},
        "s3": {"answer_correct_yes_no_uncertain": "yes",
               "evidence_sufficient_yes_no_uncertain": "yes"},
    }
    b = {
        "s1": {"answer_correct_yes_no_uncertain": "yes",
               "evidence_sufficient_yes_no_uncertain": "yes"},
        # Disagrees on s2: the row is excluded from the evaluator score.
        "s2": {"answer_correct_yes_no_uncertain": "yes",
               "evidence_sufficient_yes_no_uncertain": "yes"},
        "s3": {"answer_correct_yes_no_uncertain": "uncertain",
               "evidence_sufficient_yes_no_uncertain": "yes"},
    }
    result = scoring.score(key, {"a": a, "b": b})
    field = result["fields"]["answer_correct_yes_no_uncertain"]
    assert field["evaluator_vs_human"] == {
        "tp": 2, "fp": 0, "fn": 0, "precision": 1.0, "recall": 1.0, "f1": 1.0, "n": 2,
    }
    assert field["excluded_uncertain_or_missing"] == 1
    assert result["inter_annotator_answer_correct_yes_no_uncertain"]["kappa"] is not None
