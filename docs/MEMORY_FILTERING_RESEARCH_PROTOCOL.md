# Research Protocol: Evidence-Dependency-Aware Memory Filtering

> **Status:** Protocol draft v0.1 — proposed, not preregistered  
> **Research track:** Memory filtering under evidence dependency  
> **Repository relationship:** Separate exploratory track from the repository's existing memory-failure-attribution claims. It may reuse adapters, provenance utilities, and evaluation infrastructure, but its findings must not be merged into the existing paper's claims without separately documented experiments.  
> **Last updated:** 2026-11-08

## 0. Executive summary

This project studies whether deleting a memory item causes different downstream reasoning damage depending on its query-specific evidence role, after controlling for whether the item is actually necessary and whether alternative evidence paths exist.

The central methodological risk is confounding: a bridge item may appear more important simply because it is the only necessary item, while a direct item may be redundant. Evidence role and evidence necessity must therefore be annotated as separate dimensions.

The first goal is a small, controlled falsification study—not a complete long-horizon agent or a claim of a new memory architecture. Proceed only if role-specific effects remain after controlling for necessity, redundancy, dependency depth, and alternative paths.

## 1. Research question and scope

### 1.1 Primary research question

**RQ1.** Under a fixed candidate-memory set and controlled filtering intervention, does deleting evidence with different query-specific roles (Direct, Bridge, Background) cause different answer-quality degradation after accounting for evidence necessity and alternative derivation paths?

### 1.2 Secondary questions

- **RQ2 — Dependency depth:** Does deletion impact change with the number of inference links in the evidence dependency graph?
- **RQ3 — Redundancy:** Do alternative evidence paths reduce the damage caused by deleting a Direct or Bridge item?
- **RQ4 — Policy value:** Can an evidence-dependency-aware filtering policy reduce answer degradation at a matched filtering/token budget compared with simple filtering baselines?
- **RQ5 — Generalization:** Do controlled findings transfer from constructed evidence chains to manually audited long-dialogue QA examples?

### 1.3 Explicit non-goals for the first study

- No claim that this work solves permanent memory deletion, privacy erasure, or consent management.
- No full comparison of every memory architecture.
- No claim that Bridge evidence is inherently more important than Direct evidence.
- No claim of generalization to all agent tasks from a single benchmark.
- No end-to-end retrieval improvement claim: the primary causal experiment fixes the candidate-memory set and intervenes only at filtering.

## 2. Relationship to prior work and novelty boundary

The closest known work in the current literature review is **REALM 2026, “When Should LLM Agents Forget? Memory Filtering Under Query-Critical Resolver Errors.”** REALM studies query-time filtering, resolver errors, false-drop/false-keep interventions, and downstream answer effects. It also reports limitations around long-horizon trajectories and broader system validation.

This project must not present “false-drop harms answers” or “multi-hop evidence can be lost” as new contributions. The proposed incremental question is narrower:

> Does the functional position of a deleted evidence item in a query-specific dependency structure predict additional damage beyond its necessity, redundancy, and dependency depth?

Before any paper claim is made, the related-work review must verify whether this exact conditional comparison has already been studied in memory filtering, multi-hop QA, information deletion, graph reasoning, and evidence selection.

### 2.1 Novelty gate

The novelty gate is passed only if all are true:

1. The closest prior work does not already perform a matched intervention separating evidence role from necessity/redundancy.
2. The operational definitions and intervention add a measurable construct, not merely renamed labels.
3. The effect is reproducible on held-out data and at least two model configurations.
4. The effect is not fully explained by ordinary evidence recall, token position, context length, or alternative-path availability.
5. A practical filtering policy demonstrates value over matched-budget baselines, if a method contribution is claimed.

If this gate fails, narrow the paper to a replication/extension or stop the proposed role-based claim.

## 3. Operational definitions

All labels are assigned with respect to a specific question and reference answer, not globally to a memory item.

### 3.1 Evidence role (functional dimension)

- **Direct:** The item directly states or entails an answer component without requiring another factual bridge.
- **Bridge:** The item supplies an intermediate relation/state needed to connect other evidence to the answer.
- **Background:** The item may provide context but is not required to derive the answer under the annotated evidence set.

An item may have multiple functions in complex cases. If annotators cannot agree on one primary role, record MULTI_ROLE or UNCERTAIN; do not force a single label.

### 3.2 Evidence necessity (independent dimension)

- **Necessary:** Removing the item makes the reference answer unsupported by the remaining admissible evidence under the annotation protocol.
- **Redundant:** Removing the item leaves at least one valid alternative evidence path to the answer.
- **Distractor/irrelevant:** The item is not needed and does not supply a valid alternative path. It may be topically related or unrelated.
- **Uncertain:** Necessity cannot be decided reliably.

Necessity must not be inferred from role. A Bridge item can be redundant; a Direct item can be the only necessary evidence.

### 3.3 Dependency graph

For each question, construct a directed acyclic graph (DAG) where nodes are atomic evidence units and edges encode “is required to derive / interpret” dependencies. Record:

- evidence-unit ID and source turn/document ID;
- role label(s);
- necessity label;
- dependency parent/child IDs;
- whether an alternative path exists;
- shortest derivation depth;
- annotator confidence and rationale.

The graph is query-specific. Do not infer edges from temporal order alone.

### 3.4 Answerability after deletion

For each candidate deletion, annotators answer: “Can the reference answer still be derived from the remaining evidence without importing outside knowledge?” This remove-one test adjudicates necessity and alternative paths. It is not the model's generated answer.

## 4. Hypotheses and estimands

### 4.1 Primary hypothesis

**H1 (conditional role effect):** At a matched deletion budget, deletion of necessary evidence has a larger effect on answer failure than deletion of redundant/background evidence; and among evidence items matched on necessity, dependency depth, and alternative-path availability, deletion effect may still differ by evidence role.

The second clause is the actual role-specific claim. The first clause is a sanity check, not the novelty claim.

### 4.2 Secondary hypotheses

- **H2:** Deletion damage increases with dependency depth when the deleted item lies on a necessary derivation path.
- **H3:** Alternative valid paths attenuate deletion damage.
- **H4:** An evidence-dependency-aware policy improves answer quality at a matched filtering/token budget over random and simple confidence-based filtering.

### 4.3 Primary outcome

Binary answer correctness judged against the question and admissible evidence. The judge must be blind to intervention condition. A manually adjudicated subset estimates judge error.

### 4.4 Secondary outcomes

- semantic answer score/correctness;
- necessary-evidence recall in final context;
- bridge-evidence recall;
- complete-path availability;
- unsupported-answer rate;
- abstention rate;
- input-token count and latency;
- filtering precision/recall, where gold labels are available.

### 4.5 Causal contrast

Let Y=1 indicate answer failure. For evidence role r, define:

\[
\Delta_r = P(Y=1 \mid do(delete=1), r) -
P(Y=1 \mid do(delete=0), r).
\]

The key comparison is not raw Δ across unmatched groups. It is the conditional role contrast after matching or adjusting for necessity, dependency depth, alternative-path count, question family, and deletion budget.

## 5. Datasets and sampling plan

### 5.1 Controlled evidence-chain set

Construct a small synthetic/controlled set first. Each item contains:

- a question and reference answer;
- a fixed candidate-memory set;
- atomic evidence units;
- a gold dependency DAG;
- controlled Direct / Bridge / Background roles;
- Necessary / Redundant / Distractor labels;
- chain depth and alternative-path count.

Synthetic examples support exact interventions and known ground truth, but cannot establish real-world generalization alone. Vary templates and surface forms to reduce template leakage.

### 5.2 Naturalistic external validation: LoCoMo

LoCoMo is the first naturalistic validation candidate because it contains long conversations, turn identifiers, timestamps, QA items, and evidence-dialog references. It does **not** provide ready-made Direct/Bridge/Background labels or dependency edges; these must be annotated.

Pilot target: **30–50 audited multi-hop questions**, subject to a feasibility review. This is a pilot size, not a claim of adequate power for final confirmatory inference.

Sampling rules:

1. Sample across conversations where possible; do not take all examples from one conversation.
2. Audit question/reference-answer/evidence alignment before annotation.
3. Retain source conversation and question IDs for cluster-aware analysis.
4. Do not treat questions from the same conversation as independent observations.
5. Record exclusions and reasons before running model interventions.

If pilot annotation burden or data quality is unacceptable, revise the sampling plan before scaling. Any replacement benchmark must be justified and versioned.

### 5.3 External benchmark policy

MemoryAgentBench or LongMemEval may be considered after the pilot. Their role is external validation, not a substitute for query-specific evidence-role annotation. Benchmark adapters must preserve original IDs and provenance. Do not compare results across benchmarks as if they were identically sampled.

## 6. Annotation protocol and quality control

### 6.1 Annotation workflow

For each question:

1. Verify that the reference answer answers the exact question.
2. Identify the smallest sufficient evidence set.
3. Split cited turns/documents into atomic evidence units where needed.
4. Annotate role and necessity independently.
5. Draw dependency edges and identify alternative paths.
6. Perform remove-one and, where needed, remove-set checks.
7. Record uncertainty and rationale.

### 6.2 Annotators

- Two independent annotators for all pilot questions.
- Third-person adjudication for disagreements.
- Annotators must not see model outputs or intervention results.
- A written codebook and 5–10 jointly discussed training examples precede formal annotation.

### 6.3 Agreement reporting

Report agreement separately for evidence-unit identification, role labels, necessity labels, dependency-edge decisions, and answerability after deletion. Use Cohen's kappa or an appropriate multi-label/graph agreement measure where applicable, and report raw agreement and class prevalence. Do not report one aggregate agreement number that hides a collapsed label distribution.

### 6.4 Annotation freeze

Before model runs, freeze question IDs, evidence units, role/necessity labels, dependency graphs, exclusion decisions, and adjudication notes.

Any later correction must be logged with the old value, new value, reason, date, and affected experiment IDs.

## 7. Controlled intervention design

### 7.1 Primary causal control

For each question, construct and freeze the candidate-memory set first. All intervention conditions use the same set, ordering policy, prompt, model, decoding parameters, and context budget. The primary experiment does not rerun retrieval after deletion.

This isolates filtering-stage deletion from retrieval recall. Retrieval and ranking experiments, if later needed, are a separate study.

### 7.2 Conditions

| Condition | Intervention | Purpose |
|---|---|---|
| No-drop | Keep all candidate memories | Reference condition |
| Matched random-drop | Delete the same number of items at random | Generic deletion baseline |
| Necessary-Direct | Delete a necessary Direct item | Direct-evidence loss |
| Necessary-Bridge | Delete a necessary Bridge item | Bridge-evidence loss |
| Redundant-Bridge | Delete a redundant Bridge item | Role vs necessity separation |
| Background-drop | Delete a Background item | Non-necessary deletion control |

Not every question supports every condition. Only run a condition when its required annotated item exists; report the eligible denominator for each contrast. Do not manufacture a Bridge item by relabeling a Direct fact.

### 7.3 Matching and randomization

- Match deletion count across conditions.
- Where possible, match deleted-token count or include it as a covariate.
- Randomize memory order and intervention assignment using a recorded seed.
- Keep prompt templates and answer-generation parameters frozen.
- Avoid truncation differences: all conditions obey the same context budget and truncation policy.
- Record exact candidate set, deleted IDs, retained IDs, final context, model version, prompt hash, seed, and output.

### 7.4 Models

Pilot: one locally available model to validate the pipeline.  
Confirmatory stage: at least two model configurations from distinct model families where feasible. Record exact model name, version/snapshot, provider, decoding settings, and date. Model names alone are insufficient for reproducibility.

## 8. Baselines and candidate method

### 8.1 Baselines

- No filtering / no-drop.
- Matched random filtering.
- Simple hard-drop policy based on the available validity/staleness label.
- Confidence-based filtering.
- Soft-retention policy, if the reproduced REALM implementation supports it.
- REALM policy/conditions, only after its supplementary artifact and exact implementation are obtained and verified.

Do not claim a faithful REALM reproduction from a paper-level reimplementation. Label it REALM-inspired until code and settings have been verified.

### 8.2 Candidate policy (exploratory)

An evidence-dependency-aware policy may estimate whether a memory is on a necessary derivation path, is a unique bridge, is replaceable by an alternative path, or is background to the current query.

The policy should avoid deleting high-risk evidence when confidence is low, potentially using quarantine/soft-retain rather than irreversible deletion.

This is a later method-development phase. Do not design the policy around pilot outcomes and then evaluate it on the same questions. Use a held-out set or cross-validation grouped by conversation/query template.

## 9. Statistical analysis plan

### 9.1 Primary analysis

Use paired within-question comparisons wherever each question supports multiple conditions. Report absolute answer-failure rates, paired risk differences, 95% confidence intervals, and per-condition eligible sample counts.

For binary outcomes, use McNemar's test for paired contrasts where appropriate. Use cluster bootstrap by conversation for LoCoMo; do not bootstrap individual questions independently. For multi-factor analysis, use mixed-effects logistic regression with question/conversation grouping where sample size supports stable estimation.

### 9.2 Covariates and interactions

Pre-specified covariates:
- necessity class;
- dependency depth;
- alternative-path count;
- number of candidate memories;
- deleted-token count;
- question category;
- conversation cluster.

Pre-specified interactions:
- deletion × evidence role;
- deletion × necessity;
- deletion × dependency depth;
- role × necessity.

If sample size is too small for a stable multi-way model, report the pilot as descriptive and do not overinterpret p-values.

### 9.3 Multiple comparisons

Declare one primary contrast before confirmatory runs. Treat other contrasts as secondary and apply a suitable multiple-comparison correction (e.g., Holm). Report effect sizes and confidence intervals, not only significance.

### 9.4 Power and sample-size decision

The 30–50 question pilot is for feasibility, annotation reliability, variance estimation, and pipeline debugging. It is not automatically powered for a small interaction effect. After the pilot, perform a power or precision analysis using observed paired discordance/cluster variance, then set confirmatory sample size before collecting or inspecting confirmatory outcomes.

## 10. Implementation plan

### Phase 0 — Artifact and literature audit

**Tasks**
- Obtain and inspect REALM supplementary materials (the paper identifies an OpenReview submission artifact); record exact archive contents and reproduction instructions.
- Verify closest related work, including multi-hop QA, evidence graphs, selective memory filtering, and information deletion.
- Inspect LoCoMo data schema, license, evidence IDs, and adapter behavior.

**Deliverables**
- docs/RELATED_WORK_MATRIX.md
- docs/ARTIFACT_AUDIT.md
- source/version manifest

**Exit gate**
- Exact overlap with REALM and other closest work is documented.
- No unsupported novelty statement remains.

### Phase 1 — Annotation codebook and pilot data

**Tasks**
- Write annotation guidelines and examples.
- Select 30–50 candidate LoCoMo multi-hop questions.
- Audit question/evidence/reference alignment.
- Double-annotate and adjudicate.
- Build evidence-DAG serialization and validation.

**Deliverables**
- data/annotations/ (subject to dataset license and redistribution restrictions)
- docs/ANNOTATION_GUIDELINES.md
- schemas/evidence_graph.schema.json
- agreement report

**Exit gate**
- Agreement is acceptable for primary labels, or definitions are revised and re-annotated.
- Each retained question has a valid evidence graph and documented answerability decision.

### Phase 2 — Controlled intervention pipeline

**Tasks**
- Freeze candidate memory sets.
- Implement deterministic intervention generation.
- Implement no-drop, matched random-drop, and role/necessity-specific deletions.
- Save intervention manifests and exact final contexts.
- Add tests ensuring only intended memory items differ between paired conditions.

**Deliverables**
- interventions/
- experiments/controlled_deletion.py
- tests/test_intervention_invariants.py
- immutable pilot manifest

**Exit gate**
- Automated invariants pass: same candidate set before intervention, matched deletion budget, no unintended prompt/model/context changes.

### Phase 3 — Pilot execution and falsification

**Tasks**
- Run one local model end-to-end.
- Manually audit a subset of answers and judge decisions.
- Analyze role, necessity, depth, and alternative-path effects.
- Inspect failures and verify no context truncation or ID leakage.

**Deliverables**
- results/pilot/
- docs/PILOT_REPORT.md
- reproducible analysis script

**Go/no-go gate**

Proceed only if:
1. annotation and intervention pipeline are reliable;
2. the primary contrast is identifiable from the available sample;
3. observed effects are not trivially explained by necessity, redundancy, token count, or truncation;
4. no major benchmark alignment defect remains.

If not, revise the construct or stop the role-specific claim.

### Phase 4 — Confirmatory experiment

**Tasks**
- Determine sample size from pilot variance/paired discordance.
- Freeze v1.0 protocol, datasets, exclusions, prompts, model versions, and primary contrast.
- Run at least two model configurations.
- Use held-out questions/conversations for policy evaluation.
- Run paired and cluster-aware statistics.

**Deliverables**
- docs/PROTOCOL_v1.0.md
- results/confirmatory/
- docs/STATISTICAL_REPORT.md
- complete experiment manifests

**Exit gate**
- Confirmatory results answer the pre-registered question.
- All exclusions and deviations are disclosed.
- Robustness checks do not overturn the main interpretation.

### Phase 5 — Policy development and external validation

**Tasks**
- Develop evidence-dependency-aware filtering only if the mechanism is supported.
- Compare against matched-budget baselines.
- Evaluate on a held-out split and a second benchmark where annotations can be validated.
- Measure answer quality, evidence preservation, token cost, latency, and abstention.

**Deliverables**
- methods/
- experiments/policy_comparison.py
- results/external_validation/
- ablation and error analysis

**Exit gate**
- The proposed policy must improve a meaningful quality/cost metric over simple baselines.
- If not, publishable value may remain in the empirical finding, but do not claim a superior method.

### Phase 6 — Paper and reproducibility package

**Tasks**
- Write claims strictly bounded by datasets/models/conditions tested.
- Release code, configs, annotation instructions, manifests, and permitted derived annotations.
- Document data licenses, model access requirements, and limitations.
- Re-run a clean reproduction from documented instructions.

**Deliverables**
- paper draft;
- artifact README;
- release checklist;
- limitations and ethics statement.

## 11. Stop conditions and fallback paths

### Stop or substantially reframe if

- Role labels cannot be reliably distinguished from necessity labels.
- The role effect disappears after controlling for necessity, alternative paths, and dependency depth.
- Effects are driven by context truncation, token position, or retrieval differences.
- The effect appears only in one model or one synthetic template family.
- Benchmark evidence does not support the reference answer.
- A matched no-filter/keep-all baseline dominates the proposed policy at acceptable cost.
- The proposed distinction is already covered by closer prior work.

### Fallback paths

1. **Role effect absent, necessity effect robust:** Reframe as a study of evidence necessity and redundancy under filtering; remove the Direct/Bridge novelty claim.
2. **Synthetic effect only:** Keep synthetic work as a mechanism study; do not claim naturalistic generalization.
3. **Annotation reliability weak:** Simplify the ontology, merge ambiguous labels, or use evidence-path necessity as the primary construct.
4. **Policy does not outperform baselines:** Focus on empirical boundary conditions and failure analysis; do not force an algorithm contribution.
5. **REALM artifact unavailable:** Implement a clearly labeled independent baseline from the paper specification and disclose deviations.

## 12. Change-control and protocol versioning

This project is expected to evolve. Changes are allowed, but they must be auditable.

### 12.1 Version rules

- v0.x: exploratory design and pilot changes.
- v1.0: confirmatory protocol frozen before confirmatory outcome inspection.
- v1.x: clarifications or implementation fixes that do not change hypotheses, primary outcomes, sampling, or analysis.
- v2.0: changes to hypotheses, primary estimand, label ontology, sampling frame, or primary statistical analysis.

### 12.2 Required change log fields

Every substantive change must record:
- date and protocol version;
- old decision;
- new decision;
- reason/evidence;
- whether confirmatory outcomes had been inspected;
- affected data, code, and experiment IDs;
- whether the change is exploratory or confirmatory.

### 12.3 No silent changes

Do not overwrite old results after changing labels, prompts, model versions, or analysis. Preserve the original run and create a new run ID. Report deviations from the frozen protocol in the final paper.

## 13. Initial repository structure

Suggested structure; adapt to the existing repository rather than duplicating components:

~~~text
memory-filtering/
├── configs/
├── schemas/
│   └── evidence_graph.schema.json
├── data/
│   ├── raw/                 # source data; do not commit restricted raw data
│   ├── processed/
│   └── annotations/
├── memory/
│   ├── candidate_set.py
│   └── evidence_graph.py
├── interventions/
│   ├── random_drop.py
│   └── targeted_drop.py
├── baselines/
│   ├── no_filter.py
│   ├── hard_drop.py
│   ├── confidence_filter.py
│   └── soft_retain.py
├── methods/
│   └── dependency_aware_filter.py
├── evaluation/
│   ├── answer_judge.py
│   ├── evidence_metrics.py
│   └── statistics.py
├── experiments/
│   ├── pilot.py
│   └── confirmatory.py
├── results/
└── docs/
    ├── PROTOCOL.md
    ├── ANNOTATION_GUIDELINES.md
    ├── RELATED_WORK_MATRIX.md
    ├── ARTIFACT_AUDIT.md
    └── CHANGELOG.md
~~~

Potential reusable components from the existing repository should be imported through explicit adapters. Avoid copying code and silently creating two divergent implementations.

## 14. Reproducibility requirements

Every run must save a machine-readable manifest containing:

- run ID and protocol version;
- dataset name/version/license and source IDs;
- selected/excluded question IDs and reasons;
- candidate-memory set hash;
- evidence annotation version;
- intervention condition and deleted item IDs;
- random seed;
- model/provider/snapshot;
- prompt/template hash;
- decoding settings;
- context budget and actual token count;
- output and judge versions;
- code commit SHA;
- start/end time and error status.

Raw user/private conversation data must not be committed. Follow dataset licenses and store only permitted data/derived annotations.

## 15. Immediate next actions

1. Retrieve and inspect the REALM artifact before implementing a duplicate baseline.
2. Verify LoCoMo schema, license, and multi-hop question/evidence alignment.
3. Draft the annotation codebook with positive, negative, redundant-path, and ambiguous examples.
4. Build a 5-question annotation dry run; revise definitions before scaling to 30–50.
5. Implement one deterministic fixed-candidate deletion test and its invariants.
6. Run the pilot only after annotation and intervention checks pass.

**Current decision:** Proceed to Phase 0 and the annotation dry run. Do not begin confirmatory experiments or make novelty claims yet.
