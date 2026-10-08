# Memory Failure Attribution

**From Memory Formation to Reasoning: Diagnosing Information Loss in Long-Term LLM Agents**

This repository studies a simple question:

> When a long-term LLM agent gives a wrong answer, where was the required evidence lost?

Instead of optimizing retrieval alone, the project traces evidence through the complete lifecycle:

Conversation → Formation → Storage → Evolution → Retrieval → Reranking → Context → Reasoning

## Failure taxonomy

- **F1 Formation** — evidence exists in the conversation but is not extracted into memory.
- **F2 Storage** — extracted memory is not persisted or becomes inaccessible.
- **F3 Evolution** — updates, stale facts, or conflicts are handled incorrectly.
- **F4 Retrieval** — required evidence exists in memory but is not retrieved.
- **F5 Context** — evidence is retrieved but dropped or truncated before reasoning.
- **F6 Reasoning** — required evidence reaches the model, but the answer is still wrong.

## Repository structure

- memory_engine/ — reusable memory components ported from njuer-bin/agent_memory.
- tracing/ — lifecycle evidence tracing and first-loss attribution.
- evaluation/ — evidence, answer, temporal, and failure metrics.
- experiments/ — real-system, oracle, ablation, and baseline experiments.
- datasets/ — benchmark adapters and diagnostic annotations.
- api/ — service entry points inherited from the AML implementation.
- tests/ — regression and benchmark tests.

## Oracle experiments

The core diagnosis compares:

1. **Real System:** real conversation → real memory → retrieval → LLM.
2. **Oracle Memory:** gold evidence is forced into memory, then the normal pipeline runs.
3. **Oracle Context:** gold evidence is given directly to the answer model.

This separates upstream memory loss from downstream reasoning failure.

## Diagnostic metrics

The project records Evidence Recall, Evidence Precision, Complete Evidence, Answer F1/EM, Temporal Accuracy, Failure Distribution, and first-loss accuracy.

## Relationship to agent_memory

njuer-bin/agent_memory remains the AML competition implementation. This repository is a research fork that reuses its memory infrastructure while adding explicit lifecycle tracing, failure attribution, controlled oracle experiments, and reproducible diagnostics.

## Research status

The reusable memory engine and the first research-layer tracing and metric scaffolding are now in place. The next implementation stage is to connect these traces to the existing LoCoMo and AML test runners, then generate the first failure-attribution tables and oracle comparisons.
