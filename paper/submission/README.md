# Submission build — 8-page *ACL / COLING format

This folder is self-contained except for the official style files, which are
distributed with the conference template and should not be copied from here.

## Files

- `main.tex` — main body, Limitations, Ethics, References, Appendix.
- `custom.bib` — 16 references, checked against the full texts.
- `figures/` — Figs. 1–6 as vector PDFs (ACL column width).
- `../V3_PAPER_DRAFT.md` — the working draft everything here is compressed from.

## Build on Overleaf (recommended; no local TeX needed)

1. Create a project from the official *ACL template ("ACL Conference
   Proceedings Template", or the `acl-org/acl-style-files` repository). It
   provides `acl.sty`, `acl_natbib.bst`, and `main.tex`.
2. Replace its `main.tex` with this folder's `main.tex`.
3. Upload `custom.bib` and the six PDFs in `figures/`.
4. Compile with pdfLaTeX. BibTeX runs automatically on Overleaf; if you build
   locally, run `pdflatex → bibtex → pdflatex → pdflatex`.
5. The `[review]` option in `\usepackage[review]{acl}` produces anonymized,
   line-numbered output. For the camera-ready, switch to
   `\usepackage{acl}` and add the author block.

## Page budget

The body text is ~4,500 words plus five figures and two tables, which lands
near 7–7.5 pages of the 8-page main body. Limitations, Ethics, References, and
Appendix do not count. If the body overruns:

- move Fig. 3 (mechanism) to the appendix and cite it there;
- move the second-writer table (already in Appendix D) into the text only if
  space allows;
- trim Section 7 (real-data) to two paragraphs, keeping the calibration numbers.

If it comes in short, the cheapest additions are the Study 2a decision table
(Appendix B) as a compact body table and one paragraph on the reason coding.

## Anonymization checklist

- [x] No repository URL, username, machine path, or commit hash in `main.tex`,
  `custom.bib`, or the figure PDFs.
- [x] No internal artifact or protocol names in the text.
- [x] Author block is `Anonymous ACL submission`; `review` mode on.
- [ ] Check the PDF metadata (Overleaf sets the title, not the author).
- [ ] Check the supplementary archive: no `.git`, no `results/`, no state files.
- [ ] Re-read the acknowledgments: there should be none in review mode.

## What still needs a human

The experimental content is final, but two disclosures are unresolved and are
stated in Limitations: the 16 new authorization controls are not
two-human-validated, and the reason coding is analyst-only. See
`../../to_human/2026-11-19_outstanding_human_tasks.md`.

## Rebuilding the figures

Figures are generated from the frozen analysis artifacts, never retyped:

```bash
G:/aconda/python.exe -m experiments.make_paper_figures
```

The generator now mirrors every figure into `paper/submission/figures/` (and
`paper/submission_ecai/figures/`) with the short names used by `main.tex`
(`fig2_omission.pdf`, `fig3_mechanism.pdf`, `fig6_calibration.pdf`), so no manual
copy step is needed.
