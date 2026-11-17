# V3 Formal Definitions and Label Ontology
**Status:** Draft for calibration; not yet frozen.

## 1. Evidence trajectory
A trajectory is a chronologically ordered dialogue segment D = (u1, ..., un), together with a target proposition p and the subset of turns E(p) that support, qualify, update, or contradict its state. A trajectory may include irrelevant distractors. Evidence-turn IDs are maintained separately from annotator-facing material during blind labeling.

## 2. Proposition identity
Proposition identity concerns whether the memory still refers to the same claim, not whether its status is correct.
- PRESERVED: the same target proposition and its essential arguments remain recoverable.
- PARTIAL: the topic or a subset remains, but an argument, scope, entity, or relation needed to identify the claim is missing.
- LOST: the target proposition cannot reasonably be recovered.
- AMBIGUOUS: multiple interpretations remain plausible and cannot be resolved from the memory alone.

Annotators must not use status wording as proof of proposition identity.

## 3. State representation
Represent a state as a typed tuple rather than one undifferentiated label:
S(p,t) = (epistemic, intentional, conditional, action, polarity, scope, time).
Not every dimension applies to every proposition. Non-applicable dimensions are N/A, not UNKNOWN.

### Epistemic state
Draft ordered labels:
- UNKNOWN: dialogue does not establish the speaker's epistemic position.
- POSSIBLE: explicitly possible or under consideration as a factual belief.
- PROBABLE: expressed as likely but not established.
- SUPPORTED: evidence or explicit assertion supports the proposition, but certainty is not warranted.
- ESTABLISHED: explicitly confirmed or established by authoritative evidence within the dialogue.
- REJECTED: explicitly denied or disconfirmed.
Annotate speaker/source and scope where relevant. Do not infer certainty from confident writing style alone.

### Intentional state
- NOT_EXPRESSED: no intention is expressed.
- CONSIDERING: evaluating or contemplating.
- INTERESTED: expresses preference or desire but no commitment.
- INTENDING: states an intention or plan.
- COMMITTED: explicit decision or commitment.
- EXECUTING: action has begun.
- COMPLETED: action completed.
- CANCELLED: prior intention/commitment explicitly cancelled.
- NOT_INTENDED: explicitly says the action is not intended.
These labels are not assumed to form a simple linear scale. For example, COMPLETED and CANCELLED are distinct terminal states.

### Conditional state
Store condition and action separately:
- condition_status ∈ {UNKNOWN, ACTIVE_UNSATISFIED, SATISFIED, FAILED, WAIVED, NOT_APPLICABLE}
- action_status ∈ {NOT_EXPRESSED, CONSIDERING, INTENDING, COMMITTED, EXECUTING, COMPLETED, CANCELLED}
A satisfied prerequisite does not automatically imply that the action is committed or executed.

## 4. Legitimate state transition
A transition S_t → S_t+1 is legitimate only when supported by later dialogue evidence that explicitly changes, clarifies, or resolves the relevant state. A later correction, cancellation, qualification, or reversal is legitimate when attributable to evidence in the trajectory. Recency alone is not evidence.

## 5. Unsupported status distortion
A memory exhibits unsupported status distortion only if:
1. proposition identity is PRESERVED;
2. at least one applicable state dimension differs from the evidence-supported final state;
3. the difference is not supported by any later dialogue evidence;
4. the difference is not merely an allowed paraphrase or annotation ambiguity.

Subtypes:
- Escalation: weaker/uncertain state becomes stronger/more certain without support.
- Attenuation: stronger state becomes weaker/less certain without support.
- Commitment inflation: consideration/interest is represented as intention or commitment.
- Commitment deflation: intention/commitment is represented as mere consideration or omitted.
- Conditional collapse: condition state and action state are conflated.
- Polarity/scope distortion: negation, scope, or target changes while superficially similar wording remains.
- Temporal distortion: a past or superseded state is represented as current.

## 6. Distinguishing omission from distortion
If proposition identity is LOST, record proposition loss; do not count status drift.
If identity is PARTIAL, record partial loss and separately indicate whether any status claim is still assessable. Primary analysis should not silently include PARTIAL cases in the PRESERVED denominator.
If identity is PRESERVED but status is absent, distinguish:
- status omitted but recoverable from memory context;
- status omitted and not recoverable;
- status ambiguous.
The main drift outcome requires an unsupported status change, not merely missing a cue. A separate status-omission outcome is reported.

## 7. Evidence traceability
For every final-state label, the gold dataset stores:
- target proposition ID;
- final state tuple;
- supporting/contradicting turn IDs;
- update type (stable / strengthen / weaken / commit / cancel / complete / condition change / reverse);
- adjudication note.
Annotators do not see these fields before independent annotation.

## 8. Annotation decision order
1. Is the target proposition identifiable?
2. Which state dimensions apply?
3. What state is represented in the memory?
4. Is the represented state supported by the dialogue evidence?
5. Is any difference a legitimate update, a paraphrase, omission, ambiguity, or unsupported distortion?
This order reduces hindsight leakage from the gold state.

## 9. Path and path divergence

A transformation path is the ordered sequence of writer calls and intermediate
budgets applied to a trajectory, ending at a fixed final budget. A path is not
the same as a condition: one condition may admit multiple paths.

For a trajectory and condition, let the final memories of P paths be
m_1,...,m_P. For each applicable state dimension d, define the path state set
S_d = { state(m_i, d) } over paths whose proposition identity is PRESERVED.

- **Pairwise divergence:** fraction of path pairs whose state differs,
  averaged over applicable dimensions.
- **Dispersion:** number of distinct states in S_d minus 1.
- **Path-dependence index:** 1 − max_state_share (0 = all paths agree; higher =
  more path-dependent), reported per dimension.

Paths with proposition identity LOST/PARTIAL/AMBIGUOUS are excluded from S_d and
reported separately. A condition whose path divergence is driven mostly by
proposition loss is not evidence for status path dependence.

## 10. Ontology convergence for the confirmatory study

The rich ontology is for calibration and descriptive analysis. Before the
confirmatory run, labels that cannot be applied reliably (e.g., POSSIBLE vs
PROBABLE vs SUPPORTED, or INTENDING vs COMMITTED) must be collapsed to 2–3
mutually exclusive categories per dimension, with the mapping and reliability
reported. The confirmatory ontology is frozen together with the protocol.

## 11. Non-claims
The ontology is a research instrument, not a universal theory of belief or intention. Labels must be revised if calibration reveals systematic ambiguity. No claim of psychological access to a speaker's true internal state is made; the target is the state communicated in the dialogue.

## 12. Confirmatory ontology v3.2.1 (collapsed)

The rich ontology in §3 is for calibration and descriptive work. The
confirmatory study uses **one primary dimension per item** and 2–3 labels per
dimension:

- EPISTEMIC: `POSSIBLE` / `ESTABLISHED` / `UNKNOWN`
- INTENTIONAL: `CONSIDERING` / `COMMITTED` / `UNKNOWN`
- CONDITIONAL: `CONDITION_ACTIVE` / `CONDITION_SATISFIED` / `UNKNOWN`
- ACTION: `ACTION_NOT_STARTED` / `ACTION_STARTED` / `UNKNOWN`
- plus `NOT_EXPRESSED` and `UNRECOVERABLE` for omission.

### Proposition identity unit (v3.2)

Proposition identity is scored over the **target predicate plus its essential
arguments**. Modality, condition relation, and state labels are *not* part of
identity. For a conditional trajectory the target proposition is the action
(e.g. `购买电脑`), not the full "if condition, then action" sentence. A topic
label without the target predicate is `PARTIAL`; in the primary outcome every
`PARTIAL` is scored as `PROPOSITION_LOSS` and reported separately.

### Applicability rule

Choose the single dimension the target proposition is primarily about:

- EPISTEMIC: whether something is true, confirmed, or uncertain.
- INTENTIONAL: the speaker's commitment to a future action.
- CONDITIONAL: whether a prerequisite is met; action state is separate and is
  scored only if the memory explicitly asserts it.
- ACTION: execution progress of an already-committed action.
- CANNOT_DETERMINE: the memory supports two incompatible readings.

If two dimensions seem applicable, choose the one the dialogue's update turns
are about; record the other in `rationale`.

### Status expression (v3.2)

A status is expressed only with an explicit lexical cue. An unmarked action
verb records the action but does not assert its state; a bare topic noun does
not assert a condition state. Juxtaposition (`奖学金购机`) is not a cue for
condition satisfied or action committed.

### Conditional scoring (v3.2.1)

Store condition and action separately. When `CONDITIONAL` is the primary
dimension, `expressed_status` records the **condition state only**. The action
state is recorded in a separate required field, `action_status` ∈
{`NOT_EXPRESSED`, `CONSIDERING`, `COMMITTED`, `UNKNOWN`, `NOT_APPLICABLE`}.
A bare action verb is not a cue.

- A condition state expressed without an explicit acquisition or satisfaction
  cue is `STATUS_OMISSION`, not distortion.
- A satisfied condition with an unexpressed action state is `NO_DISTORTION` on
  the condition dimension.
- An explicit `action_status = COMMITTED` when the dialogue only supports
  `CONSIDERING` is `UNSUPPORTED_STATUS_DISTORTION` (`CONDITIONAL_COLLAPSE`),
  even if the condition state is correct.

### Judgment order (v3.2.1)

1. `PROPOSITION_LOSS` — identity `LOST` or `PARTIAL`.
2. `LEGITIMATE_UPDATE` — later supported change represented **as a change**
   (explicit marker, or an ordered chain retaining both states).
3. `UNSUPPORTED_STATUS_DISTORTION` — an applicable dimension explicitly asserts
   an unsupported state (condition or action).
4. `STATUS_OMISSION` — the primary dimension has no explicit status cue and no
   dimension is distorted.
5. `NO_DISTORTION` — expressed statuses match the final state.
6. `AMBIGUOUS_UNASSESSABLE` — unresolvable.

Steps 2 and 3 precede omission and no-distortion so that a supported update is
not hidden by `NO_DISTORTION` and an unsupported action escalation is not
hidden by `STATUS_OMISSION`.

### NO_DISTORTION vs LEGITIMATE_UPDATE

- `NO_DISTORTION`: the memory's status matches the evidence-supported final
  state, even if the dialogue contained an update. A memory that simply states
  the final state is `NO_DISTORTION`.
- `LEGITIMATE_UPDATE`: the memory explicitly represents a later supported change
  as a change (e.g., "was considering, now decided", or an ordered chain
  retaining both states) and is faithful.

### STATUS_OMISSION vs UNSUPPORTED_STATUS_DISTORTION

- `STATUS_OMISSION`: no status is asserted or recoverable; there is no
  conflicting state.
- `UNSUPPORTED_STATUS_DISTORTION`: a different status is asserted, and no later
  dialogue evidence supports it.
