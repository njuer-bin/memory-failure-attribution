# Outstanding human-only tasks — ECAI 2027 (2026-11-20)

The ECAI 7+1-page port is built (`paper/submission_ecai/`), and the figures and
supplementary archive are resynced to include the glm-5.3-flash v3.1 matrix.
Everything below needs a person. Items 1–3 were completed on 2026-11-20;
items 4–5 remain before submission (~April 2027).

## 1. Validate the 16 new authorized controls — DONE (2026-11-20)

WMY (A) and YTB (B) completed `validation_A_16.csv` / `validation_B_16.csv`
independently. Pooled over 16: realism 4.97, status clarity 5.00, rule clarity
4.97, distortion plausibility 4.31, stake severity 2.88;
`only_status_differs` yes-both 0.9375 (kappa 1.000); `HEA-11` excluded, 15
survivors. Acceptance (realism ≥ 3.5, yes-both ≥ 0.90) passes.
`request_check.csv` is 54/54 `manipulation_ok=yes` with notes. Provenance is in
`validation_16_provenance_A.json` / `_B.json`.

## 2. Independent second rater for the reason coding — DONE (2026-11-20)

Sheet: `results/status_drift_v3_p4_2_v3_v31/analysis/reason_sheet_blind.csv`
(39 rows) is complete (D1 34, O2 5). Agreement with `analyst_code` is raw 1.000,
kappa 1.000; `unauthorized_reason_codes.csv` now carries `rater_b_code` /
`rater_b_note`. Record the rater's identity and independence in
`unauthorized_reason_codes_summary.json` before citing this as human.

## 3. Annotate the remaining 18 writer-replication trajectories — DONE (2026-11-20)

Directory: `results/status_drift_v3_replication_writer/annotation_v325_remaining/`
(126 items, ids `REPR-0085`–`REPR-0210`). `annotator_A.csv` and
`annotator_B.csv` are complete (126/126, schema-clean). The 50 A/B
disagreements were adjudicated by
`claude-sonnet-4.6 (model third-reviewer simulation; NOT human)`; all 50
resolved to A. Report n = 12 (pre-registered) and n = 30 (post-hoc
sensitivity, model-adjudicated) separately.

## 4. Swap in the official ECAI 2027 class when released

`paper/submission_ecai/ecai.cls` is a local stand-in reproducing the ECAI
geometry. When the official kit appears: replace `ecai.cls`/`.bst`, recompile
`main.tex` and `appendix.tex`, and re-check the page count (the official class
may use 10 pt and grow the body) and the PDF metadata. Only the front matter
(`\title`, `\author`, abstract) should need touching.

## 5. Final read-through against the frozen state

Items (1)–(3) are complete. Refresh `paper/V3_NUMBERS.md` and the ECAI main
text so the disclosures match the final state: validated controls, n = 30
post-hoc sensitivity, and the second reason rater. Rebuild the PDF after any
wording change.
