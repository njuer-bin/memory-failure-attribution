# Findings — Status Drift v2 Pilot

This file is the evolving narrative synthesis for the autonomous research loop.
Authoritative pre-autoresearch history lives in `docs/RESEARCH_LOG.md`; the v2
plan and protocol live in `docs/STATUS_DRIFT_RESEARCH_PLAN_V2.md` and
`docs/STATUS_DRIFT_PILOT_PROTOCOL.md`.

## Current Understanding

As of 2026-11-16, one 6-trajectory smoke test has been run (writer = judge =
`qwen2.5:7b`). The pipeline is reproducible and every output parsed, but the
v1.0 judge is **not a valid instrument** for this pilot:

- The conditional judge inverts `CONDITION_ACTIVE` and `CONDITION_SATISFIED`.
  Its own rationale says "条件未满足" while the label field says
  `CONDITION_SATISFIED`.
- `proposition_retained` is used to mean "status changed" or "wording changed",
  not "the proposition is missing". It is false even on the raw full dialogue.
- Historical uncertainty markers are read as current uncertainty, downgrading
  explicit confirmations.
- Near-identical D5 memories receive different labels at temperature 0.

Manual (assistant) inspection indicates the **writer is mostly faithful** at
D1–D3. The clearest writer-side candidate is `intentional_01`, where recursive
D2–D5 memories drop the commitment cue `决定` while keeping the proposition.
This is a candidate for H2/H3, not a certified finding.

## Patterns and Insights

- Apparent "recursion improves status accuracy at D5" is judge noise, not a
  recursion effect.
- Automated accuracy/CPSD numbers from v1.0 should not be interpreted; the
  denominator (`proposition_retained`) is broken.
- The pilot is doing its job: it exposed a measurement failure before a larger
  run, which is why the decision gate exists.

## Lessons and Constraints

- Same-model writer/judge can share correlated errors; treat v1.0 results as
  exploratory only.
- Character budgets are approximate, not token-matched.
- `evaluate_condition` excludes `INVALID_LABEL`/`PARSE_ERROR` from denominators;
  always compare `n_valid` with `completed_trajectories`.
- The 6-item smoke test is far too small to distinguish real drift from judge
  noise. Do not scale until judge v1.1 is validated on the same memories.
- Never claim novelty before checking HELM, ProgMem, BELIEFMEM, and Answer
  Bubbles full texts and appendices. The local web-search backend returned no
  results for these names on 2026-11-16; bibliographic details remain unverified.
- Do not tune the writer prompt after seeing outputs. Judge v1.1 is a
  calibration of a demonstrably broken instrument and is versioned and
  documented separately.

## Open Questions

- Does judge v1.1 fix the conditional inversion with both `qwen2.5:7b` and the
  independent `gemma3:12b`?
- After calibration, do the conditional and epistemic "errors" disappear,
  leaving only the `intentional_01` recursive cue-loss candidate?
- Is commitment-cue loss under recursion reproducible across topics, or is it a
  single-topic artifact?
- At what recursion depth does the proposition itself (not just the status cue)
  start to disappear?
