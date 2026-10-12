# LoCoMo n=50 Cumulative Lifecycle Transition Results

## Purpose

The strict-provenance n=50 experiment exposed strong upstream confounding in raw stage recall. The transition analyzer was therefore extended with a primary cumulative-upstream view: a stage is evaluated only among questions/evidence items that have survived the entire upstream causal chain.

Input: `results/oracle_experiments/comparison.jsonl`

- 50 successful rows
- strict turn-level provenance evaluator
- no additional model calls
- 46 gate-sufficient rows

## Question-level results

### All eligible rows

Eligible rows: 49.

| Cumulative transition | Eligible after upstream | Survived | Conditional survival | Conditional failure |
|---|---:|---:|---:|---:|
| storage given upstream | 5 | 5 | 1.000 | 0.000 |
| evolution given upstream | 5 | 5 | 1.000 | 0.000 |
| retrieval given upstream | 5 | 3 | 0.600 | 0.400 |
| rerank given upstream | 3 | 3 | 1.000 | 0.000 |
| context given upstream | 3 | 2 | 0.667 | 0.333 |

### Gate-sufficient rows

Eligible rows: 46.

| Cumulative transition | Eligible after upstream | Survived | Conditional survival | Conditional failure |
|---|---:|---:|---:|---:|
| storage given upstream | 5 | 5 | 1.000 | 0.000 |
| evolution given upstream | 5 | 5 | 1.000 | 0.000 |
| retrieval given upstream | 5 | 3 | 0.600 | 0.400 |
| rerank given upstream | 3 | 3 | 1.000 | 0.000 |
| context given upstream | 3 | 2 | 0.667 | 0.333 |

## Evidence-level results

### All eligible rows

Eligible evidence items: 68.

| Cumulative transition | Eligible after upstream | Survived | Conditional survival | Conditional failure |
|---|---:|---:|---:|---:|
| storage given upstream | 11 | 11 | 1.000 | 0.000 |
| evolution given upstream | 11 | 11 | 1.000 | 0.000 |
| retrieval given upstream | 11 | 6 | 0.545 | 0.455 |
| rerank given upstream | 6 | 5 | 0.833 | 0.167 |
| context given upstream | 5 | 3 | 0.600 | 0.400 |

### Gate-sufficient rows

Eligible evidence items: 65.

| Cumulative transition | Eligible after upstream | Survived | Conditional survival | Conditional failure |
|---|---:|---:|---:|---:|
| storage given upstream | 11 | 11 | 1.000 | 0.000 |
| evolution given upstream | 11 | 11 | 1.000 | 0.000 |
| retrieval given upstream | 11 | 6 | 0.545 | 0.455 |
| rerank given upstream | 6 | 5 | 0.833 | 0.167 |
| context given upstream | 5 | 3 | 0.600 | 0.400 |

## Interpretation

The primary question-level causal funnel in this sample is:

`Formation -> Storage -> Evolution -> Retrieval -> Rerank -> Context`

Among the small set that survives the upstream chain:

- Formation -> Storage: 100% survival.
- Storage -> Evolution, conditioned on prior Formation success: 100% survival.
- Formation + Storage + Evolution -> Retrieval: 60% survival.
- Formation + Storage + Evolution + Retrieval -> Rerank: 100% survival.
- Formation + Storage + Evolution + Retrieval + Rerank -> Context: 66.7% survival.

The corresponding evidence-level funnel is:

- Formation -> Storage: 100%.
- Upstream-surviving evidence -> Evolution: 100%.
- Upstream-surviving evidence -> Retrieval: 54.5%.
- Upstream-surviving evidence -> Rerank: 83.3%.
- Upstream-surviving evidence -> Context: 60.0%.

This gives a cleaner interpretation than the raw stage recall table. In particular, the earlier `storage -> evolution = 5/46 = 10.9%` adjacent statistic is not a causal evolution-success rate because many rows had already failed formation. The cumulative statistic conditions on the complete upstream chain.

## Research significance

The current n=50 sample suggests that, conditional on successful formation, storage and evolution do not show an additional observed loss in the surviving cases. Retrieval and context remain the clearest downstream loss points in the current causal funnel. Rerank appears relatively strong, although its question-level denominator is only 3 and its evidence-level denominator is only 6.

The result does **not** establish stable population-level probabilities. The critical denominators are very small:

- formation survivors: 5 questions / 11 evidence items;
- retrieval-eligible cumulative questions: 5;
- rerank-eligible cumulative questions: 3.

Therefore these percentages are exploratory and should not be generalized before larger samples and uncertainty estimates.

## Methodological status

This cumulative view should be treated as the primary transition statistic for subsequent experiments. The adjacent transition view remains useful as a descriptive diagnostic and for debugging the lifecycle trace, but should not be used alone for causal claims.

Next steps:

1. run the transition-analysis tests and full CI;
2. perform human annotation on 20–30 representative cases to validate lifecycle attribution and E0 decisions;
3. freeze the evaluator;
4. scale to LoCoMo n>=100 and then LongMemEval n>=100;
5. report bootstrap confidence intervals and evidence-level results alongside question-level results.
