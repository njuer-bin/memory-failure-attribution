# LoCoMo n=50 Conditional / Transition Failure Analysis

## 1. Purpose

This analysis is the next step after the strict turn-level provenance rerun of `locomo_refined_public` n=50. The goal is to avoid interpreting raw lifecycle recall as independent failure rates when upstream lifecycle loss already prevents downstream evidence from surviving.

Input:

- `results/oracle_experiments/comparison.jsonl`
- 50 successful rows
- strict lifecycle provenance evaluator
- no model calls during this analysis

The analysis reports both question-level and evidence-level transitions, with and without restricting to E0 gate-sufficient rows.

## 2. Observed results

### 2.1 Question level — all rows

Eligible rows: 49.

| Stage | Pass | Total | Rate |
|---|---:|---:|---:|
| formation | 5 | 49 | 0.102 |
| storage | 48 | 49 | 0.980 |
| evolution | 5 | 49 | 0.102 |
| retrieval | 23 | 49 | 0.469 |
| rerank | 22 | 49 | 0.449 |
| context | 13 | 49 | 0.265 |

Adjacent conditional transitions:

| Transition | Eligible after previous | Survived | Conditional survival | Conditional failure |
|---|---:|---:|---:|---:|
| formation -> storage | 5 | 5 | 1.000 | 0.000 |
| storage -> evolution | 48 | 5 | 0.104 | 0.896 |
| evolution -> retrieval | 5 | 3 | 0.600 | 0.400 |
| retrieval -> rerank | 23 | 22 | 0.957 | 0.043 |
| rerank -> context | 22 | 13 | 0.591 | 0.409 |

### 2.2 Evidence level — all rows

Eligible evidence items: 68.

| Transition | Eligible after previous | Survived | Conditional survival | Conditional failure |
|---|---:|---:|---:|---:|
| formation -> storage | 11 | 11 | 1.000 | 0.000 |
| storage -> evolution | 67 | 11 | 0.164 | 0.836 |
| evolution -> retrieval | 11 | 6 | 0.545 | 0.455 |
| retrieval -> rerank | 30 | 27 | 0.900 | 0.100 |
| rerank -> context | 27 | 14 | 0.519 | 0.481 |

### 2.3 Gate-sufficient rows

There are 46 gate-sufficient rows.

Question-level stage pass rates:

| Stage | Pass | Total | Rate |
|---|---:|---:|---:|
| formation | 5 | 46 | 0.109 |
| storage | 46 | 46 | 1.000 |
| evolution | 5 | 46 | 0.109 |
| retrieval | 23 | 46 | 0.500 |
| rerank | 22 | 46 | 0.478 |
| context | 13 | 46 | 0.283 |

Adjacent transitions are:

| Transition | Eligible after previous | Survived | Conditional survival | Conditional failure |
|---|---:|---:|---:|---:|
| formation -> storage | 5 | 5 | 1.000 | 0.000 |
| storage -> evolution | 46 | 5 | 0.109 | 0.891 |
| evolution -> retrieval | 5 | 3 | 0.600 | 0.400 |
| retrieval -> rerank | 23 | 22 | 0.957 | 0.043 |
| rerank -> context | 22 | 13 | 0.591 | 0.409 |

Evidence-level gate-sufficient results:

| Transition | Eligible after previous | Survived | Conditional survival | Conditional failure |
|---|---:|---:|---:|---:|
| formation -> storage | 11 | 11 | 1.000 | 0.000 |
| storage -> evolution | 65 | 11 | 0.169 | 0.831 |
| evolution -> retrieval | 11 | 6 | 0.545 | 0.455 |
| retrieval -> rerank | 30 | 27 | 0.900 | 0.100 |
| rerank -> context | 27 | 14 | 0.519 | 0.481 |

## 3. Important methodological correction

The adjacent transition `storage -> evolution = 5/46 = 10.9%` should **not** be interpreted as "only 10.9% of stored evidence evolves".

The current lifecycle statuses are not strictly monotonic. In particular, storage can succeed even when formation has already failed. Therefore the adjacent transition denominator contains many rows whose formation failed. This makes the adjacent transition useful as a descriptive statistic, but not sufficient as a causal lifecycle-transition estimate.

The more meaningful causal question is:

> Among evidence that has successfully survived the upstream causal stages, how often does the next stage also succeed?

For the current n=50 data, the relevant calculations are therefore:

- `P(evolution | formation)` = 5 / 5 = **1.000** at question level.
- `P(retrieval | formation AND evolution)` = 3 / 5 = **0.600**.
- `P(rerank | retrieval)` = 22 / 23 = **0.957**.
- `P(context | rerank)` = 13 / 22 = **0.591**.

At evidence level, using the observed transition survivors:

- `P(evolution | formation)` = 11 / 11 = **1.000**.
- `P(retrieval | formation AND evolution)` = 6 / 11 = **0.545**.
- `P(rerank | retrieval)` = 27 / 30 = **0.900**.
- `P(context | rerank)` = 14 / 27 = **0.519**.

These causal-chain calculations are the preferred interpretation for future failure analysis. The existing adjacent-transition output should be retained as a descriptive diagnostic, not treated as the final causal attribution statistic.

## 4. Research interpretation

The n=50 strict-provenance sample currently suggests a strong separation between lifecycle stages:

1. **Formation is the dominant earliest observed loss.** Only 5/46 gate-sufficient questions have all Gold Evidence represented at formation.
2. **Storage is not the apparent bottleneck once formation succeeds.** All 5 question-level formation-success cases also pass storage; the evidence-level formation-to-storage transition is also 11/11.
3. **Evolution does not show an additional loss among the small set that survives formation.** At question level, 5/5 formation-success cases also pass evolution. This must be treated cautiously because the denominator is only 5.
4. **Retrieval is a substantial downstream bottleneck.** Conditional survival from formation+evolution to retrieval is 3/5 = 60% at question level and 6/11 = 54.5% at evidence level.
5. **Rerank is relatively strong conditional on retrieval.** Survival is 95.7% at question level and 90.0% at evidence level.
6. **Context is another substantial downstream loss.** Survival from rerank to context is 59.1% at question level and 51.9% at evidence level.

The most important pattern is therefore not simply the raw recall table. It is the causal funnel:

`Formation -> Evolution -> Retrieval -> Rerank -> Context`

with the current observed conditional survival approximately:

`100% -> 60% -> 95.7% -> 59.1%` (question level).

However, the formation denominator is only 5 questions, so these percentages are unstable and should not be generalized from n=50.

## 5. What this establishes

Supported by this experiment:

- Strict provenance materially separates upstream formation loss from downstream retrieval/context loss.
- Storage has very high observed survival after formation in this sample.
- Retrieval and context remain meaningful downstream loss points among the small set that survives upstream stages.
- Rerank has relatively high conditional survival after retrieval.

Not established:

- Formation is the dominant failure source for Agent Memory in general.
- The observed conditional rates generalize to other datasets, MemoryEngine implementations, or larger samples.
- The small 5-question formation-survivor denominator is sufficient for a stable estimate.
- F6 reasoning failures are definitively established without further case-level audit.

## 6. Next methodological step

Before scaling to n>=100, the evaluator should expose the causal-chain statistics directly rather than requiring manual reconstruction from adjacent transitions.

Recommended implementation:

- retain the current adjacent transition report;
- add cumulative upstream-survival transitions such as `evolution | formation`, `retrieval | formation+evolution`, `rerank | formation+evolution+retrieval`, and `context | formation+evolution+retrieval+rerank`;
- add tests for non-monotonic stage outcomes where storage succeeds after formation failure;
- use the cumulative conditional view as the primary research table.

After that, proceed to the planned 20–30 case human annotation subset, freeze the evaluator, and only then scale to larger benchmark samples.
