# Reason-code provenance record — 2026-11-20

Scope: the unauthorized-execution reason codes reported in Study 2b
(`tab:reasons`). This record states only verifiable facts. Details that cannot
be verified from the repository are marked `not recorded`; nothing was
backfilled from memory.

## Gemma3:12b, 39 over-commitment executions

| Field | Value |
| --- | --- |
| Records coded | 39 (34 distorted, 5 omitted) |
| Rater | single analyst (project maintainer) |
| Reviewer type | human |
| Timing | post hoc, after the frozen v3.1 run; exact date not recorded |
| Codebook | four codes: D1, O1, O2, O3 (`analysis/unauthorized_reason_codes.csv`); version not recorded |
| Saw model identity | yes |
| Saw condition/variant | yes |
| Saw gold labels | yes (gold-unblinded) |
| Saw prior codes | n/a (first coding round) |
| Independence | single rater, no joint discussion |

An additional blind sheet (`analysis/reason_sheet_blind.csv`, 39 rows, no
analyst code, no variant, shuffled) was completed with 39/39 agreement
(raw 1.00, kappa 1.00). Its annotator identity and independence are
**not recorded**, so it is not counted as an independent human rating. It is
recorded as `second_rater` in `unauthorized_reason_codes_summary.json` with
`independent_human_rating: false`.

## glm-5.3-flash, 65 over-commitment executions

| Field | Value |
| --- | --- |
| Records coded | 65 (54 D1, 11 O2, 0 O1/O3) |
| Rater | single analyst (project maintainer) |
| Reviewer type | human |
| Timing | post hoc, after the v3.1 gateway run; exact date not recorded |
| Codebook | same four codes as the Gemma round; version not recorded |
| Saw model identity | yes |
| Saw condition/variant | yes |
| Saw gold labels | yes (gold-unblinded) |
| Saw prior codes | yes (the Gemma codes were already recorded) |
| Independence | single rater |
| Second coding | none |
| Rater identity, date, and codebook-version record | **not recorded** beyond this summary |

The GLM 65-record coding has no blind sheet and no second rater. It stays a
single-analyst, post-hoc description.

## Claim boundary

Reason codes describe what the output text says, not why the model acted. They
support the exploratory claim that the two failure modes are textually
different: distortion follows a memory that states a decision or
authorization; omission upgrades a mention of consent into consent. They do not
support a causal account of the model's behavior, and the manuscripts describe
the coding as exploratory, post hoc, and gold-unblinded.

## What would change this

A fresh blind re-coding of all 39 Gemma and 65 GLM records under a frozen
codebook, with two independent raters and a documented resolution step, would
replace the "not recorded" fields. The coding round would still be
retrospective and could not be called preregistered.
