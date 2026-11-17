# V3.1 Annotation Adjudication and Rule Revision (2026-11-17)

**Set:** `results/status_drift_v2_pilot/v3_path_pilot_p1c/annotation_v31/`
**Items:** 60 (10 trajectories × 6 paths), blind, condition key outside the repo.
**Files:** `annotator_A.csv`, `annotator_B.csv` — declared final by the
maintainer on 2026-11-17. Original files are unchanged.
**Adjudication record:** `annotation_v31/adjudication.csv`.
**Adjudicator:** `claude-sonnet-4.6`, used as a **model third-reviewer
simulation**. This is *not* a human adjudicator and cannot be cited as human
reliability. It is a rule-consistency audit used to revise the guide.
**Status:** calibration only; not a confirmatory result.

## 1. Agreement before adjudication

Reproduced by `experiments.check_v3_annotations`:

| Field | n | Raw | Cohen's κ |
|---|---:|---:|---:|
| proposition_identity | 60 | 0.933 | −0.026 |
| primary_dimension | 60 | 0.900 | 0.853 |
| status_expressed | 60 | 0.967 | 0.928 |
| expressed_status | 54 | 0.963 | 0.954 |
| evidence_support | 60 | 0.917 | 0.840 |
| **primary_judgment** | **60** | **0.850** | **0.728** |
| confidence | 60 | 0.833 | 0.536 |

By dimension: epistemic κ 0.788; intentional κ 0.904; **conditional κ 0.126**.
The conditional failure is the blocking issue.

## 2. Disagreement inventory

| Field | Disagreements |
|---|---:|
| primary_judgment | 9 |
| primary_dimension | 6 |
| expressed_status | 8 |
| evidence_support | 5 |
| proposition_identity | 4 |
| subtype | 5 |
| status_expressed | 2 |
| confidence | 10 |

The 9 primary-judgment pairs:

| Item | A | B |
|---|---|---|
| V3C-0003 | UNSUPPORTED_STATUS_DISTORTION | NO_DISTORTION |
| V3C-0008 | AMBIGUOUS_UNASSESSABLE | STATUS_OMISSION |
| V3C-0012 | PROPOSITION_LOSS | STATUS_OMISSION |
| V3C-0013 | STATUS_OMISSION | PROPOSITION_LOSS |
| V3C-0014 | LEGITIMATE_UPDATE | NO_DISTORTION |
| V3C-0022 | STATUS_OMISSION | NO_DISTORTION |
| V3C-0033 | LEGITIMATE_UPDATE | NO_DISTORTION |
| V3C-0053 | UNSUPPORTED_STATUS_DISTORTION | NO_DISTORTION |
| V3C-0058 | UNSUPPORTED_STATUS_DISTORTION | NO_DISTORTION |

Five of the nine are conditional; four of those are updated
(`CONDITION_SATISFIED`) items.

## 3. Diagnosed guide defects

The disagreements are not random. They trace to four defects in the v3.1 guide:

1. **Proposition identity included the condition relation.** §3.A said the
   condition-to-action relation is part of the proposition, while the formal
   definitions (§2, §3) treat the condition as a state dimension. This made
   A and B split on `买电脑→…` (V3C-0013) and on topic labels (V3C-0008,
   V3C-0012, V3C-0035).
2. **`LEGITIMATE_UPDATE` was unreachable.** In the v3.1 decision order,
   `NO_DISTORTION` was checked before `LEGITIMATE_UPDATE`. Any memory whose
   final state matched therefore returned `NO_DISTORTION` even when it
   represented the change as a change. This produced V3C-0014 and V3C-0033.
3. **No explicit-cue rule for status expression.** A treated an unmarked action
   verb (`购电脑`, `购机`) as a commitment assertion; B treated juxtaposition
   as condition satisfaction. Both are defensible under v3.1, which made the
   conditional items unstable (V3C-0003, V3C-0022, V3C-0053, V3C-0058).
4. **"Materially `PARTIAL`" was undefined.** A scored some `PARTIAL` items as
   `STATUS_OMISSION`; B scored one as `PROPOSITION_LOSS`. The boundary moved
   per item.

## 4. Adjudicated labels

Rule IDs: **R1** explicit-cue rule; **R2** proposition unit; **R3** update
ordering; **R4** ambiguity; **R5** subtype precedence.

| Item | Dimension | Identity | Status | Judgment | Rule |
|---|---|---|---|---|---|
| V3C-0003 | CONDITIONAL | PRESERVED | CONDITION_SATISFIED | NO_DISTORTION | R1: `获奖学金` is an explicit satisfaction cue; `购电脑` is not an action-state cue |
| V3C-0008 | EPISTEMIC | PARTIAL | NOT_EXPRESSED | PROPOSITION_LOSS | R2: bare topic `上海工作` lacks predicate `去` |
| V3C-0012 | EPISTEMIC | PARTIAL | NOT_EXPRESSED | PROPOSITION_LOSS | R2: `电脑调整` lacks predicate `购买` |
| V3C-0013 | CONDITIONAL | PRESERVED | NOT_EXPRESSED | STATUS_OMISSION | R2: `买电脑` preserves predicate+object; condition relation is state, not identity |
| V3C-0014 | INTENTIONAL | PRESERVED | COMMITTED | LEGITIMATE_UPDATE | R3: ordered chain retains `计划` and `决定` |
| V3C-0022 | CONDITIONAL | PRESERVED | NOT_EXPRESSED | STATUS_OMISSION | R1: `奖学金` noun has no acquisition cue |
| V3C-0033 | EPISTEMIC | PRESERVED | ESTABLISHED | LEGITIMATE_UPDATE | R3: chain retains `计划` and `确认` |
| V3C-0035 | EPISTEMIC | PARTIAL | NOT_EXPRESSED | PROPOSITION_LOSS | R2: `上海工作：` label lacks predicate `去` |
| V3C-0040 | CANNOT_DETERMINE | PRESERVED | UNRECOVERABLE | AMBIGUOUS_UNASSESSABLE | R4: `决策前后购电脑` supports opposite readings |
| V3C-0044 | EPISTEMIC | PRESERVED | POSSIBLE | UNSUPPORTED_STATUS_DISTORTION | R5: superseded state represented as current → TEMPORAL, not ATTENUATION |
| V3C-0053 | CONDITIONAL | PRESERVED | NOT_EXPRESSED | STATUS_OMISSION | R1: `奖学金` noun has no acquisition cue |
| V3C-0058 | CONDITIONAL | PRESERVED | NOT_EXPRESSED | STATUS_OMISSION | R1: `奖学金` noun has no acquisition cue |

The adjudication also fixed the four identity, six dimension, two
status-expressed, five evidence-support, and five subtype disagreements; see
`adjudication.csv` for field-level values.

## 5. Adjudicated distribution and agreement

Adjudicated primary-judgment distribution (n=60):

| Label | n |
|---|---:|
| NO_DISTORTION | 34 |
| STATUS_OMISSION | 19 |
| PROPOSITION_LOSS | 3 |
| LEGITIMATE_UPDATE | 2 |
| AMBIGUOUS_UNASSESSABLE | 1 |
| UNSUPPORTED_STATUS_DISTORTION | 1 |

Agreement with the adjudicated labels:

| Field | A raw / κ | B raw / κ |
|---|---|---|
| proposition_identity | 1.000 / 1.000 | 0.933 / −0.026 |
| primary_dimension | 0.917 / 0.878 | 0.983 / 0.975 |
| primary_judgment | 0.917 / 0.859 | 0.850 / 0.720 |

A is closer to the revised-rule adjudication on the disputed conditional and
identity items, but neither annotator is "right" in the sense of human gold;
the exercise identifies rules that make the labels determinate.

## 6. Revised rules (v3.2)

Written into `V3_ANNOTATION_GUIDELINES.md`,
`V3_ANNOTATION_HOWTO.md`, and `V3_FORMAL_DEFINITIONS.md` §12:

- **Proposition identity** = target predicate + essential arguments; modality,
  condition relation, and status are excluded. Any `PARTIAL` is scored
  `PROPOSITION_LOSS` in the primary outcome and reported separately.
- **Explicit-cue rule.** A status is expressed only with an explicit lexical
  cue. An unmarked action verb and a bare topic noun are not cues.
  `获奖学金购电脑` expresses condition satisfied but not action commitment;
  `奖学金购机` expresses neither.
- **Conditional scoring.** `expressed_status` records the condition state only;
  the action state, if explicitly cued, goes in `rationale`.
- **Update ordering.** `LEGITIMATE_UPDATE` is checked before `NO_DISTORTION`.
  An ordered chain retaining both old and new states counts as representing the
  change as a change; only the final state remains `NO_DISTORTION`.
- **Ambiguity.** `CANNOT_DETERMINE` is for memories supporting incompatible
  readings, not for `PARTIAL` identity.

Under these rules, all nine primary disagreements become determinate:
V3C-0003 → NO_DISTORTION; 0008/0012/0035 → PROPOSITION_LOSS; 0013/0022/0053/0058
→ STATUS_OMISSION; 0014/0033 → LEGITIMATE_UPDATE.

## 7. Provenance caveat

The maintainer has declared A and B final, but the repository still does not
record who or what produced them, their procedure, or their independence. A
previous B file was withdrawn because it was gold-derived. Until provenance is
recorded in the curator-only key, these numbers must be labeled
**annotator-unspecified calibration**, not human inter-annotator reliability.

## 8. Required next actions

1. Record annotator provenance (identity or model, procedure, date,
   independence) in the curator-only key.
2. Recalibrate on the v3.2 conditional-focused set
   (`annotation_v32/`, 60 items: 5 updated + 5 stable conditional
   trajectories × 6 paths), with the revised guide.
3. Pre-register the freeze threshold before annotation. Proposal: overall
   primary-judgment κ ≥ 0.80 and every dimension κ ≥ 0.70; conditional must
   reach κ ≥ 0.70 to be reportable and ≥ 0.80 to be frozen. This proposal
   requires sign-off.
4. If the conditional gate passes, freeze the guide and ontology, then proceed
   to P2 confirmatory generation. If it fails, revise the conditional rules
   again rather than dropping the dimension.
