# 2026-10-12 — Deterministic n=50 answer rescore

## Purpose

The LoCoMo strict-provenance n=50 experiment was generated before the latest
reference-anchor temporal scorer fix. Two raw F6 candidates (q0027 and q0031)
were subsequently identified as likely temporal scoring artifacts.

We therefore add a deterministic rescore path that updates only answer
adjudication and answer-failure attribution. It does **not** rebuild the
MemoryEngine, rerun retrieval, regenerate answers with Ollama, or change Gold
Evidence or lifecycle provenance.

## Implementation

Added:

- `experiments/rescore_existing_results.py`
- `tests/test_rescore_existing_results.py`

The utility reads the existing `results/oracle_experiments/comparison.jsonl`
rows and applies the current `evaluation.answer_generation.score_answer()` to
the already persisted answers.

Because the original comparison rows do not persist the complete final-context
payload, the utility reuses the previously persisted `temporal_anchor_date`
when one exists. If no persisted anchor exists, the current scorer can still
use explicit temporal anchors contained in the benchmark reference answer,
such as `before 17 July 2023` and `before 20 July 2023`.

After rescoring, `answer_failure_type` is recomputed from the unchanged
lifecycle/gate fields.

Outputs:

- `results/oracle_experiments/comparison_rescored.jsonl`
- `results/oracle_experiments/summary_rescored.json`

## Validation

Unit tests cover both previously flagged temporal patterns:

- q0027: `Last weekend.` vs. `The weekend before 17 July 2023 / From July 15, 2023 to July 16, 2023`
- q0031: `Last Tuesday.` vs. `The Tuesday before 20 July 2023 / July 18, 2023`

Both now score as temporally equivalent and correct, and therefore no longer
receive F6.

## Required local command

```powershell
G:\aconda\python.exe -m pytest tests/test_rescore_existing_results.py -q
G:\aconda\python.exe -m experiments.rescore_existing_results
```

The resulting aggregate, rather than a hand-edited count, is the authoritative
post-fix n=50 answer-failure distribution.

## Research boundary

This is an evaluator-only correction. It should not be described as a new
memory-system experiment. The strict-provenance n=50 lifecycle results remain
unchanged; only the answer adjudication layer is recomputed.
