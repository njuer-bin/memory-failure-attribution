# 2026-10-12 Targeted F6 Temporal Rescore Validation

## Purpose

After the temporal scorer fix in `evaluation/answer_generation.py`, rerun the two LoCoMo cases that had been identified as the only F6 candidates in the strict-provenance n=50 audit:

- `conv-26#q0027`
- `conv-26#q0031`

The goal is to determine whether the apparent F6 failures survive the corrected temporal adjudication.

## q0027

Question: `When did Caroline join a mentorship program?`

Reference: `The weekend before 17 July 2023 / From July 15, 2023 to July 16, 2023`

Targeted attribution completed successfully with `failure=None`.

Lifecycle provenance was complete for the Gold Evidence item:

- formation: found by exact provenance (`D9:turn_1`)
- storage: found by exact provenance (`D9:turn_1`)
- evolution: found by exact provenance (`D9:turn_1`)
- retrieval: found by exact provenance (`D9:turn_1`)
- rerank: found by exact provenance (`D9:turn_1`)
- context: found by exact provenance (`D9:turn_1`)

The retrieved/context evidence contains the original relative expression `Last weekend`. The engine-generated numeric timestamp is not used as a benchmark temporal anchor.

The targeted run completed without an attribution failure and saved its result to `results/oracle_experiments/targeted_attribution.json`.

## q0031

Question: `When did Caroline join a new activist group?`

Reference: `The Tuesday before 20 July 2023 / July 18, 2023`

Targeted attribution completed successfully with `failure=None`.

Lifecycle provenance was complete for the Gold Evidence item:

- formation: found by exact provenance (`D10:turn_2`)
- storage: found by exact provenance (`D10:turn_2`)
- evolution: found by exact provenance (`D10:turn_2`)
- retrieval: found by exact provenance (`D10:turn_2`)
- rerank: found by exact provenance (`D10:turn_2`)
- context: found by exact provenance (`D10:turn_2`)

Most importantly, the corrected answer scorer now reports:

- answer: `Last Tuesday.`
- `temporal_equivalent: true`
- `correct: true`
- `temporal_anchor_date: null`
- `explicit_date_mismatch: false`

This confirms that the candidate is no longer treated as a reasoning failure after the reference-anchor fix.

## Interpretation

The targeted reruns support the previous case audit: these two cases should not be counted as confirmed `F6_REASONING` failures.

The key distinction is that the memory lifecycle successfully delivered the exact Gold Evidence in both cases. The apparent failure came from answer adjudication of relative temporal language, not from retrieval, reranking, context construction, or reasoning.

For q0031, the corrected scorer result is directly observed and unambiguous. For q0027, the targeted run completed without an attribution failure and preserved exact provenance through context; the saved targeted result should be used for the final numeric rescore record if a complete answer block is needed.

## Research status

- q0027: targeted validation completed; lifecycle path is clean; final scorer field should be checked from the saved JSON before updating aggregate F6 counts.
- q0031: targeted validation confirms `correct=true`; remove it from the confirmed F6 set.
- The evaluator is still **not frozen**.
- Do **not** run the n>=100 benchmark expansion yet.
- Next validation stage remains representative human annotation (20–30 cases), followed by evaluator freeze and then larger-scale experiments.

## Related commits

- `51f9c2de89f8eeaa70d2426c07818b2e2fcbff55` — temporal scorer fix.
- `72300f2349c0a060e51d360c22e2ab76e2fcb457` — regression tests.
- `b23841254d9e889c9fb87ba0effebd875c937e1a` — original F6 candidate audit and scorer-fix research log.
