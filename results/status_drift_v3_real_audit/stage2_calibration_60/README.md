# Stage 2 Calibration Set (60 items)

Purpose: test whether two annotators can apply the Stage 2 v2 gold-coding
guide to real dialogue with acceptable agreement before any confirmatory
generation.

## Files

- `annotator_A.csv`, `annotator_B.csv` — one sheet per annotator; fill only the
  ten gold fields. Do not edit the dialogue columns.
- `sheet.csv` — identical reference copy.
- `provenance_template.json` — copy to `provenance_A.json` / `provenance_B.json`
  and fill.
- Composition, proposed stratum, and boundary/cue flags are **outside the
  repository** in `G:/memory_failure_backup/stage2_calibration_key_2026-11-18.csv`.
  Do not open it before finishing.

Do not open the other annotator's file. Do not open the 50-item screening
labels or the P4.2 files.

## Composition (60 items)

- 30 LoCoMo intentional propositions (heuristic split: considering/intending
  vs committed/completed; the split is provisional and lives in the key).
- 15 conditional propositions with judgeable condition and action states:
  5 LoCoMo, 5 longmemeval_s, 5 longmemeval oracle.
- 15 longmemeval_s non-conditional items (44-57 sessions).
- 11 boundary-flagged and 5 cue-mismatch items ("I think I'll", "I'll
  definitely") are included.

The final split is 35 LoCoMo and 25 longmemeval items (20 from
`longmemeval_s`, 5 from the oracle conditional arm).

**LoCoMo constraint.** The public LoCoMo-Refined split has only 10
conversations, and all 10 were used in the 50-item screening set. This
calibration set excludes the exact screening items by dialogue key but reuses
the conversations, so agreement may be mildly inflated. The `longmemeval_s`
instances are not used in the screening set. Record this deviation in the
Stage 2 freeze record; do not describe the set as conversation-disjoint.

The proposed stratum and flags are heuristic and are not gold labels. They are
kept out of the annotator sheet to avoid anchoring.

## What to fill

For each row, read `target_sentence` and `context` (the target turn is marked
`>>`), and `later_mention` when present. Fill:

| Field | Values |
|---|---|
| `target_proposition` | one testable claim about the speaker |
| `gold_dimension` | epistemic / intentional / conditional / mixed / E0 |
| `gold_status` | epistemic: UNKNOWN / POSSIBLE / PROBABLE / SUPPORTED / ESTABLISHED / REJECTED; intentional: NOT_EXPRESSED / CONSIDERING / INTERESTED / INTENDING / COMMITTED / EXECUTING / COMPLETED / CANCELLED / NOT_INTENDED; conditional: `N/A` (use the two state fields) |
| `gold_condition_state` | conditional only: UNKNOWN / ACTIVE_UNSATISFIED / SATISFIED / FAILED / WAIVED / NOT_APPLICABLE |
| `gold_action_state` | conditional only: NOT_EXPRESSED / CONSIDERING / INTENDING / COMMITTED / EXECUTING / COMPLETED / CANCELLED |
| `gold_strength` | weak / moderate / strong |
| `gold_confidence` | high / medium / low |
| `evidence_quote` | the minimal supporting quote |
| `update_history` | ordered earlier statuses, if any |
| `notes` | boundary reason, or empty |

If the evidence cannot support a status, use `gold_dimension=E0`, set
`gold_status=N/A`, and explain in `notes`; do not guess. No blanks in the other
fields.

### Decision order

1. Can you state the same proposition from `target_sentence` + `context`?
   If not, `gold_dimension=E0`.
2. Is the evidence sufficient to assign one status without guessing? If not,
   `E0` or `mixed` with a note; do not force a label.
3. Assign the dimension from **meaning**, not from the word that matched.
4. Assign the status and strength.
5. For conditional items, assign the condition state and the action state
   separately. A satisfied condition does not imply a committed action.
6. Record ambiguity in `notes` rather than selecting an arbitrary label.

### Boundary rules

- "I think I'll X" → intentional (hedged commitment), not epistemic.
- "I think X happened / X is true" → epistemic.
- "I hope to X" → INTENDING or CONSIDERING, not COMMITTED.
- "I'm going to X" → INTENDING or COMMITTED; context decides.
- "I booked / signed up / paid for X" → COMMITTED or COMPLETED.
- "Maybe X" → POSSIBLE (epistemic) or CONSIDERING (intentional) by the
  proposition type.
- "If X, I'll Y" → conditional; record condition state and action state.
- "just in case" → conditional backup; the action is conditional.
- Preferences, past evaluations, third-party states, questions → not the
  speaker's status.
- Negation ("I'm not going to X") → NOT_INTENDED, a status, not absence.
- Hypotheticals and quotes → exclude unless the speaker endorses them.
- Sarcasm or unresolved hedging → `mixed` or `E0` with a note.

Use the definitions, boundary rules, and decision order in
`docs/research/V3_REAL_STAGE2_DRAFT.md` §3-§8. The v2 corrections in §8a apply:
`lexical_labelable` requires the same status type, `update_present` has three
states, and `evidence_sufficient` distinguishes yes / partial / no.

Time: about 2-3 minutes per item, 2-3 hours total.

## What this set does not do

This is the **gold-coding** calibration. LSF/SSF calibration requires generated
memory variants `M` and is a separate sheet, produced after the gold labels are
frozen. Do not score LSF or SSF here.

## Gates

Proposed, to confirm before freezing:

| Field | Raw | Kappa |
|---|---:|---:|
| `proposition_identity` (from gold coding) | >= 0.90 | >= 0.80 |
| `gold_dimension` | >= 0.85 | >= 0.70 |
| `gold_status` | >= 0.85 | >= 0.70 |
| `lsf_outcome` (later sheet) | >= 0.85 | >= 0.70 |
| `ssf_outcome` (later sheet) | >= 0.80 | >= 0.65 |

If a gate fails, revise the guide and re-calibrate on a new item set; do not
reuse calibration items in the confirmatory set.
