# Conditional v2.2 Validation — PASS (2026-11-16)

**Protocol:** `docs/STATUS_DRIFT_PROTOCOL_V2_2.md`
**Run:** `--design v3 --dimensions conditional --limit 4 --writer-style status_aware --skip-judge`, seed 42.
**Judges:** qwen2.5:7b, gemma3:12b.
**Status:** successful validation; gates passed.

## Result

| Metric | Value | Gate |
|---|---:|---|
| Inter-judge agreement | 34/36 = 0.944 | ≥ 0.85 PASS |
| qwen accuracy | 36/36 = 1.000 | — |
| gemma accuracy | 34/36 = 0.944 | — |
| Deterministic proposition omission | 0/36 = 0.000 | < 10% PASS |
| Deterministic condition omission | 2/32 = 0.062 | < 10% PASS |
| Deterministic wrong condition label | 0/32 | — |

The two judge disagreements (`conditional_01_U` recursive D3 and D5) are the
same two items flagged by the deterministic condition check. Their memory text
is `去上海工作。`: the condition (奖学金) has disappeared. qwen guesses
`CONDITION_SATISFIED`; gemma guesses `CONDITION_ACTIVE`; neither reports that
the status is missing. Manual reading confirms the deterministic check, not
either judge.

## Interpretation

- The v2.1 conditional defect is fixed: removing the action-status clause
  raised inter-judge agreement from 0.25 to 0.944 and eliminated the systematic
  inversion.
- The deterministic condition check is necessary. Without it, the judge-based
  gate would have passed while missing a real writer-side condition loss.
- The only remaining defect is a recursive D3/D5 condition-cue loss in one
  topic. This is a candidate instance of the same phenomenon seen in the v2.1
  neutral writer, now visible in the conditional dimension.

## Decision

- Conditional v2.2 passes its validation gates.
- Proceed to the full 30-trajectory run with design v3, both writer styles, and
  both judges.
- Report deterministic condition omission alongside judge accuracy in all
  subsequent results.

## Limitations

- Four conditional trajectories (two topics, S/U).
- Status-aware writer only in this validation.
- Assistant adjudication, not human annotation.
