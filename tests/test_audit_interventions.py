"""Tests for the Phase-0 intervention audit."""

from experiments import audit_interventions as audit


def test_holm_adjust_is_step_down_and_monotone():
    adjusted = audit.holm_adjust([0.01, 0.04, 0.03])
    assert adjusted == [0.03, 0.06, 0.06]


def test_holm_adjust_caps_at_one():
    assert audit.holm_adjust([0.5, 0.9]) == [1.0, 1.0]


def _baseline_row(qid, failure_type):
    return {"question_id": qid, "modes": {"real_memory": {"answer_failure_type": failure_type}}}


def _row(qid, arm, *, stored, baseline, repaired, stage="formation", adjudication="judge"):
    return {
        "question_id": qid,
        "arm": arm,
        "skipped": False,
        "target_stage": stage,
        "stored_baseline_semantic_correct": stored,
        "baseline": {"semantic_correct": baseline, "answer": "a",
                     "semantic_adjudication": adjudication},
        "repaired": {"semantic_correct": repaired, "answer": "a b",
                     "semantic_adjudication": adjudication},
    }


def test_audit_flags_losses_that_land_on_stale_labels():
    # q1: stored failure, but the fresh baseline is already correct (stale label);
    # the arm then "loses" it. That loss must be attributed to staleness.
    rows = [
        _row("q1", "first_loss", stored=False, baseline=True, repaired=False),
        _row("q2", "first_loss", stored=False, baseline=False, repaired=True),
    ]
    result = audit.audit(rows, [_baseline_row("q1", "F1_FORMATION"),
                                _baseline_row("q2", "F1_FORMATION")])
    arm = result["per_arm"]["first_loss"]
    assert arm["net_flips"] == 0
    assert arm["losses_on_stale_labels"] == 1
    assert arm["gains_on_stale_labels"] == 0
    assert result["stale_label_questions"] == 1


def test_audit_counts_deterministic_flip_provenance_and_itt():
    rows = [
        _row("q1", "agnostic", stored=False, baseline=False, repaired=True,
             adjudication="deterministic_temporal"),
        _row("q2", "agnostic", stored=False, baseline=False, repaired=True),
    ]
    result = audit.audit(rows, [_baseline_row("q1", "F1_FORMATION"),
                                _baseline_row("q2", "F1_FORMATION")])
    arm = result["per_arm"]["agnostic"]
    assert arm["deterministic_flips"] == 1
    assert arm["flip_provenance"]["judge"] == 1
    assert arm["itt_accuracy_gain"] == 1.0


def test_eval_rows_are_not_targeted():
    rows = [_row("q1", "first_loss", stored=False, baseline=False, repaired=True,
                 stage=None)]
    result = audit.audit(rows, [_baseline_row("q1", "EVAL_SEMANTIC_UNCERTAIN")])
    assert result["per_arm"]["first_loss"]["paired_rows"] == 0
    assert result["per_arm"]["first_loss"]["eval_negative_control"]["rows"] == 0
