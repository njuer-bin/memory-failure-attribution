# Current Research State

**As of:** 2026-11-08  
**Phase:** Phase 0 — novelty, artifact, and annotation feasibility audit  
**Status:** Exploratory; no causal model experiment has been run.

## Current question

Does the query-specific evidence role of a dropped memory item predict downstream answer damage in long-horizon conversational memory after separating evidence necessity and controlling alternative paths, temporal validity, query intent, and structural confounds?

## What is actually complete

- Initial research protocol drafted: `docs/MEMORY_FILTERING_RESEARCH_PROTOCOL.md`.
- Preliminary nearest-work matrix drafted: `docs/RELATED_WORK_MATRIX.md`.
- Annotation guidelines and JSON schema created.
- LoCoMo official dataset provenance and category mapping audited.
- Category 1 is multi-hop; category 3 is open-domain.
- Five dry-run questions from five conversations are recorded in `docs/LOCOMO_PILOT_MANIFEST.json`.
- The five manifest entries were checked against the official dataset for category, question, answer, and evidence IDs (5/5 integrity checks passed).
- Annotation sheet prepared for two independent annotators.

## What is NOT complete

- The five questions have not been human-annotated.
- The annotation packet generator has not been successfully executed end-to-end in the user's local environment.
- No inter-annotator agreement has been calculated.
- No REALM supplementary archive has been downloaded or audited.
- SPARE-RAG full artifact/reproduction status has not been fully checked.
- MemConflict and STALE/CUPMem scripts/data-generation pipelines have not been fully audited.
- Weighted Memory Tree poisoning protocol has not been fully inspected.
- No causal deletion intervention or model experiment has been run.
- No sample-size/power analysis has been completed.
- No paper-ready novelty claim is established.

## Known major overlap risks

- REALM 2026: query-time memory filtering, controlled resolver false-drops/false-keeps, downstream answer impact.
- SPARE-RAG: fixed candidate pool, multi-hop evidence repair, sequential deletion, chain-preservation verification and rollback.
- TSHMem/TiMem: temporal conversational memory structures, retrieval, consolidation.
- MemConflict and STALE: cross-session conflict, stale-state validity and state resolution.
- Weighted Memory Tree: long-horizon retention and controlled memory-poisoning experiments.

Do not claim novelty for generic dependency-aware pruning or false-drop harm.

## Next recommended work

1. Obtain and inspect REALM's OpenReview supplementary archive (submission 52): code, generated data, prompts, frozen outputs, grading/audit reports.
2. Read SPARE-RAG methods, appendices, and any released artifact; map exact experimental overlap.
3. Audit MemConflict and STALE/CUPMem scripts and benchmark construction.
4. Read Weighted Memory Tree's poisoning experiment carefully: injection stage, provenance, quarantine/removal, and agent self-detection.
5. Run the LoCoMo annotation packet generator locally and obtain two independent dry-run annotations.
6. Revise the annotation codebook based on disagreements before scaling.

## Current human decision needed

None for the low-cost Phase 0 audits. Human approval is required before changing the core research question, starting expensive model runs, changing a frozen confirmatory protocol, deleting data, or merging to main.

## Last-run discipline

This file must describe only verified work. Every autonomous run should append a dated entry to `docs/RESEARCH_LOG.md` and update this file only when state materially changes.