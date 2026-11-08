# Research Decision Log

Append new decisions; do not rewrite historical decisions. Correct factual errors with a dated superseding entry.

## D-001 — Narrow generic dependency-aware pruning claims
- **Date:** 2026-11-08
- **Status:** Active
- **Decision:** Do not claim a novel generic dependency-aware memory pruning algorithm.
- **Evidence:** REALM 2026 directly studies query-time memory false-drops; SPARE-RAG studies fixed-pool multi-hop evidence repair, sequential pruning, chain-preservation verification, and rollback.
- **Consequence:** Treat the current track as a causal diagnostic study in long-horizon conversational memory, not a new generic pruning method.
- **Revisit if:** Full artifact audit reveals a materially different and defensible gap, or a new closest-work paper invalidates the remaining distinction.

## D-002 — Separate evidence role from evidence necessity
- **Date:** 2026-11-08
- **Status:** Active
- **Decision:** Annotate functional role and necessity independently.
- **Rationale:** A Bridge item may have alternative paths; a Direct item may be the only necessary support. Collapsing the labels confounds functional position with necessity.
- **Consequence:** Any role-specific effect must be estimated within comparable necessity/alternative-path strata and adjusted for structural properties.

## D-003 — LoCoMo category and clustering audit
- **Date:** 2026-11-08
- **Status:** Active
- **Decision:** Use category 1 for multi-hop QA; category 3 is open-domain. Treat conversation as a clustering unit.
- **Evidence:** Official LoCoMo evaluation mapping and dataset integrity checks.
- **Consequence:** Do not treat 282 multi-hop questions as 282 independent observations. Five selected questions are only a dry run.

## D-004 — Defer method construction pending evidence
- **Date:** 2026-11-08
- **Status:** Active
- **Decision:** Do not implement a new graph-pruning algorithm before the empirical gap, annotation reliability, and causal effect are established.
- **Rationale:** Avoid engineering a method around an unverified premise and duplicating SPARE-RAG.
- **Consequence:** Prioritize literature/artifact audits and annotation operationalization.