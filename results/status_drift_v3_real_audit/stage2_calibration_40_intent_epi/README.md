# Stage 2 Calibration Set — Intentional + Epistemic (40 items)

**Status: calibration run failed on rule adherence (2026-11-18).** Do not treat
the current sheets as a pass. Read `V3_REAL_STAGE2_DRAFT.md` v2.2 §8b-§8c and
run `STAGE2_V22_TRAINING.md` before re-annotating. The results and diagnosis
are in `2026-11-18-stage2-calibration-40-result.md`.

Run 1 A labels are preserved as `annotator_A_run1_2026-11-18.csv`; the active
`annotator_A.csv` is reset to blank for a new annotator. B's labels are
unchanged. The run-1 analysis is preserved as
`analysis/agreement_run1_2026-11-18.json`.

Decision C: calibrate the intentional/epistemic arm now; conditional is a
separate future set. This set contains **no conditional items**; do not gate
condition/action states on it.

## Composition

- 40 items: 25 LoCoMo, 15 longmemeval (14 from the 44-57-session
  `longmemeval_s` instances; the rest from the oracle arm).
- Heuristic dimensions: 29 intentional, 11 epistemic.
- 7 boundary-flagged, 4 cue-mismatch ("I think I'll", "I'll definitely").
- Screening (50) and v1-calibration (60) items are excluded by dialogue key.
  The v2 candidate is superseded; its unannotated items may overlap this set.
- LoCoMo conversations are reused because the public split has only 10 and all
  were screened. Items are distinct, but the set is **not**
  conversation-disjoint; report this limitation.

Proposed strata and flags are outside the repository in
`G:/memory_failure_backup/stage2_calibration_40_intent_epi_key_2026-11-18.csv`.
Do not open it before finishing.

## Files

- `annotator_A.csv`, `annotator_B.csv` — blank sheets; one per annotator.
- `analysis/selection_summary.json` — composition.
- `provenance_template.json` — retained but optional.

Two independent humans are required. No model first draft and no model help on
cells. **Provenance is not collected by maintainer decision (2026-11-18).**
Report the reliability as annotator-unspecified; do not claim an unaided
two-human provenance record.

## Fields

| Field | Values |
|---|---|
| `target_proposition` | one English sentence: "The speaker [status] [action/object]" |
| `gold_dimension` | epistemic / intentional / mixed / E0 |
| `gold_status` | epistemic: UNKNOWN / POSSIBLE / PROBABLE / SUPPORTED / ESTABLISHED / REJECTED; intentional: NOT_EXPRESSED / CONSIDERING / INTERESTED / INTENDING / COMMITTED / EXECUTING / COMPLETED / CANCELLED / NOT_INTENDED |
| `gold_condition_state` | `N/A` for every row (no conditional items) |
| `gold_action_state` | `N/A` for every row |
| `gold_strength` | weak / moderate / strong / N/A |
| `gold_confidence` | high / medium / low |
| `evidence_quote` | minimal supporting quote |
| `update_history` | ordered earlier statuses, or empty |
| `notes` | boundary reason, or empty |

Use the v2.1 rules in `docs/research/V3_REAL_STAGE2_DRAFT.md` §3-§8b. The
calibration-critical rules:

- `E0` → all status fields `N/A`; never `NOT_EXPRESSED`.
- "I want to / I'd like to X" → `INTERESTED`; not `INTENDING`/`CONSIDERING`.
- "I plan to / I'm going to X" → `INTENDING`; `COMMITTED` needs an explicit
  decision/booking/payment cue.
- `EXECUTING` only for action already under way; "I'm going to keep X-ing" is
  `INTENDING`, "I want to keep X-ing" is `INTERESTED`.
- "I'm wondering if I could X" about the speaker's own action → intentional
  `CONSIDERING`, not epistemic.
- A desire with a concrete plan is `INTENDING`; quote the plan.

## Gates

| Field | Raw | Kappa |
|---|---:|---:|
| `gold_dimension` | ≥0.85 | ≥0.70 |
| `gold_status` | ≥0.85 | ≥0.70 |

`gold_strength` and `gold_confidence` are descriptive. If the gates fail,
revise the guide and use a new item set; do not reuse these 40 in confirmatory
data.

## After completion

```
G:/aconda/python.exe experiments/check_stage2_annotations.py \
  --dir results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi \
  --expected 40

G:/aconda/python.exe -m experiments.analyze_stage2_calibration \
  --a results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/annotator_A.csv \
  --b results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/annotator_B.csv \
  --out results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/analysis/agreement.json
```

Do not open the other annotator's file, the key, the screening labels, or the
raw source corpora.

## Hashes

- Generator: `3f85655a8fa728bd5b571c0e852eda8bb7b6475ca97cfb9ee4ee04dd535bc6a6`
- Sheets: `43b18cd896296cdd1d7b6392e5c748255e5bcfd812b91b24e7ce9c5c3795e2f1`
- Key: `1ced0d028e56abc921cfd2034a44352eae7460694b676a4a92907fb70c3ab457`

If regenerated, these hashes change and the previous sheets are void.
