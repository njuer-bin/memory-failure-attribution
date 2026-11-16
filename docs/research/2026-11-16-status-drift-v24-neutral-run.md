# v2.4 Neutral-Writer Run and Annotation Set (2026-11-16)

**Protocol:** v2.4 (design v3, rewrite-matched, token logging).
**Run:** 30 trajectories, qwen2.5:7b writer and judge, `--writer-style neutral`.
**Output:** `results/status_drift_v2_pilot/v24_full_neutral/`

## 1. Pipeline

- 30/30 trajectories; 0 errors; 0 invalid/missing predictions.
- Token usage logged per writer/judge call (`usage.jsonl`,
  `usage_summary.json`).
- 120-item annotation set per annotator generated under `annotation/`
  (Raw / Direct D5 / Recursive D5 / Rewrite-matched D5; balanced gold statuses).

## 2. Provisional judge metrics

| Condition | D1 | D2 | D3 | D5 |
|---|---:|---:|---:|---:|
| direct accuracy | 0.833 | 0.700 | 0.700 | 0.633 |
| recursive accuracy | 0.767 | 0.533 | 0.433 | 0.433 |
| rewrite-matched accuracy | 0.833 | 0.600 | 0.533 | 0.400 |

Recursive-minus-direct error rate: **+0.067 / +0.167 / +0.267 / +0.200**
(recursive worse at every depth). Rewrite-matched-minus-direct:
0.000 / +0.100 / +0.167 / +0.233.

This is the opposite direction from the status-aware run, where the
recursive-minus-direct deltas were negative. The uncalibrated judge still has
known errors, but the neutral-vs-status-aware contrast is large and consistent
with the deterministic cue metric below.

## 3. Deterministic status-cue metric

Updated cases, n=10 per condition:

| Condition | neutral ABSENT | status-aware ABSENT |
|---|---:|---:|
| direct D1 / D2 / D3 / D5 | 0 / 0 / 0 / 1 | 0 / 0 / 0 / 0 |
| recursive D1 / D2 / D3 / D5 | 0 / 7 / 8 / **8** | 0 / 1 / 1 / **2** |
| rewrite-matched D1 / D2 / D3 / D5 | 0 / 6 / 6 / **8** | 0 / 0 / 0 / **2** |

The neutral writer loses the gold status cue in 8/10 deep updated cases;
the status-aware prompt reduces that to 2/10. This is judge-independent evidence
for the mitigation.

## 4. Token ranges (not token-matched)

Writer completion tokens at D5:

| Condition | mean | min | max |
|---|---:|---:|---:|
| direct D5 | 21.4 | 16 | 28 |
| recursive D5 | 16.1 | 9 | 22 |
| rewrite-matched D5 (final step) | 16.2 | 8 | 22 |

Chained outputs are roughly 25% shorter in tokens than direct outputs. The
conditions therefore are **not** token-budget matched; the recursion contrast
may partly reflect shorter outputs. A genuinely matched-budget experiment is
required before a causal recursion claim. Character and byte lengths are also
recorded, but they are not token counts.

## 5. Annotation set

`v24_full_neutral/annotation/` contains:

- `annotation_items.csv` — 120 items with memory and dialogue text.
- `annotator_A.csv`, `annotator_B.csv` — blank label fields.
- `prevalence.json` — 20 items per gold status.

The set mirrors the status-aware annotation set, so the two runs can be compared
under the same human protocol.

## 6. Interpretation

- The neutral writer reproduces the chaining effect: judge accuracy drops at
  recursive/rewrite D3–D5, and the deterministic cue is absent in 8/10 deep
  updated cases.
- The status-aware writer largely prevents this (cue absent 2/10).
- The effect is not yet token-matched; the chained memories are shorter. Do not
  claim a pure recursion effect until a matched-budget run is done.
- Human annotation of this neutral set is the next step to confirm the effect
  with human labels rather than LLM judges.

## 7. Next

1. Annotate the 120-item neutral set (two annotators, same guide).
2. Build a token-matched follow-up: target the same final writer token count for
   direct, recursive, and rewrite-matched conditions.
3. Compare human drift rates across writers at matched token budgets.
