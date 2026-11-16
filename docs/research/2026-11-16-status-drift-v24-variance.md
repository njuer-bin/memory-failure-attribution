# Repeated-Seed Variance — v2.4 Result (2026-11-16)

**Protocol:** `docs/STATUS_DRIFT_PROTOCOL_V2_4.md`
**Runs:** neutral writer, 30 trajectories each, design v3, seeds 42/43/44.
**Status:** completed; measurement study.

## 1. Memory identity

| Pair | Mean identity | direct D1/D2/D3/D5 | recursive D1/D2/D3/D5 |
|---|---:|---|---|
| 42 vs 43 | 0.642 | 0.700 / 0.867 / 0.700 / 0.767 | 0.700 / 0.533 / 0.433 / 0.433 |
| 42 vs 44 | 0.629 | 0.733 / 0.867 / 0.700 / 0.700 | 0.667 / 0.500 / 0.433 / 0.433 |
| 43 vs 44 | **0.963** | 0.967 / 1.000 / 1.000 / 0.867 | 0.967 / 0.967 / 0.967 / 0.967 |

Seeds 43 and 44 are nearly byte-identical; seed 42 differs substantially from
both. This is **not** a simple seed effect: if the seed controlled sampling,
two different seeds would not be 96% identical while a third differs by 37%.

Most likely explanation: the seed-42 run was produced in an earlier session /
model state (before a model reload or cache change). The writer is nearly
deterministic within a session, but not across sessions. This is a
**between-session reproducibility** problem, not only a seed-variance problem.

## 2. Deterministic status-cue ranges (updated cases, n=10/depth)

| Condition | run 42 ABSENT | run 43 ABSENT | run 44 ABSENT | range |
|---|---:|---:|---:|---:|
| direct D1 | 0 | 0 | 0 | 0 |
| direct D2 | 0 | 1 | 1 | 0–1 |
| direct D3 | 1 | 0 | 0 | 0–1 |
| direct D5 | 1 | 1 | 1 | 1 |
| recursive D1 | 0 | 0 | 0 | 0 |
| recursive D2 | 7 | 5 | 5 | 5–7 |
| recursive D3 | 7 | 6 | 6 | 6–7 |
| recursive D5 | 8 | 6 | 6 | 6–8 |

The chaining contrast is robust: direct ABSENT is 0–1, recursive D3/D5 ABSENT is
6–8, across all three runs. The cross-run range (≤2) is far smaller than the
chaining difference (5–8).

## 3. Deterministic proposition omission

Range across runs: 0–2/30 in every condition. Proposition loss is negligible and
does not explain the cue loss.

## 4. Interpretation

- **Aggregate cue effects are stable; memory-level outputs are not.** The
  direct-versus-recursive cue-loss gap survives between-session variability.
- **Single-run memory-level claims are unreliable.** The same condition can
  produce 37% different memories across sessions. Report aggregate ranges.
- **The seed is not the main source of variance.** Two different seeds were
  96% identical. The dominant factor is between-session model state.
- **Protocol reading:** the chaining effect exceeds the cross-run range, so it
  stands. The exact magnitude should be reported as a range, not a point
  estimate.

## 5. Consequences

1. Report status-cue ABSENT counts as ranges across runs.
2. Do not compare two single runs as if the only difference were the
   experimental condition; both must be run in the same session or with
   repeated seeds in each session.
3. The v3 neutral-vs-status-aware comparison is between sessions and therefore
   approximate in magnitude; the within-run v2.3 contrasts (direct vs
   recursive vs rewrite-matched) remain the strongest evidence.
4. Add a same-session A/B run for the writer-prompt contrast if the exact
   magnitude matters.

## 6. Limitations

- Three runs, all neutral, all synthetic, n=30.
- No judged variance estimate; this is writer-side and cue-level only.
- The cause of the session effect (model reload, cache, kernel) is not
  identified.
