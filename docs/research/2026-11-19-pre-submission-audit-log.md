# 2026-11-19 — pre-submission audit log

Running record of the pre-submission checks required by the paper plan. Each
entry states what was checked, against which artifact, and the verdict.

## A1. P4 downstream numbers (raw records vs paper Table 5)

Checked `paper/V3_PAPER_DRAFT.md` Table 5 and §5.1 against
`results/status_drift_v3_p4/records.jsonl` (30 trajectories × 4 variants).

| Variant | Decisions recomputed | Paper |
|---|---|---|
| present | PROCEED 12, CONFIRM 18 | 12 / 18 |
| omitted | CONFIRM 30 | 0 / 30 |
| distorted | PROCEED 20, CONFIRM 10 | 20 / 10 |
| no_memory | ABSTAIN 17, CONFIRM 13 | 0 / 13 / 17 |

`summary.json` by_variant: unauthorized 2 / 0 / 20 / 0; evidence-consistent
28 / 20 / 0 / 20. Paired contrasts vs present: omitted unauthorized −0.067
[−0.167, 0.000], evidence-consistent −0.267 [−0.467, −0.067]; distorted
unauthorized +0.600 [0.433, 0.767], evidence-consistent −0.933
[−1.000, −0.833]. All match the paper. The summary contrasts are not stale for
P4; no replacement needed.

## A2. P4.2 v3.1 numbers (records → summary → paper)

Checked in this order: `records_*.jsonl` → `summary.json` (regenerated with the
runner's own `summarize()`) → `analysis/p4_2_v31_summary.json` (built by
`experiments/analyze_v31_p4_2.py`) → paper §5.2–5.5 and Table 7–10. The paper
numbers match the analysis artifacts. Denominators audited: over-commitment
34 (24 intentional + 10 conditional); controls 20; per-dimension cells 24 and
10.

## A3. Figure provenance

`experiments/make_paper_figures.py` reads only frozen CSV/JSON analysis
artifacts; no number is typed into the script. Generated: Fig. 1 (schematic),
Fig. 2 (P3 omission), Fig. 3 (P3 mechanism), Fig. 4 (P4 + P4.2 behavior),
Fig. 5 (P5 mitigation). Palette: categorical slots 1–3 of the validated
reference palette (blue `#2a78d6`, orange `#eb6834`, aqua `#1baf7a`), which
passes the all-pairs CVD and normal-vision checks in light mode; aqua is below
3:1 contrast, so every aqua mark carries a direct label. Fig. 6 (real-data
calibration) still needs a reader over the stage-2 agreement artifacts.

## A4. Novelty appendix check

ABBEL and Supersede read to the end; neither contains a
proposition-controlled status split. See
`docs/research/2026-11-17-novelty-audit.md` §8.

## A5. Third-model control probe

`mistral:7b` fails the P4.2 action-form control gate (9/20); not run on the
full matrix. Reported as a model limitation, not a replication.

## Open audit items

- Fig. 6.
- Citation placeholders: verify authors, venues, years, and IDs for all 2026
  preprints and Findings papers.
- Claim audit against the C1–C9 matrix in `docs/research/V3_PAPER_PLAN.md`.
- Provenance and adjudication disclosure pass (annotator-unspecified for
  P3/P5; model-assisted override counts).
- Anonymity pass (no repository URLs, usernames, or local paths in the main
  PDF, appendices, or supplementary metadata).
- COLING/ACL 8-page compression and LaTeX build; limitations and ethics
  sections after the reference-free page budget.
