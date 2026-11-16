# V3 Blind Annotation Calibration Result (2026-11-16)

**Set:** `results/status_drift_v2_pilot/v3_path_pilot_p1c/annotation/`
**Items:** 60 (10 trajectories × 6 paths), anonymized and shuffled.
**Annotators:** A and B, independent.
**Condition key:** stored outside the repository
(`G:/memory_failure_backup/v3_annotation_key_p1c.csv`), curator-only.
**Status:** calibration only; **not** a confirmatory result.

## 1. Agreement

| Field | Raw agreement | Cohen's kappa |
|---|---:|---:|
| proposition_identity | 0.933 | −0.026 |
| epistemic_applicable | 0.400 | 0.000 |
| intentional_applicable | 0.600 | 0.000 |
| conditional_applicable | 1.000 | 1.000 |
| action_applicable | 1.000 | n/a |
| epistemic_status | 0.383 | 0.321 |
| intention_status | 0.367 | 0.256 |
| action_status | 0.450 | 0.000 |
| condition_status | 0.933 | 0.858 |
| evidence_support | 0.833 | 0.703 |
| **primary_judgment** | **0.733** | **0.578** |
| confidence | 0.883 | 0.673 |

The primary-judgment agreement is moderate, not at a confirmatory level. The
applicability fields are the weakest: the annotators disagree strongly about
which state dimensions apply.

## 2. Human label distribution

| Label | A | B |
|---|---:|---:|
| NO_DISTORTION | 36 | 25 |
| STATUS_OMISSION | 22 | 19 |
| LEGITIMATE_UPDATE | 0 | 10 |
| UNSUPPORTED_STATUS_DISTORTION | 1 | 4 |
| PROPOSITION_LOSS | 1 | 1 |
| AMBIGUOUS_UNASSESSABLE | 0 | 1 |

**Status omission dominates; unsupported status distortion is rare.** This is
the central calibration finding.

## 3. Unsupported distortion by path (human labels)

| Path | A unsup / preserved | B unsup / preserved |
|---|---:|---:|
| PEEK | 0/10 | 0/10 |
| S1 | 0/10 | 1/10 |
| S2 | 0/9 | 0/10 |
| PARA | 0/10 | 0/10 |
| TEMP1 | 1/10 | 2/9 |
| TEMP2 | 0/10 | 1/8 |

The deterministic cue metric showed a strong PEEK > TEMP gradient; the human
labels do not reproduce it as **unsupported distortion**. Most of the
deterministic "ABSENT" cases are annotated as **status omission**, not as an
unsupported changed state.

## 4. Disagreement categories

Primary judgment (A → B):

- `NO_DISTORTION → LEGITIMATE_UPDATE`: **10**
- `STATUS_OMISSION → UNSUPPORTED_STATUS_DISTORTION`: **3**
- `PROPOSITION_LOSS → STATUS_OMISSION`: 1
- `NO_DISTORTION → AMBIGUOUS_UNASSESSABLE`: 1
- `STATUS_OMISSION → PROPOSITION_LOSS`: 1

Applicability:

- epistemic: A `NOT_APPLICABLE` → B `APPLICABLE`: **36**
- intentional: A `NOT_APPLICABLE` → B `APPLICABLE`: **24**

B systematically marks more dimensions applicable than A. This is a guide
problem, not a data problem.

## 5. Interpretation

1. **The deterministic cue metric conflates omission with distortion.** It maps
   "status cue absent" to ABSENT, which the V3 ontology distinguishes from an
   unsupported changed state. The P1c path divergence is therefore largely
   **omission divergence**, not necessarily unsupported status distortion.
2. **The dominant human-labeled outcome is STATUS_OMISSION** (A 37%, B 32%).
   Any V3 claim must include omission in the joint outcome distribution; an
   unsupported-distortion-only claim is not supported by these labels.
3. **The path gradient is weak in human labels.** PEEK is 0 unsupported in both
   annotators, but so are S2 and PARA; TEMP1 is highest (10–22%) with n=9–10.
   This is directional at best.
4. **Applicability and the omission/distortion boundary are not yet stable.**
   The guide needs explicit rules for when each dimension applies and for
   distinguishing NO_DISTORTION, LEGITIMATE_UPDATE, STATUS_OMISSION, and
   UNSUPPORTED_STATUS_DISTORTION.

## 6. Gate verdict (V3 P0/P1)

- Two annotators can apply the guide with acceptable agreement after
  adjudication: **FAIL** for the rich ontology.
  - primary kappa 0.578;
  - epistemic applicability raw 0.40; intentional applicability raw 0.60;
  - status-field agreement low (epistemic 0.383, intention 0.367).
- Do **not** proceed to the V3 confirmatory annotation or paired study with the
  current guide.

## 7. Required revisions before re-calibration

1. **Applicability rules:** define exactly when epistemic, intentional,
   conditional, and action dimensions are applicable, with positive and
   negative examples.
2. **Collapse the ontology:** reduce each dimension to 2–3 mutually exclusive
   categories for the confirmatory study (e.g., epistemic POSSIBLE /
   ESTABLISHED / OMITTED; intention CONSIDERING / COMMITTED / OMITTED).
3. **Two-step judgment:** first "is any status expressed?" (omission check),
   then "is the expressed status supported?" (distortion check).
4. **Clarify LEGITIMATE_UPDATE vs NO_DISTORTION:** give examples of a later
   supported change of mind.
5. **Clarify STATUS_OMISSION vs UNSUPPORTED_STATUS_DISTORTION:** omission has no
   asserted alternative state; distortion asserts a different state.
6. **Re-calibrate** on a new 60-item set with the revised guide; do not reuse
   this set for confirmatory claims.

## 8. Consequence for the research route

- The P1a/P1b/P1c deterministic path results remain valid as **cue-state
  divergence** measurements, but they must not be reported as unsupported
  status distortion without human labels.
- The V3 primary outcome should be the **joint distribution including
  STATUS_OMISSION**, not unsupported distortion alone.
- The path-dependent claim is provisionally about **cue/status omission and
  divergence**, with unsupported distortion as a rarer subtype.
