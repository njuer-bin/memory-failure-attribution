# Commitment-Aware Writer — Judge Confirmation (2026-11-16)

**Run:** `v27_commitment_aware_intentional`, 20 intentional trajectories,
180 condition-items.
**Judges:** qwen2.5:7b and gemma3:12b.
**Status:** completed; label confirmation passed.

## 1. Agreement

- Inter-judge agreement: **180/180 = 1.000**.
- Both-judges-wrong: **0/180**.

## 2. Updated-case labels (D3/D5)

There are 40 updated D3/D5 items (20 trajectories × 2 depths).

- Both judges return COMMITTED for **40/40**.
- No item is judged CONSIDERING or another label.

So the strong commitment cues are not only present as words; both judges read
the memories as committed.

## 3. Stable-case labels

The stable (`_S`) intentional trajectories are correctly judged CONSIDERING by
both judges; the commitment-aware prompt did not flip stable cases to
COMMITTED.

## 4. Deterministic checks

- Proposition omission: 1/20 at recursive D3/D5 (5%), below the 10% gate.
- Strict status-cue MATCH: 10/10 at every depth (v2.7 result).
- Strong commitment cue: 10/10 at every depth.

## 5. Interpretation

The commitment-aware intervention survives both measurement layers:

1. deterministic cue presence (10/10 strong), and
2. independent judge labels (40/40 COMMITTED, 180/180 agreement).

This confirms the v2.7 ceiling result. It remains a ceiling intervention, not a
practical default: the prompt names the target cue and the outputs are
templated. The realistic mitigation test is the structured sidecar (v2.8).

## 6. Caveats

- Intentional dimension only; synthetic templates; two local judges.
- No human label pass for this run.
- The near-perfect agreement may partly reflect templated outputs.
