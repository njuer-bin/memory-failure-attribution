# 2026-10-09 — Integrate benchmark-level E0 gate into oracle experiments

## Problem

The experiment already had an evidence-sufficiency evaluator, but the oracle experiment runner could recompute `answer_failure_type` directly from lifecycle coverage. That duplicate path could bypass the E0/EVAL gate and report an F6 reasoning failure even when the benchmark Gold Evidence did not support the question.

## Fix

The oracle experiment runner now:

1. Evaluates Gold Evidence sufficiency before F1–F6 attribution.
2. Uses the benchmark reference answer as the semantic-evaluation candidate for the gate, rather than the Real Memory prediction. This makes the gate independent of the system output being diagnosed.
3. Stores the gate result in each mode and in the experiment summary.
4. Keeps `E0_EVIDENCE_INSUFFICIENCY` for insufficient evidence and `EVAL_EVIDENCE_SUFFICIENCY` for uncertain/judge-error cases.
5. Uses the validated attribution path for the Real Memory failure distribution instead of recomputing an ungated F6 decision.

## Scientific interpretation

This prevents the following invalid inference:

```text
Oracle answer is wrong
        ↓
therefore F6
```

The required order is now:

```text
Gold Evidence
      ↓
Evidence sufficiency gate
      ├── insufficient → E0
      └── sufficient
             ↓
      lifecycle evidence boundary
             ↓
      all evidence reaches context?
             ├── no → F1–F5
             └── yes + benchmark answer scorer says wrong → F6
```

## Validation

Added a regression test ensuring the E0 gate receives the benchmark reference answer rather than a Real Memory prediction.

The next validation step is to run the full test suite and then rerun `locomo_refined_public --limit 10`. Do not interpret F6 prevalence or scale to n=50 until that rerun is audited.
