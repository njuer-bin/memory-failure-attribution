# LoCoMo Five-Question Pilot: Blank Annotation Sheet

> **Use:** Complete independently by annotators A and B.  
> **Dataset:** LoCoMo, JSON category 1 (multi-hop).  
> **Source text:** Run experiments/prepare_locomo_annotation_packet.py to generate the local packet.  
> **Blinding:** Do not share labels or rationales with the other annotator until both sheets are locked.

## Annotator metadata

- Annotator ID:
- Date:
- Annotation codebook version: 0.1
- Dataset revision: snap-research/locomo@cbfbc1dba6bc53d00625212a0f22d55ffee7c1fc

## General instructions

For each question:
1. Verify the reference answer against the raw dialogue, not just the benchmark evidence list.
2. Split compound answers into atomic answer slots.
3. Split multi-fact turns into atomic evidence units.
4. Assign evidence role and necessity independently.
5. Perform remove-one counterfactual checks.
6. Draw only defensible dependency edges.
7. Mark uncertain or insufficient cases explicitly.

## Q1 — conv-26#qa[11]

**Question:** Where did Caroline move from 4 years ago?

**Reference answer:** Sweden

**Candidate evidence IDs:** D3:13, D4:3

- Evidence sufficiency: SUFFICIENT / PARTIAL / INSUFFICIENT / MISALIGNED / AMBIGUOUS / UNSCORABLE
- Answer slots:
- Atomic evidence units:
  - D3:13 — fact(s):
  - D4:3 — fact(s):
- Role per unit (DIRECT / BRIDGE / BACKGROUND / IRRELEVANT / MULTI_ROLE / UNCERTAIN):
- Necessity per unit (NECESSARY / REDUNDANT / OPTIONAL / DISTRACTOR / UNCERTAIN):
- Remove-one answerability per unit (YES / NO / UNCERTAIN):
- Alternative path(s):
- Dependency edges and rationale:
- Minimal sufficient evidence set(s):
- Confidence (1–5) and notes:

## Q2 — conv-41#qa[3]

**Question:** What type of volunteering have John and Maria both done?

**Reference answer:** Volunteering at a homeless shelter

**Candidate evidence IDs:** D3:5, D2:1

- Evidence sufficiency:
- Answer slots:
- Atomic evidence units:
  - D3:5 — fact(s):
  - D2:1 — fact(s):
- Role per unit:
- Necessity per unit:
- Remove-one answerability per unit:
- Alternative path(s):
- Dependency edges and rationale:
- Minimal sufficient evidence set(s):
- Confidence (1–5) and notes:

## Q3 — conv-42#qa[11]

**Question:** What is Joanna allergic to?

**Reference answer:** Most reptiles, animals with fur, cockroaches, dairy

**Candidate evidence IDs:** D4:4, D5:11, D2:23

**Pre-registered audit warning:** The dairy turn may establish avoidance/intolerance but not necessarily allergy. Do not silently equate these.

- Evidence sufficiency:
- Answer slots:
- Atomic evidence units:
  - D4:4 — fact(s):
  - D5:11 — fact(s):
  - D2:23 — fact(s):
- Role per unit:
- Necessity per unit:
- Remove-one answerability per unit:
- Alternative path(s):
- Dependency edges and rationale:
- Minimal sufficient evidence set(s):
- Confidence (1–5) and notes:

## Q4 — conv-43#qa[1]

**Question:** What are John's goals for his career that are not related to his basketball skills?

**Reference answer:** Get endorsements, build his brand, do charity work

**Candidate evidence IDs:** D6:15, D11:17

- Evidence sufficiency:
- Answer slots:
- Atomic evidence units:
  - D6:15 — fact(s):
  - D11:17 — fact(s):
- Role per unit:
- Necessity per unit:
- Remove-one answerability per unit:
- Alternative path(s):
- Dependency edges and rationale:
- Minimal sufficient evidence set(s):
- Confidence (1–5) and notes:

## Q5 — conv-44#qa[12]

**Question:** What outdoor activities has Andrew done other than hiking in nature?

**Reference answer:** Rock climbing, fishing, camping

**Candidate evidence IDs:** D8:1, D17:1, D14:1

- Evidence sufficiency:
- Answer slots:
- Atomic evidence units:
  - D8:1 — fact(s):
  - D17:1 — fact(s):
  - D14:1 — fact(s):
- Role per unit:
- Necessity per unit:
- Remove-one answerability per unit:
- Alternative path(s):
- Dependency edges and rationale:
- Minimal sufficient evidence set(s):
- Confidence (1–5) and notes:

## Completion checklist

- [ ] I used the raw dialogue text.
- [ ] I did not use world knowledge to fill gaps.
- [ ] I judged benchmark evidence sufficiency independently of model outputs.
- [ ] I separated role from necessity.
- [ ] I checked alternatives per answer slot.
- [ ] I marked uncertainty rather than forcing a label.
- [ ] I did not see the other annotator's labels.
- [ ] I saved a locked copy before adjudication.
