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

## Re-annotation status (2026-11-20)

A completed `annotator_B.csv` was found to be gold-derived: it matched an
untracked pattern-labeled JSON, used 44 out-of-schema `action_status` values,
and mapped every expressed status deterministically from `key.csv`. It has been
quarantined under `_invalid/` (see `_invalid/README.md`). `annotator_B.csv` is
blank again and must be filled by a genuine independent human annotator who has
not seen the key or `annotator_A.csv`. `annotator_A.csv` is valid
single-annotator data; the n = 30 cohort remains blocked until B is redone.

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
