# Model-Free Re-Annotation Subset (25 items)

Purpose: estimate how much the original annotator B was anchored by the AI
first draft. YTB re-annotates these 25 screening items from scratch, without
the draft, without the earlier A/B labels, and without the composition key.

## Files

- `annotator_YTB.csv` — the sheet to fill. One row per item; do not edit any
  column except the ten rating columns.
- `sheet.csv` — identical copy for reference.
- `provenance_YTB.json` — fill after completion.
- The mapping from `item_id` to the original screening `candidate_id` is
  **outside the repository** at
  `G:/memory_failure_backup/stage2_model_free_key_2026-11-18.csv`. Do not open
  it before finishing.

Do not open `screening_A.csv`, `screening_B.csv`, `diagnostic_read.csv`, or
`screening_50.csv`. They contain the earlier labels and would defeat the
purpose.

## What to do

Use `docs/research/REAL_SCREENING_ANNOTATION_HOWTO.md` for the ten fields, with
the v2 corrections in `V3_REAL_STAGE2_DRAFT.md` §8a:

- `lexical_labelable=yes` only when the cue rule would assign the **same status
  type** as the semantic dimension. A present but misleading cue is `no`.
- `update_present` has three states: `yes` (a later session changes the
  status), `no` (a later mention exists and the status is unchanged), `unknown`
  (no later mention is available). A re-mention is not an update.
- `evidence_sufficient`: `yes` (gold status assignable and comparable),
  `partial` (assignable but the comparison is weak), `no` (not assignable).
- A conditional risk statement with `if` is `conditional`, not `epistemic`.
- Past evaluation, preference, and self-encouragement are `none`.

### Fields

| Field | Values |
|---|---|
| `status_bearing` | yes / ambiguous / no |
| `dimension` | epistemic / intentional / conditional / mixed / none |
| `proposition_clear` | yes / no |
| `evidence_sufficient` | yes / partial / no |
| `lexical_cue_present` | yes / no (target sentence only) |
| `lexical_labelable` | yes / no (cue must match the semantic status type) |
| `semantic_labelable` | yes / no |
| `update_present` | yes / no / unknown |
| `difficulty_1_3` | 1 / 2 / 3 |
| `notes` | one line: P, assigned status, boundary reason |

### Decision order

1. Is there a specific proposition about the speaker's own action, state, or
   belief? If not, `status_bearing=no`, `dimension=none`,
   `proposition_clear=no`, `semantic_labelable=no`.
2. Can you state it as one testable claim? If not, `proposition_clear=no`.
3. Does the context let you assign a status without guessing? If not,
   `status_bearing=ambiguous` and `evidence_sufficient=partial` or `no`.
4. What is the semantic dimension? Ignore which word matched.
5. Is there an explicit cue in the **target sentence**? (`lexical_cue_present`)
6. Would the cue rule assign the **same status type**? (`lexical_labelable`)
   "I think I'll X" is intentional, but `I think` is canonically epistemic →
   `no`. "I'll definitely X" → `no`. "If X, I'll Y" → `yes`.
7. Could a human assign the status from meaning even if paraphrased?
   (`semantic_labelable`)
8. Is there a later mention? If yes, does it change the status? A mere
   re-mention is `no`, not `yes`; no later mention is `unknown`.
9. How hard was the call? (`difficulty_1_3`)

Work one row at a time: read `target_sentence`, then `context` (the target turn
is marked `>>`), then `later_mention` if present. Decide `status_bearing`
first; if `no`, set `dimension=none` and `proposition_clear=no`, and still fill
the remaining fields with the lowest defensible values. No blanks.

Time: about 1.5-2.5 minutes per item, 40-60 minutes total.

## Gates for using this subset

The subset estimates anchoring, not population reliability. Report:

- raw agreement and Cohen's kappa between YTB's new labels and the old
  `screening_B` labels on the same items;
- the same comparison against `screening_A` as a reference;
- the direction and size of any shift in `dimension`, `status_bearing`,
  `lexical_labelable`, and `update_present`.

If the new labels agree with B's old labels at the same level as A/B, the AI
draft did not materially anchor B; if they shift toward A, the old B labels
were draft-anchored and the earlier reliability estimate is inflated. Either
way, report the comparison as an anchoring sensitivity analysis, not as a new
two-human reliability estimate.
