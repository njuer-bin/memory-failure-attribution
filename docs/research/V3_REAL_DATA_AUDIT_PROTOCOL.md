# Real-Dialogue Feasibility Audit Protocol (Stage 1)

Status: candidate screening complete; human screening pending. This protocol
covers the feasibility audit only. It does not change the frozen V3 pilot and
does not authorize a confirmatory run.

## Purpose

Before committing to real-dialogue experiments, determine whether LoCoMo and
LongMemEval actually contain target propositions with identifiable epistemic,
intentional, or conditional status, enough original evidence to label that
status, and a later opportunity to observe whether the status survives
rewriting.

## Data sources

- LoCoMo-Refined public split: 10 conversations, 19 sessions each, casual
  two-speaker dialogue.
- LongMemEval oracle: 500 question instances, 3-session haystacks; question
  types include knowledge-update (78), multi-session (133), temporal-reasoning
  (133), single-session (156).

The unit of analysis is a **target proposition**: a sentence (or clause) about
the speaker's own state, action, or condition, with its original evidence span
and the session in which it occurs.

## Candidate generation

`experiments/v3_real_feasibility_audit.py` is a rule-based generator, not a
measurement instrument. It:

1. splits messages into sentences and keeps first-person, non-question
   sentences of at least six words;
2. matches broad marker families (epistemic, intentional, conditional);
3. scores specificity (concrete action, time expression, potential update,
   later mention) and penalizes vague, procedural, advice, and past-evaluation
   phrasing;
4. keeps sentences scoring >= 4;
5. selects a 50-item screening set balanced by dataset and marker dimension,
   with at most two items per source and near-duplicate suppression.

Outputs: `results/status_drift_v3_real_audit/` (`candidates.csv`,
`screening_50.csv`, `screening_A.csv`, `screening_B.csv`,
`analysis/feasibility_summary.json`).

Automated matches over-generate. Precision, evidence sufficiency, and
labelability are established only by the human screening columns.

## Screening fields

| Field | Values | Meaning |
|---|---|---|
| `status_bearing` | yes / ambiguous / no | Does the span express a determinable status for a specific proposition? |
| `dimension` | epistemic / intentional / conditional / mixed / none | Semantic primary dimension, not the matched marker. |
| `proposition_clear` | yes / no | Can the target proposition be stated as one claim? |
| `evidence_sufficient` | yes / partial / no | Does the source span let a labeler assign a gold status and later check preservation? |
| `lexical_cue_present` | yes / no | Is there an explicit status expression in the source? |
| `lexical_labelable` | yes / no | Can a lexical status-cue metric be defined for this item? |
| `semantic_labelable` | yes / no | Can a careful reader assign the status from meaning, even if wording changes? |
| `update_present` | yes / no / unknown | Does a later session change the status of the same proposition? |
| `difficulty_1_3` | 1 / 2 / 3 | Requested judgment effort for a trained annotator. |
| `notes` | free text | Boundary cases and ambiguity source. |

A model diagnostic read is stored separately in `diagnostic_read.csv` and is
**not** an annotator label. It must never be reported as human annotation.

## Two fidelity metrics (frozen for Stage 2)

### Lexical Status Fidelity (LSF)

Given transformed memory M, source evidence E, and target proposition P:
does M contain an explicit status expression for P whose type matches the
status justified by E?

- `CUE_PRESERVED` — same cue or a pre-listed equivalent.
- `CUE_ALTERED` — explicit cue present but a different status type.
- `CUE_ABSENT` — no explicit status expression for P.
- `NOT_APPLICABLE` — source itself had no explicit cue.

### Semantic Status Fidelity (SSF)

Given M (with E available for adjudication), can an annotator assign the status
that E justifies for P?

- `SEMANTIC_CORRECT` — assigned status matches E.
- `SEMANTIC_DISTORTED` — assigned status contradicts E.
- `SEMANTIC_UNDERSPECIFIED` — M permits the correct status but does not
  determine it.
- `UNASSESSABLE` — P is lost or E is insufficient.

Rules:

- `CUE_ABSENT` is not automatically `SEMANTIC_DISTORTED`; a paraphrase without
  the cue can still preserve the status.
- `SEMANTIC_DISTORTED` requires evidence contradicting the assigned status,
  not merely a missing cue.
- Report LSF and SSF as separate outcomes with separate denominators.

## Annotation procedure

- Two independent annotators label the same 50 items blind to each other, to
  condition, and to any gold label.
- Each annotator writes their own copy (`screening_A.csv`, `screening_B.csv`);
  provenance (person or tool, date) is recorded in the file header or an
  accompanying note.
- Disagreements are resolved by the pre-registered order below, not ad hoc:
  1. proposition identity (can both annotators state the same P?);
  2. evidence span sufficiency;
  3. status type;
  4. status strength.
- Model assistance is allowed for candidate generation and for a flagged
  second opinion, but a model-assisted resolution is recorded as such and is
  never described as independent human adjudication.
- Report raw agreement and Cohen's kappa per field; kappa is
  prevalence-sensitive, so report raw agreement alongside it.

## Decision gates for Stage 2

Evaluated after human adjudication, not on the model diagnostic:

1. **Status-bearing yield:** >= 35/50.
2. **Semantic labelability:** >= 30/50.
3. **Dimension coverage:** >= 8 semantic-labelable items per dimension that
   will be used. If epistemic falls below 8, do not run a three-dimension
   confirmatory design on real dialogue; either drop epistemic or add targeted
   elicitation.
4. **Update opportunity:** >= 25/50 with a later-session mention of the same
   proposition.
5. **Downstream relevance:** >= 10/50 clearly consequential. If not met, P4.2
   must construct curated high-stakes scenarios rather than sample them.

Failure of a gate changes the design (targeted sampling, different dataset, or
a narrower dimension set); it is not a reason to relax the gate.

## Sampling caveat

The 50 items are top-scored by the rule-based generator, so precision here is
an upper bound for this screening rule, not the prevalence of status-bearing
propositions in the datasets. Prevalence requires a random sample and is out of
scope for Stage 1.

## Related artifacts

- Candidate generator: `experiments/v3_real_feasibility_audit.py`
- Run report: `docs/research/2026-11-17-real-dialogue-feasibility-audit.md`
- Frozen V3 pilot: `docs/research/V3_FINAL_FREEZE.md`
