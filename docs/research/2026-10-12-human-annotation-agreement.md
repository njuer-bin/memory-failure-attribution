# Human Annotation Agreement Analysis

## Source

This analysis uses the completed 25-case human annotation file `human_annotation_completed_2026-10-12.csv` supplied by the researcher. The human labels in that file are treated as the ground truth for this audit.

This is a stratified evaluator-audit sample, not a prevalence estimate for the full LoCoMo benchmark.

## Final-label agreement

Sample size: **25**.

Automatic final labels in the sample:

- F1_FORMATION: 11
- E0_EVIDENCE_INSUFFICIENCY: 4
- F4_RETRIEVAL: 3
- F5_CONTEXT: 1
- NONE: 6
- F6_REASONING: 0

Human final labels:

- F1_FORMATION: 9
- E0_EVIDENCE_INSUFFICIENCY: 4
- F4_RETRIEVAL: 3
- F5_CONTEXT: 1
- EVAL: 3
- NONE: 5
- F6_REASONING: 0

Exact final-label agreement: **18/25 = 72.0%**.

Multi-class Cohen's kappa, treating EVAL as a distinct label: **0.628**.

This is substantial agreement for the audited sample, but not sufficient to claim that the evaluator is frozen because three cases were judged EVAL by the human annotator and several category confusions remain.

## Confusion matrix

Rows are automatic labels; columns are human labels.

| Auto → Human | E0 | EVAL | F1 | F4 | F5 | NONE |
|---|---:|---:|---:|---:|---:|---:|
| E0 | 3 | 0 | 1 | 0 | 0 | 0 |
| F1 | 0 | 3 | 7 | 1 | 0 | 0 |
| F4 | 0 | 0 | 1 | 2 | 0 | 0 |
| F5 | 0 | 0 | 0 | 0 | 1 | 0 |
| NONE | 1 | 0 | 0 | 0 | 0 | 5 |

The main disagreements are:

1. **Auto F1 -> Human EVAL: 3 cases.** These indicate uncertainty about the benchmark/evidence timing or evidence provenance and should not be treated as confirmed F1 failures.
2. **Auto E0 -> Human F1: 1 case.** This is a direct evidence-gate contradiction and is important for E0 validation.
3. **Auto F1 -> Human F4: 1 case.** This is a lifecycle attribution boundary error: the human adjudication places the first loss at retrieval/rerank rather than formation.
4. **Auto F4 -> Human F1: 1 case.** This is the reverse boundary error.
5. **Auto NONE -> Human E0: 1 case.** This shows that an answer that happened to be correct under the automatic scorer can still have insufficient Gold Evidence.

## Per-class performance

Using the human final label as ground truth:

| Class | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| F1_FORMATION | 7 | 4 | 2 | 63.6% | 77.8% | 70.0% |
| E0_EVIDENCE_INSUFFICIENCY | 3 | 1 | 1 | 75.0% | 75.0% | 75.0% |
| F4_RETRIEVAL | 2 | 1 | 1 | 66.7% | 66.7% | 66.7% |
| F5_CONTEXT | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| F6_REASONING | 0 | 0 | 0 | N/A | N/A | N/A |
| NONE | 5 | 1 | 0 | 83.3% | 100.0% | 90.9% |
| EVAL | 0 | 0 | 3 | 0.0% | 0.0% | 0.0% |

F6 has no positive human examples in this 25-case sample, so no F6 performance estimate is possible.

## Evidence sufficiency agreement

Automatic evidence sufficiency is derived from the automatic E0 label:

- auto E0 -> INSUFFICIENT
- all other automatic final labels -> SUFFICIENT

Human evidence-sufficiency labels contain three states: SUFFICIENT, INSUFFICIENT, UNCERTAIN.

Exact agreement over all 25 cases: **20/25 = 80.0%**.

If the three human UNCERTAIN cases are excluded, agreement is **20/22 = 90.9%**.

Treating UNCERTAIN as a separate category, the Cohen's kappa is **0.459**. This lower value reflects the fact that the automatic gate has no UNCERTAIN output while human adjudication explicitly permits uncertainty.

## Key research finding

The audit supports the general usefulness of the attribution framework, but exposes a specific evaluator weakness:

> The dominant remaining problem is not simply whether evidence is present; it is whether the evaluator can confidently determine evidence provenance and the earliest causal loss when benchmark timing/provenance is ambiguous.

The three human EVAL cases should therefore be treated as evaluator-uncertainty cases rather than forced into F1/F4/E0.

The audit also confirms that F4 must remain defined as **retrieval OR rerank**, because the human annotation explicitly contains cases where the available audit evidence is insufficient to safely distinguish those two internal stages.

## Implications for n>=100

Do not use the 72.0% agreement as a final benchmark-quality claim. The sample was intentionally stratified toward failure categories.

Before the final large-scale run:

1. Preserve EVAL as a first-class adjudication state.
2. Keep strict exact provenance for causal lifecycle attribution.
3. Keep F4 as retrieval-or-rerank at the top-level attribution layer unless exact stage evidence is available.
4. Revisit the four disagreement patterns above after provenance/timestamp inputs are frozen.
5. Only then run the larger benchmark and bootstrap confidence intervals.
