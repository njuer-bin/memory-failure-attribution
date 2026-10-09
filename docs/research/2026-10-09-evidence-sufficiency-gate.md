# 2026-10-09 — Add Evidence Sufficiency Gate Before Failure Attribution

## Motivation

The LoCoMo n=10 experiment can reach the final context boundary while the benchmark evidence itself is insufficient to answer the question. Such cases must not be counted as F6 reasoning failures.

## Change

The oracle experiment now performs a benchmark-level evidence sufficiency check before F1-F6 attribution. The check uses `evaluation.answer_semantic_eval.evaluate_answer()` with the question, the generated candidate answer, and the normalized gold evidence.

The gate has three outcomes:

- `sufficient`: continue to lifecycle attribution.
- `insufficient`: classify the answer failure as `E0_EVIDENCE_INSUFFICIENCY`.
- `uncertain` or judge error: classify as `EVAL_EVIDENCE_SUFFICIENCY` rather than forcing F6.

The semantic judge is used only for the evidence-sufficiency gate. Its answer-correctness verdict does not override the deterministic benchmark answer scorer.

## Attribution contract

```text
Gold Evidence
    ↓
Evidence Sufficiency Gate
    ├─ insufficient → E0
    ├─ uncertain/error → EVAL
    └─ sufficient
          ↓
      lifecycle stages
          ↓
      evidence reaches context?
          ├─ no → earliest F1-F5 boundary
          └─ yes + answer wrong → F6_REASONING
```

Oracle Context remains a reasoning control. Its own incorrect answer is not evidence of memory failure.

## Validation

Added regression tests covering:

1. insufficient evidence → E0;
2. low-confidence sufficiency → EVAL;
3. sufficient evidence + retrieval loss → F4;
4. sufficient evidence + full context + wrong answer → F6.

The next validation command is:

```powershell
G:\aconda\python.exe -m pytest -q
```

Then rerun only LoCoMo n=10 before any larger sample:

```powershell
G:\aconda\python.exe -u -m experiments.run_oracle_experiments --dataset locomo_refined_public --limit 10
```

Do not interpret F6 prevalence until this n=10 run passes the evidence-sufficiency audit.
