# V3 Research Roadmap
## Path-Dependent State Distortion in Recursive Conversational Memory
**中文题目：** 递归对话记忆中的路径依赖性状态失真：转换历史与下游影响的控制实验  
**Status:** Research proposal / protocol-development stage. No V3 confirmatory experiment has been run.

## 1. Executive summary
V3 reframes the project from a broad claim that recursive compression causes status drift to a controlled question: when the same dialogue evidence is transformed through different memory-writing histories, do the resulting memories differ in how faithfully they represent the proposition's evidence-supported state, even after proposition identity and storage budget are controlled? If so, do those state differences causally alter downstream agent decisions?

The intended contribution is not another generic memory architecture, uncertainty-preservation prompt, belief-state store, stale-memory benchmark, or claim that memory errors affect behavior. Those areas have close prior work. The candidate contribution is a rigorous, paired and budget-controlled analysis of transformation-history effects, separating proposition loss from status distortion and testing downstream consequences through controlled status-only interventions.

## 2. Research questions
- RQ1 — Path effect (between-condition): Do Direct, Recursive, and Rewrite-matched transformation histories differ in status fidelity when proposition identity is preserved?
- RQ1b — Path effect (within-condition): Do multiple transformation paths under the same condition (different intermediate schedules, same source and final budget) produce different final states? This is the operational core of the word "path-dependent".
- RQ2 — Mechanism: Are observed differences attributable to transformation history rather than final length, number of model calls, source access, topic omission, or writer/judge artifacts?
- RQ3 — Consequence: Holding proposition content fixed, does changing only its represented status alter downstream agent decisions, clarification, abstention, or authorization behavior?
- RQ4 — Mitigation: Can evidence anchoring or explicit state-transition verification reduce unsupported distortion without defaulting to UNKNOWN or increasing storage without bound?

## 3. Operational scope
Primary status dimensions:
1. Epistemic: unknown / possible / probable / supported / established / explicitly rejected. The final ontology must be calibrated and mutually interpretable.
2. Intentional: considering / expressing interest / intending / committed / executing / completed / cancelled / explicitly not intended.
3. Conditional: condition unknown / active-unsatisfied / satisfied / failed / waived, with the associated action state represented separately.

The unit of analysis is a target proposition plus its evidence-bearing dialogue trajectory and the state transition justified by that evidence. A status change supported by later dialogue is a legitimate update, not drift.

## 4. Experimental conditions
- Raw: full dialogue supplied at evaluation; reference ceiling, not a compressed-memory condition.
- Direct: final memory generated once from the original dialogue.
- Recursive: initial memory generated, then repeatedly rewritten from the previous memory.
- Rewrite-matched: repeated rewriting with controlled intermediate storage budgets, designed to separate chained re-editing from shrinking-budget schedules.
- Path-replicate: multiple predeclared intermediate schedules under the same condition, with the same source and final budget. This is the primary unit for path divergence.
- Source-peek: chained rewriting with access to both the prior memory and the original dialogue, separating transformation history from source availability.
- Repeated-direct: d independent direct compressions of the full dialogue, keeping the last; matches writer-call count without chaining.
- Retrieval: evidence retrieval from the original dialogue or immutable evidence store, reported as a distinct access strategy rather than conflated with summarization.
- Optional Structured State: explicit proposition/status/evidence representation as a reference baseline, not assumed to be novel.

All conditions must use the same source trajectories, writer model family, decoding settings where possible, and predeclared budget targets. Every generated output must be retained and analyzed; do not select cases after observing output length.

## 5. Primary outcomes
- Proposition identity: PRESERVED / PARTIAL / LOST / AMBIGUOUS.
- Status fidelity conditional on proposition PRESERVED: correct / unsupported change / ambiguous / not recoverable.
- Unsupported Status Drift Rate (USDR): unsupported status changes among proposition-preserved outputs.
- Proposition Loss Rate (PLR): proposition identity lost or materially incomplete, reported separately.
- Legitimate Update Accuracy (LUA): correct representation of evidence-supported state transitions.
- Status contradiction rate and evidence traceability.
- Downstream Decision Error (DDE), clarification rate, appropriate abstention, and unauthorized-action rate in simulated tasks.

Report both P(unsupported drift | proposition preserved) and P(proposition loss). Never merge them into one score without also publishing both components.

## 6. Design principles and confound controls
- Paired design: every trajectory appears in every applicable condition.
- Budget control: predeclare multiple target budget bands; report actual token counts and analyze all outputs. Do not post-select outputs into a token band as the primary analysis.
- Source-access control: record whether each condition can access the original dialogue, intermediate memories, and evidence snippets.
- Call-count control: distinguish the effect of chaining from the effect of repeated generation. Rewrite-matched is necessary but not sufficient; include repeated-direct and source-access ablations.
- Path-level unit: for path-dependence claims, the unit is a path within a condition. Report pairwise state divergence and dispersion, not only condition means.
- Source-access crossing: history (chain / no chain) × source access (memory-only / memory+source) where feasible.
- Joint-outcome primary: report the joint distribution of proposition identity × status fidelity; do not make a conditional-on-preserved quantity the sole primary outcome.
- Model control: begin with one locally reproducible writer model, then replicate on a second model only after the primary protocol is stable.
- Human primary labels: model judges are diagnostic only. Preserve raw outputs and blind annotators to condition and gold labels.
- Legitimate updates: include stable, updated, reversed, cancelled, and conditional trajectories.
- No real side effects: all behavioral tasks are sandboxed simulations.

## 7. Staged execution and gates
### P0 — Protocol freeze
Finalize ontology, unit of analysis, condition definitions, exclusions, annotation guide, analysis plan, and artifact schema before confirmatory generation.
Gate: two annotators can apply the guide to a calibration set with acceptable agreement after adjudication.

### P1 — Calibration pilot
Use a small balanced set across all status dimensions and update types. Inspect ambiguity, proposition identity, and annotation failure modes. This phase is for protocol repair, not hypothesis testing.
Gate: freeze definitions and report all changes before the main run.

### P1a — Path-replicate existence check
Before the full paired study, run a cheap within-condition path pilot: 12 trajectories × 3 predeclared intermediate schedules + direct reference. Measure whether final states diverge across paths with the same source and final budget. This is the minimal evidence that "path-dependent" is the right claim.
Gate: report whether path divergence exists, is null, or is dominated by proposition loss; revise the claim accordingly.

### P2 — Paired transformation study
Generate all conditions for each trajectory under predeclared budgets. Store full source, prompts, intermediate memories, final outputs, token counts, model/config fingerprints, and errors.
Gate: pipeline completeness, no silent missing conditions, and acceptable proposition-retention rates.

### P3 — Human evaluation
At least two independent blind annotators label proposition identity, status, evidence support, and ambiguity. Adjudicate disagreements. Report raw agreement and an appropriate chance-corrected statistic, with confidence intervals.
Gate: drift remains observable after adjudication and is not explained by proposition loss or annotation ambiguity.

### P4 — Downstream behavioral intervention
Construct paired memories with identical proposition wording and different status representation. Use the same agent, prompt, tools, and scenario; randomize condition order. Evaluate mock decisions, requests for confirmation, abstention, and authorization boundaries.
Gate: status-only intervention produces a measurable and interpretable behavioral difference, or a well-powered null result.

### P5 — Mitigation
Compare neutral summary, status-aware summary, evidence-anchored summary, and explicit transition verification under matched budgets. Include an UNKNOWN-heavy baseline to detect trivial abstention strategies.
Gate: improvement in status fidelity without unacceptable proposition loss, excessive abstention, or budget inflation.

### P6 — Replication and paper
Replicate the key contrast on a second writer model or a distinct trajectory source if resources permit. Publish all exclusions, null results, prompts, annotation instructions, and analysis scripts.

## 8. Statistical plan overview
Use paired trajectory-level contrasts. The primary comparison is Recursive versus Direct among proposition-preserved outputs, with Rewrite-matched as a mechanism control. Because conditioning on proposition preservation can introduce selection bias, report (a) unconditional joint outcomes, (b) conditional status fidelity, and (c) a sensitivity analysis that treats LOST/PARTIAL/AMBIGUOUS under predeclared alternative rules. Use cluster-aware uncertainty estimates at the trajectory level. Sample size is determined after pilot variance and target effect assumptions are specified; no fixed sample count is asserted as statistically powered in advance.

## 9. Positioning against prior work
V3 must not claim novelty for:
- structured belief-state or plan-lifecycle memory;
- preserving uncertainty markers in a single summary or rewrite;
- stale memories influencing personalized responses;
- generic long-term memory benchmarks;
- memory provenance or versioning by itself.

The defensible candidate gap is narrower: causal and paired isolation of transformation-history effects on state fidelity, conditional on proposition identity, with explicit controls for budget/call count/source access and a downstream status-only intervention. This remains a hypothesis about the literature gap until a full-text novelty audit is completed.

## 10. Relationship to earlier project work
All v2.x experiments are retained as exploratory/pilot evidence. They motivate the distinction between proposition loss and status-cue loss and identify intentional-state cues as a potentially vulnerable case. However, prior runs include small samples, model-judge dependence, prompt-specific effects, imperfect budget matching, and annotation-integrity corrections. They do not establish V3's causal claims and must not be pooled with V3 confirmatory data.

## 11. Go / No-Go decisions
0. Is there within-condition path divergence at all? If not, "path-dependent" is not supported; revise the claim to a condition/history effect.
1. After controlling for proposition identity and budget, is there a reproducible transformation-history effect?
2. Does the effect survive blind human annotation and independent replication?
3. Does changing status alone alter downstream behavior under a controlled intervention?
If the first fails, pivot to a descriptive analysis of status representation rather than claiming path dependence. If the second fails, revise measurement. If the third fails with adequate power, report that status distortion does not necessarily translate into behavior change in the tested task family.

## 12. Immediate next actions
1. Complete full-text novelty audit of recursive summarization, memory rewriting, status/commitment tracking, and causal memory interventions.
2. Freeze formal ontology and annotation manual.
3. Implement a paired-condition artifact schema and audit checks before running the local model.
4. Run calibration only; do not scale until human labels are reliable.
