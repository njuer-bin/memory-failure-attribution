# Writer-replication annotation — remaining 18 trajectories

Blind annotation sheets for the 18 writer-replication trajectories that were
generated but not yet annotated. The first 12 trajectories are complete in
`../annotation_v325/` and remain the pre-registered cohort.

## Files

- `annotator_A.csv`, `annotator_B.csv` — one row per item, label fields blank.
  Give one file to each annotator. No condition, gold status, or model name
  appears in either file.
- `annotation_items.csv` — the same items without the label columns, for
  reading or spot checks.
- `key.csv` — item → trajectory, condition, dimension, gold status. **Gold
  key; do not give it to annotators.**
- `prevalence.json` — aggregate counts only.

126 items = 18 trajectories × 7 conditions (`direct`, `recursive`,
`rewrite_matched`, `repeated_direct`, `neutral_source`, `status_aware`,
`status_aware_source`). Item ids continue the existing series
(`REPR-0085`–`REPR-0210`).

## Annotation status (final, 2026-11-20)

A morning `annotator_B.csv` was found to be gold-derived and quarantined under
`_invalid/` (see `_invalid/README.md`). The maintainer re-annotated the sheet
in the afternoon; the replacement passes schema validation (126/126, 0 missing,
0 invalid) and is accepted. `annotator_A.csv` and the re-annotated
`annotator_B.csv` are both complete.

`adjudication.csv` is complete (126/126). The 50 A/B disagreements were
adjudicated by `claude-sonnet-4.6 (model third-reviewer simulation; NOT human)`
and all resolved to A's labels; the other 76 rows are marked
`auto (A=B, no adjudication)`. This is rule-consistent model adjudication, not
independent human adjudication.

Merged with `../annotation_v325/adjudication.csv`, the full cohort is
210 items = 30 trajectories x 7 conditions. It is analysed separately in
`../analysis_v325_full/` (`condition_table.csv`, `summary.json`): report n = 12
as the pre-registered cohort and n = 30 as a post-hoc sensitivity analysis, and
do not pool either with the primary qwen writer result.

## Protocol

Follow `docs/research/V3_ANNOTATION_GUIDELINES.md` (v3.2.5). Work from
`memory_text` and `dialogue` only; do not inspect `key.csv` and do not use a
model to draft labels. Label these fields:

| Field | Allowed values |
|---|---|
| `proposition_identity` | `PRESERVED`, `PARTIAL`, `LOST`, `AMBIGUOUS` |
| `primary_dimension` | `EPISTEMIC`, `INTENTIONAL`, `CONDITIONAL`, `ACTION`, `CANNOT_DETERMINE` |
| `status_expressed` | `YES`, `NO`, `UNCLEAR` |
| `expressed_status` | the value set for the chosen dimension, or `NOT_EXPRESSED` / `UNRECOVERABLE` |
| `action_status` | conditional items only |
| `evidence_support` | `SUPPORTED_BY_DIALOGUE`, `CONTRADICTED_BY_LATER_DIALOGUE`, `NOT_SUPPORTED`, `AMBIGUOUS`, `NOT_ASSESSABLE` |
| `primary_judgment` | `NO_DISTORTION`, `LEGITIMATE_UPDATE`, `UNSUPPORTED_STATUS_DISTORTION`, `STATUS_OMISSION`, `PROPOSITION_LOSS`, `AMBIGUOUS_UNASSESSABLE` |
| `confidence` | `HIGH`, `MEDIUM`, `LOW` |

`rationale`, `subtype`, and `turn_references` are optional but useful for
adjudication.

## After both annotators finish

```bash
G:/aconda/python.exe -m experiments.check_v3_annotations \
    --a results/status_drift_v3_replication_writer/annotation_v325_remaining/annotator_A.csv \
    --b results/status_drift_v3_replication_writer/annotation_v325_remaining/annotator_B.csv
```

Then adjudicate disagreements and merge with `../annotation_v325/adjudication.csv`.
Report two cohorts separately:

- **n = 12** — the pre-registered cohort already in the paper;
- **n = 30** — the full cohort, reported as a post-hoc sensitivity analysis.

Do not describe the n = 30 cohort as pre-registered, and do not pool it with
the primary qwen writer result.
