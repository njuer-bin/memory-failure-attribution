# Status Drift Pilot — Protocol v2.9.1 (Token-Band Amendment)

**Status:** pre-registered amendment before the full matched run.
**Parent:** `docs/STATUS_DRIFT_PROTOCOL_V2_9.md`

## 1. What the feasibility check showed

A 3-trajectory check (no cue outcomes inspected) found that exact token
matching is not achievable with character-budget iteration at this model scale:

- target 21: chained outputs capped near 17; direct reached 22.
- target 17: direct 16–22, recursive 12–17, rewrite 9–17.

The model does not expand or contract linearly with the character budget, so a
single exact target is not realistic.

## 2. Amendment

- Lower the D5 target from 21 to **17** (achievable for chained outputs; direct
  can be compressed toward it).
- Use **4 attempts** and tolerance **1**.
- Do **not** claim exact token matching. Report achieved distributions.
- Primary matched comparison: a **token band** of final D5 writer outputs in
  **[14, 18] tokens**, pooled across conditions. Compare deterministic cue
  ABSENT within this band.

## 3. Design

- Neutral writer, 30 trajectories, design v3, rewrite-matched.
- D5 token targeting as above; D1–D3 unchanged.
- Full annotation set is not required for this control; the deterministic cue
  metric is the primary measure.

## 4. Pre-registered reading

- If the cue-loss difference persists within the [14,18] token band, the
  chaining effect is not solely a length artifact.
- If the difference disappears in the band, the earlier effect is partly a
  shorter-output effect.
- If fewer than 5 items per condition fall in the band, report the matched
  comparison as underpowered and do not use it as evidence either way.

## 5. Integrity

- The target change is based on output-length feasibility only; no cue outcome
  was inspected before this amendment.
- Raw token counts and per-record achieved tokens are stored.
- This is a pilot control, not a confirmatory matched-budget benchmark.
