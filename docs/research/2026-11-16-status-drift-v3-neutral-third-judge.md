# Third-Judge Triangulation — v3 Neutral Writer (2026-11-16)

**Run:** `v3_neutral` (30 trajectories), three judges: qwen2.5:7b, gemma3:12b,
mistral:7b.
**Scope:** 270 condition-items.

## 1. Agreement

| Pair | Agreement |
|---|---:|
| qwen vs gemma | 244/270 = 0.904 |
| qwen vs mistral | 229/270 = 0.848 |
| gemma vs mistral | 233/270 = 0.863 |

Majority correct: **232/270 = 0.859**.

## 2. The central result

**All 23 items that qwen and gemma both judged wrong are also judged wrong by
mistral.** The all-three-wrong set is exactly the previous both-wrong set; no
item is rescued by the third judge.

By dimension:

| Dimension | all-three-wrong |
|---|---:|
| conditional | 6 |
| epistemic | 5 |
| intentional | 12 |

Examples (memory text from the manual adjudication):

- `intentional_04_U | recursive_d2/d3/d5`: `学习日语…` — commitment cue gone.
- `epistemic_04_U | recursive_d2/d3/d5`: `学习日语…` — confirmation cue gone.
- `intentional_00_U | recursive_d3/d5`: `买电脑用于课程作业和日常…`.
- `conditional_01_U | recursive_d2/d3/d5`: `奖学金在手，上海工作待定…` —
  condition satisfied but the action clause dominates; all three judges return
  ACTIVE.

These are status-cue omissions or weakenings, not explicit inversions.

## 3. Majority-wrong (38)

The 38 majority-wrong items are the 23 all-three-wrong items plus 15 items where
exactly two judges are wrong and one is right. The 15 are judge-specific
near-ties, not writer drift:

- `epistemic_00_U | recursive_d2/d3/d5`: qwen CERTAIN, gemma+mistral POSSIBLE.
- `epistemic_03_U | recursive_d2/d3`: gemma CERTAIN, qwen+mistral POSSIBLE.
- `intentional_01_U | recursive_d2`: gemma COMMITTED, qwen+mistral CONSIDERING.
- `intentional_03_U | recursive_d2`: same pattern.
- `intentional_04_S | recursive_d3`: qwen CONSIDERING, gemma+mistral COMMITTED.
- `conditional_00_U | recursive_d3/d5`: qwen SATISFIED, gemma+mistral ACTIVE.
- `conditional_03_U | direct/recursive d1–d3`: qwen SATISFIED, gemma+mistral
  ACTIVE.

## 4. Status-aware comparison

| Metric | neutral | status-aware |
|---|---:|---:|
| all-three-wrong | **23** | **1** |
| majority-wrong | 38 | 10 |
| majority correct | 232/270 | 260/270 |

The mitigation effect is robust to a third judge: 23 → 1 all-three-wrong.

## 5. Interpretation

- The neutral writer's errors are **not** a qwen/gemma artifact. A third,
  independently prompted model reproduces all 23.
- The status-aware result is likewise robust: exactly one all-three-wrong item,
  a real writer cue loss.
- Majority voting still leaves judge-specific near-tie errors; it does not
  replace deterministic checks and manual adjudication.
- The headline is now three-judge-supported: neutral chained compression loses
  status cues in 23/270 condition-items; the status-aware prompt reduces that
  to 1/270.

## 6. Caveats

- Three local model families, not human annotators.
- The 23 all-three-wrong items were manually read earlier; most are cue
  omissions, not inversions.
- Synthetic templates; n=30.
