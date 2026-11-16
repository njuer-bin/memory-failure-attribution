# Status Drift v2.4 — Human Annotation Guide

## Purpose

Annotate whether a compressed memory preserves the target proposition and its status, using the full original dialogue as the evidence source. Annotators must not infer missing information from common sense.

## Unit of annotation

One row = one trajectory × one condition × one depth × one annotator.

For each row, read:
1. the full original dialogue;
2. the target proposition and dimension;
3. the specific memory output being evaluated.

Annotators work independently before discussion. Do not inspect the other annotator's labels.

## Step 1 — Proposition identity

Choose exactly one:
- PRESERVED: same target proposition and essential relation remain recoverable.
- PARTIAL: target is identifiable, but a material argument, relation, object, or scope is missing.
- LOST: target proposition cannot be recovered.
- AMBIGUOUS: memory supports multiple materially different interpretations.

A keyword/topic mention alone is not preservation. For conditional examples, the condition-to-action relation is part of the proposition. For intentional examples, distinguish the intention from the action itself.

## Step 2 — Polarity and status

Annotate only the applicable dimension, but use the other fields to avoid conflation.

- Epistemic status describes certainty about the proposition, not whether the user intends to act.
- Intention status describes the user's commitment toward an action. COMMITTED does not mean the action has been executed.
- Action status describes execution progress. COMPLETED does not automatically imply the user had explicitly committed in the original dialogue.
- Condition status describes whether the prerequisite is unknown, unsatisfied, satisfied, or invalidated. It must not be inferred from whether the downstream action is being considered.

If a field is not relevant, use NOT_APPLICABLE; if the memory does not permit a decision, use UNCLEAR or UNKNOWN as appropriate.

## Step 3 — Evidence and unsupported drift

Use the full dialogue to identify the evidence turns supporting the final gold state. Record turn IDs, not invented explanations.

Set unsupported_status_change=YES only when:
1. proposition identity is PRESERVED;
2. the memory expresses a status different from the evidence-supported final status; and
3. no later dialogue evidence supports the memory's status.

Set NO when the status is faithful or the apparent change is a legitimate update supported by later turns. Set UNCLEAR when proposition identity or status cannot be resolved.

Do not label omission as status drift. Do not treat legitimate user change of mind, progress, cancellation, or completion as compression error when the dialogue supports it.

## Step 4 — Adjudication and reliability

Two annotators independently label the initial reliability set. Calculate raw agreement and Cohen's kappa for each categorical field separately. Discuss disagreements only after independent annotation; preserve both original labels and record the adjudicated label in a separate column/file.

Report the number of UNCLEAR and AMBIGUOUS cases. Do not silently discard them. If agreement is poor, revise the guide and re-annotate before making claims.

## Controlled pilot caution

The synthetic data are intentionally simple and cannot establish performance on natural dialogue. Human annotations validate the measurement on these examples only; they do not establish generalization or novelty.
