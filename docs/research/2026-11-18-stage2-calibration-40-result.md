# Stage 2 40-Item Calibration — Result (2026-11-18)

## Status: FAILED; this is a rule-adherence failure, not a new ontology failure

Both sheets are complete (40/40, no blanks). `gold_dimension` and `gold_status`
fail their kappa gates. The disagreements are not spread across the ontology:
they cluster on four v2.1 rules that annotator A did not apply, while annotator
B's labels follow the guide. Do not freeze Stage 2 and do not treat this run as
a reliability pass.

Provenance is not collected by maintainer decision; report the result as
**annotator-unspecified**.

## Run 2 update (new annotator A) — 2026-11-18

A was replaced and the blank A sheet was re-annotated. B is unchanged.

| Field | Raw | Kappa | Gate | Verdict |
|---|---:|---:|---|---|
| `gold_dimension` | 0.925 | 0.639 | raw ≥0.85, κ ≥0.70 | FAIL (κ) |
| `gold_status` | 0.900 | 0.875 | raw ≥0.85, κ ≥0.70 | **PASS** |
| `gold_strength` | 0.675 | 0.326 | descriptive | weak |
| `gold_confidence` | 0.725 | 0.362 | descriptive | prevalence |

The status ontology is now working: `gold_status` passes both thresholds. The
dimension gate fails by 0.061 on kappa with only three disagreements (raw
0.925):

1. `S2IE-003` — "I will provide some details about the app and it will be your
   job to write up a detailed statement..." A `intentional/INTENDING`; B `E0`.
   This is an instruction/roleplay to the assistant, not the speaker's own
   status. B is correct; A over-coded.
2. `S2IE-021` — "I think about my life too sometimes ... felt like writing a
   drama." A `intentional/INTERESTED`; B `E0`. Past/emotional musing is not a
   current action status. B is correct; A over-coded.
3. `S2IE-025` — "I think I've managed to make it work with dogs while still
   living in the city." A `intentional/COMPLETED`; B `epistemic/SUPPORTED`.
   This is a genuine boundary: a completed action vs a factual claim about a
   state. The guide does not decide it.

Two of three are A over-coding `E0`; one is a guide gap. The run is much closer
than run 1 and the status gate is met, but the pre-registered dimension gate is
not. Do not freeze yet.

Recommended next step: add v2.3 examples for the three boundaries (instructions
to the assistant, past/emotional musing, and "I've managed to X"), then either
re-annotate a new 40-item set or use a third-person adjudication of the three
items and report unadjudicated and adjudicated results side by side. Do not
lower the gate post hoc.

## Third-person adjudication (2026-11-18)

A third adjudicator (not A or B) resolved the three boundary items under v2.3
§8c-§8d:

| Item | Adjudicated | Rationale (short) |
|---|---|---|
| `S2IE-003` | `E0`, `N/A`, `N/A` | Instruction to the assistant, not the speaker's status. |
| `S2IE-021` | `E0`, `N/A`, `N/A` | Past/emotional musing, not a current/future action status. |
| `S2IE-025` | intentional `COMPLETED`, strong | The speaker's own completed action ("managed to make it work"). |

Unadjudicated vs adjudicated:

| Field | Unadj raw | Unadj κ | Adj raw | Adj κ |
|---|---:|---:|---:|---:|
| `gold_dimension` | 0.925 | 0.639 | **1.000** | **1.000** |
| `gold_status` | 0.900 | 0.875 | **0.975** | **0.969** |
| `gold_strength` | 0.675 | 0.326 | 0.725 | 0.472 |

Both gold gates pass after adjudication. Original A/B labels are preserved; the
adjudicated analysis is `analysis/agreement_adjudicated.json`. `gold_strength`
remains weak but is descriptive, not gated.

**Gold calibration is complete with third-person adjudication of three items.**
This is not a full Stage 2 freeze: LSF/SSF calibration on a generated-memory
sheet, the cue table, inclusion/exclusion rules, adjudication order, and the
analysis plan still need to be frozen together.

## Agreement

| Field | Raw | Kappa | Gate | Verdict |
|---|---:|---:|---|---|
| `gold_dimension` | 0.875 | 0.600 | raw ≥0.85, κ ≥0.70 | FAIL (κ) |
| `gold_status` | 0.675 | 0.607 | raw ≥0.85, κ ≥0.70 | FAIL |
| `gold_strength` | 0.825 | 0.560 | descriptive | weak |
| `gold_confidence` | 0.775 | 0.217 | descriptive | prevalence-driven |
| `target_proposition` | exact 0.000, Jaccard 0.017 | — | free text | expected |
| `evidence_quote` | exact 0.750, Jaccard 0.889 | — | descriptive | good |

No conditional items; `gold_condition_state` / `gold_action_state` are `N/A` and
were not gated.

## Disagreement decomposition (13 status disagreements)

| Family | Count | Items | Rule |
|---|---:|---|---|
| `E0` encoding | 2 | S2IE-003, S2IE-031 | A `NOT_EXPRESSED`; B `N/A` |
| Commitment inflation | 4 | S2IE-008, S2IE-011, S2IE-032, S2IE-034 | "I think I'll" / "I'm going to try" coded `COMMITTED`; should be `INTENDING` |
| Desire as intention | 3 | S2IE-006, S2IE-019, S2IE-028 | "I'd like to / I want to" coded `INTENDING`; should be `INTERESTED` |
| `EXECUTING` for resolve | 2 | S2IE-001, S2IE-039 | "I'm gonna keep / I'm going to keep" coded `EXECUTING`; should be `INTENDING` |
| `mixed` / `E0` boundary | 2 | S2IE-012, S2IE-021 | A used `mixed`/intentional; B used `E0` |

Ten of thirteen are direct v2.1 rule violations by A; B matches the guide. This
is a training/adherence problem. The two `mixed` cases expose a separate rule
gap: the sheet does not say how to select one target proposition when a
sentence contains a main action plus a secondary conditional or emotional
clause.

`gold_strength` disagreements are mostly A `moderate` vs B `weak` (7 items); the
strength anchors need worked examples.

## What not to conclude

- Do not conclude that the intentional ontology is unreliable. The guide was
  not applied consistently.
- Do not pool this set with v1 or with the 25-item check.
- Do not use these 40 items in confirmatory data.

## Next

1. Add worked examples to the guide (v2.2) for the five families above, plus a
   target-proposition selection rule: one item = one target proposition;
   `mixed` only when the same proposition has two status dimensions; secondary
   clauses go in `notes`.
2. Run a short training/adjudication pass (8-10 examples) with both annotators
   before touching a new 40-item set.
3. Re-annotate the same 40 items as a calibration round, or generate a new set
   if the guide wording changes materially. Either way, this run is not
   confirmatory.
4. Recompute the two gates. Only then consider the LSF/SSF memory sheet.

## Artifacts

- `results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/annotator_A.csv`
- `results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/annotator_B.csv`
- `results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/analysis/agreement.json`
- `experiments/analyze_stage2_calibration.py`
