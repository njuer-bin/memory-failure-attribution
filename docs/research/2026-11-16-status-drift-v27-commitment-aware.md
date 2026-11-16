# Commitment-Aware Writer — v2.7 Result (2026-11-16)

**Protocol:** `docs/STATUS_DRIFT_PROTOCOL_V2_7.md`
**Run:** commitment-aware writer, intentional dimension only, 10 topics × S/U =
20 trajectories, design v3, `--skip-judge`.
**Status:** completed; gates passed.

## 1. Strict cue result

| Condition | MATCH | MIXED | OPPOSITE | ABSENT |
|---|---:|---:|---:|---:|
| direct D1–D5 | 10 / 10 / 10 / 10 | 0 | 0 | 0 |
| recursive D1–D5 | 10 / 10 / 10 / 10 | 0 | 0 | 0 |

**Zero strict cue absence at every depth**, including recursive D5.

## 2. Strong / weak / none (intentional)

| Depth | strong | weak | none |
|---|---:|---:|---:|
| direct D2 / D3 / D5 | 10 / 10 / 10 | 0 | 0 |
| recursive D2 / D3 / D5 | 10 / 10 / 10 | 0 | 0 |

Every memory uses an explicit commitment form such as
`已经决定购买电脑，会按计划推进。` even after the full recursive chain.

## 3. Comparison at intentional D5

| Writer | strong (`决定`) | weak (`推进计划`/`按计划`/`已开始`) | none |
|---|---:|---:|---:|
| neutral | 1 | 1 | 8 |
| status-aware | 5 | 5 | 0 |
| commitment-aware | **10** | **0** | **0** |

## 4. Predictions

- **P11 supported:** strict D5 ABSENT = 0 < 5/10.
- **P12 supported:** strong retention 10/10 ≥ 8/10.
- **P13 supported:** proposition omission 0–1/20 (<10%).

## 5. Gate verdict

- 20 trajectories complete and parse: PASS.
- Proposition omission < 10%: PASS (0–1/20).
- No topic domination: trivially PASS (zero strict absence).
- Direct-vs-recursive pattern: no loss to compare; the intervention removes it.

## 6. Interpretation

- The intentional cue loss is **prompt-controllable**: an explicit
  commitment-preservation instruction eliminates weakening in this setup.
- This is a **ceiling intervention**, not a practical default. The prompt names
  the target cue, and the writer converges to a templated
  `已经决定…会按计划执行` form. It shows the phenomenon is not an inherent
  limit of the model, but it does not show that a realistic memory system would
  preserve commitment without such explicit instruction.
- The practical implication is a **post-hoc status checker/repair step**: detect
  weakened commitment cues and restore them, rather than relying on every
  writer prompt to be commitment-aware.

## 7. Caveats

- Intentional dimension only; no judge in this run.
- One writer model, synthetic templates, n=20.
- The templated outputs may inflate cue-match rates; manual reading confirms the
  cue is present but the phrasing is repetitive.
- No test of whether the stronger prompt harms proposition fidelity; omission is
  0–1/20, so it does not in this sample.

## 8. Next

1. Judge the 20 commitment-aware trajectories with qwen/gemma to confirm the
   labels, not just the cue words.
2. Test a post-hoc repair prompt as a more realistic mitigation.
3. Keep the strong/weak distinction in the paper narrative.
