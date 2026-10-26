# Stage B design — architecture ablation for the construction confound

Status: design only, 2026-10-26. Do not run until frozen in
`docs/PRE_REGISTRATION_CHANGELOG.md`. Governed by
`docs/CCF_B_DECISION_PLAN_2026-10-26.md`.

## Question

The adversarial review's critical attack (P1): the three systems' failure
fingerprints may be a direct product of the bottlenecks they were built with
(fact extraction → formation, one session summary → context, raw-turn
cosine → retrieval). This experiment changes each bottleneck and asks whether
the dominant failure stage moves with the architecture.

## Conditions

Each condition changes exactly one system's bottleneck, holding data, answer
model, judge, gate and context budget fixed.

| id | system | baseline | knob-on | expected if architecture-conditional |
|---|---|---|---|---|
| A1 | semantic | atomic fact extraction | raw-write: every turn also stored verbatim as a memory | F1 (formation) share falls; failures move to retrieval/context/reasoning |
| A2 | summary | one LLM session summary | raw-context: raw session messages replace summaries (no LLM ingest) | F5 (context) share falls; failures move to retrieval/reasoning |
| A3 | verbatim | dense top-k cosine | hybrid ranking (0.5 cosine + 0.5 question-token overlap), same k | F4 (retrieval) share falls; failures move downstream |
| A4 | all three | baseline | A1+A2+A3 together | the cross-system fingerprint no longer shows the original mapping |

A1 and A2 remove the bottleneck without changing the downstream pipeline; A3 is
the already-implemented repair. None requires new LLM ingestion except the
answer/judge calls; A2's raw-context variant needs no summarization calls.

## Measurements

Per condition, on the same 100 LoCoMo questions (`locomo_refined_public`,
sha frozen in `PROTOCOL_FREEZE.md`):

- answered accuracy (semantic, judged rows) and paired McNemar vs baseline;
- failure-stage distribution (F1–F6/E0/EVAL/RC) per system;
- stage recall at formation/retrieval/context;
- Stuart–Maxwell on paired labels: baseline vs knob-on, **within the same
  system**; Holm across the three within-system tests;
- the cross-system fingerprint (all three systems) under each condition.

## Pre-registered decision rule (gate B)

The fingerprint is **architecture-conditional** if, for at least two of the
three systems, turning off its bottleneck:

1. changes that system's dominant-stage share by **≥ 20 percentage points**
   (e.g. semantic F1 share falls by ≥0.20), and
2. the within-system Stuart–Maxwell p < 0.05 survives Holm across the three
   tests.

The fingerprint is **architecture-independent** if all three knobs leave the
dominant-stage share within ±10 points and no within-system test is significant.

Anything between is reported as partial and the claim is narrowed to the
systems/conditions where the stage moved.

## Power and cost

- n=100 questions per condition; stage-share changes of 0.20 are well above the
  0.1 detection floor at n=100 for a paired categorical test.
- A3 and A2 need no new LLM ingestion; A1 needs raw-turn writes only. Answer +
  judge calls: roughly 100 questions × (1 answer + ≤1 judge) per affected
  system ≈ 200 calls per condition; four conditions ≈ 800 calls ≈ 1–1.5 h at
  current gateway latency. Verbatim/semantic ingestion is local.
- If A2's raw-context variant is judged too far from a "real" system, treat it
  as a mechanism check, not a system result, and say so.

## Falsifiers and what would change our mind

- Knob-on improves retrieval/formation recall but does **not** move the failure
  stage: the stage distribution is not driven by the bottleneck (supports the
  phenomenon claim).
- Knob-on moves the stage but accuracy is unchanged: the stage is real but the
  bottleneck is not the binding constraint; report both.
- A1/A2 degrade accuracy so much that the comparison is unfair: report the
  accuracy delta alongside the stage delta; do not claim a clean ablation.

## Implementation notes

- A3 is already implemented (`experiments/retrieval_intervention.py`
  `rank_items`, `alpha=0.5`).
- A2: a `RawContextSystem` variant of `_EmbeddingSystem` that stores raw session
  messages instead of LLM summaries; no API ingestion.
- A1: a `write_through_verbatim`-style toggle on `SemanticSystem` that also
  writes every turn as a verbatim memory, so formation can no longer miss gold;
  measure whether F1 disappears.
- All variants reuse `run_systems` with `--systems` extended and the same
  `summary["search"]` provenance.
