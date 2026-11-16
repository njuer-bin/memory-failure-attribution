# Status Drift Pilot — Progress Report (2026-11-16, overnight run)

Branch: `research/status-drift-v2-pilot`
Remote: https://github.com/njuer-bin/memory-failure-attribution/tree/research/status-drift-v2-pilot

## The question

Does repeated compression of conversational memory change the **epistemic /
intentional / conditional status** attached to a proposition, even when the
proposition itself survives?

## Main result

**Yes, but the mechanism is chained rewriting, not budget shrinkage — and a
status-aware writer prompt largely prevents it.**

| Contrast | Result |
|---|---|
| Neutral writer, 30 trajectories | 23 both-judge-wrong items |
| Status-aware writer, 30 trajectories | 1 both-judge-wrong item (a real cue loss) |
| Chained vs direct, neutral | direct D5 27/30 correct vs chained 15–16/30 |
| Chained vs direct, status-aware | direct 116/120 vs chained 107–108/120 |
| Rewrite-matched vs recursive | essentially equal in both writers |
| Proposition omission | 0–2/30 everywhere |

The rewrite-matched control (same number of chained calls, intermediate
budgets held at 220) is **equal to** the shrinking-budget recursion. So the
damage comes from re-editing the writer's own output, not from the budget
schedule.

## Judge-independent confirmation

`evaluation/status_cue_metrics.py` checks whether a memory still carries the
gold status cue. Updated cases, D5:

| Writer | direct MATCH / ABSENT | chained MATCH / ABSENT |
|---|---|---|
| neutral | 7–8 / 1 | 2–4 / 6–8 |
| status-aware | 10 / 0 | 4–5 / 3–5 |

Same-seed (43) neutral vs status-aware: chained cue ABSENT drops from 5–6/10 to
2–3/10. The mitigation is not a seed or session artifact.

## Why this is not just a judge artifact

- v1.0 judge was invalid; v1.1 fixed most label semantics.
- Three judges (qwen, gemma, mistral) on the status-aware run:
  - pairwise agreement 0.919–0.952;
  - majority accuracy 260/270;
  - **exactly one item is wrong under all three judges**, and it is a real
    writer cue loss (`epistemic_02_U`, D5).
- 10 majority-wrong items split into 3 writer omissions and 7 shared judge
  biases. Majority voting does not remove judge bias.

## Reproducibility caveat

The neutral writer is **not reliably deterministic at temperature 0**. Three
runs: seed 43 vs 44 were 96% identical, but seed 42 differed by ~37%. The
status-aware writer was byte-identical across seeds 42/43 (270/270). The seed
option is not a variance control; freer prompts hit near-tie flips.

Report neutral magnitudes as ranges; the status-aware mitigation is stable.

## Where things stand

- Protocols v2.1 → v2.6 are committed and pushed.
- Raw records, judge outputs, summaries, and adjudication notes are on GitHub
  (2.4 MB, synthetic data only).
- 42 tests pass.
- Novelty: the belief-memory space is crowded (BELIEFMEM, MemTX, PoS, Agent-
  BRACE, MemCoRe). The defensible gap is **controlled measurement of status
  cue loss under chained compression**, not a new memory architecture.

## Overnight results added after the first draft

- **Third judges:** neutral 23 errors are all-three-judge confirmed (mistral
  also wrong on all 23); status-aware has exactly 1 all-three-wrong item.
- **10-topic, 60-trajectory cue study:** the chaining loss is
  intentional-specific. Neutral intentional recursive D5 ABSENT 9/10 vs
  epistemic 2/10; status-aware 5/10 vs 2/10; direct 0/10 in both. No single
  topic dominates.
- **Commitment-aware writer:** 10/10 strong commitment cues at every depth
  (recursive D5 included), vs neutral 1 strong/8 none and status-aware
  5 strong/5 weak. This is a ceiling intervention, not a deployment default.
- **Sidecar mitigation:** pre-registered (v2.8) and implemented; a parseable
  `[状态: ...]` line is appended to each memory. Run pending.
- **Human review sample:** `to_human/adjudication_sample.csv` (18 items,
  stratified across writer drift, judge errors, and controls).

## Currently running

- gemma judging of the 20 commitment-aware trajectories. qwen is done: all 20
  updated D5 items are judged COMMITTED, and the stable CONSIDERING items are
  also correct.
- Next: the 60-trajectory sidecar run, then a human-adjudication pass.

## File map

- Plans/protocols: `docs/STATUS_DRIFT_*.md`
- Results: `docs/research/2026-11-16-status-drift-*.md`
- Raw data: `results/status_drift_v2_pilot/`
- Metrics: `evaluation/status_cue_metrics.py`
- Runner: `experiments/status_drift_recursive_pilot.py`
- Judge: `experiments/status_drift_judge_calibration.py`
- Variance: `experiments/status_drift_variance.py`
