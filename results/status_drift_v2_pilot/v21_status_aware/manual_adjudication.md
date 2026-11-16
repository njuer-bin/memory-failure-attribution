# v2.1 status-aware writer smoke + neutral comparison (2026-11-16)

**Run:** `--design v2 --limit 12 --writer-style status_aware --skip-judge`, seed 42.
**Judges:** qwen2.5:7b (A), gemma3:12b (B).
**Status:** local analysis only; not committed.

## Gate metrics

- Inter-judge agreement: 77/108 = 0.713 overall.
  - epistemic 32/36 = 0.889
  - intentional 36/36 = 1.000
  - conditional 9/36 = 0.250
- Deterministic omission: 0.0 in every condition.
- Accuracy by depth (A qwen / B gemma):
  - direct d1 1.000 / 0.833; d2-d5 0.917 / 0.833
  - recursive d1 0.833 / 0.833; d2 0.750 / 0.833; d3 0.667 / 0.833; d5 0.750 / 0.833

The overall agreement gate fails only because of the conditional dimension.
Epistemic and intentional both pass 0.85.

## Manual adjudication of updated cases

### epistemic_00_U (gold CERTAIN)

- direct and recursive d2/d3/d5 all contain `确认购买电脑`.
- Both judges return CERTAIN at every depth.
- **No writer-side cue loss.**

### epistemic_01_U (gold CERTAIN)

- direct and recursive d2/d3/d5 all contain `确认去上海工作`.
- Recursive d2/d3 add `考虑不确定性`; qwen downgrades to POSSIBLE, gemma keeps
  CERTAIN. Manual reading: the confirmation is explicit; the extra clause refers
  to earlier uncertainty. This is a **judge** ambiguity, not writer drift.
- recursive d5: both CERTAIN.

### intentional_00_U (gold COMMITTED)

- direct and recursive d2/d3/d5 all contain `决定购买电脑`.
- Both judges return COMMITTED at every depth.
- **No writer-side cue loss.**

### intentional_01_U (gold COMMITTED)

- direct and recursive d2/d3/d5 all contain `决定去上海工作`.
- Both judges return COMMITTED at every depth.
- **No writer-side cue loss.**

### conditional_00_U / conditional_01_U (gold CONDITION_SATISFIED)

- Memories contain `已拿到奖学金` / `已获奖学金` at every depth.
- qwen returns CONDITION_SATISFIED (correct); gemma returns CONDITION_ACTIVE
  (wrong) at every depth.
- This is the same label-ontology failure as in the neutral run. Conditional is
  invalid under the current dialogue template.

## Neutral vs status-aware comparison

| Dimension | Neutral recursive D3 | Status-aware recursive D3 |
|---|---|---|
| epistemic (A/B) | 0.58 / 0.50 | 0.67 / 0.83 |
| intentional (A/B) | 0.58 / 0.50 | 0.67 / 0.83 |
| Manual claim | cues `确认`/`决定` dropped | cues preserved |

Manual memory reading is decisive: under the neutral writer, recursive D3/D5
memories become `购电脑…`, `上海工作…`, `买电脑用于课程作业…`; under the
status-aware writer they keep `确认…` / `决定…`.

## Findings (local, pending commit decision)

1. **P1 supported:** the neutral writer preserves status less often than the
   status-aware writer.
2. **H2 negative under a status-preserving writer:** recursion alone does not
   add status drift when the prompt explicitly requires status preservation.
3. **H3 supported for the neutral writer:** the proposition keyword remains
   present while the status cue disappears at D3/D5.
4. **Conditional is invalid** because the final turn states both condition
   satisfaction and action status. Both judges read the action status. This is
   a label/dataset defect, not drift.
5. **Judge caveat:** qwen downgrades explicit confirmations when a stale
   `考虑不确定性` clause is present; gemma ignores `已获奖学金`. Neither judge
   is uniformly correct.

## Decision

- Do **not** run the 30-trajectory mixed pilot on this conditional template.
- Fix conditional (protocol v2.2): the final turn states only whether the
  condition is satisfied; no action-status clause. Add a conditional-specific
  judge instruction.
- Re-validate conditional on a small smoke before any 30 run.
- The epistemic/intentional v2.1 result is a clean, manually verified candidate
  finding, but it will not be committed until the conditional defect is fixed
  and the combined experiment passes its gates (per "only successful
  experiments").

## Limitations

- Two topics per dimension; no statistical claim.
- Direct control is not matched on number of rewrites.
- Assistant adjudication, not human annotation.
