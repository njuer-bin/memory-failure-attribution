from experiments.judge_reliability import reliability_summary


def test_reliability_summary_skips_missing_and_computes_kappa():
    stored = [True, True, False, False, None]
    rerun = [True, False, False, True, True]

    summary = reliability_summary(stored, rerun)

    assert summary["n"] == 4
    assert summary["agreement"] == 0.5
    assert summary["n_stored_true"] == 2
    assert summary["n_rerun_true"] == 3


def test_reliability_summary_perfect_agreement_has_kappa_one():
    summary = reliability_summary([True, False, True], [True, False, True])
    assert summary["agreement"] == 1.0
    assert summary["kappa"] == 1.0
