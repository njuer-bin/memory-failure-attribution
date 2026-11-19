# Real-Dialogue Proposition Identity and Status Coding (v2.5)

Status: proposed rule for a fresh calibration set, 2026-11-18. This replaces
the v2.4 rule that failed the LSF/SSF calibration. It is frozen before any
memory generation and before any model-assisted labelling.

## 1. Unit of analysis

The **target proposition** is the action predicate and its key arguments in the
target utterance:

- the action predicate (e.g., *write*, *cancel*, *book*, *ask for advice*);
- the key arguments needed to identify the action: agent, object/patient,
  recipient, amount, and any date or condition that is part of the action;
- the speech-act type (statement, plan, request, question, promise).

The **status** is the intentional, epistemic, or conditional state attached to
that proposition: `NOT_EXPRESSED`, `CONSIDERING`, `INTENDING`, `COMMITTED`,
`EXECUTING`, `COMPLETED`, `CANCELLED`, `NOT_INTENDED`; for conditional
propositions, the condition state and the action state are coded separately.

## 2. Proposition identity

Compare a memory `M` to the target proposition `P`.

| Label | Rule |
|---|---|
| `PRESERVED` | `M` entails the same action predicate with the same key arguments, and the same speech-act type. Lexical paraphrase, pronoun/tense normalization, and omission of non-essential modifiers are allowed. |
| `PARTIAL` | `M` keeps the object or topic but weakens or generalizes the action predicate, or drops a key argument needed to identify the action. The action is still recognizable but no longer the same proposition. |
| `LOST` | `M` replaces the action with a different action or speech act, or the target proposition is no longer recoverable. |

**Hard rule.** A change in the action predicate or speech act is never a status
omission. If the memory turns "I'll start writing about my journaling routine"
into "the user asks for advice on structuring a blog post", the action changed
from *writing* to *asking for advice*; code `LOST` (or `PARTIAL` only if the
object is retained and the action is merely generalized), never
`STATUS_OMISSION`.

## 3. Status outcome (only for `PRESERVED`)

| Label | Rule |
|---|---|
| `FAITHFUL` | The status expressed in `M` matches the gold status at the memory's time. |
| `STATUS_OMISSION` | `M` preserves the proposition but does not express the status; it is a bare topic mention or a generic reference. |
| `UNSUPPORTED_STATUS_DISTORTION` | `M` expresses a status that is stronger or different from the source at that time, with no supporting turn. |
| `LEGITIMATE_UPDATE` | `M` expresses a new status that is supported by a later source turn. Cite the update turn. |
| `AMBIGUOUS` | The evidence does not decide between the labels. |

If identity is `PARTIAL` or `LOST`, do **not** code status omission or
distortion. Code `PROPOSITION_LOSS` at the outcome level. This is the v2.5
change that resolves the second LSF/SSF failure.

## 4. Boundary examples

1. **Status omission.** Target: "I'm still comparing standing desks ... I'm
   not sure yet." Memory: "The user mentioned buying the Fully Jarvis standing
   desk." Identity `PRESERVED`; status `CONSIDERING` is absent; outcome
   `STATUS_OMISSION`.
2. **Unsupported distortion.** Same target. Memory: "The user has decided to
   buy the Fully Jarvis standing desk." Identity `PRESERVED`; status is
   strengthened; outcome `UNSUPPORTED_STATUS_DISTORTION`.
3. **Proposition loss.** Target: "I'll start writing about my journaling
   routine." Memory: "The user asks for advice on structuring a blog post."
   The action changes from writing to asking for advice; outcome
   `PROPOSITION_LOSS`, not omission.
4. **Legitimate update.** Target: "I'm thinking about cancelling my gym
   membership." Later turn: "I cancelled it this morning." Memory: "The user
   cancelled the gym membership." Outcome `LEGITIMATE_UPDATE`; cite the later
   turn.

## 5. Annotation protocol

- Two annotators label every item independently.
- No model-prefilled labels, no automatic cue columns, no shared draft.
- Label `target_proposition`, `action_predicate`, `key_arguments`,
  `identity`, `gold_status`, `outcome`, `evidence_quote`, and `confidence`.
- Report **pre-adjudication** raw agreement and Cohen's kappa for every field.
- Adjudicate only after reliability is computed; preserve both original label
  sets and the adjudication record.
- Freeze the rule only if `identity` kappa is at least 0.80 and `outcome`
  kappa is at least 0.70. Do not lower the gate after seeing the result.
- If the gate fails, stop the real-dialogue confirmatory arm and report the
  measurement failure. Do not generate memories on an unreliable instrument.

## 6. Scope

The fresh calibration is restricted to **intentional** status. Conditional and
epistemic status are not part of this calibration; the existing synthetic line
covers all three dimensions.
