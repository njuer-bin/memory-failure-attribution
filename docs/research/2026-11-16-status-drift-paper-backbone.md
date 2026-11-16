# Status Drift Pilot — Paper Backbone (2026-11-16)

Working synthesis of committed results. Not a paper draft; a narrative skeleton
with the evidence attached.

## Working title

**Status Drift in Chained Conversational Memory Compression: Commitment Cues
Are Lost Before Propositions Are**

## Abstract (working)

Long-term LLM agents repeatedly compress conversational memory. We ask whether
this changes the epistemic, intentional, or conditional **status** attached to a
proposition, even when the proposition survives. Across 30- and 60-trajectory
synthetic pilots, three local judges, and a deterministic status-cue metric, we
find that chained rewriting — not shrinking compression budgets — erodes status
cues. The loss is concentrated in **intentional commitment** (`决定`), not
epistemic certainty; propositions remain identifiable. A rewrite-matched control
(intermediate budgets held constant) reproduces the effect, isolating the chain
from the budget schedule. A status-aware writer reduces the loss, and a
commitment-targeted writer eliminates it in a 20-trajectory ceiling test,
showing the phenomenon is controllable rather than an inherent model limit.

## Contributions

1. **A diagnostic**: status-cue loss measured separately from proposition
   retention, with a deterministic cue metric and three-judge validation.
2. **A mechanism**: chained rewriting, not intermediate budget shrinkage,
   drives the loss (direct vs recursive vs rewrite-matched).
3. **A dimension split**: intentional commitment cues are vulnerable; epistemic
   certainty cues are largely robust.
4. **A mitigation curve**: neutral → status-aware → commitment-aware, from 8/10
   cue removal to 0/10, with the caveat that the strongest prompt is a ceiling
   intervention.

## Method

- Synthetic Chinese multi-turn trajectories, 3 dimensions (epistemic,
  intentional, conditional), 10 topics, crossed stable/updated design.
- Conditions: raw, direct compression, recursive chain, rewrite-matched chain.
- Writers: neutral, status-aware, commitment-aware.
- Measures: deterministic proposition retention, deterministic status-cue state
  (MATCH / MIXED / OPPOSITE / ABSENT), judge labels (qwen2.5:7b, gemma3:12b,
  mistral:7b), manual adjudication.

## Headline numbers

### 30-trajectory run (design v3, five topics)

| Metric | neutral | status-aware |
|---|---:|---:|
| Inter-judge agreement | 0.904 | 0.952 |
| Both-judge-correct | 221/270 | 256/270 |
| Both-judge-wrong | 23 | 1 |
| Three-judge all-wrong | 23 | 1 |
| Proposition omission | 3/270 | 0/270 |

### Rewrite-matched control (neutral, 30 trajectories)

Both-correct by depth D1/D2/D3/D5:

- direct: 29 / 28 / 28 / 27
- recursive: 29 / 20 / 17 / 16
- rewrite-matched: 29 / 19 / 17 / 15

Recursive ≈ rewrite-matched; both far below direct. Chaining is the mechanism.

### 10-topic expansion (60 trajectories, cue-only)

Updated cases, ABSENT by depth:

| Condition | neutral | status-aware |
|---|---|---|
| direct D1–D5 | 0 / 3 / 1 / 3 (of 20) | 0 / 0 / 0 / 0 |
| recursive D1–D5 | 0 / 9 / 11 / 11 (of 20) | 0 / 2 / 5 / 7 |

Dimension split at intentional vs epistemic recursive D5:

- neutral: 9/10 vs 2/10
- status-aware: 5/10 vs 2/10

### Commitment-aware ceiling (20 intentional trajectories)

Strong/weak/none commitment cues at D5:

- neutral: 1 / 1 / 8
- status-aware: 5 / 5 / 0
- commitment-aware: **10 / 0 / 0**

Judge confirmation: qwen and gemma agree **180/180**; all **40/40** updated
D3/D5 items are judged COMMITTED, and stable CONSIDERING cases remain correct.

### Human annotation (v2.4)

**Status-aware** (single manual annotator A; the B file is gold-derived and is
not used):

- overall 5/119 = 4.2%; Raw 0/30; Direct D5 0/30; Recursive D5 2/29 = 6.9%;
  Rewrite-matched D5 3/30 = 10.0%; intentional 3/40 = 7.5%; epistemic 5.0%;
  conditional 0%.

**Neutral** (two independent manual annotators):

- overall 6.7–7.9% (A 9/114, B 7/105); Raw 0/30; Direct D5 0/30;
  Recursive D5 13.6–15.4%; Rewrite-matched D5 16.7–17.9%;
  intentional 21.9–25.7%; epistemic and conditional 0%;
- primary-label agreement raw 0.942, Cohen's kappa 0.849.

The neutral writer roughly doubles the human-annotated drift.

## Figures (planned)

1. Condition diagram: raw → direct / recursive / rewrite-matched.
2. Accuracy by depth for the three conditions, both writers.
3. Status-cue ABSENT by dimension and depth.
4. Judge-confusion / agreement heatmap.
5. Mitigation curve: neutral → status-aware → commitment-aware.

## Limitations

- Synthetic templates; one writer model; local judges.
- Human annotation exists for both writers, but the status-aware estimate uses
  one manual annotator; the neutral estimate has two-annotator reliability.
- Token budgets are not matched in the main runs; chained outputs are ~25%
  shorter. A token-band matched control (v2.9, band 14–18) is in progress.
- Neutral writer is not reliably deterministic at temperature 0; report ranges.
- Conditional remains the least reliable dimension (ontology/judge issues).
- Rewrite-matched controls call count but not intermediate content; call count
  and chaining are still entangled.
- The commitment-aware prompt is a ceiling intervention, not a deployment
  recommendation.
- The one-call structured sidecar is blocked with a 7B writer: it either drops
  the prose or copies the option strings. A reliable version needs a separate
  status extractor or a stronger model.

## Related work / novelty

- BELIEFMEM (2605.05583): probabilistic belief memory, LoCoMo/ALFWorld; not a
  measurement of status under chained compression.
- MemCoRe (2602.07885): compression-hierarchy evidence retrieval; not status
  preservation.
- PoS, MemTX, Memory as Belief, Agent-BRACE, TWIST: adjacent belief/state work;
  full-text comparison pending.
- Novelty claim: controlled status-cue diagnostic with a rewrite-matched
  mechanism control and a mitigation curve, not a new memory architecture.

## Open questions

1. Does the intentional-specific loss replicate on natural dialogue?
2. Can a **separate status extractor** (rather than a one-call prose+sidecar
   writer) achieve the commitment-aware result without templated prose? The
   one-call version is blocked at 7B.
3. Can a post-hoc checker repair weakened cues without the source?
4. Does the loss change downstream decisions (Stage B)?
5. What is the human-adjudicated error rate, and does it survive a genuine
   second annotator for the status-aware condition? (Neutral has two-annotator
   reliability; status-aware currently uses one manual annotator.)
