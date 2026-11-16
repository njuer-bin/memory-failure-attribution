# V3 P1b — Broadened Path-Replicate Result (2026-11-16)

**Protocol:** `docs/research/V3_P1B_PROTOCOL.md`
**Runner:** `experiments/v3_path_pilot.py --design heterogeneous`
**Run:** neutral writer, qwen2.5:7b, 12 trajectories (3 dimensions × 2 topics ×
stable/update), 5 paths + direct, final budget 100 characters.
**Output:** `results/status_drift_v2_pilot/v3_path_pilot_p1b/`
**Status:** completed; 12/12, 0 errors.

## 1. Paths

| Path | Schedule | Source access | Prompt | Temperature |
|---|---|---|---|---|
| S1 | 220→180→140→120→100 | prior memory | neutral | 0 |
| S2 | 220→160→150→120→100 | prior memory | neutral | 0 |
| PEEK | 220→180→140→120→100 | prior memory + original dialogue | neutral | 0 |
| PARA | 220→180→140→120→100 | prior memory | neutral paraphrase | 0 |
| TEMP | 220→180→140→120→100 | prior memory | neutral | 0.7 |
| Direct | one call to 100 | original dialogue | neutral | 0 |

## 2. Headline result

| Metric | Value |
|---|---:|
| Mean pairwise path disagreement | **0.439** |
| Trajectories with any path divergence | **10 / 12** |
| Mean direct-vs-paths disagreement | 0.494 |

This is a large increase over P1a's schedule-only result (0.056; 1/12), so the
broadened path space exposes genuine path dependence.

## 3. Pairwise path rates

| Pair | n | disagree | rate |
|---|---:|---:|---:|
| S1–S2 (schedule only) | 11 | 1 | **0.091** |
| S1–PEEK | 11 | 6 | 0.545 |
| S1–PARA | 11 | 4 | 0.364 |
| S1–TEMP | 11 | 3 | 0.273 |
| S2–PEEK | 12 | 6 | 0.500 |
| S2–PARA | 12 | 3 | 0.250 |
| S2–TEMP | 11 | 4 | 0.364 |
| PEEK–PARA | 12 | 7 | 0.583 |
| PEEK–TEMP | 11 | 9 | **0.818** |
| PARA–TEMP | 11 | 5 | 0.455 |

**Intermediate-budget schedule alone is nearly null (9.1%).** The divergence is
driven by source access (PEEK), prompt paraphrase (PARA), and decoding
temperature (TEMP).

## 4. Per-path status fidelity (gold match, topic-mentioned)

| Dimension | S1 | S2 | PEEK | PARA | TEMP | Direct |
|---|---:|---:|---:|---:|---:|---:|
| epistemic | 1/4 | 2/4 | 3/4 | 1/4 | 0/4 | 4/4 |
| intentional | 1/4 | 1/4 | 3/4 | 1/4 | 0/4 | 3/4 |
| conditional | 2/3 | 2/4 | 4/4 | 2/4 | 1/3 | 4/4 |

- **PEEK is the best chained path**: access to the original dialogue preserves
  the status cue.
- **TEMP (temperature 0.7) is the worst**: sampling increases status loss.
- **PARA is also lossy**: a paraphrased neutral instruction is not neutral.
- **Direct remains best**; schedule-only chaining sits between direct and the
  lossy paths.
- Two conditional paths were topic-lost and excluded from the divergence
  denominators; they are reported in the summary.

## 5. Interpretation

- **Path dependence is real, but its mechanism is information access and
  generation variability, not budget schedule.** Schedule-only paths nearly
  converge (9.1%); source access, prompt wording, and temperature create
  divergence.
- **The V3 claim should be kept but scoped**: path-dependent state distortion
  is supported for heterogeneous transformation paths. The primary contrasts
  should be PEEK vs memory-only and deterministic vs sampled, with schedule-only
  as a near-null control.
- **Direct is still the best strategy** in this pilot, and PEEK is the best
  chained path.
- This reframes V3's mechanism section: "history" matters mainly through what
  information each stage can see and how the writer is sampled, not merely
  through the budget curve.

## 6. Gate verdict

- P1b-3 threshold: within-condition divergence ≥2/12? **PASS (10/12).**
- Path-dependent claim: **supported for heterogeneous paths**, with a specific
  mechanism.
- Schedule-only path dependence: **not supported** (9.1%).
- No human labels; this is a deterministic-cue pilot.

## 7. Caveats

- n=12; 2 topics; one writer model.
- TEMP has one sampled path per trajectory, not repeated samples.
- Deterministic status-cue metric, not human adjudication.
- Two conditional paths were topic-lost and excluded from divergence.
- The conditional normalized-state mapping was corrected during analysis; the
  divergence summary is unaffected (one-to-one relabeling), and per-path gold
  match was recomputed from stored memories.

## 8. Next

1. Increase n (e.g., 40 trajectories) and add repeated TEMP samples per
   trajectory.
2. Make PEEK vs memory-only the primary path contrast; keep schedule-only as a
   near-null control.
3. Add blind human labels for a stratified subset.
4. Freeze the heterogeneous path definitions for the V3 confirmatory phase.
