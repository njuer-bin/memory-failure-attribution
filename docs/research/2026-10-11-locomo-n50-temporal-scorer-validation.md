# 2026-10-11 — LoCoMo-Refined n=50 validation after temporal scorer timestamp fix

## Purpose

This checkpoint records the first full LoCoMo-Refined n=50 experiment after the benchmark timestamp parsing fix in `evaluation/answer_generation.py`.

The preceding engineering fix was intended to make relative temporal answers such as `Yesterday`, `Last Saturday`, and `Last week` comparable against benchmark timestamps such as `1:56 pm on 8 May, 2023`.

The fix had already passed:

- 11 dedicated temporal/timestamp tests
- 28/28 repository tests

## Experiment

Command:

```text
G:\\aconda\\python.exe -u -m experiments.run_oracle_experiments --dataset locomo_refined_public --limit 50
```

Result:

- dataset: `locomo_refined_public`
- records: 50
- errors: 0

## Results

### Real Memory lifecycle

| Stage | Recall |
|---|---:|
| Formation | 0.885 |
| Storage | 0.98 |
| Evolution | 0.885 |
| Retrieval | 0.8183333333 |
| Rerank | 0.7533333333 |
| Context | 0.44 |

First-loss distribution:

| First loss | Count |
|---|---:|
| none | 20 |
| retrieval | 8 |
| rerank | 2 |
| context | 13 |
| formation | 7 |

### Oracle Memory

| Stage | Recall |
|---|---:|
| Formation | 0.98 |
| Storage | 0.98 |
| Evolution | 0.98 |
| Retrieval | 0.98 |
| Rerank | 0.98 |
| Context | 0.98 |

First-loss distribution:

- none: 49
- formation: 1

### Oracle Context

Context recall: 0.98.

### Evidence sufficiency gate

- sufficient: 47
- insufficient: 3
- gate protocol: E0 is evaluated before F1–F6; uncertain/error cases are EVAL.

### Answer scoring

Scoring method:

`local_ollama_token_f1_plus_temporal_phrase_rules`

| Mode | Correct | Accuracy | Exact Match | Token F1 |
|---|---:|---:|---:|---:|
| Real Memory | 1/50 | 0.02 | 0.00 | 0.0371271529 |
| Oracle Memory | 19/50 | 0.38 | 0.08 | 0.1793938320 |
| Oracle Context | 19/50 | 0.38 | 0.08 | 0.1793938320 |

First answer-failure distribution:

| Failure | Count |
|---|---:|
| F6_REASONING | 19 |
| E0_EVIDENCE_INSUFFICIENCY | 3 |
| F4_RETRIEVAL | 8 |
| F5_CONTEXT | 13 |
| F1_FORMATION | 6 |

## Comparison with the preceding n=50 result

The post-fix aggregate result is effectively unchanged from the immediately preceding n=50 run:

- Real Memory accuracy remains 2%.
- Oracle Memory accuracy remains 38%.
- Oracle Context accuracy remains 38%.
- F6 remains 19.
- F5 remains 13.
- E0 remains 3.
- Real Memory lifecycle recall is unchanged.

Therefore, the timestamp parsing fix is **validated as an engineering fix**, but this n=50 rerun does not provide evidence that timestamp parsing was responsible for the aggregate F6 count.

## Interpretation status

### Confirmed

1. The n=50 experiment completes reproducibly with 0 execution errors.
2. The evidence-sufficiency gate remains operational after the scorer change.
3. Real Memory has a large context-stage evidence loss in this sample (`0.44` recall), while Oracle Memory preserves `0.98` context recall.
4. Oracle Memory and Oracle Context both score 19/50 under the current answer scorer.
5. The timestamp parsing fix does not change the aggregate n=50 answer/failure distribution.

### Not yet confirmed

The 19 `F6_REASONING` cases must **not** yet be treated as 19 confirmed reasoning failures.

The remaining methodological question is whether some of these cases are answer-scorer false positives/false negatives, semantic equivalence cases, or genuine downstream reasoning failures.

In particular, previously suspected relative-temporal cases (`q0000`, `q0005`, `q0009`, `q0014`, `q0015`) require case-level inspection rather than aggregate inference.

## Research decision

Do **not** scale to n=100/n=500 yet.

The next step is a case-level audit of all 19 F6 cases using:

- question
- benchmark reference answer
- generated answer
- Gold Evidence
- final context
- Token F1
- temporal equivalence fields
- phrase-match fields
- semantic correctness/evidence-sufficiency fields where available

Each case will be classified as:

1. confirmed F6 reasoning candidate;
2. answer-scorer false positive;
3. answer-scorer false negative;
4. case requiring a new explicit scoring rule.

Only after this audit is complete should the protocol be considered ready for larger-scale LoCoMo evaluation.

## Methodological lesson

This experiment strengthens the project's central methodological point:

> Lifecycle attribution and answer evaluation must be validated independently. A correct engineering fix to the scorer does not automatically imply that the remaining answer failures are reasoning failures.

The current n=50 result is therefore a **protocol-validation checkpoint**, not a final quantitative claim about the prevalence of F6 reasoning failures.
