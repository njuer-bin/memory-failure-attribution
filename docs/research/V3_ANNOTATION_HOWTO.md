# V3 Blind Annotation — Practical How-To (v3.2)

This is the operational checklist for the **v3.2 conditional calibration set**
(`annotation_v32/`).

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

The proposition unit is the target predicate plus its essential arguments.
Modality, condition relation, and status are **not** part of identity. For a
conditional trajectory the target is the action (e.g. `购买电脑`), not the whole
"if condition, then action" sentence.

A keyword or topic label alone is not preservation. If the target predicate is
absent (`电脑调整` for `购买电脑`; `上海工作多` for `去上海工作`), record
`PARTIAL`.

### 2. `primary_dimension` (required)

Choose exactly one:

- `EPISTEMIC` — whether something is true, confirmed, or uncertain.
- `INTENTIONAL` — the speaker's commitment to a future action.
- `CONDITIONAL` — whether a prerequisite is met; action state is separate and
  is scored only if the memory explicitly asserts it.
- `ACTION` — execution progress of an already-committed action.
- `CANNOT_DETERMINE` — both readings are incompatible; no dimension selectable.

If two seem applicable, choose the one the dialogue's update turns are about and
explain the other in `rationale`. For a conditional trajectory choose
`CONDITIONAL` even when an action verb appears.

### 3. `status_expressed` (required)

A status is expressed only with an **explicit lexical cue**. An unmarked action
verb does not assert an action state; a bare topic noun does not assert a
condition state.

- `YES` — an explicit cue expresses a status for the primary dimension.
- `NO` — no explicit cue.
- `UNCLEAR` — the cue supports two incompatible states.

Explicit cues include `可能`/`不能确定`, `确认`/`已确定`, `考虑`/`打算`,
`决定`/`已承诺`, `未拿到`/`未满足`, `已拿到`/`条件满足`. Juxtaposition such as
`奖学金购机` is not a cue for either condition satisfied or action commitment.

### 4. `expressed_status`

Use only the labels for your chosen primary dimension:

- EPISTEMIC: `POSSIBLE`, `ESTABLISHED`, `UNKNOWN`
- INTENTIONAL: `CONSIDERING`, `COMMITTED`, `UNKNOWN`
- CONDITIONAL: `CONDITION_ACTIVE`, `CONDITION_SATISFIED`, `UNKNOWN`
- ACTION: `ACTION_NOT_STARTED`, `ACTION_STARTED`, `UNKNOWN`
- all: `NOT_EXPRESSED`, `UNRECOVERABLE`

For `CONDITIONAL`, this field records the **condition state only**. Put the
action state, if explicitly cued, in `rationale`.

### 5. `evidence_support`

`SUPPORTED_BY_DIALOGUE` / `CONTRADICTED_BY_LATER_DIALOGUE` / `NOT_SUPPORTED` /
`AMBIGUOUS` / `NOT_ASSESSABLE`.

### 6. `primary_judgment` (required)

Apply this order strictly:

1. `PROPOSITION_LOSS` — identity is `LOST` or `PARTIAL` (no "materially
   partial" exception).
2. `STATUS_OMISSION` — identity preserved, no explicit status cue, and no
   conflicting state asserted.
3. `LEGITIMATE_UPDATE` — the dialogue contains a later supported change and the
   memory represents it as a change (explicit marker, or an ordered chain that
   retains both the old and new state).
4. `NO_DISTORTION` — the expressed status matches the evidence-supported final
   state. A memory that only states the final state belongs here.
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
- **Implicit inference is not assertion**: `奖学金购机` asserts neither
  condition satisfied nor action committed; `获奖学金购电脑` asserts condition
  satisfied (explicit `获奖学金`) but not action commitment.
- **A memory that states only the final state is `NO_DISTORTION`**, not
  `LEGITIMATE_UPDATE`. The latter requires the change to be represented as a
  change (explicit marker, or an ordered chain retaining both states).
- A shorter paraphrase is not automatically distortion.
- A topic label replacing the target predicate is `PARTIAL`, not `PRESERVED`,
  and scores `PROPOSITION_LOSS`.

## Worked examples

1. Memory `确认去上海工作…` vs explicit confirmation:
   `PRESERVED`, `EPISTEMIC`, `YES`, `ESTABLISHED`, `SUPPORTED_BY_DIALOGUE`,
   `NO_DISTORTION`.

2. Memory `上海工作：整理日程…` vs `可能会去上海工作`:
   `PARTIAL` (predicate `去` absent), `EPISTEMIC`, `NO`, `NOT_EXPRESSED`,
   `NOT_ASSESSABLE`, `PROPOSITION_LOSS`.

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

6. Memory `获奖学金购电脑` vs T3 `我已经拿到奖学金了，条件已经满足` and an
   action that is only considered:
   `PRESERVED`, `CONDITIONAL`, `YES`, `CONDITION_SATISFIED`,
   `SUPPORTED_BY_DIALOGUE`, `NO_DISTORTION`; note in `rationale` that the
   action state is not explicitly expressed.

7. Memory `奖学金购机` vs the same dialogue:
   `PRESERVED`, `CONDITIONAL`, `NO`, `NOT_EXPRESSED`, `NOT_ASSESSABLE`,
   `STATUS_OMISSION` (no acquisition cue, so condition satisfied is not
   asserted).

8. Memory `买电脑→调天气→处理作业` for a conditional trajectory:
   `PRESERVED` (predicate and object intact), `CONDITIONAL`, `NO`,
   `NOT_EXPRESSED`, `NOT_ASSESSABLE`, `STATUS_OMISSION`.

9. Memory `计划买电脑→天气变→整理日程→确认买电脑→做作业` vs T1 possible and
   T3 confirmed:
   `PRESERVED`, `EPISTEMIC`, `YES`, `ESTABLISHED`,
   `SUPPORTED_BY_DIALOGUE`, `LEGITIMATE_UPDATE` (ordered chain retains both
   states).

10. Memory `决策前后购电脑，用于日常事务管理`:
    `PRESERVED`, `CANNOT_DETERMINE`, `UNCLEAR`, `UNRECOVERABLE`, `AMBIGUOUS`,
    `AMBIGUOUS_UNASSESSABLE`.

## After annotating

Keep UTF-8, do not delete rows, fill `rationale` when unsure. Then run:

```
python -m experiments.check_v3_annotations \
  --a .../annotator_A.csv --b .../annotator_B.csv
```

The checker validates labels and dimension/status compatibility, then reports
raw agreement and Cohen's kappa per field. Disagreements are adjudicated only
after both files are complete.

This is the v3.2 **conditional-focused** calibration set (60 items: 5 updated
and 5 stable conditional trajectories × 6 paths). It tests whether the revised
conditional rules remove the action-vs-condition disagreement. Do not freeze
the guide or start the confirmatory run until the pre-registered agreement
thresholds are met. Proposed thresholds (require sign-off before annotation):
overall primary-judgment κ ≥ 0.80 and every dimension κ ≥ 0.70.
