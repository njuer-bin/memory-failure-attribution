# q0000 final attribution validation

Date: 2026-10-12

## Validation command

```powershell
G:\aconda\python.exe -u -m experiments.run_oracle_experiments --dataset locomo_refined_public --limit 1
```

## Result

The experiment completed successfully:

- dataset: `locomo_refined_public`
- question: `conv-26#q0000`
- records: `1`
- errors: `0`
- runtime: `29.02s`
- final failure attribution: `F1_FORMATION`

## Lifecycle result

Real Memory stage recall:

| Stage | Recall |
|---|---:|
| formation | 0.0 |
| storage | 1.0 |
| evolution | 0.0 |
| retrieval | 1.0 |
| rerank | 1.0 |
| context | 1.0 |

The earliest lifecycle loss is formation, so the final attribution is `F1_FORMATION`.

This is important because it validates that the strict turn-level provenance rule is not only working in the standalone provenance gate; it has also propagated into the final `run_oracle_experiments -> attribute_failure` path.

## Evidence sufficiency and oracle controls

Evidence sufficiency was `sufficient`, so the case was not stopped by `E0`.

Oracle Memory achieved full lifecycle recall and the oracle answer was judged correct. Oracle Context was also judged correct. Therefore this case is consistent with a Real Memory lifecycle failure rather than an evidence-insufficiency or reasoning-control failure.

## Answer scoring

Real Memory answer:

- correct: `0`
- accuracy: `0.0`
- token F1: `0.0`

Oracle Memory answer:

- correct: `1`
- accuracy: `1.0`

Oracle Context answer:

- correct: `1`
- accuracy: `1.0`

The final answer-failure distribution for this one-record run was:

```text
F1_FORMATION: 1
```

## Research significance

This provides the first end-to-end validation after the strict lifecycle provenance correction:

```text
Gold Evidence sufficient
        -> strict turn provenance
        -> formation missing
        -> earliest loss = formation
        -> final attribution = F1_FORMATION
```

The result supports the intended causal interpretation for `q0000` and shows that the provenance correction reaches the final attribution output, not only the diagnostic gate.

## Important limitation

This is a single-question validation (`n=1`). It does not justify updating dataset-level failure distributions or lifecycle recall statistics.

The previously identified cases `conv-26#q0002`, `conv-26#q0016`, and `conv-26#q0041` still need final attribution-path validation. Only after those targeted checks should the full `n=50` experiment be rerun and new lifecycle/failure distributions be treated as research results.

## Status

- strict lifecycle provenance evaluator: validated
- final attribution path on `q0000`: validated
- dataset-level conclusions: not yet frozen
- next step: targeted final attribution validation for `q0002`, `q0016`, `q0041`, then rerun `n=50`
