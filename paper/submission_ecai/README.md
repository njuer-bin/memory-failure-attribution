# ECAI 2027 submission build

Target: **ECAI 2027** (CCF-B, double-blind, non-ARR). Budget enforced:
**7-page main body (including Limitations) + at most 1 page of references**;
all appendices move to a separate supplementary PDF.

## Files

- `main.tex` — main body, abstract, Limitations folded in, references.
- `appendix.tex` — standalone Supplementary Appendix (prompts, full tables,
  annotation/reliability details, scenario examples, Chinese probe). Not
  page-limited; compiled to `appendix.pdf` and shipped separately.
- `custom.bib` — 16 references, checked against the full texts.
- `figures/` — Figs. 1–6 as vector PDFs.
- `ecai.cls` — **LOCAL STAND-IN**, see below.

## Template status (read this first)

The official ECAI 2027 author kit (the real `ecai.cls`/`.bst` and sample) is
distributed by the conference and IOS Press and is **not yet released** (the
deadline is ~April 2027; the kit usually appears a few months before). This
folder therefore ships `ecai.cls`, a stand-in that reproduces the ECAI
geometry — A4, 9 pt, two columns, IOS-Press-like margins — so the page budget
can be measured now.

When the official kit is released:
1. Replace `ecai.cls` (and add the official `.bst`).
2. Recompile; re-check the page count (the official class may use 10 pt, which
   would make the body slightly longer than measured here).
3. Re-check only the front matter (`\title`, `\author`, abstract block); the
   rest of the source is class-agnostic.

## Build

Local MiKTeX is installed. From this folder:

```bash
latexmk -pdf main.tex
latexmk -pdf appendix.tex
```

Both files set `\pdfsuppressptexinfo=-1`, which strips the local build path
that pdfTeX otherwise embeds in included-figure XObjects (a double-blind leak).

## Measured page budget (stand-in class, 2026-11-20)

- `main.pdf`: **6 pages total** — body (incl. Limitations) and references
  both fit inside 6 pages, i.e. within the 7+1 ceiling with margin.
- `appendix.pdf`: 4 pages, unconstrained.
- 0 overfull boxes, 0 unresolved references/citations.

## Anonymization checklist

- [x] No repository URL, username, machine path, or commit hash in `main.tex`,
  `appendix.tex`, `custom.bib`, or the figure PDFs.
- [x] `main.pdf` / `appendix.pdf` contain no local path (verified by byte scan
  after `\pdfsuppressptexinfo=-1`).
- [x] PDF metadata has no Author/Title (blind-safe); Producer is MiKTeX.
- [x] Author block is `Anonymous ECAI submission`.
- [ ] Re-check metadata once the official class replaces the stand-in.

## What still needs a human (unchanged from the *ACL build)

Two disclosures are unresolved and are stated in Limitations and the
supplementary archive:

1. The 16 expansion authorization controls are mechanically checked but not
   two-human validated.
2. The unauthorized-reason coding is analyst-only, post hoc, gold-unblinded.

The second-writer replication is reported at n = 12 (pre-registered); the
n = 30 sensitivity cohort awaits annotation of 18 trajectories. See
`../../to_human/2026-11-20_ecai_submission_tasks.md`.

## Rebuilding the figures

```bash
G:/aconda/python.exe -m experiments.make_paper_figures
```

Fig. 4 is a three-panel plot (Study 2a, plus Study 2b by request form across
qwen2.5:7b, gemma3:12b, and glm-5.3-flash), generated from the frozen
analysis artifacts, never retyped.
