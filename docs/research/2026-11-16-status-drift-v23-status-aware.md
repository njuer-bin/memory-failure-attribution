# Rewrite-Matched Control — Status-Aware Writer (2026-11-16)

**Protocol:** `docs/STATUS_DRIFT_PROTOCOL_V2_3.md`
**Run:** design v3, status-aware writer, 30 trajectories, `--rewrite-matched`, seed 42.
**Judges:** qwen2.5:7b and gemma3:12b.
**Status:** completed; gates passed.

## 1. Gate metrics

- Inter-judge agreement: 364/390 = 0.933 (≥0.85).
- Deterministic proposition omission: 0/30 in every condition and depth.
- Deterministic condition omission: direct 0/10; recursive 1/10 at D3 and D5;
  rewrite-matched 0/10.
- All 3 both-wrong items manually adjudicated.

## 2. Both-correct / both-wrong

| Condition | D1 | D2 | D3 | D5 | both-wrong total |
|---|---:|---:|---:|---:|---:|
| direct | 29 | 29 | 29 | 29 | 0 |
| recursive | 29 | 27 | 25 | 26 | 1 |
| rewrite-matched | 29 | 27 | 26 | 26 | 2 |

Paired both-correct contrasts:

| Contrast | A | B | A-only | B-only |
|---|---:|---:|---:|---:|
| recursive vs rewrite-matched | 107 | 108 | 6 | 7 |
| rewrite-matched vs direct | 108 | 116 | 1 | 9 |
| recursive vs direct | 107 | 116 | 3 | 12 |

## 3. Neutral vs status-aware (same protocol)

| Metric | neutral | status-aware |
|---|---:|---:|
| direct both-correct (D1–D5 sum) | 112 | 116 |
| recursive both-correct | 82 | 107 |
| rewrite-matched both-correct | 80 | 108 |
| both-wrong total | 23 | 3 |
| chained penalty (direct − rewrite-matched) | 32 | 8 |

The status-aware prompt cuts the chaining penalty from 32 to 8 both-correct
cells and the both-wrong count from 23 to 3. It does not eliminate the effect.

## 4. Deterministic status cue (updated cases, n=10/depth)

| Condition | D5 MATCH | D5 ABSENT |
|---|---:|---:|
| direct | 10 | 0 |
| recursive | 4 | 5 |
| rewrite-matched | 4 | 4 |

Even under the status-aware prompt, chained rewriting removes the explicit
status cue in roughly half of the deep updated cases. The judges still recover
the status from remaining context in most of them, which is why the judge-level
penalty is small (8) while the cue-level penalty is large.

## 5. Both-wrong adjudication (3 items)

All three are `epistemic_02_U` (申请研究生, gold CERTAIN):

- recursive D5: `申请研究生，专注课程和事务，注意天气，整理日程。`
- rewrite-matched D3: `申请研究生，处理课程作业和日常事务，注意天气，整理日程。`
- rewrite-matched D5: `申请研究生，处理课程作业，注意天气，整理日程。`

The confirmation cue `确认` is absent; both judges return POSSIBLE. These are
writer-side status omissions, not judge errors.

## 6. P10 verdict

**Supported.** Under the status-aware writer, rewrite-matched ≈ recursive
(108 vs 107 both-correct; 7 vs 6 exclusive) and both are slightly below direct
(116). The chaining effect persists but is much smaller than under the neutral
writer. The mechanism is repeated chained rewriting, not shrinking intermediate
budgets, in both writer conditions.

## 7. Caveats

- Different run from the neutral v2.3 condition; cross-run nondeterminism is
  known (106/270 memory differences under the same seed in an earlier pair).
  The neutral-vs-status-aware comparison is between runs, so treat the
  magnitude as approximate; the within-run contrasts are the strong evidence.
- Synthetic templates; n=30; assistant adjudication.
- The deterministic cue checker is heuristic; MATCH/ABSENT is about explicit
  cue words, not semantic status.

## 8. Next

1. Repeated-seed variance (2–3 seeds) to bound the cross-run noise.
2. A status-cue-aware judge or a condition-only extraction step.
3. Read BELIEFMEM (2605.05583) and MemCoRe (2602.07885) in full before any
   novelty claim.
