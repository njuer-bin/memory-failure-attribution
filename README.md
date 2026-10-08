# Memory Failure Attribution

**From Memory Formation to Reasoning: Diagnosing Information Loss in Long-Term LLM Agents**

This repository studies a diagnostic question:

> When a long-term LLM agent gives a wrong answer, where did the failure first occur?

Instead of treating every error as retrieval failure, the project traces required evidence across the complete lifecycle:

Conversation → Formation → Storage → Evolution → Retrieval → Reranking → Context → Reasoning → Answer

## Research questions

- **RQ1 — Failure Attribution:** At which lifecycle boundary does required evidence first become unavailable?
- **RQ2 — Evidence Preservation:** How much required evidence survives each memory stage?
- **RQ3 — Downstream Answer Failure:** Can an answer remain incorrect when required evidence reaches the final context?
- **RQ4 — Attribution Reliability:** How does answer-evaluation quality affect failure attribution?

## Failure taxonomy

- **F1 Formation** — evidence exists in the conversation but is not extracted into usable memory.
- **F2 Storage** — extracted memory is not persisted or becomes inaccessible.
- **F3 Evolution** — updates, stale facts, or conflicts are handled incorrectly.
- **F4 Retrieval** — required evidence exists in memory but is not retrieved or reranked into the usable set.
- **F5 Context** — required evidence is lost before the final answer context.
- **F6 Reasoning** — required evidence reaches the final context and a semantically incorrect answer is still produced.
- **E0 Evidence Insufficiency** — Gold Evidence does not actually establish the attribute requested by the question, or the benchmark evidence/question pairing is mismatched.
- **EVAL Semantic Uncertainty** — answer evaluation is not reliable enough to support attribution.

F6 is treated as a **candidate attribution** only when evidence is sufficient, all required evidence reaches final context, and semantic evaluation is sufficiently confident.

## Repository structure

- memory_engine/ — reusable memory components ported from njuer-bin/agent_memory.
- tracing/ — lifecycle evidence tracing and first-loss attribution.
- evaluation/ — evidence, lexical answer, semantic answer, temporal, and failure metrics.
- experiments/ — real-system, oracle, calibration, ablation, and baseline experiments.
- datasets/ — benchmark adapters and diagnostic annotations.
- api/ — service entry points inherited from the AML implementation.
- tests/ — regression and benchmark tests.
- docs/ — research formulation, experiment protocol, and progress history.

## Oracle experiments

The core diagnosis compares three controlled conditions:

1. **Real Memory:** real conversation → real memory → retrieval → context → answer model.
2. **Oracle Memory:** Gold Evidence bypasses the memory formation/storage/evolution uncertainty and is supplied to the downstream memory-side path.
3. **Oracle Context:** Gold Evidence is supplied directly to the final answer context.

The oracle conditions are controls, not competing production systems. Their purpose is to isolate memory-induced evidence loss from downstream answer failures.

## Answer evaluation and attribution protocol

A key methodological lesson from the first 10-sample experiment is that lexical answer matching is insufficient for open-ended benchmark QA.

For example, the evidence can state:

> The play I attended was actually a production of The Glass Menagerie.

while the correct concise answer is simply:

> The Glass Menagerie.

A token-F1 scorer can incorrectly mark the concise answer as wrong when the benchmark reference contains a longer sentence.

The project therefore keeps the original reproducible lexical metrics:

- Exact Match (EM)
- Token F1

and adds a semantic evaluation layer that separately asks:

1. **Is the Gold Evidence sufficient to answer the exact question?**
2. **If sufficient, is the candidate answer semantically correct?**
3. **Is the evaluator confident enough to support attribution?**

The attribution rule is conservative:

    Answer evaluation
          ↓
    Evidence sufficient?
       ├── no  → E0_EVIDENCE_INSUFFICIENT
       └── yes
             ↓
       Gold Evidence reaches final context?
       ├── no  → F1–F5
       └── yes
             ↓
       Semantically incorrect + non-low confidence
             → F6_REASONING_CANDIDATE

If the evaluator itself is unavailable or uncertain, the result is recorded as
EVAL_SEMANTIC_UNCERTAIN rather than being forced into F6.

The semantic evaluator also contains a narrow lexical-anchor adjudication rule:
when the judge says evidence is sufficient but incorrectly rejects a candidate that
contains a meaningful exact phrase from the evidence, the result can be repaired.
This is deliberately disabled for evidence-insufficient cases, so merely mentioning
an entity such as "Serenity Yoga" does not prove that the evidence answers "Where do
I take yoga classes?"

This distinction is important because answer correctness is upstream of F6 attribution:

Evidence tracing + evidence sufficiency + reliable answer evaluation → reliable failure attribution

## Diagnostic metrics

The project records:

- stage-level Evidence Recall
- complete evidence availability
- first-loss stage
- failure distribution
- Exact Match
- Token F1
- semantic answer correctness
- oracle gaps
- bootstrap confidence intervals

## Current experiment

### Preliminary LongMemEval sanity-check

Dataset: longmemeval_s_sample10

- Samples: 10
- Errors: 0
- Answer model: local Ollama qwen2.5:7b
- Real Memory evidence recall: 1.00 at Formation, Storage, Evolution, Retrieval, Rerank, and Context
- First-loss distribution: none in all 10 samples

The initial lexical scoring produced:

| Mode | Accuracy | EM | Token F1 |
|---|---:|---:|---:|
| Real Memory | 0.70 | 0.40 | 0.6813 |
| Oracle Memory | 0.50 | 0.40 | 0.5808 |
| Oracle Context | 0.50 | 0.40 | 0.5808 |

However, post-hoc inspection showed that lexical scoring can create apparent answer failures when a concise correct answer is compared with a longer reference.

Semantic calibration then exposed two additional issues: the semantic judge itself produced false-negative judgments, and some Gold Evidence did not fully answer the exact question. In the 10-sample calibration, the four apparent F6 candidates were reclassified as:

- e47becba — evaluator false negative
- 58bf7951 — evaluator false negative
- 6ade9755 — E0 evidence/question mismatch
- 58ef2f1c — E0 evidence/question mismatch

The revised 10-sample calibration now contains **0 F6 reasoning candidates**, **1 E0 evidence-insufficiency case**, and **0 semantic-evaluation-uncertain cases**. This is a protocol-calibration result, not evidence that F6 never occurs. The remaining E0 case is the local-animal-shelter fundraising-dinner question, whose Gold Evidence describes a different fundraising dinner. Oracle Memory scores 10/10 semantically, while Oracle Context remains 9/10 because the same deficient Gold Evidence is supplied directly to the answer model.

The unexpected Real Memory > Oracle Context ordering is also not interpreted as a memory-system advantage. It is being investigated jointly with answer-evaluation calibration.

## Semantic calibration

Run semantic evaluation on the already completed experiment without re-running memory ingestion:

    G:\\aconda\\python.exe -u -m experiments.semantic_calibration

This reads:

    results/oracle_experiments/comparison.jsonl

and writes:

- results/oracle_experiments/comparison_semantic.jsonl
- results/oracle_experiments/semantic_summary.json

The semantic judge uses the local Ollama model and evaluates each existing answer against the question and Gold Evidence.

For reproducibility, the lexical metrics remain stored alongside the semantic verdict.

## Research status

The project currently has:

- reusable long-term memory infrastructure
- provenance-aware lifecycle tracing
- first-loss attribution
- Real / Oracle Memory / Oracle Context controls
- reproducible answer generation
- lexical answer metrics
- semantic answer calibration
- post-hoc anomaly analysis

The revised n=10 semantic calibration gate is now stable. The next step is to freeze this protocol and scale to n=50 LongMemEval samples, followed by inspection and then larger evaluation. LoCoMo cross-benchmark validation and statistically useful failure-attribution tables come after the larger LongMemEval run.

Detailed experimental history is maintained in docs/RESEARCH_LOG.md.

## Relationship to agent_memory

njuer-bin/agent_memory remains the AML competition implementation. This repository is a research fork that reuses its memory infrastructure while adding explicit lifecycle tracing, failure attribution, controlled oracle experiments, answer-evaluation calibration, and reproducible diagnostics.
