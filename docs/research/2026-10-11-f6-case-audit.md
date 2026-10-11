# 2026-10-11 — F6 case-level audit of LoCoMo-Refined n=50

## Purpose

Audit the 19 cases initially classified as `F6_REASONING` after the temporal scorer timestamp fix.

The goal is to separate genuine downstream reasoning failures from answer-scorer artifacts and evidence-gate problems.

## Audit source

The audit used the generated `experiments.audit_f6_cases` report over the existing `comparison.jsonl`. No new model calls were made during this classification.

## Result

The 19 initial F6 candidates split into three groups:

| Classification | Cases | Count |
|---|---|---:|
| Answer-scorer artifact / scoring-rule gap | q0000, q0005, q0009, q0011, q0014, q0015, q0017, q0018, q0020, q0027, q0031, q0039, q0040, q0043, q0044, q0048 | 16 |
| Confirmed reasoning-failure candidates | q0034, q0035 | 2 |
| Evidence-gate candidate requiring correction | q0037 | 1 |

Thus the raw `F6_REASONING=19` count should **not** be reported as 19 confirmed reasoning failures.

## Detailed findings

### Clear scorer artifacts / rule gaps

- **q0000** — `Yesterday.` is correct. Oracle Memory/Context already score it as temporally equivalent; Real Memory scoring lacks the timestamp anchor. This is an answer-scoring context-anchor problem, not a reasoning failure.
- **q0005** — `Last Saturday.` is semantically correct for 25 May 2023 → 20 May 2023, but both Oracle modes score false. The weekday-relative temporal scorer lacks this equivalence in the current implementation.
- **q0009** — `Last week.` is semantically equivalent to the reference interval May 29–June 4, 2023, but Oracle scoring returns false. Week-relative interval handling is incomplete.
- **q0011** — `her home country` is supported by the two Gold Evidence items and resolves to Sweden; Oracle answers `Sweden` and scores true. The Real Memory answer is a valid semantic paraphrase but token-F1/EM does not recognize it.
- **q0014** — `Yesterday.` correctly maps from 3 July to 2 July; Oracle scores true.
- **q0015** — `This month.` correctly maps from 3 July to July 2023; Oracle scores true.
- **q0017** — `Yesterday.` correctly maps from 6 July to 5 July; Oracle scores true.
- **q0018** — `Last week.` is semantically equivalent to the reference week before 6 July 2023, but Oracle scoring returns false. Another week-relative interval rule gap.
- **q0020** — `Two days ago.` correctly maps from 12 July to 10 July, but Oracle scoring returns false. Multi-day relative-date handling is incomplete.
- **q0027** — `Last weekend.` correctly maps to July 15–16 before 17 July, but Oracle scoring returns false.
- **q0031** — `Last Tuesday.` correctly maps to July 18 before 20 July, but Oracle scoring returns false.
- **q0039** — `This week.` correctly maps to the week containing 23 August 2023; Oracle scores true.
- **q0040** — `Last week.` correctly maps to the week before 23 August, but Oracle scoring returns false.
- **q0043** — `Last week.` correctly maps to the week before 25 August, but Oracle scoring returns false.
- **q0044** — `Yesterday.` correctly maps from 25 August to 24 August; Oracle scores true.
- **q0048** — `Next month.` correctly maps from 28 August to September 2023; Oracle scores true.

### Confirmed reasoning-failure candidates

- **q0034** — Oracle Memory and Oracle Context both answer `August 31.` while the evidence/reference requires August 11, 2023 (`last Friday` before August 14). The complete evidence reaches context, so the error survives retrieval/context controls and is a genuine downstream answer/reasoning failure candidate.
- **q0035** — Oracle Memory and Oracle Context both answer `No.` while Gold Evidence supports that Melanie is an ally/supportive of the transgender community. The evidence is complete and the semantic gate says sufficient. This is a genuine downstream reasoning/answer interpretation failure candidate.

### Evidence-gate issue

- **q0037** — The question asks when Caroline and Melanie went to a Pride festival together; reference is 2022. The evidence only says `We had a blast last year at the Pride fest` and does not establish the explicit year or the requested joint attendance strongly enough. The gate reports `sufficient`, but its own reason says the evidence does not specify 2022 or that they attended together. This is an evidence-sufficiency contradiction and should be treated as an E0/gate candidate, not F6.

## Revised interpretation

The current 19-case F6 bucket should be decomposed as:

- **2/19 confirmed F6 reasoning candidates (10.5%)**
- **16/19 scorer/rule artifacts (84.2%)**
- **1/19 evidence-gate candidate (5.3%)**

Within the full n=50 sample, this suggests that the previously reported `F6=19/50` substantially overstates downstream reasoning failures under the current scoring protocol.

A provisional corrected count would be:

- confirmed F6 reasoning: **2/50 (4%)**
- E0/gate candidate: **1/50 (2%)**
- scorer artifacts/rule gaps among the original F6 bucket: **16/50 (32%)**

These corrected figures are **audit classifications**, not yet the final experiment summary, because the scorer should be fixed and the n=50 experiment rerun before final quantitative claims.

## Next engineering actions

1. Extend temporal answer scoring for:
   - `last Saturday`
   - `last/next weekday`
   - `last week`
   - `last weekend`
   - `two days ago`
   - month/week interval equivalence
2. Add semantic equivalence handling for concise paraphrases such as `her home country` → `Sweden` when the supplied context explicitly resolves the entity.
3. Strengthen the evidence-gate contradiction detector for reasons such as `does not specify` / `does not establish` so q0037 cannot be marked sufficient while its explanation says the requested fact is unsupported.
4. Add regression tests for q0005/q0009/q0018/q0020/q0027/q0031/q0034/q0035/q0037-style cases.
5. Rerun n=50 after these fixes; only then scale to n=100/n=500.

## Methodological conclusion

The audit confirms that attribution must be performed only after validating the answer scorer and evidence gate. The initial F6 count was an upper bound produced by an imperfect evaluator, not a direct measurement of reasoning failure prevalence.
