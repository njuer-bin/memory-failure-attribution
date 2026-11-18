# Adjudication — Three Boundary Items

A third person (not annotator A or B) resolves the three items where the
dimension labels disagree. This is an adjudication, not a re-annotation of the
40-item set.

## Files

- `adjudication_sheet.csv` — the only file to fill.
- Do not open `annotator_A.csv`, `annotator_B.csv`, the composition key, or the
  raw source corpora. The two labels are already shown in the sheet.

## What to fill

For each of the three rows, read `target_sentence` and `context`, then apply
`V3_REAL_STAGE2_DRAFT.md` v2.3 §8c-§8d. Fill:

| Column | Values |
|---|---|
| `adjudicated_dimension` | epistemic / intentional / mixed / E0 |
| `adjudicated_status` | epistemic: UNKNOWN/POSSIBLE/PROBABLE/SUPPORTED/ESTABLISHED/REJECTED; intentional: NOT_EXPRESSED/CONSIDERING/INTERESTED/INTENDING/COMMITTED/EXECUTING/COMPLETED/CANCELLED/NOT_INTENDED; E0: `N/A` |
| `adjudicated_strength` | weak / moderate / strong / N/A |
| `adjudicated_condition_state` | `N/A` for all three (no conditional items) |
| `adjudicated_action_state` | `N/A` for all three |
| `rationale` | one sentence: the rule you applied and why |

No blanks. No model assistance. Time: 10-15 minutes.

## The three items

1. `S2IE-003` — an instruction to the assistant ("I will provide ... it will be
   your job to write up ..."). v2.3 §8d: instructions to the assistant are
   `E0`, not the speaker's own status.
2. `S2IE-021` — "I think about my life too sometimes ... felt like writing a
   drama." v2.3 §8d: past/emotional musing is `E0` unless it states a current or
   future action/status.
3. `S2IE-025` — "I think I've managed to make it work with dogs while still
   living in the city." v2.3 §8d: intentional `COMPLETED` if the item is the
   speaker's action; epistemic `SUPPORTED`/`ESTABLISHED` if it is a factual
   claim about a state. If both, code the action and note the fact.

## After completion

Return `adjudication_sheet.csv`. The analysis will report the unadjudicated
result (raw 0.925 / κ 0.639 for dimension; raw 0.900 / κ 0.875 for status) and
the adjudicated result side by side. Original A/B labels are preserved.
