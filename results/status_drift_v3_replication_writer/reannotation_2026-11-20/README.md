# n = 30 full re-annotation (2026-11-20)

Two independent human annotators and a human adjudicator re-annotate all
210 items (30 trajectories x 7 conditions). The previous labels stay in
`../annotation_v325/` and `../annotation_v325_remaining/`; nothing here
overwrites them.

## Files

- `annotator_RA.csv`, `annotator_RB.csv` — blind sheets with different row
  orders. Give one to each annotator. They contain no condition, no gold
  status, and no old labels.
- `annotation_items.csv` — the items in canonical id order (reference only;
  annotators should use their own sheet).
- `key.csv` — hidden mapping from item id to trajectory, condition, dimension,
  and gold status. Do not give this to annotators. It is curator-only and is
  intentionally not committed to the repository.
- `frozen_manifest.json` — SHA-256 of the inputs and sheets at freeze time.

## Independence rules

1. Each annotator fills only their own file and does not see the other file,
   the key, the old labels, or condition summaries.
2. Do not discuss items with the other annotator before both files are
   returned. Questions about the rubric go to the coordinator, not to each
   other.
3. Keep `annotator_id` as `RA` / `RB`; do not rename the files.
4. Fill every required field; `rationale` is required for any judgment other
   than `NO_DISTORTION`, and `confidence` is always required.
5. Return the CSVs unchanged in structure.

## Rubric

Use `docs/research/V3_ANNOTATION_GUIDELINES.md` (frozen hash in the manifest).
The primary judgment is one of `NO_DISTORTION`, `LEGITIMATE_UPDATE`,
`UNSUPPORTED_STATUS_DISTORTION`, `STATUS_OMISSION`, `PROPOSITION_LOSS`,
`AMBIGUOUS_UNASSESSABLE`.

## After both sheets return

```
python -m experiments.reannotation_round check --a annotator_RA.csv --b annotator_RB.csv
```

This writes `validation.json`, `agreement.json`, and
`adjudication_sheet.csv` containing only disputed items. A third human fills
the `adj_*` fields for the fields listed in `disputed_fields`, signs
`adjudicator`, and records a short `rule`. Then:

```
python -m experiments.reannotation_round merge --sheet adjudication_sheet.csv
python -m experiments.reannotation_round summarize
```

`merge` refuses to run while any disputed field is blank. It never resolves a
dispute automatically. `summarize` writes `condition_table.csv`,
`summary.json`, and `reliability.json` for the re-annotated n = 30 cohort.

## 中文要点

- 两名批注者各用一份表，行序不同；互不看对方的表、key、旧标签或条件汇总。
- key.csv 含条件与 gold，只能由协调者保管。
- 两人都交回后再由第三人人工裁决分歧；脚本不会自动替任何一方裁决。
- 旧标签原样保留，重批结果写入本目录。
