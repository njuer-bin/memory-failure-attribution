# Status Drift Pilot — Protocol v2.4 (Repeated-Seed Variance)

**Status:** pre-registered; no v2.4 outputs exist yet.
**Branch:** `research/status-drift-v2-pilot`
**Scope:** measurement study of writer-side run-to-run variance. No new
condition, no new dataset.

## 1. Why

Two neutral-writer runs with the same seed, model, prompts, and temperature
produced **106/270 different direct/recursive memories** (v3 vs v2.3). That is
large enough to threaten single-run comparisons. Before treating any
condition difference as real, we need a bound on run-to-run variance.

## 2. Design

Three neutral-writer runs of the same 30-trajectory v3 dataset:

- seed 42 — already exists as `v3_neutral`.
- seed 43 — new.
- seed 44 — new.

All use `--design v3 --limit 30 --writer-style neutral --skip-judge`, no
rewrite-matched condition. Writer = `qwen2.5:7b`.

No judge calls are required for the primary variance estimate: the target is
writer-side memory variability. Judges are added only if a metric-level
variance estimate is needed.

## 3. Metrics

Judge-independent, computed per run:

- Memory identity across runs: fraction of identical memories per condition and
  depth (direct D1/D2/D3/D5, recursive D1/D2/D3/D5).
- Status-cue state for updated cases (`evaluation.status_cue_metrics`):
  MATCH / MIXED / OPPOSITE / ABSENT per condition and depth.
- Deterministic proposition omission.
- Deterministic condition omission.

Report per-run counts and the cross-run range (min–max). Do not report a
single-run number as if it were stable.

## 4. Pre-registered reading

- The chaining contrast (direct vs recursive/rewrite-matched) is credible only
  if it exceeds the maximum cross-run difference at the same condition/depth.
- If cross-run ranges overlap the reported effects, the effect is not
  established and must be reported as inconclusive.
- Memory identity below ~80% between identical runs indicates the writer is
  too nondeterministic for single-run claims; increase repeats or reduce
  temperature/sampling variance (e.g., greedy decoding if available).

## 5. Expected outcomes

Either:

- cross-run variance is small relative to the chaining effect (effect stands),
  or
- cross-run variance is comparable to the effect (single-run effect
  inconclusive; report ranges and increase repeats).

Both outcomes are valid. No result is discarded.

## 6. Integrity

- Existing v3/v2.3 outputs are unchanged.
- New runs go to separate directories.
- No judge is used to rescue a null writer-side variance result.
- All runs use the same prompts and dataset; only the seed differs.
