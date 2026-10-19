import pytest

from evaluation.paired_stats import (
    cohens_kappa,
    compare_modes,
    mcnemar_exact,
    paired_bootstrap_diff,
    paired_table,
)


def test_paired_table_counts_discordant_pairs():
    a = [True, True, False, False]
    b = [False, True, True, False]
    assert paired_table(a, b) == {"n00": 1, "n01": 1, "n10": 1, "n11": 1}


def test_paired_table_skips_missing_verdicts():
    table = paired_table([True, None, False], [False, True, None])
    assert table["n10"] == 1
    assert table["n01"] == 0
    assert table["n11"] == 0
    assert table["n00"] == 0


def test_mcnemar_exact_matches_known_binomial_value():
    # n01=9, n10=1 -> two-sided exact p = 2*(C(10,0)+C(10,1))/2^10 = 0.021484375
    result = mcnemar_exact([True] * 1 + [False] * 9, [False] * 1 + [True] * 9)
    assert result["n01"] == 9
    assert result["n10"] == 1
    assert result["p_value"] == pytest.approx(0.021484375)


def test_mcnemar_exact_symmetric_pairs_is_not_significant():
    result = mcnemar_exact([True] * 5 + [False] * 5, [False] * 5 + [True] * 5)
    assert result["p_value"] == pytest.approx(1.0)


def test_mcnemar_exact_no_discordant_pairs():
    result = mcnemar_exact([True, False], [True, False])
    assert result["n_discordant"] == 0
    assert result["p_value"] == 1.0


def test_paired_bootstrap_diff_identical_modes_is_zero():
    result = paired_bootstrap_diff([True, False, True], [True, False, True], repeats=200, seed=1)
    assert result["diff"] == 0.0
    assert result["ci_low"] == 0.0
    assert result["ci_high"] == 0.0


def test_paired_bootstrap_diff_requires_equal_length():
    with pytest.raises(ValueError):
        paired_bootstrap_diff([True], [True, False])


def test_cohens_kappa_perfect_and_chance():
    assert cohens_kappa([True, True, False, False], [True, True, False, False]) == pytest.approx(1.0)
    # Agreement equals chance probability -> kappa 0.
    assert cohens_kappa([True, True, False, False], [True, False, True, False]) == pytest.approx(0.0)


def test_compare_modes_reads_nested_verdicts():
    rows = [
        {"modes": {"real_memory": {"answer": {"semantic_correct": True}},
                   "oracle_context": {"answer": {"semantic_correct": False}}}},
        {"modes": {"real_memory": {"answer": {"semantic_correct": False}},
                   "oracle_context": {"answer": {"semantic_correct": False}}}},
    ]
    result = compare_modes(rows, "real_memory", "oracle_context")
    assert result["table"]["n10"] == 1
    assert result["table"]["n00"] == 1
    assert result["mcnemar"]["n_discordant"] == 1
