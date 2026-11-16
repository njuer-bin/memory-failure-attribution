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
