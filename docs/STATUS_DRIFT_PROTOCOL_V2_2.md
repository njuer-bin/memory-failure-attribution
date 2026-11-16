# Status Drift Pilot — Protocol v2.2 (Conditional Fix)

**Status:** pre-registered design revision; no v2.2 outputs exist yet.
**Branch:** `research/status-drift-v2-pilot`
**Scope:** conditional dimension only. Epistemic and intentional templates are
unchanged.

## 1. Why revise

The v2.1 smoke showed that the conditional dimension is invalid:

- The final turn states both condition satisfaction and action status, e.g.
  `我已经拿到奖学金了，所以这个条件已经满足；我现在开始考虑购买电脑。`
- The label is `CONDITION_ACTIVE` vs `CONDITION_SATISFIED`, i.e. about the
  condition (奖学金), not about whether the speaker is considering the action.
- Both judges read the action clause instead: gemma labels `已拿到奖学金` as
  `CONDITION_ACTIVE` in every compressed condition; qwen labels the stable case
  as `CONDITION_SATISFIED`. Inter-judge agreement on conditional was 0.25 in
  the status-aware run.
- This is a dataset/label defect, not status drift. Results from the v2.1
  conditional template must be discarded.

## 2. Change

### 2.1 Conditional turn text

Turn 1 is unchanged and still introduces the proposition and the condition:

    [Turn 1] 如果拿到奖学金，我才考虑{action}。

Turn 3 now states **only** whether the condition is satisfied:

- stable: `奖学金还没有结果，条件尚未满足。`
- updated: `我已经拿到奖学金了，条件已经满足。`

No action-status clause (`开始考虑`, `暂时不考虑`) appears in Turn 3.

### 2.2 Conditional judge instruction

The judge prompt adds, for the conditional dimension only:

> 只判断条件（奖学金）是否满足。说话人是否开始考虑或暂时不考虑该行动，与
> `CONDITION_ACTIVE` / `CONDITION_SATISFIED` 标签无关。

The two-step rule (quote latest evidence, then label) is unchanged.

### 2.3 Design identifier

- `--design v3` = crossed v2 design + fixed conditional turns.
- `--design v2` remains the v2.1 template for reproducibility; do not mix v2
  and v3 results.
- `--dimensions` allows a conditional-only validation run.

## 3. Validation before scaling

Run a conditional-only smoke:

    --design v3 --dimensions conditional --limit 4 --writer-style status_aware --skip-judge

Judge with qwen2.5:7b and gemma3:12b.

Gates:

- inter-judge agreement on conditional ≥ 0.85;
- deterministic omission < 10%;
- no systematic inversion (gemma must not label `已拿到奖学金` as ACTIVE);
- all disagreements manually adjudicated.

If the gates pass, run the full 30-trajectory set with `--design v3`,
`--writer-style status_aware`. The neutral writer remains a separate contrast.

## 4. Pre-registered predictions

- **P5:** conditional inter-judge agreement rises from 0.25 to ≥ 0.85.
- **P6:** gemma no longer labels `已拿到奖学金` as `CONDITION_ACTIVE`.
- **P7:** the epistemic/intentional v2.1 result (neutral writer loses status
  cues at D3/D5; status-aware writer preserves them) replicates under v3,
  since those templates are unchanged.

## 5. Integrity

- v2.1 conditional outputs remain on disk and are not reused.
- The change removes an ambiguous clause; it does not tune toward a desired
  drift result.
- No 30-trajectory run until the conditional validation gates pass.
