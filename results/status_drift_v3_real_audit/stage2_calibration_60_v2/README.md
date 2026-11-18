# Stage 2 Calibration Set v2 (60 items) — Candidate, Conditional Underpowered

**Status: superseded (2026-11-18).** Decision C uses the 40-item
intentional/epistemic set in
`results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/`. Do not
annotate this v2 set; it is retained only as a record of the conditional
shortfall.

## Composition

- 60 items: 35 LoCoMo, 25 longmemeval.
- Heuristic dimensions: 41 intentional, 12 epistemic, 7 conditional.
- 10 boundary-flagged, 6 cue-mismatch.
- Proposed strata and flags are outside the repository in
  `G:/memory_failure_backup/stage2_calibration_v2_key_2026-11-18.csv`.
- Exact screening and v1-calibration items are excluded (110 keys); LoCoMo
  conversations are still reused because the public split has only 10.

## The conditional decision

| Option | What it means | Cost |
|---|---|---|
| A. Calibrate without a conditional gate | Gate `gold_dimension` and `gold_status` only; report conditional states descriptively (n=7). | 60 annotations; conditional is not a reliability claim. |
| B. Source more conditional dialogue | Find another conditional-rich corpus (or the full LoCoMo split) and regenerate. | Data work before annotation; preserves the conditional arm. |
| C. Split the calibration | 30-40 intentional/epistemic items now; a separate conditional set later. | Less annotation now; conditional remains open. |

Recommendation: **B** if the paper will claim conditional status fidelity on
real dialogue; **A** if conditional is explicitly secondary and the paper says
it is descriptive only. Do not pad conditional to 15 by relabeling
non-conditional items.

## Files

- `annotator_A.csv`, `annotator_B.csv` — blank sheets; do not fill yet.
- `analysis/selection_summary.json` — exact composition and caveat.
- Key outside repo (do not open before finishing):
  `G:/memory_failure_backup/stage2_calibration_v2_key_2026-11-18.csv`.

## Hashes

- Generator: `52bb9697c9fa2eb7d691cb3fbd4e6eec857fe3067a3e0ea67cbdde534371ecb3`
- Sheets: `9d24d8223ed314ca215284d8400b991eed10e953be8be801277db84163b5953a`
- Key: `19b4523bfb546b9fd36eb9ac61e589d221b14858d62597b29075be331aeeef1c`

If the set is regenerated, these hashes change and the previous sheets are
void.
