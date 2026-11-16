# Judge Disagreement Adjudication — v3 30-Run (2026-11-16)

**Scope:** all 39 condition-items where qwen2.5:7b and gemma3:12b returned
different statuses in the v3 30-trajectory run.
**Method:** read the memory text, the gold status, and both labels. Classify as
qwen correct, gemma correct, or both wrong/undecidable. This is assistant
adjudication, not human annotation.

## Summary

| Writer | Disagreements | qwen correct | gemma correct | both wrong/undecidable |
|---|---:|---:|---:|---:|
| status-aware | 13 | 2 | 9 | 2 |
| neutral | 26 | 13 | 8 | 5 |
| total | 39 | 15 | 17 | 7 |

No judge is uniformly reliable. The better judge flips with the writer style.

## Status-aware (13)

### gemma correct (9)

- `epistemic_00_U` direct d1/d2/d3: `确认会购买电脑，但未确定时间`.
  qwen downgrades because of `未确定时间` (timing, not the proposition).
- `epistemic_01_U` recursive d2/d3: `确认去上海工作，考虑不确定性`.
  qwen downgrades because of the stale-uncertainty clause.
- `conditional_02_S` recursive d2/d3/d5: `无奖学金，未申请研究生`.
  qwen says SATISFIED; gemma correctly says ACTIVE.
- `conditional_03_U` direct d5: `拿到奖学金，考虑参加数学建模比赛`.
  qwen says ACTIVE; gemma correctly says SATISFIED.

### qwen correct (2)

- `epistemic_04_U` recursive d2/d3: `确认开始学习日语，但尚未开始`.
  gemma downgrades because of `尚未开始` (action not started, not
  unconfirmed). qwen keeps CERTAIN.

### both wrong (2)

- `conditional_01_U` recursive d3/d5: `将去上海工作。` / `去上海工作。`
  The condition is absent. qwen guesses SATISFIED (gold), gemma guesses ACTIVE.
  Neither reports the omission. These are the two deterministic condition
  omissions.

## Neutral (26)

### gemma correct (8)

- `conditional_00_S` recursive d3/d5: `奖学金未发先不买电脑`.
  qwen says SATISFIED; gemma correctly says ACTIVE.
- `epistemic_00_U` recursive d2: `计划购电脑` (confirmation became a plan).
  gemma POSSIBLE; qwen over-credits CERTAIN.
- `epistemic_01_U` recursive d3: `确认上海工作`.
- `epistemic_03_U` recursive d2/d3: `确认数学建模比赛`.
- `intentional_00_U` recursive d2: `买电脑推进中`.
- `intentional_03_U` recursive d2: `参加数学建模比赛，推进计划`.

### qwen correct (13)

- `conditional_03_U` direct d1-d5 and recursive d1-d3:
  `已获奖学金，考虑参加数学建模比赛`. gemma reads the action clause and says
  ACTIVE; qwen correctly says SATISFIED.
- `conditional_04_U` direct d2/d3/d5: `已获奖学金，将开始学习日语`.
- `conditional_04_U` recursive d3: `…已达标`.
- `intentional_04_S` recursive d3/d5: `日语学习中…` / `今日完成日语作业`.
  gemma over-credits COMMITTED; qwen keeps CONSIDERING.

This is the mirror image of the status-aware result: gemma systematically fails
on condition-satisfied cases, while qwen systematically downgrades explicit
confirmations that carry a trailing qualifier.

### both wrong / undecidable (5)

- `conditional_00_U` recursive d3: `奖学金买电脑…` — condition not stated.
- `conditional_00_U` recursive d5: `奖学金买机…` — condition and proposition
  both degraded.
- `epistemic_00_U` recursive d3/d5: `购电脑处理作业事务` — status cue absent.
- `intentional_01_U` recursive d2: `去上海工作…` — commitment cue absent.

Both judges pick a label from priors because the writer removed the status.
These are writer omissions, not judge misreadings.

## Consequences

1. **The 23 neutral both-wrong items are not all writer drift.** About 6 are
   judge errors (mainly gemma on `已获奖学金`). The real writer-drift count is
   lower but still substantial.
2. **The 7 both-wrong disagreements are writer omissions.** They strengthen H3:
   the proposition survives while the status cue disappears, and both judges
   guess.
3. **A single judge is not a valid instrument.** Status-aware favors gemma;
   neutral favors qwen. Report both and the deterministic checks.
4. **Conditional remains judge-limited.** `已获奖学金` is still read as ACTIVE by
   gemma, even after the v2.2 template fix. A condition-only extraction step or
   a third judge is needed before external claims.
5. **Deterministic checks are necessary.** They catch the 7 both-wrong
   disagreements that judge accuracy alone would misclassify.

## Limitations

- Assistant adjudication, not human annotation.
- Gold labels are synthetic-template labels.
- No rewrite-matched control yet.
