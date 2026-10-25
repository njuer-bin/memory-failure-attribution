"""Stage-distribution tests for cross-system fingerprints.

Two systems answer the same questions; each row carries a failure label
(`none` included). The question is whether the two label distributions
differ, not just the accuracy. Three paired tests:

- Stuart-Maxwell marginal-homogeneity test on the K x K paired-label
  contingency table (chi2 = u' V+ u via the pseudo-inverse, df = rank(V)).
- Per-label paired bootstrap CIs for share(a) - share(b).
- Paired permutation test on the max-abs share difference: within each
  question, swap the two systems' labels with probability 1/2; p is the
  two-sided tail of the permuted statistic beyond the observed one.
"""
from __future__ import annotations

import math
import random
from typing import Any, Sequence


def _paired_strings(a: Sequence[Any], b: Sequence[Any]) -> tuple[list[str], list[str]]:
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if not pairs:
        return [], []
    aa, bb = zip(*pairs)
    return [str(x) for x in aa], [str(y) for y in bb]


def _offdiag_counts(la: list[str], lb: list[str], cats: list[str]) -> list[list[float]]:
    index = {c: i for i, c in enumerate(cats)}
    k = len(cats)
    off = [[0.0] * k for _ in range(k)]
    for x, y in zip(la, lb):
        if x != y:
            off[index[x]][index[y]] += 1.0
    return off


def _jacobi_eigen(v: list[list[float]]) -> tuple[list[float], list[list[float]]]:
    """Eigendecomposition of a symmetric matrix via cyclic Jacobi rotations."""
    m = len(v)
    a = [row[:] for row in v]
    vecs = [[1.0 if i == j else 0.0 for j in range(m)] for i in range(m)]
    for _ in range(100):
        off = math.sqrt(sum(a[i][j] ** 2 for i in range(m) for j in range(m) if i != j))
        if off < 1e-14:
            break
        for p in range(m - 1):
            for q in range(p + 1, m):
                if abs(a[p][q]) < 1e-18:
                    continue
                theta = (a[q][q] - a[p][p]) / (2 * a[p][q])
                t = (1 if theta >= 0 else -1) / (abs(theta) + math.sqrt(theta * theta + 1))
                c = 1 / math.sqrt(t * t + 1)
                s = t * c
                for k in range(m):
                    akp, akq = a[k][p], a[k][q]
                    a[k][p] = c * akp - s * akq
                    a[k][q] = s * akp + c * akq
                for k in range(m):
                    apk, aqk = a[p][k], a[q][k]
                    a[p][k] = c * apk - s * aqk
                    a[q][k] = s * apk + c * aqk
                for k in range(m):
                    vkp, vkq = vecs[k][p], vecs[k][q]
                    vecs[k][p] = c * vkp - s * vkq
                    vecs[k][q] = s * vkp + c * vkq
    return [a[i][i] for i in range(m)], vecs


def stuart_maxwell(a: Sequence[Any], b: Sequence[Any]) -> dict[str, Any]:
    """Stuart-Maxwell marginal-homogeneity test on paired categorical labels.

    Null: the marginal distribution of labels is the same for both systems.
    u_i is the row-minus-column marginal for category i; chi2 = u' V+ u with
    the Moore-Penrose pseudo-inverse of the off-diagonal covariance, so the
    statistic stays defined when some category carries no off-diagonal mass.
    df = rank of the retained covariance.
    """
    la, lb = _paired_strings(a, b)
    cats = sorted(set(la) | set(lb))
    k = len(cats)
    n = len(la)
    if n == 0 or k < 2:
        return {"chi2": None, "df": None, "p_value": None, "n": n,
                "categories": cats, "method": "stuart_maxwell",
                "note": "needs >=2 categories"}

    off = _offdiag_counts(la, lb, cats)
    u = [sum(off[i][j] - off[j][i] for j in range(k) if j != i) for i in range(k)]
    if not any(u):
        return {"chi2": 0.0, "df": 0, "p_value": 1.0, "n": n,
                "categories": cats, "method": "stuart_maxwell",
                "note": "identical marginals"}

    v = [[0.0] * k for _ in range(k)]
    for i in range(k):
        v[i][i] = sum(off[i][j] + off[j][i] for j in range(k) if j != i)
        for j in range(i + 1, k):
            v[i][j] = v[j][i] = -(off[i][j] + off[j][i])

    eig, vecs = _jacobi_eigen(v)
    scale = max(abs(e) for e in eig)
    tol = 1e-10 * max(1.0, scale)
    chi2 = 0.0
    df = 0
    for lam, col in zip(eig, zip(*vecs)):
        if lam <= tol:
            continue
        proj = sum(u[i] * col[i] for i in range(k))
        chi2 += proj * proj / lam
        df += 1
    if df == 0:
        return {"chi2": None, "df": 0, "p_value": None, "n": n,
                "categories": cats, "method": "stuart_maxwell",
                "note": "degenerate covariance"}
    p = _chi2_sf(chi2, df)
    return {"chi2": chi2, "df": df, "p_value": p, "n": n,
            "categories": cats, "method": "stuart_maxwell"}


def _chi2_sf(x: float, df: int) -> float:
    """Upper-tail probability of the chi-square distribution (regularized Q)."""
    if x <= 0:
        return 1.0
    if df <= 0:
        return float("nan")
    return _gamma_sf(df / 2.0, x / 2.0)


def _gamma_sf(s: float, x: float) -> float:
    """Upper incomplete gamma Q(s, x) via series/continued-fraction (NR 6.2)."""
    if x <= 0 or s <= 0:
        return float("nan")
    if x < s + 1.0:
        term = 1.0 / s
        total = term
        ap = s
        for _ in range(1000):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-16:
                break
        p = total * math.exp(-x + s * math.log(x) - math.lgamma(s))
        return max(0.0, min(1.0, 1.0 - p))
    b = x + 1.0 - s
    c = 1e300
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - s)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    q = math.exp(-x + s * math.log(x) - math.lgamma(s)) * h
    return max(0.0, min(1.0, q))


def paired_label_bootstrap(
    a: Sequence[Any],
    b: Sequence[Any],
    *,
    repeats: int = 10000,
    seed: int = 42,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Per-label paired bootstrap percentile CIs for share(a) - share(b).

    Resamples questions (rows), preserving each row's pair of labels.
    Contains no p-value: significance comes from stuart_maxwell or
    paired_label_permutation.
    """
    la, lb = _paired_strings(a, b)
    n = len(la)
    if n == 0:
        return {"labels": {}, "repeats": 0, "n": 0}
    cats = sorted(set(la) | set(lb))
    obs_diff = {c: sum(1 for x in la if x == c) / n - sum(1 for x in lb if x == c) / n
                for c in cats}
    rng = random.Random(seed)
    boot_diffs: dict[str, list[float]] = {c: [] for c in cats}
    for _ in range(repeats):
        ca: dict[str, int] = {c: 0 for c in cats}
        cb: dict[str, int] = {c: 0 for c in cats}
        for _ in range(n):
            i = rng.randrange(n)
            ca[la[i]] += 1
            cb[lb[i]] += 1
        for c in cats:
            boot_diffs[c].append(ca[c] / n - cb[c] / n)
    out_labels: dict[str, dict[str, float]] = {}
    for c in cats:
        vals = sorted(boot_diffs[c])
        lo = vals[max(0, int((alpha / 2) * repeats))]
        hi = vals[min(repeats - 1, int((1 - alpha / 2) * repeats))]
        out_labels[c] = {
            "share_a": sum(1 for x in la if x == c) / n,
            "share_b": sum(1 for x in lb if x == c) / n,
            "diff": obs_diff[c],
            "ci_low": lo,
            "ci_high": hi,
        }
    return {"labels": out_labels, "repeats": repeats, "seed": seed, "n": n}


def paired_label_permutation(
    a: Sequence[Any],
    b: Sequence[Any],
    *,
    repeats: int = 10000,
    seed: int = 42,
) -> dict[str, Any]:
    """Paired permutation test on the max-abs label-share difference.

    Statistic T = max_label |share_a(label) - share_b(label)|. Under H0 the
    two systems' labels are exchangeable within each question, so each row's
    (a, b) pair is swapped with probability 1/2. p = P(T_perm >= T_obs) over
    the random swaps, one-sided on the non-negative statistic (T_obs is
    always >= 0 and the swap makes the null distribution symmetric).
    """
    la, lb = _paired_strings(a, b)
    n = len(la)
    if n == 0:
        return {"statistic": None, "p_value": None, "repeats": 0, "n": 0}
    cats = sorted(set(la) | set(lb))

    def max_abs_diff(xa: list[str], xb: list[str]) -> float:
        t = 0.0
        for c in cats:
            d = sum(1 for x in xa if x == c) - sum(1 for x in xb if x == c)
            t = max(t, abs(d) / n)
        return t

    observed = max_abs_diff(la, lb)
    rng = random.Random(seed)
    count_ge = 0
    for _ in range(repeats):
        xa: list[str] = []
        xb: list[str] = []
        for i in range(n):
            if rng.random() < 0.5:
                xa.append(lb[i])
                xb.append(la[i])
            else:
                xa.append(la[i])
                xb.append(lb[i])
        if max_abs_diff(xa, xb) >= observed - 1e-12:
            count_ge += 1
    p = count_ge / repeats
    return {"statistic": observed, "p_value": p, "repeats": repeats,
            "seed": seed, "n": n}


def stage_distribution_test(
    a: Sequence[Any],
    b: Sequence[Any],
    *,
    bootstrap_repeats: int = 10000,
    permutation_repeats: int = 10000,
    seed: int = 42,
) -> dict[str, Any]:
    """All three stage-distribution readouts for one system pair."""
    return {
        "stuart_maxwell": stuart_maxwell(a, b),
        "per_label_bootstrap": paired_label_bootstrap(
            a, b, repeats=bootstrap_repeats, seed=seed),
        "permutation": paired_label_permutation(
            a, b, repeats=permutation_repeats, seed=seed),
    }
