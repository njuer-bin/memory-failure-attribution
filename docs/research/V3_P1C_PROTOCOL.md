# V3 P1c — Scaled Heterogeneous Path Pilot

**Status:** pre-registered; no P1c outputs exist yet.
**Parents:** `V3_P1B_PROTOCOL.md`, `2026-11-16-v3-path-pilot-p1b.md`.

## 1. Why

P1b (n=12) found real path divergence but only one TEMP sample per trajectory
and limited topic coverage. P1c scales the heterogeneous design and adds a
second independent temperature sample to quantify sampling variance.

## 2. Trajectories

- 7 topics × 3 dimensions × stable/update = **42 trajectories**.
- Same source generation and final budget (100 characters) as P1b.

## 3. Paths (predeclared)

| Path | Schedule | Source access | Prompt | Temperature | Seed |
|---|---|---|---|---|---|
| S1 | 220→180→140→120→100 | prior memory | neutral | 0 | 42 |
| S2 | 220→160→150→120→100 | prior memory | neutral | 0 | 42 |
| PEEK | 220→180→140→120→100 | prior memory + original dialogue | neutral | 0 | 42 |
| PARA | 220→180→140→120→100 | prior memory | neutral paraphrase | 0 | 42 |
| TEMP1 | 220→180→140→120→100 | prior memory | neutral | 0.7 | 42 |
| TEMP2 | 220→180→140→120→100 | prior memory | neutral | 0.7 | 43 |

Direct (one call to 100, neutral, temperature 0) is a reference.

## 4. Metrics

- Pairwise path divergence for all 15 path pairs.
- Any-divergence count per trajectory.
- Per-path gold match (topic-mentioned only).
- Direct-vs-paths divergence.
- Topic-lost paths.
- TEMP1–TEMP2 divergence as a direct estimate of sampling variance.

## 5. Pre-registered predictions

- **P1c-1:** PEEK remains the best chained path on gold match.
- **P1c-2:** TEMP1/TEMP2 remain the worst, and TEMP1–TEMP2 divergence is
  non-trivial (sampling alone changes status).
- **P1c-3:** schedule-only S1–S2 remains near-null.
- **P1c-4:** the P1b ordering (source access > prompt paraphrase > schedule
  variation) replicates at n=42.

## 6. Gates

- 42/42 trajectories complete; no unreported errors.
- Report all path pairs; do not select paths after observing outputs.
- Report topic-lost counts separately.
- Deterministic cue metric only; no human-label claim.

## 7. Integrity

- Path specifications and seeds are fixed before the run.
- Same source and final budget across paths.
- Raw outputs retained; no post-hoc path selection.
- This is still a pilot; no confirmatory claim.
