# How to Annotate the 50-Item Real-Dialogue Screening Set

This is a feasibility screen, not a hypothesis test. You are answering: does
this span contain a status that could be measured, and is the evidence enough
to label it later? Do not try to answer the research question.

## Files and independence

- Annotator A fills `screening_A.csv`; annotator B fills `screening_B.csv`.
- Do not open the other annotator's file. Do not open `diagnostic_read.csv`
  until both files are complete; it is a model read, not a gold label.
- Do not edit any column other than the ten rating columns.
- Save as UTF-8 CSV. Leave no rating cell blank; if unsure, use
  `ambiguous`/`unknown` and explain in `notes`.

## Workflow per row (about 1.5-2.5 minutes)

1. Read `target_sentence`, then `context`; the target turn is marked `>>`.
2. Write the proposition P in your head (or in `notes`) as:
   "Speaker [status] that [specific action or fact]."
3. Decide `status_bearing` first; if `no`, set `dimension=none`,
   `proposition_clear=no`, and leave `semantic_labelable=no`. You still fill
   the rest as specified below.
4. If `status_bearing=yes`, assign the semantic `dimension` (not the word that
   triggered the match), then the remaining fields.
5. Use the decision order below. Do not reorder it per item.

## Field definitions and allowed values

Use these exact values (lowercase).

### `status_bearing`
- `yes` — the span expresses a determinable relation between the speaker and a
  specific proposition: a degree of certainty (epistemic), a commitment to a
  future action (intentional), or an action contingent on a condition
  (conditional).
- `ambiguous` — a relation is suggested but the proposition or its status is
  underdetermined by the evidence.
- `no` — opinion, advice, values, emotion, generic encouragement, past
  evaluation, third-party state, or a status word used incidentally.

### `dimension` (semantic, not lexical)
- `epistemic` — how certain the speaker is about a factual proposition:
  "I think I got the price wrong", "not sure whether the tank can be seeded".
- `intentional` — the speaker's consideration, plan, commitment, execution, or
  cancellation of a future action: "I'm thinking of registering", "I booked a
  trip".
- `conditional` — the action's status depends on a condition: "If I need more
  accuracy, I can upgrade later", "just in case it rains".
- `mixed` — two dimensions jointly carry the status ("I'll think about it and
  maybe get a pet if I'm not allergic"). Note the pair in `notes`.
- `none` — no status proposition.

Key rule: **"I think I'll X" is intentional, not epistemic.** The "think"
hedges commitment strength. **"I think X happened / X is true" is epistemic.**

### `proposition_clear`
- `yes` — you can state the status-bearing proposition as one testable claim
  with a concrete action, object, or fact.
- `no` — the claim is too vague to test ("make my plan work", "keep finding
  ways to do good"), or there is no status proposition.

### `evidence_sufficient`
- `yes` — a third annotator seeing only this context could assign the gold
  status without guessing.
- `partial` — the status is inferable but its strength, time, or condition is
  ambiguous.
- `no` — the context does not support a status label.

### `lexical_cue_present`
- `yes` — the **target sentence itself** contains an explicit status word or
  phrase ("I think", "maybe", "I'm planning", "if").
- `no` — the status would have to be inferred from context alone.
This field is about the source sentence, not the context and not the memory.

### `lexical_labelable`
- `yes` — a pre-defined cue lexicon would produce a stable status label for
  this proposition (cue present and not misleading).
- `no` — no cue, or the cue is incidental/misleading (e.g., "I think schools
  should be funded" is a stance, not an epistemic status of a fact).

### `semantic_labelable`
- `yes` — a careful reader could assign the status from meaning, even if the
  wording is paraphrased later.
- `no` — the meaning does not determine a status, or the proposition is not
  recoverable.

### `update_present`
- `yes` — a later session in the provided material changes the status; quote
  the change in `notes`.
- `no` — a later mention exists and the status is unchanged.
- `unknown` — no later mention is available; absence of evidence is not a
  status change.

### `difficulty_1_3`
- `1` — straightforward after one reading.
- `2` — needs re-reading or a boundary call.
- `3` — genuinely ambiguous or the guide does not decide it.

### `notes`
One line: the proposition P, the status you assigned to it, and any boundary
reason. Example: `P=attend conference this month; I=COMMITTED; cue "going to"`.

## Decision order (apply in this order)

1. Is there a specific proposition about the speaker's own action, state, or
   belief? If not → `status_bearing=no`.
2. Can you state it as one testable claim? If not → `proposition_clear=no`.
3. Does the context let you assign a status without guessing? If not →
   `evidence_sufficient=partial` or `no`, and `status_bearing=ambiguous`.
4. What semantic dimension is the status? Ignore which word matched.
5. Is there an explicit cue in the target sentence? (`lexical_cue_present`)
6. Could a cue lexicon label this reliably? (`lexical_labelable`)
7. Could a human label the meaning even if paraphrased? (`semantic_labelable`)
8. Is there a later session? If yes, does it change the status?
   (`update_present`)
9. How hard was the call? (`difficulty_1_3`)

## Worked examples

1. **RD-013** "I'm going to a transgender conference this month."
   `status_bearing=yes, dimension=intentional, proposition_clear=yes,
   evidence_sufficient=yes, lexical_cue_present=yes,
   lexical_labelable=yes, semantic_labelable=yes, update_present=unknown,
   difficulty_1_3=1`.
   P = attend a conference this month; status = committed/planned.

2. **RD-029** "I think I got the price from my friend wrong, yeah it's actually
   $10..."
   `yes, epistemic, yes, yes, yes, yes, yes, yes, 2`.
   P = the train price is $10; status = corrected/established. This is a genuine
   epistemic self-correction.

3. **RD-028** "If I find that I need more accuracy or features, I can always
   upgrade to a basic GPS device later."
   `yes, conditional, yes, yes, yes, yes, yes, unknown, 1`.
   Condition = needing more accuracy; action = upgrade. Both are stated.

4. **RD-021** "I'm open to any type of accommodation as long as it's safe and
   clean."
   `no, none, no, no, yes, no, no, unknown, 3`.
   This is a preference, not a condition on the speaker's action.

5. **RD-009** "Going to those places is definitely on my to-do list."
   `ambiguous, intentional, yes, partial, yes, yes, no, unknown, 2`.
   An intention is suggested, but a to-do list is not a commitment; the guide
   cannot decide committed vs considering.

6. **RD-006** "I think schools and infrastructure should be funded properly."
   `no, none, no, no, yes, no, no, unknown, 3`.
   "I think" marks a normative stance, not the epistemic status of a fact.

## Hygiene and provenance

- Work independently; do not discuss items before both files are complete.
- Record your provenance in `screening_provenance_A.json` or
  `screening_provenance_B.json` (copy the template):
  `{"annotator": "A", "role": "human", "date": "YYYY-MM-DD", ...}`.
  If a model assists any item, mark that item in `notes` as `model-assisted`.
- Do not infer the condition or the hypothesis from item order; the sheet is
  ordered by dataset and marker dimension, but item order carries no condition
  label or gold status.
- If you change a label after re-reading, keep the final value; do not leave
  history in the file.

## What happens next

Both files are joined on `candidate_id`; raw agreement and Cohen's kappa are
computed per field; disagreements are adjudicated in the pre-registered order
in `V3_REAL_DATA_AUDIT_PROTOCOL.md`; only then are the Stage 2 gates evaluated.
