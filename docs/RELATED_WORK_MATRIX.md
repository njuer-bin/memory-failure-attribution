# Phase 0 Literature Audit: Memory Filtering and Evidence-Chain Preservation

> **Status:** Preliminary audit v0.1
> **Date:** 2026-11-08
> **Scope:** Closest work relevant to evidence deletion, multi-hop evidence preservation, and long-horizon conversational memory. This is a working comparison, not an exhaustive systematic review.

## Executive conclusion

The original proposed method contribution—an evidence-dependency-aware filter that checks whether deletion breaks a multi-hop evidence chain—is **not novel as currently phrased**.

Two 2026 papers create substantial overlap:

1. **REALM 2026** directly studies query-time memory filtering, controlled false-drop/false-keep errors, and downstream answer degradation.
2. **SPARE-RAG (Information, 2026)** studies fixed-candidate-pool multi-hop evidence repair and verification-guided sequential pruning. It explicitly proposes a deletion, constructs a tentative child evidence state, checks chain preservation and per-need coverage, and commits or rolls back the deletion.

The remaining plausible research space is narrower and must be tested: **long-horizon conversational memory**, where evidence is distributed across sessions, may be updated or superseded, has provenance and temporal scope, and must support different query intents (current-state, historical-state, and cross-session aggregation). A role/necessity experiment could be an empirical extension in this setting, but its novelty is not yet established.

Do not claim a new generic dependency-aware pruning algorithm on the basis of the current plan.

## Closest-work comparison

| Work | Setting | What it manipulates | Direct overlap | Remaining distinction to test |
|---|---|---|---|---|
| Vinayaka, REALM 2026, “When Should LLM Agents Forget?” | Memory-conditioned QA; synthetic validity chains plus a MemoryAgentBench diagnostic | Query-time filtering/assembly under controlled resolver corruption; targeted false-drop and false-keep | Memory filtering errors, query-critical evidence loss, fixed candidate memory set, downstream answer impact | Does not model query-specific Direct/Bridge roles as a separate factor; does not test long multi-session evidence dependency graphs, planning/tool trajectories, or persistent deletion |
| Guo et al., SPARE-RAG, Information 2026, 17(10), 1052 | Multi-hop RAG over fixed candidate passage pools; HotpotQA, 2WikiMultiHopQA, MuSiQue | Need planning, full-pool need-to-passage coverage, evidence repair, sequential deletion proposal, parent/child sufficiency verification, rollback/commit | Very strong overlap with dependency-aware deletion and preserving multi-hop support under a fixed candidate set | RAG passage pools rather than evolving conversational agent memory; paper's stated scope does not establish long-horizon memory formation/evolution, temporal validity, provenance-aware cross-session memory, or historical-vs-current query intent |
| LoCoMo, Maharana et al., ACL 2024 / arXiv 2024 | Very long-term conversational memory benchmark | QA over ten public conversations, including multi-hop, temporal, open-domain, single-hop, adversarial questions | Provides a naturalistic cross-session memory test bed and evidence turn IDs | Does not provide Direct/Bridge/Background labels, dependency graphs, or counterfactual necessity annotations |
| MemoryAgentBench, ICLR 2026 | Incremental multi-turn memory benchmark | Memory competencies including retrieval, test-time learning, long-range understanding, conflict resolution | Useful harness and external memory-system validation | Benchmark scores alone do not identify which evidence role was deleted or whether a dependency path was broken |

## Detailed notes

### 1. REALM 2026

**Citation:** Samarth Vinayaka. 2026. *When Should LLM Agents Forget? Memory Filtering Under Query-Critical Resolver Errors.* Proceedings of the Second Workshop for REsearch on Agent Language Models (REALM 2026), pp. 212–225. DOI: 10.18653/2026.realm-1.16.

- ACL Anthology: https://aclanthology.org/2026.realm-1.16/
- PDF: https://aclanthology.org/2026.realm-1.16.pdf

Relevant design:
- Decomposes the path into Resolver, Assembly, and Generator.
- Holds candidate memories and generator fixed while varying resolver quality and assembly policy.
- Uses controlled false-drop and false-keep interventions.
- Reports false-drop as more damaging than false-keep in its targeted probe.
- Explicitly scopes “forgetting” to query-time omission: excluded memories remain in the persistent store.

Important boundary:
- The paper explicitly says it does not evaluate permanent erasure, multi-turn trajectories, planning, or tool use.
- Its central question is validity resolution and packaging, not the functional position of evidence in a cross-session derivation graph.
- It already establishes that query-critical false drops matter. That statement cannot be reused as this project's novelty claim.

Artifact note:
- The paper's Artifact Availability section identifies an OpenReview supplementary archive with code, generated data, prompts, frozen outputs, and reports. The actual archive has **not yet been downloaded or audited** in this project. Do not describe a reproduction as faithful until the artifact is inspected.

### 2. SPARE-RAG (high-priority nearest neighbor)

**Citation:** Ziyao Guo, Yixuan Zhang, Yuhao Huang, Jieyan Liu, and Ke Zhang. 2026. *SPARE-RAG: Evidence Repair and Verification-Guided Sequential Neural Pruning for Multi-Hop RAG.* Information 17(10), 1052. Published 21 October 2026. DOI: 10.3390/info17101052.

- Article: https://www.mdpi.com/2078-2489/17/10/1052
- DOI: https://doi.org/10.3390/info17101052

Relevant method:
1. Generate explicit information needs.
2. Build a full candidate-pool need-to-passage coverage table.
3. Repair missing support before pruning.
4. Propose one passage deletion at a time conditioned on the current evidence state.
5. Construct a tentative child state.
6. Verify chain preservation and per-need coverage.
7. Commit or roll back the deletion; recompute priorities after accepted state changes.

The paper evaluates HotpotQA, 2WikiMultiHopQA, and MuSiQue with fixed candidate pools. Its ablation explicitly measures broken evidence chains when the verification gate is removed.

**Novelty consequence:** A method described simply as “score a memory's dependency importance, simulate its deletion, and keep it if the evidence chain breaks” would substantially overlap SPARE-RAG. A generic dependency-aware filter should therefore be removed from the novelty claim unless a precise, defensible distinction is found.

Potential distinction—not yet a novelty claim:
- The unit is a memory derived from a long conversational history, not a retrieved RAG passage.
- Memory items can be updated, superseded, temporally scoped, or linked to provenance across sessions.
- The same memory can be necessary for a historical query but invalid for a current-state query, or vice versa.
- Query-time filtering errors may interact with memory evolution and the provenance of intermediate facts.
- LoCoMo can provide cross-session evidence, while a second benchmark/system is needed for external validation.

The article's abstract and main text were inspected in the preliminary audit. Its code/model-checkpoint release is described as future work in the data-availability statement; no public artifact was verified during this audit. Re-check before attempting replication.

### 3. LoCoMo

**Citation:** Adyasha Maharana et al. *Evaluating Very Long-Term Conversational Memory of LLM Agents.* ACL 2024 / arXiv:2402.17753.

- Official repository: https://github.com/snap-research/locomo
- Data file: data/locomo10.json
- License file: LICENSE.txt (CC BY-NC 4.0)

Official README confirms:
- Ten public conversations.
- Turn-level dia_id, speaker, and text.
- QA items include question, answer, category, and evidence dialog IDs when available.
- Session summaries and observations are generated fields, not the same as raw dialogue evidence.

**Category mapping warning:** The integer category IDs in locomo10.json do not follow the order in which the paper lists task names. The official evaluation code (task_eval/evaluation.py) treats category 1 as multi-hop (partial/sub-answer F1), categories 2, 3, and 4 as temporal/open-domain/single-hop-style evaluation without multi-hop sub-answer splitting, and category 5 as adversarial. The practical mapping is:

| JSON category | Type | Public count |
|---:|---|---:|
| 1 | Multi-hop | 282 |
| 2 | Temporal | 321 |
| 3 | Open-domain | 96 |
| 4 | Single-hop | 841 |
| 5 | Adversarial | 446 |
| **Total** | | **1,986** |

Never select LoCoMo multi-hop questions by assuming category 3. Use category 1 and validate against the official evaluation implementation.

**Sampling limitation:** The ten conversations are the independent top-level clusters. The 282 multi-hop questions are not 282 independent conversations. Use conversation-clustered inference and be explicit that ten clusters limit generalization and cluster-bootstrap precision.

**License limitation:** CC BY-NC 4.0 is non-commercial. Do not commit the raw JSON or large copied dialogue excerpts to this repository. Keep source IDs and derived annotation records only where permitted, include attribution, and review the license before redistributing transformed data.

### 4. Current overlap judgment

| Proposed element | Status |
|---|---|
| False-drop can damage answer quality | Already established by REALM |
| Multi-hop evidence can be lost by deletion | Already addressed by SPARE-RAG and broader multi-hop evidence-selection literature |
| Fixed candidate set + counterfactual deletion | Already present in REALM/SPARE-RAG-style experimental designs |
| Verify whether a deletion breaks a support chain | Directly present in SPARE-RAG |
| Separate evidence role from necessity | Potentially useful operational factor; exact prior-art coverage remains to be audited |
| Cross-session conversational memory with temporal evolution/provenance | Plausible setting-specific gap; needs more closest-work search |
| Interaction between query intent, temporal validity, provenance, and evidence dependency | Candidate research question; not yet validated as novel |
| New generic dependency-aware pruning model | **Do not claim** |

## Revised research direction (provisional)

Before building a filter, run a small empirical study with the following more specific question:

> In long-horizon conversational memory, does the downstream cost of a false-drop depend on the memory's query-specific role and temporal/provenance position, after controlling for necessity, redundancy, and alternative evidence paths—and does this relationship differ between current-state, historical-state, and cross-session aggregation queries?

This question is more distinct from SPARE-RAG's RAG pruning setting and REALM's validity-resolver setting, but it is still only a candidate. A targeted literature audit is required for temporal memory, memory conflict resolution, query intent, and evidence provenance.

Ablation-only deletion experiments establish the causal cost of losing an item; they do not evaluate a resolver. A separate system-level experiment must inject controlled false-drop errors into a filtering policy and measure whether a memory-aware policy avoids them.

## Immediate actions

1. Inspect REALM's OpenReview supplementary archive and record exact files/settings.
2. Inspect SPARE-RAG appendices, training/evaluation protocol, and any released artifact; verify the exact degree of overlap.
3. Complete a five-question LoCoMo annotation dry run with category 1 examples from different conversations.
4. Search for work on temporal memory filtering, provenance-aware memory, and query-intent-dependent evidence retention.
5. Only then freeze a revised RQ and decide whether to continue, narrow, or abandon the role-based claim.

## Sources

- Vinayaka (2026), REALM: https://aclanthology.org/2026.realm-1.16/
- Guo et al. (2026), SPARE-RAG: https://doi.org/10.3390/info17101052
- Maharana et al. (2024), LoCoMo: https://github.com/snap-research/locomo
- Official LoCoMo evaluation code: https://github.com/snap-research/locomo/blob/main/task_eval/evaluation.py
