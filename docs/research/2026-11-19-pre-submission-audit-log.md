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
Fig. 5 (P5 mitigation), Fig. 6 (real-data calibration; gold fields after
third-person adjudication, LSF/SSF unadjudicated, gates from
`V3_REAL_STAGE2_PREFREEZE.md`). Palette: categorical slots 1–3 of the validated
reference palette (blue `#2a78d6`, orange `#eb6834`, aqua `#1baf7a`), which
passes the all-pairs CVD and normal-vision checks in light mode; aqua is below
3:1 contrast, so every aqua mark carries a direct label.

## A4. Novelty appendix check

ABBEL and Supersede read to the end; neither contains a
proposition-controlled status split. See
`docs/research/2026-11-17-novelty-audit.md` §8.

## A5. Third-model control probe

`mistral:7b` fails the P4.2 action-form control gate (9/20); not run on the
full matrix. Reported as a model limitation, not a replication.

## A6. Unauthorized-reason sheet

`experiments/make_v31_reason_sheet.py` regenerates the 39-row audit record and a
blind second-rater sheet (no analyst code, no variant, shuffled order). The
analyst distribution is 34 D1 + 5 O2; the second-rater columns are blank, so
the sheet is ready for an independent rater but the claim remains analyst-only.

## A7. Claim audit against C1-C9

| Claim | Draft location | Evidence | Verdict |
|---|---|---|---|
| C1 chained rewriting omits status | Abstract, section 4.2, Table 3 | P3 330 items, 44-54% vs 3.7% | supported |
| C2 re-editing, not budget/call count | section 4.3, Fig. 3 | rewrite-matched = recursive; repeated-direct = direct; source peek -0.400 | supported |
| C3 distortion is rare | section 4.2 | 3/330, underpowered | supported with caveat |
| C4 distortion raises unauthorized action | Abstract, section 5.3, Table 8 | P4 20/30 vs 2/30; P4.2 24/34 and 10/34 vs 0/34 | supported |
| C5 omission is task/request-dependent | Abstract, section 5.3, section 8 | P4 0/30; P4.2 5/34 neutral, 0/34 action | supported |
| C6 source access strongest (primary) | Abstract, section 6 | 30/30 vs 14/26; +0.533 | supported, model-dependent |
| C7 status-aware prompt partial, non-additive | section 6 | 27/30; interaction -0.500 | supported |
| C8 intentional status gold-codeable | section 7 | adjudicated 1.000/1.000 and 0.975/0.969 | supported with caveats |
| C9 LSF/SSF reliable | section 7, Fig. 6 | 0.689/0.625/0.607 kappa | **not supported**; reported negative |

The do-not-say list is respected: no "first" claim for state tracking, recursive
omission, source access, or memory-to-action; no universal omission claim; no
LSF/SSF or conditional reliability claim; no natural-dialogue replication.

## A8. Citations

All 14 audited PDFs were re-read at the title page; authors, titles, venues, and
arXiv identifiers in the draft match. LongMemEval and LoCoMo have no local PDF
and use the published records (arXiv:2410.10813; arXiv:2402.17753); re-check at
build time.

## A9. Variant-length reconciliation (2026-11-19)

The draft's "present 15.7 / omitted 9.4 / distorted 10.3 tokens, rank
correlation 0.16" had no artifact and no longer reproduced. Recomputed from
`results/status_drift_v3_p4_2_v3_v31/run/records_gemma3_12b.jsonl` by
`experiments/analyze_p4_2_lengths.py` (whitespace tokens of the `memory` field,
neutral form):

| Stratum | Present | Omitted | Distorted | Spearman vs execution |
|---|---:|---:|---:|---:|
| 34 over-commitment (paper) | 15.353 | 10.059 | 10.471 | 0.020 |
| all 54 incl. controls | 15.667 | 9.370 | 10.278 | 0.236 |

The old values reproduce only on the all-54 stratum, which mixes in the 20
authorized controls (distorted execution is near zero there by construction),
and the old 0.16 came from ordinal tie ranks. The paper now uses the 34-scenario
values and reports Spearman 0.02 / Pearson -0.06. Artifact:
`analysis/variant_length_check.json`; registry: `paper/V3_NUMBERS.md` §7c.
The direction of the argument is unchanged and stronger.

## A10. Table completeness and LaTeX structure

- The second-writer table omitted the ambiguous column, so row sums were 10/12
  for rewrite-matched. Added the ambiguous column (2/12) in both the draft and
  `main.tex`.
- The mitigation table dropped unsupported and ambiguous items; the caption now
  accounts for them (neutral 1 unsupported; status-aware 2 + 1; combination
  1 + 1; source access none).
- Structural check of `main.tex`: environments balanced, braces balanced, every
  `\ref` has a label, every citation key exists in `custom.bib`, and every bib
  entry is cited.
- Anonymity: no URL, username, machine path, repository name, or commit hash in
  `main.tex`, `custom.bib`, or the six figure PDFs; figure metadata carries only
  the Matplotlib producer string.

## A11. Figure scale audit

The figure PDFs did not match the widths at which `main.tex` included them.
Fig. 1 was drawn on a 6.9 in canvas but included at `\columnwidth`, so its
7.6 pt labels would have printed at about 4.7 pt. Figs. 3 and 6 had tight
bounding boxes of 3.9 in and 3.6 in because annotations and tick labels
overflowed, shrinking their text to about 6.8 pt.

Fixed in `make_paper_figures.py`: `save()` now calls `tight_layout(pad=0.25)`
and saves at the nominal canvas size, tick labels no longer sit on the axes
edge, and the long annotations are shortened or moved inside the axes. Every
single-column PDF is now exactly 3.3 in and every double-column PDF 6.9 in, so
the 8 pt text prints at 8 pt. Fig. 1 is included as a full-width `figure*` at
`\textwidth`. Text blocks were checked programmatically for page-edge overflow;
none remain. The six submission copies were regenerated from the same script.

## A12. Chinese parallel check (2026-11-19)

Ten English Study 2b scenarios (7 over-commitment, 3 authorized controls) were
mirrored to Chinese and run with the same four memory variants and two request
forms (80 calls, `gemma3:12b`, 80/80 parsed). The Chinese items are
analyst-translated, not human-validated. Distortion harm replicates (7/7
neutral, 4/7 action; DiD $-0.429$), and the action-form attenuation matches the
English sign and size. The request-dependence of omission over-action does not
replicate at $n=7$ per cell: one omitted scenario executes in each form, and its
stated reason is the O2 mechanism. Three controls are not a gate: present 3/3 in
both forms, but no-memory executes once under the action request and distorted
controls execute 3/6. Artifact:
`results/status_drift_v3_p4_2_zh_parallel/`; note:
`docs/research/2026-11-19-v3-p4-2-zh-parallel.md`; number registry
`paper/V3_NUMBERS.md` §7d. The paper's Study 2b paragraph and Appendix
(`app:zh`) state the analyst-translated provenance and the non-replication.

## A13. Supplementary package (2026-11-19)

`experiments/make_supplementary.py` assembles and zips
`paper/supplementary/` (46 files, 747 KiB; zip 179 KiB) from curated sources:
four scenario banks, prompt sources, nine frozen analysis scripts, aggregate
label tables for Studies 1, 2a, 2b (including the Chinese slice), 3, the
replication and the real-data audit, the annotation protocol, and Figures 1–6.
The builder strips local interpreter
and machine paths and refuses to include raw annotation sheets, provenance
files, or model-output records. A SHA-256 manifest verifies every file
(46/46 OK). An identifier scan finds no user name, initials, repository URL, or
absolute path in the package.

## Open audit items

- Provenance and adjudication disclosure pass: **read complete**. Limitations
  states annotator-unspecified for the synthetic annotation, model-assisted
  adjudication, 12-trajectory replication, and analyst-only reason coding; the
  P4.2 bank keeps its recorded two-human provenance. No overclaim found.
- Anonymity pass: source, bibliography, figures, and the supplementary package
  are clean (A10, A13). Only the built PDF metadata still needs a post-build
  check.
- 8-page build: **done locally** (2026-11-19). MiKTeX 25.12 is now
  installed; the submission builds with pdfLaTeX -> BibTeX -> pdfLaTeX x2.
  Output `paper/submission/main.pdf` is 12 pages total; the main body ends at
  the Conclusion and ``Limitations`` begins on page 8, so the body is within
  the 8-page main-body limit (Limitations/Ethics/References/Appendix are
  exempt). Structural checks pass; 0 unresolved references or citations and
  0 ``??``. Overfull boxes were eliminated by rewriting the long status-tuple
  math atom, adding breakpoints to the slash-joined small-caps label runs,
  widening the two parameter columns, and promoting the two widest appendix
  tables (Study 2a counts, second-writer replication) to full-width
  ``table*``. The only remaining warnings are the harmless ``T1/ptm/m/scit
  undefined`` font-shape fallback and ``h float specifier changed to ht``.
  Rebuild: `cd .tools/build && latexmk -pdf main.tex`, or pdflatex/bibtex/pdflatex/pdflatex as above.
- Supplementary archive: **assembled** (A13, 44 files, manifest 44/44 OK).
