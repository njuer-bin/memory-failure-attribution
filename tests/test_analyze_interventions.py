"""Tests for the same-sample intervention analysis."""

from experiments import analyze_interventions as analysis


def _row(qid, arm, *, baseline, repaired, stage="formation", skipped=False):
    return {
        "question_id": qid,
        "arm": arm,
        "skipped": skipped,
        "target_stage": stage,
        "baseline": {"semantic_correct": baseline},
        "repaired": {"semantic_correct": repaired},
    }


def test_common_questions_requires_a_scored_row_in_every_arm():
    rows = [
        _row("q1", "first_loss", baseline=False, repaired=True),
        _row("q1", "path", baseline=False, repaired=True),
        _row("q1", "agnostic", baseline=False, repaired=True),
        # q2 is missing the agnostic arm; q3 has no repaired verdict.
        _row("q2", "first_loss", baseline=False, repaired=True),
        _row("q2", "path", baseline=False, repaired=False),
        _row("q3", "first_loss", baseline=False, repaired=None),
        _row("q3", "path", baseline=False, repaired=True),
        _row("q3", "agnostic", baseline=False, repaired=True),
        # q4 was skipped everywhere (no target stage).
        _row("q4", "first_loss", baseline=None, repaired=None, stage=None, skipped=True),
        _row("q4", "path", baseline=None, repaired=None, stage=None, skipped=True),
        _row("q4", "agnostic", baseline=None, repaired=None, stage=None, skipped=True),
    ]
    grouped = analysis.by_question(rows)
    assert analysis.common_questions(grouped, analysis.ALL_ARMS) == ["q1"]
    assert analysis.common_questions(grouped, ("first_loss", "path")) == ["q1", "q2"]


def test_analyze_reports_per_arm_and_pairwise_on_common_subset():
    rows = [
        _row("q1", "first_loss", baseline=False, repaired=False),
        _row("q1", "path", baseline=False, repaired=True),
        _row("q1", "agnostic", baseline=False, repaired=True),
        _row("q2", "first_loss", baseline=True, repaired=True),
        _row("q2", "path", baseline=True, repaired=False),
        _row("q2", "agnostic", baseline=True, repaired=True),
        # q3 targets only first_loss; it must stay out of the common subset.
        _row("q3", "first_loss", baseline=False, repaired=True, stage="context"),
        _row("q3", "path", baseline=None, repaired=None, stage=None, skipped=True),
        _row("q3", "agnostic", baseline=None, repaired=None, stage=None, skipped=True),
    ]
    result = analysis.analyze(rows, analysis.ALL_ARMS)

    assert result["common_questions"] == 2
    assert result["per_arm"]["first_loss"]["targeted_rows"] == 3
    assert result["per_arm"]["first_loss"]["common_subset"]["compared_correct"] == 1

    pair = result["pairwise_common_subset"]["first_loss_vs_path"]
    assert pair["pairs"] == 2
    assert pair["accuracy_a"] == 0.5
    assert pair["accuracy_b"] == 0.5
    assert pair["mcnemar"]["n01"] == 1
    assert pair["mcnemar"]["n10"] == 1


def test_analyze_handles_an_empty_common_subset():
    rows = [
        _row("q1", "first_loss", baseline=False, repaired=True),
        _row("q1", "path", baseline=None, repaired=None, stage=None, skipped=True),
        _row("q1", "agnostic", baseline=None, repaired=None, stage=None, skipped=True),
    ]
    result = analysis.analyze(rows, analysis.ALL_ARMS)
    assert result["common_questions"] == 0
    assert result["pairwise_common_subset"]["first_loss_vs_path"]["accuracy_a"] is None
