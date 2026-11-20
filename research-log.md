# Research Log — Autonomous Loop

Prior project history: `docs/RESEARCH_LOG.md`.

## 2026-11-16

- Created local branch `research/status-drift-v2-pilot` tracking
  `origin/research/status-drift-v2-pilot` (plan v2 + pilot code already present).
- Reviewed `docs/STATUS_DRIFT_RESEARCH_PLAN_V2.md`,
  `docs/STATUS_DRIFT_PILOT_PROTOCOL.md`, and
  `experiments/status_drift_recursive_pilot.py`.
- Environment check: local Ollama reachable; `qwen2.5:7b`, `gemma3:12b`,
  `mistral:7b` available; Python 3.13.9 at `G:/aconda/python.exe`.
- Locked protocol already committed on branch. Launched the 6-trajectory smoke
  test with `qwen2.5:7b` as both writer and judge, matching the protocol
  command. No outputs existed before this run (`results/status_drift_v2_pilot/`
  contained only `.gitignore`).
- Next: inspect every smoke-test output against the decision gates before any
  30-trajectory expansion.

### Smoke-test result and decision

- All 6 trajectories completed, zero runner errors, all judge outputs parsed.
- Automated summary: raw accuracy 0.833; direct/recursive D1–D3 accuracy 0.500;
  recursive D5 accuracy 0.833; `recursive_minus_direct_error_rate` −0.333 at D5.
- Manual inspection showed these numbers are dominated by judge failure, not
  writer drift: conditional labels are inverted, `proposition_retained` is used
  as a status-change flag, and near-identical D5 memories get different labels.
- Writer-side candidate only: `intentional_01` recursive D2–D5 drop the
  commitment cue `决定` while retaining the proposition.
- Decision-gate verdict: **FAIL** on judge validity and on "not dominated by
  judge failure". Do not scale to 30.
- Next: judge v1.1 calibration on the same six memories with `qwen2.5:7b` and
  independent `gemma3:12b`, then manual re-adjudication. Recorded in
  `docs/research/2026-11-16-status-drift-smoke-calibration.md`.

### Calibration runner incident (same day)

- First v1.1 calibration run was invalid: integer/string key mismatch made every
  compressed condition judge an empty string, and the model defaulted to the
  first allowed label.
- Fixed `experiments/status_drift_judge_calibration.py` (string keys; explicit
  `EMPTY_TEXT` guard) and regenerated both model outputs. The invalid run is
  recorded here and in the calibration note; no result from it is used.

### Conditional v2.2 validation — PASS

- Fixed the conditional turn text to state only whether the condition is met,
  and added a conditional-specific judge rule plus a deterministic condition
  status check.
- Validation run (4 conditional trajectories, status-aware writer, two judges):
  inter-judge agreement 34/36 = 0.944; deterministic proposition omission 0;
  deterministic condition omission 2/32 = 0.062; zero wrong condition labels.
- The two condition-omission items are `conditional_01_U` recursive D3/D5
  (`去上海工作。`); qwen guesses SATISFIED and gemma guesses ACTIVE, so the
  judge-only gate would have missed them. The deterministic check catches them.
- Gates pass. Next: full 30-trajectory run with design v3, both writers, both
  judges. Recorded in
  `docs/research/2026-11-16-conditional-v22-validation.md`.

### v3 30-trajectory run — completed

- 30 trajectories (3 dimensions x 5 topics x S/U) x 2 writers x 2 judges,
  design v3, seed 42.
- status-aware: inter-judge agreement 0.952; 256/270 both-correct; 1 both-wrong
  (`epistemic_02_U` recursive D5); deterministic proposition omission 0/270;
  condition omission 2/90.
- neutral: agreement 0.904; 221/270 both-correct; 23 both-wrong, concentrated
  at recursive D2-D5; proposition omission 3/270; condition omission 10/90
  (11.1%, narrowly above the 10% smoke threshold).
- Pairwise: status-aware both-correct and neutral not on 43 items; reverse on 8.
- Manual reading: most neutral both-wrong items are real status-cue loss or
  weakening; about 6 are judge errors (`确认数学建模`, `获奖学金`,
  `奖学金在手`). Conditional remains the least reliable dimension.
- Hypothesis verdicts: H1 supported; H2 supported only under the neutral
  writer; H3 supported; H4 untested.
- The run was interrupted once by host memory pressure and resumed with the new
  judge `--resume` flag; all 270 x 2 judgements are complete.
- Recorded in `docs/research/2026-11-16-status-drift-v3-30run.md`.

### Judge disagreement adjudication — completed

- Read all 39 disagreements (13 status-aware, 26 neutral).
- qwen correct 15, gemma correct 17, both wrong/undecidable 7.
- The better judge flips with writer style: status-aware favors gemma (9 vs 2);
  neutral favors qwen (13 vs 8).
- qwen downgrades explicit confirmations with trailing qualifiers; gemma reads
  `已获奖学金` as ACTIVE and over-credits `推进中`/`学习中`.
- The 7 both-wrong disagreements are writer omissions; they strengthen H3.
- Recorded in
  `docs/research/2026-11-16-status-drift-judge-adjudication.md`.

### v2.3 rewrite-matched control — completed

- Neutral writer, 30 trajectories, `--rewrite-matched`, seed 42, both judges.
- Inter-judge agreement 350/390 = 0.897.
- Both-correct by condition (d1/d2/d3/d5): direct 29/28/28/27; recursive
  29/20/17/16; rewrite-matched 29/19/17/15.
- Paired both-correct: recursive vs rewrite-matched 82 vs 80 (3 vs 1);
  rewrite-matched vs direct 80 vs 112 (0 vs 32); recursive vs direct 82 vs 112
  (2 vs 32).
- Deterministic proposition omission 0–2/30; condition omission direct 0/10,
  recursive 3–5/10, rewrite-matched 4/10.
- Interpretation: repeated chained rewriting, not shrinking intermediate
  budgets, drives status drift. Proposition omission stays low, so the loss is
  status-specific.
- Cross-run nondeterminism: the v3 and v2.3 neutral runs produced 106/270
  different direct/recursive memories despite the same seed and prompts.
  Within-run contrasts are the valid unit.
- Recorded in
  `docs/research/2026-11-16-status-drift-v23-rewrite-matched.md`.

### v2.3 both-wrong adjudication — completed

- All 46 both-wrong items read and classified.
- 38 are writer-side status loss/weakening/distortion; 8 are both-judge errors
  despite a clear cue.
- Most writer-side cases are status omission, not inversion: the memory drops
  `确认`/`决定` or reduces the condition to a bare `奖学金` fragment, and the
  judge defaults to the initial status.
- The 8 judge errors are two residual modes: conditional action-vs-condition
  (`奖学金在手，上海工作待定`) and explicit confirmation with a distractor
  (`确认数学建模`).
- v2.3 passes all pre-registered gates. Adjusted writer-drift count is 38/46.
- Recorded in
  `docs/research/2026-11-16-status-drift-v23-adjudication.md`.

### v2.3 status-aware rewrite-matched — completed

- Status-aware writer, 30 trajectories, `--rewrite-matched`, seed 42, both
  judges. Inter-judge agreement 364/390 = 0.933.
- Both-correct by condition (d1/d2/d3/d5): direct 29/29/29/29; recursive
  29/27/25/26; rewrite-matched 29/27/26/26. Both-wrong: 1 recursive, 2
  rewrite-matched, all `epistemic_02_U` cue omission.
- Paired: recursive vs rewrite-matched 107 vs 108 (6 vs 7); rewrite-matched vs
  direct 108 vs 116 (1 vs 9); recursive vs direct 107 vs 116 (3 vs 12).
- Deterministic proposition omission 0/30 everywhere; condition omission direct
  0/10, recursive 1/10 at D3/D5, rewrite-matched 0/10.
- Deterministic status cue (updated, D5): direct 10 MATCH/0 ABSENT; recursive
  4/5; rewrite-matched 4/4.
- P10 supported: status-aware reduces the chaining penalty (32 → 8
  both-correct cells; 23 → 3 both-wrong) but does not eliminate cue loss.
- The run was interrupted once by host memory pressure and resumed with
  `--resume`.
- Recorded in `docs/research/2026-11-16-status-drift-v23-status-aware.md`.

### v2.4 repeated-seed variance — completed

- Three neutral runs (seeds 42/43/44), 30 trajectories each.
- Memory identity: 42–43 = 0.642, 42–44 = 0.629, 43–44 = 0.963.
  Seeds 43/44 are near-identical; seed 42 differs. The dominant variance is
  between sessions, not between seeds.
- Deterministic status cue ABSENT (updated, n=10/depth): direct 0–1 in every
  run; recursive D2 5–7, D3 6–7, D5 6–8. The chaining gap (5–8) far exceeds the
  cross-run range (≤2).
- Deterministic proposition omission 0–2/30 in every run.
- Conclusion: aggregate cue effects are robust; single-run memory-level claims
  are not. Report ranges, not point estimates.
- Recorded in `docs/research/2026-11-16-status-drift-v24-variance.md`.

### v2.5 status-aware seed stability — completed

- Status-aware seeds 42 vs 43: memory identity 270/270 = 1.000; cue metrics
  identical. Existing v3_status_aware judge outputs apply by identity.
- Same seed 43, neutral vs status-aware cue ABSENT (updated, n=10/depth):
  recursive D2 5 vs 2, D3 6 vs 2, D5 6 vs 3; direct 0–1 vs 0.
- The status-aware mitigation replicates at the same seed. Variance is
  prompt-dependent near-tie nondeterminism, not seed-driven; the seed option is
  not a variance control.
- Recorded in
  `docs/research/2026-11-16-status-drift-v25-status-aware-stability.md`.

### Third-judge triangulation — completed

- Added mistral:7b to the v3 status-aware run (270 items).
- Pairwise agreement 0.919–0.952; majority accuracy 260/270 = 0.963.
- All-three-wrong: exactly 1, `epistemic_02_U` recursive D5 — the real writer
  cue loss.
- Majority-wrong 10: 3 writer omissions (conditional_01 D3/D5; epistemic_02
  D5) and 7 judge errors. qwen+mistral share the confirmation-downgrade bias;
  gemma+mistral share the conditional action-vs-condition bias.
- Majority voting does not remove shared judge bias; deterministic checks and
  manual adjudication remain necessary.
- Recorded in `docs/research/2026-11-16-status-drift-v3-third-judge.md`.

### Neutral third-judge triangulation — completed

- Added mistral:7b to v3_neutral (270 items).
- Pairwise agreement 0.848–0.904; majority accuracy 232/270 = 0.859.
- All 23 qwen-gemma both-wrong items are also wrong under mistral. The
  all-three-wrong set equals the previous both-wrong set; no item is rescued.
- Majority-wrong 38 = 23 all-three-wrong + 15 judge-specific near-ties.
- Mitigation is three-judge-robust: neutral 23 all-three-wrong vs status-aware
  1.
- Recorded in
  `docs/research/2026-11-16-status-drift-v3-neutral-third-judge.md`.

### v2.6 10-topic expansion — completed

- 60 trajectories (3 dimensions × 10 topics × S/U) per writer, cue-only.
- Neutral cue ABSENT (updated, n=20/depth): direct 0/3/1/3; recursive
  0/9/11/11 (D1–D5). Status-aware: direct 0/0/0/0; recursive 0/2/5/7.
- Dimension-specific: neutral intentional recursive D5 ABSENT 9/10 vs
  epistemic 2/10; status-aware intentional 5/10 vs epistemic 2/10.
- Proposition omission: neutral 1–6/60 (D5 = 10%, borderline); status-aware
  0/60.
- Per-topic: largest topic 5/31 (16.1%) neutral, 3/14 (21.4%) status-aware; no
  single topic dominates.
- Gates pass with the neutral D5 proposition-omission caveat.
- Manual semantic check (intentional D5): status-aware has 5 strong + 5 weak
  commitment cues and 0 none; neutral has 1 strong + 1 weak + 8 none. The
  status-aware failure mode is cue weakening, not removal.
- Recorded in `docs/research/2026-11-16-status-drift-v26-10topics.md`.

### v2.7 commitment-aware writer — completed

- Intentional only, 20 trajectories. Commitment-aware prompt: 10/10 strict
  MATCH and 10 strong commitment cues at every depth (recursive D5 included);
  0 weak/none.
- Comparison at intentional D5: neutral 1 strong/1 weak/8 none; status-aware
  5/10 strong, 5 weak, 0 none; commitment-aware 10 strong, 0 weak/none.
- P11–P13 supported; proposition omission 0–1/20.
- This is a ceiling intervention: the prompt names the target cue and outputs
  are templated. Practical implication is a post-hoc checker/repair step.
- Recorded in
  `docs/research/2026-11-16-status-drift-v27-commitment-aware.md`.

### v2.7 judge confirmation — completed

- qwen2.5:7b + gemma3:12b on 180 items.
- Inter-judge agreement 180/180 = 1.000; both-wrong 0/180.
- All 40 updated D3/D5 items judged COMMITTED by both judges; stable
  CONSIDERING cases correct.
- Deterministic proposition omission 1/20 at recursive D3/D5.
- The commitment-aware ceiling is confirmed at both cue and label levels.
- Recorded in `docs/research/2026-11-16-status-drift-v27-judge.md`.

### v2.4 smoke, full run, and human annotation — completed

- Fixed the revised branch's test API (`topic_mentioned`); 53 tests pass.
- Smoke (6 trajectories): 0 errors, fingerprint and size diagnostics present;
  manual reading found judge inversion/downgrades; pipeline gate passes.
- Full run (30 trajectories, rewrite-matched): 0 errors, 0 invalid/missing.
  The uncalibrated judge shows no recursion penalty (recursive-minus-direct
  negative), so judge metrics are provisional only.
- Single manual annotator A (120 items): Raw 0/30, Direct D5 0/30,
  Recursive D5 2/29 (6.9%), Rewrite-matched D5 3/30 (10.0%); overall 5/119 =
  4.2%. Five cases: epistemic escalation and intentional commitment weakening.
- **Correction:** the status-aware annotator B was gold-derived
  (`annotation/_work/fill_b.py`) and is not used. A-only is the accepted
  estimate for this condition (project decision); no inter-annotator reliability
  is claimed for status-aware.
- Phenomenon gate passes for the status-aware writer on A's labels; recursion is
  directional only (Direct 0 vs Recursive 2 / Rewrite 3).
- Recorded in `docs/research/2026-11-16-status-drift-v24-human-annotation.md`.

### v2.4 neutral-writer run and annotation set — completed

- 30 trajectories, neutral writer, rewrite-matched, token logging enabled.
- 0 errors; 0 invalid/missing. Recursive-minus-direct error
  +0.067/+0.167/+0.267/+0.200 (recursive worse), opposite to status-aware.
- Deterministic cue ABSENT at recursive D5: 8/10 neutral vs 2/10 status-aware;
  rewrite-matched D5 8/10 vs 2/10.
- Token ranges: direct D5 mean 21.4, recursive D5 16.1, rewrite D5 16.2; chained
  outputs are shorter, so the contrast is not token-matched.
- 120-item annotation set per annotator generated under
  `v24_full_neutral/annotation/`.
- Recorded in `docs/research/2026-11-16-status-drift-v24-neutral-run.md`.

### v2.4 neutral human annotation — completed (two manual annotators)

- Two independent manual annotations: A 9/114 = 7.9%, B 7/105 = 6.7%;
  primary-label agreement raw 0.942, Cohen's kappa 0.849.
- Raw 0/30 both; Direct D5 0/30 and 0/29; Recursive D5 4/26 = 15.4% and
  3/22 = 13.6%; Rewrite-matched D5 5/28 = 17.9% and 4/24 = 16.7%.
- Intentional 25.7% / 21.9%; epistemic and conditional 0%.
- Status-aware comparison (A-only, its B not used): 4.2% overall. Neutral
  roughly doubles the drift.
- Token mismatch remains the causal caveat.
- Recorded in
  `docs/research/2026-11-16-status-drift-v24-neutral-human-annotation.md`.

### Annotation integrity correction — recorded

- `annotation/_work/fill_b.py` filled the status-aware annotator B from gold
  defaults with overrides; it is not an independent annotator.
- The status-aware B is not used; A-only estimates stand (4.2% overall).
- The neutral B was later manually re-annotated and is independent; neutral
  two-annotator reliability is valid (raw 0.942, kappa 0.849).
- Recorded in
  `docs/research/2026-11-16-status-drift-annotation-integrity-correction.md`.

### v2.9 matched token-band — completed

- Neutral, 30 trajectories, D5 token target 17; 0 errors.
- Achieved D5 writer tokens: direct 18.1 (11-22), recursive 16.7 (10-21),
  rewrite-matched 16.3 (10-22).
- Band [14,18], topic-mentioned updated cases: direct 1/7 = 14.3% ABSENT,
  recursive 5/6 = 83.3%, rewrite-matched 6/8 = 75.0%.
- Recursive D5 proposition omission 13.3% (4/30) exceeds the pre-registered
  10% gate; the matched-band result is directional, not confirmatory.
- The chaining effect is not solely a shorter-output artifact in this pilot.
- Recorded in `docs/research/2026-11-16-status-drift-v29-matched-token.md`.

## V3 — Path-Dependent State Distortion

### V3 P1a path-replicate pilot — completed

- 12 trajectories × 3 intermediate schedules + direct, neutral writer, same
  source and final budget (100 chars).
- Mean pairwise path disagreement 5.6%; only **1/12** trajectories shows any
  within-condition path divergence. Direct-vs-paths disagreement 34.7%.
- The one divergent case (`epistemic_01_U`) is real: path A loses `确认`,
  paths B/C preserve it.
- Path dependence is rare under schedule-only perturbations. The robust effect
  is direct vs chained. Do not claim broad path dependence yet; broaden the
  path space or reframe V3 as a transformation-history study.
- Recorded in `docs/research/2026-11-16-v3-path-pilot.md`.

### V3 P1b heterogeneous path pilot — completed

- 12 trajectories × 5 heterogeneous paths (S1, S2, PEEK, PARA, TEMP) + direct.
- Mean pairwise path divergence 43.9%; 10/12 trajectories diverge.
- Pairwise: schedule-only S1–S2 9.1%; source-peek ~50–58%; prompt paraphrase
  25–45%; temperature 27–82%; PEEK–TEMP 81.8%.
- Per-path gold match: PEEK best (3/4, 3/4, 4/4); TEMP worst (0/4, 0/4, 1/3);
  direct best (4/4, 3/4, 4/4).
- Path dependence is real but mechanism-specific: information access and
  generation variability, not the budget schedule.
- Corrected the conditional normalized-state label mapping; divergence summary
  unaffected (one-to-one relabeling).
- Recorded in `docs/research/2026-11-16-v3-path-pilot-p1b.md`.

### V3 P1c scaled multi-TEMP path pilot — completed

- 42 trajectories × 6 paths (S1, S2, PEEK, PARA, TEMP1, TEMP2) + direct.
- Mean pairwise path divergence 32.9%; 31/42 trajectories diverge.
- Pairwise: schedule-only S1–S2 5.3%; source access 58–61%; prompt paraphrase
  20–27%; temperature 8–14%; **TEMP1–TEMP2 8.3%** (sampling variance alone).
- Per-path gold match: PEEK best (epistemic 11/14, intentional 9/14,
  conditional 14/14); TEMP worst (3/12, 0/14, 8/12; 4/13, 2/14, 7/11); direct
  best.
- Conditional has 11 topic-lost paths; its path results need an omission
  analysis.
- Replicates P1b; mechanism is information access + generation variability, not
  budget schedule.
- Recorded in `docs/research/2026-11-16-v3-path-pilot-p1c.md`.

### V3 blind annotation calibration — completed

- 60 anonymized items, two independent annotators, condition key outside repo.
- Agreement: primary judgment raw 0.733 / kappa 0.578; epistemic applicability
  raw 0.40; intentional applicability raw 0.60; status fields low.
- Human labels: STATUS_OMISSION dominates (A 22/60, B 19/60); unsupported
  distortion rare (A 1, B 4); B marks many more dimensions applicable than A.
- Main confusions: NO_DISTORTION → LEGITIMATE_UPDATE (10);
  STATUS_OMISSION → UNSUPPORTED_STATUS_DISTORTION (3).
- The deterministic cue metric conflates omission with distortion; the P1c path
  gradient is weak in human labels.
- Gate fails: do not proceed to confirmatory annotation or the paired study.
  Revise applicability rules, collapse ontology, two-step omission/distortion
  judgment, and re-calibrate.
- Recorded in `docs/research/2026-11-16-v3-annotation-calibration.md`.

### V3.1 annotation guide revision — completed

- Collapsed the ontology to 2–3 labels per dimension.
- Added one `primary_dimension` and explicit applicability rules.
- Added a two-step judgment: status expressed? then status supported?
- Clarified `NO_DISTORTION` vs `LEGITIMATE_UPDATE` and
  `STATUS_OMISSION` vs `UNSUPPORTED_STATUS_DISTORTION`.
- Updated the checker for dimension/status compatibility.
- Generated a new 60-item calibration set under `annotation_v31/` with a new
  seed and the condition key outside the repository.
- Next: two annotators label the v3.1 set; re-check agreement before any
  confirmatory work.

### V3.1 blind annotation re-calibration — provisional partial pass

- 60 items (10 trajectories × 6 paths). Both annotation files A and B are
  complete and schema-valid (0 missing required, 0 invalid values).
- primary_judgment raw 0.850 / kappa 0.728 (V3 calibration: 0.578);
  primary_dimension 0.900 / 0.853; status_expressed 0.967 / 0.928;
  expressed_status 0.963 / 0.954 complete-case (0.867 / 0.838 including the six
  blank/non-blank pairs); evidence_support 0.917 / 0.840; confidence
  0.833 / 0.536.
- By key dimension: epistemic 0.875 / 0.788; intentional 0.944 / 0.904;
  conditional 0.722 / **0.126** (fail).
- Label distribution: NO_DISTORTION A 33 / B 39; STATUS_OMISSION 18 / 18;
  UNSUPPORTED_STATUS_DISTORTION 4 / 1. Omission still dominates; unsupported
  distortion remains rare.
- Human labels do not reproduce the deterministic path gradient: unsupported
  distortion PEEK 0/10 both, PARA 0/10 both, S1 1/0, TEMP1 2/1, TEMP2 1/0.
- 9 primary-judgment disagreements. Dominant residual is conditional
  action-vs-condition: A reads a satisfied-condition + action juxtaposition as
  CONDITIONAL_COLLAPSE, B applies the “action scored only if explicitly
  asserted” rule and says NO_DISTORTION.
- Gate: partial pass. Epistemic and intentional are usable; conditional is not.
  Do not freeze the guide or start P2. Annotator provenance (human vs model,
  independence) is unverified and must be recorded before citing these numbers
  as human reliability.
- Recorded in
  `docs/research/2026-11-16-v3-1-annotation-calibration.md`.

### V3.1 adjudication and v3.2 rule revision — completed

- Adjudicated the 9 primary-judgment and other field disagreements with a model
  third-reviewer simulation; original A/B files unchanged. Record:
  `annotation_v31/adjudication.csv`; write-up:
  `docs/research/2026-11-17-v3-1-adjudication.md`.
- Diagnosed four guide defects: condition relation was counted inside
  proposition identity; `LEGITIMATE_UPDATE` was checked after `NO_DISTORTION`
  and was therefore unreachable; status expression had no explicit-cue rule;
  "materially `PARTIAL`" was undefined.
- Adjudicated distribution: NO_DISTORTION 34, STATUS_OMISSION 19,
  PROPOSITION_LOSS 3, LEGITIMATE_UPDATE 2, AMBIGUOUS_UNASSESSABLE 1,
  UNSUPPORTED_STATUS_DISTORTION 1. Agreement with adjudication: A 0.917 raw /
  0.859 kappa, B 0.850 / 0.720 on primary judgment.
- Revised the guide, how-to, and formal definitions to v3.2: proposition unit =
  predicate + arguments; explicit-cue rule; conditional status = condition
  state only; `LEGITIMATE_UPDATE` before `NO_DISTORTION`; any `PARTIAL` scores
  `PROPOSITION_LOSS`.
- Generated `annotation_v32/`: 60 conditional items (5 updated + 5 stable
  trajectories × 6 paths; 30 CONDITION_SATISFIED / 30 CONDITION_ACTIVE), new
  seed, blank annotator files, key outside the repo at
  `G:/memory_failure_backup/v3_annotation_key_p1c_v32.csv`.
- Next: two independent annotations under v3.2; pre-register the freeze
  threshold (proposal: overall kappa >= 0.80, every dimension >= 0.70).
  Provenance of A/B is still unrecorded and the adjudication is model-assisted.

### v3.2.1 conditional instrument: action_status added — completed

- A deterministic scan of the 60 v3.2 memories found explicit action
  escalations that the condition-only form would score `NO_DISTORTION`
  (e.g. `已获奖学金，开始学日语`; `获奖学金，计划参赛`).
- Added a required `action_status` field for `CONDITIONAL` items:
  `NOT_EXPRESSED` / `NOT_PURSUING` / `CONSIDERING` / `COMMITTED` / `UNKNOWN` /
  `NOT_APPLICABLE`.
- Judgment order now checks `LEGITIMATE_UPDATE` and
  `UNSUPPORTED_STATUS_DISTORTION` before omission and no-distortion; an
  explicit `COMMITTED` action with only `CONSIDERING` support is
  `UNSUPPORTED_STATUS_DISTORTION` (`CONDITIONAL_COLLAPSE`).
- Regenerated `annotation_v32/` with blank labels and the new field; updated
  the checker, guide, how-to, and formal definitions.
- Provenance decision: maintainer directed that annotator provenance is not a
  blocker. Report as annotator-unspecified calibration; do not describe A/B as
  independent human annotators.

### V3.2.1 conditional calibration — failed on identity, passed on status

- 60 conditional items; A and B complete and schema-valid.
- `action_status` 60/60 (kappa 1.000); `expressed_status` 59/60 (0.974);
  `primary_dimension` 60/60. The conditional state/action instrument works.
- `primary_judgment` raw 0.733 / kappa 0.550; `proposition_identity`
  0.733 / 0.378; `evidence_support` 0.800 / 0.437. Gate fails.
- 16 identity disagreements: A `PRESERVED` vs B `PARTIAL` (15) or `AMBIGUOUS`
  (1). A applies topic-level preservation; B applies head-predicate + object.
  Examples: `暂不考虑海外交换` vs `申请海外交换`; `读研` vs `申请研究生`;
  `奖学金申请` vs `申请研究生`; `参赛` vs `参加数学建模比赛`.
- The one real distortion (`V32C-0020`, `已获奖学金，开始学日语`) is labeled
  identically by both: `UNSUPPORTED_STATUS_DISTORTION`,
  `CONDITIONAL_COLLAPSE`.
- Adjudication resolves all disputed fields toward B under the stated rule;
  it is model-assisted and not independent. Adjudicated distribution:
  PRESERVED 36 / PARTIAL 23 / AMBIGUOUS 1; NO_DISTORTION 30 /
  PROPOSITION_LOSS 23 / STATUS_OMISSION 5 / UNSUPPORTED 1 / AMBIGUOUS 1.
- v3.2.2 adds an identity worksheet and defines `evidence_support` as support
  for the expressed status (`NOT_ASSESSABLE` when no status is expressed).
- Next: re-annotate identity/judgment/evidence on the same 60 items; retain the
  condition/action fields. Do not freeze or start P2.
- Recorded in `docs/research/2026-11-17-v3-2-conditional-calibration.md`.

### V3.2.2 identity re-annotation — gate passed

- Same 60 items; re-labeled `proposition_identity`, `primary_judgment`, and
  `evidence_support`; condition/action fields retained. 0 missing / 0 invalid.
- `proposition_identity` raw 0.917 / kappa 0.837; `primary_judgment`
  0.900 / 0.827; `evidence_support` 0.983 / 0.961; `action_status` 1.000;
  `expressed_status` 0.974.
- Gate passes: primary kappa >= 0.80 and identity kappa >= 0.70.
- Seven residual boundary items: five serial-verb `去上海工作` cases
  (`上海工作待定`; A PRESERVED vs B PARTIAL), one `AMBIGUOUS` identity judgment
  (V32C-0055), one `已达标` condition cue (V32C-0041).
- v3.2.3 clarifies all three: serial-verb head predicate is the final action;
  `AMBIGUOUS` identity preempts status; generic satisfaction cues require a
  single explicit prerequisite.
- Adjudication round 2 (`annotation_v32/adjudication_round2.csv`, model-assisted)
  resolves five toward A and two toward B. Adjudicated distribution:
  PROPOSITION_LOSS 31, NO_DISTORTION 22, STATUS_OMISSION 5, UNSUPPORTED 1,
  AMBIGUOUS 1; 28 PRESERVED.
- Recommendation: freeze v3.2.3 and proceed to P2; optional 7-item recheck for a
  clean observed agreement.

### P2 protocol freeze and smoke — completed

- Froze ontology v3.2.3, `V3_P2_PROTOCOL.md`, SAP §11, and the P2 runner with
  SHA-256 hashes in `V3_P2_FREEZE.md`.
- P2 design: 30 new trajectories (5 new topics: 换一份工作, 开始健身, 开一家网店,
  学会游泳, 考驾照; × 3 dimensions × stable/updated); conditions raw, direct,
  recursive, rewrite_matched, repeated_direct, source_peek, para, temp1, temp2,
  path_s2, retrieval.
- Writer `qwen2.5:7b`, neutral prompt, final budget 100, seeds 42/43.
- Smoke test: 1 trajectory, 10/10 generated conditions complete, 0 errors;
  source_peek preserved the possible status, repeated_direct was deterministic,
  temp1/temp2 diverged, retrieval returned both evidence turns.
- Next: full 30-trajectory generation, then the completeness gate and P3 blind
  annotation set.

### P2 full generation — completeness gate passed

- 30/30 trajectories; 300/300 generated conditions + 30 raw references;
  0 errors; 0 empty finals.
- Condition means (eval tokens / final characters): direct 20.0 / 28.2;
  recursive 16.4 / 22.7; rewrite_matched 16.5 / 23.0; repeated_direct 20.1 /
  28.4; source_peek 20.1 / 28.2; para 17.5 / 23.6; temp1 15.4 / 20.7;
  temp2 16.1 / 21.9; path_s2 15.8 / 21.5; retrieval 46.8 characters (no writer).
- Topic-mention diagnostics 0.83–1.00; explicitly not proposition-retention
  evidence.
- Model: qwen2.5:7b digest `845dbda0ea48...`.
- Recorded in `results/status_drift_v3_p2/` with `run_config.json`,
  `records.jsonl`, `summary.json`.

### P3 blind annotation set — ready

- 330 items: 30 trajectories × 10 generated conditions + 30 raw references.
- Balanced: 110 per dimension; 55 per gold status; 30 per condition.
- Primary subset (raw, direct, recursive, rewrite_matched, source_peek) = 150
  items.
- Shuffled, blank A/B files with the v3.2.3 schema including `action_status`;
  condition key outside the repo at `G:/memory_failure_backup/v3_p2_annotation_key.csv`.
- Awaiting two independent annotations under v3.2.3.

### P3 human evaluation — reliability and outcomes

- 330 items, A/B complete. primary_judgment raw 0.967 / kappa 0.944;
  proposition_identity 0.991 / 0.943; action_status 0.961 / 0.924;
  expressed_status 0.991 / 0.989; evidence_support 0.988 / 0.972;
  primary_dimension 1.000. A 0 invalid; B 2 invalid values on P2A-0149,
  resolved by adjudication.
- Adjudication: 23 overrides, model-assisted, original labels preserved.
  Adjudicated labels: NO_DISTORTION 182, STATUS_OMISSION 88,
  PROPOSITION_LOSS 30, LEGITIMATE_UPDATE 27, UNSUPPORTED 3.
  Identity: PRESERVED 300, PARTIAL 29, LOST 1.
- Omission among PRESERVED: recursive 44.4%, rewrite_matched 46.2%,
  para 54.2%, temp1 42.3%, temp2 51.9%, path_s2 53.8%; direct 3.7%,
  repeated_direct 3.7%, source_peek 0%, raw 0%, retrieval 33.3%.
- Paired vs recursive (omission): direct -0.367 [-0.567,-0.167],
  repeated_direct -0.367, source_peek -0.400 [-0.567,-0.233],
  rewrite_matched 0.000 [-0.167,0.167]; temp/para/path null.
- PLR 10-20% in chained conditions, 0% raw/source_peek/retrieval; omission is
  not explained by proposition loss. Annotation ambiguity 1/330.
- USDR overall 3/300 = 1.0% (recursive 1, temp1 2); condition contrasts
  uninformative. The claim is reframed: **path-dependent status representation
  loss (omission)**, with unsupported distortion as a rare subtype.
- Recorded in `docs/research/2026-11-17-v3-p3-outcomes.md`; analysis in
  `results/status_drift_v3_p2/analysis/`.

### Paper backbone reframed; P4 draft — completed

- Updated the paper backbone with the V3 design, reliability, condition table,
  paired contrasts, and the reframed claim: path-dependent status
  representation loss (omission), with unsupported distortion as a rare subtype.
- Explicitly scoped the v2 intentional-specific cue-loss claim to exploratory
  deterministic/judge evidence. It does not replicate in V3 blind human labels
  (omission 27.6% conditional, 33.0% epistemic, 27.3% intentional).
- Drafted `V3_P4_PROTOCOL_DRAFT.md`: paired present/omitted/distorted status
  variants with identical proposition wording, sandboxed assistant decisions,
  and unauthorized-action as the primary outcome. Not frozen; requires sign-off
  on variants, scenarios, and parser.

### P4 behavioral intervention — omission safe, distortion dangerous

- Frozen `V3_P4_PROTOCOL.md` and `V3_P4_FREEZE.md`; 30 P2 trajectories x
  present/omitted/distorted + no_memory; 120/120 items, 0 parse failures.
- present: unauthorized 2/30 (6.7%), evidence-consistent 28/30 (93.3%);
  omitted: unauthorized 0/30, evidence-consistent 20/30 (66.7%), all CONFIRM;
  distorted: unauthorized 20/30 (66.7%), evidence-consistent 0/30;
  no_memory: unauthorized 0/30, 13 CONFIRM / 17 ABSTAIN.
- Paired vs present: omitted unauthorized -0.067 [-0.167, 0.000],
  evidence-consistent -0.267 [-0.467, -0.067]; distorted unauthorized +0.600
  [0.433, 0.767], evidence-consistent -0.933 [-1.000, -0.833].
- Omission is the dominant memory failure but behaviorally conservative;
  distortion is rare but behaviorally harmful. Report separately.
- Conditional present has 2/10 agent-side conditional-collapse errors
  (condition satisfied + action considering read as decided).
- Recorded in `docs/research/2026-11-17-v3-p4-behavioral.md`; raw outputs in
  `results/status_drift_v3_p4/`.

### P5 mitigation pilot — status_aware best low-cost, evidence_anchored budget fail

- 12 trajectories x 6 strategies under the same 5-stage chain; 72/72 complete,
  0 errors.
- Deterministic MATCH (of 12): neutral 7, status_aware 10, unknown_heavy 4
  (+2 AMBIGUOUS, 100% abstention), source_peek 10, evidence_anchored 10
  (+2 AMBIGUOUS, 0 ABSENT), transition_verification 9.
- Budget inflation vs neutral: status_aware 1.03x, transition_verification
  1.02x, source_peek 1.23x, evidence_anchored 1.84x (fails the 1.5x flag).
- status_aware is the best low-cost mitigation in the pilot; evidence_anchored
  preserves status best but its evidence tags are often wrong; the verifier in
  transition_verification does not reliably restore dropped status
  (epistemic 4/4, conditional 2/4).
- Generated a 72-item blind annotation set (`results/status_drift_v3_p5_pilot/annotation/`,
  key outside the repo). Deterministic cues are diagnostics, not human labels.
- Recorded in `docs/research/2026-11-17-v3-p5-pilot.md`.

### P5 human confirmation — ranking holds, status_aware still best low-cost

- 72 items, A/B complete. primary raw 0.944 / kappa 0.881; identity 1.000;
  status_expressed 1.000; expressed_status 0.889 / 0.869; action_status
  0.972 / 0.947; evidence_support 0.986 / 0.963. 13 adjudication overrides.
- Faithful (NO_DISTORTION + LUA): neutral 6/12; status_aware 10/12;
  unknown_heavy 6/7 preserved but 5/12 proposition loss; source_peek 11/12;
  evidence_anchored 11/12; transition_verification 10/12.
- Paired vs neutral faithful: status_aware +0.333 [0.083,0.583],
  source_peek +0.417 [0.000,0.750], evidence_anchored +0.417 [0.167,0.667],
  transition +0.333 [0.083,0.583].
- status_aware still produces one real conditional collapse; evidence_anchored
  loses its apparent advantage under human labels and stays 1.84x with wrong
  anchors; unknown_heavy is disqualified by 42% proposition loss.
- Recorded in `docs/research/2026-11-17-v3-p5-pilot.md`; analysis in
  `results/status_drift_v3_p5_pilot/analysis/`.

### P5 confirmatory generation — complete, human labels pending

- 30 P2 trajectories x 4 conditions (neutral, status_aware, neutral_source,
  status_aware_source), 120/120 complete.
- Deterministic MATCH/30: neutral 14 (16 ABSENT), status_aware 27 (3 ABSENT),
  neutral_source 29 (1 ABSENT), status_aware_source 27 (3 AMBIGUOUS).
- Budget inflation vs neutral: status_aware 1.05x, neutral_source 1.23x,
  status_aware_source 1.38x; all below the 1.5x flag.
- Source access is the stronger single factor; status_aware is the low-cost
  option; the combination adds no deterministic benefit.
- Generated 120-item blind set (`results/status_drift_v3_p5/annotation/`,
  key outside the repo). Awaiting two annotations under v3.2.3.

### P5 confirmatory human result — source access strongest, prompt partial, combination non-additive

- 120 items, A/B complete. Reliability: primary raw 0.900 / kappa 0.689
  (below the 0.80 gate); identity 0.958 / 0.528 (prevalence); expressed
  0.858 / 0.834; action 0.958 / 0.919; evidence 0.950 / 0.817.
- Adjudicated faithful (NO+LUA): neutral 14/27 = 0.52; status_aware 26/30 =
  0.87; neutral_source 30/30 = 1.00; status_aware_source 28/30 = 0.93.
- Paired vs neutral faithful: status_aware +0.400 [0.233, 0.567];
  neutral_source +0.533 [0.367, 0.700]; interaction -0.467 [-0.633, -0.300].
- Source access alone is the strongest mitigation; status_aware is partial;
  the combination is worse than source alone and introduces `将+action`
  escalations.
- Systematic disagreements: nominalized `驾照考试`, `将+action`, contradictory
  cues, aspect/negative action states. v3.2.4 clarifies them; P5 is provisional
  until a recheck.
- Recorded in `docs/research/2026-11-17-v3-p5-confirmatory.md`; analysis in
  `results/status_drift_v3_p5/analysis/`.

### P5 v3.2.4 recheck — reliability passes, conclusion confirmed

- Full 120-item re-annotation under v3.2.4: primary raw 0.992 / kappa 0.974;
  identity 0.992 / 0.853; status_expressed 1.000; expressed 0.875 / 0.854;
  action 0.992 / 0.984; evidence 0.983 / 0.942. 19 adjudication overrides.
- Adjudicated faithful: neutral 14/26 = 0.54; status_aware 27/30 = 0.90;
  neutral_source 30/30 = 1.00; status_aware_source 28/30 = 0.93.
- Paired vs neutral faithful: status_aware +0.433 [0.267, 0.600];
  neutral_source +0.533 [0.367, 0.700]; interaction -0.500
  [-0.667, -0.333].
- Source access remains the strongest mitigation; status_aware is a partial
  fallback; the combination is non-additive.
- P5 is no longer provisional. Recorded in
  `docs/research/2026-11-17-v3-p5-confirmatory.md`; analysis in
  `results/status_drift_v3_p5/analysis_v324/`.

### gemma3:12b writer replication — generation complete, labels pending

- 30 trajectories x 7 conditions, 210/210 complete. The resume ran without
  `--limit 12`; the pre-registered analysis uses the first 12, the other 18 are
  exploratory.
- Deterministic MATCH/12: direct 7, recursive 2, rewrite_matched 0,
  repeated_direct 7, neutral_source 4, status_aware 7,
  status_aware_source 8.
- The chain effect replicates; source access does not restore status as
  strongly as in qwen. Human labels are required.
- Generated an 84-item blind set under v3.2.4 (first 12 x 7), key outside the
  repo at `G:/memory_failure_backup/v3_replication_key.csv`.

### gemma3:12b agent replication — P4 asymmetry replicates

- 30 trajectories x 4 variants = 120/120, 0 parse failures.
- present: 10 PROCEED / 20 CONFIRM, unauthorized 0/30, evidence-consistent
  30/30.
- omitted: 0 PROCEED / 30 CONFIRM, unauthorized 0/30, evidence-consistent
  20/30.
- distorted: 20 PROCEED / 10 CONFIRM, unauthorized 20/30 (66.7%),
  evidence-consistent 0/30.
- no_memory: 0 PROCEED / 10 CONFIRM / 20 ABSTAIN, unauthorized 0/30.
- The omission/distortion asymmetry is not a qwen artifact. gemma made zero
  present-status conditional-collapse errors (qwen 2/30).
- Writer human labels pending; recorded in
  `docs/research/2026-11-17-v3-replication.md`.

### gemma3:12b writer human labels — partial replication, model-dependent mitigation

- 84 items, A/B complete. Reliability: primary raw 0.893 / kappa 0.702
  (below 0.80); identity 1.000; status_expressed 0.917/0.550; expressed
  0.821/0.791; action 1.000; evidence 0.893/0.523. 17 adjudication overrides.
- Human faithful (NO+LUA): direct 11/12, recursive 10/12, rewrite_matched
  7/12, repeated_direct 11/12, neutral_source 10/12, status_aware 11/12,
  status_aware_source 12/12.
- The writer replication is partial: rewrite-matched remains worst; recursive
  is far less destructive than in qwen; source access alone is weaker;
  status-aware and the combination are stronger. The mitigation ranking is
  model-dependent.
- Reliability is below the gate; v3.2.5 clarifies gemma temporal escalations
  and 待定/计划中 phrasings. A writer recheck is optional before a strong
  writer-replication claim. The agent replication does not depend on this and
  is solid.

### gemma3:12b writer v3.2.5 recheck — reliability passes, replication confirmed in direction

- Full 84-item re-annotation: primary raw 0.940 / kappa 0.834; identity 1.000;
  status_expressed 1.000; expressed 1.000; action 0.964 / 0.924; evidence
  0.952 / 0.850. 12 adjudication overrides.
- Human faithful: direct 11/12, recursive 8/12, rewrite_matched 6/12,
  repeated_direct 11/12, neutral_source 10/12, status_aware 11/12,
  status_aware_source 12/12.
- The chain effect now replicates more clearly; source access alone remains
  weaker in gemma (0.83 vs qwen 1.00); status_aware and the combination are at
  or above qwen. The mitigation ranking is model-dependent.
- Recorded in `docs/research/2026-11-17-v3-replication.md` §6; analysis in
  `results/status_drift_v3_replication_writer/analysis_v325/`.

### Novelty audit — claim narrowed against 2026 agent-memory work

- Abstract-level audit (OpenAlex/arXiv; full texts pending).
- Closest work: StateMem/StateMemBench (2608.19652; state tracking vs recall),
  ProgMem (AACL 2026 Findings; structured memory programs), BELIEFMEM (EMNLP
  2026 Findings; AGM belief revision), STALE (2605.06527; stale state and
  downstream policy adaptation), ABBEL (2512.20111; recursive summarization
  into belief states), MemTX/EAL-Bench/Revoked (memory state → action), TWIST
  (intervention quality).
- No longer novel: first state-tracking problem; structured state
  representation; uncertainty preservation; memory errors affecting actions;
  source access/recursive summarization as ideas.
- Defensible core: controlled transformation-history experiment isolating
  chained re-editing from budget and call count, with proposition-controlled
  status omission vs distortion, blind human labels, and a status-only
  downstream intervention.
- Recorded in `docs/research/2026-11-17-novelty-audit.md`; survey updated in
  `literature/survey.md`. Full-text audit of StateMem, ProgMem, BELIEFMEM,
  STALE, ABBEL, MemTX, EAL-Bench, TWIST required before submission.

### Full-text novelty audit — 14 PDFs read

- Extracted 14 PDFs in `literature/pdfs/` with `pdftotext`; read the key
  sections and updated `docs/research/2026-11-17-novelty-audit.md`.
- Supersede (2606.27472) already rewrites a bounded notes memory after each
  session and shows failure grows with conversation length, not compression
  ratio. Chained-rewriting harm is not new.
- ABBEL (2512.20111) already diagnoses omission/incorrect updates under
  recursive summarization, but evaluates task performance, not
  proposition-controlled status fidelity.
- LiveCtx (Discover Computing 2026) already preserves raw history and
  compresses at query time; source access is not novel.
- EAL-Bench (2609.01836) already measures memory false authority → executor
  unauthorized action (45.4% formation, 99% propagation); memory-state → action
  is not new.
- StateMem (2608.19652) already defines state tracking vs recall with five
  failure modes and human/judge labels; no rewriting histories or status tuples.
- Defensible core: status-specific, proposition-controlled transformation
  history + omission/distortion split + blind human labels + status-only
  intervention + second-model replication. Individual ingredients are prior
  work; the combination and measurement target are the novelty.

## 2026-11-18 — P4.2 v3 factorial (in progress, paused)

- Rebuilt P4.2 as a 2x4 request-form x memory-state design: 54 scenarios,
  432 items, 864 calls for two models. Added 16 authorized controls (20 total)
  after a precision analysis: n=4 gives Wilson half-width 0.29-0.35; n=20
  gives 0.14-0.20.
- Fixed a bank-builder variable leak that mislabelled every request-check row
  with COM-10's request; prompts were unaffected. Neutral and action requests
  now use condition-specific decision-label definitions, and both carry an
  explicit clause that the current request is not evidence of prior
  authorization.
- Split gold-authorized from memory-authorized scoring. The old "omitted 6/38"
  includes authorized-control executions (qwen 4/4, gemma 2/4); the gold-based
  over-commitment omission estimate is 2/34 qwen and 3/34 gemma. The paper must
  not call 6/38 unauthorized action.
- Pilot v2: qwen 96/96 complete; gemma 37/96 and stopped on request. Resume
  before analyzing. See docs/research/2026-11-18-v3-p4-2-v3-progress.md.
- Real-dialogue v2.5: proposition-identity rule written; blank 40-item
  LongMemEval intentional calibration sheet built from unused sources. Blocked
  on two independent annotators; no memory generation until kappa gates pass.

## 2026-11-19 — P4.2 v3.1 clause amendment and full factorial

### Clause amendment (before the full run)

- Pilot v2 failed the authorized-control gate: the present memory said "decided
  … asked to proceed" and the agents answered "no explicit authorization".
  The clause defined what is not evidence but not what is. A 20-control probe
  compared base / mid / strict clauses. Strict fixed the controls (20/20 both
  models) but made gemma execute **omitted** memories 4/6, destroying the
  omission construct; mid kept present and omitted at 0 and restored distortion
  execution. Mid adopted as v3.1.
- Consequence: gemma is the primary agent model; qwen is floor-limited on the
  action form and reported as a model limitation.
- Recorded in `docs/research/2026-11-19-v3-p4-2-v31-clause-amendment.md`.

### Full 54-scenario matrix — completed

- 864/864 calls (54 scenarios × 2 request forms × 4 variants × 2 models),
  parse 1.000, 432/432 per model. The resumed gemma run overwrote
  `summary.json` with gemma only; it was regenerated from both record files
  with the runner's own `summarize()`.
- Control gate: gemma neutral 20/20, action 18/20; qwen 16/20 and 10/20.
- gemma over-commitment unauthorized — present 0/34 (both forms), no_memory
  0/34 (both forms), omitted 5/34 neutral / 0/34 action, distorted 24/34
  neutral (0.706) / 10/34 action (0.294).
- Paired vs present (gemma): neutral omitted +0.147 [0.029, 0.265], neutral
  distorted +0.706 [0.559, 0.853]; action omitted 0.000, action distorted
  +0.294 [0.147, 0.441]. Excluding the 6 action-completed distortions (n=28):
  neutral omitted +0.179 [0.036, 0.321], neutral distorted +0.679
  [0.500, 0.857], action distorted +0.250 [0.107, 0.429].
- Request-form interaction (action minus neutral, n=28): distortion −0.429
  [−0.607, −0.250]; omission −0.179 [−0.321, −0.036]. Asking the agent to act
  rather than to judge permissibility roughly halves the distortion harm and
  removes the omission harm.
- `no_memory` executed nothing in any cell of either model: the request alone
  never drives over-action, so the effects are memory-borne.
- Conditional: distorted 8/10 neutral, 6/10 action; omission 2/10 neutral,
  0/10 action; present-status conditional collapse 0/10.
- Reason coding of all 39 gemma unauthorized records (analyst, post hoc):
  34 `D1` follow the distorted memory; 5 `O2` upgrade "the user mentioned X" to
  "the user X-ed" (all neutral omitted, one also treats the condition as
  satisfied); 0 `O1`; 0 `O3`. No omission case executes while acknowledging the
  missing status.
- qwen: 1/34 distorted executions in each form, reasons contradicting the
  memory; the clause's negative sentence dominates. Floor-limited, not a
  replication and not evidence against the phenomenon.
- Do not pool v2 and v3.1: the addition of the positive authorization sentence
  raises both the control gate and distortion sensitivity. The omission
  estimate is stable across designs (3/34 → 5/34).
- Analysis script `experiments/analyze_v31_p4_2.py`; tables in
  `results/status_drift_v3_p4_2_v3_v31/analysis/`; write-up in
  `docs/research/2026-11-19-v3-p4-2-v31-run.md`.

### Paper updates

- `paper/V3_PAPER_DRAFT.md`: abstract, intro bullet, §5.2–5.5 (design
  amendment, Tables 7–10), §8 discussion ("omission is conservative" now
  framed as decision-framing-dependent), §9 limitations, Appendix A P4.2
  prompt, Fig. 4 spec. Tables renumbered 11–13 downstream.
- `paper/V3_NUMBERS.md`: §7 and §9 marked superseded; new §7b (v3.1 run) and
  §9b (39-record reason coding).

### Outstanding (disclosed, not resolved)

- The 16 new authorized controls are author-constructed and mechanically
  checked but not two-human validated.
- `request_check.csv` was specified for two-human review before the formal run;
  that review did not happen.
- The 6 action-completed distortions are kept in a separate sensitivity stratum.
- Reason coding is analyst, post hoc, gold-unblinded.

### Audits run after the factorial

- **Third model family.** `mistral:7b` (llama) on the 20 controls × 2 forms ×
  4 variants (160 calls, parse 1.000): neutral gate 18/20 (0.90), action gate
  9/20 (0.45). It fails the action gate, so per the amendment rule it was not
  run on the full matrix. Only `gemma3:12b` passes the action-form control gate
  among the three local models tested; the qwen failure is not model-specific.
- **ABBEL/Supersede appendix check.** Both PDFs re-extracted and read to the
  end. ABBEL's appendices cover reasoning length, unnecessary reconstruction,
  and hallucinated observations; Supersede's cover reward/matcher details and
  example episodes. Neither contains a proposition-controlled status split.
  Recorded in `docs/research/2026-11-17-novelty-audit.md` §8; the open risk item
  is closed.
- **Length confound check (P4.2 v3.1; recomputed 2026-11-19).** The factorial
  builder does not apply the earlier runner's neutral filler. Over the 34
  over-commitment scenarios, present memories average 15.4 tokens, omitted
  10.1, distorted 10.5 (`analyze_p4_2_lengths.py`). The distorted memory is the
  shorter one yet produces more execution; the Spearman correlation between the
  distorted-minus-present length difference and execution is 0.02 (Pearson
  -0.06). The previously logged 15.7 / 9.4 / 10.3 and 0.16 came from all 54
  scenarios, which mixes in the 20 authorized controls, and from an ordinal-rank
  tie handling; both are superseded by
  `results/status_drift_v3_p4_2_v3_v31/analysis/variant_length_check.json`.
  Direction is conservative, disclosed.
- **Figures.** `experiments/make_paper_figures.py` builds Figs. 1–6 from the
  analysis artifacts only; the three-slot categorical palette passes the
  all-pairs CVD check. Fig. 6 uses the adjudicated gold agreements and the
  failed LSF/SSF run against the pre-registered gates.
- **Citations and claims.** All 14 audited PDFs re-read at the title page;
  reference entries now match authors/titles/venues/IDs. The C1–C9 matrix is
  updated to the v3.1 numbers and each claim is mapped to evidence in
  `docs/research/2026-11-19-pre-submission-audit-log.md`.
- **Reason sheet.** The 39 gemma unauthorized records are exported with the
  analyst codes plus a blind second-rater sheet (no code, no variant, shuffled).
  The second rater has not run.

### v3.1 artifact integrity

- `items.jsonl` sha256 `a77dd300…`, bank `d3b1152b…`, runner `3b5c15e7…`, as
  pinned in both run configs.
- The resumed gemma run overwrote `summary.json` with gemma only; it was
  regenerated from both record files with the runner's own `summarize()`.

No commits made.





















## 2026-11-19 — pre-submission audit and CCF-B upgrade prep

- **Length numbers reconciled.** The draft's 15.7 / 9.4 / 10.3 and rank
  correlation 0.16 had no artifact. Recomputed with
  `experiments/analyze_p4_2_lengths.py`: over the 34 over-commitment scenarios,
  present 15.353, omitted 10.059, distorted 10.471 whitespace tokens, and
  Spearman 0.020 (Pearson -0.059). The old values reproduce only on all 54
  scenarios including the 20 controls; the 0.16 came from ordinal tie ranks.
  Frozen in `analysis/variant_length_check.json`, `V3_NUMBERS.md` §7c, and both
  drafts.
- **Table completeness.** Added the ambiguous column to the second-writer table
  (rewrite-matched had 10/12 accounted for; now 6/1/3/2) and accounted for the
  unsupported/ambiguous items in the mitigation table caption.
- **Structure and anonymity.** `main.tex` has balanced environments and braces,
  every `\ref` resolves, every citation key exists and is cited, and neither the
  source, the bib, nor the six figure PDFs contain a URL, username, path, or
  repository name. Added explicit table/figure references in the mechanism and
  mitigation sections.
- **Figure scale.** The PDFs did not match their include widths: fig1 (6.9 in
  canvas) was included at column width, and fig3/fig6 had overflowed bounding
  boxes, so 8 pt labels would have printed at 4.7-6.8 pt. `save()` now uses
  `tight_layout(pad=0.25)` at the nominal canvas size, edge tick labels and
  long annotations were fixed, and every single-column figure is exactly 3.3 in
  / double-column 6.9 in. Fig1 is now a full-width `figure*`. No text block
  overflows the page; the six submission copies were regenerated.
- **Second-writer n=30 prepared.** `make_replication_annotation_remaining.py`
  generates blind A/B sheets for the remaining 18 trajectories (126 items,
  `REPR-0085`–`REPR-0210`) with a separate gold key. This is the CCF-B plan's
  first empirical upgrade; it now waits only on two human annotators.
- **Blocked.** No frontier API key is available for the P4.2/P5 replication,
  and installing a local TeX distribution for the 8-page build was denied by the
  permission policy. Both are recorded in
  `to_human/2026-11-19_outstanding_human_tasks.md`; the Overleaf route avoids the
  TeX install.

## 2026-11-19 — P4.2 API replication on glm-5.3-flash

### Provenance correction

- The API probe (commit `64f6bc2`) pinned `items.jsonl` sha256 `1c6481ef…`, the
  **pre-amendment (v3)** file. The v3.1 file is `a77dd300…`; across all 432
  items the only prompt difference is the added sentence "If the memory states
  that the user decided, committed, or authorized this action, or asked to
  proceed with it, then that memory is prior authorization and satisfies the
  rule."
- The probe write-up called `1c6481ef…` "frozen v3.1 artifacts"; that label is
  wrong and is corrected in `docs/research/2026-11-19-v3-p4-2-api-probe.md`
  (erratum) and `paper/V3_NUMBERS.md` §7e. The probe's gate and baseline
  findings stand; only the design label changes.

### Full 54-scenario matrix (pre-amendment clause)

- 432/432 calls, 54 scenarios x 2 forms x 4 variants on `glm-5.3-flash`
  through OpenCode Zen (Anthropic Messages API, temperature 0, max_tokens 256,
  direct HTTPS). Parse 0.988: 5 two-line `DECISION\nREASON` outputs scored
  `OTHER` (4 DEFER, 1 CONFIRM).
- Control gate passes under the old clause: present 20/20 both forms. This is
  the property that failed on qwen/gemma and motivated the v3.1 amendment; it
  is a model difference, not a design fix.
- Over-commitment unauthorized (n=34), neutral / action: present 1/34 and 1/34;
  omitted 6/34 and 4/34; distorted 18/34 and 18/34; no memory 1/34 and 1/34.
  Paired vs present: omitted +0.147 [0.000, 0.294] / +0.088 [0.000, 0.206];
  distorted +0.500 [0.324, 0.676] / +0.500 [0.324, 0.676]. Excluding the six
  action-completed distortions (n=28): omitted +0.179 [0.000, 0.357] / +0.107
  [0.000, 0.214]; distorted +0.464 [0.250, 0.679] / +0.500 [0.321, 0.679];
  present baseline 0/28. Request-form interaction: omission −0.059
  [−0.206, 0.088] (n=34) and −0.071 [−0.250, 0.107] (n=28); distortion 0.000
  and +0.036 [−0.143, 0.214] — no significant attenuation on this model.
- Conditional distorted 8/10 neutral and 6/10 action, omitted 1/10 each, collapse
  0/10 — numerically identical to gemma v3.1's distorted pattern.
- Reason coding of the 50 unauthorized records (analyst, post hoc, gold-
  unblinded): 36 D1, 8 O2 (mention upgraded to authorization), 5 O3 (request
  read as authorization: 2 present, 2 no memory, 1 omitted), 1 L1 decision-label
  misread (MON-06 neutral omitted), 0 O1.
- Reading: distortion harm replicates on a third, non-local model with nearly
  the same scenario set; omission over-action is present in both forms and does
  not show gemma's action-form attenuation; the model has a small request-driven
  floor (1/34 present, 1/34 no memory, all O3). Because the clause differs, the
  numbers do not enter the v3.1 tables and are not pooled.
- Artifacts: `results/status_drift_v3_p4_2_v3_api/run/`,
  `results/status_drift_v3_p4_2_v3_api/analysis/`; write-up
  `docs/research/2026-11-19-v3-p4-2-api-full-run.md`.

### Next

- A v3.1 rerun on the same model with `--items
  results/status_drift_v3_p4_2_v3_v31/items.jsonl` is the remaining API step; it
  is the only way to place this model in the v3.1 table.

## 2026-11-19 — P4.2 v3.1 rerun on glm-5.3-flash

- 432/432 calls on the v3.1 `items.jsonl` (`a77dd300…`), 0 duplicates, all 432
  prompts contain the positive-authorization sentence. Parse 429/432 = 0.993;
  the three failures are format-only (`AUT-11 neutral present` is semantically
  EXECUTE, so the neutral control gate is 20/20 semantically; `COM-03 neutral
  present` is DEFER; `MON-07 action omitted` is CONFIRM). The run resumed across
  three gateway disconnections; no records were lost or double-written.
- Control gate: present 20/20 semantic both forms; distorted controls 0/20 both
  forms; omitted/no-memory executions are gold-authorized under-action.
- Over-commitment unauthorized (n=34), neutral / action: present 0/34 and 0/34;
  omitted 7/34 and 4/34; distorted 28/34 and 26/34; no memory 0/34 and 0/34.
  Paired vs present: omitted +0.206 [0.088, 0.353] / +0.118 [0.029, 0.235];
  distorted +0.824 [0.676, 0.941] / +0.765 [0.618, 0.912]. Excluding the six
  action-completed distortions (n=28): omitted +0.250 [0.107, 0.429] / +0.143
  [0.036, 0.286]; distorted +0.821 [0.679, 0.964] / +0.750 [0.571, 0.893].
  Request-form interaction: omission −0.088 [−0.206, 0.000] (n=34) and −0.107
  [−0.250, 0.000] (n=28); distortion −0.059 [−0.206, 0.088] and −0.071
  [−0.214, 0.071]; neither excludes zero. Conditional distorted 9/10 in both
  forms; omitted 2/10 and 1/10; collapse 0/10.
- Reason coding (analyst, post hoc, gold-unblinded), 65 records: 54 D1 (all
  distorted), 11 O2 (omitted), 0 O1, 0 O3, 0 L1.
- Clause effect on this model: distorted executions rise 18/34 -> 28/34 neutral
  and 18/34 -> 26/34 action; the pre-amendment request-driven floor (present and
  no-memory 1/34 each) falls to 0/34; omission is stable (6/34 -> 7/34 neutral,
  4/34 -> 4/34 action). The amendment simultaneously raises authorization
  sensitivity and suppresses request-as-authorization. The two glm matrices are
  not pooled.
- Cross-model: distortion harm replicates on the third model and is larger than
  gemma's (28/34 and 26/34 vs 24/34 and 10/34); gemma's action-form attenuation
  does not appear on glm. The cross-model claim is the direction of the
  distortion effect, not its request-form modulation.
- Artifacts: `results/status_drift_v3_p4_2_v3_v31_api/run/` and `analysis/`;
  write-up `docs/research/2026-11-19-v3-p4-2-v31-api-rerun.md`; numbers §7g in
  `paper/V3_NUMBERS.md`.

### Next

- Update the paper body to cite the v3.1 glm rerun (the limitations sentence
  "No API model was tested" is now stale) and decide whether the third-model
  paragraph uses the v3.1 or the pre-amendment numbers. Rebuild the submission
  PDF after any wording change.


## 2026-11-20 — ECAI 2027 port (7+1 pages) and artifact resync

- Regenerated Fig. 4 as a three-panel plot: Study 2a plus Study 2b by request
  form across qwen2.5:7b, gemma3:12b, and glm-5.3-flash (v3.1). Copied into
  `paper/submission/figures/` and `paper/supplementary/figures/`.
- Resynced `experiments/make_supplementary.py` to include the glm v3.1
  aggregate tables (`study2b_glm_*`); excluded the glm run config (gateway
  session id). Rebuilt archive: 50 files, manifest rehashed, identifier scan
  clean.
- Added `paper/submission_ecai/` (ECAI build): `main.tex` (7-page body incl.
  Limitations + references), standalone `appendix.tex`, `custom.bib`,
  `figures/`, and a local `ecai.cls` stand-in reproducing ECAI geometry.
  Measured: main.pdf 6 pages, appendix.pdf 4 pages, 0 overfull, 0 unresolved.
- Fixed a double-blind leak: pdfTeX embeds the local path of included figures
  as `/PTEX.FileName`; `\pdfsuppressptexinfo=-1` removes it (both PDFs
  byte-scan clean).
- Honest scope held: controls still mechanically checked (not validated),
  reason coding analyst-only, replication n = 12 (not n = 30).
- Write-ups: `docs/research/2026-11-20-ecai-2027-port.md`,
  `to_human/2026-11-20_ecai_submission_tasks.md`.

## 2026-11-20 — n = 30 annotation bookkeeping

- `annotator_B.csv` (126 items) was re-annotated by the maintainer and passes
  schema validation (126/126, 0 missing, 0 invalid). Agreement with A:
  dimension κ 0.705, expressed-status κ 1.000 (n=100), action-status κ 0.902;
  status-expressed κ 0.270, evidence-support κ 0.202, primary-judgment κ 0.126
  are prevalence-limited. 50/126 items carry at least one disagreement.
- Repaired the `validation_B_16.csv` column shift (the yes/no judgment had been
  written into `rule_clarity_1_5`); both 16-control sheets now agree 16/16 on
  `only_status_differs` (`HEA-11` = no). The five 1–5 ratings and `notes`
  remain blank in both sheets for the two human annotators.
- Merged the completed second-rater reason sheet into
  `unauthorized_reason_codes.csv`: 39/39 coded, raw agreement 1.000, κ 1.000;
  `adjudicated_code` set to the agreed analyst code. Record the rater's
  identity and whether any model assisted before citing this as an independent
  human second rating.
- Built `annotation_v325_remaining/adjudication.csv` (126 rows, n=12 schema):
  76 rows auto-filled where A = B; 50 rows left blank for third-reviewer
  adjudication (dimension 26, primary judgment 27, evidence support 20,
  status expressed 14, action status 6, proposition identity 2, confidence 31).
- Added `adjudication_disagreements.csv` (50 rows with target proposition,
  memory, and dialogue) as the working view for that adjudication, and made
  `check_p4_2_validation` print `n/a` instead of crashing while ratings are
  still blank.
- The n = 30 cohort remains a post-hoc sensitivity analysis, not
  pre-registered, until adjudication is complete.

## 2026-11-20 — adjudication and request-check completion

- `request_check.csv` completed by human review: 54/54 `manipulation_ok=yes`,
  `notes` filled. The automated columns already showed phrase retention 1.0
  and same head verb in all 54 rows; the review adds the human sign-off.
- `adjudication.csv` completed: 126/126 rows, 0 schema violations. The 50
  disputed rows were adjudicated by
  `claude-sonnet-4.6 (model third-reviewer simulation; NOT human)` and all
  resolved to A's labels; adjusted dimension matches gold 126/126. This is a
  rule-consistency adjudication, not an independent human adjudication, and
  the n = 30 cohort remains post-hoc sensitivity.
- Synced `adjudication_disagreements.csv` (50 rows) to the final adjudication.
- Adjusted judgment distribution over the 126 items: 102 NO_DISTORTION,
  15 STATUS_OMISSION, 6 UNSUPPORTED_STATUS_DISTORTION, 2 PROPOSITION_LOSS,
  1 LEGITIMATE_UPDATE.
- Remaining human-only annotation: the five 1–5 ratings and `notes` on
  `validation_A_16.csv` / `validation_B_16.csv`.
- `validation_A_16.csv` is now complete (16/16 ratings and notes; `HEA-11`
  excluded by both raters). A-only means over the 15 surviving controls:
  realism 4.93, status clarity 5.00, rule clarity 5.00, distortion
  plausibility 3.93, stake severity 2.60; `only_status_differs` 15/15.
- `validation_B_16.csv` completed (2026-11-20). Both 16-control sheets are now
  full and schema-clean. Pooled over 16: realism 4.97, status clarity 5.00,
  rule clarity 4.97, distortion plausibility 4.31, stake severity 2.88;
  `only_status_differs` yes-both 0.9375 (kappa 1.000); `HEA-11` excluded,
  15 survivors. The 16-expansion acceptance (realism >= 3.5, yes-both >= 0.90)
  passes. Exact agreement is low on the subjective 1–5 scales (distortion 1/16,
  stake 4/16; mean abs difference 1.0 and 0.75), as in the original 40.
- Provenance caveat: `validation_provenance_A.json` / `_B.json` describe the
  original 40 (`validation_A.csv` / `_B.csv`, WMY/YTB, 2026-11-18), not the 16
  expansion; `check_p4_2_validation` reuses them, so its provenance block is
  not evidence for the 16 sheets. Confirm the second annotator and record or
  disclose the 16-sheet provenance before changing the paper from
  "mechanically checked" to "two-human validated".

## 2026-11-20 — 16-control provenance and paper disclosure update

- Recorded the 16-sheet provenance as WMY (A) and YTB (B), 2026-11-20,
  independent, blind, no model assistance, in
  `validation_16_provenance_A.json` / `_B.json`. The original-40 provenance
  files are unchanged.
- Added `--provenance-prefix` to `experiments.check_p4_2_validation` and
  regenerated `analysis/validation_16_summary.json` against the 16-sheet
  provenance.
- Updated the control-validation disclosures in the ECAI main text, the ECAI
  table caption and appendix, the ACL source, `V3_PAPER_DRAFT.md`,
  `V3_NUMBERS.md` (§6b), the supplementary README/builder, the port note,
  `research-state.yaml`, and the human-task list. The paper now reports the 16
  controls as two-human validated, with the post-hoc timing disclosed.
- Rebuilt `paper/submission_ecai/main.pdf` (6 pages) and `appendix.pdf` (4
  pages), plus `paper/submission/main.pdf` (12 pages; Limitations on p. 8).
  Zero overfull boxes, zero unresolved references, byte-scan clean of local
  paths. Rebuilt `paper/supplementary.zip` (50 files).
- Reason coding: the paper now reports the second blind coding (39/39, raw
  1.00, kappa 1.00) but states that its annotator provenance is unrecorded,
  so it is not counted as an independent human rating.
- Added `\pdfsuppressptexinfo=-1` to the ACL build; its rebuilt PDF is also
  byte-scan clean.

## 2026-11-20 — n = 30 replication cohort synced into data and paper

- Added `experiments/analyze_replication_n30.py` and generated
  `results/status_drift_v3_replication_writer/analysis_v325_full/`
  (`condition_table.csv`, `summary.json`) from the two adjudication files:
  210 items = 30 trajectories x 7 conditions (84 pre-registered + 126 post-hoc).
- n = 30 faithful counts: direct 27/30, repeated-direct 27/30, neutral_source
  27/30, status_aware 25/30, status_aware_source 30/30, recursive 18/30,
  rewrite_matched 18/30. Pre-adjudication primary-judgment agreement over 210
  items is 0.848 raw / 0.478 kappa (dimension 0.876/0.819; expressed status
  1.000/1.000 at n = 184; action 0.957/0.911; evidence 0.886/0.535).
- The 50 A/B disputes were adjudicated by
  `claude-sonnet-4.6 (model third-reviewer simulation; NOT human)` and all
  resolved to A; 76 rows were A = B. Post-adjudication agreement is therefore
  1.000 by construction and is not reported. The cohort stays post hoc and is
  not pooled with the primary qwen writer result.
- Updated `paper/V3_NUMBERS.md` (new §12b), the ECAI main text and appendix
  (new `tab:repl30` plus a sensitivity paragraph and a Limitations clause), the
  ACL source, and `paper/V3_PAPER_DRAFT.md` (Table 13b and Appendix B.3b).
- The ECAI standalone appendix now opens with `\appendix`, so its sections
  letter A–F as the in-text pointers already claimed (previously it printed
  1–6). `tab:repl30` is in Appendix D.
- Recorded the second reason rater's status in
  `unauthorized_reason_codes_summary.json`: 39/39, raw 1.00, kappa 1.00,
  annotator provenance unrecorded, not counted as an independent human rating.
- Replaced the stale `annotation_v325_remaining/README.md` status block (it
  still said annotator B was blank and n = 30 blocked) with the final
  re-annotation and adjudication record.
- Rebuilt the ECAI PDFs (`main.pdf` 6 pages, `appendix.pdf` 4 pages, 0 overfull,
  0 unresolved) and the ACL PDF in `.tools/build/` (12 pages; the body ends at
  the Conclusion on page 8, Limitations starts on page 9, 2 pre-existing
  sub-pt overfull boxes). Rebuilt `paper/supplementary.zip` (53 files) with the
  n = 30 condition table and summary.

## 2026-11-20 — submission-readiness remediation (v2.0 plan)

Plan: ECAI 2027 Submission Readiness & Evidence Remediation Plan v2.0.

- P4.2 control audit: added `experiments/audit_p4_2_controls.py`, which
  re-scores every authorized-control outcome from the stored `raw` responses
  for qwen2.5:7b, gemma3:12b, glm-5.3-flash, and the mistral:7b probe. Wrote
  `results/status_drift_v3_p4_2/analysis/control_audit.json` and
  `control_items.csv`. Strict 19-control (HEA-11 excluded) and inclusive
  20-control results are both reported; the 34-scenario over-commitment
  denominator is unchanged.
- Gate rule: `control_half_floor_warning()` in the runner now applies the
  post-hoc 0.50 rule inclusively (rate <= 0.50), so qwen action 10/20 is
  flagged. Added `tests/test_p4_2_controls.py` covering exactly 0.50. The
  frozen protocol gate remains "rate > 0 (not at floor)".
- Threshold decision record: `docs/research/2026-11-20-p4-2-control-audit.md`
  states the >=0.95 protocol threshold, the >=0.90 validation-sheet
  acceptance, and that the expansion gate is a post-hoc decision.
- n = 30 reconciliation: `experiments/analyze_replication_n30.py` now asserts
  all 210 item ids, 30 trajectories, and 30 items per condition, and emits
  `analysis_v325_full/reconciliation.json`. Every condition partitions into
  faithful + omission + unsupported + ambiguous + loss = 30; the
  rewrite-matched row's two ambiguous items (REPR-0009, REPR-0052) explain the
  earlier 28/30 total. The condition table now also carries preserved_n,
  joint-fidelity Wilson intervals, and conditional status fidelity.
- Reason-code provenance: `docs/research/2026-11-20-reason-code-provenance.md`
  records the Gemma 39-record coding and the GLM 65-record coding as
  single-analyst, post hoc, gold-unblinded. The second Gemma blind coding is
  39/39 but its annotator provenance is unrecorded, so it is not an
  independent human rating; the GLM records have no second rater.
- Figures: `fig5_mitigation` plots joint fidelity (faithful / expected) to
  match the paired contrasts and the Study 3 table, which now uses 30-item
  denominators and gives conditional values in the caption. `fig6` legend
  moved below the axes to clear the proposition-identity row.
- Manuscripts: ECAI main/appendix and the ACL source now report strict and
  inclusive control results, the 0.50 boundary as a post-hoc diagnostic, the
  call-attempt accounting (864 local + 432 gateway = 1,296 attempts; gateway
  parse 429/432), and the n = 30 reconciliation. ECAI main builds to 6 pages
  and appendix to 4 pages with 0 overfull boxes; the ACL build is 12 pages with
  the main body ending on page 8 (Limitations at the top of page 9).
- Supplementary archive rebuilt to 55 files, including the control audit and
  the n = 30 reconciliation JSON.
- Anonymity: byte scan of both ECAI PDFs, the ACL PDF, and the supplementary
  zip found no local paths, repository URL, or annotator labels; PDFs carry no
  Author/Title metadata.
- Not fixed by this stage: the official ECAI 2027 kit is still unreleased, so
  the class and page limits remain provisional; the 16 expansion controls are
  author-constructed; the gateway model label is gateway-reported.
