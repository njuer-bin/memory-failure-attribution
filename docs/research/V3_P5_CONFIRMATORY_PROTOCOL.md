# V3 P5 Confirmatory Mitigation Protocol — Frozen

**Status:** frozen 2026-11-17 before generation. 30 P2 trajectories × 4
writer conditions = 120 final memories. Deterministic diagnostics plus blind
human annotation under v3.2.3.

## 1. Design

A 2×2 factorial over **prompt** (neutral vs status-aware) and **source access**
(memory-only vs memory + original dialogue), under one fixed 5-stage chain
(220 → 180 → 140 → 120 → 100 characters).

| Condition | Prompt | Source at each rewrite |
|---|---|---|
| `neutral` | neutral | previous memory only |
| `status_aware` | status-aware | previous memory only |
| `neutral_source` | neutral | previous memory + original dialogue |
| `status_aware_source` | status-aware | previous memory + original dialogue |

30 P2 trajectories (10 per dimension, 15 stable / 15 updated), reused by design.
P5 is a mitigation question and is not pooled with the P2/P3 path analysis.

## 2. Excluded strategies

- `evidence_anchored`: pilot 11/12 faithful but 1.84× neutral length and
  frequently wrong evidence tags; fails the budget gate.
- `transition_verification`: pilot 10/12 and dimension-unstable; the verifier
  did not reliably restore dropped status.
- `unknown_heavy`: 5/12 proposition loss; a trivial-abstention control, not a
  mitigation.

## 3. Primary and secondary outcomes

Human labels under v3.2.3:

- **Primary:** faithful status rate (`NO_DISTORTION` + `LEGITIMATE_UPDATE`)
  among proposition-preserved items.
- Secondary: status omission, unsupported distortion, proposition loss, and
  legitimate-update accuracy.
- Reported with counts and denominators, by condition and dimension.

Primary contrast: `status_aware` vs `neutral` (prompt effect, memory-only).
Key secondary: `neutral_source` vs `neutral` (source-access main effect);
`status_aware_source` vs the other cells (interaction); `status_aware_source`
vs `neutral` (best vs baseline).

## 4. Generation settings

- Writer: `qwen2.5:7b`, temperature 0, seed 42.
- Final budget 100 characters; actual lengths recorded, no post-selection.
- All intermediate memories, prompts, token counts, and errors retained.
- Budget gate: no condition may exceed 1.5× the neutral mean final length;
  report actual inflation.

## 5. Annotation

120 final memories, shuffled, anonymized, condition key outside the repository.
Two annotators under the frozen v3.2.3 guide, including `action_status`.
Adjudicate disagreements with a third reviewer; preserve original labels.
Report raw agreement and Cohen's κ per field.

## 6. Analysis

- Paired by trajectory (30 clusters); cluster bootstrap 95% CI.
- Report the full 2×2 cell means and paired contrasts.
- Primary: `status_aware` − `neutral` faithful rate.
- Secondary: source main effect, interaction, and best-vs-baseline.
- No power claim; report effect sizes and intervals.
- Do not pool with P2/P3/P4 or the P5 pilot.

## 7. Exclusions

Predeclared only: generation failure, missing source, malformed artifact, or a
variant that cannot be built. Do not exclude by length, label, or condition
performance. Report all exclusions.

## 8. Freeze

The runner and this protocol are hashed in `V3_P5_CONFIRMATORY_FREEZE.md`.
Any change creates a new version and a separate cohort.
