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

## 9. Non-claims
The ontology is a research instrument, not a universal theory of belief or intention. Labels must be revised if calibration reveals systematic ambiguity. No claim of psychological access to a speaker's true internal state is made; the target is the state communicated in the dialogue.
