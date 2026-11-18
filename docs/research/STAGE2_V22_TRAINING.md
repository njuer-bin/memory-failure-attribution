# Stage 2 v2.2 Training Examples (not data)

Use these eight examples in a 15-20 minute training pass before the next
calibration. Each annotator labels them independently, then the pair compares
and discusses only these examples. **Do not include them in any calibration or
confirmatory set.**

| # | Sentence | Dimension | Status | Strength | Why |
|---|---|---|---|---|---|
| 1 | "I think I'll go with the fruit chaat." | intentional | `INTENDING` | moderate | "I think I'll" is hedged; not `COMMITTED`. |
| 2 | "I'm going to try making it tonight." | intentional | `INTENDING` | moderate | "try" is an intention; not a decision. |
| 3 | "I'd like to find a more challenging route." | intentional | `INTERESTED` | weak/moderate | Desire, no plan. |
| 4 | "I want to live authentically and help others do the same." | intentional | `INTERESTED` | weak/moderate | Values/desire, no plan. |
| 5 | "I'm going to keep chasing my dreams and working hard." | intentional | `INTENDING` | moderate | Resolve, not ongoing action. |
| 6 | "I'm trying to improve my data analysis skills." | intentional | `EXECUTING` | moderate | Action under way. |
| 7 | "I have to go, bye!" | `E0` | `N/A` | `N/A` | No status proposition; all status fields `N/A`. |
| 8 | "I'm gonna keep writing, but if acting calls out I might give it a try." | intentional | `INTENDING` | moderate | Target P = keep writing; the conditional clause goes in `notes`; do not code `mixed`. |

## Checklist after the pass

- Did both annotators use `INTERESTED` for "I want to / I'd like to"?
- Did both avoid `COMMITTED` unless there is a decision/booking/payment cue?
- Did both reserve `EXECUTING` for an action already under way?
- Did both use `N/A` for every `E0` status field?
- Did both code one target proposition and put secondary clauses in `notes`
  instead of using `mixed`?

If any answer is no, do not start the calibration; re-read
`V3_REAL_STAGE2_DRAFT.md` §8b-§8c.

## v2.3 additions (2026-11-18)

Run 2 passed `gold_status` but failed `gold_dimension` on three boundary items.
Add these to the training pass:

| Sentence | Label | Why |
|---|---|---|
| "I will provide some details about the app and it will be your job to write up a detailed statement..." | `E0` | Instruction to the assistant, not the speaker's own status. |
| "I think about my life too sometimes ... felt like writing a drama." | `E0` | Past/emotional musing, not a current or future action status. |
| "I think I've managed to make it work with dogs while still living in the city." | intentional `COMPLETED` if the item is the speaker's action; epistemic `SUPPORTED`/`ESTABLISHED` if it is a factual claim | Choose the proposition type; if both, code the action and note the fact. |

