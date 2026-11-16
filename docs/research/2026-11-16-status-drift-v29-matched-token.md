# Matched Token-Band Result — v2.9 (2026-11-16)

**Protocols:** v2.9 + v2.9.1
**Run:** neutral writer, 30 trajectories, design v3, rewrite-matched,
D5 token target 17 (tolerance 1, up to 4 attempts).
**Output:** `results/status_drift_v2_pilot/v29_matched_neutral/`
**Status:** completed; 30/30, 0 errors.

## 1. Achieved D5 writer tokens

| Condition | mean | min | max |
|---|---:|---:|---:|
| direct | 18.1 | 11 | 22 |
| recursive | 16.7 | 10 | 21 |
| rewrite-matched | 16.3 | 10 | 22 |

The ranges overlap heavily but are not identical; the mean difference is 1.4–1.8
tokens. This is a **token-band** control, not exact token matching.

## 2. Matched-band cue result

Band = **[14, 18] tokens**, updated cases only, topic-mentioned items only
(proposition-lost items excluded and counted separately):

| Condition | n | cue ABSENT | rate | topic-lost excluded |
|---|---:|---:|---:|---:|
| direct | 7 | 1 | **14.3%** | 1 |
| recursive | 6 | 5 | **83.3%** | 1 |
| rewrite-matched | 8 | 6 | **75.0%** | 1 |

Outside the band:

| Condition | n | cue ABSENT | rate |
|---|---:|---:|---:|
| direct | 2 | 0 | 0.0% |
| recursive | 2 | 1 | 50.0% |
| rewrite-matched | 1 | 1 | 100.0% |

## 3. Proposition omission and the pre-registered gate

- Overall topic-not-mentioned rate at D5: direct 3.3%, rewrite-matched 3.3%,
  **recursive 13.3% (4/30)**.
- The v2.9.1 gate required proposition omission < 10%. **Recursive D5 fails
  that gate.** The matched-band comparison above excludes the topic-lost items
  and still shows direct 1/7 vs recursive 5/6 and rewrite 6/8. The status effect
  is therefore not driven by proposition omission, but the overall run is
  **conditionally interpretable**, not a clean matched-budget pass.

## 4. Provisional judge metrics

| Condition | judge accuracy at D5 |
|---|---:|
| direct | 0.633 |
| recursive | 0.467 |
| rewrite-matched | 0.400 |

These point in the same direction but are dominated by the uncalibrated judge
and remain secondary.

## 5. Interpretation

- **The chaining effect survives length matching in this pilot.** Among
  topic-mentioned memories of 14–18 tokens, direct compression loses the status
  cue in 1/7 cases; recursive and rewrite-matched lose it in 5/6 and 6/8.
- **The earlier effect is not solely a shorter-output artifact.** Token ranges
  overlap and the omission-adjusted comparison preserves the contrast.
- **The result is conditional, not confirmatory.** The band is post-hoc and
  small (6–8 items per condition), and the recursive-D5 omission gate (13.3%)
  is above the pre-registered 10% threshold.
- Do not claim exact token matching; report the achieved distributions.

## 6. Gate verdict

- 30/30 complete, no unreported errors: PASS.
- Band has ≥5 items per condition: PASS (7/6/8).
- Token ranges overlap: PASS in range, though means differ by ~1.5 tokens.
- Deterministic proposition omission < 10%: **FAIL at recursive D5 (13.3%)**.

**Verdict: directional matched-band evidence; not a clean confirmatory result.**

## 7. Next

1. Increase n or tighten the band to raise per-condition counts.
2. Run the same matched-band control with the status-aware writer.
3. Report the omission-adjusted band comparison alongside the raw gate.
4. Obtain a second manual annotator for the status-aware condition.
