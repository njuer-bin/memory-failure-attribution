# Human Annotation Audit Protocol

## Purpose

After the deterministic n=50 answer rescore, the current automated attribution is:

- F1_FORMATION: 35
- E0_EVIDENCE_INSUFFICIENCY: 4
- F4_RETRIEVAL: 2
- F5_CONTEXT: 1
- F6_REASONING: 0

These labels are still evaluator outputs, not human-validated ground truth. This audit checks whether the evidence gate and lifecycle attribution are credible before scaling to n>=100.

## Sampling

Use `experiments/sample_human_annotation.py` on `comparison_rescored.jsonl`.

Default sample size is 25 with a fixed seed. Mandatory strata are:

- F1_FORMATION: 12
- E0_EVIDENCE_INSUFFICIENCY: 4
- F4_RETRIEVAL: 2
- F5_CONTEXT: 1
- other labels: 6

The sampler is deterministic and never calls a model.

## Annotation order

Annotators should inspect the following before seeing the automatic failure label:

1. Question
2. Benchmark reference answer
3. Gold Evidence
4. Lifecycle artifacts/provenance
5. Real Memory answer
6. Oracle Context answer when needed for F6 adjudication
7. Only then reveal the automatic attribution label

This order reduces confirmation bias.

## Evidence sufficiency

Label one of:

- `SUFFICIENT`: Gold Evidence contains enough information to answer the benchmark question correctly.
- `INSUFFICIENT`: Gold Evidence does not contain enough information.
- `UNCERTAIN`: the evidence/answer relationship cannot be judged confidently.

E0 is only valid when the human judgment is `INSUFFICIENT`.

## Lifecycle labels

For each Gold Evidence item, inspect exact provenance rather than semantic similarity:

- `FOUND`
- `MISSING`
- `N/A`
- `UNCERTAIN`

Stages:

`formation -> storage -> evolution -> retrieval -> rerank -> context`

A semantically similar memory from a different benchmark turn is not evidence that the Gold Evidence survived the lifecycle.

## Failure attribution

Use the earliest blocking stage among the Gold Evidence required for the answer:

- Formation missing -> F1_FORMATION
- Storage missing after formation -> F2_STORAGE
- Evolution missing after storage -> F3_EVOLUTION
- Retrieval or rerank missing -> F4_RETRIEVAL
- Context missing after retrieval/rerank -> F5_CONTEXT
- All Gold Evidence reaches final context, gate is sufficient, and Real answer remains wrong while Oracle Context is correct -> F6_REASONING

If evidence is insufficient, use E0 rather than F1-F6.

If the gate cannot be judged confidently, use EVAL.

If Oracle Context is itself wrong, record `RC_REASONING_CONTROL_FAILURE` rather than claiming F6.

## Agreement metrics after annotation

After the 25 cases are labeled, compute:

1. Overall agreement between automatic and human final labels.
2. Cohen's kappa for the multi-class final failure label.
3. Per-class precision and recall for F1, E0, F4, F5, and F6.
4. Separate agreement for evidence sufficiency.

Do not use the audit sample to replace the full benchmark estimate. Its purpose is evaluator validation.

## Freeze rule

Do not run the final n>=100 benchmark until the annotation protocol has been applied and major evaluator contradictions have been resolved. If substantial disagreement remains, revise the evaluator, rerun the audit, and document the change.
