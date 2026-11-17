# V3 Replication Protocol — Second Model (gemma3:12b)

**Status:** frozen 2026-11-17 before generation. Two phases: writer replication
(R1) and agent replication (R2), both with `gemma3:12b`.

## 1. R1 — Writer replication

12 P2 trajectories (first 2 topics × 2 update variants × 3 dimensions = 4 per
dimension). Conditions:

| Condition | Definition |
|---|---|
| `direct` | one writer call from the full dialogue to budget 100. |
| `recursive` | 5-stage chain 220 → 180 → 140 → 120 → 100. |
| `rewrite_matched` | 5-stage chain 220 → 220 → 220 → 220 → 100. |
| `repeated_direct` | 5 independent direct compressions at 100, keep the last. |
| `neutral_source` | 5-stage chain with the original dialogue available at each rewrite. |
| `status_aware` | 5-stage chain with the status-aware prompt. |
| `status_aware_source` | status-aware prompt + original dialogue at each rewrite. |

84 final memories. Writer `gemma3:12b`, temperature 0, seed 42, final budget
100. Deterministic status cues are diagnostics; blind human labels under
v3.2.4 are the primary replication outcome.

Key replication contrasts:

- direct vs recursive (chain effect);
- rewrite_matched vs recursive (budget mechanism);
- repeated_direct vs recursive (call count);
- neutral_source vs recursive (source access);
- status_aware vs recursive (prompt mitigation);
- status_aware_source vs neutral_source (non-additivity).

## 2. R2 — Agent replication

30 P2 trajectories × `present` / `omitted` / `distorted` / `no_memory`, same
sandboxed action task and scoring as P4. Agent `gemma3:12b`, temperature 0,
seed 42. 120 decisions; automatic outcomes; no human annotation.

Key replication contrasts: omitted vs present on unauthorized action;
distorted vs present on unauthorized action.

## 3. Analysis

- R1: human faithful status (`NO_DISTORTION` + `LEGITIMATE_UPDATE`) among
  PRESERVED, by condition; paired by trajectory; report counts and exact
  proportions. Compare direction and magnitude to the qwen results; label as
  replicated only if the same sign and a non-trivial effect.
- R2: unauthorized-action rate by variant; paired by trajectory; compare to
  qwen.
- No pooling with the qwen confirmatory cohorts; replication is a separate
  cohort.

## 4. Gates

- R1: 12/12 trajectories, 84/84 conditions, 0 failure; budget inflation
  reported; annotation schema-valid and κ reported.
- R2: 30/30 trajectories, 120/120 decisions, 0 parse failures.
- Replication interpretation is descriptive; no power claim.

## 5. Freeze

The runners and this protocol are hashed in
`V3_REPLICATION_FREEZE.md`.
