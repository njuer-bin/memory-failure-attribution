# Research Backlog

Backlog is ordered by expected information gain, not by implementation convenience. Reorder when new evidence justifies it; record substantive changes in `DECISION_LOG.md`.

## P0 — Resolve nearest-work overlap

### B-001: Obtain and audit REALM supplementary archive
- **Why:** REALM is the closest direct work on query-time memory false-drops.
- **Tasks:** Locate official OpenReview submission 52 archive; inspect source code, generated dataset, prompts, frozen outputs, grading/audit reports, calibration sensitivity.
- **Acceptance:** Record exact archive URL/identifier, files inspected, code entry points, benchmark construction, interventions, metrics, and limitations. If inaccessible, record attempts and blockers.
- **Do not:** Claim faithful reproduction before executing and verifying the artifact.

### B-002: Full SPARE-RAG method and artifact audit
- **Why:** It overlaps strongly with dependency-aware deletion and chain-preserving verification.
- **Tasks:** Inspect full methods, appendix, ablations, evidence-need representation, sufficiency verifier, rollback logic, datasets, and code availability.
- **Acceptance:** A feature-by-feature overlap table and explicit statement of what would be redundant in the proposed study.

### B-003: Audit MemConflict and STALE/CUPMem implementations
- **Tasks:** Inspect benchmark scripts, conflict/state generation, evidence labels, retrieval diagnostics, temporal logic, and evaluation.
- **Acceptance:** Verified description of covered constructs and any uncovered causal intervention, with source links and artifact status.

### B-004: Audit Weighted Memory Tree poisoning experiments
- **Tasks:** Inspect exactly where poisoning is injected, what is measured, whether provenance is tracked, whether poisoned memories are quarantined/removed, and whether the agent detects poisoning itself.
- **Acceptance:** A precise overlap matrix. Do not use “first” claims without a broad search.

## P1 — Validate annotation process

### B-005: Execute LoCoMo pilot packet generator
- **Tasks:** Run `experiments/prepare_locomo_annotation_packet.py` against the official local dataset; verify output paths and that raw dialogue excerpts stay outside the repository.
- **Acceptance:** Actual successful command/output, generated packet location, and validation summary. Do not claim success from code inspection alone.

### B-006: Two-annotator dry run
- **Tasks:** Obtain independent annotations for the five pilot examples; adjudicate disagreements; revise role/necessity definitions.
- **Acceptance:** Per-field agreement, confusion matrix, suitable reliability statistic with caveats for tiny n, disagreement examples, revised codebook. Five examples remain a process pilot only.

### B-007: Expand annotation sampling and estimate power
- **Dependency:** B-006 and novelty gate.
- **Tasks:** Define independent conversation/trajectory units, stratified sample plan, minimum detectable effect, clustering assumptions, annotation budget.
- **Acceptance:** Written sample-size plan before confirmatory data collection.

## P2 — Controlled experiment design (blocked pending novelty gate)

### B-008: Freeze causal intervention protocol
- **Tasks:** Define fixed candidate memory pool; paired drop/no-drop counterfactuals; generator/model/prompt/context budget controls; primary outcome; role × necessity factors; alternative-path and temporal moderators.
- **Acceptance:** Versioned protocol with pre-registered inclusion, exclusions, metrics, statistical model, clustering, multiple comparisons, and stop conditions.

### B-009: Pilot intervention and confound audit
- **Dependency:** B-008 approval and bounded budget.
- **Acceptance:** Reproducible pilot, negative controls, manipulation checks, retrieval-confound test, cross-model robustness report.

## P3 — Paper decision

### B-010: Go/no-go research contribution review
- **Acceptance:** Skeptical review of novelty, construct validity, causal identification, external validity, and expected contribution. Recommend continue, pivot, or stop with reasons.

## Run selection rule

At each autonomous run:
1. Select the highest-priority unblocked task.
2. Prefer tasks that reduce a major uncertainty over tasks that merely add code.
3. Do not start P2 before P0 novelty audit and P1 annotation feasibility are sufficiently resolved.
4. Do not repeat completed tasks unless a new source or discrepancy warrants it.
5. If blocked, perform the next independent P0/P1 task.