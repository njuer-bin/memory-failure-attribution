# v2.1 neutral-writer smoke — manual adjudication (2026-11-16)

**Run:** `--design v2 --limit 12 --writer-style neutral --skip-judge`, seed 42.
**Judges:** qwen2.5:7b (A), gemma3:12b (B).
**Status:** local analysis only; not committed per "only successful experiments".

## Gate metrics

- Inter-judge agreement: 96/108 = 0.889 (epistemic 0.917, intentional 0.944,
  conditional 0.806).
- Deterministic omission: 0.0 in every condition.
- Direct conditions: A 11/12, B 10/12, stable across depths.
- Recursive conditions degrade at depth:
  - A: d2 8/12, d3 7/12, d5 9/12.
  - B: d2 9/12, d3 6/12, d5 6/12.
- Raw: 12/12 for both.

## Manual adjudication of updated cases

### epistemic_00_U (gold CERTAIN, 购买电脑)

- direct d2/d3/d5: `确认购电脑` -> CERTAIN. Both judges correct.
- recursive d2: `计划购电脑` -> confirmation became a plan (drift). B correct
  (POSSIBLE); A over-credits CERTAIN.
- recursive d3: `购电脑处理作业事务` -> status cue absent.
- recursive d5: `购电脑处理事务` -> status cue absent.

### epistemic_01_U (gold CERTAIN, 去上海工作)

- direct d2/d3/d5: `确认去上海工作` -> CERTAIN. Correct.
- recursive d2: `确认去上海工作` -> CERTAIN. Correct.
- recursive d3: `去上海工作...` -> cue dropped; both judges POSSIBLE.
- recursive d5: `上海工作...` -> cue dropped; both judges POSSIBLE.

### intentional_00_U (gold COMMITTED, 购买电脑)

- direct d2/d3/d5: `已决定推进` -> COMMITTED. Correct.
- recursive d2: `买电脑推进中` -> cue weakened; A CONSIDERING, B COMMITTED.
- recursive d3/d5: `买电脑用于课程作业和日常` -> commitment cue gone; both
  judges CONSIDERING. Note the writer also merges the proposition with the
  coursework distractor ("买电脑用于课程作业"), a semantic distortion.

### intentional_01_U (gold COMMITTED, 去上海工作)

- direct d2/d3/d5: `决定去上海工作` -> COMMITTED. Correct.
- recursive d2: `去上海工作...` -> cue dropped; A CONSIDERING, B COMMITTED.
- recursive d3/d5: `上海工作...` -> cue dropped; both judges CONSIDERING.

### conditional_00_U (gold CONDITION_SATISFIED, 购买电脑)

- direct d2/d3/d5: `已获奖学金，开始考虑买电脑` -> condition satisfied.
  A correct; B says ACTIVE (ignores `已获奖学金`).
- recursive d2/d3: `获奖学金，考虑买电脑` -> condition still satisfied in text,
  but **both** judges say ACTIVE.
- recursive d5: `获奖金买电脑` -> garbled; A SATISFIED, B ACTIVE.

### conditional_01_U (gold CONDITION_SATISFIED, 去上海工作)

- direct d2/d3/d5: `已获奖学金，将考虑去上海工作` -> condition satisfied.
  **Both** judges say ACTIVE because they read `将考虑` as the action status.
- recursive d2-d3: same pattern.
- recursive d5: A SATISFIED, B ACTIVE.

## Findings (local, pending full run)

1. **Recursive status-cue loss is real for epistemic and intentional.**
   Direct compression preserves `确认` / `决定` at every depth. Recursive
   compression preserves them through D2 in one case and then drops them at
   D3/D5 in both topics. The proposition keyword remains present in every
   memory, so this is content-preserved status distortion (H3), not omission.
2. **The effect is depth-dependent, not monotone.** D2 is mixed; the clear
   loss is at D3 and D5. With only two topics per dimension this is a
   candidate pattern, not a measured threshold.
3. **Conditional is invalid under the current ontology.** The label asks about
   condition satisfaction, but the final turn also states action status
   (`开始考虑`). Both judges read the action status and label the condition
   ACTIVE even when `已获奖学金` is present. This is not writer drift; it is a
   label-definition failure. Conditional results must be discarded and the
   design revised.
4. **Judge leniency differs by cue presence.** qwen over-credits CERTAIN /
   COMMITTED when the memory has no cue; gemma is stricter on epistemic but
   fails conditional. Neither judge is uniformly correct; manual adjudication
   is required.

## Decision

- Do not scale to 30 with this conditional operationalization.
- Wait for the status-aware writer run to finish; compare whether the explicit
  preservation instruction stops the D3/D5 cue loss.
- Before any 30-trajectory run: fix conditional (state only the condition, not
  the action), and add a control matched on number of rewrites.

## Limitations

- Neutral writer only; status-aware not yet analyzed.
- Two topics per dimension; no statistical claim.
- Direct control is not matched on number of rewrites, so recursion vs repeated
  rewriting is not fully separated.
- Assistant adjudication, not human annotation.
