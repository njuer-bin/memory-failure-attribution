# V3 Paper Plan — Status Fidelity Under Chained Memory Rewriting

Status: planning document, 2026-11-18. This is the writing plan, not the paper
draft. It fixes the claims, section structure, figures, and order of work.

## 1. Working title

**Status Fidelity Under Chained Memory Rewriting: Omission, Distortion, and
Downstream Behavior**

Alternatives:

- "When Memory Keeps the Fact but Loses the Stance"
- "The Status Gets Lost: Proposition-Preserving Rewriting Omits Epistemic,
  Intentional, and Conditional State"

Avoid "path-dependent" in the title. The schedule-only path pilot (P1a) was
near-null; the robust contrast is chained rewriting versus direct, not
intermediate-budget schedules.

## 2. Abstract draft

Long-term conversational agents compress dialogue into memory. The same
proposition can survive compression while the stance attached to it disappears.
We introduce a proposition-controlled diagnostic for **status fidelity**: the
epistemic, intentional, or conditional state attached to a proposition, measured
across paired transformation histories with proposition identity held fixed.

In a 30-trajectory paired study with 330 blind human-labeled memories, chained
rewriting omitted the status of 44-54% of proposition-preserved memories, while
unsupported distortion was rare (3/330). Rewrite-matched and repeated-direct
controls isolate chained re-editing from intermediate budget and raw call count;
giving the writer access to the source removes the omission. Downstream,
distortion robustly raises unauthorized action (P4: 66.7% vs 6.7%; P4.2:
23.7% and 21.1% vs 0%). Omission's profile is task-dependent: conservative
under-action in a synthetic decision task, but over-action in high-stakes
authorization when the agent fills the missing status from a bare mention or the
current request. Source access is the strongest mitigation; a status-aware
prompt is partial and non-additive. A real-dialogue feasibility audit shows
intentional status is findable and gold-codeable, but the LSF/SSF annotation
instrument fails calibration; we report that as a measurement lesson.

The ingredients are prior work. The contribution is the status-specific,
proposition-controlled diagnostic and the separation of omission from
distortion.

## 3. Contributions

1. **Measurement.** A status tuple and a paired transformation-history design
   that fixes proposition identity, separates status omission from unsupported
   distortion, and uses blind human labels plus deterministic controls.
2. **Mechanism.** Chained re-editing of the writer's own output, not budget
   shrinkage or call count, drives status loss; source access removes it.
3. **Consequence.** Distortion is the robust downstream harm. Omission is not a
   safe failure in general; its behavioral profile depends on the task and on
   whether the agent fills the missing status.
4. **Mitigation.** Source access is the strongest mitigation in the primary
   model; a status-aware prompt is partial; the combination is non-additive and
   model-dependent.
5. **Real-data measurement lesson.** Intentional status is feasible to find and
   gold-code on real dialogue; LSF/SSF annotation fails calibration and is
   reported as a negative result and future work.

## 4. Claims-evidence matrix

| ID | Claim | Evidence | Status | Where |
|---|---|---|---|---|
| C1 | Chained rewriting omits status while the proposition survives. | P3: 330 items, primary κ 0.944; omission 44-54% vs 3.7% direct. | Supported | §5 |
| C2 | Chained re-editing, not budget or call count, drives the loss. | P3: rewrite-matched = recursive (0.000 [−0.167, 0.167]); repeated-direct = direct; source-peek −0.400. | Supported | §5 |
| C3 | Unsupported distortion is rare under rewriting. | P3: 3/330 (0.9%); underpowered for condition contrasts. | Supported with caveat | §5 |
| C4 | Distortion raises unauthorized action. | P4: 66.7% vs 6.7%; P4.2: 23.7%/21.1% vs 0%. | Supported | §6 |
| C5 | Omission's behavioral profile is task-dependent. | P4: 0/30 unauthorized, under-action; P4.2: 6/38 and 5/38 unauthorized overall, 2/34 and 3/34 over-commitment only. | Supported as task-dependence | §6 |
| C6 | Source access is the strongest mitigation in the primary model. | P5: 30/30 faithful vs 14/26 neutral; +0.533 [0.367, 0.700]. | Supported (qwen); model-dependent | §7 |
| C7 | Status-aware prompting is partial and non-additive. | P5: 27/30; interaction −0.500 [−0.667, −0.333]. | Supported | §7 |
| C8 | Intentional status is findable and gold-codeable on real dialogue. | Feasibility audit; 40-item gold calibration with adjudication: dimension 1.000/1.000, status 0.975/0.969. | Supported with caveats | §8/appendix |
| C9 | LSF/SSF annotation is reliable on real dialogue. | Runs 1-2 failed (run 2: LSF 0.800/0.689; SSF 0.756/0.625; identity 0.800/0.607). | **Not supported** — report negative | §8/appendix |

## 5. Section plan

Page budget assumes ACL/EMNLP long (8 pages content + references/appendix).

### 1. Introduction (1.25 pages)

- Opening example: a memory keeps "the user is buying a desk" but drops "still
  considering", and a downstream agent orders it.
- The gap: memory evaluation usually measures fact recall, not the stance
  attached to a fact.
- The diagnostic and the two failure modes: omission vs distortion.
- Contributions (five bullets).
- One-paragraph result preview with the P3 and P4.2 headline numbers.

### 2. Related work (1.5 pages)

Organize by what is prior, not by paper summary:

- State tracking vs recall: StateMem/StateMemBench.
- Structured state and belief revision: ProgMem, BELIEFMEM.
- Recursive summarization and chained rewriting: ABBEL, ReSum, Supersede,
  LightMem.
- Source access and raw-history preservation: LiveCtx.
- Stale state and memory-to-action: STALE, StateAuditor, MemTX, EAL-Bench.
- Belief-change interventions: TWIST.
- Position: each ingredient is prior work; the contribution is the
  status-specific, proposition-controlled combination. Use the say/do-not-say
  list from `2026-11-17-novelty-audit.md`.

### 3. Definitions and measurement (1.25 pages)

- Unit: proposition `P`, evidence `E`, transformation history `H`, memory `M`,
  evaluation time `t`.
- Status tuple: epistemic, intentional, conditional (condition + action),
  polarity/scope/time.
- Outcomes: proposition identity (PRESERVED/PARTIAL/LOST/AMBIGUOUS) × status
  fidelity; omission, unsupported distortion, legitimate update.
- LSF/SSF definitions; why they are separate.
- Human labeling: blind annotators, adjudication, reliability; model judges are
  diagnostic only.
- Controls: direct, recursive, rewrite-matched, repeated-direct, source-peek,
  raw; budget and call-count controls.

### 4. Study 1 — synthetic paired transformation study (2 pages)

- Design: 30 trajectories, 10 conditions, 330 blind items, κ 0.944.
- Primary result: omission among proposition-preserved by condition; direct and
  source-peek near zero.
- Mechanism: rewrite-matched = recursive; repeated-direct = direct; source-peek
  removes omission. Report paired differences and CIs.
- Unsupported distortion: 3/330; condition contrasts uninformative.
- Dimension breakdown: conditional 27.6%, epistemic 33.0%, intentional 27.3%
  omission among preserved; the v2 "intentional-specific" pattern does not
  replicate.
- Legitimate updates and proposition loss reported separately.
- Do not merge omission and distortion into one drift score.

### 5. Study 2 — downstream behavior (2 pages)

- P4 design: 30 trajectories × present/omitted/distorted + no-memory; sandboxed
  PROCEED/CONFIRM/ABSTAIN; qwen and gemma.
- P4 result: present 2/30, omitted 0/30 (under-action), distorted 20/30;
  paired contrasts.
- P4.2 design: 38 validated English high-stakes scenarios, 304 calls,
  authorized-execution controls; two-human validation.
- P4.2 result: present 0/38; omitted 6/38 and 5/38; distorted 9/38 and 8/38;
  over-commitment-only 2/34 and 3/34 vs 9/34 and 8/34; distorted-minus-omitted
  +0.206/+0.147.
- Mechanism: 17 distorted cases follow a false memory; 15 omission cases
  fabricate a status (`O1` 6, `O2` 3, `O3` 6). The control probe shows the
  effect is not only lexical.
- Framing: P4 and P4.2 are different task families; do not pool. The robust
  claim is distortion harm; omission is task-dependent.

### 6. Mitigation (1 page)

- P5 confirmatory 2×2: prompt × source access; 30 trajectories.
- Faithful: neutral 14/26, status-aware 27/30, source 30/30, combined 28/30.
- Paired: status-aware +0.433, source +0.533, interaction −0.500.
- Gemma writer replication: ranking flips toward the prompt; report the model
  boundary, not a universal mitigation.
- Practical implication: expose the source at rewrite time; a status-aware
  prompt is a fallback, not a fix.

### 7. Real-dialogue arm (0.5 page main text, appendix)

- Feasibility audit: 2,135 candidates; intentional viable, epistemic thin,
  conditional scarce.
- 40-item gold calibration: passes after third-person adjudication
  (dimension 1.000/1.000, status 0.975/0.969).
- LSF/SSF calibration: failed twice; report the negative result and the
  measurement lesson (target-turn focus, cue lexicon, predicate identity).
- Do not claim natural-dialogue replication, LSF/SSF reliability, or
  conditional reliability. Put details in the appendix.

### 8. Discussion (1 page)

- Two failure modes with different mechanisms and behavioral profiles.
- Why "omission is conservative" is not a general law: it depends on whether
  the task and request let the agent fill the missing status.
- Measurement implication: evaluate stance, not only fact recall; report
  proposition identity and status jointly.
- Design implication: source access beats prompting; prompting is partial.
- Real-data lesson: annotation instruments for stance are hard; a negative
  calibration is informative.

### 9. Limitations (0.5 page)

- Synthetic templates and local 7B/12B models; no API-model replication.
- Distortion underpowered (3/330); P4.2 has 17 unauthorized distortion events.
- Human label provenance unrecorded; adjudication partly model-assisted.
- Real-data LSF/SSF calibration failed; conditional arm thin.
- No formal power claim; 38 scenarios is a mechanism experiment.
- P4 and P4.2 task families differ; do not pool.

### 10. Conclusion (0.25 page)

Restate: status fidelity is a distinct measurement target; chained rewriting
omits status; distortion is the robust behavioral harm; omission is
task-dependent; source access is the strongest mitigation; real-dialogue
annotation remains an open measurement problem.

## 6. Figures and tables

### Figures

1. **Fig. 1 — Design.** Proposition/evidence/history/memory; conditions and
   controls; the status tuple. (Schematic.)
2. **Fig. 2 — P3 omission by condition.** Bars with paired CIs; raw/direct/
   recursive/rewrite-matched/repeated-direct/source-peek.
3. **Fig. 3 — P3 mechanism.** Paired differences: rewrite-matched vs recursive,
   repeated-direct vs direct, source-peek vs recursive.
4. **Fig. 4 — P4 and P4.2 behavior.** Two panels: unauthorized action by
   variant; over-commitment-only P4.2 inset.
5. **Fig. 5 — P5 mitigation.** Faithful rate by condition; interaction.
6. **Fig. 6 (appendix) — Real-data calibration.** Gold calibration and LSF/SSF
   gates; failed LSF/SSF runs.

### Tables

1. **Table 1 — Status tuple and outcomes.** Definitions and allowed labels.
2. **Table 2 — P3 joint distribution.** Proposition identity × status fidelity;
   omission among preserved by condition.
3. **Table 3 — P4/P4.2 paired contrasts.** Unauthorized and evidence-consistent;
   CIs; do not pool.
4. **Table 4 — P5 mitigation.** Faithful, omission, distortion, budget.
5. **Appendix A — Prompts and conditions.**
6. **Appendix B — Annotation guides and reliability.**
7. **Appendix C — Real-data feasibility and calibration.**

## 7. Positioning: say / do not say

**Say:**

- A status-specific, proposition-controlled diagnostic; the ingredients are
  prior work.
- Chained re-editing causes status omission; distortion is a rare subtype.
- Distortion is the robust behavioral harm; omission is task-dependent.
- Source access is the strongest mitigation in the primary model; prompting is
  partial and non-additive.
- Real-dialogue LSF/SSF annotation failed calibration; report it as a
  measurement lesson.

**Do not say:**

- First state tracking, first structured belief state, first recursive
  summarization omission, first source access, first memory-to-action effect.
- "Path-dependent" as a schedule-level claim; P1a was near-null.
- "Omission is conservative" as a general law.
- Real-dialogue LSF/SSF reliability or natural-dialogue replication.
- Conditional reliability.

## 8. Venue and submission strategy

- **Primary:** ACL or EMNLP main conference (long). The paper is an empirical
  diagnostic, not an architecture paper.
- **Fallback:** COLM; NeurIPS Datasets & Benchmarks if framed as a diagnostic
  benchmark + measurement study.
- **Anonymity:** cite the internal protocols only in the appendix; do not link
  the repository in the anonymized version.
- **Artifacts:** release code, prompts, scenario bank, and aggregate labels;
  raw dialogue outputs may need a data statement. Be explicit that provenance
  is annotator-unspecified.

## 9. Writing order

1. **Numbers table.** One source of truth for every number in the paper.
   Cross-check against `research-state.yaml`, `findings.md`, and the run notes.
2. **Methods/definitions** (§3) — stable, no results.
3. **Study 1 results** (§4) — P3 tables/figures.
4. **Study 2 results** (§5) — P4/P4.2; write the task-dependence paragraph
   carefully.
5. **Mitigation** (§6).
6. **Introduction and discussion** — after the results are fixed.
7. **Related work** — use the novelty audit; keep the say/do-not-say list.
8. **Appendix and real-data negative result**.
9. **Internal audits:** number audit, claim audit, citation audit, anonymity
   check.

## 10. Open issues before submission

- P4.2 control wording: v1 omitted controls are request-like; the v2 probe
  shows the effect persists but is model-dependent (qwen 1/4, gemma 3/4). Report
  both and do not pool.
- P4 vs P4.2: task families differ; the paper must not present a single
  "omission is safe/dangerous" claim.
- Distortion event count: 3/330 in P3 and 17 unauthorized distorted cases in
  P4.2; keep the "rare but harmful" framing and report precision.
- Human labels: P3 used two annotators but provenance is unrecorded; adjudication
  is partly model-assisted. Report as annotator-unspecified.
- Real-data LSF/SSF: negative result; do not bury it, but keep it in the
  appendix.
- Novelty risk: ABBEL/Supersede appendices may contain a proposition/status
  split; the full-text audit argues against it, but check before submission.
- Model scope: qwen2.5:7b and gemma3:12b only; no API models. Frame as a
  mechanism study, not a model-ranking claim.

## 11. Artifact map

- `docs/research/V3_P2_PROTOCOL.md`, `V3_P5_CONFIRMATORY_PROTOCOL.md`,
  `V3_P4_2_PROTOCOL_DRAFT.md`, `V3_P4_2_FREEZE.md`,
  `V3_P4_2_RUNNER_FREEZE.md`, `V3_STATISTICAL_ANALYSIS_PLAN.md`,
  `V3_FORMAL_DEFINITIONS.md`, `V3_ANNOTATION_GUIDELINES.md`.
- Results: `results/status_drift_v3_p2/`, `status_drift_v3_p4/`,
  `status_drift_v3_p4_2/`, `status_drift_v3_p5/`,
  `status_drift_v3_real_audit/`.
- Run notes: `2026-11-16-status-drift-paper-backbone.md`,
  `2026-11-18-v3-p4-2-results.md`, `2026-11-18-stage2-calibration-40-result.md`,
  `2026-11-18-stage2-lsf-ssf-run2-result.md`,
  `2026-11-18-real-data-arm-scoping.md`.
