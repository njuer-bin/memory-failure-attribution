# Model-Free Re-Annotation Check (25 items) — 2026-11-18

## Status: the check is model-assisted, not model-free

`results/status_drift_v3_real_audit/model_free_25/provenance_YTB.json` records
that the 25 items were re-annotated with model assistance (WorkBuddy,
MiniMax-M3.1-Flash), that the annotator was not blind to the cue-derived
columns carried by the sheet (`dimensions`, `primary_dimension`,
`matched_markers`, `potential_update`, `later_mention`), and that the raw
source dialogues were read to recover later mentions because the earlier
`update_evidence` field was truncated.

This does **not** satisfy the planned model-free anchoring check. It is a
model-assisted sensitivity analysis, and it must not be described as an
unaided human re-annotation or used to claim unaided two-human reliability.

## What was compared

The new labels were joined to the old `screening_B` and `screening_A` labels by
the item id key outside the repository. Raw agreement and Cohen's kappa:

| Field | vs old B raw | vs old B kappa | vs old A raw | vs old A kappa |
|---|---:|---:|---:|---:|
| `status_bearing` | 0.960 | 0.648 | 1.000 | 1.000 |
| `dimension` | 0.880 | 0.762 | 0.840 | 0.688 |
| `proposition_clear` | 0.880 | 0.336 | 0.920 | 0.468 |
| `evidence_sufficient` | 0.560 | 0.042 | 0.600 | 0.132 |
| `lexical_cue_present` | 1.000 | n/a | 1.000 | n/a |
| `lexical_labelable` | 0.840 | 0.662 | 0.840 | 0.565 |
| `semantic_labelable` | 0.880 | 0.336 | 0.920 | 0.468 |
| `update_present` | 0.200 | 0.040 | 0.280 | 0.102 |
| `difficulty_1_3` | 0.560 | 0.337 | 0.600 | 0.398 |

## Why `update_present` is not comparable

- Old B: `unknown` 24, `yes` 1.
- Old A: `unknown` 19, `yes` 6.
- New model-assisted: `no` 13, `yes` 8, `unknown` 4.

The new annotator searched the raw source dialogues for later mentions, while
the old sheet often had no later mention and was labeled `unknown`. The two
label sets therefore answer different questions: "is a later mention available
in the sheet?" versus "can one be found in the full source?". The 0.20/0.28 raw
agreement is a methodological difference, not an estimate of anchoring.

`evidence_sufficient` is also weak (raw 0.56/0.60, kappa 0.04/0.13), consistent
with the v2 guide's sharper yes/partial/no distinction.

## Consequence

The anchoring question remains open. To answer it, the re-annotation must be:

1. unaided (no model first pass and no model help on cells);
2. blind to the cue-derived columns — the strict sheet should carry only
   `item_id`, `target_sentence`, `context`, and, if needed, `later_mention`;
3. restricted to the sheet's later-mention text, or with a pre-declared rule
   that the full source may be consulted. Do not change the evidence source
   between the old and new label sets.

Until then, the 50-item screen remains a mixed-provenance rubric diagnostic,
and the 60-item calibration is the primary reliability gate for Stage 2.

## Artifacts

- `results/status_drift_v3_real_audit/model_free_25/annotator_YTB.csv`
- `results/status_drift_v3_real_audit/model_free_25/provenance_YTB.json`
- Key outside repo:
  `G:/memory_failure_backup/stage2_model_free_key_2026-11-18.csv`

## Correction instrument

`results/status_drift_v3_real_audit/model_free_25_strict/` contains a clean
25-item sheet with only `item_id`, `target_sentence`, `context`, and
`later_mention`, and blank ratings. It removes the cue-derived columns and the
dataset/source identifiers, and its instructions forbid opening the old labels,
the key, or the raw corpus. Its key is outside the repository at
`G:/memory_failure_backup/stage2_model_free_strict_key_2026-11-18.csv`.

A third human is the preferred annotator. YTB may use it after a washout, but
the earlier exposure cannot be undone; record that in provenance and do not
call the result fully naive.

