# Supplementary Material

Status fidelity under chained memory rewriting: omission, distortion, and
downstream behavior.

This package is anonymized for double-blind review. It contains the scenario
banks, prompt sources, frozen analysis scripts, aggregate label tables, and the
publication figures behind the paper. Raw dialogue corpora and per-item model
outputs are not redistributed here; the aggregate tables reproduce every number
in the main text.

## Contents

- `scenarios/` — the high-stakes authorization bank (`p4_2_scenarios.yaml`),
  the expansion controls (`p4_2_controls_v2.yaml`), the request-form overlay
  (`p4_2_v3_requests.yaml`), and the analyst-translated Chinese parallel slice
  (`p4_2_zh_parallel.yaml`).
- `prompts/` — the exact system template, evidentiary clause, decision-label
  blocks, and request forms used for Study 2b.
- `code/` — the frozen generators, runners, and analyzers. Scripts read the
  scenario banks and emit the aggregate tables in `results/`, so the numbers
  are never retyped.
- `results/` — aggregate condition tables, paired contrasts, interaction
  estimates, reason-code counts, bank validation summary, and the length
  check. File names map to the paper's studies (Study 1 = P3; Study 2a = P4;
  Study 2b = P4.2 v3.1; Study 3 = P5). The `study2b_glm_*` files are the
  third agent model (`glm-5.3-flash`) on the same v3.1 design; its per-record
  outputs and run configuration are withheld because the configuration
  carries a gateway session identifier. The aggregate tables reproduce every
  cross-model number in the paper.
- `annotation/` — the blind annotation guideline and the bank-validation
  rubric.
- `figures/` — Figures 1–6 as vector PDFs.

## Reproducing the figures

    python -m experiments.make_paper_figures

The script reads only the frozen CSV/JSON aggregate tables; no number is typed
into the plotting code.

## Disclosures

- The synthetic annotation is reported as **annotator-unspecified**: human
  label provenance was not recorded. All reported kappa values are
  post-adjudication, and adjudication was model-assisted.
- The 16 expansion controls (`*-11` through `*-14`) are mechanically checked
  but not two-human validated; the original 40 scenarios carry recorded
  two-human ratings.
- The unauthorized-reason coding is post hoc, gold-unblinded, and analyst
  performed; no independent second rater is included.
- The Chinese parallel slice is **analyst-translated** from the English bank
  and is not independently human-validated. It is a cross-lingual direction
  check, not a validated Chinese instrument.
- The real-dialogue arm is a feasibility and calibration appendix. The
  LSF/SSF instrument failed calibration and is reported as a negative
  measurement result, not as a working instrument.

## Manifest

`MANIFEST.sha256` lists every file with its SHA-256 digest.
