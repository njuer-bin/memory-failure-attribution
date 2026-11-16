# Annotation status — status-aware set

- `annotator_A.csv` — manual single-annotator labels; valid.
- `annotator_B.csv` — **gold-derived** construction from
  `_work/fill_b.py` (defaults follow gold, with overrides). It is **not** an
  independent annotator.
- **Do not report inter-annotator agreement or Cohen's kappa from these two
  files.** The earlier agreement/kappa numbers are withdrawn.

Valid A-only drift estimates:

- overall 5/119 = 4.2%;
- Raw 0/30; Direct D5 0/30;
- Recursive D5 2/29 = 6.9%;
- Rewrite-matched D5 3/30 = 10.0%.

See `docs/research/2026-11-16-status-drift-annotation-integrity-correction.md`.
A genuine second independent annotator is required for reliability statistics.
