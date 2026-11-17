# Findings — Status Drift v2 Pilot

This file is the evolving narrative synthesis for the autonomous research loop.
Authoritative pre-autoresearch history lives in `docs/RESEARCH_LOG.md`; the v2
plan and protocol live in `docs/STATUS_DRIFT_RESEARCH_PLAN_V2.md`,
`docs/STATUS_DRIFT_PILOT_PROTOCOL.md`, and `docs/STATUS_DRIFT_PROTOCOL_V2_1.md`
/ `_V2_2.md`.

## Current Understanding (2026-11-16, after the 30-trajectory run)

The pilot now has a coherent result. **The writer prompt is the dominant factor
in status preservation.**

- **status-aware writer:** 256/270 condition-items are correct under both
  judges; exactly **1** both-judge error (`epistemic_02_U`, recursive D5).
- **neutral writer:** 221/270 both-correct and **23** both-wrong, concentrated
  at recursive D2–D5.
- Pairwise: status-aware is both-correct where neutral is not on 43 items;
  the reverse holds on 8.
- Deterministic proposition omission: 0/270 (status-aware), 3/270 (neutral).
- Deterministic condition omission: 2/90 (status-aware), 10/90 (neutral).
- Inter-judge agreement: 0.952 (status-aware), 0.904 (neutral); all dimensions
  ≥0.80.

## Patterns and Insights

- **Neutral compression erodes status while keeping the proposition.** The
  characteristic failure is `确认`/`决定` disappearing from
  `购电脑…`, `上海工作…`, `学习日语…`, or weakening to `决定中`.
- **Recursion matters only when the writer is not status-preserving.** Under
  the neutral writer, errors cluster at recursive D2–D5; under the status-aware
  writer only one D5 item fails in the 30-run.
- **The chaining effect is dimension-specific (10 topics, 60 trajectories).**
  Neutral: intentional recursive D5 ABSENT 9/10 vs epistemic 2/10. Status-aware:
  intentional 5/10 vs epistemic 2/10; direct 0/10 in both. Aggregate numbers hid
  this. Intentional commitment cues (`决定`) are the vulnerable status;
  epistemic certainty cues are largely robust.
- **Status-aware mitigation is partial and dimension-specific.** It removes
  direct-condition cue loss (0/10) and halves intentional recursive D5 strict
  cue absence (9 → 5/10). Manual reading: all 5 status-aware "absent" items
  still carry a weak commitment cue (`推进计划`, `按计划`, `已开始`), while the
  neutral writer removes the cue entirely in 8/10. The status-aware failure
  mode is **cue weakening**, not removal.
- **The intentional cue loss is prompt-controllable.** A commitment-aware
  writer that requires an explicit commitment word achieves **10/10 strong
  cues at every depth** (recursive D5 included), versus neutral 1 strong/8 none
  and status-aware 5 strong/5 weak. Judge confirmation: qwen and gemma agree
  **180/180**, and all **40/40** updated D3/D5 items are judged COMMITTED. This
  is a ceiling intervention, not a practical default: the prompt names the
  target cue and the outputs are templated. The practical implication is a
  structured sidecar or a post-hoc status checker.
- **Repeated chained rewriting is the destructive factor, not budget
  shrinkage.** v2.3 holds intermediate budgets constant at 220 and recovers
  the same degradation as the shrinking schedule; both are much worse than a
  single compression to the same final budget. Proposition omission stays
  0–2/30, so the loss is status-specific.
- **Status-aware mitigates but does not eliminate chained cue loss.** v2.3
  neutral: chaining penalty 32 both-correct cells and 23 both-wrong items.
  Status-aware: 8 and 3. Yet the explicit cue is absent in roughly 4–5/10 deep
  updated cases even under status-aware; the judge often recovers the status
  from remaining context. Judge-level accuracy therefore understates the
  cue-level loss.
- **Cross-run nondeterminism is prompt-dependent.** The neutral writer varies
  across runs (seed 42 vs 43/44 ≈ 0.63; seed 43 vs 44 ≈ 0.96), while the
  status-aware writer is byte-identical across seeds 42 and 43
  (270/270 = 1.000). The seed option is not a variance control. At temperature
  0, freer prompts can hit near-ties that flip; constrained prompts do not.
- **A third judge confirms both writer results.** Three judges
  (qwen/gemma/mistral) on the 30-run: status-aware has exactly **1**
  all-three-wrong item (the real `epistemic_02_U` D5 cue loss); neutral has
  **23** all-three-wrong items, exactly its earlier both-wrong set. Majority
  accuracy 260/270 (status-aware) vs 232/270 (neutral). The mitigation
  23 → 1 is not a judge artifact. Majority voting still leaves 15
  judge-specific near-tie errors in neutral.
- **Neutral v2.4 replication (30 trajectories).** Recursive-minus-direct judge
  error is +0.067/+0.167/+0.267/+0.200 at D1/D2/D3/D5 (recursive worse), while
  the status-aware run was negative. Deterministic cue ABSENT at recursive D5
  is 8/10 neutral vs 2/10 status-aware; rewrite-matched D5 is 8/10 vs 2/10.
  Token logging shows chained outputs are shorter (D5 mean 16.1 vs direct 21.4
  tokens), so the contrast is not token-matched and a matched-budget follow-up
  is required.
- **Status-aware drift, single manual annotator (A): 4.2%.** 120 items, v2.4
  full run: 0/30 at Raw, 0/30 at Direct D5, 2/29 at Recursive D5 (6.9%),
  3/30 at Rewrite-matched D5 (10.0%); overall 5/119 = 4.2%. All five cases are
  epistemic escalation or intentional commitment weakening. The status-aware B
  file is gold-derived and is **not used**; A-only is the accepted estimate for
  this condition (project decision).
- **Neutral drift, two independent manual annotators: 6.7–7.9%.** 120 items,
  v2.4 neutral run: A 9/114 = 7.9%, B 7/105 = 6.7%; primary-label agreement
  raw 0.942, Cohen's kappa 0.849. Raw and Direct D5 are 0; Recursive D5
  13.6–15.4%; Rewrite-matched D5 16.7–17.9%; intentional 21.9–25.7%;
  epistemic and conditional 0. Neutral roughly doubles the status-aware drift.
- **Matched token-band control (v2.9) supports the chaining effect,
  conditionally.** At [14,18] writer tokens, topic-mentioned updated cases:
  direct 1/7 ABSENT, recursive 5/6, rewrite-matched 6/8. Achieved token means
  are close (18.1 / 16.7 / 16.3) and ranges overlap, so the effect is not solely
  a length artifact. However, recursive D5 topic omission is 13.3%, above the
  pre-registered 10% gate; treat this as directional matched-band evidence, not
  a clean confirmatory result.
- **V3 P1a path-replicate pilot: schedule-only path divergence is rare.**
  12 trajectories × 3 intermediate schedules + direct, neutral writer, same
  source and final budget. Only **1/12** trajectories shows any within-condition
  path divergence (mean pairwise 5.6%); direct-vs-paths disagreement is 34.7%.
  This motivated P1b's broader path space.
- **V3 P1b heterogeneous path pilot: path dependence is real but
  mechanism-specific.** 12 trajectories × 5 paths (schedule, source-peek,
  prompt paraphrase, temperature 0.7) + direct. Mean pairwise divergence 43.9%;
  **10/12** trajectories diverge. Schedule-only S1–S2 is nearly null (9.1%);
  source access gives ~50–58%, prompt paraphrase 25–45%, temperature 27–82%.
  PEEK preserves gold best (epistemic 3/4, intentional 3/4, conditional 4/4);
  TEMP is worst (0/4, 0/4, 1/3); direct is best. Path dependence arises from
  information access and generation variability, not from the budget schedule.
  Keep the claim but scope it.
- **V3 P1c (n=42) replicates path dependence with a mechanism.** Mean pairwise
  path divergence 32.9%; 31/42 trajectories diverge. Schedule-only S1–S2 is
  5.3%; source access (PEEK) 58–61%; prompt paraphrase 20–27%; temperature
  8–14%; TEMP1–TEMP2 sampling variance alone is 8.3%. PEEK has the best chained
  gold match (epistemic 11/14, intentional 9/14, conditional 14/14); TEMP is
  worst (3/12, 0/14, 8/12; 4/13, 2/14, 7/11); direct remains best. Mechanism:
  information access + generation variability, not budget schedule. Conditional
  has 11 topic-lost paths, so its path results need an omission analysis.
- **V3 blind annotation calibration fails the agreement gate.** 60 items, two
  independent annotators. Primary judgment raw 0.733, kappa 0.578;
  applicability raw 0.40 (epistemic) and 0.60 (intentional); status-field
  agreement low. Dominant human label is **STATUS_OMISSION** (A 22/60, B
  19/60); unsupported distortion is rare (A 1, B 4). The deterministic cue
  metric conflates omission with distortion; the P1c path gradient is weak in
  human labels. Do not proceed to confirmatory annotation or the paired study;
  revise applicability rules, collapse the ontology, and re-calibrate.
- **V3.1 annotation guide revision.** Collapsed the ontology to 2–3 labels per
  dimension, added one `primary_dimension`, a two-step omission/distortion
  decision, and explicit `NO_DISTORTION` vs `LEGITIMATE_UPDATE` rules. A new
  60-item calibration set (`annotation_v31`) is ready; re-calibrate before any
  confirmatory work.
- **V3.1 re-calibration: applicability fixed, conditional still fails.** 60
  items, files A/B. Primary-judgment raw 0.850 / kappa 0.728 (V3: 0.578);
  primary-dimension kappa 0.853; epistemic kappa 0.788, intentional 0.904,
  conditional **0.126**. NO_DISTORTION dominates (A 33, B 39); STATUS_OMISSION
  18/18; unsupported distortion 4/1. Human labels do not reproduce the
  deterministic path gradient (PEEK and PARA 0 unsupported under both). The
  recurrent disagreement is conditional action-vs-condition. Provisional
  partial pass: epistemic/intentional usable, conditional not; do not freeze
  the guide. Annotator provenance and adjudication are pending.
- **The conditional failure is a guide defect, not sampling noise.** The v3.1
  adjudication found four rule ambiguities: the condition relation was counted
  inside proposition identity (conflicting with the formal ontology);
  `LEGITIMATE_UPDATE` was checked after `NO_DISTORTION`, making it unreachable;
  status expression had no explicit-cue rule, so `购电脑`/`购机` was read by one
  annotator as commitment and by the other as mere juxtaposition; and
  "materially PARTIAL" had no boundary. All nine primary disagreements become
  determinate under the v3.2 rules. The adjudication is model-assisted, not
  human.
- **v3.2 rules: explicit cues and a strict judgment order.** A status counts
  only with an explicit lexical cue (`已拿到`/`条件满足` vs bare `奖学金`);
  proposition identity is predicate + arguments, with condition/status scored
  separately; an ordered chain retaining both old and new states is
  `LEGITIMATE_UPDATE`; any `PARTIAL` is `PROPOSITION_LOSS`. A conditional
  memory with condition satisfied but no action cue is `NO_DISTORTION` on the
  conditional dimension, with the action state recorded as unexpressed.
- **The condition-only form under-measured conditional collapse.** A scan of
  the v3.2 set found explicit action escalations (`已获奖学金，开始学日语`;
  `获奖学金，计划参赛`) that the old form would have scored `NO_DISTORTION`
  because only the condition state was recorded. v3.2.1 adds a required
  `action_status` field; an explicit `COMMITTED` action with only
  `CONSIDERING` support is `UNSUPPORTED_STATUS_DISTORTION`
  (`CONDITIONAL_COLLAPSE`).
- **The v3.2.1 conditional calibration failed only on identity; the v3.2.2
  re-annotation passes.** First round: `action_status` 60/60 (κ 1.000),
  condition state 59/60 (κ 0.974), but `primary_judgment` κ 0.550,
  `proposition_identity` κ 0.378, `evidence_support` κ 0.437. All 16 identity
  disagreements were A `PRESERVED` vs B `PARTIAL`/`AMBIGUOUS`: A applied
  topic-level preservation, B head-predicate + object. After the v3.2.2
  identity worksheet and evidence rule: identity κ 0.837, primary κ 0.827,
  evidence κ 0.961, action κ 1.000. Gate passes.
- **Strict identity implies substantial proposition loss.** Under the
  predicate+object rule, 31/60 (52%) are `PARTIAL`/`AMBIGUOUS`; the joint
  outcome must report proposition loss separately, and status analyses are
  conditioned on the 28 `PRESERVED` items. A lenient topic-level rule would
  inflate the status-distortion denominator.
- **The one real distortion is stable across both rounds.** `V32C-0020`
  (`已获奖学金，开始学日语`) is labeled identically by both annotators as
  `CONDITION_SATISFIED` + `COMMITTED`, `UNSUPPORTED_STATUS_DISTORTION`,
  `CONDITIONAL_COLLAPSE`. The condition/action instrument works.
- **Seven residual boundary items remain.** Five serial-verb
  `去上海工作` cases (`上海工作待定`), one `AMBIGUOUS` identity judgment, one
  `已达标` cue. v3.2.3 clarifies them; adjudication round 2 resolves five toward
  A and two toward B. Recommendation: freeze v3.2.3 and start P2; a 7-item
  recheck is optional for a clean observed agreement.
- **P2 is frozen and generation has started.** 30 new trajectories across 5
  unseen topics, 10 generated conditions plus raw, `qwen2.5:7b` neutral writer,
  final budget 100, seeds 42/43. The smoke test completed 10/10 conditions with
  no errors. The completeness gate is 30/30 trajectories and 300/300 generated
  conditions; P3 blind annotation under v3.2.3 is the primary measurement.
- **P2 completeness gate passed.** 30/30 trajectories, 300/300 generated
  conditions + 30 raw references, 0 errors, 0 empty finals. Chained conditions
  are shorter on average (recursive 22.7 chars/16.4 tokens; rewrite-matched
  23.0/16.5; temp1 20.7/15.4; path_s2 21.5/15.8) than direct (28.2/20.0) and
  source-peek (28.2/20.1); retrieval is longest (46.8 chars). Topic-mention
  diagnostics are 0.83–1.00 and are not proposition-retention evidence.
- **The P3 blind set is ready.** 330 items (30 trajectories × 11 conditions),
  balanced across dimensions, gold statuses, and conditions; a 150-item primary
  subset covers raw/direct/recursive/rewrite_matched/source_peek. Two
  independent annotations under the frozen v3.2.3 guide are the next gate.
- **P3 human labels are reliable.** 330 items: primary-judgment raw 0.967 /
  κ 0.944; identity 0.991 / 0.943; action_status 0.961 / 0.924;
  expressed_status 0.991 / 0.989; evidence 0.988 / 0.972; dimension 1.000.
  One B data-entry inconsistency was resolved in adjudication.
- **The confirmatory result is status omission, not unsupported distortion.**
  Among 300 proposition-preserved items, 88 are `STATUS_OMISSION` (29%);
  unsupported distortion is 3/330 (0.9%). Omission by condition: recursive
  44.4%, rewrite_matched 46.2%, para 54.2%, temp1 42.3%, temp2 51.9%,
  path_s2 53.8%; direct 3.7%, repeated_direct 3.7%, source_peek 0%, raw 0%,
  retrieval 33.3%.
- **Mechanism: chaining, not budget or call count.** Rewrite-matched equals
  recursive (paired omission difference 0.000, CI [−0.167, 0.167]); repeated-
  direct matches call count but behaves like direct (−0.367, CI
  [−0.567, −0.167]); source-peek eliminates omission (−0.400, CI
  [−0.567, −0.233]). Intermediate budget shrinkage and raw call count are not
  the cause.
- **The v2 intentional-specific pattern does not replicate.** In V3 blind human
  labels, omission among preserved is 27.6% conditional, 33.0% epistemic, and
  27.3% intentional. The earlier "intentional commitment cues are uniquely
  vulnerable" claim is scoped to the v2 deterministic/judge evidence, not the
  V3 confirmatory result.
- **The paper backbone is reframed.** The working claim is path-dependent
  status representation loss (omission), with unsupported distortion as a rare
  subtype. A P4 draft (paired present/omitted/distorted status, sandboxed
  downstream decisions) is ready for sign-off.
- **P4 separates the two failure modes behaviorally.** Omission is conservative:
  0/30 unauthorized actions, but evidence-consistent action falls 26.7 points
  because the agent asks instead of acting. Distortion is dangerous: 20/30
  (66.7%) unauthorized actions vs 2/30 (6.7%) under present status; paired
  +60 points, CI [0.433, 0.767]. The dominant memory failure is the safe one;
  the rare failure is the harmful one.
- **The agent itself shows conditional collapse.** Under present status, 2/10
  conditional memories (condition satisfied, action only considering) were read
  as decided and produced PROCEED. This is an agent-side error, not a
  memory-generation error, and must be reported separately.
- **Do not merge omission and distortion into one drift score.** They have
  opposite behavioral profiles. The paper's joint outcome must lead with both.
- **P5 pilot: status_aware is the best low-cost mitigation.** 12 trajectories
  × 6 strategies under one chain; deterministic MATCH: neutral 7/12,
  status_aware 10/12 at 1.03× length, source_peek 10/12 at 1.23×,
  evidence_anchored 10 MATCH + 2 AMBIGUOUS at 1.84× (fails the 1.5× budget
  flag), transition_verification 9/12, unknown_heavy 4/12 with 100%
  abstention.
- **The verifier does not reliably repair status.** `transition_verification`
  fixes 4/4 epistemic items but only 2/4 conditional items; it often treats
  the compressed memory as the source of truth. `evidence_anchored` preserves
  status best but its evidence tags are frequently wrong and it inflates the
  budget.
- **P5 human labels confirm the ranking, with one correction.** 72 items,
  primary κ 0.881. Faithful: neutral 6/12, status_aware 10/12, source_peek
  11/12, evidence_anchored 11/12, transition_verification 10/12,
  unknown_heavy 6/7 preserved but 5/12 proposition loss. Paired vs neutral
  faithful: status_aware +0.333 [0.083,0.583], source_peek +0.417
  [0.000,0.750], evidence_anchored +0.417 [0.167,0.667], transition +0.333
  [0.083,0.583].
- **`status_aware` remains the practical candidate but is not a complete fix.**
  It improves faithful status by 33 points at 1.03× length, but still produces
  one real conditional collapse (`已拿奖学金，将开始健身`).
  `evidence_anchored` loses its deterministic advantage under human labels and
  remains 1.84× with wrong anchors; `unknown_heavy` is disqualified by 42%
  proposition loss.
- **P5 confirmatory generation: source access is the stronger factor.**
  30 trajectories × 4 conditions, 120/120. Deterministic MATCH/30: neutral 14,
  status_aware 27 (1.05×), neutral_source 29 (1.23×), status_aware_source 27
  with 3 AMBIGUOUS (1.38×). All below the 1.5× budget flag. The combination
  does not add deterministic benefit over source access alone; human labels
  will decide the final ranking.
- **P5 confirmatory human labels: source access wins, the prompt is partial,
  the combination is non-additive.** Faithful: neutral 14/27 (0.52),
  status_aware 26/30 (0.87), neutral_source 30/30 (1.00),
  status_aware_source 28/30 (0.93). Paired vs neutral: status_aware +0.400
  [0.233, 0.567]; neutral_source +0.533 [0.367, 0.700]; interaction −0.467
  [−0.633, −0.300]. Exposing the source at rewrite time is the strongest
  mitigation; a status-aware prompt is a partial fallback and can introduce
  `将+action` escalations when source is available.
- **P5 reliability is below the gate.** Primary κ 0.689 vs the 0.80 threshold;
  disagreements are systematic (`驾照考试`, `将+action`, contradictory cues,
  aspect/negative action states). v3.2.4 clarifies them; P5 is provisional
  until a recheck.
- **The v3.2.4 recheck passes and confirms the conclusion.** Full 120-item
  re-annotation: primary κ **0.974**, identity 0.853, action 0.984, evidence
  0.942. Faithful: neutral 14/26 (0.54), status_aware 27/30 (0.90),
  neutral_source 30/30 (1.00), status_aware_source 28/30 (0.93). Paired vs
  neutral: status_aware +0.433 [0.267, 0.600]; neutral_source +0.533
  [0.367, 0.700]; interaction −0.500 [−0.667, −0.333]. Source access beats the
  prompt; the combination is non-additive. P5 is no longer provisional.
- **Second-model agent replication: the omission/distortion asymmetry holds.**
  gemma3:12b, 30 trajectories × 4 variants. Omitted status: 0/30 unauthorized;
  distorted status: 20/30 (66.7%) unauthorized; present: 0/30; no-memory:
  0/30. The pattern is not a qwen artifact. gemma made zero present-status
  conditional-collapse errors (qwen 2/30).
- **Second-model writer replication: chain effect holds, but the mitigation
  ranking is model-dependent.** gemma3:12b, first 12 trajectories × 7
  conditions. Deterministic MATCH: direct 7, recursive 2, rewrite-matched 0,
  repeated-direct 7, neutral-source 4, status-aware 7, combined 8. Human
  faithful (κ 0.702, provisional): direct 11/12, recursive 10/12,
  rewrite-matched 7/12, repeated-direct 11/12, neutral-source 10/12,
  status-aware 11/12, combined 12/12. Rewrite-matched remains worst, but
  recursive is far less destructive than in qwen; source access alone is
  weaker; status-aware and the combination are stronger. The mitigation
  ranking is model-dependent. The writer run over-collected 30 trajectories;
  the pre-registered 12 are the primary cohort.
- **The agent asymmetry is model-robust.** gemma3:12b: omitted status 0/30
  unauthorized, distorted 20/30 (66.7%), present 0/30, no-memory 0/30. The
  omission/distortion asymmetry is not a qwen artifact.
- **Status-aware mitigation replicates at the same seed.** Seed 43: chained cue
  ABSENT 2–3/10 under status-aware vs 5–6/10 under neutral; direct 0/10 in
  both. The mitigation is not a seed or session artifact.
- **v2.3 both-wrong adjudication: 38/46 writer-side, 8 judge errors.** Most
  writer-side cases are status omission or weakening, not an explicit opposite
  status; the judge defaults to the initial status. The adjusted writer-drift
  count is 38/46. v2.3 passes its pre-registered gates.
- **The status-aware prompt is a strong but not perfect intervention.** It does
  not guarantee preservation at D5; one topic lost the confirmation cue.
- **Conditional remains the least reliable dimension.** The v2.2 fix removed
  the explicit action clause, but the neutral writer sometimes reintroduces
  action uncertainty (`上海工作待定`) or paraphrases the condition
  (`奖学金在手`). Both judges then read the action status.
- **Some both-judge errors are judge errors, not writer drift.** `确认数学建模`
  and `获奖学金` were both judged as the wrong status. The 23 neutral
  both-wrong items overstate pure writer drift by roughly 6.

## Judge Adjudication (39 disagreements)

All qwen/gemma disagreements were read manually. qwen is correct on 15, gemma
on 17, and 7 are cases where the writer removed the status and both judges
guessed. The better judge flips with the writer style:

- status-aware: gemma 9, qwen 2, both wrong 2 (the two conditional omissions).
- neutral: qwen 13, gemma 8, both wrong 5 (writer omissions).

qwen systematically downgrades explicit confirmations that carry a trailing
qualifier (`确认…但未确定时间`, `确认…考虑不确定性`). gemma systematically reads
`已获奖学金` as `CONDITION_ACTIVE` and over-credits `推进中`/`学习中` as
committed. No single judge is a valid instrument.

## Lessons and Constraints

- Deterministic checks need broad markers and must count only `OMITTED` toward
  the omission gate; `AMBIGUOUS` is reported separately.
- A keyword match proves only that the proposition is identifiable, not that
  the status is present. Report both.
- Judge agreement is necessary but not sufficient; both judges can agree on the
  wrong label when the memory is paraphrased.
- All 39 disagreements from the 30-run were manually adjudicated; new runs need
  their own adjudication pass rather than carrying stale counts.
- The rewrite-matched control separates chaining from intermediate budget
  shrinkage; writer call count and chaining remain entangled.
- A 7B writer cannot reliably emit prose + a structured sidecar in one call;
  v2.8 is blocked and needs a separate extractor or a stronger model.
- Never claim novelty before reading BELIEFMEM (2605.05583) and MemCoRe
  (2602.07885) in full.

## Hypothesis Status

- **H1 — supported.** Writer strategies differ strongly in status preservation.
- **H2 — supported under both writers; mechanism refined by v2.3 and v2.6.**
  Chained rewriting (`recursive` and `rewrite_matched`) degrades status equally
  and far more than a single compression to the same final budget. Neutral:
  D3 17 vs 17 both-correct, D5 15 vs 16, direct D5 27; status-aware: chained
  107–108 vs direct 116 both-correct across depths. The mechanism is repeated
  re-editing of the writer's own output, not shrinking intermediate budgets.
  The effect is concentrated in **intentional** status, not epistemic. The
  status-aware prompt reduces the chaining penalty (32 → 8 both-correct cells)
  but does not remove it.
- **H3 — supported.** Proposition retention (98.9–100%) coexists with status
  errors agreed by both judges.
- **H4 — untested.**

## Open Questions

- After manual adjudication of all 39 disagreements, how many neutral errors
  remain writer-side?
- Does a rewrite-matched control preserve the recursive effect?
- Can a third judge or a condition-only extraction step fix the residual
  conditional ontology errors?
- Does the D5 status-aware cue loss replicate across topics and seeds?
- Do BELIEFMEM / MemCoRe already measure this contrast?
