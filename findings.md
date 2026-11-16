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
- **The status-aware prompt is a strong but not perfect intervention.** It does
  not guarantee preservation at D5; one topic lost the confirmation cue.
- **Conditional remains the least reliable dimension.** The v2.2 fix removed
  the explicit action clause, but the neutral writer sometimes reintroduces
  action uncertainty (`上海工作待定`) or paraphrases the condition
  (`奖学金在手`). Both judges then read the action status.
- **Some both-judge errors are judge errors, not writer drift.** `确认数学建模`
  and `获奖学金` were both judged as the wrong status. The 23 neutral
  both-wrong items overstate pure writer drift by roughly 6.

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
- **H2 — supported under the neutral writer; not under the status-aware
  writer.** Recursion adds drift only when the prompt does not require
  preservation.
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
