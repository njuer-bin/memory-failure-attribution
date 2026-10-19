# Novelty check — lifecycle-stage failure attribution (2026-10-19)

Skill: `aris-novelty-check`. Literature: arXiv API sweep (8 queries, 2025–2026),
7 abstracts read. Cross-model review: `deepseek-v4.1-flash` via the opencode
gateway (Codex MCP reviewer `gpt-6-astra` was unavailable in this session; the
proxy is recorded, not hidden). Traces:
`.aris/traces/novelty-check/` (`arxiv_hits.json`, `abstracts.json`,
`NOVELTY_DOSSIER.md`, `reviewer_deepseek.md`).

## Verdict

**PROCEED WITH CAUTION — 6/10.** Delta: per-question earliest-loss attribution
across a long-term-memory lifecycle via nested Real/Oracle-Memory/Oracle-Context
conditions, showing the dominant failure stage is workload-conditional. The delta
is thin because it integrates existing decoupled-evaluation, bottleneck-diagnosis,
and sufficiency-gating ideas, and the workload-conditional claim is preliminary.

## Closest prior work

| Paper | Year | Overlap | Difference |
|---|---|---|---|
| A-TMA: Decoupling State-Aware Memory Failures (2607.01935) | 2026 | argues decoupled evaluation of bank / retrieval / answer levels | overlay system, no per-question attribution, no oracle ladder |
| Diagnosing Retrieval vs. Utilization Bottlenecks (2603.02473) | 2026 | controlled write×retrieval study on LoCoMo; retrieval dominant | 3 coarse factors, no lifecycle stages, no per-question first-loss |
| Stale, Misattributed, or Late (2610.10265) | 2026 | pre-generation failure measurement | different taxonomy (temporal validity), PFM reference layer |
| Causal Failure Attribution in Agentic RAG (2608.20627) | 2026 | attribution of failures to pipeline hops | interventional multi-hop RAG, not observational memory lifecycle |
| Relevance Is Not Sufficiency (2610.09348) | 2026 | evidence sufficiency, blinded judgment, Gold/Turn Hit | retrieval method, not attribution gate |

## What would make the delta carry (reviewer + our reading)

1. **Scale**: n≫50 per benchmark, multiple systems/seeds, uncertainty intervals.
2. **Intervention**: inject/repair at the attributed stage and show the failure
   rate moves — the oracle-ladder is observational and reads as engineering
   without it.
3. **Distinguish from P2 explicitly**: our LoCoMo retrieval-heavy profile likely
   overlaps 2603.02473; the paper must show that per-question attribution changes
   the conclusion (e.g., which questions to repair) beyond coarse factor
   dominance.
4. **Judge validity**: kappa ≈ 0.03 is a validity threat; report deterministic
   floors and their audit, not only the protocol.
5. **Non-circularity of E0** formalized.

## Venue

CIKM (best fit) or ECIR (if framed as evidence sufficiency / memory retrieval);
COLING for evaluation methodology; NLPCC weakest.

## Consequence for the roadmap

The P1 gate is met (generalization + ≤1 direct prior). P2 (intervention) is now a
publication prerequisite, not an option: without it the work reads as a diagnostic
engineering report at n=50. The n=200 scaling remains required for C2.
