# V3 Blind Human Annotation Guidelines (v3.2.5)

**Status:** calibration guide for the collapsed confirmatory ontology. Do not
treat as frozen until the v3.2 conditional calibration set reaches acceptable
agreement.

**Revision note (2026-11-17).** v3.2 resolves the four rule ambiguities found in
the v3.1 adjudication (`docs/research/2026-11-17-v3-1-adjudication.md`):
proposition identity no longer includes the condition relation; a status counts
as expressed only with an explicit cue; an ordered chain that retains both the
old and new state is `LEGITIMATE_UPDATE`; and `LEGITIMATE_UPDATE` is checked
before `NO_DISTORTION`. Any `PARTIAL` identity is now scored
`PROPOSITION_LOSS`. v3.2.1 adds a required `action_status` field for
`CONDITIONAL` items so condition and action states are measured separately;
an explicit action escalation with no dialogue support is
`UNSUPPORTED_STATUS_DISTORTION` (`CONDITIONAL_COLLAPSE`).

**v3.2.2 (2026-11-17).** The v3.2.1 calibration showed that `action_status` and
the condition state are reliable (κ 1.000 and 0.974) but that proposition
identity was applied at topic level by one annotator. v3.2.2 adds the
head-predicate + object worksheet below and defines evidence support as support
for the **expressed status**, not the proposition. v3.2.3 clarifies serial-verb
targets (`去上海工作` → main action `工作`), makes `AMBIGUOUS` identity preempt
the status judgment, and restricts generic satisfaction cues (`已达标`) to
trajectories with a single explicit prerequisite. v3.2.4 adds the post-P5
clarifications in §9 (nominalized predicates, future-action cues, contradictory
cues, aspect/negative action states); they are pending calibration.

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

**Identity worksheet (v3.2.2).** For every item:

1. Write the target's **head predicate** and **object/entity**.
2. Locate both in the memory. Direct synonyms and inflections count; aspect and
   modality words do not (`开始学习` preserves `学习`; `决定购买` preserves
   `购买`).
3. `PRESERVED` only if both are recoverable. A contextually unambiguous object
   shorthand counts (`购机` for `购买电脑` in a computer trajectory).
4. `PARTIAL` if the head predicate is replaced by a different action
   (`读研` for `申请研究生`), the object is lost or broadened
   (`参赛` for `参加数学建模比赛`; `奖学金申请` for `申请研究生`), or only a
   topic noun remains (`海外交换` for `申请海外交换`).
5. Do not infer identity from status correctness or from the target question.

**Serial-verb targets (v3.2.3).** For targets of the form `去/来 + place +
action` (e.g. `去上海工作`), the head predicate is the final action (`工作`);
the directional verb is not required if the action and place are preserved and
the memory refers to the same agent/plan. `上海工作待定` → `PRESERVED`. A
generic statement about the place (`上海工作多`) is a different claim →
`PARTIAL`.

| Target | Memory | Identity |
|---|---|---|
| 购买电脑 | 买电脑 / 购电脑 / 购机 | PRESERVED |
| 开始学习日语 | 学日语 / 日语学习 | PRESERVED |
| 申请海外交换 | 暂不考虑海外交换 | PARTIAL (no `申请`) |
| 申请研究生 | 暂不读研 | PARTIAL (different action) |
| 申请研究生 | 奖学金申请 | PARTIAL (object lost) |
| 参加数学建模比赛 | 参赛 | PARTIAL (specific object lost) |
| 申请研究生 | 研究生申请奖学金 | AMBIGUOUS (two parses) |
| 去上海工作 | 上海工作待定 / 瞄准上海工作 | PRESERVED (main action `工作` + place) |
| 去上海工作 | 上海工作多 | PARTIAL (different claim: generic job market) |

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
for action commitment. A generic satisfaction cue (`已达标` / `已满足`) counts
only when the trajectory has a single explicit prerequisite; if it could refer
to another standard, use `UNKNOWN`.

### D. Expressed status (collapsed labels)

Use only the labels for the chosen primary dimension:

- EPISTEMIC: `POSSIBLE`, `ESTABLISHED`, `UNKNOWN`
- INTENTIONAL: `CONSIDERING`, `COMMITTED`, `UNKNOWN`
- CONDITIONAL: `CONDITION_ACTIVE`, `CONDITION_SATISFIED`, `UNKNOWN`
- ACTION: `ACTION_NOT_STARTED`, `ACTION_STARTED`, `UNKNOWN`
- all dimensions: `NOT_EXPRESSED`, `UNRECOVERABLE`

For `CONDITIONAL`, `expressed_status` records the **condition state only**.
Record the action state separately in `action_status` (v3.2.1):

- `NOT_EXPRESSED` — no explicit cue for the action's state.
- `NOT_PURSUING` — explicitly not intended, not pursued, or not started
  (`暂不`, `不打算`, `还没开始`).
- `CONSIDERING` — explicit consideration or interest, no commitment.
- `COMMITTED` — explicit decision, commitment, registration, start, or
  execution (`决定`, `已报名`, `开始`, `已买`, `按计划推进`).
- `UNKNOWN` — an action cue is present but supports incompatible states.
- `NOT_APPLICABLE` — non-conditional item.

A bare action verb (`购电脑`, `参赛`) is not a cue; only an explicit state cue
counts. For all conditional items `action_status` is required.

### E. Evidence support

Evidence support is about the **expressed status**, not about the proposition.
If `status_expressed` is `NO` or `UNCLEAR` (or the status is `NOT_EXPRESSED` /
`UNRECOVERABLE`), use `NOT_ASSESSABLE`; do not use `SUPPORTED_BY_DIALOGUE`
merely because the dialogue's final state is clear. If a status is explicitly
expressed, assess it even when proposition identity is `PARTIAL`; the primary
judgment still follows the identity-first order.

- `SUPPORTED_BY_DIALOGUE`
- `CONTRADICTED_BY_LATER_DIALOGUE`
- `NOT_SUPPORTED`
- `AMBIGUOUS`
- `NOT_ASSESSABLE`

### F. Primary judgment

Apply this order strictly:

1. If `proposition_identity` is `AMBIGUOUS`: `AMBIGUOUS_UNASSESSABLE`.
   Identity ambiguity preempts the status judgment.
2. Else if `proposition_identity` is `LOST` or `PARTIAL`: `PROPOSITION_LOSS`.
   There is no "materially partial" exception; partial loss is loss for the
   primary outcome and is reported separately.
3. Else if the dialogue contains a later supported change and the memory
   represents that change **as a change**: `LEGITIMATE_UPDATE`.
   An explicitly ordered chain that retains both the earlier and the later
   state of the same proposition (e.g. `计划买电脑→…→确认买电脑`) counts.
4. Else if any applicable dimension explicitly asserts a state that the
   dialogue does not support: `UNSUPPORTED_STATUS_DISTORTION`.
   For `CONDITIONAL`, this includes `action_status = COMMITTED` when the
   dialogue only supports `CONSIDERING` (subtype `CONDITIONAL_COLLAPSE`).
5. Else if the primary dimension has no explicit status cue: `STATUS_OMISSION`.
6. Else if the expressed statuses match the evidence-supported final states:
   `NO_DISTORTION`.
7. If status cannot be resolved: `AMBIGUOUS_UNASSESSABLE`.

Steps 3 and 4 are checked before omission and no-distortion: an explicit
unsupported action escalation is distortion even when the condition state is
omitted. A memory that only states the final state remains `NO_DISTORTION`.

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
- **Explicit action escalation is distortion.** `开始学日语` or `报名马拉松`
  after a dialogue that only says `才考虑...` asserts `COMMITTED` without
  support; score `UNSUPPORTED_STATUS_DISTORTION`, subtype
  `CONDITIONAL_COLLAPSE`, even if the condition state is correct.
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

## 9. v3.2.4 clarifications (post-P5, pending calibration)

These resolve systematic disagreements on the P5 confirmatory set. They are
**not yet calibrated**; treat P5 human results as provisional until a recheck.

### Nominalized predicates

A nominalized form of the target action preserves identity when the action and
object are recoverable:

- `驾照考试` for `考驾照` → `PRESERVED` (`考试` nominalizes `考`).
- `日语学习` for `开始学习日语` → `PRESERVED`.
- A bare topic noun without the action (`驾照` alone) remains `PARTIAL`.

### Future-action cues

- `将 / 就要 / 会 + action` asserts a future commitment → `COMMITTED`
  (e.g. `将开始健身`).
- `计划 / 打算 / 考虑 + action` are weaker → `CONSIDERING`.
- `已决定 / 已承诺 / 按计划推进` → `COMMITTED`.

### Contradictory cues

If the memory contains both an affirmative and a negative status cue for the
same proposition and the scope is not resolvable (`确认未开网店`,
`确认将开网店但不确定`), use `status_expressed = UNCLEAR`,
`expressed_status = UNKNOWN`, `evidence_support = AMBIGUOUS` or
`NOT_ASSESSABLE`, and `primary_judgment = AMBIGUOUS_UNASSESSABLE`.

### Aspect and negative action states

- `...中` (e.g. `换工作中`) asserts committed/ongoing → `COMMITTED`.
- `不 / 暂不 / 不打算 + action` asserts a negative action state →
  `NOT_PURSUING`.
- A bare action verb remains `NOT_EXPRESSED`.

## 10. v3.2.5 clarifications (post-replication, pending calibration)

These resolve systematic gemma3:12b writer phrasings:

- `已开始 / 进行中 / 计划进行中` for a target whose evidence only confirms
  "will start" (`会开始`) is a **temporal escalation** →
  `UNSUPPORTED_STATUS_DISTORTION`, subtype `TEMPORAL`.
- `待定 / 未定` as the only status cue counts as `CONSIDERING` (intentional) or
  `POSSIBLE` (epistemic); it is not omission.
- `计划中` for a gold COMMITTED target is `CONSIDERING` (commitment deflation),
  unless the memory says `按计划推进` or `已决定`.
- Contradictory pairs (`待定 + 已安排`, `到账 + 需满足`) →
  `AMBIGUOUS_UNASSESSABLE` (see §9).

These are pending calibration on the replication set.
