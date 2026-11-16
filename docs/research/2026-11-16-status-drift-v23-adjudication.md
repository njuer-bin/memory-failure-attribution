# v2.3 Both-Wrong Adjudication — 46 Items (2026-11-16)

**Scope:** all 46 items in the v2.3 rewrite-matched run where both qwen2.5:7b
and gemma3:12b returned a status different from gold.
**Method:** read the memory text and gold status; classify as writer-side status
loss (A) or both-judge error despite a clear cue (B). Assistant adjudication,
not human annotation.

## Summary

| Category | Count | Meaning |
|---|---:|---|
| A — writer-side status loss/weakening/distortion | 38 | The memory no longer carries the correct status cue, or carries a distorted one. |
| B — both judges wrong despite a clear cue | 8 | The memory states the correct status, but both judges return another label. |

By dimension:

| Dimension | A | B | Total |
|---|---:|---:|---:|
| conditional | 13 | 6 | 19 |
| epistemic | 6 | 2 | 8 |
| intentional | 19 | 0 | 19 |

## Key nuance: omission, not inversion

Most A items are **status omission or weakening**, not an assertion of the
opposite status. Examples:

- `奖学金` appears as a bare fragment (`买电脑-奖学金`) with no received/not
  received status.
- `决定` disappears (`上海工作，留意天气…`), leaving the action but not the
  commitment.
- `确认` disappears (`去上海工作，天气多变…`).
- `决定` weakens to `推进中` / `推进计划`.
- One genuine distortion: `奖学金申请` / `研究生申请奖学金` turns a received
  scholarship into an application.

The binary label forces the judge to pick a status even when the memory states
none. "Both wrong" therefore overstates active inversion; the correct reading
is "status cue lost, judge defaults to the initial status." This is precisely
H3: the proposition survives, the status does not.

## Category B items (judge errors)

- `conditional_01_U` recursive/rewrite-matched d2/d3/d5 (6 items):
  `奖学金在手，上海工作待定…`. The condition is satisfied; the action is
  pending. Both judges read the action and return `CONDITION_ACTIVE`.
- `epistemic_03_U` recursive/rewrite-matched d5 (2 items):
  `确认数学建模` / `确认比赛`. The confirmation is explicit; both judges return
  `POSSIBLE`.

B is not random noise: it is two specific residual failure modes (conditional
action-vs-condition, and a confirmation with a trailing distractor).

## Gate verdict

The v2.3 protocol required every new both-wrong item to be adjudicated. That is
now complete.

- inter-judge agreement 0.897 ≥ 0.85: PASS.
- deterministic proposition omission 0–2/30: PASS.
- three contrasts reported with raw counts: PASS.
- all 46 both-wrong items adjudicated: PASS.

**v2.3 passes its pre-registered gates.** The substantive result stands:
chained rewriting, not intermediate budget shrinkage, drives status drift.

## Consequence for measurement

- Do not report "both wrong" as "status inverted." Report it as "status cue
  lost" unless the memory contains an explicit opposite cue.
- Conditional needs a condition-only extraction step before external claims.
- Epistemic/intentional need a deterministic status-cue checker analogous to
  the condition-status checker.
- The 8 B items should be excluded from writer-drift counts; the adjusted
  writer-side count is 38/46.

## Limitations

- Assistant adjudication; synthetic templates; n=30.
- No rewrite-matched status-aware run yet.
- No repeated-seed variance estimate yet.
