# Quarantined annotator-B artifact (2026-11-20)

This directory holds the `annotator_B.csv` produced on 2026-11-20 for the
126-item writer-replication cohort. It is **not** an independent blind
annotation and must not be used for agreement, kappa, or the n = 30 cohort.

## Evidence

- It matches `_annotations.patterned_2026-11-20.json` on all eight label fields
  for all 126 items; that JSON carries `pattern` labels A–E.
- 44 `action_status` values are outside the schema (`ACTION_NOT_STARTED`,
  `ACTION_STARTED`, and one free-text `NOT_APPLICABLE for CONDITIONAL item`).
- `primary_dimension` matches the gold key on only 80/126 items; 38/42
  EPISTEMIC items are coded INTENTIONAL.
- For all 80 items where `status_expressed = YES`, `expressed_status` is a
  deterministic projection of `key.csv` gold status (`CERTAIN` → `COMMITTED`,
  `POSSIBLE` → `CONSIDERING`). A blind annotator cannot know the gold key; this
  is the signature of a gold-derived file.

This repeats the failure documented in
`docs/research/2026-11-16-status-drift-annotation-integrity-correction.md`.

## Files

- `annotator_B.gold_derived_2026-11-20.csv`
  — sha256 `6ae4129660d884a3cbbf334d3ad0b46925101c68423970faf35cae9f750c7f1a`
- `_annotations.patterned_2026-11-20.json`
  — sha256 `231baac87e7faabd2c9c92127d66b00315fb748b6915b84b051b29ef36af4c7d`

Both are local audit artifacts and are ignored by git. Do not copy them into
any analysis or manuscript artifact.

## What remains valid

`../annotator_A.csv` is valid single-annotator data: it matches the gold
dimension 126/126, uses the v3.2.5 vocabulary (`ESTABLISHED` for gold
`CERTAIN`), and contains genuine disagreements with gold. It can support a
single-annotator sensitivity analysis only, not two-annotator reliability.

## Re-annotation procedure

1. Give `../annotator_B.csv` (now blank) to a second person who has not seen
   `key.csv`, `annotator_A.csv`, or this audit note.
2. Work only from `memory_text` and `dialogue`, following
   `docs/research/V3_ANNOTATION_GUIDELINES.md` v3.2.5.
3. Do not use a model to draft labels.
4. After completion run:
   `G:/aconda/python.exe -m experiments.check_v3_annotations --a .../annotator_A.csv --b .../annotator_B.csv`
5. Report n = 12 as pre-registered and n = 30 as sensitivity, separately.
