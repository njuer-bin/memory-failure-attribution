# Human Annotation Re-audit Decisions — 2026-10-12

## Status
The uploaded 25-case annotation CSV is treated as the researcher's Human Ground Truth. The five automatic-vs-human disagreement cases are being re-audited individually before final agreement metrics are frozen.

## Confirmed re-audit decisions

| Question | Previous auto label | Human re-audit decision | Interpretation |
|---|---|---|---|
| q0037 | E0_EVIDENCE_INSUFFICIENCY | F1_FORMATION | Evidence is sufficient; the lifecycle failure is formation. |
| q0020 | F1_FORMATION | EVAL | Evidence/timestamp provenance is uncertain or contradictory, so the case should not be forced into a lifecycle failure label. |
| q0032 | NONE | E0_EVIDENCE_INSUFFICIENCY | The retrieved memories do not establish the queried national-park vs theme-park preference. |

## Remaining disagreements pending re-audit

- q0047: previous auto `F1_FORMATION`, human annotation currently `EVAL`.
- q0006: previous auto `F1_FORMATION`, human annotation currently `EVAL`.

These two cases should remain unresolved until the researcher explicitly confirms the final labels.

## Important methodological note
The re-audit decisions above are researcher-confirmed labels and therefore supersede the earlier automatic labels for the purpose of Human-vs-Auto agreement analysis. Final agreement statistics, confusion matrix, Cohen's kappa, and per-class metrics should be recomputed only after all five disagreement cases have been finalized.
