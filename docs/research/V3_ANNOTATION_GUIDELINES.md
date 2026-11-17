# V3 Blind Human Annotation Guidelines (v3.2)

**Status:** calibration guide for the collapsed confirmatory ontology. Do not
treat as frozen until the v3.2 conditional calibration set reaches acceptable
agreement.

**Revision note (2026-11-17).** v3.2 resolves the four rule ambiguities found in
the v3.1 adjudication (`docs/research/2026-11-17-v3-1-adjudication.md`):
proposition identity no longer includes the condition relation; a status counts
as expressed only with an explicit cue; an ordered chain that retains both the
old and new state is `LEGITIMATE_UPDATE`; and `LEGITIMATE_UPDATE` is checked
before `NO_DISTORTION`. Any `PARTIAL` identity is now scored
`PROPOSITION_LOSS`.

## 1. Purpose

Evaluate whether a generated memory preserves the target proposition and
accurately represents its evidence-supported state. Do not judge writing
quality, helpfulness, or plausibility.

## 2. What annotators receive

For each item:

- the source dialogue in chronological order;
- a neutral target-proposition question that does not reveal the dimension or
  the gold state;
- one anonymized generated memory.

Annotators do **not** receive condition, path, model, prompt, gold final state,
gold evidence-turn IDs, or other annotations.

## 3. Label sequence

### A. Proposition identity

- `PRESERVED` — same claim and essential arguments recoverable.
- `PARTIAL` — topic identifiable but a material argument/relation/scope missing.
- `LOST` — target cannot be recovered.
- `AMBIGUOUS` — multiple materially different interpretations.

The proposition unit is the **target predicate plus its essential arguments**
(agent, object, place, polarity). Modality, condition relation, and status are
**not** part of proposition identity; they are scored in the state dimensions.
For a conditional trajectory the target proposition is the action itself (e.g.
`购买电脑`), not the full "if condition, then action" sentence.

A keyword or topic label alone is not preservation. If the target predicate is
absent (e.g. `电脑调整` for `购买电脑`; `上海工作多` for `去上海工作`), record
`PARTIAL`, not `PRESERVED`.

### B. Primary dimension (applicability)

Choose exactly one:

- `EPISTEMIC` — whether something is true, confirmed, or uncertain.
- `INTENTIONAL` — the speaker's commitment to a future action.
- `CONDITIONAL` — whether a prerequisite is met; action state is separate and
  is scored only if the memory explicitly asserts it.
- `ACTION` — execution progress of an already-committed action.
- `CANNOT_DETERMINE` — the memory is unparseable in both directions, so no
  dimension can be selected.

If two seem applicable, choose the dimension the dialogue's update turns are
about and explain the other in `rationale`. For a conditional trajectory the
update turn is normally about the prerequisite, so choose `CONDITIONAL` even
when an action verb also appears. Use `CANNOT_DETERMINE` only when the memory
supports mutually incompatible readings; do not use it merely because the
proposition is `PARTIAL` — choose the dimension the dialogue is about and score
`PROPOSITION_LOSS`.

### C. Status expressed?

A status counts as expressed only when the memory contains an **explicit
lexical cue** for that state. An unmarked action verb records the action but
does not assert its state; a bare topic noun does not assert a condition state.

- `YES` — an explicit cue expresses a status for the primary dimension.
- `NO` — no explicit cue is present.
- `UNCLEAR` — the cue is present but supports two incompatible states.

Examples of explicit cues: `可能` / `不能确定` (POSSIBLE), `确认` / `已确定`
(ESTABLISHED), `考虑` / `打算` (CONSIDERING), `决定` / `已承诺` (COMMITTED),
`未拿到` / `未满足` (CONDITION_ACTIVE), `已拿到` / `条件满足` (CONDITION_SATISFIED).
Juxtaposition alone (`奖学金购机`) is **not** a cue for condition satisfied or
for action commitment.

### D. Expressed status (collapsed labels)

Use only the labels for the chosen primary dimension:

- EPISTEMIC: `POSSIBLE`, `ESTABLISHED`, `UNKNOWN`
- INTENTIONAL: `CONSIDERING`, `COMMITTED`, `UNKNOWN`
- CONDITIONAL: `CONDITION_ACTIVE`, `CONDITION_SATISFIED`, `UNKNOWN`
- ACTION: `ACTION_NOT_STARTED`, `ACTION_STARTED`, `UNKNOWN`
- all dimensions: `NOT_EXPRESSED`, `UNRECOVERABLE`

For `CONDITIONAL`, `expressed_status` records the **condition state only**.
Record the action state (if explicitly cued) in `rationale`; it is a secondary
dimension and does not replace the condition state.

### E. Evidence support

- `SUPPORTED_BY_DIALOGUE`
- `CONTRADICTED_BY_LATER_DIALOGUE`
- `NOT_SUPPORTED`
- `AMBIGUOUS`
- `NOT_ASSESSABLE`

### F. Primary judgment

Apply this order strictly:

1. If `proposition_identity` is `LOST` or `PARTIAL`: `PROPOSITION_LOSS`.
   There is no "materially partial" exception; partial loss is loss for the
   primary outcome and is reported separately.
2. Else if `status_expressed` is `NO` or `UNCLEAR`: `STATUS_OMISSION`.
3. Else if the dialogue contains a later supported change and the memory
   represents that change **as a change**: `LEGITIMATE_UPDATE`.
   An explicitly ordered chain that retains both the earlier and the later
   state of the same proposition (e.g. `计划买电脑→…→确认买电脑`) counts.
4. Else if the expressed status matches the evidence-supported final state:
   `NO_DISTORTION`.
5. Else if the expressed status differs and is unsupported:
   `UNSUPPORTED_STATUS_DISTORTION`.
6. If identity or status cannot be resolved: `AMBIGUOUS_UNASSESSABLE`.

Step 3 must be checked **before** step 4. A memory that only states the final
state (no earlier state retained) remains `NO_DISTORTION`.

### G. Subtype, rationale, confidence, turn references

- `subtype` for distortion: `ESCALATION`, `ATTENUATION`,
  `COMMITMENT_INFLATION`, `COMMITMENT_DEFLATION`, `CONDITIONAL_COLLAPSE`,
  `POLARITY_SCOPE`, `TEMPORAL`, `NONE`.
- `rationale`: one or two sentences.
- `confidence`: `HIGH`, `MEDIUM`, `LOW`.
- `turn_references`: turn IDs or a short quote.

## 4. Critical distinctions

- `我可能会` is not `我确定`; `我想去` is not `我已决定去`.
- A satisfied prerequisite does not prove commitment or execution.
- `已决定，但时间未定` is still COMMITTED with unresolved timing.
- A later explicit cancellation supersedes an earlier commitment.
- **Omission is not distortion.** Removing a status cue is
  `STATUS_OMISSION` unless the memory asserts a different state.
- **Implicit inference is not assertion.** `奖学金购机` does not assert that the
  condition is satisfied or that the purchase is committed. `获奖学金购电脑`
  asserts condition satisfied (explicit `获奖学金`) but not action commitment.
- **A memory that simply states the final state is `NO_DISTORTION`**, not
  `LEGITIMATE_UPDATE`. `LEGITIMATE_UPDATE` requires the memory to represent the
  later supported change *as a change* (explicit marker or ordered chain that
  retains both states).
- A shorter paraphrase is not automatically distortion.
- A topic label in place of the target predicate is `PARTIAL`, not
  `PRESERVED`; it is scored as `PROPOSITION_LOSS`, not `STATUS_OMISSION`.

## 5. Handling uncertainty

Use `AMBIGUOUS_UNASSESSABLE`, `UNCLEAR`, or `UNRECOVERABLE` rather than guessing.
If the dialogue itself does not determine the final state, record that the item
is underdetermined.

## 6. Independence and adjudication

Annotators work independently and do not discuss cases before submission. After
labels are locked:

1. compute raw agreement and a chance-corrected statistic;
2. inspect disagreement categories;
3. adjudicate with a third reviewer using the dialogue and this guide;
4. preserve original labels and adjudication separately.

Gold state and evidence-turn annotations are created by a separate curator and
remain hidden until labels are frozen.

## 7. Quality controls and staged budget

- Include repeated hidden items and clear positive/negative controls.
- Report agreement per field and label prevalence; a single overall kappa can
  hide class imbalance.
- Use a 60-item calibration set first. Freeze this guide and the collapsed
  ontology only after acceptable agreement. Then size the confirmatory set by
  power analysis.
- For PATH_REPLICATE, each path is a separate anonymized item; path IDs are
  opaque and shuffled. Do not annotate all paths of one trajectory
  consecutively.

## 8. Annotation record schema

`item_id`, `annotator_id`, `proposition_identity`, `primary_dimension`,
`status_expressed`, `expressed_status`, `evidence_support`, `primary_judgment`,
`subtype`, `rationale`, `confidence`, `turn_references`.

Condition mapping and gold labels remain in a separate curator-only file.
