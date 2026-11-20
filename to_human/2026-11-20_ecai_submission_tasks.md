# Outstanding human-only tasks — ECAI 2027 (2026-11-20)

The ECAI 7+1-page port is built (`paper/submission_ecai/`), and the figures and
supplementary archive are resynced to include the glm-5.3-flash v3.1 matrix.
Everything below needs a person; none blocks the current build, but the first
two should be resolved or disclosed before submission (~April 2027).

## 1. Validate the 16 new authorized controls (highest priority)

Unchanged from 2026-11-19. Scenarios `MON/HEA/AUT/COM-11..14` in
`datasets/p4_2_scenarios/p4_2_scenarios.yaml`. Score realism, status clarity,
rule clarity, distortion plausibility, stake severity (1–5), and
`only_status_differs` with `experiments/check_p4_2_validation.py`; also review
the 54-row `request_check.csv`. Acceptance: pooled realism ≥ 3.5,
only-status-differs yes-both ≥ 0.90; exclude and recompute any failure.

Until done, the ECAI paper keeps: "the 16 new controls are mechanically
checked but not two-human-validated."

## 2. Independent second rater for the reason coding

Sheet: `results/status_drift_v3_p4_2_v3_v31/analysis/reason_sheet_blind.csv`
(39 rows). Report raw agreement and kappa against the analyst codes. If no
rater is available, keep "analyst, post hoc, gold-unblinded."

## 3. Annotate the remaining 18 writer-replication trajectories

Directory: `results/status_drift_v3_replication_writer/annotation_v325_remaining/`
(126 items, ids `REPR-0085`–`REPR-0210`). Give `annotator_A.csv` and
`annotator_B.csv` to two people without `key.csv`; no model-drafted labels.
Then run `experiments.check_v3_annotations`, adjudicate, and merge with the
n = 12 cohort. Report n = 12 (pre-registered) and n = 30 (sensitivity)
separately. The ECAI paper currently reports n = 12 only.

## 4. Swap in the official ECAI 2027 class when released

`paper/submission_ecai/ecai.cls` is a local stand-in reproducing the ECAI
geometry. When the official kit appears: replace `ecai.cls`/`.bst`, recompile
`main.tex` and `appendix.tex`, and re-check the page count (the official class
may use 10 pt and grow the body) and the PDF metadata. Only the front matter
(`\title`, `\author`, abstract) should need touching.

## 5. Final read-through against the frozen state

After (1)–(3), update `paper/V3_NUMBERS.md` and the ECAI main text so the
disclosures match the final state: validated controls, n = 30 writer
replication, and (if run) a second reason coder. Do not claim these before
they are done.
