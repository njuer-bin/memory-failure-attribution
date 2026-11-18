# Stage 2 LSF/SSF Calibration — Result (2026-11-18)

## Status: FAILED; do not freeze Stage 2

Both sheets are complete (45/45, no blanks), but all three gates fail:

| Field | Raw | Kappa | Gate | Verdict |
|---|---:|---:|---|---|
| `proposition_identity_in_memory` | 0.756 | 0.507 | raw ≥0.90, κ ≥0.80 | FAIL |
| `lsf_outcome` | 0.733 | 0.581 | raw ≥0.85, κ ≥0.70 | FAIL |
| `ssf_outcome` | 0.578 | 0.432 | raw ≥0.80, κ ≥0.65 | FAIL |
| `status_assigned_from_memory` | 0.667 | 0.569 | descriptive | weak |

Provenance is not collected by maintainer decision; report as
**annotator-unspecified**.

## Distributions

- LSF: A preserved 23 / altered 11 / absent 11; B 20 / 13 / 12.
- SSF: A correct 17 / underspecified 14 / distorted 10 / unassessable 4;
  B 10 / 15 / 10 / 10.
- Proposition identity: A preserved 30 / partial 11 / lost 4;
  B 28 / 16 / 1.
- Status from memory: A intending 24, unassessable 5; B intending 15,
  unassessable 10.

## Diagnosis

### 1. Generation drift (the main cause of proposition loss)

The generator passed the full context to the writer but **stripped the target
turn marker** (`>>`). With real multi-topic contexts, the writer often
compressed an adjacent turn instead of the target proposition. Example
`S2M-012`: the target is "I want to live authentically and help others to do
the same", but the memory is about Melanie praising Caroline's art. This makes
the item genuinely unassessable and drives the 15-17 partial/lost ratings.

This is a proposition-control failure, not a status effect. The writer must be
told which turn is the target; the marker must stay in the prompt. The marker
does not add status information beyond what is already in the conversation.

### 2. Cue lexicon gap

The guide does not map common paraphrases to status types. Examples:

- `S2M-004`: memory "User will create a dedicated meditation space"; A
  `CUE_PRESERVED`, B `CUE_ALTERED`.
- `S2M-007`: gold "I think I'll go with the fruit chaat" (hedged `INTENDING`);
  memory "The user chose fruit chaat"; A assigned `COMMITTED`, B `COMPLETED`.
- `S2M-008`: memory "User will use an online route finder"; A `CUE_PRESERVED`,
  B `CUE_ALTERED`.

"will", "plan to", "chose", "learned", and "managed to" need explicit status
mappings.

### 3. SSF `UNDERSPECIFIED` vs `DISTORTED` boundary

A often calls a memory `DISTORTED` where B calls it `UNDERSPECIFIED`
(`S2M-001`, `S2M-006`, `S2M-008`). The guide says a missing cue alone is not
distortion, but does not define when a weaker/stronger cue crosses into
distortion. A decision tree is needed.

### 4. `UNASSESSABLE` threshold

B uses `UNASSESSABLE` 10 times, A 4. The guide does not say how much of the
proposition must survive before the status can be assessed.

## Decision

- Stage 2 remains **not frozen**; no confirmatory generation.
- Do not reuse these 45 memories. They are a failed calibration instrument.
- Fix the generator to keep the target marker and instruct the writer to focus
  on the marked turn.
- Add a cue lexicon, an SSF decision tree, and proposition-identity examples to
  the guide (v2.4), plus a short training pass.
- Regenerate the 45 memories and re-annotate with two independent humans.

## Artifacts

- `results/status_drift_v3_real_audit/stage2_lsf_ssf/annotator_A.csv`
- `results/status_drift_v3_real_audit/stage2_lsf_ssf/annotator_B.csv`
- `results/status_drift_v3_real_audit/stage2_lsf_ssf/analysis/agreement.json`
- `experiments/stage2_lsf_ssf_generator.py`
- `experiments/analyze_stage2_lsf_ssf.py`
