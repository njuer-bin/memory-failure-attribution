# v3 30-trajectory run — PARTIAL STATE (2026-11-16)

**Stopped:** the background job was killed by the Claude Code harness because the
system was critically low on memory while the session was idle. This is not a
code or experiment failure. Do not restart automatically.

## What completed

| Directory | Records | qwen judge | gemma judge |
|---|---:|---:|---:|
| `v3_status_aware` | 30/30 | 270/270 | 263/270 |
| `v3_neutral` | 30/30 | 0/270 | 0/270 |

## Provisional status-aware metrics (263 common items)

- Inter-judge agreement: 250/263 = 0.951.
  - epistemic 83/90 = 0.922
  - intentional 90/90 = 1.000
  - conditional 77/83 = 0.928
- Deterministic proposition omission: 0/263.
- Deterministic condition omission: 2/83 = 0.024; ambiguous 9; wrong label 0.
- Both-judges-wrong candidates: **1**
  - `epistemic_02_U | recursive_d5`: gold CERTAIN, qwen POSSIBLE, gemma
    POSSIBLE. Memory: `申请研究生；当前日期和天气不确定；专注课程和日常事务。`
    The confirmation cue is gone at D5. Real writer-side cue loss, not judge
    error.
- Condition omissions (2):
  - `conditional_01_U | recursive_d3` and `recursive_d5`:
    `将去上海工作。` / `去上海工作。` — condition status gone.

## Interpretation (provisional)

- Status-aware writer is stable at most depths; the only clear epistemic
  both-judge error is one D5 cue loss in a third topic (申请研究生).
- Conditional condition omission is low (2/83) but concentrated at D3/D5.
- These are provisional: 7 status-aware gemma items and the entire neutral
  writer judging are missing.

## To resume (only when the user asks)

1. Add resume support to `experiments/status_drift_judge_calibration.py` so the
   263 completed status-aware gemma items are not re-judged.
2. Judge the remaining 7 status-aware gemma items.
3. Judge all 270 neutral items with qwen and gemma.
4. Re-run the analysis script over both directories.

Do not launch these on a low-memory machine without user confirmation.
