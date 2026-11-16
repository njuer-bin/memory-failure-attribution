# v2.3 status-aware run — PARTIAL STATE (2026-11-16)

**Stopped:** the background job was killed by the Claude Code harness because the
system was critically low on memory while the session was idle. Not a code or
experiment failure. Do not restart automatically.

## Completed

| Component | Status |
|---|---|
| 30 writer trajectories (`--rewrite-matched`) | 30/30 |
| qwen2.5:7b judge | 390/390 |
| gemma3:12b judge | 273/390 |

## Partial qwen metrics

- raw 1.000; direct 0.967 at every depth.
- recursive: d1 0.967, d2 0.933, d3 0.900, d5 0.900.
- rewrite-matched: d1 0.967, d2 0.967, d3 0.933, d5 0.933.
- Deterministic proposition omission 0 at every depth.
- Deterministic condition omission 0 except recursive d3/d5 = 0.1.

Interpretation: under the status-aware writer, rewrite-matched ≈ recursive and
both are only slightly below direct. This is the expected P10 direction, but
gemma is incomplete, so it is not a final result.

## Deterministic status cue (updated cases, n=10/depth)

| Condition | D5 MATCH | D5 ABSENT |
|---|---:|---:|
| direct | 10 | 0 |
| recursive | 4 | 5 |
| rewrite-matched | 4 | 4 |

Chained rewriting still removes the status cue in roughly half of deep updated
cases even with the status-aware prompt, but the judge often recovers the status
from remaining context.

## To resume (only when the user asks)

    python -m experiments.status_drift_judge_calibration \
      --records results/status_drift_v2_pilot/v23_status_aware/records.jsonl \
      --judge-model gemma3:12b \
      --out-dir results/status_drift_v2_pilot/v23_status_aware \
      --resume

`--resume` keeps the 273 completed gemma items and judges only the missing 117.
