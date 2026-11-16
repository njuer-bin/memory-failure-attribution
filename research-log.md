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
