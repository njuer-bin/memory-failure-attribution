# Status Drift Pilot — Protocol v2.9 (Matched Final-Token Budget)

**Status:** pre-registered; no v2.9 outputs exist yet.
**Branch:** `research/status-drift-v2.4-revision`
**Scope:** one matched-budget control at D5, neutral writer.

## 1. Why

The v2.4 neutral run showed chained outputs are shorter than direct outputs at
D5: mean writer completion tokens 16.1 (recursive), 16.2 (rewrite-matched) vs
21.4 (direct). The status-cue difference could therefore partly reflect a
stronger compression, not only chained rewriting.

## 2. Design

- Neutral writer, 30 trajectories, design v3, rewrite-matched.
- At **D5 only**, iteratively adjust the writer's character budget so that the
  final writer output is close to a common token target.
- Earlier depths (D1–D3) keep their original budgets; only the final D5 output
  is length-matched.
- Target: **21 tokens**, tolerance **±2**, up to **3 attempts** per memory.
  The target comes from the direct-D5 mean of the v2.4 neutral run (21.4),
  rounded down; it is fixed before the run.
- Conditions:
  - direct D5: adjust the one-shot compression of the full dialogue.
  - recursive D5: adjust the final compression of the D4 memory.
  - rewrite-matched D5: adjust the final (step-5) compression.

## 3. Metrics

- Achieved writer `eval_count` at D5: mean, min, max per condition; report
  overlap.
- Deterministic status-cue ABSENT (updated cases).
- Deterministic proposition omission.
- Provisional judge accuracy (secondary; the judge is uncalibrated).

## 4. Pre-registered reading

- If the cue-loss difference between direct and chained persists while the
  achieved token ranges overlap, the chaining effect is not solely a
  length/compression artifact.
- If the difference disappears once token counts are matched, the earlier
  effect is partly explained by shorter chained outputs, and the causal claim
  must be narrowed.
- A null matched-budget difference is a valid, reportable result.

## 5. Gates

Interpret only if:

- all 30 trajectories complete without unreported errors;
- achieved D5 token ranges overlap across the three conditions (or the overlap
  failure is reported explicitly);
- deterministic proposition omission < 10%.

## 6. Integrity

- The target is set from the direct-D5 mean before the matched run; it is not
  tuned to the observed cue results.
- Every attempt is logged in `usage.jsonl` with role and tag.
- This is a pilot (30 trajectories, synthetic); no generalization claim.
