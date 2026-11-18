# Stage 2 60-Item Gold Calibration — Result (2026-11-18)

## Status: FAILED; Stage 2 is not frozen

Both annotator sheets are complete (60/60, no blanks). The `gold_dimension`
gate passes; `gold_status` and the conditional-state gates fail. The failure is
systematic and traceable to guide rules, not sampling noise. Do not freeze the
guide and do not run confirmatory generation.

Provenance: by maintainer decision (2026-11-18), annotator provenance is not
collected. Report this calibration as **annotator-unspecified**; do not claim
an unaided two-human provenance record.

## Agreement

| Field | Raw | Kappa | Gate | Verdict |
|---|---:|---:|---|---|
| `gold_dimension` | 0.917 | 0.809 | raw ≥0.85, κ ≥0.70 | PASS |
| `gold_status` | 0.633 | 0.584 | raw ≥0.85, κ ≥0.70 | FAIL |
| `gold_condition_state` | 0.500 | 0.000 | raw ≥0.85, κ ≥0.70 | FAIL (n=4) |
| `gold_action_state` | 0.500 | 0.333 | raw ≥0.85, κ ≥0.70 | FAIL (n=4) |
| `gold_strength` | 0.750 | 0.570 | descriptive | weak |
| `gold_confidence` | 0.850 | 0.224 | descriptive | prevalence-driven |
| `target_proposition` | exact 0.000, Jaccard 0.019 | — | free text | expected |
| `evidence_quote` | exact 0.783, Jaccard 0.907 | — | descriptive | good |

Sensitivity analyses:

- Normalizing A's `NOT_EXPRESSED` to `N/A` on the seven both-`E0` items raises
  `gold_status` to raw 0.750 / κ 0.708.
- Restricting to the 48 dimension-agreed non-`E0` items gives the same
  `gold_status` raw 0.750 / κ 0.708.
- The conditional arm has only four items (A) and three (B); it cannot support
  a reliability claim.

## Diagnosis: three guide defects and one convention defect

1. **`E0` status convention (7 items).** On both-`E0` items, A wrote
   `NOT_EXPRESSED`; B wrote `N/A`. This is a field-convention mismatch, not a
   substantive disagreement. The guide must require `gold_status=N/A`,
   condition/action `N/A`, and strength `N/A` whenever `gold_dimension=E0`.
2. **Desire vs intention (10 items, 9 disagreements).** Items phrased
   "I want to X" / "I'd like to X": A used `INTENDING` (7), `CONSIDERING` (1),
   `EXECUTING` (1); B used `INTERESTED` (9). The guide does not say that a bare
   desire is `INTERESTED` and not `INTENDING`. This single rule explains most of
   the residual status disagreement.
3. **Progressive vs resolve (6 `EXECUTING` items, 2 disagreements).**
   "I'm going to keep working hard" (A `EXECUTING`, B `INTENDING`) and "I want to
   keep working in engineering" (A `EXECUTING`, B `INTERESTED`). `EXECUTING`
   should require an action already under way ("I'm trying to", "I've been
   reading"), not a resolve or a desire.
4. **Conditional boundary (4 items).** A/B agree on 2/4. `S2C-020`
   ("Let me know if you need someone to talk to or if I can do anything to
   help") is an offer to the interlocutor; A called it `conditional`, B `E0`.
   The guide must state that conditional status is about the speaker's own
   action contingent on a factual prerequisite, not an offer or generic
   conditional about the world.

Minor: "I'm wondering if I could link this story" (A epistemic `UNKNOWN`, B
intentional `CONSIDERING`) shows the same own-action vs factual-uncertainty
boundary is underspecified. `gold_strength` has no anchors and A/B differ on
weak vs moderate; `gold_confidence` is almost all `high`, so kappa is
prevalence-sensitive.

## Decision

- Stage 2 remains **not frozen**; no confirmatory generation.
- Revise the guide with explicit rules (v2.1) for `E0` encoding, desire vs
  intention, `EXECUTING`, conditional offers, and own-action wondering.
- Re-calibrate on a **new** item set; do not reuse these 60 items in
  confirmatory data. The current conditional pool is thin; a new set may have
  fewer than 15 conditional items, and that shortfall must be reported rather
  than padded with mislabeled examples.
- Record A/B provenance before any future calibration is treated as complete.

## Artifacts

- `results/status_drift_v3_real_audit/stage2_calibration_60/annotator_A.csv`
- `results/status_drift_v3_real_audit/stage2_calibration_60/annotator_B.csv`
- `results/status_drift_v3_real_audit/stage2_calibration_60/analysis/agreement.json`
- `experiments/analyze_stage2_calibration.py`
- `experiments/check_stage2_annotations.py`
