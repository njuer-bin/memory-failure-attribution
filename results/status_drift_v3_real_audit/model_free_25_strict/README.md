# Strict Model-Free Re-Annotation (25 items)

This is the clean instrument for the anchoring check. It contains only the
target sentence, its context, and the provided later-mention text. It has no
dataset or source identifiers, no cue-derived columns, and no proposed labels.

## Who should fill it

A third human is preferred. YTB may fill it only after a washout; the earlier
exposure to the cue columns cannot be undone, so record that limitation in
provenance and do not call the result fully naive.

## Rules

- Fill `annotator.csv` only.
- Do not open `model_free_25/`, `screening_A.csv`, `screening_B.csv`,
  `diagnostic_read.csv`, `screening_50.csv`, the mapping keys, or the raw source
  corpora (`longmemeval_*.json`, `locomo_refined_dataset/`).
- Use only `target_sentence`, `context`, and `later_mention` from this sheet.
- If `later_mention` is empty, set `update_present=unknown`. Do not search the
  full source; the old and new labels must use the same evidence source.
- No model assistance on any cell. If a model helps, record it in provenance
  and the sheet becomes model-assisted, not independent.
- No blanks; use the allowed values.

## Fields and decision order

Use the table and nine-step order in
`results/status_drift_v3_real_audit/model_free_25/README.md`. In brief:

| Field | Values |
|---|---|
| `status_bearing` | yes / ambiguous / no |
| `dimension` | epistemic / intentional / conditional / mixed / none |
| `proposition_clear` | yes / no |
| `evidence_sufficient` | yes / partial / no |
| `lexical_cue_present` | yes / no (target sentence only) |
| `lexical_labelable` | yes / no (cue must match the semantic status type) |
| `semantic_labelable` | yes / no |
| `update_present` | yes / no / unknown |
| `difficulty_1_3` | 1 / 2 / 3 |
| `notes` | one line: P, assigned status, boundary reason |

## Files

- `annotator.csv` — fill this.
- `provenance_template.json` — copy to `provenance.json` and fill.
- Mapping from `MFS-###` to the earlier item ids is outside the repository:
  `G:/memory_failure_backup/stage2_model_free_strict_key_2026-11-18.csv`. Do
  not open it before finishing.

Time: about 40-60 minutes.
