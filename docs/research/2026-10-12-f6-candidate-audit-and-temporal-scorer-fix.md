# 2026-10-12 F6 Candidate Audit and Temporal Scorer Fix

## Trigger

The strict-provenance LoCoMo n=50 run reported two F6 candidates from `experiments.audit_f6_cases.py`:

- `conv-26#q0027`
- `conv-26#q0031`

Both cases had complete Gold Evidence through formation, storage, evolution, retrieval, rerank, and context. Oracle Memory and Oracle Context both produced answers that the existing temporal-aware scorer marked correct, while Real Memory answers were marked incorrect.

## Case audit

### q0027

Question: `When did Caroline join a mentorship program?`

Reference: `The weekend before 17 July 2023 / From July 15, 2023 to July 16, 2023`

Real answer: `Last weekend`

Gold Evidence states that Caroline joined the mentorship program `last weekend`, with benchmark timestamp `2:31 pm on 17 July, 2023`.

Human semantic judgment: `Last weekend` is a correct relative answer. The existing scorer returned `correct=False` because Real Memory context exposed an engine-generated numeric timestamp rather than the benchmark timestamp string, so the temporal anchor could not be resolved safely.

### q0031

Question: `When did Caroline join a new activist group?`

Reference: `The Tuesday before 20 July 2023 / July 18, 2023`

Real answer: `Last Tuesday.`

Gold Evidence states that Caroline joined the group `last Tues`, with benchmark timestamp `8:56 pm on 20 July, 2023`.

Human semantic judgment: `Last Tuesday` is a correct relative answer. The existing scorer again lacked the benchmark temporal anchor in Real Memory context and returned `correct=False`.

## Root cause

`evaluation/answer_generation.py` already supported relative temporal expressions such as `last weekend` and `last Tuesday`, but `_context_anchor_date()` only extracted benchmark dates from textual timestamp fields. Real Memory artifacts may instead expose numeric engine timestamps. Blindly interpreting those numeric values as benchmark dates would be unsafe because the observed values can differ from the original benchmark timestamp.

The safer fix is to use an explicit temporal anchor already stated in the benchmark reference answer when the reference contains constructions such as:

- `the weekend before 17 July 2023`
- `the Tuesday before 20 July 2023`

The scorer now resolves the candidate relative expression against that explicit reference anchor, without treating an unrelated engine timestamp as ground truth.

## Regression coverage

Added tests for:

1. `Last weekend` vs `the weekend before 17 July 2023 / July 15-16, 2023`.
2. `Last Tuesday` vs `the Tuesday before 20 July 2023 / July 18, 2023`.
3. Both tests use the numeric Real Memory timestamp shape observed in the audited cases, ensuring the fix does not depend on parsing the unsafe engine timestamp.

Commits:

- `51f9c2de89f8eeaa70d2426c07818b2e2fcbff55` — temporal scorer fix.
- `72300f2349c0a060e51d360c22e2ab76e2fcb457` — regression tests.

## Interpretation

The two current n=50 F6 candidates are therefore **provisional scorer artifacts**, not confirmed reasoning failures. This is consistent with the earlier observation that F6 is especially sensitive to temporal answer scoring.

This fix should be validated with the full test suite and then the affected experiment rows should be rescored/recomputed before making any F6 distribution claim.

The evaluator is **not yet frozen**. Human annotation of representative cases remains required before scaling the experiment to n>=100.
