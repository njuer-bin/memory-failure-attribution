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









