# Stage 2 LSF/SSF Calibration — Run 2 Result (2026-11-18)

## Status: FAILED, but improved; Stage 2 is not frozen

Both sheets are complete (45/45, no blanks). All three gates fail, but every
field improved from run 1:

| Field | Run 1 raw/κ | Run 2 raw/κ | Gate |
|---|---:|---:|---|
| `lsf_outcome` | 0.733 / 0.581 | **0.800 / 0.689** | ≥0.85 / ≥0.70 |
| `ssf_outcome` | 0.578 / 0.432 | **0.756 / 0.625** | ≥0.80 / ≥0.65 |
| `proposition_identity_in_memory` | 0.756 / 0.507 | **0.800 / 0.607** | ≥0.90 / ≥0.80 |
| `status_assigned_from_memory` | 0.667 / 0.569 | 0.844 / 0.778 | descriptive |

LSF and SSF are close (κ short by 0.011 and 0.025). Proposition identity is the
real blocker (κ 0.607 vs 0.80).

Provenance is not collected by maintainer decision; report as
**annotator-unspecified**.

## Diagnosis

### Proposition identity: predicate paraphrase

Nine disagreements, mostly A `PARTIAL` vs B `PRESERVED`/`LOST`. The memories
often replace the target speech act with a related one:

- `S2M-003`: target "I'll start writing about my journaling routine"; memory
  "You ask for advice on structuring a blog post..." — A `PARTIAL`, B
  `PRESERVED`. The action changed from writing to asking for advice.
- `S2M-018`: same target; memory "Asked about structuring a 500-700 word blog
  post..." — A `PARTIAL`, B `PRESERVED`.
- `S2M-042`: target "I'm planning a trip to Chicago ... recommend restaurants";
  memory "User seeks restaurant recommendations..." — A `PARTIAL`, B
  `PRESERVED`. The planning action is gone.
- `S2M-033`: target "I'll go with the fruit chaat"; memory "Recommended fruit
  pairings... Enjoy your fruit chaat" — A `PARTIAL`, B `LOST`. The user's
  choice is not stated.

The guide's `PRESERVED` rule says "action + object + person recoverable" but
does not require the **same action predicate**. Annotators reasonably differ on
whether "ask for advice about writing" preserves "writing".

### LSF: cue mapping beyond the lexicon

Nine disagreements, eight outside identity. Examples:

- `S2M-008`: gold `INTERESTED` ("I'd like to find a route"); memory "The user
  will use an online route finder" (`will` = `INTENDING`); A `DISTORTED`, B
  `CORRECT`.
- `S2M-019`: gold `CONSIDERING`/`INTERESTED` ("thinking of going... want to try
  rock climbing"); memory "You plan to climb rocks" (`plan to` = `INTENDING`);
  A `CORRECT`, B `DISTORTED`.
- `S2M-015`: gold `INTERESTED`; memory "User prefers MapMyRun..." — preference
  is not a status cue; A `UNDERSPECIFIED`, B `DISTORTED`.

The lexicon helped, but the annotators still differ on whether a paraphrase
("prefers", "will use", "plans to") is the same status type or a different one.

### SSF: `DISTORTED` vs `UNDERSPECIFIED`/`CORRECT`

Eleven disagreements, ten outside identity. The same memories show A calling a
stronger paraphrase `CORRECT` while B calls it `DISTORTED`, or the reverse.
The v2.4 tree defines incompatible authorization changes, but the boundary
between "same family, weaker cue" and "authorization changes" is still applied
differently.

## Decision options

**A. v2.5 + training + re-annotate.** Add a predicate-preservation rule
(`PRESERVED` requires the same action predicate or a direct inflection; a
different speech act is `PARTIAL`/`LOST`), LSF examples for "will use / plans
to / prefers", and SSF examples for authorization change. Then retrain and
re-annotate the 45 memories. Cleanest, but another 1.5-2 h per annotator.

**B. Third-person adjudication.** A third person adjudicates the 9 identity +
9 LSF + 11 SSF disagreements (29 items), and the analysis reports unadjudicated
and adjudicated results. Cheaper than re-annotation, but 29/45 adjudicated is a
large fraction; the reliability claim becomes weak.

**C. Scope the real-data arm.** Keep the successful gold calibration as a
feasibility/measurement appendix, report LSF/SSF as a failed calibration and
future work, and keep the paper's primary claims on the synthetic V3
(P2/P3/P5) and P4.2. This does not require another annotation cycle and does
not overclaim real-dialogue fidelity.

Recommendation for the paper timeline: **C**. The real-data arm's contribution
is the feasibility audit + gold coding calibration; the LSF/SSF instrument is
not reliable enough to carry a confirmatory claim. If real-dialogue LSF/SSF is
a headline, choose A; B only if a third adjudicator is available and the
29-item adjudication is acceptable.

## Artifacts

- `results/status_drift_v3_real_audit/stage2_lsf_ssf/annotator_A.csv` /
  `annotator_B.csv`
- `analysis/agreement.json`
- `annotator_A_failed_run1.csv` / `annotator_B_failed_run1.csv`
- `analysis/agreement_failed_run1.json`
- `docs/research/STAGE2_LSF_SSF_TRAINING.md`
- `V3_REAL_STAGE2_DRAFT.md` v2.4 §8e
