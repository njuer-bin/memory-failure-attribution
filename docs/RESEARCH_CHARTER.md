# Research Charter

**Project:** Causal diagnosis of query-critical memory filtering errors in long-horizon conversational agents  
**Status:** Exploratory candidate track; novelty and feasibility not yet established  
**Active branch:** `research/memory-filtering-protocol`  
**Last updated:** 2026-11-08

## Mission

Identify and rigorously test a meaningful, falsifiable research question about long-horizon agent memory. A publishable paper is a possible outcome, not an assumption. The project must be willing to narrow, redirect, or stop the current idea when evidence warrants it.

## Candidate research question

In long-horizon conversational memory, how does the causal damage from dropping a query-relevant memory vary with its functional evidence role and actual necessity, and how is this relationship moderated by query intent, temporal validity, and alternative evidence paths?

Candidate query intents:
- current-state query;
- historical-state query;
- cross-session aggregation.

Candidate evidence roles:
- Direct;
- Bridge;
- Background;
- Irrelevant.

Candidate necessity labels:
- Necessary;
- Redundant;
- Optional;
- Distractor.

Role and necessity are separate annotation axes. They must not be collapsed.

## Current novelty boundary

The following are not novel claims by themselves:
- query-critical false-drops can damage answers (REALM 2026);
- generic evidence-chain-preserving deletion/pruning (SPARE-RAG);
- temporal graph retrieval for conversational memory (TSHMem);
- temporal-hierarchical memory consolidation and recall (TiMem);
- conflict and stale-state evaluation (MemConflict, STALE/CUPMem);
- memory retention/poisoning resistance in long-horizon agents (Weighted Memory Tree).

A possible empirical gap is a controlled causal study of heterogeneous false-drop costs in evolving, cross-session conversational memory, with evidence role and necessity independently annotated and confounds controlled. This gap is provisional until the closest papers and artifacts are audited.

## Primary estimand candidate

For evidence role (r), estimate the paired change in failure probability under a controlled drop intervention:

`Delta_r = P(F | do(drop=1), r) - P(F | do(drop=0), r)`

The causal interpretation is valid only if the candidate memory set, model, prompt, generation settings, and all non-intervention inputs are held fixed. The analysis must distinguish necessity, redundancy, alternative paths, dependency depth, and conversation-level clustering.

## Non-goals for the initial study

- Building a generic dependency-aware pruning algorithm before empirical evidence justifies it.
- Claiming permanent deletion, privacy erasure, or consent compliance.
- Claiming broad agent planning/tool-use generalization from static QA.
- Treating LoCoMo's 282 multi-hop questions as 282 independent samples.
- Treating the five-question dry run as annotation evidence.
- Optimizing benchmark score before establishing construct validity.

## Success criteria

A viable study requires:
1. a defensible gap after full nearest-work/artifact audit;
2. operationally reliable role and necessity annotations;
3. a controlled intervention with a clear estimand;
4. enough independent conversations/trajectories for credible inference;
5. robust effects not reducible to graph position, retrieval, or model-specific artifacts;
6. transparent negative/null results and reproducible artifacts.

## Stop / pivot principle

If role/necessity effects disappear after controlling structural properties, if results are entirely explained by retrieval, if a close paper already answers the question, or if annotation reliability is inadequate, stop or redesign rather than forcing the current narrative. See `docs/STOP_CONDITIONS.md`.