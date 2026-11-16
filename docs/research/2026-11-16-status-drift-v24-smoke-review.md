# v2.4 Smoke Test — Manual Review (2026-11-16)

**Protocol:** `docs/STATUS_DRIFT_PILOT_PROTOCOL.md` (v2.4)
**Run:** design v3, 6 trajectories, qwen2.5:7b writer and judge, seed 42.
**Config fingerprint:** `201c217c217362cb5095f0716695c087eaf08fd2dcb91783f0811cf421ede074`
**Output:** `results/status_drift_v2_pilot/v24_smoke/`

## 1. Pipeline checks

- 6/6 trajectories completed; 0 errors.
- Every direct and recursive depth has a memory, a judge output, a Unicode/byte
  size record, a topic-mention flag, and a condition-marker diagnostic.
- `run_config.json` contains the canonical configuration fingerprint.
- No invalid or parse-error predictions; no missing predictions.
- Topic-mention rate 100% (lexical diagnostic only, not proposition identity).

## 2. Manual reading of all six trajectories

### Correct end-to-end

- `epistemic_00_S`: all depths POSSIBLE; the uncertainty cue is preserved.
- `intentional_00_S`: all depths CONSIDERING; the considering cue is preserved.
- `intentional_00_U`: all depths COMMITTED; `决定` is preserved through the
  recursive chain.
- `conditional_00_U`: all depths CONDITION_SATISFIED; `条件已满足` is preserved.

### Judge errors (not writer drift)

- `conditional_00_S` raw: memory says `奖学金还没有结果，条件尚未满足`;
  the judge returns CONDITION_SATISFIED, while its own reason says the condition
  is not satisfied. This is the old conditional label inversion.
  `direct_d2` and `direct_d5` show the same inversion
  (`[记忆] 拿到奖学金才考虑买电脑，目前条件尚未满足。` -> SATISFIED).
  The recursive chain is correctly judged ACTIVE.
- `epistemic_00_U` direct: memory says `用户确认会购买电脑，但未确定时间` /
  `用户确认购买电脑但未购`; the judge returns POSSIBLE, gold is CERTAIN. The
  confirmation is explicit; `未确定时间` / `未购` are action/timing status, not
  epistemic status. Judge error.

### Writer-side candidate

- `epistemic_00_U` recursive D3/D5: the memory becomes
  `用户确认购买电脑但未购，已完成课程和事务。` for D2, then at D3/D5 the
  phrasing still contains `确认` but the judge marks `proposition_retained=false`.
  The direct condition keeps the confirmation more fully. This is a candidate
  cue/retention loss, but the judge is too unreliable here to certify it; human
  annotation is required.

## 3. Metric caveats observed

- `topic_mentioned` is true for every memory, including paraphrases; it is not
  proposition identity, as the v2.4 revision states.
- `condition_marker_heuristic` flags `拿到奖学金才考虑买电脑，...条件未满足` as
  AMBIGUOUS because both a satisfied marker and an active marker appear. Manual
  reading says ACTIVE; the heuristic is deliberately conservative.
- Judge metrics are exploratory: the same model writes and judges, and the
  conditional inversion and confirmation downgrades are confirmed in this smoke.

## 4. Decision

The **pipeline gate passes**: all requested trajectories complete without
unreported errors, resume fingerprinting is present, all memory outputs and
size diagnostics exist, and the labels are interpretable by a human using the
v2.4 guide.

The judge is not trustworthy enough for confirmatory metrics. Proceed to the
full 30-trajectory run with rewrite-matched to generate raw outputs for human
annotation; keep judge metrics provisional. Consider an independent judge
(gemma/mistral) for a secondary diagnostic.

## 5. Next

1. Run `v24_full` (30 trajectories, `--rewrite-matched`).
2. Build the 120-item-per-annotator reliability set from Raw / Direct D5 /
   Recursive D5 / Rewrite-matched D5.
3. Compute human agreement (raw agreement and Cohen's kappa) before any claim.
