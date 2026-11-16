# Status-Aware Seed Stability — v2.5 Result (2026-11-16)

**Protocol:** `docs/STATUS_DRIFT_PROTOCOL_V2_5.md`
**Runs:** status-aware writer, 30 trajectories, design v3, seeds 42 and 43.
**Status:** completed; measurement study.

## 1. Stability (status-aware, seed 42 vs 43)

Memory identity: **270/270 = 1.000**. Every direct and recursive memory is
byte-identical across the two runs. Deterministic metrics are identical:

| Condition | MATCH | MIXED | OPPOSITE | ABSENT |
|---|---:|---:|---:|---:|
| direct D1–D5 | 7 / 8 / 9 / 10 | 2 / 1 / 0 / 0 | 1 / 1 / 1 / 0 | 0 / 0 / 0 / 0 |
| recursive D1–D5 | 7 / 5 / 6 / 5 | 2 / 3 / 2 / 1 | 1 / 0 / 0 / 1 | 0 / 2 / 2 / 3 |

Proposition omission is 0/30 in every condition.

Because the v25 memories are byte-identical to `v3_status_aware`, all existing
judge outputs for `v3_status_aware` apply exactly to v25. The status-aware
result (agreement 0.952; 3 both-wrong, all `epistemic_02_U`) therefore
replicates on an independent run without re-judging.

## 2. Same-seed writer-prompt contrast (seed 43)

Neutral (`v24_seed43_neutral`) vs status-aware (`v25_seed43_status_aware`),
deterministic status-cue ABSENT for updated cases:

| Condition | neutral ABSENT | status-aware ABSENT | delta |
|---|---:|---:|---:|
| direct D1 / D2 / D3 / D5 | 0 / 1 / 0 / 1 | 0 / 0 / 0 / 0 | 0 / −1 / 0 / −1 |
| recursive D1 | 0 | 0 | 0 |
| recursive D2 | 5 | 2 | **−3** |
| recursive D3 | 6 | 2 | **−4** |
| recursive D5 | 6 | 3 | **−3** |

The status-aware prompt cuts chained cue loss by 3–4 items per depth at the
same seed. The mitigation is not an artifact of comparing different seeds or
distant sessions.

## 3. What the variance actually is

The status-aware writer is byte-identical across two runs, while the neutral
writer is not (seed 42 vs 43/44 = 0.63, seed 43 vs 44 = 0.96). The seed
parameter therefore does **not** control the variability.

The most consistent explanation is **prompt-dependent near-tie
nondeterminism**: at temperature 0, some prompts have stable argmax outputs
(status-aware), while the freer neutral prompt occasionally hits near-ties
where small implementation-level differences flip the memory. The neutral
writer is not reliably deterministic even at temperature 0.

## 4. Consequences

- The status-aware mitigation is stable and replicated at the same seed:
  chained cue ABSENT 2–3/10 vs neutral 5–6/10; direct 0/10 in both.
- Neutral magnitudes must be reported as ranges across runs; status-aware can
  be reported as a stable value for this model/prompt pair.
- Do not treat the `seed` option as a variance control for this setup.
- The v2.4 "between-session" hypothesis should be narrowed: variance is
  prompt-dependent and can occur within the same period; it is not simply a
  seed or session effect.

## 5. Limitations

- Two status-aware runs; both may share the same deterministic path.
- One model pair (qwen2.5:7b writer, qwen/gemma judges).
- Synthetic templates; n=30.
- No judged run of v25 was needed because the memories are identical; this is
  an identity-based replication, not an independent-memory replication.
