"""Precision analysis for the P4.2 v3 positive-control count.

The question is how many authorized-execution scenarios are needed to estimate
a single control-cell rate with a usable interval, and to estimate a paired
present-vs-omitted difference. This is a precision statement, not a power
claim: the pilot is descriptive and the formal run is frozen at the chosen n.

Run:
    G:/aconda/python.exe -m experiments.v3_p4_2_v3_precision
"""

from __future__ import annotations

import math
import random
import statistics

Z = 1.959963984540054
RESAMPLES = 10000
SEED = 20261118


def wilson(p: float, n: int) -> tuple[float, float]:
    denom = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / denom
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def paired_halfwidth(n: int, discordance: float, seed: int = SEED) -> float:
    """Bootstrap half-width of a paired difference with given discordance.

    Each pair is (present, omitted). With probability `discordance` the two
    outcomes differ; the direction is balanced. The marginal rate is 0.5 in
    the discordant pairs, which is the worst case for a binary difference.
    """
    rng = random.Random(seed)
    differences = []
    for _ in range(RESAMPLES):
        total = 0.0
        for _ in range(n):
            if rng.random() < discordance:
                total += 1.0 if rng.random() < 0.5 else -1.0
        differences.append(total / n)
    differences.sort()
    return (differences[int(0.975 * RESAMPLES)] - differences[int(0.025 * RESAMPLES)]) / 2


def main() -> None:
    print("Single-cell Wilson 95% interval half-width")
    print(f"{'n':>4} | " + " | ".join(f"p={p:.2f}" for p in (0.05, 0.10, 0.25, 0.50)))
    for n in (4, 8, 12, 16, 20, 24, 30):
        cells = []
        for p in (0.05, 0.10, 0.25, 0.50):
            low, high = wilson(p, n)
            cells.append(f"{(high - low) / 2:.2f}")
        print(f"{n:>4} | " + " | ".join(cells))

    print("\nPaired present-vs-omitted bootstrap 95% half-width (worst-case 0.5)")
    print(f"{'n':>4} | " + " | ".join(f"d={d:.1f}" for d in (0.10, 0.20, 0.30, 0.40)))
    for n in (4, 8, 12, 16, 20, 24, 30):
        cells = [f"{paired_halfwidth(n, d):.2f}" for d in (0.10, 0.20, 0.30, 0.40)]
        print(f"{n:>4} | " + " | ".join(cells))

    print("\nChosen count: 20 authorized-execution controls.")
    print("Worst-case single-cell half-width at n=20 is "
          f"{(wilson(0.5, 20)[1] - wilson(0.5, 20)[0]) / 2:.2f}; "
          "at p=0.10 it is "
          f"{(wilson(0.10, 20)[1] - wilson(0.10, 20)[0]) / 2:.2f}.")
    print("The pilot's four controls give "
          f"{(wilson(0.5, 4)[1] - wilson(0.5, 4)[0]) / 2:.2f} / "
          f"{(wilson(0.10, 4)[1] - wilson(0.10, 4)[0]) / 2:.2f}; "
          "that is too coarse to separate the three control outcomes.")


if __name__ == "__main__":
    main()
