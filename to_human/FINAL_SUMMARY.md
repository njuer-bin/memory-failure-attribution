# Status Drift Pilot — Final One-Page Summary (2026-11-16)

## Question

When long-term memory repeatedly compresses a conversation, does it preserve
the **status** of a proposition (possible vs confirmed, considering vs
committed, condition active vs satisfied), even when the proposition survives?

## Answer

**No — chained rewriting degrades status, and the damage is concentrated in
intentional commitment, not epistemic certainty.** The effect is caused by
re-editing the writer's own output, not by shrinking compression budgets, and
it is preventable by an explicit commitment-preserving instruction.

## Key evidence

| Comparison | Result |
|---|---|
| 30 trajectories, neutral writer | 23/270 items wrong under three judges |
| 30 trajectories, status-aware writer | 1/270 items wrong under three judges |
| Direct vs chained (same final budget) | direct 27/30 correct vs chained 15–16/30 at D5 |
| Chained vs rewrite-matched (constant 220 intermediates) | 82 vs 80 both-correct: equal |
| Proposition omission | 0–10%, far below the status loss |
| Intentional D5, neutral (10 topics) | 9/10 status cues absent |
| Intentional D5, status-aware | 5/10 strict absent, but 10/10 carry a cue (5 strong + 5 weak) |
| Intentional D5, commitment-aware | 10/10 strong; judges agree 180/180, 40/40 committed |
| Human-annotated drift, neutral (two annotators) | 6.7–7.9% overall; 13.6–15.4% recursive D5; 16.7–17.9% rewrite D5 |
| Human-annotated drift, status-aware (one annotator) | 4.2% overall; 6.9% recursive D5; 10.0% rewrite D5 |

Three judges (qwen2.5:7b, gemma3:12b, mistral:7b) confirm the neutral errors:
all 23 qwen-gemma both-wrong items are also wrong under mistral. The
status-aware run has exactly one all-three-judge error, a real cue loss.

## Mechanism

The rewrite-matched control keeps the recursive chain and the number of writer
calls but holds intermediate budgets at 220. It produces the same degradation
as the shrinking-budget recursion, so the damage is **chained rewriting** —
re-editing the writer's own output — not the budget schedule.

## Mitigation curve (intentional D5)

- neutral: 1 strong cue, 1 weak, 8 none.
- status-aware: 5 strong, 5 weak, 0 none.
- commitment-aware: **10 strong, 0 weak, 0 none** (ceiling intervention; the
  prompt names the target cue and outputs are templated).

A realistic structured-sidecar mitigation is currently **blocked**: the 7B
writer cannot reliably emit prose plus a parseable status line in one call. It
needs a separate extractor or a stronger model.

## Validity and caveats

- Synthetic Chinese templates, one writer model.
- Human annotation: the neutral condition has two independent manual annotators
  (unsupported-label kappa 0.849); the status-aware condition uses one manual
  annotator because its B file was gold-derived and was withdrawn.
- Unconstrained chained outputs are ~25% shorter in tokens than direct outputs;
  a matched token-band control (14–18 tokens) is in progress.
- The neutral writer is not reliably deterministic at temperature 0: the same
  seed produced 63–96% identical memories across runs. Status-aware was
  byte-identical across two seeds (270/270). Report neutral magnitudes as
  ranges.
- Conditional is the least reliable dimension; its ontology and judge behavior
  remain a limitation.
- Direct and rewrite-matched controls still leave call count entangled with
  chaining.
- The commitment-aware result is a ceiling, not a deployment recommendation.

## Novelty

The belief-memory space is crowded (BELIEFMEM 2605.05583, MemCoRe 2602.07885,
PoS, MemTX, Agent-BRACE, TWIST). BELIEFMEM is a probabilistic belief-memory
architecture; MemCoRe is compression-hierarchy evidence retrieval. Neither
appears to measure status preservation under chained compression. The
defensible gap is the **controlled status-cue diagnostic** with a
rewrite-matched mechanism control and a mitigation curve — not a new memory
architecture.

## Next

1. Complete the token-band matched control and check whether the chaining
   effect survives at equal output length.
2. Obtain a second manual annotator for the status-aware condition.
3. Build a separate status-extractor sidecar prototype.
4. Test the intentional-specific loss on natural dialogue.
5. If confirmed, move to Stage B: downstream decision impact.

## Where things are

- Protocols: `docs/STATUS_DRIFT_PROTOCOL_V2_*.md`
- Results: `docs/research/2026-11-16-status-drift-*.md`
- Raw data: `results/status_drift_v2_pilot/`
- Metrics: `evaluation/status_cue_metrics.py`, `evaluation/status_sidecar.py`
- Paper backbone: `docs/research/2026-11-16-status-drift-paper-backbone.md`
- Everything is pushed to `research/status-drift-v2.4-revision`.
