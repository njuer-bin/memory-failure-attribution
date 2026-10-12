# Conditional / Transition Failure Analysis

**Date:** 2026-10-12  
**Status:** analysis tool implemented; strict LoCoMo n=50 result pending local execution

## 1. Motivation

The strict LoCoMo n=50 experiment showed Real Memory lifecycle recall of 17% at Formation, 17% at Evolution, 54% at Retrieval, 50.5% at Rerank, and 29% at Context. These raw stage recalls are not independent failure probabilities because a downstream stage can only preserve evidence that survived upstream stages.

For example, a Formation failure can automatically produce an Evolution miss, Retrieval miss, and Context miss for the same Gold Evidence. Counting each of those as separate failures would overstate downstream failure rates.

## 2. Analysis definition

The new post-hoc analysis reports two levels.

### Question level

For each question, a stage passes only when **all** Gold Evidence items are present at that stage under strict turn-level provenance.

For adjacent stages A -> B:

`P(B succeeds | A succeeds)`

is computed only over questions that passed A.

This yields the transition chain:

`Formation -> Storage -> Evolution -> Retrieval -> Rerank -> Context`

### Evidence level

The same conditional survival is also computed per Gold Evidence item. This exposes partial multi-evidence failures that can be hidden by an all-evidence question-level pass/fail rule.

## 3. Evidence gate handling

The analysis reports both:

1. all rows with Gold Evidence; and
2. rows whose Real Memory evidence-sufficiency gate is `sufficient`.

The second view is the primary attribution view because E0 cases should not be interpreted as memory lifecycle failures.

`uncertain` / `error` gate states are not treated as sufficient.

## 4. Implementation

Added:

- `experiments/analyze_transitions.py`
- `tests/test_transition_analysis.py`

The analysis reads the existing `comparison.jsonl` and does **not** rerun MemoryEngine or the answer model.

It writes:

`results/oracle_experiments/transition_analysis.json`

## 5. Execution

After the strict n=50 `comparison.jsonl` is available locally:

```powershell
G:\aconda\python.exe -u -m experiments.analyze_transitions
```

Expected output includes question-level and evidence-level conditional survival/failure for every adjacent lifecycle transition.

## 6. Interpretation rule

Do not read raw downstream recall as an independent failure rate.

The primary quantities for causal interpretation are:

- Evolution failure given Formation success;
- Retrieval failure given Evolution success;
- Rerank failure given Retrieval success;
- Context failure given Rerank success.

Formation remains the initial boundary and therefore has no upstream lifecycle condition.

## 7. Next research gate

After this analysis is executed and inspected:

1. manually audit roughly 20-30 attribution cases;
2. freeze the evaluator/provenance protocol;
3. only then scale LoCoMo to n>=100 and add bootstrap confidence intervals;
4. validate the same methodology on LongMemEval or another benchmark.

No broad claim that Formation is the dominant Agent Memory failure source should be made before these validation steps.
