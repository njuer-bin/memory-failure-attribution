# LoCoMo n=50 deterministic rescore results

Date: 2026-10-12
Branch: `fix/independent-evidence-gate`
Dataset: `locomo_refined_public`
N: 50

## Purpose

Re-score the already completed n=50 experiment using the current answer adjudicator after the temporal-reference fix. This is an answer-only rescore: no MemoryEngine rebuild, retrieval, rerank, context construction, or Ollama generation was rerun.

Input:
`results/oracle_experiments/comparison.jsonl`

Output:
`results/oracle_experiments/comparison_rescored.jsonl`

Scorer:
`evaluation.answer_generation.score_answer`

## Corrected answer distribution

Real Memory:
- scored: 50/50
- correct: 8/50 = 16%
- exact match: 0%
- token F1: 0.028351553787659266
- model errors: 0

First answer failure:
- F1_FORMATION: 35
- E0_EVIDENCE_INSUFFICIENCY: 4
- F4_RETRIEVAL: 2
- F5_CONTEXT: 1
- F6_REASONING: 0

Therefore, after the temporal scorer correction, the n=50 run contains **zero F6 cases in the deterministic rescore**.

Oracle Memory:
- correct: 30/50 = 60%
- exact match: 10%
- token F1: 0.18028272086336602

Oracle Context:
- correct: 30/50 = 60%
- exact match: 10%
- token F1: 0.17996526054590573

## Lifecycle results

These lifecycle values are unchanged by the answer-only rescore:

| Stage | Real Memory recall |
|---|---:|
| formation | 0.17 |
| storage | 0.98 |
| evolution | 0.17 |
| retrieval | 0.54 |
| rerank | 0.505 |
| context | 0.29 |

First lifecycle loss:
- formation: 44
- retrieval: 2
- context: 1
- none: 3

Oracle Memory lifecycle recall remains 0.98 at every stage.
Oracle Context context recall remains 0.98.

## Evidence gate

- sufficient: 46
- insufficient: 4
- uncertain/error: 0

The gate remains independent of the Real Memory answer and is evaluated against the benchmark reference answer.

## Important interpretation

`first_loss_distribution` and `first_answer_failure_distribution` answer different questions and must not be conflated.

The lifecycle first-loss distribution counts the earliest lifecycle stage at which Gold Evidence is absent, regardless of whether the final answer is correct. The answer-failure distribution is conditional on the final answer being incorrect and additionally applies the E0 gate and attribution rules. Therefore it is expected that lifecycle formation first-loss (44) is larger than attributed F1 failures (35).

The corrected result supports the following limited statement for this n=50 validation sample: **no deterministic F6 reasoning failures remain after the temporal scorer correction.** This does not prove that F6 never occurs; the sample is too small and the evaluator still requires human validation before being considered frozen.

## Next step

Do not launch the n>=100 benchmark yet. First perform a 20–30 case human annotation of representative attribution cases and compare human judgments with the evaluator. Freeze the adjudication protocol only after that validation.