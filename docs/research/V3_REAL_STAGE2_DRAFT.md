# Stage 2 Draft v2.4 — Real-Dialogue Status Fidelity Annotation and Calibration

Status: **DRAFT v2.4, not frozen.** Revised after the 50-item screening, the
60-item gold calibration, two 40-item runs, and the failed LSF/SSF calibration.
The LSF/SSF failure (LSF raw 0.733 / κ 0.581; SSF raw 0.578 / κ 0.432) came from
generator target drift and an underspecified cue/SSF boundary. v2.4 adds a cue
lexicon, an SSF decision tree, proposition-identity examples, and a target-focus
rule for the generator. Do not freeze or run confirmatory generation yet.

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

## 8b. v2.1 calibration revisions (2026-11-18)

The 60-item gold calibration failed (`2026-11-18-stage2-calibration-result.md`).
The disagreements cluster into four rules; these are now binding.

### `E0` encoding

If `gold_dimension=E0`, then `gold_status=N/A`, `gold_condition_state=N/A`,
`gold_action_state=N/A`, and `gold_strength=N/A`. Never use `NOT_EXPRESSED`
for an `E0` item. `NOT_EXPRESSED` is only for a non-`E0` intentional item where
no intention is expressed.

### Desire vs intention

- "I want to X", "I'd like to X", "I'm interested in X" → `INTERESTED`.
  A bare desire is not a plan and not a commitment.
- "I plan to X", "I intend to X", "I'm going to X" → `INTENDING`.
- "I'm thinking of X", "I'm considering X", "I might X" → `CONSIDERING`.
- `COMMITTED` only with an explicit decision, booking, registration, payment,
  or equivalent commitment cue.
- If a desire is accompanied by a concrete plan or step, code `INTENDING` and
  quote the plan. Do not upgrade a desire to `INTENDING` on context alone.

### `EXECUTING`

- Use `EXECUTING` only when the action is already under way: "I'm trying to X",
  "I've been X-ing", "I started X".
- "I'm going to keep X-ing" → `INTENDING`.
- "I want to keep X-ing" → `INTERESTED`.

### Conditional boundary

- Conditional status is about the speaker's own action contingent on a factual
  prerequisite. Both the condition state and the action state must be judgeable.
- Offers or advice to the interlocutor ("let me know if you need someone to
  talk to", "if I can do anything to help") and generic conditionals about the
  world ("we can have great experiences if we take risks") are `E0`, not
  conditional.
- If either the condition or the action is not judgeable, use `E0`; do not fill
  only one state.

### Own-action wondering

- "I'm wondering if I could X", where X is the speaker's own action → intentional
  `CONSIDERING`, not epistemic.
- Epistemic applies when the uncertainty is about a factual proposition, not
  about whether the speaker will act.

### Strength and confidence anchors

- `gold_strength=weak`: hedged desire or possibility, no plan.
- `moderate`: stated plan, or ongoing consideration.
- `strong`: explicit decision/commitment, or a completed action.
- `gold_confidence=high`: the evidence directly states the status with an
  explicit cue.
- `medium`: the status is inferred from context, or the plan is implied.
- `low`: ambiguous or a boundary case.

### `target_proposition`

Write one English sentence in the form "The speaker [status] [action/object]".
Do not write commentary, Chinese translations, or multiple propositions. Free
text is not agreement-gated, but a consistent form makes adjudication cheaper.

## 8c. v2.2 worked examples and target-proposition rule (2026-11-18)

The 40-item calibration failed because four v2.1 rules were not applied. These
examples are binding; apply them before the next calibration run.

| Sentence | Label | Why |
|---|---|---|
| "I think I'll go with the fruit chaat." | intentional `INTENDING`, moderate | "I think I'll" is hedged; not a decision, so not `COMMITTED`. |
| "I'm going to try making it tonight." | `INTENDING`, moderate | "try" states an intention; not a decision, so not `COMMITTED`. |
| "I'd like to find a more challenging route." | `INTERESTED`, weak/moderate | Desire, no plan; not `INTENDING`. |
| "I want to live authentically and help others do the same." | `INTERESTED` | Desire/values, no plan; not `INTENDING`. |
| "I'm going to keep chasing my dreams and working hard." | `INTENDING` | Resolve, not an action already under way; not `EXECUTING`. |
| "I'm trying to improve my data analysis skills." | `EXECUTING` | Action already under way. |
| "I have to go, bye!" | `E0`; all status fields `N/A` | No status proposition about a future action. |
| "I'm gonna keep writing, but if acting calls out I might give it a try." | target P = keep writing; `INTENDING`; note the secondary conditional | One target proposition; the "if acting" clause goes in `notes`. Do not code `mixed`. |
| "I'm trying to juggle my engineering, relationship, and growing as a person." | `E0` if the proposition is vague/emotional; `EXECUTING` only if it names an ongoing action | Choose one reading and explain the boundary in `notes`. |

**Target-proposition rule.** One item = one target proposition, usually the main
clause. If a sentence has a main action plus a secondary conditional or
emotional clause, code the main action and put the secondary clause in `notes`.
Use `mixed` only when the **same** proposition independently carries two status
dimensions (for example, a factual claim with both epistemic uncertainty and an
intentional commitment). If the second dimension is a condition, use
`conditional`; if it is background, use the primary dimension and note it.

**Strength anchors.** `weak` = desire, hedge, or possibility with no plan;
`moderate` = stated plan or intention; `strong` = explicit decision,
commitment, booking, payment, or completed action.

## 8d. v2.3 boundary examples (2026-11-18)

Run 2 passes `gold_status` but fails `gold_dimension` on three items. These
rules are binding.

### Instructions to the assistant / roleplay

"I will provide some details about the app and it will be your job to write up a
detailed statement..." is an instruction to the assistant, not the speaker's own
status. Code `E0`. Only the speaker's own action, state, or belief is a status
proposition.

### Past or emotional musing

"I think about my life too sometimes ... felt like writing a drama" is past
emotion/musing, not a current or future action status. Code `E0`. A status
requires a current or future action/state, or an explicit commitment; "felt
like" is a past feeling.

### "I've managed to X"

- If X is the speaker's own action, code intentional `COMPLETED`.
- If the item is a factual claim about a state or the world, code epistemic
  `SUPPORTED` or `ESTABLISHED`.
- If both are present, code the action and put the factual claim in `notes`.
  Do not use `mixed` unless both dimensions independently carry the same
  proposition.

### Rule of thumb

If the sentence is about the assistant's task or a past emotion, `E0`. If it is
about the speaker's own future or past action, intentional. If it is about the
truth of a factual claim, epistemic.

## 8e. v2.4 cue lexicon and LSF/SSF decision tree (2026-11-18)

The LSF/SSF calibration failed because the guide did not map common paraphrases
to status types and did not define the `UNDERSPECIFIED` vs `DISTORTED` boundary.
These rules are binding.

### Cue lexicon (canonical type)

| Cue | Canonical status type |
|---|---|
| "thinking of/about", "considering", "might", "maybe", "wondering whether to" | `CONSIDERING` |
| "want to", "would like to", "interested in", "hope to" | `INTERESTED` (a bare desire; "hope to" is not `COMMITTED`) |
| "plan to", "intend to", "going to", "will" (future action), "planning to", "aim to" | `INTENDING` |
| "decided", "committed", "booked", "signed up", "registered", "paid", "promised", "chose" (a decision) | `COMMITTED` |
| "trying to", "currently X-ing", "have been X-ing", "started", "in the process of" | `EXECUTING` |
| "managed to", "finished", "completed", "did", "have done" | `COMPLETED` |
| "sure", "probably", "possibly", "likely", "established", "confirmed" | epistemic |
| "if", "unless", "in case", "as long as", "depending on" | conditional |

"I think I'll X" is a hedged `INTENDING` cue, not an epistemic cue. "Will" is
`INTENDING` unless a decision/booking cue makes it `COMMITTED`.

### LSF decision

1. Determine the evidence-supported status type.
2. Find the status cue in M.
3. Same type → `CUE_PRESERVED`.
4. Different type or materially different strength → `CUE_ALTERED`.
5. No cue → `CUE_ABSENT`.
6. Source had no cue → `NOT_APPLICABLE`.

### SSF decision tree

1. If proposition identity is `LOST` or `AMBIGUOUS`, `SSF=UNASSESSABLE`.
2. Assign the status type M implies, using the cue lexicon and semantics.
3. Same type as the evidence status, or a paraphrase with the same action
   implication → `SEMANTIC_CORRECT`.
4. M permits the evidence status but does not determine it → 
   `SEMANTIC_UNDERSPECIFIED`.
5. M implies an incompatible status → `SEMANTIC_DISTORTED`.
   Incompatible means the action authorization changes:
   `CONSIDERING`/`INTERESTED` vs `COMMITTED`/`EXECUTING`/`COMPLETED`;
   `INTENDING` vs `COMPLETED`; condition satisfied vs unsatisfied.
   A weaker cue within the same authorization family (e.g., `INTENDING` vs
   `COMMITTED` where both authorize the same action) is `UNDERSPECIFIED`, not
   distortion.
6. A missing cue alone is not distortion. If M still implies the same status,
   it is `CORRECT`.

### Proposition identity

- `PRESERVED`: action + object + person recoverable.
- `PARTIAL`: one core element (action, object, person, condition) is missing.
- `LOST`: only a topic/entity remains, no recoverable action.
- `AMBIGUOUS`: cannot decide.

Examples: "write a blog post about journaling" → `PRESERVED`; "write about
journaling" (object missing) → `PARTIAL`; "journaling" (topic only) → `LOST`.

### `UNASSESSABLE`

Use `UNASSESSABLE` when the proposition is lost/ambiguous in M or E is
insufficient. Do not use it merely because the status cue is absent; a memory
without a cue can still be `UNDERSPECIFIED` or `CORRECT` by implication.

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
  reliability; the 25-item subset is in
  `results/status_drift_v3_real_audit/model_free_25/`.
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

- Fill the 25-item model-free re-annotation subset
  (`results/status_drift_v3_real_audit/model_free_25/`); A's screening
  provenance is recorded. Recruit a third human adjudicator if available.
- Pass a fresh 60-item calibration after the D1-D5 revisions.
- Validate the P4.2 scenario bank with two humans.
- Record the freeze hashes for the guide, ontology, cue table, form schema,
  inclusion/exclusion rules, adjudication order, and analysis plan.

## 16. Related artifacts

- Stage 1 protocol: `V3_REAL_DATA_AUDIT_PROTOCOL.md`
- Stage 1 report: `2026-11-17-real-dialogue-feasibility-audit.md`
- Screening how-to: `REAL_SCREENING_ANNOTATION_HOWTO.md`
- Frozen synthetic pilot: `V3_FINAL_FREEZE.md`
