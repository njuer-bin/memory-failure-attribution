# Real-Data Arm Scoping Decision (2026-11-18)

**Decision C.** The real-dialogue arm is scoped to a **feasibility audit plus a
gold-coding calibration**. The LSF/SSF instrument is reported as a failed
calibration and future work. There is no confirmatory real-dialogue generation
in the current paper. The paper's primary claims remain the synthetic V3 line
(P2/P3/P5) and the P4.2 high-stakes behavioral line.

## What passed

- Stage 1 feasibility audit: 2,135 candidate spans; intentional is the viable
  real-dialogue dimension; epistemic is thin; conditional is scarce.
- 40-item gold-coding calibration (decision C): after a third-person
  adjudication of three boundary items, `gold_dimension` 1.000 / κ 1.000 and
  `gold_status` 0.975 / κ 0.969. The calibration set is 14 intentional + 1
  epistemic eligible items; epistemic remains descriptive only.
- The 25-item "model-free" check was **model-assisted** and is not an unaided
  human anchoring estimate; it is retained as a sensitivity analysis only.

## What failed

- LSF/SSF calibration run 1: LSF 0.733 / κ 0.581; SSF 0.578 / κ 0.432;
  proposition identity 0.756 / κ 0.507. Cause: the generator stripped the
  target-turn marker and the guide lacked a cue lexicon/SSF tree.
- LSF/SSF calibration run 2 (target-focus generator, v2.4): LSF 0.800 / κ 0.689;
  SSF 0.756 / κ 0.625; proposition identity 0.800 / κ 0.607. LSF and SSF are
  near their gates; proposition identity is the blocker because memories
  replace the target speech act ("write" → "ask for advice"). LSF/SSF
  disagreements are mostly outside identity and turn on cue paraphrase and the
  distortion boundary.
- The LSF/SSF instrument is therefore not reliable enough to support a
  confirmatory real-dialogue fidelity claim.

## Paper claims

**Can claim:**

- Chained rewriting causes status omission in the synthetic V3 line, with the
  mechanism isolated from budget and call count, and the P5 mitigation ranking.
- P4.2: distortion is the robust downstream harm; omission's behavioral profile
  is task-dependent and can produce over-action when the agent fills the
  missing status; the curated bank passes two-human validation.
- Real-dialogue feasibility: intentional status is findable and gold-codeable;
  the 40-item gold calibration passes with adjudication; epistemic/conditional
  are too thin for confirmatory work.

**Cannot claim:**

- Real-dialogue LSF/SSF reliability or a natural-dialogue replication of the
  omission effect.
- Conditional status reliability.
- That the 25-item model-assisted check is an unaided human anchoring result.
- That the real-dialogue arm is confirmatory. It is an appendix/feasibility
  contribution.

## Conditions to reopen

The real-data arm can be reopened only with:

1. a v2.5 predicate-preservation rule plus LSF/SSF examples and a training pass;
2. a fresh calibration set (or a new annotation round) that passes the LSF/SSF
   gates; and
3. a model-free anchoring check, if an unaided human is available.

Until then, report LSF/SSF as a failed calibration and a measurement lesson, not
as a negative finding about memory systems.

## Artifacts

- `docs/research/2026-11-18-stage2-calibration-40-result.md`
- `docs/research/2026-11-18-stage2-lsf-ssf-result.md`
- `docs/research/2026-11-18-stage2-lsf-ssf-run2-result.md`
- `docs/research/V3_REAL_STAGE2_PREFREEZE.md`
- `results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/`
- `results/status_drift_v3_real_audit/stage2_lsf_ssf/`
