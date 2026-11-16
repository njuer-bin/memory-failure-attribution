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
- Human annotation: 120 items per annotator, balanced gold statuses;
  unsupported-status agreement 1.000 (kappa 1.0).
- Primary drift: Raw 0/30, Direct D5 0/30, Recursive D5 2/27–29 (6.9–7.4%),
  Rewrite-matched D5 3/28–30 (10.0–10.7%); overall 4.2–4.3%. Five cases:
  epistemic escalation and intentional commitment weakening.
- Phenomenon gate passes for the status-aware writer; recursion is directional
  only (Direct 0 vs Recursive 2 / Rewrite 3).
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

### v2.4 neutral human annotation — completed

- 120 items per annotator; primary-label agreement raw 0.900, kappa 0.764
  (12 disagreements).
- Overall drift 7.9% (A) / 8.2% (B); bounded 7.2-8.8%.
- Recursive D5 15.4-15.8%; Rewrite-matched D5 19.0-21.4%; Raw and Direct D5 0%.
- Intentional 21.9-25.7%; epistemic 0%; conditional 0-3.3%.
- Status-aware comparison: 4.2-4.3% overall, 6.9-7.4% recursive, 10.0-10.7%
  rewrite. Neutral roughly doubles the human-annotated drift.
- Direction robust to the 12 disagreements; token mismatch remains the causal
  caveat.
- Recorded in
  `docs/research/2026-11-16-status-drift-v24-neutral-human-annotation.md`.
