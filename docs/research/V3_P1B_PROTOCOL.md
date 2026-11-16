# V3 P1b — Broadened Path-Replicate Pilot

**Status:** pre-registered; no P1b outputs exist yet.
**Parent:** `docs/research/V3_RESEARCH_ROADMAP.md` §7 P1a.

## 1. Why

P1a varied only intermediate character budgets and found within-condition path
divergence in 1/12 trajectories. That path space may be too narrow. P1b
broadens the perturbation types while holding the source trajectory and final
budget fixed.

## 2. Paths (predeclared)

All paths end at the same final budget (100 characters) and use the same neutral
writer model (`qwen2.5:7b`). They differ only in the transformation path:

1. **S1 — schedule A**: memory-only recursive, `220→180→140→120→100`,
   neutral prompt, temperature 0.
2. **S2 — schedule C**: memory-only recursive, `220→160→150→120→100`,
   neutral prompt, temperature 0.
3. **PEEK — source access**: recursive `220→180→140→120→100`, but each stage
   sees the prior memory **and** the original dialogue; neutral prompt.
4. **PARA — prompt paraphrase**: memory-only recursive `220→180→140→120→100`
   with a paraphrased neutral compression instruction.
5. **TEMP — decoding sample**: memory-only recursive `220→180→140→120→100`
   with temperature 0.7.

Direct (one compression to 100, neutral, temperature 0) is a reference, not a
path.

## 3. Design

- 12 trajectories (3 dimensions × 2 topics × stable/update), same as P1a.
- 5 paths + direct per trajectory.
- Measure final state with the deterministic status-cue metric.
- Exclude topic-lost paths from divergence and report them separately.

## 4. Pre-registered predictions

- **P1b-1:** source-peek should preserve status more often than memory-only
  paths (less information loss).
- **P1b-2:** temperature sampling may increase path divergence relative to
  deterministic schedules.
- **P1b-3:** if within-condition divergence remains below 2/12 trajectories even
  in this broader space, the broad "path-dependent" claim should be reframed as
  a transformation-history effect with path dependence as a rare secondary
  result.

## 5. Gates

- 12/12 trajectories complete; no unreported errors.
- Report pairwise divergence per path pair, any-divergence count, and topic-lost
  counts.
- Do not select paths or trajectories after observing outputs.

## 6. Integrity

- Path specifications are fixed before the run.
- Same source and final budget across paths; only the listed perturbation
  differs.
- Raw outputs and token/call logs are retained.
- This is a pilot; no human labels and no confirmatory claim.
