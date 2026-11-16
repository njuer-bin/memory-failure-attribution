# Third-Judge Triangulation — v3 Status-Aware (2026-11-16)

**Run:** `v3_status_aware` (30 trajectories), three judges:
qwen2.5:7b, gemma3:12b, mistral:7b.
**Scope:** 270 condition-items, majority vote and all-three-wrong analysis.

## 1. Agreement

| Pair | Agreement |
|---|---:|
| qwen vs gemma | 257/270 = 0.952 |
| qwen vs mistral | 248/270 = 0.919 |
| gemma vs mistral | 251/270 = 0.930 |

Majority correct: **260/270 = 0.963**.

## 2. All-three-wrong

Exactly **1** item:

- `epistemic_02_U | recursive_d5`: gold CERTAIN; all three judges return
  POSSIBLE. Memory: `申请研究生；当前日期和天气不确定；专注课程和日常事务。`
  The confirmation cue is absent. This is the same writer-side cue loss found
  earlier; a third judge confirms it is not a qwen/gemma artifact.

## 3. Majority-wrong (10 items)

Classified by manual reading:

**Writer-side omissions (3)**

- `conditional_01_U | recursive_d3/d5`: condition absent; majority guesses
  ACTIVE. These are the two deterministic condition omissions.
- `epistemic_02_U | recursive_d5`: the all-three-wrong cue loss above.

**Judge errors (7)**

- `epistemic_00_U | direct_d1/d2/d3`: memory says `确认会购买电脑，但未确定时间`.
  gemma correctly returns CERTAIN; qwen and mistral downgrade because of
  `未确定时间` (timing, not status).
- `epistemic_01_U | recursive_d3`: `确认去上海工作，考虑不确定性`.
  gemma CERTAIN; qwen and mistral downgrade on the stale-uncertainty clause.
- `epistemic_04_U | recursive_d2/d3`: `确认开始学习日语，但尚未开始`.
  qwen CERTAIN; gemma and mistral downgrade on `尚未开始` (action not started).
- `conditional_03_U | direct_d5`: `拿到奖学金，考虑参加数学建模比赛`.
  gemma SATISFIED; qwen and mistral return ACTIVE.

## 4. Interpretation

- The status-aware 30-run is robust to a third judge: only one item is wrong
  under all three judges, and it is a genuine writer-side cue loss.
- Majority voting does **not** eliminate judge-specific errors. Two judges can
  share the same failure mode:
  - qwen + mistral downgrade explicit confirmations with a trailing qualifier;
  - gemma + mistral read condition satisfaction through the action clause.
- The deterministic status-cue checker and manual adjudication are still
  necessary; a third judge reduces but does not remove judge error.
- The adjusted status-aware writer-drift count remains 1 per 30 trajectories
  (plus 2 deterministic condition omissions).

## 5. Caveats

- Three local models, not human annotators.
- Majority-wrong classification is assistant adjudication.
- Only the status-aware run has a third judge; the neutral 23 both-wrong items
  have not yet been triangulated.
