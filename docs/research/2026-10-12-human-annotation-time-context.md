# Human annotation: expose LoCoMo turn time context

## Problem

The 25-case human attribution CSV previously displayed Gold Evidence as `[D*:turn_*] text` only. Human annotators could not safely judge relative temporal expressions such as `yesterday`, `last week`, or `last Tuesday` from a turn ID alone.

This was a usability and validity problem: the annotation protocol asks whether Gold Evidence is sufficient to establish the benchmark reference answer, but the required temporal anchor was hidden.

## First implementation

`experiments/sample_human_annotation.py` was changed to build a LoCoMo evidence-turn index from the normalized benchmark loader and export the resolved timestamp/date alongside each Gold Evidence item when available.

The CSV now includes:

- `gold_evidence`: `[D*:turn_* | benchmark timestamp] evidence text`
- `gold_evidence_time_context`: `D*:turn_* = benchmark timestamp`

## Follow-up bug found during audit

The first implementation used a global `turn_id -> timestamp` index. This is unsafe because LoCoMo turn IDs such as `D1:turn_1` are reused across different conversations. A later conversation could overwrite an earlier conversation's timestamp and make a human-audit CSV show the wrong temporal anchor.

The fix now:

1. keys the benchmark fallback index by `(question_id, turn_id)`;
2. prefers the timestamp already persisted on the Gold Evidence item itself;
3. only uses the benchmark index when the persisted evidence row lacks a timestamp;
4. keeps backward-compatible support for the old turn-only lookup shape used by tests/callers.

This prevents cross-conversation timestamp collisions from contaminating human annotation.

## Annotation rule

The human annotator should use the exported benchmark time context as the anchor for relative expressions. Do not infer a date from `D*:turn_*` itself.

If the benchmark timestamp is unavailable, leave the time-context information blank and mark the case for review rather than inventing an anchor.

## Validation

Regression coverage now includes:

1. rendering a resolved timestamp in Gold Evidence;
2. preferring a persisted evidence timestamp over a conflicting fallback index value;
3. proving that identical turn IDs from different question IDs resolve to their own timestamps;
4. exposing the new time-context CSV column;
5. preserving deterministic stratified sampling counts and reproducibility.

## Research consequence

The previously flagged temporal annotation cases `q0006`, `q0020`, and `q0047` should **not** be treated as confirmed dataset problems solely from the old CSV. The old CSV may have been affected by cross-conversation time-index collisions. Regenerate the sample after this fix and re-check those cases against the corrected benchmark-scoped time context.

## Next step

Regenerate the 25-case annotation CSV and inspect all temporal examples before beginning or finalizing manual labeling. Do not use the earlier assistant-generated annotation file as human ground truth.
