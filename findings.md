# Findings — Status Drift (v2 exploratory → V3 confirmatory)

This file is the evolving narrative synthesis for the autonomous research loop.
The current result is the V3 confirmatory line; the v2 sections are retained
as exploratory history. Authoritative pre-autoresearch history lives in
`docs/RESEARCH_LOG.md`; V3 protocols, freeze records, and run notes live in
`docs/research/` (`V3_*`, `2026-11-17-*`).

## Current Understanding (2026-11-17, after V3 P2–P5 and replication)

**V3 is the current result; the v2 baseline below is exploratory and must not
be pooled with it.** Under paired transformation histories with blind human
labels (30 new trajectories × 10 generated conditions + raw, 330 items,
primary-judgment κ 0.944), chained rewriting causes **status omission**, not
unsupported distortion:

- Omission among proposition-preserved items: recursive 44.4%,
  rewrite-matched 46.2%, source-peek 0.0%, direct 3.7%, repeated-direct 3.7%,
  raw 0%. Dimension-general (conditional 27.6%, epistemic 33.0%,
  intentional 27.3%).
- Unsupported distortion is 3/330 (0.9%); the condition contrasts are
  uninformative at that event count.
- Mechanism: rewrite-matched equals recursive (paired difference 0.000
  [−0.167, 0.167]) and repeated-direct behaves like direct, so repeated
  re-editing of the writer's own output — not intermediate budget shrinkage or
  raw call count — drives the loss. Source access removes it (−0.400
  [−0.567, −0.233]).
- Downstream (P4): in the synthetic Chinese tasks, omission is conservative
  (0/30 unauthorized, but evidence-consistent action −26.7 points), distortion
  is dangerous (66.7% vs 6.7% unauthorized; +0.600 [0.433, 0.767]). Replicates
  on gemma3:12b. **P4.2 does not replicate the omission side**; see the P4.2
  bullet below.
- Mitigation (P5 confirmatory, v3.2.4 recheck κ 0.974): source access alone
  1.00 faithful, status-aware prompt 0.90, combination 0.93 with a negative
  interaction (−0.500). The ranking is model-dependent.
- The v2 "intentional commitment cues are specifically vulnerable" pattern
  does **not** replicate in V3 blind human labels.

Novelty: the individual ingredients are prior work (audited in
`docs/research/2026-11-17-novelty-audit.md`); the defensible claim is the
status-specific, proposition-controlled transformation-history diagnostic.

### Real-dialogue feasibility audit (Stage 1, 2026-11-17)

- A rule-based screen over LoCoMo (10 conversations x 19 sessions) and
  LongMemEval oracle (500 x 3 sessions) produced 2,135 candidates
  (intentional 1,123, epistemic 981, conditional 31); 725 are re-mentioned in
  a later session and 269 contain a potential change cue.
- The 50-item screening set and blank A/B files are ready
  (`results/status_drift_v3_real_audit/`). A model diagnostic read — not human
  annotation — rates 42/50 as status-bearing, but semantically 32 are
  intentional, 8 conditional, and only 2 epistemic.
- Marker-based epistemic detection mostly captures "I think I'll ..." plans or
  evaluative stances. A lexical-cue metric would count those as epistemic
  status when they are not.
- Only 4/50 items are clearly consequential for a downstream authorization
  decision; P4.2 cannot be sampled from chat corpora and needs curated
  high-stakes scenarios.
- Provisional gate verdict: intentional status is viable on real dialogue;
  conditional is thin; epistemic fails dimension coverage; downstream
  relevance fails on sampled data.
- Two independent human annotations under `V3_REAL_DATA_AUDIT_PROTOCOL.md` are
  the next blocking step. The model diagnostic must not be reported as human
  annotation.
- **The 50-item screen is a mixed-provenance rubric diagnostic, not an unaided
  two-human reliability result.** A (WMY) and B (YTB) worked independently, but
  B used an AI first draft and edited every cell. Agreement: dimension κ 0.826
  and semantic labelability 0.730 are usable; `lexical_labelable` κ 0.226,
  `update_present` κ 0.170, `evidence_sufficient` κ 0.535, and
  `status_bearing` κ 0.606 fail or are weak (status-bearing raw agreement is
  0.920; kappa is prevalence-sensitive).
- **The failures are systematic rubric defects.** A misleading cue
  ("I think I'll") was counted as lexically labelable; a later re-mention was
  counted as an update; evidence sufficiency conflated gold assignability with
  later comparison; conditional risk statements were typed as epistemic.
- **Decisions (2026-11-17).** Epistemic is dropped from the real-data
  confirmatory arm (2/50 semantic epistemic) and retained in the synthetic V3
  arm; conditional is enriched with pre-registered inclusion plus a natural
  base rate; P4.2 uses a curated 40-60 high-stakes scenario bank; two
  independent humans are required (the current pair is not compliant); sample
  size is precision-based after calibration plus a pilot; the second domain is
  `longmemeval_s` (44-57 sessions), not the 1-6-session oracle.
- Stage 2 guide revised to v2; calibration on a fresh 60-item set is pending.
- **P4.2 scenario bank is built and passes automated manipulation checks.** 40
  English high-stakes scenarios (10 each: money, health, authorization,
  commitments), each with present / omitted / distorted / no-memory variants:
  36 over-commitment scenarios (26 intentional, 10 conditional) plus 4
  authorized-execution positive controls. Proposition identity is checked by
  shared content terms, length by a neutral filler (token spread <= 3), and
  the authorization rule makes the expected decision determinate.
- **P4.2 validation passes; the bank is frozen at 38/40.** Two blind human
  annotators (WMY, YTB; 2026-11-18; provenance recorded, no model assistance)
  rated all 40 scenarios. Pooled means: realism 4.11 (A 3.98, B 4.25), status
  clarity 4.98, rule clarity 4.95, distortion plausibility 4.25, stake severity
  3.35; `only_status_differs` 38/40 (raw agreement 0.975, kappa 0.655).
  `AUT-05` (both annotators) and `AUT-01` (B only; A's dissent recorded) are
  excluded because the distorted variant changes scope, not only status. The
  frozen set is 38 scenarios / 152 items (`V3_P4_2_FREEZE.md`); the
  pooled-means gate interpretation and A's 3.975 realism mean are disclosed in
  the freeze record.
- **P4.2 behavioral result: distortion harm replicates; omission is not
  conservative.** 304/304 calls, 0 parse failures, positive control 4/4 in
  both models. Unauthorized execution: present 0/38; omitted 6/38 (qwen) and
  5/38 (gemma); distorted 9/38 and 8/38. Paired vs present: omitted +0.158
  [0.053, 0.289] / +0.132 [0.026, 0.237]; distorted +0.237 [0.105, 0.368] /
  +0.211 [0.079, 0.342]. `under_action` is 0 and conditional collapse 0/10 in
  both. Most of the omission effect comes from the four authorized-execution
  controls (qwen 4/4, gemma 2/4 execute on "mentioned X"); within the 34
  over-commitment scenarios omission is 2/34 and 3/34 (CIs touch zero) while
  distortion is 9/34 and 8/34, and distorted-minus-omitted is +0.206
  [0.088, 0.353] / +0.147 [0.029, 0.265]. Conditional omission is 0/10 in both
  models. P4.2 therefore does **not** replicate P4's "omission is conservative"
  asymmetry and must not be pooled with it. Run note:
  `docs/research/2026-11-18-v3-p4-2-results.md`.
- **The control omission effect is not just the word "requesting" (v2 probe,
  32 calls).** Re-running the four controls with a topic-only omitted wording
  ("Parental controls for the tablet came up in a recent conversation"; no date,
  no request) leaves present 4/4 and distorted 0/4 in both models, and still
  yields over-action: qwen 1/4 (down from 4/4), gemma 3/4 (up from 2/4).
  n=4 and model-dependent, so descriptive only. The reasons show the
  mechanism: models assert commitment or a date that the memory does not
  contain — agent-side inference from a topic mention. The imperative request
  ("Submit ... today") remains a confound; a neutral-request v3 probe is
  optional, not required.
- **Reason coding separates the two mechanisms (analyst, not human).** All 32
  unauthorized records: the 17 distorted cases all follow an explicitly
  authorizing memory (`D1_FOLLOWED_DISTORTED_MEMORY`); the 15 omission cases
  assert an unstated commitment (`O1`, 6), upgrade a mention (`O2`, 3), or use
  the current request as authorization (`O3`, 6; all four v2 probe cases are
  `O3`). No omission case executes while acknowledging that the memory lacks a
  status. Coding is post hoc, gold-unblinded, and analyst-performed
  (`results/status_drift_v3_p4_2/analysis/unauthorized_reason_codes.csv`), not
  a pre-registered human instrument.
- **Stage 2 is pre-frozen, not frozen.** The candidate v2 guide, ontology,
  screening evidence, and calibration generator are hashed in
  `V3_REAL_STAGE2_PREFREEZE.md`. A 60-item gold calibration set (35 LoCoMo, 25
  longmemeval; 39 intentional, 15 conditional, 6 epistemic; 11 boundary and 5
  cue-mismatch items) and a 25-item model-free re-annotation subset are ready.
  Because the public LoCoMo-Refined split has only 10 conversations and all
  were used in screening, the calibration set is **not** conversation-disjoint;
  it excludes the exact items but reuses conversations. Freeze is blocked on
  the model-free re-annotation and the 60-item gold calibration; LSF/SSF
  calibration needs a separate generated-memory sheet.
- **The 25-item "model-free" check is model-assisted, not model-free.** The
  provenance records WorkBuddy/MiniMax assistance, exposure to cue-derived
  columns, and full-corpus searching for later mentions. Compared with old B:
  dimension raw 0.880 / κ 0.762, but `update_present` raw 0.200 / κ 0.040
  because old labels were mostly `unknown` while the new annotator searched the
  source; `evidence_sufficient` raw 0.560 / κ 0.042. The result is a
  model-assisted sensitivity analysis, not an anchoring estimate. A strict
  correction sheet without cue columns or source ids is ready at
  `results/status_drift_v3_real_audit/model_free_25_strict/`; a third human (or
  a washed-out YTB) must fill it. The 50-item screen remains a mixed-provenance
  diagnostic, and the 60-item calibration is the primary Stage 2 gate.
- **Stage 2 calibration v1 fails; the guide is revised to v2.1.** Both sheets
  complete (60/60), but `gold_dimension` passes (raw 0.917, κ 0.809) while
  `gold_status` fails (raw 0.633, κ 0.584; after normalizing the seven both-E0
  status entries, raw 0.750, κ 0.708). The conditional arm is n=4 (raw 0.500).
  The disagreements are systematic, not sampling noise: (1) A used
  `NOT_EXPRESSED` and B `N/A` for E0; (2) "I want to / I'd like to" was coded
  `INTENDING`/`CONSIDERING`/`EXECUTING` by A but `INTERESTED` by B (9
  disagreements); (3) `EXECUTING` was used for resolve ("I'm going to keep
  X-ing") as well as ongoing action; (4) an offer to the interlocutor ("let me
  know if you need...") was coded conditional by A but E0 by B. v2.1 adds
  explicit rules for all four. Provenance is not collected by maintainer
  decision; report the calibration as annotator-unspecified. The v2 candidate set
  excludes screening + v1 items but has only 7 conditional items; choose
  between a descriptive conditional arm and sourcing more conditional dialogue
  before annotating it.
- **Decision C: calibrate intentional/epistemic now; conditional separately.**
  A 40-item set is ready at
  `results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/`
  (25 LoCoMo, 15 longmemeval; 29 intentional, 11 epistemic; 7 boundary, 4
  cue-mismatch). It excludes screening and v1-calibration items, reuses LoCoMo
  conversations (not conversation-disjoint), and gates only `gold_dimension`
  and `gold_status`. The conditional arm is deferred; the paper must not claim
  conditional reliability from this calibration. The v2 candidate with 7
  conditional items is superseded.
- **The 40-item calibration fails on rule adherence, not ontology.** Both
  sheets complete (40/40); `gold_dimension` raw 0.875 / κ 0.600 and
  `gold_status` raw 0.675 / κ 0.607 both fail. Of 13 status disagreements, 10
  are direct v2.1 violations by A while B matches the guide: `E0` encoding (2),
  commitment inflation ("I think I'll" → `COMMITTED`, 4), desire as intention
  ("I want to" → `INTENDING`, 3), and `EXECUTING` for resolve (2). Two
  `mixed`/`E0` cases expose a target-proposition gap. v2.2 adds worked examples
  and a one-target-proposition rule (`STAGE2_V22_TRAINING.md`). Training pass,
  then re-annotate these 40 as a calibration round; do not freeze and do not use
  them as confirmatory data.
- **Run 2 (new annotator A) passes `gold_status`, fails `gold_dimension` on
  three boundary items.** `gold_status` raw 0.900 / κ 0.875 (PASS);
  `gold_dimension` raw 0.925 / κ 0.639 (FAIL on κ). The three disagreements are
  an instruction to the assistant (`S2IE-003`), past/emotional musing
  (`S2IE-021`), and a completed-action vs factual-claim boundary (`S2IE-025`).
  The status ontology is working; the dimension gate is a boundary/prevalence
  issue, not a broad failure. v2.3 adds examples for all three. Next: a new
  40-item set under v2.3, or a third-person adjudication of the three items
  with unadjudicated and adjudicated results reported side by side. Do not lower
  the gate post hoc.
- **Third-person adjudication passes both gold gates.** `S2IE-003` and
  `S2IE-021` are E0; `S2IE-025` is intentional COMPLETED. Adjudicated:
  `gold_dimension` 1.000 / κ 1.000; `gold_status` 0.975 / κ 0.969;
  `gold_strength` 0.725 / κ 0.472 (descriptive). Gold calibration is complete
  with adjudication. This is not a full Stage 2 freeze: LSF/SSF calibration,
  the cue table, inclusion rules, adjudication order, and the analysis plan
  remain to be frozen.

### v2 exploratory baseline (2026-11-16, 30-trajectory run)

The v2 pilot has a coherent result. **The writer prompt is the dominant factor
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
- **Second-model writer replication: chain effect holds, mitigation ranking is
  model-dependent.** gemma3:12b, first 12 trajectories × 7 conditions.
  v3.2.5 recheck (primary κ 0.834): human faithful direct 11/12, recursive
  8/12, rewrite-matched 6/12, repeated-direct 11/12, neutral-source 10/12,
  status-aware 11/12, combined 12/12. Recursive and rewrite-matched are the
  low conditions; direct and repeated-direct are high. Rewrite-matched remains
  the worst. Source access alone is weaker in gemma (0.83 vs qwen 1.00), while
  status-aware and the combination are at or above qwen. The mitigation ranking
  is model-dependent; the writer replication is confirmed in direction, not in
  every magnitude. The writer run over-collected 30 trajectories; the
  pre-registered 12 are the primary cohort.
- **The agent asymmetry is model-robust.** gemma3:12b: omitted status 0/30
  unauthorized, distorted 20/30 (66.7%), present 0/30, no-memory 0/30. The
  omission/distortion asymmetry is not a qwen artifact.
- **Novelty audit narrows the claim.** StateMem/StateMemBench already defines
  state tracking vs recall; ProgMem publishes structured state programs;
  BELIEFMEM publishes AGM belief revision; STALE/StateAuditor study stale state
  and downstream policy adaptation; ABBEL studies recursive summarization into
  belief states; MemTX/EAL-Bench study memory state → unauthorized action;
  TWIST benchmarks belief-change intervention. The defensible core is the
  controlled transformation-history experiment: chained re-editing isolated
  from budget/call count, proposition identity fixed, status omission vs
  distortion separated, blind human labels, and a status-only downstream
  intervention. Do not claim first state tracking, first structured state, or
  first memory→action effect. Full-text audit still required.
- **Full-text audit confirms the ingredients are prior work.** Supersede
  already rewrites a bounded notes memory per session and shows failure grows
  with conversation length, not compression ratio; ABBEL already diagnoses
  omission/incorrect updates under recursive summarization; LiveCtx already
  preserves raw history and compresses at query time; EAL-Bench already
  measures memory false authority → unauthorized action (45.4% formation, 99%
  propagation). The novelty is the **status-specific, proposition-controlled**
  combination, not chaining, summarization, source access, or memory→action
  alone.
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
- The full-text novelty audit is complete (14 PDFs, `literature/pdfs/`); the
  individual ingredients are prior work. The defensible claim is the
  status-specific, proposition-controlled combination — see
  `docs/research/2026-11-17-novelty-audit.md` for the say/do-not-say list.
- V3 annotation guides are versioned: v3.2.3 for the P2/P3 labels, v3.2.4
  for the P5 recheck, v3.2.5 for the gemma writer recheck. Do not mix
  reliability statistics across guide versions.

## Hypothesis Status

V3 statuses are authoritative; v2 evidence is kept as supporting history.

- **H1 — supported.** Writer/transformation strategies differ strongly in
  status preservation. V3: chained conditions omit status in 44–54% of
  proposition-preserved items vs 3.7% for direct; v2: status-aware 256/270 vs
  neutral 221/270 both-judge-correct.
- **H2 — supported, mechanism refined.** Repeated chained rewriting of the
  writer's own output, not intermediate budget shrinkage or call count, drives
  the loss. V3 paired omission vs recursive: rewrite-matched 0.000
  [−0.167, 0.167], repeated-direct −0.367, source-peek −0.400. v2 rewrite-matched
  (constant 220 intermediates) and the 14–18-token matched band agree.
- **H3 — supported.** Proposition retention does not guarantee status
  retention: 300/330 V3 items preserve the proposition; 88/300 are status
  omissions. Proposition loss (10–20% in chained conditions) does not explain
  the omission contrast.
- **H4 — supported for distortion; omission is task-dependent.** P4: present
  2/30 unauthorized, omitted 0/30 (but evidence-consistent −26.7 points),
  distorted 20/30 (+0.600 [0.433, 0.767]); this replicates on gemma3:12b. P4.2
  (English high-stakes, 304 calls) reproduces the distortion harm but not the
  omission side: omitted 6/38 and 5/38, distorted 9/38 and 8/38; over-commitment
  only, omitted 2/34 and 3/34 (intervals touch zero) vs distorted 9/34 and 8/34.
  Distortion is the robust harm; omission is a common failure whose behavioral
  profile depends on the task and request framing.
- **H5 — supported.** status-aware 27/30 faithful vs neutral 14/26 at 1.05×
  budget; source access 30/30 at 1.23×; combination 28/30 at 1.38× with a
  −0.500 interaction. Source access is the stronger mitigation; status-aware is
  a partial fallback. In gemma the ranking flips toward the prompt, so report
  the model boundary, not a universal mitigation.

## Open Questions

- Does the omission effect hold on natural dialogue, not only synthetic Chinese
  templates?
- The writer replication covers 12 pre-registered trajectories on one second
  model; does the mitigation ranking stabilize at 30 trajectories or a third
  writer?
- Can a separate status extractor (beyond the blocked one-call 7B sidecar)
  preserve commitment status without templated prose?
- Do the ABBEL/Supersede appendices already contain a proposition/status split?
  This is the main remaining novelty risk.
- Annotator provenance is unrecorded and adjudication is model-assisted; how
  much of the κ stability survives fully independent annotation?
- Unsupported distortion is underpowered (3/330); is the P4 distortion effect
  stable at a larger event count?
