# Annotation Integrity Correction (2026-11-16)

## What was found

`results/status_drift_v2_pilot/v24_full/annotation/_work/fill_b.py` states:

> Annotator B pass. Labels are keyed by (trajectory_id, condition); **defaults
> follow the gold final status**, overrides carry the genuinely contested rows
> plus notes.

The script fills `annotator_B.csv` from the gold status for all non-override
rows, and from hand-written overrides for a small set of contested rows. It does
not read `annotator_A.csv`, but it is not an independent human annotation.

## What this invalidates

- The reported **inter-annotator agreement** (status-aware: raw 1.000, kappa
  1.000; neutral: raw 0.900, kappa 0.764) is **not** evidence of independent
  annotator reliability. It compares one manual annotator against a
  gold-derived file.
- The B-based drift rates are **gold-anchored**, not independent estimates.
- The earlier claims "two annotators, independent" in
  `2026-11-16-status-drift-v24-human-annotation.md` and
  `2026-11-16-status-drift-v24-neutral-human-annotation.md` are corrected by
  this note.

## What remains valid

**Annotator A's labels are the only manual annotations.** They were produced
before the B script and contain row-level notes. The A-only estimates are:

### Status-aware writer (`v24_full`)

| Condition | A YES / preserved | rate |
|---|---:|---:|
| Raw | 0 / 30 | 0.0% |
| Direct D5 | 0 / 30 | 0.0% |
| Recursive D5 | 2 / 29 | 6.9% |
| Rewrite-matched D5 | 3 / 30 | 10.0% |
| Overall | 5 / 119 | 4.2% |

Dimensions: epistemic 2/40 = 5.0%, intentional 3/40 = 7.5%,
conditional 0/39 = 0.0%.

### Neutral writer (`v24_full_neutral`)

| Condition | A YES / preserved | rate |
|---|---:|---:|
| Raw | 0 / 30 | 0.0% |
| Direct D5 | 0 / 30 | 0.0% |
| Recursive D5 | 4 / 26 | 15.4% |
| Rewrite-matched D5 | 5 / 28 | 17.9% |
| Overall | 9 / 114 | 7.9% |

Dimensions: epistemic 0/40 = 0.0%, intentional 9/35 = 25.7%,
conditional 0/39 = 0.0%.

## Corrected interpretation

- The qualitative contrast survives on A's labels: neutral roughly doubles the
  status-aware drift at Recursive and Rewrite-matched D5, and the intentional
  dimension carries most neutral cases.
- **Do not report inter-annotator agreement or kappa for these files.** One
  annotation source is manual, the other is gold-derived.
- A genuine two-annotator reliability study requires a second person to label
  the 120 items independently, without gold defaults and without inspecting A's
  file. Only then can raw agreement and Cohen's kappa be computed.

## Status of files

- `annotator_A.csv` — manual annotation; valid single-annotator data.
- `annotator_B.csv` — gold-derived construction with overrides; keep as a
  gold-anchored sanity check, **not** as an independent annotator.
- `annotation/_work/` — working scripts and dumps; not committed. `fill_b.py`
  documents the construction.

## Update (2026-11-16, later)

The **neutral** `annotator_B.csv` was re-annotated manually and is now an
independent manual annotator. The neutral two-annotator reliability is valid:
unsupported-status raw agreement 0.942, Cohen's kappa 0.849; drift 6.7–7.9%.

The **status-aware** `annotator_B.csv` remains gold-derived. Its agreement and
kappa claims remain withdrawn until it is re-annotated manually.

## Required action

1. Recruit a genuine second annotator (or run a second independent manual pass
   without gold defaults).
2. Recompute agreement and kappa on two manual files.
3. Until then, report only A-only drift estimates and label them as
   single-annotator.
