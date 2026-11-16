# Status Drift v3 — 30-Trajectory Run (2026-11-16)

**Protocol:** v2.1 design + v2.2 conditional fix.
**Run:** `--design v3 --limit 30`, seed 42. 30 trajectories = 3 dimensions ×
5 topics × 2 variants (stable S / updated U).
**Writers:** `status_aware` and `neutral`.
**Judges:** qwen2.5:7b and gemma3:12b, two-step prompt.
**Status:** completed; main result.

## 1. Gate metrics

| Metric | status-aware | neutral | Gate |
|---|---:|---:|---|
| Inter-judge agreement | 257/270 = 0.952 | 244/270 = 0.904 | ≥0.85 PASS |
| Epistemic agreement | 0.922 | 0.933 | ≥0.80 PASS |
| Intentional agreement | 1.000 | 0.944 | ≥0.80 PASS |
| Conditional agreement | 0.933 | 0.833 | ≥0.80 PASS |
| Deterministic proposition omission | 0/270 = 0.000 | 3/270 = 0.011 | <10% PASS |
| Deterministic condition omission | 2/90 = 0.022 | 10/90 = 0.111 | <10% (neutral 11.1% narrowly above) |
| Condition ambiguous | 9/90 | 5/90 | reported |
| Deterministic condition wrong label | 0/90 | 0/90 | PASS |
| Both-judges-wrong items | 1 | 23 | — |
| Both-judges-correct items | 256 | 221 | — |

The neutral conditional omission rate is 11.1%, 1.1 points above the smoke
threshold. This is a substantive signal (condition status lost under recursive
compression), not a pipeline failure; it is reported explicitly rather than
excluded.

## 2. Main result

The writer prompt is the dominant factor.

- **status-aware writer:** 256/270 condition-items are judged correctly by both
  judges; there is exactly **1** both-judge error.
- **neutral writer:** 221/270 both-correct and **23** both-wrong.
- Pairwise over the 270 common items: status-aware is both-correct and neutral
  is not on **43** items; the reverse holds on **8** items.

Directional hypothesis verdicts:

- **H1 (strategies differ): supported.** The status-aware vs neutral contrast is
  large and consistent across dimensions.
- **H2 (recursion adds drift): supported under the neutral writer, not under the
  status-aware writer.** Neutral errors concentrate at recursive D2–D5;
  status-aware has one D5 error.
- **H3 (proposition retention ≠ status retention): supported.** Neutral
  deterministic proposition omission is 1.1%, while 23 condition-items have a
  status error agreed by both judges.
- **H4 (downstream behavior): untested.**

## 3. Manual adjudication of both-judge errors

### status-aware (1 item)

- `epistemic_02_U | recursive_d5`: gold CERTAIN. Memory:
  `申请研究生；当前日期和天气不确定；专注课程和日常事务。`
  The confirmation cue is gone. Real writer-side cue loss at D5.

### neutral (23 items)

Most are writer-side status-cue loss or weakening. Examples:

- `epistemic_01_U | recursive_d5`: `上海工作，因天气改日程…` — no confirmation cue.
- `epistemic_04_U | recursive_d2/d3/d5`: `学习日语…` — confirmation cue absent
  from D2 onward.
- `intentional_00_U | recursive_d3/d5`: `买电脑用于课程作业和日常…` — commitment
  cue gone.
- `intentional_01_U | recursive_d3/d5`: `上海工作，留意天气…` — commitment cue gone.
- `intentional_04_U | recursive_d2/d3/d5`: `学习日语…` — commitment cue gone.
- `intentional_00_U | direct_d5`: `购买电脑决定中…` — `决定` weakened to `决定中`.
- `conditional_00_U | recursive_d2`: `奖学金后买电脑…` — the satisfied condition
  became a conditional plan.

A minority are judge-side errors rather than writer drift:

- `epistemic_03_U | recursive_d5`: memory says `确认数学建模`, but both judges
  return POSSIBLE. The confirmation is explicit; this is a judge error.
- `conditional_03_U | recursive_d5`: memory says `获奖学金`, but both judges
  return CONDITION_ACTIVE. The condition is satisfied; this is a judge error.
- `conditional_01_U` and `conditional_02_U`: memories say `奖学金在手` (condition
  satisfied) but also `上海工作待定` (action pending); both judges read the action
  and return ACTIVE. The condition itself is satisfied. This is residual
  ontology confusion despite the v2.2 fix.

The both-judge-error count therefore overstates pure writer drift by roughly
6 items in the neutral condition. The qualitative contrast still holds: the
neutral writer loses status cues far more often.

## 4. Conditional dimension caveat

The v2.2 fix removed the explicit action clause from the corpus, but the
neutral writer sometimes reintroduces an action clause (`上海工作待定`) or
paraphrases the condition (`奖学金在手`, `获奖学金`) in ways the judges still
misread. Conditional results are directionally consistent but less reliable
than epistemic and intentional.

## 5. Limitations

- Two local models; writer and judge overlap (qwen is both a writer and a judge
  in one condition). Cross-model bias remains.
- Direct and recursive conditions are not matched on number of rewrites; the
  contrast mixes recursion with repeated editing.
- Synthetic templates; no human annotation.
- n=30 is a pilot, not a benchmark; no significance claims.
- The neutral conditional omission gate narrowly fails (11.1% vs 10%).

## 6. Next steps

1. Manually adjudicate the 39 judge disagreements (13 status-aware, 26 neutral)
   before any external claim.
2. Add a rewrite-matched control to separate recursion from repeated editing.
3. Consider a third judge or a human spot-check for the conditional dimension.
4. Only then consider expanding topics or moving to natural dialogue.
5. Read BELIEFMEM (2605.05583) and MemCoRe (2602.07885) in full before any
   novelty claim.
