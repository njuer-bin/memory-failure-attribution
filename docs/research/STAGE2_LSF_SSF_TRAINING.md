# Stage 2 LSF/SSF Training Examples (not data)

Use these examples in a 15-20 minute pass before the next LSF/SSF calibration.
Each annotator labels them independently, then the pair compares. **Do not
include them in any calibration or confirmatory set.**

| # | Evidence status | Memory | LSF | SSF | Identity | Why |
|---|---|---|---|---|---|---|
| 1 | `INTENDING` ("I think I'll start writing...") | "You plan to write about your journaling routine." | `CUE_PRESERVED` | `SEMANTIC_CORRECT` | `PRESERVED` | "plan to" is the same `INTENDING` type. |
| 2 | `INTENDING` | "User asks for guidance on organizing the post." | `CUE_ABSENT` | `SEMANTIC_UNDERSPECIFIED` | `PRESERVED` | The plan is not stated; the memory permits it but does not determine it. |
| 3 | `COMMITTED` ("I booked the flight") | "User plans to book a flight." | `CUE_ALTERED` | `SEMANTIC_DISTORTED` | `PRESERVED` | "plans to" is `INTENDING`; the action authorization changes. |
| 4 | `CONSIDERING` ("I'm thinking of going") | "User will go to the mountains." | `CUE_ALTERED` | `SEMANTIC_DISTORTED` | `PRESERVED` | "will" is `INTENDING`; consideration is overstated. |
| 5 | `COMPLETED` ("I managed to make it work") | "User wants to make it work." | `CUE_ALTERED` | `SEMANTIC_DISTORTED` | `PRESERVED` | Desire replaces a completed action. |
| 6 | Any status | "Melanie praised Caroline's art." (target is a different proposition) | `CUE_ABSENT` | `UNASSESSABLE` | `LOST` | The target proposition is not recoverable. |
| 7 | `INTENDING` | "Writing about the journaling routine is the user's next step." | `CUE_ABSENT` | `SEMANTIC_CORRECT` | `PRESERVED` | No cue, but the implication is the same `INTENDING` status. |

## Checklist

- Did both assign the same **cue type**, not just "a cue exists"?
- Did both avoid calling a missing cue `DISTORTED`?
- Did both use `UNDERSPECIFIED` when the memory permits the gold status but does
  not determine it?
- Did both use `DISTORTED` only when the memory implies an incompatible
  authorization?
- Did both use `PRESERVED` only when action + object + person are recoverable?

If any answer is no, re-read `V3_REAL_STAGE2_DRAFT.md` v2.4 §8e before starting.
