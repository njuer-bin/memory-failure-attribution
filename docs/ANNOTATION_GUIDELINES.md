# Annotation Guidelines: Query-Specific Evidence Roles and Necessity

> **Version:** 0.1-draft
> **Purpose:** Five-question LoCoMo dry run; definitions may change before confirmatory annotation.
> **Annotators:** Two independent annotators, followed by adjudication.
> **Blinding:** Annotators must not see model outputs or deletion-condition results.

## 1. Annotation unit

The unit is not a memory item in isolation. It is a tuple:

(conversation_id, question_id, question, reference_answer, candidate_evidence_set)

All labels are query-specific. The same turn may be Direct evidence for one question, Bridge evidence for another, and irrelevant to a third.

The raw dialogue is the source of truth. Benchmark-provided evidence IDs are candidate evidence pointers, not unquestionable gold labels.

## 2. Required annotation sequence

For every question, complete the following in order:

1. **Question/reference audit:** Does the reference answer answer the exact question? Is it fully supported by the cited dialogue?
2. **Answer decomposition:** Split a list or compound answer into atomic answer slots.
3. **Evidence atomization:** Split each cited turn into atomic factual units if it contains more than one fact.
4. **Minimal sufficient set:** Identify the smallest admissible evidence set that supports every answer slot.
5. **Role annotation:** Label each evidence unit's function independently of necessity.
6. **Necessity annotation:** Perform remove-one tests and identify alternative paths.
7. **Dependency annotation:** Add only defensible derivation/dependency edges.
8. **Uncertainty:** Mark unsupported, ambiguous, or unresolvable cases; do not force labels.

Do not use world knowledge to repair missing conversational evidence. If the benchmark answer requires outside knowledge, mark the evidence as insufficient for this study's memory-grounded setting.

## 3. Evidence role ontology

### DIRECT

A memory unit directly states or entails an answer slot. For list/aggregation questions, several Direct units may each support different slots.

### BRIDGE

A memory unit provides an intermediate relation, entity resolution, temporal anchor, or state transition needed to connect other evidence to an answer slot. It is not simply a fact that happens to be old or far from the answer in the conversation.

### BACKGROUND

A unit provides context but is not used by the minimal derivation and is not needed to disambiguate the answer.

### IRRELEVANT / DISTRACTOR

A unit does not support the answer. It may be topically related or misleading.

### MULTI_ROLE / UNCERTAIN

Use when a unit has multiple defensible functions or the role cannot be decided. Record a rationale. Do not force a single label to inflate agreement.

**Important:** Bridge is a functional label, not a graph-centrality score. Do not define Bridge as “high degree,” “many descendants,” or “high betweenness”; those are structural properties to measure separately.

## 4. Evidence necessity ontology (independent of role)

### NECESSARY

Removing the unit makes at least one required answer slot unsupported by all remaining admissible evidence, and no valid alternative evidence path remains.

### REDUNDANT

Removing the unit leaves another admissible path supporting the same answer slot. Redundancy is assessed per answer slot, not merely because another fact is present in the context.

### OPTIONAL / BACKGROUND

The unit is not required for any answer slot and is not an alternative support path.

### DISTRACTOR

The unit is not needed and may mislead the answerer.

### UNCERTAIN

Evidence does not permit a reliable decision.

Do not label an item Necessary merely because the benchmark lists it in evidence. Conversely, do not label it Redundant merely because another evidence ID is listed: two items may support different answer slots.

## 5. Dependency graph

Construct a query-specific directed graph. Nodes are atomic evidence units or intermediate answer propositions. Use separate node types for dialogue evidence and derived propositions.

Allowed edge labels:

- SUPPORTS: evidence unit supports an answer proposition.
- REQUIRES: proposition/evidence is needed to derive another proposition.
- RESOLVES_ENTITY: evidence identifies the referent/entity in another item.
- TEMPORAL_ANCHOR: evidence establishes time/order needed to interpret another item.
- UPDATES_OR_SUPERSEDES: a later statement changes the validity of an earlier state.
- CONTRADICTS: evidence conflicts with another item.

The derivation subgraph should be acyclic. Temporal update/conflict links may be represented in a separate relation layer if a DAG would otherwise be inappropriate.

Every edge needs a short rationale. Do not infer a dependency from chronological order alone.

## 6. Counterfactual deletion test

For each evidence unit:

- Remove only that unit while keeping all other admissible dialogue evidence.
- Ask whether every answer slot remains derivable from the remaining evidence.
- Record YES, NO, or UNCERTAIN.
- If YES, identify the alternative path and label the removed unit Redundant or Optional as appropriate.
- If NO, record which answer slot or dependency edge becomes unsupported.

For evidence sets, use remove-set tests only when two units are jointly redundant or mutually dependent. Record the exact set removed.

This annotation test is about logical support in the source dialogue, not whether an LLM happens to guess the right answer after deletion.

## 7. Evidence sufficiency and benchmark audit

Use one of these question-level labels:

- SUFFICIENT: cited dialogue supports all answer slots.
- PARTIAL: some answer slots are supported, others are not.
- INSUFFICIENT: the reference answer cannot be derived from the cited dialogue.
- MISALIGNED: evidence IDs do not point to the relevant dialogue content.
- AMBIGUOUS: multiple plausible interpretations or unresolved contradictions.
- UNSCORABLE: data issue prevents assessment.

If the benchmark reference answer contains a stronger claim than the evidence, preserve that discrepancy. Do not silently rewrite the reference answer.

## 8. Annotation schema

Recommended JSON record:

~~~json
{
  "dataset": "locomo10",
  "dataset_revision": "snap-research/locomo@<commit>",
  "conversation_id": "conv-26",
  "qa_index": 11,
  "question": "...",
  "reference_answer": "...",
  "category_id": 1,
  "category_name": "multi_hop",
  "evidence_sufficiency": "SUFFICIENT|PARTIAL|INSUFFICIENT|MISALIGNED|AMBIGUOUS|UNSCORABLE",
  "answer_slots": [
    {"slot_id": "a1", "text": "..."}
  ],
  "evidence_units": [
    {
      "unit_id": "e1",
      "source_dia_id": "D3:13",
      "atomic_fact": "...",
      "role": "DIRECT|BRIDGE|BACKGROUND|IRRELEVANT|MULTI_ROLE|UNCERTAIN",
      "necessity": "NECESSARY|REDUNDANT|OPTIONAL|DISTRACTOR|UNCERTAIN",
      "supports_slots": ["a1"],
      "alternative_path_ids": [],
      "answerability_after_remove": "YES|NO|UNCERTAIN",
      "rationale": "...",
      "annotator_confidence": 1
    }
  ],
  "dependency_edges": [
    {
      "source": "e1",
      "target": "a1",
      "type": "SUPPORTS",
      "rationale": "..."
    }
  ],
  "minimal_sufficient_evidence_sets": [["e1", "e2"]],
  "annotator_id": "A",
  "annotation_version": "0.1"
}
~~~

The schema is illustrative; create a machine-validated JSON Schema before formal annotation. Store source IDs and annotations, not copied raw dialogue text, unless redistribution rights have been reviewed.

## 9. Inter-annotator procedure

- Both annotators independently label all five dry-run questions.
- Before independent annotation, discuss the ontology using two practice examples not included in the five dry-run questions.
- Compare disagreements separately for evidence sufficiency, role, necessity, and edges.
- Adjudicate with a third reviewer or documented joint resolution.
- Report raw agreement and class distributions alongside Cohen's kappa or an appropriate alternative.
- If a label is rare or never used by one annotator, report that fact; do not interpret a misleadingly high agreement score as reliability.

## 10. Pilot acceptance criteria

The five-question dry run is for finding ontology defects, not claiming statistical reliability.

Proceed to 30–50 questions only if:
1. annotators can consistently separate role from necessity;
2. each retained question has a defensible answerability judgment;
3. Bridge has at least one unambiguous positive example, not just an inferred graph-centrality label;
4. alternative paths can be recorded without circular definitions;
5. evidence IDs resolve to the official source turns.

If no clear Bridge examples appear, revise the ontology or abandon role as a primary factor. Do not manufacture examples.
