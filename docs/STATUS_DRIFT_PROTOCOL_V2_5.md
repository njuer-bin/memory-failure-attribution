# Status Drift Pilot — Protocol v2.5 (Status-Aware Seed Stability)

**Status:** pre-registered; no v2.5 outputs exist yet.
**Branch:** `research/status-drift-v2-pilot`
**Scope:** repeated-seed stability of the status-aware writer. No new condition
or dataset change.

## 1. Why

The main mitigation claim — the status-aware prompt reduces chained status
drift from 23 to 3 both-wrong items — rests on a single status-aware run
(`v3_status_aware`, seed 42). The neutral writer already showed large run-to-run
memory variability (mean identity 0.64 between seeds 42 and 43). The
status-aware claim needs at least one independent repeat.

## 2. Design

Run the status-aware writer once more:

- seed 43, design v3, 30 trajectories, `--skip-judge`, no rewrite-matched.
- Compare with `v3_status_aware` (seed 42).

No judge calls are required for the primary estimate; the target is writer-side
memory and cue variability. Judges can be added later if metric-level variance
is needed.

## 3. Metrics

Judge-independent:

- Memory identity between seed 42 and seed 43, per condition and depth.
- Status-cue state for updated cases (`evaluation.status_cue_metrics`):
  MATCH / MIXED / OPPOSITE / ABSENT.
- Deterministic proposition omission.
- Deterministic condition omission.

Report per-run values and the cross-run difference. Do not report a single run
as stable.

## 4. Pre-registered reading

- The status-aware mitigation is credible if, across both seeds,
  direct ABSENT stays at 0–1/10 and recursive D5 ABSENT stays clearly below the
  neutral range (approximately 5–8/10).
- If status-aware recursive D5 ABSENT overlaps the neutral range, the mitigation
  claim is weakened and must be reported as seed-dependent.
- If memory identity is below ~80%, repeat once more before drawing any
  memory-level conclusion.

## 5. Integrity

- Existing outputs are unchanged; the new run goes to a separate directory.
- Same prompts, dataset, and model; only the seed changes.
- No judge is used to rescue a null writer-side result.
