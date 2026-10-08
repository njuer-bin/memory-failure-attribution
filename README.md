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

F6 is treated as a **candidate attribution** until answer correctness has been validated by the semantic evaluation protocol.

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

## Two-layer evaluation protocol

A key methodological lesson from the first 10-sample experiment is that lexical answer matching is insufficient for open-ended benchmark QA.

For example, the evidence can state:

> The play I attended was actually a production of The Glass Menagerie.

while the correct concise answer is simply:

> The Glass Menagerie.

A token-F1 scorer can incorrectly mark the concise answer as wrong when the benchmark reference contains a longer sentence.

The project therefore keeps the original reproducible lexical metrics:

- Exact Match (EM)
- Token F1

and adds an independent semantic answer evaluation layer:

- **Semantic Correctness** — whether the candidate answer correctly answers the question and is supported by Gold Evidence, without requiring lexical overlap with a long reference sentence.

This distinction is important because answer correctness is upstream of F6 attribution:

Evidence tracing + reliable answer evaluation → reliable failure attribution

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

However, post-hoc inspection found that some apparent errors were actually **reference-answer lexical mismatches**. For example, concise answers such as The Glass Menagerie and From a sports store downtown. are semantically supported by the evidence even though their token overlap with a longer reference can be low.

Therefore the original 3 F6 cases are now treated as **F6 candidates**, not confirmed reasoning failures.

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

The immediate next step is to run semantic calibration on the existing 10 samples. Only after the answer-evaluation protocol is stable should the benchmark be scaled to 50–100+ LongMemEval samples, followed by LoCoMo cross-benchmark validation and statistically useful failure-attribution tables.

Detailed experimental history is maintained in docs/RESEARCH_LOG.md.

## Relationship to agent_memory

njuer-bin/agent_memory remains the AML competition implementation. This repository is a research fork that reuses its memory infrastructure while adding explicit lifecycle tracing, failure attribution, controlled oracle experiments, answer-evaluation calibration, and reproducible diagnostics.
