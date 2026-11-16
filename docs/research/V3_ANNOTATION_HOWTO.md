# V3 Blind Annotation — Practical How-To

This is the operational checklist for the 60-item calibration set in
`results/status_drift_v2_pilot/v3_path_pilot_p1c/annotation/`.

## Files

- `annotator_A.csv` — one annotator.
- `annotator_B.csv` — a second, independent annotator.
- `annotation_items.csv` — same items, no label columns.
- `condition_key.csv` — **curator only. Do not open it.** It contains path,
  gold state, and condition mapping.

Do not inspect the other annotator's file. Do not edit `annotation_items.csv`.
Item order is shuffled; do not annotate all paths of one trajectory
consecutively.

## One row at a time

Each row gives you:

- `item_id` — opaque identifier;
- `target_proposition` — the action, e.g. `购买电脑`;
- `target_question` — a neutral question, e.g. "说话人对「购买电脑」的确定性状态是什么？";
- `memory_text` — the generated memory you are judging;
- `dialogue` — the full original dialogue.

Work in this order:

1. Read the full dialogue.
2. Identify the target proposition and the evidence-bearing turns.
3. Read `memory_text`.
4. Fill the fields below using only the dialogue as evidence.

## Field-by-field

### 1. `proposition_identity` (required)

- `PRESERVED` — same claim and essential arguments recoverable.
- `PARTIAL` — topic identifiable but a material argument/relation/scope is missing.
- `LOST` — target cannot be recovered.
- `AMBIGUOUS` — multiple materially different interpretations.

A keyword alone is not preservation. For conditional items, the
condition-to-action relation is part of the proposition.

### 2. Applicability fields

For each of `epistemic_applicable`, `intentional_applicable`,
`conditional_applicable`, `action_applicable`, choose:

- `APPLICABLE`
- `NOT_APPLICABLE`
- `CANNOT_DETERMINE`

### 3. Status fields

Only fill the applicable dimensions; use `NOT_APPLICABLE` otherwise.

- `epistemic_status`: `UNKNOWN`, `POSSIBLE`, `PROBABLE`, `SUPPORTED`,
  `ESTABLISHED`, `REJECTED`, `UNEXPRESSED`, `UNRECOVERABLE`, `NOT_APPLICABLE`.
- `intention_status`: `NOT_EXPRESSED`, `CONSIDERING`, `INTERESTED`, `INTENDING`,
  `COMMITTED`, `EXECUTING`, `COMPLETED`, `CANCELLED`, `NOT_INTENDED`,
  `UNRECOVERABLE`, `NOT_APPLICABLE`.
- `action_status`: `NOT_EXPRESSED`, `CONSIDERING`, `INTENDING`, `COMMITTED`,
  `EXECUTING`, `COMPLETED`, `CANCELLED`, `UNKNOWN`, `NOT_APPLICABLE`.
- `condition_status`: `UNKNOWN`, `ACTIVE_UNSATISFIED`, `SATISFIED`, `FAILED`,
  `WAIVED`, `NOT_APPLICABLE`, `UNRECOVERABLE`.

Critical distinctions:

- `我可能会` is not `我确定`.
- `我想去` is not `我已决定去`.
- A satisfied condition does not imply commitment or execution of the action.
- `已决定，但时间未定` is still COMMITTED with unresolved timing.
- A later explicit cancellation supersedes an earlier commitment.

### 4. `evidence_support` (required)

- `SUPPORTED_BY_DIALOGUE`
- `CONTRADICTED_BY_LATER_DIALOGUE`
- `NOT_SUPPORTED`
- `AMBIGUOUS`
- `NOT_ASSESSABLE`

### 5. `primary_judgment` (required)

Use this decision order:

1. `PROPOSITION_LOSS` — identity is LOST (or materially PARTIAL).
2. `STATUS_OMISSION` — identity preserved, but the status is absent or not
   recoverable; no conflicting state is asserted.
3. `LEGITIMATE_UPDATE` — the memory reflects a later evidence-supported change.
4. `UNSUPPORTED_STATUS_DISTORTION` — identity preserved, a different status is
   asserted, and no later dialogue supports it.
5. `NO_DISTORTION` — status is faithful.
6. `AMBIGUOUS_UNASSESSABLE` — cannot decide from the memory and dialogue.

Omission is not drift. A shorter paraphrase is not automatically distortion.

### 6. `subtype` (optional but encouraged for drift)

`ESCALATION`, `ATTENUATION`, `COMMITMENT_INFLATION`,
`COMMITMENT_DEFLATION`, `CONDITIONAL_COLLAPSE`, `POLARITY_SCOPE`,
`TEMPORAL`, `NONE`.

### 7. `rationale`, `confidence`, `turn_references`

- `rationale`: one or two sentences.
- `confidence`: `HIGH`, `MEDIUM`, `LOW`.
- `turn_references`: dialogue turn IDs or a short quote.

## Worked examples

1. Memory `确认去上海工作…` against a dialogue that explicitly confirms:
   proposition `PRESERVED`; epistemic `ESTABLISHED` or `SUPPORTED`; primary
   `NO_DISTORTION`.

2. Memory `上海工作，天气多变…` against a dialogue that explicitly confirms:
   proposition `PRESERVED`; epistemic `UNEXPRESSED` or `UNRECOVERABLE`;
   primary `STATUS_OMISSION` (not `UNSUPPORTED_STATUS_DISTORTION`).

3. Memory `用户申请研究生，推进计划…` against a dialogue that says
   `我已经决定…`: proposition `PRESERVED`; intention `INTENDING` rather than
   `COMMITTED`; primary `UNSUPPORTED_STATUS_DISTORTION`, subtype
   `COMMITMENT_DEFLATION`.

4. Memory `开始学日语` against a dialogue that only commits to start:
   proposition `PRESERVED`; intention `COMMITTED`; action `EXECUTING` (if the
   memory asserts it); primary `UNSUPPORTED_STATUS_DISTORTION`, subtype
   `TEMPORAL` or `COMMITMENT_INFLATION`.

5. Memory `已拿到奖学金，条件满足` against a dialogue that says the condition is
   met but the action is only being considered: condition `SATISFIED`;
   intention `CONSIDERING`; primary `NO_DISTORTION`.

## After annotating

Keep UTF-8, do not delete rows, fill `rationale` when unsure. Then run:

```
python -m experiments.check_v3_annotations \
  --a .../annotator_A.csv --b .../annotator_B.csv
```

The checker reports missing/invalid values, raw agreement, and Cohen's kappa
per field. Disagreements are adjudicated only after both files are complete.

This is a 60-item calibration set. Freeze the guide and ontology before the
confirmatory annotation set.
