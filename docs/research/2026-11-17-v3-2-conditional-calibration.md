# V3.2.1 Conditional Calibration Result (2026-11-17)

**Set:** `results/status_drift_v2_pilot/v3_path_pilot_p1c/annotation_v32/`
**Items:** 60 conditional (5 updated + 5 stable trajectories × 6 paths;
30 `CONDITION_SATISFIED` / 30 `CONDITION_ACTIVE`).
**Files:** `annotator_A.csv`, `annotator_B.csv`, complete and schema-valid.
**Adjudication record:** `annotation_v32/adjudication.csv`.
**Adjudicator:** `claude-sonnet-4.6`, model third-reviewer simulation; not human.
**Provenance:** annotator-unspecified per maintainer decision (2026-11-17).
**Status:** calibration only; not a confirmatory result.

## 1. Validation

`experiments.check_v3_annotations` reports **0 missing required fields and 0
invalid values** for A and B.

## 2. Agreement

| Field | n | Raw | Cohen's κ |
|---|---:|---:|---:|
| proposition_identity | 60 | 0.733 | 0.378 |
| primary_dimension | 60 | 1.000 | 1.000 |
| status_expressed | 60 | 0.983 | 0.959 |
| expressed_status | 60 | 0.983 | 0.974 |
| **action_status** | **60** | **1.000** | **1.000** |
| evidence_support | 60 | 0.800 | 0.437 |
| **primary_judgment** | **60** | **0.733** | **0.550** |
| confidence | 60 | 0.733 | 0.220 |

All 60 items are conditional, so the conditional dimension κ is 0.550.

## 3. Gate verdict

**FAIL.** Primary-judgment κ 0.550 is below the pre-registered 0.80 overall and
0.70 per-dimension threshold. Do not freeze the guide and do not begin P2.

But the failure is localized:

- **Conditional state and action state are reliable.** `action_status` is
  60/60 identical (κ 1.000); `expressed_status` is 59/60 (κ 0.974);
  `primary_dimension` is 60/60.
- **The new field captured the target phenomenon.** Both annotators
  independently labeled `V32C-0020` (`已获奖学金，开始学日语`) as
  `CONDITION_SATISFIED` + `COMMITTED`, `NOT_SUPPORTED`,
  `UNSUPPORTED_STATUS_DISTORTION`, subtype `CONDITIONAL_COLLAPSE`. This is the
  conditional collapse the condition-only form would have missed.
- **Proposition identity is the sole blocker.** 16 disagreements: A
  `PRESERVED` vs B `PARTIAL` on 15 items, and A `PRESERVED` vs B `AMBIGUOUS`
  on one. Evidence support has 12 disagreements, all downstream of the same
  rule.

## 4. Diagnosis: identity rule not operationalized

A applies a **topic-level** standard: if the target's object/topic is present
(`海外交换`, `马拉松`, `研究生`), A calls the proposition preserved. B applies
the **head-predicate + object** standard: `暂不考虑海外交换` lacks `申请`;
`读研` is not `申请研究生`; `奖学金申请` loses the object `研究生`. The v3.2.1
guide states "target predicate plus essential arguments" but gives no
operational test, so A and B applied different readings.

Representative cases:

| Memory | Target | A | B | Correct under predicate+object |
|---|---|---|---|---|
| `暂不考虑海外交换` | 申请海外交换 | PRESERVED | PARTIAL | PARTIAL: head verb `申请` absent |
| `暂不读研` | 申请研究生 | PRESERVED | PARTIAL | PARTIAL: `读研` is a different action |
| `奖学金申请` | 申请研究生 | PRESERVED | PARTIAL | PARTIAL: object `研究生` lost |
| `参赛` | 参加数学建模比赛 | PRESERVED | PARTIAL | PARTIAL: specific object lost |
| `研究生申请奖学金` | 申请研究生 | PRESERVED | AMBIGUOUS | AMBIGUOUS: two parses |
| `买电脑` / `购电脑` | 购买电脑 | PRESERVED | PRESERVED | PRESERVED: direct predicate synonym |
| `学日语` | 开始学习日语 | PRESERVED | PRESERVED | PRESERVED: `开始` is aspect, not identity |

The evidence-support disagreements follow the same pattern. A records
`SUPPORTED_BY_DIALOGUE` when the dialogue's final state is clear, even when the
memory expresses no status. B records `NOT_ASSESSABLE`. The guide does not say
that evidence support refers to the **expressed status**, not the proposition.

## 5. Adjudication

All disputed fields resolve in B's direction under the stated predicate+object
rule; the adjudication is therefore not independent evidence, but it confirms
that the disagreements are rule-application differences rather than sampling
noise.

Adjudicated distribution (n=60):

| Field | Distribution |
|---|---|
| proposition_identity | PRESERVED 36, PARTIAL 23, AMBIGUOUS 1 |
| primary_judgment | NO_DISTORTION 30, PROPOSITION_LOSS 23, STATUS_OMISSION 5, UNSUPPORTED_STATUS_DISTORTION 1, AMBIGUOUS_UNASSESSABLE 1 |
| action_status | NOT_PURSUING 28, NOT_EXPRESSED 21, CONSIDERING 10, COMMITTED 1 |

Agreement with adjudication:

| Field | A raw / κ | B raw / κ |
|---|---|---|
| proposition_identity | 0.733 / 0.378 | 1.000 / 1.000 |
| evidence_support | 0.800 / 0.437 | 1.000 / 1.000 |
| primary_judgment | 0.733 / 0.550 | 1.000 / 1.000 |
| action_status | 1.000 / 1.000 | 1.000 / 1.000 |
| expressed_status | 0.983 / 0.974 | 1.000 / 1.000 |

## 6. Consequences

1. **Do not freeze the guide; do not start P2.** The primary outcome depends on
   proposition identity, and identity is not yet reproducible.
2. **Do not discard the conditional instrument.** `primary_dimension`,
   `expressed_status`, and `action_status` are reliable and should be retained.
3. **The strict identity rule implies a high proposition-loss rate.** 23/60
   (38%) are PARTIAL under predicate+object. The joint outcome must report
   proposition loss separately; status analyses are conditioned on the 36
   PRESERVED items.
4. **The one distortion case is real and agreed.** `V32C-0020` is a clean
   conditional collapse under both annotators.

## 7. Required next actions

1. Revise the guide to v3.2.2 with an **identity worksheet**: write the target
   head predicate and object, locate both in the memory, allow direct synonyms,
   and treat a noun topic, a different verb, or a broader/different object as
   `PARTIAL`.
2. Define `evidence_support` as support for the **expressed status**; if no
   status is expressed, use `NOT_ASSESSABLE`.
3. Re-annotate `proposition_identity`, `primary_judgment`, and
   `evidence_support` on the same 60 items (condition/action fields can be
   retained, since they passed). Recompute κ against the same thresholds.
4. If identity κ ≥ 0.70 and primary κ ≥ 0.80, freeze and proceed to P2. If not,
   simplify the identity ontology (e.g. PRESERVED vs not-PRESERVED) before
   another confirmatory attempt.

## 8. Re-annotation under v3.2.2 (2026-11-17)

The same two annotators re-labeled `proposition_identity`, `primary_judgment`,
and `evidence_support` on the same 60 items; condition/action fields were
retained. Both files validate with 0 missing and 0 invalid values.

| Field | n | Raw | Cohen's κ |
|---|---:|---:|---:|
| proposition_identity | 60 | 0.917 | **0.837** |
| primary_dimension | 60 | 1.000 | 1.000 |
| status_expressed | 60 | 0.983 | 0.959 |
| expressed_status | 60 | 0.983 | 0.974 |
| action_status | 60 | 1.000 | 1.000 |
| evidence_support | 60 | 0.983 | 0.961 |
| **primary_judgment** | **60** | **0.900** | **0.827** |
| confidence | 60 | 0.733 | 0.220 |

**Gate: PASS.** Primary κ 0.827 ≥ 0.80 and identity κ 0.837 ≥ 0.70; all
conditional subfields exceed 0.70. The v3.2.2 identity worksheet fixed the
topic-level reading.

Seven residual disagreements remain, all rule boundaries:

- five `去上海工作` items where memory says `上海工作待定` / `瞄准上海工作`
  (A `PRESERVED`, B `PARTIAL`);
- one `AMBIGUOUS` identity item (V32C-0055) where A scored `STATUS_OMISSION`
  instead of `AMBIGUOUS_UNASSESSABLE`;
- one `已达标` condition cue (V32C-0041) where A used `UNKNOWN`.

v3.2.3 clarifies all three: serial-verb targets use the final action as the
head predicate; `AMBIGUOUS` identity preempts status; a generic satisfaction
cue counts only with a single explicit prerequisite. These clarifications were
added after observing the residual boundary, so they are not part of the
observed κ. Adjudication of the seven items (`adjudication_round2.csv`,
model-assisted) resolves five toward A and two toward B.

Adjudicated distribution (n=60):

| Label | n |
|---|---:|
| PROPOSITION_LOSS | 31 |
| NO_DISTORTION | 22 |
| STATUS_OMISSION | 5 |
| UNSUPPORTED_STATUS_DISTORTION | 1 |
| AMBIGUOUS_UNASSESSABLE | 1 |

Proposition loss remains high (31/60, 52%) even after the serial-verb
correction; status analyses are conditioned on the 28 `PRESERVED` items.

**Recommendation:** freeze v3.2.3 with the serial-verb and ambiguity
clarifications and proceed to P2. Before P2 generation, recheck the seven
adjudicated items under v3.2.3 if a clean observed agreement is required.
