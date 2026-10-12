# Human Annotation Re-audit Decisions — 2026-10-12

## Status
The uploaded 25-case annotation CSV is treated as the researcher's Human Ground Truth. All five automatic-vs-human disagreement cases have now been explicitly re-audited by the researcher.

## Final re-audit decisions

| Question | Previous auto label | Final human label | Interpretation |
|---|---|---|---|
| q0037 | E0_EVIDENCE_INSUFFICIENCY | F1_FORMATION | Evidence is sufficient; the lifecycle failure is formation. |
| q0020 | F1_FORMATION | EVAL | Evidence/timestamp provenance is uncertain or contradictory, so the case should not be forced into a lifecycle failure label. |
| q0032 | NONE | E0_EVIDENCE_INSUFFICIENCY | The retrieved memories do not establish the queried national-park vs theme-park preference. |
| q0047 | F1_FORMATION | EVAL | Temporal evidence conflicts with the supplied benchmark timestamp context; keep the case as evaluator-uncertain rather than forcing F1. |
| q0006 | F1_FORMATION | F1_FORMATION | The researcher confirms the evidence as sufficient and the lifecycle failure as formation. |

## Human Ground Truth is now frozen for these five disagreements

The researcher explicitly confirmed:

- q0037 → `F1_FORMATION`
- q0020 → `EVAL`
- q0032 → `E0_EVIDENCE_INSUFFICIENCY`
- q0047 → `EVAL`
- q0006 → `F1_FORMATION`

These labels supersede the previous automatic labels for Human-vs-Auto agreement analysis.

## Next step
Recompute the complete 25-case Human-vs-Auto agreement statistics, including:

- overall final-label agreement
- confusion matrix
- Cohen's kappa
- evidence-sufficiency agreement
- per-class precision / recall / F1
- disagreement case list

No metric should be treated as final until it is recomputed from the completed annotation CSV plus these explicit re-audit decisions.
