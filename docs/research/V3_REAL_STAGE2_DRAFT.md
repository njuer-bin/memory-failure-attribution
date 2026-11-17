# Stage 2 Draft v2 — Real-Dialogue Status Fidelity Annotation and Calibration

Status: **DRAFT v2, not frozen.** Revised after the 50-item screening exposed
rubric defects in `lexical_labelable` and `update_present`. Calibration has
not passed; the current A/B pair is not two independent humans (B is a model,
A's provenance is blank). Do not freeze or run confirmatory generation yet.

This document does not change the frozen V3 synthetic pilot
(`freeze/v3-pilot-2026-11-17`).

## 1. What Stage 2 must settle

The Stage 1 audit showed that a marker-based screen mostly finds intentional
plans, rarely finds epistemic status, and can confuse an explicit cue with the
semantic status. Stage 2 therefore fixes **what is measured** before any
confirmatory generation:

1. Lexical Status Fidelity (LSF) — was the explicit status expression kept?
2. Semantic Status Fidelity (SSF) — was the meaning of the status kept?

These are separate outcomes. A memory can lose the cue and keep the status
(paraphrase), or keep a cue and change the status (distortion). Reporting one
number would hide both.

## 1a. What the 50-item screen changed (2026-11-17)

The screen was filled by A (human, WMY) and B (human, YTB, reviewing an AI
first draft), so it is a mixed-provenance rubric diagnostic, not an unaided
two-human reliability estimate. Agreement was usable for `dimension` (kappa
0.826), `semantic_labelable` (0.730), and `difficulty` (0.750); it failed for
`lexical_labelable` (0.226) and `update_present` (0.170), and was weak for
`evidence_sufficient` (0.535) and `status_bearing` (0.606, raw 0.920).

This version therefore:

- defines `lexical_labelable` as "would the cue rule assign the **correct**
  status type?", not "is a cue present?";
- gives `update_present` three states (`yes` / `no` / `unknown`) so a later
  mention without a change is not scored as an update;
- defines `evidence_sufficient` as both gold assignability and later
  comparison;
- adds anchors for conditional risk, past evaluation, self-encouragement, and
  hedged plans.

Full defect analysis: `2026-11-17-real-screening-results.md`.

## 2. Unit of analysis

For each item:

- `P` — the target proposition (one testable claim about the speaker's own
  action, state, or belief).
- `E` — the evidence span in the source dialogue (session id + turn ids, with
  the minimal surrounding turns needed to interpret P).
- `H` — the transformation history applied to E (direct, recursive,
  rewrite-matched, repeated-direct, source-peek, raw reference).
- `M` — the resulting memory text shown to the annotator.
- `t` — the evaluation time; the gold status is the latest state supported by
  E up to `t`, including legitimate updates.

A status change supported by later evidence is a legitimate update, not drift.
The gold status is not "the first thing said".

## 3. Ontology for English dialogue

Stage 2 reuses the frozen V3 typed state
`S(p,t) = (epistemic, intentional, conditional, action, polarity, scope, time)`
from `V3_FORMAL_DEFINITIONS.md`; it does not invent a new ontology. The cue
lists are illustrative, not definitional. Status is assigned from meaning, and
non-applicable dimensions are `N/A`, not `UNKNOWN`.

### Epistemic state

`UNKNOWN` / `POSSIBLE` / `PROBABLE` / `SUPPORTED` / `ESTABLISHED` / `REJECTED`

- `UNKNOWN`: the dialogue does not establish the speaker's epistemic position.
- `POSSIBLE`: explicitly possible, or under consideration as a factual belief.
- `PROBABLE`: expressed as likely but not established.
- `SUPPORTED`: evidence or assertion supports it, but certainty is not
  warranted.
- `ESTABLISHED`: explicitly confirmed or established by authoritative evidence
  in the dialogue.
- `REJECTED`: explicitly denied or disconfirmed.

Do not infer certainty from confident writing style.

### Intentional state

`NOT_EXPRESSED` / `CONSIDERING` / `INTERESTED` / `INTENDING` / `COMMITTED` /
`EXECUTING` / `COMPLETED` / `CANCELLED` / `NOT_INTENDED`

- `NOT_EXPRESSED`: no intention is expressed.
- `CONSIDERING`: evaluating or contemplating.
- `INTERESTED`: preference or desire, no commitment.
- `INTENDING`: states an intention or plan.
- `COMMITTED`: explicit decision or commitment.
- `EXECUTING`: action has begun.
- `COMPLETED`: action completed.
- `CANCELLED`: prior intention/commitment explicitly cancelled.
- `NOT_INTENDED`: explicitly says the action is not intended.

These labels are not assumed to be a linear scale; `COMPLETED` and `CANCELLED`
are distinct terminal states.

### Conditional state

Store condition and action separately:

- `condition_status` ∈ `{UNKNOWN, ACTIVE_UNSATISFIED, SATISFIED, FAILED,
  WAIVED, NOT_APPLICABLE}`
- `action_status` ∈ `{NOT_EXPRESSED, CONSIDERING, INTENDING, COMMITTED,
  EXECUTING, COMPLETED, CANCELLED}` (use `NOT_INTENDED` only if the action is
  explicitly denied)

A satisfied prerequisite does not imply the action is committed or executed.
A conditional memory can preserve the condition and lose the action, or the
reverse. Both must be recorded.

## 4. Gold coding (from E only)

The gold annotator sees `E`, not `M`, and records:

| Field | Values |
|---|---|
| `target_proposition` | free text, one claim |
| `gold_dimension` | epistemic / intentional / conditional / mixed |
| `gold_status` | value from the dimension scale |
| `gold_condition_state` | conditional only |
| `gold_action_state` | conditional only |
| `gold_strength` | weak / moderate / strong (within the status) |
| `gold_confidence` | high / medium / low |
| `evidence_quote` | the minimal supporting quote |
| `update_history` | ordered list of earlier statuses, if any |

If `E` cannot support a status, the item is `E0_INSUFFICIENT` and is excluded
from fidelity analyses (reported separately). This protects against scoring a
memory as distorted when the source was never clear.

## 5. Lexical Status Fidelity (LSF)

The LSF annotator sees `M` (and may see `P` and `E` for reference) and records
only whether an explicit status expression for `P` is present and what type it
is.

| Outcome | Rule |
|---|---|
| `CUE_PRESERVED` | an explicit cue of the same status type is present |
| `CUE_ALTERED` | an explicit cue is present but of a different status type or strength |
| `CUE_ABSENT` | no explicit status expression for `P` |
| `NOT_APPLICABLE` | the source itself had no explicit cue |

Rules:

- Wording may change; the status type must match.
- A weaker cue for a `COMMITTED` gold status (e.g., "plans to") is
  `CUE_ALTERED`, not `CUE_PRESERVED`.
- A stronger cue for a `CONSIDERING` gold status (e.g., "will") is
  `CUE_ALTERED`.
- `CUE_ABSENT` is never automatically distortion.
- Record the cue text and its position in `M`.
- **Cue type must match the semantic status.** A cue whose canonical type is
  different does not count as preserved:
  - "I think I'll X": `I think` is canonically epistemic, status is
    intentional → not preserved.
  - "I'll definitely X": `definitely` is canonically epistemic, status is
    intentional → not preserved.
  - "If I X, I'll Y" with a conditional status: `if` matches → preserved.
  - "just in case" is a conditional backup cue; add it explicitly to the cue
    table or it will be missed.

## 6. Semantic Status Fidelity (SSF)

The SSF annotator sees `M` and assigns the status a careful reader would infer.
`E` may be consulted only for adjudication, not during the first pass.

| Outcome | Rule |
|---|---|
| `SEMANTIC_CORRECT` | assigned status matches the gold status |
| `SEMANTIC_DISTORTED` | assigned status contradicts the gold status |
| `SEMANTIC_UNDERSPECIFIED` | `M` permits the gold status but does not determine it |
| `UNASSESSABLE` | `P` is lost/ambiguous, or `E` was insufficient |

Rules:

- `SEMANTIC_DISTORTED` requires `M` to support a status incompatible with the
  gold status. A missing cue alone is not distortion.
- If `M` can be read as either the gold status or another status, code
  `SEMANTIC_UNDERSPECIFIED`, not distortion.
- If `P` is not recoverable from `M`, code `UNASSESSABLE` and report
  proposition loss separately.
- For conditional items, code condition and action separately; a mismatch in
  either is distortion for that component.

## 7. Decision order (pre-registered)

1. `P` identity: can the annotator state the same proposition from `E` and `M`?
2. `E` sufficiency: if not, `E0`.
3. Dimension: semantic, not the matched word.
4. Gold status and strength.
5. LSF: cue type in `M`.
6. SSF: status inferred from `M`.
7. Ambiguity: if unresolved, record the reason; do not force a label.

## 8. Boundary rules (must be in the guide before freezing)

- **"I think I'll X"** → intentional (hedged commitment), not epistemic.
- **"I think X is true / happened"** → epistemic.
- **"I hope to X"** → `INTENDING` or `CONSIDERING`, not `COMMITTED`.
- **"I'm going to X"** → `INTENDING` or `COMMITTED`; context decides.
- **"I booked / signed up / paid for X"** → `COMMITTED` or `COMPLETED`.
- **"Maybe X"** → `POSSIBLE` (epistemic) or `CONSIDERING` (intentional) by the
  proposition type.
- **"If X, I'll Y"** → conditional; record condition state and action state.
- **"just in case"** → conditional backup; action is conditional.
- **Preferences** ("as long as it's safe", "I'm open to any") → not status.
- **Past evaluations** ("the bread didn't turn out") → not current status.
- **Third-party states** ("my friend is publishing") → not the speaker's status.
- **Negation** ("I'm not going to X") → `NOT_INTENDED`, a status; not absence.
- **Hypotheticals / quotes** → exclude unless the speaker endorses them.
- **Questions** → exclude.
- **Sarcasm / unresolved hedging** → `ambiguous` with a note.

## 8a. Corrected screening-field definitions (from the 50-item screen)

These replace the ambiguous v1 wording.

### `lexical_labelable`

`yes` only if the cue-mapping rule would assign the **same status type** as
the semantic dimension. A present but misleading cue is `no` while
`lexical_cue_present` stays `yes`.

- "I think I'll try it" → cue `I think` (epistemic) vs status intentional →
  `no`.
- "I'll definitely check it out" → `definitely` (epistemic) vs intentional →
  `no`.
- "worried it'll break if I don't fix it" → `if` (conditional) vs conditional
  → `yes`.
- "I'll pack it just in case" → `in case` (conditional) vs conditional →
  `yes`, provided `in case` is in the cue table.

### `update_present`

- `yes`: a later session changes the status; quote the change.
- `no`: a later mention exists and the status is unchanged.
- `unknown`: no later mention is available.

Do not use `yes` for a mere re-mention. Do not use `unknown` when a later
mention exists but is unchanged.

### `evidence_sufficient`

- `yes`: the gold status is assignable **and** a later memory can be compared.
- `partial`: the gold status is assignable but the comparison is weak.
- `no`: the gold status is not assignable.

### `status_bearing` anchors

- `yes`: "who knows if I'll ever get a pet" (possibility);
  "if I don't make changes soon, it can get worse" (conditional risk);
  "wondering if I can use bacteria from the old tank" (uncertainty).
- `no`: "the bread I tried didn't turn out" (past evaluation);
  "I think schools should be funded" (normative stance);
  "I'm open to any accommodation as long as it's safe" (preference).

### `dimension` anchors

- A risk statement with `if` is `conditional`, not `epistemic`
  ("it can get worse if I don't...").
- A past evaluation is `none`, not `intentional`.
- Self-encouragement ("I'll keep going and find those keys") is `none`, not a
  status.
- A hedged future action ("I think I'll X", "maybe I'll X") is `intentional`
  with weak strength, not `epistemic`.

## 9. Annotation form (formal study)

One row per `(item, transformation)`. Proposed columns:

| Column | Values |
|---|---|
| `item_id` | stable id |
| `transformation` | raw / direct / recursive / rewrite_matched / repeated_direct / source_peek |
| `target_proposition` | free text |
| `evidence_quote` | free text |
| `gold_dimension` | E / I / C / mixed / E0 |
| `gold_status` | ontology value |
| `gold_condition_state` | conditional only |
| `gold_action_state` | conditional only |
| `gold_strength` | weak / moderate / strong |
| `gold_confidence` | high / medium / low |
| `lsf_outcome` | CUE_PRESERVED / CUE_ALTERED / CUE_ABSENT / NOT_APPLICABLE |
| `lexical_cue_in_memory` | quote or empty |
| `ssf_outcome` | SEMANTIC_CORRECT / SEMANTIC_DISTORTED / SEMANTIC_UNDERSPECIFIED / UNASSESSABLE |
| `status_assigned_from_memory` | ontology value or UNASSESSABLE |
| `proposition_identity_in_memory` | PRESERVED / PARTIAL / LOST / AMBIGUOUS |
| `ambiguity_reason` | free text or empty |
| `notes` | free text |

Gold fields are filled once per item; memory fields once per
`(item, transformation)`.

## 10. Independence, blinding, and adjudication

- Two annotators label every item independently.
- An AI first draft may be used for one annotator only if disclosed. That
  annotator's labels are `human-reviewed-model`, not unaided human. Re-annotate
  a model-free subset (20-30 items) to estimate anchoring before claiming
  reliability.
- Memory annotators are blind to the transformation label and to the gold
  status. The gold annotator is blind to `M`.
- If one person plays both roles, the roles must be separated in time and the
  gold file must be locked before memory coding. Record this in provenance.
- Disagreements are resolved in the pre-registered order:
  `P` identity → `E` sufficiency → dimension → status → strength → LSF → SSF.
- Adjudication is by a third human or by a pre-registered rule. Model
  assistance is allowed but recorded as `model-assisted`; it is never described
  as independent human adjudication.
- Original labels are preserved in `annotator_A` / `annotator_B`; adjudicated
  labels go in separate `adj_*` columns.
- Report raw agreement and Cohen's kappa per field. Kappa is
  prevalence-sensitive; raw agreement is always reported alongside.

## 11. Calibration set and gates

Proposed calibration: 60 items from **different conversations** than the 50
screening items. The screening set is a development set; reusing it would
inflate agreement.

- 30 LoCoMo intentional-status propositions (15 considering/intending,
  15 committed/completed).
- 15 conditional propositions with judgeable condition and action states,
  enriched per the Stage 2 decision.
- 15 long-haystack LongMemEval-s items (44-57 sessions) as a second-domain
  check; do not use the 1-6-session oracle variant for depth.
- Include at least 10 items from the `ambiguous`/`no` boundary anchors, and at
  least 5 cue-mismatch items ("I think I'll", "I'll definitely") that broke
  `lexical_labelable` in the screening set.

The current A/B agreement (kappa 0.826 dimension, 0.730 semantic labelability,
0.226 lexical labelability, 0.170 update) is a rubric diagnostic, not a
calibration pass.

Proposed reliability gates (to confirm before freezing):

| Field | Raw | Kappa |
|---|---:|---:|
| `proposition_identity` | >= 0.90 | >= 0.80 |
| `gold_dimension` | >= 0.85 | >= 0.70 |
| `gold_status` | >= 0.85 | >= 0.70 |
| `lsf_outcome` | >= 0.85 | >= 0.70 |
| `ssf_outcome` | >= 0.80 | >= 0.65 |

If a gate fails, revise the guide and re-calibrate on a **new** item set; do not
reuse calibration items in the confirmatory set. If LSF passes but SSF fails,
the semantic ontology is the problem, not the annotators; do not proceed by
dropping SSF.

## 12. Sampling and inclusion after calibration

The Stage 1 audit gives a usable-yield estimate, not a prevalence estimate.
After calibration:

1. Set `n_usable` from the calibration yield: 150-200 usable propositions is the
   planning target (no formal power claim; report precision).
2. Set the final n after a 40-60 item real-data pilot estimates the paired
   difference SD. Target a paired CI half-width of 0.10-0.12. If the annotation
   budget is fixed, reduce the number of conditions (for example, move
   `repeated_direct` to a side arm) before reducing the item count; the paired
   contrast is the primary analysis.
3. Screen `n_usable / yield` candidates; if yield is 60%, screen ~300.
3. Stratify by dimension (intentional primary; conditional secondary; epistemic
   only if calibration supports it) and by consequence (high / partial / low).
4. Include only items with `status_bearing=yes`, a clear proposition,
   sufficient evidence, and a later-session mention when the design tests
   persistence or depth.
5. Exclude `E0`, third-party states, preferences, past evaluations, and
   unresolved ambiguity. Report exclusion counts.

If epistemic calibration fails, the confirmatory study drops epistemic and says
so in the title/abstract; it does not quietly rename an intentional study as a
three-dimension status study.

## 13. Confirmatory design preview (not frozen)

- Conditions: raw reference, direct, recursive, rewrite-matched,
  repeated-direct, source-peek.
- Writer: `qwen2.5:7b` primary; `gemma3:12b` replication after the primary
  result is stable.
- Budget: predeclare final budget and report actual lengths; do not select
  outputs into a token band.
- Outcomes: LSF, SSF, proposition identity, condition/action states; joint
  distribution reported.
- Analysis: paired trajectory-level contrasts, cluster bootstrap; no pooling
  with synthetic V3; condition-level percentages descriptive only.
- P4.2 is separate and uses curated high-stakes scenarios, not sampled chat.

## 14. What is frozen, and the freeze checklist

Frozen when calibration passes:

- this guide (hash);
- ontology and allowed values (hash);
- cue lexicon (hash; illustrative only);
- inclusion/exclusion rules;
- adjudication order;
- reliability gates;
- annotation form schema;
- analysis plan (paired estimand, cluster bootstrap, joint outcomes).

Not frozen until opened by a protocol amendment: writer models, budgets,
dataset composition, and the decision to keep or drop epistemic.

## 15. Decisions recorded (2026-11-17)

1. **Epistemic — dropped from the real-data confirmatory arm.** The screen found
   2/50 semantic epistemic propositions (5/50 by A, 3/50 by B at the label
   level). A confirmatory claim would be underpowered, and targeted elicitation
   would risk the same construct-validity objection as synthetic templates.
   Epistemic stays in the frozen synthetic V3 arm and may appear as a
   descriptive note on real data.
2. **Conditional — targeted enrichment, not a small secondary analysis.** The
   natural screen yielded only 5-6 conditional items, mostly backup or
   preference phrasing. Enrichment requires a pre-registered inclusion rule:
   condition state and action state both judgeable, and a consequence.
   Report the natural-sample descriptive base rate separately and never call
   the enriched sample a natural distribution.
3. **P4.2 — curated high-stakes scenario bank.** 40-60 scenarios across money,
   health, authorization, and commitments. Proposition content, evidence,
   task, and length matched; only the status varies (present / omitted /
   distorted). A model may draft scenarios, but humans approve, blind, and
   validate realism and manipulation before the run. The scenario-writing
   model is not the tested agent.
4. **Annotators — two independent humans are required.** The current A/B pair
   has two independent humans, but B used an AI first draft and edited it, so
   the pair is `human-reviewed-model` versus human. Obtain a model-free subset
   (YTB re-annotates 20-30 items from scratch, or a third human labels all 50)
   before claiming unaided human reliability. A third human adjudicator is
   preferred; if unavailable, use a pre-registered deterministic rule and
   report unadjudicated and adjudicated results side by side. Model assistance
   is always disclosed.
5. **Sample size — precision-based after calibration plus a pilot.** Planning
   target 150-200 usable propositions; final n set by the paired-difference SD
   from a 40-60 item pilot, targeting a CI half-width of 0.10-0.12. Reduce
   conditions before reducing items if the budget is fixed.
6. **Second domain — `longmemeval_s`, not the oracle variant.** The oracle
   haystack has 1-6 sessions (median 2); the `s` variant has 44-57 sessions.
   Use `s` for depth replication if the full split is available; use the oracle
   only as a construct check, and never as evidence about chained rewriting.

### Remaining prerequisites before freezing

- Fill A's provenance and recruit a genuine second human annotator.
- Pass a fresh 60-item calibration after the D1-D5 revisions.
- Validate the P4.2 scenario bank with two humans.
- Record the freeze hashes for the guide, ontology, cue table, form schema,
  inclusion/exclusion rules, adjudication order, and analysis plan.

## 16. Related artifacts

- Stage 1 protocol: `V3_REAL_DATA_AUDIT_PROTOCOL.md`
- Stage 1 report: `2026-11-17-real-dialogue-feasibility-audit.md`
- Screening how-to: `REAL_SCREENING_ANNOTATION_HOWTO.md`
- Frozen synthetic pilot: `V3_FINAL_FREEZE.md`
