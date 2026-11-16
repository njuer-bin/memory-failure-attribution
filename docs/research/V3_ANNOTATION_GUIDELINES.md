# V3 Blind Human Annotation Guidelines
**Status:** Draft for annotator calibration. Do not use as a frozen manual until calibration is complete.

## 1. Purpose
Evaluate whether a generated memory preserves the target proposition and accurately represents its evidence-supported state. Do not judge writing quality, helpfulness, or plausibility.

## 2. What annotators receive
For each item, annotators receive:
- the source dialogue in chronological order;
- an opaque target-proposition description that does not reveal the gold state;
- one anonymized generated memory.
They do NOT receive condition, model, prompt, gold final state, gold evidence-turn IDs, other annotations, or the expected result.

The target-proposition description must identify the semantic claim without stating its state. Example: "whether the speaker will attend the conference" rather than "the speaker has committed to attending the conference."

## 3. Label sequence
### A. Proposition identity
Choose one:
- PRESERVED
- PARTIAL
- LOST
- AMBIGUOUS

Explain which entity, relation, scope, polarity, or argument is missing if not PRESERVED.

### B. Applicable state dimensions
Mark each as APPLICABLE / NOT_APPLICABLE / CANNOT_DETERMINE:
- epistemic
- intentional
- conditional
- action/execution
- polarity/scope/time where relevant

### C. State represented in the memory
Select the best-fitting label from the ontology for each applicable dimension. Use UNEXPRESSED or UNRECOVERABLE where the memory contains no assessable state. Do not infer commitment from a future-tense phrase unless the ontology's criteria are met.

### D. Evidence support
For each represented state, choose:
- SUPPORTED_BY_DIALOGUE
- CONTRADICTED_BY_LATER_DIALOGUE
- NOT_SUPPORTED
- AMBIGUOUS
- NOT_ASSESSABLE
Provide the relevant dialogue turn IDs only if the annotation interface exposes them; otherwise quote a short identifying phrase.

### E. Final judgment
- NO_DISTORTION
- LEGITIMATE_UPDATE
- UNSUPPORTED_STATUS_DISTORTION
- STATUS_OMISSION
- PROPOSITION_LOSS
- AMBIGUOUS_UNASSESSABLE

Multiple tags may be recorded when different dimensions have different outcomes, but the primary outcome must follow the decision order in the formal definitions.

## 4. Critical distinctions
- "I might apply" is not equivalent to "I will apply."
- "I want to go" is not necessarily "I have decided to go."
- A prerequisite being satisfied does not prove the action is committed.
- "I decided to go, but the date is not fixed" remains a commitment with unresolved timing.
- A later explicit cancellation supersedes an earlier commitment.
- A later supported confirmation is a legitimate update, not drift.
- Removing a status cue is omission unless the remaining memory asserts a different state. Omission is important but must not be silently counted as a changed status.
- A shorter paraphrase is not automatically a distortion.

## 5. Handling uncertainty
Use AMBIGUOUS or NOT_ASSESSABLE when multiple readings remain plausible. Do not resolve ambiguity by guessing the writer's intent. If the dialogue itself does not determine the final state, mark the gold adjudication as underdetermined rather than inventing a state.

## 6. Independence and adjudication
Annotators work independently and cannot discuss cases before submission. After labels are locked:
1. compute raw agreement and chance-corrected agreement;
2. inspect disagreement categories;
3. adjudicate with a third reviewer using the dialogue and ontology;
4. preserve original labels and adjudication separately.
Gold state and evidence-turn annotations are created by a separate curator and hidden until the independent labels are frozen.

## 7. Quality controls
Include repeated hidden items to estimate intra-annotator consistency, clear positive/negative controls, and ambiguous controls. Do not use trick questions that rely on undocumented conventions. Report agreement by dimension and label prevalence; a single overall kappa can hide severe class imbalance.

Staged annotation budget (recommended): a 60-item calibration set first; freeze the guide and ontology; then a confirmatory set sized by the power analysis. For PATH_REPLICATE, each path is a separate anonymized item; path IDs are opaque and shuffled so annotators cannot infer the schedule. Do not annotate all paths of one trajectory consecutively.

## 8. Annotation record schema
Each record should include item_id, annotator_id, proposition_identity, applicable_dimensions, represented_state, evidence_support, primary_judgment, subtype, rationale, confidence, and optional turn references. Condition mapping and gold labels remain in a separate file.
