# Status Drift v2 — Smoke-Test Calibration Note (2026-11-16)

**Branch:** `research/status-drift-v2-pilot`
**Runner:** `experiments/status_drift_recursive_pilot.py`
**Run:** `--limit 6 --writer-model qwen2.5:7b --judge-model qwen2.5:7b`
**Status:** calibration finding; not a substantive research result.

## 1. What was run

The protocol command in `docs/STATUS_DRIFT_PILOT_PROTOCOL.md` was executed
unchanged: six synthetic trajectories (two each: epistemic, intentional,
conditional), one stable and one evidence-supported update per dimension.
Writer and judge were both `qwen2.5:7b` at temperature 0. All six trajectories
completed with zero runner errors; every condition produced parseable JSON.

## 2. Automated summary (as produced)

| Condition | Accuracy | CPSD | Omission rate |
|---|---:|---:|---:|
| Raw | 0.833 | 0.000 | 0.500 |
| Direct D1 | 0.500 | 0.400 | 0.167 |
| Recursive D1 | 0.500 | 0.400 | 0.167 |
| Direct D2 | 0.500 | 0.400 | 0.167 |
| Recursive D2 | 0.500 | 0.500 | 0.333 |
| Direct D3 | 0.500 | 0.400 | 0.167 |
| Recursive D3 | 0.500 | 0.500 | 0.333 |
| Direct D5 | 0.500 | 0.400 | 0.167 |
| Recursive D5 | 0.833 | 0.200 | 0.167 |

`recursive_minus_direct_error_rate` was 0.0 at D1–D3 and −0.333 at D5.

Taken at face value, this would suggest recursion is harmless and that raw
accuracy is unstable. Manual inspection contradicts that reading.

## 3. Manual inspection (assistant adjudication, not human)

Every memory and every judge rationale was read. The main pattern is a
**judge-instrument failure**, not writer drift.

### 3.1 Conditional label inversion

For `conditional_00` (gold `CONDITION_ACTIVE`; dialogue: 奖学金还没有结果，所以条件尚未满足):

- The writer faithfully produced `奖学金未结果，暂不考虑购买电脑。`
- The judge returned `CONDITION_SATISFIED` with `proposition_retained=false`,
  and its own rationale said "条件未满足".

For `conditional_01` (gold `CONDITION_SATISFIED`; dialogue: 已拿到奖学金，所以条件已经满足):

- The writer faithfully produced `已拿到奖学金，开始考虑去上海工作。`
- The judge returned `CONDITION_ACTIVE` with `proposition_retained=true`.

The conditional judge appears to invert the two label names and to read
"开始考虑/暂不考虑" as condition status. Every conditional condition in the
smoke test is therefore invalid.

### 3.2 `proposition_retained` is not an omission signal

`proposition_retained=false` appears on the **raw full dialogue** for
`epistemic_01` and `intentional_01`, where the proposition is plainly present.
For `intentional_01` the judge wrote that the proposition was not retained even
as its own `status` field returned the correct `COMMITTED`. The field is being
used to mean "status changed" or "the original wording changed", not "the
proposition is missing". Omission rates and CPSD denominators are therefore
unreliable.

### 3.3 Historical uncertainty read as current status

For `epistemic_01` (gold `CERTAIN`; dialogue: 我已经确认会去上海工作) the writer's
memories say `用户确认去上海工作`, but several add `但之前曾考虑不确定性` or
`原计划可能有变`. The judge downgraded these to `POSSIBLE`. Some of that
ambiguity is writer-added context, but the judge also ignored the explicit
`确认`. This failure mode also appears on the raw dialogue.

### 3.4 Writer-side observation (candidate, unconfirmed)

`intentional_01` (gold `COMMITTED`): direct memories preserve
`用户决定去上海工作并按计划推进`. Recursive D2–D5 memories become
`用户去上海工作，推进计划…`, dropping the commitment cue `决定`. The
proposition survives; the intentional status becomes ambiguous. This is the
only smoke-test case consistent with the H2/H3 hypothesis, but the current
judge cannot be used to certify it.

### 3.5 Non-determinism at temperature 0

`direct_d5` and `recursive_d5` for `epistemic_01` carry near-identical
proposition/status content, yet the judge returned `POSSIBLE` and `CERTAIN`
respectively. The reported D5 "recursive beats direct" result is judge noise,
not a recursion effect.

## 4. Decision-gate verdict

From `docs/STATUS_DRIFT_RESEARCH_PLAN_V2.md` §8:

- outputs parseable and pipeline reproducible — **PASS**
- manual review confirms the judge can distinguish the labels — **FAIL**
- candidate cases retain the proposition while changing status — **candidate
  only; one writer-side case, uncertified**
- results not dominated by omission or judge failure — **FAIL**

**Verdict: do not scale to 30 trajectories yet.** Scaling now would produce a
large table of judge artifacts. The measurement instrument must be fixed and
re-validated on the same six trajectories first.

## 5. Pre-registered instrument fix (judge v1.1)

This is a calibration change, not a result-driven tuning of the substantive
hypothesis. It is committed before the calibration run.

1. Give the judge explicit, mutually exclusive definitions for every label
   (especially `CONDITION_ACTIVE` vs `CONDITION_SATISFIED`).
2. Separate `proposition_retained` from status: ask only whether the target
   proposition is still identifiable, independent of its status.
3. Require an `evidence` span and a `confidence` field.
4. Instruct the judge to apply later evidence, and not to downgrade a confirmed
   status because earlier turns expressed uncertainty.
5. Re-score the **existing** memories only (no writer re-run) with the new
   prompt, using `qwen2.5:7b` and the independent `gemma3:12b`.
6. Report raw / direct / recursive metrics and inter-judge agreement. Manually
   re-adjudicate every disagreement before any claim.

The original v1.0 outputs are preserved in
`results/status_drift_v2_pilot/records.jsonl`; they are not overwritten.

## 6. Integrity notes

- The adjudication in §3 was performed by the assistant (an LLM), **not by a
  human annotator**. It is a diagnostic, not ground truth.
- Synthetic templates only; n=6; one writer model.
- The v1.0 judge prompt is not deleted; v1.1 is a versioned calibration.
- No claim about H1–H4 is made from this run.
