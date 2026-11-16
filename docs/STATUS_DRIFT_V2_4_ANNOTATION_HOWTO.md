# How to Annotate the v2.4 Status-Drift Set

This is the practical checklist for the 120-item set in
`results/status_drift_v2_pilot/v24_full/annotation/`.

## Files

- `annotator_A.csv` — one annotator.
- `annotator_B.csv` — a second, independent annotator.
- `annotation_items.csv` — the same items without label columns; use it as a
  reference or for a third annotator.

Do not look at the other annotator's file. Do not edit `annotation_items.csv`.

## One row at a time

Each row is one trajectory × one condition × one depth. It gives you:

- `trajectory_id`, `dimension`, `target_proposition`;
- `condition` (raw / direct / recursive / rewrite_matched) and `depth`;
- `gold_final_status_from_dialogue`;
- `evidence_turn_ids`;
- `memory_text` (the output you are judging);
- `dialogue` (the full original dialogue).

Work in this order:

1. Read the **full dialogue**.
2. Find the turns listed in `evidence_turn_ids`; they establish the final status.
3. Read `memory_text`.
4. Label the fields below. Use only the dialogue as evidence.

## Labels

### proposition_identity (required)

- `PRESERVED` — the same target proposition and essential relation are
  recoverable.
- `PARTIAL` — the target is identifiable, but a material argument, relation,
  object, or scope is missing.
- `LOST` — the target proposition cannot be recovered.
- `AMBIGUOUS` — the memory supports materially different interpretations.

A keyword alone is not preservation. For conditional items, the
condition-to-action relation is part of the proposition. For intentional items,
the intention is not the action.

### polarity (required)

`POSITIVE`, `NEGATIVE`, `MIXED`, `NOT_APPLICABLE`, `UNCLEAR`.

### Status fields (required; use `NOT_APPLICABLE` when the dimension does not apply)

- `epistemic_status`: `POSSIBLE`, `PROBABLE`, `CERTAIN`, `UNKNOWN`,
  `EXPLICITLY_UNCERTAIN`, `NOT_APPLICABLE`.
- `intention_status`: `NONE`, `CONSIDERING`, `INTENDING`, `COMMITTED`,
  `EXPLICITLY_NOT_INTENDED`, `NOT_APPLICABLE`.
- `action_status`: `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `ABANDONED`,
  `CANCELLED`, `UNKNOWN`, `NOT_APPLICABLE`.
- `condition_status`: `ACTIVE_UNSATISFIED`, `ACTIVE_UNKNOWN`, `SATISFIED`,
  `INVALIDATED`, `NOT_APPLICABLE`, `UNCLEAR`.

Use only the applicable dimension for the drift decision, but fill the other
fields to avoid conflation:

- epistemic status is about certainty, not about intending to act;
- intention is not action execution;
- condition satisfaction is not inferred from whether the action is considered.

### unsupported_status_change (required)

Set `YES` only when all three hold:

1. `proposition_identity = PRESERVED`;
2. the memory's status differs from the evidence-supported final status;
3. no later dialogue evidence supports the memory's status.

Set `NO` when the status is faithful or the change is a legitimate,
evidence-supported update. Set `UNCLEAR` when identity or status cannot be
resolved.

Do **not** label omission as drift; mark `proposition_identity = LOST` and
report it separately. Do **not** count a legitimate change of mind, progress,
cancellation, or completion as drift when the dialogue supports it.

## Worked examples

1. `epistemic_00_S`, raw, gold POSSIBLE
   - memory = full dialogue (`我可能会购买电脑…目前仍然只是可能…`).
   - proposition `PRESERVED`; epistemic `POSSIBLE`; intention/action/condition
     `NOT_APPLICABLE`; unsupported `NO`.

2. `epistemic_00_U`, direct D5, gold CERTAIN
   - memory = `用户确认购买电脑，但未确定时间…`
   - `确认` preserves the proposition and the CERTAIN status. `未确定时间` is
     about timing/action, not epistemic uncertainty.
   - proposition `PRESERVED`; epistemic `CERTAIN`; unsupported `NO`.

3. `intentional_00_U`, recursive D5, gold COMMITTED
   - memory = `用户决定购电脑，按计划进行…`
   - proposition `PRESERVED`; intention `COMMITTED`; action `NOT_STARTED` or
     `NOT_APPLICABLE` (the dialogue does not say the purchase happened);
     unsupported `NO`.

4. `conditional_00_S`, direct D5, gold CONDITION_ACTIVE
   - memory = `拿不到奖学金，不考虑购买电脑。条件未满足。`
   - proposition `PRESERVED`; condition `ACTIVE_UNSATISFIED`; unsupported `NO`.
   - The judge's `SATISFIED` label for this memory is a judge error; your
     annotation is the gold here.

5. `intentional_02_U`, recursive D5, gold COMMITTED
   - memory = `用户申请研究生，推进计划，处理课程和事务。`
   - proposition `PRESERVED`; intention: `推进计划` is weaker than `决定`, so
     mark `INTENDING` (not `COMMITTED`); action `NOT_STARTED`;
     unsupported `YES` because the final evidence-supported status is
     COMMITTED and no later turn supports weakening it.
   - If you think `推进计划` is still an explicit commitment, mark `COMMITTED`
     and explain in `notes`. This is exactly the kind of disagreement the
     reliability study is meant to measure.

## After annotating

1. Keep the CSV encoding (`UTF-8` with BOM) and the row order; do not delete
   rows.
2. Fill `notes` whenever you hesitated.
3. Run the checker:

    python -m experiments.check_annotations \
        --a results/status_drift_v2_pilot/v24_full/annotation/annotator_A.csv \
        --b results/status_drift_v2_pilot/v24_full/annotation/annotator_B.csv

It reports missing/invalid values, raw agreement, and Cohen's kappa per field.
Disagreements are adjudicated only after both files are complete.
