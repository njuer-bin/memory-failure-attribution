# Human annotation: expose LoCoMo turn time context

## Problem

The 25-case human attribution CSV previously displayed Gold Evidence as `[D*:turn_*] text` only. Human annotators could not safely judge relative temporal expressions such as `yesterday`, `last week`, or `last Tuesday` from a turn ID alone.

This was a usability and validity problem: the annotation protocol asks whether Gold Evidence is sufficient to establish the benchmark reference answer, but the required temporal anchor was hidden.

## Change

`experiments/sample_human_annotation.py` now builds a LoCoMo evidence-turn index from the repository's normalized benchmark loader and exports the resolved timestamp/date alongside each Gold Evidence item when available.

The CSV now includes:

- `gold_evidence`: `[D*:turn_* | benchmark timestamp] evidence text`
- `gold_evidence_time_context`: `D*:turn_* = benchmark timestamp`

The sampler remains deterministic and does not call a model or modify experiment results.

## Annotation rule

The human annotator should use the exported benchmark time context as the anchor for relative expressions. Do not infer a date from `D*:turn_*` itself.

If the benchmark timestamp is unavailable, leave the time-context information blank and mark the case for review rather than inventing an anchor.

## Validation

Added regression coverage for:

1. rendering a resolved timestamp in Gold Evidence;
2. exposing the new time-context CSV column;
3. preserving the existing deterministic stratified sampling counts and reproducibility.

## Next step

Regenerate the 25-case annotation CSV and inspect that temporal examples show their benchmark timestamps before beginning manual labeling.
