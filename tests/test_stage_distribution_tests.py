"""Tests for stage-distribution tests (Stuart-Maxwell, bootstrap, permutation)."""

import math

import pytest

from evaluation.stage_distribution_tests import (
    _chi2_sf,
    paired_label_bootstrap,
    paired_label_permutation,
    stage_distribution_test,
    stuart_maxwell,
)


def test_stuart_maxwell_identical_labels_is_null():
    labels = ["F4", "F5", "none", "F4", "F5"]
    result = stuart_maxwell(labels, labels)
    assert result["p_value"] == pytest.approx(1.0)
    assert result["chi2"] == pytest.approx(0.0)


def test_stuart_maxwell_two_categories_reduces_to_mcnemar_chisq():
    a = ["right", "wrong", "wrong", "right", "right", "wrong", "right", "right",
         "right", "wrong"]
    b = ["right", "right", "wrong", "wrong", "right", "right", "wrong", "wrong",
         "right", "wrong"]
    result = stuart_maxwell(a, b)
    # 2 categories: Stuart-Maxwell is the (uncorrected) McNemar chi-square
    # chi2 = (3-2)^2/(3+2) = 0.2, df 1
    assert result["chi2"] == pytest.approx(0.2, abs=1e-9)
    assert result["df"] == 1
    assert result["p_value"] == pytest.approx(_chi2_sf(0.2, 1), rel=1e-9)


def test_stuart_maxwell_classic_three_category_example():
    # Off-diagonal table (rows = system a, cols = system b):
    #     10   5
    #   3     10
    #   5  10
    # u = row-minus-column marginals = (7, -7, 0); V dropped-z block
    # [[23,-13],[-13,33]]; chi2 = u' V^-1 u = 2.4915, df 2, p ~0.2877.
    # (Hand-verifiable: see docs; matches the standard Stuart-Maxwell
    # computation, e.g. via numpy pinv in the CI.)
    off = {(0, 1): 10, (0, 2): 5, (1, 0): 3, (1, 2): 10, (2, 0): 5, (2, 1): 10}
    a: list[str] = []
    b: list[str] = []
    cats = ["x", "y", "z"]
    for (i, j), count in off.items():
        a.extend([cats[i]] * count)
        b.extend([cats[j]] * count)
    result = stuart_maxwell(a, b)
    assert result["chi2"] == pytest.approx(2.4915, abs=0.001)
    assert result["df"] == 2
    assert result["p_value"] == pytest.approx(0.2877, abs=0.001)


def test_stuart_maxwell_strongly_different_marginals_rejects():
    a = ["F4"] * 8 + ["none"] * 2
    b = ["F5"] * 8 + ["none"] * 2
    result = stuart_maxwell(a, b)
    assert result["p_value"] < 0.01


def test_stuart_maxwell_symmetric_swap_is_not_significant():
    a = ["F4"] * 5 + ["F5"] * 5
    b = ["F5"] * 5 + ["F4"] * 5
    result = stuart_maxwell(a, b)
    assert result["p_value"] > 0.5


def test_stuart_maxwell_handles_none_and_skips():
    result = stuart_maxwell(["F4", None, "none"], ["F5", "F6", None])
    assert result["n"] == 1
    assert result["p_value"] is not None and 0.0 < result["p_value"] <= 1.0


def test_stuart_maxwell_empty():
    result = stuart_maxwell([], [])
    assert result["p_value"] is None
    assert result["n"] == 0


def test_chi2_sf_matches_closed_forms():
    for x in (0.5, 1.0, 3.84):
        assert _chi2_sf(x, 1) == pytest.approx(math.erfc(math.sqrt(x / 2)), rel=1e-9)
    for x in (1.0, 5.0):
        assert _chi2_sf(x, 2) == pytest.approx(math.exp(-x / 2), rel=1e-9)
    # df=3, x=3.0: Q(1.5, 1.5) = erfc(0)? no -- independent numeric value:
    # scipy: 1 - chi2.cdf(3.0, 3) = 0.39162517627108884
    assert _chi2_sf(3.0, 3) == pytest.approx(0.39162517627108884, rel=1e-9)


def test_bootstrap_identical_systems_zero_diff():
    labels = ["F4", "F5", "none", "F4", "F5", "none", "F4", "F5", "none", "F4"]
    result = paired_label_bootstrap(labels, labels, repeats=500, seed=7)
    for label in result["labels"].values():
        assert label["diff"] == 0.0
        assert label["ci_low"] == 0.0
        assert label["ci_high"] == 0.0


def test_bootstrap_detects_large_shift():
    a = ["F4"] * 10 + ["none"] * 10
    b = ["F5"] * 10 + ["none"] * 10
    result = paired_label_bootstrap(a, b, repeats=500, seed=3)
    assert result["labels"]["F4"]["diff"] == pytest.approx(0.5)
    assert result["labels"]["F5"]["diff"] == pytest.approx(-0.5)
    # Resampling is over questions, and every question contributes the same
    # (F4, F5) or (none, none) pair, so the F4 diff concentrates near 0.5.
    assert 0.3 <= result["labels"]["F4"]["ci_low"] <= 0.5
    assert 0.5 <= result["labels"]["F4"]["ci_high"] <= 0.7


def test_bootstrap_paired_resampling_keeps_zero_diff_labels_at_zero():
    a = ["F4"] * 5 + ["none"] * 5
    b = ["F6"] * 5 + ["none"] * 5
    result = paired_label_bootstrap(a, b, repeats=500, seed=11)
    assert result["labels"]["none"]["diff"] == 0.0
    assert result["labels"]["none"]["ci_low"] == 0.0
    assert result["labels"]["none"]["ci_high"] == 0.0


def test_permutation_identical_systems_not_significant():
    labels = ["F4", "F5", "none", "F4", "F5", "none", "F4", "F5", "none", "F4"]
    result = paired_label_permutation(labels, labels, repeats=2000, seed=5)
    assert result["statistic"] == 0.0
    assert result["p_value"] == pytest.approx(1.0)


def test_permutation_detects_large_shift():
    a = ["F4"] * 10 + ["none"] * 10
    b = ["F5"] * 6 + ["F6"] * 4 + ["none"] * 10
    result = paired_label_permutation(a, b, repeats=2000, seed=3)
    # observed max-abs diff = max(|F4 .5|, |F5 .3|, |F6 .2|) = 0.5; under
    # swaps the spread shrinks, so the tail should be small. (A pure
    # two-label even swap leaves the statistic invariant -- that case is
    # Stuart-Maxwell's job.)
    assert result["statistic"] == pytest.approx(0.5)
    assert result["p_value"] < 0.05


def test_permutation_sees_unbalanced_shift():
    a = ["F4"] * 8 + ["none"] * 12
    b = ["F5"] * 8 + ["F4"] * 4 + ["none"] * 8
    result = paired_label_permutation(a, b, repeats=5000, seed=9)
    assert result["p_value"] < 0.05


def test_stage_distribution_test_combines_all_three():
    a = ["F4"] * 6 + ["none"] * 4
    b = ["F5"] * 6 + ["none"] * 4
    result = stage_distribution_test(a, b, bootstrap_repeats=200,
                                     permutation_repeats=200, seed=1)
    assert set(result) == {"stuart_maxwell", "per_label_bootstrap", "permutation"}
    assert result["stuart_maxwell"]["p_value"] < 0.05
