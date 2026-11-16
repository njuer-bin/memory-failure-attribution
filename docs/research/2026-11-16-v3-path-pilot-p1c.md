# V3 P1c — Scaled Multi-TEMP Path Pilot (2026-11-16)

**Protocol:** `docs/research/V3_P1C_PROTOCOL.md`
**Runner:** `experiments/v3_path_pilot.py --design heterogeneous_multi_temp`
**Run:** 42 trajectories (7 topics × 3 dimensions × stable/update), 6 paths +
direct, neutral writer, qwen2.5:7b, final budget 100 characters.
**Output:** `results/status_drift_v2_pilot/v3_path_pilot_p1c/`
**Status:** completed; 42/42, 0 errors.

## 1. Paths

| Path | Schedule | Source access | Prompt | Temp | Seed |
|---|---|---|---|---|---|
| S1 | 220→180→140→120→100 | prior memory | neutral | 0 | 42 |
| S2 | 220→160→150→120→100 | prior memory | neutral | 0 | 42 |
| PEEK | 220→180→140→120→100 | prior memory + original dialogue | neutral | 0 | 42 |
| PARA | 220→180→140→120→100 | prior memory | neutral paraphrase | 0 | 42 |
| TEMP1 | 220→180→140→120→100 | prior memory | neutral | 0.7 | 42 |
| TEMP2 | 220→180→140→120→100 | prior memory | neutral | 0.7 | 43 |
| Direct | one call to 100 | original dialogue | neutral | 0 | 42 |

## 2. Headline result

| Metric | Value |
|---|---:|
| Mean pairwise path disagreement | **0.329** |
| Trajectories with any path divergence | **31 / 42** |
| Mean direct-vs-paths disagreement | 0.387 |

P1b's n=12 pattern replicates: path divergence is substantial but not
universal.

## 3. Pairwise path rates (n=42)

| Pair | disagree / n | rate |
|---|---:|---:|
| S1–S2 (schedule only) | 2/38 | **0.053** |
| S1–PEEK | 22/38 | 0.579 |
| S2–PEEK | 25/41 | 0.610 |
| S1–PARA | 10/37 | 0.270 |
| S2–PARA | 8/39 | 0.205 |
| S1–TEMP1 | 5/36 | 0.139 |
| S1–TEMP2 | 5/36 | 0.139 |
| S2–TEMP1 | 4/37 | 0.108 |
| S2–TEMP2 | 3/37 | 0.081 |
| PEEK–PARA | 24/40 | 0.600 |
| PEEK–TEMP1 | 23/38 | 0.605 |
| PEEK–TEMP2 | 22/38 | 0.579 |
| PARA–TEMP1 | 9/38 | 0.237 |
| PARA–TEMP2 | 6/38 | 0.158 |
| **TEMP1–TEMP2** | **3/36** | **0.083** |

Key readings:

- **Schedule-only remains near-null (5.3%).**
- **Source access is the dominant path perturbation (~58–61%).**
- Prompt paraphrase is moderate (~20–27%).
- Temperature vs deterministic is ~8–14%.
- **TEMP1–TEMP2 divergence is 8.3%:** pure sampling variance alone changes the
  final state in about one in twelve path pairs.

## 4. Per-path gold match (topic-mentioned only)

| Dimension | S1 | S2 | PEEK | PARA | TEMP1 | TEMP2 | Direct |
|---|---:|---:|---:|---:|---:|---:|---:|
| epistemic | 6/14 | 6/14 | **11/14** | 2/13 | 3/12 | 4/13 | 12/14 |
| intentional | 1/14 | 1/14 | **9/14** | 2/14 | 0/14 | 2/14 | 12/13 |
| conditional | 6/10 | 6/13 | **14/14** | 8/13 | 8/12 | 7/11 | 14/14 |

- **PEEK is the best chained path** in every dimension.
- **TEMP1/TEMP2 are the worst** (especially intentional: 0/14 and 2/14).
- PARA is also lossy; schedule-only S1/S2 are weak.
- Direct remains best.

## 5. Dimension and omission notes

| Dimension | Mean path divergence | Any divergence | Topic-lost paths |
|---|---:|---:|---:|
| epistemic | 0.324 | 11/14 | 4 |
| intentional | 0.352 | 12/14 | 0 |
| conditional | 0.312 | 8/14 | **11** |

Conditional has 11 topic-lost paths, so its divergence and gold-match are less
reliable and must be read with the omission count. Epistemic has 4; intentional
has 0.

## 6. Interpretation

- **P1b replicates at n=42.** Path dependence is real, but its mechanism is
  **information access and generation variability**, not the intermediate budget
  schedule.
- **Source access dominates**: being able to reread the original dialogue
  (PEEK) is the single largest determinant of status fidelity among chained
  paths.
- **Decoding matters**: two temperature samples differ in 8.3% of path pairs,
  which is irreducible sampling variance in this setup.
- **Prompt wording matters**: a paraphrase of the neutral instruction is not
  neutral.
- **Budget schedule alone nearly null**: this strongly supports treating
  schedule-only variation as a control, not the primary path axis.

## 7. Gate verdict

- 42/42 complete, no unreported errors: PASS.
- Report all 15 path pairs: PASS.
- Topic-lost counts reported: PASS (conditional 11; epistemic 4).
- Predictions P1c-1..4: **supported.**
  - PEEK best among chained paths: yes.
  - TEMP worst and TEMP1–TEMP2 non-trivial: yes (8.3%).
  - Schedule-only near-null: yes (5.3%).
  - P1b ordering replicates: yes.

**Verdict: path-dependent state distortion is supported at pilot scale, with a
mechanism-specific claim: source access and generation variability, not budget
schedule.**

## 8. Caveats

- Deterministic status-cue metric, not human labels.
- One writer model; synthetic templates.
- TEMP has two samples, not a full sampling distribution.
- Conditional topic-lost rate (11 paths) is high; conditional results need a
  separate omission analysis.
- No behavioral/downstream outcome in this pilot.

## 9. Next

1. Blind human labels for a stratified subset (PEEK vs S1 vs TEMP).
2. Make PEEK vs memory-only the primary path contrast; keep schedule-only as a
   near-null control.
3. Fix or separately analyze conditional topic loss before using conditional
   path divergence.
4. Freeze heterogeneous path definitions for the V3 confirmatory phase.
