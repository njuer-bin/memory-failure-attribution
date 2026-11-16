# Status Drift Pilot — Protocol v2.8 (Structured Status Sidecar)

**Status:** pre-registered; no v2.8 outputs exist yet.
**Branch:** `research/status-drift-v2-pilot`
**Scope:** a practical mitigation, not a prompt that names the target cue.

## 1. Why

The commitment-aware prompt (v2.7) eliminates intentional cue loss but is a
ceiling intervention: it names the target cue and produces templated prose. A
realistic memory system should preserve status **structurally**, without relying
on every prose compression to keep the right adjective.

## 2. New writer mode: `sidecar`

The writer still compresses prose, but appends a structured status line:

    [状态: 确定性=已确认|可能|不适用；意图=已决定|考虑中|不适用；条件=已满足|未满足|不适用]

The sidecar is generated from the input, not from the gold label.

## 3. Design

- 10 topics, 3 dimensions × 2 variants = 60 trajectories, design v3.
- Writer style: `sidecar`, direct and recursive conditions.
- Recursive chain must carry the sidecar forward; the writer may update it only
  when the input explicitly changes the status.

## 4. Metrics

- Sidecar presence and parseability.
- Sidecar status correctness against gold, per dimension and depth.
- Prose cue state (`evaluation.status_cue_metrics`) as a secondary measure.
- Deterministic proposition omission.

## 5. Pre-registered predictions

- **P14:** sidecar presence ≥ 90% at every depth (including recursive D5).
- **P15:** sidecar status correctness ≥ 90% at every depth.
- **P16:** proposition omission < 10%.
- **P17:** prose cue loss may persist; the sidecar should carry the status even
  when prose weakens. This decouples status preservation from prose phrasing.

## 6. Gates

Interpret only if:

- sidecar presence/parseability ≥ 90% in all conditions;
- sidecar status correctness ≥ 90%;
- proposition omission < 10%;
- no single topic accounts for more than half of sidecar failures.

If the sidecar does not survive recursive compression, report that structural
preservation also fails and do not claim a practical mitigation.

## 7. Integrity

- Existing runs are unchanged; v2.8 uses a new writer mode and output dir.
- The sidecar is generated from the input, never from gold.
- Any sidecar parsing failures are reported, not silently dropped.

## 8. Pilot attempt 1 (invalid, discarded)

The first sidecar execution produced **only** the status line and dropped the
prose (`direct_d1: [状态: 确定性=可能；...]`), and some fields were malformed
(`确定性=未满足`, `条件=已满足|未满足|不适用`). The run was stopped after 4
trajectories; its output is discarded and never used.

The prompt was revised to require a two-line output (prose first, sidecar
second) with a worked example. This is a prompt-bug fix made before any v2.8
result was observed; it is not a result-driven change.

## 9. Attempt 2 (invalid, discarded) — v2.8 blocked

The revised two-line prompt still fails with qwen2.5:7b:

- `direct_d1` output only the sidecar line, duplicated, with no prose;
- `recursive_d3` produced prose but copied the option strings verbatim
  (`确定性=已确认|可能`).

The writer cannot reliably emit prose + a structured sidecar in one call at
this model scale. **Status: blocked.** A reliable version needs either a
separate status-extractor call (prose and sidecar generated independently) or a
stronger writer model.

No v2.8 result is reported. The v2.7 commitment-aware ceiling remains the
mitigation evidence; the sidecar is recorded as an open engineering direction,
not a completed experiment.

