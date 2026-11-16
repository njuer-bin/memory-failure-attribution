# Status Drift Pilot — Protocol v2.7 (Commitment-Targeted Writer)

**Status:** pre-registered; no v2.7 outputs exist yet.
**Branch:** `research/status-drift-v2-pilot`
**Scope:** one new writer prompt targeting intentional commitment cues.

## 1. Why

v2.6 shows the chained-compression failure is concentrated in **intentional**
status. Manual reading of intentional D5:

- neutral: 1 strong cue (`决定`), 1 weak (`推进`), 8 none.
- status-aware: 5 strong, 5 weak (`推进计划`, `按计划`, `已开始`), 0 none.

The status-aware prompt reduces removal but still allows **weakening**. A
targeted prompt may prevent the weakening itself.

## 2. New condition

`commitment_aware` writer prompt. It keeps the status-aware requirements and
adds:

- if the user expressed a decision or commitment, the memory must keep an
  explicit commitment word (`已决定`, `已承诺`, `会按计划执行`);
- it must not weaken this to `推进计划`, `计划中`, `开始考虑`, or a bare action.

No other change to the dataset or metrics.

## 3. Design

- Intentional dimension only.
- 10 topics × stable/updated = 20 trajectories, design v3, `--skip-judge`.
- Compare with the intentional subsets of:
  - `v26_neutral_60`
  - `v26_status_aware_60`
- Writer model and seed unchanged from the generic setup.

## 4. Metrics

- Strict status-cue state (`evaluation.status_cue_metrics`): MATCH / MIXED /
  OPPOSITE / ABSENT.
- Manual strong/weak/none commitment-cue classification for intentional D5.
- Deterministic proposition omission.

## 5. Pre-registered predictions

- **P11:** `commitment_aware` reduces strict intentional recursive D5 ABSENT
  below the status-aware value (5/10).
- **P12:** strong-cue retention (`决定` or `承诺`) reaches ≥8/10 at D3/D5.
- **P13:** proposition omission stays at 0/20.

Null results are valid: if the prompt does not improve strong-cue retention,
report that the weakening is not prompt-fixable in this setup.

## 6. Gates

Interpret only if:

- all 20 trajectories complete and parse;
- deterministic proposition omission < 10%;
- no single topic accounts for more than half of the cue-loss cases.

## 7. Integrity

- Existing v2.6 outputs are unchanged.
- Only the writer prompt changes; dataset and metrics are fixed.
- Manual strong/weak classification is assistant adjudication, not human.
