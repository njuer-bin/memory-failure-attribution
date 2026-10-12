# Targeted provenance validation: q0002, q0016, q0041

Date: 2026-10-12

## Validation scope

After the strict lifecycle provenance correction, three previously suspicious LoCoMo cases were rechecked with the single-sample provenance E2E gate:

- `conv-26#q0002`
- `conv-26#q0016`
- `conv-26#q0041`

All three returned `status: PASS` with `provenance_errors: []`.

The gate uses exact benchmark turn provenance. Semantic similarity from another turn is not accepted as lifecycle success.

## q0002

Question: `What fields would Caroline be likely to pursue in her education?`

Gold Evidence:

- `e0`: `D1:turn_8` — exact provenance PASS
- `e1`: `D1:turn_10` — exact provenance PASS

Lifecycle results:

| Stage | Found | Gold Evidence | Result |
|---|---:|---:|---|
| formation | 0 | 2 | missing |
| storage | 2 | 2 | provenance found |
| evolution | 0 | 2 | missing |
| retrieval | 0 | 2 | missing |
| rerank | 0 | 2 | missing |
| context | 0 | 2 | missing |

Because formation is the earliest stage with missing Gold Evidence, the expected first-loss attribution is `F1_FORMATION`.

## q0016

Question: `Where has Melanie camped?`

Gold Evidence:

- `e0`: `D6:turn_15` — exact provenance PASS
- `e1`: `D4:turn_5` — exact provenance PASS
- `e2`: `D8:turn_31` — exact provenance PASS

Lifecycle results:

| Stage | Found | Gold Evidence | Result |
|---|---:|---:|---|
| formation | 0 | 3 | missing |
| storage | 3 | 3 | provenance found |
| evolution | 0 | 3 | missing |
| retrieval | 0 | 3 | missing |
| rerank | 0 | 3 | missing |
| context | 0 | 3 | missing |

The expected first-loss attribution is therefore `F1_FORMATION`.

## q0041

Question: `What subject have Caroline and Melanie both painted?`

Gold Evidence:

- `e0`: `D14:turn_4` — exact provenance PASS
- `e1`: `D8:turn_5` — exact provenance PASS

Lifecycle results:

| Stage | Found | Gold Evidence | Result |
|---|---:|---:|---|
| formation | 1 | 2 | partial loss |
| storage | 2 | 2 | provenance found |
| evolution | 1 | 2 | partial loss |
| retrieval | 0 | 2 | missing |
| rerank | 0 | 2 | missing |
| context | 0 | 2 | missing |

For multi-evidence questions, the lifecycle stage is considered successful only when all Gold Evidence items have exact provenance. Therefore formation is already the first loss, giving the expected attribution `F1_FORMATION`.

## Research finding

These three cases confirm the diagnostic pattern discovered before the strict provenance change:

> A semantic match from another turn must not be allowed to turn a lifecycle stage into `found`.

The corrected evaluator now distinguishes the actual source-turn lifecycle state from merely similar content elsewhere. In particular:

```text
q0002: formation 0/2 -> first loss F1
q0016: formation 0/3 -> first loss F1
q0041: formation 1/2 -> first loss F1
```

This strengthens the hypothesis that the earlier F4 assignments for these cases were caused by semantic cross-turn matching masking an earlier formation failure.

## Important qualification

This E2E gate validates provenance alignment and expected lifecycle first-loss interpretation. It does not by itself prove that the final `run_oracle_experiments -> attribute_failure` output has changed for all three questions.

The next required validation is a targeted final-attribution run that inspects the experiment records and confirms:

- `q0002 -> F1_FORMATION`
- `q0016 -> F1_FORMATION`
- `q0041 -> F1_FORMATION`

Only after that final attribution-path check should the full `n=50` experiment be rerun and its lifecycle recall / failure distributions treated as updated research results.

## Status

- provenance E2E gate: `3/3 PASS`
- provenance errors: `0`
- expected lifecycle first loss: `F1_FORMATION` for all three
- final attribution-path validation: pending
- n=50 rerun: pending
