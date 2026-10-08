# Research Progress Log

This file records reproducible research progress, experimental observations, methodological decisions, and caveats for later paper writing.

## 2026-10-08 — First answer-level failure attribution result

### Research question

The project originally focused on locating where required evidence is lost in the long-term memory lifecycle. The current framework extends this into a broader **memory-to-reasoning failure attribution** problem:

> When a long-term agent gives a wrong answer, did the failure arise because evidence was lost during the memory lifecycle, or did the evidence reach the final context and the downstream reasoner still fail?

The current lifecycle is:

    Conversation
      ↓
    Formation
      ↓
    Storage
      ↓
    Evolution
      ↓
    Retrieval
      ↓
    Reranking
      ↓
    Context
      ↓
    Reasoning
      ↓
    Answer

Failure taxonomy:

- F1 — Formation Failure
- F2 — Storage Failure
- F3 — Evolution Failure
- F4 — Retrieval Failure
- F5 — Context Failure
- F6 — Reasoning Failure

### Experiment

Command:

    G:\aconda\python.exe -u -m experiments.run_oracle_experiments --dataset longmemeval_s_sample10 --limit 10

Dataset: `longmemeval_s_sample10`

Samples: 10

Successful records: 10

Errors: 0

Total runtime: 1295.97 s

Answer model: local Ollama `qwen2.5:7b`

Answer scoring:

- exact match OR token F1 >= 0.5
- deterministic scoring; no LLM judge

### Evidence lifecycle result

For Real Memory:

| Stage | Recall |
|---|---:|
| Formation | 1.00 |
| Storage | 1.00 |
| Evolution | 1.00 |
| Retrieval | 1.00 |
| Rerank | 1.00 |
| Context | 1.00 |

First-loss distribution:

    none: 10

Oracle Memory produced the same 1.00 evidence recall at all measured downstream stages.

Oracle Context intentionally bypasses the earlier evidence stages and supplies Gold Evidence directly to the final context.

### Answer result

| Mode | Correct | Accuracy | Exact Match | Token F1 |
|---|---:|---:|---:|---:|
| Real Memory | 7/10 | 0.70 | 0.40 | 0.6813 |
| Oracle Memory | 5/10 | 0.50 | 0.40 | 0.5808 |
| Oracle Context | 5/10 | 0.50 | 0.40 | 0.5808 |

Model errors: 0 in all three modes.

The preliminary answer-level attribution reported:

    F6_REASONING: 3

### Interpretation

The key observation is that **evidence preservation and answer correctness are not equivalent**.

In these 10 samples, all required Gold Evidence was observed through every measured lifecycle stage in the Real Memory condition, yet only 7/10 answers were classified as correct by the current deterministic scoring rule. Three incorrect cases were therefore candidates for F6 because their required evidence was available through final context.

Oracle Context also achieved only 5/10 under the current scoring protocol. This provides an important control: some failures persist even when Gold Evidence is supplied directly to the answer model.

The unexpected ordering

    Real Memory > Oracle Memory = Oracle Context

should **not** be interpreted as evidence that the real memory system is better than oracle memory. With only 10 samples, possible explanations include additional useful context in the real condition, answer-generation variance, benchmark/reference-answer effects, context-format effects, or limitations of the current token-F1 correctness criterion. This requires per-example inspection before drawing conclusions.

### Methodological significance

The research direction remains consistent with the original thesis, but is now broader:

> **From Memory Formation to Reasoning: Diagnosing Information Loss and Answer Failure Across the Long-Term Agent Lifecycle**

The contribution is a diagnostic framework rather than a claim that one particular retriever or memory architecture is universally superior.

The oracle controls provide a way to separate:

1. failures caused by missing evidence in the memory lifecycle; and
2. failures that remain when evidence is directly available to the reasoner.

### Important caveats

1. `n=10` is a preliminary sanity-check experiment, not a statistically reliable benchmark result.
2. The current answer metric is exact match OR token F1 >= 0.5. It is a first reproducible scoring protocol and requires calibration against LongMemEval answer semantics.
3. F6 should currently be described as an operational/candidate attribution under this scoring protocol, not as a universally proven cognitive reasoning failure.
4. The English analyzer provides basic LongMemEval formation coverage and is not a comprehensive semantic parser.
5. The experiment demonstrates evidence-level preservation on this sample; it does not imply 100% lifecycle performance on LongMemEval as a whole.

### Next experiments

1. Inspect all 10 examples at the question/reference/prediction/evidence level.
2. Specifically inspect the 3 candidate F6 cases.
3. Explain the Real Memory > Oracle Context anomaly before scaling.
4. Calibrate answer scoring and threshold.
5. Run a larger LongMemEval sample (50–100+).
6. Add LoCoMo or another complementary long-term memory benchmark.
7. Produce failure-attribution tables, oracle gaps, and confidence intervals for the paper.

### Paper-ready takeaway

A useful current formulation is:

> Long-term agent failures should not be treated solely as retrieval failures. Even when required evidence survives the memory lifecycle and reaches the final context, the answer can still be incorrect. Oracle controls therefore allow memory-induced evidence loss to be separated from downstream answer failures.

This statement is a preliminary research observation and should be validated on larger samples before being presented as a general empirical claim.