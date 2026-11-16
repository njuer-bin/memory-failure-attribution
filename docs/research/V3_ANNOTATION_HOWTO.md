# V3 v3.1 Blind Annotation — Practical How-To

This is the operational checklist for the **v3.1 collapsed-ontology calibration
set**.

## Files

- `annotator_A.csv` — one annotator.
- `annotator_B.csv` — a second, independent annotator.
- `annotation_items.csv` — same items, no labels.
- The condition key is stored **outside the repository**; do not open it.

Do not inspect the other annotator's file. Item order is shuffled; do not
annotate all paths of one trajectory consecutively.

## One row at a time

Each row gives you:

- `item_id` — opaque identifier;
- `target_proposition` — the action, e.g. `购买电脑`;
- `target_question` — neutral, does not reveal dimension or gold;
- `memory_text` — the memory you are judging;
- `dialogue` — the full original dialogue.

Work in this order:

1. Read the full dialogue.
2. Read `memory_text`.
3. Fill the fields below using only the dialogue as evidence.

## Fields

### 1. `proposition_identity` (required)

`PRESERVED` / `PARTIAL` / `LOST` / `AMBIGUOUS`.

A keyword alone is not preservation. For conditional items, the
condition-to-action relation is part of the proposition.

### 2. `primary_dimension` (required)

Choose exactly one:

- `EPISTEMIC` — whether something is true, confirmed, or uncertain.
- `INTENTIONAL` — the speaker's commitment to a future action.
- `CONDITIONAL` — whether a prerequisite is met; action state is separate.
- `ACTION` — execution progress of an already-committed action.
- `CANNOT_DETERMINE`.

If two seem applicable, choose the one the dialogue's update turns are about and
explain the other in `rationale`.

### 3. `status_expressed` (required)

- `YES` — the memory expresses a status for the primary dimension.
- `NO` — no status is expressed or recoverable.
- `UNCLEAR` — ambiguous.

### 4. `expressed_status`

Use only the labels for your chosen primary dimension:

- EPISTEMIC: `POSSIBLE`, `ESTABLISHED`, `UNKNOWN`
- INTENTIONAL: `CONSIDERING`, `COMMITTED`, `UNKNOWN`
- CONDITIONAL: `CONDITION_ACTIVE`, `CONDITION_SATISFIED`, `UNKNOWN`
- ACTION: `ACTION_NOT_STARTED`, `ACTION_STARTED`, `UNKNOWN`
- all: `NOT_EXPRESSED`, `UNRECOVERABLE`

### 5. `evidence_support`

`SUPPORTED_BY_DIALOGUE` / `CONTRADICTED_BY_LATER_DIALOGUE` / `NOT_SUPPORTED` /
`AMBIGUOUS` / `NOT_ASSESSABLE`.

### 6. `primary_judgment` (required)

Apply the two-step order:

1. `PROPOSITION_LOSS` — identity is LOST (or materially PARTIAL).
2. `STATUS_OMISSION` — identity preserved, but no status expressed or
   recoverable; no conflicting state asserted.
3. `NO_DISTORTION` — the expressed status matches the evidence-supported final
   state. A memory that simply states the final state belongs here.
4. `LEGITIMATE_UPDATE` — the dialogue contains a later supported change and the
   memory represents that change **as a change** (e.g., "was considering, now
   decided").
5. `UNSUPPORTED_STATUS_DISTORTION` — a different status is asserted and no later
   dialogue supports it.
6. `AMBIGUOUS_UNASSESSABLE` — cannot decide.

### 7. `subtype`, `rationale`, `confidence`, `turn_references`

- subtype: `ESCALATION`, `ATTENUATION`, `COMMITMENT_INFLATION`,
  `COMMITMENT_DEFLATION`, `CONDITIONAL_COLLAPSE`, `POLARITY_SCOPE`,
  `TEMPORAL`, `NONE`.
- confidence: `HIGH`, `MEDIUM`, `LOW`.
- turn_references: turn IDs or a short quote.

## Critical distinctions

- `我可能会` ≠ `我确定`; `我想去` ≠ `我已决定去`.
- A satisfied condition does not prove commitment or execution.
- `已决定，但时间未定` is still COMMITTED with unresolved timing.
- A later explicit cancellation supersedes an earlier commitment.
- **Omission is not distortion**: missing a status cue is `STATUS_OMISSION`
  unless the memory asserts a different state.
- **A memory that states the final state is `NO_DISTORTION`**, not
  `LEGITIMATE_UPDATE`. The latter requires the memory to represent the change as
  a change.
- A shorter paraphrase is not automatically distortion.

## Worked examples

1. Memory `确认去上海工作…` vs a dialogue that explicitly confirms:
   `PRESERVED`, `EPISTEMIC`, `YES`, `ESTABLISHED`, `SUPPORTED_BY_DIALOGUE`,
   `NO_DISTORTION`.

2. Memory `上海工作，天气多变…` vs a dialogue that explicitly confirms:
   `PRESERVED`, `EPISTEMIC`, `NO`, `NOT_EXPRESSED`, `NOT_ASSESSABLE`,
   `STATUS_OMISSION` (not unsupported distortion).

3. Memory `用户申请研究生，推进计划…` vs `我已经决定…`:
   `PRESERVED`, `INTENTIONAL`, `YES`, `CONSIDERING` or `UNKNOWN`,
   `NOT_SUPPORTED`, `UNSUPPORTED_STATUS_DISTORTION`, subtype
   `COMMITMENT_DEFLATION`.

4. Memory `开始学日语` vs a dialogue that only commits to start:
   `PRESERVED`, `ACTION`, `YES`, `ACTION_STARTED`, `NOT_SUPPORTED`,
   `UNSUPPORTED_STATUS_DISTORTION`, subtype `TEMPORAL`.

5. Memory `已拿到奖学金，条件满足` vs a dialogue where the condition is met but
   the action is only considered:
   `PRESERVED`, `CONDITIONAL`, `YES`, `CONDITION_SATISFIED`,
   `SUPPORTED_BY_DIALOGUE`, `NO_DISTORTION`.

## After annotating

Keep UTF-8, do not delete rows, fill `rationale` when unsure. Then run:

```
python -m experiments.check_v3_annotations \
  --a .../annotator_A.csv --b .../annotator_B.csv
```

The checker validates labels and dimension/status compatibility, then reports
raw agreement and Cohen's kappa per field. Disagreements are adjudicated only
after both files are complete.

This is the v3.1 calibration set. Freeze the guide and ontology before the
confirmatory annotation set.
