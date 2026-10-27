"""Paired statistics for comparing oracle conditions.

The oracle experiment is a paired design: every condition answers the same
question, so differences must be tested with paired tests rather than by
comparing independent accuracies. This module provides the minimum needed for
that: McNemar's exact test on discordant pairs, a paired bootstrap confidence
interval for the accuracy difference, and agreement/kappa for judge reliability
(audit I1/I2).
"""
from __future__ import annotations

import math
import random
from typing import Any, Iterable, Sequence


def _as_bool(values: Iterable[Any]) -> list[bool]:
    return [bool(v) for v in values if v is not None]


def paired_table(a: Sequence[Any], b: Sequence[Any]) -> dict[str, int]:
    """Count 2x2 concordant/discordant pairs for two paired boolean outcomes.

    ``n01`` = a incorrect, b correct (first index = a, second = b);
    ``n10`` = a correct, b incorrect.
    """
    if len(a) != len(b):
        raise ValueError("paired_statistics requires equal-length sequences")
    table = {"n00": 0, "n01": 0, "n10": 0, "n11": 0}
    for x, y in zip(a, b):
        if x is None or y is None:
            continue
        key = f"n{int(bool(x))}{int(bool(y))}"
        table[key] += 1
    return table


def mcnemar_exact(a: Sequence[Any], b: Sequence[Any]) -> dict[str, Any]:
    """Two-sided exact McNemar test on the discordant pairs.

    Null hypothesis: the two paired conditions are equally accurate. Uses the
    exact binomial distribution of ``n01`` given ``n01 + n10`` trials, so it is
    valid for the small discordant counts typical of n<=200 benchmarks.
    """
    table = paired_table(a, b)
    n01, n10 = table["n01"], table["n10"]
    n = n01 + n10
    if n == 0:
        return {
            "n01": 0, "n10": 0, "n_discordant": 0,
            "p_value": 1.0, "note": "no discordant pairs",
        }
    k = min(n01, n10)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    p = min(1.0, 2.0 * tail)
    return {
        "n01": n01, "n10": n10, "n_discordant": n,
        "statistic": k, "p_value": p, "method": "exact_binomial_two_sided",
    }


def paired_bootstrap_diff(
    a: Sequence[Any],
    b: Sequence[Any],
    *,
    repeats: int = 5000,
    seed: int = 42,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Paired bootstrap CI for accuracy(a) - accuracy(b).

    Resamples questions (not individual answers), preserving the pairing.
    """
    if len(a) != len(b):
        raise ValueError("paired_statistics requires equal-length sequences")
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if not pairs:
        return {"diff": None, "ci_low": None, "ci_high": None, "repeats": 0}
    diffs = [float(bool(x)) - float(bool(y)) for x, y in pairs]
    observed = sum(diffs) / len(diffs)
    rng = random.Random(seed)
    n = len(diffs)
    estimates = []
    for _ in range(repeats):
        total = 0.0
        for _ in range(n):
            total += diffs[rng.randrange(n)]
        estimates.append(total / n)
    estimates.sort()
    lo = estimates[max(0, int((alpha / 2) * repeats))]
    hi = estimates[min(repeats - 1, int((1 - alpha / 2) * repeats))]
    return {
        "diff": observed, "ci_low": lo, "ci_high": hi,
        "repeats": repeats, "seed": seed, "pairs": n,
    }


def agreement(labels_a: Sequence[Any], labels_b: Sequence[Any]) -> float | None:
    pairs = [(x, y) for x, y in zip(labels_a, labels_b) if x is not None and y is not None]
    if not pairs:
        return None
    return sum(1 for x, y in pairs if bool(x) == bool(y)) / len(pairs)


def cohens_kappa(labels_a: Sequence[Any], labels_b: Sequence[Any]) -> float | None:
    """Cohen's kappa for two boolean raters (judge reliability, audit I2)."""
    pairs = [(bool(x), bool(y)) for x, y in zip(labels_a, labels_b) if x is not None and y is not None]
    n = len(pairs)
    if n == 0:
        return None
    po = sum(1 for x, y in pairs if x == y) / n
    pa1 = sum(1 for x, _ in pairs if x) / n
    pb1 = sum(1 for _, y in pairs if y) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def compare_modes(
    rows: list[dict[str, Any]],
    mode_a: str,
    mode_b: str,
    *,
    verdict_key: str = "semantic_correct",
) -> dict[str, Any]:
    """Compare two modes over rows that contain a per-mode answer verdict."""
    a: list[Any] = []
    b: list[Any] = []
    for row in rows:
        aa = (row.get("modes", {}).get(mode_a, {}).get("answer") or {}).get(verdict_key)
        bb = (row.get("modes", {}).get(mode_b, {}).get("answer") or {}).get(verdict_key)
        a.append(aa)
        b.append(bb)
    table = paired_table(a, b)
    return {
        "mode_a": mode_a,
        "mode_b": mode_b,
        "verdict_key": verdict_key,
        "mcnemar": mcnemar_exact(a, b),
        "bootstrap": paired_bootstrap_diff(a, b),
        "table": table,
    }
