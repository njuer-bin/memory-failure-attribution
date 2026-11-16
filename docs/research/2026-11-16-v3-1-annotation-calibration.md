# V3.1 Blind Annotation Re-calibration Result (2026-11-16)

**Set:** `results/status_drift_v2_pilot/v3_path_pilot_p1c/annotation_v31/`
**Items:** 60 (10 trajectories × 6 paths), anonymized and shuffled.
**Annotators:** files A and B. **Provenance is not yet recorded** (see §7).
**Condition key:** `G:/memory_failure_backup/v3_annotation_key_p1c_v31.csv`,
curator-only and outside the repository.
**Status:** calibration only; **not** a confirmatory result.

## 1. Validation

Both files contain all 60 items. `experiments.check_v3_annotations` reports
**0 missing required fields and 0 invalid values** for A and B.

## 2. Agreement

Complete-case agreement (fields with both values present; `expressed_status`
also requires the two annotators to agree on the primary dimension).

| Field | n | Raw | Cohen's κ |
|---|---:|---:|---:|
| proposition_identity | 60 | 0.933 | −0.026 |
| primary_dimension | 60 | 0.900 | 0.853 |
| status_expressed | 60 | 0.967 | 0.928 |
| expressed_status | 54 | 0.963 | 0.954 |
| evidence_support | 60 | 0.917 | 0.840 |
| **primary_judgment** | **60** | **0.850** | **0.728** |
| confidence | 60 | 0.833 | 0.536 |

Sensitivity checks:

- `expressed_status` including the six blank/non-blank pairs: raw **0.867**,
  κ **0.838**.
- `primary_judgment` restricted to items both annotators call PRESERVED
  (n=56): raw **0.893**, κ **0.791**.
- `proposition_identity` κ is a prevalence artifact: A labels 57/60 and B
  59/60 PRESERVED. Raw agreement 0.933 with 4 disagreements is the informative
  number; do not interpret the negative κ as substantive disagreement.

Primary-judgment agreement by key dimension:

| Dimension | n | Raw | κ |
|---|---:|---:|---:|
| epistemic | 24 | 0.875 | 0.788 |
| intentional | 18 | 0.944 | 0.904 |
| conditional | 18 | 0.722 | **0.126** |

## 3. Label distribution

| Label | A | B |
|---|---:|---:|
| NO_DISTORTION | 33 | 39 |
| STATUS_OMISSION | 18 | 18 |
| UNSUPPORTED_STATUS_DISTORTION | 4 | 1 |
| LEGITIMATE_UPDATE | 2 | 0 |
| PROPOSITION_LOSS | 1 | 1 |
| AMBIGUOUS_UNASSESSABLE | 2 | 1 |

The dominant label is still **NO_DISTORTION**, with **STATUS_OMISSION**
second (30% under both annotators). Unsupported distortion remains rare
(A 4/60, B 1/60). This replicates the V3 calibration finding.

## 4. Remaining disagreements (9 primary-judgment pairs)

| Direction (A → B) | Count | Items / dimension |
|---|---:|---|
| UNSUPPORTED_STATUS_DISTORTION → NO_DISTORTION | 3 | conditional, gold CONDITION_SATISFIED |
| LEGITIMATE_UPDATE → NO_DISTORTION | 2 | epistemic, intentional |
| STATUS_OMISSION → PROPOSITION_LOSS | 1 | conditional |
| PROPOSITION_LOSS → STATUS_OMISSION | 1 | epistemic |
| STATUS_OMISSION → NO_DISTORTION | 1 | conditional |
| AMBIGUOUS_UNASSESSABLE → STATUS_OMISSION | 1 | epistemic |

Other field disagreements: 4 proposition identity, 6 primary dimension
(3 INTENTIONAL→CONDITIONAL, 3 involving CANNOT_DETERMINE), 2 status expressed,
10 confidence (6 MEDIUM→HIGH), 5 subtype (3 CONDITIONAL_COLLAPSE→NONE).

The dominant residual is **conditional action-vs-condition**: A reads a memory
that juxtaposes a satisfied prerequisite with the action (e.g.
`获奖学金购电脑`) as asserted commitment (`CONDITIONAL_COLLAPSE`), while B
applies the “action scored only if explicitly asserted” rule and says
NO_DISTORTION. Four of the five conditional disagreements are updated
(`CONDITION_SATISFIED`) items.

## 5. Unsupported distortion by path (human labels)

Numerator = UNSUPPORTED_STATUS_DISTORTION; denominator = items the annotator
calls PRESERVED.

| Path | A | B |
|---|---:|---:|
| PEEK | 0/10 | 0/10 |
| PARA | 0/10 | 0/10 |
| S1 | 1/10 | 0/10 |
| S2 | 0/10 | 0/9 |
| TEMP1 | 2/9 | 1/10 |
| TEMP2 | 1/8 | 0/10 |

As in the V3 calibration, the deterministic cue gradient (PEEK best, TEMP
worst) is **not reproduced as unsupported distortion** in human labels. Most
deterministic “ABSENT” cases remain STATUS_OMISSION. TEMP1 is the only path
where both annotators see any unsupported distortion (1–2 cases).

## 6. Interpretation and gate verdict

1. **V3.1 fixes the applicability failure.** Primary-dimension agreement rose
   from 0.40/0.60 raw applicability in V3 to κ 0.853; overall primary-judgment
   κ rose from 0.578 to 0.728. The two-step judgment and collapsed labels are
   usable for epistemic and intentional items.
2. **Conditional is not yet usable.** κ 0.126 on 18 conditional items; 5 of the
   9 primary-judgment disagreements are conditional. This is a guide problem,
   not a sampling artifact: the same rule is being applied two ways.
3. **The outcome claim must include omission.** With unsupported distortion at
   1–4/60 and omission at 18/60, a confirmatory study powered on unsupported
   distortion alone is not feasible with this template family. The joint
   outcome distribution (including omission) remains the primary estimand.
4. **Gate verdict: partial pass.**
   - Epistemic and intentional: acceptable (κ 0.788, 0.904).
   - Conditional: **FAIL** (κ 0.126).
   - Overall primary κ 0.728 meets a “substantial” (≥0.70) threshold but not a
     strict ≥0.80 threshold. The protocol does not yet state which threshold
     governs; record it before the next calibration.
   Do **not** freeze the full guide or begin P2 confirmatory generation.
5. **Path-dependence claim is narrowed.** Human labels support cue/omission
   divergence, not an unsupported-distortion gradient. Any path-dependence
   claim must be stated over the joint outcome (omission + distortion).

## 7. Provenance and integrity caveat

The repository does not record who or what produced A and B. File-level
inspection:

- both files are complete and schema-valid;
- A's rationales cite rules “R1/R2” that are not in the current v3.1 guide,
  and A repeats identical rationale templates (up to 5 identical entries);
- B's rationales are independently worded (mean pairwise string similarity
  0.267; 0/60 identical).

This is consistent with two different labeling processes, but **independence
and human status are unverified**. Because the project previously withdrew a
gold-derived annotator B, record the annotator source before citing these
numbers as human inter-annotator reliability. If either file is model-generated,
label this result “model-assisted calibration” and do not use it as the human
reliability gate.

## 8. Required next actions

1. Record annotator provenance (identity or model, procedure, date) in the
   curator-only key; confirm A and B are independent.
2. Adjudicate the 9 primary-judgment, 4 identity, and 6 dimension
   disagreements with a third reviewer; preserve original labels separately.
3. Revise the V3.1 conditional rules: separate prerequisite state from action
   state, and give positive/negative examples for memories that juxtapose a
   satisfied condition with the action. Decide explicitly whether juxtaposition
   asserts action commitment.
4. Re-calibrate the conditional subset (or a new balanced 60-item set with more
   updated conditional cases) against the stated κ threshold.
5. Only then freeze the guide/ontology and proceed to P2.
