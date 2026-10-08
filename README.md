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

The project records Evidence Recall, Evidence Precision, Complete Evidence, Answer F1/EM, Temporal Accuracy, Failure Distribution, and first-loss accuracy. Answer scoring is now implemented for the oracle experiment using a configurable local Ollama model plus exact match/token-F1 scoring; an answer-level F6 reasoning attribution is emitted when the final context contains all required evidence but the answer remains incorrect.

## Relationship to agent_memory

njuer-bin/agent_memory remains the AML competition implementation. This repository is a research fork that reuses its memory infrastructure while adding explicit lifecycle tracing, failure attribution, controlled oracle experiments, and reproducible diagnostics.


### Latest preliminary result (2026-10-08)

On a 10-sample LongMemEval sanity-check, the Real Memory condition achieved 1.00 evidence recall at Formation, Storage, Evolution, Retrieval, Rerank, and Context, with no evidence-level first loss. Answer scoring with local Ollama `qwen2.5:7b` classified 7/10 Real Memory answers as correct, versus 5/10 for both Oracle Memory and Oracle Context under the current exact-match-or-token-F1>=0.5 protocol. Three Real Memory cases were provisionally attributed to F6 because required evidence reached final context while the answer remained incorrect.

These numbers are preliminary (`n=10`) and are not yet benchmark-level conclusions. In particular, the unexpected Real Memory > Oracle ordering requires per-example inspection and scoring calibration. Detailed experimental history is maintained in `docs/RESEARCH_LOG.md`.

## Research status

The reusable memory engine, lifecycle tracing, oracle controls, and benchmark answer scoring are now in place. The next stage is to calibrate the answer threshold and run larger LongMemEval/LoCoMo samples, then generate statistically useful failure-attribution tables and oracle comparisons.
