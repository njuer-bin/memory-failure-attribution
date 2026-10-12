# Strict lifecycle provenance fix

Date: 2026-10-12

## Motivation

Recent LoCoMo cases exposed a failure mode in lifecycle attribution: semantic matching could mark a Gold Evidence item as `found` even when the matched memory came from a different benchmark turn.

Examples observed in the current validation output:

- `conv-26#q0002`: Gold Evidence at `D1:turn_8` and `D1:turn_10` was semantically matched to `D4:turn_14` during formation/evolution and to `D3:turn_5` / `D7:turn_4` during retrieval.
- `conv-26#q0016`: all three Gold Evidence items had zero semantic memories on their exact source turns, while semantic matches existed elsewhere.
- `conv-26#q0041`: one evidence item had exact formation provenance, while the other was only represented by a semantic match from another turn.

These cases show that `semantic match != lifecycle success`.

## Change

`tracing/engine_trace.py::stage_match` now uses exact turn provenance as the criterion for lifecycle `found`/`missing`:

1. Read Gold Evidence `turn_id`.
2. Read observed artifact `source_turn_id` (or `turn_id`).
3. Mark an evidence item `found` only when the turn IDs are exactly equal.
4. A semantically similar artifact from another turn remains available under `semantic_matches` for diagnosis, but cannot promote the evidence to `found`.
5. Exact provenance matches are reported as `match_type=provenance` with score `1.0`.

This applies uniformly to formation, storage, evolution, retrieval, rerank, and context because these stages use `stage_match`.

## Why this matters for attribution

The previous behavior could create this invalid causal chain:

```text
Gold evidence
  -> semantic match from another turn
  -> stage marked found
  -> earlier lifecycle failure hidden
  -> downstream F4/F5 attribution
```

The corrected chain is:

```text
Gold evidence
  -> exact turn provenance
      -> found: stage survives
      -> missing: stage loses the evidence
            -> semantic match, if any, is diagnostic only
```

Therefore a case such as `q0002` should no longer be treated as `F4` merely because a related memory was found elsewhere. If the Gold Evidence was not formed on its source turn, the first-loss logic can correctly attribute the failure to formation.

## Regression coverage

Added `tests/test_stage_provenance_matching.py` covering:

- semantic match from a wrong turn is rejected as lifecycle success;
- exact turn provenance is accepted;
- multi-evidence stages require each Gold Evidence item to have exact provenance.

## Research status

This is an attribution/evaluation correction, not a change to the MemoryEngine itself.

The previous n=50 lifecycle distributions should be treated as validation-only until the experiment is rerun with this strict provenance rule. The semantic matches are still retained as diagnostic evidence, so the experiment can distinguish `true provenance miss` from `wrong-source semantic match`.

Next step: run the new regression test and the full test suite locally, then rerun the provenance-safe experiment before drawing updated F1-F6 distribution conclusions.
