# Stage 2 LSF/SSF Calibration Sheet (45 memories)

**Status: run 1 failed; sheet regenerated under v2.4.** The first run
(LSF 0.733/0.581; SSF 0.578/0.432; proposition identity 0.756/0.507) failed
because the generator stripped the target-turn marker and the guide lacked a cue
lexicon and SSF tree. The generator now keeps the `>>` marker and focuses the
writer on that turn; v2.4 adds the cue lexicon and SSF decision tree. Run-1
labels are preserved as `annotator_A_failed_run1.csv` /
`annotator_B_failed_run1.csv`.

Purpose: calibrate Lexical Status Fidelity (LSF) and Semantic Status Fidelity
(SSF) on generated memories before any confirmatory generation. This sheet is
separate from the gold-coding calibration.

## Composition

- 15 gold items (14 intentional, 1 epistemic) x 3 memory conditions
  (`direct`, `recursive`, `source_peek`) = 45 memories. The eligible pool is
  34 intentional and 1 epistemic, so the epistemic arm is descriptive only;
  do not gate epistemic reliability on one item.
- The memory condition and the gold labels are **not** in the sheet; they are
  in the key outside the repository at
  `G:/memory_failure_backup/stage2_lsf_ssf_key_2026-11-18.csv`.
- Do not open `memories.jsonl`, the key, the gold calibration sheets, or the
  raw source corpora.

## Files

- `annotator_A.csv`, `annotator_B.csv` — one per annotator; fill only the six
  rating columns.
- `sheet.csv` — identical reference copy.
- `provenance_template.json` — retained but optional.

Two independent humans annotate every row. No model assistance. Provenance is
not collected by maintainer decision; report the result as
**annotator-unspecified**.

## What to fill

For each row:

1. Read `target_sentence` and `context` (the evidence E). Decide the
   evidence-supported status of the target proposition in your own judgment.
2. Read `memory` (M).
3. Fill:

| Column | Values |
|---|---|
| `lsf_outcome` | `CUE_PRESERVED` / `CUE_ALTERED` / `CUE_ABSENT` / `NOT_APPLICABLE` |
| `lexical_cue_in_memory` | the cue text in M, or empty |
| `ssf_outcome` | `SEMANTIC_CORRECT` / `SEMANTIC_DISTORTED` / `SEMANTIC_UNDERSPECIFIED` / `UNASSESSABLE` |
| `status_assigned_from_memory` | the status a careful reader would infer from M, or `UNASSESSABLE` |
| `proposition_identity_in_memory` | `PRESERVED` / `PARTIAL` / `LOST` / `AMBIGUOUS` |
| `ambiguity_reason` | free text or empty |
| `notes` | one line: P, gold status you inferred from E, and the M status |

### LSF rules

- `CUE_PRESERVED`: M contains an explicit cue of the **same status type** as
  the evidence-supported status.
- `CUE_ALTERED`: M contains an explicit cue of a different status type or a
  materially different strength (e.g., evidence `COMMITTED`, M says "plans to").
- `CUE_ABSENT`: no explicit status expression for the target proposition.
- `NOT_APPLICABLE`: the source itself had no explicit cue.
- Record the cue text in `lexical_cue_in_memory`.
- "I think I'll X" is a hedged intentional cue, not an epistemic cue.

### SSF rules

- `SEMANTIC_CORRECT`: the status a careful reader infers from M matches the
  evidence-supported status.
- `SEMANTIC_DISTORTED`: M supports a status incompatible with the evidence
  (stronger, weaker in a way that changes action, or the opposite).
- `SEMANTIC_UNDERSPECIFIED`: M permits the evidence-supported status but does
  not determine it.
- `UNASSESSABLE`: the proposition is lost/ambiguous in M, or E is insufficient.
- A missing cue alone is not distortion. If M can be read as the evidence
  status or another status, use `SEMANTIC_UNDERSPECIFIED`.

### Proposition identity

- `PRESERVED`: the same proposition (action + object) is recoverable.
- `PARTIAL`: a core element (action, object, person, condition) is missing.
- `LOST`: the proposition is not recoverable.
- `AMBIGUOUS`: cannot decide.

### Decision order

1. State the target proposition from E.
2. Assign the evidence-supported status.
3. Does M preserve the same proposition? (`proposition_identity_in_memory`)
4. LSF: is a same-type cue present in M?
5. SSF: what status does M imply, and does it match the evidence status?
6. Record ambiguity rather than forcing a label.

## Gates (proposed)

| Field | Raw | Kappa |
|---|---:|---:|
| `proposition_identity_in_memory` | ≥0.90 | ≥0.80 |
| `lsf_outcome` | ≥0.85 | ≥0.70 |
| `ssf_outcome` | ≥0.80 | ≥0.65 |

## After completion

Run:

```
G:/aconda/python.exe -m experiments.analyze_stage2_lsf_ssf
```

The analysis reports raw agreement and Cohen's kappa per field, and joins the
key only after the labels are fixed to report condition-level descriptives.
