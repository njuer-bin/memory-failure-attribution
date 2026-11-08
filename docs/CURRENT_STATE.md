# Current Research State

**As of:** 2026-11-08 (initial Research Director audit)  
**Phase:** Phase 0 — novelty, artifact, and annotation feasibility audit  
**Status:** Exploratory; no causal model experiment has been run.  
**Audit report:** `docs/CLAUDE_INITIAL_RESEARCH_AUDIT.md`

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
- `experiments/prepare_locomo_annotation_packet.py` was executed end-to-end against the official pinned dataset (`snap-research/locomo@cbfbc1db...`, fetched outside the repository): 5/5 records written, all evidence turns resolved. The generated packet stays outside the repository. (2026-11-08 audit)
- Official dataset facts re-verified from the pinned commit: 10 conversations, 1,986 QA; category 1 = 282, 2 = 321, 3 = 96, 4 = 841, 5 = 446. (2026-11-08 audit)
- Repository test suite passes: `pytest -q` → 22 passed. (2026-11-08 audit)
- Initial multi-role research audit completed: `docs/CLAUDE_INITIAL_RESEARCH_AUDIT.md`. (2026-11-08 audit)

## What is NOT complete

- The five questions have not been human-annotated.
- No inter-annotator agreement has been calculated.
- No REALM supplementary archive has been downloaded or audited. The paper's Artifact Availability section (OpenReview submission 52) was read, but the archive itself is still not obtained.
- SPARE-RAG full artifact/reproduction status has not been fully checked. Bibliographic metadata and abstract were verified via Crossref/OpenAlex; the MDPI full text returned HTTP 403 and code availability is UNKNOWN.
- MemConflict and STALE/CUPMem scripts/data-generation pipelines have not been fully audited.
- Weighted Memory Tree poisoning protocol has not been fully inspected.
- No causal deletion intervention or model experiment has been run.
- No deletion/intervention code exists (repository-wide grep found none).
- No annotation-schema validator or annotation-agreement script exists; `requirements.txt` does not list `jsonschema` or `pytest`.
- The revised RQ names temporal validity and query intent as moderators, but neither field exists in `schemas/evidence_annotation.schema.json` or `docs/ANNOTATION_GUIDELINES.md`.
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

1. Obtain and inspect REALM's OpenReview supplementary archive (submission 52): code, generated data, prompts, frozen outputs, grading/audit reports. If still unreachable, record the exact blocker and downgrade all negative novelty assertions about REALM to TENTATIVE.
2. Obtain the SPARE-RAG full text/appendices/code (MDPI returned 403); produce a feature-by-feature overlap table.
3. Build a small synthetic evidence-chain set (20–40 items) and validate that role can be annotated independently of necessity before scaling natural-data annotation.
4. Before expanding the LoCoMo sample: add `query_intent` and `temporal_validity` fields to the schema and codebook, define compound-evidence-ID splitting, and add a schema validator plus tests.
5. Propose (L2, needs human approval) narrowing the primary hypothesis to a necessity/redundancy contrast, with role as a secondary/exploratory factor.

## Working-tree blocker (2026-11-08 audit)

The user's local directory `G:\PythonProject\memory-failure-attribution` is on branch `fix/formation-diagnostics-evidence-based` with 76 uncommitted/untracked changes, and does not contain this branch's files. The audit was therefore performed in an isolated clone of `research/memory-filtering-protocol`. No write was made to the `G:` working tree. Landing the audit files there requires the user to commit or stash existing work first.

## Current human decision needed

1. **Working tree:** decide how to reconcile the `G:` working tree (different branch, 76 uncommitted changes) so the audit files can land on `research/memory-filtering-protocol`.
2. **Hypothesis scope:** approve or reject the audit's recommendation to narrow the primary hypothesis to a necessity/redundancy contrast with role as a secondary/exploratory factor. This changes the core hypothesis and therefore requires explicit human approval.
3. No approval is needed for the remaining low-cost Phase 0 audits (REALM/SPARE-RAG/MemConflict/STALE/WMT artifact inspection).

Human approval is required before changing the core research question, starting expensive model runs, changing a frozen confirmatory protocol, deleting data, or merging to main.

## Last-run discipline

This file must describe only verified work. Every autonomous run should append a dated entry to `docs/RESEARCH_LOG.md` and update this file only when state materially changes.