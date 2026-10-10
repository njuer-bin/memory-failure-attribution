# 2026-10-10 — LoCoMo-Refined n=10 semantic-gate validation

## Purpose

Record the first post-fix LoCoMo-Refined sanity-check after hardening the evidence-sufficiency gate against lexical false positives.

The experiment is deliberately small (`n=10`). It is a validation run for the research protocol, not a statistically reliable benchmark result.

## Code validation before the experiment

Local regression suite:

```text
22 passed in 0.55s
```

The suite covers:

- relative temporal answer evaluation;
- deterministic temporal evidence sufficiency;
- rejection of lexical-overlap-only evidence sufficiency;
- unrelated-evidence rejection;
- E0 evidence-insufficiency attribution;
- F6 evidence/context requirements;
- LoCoMo turn provenance and public evidence resolution;
- oracle experiment use of benchmark answers rather than real predictions.

The key methodological change is that lexical overlap between a candidate answer and evidence no longer bypasses the semantic evidence-sufficiency judge. A phrase appearing in evidence is not by itself proof that the evidence answers the exact question.

## Experiment

Command:

```text
G:\\aconda\\python.exe -u -m experiments.run_oracle_experiments --dataset locomo_refined_public --limit 10
```

Input dataset: `locomo_refined_public`

Samples: 10

Successful rows: 10

Output:

`results/oracle_experiments/comparison.jsonl`

## Sample-level result

The current attribution distribution is:

| Attribution | Count | Share |
|---|---:|---:|
| E0_EVIDENCE_INSUFFICIENCY | 7 | 70% |
| F6_REASONING | 2 | 20% |
| None | 1 | 10% |

The F6 candidates are:

- `conv-26#q0005` — “When did Melanie run a charity race?”
- `conv-26#q0009` — “When did Caroline meet up with her friends, family, and mentors?”

For both candidates, the evidence trace is complete through Formation, Storage, Evolution, Retrieval, Rerank, and Context. The generated answer is still classified as incorrect, so these are operational F6 reasoning candidates under the current semantic protocol.

### Example F6 candidate: q0005

Gold Evidence explicitly states that Melanie ran a charity race “last Saturday.” The generated answer is also “Last Saturday.” Nevertheless, the current semantic answer field is `correct=False` and Token F1 is 0.0. This is a useful diagnostic case because the evidence trace is complete but the answer evaluator does not agree with the apparent semantic match.

### Example F6 candidate: q0009

Gold Evidence states that Caroline met her friends, family, and mentors “last week.” The generated answer is “Last week.” Again, all evidence stages are present, but the current answer field is `correct=False` and Token F1 is 0.0.

These two examples show why answer evaluation itself must remain under calibration. They should not yet be presented as definitive evidence of a reasoning failure.

## Real vs Oracle inversion

Four questions show `real_memory=False` while `oracle_memory=True`:

- `conv-26#q0000`
- `conv-26#q0002`
- `conv-26#q0003`
- `conv-26#q0006`

This is the desired diagnostic signal from the oracle design: supplying better/complete memory evidence can change an incorrect real-memory answer into a semantically accepted answer.

One additional sample, `conv-26#q0007`, is correct in both Real and Oracle conditions.

Thus, using the experiment's semantic `correct` field, the observed counts are:

| Mode | Semantically accepted | Rate |
|---|---:|---:|
| Real Memory | 1/10 | 10% |
| Oracle Memory | 5/10 | 50% |
| Oracle Context | 5/10 | 50% |

These are **not** final benchmark scores; they are n=10 diagnostic observations.

## Important metric discrepancy

The same output also reports a post-hoc Token-F1 threshold sweep. At threshold 0.50 it gives:

| Mode | Token-F1 accuracy |
|---|---:|
| Real Memory | 10% |
| Oracle Memory | 20% |
| Oracle Context | 20% |

This differs from the semantic `correct` counts above. For example, `conv-26#q0000` has answer `Yesterday.` and is marked semantically `correct=True`, while its Token F1 is 0.0.

This discrepancy is now a research-methodology issue that must be resolved before using a single accuracy number in a paper. Lexical metrics remain useful for reproducibility, but they should not be treated as interchangeable with semantic correctness.

## What this experiment establishes

1. The complete experiment pipeline runs successfully on LoCoMo-Refined for n=10.
2. The evidence-sufficiency gate regression tests pass after the lexical-overlap hardening.
3. The oracle controls expose real-memory-to-oracle improvements on multiple samples.
4. The framework can produce explicit E0 and F6 candidate attributions instead of labeling every wrong answer as retrieval failure.
5. Answer evaluation remains a critical dependency of failure attribution; the current semantic-vs-Token-F1 discrepancy must be investigated.

## What this experiment does not establish

- It does not establish population-level accuracy.
- It does not prove that the two F6 candidates are genuine reasoning failures.
- It does not justify comparing the semantic `correct` rate directly with Token-F1 accuracy.
- It does not justify scaling to a large run without first resolving the evaluation discrepancy.

## Next experimental gate

Before increasing the sample size:

1. Preserve the current n=10 result as a reproducible checkpoint.
2. Compare the previous pre-gate result with this post-gate result where available.
3. Inspect the semantic evaluator for the q0005/q0009 false-negative-looking cases.
4. Clarify the relationship between semantic `correct`, EM, and Token F1 in the analyzer.
5. Re-run the n=10 validation after any evaluation fix.
6. Only then scale to LoCoMo n=50 and/or the larger cross-benchmark experiment.

## Research interpretation

The current evidence supports the following cautious formulation:

> A lifecycle-aware memory diagnostic can separate evidence-loss cases from cases in which evidence reaches the final context, but the reliability of that attribution depends directly on the correctness and calibration of the answer-evaluation layer.

This statement is a methodological observation from the current n=10 validation and requires larger-scale validation before being treated as a general empirical claim.
