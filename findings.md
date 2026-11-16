# Findings — Status Drift v2 Pilot

This file is the evolving narrative synthesis for the autonomous research loop.
Authoritative pre-autoresearch history lives in `docs/RESEARCH_LOG.md`; the v2
plan and protocol live in `docs/STATUS_DRIFT_RESEARCH_PLAN_V2.md`,
`docs/STATUS_DRIFT_PILOT_PROTOCOL.md`, and `docs/STATUS_DRIFT_PROTOCOL_V2_1.md`
/ `_V2_2.md`.

## Current Understanding (2026-11-16, after the 30-trajectory run)

The pilot now has a coherent result. **The writer prompt is the dominant factor
in status preservation.**

- **status-aware writer:** 256/270 condition-items are correct under both
  judges; exactly **1** both-judge error (`epistemic_02_U`, recursive D5).
- **neutral writer:** 221/270 both-correct and **23** both-wrong, concentrated
  at recursive D2–D5.
- Pairwise: status-aware is both-correct where neutral is not on 43 items;
  the reverse holds on 8.
- Deterministic proposition omission: 0/270 (status-aware), 3/270 (neutral).
- Deterministic condition omission: 2/90 (status-aware), 10/90 (neutral).
- Inter-judge agreement: 0.952 (status-aware), 0.904 (neutral); all dimensions
  ≥0.80.

## Patterns and Insights

- **Neutral compression erodes status while keeping the proposition.** The
  characteristic failure is `确认`/`决定` disappearing from
  `购电脑…`, `上海工作…`, `学习日语…`, or weakening to `决定中`.
- **Recursion matters only when the writer is not status-preserving.** Under
  the neutral writer, errors cluster at recursive D2–D5; under the status-aware
  writer only one D5 item fails.
- **Repeated chained rewriting is the destructive factor, not budget
  shrinkage.** v2.3 holds intermediate budgets constant at 220 and recovers
  the same degradation as the shrinking schedule; both are much worse than a
  single compression to the same final budget. Proposition omission stays
  0–2/30, so the loss is status-specific.
- **Cross-run nondeterminism is real.** Two neutral runs with the same seed and
  prompts produced 106/270 different direct/recursive memories. Within-run
  contrasts are the valid unit; do not compare single runs as if deterministic.
- **v2.3 both-wrong adjudication: 38/46 writer-side, 8 judge errors.** Most
  writer-side cases are status omission or weakening, not an explicit opposite
  status; the judge defaults to the initial status. The adjusted writer-drift
  count is 38/46. v2.3 passes its pre-registered gates.
- **The status-aware prompt is a strong but not perfect intervention.** It does
  not guarantee preservation at D5; one topic lost the confirmation cue.
- **Conditional remains the least reliable dimension.** The v2.2 fix removed
  the explicit action clause, but the neutral writer sometimes reintroduces
  action uncertainty (`上海工作待定`) or paraphrases the condition
  (`奖学金在手`). Both judges then read the action status.
- **Some both-judge errors are judge errors, not writer drift.** `确认数学建模`
  and `获奖学金` were both judged as the wrong status. The 23 neutral
  both-wrong items overstate pure writer drift by roughly 6.

## Judge Adjudication (39 disagreements)

All qwen/gemma disagreements were read manually. qwen is correct on 15, gemma
on 17, and 7 are cases where the writer removed the status and both judges
guessed. The better judge flips with the writer style:

- status-aware: gemma 9, qwen 2, both wrong 2 (the two conditional omissions).
- neutral: qwen 13, gemma 8, both wrong 5 (writer omissions).

qwen systematically downgrades explicit confirmations that carry a trailing
qualifier (`确认…但未确定时间`, `确认…考虑不确定性`). gemma systematically reads
`已获奖学金` as `CONDITION_ACTIVE` and over-credits `推进中`/`学习中` as
committed. No single judge is a valid instrument.

## Lessons and Constraints

- Deterministic checks need broad markers and must count only `OMITTED` toward
  the omission gate; `AMBIGUOUS` is reported separately.
- A keyword match proves only that the proposition is identifiable, not that
  the status is present. Report both.
- Judge agreement is necessary but not sufficient; both judges can agree on the
  wrong label when the memory is paraphrased.
- Do not scale further until the 39 judge disagreements are manually
  adjudicated and the conditional ontology is tightened again.
- Direct and recursive conditions are not matched on rewrite count; the
  recursion claim mixes recursion with repeated editing.
- Never claim novelty before reading BELIEFMEM (2605.05583) and MemCoRe
  (2602.07885) in full.

## Hypothesis Status

- **H1 — supported.** Writer strategies differ strongly in status preservation.
- **H2 — supported under the neutral writer; refined by v2.3.** Chained
  rewriting (`recursive` and `rewrite_matched`) degrades status equally
  (D3 17 vs 17 both-correct, D5 15 vs 16) and far more than a single
  compression to the same final budget (D5 27). The mechanism is repeated
  re-editing of the writer's own output, not shrinking intermediate budgets.
  It is not observed under the status-aware writer (one D5 error).
- **H3 — supported.** Proposition retention (98.9–100%) coexists with status
  errors agreed by both judges.
- **H4 — untested.**

## Open Questions

- After manual adjudication of all 39 disagreements, how many neutral errors
  remain writer-side?
- Does a rewrite-matched control preserve the recursive effect?
- Can a third judge or a condition-only extraction step fix the residual
  conditional ontology errors?
- Does the D5 status-aware cue loss replicate across topics and seeds?
- Do BELIEFMEM / MemCoRe already measure this contrast?
